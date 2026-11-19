#!/usr/bin/env python3
"""Serial policy-4 HTTP/gRPC calibration using the existing exclusive cell driver.

This is a thin short-run command loop, not a supervisor or resume facility.
Root owns the complete invocation and checks known descendants after interruption.
"""
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

BASELINE = "ea5fa528035d025bd7a28698ee7c71194432236c"
ROUTES = {"before": "nativeweave-aot-rust", "after": "nativeweave-aot-rust", "direct": "direct-rust"}
PROFILE_SHA256 = {
    "http": "b523306d177fe23a9c32025fdb97fa8efb422a182320a64d8f037905e31efa6a",
    "grpc": "fcd529ae210b57a6c3030f7521127204f665f33978ec50d848d13259a7b697af",
}


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nativeweave", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--policy-sha256", required=True)
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--build-sha256", required=True)
    parser.add_argument("--client-build", type=Path, required=True)
    parser.add_argument("--client-build-sha256", required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--private-key", type=Path, required=True)
    parser.add_argument("--exclusive-lock", type=Path, required=True)
    parser.add_argument("--variant", choices=ROUTES, required=True)
    parser.add_argument("--groups", nargs="+", choices=("http", "grpc"), required=True)
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    require(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", args.attempt) is not None, "Use a fresh simple attempt label")
    require(len(set(args.groups)) == len(args.groups), "Each group may be selected once")
    for name in ("nativeweave", "policy", "build", "client_build", "certificate", "private_key", "exclusive_lock", "output_root"):
        setattr(args, name, getattr(args, name).resolve())
    for path, expected in ((args.policy, args.policy_sha256), (args.build, args.build_sha256),
                           (args.client_build, args.client_build_sha256)):
        require(sha(path) == expected, "Supplied immutable input hash differs: " + path.name)
    policy = json.loads(args.policy.read_text())
    require(policy["policy_revision"] == 4 and policy["before_product_commit"] == BASELINE, "Use the frozen policy-4 baseline")
    resource, calibration = policy["resource_policy"], policy["calibration"]
    require(sorted(os.sched_getaffinity(0)) == resource["cpu_affinity"] == [2, 3]
            and resource["generator_cpu_affinity"] == [0, 1], "Use the frozen service/generator CPU layout")
    python = policy["build_policy"]["measurement_python"]
    require(sys.version_info[:3] == (3, 12, 14) and Path(sys.executable).resolve() == Path(python["executable"]).resolve()
            and sha(Path(sys.executable).resolve()) == python["executable_sha256"], "Use the exact locked measurement Python")
    require((calibration["stage_seconds"], calibration["confirmation_seconds"], calibration["confirmation_fresh_processes"],
             calibration["confirmation_attempt_limit"], calibration["short_idle_seconds"]) == (30, 60, 3, 10, 5),
            "This wrapper preserves the existing policy-4 finite algorithm")
    build, client = (json.loads(path.read_text()) for path in (args.build, args.client_build))
    require(build["eligible_for_measurement"] is True and client["eligible_for_measurement"] is True,
            "Compilation-only outputs cannot be calibrated")
    require(build.get("route", "nativeweave-aot-rust") == ROUTES[args.variant], "Build route differs from selected variant")
    require(client.get("route", "nativeweave-aot-rust") == "nativeweave-aot-rust"
            and client["product_source_commit"] == BASELINE and client["product_source_dirty"] is False
            and client["toolchain"]["isa"] == "x86-64-v2", "Use the immutable common before client build")
    if args.variant in ("before", "after"):
        require(build["product_source_dirty"] is False and build["toolchain"]["isa"] == "x86-64-v2",
                "NativeWeave producer must identify clean runtime source and the frozen AOT ISA")
        if args.variant == "before":
            require(build["product_source_commit"] == BASELINE, "Before must load the fixed main runtime")
    else:
        require(build["toolchain"]["isa"] == "x86-64-default" and build["client_build_sha256"] == args.client_build_sha256,
                "Direct Rust must retain its generic producer and the same common client")
    profiles = {"http": args.nativeweave / "tests/Perf01.Protocols/profile-v1.json",
                "grpc": args.policy.parent / "grpc-budget-profile-v2.json"}
    driver = args.nativeweave / "tests/Perf01.Protocols/run.py"
    inputs = [Path(__file__).resolve(), args.policy, args.build, args.client_build, args.certificate, args.private_key]
    inputs += [args.nativeweave / name for name in (
        "tests/Perf01.Protocols/run.py", "tests/Perf01.Protocols/adapter.py", "tests/Perf01.Protocols/affinity.py",
        "src/Benchmarks.Harness/nativeweave_bench.py", "src/Benchmarks.Domain/common.py", "src/Benchmarks.Domain/supervision.py")]
    inputs += [profiles[group] for group in args.groups]
    pins = {str(path): sha(path) for path in inputs}

    def unchanged():
        require(all(sha(path) == value for path, value in pins.items()), "Controller, producer, profile, TLS or driver input changed")
        require(hashlib.sha256(Path("/proc/sys/kernel/random/boot_id").read_bytes().strip()).hexdigest()
                == resource["measurement_host_kernel_boot_sha256"], "Measurement host boot identity changed")
        require(sorted(os.sched_getaffinity(0)) == resource["cpu_affinity"], "Controller service affinity changed")

    unchanged()
    for group in args.groups:
        require(pins[str(profiles[group])] == PROFILE_SHA256[group], "Use the reviewed mixed policy-4 protocol profile")
        profile = json.loads(profiles[group].read_text())
        require(profile["timing"]["max_dispatch_lag_ns"] == resource["generator_maximum_dispatch_lag_ms"] * 1_000_000
                and profile["service_standard"]["arrival_p99_maximum_ms"] == resource["arrival_p99_limit_ms"]
                and profile["service_standard"]["whole_process_rss_bytes_maximum"] == resource["application_rss_limit_bytes"]
                and profile["service_standard"]["unexpected_error_rate_maximum"] == resource["unexpected_errors_maximum"],
                "Profile and policy service standard differ")
        output = args.output_root / f"{args.variant}-{group}-{args.attempt}"
        output.mkdir(parents=True, exist_ok=False)
        profile["timing"]["idle_seconds"] = calibration["short_idle_seconds"]
        profile_path = output / "profile-short.json"
        save(profile_path, profile)
        pins[str(profile_path)] = sha(profile_path)
        rows = []
        receipt = {"task": "Perf-01", "group": group, "variant": args.variant, "state": "running",
                   "policy_sha256": args.policy_sha256, "script_sha256": pins[str(Path(__file__).resolve())],
                   "build_manifest": str(args.build), "build_sha256": args.build_sha256,
                   "client_build_manifest": str(args.client_build), "client_build_sha256": args.client_build_sha256,
                   "source_and_input_sha256": dict(pins), "profile_sha256": pins[str(profile_path)],
                   "python_version": sys.version, "kernel_boot_sha256": resource["measurement_host_kernel_boot_sha256"],
                   "service_cpus": resource["cpu_affinity"], "generator_cpus": resource["generator_cpu_affinity"], "cells": rows}

        def checkpoint():
            save(output / "controller.json", receipt)

        def supported(rate, seconds):
            return 0 < rate <= 10000 and math.ceil((seconds * 1e9 + profile["timing"]["max_dispatch_lag_ns"]) / round(1e9 / rate)) + 1 <= 1_000_000

        def cell(rate, seconds=30, phase="ladder"):
            unchanged()
            require(supported(rate, seconds), "Requested cell exceeds the existing protocol finite bounds")
            index = len(rows); path = output / f"{index:02}-{phase}-{rate:g}"
            row = {"index": index, "phase": phase, "rate": rate, "seconds": seconds, "directory": str(path),
                   "start_utc": utc(), "state": "running", "commands": []}
            rows.append(row); checkpoint()
            print(json.dumps({key: row[key] for key in ("index", "phase", "rate", "seconds", "directory", "start_utc")}), flush=True)
            prep = [sys.executable, str(driver), "prepare", "--build", str(args.build), "--client-build", str(args.client_build),
                    "--profile", str(profile_path), "--group", group, "--rate", str(rate), "--concurrency", "64",
                    "--generator-cpus", "0,1", "--duration", str(seconds), "--output", str(path),
                    "--certificate", str(args.certificate), "--private-key", str(args.private_key)]
            run = [sys.executable, str(driver), "run", "--plan", str(path / "plan.json"), "--exclusive-lock", str(args.exclusive_lock)]
            try:
                for label, command in (("prepare", prep), ("run", run)):
                    row["commands"].append(command); checkpoint()
                    with (output / f"{index:02}-{label}.log").open("x") as log:
                        completed = subprocess.run(command, cwd=args.nativeweave, stdout=log, stderr=subprocess.STDOUT)
                    row[label + "_exit_code"] = completed.returncode; checkpoint()
                    if label == "prepare":
                        require(completed.returncode == 0, "Preparation failed; preserve the attempt and inspect its log")
                row.update(exit_code=completed.returncode, end_utc=utc(), state="completed")
                unchanged()
                result_path = path / "result.json"
                require(result_path.is_file(), "Missing final result; inspect original partial/ownership evidence before resuming")
                result = json.loads(result_path.read_text()); plan = json.loads((path / "plan.json").read_text())
                require(plan["route"] == result["route"] == ROUTES[args.variant]
                        and result["workload_kind"] == "protocol-" + group
                        and result["plan_sha256"] == sha(path / "plan.json")
                        and plan["artifacts"][str(args.build)] == args.build_sha256
                        and plan["artifacts"][str(args.client_build)] == args.client_build_sha256,
                        "Actual cell producer/plan binding differs")
                qualifies = (completed.returncode == 0 and result.get("status") == "completed"
                             and result.get("valid") is True and result.get("service_standard_met") is True)
                resources = result.get("resources", {}).get("server", {})
                tail = result.get("histograms", {}).get("arrival_success", {}).get("percentiles_from_exact_samples_ns", {})
                business = result.get("independent_client", {})
                row.update(valid=result.get("valid", False), qualifies=qualifies, p99_ns=tail.get("p99"),
                           rss_peak_bytes=resources.get("rss_bytes_maximum"), cpu_percent_one_core=resources.get("cpu_percent_one_core"),
                           successes=result.get("successful"), offered=result.get("offered"), throughput=result.get("success_per_second"),
                           business_successes=business.get("business_successful_calls"), business_throughput=business.get("business_success_per_second"),
                           outcomes=result.get("outcome_counts"), invalid_reasons=result.get("invalid_reasons"),
                           result_sha256=sha(result_path), plan_sha256=sha(path / "plan.json"))
                checkpoint(); print(json.dumps(row), flush=True)
                return qualifies
            except BaseException as error:
                row.update(state="interrupted-or-failed", end_utc=utc(), error=type(error).__name__ + ": " + str(error)[:1000])
                checkpoint()
                raise

        checkpoint()
        try:
            low = high = None
            for rate in calibration["protocol_rates"]:
                if cell(rate): low = rate
                else: high = rate; break
            require(low is not None, "No passing low point; inspect fixture/environment without relaxing criteria")
            while high is None:
                rate = low * 2
                if not supported(rate, calibration["confirmation_seconds"]): break
                if cell(rate): low = rate
                else: high = rate
            while high is not None and high - low > max(1, low * .1):
                rate = (low + high) // 2
                if cell(rate, phase="refine"): low = rate
                else: high = rate
            for attempt in range(calibration["confirmation_attempt_limit"]):
                passed = [cell(low, seconds=60, phase=f"confirmation-{index}") for index in range(3)]
                if all(passed): break
                high = low; low = max(1, math.floor(low * .9))
                cell(low, phase="confirmation-step-down")
            else:
                raise RuntimeError("No consistently passing confirmation point; inspect generator/environment")
            unchanged(); receipt.update(state="completed", completed_utc=utc()); checkpoint()
            selection = {"group": group, "variant": args.variant, "route": ROUTES[args.variant],
                         "highest_consistently_passing_rate": low, "first_failing_bracket_rate": high,
                         "long_rate": max(1, min(500, math.floor(.8 * low))) if args.variant == "before" else None,
                         "concurrency": 64, "completed_utc": utc(), "policy_sha256": args.policy_sha256,
                         "controller_sha256": sha(output / "controller.json"), "profile_sha256": pins[str(profile_path)],
                         "build_sha256": args.build_sha256, "client_build_sha256": args.client_build_sha256,
                         "certificate": str(args.certificate), "private_key_local_only": str(args.private_key),
                         "higher_failed_points": [{key: row.get(key) for key in ("rate", "phase", "exit_code", "valid", "qualifies", "invalid_reasons")}
                                                  for row in rows if row["rate"] > low and not row.get("qualifies")],
                         "capacity_scope": "Largest consistently passing sampled offered rate; generator failures do not bound server capacity. An unbracketed result is only a measured lower bound.",
                         "long_rate_scope": "Only before selects paired long rates; after/direct capacity never retunes them."}
            save(output / "selection.json", selection); print(json.dumps(selection), flush=True)
        except BaseException as error:
            receipt.update(state="interrupted-or-failed", finished_utc=utc(), error=type(error).__name__ + ": " + str(error)[:1000])
            checkpoint()
            raise


if __name__ == "__main__":
    main()
