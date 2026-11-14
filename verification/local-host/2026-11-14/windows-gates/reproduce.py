"""Run unchanged Plan gates in isolated exact-byte sibling checkouts on Windows."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
WORKSPACE = Path(r"C:\MyFile\Projects\IzuSharp")
PAIR = WORKSPACE / "Plan/.worktree/validation-pair"
COMMITS = {
    "Plan": "dacaab7fc346da5b649e943a4d937a756345c492",
    "NativeWeave-Design": "4c5c385779b753a4f06e59d07f80ad27ca10a841",
}
ENV = os.environ.copy()
ENV.update(PYTHONUTF8="1", PYTHONIOENCODING="utf-8", GIT_CONFIG_NOSYSTEM="1")
SHA = lambda raw: hashlib.sha256(raw).hexdigest()
NOW = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
records = []
manifest = {
    "schema_version": "1.0.0",
    "kind": "actual-local-planning-gate-execution",
    "transport": "ArcForges Windows MCP start_process",
    "started_at_utc": NOW(),
    "source_commits": COMMITS,
    "environment": {"os": platform.system(), "release": platform.release(),
                    "architecture": platform.machine(), "python": sys.version,
                    "python_executable": sys.executable},
    "checkout_policy": {"core.autocrlf": "false", "core.longpaths": "true",
                        "purpose": "Preserve committed content hashes, independent of user Git defaults"},
    "records": records,
    "product_delivery_executed": False,
    "native_experiments_rerun": False,
    "independent_review_of_later_root_report": False,
}


def save():
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run(label, command, cwd, timeout=900, source=None):
    started = NOW()
    begin = time.monotonic()
    try:
        result = subprocess.run([str(x) for x in command], cwd=cwd, env=ENV,
                                capture_output=True, timeout=timeout)
        stdout, stderr, code = result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired as error:
        stdout, stderr, code = error.stdout or b"", error.stderr or b"", 124
    (OUT / (label + ".stdout")).write_bytes(stdout)
    (OUT / (label + ".stderr")).write_bytes(stderr)
    row = {"label": label, "command": list(map(str, command)), "cwd": str(cwd),
           "exit_code": code, "started_at_utc": started, "finished_at_utc": NOW(),
           "elapsed_seconds": round(time.monotonic() - begin, 3),
           "stdout_sha256": SHA(stdout), "stderr_sha256": SHA(stderr)}
    if source is not None:
        row["executed_source_sha256"] = SHA(source.read_bytes())
    records.append(row)
    save()
    print(label, code, flush=True)
    return code


def git_output(cwd, *args):
    return subprocess.check_output(["git", *args], cwd=cwd, env=ENV, text=True).strip()


if (OUT / "manifest.json").exists():
    raise SystemExit("Existing attempt preserved; choose a fresh output directory")
PAIR.mkdir(parents=True, exist_ok=True)
save()
for name, commit in COMMITS.items():
    target = PAIR / name
    if target.exists():
        raise SystemExit("Isolated checkout already exists: " + str(target))
    command = ["git", "clone", "--shared", "--no-checkout", "-c", "core.autocrlf=false",
               "-c", "core.longpaths=true", str(WORKSPACE / name), str(target)]
    assert run("clone-" + name, command, WORKSPACE, 120) == 0
    assert run("checkout-" + name, ["git", "checkout", "--detach", commit], target, 120) == 0
    assert git_output(target, "rev-parse", "HEAD") == commit
    assert not git_output(target, "status", "--porcelain")

plan = PAIR / "Plan"
design = PAIR / "NativeWeave-Design"
manifest["source_tools_sha256"] = {
    name + ":" + p.relative_to(PAIR / name).as_posix(): SHA(p.read_bytes())
    for name in COMMITS for p in sorted((PAIR / name / "tools").glob("*.py"))
}
run("python-info", [sys.executable, "--version"], plan, 20)
run("git-info", ["git", "--version"], plan, 20)

# Exact English verification precedes gates that intentionally write derived reports.
checks = [
    ("english-design", design, "tools/verify_english_translation.py", []),
    ("english-plan", plan, "tools/verify_english_translation.py", []),
    ("contract-bindings", plan, "tools/migrate_english_acceptance.py", ["verify-contracts"]),
    ("task-bindings", plan, "tools/migrate_english_acceptance.py", ["verify-tasks"]),
    ("completion", plan, "tools/verify_completion.py", ["--require-complete"]),
    ("graphs", plan, "tools/validate_graphs.py", ["--output", "verification/graph-validation.json"]),
    ("research-assets", plan, "tools/verify_research_assets.py", []),
    ("logical-history", plan, "tools/verify_logical_admission_history.py", []),
    ("source-lifecycle", plan, "tools/verify_source_lifecycle.py", []),
    ("lifecycle-bindings", plan, "tools/source_lifecycle_binding_checks.py", []),
    ("mutations", plan, "tools/mutation_checks.py", []),
    ("host-selection", plan, "tools/host_selection_checks.py", []),
    ("rust-history", plan, "tools/rust1100_checks.py", []),
]
gate_results = []
for label, cwd, script, extra in checks:
    code = run(label, [sys.executable, script, *extra], cwd, source=cwd / script)
    gate_results.append({"label": label, "exit_code": code})

manifest["gate_results"] = gate_results
manifest["all_gates_passed"] = all(row["exit_code"] == 0 for row in gate_results)
manifest["post_run_worktree_status"] = {
    name: git_output(PAIR / name, "status", "--porcelain", "--untracked-files=all")
    for name in COMMITS
}
generated = []
for root in (plan / "verification/current-gates",):
    if root.exists():
        for path in sorted(root.rglob("*")):
            if path.is_file():
                relative = path.relative_to(plan)
                dest = OUT / "generated" / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, dest)
                generated.append({"path": dest.relative_to(OUT).as_posix(), "sha256": SHA(dest.read_bytes())})
for name in ["completion.json", "graph-validation.json", "research-assets-integrity-checks.json",
             "logical-admission-history-checks.json", "source-lifecycle-current-checks.json",
             "source-lifecycle-binding-checks.json", "mutation-checks.json", "host-selection-checks.json",
             "rust1100-checks.json"]:
    path = plan / "verification" / name
    if path.exists():
        dest = OUT / "generated/verification" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
        generated.append({"path": dest.relative_to(OUT).as_posix(), "sha256": SHA(dest.read_bytes())})
manifest["generated_artifacts"] = generated
manifest["reproduction_script_sha256"] = SHA(Path(__file__).read_bytes())
manifest["finished_at_utc"] = NOW()
save()
print(json.dumps({"all_gates_passed": manifest["all_gates_passed"], "checks": gate_results}))
raise SystemExit(0 if manifest["all_gates_passed"] else 1)
