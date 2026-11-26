#!/usr/bin/env python3
"""Bind completed local mixed-load plans to the existing read-only analyzer."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def identity(path):
    path = path.resolve(strict=True)
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def option(argv, name, default=None):
    positions = [i for i, value in enumerate(argv) if value == name]
    if not positions:
        return default
    if len(positions) != 1 or positions[0] + 1 == len(argv):
        raise ValueError("Missing or duplicate option: " + name)
    return argv[positions[0] + 1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, action="append", required=True)
    parser.add_argument("--host-record", type=Path, required=True)
    parser.add_argument("--group-prefix", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a new index; existing evidence is never overwritten")
    host = identity(args.host_record)
    observations = []
    for directory in args.directory:
        directory = directory.resolve(strict=True)
        plan_path = directory / "plan.json"
        plan = json.loads(plan_path.read_text())
        if plan["lane"] not in ("calibration", "offered", "final"):
            raise ValueError("Not a mixed-load plan: " + str(plan_path))
        manifest = identity(Path(plan["inputs"]["manifest"]["path"]))
        if manifest != plan["inputs"]["manifest"]:
            raise ValueError("Manifest changed after plan generation")
        for command in plan["commands"]:
            if not command["timingRequested"]:
                continue
            argv = command["argv"]
            name, cohort = command["name"], command["cohort"]
            seconds = float(option(argv, "--seconds"))
            rate = float(option(argv, "--rate", 0))
            concurrency = int(option(argv, "--concurrency"))
            requested = {"seconds": seconds, "rate": rate, "concurrency": concurrency,
                         "rows": int(option(argv, "--rows")),
                         "batchRows": int(option(argv, "--batch-rows"))}
            if rate:
                requested["queueCapacity"] = int(option(argv, "--queue-capacity"))
            observations.append({
                "id": directory.name + "/" + name, "kind": "load", "cohort": cohort,
                "provider": plan["provider"],
                "comparisonGroup": f"{args.group_prefix}-{plan['lane']}-c{concurrency}-r{rate:g}",
                "host": "recorded-local-linux-x64", "instrumented": False,
                "final": plan["lane"] == "final" and cohort in ("candidate", "dapper"),
                "receipt": str(directory / (name + ".json")),
                "commandReceipt": str(directory / (name + ".command.json")),
                "resources": str(directory / (name + ".resources.jsonl")),
                "runnerReceipt": str(directory / "runner.json"), "planReceipt": str(plan_path),
                "workloadManifest": manifest["path"], "workloadManifestSha256": manifest["sha256"],
                "requested": requested,
            })
    if len({entry["id"] for entry in observations}) != len(observations):
        raise ValueError("Duplicate observation names")
    result = {
        "schemaVersion": 1,
        "scope": "Explicit local mixed-load invocation bindings. No execution, retry selection, threshold change or environment qualification. Final flags request analysis only; raw evidence decides completeness.",
        "hosts": {"recorded-local-linux-x64": {
            **host, "identityPointers": ["/uname/node", "/uname/machine", "/uname/release"],
            "scope": "Same recorded local environment; no exclusive physical host or visible cgroup quota claim."}},
        "observations": observations,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"index": str(args.output.resolve()), "observations": len(observations),
                      "measurementProcessesStarted": 0, "measurementReceiptsRead": 0}))


if __name__ == "__main__":
    main()
