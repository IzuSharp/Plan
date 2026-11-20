#!/usr/bin/env python3
"""Root-owned, serial short protocol cohorts using existing immutable binaries.

This is an execution entrypoint, not a result. Run only after source review,
finite utility tests, and explicit release of the shared measurement resource.
The noise stage sees before data only. Compare uses a previously committed index
and fresh cells in interleaved before/after/direct order, reversed on repetition1.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def now():
    return datetime.now(timezone.utc).isoformat()


def interrupted(signum, frame):
    raise InterruptedError("Protocol cohort controller received signal " + str(signum))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("noise", "compare"), required=True)
    parser.add_argument("--nativeweave", type=Path, required=True)
    parser.add_argument("--catalog", type=Path, default=HERE / "protocol-layered/catalog.json")
    parser.add_argument("--before-build", type=Path, required=True)
    parser.add_argument("--direct-build", type=Path, required=True)
    parser.add_argument("--client-build", type=Path, required=True)
    parser.add_argument("--after-build", type=Path)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--private-key", type=Path, required=True)
    parser.add_argument("--exclusive-lock", type=Path, required=True)
    parser.add_argument("--noise-index", type=Path)
    parser.add_argument("--noise-index-sha256")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, interrupted)
    require(sys.version_info[:3] == (3, 12, 14), "Use the frozen Python 3.12.14 interpreter")
    require(args.stage != "compare" or args.after_build and args.noise_index and args.noise_index_sha256,
            "Compare needs actual after producer and precommitted noise index/SHA")
    root = args.output.resolve()
    require(not root.exists(), "Choose a new output; earlier complete/partial evidence is never overwritten")
    product = args.nativeweave.resolve()
    driver = product / "tests/Perf01.Protocols/run.py"
    compare = HERE / "protocol_compare.py"
    catalog = read(args.catalog)
    require(catalog["task"] == "Perf-01" and catalog["service_cpus"] == [2, 3] and catalog["generator_cpus"] == [0, 1], "Wrong frozen resource layout")
    profiles = [row for row in catalog["cells"] if row["kind"] == "short-comparison"]
    require(len(profiles) == 2 and {row["id"] for row in profiles} == {"grpc-unary", "grpc-streams"}, "Expected the two frozen weak-writer gRPC partitions")
    source_items = {"protocol_cohorts.py": Path(__file__), "protocol_compare.py": compare, "catalog.json": args.catalog}
    for name in ("tests/Perf01.Protocols/run.py", "tests/Perf01.Protocols/adapter.py", "tests/Perf01.Protocols/affinity.py",
                 "src/Benchmarks.Harness/nativeweave_bench.py", "src/Benchmarks.Domain/common.py",
                 "src/Benchmarks.Domain/supervision.py", "tests/Perf01/verify_long.py"):
        source_items[name] = product / name
    for row in profiles:
        path = args.catalog.parent / row["profile"]
        require(sha(path) == row["profile_sha256"] and row["planned_minimum_per_scenario"] >= 100 and row["concurrency"] == 4,
                "Layered profile identity or minimum count differs")
        source_items["profiles/" + row["id"] + ".json"] = path
    source_contract = {name: sha(path) for name, path in source_items.items()}
    frozen_sources = {str(path.resolve()): source_contract[name] for name, path in source_items.items()}
    builds = {"before": args.before_build.resolve(), "direct": args.direct_build.resolve()}
    if args.stage == "compare":
        builds["after"] = args.after_build.resolve()
    build_pins = {key: {"path": str(path), "sha256": sha(path)} for key, path in builds.items()}
    common = {"path": str(args.client_build.resolve()), "sha256": sha(args.client_build)}
    tls = {"certificate_sha256": sha(args.certificate), "private_key_sha256": sha(args.private_key)}
    noise = None
    if args.stage == "compare":
        require(sha(args.noise_index) == args.noise_index_sha256, "Noise index differs from the hash committed before after timing")
        noise = read(args.noise_index)
        require(noise["status"] == "completed" and noise["stage"] == "noise", "Noise stage was not complete")
        require(noise["source_contract_sha256"] == source_contract and noise["common_client"]["sha256"] == common["sha256"] and noise["tls"] == tls,
                "Driver/profile/client/TLS input differs from before-only freeze")
        require(all(noise["builds"][key]["sha256"] == build_pins[key]["sha256"] for key in ("before", "direct")), "Before/direct producer differs from noise stage")
    root.mkdir(parents=True)
    journal = {"task": "Perf-01", "stage": args.stage, "status": "incomplete", "started_utc": now(),
               "source_files_sha256": frozen_sources, "source_contract_sha256": source_contract,
               "builds": build_pins, "common_client": common, "tls": tls,
               "service_cpus": [2, 3], "generator_cpus": [0, 1], "cells": [], "profiles": {},
               "notice": "Only actual completed cells receive results; no duration/capacity acceptance is inferred by orchestration"}
    save(root / "controller.json", journal)

    def stable():
        require(all(sha(Path(path)) == digest for path, digest in frozen_sources.items()), "A frozen driver/profile source changed")
        require(all(sha(Path(row["path"])) == row["sha256"] for row in build_pins.values()) and sha(args.client_build) == common["sha256"],
                "Producer metadata changed")
        require(sha(args.certificate) == tls["certificate_sha256"] and sha(args.private_key) == tls["private_key_sha256"], "TLS input changed")

    def command(argv, directory, label):
        with (directory / (label + ".stdout.log")).open("w") as stdout, (directory / (label + ".stderr.log")).open("w") as stderr:
            process = subprocess.Popen(argv, stdout=stdout, stderr=stderr, start_new_session=True)
            try:
                status = process.wait()
            except BaseException:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=60)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    journal["forced_controller_cleanup"] = True
                    journal["cleanup_limit"] = "Controller group was forcibly reaped; independently verify that its separately grouped adapter and workloads are absent before another timing window"
                raise
        require(status == 0, label + " exited " + str(status) + "; preserve the failed cell and logs")

    try:
        for row in profiles:
            profile_root = root / row["id"]
            profile_root.mkdir()
            paths = {variant: [] for variant in ("before", "after", "direct")}
            for repetition in range(3):
                order = ["before"] if args.stage == "noise" else (["direct", "after", "before"] if repetition == 1 else ["before", "after", "direct"])
                for variant in order:
                    stable()
                    output = profile_root / (str(repetition) + "-" + variant)
                    entry = {"profile": row["id"], "variant": variant, "repetition": repetition, "output": str(output), "state": "running", "started_utc": now()}
                    journal["cells"].append(entry)
                    save(root / "controller.json", journal)
                    print(json.dumps(entry), flush=True)
                    prepare = ["taskset", "--cpu-list", "2,3", sys.executable, str(driver), "prepare", "--build", str(builds[variant]),
                        "--client-build", str(args.client_build.resolve()), "--profile", str((args.catalog.parent / row["profile"]).resolve()),
                        "--group", row["group"], "--rate", str(row["rate"]), "--duration", str(row["duration_seconds"]), "--concurrency", "4",
                        "--generator-cpus", "0,1", "--certificate", str(args.certificate.resolve()), "--private-key", str(args.private_key.resolve()), "--output", str(output)]
                    entry["prepare_command"] = prepare
                    command(prepare, profile_root, str(repetition) + "-" + variant + "-prepare")
                    run = ["taskset", "--cpu-list", "2,3", sys.executable, str(driver), "run", "--plan", str(output / "plan.json"),
                           "--exclusive-lock", str(args.exclusive_lock.resolve())]
                    entry["run_command"] = run
                    command(run, profile_root, str(repetition) + "-" + variant + "-run")
                    stable()
                    result = read(output / "result.json")
                    entry.update(state="completed", ended_utc=now(), result_sha256=sha(output / "result.json"),
                                 valid=result.get("valid"), service_standard_met=result.get("service_standard_met"))
                    save(root / "controller.json", journal)
                    require(result["valid"] and result["service_standard_met"], "Completed cell failed correctness/generation/service standard; no automatic replacement")
                    paths[variant].append(str(output))
            stable()
            extraction = profile_root / ("noise" if args.stage == "noise" else "comparison")
            argv = [sys.executable, str(compare), "--nativeweave", str(product), "--output", str(extraction)]
            if args.stage == "noise":
                argv += ["freeze-noise", "--before", *paths["before"], "--direct-build", str(args.direct_build.resolve()),
                         "--direct-build-sha256", build_pins["direct"]["sha256"]]
                output_name = "noise.json"
            else:
                frozen = noise["profiles"][row["id"]]
                argv += ["compare", "--before", *paths["before"], "--after", *paths["after"], "--direct", *paths["direct"],
                         "--noise", frozen["receipt"], "--noise-sha256", frozen["sha256"]]
                output_name = "comparison.json"
            command(argv, profile_root, "extract")
            journal["profiles"][row["id"]] = {"configuration": row, "receipt": str(extraction / output_name), "sha256": sha(extraction / output_name), "cells": paths}
            save(root / "controller.json", journal)
        stable()
        journal.update(status="completed", finished_utc=now())
    except BaseException as error:
        journal.update(status="failed", finished_utc=now(), failure=type(error).__name__ + ": " + str(error))
        raise
    finally:
        save(root / "controller.json", journal)
        if journal["status"] == "completed":
            save(root / ("noise-index.json" if args.stage == "noise" else "comparison-index.json"), journal)
    print(json.dumps({"status": journal["status"], "output": str(root), "profiles": len(journal["profiles"])}), flush=True)


if __name__ == "__main__":
    main()
