"""Offline, allowlisted numerical projection of the accepted codec before attempt002.

Reuse the pinned codec comparator's complete raw-row reconciliation. Never copy
its process identities, paths, controls, arbitrary text or entire event objects.
This is reporting of an existing acceptance, not a workload or a new verifier.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import sys
import time

sys.dont_write_bytecode = True
BASELINE = "ea5fa528035d025bd7a28698ee7c71194432236c"
PINS = {
    "codec_compare.py": "6f09ac17bc60544ef97c147a47cada66344f6ea068318821f204da0a6e468663",
    "codec-before004-r241-long-commands.json": "cd7c7eafe989b1b3aada00d6cf5ab7732f331a75ddde3618844b82b05e0711e7",
    "frozen-execution.json": "85061c4e01b28fc72a5b20519ce2d8c01d79cae271238ba36e0a3465b0b8f4a3",
    "codec-before-resume-002.json": "225c9295a102de22a59e2bea01f2bb3f3abecbea98313f5b7c157322916a9e12",
    "run_codec_before_resume_002.py": "dac0016659b6352bb0e2c93c80fb8ad276507c113a635a72b3250c12cb01f131",
}
PHASES = ("warmup", "measurement", "recovery")
COUNT_KEYS = ("planned", "sent", "dispatch_attempted", "admitted", "completed", "ok")
OUTCOMES = ("ok", "failed", "timeout", "rejected", "generator_capacity", "interrupted")
METRICS = ("call_ns", "arrival_ns", "consume_ns", "release_ns", "operation_ns", "dispatch_lag_ns", "dispatch_to_admission_ns")
COUNTERS = ("managed_allocated_bytes", "managed_allocated_bytes_including_validation", "copied_bytes_derived", "ffi_calls_derived")
BUCKET_SECONDS = 30
PROCESS_COLUMNS = ("bucket_start_seconds", "sample_count", "first_sample_seconds", "last_sample_seconds",
                   "rss_first_bytes", "rss_last_bytes", "rss_peak_bytes", "cpu_percent_one_core",
                   "threads_peak", "open_file_descriptors_peak")
TELEMETRY_COLUMNS = ("bucket_start_seconds", "sample_count", "first_sample_seconds", "last_sample_seconds",
                     "managed_allocated_bytes_delta", "gc0_delta", "gc1_delta", "gc2_delta", "gc_heap_peak_bytes",
                     "gc_committed_peak_bytes", "native_live_peak", "native_capacity_peak_bytes", "native_active_peak",
                     "native_released_delta")
STRINGS = {"Perf-01", "codec", "before", "nativeweave", "compress", "decompress", "array", "owned",
           "compressible", "pseudorandom", "zlib", "Adler32", "accepted", "whole-process",
           "controller-event-observation", "derived-output-payload-only", "codec-and-result-free-only",
           "sample-bracket", "measurement", "post-drain", *PROCESS_COLUMNS, *TELEMETRY_COLUMNS}


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def number(value, *, optional=False):
    if optional and value is None:
        return None
    need(type(value) in (int, float) and math.isfinite(value) and value >= 0, "Invalid numerical source value")
    return value


def read(path):
    with Path(path).open("rb") as stream:
        raw = stream.read(2 * 1024 * 1024 + 1)
    need(len(raw) <= 2 * 1024 * 1024, "Oversized control input")
    return json.loads(raw)


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def same(left, right):
    if left is None or right is None:
        return left is right
    return math.isclose(left, right, rel_tol=1e-12, abs_tol=1e-9)


def public(value):
    """All values are scalars, fixed enums, reviewed hashes or their containers."""
    if value is None or type(value) is bool:
        return
    if type(value) in (int, float):
        need(math.isfinite(value), "Nonfinite public value")
        return
    if type(value) is str:
        need(value in STRINGS or re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value), "Unapproved public string")
        return
    if type(value) is list:
        for child in value:
            public(child)
        return
    need(type(value) is dict, "Unsupported public value")
    for key, child in value.items():
        need(type(key) is str and re.fullmatch(r"[a-z][a-z0-9_]*", key), "Unapproved public key")
        public(child)


def fresh_write(path, content):
    with path.open("xb") as stream:
        stream.write(content); stream.flush(); os.fsync(stream.fileno())


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def process_metrics(rows, origin):
    need(rows, "Missing process observations")
    times = [row["t"] for row in rows]
    rss = [(row["t"], row["rss"]) for row in rows if row["rss"] is not None]
    cpu = [(row["t"], row["cpu"]) for row in rows if row["cpu"] is not None]
    need(all(a[1] <= b[1] for a, b in zip(cpu, cpu[1:])), "CPU counter decreased")
    seconds = (cpu[-1][0] - cpu[0][0]) / 1e9 if len(cpu) > 1 else None
    delta = cpu[-1][1] - cpu[0][1] if seconds else None
    result = {"sample_count": len(rows), "first_sample_seconds": (times[0] - origin) / 1e9,
              "last_sample_seconds": (times[-1] - origin) / 1e9, "rss_sample_count": len(rss),
              "rss_first_bytes": rss[0][1] if rss else None, "rss_last_bytes": rss[-1][1] if rss else None,
              "rss_peak_bytes": max((v for _, v in rss), default=None), "cpu_sample_count": len(cpu),
              "cpu_observation_seconds": seconds, "cpu_seconds": delta,
              "cpu_percent_one_core": delta / seconds * 100 if seconds else None}
    for field in ("threads", "open_file_descriptors"):
        values = [row[field] for row in rows if row[field] is not None]
        result[field + "_peak"] = max(values, default=None)
    return result


def telemetry_metrics(rows, origin):
    need(rows, "Missing managed/native observations")
    result = {"sample_count": len(rows), "first_sample_seconds": (rows[0]["t"] - origin) / 1e9,
              "last_sample_seconds": (rows[-1]["t"] - origin) / 1e9,
              "observation_seconds": (rows[-1]["t"] - rows[0]["t"]) / 1e9}
    for source, target in (("managed_allocated_bytes_total", "managed_allocated_bytes"), ("gc0", "gc0"),
                           ("gc1", "gc1"), ("gc2", "gc2"), ("released", "native_released")):
        values = [row[source] for row in rows]
        need(all(a <= b for a, b in zip(values, values[1:])), "Managed/native cumulative counter decreased")
        result[target + "_delta"] = values[-1] - values[0]
    result["managed_allocated_mib_per_second"] = (result["managed_allocated_bytes_delta"] / 1048576 /
                                                  result["observation_seconds"] if result["observation_seconds"] else None)
    for source, target in (("gc_heap_bytes", "gc_heap"), ("gc_committed_bytes", "gc_committed"),
                           ("live", "native_live"), ("capacity", "native_capacity"), ("active", "native_active")):
        unit = "_bytes" if source in ("gc_heap_bytes", "gc_committed_bytes", "capacity") else ""
        result[target + "_peak" + unit] = max(row[source] for row in rows)
        result[target + "_last" + unit] = rows[-1][source]
    result["errors_maximum"] = max(row["errors"] for row in rows)
    return result


def series(rows, phase_origin, report_origin, calculate, columns):
    buckets = defaultdict(list)
    for row in rows:
        buckets[(row["t"] - phase_origin) // (BUCKET_SECONDS * 1_000_000_000)].append(row)
    output = []
    for index, values in sorted(buckets.items()):
        result = calculate(values, report_origin)
        result["bucket_start_seconds"] = (phase_origin - report_origin) / 1e9 + index * BUCKET_SECONDS
        output.append([result[column] for column in columns])
    return output


def run(args):
    started = time.monotonic()
    root, repository, output = args.root.resolve(), args.plan_root.resolve(), args.output.resolve()
    raw = root / "perf01-evidence/long/before/codec-002"
    perf = repository / "ledger/evidence/batches/Perf-01"
    need(output != raw and raw not in output.parents, "Never write into original evidence")
    output.mkdir(parents=True, exist_ok=True)
    for name in ("summary.json", "README.md", "manifest.json"):
        need(not os.path.lexists(output / name), "Use fresh projection output files")
    inputs = {name: perf / name for name in PINS}
    for name, expected in PINS.items():
        need(sha(inputs[name]) == expected, "Reporting dependency changed: " + name)
    original, resume = read(inputs["codec-before004-r241-long-commands.json"]), read(inputs["codec-before-resume-002.json"])
    for table in ("required_source_and_metadata_sha256", "required_final_selection_sha256"):
        for path, expected in original[table].items():
            need(sha(path) == expected, "Original source/selection pin changed")
    execution_path = root / "perf01-run/before-codec-long-002-execution.json"
    verification_path = raw.with_name("codec-002-verification.json")
    execution, verification = read(execution_path), read(verification_path)
    need(execution["state"] == "completed" and execution["accepted"] is True and execution["domain_verifier_accepted"] is True,
         "No completed accepted supervisor receipt")
    need(execution["attempt"] == 2 and execution["group"] == "codec" and execution["variant"] == "before", "Wrong attempt identity")
    need(execution["output"] == str(raw) and execution["verification_receipt"] == str(verification_path), "Wrong actual evidence paths")
    need(execution["document_sha256"] == PINS["codec-before-resume-002.json"] and execution["freeze_sha256"] == PINS["frozen-execution.json"]
         and execution["supervisor_source_sha256"] == PINS["run_codec_before_resume_002.py"], "Supervisor/config identity mismatch")
    need(len(execution["commands"]) == 2 and all(item["exit_code"] == 0 and item["state"] == "completed" for item in execution["commands"]),
         "Both actual command exits must be zero")
    need([item["argv"] for item in execution["commands"]] == [item["argv"] for item in resume["commands"]], "Executed argv differs from reviewed attempt")
    need(sha(verification_path) == execution["verification_sha256"], "Verification receipt changed")
    need(verification["accepted"] is True and not verification["failure_reasons"] and verification["group"] == "codec"
         and verification["output_directory"] == str(raw), "Independent long verification did not accept this cell")
    need(verification["verifier_sha256"] == original["post_run_verifier"]["sha256"]
         and sha(original["post_run_verifier"]["path"]) == verification["verifier_sha256"], "Verifier source mismatch")
    need(same(execution["long_duration_credit_seconds"], verification["duration_credit_seconds"])
         and verification["duration_credit_seconds"] >= 1800, "Missing actual long credit")
    plan, result, saved = (read(raw / name) for name in ("plan.json", "result.json", "summary.json"))
    build_path, corpus_path = root / "perf01-codec-checks/package-before-004/manifest.json", root / "perf01-codec-checks/corpus/manifest.json"
    build, corpus = read(build_path), read(corpus_path)
    need(plan["source_commit"] == build["source_commit"] == BASELINE, "Before product identity changed")
    need(plan["planned_rate"] == 192 and plan["workers"] == 2 and plan["duration_seconds"] == 1802, "Wrong frozen long selection")
    need(not result["invalid_reasons"], "Invalid domain result")
    a21_path = root / ".worktree/Perf-01-linux/NativeWeave/src/Benchmarks.Harness/nativeweave_bench.py"
    cmp = module(inputs["codec_compare.py"], "codec_numerical_comparator")
    a21_hash = sha(a21_path)
    need(a21_hash == plan["a21_sha256"] == build["a21_sha256"], "A21 identity mismatch")
    a21 = cmp.a21_module(a21_path)
    stamp_paths = [raw / name for name in verification["evidence_sha256"]] + [execution_path, verification_path, build_path, corpus_path]
    def stamp(path):
        stat = path.stat(); return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns
    initial = {path: stamp(path) for path in stamp_paths}
    cell, groups, _, _ = cmp.cell(raw, build_path, "nativeweave", corpus, sha(corpus_path), a21, a21_hash,
                                {"arrival_p99_maximum_ns": 500_000_000, "rss_maximum_bytes": 256 * 1048576})
    for name, expected in verification["evidence_sha256"].items():
        observed = cell["summary_sha256"] if name == "summary.json" else cell["files_sha256"][name]
        need(observed == expected, "Independent verifier and raw reporting hashes differ")
    identity = verification["original_checked_identities"]
    need(all(identity[key] == plan[key] for key in ("source_commit", "route", "manifest_sha256", "controller_sha256", "a21_sha256", "corpus_manifest_sha256", "actual_loaded_native")), "Verifier/plan identity mismatch")
    seconds, origin = cell["observation_seconds"], result["scheduled_start_ns"]
    end = origin + round(seconds * 1e9)
    need(same(seconds, result["measurement_observation_seconds"]), "Wall denominator mismatch")
    phase_counts = {phase: {key: number(result["phase_counts"][phase][key]) for key in COUNT_KEYS} for phase in PHASES}
    need([phase_counts[p]["planned"] for p in PHASES] == [3861, 346005, 12], "Frozen phase counts differ")
    planned = Counter(tuple(plan["sequence"][i % len(plan["sequence"])]) for i in range(phase_counts["measurement"]["planned"]))
    rows, combined = [], {}
    for case in range(8):
        for action in "cd":
            for interface in "ao":
                key = cmp.group_key(case, action, interface)
                item, metrics, old = groups[key], cell["groups"][key], saved["groups"][key]
                need(item["count"] == planned[(case, action, interface)] and old["outcomes"] == {"ok": item["count"]}, "Partition plan/outcome mismatch")
                for metric in METRICS[:5]:
                    need(all(same(metrics["latency"][metric][q], old[metric][q]) for q in ("p50", "p95", "p99")), "Saved ownership/tail metric differs")
                for new, prior in (("successes_per_second", "successes_per_second"), ("raw_mib_per_second_wall", "raw_mib_per_second_wall"),
                                   ("raw_mib_per_second_summed_call", "raw_mib_per_second_summed_codec_time"), ("raw_over_encoded_ratio", "compression_ratio_raw_over_encoded")):
                    need(same(metrics[new], old[prior]), "Saved throughput/ratio differs")
                need(metrics["counter_totals"]["managed_allocated_bytes"] == old["managed_allocated_bytes"]
                     and metrics["counter_totals"]["copied_bytes_derived"] == old["copied_bytes_derived"], "Saved allocation/copy total differs")
                need(metrics["counter_totals"]["ffi_calls_derived"] == 2 * item["count"], "Derived codec/free call scope changed")
                expected_copy = (item["encoded"] if action == "c" else item["raw"]) if interface == "a" else 0
                need(metrics["counter_totals"]["copied_bytes_derived"] == expected_copy, "Derived output copy scope changed")
                rows.append({"case_id": case, "raw_size_bytes": corpus["cases"][case]["size"],
                             "entropy": "compressible" if case % 2 == 0 else "pseudorandom",
                             "action": "compress" if action == "c" else "decompress", "interface": "array" if interface == "a" else "owned",
                             "planned": planned[(case, action, interface)], **metrics})
                pair = (action, interface)
                cmp.merge(combined.setdefault(pair, cmp.group()), item)
    aggregate = [{"action": "compress" if action == "c" else "decompress", "interface": "array" if interface == "a" else "owned",
                  **cmp.metrics(combined[(action, interface)], seconds, a21)} for action in "cd" for interface in "ao"]
    snapshots, drains = [], []
    for event in cmp.lines(raw / "events.jsonl", saved["files"]["events.jsonl"]):
        if event.get("kind") not in ("telemetry", "snapshot", "idle", "drained"):
            continue
        row = {"t": number(event["observer_ns"])}
        for key in ("managed_allocated_bytes_total", "gc0", "gc1", "gc2", "gc_heap_bytes", "gc_committed_bytes", "errors"):
            row[key] = number(event[key])
        for key in ("live", "released", "capacity", "active"):
            row[key] = number(event["native"][key])
        snapshots.append(row)
        if event["kind"] == "drained":
            drains.append(row)
    need(len(drains) == 1, "Missing unique drained telemetry")
    drain = drains[0]
    need(all(drain[key] == 0 for key in ("live", "capacity", "active", "errors")), "Owner/error drain failed")
    samples = {role: [] for role in ("target", "generator")}
    for row in cmp.lines(raw / "resources.jsonl", saved["files"]["resources.jsonl"]):
        for role in samples:
            value = row[role]
            samples[role].append({"t": number(row["observer_ns"]), "rss": number(value["rss_bytes"]["value"], optional=True),
                                  "cpu": number(value["cpu_seconds"], optional=True), "threads": number(value["threads"]["value"], optional=True),
                                  "open_file_descriptors": number(value["open_file_descriptors"], optional=True)})
    resource = {}
    for phase, begin, finish in (("measurement", origin, end), ("post_drain", drain["t"], math.inf)):
        selected = [row for row in snapshots if begin <= row["t"] <= finish]
        managed = telemetry_metrics(selected, origin)
        need(managed["errors_maximum"] == 0, "Recorded telemetry contains target errors")
        processes, process_series = {}, {}
        for role in samples:
            data = [row for row in samples[role] if begin <= row["t"] <= finish]
            processes[role] = process_metrics(data, origin)
            process_series[role] = series(data, begin, origin, process_metrics, PROCESS_COLUMNS)
        resource[phase] = {"processes": processes, "managed_and_native": managed,
                           "process_series": process_series,
                           "managed_and_native_series": series(selected, begin, origin, telemetry_metrics, TELEMETRY_COLUMNS)}
    target = resource["measurement"]["processes"]["target"]
    need(target["rss_peak_bytes"] == verification["resources"]["rss_peak_bytes"]
         and target["rss_sample_count"] == verification["resources"]["rss_samples"], "Verifier resource reconciliation failed")
    proof = verification["duration_proof"]
    max_lag = max(max(value["latency"]["dispatch_lag_ns"]) for value in groups.values())
    lag_over_50 = sum(sum(value > 50_000_000 for value in item["latency"]["dispatch_lag_ns"]) for item in groups.values())
    need(max_lag == proof["maximum_dispatch_start_lag_ns"] and lag_over_50 == proof["dispatch_start_lag_over_50ms_count"], "Verifier lag reconciliation failed")
    packages = sorted(value for name, value in build["artifacts"].items() if name.endswith(".nupkg"))
    hashes = {name.removesuffix(".jsonl").removesuffix(".json"): value for name, value in verification["evidence_sha256"].items()}
    hashes.update(verification=sha(verification_path), execution=sha(execution_path), producer_manifest=sha(build_path), corpus_manifest=sha(corpus_path))
    report = {"schema_version": 1, "task": "Perf-01", "domain": "codec", "variant": "before", "route": "nativeweave", "attempt": 2,
              "state": "accepted", "accepted": True, "duration_credit_seconds": verification["duration_credit_seconds"],
              "identity": {"product_source_commit": plan["source_commit"], "producer_manifest_sha256": plan["manifest_sha256"],
                           "controller_sha256": plan["controller_sha256"], "a21_sha256": a21_hash,
                           "verifier_sha256": verification["verifier_sha256"], "comparator_sha256": PINS["codec_compare.py"],
                           "projection_source_sha256": sha(__file__), "corpus_manifest_sha256": plan["corpus_manifest_sha256"],
                           "actual_loaded_native_sha256": plan["actual_loaded_native"][0]["sha256"],
                           "aot_executable_sha256": build["artifacts"][build["managed_executable"]], "package_sha256": packages,
                           "frozen_execution_sha256": PINS["frozen-execution.json"], "resume_configuration_sha256": PINS["codec-before-resume-002.json"]},
              "configuration": {key: number(plan[key]) for key in ("planned_rate", "workers", "queue_capacity", "max_in_flight", "period_ns", "duration_seconds", "warmup_seconds", "recovery_seconds", "recovery_rate", "idle_seconds", "deadline_ms", "max_lag_ms", "seed")},
              "codec_limits": {key: corpus[key] for key in ("raw_limit", "encoded_limit", "decoded_limit", "level", "format", "checksum")},
              "phase_counts": phase_counts, "operation_outcomes": {key: result["operation_outcomes"].get(key, 0) for key in OUTCOMES},
              "measurement": {"offered": saved["offered"], "successes": saved["successes"], "successes_per_second": saved["successful_operations_per_second"],
                              "observation_seconds": seconds, "actual_dispatch_span_seconds": result["actual_dispatch_span_seconds"],
                              "ordinary_operation_lower_bound_ns": proof["ordinary_operation_lower_bound_ns"],
                              "original_dispatch_start_span_ns": proof["original_dispatch_start_span_ns"],
                              "arrival_ns": {q: saved["arrival_success_ns"][q] for q in ("p50", "p95", "p99")},
                              "maximum_dispatch_start_lag_ns": max_lag, "dispatch_start_lag_over_50ms_count": lag_over_50,
                              "dispatch_start_lag_over_limit_count": 0, "target_cpu_seconds_bracket": saved["target_cpu_seconds"],
                              "target_cpu_percent_one_core_bracket": saved["target_cpu_percent_one_core"],
                              "rss_bracket_before_bytes": saved["rss_before_bytes"], "rss_bracket_after_bytes": saved["rss_after_bytes"]},
              "rows": rows, "action_interface_totals": aggregate, "resources": resource,
              "resource_series": {"bucket_seconds": BUCKET_SECONDS, "process_columns": list(PROCESS_COLUMNS), "managed_and_native_columns": list(TELEMETRY_COLUMNS)},
              "drain": {"observed_seconds_after_measurement_origin": (drain["t"] - origin) / 1e9,
                        "native_live": drain["live"], "native_capacity_bytes": drain["capacity"], "native_active": drain["active"],
                        "errors": drain["errors"], "idle_observation_seconds": result["idle_observation_seconds"], "actual_target_exit_code": result["exit_code"]},
              "scope": {"resources": "whole-process", "event_clock": "controller-event-observation", "gc_allocation_interval": "sample-bracket",
                        "copied_bytes": "derived-output-payload-only", "ffi_calls": "codec-and-result-free-only", "network_compression_measured": False,
                        "native_allocator_counts": None, "upstream_workspace_peak_bytes": None, "all_internal_copy_bytes": None,
                        "per_partition_cpu": None, "gc_pause_time_ns": None, "queue_occupancy_peak": None,
                        "direct_rust_gap": None, "before_after_improvement": None},
              "checks": {"both_actual_exits_zero": True, "independent_verifier_accepted": True, "frozen_source_and_configuration_match": True,
                         "complete_raw_hashes_match": True, "all_phases_reconciled": True, "all_32_partitions_match_frozen_sequence": True,
                         "all_saved_partition_tails_throughput_counters_match": True, "bytes_and_loaded_native_identity_match": True,
                         "recovery_passed": True, "unique_normal_drain": True, "native_owners_drained": True,
                         "actual_duration_proved": True, "resource_and_service_standard_met": True, "raw_inputs_unchanged": True},
              "input_sha256": hashes}
    need(all(stamp(path) == prior for path, prior in initial.items()), "Input changed during reporting")
    public(report)
    # These exact names and values are written by this source; raw records are never serialized.
    summary_content = json_bytes(report)
    timestamp = lambda value: datetime.fromisoformat(value).astimezone(timezone.utc).isoformat()
    readme = f"""# Perf-01 codec before attempt002: accepted numerical report

This is an offline numerical projection of the existing accepted run. It adds no
load, changes no raw evidence, and grants no additional acceptance beyond the
independent verifier. The interrupted attempt001 remains separate with zero credit.

## Actual result

- Product: `{plan['source_commit']}`; actual Native AOT package consumer, Linux x64.
- Measurement first dispatch: {timestamp(result['measurement_start_utc'])}.
- Measurement last observed completion: {timestamp(result['measurement_end_utc'])}.
- Supervisor completed: {timestamp(execution['ended_utc'])}; both actual exits were zero.
- Successful measurement operations: {saved['successes']:,}/{saved['offered']:,}; warmup 3,861 and recovery 12, all successful.
- Independent ordinary-operation duration credit: {verification['duration_credit_seconds']:.9f} s.
- Actual first-to-last dispatch: {result['actual_dispatch_span_seconds']:.9f} s; observation window: {seconds:.9f} s.
- Success rate: {saved['successful_operations_per_second']:.9f}/s; arrival p99: {saved['arrival_success_ns']['p99']/1e6:.6f} ms.
- Target CPU: {saved['target_cpu_percent_one_core']:.6f}% of one core; sampled peak RSS: {target['rss_peak_bytes']/1048576:.6f} MiB.
- Normal owner drain: live/capacity/active = 0/0/0; separately observed idle: {result['idle_observation_seconds']:.9f} s.

## Fields and interpretation

`summary.json` retains all 32 payload/action/interface partitions and four pooled
action/interface summaries. The eight corpus cases cover 256 B, 4 KiB, 1 MiB and
4 MiB with compressible and fixed-seed pseudorandom input. Compression and
decompression are separate. Expected partition counts follow the frozen shuffled
160-operation cycle; they are not equal subdivisions of the total.

Wall MiB/s divides original raw bytes by the full observation window. Summed-call
MiB/s divides raw bytes by summed public codec-call time and is not concurrent
throughput. Every row is a contribution to this mixed workload, not standalone
capacity. Raw/encoded ratios are computed from byte sums, not averaged ratios.
Array call time includes copying and native result retirement. Owned call time
ends before Read/Dispose; consume/release/operation fields retain those costs.
Pooled quantiles are recomputed from actual operations using the unchanged A21
percentile function, never averaged from row percentiles.

CPU/RSS and managed/native telemetry belong to the whole mixed process. The
measurement CPU bracket also includes bounded fixture/oracle/telemetry work.
GC and total-allocation deltas use the first/last telemetry observations inside
the stated interval; their actual relative endpoints are retained. They do not
precisely cover the entire measurement. Total allocated bytes use the consumer's
`GC.GetTotalAllocatedBytes(false)` observation. Per-call allocation is measured
on the worker thread before output formatting; the including-validation counter
also includes validation/ownership work. These scopes must not be equated.

The 30-second numerical resource buckets retain first/last/peak RSS, observed CPU
intervals, thread/descriptor peaks and managed/native deltas/peaks. All original
approximately one-second samples remain in the private raw evidence. Bucket
delta sums omit gaps between observation brackets; use the whole interval delta
for totals. Post-drain observations include the drained event and subsequent idle
samples. Released owners are cumulative; live is an owner count, capacity is
result Vec capacity in bytes, active is an engine-call count. No allocator/workspace
coverage or unsampled peak guarantee is implied. RSS and GC heap need not return
to zero when all owners retire.

Output copying and FFI counts are derived only for the result payload copy and
codec/result-free pair. Native allocator counts, upstream workspace peaks, all
internal copies, per-partition CPU, GC pause time and queue occupancy are unavailable.
No network compression, before/after improvement or direct-Rust gap is claimed.
The three-process frozen-noise comparator remains a separate comparison workflow.

## Integrity and publication boundary

The pinned `codec_compare.py` reads and hashes every original operation, event and
resource line and checks the complete 32-row corpus, phases, bytes, timing,
native identity, service standard and drain. This projection additionally binds
the actual supervisor/verifier to attempt002, reconciles saved partition metrics,
and matches verifier hashes, duration, lag and RSS. The original six raw hashes,
producer/corpus, acceptance and exact source hashes remain in the numerical report.

Public output is explicitly reconstructed from finite numbers, booleans, null,
fixed enums and reviewed SHA identities. It excludes raw controls, arbitrary
strings, payload contents, command lines, process IDs, process start ticks, host
paths, environment values and ownership tokens. Relative observation times are
used in JSON; the human UTC interval is stated above. The original raw data and
receipts are unchanged and are not embedded or archived here.

## Reproduction

Run outside every measurement window, on CPU8, with the locked Python and the
original retained codec002 evidence. The program acquires the existing timing
lock nonblocking and rejects existing output files. `PERF01_ROOT`, `PLAN_CHECKOUT`
and `NEW_OUTPUT` refer to the retained workspace, this Plan checkout and a fresh
output directory; no network or workload is started.

```bash
taskset -c 8 "$LOCKED_PYTHON" -B \\
  "$PLAN_CHECKOUT/ledger/evidence/batches/Perf-01/checks/before-codec-long-002/project_numbers.py" \\
  --root "$PERF01_ROOT" --plan-root "$PLAN_CHECKOUT" --output "$NEW_OUTPUT"
```

Reproduction binds the unchanged global freeze, original codec commands, attempt002
configuration/supervisor, comparator, A21 and verifier. Input paths are resolved
locally; only their reviewed content identities are published. The manifest
records output hashes and the actual offline projection duration. It does not
pretend that an in-process completion record is a separate observed process exit.
"""
    source = Path(__file__).read_bytes()
    destination_source = output / "project_numbers.py"
    if destination_source.resolve() != Path(__file__).resolve():
        fresh_write(destination_source, source)
    fresh_write(output / "summary.json", summary_content)
    fresh_write(output / "README.md", readme.encode())
    manifest = {"schema_version": 1, "task": "Perf-01", "domain": "codec", "variant": "before", "attempt": 2,
                "projection_completed": True, "projection_cpu_affinity": [8], "projection_elapsed_seconds": time.monotonic() - started,
                "projection_source_sha256": hashlib.sha256(source).hexdigest(), "input_sha256": hashes,
                "output": {"summary": {"bytes": len(summary_content), "sha256": sha(output / "summary.json")},
                           "readme": {"bytes": len(readme.encode()), "sha256": sha(output / "README.md")},
                           "source": {"bytes": len(source), "sha256": sha(destination_source)}},
                "public_value_allowlist_passed": True, "unchanged_original_inputs": True,
                "raw_archives_published": False, "new_load_executed": False}
    public(manifest)
    fresh_write(output / "manifest.json", json_bytes(manifest))
    print(json.dumps({"accepted": report["accepted"], "successes": saved["successes"], "partition_count": len(rows),
                      "action_interface_count": len(aggregate), "duration_credit_seconds": report["duration_credit_seconds"],
                      "summary_sha256": sha(output / "summary.json"), "manifest_sha256": sha(output / "manifest.json")}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--plan-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    need(os.sched_getaffinity(0) == {8}, "Offline reporting must run on CPU8")
    with (args.root / "perf01-evidence/timing.lock").open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        run(args)


if __name__ == "__main__":
    main()
