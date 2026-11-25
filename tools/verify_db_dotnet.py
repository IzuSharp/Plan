#!/usr/bin/env python3
"""Validate DB-DotNet-01 records without manufacturing execution evidence."""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "ledger/evidence/batches/DB-DotNet-01"
FROZEN = "c73943c72b77cca0398e4034cb82663db0d20bd0"
PERF_FROZEN = "38f8ce8a01f88e6e4c4459926f197c5438c2f6fc"
PHASES = {
    "source-baseline", "migration-compatibility", "internal-dotnet-baseline",
    "benchmark-correctness", "measured-optimization", "independent-review",
    "pr-and-main-ci", "preview-public-consumption",
}
CELLS = {
    ("postgresql", "Korda"), ("postgresql", "Dapper.AOT"),
    ("sqlite", "Korda"), ("sqlite", "Dapper.AOT"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def verify_evidence(items):
    require(isinstance(items, list), "Evidence must be a list")
    for item in items:
        require(isinstance(item, dict), "Evidence needs a path and content hash")
        name = item.get("path", "")
        path = (ROOT / name).resolve()
        require(bool(name) and path.is_relative_to(BATCH.resolve()), "Evidence must belong to this batch")
        require(path.is_file(), "Missing evidence: " + name)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == item.get("sha256"), "Evidence hash mismatch: " + name)


def validate(record, *, complete=False, check_files=True):
    require(record.get("schema_version") == 1 and record.get("task") == "DB-DotNet-01", "Wrong task schema")
    require(record.get("platform") == "linux-x64", "Wrong platform")
    require(record.get("status") in {"pending", "in_progress", "blocked", "complete"}, "Invalid status")
    phases = record.get("phases", [])
    require(len(phases) == len(PHASES) and {p.get("id") for p in phases} == PHASES, "Missing or duplicate phases")
    for phase in phases:
        require(phase.get("status") in {"pending", "in_progress", "blocked", "passed"}, "Invalid phase status")
        if check_files:
            verify_evidence(phase.get("evidence"))
        if phase["status"] == "passed":
            require(bool(phase.get("evidence")), "A passed phase needs observed evidence")
    cells = record.get("long_segments", [])
    require(len(cells) == 4 and {(c.get("database"), c.get("route")) for c in cells} == CELLS, "Expected exactly four long cells")
    require(len({c.get("id") for c in cells}) == 4, "Duplicate long-segment identity")
    accepted = 0
    seconds = 0
    environments = set()
    for cell in cells:
        require(cell.get("status") in {"pending", "running", "blocked", "rejected", "complete"}, "Invalid segment status")
        duration = cell.get("valid_seconds")
        require(type(duration) in {int, float} and duration >= 0, "Invalid long duration")
        if check_files:
            verify_evidence(cell.get("evidence"))
        if cell["status"] == "complete":
            require(duration >= 1800, "A complete segment needs 1,800 continuous effective seconds")
            require(bool(cell.get("environment_id")) and bool(cell.get("evidence")), "A long segment needs environment-bound raw evidence")
            accepted += 1
            seconds += duration
            environments.add(cell["environment_id"])
        else:
            require(duration == 0, "Unaccepted/interrupted durations cannot count as long credit")
    require(len(environments) <= 1, "Long cells must use the same admitted resource set")
    require(record.get("accepted_long_segments") == accepted, "Wrong accepted cell count")
    require(record.get("effective_long_seconds") == seconds, "Wrong accepted duration")
    for claim in record.get("allocation_claims", []):
        require(claim.get("path") and claim.get("boundary"), "Allocation claim needs a named path/boundary")
        require(claim.get("status") in {"met", "not_met", "unproven"}, "Invalid allocation status")
        if claim["status"] == "met":
            require(claim.get("attributable_korda_raw_bytes") == 0, "A zero claim needs exactly zero raw attributable bytes")
            require(type(claim.get("successful_operations")) is int and claim["successful_operations"] > 0, "Zero claim needs counted operations")
            require(bool(claim.get("attribution_method")) and bool(claim.get("evidence")), "Zero claim needs attribution evidence")
        if check_files:
            verify_evidence(claim.get("evidence", []))
    if complete or record["status"] == "complete":
        require(all(p["status"] == "passed" for p in phases), "Product phases are incomplete")
        require(accepted == 4 and seconds >= 7200, "Four long segments are incomplete")
        require(record.get("product_execution_claimed") is True, "Missing observed execution state")
        require(not any(d.get("blocks_compatibility", True) for d in record.get("unresolved_differences", [])), "Unresolved compatibility blocker")


def history_integrity():
    protected = [
        "ledger/evidence/batches/DB-Perf-01", "ledger/evidence/batches/DB-Rename-01",
        "ledger/evidence/batches/DB-API-01", "ledger/evidence/batches/DB-CPP-01",
        "ledger/evidence/batches/DB-Scope-01", "tools/verify_db_perf.py",
        "tools/verify_db_rename.py", "tools/verify_db_api.py", "tools/verify_db_cpp.py",
        "tools/verify_db_scope.py", "schemas/db-perf-v1.schema.json",
        "research-graph.json", "documentation-graph.json", "source-driven-baseline.json",
    ]
    changed = subprocess.check_output(["git", "diff", "--name-only", FROZEN, "--", *protected], cwd=ROOT, text=True)
    require(not changed.strip(), "Historical inputs changed: " + changed)
    before = json.loads(subprocess.check_output(["git", "show", FROZEN + ":delivery-graph.json"], cwd=ROOT, text=True))
    now = read(ROOT / "delivery-graph.json")
    require(now["prior_execution_snapshots"]["DB-Perf-01"] == {"frozen_plan": FROZEN, "entry": before["current_execution"]}, "Old current_execution was not preserved exactly")
    for key, value in before.items():
        if key not in {"current_execution", "prior_execution_snapshots"}:
            require(now.get(key) == value, "Historical graph field changed: " + key)
    for key, value in before["prior_execution_snapshots"].items():
        require(now["prior_execution_snapshots"].get(key) == value, "Prior execution snapshot changed")
    require(now["current_execution"]["task"] == "DB-DotNet-01" and now["current_execution"]["branch"] == "DB-DotNet-01", "Wrong current task")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--verify-frozen-history", action="store_true")
    args = parser.parse_args()
    record = read(BATCH / "acceptance.json")
    validate(record, complete=args.require_complete)
    history_integrity()
    baseline = read(BATCH / "baseline.json")
    require(baseline["source_main"]["Plan"] == FROZEN, "Wrong Plan baseline")
    require(baseline["external_performance_comparator"] == "Dapper.AOT", "Wrong external comparator")
    require(baseline["old_performance_credit_transferred"] is False, "Historical credit cannot transfer")
    cases = read(BATCH / "workload-cases.json")["cases"]
    require(len(cases) >= 24 and len({c["id"] for c in cases}) == len(cases), "Need 24 distinct business case IDs")
    require(any(c["id"] == "Q31" and "100" in c["business_operation"] for c in cases), "Missing 100-DTO list case")
    for case in cases:
        require(case["required_databases"] == ["postgresql", "sqlite"] and case["required_routes"] == ["Korda", "Dapper.AOT"], "Incomplete case matrix")
    for name in ["plan.md", "handoff-linux.md", "workloads.md", "driver-source-review.md"]:
        require((BATCH / name).is_file(), "Missing current document " + name)
    invalid = []
    bad = copy.deepcopy(record); bad["long_segments"].pop(); invalid.append(bad)
    bad = copy.deepcopy(record); bad["phases"][0].update(status="passed", evidence=[]); invalid.append(bad)
    bad = copy.deepcopy(record); bad["long_segments"][0].update(status="complete", valid_seconds=1799); invalid.append(bad)
    bad = copy.deepcopy(record); bad["effective_long_seconds"] = 7200; invalid.append(bad)
    for bad in invalid:
        try:
            validate(bad, check_files=False)
        except ValueError:
            continue
        raise ValueError("An invalid acceptance record passed")
    if args.verify_frozen_history:
        with tempfile.TemporaryDirectory(prefix="db-dotnet-history-", dir=ROOT.parent) as temp:
            work = Path(temp) / "Plan"
            subprocess.run(["git", "worktree", "add", "--detach", str(work), PERF_FROZEN], cwd=ROOT, check=True)
            try:
                subprocess.run(["python3", "tools/verify_db_perf.py"], cwd=work, check=True)
            finally:
                subprocess.run(["git", "worktree", "remove", "--force", str(work)], cwd=ROOT, check=True)
    print(json.dumps({"task": "DB-DotNet-01", "record_gate": "passed", "negative_controls": len(invalid), "product_acceptance": record["status"], "accepted_long_segments": record["accepted_long_segments"], "record_gate_proves_product_execution": False}, indent=2))


if __name__ == "__main__":
    main()
