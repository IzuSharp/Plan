"""Opt-in GC observations for two exact frozen Perf-01 Python entry points.

This file is discovered through a diagnostic-only PYTHONPATH. It does not alter
GC policy, timing functions, schedulers, business code, or signal handlers.
"""
import os
import sys


def _install():
    config_path = os.environ.get("NW_PERF01_GC_CONFIG")
    if not config_path or not sys.argv:
        return
    # Other Python children, including the outer DB controller, remain untouched.
    entry = os.path.realpath(sys.argv[0])
    if not (entry.endswith("/src/Benchmarks.Domain/cell_worker.py") or
            entry.endswith("/tests/Perf01.Database/target.py")):
        return

    import gc
    import hashlib
    import json
    import time
    import _thread

    with open(config_path, "rb") as stream:
        config_bytes = stream.read(65537)
    if len(config_bytes) > 65536:
        raise ValueError("Oversized diagnostic configuration")
    config = json.loads(config_bytes)
    roles = [role for role in config["roles"] if role["entry"] == entry]
    if not roles:
        return
    role = roles[0]
    config_sha = hashlib.sha256(config_bytes).hexdigest()
    pid = os.getpid()

    def digest(path):
        with open(path, "rb") as stream:
            return hashlib.file_digest(stream, "sha256").hexdigest()

    def failure(message):
        path = os.path.join(config["log_directory"], f"attachment-error-{pid}.json")
        with open(path, "x", encoding="utf-8") as stream:
            json.dump({"formal_timing_eligible": False, "pid": pid,
                       "role": role["role"], "error": message,
                       "configuration_sha256": config_sha}, stream)

    descriptor = None
    try:
        if sys.argv != role["argv"]:
            raise ValueError("Exact diagnostic entry-point argv differs")
        if sys.version_info[:3] != (3, 12, 14):
            raise ValueError("Diagnostic requires the frozen Python 3.12.14")
        if os.path.realpath(sys.executable) != config["python_realpath"]:
            raise ValueError("Diagnostic interpreter differs")
        if sorted(os.sched_getaffinity(0)) != [0, 1]:
            raise ValueError("Python generator role is outside frozen CPUs0,1")
        if digest(entry) != role["entry_sha256"]:
            raise ValueError("Frozen Python entry-point bytes differ")
        if digest(config["a21_path"]) != config["a21_sha256"]:
            raise ValueError("Frozen A21 source differs")
        if digest(__file__) != config["hook_sha256"]:
            raise ValueError("Diagnostic hook bytes differ")
        with open(config["plan_path"], "rb") as stream:
            plan_bytes = stream.read(131073)
        if len(plan_bytes) > 131072:
            raise ValueError("Unexpected diagnostic plan size")
        plan = json.loads(plan_bytes)
        if (plan["timing"]["requests"] != 259526 or
                plan["timing"]["period_ns"] != 6944444 or
                plan["timing"]["max_dispatch_lag_ns"] != 100000000 or
                plan["settings"]["features"]["concurrency"] != 16 or
                not plan["settings"]["features"]["compact_observation"]):
            raise ValueError("Full original PostgreSQL144/C16 plan was not retained")
        with open("/proc/self/stat", encoding="utf-8") as stream:
            fields = stream.read().rsplit(")", 1)[1].split()
        start_ticks, ppid = int(fields[19]), int(fields[1])
        path = os.path.join(config["log_directory"],
                            f"gc-{role['role']}-{pid}-{start_ticks}.jsonl")
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL |
                             os.O_APPEND | os.O_CLOEXEC, 0o600)
        marker = dict(config["marker"], configuration_sha256=config_sha)
        temporary = config["marker_path"] + "." + str(pid) + ".tmp"
        try:
            with open(temporary, "x", encoding="utf-8") as stream:
                json.dump(marker, stream, sort_keys=True); stream.write("\n")
            try:
                os.link(temporary, config["marker_path"])
            except FileExistsError:
                with open(config["marker_path"], encoding="utf-8") as stream:
                    if json.load(stream) != marker:
                        raise ValueError("Another profiling marker occupies this cell")
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    except Exception as error:
        if descriptor is not None:
            os.close(descriptor)
        failure(type(error).__name__ + ": " + str(error)[:512])
        return

    limit = config["log_limit_bytes_per_process"]
    written = 0
    exhausted = False
    busy = False
    sequence = 0
    active = {}

    def append(record):
        nonlocal written, exhausted
        if exhausted:
            return
        data = (json.dumps(record, separators=(",", ":"), allow_nan=False) + "\n").encode()
        if len(data) > 8192:
            raise ValueError("Oversized fixed-shape GC observation")
        if written + len(data) > limit - 1024:
            data = (json.dumps({"kind": "log-limit", "pid": pid,
                               "start_ticks": start_ticks, "role": role["role"],
                               "monotonic_ns": time.monotonic_ns()}) + "\n").encode()
            exhausted = True
        offset = 0
        while offset < len(data):
            count = os.write(descriptor, data[offset:])
            if count <= 0:
                raise OSError("GC append made no progress")
            offset += count
        written += len(data)

    append({"kind": "attached", "schema_version": 1, "task": "Perf-01",
            "formal_timing_eligible": False, "role": role["role"],
            "supervision_role": role["supervision_role"], "pid": pid,
            "ppid": ppid, "start_ticks": start_ticks,
            "native_thread_id": _thread.get_native_id(),
            "monotonic_ns": time.monotonic_ns(), "process_cpu_ns": time.process_time_ns(),
            "configuration_sha256": config_sha, "entry": entry,
            "entry_sha256": role["entry_sha256"], "argv": sys.argv,
            "python_executable": os.path.realpath(sys.executable),
            "plan_sha256": hashlib.sha256(plan_bytes).hexdigest(),
            "a21_sha256": config["a21_sha256"], "hook_sha256": config["hook_sha256"],
            "cpu_affinity": sorted(os.sched_getaffinity(0)),
            "gc_enabled": gc.isenabled(), "gc_threshold": gc.get_threshold(),
            "preexisting_gc_callbacks": len(gc.callbacks),
            "log_limit_bytes": limit,
            "clock_scope": "actual callback entry clocks; no clock or GC-policy changes"})

    def callback(phase, info):
        nonlocal busy, sequence, exhausted
        if busy or exhausted or os.getpid() != pid:
            return
        busy = True
        try:
            now, cpu = time.monotonic_ns(), time.process_time_ns()
            generation = info.get("generation")
            if phase not in ("start", "stop") or type(generation) is not int:
                return
            sequence += 1
            record = {"kind": "gc", "sequence": sequence, "phase": phase,
                      "generation": generation, "monotonic_ns": now,
                      "process_cpu_ns": cpu, "pid": pid, "start_ticks": start_ticks,
                      "role": role["role"], "native_thread_id": _thread.get_native_id(),
                      "gc_count": gc.get_count(), "callbacks": len(gc.callbacks)}
            if phase == "start":
                append(record)
                # Exclude this start callback's measured logging cost from the
                # interval used by the external diagnostic stop rule.
                active[generation] = (now, cpu, time.monotonic_ns(), time.process_time_ns())
            else:
                started = active.pop(generation, None)
                record.update(collected=info.get("collected"), uncollectable=info.get("uncollectable"))
                if started is not None:
                    record.update(start_monotonic_ns=started[0],
                                  callback_entry_duration_ns=now - started[0],
                                  callback_entry_cpu_ns=cpu - started[1],
                                  start_hook_ns=started[2] - started[0],
                                  collection_interval_ns=now - started[2],
                                  collection_interval_cpu_ns=cpu - started[3])
                append(record)
        except Exception as error:
            # A diagnostic write failure never becomes a fabricated target
            # failure or an exception on the application event channel.
            exhausted = True
            try:
                failure("GC logger stopped: " + type(error).__name__ + ": " + str(error)[:256])
            except Exception:
                pass
        finally:
            busy = False

    gc.callbacks.append(callback)


_install()
