"""Synthetic verifier controls held only in memory, never execution evidence."""
import copy
import json

import verify_db_cpp as verifier
from db_cpp_evidence import BASELINES, CI_PRODUCT_CLAIMS, CONSUMER_FILES, PACKAGES, PREFIX, REPOSITORIES, ROWS, SHARED_COMPARISON_INPUTS, STEPS, WORKFLOWS, canonical, sha


def encoded(value):
    return (json.dumps(value, sort_keys=True) + "\n").encode()


class Fixture:
    def __init__(self, graph, acceptance):
        self.graph, self.acceptance = copy.deepcopy(graph), copy.deepcopy(acceptance)
        self.files = {}
        self.paths = {}
        for phase in self.graph["current_execution"]["phases"]:
            phase["state"] = "complete"
        data = self.acceptance
        data["state"] = "accepted"
        data["checks"] = {name: {"status": "passed", "evidence": []} for name in verifier.CHECKS}
        data["checks"]["baseline_reference_provenance"]["evidence"] = [copy.deepcopy(verifier.LEGACY_REFERENCE)]
        data["candidate_sources"] = {repo: {"commit": str(index + 1) * 40, "tree": str(index + 4) * 40}
                                     for index, repo in enumerate(sorted(REPOSITORIES))}
        data["prs"] = {}
        for index, repo in enumerate(sorted(REPOSITORIES)):
            head = data["candidate_sources"][repo]
            merged = {"commit": str(index + 7) * 40, "tree": head["tree"]}
            record = {"url": "https://github.com/IzuSharp/" + repo + "/pull/999999", "state": "merged",
                      "tested_commit": head["commit"], "tested_tree": head["tree"],
                      "merged_commit": merged["commit"], "merged_tree": merged["tree"]}
            observed = {"html_url": record["url"], "head": {"sha": head["commit"], "ref": "task/DB-CPP-01-linux", "repo": {"full_name": "IzuSharp/" + repo}},
                        "base": {"ref": "main", "repo": {"full_name": "IzuSharp/" + repo}},
                        "state": "closed", "merged": True, "merge_commit_sha": merged["commit"]}
            record["observation"] = self.put(repo + "-pr", observed)
            data["prs"][repo] = record
            for scope, source, claim, field in (
                    ("pr_head", head, "required_pr_checks", "head_checks"),
                    ("merged_main", merged, "merged_main_ci", "merged_main_checks")):
                refs = []
                for offset, (workflow, job_names) in enumerate(WORKFLOWS[repo].items()):
                    run_id = 900000 + index * 100 + offset * 10 + (1 if scope == "pr_head" else 2)
                    url = "https://github.com/IzuSharp/" + repo + "/actions/runs/" + str(run_id)
                    api = "https://api.github.com/repos/IzuSharp/" + repo + "/actions/runs/" + str(run_id)
                    branch = "main" if scope == "merged_main" else "task/DB-CPP-01-linux"
                    run = {"id": run_id, "html_url": url, "url": api, "jobs_url": api + "/jobs", "path": workflow,
                           "repository": {"full_name": "IzuSharp/" + repo}, "head_sha": source["commit"],
                           "head_commit": {"id": source["commit"], "tree_id": source["tree"]}, "head_branch": branch,
                           "event": "push" if scope == "merged_main" else "pull_request", "pull_requests": [],
                           "status": "completed", "conclusion": "success", "run_attempt": 1}
                    jobs = []
                    for job_index, name in enumerate(sorted(job_names)):
                        job_id = run_id * 100 + job_index
                        skipped = scope == "merged_main" and name == "security / Dependency review"
                        jobs.append({"id": job_id, "name": name, "run_id": run_id, "run_attempt": 1,
                                     "head_sha": source["commit"], "head_branch": branch, "run_url": api,
                                     "url": "https://api.github.com/repos/IzuSharp/" + repo + "/actions/jobs/" + str(job_id),
                                     "html_url": url + "/job/" + str(job_id), "status": "completed",
                                     "conclusion": "skipped" if skipped else "success",
                                     "steps": [{"name": step, "status": "completed", "conclusion": "success"} for step in sorted(STEPS.get(name, set()))]})
                    stem = repo + "-" + scope + "-" + str(offset)
                    run_ref = self.put(stem + "-run", run)
                    jobs_ref = self.put(stem + "-jobs", {"total_count": len(jobs), "jobs": jobs})
                    claims = {claim} | (CI_PRODUCT_CLAIMS if repo == "NativeWeave" and scope == "pr_head" else set())
                    ref = self.add_receipt(stem, claims, {repo: source}, [dict(run_ref, kind="github-run"), dict(jobs_ref, kind="github-jobs")],
                        required_checks_complete=True, ci=[{"repository": repo, "scope": scope, "url": url, "workflow_path": workflow, "run": run_ref, "jobs": jobs_ref}])
                    refs.append(ref)
                    if repo == "NativeWeave" and scope == "pr_head":
                        self.paths.update(product_receipt=ref["path"], product_run=run_ref["path"], product_jobs=jobs_ref["path"])
                        for name in CI_PRODUCT_CLAIMS:
                            data["checks"][name]["evidence"] = [ref]
                    if repo == "Plan" and scope == "merged_main":
                        self.paths["plan_main_run"] = run_ref["path"]
                record[field] = refs
                data["checks"][claim]["evidence"].extend(refs)
        product = data["candidate_sources"]["NativeWeave"]
        common_rows = {row: {"passed": True, "comparisons": ["fresh-seed", "old-database-read", "old-database-continue", "changed-dto-same-native"],
                            "dto_change": {"native_sha256_unchanged": True}} for row in sorted(ROWS)}
        consumer = {name: "a" * 64 for name in CONSUMER_FILES}
        abi_inputs = {"probe": "b" * 64}
        abi = {"passed": True, "differences": [], "retired_counts": [0] * 6, "cases": {str(i): {} for i in range(24)}}
        runs = {}
        for phase, commit in (("baseline", BASELINES["NativeWeave"]["commit"]), ("candidate", product["commit"])):
            packages = {name: {"sha256": "c" * 64, "repository": {"commit": commit, "url": "https://github.com/IzuSharp/NativeWeave"}} for name in PACKAGES}
            actual_rows = copy.deepcopy(common_rows)
            for row in actual_rows.values():
                row["snapshots"] = {"seed" if phase == "baseline" else "old_seed": {"sha256": "d" * 64, "bytes": 40000}}
            native_hashes = {"libnw_database_sqlite.so": "e" * 64, "libnw_database_postgresql.so": "f" * 64}
            build_names = {"jit", "aot"} | ({"jit-dto-v2", "aot-dto-v2"} if phase == "candidate" else set())
            builds = {name: {"native_sha256": native_hashes,
                            "source_sha256": dict(consumer, **({"DtoMapping.cs": "b" * 64} if name.endswith("-dto-v2") else {}))} for name in build_names}
            run = {"passed": True, "source_identity": {"commit": product["commit"], "scope_status": ""},
                   "phase": phase, "commands": [{"exit_code": 0}], "required_rows": sorted(ROWS), "rows": actual_rows,
                   "rust_or_cpp_build_tools_invoked": False, "packages": packages, "source_sha256": consumer,
                   "abi": abi, "abi_inputs_sha256": abi_inputs, "native_sha256": native_hashes, "builds": builds,
                   **{field: "b" * 64 for field in SHARED_COMPARISON_INPUTS}}
            runs[phase] = {"ref": self.put("migration-" + phase, run), "value": run}
        comparison = {"passed": True, "rows": runs["candidate"]["value"]["rows"], "rust_commit": BASELINES["NativeWeave"]["commit"],
                      "cpp_packages": runs["candidate"]["value"]["packages"], "same_consumer_source_sha256": consumer,
                      "candidate_result_sha256": runs["candidate"]["ref"]["sha256"], "baseline_result_sha256": runs["baseline"]["ref"]["sha256"],
                      "abi_compatibility": {"candidate": abi, "baseline": abi, "inputs_sha256": abi_inputs}}
        comparison_ref = self.put("comparison", comparison)
        migration_claims = set(verifier.RESULT_KINDS) - CI_PRODUCT_CLAIMS - {"independent_review"}
        comparison_receipt = self.add_receipt("migration-receipt", migration_claims, {"NativeWeave": product},
            [dict(run["ref"], kind="migration-run") for run in runs.values()] + [dict(comparison_ref, kind="migration-comparison")])
        for name in migration_claims:
            data["checks"][name]["evidence"] = [comparison_receipt]
        self.paths.update(candidate_run=runs["candidate"]["ref"]["path"], comparison=comparison_ref["path"], migration_receipt=comparison_receipt["path"])
        review_sources = {repo: data["candidate_sources"][repo] for repo in ("NativeWeave", "NativeWeave-Design")}
        review = self.put("review", {"status": "passed", "sources": review_sources, "reviewer": "in-memory-test-reviewer",
                                    "authorship_disclosure": "Synthetic parser test only; not a real review", "blocking_findings": []})
        review_receipt = self.add_receipt("review-receipt", {"independent_review"}, review_sources, [dict(review, kind="review")])
        data["checks"]["independent_review"]["evidence"] = [review_receipt]
        plan = data["prs"]["Plan"]
        data["delivery_snapshot"] = {"plan_pr": plan["url"], "plan_tested": verifier.expected_pr_source(plan, "pr_head"),
                                     "plan_merged": verifier.expected_pr_source(plan, "merged_main"),
                                     "record_policy": "evidence-only-followup", "self_ci": "checked-separately"}

    def put(self, name, value):
        path = PREFIX + "selftest/in-memory-only-" + name + ".json"
        self.files[path] = encoded(value)
        return {"path": path, "sha256": sha(self.files[path])}

    def add_receipt(self, name, claims, sources, artifacts, **extra):
        return self.put(name, {"schema_version": 2, "task": "DB-CPP-01", "platform": "linux-x64", "outcome": "passed",
                               "claims": sorted(claims), "sources": sources, "artifacts": artifacts, **extra})

    def read(self, path):
        canonical(path)
        if path in self.files:
            return self.files[path]
        # The only real ledger reads are the previously accepted fixed Rust
        # reference bytes. Synthetic execution evidence is never written.
        assert path in {verifier.LEGACY_REFERENCE["path"], PREFIX + "rust-reference-provenance.json", PREFIX + "rust-reference-packages.json"}
        return verifier.artifact(path)

    def change(self, path, mutate):
        value = json.loads(self.files[path])
        mutate(value)
        self.files[path] = encoded(value)
        pending = [path]

        def rebind(value, changed, digest):
            if isinstance(value, dict):
                if value.get("path") == changed and "sha256" in value:
                    value["sha256"] = digest
                for item in value.values():
                    rebind(item, changed, digest)
            elif isinstance(value, list):
                for item in value:
                    rebind(item, changed, digest)

        while pending:
            changed = pending.pop()
            digest = sha(self.files[changed])
            rebind(self.acceptance, changed, digest)
            for current, raw in list(self.files.items()):
                if current == changed:
                    continue
                value = json.loads(raw)
                rebind(value, changed, digest)
                updated = encoded(value)
                if raw != updated:
                    self.files[current] = updated
                    pending.append(current)

    def change_candidate(self, mutate, sync_rows=False, sync_abi=False):
        """Rehash the actual run and its summary so semantic checks must reject."""
        path = self.paths["candidate_run"]
        self.change(path, mutate)
        candidate = json.loads(self.files[path])

        def update_summary(value):
            value["candidate_result_sha256"] = sha(self.files[path])
            if sync_rows:
                value["rows"] = candidate["rows"]
            if sync_abi:
                value["abi_compatibility"]["candidate"] = candidate["abi"]

        self.change(self.paths["comparison"], update_summary)


def negative_controls(graph, acceptance, baseline):
    valid = Fixture(graph, acceptance)
    verifier.validate(valid.graph, valid.acceptance, baseline, read_bytes=valid.read, complete=True)
    mutations = {
        "wrong_receipt_source": lambda f: f.change(f.paths["migration_receipt"], lambda d: d["sources"].update(NativeWeave=BASELINES["NativeWeave"])),
        "wrong_actual_result_source": lambda f: f.change(f.paths["candidate_run"], lambda d: d["source_identity"].update(commit=BASELINES["NativeWeave"]["commit"])),
        "passed_wrapper_failed_actual_result": lambda f: f.change(f.paths["candidate_run"], lambda d: d.update(passed=False)),
        "dirty_actual_source": lambda f: f.change(f.paths["candidate_run"], lambda d: d["source_identity"].update(scope_status=" M source.cpp")),
        "missing_runtime_cell": lambda f: f.change(f.paths["candidate_run"], lambda d: d["rows"].pop("sqlite-aot")),
        "failed_runtime_cell": lambda f: f.change(f.paths["candidate_run"], lambda d: d["rows"]["sqlite-aot"].update(passed=False)),
        "missing_package": lambda f: f.change(f.paths["candidate_run"], lambda d: d["packages"].pop("NativeWeave.Core")),
        "comparison_wrong_result_hash": lambda f: f.change(f.paths["comparison"], lambda d: d.update(candidate_result_sha256="0" * 64)),
        "comparison_wrong_executed_rows": lambda f: f.change(f.paths["comparison"], lambda d: d["rows"]["sqlite-aot"].update(unexecuted=True)),
        "different_sdk_configuration": lambda f: f.change_candidate(lambda d: d.update(global_json_sha256="d" * 64)),
        "different_driver_source": lambda f: f.change_candidate(lambda d: d.update(controller_sha256="d" * 64)),
        "different_database_version": lambda f: f.change_candidate(lambda d: d.update(postgres_version="a different server version")),
        "different_actual_abi_outcome": lambda f: f.change_candidate(lambda d: d["abi"]["cases"]["0"].update(status=99), sync_abi=True),
        "different_old_snapshot": lambda f: f.change_candidate(lambda d: d["rows"]["sqlite-aot"]["snapshots"]["old_seed"].update(sha256="0" * 64), sync_rows=True),
        "dto_build_changed_native_hash": lambda f: f.change_candidate(lambda d: d["builds"]["aot-dto-v2"]["native_sha256"].update({"libnw_database_sqlite.so": "0" * 64})),
        "forged_ci_summary_without_runs": lambda f: f.change(f.paths["product_receipt"], lambda d: d.update(ci=[])),
        "incomplete_required_checks": lambda f: f.change(f.paths["product_receipt"], lambda d: d.update(required_checks_complete=False)),
        "wrong_ci_commit": lambda f: f.change(f.paths["product_run"], lambda d: d.update(head_sha="a" * 40)),
        "wrong_ci_tree": lambda f: f.change(f.paths["product_run"], lambda d: d["head_commit"].update(tree_id="a" * 40)),
        "unfinished_ci": lambda f: f.change(f.paths["product_run"], lambda d: d.update(status="in_progress", conclusion=None)),
        "failed_ci": lambda f: f.change(f.paths["product_run"], lambda d: d.update(conclusion="failure")),
        "truncated_jobs_page": lambda f: f.change(f.paths["product_jobs"], lambda d: d["jobs"].pop()),
        "omitted_job_adjusted_count": lambda f: f.change(f.paths["product_jobs"], lambda d: (d["jobs"].pop(), d.update(total_count=5))),
        "wrong_ci_attempt": lambda f: f.change(f.paths["product_jobs"], lambda d: d["jobs"][0].update(run_attempt=2)),
        "skipped_required_job": lambda f: f.change(f.paths["product_jobs"], lambda d: d["jobs"][0].update(conclusion="skipped")),
        "skipped_required_step": lambda f: f.change(f.paths["product_jobs"], lambda d: next(j for j in d["jobs"] if j["name"] == "build / Build, package and Native AOT")["steps"][0].update(conclusion="skipped")),
        "wrong_merged_main_branch": lambda f: f.change(f.paths["plan_main_run"], lambda d: d.update(head_branch="task/DB-CPP-01-linux")),
        "unmerged_actual_pr": lambda f: f.change(f.acceptance["prs"]["Plan"]["observation"]["path"], lambda d: d.update(merged=False)),
        "missing_plan_main_ci": lambda f: f.acceptance["prs"]["Plan"].pop("merged_main_checks"),
        "changed_merged_tree": lambda f: f.acceptance["prs"]["NativeWeave"].update(merged_tree="a" * 40),
        "empty_phases": lambda f: f.graph["current_execution"].update(phases=[]),
        "phase_out_of_order": lambda f: f.graph["current_execution"]["phases"][1].update(state="pending"),
        "missing_delivery_snapshot": lambda f: f.acceptance.pop("delivery_snapshot"),
        "circular_future_self_ci": lambda f: f.acceptance["delivery_snapshot"].update(self_ci="predicted-success"),
        "wrong_delivered_plan_snapshot": lambda f: f.acceptance["delivery_snapshot"]["plan_merged"].update(commit="a" * 40),
        "passed_without_evidence": lambda f: f.acceptance["checks"]["native_sanitizers"].update(evidence=[]),
        "baseline_moved": lambda f: f.acceptance["baseline"]["NativeWeave"].update(commit="a" * 40),
    }
    rejected = []
    for name, mutate in mutations.items():
        fixture = Fixture(graph, acceptance)
        mutate(fixture)
        try:
            verifier.validate(fixture.graph, fixture.acceptance, baseline, read_bytes=fixture.read, complete=True)
        except AssertionError:
            rejected.append(name)
        else:
            raise AssertionError("Invalid migration evidence accepted: " + name)
    return rejected
