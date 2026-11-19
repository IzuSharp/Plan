"""Project only typed synthetic numbers, fixed enums and hashes from this actual pair."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re

EXPECTED = {
    "execution": "c64debb45b30388809373695dfda3e59714571debf3db8801b4672a54c7de796",
    "pair": "bfca614ae18a47237df7f1fdea5daed54a364cd087a12118fc3937aaedee130d",
    "synchronous": "311a8720af69a7a57e7fbf347b73e3a48fe7f7393d009104949ed56f0b8b3fca",
    "threaded": "205ec4f49539835997a1e3ec3ac732329ff6612daad4197fb0b6a1187ba2c3bb",
}
ROLES = ("application", "target", "scheduler", "controller")
PHASES = ("startup-and-seed", "measurement", "reconciliation-and-shutdown",
          "post-load-recovery", "post-load-idle", "final-reconciliation-and-shutdown")
RESOURCE_KEYS = ("samples", "cpu_samples", "cpu_seconds", "cpu_percent_one_core", "cpu_span_seconds",
                 "rss_peak_bytes", "rss_window_overlap_samples", "rss_window_overlap_peak_bytes",
                 "fd_peak_count", "socket_peak_count")
ERROR_KEYS = ("affinity", "cpu", "descriptor", "identity", "memory")
SOURCE_ENUMS = {"Perf-01", "observer-diagnostic-pair", "postgresql", "http1", "nativeweave-aot-rust",
                "deferred", "synchronous", "threaded", "unavailable", "not-established",
                "phase-or-measurement-window-overlap", "phase-cpu-endpoints",
                "driver-process", "target-observed-load", "source-bound-summary-projection"}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path, expected=None):
    assert path.stat().st_size <= 1024 * 1024
    raw = path.read_bytes()
    actual = digest(raw)
    assert expected is None or actual == expected
    return json.loads(raw), actual


def strict_public(value):
    """Reject unrestricted strings/keys and non-finite numbers before writing."""
    if isinstance(value, dict):
        for key, item in value.items():
            assert isinstance(key, str) and re.fullmatch(r"[a-z][a-z0-9_-]*", key)
            strict_public(item)
    elif isinstance(value, list):
        for item in value:
            strict_public(item)
    elif isinstance(value, str):
        assert value in SOURCE_ENUMS or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value) or re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)", value)
    else:
        assert value is None or type(value) in (int, float, bool)
        if type(value) is float:
            assert math.isfinite(value)


def write(path, value):
    strict_public(value)
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    with path.open("xb") as stream:
        stream.write(raw)
    return digest(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execution", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    assert sorted(os.sched_getaffinity(0)) == [8]
    assert args.output.is_dir()
    source_sha = digest(Path(__file__).read_bytes())
    execution, execution_sha = read(args.execution, EXPECTED["execution"])
    pair, pair_sha = read(args.evidence / "audit-pair/analysis.json", EXPECTED["pair"])
    assert execution["state"] == "diagnostic-functional-equivalence-completed"
    assert execution["functional_equivalence_passed"] is pair["functional_equivalence_passed"] is True
    assert execution["duration_credit_seconds"] == pair["duration_credit_seconds"] == 0
    assert pair["formal_timing_eligible"] is pair["product_performance_gain_claimed"] is False
    assert execution["pair_audit"]["exit_code"] == 0
    assert all(row["passed"] is True for row in pair["checklist"])
    assert execution["document_sha256"] == pair["document_sha256"] == "2f7a7149d3f8de59a90b1cd569032bb16a203957c4807062e8a5330c6f1368e0"
    result = {"schema_version": 1, "task": "Perf-01", "kind": "observer-diagnostic-pair",
              "projection_source_sha256": source_sha, "formal_timing_eligible": False,
              "duration_credit_seconds": 0, "product_performance_gain_claimed": False,
              "functional_equivalence_passed": True, "noise_clearance": "not-established",
              "long_heap_clearance": "not-established", "supervisor_started_utc": execution["started_utc"],
              "supervisor_finished_utc": execution["ended_utc"], "pair_audit_exit_code": 0,
              "pair_audit_checks": len(pair["checklist"]),
              "input_sha256": {"execution": execution_sha, "pair_audit": pair_sha,
                  "command_document": pair["document_sha256"], "auditor": pair["extractor_sha256"],
                  "supervisor": execution["supervisor_source_sha256"]},
              "configuration": {"provider": "postgresql", "protocol": "http1", "route": "nativeweave-aot-rust",
                  "arrival_rate": 144, "concurrency": 16, "nominal_load_seconds": 120, "warmup_operations": 16,
                  "recovery_operations": 32, "idle_seconds": 60, "scheduler_gc": "deferred",
                  "application_rss_limit_bytes": 268435456, "arrival_p99_limit_ns": 500000000,
                  "dispatch_lag_limit_ns": 100000000, "service_cpu_count": 2, "generator_cpu_count": 2,
                  "measurement_driver_commit": "a3ce0f6295c535b0a81de95fc0f98aa19deb259c",
                  "measurement_driver_tree": "eb6b61e7c159c343513f7a50359f1a6c09f8df77",
                  "product_before_commit": "ea5fa528035d025bd7a28698ee7c71194432236c"}, "cells": {}}
    for index, mode in enumerate(("synchronous", "threaded"), 1):
        location = args.evidence / ("audit-" + str(index).zfill(2) + "-" + mode)
        audit, audit_sha = read(location / "analysis.json", EXPECTED[mode])
        cell = audit["cell"]
        assert cell == pair["cells"][mode]
        assert audit["semantic_resource_gate_passed"] is True and all(row["passed"] is True for row in audit["checklist"])
        assert len(audit["checklist"]) == (84 if mode == "synchronous" else 78)
        actual = execution["commands"][index - 1]
        assert actual["policy"] == mode and actual["exit_code"] == actual["audit"]["exit_code"] == 0
        assert actual["audit"]["analysis_sha256"] == audit_sha
        summary, summary_sha = read(location / mode / "summary.json", cell["summary_sha256"])
        policy, policy_sha = read(location / mode / "scheduler-gc.json", summary["scheduler_gc_receipt"]["sha256"])
        window = cell["measurement_window"]
        assert summary["outcomes"] == {"ok": 17282} and summary["invalid_reasons"] == []
        assert cell["operations"] == summary["successful"] == summary["offered"] == summary["dispatched"] == 17282
        assert all(cell["performance_validity"][key] is True for key in
                   ("raw_valid", "summary_valid", "qualifies_service_standard", "dispatch_lag_gate_passed",
                    "arrival_p99_gate_passed", "conservative_application_rss_gate_passed"))
        out = {"driver_started_utc": actual["started_utc"], "driver_finished_utc": actual["ended_utc"],
               "driver_elapsed_seconds": actual["elapsed_seconds"], "driver_utc_scope": "driver-process",
               "target_load_started_utc": summary["phases"]["load"]["start_utc"],
               "target_load_finished_utc": summary["phases"]["load"]["last_completion_utc"],
               "load_utc_scope": "target-observed-load", "effective_duration_ns": window["elapsed"],
               "driver_exit_code": actual["exit_code"], "audit_exit_code": actual["audit"]["exit_code"],
               "audit_checks_passed": len(audit["checklist"]), "operations": cell["operations"],
               "cycles": cell["mix"]["cycle"], "pages": cell["mix"]["list"],
               "successful_per_second": cell["successful_per_second"],
               "arrival_latency_ns": {key: cell["arrival_latency_ns"][key] for key in ("p50", "p95", "p99")},
               "dispatch": {key: cell["dispatch"][key] for key in
                    ("maximum_ns", "mean_ns", "p50_ns", "p95_ns", "p99_ns", "span_ns", "above_50ms", "above_100ms")},
               "original_valid": summary["valid"], "original_qualifies_service_standard": summary["qualifies_service_standard"],
               "original_invalid_reason_count": len(summary["invalid_reasons"]),
               "measurement_errors": 0, "measurement_timeouts": 0, "measurement_cancellations": 0,
               "measurement_rejections": 0, "unexpected_provider_exceptions": summary["provider_errors"]["observed_exceptions"],
               "business_retry_attempts": summary["business_retry_attempts"], "resources": {}, "samplers": {},
               "input_sha256": {"side_audit": audit_sha, "summary": summary_sha, "scheduler_gc_receipt": policy_sha,
                    "observation": cell["observation_sha256"], "dataset": cell["dataset_sha256"]},
               "scheduler_gc": {"collections_during_scope": policy["collections_during_scope"],
                    "initial_enabled": policy["initial_gc"]["enabled"], "entry_enabled": policy["scope_entry_gc"]["enabled"],
                    "exit_enabled": policy["scope_exit_gc"]["enabled"], "restored_enabled": policy["restored_gc"]["enabled"],
                    "scope_seconds": (policy["scope_finished_ns"] - policy["scope_started_ns"]) / 1e9},
               "managed_gc": "unavailable", "managed_allocation": "unavailable",
               "recovery_operations": cell["recovery_operations"], "idle_duration_ns": cell["idle_duration_ns"],
               "persisted_rows_per_table_before_recovery": cell["durable_counts_before_recovery"],
               "persisted_rows_per_table_before_shutdown": cell["durable_counts_after_recovery"],
               "checklist": {"full_operation_oracle": cell["all_expected_values_matched"],
                    "supervision_cleanup": cell["supervision_cleanup_passed"]}}
        for key, check_name in {
            "full_raw_accounting_no_late_errors": "complete raw accounting and no late/error records",
            "full_outcome_journal_published": "complete published warmup/measurement journal",
            "independent_sql_before_recovery": "independent SQL persisted_before_recovery",
            "independent_sql_before_shutdown": "independent SQL persisted_before_shutdown",
            "durable_content_oracle": "independent durable oracle cardinality",
            "recovery_and_idle": "same-process recovery and idle",
            "ownership_and_application_closure": "original application correctness and closure",
            "database_teardown": "database teardown", "gc_restore": "normal GC lifecycle and exact deltas",
            "sampler_completion": "generator observer completed without identity/errors",
            "actual_loaded_binaries": "exact original before package and libraries",
            "actual_driver_sources": "exact measured runtime helper/source map",
        }.items():
            matches = [x for x in audit["checklist"] if x["name"] == mode + ": " + check_name]
            assert len(matches) == 1 and matches[0]["passed"] is True
            out["checklist"][key] = True
        phases_by_role = {"application": cell["application_resources"], **cell["generator_resources"]}
        for role in ROLES:
            phases = phases_by_role[role]
            assert set(phases) <= set(PHASES)
            projected = {}
            for phase in PHASES:
                if phase not in phases:
                    continue
                value = phases[phase]
                selected = {key: value.get(key) for key in RESOURCE_KEYS}
                selected["error_samples"] = {key: value["error_samples"][key] for key in ERROR_KEYS}
                selected["first_rss_bytes"] = value["first"]["rss_bytes"]
                selected["last_rss_bytes"] = value["last"]["rss_bytes"]
                if phase == "measurement":
                    first, last = value["first"]["cpu_observed_ns"], value["last"]["cpu_observed_ns"]
                    selected["cpu_first_offset_from_window_start_ns"] = first - window["start"]
                    selected["cpu_last_offset_from_window_end_ns"] = last - window["end"]
                    selected["cpu_bracket_intersection_with_window_ns"] = max(0, min(last, window["end"]) - max(first, window["start"]))
                    selected["rss_scope"] = "phase-or-measurement-window-overlap"
                    selected["cpu_scope"] = "phase-cpu-endpoints"
                projected[phase] = selected
            out["resources"][role] = projected
        for sampler in ("a21", "application", "generator"):
            raw = cell["sampler_execution"][sampler]
            out["samplers"][sampler] = {"samples": raw["samples"], "distinct_worker_threads_observed": len(raw["thread_ids"]),
                "cross_phase_samples": raw.get("cross_phase_samples"), "unavailable_rss_samples": raw.get("unavailable_rss_samples")}
        out["samplers"]["target_pool_distinct_worker_threads_observed"] = len(
            set(cell["sampler_execution"]["application"]["thread_ids"]) | set(cell["sampler_execution"]["generator"]["thread_ids"]))
        result["cells"][mode] = out
    left, right = [result["cells"][mode] for mode in ("synchronous", "threaded")]
    def delta(a, b):
        return {"absolute": b - a, "relative_percent": (b - a) / a * 100 if a else None}
    result["threaded_minus_synchronous"] = {
        "successful_per_second": delta(left["successful_per_second"], right["successful_per_second"]),
        "arrival_p99_ns": delta(left["arrival_latency_ns"]["p99"], right["arrival_latency_ns"]["p99"]),
        "dispatch_maximum_ns": delta(left["dispatch"]["maximum_ns"], right["dispatch"]["maximum_ns"]),
        "dispatch_p99_ns": delta(left["dispatch"]["p99_ns"], right["dispatch"]["p99_ns"]),
        "resources": {role: {key: delta(left["resources"][role]["measurement"][key], right["resources"][role]["measurement"][key])
            for key in ("cpu_seconds", "cpu_percent_one_core", "rss_peak_bytes")} for role in ROLES}}
    result["loaded_sha256"] = {}
    for label, filename in {"application": "NativeWeave.Reference.TaskService", "server_native": "libnativeweave_server.so",
                            "postgresql_native": "libnw_database_postgresql.so", "sqlite_native": "libnw_database_sqlite.so"}.items():
        hashes = []
        for mode in ("synchronous", "threaded"):
            matched = [value for path, value in pair["cells"][mode]["loaded_files"].items() if Path(path).name == filename]
            assert len(matched) == 1
            hashes.extend(matched)
        assert hashes[0] == hashes[1]
        result["loaded_sha256"][label] = hashes[0]
    output_sha = write(args.output / "public-summary.json", result)
    receipt = {"schema_version": 1, "kind": "source-bound-summary-projection", "started_utc": started,
        "finished_utc": datetime.now(timezone.utc).isoformat(), "exit_code": 0, "cpu_affinity": [8],
        "projection_source_sha256": source_sha, "output_sha256": output_sha,
        "input_sha256": {**EXPECTED}, "side_audit_checks": [84, 78], "pair_audit_checks": len(pair["checklist"]),
        "typed_allowlist_validation_passed": True, "raw_replayed": False, "new_workload_run": False,
        "duration_credit_seconds": 0}
    write(args.output / "projection-execution.json", receipt)
    print(json.dumps({"public_summary_sha256": output_sha, "source_sha256": source_sha,
                      "projection_exit_code": 0, "duration_credit_seconds": 0}))


if __name__ == "__main__":
    main()
