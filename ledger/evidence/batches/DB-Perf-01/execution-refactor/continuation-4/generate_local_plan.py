#!/usr/bin/env python3
"""Write one fresh, serial run.py plan; never launch a consumer or database."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shlex


COHORTS = ("before", "candidate", "dapper")


def identity(path):
    path = path.resolve(strict=True)
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"path": str(path), "sha256": digest}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="actual Korda source checkout")
    parser.add_argument("--provider", choices=("sqlite", "postgresql"), required=True)
    parser.add_argument("--lane", choices=("phases", "calibration", "offered", "final"), required=True)
    for cohort in COHORTS:
        parser.add_argument(f"--{cohort}-dir", type=Path, required=True, help="published binary directory")
    parser.add_argument("--plan", type=Path, required=True, help="new JSON file outside the output directory")
    parser.add_argument("--output", type=Path, required=True, help="new run.py evidence directory")
    parser.add_argument("--postgres-bin", type=Path)
    parser.add_argument("--sqlite-library", type=Path, help="exact Dapper libsqlite3.so")
    parser.add_argument("--concurrency", type=int, help="required fixed C for offered/final")
    parser.add_argument("--rate", type=float, help="required observed/selected R for offered/final")
    parser.add_argument("--queue-capacity", type=int, default=64, help="consumer default, explicit in plans")
    args = parser.parse_args()
    fixed = args.lane in ("offered", "final")
    if fixed and (args.concurrency is None or not 1 <= args.concurrency <= 256
                  or args.rate is None or not math.isfinite(args.rate) or not 0 < args.rate <= 1_000_000):
        parser.error("offered/final require explicit valid --concurrency and --rate; no rate is inferred")
    if not fixed and (args.concurrency is not None or args.rate is not None):
        parser.error("phases/calibration have fixed concurrency; do not supply a rate")
    if not 1 <= args.queue_capacity <= 65536:
        parser.error("queue capacity is outside the existing consumer's bounds")
    source = args.source.resolve(strict=True)
    runner = identity(source / "benchmarks/db-perf/run.py")
    manifest = identity(source / "benchmarks/db-perf/workload/queries-v3.json")
    workload = json.loads(Path(manifest["path"]).read_text())
    names = [query["name"] for query in workload["queries"]]
    expected = {"tenants": 8, "ordersPerTenant": 1024, "requestedRows": 32, "batchRows": 32}
    if (workload["schemaVersion"] != 3 or len(names) != 35 or len(set(names)) != 35
            or any(not isinstance(name, str) or not name or "," in name for name in names)
            or any(workload["dataset"].get(key) != value for key, value in expected.items())):
        parser.error("the actual manifest does not describe the fixed 35-case, 8/1024, rows/batch32 workload")
    plan_path, output = args.plan.resolve(), args.output.resolve()
    if plan_path.exists() or output.exists() or plan_path.is_relative_to(output):
        parser.error("plan and output must be new, and the plan must be outside the output directory")
    binaries = {}
    for cohort in COHORTS:
        stem = "DbPerf.Dapper" if cohort == "dapper" else "DbPerf.Korda"
        if args.lane == "phases":
            stem = "DbPerf.DapperQueryPhases" if cohort == "dapper" else "DbPerf.QueryPhases"
        binaries[cohort] = identity(getattr(args, cohort + "_dir") / stem)
    native_args, native = [], None
    if args.provider == "sqlite":
        if args.sqlite_library is None:
            parser.error("SQLite Dapper requires the actual --sqlite-library")
        native = identity(args.sqlite_library)
        native_args = ["--native-library", native["path"]]
    elif args.postgres_bin is None:
        parser.error("PostgreSQL requires the actual --postgres-bin")
    commands = []

    def add(name, cohort, argv, seconds=0, timed=True):
        commands.append({"name": name, "cohort": cohort, "phase": args.lane if timed else "fixture",
                         "timingRequested": timed, "longRunAcceptance": False,
                         "comparisonRole": "baseline" if cohort == "before" else cohort,
                         "argv": argv, "cpus": "0-3", "timeoutSeconds": max(600, seconds + 315)})

    def mixed(cohort, concurrency):
        argv = [binaries[cohort]["path"], "--connection", "{connection}", "--case", "mixed",
                "--cases", ",".join(names), "--mode", "prepared", "--session", "persistent",
                "--concurrency", str(concurrency), "--rows", "32", "--batch-rows", "32",
                "--tenants", "8", "--orders-per-tenant", "1024", "--warmup", "64",
                "--queue-capacity", str(args.queue_capacity)]
        return argv + (native_args if cohort == "dapper" else [])

    if args.lane == "phases":
        # This existing consumer has positional initialize, then executes a probe.
        # Its entire separate fixture command is excluded from timing comparisons.
        add("fixture-phases", "candidate", [binaries["candidate"]["path"], "{connection}",
            "{output}/fixture-phases.json", "1", "1", "initialize", "--rows", "1"], timed=False)
        for index, rows in enumerate((1, 100, 1000)):
            order = ("candidate", "before", "dapper") if index == 1 else COHORTS
            for cohort in order:  # candidate receipt must exist before the matching Dapper command
                name = f"{cohort}-rows{rows}"
                argv = [binaries[cohort]["path"]]
                if cohort == "dapper":
                    argv += ["--connection", "{connection}", "--output", f"{{output}}/{name}.json",
                             "--korda-receipt", f"{{output}}/candidate-rows{rows}.json", "--rows", str(rows),
                             "--iterations", "256", "--windows", "3", *native_args]
                else:
                    argv += ["{connection}", f"{{output}}/{name}.json", "256", "3", "--rows", str(rows)]
                add(name, cohort, argv)
    else:
        add("fixture-mixed", "candidate", mixed("candidate", 1) + ["--initialize", "--operations", "0"], timed=False)
        settings = (1, 4, 8) if args.lane == "calibration" else (args.concurrency,)
        seconds = {"calibration": 15, "offered": 30, "final": 1800}[args.lane]
        for index, concurrency in enumerate(settings):
            order = COHORTS[index:] + COHORTS[:index]
            for cohort in order:
                name = f"{cohort}-c{concurrency}"
                argv = mixed(cohort, concurrency) + ["--verify", "--seconds", str(seconds),
                        "--idle-seconds", "15" if args.lane == "final" else "0",
                        "--output", f"{{output}}/{name}.json"]
                if fixed:
                    argv += ["--rate", str(args.rate)]
                add(name, cohort, argv, seconds)
    plan = {"schemaVersion": 1, "provider": args.provider, "lane": args.lane,
            "scope": "Local serial observations; before is baseline; existing analyzer decides final four-cell credit",
            "longRunAcceptance": False, "sourceDirectory": str(source),
            "inputs": {"runner": runner, "manifest": manifest, "consumers": binaries, "sqliteLibrary": native},
            "manifestCaseNames": names, "mixedDataset": expected,
            "phaseDataset": {"tenants": 2, "rowsPerTenant": 1000, "batchRows": 32},
            "affinity": {"client": "0-3", "postgres": "4-7", "observer": "8"},
            "hostAdmission": "not established by plan generation; observe actual host and cgroup visibility",
            "commands": commands}
    if args.provider == "postgresql":
        binary = args.postgres_bin.resolve(strict=True)
        plan["inputs"]["postgresTools"] = {name: identity(binary / name)
                                            for name in ("initdb", "postgres", "pg_isready", "psql")}
        concurrency = 8 if args.lane == "calibration" else args.concurrency or 1
        plan["postgres"] = {"bin": str(binary), "data": str(output / "pgdata"), "cpus": "4-7",
                            "maxConnections": max(64, concurrency + 8), "maxClientConcurrency": concurrency}
    else:
        plan["connection"] = str(output / "fixture.sqlite")
    invocation = ["taskset", "-c", "8", "python3", runner["path"], str(plan_path), "--output", str(output)]
    plan["runnerCommand"] = invocation
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    with plan_path.open("x") as stream:
        json.dump(plan, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
    print(shlex.join(invocation))  # Printed only: no subprocess, database, build or timing is started.


if __name__ == "__main__":
    main()
