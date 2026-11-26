#!/usr/bin/env python3
"""Validate completed schema-4 buffered runs before comparing every recorded sample.

Reads only the explicitly supplied completed directories and their frozen inputs.
It never starts a consumer, database, build, test, profiler, or network request.
Every supplied attempt is retained; any invalid attempt suppresses comparisons.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile


BEFORE = "805812872d9d8860bb3bf9e55db18772f3579d85"
CANDIDATE = "31693e3883f1192a34fcb9e9c49acdcca4ad321c"
PROGRAM = "7bba2e224acfe92cf6ad126907bfd332af3b7a8ae932560e9a0faf72d13c7992"
ROUTES = ("fluent", "prepared", "host-sql")
ROWS = (1, 100, 1000)
PHASES = ("ConstructTicks", "SubmitToListTicks", "ReleaseTicks")
OWNERS = ("Sources", "Sessions", "Operations", "Cursors", "Buffers", "Owners", "PullChannels")
COUNTERS = (*OWNERS, "SqlExecutions", "ProtocolSubmissions")
CONTRACTS = {
    "fixture_sql_parameters_expected_values": "9ed0228461b35deba4f5e90956438d750f2fe4c219f37e52ca2c1f150a784640",
    "dto_projection": "64aec49fa21dba53f8f81c0105ff2086802885c4d40c23a0e5b5e4d91783a522",
}
FILES = {}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, name, minimum=0):
    require(type(value) is int and value >= minimum, "Invalid integer: " + name)
    return value


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def invalid_constant(value):
    raise ValueError("Nonfinite JSON number: " + value)


def finite_float(value):
    result = float(value)
    require(math.isfinite(result), "Nonfinite JSON number: " + value)
    return result


def read_json(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=unique_object,
                      parse_constant=invalid_constant, parse_float=finite_float)


def identity(path, wanted=None):
    path = Path(path).resolve(strict=True)
    digest = sha(path)
    require(wanted is None or digest == wanted, "Changed input: " + str(path))
    require(FILES.setdefault(str(path), digest) == digest, "Input changed during this analysis: " + str(path))
    return {"path": str(path), "sha256": digest}


def frozen(item):
    require(isinstance(item, dict) and isinstance(item.get("path"), str)
            and re.fullmatch("[0-9a-f]{64}", item.get("sha256", "")), "Invalid frozen file identity")
    return identity(item["path"], item["sha256"])


def quantiles(ticks, frequency):
    values = sorted(ticks)
    require(values and all(type(value) is int and value >= 0 for value in values), "Invalid duration samples")
    scale = 1_000_000 / frequency
    return {"sampleCount": len(values), "totalTicks": sum(values),
            "meanMicroseconds": sum(values) / len(values) * scale,
            **{f"p{percent}Microseconds": values[math.ceil(len(values) * percent / 100) - 1] * scale
               for percent in (50, 95, 99)},
            "method": "nearest rank over every raw sample; no trimming, retry selection or subtraction"}


def consumer(item, expected_commit, provider, audit):
    audit.append(frozen(item["buildReceipt"]))
    build_path = Path(item["buildReceipt"]["path"])
    build = read_json(build_path)
    require(build.get("kind") == "buffered-query-phases" and build.get("provider") == provider,
            "Unexpected consumer kind/provider")
    require(type(build.get("exit_code")) is int and build["exit_code"] == 0
            and build.get("project_references") == 0 and build.get("abi_wrapper_instrumentation") is False
            and build.get("first_row_observable") is False and build.get("execution_performed") is False,
            "The consumer is not an ordinary successfully built buffered AOT input")
    require(build.get("ordinary_consumer_unchanged") is True and build.get("package_unchanged") is True,
            "Original build input preservation was not established")
    require(item["packageSourceCommit"] == build["package_source_commit"] == expected_commit
            and item["packageSha256"] == build["package_sha256"], "Package identity does not match its selected source")
    require(build["sources"] == {"Program.cs": PROGRAM}
            and build["business_contract_sha256"] == CONTRACTS, "Unreviewed buffered harness or business contract")
    program = frozen(item["program"])
    require(program["sha256"] == PROGRAM and Path(program["path"]) == build_path.parent / "Program.cs",
            "The actual consumer Program does not match the fixed buffered harness")
    audit.append(program)
    executable = frozen(item["executable"])
    require(executable["sha256"] == build["executable_sha256"], "Executable/build receipt mismatch")
    with Path(executable["path"]).open("rb") as stream:
        require(stream.read(4) == b"\x7fELF", "The consumer is not an ELF")
    require(not Path(executable["path"]).with_suffix(".dll").exists(), "A JIT output accompanies the claimed AOT executable")
    audit.append(executable)
    project = Path(build["command"][2])
    require(project.parent == build_path.parent and not ET.parse(project).getroot().findall(".//ProjectReference"),
            "The buffered project is not the actual external PackageReference project")
    require(build["command"][:2] == ["dotnet", "publish"]
            and "-p:PublishAot=true" in build["command"] and "-p:IlcTreatWarningsAsErrors=true" in build["command"]
            and build["command"][build["command"].index("-c") + 1] == "Release"
            and build["command"][build["command"].index("-r") + 1] == "linux-x64",
            "The recorded build is not Release Linux x64 Native AOT")
    audit.append(identity(project, build["project_sha256"]))
    audit.append(identity(build_path.parent / "project.assets.json", build["assets_sha256"]))
    assets = read_json(build_path.parent / "project.assets.json")
    require({name for name in assets["libraries"] if name.lower().startswith("korda.")}
            == {build["package"] + "/" + build["version"]}, "The resolved Korda package graph differs")
    generated_root = build_path.parent / "generated/Korda.Query.Generator/Korda.Query.Generator.ModelGenerator"
    generated = {path.name: identity(path) for path in sorted(generated_root.glob("*.g.cs"))}
    require(len(generated) == 2 and sum(name.startswith("PhaseRow.") and name.endswith(".Projection.g.cs") for name in generated) == 1
            and sum(name.startswith("PhaseOrder.") and name.endswith(".Mapping.g.cs") for name in generated) == 1,
            "The actual DTO projection/model generated source is missing or unexpected")
    audit.extend(generated.values())
    ordinary = Path(build["source_consumer"])
    audit.append(identity(ordinary / "build-receipt.json", build["source_receipt_sha256"]))
    audit.append(identity(build_path.parent / "source-build-receipt.json", build["source_receipt_sha256"]))
    prior = read_json(ordinary / "build-receipt.json")
    require(prior["package_sha256"] == build["package_sha256"]
            and prior["executable_sha256"] == build["source_executable_sha256"], "Ordinary source receipt mismatch")
    audit.append(identity(ordinary / "out/DbPerf.QueryPhases", build["source_executable_sha256"]))
    for name, digest in build["source_inputs"].items():
        audit.append(identity(ordinary / name, digest))
        if name != "Program.cs":
            audit.append(identity(build_path.parent / name, digest))
    package_id, version = build["package"].lower(), build["version"].lower()
    package = ordinary / "packages" / package_id / version / f"{package_id}.{version}.nupkg"
    audit.append(identity(package, build["package_sha256"]))
    with zipfile.ZipFile(package) as archive:
        spec = ET.fromstring(archive.read(next(name for name in archive.namelist() if name.endswith(".nuspec"))))
        require(spec.find(".//{*}repository").attrib["commit"] == expected_commit
                and spec.find(".//{*}id").text == build["package"]
                and spec.find(".//{*}version").text == build["version"], "Actual nupkg metadata mismatch")
        require(json.loads(archive.read("korda/public.json")) == build["package_inputs"], "Actual package inputs mismatch")
    expected_name = "libnw_database_" + provider + ".so"
    require(set(item["native"]) == set(build["native_images"]) == {expected_name}, "Unexpected native provider inventory")
    native = frozen(item["native"][expected_name])
    require(native["sha256"] == build["native_images"][expected_name]
            and Path(native["path"]).parent == Path(executable["path"]).parent, "Native image identity/path mismatch")
    audit.append(native)
    audit.append(identity(ordinary / "out" / expected_name, native["sha256"]))
    return {"build": build, "executable": executable, "native": native,
            "generated": {name: value["sha256"] for name, value in generated.items()}}


def check_sample(sample, rows):
    require(set(sample) == {*PHASES, "Rows"} and integer(sample["Rows"], "sample.Rows", 1) == rows,
            "Incomplete or mislabeled sample")
    for phase in PHASES:
        integer(sample[phase], phase)
    require(sample["SubmitToListTicks"] > 0, "A completed database terminal needs a positive observed duration")


def counts(value):
    require(set(value) == set(COUNTERS), "Unknown or missing native counter")
    for key in COUNTERS:
        integer(value[key], "native." + key)


def summarize_receipt(raw, rows, windows, iterations, bound, command, provider):
    require(raw.get("SchemaVersion") == 4 and raw.get("NativeAot") is True
            and raw.get("Buffered") is True and raw.get("FirstRowObservable") is False
            and raw.get("AbiWrapperInstrumentation") is False, "A real uninstrumented buffered schema-4 receipt is required")
    require(raw["Provider"] == ("Sqlite" if provider == "sqlite" else "PostgreSql")
            and raw["ResultRows"] == rows and raw["WarmupPerRoute"] == 64, "Provider, result shape or warmup mismatch")
    require(raw["ExecutableSha256"] == bound["executable"]["sha256"]
            and raw["NativeSha256"] == bound["native"]["sha256"]
            and Path(raw["NativePath"]).resolve() == Path(bound["native"]["path"]), "Loaded image differs from frozen input")
    require(isinstance(raw["DatabaseVersion"], str) and raw["DatabaseVersion"]
            and isinstance(raw["Sql"], str) and raw["Sql"] and isinstance(raw["RawTemplate"], str) and raw["RawTemplate"],
            "SQL/database identity is missing")
    expected_results = (f"Int64 tenant alternates 1 and 2; direct returned IReadOnlyList<PhaseRow> with {rows} rows, "
                        "exact Id/Note/null checks; the one-row case binds the complete composite primary key")
    require(raw["ParametersAndResults"] == expected_results, "Unexpected parameter/result contract")
    frequency = integer(raw["StopwatchFrequency"], "StopwatchFrequency", 1)
    integer(raw["PreparationTicks"], "PreparationTicks")
    integer(raw["TeardownTicks"], "TeardownTicks")
    require(len(raw["FirstExecutions"]) == 3, "Incomplete first complete-operation observations")
    for sample in raw["FirstExecutions"]:
        check_sample(sample, rows)
    counts(raw["Drained"])
    require(all(raw["Drained"][owner] == 0 for owner in OWNERS), "Native owners did not drain")
    expected_order = [(ROUTES[(index + position) % 3], index)
                      for index in range(windows) for position in range(3)]
    require([(window["Route"], window["Index"]) for window in raw["Windows"]] == expected_order,
            "The complete rotating route/window matrix is missing or reordered")
    last_finished, last_native = 0, None
    for window in raw["Windows"]:
        require(window["Operations"] == iterations and len(window["Samples"]) == iterations, "Incomplete operation window")
        start = integer(window["StartedTicks"], "StartedTicks", 1)
        end = integer(window["FinishedTicks"], "FinishedTicks", 1)
        require(last_finished <= start < end, "Window timestamps overlap or run backwards")
        last_finished = end
        # Both clocks are CLOCK_MONOTONIC on the fixed Linux x64 consumer/runner.
        require(command["startedMonotonicNs"] <= start * 1_000_000_000 // frequency
                and end * 1_000_000_000 // frequency <= command["finishedMonotonicNs"], "Window lies outside its recorded process lifetime")
        for sample in window["Samples"]:
            check_sample(sample, rows)
        require(sum(sum(sample[phase] for phase in PHASES) for sample in window["Samples"]) <= end - start,
                "The sequential phase samples exceed their containing full window")
        for before, after in (("AllocatedBefore", "AllocatedAfter"), ("CpuBeforeTicks", "CpuAfterTicks")):
            require(integer(window[after], after) >= integer(window[before], before), "A cumulative process counter moved backwards")
        for key in ("Gen0", "Gen1", "Gen2", "ResidentBytes", "PeakResidentBytes"):
            integer(window[key], key)
        require(window["PeakResidentBytes"] >= window["ResidentBytes"], "RSS exceeds its process peak")
        before, after = window["NativeBefore"], window["NativeAfter"]
        counts(before)
        counts(after)
        require(all(before[owner] == after[owner] for owner in OWNERS), "Native ownership grew inside a completed window")
        require(before["Sources"] == before["Sessions"] == 1
                and all(before[name] == 0 for name in ("Operations", "Cursors", "Buffers", "PullChannels")),
                "The query window did not begin and end with a single idle persistent session")
        require(after["SqlExecutions"] - before["SqlExecutions"] == iterations, "SQL executions differ from one statement per operation")
        require(after["ProtocolSubmissions"] >= before["ProtocolSubmissions"], "Protocol counter moved backwards")
        if last_native is not None:
            require(all(before[key] >= last_native[key] for key in ("SqlExecutions", "ProtocolSubmissions")),
                    "Native cumulative counters moved backwards between windows")
        last_native = after
    require(all(raw["Drained"][key] >= last_native[key] for key in ("SqlExecutions", "ProtocolSubmissions")),
            "Final native counters precede the measured windows")
    summaries = {}
    for route in ROUTES:
        selected = [window for window in raw["Windows"] if window["Route"] == route]
        samples = [sample for window in selected for sample in window["Samples"]]
        operations = windows * iterations
        elapsed = sum(window["FinishedTicks"] - window["StartedTicks"] for window in selected)
        allocated = sum(window["AllocatedAfter"] - window["AllocatedBefore"] for window in selected)
        cpu_ticks = sum(window["CpuAfterTicks"] - window["CpuBeforeTicks"] for window in selected)
        summaries[route] = {
            "windows": windows, "operations": operations, "returnedRows": operations * rows,
            "phases": {phase: quantiles([sample[phase] for sample in samples], frequency) for phase in PHASES},
            "threePhaseTotal": quantiles([sum(sample[phase] for phase in PHASES) for sample in samples], frequency),
            "wholeProcessCpuTicks": cpu_ticks, "wholeProcessCpuSeconds": cpu_ticks / 10_000_000,
            "wholeProcessCpuMicrosecondsPerOperation": cpu_ticks / 10 / operations,
            "wholeProcessAllocatedBytes": allocated, "wholeProcessBytesPerOperation": allocated / operations,
            "wholeProcessGc": {key: sum(window[key] for window in selected) for key in ("Gen0", "Gen1", "Gen2")},
            "windowTicksIncludingVerification": elapsed, "windowSecondsIncludingVerification": elapsed / frequency,
            "operationsPerSecondIncludingVerification": operations * frequency / elapsed,
            "maxObservedWindowRssBytes": max(window["ResidentBytes"] for window in selected),
            "processLifetimePeakRssBytes": max(window["PeakResidentBytes"] for window in selected),
            "sqlExecutions": sum(window["NativeAfter"]["SqlExecutions"] - window["NativeBefore"]["SqlExecutions"] for window in selected),
            "protocolSubmissions": sum(window["NativeAfter"]["ProtocolSubmissions"] - window["NativeBefore"]["ProtocolSubmissions"] for window in selected),
        }
    return summaries


def analyze(directory, attempt, series, host):
    directory = directory.resolve(strict=True)
    audit = attempt["files"]
    plan_path, runner_path = directory / "plan.json", directory / "runner.json"
    plan, runner = read_json(plan_path), read_json(runner_path)
    audit.extend((identity(plan_path, runner["planSha256"]), identity(runner_path)))
    require(plan.get("lane") == "buffered" and plan.get("schemaVersion") == 1
            and plan.get("firstRowObservable") is False and plan.get("longRunAcceptance") is False,
            "Unexpected plan lane/acceptance contract")
    provider = plan["provider"]
    require(provider in ("sqlite", "postgresql"), "Unknown provider")
    attempt["provider"] = provider
    audit.append(frozen(plan["inputs"]["generator"]))
    audit.append(frozen(plan["inputs"]["runner"]))
    require(runner["runnerSha256"] == plan["inputs"]["runner"]["sha256"]
            and runner.get("hostQualifiedForLongRuns") is False and runner["cpuAffinity"] == [8], "Runner identity/affinity mismatch")
    require(host["uname"]["system"] == "Linux" and host["uname"]["machine"] == "x86_64"
            and host["observerSource"]["sha256"] == runner["runnerSha256"], "Host/runner record does not match Linux x64")
    outer = [item for item in series if item["command"][-2:] == ["--output", str(directory)]]
    require(len(outer) == 1, "Missing or ambiguous actual outer runner completion")
    outer = outer[0]
    require(outer["name"] == directory.name and type(outer["exitCode"]) is int and outer["exitCode"] == 0
            and outer["command"] == plan["runnerCommand"] and outer["planSha256"] == runner["planSha256"],
            "The outer runner command, exit or plan identity differs")
    audit.append(identity(outer["command"][-3], runner["planSha256"]))
    audit.append(identity(outer["log"], outer["logSha256"]))
    attempt["outerRunner"] = outer
    require(plan["phaseDataset"] == {"tenants": 2, "rowsPerTenant": 1000, "batchRows": 32}
            and plan["affinity"] == {"client": "0-3", "postgres": "4-7", "observer": "8"}, "Unmatched dataset or affinities")
    bound = {name: consumer(plan["inputs"]["consumers"][name], commit, provider, audit)
             for name, commit in (("before", BEFORE), ("candidate", CANDIDATE))}
    for field in ("sources", "project_sha256", "business_contract_sha256", "tools", "native_images"):
        require(bound["before"]["build"][field] == bound["candidate"]["build"][field], "Before/candidate inputs differ: " + field)
    require(bound["before"]["generated"] == bound["candidate"]["generated"], "Actual generated DTO/model code differs")
    expected = [("fixture-buffered", "candidate", 1, True)]
    expected += [(cohort + "-rows" + str(rows), cohort, rows, False) for rows in ROWS
                 for cohort in (("candidate", "before") if rows == 100 else ("before", "candidate"))]
    require([item["name"] for item in plan["commands"]] == [item[0] for item in expected], "Missing, extra or reordered plan command")
    require({path.name for path in directory.glob("*.command.json")} == {name + ".command.json" for name, *_ in expected},
            "Incomplete or additional command attempts exist in this run")
    failures = [identity(path) for path in sorted(directory.glob("*.failure.json"))]
    attempt["failureSidecars"] = failures
    require(not failures, "A failure sidecar exists; no successful retry can replace this attempt")
    command_receipts = {}
    for name, *_ in expected:
        path = directory / (name + ".command.json")
        audit.append(identity(path))
        value = read_json(path)
        command_receipts[name] = value
        attempt["commandOutcomes"].append({"name": name, "exitCode": value.get("exitCode"),
                                            "success": value.get("success"), "timedOut": value.get("timedOut"),
                                            "observerErrors": value.get("observerErrors")})
    require(all(value.get("success") is True and type(value.get("exitCode")) is int and value["exitCode"] == 0
                and value.get("timedOut") is False and value.get("observerErrors") == []
                for value in command_receipts.values()), "One or more commands failed, timed out or lost observer evidence")
    if provider == "sqlite":
        require(Path(plan["connection"]).resolve() == directory / "fixture.sqlite", "The SQLite fixture is not private to this run")
        connection = plan["connection"]
    else:
        for item in plan["inputs"]["postgresTools"].values():
            audit.append(frozen(item))
        owner_path = directory / "postgres-owner.json"
        audit.append(identity(owner_path))
        owner = read_json(owner_path)
        require(owner.get("exitCode") == 0 and not any(key in owner for key in ("error", "shutdownError", "finalSampleError", "cpuGroupError")),
                "The PostgreSQL owner did not retire cleanly")
        require(Path(plan["postgres"]["data"]).resolve() == directory / "pgdata" and "queryPlans" not in plan["postgres"],
                "The PostgreSQL fixture is not private or has additional server instrumentation")
        argv = owner["argv"]
        require(argv[:4] == ["taskset", "-c", "4-7", str(Path(plan["postgres"]["bin"]) / "postgres")]
                and argv.count("-p") == 1 and argv.count("-D") == 1
                and Path(argv[argv.index("-D") + 1]).resolve() == directory / "pgdata", "Unexpected PostgreSQL launch")
        port = int(argv[argv.index("-p") + 1])
        require(1 <= port <= 65535, "Invalid PostgreSQL port")
        connection = f"postgresql://korda@127.0.0.1:{port}/db_perf_01"
        audit.append(identity(directory / "postgres-settings.txt"))
    measured, last_finished = {}, 0
    for item, (name, cohort, rows, fixture) in zip(plan["commands"], expected):
        phase, iterations, windows = ("fixture", 1, 1) if fixture else ("buffered", 256, 3)
        require(item["cohort"] == cohort and item["phase"] == phase and item["rows"] == rows
                and item["timingRequested"] is (not fixture) and item["longRunAcceptance"] is False
                and item["instrumented"] is False and item["cpus"] == "0-3" and item["timeoutSeconds"] == 600,
                "A planned command changed its measurement contract")
        raw_path = directory / (name + ".json")
        expected_argv = [bound[cohort]["executable"]["path"], "{connection}", "{output}/" + name + ".json",
                         str(iterations), str(windows), *(["initialize"] if fixture else []), "--rows", str(rows)]
        require(item["argv"] == expected_argv, "A planned command differs from the bound public buffered invocation")
        actual = ["taskset", "-c", "0-3", *[value.replace("{connection}", connection).replace("{output}", str(directory)) for value in expected_argv]]
        receipt = command_receipts[name]
        require(receipt["name"] == name and receipt["phase"] == phase and receipt["argv"] == actual
                and receipt["timeoutSeconds"] == 600 and receipt["longRunAcceptance"] is False, "Actual command differs from its frozen plan")
        began = integer(receipt["startedMonotonicNs"], "command start", 1)
        ended = integer(receipt["finishedMonotonicNs"], "command end", 1)
        require(last_finished <= began < ended, "Paired commands overlap or run out of order")
        last_finished = ended
        names = {name + suffix for suffix in (".stdout.log", ".resources.jsonl")}
        require(set(receipt["files"]) == names and receipt["resourceSamples"] == name + ".resources.jsonl", "Missing observer file hashes")
        for filename, digest in receipt["files"].items():
            audit.append(identity(directory / filename, digest))
        stdout = (directory / (name + ".stdout.log")).read_text().splitlines()
        sentinel = "DB_PERF_BUFFERED_QUERY_PHASES "
        require([line for line in stdout if line.startswith(sentinel)] == [sentinel + str(raw_path)],
                "The hashed stdout does not name exactly this completed buffered receipt")
        audit.append(identity(raw_path))
        raw = read_json(raw_path)
        stats = summarize_receipt(raw, rows, windows, iterations, bound[cohort], receipt, provider)
        if not fixture:
            measured[(cohort, rows)] = {"raw": raw, "stats": stats, "receipt": identity(raw_path)}
    if provider == "postgresql":
        require(integer(owner["finishedMonotonicNs"], "PostgreSQL end", 1) >= last_finished,
                "PostgreSQL retired before the final client command")
    comparisons = []
    for rows in ROWS:
        before, candidate = measured[("before", rows)], measured[("candidate", rows)]
        for field in ("Sql", "RawTemplate", "ParametersAndResults", "ResultRows", "DatabaseVersion", "StopwatchFrequency"):
            require(before["raw"][field] == candidate["raw"][field], "Measured before/candidate contract differs: " + field)
        for route in ROUTES:
            comparisons.append({"attempt": str(directory), "provider": provider, "rows": rows, "route": route,
                                "beforeSource": BEFORE, "candidateSource": CANDIDATE,
                                "beforeReceipt": before["receipt"], "candidateReceipt": candidate["receipt"],
                                "sql": before["raw"]["Sql"], "rawTemplate": before["raw"]["RawTemplate"],
                                "before": before["stats"][route], "candidate": candidate["stats"][route]})
    attempt["packageSources"] = {"before": BEFORE, "candidate": CANDIDATE}
    attempt["runnerCompletionProof"] = "The external series records the exact outer runner command and exit 0; every planned command and PostgreSQL owner also completed successfully."
    return comparisons


def markdown(result):
    lines = ["# Buffered public-terminal A/B", "", "Validation: **" + ("passed" if result["passed"] else "failed") + "**.", "",
             "All explicitly supplied attempts are listed. No first-row latency is observable. Submit-to-list includes complete result creation and cursor retirement; release covers later explicit query disposal.", "",
             "CPU, allocation and GC are whole-process window observations, including result validation and business/harness allocations. No business subtraction, framework-only allocation claim, retry selection or long-run acceptance is made.", ""]
    for attempt in result["attempts"]:
        lines += [f"- `{attempt['directory']}`: {'passed' if attempt['passed'] else 'failed'}"
                  + (": " + attempt["error"] if not attempt["passed"] else "")]
    if not result["passed"]:
        return "\n".join(lines + ["", "Comparisons are suppressed because at least one input failed validation.", ""])
    for provider in ("sqlite", "postgresql"):
        selected = [entry for entry in result["comparisons"] if entry["provider"] == provider]
        if not selected:
            continue
        lines += ["", "## " + provider, "", "All entries are before → candidate; time is microseconds.", "",
                  "| Rows | Route | List p50/p95/p99 before | List p50/p95/p99 candidate | CPU/op | B/op | GC 0/1/2 |",
                  "| ---: | --- | ---: | ---: | ---: | ---: | --- |"]
        for entry in selected:
            before, after = entry["before"], entry["candidate"]
            def timing(value):
                return "/".join(f"{value['phases']['SubmitToListTicks'][f'p{percent}Microseconds']:.3f}" for percent in (50, 95, 99))
            def gc(value):
                return "/".join(str(value["wholeProcessGc"][key]) for key in ("Gen0", "Gen1", "Gen2"))
            lines.append(f"| {entry['rows']} | {entry['route']} | {timing(before)} | {timing(after)} | "
                         f"{before['wholeProcessCpuMicrosecondsPerOperation']:.3f} → {after['wholeProcessCpuMicrosecondsPerOperation']:.3f} | "
                         f"{before['wholeProcessBytesPerOperation']:.3f} → {after['wholeProcessBytesPerOperation']:.3f} | {gc(before)} → {gc(after)} |")
    return "\n".join(lines + ["", "The JSON retains every phase p50/p95/p99, untrimmed three-phase totals, raw summed CPU/allocation/GC counters, throughput including validation, RSS, SQL/protocol counts and all verified file identities.", ""])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", nargs="+", type=Path, help="every completed attempt to include; no automatic retry selection")
    parser.add_argument("--series", required=True, type=Path, help="actual serial outer-runner completion records")
    parser.add_argument("--host-record", required=True, type=Path, help="the pre-series host/affinity observation")
    parser.add_argument("--output", required=True, type=Path, help="new JSON output; a same-name .md is also written")
    args = parser.parse_args()
    output = args.output.resolve()
    text_output = output.with_suffix(".md")
    require(output.suffix == ".json" and not output.exists() and not text_output.exists(), "Use fresh .json/.md summary paths")
    directories = [path.resolve() for path in args.directories]
    require(len(directories) == len(set(directories)) and all(not output.is_relative_to(path) for path in directories),
            "Do not repeat an attempt or write summaries into raw evidence directories")
    series_identity, host_identity = identity(args.series), identity(args.host_record)
    series, host = read_json(args.series), read_json(args.host_record)
    last_end = None
    for item in series:
        start, end = datetime.fromisoformat(item["startedUtc"]), datetime.fromisoformat(item["finishedUtc"])
        require(start < end and (last_end is None or last_end <= start), "The recorded outer series overlaps or runs backwards")
        last_end = end
    require({Path(item["command"][-1]).resolve() for item in series if item["name"].startswith("buffered-")}
            == set(directories), "Every buffered attempt in the supplied outer series must be included; do not select a good retry")
    result = {"schemaVersion": 1, "analyzer": identity(__file__), "passed": True,
              "scope": "Strict paired buffered observations over every supplied attempt; no environment, release, final campaign or framework-zero acceptance",
              "firstRowObservable": False, "frameworkOnlyAllocationProven": False, "longRunAcceptance": False,
              "attemptInventoryScope": "Every buffered attempt listed in the supplied serial outer-runner record is required; there is no best-run selection. Other unprovided series cannot be certified absent.",
              "outerSeries": series_identity, "hostRecord": host_identity, "hostScope": host["scope"],
              "rawReceiptHashScope": "Hashed command stdout names the completed result path. Schema 4 does not embed result bytes/hash in stdout; the result payload is content-hashed at analysis and rechecked before writing this summary.",
              "resultValueProof": "The fixed Program checks every ordered Id/Note/null in the returned IReadOnlyList; normal command completion proves these assertions ran. Raw samples store counts, not copies of DTO values.",
              "processCounterScope": "CPU uses .NET TimeSpan ticks at 100 ns, allocation and GC use whole-process windows. Phase ticks use the receipt StopwatchFrequency. No wait4 process-lifetime CPU is relabeled as a steady window.",
              "attempts": [], "comparisons": []}
    comparisons = []
    for directory in directories:
        attempt = {"directory": str(directory), "passed": False, "files": [], "commandOutcomes": []}
        result["attempts"].append(attempt)
        try:
            comparisons.extend(analyze(directory, attempt, series, host))
            attempt["passed"] = True
        except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, ET.ParseError, zipfile.BadZipFile) as error:
            attempt["error"] = type(error).__name__ + ": " + str(error)
            result["passed"] = False
    changed = []
    for path, digest in FILES.items():
        try:
            if sha(path) != digest:
                changed.append(path)
        except OSError:
            changed.append(path)
    result["inputMutationCheck"] = {"unchanged": not changed, "changedOrMissingFiles": changed}
    if changed:
        result["passed"] = False
    if result["passed"]:
        result["comparisons"] = comparisons
    else:
        result["comparisonSuppressionReason"] = "At least one supplied attempt failed; no favorable retry or partial comparison is selected."
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    with text_output.open("x") as stream:
        stream.write(markdown(result))
    print(json.dumps({"passed": result["passed"], "attempts": len(result["attempts"]),
                      "comparisons": len(result["comparisons"]), "output": str(output), "sha256": sha(output)}))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
