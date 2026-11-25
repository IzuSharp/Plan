#!/usr/bin/env python3
"""Validate one changed default AOT entry; this is not the final full verifier."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import traceback


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def identity(root):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()
    return {"commit": git("rev-parse", "HEAD"), "tree": git("rev-parse", "HEAD^{tree}"),
            "status": git("status", "--porcelain")}


PROJECTS = {
    "Data.Abstractions": "Korda.Data.Tests",
    "Query.Binding": "Korda.Query.Binding.Tests",
    "Data.Streaming": "Korda.Data.Streaming.Tests",
    "Interop.Negotiation": "Korda.Interop.Negotiation.Tests",
    "Data.NativeHost": "Korda.Data.NativeHost.Tests",
    "Query.Fluent": "Korda.Query.Fluent.Tests",
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", choices=PROJECTS, required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--native-root", type=Path, required=True)
    parser.add_argument("--negotiation-fixtures", type=Path, required=True)
    parser.add_argument("--postgres-bin", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expect-commit", required=True)
    args = parser.parse_args()
    root, native_root, output = [p.resolve() for p in (args.root, args.native_root, args.output)]
    output.mkdir(parents=True, exist_ok=False)
    (output / "controller.py").write_bytes(Path(__file__).read_bytes())
    receipt = {"scope": "affected AOT entry validation", "fullVerifierAcceptance": False,
               "performanceCampaign": False, "component": args.component, "status": "running",
               "scriptSha256": sha(__file__), "commands": []}

    def save():
        (output / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")

    env = os.environ | {"DOTNET_CLI_USE_MSBUILD_SERVER": "0", "MSBUILDUSESERVER": "0",
                       "MSBUILDDISABLENODEREUSE": "1"}

    def run(label, command, extra_env=None):
        argv = list(map(str, command))
        log = output / (label + ".log")
        print("RUN " + label, flush=True)
        with log.open("w") as stream:
            result = subprocess.run(argv, cwd=root, env=env | (extra_env or {}),
                                    stdout=stream, stderr=subprocess.STDOUT, timeout=900)
        receipt["commands"].append({"label": label, "argv": argv, "exitCode": result.returncode,
                                    "log": str(log), "sha256": sha(log)})
        save()
        if result.returncode:
            raise RuntimeError(f"{label}: exit {result.returncode}; see {log}")

    try:
        receipt["source"] = identity(root)
        if receipt["source"]["commit"] != args.expect_commit or receipt["source"]["status"]:
            raise RuntimeError("Expected a clean committed cleanup worktree")
        manifest_path = native_root / "artifacts/db-exec-b-native/manifest.json"
        manifest = json.loads(manifest_path.read_text())
        if manifest["sourceDirty"]:
            raise RuntimeError("Native source producer is not clean")
        for name, expected in manifest["inputSha256"].items():
            if sha(root / name) != expected:
                raise RuntimeError("Native input differs from the retained producer: " + name)
        receipt["nativeProducer"] = {"sourceCommit": manifest["sourceCommit"],
                                      "manifest": str(manifest_path), "sha256": sha(manifest_path),
                                      "verifiedSourceFiles": len(manifest["inputSha256"])}
        native_build = native_root / "artifacts/cmake/linux-x64-release"
        assets = native_root / "artifacts/native-install/linux-x64-release/lib"
        fixtures = native_build / "fixtures"
        asset_properties = []
        pinned = {}
        for provider, property_name in (("sqlite", "KordaSqliteAssetPath"),
                                        ("postgresql", "KordaPostgresAssetPath")):
            path = assets / ("libnw_database_" + provider + ".so")
            expected = next(item["sha256"] for item in manifest["assets"]
                            if Path(item["installedArtifactPath"]).name == path.name)
            if sha(path) != expected:
                raise RuntimeError("Retained native asset changed: " + str(path))
            pinned[str(path)] = expected
            asset_properties.append("-p:" + property_name + "=" + str(path))
        for name in ("libkorda_query_binding_fixture.so", "libkorda_streaming_fixture.so"):
            pinned[str(fixtures / name)] = sha(fixtures / name)
        receipt["nativeBinarySha256"] = pinned
        native_env = {"LD_LIBRARY_PATH": str(fixtures) + (":" + env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else "")}
        flags = ["-m:1", "-nr:false", "-p:UseSharedCompilation=false", *asset_properties]
        assembly = PROJECTS[args.component]
        project_name = "Interop.Negotiation.Tests" if args.component == "Interop.Negotiation" else assembly
        project = root / "tests" / args.component / (project_name + ".csproj")
        publish = output / "aot"
        run("restore", ["dotnet", "restore", project, "--locked-mode", "-r", "linux-x64",
                        "-p:RuntimeIdentifier=linux-x64", "-p:PublishAot=true", *flags])
        run("publish", ["dotnet", "publish", project, "-c", "Release", "-r", "linux-x64", "--no-restore",
                        "-p:PublishAot=true", "-p:IlcTreatWarningsAsErrors=true", *flags, "-o", publish])
        executable = publish / assembly
        if executable.read_bytes()[:4] != b"\x7fELF" or executable.with_suffix(".dll").exists():
            raise RuntimeError("Default entry is not an actual standalone Native AOT executable")
        receipt["executable"] = {"path": str(executable), "sha256": sha(executable)}
        save()
        results = output / "results"
        if args.component == "Data.Abstractions":
            run("default-aot", [executable, results, "--require-aot"])
        elif args.component == "Query.Binding":
            run("default-aot", [executable, fixtures / "libkorda_query_binding_fixture.so", results, "--require-aot"], native_env)
        elif args.component == "Interop.Negotiation":
            # Case helpers may create repaired/corrupt files. Retain old evidence unchanged.
            target = output / "fixtures"
            target.mkdir()
            for path in args.negotiation_fixtures.resolve().glob("libnw_a02_*.so"):
                shutil.copyfile(path, target / path.name)
            receipt["negotiationFixtureSha256"] = {p.name: sha(p) for p in target.iterdir()}
            syntax = ast.parse((root / "tests/Interop.Negotiation/verify.py").read_text())
            cases = next(ast.literal_eval(node.value) for node in syntax.body
                         if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets))
            receipt["defaultCaseList"] = cases
            for case in cases:
                run("default-aot-" + case, [executable, case, target, "--require-aot"])
        else:
            actual = [executable] if args.component == "Data.NativeHost" else [executable, results, "--require-aot"]
            if args.component == "Data.Streaming":
                # Preserve the actual default argv: only output and the AOT assertion.
                # The original PG wrapper sets NW_TEST_POSTGRES; this adapter forwards
                # that same endpoint to the streaming fixture's established env name.
                code = 'import os,sys; env=dict(os.environ); env["KORDA_TEST_POSTGRES_URL"]=env["NW_TEST_POSTGRES"]; os.execve(sys.argv[1],sys.argv[1:],env)'
                actual = [sys.executable, "-c", code, *actual]
                receipt["defaultApplicationArgv"] = list(map(str, [executable, results, "--require-aot"]))
            run("default-aot-live-providers", [sys.executable, root / "tests/Data.NativeHost/run.py",
                                               "--postgres-bin", args.postgres_bin.resolve(),
                                               "--output", output / "postgres", "--", *actual], native_env)
        if identity(root) != receipt["source"]:
            raise RuntimeError("Cleanup source changed during validation")
        if any(sha(path) != expected for path, expected in pinned.items()):
            raise RuntimeError("Retained native fixture/asset changed during validation")
        receipt.update(status="passed", sourceStable=True, nativeInputsStable=True)
    except BaseException as error:
        receipt.update(status="failed", exceptionType=type(error).__name__, error=str(error))
        (output / "failure.txt").write_text(traceback.format_exc())
        save()
        raise
    save()
    print("PASS " + args.component + " affected default AOT entry", flush=True)


if __name__ == "__main__":
    main()
