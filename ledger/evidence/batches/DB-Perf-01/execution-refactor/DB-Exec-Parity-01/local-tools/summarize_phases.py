#!/usr/bin/env python3
"""Summarize actual phase receipts without inventing finer attribution."""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics


def quantile(values, q):
    values = sorted(values)
    return values[max(0, math.ceil(len(values) * q) - 1)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    entries = []
    for path in sorted(args.directory.glob("*.json")):
        receipt = json.loads(path.read_text())
        if not isinstance(receipt, dict) or "Windows" not in receipt:
            continue
        routes = defaultdict(list)
        for window in receipt["Windows"]:
            routes[window["Route"]].append(window)
        frequency = receipt["StopwatchFrequency"]
        for route, windows in routes.items():
            ops = sum(w["Operations"] for w in windows)
            samples = [s for w in windows for s in w["Samples"]]
            row = {"provider": receipt["Provider"], "rows": receipt["ResultRows"],
                   "route": route, "operations": ops, "windows": len(windows),
                   "receipt": str(path.resolve()),
                   "receiptSha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                   "executableSha256": receipt["ExecutableSha256"],
                   "cpuUsPerOperation": sum(w["CpuAfterTicks"] - w["CpuBeforeTicks"] for w in windows) / ops / 10,
                   "managedBytesPerOperation": sum(w["AllocatedAfter"] - w["AllocatedBefore"] for w in windows) / ops,
                   "elapsedUsPerOperation": sum(w["FinishedTicks"] - w["StartedTicks"] for w in windows) * 1e6 / frequency / ops,
                   "phaseUs": {},
                   "peakRssBytes": max(w["PeakResidentBytes"] for w in windows),
                   "gc": {"gen" + str(i): sum(w["Gen" + str(i)] for w in windows) for i in range(3)}}
            for phase in ("ConstructTicks", "SubmitToFirstRowTicks", "ReadCompleteTicks", "ReleaseTicks", "total"):
                values = [(sum(s[k] for k in ("ConstructTicks", "SubmitToFirstRowTicks", "ReadCompleteTicks", "ReleaseTicks"))
                           if phase == "total" else s[phase]) * 1e6 / frequency for s in samples]
                row["phaseUs"][phase] = {"mean": statistics.fmean(values), **{str(q): quantile(values, q) for q in (0.5, 0.95, 0.99)}}
            if "NativeBefore" in windows[0]:
                row["nativeCountsPerOperation"] = {
                    name: sum(w["NativeAfter"][name] - w["NativeBefore"][name] for w in windows) / ops
                    for name in ("SqlExecutions", "ProtocolSubmissions")}
            entries.append(row)
    result = {"scope": "Existing diagnostic phase clocks; process CPU/allocation; not final ordinary mixed timing. Phase medians do not add to total median. No thread CPU/wait attribution inferred.", "entries": entries}
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    for r in sorted(entries, key=lambda v: (v["rows"], v["route"])):
        p = r["phaseUs"]
        print(f'{r["provider"]:10s} {r["rows"]:4d} {r["route"]:16s} cpu {r["cpuUsPerOperation"]:9.3f} us alloc {r["managedBytesPerOperation"]:10.3f} B p50 total {p["total"]["0.5"]:9.3f} us construct {p["ConstructTicks"]["0.5"]:8.3f} first {p["SubmitToFirstRowTicks"]["0.5"]:8.3f} read {p["ReadCompleteTicks"]["0.5"]:9.3f} close {p["ReleaseTicks"]["0.5"]:7.3f}')


if __name__ == "__main__":
    main()
