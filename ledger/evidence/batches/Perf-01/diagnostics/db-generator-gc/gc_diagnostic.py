#!/usr/bin/env python3
"""Prepare/run/stop one zero-credit GC diagnostic using unchanged frozen DB code."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

FREEZE_SHA = "85061c4e01b28fc72a5b20519ce2d8c01d79cae271238ba36e0a3465b0b8f4a3"
COMMAND_SHA = "9604544d24953430ed90ec20f460565d41fa706202d21e397f56194c491594d7"
DRIVER_COMMIT = "ce2a3c75cbd535490897d062b6cbb7c095408307"
HERE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path, maximum=131072):
    with Path(path).open("rb") as stream:
        data = stream.read(maximum + 1)
    require(len(data) <= maximum, "Oversized diagnostic metadata: " + str(path))
    return json.loads(data)


def create(path, value):
    path = Path(path)
    temporary = path.with_name(path.name + "." + str(os.getpid()) + ".tmp")
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
            stream.write("\n")
        # Publish complete JSON without replacing any existing owner receipt.
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def prepare(args):
    require(sha(args.freeze) == FREEZE_SHA, "Use the unchanged published final freeze")
    require(sha(args.command_document) == COMMAND_SHA, "Use the exact frozen DB command document")
    freeze, document = read(args.freeze), read(args.command_document)
    require(document["immutable_measurement_driver"]["commit"] == DRIVER_COMMIT, "Wrong DB driver identity")
    driver = Path(document["immutable_measurement_driver"]["path"]).resolve()
    original = next(row["argv"] for row in document["commands"]
                    if row["id"] == "database-before-postgresql-long-001")
    expected = {"--provider": "postgresql", "--route": "nativeweave-aot-rust",
                "--stage": "soak", "--scenario": "mixed", "--rate": "144",
                "--seconds": "1802", "--concurrency": "16", "--seed": "20261119",
                "--warmup": "16", "--recovery-requests": "32", "--idle-seconds": "60"}
    for flag, value in expected.items():
        require(original[original.index(flag) + 1] == value, "Unexpected frozen flag: " + flag)
    require("--compact-observation" in original, "Full compact ledger mode is required")
    require(document["python"]["recorded_executable_sha256"] == sha(document["python"]["executable"]),
            "Measurement Python bytes differ")
    pins = document["required_source_and_metadata_sha256"]
    sources = [driver / name for name in (
        "src/Benchmarks.Domain/cell_worker.py", "tests/Perf01.Database/target.py",
        "tests/Perf01.Database/run.py", "src/Benchmarks.Harness/nativeweave_bench.py",
        "src/Benchmarks.Domain/supervision.py", "tests/Perf01/verify_long.py")]
    require(all(sha(path) == pins[str(path)] for path in sources), "Frozen diagnostic entry/helper source differs")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    logs = output / "gc"
    logs.mkdir()
    cell = output / "cell"
    a21 = driver / "src/Benchmarks.Harness/nativeweave_bench.py"
    scheduler = driver / "src/Benchmarks.Domain/cell_worker.py"
    target = driver / "tests/Perf01.Database/target.py"
    argv = list(original)
    argv[argv.index("--output") + 1] = str(cell)
    argv[argv.index("--variant") + 1] = "diagnostic"
    config = {"schema_version": 1, "task": "Perf-01", "formal_timing_eligible": False,
              "duration_credit_seconds": 0, "freeze_sha256": FREEZE_SHA,
              "command_document_sha256": COMMAND_SHA, "original_command": original,
              "command": argv, "working_directory": document["working_directory"],
              "only_argv_changes": ["--output", "--variant"],
              "cell_output": str(cell), "plan_path": str(cell / "plan.json"),
              "control_path": str(cell / "control.json"), "marker_path": str(cell / "profile-driver.json"),
              "log_directory": str(logs), "log_limit_bytes_per_process": 16 * 1024**2,
              "python_realpath": str(Path(document["python"]["executable"]).resolve()),
              "python_sha256": document["python"]["recorded_executable_sha256"],
              "a21_path": str(a21), "a21_sha256": pins[str(a21)],
              "hook_path": str(HERE / "sitecustomize.py"), "hook_sha256": sha(HERE / "sitecustomize.py"),
              "controller_path": str(Path(__file__).resolve()), "controller_sha256": sha(__file__),
              "frozen_source_sha256": {str(path): pins[str(path)] for path in sources},
              "manual_max_effective_seconds": 360, "manual_pause_flush_grace_seconds": 2,
              "manual_stop_pause_ns": 100000000,
              "marker": {"task": "Perf-01", "formal_timing_eligible": False,
                         "duration_credit_seconds": 0,
                         "scope": "GC callback diagnostic, intentionally interrupted; not formal timing"},
              "roles": [
                  {"role": "scheduler", "supervision_role": "cell-worker", "entry": str(scheduler),
                   "entry_sha256": pins[str(scheduler)],
                   "argv": [str(scheduler), "--plan", str(cell / "plan.json"), "--route", "nativeweave-aot-rust",
                            "--repetition", "0", "--output", str(cell / "observation.json"),
                            "--a21", str(a21), "--compact-observation"]},
                  {"role": "target", "supervision_role": "http-adapter", "entry": str(target),
                   "entry_sha256": pins[str(target)],
                   "argv": [str(target), "--manifest", str(cell / "target.json"), "--route", "nativeweave-aot-rust",
                            "--a21", str(a21)]}]}
    require(freeze["long_acceptance"]["groups"] and len(json.dumps(config)) < 65536, "Invalid diagnostic configuration")
    create(output / "configuration.json", config)
    print(json.dumps({"configuration": str(output / "configuration.json"),
                      "configuration_sha256": sha(output / "configuration.json"),
                      "planned_requests": 259526, "formal_timing_eligible": False,
                      "duration_credit_seconds": 0}, indent=2))


def load_config(path):
    config = read(path, 65536)
    require(config["formal_timing_eligible"] is False and config["duration_credit_seconds"] == 0,
            "Only an explicitly zero-credit diagnostic is supported")
    require(config["freeze_sha256"] == FREEZE_SHA and config["command_document_sha256"] == COMMAND_SHA,
            "Diagnostic source selection differs")
    require(sha(config["hook_path"]) == config["hook_sha256"] and sha(__file__) == config["controller_sha256"],
            "Diagnostic helper bytes changed after preparation")
    return config


def run(args):
    config = load_config(args.config)
    require(not Path(config["cell_output"]).exists(), "Never rerun into an existing diagnostic cell")
    require(all(sha(path) == expected for path, expected in config["frozen_source_sha256"].items()),
            "Frozen measurement files changed")
    environment = dict(os.environ)
    environment["NW_PERF01_GC_CONFIG"] = str(args.config.resolve())
    environment["PYTHONPATH"] = str(Path(config["hook_path"]).parent) + (
        os.pathsep + environment["PYTHONPATH"] if environment.get("PYTHONPATH") else "")
    os.chdir(config["working_directory"])
    # Replace this launcher with the original flock/taskset/DB command. The
    # existing DB supervisor and PostgreSQL context retain process ownership.
    os.execvpe(config["command"][0], config["command"], environment)


def marker(config, config_sha):
    path = Path(config["marker_path"])
    if not path.parent.is_dir():
        return
    value = dict(config["marker"], configuration_sha256=config_sha)
    try:
        create(path, value)
    except FileExistsError:
        require(read(path, 8192) == value, "Another marker occupies the diagnostic cell")


def stop(config, reason):
    path = Path(config["control_path"])
    require(path.parent.is_dir(), "Cell has not created its directory; do not create it before run.py")
    value = {"stop": True, "reason": reason, "task": "Perf-01", "formal_timing_eligible": False}
    try:
        create(path, value)
    except FileExistsError:
        require(read(path, 8192).get("stop") is True, "A different existing control requires owner inspection")
    return {"path": str(path), "monotonic_ns": time.monotonic_ns(), "reason": reason}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    prep = commands.add_parser("prepare")
    prep.add_argument("--freeze", type=Path, required=True)
    prep.add_argument("--command-document", type=Path, required=True)
    prep.add_argument("--output", type=Path, required=True)
    for name in ("run", "stop"):
        command = commands.add_parser(name)
        command.add_argument("--config", type=Path, required=True)
        if name == "stop":
            command.add_argument("--reason", default="Operator stopped zero-credit GC diagnostic")
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args)
    elif args.action == "run":
        run(args)
    else:
        config = load_config(args.config)
        marker(config, sha(args.config))
        print(json.dumps(stop(config, args.reason), indent=2))


if __name__ == "__main__":
    main()
