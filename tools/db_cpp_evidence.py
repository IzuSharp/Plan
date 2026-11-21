"""Source and result checks for DB-CPP-01's finite Linux acceptance record.

This is an offline consistency verifier, not an attestation service. GitHub API
observations must still be obtained and independently reviewed through GitHub.
"""
import hashlib
import json
import re
from pathlib import PurePosixPath

PREFIX = "ledger/evidence/batches/DB-CPP-01/"
REPOSITORIES = {"NativeWeave", "NativeWeave-Design", "Plan"}
ROWS = {"sqlite-jit", "sqlite-aot", "postgresql-jit", "postgresql-aot"}
PACKAGES = {"NativeWeave.Core", "NativeWeave.Data", "NativeWeave.Data.Streaming", "NativeWeave.Database",
            "NativeWeave.Database.PostgreSql", "NativeWeave.Database.PostgreSql.Native",
            "NativeWeave.Database.Sqlite", "NativeWeave.Database.Sqlite.Native",
            "NativeWeave.Database.Transactions", "NativeWeave.Interop.Abi", "NativeWeave.Query.Binding",
            "NativeWeave.Query.Generator"}
CONSUMER_FILES = {"Consumer.csproj", "DtoMapping.cs", "Models.cs", "Program.cs"}
SHARED_COMPARISON_INPUTS = {
    "controller_sha256", "identity_helper_sha256", "required_cases_sha256", "reference_lock_sha256",
    "global_json_sha256", "dto_variant_sha256", "postgres_version", "sqlite_observer_version", "sdk_feed_sha256"}
BASELINES = {
    "NativeWeave": {"commit": "465cd0f90e6af05ec50eb581156240377cf0825b", "tree": "5f5d74ec7cfa502a4f8d119bb89e2e2776d4b65b"},
    "NativeWeave-Design": {"commit": "8298dc4128b745cf1809bad0c3cf02c45eb7f522", "tree": "74f886a74a38d0478d1c4b4a22ea17383dfd0424"},
    "Plan": {"commit": "1fe52a8bd792ccdbb4bbea17ba59b0ad0c24349d", "tree": "1124fde6d1b76cdf8f36ce4f10457b5386461990"},
}
WORKFLOWS = {
    "NativeWeave": {".github/workflows/ci.yml": {
        "build / Build, package and Native AOT", "security / Dependency review",
        "security / Secret scan", "security / CodeQL (csharp)", "security / CodeQL (python)", "Verify"}},
    "NativeWeave-Design": {
        ".github/workflows/public-api-design.yml": {"api-interface (ubuntu-24.04)"},
        ".github/workflows/english-translation.yml": {"translation-integrity"}},
    "Plan": {".github/workflows/native-slices-final-check.yml": {"paired-integrity"}},
}
STEPS = {
    "build / Build, package and Native AOT": {
        "Install native build prerequisites and pinned Clang tools",
        "Prepare pinned PostgreSQL tools for real TLS and process fault oracles",
        "Verify database workspaces, API, regressions and actual package JIT/AOT consumers",
        "Reject generated source or dependency drift",
        "Verify shared ASan and UBSan preset with leak detection enabled",
        "Verify retained cross-version compatibility and Core property/fuzz gates",
        "Verify retained Core package closure and minimum CPU/runtime transfer",
        "Reject shared packaging source or dependency drift",
        "Verify database release recovery, no-Rust SDK consumption and runtime-only transfer",
        "Reject database packaging source or dependency drift",
        "Build and package C++ assets in a fresh Linux image without Rust",
        "Retain verification logs and evidence", "Retain the exact verified database candidate"},
    "Verify": {"Require every gate"},
    "api-interface (ubuntu-24.04)": {
        "Validate migration decision and unchanged accepted database scope at its frozen input"},
    "translation-integrity": {"Verify unchanged complete historical acceptance and negative controls"},
    "paired-integrity": {
        "Verify current C++ migration progress and preserved historical records",
        "Run unchanged completed database-scope acceptance gates",
        "Run every unchanged historical provenance and graph gate"},
}
CI_PRODUCT_CLAIMS = {
    "native_release_clang", "native_sanitizers", "native_format_tidy", "retained_native_assertions",
    "managed_api_and_regressions", "failure_cancellation_resources", "rust_free_build_pack_run",
    "package_abi_load_closure", "postgresql_behavior_parity", "sqlite_behavior_parity",
}
KINDS = {"native-build", "package-manifest", "component-result", "compatibility-result",
         "regression-result", "verification-result", "migration-run", "migration-comparison",
         "command-result", "review", "log", "github-run", "github-jobs", "github-pr"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    assert isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value), "Invalid SHA-256"


def identity(value):
    assert isinstance(value, dict) and set(value) == {"commit", "tree"}, "Invalid source identity"
    assert all(isinstance(x, str) and re.fullmatch(r"[0-9a-f]{40}", x) for x in value.values()), "Invalid Git identity"


def canonical(path):
    assert isinstance(path, str) and "\\" not in path, "Invalid evidence path"
    p = PurePosixPath(path)
    assert str(p) == path and not p.is_absolute() and ".." not in p.parts and path.startswith(PREFIX), "Evidence outside batch"
    assert path != PREFIX + "acceptance.json", "Acceptance cannot cite itself"


def reference_bytes(reference, read_bytes):
    assert isinstance(reference, dict) and set(reference) == {"path", "sha256"}, "Invalid artifact reference"
    canonical(reference["path"])
    digest(reference["sha256"])
    raw = read_bytes(reference["path"])
    assert sha(raw) == reference["sha256"], "Evidence bytes changed: " + reference["path"]
    return raw


def json_object(raw):
    value = json.loads(raw)
    assert isinstance(value, dict), "Expected JSON object"
    return value


def unwrap(raw):
    value = json_object(raw)
    if "sanitized" in value:
        assert set(value) == {"sanitized", "source_artifact_sha256", "data"} and value["sanitized"] is True
        digest(value["source_artifact_sha256"])
        assert isinstance(value["data"], dict)
        return value["data"], value["source_artifact_sha256"]
    return value, sha(raw)


def terminal(value):
    """Only actual top-level terminal fields; expected-failure probes are nested."""
    found = False
    for key in ("passed", "status", "result"):
        if key in value:
            found = True
            expected = True if key == "passed" else "passed"
            assert value[key] == expected and type(value[key]) is type(expected), "Actual result is not passed: " + key
    assert found, "Actual result has no terminal conclusion"
    if "failures" in value:
        assert value["failures"] == [], "Actual result contains failures"


def commands(value, key="commands"):
    rows = value.get(key)
    assert isinstance(rows, list) and rows, "Missing actual command results"
    for row in rows:
        assert isinstance(row, dict)
        keys = {key for key in ("exitCode", "exit_code", "returncode") if key in row}
        assert keys, "Command has no exit status"
        assert all(type(row[key]) is int and row[key] == 0 for key in keys), "Actual command failed"


def product_source(value, expected, required=True):
    found = False
    for key in ("sourceCommit", "source_commit"):
        if key in value:
            found = True
            assert value[key] == expected["commit"], "Actual artifact source differs from candidate"
    if "source" in value:
        found = True
        source = value["source"]
        assert isinstance(source, dict)
        assert source.get("commit") == expected["commit"] and source.get("tree") == expected["tree"], "Actual source/tree differs"
    if "source_identity" in value:
        found = True
        source = value["source_identity"]
        assert source.get("commit") == expected["commit"] and source.get("scope_status") == "", "Dirty or different actual controller source"
    if "sourceTree" in value:
        assert value["sourceTree"] == expected["tree"], "Actual source tree differs"
    for key in ("sourceDirty", "source_dirty"):
        if key in value:
            assert value[key] is False, "Artifact built from dirty source"
    for key in ("sourceStable", "source_stable"):
        if key in value:
            assert value[key] is True, "Source changed during execution"
    for key in ("prepare_only", "prepareOnly"):
        if key in value:
            assert value[key] is False, "Preparation is not acceptance"
    assert found or not required, "Actual result does not identify its source"


def packages(values, commit):
    assert isinstance(values, dict) and set(values) == PACKAGES, "Missing actual package identities"
    for value in values.values():
        repo = value.get("repository", {})
        assert repo.get("commit") == commit and repo.get("url") == "https://github.com/IzuSharp/NativeWeave", "Package source differs"
        digest(value.get("sha256"))


def rows(value):
    assert set(value.get("rows", {})) == ROWS, "Missing database/runtime cell"
    assert all(row.get("passed") is True for row in value["rows"].values()), "Actual database/runtime cell failed"


def validate_result(kind, value, receipt, acceptance):
    expected = acceptance["candidate_sources"].get("NativeWeave")
    if kind in {"log", "github-run", "github-jobs", "github-pr"}:
        return
    if kind == "review":
        terminal(value)
        assert value.get("sources") == receipt["sources"], "Review binds different source identities"
        assert isinstance(value.get("reviewer"), str) and value["reviewer"]
        assert isinstance(value.get("authorship_disclosure"), str) and value["authorship_disclosure"]
        assert value.get("blocking_findings") == [], "Review contains unresolved blockers"
        return
    assert expected is not None, "Product candidate has no source identity"
    identity(expected)
    if kind != "migration-comparison":
        product_source(value, expected)
    if kind == "native-build":
        assert value.get("task") == "DB-CPP-01" and value.get("rid") == "linux-x64"
        assert value.get("sourceTree") == expected["tree"] and value.get("sourceDirty") is False
        assert value.get("language") == "C++20" and value.get("preset") == "linux-x64-release"
        assert value.get("target") == "x86_64-unknown-linux-gnu"
        assert {"clang", "clang++", "clang-format", "clang-tidy"} <= set(value.get("tools", {}))
        assert {a["engineId"] for a in value.get("assets", [])} == {"database.sqlite", "database.postgresql"}
        commands(value)
    elif kind == "package-manifest":
        assert value.get("nativeSourceCommit") == expected["commit"] and value.get("sourceDirty") is False
        assert value.get("rid") == "linux-x64" and value.get("candidate", {}).get("packages")
        digest(value.get("nativeInputManifestSha256"))
    elif kind == "component-result":
        terminal(value)
        assert value.get("sourceDirty") is False and value.get("sourceStable") is True
        commands(value)
    elif kind == "compatibility-result":
        terminal(value)
        assert value.get("prepare_only") is False and value.get("source_dirty") is False and value.get("source_stable") is True
        assert value.get("matrix_rows") == 20 and value.get("policy_cases") == 30
        assert type(value.get("commands")) is int and value["commands"] >= 85
    elif kind == "regression-result":
        terminal(value)
        commands(value)
        assert value.get("platform") == "linux-x64"
        assert set(value.get("providers", [])) == {"sqlite", "postgresql"} and set(value.get("modes", [])) == {"jit", "aot"}
        required = {"native.interop", "native.contracts", "native.query", "native.scalar", "native.execution", "native.administration", "native.provider"}
        assert required <= set(value.get("nativeTests", [])), "Retained native regression inventory missing"
        names = {row.get("name") for row in value["commands"]}
        assert {"data.transactions", "data.streaming", "data.codecs", "data.postgres", "data.sqlite", "query.binding", "query.native"} <= names
        assert {name + "-" + mode for name in ("Data.NativeHost", "Data.Migrations", "Data.Materialization", "Query.Fluent", "Orm.Relations") for mode in ("jit", "aot")} <= names
    elif kind == "verification-result":
        terminal(value)
        assert value.get("rid") == "linux-x64"
        assert {"clang-format", "clang-tidy", "cpp-contract-tests", "managed-workspace-build", "dotnet-format", "compiled-api-and-xml", "postgresql-and-sqlite-regressions", "nuget-closure", "external-fluent-dto-jit-and-aot"} <= set(value.get("checks", []))
        digest(value.get("nativeManifestSha256"))
        digest(value.get("candidateManifestSha256"))
    elif kind == "migration-run":
        terminal(value)
        commands(value)
        rows(value)
        assert value.get("phase") in {"candidate", "baseline"}
        assert set(value.get("required_rows", [])) == ROWS and value.get("rust_or_cpp_build_tools_invoked") is False
        commit = expected["commit"] if value["phase"] == "candidate" else BASELINES["NativeWeave"]["commit"]
        packages(value.get("packages"), commit)
        assert value.get("abi", {}).get("passed") is True
        assert value["abi"].get("differences") == [] and value["abi"].get("retired_counts") == [0] * 6
        assert isinstance(value["abi"].get("cases"), dict) and len(value["abi"]["cases"]) == 24
        assert set(value.get("source_sha256", {})) == CONSUMER_FILES
        for field in SHARED_COMPARISON_INPUTS:
            assert value.get(field), "Missing comparison environment/input: " + field
        expected_builds = {"jit", "aot"} | ({"jit-dto-v2", "aot-dto-v2"} if value["phase"] == "candidate" else set())
        assert set(value.get("builds", {})) == expected_builds, "Missing executed business build"
        native = value.get("native_sha256", {})
        assert set(native) == {"libnw_database_sqlite.so", "libnw_database_postgresql.so"}
        for native_hash in native.values():
            digest(native_hash)
        for build_name, build in value["builds"].items():
            assert build.get("native_sha256") == native, "Business/DTO build changed native asset bytes"
            expected_sources = dict(value["source_sha256"])
            if build_name.endswith("-dto-v2"):
                assert expected_sources["DtoMapping.cs"] != value["dto_variant_sha256"]
                expected_sources["DtoMapping.cs"] = value["dto_variant_sha256"]
            assert build.get("source_sha256") == expected_sources, "Business build source differs from declared consumer/DTO change"
    elif kind == "migration-comparison":
        terminal(value)
        rows(value)
        assert value.get("rust_commit") == BASELINES["NativeWeave"]["commit"]
        packages(value.get("cpp_packages"), expected["commit"])
        digest(value.get("candidate_result_sha256"))
        digest(value.get("baseline_result_sha256"))
        assert all(row.get("dto_change", {}).get("native_sha256_unchanged") is True for row in value["rows"].values())
        required_comparisons = {"fresh-seed", "old-database-read", "old-database-continue", "changed-dto-same-native"}
        assert all(set(row.get("comparisons", [])) == required_comparisons for row in value["rows"].values())
    elif kind == "command-result":
        terminal(value)
        commands(value)
    else:
        raise AssertionError("Unsupported result kind: " + kind)


def validate_links(items):
    """Bind summaries to the actual exported byte identities they summarize."""
    manifests = {item["original_sha256"] for item in items if item["kind"] == "native-build"}
    for item in items:
        value = item["data"]
        if item["kind"] == "package-manifest":
            assert value["nativeInputManifestSha256"] in manifests, "Package manifest lacks its exact native producer result"
        if item["kind"] == "migration-comparison":
            actual = {}
            for other in items:
                if other["kind"] == "migration-run":
                    phase = other["data"]["phase"]
                    assert phase not in actual, "Duplicate migration result phase"
                    actual[phase] = other
            assert set(actual) == {"baseline", "candidate"}, "Comparison lacks both actual process results"
            for phase in actual:
                assert value[phase + "_result_sha256"] == actual[phase]["original_sha256"], "Comparison refers to different actual result bytes"
                assert value.get("same_consumer_source_sha256") == actual[phase]["data"].get("source_sha256"), "Business consumer source differs"
            assert value["cpp_packages"] == actual["candidate"]["data"]["packages"], "Compared packages differ from executed packages"
            assert value["rows"] == actual["candidate"]["data"]["rows"], "Compared matrix differs from executed matrix"
            abi = value.get("abi_compatibility", {})
            for phase in actual:
                assert abi.get(phase) == actual[phase]["data"].get("abi"), "ABI comparison differs from actual process result"
                assert abi.get("inputs_sha256") == actual[phase]["data"].get("abi_inputs_sha256"), "ABI probe inputs differ"
            old, new = actual["baseline"]["data"], actual["candidate"]["data"]
            for field in SHARED_COMPARISON_INPUTS:
                assert old[field] == new[field], "Old/new comparison uses different environment/input: " + field
            assert old["abi"]["cases"] == new["abi"]["cases"], "Actual ABI outcomes differ"
            for row in ROWS:
                seed = old["rows"][row].get("snapshots", {}).get("seed")
                assert isinstance(seed, dict) and seed == new["rows"][row].get("snapshots", {}).get("old_seed"), "Candidate did not receive the exact old database snapshot"
                digest(seed.get("sha256"))


def validate_ci_row(row, sources, artifacts, prs):
    repo = row.get("repository")
    assert repo in REPOSITORIES and repo in sources, "CI source repository missing"
    scope = row.get("scope")
    assert scope in {"pr_head", "merged_main"}
    path = row.get("workflow_path")
    assert path in WORKFLOWS[repo], "Unexpected workflow cannot replace required CI"
    expected = sources[repo]
    for key, kind in (("run", "github-run"), ("jobs", "github-jobs")):
        reference = row.get(key)
        assert isinstance(reference, dict) and set(reference) == {"path", "sha256"}
        item = artifacts.get(reference["path"])
        assert item and item["kind"] == kind and item["sha256"] == reference["sha256"], "CI lacks hashed raw run/jobs observations"
    run, jobs = artifacts[row["run"]["path"]]["data"], artifacts[row["jobs"]["path"]]["data"]
    run_id = run.get("id")
    assert type(run_id) is int and run_id > 0
    url = "https://github.com/IzuSharp/" + repo + "/actions/runs/" + str(run_id)
    api = "https://api.github.com/repos/IzuSharp/" + repo + "/actions/runs/" + str(run_id)
    assert row.get("url") == run.get("html_url") == url and run.get("url") == api and run.get("jobs_url") == api + "/jobs"
    assert run.get("repository", {}).get("full_name") == "IzuSharp/" + repo and run.get("path") == path
    assert run.get("head_sha") == expected["commit"]
    head = run.get("head_commit", {})
    assert head.get("id") == expected["commit"] and head.get("tree_id") == expected["tree"], "CI actual commit/tree differs"
    branch = "main" if scope == "merged_main" else "task/DB-CPP-01-linux"
    event = "push" if scope == "merged_main" else "pull_request"
    assert run.get("head_branch") == branch and run.get("event") == event, "Wrong CI branch/event"
    if scope == "pr_head":
        # GitHub may return an empty pull_requests collection after a PR merges.
        # The hashed PR observation separately binds this exact head to main.
        pulls = run.get("pull_requests")
        assert isinstance(pulls, list)
        if pulls:
            number = int(prs[repo]["url"].rsplit("/", 1)[1])
            selected = [pull for pull in pulls if pull.get("number") == number]
            assert len(selected) == 1 and selected[0].get("head", {}).get("sha") == expected["commit"]
            assert selected[0].get("base", {}).get("ref") == "main", "CI belongs to another pull request/base"
    assert run.get("status") == "completed" and run.get("conclusion") == "success", "CI is unfinished or failed"
    attempt = run.get("run_attempt")
    assert type(attempt) is int and attempt > 0
    observed = jobs.get("jobs")
    assert isinstance(observed, list) and observed and type(jobs.get("total_count")) is int and jobs["total_count"] == len(observed), "CI jobs response is incomplete"
    names = [job.get("name") for job in observed]
    expected_jobs = WORKFLOWS[repo][path]
    assert len(set(names)) == len(names) and set(names) == expected_jobs, "Required job inventory differs"
    skipped = {"security / Dependency review"} if repo == "NativeWeave" and scope == "merged_main" else set()
    assert set(row.get("required_jobs", expected_jobs - skipped)) == expected_jobs - skipped
    assert set(row.get("normally_skipped_jobs", skipped)) == skipped
    ids = set()
    for job in observed:
        job_id = job.get("id")
        assert type(job_id) is int and job_id > 0 and job_id not in ids
        ids.add(job_id)
        assert job.get("run_id") == run_id and job.get("run_attempt") == attempt
        assert job.get("head_sha") == expected["commit"] and job.get("head_branch") == branch and job.get("run_url") == api
        assert job.get("url") == "https://api.github.com/repos/IzuSharp/" + repo + "/actions/jobs/" + str(job_id)
        assert job.get("html_url") == url + "/job/" + str(job_id)
        assert job.get("status") == "completed"
        assert job.get("conclusion") == ("skipped" if job["name"] in skipped else "success"), "Required job failed or was skipped"
        required_steps = STEPS.get(job["name"], set())
        actual_steps = job.get("steps", [])
        assert isinstance(actual_steps, list)
        for name in required_steps:
            found = [step for step in actual_steps if step.get("name") == name]
            assert len(found) == 1 and found[0].get("status") == "completed" and found[0].get("conclusion") == "success", "Mandatory CI step missing, failed or skipped: " + name
    return repo, scope, path
