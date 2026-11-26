#!/usr/bin/env python3
"""Local capability and prerequisite evidence; never a product benchmark."""
import collections
import ctypes
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time

ROOT = Path(__file__).resolve().parent
TASK = ROOT.parent


def run(argv, cwd=None, timeout=30):
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    begin = time.monotonic_ns()
    try:
        result = subprocess.run(argv, cwd=cwd, text=True, capture_output=True, timeout=timeout)
        value = {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}
    except FileNotFoundError as exc:
        value = {"exit_code": 127, "stdout": "", "stderr": str(exc), "not_started": True}
    except subprocess.TimeoutExpired as exc:
        value = {"exit_code": None, "timeout": True, "stdout": str(exc.stdout or ""), "stderr": str(exc.stderr or "")}
    return {"argv": argv, "cwd": str(cwd or ROOT), "started_utc": started,
            "elapsed_ns": time.monotonic_ns() - begin, **value}


def read(path):
    try:
        return {"value": Path(path).read_text().strip()}
    except OSError as exc:
        return {"errno": exc.errno, "error": str(exc)}


def main():
    names = ["dotnet", "perf", "cmake", "ninja", "clang", "clang++", "psql", "postgres",
             "pg_ctl", "initdb", "sqlite3", "go", "gcc", "g++", "objdump", "readelf", "addr2line"]
    inventory = {
        "task": "DB-Exec-Parity-01", "scope": "environment capabilities, not database performance",
        "captured_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "uname": list(platform.uname()), "uid": os.getuid(), "cpu_affinity": sorted(os.sched_getaffinity(0)),
        "executables": {name: shutil.which(name) for name in names},
        "controls": {path: read(path) for path in ["/proc/sys/kernel/perf_event_paranoid",
                     "/proc/sys/kernel/kptr_restrict", "/sys/fs/cgroup/cpu.max", "/sys/fs/cgroup/memory.max",
                     "/sys/kernel/tracing/events/sched/sched_switch/id"]},
        "repositories": {}, "system_libraries_not_locked_inputs": {},
    }
    for name in ["Korda", "Korda-Design", "Plan"]:
        repo = TASK / "worktrees" / name
        inventory["repositories"][name] = {"head": run(["git", "rev-parse", "HEAD"], repo),
                                            "tree": run(["git", "rev-parse", "HEAD^{tree}"], repo),
                                            "status": run(["git", "status", "--porcelain"], repo)}
    for name, function, returns_string in [("libsqlite3.so.0", "sqlite3_libversion", True),
                                            ("libpq.so.5", "PQlibVersion", False)]:
        try:
            library = ctypes.CDLL(name)
            fn = getattr(library, function)
            fn.restype = ctypes.c_char_p if returns_string else ctypes.c_int
            value = fn()
            inventory["system_libraries_not_locked_inputs"][name] = value.decode() if returns_string else value
        except Exception as exc:
            inventory["system_libraries_not_locked_inputs"][name] = {"error": str(exc)}
    inventory["tool_versions"] = [run(argv) for argv in [["gcc", "--version"], ["objdump", "--version"],
                                                          ["dotnet", "--info"], ["cmake", "--version"],
                                                          ["psql", "--version"]]]
    (ROOT / "environment.json").write_text(json.dumps(inventory, indent=2) + "\n")
    network = []
    for label, url in [
        ("locked-dotnet-sdk", "https://builds.dotnet.microsoft.com/dotnet/Sdk/11.0.100/dotnet-sdk-11.0.100-linux-x64.tar.gz"),
        ("nuget-service-index", "https://api.nuget.org/v3/index.json"),
    ]:
        result = run(["curl", "-sSI", "--connect-timeout", "15", "--max-time", "20", url], timeout=25)
        network.append({"label": label, **result})
    (ROOT / "dependency-fetch-attempts.json").write_text(json.dumps(network, indent=2) + "\n")
    for stem, executable in [("self-probe", "self_probe"), ("self-probe-sched", "self_probe_sched")]:
        rows = [json.loads(line) for line in (ROOT / (stem + ".jsonl")).read_text().splitlines()]
        summary = {"scope": "self-process native capability probe only; not database profiling",
                   "records": [r for r in rows if r["kind"] not in ["signal_sample", "perf_sample"]],
                   "resolved_sample_ips": {}}
        for kind in ["perf_sample", "signal_sample"]:
            counts = collections.Counter(row["ip"] for row in rows if row["kind"] == kind)
            summary["resolved_sample_ips"][kind] = [
                {"ip": ip, "samples": count,
                 "resolution": run(["addr2line", "-e", str(ROOT / executable), "-f", "-C", "-i", ip])}
                for ip, count in counts.most_common(12)]
        (ROOT / (stem + "-summary.json")).write_text(json.dumps(summary, indent=2) + "\n")
    manifest = {p.name: {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                for p in sorted(ROOT.iterdir()) if p.is_file() and p.name != "sha256-manifest.json"}
    (ROOT / "sha256-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"tools": inventory["executables"],
                      "system_libraries_not_locked_inputs": inventory["system_libraries_not_locked_inputs"],
                      "network": [{"label": n["label"], "exit_code": n["exit_code"], "stderr": n["stderr"]} for n in network],
                      "manifest_files": len(manifest)}, indent=2))


if __name__ == "__main__":
    main()
