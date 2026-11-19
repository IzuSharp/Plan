#!/usr/bin/env python3
"""Read one completed Perf-01 cell and write a separate, conservative long-run receipt.

This is post-run evidence processing, never a timed driver. All thresholds are
fixed here; an admission event is not treated as a network/codec start event.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re

REQUIRED_NS = 1_800_000_000_000
P99_NS = 500_000_000
RSS_BYTES = 256 * 1024**2
MAX_RECORDS = 1_000_000
PROBES = {"http-cancel", "grpc-cancel", "grpc-deadline"}
HASH = re.compile(r"[0-9a-f]{64}\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value):
    return type(value) is int and value >= 0


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


class JsonStream:
    """Bounded stdlib reader for a top-level array or one array inside an object.

    DB A21 stores records in a JSON array, not JSONL. Skip other containers
    recursively, and decode only one record at a time. No whole ledger is loaded.
    """
    def __init__(self, stream, chunk=65536):
        self.stream, self.chunk = stream, chunk
        self.buffer, self.pos, self.eof = "", 0, False
        self.decoder = json.JSONDecoder()

    def fill(self):
        self.buffer = self.buffer[self.pos:]
        self.pos = 0
        more = self.stream.read(self.chunk)
        self.buffer += more
        self.eof = not more

    def peek(self):
        while True:
            while self.pos < len(self.buffer) and self.buffer[self.pos].isspace():
                self.pos += 1
            if self.pos < len(self.buffer):
                return self.buffer[self.pos]
            if self.eof:
                return ""
            self.fill()

    def take(self, token):
        require(self.peek() == token, "Malformed streamed JSON: expected " + token)
        self.pos += 1

    def value(self):
        self.peek()
        while True:
            try:
                value, end = self.decoder.raw_decode(self.buffer, self.pos)
                # A number can end at a chunk boundary before its remaining digits.
                if end < len(self.buffer) and self.buffer[end] in ",]}: \t\r\n" or self.eof and end == len(self.buffer):
                    self.pos = end
                    return value
            except json.JSONDecodeError:
                pass
            require(not self.eof, "Truncated or invalid streamed JSON value")
            require(len(self.buffer) - self.pos <= 4 * 1024**2, "Oversized evidence record")
            self.fill()

    def skip(self, depth=0):
        require(depth < 64, "Evidence JSON nesting exceeds bound")
        first = self.peek()
        if first not in ("[", "{"):
            self.value()
            return
        close = "]" if first == "[" else "}"
        self.take(first)
        if self.peek() != close:
            while True:
                if first == "{":
                    require(isinstance(self.value(), str), "JSON object key is not a string")
                    self.take(":")
                self.skip(depth + 1)
                if self.peek() == close:
                    break
                self.take(",")
        self.take(close)

    def array(self):
        self.take("[")
        if self.peek() != "]":
            while True:
                yield self.value()
                if self.peek() == "]":
                    break
                self.take(",")
        self.take("]")


def array_records(path, key=None, metadata=None):
    with path.open(encoding="utf-8") as stream:
        reader = JsonStream(stream)
        if key is None:
            yield from reader.array()
        else:
            found = False
            reader.take("{")
            while reader.peek() != "}":
                name = reader.value()
                require(isinstance(name, str), "JSON object key is not a string")
                reader.take(":")
                if name == key:
                    require(not found, "Duplicate measurement ledger")
                    found = True
                    yield from reader.array()
                elif metadata is not None and name in metadata:
                    metadata[name] = reader.value()
                else:
                    reader.skip()
                if reader.peek() == "}":
                    break
                reader.take(",")
            reader.take("}")
            require(found, "Missing measurement ledger")
        require(reader.peek() == "", "Trailing evidence after JSON document")


class Evidence:
    def __init__(self, root):
        self.root = root.resolve()
        self.files, self.stamps = {}, {}
        self.identities = {}

    def pin(self, path, expected=None):
        path = Path(path).resolve()
        require(path.is_relative_to(self.root), "Evidence input is outside the selected output directory")
        if path not in self.stamps:
            stat = path.stat()
            self.stamps[path] = (stat.st_size, stat.st_mtime_ns, stat.st_ino)
            self.files[str(path.relative_to(self.root))] = digest(path)
        actual = self.files[str(path.relative_to(self.root))]
        if expected is not None:
            require(actual == expected, "Evidence hash mismatch: " + path.name)
        return path

    def load(self, name, expected=None):
        path = self.pin(self.root / name, expected)
        require(path.stat().st_size <= 64 * 1024**2, "Oversized summary; raw ledgers must be streamed")
        value = json.loads(path.read_text())
        require(not isinstance(value, dict) or value.get("formal_timing_eligible") is not False, "Profiling-only evidence is ineligible for long acceptance")
        return value

    def lines(self, name, expected=None):
        path = self.pin(self.root / name, expected)
        with path.open() as stream:
            for line in stream:
                require(len(line) <= 4 * 1024**2, "Oversized JSONL evidence row")
                yield json.loads(line)

    def local(self, recorded, original_root):
        path = Path(recorded)
        relative = path.relative_to(original_root) if path.is_absolute() else path
        return self.pin(self.root / relative)

    def unchanged(self):
        for path, before in self.stamps.items():
            stat = path.stat()
            require(before == (stat.st_size, stat.st_mtime_ns, stat.st_ino), "Input changed during verification: " + path.name)


class Span:
    def __init__(self, expected, period, maximum_lag, first_id=0):
        require(integer(expected) and 100 <= expected <= MAX_RECORDS, "Invalid finite measurement count")
        require(integer(period) and period > 0, "Invalid arrival period")
        require(integer(maximum_lag) and maximum_lag <= 100_000_000, "Dispatch lag policy exceeds 100 ms")
        self.expected, self.period, self.maximum_lag, self.first_id = expected, period, maximum_lag, first_id
        self.seen = bytearray(expected)
        self.count = self.ordinary = self.probes = self.within_slo = 0
        self.first = self.last = self.earliest_completion = self.last_ordinary = None
        self.origin = None
        self.last_completion = self.max_lag = self.lag_over_50ms = 0
        self.reported_span = None

    def add(self, row, ordinary=True):
        identifier = row["id"]
        require(integer(identifier), "Invalid operation ID")
        index = identifier - self.first_id
        require(0 <= index < self.expected and not self.seen[index], "Missing-range or duplicate measurement ID")
        self.seen[index] = 1
        require(row["status"] == "ok", "Measurement contains a non-successful logical operation")
        s, d, a, c = (row[name] for name in ("scheduled_ns", "dispatch_ns", "admission_ns", "completion_ns"))
        require(all(integer(value) for value in (s, d, a, c)) and s <= d <= a <= c, "Invalid or missing controller event ordering")
        if "target_completion_observed_ns" in row:
            require(c == row["target_completion_observed_ns"], "A21 success differs from observed target completion")
        origin = s - index * self.period
        if self.origin is None:
            self.origin = origin
        require(origin == self.origin, "Measurement schedule is not the frozen continuous arrival sequence")
        require(d - s <= self.maximum_lag, "Generator dispatch lag exceeds the frozen policy")
        self.count += 1
        self.within_slo += c - s <= P99_NS
        self.max_lag = max(self.max_lag, d - s)
        self.lag_over_50ms += d - s > 50_000_000
        self.last_completion = max(self.last_completion, c)
        endpoint = {"id": identifier, "scheduled_ns": s, "dispatch_ns": d, "admission_ns": a, "completion_ns": c}
        if self.first is None or d < self.first["dispatch_ns"]:
            self.first = endpoint
        if self.last is None or d > self.last["dispatch_ns"]:
            self.last = endpoint
        if ordinary:
            self.ordinary += 1
            if self.earliest_completion is None or c < self.earliest_completion["completion_ns"]:
                self.earliest_completion = endpoint
            if self.last_ordinary is None or d > self.last_ordinary["dispatch_ns"]:
                self.last_ordinary = endpoint
        else:
            self.probes += 1

    def finish(self):
        require(self.count == self.expected and all(self.seen), "Incomplete measurement ledger")
        require(self.ordinary >= 2, "Insufficient successful ordinary operations for duration proof")
        duration = self.last_ordinary["dispatch_ns"] - self.earliest_completion["completion_ns"]
        original = self.last["dispatch_ns"] - self.first["dispatch_ns"]
        ipc = self.last["dispatch_ns"] - self.first["admission_ns"]
        require(self.reported_span is None or abs(original - self.reported_span) <= 1, "Driver dispatch span differs from raw measurement records")
        return {"offered": self.expected, "successful_logical_checks": self.count,
                "ordinary_successes": self.ordinary, "expected_probe_successes": self.probes,
                "earliest_ordinary_completion": self.earliest_completion, "last_ordinary_dispatch": self.last_ordinary,
                "first_dispatch": self.first, "last_dispatch": self.last,
                "ordinary_operation_lower_bound_ns": duration, "ipc_send_lower_bound_ns": ipc,
                "original_dispatch_start_span_ns": original,
                "driver_reported_dispatch_span_ns": self.reported_span,
                "scheduled_span_ns": (self.expected - 1) * self.period,
                "duration_proved": duration >= REQUIRED_NS and original >= REQUIRED_NS,
                "arrival_p99_at_most_500ms_from_raw": self.within_slo >= (99 * self.count + 99) // 100,
                "maximum_dispatch_start_lag_ns": self.max_lag, "dispatch_start_lag_over_50ms_count": self.lag_over_50ms}


def passed(document, *flags):
    for flag in flags:
        require(document.get(flag) is True, "Required acceptance flag is not true: " + flag)
    require(not document.get("invalid_reasons"), "Original driver invalidated the cell")


def counts(document, expected, names):
    require(all(document.get(key) == expected for key in names), "Driver counts do not equal the full measurement ledger")


def rss_peak(rows, select):
    values = []
    missing = 0
    for row in rows:
        item = select(row)
        if item is False:
            continue
        if isinstance(item, dict) and item.get("availability") == "measured" and integer(item.get("value")):
            values.append(item["value"])
        else:
            missing += 1
    require(values, "No measured application RSS sample in the measurement interval")
    return {"rss_peak_bytes": max(values), "rss_samples": len(values), "rss_unavailable_samples": missing}


def check_db(evidence, group):
    summary = evidence.load("summary.json")
    passed(summary, "valid", "qualifies_service_standard", "duration_valid")
    require(summary["provider"] == group and summary["scenario"] == "mixed" and summary["stage"] == "soak", "Not the selected mixed database soak group")
    require(summary["supervision"] == "completed", "Database supervision did not complete")
    progress = evidence.load("progress.json")
    require(progress["state"] == "completed" and progress["summary_sha256"] == evidence.files["summary.json"], "Database completion receipt differs")
    frozen = evidence.load("frozen-inputs.json", summary["frozen_inputs_sha256"])
    standard = frozen["service_standard"]
    require(standard["max_unexpected_errors"] == 0 and standard["max_p99_ms"] == 500 and standard["max_app_rss_mib"] == 256, "Database frozen service limits differ")
    plan = evidence.load("plan.json", frozen["plan_sha256"])
    require(frozen["planned_load_seconds"] >= 1802, "Missing prospective 1802-second schedule guard")
    target = evidence.load("target.json", plan["routes"][0]["artifacts"][str(Path(plan["oracle"]["dataset"]).parent / "target.json")])
    original_root = Path(plan["oracle"]["dataset"]).parent
    app_path = evidence.local(summary["application_receipt"]["path"], original_root)
    app = evidence.load(app_path, summary["application_receipt"]["sha256"])
    extra_path = evidence.local(summary["perf01_receipt"]["path"], original_root)
    extra = evidence.load(extra_path, summary["perf01_receipt"]["sha256"])
    require(app["status"] == extra["status"] == "passed" and not app["errors"], "Application correctness or diagnostics failed")
    require(app["durable_oracle"]["passed"] is True, "Independent durable oracle did not pass")
    closed = app["closed"]
    require(closed.get("databaseResourcesReleased") is True and closed.get("consumerResourcesReleased") is True and closed.get("serverState") == "Disposed", "Database/application resources did not drain")
    observer = extra["generator_resource_observer"]
    require(observer["status"] == "completed" and not observer.get("errors"), "Generator observer did not complete")
    recovery = extra["phases"]["recovery"]
    require(len(recovery["operations"]) == target["perf01"]["recovery_requests"] >= 32 and all(row["status"] == "ok" for row in recovery["operations"]), "Same-process database recovery failed")
    require(recovery["oracle"]["passed"] is True, "Recovery durable oracle failed")
    idle = extra["phases"]["idle"]
    require(idle["end_ns"] - idle["start_ns"] >= 60_000_000_000, "Database idle observation is incomplete")
    loaded = extra["loaded_files"]
    require(loaded and all(frozen["route"]["artifacts"].get(name) == value["sha256"] for name, value in loaded.items()), "Actual mapped database/application identity differs from frozen artifacts")
    executable = frozen["route"]["command"][0]
    require(executable in loaded, "Actual application executable identity is missing")
    evidence.identities = {"route": summary["route"], "source": frozen["route"]["source"], "loaded_files": loaded,
                           "driver_source_files": frozen["source_files"]}
    metadata = dict.fromkeys(("valid", "invalid_reasons", "offered", "admitted", "completed", "successful", "exit_code"))
    timing = plan["timing"]
    span = Span(timing["requests"], timing["period_ns"], timing["max_dispatch_lag_ns"])
    span.reported_span = round(summary["actual_dispatch_span_seconds"] * 1e9)
    for row in array_records(evidence.pin(evidence.root / "observation.json"), "records", metadata):
        span.add(row)
    passed(metadata, "valid")
    counts(metadata, span.expected, ("offered", "admitted", "completed", "successful"))
    counts(summary, span.expected, ("offered", "successful", "dispatched"))
    require(metadata["exit_code"] == 0, "Database target exit was nonzero")
    resource_name = str((app_path.parent / "application/resources.jsonl").relative_to(evidence.root))
    resource = rss_peak(evidence.lines(resource_name), lambda row: row.get("counters", {}).get("rss_bytes") if row.get("phase") == "measurement" else False)
    return span, resource, summary["p99_ns"]


def check_protocol(evidence, group):
    result = evidence.load("result.json")
    passed(result, "valid", "service_standard_met", "full_30_minute_valid_load", "idle_owner_and_request_gauges_receded")
    require(result["status"] == "completed" and result["exit_code"] == 0, "Protocol process tree did not complete")
    hashes = result["evidence_sha256"]
    plan = evidence.load("plan.json", result["plan_sha256"])
    require(plan["schedule"]["group"] == group and plan["schedule"]["duration_seconds"] >= 1802, "Wrong protocol group or missing 1802-second guard")
    standard = plan["service_standard"]
    require(standard["unexpected_error_rate_maximum"] == 0 and standard["arrival_p99_maximum_ms"] == 500 and standard["whole_process_rss_bytes_maximum"] == RSS_BYTES, "Protocol frozen service limits differ")
    adapter = evidence.load("adapter.json", plan["manifest_sha256"])
    receipt = evidence.load("execution/receipt.json", hashes["execution/receipt.json"])
    require(receipt["status"] == "passed" and not receipt["errors"] and receipt["manifest_sha256"] == plan["manifest_sha256"], "Protocol retirement/identity receipt did not pass")
    closed = receipt["closed"]
    require(closed["status"] == "Completed" and closed["state"] == "Disposed" and all(closed[key] == 0 for key in ("pending_requests", "retained_managed_bytes", "retained_native_bytes")), "Protocol owners did not drain")
    require(receipt["loaded_native_sha256"] == adapter["native_sha256"], "Actual loaded protocol native identity differs")
    require(receipt["client_hello"]["dynamic_code_supported"] is False, "Protocol client was not Native AOT")
    require(plan["route"] != "nativeweave-aot-rust" or receipt["loaded_native_sha256"], "NativeWeave protocol native identity is missing")
    require(result["recovery"]["status"] == "passed" and not result["recovery"]["failures"] and result["recovery"]["calls"] == plan["settings"]["recovery_requests"] >= 32, "Protocol recovery incomplete")
    require(adapter["idle_seconds"] >= 60 and receipt["idle_end_utc_ns"] > receipt["idle_start_utc_ns"], "Protocol idle observation missing")
    evidence.identities = {"route": plan["route"], "comparison_identity_sha256": plan["comparison_identity_sha256"],
                           "artifacts": plan["artifacts"], "loaded_native_sha256": receipt["loaded_native_sha256"]}
    timing = plan["timing"]
    span = Span(timing["requests"], timing["period_ns"], timing["max_dispatch_lag_ns"])
    span.reported_span = result["measurement_window"]["actual_dispatch_span_ns"]
    # One byte per request selects a small frozen token dictionary, not a million Python dicts.
    indices, tokens, token_ids = bytearray(), [], {}
    for entry in array_records(evidence.pin(evidence.root / "oracle.json", plan["oracle"]["sha256"])):
        token = entry["input"]
        require(isinstance(token, str) and token == entry["expected"], "Protocol oracle input/expected mismatch")
        fields = token.split("|")
        require(len(fields) == 4 and fields[0].startswith(group + "-"), "Frozen oracle contains a different protocol group")
        if token not in token_ids:
            require(len(tokens) < 256, "Protocol token vocabulary exceeds bound")
            token_ids[token] = len(tokens); tokens.append(fields)
        indices.append(token_ids[token])
        require(len(indices) <= span.expected, "Protocol oracle exceeds measurement count")
    require(len(indices) == span.expected, "Protocol oracle lacks measurement rows")
    client_seen = bytearray(span.expected)
    for row in evidence.lines("execution/client/operations.jsonl", hashes["execution/client/operations.jsonl"]):
        identifier = row["id"]
        require(integer(identifier), "Invalid independent client ID")
        if identifier >= span.expected:
            require(identifier < span.expected + plan["settings"]["warmup_requests"] + plan["settings"]["recovery_requests"], "Unknown independent client phase ID")
            continue  # Warmup/recovery have separate passed receipts and receive no duration credit.
        require(not client_seen[identifier], "Duplicate independent protocol client result")
        client_seen[identifier] = 1
        fields = tokens[indices[identifier]]
        require(row["logical_status"] == "ok" and row["correctness_failure"] is False and [row["scenario"], row["protocol"]] == fields[:2], "Independent protocol payload/status oracle did not pass")
    require(all(client_seen), "Missing independent protocol client result")
    for row in evidence.lines("requests.jsonl", hashes["requests.jsonl"]):
        identifier = row["id"]
        require(integer(identifier) and identifier < span.expected, "Invalid protocol measurement ID")
        fields = tokens[indices[identifier]]
        require(row["value"] == "|".join(fields), "Controller completion differs from frozen protocol oracle")
        span.add(row, fields[0] not in PROBES)
    counts(result, span.expected, ("offered", "actually_dispatched", "admitted", "completed", "successful"))
    window = result["measurement_window"]
    resource = rss_peak(evidence.lines("execution/process-resources.jsonl", hashes["execution/process-resources.jsonl"]),
                        lambda row: (row.get("server") or {}).get("counters", {}).get("rss_bytes")
                        if window["start_monotonic_ns"] <= row["monotonic_ns"] <= window["end_monotonic_ns"] else False)
    return span, resource, result["histograms"]["arrival_success"]["percentiles_from_exact_samples_ns"]["p99"]


def check_codec(evidence):
    summary = evidence.load("summary.json")
    hashes = summary["files"]
    plan = evidence.load("plan.json", hashes["plan.json"])
    result = evidence.load("result.json", hashes["result.json"])
    passed(summary, "valid")
    passed(result, "valid", "complete", "service_standard_met", "recovery_standard_met")
    require(result["exit_code"] == 0 and result["drained_at_utc"] and result["idle_observation_seconds"] >= 60, "Codec exit/drain/idle observation incomplete")
    require(plan["domain"] == "codec" and plan["duration_seconds"] >= 1802 and plan["action"] == plan["interface"] == "mixed", "Not the frozen mixed codec long group")
    require(isinstance(plan["sequence"], list) and 0 < len(plan["sequence"]) <= MAX_RECORDS, "Missing bounded codec action sequence")
    for key in ("manifest_sha256", "controller_sha256", "a21_sha256", "corpus_manifest_sha256"):
        require(isinstance(plan.get(key), str) and HASH.fullmatch(plan[key]), "Missing codec frozen source/manifest hash")
    require(plan["route"] != "nativeweave" or plan["actual_loaded_native"], "Missing actual codec native identity")
    evidence.identities = {key: plan.get(key) for key in ("source_commit", "route", "manifest_sha256", "controller_sha256", "a21_sha256", "corpus_manifest_sha256", "actual_loaded_native")}
    phases = result["phase_counts"]
    span = Span(phases["measurement"]["planned"], plan["period_ns"], round(plan["max_lag_ms"] * 1e6), phases["warmup"]["planned"])
    span.reported_span = round(result["actual_dispatch_span_seconds"] * 1e9)
    recovery = Counter()
    for row in evidence.lines("operations.jsonl", hashes["operations.jsonl"]):
        if row["phase"] == "recovery":
            recovery[row["outcome"]] += 1
        if row["phase"] != "measurement":
            continue
        require(row["terminal_status"] == row["target"]["status"] == "ok" and row["target"]["id"] == row["id"], "Codec terminal correctness failed")
        require([row["case"], row["action"], row["interface"]] == plan["sequence"][(row["id"] - span.first_id) % len(plan["sequence"])], "Codec action differs from frozen sequence")
        span.add({**row, "status": row["outcome"], "admission_ns": row["admitted_ns"]})
    counts(phases["measurement"], span.expected, ("planned", "sent", "dispatch_attempted", "admitted", "completed", "ok"))
    counts(summary, span.expected, ("offered", "successes"))
    require(recovery["ok"] == phases["recovery"]["planned"] > 0 and sum(recovery.values()) == recovery["ok"], "Codec raw recovery outcomes are incomplete or failed")
    drained = []
    for event in evidence.lines("events.jsonl", hashes["events.jsonl"]):
        if event.get("kind") == "drained":
            drained.append(event)
    require(len(drained) == 1 and drained[0].get("errors", 0) == 0, "Missing or failed codec drained event")
    native = drained[0].get("native")
    require(native is None or all(native[key] == 0 for key in ("live", "capacity", "active")), "Codec result owners did not drain")
    if plan["route"] == "nativeweave":
        require(native is not None, "NativeWeave codec drain counters unavailable")
    end = max(result["scheduled_end_ns"], span.last_completion)
    resource = rss_peak(evidence.lines("resources.jsonl", hashes["resources.jsonl"]),
                        lambda row: row.get("target", {}).get("rss_bytes") if result["scheduled_start_ns"] <= row["observer_ns"] <= end else False)
    return span, resource, summary["arrival_success_ns"]["p99"]


def verify(group, output):
    evidence = Evidence(output)
    receipt = {"schema_version": 1, "task": "Perf-01", "group": group, "output_directory": str(evidence.root),
               "verified_at_utc": datetime.now(timezone.utc).isoformat(), "accepted": False, "duration_credit_seconds": 0,
               "verifier_sha256": digest(Path(__file__)), "required_operation_span_ns": REQUIRED_NS,
               "arrival_p99_limit_ns": P99_NS, "application_rss_limit_bytes": RSS_BYTES, "failure_reasons": [],
               "limitations": ["Post-run consistency check relies on the hashed domain driver's payload, persistence, identity and ownership oracles; it does not replay them.",
                   "Inputs with recorded prior hashes are compared; every consumed input gets a new hash. DB raw records/resources lacking prior hashes are pinned now, not authenticated against arbitrary historical edits.",
                   "Completion-observed to later dispatch-start is a conservative operation-span bound, not an exact wire timestamp or total busy CPU time.",
                   "Application RSS is sampled; unobserved between-sample peaks and physical-host interference cannot be reconstructed.",
                   "This receipt does not by itself establish before/after equivalence, pairing, or five-group coverage.",
                   "Protocol idle duration has a configured wait and wall-clock receipt; it is excluded from effective operation duration.",
                   "SQLite business_retry_attempts=0 means no explicit business retry policy; internal SQLite/sqlx busy-handler retry counts are unavailable."]}
    try:
        for marker in ("profile-driver.json", "postgres-profile-summary.json", "profiling.json"):
            if (evidence.root / marker).exists():
                evidence.load(marker)
        if group == "codec":
            span, resource, p99 = check_codec(evidence)
        elif group in ("http", "grpc"):
            span, resource, p99 = check_protocol(evidence, group)
        else:
            span, resource, p99 = check_db(evidence, group)
        proof = span.finish()
        receipt.update(duration_proof=proof, resources=resource, driver_arrival_p99_ns=p99)
        if not proof["duration_proved"]:
            receipt["failure_reasons"].append("Successful ordinary-operation lower bound or original dispatch span is below 1800 seconds")
        if not proof["arrival_p99_at_most_500ms_from_raw"] or type(p99) not in (int, float) or not math.isfinite(p99) or not 0 <= p99 <= P99_NS:
            receipt["failure_reasons"].append("Arrival p99 service limit is failed or unavailable")
        if resource["rss_peak_bytes"] > RSS_BYTES:
            receipt["failure_reasons"].append("Measured application RSS exceeds 256 MiB")
        evidence.unchanged()
        receipt["accepted"] = not receipt["failure_reasons"]
        if receipt["accepted"]:
            receipt["duration_credit_seconds"] = proof["ordinary_operation_lower_bound_ns"] / 1e9
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, OverflowError) as error:
        receipt["failure_reasons"].append(type(error).__name__ + ": " + str(error))
    receipt.update(evidence_sha256=evidence.files, original_checked_identities=evidence.identities)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=("codec", "http", "grpc", "sqlite", "postgresql"), required=True)
    parser.add_argument("--output", type=Path, required=True, help="Actual completed domain cell directory")
    parser.add_argument("--receipt", type=Path, required=True, help="New receipt path; existing files are never overwritten")
    args = parser.parse_args()
    require(not args.receipt.exists(), "Verification receipt already exists")
    result = verify(args.group, args.output)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    with args.receipt.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True); stream.write("\n")
    print(json.dumps({key: result[key] for key in ("accepted", "group", "duration_credit_seconds", "failure_reasons")}, indent=2))
    raise SystemExit(0 if result["accepted"] else 1)


if __name__ == "__main__":
    main()
