#!/usr/bin/env python3
"""One fresh, identity-bound mixed35 observation; never automatic final credit.

Prepare with the unchanged local helper, execute the independently reviewed
proc observer adapter, then validate business/timing/resource evidence. Import
is read-only and starts no process. --prepare-only never executes a workload.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import re
import signal
import subprocess
import sys
import traceback
import time
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / "experiments/recovery"
REPO = ROOT / "worktrees/Korda/benchmarks/db-perf"
HELPER = LOCAL / "run_mixed_cell.py"
ADAPTER = LOCAL / "run_proc_tree_observer.py"
MANIFEST = REPO / "workload/queries-v3.json"
MANIFEST_SHA = "76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2"
ADAPTER_SHA = "d7db0a60fd171e6124aecec078ee1bdd3331a9b534df340b2155f509ede4d8ff"
OBSERVER_SHA = "296e6b802d8bc1bcf964d7faa71d4adaa37226a867c17a9a3b5f00284f769b86"
SQLITE = ROOT / "builds/baseline-matched-sqlite/sqlite-image/shared/libsqlite3.so"
POSTGRES = ROOT / "toolchain/postgres-18.0/install/bin"
SHIM = ROOT / "restored-stage1/diagnostics/allocation-shim/libdb-perf-alloc.so"
BLOCKER = LOCAL / "verified-mixed-cell.blocked.json"
VARIANTS = {"before": ("baseline-final", "korda"), "candidate": ("integrated05", "korda"),
            "dapper": ("baseline-final", "dapper")}
KINDS = ("zero-cost", "pressure", "before-long", "final-long", "allocation")
LONG = ("before-long", "final-long")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def canonical_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def atomic(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def contained(path):
    path = Path(path).resolve()
    require(path.is_relative_to(ROOT), "An identity path escaped the task workspace: " + str(path))
    return path


def runtime_identity():
    allowed = {"DOTNET_ROOT", "DOTNET_ROOT_X64", "DOTNET_CLI_HOME", "DOTNET_NOLOGO",
               "DOTNET_SKIP_FIRST_TIME_EXPERIENCE", "DOTNET_CLI_TELEMETRY_OPTOUT", "DOTNET_MULTILEVEL_LOOKUP",
               "DOTNET_ROLL_FORWARD", "DOTNET_HOST_PATH", "DOTNET_BUNDLE_EXTRACT_BASE_DIR"}
    unexpected = sorted(key for key, value in os.environ.items() if value and (
        key.startswith("COMPlus_") or key.startswith("DB_PERF_")
        or key.startswith("DOTNET_") and key not in allowed or key in ("LD_PRELOAD", "LD_AUDIT")))
    require(not unexpected, "Default runtime/instrumentation policy rejected environment names: " + ", ".join(unexpected))
    # Only known nonsecret runtime/search-path settings are serialized.
    return {key: os.environ.get(key) for key in sorted(allowed | {"LD_LIBRARY_PATH", "LD_PRELOAD", "LD_AUDIT"})}


def host_identity():
    model = {}
    for line in Path("/proc/cpuinfo").read_text().splitlines():
        key, _, value = line.partition(":")
        if key.strip() in ("vendor_id", "model name", "flags") and key.strip() not in model:
            model[key.strip()] = value.strip()
    boot = Path("/proc/sys/kernel/random/boot_id")
    return {"system": platform.system(), "machine": platform.machine(), "kernel": platform.release(),
            "bootId": boot.read_text().strip() if boot.exists() else None, "cpu": model}


def app_path(provider, variant):
    family, route = VARIANTS[variant]
    return ROOT / f"consumers/{family}-{provider}/{route}-workload"


def input_snapshot(provider, variant, allocation=False):
    """Rehash actual bytes on every call; no cross-boundary hash cache."""
    app = app_path(provider, variant)
    family, route = VARIANTS[variant]
    files = {}

    def add(path, expected=None):
        path = contained(path)
        require(path.is_file(), "Frozen input is missing: " + str(path))
        if str(path) not in files:
            files[str(path)] = {"sha256": sha(path), "bytes": path.stat().st_size}
        value = files[str(path)]["sha256"]
        require(expected is None or value == expected, "Input differs from its receipt: " + str(path))
        return value

    prep, build, binding = (read(app / name) for name in ("preparation.json", "build-receipt.json", "binding-verification.json"))
    add(app / "preparation.json", build["preparationSha256"])
    add(app / "preparation.json", binding["preparationSha256"])
    add(app / "build-receipt.json", binding["buildReceiptSha256"])
    add(app / "binding-verification.json")
    require(build["buildCompleted"] is True and build["exitCode"] == 0 and binding["passed"] is True,
            "Actual external consumer build/binding validation is incomplete")
    require(build["provider"] == provider and build["route"] == route, "Wrong consumer route/provider")
    require(prep["onlyChangedCsFile"] == "Measurement.cs" and not prep["forcedGcAdded"]
            and not prep["perRowHooksAdded"] and not prep["sqlScheduleWarmupChanged"], "Unexpected final-harness preparation")
    sources = {path.name: add(path) for path in sorted(app.glob("*.cs"))}
    require(sources == prep["sources"] == build["sources"], "Actual root C# differs from source receipts")
    projects = list(app.glob("*.csproj"))
    require(len(projects) == 1, "Expected exactly one external consumer project")
    project = projects[0]
    require(not ET.parse(project).getroot().findall(".//ProjectReference"), "A final consumer must use actual PackageReference")
    add(project, build["projectSha256"])
    add(project, prep["projectSha256"])
    add(app / "global.json", prep["globalJsonSha256"])
    add(app / "workload-manifest.json", MANIFEST_SHA)
    require(build["workloadManifestSha256"] == prep["workloadManifestSha256"] == MANIFEST_SHA, "Wrong workload manifest receipt")
    add(app / "gc-observation.patch", prep["sourcePatchSha256"])
    add(app / "NuGet.Config", build["nugetConfigSha256"])
    add(app / "project.assets.json", build["assetsSha256"])
    for optional in ("Directory.Build.props", "sql-contract.json", "generated-sql-contract.json", "source-generated-sql-contract.json"):
        if (app / optional).exists():
            add(app / optional)
    generated = {str(path.relative_to(app / "generated")): add(path) for path in sorted((app / "generated").rglob("*.cs"))}
    require(generated == build["generatedSources"] and generated, "Actual generated code differs from the built AOT consumer")
    process_reading = list((app / "generated").rglob("PerfJson.ProcessReading.g.cs"))
    require(len(process_reading) == 1 and "TotalGcPauseTicks" in process_reading[0].read_text()
            and build["serializesTotalGcPauseTicks"] is True, "Actual generated JSON lacks process GC pause")
    add(process_reading[0], build["generatedProcessReadingSha256"])
    exe = app / "out" / ("DbPerf." + route.capitalize())
    add(exe, build["executableSha256"])
    debug = Path(str(exe) + ".dbg")
    add(debug, build["debugSha256"])
    with exe.open("rb") as stream:
        require(stream.read(4) == b"\x7fELF", "Expected the actual Native AOT ELF")
    require(not Path(str(exe) + ".dll").exists(), "Managed DLL cannot replace the AOT executable")
    build_ids = [re.findall(r"Build ID: (\w+)", subprocess.check_output(["readelf", "-n", str(path)], text=True))
                 for path in (exe, debug)]
    require(len(build_ids[0]) == 1 and build_ids[0] == build_ids[1], "ELF and .dbg build IDs differ")
    native = {str(path.relative_to(app / "out")): add(path) for path in sorted((app / "out").rglob("*.so"))}
    require(native == build["nativeImages"], "Actual native output differs from the built package")
    assets = read(app / "project.assets.json")
    libraries = {name: value for name, value in assets["libraries"].items() if value.get("type") == "package"}
    require(set(libraries) == set(build["packages"]), "Resolved package graph differs from the build receipt")
    for name, package in build["packages"].items():
        require(package["resolvedContentHash"] == libraries[name].get("sha512"), "Resolved package content hash changed: " + name)
        require(package.get("rawArchivePath") and package.get("rawArchiveSha256"), "Actual upstream nupkg evidence is missing: " + name)
        add(package["rawArchivePath"], package["rawArchiveSha256"])
    if route == "korda":
        add(build["package"], build["packageSha256"])
        packages = [name for name in libraries if name.startswith("Korda.Database.")]
        require(len(packages) == 1 and binding["resolvedPackageRawBytesMatchFeed"] is True, "Korda provider package binding is ambiguous")
        resolved = build["packages"][packages[0]]
        require(resolved["rawArchiveSha256"] == build["packageSha256"], "Korda feed/cache bytes differ")
        require(sorted(build["packedNativeImages"].values()) == sorted(native.values()), "Package/ELF native payload differs")
        require(len(native) == 1, "Expected one Korda provider image")
        native_name = next(iter(native))
        expected_native = {"path": str((app / "out" / native_name).resolve()), "sha256": native[native_name]}
        package_version = packages[0].split("/", 1)[1]
        expected_provider = "Sqlite" if provider == "sqlite" else "PostgreSql"
        expected_route = "korda-public-fluent"
    else:
        require(binding["actualGeneratedFactoriesVerified"] is True, "Dapper generated factories were not validated")
        add(app / "generated-sql-contract.json", binding["generatedContractSha256"])
        require(all(binding["upstreamRawArchivesMatchOriginal"].values()), "Dapper upstream package bytes changed")
        driver = "Microsoft.Data.Sqlite.Core" if provider == "sqlite" else "Npgsql"
        package_version = ";".join(next(name for name in libraries if name.startswith(prefix + "/"))
                                   for prefix in ("Dapper.AOT", "Dapper", driver))
        expected_provider, expected_route = driver, "independent-csharp-micro-orm-dapper-aot"
        expected_native = {"path": str(SQLITE.resolve()), "sha256": add(SQLITE)} if provider == "sqlite" else None
    infrastructure = [Path(__file__), HELPER, ADAPTER, LOCAL / "prepare_final_consumers.py", LOCAL / "verify_final_consumer.py",
                      LOCAL / "freeze_verified_mixed_inputs.py", REPO / "run.py", REPO / "campaign.py",
                      REPO / "campaign_build.py", REPO / "plan_diagnostics.py", REPO / "workload/check_dapper_contract.py", MANIFEST]
    for path in infrastructure:
        add(path)
    add(ADAPTER, ADAPTER_SHA)
    add(REPO / "run.py", OBSERVER_SHA)
    add(MANIFEST, MANIFEST_SHA)
    initialize_app = ROOT / f"restored-stage1/consumers/baseline-{provider}/korda-workload"
    initialize = initialize_app / "out/DbPerf.Korda"
    add(initialize)
    add(initialize_app / "build-receipt.json")
    for path in sorted((initialize_app / "out").glob("*.so")):
        add(path)
    if provider == "postgresql":
        for name in ("postgres", "psql", "initdb", "pg_isready"):
            add(POSTGRES / name)
    if allocation:
        add(SHIM)
    identity = {"schemaVersion": 1, "task": "DB-Exec-Parity-01", "provider": provider, "variant": variant,
                "family": family, "route": route, "app": str(app.resolve()), "files": files,
                "runtime": runtime_identity(), "host": host_identity(), "sources": sources,
                "expectedResultIdentity": {"provider": expected_provider, "route": expected_route,
                    "packageVersion": package_version, "executable": str(exe.resolve()),
                    "executableSha256": build["executableSha256"], "native": expected_native},
                "elfDebugBuildId": build_ids[0][0], "allocationDiagnostic": allocation}
    require(identity["host"]["system"] == "Linux" and identity["host"]["machine"] == "x86_64", "Linux x64 required")
    return {"capturedUtc": utc(), "identitySha256": canonical_sha(identity), "identity": identity}


def conditions(provider, seconds, rate, queue=64, idle=5, concurrency=None):
    return {"provider": provider, "seconds": seconds, "rate": rate, "queue": queue, "idle": idle,
            "concurrency": concurrency or (4 if provider == "sqlite" else 8), "warmup": 64,
            "rows": 32, "batchRows": 32, "tenants": 8, "ordersPerTenant": 1024,
            "mode": "prepared", "session": "persistent"}


def validate_request(args):
    require(args.provider in ("sqlite", "postgresql") and args.variant in VARIANTS and args.kind in KINDS, "Unknown cell identity")
    require(type(args.seconds) is int and 1 <= args.seconds <= 3600, "Duration must be finite and bounded")
    require(math.isfinite(args.rate) and 0 < args.rate <= 1_000_000, "Finite positive rate required")
    require(1 <= args.queue <= 65536 and 1 <= args.idle <= 300, "Queue/idle outside supported bounds")
    require(args.concurrency is None or 1 <= args.concurrency <= 256, "Concurrency outside supported bounds")
    if args.kind in LONG:
        require(args.seconds == 1800 and args.freeze is not None, "Long cells require exactly 1800 seconds and an explicit freeze manifest")
        require(args.variant == "before" if args.kind == "before-long" else args.variant in ("candidate", "dapper"),
                "Long cell kind and variant differ")


def validate_freeze(path, snapshot, settings, kind, variant):
    if path is None:
        return None
    frozen = read(path)
    require(frozen.get("schemaVersion") == 1 and frozen.get("task") == "DB-Exec-Parity-01"
            and frozen.get("frozen") is True, "An explicit frozen input manifest is required")
    key = settings["provider"] + "/" + variant
    inputs = frozen["allocationInputs"] if kind == "allocation" else frozen["inputs"]
    require(inputs[key]["identitySha256"] == snapshot["identitySha256"]
            and inputs[key]["identity"] == snapshot["identity"], "Actual inputs differ from the explicit freeze")
    if kind in LONG:
        cell = frozen["longCells"][kind + "/" + key]
        require(cell["conditions"] == settings, "Long-cell conditions differ from the explicit freeze")
    return {"path": str(Path(path).resolve()), "sha256": sha(path),
            "requireZeroRejections": frozen.get("requireZeroRejections", False)}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def expected_commands(settings, snapshot, cases):
    provider, route = settings["provider"], snapshot["identity"]["route"]
    initialize = ROOT / f"restored-stage1/consumers/baseline-{provider}/korda-workload/out/DbPerf.Korda"
    argv = [snapshot["identity"]["expectedResultIdentity"]["executable"], "--connection", "{connection}",
            "--case", "mixed", "--cases", ",".join(cases), "--mode", "prepared", "--session", "persistent",
            "--concurrency", str(settings["concurrency"]), "--warmup", "64", "--seconds", str(settings["seconds"]),
            "--idle-seconds", str(settings["idle"]), "--arrival-rate", str(float(settings["rate"])),
            "--queue-capacity", str(settings["queue"]), "--rows", "32", "--batch-rows", "32",
            "--tenants", "8", "--orders-per-tenant", "1024", "--verify", "--output", "{output}/result.json"]
    allocation = snapshot["identity"]["allocationDiagnostic"]
    if route == "dapper" and provider == "sqlite":
        argv += ["--native-library", str(SQLITE)]
    if allocation:
        argv = ["env", "LD_PRELOAD=" + str(SHIM), "DB_PERF_ALLOC_PROFILE_LIBRARY=" + str(SHIM),
                "DB_PERF_ALLOC_CAPACITY=1048576", *argv, "--allocation-profile"]
    return [
        {"name": "initialize", "phase": "fixture-only", "cpus": "0-3", "timeoutSeconds": 240,
         "executableSha256": snapshot["identity"]["files"][str(initialize)]["sha256"],
         "argv": [str(initialize), "--connection", "{connection}", "--initialize", "--tenants", "8", "--orders-per-tenant", "1024"]},
        {"name": "client", "phase": "native-allocation-diagnostic" if allocation else "ordinary-mixed35",
         "cpus": "0-3", "timeoutSeconds": settings["seconds"] + settings["idle"] + 180,
         "executableSha256": snapshot["identity"]["expectedResultIdentity"]["executableSha256"], "argv": argv},
    ]


def validate_plan(plan, measurement, settings, snapshot, cases):
    identity = snapshot["identity"]
    require(plan["task"] == "DB-Exec-Parity-01" and plan["provider"] == settings["provider"]
            and plan["route"] == identity["route"] and plan["family"] == identity["family"], "Prepared plan selected another consumer")
    require(plan["sourceHelperSha256"] == identity["files"][str(HELPER)]["sha256"], "Prepared helper identity changed")
    require(plan["commands"] == expected_commands(settings, snapshot, cases), "Prepared argv, duration, affinity, or executable identity differs")
    require(plan["logicalFixture"]["manifestSha256"] == MANIFEST_SHA
            and plan["logicalFixture"]["tenants"] == 8 and plan["logicalFixture"]["ordersPerTenant"] == 1024
            and plan["logicalFixture"]["customers"] == 256, "Fixture differs from mixed35")
    if settings["provider"] == "sqlite":
        require(plan["connection"] == str(measurement / "mixed35.sqlite") and "postgres" not in plan,
                "SQLite fixture is not fresh and dedicated")
    else:
        require(plan["postgres"] == {"bin": str(POSTGRES), "data": str(measurement / "postgres-data"),
                "maxConnections": 100, "maxClientConcurrency": settings["concurrency"], "cpus": "4-7"},
                "PostgreSQL server/affinity/fixture configuration changed")


def number(value, label, minimum=0):
    require(type(value) in (int, float) and math.isfinite(value) and value >= minimum, "Invalid " + label)
    return value


def close(actual, expected, label):
    number(actual, label)
    require(math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-9), "Derived " + label + " differs from raw counters")


def pid_identity(value):
    require(isinstance(value, dict) and type(value.get("pid")) is int and value["pid"] > 0
            and type(value.get("startTicks")) is int and value["startTicks"] > 0, "Missing PID/startTicks identity")
    return [value["pid"], value["startTicks"]]


def current_process_identity(pid):
    try:
        raw = Path(f"/proc/{pid}/stat").read_text()
        fields = raw[raw.rfind(")") + 2:].split()
        return {"pid": pid, "parentPid": int(fields[1]), "startTicks": int(fields[19])}
    except (FileNotFoundError, ProcessLookupError):
        return None


def interrupt_signal(signum, frame):
    raise KeyboardInterrupt("Wrapper received signal " + str(signum))


def require_unblocked(path=BLOCKER):
    require(not path.exists(), "Prior observer retirement is unproven; inspect and independently resolve " + str(path))


def clean_retirement(output, provider, observer_returncode):
    """Conservative lease release, separate from business/timing acceptance."""
    if observer_returncode != 0:
        return False
    try:
        retirement = read(output / "observer-adapter-retirement.json")
        if not (retirement["passed"] is True and retirement["completed"] is True and retirement["sourceIdentitiesUnchanged"] is True):
            return False
        for name in ("initialize", "client"):
            command = read(output / (name + ".command.json"))
            if not (command["success"] is True and command["exitCode"] == 0 and command["timedOut"] is False and command["observerErrors"] == []):
                return False
        if provider == "postgresql":
            owner = read(output / "postgres-owner.json")
            if owner["exitCode"] != 0 or any(key in owner for key in ("error", "finalSampleError", "shutdownError", "cpuGroupError")):
                return False
        return True
    except (OSError, KeyError, ValueError):
        return False


def stop_observer(child):
    """Give the existing observer its cleanup path; never claim unseen retirement."""
    try:
        child.send_signal(signal.SIGINT)
    except ProcessLookupError:
        return "Observer exited before SIGINT; persistent marker still requires owner-retirement review"
    try:
        child.wait(timeout=45)
        return "Observer received SIGINT and exited; persistent marker still requires owner-retirement review"
    except subprocess.TimeoutExpired:
        try:
            child.terminate()
        except ProcessLookupError:
            pass
        return "Observer did not retire within 45 seconds; child/server cleanup is unproven; persistent marker blocks another cell"


def validate_command(receipt, item, output, connection):
    require(receipt["name"] == item["name"] and receipt["phase"] == item["phase"]
            and receipt["timeoutSeconds"] == item["timeoutSeconds"] and receipt["exitCode"] == 0
            and receipt["success"] is True and receipt["timedOut"] is False and receipt["observerErrors"] == [],
            "Command did not finish cleanly: " + item["name"])
    expected = ["taskset", "-c", item["cpus"], *[value.replace("{connection}", connection).replace("{output}", str(output))
                                                   for value in item["argv"]]]
    require(receipt["argv"] == expected, "Executed command differs from prepared argv")
    require(receipt["finishedMonotonicNs"] > receipt["startedMonotonicNs"], "Command clock boundaries are invalid")
    for name, expected_hash in receipt["files"].items():
        require(Path(name).name == name and sha(output / name) == expected_hash, "Command raw evidence changed: " + name)
    require(set(receipt["files"]) == {item["name"] + ".stdout.log", item["name"] + ".resources.jsonl"},
            "Incomplete command evidence inventory")
    require(receipt["resourceSamples"] == item["name"] + ".resources.jsonl", "Unexpected resource sample path")
    return pid_identity(receipt["clientIdentity"])


def validate_result(output, plan_path, settings, snapshot, kind, freeze):
    sys.path.insert(0, str(REPO))
    campaign = load_module("db_exec_parity_campaign_gate", REPO / "campaign.py")
    adapter = load_module("db_exec_parity_observer_gate", ADAPTER)
    manifest = read(MANIFEST)
    queries = manifest["queries"]
    cases = [item["name"] for item in queries]
    require(len(cases) == len(set(cases)) == 35, "Expected the frozen 35-case sequence")
    plan, raw = read(plan_path), read(output / "result.json")
    validate_plan(plan, output, settings, snapshot, cases)
    require(sha(output / "plan.json") == sha(plan_path), "Observer executed a different plan")
    runner, retirement = read(output / "runner.json"), read(output / "observer-adapter-retirement.json")
    require(runner["runnerSha256"] == OBSERVER_SHA and runner["planSha256"] == sha(plan_path)
            and runner["cpuAffinity"] == [8], "Observer identity/affinity differs")
    for entry in (runner["observerAdapter"], retirement):
        require(entry["adapterSha256"] == ADAPTER_SHA and entry["originalObserverSha256"] == OBSERVER_SHA
                and entry["repositoryObserverModified"] is False, "Unreviewed observer adapter")
    require(retirement["passed"] is True and retirement["completed"] is True
            and retirement["sourceIdentitiesUnchanged"] is True, "Observer did not retire with unchanged sources")
    expected = snapshot["identity"]["expectedResultIdentity"]
    require(raw["Provider"] == expected["provider"] and raw["Route"] == expected["route"]
            and raw["NativeAot"] is True and raw["PackageVersion"] == expected["packageVersion"]
            and raw["ExecutableSha256"] == expected["executableSha256"], "Actual result is not the frozen Native AOT consumer")
    native = expected["native"]
    require((raw["LoadedNativePath"] is None and raw["LoadedNativeSha256"] is None) if native is None else
            (str(Path(raw["LoadedNativePath"]).resolve()) == native["path"] and raw["LoadedNativeSha256"] == native["sha256"]),
            "Loaded provider image differs from the package/engine snapshot")
    for key, value in {"Case": "mixed", "Mode": "prepared", "SessionMode": "persistent", "EmptyDriver": False,
                       "Concurrency": settings["concurrency"], "WarmupPerWorker": 64, "RequestedRows": 32,
                       "BatchRows": 32, "Tenants": 8, "OrdersPerTenant": 1024}.items():
        require(raw[key] == value, "Actual workload setting differs: " + key)
    offered = raw["OfferedLoad"]
    require(offered["RequestsPerSecond"] == settings["rate"] and offered["OfferedSeconds"] == settings["seconds"]
            and offered["QueueCapacity"] == settings["queue"], "Actual offered rate/duration/queue differs")
    normalized = campaign.normalized_result(raw, cases, settings["seconds"], settings["rate"], require_coverage=True)
    counts = normalized["counts"]
    require(normalized["correctnessPassed"] is True and counts["failed"] == 0 and counts["succeeded"] > 0
            and raw["Errors"] == [] and offered["Errors"] == [] and offered["ErrorClasses"] == {}, "Business failures cannot enter comparison")
    for name, key in (("Planned", "planned"), ("Started", "started"), ("Completed", "succeeded"),
                      ("Failed", "failed"), ("Retries", "retries"), ("Rows", "rows")):
        require(raw[name] == counts[key], "Outer and offered ledgers differ: " + name)
    require([item["Name"] for item in raw["Cases"]] == cases and set(raw["ExpectedResults"]) == set(cases),
            "Per-case result/oracle sequence differs")
    for query, item in zip(queries, raw["Cases"]):
        expected_result = raw["ExpectedResults"][query["name"]]
        require(item["Succeeded"] > 0 and item["Failed"] == 0
                and item["Rows"] == item["Succeeded"] * query["expectedRows"], "Per-case consumed rows differ: " + query["name"])
        require(expected_result["Rows"] == query["expectedRows"] and int(expected_result["Digest"]) == int(query["expectedDigest"]),
                "Per-case digest oracle differs: " + query["name"])
    zero_required = kind == "zero-cost" or bool(freeze and freeze["requireZeroRejections"])
    require(not zero_required or counts["rejected"] == 0, "The zero-rejection lane rejected work")
    if kind == "allocation":
        require(raw["TimingComparisonEligible"] is False and raw["NativeAllocationProfile"]["passed"] is True,
                "Native allocation diagnostics cannot grant ordinary timing")
        campaign.validate_native_profile(raw["NativeAllocationProfile"], sha(SHIM), 1048576)
    else:
        campaign.validate_uninstrumented_timing(raw)
        require(raw["TimingComparisonEligible"] is True, "Ordinary timing eligibility must be explicit")
    service = offered["SuccessServiceHistogram"]
    require(raw["Latencies"]["Histogram"] == service, "Outer service histogram differs from offered ledger")
    quantiles = {}
    for label, histogram in (("service", service), ("scheduled", offered["SuccessScheduledHistogram"]),
                              ("startDelay", offered["StartDelayHistogram"])):
        quantiles[label] = {"p" + str(percent) + "MicrosecondsUpper": campaign.quantile(histogram, percent / 100)
                            for percent in (50, 95, 99)}
    for percent in (50, 95, 99):
        close(raw["Latencies"][f"P{percent}MicrosecondsUpper"], quantiles["service"][f"p{percent}MicrosecondsUpper"], "service quantile")
        close(normalized[f"p{percent}MicrosecondsUpper"], quantiles["scheduled"][f"p{percent}MicrosecondsUpper"], "scheduled quantile")
    start, end = raw["SteadyStartMonotonicNs"], raw["SteadyEndMonotonicNs"]
    require(type(start) is int and type(end) is int and start < end, "Missing raw process measurement boundaries")
    close(raw["EffectiveSeconds"], (end - start) / 1e9, "effective duration")
    require(abs(start - normalized["steadyStartMonotonicNs"]) <= 1000
            and normalized["plannedOfferedEndMonotonicNs"] <= end <= normalized["drainedMonotonicNs"] + 1000,
            "Process and offered timing boundaries disagree")
    before, after, idle = raw["ProcessBefore"], raw["ProcessAfter"], raw["Idle"]
    require(isinstance(idle, dict) and idle["RequestedSeconds"] == settings["idle"]
            and idle["ObservedSeconds"] >= settings["idle"] - .01, "Release/idle observation is missing or too short")
    for reading in (before, after, idle["Before"], idle["After"]):
        for key in ("UserCpuSeconds", "SystemCpuSeconds", "RssBytes", "PeakRssBytes", "TotalGcPauseTicks"):
            number(reading[key], "process " + key)
        require(type(reading["TotalGcPauseTicks"]) is int and reading["PeakRssBytes"] >= reading["RssBytes"] > 0,
                "Invalid process RSS/GC pause snapshot")
    cpu_user, cpu_system = after["UserCpuSeconds"] - before["UserCpuSeconds"], after["SystemCpuSeconds"] - before["SystemCpuSeconds"]
    close(raw["UserCpuSeconds"], cpu_user, "client user CPU")
    close(raw["SystemCpuSeconds"], cpu_system, "client system CPU")
    close(raw["CpuSecondsPerSuccessfulOperation"], (cpu_user + cpu_system) / counts["succeeded"], "CPU per success")
    require(type(raw["AllocatedBefore"]) is int and type(raw["AllocatedAfter"]) is int
            and raw["AllocatedAfter"] >= raw["AllocatedBefore"] >= 0
            and raw["AllocatedBytes"] == raw["AllocatedAfter"] - raw["AllocatedBefore"], "Managed allocation boundary differs")
    close(raw["BytesPerSuccessfulOperation"], raw["AllocatedBytes"] / counts["succeeded"], "managed bytes per success")
    close(raw["BytesPerRow"], raw["AllocatedBytes"] / counts["rows"], "managed bytes per row")
    require(all(type(raw[key]) is int and raw[key] >= 0 for key in ("Gen0", "Gen1", "Gen2")), "Invalid process GC counts")
    readings = (before, after, idle["Before"], idle["After"])
    require(all(b["TotalGcPauseTicks"] >= a["TotalGcPauseTicks"] for a, b in zip(readings, readings[1:])), "GC pause counter reset")
    for key in ("UserCpuSeconds", "SystemCpuSeconds"):
        close(idle[key], idle["After"][key] - idle["Before"][key], "idle " + key)
    for key in ("ManagedBytesBefore", "ManagedBytesAfter"):
        require(type(idle[key]) is int and idle[key] >= 0, "Invalid idle managed-heap observation")
    if snapshot["identity"]["route"] == "korda":
        for key in ("Sources", "Sessions", "Operations", "Cursors", "Buffers", "Owners"):
            require(raw["Drained"][key] == 0, "Tracked native owner did not drain: " + key)
        require(all(raw["Drained"].get(key) in (None, 0) for key in ("PullChannels", "CommandCompletions")), "Extra tracked owners did not drain")
    else:
        require(raw["Drained"]["ApplicationConnections"] == 0, "Dapper application connections did not drain")
    command = read(output / "client.command.json")
    connection = command["argv"][command["argv"].index("--connection") + 1]
    if settings["provider"] == "sqlite":
        require(connection == str(output / "mixed35.sqlite"), "SQLite command connected to another database")
    else:
        require(re.fullmatch(r"postgresql://korda@127\.0\.0\.1:\d+/db_perf_01", connection) is not None,
                "PostgreSQL command did not use the dedicated local server")
    initialize = read(output / "initialize.command.json")
    validate_command(initialize, plan["commands"][0], output, connection)
    client_id = validate_command(command, plan["commands"][1], output, connection)
    require(initialize["finishedMonotonicNs"] <= command["startedMonotonicNs"] <= start
            and normalized["drainedMonotonicNs"] <= command["finishedMonotonicNs"], "One uninterrupted client interval is not established")
    samples = [json.loads(line) for line in (output / "client.resources.jsonl").read_text().splitlines() if line]
    require(samples and all(right["monotonicNs"] > left["monotonicNs"] for left, right in zip(samples, samples[1:])),
            "Client observations are missing or not monotonic")
    require(retirement["expectedRootIdentities"]["client"] == client_id, "Observer/client PID startTicks binding differs")
    observed_client = 0
    for sample in samples:
        observation = sample["clientProcObservation"]
        if observation and observation["rootIdentity"]:
            require(pid_identity(observation["rootIdentity"]) == client_id, "A second client process entered the cell")
            observed_client += 1
    require(observed_client >= 2, "Single-process client observation coverage is missing")
    lifetime_keys = ("processLifetimeUserCpuSeconds", "processLifetimeSystemCpuSeconds", "processLifetimeMaxRssBytes")
    for key in lifetime_keys:
        number(command[key], "client wait4 " + key)
    server_evidence = None
    if settings["provider"] == "postgresql":
        owner = read(output / "postgres-owner.json")
        require(owner["exitCode"] == 0 and not any(key in owner for key in ("error", "finalSampleError", "shutdownError", "cpuGroupError")),
                "Dedicated PostgreSQL server did not retire cleanly")
        server_id = pid_identity(owner["identity"])
        require(owner["argv"][:4] == ["taskset", "-c", "4-7", str(POSTGRES / "postgres")]
                and owner["argv"][owner["argv"].index("-D") + 1] == str(output / "postgres-data")
                and owner["argv"][owner["argv"].index("-p") + 1] == connection.split(":")[-1].split("/")[0],
                "PostgreSQL owner does not match the client connection and prepared server")
        require(owner["startedMonotonicNs"] < initialize["startedMonotonicNs"]
                and owner["finishedMonotonicNs"] > command["finishedMonotonicNs"]
                and retirement["expectedRootIdentities"]["server"] == server_id, "Server owner/PID/lifetime binding differs")
        for sample in samples:
            observation = sample["serverProcObservation"]
            if observation and observation["rootIdentity"]:
                require(pid_identity(observation["rootIdentity"]) == server_id, "Server PID identity changed")
        intervals = adapter.visible_cpu_intervals(samples, normalized["steadyStartMonotonicNs"], normalized["drainedMonotonicNs"], "server")
        require(intervals["rootPidStartTicks"] == server_id, "CPU endpoints do not belong to the server owner")
        for key in lifetime_keys:
            number(owner[key], "server wait4 " + key)
        metric_available = all(intervals[name] is not None and intervals[name]["allObservedCountersMonotonic"]
                               for name in ("inner", "outer"))
        server_evidence = {"visibleSteadyIntervals": intervals, "observedInnerOuterAvailable": metric_available,
                           "wait4Lifetime": {key: owner[key] for key in lifetime_keys},
                           "lifetimeScope": "Separate lifetime total includes server startup, fixture, warmup, idle and shutdown; never added to sampled interval CPU",
                           "exactSteadyCpuProven": False, "unobservedExitedChildrenOrNonAtomicTransferLoss": "unknown"}
    resources = {"clientUserCpuSeconds": cpu_user, "clientSystemCpuSeconds": cpu_system,
                 "clientCpuSecondsPerSuccess": (cpu_user + cpu_system) / counts["succeeded"],
                 "managedAllocatedBytes": raw["AllocatedBytes"], "managedBytesPerSuccess": raw["BytesPerSuccessfulOperation"],
                 "gcCountsProcessScope": {key: raw[key] for key in ("Gen0", "Gen1", "Gen2")},
                 "gcPauseSecondsProcessScope": (after["TotalGcPauseTicks"] - before["TotalGcPauseTicks"]) / 10_000_000,
                 "peakRssThroughMeasurementBytes": after["PeakRssBytes"], "releasedIdleRssBytes": idle["After"]["RssBytes"],
                 "releasedIdlePssBytes": idle["After"]["PssBytes"], "idleObservation": idle,
                 "clientWait4Lifetime": {key: command[key] for key in lifetime_keys}, "postgres": server_evidence,
                 "nativeAllocationProfile": raw["NativeAllocationProfile"],
                 "allocationScope": raw["AllocationAttribution"], "frameworkOnlyManagedBytes": None,
                 "producerAndHarnessCpuAndAllocationsIncluded": True,
                 "scope": "Client process counters bracket the nominal offered interval and include boundary observation, scheduler/producer, driver, framework and DTO work. Peak RSS is lifetime-to-snapshot, idle RSS follows owner release without forced GC."}
    raw_files = [output / name for name in ("result.json", "plan.json", "runner.json", "observer-adapter-retirement.json",
                 "client.command.json", "client.resources.jsonl", "client.stdout.log", "initialize.command.json",
                 "initialize.resources.jsonl", "initialize.stdout.log")]
    if settings["provider"] == "postgresql":
        raw_files += [output / name for name in ("postgres-owner.json", "postgres-settings.txt", "postgres.log", "postgres-init.log")]
    return {"schemaVersion": 1, "task": "DB-Exec-Parity-01", "passed": True, "kind": kind,
            "conditions": settings, "inputIdentitySha256": snapshot["identitySha256"], "freeze": freeze,
            "ordinaryTiming": kind != "allocation", "finalCredit": False, "newFinalCellCredit": False,
            "longEvidenceReadyForReview": kind in LONG and (server_evidence is None or server_evidence["observedInnerOuterAvailable"]),
            "normalized": normalized, "quantiles": quantiles, "resources": resources,
            "oneClientPidStartTicks": client_id, "warmupPerWorkerOutsideMeasuredInterval": 64,
            "additionalVerificationCasesPerWorkerBeforeWarmup": 35,
            "zeroRejections": counts["rejected"] == 0,
            "rawFiles": {str(path): {"sha256": sha(path), "bytes": path.stat().st_size} for path in raw_files},
            "limitations": ["One cell is evidence for independent review, never automatic final acceptance.",
                            "Wrapper flock serializes cooperating wrappers; external quietness is a separately controlled campaign condition.",
                            "Native allocations require their own instrumented lane; process totals cannot establish framework-only 0 B.",
                            "PostgreSQL visible-proc intervals are non-atomic observations, not exact steady CPU bounds."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("provider", choices=("sqlite", "postgresql"))
    parser.add_argument("variant", choices=VARIANTS)
    parser.add_argument("--kind", choices=KINDS, required=True)
    parser.add_argument("--seconds", type=int, required=True)
    parser.add_argument("--rate", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--freeze", type=Path)
    parser.add_argument("--queue", type=int, default=64)
    parser.add_argument("--idle", type=int, default=5)
    parser.add_argument("--concurrency", type=int)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    validate_request(args)
    output = contained(args.output)
    require(not output.exists(), "Every attempt requires a new output directory; prior attempts are immutable")
    output.mkdir(parents=True, exist_ok=False)
    state = {"schemaVersion": 1, "task": "DB-Exec-Parity-01", "startedUtc": utc(),
             "provider": args.provider, "variant": args.variant, "kind": args.kind,
             "output": str(output), "wrapperPid": os.getpid(), "finalCredit": False,
             "newFinalCellCredit": False, "workloadExecuted": False, "stages": []}
    def stage(name, **details):
        state.update(stage=name, updatedUtc=utc(), **details)
        state["stages"].append({"stage": name, "utc": state["updatedUtc"], **details})
        atomic(output / "resume.json", state)
    lock, child, lease = None, None, None
    previous_term = signal.signal(signal.SIGTERM, interrupt_signal)
    stage("created")
    try:
        lock = (LOCAL / "verified-mixed-cell.lock").open("a+")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        require_unblocked()
        stage("serial-lock-acquired", serialLockScope="cooperating verified wrappers only")
        settings = conditions(args.provider, args.seconds, args.rate, args.queue, args.idle, args.concurrency)
        stage("snapshot-before")
        before = input_snapshot(args.provider, args.variant, args.kind == "allocation")
        atomic(output / "snapshot-before.json", before)
        freeze = validate_freeze(args.freeze, before, settings, args.kind, args.variant)
        stage("inputs-verified", inputIdentitySha256=before["identitySha256"], freeze=freeze, conditions=settings)
        measurement = output / "measurement"
        family, route = VARIANTS[args.variant]
        prepare = [sys.executable, str(HELPER), args.provider, route, "--family", family,
                   "--reference-family", "baseline-final", "--seconds", str(args.seconds), "--rate", str(args.rate),
                   "--queue", str(args.queue), "--idle", str(args.idle), "--concurrency", str(settings["concurrency"]),
                   "--output", str(measurement), "--postgres-bin", str(POSTGRES), "--sqlite-library", str(SQLITE), "--prepare-only"]
        if args.kind == "allocation":
            prepare.append("--allocation-profile")
        stage("preparing", prepareArgv=prepare)
        with (output / "prepare.log").open("x") as log:
            subprocess.run(prepare, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=60)
        plan_path = measurement.with_suffix(".plan.json")
        cases = [query["name"] for query in read(MANIFEST)["queries"]]
        validate_plan(read(plan_path), measurement, settings, before, cases)
        stage("prepared", plan=str(plan_path), planSha256=sha(plan_path))
        if args.prepare_only:
            stage("prepared-only", passed=True, workloadExecuted=False)
            print(json.dumps({"passed": True, "preparedOnly": True, "output": str(output), "finalCredit": False}), flush=True)
            return 0
        command = ["taskset", "-c", "8", sys.executable, str(ADAPTER), str(plan_path), "--output", str(measurement), "--sample-seconds", "0.25"]
        with (output / "observer.log").open("x") as log:
            lease = {"task": "DB-Exec-Parity-01", "attemptOutput": str(output), "createdUtc": utc(),
                     "wrapperIdentity": current_process_identity(os.getpid()), "observerIdentity": None,
                     "stage": "launch-intent", "reason": "Retain across abrupt termination until clean retirement is established",
                     "resolution": "After independent review of bound process identities and command/server retirement, archive this marker into the attempt with an explicit unblock-review receipt; never silently delete it"}
            atomic(BLOCKER, lease)
            child = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            lease.update(stage="running", observerIdentity=current_process_identity(child.pid))
            atomic(BLOCKER, lease)
            stage("running", workloadExecuted=True, observerPid=child.pid, observerArgv=command)
            deadline = time.monotonic() + args.seconds + args.idle + 600
            while child.poll() is None:
                try:
                    child.wait(timeout=min(30, max(.1, deadline - time.monotonic())))
                except subprocess.TimeoutExpired:
                    require(time.monotonic() < deadline, "Outer observer deadline expired")
                    state["heartbeatUtc"] = utc()
                    atomic(output / "resume.json", state)
            stage("observer-exited", observerExitCode=child.returncode)
        require(clean_retirement(measurement, args.provider, child.returncode),
                "Observer/command/server retirement is not proven clean; persistent marker blocks subsequent cells")
        require(read(BLOCKER)["attemptOutput"] == str(output), "Persistent lease identity changed")
        atomic(output / "observer-retirement-lease.json", dict(lease, stage="clean-retirement-confirmed",
               retiredUtc=utc(), observerExitCode=child.returncode))
        BLOCKER.unlink()
        lease = None
        stage("snapshot-after")
        after = input_snapshot(args.provider, args.variant, args.kind == "allocation")
        atomic(output / "snapshot-after.json", after)
        require(before["identitySha256"] == after["identitySha256"] and before["identity"] == after["identity"],
                "Actual input bytes/environment/host changed during the cell")
        require(freeze is None or sha(args.freeze) == freeze["sha256"], "Freeze manifest changed during the cell")
        require(child.returncode == 0, "Observer returned nonzero; raw evidence retained")
        stage("validating")
        validation = validate_result(measurement, plan_path, settings, before, args.kind, freeze)
        validation.update(completedUtc=utc(), prePostInputIdentitiesEqual=True,
                          snapshotBeforeSha256=sha(output / "snapshot-before.json"), snapshotAfterSha256=sha(output / "snapshot-after.json"),
                          retirementLeaseSha256=sha(output / "observer-retirement-lease.json"))
        atomic(output / "validation.json", validation)
        stage("completed", passed=True, validationSha256=sha(output / "validation.json"))
        print(json.dumps({"passed": True, "output": str(output), "counts": validation["normalized"]["counts"],
                          "successOpsPerSecond": validation["normalized"]["successOpsPerSecond"], "finalCredit": False}), flush=True)
        return 0
    except BaseException as error:
        cleanup = None
        if child is not None and child.poll() is None:
            cleanup = stop_observer(child)
        if lease is not None:
            lease.update(stage="blocked-pending-independent-review", updatedUtc=utc(), cleanup=cleanup,
                         failure={"type": type(error).__name__, "message": str(error)})
            atomic(BLOCKER, lease)
        failure = {"type": type(error).__name__, "message": str(error), "traceback": traceback.format_exc(),
                   "failedFromStage": state["stage"], "cleanup": cleanup, "finalCredit": False}
        atomic(output / "failure.json", failure)
        stage("failed", passed=False, failure=failure)
        print(json.dumps({"passed": False, "output": str(output), "error": failure["message"], "finalCredit": False}), file=sys.stderr, flush=True)
        return 1
    finally:
        signal.signal(signal.SIGTERM, previous_term)
        if lock is not None:
            lock.close()


if __name__ == "__main__":
    raise SystemExit(main())
