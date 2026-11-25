#!/usr/bin/env python3
"""Build and run locked direct-driver smoke probes, never a performance campaign."""

import argparse
from datetime import datetime, timezone
import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import time


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(part)
    return result.hexdigest()


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[3]
    parser.add_argument("--product-root", type=Path, default=root)
    parser.add_argument("--clang", type=Path, required=True, help="Locked clang++ executable")
    parser.add_argument("--llvm-root", type=Path, help="Defaults to clang's distribution root")
    parser.add_argument("--sqlite-source", type=Path, required=True, help="Locked amalgamation directory")
    parser.add_argument("--sqlite-archive", type=Path, required=True, help="Release libnw_sqlite_engine.a")
    parser.add_argument("--sqlite-build-dir", type=Path, required=True, help="Existing CMake directory with compile_commands.json")
    parser.add_argument("--postgres-prefix", type=Path, required=True, help="Source-built PostgreSQL install with korda-postgresql-build.json")
    parser.add_argument("--output", type=Path, required=True, help="A new attempt directory; must not exist")
    parser.add_argument("--port", type=int, default=0, help="Loopback port; zero selects an ephemeral port")
    parser.add_argument("--postgres-user", default=getpass.getuser(), help="Owner of the private local cluster")
    return parser.parse_args()


def main(args):
    product = args.product_root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    source_root = Path(__file__).resolve().parent
    clang = args.clang.resolve()
    llvm = args.llvm_root.resolve() if args.llvm_root else clang.parent.parent
    sqlite_source = args.sqlite_source.resolve()
    sqlite_archive = args.sqlite_archive.resolve()
    sqlite_build = args.sqlite_build_dir.resolve()
    postgres = args.postgres_prefix.resolve()
    state = {
        "task": "DB-Perf-01",
        "kind": "minimal_direct_native_real_database_probe",
        "performance_result": False,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "commands": [],
        "files": {},
        "results": [],
        "arguments": {key: str(value) if isinstance(value, Path) else value for key, value in vars(args).items()},
        "limitations": [
            "This is a smoke probe, not a workload campaign or throughput/latency result.",
            "PostgreSQL numeric is explicitly cast to text; final typed binary numeric decoding equivalence remains pending.",
            "SQLite counters cover SQLite allocations only; process-wide native allocations are not measured.",
            "The existing SQLite archive is reused. Recorded build metadata and runtime checks are not an independent rebuild proof.",
        ],
    }

    def save():
        (output / "manifest.json").write_text(json.dumps(state, indent=2) + "\n")

    def record(path, expected=None):
        path = Path(path)
        actual = digest(path)
        if expected is not None and actual != expected:
            raise RuntimeError("File hash differs: " + str(path))
        state["files"][str(path)] = {
            "sha256": actual,
            "size": path.stat().st_size,
            "expected_hash_verified": expected is not None,
        }
        return actual

    def run(label, command, timeout=60):
        logfile = output / (f"{len(state['commands']) + 1:02d}-" + label + ".log")
        entry = {
            "label": label,
            "argv": [str(value) for value in command],
            "cwd": str(output),
            "started_utc": datetime.now(timezone.utc).isoformat(),
            "log": logfile.name,
        }
        state["commands"].append(entry)
        save()
        started = time.monotonic()
        try:
            with logfile.open("w") as stream:
                result = subprocess.run(command, cwd=output, stdout=stream, stderr=subprocess.STDOUT, timeout=timeout, check=False)
            entry["exit_code"] = result.returncode
        except Exception as error:
            entry["execution_error"] = repr(error)
            raise
        finally:
            entry["elapsed_seconds"] = time.monotonic() - started
            if logfile.exists():
                entry["log_sha256"] = digest(logfile)
            save()
        if result.returncode:
            raise RuntimeError("Command failed: " + label + "; inspect " + str(logfile))
        return logfile.read_text()

    server = None
    server_log = None
    try:
        if os.name != "posix":
            raise RuntimeError("This probe requires Linux x64")
        if not 0 <= args.port <= 65535:
            raise ValueError("Port must be zero or a valid TCP port")
        lockfile = product / "native/dependencies.lock.json"
        lock = json.loads(lockfile.read_text())
        record(lockfile)
        record(clang, lock["toolchain"]["llvm"]["executables"]["clang++"])
        for name in ["native_probe.cpp", "run_probe.py", "README.md"]:
            original = source_root / name
            record(original)
            shutil.copy2(original, output / name)
            record(output / name)
        baseline = subprocess.run(["git", "-C", str(product), "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        state["product_commit"] = baseline.stdout.strip()

        sqlite_lock = next(item for item in lock["dependencies"] if item["name"] == "sqlite")
        for name, expected in sqlite_lock["sourceFiles"].items():
            record(sqlite_source / name, expected)
        record(sqlite_archive)
        commands_file = sqlite_build / "compile_commands.json"
        record(commands_file)
        entries = [entry for entry in json.loads(commands_file.read_text()) if Path(entry["file"]).name == "sqlite3.c"]
        if len(entries) != 1:
            raise RuntimeError("Expected one SQLite amalgamation build command")
        record(entries[0]["file"], sqlite_lock["sourceFiles"]["sqlite3.c"])
        state["sqlite_archive_provenance"] = {
            "path": str(sqlite_archive),
            "sha256": digest(sqlite_archive),
            "existing_build_command": entries[0],
            "existing_compile_commands_sha256": digest(commands_file),
            "independently_rebuilt_by_this_probe": False,
        }

        receipt_path = postgres / "korda-postgresql-build.json"
        record(receipt_path)
        built = json.loads(receipt_path.read_text())
        postgres_lock = next(item for item in lock["dependencies"] if item["name"] == "libpq")
        if built["version"] != postgres_lock["version"] or built["compilerSha256"] != digest(clang):
            raise RuntimeError("PostgreSQL compiler/version provenance differs")
        if built["archiveSha256"] != postgres_lock["archiveSha256"] or built["patchSha256"] != postgres_lock["patches"][0]["sha256"]:
            raise RuntimeError("PostgreSQL source/patch provenance differs")
        record(product / postgres_lock["patches"][0]["path"], postgres_lock["patches"][0]["sha256"])
        for relative in ["lib/libpq.a", "lib/libpgcommon_shlib.a", "lib/libpgport_shlib.a", "include/libpq-fe.h", "bin/postgres", "bin/initdb", "bin/pg_ctl", "bin/pg_isready"]:
            record(postgres / relative, built["files"]["install/" + relative])
        runtime = llvm / "lib/x86_64-unknown-linux-gnu"
        for name in ["libc++.a", "libc++abi.a"]:
            record(runtime / name)
        state["dependency_versions"] = {
            "clang": lock["toolchain"]["llvm"]["version"],
            "libcxx": lock["runtime"]["version"],
            "sqlite": sqlite_lock["version"],
            "libpq": postgres_lock["version"],
            "postgresql_server": built["version"],
        }
        save()
        run("compiler-version", [str(clang), "--version"])
        run("postgres-version", [str(postgres / "bin/postgres"), "--version"])
        run("host", ["uname", "-a"])
        # The driver source explicitly checks these selected runtime versions.
        if sqlite_lock["version"] != "3.51.3" or postgres_lock["version"] != "18.0":
            raise RuntimeError("The selected runtime versions changed; review the probe expectations")
        common = [str(clang), "-std=c++20", "-O3", "-DNDEBUG", "-fno-omit-frame-pointer", "-Wall", "-Wextra", "-Werror", "-stdlib=libc++", "-nostdlib++", str(output / "native_probe.cpp")]
        standard = [str(runtime / "libc++.a"), str(runtime / "libc++abi.a"), "-lpthread", "-ldl", "-lm"]
        sqlite_exe = output / "native-sqlite"
        postgres_exe = output / "native-postgresql"
        run("compile-sqlite", common + ["-DPROBE_POSTGRES=0", "-I" + str(sqlite_source), str(sqlite_archive)] + standard + ["-o", str(sqlite_exe)])
        run("compile-postgresql", common + ["-DPROBE_POSTGRES=1", "-I" + str(postgres / "include"), str(postgres / "lib/libpq.a"), str(postgres / "lib/libpgcommon_shlib.a"), str(postgres / "lib/libpgport_shlib.a"), "-lssl", "-lcrypto", "-lz"] + standard + ["-o", str(postgres_exe)])
        for provider, executable in [("sqlite", sqlite_exe), ("postgresql", postgres_exe)]:
            record(executable)
            linked = run("ldd-" + provider, ["ldd", str(executable)])
            for filename in re.findall(r"(?:=>\s+|^\s*)(/[^\s()]+)", linked, flags=re.MULTILINE):
                if Path(filename).is_file():
                    record(filename)
            run("elf-dynamic-" + provider, ["readelf", "-d", str(executable)])

        sqlite_output = run("execute-sqlite", [str(sqlite_exe), str(output / "probe.sqlite")])
        state["results"].extend(json.loads(line.removeprefix("NATIVE_PROBE_RESULT ")) for line in sqlite_output.splitlines() if line.startswith("NATIVE_PROBE_RESULT "))
        header = (sqlite_source / "sqlite3.h").read_text()
        expected_id = re.search(r'^#define SQLITE_SOURCE_ID\s+"(.*)"', header, re.MULTILINE).group(1)
        actual_id = re.search(r"^sqlite_source_id=(.*)", sqlite_output, re.MULTILINE).group(1)
        if expected_id != actual_id:
            raise RuntimeError("SQLite runtime source ID differs from locked header")
        options = set(re.findall(r"^sqlite_compile_option=(.*)", sqlite_output, re.MULTILINE))
        required = {"DEFAULT_FOREIGN_KEYS", "ENABLE_API_ARMOR", "ENABLE_COLUMN_METADATA", "ENABLE_DBSTAT_VTAB", "ENABLE_FTS3", "ENABLE_FTS3_PARENTHESIS", "ENABLE_FTS5", "ENABLE_MEMORY_MANAGEMENT", "ENABLE_RTREE", "ENABLE_STAT4", "SOUNDEX", "THREADSAFE=1", "USE_URI", "ENABLE_UNLOCK_NOTIFY"}
        missing = [option for option in sorted(required) if option not in options and option + "=1" not in options]
        if missing:
            raise RuntimeError("SQLite production options missing: " + repr(missing))
        state["sqlite_runtime_verification"] = {"source_id": actual_id, "locked_header_source_id_matches": True, "required_options": sorted(required), "reported_options": sorted(options)}
        save()

        data = output / "postgres-data"
        run("postgres-initdb", [str(postgres / "bin/initdb"), "-D", str(data), "--no-locale", "-E", "UTF8", "--auth=trust", "--username=" + args.postgres_user])
        port = args.port
        if not port:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as reservation:
                reservation.bind(("127.0.0.1", 0))
                port = reservation.getsockname()[1]
        state["postgres_endpoint"] = {"host": "127.0.0.1", "port": port, "unix_socket_directories": "", "temporary_isolated_cluster": str(data)}
        command = [str(postgres / "bin/postgres"), "-D", str(data), "-h", "127.0.0.1", "-k", "", "-p", str(port)]
        state["postgres_server_argv"] = command
        server_log = (output / "postgres-server.log").open("w")
        server = subprocess.Popen(command, cwd=output, stdout=server_log, stderr=subprocess.STDOUT)
        ready = False
        for attempt in range(100):
            if server.poll() is not None:
                break
            result = subprocess.run([str(postgres / "bin/pg_isready"), "-h", "127.0.0.1", "-p", str(port), "-d", "postgres", "-U", args.postgres_user], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
            if result.returncode == 0:
                ready = True
                break
            time.sleep(0.05)
        if not ready:
            raise RuntimeError("Temporary PostgreSQL did not become ready; inspect postgres-server.log")
        # libpq quoting is required even for an explicitly supplied local account name.
        username = args.postgres_user.replace("\\", "\\\\").replace("'", "\\'")
        connection = f"host=127.0.0.1 port={port} dbname=postgres user='{username}' sslmode=disable connect_timeout=5"
        postgres_output = run("execute-postgresql", [str(postgres_exe), connection])
        state["results"].extend(json.loads(line.removeprefix("NATIVE_PROBE_RESULT ")) for line in postgres_output.splitlines() if line.startswith("NATIVE_PROBE_RESULT "))
        if len(state["results"]) != 2 or any(result["status"] != "passed" for result in state["results"]):
            raise RuntimeError("Incomplete direct native probe results")
        state["status"] = "passed"
    except Exception as error:
        state["status"] = "failed"
        state["error"] = repr(error)
        print("PROBE_FAILURE", error, flush=True)
    finally:
        if server is not None and server.poll() is None:
            try:
                run("postgres-stop", [str(postgres / "bin/pg_ctl"), "-D", str(output / "postgres-data"), "-m", "fast", "-w", "stop"], timeout=30)
                server.wait(timeout=10)
            except Exception as error:
                state["cleanup_error"] = repr(error)
                state["status"] = "failed"
                server.terminate()
                try:
                    server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait(timeout=5)
        if server_log is not None:
            server_log.close()
            record(output / "postgres-server.log")
        state["postgres_process_exited"] = server is None or server.poll() is not None
        state["ended_utc"] = datetime.now(timezone.utc).isoformat()
        save()
        print(json.dumps({"status": state["status"], "manifest": str(output / "manifest.json"), "results": state["results"]}), flush=True)
    return 0 if state["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main(arguments()))
