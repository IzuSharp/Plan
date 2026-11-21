#!/usr/bin/env python3
"""Validate the active DB-Scope-01 overlay without relabeling historical acceptance."""
import argparse
import copy
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "ledger/evidence/batches/DB-Scope-01"
PHASES = ["stop-and-clean", "plan-first", "design-prune", "implementation-prune",
          "linux-regression", "external-consumers", "review-and-merge"]
REQUIRED = {"rust_workspace", "csharp_workspace", "retained_api_and_format",
            "postgresql_regression", "sqlite_regression", "postgresql_package_jit",
            "postgresql_package_aot", "sqlite_package_jit", "sqlite_package_aot",
            "dependency_and_loaded_asset_closure", "no_consumer_rust_invocations",
            "independent_review", "required_pr_checks", "merged_main_ci"}


def validate(graph, acceptance, complete=False):
    current = graph["current_execution"]
    assert current["task"] == acceptance["task"] == "DB-Scope-01"
    assert current["branch"] == "task/DB-Scope-01-linux"
    assert current["platforms"] == ["linux-x64"]
    assert acceptance["platform"] == "linux-x64"
    assert acceptance["performance_work_authorized"] is False
    assert {"PostgreSQL", "SQLite", "Database Host", "strongly typed Fluent",
            "DTO mapping", "Native AOT packaging"}.issubset(current["retain"])
    assert {"NativeWeave HTTP server", "NativeWeave gRPC server and binding", "MCP",
            "independent compression engine", "HelloWorld demo packages"}.issubset(current["remove"])
    assert {"performance optimization", "30-minute load tests", "new ORM features"}.issubset(current["deferred"])
    assert set(current["source_main"]) == {"Plan", "NativeWeave-Design", "NativeWeave"}
    assert all(re.fullmatch("[0-9a-f]{40}", value) for value in current["source_main"].values())
    assert acceptance["source_main"] == current["source_main"]
    assert [phase["id"] for phase in current["phases"]] == PHASES
    previous_complete = True
    for index, phase in enumerate(current["phases"]):
        assert phase["depends_on"] == PHASES[max(0, index - 1):index]
        assert phase["state"] in {"pending", "in_progress", "complete", "blocked"}
        if phase["state"] in {"in_progress", "complete"}:
            assert previous_complete, f"Started {phase['id']} before its prerequisite"
        previous_complete = phase["state"] == "complete"
    assert set(acceptance["claims"]) == REQUIRED
    for name, claim in acceptance["claims"].items():
        assert claim["status"] in {"pending", "passed", "failed", "blocked"}, name
        assert isinstance(claim["evidence"], list), name
        if claim["status"] == "passed":
            assert claim["evidence"], f"Unbound pass: {name}"
    assert acceptance["state"] in {"pending", "in_progress", "blocked", "accepted"}
    if complete or acceptance["state"] == "accepted":
        assert all(claim["status"] == "passed" for claim in acceptance["claims"].values())
        assert all(phase["state"] == "complete" for phase in current["phases"])
        assert all(acceptance["prs"].values())
    # The current overlay does not turn original design authorization into
    # product acceptance, or rewrite the historical 48 individual task records.
    assert len(graph["nodes"]) == 48
    assert all(node["status"] == "planned_candidate" for node in graph["nodes"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    graph = json.loads((ROOT / "delivery-graph.json").read_text())
    acceptance = json.loads((BATCH / "acceptance.json").read_text())
    validate(graph, acceptance, args.require_complete)
    for field in ("plan", "handoff", "acceptance"):
        assert (ROOT / graph["current_execution"][field]).is_file()
    for filename in ("README.md", "CURRENT-PHASE.md", "AGENTS.md", "task-index.md", "acceptance-register.md"):
        assert "DB-Scope-01" in (ROOT / filename).read_text().split("## Historical", 1)[0]
    mutations = []
    for case in ("database_host_removed", "missing_provider_aot", "unbound_pass", "premature_acceptance", "out_of_order"):
        changed_graph, changed_acceptance = copy.deepcopy(graph), copy.deepcopy(acceptance)
        if case == "database_host_removed":
            changed_graph["current_execution"]["retain"].remove("Database Host")
        elif case == "missing_provider_aot":
            del changed_acceptance["claims"]["postgresql_package_aot"]
        elif case == "unbound_pass":
            changed_acceptance["claims"]["sqlite_package_jit"] = {"status": "passed", "evidence": []}
        elif case == "premature_acceptance":
            changed_acceptance["state"] = "accepted"
            changed_acceptance["claims"]["sqlite_package_jit"]["status"] = "pending"
        else:
            changed_graph["current_execution"]["phases"][1]["state"] = "pending"
            changed_graph["current_execution"]["phases"][2]["state"] = "in_progress"
        try:
            validate(changed_graph, changed_acceptance)
        except AssertionError:
            mutations.append(case)
        else:
            raise AssertionError(f"Invalid scope accepted: {case}")
    print(json.dumps({"task": "DB-Scope-01", "structural_validation": "passed",
                      "negative_controls": mutations, "product_acceptance": acceptance["state"]}, indent=2))


if __name__ == "__main__":
    main()
