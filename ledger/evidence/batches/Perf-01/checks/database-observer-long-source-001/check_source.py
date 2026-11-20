"""Finite long-preparation source checks; no measurement entry point is run."""
import argparse
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def extracted(source, names, namespace):
    nodes = [node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "bounded-source-helpers", "exec"), namespace)
    return namespace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "plan-root", "configuration", "receipt"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args()
    root, plan = args.root.resolve(strict=True), args.plan_root.resolve(strict=True)
    base = plan / "ledger/evidence/batches/Perf-01"
    assert os.sched_getaffinity(0) == {8} and not os.path.lexists(args.receipt)
    started = time.monotonic(); checks = []
    def check(name, value):
        if not value: raise ValueError(name)
        checks.append({"name": name, "passed": True})
    policy = json.loads((base / "database-observer-policy-001.json").read_text())
    amendment = json.loads((base / "database-observer-long-amendment-001.json").read_text())
    doc = json.loads(args.configuration.read_text())
    source = (base / "run_db_observer_long_001.py").read_text()
    verifier = (base / "verify_db_observer_long.py").read_text()
    ast.parse(source); ast.parse(verifier)
    check("both-runtime-sources-parse", True)
    check("supervisor-source-pinned", digest(base / "run_db_observer_long_001.py") == amendment["supervisor_sha256"])
    check("verifier-wrapper-source-pinned", digest(base / "verify_db_observer_long.py") == amendment["verifier_wrapper_sha256"])
    check("adopted-contract-pinned", digest(base / "database-observer-policy-001.json") == amendment["adopted_policy_sha256"] ==
          "98f8e537d87cac9de87cb2d1ae1150465a5c9a052333451f0772398b58ad58c3")
    check("actual-private-amendment-binding", doc["amendment_sha256"] == digest(base / "database-observer-long-amendment-001.json"))
    primary = root / ".worktree/Perf-01-linux/Plan/ledger/evidence/batches/Perf-01"
    new_names = {"run_db_observer_long_001.py", "verify_db_observer_long.py", "database-observer-long-amendment-001.json"}
    for path, expected in doc["required_source_and_metadata_sha256"].items():
        actual = base / Path(path).name if Path(path).parent == primary and Path(path).name in new_names else Path(path)
        check("private-input-pin-" + str(len(checks)), digest(actual) == expected)
    check("runtime-artifacts-retain-exact-recorded-hash-shape", len(doc["required_runtime_artifact_sha256"]) == 9 and
          all(re.fullmatch(r"[0-9a-f]{64}", value) for value in doc["required_runtime_artifact_sha256"].values()))
    driver = root / doc["driver_root_relative"]
    check("actual-measurement-driver-commit", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=driver, text=True).strip() == policy["driver_commit"])
    check("actual-measurement-driver-full-tree", subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=driver, text=True).strip() == policy["driver_tree"])
    check("original-long-verifier-unchanged", digest(driver / "tests/Perf01/verify_long.py") == amendment["original_verifier_sha256"] ==
          "3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82")
    old = json.loads((primary / "database-before-long-commands.json").read_text())
    for provider, rate, operations in (("postgresql", 144, 259526), ("sqlite", 40, 72091)):
        group = doc["groups"][provider]; expected = amendment["groups"][provider]
        check("fixed-long-load-" + provider, expected["rate_per_second"] == rate and expected["planned_operations"] == operations)
        previous = copy.deepcopy(next(row["argv"] for row in old["commands"] if row["group"] == provider and "--package-probe" in row["argv"]))
        index = next(i for i, value in enumerate(previous) if value.endswith("/tests/Perf01.Database/run.py"))
        previous[index] = str(driver / "tests/Perf01.Database/run.py")
        previous[previous.index("--output") + 1] = group["output"]
        previous += ["--scheduler-gc-policy", "deferred", "--resource-sampling-policy", "threaded"]
        check("only-adopted-driver-output-and-policy-argv-delta-" + provider, group["commands"][0]["argv"] == previous)
        for command in group["commands"]:
            check("one-nonblocking-child-lock-" + command["id"], command["argv"][:3] ==
                  ["/usr/bin/flock", "--nonblock", str(root / "perf01-evidence/timing.lock")] and
                  sum(Path(value).name == "flock" for value in command["argv"]) == 1)
            check("fresh-future-log-" + command["id"], not os.path.lexists(command["log"]))
        for key in ("output", "verification", "execution_receipt"):
            check("fresh-future-" + provider + "-" + key, not os.path.lexists(group[key]))
        argv = group["commands"][1]["argv"]
        check("post-run-source-and-amendment-binding-" + provider,
              argv[argv.index("--source-sha256") + 1] == amendment["verifier_wrapper_sha256"] and
              argv[argv.index("--amendment-sha256") + 1] == doc["amendment_sha256"] and argv[5] == "8")
    check("unchanged-long-durations-and-phase-counts", [amendment[key] for key in
          ("concurrency", "requested_seconds", "warmup_operations", "recovery_operations", "idle_seconds")] == [16, 1802, 16, 32, 60])
    check("unchanged-service-limits", amendment["limits"] == policy["limits"])
    check("both-1800-second-proofs-retained", amendment["required_ordinary_lower_bound_ns"] ==
          amendment["required_original_dispatch_span_ns"] == 1_800_000_000_000)
    check("disk-margin-without-cleanup", amendment["minimum_free_disk_bytes"] == {"postgresql": 10 * 1024**3, "sqlite": 4 * 1024**3} and
          amendment["automatic_cleanup"] is False)
    check("no-diagnostic-whitelist", amendment["diagnostic_failure_whitelist"] is False and "diagnostic_continuation_policy" not in source + verifier)
    check("original-verifier-called-once-and-accepted-only-by-conjunction", verifier.count("original.verify(args.group, output)") == 1 and
          'result["accepted"] = result["original_verifier_accepted"] and result["observer_contract"]["passed"]' in verifier and
          'if not result["accepted"]:\n        result["duration_credit_seconds"] = 0' in verifier)
    supervisor = extracted(source, {"require", "sha", "read", "confined", "fresh", "qualification"},
                           {"Path": Path, "hashlib": hashlib, "json": json, "os": os})
    supervisor["qualification"](root, doc, amendment, policy)
    check("actual-calibration-and-noise-chain-qualifies-without-raw-replay", True)
    bad = copy.deepcopy(amendment); bad["groups"]["postgresql"]["rate_per_second"] = 143
    rejected = False
    try: supervisor["qualification"](root, doc, bad, policy)
    except ValueError: rejected = True
    check("changed-fixed-long-rate-rejected", rejected)
    checks_namespace = extracted(verifier, {"require", "sha", "frozen_sources"},
                                {"Path": Path, "hashlib": hashlib, "json": json, "shutil": shutil})
    with tempfile.TemporaryDirectory(prefix="long-source-boundary-", dir=args.receipt.parent) as temporary:
        sandbox = Path(temporary); fixture = sandbox / "source"; fixture.write_bytes(b"bound-source")
        values = {str(fixture): digest(fixture)}
        identity = hashlib.sha256(json.dumps(values, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        checks_namespace["frozen_sources"](sandbox, values, identity)
        check("complete-source-map-and-real-bytes-accepted", True)
        fixture.write_bytes(b"changed-source")
        rejected = False
        try: checks_namespace["frozen_sources"](sandbox, values, identity)
        except ValueError: rejected = True
        check("changed-real-source-bytes-rejected", rejected)
        rejected = False
        try: checks_namespace["frozen_sources"](sandbox, {}, identity)
        except ValueError: rejected = True
        check("missing-source-map-entry-rejected", rejected)
        dangling = sandbox / "dangling"; dangling.symlink_to("absent")
        for case, path in (("existing", fixture), ("dangling", dangling)):
            rejected = False
            try: supervisor["fresh"](sandbox, path)
            except ValueError: rejected = True
            check("fresh-" + case + "-path-rejected", rejected)
    allowed = {"Perf-01", "database-observer-long-amendment-001", "prospective", "deferred", "threaded"}
    def public(value):
        if isinstance(value, dict):
            for child in value.values(): public(child)
        elif isinstance(value, list):
            for child in value: public(child)
        elif isinstance(value, str):
            check("public-enum-or-hash-" + str(len(checks)), value in allowed or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value))
        else: assert value is None or type(value) in (int, float, bool)
    public(amendment)
    check("portable-public-source", "/workspace/" not in source + verifier)
    receipt = {"schema_version": 1, "task": "Perf-01", "checks": checks, "passed_checks": len(checks),
               "private_configuration_sha256": digest(args.configuration), "amendment_sha256": digest(base / "database-observer-long-amendment-001.json"),
               "supervisor_sha256": amendment["supervisor_sha256"], "verifier_wrapper_sha256": amendment["verifier_wrapper_sha256"],
               "source_sha256": digest(__file__), "elapsed_seconds": time.monotonic() - started, "cpu_affinity": [8],
               "measurement_entry_points_executed": False, "driver_imported": False, "load_executed": False,
               "original_verifier_executed": False, "raw_measurement_rows_replayed": False, "duration_credit_seconds": 0}
    with args.receipt.open("x") as stream: json.dump(receipt, stream, indent=2, sort_keys=True); stream.write("\n")
    print(json.dumps({"passed_checks": len(checks), "receipt_sha256": digest(args.receipt), "load_executed": False}))


if __name__ == "__main__":
    main()
