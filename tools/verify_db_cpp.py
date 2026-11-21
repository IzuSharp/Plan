#!/usr/bin/env python3
"""Validate DB-CPP-01 progress without treating preparation as product acceptance."""
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "ledger/evidence/batches/DB-CPP-01/"
BATCH = ROOT / PREFIX
BASELINE = "1fe52a8bd792ccdbb4bbea17ba59b0ad0c24349d"
CHECKS = {
    "baseline_reference_provenance", "native_release_clang", "native_sanitizers",
    "native_format_tidy", "retained_native_assertions", "managed_api_and_regressions",
    "query_semantic_parity", "postgresql_behavior_parity", "sqlite_behavior_parity",
    "historical_data_migrations", "failure_cancellation_resources", "postgresql_package_jit",
    "postgresql_package_aot", "sqlite_package_jit", "sqlite_package_aot", "rust_free_build_pack_run",
    "package_abi_load_closure", "model_change_same_native_hash", "independent_review",
    "required_pr_checks", "merged_main_ci",
}


def read(path):
    return json.loads(path.read_text())


def artifact(path):
    assert isinstance(path, str) and path.startswith(PREFIX), "Evidence outside batch"
    p = Path(path)
    assert not p.is_absolute() and ".." not in p.parts and str(p) == path
    target = ROOT / p
    assert target.resolve().is_relative_to(BATCH.resolve()) and target.is_file(), "Missing evidence"
    return target.read_bytes()


def identity(value):
    assert isinstance(value, dict) and set(value) == {"commit", "tree"}
    assert all(re.fullmatch(r"[0-9a-f]{40}", x) for x in value.values())


def validate(graph, acceptance, baseline):
    current = graph["current_execution"]
    assert current["task"] == acceptance["task"] == baseline["task"] == "DB-CPP-01"
    assert current["branch"] == baseline["branch"] == "task/DB-CPP-01-linux"
    assert current["platforms"] == ["linux-x64"]
    assert acceptance["platform"] == baseline["platform"] == "linux-x64"
    assert acceptance["baseline"] == baseline["observed_merged_main"]
    assert current["source_main"] == {k: v["commit"] for k, v in acceptance["baseline"].items()}
    for value in acceptance["baseline"].values():
        identity(value)
    assert set(acceptance["checks"]) == CHECKS
    assert acceptance["state"] in {"in_progress", "blocked", "accepted"}
    assert acceptance["publicly_published"] is False
    for name, check in acceptance["checks"].items():
        assert check["status"] in {"pending", "passed", "failed", "blocked"}
        assert isinstance(check["evidence"], list)
        if check["status"] == "passed":
            assert check["evidence"], "Passed check lacks evidence: " + name
        for reference in check["evidence"]:
            assert set(reference) == {"path", "sha256"}
            raw = artifact(reference["path"])
            assert hashlib.sha256(raw).hexdigest() == reference["sha256"], "Evidence changed"
            receipt = json.loads(raw)
            assert receipt["task"] == "DB-CPP-01" and receipt["platform"] == "linux-x64"
            assert name in receipt["claims"]
            assert receipt["outcome"] in {"passed", "failed", "blocked"}
            if check["status"] == "passed":
                assert receipt["outcome"] == "passed"
                assert receipt["sources"], "Evidence lacks exact source identities"
                for value in receipt["sources"].values():
                    identity(value)
                assert receipt["artifacts"], "Evidence lacks actual logs/results"
            for item in receipt.get("artifacts", []):
                assert hashlib.sha256(artifact(item["path"])).hexdigest() == item["sha256"]
    if acceptance["state"] == "accepted":
        assert all(x["status"] == "passed" for x in acceptance["checks"].values())
        assert all(x["state"] == "complete" for x in current["phases"])
        assert set(acceptance["candidate_sources"]) == set(acceptance["baseline"])
        for value in acceptance["candidate_sources"].values():
            identity(value)
        assert set(acceptance["prs"]) == set(acceptance["baseline"])
        for repository, pr in acceptance["prs"].items():
            assert pr["state"] == "merged" and pr["main_ci_conclusion"] == "success"
            assert re.fullmatch(r"https://github\.com/IzuSharp/" + re.escape(repository) + r"/pull/[1-9][0-9]*", pr["url"])
            assert pr["tested_tree"] == pr["merged_tree"]
            assert re.fullmatch(r"[0-9a-f]{40}", pr["merged_commit"])
            assert pr["main_ci_head"] == pr["merged_commit"]


def main():
    graph = read(ROOT / "delivery-graph.json")
    acceptance = read(BATCH / "acceptance.json")
    baseline = read(BATCH / "baseline.json")
    old = json.loads(subprocess.check_output(["git", "show", BASELINE + ":delivery-graph.json"], cwd=ROOT))
    assert graph["completed_executions"]["DB-Scope-01"] == old["current_execution"]
    for key, value in old.items():
        if key != "current_execution":
            assert graph[key] == value, "Historical delivery graph altered: " + key
    historical = subprocess.check_output(["git", "diff", "--name-only", BASELINE, "--",
        "ledger/evidence/batches/DB-Scope-01", "research-graph.json", "documentation-graph.json",
        "tasks", "research-tasks", "documentation-tasks"], cwd=ROOT, text=True)
    assert not historical.strip(), "Historical accepted records changed"
    validate(graph, acceptance, baseline)
    for case in ("unsupported_pass", "wrong_baseline", "early_acceptance"):
        changed = copy.deepcopy(acceptance)
        if case == "unsupported_pass":
            changed["checks"]["sqlite_package_jit"] = {"status": "passed", "evidence": []}
        elif case == "wrong_baseline":
            changed["baseline"]["NativeWeave"]["commit"] = "0" * 40
        else:
            changed["state"] = "accepted"
            changed["checks"]["native_sanitizers"] = {"status": "pending", "evidence": []}
        try:
            validate(graph, changed, baseline)
        except AssertionError:
            continue
        raise AssertionError("Invalid migration evidence accepted: " + case)
    print("PASS DB-CPP-01 progress, preserved history and three rejection controls; no unexecuted product claim")


if __name__ == "__main__":
    main()
