#!/usr/bin/env python3
"""Offline Perf-01 protocol cohorts; never start a service, client or workload.

Read explicit independent processes, keep their full frozen Oracle token keys,
and call unchanged A21 statistics. JSON is authoritative; Markdown summarizes
equal-weight process aggregates and never presents a mean p99 as a pooled p99.
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
import re
import statistics
import sys

BASELINE = "ea5fa528035d025bd7a28698ee7c71194432236c"
MAX_RECORDS = 1_000_000
MAX_CONTROL = 64 * 1024**2
HASH = re.compile(r"[0-9a-f]{64}\Z")
PROBES = {"http-cancel": (True, False, "ExpectedCanceledUpload"),
          "grpc-cancel": (True, False, "ExpectedCanceledStream"),
          "grpc-deadline": (False, True, "ExpectedDeadlineExceeded")}
TOTALS = ("request_messages", "response_messages", "request_payload_bytes", "response_payload_bytes",
          "request_encoded_bytes", "response_encoded_bytes")
DRIVERS = ("tests/Perf01.Protocols/run.py", "tests/Perf01.Protocols/adapter.py", "tests/Perf01.Protocols/affinity.py",
           "src/Benchmarks.Harness/nativeweave_bench.py", "src/Benchmarks.Domain/common.py", "src/Benchmarks.Domain/supervision.py")
METRICS = ("arrival_mean_ns", "arrival_p50_ns", "arrival_p95_ns", "arrival_p99_ns", "successful_calls_per_second",
           "logical_checks_per_second", "request_messages_per_second", "response_messages_per_second",
           "request_payload_bytes_per_second", "response_payload_bytes_per_second",
           "request_encoded_bytes_per_second", "response_encoded_bytes_per_second")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value):
    return type(value) is int and value >= 0


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def small(path):
    require(path.stat().st_size <= MAX_CONTROL, "Oversized control JSON: " + str(path))
    return decode(path.read_text())


def decode(text):
    def number(value):
        result = float(value)
        require(math.isfinite(result), "Nonfinite evidence number")
        return result
    return json.loads(text, parse_float=number, parse_constant=number)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def utc(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(result.tzinfo is not None, "Evidence UTC time lacks its zone")
    return result.astimezone(timezone.utc)


class Inputs:
    def __init__(self, root):
        self.root = root.resolve(strict=True)
        self.hashes, self.stamps = {}, {}

    def pin(self, name, expected=None):
        path = (self.root / name).resolve(strict=True)
        require(path.is_relative_to(self.root) and path.is_file(), "Evidence escaped cell: " + name)
        if name not in self.hashes:
            before = path.stat()
            self.stamps[name] = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            self.hashes[name] = sha(path)
        if expected is not None:
            require(self.hashes[name] == expected, "Frozen evidence hash differs: " + name)
        return path

    def load(self, name, expected=None):
        return small(self.pin(name, expected))

    def lines(self, name, expected):
        with self.pin(name, expected).open() as stream:
            for line in stream:
                require(len(line) <= 4 * 1024**2, "Oversized JSONL row")
                yield decode(line)

    def finish(self):
        for name, expected in self.stamps.items():
            now = (self.root / name).stat()
            require((now.st_dev, now.st_ino, now.st_size, now.st_mtime_ns) == expected,
                    "Evidence changed while reading: " + name)


def artifact(plan, suffix):
    matches = [digest for name, digest in plan["artifacts"].items() if name.endswith("/" + suffix)]
    require(len(matches) == 1 and HASH.fullmatch(matches[0]), "Missing/ambiguous frozen source: " + suffix)
    return matches[0]


def build_identity(plan, adapter, receipt):
    original = Path(plan["build_manifest"])
    expected = plan["artifacts"][str(original)]
    return {"build_manifest": str(original), "build_manifest_sha256": expected,
            "server_executable": adapter["server"], "server_executable_sha256": plan["artifacts"][adapter["server"]],
            "client_executable_sha256": plan["schedule"]["client_executable_sha256"],
            "actual_loaded_native_sha256": receipt["loaded_native_sha256"]}


def optional_build(cell, identity):
    # Paths may differ after restoration; the metadata's original byte hash must not.
    original = Path(identity["build_manifest"])
    restored = Path(cell["directory"]) / "bindings/build.json"
    path = restored if restored.is_file() else original
    if not path.is_file():
        identity["producer_metadata_status"] = "unavailable; original build manifest hash remains pinned"
        return
    require(sha(path) == identity["build_manifest_sha256"], "Producer metadata differs from measured manifest")
    value = small(path)
    require(value["eligible_for_measurement"] is True, "Producer was compilation-only")
    identity.update(producer_metadata_status="hash-verified", producer_metadata_path=str(path),
                    product_source_commit=value.get("product_source_commit"), product_source_dirty=value.get("product_source_dirty"),
                    driver_source_commit=value.get("driver_source_commit", value.get("source_commit")),
                    nativeweave_package_version=value.get("nativeweave_package_version"), toolchain=value["toolchain"],
                    producer_manifests_sha256=value.get("producer_manifests_sha256", {}),
                    package_archives_sha256=value.get("package_archives_sha256", {}),
                    dependency_lock_hashes=value.get("lock_hashes", {}),
                    producer_source_sha256=value.get("driver_source_sha256", {}))
    if value.get("route") == "direct-rust":
        identity["toolchain_contract"] = {"direct_rust": value["toolchain"]}
        return
    native = []
    restored_native = Path(cell["directory"]) / "bindings/native.json"
    for original_name, digest in value["producer_manifests_sha256"].items():
        original_path = Path(original_name)
        if original_path.name != "manifest.json":
            continue
        candidates = [original_path] if original_path.is_file() else []
        if restored_native.is_file() and sha(restored_native) == digest:
            candidates.append(restored_native)
        for candidate in candidates:
            require(sha(candidate) == digest, "Producer manifest no longer matches measured metadata")
            producer = small(candidate)
            if "cargoLockSha256" in producer and "tools" in producer:
                native.append((digest, producer))
    require(native and len({digest for digest, _ in native}) == 1, "Missing/ambiguous native producer metadata")
    digest, producer = native[0]
    require(producer["sourceCommit"] == value["product_source_commit"] and producer["sourceDirty"] is False,
            "Native and managed producing source differs")
    server_hashes = {row["sha256"] for row in producer["assets"] if row["engineId"] == "server"}
    require(set(identity["actual_loaded_native_sha256"].values()) == server_hashes, "Loaded native module differs from producer assets")
    native_contract = {key: producer[key] for key in ("rid", "target", "profile", "cargoLockSha256")}
    native_contract.update(tools={key: {field: item[field] for field in ("version", "sha256")}
                                 for key, item in producer["tools"].items()},
        environment={key: producer["environment"].get(key) for key in ("RUSTFLAGS", "CARGO_ENCODED_RUSTFLAGS", "CARGO_BUILD_JOBS")},
        locked_configuration={key: item for key, item in producer["inputSha256"].items()
                              if key.endswith(("Cargo.toml", "Cargo.lock")) or key == "rust-toolchain.toml" or key.startswith(".cargo/")},
        profiles=[{key: row[key] for key in ("label", "defaultFeatures", "features")} for row in producer["builds"]])
    identity.update(native_producer_manifest_sha256=digest, toolchain_contract={"managed_aot": value["toolchain"], "native": native_contract})


def direct_reference(path, expected):
    require(HASH.fullmatch(expected) and sha(path) == expected, "Direct producer must be explicitly hash-pinned before comparison")
    value = small(path)
    require(value["route"] == "direct-rust" and value["eligible_for_measurement"] is True, "Not a completed direct Rust producer")
    return {"manifest_sha256": expected, "server_executable_sha256": value["artifacts_sha256"][value["server"]],
            "toolchain": value["toolchain"], "source_sha256": value["driver_source_sha256"],
            "dependency_lock_sha256": sorted(value["lock_hashes"].values())}


def producer_signature(cell):
    value = cell["build"]
    return {name: value.get(name) for name in ("server_executable_sha256", "client_executable_sha256",
            "product_source_commit", "product_source_dirty", "nativeweave_package_version")} | {
            "native_content_sha256": sorted(value["actual_loaded_native_sha256"].values()),
            "package_content_sha256": sorted((Path(path).name.lower(), digest) for path, digest in value.get("package_archives_sha256", {}).items()),
            "toolchain_contract": value.get("toolchain_contract")}


def scene(token):
    fields = token.split("|")
    require(len(fields) == 4 and fields[1] in {"http1-tls", "http2-tls"}, "Malformed frozen protocol token")
    require(fields[0] in {"http-tiny", "http-json", "http-upload", "http-download", "http-slow", *PROBES,
                         "grpc-unary", "grpc-server", "grpc-client", "grpc-duplex"}, "Unsupported scenario")
    size, messages = int(fields[2]), int(fields[3])
    require(0 <= size <= 64 * 1024**2 and 1 <= messages <= 1_000_000, "Invalid frozen payload/message bound")
    require(not fields[0].startswith("grpc-") or fields[1] == "http2-tls", "gRPC was not HTTP/2 TLS")
    return {"key": token, "scenario": fields[0], "protocol": fields[1], "configured_payload_bytes": size,
            "configured_messages": messages, "expected_probe": fields[0] in PROBES,
            "offered": 0, "dispatched": 0, "admitted": 0, "controller_outcomes": Counter(), "client_outcomes": Counter(),
            "wire_statuses": Counter(), "client_calls": 0, "correctness_failures": 0, "intentional_cancellations": 0,
            "intentional_deadlines": 0, "successful_logical_checks": 0, "successful_calls": 0,
            "raw_observed_totals": Counter(), "successful_totals": Counter(), "_latencies": array("q")}


def resources(evidence, result, route, hashes):
    observed = {"scope": "whole profile process; never attributable to one scenario", "processes": result.get("resources", {}),
                "managed_gc": result.get("managed_gc"), "native_gauges_maximum": result.get("native_gauges_maximum"),
                "after_idle_gauges": result.get("after_idle_gauges"), "managed_gc_observation": None}
    evidence.pin("execution/process-resources.jsonl", hashes["execution/process-resources.jsonl"])
    if route == "direct-rust":
        observed["managed_gc_status"] = "not applicable to Rust; native allocations are unavailable"
        return observed
    name = "execution/server/managed-resources.jsonl"
    first = last = None
    count = 0
    for row in evidence.lines(name, hashes[name]):
        if row["phase"] != "measurement":
            continue
        require(integer(row["timestamp"]) and integer(row["timestamp_frequency"]) and row["timestamp_frequency"] > 0, "Invalid managed sample clock")
        first = row if first is None else first
        require(row["timestamp"] >= first["timestamp"] and row["timestamp_frequency"] == first["timestamp_frequency"], "Managed sample clock changed")
        last = row
        count += 1
    observed["managed_gc_status"] = "unavailable; fewer than two measurement snapshots"
    if count >= 2 and last["timestamp"] > first["timestamp"]:
        seconds = (last["timestamp"] - first["timestamp"]) / first["timestamp_frequency"]
        allocated = last["managed_allocated_bytes"] - first["managed_allocated_bytes"]
        require(integer(allocated), "Managed allocation counter decreased")
        observed["managed_gc_status"] = "approximate whole-process sampled interval"
        observed["managed_gc_observation"] = {"first_timestamp": first["timestamp"], "last_timestamp": last["timestamp"],
            "timestamp_frequency": first["timestamp_frequency"], "sample_count": count, "seconds": seconds,
            "allocated_bytes_delta": allocated, "allocated_mib_per_second": allocated / (seconds * 1024**2),
            "note": "GC.GetTotalAllocatedBytes(false); partial measurement bracket, not exact bytes/call"}
    return observed


def require_wire_counts(item, row):
    """Successful fixture cardinalities; prefix probe bytes never imply completion."""
    name, size, messages = item["scenario"], item["configured_payload_bytes"], item["configured_messages"]
    if item["expected_probe"]:
        return
    if name.startswith("http-"):
        require(row["request_messages"] == row["response_messages"] == 1, "HTTP success message count differs")
        require(row["request_encoded_bytes"] == row["response_encoded_bytes"] == 0, "HTTP bytes mislabeled as protobuf")
        require(row["request_payload_bytes"] == (size if name == "http-upload" else 0), "HTTP upload byte count differs")
        if name in ("http-download", "http-slow", "http-tiny"):
            require(row["response_payload_bytes"] == (16 if name == "http-tiny" else size), "HTTP response byte count differs")
        else:
            require(0 < row["response_payload_bytes"] <= 8192, "Bounded JSON acknowledgement length differs")
    else:
        counts = {"grpc-unary": (1, 1, size, size), "grpc-server": (1, messages, size, size * messages),
                  "grpc-client": (messages, 1, size * messages, 0), "grpc-duplex": (messages, messages, size * messages, size * messages)}[name]
        require(tuple(row[key] for key in TOTALS[:4]) == counts, "Successful protobuf message/Data byte counts differ")
        require(row["request_encoded_bytes"] >= row["request_payload_bytes"] and row["response_encoded_bytes"] > row["response_payload_bytes"],
                "Observed protobuf encoded sizes are inconsistent")


def read_cell(directory, variant, a21, reader, a21_hash):
    cell = {"directory": str(Path(directory).resolve()), "variant": variant, "eligible": False, "issues": [], "scenarios": {}}
    evidence = None
    try:
        evidence = Inputs(Path(directory))
        result = evidence.load("result.json")
        cell.update(result_sha256=evidence.hashes["result.json"], reported_status=result["status"],
                    reported_valid=result.get("valid"), reported_service_standard_met=result.get("service_standard_met"))
        require(result["status"] == "completed", "Cell is not completed; no partial rows receive comparison credit")
        plan = evidence.load("plan.json", result["plan_sha256"])
        hashes = result["evidence_sha256"]
        adapter = evidence.load("adapter.json", plan["manifest_sha256"])
        profile = evidence.load("profile.json", plan["profile_sha256"])
        receipt = evidence.load("execution/receipt.json", hashes["execution/receipt.json"])
        require(plan["route"] == ("direct-rust" if variant == "direct" else "nativeweave-aot-rust"), "Variant/actual route mismatch")
        require(plan["comparison_identity_sha256"] == result["comparison_identity_sha256"] == canonical(plan["schedule"]), "Comparison identity differs")
        require(artifact(plan, DRIVERS[3]) == a21_hash, "A21 source differs from frozen measured source")
        require(receipt["loaded_native_sha256"] == adapter["native_sha256"], "Actual loaded native identities differ")
        require(receipt["client_hello"]["dynamic_code_supported"] is False, "Independent client was not Native AOT")
        require(plan["route"] != "nativeweave-aot-rust" or receipt["loaded_native_sha256"], "NativeWeave native identity is absent")
        window = result["measurement_window"]
        require(integer(window["elapsed_ns"]) and window["elapsed_ns"] > 0
                and window["end_monotonic_ns"] - window["start_monotonic_ns"] == window["elapsed_ns"], "Invalid measured denominator")
        count = plan["timing"]["requests"]
        require(integer(count) and 0 < count <= MAX_RECORDS, "Invalid finite request count")
        signatures = {"schedule": plan["schedule"], "timing": plan["timing"], "settings": plan["settings"],
                      "histogram": plan["histogram"], "service_standard": plan["service_standard"],
                      "driver_sha256": {name: artifact(plan, name) for name in DRIVERS},
                      "host": {name: result["host"].get(name) for name in ("os", "arch", "kernel", "logical_cpu_count", "cpu", "clock", "cgroup_limits", "affinity")}}
        cell.update(signature=signatures, signature_sha256=canonical(signatures), comparison_identity_sha256=plan["comparison_identity_sha256"],
                    measurement_window=window, build=build_identity(plan, adapter, receipt), resources=resources(evidence, result, plan["route"], hashes),
                    controller_pid=result["controller_pid"], server_pid=receipt["server_pid"], client_pid=receipt["client_pid"])
        ready = receipt.get("affinity", {}).get("ready", {}).get("server", {})
        cell["server_process_identity"] = {"pid": ready.get("pid"), "start_ticks": ready.get("start_ticks")}
        require(cell["server_process_identity"]["pid"] == receipt["server_pid"] and integer(cell["server_process_identity"]["start_ticks"]),
                "Missing actual server PID/start identity")
        optional_build(cell, cell["build"])
        if cell["build"].get("producer_metadata_status") != "hash-verified":
            cell["issues"].append("Measured producer metadata is unavailable")
        if variant == "before" and cell["build"].get("product_source_commit") != BASELINE:
            cell["issues"].append("Baseline producer metadata missing or differs from frozen main commit")
        if variant != "direct" and cell["build"].get("product_source_dirty") is not False:
            cell["issues"].append("Product producer metadata does not establish a clean source")
        if variant != "direct" and (not cell["build"].get("nativeweave_package_version") or not cell["build"].get("package_archives_sha256")):
            cell["issues"].append("Measured package closure identity is incomplete")
        standard = plan["service_standard"]
        require(standard["arrival_p99_maximum_ms"] == 500 and standard["whole_process_rss_bytes_maximum"] == 256 * 1024**2
                and standard["unexpected_error_rate_maximum"] == 0, "Service standard differs from frozen Perf-01 policy")
        for key in ("valid", "service_standard_met", "idle_owner_and_request_gauges_receded"):
            if result.get(key) is not True:
                cell["issues"].append("Original driver did not pass " + key)
        if result.get("exit_code") != 0 or receipt.get("status") != "passed" or receipt.get("errors"):
            cell["issues"].append("Original process/retirement receipt did not pass")
        if result.get("recovery", {}).get("status") != "passed":
            cell["issues"].append("Same-server recovery did not pass")
        if profile.get("formal_timing_eligible") is False or any((evidence.root / marker).exists() for marker in ("profile-driver.json", "profiling.json")):
            cell["issues"].append("Profiling-only cell cannot establish a timing comparison")
        cell["issues"].extend(result.get("invalid_reasons", []))
        tokens, indices = [], array("H")
        token_ids = {}
        for entry in reader.array_records(evidence.pin("oracle.json", plan["oracle"]["sha256"])):
            token = entry["input"]
            require(type(token) is str and token == entry["expected"], "Frozen Oracle input/expected mismatch")
            if token not in token_ids:
                require(len(tokens) < 256, "Too many frozen scenarios")
                token_ids[token] = len(tokens)
                tokens.append(token)
                cell["scenarios"][token] = scene(token)
            indices.append(token_ids[token])
            require(len(indices) <= count, "Oracle has extra operations")
        require(len(indices) == count, "Oracle is incomplete")
        flags, arrivals = bytearray(count), array("q", [-1]) * count
        rows = 0
        for row in evidence.lines("requests.jsonl", hashes["requests.jsonl"]):
            require(integer(row["id"]) and row["id"] == rows and rows < count, "Measurement ID order/count differs")
            item = cell["scenarios"][tokens[indices[rows]]]
            require(row["status"] in a21.OUTCOMES, "Unknown controller outcome")
            item["offered"] += 1
            item["controller_outcomes"][row["status"]] += 1
            require(row["scheduled_ns"] == window["start_monotonic_ns"] + rows * plan["timing"]["period_ns"], "Arrival schedule differs")
            if row["dispatch_ns"] is not None:
                require(integer(row["dispatch_ns"]) and row["dispatch_ns"] >= row["scheduled_ns"], "Invalid dispatch time")
                flags[rows] |= 1
                item["dispatched"] += 1
                if row["dispatch_ns"] - row["scheduled_ns"] > plan["timing"]["max_dispatch_lag_ns"]:
                    cell["issues"].append("Generator dispatch lag exceeded frozen limit")
            if row["admission_ns"] is not None:
                require(flags[rows] & 1 and row["admission_ns"] >= row["dispatch_ns"], "Invalid admission order")
                item["admitted"] += 1
            if row["status"] == "ok":
                require(row["admission_ns"] is not None and row["completion_ns"] >= row["admission_ns"]
                        and row["completion_ns"] == row["target_completion_observed_ns"]
                        and row["completion_ns"] < row["scheduled_ns"] + plan["timing"]["timeout_ns"]
                        and row["value"] == tokens[indices[rows]], "Successful controller row fails ordering/Oracle")
                flags[rows] |= 2
                arrivals[rows] = row["completion_ns"] - row["scheduled_ns"]
            rows += 1
        require(rows == count, "Measurement ledger is incomplete")
        for row in evidence.lines("execution/client/operations.jsonl", hashes["execution/client/operations.jsonl"]):
            identifier = row["id"]
            require(integer(identifier) and identifier < count + plan["settings"]["warmup_requests"] + plan["settings"]["recovery_requests"], "Unknown independent client ID")
            if identifier >= count:
                continue
            require(flags[identifier] & 1 and not flags[identifier] & 4, "Duplicate or undispatched client operation")
            flags[identifier] |= 4
            item = cell["scenarios"][tokens[indices[identifier]]]
            require((row["scenario"], row["protocol"]) == (item["scenario"], item["protocol"]), "Independent client scenario differs")
            require(row["logical_status"] in a21.OUTCOMES, "Unknown independent outcome")
            for field in ("correctness_failure", "intentional_cancellation", "intentional_deadline"):
                require(type(row[field]) is bool, "Invalid independent correctness/probe flag")
            item["client_calls"] += 1
            item["client_outcomes"][row["logical_status"]] += 1
            item["wire_statuses"][row["wire_status"]] += 1
            item["correctness_failures"] += row["correctness_failure"]
            item["intentional_cancellations"] += row["intentional_cancellation"]
            item["intentional_deadlines"] += row["intentional_deadline"]
            for field in TOTALS:
                require(integer(row[field]), "Invalid observed byte/message counter")
                item["raw_observed_totals"][field] += row[field]
            expected = PROBES.get(item["scenario"], (False, False, "HTTP200" if item["scenario"].startswith("http-") else "GrpcOK"))
            good = bool(flags[identifier] & 2 and row["logical_status"] == "ok" and not row["correctness_failure"]
                        and (row["intentional_cancellation"], row["intentional_deadline"], row["wire_status"]) == expected)
            if good:
                require_wire_counts(item, row)
                item["successful_logical_checks"] += 1
                item["_latencies"].append(arrivals[identifier])
                if not item["expected_probe"]:
                    item["successful_calls"] += 1
                    for field in TOTALS:
                        item["successful_totals"][field] += row[field]
        seconds = window["elapsed_ns"] / 1e9
        for item in cell["scenarios"].values():
            values = item.pop("_latencies")
            item["unexpected_errors"] = item["offered"] - item["successful_logical_checks"]
            item["metrics"] = {"arrival_mean_ns": sum(values) / len(values) if values else None,
                **{"arrival_" + label + "_ns": a21.percentile(values, q) for label, q in (("p50", .5), ("p95", .95), ("p99", .99))},
                "successful_calls_per_second": item["successful_calls"] / seconds,
                "logical_checks_per_second": item["successful_logical_checks"] / seconds,
                **{name + "_per_second": item["successful_totals"][name] / seconds for name in TOTALS}}
            item["cpu_rss_gc"] = {"status": "not available per scenario", "see": "resources; shared whole-profile process observation"}
            if item["unexpected_errors"]:
                cell["issues"].append("Unexpected/missing logical result in " + item["key"])
            if not item["expected_probe"] and item["metrics"]["arrival_p99_ns"] is None:
                cell["issues"].append("Fewer than 100 ordinary successes in " + item["key"])
        require(sum(item["offered"] for item in cell["scenarios"].values()) == result["offered"] == count, "Summary offered count differs")
        require(sum(bool(value & 1) for value in flags) == result["actually_dispatched"], "Summary dispatched count differs")
        require(sum(bool(value & 2) for value in flags) == result["successful"], "Summary controller success count differs")
        if sum(bool(value & 4) for value in flags) != result["actually_dispatched"]:
            cell["issues"].append("Dispatched operations lack independent client results")
        evidence.finish()
        cell["eligible"] = not cell["issues"]
    except (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError, OverflowError) as error:
        cell["issues"].append(type(error).__name__ + ": " + str(error))
        cell["scenarios"] = {}
        cell["eligible"] = False
    cell["issues"] = sorted(set(cell["issues"]))
    cell["inputs_sha256"] = evidence.hashes if evidence else {}
    return cell


def triplet(cells):
    require(len(cells) == 3 and len({cell["directory"] for cell in cells}) == 3, "Supply exactly three distinct process directories")
    require(all(cell["eligible"] for cell in cells), "Triplet contains failed/ineligible processes")
    require(len({cell["result_sha256"] for cell in cells}) == 3, "Copied/repeated result bytes are not independent processes")
    require(len({cell["signature_sha256"] for cell in cells}) == 1, "Triplet workload/source/host signatures differ")
    require(len({canonical(producer_signature(cell)) for cell in cells}) == 1, "A route's producer artifacts differ within its triplet")
    require(len({canonical(cell["server_process_identity"]) for cell in cells}) == 3, "Repeated actual server process identity")
    windows = sorted((utc(cell["measurement_window"]["start_utc"]), utc(cell["measurement_window"]["end_utc"])) for cell in cells)
    require(all(start < end for start, end in windows) and all(windows[index - 1][1] <= windows[index][0] for index in range(1, len(windows))),
            "Independent process measurement windows overlap")


def aggregate(values):
    present = [value for value in values if finite(value)]
    complete = len(present) == len(values) == 3
    return {"process_values": values, "observed_processes": len(present), "mean": statistics.mean(present) if complete else None,
            "minimum": min(present) if complete else None, "maximum": max(present) if complete else None}


def delta(old, new):
    if not finite(old) or not finite(new):
        return {"absolute": None, "percent": None}
    return {"absolute": new - old, "percent": 100 * (new - old) / old if old else None}


def grouped(cells, key):
    selected = [cell["scenarios"].get(key) for cell in cells]
    metrics = {name: aggregate([row["metrics"][name] if row else None for row in selected]) for name in METRICS}
    return {"metrics": metrics, "unexpected_errors": sum(row["unexpected_errors"] for row in selected) if all(selected) else None,
            "offered": sum(row["offered"] for row in selected) if all(selected) else None,
            "successful_calls": sum(row["successful_calls"] for row in selected) if all(selected) else None,
            "successful_logical_checks": sum(row["successful_logical_checks"] for row in selected) if all(selected) else None,
            "raw_observed_totals": {field: sum(row["raw_observed_totals"][field] for row in selected) if all(selected) else None for field in TOTALS},
            "successful_totals": {field: sum(row["successful_totals"][field] for row in selected) if all(selected) else None for field in TOTALS}}


def whole_profile(cohorts):
    def values(cell):
        resource = cell.get("resources", {})
        result = {role + "_" + name: resource.get("processes", {}).get(role, {}).get(name)
                  for role in ("server", "client", "adapter", "controller")
                  for name in ("cpu_seconds", "cpu_percent_one_core", "rss_bytes_maximum", "threads_maximum", "fd_count_maximum", "socket_count_maximum")}
        gc = resource.get("managed_gc") or {}
        result.update({"server_" + name: gc.get(name) for name in ("managed_allocated_bytes_delta", "gen0_delta", "gen1_delta", "gen2_delta",
                                                                "managed_heap_bytes_maximum", "managed_committed_bytes_maximum")})
        result["server_gc_observed_allocated_mib_per_second"] = (resource.get("managed_gc_observation") or {}).get("allocated_mib_per_second")
        return result
    rows = {variant: [values(cell) for cell in cells] for variant, cells in cohorts.items()}
    metrics = {}
    for name in rows["before"][0]:
        routes = {variant: aggregate([row[name] for row in group]) for variant, group in rows.items()}
        metrics[name] = {"routes": routes, "after_minus_before": delta(routes["before"]["mean"], routes["after"]["mean"]),
                         "before_minus_direct": delta(routes["direct"]["mean"], routes["before"]["mean"]),
                         "after_minus_direct": delta(routes["direct"]["mean"], routes["after"]["mean"])}
    return {"scope": "Whole-profile measurements. Aggregates are equal-weight process means; RSS maximum retains the maximum process peak. Rust managed GC is N/A.", "metrics": metrics}


def freeze(cells, a21_hash, reader_hash, direct):
    triplet(cells)
    identity = cells[0]["comparison_identity_sha256"]
    source = canonical([cell["result_sha256"] for cell in cells])
    native = cells[0]["build"]["toolchain_contract"]["native"]
    require(direct["toolchain"]["rustc"].strip() == native["tools"]["rustc"]["version"].strip()
            and direct["toolchain"]["isa"] == "x86-64-default", "Direct Rust compiler/ISA differs from locked native producer")
    bands = {}
    for key, item in cells[0]["scenarios"].items():
        if item["expected_probe"]:
            continue
        values = [cell["scenarios"][key]["metrics"]["arrival_mean_ns"] for cell in cells]
        bands[key] = {"baseline_id": "Perf-01/protocol/" + identity + "/" + key + "/" + source,
                      "absolute_noise_ns": max(1000, max(values) - min(values)), "relative_noise": 0}
    return {"schema_version": 1, "task": "Perf-01", "kind": "protocol-before-only-noise", "created_utc": datetime.now(timezone.utc).isoformat(),
            "comparison_identity_sha256": identity, "signature_sha256": cells[0]["signature_sha256"],
            "a21_sha256": a21_hash, "stream_reader_sha256": reader_hash, "extractor_sha256": sha(Path(__file__)),
            "seed": 20261119, "method": "max(1000 ns, range of three before process ordinary arrival means); relative noise zero",
            "baseline_product_source_commit": BASELINE, "bands": bands, "before_processes": cells,
            "direct_reference": direct,
            "scope": "Only this exact profile/arrival/CPU/fixture/source cohort; never another mix or scenario in isolation"}


def compare(cohorts, noise, a21, a21_hash, reader_hash):
    issues = []
    all_cells = [cell for cells in cohorts.values() for cell in cells]
    for variant, cells in cohorts.items():
        try:
            triplet(cells)
        except ValueError as error:
            issues.append(variant + ": " + str(error))
    require(noise["kind"] == "protocol-before-only-noise" and noise["task"] == "Perf-01" and noise["schema_version"] == 1, "Unknown frozen-noise receipt")
    require(noise["a21_sha256"] == a21_hash and noise["baseline_product_source_commit"] == BASELINE, "Noise source/baseline differs")
    require(noise["stream_reader_sha256"] == reader_hash, "Frozen streaming parser differs")
    require(noise["extractor_sha256"] == sha(Path(__file__)), "Frozen comparison algorithm differs")
    triplet(noise["before_processes"])
    require(all(cell["variant"] == "before" and cell["signature_sha256"] == noise["signature_sha256"] for cell in noise["before_processes"]), "Noise was not frozen from this before-only cohort")
    require(type(noise["seed"]) is int and noise["seed"] == 20261119, "Noise seed differs from frozen algorithm")
    require(all(type(key) is str and finite(band["absolute_noise_ns"]) and band["absolute_noise_ns"] >= 0
                and finite(band["relative_noise"]) and band["relative_noise"] >= 0 and type(band["baseline_id"]) is str and band["baseline_id"]
                for key, band in noise["bands"].items()), "Invalid frozen noise band")
    for key, band in noise["bands"].items():
        baseline = [cell["scenarios"][key] for cell in noise["before_processes"]]
        means = [row["metrics"]["arrival_mean_ns"] for row in baseline]
        require(all(not row["expected_probe"] for row in baseline) and all(finite(value) for value in means), "Noise contains a probe or missing process mean")
        require(band["absolute_noise_ns"] == max(1000, max(means) - min(means)) and band["relative_noise"] == 0,
                "Supplied noise differs from its frozen before-only range algorithm")
    if len({cell["directory"] for cell in all_cells}) != 9 or len({cell.get("result_sha256") for cell in all_cells}) != 9:
        issues.append("The nine directories/results are not distinct independent process cells")
    if any(cell.get("signature_sha256") != noise["signature_sha256"] or cell.get("comparison_identity_sha256") != noise["comparison_identity_sha256"] for cell in all_cells):
        issues.append("One or more cells differ from the frozen profile/source/host signature")
    frozen_producer = producer_signature(noise["before_processes"][0])
    if any("build" not in cell or producer_signature(cell) != frozen_producer for cell in cohorts["before"]):
        issues.append("Before product/package/native identities differ from the frozen noise cohort")
    build_contract = noise["before_processes"][0]["build"]["toolchain_contract"]
    if any(cell.get("build", {}).get("toolchain_contract") != build_contract for cell in cohorts["before"] + cohorts["after"]):
        issues.append("Before/after managed/native toolchains, locked dependencies or build profiles differ")
    for cell in cohorts["direct"]:
        build = cell.get("build", {})
        direct = {"manifest_sha256": build.get("build_manifest_sha256"), "server_executable_sha256": build.get("server_executable_sha256"),
                  "toolchain": build.get("toolchain"), "source_sha256": build.get("producer_source_sha256"),
                  "dependency_lock_sha256": sorted(build.get("dependency_lock_hashes", {}).values())}
        if direct != noise["direct_reference"]:
            issues.append("Direct Rust producer/source/locks differ from the pre-frozen reference")
    if len({canonical(cell.get("server_process_identity")) for cell in all_cells}) != 9:
        issues.append("The nine cells do not identify distinct actual server processes")
    calibration_instances = {canonical(cell["server_process_identity"]) for cell in noise["before_processes"]}
    calibration_results = {cell["result_sha256"] for cell in noise["before_processes"]}
    if any(canonical(cell.get("server_process_identity")) in calibration_instances or cell.get("result_sha256") in calibration_results for cell in all_cells):
        issues.append("Comparison reuses a noise-calibration process; use fresh independent comparison triplets")
    frozen_time = utc(noise["created_utc"])
    require(all(utc(cell["measurement_window"]["end_utc"]) < frozen_time for cell in noise["before_processes"]), "Noise receipt predates its own before observations")
    for cell in cohorts["after"]:
        if "measurement_window" not in cell or utc(cell["measurement_window"]["start_utc"]) <= frozen_time:
            issues.append("Frozen noise does not precede every after measurement; external committed SHA proof is also required")
    windows = sorted((utc(cell["measurement_window"]["start_utc"]), utc(cell["measurement_window"]["end_utc"]))
                     for cell in all_cells if "measurement_window" in cell)
    if any(start >= end for start, end in windows) or any(windows[index][0] < windows[index - 1][1] for index in range(1, len(windows))):
        issues.append("Measurement windows overlap or have invalid UTC ordering on the shared resources")
    ordinary, probes = {}, {}
    keys = sorted({key for cell in all_cells for key in cell["scenarios"]})
    for key in keys:
        info = next(cell["scenarios"][key] for cell in all_cells if key in cell["scenarios"])
        row = {name: info[name] for name in ("scenario", "protocol", "configured_payload_bytes", "configured_messages", "expected_probe")}
        row["routes"] = {variant: grouped(cells, key) for variant, cells in cohorts.items()}
        if info["expected_probe"]:
            row["scope"] = "Expected control probes; actual observed bytes can be a prefix and are excluded from business throughput"
            probes[key] = row
            continue
        row["changes"] = {}
        for metric in METRICS:
            values = {variant: row["routes"][variant]["metrics"][metric]["mean"] for variant in cohorts}
            row["changes"][metric] = {"after_minus_before": delta(values["before"], values["after"]),
                                      "before_minus_direct": delta(values["direct"], values["before"]),
                                      "after_minus_direct": delta(values["direct"], values["after"])}
        eligible = not issues and key in noise["bands"]
        row["comparative_interpretation_eligible"] = eligible
        row["noise"] = (a21.noise_comparison(row["routes"]["before"]["metrics"]["arrival_mean_ns"]["process_values"],
                                            row["routes"]["after"]["metrics"]["arrival_mean_ns"]["process_values"], noise["bands"][key], noise["seed"])
                        if eligible else {"decision": "inconclusive", "reason": "Cohort failed eligibility or lacks its pre-frozen ordinary-scenario band"})
        ordinary[key] = row
    if not ordinary:
        issues.append("No ordinary scenarios are available for comparison")
    return {"schema_version": 1, "task": "Perf-01", "kind": "protocol-comparison", "created_utc": datetime.now(timezone.utc).isoformat(),
            "status": "completed", "comparative_interpretation_eligible": not issues and all(row["comparative_interpretation_eligible"] for row in ordinary.values()),
            "issues": sorted(set(issues)), "a21_sha256": a21_hash, "cohorts": cohorts, "ordinary_scenarios": ordinary, "expected_probes": probes,
            "whole_profile_resources": whole_profile(cohorts),
            "executed_order": sorted(({"variant": cell["variant"], "directory": cell["directory"],
                                       "start_utc": cell["measurement_window"]["start_utc"], "end_utc": cell["measurement_window"]["end_utc"]}
                                      for cell in all_cells if "measurement_window" in cell), key=lambda row: utc(row["start_utc"])),
            "aggregation": "Equal weight per independent process. Aggregate p50/p95/p99 are means of three process percentiles, with vectors/ranges; never pooled percentiles.",
            "scope": "Successful scenario rates share their whole-profile measurement denominator; CPU/RSS/GC are available only for whole processes. No capacity or long-duration acceptance is inferred."}


def shown(value, scale=1):
    return "N/A" if not finite(value) else format(value / scale, ".6g")


def markdown(report):
    lines = ["# Perf-01 protocol comparison", "", "Interpretation eligible: **" + str(report["comparative_interpretation_eligible"]).lower() + "**.", "",
             report["aggregation"], "", report["scope"], "", "## Ordinary operations", "",
             "| Frozen scenario / protocol / payload bytes / messages | Route | Success/s | Mean ms | Mean process p50 / p95 / p99 ms | Unexpected errors | Request / response messages/s | Request / response MiB/s |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for key, row in report["ordinary_scenarios"].items():
        for variant, route in row["routes"].items():
            metric = {name: value["mean"] for name, value in route["metrics"].items()}
            tails = " / ".join(shown(metric["arrival_" + label + "_ns"], 1e6) for label in ("p50", "p95", "p99"))
            payload = " / ".join(shown(metric[side + "_payload_bytes_per_second"], 1024**2) for side in ("request", "response"))
            messages = " / ".join(shown(metric[side + "_messages_per_second"]) for side in ("request", "response"))
            lines.append("| " + key.replace("|", " / ") + " | " + variant + " | " + shown(metric["successful_calls_per_second"]) + " | "
                         + shown(metric["arrival_mean_ns"], 1e6) + " | " + tails + " | " + shown(route["unexpected_errors"]) + " | " + messages + " | " + payload + " |")
    lines += ["", "## Changes and direct Rust distance", "", "Negative after-minus-before latency means lower latency. Rust gaps use direct Rust as denominator. These are descriptive differences; A21's verdict applies only to independent-process arrival means.", "",
              "| Scenario | After − before mean ms / % | After − before p99 ms / % | Before / after p99 gap to Rust % | A21 mean verdict |",
              "| --- | ---: | ---: | ---: | --- |"]
    for key, row in report["ordinary_scenarios"].items():
        mean = row["changes"]["arrival_mean_ns"]["after_minus_before"]
        tail = row["changes"]["arrival_p99_ns"]
        lines.append("| " + key.replace("|", " / ") + " | " + shown(mean["absolute"], 1e6) + " / " + shown(mean["percent"]) + " | "
                     + shown(tail["after_minus_before"]["absolute"], 1e6) + " / " + shown(tail["after_minus_before"]["percent"]) + " | "
                     + shown(tail["before_minus_direct"]["percent"]) + " / " + shown(tail["after_minus_direct"]["percent"]) + " | " + row["noise"]["decision"] + " |")
    lines += ["", "## Whole-profile process resources", "", "Each row is one process; these values cannot be assigned to an individual scenario. GC allocation rates cover only the observed approximate snapshot bracket.", "",
              "| Route / process | Server CPU % of one core | Sampled peak RSS MiB | GC observed allocation MiB/s | Source / native identity |",
              "| --- | ---: | ---: | ---: | --- |"]
    for variant, cells in report["cohorts"].items():
        for index, cell in enumerate(cells):
            resource = cell.get("resources", {})
            server = resource.get("processes", {}).get("server", {})
            gc = resource.get("managed_gc_observation") or {}
            build = cell.get("build", {})
            source = build.get("product_source_commit") or build.get("driver_source_commit") or "unavailable"
            native = ", ".join(sorted(set(build.get("actual_loaded_native_sha256", {}).values()))) or build.get("server_executable_sha256", "unavailable")
            lines.append("| " + variant + " / " + str(index) + " | " + shown(server.get("cpu_percent_one_core")) + " | "
                         + shown(server.get("rss_bytes_maximum"), 1024**2) + " | " + shown(gc.get("allocated_mib_per_second")) + " | " + source + " / " + native + " |")
    lines += ["", "## Expected control probes", "", "Expected cancellations/deadlines are excluded from business success/byte rates. Observed prefix bytes remain in JSON raw totals.", ""]
    if not report["expected_probes"]:
        lines.append("No expected probes were present in the selected ordinary-only profile.")
    else:
        lines += ["| Probe | Route | Successful checks | Unexpected errors | Observed request / response payload bytes |", "| --- | --- | ---: | ---: | ---: |"]
        for key, row in report["expected_probes"].items():
            for variant, route in row["routes"].items():
                values = route["raw_observed_totals"]
                lines.append("| " + key.replace("|", " / ") + " | " + variant + " | " + shown(route["successful_logical_checks"]) + " | "
                             + shown(route["unexpected_errors"]) + " | " + shown(values["request_payload_bytes"]) + " / " + shown(values["response_payload_bytes"]) + " |")
    lines += ["", "## Evidence and limitations", "", "The JSON contains exact cell directories, input hashes, producer/package/native identities, each process's latency/count/rate vectors, actual payload/encoded-byte totals, all resource summaries and failures. Fewer than 100 successes gives no per-process p99. Missing fields stay N/A; a failed process is never replaced by averaging only successful processes."]
    for issue in report["issues"]:
        lines.append("\n- " + issue.replace("\n", " "))
    for variant, cells in report["cohorts"].items():
        for index, cell in enumerate(cells):
            for issue in cell["issues"]:
                lines.append("\n- " + variant + " process " + str(index) + ": " + issue.replace("\n", " "))
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nativeweave", required=True, type=Path, help="Checkout containing unchanged A21 and reviewed tests/Perf01/verify_long.py streaming reader")
    parser.add_argument("--output", required=True, type=Path, help="New directory outside every input cell")
    sub = parser.add_subparsers(dest="command", required=True)
    before = sub.add_parser("freeze-noise")
    before.add_argument("--before", nargs=3, required=True, type=Path)
    before.add_argument("--direct-build", required=True, type=Path, help="Fixed direct producer metadata only; no direct timing enters noise")
    before.add_argument("--direct-build-sha256", required=True)
    comparison = sub.add_parser("compare")
    for name in ("before", "after", "direct"):
        comparison.add_argument("--" + name, nargs=3, required=True, type=Path)
    comparison.add_argument("--noise", required=True, type=Path)
    comparison.add_argument("--noise-sha256", required=True, help="Exact SHA recorded before any after measurement")
    args = parser.parse_args()
    directories = args.before + (args.after + args.direct if args.command == "compare" else [])
    output = args.output.resolve()
    require(not output.exists() and all(not output.is_relative_to(path.resolve()) for path in directories), "Output must be new and outside input cells")
    a21_path = args.nativeweave.resolve() / "src/Benchmarks.Harness/nativeweave_bench.py"
    reader_path = args.nativeweave.resolve() / "tests/Perf01/verify_long.py"
    a21_hash, reader_hash = sha(a21_path), sha(reader_path)
    a21 = module("perf01_compare_a21", a21_path)
    reader = module("perf01_compare_reader", reader_path)
    output.mkdir(parents=True)
    report = {"task": "Perf-01", "status": "failed", "comparative_interpretation_eligible": False,
              "extractor_sha256": sha(Path(__file__)), "a21_sha256": a21_hash, "stream_reader_sha256": reader_hash}
    try:
        cohorts = {"before": [read_cell(path, "before", a21, reader, a21_hash) for path in args.before]}
        report["cohorts"] = cohorts
        if args.command == "freeze-noise":
            report = freeze(cohorts["before"], a21_hash, reader_hash, direct_reference(args.direct_build, args.direct_build_sha256))
            name = "noise.json"
        else:
            require(HASH.fullmatch(args.noise_sha256) and sha(args.noise) == args.noise_sha256, "Pre-frozen noise receipt hash differs")
            for variant in ("after", "direct"):
                cohorts[variant] = [read_cell(path, variant, a21, reader, a21_hash) for path in getattr(args, variant)]
            report = compare(cohorts, small(args.noise), a21, a21_hash, reader_hash)
            report.update(noise_path=str(args.noise.resolve()), noise_sha256=args.noise_sha256, extractor_sha256=sha(Path(__file__)), stream_reader_sha256=reader_hash)
            (output / "comparison.md").write_text(markdown(report))
            name = "comparison.json"
    except (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError, OverflowError) as error:
        report.update(status="failed", comparative_interpretation_eligible=False, failure=type(error).__name__ + ": " + str(error))
        name = "failure.json"
    (output / name).write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(str(output / name))
    return 0 if report.get("kind") == "protocol-before-only-noise" or report.get("comparative_interpretation_eligible") else 2


if __name__ == "__main__":
    raise SystemExit(main())
