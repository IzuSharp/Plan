#!/usr/bin/env python3
"""Finite local PostgreSQL18 fixture setup and correctness checks; no load test."""
from pathlib import Path
import hashlib
import json
import os
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
BIN = ROOT / "postgres/bin"
DATA = ROOT / "fixtures/pgdata"
RECEIPT = ROOT / "fixtures/postgresql-setup-receipt.json"

def main():
    if DATA.exists() or RECEIPT.exists():
        raise SystemExit("Preserve previous fixture and receipt; this setup runs once.")
    DATA.parent.mkdir(parents=True, exist_ok=True)
    record = {"schemaVersion": 1, "isPressureTest": False, "startedUnixSeconds": time.time(), "uid": os.getuid(), "commands": [], "data": str(DATA), "databaseLimitedTo128MB": False, "historicalSharedBuffers": "128MB"}
    started = False
    def run(label, command, timeout=120):
        row = {"label": label, "command": [str(x) for x in command], "startedUnixSeconds": time.time()}
        result = subprocess.run(row["command"], capture_output=True, text=True, timeout=timeout)
        row.update(exitCode=result.returncode, finishedUnixSeconds=time.time())
        (ROOT / "fixtures" / (label + ".stdout.log")).write_text(result.stdout)
        (ROOT / "fixtures" / (label + ".stderr.log")).write_text(result.stderr)
        record["commands"].append(row)
        if result.returncode:
            raise RuntimeError(label + ": " + result.stderr[-2000:] + result.stdout[-2000:])
        return result.stdout
    try:
        run("postgres-initdb", [BIN / "initdb", "-D", DATA, "-U", "korda", "-A", "trust", "--no-locale", "--encoding=UTF8"])
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        options = f"-h 127.0.0.1 -p {port} -c unix_socket_directories= -c max_connections=64 -c fsync=on -c synchronous_commit=on -c full_page_writes=on -c timezone=UTC -c shared_buffers=128MB -c default_transaction_isolation='read committed'"
        start = ["taskset", "-c", "4-7", str(BIN / "pg_ctl"), "-D", str(DATA), "-l", str(ROOT / "fixtures/postgres.log"), "-o", options, "-w", "-t", "30", "start"]
        record["startCommand"] = start
        run("postgres-start", start, timeout=40)
        started = True
        pid = int((DATA / "postmaster.pid").read_text().splitlines()[0])
        record["postmasterPid"] = pid
        record["serverCpuAffinity"] = sorted(os.sched_getaffinity(pid))
        assert record["serverCpuAffinity"] == [4, 5, 6, 7]
        admin = f"postgresql://korda@127.0.0.1:{port}/postgres"
        connection = f"postgresql://korda@127.0.0.1:{port}/db_perf_01"
        record["connection"] = connection
        run("postgres-createdb", [BIN / "psql", "--no-psqlrc", "--set", "ON_ERROR_STOP=1", "--dbname", admin, "--command", "CREATE DATABASE db_perf_01"])
        run("postgres-seed", [sys.executable, ROOT / "fixture.py", "--provider", "postgresql", "--sql-output", ROOT / "fixtures/postgresql.sql", "--receipt", ROOT / "fixtures/postgresql-seed-receipt.json", "--psql", BIN / "psql", "--connection", connection])
        settings_sql = "SELECT json_build_object('server_version',current_setting('server_version'),'server_encoding',current_setting('server_encoding'),'client_encoding',current_setting('client_encoding'),'fsync',current_setting('fsync'),'synchronous_commit',current_setting('synchronous_commit'),'full_page_writes',current_setting('full_page_writes'),'timezone',current_setting('timezone'),'shared_buffers',current_setting('shared_buffers'),'default_transaction_isolation',current_setting('default_transaction_isolation'),'max_connections',current_setting('max_connections'),'jit',current_setting('jit'),'plan_cache_mode',current_setting('plan_cache_mode'),'collation',(SELECT datcollate FROM pg_database WHERE datname=current_database()),'ctype',(SELECT datctype FROM pg_database WHERE datname=current_database()));"
        output = run("postgres-settings", [BIN / "psql", "--no-psqlrc", "--set", "ON_ERROR_STOP=1", "--tuples-only", "--no-align", "--dbname", connection, "--command", settings_sql])
        settings = json.loads(output)
        expected = {"server_version": "18.0", "server_encoding": "UTF8", "client_encoding": "UTF8", "fsync": "on", "synchronous_commit": "on", "full_page_writes": "on", "timezone": "UTC", "shared_buffers": "128MB", "default_transaction_isolation": "read committed", "max_connections": "64"}
        assert all(settings[k] == v for k, v in expected.items()), settings
        record["settings"] = settings
        sqlite = json.loads((ROOT / "fixtures/sqlite-schema-verified.json").read_text())
        pg = json.loads((ROOT / "fixtures/postgresql-seed-receipt.json").read_text())
        assert pg["verification"]["normalizedOrdersSha256"] == sqlite["normalizedOrdersSha256"]
        record["crossDatabaseNormalizedOrdersMatched"] = True
        record["status"] = "verified"
    except Exception as error:
        record["status"] = "failed"
        record["error"] = {"type": type(error).__name__, "message": str(error)}
        raise
    finally:
        if started:
            try:
                run("postgres-stop", [BIN / "pg_ctl", "-D", DATA, "-m", "fast", "-w", "-t", "30", "stop"], timeout=40)
                record["serverStopped"] = not (DATA / "postmaster.pid").exists()
            except Exception as error:
                record["serverStopped"] = False
                record["stopError"] = str(error)
                record["status"] = "failed"
        record["finishedUnixSeconds"] = time.time()
        record["scriptSha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        RECEIPT.write_text(json.dumps(record, indent=2) + "\n")
        print(json.dumps(record, indent=2))

if __name__ == "__main__":
    main()
