#!/usr/bin/env python3
"""Offline, bounded extraction of the failed before gRPC long attempt.

Reuses the frozen post-run reader used by grpc-v5r1-failed-operations-001.
This script does not start workloads or change the original acceptance verdict.
"""
from collections import Counter
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

READER_SHA = "3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82"
RESULT_SHA = "6e6fec1cbca36e7fa0b78afe64323f7d0e3fa35f20b76bc65665462dc72308e8"
CLIENT_SHA = "6bfc40c993b7f02ffd4406606d78b692c298482cc786717cdd05316688a4ea4d"
MAX_OPERATIONS, MAX_FAILURES, MAX_RESOURCE_ROWS = 300_000, 256, 10_000


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def utc_ns(value):
    match = re.fullmatch(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?(?:Z|\+00:00)", value)
    if not match:
        raise ValueError("Unexpected UTC resource timestamp")
    seconds = int(datetime.fromisoformat(match[1]).replace(tzinfo=timezone.utc).timestamp())
    return seconds * 1_000_000_000 + int((match[2] or "").ljust(9, "0"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--nativeweave", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    reader = args.nativeweave.resolve() / "tests/Perf01/verify_long.py"
    if sha(reader) != READER_SHA:
        raise ValueError("Frozen post-run reader differs")
    spec = importlib.util.spec_from_file_location("failure_reader", reader)
    v = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(v)
    require = v.require
    require(not output.exists(), "Choose a fresh extraction output directory")
    cell = root / "perf01-evidence/long/before/grpc-001"
    ev, outer = v.Evidence(cell), v.Evidence(root)
    outer.pin(reader, READER_SHA)
    outer.pin(root / "perf01-build/before/protocols-v2/source/Client/Program.cs", CLIENT_SHA)
    result = v.object_metadata(ev.pin(cell / "result.json", RESULT_SHA), [
        "status", "valid", "service_standard_met", "invalid_reasons", "offered", "successful",
        "outcome_counts", "evidence_sha256", "plan_sha256", "measurement_window", "resources",
        "managed_gc", "native_gauges_maximum", "after_idle_gauges", "retirement", "recovery",
        "full_30_minute_completed_duration", "full_30_minute_valid_load", "route", "workload_kind",
        "idle_owner_and_request_gauges_receded", "scheduled_arrival_rate_per_second", "success_per_second",
    ])
    require(result["status"] == "completed" and result["valid"] is False, "Not the completed invalid attempt")
    hashes = result["evidence_sha256"]
    plan = ev.load("plan.json", result["plan_sha256"])
    count = plan["timing"]["requests"]
    require(count == 230_670 and count <= MAX_OPERATIONS and result["offered"] == count, "Attempt/count differs")
    require(plan["schedule"]["group"] == "grpc" and plan["schedule"]["rate"] == 128.0
            and plan["schedule"]["duration_seconds"] == 1802.0, "Frozen schedule differs")
    lifecycle = ev.load("execution/receipt.json", hashes["execution/receipt.json"])
    closed = ev.load("execution/server/closed.json", hashes["execution/server/closed.json"])
    frequency = lifecycle["client_hello"]["timestamp_frequency"]
    require(frequency == 1_000_000_000, "Unexpected client clock frequency")

    selected, counts, seen = {}, Counter(), bytearray(count)
    first_start, last_start = None, None
    for line, row in enumerate(ev.lines("execution/client/operations.jsonl", hashes["execution/client/operations.jsonl"]), 1):
        identifier = row["id"]
        require(type(identifier) is int, "Client ID type differs")
        if not 0 <= identifier < count:
            continue  # Recorded warmup/recovery calls are outside the measurement ID interval.
        require(not seen[identifier], "Duplicate measurement client ID")
        seen[identifier] = 1
        counts[(row["logical_status"], row["wire_status"], row["correctness_failure"])] += 1
        start = row["started_timestamp"]
        first_start = start if first_start is None else min(first_start, start)
        last_start = start if last_start is None else max(last_start, start)
        if row["logical_status"] != "ok" or row["correctness_failure"]:
            require(len(selected) < MAX_FAILURES, "Failure count exceeds bounded extraction")
            selected[identifier] = {"client_source_line": line, "client": row, "events": []}
    require(sum(seen) == count, "Missing measurement client rows")
    logical_counts = Counter()
    for (logical, wire, correctness), number in counts.items():
        logical_counts[logical] += number
    require(dict(logical_counts) == result["outcome_counts"], "Client/result outcome counts differ")
    require(logical_counts == {"ok": 230_647, "rejected": 17, "cancelled": 5, "failed": 1}, "Selected attempt outcomes differ")
    require(len(selected) == 23, "Non-ok selection differs")

    for name, key in [("requests.jsonl", "controller"), ("dispatches.jsonl", "dispatch")]:
        rows = 0
        for line, row in enumerate(ev.lines(name, hashes[name]), 1):
            rows += 1
            require(rows <= MAX_OPERATIONS, "Controller ledger exceeds bound")
            identifier = row["id"]
            if identifier in selected:
                require(key not in selected[identifier], "Duplicate selected " + key)
                selected[identifier][key] = row
                selected[identifier][key + "_source_line"] = line
        require(rows == count, "Controller ledger count differs")
    event_rows = 0
    for line, row in enumerate(ev.lines("events.jsonl", hashes["events.jsonl"]), 1):
        event_rows += 1
        require(event_rows <= MAX_OPERATIONS * 3, "Event ledger exceeds bound")
        wire = json.loads(row["wire"])
        if wire.get("id") in selected:
            target = selected[wire["id"]]["events"]
            require(len(target) < 8, "Too many events for selected operation")
            target.append({"source_line": line, "record": row, "parsed_wire": wire})
    entries = 0
    for identifier, row in enumerate(v.array_records(ev.pin(cell / "oracle.json", plan["oracle"]["sha256"]))):
        entries += 1
        require(entries <= MAX_OPERATIONS, "Oracle exceeds bound")
        if identifier in selected:
            require(row["input"] == row["expected"], "Oracle fixture contract differs")
            fields = row["input"].split("|")
            client = selected[identifier]["client"]
            require(len(fields) == 4 and fields[:2] == [client["scenario"], client["protocol"]], "Oracle/client scenario differs")
            selected[identifier]["oracle"] = row
    require(entries == count, "Oracle count differs")

    for identifier, row in selected.items():
        require(all(key in row for key in ("controller", "dispatch", "oracle")), "Missing selected join")
        client, controller, dispatch = row["client"], row["controller"], row["dispatch"]
        require(controller["status"] == client["logical_status"], "Controller/client status differs")
        require(all(dispatch[key] == controller[key] for key in ("scheduled_ns", "dispatch_ns")), "Dispatch/controller timestamps differ")
        require(controller["value"] == row["oracle"]["input"], "Controller/oracle token differs")
        events = {event["parsed_wire"]["kind"]: event for event in row["events"]}
        require(len(row["events"]) == 2 and set(events) == {"admitted", "completed"}, "Selected event sequence differs")
        require(events["admitted"]["record"]["observed_ns"] == controller["admission_ns"], "Admission join differs")
        require(events["completed"]["record"]["observed_ns"] == controller["completion_ns"], "Completion join differs")
        require(events["completed"]["parsed_wire"]["status"] == client["logical_status"], "Completion status differs")
        header = client["failure"] == "Wait headers were not committed."
        row["classification"] = {
            "kind": "required_initial_header_assertion" if header else "explicit_grpc_status",
            "underlying_terminal_status_available": not header,
            "recorded_grpc_status": None if header else client["wire_status"],
            "cause": "unavailable; no failing grant or per-request ledger is recorded",
        }
        row["timing"] = {
            "client_start_seconds_from_first_measurement_start": (client["started_timestamp"] - first_start) / frequency,
            "client_completion_seconds_from_first_measurement_start": (client["completed_timestamp"] - first_start) / frequency,
            "client_elapsed_ms": (client["completed_timestamp"] - client["started_timestamp"]) * 1000 / frequency,
            "dispatch_lag_ms": (dispatch["dispatch_ns"] - dispatch["scheduled_ns"]) / 1e6,
            "controller_arrival_to_completion_ms": (controller["completion_ns"] - controller["scheduled_ns"]) / 1e6,
            "dispatch_utc_ns": dispatch["dispatch_utc_ns"],
            "controller_completion_estimated_utc_ns": dispatch["dispatch_utc_ns"] + controller["completion_ns"] - controller["dispatch_ns"],
        }
    integrity = [row for row in selected.values() if row["client"]["correctness_failure"]]
    require(len(integrity) == 1 and integrity[0]["client"]["id"] == 22468
            and integrity[0]["classification"]["kind"] == "required_initial_header_assertion", "Correctness classification differs")

    # Read existing observations only. Bracket each operation by wall-clock time;
    # do not assume Stopwatch origins agree across the client/controller/server.
    resource_samples, resource_counts = {}, {}
    for name, label, time_field in [
        ("execution/server/managed-resources.jsonl", "managed_native", "utc"),
        ("execution/process-resources.jsonl", "process", "utc_ns"),
    ]:
        samples = []
        for line, sample in enumerate(ev.lines(name, hashes[name]), 1):
            require(line <= MAX_RESOURCE_ROWS, "Resource ledger exceeds bounded inspection")
            stamp = utc_ns(sample[time_field]) if time_field == "utc" else sample[time_field]
            samples.append((stamp, line, sample))
        require(samples, "Missing resource observations")
        samples.sort(key=lambda item: item[0])
        resource_counts[name] = len(samples)
        for row in selected.values():
            start = row["timing"]["dispatch_utc_ns"]
            end = row["timing"]["controller_completion_estimated_utc_ns"]
            before = [item for item in samples if item[0] <= start][-1:]
            during = [item for item in samples if start < item[0] < end]
            after = [item for item in samples if item[0] >= end][:1]
            require(before and after and len(during) <= 64, "Unbracketed or oversized resource interval")
            refs = []
            for position, items in [("before_dispatch", before), ("during_operation", during), ("after_completion", after)]:
                for stamp, line, sample in items:
                    key = label + ":" + str(line)
                    resource_samples[key] = {"source": name, "source_line": line, "utc_ns": stamp, "record": sample}
                    refs.append({"sample": key, "position": position,
                                 "milliseconds_from_dispatch": (stamp - start) / 1e6,
                                 "milliseconds_from_completion": (stamp - end) / 1e6})
            row.setdefault("resource_observation_refs", {})[label] = refs

    # Descriptive clusters use a stated one-second gap, not an acceptance rule.
    clusters = []
    for row in sorted(selected.values(), key=lambda item: item["client"]["started_timestamp"]):
        if not clusters or row["client"]["started_timestamp"] - clusters[-1][-1]["client"]["started_timestamp"] > frequency:
            clusters.append([])
        clusters[-1].append(row)
    cluster_summary = [{
        "ids": [row["client"]["id"] for row in cluster],
        "first_client_start_seconds": min(row["timing"]["client_start_seconds_from_first_measurement_start"] for row in cluster),
        "last_client_start_seconds": max(row["timing"]["client_start_seconds_from_first_measurement_start"] for row in cluster),
        "last_client_completion_seconds": max(row["timing"]["client_completion_seconds_from_first_measurement_start"] for row in cluster),
        "outcomes": dict(Counter(row["client"]["logical_status"] for row in cluster)),
    } for cluster in clusters]
    verifier_name = "perf01-evidence/long/before/grpc-001-verification.json"
    execution_name = "perf01-run/before-grpc-long-001-rejection-verifier-execution.json"
    verifier = outer.load(verifier_name)
    verifier_execution = outer.load(execution_name)
    require(verifier["accepted"] is False and verifier["duration_credit_seconds"] == 0
            and verifier["evidence_sha256"]["result.json"] == RESULT_SHA, "Rejection receipt differs")
    require(verifier_execution["exit_code"] == 1 and verifier_execution["long_duration_credit_seconds"] == 0, "Verifier execution differs")
    log = outer.pin(Path(verifier_execution["log"]), verifier_execution["log_sha256"])
    receipt = {
        "schema_version": 1, "task": "Perf-01", "scope": "offline extraction; original invalid verdict unchanged",
        "cell": str(cell), "reader_sha256": READER_SHA, "extractor_sha256": sha(Path(__file__)),
        "actual_client_source_sha256": CLIENT_SHA, "rate_per_second": 128.0, "configured_duration_seconds": 1802.0,
        "long_duration_credit_seconds": 0, "measured_client_rows": sum(seen),
        "client_outcomes": [dict(logical_status=key[0], wire_status=key[1], correctness_failure=key[2], count=number)
                            for key, number in sorted(counts.items())],
        "recorded_correctness_failures": {"required_initial_header_assertions": 1, "payload_or_protobuf_mismatch": 0,
                                          "note": "No claim is made about unreceived payloads. The one header failure remains invalid."},
        "client_measurement_start_span_seconds": (last_start - first_start) / frequency,
        "failure_cluster_start_gap_seconds": 1, "failure_clusters": cluster_summary,
        "last_non_ok_client_completion_seconds": max(row["timing"]["client_completion_seconds_from_first_measurement_start"] for row in selected.values()),
        "last_non_ok_measurement_id": max(selected),
        "later_measurement_ids_all_ok_count": count - max(selected) - 1,
        "original_result": result, "closed": closed,
        "resource_ledger_row_counts": resource_counts, "resource_samples": resource_samples,
        "selected": [selected[key] for key in sorted(selected)],
        "input_sha256": dict(ev.files), "supporting_input_sha256": dict(outer.files),
        "limitations": [
            "The raw driver groups header, protobuf and hash assertions under one correctness-failure label. This extraction retains that invalid verdict and refines only the recorded assertion text.",
            "ResourceExhausted is the recorded gRPC status; no failed native grant, per-request quota ledger, or instantaneous payload ownership trace was captured.",
            "The missing-header assertion occurs before stream reading; the adapter does not retain that call's underlying terminal status/trailers. Nearby status-8 calls do not establish it.",
            "Resource snapshots are separate approximately 1 Hz observations; bracketing does not reconstruct between-sample peaks or establish a causal relationship.",
            "Completion UTC is estimated from the dispatch UTC anchor plus the same controller's monotonic elapsed time. Client relative times use its recorded timestamp frequency.",
            "Warmup and recovery IDs are excluded from measurement counts. This diagnostic gives no valid 30-minute acceptance credit and does not choose a new rate.",
        ],
        "extracted_utc": datetime.now(timezone.utc).isoformat(),
    }
    ev.unchanged()
    outer.unchanged()
    output.mkdir(parents=True, exist_ok=False)
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    for source, name in [(root / verifier_name, "long-verification.json"),
                         (root / execution_name, "long-verifier-execution.json"),
                         (log, "long-verifier-execution.log")]:
        (output / name).write_bytes(source.read_bytes())
    print(json.dumps({"receipt": str(output / "receipt.json"), "outcomes": dict(logical_counts),
                      "clusters": cluster_summary, "resources_selected": len(resource_samples),
                      "duration_credit_seconds": 0}, indent=2))


if __name__ == "__main__":
    main()
