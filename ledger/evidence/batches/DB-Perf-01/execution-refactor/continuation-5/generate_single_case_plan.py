#!/usr/bin/env python3
"""Write a fresh local run.py plan; never build or execute a consumer/database.

ordinary: a separate ordinary Korda initializer, then Korda/Dapper pairs.
diagnostic: its matching ordinary Korda initializer, then only ABI-counting runs.
Both use numeric, tx-rollback, tx-commit at C1 for 15 seconds, in that order.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shlex
import shutil
import sys


CASES = ("numeric", "tx-rollback", "tx-commit")
DATASET = {"tenants": 8, "ordersPerTenant": 1024, "requestedRows": 32, "batchRows": 32}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(path, expected=None):
    path = Path(path).resolve(strict=True)
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    require(expected is None or digest == expected, "Changed input: " + str(path))
    return {"path": str(path), "sha256": digest}


def ordinary(directory, cohort, provider, manifest_hash):
    directory = directory.resolve(strict=True)
    receipt_path = directory.parent / "build-receipt.json"
    receipt = json.loads(receipt_path.read_text())
    korda = cohort == "korda"
    require(receipt.get("provider") == provider, "Consumer provider differs: " + str(receipt_path))
    require(receipt.get("kind") == ("workload" if korda else "benchmark"), "A workload consumer is required")
    require(receipt.get("exit_code" if korda else "exitCode") == 0, "Consumer build did not succeed")
    require(receipt.get("workloadManifestSha256") == manifest_hash, "Consumer manifest differs")
    if korda:
        require(receipt.get("project_references") == 0, "Korda must be an external PackageReference consumer")
    executable = identity(directory / ("DbPerf.Korda" if korda else "DbPerf.Dapper"),
                          receipt["executable_sha256" if korda else "executableSha256"])
    sources = {name: identity(directory.parent / name, digest) for name, digest in receipt["sources"].items()}
    native = {name: identity(directory / name, digest) for name, digest in receipt.get("native_images", {}).items()}
    if korda:
        package, version = receipt["package"].lower(), receipt["version"].lower()
        packages = {receipt["package"] + "/" + receipt["version"]: identity(
            directory.parent / "packages" / package / version / f"{package}.{version}.nupkg", receipt["package_sha256"])}
    else:
        packages = {name: identity(value["path"], value["sha256"]) for name, value in receipt["packages"].items()}
    return {"directory": str(directory), "executable": executable, "buildReceipt": identity(receipt_path),
            "receiptData": receipt, "sources": sources, "packages": packages, "nativeImages": native}


def diagnostic(directory, korda):
    directory = directory.resolve(strict=True)
    receipt_path = directory.parent / "diagnostic-build.json"
    receipt = json.loads(receipt_path.read_text())
    require(receipt.get("consumerKind") == "workload" and receipt.get("instrumented") is True,
            "A workload ABI diagnostic is required")
    require(receipt.get("TimingComparisonEligible") is False and receipt.get("timingCredit") is False
            and receipt.get("allocationCredit") is False, "Diagnostic credit flags are missing")
    require(receipt.get("commands") and all(c["exitCode"] == 0 for c in receipt["commands"]),
            "Diagnostic build did not succeed")
    require(all(receipt.get(key) is True for key in
                ("ordinaryConsumerUnchanged", "packageUnchanged", "nativeImagesUnchanged")),
            "Diagnostic ordinary-input preservation was not confirmed")
    original = korda["receiptData"]
    require(receipt["sourceReceiptSha256"] == korda["buildReceipt"]["sha256"]
            and receipt["sourceExecutableSha256"] == korda["executable"]["sha256"]
            and receipt["sourcePackageSha256"] == original["package_sha256"]
            and receipt["sourceNativeImages"] == original["native_images"],
            "Diagnostic is not an overlay of the supplied ordinary Korda consumer")
    require(set(receipt["runEnvironment"]) == {"LD_PRELOAD"}, "Unexpected diagnostic environment")
    shim = identity(directory / "libcursor_probe.so", receipt["outputs"]["libcursor_probe.so"])
    require(Path(receipt["runEnvironment"]["LD_PRELOAD"]).resolve() == Path(shim["path"]),
            "Diagnostic preload path differs")
    native = {name: identity(directory / name, digest) for name, digest in original["native_images"].items()}
    sources = {name: identity(directory.parent / name, digest) for name, digest in receipt["overlaySources"].items()}
    return {"directory": str(directory), "buildReceipt": identity(receipt_path), "receiptData": receipt,
            "executable": identity(directory / "DbPerf.Korda", receipt["outputs"]["DbPerf.Korda"]),
            "shim": shim, "nativeImages": native, "sources": sources}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Korda checkout supplying run.py and the manifest")
    parser.add_argument("--provider", choices=("sqlite", "postgresql"), required=True)
    parser.add_argument("--lane", choices=("ordinary", "diagnostic"), default="ordinary")
    parser.add_argument("--korda-dir", type=Path, required=True, help="ordinary published out directory")
    parser.add_argument("--dapper-dir", type=Path, required=True, help="ordinary published out directory")
    parser.add_argument("--diagnostic-dir", type=Path, help="matching ABI diagnostic out directory")
    parser.add_argument("--postgres-bin", type=Path)
    parser.add_argument("--sqlite-library", type=Path, help="actual Dapper libsqlite3.so")
    parser.add_argument("--plan", type=Path, required=True, help="new plan JSON outside the evidence directory")
    parser.add_argument("--output", type=Path, required=True, help="new run.py evidence directory")
    args = parser.parse_args()
    require((args.lane == "diagnostic") == (args.diagnostic_dir is not None),
            "Only the diagnostic lane accepts and requires --diagnostic-dir")
    plan_path, output = args.plan.resolve(), args.output.resolve()
    require(not plan_path.exists() and not output.exists() and not plan_path.is_relative_to(output),
            "Use a fresh plan and evidence directory; keep the plan outside that directory")
    source = args.source.resolve(strict=True)
    runner = identity(source / "benchmarks/db-perf/run.py")
    manifest = identity(source / "benchmarks/db-perf/workload/queries-v3.json")
    workload = json.loads(Path(manifest["path"]).read_text())
    names = [query["name"] for query in workload["queries"]]
    require(workload["schemaVersion"] == 3 and len(names) == len(set(names)) == 35
            and all(name in names for name in CASES)
            and all(workload["dataset"].get(key) == value for key, value in DATASET.items()),
            "The actual manifest differs from the selected 35-case dataset")
    consumers = {cohort: ordinary(getattr(args, cohort + "_dir"), cohort, args.provider, manifest["sha256"])
                 for cohort in ("korda", "dapper")}
    if args.diagnostic_dir is not None:
        consumers["diagnostic"] = diagnostic(args.diagnostic_dir, consumers["korda"])
    inputs = {"generator": identity(__file__), "runner": runner, "manifest": manifest, "consumers": consumers}
    native_args = []
    if args.provider == "sqlite":
        require(args.sqlite_library is not None, "SQLite requires --sqlite-library for Dapper")
        inputs["sqliteLibrary"] = identity(args.sqlite_library)
        native_args = ["--native-library", inputs["sqliteLibrary"]["path"]]
    else:
        require(args.postgres_bin is not None, "PostgreSQL requires --postgres-bin")
        inputs["postgresTools"] = {name: identity(args.postgres_bin / name)
                                   for name in ("initdb", "postgres", "pg_isready", "psql")}
    env = identity(shutil.which("env") or "/usr/bin/env")
    inputs["env"] = env
    commands = []

    def argv(cohort, case):
        command = [consumers[cohort]["executable"]["path"], "--connection", "{connection}", "--case", case,
                   "--mode", "prepared", "--session", "persistent", "--concurrency", "1", "--warmup", "64",
                   "--rows", "32", "--batch-rows", "32", "--tenants", "8", "--orders-per-tenant", "1024"]
        if cohort == "dapper":
            command += native_args
        if cohort == "diagnostic":
            command = [env["path"], "LD_PRELOAD=" + consumers[cohort]["shim"]["path"], *command]
        return command

    def add(name, cohort, case, command, fixture=False):
        require("--cases" not in command, "A single-case plan cannot contain --cases")
        instrumented = cohort == "diagnostic"
        item = {"name": name, "cohort": cohort, "case": case, "phase": "fixture" if fixture else args.lane,
                "argv": command, "cpus": "0-3", "timeoutSeconds": 600, "instrumented": instrumented,
                "timingRequested": not fixture and not instrumented, "longRunAcceptance": False}
        if fixture or instrumented:
            item.update(TimingComparisonEligible=False, timingCredit=False, allocationCredit=False)
        commands.append(item)

    add("fixture-initialize", "korda", "numeric", argv("korda", "numeric") + ["--initialize", "--operations", "0"], True)
    for case in CASES:
        for cohort in (("korda", "dapper") if args.lane == "ordinary" else ("diagnostic",)):
            name = cohort + "-" + case
            add(name, cohort, case, argv(cohort, case) + ["--seconds", "15", "--idle-seconds", "0",
                                                       "--output", "{output}/" + name + ".json"])
    plan = {"schemaVersion": 1, "provider": args.provider, "lane": "single-case-" + args.lane,
            "scope": "Local serial C1 observations; no environment or long-run acceptance is granted",
            "longRunAcceptance": False, "runnerSourceDirectory": str(source), "inputs": inputs,
            "manifestCaseNames": names, "selectedCases": list(CASES), "dataset": DATASET,
            "caseContracts": {query["name"]: query for query in workload["queries"] if query["name"] in CASES},
            "identityScope": "Consumer identity comes from its actual receipt/package hashes, not the runner checkout",
            "affinity": {"client": "0-3", "postgres": "4-7", "observer": "8"},
            "hostAdmission": "unproven; actual host/cgroup observations remain required", "commands": commands}
    if args.lane == "diagnostic":
        plan.update(instrumented=True, TimingComparisonEligible=False, timingCredit=False, allocationCredit=False)
    if args.provider == "postgresql":
        plan["postgres"] = {"bin": str(args.postgres_bin.resolve()), "data": str(output / "pgdata"),
                            "cpus": "4-7", "maxConnections": 64, "maxClientConcurrency": 1}
    else:
        plan["connection"] = str(output / "fixture.sqlite")
    # Clear inherited instrumentation for observer, database and ordinary commands.
    # Only a diagnostic command's own env argv reinstates its exact preload.
    invocation = [env["path"], "-u", "LD_PRELOAD", "-u", "DB_PERF_ALLOC_PROFILE_LIBRARY", "-u", "DB_PERF_ALLOC_CAPACITY",
                  "taskset", "-c", "8", sys.executable, runner["path"], str(plan_path), "--output", str(output)]
    plan["runnerCommand"] = invocation
    spec = importlib.util.spec_from_file_location("single_case_runner", runner["path"])
    module = importlib.util.module_from_spec(spec)
    previous_bytecode = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous_bytecode
    module.validate_plan(plan, output)  # Pure plan validation; never main/database/execute.
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    with plan_path.open("x") as stream:
        json.dump(plan, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    print(shlex.join(invocation))


if __name__ == "__main__":
    main()
