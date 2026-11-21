#!/usr/bin/env python3
"""Validate the active DB-Scope-01 overlay without relabeling historical acceptance."""
import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "ledger/evidence/batches/DB-Scope-01"
PHASES = ["stop-and-clean", "plan-first", "design-prune", "implementation-prune",
          "linux-regression", "external-consumers", "review-and-merge"]
REQUIRED = {"rust_workspace", "csharp_workspace", "retained_api_and_format",
            "postgresql_regression", "sqlite_regression", "postgresql_package_jit",
            "postgresql_package_aot", "sqlite_package_jit", "sqlite_package_aot",
            "dependency_and_loaded_asset_closure", "no_consumer_rust_invocations",
            "independent_review", "required_pr_checks", "merged_main_ci"}
REPOSITORIES = {"Plan", "NativeWeave-Design", "NativeWeave"}
PREFIX = "ledger/evidence/batches/DB-Scope-01/"
PRODUCT_CLAIMS = REQUIRED - {"independent_review", "required_pr_checks", "merged_main_ci"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def source_identity(value):
    assert isinstance(value, dict) and set(value) == {"commit", "tree"}, "Expected exact source commit and tree"
    assert all(isinstance(item, str) and re.fullmatch("[0-9a-f]{40}", item)
               for item in value.values()), "Invalid source identity"


def canonical_evidence_path(value):
    assert isinstance(value, str) and value.startswith(PREFIX), "Evidence must belong to this task batch"
    path = PurePosixPath(value)
    assert not path.is_absolute() and ".." not in path.parts and str(path) == value and "\\" not in value
    assert value != PREFIX + "acceptance.json", "Acceptance cannot cite itself as evidence"
    return path


def task_bytes(value):
    path = ROOT / canonical_evidence_path(value)
    assert path.resolve().is_relative_to(BATCH.resolve()) and path.is_file(), "Missing task evidence: " + value
    return path.read_bytes()


def evidence_receipt(reference, claim=None, require_pass=False, read_bytes=task_bytes):
    assert isinstance(reference, dict) and set(reference) == {"path", "sha256", "sources"}, "Expected a structured evidence reference"
    canonical_evidence_path(reference["path"])
    assert reference["path"].endswith(".json"), "Evidence references must identify JSON receipts"
    assert re.fullmatch("[0-9a-f]{64}", reference["sha256"]), "Invalid evidence hash"
    sources = reference["sources"]
    assert isinstance(sources, dict) and sources and set(sources) <= REPOSITORIES
    for value in sources.values():
        source_identity(value)
    raw = read_bytes(reference["path"])
    assert sha(raw) == reference["sha256"], "Changed evidence receipt: " + reference["path"]
    receipt = json.loads(raw)
    assert receipt["schema_version"] == 1 and receipt["task"] == "DB-Scope-01"
    assert receipt["platform"] == "linux-x64"
    assert receipt["sources"] == sources, "Receipt and reference sources differ"
    assert receipt["outcome"] in {"passed", "failed", "blocked"}
    assert isinstance(receipt["claims"], list) and receipt["claims"]
    assert len(receipt["claims"]) == len(set(receipt["claims"]))
    assert set(receipt["claims"]) <= REQUIRED
    if claim is not None:
        assert claim in receipt["claims"], "Receipt does not support the claimed gate"
    if require_pass:
        assert receipt["outcome"] == "passed", "A failed or blocked receipt cannot support a pass"
    assert isinstance(receipt["artifacts"], list) and receipt["artifacts"], "Receipt must bind actual logs/results/review artifacts"
    seen = set()
    for artifact in receipt["artifacts"]:
        assert isinstance(artifact, dict) and set(artifact) == {"path", "sha256"}
        canonical_evidence_path(artifact["path"])
        assert artifact["path"] != reference["path"] and artifact["path"] not in seen
        seen.add(artifact["path"])
        assert re.fullmatch("[0-9a-f]{64}", artifact["sha256"])
        assert sha(read_bytes(artifact["path"])) == artifact["sha256"], "Changed raw evidence: " + artifact["path"]
    return receipt


def ci_receipts(references, repository, source, scope, read_bytes):
    assert isinstance(references, list) and references, "Missing source-bound CI receipt"
    claim = "required_pr_checks" if scope == "pr_head" else "merged_main_ci"
    for reference in references:
        receipt = evidence_receipt(reference, claim, True, read_bytes)
        assert receipt["sources"].get(repository) == source, "CI receipt has the wrong source"
        assert receipt.get("required_checks_complete") is True, "Required checks were not completely observed"
        rows = receipt.get("ci")
        assert isinstance(rows, list) and rows, "No actual CI run recorded"
        found = False
        for row in rows:
            assert row["repository"] in REPOSITORIES
            assert re.fullmatch(r"https://github\.com/IzuSharp/" + re.escape(row["repository"]) + r"/actions/runs/[1-9][0-9]*", row["url"])
            assert row["status"] == "completed" and row["conclusion"] == "success", "CI is unfinished or unsuccessful"
            if row["repository"] == repository:
                assert row["head_commit"] == source["commit"] and row["scope"] == scope, "CI run does not bind the required commit/scope"
                if scope == "merged_main":
                    assert row["branch"] == "main", "Merged CI is not a main run"
                found = True
        assert found, "Receipt contains no CI run for the repository"


def validate_prs(acceptance, complete, read_bytes):
    assert set(acceptance["prs"]) == REPOSITORIES
    for repository, record in acceptance["prs"].items():
        if record is None:
            assert not complete, "Missing completed PR: " + repository
            continue
        assert isinstance(record, dict), "PR records cannot be truthy URL strings"
        assert re.fullmatch(r"https://github\.com/IzuSharp/" + re.escape(repository) + r"/pull/[1-9][0-9]*", record["url"])
        for field in ("initial_head", "initial_tree", "head_commit", "head_tree", "merged_commit", "merged_tree"):
            if field in record:
                assert isinstance(record[field], str) and re.fullmatch("[0-9a-f]{40}", record[field]), (repository, field)
        assert record.get("state", "open") in {"open", "closed", "merged"}
        if complete or record.get("state") == "merged":
            assert record.get("state") == "merged", "PR is not merged: " + repository
            head = {"commit": record.get("head_commit"), "tree": record.get("head_tree")}
            merged = {"commit": record.get("merged_commit"), "tree": record.get("merged_tree")}
            source_identity(head)
            source_identity(merged)
            ci_receipts(record.get("head_checks"), repository, head, "pr_head", read_bytes)
            ci_receipts(record.get("merged_main_checks"), repository, merged, "merged_main", read_bytes)
            if repository != "Plan":
                candidate = acceptance["candidate_sources"].get(repository)
                assert candidate is not None, "Missing tested/reviewed source identity"
                assert candidate["tree"] == head["tree"] == merged["tree"], "PR content differs from tested/reviewed source"


def validate_claim_sources(name, receipts, acceptance):
    candidates = acceptance["candidate_sources"]
    required = {"NativeWeave"} if name in PRODUCT_CLAIMS else {"NativeWeave", "NativeWeave-Design"}
    if name in {"required_pr_checks", "merged_main_ci"}:
        required = REPOSITORIES
    covered = set()
    for receipt in receipts:
        for repository, observed in receipt["sources"].items():
            if name in {"required_pr_checks", "merged_main_ci"}:
                record = acceptance["prs"].get(repository)
                assert isinstance(record, dict), "CI claim has no PR record"
                prefix = "head" if name == "required_pr_checks" else "merged"
                expected = {"commit": record.get(prefix + "_commit"), "tree": record.get(prefix + "_tree")}
                source_identity(expected)
                assert observed == expected, "CI claim source differs from PR identity"
            elif repository in required:
                assert candidates.get(repository) is not None and observed == candidates[repository], "Claim source differs from candidate identity"
            covered.add(repository)
    assert required <= covered, "Passed claim lacks required repository source coverage"


def evidence_negative_controls(graph, acceptance):
    """Use explicit in-memory fixtures; none are written as product evidence."""
    data = copy.deepcopy(acceptance)
    data["state"] = "in_progress"
    data["claims"] = {name: {"status": "pending", "evidence": []} for name in REQUIRED}
    data["prs"] = {repository: None for repository in REPOSITORIES}
    data["candidate_sources"] = {repository: None for repository in REPOSITORIES}
    source = {"commit": graph["current_execution"]["source_main"]["NativeWeave"], "tree": "1" * 40}
    data["candidate_sources"]["NativeWeave"] = source
    raw_path = PREFIX + "selftest/in-memory-only.log"
    receipt_path = PREFIX + "selftest/in-memory-only.json"
    raw = b"Synthetic verifier fixture only; no product execution.\n"
    receipt = {"schema_version": 1, "task": "DB-Scope-01", "platform": "linux-x64",
               "claims": ["sqlite_package_jit"], "outcome": "passed",
               "sources": {"NativeWeave": source},
               "artifacts": [{"path": raw_path, "sha256": sha(raw)}]}
    encoded = json.dumps(receipt, sort_keys=True).encode()
    reference = {"path": receipt_path, "sha256": sha(encoded), "sources": receipt["sources"]}
    data["claims"]["sqlite_package_jit"] = {"status": "passed", "evidence": [reference]}
    fixture = {receipt_path: encoded, raw_path: raw}

    def fixture_reader(path):
        canonical_evidence_path(path)
        assert path in fixture, "Missing in-memory test fixture"
        return fixture[path]

    validate(graph, data, read_bytes=fixture_reader)
    rejected = []
    for case in ("nonexistent_evidence", "mismatched_receipt_hash", "mismatched_artifact_hash",
                 "mismatched_reference_source", "mismatched_candidate_source", "incomplete_merged_pr"):
        changed = copy.deepcopy(data)
        item = changed["claims"]["sqlite_package_jit"]["evidence"][0]
        if case == "nonexistent_evidence":
            item["path"] = PREFIX + "selftest/does-not-exist.json"
        elif case == "mismatched_receipt_hash":
            item["sha256"] = "0" * 64
        elif case == "mismatched_artifact_hash":
            fixture[raw_path] = raw + b"changed"
        elif case == "mismatched_reference_source":
            item["sources"]["NativeWeave"]["commit"] = "2" * 40
        elif case == "mismatched_candidate_source":
            changed["candidate_sources"]["NativeWeave"]["tree"] = "2" * 40
        else:
            changed["prs"]["NativeWeave"] = {
                "url": "https://github.com/IzuSharp/NativeWeave/pull/999999", "state": "merged"}
        try:
            validate(graph, changed, read_bytes=fixture_reader)
        except AssertionError:
            rejected.append(case)
        else:
            raise AssertionError("Invalid evidence accepted: " + case)
        finally:
            fixture[raw_path] = raw

    # Exercise the full accepted-state path too. These identities and runs are
    # deliberately synthetic and exist only in memory, never in the ledger.
    final_graph = copy.deepcopy(graph)
    for phase in final_graph["current_execution"]["phases"]:
        phase["state"] = "complete"
    final = copy.deepcopy(data)
    final["state"] = "accepted"
    final["candidate_sources"] = {
        repository: {"commit": str(index + 1) * 40, "tree": str(index + 4) * 40}
        for index, repository in enumerate(sorted(REPOSITORIES))
    }

    def add_fixture(name, claims, sources, **fields):
        path = PREFIX + "selftest/" + name + ".json"
        value = {"schema_version": 1, "task": "DB-Scope-01", "platform": "linux-x64",
                 "claims": sorted(claims), "outcome": "passed", "sources": sources,
                 "artifacts": [{"path": raw_path, "sha256": sha(raw)}], **fields}
        fixture[path] = json.dumps(value, sort_keys=True).encode()
        return {"path": path, "sha256": sha(fixture[path]), "sources": sources}

    product = add_fixture("product", PRODUCT_CLAIMS,
                          {"NativeWeave": final["candidate_sources"]["NativeWeave"]})
    review = add_fixture("review", {"independent_review"}, {
        repository: final["candidate_sources"][repository]
        for repository in ("NativeWeave", "NativeWeave-Design")})
    for name in PRODUCT_CLAIMS:
        final["claims"][name] = {"status": "passed", "evidence": [product]}
    final["claims"]["independent_review"] = {"status": "passed", "evidence": [review]}
    for name in ("required_pr_checks", "merged_main_ci"):
        final["claims"][name] = {"status": "passed", "evidence": []}
    for index, repository in enumerate(sorted(REPOSITORIES)):
        head = final["candidate_sources"][repository]
        merged = {"commit": str(index + 7) * 40, "tree": head["tree"]}
        record = {"url": "https://github.com/IzuSharp/" + repository + "/pull/999999",
                  "state": "merged", "head_commit": head["commit"], "head_tree": head["tree"],
                  "merged_commit": merged["commit"], "merged_tree": merged["tree"]}
        for scope, claim, field, source in (
            ("pr_head", "required_pr_checks", "head_checks", head),
            ("merged_main", "merged_main_ci", "merged_main_checks", merged),
        ):
            reference = add_fixture(repository + "-" + scope, {claim}, {repository: source},
                                    required_checks_complete=True, ci=[{
                                        "repository": repository,
                                        "url": "https://github.com/IzuSharp/" + repository + "/actions/runs/999999",
                                        "head_commit": source["commit"], "scope": scope,
                                        "branch": "main" if scope == "merged_main" else "task/DB-Scope-01-linux",
                                        "status": "completed", "conclusion": "success"}])
            record[field] = [reference]
            final["claims"][claim]["evidence"].append(reference)
        final["prs"][repository] = record
    validate(final_graph, final, complete=True, read_bytes=fixture_reader)
    for case in ("mismatched_ci_commit", "incomplete_required_ci", "wrong_merged_branch", "changed_merged_tree"):
        changed = copy.deepcopy(final)
        reference = changed["prs"]["NativeWeave"]["merged_main_checks"][0]
        path = reference["path"]
        original = fixture[path]
        value = json.loads(original)
        if case == "mismatched_ci_commit":
            value["ci"][0]["head_commit"] = "a" * 40
        elif case == "incomplete_required_ci":
            value["required_checks_complete"] = False
        elif case == "wrong_merged_branch":
            value["ci"][0]["branch"] = "task/DB-Scope-01-linux"
        else:
            changed["prs"]["NativeWeave"]["merged_tree"] = "a" * 40
        fixture[path] = json.dumps(value, sort_keys=True).encode()
        reference["sha256"] = sha(fixture[path])
        try:
            validate(final_graph, changed, complete=True, read_bytes=fixture_reader)
        except AssertionError:
            rejected.append(case)
        else:
            raise AssertionError("Invalid final evidence accepted: " + case)
        finally:
            fixture[path] = original
    return rejected


def validate(graph, acceptance, complete=False, read_bytes=task_bytes):
    current = graph["current_execution"]
    assert current["task"] == acceptance["task"] == "DB-Scope-01"
    assert current["branch"] == "task/DB-Scope-01-linux"
    assert current["platforms"] == ["linux-x64"]
    assert acceptance["platform"] == "linux-x64"
    assert acceptance["performance_work_authorized"] is False
    assert acceptance["evidence_schema_version"] == 1
    assert set(acceptance["candidate_sources"]) == REPOSITORIES
    for source in acceptance["candidate_sources"].values():
        if source is not None:
            source_identity(source)
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
        receipts = [evidence_receipt(reference, name, claim["status"] == "passed", read_bytes)
                    for reference in claim["evidence"]]
        if claim["status"] == "passed":
            assert claim["evidence"], f"Unbound pass: {name}"
            validate_claim_sources(name, receipts, acceptance)
    assert acceptance["state"] in {"pending", "in_progress", "blocked", "accepted"}
    if complete or acceptance["state"] == "accepted":
        assert all(claim["status"] == "passed" for claim in acceptance["claims"].values())
        assert all(phase["state"] == "complete" for phase in current["phases"])
    validate_prs(acceptance, complete or acceptance["state"] == "accepted", read_bytes)
    for claim, scope, field, prefix in (
        ("required_pr_checks", "pr_head", "head_checks", "head"),
        ("merged_main_ci", "merged_main", "merged_main_checks", "merged"),
    ):
        if acceptance["claims"][claim]["status"] == "passed":
            for repository, record in acceptance["prs"].items():
                assert isinstance(record, dict), "CI pass requires each PR record"
                source = {"commit": record.get(prefix + "_commit"), "tree": record.get(prefix + "_tree")}
                source_identity(source)
                ci_receipts(record.get(field), repository, source, scope, read_bytes)
    # The current overlay does not turn original design authorization into
    # product acceptance, or rewrite the historical 48 individual task records.
    assert len(graph["nodes"]) == 48
    assert all(node["status"] == "planned_candidate" for node in graph["nodes"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    graph_text = (ROOT / "delivery-graph.json").read_text()
    graph = json.loads(graph_text)
    acceptance = json.loads((BATCH / "acceptance.json").read_text())
    validate(graph, acceptance, args.require_complete)
    baseline = graph["current_execution"]["source_main"]["Plan"]
    original_bytes = subprocess.check_output(
        ["git", "show", baseline + ":delivery-graph.json"], cwd=ROOT)
    original = json.loads(original_bytes)
    historical = {key: value for key, value in graph.items() if key != "current_execution"}
    assert historical == original, "Historical delivery graph was changed"
    original_prefix = graph_text.rsplit(',\n  "current_execution":', 1)[0] + "\n}\n"
    assert original_prefix.encode() == original_bytes, "Historical delivery graph bytes were rewritten"
    preserved = ["research-graph.json", "documentation-graph.json", "source-driven-baseline.json",
                 "research-tasks", "documentation-tasks", "tasks", "fragments", "schemas"]
    changed = subprocess.check_output(["git", "diff", "--name-only", baseline, "--", *preserved],
                                      cwd=ROOT, text=True).strip()
    assert not changed, "Historical graph/packet/schema inputs changed: " + changed
    evidence_changes = subprocess.check_output(["git", "diff", "--name-only", baseline, "--", "ledger"],
                                               cwd=ROOT, text=True).splitlines()
    assert all(path.startswith("ledger/evidence/batches/DB-Scope-01/") for path in evidence_changes), \
        "An existing historical evidence record was changed"
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
    evidence_mutations = evidence_negative_controls(graph, acceptance)
    print(json.dumps({"task": "DB-Scope-01", "structural_validation": "passed",
                      "negative_controls": mutations, "evidence_negative_controls": evidence_mutations,
                      "evidence_controls_use_only_in_memory_fixtures": True,
                      "product_acceptance": acceptance["state"]}, indent=2))


if __name__ == "__main__":
    main()
