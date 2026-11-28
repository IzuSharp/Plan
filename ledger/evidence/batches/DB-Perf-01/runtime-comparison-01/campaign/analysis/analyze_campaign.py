#!/usr/bin/env python3
"""Offline review of eight completed DB-Runtime-Compare-01 cells. Standard library only.

Never launches workloads, databases, subprocesses, or a plotting library. A shared
nonblocking campaign lock and eight terminal statuses are required before reading
result/resource evidence. Unknown counters remain null. Run only after owner approval.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import sys

SCHEMA = "DB-Runtime-Compare-01.offline-analysis.v1"
IMPLEMENTATIONS = ("dapper", "ef-workstation", "ef-satori", "java-native")
PROVIDERS = ("sqlite", "postgresql")
LABELS = {"dapper": "Dapper.AOT", "ef-workstation": "EF Core JIT Workstation",
          "ef-satori": "EF Core JIT Satori", "java-native": "Java 25 GraalVM Native"}
BIN_COUNT = 8192
# One reviewed historical observation, not a reusable time tolerance.
EXACT_IDLE_ADJUDICATIONS = {
    "02-dapper-postgresql": {
        "resultSha256": "61f45dae1a6a687298e87e81bdae689fa26a9aae88cd25a60d62e8368de6a50c",
        "statusSha256": "9576fc157dbcc8acae8b4515f78ec1f5fe901be8e7379f9d7203d73da32e82c4",
        "reviewFile": "02-idle-deviation-review.json",
        "reviewSha256": "ef2ea3d6f6d7c6afcdab6f64476b45f1d4ff6e84eab45a8e70cb5a2da604d44d",
        "observedIdleSeconds": 14.997119729,
    }
}


def sha_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path):
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def write_new(path, value):
    with Path(path).open("x", encoding="utf-8") as stream:
        if isinstance(value, str):
            stream.write(value)
        else:
            json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.write("\n")


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def divide(numerator, denominator):
    return numerator / denominator if numeric(numerator) and numeric(denominator) and denominator > 0 else None


def difference(after, before):
    return after - before if numeric(after) and numeric(before) else None


def close(a, b, absolute=1e-6, relative=1e-9):
    return numeric(a) and numeric(b) and math.isclose(a, b, abs_tol=absolute, rel_tol=relative)


def maximum(values):
    available = [value for value in values if numeric(value)]
    return max(available) if available else None


def identity(reading):
    return (reading.get("pid"), reading.get("startTicks")) if reading else None


def histogram(histogram, population):
    """128 subdivisions per base-2 nanosecond exponent, identical to both consumers."""
    if not isinstance(histogram, list) or len(histogram) != BIN_COUNT:
        raise ValueError("Histogram must contain exactly 8192 bins")
    if any(type(value) is not int or value < 0 for value in histogram):
        raise ValueError("Histogram bins must be nonnegative integers")
    if type(population) is not int or sum(histogram) != population:
        raise ValueError("Histogram population does not reconcile")
    answer = {"population": population, "unit": "microseconds", "quantileKind": "bin-upper-bound",
              "method": "base-2 nanoseconds; 128 subdivisions/exponent; <0.782% relative bin width"}
    for label, quantile in (("p50", 0.5), ("p95", 0.95), ("p99", 0.99)):
        answer[label] = None
        if population:
            wanted, running = math.ceil(population * quantile), 0
            for index, value in enumerate(histogram):
                running += value
                if running >= wanted:
                    lower = math.ldexp(1.0, index // 128)
                    answer[label] = (lower + lower * ((index % 128 + 1) / 128.0)) / 1000.0
                    break
    return answer


def gc_measurements(result, implementation):
    if implementation == "java-native":
        before, after = result.get("GcBefore") or {}, result.get("GcAfter") or {}
        collectors = {}
        names = sorted(set((before.get("Collectors") or {})) | set((after.get("Collectors") or {})))
        for name in names:
            first = (before.get("Collectors") or {}).get(name, {})
            last = (after.get("Collectors") or {}).get(name, {})
            counts_supported = all(numeric(value) and value >= 0 for value in (last.get("Count"), first.get("Count")))
            times_supported = all(numeric(value) and value >= 0 for value in (last.get("CollectionMilliseconds"), first.get("CollectionMilliseconds")))
            n = difference(last.get("Count"), first.get("Count")) if counts_supported else None
            milliseconds = difference(last.get("CollectionMilliseconds"), first.get("CollectionMilliseconds")) if times_supported else None
            collectors[name] = {"collections": n if n is not None and n >= 0 else None,
                                "collectionMilliseconds": milliseconds if milliseconds is not None and milliseconds >= 0 else None,
                                "rawBefore": first, "rawAfter": last}
        count = difference(after.get("Collections"), before.get("Collections"))
        duration = difference(after.get("CollectionMilliseconds"), before.get("CollectionMilliseconds"))
        return {"api": "GarbageCollectorMXBean", "collections": count if count is not None and count >= 0 else None,
                "collectionMilliseconds": duration if duration is not None and duration >= 0 else None,
                "collectors": collectors, "stopTheWorldPauseSeconds": None,
                "scope": "Process counters between client boundaries. Collection time is not a validated pause histogram; unsupported values remain null.",
                "rawBefore": before, "rawAfter": after}
    ticks = result.get("GcPauseTicks")
    return {"api": "System.GC", "generationCollectionCounts": {"gen0": result.get("Gen0"),
            "gen1": result.get("Gen1"), "gen2": result.get("Gen2")},
            "reportedPauseDurationTicks": ticks,
            "reportedPauseDurationSeconds": ticks / 10_000_000 if numeric(ticks) and ticks >= 0 else None,
            "pauseDurationUnit": "TimeSpan ticks of 100 ns, not Stopwatch ticks",
            "pauseScope": result.get("GcPauseScope") or "Pause duration is absent in the historical Dapper consumer; null is not zero.",
            "scope": "Whole-process GC counters within client boundaries. Generation counts are reported separately, not added. Satori and stock GC pause APIs are not assumed equivalent."}


def memory_measurements(result, command, implementation, policy):
    before, after = result.get("ProcessBefore") or {}, result.get("ProcessAfter") or {}
    idle = result.get("Idle") or {}
    idle_before, idle_after = idle.get("Before") or {}, idle.get("After") or {}
    runtime = result.get("RuntimeIdentity") or {}
    return {"lifetimeWait4MaxRssBytes": command.get("processLifetimeMaxRssBytes"),
            "lifetimeWait4Scope": "OS wait4-reported lifetime maxRSS for the launched process, read at owner wait4. This is a separate counter from consumer ProcessAfter and observer smaps; do not merge their maxima or require a numeric ordering.",
            "clientRssAtSteadyStartBytes": before.get("RssBytes"), "clientRssAtSteadyEndBytes": after.get("RssBytes"),
            "clientReportedPeakThroughSteadyEndBytes": after.get("PeakRssBytes"),
            "clientReportedPeakThroughSteadyEndScope": "Consumer ProcessAfter.PeakRssBytes: high-water value visible in the snapshot taken after the measured workload. Startup/warmup may contribute; this is not a post-exit lifetime reading. Preserve it independently of wait4 and smaps samples.",
            "rssCounterComparisonScope": "Different APIs, scopes and acquisition times can produce differing values. The mechanism behind any difference is unproven here. Do not force wait4 or consumer high-water values above observer RSS; do not form a cross-source maximum or classify the difference as a business error.",
            "releasedIdleRssBeforeBytes": idle_before.get("RssBytes"), "releasedIdleRssAfterBytes": idle_after.get("RssBytes"),
            "releasedIdlePssAfterBytes": idle_after.get("PssBytes"), "releasedIdleObservedSeconds": idle.get("ObservedSeconds"),
            "releasedIdleScope": idle.get("Scope"),
            "requestedCSharpGcHeapBytes": None if implementation == "java-native" else policy.get("csharpRequestedGcHeapBytes"),
            "clientTotalMemoryHardLimitClaimed": False, "cgroupRequired": False,
            "runtimeIdentity": runtime or None,
            "gcReportedAvailableMemoryAtStartupBytes": runtime.get("GcTotalAvailableMemoryBytesAtStartup"),
            "gcReportedConfiguredHeapLimitBytes": runtime.get("ObservedConfiguredGcHeapHardLimitBytes"),
            "gcBudgetEnforcementProven": runtime.get("GcHeapBudgetEnforcementProven"),
            "javaHeapAtSteadyEnd": {key: after.get(key) for key in ("JavaHeapUsedBytes", "JavaHeapCommittedBytes", "JavaHeapMaximumBytes")} if implementation == "java-native" else None,
            "javaHeapApiScope": "Raw Runtime API values only: Used=totalMemory()-freeMemory(), the legacy field named Committed=Runtime.totalMemory(), Maximum=Runtime.maxMemory(). Native Image can report logical/runtime capacity values here; neither field establishes physical RSS or actual OS-committed memory. Retain exact values without equating them to observer or wait4 memory." if implementation == "java-native" else None,
            "scope": "SQLite native engine/cache are inside client process memory. PostgreSQL server is external. Java has no cap imposed by the C# requested-budget policy. RSS is not allocated bytes."}


def validate_and_extract(result, command, status, cell, case_names, policy):
    errors, warnings = [], []
    def require(condition, message):
        if not condition:
            errors.append(message)
    provider, implementation = cell["provider"], cell["implementation"]
    rate, concurrency = (3000, 4) if provider == "sqlite" else (3600, 8)
    offered = result.get("OfferedLoad") or {}
    require(status.get("status") == "passed", "runner cell-status is not passed")
    require(status.get("allStoredRowsRestored") is True, "runner has not confirmed restored fixture")
    require(command.get("success") is True and command.get("exitCode") == 0 and not command.get("timedOut"), "client/observer exit failed or timed out")
    require(not command.get("observerErrors"), "observer reported errors")
    require(result.get("TimingComparisonEligible") is True, "consumer is ineligible")
    require(result.get("Failed") == 0 and result.get("OracleFailures") == 0, "business or oracle failure")
    require(result.get("ApplicationConnectionsReturnedToZero") is True, "logical connections not returned")
    require(result.get("TimeSeriesTruncated") is not True and offered.get("TimeSeriesTruncated") is False, "time series truncated or missing")
    receipt_provider = provider if implementation == "java-native" else ("Microsoft.Data.Sqlite.Core" if provider == "sqlite" else "Npgsql")
    expected = {"Provider": receipt_provider, "Case": "mixed", "Mode": "prepared", "SessionMode": "persistent",
                "Concurrency": concurrency, "WarmupPerWorker": 64, "RequestedRows": 32, "BatchRows": 32,
                "Tenants": 8, "OrdersPerTenant": 1024, "EmptyDriver": False}
    for key, value in expected.items():
        require(result.get(key) == value, "consumer setting: " + key)
    require(result.get("ActualCaseIds") == case_names, "35-case order differs from frozen matrix")
    for key, value in {"RequestsPerSecond": rate, "OfferedSeconds": 1800, "QueueCapacity": 64,
                       "Planned": rate * 1800, "Attempted": rate * 1800, "Retries": 0,
                       "Failed": 0, "OracleFailures": 0}.items():
        require(offered.get(key) == value, "offered setting/counter: " + key)
    idle = result.get("Idle") or {}
    require(idle.get("RequestedSeconds") == 15 and numeric(idle.get("ObservedSeconds")) and idle["ObservedSeconds"] >= 15, "15-second released idle incomplete")
    counts = {key: offered.get(key) for key in ("Planned", "Attempted", "Sent", "Started", "Completed", "Succeeded", "Failed", "Rejected", "Retries", "Rows")}
    require(all(type(value) is int and value >= 0 for value in counts.values()), "offered counts must be nonnegative integers")
    if all(type(value) is int for value in counts.values()):
        require(counts["Attempted"] == counts["Sent"] + counts["Rejected"], "attempted != sent + rejected")
        require(counts["Sent"] == counts["Started"] == counts["Completed"], "admitted work not completely drained")
        require(counts["Completed"] == counts["Succeeded"] + counts["Failed"], "completion accounting differs")
        require(counts["Succeeded"] == result.get("Completed") and counts["Succeeded"] > 0, "top-level Completed is not successful completions")
        require(counts["Started"] == result.get("Started") and counts["Failed"] == result.get("Failed") and counts["Rows"] == result.get("Rows"), "top-level counters differ")
    frequency = offered.get("TimerFrequency")
    times = {key: offered.get(key) for key in ("StartedTicks", "DeadlineTicks", "OfferedEndTicks", "DrainedTicks")}
    start_ns, end_ns = result.get("SteadyStartMonotonicNs"), result.get("SteadyEndMonotonicNs")
    effective = result.get("EffectiveSeconds")
    interval = {"effectiveSeconds": effective, "offeredSecondsRequested": offered.get("OfferedSeconds"),
                "steadyStartMonotonicNs": start_ns, "steadyEndMonotonicNs": end_ns,
                "timerFrequency": frequency, "rawOfferedTimes": times}
    if numeric(frequency) and frequency > 0 and all(numeric(value) for value in times.values()):
        require(close((times["DeadlineTicks"] - times["StartedTicks"]) / frequency, 1800), "monotonic offered deadline is not 1800 seconds")
        require(times["StartedTicks"] <= times["DeadlineTicks"] <= times["OfferedEndTicks"] <= times["DrainedTicks"], "offered monotonic ordering invalid")
        interval.update(actualProducerSeconds=(times["OfferedEndTicks"]-times["StartedTicks"])/frequency,
                        scheduleSnapshotSeconds=(times["DrainedTicks"]-times["StartedTicks"])/frequency,
                        scheduleDrainAfterProducerSeconds=(times["DrainedTicks"]-times["OfferedEndTicks"])/frequency,
                        producerOvershootSeconds=(times["OfferedEndTicks"]-times["DeadlineTicks"])/frequency)
    else:
        errors.append("missing/invalid offered clock")
    if numeric(start_ns) and numeric(end_ns) and numeric(effective):
        require(end_ns >= start_ns and effective >= 1800, "steady measurement shorter than 1800 seconds")
        require(close((end_ns-start_ns)/1e9, effective, absolute=0.001), "consumer nanosecond boundaries differ from effective duration")
        require(command.get("startedMonotonicNs", start_ns+1) <= start_ns <= end_ns <= command.get("finishedMonotonicNs", end_ns-1), "consumer clock window outside observer command window")
        if numeric(frequency) and frequency > 0 and all(numeric(value) for value in times.values()):
            require(close(start_ns/1e9, times["StartedTicks"]/frequency, absolute=0.001, relative=0), "consumer and offered start clocks differ")
            interval["scheduleSnapshotMinusConsumerEndSeconds"] = times["DrainedTicks"]/frequency-end_ns/1e9
    else:
        errors.append("missing consumer steady window")
    interval["scope"] = "After warmup through completion of admitted work. C# OfferedLoad.DrainedTicks is a later Snapshot call, not necessarily the CPU/allocation metric end. Resource alignment uses top-level steady nanoseconds."
    seconds = offered.get("Seconds") or []
    for key in ("Planned", "Sent", "Started", "Succeeded", "Failed", "Rejected", "Rows"):
        values = [row.get(key) for row in seconds]
        require(bool(values) and all(type(value) is int and value >= 0 for value in values) and sum(value for value in values if type(value) is int) == offered.get(key), "per-second accounting: " + key)
    require([row.get("Second") for row in seconds] == list(range(len(seconds))), "per-second indices are not continuous from zero")
    latency = {}
    for label, field, count in (("successService", "SuccessServiceHistogram", "Succeeded"),
                                ("successScheduled", "SuccessScheduledHistogram", "Succeeded"),
                                ("allCompletedScheduled", "AllCompletedScheduledHistogram", "Completed"),
                                ("startDelay", "StartDelayHistogram", "Started")):
        try:
            latency[label] = histogram(offered.get(field), offered.get(count))
        except (ValueError, TypeError) as error:
            errors.append(field + ": " + str(error))
            latency[label] = None
    if latency["successService"]:
        for key, field in (("p50", "P50MicrosecondsUpper"), ("p95", "P95MicrosecondsUpper"), ("p99", "P99MicrosecondsUpper")):
            require(close(latency["successService"][key], (result.get("Latencies") or {}).get(field)), "top-level service quantile: " + key)
    latency["scope"] = "Successful service and scheduled-to-completion histograms exclude rejected work. Scheduled latency and start delay include producer dispatch lag and queueing. Percentiles cannot be subtracted to obtain a queue-time percentile."
    successes = counts["Succeeded"]
    within = sum(row.get("Succeeded", 0) for row in seconds if type(row.get("Second")) is int and row["Second"] < 1800)
    throughput = {"successfulOperationsPerEffectiveSecond": divide(successes, effective),
                  "allSuccessesNormalizedByRequested1800Seconds": divide(successes, 1800),
                  "successesCompletedWithinFirst1800Seconds": within,
                  "successfulOperationsPerSecondWithinFirst1800Seconds": divide(within, 1800),
                  "successesCompletedAfterFirst1800Seconds": difference(successes, within),
                  "actualAttemptedPerProducerSecond": divide(counts["Attempted"], interval.get("actualProducerSeconds")),
                  "rejectedFractionOfAttempts": divide(counts["Rejected"], counts["Attempted"]),
                  "businessFailureFractionOfAdmitted": divide(counts["Failed"], counts["Sent"]),
                  "scope": "Primary throughput uses all successful admitted operations / consumer effective seconds including drain; requested-window normalization is separately labelled."}
    cpu_user, cpu_system = result.get("UserCpuSeconds"), result.get("SystemCpuSeconds")
    cpu_total = cpu_user + cpu_system if numeric(cpu_user) and numeric(cpu_system) else None
    before, after = result.get("ProcessBefore") or {}, result.get("ProcessAfter") or {}
    require(cpu_total is not None and cpu_user >= 0 and cpu_system >= 0, "client steady CPU invalid")
    for key in ("UserCpuSeconds", "SystemCpuSeconds"):
        require(close(result.get(key), difference(after.get(key), before.get(key))), "client CPU endpoint delta: " + key)
    require(close(divide(cpu_total, successes), result.get("CpuSecondsPerSuccessfulOperation")), "CPU/success mismatch")
    cpu = {"steadyUserSeconds": cpu_user, "steadySystemSeconds": cpu_system, "steadyTotalSeconds": cpu_total,
           "steadyCpuSecondsPerSuccessfulOperation": divide(cpu_total, successes),
           "steadyCpuMicrosecondsPerSuccessfulOperation": divide(cpu_total * 1e6 if cpu_total is not None else None, successes),
           "steadyAverageCpuCores": divide(cpu_total, effective),
           "lifetimeWait4UserSeconds": command.get("processLifetimeUserCpuSeconds"),
           "lifetimeWait4SystemSeconds": command.get("processLifetimeSystemCpuSeconds"),
           "scope": "Primary CPU is the consumer's whole-process before/after delta. Separate wait4 values include startup, warmup, release, idle and exit; never add them to steady CPU."}
    allocated, allocated_before, allocated_after = result.get("AllocatedBytes"), result.get("AllocatedBefore"), result.get("AllocatedAfter")
    if allocated is not None:
        require(type(allocated) is int and allocated >= 0 and allocated == difference(allocated_after, allocated_before), "allocation counter delta invalid")
        require(close(divide(allocated, successes), result.get("BytesPerSuccessfulOperation")), "allocated bytes/success mismatch")
    elif allocated_before is not None or allocated_after is not None:
        warnings.append("Only one allocation boundary is available; aggregate allocation remains null")
    allocation = {"runtime": "Java" if implementation == "java-native" else "managed-dotnet",
                  "wholeProcessAllocatedBytes": allocated,
                  "bytesPerSuccessfulOperation": divide(allocated, successes),
                  "bytesPerResultRow": divide(allocated, counts["Rows"]),
                  "attribution": result.get("AllocationAttribution"),
                  "nativeAllocatedBytes": result.get("NativeAllocationBytes"),
                  "nativeAllocationProfile": result.get("NativeAllocationProfile"),
                  "scope": "Raw whole-process counter delta includes runtime/library/driver/DTO/harness allocation. No subtraction or framework-only zero-allocation claim. Unavailable native/Java metrics remain null."}
    require(result.get("NativeAllocationProfile") is None, "instrumented native allocation profile present in formal measurement")
    cases = result.get("Cases") or []
    require(len(cases) == len(case_names) and [row.get("Name") for row in cases] == case_names, "per-case records differ from frozen case order")
    for field in ("Started", "Succeeded", "Failed", "Rows"):
        values = [row.get(field) for row in cases]
        require(all(type(value) is int and value >= 0 for value in values) and sum(value for value in values if type(value) is int) == counts.get(field), "per-case accounting: " + field)
    # All three clients map the global scheduled job index modulo ActiveCaseIds.
    # Full admission/drain accounting above permits exact rejection derivation.
    enriched_cases = []
    planned_total = counts.get("Planned")
    valid_planned = type(planned_total) is int and planned_total >= 0 and bool(case_names)
    for index, row in enumerate(cases):
        planned_case = planned_total // len(case_names) + (1 if index < planned_total % len(case_names) else 0) if valid_planned else None
        planned_share, success_share = divide(planned_case, planned_total), divide(row.get("Succeeded"), successes)
        rejected_case = difference(planned_case, row.get("Started"))
        require(rejected_case is not None and rejected_case >= 0, "per-case inferred rejection is invalid: " + str(row.get("Name")))
        enriched_cases.append(dict(row, Planned=planned_case, RejectedDerivedFromPlanMinusStarted=rejected_case,
                                   PlannedShare=planned_share, SuccessfulShare=success_share,
                                   SuccessfulShareMinusPlannedPercentagePoints=100*(success_share-planned_share) if success_share is not None and planned_share is not None else None))
    cases = enriched_cases
    if cases and all(type(row["RejectedDerivedFromPlanMinusStarted"]) is int for row in cases):
        require(sum(row["Planned"] for row in cases) == counts["Planned"], "per-case planned sum differs")
        require(sum(row["RejectedDerivedFromPlanMinusStarted"] for row in cases) == counts["Rejected"], "per-case inferred rejection sum differs")
    if numeric(counts.get("Rejected")) and counts["Rejected"] > 0:
        warnings.append("Rejection changes the admitted case population; compare per-case success shares. No rejection latency is inserted into successful-operation histograms.")
    if implementation == "ef-satori":
        warnings.append("192 MiB is requested GC configuration only. A prior 128 MiB Satori probe crossed its requested heap budget; no equivalent enforcement probe was performed at 192 MiB. This run preserves the observed GC available-memory value and makes no enforced-cap or GC-only causal claim.")
    return {"name": cell["name"], "provider": provider, "implementation": implementation,
            "label": LABELS.get(implementation, implementation), "checks": {"accepted": not errors, "errors": errors, "warnings": warnings},
            "identity": {key: result.get(key) for key in ("Route", "Provider", "NativeAot", "ExecutableSha256", "PackageVersion", "DatabaseVersion", "Database", "JavaVersion", "VmVersion", "GcContract", "GcIdentity")},
            "interval": interval, "counts": counts, "throughput": throughput, "latency": latency,
            "clientCpu": cpu, "memory": memory_measurements(result, command, implementation, policy),
            "allocation": allocation, "gc": gc_measurements(result, implementation), "cases": cases,
            "caseDistributionScope": "Planned counts reconstructed exactly from global job index modulo the frozen 35-case order. Per-case rejection is derived, not separately instrumented: Planned minus Started, valid only after full Attempted=Planned and Sent=Started reconciliation.",
            "perSecond": seconds, "errorClasses": offered.get("ErrorClasses"), "oracleFailures": result.get("OracleFailures"),
            "rawErrors": result.get("Errors") or offered.get("Errors"), "originalCellStatus": status}


def inspect_resources(path, result, command, owner, ticks_per_second):
    """Two raw tree endpoints; never sum per-PID maxima or positive-only tick deltas."""
    start_ns, end_ns = result["SteadyStartMonotonicNs"], result["SteadyEndMonotonicNs"]
    client_id = identity(command.get("clientIdentity"))
    server_id = identity((owner or {}).get("identity"))
    file_hash = hashlib.sha256()
    count = inside_count = 0
    client_rss, client_pss, server_rss, server_pss = [], [], [], []
    complete_server_rss = complete_server_pss = 0
    first = last = previous = None
    negative_steps, errors, acquisition_ns, server_identity_seen = [], [], [], set()
    server_process_counts = []
    server_observation_errors = []
    before_edge = after_edge = None
    recomputed_match = True
    client_matching_samples = 0
    with path.open("rb") as stream:
        for line_number, raw in enumerate(stream, 1):
            file_hash.update(raw)
            if not raw.strip():
                errors.append({"line": line_number, "error": "blank JSONL line"})
                continue
            try:
                reading = json.loads(raw)
            except json.JSONDecodeError as error:
                errors.append({"line": line_number, "error": str(error)})
                continue
            count += 1
            begin, end = reading.get("monotonicNs"), reading.get("acquiredThroughMonotonicNs")
            if not numeric(begin) or not numeric(end) or end < begin:
                errors.append({"line": line_number, "error": "invalid acquisition interval"})
                continue
            if end < start_ns:
                before_edge = {"line": line_number, "monotonicNs": begin, "acquiredThroughMonotonicNs": end}
            if after_edge is None and begin > end_ns:
                after_edge = {"line": line_number, "monotonicNs": begin, "acquiredThroughMonotonicNs": end}
            if begin < start_ns or end > end_ns:
                continue
            inside_count += 1
            acquisition_ns.append(end-begin)
            client = [value for value in reading.get("client", []) if identity(value) == client_id]
            if len(client) == 1:
                client_matching_samples += 1
                memory = client[0].get("memoryBytes") or {}
                client_rss.append(memory.get("Rss"))
                client_pss.append(memory.get("Pss"))
            server = reading.get("server") or []
            if not server:
                continue
            server_process_counts.append(len(server))
            roots = [value for value in server if identity(value) == server_id]
            if len(roots) != 1:
                server_observation_errors.append({"line": line_number, "error": "server root identity absent or duplicated; sample excluded from subset endpoint accounting"})
                continue
            user = sum(value["userTicks"] + value["reapedChildUserTicks"] for value in server)
            system = sum(value["systemTicks"] + value["reapedChildSystemTicks"] for value in server)
            totals = reading.get("serverTotals") or {}
            recomputed_match &= (user == totals.get("ownAndReapedUserTicks") and system == totals.get("ownAndReapedSystemTicks"))
            for value in server:
                server_identity_seen.add(identity(value))
            rss_complete = all("Rss" in (value.get("memoryBytes") or {}) for value in server)
            pss_complete = all("Pss" in (value.get("memoryBytes") or {}) for value in server)
            if rss_complete:
                complete_server_rss += 1
                server_rss.append(sum(value["memoryBytes"]["Rss"] for value in server))
            if pss_complete:
                complete_server_pss += 1
                server_pss.append(sum(value["memoryBytes"]["Pss"] for value in server))
            endpoint = {"line": line_number, "monotonicNs": begin, "acquiredThroughMonotonicNs": end,
                        "ownAndReapedUserTicks": user, "ownAndReapedSystemTicks": system, "observedProcessCount": len(server),
                        "processIdentities": [{"pid": value["pid"], "startTicks": value["startTicks"]} for value in server],
                        "rootIdentity": {"pid": roots[0]["pid"], "startTicks": roots[0]["startTicks"]}}
            if previous and (user < previous["ownAndReapedUserTicks"] or system < previous["ownAndReapedSystemTicks"]):
                negative_steps.append({"fromLine": previous["line"], "toLine": line_number,
                                       "userTickDelta": user-previous["ownAndReapedUserTicks"],
                                       "systemTickDelta": system-previous["ownAndReapedSystemTicks"]})
            if first is None:
                first = endpoint
            last = previous = endpoint
    is_postgres = result.get("Provider") in ("Npgsql", "postgresql")
    expected_backends = result.get("Concurrency") if is_postgres and result.get("SessionMode") == "persistent" else None
    minimum_processes = expected_backends + 1 if type(expected_backends) is int and expected_backends > 0 else None
    observed_min = min(server_process_counts) if server_process_counts else None
    observed_max = max(server_process_counts) if server_process_counts else None
    necessarily_incomplete = bool(server_observation_errors) or (minimum_processes is not None and (observed_min is None or observed_min < minimum_processes))
    coverage = {"applicable": is_postgres,
                "status": "not-applicable" if not is_postgres else "incomplete-observed" if necessarily_incomplete else "unproven",
                "serverIdentityObservationErrorCount": len(server_observation_errors),
                "wholeServerEnumerationProven": False,
                "observedProcessCountMinimum": observed_min, "observedProcessCountMaximum": observed_max,
                "expectedPersistentClientBackends": expected_backends,
                "minimumRootPlusPersistentBackends": minimum_processes,
                "minimumCountIsNecessaryNotSufficient": True,
                "recordedRssCompleteProvesEnumeration": False,
                "reason": "The frozen observer follows /proc/<pid>/task/*/children but records no enumeration-coverage evidence. rssComplete/pssComplete cover only returned records. A postmaster-only snapshot omits live backends/background processes; even reaching the lower count bound does not prove full coverage.",
                "policy": "Whole-server steady CPU/RSS/PSS remain null unless independent enumeration coverage is established; this schema supplies none. Preserve observed subset values only, without replacing unknown with zero."}
    server_cpu = {"available": False, "observedSubsetAvailable": False, "coverage": coverage,
                  "wholeServerSteadyUserSeconds": None, "wholeServerSteadySystemSeconds": None,
                  "wholeServerSteadyTotalSeconds": None, "wholeServerCpuSecondsPerSuccessfulOperation": None,
                  "method": "last raw inside-window tree total minus first raw inside-window tree total",
                  "treeSnapshotNonAtomic": True, "clockTicksPerSecond": ticks_per_second,
                  "firstEndpoint": first, "lastEndpoint": last, "negativeAdjacentSnapshotDeltas": negative_steps,
                  "recomputedTotalsMatchObserver": recomputed_match,
                  "uniqueObservedProcessIdentities": len(server_identity_seen),
                  "scope": "Observed subset only: sum each endpoint's own user/system and already-reaped child ticks once. Never accumulate per-PID maxima, sum positive deltas, or add wait4 totals. Missing descendants, brief processes and non-atomic transfers can affect endpoints; these are not whole-server costs."}
    if first and last and last["line"] > first["line"] and numeric(ticks_per_second) and ticks_per_second > 0:
        user = (last["ownAndReapedUserTicks"]-first["ownAndReapedUserTicks"])/ticks_per_second
        system = (last["ownAndReapedSystemTicks"]-first["ownAndReapedSystemTicks"])/ticks_per_second
        covered = (last["monotonicNs"]-first["monotonicNs"])/1e9
        server_cpu.update(observedSubsetAvailable=user >= 0 and system >= 0 and recomputed_match,
                          observedSubsetUserSeconds=user, observedSubsetSystemSeconds=system, observedSubsetTotalSeconds=user+system,
                          acquisitionStartSpanSeconds=covered,
                          observedSubsetAverageCpuCoresOverSampleSpan=divide(user+system, covered),
                          leadingUnsampledSeconds=(first["monotonicNs"]-start_ns)/1e9,
                          trailingUnsampledSeconds=(end_ns-last["acquiredThroughMonotonicNs"])/1e9,
                          observedSubsetCpuSecondsPerAllSuccessfulOperations=divide(user+system, result.get("Completed")),
                          normalizationCaution="Partial numerator covers only enumerated processes and the inner sampled span; denominator is all consumer successes. It is not whole-server CPU/success. No interpolation/extrapolation to manufacture exact 1800-second server CPU.")
    return {"path": str(path), "sha256": file_hash.hexdigest(), "allSamples": count, "fullyInsideSteadySamples": inside_count,
            "clientIdentityMatchingInsideSamples": client_matching_samples,
            "clientSampledSteadyPeakRssBytes": maximum(client_rss), "clientSampledSteadyPeakPssBytes": maximum(client_pss),
            "clientSampledSteadyPeakScope": "Separate maxima of observer smaps_rollup Rss and Pss from the exact client PID/startTicks, using only samples whose entire acquisition interval is inside the consumer steady window. These are discrete observed maxima, not guaranteed instantaneous/lifetime peaks; no cross-source ordering is enforced.",
            "clientRssAvailableSamples": sum(value is not None for value in client_rss),
            "clientPssAvailableSamples": sum(value is not None for value in client_pss),
            "serverSampledSteadyPeakTreeRssBytes": None, "serverSampledSteadyPeakTreePssBytes": None,
            "serverObservedSubsetPeakRssBytes": maximum(server_rss), "serverObservedSubsetPeakPssBytes": maximum(server_pss),
            "serverObservedSubsetRssCompleteSamples": complete_server_rss, "serverObservedSubsetPssCompleteSamples": complete_server_pss,
            "serverEnumerationCoverage": coverage,
            "serverTreeRssScope": "Whole-server RSS/PSS unavailable: enumeration coverage unproven/incomplete. Only explicitly labelled observed-subset peaks are retained. Subset process RSS can count shared pages repeatedly; readability within returned records is not proof of complete enumeration. Neither RSS nor PSS is allocated-byte volume.",
            "largestAcquisitionNanoseconds": maximum(acquisition_ns), "lastBeforeSteady": before_edge, "firstAfterSteady": after_edge,
            "serverCpu": server_cpu, "errors": errors, "serverObservationErrors": server_observation_errors}


def postgres_measurements(directory, owner, resource):
    if owner is None:
        return None
    before_path, after_path = directory/"postgres-stats-before.json", directory/"postgres-stats-after.json"
    before = read_json(before_path) if before_path.exists() else None
    after = read_json(after_path) if after_path.exists() else None
    changes = {}
    if before and after:
        for key, last in after.get("value", {}).items():
            if key not in ("datid",) and numeric(last) and numeric(before.get("value", {}).get(key)):
                changes[key] = last-before["value"][key]
    return {"sampledSteadyTreeCpu": resource["serverCpu"],
            "lifetimeWait4": {key: owner.get(key) for key in ("processLifetimeUserCpuSeconds", "processLifetimeSystemCpuSeconds", "processLifetimeMaxRssBytes", "startedMonotonicNs", "finishedMonotonicNs", "exitCode")},
            "lifetimeScope": "PostgreSQL owner OS-reported wait4 lifetime own/reaped-descendant usage, including fixture/warmup/release/idle/shutdown as applicable. Keep as the OS lifetime counter after normal shutdown; it is not steady CPU or proof of observer descendant coverage. Never add to observed-subset CPU. wait4 maxRSS is not peak simultaneous tree RSS.",
            "statsBeforeAfter": {"numericDeltas": changes, "before": before, "after": after,
                                 "scope": "pg_stat_database observations outside client timed boundaries; broad session scope and delayed statistics publication, not pure steady server execution cost."},
            "shutdownClean": owner.get("exitCode") == 0 and not owner.get("shutdownError") and not owner.get("finalSampleError")}


def apply_exact_idle_adjudication(record, result, analysis_root):
    """Preserve strict errors; classify only the exact independently reviewed bytes."""
    checks, status, idle = record["checks"], record["originalCellStatus"], result.get("Idle") or {}
    checks["strictAccepted"] = checks["accepted"]
    checks["businessMeasurementAccepted"] = checks["accepted"]
    checks["strictIdleRequirementMet"] = (idle.get("RequestedSeconds") == 15
        and numeric(idle.get("ObservedSeconds")) and idle["ObservedSeconds"] >= 15)
    record["originalStrictStatus"] = status.get("status")
    record["originalStrictFailures"] = status.get("failures", [])
    record["measurementClassification"] = "strictly-accepted" if checks["accepted"] else "strict-failed"
    record["idleAdjudication"] = None
    approved = EXACT_IDLE_ADJUDICATIONS.get(record["name"])
    if approved is None or checks["accepted"]:
        return
    path = analysis_root/approved["reviewFile"]
    required_errors = {"runner cell-status is not passed", "15-second released idle incomplete"}
    exact = (record["evidence"]["result"]["sha256"] == approved["resultSha256"]
        and record["evidence"]["status"]["sha256"] == approved["statusSha256"]
        and status.get("status") == "failed" and status.get("failures") == ["released_idle"]
        and len(checks["errors"]) == 2 and set(checks["errors"]) == required_errors
        and idle.get("RequestedSeconds") == 15 and idle.get("ObservedSeconds") == approved["observedIdleSeconds"]
        and path.is_file() and sha_file(path) == approved["reviewSha256"])
    if not exact:
        checks["warnings"].append("The exact idle-adjudication allowlist did not match this evidence; no business classification exception applied.")
        return
    review = read_json(path)
    documented = (review.get("schema") == "DB-Runtime-Compare-01.exact-idle-adjudication.v1"
        and review.get("cellName") == record["name"]
        and review.get("classification") == "business-valid/idle-deviation"
        and review.get("reviewedBy") == ["/root", "/root/baseline_recovery"]
        and review.get("originalStrictStatus") == "failed"
        and review.get("strictIdleRequirementMet") is False
        and review.get("fullStrictAcceptance") is False
        and review.get("businessMeasurementAccepted") is True
        and review.get("business", {}).get("allBusinessChecksPassed") is True
        and review.get("evidence", {}).get("result", {}).get("sha256") == approved["resultSha256"]
        and review.get("evidence", {}).get("status", {}).get("sha256") == approved["statusSha256"]
        and review.get("idle", {}).get("raw") == idle)
    if not documented:
        checks["warnings"].append("The hash-bound idle review does not assert the required narrow classification; no exception applied.")
        return
    checks["businessMeasurementAccepted"] = True
    record["measurementClassification"] = "business-valid/idle-deviation"
    record["idleAdjudication"] = {"path":str(path),"sha256":approved["reviewSha256"],
        "classification":review["classification"],"reviewedBy":review["reviewedBy"],
        "originalStrictStatus":"failed","strictIdleRequirementMet":False,
        "requestedIdleSeconds":15,"observedIdleSeconds":idle["ObservedSeconds"],
        "scope":"Exact reviewed business window only. Preserve strict failure and actual shorter idle; no generalized tolerance and no rewrite of source evidence."}
    checks["warnings"].append("Exact SHA-bound two-assistant review accepts this 1800-second business window only. Original strict status remains failed; idle is 14.997119729 seconds, not a full 15 seconds.")


def compare(cells):
    result = []
    for provider in PROVIDERS:
        baseline = next((cell for cell in cells if cell["provider"] == provider and cell["implementation"] == "dapper"), None)
        if baseline is None:
            continue
        for cell in cells:
            if cell["provider"] != provider or cell["implementation"] == "dapper":
                continue
            metrics = {
                "successThroughput": (cell["throughput"]["successfulOperationsPerEffectiveSecond"], baseline["throughput"]["successfulOperationsPerEffectiveSecond"]),
                "clientCpuPerSuccess": (cell["clientCpu"]["steadyCpuSecondsPerSuccessfulOperation"], baseline["clientCpu"]["steadyCpuSecondsPerSuccessfulOperation"]),
                "lifetimeWait4MaxRss": (cell["memory"]["lifetimeWait4MaxRssBytes"], baseline["memory"]["lifetimeWait4MaxRssBytes"]),
                "releasedIdleRss": (cell["memory"]["releasedIdleRssAfterBytes"], baseline["memory"]["releasedIdleRssAfterBytes"]),
                "wholeProcessAllocationPerSuccess": (cell["allocation"]["bytesPerSuccessfulOperation"], baseline["allocation"]["bytesPerSuccessfulOperation"])}
            for key in ("successService", "successScheduled"):
                metrics[key+"P99Upper"] = ((cell["latency"].get(key) or {}).get("p99"), (baseline["latency"].get(key) or {}).get("p99"))
            valid = cell["checks"]["businessMeasurementAccepted"] and baseline["checks"]["businessMeasurementAccepted"]
            values = {}
            for name, (value, reference) in metrics.items():
                ratio = divide(value, reference) if valid else None
                values[name] = {"value": value, "dapperValue": reference, "ratio": ratio,
                                "differencePercent": (ratio-1)*100 if ratio is not None else None,
                                "absoluteDifference": difference(value, reference) if valid else None}
            result.append({"provider": provider, "implementation": cell["implementation"], "descriptiveComparisonEligible": valid,
                           "metrics": values,
                           "originalStrictStatuses":{"value":cell["originalStrictStatus"],"dapper":baseline["originalStrictStatus"]},
                           "businessClassifications":{"value":cell["measurementClassification"],"dapper":baseline["measurementClassification"]},
                           "idleObservedSeconds":{"value":cell["memory"]["releasedIdleObservedSeconds"],"dapper":baseline["memory"]["releasedIdleObservedSeconds"]},
                           "scope": "One serial run per cell on the same observed host/boot. Descriptive ratios only: no repeated-measurement significance, causal GC-only conclusion, saturation knee, or alignment claim."})
    return result


def formatted(value, digits=2):
    return "不可用" if not numeric(value) else f"{value:,.{digits}f}"


def render_report(summary):
    lines = ["# DB-Runtime-Compare-01：八格正式运行的离线分析", "",
             "## 验收与解释范围", "",
             f"原始严格验收：**{'全部通过' if summary['allCellsAccepted'] else '存在严格失败；原状态完整保留'}**。1800秒业务窗口比较资格：**{'全部有效（含表中精确Hash绑定的独立评审分类）' if summary['allBusinessMeasurementsAccepted'] else '存在未通过项'}**。PG整库steady成本缺测须另看覆盖说明，不能把业务资格解释为所有指标完整。本报告由冻结回执和原始observer采样生成，未经重复运行，不宣称统计显著、GC单因素因果或已对齐。", "",
             "C#统一请求192 MiB GC预算，未施加cgroup或进程总内存硬限；Satori的本格实际GC available按RuntimeIdentity展示；既有越界探针是128 MiB，不能冒称已完成192 MiB边界探针。SQLite原生内存计入客户端，PG服务端单列，Java未施加该C#预算。", "",
             "主吞吐为成功业务数除以消费者EffectiveSeconds（包含已准入任务drain）。延迟是直方图bin上界；拒绝不进入成功延迟样本。StartDelay包含到达调度迟滞和排队。", "",
             "## 成功、拒绝与错误", "",
             "| 实现 | 数据库 | 成功数 | 拒绝数 | 业务错误 | 成功/s | 拒绝率 | Effective秒 |", "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for cell in summary["cells"]:
        counts, throughput = cell["counts"], cell["throughput"]
        reject = throughput["rejectedFractionOfAttempts"]
        lines.append(f"| {cell['label']} | {cell['provider']} | {formatted(counts['Succeeded'],0)} | {formatted(counts['Rejected'],0)} | {formatted(counts['Failed'],0)} | {formatted(throughput['successfulOperationsPerEffectiveSecond'])} | {formatted(reject*100 if reject is not None else None)}% | {formatted(cell['interval']['effectiveSeconds'],6)} |")
    lines += ["", "## 原始严格状态与业务分类", "",
              "| 格 | 原始严格状态 | 业务分类 | strict idle ≥15s | 实际idle秒 |",
              "| --- | --- | --- | --- | ---: |"]
    for cell in summary["cells"]:
        lines.append(f"| {cell['name']} | {cell['originalStrictStatus']} | {cell['measurementClassification']} | {cell['checks']['strictIdleRequirementMet']} | {formatted(cell['memory']['releasedIdleObservedSeconds'],9)} |")
    lines += ["", "business-valid/idle-deviation只用于已列入精确case名、result/status/review Hash绑定的单条独立评审。原strict failed与严格错误保留，实际idle不改成15秒，也没有为其他格增加通用毫秒容差。", ""]
    lines += ["", "## 客户端成本与释放后内存", "", "| 实现 | 数据库 | CPU µs/成功业务 | 释放idle后RSS MiB | 实际idle秒 | GC启动可用MiB | 全进程分配 B/成功业务 |", "| --- | --- | ---: | ---: | ---: | ---: | ---: |"]
    for cell in summary["cells"]:
        lines.append(f"| {cell['label']} | {cell['provider']} | {formatted(cell['clientCpu']['steadyCpuMicrosecondsPerSuccessfulOperation'])} | {formatted(divide(cell['memory']['releasedIdleRssAfterBytes'],2**20))} | {formatted(cell['memory']['releasedIdleObservedSeconds'],9)} | {formatted(divide(cell['memory']['gcReportedAvailableMemoryAtStartupBytes'],2**20))} | {formatted(cell['allocation']['bytesPerSuccessfulOperation'])} |")
    lines += ["", "RSS为内存驻留量；分配来自全进程累计计数，含驱动、DTO、JSON与工具成本，不能反推框架单独分配。Native/Java不支持的计数保持null，未记为0。三种峰值来源及范围在下一表分别展示，不合并为一个max。idle没有强制GC；请求15秒，各格实测时长见表。实际idle观察后的RSS不能单独证明泄漏或无泄漏。GC启动可用值来自本格RuntimeIdentity；未记录的Dapper字段保持不可用，不用独立探针代填。", "",
              "## 客户端RSS/PSS的三个观测来源", "",
              "| 实现 | 数据库 | OS wait4 生命周期 maxRSS MiB | 消费者ProcessAfter自报峰 MiB | observer稳态采样RSS峰 MiB | observer稳态采样PSS峰 MiB |",
              "| --- | --- | ---: | ---: | ---: | ---: |"]
    for cell in summary["cells"]:
        memory, resources = cell["memory"], cell["resources"]
        lines.append(f"| {cell['label']} | {cell['provider']} | {formatted(divide(memory['lifetimeWait4MaxRssBytes'],2**20),8)} | {formatted(divide(memory['clientReportedPeakThroughSteadyEndBytes'],2**20),8)} | {formatted(divide(resources['clientSampledSteadyPeakRssBytes'],2**20),8)} | {formatted(divide(resources['clientSampledSteadyPeakPssBytes'],2**20),8)} |")
    lines += ["", "OS wait4列保留操作系统在进程退出回收时报告的生命周期maxRSS。消费者列来自业务结束后的ProcessAfter快照所见高水位，可能包含此前暖机，不能冒称退出后的全生命周期值。observer列分别取同一PID/startTicks、且采集全程落在steady窗口内的离散RSS/PSS样本最大值，不能保证捕获瞬时峰。", "",
              "三种数值的差异原样保留，不强制wait4或消费者自报峰大于等于smaps样本，不跨来源取max，不把差异列为业务错误。具体Linux/API计数差异原因没有在本轮证实；各列原始bytes、有效采样数和scope保留在summary.json。 Java结果另保留Runtime.totalMemory()/maxMemory()的API原值：历史字段JavaHeapCommittedBytes实际来自totalMemory()，不能将其解释为物理RSS或真实OS已提交内存。", "",
              "## 服务及含调度/排队延迟", "", "| 实现 | 数据库 | 成功service p50/p95/p99 µs | 成功scheduled p50/p95/p99 µs | start-delay p50/p95/p99 µs |", "| --- | --- | --- | --- | --- |"]
    def quantiles(cell, key):
        item = cell["latency"].get(key) or {}
        return " / ".join(formatted(item.get(percentile)) for percentile in ("p50", "p95", "p99"))
    for cell in summary["cells"]:
        lines.append(f"| {cell['label']} | {cell['provider']} | {quantiles(cell,'successService')} | {quantiles(cell,'successScheduled')} | {quantiles(cell,'startDelay')} |")
    lines += ["", "## PostgreSQL服务端成本", "", "| 实现 | 整库steady CPU秒 | 观测子集CPU秒 | 子集进程数min/max | 生命周期wait4 CPU秒 | 整库steady峰PSS MiB |", "| --- | ---: | ---: | --- | ---: | ---: |"]
    for cell in summary["cells"]:
        if not cell.get("postgres"):
            continue
        pg, resource = cell["postgres"], cell["resources"]
        cpu, lifetime = pg["sampledSteadyTreeCpu"], pg["lifetimeWait4"]
        life = lifetime.get("processLifetimeUserCpuSeconds")
        if numeric(life) and numeric(lifetime.get("processLifetimeSystemCpuSeconds")):
            life += lifetime["processLifetimeSystemCpuSeconds"]
        else:
            life = None
        coverage = cpu.get("coverage") or {}
        process_range = str(coverage.get("observedProcessCountMinimum")) + "/" + str(coverage.get("observedProcessCountMaximum"))
        lines.append(f"| {cell['label']} | {formatted(cpu.get('wholeServerSteadyTotalSeconds') if cpu.get('available') else None)} | {formatted(cpu.get('observedSubsetTotalSeconds') if cpu.get('observedSubsetAvailable') else None)} | {process_range} | {formatted(life)} | {formatted(divide(resource.get('serverSampledSteadyPeakTreePssBytes'),2**20))} |")
    lines += ["", "整库steady CPU/RSS/PSS未获得完整进程枚举证明，保持不可用；只看到postmaster时，其CPU或RSS不能当成整库值，rssComplete=true也只证明已返回记录可读。表中观测子集是原始端点own+already-reaped差，可能遗漏全部活跃backend，绝不是整库成本。树快照非原子，边缘缺口和负向跳变保留，不插值成精确1800秒；没有累加per-PID最大值、重复计parent reaped或加上wait4。正常shutdown后的wait4保留OS生命周期计数口径，不能据此倒推steady；PG统计查询的前后差也覆盖更宽窗口。", "",
              "## GC口径", "", "| 实现 | 数据库 | 进程计数 | 计时时长与限制 |", "| --- | --- | --- | --- |"]
    for cell in summary["cells"]:
        gc = cell["gc"]
        if gc["api"] == "System.GC":
            counts = json.dumps(gc["generationCollectionCounts"],ensure_ascii=False,separators=(",",":"))
            time = formatted(gc["reportedPauseDurationSeconds"],6) + "秒；" + gc["pauseScope"]
        else:
            counts = formatted(gc.get("collections"),0)
            time = formatted(gc.get("collectionMilliseconds"),3) + "毫秒collection time；不是已验证的STW暂停分布"
        lines.append(f"| {cell['label']} | {cell['provider']} | {counts} | {time} |")
    lines += ["", "## 相对同库Dapper的描述性差距", "", "| 实现 | 数据库 | 成功吞吐变化 | CPU/成功变化 | service p99变化 | scheduled p99变化 |", "| --- | --- | ---: | ---: | ---: | ---: |"]
    for comparison in summary["relativeToDapper"]:
        metrics = comparison["metrics"]
        def percentage(key):
            value = metrics[key]["differencePercent"]
            return (formatted(value)+"%") if value is not None else "不可用"
        lines.append(f"| {LABELS.get(comparison['implementation'],comparison['implementation'])} | {comparison['provider']} | {percentage('successThroughput')} | {percentage('clientCpuPerSuccess')} | {percentage('successServiceP99Upper')} | {percentage('successScheduledP99Upper')} |")
    lines += ["", "各格只有一次长run，CPU/内存预算、ORM/驱动、SQL翻译、调度与GC可能同时不同；不能把差距全部归因GC。出现拒绝时，应结合case-distribution.md及summary.json中的35类计划与实际成功占比，避免把不同准入业务构成当成单查询加速。固定到达率的八格不能推出持续吞吐上限或开始拒绝的压力拐点。", "", "## 核验问题与保留限制", ""]
    for cell in summary["cells"]:
        lines.append(f"### {cell['name']}")
        lines.append("")
        messages = cell["checks"]["errors"] + cell["checks"]["warnings"]
        if messages:
            lines.extend("- " + message for message in messages)
        else:
            lines.append("完整时长、计数与原始证据检查通过。")
        lines.append("")
    lines += ["## 证据定位", "", "summary.json保留输入文件SHA-256、原始回执路径、时间边界、采样覆盖与完整35类计数；所有数字可回到原始JSON/JSONL。原始记录没有被修改。本轮不与历史另一机器的数值直接拼接作同机前后对照。", ""]
    return "\n".join(lines)


def render_case_distribution(summary):
    lines = ["# 35类业务的计划与实际分布", "",
             "计划数由全局job index % 35及冻结case order恢复。完整Attempted=Planned和Sent=Started对账成立后，按类计划数减Started推导拒绝数；这是派生量，未假称采集了每次拒绝事件的case标签。", "",
             "成功业务份额可能因拒绝而偏离计划份额。CPU/成功业务是该实际业务组合的总体成本，不能未经分层就归因框架、ORM或GC。", ""]
    for cell in summary["cells"]:
        lines += ["## " + cell["name"], "",
                  "| 业务 | 计划 | 实际Started | 成功 | 失败 | 推导拒绝 | 计划占比 | 成功占比 | 成功减计划p.p. |",
                  "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
        for row in cell["cases"]:
            planned_share, success_share = row.get("PlannedShare"), row.get("SuccessfulShare")
            lines.append(f"| {row['Name']} | {formatted(row.get('Planned'),0)} | {formatted(row.get('Started'),0)} | {formatted(row.get('Succeeded'),0)} | {formatted(row.get('Failed'),0)} | {formatted(row.get('RejectedDerivedFromPlanMinusStarted'),0)} | {formatted(planned_share*100 if planned_share is not None else None,4)}% | {formatted(success_share*100 if success_share is not None else None,4)}% | {formatted(row.get('SuccessfulShareMinusPlannedPercentagePoints'),4)} |")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, required=True)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if hasattr(os, "sched_getaffinity") and os.sched_getaffinity(0) != {8}:
        raise ValueError("Launch offline analysis with taskset -c 8; the script does not change affinity")
    directory, target = args.campaign.resolve(), args.output.resolve()
    analysis_root = Path(__file__).resolve().parent
    if not target.is_relative_to(analysis_root) or target == analysis_root or target.exists():
        raise ValueError("Output must be a new child directory of campaign/analysis")
    matrix, host = read_json(args.matrix), read_json(directory/"host.json")
    expected = [(implementation, provider) for implementation in IMPLEMENTATIONS for provider in PROVIDERS]
    if [(cell.get("implementation"),cell.get("provider")) for cell in matrix.get("cells",[])] != expected:
        raise ValueError("Exactly eight frozen cells in the prescribed serial order are required")
    matrix_hash = sha_file(args.matrix)
    if host.get("matrixSha256") != matrix_hash:
        raise ValueError("Host evidence is bound to a different matrix")
    if len(matrix.get("caseNames",[])) != 35 or len(set(matrix["caseNames"])) != 35:
        raise ValueError("Frozen matrix must identify all 35 distinct cases")
    policy = matrix.get("memoryPolicy") or {}
    if policy.get("cgroupRequired") is not False or policy.get("csharpRequestedGcHeapBytes") != 201326592:
        raise ValueError("Matrix does not carry the accepted requested-192-MiB/no-cgroup policy")
    with (directory/"campaign.lock").open("r") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError("Campaign is still locked by its runner; no result/resource analysis performed") from error
        statuses = []
        for cell in matrix["cells"]:
            path = directory/cell["name"]/"cell-status.json"
            if not path.exists():
                raise ValueError("All eight cells must have terminal evidence before offline analysis: " + cell["name"])
            status = read_json(path)
            if status.get("status") not in ("passed","failed") or not status.get("finishedUtc"):
                raise ValueError("Cell is not terminal: " + cell["name"])
            statuses.append(status)
        cells = []
        for cell, status in zip(matrix["cells"], statuses):
            path = directory/cell["name"]
            result_path = path/"result.json"
            command_path = path/(cell["name"]+".command.json")
            if not result_path.exists() or not command_path.exists():
                raise ValueError("Terminal cell lacks result/command JSON; retain failure records and request a separate failure-only review: " + cell["name"])
            result, command, plan = read_json(result_path), read_json(command_path), read_json(path/"plan.json")
            record = validate_and_extract(result,command,status,cell,matrix["caseNames"],policy)
            resource_name = command.get("resourceSamples")
            if not isinstance(resource_name,str) or Path(resource_name).name != resource_name:
                raise ValueError("Resource filename must be a local basename")
            resource_path = path/resource_name
            owner_path = path/"postgres-owner.json"
            owner = read_json(owner_path) if cell["provider"] == "postgresql" and owner_path.exists() else None
            resources = inspect_resources(resource_path,result,command,owner,host.get("ticksPerSecond"))
            record["resources"] = resources
            record["postgres"] = postgres_measurements(path,owner,resources)
            evidence = {"result": {"path":str(result_path),"sha256":sha_file(result_path)},
                        "command": {"path":str(command_path),"sha256":sha_file(command_path)},
                        "status": {"path":str(path/"cell-status.json"),"sha256":sha_file(path/"cell-status.json")},
                        "plan": {"path":str(path/"plan.json"),"sha256":sha_file(path/"plan.json")},
                        "resources": {"path":str(resource_path),"sha256":resources["sha256"]}}
            errors = record["checks"]["errors"]
            if status.get("resultSha256") != evidence["result"]["sha256"]:
                errors.append("result hash differs from terminal status")
            if plan.get("matrixSha256") != matrix_hash or plan.get("cell") != cell:
                errors.append("cell plan differs from frozen matrix")
            if resources["sha256"] != (command.get("files") or {}).get(resource_name):
                errors.append("resource JSONL hash differs from owner command receipt")
            stdout_path = path/(cell["name"]+".stdout.log")
            if stdout_path.exists():
                evidence["stdout"] = {"path":str(stdout_path),"sha256":sha_file(stdout_path)}
                if evidence["stdout"]["sha256"] != (command.get("files") or {}).get(stdout_path.name):
                    errors.append("stdout hash differs from owner command receipt")
            else:
                errors.append("stdout evidence missing")
            if resources["errors"]:
                errors.append("resource stream has invalid acquisition/identity/JSON records")
            if resources["fullyInsideSteadySamples"] < 2 or resources["clientIdentityMatchingInsideSamples"] < 2:
                errors.append("insufficient identity-matched steady client samples")
            if cell["provider"] == "postgresql":
                if resources["serverObservationErrors"]:
                    record["checks"]["warnings"].append("One or more server snapshots lacked a unique owner PID/startTicks identity; those snapshots are excluded from partial endpoint accounting. This is a server observation gap, not a client business failure.")
                if owner is None or not record["postgres"]["shutdownClean"]:
                    errors.append("PostgreSQL owner did not shut down cleanly")
                elif not resources["serverCpu"]["available"]:
                    record["checks"]["warnings"].append("Whole-server steady PostgreSQL CPU/RSS/PSS unavailable because descendant enumeration is incomplete or unproven. Explicit observed-subset values and OS lifetime wait4 remain separate; unknown whole-server cost is not zero.")
                if resources["serverCpu"]["negativeAdjacentSnapshotDeltas"]:
                    record["checks"]["warnings"].append("Non-atomic PG tree counters decreased at one or more adjacent snapshots; raw anomalies retained")
                for label in ("postgres-owner.json","postgres-stats-before.json","postgres-stats-after.json"):
                    if (path/label).exists():
                        evidence[label] = {"path":str(path/label),"sha256":sha_file(path/label)}
            record["checks"]["accepted"] = not errors
            record["evidence"] = evidence
            apply_exact_idle_adjudication(record,result,analysis_root)
            cells.append(record)
        summary = {"schema":SCHEMA,"generatedUtc":dt.datetime.now(dt.timezone.utc).isoformat(),
                   "matrix":{"path":str(args.matrix.resolve()),"sha256":matrix_hash},
                   "campaignDirectory":str(directory),"analysisScriptSha256":sha_file(__file__),
                   "host":host,"memoryPolicy":policy,"cellCount":len(cells),
                   "allCellsAccepted":all(cell["checks"]["accepted"] for cell in cells),
                   "allBusinessMeasurementsAccepted":all(cell["checks"]["businessMeasurementAccepted"] for cell in cells),
                   "exactIdleAdjudicationCount":sum(cell["idleAdjudication"] is not None for cell in cells),
                   "metricCoverage":{"postgresWholeServerSteadyCpuAndMemoryAvailable":False,
                                     "postgresScope":"Observed process subset and OS wait4 lifetime only; full steady tree enumeration not established by the frozen observer schema."},
                   "interpretation":{"sameObservedHostAndBoot":True,"physicalHostExclusivityEstablished":host.get("physicalHostExclusivityEstablished"),
                                     "repeatedMeasurements":False,"statisticalSignificanceClaimed":False,
                                     "gcOnlyCausalComparison":False,"saturationKneeMeasured":False,
                                     "hard192MiBProcessMemoryLimitClaimed":False,"alignmentClaimed":False},
                   "cells":cells,"relativeToDapper":compare(cells)}
        target.mkdir(parents=False,exist_ok=False)
        write_new(target/"summary.json",summary)
        write_new(target/"report.md",render_report(summary))
        write_new(target/"case-distribution.md",render_case_distribution(summary))
        write_new(target/"analysis-receipt.json",{"schema":SCHEMA,"allCellsAccepted":summary["allCellsAccepted"],
                  "allBusinessMeasurementsAccepted":summary["allBusinessMeasurementsAccepted"],
                  "exactIdleAdjudicationCount":summary["exactIdleAdjudicationCount"],
                  "sourceMatrixSha256":matrix_hash,"analysisScriptSha256":summary["analysisScriptSha256"],
                  "summarySha256":sha_file(target/"summary.json"),"reportSha256":sha_file(target/"report.md"),
                  "caseDistributionSha256":sha_file(target/"case-distribution.md"),
                  "analysisAffinity":sorted(os.sched_getaffinity(0)),"workloadExecuted":False,
                  "rawEvidenceModified":False,"outputDirectory":str(target)})
        print(json.dumps({"outputDirectory":str(target),"cellCount":len(cells),"allCellsAccepted":summary["allCellsAccepted"],"allBusinessMeasurementsAccepted":summary["allBusinessMeasurementsAccepted"],"exactIdleAdjudicationCount":summary["exactIdleAdjudicationCount"]}))
        return 0 if summary["allBusinessMeasurementsAccepted"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(type(error).__name__+": "+str(error),file=sys.stderr)
        raise SystemExit(2)
