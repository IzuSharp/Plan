#!/usr/bin/env python3
"""Portable numerical projection of the two accepted before DB long cells.

No benchmark is run. Only hash-bound small JSON and optional resource JSONL are
read. Operation/event journals are not replayed; their completed frozen verifier
is the source of full-row correctness and duration claims. Run under timing.lock.
"""
import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys

ROLES = ("application", "target", "scheduler", "controller")
PHASES = {"startup": "startup-and-seed", "measurement": "measurement", "reconciliation": "reconciliation-and-shutdown", "recovery": "post-load-recovery", "idle": "post-load-idle", "finalization": "final-reconciliation-and-shutdown"}
POLICY = {"scheduler_gc": "a2fa36f9ef4a05d7d56d05dc7d8dcd6f881e3849285907ed1d132b32b9fe9cb7", "resource_sampling": "19d72617af9acb329148dbae9f6e0419e79013f7d9381998957b310eec008826", "amendment": "69e5e4733830f0efcb1181a024e70099ef0ab12117af1fc4ce72e1e61499110f", "observer_verifier": "a8f39b4409d63343edcbcad1c8745c02e742d5da168d86460a2b23b3a784881e", "original_verifier": "3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82", "adopted_policy": "98f8e537d87cac9de87cb2d1ae1150465a5c9a052333451f0772398b58ad58c3"}
LOADED = {"application": ("NativeWeave.Reference.TaskService", "6f2bd3e2b31422393d0e9543388f238226df2e3ab8f7e67c7f6b613a00e650d3"), "server": ("libnativeweave_server.so", "4827a6ecc76f871e0b4828f4ff6fe23a0d0a4ca1c57c5fc89a10a8e4d83ffe69"), "postgresql": ("libnw_database_postgresql.so", "b0510d35c2b7b633a9aade7a5d3ad9a74498b54fbe23863c770881e38442a6f3"), "sqlite": ("libnw_database_sqlite.so", "7254f8e490f19637701d92523c2ba08e0cbdfdbe4c5f28173d4215b5f303da8d")}
CONFIG = {"postgresql": (144, 259526, 6944444, 129763, 129763, 129899), "sqlite": (40, 72091, 25000000, 36046, 36045, 36182)}
COUNTERS = ("connection_pool_wait_ns", "copied_bytes", "database_execution_ns", "database_lock_wait_ns", "ffi_calls", "native_allocator_live_bytes", "sqlite_busy_handler_attempts")
INPUTS = []
CHECKS = 0


def check(value):
    global CHECKS
    CHECKS += 1
    if not value:
        raise ValueError("Bound metadata check failed: " + str(CHECKS))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path, role, expected):
    check(Path(path).stat().st_size <= 2 * 1024 * 1024)
    data = Path(path).read_bytes()
    check(sha(data) == expected)
    INPUTS.append({"role": role, "sha256": expected, "bytes": len(data)})
    return json.loads(data)


def relocate(name, cell, original):
    p = Path(name)
    if p.is_absolute():
        p = p.relative_to(Path(original))
    result = (cell / p).resolve()
    check(result.is_relative_to(cell.resolve()))
    return result


def numbers(obj, fields):
    value = {k: obj.get(k) for k in fields}
    check(all(x is None or type(x) in (int, float, bool) for x in value.values()))
    return value


def resources(summary):
    fields = ("samples", "cpu_samples", "cpu_seconds", "cpu_percent_one_core", "cpu_span_seconds", "rss_peak_bytes", "rss_window_overlap_peak_bytes", "rss_window_overlap_samples", "fd_peak_count", "socket_peak_count", "descriptor_scan_misses")
    result = {}
    for role in ROLES:
        phases = summary["resources"] if role == "application" else summary["generator_resources"][role]
        result[role] = {}
        for name, original in PHASES.items():
            row = phases.get(original, {})
            result[role][name] = {**numbers(row, fields), "identity_count": len(row.get("identities", [])), "errors": numbers(row.get("error_samples", {}), ("affinity", "cpu", "descriptor", "identity", "memory"))}
    return result


def resource_buckets(path, expected, fixed_role, start_ns, end_ns):
    """Constant space per 30s bucket; RSS overlap and real CPU brackets only."""
    width = 30_000_000_000
    count = math.ceil((end_ns - start_ns) / width)
    roles = (fixed_role,) if fixed_role else ROLES[1:]
    def empty():
        return {"reads": 0, "rss_samples": 0, "rss_min_bytes": None, "rss_max_bytes": None, "cpu_samples": 0, "cpu_first": None, "cpu_last": None, "cpu_identity": None, "cpu_identity_changed": False, "cpu_regressions": 0, "identity_failures": 0}
    buckets = {role: [empty() for _ in range(count)] for role in roles}
    digest = hashlib.sha256()
    rows = outside = byte_count = 0
    with path.open("rb") as stream:
        while raw := stream.readline(262145):
            check(len(raw) <= 262144)
            digest.update(raw)
            byte_count += len(raw)
            if not raw.strip():
                continue
            row = json.loads(raw)
            rows += 1
            role = fixed_role or row["role"]
            check(role in roles)
            lo, hi = row.get("time_ns"), row.get("finished_ns")
            check(type(lo) is int and type(hi) is int and hi >= lo)
            if hi < start_ns or lo >= end_ns:
                outside += 1
                continue
            first = max(0, (max(lo, start_ns) - start_ns) // width)
            last = min(count - 1, (min(hi, end_ns) - start_ns) // width)
            rss = row.get("counters", {}).get("rss_bytes", {}).get("value")
            for index in range(first, last + 1):
                b = buckets[role][index]
                b["reads"] += 1
                b["identity_failures"] += row.get("identity_matches") is False
                if type(rss) is int:
                    b["rss_samples"] += 1
                    b["rss_min_bytes"] = rss if b["rss_min_bytes"] is None else min(rss, b["rss_min_bytes"])
                    b["rss_max_bytes"] = rss if b["rss_max_bytes"] is None else max(rss, b["rss_max_bytes"])
            observed, ticks, frequency = row.get("cpu_observed_ns"), row.get("cpu_ticks"), row.get("clock_ticks_per_second")
            identity = (row.get("pid"), row.get("start_ticks"), frequency)
            if (type(observed) is int and start_ns <= observed < end_ns and type(ticks) is int and type(frequency) is int and frequency > 0 and row.get("identity_matches") is True and all(type(x) is int for x in identity)):
                b = buckets[role][min(count - 1, (observed - start_ns) // width)]
                b["cpu_samples"] += 1
                point = (observed, ticks, frequency)
                if b["cpu_first"] is None:
                    b["cpu_first"] = point
                    b["cpu_identity"] = identity
                else:
                    b["cpu_identity_changed"] |= b["cpu_identity"] != identity
                    b["cpu_regressions"] += observed < b["cpu_last"][0] or ticks < b["cpu_last"][1]
                b["cpu_last"] = point
    check(digest.hexdigest() == expected)
    INPUTS.append({"role": "application_resources" if fixed_role else "generator_resources", "sha256": expected, "bytes": byte_count})
    projected = {}
    for role, cells in buckets.items():
        projected[role] = []
        for index, b in enumerate(cells):
            first, last = b.pop("cpu_first"), b.pop("cpu_last")
            b.pop("cpu_identity")
            seconds = span = None
            if b["cpu_samples"] >= 2 and not b["cpu_identity_changed"] and not b["cpu_regressions"] and last[0] > first[0]:
                seconds = (last[1] - first[1]) / first[2]
                span = (last[0] - first[0]) / 1e9
            projected[role].append({"index": index, "start_offset_seconds": index * 30, "end_offset_seconds": min((index + 1) * 30, (end_ns - start_ns) / 1e9), **b, "cpu_seconds": seconds, "cpu_span_seconds": span})
    return {"scope": "target_load_window", "width_seconds": 30, "source_sha256": expected, "source_rows": rows, "rows_outside_window": outside, "roles": projected}


def safe(value):
    enums = {"Perf-01", "postgresql", "sqlite", "before", "accepted", "failed", "completed", "deferred", "threaded", "target_load_window", "binding", "summary", "plan", "target", "progress", "frozen_inputs", "perf01_receipt", "scheduler_gc_receipt", "supervision_receipt", "original_execution", "original_verification", "verification", "reverification_execution", "application_resources", "generator_resources", "duration_field_interpretation", "metadata_and_resource_projection"}
    if isinstance(value, dict):
        for key, item in value.items():
            check(re.fullmatch(r"[a-z][a-z0-9_]*", key) is not None)
            safe(item)
    elif isinstance(value, list):
        for item in value:
            safe(item)
    elif isinstance(value, str):
        check(value in enums or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value) is not None or re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)", value) is not None)
    else:
        check(value is None or type(value) in (int, float, bool))
        if type(value) is float:
            check(math.isfinite(value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("cell", "execution", "verification", "binding", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--original-verification", type=Path)
    parser.add_argument("--reverification-execution", type=Path)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--binding-sha256", required=True)
    parser.add_argument("--resource-buckets", action="store_true")
    args = parser.parse_args()
    check(sha(Path(__file__).read_bytes()) == args.source_sha256)
    check(os.sched_getaffinity(0) == {8})
    check(not (args.output / "public-summary.json").exists() and not (args.output / "projection-execution.json").exists())
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    binding = read_json(args.binding, "binding", args.binding_sha256)
    check(binding["status"] == "ready-for-authorized-projection")
    provider = binding["provider"]
    check(provider in CONFIG)
    rate, count, period, cycles, pages, persisted_before = CONFIG[provider]
    pins = binding["expected_sha256"]
    summary = read_json(args.cell / "summary.json", "summary", pins["summary"])
    frozen = read_json(args.cell / "frozen-inputs.json", "frozen_inputs", pins["frozen_inputs"])
    plan = read_json(args.cell / "plan.json", "plan", pins["plan"])
    target = read_json(args.cell / "target.json", "target", pins["target"])
    progress = read_json(args.cell / "progress.json", "progress", pins["progress"])
    execution = read_json(args.execution, "original_execution", pins["execution"])
    verified = read_json(args.verification, "verification", pins["verification"])
    original_root = execution["output"]
    check(verified["output_directory"] == original_root)
    check(verified["accepted"] and verified["original_verifier_accepted"] and not verified["failure_reasons"])
    contract = verified["observer_contract"]
    check(contract["passed"] and contract["scheduler_gc_restored"] and contract["threaded_observer_completed"])
    check(verified["duration_credit_seconds"] >= 1800 and verified["group"] == provider)
    for key, expected in (("long_amendment_sha256", POLICY["amendment"]), ("observer_verifier_sha256", POLICY["observer_verifier"]), ("verifier_sha256", POLICY["original_verifier"]), ("adopted_policy_sha256", POLICY["adopted_policy"])):
        check(verified[key] == expected)
    check(progress == {"state": "completed", "summary_sha256": pins["summary"]})
    history = None
    if provider == "postgresql":
        check(args.original_verification is not None and args.reverification_execution is not None)
        old = read_json(args.original_verification, "original_verification", pins["original_verification"])
        reverify = read_json(args.reverification_execution, "reverification_execution", pins["reverification_execution"])
        check(not old["accepted"] and old["original_verifier_accepted"] and old["duration_credit_seconds"] == 0)
        check(old["failure_reasons"] == ["ValueError: Actual long schedule/recovery/idle policy differs"])
        check(execution["state"] == "failed" and [c["exit_code"] for c in execution["commands"]] == [0, 1])
        check(reverify["exit_code"] == 0 and reverify["accepted"] and reverify["state"] == "completed")
        check(reverify["load_executed"] is False and reverify["original_records_unchanged"] is True)
        check(reverify["verification_sha256"] == pins["verification"] and reverify["source_sha256"] == POLICY["observer_verifier"] and reverify["amendment_sha256"] == POLICY["amendment"])
        check(reverify["duration_credit_seconds"] == verified["duration_credit_seconds"])
        history = {"accepted": False, "duration_credit_seconds": 0, "driver_exit_code": 0, "wrapper_exit_code": 1, "failure": "duration_field_interpretation", "verification_sha256": pins["original_verification"], "execution_sha256": pins["execution"], "reverification_execution_sha256": pins["reverification_execution"], "reverification_exit_code": reverify["exit_code"], "reverification_started_utc": reverify["started_utc"], "reverification_ended_utc": reverify["ended_utc"], "reverification_elapsed_seconds": reverify["elapsed_seconds"], "load_rerun": False, "original_records_unchanged": True}
        acceptance_end = reverify["ended_utc"]
    else:
        check(args.original_verification is None and args.reverification_execution is None)
        check(execution["state"] == "completed" and execution["accepted"] and [c["exit_code"] for c in execution["commands"]] == [0, 0])
        check(execution["verification_sha256"] == pins["verification"] and execution["amendment_sha256"] == POLICY["amendment"])
        check(execution["long_duration_credit_seconds"] == verified["duration_credit_seconds"])
        acceptance_end = execution["ended_utc"]
    check(summary["provider"] == provider and summary["variant"] == "before" and summary["stage"] == "soak")
    check(summary["valid"] and summary["duration_valid"] and summary["qualifies_service_standard"] and not summary["invalid_reasons"])
    check(summary["offered"] == summary["successful"] == summary["dispatched"] == count and summary["outcomes"] == {"ok": count})
    check(summary["rate"] == rate and summary["concurrency"] == 16)
    check(plan["timing"] == {"cleanup_timeout_ns": 180000000000, "max_dispatch_lag_ns": 100000000, "max_in_flight": 512, "period_ns": period, "requests": count, "timeout_ns": 30000000000})
    planned = (count - 1) * period / 1e9
    check(planned == frozen["planned_load_seconds"] == summary["planned_load_seconds"])
    check(target["profile"]["warmup"] == 16 and target["perf01"]["recovery_requests"] == 32 and target["perf01"]["idle_seconds"] == 60)
    check(frozen["driver_source"]["commit"] == "a3ce0f6295c535b0a81de95fc0f98aa19deb259c" and frozen["route"]["source"]["commit"] == "ea5fa528035d025bd7a28698ee7c71194432236c")
    check(summary["frozen_inputs_sha256"] == pins["frozen_inputs"] and frozen["plan_sha256"] == pins["plan"])
    check(frozen["service_standard"] == {"max_app_rss_mib": 256.0, "max_generator_dispatch_lag_ms": 100, "max_p99_ms": 500.0, "max_unexpected_errors": 0})
    for key in ("scheduler_gc", "resource_sampling"):
        check(summary[key + "_policy_sha256"] == frozen[key + "_policy_sha256"] == POLICY[key])
    loaded = {k: v for k, v in LOADED.items() if provider == "postgresql" or k != "postgresql"}
    check({Path(k).name: v["sha256"] for k, v in summary["loaded_files"].items()} == {v[0]: v[1] for v in loaded.values()})
    perf = read_json(relocate(summary["perf01_receipt"]["path"], args.cell, original_root), "perf01_receipt", pins["perf01_receipt"])
    gc = read_json(relocate(summary["scheduler_gc_receipt"]["path"], args.cell, original_root), "scheduler_gc_receipt", pins["scheduler_gc_receipt"])
    supervision = read_json(args.cell / "supervision/receipt.json", "supervision_receipt", pins["supervision_receipt"])
    check(perf["status"] == "passed" and summary["durable_oracle"]["passed"] and not summary["permanent_integrity_halt"])
    check(not summary["classified_error_counts"] and summary["business_retry_attempts"] == 0)
    check(summary["provider_errors"]["availability"] == "measured" and summary["provider_errors"]["observed_exceptions"] == 0 and not summary["provider_errors"]["provider_code_counts"])
    check(summary["provider_errors"]["sqlite_busy"] == summary["provider_errors"]["sqlite_locked"] == (0 if provider == "sqlite" else None))
    check(all(perf["counter_limits"][k] == {"availability": "unavailable", "value": None} for k in COUNTERS))
    check(gc["status"] == "completed" and gc["worker_exit_code"] == 0 and gc["collections_during_scope"] == [0, 0, 0])
    check(gc["policy_sha256"] == POLICY["scheduler_gc"] and gc["plan_sha256"] == pins["plan"] and summary["scheduler_gc_policy_valid"])
    check(gc["restored_gc"]["enabled"] == gc["initial_gc"]["enabled"] and gc["scope_entry_gc"]["enabled"] is False)
    check(supervision["status"] == "completed" and supervision["worker_exit_code"] == 0 and not supervision["live_owned_processes_after_cleanup"] and not supervision["signals"] and not supervision["registry_errors"] and supervision["failure"] is None)
    check(summary["closed"] == {"consumerResourcesReleased": True, "consumerStatus": "Succeeded", "databaseResourcesReleased": True, "databaseStatus": "Succeeded", "serverState": "Disposed"})
    journal = perf["outcome_journal"]
    check(journal["status"] == "completed" and journal["closed"] and journal["sealed"] and journal["published"] and journal["error"] is None and journal["rows"] == count + 16)
    observer = summary["generator_resource_observer"]
    check(observer["status"] == "completed" and not observer["errors"] and not observer["identity_failures"])
    check(observer["resource_sampling_policy"]["mode"] == "threaded")
    persisted = {}
    for name, expected in (("persisted_before_recovery", persisted_before), ("persisted_before_shutdown", persisted_before + 32)):
        x = summary[name]
        check(x["availability"] == "measured" and all(x["persisted_rows"][k] == expected for k in ("items", "operations", "outbox")))
        persisted[name] = {"utc": x["utc"], "rows_per_table": expected, "commits_by_phase": numbers(x["committed_operations_by_phase"], ("seed", "warmup", "measurement", "recovery"))}
    recovery, idle, load = (summary["phases"][k] for k in ("recovery", "idle", "load"))
    check(len(recovery["operations"]) == 32 and all(x["status"] == "ok" for x in recovery["operations"]) and recovery["oracle"]["passed"])
    check(idle["end_ns"] - idle["start_ns"] >= 60_000_000_000)
    by_kind = {}
    for name, expected in (("cycle", cycles), ("list", pages)):
        row = summary["by_kind"][name]
        check(row["offered"] == row["successful"] == expected and row["outcomes"] == {"ok": expected})
        by_kind[name] = numbers(row, ("offered", "successful", "p50_ns", "p95_ns", "p99_ns"))
    proof = verified["duration_proof"]
    check(proof["duration_proved"] and proof["arrival_p99_at_most_500ms_from_raw"] and proof["ordinary_successes"] == proof["successful_logical_checks"] == count and proof["expected_probe_successes"] == 0)
    check(proof["ordinary_operation_lower_bound_ns"] / 1e9 == verified["duration_credit_seconds"] and proof["maximum_dispatch_start_lag_ns"] <= 100_000_000)
    check(verified["driver_arrival_p99_ns"] == summary["p99_ns"] <= 500_000_000)
    check(verified["resources"]["rss_peak_bytes"] <= verified["application_rss_limit_bytes"] == 268435456)
    result = {"schema_version": 1, "task": "Perf-01", "provider": provider, "variant": "before", "acceptance": "accepted", "duration_credit_seconds": verified["duration_credit_seconds"], "product_gain_measured": False,
        "summary_sha256": pins["summary"], "verification_sha256": pins["verification"], "policy_sha256": POLICY, "loaded_sha256": {k: v[1] for k, v in loaded.items()}, "driver_commit": frozen["driver_source"]["commit"], "product_commit": frozen["route"]["source"]["commit"], "dataset_sha256": frozen["dataset_sha256"], "observer_verified_input_count": len(contract["inputs_sha256"]),
        "load": {"rate_per_second": rate, "concurrency": 16, "warmup": 16, "recovery": 32, "idle_seconds": 60, "requested_seconds": 1802, "planned_seconds": planned, "max_dispatch_lag_ns": 100000000, "max_arrival_p99_ns": 500000000, "max_application_rss_bytes": 268435456},
        "outcomes": {"offered": count, "dispatched": count, "successful": count, "errors": 0, "timeouts": 0, "cancellations": 0, "rejections": 0}, "successful_per_second": summary["successful_per_second"], "latency_ns": numbers(summary, ("p50_ns", "p95_ns", "p99_ns")), "by_kind": by_kind,
        "timing": {**numbers(summary, ("actual_dispatch_span_seconds", "observation_seconds")), "target_load_start_utc": load["start_utc"], "target_load_end_utc": load["last_completion_utc"], "target_load_span_seconds": (load["last_completion_ns"] - load["first_dispatch_ns"]) / 1e9, "supervised_execution_started_utc": execution["started_utc"], "supervised_execution_ended_utc": execution["ended_utc"], "acceptance_completed_utc": acceptance_end, "duration_proof": numbers(proof, ("ordinary_operation_lower_bound_ns", "ipc_send_lower_bound_ns", "scheduled_span_ns", "maximum_dispatch_start_lag_ns", "dispatch_start_lag_over_50ms_count", "ordinary_successes", "expected_probe_successes", "successful_logical_checks"))},
        "resources": resources(summary), "persisted": persisted, "recovery": {"successful": 32, "oracle_passed": True, "start_utc": recovery["start_utc"], "end_utc": recovery["end_utc"], "seconds": (recovery["end_ns"] - recovery["start_ns"]) / 1e9}, "idle": {"start_utc": idle["start_utc"], "end_utc": idle["end_utc"], "seconds": (idle["end_ns"] - idle["start_ns"]) / 1e9, "application_rss_before_bytes": idle["before"]["counters"]["rss_bytes"]["value"], "application_rss_after_bytes": idle["after"]["counters"]["rss_bytes"]["value"]},
        "correctness": {"full_row_verifier_passed": True, "logical_checks": count, "durable_oracle_passed": True, "outcome_journal_rows_warmup_plus_measured": journal["rows"], "outcome_journal_sha256": journal["sha256"], "outcome_journal_closed_and_sealed": True, "normal_resource_release": True, "supervision_worker_exit_code": 0, "live_owned_after_cleanup": 0, "forced_signals": 0},
        "provider_observations": {"surfaced_exceptions": 0, "business_retry_attempts": 0, "sqlite_busy": summary["provider_errors"]["sqlite_busy"], "sqlite_locked": summary["provider_errors"]["sqlite_locked"], "internal_busy_handler_attempts": None},
        "unavailable": {**{k: None for k in COUNTERS}, "managed_allocation_bytes": None, "managed_gc_collections": None, "separate_database_server_cpu_seconds": None, "post_restore_generator_rss_bytes": None},
        "scheduler_gc": {"mode": "deferred", "collections_during_scope": gc["collections_during_scope"], "initial_enabled": gc["initial_gc"]["enabled"], "restored_enabled": gc["restored_gc"]["enabled"], "scope_seconds": (gc["scope_finished_ns"] - gc["scope_started_ns"]) / 1e9, "scope_end_after_target_start_seconds": (gc["scope_finished_ns"] - load["first_dispatch_ns"]) / 1e9},
        "resource_observer": {"mode": "threaded", "completed": True, "interval_seconds": observer["interval_seconds"], "samples": numbers(observer["samples"], ("target", "scheduler", "controller")), "started_utc": observer["started_utc"], "finished_utc": observer["finished_utc"], "errors": 0, "identity_failures": 0}, "original_history": history}
    if args.resource_buckets:
        app = [(k, v) for k, v in verified["evidence_sha256"].items() if k.endswith("/application/resources.jsonl")]
        gen = [(k, v) for k, v in contract["inputs_sha256"].items() if k.endswith("/generator-resources.jsonl")]
        check(len(app) == len(gen) == 1 and gen[0][1] == observer["sha256"])
        result["resource_buckets"] = {}
        for key, pair, role in (("application", app[0], "application"), ("generator", gen[0], None)):
            result["resource_buckets"][key] = resource_buckets(relocate(pair[0], args.cell, original_root), pair[1], role, load["first_dispatch_ns"], load["last_completion_ns"])
    safe(result)
    safe(INPUTS)
    args.output.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    receipt = {"schema_version": 1, "task": "Perf-01", "scope": "metadata_and_resource_projection", "started_utc": started, "ended_utc": dt.datetime.now(dt.timezone.utc).isoformat(), "cpu_affinity": sorted(os.sched_getaffinity(0)), "projector_sha256": args.source_sha256, "binding_sha256": args.binding_sha256, "public_summary_sha256": sha(encoded), "checks": CHECKS, "input_files": INPUTS, "resource_journals_streamed": args.resource_buckets, "operation_journals_replayed": False, "load_executed": False, "exit_code": 0}
    safe(receipt)
    with (args.output / "public-summary.json").open("xb") as stream:
        stream.write(encoded)
    with (args.output / "projection-execution.json").open("x") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"exit_code": 0, "public_summary_sha256": receipt["public_summary_sha256"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
