#!/usr/bin/env python3
"""Register the fixed 18 ordinary phase filenames; never reads or runs a consumer.

Run the analyzer only after both directories have finished. Missing entries
remain in this index and become explicit missing observations in its report.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measurements-root", required=True, type=Path)
    parser.add_argument("--sqlite-directory", type=Path)
    parser.add_argument("--postgresql-directory", type=Path)
    parser.add_argument("--host-record", type=Path)
    parser.add_argument("--host-pointer", action="append", help="Stable recorded identity JSON Pointer; defaults to /uname/node, /uname/machine, /uname/release")
    parser.add_argument("--comparison-group", default="ordinary-phases-01")
    parser.add_argument("--iterations", type=int, default=256)
    parser.add_argument("--windows", type=int, default=3)
    parser.add_argument("--instrumented", action="store_true", help="Register diagnostics explicitly without timing credit")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a new index path; prior evidence is never overwritten")
    if args.iterations < 1 or args.windows < 1:
        parser.error("Positive iterations and windows are required")
    base = args.measurements_root.resolve()
    directories = {"sqlite": (args.sqlite_directory or base / "phases-sqlite-01").resolve(),
                   "postgresql": (args.postgresql_directory or base / "phases-postgresql-01").resolve()}
    host = (args.host_record or base / "host-before-phases.json").resolve()
    entries = []
    for provider, cohort, rows in itertools.product(directories, ("before", "candidate", "dapper"), (1, 100, 1000)):
        directory = directories[provider]
        name = f"{cohort}-rows{rows}"
        entries.append({"id": f"{provider}-{name}", "kind": "phase", "cohort": cohort,
            "provider": provider, "rows": rows, "comparisonGroup": args.comparison_group,
            "host": "recorded-local-linux-x64", "instrumented": args.instrumented, "final": False,
            "receipt": str(directory / (name + ".json")),
            "commandReceipt": str(directory / (name + ".command.json")),
            "resources": str(directory / (name + ".resources.jsonl")),
            "runnerReceipt": str(directory / "runner.json"), "planReceipt": str(directory / "plan.json"),
            "requested": {"iterations": args.iterations, "windows": args.windows, "rows": rows}})
    value = {"schemaVersion": 1,
        "scope": "Explicit ordinary same-host phase filenames; no auto-selected retries, historical acceptance, or cgroup qualification. The index's instrumentation statement is an invocation declaration; actual commands/producer flags are checked by the analyzer.",
        "hosts": {"recorded-local-linux-x64": {"path": str(host),
            "identityPointers": args.host_pointer or ["/uname/node", "/uname/machine", "/uname/release"],
            "scope": "Same recorded local environment; no claim of exclusive physical hardware or observable cgroup quota."}},
        "observations": entries}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"index": str(args.output.resolve()), "expectedPhaseReceipts": len(entries),
                      "measurementProcessesStarted": 0, "measurementReceiptsRead": 0}))


if __name__ == "__main__":
    main()
