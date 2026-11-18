#!/usr/bin/env python3
"""Export completed B22 finite-stage evidence, excluding runtime/private bytes.

This is an evidence projection only. It does not alter or reinterpret run inputs,
turn a failed attempt into a pass, or replace an independent result review.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil


def sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def read(path: Path):
    return json.loads(path.read_text())


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    if sha256(source) != sha256(destination):
        raise RuntimeError(f"Copy hash mismatch: {source}")


def metadata(path: Path) -> dict:
    return {"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size}


def all_native_zero(observation: dict) -> bool:
    inventories = observation.get("databaseNativeOwners", {})
    return bool(inventories) and all(
        len(counts) == 6 and all(value == 0 for value in counts)
        for counts in inventories.values()
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--provider", choices=("sqlite", "postgresql"), action="append")
    parser.add_argument("--review", type=Path, action="append", default=[])
    args = parser.parse_args()
    run_root = args.root / "task07-runs"
    providers = args.provider or ["sqlite", "postgresql"]
    if len(set(providers)) != len(providers):
        raise ValueError("Duplicate provider")

    # Refuse to snapshot a mutable, unfinished attempt as complete evidence.
    sources = {}
    for provider in providers:
        run = run_root / f"b22-corrected-steady-{provider}-001-f889"
        descriptor = run.with_name(run.name + "-descriptors")
        receipt = read(run / "receipt.json")
        monitor = read(descriptor / "receipt.json")
        if receipt.get("status") in (None, "running") or monitor.get("status") in (None, "running"):
            raise RuntimeError(f"{provider}: completed receipts are required")
        sources[provider] = (run, descriptor, receipt, monitor)

    args.output.mkdir(parents=True, exist_ok=False)
    projector_path = Path(__file__).with_name("project_numeric_csv.py")
    spec = importlib.util.spec_from_file_location("b22_scalar_projector", projector_path)
    projector = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(projector)
    default_sources = projector.SOURCES
    copy(Path(__file__), args.output / Path(__file__).name)
    copy(projector_path, args.output / projector_path.name)

    summary = {
        "schemaVersion": 1,
        "task": "B22",
        "platform": "linux-x64",
        "scope": "Actual corrected-source 1800-second finite steady stages and their separate descriptor monitors; original frozen inputs and all attempt outcomes are preserved.",
        "multiDayExecution": {"24h": "not-executed-user-excluded", "72h": "not-executed-user-excluded"},
        "fullOriginalB22Acceptance": False,
        "globalPlateauOrLeakFreeClaim": False,
        "independentReview": "included" if args.review else "pending-separate-review",
        "exclusions": "No private configuration/key bytes, databases, executables, EventPipe binary buffers or raw known-handle addresses are exported. Original local hashes and all allowlisted scalar rows remain identified.",
        "providers": {},
        "localOnly": [],
    }

    for provider, (run, descriptor, receipt, monitor) in sources.items():
        destination = args.output / provider
        destination.mkdir()
        for relative in ("identity.json", "receipt.json", "trace-receipt.json"):
            path = run / relative
            if path.exists():
                copy(path, destination / relative)
        for relative in ("request.json", "receipt.json", "final-live-idle.json"):
            path = descriptor / relative
            if path.exists():
                copy(path, destination / "descriptors" / relative)

        identity_hash = sha256(run / "identity.json")
        if identity_hash != receipt["identitySha256"]:
            raise RuntimeError(f"{provider}: receipt identity mismatch")
        for relative, expected in receipt.get("rawHashes", {}).items():
            if sha256(run / relative) != expected:
                raise RuntimeError(f"{provider}: raw hash mismatch for {relative}")
        if monitor.get("soakReceiptSha256") != sha256(run / "receipt.json"):
            raise RuntimeError(f"{provider}: composite receipt does not bind actual soak receipt")
        for key, relative in (("numericSamplesSha256", "counts.jsonl"), ("peakInventoriesSha256", "peak-inventories.jsonl")):
            if monitor.get(key) != sha256(descriptor / relative):
                raise RuntimeError(f"{provider}: descriptor hash mismatch for {relative}")
        if "finalLiveIdleSha256" in monitor and monitor["finalLiveIdleSha256"] != sha256(descriptor / "final-live-idle.json"):
            raise RuntimeError(f"{provider}: final live descriptor witness mismatch")

        command = read(descriptor / "request.json")["command"]
        profile_path = Path(command[command.index("--profile") + 1])
        profile = read(profile_path)
        profile_hash = sha256(profile_path)
        if profile_hash != receipt["profileSha256"] or profile_hash != monitor["profileSha256"]:
            raise RuntimeError(f"{provider}: frozen profile mismatch")
        copy(profile_path, destination / "frozen-profile.json")

        projector.SOURCES = default_sources
        projector.project(run, destination / "scalar-csv")
        projector.SOURCES = ("counts.jsonl", "peak-inventories.jsonl")
        projector.project(descriptor, destination / "descriptor-csv")

        observations_path = run / "service" / "observations.jsonl"
        observations = [json.loads(line) for line in observations_path.read_text().splitlines()]
        before_finalizers = [row for row in observations if row.get("phase") == "application-main-returned-before-finalizers"]
        roots = receipt.get("idleGcHandleObservations", [])
        calibration_path = run_root / f"b22-corrected-calibration-{provider}-001-f889" / "receipt.json"
        calibration = read(calibration_path)
        root_values = [max(row["runtimeGcHandlesAtLastGc"], row["trackedLiveHandles"]) for row in roots]
        final = receipt.get("finalRetirement", {})
        provider_summary = {
            "runPath": str(run),
            "descriptorPath": str(descriptor),
            "ordinaryStatus": receipt["status"],
            "descriptorStatus": monitor["status"],
            "ordinaryError": receipt.get("error"),
            "descriptorError": monitor.get("error"),
            "bothStageReceiptsPass": receipt["status"] == "stage-passed" and monitor["status"] == "supplemented-stage-passed",
            "completedStageSeconds": receipt.get("completedStageSeconds"),
            "steadyLoadElapsedSeconds": receipt.get("steadyLoadElapsedSeconds"),
            "requiredStageSeconds": receipt["requiredStageSeconds"],
            "elapsedSeconds": receipt["elapsedSeconds"],
            "creditedPredecessorSeconds": receipt["creditedPredecessorSeconds"],
            "workloadCounts": receipt["workloadCounts"],
            "observedMax": receipt["observedMax"],
            "idleCaps": profile["idleCaps"],
            "peakCaps": profile["peakCaps"],
            "idleGcHandleCap": profile["idleGcHandleCap"],
            "nativeBeforeExplicitFinalizers": [row.get("databaseNativeOwners", {}) for row in before_finalizers],
            "allNativeBeforeExplicitFinalizersZero": bool(before_finalizers) and all(all_native_zero(row) for row in before_finalizers),
            "finalNative": final.get("databaseNativeOwners"),
            "finalNativeAllZero": all_native_zero(final),
            "finalServer": final.get("serverMeter"),
            "observerFailures": final.get("observerFailures"),
            "qualifiedPostGcNativeObservations": receipt.get("qualifiedPostGcNativeObservations"),
            "finalDurableOracle": receipt.get("finalDurableOracle"),
            "freshCalibrationRoots": calibration["idleGcHandleObservations"],
            "steadyRoots": roots,
            "steadyRootTotals": root_values,
            "rootTrendQualification": "The three calibration aggregate idle handle totals rose while normal handles were stable and pins were zero. The frozen finite-stage band is assessed by the exact receipts. A single final idle window does not establish a multi-day plateau or attribute all runtime handles to the product.",
            "traceObservation": receipt.get("traceObservation"),
            "inputRechecks": receipt.get("inputRechecks"),
            "profileSha256": profile_hash,
            "ordinaryReceiptSha256": sha256(run / "receipt.json"),
            "descriptorReceiptSha256": sha256(descriptor / "receipt.json"),
            "calibrationReceiptSha256": sha256(calibration_path),
            "descriptorPeak": monitor.get("peakEnumeratedDescriptors"),
            "descriptorProcessReadRaces": monitor.get("processReadRaces"),
            "finalLiveIdle": read(descriptor / "final-live-idle.json") if (descriptor / "final-live-idle.json").exists() else None,
        }
        summary["providers"][provider] = provider_summary
        for relative in ("runtime.nettrace", "known-handles.jsonl", "service/service.log"):
            path = run / relative
            if path.exists():
                summary["localOnly"].append({**metadata(path), "reason": "Binary trace, raw GCHandle addresses or unprojected diagnostic log retained locally; relevant scalar observations and result receipts are exported."})

    launch = run_root / "b22-corrected-steady-launch-001-f889"
    for name in ("request.json", "receipt.json", "exec-session.json"):
        if (launch / name).exists():
            copy(launch / name, args.output / ("launch-" + name))
    for review in args.review:
        copy(review, args.output / "reviews" / review.name)
    summary["allIncludedStagesPassed"] = all(row["bothStageReceiptsPass"] for row in summary["providers"].values())
    write(args.output / "result-summary.json", summary)
    files = []
    for path in sorted(args.output.rglob("*")):
        if path.is_file():
            files.append({**metadata(path), "path": path.relative_to(args.output).as_posix()})
    write(args.output / "manifest.json", {
        "schemaVersion": 1,
        "scope": summary["scope"],
        "allIncludedStagesPassed": summary["allIncludedStagesPassed"],
        "independentReview": summary["independentReview"],
        "exclusions": summary["exclusions"],
        "localOnly": summary["localOnly"],
        "files": files,
    })
    print(json.dumps({"output": str(args.output), "files": len(files) + 1, "bytes": sum(p.stat().st_size for p in args.output.rglob("*") if p.is_file()), "allIncludedStagesPassed": summary["allIncludedStagesPassed"]}))


if __name__ == "__main__":
    main()
