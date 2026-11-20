#!/usr/bin/env python3
"""Project hash-bound completed calibration metadata; never open full raw journals."""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys

PINS = {
    "calibration_execution": "04a052a4902d8b191ccb68d8c2a22b8632db37db33a1d51cfe14b786c145325c",
    "noise_execution": "ba45fbd2141eae25b3896bb7f0fda00af8401a0a897f00e5e1f544e067f2b8a5",
    "postgresql": {
        "controller": "4a87700447f84853ef68c2edbdf81a9cf76b45c1d8dd799e74b99a41edc73206",
        "selection": "2070cae31ab0e72d69f1b02eea237dab7c3dc87f62b248c95cfef104d7528f43",
        "noise": "1da887679a1e115070428d38c4069e35faacd6288f24c5854d6afefc64d697f1",
        "cells": 13, "rate": 220, "long_rate": 144},
    "sqlite": {
        "controller": "6b06eea81b24cbec2e7b916dc8f0552182887771e20b3c681e53c3d6e4340831",
        "selection": "5d9b6bbec0186503ddfdab3b9d21fedc95bd0fa5480841e4faba44036b24436f",
        "noise": "69a4c8b909b1336fae7302944f2db176856a84addc96e85275b037009a405557",
        "cells": 11, "rate": 60, "long_rate": 40},
}
SOURCE_PINS = {
    "controller": "b1c9156ab1e72f46ca551ff92a5c7d88f0bdafa69d6762d9b2b5303a5445d4d9",
    "noise_extractor": "d4c2a887452985697b3ec69d45500b4cf87185c9b54433ed887224047524f3de",
    "comparison_reader": "0f3ee6ca0d4ce9fcdce256df9b9fce1f9ce5eaa9032c3afa86e443aeceff59b8",
    "driver_commit": "a3ce0f6295c535b0a81de95fc0f98aa19deb259c",
    "product_commit": "ea5fa528035d025bd7a28698ee7c71194432236c",
    "database_amendment": "98f8e537d87cac9de87cb2d1ae1150465a5c9a052333451f0772398b58ad58c3",
    "original_policy": "0c7cd866b1ad0fc86d647e31dd1b6fe0b148d2e7ca54d83b7286cec09f11cafc",
    "scheduler_gc_policy": "a2fa36f9ef4a05d7d56d05dc7d8dcd6f881e3849285907ed1d132b32b9fe9cb7",
    "resource_sampling_policy": "19d72617af9acb329148dbae9f6e0419e79013f7d9381998957b310eec008826",
}
LOADED = {
    "application": ("NativeWeave.Reference.TaskService", "6f2bd3e2b31422393d0e9543388f238226df2e3ab8f7e67c7f6b613a00e650d3"),
    "server": ("libnativeweave_server.so", "4827a6ecc76f871e0b4828f4ff6fe23a0d0a4ca1c57c5fc89a10a8e4d83ffe69"),
    "postgresql": ("libnw_database_postgresql.so", "b0510d35c2b7b633a9aade7a5d3ad9a74498b54fbe23863c770881e38442a6f3"),
    "sqlite": ("libnw_database_sqlite.so", "7254f8e490f19637701d92523c2ba08e0cbdfdbe4c5f28173d4215b5f303da8d"),
}
ROLES = ("application", "target", "scheduler", "controller")
PHASES = {"measurement": "measurement", "recovery": "post-load-recovery", "idle": "post-load-idle"}
OUTCOMES = ("ok", "error", "timeout", "cancelled", "rejected")
COUNTERS = ("connection_pool_wait_ns", "copied_bytes", "database_execution_ns", "database_lock_wait_ns", "ffi_calls", "native_allocator_live_bytes", "sqlite_busy_handler_attempts")
INPUTS = []
CHECKS = 0


def check(condition):
    global CHECKS
    CHECKS += 1
    if not condition:
        raise ValueError("Source-bound metadata check failed at check " + str(CHECKS))


def digest(b):
    return hashlib.sha256(b).hexdigest()


def read_json(path, role, provider=None, index=None, expected=None):
    path = Path(path)
    check(path.stat().st_size <= 1024 * 1024)
    b = path.read_bytes()
    h = digest(b)
    if expected:
        check(h == expected)
    INPUTS.append({"role": role, "provider": provider, "cell_index": index, "bytes": len(b), "sha256": h})
    return json.loads(b), h


def relocated(recorded, original_cell, cell):
    suffix = Path(recorded).relative_to(Path(original_cell))
    result = cell / suffix
    check(result.resolve().is_relative_to(cell.resolve()))
    return result


def outcomes(source):
    check(set(source).issubset(OUTCOMES))
    check(all(type(v) is int and v >= 0 for v in source.values()))
    return {k: source.get(k, 0) for k in OUTCOMES}


def scalar(source, names):
    result = {name: source.get(name) for name in names}
    check(all(v is None or type(v) in (int, float, bool) for v in result.values()))
    return result


def counters(source):
    return {k: scalar(source[k], ("value",))["value"] for k in COUNTERS}


def resources(source):
    result = {}
    fields = ("samples", "cpu_samples", "cpu_seconds", "cpu_span_seconds", "cpu_percent_one_core", "rss_peak_bytes", "rss_window_overlap_peak_bytes", "rss_window_overlap_samples", "fd_peak_count", "socket_peak_count", "descriptor_scan_misses")
    for role in ROLES:
        phases = source["resources"] if role == "application" else source["generator_resources"][role]
        result[role] = {}
        for public, original in PHASES.items():
            x = phases.get(original, {})
            row = scalar(x, fields)
            row["error_samples"] = scalar(x.get("error_samples", {}), ("affinity", "cpu", "descriptor", "identity", "memory"))
            row["identity_count"] = len(x.get("identities", []))
            if public == "measurement":
                check(x.get("rss_inclusion_policy") == "Worker-start phase measurement OR read span overlaps actual A21 measurement window")
            result[role][public] = row
    return result


def phase_times(p):
    return {"start_utc": p["start_utc"], "end_utc": p["end_utc"], "seconds": (p["end_ns"] - p["start_ns"]) / 1e9}


def project_cell(c, base, provider):
    index = c["index"]
    cell = base / Path(c["directory"]).name
    summary, summary_hash = read_json(cell / "summary.json", "summary", provider, index, c["summary_sha256"])
    progress, _ = read_json(cell / "progress.json", "progress", provider, index)
    frozen, _ = read_json(cell / "frozen-inputs.json", "frozen_inputs", provider, index, c["frozen_inputs_sha256"])
    pr, _ = read_json(relocated(summary["perf01_receipt"]["path"], c["directory"], cell), "perf01_receipt", provider, index, summary["perf01_receipt"]["sha256"])
    gc, _ = read_json(relocated(summary["scheduler_gc_receipt"]["path"], c["directory"], cell), "scheduler_gc_receipt", provider, index, c["scheduler_gc_receipt_sha256"])
    supervision, _ = read_json(cell / "supervision/receipt.json", "supervision_receipt", provider, index)
    check(progress == {"state": "completed" if summary["valid"] else "completed-invalid", "summary_sha256": summary_hash})
    check(frozen["driver_source"]["commit"] == SOURCE_PINS["driver_commit"] and frozen["driver_source"]["scope_status"] == "")
    check(frozen["route"]["source"]["commit"] == SOURCE_PINS["product_commit"] and frozen["route"]["source"]["scope_status"] == "")
    check(frozen["service_standard"] == {"max_app_rss_mib": 256.0, "max_generator_dispatch_lag_ms": 100, "max_p99_ms": 500.0, "max_unexpected_errors": 0})
    check(summary["provider"] == provider and summary["variant"] == "before" and summary["stage"] == "short")
    check(summary["concurrency"] == 16 and summary["rate"] == c["rate"])
    check(summary["valid"] == c["valid"] and summary["qualifies_service_standard"] == c["qualifies"])
    check(summary["outcomes"].get("ok", 0) == summary["successful"] == c["successes"])
    check(summary["offered"] == c["offered"] and sum(summary["outcomes"].values()) == summary["offered"])
    check(summary["p99_ns"] == c["p99_ns"] and summary["successful_per_second"] == c["throughput"])
    check(summary["invalid_reasons"] == c["invalid_reasons"])
    reason_map = {"generator saturation: in-flight capacity": "generator_inflight_saturation"}
    check(all(r in reason_map for r in c["invalid_reasons"]))
    check(gc["status"] == "completed" and gc["worker_exit_code"] == 0)
    check(gc["plan_sha256"] == frozen["plan_sha256"])
    check(gc["policy_sha256"] == SOURCE_PINS["scheduler_gc_policy"])
    check(gc["policy"]["mode"] == "deferred" and gc["collections_during_scope"] == [0, 0, 0])
    check(not gc["scope_entry_gc"]["enabled"] and not gc["scope_exit_gc"]["enabled"])
    check(gc["initial_gc"]["enabled"] == gc["restored_gc"]["enabled"])
    check(summary["scheduler_gc_policy_valid"] is True)
    check(summary["resource_sampling_policy"]["mode"] == "threaded" and summary["resource_sampling_policy_sha256"] == SOURCE_PINS["resource_sampling_policy"])
    check(pr["status"] == "passed" and pr["business_retry_attempts"] == summary["business_retry_attempts"])
    check(not summary["permanent_integrity_halt"] and not summary["classified_error_counts"])
    check(supervision["status"] == "completed" and supervision["worker_exit_code"] == 0 and supervision["failure"] is None)
    check(not supervision["live_owned_processes_after_cleanup"] and not supervision["signals"] and not supervision["registry_errors"])
    check(summary["closed"] == {"consumerResourcesReleased": True, "consumerStatus": "Succeeded", "databaseResourcesReleased": True, "databaseStatus": "Succeeded", "serverState": "Disposed"})
    journal = pr["outcome_journal"]
    check(journal["status"] == "completed" and journal["sealed"] and journal["published"] and journal["closed"] and journal["error"] is None)
    check(journal["rows"] == summary["dispatched"] + 16)
    recovery = summary["phases"]["recovery"]
    check(len(recovery["operations"]) == 16 and all(o["status"] == "ok" for o in recovery["operations"]))
    check(recovery["oracle"]["passed"] and summary["durable_oracle"]["passed"])
    persisted = {}
    for name in ("persisted_before_recovery", "persisted_before_shutdown"):
        p = summary[name]
        check(p["availability"] == "measured")
        count = sum(p["committed_operations_by_phase"].values())
        check(all(p["persisted_rows"][k] == count for k in ("items", "operations", "outbox")))
        persisted[name] = {"utc": p["utc"], "rows_per_table": count, "commits_by_phase": {k: p["committed_operations_by_phase"].get(k, 0) for k in ("seed", "warmup", "measurement", "recovery")}}
    check(persisted["persisted_before_recovery"]["commits_by_phase"]["measurement"] == summary["by_kind"]["cycle"]["successful"])
    check(summary["durable_oracle"]["operations"] == persisted["persisted_before_recovery"]["rows_per_table"])
    loaded = {Path(k).name: v["sha256"] for k, v in summary["loaded_files"].items()}
    expected_loaded = {v[0]: v[1] for k, v in LOADED.items() if provider == "postgresql" or k != "postgresql"}
    check(loaded == expected_loaded)
    obs = summary["generator_resource_observer"]
    check(obs["status"] == "completed" and not obs["errors"] and not obs["identity_failures"])
    row = {
        "index": index, "phase": "confirmation" if c["phase"].startswith("confirmation-") else c["phase"],
        "confirmation_index": int(c["phase"].split("-")[1]) if c["phase"].startswith("confirmation-") else None,
        "rate": c["rate"], "requested_seconds": c["seconds"], "concurrency": summary["concurrency"],
        "controller_start_utc": c["start_utc"], "controller_end_utc": c["end_utc"], "driver_exit_code": c["exit_code"],
        "valid": c["valid"], "qualifies_service_standard": c["qualifies"], "recorded_progress_state": progress["state"],
        "invalid_reasons": [reason_map[r] for r in c["invalid_reasons"]],
        "status": "qualified" if c["qualifies"] else ("service_standard_failed" if c["valid"] else "generator_invalid"),
        "summary_sha256": summary_hash, "frozen_inputs_sha256": c["frozen_inputs_sha256"], "dataset_sha256": frozen["dataset_sha256"],
        "timing": scalar(summary, ("planned_load_seconds", "actual_dispatch_span_seconds", "observation_seconds")),
        "load_target_start_utc": summary["phases"]["load"]["start_utc"],
        "load_target_end_utc": summary["phases"]["load"]["last_completion_utc"],
        "offered": summary["offered"], "dispatched": summary["dispatched"], "successful": summary["successful"],
        "successful_per_second": summary["successful_per_second"], "outcomes": outcomes(summary["outcomes"]),
        "latency_ns": scalar(summary, ("p50_ns", "p95_ns", "p99_ns")),
        "by_kind": {k: {"offered": summary["by_kind"][k]["offered"], "successful": summary["by_kind"][k]["successful"], "outcomes": outcomes(summary["by_kind"][k]["outcomes"]), "latency_ns": scalar(summary["by_kind"][k], ("p50_ns", "p95_ns", "p99_ns"))} for k in ("cycle", "list")},
        "provider_errors": scalar(summary["provider_errors"], ("observed_exceptions", "sqlite_busy", "sqlite_locked")),
        "business_retry_attempts": summary["business_retry_attempts"], "unavailable_counters": counters(pr["counter_limits"]),
        "resources": resources(summary),
        "generator_observer": {"start_utc": obs["started_utc"], "end_utc": obs["finished_utc"], "interval_seconds": obs["interval_seconds"], "samples_by_role": scalar(obs["samples"], ("target", "scheduler", "controller")), "errors": len(obs["errors"]), "identity_failures": len(obs["identity_failures"])},
        "scheduler_gc": {"collections_during_scope": gc["collections_during_scope"], "initial_enabled": gc["initial_gc"]["enabled"], "restored_enabled": gc["restored_gc"]["enabled"], "scope_seconds": (gc["scope_finished_ns"] - gc["scope_started_ns"]) / 1e9},
        "correctness": {"durable_oracle_passed": summary["durable_oracle"]["passed"], "recovery_oracle_passed": recovery["oracle"]["passed"], "normal_native_drain": True, "supervision_worker_exit_code": supervision["worker_exit_code"], "live_owned_processes_after_cleanup_count": len(supervision["live_owned_processes_after_cleanup"]), "journal_rows": journal["rows"], "journal_sha256": journal["sha256"], "journal_sealed": journal["sealed"], **persisted},
        "recovery": {**phase_times(recovery), "operations": len(recovery["operations"]), "successful": sum(o["status"] == "ok" for o in recovery["operations"])},
        "idle": phase_times(summary["phases"]["idle"]),
        "maximum_dispatch_lag_ns": None, "full_row_noise_reader_checked": False,
    }
    return row


def project_group(base, noise_path, provider):
    pins = PINS[provider]
    controller, _ = read_json(base / "controller.json", "controller", provider, expected=pins["controller"])
    selection, _ = read_json(base / "selection.json", "selection", provider, expected=pins["selection"])
    noise, _ = read_json(noise_path, "noise", provider, expected=pins["noise"])
    check(controller["state"] == "completed" and len(controller["cells"]) == pins["cells"])
    check(controller["script_sha256"] == SOURCE_PINS["controller"])
    check(selection["controller_sha256"] == pins["controller"] and selection["highest_consistently_passing_rate"] == pins["rate"])
    check(selection["long_rate"] == selection["paired_long_rate_already_frozen"] == pins["long_rate"] and selection["fixed_long_rate_within_confirmed_capacity"])
    for obj in (controller, selection, noise):
        for field, pin in (("database_amendment_sha256", "database_amendment"), ("policy_sha256", "original_policy"), ("scheduler_gc_policy_sha256", "scheduler_gc_policy"), ("resource_sampling_policy_sha256", "resource_sampling_policy")):
            check(obj[field] == SOURCE_PINS[pin])
    check(noise["provider"] == provider and noise["rate"] == pins["rate"] and noise["concurrency"] == 16)
    check(len(noise["inputs_sha256"]) == 59 and len(noise["processes"]) == 3)
    for filename, key in (("database_observer_calibrate.py", "controller"), ("database_freeze_observer_noise.py", "noise_extractor"), ("database_compare.py", "comparison_reader")):
        check([v for k, v in noise["inputs_sha256"].items() if Path(k).name == filename] == [SOURCE_PINS[key]])
    cells = [project_cell(c, base, provider) for c in controller["cells"]]
    for i, p in enumerate(noise["processes"]):
        cell = cells[-3 + i]
        check(cell["phase"] == "confirmation" and cell["confirmation_index"] == i and cell["requested_seconds"] == 60)
        check(p["eligible"] and p["recorded_valid"] and p["service_standard_met"] and not p["invalid_reasons"] and not p["raw_invalid_reasons"])
        check(p["scopes"]["whole"]["successful"] == cell["successful"] and p["scopes"]["whole"]["p99_ns"] == cell["latency_ns"]["p99_ns"])
        check(p["observation_seconds"] == cell["timing"]["observation_seconds"] and p["durable_measurement_commits"] == cell["by_kind"]["cycle"]["successful"])
        check(noise["inputs_sha256"][str(Path(controller["cells"][-3 + i]["directory"]) / "summary.json")] == cell["summary_sha256"])
        cell["maximum_dispatch_lag_ns"] = p["maximum_dispatch_lag_ns"]
        cell["full_row_noise_reader_checked"] = True
        cell["mean_arrival_ns"] = {name: p["scopes"][original]["mean_ns"] for name, original in (("mixed", "whole"), ("cycle", "cycle"), ("page", "page"))}
    bands = {}
    for name in ("mixed", "cycle", "page"):
        means = noise["process_means_ns"][name]
        check(len(means) == 3)
        check(means == [c["mean_arrival_ns"][name] for c in cells[-3:]])
        check(math.isclose(noise["bands"][name]["absolute_noise_ns"], max(1000, max(means) - min(means)), rel_tol=1e-12))
        check(noise["bands"][name]["relative_noise"] == 0)
        bands[name] = {"process_means_ns": means, "absolute_noise_ns": noise["bands"][name]["absolute_noise_ns"], "relative_noise": 0}
    return {"provider": provider, "controller_sha256": pins["controller"], "selection_sha256": pins["selection"], "noise_sha256": pins["noise"], "highest_consistently_passing_rate": pins["rate"], "first_failing_service_bracket_rate": selection["first_failing_bracket_rate"], "unchanged_paired_long_rate": pins["long_rate"], "concurrency": 16, "noise_created_utc": noise["created_utc"], "noise_input_pin_count": len(noise["inputs_sha256"]), "noise_process_count": 3, "noise_bands": bands, "cells": cells}


ENUMS = {"Perf-01", "before", "postgresql", "sqlite", "application", "server", "controller", "selection", "noise", "summary", "progress", "frozen_inputs", "perf01_receipt", "scheduler_gc_receipt", "supervision_receipt", "calibration_execution", "noise_execution", "confirmation", "ladder", "refine", "qualified", "service_standard_failed", "generator_invalid", "generator_inflight_saturation", "deferred", "threaded", "calibration-completed-noise-pending", "completed", "before_calibration", "metadata_projection", "source_bound_no_raw_replay", "completed-invalid", "progress_state_assumption_corrected"}


def public_only(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            check(re.fullmatch(r"[a-z][a-z0-9_]*", k) is not None)
            public_only(v)
    elif isinstance(obj, list):
        for item in obj:
            public_only(item)
    elif isinstance(obj, str):
        check(obj in ENUMS or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", obj) is not None or re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)", obj) is not None)
    else:
        check(obj is None or type(obj) in (int, float, bool))
        if type(obj) is float:
            check(math.isfinite(obj))


def write_exclusive(path, obj):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(obj, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--postgresql", type=Path, required=True)
    parser.add_argument("--sqlite", type=Path, required=True)
    parser.add_argument("--noise", type=Path, required=True)
    parser.add_argument("--calibration-execution", type=Path, required=True)
    parser.add_argument("--noise-execution", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    check(os.sched_getaffinity(0) == {8})
    check(args.output.is_dir())
    check(not (args.output / "public-summary.json").exists() and not (args.output / "projection-execution.json").exists())
    calibration, _ = read_json(args.calibration_execution, "calibration_execution", expected=PINS["calibration_execution"])
    noise_execution, _ = read_json(args.noise_execution, "noise_execution", expected=PINS["noise_execution"])
    check(calibration["state"] == "calibration-completed-noise-pending" and calibration["duration_credit_seconds"] == 0)
    check(noise_execution["state"] == "completed" and not noise_execution["load_executed"] and noise_execution["duration_credit_seconds"] == 0)
    check(len(calibration["commands"]) == len(noise_execution["commands"]) == 2)
    runs = []
    for i, provider in enumerate(("postgresql", "sqlite")):
        c = calibration["commands"][i]
        n = noise_execution["commands"][i]
        check(c["exit_code"] == 0 and c["selection_gate_passed"] and c["selection_sha256"] == PINS[provider]["selection"] and c["controller_sha256"] == PINS[provider]["controller"])
        check(n["provider"] == provider and n["exit_code"] == 0 and n["output_sha256"] == PINS[provider]["noise"])
        runs.append({"provider": provider, "calibration": {"start_utc": c["started_utc"], "end_utc": c["ended_utc"], "elapsed_seconds": c["elapsed_seconds"], "exit_code": c["exit_code"], "selection_gate_passed": c["selection_gate_passed"]}, "noise_extraction": {"start_utc": n["started_utc"], "end_utc": n["ended_utc"], "elapsed_seconds": n["elapsed_seconds"], "exit_code": n["exit_code"]}})
    result = {"schema_version": 1, "task": "Perf-01", "scope": "before_calibration", "variant": "before", "formal_long_credit_seconds": 0, "product_optimization_measured": False, "source_sha256": SOURCE_PINS, "loaded_sha256": {k: v[1] for k, v in LOADED.items()}, "scheduler_gc_mode": "deferred", "resource_sampling_mode": "threaded", "service_standard": {"max_p99_ms": 500, "max_generator_dispatch_lag_ms": 100, "max_app_rss_mib": 256, "max_unexpected_errors": 0}, "executions": {"calibration_start_utc": calibration["started_utc"], "calibration_end_utc": calibration["ended_utc"], "calibration_receipt_sha256": PINS["calibration_execution"], "noise_start_utc": noise_execution["started_utc"], "noise_end_utc": noise_execution["ended_utc"], "noise_receipt_sha256": PINS["noise_execution"], "groups": runs}, "groups": [project_group(args.postgresql, args.noise / "postgresql.json", "postgresql"), project_group(args.sqlite, args.noise / "sqlite.json", "sqlite")]}
    public_only(result)
    public_only(INPUTS)
    write_exclusive(args.output / "public-summary.json", result)
    receipt = {"schema_version": 1, "task": "Perf-01", "scope": "metadata_projection", "validation": "source_bound_no_raw_replay", "started_utc": started, "ended_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "cpu_affinity": sorted(os.sched_getaffinity(0)), "projector_source_sha256": digest(Path(__file__).read_bytes()), "public_summary_sha256": digest((args.output / "public-summary.json").read_bytes()), "consistency_and_public_type_checks": CHECKS, "load_executed": False, "raw_replayed": False, "formal_long_credit_seconds": 0, "input_files": INPUTS, "prior_projection_attempts": [{"projector_source_sha256": "8acfbb103d4e1a47dac4b4c369ec95a47e364d291fd1dc8f96f78d910245ebae", "exit_code": 1, "failed_check": 630, "reason": "progress_state_assumption_corrected", "load_executed": False, "output_written": False}], "exit_code": 0}
    public_only(receipt)
    write_exclusive(args.output / "projection-execution.json", receipt)
    print(json.dumps({"exit_code": 0, "cells": 24, "noise_processes": 6, "public_summary_sha256": receipt["public_summary_sha256"], "checks": receipt["consistency_and_public_type_checks"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
