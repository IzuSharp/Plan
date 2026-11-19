#!/usr/bin/env python3
"""Freeze DB before noise from the three final existing calibration confirmations.

Derived from the v5 freeze-noise.sh recipe. Reuses database_compare's unchanged
full-row reader; never starts a load or treats noise processes as comparisons.
"""
import argparse
import importlib.util
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path



def read(path):
    return json.loads(path.read_text())


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def confined(root, value):
    value = Path(value)
    path = (value if value.is_absolute() else root / value).resolve()
    require(path.is_relative_to(root), "Noise input/output path escapes the workspace root")
    return path


def checked_module(path, expected, name):
    require(sha(path) == expected, "Noise reporting dependency changed")
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def observer_inputs(cell_root, summary, expected_resource_sha256):
    receipt_path = confined(cell_root, summary["perf01_receipt"]["path"])
    require(sha(receipt_path) == summary["perf01_receipt"]["sha256"],
            "Actual Perf-01 receipt differs from the confirmation summary")
    observed = summary["generator_resource_observer"]
    require(read(receipt_path)["generator_resource_observer"] == observed,
            "Actual resource observer differs from the confirmation summary")
    resources_path = confined(receipt_path.parent, observed["path"])
    require(sha(resources_path) == observed["sha256"] == expected_resource_sha256,
            "Actual generator resource bytes differ from the confirmation")
    return {str(receipt_path): summary["perf01_receipt"]["sha256"],
            str(resources_path): observed["sha256"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("root", "nativeweave", "database-amendment", "calibration", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("database-amendment-sha256", "selection-sha256", "controller-sha256", "source-sha256", "comparison-source-sha256"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    product, calibration, destination = (confined(root, value) for value in (args.nativeweave, args.calibration, args.output))
    require(not destination.exists(), "Never overwrite an existing noise receipt")
    amendment_path = confined(root, args.database_amendment)
    require(sha(amendment_path) == args.database_amendment_sha256, "DB amendment identity differs")
    amendment = read(amendment_path)
    require(sha(Path(__file__).resolve()) == args.source_sha256 == amendment["noise_source_sha256"], "Noise source differs")
    require(args.comparison_source_sha256 == amendment["comparison_source_sha256"], "Comparison source differs from the adopted contract")
    comparison = checked_module(confined(root, Path(__file__).with_name("database_compare.py")), args.comparison_source_sha256, "observer_noise_comparison")
    controller_source = checked_module(confined(root, Path(__file__).with_name("database_observer_calibrate.py")), amendment["controller_source_sha256"], "observer_noise_controller")
    pair_inputs = controller_source.require_adoption(amendment, root)
    require(sha(Path(__file__).resolve()) == args.source_sha256 and
            sha(Path(comparison.__file__).resolve()) == args.comparison_source_sha256, "Noise/read source differs")
    sources = {str(controller_source.confined(product, name)): digest for name, digest in amendment["driver_source_files_sha256"].items()}
    require(all(sha(Path(path)) == digest for path, digest in sources.items()), "DB driver/wrapper source differs")
    a21_path, reader_path = product / "src/Benchmarks.Harness/nativeweave_bench.py", product / "tests/Perf01/verify_long.py"
    a21 = comparison.module(a21_path, "perf01_noise_a21")
    reader = comparison.module(reader_path, "perf01_noise_reader")
    gc_driver = comparison.module(product / "tests/Perf01.Database/scheduler_gc.py", "perf01_noise_gc_receipt")
    selected_policy = gc_driver.policy("deferred")
    require(selected_policy["mode"] == amendment["scheduler_gc_mode"] and
            gc_driver.policy_sha256(selected_policy) == amendment["scheduler_gc_policy_sha256"], "Wrong noise GC policy")
    sampling_policy = controller_source.sampling_descriptor(product, "threaded")
    require(sampling_policy["mode"] == amendment["resource_sampling_mode"] and
            gc_driver.policy_sha256(sampling_policy) == amendment["resource_sampling_policy_sha256"], "Wrong noise resource-sampling policy")
    selection_path, controller_path = calibration / "selection.json", calibration / "controller.json"
    require(sha(selection_path) == args.selection_sha256 and sha(controller_path) == args.controller_sha256,
            "Use exact completed selection/controller hashes")
    selection, controller = read(selection_path), read(controller_path)
    require(selection["controller_sha256"] == args.controller_sha256 and controller["state"] == "completed" and
            selection["variant"] == controller["variant"] == "before", "Need a completed before-only calibration")
    require(controller["script_sha256"] == amendment["controller_source_sha256"] and
            selection["group"] == controller["group"] and selection["group"] in ("postgresql", "sqlite"),
            "Actual calibration controller source/provider differs")
    for value in (selection, controller):
        require(value["database_amendment_sha256"] == args.database_amendment_sha256 and
                value["scheduler_gc_policy"] == selected_policy and
                value["scheduler_gc_policy_sha256"] == amendment["scheduler_gc_policy_sha256"] and
                value["policy_sha256"] == amendment["base_calibration_policy_sha256"], "Calibration policy identity differs")
        require(value["resource_sampling_policy"] == sampling_policy and
                value["resource_sampling_policy_sha256"] == amendment["resource_sampling_policy_sha256"],
                "Calibration resource-sampling identity differs")
    require(controller["driver_source_sha256"] == sources, "Controller driver pins differ")
    triplet = controller["cells"][-3:]
    require([row["phase"] for row in triplet] == ["confirmation-0", "confirmation-1", "confirmation-2"],
            "Use all three final confirmations, never a favorable subset")
    inputs = {str(path): sha(path) for path in (selection_path, controller_path, amendment_path,
              Path(__file__).resolve(), Path(comparison.__file__).resolve(), Path(controller_source.__file__).resolve(), a21_path, reader_path)}
    inputs.update(sources)
    inputs.update(pair_inputs)
    cells, signatures = [], []
    for row in triplet:
        require(row["state"] == "completed" and row["exit_code"] == 0 and row["valid"] and row["qualifies"] and
                row["seconds"] == 60 and row["rate"] == selection["highest_consistently_passing_rate"],
                "Each exact final confirmation must pass its original gates")
        root = controller_source.confined(args.root, row["directory"])
        require(sha(root / "summary.json") == row["summary_sha256"] and
                sha(root / "frozen-inputs.json") == row["frozen_inputs_sha256"], "Confirmation receipt identity differs")
        summary, frozen, plan = (read(root / name) for name in ("summary.json", "frozen-inputs.json", "plan.json"))
        require(summary["provider"] == selection["group"] and summary["scenario"] == "mixed" and
                summary["concurrency"] == 16 and summary["rate"] == row["rate"], "Confirmation load differs")
        require(frozen["driver_source"]["commit"] == amendment["driver_commit"] and frozen["driver_source"]["scope_status"] == "" and
                frozen["route"]["source"]["commit"] == amendment["before_runtime_commit"], "Actual before/driver source differs")
        require(summary["scheduler_gc_policy"] == frozen["scheduler_gc_policy"] ==
                plan["settings"]["features"]["scheduler_gc_policy"] == selected_policy and
                summary["scheduler_gc_policy_sha256"] == frozen["scheduler_gc_policy_sha256"] ==
                amendment["scheduler_gc_policy_sha256"], "Actual confirmation policy identity differs")
        require(summary["resource_sampling_policy"] == frozen["resource_sampling_policy"] ==
                plan["settings"]["features"]["resource_sampling_policy"] == sampling_policy and
                summary["resource_sampling_policy_sha256"] == frozen["resource_sampling_policy_sha256"] ==
                row["resource_sampling_policy_sha256"] == amendment["resource_sampling_policy_sha256"],
                "Actual confirmation resource-sampling identity differs")
        observed = summary["generator_resource_observer"]
        require(observed["status"] == "completed" and not observed["errors"] and not observed["identity_failures"]
                and observed["resource_sampling_policy"] == sampling_policy
                and observed["sha256"] == row["generator_resources_sha256"], "Confirmation resource observer did not complete")
        inputs.update(observer_inputs(root, summary, row["generator_resources_sha256"]))
        gc_path, supervision_path = root / "observation.scheduler-gc.json", root / "supervision/receipt.json"
        require(Path(summary["scheduler_gc_receipt"]["path"]).resolve() == gc_path and
                sha(gc_path) == summary["scheduler_gc_receipt"]["sha256"] == row["scheduler_gc_receipt_sha256"] and
                summary["scheduler_gc_policy_valid"] is True and gc_driver.valid_receipt(
                    read(gc_path), selected_policy, read(supervision_path), frozen["plan_sha256"], frozen["source_files"]),
                "Actual policy receipt is missing, interrupted or inconsistent")
        cell = comparison.read_cell(root, "before", a21, reader, sha(a21_path))
        require(cell["eligible"] and all(cell["scopes"][key]["successful"] >= 100 for key in ("whole", "cycle", "page")),
                "Noise confirmation is invalid or lacks samples")
        signature = dict(cell["configuration"], source_files=cell["driver_source_files"], route=cell["route_identity"])
        signatures.append(signature); cells.append(cell)
        inputs.update({str(root / name): digest for name, digest in cell["evidence_sha256"].items()})
        inputs.update({str(gc_path): sha(gc_path), str(supervision_path): sha(supervision_path)})
    require(all(value == signatures[0] for value in signatures), "Noise process configurations differ")
    require(len({(row["application_instance"]["pid"], row["application_instance"]["start_ticks"]) for row in cells}) == 3,
            "Noise needs three independent application instances")
    windows = sorted((row["measurement_window_ns"]["start"], row["measurement_window_ns"]["end"]) for row in cells)
    require(all(left[1] <= right[0] for left, right in zip(windows, windows[1:])), "Noise windows overlap")
    require(all(sha(Path(path)) == digest for path, digest in inputs.items()), "Noise inputs changed while extracting")
    means = {key: [row["scopes"][scope]["mean_ns"] for row in cells]
             for key, scope in (("mixed", "whole"), ("cycle", "cycle"), ("page", "page"))}
    identity = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    bands = {key: {"baseline_id": f"Perf-01/{selection['group']}/mixed/c16/{selection['highest_consistently_passing_rate']}/gc-deferred-threaded/{key}/{identity}",
                   "absolute_noise_ns": max(1000, max(values) - min(values)), "relative_noise": 0} for key, values in means.items()}
    receipt = {"task": "Perf-01", "created_utc": datetime.now(timezone.utc).isoformat(),
               "scope": "Before-only mixed anchor and conditional cycle/page slices; original v5 process-mean range rule",
               "provider": selection["group"], "rate": selection["highest_consistently_passing_rate"], "concurrency": 16,
               "policy_sha256": amendment["base_calibration_policy_sha256"], "database_amendment_sha256": args.database_amendment_sha256,
               "scheduler_gc_policy": selected_policy, "scheduler_gc_policy_sha256": amendment["scheduler_gc_policy_sha256"],
               "resource_sampling_policy": sampling_policy, "resource_sampling_policy_sha256": amendment["resource_sampling_policy_sha256"],
               "process_means_ns": means, "bands": bands, "processes": cells, "configuration": signatures[0], "inputs_sha256": inputs}
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True); stream.write("\n")
    print(json.dumps({"output": str(destination), "sha256": sha(destination), "load_executed": False}))


if __name__ == "__main__":
    main()
