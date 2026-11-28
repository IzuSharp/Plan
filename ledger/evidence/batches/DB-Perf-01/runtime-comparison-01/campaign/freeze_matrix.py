#!/usr/bin/env python3
"""Bind already built and reviewed consumers to the serial local campaign."""
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def bound(path, expected=None):
    path = Path(path).resolve()
    actual = sha(path)
    if expected and actual != expected:
        raise ValueError("Changed reviewed input: " + str(path))
    return {"path": str(path), "sha256": actual}


def save_new(path, value):
    with path.open("x") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-root", type=Path, required=True)
    parser.add_argument("--java-verification", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    task = args.task_root.resolve()
    evidence = Path(__file__).resolve().parent.parent
    campaign = evidence / "campaign"
    policy_path = campaign / "memory-policy-192.json"
    policy = json.loads(policy_path.read_text())
    if policy["csharpRequestedGcHeapBytes"] != 201326592 or policy["cgroupRequired"]:
        raise ValueError("Owner memory policy differs")
    korda = task / "Korda"
    manifest = korda / "benchmarks/db-perf/workload/queries-v3.json"
    workload = json.loads(manifest.read_text())
    case_names = [item["name"] for item in workload["queries"]]
    if len(case_names) != 35:
        raise ValueError("Expected the original 35-case manifest")
    db = task / "toolchains/native-db"
    ef = evidence / "clients/efcore"
    java = evidence / "clients/java"
    ef_summary = json.loads((ef / "verification/attempt03-summary.json").read_text())
    java_identity = json.loads((java / "build-identity.json").read_text())
    java_verification = json.loads(args.java_verification.read_text())
    if java_verification["status"] != "passed" or java_verification["nativeExecutableSha256"] != java_identity["executableSha256"]:
        raise ValueError("Final Java executable lacks its matching successful finite verification")
    java_exe = java / "target/runtime-comparison-java"
    java_inputs = [bound(java_exe, java_identity["executableSha256"]),
                   bound(java / "build-identity.json"), bound(args.java_verification)]
    java_inputs += [bound(java / name, digest) for name, digest in java_identity["sourceHashes"].items()]
    java_inputs += [bound(path) for path in sorted((task / "toolchains/java/sqlite-jni").glob("*.so"))]
    if not any(item["path"].endswith("libsqlitejdbc.so") for item in java_inputs):
        raise ValueError("The common-engine SQLite JNI wrapper is absent")
    shared_inputs = [bound(manifest, policy["manifestSha256"]), bound(policy_path),
                     bound(Path(__file__)), bound(campaign / "run_matrix.py"),
                     bound(korda / "benchmarks/db-perf/run.py"), bound(db / "fixture.py"),
                     bound(db / "sqlite/lib/libsqlite3.so"), bound(db / "fixtures/seed.sqlite"),
                     bound(db / "postgres/bin/postgres"), bound(db / "postgres/bin/initdb"),
                     bound(db / "postgres/bin/psql"), bound(db / "postgres/bin/pg_isready")]
    matrix = {"schemaVersion": 1, "task": "DB-Runtime-Compare-01",
              "memoryPolicy": policy, "caseNames": case_names,
              "observerPath": str(korda / "benchmarks/db-perf/run.py"),
              "fixtureScript": str(db / "fixture.py"),
              "sqliteSeed": str(db / "fixtures/seed.sqlite"),
              "sqliteLibrary": str(db / "sqlite/lib/libsqlite3.so"),
              "postgresBin": str(db / "postgres/bin"), "frozenInputs": shared_inputs, "cells": []}
    lanes = {lane["lane"]: lane for lane in ef_summary["lanes"]}
    for implementation in ("dapper", "ef-workstation", "ef-satori", "java-native"):
        for provider in ("sqlite", "postgresql"):
            number = len(matrix["cells"]) + 1
            name = f"{number:02d}-{implementation}-{provider}"
            concurrency, rate = (4, 3000) if provider == "sqlite" else (8, 3600)
            if implementation == "dapper":
                build = task / f"builds/dapper-{provider}-01"
                exe = build / "out/DbPerf.Dapper"
                build_receipt = json.loads((build / "build-receipt.json").read_text())
                inputs = [bound(exe, build_receipt["executableSha256"]), bound(build / "build-receipt.json")]
            elif implementation.startswith("ef-"):
                lane = lanes[provider + "-" + implementation.removeprefix("ef-")]
                if not (lane["publishExitCode"] == lane["runExitCode"] == lane["failed"] == lane["oracleFailures"] == 0
                        and lane["all35CasesSucceededOnce"] and lane["applicationConnectionsReturnedToZero"]):
                    raise ValueError("EF lane did not pass finite validation")
                published = Path(lane["publishedDirectory"])
                exe = published / "DbPerf.EfCore"
                for artifact_name, digest in lane["publishedArtifacts"].items():
                    bound(published / artifact_name, digest)
                for image in lane["runtimeIdentity"]["RuntimeImages"]:
                    bound(image["Path"], image["Sha256"])
                inputs = [bound(path) for path in sorted(published.rglob("*")) if path.is_file()]
                inputs += [bound(ef / "verification/attempt03-summary.json")]
                inputs += [bound(ef / path, digest) for path, digest in ef_summary["sourceFilesSha256"].items()]
            else:
                exe = java_exe
                inputs = list(java_inputs)
            argv = [str(exe), "--connection", "{connection}", "--case", "mixed", "--mode", "prepared",
                    "--session", "persistent", "--concurrency", str(concurrency), "--rows", "32",
                    "--batch-rows", "32", "--tenants", "8", "--orders-per-tenant", "1024", "--warmup", "64",
                    "--queue-capacity", "64", "--verify", "--seconds", "1800", "--idle-seconds", "15",
                    "--rate", str(rate), "--output", "{output}/result.json"]
            if implementation == "java-native":
                admission = {"Schema": "DB-Runtime-Compare-01.java-admission.v1", "ApprovedForFormalMeasurement": True,
                             "ExecutableSha256": java_identity["executableSha256"],
                             "ContractSha256": policy["manifestSha256"], "Provider": provider,
                             "Case": "mixed", "Mode": "prepared", "SessionMode": "persistent",
                             "Concurrency": concurrency, "RequestsPerSecond": rate, "QueueCapacity": 64,
                             "Seconds": 1800, "WarmupPerWorker": 64, "IdleSeconds": 15,
                             "CSharpGcBudgetMiB": 192, "CgroupRequired": False, "JavaMemoryCapBytes": None,
                             "OwnerMemoryPolicySha256": sha(policy_path),
                             "FiniteNativeVerificationSha256": sha(args.java_verification)}
                admission_path = campaign / f"java-{provider}-admission.json"
                save_new(admission_path, admission)
                inputs.append(bound(admission_path))
                argv += ["--provider", provider, "--formal-admission", str(admission_path)]
                if provider == "sqlite":
                    argv += ["--sqlite-native-library", matrix["sqliteLibrary"], "--sqlite-jni-directory", str(task / "toolchains/java/sqlite-jni")]
                env = {"DOTNET_GCHeapHardLimit": None, "COMPlus_GCHeapHardLimit": None,
                       "LD_LIBRARY_PATH": str(db / "sqlite/lib")}
            else:
                if provider == "sqlite":
                    argv += ["--native-library", matrix["sqliteLibrary"]]
                env = {"DOTNET_GCHeapHardLimit": "0xC000000", "COMPlus_GCHeapHardLimit": None}
            matrix["cells"].append({"name": name, "implementation": implementation, "provider": provider,
                                    "environmentOverrides": env, "frozenInputs": inputs,
                                    "command": {"name": name, "phase": "formal-30-minute", "argv": argv,
                                                "cpus": "0-3", "timeoutSeconds": 2115}})
    save_new(args.output, matrix)
    print(json.dumps({"matrix": str(args.output), "sha256": sha(args.output), "cells": len(matrix["cells"])}))


if __name__ == "__main__":
    main()
