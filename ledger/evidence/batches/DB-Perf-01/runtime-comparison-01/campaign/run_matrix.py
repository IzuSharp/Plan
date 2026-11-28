#!/usr/bin/env python3
"""Run the owner-authorized local matrix using the unchanged Korda observer.

Builds and diagnostics are deliberately absent. Each cell has a fresh fixture,
an independent database lifetime, immutable raw evidence and explicit admission.
"""
from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import threading
import time
from urllib.parse import urlparse


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def save(path, value):
    path = Path(path)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, indent=2) + "\n")
    tmp.replace(path)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_inputs(inputs):
    for item in inputs:
        actual = sha(item["path"])
        if actual != item["sha256"]:
            raise ValueError("Frozen input changed: " + item["path"])


def validate_matrix(matrix):
    expected = [(implementation, provider) for implementation in
                ("dapper", "ef-workstation", "ef-satori", "java-native")
                for provider in ("sqlite", "postgresql")]
    cells = matrix["cells"]
    if [(cell["implementation"], cell["provider"]) for cell in cells] != expected:
        raise ValueError("Expected the eight cells in the owner-requested order")
    if len(matrix["caseNames"]) != 35 or len(set(matrix["caseNames"])) != 35:
        raise ValueError("The matrix requires the 35 distinct original cases")
    for index, cell in enumerate(cells, 1):
        command, provider = cell["command"], cell["provider"]
        expected_name = f"{index:02d}-{cell['implementation']}-{provider}"
        if cell["name"] != expected_name or command["name"] != expected_name:
            raise ValueError("Cell names/order differ from the fixed matrix")
        if command["cpus"] != "0-3" or command["timeoutSeconds"] != 2115:
            raise ValueError("Client affinity or timeout differs from the restored plan")
        argv = command["argv"]
        concurrency, rate = (4, 3000) if provider == "sqlite" else (8, 3600)
        values = {"--case": "mixed", "--mode": "prepared", "--session": "persistent",
                  "--concurrency": str(concurrency), "--warmup": "64", "--rows": "32",
                  "--batch-rows": "32", "--tenants": "8", "--orders-per-tenant": "1024",
                  "--queue-capacity": "64", "--seconds": "1800", "--idle-seconds": "15",
                  "--rate": str(rate), "--output": "{output}/result.json", "--connection": "{connection}"}
        for key, expected_value in values.items():
            if argv.count(key) != 1 or argv.index(key) + 1 >= len(argv) or argv[argv.index(key) + 1] != expected_value:
                raise ValueError("Command does not match the restored plan: " + key)
        if argv.count("--verify") != 1 or any(value in argv for value in
                ("--empty-driver", "--allocation-profile", "--initialize", "--verify-only", "--allow-jit-diagnostic")):
            raise ValueError("Formal commands require correctness verification and no diagnostic mode")
        if cell["implementation"] != "java-native" and cell["environmentOverrides"].get("DOTNET_GCHeapHardLimit") != "0xC000000":
            raise ValueError("C# requested GC budget differs from the owner policy")
        if cell["implementation"] == "java-native" and argv.count("--formal-admission") != 1:
            raise ValueError("Java formal command lacks its executable-bound admission")


@contextlib.contextmanager
def environment(overrides):
    previous = {key: os.environ.get(key) for key in overrides}
    try:
        for key, value in overrides.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def heartbeat(stop, path, name, started):
    while not stop.wait(45):
        value = {"cell": name, "phase": "client_process_active",
                 "processElapsedSeconds": round(time.monotonic() - started, 1),
                 "scope": "Progress only; final monotonic boundaries determine offered duration."}
        try:
            with path.open("rb") as stream:
                stream.seek(0, 2)
                stream.seek(max(0, stream.tell() - 131072))
                lines = stream.read().splitlines()
            sample = json.loads(lines[-1])
            value.update(lastObservedUtc=sample["utc"],
                         client=sample["clientTotals"], server=sample["serverTotals"])
        except (OSError, ValueError, IndexError, KeyError):
            value["lastSampleAvailable"] = False
        print("PROGRESS " + json.dumps(value, separators=(",", ":")), flush=True)


def database_verify(fixture, provider, connection, sqlite_library, psql):
    db = fixture.Sqlite(sqlite_library, connection) if provider == "sqlite" else fixture.Postgres(psql, connection)
    try:
        return fixture.verify(db, provider, 13120)
    finally:
        db.close()


def pg_stats(psql, connection):
    sql = ("SELECT row_to_json(s) FROM (SELECT datid,datname,xact_commit,xact_rollback,"
           "blks_read,blks_hit,tup_returned,tup_fetched,tup_inserted,tup_updated,tup_deleted,"
           "conflicts,temp_files,temp_bytes,deadlocks,blk_read_time,blk_write_time,"
           "session_time,active_time,idle_in_transaction_time,sessions,sessions_abandoned,"
           "sessions_fatal,sessions_killed,stats_reset FROM pg_stat_database "
           "WHERE datname=current_database()) s")
    command = [str(psql), "--no-psqlrc", "--set", "ON_ERROR_STOP=1", "--dbname", connection, "-At", "-c", sql]
    return {"command": command, "scope": "Outside timed interval; includes fixture verification/warmup/idle as applicable.",
            "value": json.loads(subprocess.check_output(command, text=True, timeout=30))}


def evaluate(result, command, provider, implementation, case_names):
    offered = result.get("OfferedLoad")
    failures = []
    if not command.get("success"):
        failures.append("client_or_observer_failure")
    if result.get("Failed") != 0 or result.get("OracleFailures") != 0:
        failures.append("business_or_oracle_failure")
    if result.get("TimingComparisonEligible") is not True:
        failures.append("consumer_not_eligible")
    if result.get("ApplicationConnectionsReturnedToZero") is not True:
        failures.append("connections_not_returned")
    if not offered:
        failures.append("missing_offered_load_receipt")
    else:
        rate, concurrency = (3000, 4) if provider == "sqlite" else (3600, 8)
        required = {"RequestsPerSecond": rate, "OfferedSeconds": 1800,
                    "QueueCapacity": 64, "Planned": rate * 1800,
                    "Attempted": rate * 1800, "Failed": 0, "Retries": 0,
                    "OracleFailures": 0, "TimeSeriesTruncated": False}
        for key, value in required.items():
            if offered.get(key) != value:
                failures.append("offered_" + key)
        try:
            if not (offered["Attempted"] == offered["Sent"] + offered["Rejected"]
                    and offered["Sent"] == offered["Started"] == offered["Completed"]
                    and offered["Completed"] == offered["Succeeded"] + offered["Failed"]
                    and offered["Succeeded"] == result["Completed"] > 0):
                failures.append("operation_accounting")
            frequency = offered["TimerFrequency"]
            if frequency <= 0 or not (
                    abs((offered["DeadlineTicks"] - offered["StartedTicks"]) / frequency - 1800) < 0.000001
                    and offered["OfferedEndTicks"] >= offered["DeadlineTicks"]
                    and offered["DrainedTicks"] >= offered["OfferedEndTicks"]
                    and result["EffectiveSeconds"] >= 1800):
                failures.append("full_monotonic_interval")
            for field, count in (("SuccessServiceHistogram", "Succeeded"),
                                 ("SuccessScheduledHistogram", "Succeeded"),
                                 ("AllCompletedScheduledHistogram", "Completed"),
                                 ("StartDelayHistogram", "Started")):
                if sum(offered[field]) != offered[count]:
                    failures.append("histogram_" + field)
            for field in ("Planned", "Sent", "Started", "Succeeded", "Failed", "Rejected", "Rows"):
                if sum(item[field] for item in offered["Seconds"]) != offered[field]:
                    failures.append("per_second_" + field)
        except (KeyError, TypeError, ZeroDivisionError):
            failures.append("missing_or_invalid_offered_accounting")
        settings = {"Concurrency": concurrency, "WarmupPerWorker": 64, "RequestedRows": 32,
                    "BatchRows": 32, "Tenants": 8, "OrdersPerTenant": 1024,
                    "Mode": "prepared", "SessionMode": "persistent", "EmptyDriver": False}
        for key, value in settings.items():
            if result.get(key) != value:
                failures.append("consumer_" + key)
        if result.get("ActualCaseIds") != case_names:
            failures.append("case_order")
        idle = result.get("Idle") or {}
        if idle.get("RequestedSeconds") != 15 or idle.get("ObservedSeconds", 0) < 15:
            failures.append("released_idle")
    if result.get("TimeSeriesTruncated") is True:
        failures.append("time_series_truncated")
    return {"status": "passed" if not failures else "failed", "failures": failures,
            "provider": provider, "implementation": implementation,
            "memoryEnforcementClaimed": False,
            "scope": "Full offered duration, exact settings, planned/admitted/completed accounting, histogram populations, per-second totals and released idle checked; rejection remains a measured outcome."}


def run_cell(matrix, cell, output, observer, fixture):
    name = cell["name"]
    directory = output / name
    directory.mkdir(parents=True, exist_ok=False)
    verify_inputs(matrix["frozenInputs"])
    verify_inputs(cell["frozenInputs"])
    provider = cell["provider"]
    psql = Path(matrix["postgresBin"]) / "psql"
    plan = {"provider": provider, "commands": [cell["command"]]}
    if provider == "sqlite":
        database = directory / "fixture.sqlite"
        shutil.copyfile(matrix["sqliteSeed"], database)
        plan["connection"] = str(database)
    else:
        plan["postgres"] = {"bin": matrix["postgresBin"], "data": str(directory / "pgdata"),
                            "cpus": "4-7", "maxConnections": 64, "maxClientConcurrency": 8}
    save(directory / "plan.json", {"matrixSha256": matrix["_sha256"], "cell": cell, "database": plan,
                                   "environmentOverrides": cell["environmentOverrides"],
                                   "memoryPolicy": matrix["memoryPolicy"],
                                   "observerSha256": sha(matrix["observerPath"]),
                                   "orchestratorSha256": sha(__file__)})
    status = {"name": name, "status": "starting", "startedUtc": observer.utc(),
              "formalSecondsRequested": 1800, "result": str(directory / "result.json")}
    save(output / "current.json", status)
    print("START " + json.dumps(status), flush=True)
    result = None
    try:
        with observer.database(plan, directory) as (connection, server_pid):
            if provider == "postgresql":
                sql, _ = fixture.generate(provider)
                sql_path = directory / "fixture.sql"
                sql_path.write_text(sql)
                fixture.Postgres(psql, connection).initialize(sql_path)
            save(directory / "fixture-before.json", database_verify(fixture, provider, connection, matrix["sqliteLibrary"], psql))
            if provider == "postgresql":
                save(directory / "postgres-stats-before.json", pg_stats(psql, connection))
            client_connection = connection
            if cell["implementation"] == "java-native" and provider == "postgresql":
                uri = urlparse(connection)
                client_connection = f"jdbc:postgresql://{uri.hostname}:{uri.port}{uri.path}?user=korda&sslmode=disable"
            stop = threading.Event()
            pulse = threading.Thread(target=heartbeat, args=(stop, directory / (name + ".resources.jsonl"), name, time.monotonic()), daemon=True)
            pulse.start()
            try:
                with environment(cell["environmentOverrides"]):
                    command = observer.execute(cell["command"], client_connection, server_pid, directory, 0.25, check=False)
            finally:
                stop.set()
                pulse.join(timeout=2)
            result_path = directory / "result.json"
            if result_path.exists():
                result = json.loads(result_path.read_text())
                status.update(evaluate(result, command, provider, cell["implementation"], matrix["caseNames"]))
                status["resultSha256"] = sha(result_path)
            else:
                status.update(status="failed", failures=["missing_result"], exitCode=command.get("exitCode"))
            if provider == "postgresql":
                save(directory / "postgres-stats-after.json", pg_stats(psql, connection))
            save(directory / "fixture-after.json", database_verify(fixture, provider, connection, matrix["sqliteLibrary"], psql))
            status["allStoredRowsRestored"] = True
        verify_inputs(cell["frozenInputs"])
        verify_inputs(matrix["frozenInputs"])
    except BaseException as error:
        status.update(status="failed", error={"type": type(error).__name__, "message": str(error)})
        raise
    finally:
        status["finishedUtc"] = observer.utc()
        save(directory / "cell-status.json", status)
        save(output / "current.json", status)
        with (output / "events.jsonl").open("a") as stream:
            stream.write(json.dumps(status, separators=(",", ":")) + "\n")
        print("END " + json.dumps(status), flush=True)
    if status["status"] != "passed":
        raise RuntimeError(name + " failed; immutable partial evidence retained; no automatic retry")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--only")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    matrix = json.loads(args.matrix.read_text())
    matrix["_sha256"] = sha(args.matrix)
    if platform.machine() != "x86_64" or platform.system() != "Linux":
        raise ValueError("Local Linux x64 is required")
    if not set(range(9)) <= os.sched_getaffinity(0):
        raise ValueError("The restored CPU placement requires visible CPUs 0 through 8")
    policy = matrix["memoryPolicy"]
    if policy["cgroupRequired"] or policy["csharpRequestedGcHeapBytes"] != 201326592:
        raise ValueError("The matrix does not carry the latest owner memory policy")
    validate_matrix(matrix)
    if args.only and args.only not in {cell["name"] for cell in matrix["cells"]}:
        raise ValueError("Unknown --only cell")
    verify_inputs(matrix["frozenInputs"])
    for cell in matrix["cells"]:
        verify_inputs(cell["frozenInputs"])
    if args.validate_only:
        print(json.dumps({"matrixSha256": matrix["_sha256"], "allFrozenInputsMatched": True, "cellCount": len(matrix["cells"])}))
        return
    os.sched_setaffinity(0, {8})
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    with (output / "campaign.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        observer = load_module("korda_original_observer", matrix["observerPath"])
        fixture = load_module("restored_fixture", matrix["fixtureScript"])
        host = {"observedUtc": observer.utc(), "platform": platform.platform(),
             "hostName": platform.node(), "bootId": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
             "ticksPerSecond": os.sysconf("SC_CLK_TCK"), "observerAffinity": sorted(os.sched_getaffinity(0)),
             "cgroupObservation": observer.cgroup_snapshot(), "physicalHostExclusivityEstablished": False,
             "ownerMemoryPolicy": policy, "matrixSha256": matrix["_sha256"]}
        host_path = output / "host.json"
        if host_path.exists():
            previous = json.loads(host_path.read_text())
            if any(previous.get(key) != host[key] for key in ("bootId", "hostName", "matrixSha256", "ownerMemoryPolicy")):
                raise ValueError("Resume host, boot, matrix or owner policy changed; use a separately identified campaign")
        else:
            save(host_path, host)
        with (output / "invocations.jsonl").open("a") as stream:
            stream.write(json.dumps({"utc": observer.utc(), "only": args.only, "hostObservation": host}, separators=(",", ":")) + "\n")
        for cell in matrix["cells"]:
            if args.only and args.only != cell["name"]:
                continue
            run_cell(matrix, cell, output, observer, fixture)


if __name__ == "__main__":
    main()
