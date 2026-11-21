#!/usr/bin/env python3
"""Verify DB-CPP-01 source-bound progress and the delivered Linux snapshot."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from db_cpp_evidence import (
    BASELINES, CI_PRODUCT_CLAIMS, KINDS, PREFIX, REPOSITORIES, WORKFLOWS,
    canonical, identity, json_object, reference_bytes, sha, unwrap, validate_ci_row,
    validate_links, validate_result,
)

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / PREFIX
BASELINE = BASELINES["Plan"]["commit"]
PHASES = ["baseline-and-cleanup", "plan-first", "design-decision", "cpp-execution",
          "behavior-comparison", "rust-free-packages", "review-and-merge"]
CHECKS = {
    "baseline_reference_provenance", "native_release_clang", "native_sanitizers",
    "native_format_tidy", "retained_native_assertions", "managed_api_and_regressions",
    "query_semantic_parity", "postgresql_behavior_parity", "sqlite_behavior_parity",
    "historical_data_migrations", "failure_cancellation_resources", "postgresql_package_jit",
    "postgresql_package_aot", "sqlite_package_jit", "sqlite_package_aot", "rust_free_build_pack_run",
    "package_abi_load_closure", "model_change_same_native_hash", "independent_review",
    "required_pr_checks", "merged_main_ci",
}
CI_CLAIMS = {"required_pr_checks", "merged_main_ci"}
RESULT_KINDS = {
    "native_release_clang": {"native-build", "verification-result"},
    "native_sanitizers": set(),
    "native_format_tidy": {"verification-result"},
    "retained_native_assertions": {"regression-result"},
    "managed_api_and_regressions": {"regression-result", "verification-result"},
    "query_semantic_parity": {"migration-comparison"},
    "postgresql_behavior_parity": {"migration-comparison", "regression-result"},
    "sqlite_behavior_parity": {"migration-comparison", "regression-result"},
    "historical_data_migrations": {"migration-comparison"},
    "failure_cancellation_resources": {"regression-result"},
    "postgresql_package_jit": {"migration-comparison"},
    "postgresql_package_aot": {"migration-comparison"},
    "sqlite_package_jit": {"migration-comparison"},
    "sqlite_package_aot": {"migration-comparison"},
    "rust_free_build_pack_run": set(),
    "package_abi_load_closure": {"migration-comparison", "verification-result"},
    "model_change_same_native_hash": {"migration-comparison"},
    "independent_review": {"review"},
}
LEGACY_REFERENCE = {"path": PREFIX + "reference-receipt.json",
                    "sha256": "712101dbd377492cc8bab7dda298d002633fd4a6a27ee993b0be10ab5972ec95"}


def read(path):
    return json.loads(path.read_text())


def artifact(path):
    canonical(path)
    target = ROOT / path
    assert target.resolve().is_relative_to(BATCH.resolve()) and target.is_file(), "Missing evidence: " + path
    return target.read_bytes()


def expected_pr_source(record, scope):
    prefix = "tested" if scope == "pr_head" else "merged"
    source = {"commit": record.get(prefix + "_commit"), "tree": record.get(prefix + "_tree")}
    identity(source)
    return source


def receipt(reference, name, passed, acceptance, read_bytes):
    raw = reference_bytes(reference, read_bytes)
    value = json_object(raw)
    assert value.get("task") == "DB-CPP-01" and value.get("platform") == "linux-x64"
    claims = value.get("claims")
    assert isinstance(claims, list) and claims and len(set(claims)) == len(claims) and set(claims) <= CHECKS
    assert name in claims and value.get("outcome") in {"passed", "failed", "blocked"}
    assert not passed or value["outcome"] == "passed", "Passed check cites failed/blocked evidence"
    sources = value.get("sources")
    assert isinstance(sources, dict) and sources and set(sources) <= REPOSITORIES
    for source in sources.values():
        identity(source)
    legacy = reference == LEGACY_REFERENCE
    assert name != "baseline_reference_provenance" or legacy, "Only the fixed verified Rust reference may establish the baseline"
    if legacy:
        assert claims == ["baseline_reference_provenance"] and sources == {"NativeWeave": BASELINES["NativeWeave"]}
    else:
        assert value.get("schema_version") == 2, "New evidence requires schema_version 2"
    items = value.get("artifacts")
    assert isinstance(items, list) and items, "Evidence lacks actual artifacts"
    loaded = {}
    for item in items:
        assert isinstance(item, dict) and set(item) == ({"path", "sha256"} if legacy else {"path", "sha256", "kind"})
        path = item["path"]
        assert path != reference["path"] and path not in loaded, "Self-reference or duplicate artifact"
        data = reference_bytes({k: item[k] for k in ("path", "sha256")}, read_bytes)
        kind = "legacy-reference" if legacy else item["kind"]
        assert legacy or kind in KINDS, "Unknown artifact kind"
        decoded, original_sha = ({}, sha(data)) if kind == "log" else unwrap(data)
        if passed and not legacy:
            validate_result(kind, decoded, value, acceptance)
        loaded[path] = {**item, "kind": kind, "data": decoded, "original_sha256": original_sha}
    if legacy:
        assert loaded[PREFIX + "rust-reference-provenance.json"]["data"].get("source_commit") == BASELINES["NativeWeave"]["commit"]
        assert loaded[PREFIX + "rust-reference-packages.json"]["data"].get("sourceCommit") == BASELINES["NativeWeave"]["commit"]
    if passed:
        validate_links(list(loaded.values()))
    ci = []
    if "ci" in value and passed:
        assert value.get("required_checks_complete") is True
        assert isinstance(value["ci"], list) and value["ci"]
        ci = [validate_ci_row(row, sources, loaded, acceptance["prs"]) for row in value["ci"]]
        assert len(set(ci)) == len(ci), "Duplicate CI observations"
    if passed and name in CI_CLAIMS:
        assert ci, "CI claim has no actual run/jobs observations"
    if passed and name in RESULT_KINDS:
        kinds = {item["kind"] for item in loaded.values()}
        actual_result = bool(kinds & RESULT_KINDS[name])
        actual_ci = name in CI_PRODUCT_CLAIMS and ("NativeWeave", "pr_head", ".github/workflows/ci.yml") in ci
        assert actual_result or actual_ci, "Claim lacks an applicable actual result: " + name
    return {**value, "validated_ci": ci, "loaded": loaded}


def claim_sources(name, values, acceptance):
    if name == "baseline_reference_provenance":
        required = {"NativeWeave"}
    elif name in CI_CLAIMS:
        required = REPOSITORIES
    elif name == "independent_review":
        required = {"NativeWeave", "NativeWeave-Design"}
    else:
        required = {"NativeWeave"}
    covered = set()
    for value in values:
        for repo, observed in value["sources"].items():
            if name == "baseline_reference_provenance":
                expected = BASELINES[repo]
            elif name in CI_CLAIMS:
                record = acceptance["prs"].get(repo)
                assert isinstance(record, dict), "CI claim lacks corresponding PR"
                expected = expected_pr_source(record, "pr_head" if name == "required_pr_checks" else "merged_main")
            else:
                expected = acceptance["candidate_sources"].get(repo)
            assert expected is not None and observed == expected, "Claim source differs from its exact candidate/baseline/PR identity: " + name
            covered.add(repo)
    assert required <= covered, "Claim lacks required repository source coverage: " + name


def ci_references(references, repo, scope, source, acceptance, read_bytes):
    assert isinstance(references, list) and references, "Missing exact-head/merged-main CI receipts"
    name = "required_pr_checks" if scope == "pr_head" else "merged_main_ci"
    paths = set()
    seen = set()
    for reference in references:
        assert reference["path"] not in seen
        seen.add(reference["path"])
        value = receipt(reference, name, True, acceptance, read_bytes)
        assert value["sources"].get(repo) == source, "CI receipt source differs from PR identity"
        selected = [path for observed_repo, observed_scope, path in value["validated_ci"] if observed_repo == repo and observed_scope == scope]
        assert selected, "CI receipt has no run for the expected repository/scope"
        assert not paths.intersection(selected), "Duplicate required workflow"
        paths.update(selected)
    assert paths == set(WORKFLOWS[repo]), "Required workflow set is incomplete"


def validate_prs(acceptance, complete, read_bytes):
    assert set(acceptance.get("prs", {})) == REPOSITORIES
    for repo, record in acceptance["prs"].items():
        assert isinstance(record, dict)
        assert re.fullmatch(r"https://github\.com/IzuSharp/" + re.escape(repo) + r"/pull/[1-9][0-9]*", record.get("url", ""))
        assert record.get("state") in {"draft", "open", "closed", "merged"}
        for field in ("tested_commit", "tested_tree", "merged_commit", "merged_tree", "main_ci_head"):
            if field in record:
                assert isinstance(record[field], str) and re.fullmatch(r"[0-9a-f]{40}", record[field]), "Invalid PR Git identity"
        if "tested_commit" in record:
            tested = expected_pr_source(record, "pr_head")
            candidate = acceptance["candidate_sources"].get(repo)
            # Older progress checkpoints recorded the observed Design merge.
            # This is never sufficient for a passed final or exact-head claim.
            if candidate is not None:
                legacy_merge = not complete and not record.get("head_checks") and record.get("state") == "merged" and candidate == expected_pr_source(record, "merged_main")
                assert candidate == tested or legacy_merge, "PR tested source differs from candidate"
        if record.get("state") == "merged":
            tested, merged = expected_pr_source(record, "pr_head"), expected_pr_source(record, "merged_main")
            assert tested["tree"] == merged["tree"], "Merged tree differs from tested tree"
            if "main_ci_head" in record:
                assert record["main_ci_head"] == merged["commit"]
        if complete:
            assert record.get("state") == "merged", "Required PR remains unmerged"
            assert acceptance["candidate_sources"][repo] == tested
        if complete or "observation" in record:
            observed = json_object(reference_bytes(record.get("observation"), read_bytes))
            assert observed.get("html_url") == record["url"]
            assert observed.get("head", {}).get("sha") == record["tested_commit"]
            assert observed.get("head", {}).get("ref") == "task/DB-CPP-01-linux"
            assert observed.get("base", {}).get("ref") == "main"
            for key in ("head", "base"):
                assert observed.get(key, {}).get("repo", {}).get("full_name") == "IzuSharp/" + repo
            if record.get("state") == "merged":
                assert observed.get("merged") is True and observed.get("state") == "closed" and observed.get("merge_commit_sha") == record["merged_commit"], "Observed PR has not merged at the recorded identity"
        for scope, field in (("pr_head", "head_checks"), ("merged_main", "merged_main_checks")):
            if complete or field in record:
                ci_references(record.get(field), repo, scope, expected_pr_source(record, scope), acceptance, read_bytes)


def validate(graph, acceptance, baseline, read_bytes=artifact, complete=False):
    current = graph["current_execution"]
    assert acceptance.get("schema_version") == baseline.get("schema_version") == 1
    assert current["task"] == acceptance["task"] == baseline["task"] == "DB-CPP-01"
    assert current["branch"] == baseline["branch"] == "task/DB-CPP-01-linux"
    assert current["platforms"] == ["linux-x64"]
    assert acceptance["platform"] == baseline["platform"] == "linux-x64"
    assert acceptance["baseline"] == baseline["observed_merged_main"] == BASELINES, "Frozen starting sources changed"
    assert current["source_main"] == {k: v["commit"] for k, v in BASELINES.items()}
    assert [phase["id"] for phase in current["phases"]] == PHASES, "Missing or reordered migration phase"
    previous_complete = True
    for index, phase in enumerate(current["phases"]):
        assert phase["state"] in {"pending", "in_progress", "complete", "blocked"}
        if "depends_on" in phase:
            assert phase["depends_on"] == PHASES[max(0, index - 1):index]
        if phase["state"] in {"in_progress", "complete"}:
            assert previous_complete, "Migration phase started before prerequisite"
        previous_complete = phase["state"] == "complete"
    assert set(acceptance["checks"]) == CHECKS
    assert acceptance["state"] in {"in_progress", "blocked", "accepted"}
    assert acceptance["publicly_published"] is False
    candidates = acceptance.get("candidate_sources")
    assert isinstance(candidates, dict) and set(candidates) <= REPOSITORIES
    for value in candidates.values():
        identity(value)
    for name, check in acceptance["checks"].items():
        assert check["status"] in {"pending", "passed", "failed", "blocked"}
        assert isinstance(check["evidence"], list)
        assert len({ref["path"] for ref in check["evidence"]}) == len(check["evidence"]), "Duplicate check evidence"
        passed = check["status"] == "passed"
        assert not passed or check["evidence"], "Passed check lacks evidence: " + name
        values = [receipt(ref, name, passed, acceptance, read_bytes) for ref in check["evidence"]]
        if passed:
            claim_sources(name, values, acceptance)
    complete = complete or acceptance["state"] == "accepted"
    if complete:
        assert acceptance["state"] == "accepted"
        assert all(x["status"] == "passed" for x in acceptance["checks"].values())
        assert all(x["state"] == "complete" for x in current["phases"])
        assert set(candidates) == REPOSITORIES
    validate_prs(acceptance, complete, read_bytes)
    for name, scope, field in (("required_pr_checks", "pr_head", "head_checks"), ("merged_main_ci", "merged_main", "merged_main_checks")):
        if acceptance["checks"][name]["status"] == "passed":
            check_refs = {(ref["path"], ref["sha256"]) for ref in acceptance["checks"][name]["evidence"]}
            for repo, record in acceptance["prs"].items():
                ci_references(record.get(field), repo, scope, expected_pr_source(record, scope), acceptance, read_bytes)
                assert {(ref["path"], ref["sha256"]) for ref in record[field]} <= check_refs, "CI claim omits a required PR receipt"
    if complete:
        snapshot = acceptance.get("delivery_snapshot")
        assert isinstance(snapshot, dict), "Accepted delivery lacks a non-circular snapshot"
        plan = acceptance["prs"]["Plan"]
        assert snapshot.get("plan_pr") == plan["url"]
        assert snapshot.get("plan_tested") == expected_pr_source(plan, "pr_head")
        assert snapshot.get("plan_merged") == expected_pr_source(plan, "merged_main")
        assert snapshot.get("record_policy") == "evidence-only-followup"
        assert snapshot.get("self_ci") == "checked-separately", "Evidence record cannot predict its own future CI"
    assert len(graph["nodes"]) == 48 and all(node["status"] == "planned_candidate" for node in graph["nodes"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    graph, acceptance, baseline = read(ROOT / "delivery-graph.json"), read(BATCH / "acceptance.json"), read(BATCH / "baseline.json")
    old = json.loads(subprocess.check_output(["git", "show", BASELINE + ":delivery-graph.json"], cwd=ROOT))
    assert graph["completed_executions"]["DB-Scope-01"] == old["current_execution"]
    for key, value in old.items():
        if key != "current_execution":
            assert graph[key] == value, "Historical delivery graph altered: " + key
    historical = subprocess.check_output(["git", "diff", "--name-only", BASELINE, "--",
        "ledger/evidence/batches/DB-Scope-01", "research-graph.json", "documentation-graph.json",
        "tasks", "research-tasks", "documentation-tasks", "tools/verify_db_scope.py"], cwd=ROOT, text=True)
    assert not historical.strip(), "Historical accepted records changed"
    validate(graph, acceptance, baseline, complete=args.require_complete)
    from verify_db_cpp_negative import negative_controls
    rejected = negative_controls(graph, acceptance, baseline)
    print(json.dumps({"task": "DB-CPP-01", "validation": "passed", "product_acceptance": acceptance["state"],
        "negative_controls": rejected, "negative_controls_only_in_memory": True,
        "github_observations_require_independent_review": True}, indent=2))


if __name__ == "__main__":
    main()
