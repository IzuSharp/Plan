"""Run the six source-frozen before-only anchor-noise commands serially.

Each unchanged command prefix owns one timing lock. A reset/exception may leave
an owned child running; only actual observed exits are recorded as completed.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import time


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--document", type=Path, required=True)
    parser.add_argument("--document-sha256", required=True)
    parser.add_argument("--source-sha256", required=True)
    args = parser.parse_args()
    root = args.root.resolve(strict=True); document = args.document.resolve(strict=True)
    if not document.is_relative_to(root) or sha(document) != args.document_sha256 or sha(Path(__file__)) != args.source_sha256:
        raise ValueError("Reviewed runner/document identity differs")
    doc = json.loads(document.read_text())
    contract_path = Path(doc["contract"])
    contract_path = (contract_path if contract_path.is_absolute() else root / contract_path).resolve(strict=True)
    if not contract_path.is_relative_to(root) or sha(contract_path) != doc["contract_sha256"]:
        raise ValueError("Reviewed contract identity differs")
    contract = json.loads(contract_path.read_text())
    adapter_path = Path(__file__).with_name("database_freeze_anchor_noise.py")
    if sha(adapter_path) != contract["adapter_source_sha256"] or args.source_sha256 != contract["runner_source_sha256"]:
        raise ValueError("Published runner/adapter source differs")
    spec = importlib.util.spec_from_file_location("anchor_run_preflight", adapter_path)
    adapter = importlib.util.module_from_spec(spec); spec.loader.exec_module(adapter)
    doc, contract, policy, _, _, _, _, inputs = adapter.context(root, document, args.document_sha256)
    receipt = adapter.fresh(root, doc["execution_receipt"])
    adapter.fresh(root, receipt.with_suffix(".tmp"))
    for cell in doc["cells"]:
        adapter.fresh(root, cell["output"]); adapter.fresh(root, cell["log"])
    adapter.require(shutil.disk_usage(root).free >= contract["minimum_free_disk_bytes"],
                    "Insufficient disk margin; no automatic cleanup is permitted")
    working = adapter.confined(root, doc["working_directory"])
    result = {"task": "Perf-01", "state": "running", "started_utc": utc(), "document_sha256": args.document_sha256,
              "contract_sha256": doc["contract_sha256"], "runner_source_sha256": args.source_sha256,
              "long_duration_credit_seconds": 0, "cells": []}
    receipt.parent.mkdir(parents=True, exist_ok=True); save(receipt, result)
    try:
        for expected in doc["cells"]:
            row = {k: expected[k] for k in ("group", "index", "output", "argv")}
            row.update(state="running", started_utc=utc(), started_monotonic_ns=time.monotonic_ns())
            result["cells"].append(row); save(receipt, result)
            log = adapter.confined(root, expected["log"]); log.parent.mkdir(parents=True, exist_ok=True)
            with log.open("xb") as stream:
                child = subprocess.Popen(expected["argv"], cwd=working, stdout=stream, stderr=subprocess.STDOUT)
                while child.poll() is None:
                    try:
                        child.wait(timeout=40)
                    except subprocess.TimeoutExpired:
                        print(json.dumps({"event": "anchor-running", "provider": expected["group"], "index": expected["index"],
                                          "elapsed_seconds": (time.monotonic_ns() - row["started_monotonic_ns"]) / 1e9}), flush=True)
            row.update(state="completed", exit_code=child.returncode, ended_utc=utc(),
                       ended_monotonic_ns=time.monotonic_ns(), log_sha256=sha(log))
            save(receipt, result)
            if child.returncode != 0:
                result.update(state="failed", finished_utc=utc()); save(receipt, result)
                return child.returncode or 1
            output = adapter.confined(root, expected["output"])
            summary, frozen, plan, target = (adapter.read(output / name) for name in
                                            ("summary.json", "frozen-inputs.json", "plan.json", "target.json"))
            adapter.metadata_gate(expected["group"], summary, frozen, plan, target, contract, policy,
                                  doc["expected_frozen_source_files_sha256"][expected["group"]])
            row.update(summary_sha256=sha(output / "summary.json"), frozen_inputs_sha256=sha(output / "frozen-inputs.json"))
            save(receipt, result)
        adapter.require(all(sha(Path(name)) == value for name, value in inputs.items()), "Execution preparation bytes changed")
        result.update(state="completed", finished_utc=utc(), ready_for_full_row_noise_extraction=True)
        save(receipt, result)
        print(json.dumps({"event": "anchor-cells-completed", "actual_exits": [r["exit_code"] for r in result["cells"]],
                          "long_duration_credit_seconds": 0}), flush=True)
        return 0
    except BaseException as error:
        result.update(state="interrupted-or-failed", finished_utc=utc(), error_type=type(error).__name__)
        save(receipt, result)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
