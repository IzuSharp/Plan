"""GitHub event adapter for the same impact planner developers can run locally."""

import json
import os
from pathlib import Path
import subprocess
import sys

from impact import plan_tree
from catalog import git


def require_checks(plan, results, artifacts):
    expected = {
        "plan": True,
        "security": True,
        "build": bool(plan["build_scopes"]),
        "modules": bool(plan["modules"] or plan["module_packages"]),
    }
    for name, required in expected.items():
        want = "success" if required else "skipped"
        if results[name]["result"] != want:
            raise ValueError(f"{name}: expected {want}, got {results[name]['result']}")
    packages = set(plan["public_checks"]) | set(plan["module_packages"])
    missing = {f"candidate-{p}" for p in packages} - artifacts
    if missing or not set(plan["candidates"]).issubset(packages):
        raise ValueError(
            f"Missing verified package artifacts: {sorted(missing or set(plan['candidates']) - packages)}"
        )


def main():
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    kind = os.environ["GITHUB_EVENT_NAME"]
    if kind == "push":
        base = event["before"]
        if event["after"] != git("rev-parse", "HEAD").decode().strip():
            raise ValueError("The checkout does not match the pushed commit")
    elif kind == "pull_request":
        # The pull_request checkout is GitHub's proposed merge commit.
        base = git("rev-parse", "HEAD^1").decode().strip()
    elif kind == "merge_group":
        base = event["merge_group"]["base_sha"]
    else:
        base = "HEAD^"
    replay = (
        event.get("inputs", {}).get("check_paths", "").splitlines() if kind == "workflow_dispatch" else []
    )
    replay = [p.strip() for p in replay if p.strip()]
    full = kind == "schedule" or (kind == "workflow_dispatch" and not replay)
    images = (
        kind == "workflow_dispatch"
        and str(event.get("inputs", {}).get("verify_images", "")).lower() == "true"
    )
    result = plan_tree(
        base,
        replay=replay or None,
        full=full,
        images=images,
        reconcile=kind == "push" and os.environ["GITHUB_REF"] == "refs/heads/main",
    )
    output = Path("artifacts/plan.json")
    output.parent.mkdir(exist_ok=True)
    data = json.dumps(result, sort_keys=True, indent=2)
    output.write_text(data + "\n")
    print(data)
    workflow_plan = {k: v for k, v in result.items() if k != "reasons"}
    with open(os.environ["GITHUB_OUTPUT"], "a") as out:
        print("plan=" + json.dumps(workflow_plan, separators=(",", ":")), file=out)
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as out:
        print(
            "Linux checks:",
            result["scope"],
            "\n\nPublic candidates:",
            ", ".join(result["candidates"]) or "none",
            file=out,
        )
        print(
            "\nDeferred checks:",
            ", ".join(result["deferred"]) or "none",
            "\n\nCodeQL:",
            ", ".join(result["languages"]) or "none",
            file=out,
        )
        print("\nModule jobs:", ", ".join(result["modules"]) or "none", file=out)
        for group, actions in result["actions"].items():
            print(f"\n* {group}: {', '.join(actions)}", file=out)
        for lane, names in result["reasons"].items():
            print(f"\n* {lane}: {len(names)} changed paths", file=out)


if __name__ == "__main__":
    if sys.argv[1:] == ["--verify"]:
        plan = json.loads(os.environ["PLAN"])
        packages = plan["public_checks"] or plan["module_packages"]
        artifacts = set()
        if packages:
            endpoint = f"repos/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}/artifacts"
            names = subprocess.check_output(
                [
                    "gh",
                    "api",
                    "--paginate",
                    endpoint,
                    "--jq",
                    ".artifacts[] | select(.expired == false) | .name",
                ],
                text=True,
            )
            artifacts.update(names.splitlines())
        require_checks(plan, json.loads(os.environ["RESULTS"]), artifacts)
    else:
        main()
