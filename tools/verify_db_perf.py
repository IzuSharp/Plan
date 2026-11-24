#!/usr/bin/env python3
"""Verify DB-Perf-01 records without treating document checks as execution."""

from __future__ import annotations

import argparse
import copy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "ledger/evidence/batches/DB-Perf-01/"
FROZEN = "bc1956936ee77a997a016856c97def6aabc0bbc6"
PRODUCT = "771bc77cbd68d3f932b99ed2497c0697bbba5f02"
PRODUCT_TREE = "ddc4ec36cdade1749127fe5d50cbbf218b2878e6"
BASELINES = {"Korda": PRODUCT, "Plan": FROZEN}
DATABASES = ("postgresql", "sqlite")
COLUMNS = ("direct_cpp", "korda_before", "korda_after", "independent_csharp_orm")
CELLS = [f"{database}/{column}" for database in DATABASES for column in COLUMNS]
CHECKS = {
    "comparable_baselines", "independent_orm_aot", "business_correctness",
    "public_allocation_coverage", "allocation_resource_bounds", "noise_and_fixed_load",
    "capacity_and_recovery", "eight_long_segments", "cpu_memory_latency_throughput",
    "optimization_stop_basis", "package_aot_and_dto_reuse", "api_and_selected_ci",
    "independent_review", "normal_merges_and_main", "public_preview_verification",
    "final_report_reproduction",
}
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def integer(value, name, minimum=0):
    require(type(value) is int and value >= minimum, f"Invalid integer {name}")


def source(value, name):
    require(isinstance(value, str) and HEX40.fullmatch(value) is not None
            and value != "0" * 40, f"Invalid source identity {name}")


def sha(value, name):
    require(isinstance(value, str) and HEX64.fullmatch(value) is not None
            and value != "0" * 64, f"Invalid SHA-256 {name}")


def reference(item):
    require(isinstance(item, dict) and set(item) == {"path", "sha256"}, "Invalid file reference")
    require(isinstance(item["path"], str) and not Path(item["path"]).is_absolute(), "Absolute evidence path")
    path = (ROOT / item["path"]).resolve()
    require(path.is_relative_to(ROOT) and path.is_file(), f"Missing/outside evidence: {item['path']}")
    sha(item["sha256"], item["path"])
    require(digest(path) == item["sha256"], f"Evidence digest changed: {item['path']}")
    return path


def references(items, required=False):
    require(isinstance(items, list), "Evidence must be a list")
    if required:
        require(bool(items), "Observed evidence is required")
    return [reference(item) for item in items]


def validate_current(current, state):
    require(current["task"] == "DB-Perf-01" and current["branch"] == "task/DB-Perf-01-linux", "Wrong current task")
    require(current["platforms"] == ["linux-x64"] and current["source_main"] == BASELINES, "Wrong scope/baseline")
    require(current["status"] == state, "Graph/acceptance states differ")
    require(current["merge_authorized"] is True and current["publication_authorized"] is True, "Current authority lost")
    for field, filename in (("plan", "plan.md"), ("handoff", "handoff-linux.md"), ("acceptance", "acceptance.json")):
        require(current[field] == PREFIX + filename, f"Wrong {field} entry")


def validate_claim(name, check, final):
    require(check["status"] in {"pending", "blocked", "passed"}, f"Invalid claim state: {name}")
    require(isinstance(check["requirement"], str) and bool(check["requirement"]), f"Missing requirement: {name}")
    paths = references(check["evidence"], required=check["status"] == "passed")
    if check["status"] != "passed":
        return
    for path in paths:
        receipt = read_json(path)
        require(receipt.get("task") == "DB-Perf-01" and receipt.get("claim") == name
                and receipt.get("kind") == "observed_claim" and receipt.get("status") == "passed",
                f"Wrong/unobserved claim receipt: {name}")
        source(receipt.get("source_commit"), name)
        require(receipt["source_commit"] in {PRODUCT, (final or {}).get("commit")}, f"Unbound claim source: {name}")
        references(receipt.get("raw_files"), required=True)
        require(isinstance(receipt.get("reproduction_commands"), list)
                and bool(receipt["reproduction_commands"]), f"Missing reproduction commands: {name}")
        require(receipt.get("internal_diagnostic_only") is False, f"Internal diagnostic cannot accept {name}")
        if name == "business_correctness":
            cases = receipt.get("business_cases", [])
            for provider in DATABASES:
                actual = [case for case in cases if case.get("provider") == provider and case.get("passed") is True]
                require(len({case["semantic_case_id"] for case in actual}) >= 24,
                        "Fewer than 24 executed semantic business cases for a database")
                for case in actual:
                    references(case.get("raw_files"), required=True)
        if name == "comparable_baselines":
            executions = receipt.get("executed_cells", [])
            require(len(executions) == 8 and {item["cell"] for item in executions} == set(CELLS),
                    "All four routes on both databases must actually execute")
            for item in executions:
                require(item.get("real_database") is True, "Synthetic driver cannot fill a comparison cell")
                integer(item.get("completed_operations"), "comparison completed operations", 1)
                sha(item.get("executable_sha256"), "comparison executable")
                references(item.get("raw_files"), required=True)


def validate_allocation(allocation, final=None):
    require(allocation["status"] in {"unproven", "mixed", "zero", "unmet"}, "Invalid allocation status")
    require(type(allocation["framework_wide_zero_bytes"]) is bool and type(allocation["coverage_complete"]) is bool,
            "Allocation flags must be boolean")
    inventory = allocation["public_api_inventory"]
    if inventory is not None:
        reference(inventory)
    paths = allocation["paths"]
    require(isinstance(paths, list) and isinstance(allocation["residual_paths"], list), "Invalid path inventory")
    identities = set()
    measured_sources = set()
    for path in paths:
        key = (path["provider"], path["id"], path["mode"], path["scope"])
        require(key not in identities and path["provider"] in DATABASES, "Repeated/invalid allocation path")
        identities.add(key)
        require(path["mode"] in {"sync", "suspended_async", "concurrent"}
                and path["scope"] in {"operation", "batch", "row"}, "Invalid allocation mode/boundary")
        require(path["status"] in {"unproven", "unmet", "zero"}, "Invalid path status")
        if path["status"] == "unproven":
            continue
        receipt = read_json(reference(path["measurement"]))
        require(receipt.get("kind") == "normal_public_api_allocation" and receipt.get("process_wide") is True,
                "A public, process-wide allocation measurement is required")
        require(receipt.get("provider") == path["provider"] and receipt.get("path_id") == path["id"], "Wrong allocation scope")
        source(receipt.get("source_commit"), "allocation producer")
        measured_sources.add(receipt["source_commit"])
        for field in ("package_sha256", "executable_sha256", "native_sha256"):
            sha(receipt.get(field), f"allocation {field}")
        require(bool(receipt.get("package_version")) and bool(receipt.get("boundary")), "Missing measured version/boundary")
        for field in ("operations", "batches", "rows", "raw_allocated_bytes", "business_allocated_bytes",
                      "framework_allocated_bytes", "other_attributed_bytes", "unattributed_bytes", "suspended_operations"):
            integer(receipt.get(field), field)
        require(receipt["operations"] > 0, "Empty allocation measurement")
        require(receipt["raw_allocated_bytes"] == sum(receipt[field] for field in
                ("business_allocated_bytes", "framework_allocated_bytes", "other_attributed_bytes", "unattributed_bytes")),
                "Allocation attribution totals do not reconcile")
        references(receipt.get("raw_files"), required=True)
        require(bool(receipt.get("attribution_method")), "Missing allocation attribution")
        if path["mode"] == "suspended_async":
            require(receipt["suspended_operations"] > 0, "No actual asynchronous suspension")
        if path["status"] == "zero":
            require(receipt["framework_allocated_bytes"] == 0 and receipt["unattributed_bytes"] == 0,
                    "Nonzero or unresolved bytes cannot establish zero")
        if path["status"] == "unmet":
            require(receipt["framework_allocated_bytes"] > 0, "An unmet allocation path needs observed framework bytes")
    if allocation["framework_wide_zero_bytes"]:
        require(final is not None and measured_sources == {final["commit"]},
                "Intermediate or mixed producer measurements cannot establish final framework-wide zero")
        require(allocation["status"] == "zero" and allocation["coverage_complete"]
                and inventory is not None and bool(paths) and not allocation["residual_paths"], "Incomplete global zero claim")
        require(all(path["status"] == "zero" for path in paths), "Nonzero/unproven path in global zero claim")
        require({path["provider"] for path in paths} == set(DATABASES), "Missing provider in global zero claim")
        require({path["scope"] for path in paths} >= {"operation", "batch", "row"}, "Per-row zero is not global zero")
    else:
        require(allocation["status"] != "zero", "Global allocation status cannot be zero without a substantiated claim")


def validate_long_tests(long_tests, environment, final):
    require(long_tests["required_cells"] == CELLS and long_tests["minimum_seconds_per_cell"] == 1800
            and long_tests["minimum_total_seconds"] == 14400, "Long-test requirements were weakened")
    segments = long_tests["segments"]
    require(isinstance(segments, list), "Invalid long-test segments")
    integer(long_tests["accepted_count"], "accepted_count")
    integer(long_tests["effective_seconds"], "effective_seconds")
    require(long_tests["accepted_count"] == len(segments), "Long-test count has no corresponding segment")
    require(long_tests["effective_seconds"] == sum(segment["effective_seconds"] for segment in segments), "Duration has no corresponding segment")
    cells, workloads, intervals = set(), set(), []
    for segment in segments:
        require(environment["status"] == "qualified", "Unqualified environment cannot earn long-test credit")
        cell = segment["cell"]
        require(cell in CELLS and cell not in cells, "Repeated or unknown long-test cell")
        cells.add(cell)
        integer(segment["effective_seconds"], "effective_seconds", 1800)
        require(segment["environment_id"] == environment["identity"], "Long-test environment differs")
        start, end = (datetime.fromisoformat(segment[name].replace("Z", "+00:00"))
                      for name in ("effective_start_utc", "effective_end_utc"))
        require(start.tzinfo is not None and end.tzinfo is not None and (end - start).total_seconds() >= segment["effective_seconds"],
                "Effective duration exceeds actual interval")
        intervals.append((start, end))
        for field in ("workload_sha256", "application_sha256", "native_sha256"):
            sha(segment[field], field)
        workloads.add(segment["workload_sha256"])
        source(segment["source_commit"], "long segment")
        if cell.endswith("/korda_before"):
            require(segment["source_commit"] == PRODUCT, "Before segment is not fixed-main source")
        if cell.endswith("/korda_after"):
            require(final is not None and segment["source_commit"] == final["commit"], "After segment is not final-candidate source")
        require(segment["correctness_passed"] is True, "Long run lacks result/state verification")
        references(segment["raw_files"], required=True)
        counts = segment["operation_counts"]
        for field in ("planned", "issued", "completed", "succeeded", "failed", "rejected", "retries"):
            integer(counts.get(field), field)
        require(counts["succeeded"] > 0 and counts["succeeded"] + counts["failed"] == counts["completed"]
                and counts["completed"] <= counts["issued"], "Invalid operation ledger")
        metrics = segment["metrics"]
        required_metrics = {"ops_per_second", "rows_per_second", "p50", "p95", "p99", "client_cpu_user_seconds",
                            "client_cpu_system_seconds", "cpu_seconds_per_success", "idle_cpu_seconds",
                            "steady_rss_bytes", "peak_rss_bytes", "retained_rss_bytes", "pss", "native_heap_peak",
                            "managed_allocation", "ownership_after_drain"}
        require(required_metrics <= metrics.keys(), "Long run lacks CPU/memory/latency/allocation/drain metrics")
        if cell.startswith("postgresql/"):
            require("database_service" in metrics, "PostgreSQL service accounting is missing")
        if cell.endswith("/direct_cpp"):
            require(metrics["managed_allocation"] == "not_applicable" and "native_allocations_and_frees" in metrics,
                    "Direct C++ accounting is not applicable to managed bytes")
    for previous, following in zip(sorted(intervals), sorted(intervals)[1:]):
        require(previous[1] <= following[0], "Long segments overlap on exclusive measurement resources")
    require(len(workloads) <= 1, "The eight comparison cells do not share a frozen workload manifest")


def validate_acceptance(record):
    schema = read_json(ROOT / "schemas/db-perf-v1.schema.json")
    require(set(record) == set(schema["required"]), "Acceptance record fields differ from its schema")
    require(record["schema_version"] == 1 and record["task"] == "DB-Perf-01"
            and record["platform"] == "linux-x64" and record["baseline"] == BASELINES, "Wrong record identity")
    require(record["state"] in {"in_progress", "blocked", "accepted"}, "Invalid acceptance state")
    require(record["self_ci"] == "checked_separately", "Future self-CI cannot be asserted")
    final = record["final_candidate"]
    if final is not None:
        source(final["commit"], "candidate commit")
        source(final["tree"], "candidate tree")
    environment = record["environment"]
    require(environment["status"] in {"unqualified", "qualified"}, "Invalid environment state")
    references(environment["evidence"], required=environment["status"] == "qualified")
    if environment["status"] == "qualified":
        require(isinstance(environment["identity"], str) and bool(environment["identity"]), "Missing admitted environment identity")
        for path in references(environment["evidence"]):
            receipt = read_json(path)
            require(receipt.get("kind") == "dedicated_environment_admission"
                    and receipt.get("environment_id") == environment["identity"]
                    and receipt.get("exclusive_resources") is True
                    and receipt.get("stable_quotas_verified") is True
                    and receipt.get("client_server_accounting_verified") is True
                    and receipt.get("before_noise_verified") is True, "Unsupported dedicated-environment qualification")
            references(receipt.get("raw_files"), required=True)
    else:
        require(environment["identity"] is None, "Unqualified environment cannot have an admitted identity")
    require(set(record["checks"]) == CHECKS, "Required acceptance claims changed")
    for name, check in record["checks"].items():
        validate_claim(name, check, final)
    validate_allocation(record["allocation"], final)
    validate_long_tests(record["long_tests"], environment, final)
    if record["checks"]["eight_long_segments"]["status"] == "passed":
        require(record["long_tests"]["accepted_count"] == 8 and record["long_tests"]["effective_seconds"] >= 14400,
                "The long-test claim cannot pass before all eight segments")
    if record["checks"]["public_allocation_coverage"]["status"] == "passed":
        require(record["allocation"]["coverage_complete"] and record["allocation"]["public_api_inventory"] is not None,
                "Public allocation coverage is still incomplete")
    publication = record["publication"]
    require(publication["status"] in {"pending", "verified", "unchanged_inputs_skip"}, "Invalid publication state")
    references(publication["evidence"], required=publication["status"] != "pending")
    if publication["status"] == "unchanged_inputs_skip":
        require(publication["package_inputs_changed"] is False, "Changed inputs cannot skip publication")
    if publication["status"] == "verified":
        require({package["provider"] for package in publication["packages"]} == set(DATABASES), "Missing verified public provider")
    if record["state"] == "accepted":
        require(final is not None and all(check["status"] == "passed" for check in record["checks"].values()), "Incomplete accepted batch")
        require(environment["status"] == "qualified" and record["long_tests"]["accepted_count"] == 8
                and record["long_tests"]["effective_seconds"] >= 14400, "Incomplete long campaign")
        require(record["allocation"]["coverage_complete"] and record["allocation"]["public_api_inventory"] is not None,
                "Unmeasured public-path allocation inventory")
        require(publication["status"] != "pending", "Publication verification is unfinished")


def validate_baseline(baseline, archives=None):
    require(baseline["task"] == "DB-Perf-01" and baseline["source_main"] == BASELINES
            and baseline["source_trees"]["Korda"] == PRODUCT_TREE, "Wrong immutable baseline")
    require(baseline["comparison_columns"] == list(COLUMNS) and baseline["databases"] == list(DATABASES), "Comparison column/database dropped")
    require(baseline["historical_results_reused"] is False, "Old performance results were rebound")
    reference(baseline["environment"]["observation"])
    reference(baseline["archive_review"])
    for diagnostic in baseline.get("diagnostics", []):
        reference({key: diagnostic[key] for key in ("path", "sha256")})
        require(diagnostic["public_provider_acceptance"] is False and diagnostic["long_test_credit"] == 0,
                "Diagnostic evidence cannot be promoted to provider/campaign acceptance")
    require(set(baseline["packages_before"]) == set(DATABASES), "Missing original provider candidate")
    for provider, package in baseline["packages_before"].items():
        require(package["source_commit"] == PRODUCT and package["source_tree"] == PRODUCT_TREE, "Wrong original package source")
        manifest = read_json(reference(package["release_manifest"]))
        require(manifest["source_commit"] == PRODUCT and manifest["source_tree"] == PRODUCT_TREE
                and manifest["source_dirty"] is False, "Original producer is not the fixed clean source")
        require(len(manifest["packages"]) == 1, "Provider archive must remain independently installable")
        entry = manifest["packages"][0]
        require(entry["id"] == package["id"] and entry["version"] == package["version"]
                and entry["source_commit"] == PRODUCT and entry["native"]["source_commit"] == PRODUCT
                and entry["native"]["sha256"] == package["native_sha256"], "Original package metadata differs")
        for field in ("nupkg_sha256", "native_sha256", "artifact_zip_sha256"):
            sha(package[field], field)
        if archives is not None:
            path = archives / provider / "feed" / package["filename"]
            require(digest(archives / f"{provider}.zip") == package["artifact_zip_sha256"], "Artifact ZIP differs")
            require(digest(path) == package["nupkg_sha256"], "Original candidate nupkg differs")
            with zipfile.ZipFile(path) as archive:
                members = [name for name in archive.namelist() if not name.endswith("/")]
                require(len(members) == len(set(members)) and set(members) == set(entry["unsigned_entries"]), "Archive member set differs")
                for name, expected in entry["unsigned_entries"].items():
                    require(hashlib.sha256(archive.read(name)).hexdigest() == expected, f"Archive member differs: {name}")


def validate_history(graph):
    old = json.loads(subprocess.check_output(["git", "show", FROZEN + ":delivery-graph.json"], cwd=ROOT))
    for key, value in old.items():
        if key != "current_execution":
            require(graph[key] == value, f"Historical graph changed: {key}")
    require(graph["prior_execution_snapshots"] == {"DB-Rename-01": {"frozen_plan": FROZEN, "entry": old["current_execution"]}},
            "Historical current-execution snapshot was relabeled")
    allowed = {"AGENTS.md", "delivery-graph.json", ".gitattributes", ".github/workflows/native-slices-final-check.yml",
               "tools/verify_db_perf.py", "schemas/db-perf-v1.schema.json"}
    changed = subprocess.check_output(["git", "diff", "--name-only", FROZEN], cwd=ROOT, text=True).splitlines()
    require(all(path in allowed or path.startswith(PREFIX) for path in changed), "Unrelated/historical input changed")
    old_attributes = subprocess.check_output(["git", "show", FROZEN + ":.gitattributes"], cwd=ROOT)
    attributes = (ROOT / ".gitattributes").read_bytes()
    require(attributes.startswith(old_attributes), "Historical attributes changed")
    for line in attributes[len(old_attributes):].decode().splitlines():
        require(not line or line.startswith("#") or line.startswith(PREFIX + "preflight/"),
                "Unrelated attributes exemption")
    historical_verifiers = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", FROZEN, "tools"], cwd=ROOT, text=True).splitlines()
    for name in historical_verifiers:
        original = subprocess.check_output(["git", "show", f"{FROZEN}:{name}"], cwd=ROOT)
        require((ROOT / name).read_bytes() == original, f"Historical tool bytes changed: {name}")


def validate_diagnostic_indexes():
    for path in (ROOT / PREFIX / "checkpoints").glob("*/files.json"):
        index = read_json(path)
        for item in index["files"]:
            reference({key: item[key] for key in ("path", "sha256")})
            require((ROOT / item["path"]).stat().st_size == item["bytes"], "Raw diagnostic length changed")
    reconciliation = ROOT / PREFIX / "reconciled-remote/ba380202/retained-files.json"
    if reconciliation.is_file():
        index = read_json(reconciliation)
        require(index["origin_commit"] == "ba380202e7b36cbfe8dcd4bc2cfa0afe86048d92", "Wrong concurrent evidence origin")
        for item in index["files"]:
            path = reference({key: item[key] for key in ("path", "sha256")})
            require(path.stat().st_size == item["bytes"], "Retained concurrent evidence length changed")
            raw = subprocess.check_output(["git", "show", index["origin_commit"] + ":" + item["original_path"]], cwd=ROOT)
            require(hashlib.sha256(raw).hexdigest() == item["sha256"], "Concurrent evidence was relabeled")


def validate_source_reference(value, original, korda_source=None):
    require(value.get("schema_version") == 1 and value.get("task") == "DB-Perf-01"
            and value.get("kind") == "source_reference", "Invalid source-reference record")
    require(value.get("original_plan_path") == original["plan_path"]
            and value.get("original_git_blob") == original["blob"]
            and value.get("sha256") == original["sha256"] and value.get("bytes") == original["bytes"],
            "Historical source identity changed during relocation")
    source(value["original_git_blob"], "original source blob")
    sha(value["sha256"], "historical source")
    integer(value["bytes"], "historical source length", 1)
    target = value.get("source", {})
    require(target.get("repository") == "IzuSharp/Korda" and target.get("sha256") == value["sha256"]
            and target.get("bytes") == value["bytes"], "Source reference moved outside Korda or changed bytes")
    path = target.get("path")
    require(isinstance(path, str) and not Path(path).is_absolute() and ".." not in Path(path).parts,
            "Invalid Korda source path")
    require(target.get("status") in {"fixed_commit", "pending_harness_commit"}, "Unknown source-binding state")
    if target["status"] == "pending_harness_commit":
        require(target.get("commit") is None and target.get("tree") is None,
                "Pending source binding cannot invent a source commit")
        require(path.startswith("benchmarks/db-perf/reproduction-inputs/by-sha256/" + value["sha256"] + "/"),
                "Pending historical source must use immutable content-addressed Korda storage")
        return False
    source(target.get("commit"), "fixed Korda source commit")
    source(target.get("tree"), "fixed Korda source tree")
    require(target.get("url") == f"https://github.com/IzuSharp/Korda/blob/{target['commit']}/{path}",
            "Korda source link is not commit-pinned")
    if korda_source is not None:
        tree = subprocess.check_output(["git", "rev-parse", target["commit"] + "^{tree}"], cwd=korda_source, text=True).strip()
        require(tree == target["tree"], "Referenced Korda commit tree changed")
        raw = subprocess.check_output(["git", "show", target["commit"] + ":" + path], cwd=korda_source)
        require(len(raw) == target["bytes"] and hashlib.sha256(raw).hexdigest() == target["sha256"],
                "Referenced fixed Korda source bytes differ")
    return True


def validate_source_scope(state, korda_source=None):
    path = ROOT / PREFIX / "source-scope-correction/source-references.json"
    index = read_json(path)
    require(index["kind"] == "source_scope_correction" and index["task"] == "DB-Perf-01"
            and index["remote_existing_files_removed"] is False and index["original_measurement_bytes_changed"] is False,
            "Source relocation must preserve remote records and raw measurement bytes")
    original_remote = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", index["remote_evidence_commit"]], cwd=ROOT, text=True).splitlines()
    original_paths, unique_hashes, pending = set(), set(), 0
    for item in index["references"]:
        record_path = reference({key: item[key] for key in ("path", "sha256")})
        require(record_path.stat().st_size == item["bytes"], "Source reference length changed")
        original = item["original_source"]
        require(original["plan_path"] not in original_paths and original["plan_path"] not in original_remote,
                "Relocation duplicated a source or removed pre-existing remote evidence")
        require(not (ROOT / original["plan_path"]).exists(), "A new implementation copy remains in Plan")
        original_paths.add(original["plan_path"])
        unique_hashes.add(original["sha256"])
        pending += not validate_source_reference(read_json(record_path), original, korda_source)
    require(len(original_paths) == index["source_reference_count"] == 93
            and len(unique_hashes) == index["unique_source_hashes"] == 52
            and pending == index["pending_reference_count"], "Source relocation inventory does not reconcile")
    require(index["status"] == ("pending_korda_bindings" if pending else "fixed_korda_bindings"), "Source-binding summary is stale")
    for item in index["original_indexes"]:
        record_path = reference({key: item[key] for key in ("path", "sha256")})
        require(record_path.stat().st_size == item["bytes"], "Original diagnostic index bytes changed")
    require(state != "accepted" or (pending == 0 and korda_source is not None),
            "Batch acceptance requires all relocated source bytes verified at fixed Korda commits")
    return {"references": len(original_paths), "pending": pending, "fixed_bytes_verified": korda_source is not None}


def negative_controls(record):
    record = copy.deepcopy(record)
    record["state"] = "in_progress"
    record["final_candidate"] = None
    record["environment"].update(status="unqualified", identity=None, evidence=[])
    for check in record["checks"].values():
        check.update(status="pending", evidence=[])
    record["allocation"].update(framework_wide_zero_bytes=False, coverage_complete=False,
                                public_api_inventory=None, paths=[], residual_paths=[], status="unproven")
    record["long_tests"].update(segments=[], accepted_count=0, effective_seconds=0)
    record["publication"].update(status="pending", package_inputs_changed=None, packages=[], evidence=[])
    validate_acceptance(record)
    cases = []
    def add(name, edit):
        mutated = copy.deepcopy(record)
        edit(mutated)
        cases.append((name, mutated))
    add("wrong baseline", lambda value: value["baseline"].update(Korda="0" * 40))
    add("accepted without execution", lambda value: value.update(state="accepted"))
    add("passed claim without receipt", lambda value: value["checks"]["comparable_baselines"].update(status="passed", evidence=[]))
    add("missing comparison obligation", lambda value: value["checks"].pop("independent_orm_aot"))
    add("unobserved environment", lambda value: value["environment"].update(status="qualified", identity="invented", evidence=[]))
    add("invented long count", lambda value: value["long_tests"].update(accepted_count=8))
    add("invented duration", lambda value: value["long_tests"].update(effective_seconds=14400))
    add("shortened interval", lambda value: value["long_tests"].update(minimum_seconds_per_cell=1799))
    add("missing long column", lambda value: value["long_tests"]["required_cells"].pop())
    add("global zero from no paths", lambda value: value["allocation"].update(framework_wide_zero_bytes=True, status="zero"))
    add("global zero label alone", lambda value: value["allocation"].update(status="zero"))
    add("publish without receipt", lambda value: value["publication"].update(status="verified", evidence=[]))
    add("self-CI prediction", lambda value: value.update(self_ci="already_passed"))
    for name, mutated in cases:
        try:
            validate_acceptance(mutated)
        except (ValueError, KeyError, TypeError):
            continue
        raise ValueError(f"Negative control accepted: {name}")
    return len(cases)


def source_negative_controls():
    index = read_json(ROOT / PREFIX / "source-scope-correction/source-references.json")
    item = index["references"][0]
    original = item["original_source"]
    baseline = read_json(ROOT / item["path"])
    cases = []
    for field, value in (("repository", "IzuSharp/Plan"), ("path", "../outside.cs"), ("sha256", "0" * 64)):
        changed = copy.deepcopy(baseline)
        changed["source"][field] = value
        cases.append(changed)
    changed = copy.deepcopy(baseline)
    changed["source"].update(status="pending_harness_commit", commit="a" * 40)
    cases.append(changed)
    for changed in cases:
        try:
            validate_source_reference(changed, original)
        except (ValueError, KeyError, TypeError):
            continue
        raise ValueError("Invalid source relocation reference was accepted")
    return len(cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-frozen-history", action="store_true")
    parser.add_argument("--archives", type=Path)
    parser.add_argument("--korda-source", type=Path, help="Verify referenced bytes from fixed commits in an existing Korda checkout")
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    graph = read_json(ROOT / "delivery-graph.json")
    record = read_json(ROOT / PREFIX / "acceptance.json")
    validate_history(graph)
    validate_current(graph["current_execution"], record["state"])
    validate_acceptance(record)
    if args.require_complete:
        require(record["state"] == "accepted", "DB-Perf-01 is not accepted; pending work cannot be waived by this gate")
    validate_baseline(read_json(ROOT / PREFIX / "baseline.json"), args.archives)
    validate_diagnostic_indexes()
    source_scope = validate_source_scope(record["state"], args.korda_source)
    for name in ("plan.md", "handoff-linux.md", "allocation-inventory.md"):
        path = ROOT / PREFIX / name
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if not re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) and not target.startswith("#"):
                require((path.parent / target.split("#", 1)[0]).is_file(), f"Broken local link: {target}")
    count = negative_controls(record)
    source_count = source_negative_controls()
    if args.verify_frozen_history:
        with tempfile.TemporaryDirectory(prefix="db-perf-history-", dir=ROOT.parent) as temp:
            work = Path(temp) / "Plan"
            subprocess.run(["git", "worktree", "add", "--detach", str(work), FROZEN], cwd=ROOT, check=True)
            try:
                subprocess.run(["python3", "tools/verify_db_rename.py"], cwd=work, check=True)
            finally:
                subprocess.run(["git", "worktree", "remove", "--force", str(work)], cwd=ROOT, check=True)
    print(json.dumps({"task": "DB-Perf-01", "record_integrity": "passed", "negative_controls": count,
                      "state": record["state"], "accepted_long_segments": record["long_tests"]["accepted_count"],
                      "archives_verified": args.archives is not None,
                      "source_references": source_scope,
                      "source_reference_negative_controls": source_count,
                      "frozen_history_executed": args.verify_frozen_history,
                      "performance_execution_claimed_by_this_gate": False}, indent=2))


if __name__ == "__main__":
    main()
