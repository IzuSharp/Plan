#!/usr/bin/env python3
"""Serial policy-4 DB calibration using the existing explicit compact driver.

Derived from ROOT/perf01-run/calibrate-apps-v4.py. This does not replace the
domain driver's supervisor, retry policy, correctness oracle or resource checks.
Execute only under the integration owner's exclusive measurement control.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys

ROUTES = {"before": "nativeweave-aot-rust", "after": "nativeweave-aot-rust",
          "direct": "direct-rust", "managed": "managed-aot"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    temporary.replace(path)


def command(args, policy, provider, rate, seconds, output):
    resource = policy["resource_policy"]
    result = [sys.executable, str(args.nativeweave / "tests/Perf01.Database/run.py"),
              "--package-probe", str(args.package_probe), "--provider", provider,
              "--protocol", "http1", "--scenario", "mixed", "--stage", "short",
              "--variant", args.variant, "--route", ROUTES[args.variant],
              "--rate", str(rate), "--seconds", str(seconds), "--concurrency", "16",
              "--seed", "20261119", "--warmup", "16", "--idle-seconds", str(policy["calibration"]["short_idle_seconds"]),
              "--recovery-requests", "16", "--continue-classified-overload", "--compact-observation",
              "--generator-cpus", ",".join(map(str, resource["generator_cpu_affinity"])),
              "--max-p99-ms", str(resource["arrival_p99_limit_ms"]),
              "--max-rss-mib", str(resource["application_rss_limit_bytes"] / 1024**2),
              "--output", str(output), "--isolation-note", args.isolation_note]
    if args.variant in ("before", "after"):
        result.extend(("--observer", str(args.observer)))
    else:
        result.extend(("--comparators", str(args.comparators)))
    if provider == "postgresql":
        result.extend(("--postgres-bin", str(args.postgres_bin)))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nativeweave", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--policy-sha256", required=True)
    parser.add_argument("--package-probe", type=Path, required=True)
    parser.add_argument("--observer", type=Path)
    parser.add_argument("--comparators", type=Path)
    parser.add_argument("--postgres-bin", type=Path)
    parser.add_argument("--variant", choices=ROUTES, default="before")
    parser.add_argument("--groups", nargs="+", choices=("sqlite", "postgresql"), required=True)
    parser.add_argument("--attempt", default="compact-v4")
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--isolation-note", required=True)
    args = parser.parse_args()
    require(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", args.attempt) is not None, "Use a new simple attempt label")
    require(len(set(args.groups)) == len(args.groups), "A provider may appear only once")
    require(args.observer is not None if args.variant in ("before", "after") else args.comparators is not None,
            "NativeWeave needs its exact observer; comparator routes need their actual build manifest")
    require("postgresql" not in args.groups or args.postgres_bin is not None, "PostgreSQL requires its locked server bin directory")
    for name in ("nativeweave", "policy", "package_probe", "observer", "comparators", "postgres_bin", "output_root"):
        if getattr(args, name) is not None:
            setattr(args, name, getattr(args, name).resolve())
    policy = json.loads(args.policy.read_text())
    require(sha(args.policy) == args.policy_sha256 and policy["policy_revision"] == 4, "Use the immutable actual policy-4 SHA")
    require(policy["before_product_commit"] == "ea5fa528035d025bd7a28698ee7c71194432236c", "Unexpected before runtime source")
    resource, calibration = policy["resource_policy"], policy["calibration"]
    require(sorted(os.sched_getaffinity(0)) == resource["cpu_affinity"], "Launch on the frozen service CPUs before spawning PostgreSQL")
    python = policy["build_policy"]["measurement_python"]
    require(sys.version_info[:3] == (3, 12, 14) and Path(sys.executable).resolve() == Path(python["executable"]).resolve()
            and sha(Path(sys.executable).resolve()) == python["executable_sha256"], "Use the exact locked measurement Python")
    require(resource["generator_maximum_dispatch_lag_ms"] == 100 and resource["unexpected_errors_maximum"] == 0,
            "The existing DB driver requires the frozen 100 ms/zero-error policy")
    script_hash = sha(Path(__file__))
    driver_paths = [args.nativeweave / relative for relative in (
        "tests/Perf01.Database/run.py", "tests/Perf01.Database/target.py", "tests/Perf01.Database/perf01_affinity.py",
        "tests/Perf01.Database/perf01_resources.py", "tests/Perf01.Database/perf01_outcomes.py",
        "src/Benchmarks.Domain/cell_worker.py",
        "src/Benchmarks.Domain/common.py", "src/Benchmarks.Domain/http_target.py", "src/Benchmarks.Domain/run.py",
        "src/Benchmarks.Domain/supervision.py", "src/Benchmarks.Harness/nativeweave_bench.py", "tests/Perf01/verify_long.py")]
    driver_hashes = {str(path): sha(path) for path in driver_paths}
    probe_path = args.package_probe / "progress.json"
    producer_paths = [probe_path, args.observer if args.variant in ("before", "after") else args.comparators]
    producer_hashes = {str(path): sha(path) for path in producer_paths}
    probe = json.loads(probe_path.read_text())
    runtime_source = probe["source_repository"]
    if args.variant in ("before", "after"):
        observer = json.loads(args.observer.read_text())
        packages = probe["inputs"]["packages"]
        require(runtime_source.get("scope_status") == "" and observer["original_source"].get("scope_status") == "",
                "Package consumer and observer must identify clean runtime source scopes")
        require(observer["state"] == "built" and observer["original_source"]["commit"] == runtime_source["commit"],
                "Observer and package consumer identify different runtime sources")
        require(packages and all(value["repository"]["commit"] == runtime_source["commit"] for value in packages.values()),
                "Every measured package must come from the same fresh runtime source closure")
        if args.variant == "before":
            require(runtime_source["commit"] == policy["before_product_commit"], "Actual before package/observer source is not the frozen main commit")

    def unchanged():
        require(sha(Path(__file__)) == script_hash and sha(args.policy) == args.policy_sha256, "Controller or policy changed")
        require(all(sha(Path(path)) == digest for path, digest in driver_hashes.items()), "Measurement driver source changed")
        require(all(sha(Path(path)) == digest for path, digest in producer_hashes.items()), "Supplied producer metadata changed between cells")
        require(hashlib.sha256(Path("/proc/sys/kernel/random/boot_id").read_bytes().strip()).hexdigest()
                == resource["measurement_host_kernel_boot_sha256"], "Measurement host boot identity changed")
        require(sorted(os.sched_getaffinity(0)) == resource["cpu_affinity"], "Controller service affinity changed")

    for provider in args.groups:
        output = args.output_root / f"{args.variant}-{provider}-{args.attempt}"
        output.mkdir(parents=True, exist_ok=False)
        rows = []
        receipt = {"task": "Perf-01", "group": provider, "variant": args.variant, "state": "running",
                   "script_sha256": script_hash, "policy_sha256": args.policy_sha256, "compact_observation": True,
                   "driver_source_sha256": driver_hashes, "python_version": sys.version,
                   "producer_metadata_sha256": producer_hashes,
                   "kernel_boot_sha256": resource["measurement_host_kernel_boot_sha256"], "cells": rows}

        def checkpoint():
            save(output / "controller.json", receipt)

        def cell(rate, seconds=None, phase="ladder"):
            unchanged()
            seconds = calibration["stage_seconds"] if seconds is None else seconds
            require(0 < rate <= 10000 and math.ceil(seconds * 1e9 / round(1e9 / rate)) + 1 <= 1_000_000,
                    "Requested cell exceeds the existing DB finite driver bound")
            index = len(rows)
            path = output / f"{index:02}-{phase}-{rate:g}"
            row = {"index": index, "phase": phase, "rate": rate, "seconds": seconds,
                   "directory": str(path), "start_utc": utc(), "state": "running", "commands": []}
            rows.append(row)
            cmd = command(args, policy, provider, rate, seconds, path)
            row["commands"].append(cmd); checkpoint()
            print(json.dumps(row), flush=True)
            try:
                with (output / f"{index:02}.log").open("x") as log:
                    completed = subprocess.run(cmd, cwd=args.nativeweave, stdout=log, stderr=subprocess.STDOUT)
            except BaseException as error:
                row.update(state="interrupted-or-failed", end_utc=utc(), error=type(error).__name__)
                checkpoint()
                raise
            row.update(exit_code=completed.returncode, end_utc=utc(), state="completed")
            result_path = path / "summary.json"
            if not result_path.is_file():
                row.update(valid=False, qualifies=False, error="Missing final result"); checkpoint()
                raise RuntimeError("Incomplete cell; inspect original supervision/partial evidence before resuming")
            result = json.loads(result_path.read_text())
            frozen = json.loads((path / "frozen-inputs.json").read_text())
            plan = json.loads((path / "plan.json").read_text())
            require(frozen["compact_observation"] is True and plan["settings"]["features"]["compact_observation"] is True,
                    "The actual cell did not freeze compact observation")
            require(frozen["route"]["id"] == ROUTES[args.variant], "The actual measured route differs")
            if args.variant in ("before", "after"):
                route = frozen["route"]
                require(route["source"] == runtime_source
                        and route["package_probe_receipt"]["sha256"] == producer_hashes[str(probe_path)]
                        and route["observer_manifest"]["sha256"] == producer_hashes[str(args.observer)],
                        "Actual frozen runtime/observer binding differs from the pinned supplied producers")
            resources = result.get("resources", {}).get("measurement", {})
            qualifies = completed.returncode == 0 and result.get("valid") is True and result.get("qualifies_service_standard") is True
            row.update(valid=result.get("valid", False), qualifies=qualifies, p99_ns=result.get("p99_ns"),
                       rss_peak_bytes=resources.get("rss_peak_bytes"), successes=result.get("successful"),
                       offered=result.get("offered"), throughput=result.get("successful_per_second"),
                       cpu_percent_one_core=resources.get("app_cpu_percent_one_core"), invalid_reasons=result.get("invalid_reasons"),
                       summary_sha256=sha(result_path), frozen_inputs_sha256=sha(path / "frozen-inputs.json"))
            unchanged(); checkpoint()
            print(json.dumps(row), flush=True)
            return qualifies

        checkpoint()
        low = high = None
        try:
            for rate in calibration["database_rates"]:
                if cell(rate): low = rate
                else: high = rate; break
            require(low is not None, "No passing low point; inspect fixture/environment without relaxing criteria")
            while high is None:
                rate = low * 2
                if rate > 10000 or math.ceil(calibration["confirmation_seconds"] * 1e9 / round(1e9 / rate)) + 1 > 1_000_000:
                    break
                if cell(rate): low = rate
                else: high = rate
            while high is not None and high - low > max(1, low * .1):
                rate = (low + high) // 2
                if cell(rate, phase="refine"): low = rate
                else: high = rate
            for attempt in range(calibration["confirmation_attempt_limit"]):
                passed = [cell(low, seconds=calibration["confirmation_seconds"], phase=f"confirmation-{index}")
                          for index in range(calibration["confirmation_fresh_processes"])]
                if all(passed): break
                high = low; low = max(1, math.floor(low * .9))
                cell(low, phase="confirmation-step-down")
            else:
                raise RuntimeError("No consistently passing confirmation point; inspect generator/environment")
            unchanged()
            receipt.update(state="completed", completed_utc=utc()); checkpoint()
            selection = {"group": provider, "variant": args.variant, "compact_observation": True,
                         "highest_consistently_passing_rate": low, "first_failing_bracket_rate": high,
                         "long_rate": max(1, min(500, math.floor(.8 * low))) if args.variant == "before" else None,
                         "concurrency": 16, "completed_utc": utc(), "policy_sha256": args.policy_sha256,
                         "controller_sha256": sha(output / "controller.json"),
                         "higher_failed_points": [{key: row.get(key) for key in ("rate", "phase", "valid", "qualifies", "invalid_reasons")}
                                                  for row in rows if row["rate"] > low and not row.get("qualifies")],
                         "capacity_scope": "Largest consistently passing sampled offered rate; generator failures are not a server-capacity upper bound. An unbracketed result is only a measured lower bound.",
                         "long_rate_scope": "Only the before selection freezes paired long rates; comparator/after capacity never retunes them."}
            save(output / "selection.json", selection)
            print(json.dumps(selection), flush=True)
        except BaseException as error:
            receipt.update(state="interrupted-or-failed", finished_utc=utc(), error=type(error).__name__)
            checkpoint()
            raise


if __name__ == "__main__":
    main()
