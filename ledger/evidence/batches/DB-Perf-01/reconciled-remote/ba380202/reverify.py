#!/usr/bin/env python3
"""Recheck retained public preflight identities; this does not execute a benchmark."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import zipfile


HERE = Path(__file__).resolve().parent
BATCH = HERE.parents[1]
ROOT = BATCH.parents[3]
REMOTE = "ba380202e7b36cbfe8dcd4bc2cfa0afe86048d92"
BASELINE = "771bc77cbd68d3f932b99ed2497c0697bbba5f02"
LAZY_ONLY = "28110ee03391831c737a54204730730a01b77a34"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def ref(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def read(path):
    return json.loads(Path(path).read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_window(window):
    require(window["end"]["allocated_bytes"] - window["start"]["allocated_bytes"]
            == window["allocated_bytes_total"], "Cumulative allocation counters differ")
    require(window["end"]["timestamp"] >= window["start"]["timestamp"], "Reversed interval")
    for generation in range(3):
        key = f"gc{generation}"
        require(window["end"][key] - window["start"][key] == window[f"{key}_delta"], "GC counters differ")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harness-repository", type=Path, required=True)
    parser.add_argument("--candidate-repository", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "schema_version": 1,
        "task": "DB-Perf-01",
        "kind": "read_only_reconciliation_verification",
        "verified_at_utc": datetime.now(timezone.utc).isoformat(),
        "origin_plan_commit": REMOTE,
        "origin_worktree": "/workspace/scratch/754bc732518e",
        "verifier_worktree": "/workspace/scratch/b94e2a0e0c3f",
        "execution_authorship": "Recovered concurrent execution, not rerun or attributed to the reconciling executor.",
        "final_candidate_acceptance": False,
        "long_test_credit": 0,
        "script": ref(Path(__file__).resolve()),
        "argv": ["python3", str(Path(__file__).resolve()), "--harness-repository", str(args.harness_repository),
                 "--candidate-repository", str(args.candidate_repository)],
        "sides": {},
    }
    manifests = {}
    for side, directory, expected_commit in (
        ("before", "korda-allocation", BASELINE),
        ("lazy_join_only", "korda-allocation-after-lazy-join", LAZY_ONLY),
    ):
        folder = BATCH / "preflight" / directory
        manifest_path = folder / "build-manifest.json"
        manifest = read(manifest_path)
        manifests[side] = manifest
        sources = {}
        for name, expected in manifest["source_files"].items():
            path = args.harness_repository / "benchmarks/Database/allocations" / name
            require(sha(path) == expected, f"Harness input changed: {name}")
            sources[name] = expected
        providers = {}
        for provider, identity in manifest["providers"].items():
            require(identity["source_commit"] == expected_commit, "Wrong measured producer")
            bound = {"source_commit": expected_commit, "package_version": identity["version"], "files": {}}
            for role in ("package", "executable", "native"):
                path = Path(identity[f"{role}_path"])
                require(sha(path) == identity[f"{role}_sha256"], f"Artifact changed: {path}")
                bound["files"][role] = {"path": str(path), "sha256": sha(path), "bytes": path.stat().st_size}
            release_path = folder / f"{provider}-release.json"
            require(sha(release_path) == identity["release_receipt_sha256"], "Release receipt changed")
            release = read(release_path)
            entry = next(item for item in release["packages"] if item["id"] == identity["package_id"])
            require(entry["source_commit"] == expected_commit, "Package source differs")
            with zipfile.ZipFile(identity["package_path"]) as archive:
                names = [name for name in archive.namelist() if not name.endswith("/")]
                require(len(names) == len(set(names)) and set(names) == set(entry["unsigned_entries"]), "Package entry set differs")
                for name, expected in entry["unsigned_entries"].items():
                    require(hashlib.sha256(archive.read(name)).hexdigest() == expected, f"Package member differs: {name}")
            bound["verified_package_members"] = len(names)
            raw_files = []
            windows = []
            complete = {}
            refill = []
            process_ids = []
            for run in manifest["runs"]:
                if run["provider"] != provider:
                    continue
                path = folder / run["result"]
                require(sha(path) == run["result_sha256"], "Raw result changed")
                raw = read(path)
                require(raw["source_commit"] == expected_commit and raw["native_aot"] is True, "Unbound raw source/AOT")
                require(raw["package_sha256"] == identity["package_sha256"]
                        and raw["executable_sha256"] == identity["executable_sha256"]
                        and raw["loaded_native_sha256"] == identity["native_sha256"], "Raw artifact identity differs")
                require(raw["dataset_rows"] == 256 and raw["batch_rows"] == 128
                        and raw["expected_query_checksum"] == 32896 and raw["measured_iterations"] == 128,
                        "Measured input changed")
                require(raw["session_local_resources_released"] and raw["source_local_resources_released"]
                        and raw["native_counters_after_source_close"][:6] == [0] * 6, "Tracked owners did not drain")
                process_ids.append(raw["process_id"])
                raw_files.append(ref(path))
                for key in ("complete_queries", "within_first_batch", "supplemental_fetch_including_first_row", "empty_sync_control"):
                    for window in raw[key]:
                        verify_window(window)
                for key in ("empty_async_control", "source_open_idle_control"):
                    verify_window(raw[key])
                    require(raw[key]["allocated_bytes_total"] == 0, "Nonzero control")
                require(len(raw["within_first_batch"]) == 128 and len(raw["empty_sync_control"]) == 128, "Wrong window count")
                for window in raw["within_first_batch"]:
                    require(window["rows"] == 127 and window["operations"] == 127
                            and window["incomplete_move_observations"] == 0
                            and window["await_thread_changes"] == 0, "Window is not the claimed synchronous row path")
                    require(all(window[f"gc{generation}_delta"] == 0 for generation in range(3)), "Narrow GC delta changed")
                    require(window["allocated_bytes_total"] == (11176 if side == "before" else 0), "Narrow raw count changed")
                require(all(item["allocated_bytes_total"] == 0 for item in raw["empty_sync_control"]), "Nonzero empty control")
                windows.extend(raw["within_first_batch"])
                refill.extend(raw["supplemental_fetch_including_first_row"])
                for item in raw["complete_queries"]:
                    totals = complete.setdefault(item["name"], {"raw_allocated_bytes": 0, "operations": 0, "rows": 0})
                    for source, target in (("allocated_bytes_total", "raw_allocated_bytes"), ("operations", "operations"), ("rows", "rows")):
                        totals[target] += item[source]
            require(len(raw_files) == 3 and len(set(process_ids)) == 3, "Expected three distinct processes")
            bound.update(raw_files=raw_files, independent_processes=3, process_ids=process_ids,
                         synchronous_windows=len(windows), synchronous_rows=sum(w["rows"] for w in windows),
                         synchronous_raw_allocated_bytes=sum(w["allocated_bytes_total"] for w in windows),
                         complete_queries=complete, refill_windows=len(refill),
                         refill_raw_allocated_bytes=sum(w["allocated_bytes_total"] for w in refill),
                         exact_framework_fraction_of_positive_totals="unproven")
            providers[provider] = bound
            if side == "lazy_join_only":
                receipt = {
                    "task": "DB-Perf-01", "kind": "normal_public_api_allocation", "process_wide": True,
                    "provider": provider, "path_id": "lazy_join_only_sync_numeric_in_batch",
                    "source_commit": expected_commit, "package_version": identity["version"],
                    "package_sha256": identity["package_sha256"], "executable_sha256": identity["executable_sha256"],
                    "native_sha256": identity["native_sha256"], "independent_processes": 3,
                    "operations": sum(w["operations"] for w in windows), "rows": sum(w["rows"] for w in windows),
                    "batches": len(windows), "raw_allocated_bytes": 0, "business_allocated_bytes": 0,
                    "framework_allocated_bytes": 0, "other_attributed_bytes": 0, "unattributed_bytes": 0,
                    "suspended_operations": 0,
                    "gc_counts": [sum(w[f"gc{generation}_delta"] for w in windows) for generation in range(3)],
                    "attribution_method": "Every whole-process cumulative start/end pair is identical; no subtraction, DTO, string, list or result array in this numeric in-batch window.",
                    "boundary": "127 synchronous numeric MoveNext calls inside an already fetched/parsed first batch; 128 windows per process.",
                    "excluded": ["query construction", "binding", "first fetch", "refill", "final false", "disposal", "connection acquisition/return", "concurrency", "cancellation", "exceptions"],
                    "origin_plan_commit": REMOTE, "origin_worktree": result["origin_worktree"],
                    "execution_authorship": result["execution_authorship"], "final_candidate_acceptance": False,
                    "raw_files": raw_files + [ref(manifest_path)],
                }
                (HERE / f"{provider}-narrow-allocation.json").write_text(json.dumps(receipt, indent=2) + "\n")
        result["sides"][side] = {"manifest": ref(manifest_path), "consumer_sources": sources, "providers": providers}
    require(manifests["before"]["source_files"] == manifests["lazy_join_only"]["source_files"], "Different consumer sources")
    producer = read(BATCH / "preflight/korda-allocation-after-lazy-join/candidate-build-receipt.json")
    require(producer["source_commit"] == LAZY_ONLY, "Wrong candidate receipt")
    tree = subprocess.check_output(["git", "rev-parse", LAZY_ONLY + "^{tree}"], cwd=args.candidate_repository, text=True).strip()
    require(tree == producer["source_tree"], "Candidate tree differs")
    for path, expected in producer["tracked_product_inputs"].items():
        data = subprocess.check_output(["git", "show", LAZY_ONLY + ":" + path], cwd=args.candidate_repository)
        require(hashlib.sha256(data).hexdigest() == expected, f"Producer source differs: {path}")
    result["candidate_source_tree"] = tree
    result["candidate_tracked_inputs_verified"] = len(producer["tracked_product_inputs"])
    result["result"] = "passed_read_only_integrity_and_counter_reconciliation"
    result["not_reusable_as"] = ["ci.1 combined/scalar candidate", "future final package", "dedicated-host timing", "full public API zero allocation", "any 30-minute segment"]
    (HERE / "public-preflight-verification.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"result": result["result"], "raw_processes": 12,
                      "candidate_tracked_inputs_verified": result["candidate_tracked_inputs_verified"],
                      "long_test_credit": 0}, indent=2))


if __name__ == "__main__":
    main()
