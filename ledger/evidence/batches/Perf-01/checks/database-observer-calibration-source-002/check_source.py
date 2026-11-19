"""Finite source/metadata checks only; never import or execute a measurement entry point."""
import argparse
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import tempfile
from types import SimpleNamespace


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--plan-root", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    base = args.plan_root.resolve(strict=True) / "ledger/evidence/batches/Perf-01"
    assert os.sched_getaffinity(0) == {8} and not args.receipt.exists()
    started = time.monotonic()
    checks = []

    def check(name, value):
        if not value:
            raise ValueError(name)
        checks.append({"name": name, "passed": True})

    original = (base / "database_calibrate.py").read_text()
    current = (base / "database_observer_calibrate.py").read_text()
    noise_old = (base / "database_freeze_gc_noise.py").read_text()
    noise_new = (base / "database_freeze_observer_noise.py").read_text()
    policy = json.loads((base / "database-observer-policy-001.json").read_text())
    inherited = json.loads((base / "prospective-policy.json").read_text())
    check("original-controller-unchanged", digest(base / "database_calibrate.py") == "04a898d3e9340a85594dd4d4284fb3b6486299feca1b7d8bb6702c5743b889ae")
    check("original-noise-freezer-unchanged", digest(base / "database_freeze_gc_noise.py") == "010e8eaaf225b02b096f8a1441b5170ed1b86877a1c55d00a37693bd3de05a4d")
    check("original-policy-unchanged", digest(base / "prospective-policy.json") == policy["base_calibration_policy_sha256"])
    for field, name in (("controller_source_sha256", "database_observer_calibrate.py"),
                        ("noise_source_sha256", "database_freeze_observer_noise.py"),
                        ("supervisor_source_sha256", "run_db_observer_calibration_001.py"),
                        ("comparison_source_sha256", "database_compare.py")):
        check("exact-" + field, digest(base / name) == policy[field])
        ast.parse((base / name).read_text())
    begin, end = '            for rate in calibration["database_rates"]:', '            selection = {'
    check("complete-ladder-refinement-confirmation-control-flow-unchanged",
          original[original.index(begin):original.index(end)] == current[current.index(begin):current.index(end)])
    begin, end = '    triplet = controller["cells"][-3:]', '    inputs = {'
    check("entire-final-confirmation-triplet-selection-unchanged",
          noise_old[noise_old.index(begin):noise_old.index(end)] == noise_new[noise_new.index(begin):noise_new.index(end)])
    check("original-noise-floor-range-formula-preserved", 'max(1000, max(values) - min(values))' in noise_new)
    check("all-confirmations-still-complete-valid-and-qualifying",
          'row["state"] == "completed" and row["exit_code"] == 0 and row["valid"] and row["qualifies"]' in noise_new)
    check("calibration-has-no-diagnostic-whitelist", "diagnostic_continuation_policy" not in current + noise_new)
    check("fixed-paired-long-targets", policy["paired_long_rates_per_second"] == {"postgresql": 144, "sqlite": 40})
    check("fixed-long-workload", [policy[k] for k in ("paired_long_concurrency", "paired_long_seconds", "paired_long_warmup_requests", "paired_long_recovery_requests", "paired_long_idle_seconds")] == [16, 1802, 16, 32, 60])
    for key in ("stage_seconds", "confirmation_seconds", "confirmation_fresh_processes", "confirmation_attempt_limit", "short_idle_seconds"):
        check("inherited-" + key, policy["calibration"][key] == inherited["calibration"][key])
    check("inherited-ladder-rates", policy["calibration"]["rates"] == inherited["calibration"]["database_rates"])
    check("inherited-resource-limits", policy["limits"] == {"application_rss_bytes": inherited["resource_policy"]["application_rss_limit_bytes"],
          "arrival_p99_ns": inherited["resource_policy"]["arrival_p99_limit_ms"] * 1_000_000,
          "generator_dispatch_lag_ns": inherited["resource_policy"]["generator_maximum_dispatch_lag_ms"] * 1_000_000,
          "unexpected_errors_maximum": inherited["resource_policy"]["unexpected_errors_maximum"]})
    # Extract only pure argv builders and the bounded source-proof/path guard.
    names = {"require", "sha", "confined", "require_adoption", "command"}
    namespace = {"Path": Path, "hashlib": hashlib, "json": json, "re": re,
                 "sys": SimpleNamespace(executable="LOCKED_PYTHON"),
                 "ROUTES": {"before": "nativeweave-aot-rust", "after": "nativeweave-aot-rust", "direct": "direct-rust", "managed": "managed-aot"}}
    tree = ast.parse(current)
    selected = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names or
                isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "PAIR_FILES" for target in node.targets)]
    exec(compile(ast.Module(body=selected, type_ignores=[]), "source-extracted-boundaries", "exec"), namespace)
    old_namespace = {"sys": namespace["sys"], "ROUTES": namespace["ROUTES"]}
    old_command = next(node for node in ast.parse(original).body if isinstance(node, ast.FunctionDef) and node.name == "command")
    exec(compile(ast.Module(body=[old_command], type_ignores=[]), "original-pure-argv", "exec"), old_namespace)
    for variant in ("before", "after", "direct", "managed"):
        for provider in ("postgresql", "sqlite"):
            value = SimpleNamespace(nativeweave=Path("DRIVER"), package_probe=Path("PRODUCER"), variant=variant,
                                    observer=Path("OBSERVER"), comparators=Path("COMPARATORS"), postgres_bin=Path("POSTGRES"),
                                    scheduler_gc_policy="deferred", resource_sampling_policy="threaded", isolation_note="SOURCE_ONLY")
            old_argv = old_namespace["command"](value, inherited, provider, 40, 60, Path("OUTPUT"))
            new_argv = namespace["command"](value, inherited, provider, 40, 60, Path("OUTPUT"))
            check("only-sampling-flag-added-" + variant + "-" + provider,
                  new_argv == old_argv + ["--resource-sampling-policy", "threaded"])
    check("relative-path-confined", namespace["confined"](root, "perf01-run").is_relative_to(root))
    rejected = False
    try:
        namespace["confined"](root, "../outside-workspace")
    except ValueError:
        rejected = True
    check("path-traversal-rejected", rejected)
    rejected = False
    try:
        namespace["confined"](root, "/outside-workspace")
    except ValueError:
        rejected = True
    check("absolute-outside-root-rejected", rejected)
    proofs = namespace["require_adoption"](policy, root)
    check("actual-current-pair-three-proofs-bound", len(proofs) == 3)
    rejected = False
    pending = copy.deepcopy(policy); pending["current_pair_adoption"]["accepted"] = False
    try:
        namespace["require_adoption"](pending, root)
    except ValueError:
        rejected = True
    check("unadopted-pair-rejected", rejected)
    rejected = False
    altered = copy.deepcopy(policy); altered["current_pair_adoption"]["audit_sha256"] = "0" * 64
    try:
        namespace["require_adoption"](altered, root)
    except ValueError:
        rejected = True
    check("changed-pair-proof-rejected", rejected)
    driver = root / ".worktree/Perf-01-db-observer-measured-linux/NativeWeave"
    for relative, expected in policy["driver_source_files_sha256"].items():
        check("driver-source-" + relative, digest(driver / relative) == expected)
    # Exercise only the new file-identity/fresh-path helpers on tiny owned fixtures.
    noise_namespace = {"Path": Path, "hashlib": hashlib, "json": json}
    selected = [node for node in ast.parse(noise_new).body if isinstance(node, ast.FunctionDef) and
                node.name in {"read", "require", "sha", "confined", "observer_inputs"}]
    exec(compile(ast.Module(body=selected, type_ignores=[]), "noise-resource-boundary", "exec"), noise_namespace)
    supervisor = (base / "run_db_observer_calibration_001.py").read_text()
    supervisor_namespace = {"Path": Path, "os": os}
    selected = [node for node in ast.parse(supervisor).body if isinstance(node, ast.FunctionDef) and
                node.name in {"confined", "fresh"}]
    exec(compile(ast.Module(body=selected, type_ignores=[]), "supervisor-fresh-boundary", "exec"), supervisor_namespace)
    with tempfile.TemporaryDirectory(prefix="source-boundaries-", dir=args.receipt.parent) as directory:
        cell = Path(directory).resolve()
        app = cell / "application"; app.mkdir()
        resources, extra = app / "generator-resources.jsonl", app / "perf01.json"
        def fixture():
            resources.write_bytes(b'{"rss_bytes":32}\n')
            observer = {"path": resources.name, "sha256": digest(resources), "status": "completed"}
            extra.write_text(json.dumps({"generator_resource_observer": observer}))
            return {"perf01_receipt": {"path": str(extra), "sha256": digest(extra)},
                    "generator_resource_observer": observer}
        summary = fixture()
        bound = noise_namespace["observer_inputs"](cell, summary, digest(resources))
        check("actual-perf01-and-resource-bytes-bound", bound == {str(extra): digest(extra), str(resources): digest(resources)})
        for case in ("changed", "missing", "receipt-mismatch", "resource-escape", "receipt-escape"):
            summary = fixture(); expected = digest(resources)
            if case == "changed": resources.write_bytes(b'{"rss_bytes":64}\n')
            elif case == "missing": resources.unlink()
            elif case == "receipt-mismatch":
                altered = copy.deepcopy(summary["generator_resource_observer"]); altered["status"] = "failed"
                extra.write_text(json.dumps({"generator_resource_observer": altered}))
                summary["perf01_receipt"]["sha256"] = digest(extra)
            elif case == "resource-escape":
                summary["generator_resource_observer"]["path"] = "../outside.jsonl"
                extra.write_text(json.dumps({"generator_resource_observer": summary["generator_resource_observer"]}))
                summary["perf01_receipt"]["sha256"] = digest(extra)
            else: summary["perf01_receipt"]["path"] = str(cell.parent / "outside.json")
            rejected = False
            try:
                noise_namespace["observer_inputs"](cell, summary, expected)
            except (ValueError, FileNotFoundError):
                rejected = True
            check("generator-resource-" + case + "-rejected", rejected)
        check("fresh-path-resolves-inside-root", supervisor_namespace["fresh"](cell, "future") == cell / "future")
        existing = cell / "existing"; existing.write_bytes(b"fixture")
        dangling = cell / "dangling"; dangling.symlink_to("absent-target")
        for case, path in (("existing", existing), ("dangling-symlink", dangling)):
            rejected = False
            try:
                supervisor_namespace["fresh"](cell, path)
            except AssertionError:
                rejected = True
            check("fresh-" + case + "-rejected", rejected)
    body = next(node.body for node in ast.parse(supervisor).body if isinstance(node, ast.FunctionDef) and node.name == "main")
    optimize_guard = next(i for i, node in enumerate(body) if isinstance(node, ast.If) and
                          ast.unparse(node.test) == "sys.flags.optimize != 0" and isinstance(node.body[0], ast.Raise))
    check("optimized-supervisor-rejected-before-first-assert", optimize_guard < next(i for i, node in enumerate(body) if isinstance(node, ast.Assert)))
    check("actual-interpreter-path-version-and-bytes-checked",
          "actual_python = Path(sys.executable).resolve(strict=True)" in supervisor and
          "actual_python == Path(doc['python']['executable']).resolve(strict=True)" in supervisor and
          "'.'.join(map(str, sys.version_info[:3])) == doc['python']['version']" in supervisor and
          "digest(actual_python) == doc['python']['recorded_executable_sha256']" in supervisor)
    preflight = supervisor[:supervisor.index("    result = {")]
    check("both-future-logs-and-outputs-preflighted-before-first-provider",
          "for command in doc['commands']:" in preflight and
          "fresh(ROOT, command['output'])" in preflight and
          "fresh(ROOT, Path('perf01-run') / (command['id'] + '.log'))" in preflight and
          "RECEIPT = fresh(ROOT, RECEIPT)" in preflight)
    allowed = {"Perf-01", "database-observer-policy-001", "deferred", "threaded", "calibration-noise-only"}
    forbidden = {"path", "argv", "commands", "environment", "host", "pid", "ppid", "start_ticks", "token"}
    def inspect(value):
        if isinstance(value, dict):
            assert not forbidden.intersection(value)
            for child in value.values(): inspect(child)
        elif isinstance(value, list):
            for child in value: inspect(child)
        elif isinstance(value, str):
            assert value in allowed or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value)
        else:
            assert value is None or type(value) in (int, float, bool)
    inspect(policy)
    check("public-contract-only-numbers-booleans-enums-hashes", True)
    for name in ("database_observer_calibrate.py", "database_freeze_observer_noise.py", "run_db_observer_calibration_001.py"):
        check("portable-source-" + name, "/workspace/" not in (base / name).read_text())
    receipt = {"schema_version": 1, "task": "Perf-01", "checks": checks, "passed_checks": len(checks),
               "contract_sha256": digest(base / "database-observer-policy-001.json"), "source_sha256": digest(__file__),
               "source_identity": {key: policy[key] for key in ("controller_source_sha256", "noise_source_sha256", "supervisor_source_sha256", "comparison_source_sha256")},
               "cpu_affinity": [8], "elapsed_seconds": time.monotonic() - started,
               "measurement_entry_points_executed": False, "driver_imported": False, "load_executed": False,
               "calibration_executed": False, "noise_extracted": False, "duration_credit_seconds": 0}
    with args.receipt.open("x") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True, allow_nan=False); stream.write("\n")
    print(json.dumps({"passed_checks": len(checks), "receipt_sha256": digest(args.receipt), "load_executed": False}))


if __name__ == "__main__":
    main()
