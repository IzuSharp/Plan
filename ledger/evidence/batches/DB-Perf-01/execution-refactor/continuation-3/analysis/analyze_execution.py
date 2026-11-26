#!/usr/bin/env python3
"""Read-only DB-Exec-02 phase/load analysis. Never starts a measured process.

The explicit index binds observations to cohorts and host evidence. This file
does not import campaign_admission or assess the historical eight-cell gate.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import gzip
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import re
import subprocess
import sys

sys.dont_write_bytecode = True
COHORTS = ("before", "candidate", "dapper")
PROVIDERS = ("sqlite", "postgresql")
ROW_COUNTS = (1, 100, 1000)
PHASES = ("ConstructTicks", "SubmitToFirstRowTicks", "ReadCompleteTicks", "ReleaseTicks")
OWNER_NAMES = ("Sources", "Sessions", "Operations", "Cursors", "Buffers", "Owners")
MAX_BYTES = 128 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def import_file(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class Helpers:
    def __init__(self, root):
        self.root = root.resolve()
        folder = self.root / "benchmarks/db-perf/analysis"
        sys.path.insert(0, str(folder))
        self.io = import_file("strict_io", folder / "strict_io.py")
        self.raw = import_file("raw_metrics", folder / "raw_metrics.py")
        self.phase = import_file("db_exec_phase_summary", self.root / "benchmarks/db-perf/query-phases/summarize.py")
        self.sources = {str(path.relative_to(self.root)): digest(path.read_bytes()) for path in (
            folder / "strict_io.py", folder / "raw_metrics.py",
            self.root / "benchmarks/db-perf/query-phases/summarize.py")}


@dataclass
class Input:
    path: Path
    stored_hash: str
    content_hash: str
    content: bytes
    value: object

    # The existing phase summarizer only needs read_bytes and str(path).
    # This adapter also permits a losslessly gzipped phase receipt without
    # extracting it or changing the original summarizer.
    def read_bytes(self):
        return self.content

    def __str__(self):
        return str(self.path)

    def identity(self):
        return {"path": str(self.path), "storedSha256": self.stored_hash,
                "contentSha256": self.content_hash, "bytes": len(self.content)}


class Analyzer:
    def __init__(self, index_path, helpers):
        self.helpers = helpers
        self.io, self.raw = helpers.io, helpers.raw
        self.base = index_path.resolve().parent
        self.inputs = {}
        self.index_input = self.read(index_path.resolve())
        self.index = self.index_input.value
        self.hosts = {}

    def read(self, name, expected_sha=None):
        path = Path(name)
        if not path.is_absolute():
            path = self.base / path
        path = path.resolve()
        if path in self.inputs:
            value = self.inputs[path]
        else:
            before = path.stat()
            self.io.need(before.st_size <= MAX_BYTES, "input_size", "Input exceeds the bounded reader: " + str(path))
            stored = path.read_bytes()
            after = path.stat()
            self.io.need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
                         (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns),
                         "input_changed", "Input changed while being read: " + str(path))
            if path.suffix == ".gz":
                import io
                with gzip.GzipFile(fileobj=io.BytesIO(stored)) as stream:
                    content = stream.read(MAX_BYTES + 1)
            else:
                content = stored
            self.io.need(len(content) <= MAX_BYTES, "decoded_size", "Decoded JSON exceeds the bounded reader")
            json_lines = path.name.removesuffix(".gz").endswith(".jsonl")
            parsed = [self.io.strict_json(line) for line in content.splitlines() if line.strip()] if json_lines else self.io.strict_json(content)
            self.io.need(isinstance(parsed, list if json_lines else dict), "input_object", "Expected an object receipt/index or JSONL records")
            value = Input(path, digest(stored), digest(content), content, parsed)
            self.inputs[path] = value
        if expected_sha is not None:
            self.io.need(value.stored_hash == self.io.valid_sha(expected_sha), "input_hash", "Indexed hash differs: " + str(path))
        return value

    @staticmethod
    def issue(result, code, message, level="invalid"):
        result["issues"].append({"level": level, "code": code, "message": str(message)})

    def attempt(self, result, label, action):
        try:
            return action()
        except FileNotFoundError as error:
            self.issue(result, "missing_file", str(error), "missing")
        except self.io.EvidenceError as error:
            self.issue(result, error.code, label + ": " + str(error), "missing" if error.unproven else "invalid")
        except (KeyError, TypeError, ValueError, ArithmeticError, OSError) as error:
            self.issue(result, "invalid_" + label, type(error).__name__ + ": " + str(error))
        return None

    def field(self, data, *names, default=None):
        return self.io.field(data, *names, optional=True, default=default)

    def host(self, name):
        if name in self.hosts:
            return self.hosts[name]
        descriptor = self.index.get("hosts", {}).get(name)
        self.io.need(isinstance(descriptor, dict), "host_binding_missing", "No recorded host evidence for " + str(name), unproven=True)
        record = self.read(descriptor["path"], descriptor.get("sha256"))
        pointers = descriptor.get("identityPointers")
        self.io.need(isinstance(pointers, list) and pointers, "host_identity_missing", "Select actual stable identity fields from the recorded host evidence", unproven=True)
        selected = {}
        for pointer in pointers:
            self.io.need(isinstance(pointer, str) and pointer.startswith("/"), "host_pointer", "Host identity uses JSON Pointer paths")
            value = record.value
            for part in pointer.split("/")[1:]:
                part = part.replace("~1", "/").replace("~0", "~")
                value = value[int(part)] if isinstance(value, list) else value[part]
            self.io.need(value is not None and value != "", "empty_host_identity", "Host identity field is empty")
            selected[pointer] = value
        fingerprint = digest(json.dumps(selected, sort_keys=True, separators=(",", ":")).encode())
        answer = {"name": name, "evidence": record.identity(), "identity": selected,
                  "fingerprint": fingerprint,
                  "bindingScope": "Explicit analysis index binds receipts to recorded host evidence; raw measurement receipts do not serialize host identity."}
        self.hosts[name] = answer
        return answer

    def timing(self, result, entry, data):
        # Absence of a profiler field in an older schema is not itself proof
        # of a clean run. The invocation index must state its instrumentation.
        instrumented = entry.get("instrumented")
        if instrumented is not False:
            self.issue(result, "instrumented" if instrumented else "instrumentation_unbound",
                       "Instrumented observations receive no timing credit." if instrumented else
                       "The index must explicitly bind instrumented=false to the recorded invocation.",
                       "instrumented" if instrumented else "missing")
        for key in ("TimingComparisonEligible", "TimingCredit"):
            if self.field(data, key) is False:
                self.issue(result, "producer_denies_timing", key + " is false", "instrumented")
        if self.field(data, "NativeAllocationProfile") is not None:
            self.issue(result, "native_allocation_profile", "Allocator-profile timings are excluded", "instrumented")
        argv = entry.get("argv", [])
        self.io.need(isinstance(argv, list) and all(isinstance(part, str) for part in argv), "argv_shape", "argv must be a string array")
        if any(part in ("--allocation-profile", "perf", "strace", "valgrind") or
               Path(part).name in ("perf", "strace", "valgrind") for part in argv):
            self.issue(result, "instrumented_invocation", "Recorded argv includes a profiling/tracing command", "instrumented")
        if entry.get("exitCode") is None:
            self.issue(result, "exit_status_missing", "Invocation exitCode is not bound", "missing")
        elif entry["exitCode"] != 0:
            self.issue(result, "process_failed", "Invocation exitCode=" + str(entry["exitCode"]), "failed")
        if self.field(data, "NativeAot") is not True:
            self.issue(result, "not_native_aot", "A real Native AOT receipt is required")
        if self.field(data, "EmptyDriver") is True:
            self.issue(result, "empty_driver", "Empty-driver observations are diagnostics; no subtraction or business timing comparison", "instrumented")

    def invocation(self, result, entry):
        """Bind actual argv/exit status, not the requested plan's presumed success."""
        bound = dict(entry)
        if not entry.get("commandReceipt"):
            self.issue(result, "command_receipt_unbound", "No actual command receipt; index argv/exitCode alone do not prove an executed invocation", "missing")
            return bound
        source = self.read(entry["commandReceipt"], entry.get("commandSha256"))
        command = source.value
        result["invocation"] = {"input": source.identity(), "record": command}
        for key in ("argv", "exitCode"):
            if key in entry:
                self.io.need(entry[key] == command.get(key), "invocation_override", "Index " + key + " differs from the actual command receipt")
            bound[key] = command.get(key)
        if command.get("success") is not True or command.get("timedOut") is not False or command.get("observerErrors"):
            self.issue(result, "observer_failed", "Command failed, timed out, or retained observer errors; see invocation record", "failed")
        start = self.io.natural(command.get("startedMonotonicNs"), "command monotonic start", 1)
        end = self.io.natural(command.get("finishedMonotonicNs"), "command monotonic finish", 1)
        self.io.need(end > start, "command_clock_order", "Command interval is empty or reversed")
        if entry.get("planReceipt"):
            plan = self.read(entry["planReceipt"])
            matches = [item for item in plan.value.get("commands", []) if item.get("name") == command.get("name")]
            self.io.need(len(matches) == 1, "command_plan_binding", "Command name must occur exactly once in its actual runner plan")
            result["invocation"]["plan"] = plan.identity()
            result["invocation"]["plannedCommand"] = matches[0]
            self.io.need(plan.value.get("provider") == entry["provider"], "plan_provider", "Runner plan provider differs from indexed provider")
        runner = None
        if entry.get("runnerReceipt"):
            runner = self.read(entry["runnerReceipt"])
            result["invocation"]["runner"] = {"input": runner.identity(), "record": runner.value}
            if result["invocation"].get("plan"):
                self.io.need(runner.value.get("planSha256") == result["invocation"]["plan"]["storedSha256"], "runner_plan_hash", "Runner's plan hash differs from actual copied plan bytes")
        if entry.get("resources"):
            self.attempt(result, "resources", lambda: self.resources(result, entry, source, runner))
        else:
            self.issue(result, "resource_observer_unbound", "No resource JSONL was bound to this invocation", "note")
        return bound

    def resources(self, result, entry, command_input, runner_input):
        command = command_input.value
        source = self.read(entry["resources"])
        records = source.value
        self.io.need(isinstance(records, list) and records, "resources_empty", "Resource observer JSONL is empty")
        self.io.need(command.get("resourceSamples") == source.path.name, "resource_name_binding", "Command and resource JSONL names differ")
        self.io.need(command.get("files", {}).get(source.path.name) == source.stored_hash,
                     "resource_hash_binding", "Actual JSONL bytes do not match the completed command receipt's file hash")
        previous = 0
        for item in records:
            start = self.io.natural(item.get("monotonicNs"), "resource sample start", 1)
            finish = self.io.natural(item.get("acquiredThroughMonotonicNs"), "resource acquisition end", 1)
            self.io.need(start > previous and finish >= start, "resource_clock_order", "Resource samples are duplicated/reversed")
            self.io.need(command["startedMonotonicNs"] <= start <= finish <= command["finishedMonotonicNs"],
                         "resource_command_interval", "Resource sample falls outside its actual command interval")
            previous = start
        memory = {}
        for name in ("client", "server"):
            complete = [item[name + "Totals"]["sampledRssBytes"] for item in records if item.get(name + "Totals", {}).get("rssComplete") is True]
            memory[name] = {"maximumCompleteSampleRssBytes": max(complete) if complete else None,
                "completeSamples": len(complete), "incompleteOrAbsentSamples": len(records) - len(complete),
                "scope": "Whole-command non-atomic process-tree RSS samples; missing process memory is never zero; this is not a steady-only high-water."}
        lifetime = {key: command.get(key) for key in
            ("processLifetimeUserCpuSeconds", "processLifetimeSystemCpuSeconds", "processLifetimeMaxRssBytes")}
        result["resources"] = {"input": source.identity(), "samples": len(records),
            "firstMonotonicNs": records[0]["monotonicNs"], "lastAcquiredThroughMonotonicNs": records[-1]["acquiredThroughMonotonicNs"],
            "processLifetimeWait4": lifetime, "sampledMemory": memory,
            "observerTicksPerSecond": runner_input.value.get("ticksPerSecond") if runner_input else None,
            "quotaAtFirstSample": records[0].get("guestQuota"), "quotaAtLastSample": records[-1].get("guestQuota"),
            "serverCpuGroupPresent": any(item.get("serverCpuGroup") is not None for item in records),
            "serverCpuScope": "Raw server PID/start-tick CPU records remain in the JSONL. No complete server CPU total is inferred from non-atomic trees or an unavailable cgroup.",
            "scope": "Observer evidence is not an environment admission. Missing cgroup visibility is retained; no historical cgroup/schema gate is applied."}

    def interval_binding(self, result, source):
        invocation = result.get("invocation")
        if not invocation:
            return
        data, command = source.value, invocation["record"]
        if result["kind"] == "phase" and data.get("Windows"):
            frequency = data["StopwatchFrequency"]
            start = min(window["StartedTicks"] for window in data["Windows"]) * 1_000_000_000 // frequency
            end = max(window["FinishedTicks"] for window in data["Windows"]) * 1_000_000_000 // frequency
        elif result["kind"] == "load" and "SteadyStartMonotonicNs" in data:
            start, end = data["SteadyStartMonotonicNs"], data["SteadyEndMonotonicNs"]
        else:
            return
        self.io.need(command["startedMonotonicNs"] <= start < end <= command["finishedMonotonicNs"],
                     "consumer_command_interval", "Consumer's monotonic interval is outside its actual invocation")
        result["invocation"]["consumerIntervalContained"] = True
        if result.get("resources"):
            observations = self.inputs[Path(result["resources"]["input"]["path"])].value
            result["resources"]["samplesFullyWithinConsumerInterval"] = sum(
                start <= item["monotonicNs"] <= item["acquiredThroughMonotonicNs"] <= end for item in observations)

    def failure_sidecars(self, result, entry, receipt):
        candidates = [Path(str(receipt.path) + ".failure.json")]
        candidates += [self.base / path if not Path(path).is_absolute() else Path(path)
                       for path in entry.get("failureReceipts", [])]
        seen = set()
        for path in candidates:
            path = path.resolve()
            if path in seen or not path.exists():
                continue
            seen.add(path)
            failure = self.attempt(result, "failure_receipt", lambda: self.read(path))
            if failure is not None:
                result.setdefault("failureReceipts", []).append({"input": failure.identity(), "record": failure.value})
                self.issue(result, "failure_receipt", "Retained failure receipt: " + str(path), "failed")

    def base_result(self, entry):
        return {key: entry.get(key) for key in ("id", "kind", "cohort", "provider", "rows", "comparisonGroup", "final")} | {"issues": []}

    def phase(self, result, entry, source):
        data = source.value
        rows = self.io.natural(self.io.field(data, "ResultRows"), "phase result rows", 1)
        self.io.need(rows in ROW_COUNTS and rows == entry.get("rows"), "phase_rows", "Indexed and observed phase result rows differ")
        frequency = self.io.natural(self.io.field(data, "StopwatchFrequency"), "phase clock frequency", 1)
        self.io.valid_sha(self.io.field(data, "ExecutableSha256"), "phase executable SHA-256")
        windows = self.io.field(data, "Windows")
        routes = ("dapper-aot",) if entry["cohort"] == "dapper" else ("fluent", "prepared", "host-sql")
        self.io.need(isinstance(windows, list) and windows, "phase_windows", "Phase windows are missing")
        self.io.need(set(window["Route"] for window in windows) == set(routes), "phase_routes", "Unexpected or omitted phase route")
        first = self.io.field(data, "FirstExecutions")
        self.io.need(isinstance(first, list) and len(first) == len(routes), "first_executions", "First executions are missing or have another route cardinality")
        for sample in first + [sample for window in windows for sample in window["Samples"]]:
            self.io.need(sample["Rows"] == rows, "phase_result_cardinality", "A phase sample did not consume the complete result")
            for key in PHASES:
                self.io.natural(sample[key], "phase " + key)
        for route in routes:
            selected = [window for window in windows if window["Route"] == route]
            indexes = [window["Index"] for window in selected]
            self.io.need(len(set(indexes)) == len(indexes), "duplicate_phase_window", "A phase window index is duplicated")
            requested = entry.get("requested", {})
            if "windows" in requested:
                self.io.need(len(selected) == requested["windows"], "phase_requested_windows", "Observed window count differs from the explicitly requested count")
            for window in selected:
                self.io.need(self.io.natural(window["Operations"], "phase operations", 1) == len(window["Samples"]),
                             "phase_sample_population", "Window operations differ from its raw samples")
                if "iterations" in requested:
                    self.io.need(window["Operations"] == requested["iterations"], "phase_requested_iterations", "Observed window operations differ from the requested count")
                for key in ("AllocatedBefore", "AllocatedAfter", "CpuBeforeTicks", "CpuAfterTicks", "ResidentBytes", "PeakResidentBytes", "Gen0", "Gen1", "Gen2", "StartedTicks", "FinishedTicks"):
                    self.io.natural(window[key], "phase window " + key)
                self.io.need(window["FinishedTicks"] > window["StartedTicks"] and window["AllocatedAfter"] >= window["AllocatedBefore"]
                             and window["CpuAfterTicks"] >= window["CpuBeforeTicks"], "phase_cumulative_order", "Phase cumulative endpoints are reversed")
        if entry["cohort"] != "dapper":
            summary = self.helpers.phase.summarize(source)
            pull = self.field(data["Drained"], "PullChannels")
            if entry["cohort"] == "candidate":
                self.io.need(type(pull) is int and pull == 0, "pull_channels_not_drained", "Current candidate must report zero PullChannels")
            elif pull is not None:
                self.io.need(type(pull) is int and pull == 0, "pull_channels_not_drained", "Observed pull owners did not drain")
        else:
            self.io.need(data["ConnectionClosed"] is True, "dapper_connection_open", "Dapper provider connection did not close")
            self.io.need(data["PhysicalConnectionsOpened"] == 1 and data["PostgreSqlMaxAutoPrepare"] == 0,
                         "dapper_phase_connection", "Dapper phase connection/preparation contract changed")
            self.io.need(data["CacheCommand"] is True, "dapper_command_cache", "The locked generated command-factory contract changed")
            scale = 1_000_000 / frequency
            summary = {"routes": [], "firstExecutions": first, "preparationMicroseconds": None}
            for route in routes:
                selected = [window for window in windows if window["Route"] == route]
                samples = [sample for window in selected for sample in window["Samples"]]
                count = len(samples)
                elapsed = sum(window["FinishedTicks"] - window["StartedTicks"] for window in selected)
                allocated = sum(window["AllocatedAfter"] - window["AllocatedBefore"] for window in selected)
                cpu = sum(window["CpuAfterTicks"] - window["CpuBeforeTicks"] for window in selected)
                summary["routes"].append({"route": route, "windows": len(selected), "operations": count,
                    "allocatedBytes": allocated, "bytesPerOperation": allocated / count,
                    "gc": {key: sum(window[key] for window in selected) for key in ("Gen0", "Gen1", "Gen2")},
                    "processCpuSeconds": cpu / 10_000_000, "processCpuMicrosecondsPerOperation": cpu / 10 / count,
                    "windowSecondsIncludingVerification": elapsed / frequency,
                    "operationsPerSecondIncludingVerification": count * frequency / elapsed,
                    "maxObservedWindowRssBytes": max(window["ResidentBytes"] for window in selected),
                    "processLifetimePeakRssBytes": max(window["PeakResidentBytes"] for window in selected),
                    "phases": {key: self.helpers.phase.quantiles([sample[key] for sample in samples], scale) for key in PHASES},
                    "fourPhaseTotal": self.helpers.phase.quantiles([sum(sample[key] for key in PHASES) for sample in samples], scale),
                    "sqlExecutions": None, "protocolSubmissions": None})
        summary["firstExecutionMicrosecondsByRoute"] = {
            route: {key: sample[key] * 1_000_000 / frequency for key in PHASES}
            for route, sample in zip(routes, first, strict=True)}
        for route in summary["routes"]:
            samples = [sample for window in windows if window["Route"] == route["route"] for sample in window["Samples"]]
            route["readAndRelease"] = self.helpers.phase.quantiles(
                [sample["ReadCompleteTicks"] + sample["ReleaseTicks"] for sample in samples], 1_000_000 / frequency)
            route["perWindow"] = [{"index": window["Index"], "operations": window["Operations"],
                "phases": {phase: self.helpers.phase.quantiles([sample[phase] for sample in window["Samples"]], 1_000_000 / frequency) for phase in PHASES}}
                for window in windows if window["Route"] == route["route"]]
        summary["firstExecutionScope"] = "Reported separately; shared setup precedes first executions, which are not independently process-cold."
        summary["allocationScope"] = "Whole-process window total including business results and harness; no phase/framework allocation partition or subtraction."
        summary["releaseScope"] = "Dapper's upstream iterator can retire inside ReadComplete; compare read+release and total as well as the individual phases."
        summary["idleRssBytes"] = None
        summary["unserializedMetrics"] = ["phase-local allocations", "FFI calls", "physical protocol reply waits", "post-idle RSS"]
        result["metrics"] = summary
        result["contract"] = {key: self.field(data, key) for key in ("Sql", "RawTemplate", "ParametersAndResults", "ResultRows", "Contract", "DatabaseVersion", "Versions", "PackageVersion", "ExecutableSha256", "NativeSha256")}
        result["businessValidation"] = {"allSamplesConsumedExpectedRows": True,
            "scope": "Successful phase producers assert every Id/Note/null value; receipts serialize row counts and the declared contract, not every returned value or a result digest.",
            "independentValueDigestPresent": False}

    def load(self, result, entry, source):
        data = source.value
        manifest_input = self.read(entry["workloadManifest"], entry.get("workloadManifestSha256"))
        manifest = manifest_input.value
        selected = self.io.field(data, "ActualCaseIds")
        offered = self.field(data, "OfferedLoad")
        # raw_metrics selects its offered branch from specification.rate.
        # Always pass the observed offered rate through this thin schema
        # adapter; a supplied external rate is checked separately below.
        observed_rate = self.io.field(offered, "RequestsPerSecond") if offered is not None else None
        requested = entry.get("requested", {})
        seconds = requested.get("seconds")
        if seconds is None:
            seconds = self.io.field(offered, "OfferedSeconds") if offered is not None else 0
            self.issue(result, "requested_duration_unbound", "Duration validation uses only the recorded interval; requested.seconds is absent", "note")
        specification = {"workloadCaseIds": selected, "seconds": seconds}
        if offered is not None:
            specification["rate"] = observed_rate
        if "rate" in requested:
            expected_rate = requested["rate"] or None
            self.io.need(expected_rate == observed_rate, "indexed_arrival_rate", "Indexed offered/closed-loop rate differs from the raw ledger")
        elif offered is not None:
            self.issue(result, "requested_rate_unbound", "Offered ledger is internally checked, but requested.rate is not bound to an external invocation", "note")
        for index_key, raw_key in (("concurrency", "Concurrency"), ("queueCapacity", "QueueCapacity"),
                                   ("rows", "RequestedRows"), ("batchRows", "BatchRows")):
            if index_key in requested:
                actual = self.io.field(offered, raw_key) if index_key == "queueCapacity" and offered else self.io.field(data, raw_key)
                self.io.need(actual == requested[index_key], "indexed_workload_setting", "Indexed " + index_key + " differs from the receipt")
        measured = self.raw.measurement(data, specification, manifest)
        client = self.raw.client_metrics(data, measured)
        owners = self.raw.owner_metrics(data, measured, manifest)
        if entry["cohort"] != "dapper":
            pull = self.field(data["Drained"], "PullChannels")
            if entry["cohort"] == "candidate":
                self.io.need(type(pull) is int and pull == 0, "pull_channels_not_drained", "Current candidate must report zero PullChannels")
            elif pull is not None:
                self.io.need(type(pull) is int and pull == 0, "pull_channels_not_drained", "Observed pull owners did not drain")
            owners["pullChannels"] = pull
        normalized = measured["normalized"]
        counts = normalized["counts"]
        # Validate the managed envelope's own series as well as the offered
        # series which the retained arithmetic helper already reconciles.
        series = self.io.field(data, "Seconds")
        self.io.need([self.io.field(item, "Second") for item in series] == list(range(len(series))),
                     "envelope_second_sequence", "Enclosing per-second series has a gap/duplicate")
        for key, population in (("Completed", "succeeded"), ("Failed", "failed"), ("Rows", "rows")):
            self.io.need(sum(self.io.natural(self.io.field(item, key), "second " + key) for item in series) == counts[population],
                         "envelope_second_totals", "Enclosing second counters differ from totals: " + key)
        if offered is not None:
            details = self.io.field(offered, "Seconds")
            self.io.need(len(series) == len(details), "second_envelope_length", "Enclosing and offered second arrays differ")
            for outer, inner in zip(series, details, strict=True):
                self.io.need(all(self.io.field(outer, left) == self.io.field(inner, right)
                                 for left, right in (("Second", "Second"), ("Completed", "Succeeded"), ("Failed", "Failed"), ("Rows", "Rows"))),
                             "second_envelope_values", "Enclosing and offered per-second counters differ")
        idle = client.get("memory", {}).get("retained_after_idle")
        if idle is None:
            self.issue(result, "idle_rss_unrecorded", "This receipt does not record post-drain idle RSS", "note")
        if counts["failed"] or counts["rejected"]:
            self.issue(result, "observed_failures_or_rejections",
                       f"Raw ledger retains {counts['failed']} failed operations and {counts['rejected']} rejected arrivals; no SLO is invented.", "note")
        result["metrics"] = {"measurement": measured, "client": client, "owners": owners,
            "observedAttemptedArrivalRate": counts["attempted"] / normalized["offeredSeconds"] if offered is not None else None,
            "requestedArrivalRate": observed_rate, "requestedOfferedSeconds": self.field(offered, "OfferedSeconds") if offered else None,
            "actualOfferedProducerSeconds": (offered["OfferedEndTicks"] - offered["StartedTicks"]) / offered["TimerFrequency"] if offered else None,
            "actualAttemptRateThroughProducerEnd": counts["attempted"] * offered["TimerFrequency"] / (offered["OfferedEndTicks"] - offered["StartedTicks"]) if offered else None,
            "successfulThroughputThroughDrain": normalized["successOpsPerSecond"],
            "idleRssBytes": idle["rssBytes"] if idle else None,
            "latencyPopulationScope": "service and scheduled response: successes; all_terminal_offered: success+failure; start_delay: all started. Rejected arrivals have no fabricated completion latency.",
            "queueLatencyScope": "start_delay is planned-arrival-to-worker-start, including producer scheduling and queue delay; it is not isolated queue residence.",
            "ffiCalls": None, "physicalProtocolReplyWaits": None}
        queries = {query["name"]: query for query in manifest["queries"]}
        result["contract"] = {"workloadManifest": manifest_input.identity(), "dataset": manifest.get("dataset"),
            "digestAlgorithm": manifest.get("digest"), "selectedCases": selected,
            "businessCases": {name: {key: queries[name].get(key) for key in
                ("parameters", "columns", "expectedRows", "expectedDigest", "materialization", "queryExecutionsPerOperation")}
                for name in selected},
            "actualDiagnosticSql": self.io.field(data, "ActualDiagnosticSql"),
            "expectedResults": self.io.field(data, "ExpectedResults"),
            "settings": {key: self.field(data, key) for key in
                ("Mode", "SessionMode", "TransactionContract", "Concurrency", "WarmupPerWorker", "RequestedRows", "BatchRows", "Tenants", "OrdersPerTenant", "QueryReuseContract", "DatabaseVersion")},
            "offeredRate": observed_rate, "queueCapacity": self.field(offered, "QueueCapacity") if offered else None,
            "scheduling": "offered" if offered is not None else "closed-loop"}
        result["businessValidation"] = {"stickyOracle": measured["oracle"], "allPerCaseRowsReconciled": True,
            "expectedDigestMatchedManifest": True, "scope": "Per-operation result digests are checked by the source-bound sticky oracle; raw aggregate receipts retain expected digests and per-case successful rows."}
        if entry.get("final"):
            self.final_interval(result, entry, data, manifest, measured)

    def final_interval(self, result, entry, data, manifest, measured):
        requested = entry.get("requested", {}).get("seconds")
        series = self.io.field(data, "Seconds")
        missing = [second for second in range(1800) if second >= len(series)]
        no_business = [second for second in range(min(1800, len(series))) if self.io.field(series[second], "Completed") == 0]
        no_rows = [second for second in range(min(1800, len(series))) if self.io.field(series[second], "Rows") == 0]
        observed_names = {item["name"] for item in measured["by_case"] if item["started"] > 0}
        expected_names = {query["name"] for query in manifest["queries"]}
        interval = {"requestedSeconds": requested, "requiredSeconds": 1800,
            "rawSeriesLength": len(series), "missingSeconds": missing,
            "secondsWithoutSuccessfulBusinessProgress": no_business, "secondsWithoutConsumedRows": no_rows,
            "observedCases": len(observed_names), "manifestCases": len(expected_names),
            "missingCases": sorted(expected_names - observed_names), "allRawCountersReconciled": True,
            "startMonotonicNs": measured["boundary"]["start_ns"],
            "offeredEndMonotonicNs": measured["boundary"]["offered_end_ns"],
            "drainedMonotonicNs": measured["boundary"]["drained_ns"],
            "startedUtc": self.io.field(data, "StartedUtc"), "finishedUtc": self.io.field(data, "FinishedUtc"),
            "idleFinishedUtc": self.field(self.field(data, "Idle", default={}) or {}, "FinishedUtc")}
        result["finalInterval"] = interval
        if requested != 1800:
            self.issue(result, "final_duration_binding", "Final request must explicitly bind the user's 1800 seconds")
        if (data["SteadyEndMonotonicNs"] - data["SteadyStartMonotonicNs"]) < 1800 * 1_000_000_000:
            self.issue(result, "short_final_interval", "Raw steady interval is shorter than 1800 seconds")
        if missing or no_business:
            self.issue(result, "final_second_progress", "Every one of seconds 0..1799 must contain successful business progress; zero/missing seconds are retained")
        if len(expected_names) != 35 or expected_names != observed_names:
            self.issue(result, "final_mixed_case_coverage", "The current final task requires the actual 35-case mixed workload, all observed")

    def observation(self, entry):
        result = self.base_result(entry)
        valid = self.attempt(result, "index_entry", lambda: self.validate_entry(entry))
        if not valid:
            result.update(state="invalid", timingCredit=False)
            return result
        entry = self.attempt(result, "invocation", lambda: self.invocation(result, entry)) or entry
        source = self.attempt(result, "receipt", lambda: self.read(entry["receipt"], entry.get("sha256")))
        if source is None:
            self.attempt(result, "failure_sidecars", lambda: self.failure_sidecars(result, entry,
                Input((self.base / entry["receipt"]).resolve(), "", "", b"", {})))
            result.update(state="failed" if any(issue["level"] == "failed" for issue in result["issues"]) else "missing", timingCredit=False)
            return result
        result["input"] = source.identity()
        result["host"] = self.attempt(result, "host", lambda: self.host(entry.get("host")))
        data = source.value
        self.attempt(result, "timing", lambda: self.timing(result, entry, data))
        self.attempt(result, "failure_sidecars", lambda: self.failure_sidecars(result, entry, source))
        if "Observations" in data and ("TimingCredit" in data or "IsTerminating" in data):
            result["failureReceipt"] = data
            self.issue(result, "failure_receipt", "Input is a failure receipt, not a completed measurement", "failed")
        else:
            observed_provider = provider(self.field(data, "Provider"))
            if observed_provider != entry["provider"]:
                self.issue(result, "provider_identity", "Indexed and observed provider differ")
            self.attempt(result, entry["kind"], lambda: self.phase(result, entry, source) if entry["kind"] == "phase" else self.load(result, entry, source))
            self.attempt(result, "interval_binding", lambda: self.interval_binding(result, source))
        blockers = [issue for issue in result["issues"] if issue["level"] != "note"]
        result["timingCredit"] = bool(result.get("metrics")) and not blockers
        levels = {issue["level"] for issue in blockers}
        result["state"] = next((state for state in ("failed", "instrumented", "invalid", "missing") if state in levels),
                               "observed" if result["timingCredit"] else "partial")
        result["metricUse"] = "Eligible for the explicit same-contract comparisons below" if result["timingCredit"] else "Diagnostic arithmetic only; excluded from timing tables and comparative ratios"
        return result

    def validate_entry(self, entry):
        self.io.need(isinstance(entry, dict) and isinstance(entry.get("id"), str) and entry["id"], "entry_id", "Every observation needs an explicit id")
        self.io.need(entry.get("kind") in ("phase", "load"), "entry_kind", "kind must be phase or load")
        self.io.need(entry.get("cohort") in COHORTS and entry.get("provider") in PROVIDERS, "entry_cohort", "Explicit before/candidate/dapper and provider labels are required")
        self.io.need(isinstance(entry.get("receipt"), str) and entry["receipt"], "entry_receipt", "A receipt path is required", unproven=True)
        return True

    def compare_phases(self, observations):
        by_hash = {item["input"]["contentSha256"]: item for item in observations if item.get("kind") == "phase" and item.get("contract") and item["cohort"] != "dapper"}
        by_hash.update({item["input"]["storedSha256"]: item for item in observations if item.get("kind") == "phase" and item.get("contract") and item["cohort"] != "dapper"})
        for item in observations:
            if item.get("kind") != "phase" or item.get("cohort") != "dapper" or not item.get("contract"):
                continue
            contract = item["contract"].get("Contract")
            if not isinstance(contract, dict):
                self.issue(item, "dapper_contract_missing", "Dapper phase receipt lacks the actual Korda receipt binding")
                item.update(timingCredit=False, state="invalid")
                continue
            target = by_hash.get(contract.get("KordaReceiptSha256"))
            checks = {"actualKordaReceiptSha256Matched": target is not None}
            if target is not None:
                other = target["contract"]
                checks.update(providerAndRows=target["provider"] == item["provider"] and target["rows"] == item["rows"],
                    actualKordaExecutableSha256=contract.get("KordaExecutableSha256") == other.get("ExecutableSha256"),
                    actualKordaSql=contract.get("KordaSql") == other.get("Sql"),
                    rawTemplate=contract.get("RawTemplate") == other.get("RawTemplate") == item["contract"].get("RawTemplate"),
                    dapperSqlEqualsRawTemplate=item["contract"].get("Sql") == other.get("RawTemplate"))
            item["dapperContractCheck"] = {"kordaObservation": target["id"] if target else None, "checks": checks}
            if not all(checks.values()):
                self.issue(item, "dapper_phase_binding", "Dapper Contract does not match an actual indexed Korda phase receipt")
                item.update(timingCredit=False, state="invalid")
        comparisons = []
        for left, right in itertools.combinations([item for item in observations if item.get("kind") == "phase" and item.get("contract")], 2):
            if (left["provider"], left["rows"], left.get("comparisonGroup")) != (right["provider"], right["rows"], right.get("comparisonGroup")) or left["cohort"] == right["cohort"]:
                continue
            a, b = left["contract"], right["contract"]
            exact_korda = a.get("Sql") == b.get("Sql") if "dapper" not in (left["cohort"], right["cohort"]) else None
            checks = {"sameRecordedHost": same_host(left, right), "sameRawTemplate": a.get("RawTemplate") == b.get("RawTemplate"),
                "kordaRenderedSqlByteEqual": exact_korda, "sameRows": left["rows"] == right["rows"],
                "databaseVersionEqual": database_version(a.get("DatabaseVersion")) == database_version(b.get("DatabaseVersion")) if database_version(a.get("DatabaseVersion")) and database_version(b.get("DatabaseVersion")) else None,
                "bothTimingEligible": left["timingCredit"] and right["timingCredit"]}
            comparable = checks["sameRecordedHost"] and checks["sameRawTemplate"] and exact_korda is not False and checks["databaseVersionEqual"] is not False and checks["bothTimingEligible"]
            comparisons.append({"left": left["id"], "right": right["id"], "provider": left["provider"], "rows": left["rows"],
                "checks": checks, "comparableRecordedContract": bool(comparable),
                "declaredParametersAndResults": {"left": a.get("ParametersAndResults"), "right": b.get("ParametersAndResults")},
                "sqlScope": "Korda Sql and RawTemplate compared literally. Dapper's accepted input SQL equals RawTemplate; its driver marker rewrite is not mislabeled as identical server wire SQL.",
                "businessScope": "Same source-bound PhaseRow assertions and complete row population; per-result bytes are not serialized.",
                "routeComparisons": phase_ratios(left, right) if comparable else []})
        return comparisons

    def compare_loads(self, observations):
        comparisons = []
        loads = [item for item in observations if item.get("kind") == "load" and item.get("contract")]
        for left, right in itertools.combinations(loads, 2):
            if (left["provider"], left.get("comparisonGroup")) != (right["provider"], right.get("comparisonGroup")) or left["cohort"] == right["cohort"]:
                continue
            a, b = left["contract"], right["contract"]
            semantic = a["businessCases"] == b["businessCases"] and a["digestAlgorithm"] == b["digestAlgorithm"] and a["dataset"] == b["dataset"]
            sql_a, sql_b = a["actualDiagnosticSql"], b["actualDiagnosticSql"]
            common = sorted(set(sql_a) & set(sql_b))
            differing = [{"case": name, "leftSql": sql_a[name], "rightSql": sql_b[name],
                          "leftSha256": digest(sql_a[name].encode()), "rightSha256": digest(sql_b[name].encode())}
                         for name in common if sql_a[name] != sql_b[name]]
            setting_keys = ("Concurrency", "SessionMode", "TransactionContract", "RequestedRows", "BatchRows", "Tenants", "OrdersPerTenant")
            differences = {key: [a["settings"].get(key), b["settings"].get(key)] for key in setting_keys if a["settings"].get(key) != b["settings"].get(key)}
            for key in ("scheduling", "offeredRate", "queueCapacity"):
                if a[key] != b[key]:
                    differences[key] = [a[key], b[key]]
            eligible = semantic and same_host(left, right) and not differences and left["timingCredit"] and right["timingCredit"]
            comparisons.append({"left": left["id"], "right": right["id"], "provider": left["provider"],
                "sameRecordedHost": same_host(left, right), "sameBusinessContract": semantic,
                "rawSqlByteEqual": not differing and set(sql_a) == set(sql_b), "sqlDifferences": differing,
                "sqlCasesOnlyLeft": sorted(set(sql_a) - set(sql_b)), "sqlCasesOnlyRight": sorted(set(sql_b) - set(sql_a)),
                "sqlScope": "ActualDiagnosticSql is the consumer's recorded SQL description; historical statement text differences remain visible. No byte-identical SQL or server trace is inferred from equal business digests.",
                "settingDifferences": differences, "comparableBusinessWorkload": bool(eligible),
                "ratiosRightOverLeft": load_ratios(left, right) if eligible else {}})
        return comparisons

    def final_matrix(self, observations):
        finals = [item for item in observations if item.get("final")]
        cells = []
        for p, cohort in itertools.product(PROVIDERS, ("candidate", "dapper")):
            selected = [item for item in finals if (item["provider"], item["cohort"]) == (p, cohort)]
            cells.append({"provider": p, "cohort": cohort, "observationIds": [item["id"] for item in selected],
                "state": "missing" if not selected else "duplicate" if len(selected) != 1 else
                "complete-raw-evidence" if selected[0]["timingCredit"] and selected[0].get("finalInterval") else selected[0]["state"]})
        pairs = []
        for left, right in itertools.combinations([item for item in finals if item.get("finalInterval")], 2):
            a, b = left["finalInterval"], right["finalInterval"]
            host = same_host(left, right)
            overlap = a["startMonotonicNs"] < b["drainedMonotonicNs"] and b["startMonotonicNs"] < a["drainedMonotonicNs"] if host else None
            wall_end_a = self.raw.timestamp(a["idleFinishedUtc"] or a["finishedUtc"])
            wall_end_b = self.raw.timestamp(b["idleFinishedUtc"] or b["finishedUtc"])
            all_process_overlap = self.raw.timestamp(a["startedUtc"]) < wall_end_b and self.raw.timestamp(b["startedUtc"]) < wall_end_a if host else None
            pairs.append({"left": left["id"], "right": right["id"], "sameRecordedHost": host,
                          "steadyThroughDrainOverlap": overlap, "includingRecordedIdleOverlap": all_process_overlap})
        complete = len(finals) == 4 and all(cell["state"] == "complete-raw-evidence" for cell in cells)
        serial = len(pairs) == 6 and all(pair["sameRecordedHost"] and pair["steadyThroughDrainOverlap"] is False
                                       and pair["includingRecordedIdleOverlap"] is False for pair in pairs)
        return {"scope": "Current user requirement: four serial 1800-second candidate/Dapper cells, two providers. No performance threshold or historical eight-cell acceptance is applied.",
                "cells": cells, "pairwiseIntervals": pairs, "fourCompleteRawReceipts": complete,
                "sameHostAndSerialIncludingRecordedIdle": serial,
                "taskAcceptance": "Not decided by this arithmetic report."}

    def analyze(self):
        entries = self.index.get("observations", [])
        self.io.need(isinstance(entries, list), "index_observations", "observations must be an explicit array")
        ids = [entry.get("id") for entry in entries]
        self.io.need(len(ids) == len(set(ids)), "duplicate_observation_id", "Observation ids must be unique")
        observations = [self.observation(entry) for entry in entries]
        phases = self.compare_phases(observations)
        loads = self.compare_loads(observations)
        matrix = []
        for p, cohort, rows in itertools.product(PROVIDERS, COHORTS, ROW_COUNTS):
            selected = [item for item in observations if (item.get("kind"), item.get("provider"), item.get("cohort"), item.get("rows")) == ("phase", p, cohort, rows)]
            matrix.append({"provider": p, "cohort": cohort, "rows": rows,
                "observationIds": [item["id"] for item in selected],
                "timingEligibleIds": [item["id"] for item in selected if item["timingCredit"]],
                "state": "missing" if not selected else "observed" if any(item["timingCredit"] for item in selected) else "unproven-or-failed"})
        changed = [str(path) for path, item in self.inputs.items() if not path.exists() or digest(path.read_bytes()) != item.stored_hash]
        return {"schemaVersion": 1, "scope": "Read-only same-host execution-path analysis; source/binary provenance remains explicitly bound by the input index. No benchmark execution, inferred threshold, or historical acceptance mutation.",
            "analyzerSha256": digest(Path(__file__).read_bytes()), "index": self.index_input.identity(),
            "reusedHelperSources": self.helpers.sources, "inputFiles": [item.identity() for item in self.inputs.values()],
            "inputsChangedDuringAnalysis": changed, "phaseCoverage": matrix, "observations": observations,
            "phaseComparisons": phases, "loadComparisons": loads, "finalFour": self.final_matrix(observations),
            "allocationAttribution": "All B/op and GC are whole-process totals. Business, harness, framework and driver costs are not separated or blindly subtracted; framework-only zero remains unproven by this report."}


def provider(value):
    return {"Sqlite": "sqlite", "sqlite": "sqlite", "Microsoft.Data.Sqlite.Core": "sqlite",
            "PostgreSql": "postgresql", "PostgreSQL": "postgresql", "postgresql": "postgresql", "Npgsql": "postgresql"}.get(value)


def same_host(left, right):
    return bool(left.get("host") and right.get("host") and left["host"]["fingerprint"] == right["host"]["fingerprint"])


def database_version(value):
    if not isinstance(value, str):
        return None
    found = re.search(r"(?:^|PostgreSQL\s+)(\d+(?:\.\d+){1,2})\b", value)
    return found.group(1) if found else None


def ratio(left, right):
    return right / left if isinstance(left, (int, float)) and left > 0 and isinstance(right, (int, float)) else None


def phase_ratios(left, right):
    output = []
    for a, b in itertools.product(left["metrics"]["routes"], right["metrics"]["routes"]):
        output.append({"leftRoute": a["route"], "rightRoute": b["route"],
            "bytesPerOperation": ratio(a["bytesPerOperation"], b["bytesPerOperation"]),
            "cpuMicrosecondsPerOperation": ratio(a["processCpuMicrosecondsPerOperation"], b["processCpuMicrosecondsPerOperation"]),
            "fourPhaseTotal": {key: ratio(a["fourPhaseTotal"][key], b["fourPhaseTotal"][key]) for key in ("p50Microseconds", "p95Microseconds", "p99Microseconds")},
            "readAndRelease": {key: ratio(a["readAndRelease"][key], b["readAndRelease"][key]) for key in ("p50Microseconds", "p95Microseconds", "p99Microseconds")},
            "definition": "right / left; route identities are explicit; no best-trial selection"})
    return output


def load_ratios(left, right):
    a, b = left["metrics"], right["metrics"]
    output = {"successfulThroughputThroughDrain": ratio(a["successfulThroughputThroughDrain"], b["successfulThroughputThroughDrain"]),
        "managedBytesPerSuccess": ratio(a["client"]["managed"]["bytes_per_success"], b["client"]["managed"]["bytes_per_success"]),
        "cpuSecondsPerSuccess": ratio(a["client"]["cpu"]["seconds_per_success"], b["client"]["cpu"]["seconds_per_success"])}
    for key in ("service", "offered", "all_terminal_offered", "start_delay"):
        ha, hb = a["measurement"]["histograms"].get(key), b["measurement"]["histograms"].get(key)
        if ha and hb:
            output[key] = {name: ratio(ha[name], hb[name]) for name in ("p50_us_upper", "p95_us_upper", "p99_us_upper")}
    return output


def number(value):
    return "未记录" if value is None else f"{value:,.3f}" if isinstance(value, float) else str(value)


def markdown(report):
    lines = ["# DB-Exec-02 执行路径测量分析", "", "本报告只重算原始证据，不运行测量，不设置性能接受阈值。历史八段验收保持独立。", "",
             "## 证据状态", "", "| 观察 | 库 / cohort | 类型 | 状态 | timing credit |", "|---|---|---|---|---|"]
    for item in report["observations"]:
        lines.append(f"| {item['id']} | {item['provider']} / {item['cohort']} | {item['kind']} | {item['state']} | {item['timingCredit']} |")
    missing = [cell for cell in report["phaseCoverage"] if not cell["timingEligibleIds"]]
    lines += ["", "Phase 未具备有效 timing 的格子：" + (", ".join(f"{item['provider']}/{item['cohort']}/{item['rows']}" for item in missing) if missing else "无"), "",
              "## 查询阶段", "", "分位为原始样本的 nearest-rank，单位 μs；first execution 单独保存在 JSON。Dapper 可在 ReadComplete 内完成上游迭代器清理，Release 不能脱离 read+release 与总时间单独比较。", "",
              "| 观察 / route | 行数 | 次数 | 构造 p50/p95/p99 | 首行 p50/p95/p99 | 余行 p50/p95/p99 | 释放 p50/p95/p99 | 总 B/op | GC0/1/2 | CPU μs/op | 峰值 RSS B |", "|---|---:|---:|---|---|---|---|---:|---|---:|---:|"]
    for item in report["observations"]:
        if item["kind"] != "phase" or not item.get("metrics") or not item["timingCredit"]:
            continue
        for route in item["metrics"]["routes"]:
            quantiles = [" / ".join(number(route["phases"][phase][f"p{p}Microseconds"]) for p in (50, 95, 99)) for phase in PHASES]
            lines.append(f"| {item['id']} / {route['route']} | {item['rows']} | {route['operations']} | " + " | ".join(quantiles) + f" | {number(route['bytesPerOperation'])} | " + "/".join(str(route["gc"]["Gen" + str(i)]) for i in range(3)) + f" | {number(route['processCpuMicrosecondsPerOperation'])} | {route['processLifetimePeakRssBytes']} |")
    lines += ["", "## 混合负载", "", "吞吐覆盖已接受请求至 drain；offered 分位与 service 分位使用不同边界。失败和拒绝原样保留；start delay 包含生产者调度与排队，不能称为纯队列驻留时间。", "",
              "| 观察 | 成功 / 失败 / 拒绝 | offered 目标 rate | 实际 attempted rate | 成功 op/s | 总 B/成功 | GC0/1/2 | CPU s | 峰值 RSS B | idle RSS B |", "|---|---|---:|---:|---:|---:|---|---:|---:|---:|"]
    for item in report["observations"]:
        if item["kind"] != "load" or not item.get("metrics") or not item["timingCredit"]:
            continue
        metrics = item["metrics"]; client = metrics["client"]; counts = metrics["measurement"]["normalized"]["counts"]
        lines.append(f"| {item['id']} | {counts['succeeded']} / {counts['failed']} / {counts['rejected']} | {number(metrics['requestedArrivalRate'])} | {number(metrics['actualAttemptRateThroughProducerEnd'])} | {number(metrics['successfulThroughputThroughDrain'])} | {number(client['managed']['bytes_per_success'])} | " + "/".join(str(value) for value in client['managed']['gc_delta_counts']) + f" | {number(client['cpu']['userCpuSeconds'] + client['cpu']['systemCpuSeconds'])} | {client['memory']['process_peak_rss_bytes']} | {number(metrics['idleRssBytes'])} |")
    lines += ["", "| 观察 | population / boundary | 样本数 | p50 μs upper | p95 μs upper | p99 μs upper |", "|---|---|---:|---:|---:|---:|"]
    for item in report["observations"]:
        if item["kind"] == "load" and item.get("metrics") and item["timingCredit"]:
            for name, hist in item["metrics"]["measurement"]["histograms"].items():
                lines.append(f"| {item['id']} | {name} | {hist['samples']} | {number(hist['p50_us_upper'])} | {number(hist['p95_us_upper'])} | {number(hist['p99_us_upper'])} |")
    lines += ["", "## SQL 与业务结果等同性", ""]
    for comparison in report["phaseComparisons"]:
        lines.append(f"- Phase {comparison['left']} ↔ {comparison['right']}：可比较记录契约={comparison['comparableRecordedContract']}；检查={json.dumps(comparison['checks'], ensure_ascii=False)}。")
    for comparison in report["loadComparisons"]:
        lines.append(f"- Load {comparison['left']} ↔ {comparison['right']}：相同业务契约={comparison['sameBusinessContract']}；SQL 逐字相同={comparison['rawSqlByteEqual']}；不同文本 {len(comparison['sqlDifferences'])} 项；可比较业务负载={comparison['comparableBusinessWorkload']}。完整 SQL 差异与配置差异保留在 JSON。")
    lines += ["", "混合负载 SQL 的历史文本差异不会因业务结果 digest 相同而被抹去。FFI 次数和必须等待的协议回复未在这些 receipts 中序列化；SQL 执行与 protocol submission 的实测计数在 JSON 单独保留，不推算 RTT。", "",
              "## 当前四段 1800 秒记录", "", f"四个原始证据完整：{report['finalFour']['fourCompleteRawReceipts']}；同机且含已记录 idle 无重叠：{report['finalFour']['sameHostAndSerialIncludingRecordedIdle']}。", ""]
    for cell in report["finalFour"]["cells"]:
        lines.append(f"- {cell['provider']} / {cell['cohort']}：{cell['state']}；观察={cell['observationIds']}。")
    for item in report["observations"]:
        if item.get("finalInterval"):
            value = item["finalInterval"]
            lines.append(f"- {item['id']}：缺失秒={value['missingSeconds']}；无成功业务进展秒={value['secondsWithoutSuccessfulBusinessProgress']}；无消费行秒={value['secondsWithoutConsumedRows']}；实际 case={value['observedCases']}/{value['manifestCases']}。")
    lines += ["", "## 缺项、失败与限制", ""]
    for item in report["observations"]:
        for issue in item["issues"]:
            lines.append(f"- {item['id']} [{issue['level']}/{issue['code']}]：{issue['message'].replace(chr(10), ' ')}")
    if report["inputsChangedDuringAnalysis"]:
        lines.append("- 分析期间输入发生变化：" + ", ".join(report["inputsChangedDuringAnalysis"]))
    lines += ["", "总 B/op 包括业务对象、字符串/JSON、harness、框架与驱动；GC 按进程计数。该报告不扣除业务结果或 empty-driver，不据此声明框架 0 B。峰值 RSS 是进程生命周期 high-water，idle RSS 是实际 post-drain 观测。", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--korda-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, help="New JSON path; a Markdown sibling is also written")
    args = parser.parse_args()
    markdown_path = args.output.with_suffix(".md")
    if args.output.exists() or markdown_path.exists():
        parser.error("Use fresh JSON and Markdown outputs; previous observations are never overwritten.")
    helpers = Helpers(args.korda_root)
    report = Analyzer(args.index, helpers).analyze()
    try:
        report["helperRepositoryCommit"] = subprocess.check_output(["git", "-C", str(args.korda_root), "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        report["helperRepositoryCommit"] = None
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    markdown_path.write_text(markdown(report))
    print(json.dumps({"json": str(args.output), "markdown": str(markdown_path),
                      "observations": len(report["observations"]),
                      "timingEligible": sum(item["timingCredit"] for item in report["observations"]),
                      "inputsChanged": report["inputsChangedDuringAnalysis"]}, ensure_ascii=False))
    # Missing/instrumented/failed evidence is reported, not silently discarded.
    # The report is an analysis artifact, not a performance acceptance gate.
    return 1 if report["inputsChangedDuringAnalysis"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
