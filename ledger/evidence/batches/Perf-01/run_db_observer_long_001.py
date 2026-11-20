"""Run one reviewed DB long cell and its original-plus-observer verifier.

The exact machine command document stays private. Each child command owns one
nonblocking timing lock; this supervisor never nests another flock around it.
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time


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
    require(path.is_relative_to(root), "Path escapes the declared workspace root")
    return path


def fresh(root, value):
    value = Path(value)
    candidate = value if value.is_absolute() else root / value
    require(not os.path.lexists(candidate), "Never reuse an existing output, receipt or log path")
    return confined(root, candidate)


def module(path, expected, name):
    require(sha(path) == expected, "Supervisor dependency source differs")
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def qualification(root, doc, amendment, policy):
    calibration_path = confined(root, doc["calibration_execution"])
    noise_path = confined(root, doc["noise_execution"])
    require(sha(calibration_path) == amendment["calibration_execution_sha256"] and
            sha(noise_path) == amendment["noise_execution_sha256"], "Actual qualification execution differs")
    calibration, noise_execution = read(calibration_path), read(noise_path)
    require(calibration["state"] == "calibration-completed-noise-pending" and
            calibration["document_sha256"] == amendment["calibration_configuration_sha256"] and
            calibration["supervisor_source_sha256"] == policy["supervisor_source_sha256"] and
            len(calibration["commands"]) == 2 and all(row["state"] == "completed" and row["exit_code"] == 0 and
            row["selection_gate_passed"] is True for row in calibration["commands"]), "Calibration did not complete its original gates")
    require(noise_execution["state"] == "completed" and noise_execution["load_executed"] is False and
            len(noise_execution["commands"]) == 2 and all(row["state"] == "completed" and row["exit_code"] == 0
            for row in noise_execution["commands"]), "Actual before noise did not complete")
    for provider, group in doc["groups"].items():
        expected = amendment["groups"][provider]
        values = {}
        for name in ("selection", "controller", "noise"):
            path = confined(root, group[name])
            require(sha(path) == expected[name + "_sha256"], "Actual selected qualification bytes differ")
            values[name] = read(path)
        selection, controller, noise = (values[name] for name in ("selection", "controller", "noise"))
        actual_calibration = next(row for row in calibration["commands"] if row["id"] == group["calibration_command_id"])
        actual_noise = next(row for row in noise_execution["commands"] if row["provider"] == provider)
        require(actual_calibration["selection_sha256"] == expected["selection_sha256"] and
                actual_calibration["controller_sha256"] == expected["controller_sha256"] and
                actual_noise["output_sha256"] == expected["noise_sha256"], "Qualification output linkage differs")
        require(controller["state"] == "completed" and controller["script_sha256"] == policy["controller_source_sha256"] and
                selection["controller_sha256"] == expected["controller_sha256"] and
                selection["fixed_long_rate_within_confirmed_capacity"] is True and
                selection["long_rate"] == expected["rate_per_second"] and
                selection["highest_consistently_passing_rate"] == noise["rate"] == expected["confirmed_capacity_per_second"] and
                noise["provider"] == provider and noise["concurrency"] == 16, "Qualification does not support the fixed long rate")
        for value in (selection, controller, noise):
            require(value["database_amendment_sha256"] == amendment["adopted_policy_sha256"] and
                    value["scheduler_gc_policy_sha256"] == policy["scheduler_gc_policy_sha256"] and
                    value["resource_sampling_policy_sha256"] == policy["resource_sampling_policy_sha256"], "Qualification policy differs")
        triplet = controller["cells"][-3:]
        require([row["phase"] for row in triplet] == ["confirmation-0", "confirmation-1", "confirmation-2"] and
                all(row["state"] == "completed" and row["exit_code"] == 0 and row["valid"] is True and
                    row["qualifies"] is True and row["seconds"] == 60 and
                    row["rate"] == expected["confirmed_capacity_per_second"] for row in triplet),
                "Entire final fresh confirmation triplet must pass")
        require(len(noise["processes"]) == 3 and all(row["eligible"] is True for row in noise["processes"]),
                "Before noise does not contain three eligible processes")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "document"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("document-sha256", "source-sha256"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--group", choices=("postgresql", "sqlite"), required=True)
    args = parser.parse_args()
    require(sys.flags.optimize == 0 and os.sched_getaffinity(0) == {8}, "Supervisor requires normal Python on CPU8")
    require("NW_PERF01_GC_CONFIG" not in os.environ, "Do not inherit a scheduler GC wrapper scope")
    require(sha(Path(__file__).resolve()) == args.source_sha256, "Supervisor source differs")
    root = args.root.resolve(strict=True)
    document = confined(root, args.document)
    require(sha(document) == args.document_sha256, "Private command document differs")
    doc = read(document)
    require(doc["status"] == "prepared-current-observer-long", "Wrong private long document")
    python = Path(sys.executable).resolve(strict=True)
    require(python == Path(doc["python"]["executable"]).resolve(strict=True) and
            ".".join(map(str, sys.version_info[:3])) == doc["python"]["version"] and
            sha(python) == doc["python"]["recorded_executable_sha256"], "Actual Python differs")
    for path, expected in doc["required_source_and_metadata_sha256"].items():
        require(sha(confined(root, path)) == expected, "Source or metadata input differs")
    for path, expected in doc["required_runtime_artifact_sha256"].items():
        require(sha(confined(root, path)) == expected, "Runtime package/application artifact differs")
    amendment_path = confined(root, doc["amendment"])
    require(sha(amendment_path) == doc["amendment_sha256"], "Long amendment differs")
    amendment = read(amendment_path)
    require(args.source_sha256 == amendment["supervisor_sha256"], "Wrong published supervisor")
    policy_path = confined(root, doc["adopted_policy"])
    require(sha(policy_path) == amendment["adopted_policy_sha256"], "Adopted DB policy differs")
    policy = read(policy_path)
    publication = read(confined(root, doc["publication_readback"]))
    require(re.fullmatch(r"[0-9a-f]{40}", publication["commit"]) is not None, "Missing fixed publication commit")
    published = {row["path"]: row for row in publication["files"]}
    for path, expected in doc["required_public_files_sha256"].items():
        require(published[path]["matched"] is True and published[path]["sha256"] == expected,
                "Public runtime source/contract byte readback is incomplete")
    base = Path(__file__).resolve().parent
    controller = module(base / "database_observer_calibrate.py", policy["controller_source_sha256"], "long_preflight_controller")
    controller.require_adoption(policy, root)
    verifier = module(base / "verify_db_observer_long.py", amendment["verifier_wrapper_sha256"], "long_preflight_verifier")
    driver = confined(root, doc["driver_root_relative"])
    verifier.driver_identity(driver, policy)
    qualification(root, doc, amendment, policy)
    group = doc["groups"][args.group]
    verifier.frozen_sources(root, group["expected_frozen_source_files_sha256"],
                            amendment["groups"][args.group]["frozen_source_map_sha256"])
    require(len(group["commands"]) == 2, "Each group has exactly one driver and one post-run verifier")
    output = fresh(root, group["output"])
    verification = fresh(root, group["verification"])
    receipt_path = fresh(root, group["execution_receipt"])
    fresh(root, receipt_path.with_suffix(".tmp"))
    working_directory = confined(root, doc["working_directory"])
    for command in group["commands"]:
        fresh(root, command["log"])
    free_bytes = shutil.disk_usage(root).free
    require(free_bytes >= amendment["minimum_free_disk_bytes"][args.group], "Insufficient disk margin; no automatic cleanup is permitted")
    result = {"task": "Perf-01", "group": args.group, "variant": "before", "state": "running", "started_utc": utc(),
              "document_sha256": args.document_sha256, "supervisor_source_sha256": args.source_sha256,
              "amendment_sha256": doc["amendment_sha256"], "published_commit": publication["commit"],
              "output": str(output), "verification": str(verification), "free_disk_bytes_before": free_bytes,
              "commands": [], "long_duration_credit_seconds": 0}
    save(receipt_path, result)
    for command in group["commands"]:
        log = confined(root, command["log"])
        entry = {"id": command["id"], "argv": command["argv"], "started_utc": utc(), "state": "running", "log": str(log)}
        result["commands"].append(entry)
        save(receipt_path, result)
        started = time.monotonic()
        with log.open("xb") as stream:
            child = subprocess.Popen(command["argv"], cwd=working_directory, stdout=stream, stderr=subprocess.STDOUT)
            entry["pid"] = child.pid
            save(receipt_path, result)
            while child.poll() is None:
                try:
                    child.wait(timeout=40)
                except subprocess.TimeoutExpired:
                    print(json.dumps({"event": "supervision", "group": args.group, "command": command["id"],
                                      "utc": utc(), "elapsed_seconds": time.monotonic() - started}), flush=True)
        entry.update(state="completed", exit_code=child.returncode, ended_utc=utc(),
                     elapsed_seconds=time.monotonic() - started, log_sha256=sha(log))
        save(receipt_path, result)
        if child.returncode != 0:
            result.update(state="failed", ended_utc=utc(), failed_command=command["id"])
            save(receipt_path, result)
            return child.returncode or 1
    actual = read(verification)
    require(actual["accepted"] is True and actual["original_verifier_accepted"] is True and
            actual["observer_contract"]["passed"] is True and actual["duration_credit_seconds"] >= 1800 and
            actual["long_amendment_sha256"] == doc["amendment_sha256"] and
            actual["observer_verifier_sha256"] == amendment["verifier_wrapper_sha256"], "Combined long verification did not pass")
    result.update(state="completed", ended_utc=utc(), accepted=True, verification_sha256=sha(verification),
                  long_duration_credit_seconds=actual["duration_credit_seconds"])
    save(receipt_path, result)
    print(json.dumps({"event": "group-accepted", "group": args.group,
                      "duration_credit_seconds": result["long_duration_credit_seconds"]}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
