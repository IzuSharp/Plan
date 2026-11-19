#!/usr/bin/env python3
"""Extract actual Perf-01 codec cohorts; no build, workload or invented samples.

Freeze reads three before-only calibration processes. Compare reads fresh
three-process cohorts and invokes the unchanged, hash-pinned A21 statistics.
Run only outside the exclusive measurement window; raw files can be large.
"""
from __future__ import annotations

import argparse
from array import array
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import statistics

BASELINE = "ea5fa528035d025bd7a28698ee7c71194432236c"
METRICS = ("call_ns", "arrival_ns", "consume_ns", "release_ns", "operation_ns", "dispatch_lag_ns", "dispatch_to_admission_ns")
NOISE_METRICS = ("call_ns", "arrival_ns", "operation_ns")
COUNTERS = ("managed_allocated_bytes", "managed_allocated_bytes_including_validation", "copied_bytes_derived", "ffi_calls_derived")
PLAN_KEYS = ("domain", "controller_sha256", "a21_sha256", "corpus_manifest_sha256", "seed", "interface", "action", "case",
             "workers", "queue_capacity", "max_in_flight", "planned_rate", "period_ns", "duration_seconds", "warmup_seconds",
             "dispatch_span_guard_seconds", "idle_seconds", "deadline_ms", "max_lag_ms", "recovery_seconds", "recovery_rate", "sequence", "limits")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def load(path, expected=None):
    path = Path(path)
    require(path.stat().st_size <= 64 * 1024**2, "Oversized control file: " + str(path))
    data = path.read_bytes()
    require(expected is None or hashlib.sha256(data).hexdigest() == expected, "Changed control file: " + str(path))
    return json.loads(data)


def lines(path, expected):
    raw = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for line in stream:
            require(len(line) <= 4 * 1024**2, "Oversized raw record")
            raw.update(line)
            yield json.loads(line)
    require(raw.hexdigest() == expected, "Changed raw evidence: " + str(path))


def save(path, value):
    with Path(path).open("x") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False); stream.write("\n")


def a21_module(path):
    spec = importlib.util.spec_from_file_location("perf01_codec_a21", path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def quantiles(values, a21):
    return {label: a21.percentile(values, fraction) for label, fraction in (("p50", .5), ("p95", .95), ("p99", .99))}


def group_key(case, action, interface):
    return f"{action}/{interface}/case-{case}"


def require_population(groups, total):
    keys = {group_key(case, action, interface) for case in range(8) for action in "cd" for interface in "ao"}
    require(type(total) is int and total >= 16_000, "Full mixed codec cohort requires at least 16000 successes per process")
    require(set(groups) == keys, "Missing real case/action/interface rows")
    require(all(type(item["count"]) is int and item["count"] >= 100 for item in groups.values()),
            "Every codec row requires at least 100 successes in each independent process")
    require(sum(item["count"] for item in groups.values()) == total, "Per-row successes differ from the process total")


def contract(plan, build):
    # Product Git SHA and native/package/executable hashes intentionally vary.
    # The fixture, upstream locks, compiler settings and workload must not vary.
    value = {key: plan[key] for key in PLAN_KEYS}
    value["host"] = {key: item for key, item in plan["host"].items() if key != "background_load"}
    value["affinity"] = {key: plan["affinity_policy"][key] for key in ("mode", "target_cpus", "generator_cpus")}
    value["build"] = {key: build[key] for key in ("driver_sha256", "a21_sha256", "toolchain", "build_environment", "product_locks")}
    return value


def group():
    return {"count": 0, "raw": 0, "encoded": 0, "latency": {key: array("Q") for key in METRICS},
            "counters": {key: 0 for key in COUNTERS}, "known": {key: True for key in COUNTERS}}


def metrics(item, seconds, a21):
    count, call = item["count"], sum(item["latency"]["call_ns"])
    require(count > 0 and seconds > 0, "No observed successful group")
    result = {"successes": count, "successes_per_second": count / seconds,
              "raw_bytes": item["raw"], "encoded_bytes": item["encoded"],
              "raw_mib_per_second_wall": item["raw"] / 1048576 / seconds,
              "raw_mib_per_second_summed_call": item["raw"] / 1048576 / (call / 1e9) if call else None,
              "raw_over_encoded_ratio": item["raw"] / item["encoded"],
              "latency": {key: {"mean_ns": statistics.mean(values), **quantiles(values, a21)} for key, values in item["latency"].items()},
              "counter_totals": {key: item["counters"][key] if item["known"][key] else None for key in COUNTERS}}
    result["counter_per_success"] = {key: value / count if value is not None else None for key, value in result["counter_totals"].items()}
    return result


def merge(target, source):
    for key in ("count", "raw", "encoded"):
        target[key] += source[key]
    for key in METRICS:
        target["latency"][key].extend(source["latency"][key])
    for key in COUNTERS:
        target["counters"][key] += source["counters"][key]
        target["known"][key] &= source["known"][key]


def resources(root, hashes, start, end, summary):
    samples = {role: [] for role in ("target", "generator")}
    previous = None
    for row in lines(root / "resources.jsonl", hashes["resources.jsonl"]):
        require(type(row["observer_ns"]) is int and row["observer_ns"] >= 0 and (previous is None or row["observer_ns"] > previous), "Invalid resource sample clock")
        previous = row["observer_ns"]
        if start <= row["observer_ns"] <= end:
            for role in samples:
                value = row[role]
                rss, cpu = value.get("rss_bytes", {}).get("value"), value.get("cpu_seconds")
                require(rss is None or type(rss) is int and rss >= 0, "Invalid RSS scalar")
                require(cpu is None or type(cpu) in (int, float) and math.isfinite(cpu) and cpu >= 0, "Invalid CPU scalar")
                samples[role].append((row["observer_ns"], rss, cpu))
    result = {}
    for role, values in samples.items():
        rss = [(time, value) for time, value, _ in values if value is not None]
        cpu = [(time, value) for time, _, value in values if value is not None]
        require(all(left[1] <= right[1] for left, right in zip(cpu, cpu[1:])), "Process CPU counter decreased")
        result[role] = {"sample_count": len(values), "rss_sample_count": len(rss),
            "rss_sample_peak_bytes": max((value for _, value in rss), default=None),
            "rss_first_bytes": rss[0][1] if rss else None, "rss_last_bytes": rss[-1][1] if rss else None,
            "rss_observed_interval_ns": [rss[0][0], rss[-1][0]] if rss else None,
            "rss_endpoint_change_bytes_per_minute": (rss[-1][1] - rss[0][1]) * 60e9 / (rss[-1][0] - rss[0][0]) if len(rss) > 1 else None,
            "cpu_snapshot_interval_ns": [cpu[0][0], cpu[-1][0]] if len(cpu) > 1 else None,
            "cpu_percent_one_core_snapshot_interval": (cpu[-1][1] - cpu[0][1]) * 100e9 / (cpu[-1][0] - cpu[0][0]) if len(cpu) > 1 else None}
    require(all(summary[key] is None or type(summary[key]) in (int, float) and math.isfinite(summary[key]) and summary[key] >= 0
                for key in ("target_cpu_seconds", "target_cpu_percent_one_core")), "Invalid bracket CPU scalar")
    result["target"].update(cpu_seconds_bracket=summary["target_cpu_seconds"],
                            cpu_percent_one_core_bracket=summary["target_cpu_percent_one_core"],
                            rss_bracket_before_bytes=summary["rss_before_bytes"], rss_bracket_after_bytes=summary["rss_after_bytes"])
    return result


def cell(root, build_path, route, corpus, corpus_hash, a21, a21_hash, standard):
    root, build_path = Path(root).resolve(), Path(build_path).resolve()
    def stamp(path):
        value = path.stat(); return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns
    stamps = {path: stamp(path) for path in [build_path, *(root / name for name in ("summary.json", "plan.json", "result.json", "operations.jsonl", "events.jsonl", "resources.jsonl"))]}
    summary = load(root / "summary.json"); hashes = summary["files"]
    plan = load(root / "plan.json", hashes["plan.json"]); result = load(root / "result.json", hashes["result.json"])
    build = load(build_path, plan["manifest_sha256"])
    require(plan["route"] == summary["route"] == route and plan["source_commit"] == build["source_commit"] == summary["source_commit"], "Route/source identity mismatch")
    require(build["source_dirty"] is False and plan["a21_sha256"] == build["a21_sha256"] == a21_hash, "Unpinned source or changed A21")
    require(plan["corpus_manifest_sha256"] == corpus_hash and plan["limits"] == {key: corpus[key] for key in plan["limits"]}, "Corpus/limit identity mismatch")
    require(plan["action"] == plan["interface"] == "mixed" and plan["case"] is None, "Use the complete 32-row mixed corpus")
    require(summary["valid"] is True and all(result.get(key) is True for key in ("valid", "complete", "service_standard_met", "recovery_standard_met")), "Invalid, incomplete or failed cell: " + str(root))
    require(result["exit_code"] == 0 and result["drained_at_utc"] and result["idle_observation_seconds"] >= plan["idle_seconds"], "Missing exit/drain/idle proof")
    for name in ("profile-driver.json", "postgres-profile-summary.json", "profiling.json"):
        require(not (root / name).exists(), "Profiling cell cannot enter a comparison")
    require(summary["arrival_success_ns"]["p99"] is not None and summary["arrival_success_ns"]["p99"] <= standard["arrival_p99_maximum_ns"], "Frozen whole-cell latency standard failed")
    if route == "nativeweave":
        require(len(plan["actual_loaded_native"]) == 1 and plan["actual_loaded_native"][0]["sha256"] == build["native_sha256"], "Actual mapped native library mismatch")
    phase_counts = result["phase_counts"]; expected = phase_counts["measurement"]["planned"]
    require(type(expected) is int and 0 < expected <= 5_000_000, "Unbounded measurement ledger")
    first_id = phase_counts.get("warmup", {}).get("planned", 0)
    seen = bytearray(expected); phases = Counter(); groups = {}; total_arrivals = array("Q")
    last = result["scheduled_end_ns"]; first_dispatch = last_dispatch = None
    for row in lines(root / "operations.jsonl", hashes["operations.jsonl"]):
        phases[row["phase"]] += 1
        require(row["outcome"] == row["terminal_status"] == row["target"]["status"] == "ok", "Failed/late/generator-limited raw operation")
        if row["phase"] != "measurement":
            continue
        index = row["id"] - first_id
        require(0 <= index < expected and not seen[index], "Missing/duplicate measurement identity")
        seen[index] = 1
        require([row["case"], row["action"], row["interface"]] == plan["sequence"][index % len(plan["sequence"])], "Operation differs from frozen mix")
        scheduled, dispatch, admitted, completed = (row[key] for key in ("scheduled_ns", "dispatch_ns", "admitted_ns", "completion_ns"))
        require(result["scheduled_start_ns"] + index * plan["period_ns"] == scheduled and scheduled <= dispatch <= admitted <= completed, "Invalid observation clocks")
        require(dispatch - scheduled <= plan["max_lag_ms"] * 1e6 and completed - scheduled <= plan["deadline_ms"] * 1e6, "Arrival or generator constraint failed")
        first_dispatch = dispatch if first_dispatch is None else min(first_dispatch, dispatch)
        last_dispatch = dispatch if last_dispatch is None else max(last_dispatch, dispatch)
        target = row["target"]; case = corpus["cases"][row["case"]]
        require(target["id"] == row["id"] and target["raw_bytes"] == case["size"], "Payload identity/size mismatch")
        require(type(target["encoded_bytes"]) is int and 0 < target["encoded_bytes"] <= corpus["encoded_limit"], "Encoded size exceeds frozen limit")
        require(route == "managed-zlib" or target["encoded_bytes"] == case["encoded_bytes"], "Strict encoded oracle differs")
        require(abs(target["operation_ns"] - sum(target[key] for key in ("call_ns", "consume_ns", "release_ns"))) <= 2, "Invalid ownership timing decomposition")
        key = group_key(row["case"], row["action"], row["interface"]); item = groups.setdefault(key, group())
        item["count"] += 1; item["raw"] += target["raw_bytes"]; item["encoded"] += target["encoded_bytes"]
        times = {key: target[key] for key in ("call_ns", "consume_ns", "release_ns", "operation_ns")}
        times.update(arrival_ns=completed-scheduled, dispatch_lag_ns=dispatch-scheduled, dispatch_to_admission_ns=admitted-dispatch)
        for metric, value in times.items():
            require(type(value) is int and value >= 0, "Invalid timing scalar"); item["latency"][metric].append(value)
        total_arrivals.append(completed - scheduled); last = max(last, completed)
        for counter in COUNTERS:
            value = target.get(counter)
            if value is None: item["known"][counter] = False
            else:
                require(type(value) is int and value >= 0, "Invalid allocation/copy/FFI counter"); item["counters"][counter] += value
    require(all(seen) and summary["offered"] == summary["successes"] == expected, "Incomplete successful measurement ledger")
    for phase, counts in phase_counts.items():
        require(phases[phase] == counts["planned"] and all(counts.get(key) == counts["planned"] for key in ("sent", "dispatch_attempted", "admitted", "completed", "ok")), "Incomplete phase: " + phase)
    require_population(groups, expected)
    require(set(groups) == set(summary["groups"]), "Summary case/action/interface rows differ")
    seconds = (last - result["scheduled_start_ns"]) / 1e9
    require(math.isclose(seconds, result["measurement_observation_seconds"], rel_tol=0, abs_tol=1e-9), "Wrong wall denominator")
    dispatch_span = (last_dispatch - first_dispatch) / 1e9
    require(dispatch_span >= plan["duration_seconds"] and math.isclose(dispatch_span, result["actual_dispatch_span_seconds"], rel_tol=0, abs_tol=1e-9), "Wrong actual dispatch span")
    observed = {key: metrics(item, seconds, a21) for key, item in groups.items()}
    for key, value in observed.items():
        saved = summary["groups"][key]
        require(value["successes"] == saved["successes"] == saved["offered"] and value["raw_bytes"] == saved["raw_bytes"] and value["encoded_bytes"] == saved["encoded_bytes"], "Summary counters differ from raw ledger")
        require({label: value["latency"]["arrival_ns"][label] for label in ("p50", "p95", "p99")} == saved["arrival_ns"], "Summary tail differs from raw ledger")
    require(quantiles(total_arrivals, a21) == summary["arrival_success_ns"], "Whole-cell latency summary mismatch")
    ready = []; drained = []
    for event in lines(root / "events.jsonl", hashes["events.jsonl"]):
        if event.get("kind") == "ready": ready.append(event)
        if event.get("kind") == "drained": drained.append(event)
    require(len(ready) == len(drained) == 1 and ready[0]["dynamic_code_supported"] is False and not drained[0].get("errors", 0), "Missing actual AOT/direct readiness or drain proof")
    require(ready[0]["workers"] == plan["workers"] and ready[0]["queue_capacity"] == plan["queue_capacity"]
            and ready[0]["strict_single_stream_comparable"] is (route != "managed-zlib"), "Target resource/comparability declaration differs")
    native = drained[0].get("native")
    require(native is None or all(native[key] == 0 for key in ("live", "capacity", "active")), "Native result owner did not retire")
    require(route != "nativeweave" or native is not None, "Missing native ownership counters")
    resource = resources(root, hashes, result["scheduled_start_ns"], last, summary)
    rss = resource["target"]["rss_sample_peak_bytes"]
    require(rss is not None and rss <= standard["rss_maximum_bytes"], "Missing/excessive sampled RSS")
    process = plan["affinity_observations"]["ready"]["target"]
    executable = build["direct_executable"] if route == "direct-rust" else build["managed_executable"]
    evidence = {"directory": str(root), "summary_sha256": sha(root / "summary.json"), "files_sha256": hashes,
        "source_commit": plan["source_commit"], "build_manifest_sha256": sha(build_path), "executable_sha256": build["artifacts"][executable],
        "actual_loaded_native": plan.get("actual_loaded_native"), "process_identity": [process["pid"], process["start_ticks"]],
        "window_ns": [result["scheduled_start_ns"], last], "start_utc": result["measurement_start_utc"], "end_utc": result["measurement_end_utc"],
        "observation_seconds": seconds, "actual_dispatch_span_seconds": result["actual_dispatch_span_seconds"],
        "phase_counts": phase_counts, "errors": 0, "resources": resource, "drained": drained[0], "groups": observed}
    require(all(stamp(path) == value for path, value in stamps.items()), "Input changed during extraction")
    return evidence, groups, contract(plan, build), build


def independent(cells):
    require(len({tuple(item["process_identity"]) for item in cells}) == len(cells), "Repeated process identity")
    require(len({item["summary_sha256"] for item in cells}) == len(cells), "Repeated evidence cell")
    windows = sorted(item["window_ns"] for item in cells)
    require(all(left[1] <= right[0] for left, right in zip(windows, windows[1:])), "Measurement windows overlap")


def cohort(paths, build, route, args, standard):
    require(len(paths) == 3, "Exactly three independent processes are required")
    cells = []; combined = {}; fixed = None
    for path in paths:
        receipt, groups, current, producer = cell(path, build, route, args.corpus_value, args.corpus_sha, args.a21_module, args.a21_sha, standard)
        require(fixed is None or current == fixed, "Within-cohort workload/build setting mismatch")
        fixed = current; cells.append(receipt)
        for key, item in groups.items(): merge(combined.setdefault(key, group()), item)
    independent(cells)
    seconds = sum(item["observation_seconds"] for item in cells)
    cpu = [item["resources"]["target"]["cpu_seconds_bracket"] for item in cells]
    return {"route": route, "cells": cells, "contract": fixed, "producer": producer,
        "groups": {key: metrics(item, seconds, args.a21_module) for key, item in combined.items()},
        "mixed_resource_summary": {"observation_seconds_total": seconds, "errors": 0,
            "target_cpu_percent_one_core": sum(cpu) / seconds * 100 if all(value is not None for value in cpu) else None,
            "target_rss_sample_peak_bytes": max(item["resources"]["target"]["rss_sample_peak_bytes"] for item in cells),
            "scope": "Whole mixed target process, including fixture/oracle/runtime work; not attributable to individual rows. Per-process generator and endpoint RSS observations are retained in cells."}}


def noise_bands(cells, resolution):
    bands = {}
    for key in cells[0]["groups"]:
        bands[key] = {}
        for metric in NOISE_METRICS:
            means = [item["groups"][key]["latency"][metric]["mean_ns"] for item in cells]
            bands[key][metric] = {"absolute_noise_ns": max(resolution, max(means)-min(means)), "relative_noise": 0,
                                  "before_process_means_ns": means}
    return bands


def freeze(args):
    require(not args.output.exists(), "Use a new noise receipt path")
    require(math.isfinite(args.p99_max_ms), "Nonfinite latency standard")
    standard = {"arrival_p99_maximum_ns": round(args.p99_max_ms * 1e6), "rss_maximum_bytes": args.rss_max_mib * 1048576}
    require(args.resolution_ns > 0 and standard["arrival_p99_maximum_ns"] > 0 and standard["rss_maximum_bytes"] > 0, "Invalid prospective analysis/SLO floor")
    baseline = cohort(args.cells, args.build, "nativeweave", args, standard)
    require(baseline["producer"]["source_commit"] == BASELINE, "Before producer is not the frozen pre-change main")
    fixed = baseline["contract"]
    require(args.resolution_ns >= math.ceil(fixed["host"]["clock"]["resolution_seconds"] * 1e9), "Analysis floor below advertised monotonic resolution")
    bands = noise_bands(baseline["cells"], args.resolution_ns)
    value = {"schema_version": 1, "task": "Perf-01", "kind": "codec-before-only-frozen-noise",
        "created_utc": datetime.now(timezone.utc).isoformat(), "extractor_sha256": sha(__file__), "a21_sha256": args.a21_sha,
        "corpus_manifest_sha256": args.corpus_sha, "before_build_manifest_sha256": sha(args.build),
        "before_source_commit": baseline["producer"]["source_commit"], "contract": fixed, "contract_sha256": digest(fixed),
        "standard": standard, "declared_analysis_floor_ns": args.resolution_ns, "calibration_cells": baseline["cells"], "bands": bands,
        "derivation": "Per metric/row: max(declared analysis floor, range of exactly three before-only independent process means); no candidate or direct observations used; relative band zero.",
        "direct_executable_sha256": baseline["producer"]["artifacts"][baseline["producer"]["direct_executable"]]}
    save(args.output, value)


def change(before, after):
    if before is None or after is None:
        return {"absolute": None, "percent": None, "reason": "Unavailable observed metric"}
    return {"absolute": after-before, "percent": (after-before) / before * 100 if before else None,
            **({"reason": "Percentage undefined for a zero baseline"} if before == 0 else {})}


def comparisons(before, after):
    values = {key: change(before[key], after[key]) for key in ("successes_per_second", "raw_mib_per_second_wall", "raw_mib_per_second_summed_call", "raw_over_encoded_ratio")}
    for metric in NOISE_METRICS:
        for statistic in ("mean_ns", "p99"):
            values[metric + "/" + statistic] = change(before["latency"][metric][statistic], after["latency"][metric][statistic])
    for key in COUNTERS:
        values[key + "/per_success"] = change(before["counter_per_success"][key], after["counter_per_success"][key])
    return values


def compare(args):
    require(not args.output.exists(), "Use a fresh comparison output directory")
    require(sha(args.noise) == args.noise_sha256, "Precommitted frozen-noise hash differs")
    frozen = load(args.noise)
    require(frozen["kind"] == "codec-before-only-frozen-noise" and frozen["a21_sha256"] == args.a21_sha
            and frozen["corpus_manifest_sha256"] == args.corpus_sha and frozen["extractor_sha256"] == sha(__file__), "Changed frozen analysis source/input")
    require(sha(args.before_build) == frozen["before_build_manifest_sha256"], "Before build changed after noise freeze")
    require(digest(frozen["contract"]) == frozen["contract_sha256"] and len(frozen["calibration_cells"]) == 3
            and frozen["bands"] == noise_bands(frozen["calibration_cells"], frozen["declared_analysis_floor_ns"]), "Frozen band derivation differs")
    require(bool(args.managed) == bool(args.managed_build), "Provide managed cells and their exact producer together")
    cohorts = {}
    for name, route in (("before", "nativeweave"), ("after", "nativeweave"), ("direct", "direct-rust"), ("managed", "managed-zlib")):
        paths = getattr(args, name)
        if not paths: continue
        cohort_value = cohort(paths, getattr(args, name + "_build"), route, args, frozen["standard"])
        require(cohort_value["contract"] == frozen["contract"], "Cohort differs from frozen workload/driver/upstream/build settings: " + name)
        cohorts[name] = cohort_value
    require(all(item["executable_sha256"] == frozen["direct_executable_sha256"] for item in cohorts["direct"]["cells"]), "Direct reference executable changed")
    confirmation = [item for value in cohorts.values() for item in value["cells"]]
    frozen_at = datetime.fromisoformat(frozen["created_utc"])
    require(all(datetime.fromisoformat(item["end_utc"]) <= frozen_at for item in frozen["calibration_cells"])
            and all(datetime.fromisoformat(item["start_utc"]) >= frozen_at for item in confirmation), "Noise was not frozen before fresh confirmation processes")
    independent(frozen["calibration_cells"] + confirmation)
    rows = []
    for case in args.corpus_value["cases"]:
        for action in "cd":
            for interface in "ao":
                key = group_key(case["id"], action, interface)
                observed = {name: value["groups"][key] for name, value in cohorts.items()}
                row = {"key": key, "case": case, "action": "compress" if action == "c" else "decompress",
                    "interface": "array" if interface == "a" else "owned", "observed": observed,
                    "after_minus_before": comparisons(observed["before"], observed["after"]),
                    "before_minus_direct": comparisons(observed["direct"], observed["before"]),
                    "after_minus_direct": comparisons(observed["direct"], observed["after"]), "noise": {}}
                for candidate, reference in (("after", "before"), ("after", "direct"), ("before", "direct")):
                    label = candidate + "_vs_" + reference; row["noise"][label] = {}
                    for metric in NOISE_METRICS:
                        means = lambda name: [item["groups"][key]["latency"][metric]["mean_ns"] for item in cohorts[name]["cells"]]
                        band = dict(frozen["bands"][key][metric], baseline_id=sha(args.noise))
                        row["noise"][label][metric] = args.a21_module.noise_comparison(means(reference), means(candidate), band, frozen["contract"]["seed"])
                if "managed" in cohorts:
                    row["managed_scope"] = "Valid-corpus isolated codec call only; no full semantic, arrival/operation or NativeBuffer ranking. Owned is an array-path alias; compression bytes/ratio may differ."
                rows.append(row)
    output = Path(args.output); output.mkdir(parents=True)
    value = {"schema_version": 1, "task": "Perf-01", "kind": "codec-observed-comparison", "created_utc": datetime.now(timezone.utc).isoformat(),
        "extractor_sha256": sha(__file__), "a21_sha256": args.a21_sha, "noise_sha256": sha(args.noise), "corpus_manifest_sha256": args.corpus_sha,
        "contract_sha256": frozen["contract_sha256"], "standard": frozen["standard"], "rows": rows,
        "cohorts": {name: {key: value[key] for key in ("route", "cells", "mixed_resource_summary")} for name, value in cohorts.items()},
        "definitions": ["Each independent process contains at least 16000 successes and at least 100 in every one of the 32 rows. Pooled nearest-rank tails retain per-process tails/means in cells.",
            "Throughput uses the sum of each process's full observation window; row rates are contributions to the fixed mix, not standalone maximum capacity.",
            "Summed-call MiB/s divides raw bytes by sum(call_ns), not elapsed wall time; it is not concurrent successful throughput.",
            "Noise inference uses exactly three independent process means and the unchanged pinned A21 function. P99/throughput percentage differences are descriptive, not separately bootstrapped claims.",
            "Copied bytes cover the derived managed/native output copy only; FFI counts cover codec and result-free calls. Neither is hardware traffic or all runtime/native allocations.",
            "Array public calls include managed copy and native result retirement. Owned public calls exclude subsequent Read/Dispose; consume/release/operation fields retain those costs.",
            "Direct labels both partition the same Vec path. Managed labels both partition arrays, and strict trailing/concatenated-stream rejection is not equivalent; no managed full-operation/arrival ranking is emitted.",
            "Native allocator counts and total internal copies are unavailable. Target CPU/RSS belong to the entire mixed process; resource samples do not continuously bound unsampled peaks.",
            "Extraction verifies recorded identities, bytes/counts and lifecycle receipts; it does not replay correctness or grant 30-minute acceptance. Physical host/exclusive-run ownership remains bound by the execution ledger."]}
    save(output / "comparison.json", value)
    markdown(output / "comparison.md", value)


def markdown(path, report):
    def number(value, scale=1): return "NA" if value is None else f"{value / scale:.3f}"
    text = ["# Perf-01 observed codec comparison", "", "All latency values below are observed. Arrival p99 is pooled across the three independent processes; call means and per-process values are in the JSON. CPU/RSS apply to the complete mixed process.", "",
        "| Case / action / interface | Before ops/s | After ops/s | Before p99 ms | After p99 ms | p99 change % | Before call µs | After call µs | Call-mean A21 decision |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for row in report["rows"]:
        before, after = row["observed"]["before"], row["observed"]["after"]
        label = f"{row['case']['size']} B {row['case']['entropy']} / {row['action']} / {row['interface']}"
        text.append("| " + " | ".join((label, number(before["successes_per_second"]), number(after["successes_per_second"]),
            number(before["latency"]["arrival_ns"]["p99"], 1e6), number(after["latency"]["arrival_ns"]["p99"], 1e6),
            number(row["after_minus_before"]["arrival_ns/p99"]["percent"]), number(before["latency"]["call_ns"]["mean_ns"], 1e3),
            number(after["latency"]["call_ns"]["mean_ns"], 1e3), row["noise"]["after_vs_before"]["call_ns"]["decision"])) + " |")
    text += ["", "## Direct miniz gap and valid-corpus managed observations", "", "Managed values describe the isolated valid-corpus call only; the owned label is the same managed array implementation. No managed end-to-end ranking follows from this table.", "",
        "| Row | Direct call µs | After-minus-direct call µs | Gap % | Direct arrival p99 ms | Managed call µs | After raw MiB/s wall | After raw MiB/s summed call | After ratio | After allocated B/call | After copied B/op | After derived FFI/op |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for row in report["rows"]:
        after, direct = row["observed"]["after"], row["observed"]["direct"]
        managed = row["observed"].get("managed")
        counter = after["counter_per_success"]
        text.append("| " + " | ".join((row["key"], number(direct["latency"]["call_ns"]["mean_ns"], 1e3),
            number(row["after_minus_direct"]["call_ns/mean_ns"]["absolute"], 1e3), number(row["after_minus_direct"]["call_ns/mean_ns"]["percent"]),
            number(direct["latency"]["arrival_ns"]["p99"], 1e6), number(managed["latency"]["call_ns"]["mean_ns"] if managed else None, 1e3),
            number(after["raw_mib_per_second_wall"]), number(after["raw_mib_per_second_summed_call"]), number(after["raw_over_encoded_ratio"]),
            number(counter["managed_allocated_bytes"]), number(counter["copied_bytes_derived"]), number(counter["ffi_calls_derived"]))) + " |")
    text += ["", "## Whole mixed-process resources", "", "| Cohort | Observation seconds summed | Target CPU % of one core | Target sampled peak RSS MiB | Errors |", "| --- | ---: | ---: | ---: | ---: |"]
    for name, cohort_value in report["cohorts"].items():
        item = cohort_value["mixed_resource_summary"]
        text.append(f"| {name} | {number(item['observation_seconds_total'])} | {number(item['target_cpu_percent_one_core'])} | {number(item['target_rss_sample_peak_bytes'], 1048576)} | {item['errors']} |")
    text += ["", "## Interpretation limits", ""] + ["- " + item for item in report["definitions"]]
    with path.open("x") as stream: stream.write("\n".join(text) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__); sub = parser.add_subparsers(dest="command", required=True)
    for name in ("freeze", "compare"):
        command = sub.add_parser(name)
        command.add_argument("--corpus", type=Path, required=True); command.add_argument("--a21", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True)
        if name == "freeze":
            command.add_argument("--cells", type=Path, nargs=3, required=True); command.add_argument("--build", type=Path, required=True)
            command.add_argument("--resolution-ns", type=int, required=True)
            command.add_argument("--p99-max-ms", type=float, default=500); command.add_argument("--rss-max-mib", type=int, default=256)
        else:
            command.add_argument("--noise", type=Path, required=True)
            command.add_argument("--noise-sha256", required=True, help="Exact receipt SHA recorded before confirmation measurements")
            for route in ("before", "after", "direct", "managed"):
                command.add_argument("--" + route, type=Path, nargs=3, required=route != "managed")
                command.add_argument("--" + route + "-build", type=Path, required=route != "managed")
    args = parser.parse_args(); args.a21_sha = sha(args.a21); args.a21_module = a21_module(args.a21)
    args.corpus_sha = sha(args.corpus); args.corpus_value = load(args.corpus)
    require([item["id"] for item in args.corpus_value["cases"]] == list(range(8)) and args.corpus_value["format"] == "zlib"
            and args.corpus_value["level"] == 6 and args.corpus_value["checksum"] == "Adler32", "Not the frozen eight-case zlib corpus")
    if args.command == "freeze": freeze(args)
    else: compare(args)
    print(args.output)


if __name__ == "__main__":
    main()
