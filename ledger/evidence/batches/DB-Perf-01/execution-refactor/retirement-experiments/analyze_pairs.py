#!/usr/bin/env python3
"""Summarize retained local closed-loop and phase receipts without changing scope."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics


def percentile(values, fraction):
    values = sorted(values)
    return values[math.floor((len(values) - 1) * fraction)]


def summarize(directory):
    mixed, phases = [], []
    for path in sorted(directory.glob("*.json")):
        record = json.loads(path.read_text())
        if not isinstance(record, dict):
            continue
        identity = {"file": path.name, "sha256": hashlib.file_digest(path.open("rb"), "sha256").hexdigest()}
        if record.get("Case") == "mixed" and "Latencies" in record:
            if record.get("OfferedLoad") is not None:
                raise ValueError(f"{path}: offered-load counters need their own accounting; never normalize them as closed-loop")
            mixed.append(identity | {
                "provider": record["Provider"], "route": record["Route"],
                "executableSha256": record["ExecutableSha256"], "nativeSha256": record["LoadedNativeSha256"],
                "concurrency": record["Concurrency"], "seconds": record["EffectiveSeconds"],
                "completed": record["Completed"], "failed": record["Failed"],
                "oracleFailures": record["OracleFailures"],
                "opsPerSecond": record["Completed"] / record["EffectiveSeconds"],
                "p50MicrosecondsUpper": record["Latencies"]["P50MicrosecondsUpper"],
                "p95MicrosecondsUpper": record["Latencies"]["P95MicrosecondsUpper"],
                "p99MicrosecondsUpper": record["Latencies"]["P99MicrosecondsUpper"],
                "latencyMethod": record["Latencies"]["Method"],
                "processCpuMicrosecondsPerSuccessfulOperation": record["CpuSecondsPerSuccessfulOperation"] * 1e6,
                "processBytesPerSuccessfulOperation": record["BytesPerSuccessfulOperation"],
                "processGc": [record["Gen0"], record["Gen1"], record["Gen2"]],
                "processAfter": record["ProcessAfter"], "ownersReturnedToZero": record["OwnersReturnedToZero"],
                "timingComparisonEligible": record["TimingComparisonEligible"],
                "measuredExternalRejections": None, "frameworkOnlyBytes": None,
            })
        if record.get("SchemaVersion") == 3 and "Windows" in record and "ResultRows" in record:
            for route in sorted({window["Route"] for window in record["Windows"]}):
                windows = [window for window in record["Windows"] if window["Route"] == route]
                samples = [sample for window in windows for sample in window["Samples"]]
                operations = sum(window["Operations"] for window in windows)
                if len(samples) != operations:
                    raise ValueError(f"{path}: phase sample count differs from operations")
                fields = {}
                for name in ("ConstructTicks", "SubmitToFirstRowTicks", "ReadCompleteTicks", "ReleaseTicks"):
                    values = [sample[name] * 1000 / record["StopwatchFrequency"] for sample in samples]
                    fields[name.removesuffix("Ticks")] = {
                        "p50Milliseconds": statistics.median(values),
                        "p95Milliseconds": percentile(values, .95),
                        "p99Milliseconds": percentile(values, .99),
                    }
                phases.append(identity | {
                    "provider": record["Provider"], "route": route, "rows": record["ResultRows"],
                    "executableSha256": record["ExecutableSha256"], "nativeSha256": record["NativeSha256"],
                    "operations": operations, "windows": len(windows), "phases": fields,
                    "processBytesPerOperation": sum(window["AllocatedAfter"] - window["AllocatedBefore"] for window in windows) / operations,
                    "processGc": [sum(window[key] for window in windows) for key in ("Gen0", "Gen1", "Gen2")],
                    "drained": record["Drained"], "frameworkOnlyBytes": None,
                    "phasePercentileMethod": "p50 median; p95/p99 sorted sample at floor((n-1)*p), no interpolation",
                })
    return {"directory": directory.name, "mixed": mixed, "phases": phases,
            "scope": "Short closed-loop decision experiments, not long-load acceptance. Process bytes include business results; no subtraction establishes framework allocation. Rejections from an external arrival process were not measured."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directories", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = [summarize(directory) for directory in args.directories]
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"directories": len(result), "mixed": sum(len(row["mixed"]) for row in result),
                      "phases": sum(len(row["phases"]) for row in result)}))


if __name__ == "__main__":
    main()
