#!/usr/bin/env python3
"""Project existing failed-run evidence; never launch or replay a workload."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
READER_SHA256 = "8034692b643f4dbb1385cd61e25c9d4d6f084d7b71268fec02411b5c2fcdbeb4"
A21_SHA256 = "dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53"
SUMMARY_SHA256 = "e8433d3af096b45ae7d4d5ab01bd5b345a92f053d0d7792db9e517d5bf476f4d"
MAX_OFFENDERS = 4096
RESOURCE_MARGIN_NS = 2_300_000_000


def sha256(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            result.update(chunk)
    return result.hexdigest()


def stamp(path):
    value = path.stat()
    return [value.st_size, value.st_mtime_ns, value.st_ino]


def save(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--reader", required=True, type=Path)
    parser.add_argument("--a21", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run, output = args.run.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    assert sha256(args.reader) == READER_SHA256, "Frozen reader identity mismatch"
    assert sha256(args.a21) == A21_SHA256, "Frozen A21 identity mismatch"
    summary_path, plan_path = run / "summary.json", run / "plan.json"
    assert sha256(summary_path) == SUMMARY_SHA256, "Failed sample identity mismatch"
    summary = json.loads(summary_path.read_text())
    plan = json.loads(plan_path.read_text())
    gate = plan["timing"]["max_dispatch_lag_ns"]
    assert gate == 100_000_000
    assert summary["valid"] is False
    assert summary["invalid_reasons"] == ["generator saturation: dispatch lag"]
    observation_path = run / "observation.json"
    perf01_path = Path(summary["perf01_receipt"]["path"])
    resources_path = perf01_path.parent / "generator-resources.jsonl"
    inputs = [summary_path, plan_path, observation_path, perf01_path, resources_path,
              args.reader.resolve(), args.a21.resolve()]
    before = {str(path): stamp(path) for path in inputs}
    spec = importlib.util.spec_from_file_location("perf01_frozen_json_reader", args.reader)
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)

    rows = 0
    sum_lag = 0
    over50 = 0
    maximum = None
    origin = None
    offending = []
    outcomes = Counter()
    for row in reader.array_records(observation_path, "records"):
        rows += 1
        origin = row["scheduled_ns"] if origin is None else origin
        lag = row["dispatch_ns"] - row["scheduled_ns"]
        sum_lag += lag
        over50 += lag > 50_000_000
        outcomes[row["status"]] += 1
        timing = {key: row[key] for key in
                  ("id", "scheduled_ns", "dispatch_ns", "admission_ns", "completion_ns",
                   "deadline_ns", "attempts", "status")}
        timing["dispatch_lag_ns"] = lag
        timing["scheduled_offset_ns"] = row["scheduled_ns"] - origin
        timing["operation_kind"] = row["value"]["kind"]
        if maximum is None or lag > maximum["dispatch_lag_ns"]:
            maximum = timing
        if lag > gate:
            assert len(offending) < MAX_OFFENDERS, "Diagnostic projection bound exceeded"
            offending.append(timing)
    assert rows == summary["offered"] == summary["successful"] == 259526
    assert outcomes == {"ok": 259526}
    assert len(offending) == 52
    assert [row["id"] for row in offending] == list(range(30352, 30371)) + list(range(148071, 148104))

    groups = []
    for row in offending:
        if not groups or row["id"] != groups[-1]["last_id"] + 1:
            groups.append({"first_id": row["id"], "last_id": row["id"], "count": 0,
                           "first_scheduled_ns": row["scheduled_ns"],
                           "last_scheduled_ns": row["scheduled_ns"],
                           "first_dispatch_ns": row["dispatch_ns"],
                           "last_dispatch_ns": row["dispatch_ns"]})
        group = groups[-1]
        group["last_id"] = row["id"]
        group["last_scheduled_ns"] = row["scheduled_ns"]
        group["last_dispatch_ns"] = row["dispatch_ns"]
        group["count"] += 1
    for group in groups:
        group["dispatch_span_ns"] = group["last_dispatch_ns"] - group["first_dispatch_ns"]
        group["resource_window_start_ns"] = group["first_scheduled_ns"] - RESOURCE_MARGIN_NS
        group["resource_window_end_ns"] = group["last_dispatch_ns"] + RESOURCE_MARGIN_NS
        group["resource_source_line_numbers"] = []

    with (output / "offending-timing-rows.jsonl").open("x", encoding="utf-8") as stream:
        for row in offending:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
    resource_count = 0
    role_counts = Counter()
    with resources_path.open("rb") as source, (output / "generator-resource-brackets.jsonl").open("xb") as sink:
        for line_number, line in enumerate(source, 1):
            assert len(line) <= 4 * 1024**2, "Oversized resource row"
            row = json.loads(line)
            matched = [group for group in groups
                       if group["resource_window_start_ns"] <= row["time_ns"] <= group["resource_window_end_ns"]]
            if not matched:
                continue
            sink.write(line)
            resource_count += 1
            role_counts[row["role"]] += 1
            for group in matched:
                group["resource_source_line_numbers"].append(line_number)
    input_receipts = []
    for path in inputs:
        digest = sha256(path)
        assert stamp(path) == before[str(path)], "Evidence changed during extraction"
        input_receipts.append({"path": str(path), "sha256": digest,
                               "bytes": before[str(path)][0], "stat_identity": before[str(path)]})
    result = {
        "schema_version": 1, "task": "Perf-01", "group": "postgresql", "variant": "before",
        "purpose": "Bounded read-only projection of an already invalid run; no remeasurement or acceptance amendment",
        "accepted": False, "duration_credit_seconds": 0,
        "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": sha256(Path(__file__)), "inputs": input_receipts,
        "frozen_gate_ns": gate, "gate_operator": "dispatch_ns - scheduled_ns > max_dispatch_lag_ns",
        "source_condition": "src/Benchmarks.Harness/nativeweave_bench.py lines 733-734 at the pinned SHA-256",
        "records": rows, "outcome_counts": dict(outcomes), "planned_origin_ns": origin,
        "above_100ms": len(offending), "above_50ms": over50,
        "mean_dispatch_lag_ns": sum_lag / rows, "maximum_dispatch_lag": maximum,
        "groups": groups, "resource_projection_count": resource_count,
        "resource_projection_role_counts": dict(role_counts),
        "resource_scope": "Original JSONL bytes, all roles, 2.3 seconds before first scheduled offender through 2.3 seconds after last dispatched offender",
        "interpretation_limits": [
            "Two in-run dispatch-delay clusters; neither is a startup-only event.",
            "One-hertz resource sampling cannot identify the cause of a subsecond scheduler pause.",
            "The A21 label generator saturation does not establish sustained CPU saturation, GC, or host interference.",
            "No product runtime, workload, gate, or original evidence was changed."
        ],
        "outputs": {name: sha256(output / name) for name in
                    ("offending-timing-rows.jsonl", "generator-resource-brackets.jsonl")}
    }
    save(output / "analysis.json", result)
    print(json.dumps({"status": "completed", "records": rows, "above_100ms": len(offending),
                      "maximum_dispatch_lag_ns": maximum["dispatch_lag_ns"],
                      "resource_rows": resource_count, "accepted": False, "duration_credit_seconds": 0}))


if __name__ == "__main__":
    main()
