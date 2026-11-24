#!/usr/bin/env python3
"""Compile and execute direct-driver connectivity/correctness probes; never a benchmark."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import socket
import subprocess
import time

ROOT = Path(__file__).resolve().parent
PRODUCT = ROOT.parent / "Korda-DB-Perf-01-linux"
OLD = Path("/workspace/scratch/82a414196324/Korda-DB-Rename-01-linux")
ART = OLD / "artifacts"
LLVM = ART / "toolchain/llvm-23.1.5"
PG = ART / "postgres-tools/install"
SQLITE = ART / "dependencies/sqlite/sqlite-amalgamation-3510300"
SQLITE_ARCHIVE = ART / "cmake/linux-x64-release/libnw_sqlite_engine.a"
LOCK = json.loads((PRODUCT / "native/dependencies.lock.json").read_text())
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
OUT = ROOT / ("attempt-" + STAMP)
OUT.mkdir()
STATE = {"task": "DB-Perf-01", "kind": "minimal_direct_native_real_database_probe", "performance_result": False,
         "product_baseline": "771bc77cbd68d3f932b99ed2497c0697bbba5f02", "started_utc": STAMP,
         "status": "running", "commands": [], "files": {}, "results": [],
         "limitations": ["Not a workload campaign or throughput/latency result.",
                         "PostgreSQL numeric is explicitly cast to text for this minimal correctness probe; final numeric decoding equivalence is pending.",
                         "Native allocations are not measured globally. SQLite memory counters cover SQLite only."]}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def save():
    (OUT / "manifest.json").write_text(json.dumps(STATE, indent=2) + "\n")


def record(path, expected=None):
    path = Path(path)
    value = sha(path)
    if expected is not None and value != expected:
        raise RuntimeError("Hash differs: " + str(path))
    STATE["files"][str(path)] = {"sha256": value, "size": path.stat().st_size, "expected_hash_verified": expected is not None}
    return value


def run(label, command, *, timeout=60, required=True):
    path = OUT / (f"{len(STATE['commands']) + 1:02d}-" + label + ".log")
    started = datetime.now(timezone.utc).isoformat()
    begin = time.monotonic()
    entry = {"label": label, "argv": [str(a) for a in command], "cwd": str(OUT), "started_utc": started, "log": path.name}
    STATE["commands"].append(entry)
    save()
    try:
        with path.open("w") as stream:
            completed = subprocess.run(command, cwd=OUT, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout, check=False)
        entry["exit_code"] = completed.returncode
    except Exception as error:
        entry["execution_error"] = repr(error)
        raise
    finally:
        entry["elapsed_seconds"] = time.monotonic() - begin
        if path.exists(): entry["log_sha256"] = sha(path)
        save()
    if required and completed.returncode:
        raise RuntimeError("Command failed: " + label + "; inspect " + str(path))
    return path.read_text()


pg_process = None
pg_log = None
try:
    source = ROOT / "native_probe.cpp"
    record(source)
    record(Path(__file__))
    record(PRODUCT / "native/dependencies.lock.json")
    compiler = LLVM / "bin/clang++"
    record(compiler, LOCK["toolchain"]["llvm"]["executables"]["clang++"])
    sqlite_lock = next(d for d in LOCK["dependencies"] if d["name"] == "sqlite")
    for name, digest in sqlite_lock["sourceFiles"].items():
        record(SQLITE / name, digest)
    record(SQLITE_ARCHIVE)
    pg_receipt = PG / "korda-postgresql-build.json"
    record(pg_receipt)
    built = json.loads(pg_receipt.read_text())
    if built["version"] != "18.0" or built["compilerSha256"] != sha(compiler):
        raise RuntimeError("PostgreSQL build provenance differs")
    pg_lock = next(d for d in LOCK["dependencies"] if d["name"] == "libpq")
    if built["archiveSha256"] != pg_lock["archiveSha256"] or built["patchSha256"] != pg_lock["patches"][0]["sha256"]:
        raise RuntimeError("PostgreSQL dependency input provenance differs")
    record(PRODUCT / pg_lock["patches"][0]["path"], pg_lock["patches"][0]["sha256"])
    for item in ["lib/libpq.a", "lib/libpgcommon_shlib.a", "lib/libpgport_shlib.a", "include/libpq-fe.h", "bin/postgres", "bin/initdb", "bin/pg_ctl", "bin/pg_isready"]:
        record(PG / item, built["files"]["install/" + item])
    runtime = LLVM / "lib/x86_64-unknown-linux-gnu"
    for name in ["libc++.a", "libc++abi.a"]: record(runtime / name)
    STATE["dependency_versions"] = {"clang": "23.1.5", "sqlite": "3.51.3", "libpq": "18.0", "postgresql_server": "18.0", "libcxx": "23.1.5"}
    STATE["sqlite_archive_provenance"] = {"path": str(SQLITE_ARCHIVE), "reused_existing_release_archive": True,
        "source_files_verified_against_lock": True, "runtime_version_and_compile_options_checked_in_probe": True,
        "archive_is_not_rebuilt_by_this_probe": True}
    save()
    run("compiler-version", [str(compiler), "--version"])
    run("postgres-version", [str(PG / "bin/postgres"), "--version"])
    run("host", ["uname", "-a"])
    common = [str(compiler), "-std=c++20", "-O3", "-DNDEBUG", "-fno-omit-frame-pointer", "-Wall", "-Wextra", "-Werror",
              "-stdlib=libc++", "-nostdlib++", str(source)]
    stdlibs = [str(runtime / "libc++.a"), str(runtime / "libc++abi.a"), "-lpthread", "-ldl", "-lm"]
    sqlite_exe, pg_exe = OUT / "native-sqlite", OUT / "native-postgresql"
    run("compile-sqlite", common + ["-DPROBE_POSTGRES=0", "-I" + str(SQLITE), str(SQLITE_ARCHIVE)] + stdlibs + ["-o", str(sqlite_exe)])
    run("compile-postgresql", common + ["-DPROBE_POSTGRES=1", "-I" + str(PG / "include"), str(PG / "lib/libpq.a"),
        str(PG / "lib/libpgcommon_shlib.a"), str(PG / "lib/libpgport_shlib.a"), "-lssl", "-lcrypto", "-lz"] + stdlibs + ["-o", str(pg_exe)])
    for label, executable in [("sqlite", sqlite_exe), ("postgresql", pg_exe)]:
        record(executable)
        linked = run("ldd-" + label, ["ldd", str(executable)])
        for path in re.findall(r"(?:=>\s+|^\s*)(/[^\s()]+)", linked, flags=re.MULTILINE):
            if Path(path).is_file(): record(path)
        run("elf-dynamic-" + label, ["readelf", "-d", str(executable)])
    sqlite_output = run("execute-sqlite", [str(sqlite_exe), str(OUT / "probe.sqlite")])
    STATE["results"].extend(json.loads(line.removeprefix("NATIVE_PROBE_RESULT ")) for line in sqlite_output.splitlines() if line.startswith("NATIVE_PROBE_RESULT "))
    pgdata = OUT / "postgres-data"
    run("postgres-initdb", [str(PG / "bin/initdb"), "-D", str(pgdata), "--no-locale", "-E", "UTF8", "--auth=trust"])
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    STATE["postgres_endpoint"] = {"host": "127.0.0.1", "port": port, "unix_socket_directories": "", "temporary_isolated_cluster": str(pgdata)}
    command = [str(PG / "bin/postgres"), "-D", str(pgdata), "-h", "127.0.0.1", "-k", "", "-p", str(port)]
    STATE["postgres_server_argv"] = command
    pg_log = (OUT / "postgres-server.log").open("w")
    pg_process = subprocess.Popen(command, cwd=OUT, stdout=pg_log, stderr=subprocess.STDOUT)
    ready = False
    for attempt in range(100):
        if pg_process.poll() is not None: break
        result = subprocess.run([str(PG / "bin/pg_isready"), "-h", "127.0.0.1", "-p", str(port), "-d", "postgres"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
        if result.returncode == 0:
            ready = True
            break
        time.sleep(0.05)
    if not ready: raise RuntimeError("Temporary PostgreSQL did not become ready; inspect postgres-server.log")
    output = run("execute-postgresql", [str(pg_exe), f"host=127.0.0.1 port={port} dbname=postgres user=agent sslmode=disable connect_timeout=5"])
    STATE["results"].extend(json.loads(line.removeprefix("NATIVE_PROBE_RESULT ")) for line in output.splitlines() if line.startswith("NATIVE_PROBE_RESULT "))
    if len(STATE["results"]) != 2 or any(r["status"] != "passed" for r in STATE["results"]):
        raise RuntimeError("Incomplete native probe receipts")
    STATE["status"] = "passed"
except Exception as error:
    STATE["status"] = "failed"
    STATE["error"] = repr(error)
    print("PROBE_FAILURE", error, flush=True)
finally:
    if pg_process is not None and pg_process.poll() is None:
        try:
            run("postgres-stop", [str(PG / "bin/pg_ctl"), "-D", str(OUT / "postgres-data"), "-m", "fast", "-w", "stop"], timeout=30)
            pg_process.wait(timeout=10)
        except Exception as error:
            STATE["cleanup_error"] = repr(error)
            STATE["status"] = "failed"
            pg_process.terminate()
            try: pg_process.wait(timeout=10)
            except subprocess.TimeoutExpired: pg_process.kill(); pg_process.wait(timeout=5)
    if pg_log is not None:
        pg_log.close()
        record(OUT / "postgres-server.log")
    STATE["postgres_process_exited"] = pg_process is None or pg_process.poll() is not None
    STATE["ended_utc"] = datetime.now(timezone.utc).isoformat()
    save()
    (ROOT / "latest-attempt.txt").write_text(str(OUT) + "\n")
    print(json.dumps({"status": STATE["status"], "manifest": str(OUT / "manifest.json"), "results": STATE["results"]}), flush=True)

raise SystemExit(0 if STATE["status"] == "passed" else 1)
