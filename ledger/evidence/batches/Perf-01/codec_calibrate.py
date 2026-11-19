#!/usr/bin/env python3
"""Serial codec calibration: the existing v3 loop with explicit producer inputs.

The committed codec driver owns timing, correctness, affinity and cleanup.
Run only under the integration owner's exclusive measurement control.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

ROUTES = {"before": "nativeweave", "after": "nativeweave", "direct": "direct-rust"}
BASELINE = "ea5fa528035d025bd7a28698ee7c71194432236c"


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


def command(args, policy, rate, seconds, output):
    resource = policy["resource_policy"]
    return [sys.executable, str(args.nativeweave / "tests/Perf01.Codec/driver.py"),
            "run", "--manifest", str(args.build), "--corpus", str(args.corpus),
            "--route", ROUTES[args.variant], "--workers", "2",
            "--generator-cpus", ",".join(map(str, resource["generator_cpu_affinity"])),
            "--rate", str(rate), "--queue", "64", "--inflight", "256",
            "--deadline-ms", "1000", "--max-lag-ms", str(resource["generator_maximum_dispatch_lag_ms"]),
            "--recovery-seconds", "4", "--recovery-rate", "1", "--duration-seconds", str(seconds),
            "--warmup-seconds", "5", "--idle-seconds", "5", "--output", str(output)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nativeweave", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--policy-sha256", required=True)
    parser.add_argument("--build", type=Path, required=True, help="Actual prepared codec manifest.json")
    parser.add_argument("--build-sha256", required=True)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--corpus-sha256", required=True, help="SHA-256 of corpus/manifest.json")
    parser.add_argument("--variant", choices=ROUTES, default="before")
    parser.add_argument("--output", type=Path, required=True, help="New calibration directory; never reused")
    args = parser.parse_args()
    for name in ("nativeweave", "policy", "build", "corpus", "output"):
        setattr(args, name, getattr(args, name).resolve())
    policy = json.loads(args.policy.read_text())
    require(sha(args.policy) == args.policy_sha256 and policy["policy_revision"] == 4
            and policy["before_product_commit"] == BASELINE, "Use the exact frozen policy-4 bytes")
    resource, calibration = policy["resource_policy"], policy["calibration"]
    require(resource["cpu_affinity"] == [2, 3] and resource["generator_cpu_affinity"] == [0, 1]
            and resource["generator_maximum_dispatch_lag_ms"] == 100
            and resource["arrival_p99_limit_ms"] == 500
            and resource["application_rss_limit_bytes"] == 268435456
            and resource["unexpected_errors_maximum"] == 0,
            "This v3 wrapper preserves the original CPU/SLO/resource settings")
    require(calibration["stage_seconds"] == 30 and calibration["confirmation_seconds"] == 60
            and calibration["confirmation_fresh_processes"] == 3
            and calibration["confirmation_attempt_limit"] == 10,
            "This v3 wrapper preserves the original ladder and confirmation algorithm")
    python = policy["build_policy"]["measurement_python"]
    require(sys.version_info[:3] == (3, 12, 14)
            and Path(sys.executable).resolve() == Path(python["executable"]).resolve()
            and sha(Path(sys.executable).resolve()) == python["executable_sha256"],
            "Use the exact locked measurement Python")
    require(sha(args.build) == args.build_sha256 and sha(args.corpus / "manifest.json") == args.corpus_sha256,
            "Actual build or corpus manifest differs from supplied immutable identity")
    build = json.loads(args.build.read_text())
    require(build["source_dirty"] is False, "Measured runtime source must be clean")
    if args.variant == "before":
        require(build["source_commit"] == BASELINE, "Before runtime must be the pre-product-edit main commit")
    driver_hashes = {args.nativeweave / "tests/Perf01.Codec" / name: digest
                     for name, digest in build["driver_sha256"].items()}
    driver_hashes[args.nativeweave / "src/Benchmarks.Harness/nativeweave_bench.py"] = build["a21_sha256"]
    script_hash = sha(Path(__file__))

    def unchanged():
        require(sha(Path(__file__)) == script_hash and sha(args.policy) == args.policy_sha256,
                "Controller or policy changed")
        require(sha(args.build) == args.build_sha256 and sha(args.corpus / "manifest.json") == args.corpus_sha256,
                "Build or corpus metadata changed")
        require(all(sha(path) == digest for path, digest in driver_hashes.items()),
                "Current codec/A21 driver source differs from its prepared manifest")
        require(hashlib.sha256(Path("/proc/sys/kernel/random/boot_id").read_bytes().strip()).hexdigest()
                == resource["measurement_host_kernel_boot_sha256"], "Measurement host boot changed")
        require(sorted(os.sched_getaffinity(0)) == resource["cpu_affinity"],
                "Launch and retain the wrapper on the frozen service CPUs")

    unchanged()
    args.output.mkdir(parents=True, exist_ok=False)
    rows = []
    receipt = {"task": "Perf-01", "group": "codec", "variant": args.variant, "state": "running",
               "script_sha256": script_hash, "policy_sha256": args.policy_sha256,
               "build_manifest": str(args.build), "build_sha256": args.build_sha256,
               "corpus_manifest_sha256": args.corpus_sha256, "source_commit": build["source_commit"],
               "driver_commit": build["driver_commit"], "a21_sha256": build["a21_sha256"],
               "driver_source_sha256": {str(path): digest for path, digest in driver_hashes.items()},
               "python_version": sys.version, "kernel_boot_sha256": resource["measurement_host_kernel_boot_sha256"],
               "cells": rows}

    def checkpoint():
        save(args.output / "controller.json", receipt)

    def cell(rate, seconds=30, phase="ladder"):
        unchanged()
        index = len(rows); path = args.output / f"{index:02}-{phase}-{rate:g}"
        cmd = command(args, policy, rate, seconds, path)
        row = {"index": index, "phase": phase, "rate": rate, "seconds": seconds, "directory": str(path),
               "command": cmd, "start_utc": utc(), "state": "running"}
        rows.append(row); checkpoint()
        print(json.dumps({key: value for key, value in row.items() if key != "command"}), flush=True)
        try:
            with (args.output / f"{index:02}.log").open("x") as log:
                completed = subprocess.run(cmd, cwd=args.nativeweave, stdout=log, stderr=subprocess.STDOUT,
                                           timeout=seconds + 150)
        except BaseException as error:
            row.update(state="interrupted-or-failed", end_utc=utc(), error=type(error).__name__)
            checkpoint()
            raise
        row.update(exit_code=completed.returncode, end_utc=utc(), state="completed")
        require(all((path / name).is_file() for name in ("summary.json", "result.json", "plan.json", "resources.jsonl")),
                "Missing completed cell evidence; inspect partial output and process cleanup before another load")
        result = json.loads((path / "result.json").read_text())
        summary = json.loads((path / "summary.json").read_text())
        actual = json.loads((path / "plan.json").read_text())
        require(actual["manifest_sha256"] == args.build_sha256 and actual["corpus_manifest_sha256"] == args.corpus_sha256
                and actual["source_commit"] == build["source_commit"] and actual["route"] == ROUTES[args.variant]
                and actual["controller_sha256"] == build["driver_sha256"]["driver.py"]
                and actual["a21_sha256"] == build["a21_sha256"], "Actual cell producer/driver binding differs")
        start, end = result.get("scheduled_start_ns", 0), result.get("scheduled_end_ns", 0)
        peak = None
        with (path / "resources.jsonl").open() as stream:
            for line in stream:
                sample = json.loads(line)
                if start <= sample["observer_ns"] <= end:
                    value = sample["target"]["rss_bytes"]["value"]
                    if value is not None:
                        require(type(value) is int and value >= 0, "Malformed measured RSS")
                        peak = value if peak is None else max(peak, value)
        p99 = summary["arrival_success_ns"]["p99"]
        require(p99 is None or (type(p99) in (int, float) and math.isfinite(p99) and p99 >= 0), "Malformed p99")
        qualifies = (completed.returncode == 0 and result["valid"] is True
                     and result.get("service_standard_met") is True and result.get("recovery_standard_met") is True
                     and p99 is not None and p99 <= 500_000_000 and peak is not None and peak <= 268435456)
        row.update(valid=result["valid"], qualifies=qualifies, p99_ns=p99, rss_peak_bytes=peak,
                   successes=summary["successes"], offered=summary["offered"], throughput=summary["successful_operations_per_second"],
                   cpu_percent_one_core=summary["target_cpu_percent_one_core"], invalid_reasons=result["invalid_reasons"],
                   operation_outcomes=result.get("operation_outcomes"), recovery_standard_met=result.get("recovery_standard_met"),
                   summary_sha256=sha(path / "summary.json"), result_sha256=sha(path / "result.json"), plan_sha256=sha(path / "plan.json"))
        unchanged(); checkpoint()
        print(json.dumps({key: value for key, value in row.items() if key != "command"}), flush=True)
        return qualifies

    checkpoint()
    low = high = None
    try:
        for rate in calibration["codec_rates"]:
            if cell(rate): low = rate
            else: high = rate; break
        require(low is not None, "No valid stable low point; investigate without relaxing the frozen policy")
        while high is None:
            rate = low * 2
            if rate * 30 > 1_000_000: break
            if cell(rate): low = rate
            else: high = rate
        while high is not None and high - low > max(1, low * .1):
            mid = (low + high) // 2
            if cell(mid, phase="refine"): low = mid
            else: high = mid
        for confirmation_round in range(calibration["confirmation_attempt_limit"]):
            passed = [cell(low, seconds=60, phase=f"confirmation-{index}") for index in range(3)]
            if all(passed): break
            high = low; low = max(1, math.floor(low * .9))
            if not cell(low, phase="confirmation-step-down"): continue
        else:
            raise RuntimeError("No consistent point within finite confirmation rounds")
        unchanged(); receipt.update(state="completed", completed_utc=utc()); checkpoint()
        selection = {"group": "codec", "variant": args.variant,
                     "highest_consistently_passing_rate": low, "first_failing_bracket_rate": high,
                     "long_rate": max(1, min(500, math.floor(.8 * low))) if args.variant == "before" else None,
                     "workers": 2, "completed_utc": utc(), "policy_sha256": args.policy_sha256,
                     "build_sha256": args.build_sha256, "corpus_manifest_sha256": args.corpus_sha256,
                     "controller_sha256": sha(args.output / "controller.json"),
                     "higher_failed_points": [{key: row.get(key) for key in ("rate", "phase", "valid", "qualifies", "invalid_reasons", "operation_outcomes")}
                                              for row in rows if row["rate"] > low and not row.get("qualifies")],
                     "capacity_scope": "Largest consistently passing sampled offered rate; generator-lag failures are not a server-capacity upper bound. An unbracketed result is only a measured lower bound.",
                     "long_rate_scope": "Only the before selection freezes paired long rates; after/direct capacity never retunes them."}
        save(args.output / "selection.json", selection)
        print(json.dumps(selection), flush=True)
    except BaseException as error:
        receipt.update(state="interrupted-or-failed", finished_utc=utc(), error=type(error).__name__)
        checkpoint()
        raise


if __name__ == "__main__":
    main()
