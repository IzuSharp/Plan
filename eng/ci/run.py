#!/usr/bin/env python3
"""Route one real PR or push diff and execute each selected check once."""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

import registry


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def registered_types(path: str) -> set[str]:
    return {kind for row in registry.REGISTRATIONS
            if any(fnmatch.fnmatchcase(path, pattern) for pattern in row.paths)
            for kind in row.types}


def validate_registry() -> None:
    for row in registry.REGISTRATIONS:
        if not row.paths or not row.types:
            raise ValueError("Empty registration in eng/ci/registry.py")
        for kind in row.types:
            if kind not in registry.TYPES:
                raise ValueError(f"Unknown document type: {kind}")
    for kind, spec in registry.TYPES.items():
        for affected in spec.affects:
            if affected not in registry.TYPES:
                raise ValueError(f"{kind}: unknown affected type {affected}")
        for check in spec.checks:
            if check not in registry.CHECKS:
                raise ValueError(f"{kind}: unknown check {check}")


def select(paths: list[str], current_paths: set[str]) -> dict[str, list[str]]:
    validate_registry()
    reasons: dict[str, set[str]] = {}
    for path in paths:
        kinds = registered_types(path)
        if not kinds and path in current_paths:
            raise ValueError(f"Unregistered path {path}; update eng/ci/registry.py")
        # Removed paths still match their registered type; a new registry can also
        # retire obsolete, unregistered paths without inventing a forever type.
        seen: set[str] = set()
        pending = [(kind, kind) for kind in sorted(kinds)]
        while pending:
            kind, origin = pending.pop()
            if kind in seen:
                continue
            seen.add(kind)
            spec = registry.TYPES[kind]
            via = kind if kind == origin else f"{origin} -> {kind}"
            for check in spec.checks:
                reasons.setdefault(check, set()).add(f"{path} ({via})")
            pending.extend((affected, origin) for affected in spec.affects)
    return {check: sorted(reasons[check]) for check in sorted(reasons)}


def changed_paths(root: Path, event: str, base: str, head: str) -> list[str]:
    # --no-renames makes every rename two paths, so both old and new types route.
    start = git(root, "merge-base", base, head) if event == "pull_request" else base
    data = subprocess.check_output(["git", "-C", str(root), "diff", "--no-renames",
                                    "--name-only", "-z", start, head])
    return sorted(set(data.decode().rstrip("\0").split("\0"))) if data else []


def ensure_commit(root: Path, sha: str) -> None:
    if subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"{sha}^{{commit}}"],
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
        subprocess.run(["git", "-C", str(root), "fetch", "--no-tags", "--depth=1", "--filter=blob:none",
                        "origin", sha], check=True)


def empty_tree(root: Path) -> str:
    return subprocess.check_output(["git", "-C", str(root), "hash-object", "-w", "-t", "tree", "--stdin"],
                                   input=b"").decode().strip()


def event_bounds(root: Path) -> tuple[str, str, str]:
    event = os.environ.get("GITHUB_EVENT_NAME", "")
    payload = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    first_push = False
    if event == "pull_request":
        base = payload["pull_request"]["base"]["sha"]
        head = payload["pull_request"]["head"]["sha"]
    elif event == "push":
        base, head = payload["before"], payload["after"]
        if base == "0" * 40:
            # A first push has the empty tree as its real before state.
            base = empty_tree(root)
            first_push = True
    else:
        raise ValueError("Only pull_request and push events are supported")
    if git(root, "rev-parse", "HEAD") != head:
        raise ValueError("Checkout HEAD does not match the event head/after commit")
    if not first_push:
        ensure_commit(root, base)
    ensure_commit(root, head)
    if event == "pull_request":
        # Fetch only history needed for the merge-base; never check out/replay it.
        for depth in (32, 128, 512, 2048):
            if subprocess.run(["git", "-C", str(root), "merge-base", base, head],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                break
            subprocess.run(["git", "-C", str(root), "fetch", "--no-tags", f"--deepen={depth}",
                            "--filter=blob:none", "origin", base, head], check=True)
        if subprocess.run(["git", "-C", str(root), "merge-base", base, head],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:
            raise ValueError("Could not find the PR merge-base within bounded history")
    return event, base, head


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", choices=("pull_request", "push"))
    parser.add_argument("--base")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--list", action="store_true", help="Print selection without running checks")
    parser.add_argument("--all", action="store_true", help="Run every registered check locally")
    parser.add_argument("--json", action="store_true", help="Print machine-readable plan")
    parser.add_argument("--install-dependencies", action="store_true",
                        help="Install only dependencies of selected checks (used by Actions)")
    args = parser.parse_args()
    root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel"))
    tracked = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"])
    current = set(tracked.decode().rstrip("\0").split("\0")) if tracked else set()
    if args.all:
        validate_registry()
        unknown = sorted(p for p in current if not registered_types(p))
        if unknown:
            raise ValueError("Unregistered current paths: " + ", ".join(unknown[:10]))
        selected = {check: ["explicit --all"] for check in sorted(registry.CHECKS)}
        paths = []
    else:
        if bool(args.event) != bool(args.base):
            parser.error("--event and --base must be used together")
        event, base, head = (args.event, args.base, args.head) if args.event else event_bounds(root)
        if not args.list and git(root, "rev-parse", head) != git(root, "rev-parse", "HEAD"):
            raise ValueError("Execution requires --head to be the checked-out HEAD")
        head_paths = subprocess.check_output(["git", "-C", str(root), "ls-tree", "-r", "--name-only", "-z", head])
        current = set(head_paths.decode().rstrip("\0").split("\0")) if head_paths else set()
        paths = changed_paths(root, event, base, head)
        selected = select(paths, current)
    plan = {"checks": list(selected), "reasons": selected, "changed_paths": paths}
    if args.json:
        print(json.dumps(plan, sort_keys=True))
    else:
        print(f"Changed paths: {len(paths)}; selected checks: {len(selected)}", flush=True)
        for check, reasons in selected.items():
            sample = "; ".join(reasons[:3])
            suffix = f"; +{len(reasons) - 3} more" if len(reasons) > 3 else ""
            print(f"  {check}: {sample}{suffix}", flush=True)
    if args.list:
        return 0
    start = time.monotonic()
    requirements = sorted({item for check in selected for item in registry.CHECKS[check].requirements})
    with tempfile.TemporaryDirectory(prefix="document-ci-deps-") as dependency_dir:
        environment = os.environ.copy()
        if args.install_dependencies and requirements:
            subprocess.run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "--quiet",
                            "--target", dependency_dir, *requirements], check=True)
            environment["PYTHONPATH"] = dependency_dir + os.pathsep + environment.get("PYTHONPATH", "")
        for check in selected:
            tick = time.monotonic()
            subprocess.run(registry.CHECKS[check].command, cwd=root, env=environment, check=True)
            print(f"PASS {check} ({time.monotonic() - tick:.2f}s)", flush=True)
    elapsed = time.monotonic() - start
    print(f"Completed {len(selected)} checks in {elapsed:.2f}s", flush=True)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as report:
            report.write(f"## Document CI\n\n{len(paths)} changed paths; {len(selected)} checks; {elapsed:.2f}s.\n\n")
            for check, reasons in selected.items():
                report.write(f"- **{check}**: {reasons[0]} ({len(reasons)} matching reasons)\n")
            if not selected:
                report.write("Ordinary registered documents: no checks required.\n")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Document CI failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
