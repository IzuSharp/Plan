#!/usr/bin/env python3
"""Local-only original phase comparison; no product or CI mutations.

Runs the existing Native AOT phase consumers. Their per-stage clocks and native
owner counters make these diagnostic observations, not final mixed-load timing.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("provider", choices=("sqlite", "postgresql"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=256)
    parser.add_argument("--windows", type=int, default=3)
    parser.add_argument("--family", default="baseline")
    parser.add_argument("--rows", default="1,100,1000", help="Comma-separated row cases in execution order")
    args = parser.parse_args()
    task = Path(__file__).resolve().parents[1]
    out = args.output.resolve()
    if out.exists():
        raise SystemExit("Fresh output required")
    out.parent.mkdir(parents=True, exist_ok=True)
    consumer = task / "consumers" / (args.family + "-" + args.provider)
    korda = consumer / "korda-query-phases/out/DbPerf.QueryPhases"
    reference = consumer if args.family == "allocation-baseline" else task / "consumers" / ("baseline-" + args.provider)
    dapper = reference / "dapper-query-phases/out/DbPerf.DapperQueryPhases"
    runner = task / "worktrees/Korda/benchmarks/db-perf/run.py"
    sqlite = task / "builds/baseline-sqlite/sqlite-image/shared/libsqlite3.so"
    binaries = {"korda": str(korda), "dapper": str(dapper), "runner": str(runner)}
    if args.provider == "sqlite":
        binaries["sqlite"] = str(sqlite)
    identity = {name: {"path": path, "sha256": digest(path)} for name, path in binaries.items()}
    plan = {"schemaVersion": 1, "task": "DB-Exec-Parity-01", "provider": args.provider,
            "scope": "Generated mapper/List allocation instrumentation; no timing credit" if args.family == "allocation-baseline" else "Original existing phase-clock diagnostic, no preload/injected probes; not final timing",
            "identities": identity, "commands": []}
    if args.provider == "sqlite":
        plan["connection"] = str(out / "query-phases.sqlite")
    else:
        plan["postgres"] = {"bin": str(task / "toolchain/postgres/install/bin"),
                            "data": str(out / "postgres-data"), "maxConnections": 100,
                            "maxClientConcurrency": 1, "cpus": "4-7"}
    row_cases = tuple(int(value) for value in args.rows.split(","))
    if not row_cases or any(value not in (1, 100, 1000) for value in row_cases):
        raise SystemExit("The unchanged ordinary phase consumer accepts only 1, 100 and 1000; exact32 uses the mixed text case or independent diagnostic consumer")
    for index, rows in enumerate(row_cases):
        kname, dname = f"korda-{rows}", f"dapper-{rows}"
        koutput, doutput = "{output}/" + kname + ".json", "{output}/" + dname + ".json"
        argv = [str(korda), "{connection}", koutput, str(args.iterations), str(args.windows)]
        if index == 0:
            argv.append("initialize")
        argv += ["--rows", str(rows)]
        plan["commands"].append({"name": kname, "phase": "same-query-phase-baseline",
                                 "argv": argv, "cpus": "0-3", "timeoutSeconds": 240})
        argv = [str(dapper), "--connection", "{connection}", "--output", doutput,
                "--korda-receipt", koutput, "--rows", str(rows),
                "--iterations", str(args.iterations), "--windows", str(args.windows)]
        if args.provider == "sqlite":
            argv += ["--native-library", str(sqlite)]
        plan["commands"].append({"name": dname, "phase": "same-query-phase-baseline",
                                 "argv": argv, "cpus": "0-3", "timeoutSeconds": 240})
    plan_path = out.with_suffix(".plan.json")
    with plan_path.open("x") as stream:
        json.dump(plan, stream, indent=2)
        stream.write("\n")
    if any(os.environ.get(key) for key in ("LD_PRELOAD", "DOTNET_ThreadPool_UnfairSemaphoreSpinLimit", "COMPlus_ThreadPool_UnfairSemaphoreSpinLimit")):
        raise SystemExit("Ordinary phase run must use default runtime and no inherited instrumentation")
    subprocess.run(["taskset", "-c", "8", "python3", str(runner), str(plan_path),
                    "--output", str(out), "--sample-seconds", "0.25"], check=True)


if __name__ == "__main__":
    main()
