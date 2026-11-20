"""Apply the unchanged long verifier plus the adopted DB observer contract.

Post-run only. The original verifier streams every operation once. These extra
checks read bounded control records and hash the original observer files; they
never replay a workload, waive an original failure, or alter source evidence.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    require(path.stat().st_size <= 64 * 1024**2, "Control record exceeds the existing bound")
    return json.loads(path.read_text())


def confined(root, value):
    value = Path(value)
    path = (value if value.is_absolute() else root / value).resolve()
    require(path.is_relative_to(root), "Path escapes its declared evidence root")
    return path


def module(path, expected, name):
    require(sha(path) == expected, "Post-run dependency source differs")
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def driver_identity(driver, policy):
    require(subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=driver, text=True).strip() == policy["driver_commit"],
            "Measurement driver commit differs")
    require(subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=driver, text=True).strip() == policy["driver_tree"],
            "Measurement driver full tree differs")
    require(not subprocess.check_output(["git", "status", "--porcelain"], cwd=driver), "Measurement driver tree is dirty")
    sources = {str(confined(driver, name)): value for name, value in policy["driver_source_files_sha256"].items()}
    require(all(sha(Path(path)) == value for path, value in sources.items()), "Measurement driver input source differs")
    return sources


def frozen_sources(root, values, expected):
    identity = hashlib.sha256(json.dumps(values, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    require(identity == expected, "Complete frozen source/toolchain map differs")
    taskset = Path(shutil.which("taskset")).resolve(strict=True)
    for path, value in values.items():
        candidate = Path(path).resolve(strict=True)
        require(candidate.is_relative_to(root) or candidate == taskset, "Frozen source path is outside approved roots")
        require(sha(candidate) == value, "Frozen source/toolchain bytes differ")


def policy_gate(group, root, output, driver, policy, amendment, controller, noise_reader):
    expected = amendment["groups"][group]
    summary, frozen, plan, target = (read(output / name) for name in
                                    ("summary.json", "frozen-inputs.json", "plan.json", "target.json"))
    require(sha(output / "frozen-inputs.json") == summary["frozen_inputs_sha256"] and
            sha(output / "plan.json") == frozen["plan_sha256"], "Actual DB plan/control bytes differ")
    require(summary["valid"] is True and summary["qualifies_service_standard"] is True and
            summary["duration_valid"] is True and not summary["invalid_reasons"], "Original database gates did not pass")
    require(summary["provider"] == group and summary["route"] == "nativeweave-aot-rust" and
            summary["variant"] == "before" and summary["scenario"] == "mixed" and summary["stage"] == "soak" and
            summary["rate"] == expected["rate_per_second"] and summary["concurrency"] == 16,
            "Actual long workload differs")
    require(frozen["planned_load_seconds"] == 1802 and plan["timing"]["requests"] == expected["planned_operations"] and
            plan["timing"]["period_ns"] == expected["period_ns"] and
            plan["timing"]["max_dispatch_lag_ns"] == 100_000_000 and
            plan["settings"]["warmup_requests"] == 16 and
            target["perf01"]["recovery_requests"] == 32 and target["perf01"]["idle_seconds"] == 60,
            "Actual long schedule/recovery/idle policy differs")
    require(frozen["driver_source"]["commit"] == policy["driver_commit"] and
            frozen["driver_source"]["scope_status"] == "" and
            frozen["route"]["source"]["commit"] == policy["before_runtime_commit"] and
            frozen["route"]["source"]["scope_status"] == "", "Actual runtime/driver source differs")
    sources = driver_identity(driver, policy)
    frozen_sources(root, frozen["source_files"], expected["frozen_source_map_sha256"])
    gc_driver = module(driver / "tests/Perf01.Database/scheduler_gc.py",
                       policy["driver_source_files_sha256"]["tests/Perf01.Database/scheduler_gc.py"], "long_observer_gc")
    gc_policy = gc_driver.policy("deferred")
    sampling = controller.sampling_descriptor(driver, "threaded")
    for key, value in (("scheduler_gc_policy", gc_policy), ("resource_sampling_policy", sampling)):
        digest = gc_driver.policy_sha256(value)
        require(summary[key] == frozen[key] == plan["settings"]["features"][key] == target["perf01"][key] == value and
                summary[key + "_sha256"] == frozen[key + "_sha256"] == policy[key + "_sha256"] == digest,
                "Actual explicit observer/GC policy differs")
    gc_path = confined(output, summary["scheduler_gc_receipt"]["path"])
    supervision_path = confined(output, "supervision/receipt.json")
    require(gc_path == output / "observation.scheduler-gc.json" and
            sha(gc_path) == summary["scheduler_gc_receipt"]["sha256"] and
            summary["scheduler_gc_policy_valid"] is True and
            gc_driver.valid_receipt(read(gc_path), gc_policy, read(supervision_path), frozen["plan_sha256"], frozen["source_files"]),
            "Scheduler did not complete with the original GC state restored")
    observed = summary["generator_resource_observer"]
    require(observed["status"] == "completed" and not observed["errors"] and not observed["identity_failures"] and
            observed["resource_sampling_policy"] == sampling and observed["interval_seconds"] == 1 and
            all(observed["samples"][role] > 0 for role in ("target", "scheduler", "controller")),
            "Threaded generator observer did not complete normally")
    pins = noise_reader.observer_inputs(output, summary, observed["sha256"])
    extra_path = confined(output, summary["perf01_receipt"]["path"])
    extra = read(extra_path)
    observer_path = confined(extra_path.parent, "generator-observer-receipt.json")
    require(read(observer_path) == {key: value for key, value in observed.items() if key not in ("path", "sha256")} and
            extra["resource_sampling_policy"] == sampling, "Standalone observer completion receipt differs")
    for path in (output / "summary.json", output / "frozen-inputs.json", output / "plan.json", output / "target.json",
                 gc_path, supervision_path, observer_path):
        pins[str(path)] = sha(path)
    pins.update(sources)
    require(all(sha(Path(path)) == value for path, value in pins.items()), "Observer verification inputs changed")
    return {"passed": True, "scheduler_gc_restored": True, "threaded_observer_completed": True,
            "threaded_join_scope": "completed-pinned-implementation-contract", "inputs_sha256": pins}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "nativeweave", "policy", "amendment", "output", "receipt"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("amendment-sha256", "source-sha256"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--group", choices=("postgresql", "sqlite"), required=True)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    require(os.sched_getaffinity(0) == {8}, "Post-run verification belongs on CPU8")
    receipt_candidate = args.receipt if args.receipt.is_absolute() else root / args.receipt
    require(not os.path.lexists(receipt_candidate), "Never overwrite a verification receipt")
    output, receipt_path, driver, policy_path, amendment_path = (confined(root, value) for value in
        (args.output, args.receipt, args.nativeweave, args.policy, args.amendment))
    require(sha(amendment_path) == args.amendment_sha256, "Long amendment differs")
    amendment = read(amendment_path)
    require(sha(Path(__file__).resolve()) == args.source_sha256 == amendment["verifier_wrapper_sha256"], "Verifier wrapper differs")
    require(sha(policy_path) == amendment["adopted_policy_sha256"], "Adopted observer contract differs")
    policy = read(policy_path)
    driver_identity(driver, policy)
    base = Path(__file__).resolve().parent
    controller = module(base / "database_observer_calibrate.py", policy["controller_source_sha256"], "long_observer_controller")
    noise_reader = module(base / "database_freeze_observer_noise.py", policy["noise_source_sha256"], "long_observer_noise_reader")
    controller.require_adoption(policy, root)
    original = module(driver / "tests/Perf01/verify_long.py", amendment["original_verifier_sha256"], "long_observer_original_verifier")
    result = original.verify(args.group, output)
    result.update(original_verifier_accepted=result["accepted"], observer_verifier_sha256=args.source_sha256,
                  long_amendment_sha256=args.amendment_sha256, adopted_policy_sha256=amendment["adopted_policy_sha256"],
                  observer_contract={"passed": False})
    try:
        result["observer_contract"] = policy_gate(args.group, root, output, driver, policy, amendment, controller, noise_reader)
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError, OverflowError, subprocess.SubprocessError) as error:
        result["failure_reasons"].append(type(error).__name__ + ": " + str(error))
    result["accepted"] = result["original_verifier_accepted"] and result["observer_contract"]["passed"]
    if not result["accepted"]:
        result["duration_credit_seconds"] = 0
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    with receipt_path.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True); stream.write("\n")
    print(json.dumps({key: result[key] for key in ("accepted", "group", "duration_credit_seconds", "failure_reasons")}))
    return 0 if result["accepted"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
