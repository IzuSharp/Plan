#!/usr/bin/env python3
"""Create one explicit six-input freeze; hashes/prepare only, no workload runs."""
import argparse
import copy
from pathlib import Path

import run_verified_mixed_cell as cell


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sqlite-rate", type=float, required=True)
    parser.add_argument("--postgresql-rate", type=float, required=True)
    parser.add_argument("--queue", type=int, default=64)
    parser.add_argument("--idle", type=int, default=5)
    parser.add_argument("--require-zero-rejections", action="store_true")
    args = parser.parse_args()
    output = cell.contained(args.output)
    cell.require(not output.exists() and not output.with_suffix(output.suffix + ".resume.json").exists(), "Freeze output must be fresh")
    output.parent.mkdir(parents=True, exist_ok=True)
    state_path = output.with_suffix(output.suffix + ".resume.json")
    state = {"task": "DB-Exec-Parity-01", "createdUtc": cell.utc(), "stage": "created", "completedInputs": [],
             "workloadExecuted": False, "finalCredit": False}
    cell.atomic(state_path, state)
    try:
        frozen = {"schemaVersion": 1, "task": "DB-Exec-Parity-01", "createdUtc": cell.utc(), "frozen": True,
                  "requireZeroRejections": args.require_zero_rejections, "inputs": {}, "allocationInputs": {}, "longCells": {},
                  "scope": "Explicit bytes and long-cell conditions; independently review campaign quietness/results; no automatic final credit", "finalCredit": False}
        shim = {"sha256": cell.sha(cell.SHIM), "bytes": cell.SHIM.stat().st_size}
        for provider in ("sqlite", "postgresql"):
            rate = getattr(args, provider + "_rate")
            settings = cell.conditions(provider, 1800, rate, args.queue, args.idle)
            request = argparse.Namespace(provider=provider, variant="before", kind="before-long", seconds=1800,
                                         rate=rate, queue=args.queue, idle=args.idle, concurrency=None, freeze=output)
            cell.validate_request(request)
            for variant in cell.VARIANTS:
                key = provider + "/" + variant
                state.update(stage="snapshot", currentInput=key, updatedUtc=cell.utc())
                cell.atomic(state_path, state)
                snapshot = cell.input_snapshot(provider, variant)
                frozen["inputs"][key] = snapshot
                diagnostic = copy.deepcopy(snapshot)
                diagnostic["identity"]["allocationDiagnostic"] = True
                diagnostic["identity"]["files"][str(cell.SHIM)] = shim
                diagnostic["identitySha256"] = cell.canonical_sha(diagnostic["identity"])
                frozen["allocationInputs"][key] = diagnostic
                kind = "before-long" if variant == "before" else "final-long"
                frozen["longCells"][kind + "/" + key] = {"conditions": settings, "inputIdentitySha256": snapshot["identitySha256"]}
                state["completedInputs"].append(key)
                cell.atomic(state_path, state)
        cell.atomic(output, frozen)
        state.update(stage="completed", passed=True, freezeSha256=cell.sha(output), updatedUtc=cell.utc())
        cell.atomic(state_path, state)
        print(str(output), flush=True)
        return 0
    except BaseException as error:
        state.update(stage="failed", passed=False, error={"type": type(error).__name__, "message": str(error)}, updatedUtc=cell.utc())
        cell.atomic(state_path, state)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
