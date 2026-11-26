#!/usr/bin/env python3
"""DB-Perf-01 numeric evidence extraction. Reads explicit inputs; never runs a consumer."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path


VERSION = 1
CASE_IDS = set("numeric text money json wide optional-filter range left-join inner-join null-notes literal-note customer-totals product-totals empty-sum cursor offset exists in-subquery cte window union-all union intersect except running-total three-join anti-association nullable-order raw-sql related tx-commit tx-rollback partial-update stale-conflict early-stop".split())
COUNTERS = "Sources Sessions Operations Cursors Buffers Owners SqlExecutions ProtocolSubmissions".split()
ROUTES = {"fluent", "prepared", "host-sql"}
RESOURCE_WINDOWS = set("cold-source-build cold-open-sessions cold-fluent-prepare-and-query-dispose cold-raw-suspended-burst pool-exhaustion-and-cancel dispose-prepared return-all-sessions close-source-including-public-cleanup-observation".split()) | {f"{prefix}-{i}" for prefix in ("warm-raw-suspended-burst", "prepared-fluent-c1", "prepared-fluent-concurrent") for i in range(3)}
RESOURCE_PHASES = RESOURCE_WINDOWS | set("before-source sessions-open-before-first-stream after-cold-burst after-warm-concurrent-bursts after-exhaustion idle-start idle-end after-source-close after-close-idle initial-open-session-baseline final-source-close".split())
PROVIDER = {"sqlite", "postgresql", "Sqlite", "PostgreSql"}
PACKAGES = set("Korda.Database.Sqlite Korda.Database.PostgreSql Dapper Dapper.AOT Microsoft.Data.Sqlite.Core Npgsql Microsoft.DotNet.ILCompiler Microsoft.NET.ILLink.Tasks runtime.linux-x64.Microsoft.DotNet.ILCompiler SQLitePCLRaw.core SQLitePCLRaw.provider.sqlite3 Microsoft.Extensions.Logging.Abstractions Microsoft.Extensions.DependencyInjection.Abstractions System.Diagnostics.DiagnosticSource".split())
NATIVE_IMAGES = {"libnw_database_sqlite.so", "libnw_database_postgresql.so", "libsqlite3.so", "libsqlite3.so.0", "libpq.so", "libpq.so.5"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def source(path):
    raw = Path(path).read_bytes()
    return {"sha256": digest(raw), "bytes": len(raw)}, raw


class SchemaError(ValueError):
    pass


class Context:
    def __init__(self):
        self.issues = []
        self.unknown = []

    def check(self, ok, code):
        if not ok and code not in self.issues:
            self.issues.append(code)

    def take(self, value, fields, ignored=(), required=()):
        if not isinstance(value, dict):
            raise SchemaError("object_required")
        foreign = set(value) - set(fields) - set(ignored)
        if foreign:
            self.unknown.append({"fieldCount": len(foreign), "fieldNamesSha256": digest(canonical(sorted(foreign)))})
            self.check(False, "unrecognized_fields")
        missing = set(required) - set(value)
        if missing:
            raise SchemaError("required_fields_missing")
        out = {}
        for key, convert in fields.items():
            if key in value:
                try:
                    out[key] = convert(value[key])
                except (ValueError, TypeError, OverflowError, KeyError) as error:
                    if isinstance(error, SchemaError):
                        raise
                    raise SchemaError("invalid_field_type") from error
        return out

    def validation(self):
        return {"numericAndSchemaChecksPassed": not self.issues, "issues": self.issues,
                "unrecognizedObjects": self.unknown, "performanceAcceptance": False}


def integer(value):
    if type(value) is not int:
        raise SchemaError("integer_required")
    return value


def natural(value):
    value = integer(value)
    if value < 0:
        raise SchemaError("nonnegative_integer_required")
    return value


def number(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise SchemaError("finite_number_required")
    return value


def nonnegative(value):
    value = number(value)
    if value < 0:
        raise SchemaError("nonnegative_number_required")
    return value


def boolean(value):
    if type(value) is not bool:
        raise SchemaError("boolean_required")
    return value


def exact(options):
    def convert(value):
        if not isinstance(value, str) or value not in options:
            raise SchemaError("unknown_enum_value")
        return value
    return convert


def pattern(regex):
    def convert(value):
        if not isinstance(value, str) or not re.fullmatch(regex, value):
            raise SchemaError("invalid_identity_format")
        return value
    return convert


sha = pattern(r"[0-9a-f]{64}")
commit = pattern(r"[0-9a-f]{40}")
version = pattern(r"[0-9]+(?:\.[0-9]+){1,3}(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?")
label = pattern(r"[a-z0-9][a-z0-9/-]{0,127}")


def package_version(value):
    if isinstance(value, str) and value.startswith("Dapper.AOT/"):
        pairs = value.split(";")
        names = []
        for pair in pairs:
            name, ver = pair.split("/", 1)
            exact({"Dapper.AOT", "Dapper", "Npgsql", "Microsoft.Data.Sqlite.Core"})(name)
            version(ver)
            names.append(name)
        if len(names) != len(set(names)) or set(names) not in ({"Dapper.AOT", "Dapper", "Npgsql"}, {"Dapper.AOT", "Dapper", "Microsoft.Data.Sqlite.Core"}):
            raise SchemaError("unexpected_dapper_package_set")
        return value
    return version(value)


def database_version(value):
    if not isinstance(value, str):
        raise SchemaError("database_version_string_required")
    match = re.match(r"(?:PostgreSQL )?([0-9]+(?:\.[0-9]+){1,3})(?: |$)", value)
    if not match:
        raise SchemaError("unrecognized_database_version")
    out = {"version": match[1], "original": fingerprint(value)}
    compiler = re.search(r"clang version ([0-9]+(?:\.[0-9]+){1,3})(?: |$)", value)
    if compiler:
        out["clangVersion"] = compiler[1]
    return out


def timestamp(value):
    if not isinstance(value, str) or len(value) > 40:
        raise SchemaError("invalid_timestamp")
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise SchemaError("timestamp_timezone_missing")
    return parsed.isoformat()


def maybe(convert):
    return lambda value: None if value is None else convert(value)


def array(convert):
    def apply(values):
        if not isinstance(values, list):
            raise SchemaError("array_required")
        return [convert(value) for value in values]
    return apply


def fingerprint(value):
    raw = canonical(value)
    return {"sha256": digest(raw), "canonicalJsonBytes": len(raw)}


def errors(values):
    if not isinstance(values, list):
        raise SchemaError("error_array_required")
    return {"retainedEntryCount": len(values), "entries": [fingerprint(value) for value in values]}


def fields(names, convert=natural):
    return {key: convert for key in names.split()}


def count_object(ctx, value):
    return ctx.take(value, {**{key: natural for key in COUNTERS}, "ApplicationConnections": natural}, ignored={"Scope"})


def process(ctx, value):
    return ctx.take(value, {**fields("UserCpuSeconds SystemCpuSeconds", nonnegative),
                           **fields("RssBytes PeakRssBytes"), "PssBytes": maybe(natural)}, required=("UserCpuSeconds", "SystemCpuSeconds", "RssBytes", "PeakRssBytes"))


def histogram(values):
    values = array(natural)(values)
    if len(values) != 8192:
        raise SchemaError("histogram_requires_8192_bins")
    return values


def percentile(values, percent):
    total = sum(values)
    if not total:
        return None
    rank, count = (total * percent + 99) // 100, 0
    for index, value in enumerate(values):
        count += value
        if count >= rank:
            return float(Fraction((1 << (index // 128)) * (129 + index % 128), 128000))
    raise AssertionError("unreachable")


def close(actual, expected):
    return actual is None and expected is None or type(actual) in (int, float) and type(expected) in (int, float) and abs(actual - expected) <= max(1e-8, abs(expected) * 1e-10)


def latencies(ctx, value):
    return ctx.take(value, {**fields("P50MicrosecondsUpper P95MicrosecondsUpper P99MicrosecondsUpper", nonnegative),
                            "Histogram": histogram}, ignored={"Method"}, required=("Histogram",))


def error_detail(ctx, value):
    if value is None:
        return None
    if not isinstance(value, dict):
        return {"omittedValue": fingerprint(value)}
    return ctx.take(value, {"HResult": integer, "CorrelationId": maybe(natural), "IsTransient": maybe(boolean),
                           "DatabaseKind": maybe(exact({"Provider", "Usage", "ResourceLimit", "Canceled", "Protocol", "Unsupported", "Unknown", "Timeout"})),
                           "ProviderCode": maybe(pattern(r"(?:[0-9A-Z]{5}|-?[0-9]{1,12})")),
                           "Type": fingerprint, "StackTrace": maybe(fingerprint),
                           "Inner": array(lambda v: error_detail(ctx, v))}, ignored={"Message", "Data"})


def oracle_failure(ctx, value):
    if value is None:
        return None
    return ctx.take(value, {"Sequence": natural, "Phase": fingerprint, "CaseId": maybe(exact(CASE_IDS)),
                           "Message": fingerprint, "InnerError": maybe(fingerprint), "ObservedStack": fingerprint,
                           "ObservedTicks": natural, "TimerFrequency": natural}, ignored=())


def mixed(ctx, raw):
    second = lambda v: ctx.take(v, fields("Second Completed Rows Failed"), required=("Second", "Completed", "Rows", "Failed"))
    case = lambda v: ctx.take(v, {"Name": exact(CASE_IDS), **fields("Started Succeeded Failed Rows Suspensions")}, required=("Name", "Started", "Succeeded", "Failed", "Rows"))
    expected = lambda v: {exact(CASE_IDS)(k): ctx.take(z, fields("Rows Digest Suspensions"), required=("Rows", "Digest")) for k, z in v.items()}
    idle = lambda v: ctx.take(v, {**fields("RequestedSeconds ObservedSeconds UserCpuSeconds SystemCpuSeconds", nonnegative),
                                 **fields("ManagedBytesBefore ManagedBytesAfter"), "StartedUtc": timestamp, "FinishedUtc": timestamp,
                                 "Before": lambda z: process(ctx, z), "After": lambda z: process(ctx, z)}, ignored={"Scope"})
    out = ctx.take(raw, {
        **fields("SchemaVersion Concurrency WarmupPerWorker RequestedRows BatchRows Tenants OrdersPerTenant SteadyStartMonotonicNs SteadyEndMonotonicNs Planned Started Completed Failed Retries Rows ActualStreamSuspensions AllocatedBefore AllocatedAfter AllocatedBytes Gen0 Gen1 Gen2 OracleFailuresBefore OracleFailuresAfter OracleFailures"),
        **fields("EffectiveSeconds BytesPerSuccessfulOperation BytesPerRow UserCpuSeconds SystemCpuSeconds CpuSecondsPerSuccessfulOperation", nonnegative),
        **fields("NativeAot EmptyDriver OwnersReturnedToZero ApplicationConnectionsReturnedToZero TimeSeriesTruncated TimingComparisonEligible", boolean),
        "Route": exact({"korda-public-fluent", "independent-csharp-micro-orm-dapper-aot"}), "Provider": exact(PROVIDER | {"Microsoft.Data.Sqlite.Core", "Npgsql"}), "PackageVersion": package_version,
        "ExecutableSha256": sha, "LoadedNativeSha256": maybe(sha), "Case": exact(CASE_IDS | {"mixed"}),
        "ActualCaseIds": array(exact(CASE_IDS)), "Mode": exact({"dynamic", "prepared"}), "SessionMode": exact({"persistent", "per-operation"}),
        "StartedUtc": timestamp, "FinishedUtc": timestamp, "Scheduling": fingerprint,
        "ProcessBefore": lambda v: process(ctx, v), "ProcessAfter": lambda v: process(ctx, v),
        "Before": lambda v: count_object(ctx, v), "After": lambda v: count_object(ctx, v), "Drained": lambda v: count_object(ctx, v),
        "Latencies": lambda v: latencies(ctx, v), "Seconds": array(second), "Cases": array(case), "ExpectedResults": expected,
        "Errors": errors, "Idle": maybe(idle), "OfferedLoad": maybe(fingerprint), "NativeAllocationProfile": maybe(fingerprint),
        "FirstOracleFailure": lambda v: oracle_failure(ctx, v), "DatabaseVersion": database_version, "SqliteCompileOptions": fingerprint,
        "CaseModeContracts": fingerprint, "TransactionContract": fingerprint, "ActualDiagnosticSql": fingerprint,
        "QueryReuseContract": fingerprint, "AllocationAttribution": fingerprint, "EmptyDriverScope": fingerprint,
    }, ignored={"LoadedNativePath"}, required=("SchemaVersion", "NativeAot", "ExecutableSha256", "Completed", "Failed", "Rows", "AllocatedBefore", "AllocatedAfter", "AllocatedBytes", "EffectiveSeconds", "Latencies", "Seconds", "Cases", "ProcessBefore", "ProcessAfter", "Errors"))
    ctx.check(out["SchemaVersion"] == 1, "mixed_schema_version")
    ctx.check(raw.get("OfferedLoad") is None, "offered_load_requires_separate_whitelist")
    ctx.check(raw.get("NativeAllocationProfile") is None, "native_profile_requires_separate_whitelist")
    ctx.check(raw.get("TimeSeriesTruncated") is False, "time_series_truncated")
    ctx.check(out["AllocatedAfter"] - out["AllocatedBefore"] == out["AllocatedBytes"], "allocation_endpoint_mismatch")
    ctx.check(out.get("Started") == out["Completed"] + out["Failed"], "terminal_counter_mismatch")
    ctx.check(out.get("Planned") == out.get("Started"), "closed_loop_planned_mismatch")
    ctx.check(out.get("SteadyEndMonotonicNs", 0) > out.get("SteadyStartMonotonicNs", 0), "mixed_clock_reversed")
    ctx.check(abs((out.get("SteadyEndMonotonicNs", 0) - out.get("SteadyStartMonotonicNs", 0)) / 1e9 - out["EffectiveSeconds"]) <= 0.05, "mixed_elapsed_clock_mismatch")
    ctx.check(0 <= out.get("OracleFailuresBefore", 0) <= out.get("OracleFailuresAfter", 0) <= out.get("OracleFailures", 0), "oracle_counter_reversed")
    ctx.check((out["Errors"]["retainedEntryCount"] > 0) == (out["Failed"] > 0), "failure_diagnostic_count_mismatch")
    ctx.check(sum(out["Latencies"]["Histogram"]) == out["Completed"], "histogram_population_mismatch")
    ctx.check([s["Second"] for s in out["Seconds"]] == list(range(len(out["Seconds"]))), "second_sequence_mismatch")
    for name in ("Completed", "Rows", "Failed"):
        ctx.check(sum(s[name] for s in out["Seconds"]) == out[name], "second_counter_mismatch_" + name)
    ctx.check(len({c["Name"] for c in out["Cases"]}) == len(out["Cases"]), "duplicate_case")
    for name, total in (("Started", "Started"), ("Succeeded", "Completed"), ("Failed", "Failed"), ("Rows", "Rows")):
        ctx.check(sum(c[name] for c in out["Cases"]) == out[total], "case_counter_mismatch_" + name)
    for c in out["Cases"]:
        ctx.check(c["Started"] == c["Succeeded"] + c["Failed"], "case_terminal_mismatch")
        expected_rows = out.get("ExpectedResults", {}).get(c["Name"], {}).get("Rows")
        ctx.check(expected_rows is not None and c["Rows"] == c["Succeeded"] * expected_rows, "case_expected_rows_mismatch")
    duration, completed = out["EffectiveSeconds"], out["Completed"]
    ctx.check(duration > 0, "nonpositive_duration")
    recomputed = {"successfulOperations": completed, "failedOperations": out["Failed"], "rows": out["Rows"],
                  "seconds": duration, "successOpsPerSecond": completed / duration if duration else None,
                  "rowsPerSecond": out["Rows"] / duration if duration else None,
                  "failedFractionOfStarted": out["Failed"] / out["Started"] if out["Started"] else None,
                  "allocatedBytes": out["AllocatedAfter"] - out["AllocatedBefore"],
                  "bytesPerSuccessfulOperation": out["AllocatedBytes"] / completed if completed else None,
                  "gen0": out.get("Gen0"), "gen1": out.get("Gen1"), "gen2": out.get("Gen2")}
    for p in (50, 95, 99):
        value = percentile(out["Latencies"]["Histogram"], p)
        recomputed[f"p{p}MicrosecondsUpper"] = value
        ctx.check(close(out["Latencies"].get(f"P{p}MicrosecondsUpper"), value) or completed == 0, "histogram_percentile_mismatch")
    for name in ("UserCpuSeconds", "SystemCpuSeconds"):
        delta = out["ProcessAfter"][name] - out["ProcessBefore"][name]
        recomputed[name[0].lower() + name[1:]] = delta
        ctx.check(delta >= 0 and close(out.get(name), delta), "cpu_endpoint_mismatch")
    if completed:
        ctx.check(close(out.get("BytesPerSuccessfulOperation"), recomputed["bytesPerSuccessfulOperation"]), "bytes_per_operation_mismatch")
    return {"kind": "mixed", "data": out, "recomputed": recomputed,
            "correctnessObserved": {"oracleFailures": out.get("OracleFailures"),
                                     "firstOracleFailurePresent": out.get("FirstOracleFailure") is not None,
                                     "ownershipReturnedToZero": out.get("OwnersReturnedToZero", out.get("ApplicationConnectionsReturnedToZero")),
                                     "timingComparisonEligibleReportedByProducer": out.get("TimingComparisonEligible")}}


def phase(ctx, raw):
    sample_fields = fields("ConstructTicks SubmitToFirstRowTicks ReadCompleteTicks ReleaseTicks Rows")
    sample = lambda v: ctx.take(v, sample_fields, required=sample_fields)
    win_fields = {"Route": exact(ROUTES), **fields("Index Operations AllocatedBefore AllocatedAfter Gen0 Gen1 Gen2 CpuBeforeTicks CpuAfterTicks ResidentBytes PeakResidentBytes StartedTicks FinishedTicks"),
                  "NativeBefore": lambda v: count_object(ctx, v), "NativeAfter": lambda v: count_object(ctx, v), "Samples": array(sample)}
    out = ctx.take(raw, {**fields("SchemaVersion StopwatchFrequency PreparationTicks WarmupPerRoute TeardownTicks"),
                        "Provider": exact(PROVIDER), "NativeAot": boolean, "DatabaseVersion": database_version, "PackageVersion": package_version,
                        "ExecutableSha256": sha, "NativeSha256": sha, "Sql": fingerprint, "RawTemplate": fingerprint,
                        "ParametersAndResults": fingerprint, "Scope": fingerprint,
                        "FirstExecutions": array(sample), "Windows": array(lambda v: ctx.take(v, win_fields, required=win_fields)),
                        "Drained": lambda v: count_object(ctx, v)}, ignored={"NativePath"}, required=("SchemaVersion", "StopwatchFrequency", "NativeAot", "ExecutableSha256", "Windows", "FirstExecutions", "Drained"))
    ctx.check(out["SchemaVersion"] == 2, "phase_schema_version")
    ctx.check(out["StopwatchFrequency"] > 0, "phase_timer_frequency")
    ctx.check(len(out["FirstExecutions"]) == 3, "phase_first_execution_count")
    totals = {}
    for w in out["Windows"]:
        ctx.check(len(w["Samples"]) == w["Operations"], "phase_sample_count")
        ctx.check(w["AllocatedAfter"] >= w["AllocatedBefore"], "phase_allocation_reversed")
        ctx.check(w["CpuAfterTicks"] >= w["CpuBeforeTicks"], "phase_cpu_reversed")
        ctx.check(w["FinishedTicks"] >= w["StartedTicks"], "phase_timer_reversed")
        ctx.check(all(s["Rows"] == 100 for s in w["Samples"]), "phase_row_count")
        t = totals.setdefault(w["Route"], {"operations": 0, "allocatedBytes": 0, "cpuTicks100ns": 0, "windowTicks": 0,
                                          "gen0": 0, "gen1": 0, "gen2": 0, **{n: 0 for n in sample_fields if n != "Rows"}})
        t["operations"] += w["Operations"]
        t["allocatedBytes"] += w["AllocatedAfter"] - w["AllocatedBefore"]
        t["cpuTicks100ns"] += w["CpuAfterTicks"] - w["CpuBeforeTicks"]
        t["windowTicks"] += w["FinishedTicks"] - w["StartedTicks"]
        for key in ("Gen0", "Gen1", "Gen2"):
            t[key.lower()] += w[key]
        for key in sample_fields:
            if key != "Rows":
                t[key] += sum(s[key] for s in w["Samples"])
    for t in totals.values():
        t["bytesPerOperation"] = t["allocatedBytes"] / t["operations"] if t["operations"] else None
        t["cpuSeconds"] = t["cpuTicks100ns"] / 10_000_000
        t["wallSeconds"] = t["windowTicks"] / out["StopwatchFrequency"] if out["StopwatchFrequency"] else None
    return {"kind": "phase", "data": out, "recomputed": totals,
            "firstExecutionRoutesInOrder": ["fluent", "prepared", "host-sql"], "cpuTicksPerSecond": 10_000_000}


def resource_probe(ctx, raw):
    counts = lambda v: ctx.take(v, fields("AllocatedBytes Gen0 Gen1 Gen2 Timestamp"), required=("AllocatedBytes", "Gen0", "Gen1", "Gen2", "Timestamp"))
    window_fields = {"Name": exact(RESOURCE_WINDOWS), "Start": counts, "End": counts,
                     **fields("Operations Succeeded Failed Rows Checksum PendingFirstMovesBeforeAnyConsumption IssuingThread EndingThread PlannedOperations PendingAtReturnCount RuntimePoolCacheCapacityForIssuingThread RawAllocatedBytes"),
                     "PendingAtReturn": array(boolean), "PendingBeforeConsumption": array(boolean),
                     **fields("SingleIssuingThread UnconsumedSuspensionsExceedCacheCapacity", boolean),
                     "BoundaryError": maybe(fingerprint), "FrameworkAllocatedBytes": maybe(natural)}
    memory_fields = {"Phase": exact(RESOURCE_PHASES), **fields("Timestamp ManagedLiveBytesAfterForcedGc ThreadPoolThreads RssBytes PeakRssBytes"), "PssBytes": maybe(natural),
                     **fields("UserSeconds SystemSeconds", nonnegative), "BeforeForcedGc": counts, "AfterForcedGc": counts}
    settlement_fields = {"Phase": exact(RESOURCE_PHASES), "Immediate": array(natural), "Settled": array(natural), "Expected": maybe(array(natural)),
                         "Start": counts, "End": counts, "Polls": natural, "Matched": boolean}
    out = ctx.take(raw, {"Schema": exact({"DB-Perf-01.public-resource-inventory.v1"}), "SourceCommit": commit,
                        "PackageSha256": sha, "ExecutableSha256": sha, "NativeSha256": sha, "Provider": exact(PROVIDER),
                        **fields("ProcessId ProcessorCount Concurrency SuspendedQuerySteps PendingOpensBeforeCancellation MatchingCanceledOpenResults ResourceLimitOpenResults ExhaustionAdmissionWaitMilliseconds"),
                        **fields("NativeAot PendingCancellationObserved SourceReleased Passed", boolean),
                        "ProcessorCountOverride": maybe(lambda v: natural(int(v)) if isinstance(v, str) and v.isdigit() else natural(v)),
                        **fields("IdleUserSeconds IdleSystemSeconds IdleElapsedSeconds", nonnegative),
                        "StartedUtc": timestamp, "FinishedUtc": timestamp,
                        "Windows": array(lambda v: ctx.take(v, window_fields, ignored={"FrameworkStatus"}, required=("Name", "Start", "End", "Operations", "Succeeded", "Failed", "RawAllocatedBytes"))),
                        "Memory": array(lambda v: ctx.take(v, memory_fields)),
                        "NativeObservations": array(lambda v: ctx.take(v, {"Phase": exact(RESOURCE_PHASES), "Counters": array(natural)})),
                        "OwnerSettlements": array(lambda v: ctx.take(v, settlement_fields)),
                        **{name: array(natural) for name in ("WarmOwners", "OwnersAfterExhaustion", "FinalOwners")},
                        "ExhaustionExceptions": errors, "CleanupErrors": errors, "Error": maybe(fingerprint),
                        **{name: fingerprint for name in ("Runtime", "SuspendedQuerySql", "Scope", "BusinessOutput", "SetupBoundary", "RetentionScope", "SuspensionScope")}},
                        ignored={"NativePath"}, required=("Schema", "SourceCommit", "ExecutableSha256", "Windows", "FinalOwners", "Passed"))
    totals = []
    for w in out["Windows"]:
        start, end = w["Start"], w["End"]
        ctx.check(w["Operations"] == w["Succeeded"] + w["Failed"], "resource_window_terminal_mismatch")
        delta = end["AllocatedBytes"] - start["AllocatedBytes"]
        ctx.check(delta >= 0 and delta == w["RawAllocatedBytes"], "resource_allocation_mismatch")
        gc = [end[f"Gen{i}"] - start[f"Gen{i}"] for i in range(3)]
        ctx.check(all(v >= 0 for v in gc), "resource_gc_reversed")
        totals.append({"name": w["Name"], "operations": w["Operations"], "succeeded": w["Succeeded"], "failed": w["Failed"],
                       "allocatedBytes": delta, "gc": gc, "rawWindowTicks": end["Timestamp"] - start["Timestamp"]})
    return {"kind": "resource", "data": out, "recomputed": totals, "longRunAcceptance": False,
            "frameworkAllocationSplitProved": False, "resourceWindowTimerFrequencySerialized": False}


def process_tree_item(ctx, value):
    return ctx.take(value, {**fields("pid startTicks parentPid userTicks systemTicks reapedChildUserTicks reapedChildSystemTicks threads"),
                            "state": exact(set("RSDZTtXxKWPI")),
                            "memoryBytes": lambda v: ctx.take(v, fields("Rss Pss Private_Clean Private_Dirty")),
                            "memoryErrors": errors})


def cpu_group(ctx, value):
    if value is None:
        return None
    return ctx.take(value, {"deviceInode": array(natural), "membersVerified": boolean,
                           "serverIdentity": lambda v: process_tree_item(ctx, v),
                           "members": array(lambda v: process_tree_item(ctx, v)),
                           "exitedDuringMemberAcquisition": array(natural),
                           "cpu": lambda v: ctx.take(v, fields("usage_usec user_usec system_usec nice_usec core_sched.force_idle_usec nr_periods nr_throttled throttled_usec nr_bursts burst_usec")),
                           "path": fingerprint, "parent": fingerprint, "controls": fingerprint,
                           "monotonicNs": natural, "acquiredThroughMonotonicNs": natural,
                           "ownerPid": natural}, ignored=())


def quota(ctx, value):
    # Exact numeric snapshots survive; opaque paths and unproved ancestry do not become claims.
    def node(v):
        out = ctx.take(v, {"root": boolean, "quotaStatus": exact({"read", "root_has_no_cpu_max", "cpu_controller_not_enabled_for_group"}),
                           "path": fingerprint, "cpu.max": fingerprint, "cpuset.cpus.effective": fingerprint,
                           "cpu.stat": fingerprint, "parentSubtreeControl": fingerprint}, ignored=())
        text = v.get("cpu.stat")
        if isinstance(text, str):
            counters = {}
            allowed = set("usage_usec user_usec system_usec nice_usec core_sched.force_idle_usec nr_periods nr_throttled throttled_usec nr_bursts burst_usec".split())
            for line in text.splitlines():
                pair = line.split()
                if len(pair) != 2 or pair[0] not in allowed or not pair[1].isdigit() or pair[0] in counters:
                    raise SchemaError("unsupported_quota_cpu_stat")
                counters[pair[0]] = int(pair[1])
            out["cpuCounters"] = counters
        maximum = v.get("cpu.max")
        if isinstance(maximum, str):
            pair = maximum.split()
            if len(pair) != 2 or not pair[1].isdigit() or not (pair[0].isdigit() or pair[0] == "max"):
                raise SchemaError("unsupported_quota_cpu_max")
            out["cpuQuota"] = {"maximumMicroseconds": None if pair[0] == "max" else int(pair[0]), "periodMicroseconds": int(pair[1])}
        return out
    return ctx.take(value, {"schemaVersion": natural, "available": boolean, "sameCgroupNamespaceAsInit": boolean,
                           "ancestors": array(node), "reason": fingerprint, "namespaceObservation": fingerprint,
                           "hostInit": fingerprint}, ignored={"membershipSource", "membership", "mountPoint", "mountRoot"})


def resource_sample(ctx, value):
    totals = lambda v: ctx.take(v, {**fields("ownAndReapedUserTicks ownAndReapedSystemTicks sampledRssBytes sampledPssBytes memoryAvailableProcessCount processCount"),
                                    **fields("rssComplete pssComplete treeSnapshotNonAtomic", boolean)})
    out = ctx.take(value, {"utc": timestamp, **fields("monotonicNs acquiredThroughMonotonicNs"),
                          "client": array(lambda v: process_tree_item(ctx, v)), "server": array(lambda v: process_tree_item(ctx, v)),
                          "clientTotals": totals, "serverTotals": totals, "serverCpuGroup": lambda v: cpu_group(ctx, v),
                          "hostCpuTicks": lambda v: ctx.take(v, fields("user nice system idle iowait irq softirq steal guest guestNice")),
                          "guestQuota": lambda v: quota(ctx, v)}, required=("monotonicNs", "acquiredThroughMonotonicNs", "client", "server", "clientTotals", "serverTotals"))
    ctx.check(out["acquiredThroughMonotonicNs"] >= out["monotonicNs"], "resource_acquisition_reversed")
    for side in ("client", "server"):
        vals, t = out[side], out[side + "Totals"]
        ctx.check(len({v["pid"] for v in vals}) == len(vals), "resource_duplicate_pid")
        for key, expected in (("processCount", len(vals)),
                              ("sampledRssBytes", sum(v["memoryBytes"].get("Rss", 0) for v in vals)),
                              ("sampledPssBytes", sum(v["memoryBytes"].get("Pss", 0) for v in vals)),
                              ("ownAndReapedUserTicks", sum(v["userTicks"] + v["reapedChildUserTicks"] for v in vals)),
                              ("ownAndReapedSystemTicks", sum(v["systemTicks"] + v["reapedChildSystemTicks"] for v in vals))):
            ctx.check(t.get(key) == expected, "resource_tree_total_mismatch")
    return out


def observer(ctx, raw):
    return ctx.take(raw, {**fields("startedMonotonicNs finishedMonotonicNs timeoutSeconds processLifetimeMaxRssBytes"),
                          **fields("processLifetimeUserCpuSeconds processLifetimeSystemCpuSeconds", nonnegative),
                          **fields("longRunAcceptance timedOut success", boolean), "exitCode": integer,
                          "startedUtc": timestamp, "finishedUtc": timestamp, "observerErrors": errors,
                          "clientIdentity": lambda v: process_tree_item(ctx, v),
                          "serverCpuGroupIdentity": lambda v: cpu_group(ctx, v)},
                          ignored={"name", "phase", "argv", "resourceSamples", "measurementScope", "lastSample", "files"})


def identity(ctx, raw):
    package = lambda v: ctx.take(v, {"id": exact(PACKAGES), "version": version, "sha256": sha,
                                    **fields("signedArchive publisherSignatureReverified", boolean)},
                                    ignored={"path", "archiveSha512Base64", "nugetRestoreContentHash"}, required=("id", "version", "sha256"))
    def app(v):
        return ctx.take(v, {"id": label, "provider": exact({"sqlite", "postgresql"}), "kind": exact({"mixed", "phase", "resource"}),
                            "route": exact({"before", "baseline", "recovered", "candidate", "dapper"}), "executableSha256": sha,
                            "buildReceiptSha256": sha, "elf": lambda z: ctx.take(z, {"format": exact({"ELF64"}), "architecture": exact({"x86-64", "Advanced Micro Devices X86-64", "x86_64"}), "elfType": natural}),
                            "packages": array(package), "nativeImages": lambda z: {exact(NATIVE_IMAGES)(k): sha(w) for k, w in z.items()},
                            "harnessSources": fingerprint,
                            "buildSettings": lambda z: ctx.take(z, {"configuration": exact({"Release"}), "rid": exact({"linux-x64"}),
                                "sdk": lambda w: ctx.take(w, {"version": version, "rollForward": exact({"latestPatch"}), "allowPrerelease": boolean}),
                                "commonDeclarations": fingerprint, "routeSpecificDeclarations": fingerprint}, ignored={"providerDefine", "gcScope"})},
                            ignored={"buildDirectory", "executable", "generatedFileCount", "runtimeFileCount"}, required=("id", "executableSha256", "packages", "elf"))
    out = ctx.take(raw, {"schemaVersion": natural, "createdUtc": timestamp, "workloadManifestSha256": sha,
                        "provenance": lambda v: ctx.take(v, {"producerMerge": commit, "tree": commit, "prHead": commit,
                                                            "workflowRun": natural, "repository": exact({"IzuSharp/Korda"}), "localSourceTree": commit}, ignored={"scope"}),
                        "apps": array(app), "comparisons": fingerprint},
                        ignored={"task", "status", "performanceExecutedByHelper", "performanceAcceptance", "ciGateAcceptance", "packageHashScope", "planBindings", "files", "collections", "absentBuildControls"},
                        required=("schemaVersion", "provenance", "apps", "workloadManifestSha256"))
    ctx.check(len({a["id"] for a in out["apps"]}) == len(out["apps"]), "identity_duplicate_app")
    out["externalNativeImages"] = []
    for item in raw.get("files", []):
        if item.get("roles") == ["dapper-sqlite-native"]:
            out["externalNativeImages"].append({"role": "dapper-sqlite-native", "sha256": sha(item["sha256"]), "bytes": natural(item["bytes"])})
    return out


def workload(ctx, raw):
    def query(v):
        return ctx.take(v, {"name": exact(CASE_IDS), "expectedRows": natural, "consumeRows": natural,
                            "expectedDigest": lambda x: natural(int(x)) if isinstance(x, str) and x.isdigit() else natural(x),
                            "queryExecutionsPerOperation": natural, "writesDatabase": boolean,
                            "sql": fingerprint, "parameters": fingerprint, "columns": fingerprint,
                            "operationKind": fingerprint, "lifecycle": fingerprint, "related": fingerprint},
                            ignored={"entry", "expectedDigestHex", "materialization", "preparedContract", "construction", "validation", "knownLimitation", "moneyStorage"},
                            required=("name", "expectedRows", "expectedDigest"))
    return ctx.take(raw, {"schemaVersion": natural, "queries": array(query)},
                    ignored={"dataset", "digest", "validationInputs", "postgresStatementLog", "readContractSource", "lifecycleContractSource"}, required=("schemaVersion", "queries"))


def failure_review(ctx, raw):
    # Specific reviewed receipt schema. Narrative strings are deliberately not copied.
    complete = lambda v: ctx.take(v, {"name": label, **fields("success timingCredit", boolean),
                                      **fields("operations completeRowsPerOperation"), "elapsedSeconds": nonnegative,
                                      "executableSha256": sha, "nativeSha256": sha, "drained": lambda z: count_object(ctx, z)}, ignored={"databaseVersion"})
    original = ctx.take(raw["originalFailure"], {"name": label, "exitCode": integer, "timedOut": boolean,
                       "observerErrors": errors, "startedUtc": timestamp, "finishedUtc": timestamp,
                       **fields("elapsedSeconds clientProcessLifetimeCpuSeconds", nonnegative), "clientProcessLifetimeMaxRssBytes": natural,
                       "resultFilePresent": boolean, "serverShutdownExitCode": integer, "serverFinishedUtc": timestamp,
                       "serverShutdownWasAfterObservedClientFailure": boolean, "exceptionType": fingerprint,
                       "unknownFields": fingerprint}, ignored={"message", "observedBoundary", "signalInterpretation", "finalOwnerDrain", "startupFatal", "classification"})
    reproduction = ctx.take(raw["boundedReproduction"], {**fields("authorizedMaximumProcesses executedProcesses"),
                           **fields("reproduced originalFailureFixed timingCredit", boolean), "processes": array(complete),
                           "postgresOwnerExitCode": integer, "postgresOwnerFinishedUtc": timestamp})
    def observation(v):
        return ctx.take(v, {"Boundary": exact({"query", "dispose", "unhandled"}), "Area": exact({"first", "window", "setup", "prepare", "teardown"}),
                            "Route": exact(ROUTES), "Window": integer, "Iteration": integer,
                            "Stage": exact({"Construct", "First", "Read", "Release", "None"}),
                            **fields("CompletedWindows RowsConsumed ObservedTicks"), "NativeCounts": lambda z: count_object(ctx, z),
                            "NativeCountsUnavailable": maybe(fingerprint), "Error": lambda z: error_detail(ctx, z)})
    forced = ctx.take(raw["intentionalHandlerValidation"], {**fields("authorizedProcesses executedProcesses"),
                      **fields("runnerExitCode consumerExitCode postgresOwnerExitCode", integer),
                      **fields("commandSuccess diagnosticAssertionsSatisfied isSuccessfulComparisonCell timingCredit", boolean),
                      "observation": observation, "postgresOwnerFinishedUtc": timestamp}, ignored={"purpose", "coverageLimit"})
    src = ctx.take(raw["diagnosticSource"], {**fields("successSchema"), "baseCommit": commit, "builtCommit": commit,
                   "builtProgramSha256": sha, "guardFollowupCommit": commit, "guardFollowupWasNotInExecutedElf": boolean},
                   ignored={"filesChanged", "change", "steadyOverhead", "excludedData", "changedCommittedImpact", "independentReview"})
    ctx.check(raw.get("schemaVersion") == 1, "failure_review_schema")
    ctx.check(raw.get("performanceAcceptance") is False, "failure_review_acceptance_claim")
    ctx.check(reproduction.get("originalFailureFixed") is False and reproduction.get("reproduced") is False, "failure_review_conclusion_changed")
    ctx.check(forced.get("isSuccessfulComparisonCell") is False and forced.get("timingCredit") is False, "forced_failure_comparison_claim")
    return {"schemaVersion": 1, "originalFailure": original, "originalCompleteProcesses": [complete(v) for v in raw["originalCompleteProcesses"]],
            "originalNotStartedCommands": array(label)(raw["originalNotStartedCommands"]), "boundedReproduction": reproduction,
            "intentionalHandlerValidation": forced, "diagnosticSource": src,
            "originalCauseResolved": False, "originalFailureFixed": False, "diagnosticsReplaceOriginalAttempt": False,
            "forcedFailureReproducesOriginal": False, "performanceAcceptance": False}


def phase_failure(ctx, raw):
    observation = lambda v: ctx.take(v, {"Boundary": exact({"query", "dispose", "unhandled", "primary", "cleanup"}),
        "Area": exact({"first", "window", "setup", "prepare", "teardown", "warmup", "receipt"}),
        "Route": maybe(exact(ROUTES)), "Window": integer, "Iteration": integer,
        "Stage": exact({"Setup", "Construct", "First", "Read", "Release", "Verify", "Receipt"}),
        "CompletedWindows": natural, "RowsConsumed": maybe(natural), "ObservedTicks": natural,
        "NativeCounts": maybe(lambda z: count_object(ctx, z)), "NativeCountsUnavailable": maybe(fingerprint),
        "Error": lambda z: error_detail(ctx, z)})
    out = ctx.take(raw, {**fields("SchemaVersion SuccessReceiptSchemaVersion StopwatchFrequency DroppedObservations"),
                        "Provider": exact(PROVIDER), "DatabaseVersion": maybe(database_version), "PackageVersion": package_version,
                        "ExecutableSha256": sha, "NativeSha256": maybe(sha), "IsTerminating": boolean, "TimingCredit": boolean,
                        "CaptureErrorType": maybe(fingerprint), "Observations": array(observation)}, ignored={"Scope"})
    ctx.check(out.get("SchemaVersion") == 1 and out.get("SuccessReceiptSchemaVersion") == 2, "phase_failure_schema")
    ctx.check(out.get("TimingCredit") is False, "phase_failure_timing_claim")
    return out


def write_json(path, data):
    with Path(path).open("xb") as stream:
        stream.write(canonical(data) + b"\n")
    return source(path)[0]


def extract_bundle(manifest_path, output):
    manifest_meta, manifest_bytes = source(manifest_path)
    manifest = json.loads(manifest_bytes)
    if manifest.get("schemaVersion") != 1 or not isinstance(manifest.get("entries"), list):
        raise SchemaError("manifest_schema")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    index = {"schemaVersion": VERSION, "extractorSha256": source(__file__)[0]["sha256"],
             "localInputManifest": manifest_meta, "performanceAcceptance": False, "files": [], "entries": [], "validationIssues": []}
    apps, external_native = {}, set()
    for key, convert in (("identity", identity), ("workload", workload), ("failureReview", failure_review)):
        if key not in manifest:
            continue
        ctx = Context()
        meta, data = source(manifest[key])
        try:
            converted = convert(ctx, json.loads(data))
        except (ValueError, TypeError, KeyError) as error:
            converted = None
            ctx.check(False, str(error) if isinstance(error, SchemaError) else "schema_parse_failure")
        payload = {"schemaVersion": VERSION, "original": meta, "data": converted, "validation": ctx.validation()}
        if key == "identity" and converted:
            apps = {a["id"]: a for a in converted["apps"]}
            external_native = {i["sha256"] for i in converted["externalNativeImages"]}
        name = key + ".numeric.json"
        index["files"].append({"name": name, **write_json(output / name, payload)})
        if ctx.issues:
            index["validationIssues"].append({"section": key, "issues": ctx.issues})
    seen = set()
    for entry in manifest["entries"]:
        eid, kind = label(entry["id"]), exact({"mixed", "phase", "resource", "setup"})(entry["kind"])
        if eid in seen:
            raise SchemaError("duplicate_entry_identity")
        seen.add(eid)
        ctx, originals = Context(), {}
        extracted, obs, failure = None, None, None
        for role in ("result", "observer", "failure"):
            path = entry.get(role)
            if path and Path(path).is_file():
                meta, blob = source(path)
                originals[role] = meta
                try:
                    raw = json.loads(blob)
                    if role == "result":
                        if kind == "setup":
                            raise SchemaError("setup_result_schema_unexpected")
                        extracted = {"mixed": mixed, "phase": phase, "resource": resource_probe}[kind](ctx, raw)
                    elif role == "observer":
                        obs = observer(ctx, raw)
                    else:
                        failure = phase_failure(ctx, raw)
                except (ValueError, TypeError, KeyError) as error:
                    ctx.check(False, str(error) if isinstance(error, SchemaError) else "schema_parse_failure")
        app_id = entry.get("appId")
        if extracted and app_id:
            app_id = label(app_id)
            app = apps.get(app_id)
            ctx.check(app is not None, "app_identity_missing")
            if app:
                ctx.check(extracted["data"].get("ExecutableSha256") == app["executableSha256"], "executable_identity_mismatch")
                native = extracted["data"].get("NativeSha256", extracted["data"].get("LoadedNativeSha256"))
                if native is not None:
                    allowed_native = set(app.get("nativeImages", {}).values())
                    if app.get("route") == "dapper" and app.get("provider") == "sqlite":
                        allowed_native |= external_native
                    ctx.check(native in allowed_native, "native_image_identity_mismatch")
        request = ctx.take(entry.get("request", {}), {**fields("repetition timeoutSeconds expectedSeconds"),
            "provider": exact({"sqlite", "postgresql"}), "route": exact({"before", "baseline", "recovered", "candidate", "dapper"}),
            "mode": exact({"dynamic", "prepared"})})
        if extracted and kind == "mixed" and "expectedSeconds" in request:
            ctx.check(extracted["data"]["EffectiveSeconds"] >= request["expectedSeconds"] - 0.05, "requested_duration_not_reached")
        for item in entry.get("digestOnly", []):
            role = exact({"stdout", "failure-original", "postgres-owner", "runner-receipt"})(item["role"])
            if Path(item["path"]).is_file():
                originals[role] = source(item["path"])[0]
        safe = eid.replace("/", "--")
        frame_count, last_end = 0, None
        resource_path = entry.get("resources")
        if resource_path and Path(resource_path).is_file():
            originals["resources"] = source(resource_path)[0]
            name = safe + ".resources.numeric.jsonl"
            with Path(resource_path).open() as inp, (output / name).open("xb") as out:
                for line_no, line in enumerate(inp, 1):
                    frame_count += 1
                    try:
                        frame = resource_sample(ctx, json.loads(line))
                        ctx.check(last_end is None or frame["monotonicNs"] >= last_end, "resource_acquisition_overlap")
                        last_end = frame["acquiredThroughMonotonicNs"]
                        out.write(canonical({"line": line_no, "sample": frame}) + b"\n")
                    except (ValueError, TypeError, KeyError) as error:
                        code = str(error) if isinstance(error, SchemaError) else "resource_schema_parse_failure"
                        ctx.check(False, code)
                        out.write(canonical({"line": line_no, "extractionError": code, "rawLineSha256": digest(line.encode())}) + b"\n")
            ctx.check(source(resource_path)[0] == originals["resources"], "resource_input_changed_during_extraction")
            index["files"].append({"name": name, **source(output / name)[0]})
        state = "not_observed"
        if obs:
            if obs.get("timedOut") is True:
                state = "timed_out"
            elif obs.get("success") is False or obs.get("exitCode") not in (0, None):
                state = "process_failed"
            elif obs.get("success") is True and obs.get("exitCode") == 0:
                state = "completed_setup" if kind == "setup" else "completed_with_result" if extracted else "completed_without_valid_result"
            else:
                state = "observer_incomplete"
        elif extracted:
            state = "result_without_observer"
        ctx.check(state not in {"completed_without_valid_result", "result_without_observer"}, "result_observer_continuity")
        payload = {"schemaVersion": VERSION, "id": eid, "kind": kind, "appId": app_id, "state": state,
                   "originals": originals, "result": extracted, "observer": obs, "failure": failure, "resourceSampleCount": frame_count,
                   "request": request, "validation": ctx.validation(), "performanceAcceptance": False}
        name = safe + ".numeric.json"
        index["files"].append({"name": name, **write_json(output / name, payload)})
        index["entries"].append({"id": eid, "kind": kind, "state": state, "file": name,
                                 "numericAndSchemaChecksPassed": not ctx.issues, "issues": ctx.issues})
        if ctx.issues:
            index["validationIssues"].append({"section": eid, "issues": ctx.issues})
    for ref in manifest.get("digestOnly", []):
        index.setdefault("digestOnly", []).append({"id": label(ref["id"]), **source(ref["path"])[0]})
    index["numericAndSchemaChecksPassed"] = not index["validationIssues"]
    write_json(output / "index.json", index)
    return index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    index = extract_bundle(args.manifest, args.output)
    print(json.dumps({"entries": len(index["entries"]), "files": len(index["files"]),
                      "numericAndSchemaChecksPassed": index["numericAndSchemaChecksPassed"],
                      "validationIssues": index["validationIssues"], "performanceAcceptance": False}, separators=(",", ":")))
    return 0 if index["numericAndSchemaChecksPassed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
