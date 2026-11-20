"""Freeze fixed-rate before-only DB noise from exactly three actual executions.

Post-run extraction only. Reuses the unchanged full-row comparator and observer
checks. No capacity selection is fabricated and no workload is started here.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parent
GROUPS = ("postgresql", "sqlite")
PARENT_SHA = "3a2efb983cbd8dfb98d4e0bfc65bc6b9a5ab937b0cc19a59b39fee9896e56fac"
NOTE = "Exclusive Perf-01 before-only anchor-noise; frozen service/database CPUs2,3 and generator CPUs0,1; physical-host controls unavailable"


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read(path):
    require(path.stat().st_size <= 64 * 1024**2, "Control record exceeds the existing bound")
    return json.loads(path.read_text())


def canonical(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def confined(root, value):
    value = Path(value)
    result = (value if value.is_absolute() else root / value).resolve()
    require(result.is_relative_to(root), "Path escapes the evidence root")
    return result


def fresh(root, value):
    value = Path(value)
    candidate = value if value.is_absolute() else root / value
    require(not os.path.lexists(candidate), "Never overwrite an evidence output")
    return confined(root, candidate)


def module(path, expected, name):
    require(sha(path) == expected, "Dependency source differs")
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def derived_argv(original, group, output):
    result = list(original)
    changes = {"--stage": "short", "--rate": str({"postgresql": 180, "sqlite": 50}[group]),
               "--seconds": "60", "--recovery-requests": "16", "--idle-seconds": "5",
               "--output": str(output), "--isolation-note": NOTE}
    for key, value in changes.items():
        require(result.count(key) == 1, "Original command has missing or repeated options")
        result[result.index(key) + 1] = value
    return result


def document_gate(root, doc, parent, contract):
    require(doc["status"] == "prepared-anchor-before-noise" and doc["parent_document_sha256"] == PARENT_SHA,
            "Wrong anchor preparation")
    for key in ("python", "working_directory", "driver_root_relative", "adopted_policy",
                "required_source_and_metadata_sha256", "required_runtime_artifact_sha256",
                "recorded_package_closure_from_progress"):
        require(doc[key] == parent[key], "A frozen source/runtime preparation field changed")
    require(contract["groups"]["postgresql"]["rate_per_second"] == 180 and
            contract["groups"]["sqlite"]["rate_per_second"] == 50 and len(doc["cells"]) == 6,
            "Keep the six predeclared anchor cells")
    outputs, logs = [], []
    for position, cell in enumerate(doc["cells"]):
        group, index = GROUPS[position // 3], position % 3
        require(cell["group"] == group and cell["index"] == index, "Anchor execution order changed")
        output = confined(root, cell["output"]); log = confined(root, cell["log"])
        require(cell["argv"] == derived_argv(parent["groups"][group]["commands"][0]["argv"], group, output),
                "Anchor command changes exceed the declared short-cell fields")
        outputs.append(output); logs.append(log)
    require(len(set(outputs + logs)) == 12 and all(not a.is_relative_to(b) for a in outputs for b in outputs if a != b),
            "Anchor output/log locations overlap")
    for group in GROUPS:
        expected = parent["groups"][group]["expected_frozen_source_files_sha256"]
        require(doc["expected_frozen_source_files_sha256"][group] == expected and
                canonical(expected) == contract["groups"][group]["frozen_source_map_sha256"], "Frozen driver map differs")


def context(root, document, document_sha256):
    require(sys.flags.optimize == 0 and os.sched_getaffinity(0) == {8}, "Use normal Python on CPU8")
    require("NW_PERF01_GC_CONFIG" not in os.environ, "Do not inherit a diagnostic GC scope")
    require(sha(document) == document_sha256, "Private anchor preparation differs")
    doc = read(document)
    parent_path = confined(root, doc["parent_document"])
    require(sha(parent_path) == PARENT_SHA, "Original completed-before preparation differs")
    contract_path = confined(root, doc["contract"])
    require(sha(contract_path) == doc["contract_sha256"], "Anchor contract differs")
    contract = read(contract_path); parent = read(parent_path)
    require(contract["parent_document_sha256"] == PARENT_SHA and
            sha(Path(__file__)) == contract["adapter_source_sha256"], "Adapter or parent identity differs")
    document_gate(root, doc, parent, contract)
    executable = Path(sys.executable).resolve(strict=True)
    require(executable == Path(doc["python"]["executable"]).resolve(strict=True) and
            ".".join(map(str, sys.version_info[:3])) == doc["python"]["version"] and
            sha(executable) == doc["python"]["recorded_executable_sha256"], "Actual Python differs")
    pins = {str(path): sha(path) for path in (document, parent_path, contract_path, Path(__file__).resolve())}
    for key in ("required_source_and_metadata_sha256", "required_runtime_artifact_sha256"):
        for name, expected in doc[key].items():
            path = confined(root, name)
            require(sha(path) == expected, "Original source/runtime input differs")
            pins[str(path)] = expected
    policy_path = confined(root, doc["adopted_policy"])
    require(sha(policy_path) == contract["adopted_policy_sha256"], "Adopted DB policy differs")
    policy = read(policy_path)
    comparison = module(BASE / "database_compare.py", policy["comparison_source_sha256"], "anchor_comparison")
    old_noise = module(BASE / "database_freeze_observer_noise.py", policy["noise_source_sha256"], "anchor_observer_inputs")
    controller = module(BASE / "database_observer_calibrate.py", policy["controller_source_sha256"], "anchor_adoption")
    verifier = module(BASE / "verify_db_observer_long.py", contract["driver_identity_source_sha256"], "anchor_source_identity")
    driver = confined(root, doc["driver_root_relative"])
    pins.update(verifier.driver_identity(driver, policy))
    pins.update(controller.require_adoption(policy, root))
    for group in GROUPS:
        verifier.frozen_sources(root, doc["expected_frozen_source_files_sha256"][group],
                                contract["groups"][group]["frozen_source_map_sha256"])
    for dependency in (comparison, old_noise, controller, verifier):
        pins[str(Path(dependency.__file__).resolve())] = sha(Path(dependency.__file__).resolve())
    publication_path = confined(root, doc["publication_readback"])
    publication = read(publication_path)
    require(re.fullmatch(r"[0-9a-f]{40}", publication["commit"]) is not None, "Missing fixed public commit")
    published = {row["path"]: row for row in publication["files"]}
    for name, expected in doc["required_public_files_sha256"].items():
        require(published[name]["matched"] is True and published[name]["sha256"] == expected,
                "Public source/contract byte readback is incomplete")
    pins[str(publication_path)] = sha(publication_path)
    return doc, contract, policy, driver, comparison, old_noise, controller, pins


def metadata_gate(group, summary, frozen, plan, target, contract, policy, expected_sources):
    point = contract["groups"][group]
    period = round(1e9 / point["rate_per_second"])
    count = math.ceil(contract["requested_seconds"] * 1e9 / period) + 1
    span_ns = (count - 1) * period
    require(contract["requested_seconds"] == 60 and contract["concurrency"] == 16 and
            point["period_ns"] == period and point["planned_operations"] == count and
            point["planned_first_to_last_schedule_ns"] == span_ns, "Anchor schedule formula differs")
    require(summary["provider"] == group and summary["variant"] == frozen["variant"] == "before" and
            summary["route"] == "nativeweave-aot-rust" and summary["scenario"] == "mixed" and
            summary["stage"] == frozen["stage"] == target["perf01"]["stage"] == "short" and
            summary["rate"] == point["rate_per_second"] and summary["concurrency"] == 16,
            "Actual anchor role/load differs")
    require(plan["timing"]["requests"] == target["requests"] == count and
            plan["timing"]["period_ns"] == period and
            summary["planned_load_seconds"] == frozen["planned_load_seconds"] == span_ns / 1e9 and
            plan["seed"] == 20261119 and plan["settings"]["warmup_requests"] == 16 and
            target["perf01"]["recovery_requests"] == 16 and target["perf01"]["idle_seconds"] == 5,
            "Actual anchor schedule/recovery/idle differs")
    require(plan["timing"]["max_dispatch_lag_ns"] == 100_000_000 and
            frozen["service_standard"] == {"max_unexpected_errors": 0, "max_p99_ms": 500.0,
                "max_app_rss_mib": 256.0, "max_generator_dispatch_lag_ms": 100} and
            summary["valid"] is True and summary["qualifies_service_standard"] is True and
            summary["duration_valid"] is True and not summary["invalid_reasons"], "Original anchor gates failed")
    require(frozen["driver_source"]["commit"] == policy["driver_commit"] and
            frozen["driver_source"]["scope_status"] == "" and frozen["source_files"] == expected_sources and
            frozen["route"]["source"]["commit"] == policy["before_runtime_commit"] and
            frozen["route"]["source"]["scope_status"] == "", "Actual driver/runtime identity differs")
    for key in ("scheduler_gc_policy", "resource_sampling_policy"):
        require(summary[key] == frozen[key] == plan["settings"]["features"][key] == target["perf01"][key] and
                summary[key + "_sha256"] == frozen[key + "_sha256"] == policy[key + "_sha256"] and
                canonical(summary[key]) == policy[key + "_sha256"], "Actual observer policy identity differs")


def target_file_gate(path, plan):
    original = str(Path(plan["oracle"]["dataset"]).parent / "target.json")
    require(sha(path / "target.json") == plan["routes"][0]["artifacts"][original],
            "Actual target differs from the hashed plan")


def triplet_gate(cells, signatures):
    require(len(cells) == len(signatures) == 3 and all(c["eligible"] and c["repetition"] == 0 and
            all(c["scopes"][key]["successful"] >= 100 for key in ("whole", "cycle", "page")) for c in cells),
            "Anchor cells are invalid, incomplete or undersampled")
    require(all(value == signatures[0] for value in signatures), "The three anchor configurations differ")
    require(len({(c["application_instance"]["pid"], c["application_instance"]["start_ticks"]) for c in cells}) == 3,
            "The three application instances are not independent")
    windows = sorted((c["measurement_window_ns"]["start"], c["measurement_window_ns"]["end"]) for c in cells)
    require(all(start < end for start, end in windows) and all(a[1] <= b[0] for a, b in zip(windows, windows[1:])),
            "Anchor measurement windows overlap or are empty")


def execution_gate(execution, doc, document_sha256, contract):
    require(execution["state"] == "completed" and execution["document_sha256"] == document_sha256 and
            execution["contract_sha256"] == doc["contract_sha256"] and
            execution["runner_source_sha256"] == contract["runner_source_sha256"] and
            len(execution["cells"]) == len(doc["cells"]) == 6, "Need the six actual completed anchor executions")
    last_end = None
    for expected, actual in zip(doc["cells"], execution["cells"], strict=True):
        require(all(actual[key] == expected[key] for key in ("group", "index", "output", "argv")) and
                actual["state"] == "completed" and actual["exit_code"] == 0 and
                actual["started_monotonic_ns"] < actual["ended_monotonic_ns"] and
                (last_end is None or last_end <= actual["started_monotonic_ns"]), "Execution identity, exit or ordering differs")
        last_end = actual["ended_monotonic_ns"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("root", "document", "execution", "output"):
        parser.add_argument("--" + key, type=Path, required=True)
    for key in ("document-sha256", "execution-sha256"):
        parser.add_argument("--" + key, required=True)
    parser.add_argument("--group", choices=GROUPS, required=True)
    parser.add_argument("--cells", type=Path, nargs=3, required=True)
    args = parser.parse_args(); root = args.root.resolve(strict=True)
    output = fresh(root, args.output); document = confined(root, args.document)
    doc, contract, policy, driver, comparison, old_noise, controller, inputs = context(root, document, args.document_sha256)
    require(output == confined(root, doc["noise_outputs"][args.group]), "Use the predeclared fresh noise output")
    execution_path = confined(root, args.execution)
    require(execution_path == confined(root, doc["execution_receipt"]) and sha(execution_path) == args.execution_sha256,
            "Actual execution receipt differs")
    execution = read(execution_path); execution_gate(execution, doc, args.document_sha256, contract)
    inputs[str(execution_path)] = args.execution_sha256
    selected = [(a, b) for a, b in zip(doc["cells"], execution["cells"], strict=True) if a["group"] == args.group]
    paths = [confined(root, value) for value in args.cells]
    require(paths == [confined(root, row[0]["output"]) for row in selected] and len(set(paths)) == 3,
            "Use exactly the three predeclared cells in their actual execution order")
    a21_path = driver / "src/Benchmarks.Harness/nativeweave_bench.py"
    a21 = module(a21_path, policy["driver_source_files_sha256"]["src/Benchmarks.Harness/nativeweave_bench.py"], "anchor_a21")
    reader = module(driver / "tests/Perf01/verify_long.py", policy["driver_source_files_sha256"]["tests/Perf01/verify_long.py"], "anchor_reader")
    gc = module(driver / "tests/Perf01.Database/scheduler_gc.py", policy["driver_source_files_sha256"]["tests/Perf01.Database/scheduler_gc.py"], "anchor_gc")
    sampling = controller.sampling_descriptor(driver, "threaded"); gc_policy = gc.policy("deferred")
    cells, signatures = [], []
    for path, (_, executed) in zip(paths, selected, strict=True):
        summary, frozen, plan, target = (read(path / name) for name in ("summary.json", "frozen-inputs.json", "plan.json", "target.json"))
        require(sha(path / "summary.json") == executed["summary_sha256"] and
                sha(path / "frozen-inputs.json") == executed["frozen_inputs_sha256"] == summary["frozen_inputs_sha256"] and
                sha(path / "plan.json") == frozen["plan_sha256"], "Actual execution/control hashes differ")
        target_file_gate(path, plan)
        metadata_gate(args.group, summary, frozen, plan, target, contract, policy, doc["expected_frozen_source_files_sha256"][args.group])
        require(summary["scheduler_gc_policy"] == gc_policy and summary["resource_sampling_policy"] == sampling,
                "Actual policy is not the pinned deferred/threaded descriptor")
        observed = summary["generator_resource_observer"]
        require(observed["status"] == "completed" and not observed["errors"] and not observed["identity_failures"] and
                observed["resource_sampling_policy"] == sampling and observed["interval_seconds"] == 1 and
                all(observed["samples"][role] > 0 for role in ("target", "scheduler", "controller")), "Observer did not complete")
        inputs.update(old_noise.observer_inputs(path, summary, observed["sha256"]))
        extra_path = confined(path, summary["perf01_receipt"]["path"])
        observer_path = confined(extra_path.parent, "generator-observer-receipt.json")
        require(read(observer_path) == {k: v for k, v in observed.items() if k not in ("path", "sha256")} and
                read(extra_path)["resource_sampling_policy"] == sampling, "Standalone observer receipt differs")
        gc_path, supervision_path = path / "observation.scheduler-gc.json", path / "supervision/receipt.json"
        require(confined(path, summary["scheduler_gc_receipt"]["path"]) == gc_path and
                sha(gc_path) == summary["scheduler_gc_receipt"]["sha256"] and summary["scheduler_gc_policy_valid"] is True and
                gc.valid_receipt(read(gc_path), gc_policy, read(supervision_path), frozen["plan_sha256"], frozen["source_files"]),
                "GC completion/restoration evidence differs")
        cell = comparison.read_cell(path, "before", a21, reader, sha(a21_path))
        cells.append(cell)
        signatures.append(dict(cell["configuration"], source_files=cell["driver_source_files"], route=cell["route_identity"]))
        inputs.update({str(path / name): value for name, value in cell["evidence_sha256"].items()})
        for source in (path / "target.json", gc_path, supervision_path, observer_path):
            inputs[str(source)] = sha(source)
    triplet_gate(cells, signatures)
    require(all(sha(Path(name)) == value for name, value in inputs.items()), "Anchor extraction input bytes changed")
    means = {key: [c["scopes"][scope]["mean_ns"] for c in cells]
             for key, scope in (("mixed", "whole"), ("cycle", "cycle"), ("page", "page"))}
    identity = canonical(inputs); rate = contract["groups"][args.group]["rate_per_second"]
    bands = {key: {"baseline_id": f"Perf-01/{args.group}/mixed/c16/{rate}/gc-deferred-threaded-anchor/{key}/{identity}",
                   "absolute_noise_ns": max(1000, max(values) - min(values)), "relative_noise": 0} for key, values in means.items()}
    result = {"task": "Perf-01", "created_utc": datetime.now(timezone.utc).isoformat(),
              "scope": "Before-only fixed anchor; independent of capacity selection and later comparison processes",
              "provider": args.group, "rate": rate, "concurrency": 16, "policy_sha256": policy["base_calibration_policy_sha256"],
              "database_amendment_sha256": contract["adopted_policy_sha256"], "anchor_contract_sha256": doc["contract_sha256"],
              "scheduler_gc_policy": gc_policy, "scheduler_gc_policy_sha256": policy["scheduler_gc_policy_sha256"],
              "resource_sampling_policy": sampling, "resource_sampling_policy_sha256": policy["resource_sampling_policy_sha256"],
              "process_means_ns": means, "bands": bands, "processes": cells, "configuration": signatures[0], "inputs_sha256": inputs}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False); stream.write("\n")
    print(json.dumps({"provider": args.group, "sha256": sha(output), "processes": 3, "workloads_executed": 0}))


if __name__ == "__main__":
    main()
