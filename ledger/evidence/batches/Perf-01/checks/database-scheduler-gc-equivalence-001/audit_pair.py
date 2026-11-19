#!/usr/bin/env python3
"""Audit existing fixed-before GC-policy pair evidence without running a load."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import heapq
import importlib.util
import itertools
import json
import math
from pathlib import Path
import sys

sys.dont_write_bytecode = True
DOCUMENT_SHA = "21b8f09254b41cbfe46f817d3fb61c0360b1470323b5191ef56c92e73c7d22a9"
SUPERVISOR_SHA = "b40dbb3ac829398e4ee1cef2995507414287ee1a61793e1b06cebc8407bbf3c5"
READER_SHA = "8034692b643f4dbb1385cd61e25c9d4d6f084d7b71268fec02411b5c2fcdbeb4"
DRIVER_COMMIT = "0b2af54419ecf6a11ec83a45725b1c5fbbaeb0d0"


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            value.update(chunk)
    return value.hexdigest()


def stamp(path):
    value = path.stat()
    return [value.st_size, value.st_mtime_ns, value.st_ino]


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def percentile(values, q):
    return sorted(values)[math.ceil(len(values) * q) - 1]


def endpoint(row):
    return {key: row.get(key) for key in
            ("pid", "start_ticks", "time_ns", "cpu_observed_ns", "cpu_ticks",
             "clock_ticks_per_second", "fd_count", "socket_count", "affinity_cpus")} | {
        "rss_bytes": row["counters"]["rss_bytes"]["value"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    plan_repo = root / ".worktree/Perf-01-linux/Plan"
    document_path = plan_repo / "ledger/evidence/batches/Perf-01/database-gc-fixed-before-pair-001.json"
    supervisor_path = root / "perf01-run/run_db_gc_pair_001.py"
    execution_path = root / "perf01-run/database-gc-fixed-before-pair-001-execution.json"
    inputs, checks = {}, []

    def pin(path, expected=None):
        path = Path(path)
        before = stamp(path)
        actual = digest(path)
        assert stamp(path) == before, "Input changed while hashing: " + str(path)
        assert expected is None or actual == expected, "Input hash mismatch: " + str(path)
        inputs[str(path)] = {"sha256": actual, "bytes": before[0], "stat_identity": before}
        return actual

    def small(path, expected=None, destination=None):
        pin(path, expected)
        assert Path(path).stat().st_size <= 1024 * 1024
        data = Path(path).read_bytes()
        if destination:
            (output / destination).write_bytes(data)
        return json.loads(data)

    def check(name, condition):
        checks.append({"name": name, "passed": bool(condition)})
        assert condition, name

    doc = small(document_path, DOCUMENT_SHA, "command-document.json")
    execution = small(execution_path, destination="pair-execution.json")
    pin(supervisor_path, SUPERVISOR_SHA)
    (output / "run_db_gc_pair_001.py").write_bytes(supervisor_path.read_bytes())
    check("actual supervisor/document identity", execution["document_sha256"] == DOCUMENT_SHA and
          execution["supervisor_source_sha256"] == SUPERVISOR_SHA)
    check("serial command completion pending independent audit",
          execution["state"] == "commands-completed-validation-pending" and
          execution["duration_credit_seconds"] == 0 and execution["formal_timing_eligible"] is False)
    driver = Path(doc["immutable_measurement_driver"]["path"])
    check("exact committed driver", doc["immutable_measurement_driver"]["commit"] == DRIVER_COMMIT)
    for path, expected in doc["required_source_and_metadata_sha256"].items():
        pin(Path(path), expected)
    reader_path = driver / "tests/Perf01/verify_long.py"
    pin(reader_path, READER_SHA)
    spec = importlib.util.spec_from_file_location("perf01_pair_existing_json_reader", reader_path)
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    results = {}
    comparison = {}
    for command, actual in zip(doc["commands"], execution["commands"], strict=True):
        mode = command["policy"]
        cell = Path(command["output"])
        selected = output / mode
        selected.mkdir()
        prefix = mode + "/"
        check(mode + ": exact executed argv and normal exit",
              actual["id"] == command["id"] and actual["argv"] == command["argv"] and
              actual["exit_code"] == 0 and actual["summary_gate_passed"] is True)
        pin(Path(actual["log"]), actual["log_sha256"])
        (selected / "driver.log").write_bytes(Path(actual["log"]).read_bytes())
        summary = small(cell / "summary.json", actual["summary_sha256"], prefix + "summary.json")
        progress = small(cell / "progress.json", destination=prefix + "progress.json")
        frozen = small(cell / "frozen-inputs.json", summary["frozen_inputs_sha256"], prefix + "frozen-inputs.json")
        plan = small(cell / "plan.json", frozen["plan_sha256"], prefix + "plan.json")
        target = small(cell / "target.json")
        supervision = small(cell / "supervision/receipt.json", destination=prefix + "supervision.json")
        policy = small(cell / "observation.scheduler-gc.json", summary["scheduler_gc_receipt"]["sha256"],
                       prefix + "scheduler-gc.json")
        extra_path = Path(summary["perf01_receipt"]["path"])
        extra = small(extra_path, summary["perf01_receipt"]["sha256"], prefix + "perf01.json")
        app_path = Path(summary["application_receipt"]["path"])
        pin(app_path, summary["application_receipt"]["sha256"])
        app = reader.object_metadata(app_path, ("status", "errors", "durable_oracle", "closed"))
        save(selected / "application-receipt-projection.json", app)
        check(mode + ": original validity/service flags",
              all(summary[key] is True for key in ("valid", "qualifies_service_standard",
                                                   "scheduler_gc_policy_valid", "duration_valid")) and
              summary["invalid_reasons"] == [] and summary["provider_errors"]["observed_exceptions"] == 0)
        check(mode + ": original application correctness and closure",
              app["status"] == extra["status"] == "passed" and app["errors"] == [] and
              app["durable_oracle"] == summary["durable_oracle"] and
              app["closed"] == summary["closed"] and
              summary["closed"] == {"consumerResourcesReleased": True, "consumerStatus": "Succeeded",
                                   "databaseResourcesReleased": True, "databaseStatus": "Succeeded",
                                   "serverState": "Disposed"})
        check(mode + ": source commit and source map", frozen["driver_source"]["commit"] == DRIVER_COMMIT and
              frozen["driver_source"]["scope_status"] == "")
        for path, expected in frozen["source_files"].items():
            pin(Path(path), expected)
        policy_hash = hashlib.sha256(json.dumps(policy["policy"], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        check(mode + ": policy descriptors and stable hashes",
              policy["policy"] == frozen["scheduler_gc_policy"] == summary["scheduler_gc_policy"] ==
              plan["settings"]["features"]["scheduler_gc_policy"] == target["perf01"]["scheduler_gc_policy"] and
              policy["policy"]["mode"] == mode and
              policy_hash == policy["policy_sha256"] == frozen["scheduler_gc_policy_sha256"] ==
              summary["scheduler_gc_policy_sha256"])
        owned = next(row for row in supervision["owned_processes"]
                     if row["role"] == "cell-worker" and row["pid"] == supervision["worker_pid"])
        check(mode + ": actual supervised PID/start identity",
              all(policy["process"][key] == owned[key] for key in ("pid", "start_ticks")) and
              policy["cpu_affinity"] == [0, 1])
        check(mode + ": actual policy source and plan identities",
              policy["plan_sha256"] == frozen["plan_sha256"] and
              all(frozen["source_files"].get(path) == expected for path, expected in policy["source_files"].items()))
        initial, entry, end, restored = [policy[key] for key in
                                        ("initial_gc", "scope_entry_gc", "scope_exit_gc", "restored_gc")]
        deltas = [last["collections"] - first["collections"]
                  for first, last in zip(entry["stats"], end["stats"], strict=True)]
        check(mode + ": normal GC lifecycle and exact deltas",
              policy["status"] == "completed" and policy["worker_exit_code"] == 0 and
              policy["scope_finished_ns"] > policy["scope_started_ns"] and
              initial["enabled"] is True and restored["enabled"] is True and
              entry["enabled"] is (mode == "automatic") and end["enabled"] is (mode == "automatic") and
              initial["threshold"] == entry["threshold"] == end["threshold"] == restored["threshold"] == [700, 10, 10] and
              len(deltas) == 3 and deltas == policy["collections_during_scope"] and
              all(value >= 0 for value in deltas) and (mode == "automatic" or deltas == [0, 0, 0]))
        check(mode + ": supervised cleanup without forced signals",
              supervision["status"] == "completed" and supervision["worker_exit_code"] == 0 and
              supervision.get("failure") is None and not supervision.get("signals") and
              not supervision.get("live_owned_processes_after_cleanup") and not supervision.get("cleanup_error"))
        check(mode + ": database teardown", not list((cell / "postgres").rglob("postmaster.pid")))
        dataset_sha = pin(cell / "dataset.json", frozen["dataset_sha256"])
        check(mode + ": original dataset and full planned count",
              plan["oracle"]["sha256"] == dataset_sha and plan["timing"]["requests"] == 17282 and
              plan["timing"]["period_ns"] == 6944444 and plan["timing"]["max_dispatch_lag_ns"] == 100000000)
        raw_sha = pin(cell / "observation.json")
        metadata = dict.fromkeys(("valid", "invalid_reasons", "exit_code", "offered", "admitted",
                                  "completed", "successful", "outcome_counts", "measurement_window_ns",
                                  "late_events", "raw_events"))
        records = reader.array_records(cell / "observation.json", "records", metadata)
        data = reader.array_records(cell / "dataset.json")
        count = 0
        mix = Counter()
        lags, latencies = [], []
        by_kind = {"cycle": [], "list": []}
        top = []
        first_row = last_row = None
        sentinel = object()
        for number, (row, datum) in enumerate(itertools.zip_longest(records, data, fillvalue=sentinel)):
            assert row is not sentinel and datum is not sentinel and number < 17282
            assert row["id"] == number and row["status"] == "ok" and row["value"] == datum["expected"]
            kind = row["value"]["kind"]
            assert kind == ("cycle" if number % 2 == 0 else "list")
            assert row["scheduled_ns"] <= row["dispatch_ns"] <= row["admission_ns"] <= row["completion_ns"] <= row["deadline_ns"]
            if first_row is None:
                first_row = row
            assert row["scheduled_ns"] == first_row["scheduled_ns"] + number * plan["timing"]["period_ns"]
            last_row = row
            lag = row["dispatch_ns"] - row["scheduled_ns"]
            arrival = row["completion_ns"] - row["scheduled_ns"]
            timing = {key: row[key] for key in ("id", "scheduled_ns", "dispatch_ns", "admission_ns", "completion_ns", "status")}
            timing["dispatch_lag_ns"] = lag
            heapq.heappush(top, (lag, number, timing))
            if len(top) > 5:
                heapq.heappop(top)
            lags.append(lag); latencies.append(arrival); by_kind[kind].append(arrival)
            mix[kind] += 1
            count += 1
        check(mode + ": all raw results independently match frozen dataset",
              count == 17282 and mix == {"cycle": 8641, "list": 8641} and
              summary["offered"] == summary["dispatched"] == summary["successful"] == count and
              summary["outcomes"] == {"ok": count})
        check(mode + ": complete raw accounting and no late/error records",
              metadata["valid"] is True and metadata["invalid_reasons"] == [] and
              metadata["exit_code"] == 0 and metadata["late_events"] == [] and
              all(metadata[key] == count for key in ("offered", "admitted", "completed", "successful")))
        check(mode + ": frozen dispatch and arrival service limits",
              max(lags) <= 100000000 and percentile(latencies, .99) <= 500000000 and
              all(summary["p" + label + "_ns"] == percentile(latencies, q)
                  for label, q in (("50", .5), ("95", .95), ("99", .99))) and
              all(summary["by_kind"][kind]["p99_ns"] == percentile(values, .99) for kind, values in by_kind.items()))
        raw_events = cell / metadata["raw_events"]["path"]
        pin(raw_events, metadata["raw_events"]["sha256"])
        for phase, expected in (("persisted_before_recovery", {"measurement": 8641, "seed": 128, "warmup": 8}),
                                ("persisted_before_shutdown", {"measurement": 8641, "seed": 128, "warmup": 8, "recovery": 32})):
            value = summary[phase]
            check(mode + ": independent SQL " + phase,
                  value == extra[phase] and value["availability"] == "measured" and
                  value["committed_operations_by_phase"] == expected and
                  value["persisted_rows"] == {table: sum(expected.values()) for table in ("items", "operations", "outbox")})
        check(mode + ": independent durable oracle cardinality",
              summary["durable_oracle"]["passed"] is True and
              all(summary["durable_oracle"][key] == 8777 for key in ("items", "operations", "outbox")))
        recovery = summary["phases"]["recovery"]
        check(mode + ": same-process recovery and idle",
              len(recovery["operations"]) == 32 and all(row["status"] == "ok" for row in recovery["operations"]) and
              recovery["oracle"]["passed"] is True and
              all(recovery["oracle"][key] == 8809 for key in ("items", "operations", "outbox")) and
              summary["phases"]["idle"]["end_ns"] - summary["phases"]["idle"]["start_ns"] >= 60000000000)
        journal = extra["outcome_journal"]
        check(mode + ": complete published warmup/measurement journal",
              journal["status"] == "completed" and journal["rows"] == 17298 and journal["error"] is None and
              all(journal[key] is True for key in ("closed", "published", "sealed")))
        pin(extra_path.parent / journal["path"], journal["sha256"])
        observer = summary["generator_resource_observer"]
        check(mode + ": generator observer completed without identity/errors",
              observer["status"] == "completed" and observer["errors"] == [] and observer["identity_failures"] == [])
        resource_path = extra_path.parent / observer["path"]
        pin(resource_path, observer["sha256"])
        groups, previous = {}, {}
        with resource_path.open("rb") as stream:
            for line_number, line in enumerate(stream, 1):
                assert len(line) < 4 * 1024**2
                row = json.loads(line)
                role, phase = row["role"], row["phase"]
                expected = observer["roles"][role]
                assert row["identity_matches"] is True
                assert all(row[key] == expected[key] for key in ("pid", "start_ticks"))
                assert row["affinity_cpus"] == [0, 1]
                if role in previous:
                    assert row["time_ns"] >= previous[role]["time_ns"] and row["cpu_ticks"] >= previous[role]["cpu_ticks"]
                previous[role] = row
                group = groups.setdefault((role, phase), {"first": row, "last": row, "first_line": line,
                    "last_line": line, "first_number": line_number, "last_number": line_number,
                    "samples": 0, "rss_peak_bytes": 0})
                group.update(last=row, last_line=line, last_number=line_number)
                group["samples"] += 1
                group["rss_peak_bytes"] = max(group["rss_peak_bytes"], row["counters"]["rss_bytes"]["value"])
        resource_projection = {}
        retained = {}
        for (role, phase), group in groups.items():
            given = summary["generator_resources"][role][phase]
            first, last = group["first"], group["last"]
            check(mode + ": resource samples/peak " + role + "/" + phase,
                  group["samples"] == given["samples"] and group["rss_peak_bytes"] == given["rss_peak_bytes"] and
                  first == given["first"] and last == given["last"] and not any(given["error_samples"].values()))
            if group["samples"] > 1:
                cpu = (last["cpu_ticks"] - first["cpu_ticks"]) / last["clock_ticks_per_second"]
                span = last["cpu_observed_ns"] - first["cpu_observed_ns"]
                check(mode + ": resource CPU arithmetic " + role + "/" + phase,
                      cpu == given["cpu_seconds"] and math.isclose(cpu * 1e11 / span, given["cpu_percent_one_core"], rel_tol=1e-12))
            resource_projection.setdefault(role, {})[phase] = {
                key: given.get(key) for key in ("samples", "cpu_samples", "cpu_seconds", "cpu_percent_one_core",
                    "cpu_span_seconds", "rss_peak_bytes", "fd_peak_count", "socket_peak_count", "error_samples")}
            resource_projection[role][phase].update(first=endpoint(first), last=endpoint(last))
            retained[group["first_number"]] = group["first_line"]
            retained[group["last_number"]] = group["last_line"]
        with (selected / "generator-resource-endpoints.jsonl").open("xb") as sink:
            for number in sorted(retained):
                sink.write(retained[number])
        check(mode + ": generator per-role sample totals",
              {role: sum(group["samples"] for (candidate, _), group in groups.items() if candidate == role)
               for role in observer["roles"]} == observer["samples"])
        check(mode + ": original application RSS limit",
              summary["resources"]["measurement"]["rss_peak_bytes"] <= 268435456)
        loaded = {path: value["sha256"] for path, value in summary["loaded_files"].items()}
        check(mode + ": expected actual executable hash",
              all(value.get("expected_sha256", value["sha256"]) == value["sha256"] for value in summary["loaded_files"].values()))
        comparison[mode] = {"dataset_sha256": dataset_sha, "loaded_files": loaded, "route": frozen["route"],
                            "source_files": frozen["source_files"], "python_libraries": frozen["python_libraries"]}
        results[mode] = {"summary_sha256": inputs[str(cell / "summary.json")]["sha256"],
            "observation_sha256": raw_sha, "dataset_sha256": dataset_sha, "loaded_files": loaded,
            "operations": count, "mix": dict(mix), "all_expected_values_matched": True,
            "dispatch": {"maximum_ns": max(lags), "mean_ns": sum(lags) / count,
                         "p50_ns": percentile(lags, .5), "p95_ns": percentile(lags, .95), "p99_ns": percentile(lags, .99),
                         "above_50ms": sum(value > 50000000 for value in lags),
                         "above_100ms": sum(value > 100000000 for value in lags),
                         "span_ns": last_row["dispatch_ns"] - first_row["dispatch_ns"],
                         "largest_five": [row for _, _, row in sorted(top, reverse=True)]},
            "arrival_latency_ns": {"p50": percentile(latencies, .5), "p95": percentile(latencies, .95), "p99": percentile(latencies, .99)},
            "successful_per_second": summary["successful_per_second"], "measurement_window": metadata["measurement_window_ns"],
            "policy_gc_collections": deltas, "policy_process": policy["process"],
            "policy_scope_started_ns": policy["scope_started_ns"], "policy_scope_finished_ns": policy["scope_finished_ns"],
            "restored_gc_stats": restored["stats"],
            "generator_resources": resource_projection,
            "generator_resource_endpoint_source_lines": sorted(retained),
            "last_generator_resource_observation_ns": max(row["time_ns"] for row in previous.values()),
            "application_resources": {phase: {key: value.get(key) for key in
                ("samples", "cpu_seconds", "cpu_percent_one_core", "rss_peak_bytes", "error_samples")}
                for phase, value in summary["resources"].items()},
            "idle_duration_ns": summary["phases"]["idle"]["end_ns"] - summary["phases"]["idle"]["start_ns"],
            "supervision_cleanup_passed": True, "durable_counts_before_recovery": 8777,
            "durable_counts_after_recovery": 8809, "recovery_operations": 32}
    check("pair identical dataset, actual loaded binaries, route, source and Python dependency maps",
          comparison["automatic"] == comparison["deferred"])
    auto, deferred = results["automatic"], results["deferred"]
    memory_delta = (deferred["generator_resources"]["scheduler"]["measurement"]["rss_peak_bytes"] -
                    auto["generator_resources"]["scheduler"]["measurement"]["rss_peak_bytes"])
    result = {"schema_version": 1, "task": "Perf-01", "kind": "fixed-before measurement-policy equivalence/resource gate",
        "started_utc": started, "ended_utc": datetime.now(timezone.utc).isoformat(),
        "formal_long_timing_eligible": False, "duration_credit_seconds": 0,
        "short_pair_semantic_and_declared_service_gate_passed": all(row["passed"] for row in checks),
        "long_resource_clearance": "not established by this 17,282-operation pair",
        "product_performance_gain_claimed": False, "cells": results, "checklist": checks, "inputs": inputs,
        "extractor_sha256": digest(Path(__file__)), "scheduler_measurement_peak_rss_delta_bytes": memory_delta,
        "limitations": [
            "One automatic and one deferred process provide a semantic/resource gate, not noise or a product comparison.",
            "The 17,282-entry plan is smaller than the full 259,526-entry long plan.",
            "Deferral has a measured scheduler RSS cost; memory neutrality is not established.",
            "Generator sampling ends with the target, before final A21 replay and wrapper restoration.",
            "No continuous scheduler RSS observation covers all final replay/restoration transients.",
            "Existing independent SQL receipts were validated; no database was restarted or queried by this audit.",
            "Fresh policy-bound DB noise/capacity and prospectively frozen long/resource checks remain necessary."
        ],
        "outputs": {str(path.relative_to(output)): digest(path) for path in output.rglob("*") if path.is_file()}}
    for path, value in inputs.items():
        assert stamp(Path(path)) == value["stat_identity"], "Input changed after audit: " + path
    save(output / "analysis.json", result)
    print(json.dumps({"short_pair_gate_passed": result["short_pair_semantic_and_declared_service_gate_passed"],
        "checks": len(checks), "raw_operations_per_cell": 17282,
        "maximum_dispatch_lag_ns": {mode: value["dispatch"]["maximum_ns"] for mode, value in results.items()},
        "scheduler_rss_peak_delta_bytes": memory_delta, "duration_credit_seconds": 0}))


if __name__ == "__main__":
    main()
