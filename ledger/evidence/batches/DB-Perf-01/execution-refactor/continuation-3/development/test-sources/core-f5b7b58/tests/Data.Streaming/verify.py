#!/usr/bin/env python3
"""Run B06 against the actual B02/B03 components, Linux NativeAOT.

The test-only native ABI bridge is not a second Database host or a shipped asset.
Missing PostgreSQL is a failed gate, never a successful or simulated result.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import socket
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "native/cpp/tests"))
from component_build import prepare

OWNED = (
    "native/cpp", "src/Data.Streaming", "tests/Data.Streaming",
    "samples/api/data-streaming", "docs/guides/data-streaming.md",
)
DEPENDENCIES = (
    "native/database/binding", "native/interop/abi", "CMakeLists.txt", "CMakePresets.json", ".clang-format", ".clang-tidy",
    "src/Data.Abstractions", "global.json", "Directory.Build.props", "Directory.Build.targets",
)
EXCLUDED = {"bin", "obj", "target", "artifacts", "__pycache__"}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_files() -> list[Path]:
    files = set()
    for scope in (*OWNED, *DEPENDENCIES):
        root = ROOT / scope
        if root.is_file():
            files.add(root)
        else:
            files.update(path for path in root.rglob("*") if path.is_file()
                         and not EXCLUDED.intersection(path.relative_to(ROOT).parts))
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--postgres-bin", type=Path)
    parser.add_argument("--offline-config", type=Path)
    parser.add_argument("--design-root", type=Path)
    parser.add_argument("--native-build", type=Path, default=ROOT / "artifacts/cmake/linux-x64-release")
    args = parser.parse_args()
    if platform.system() != "Linux" or platform.machine() not in ("x86_64", "amd64"):
        parser.error("This evidence runner targets Linux x64 only.")
    output = (args.output or ROOT / "artifacts/B06" / datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ")).resolve()
    output.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ, DOTNET_CLI_USE_MSBUILD_SERVER="0", MSBUILDDISABLENODEREUSE="1")
    records = []
    inputs = [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in source_files()]
    source = {
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "tree_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
        "files": inputs,
    }
    (output / "source-inputs.json").write_text(json.dumps(source, indent=2) + "\n")

    def run(name: str, command: list[str], use_env=None) -> str:
        log = output / (name + ".log")
        started = time.monotonic()
        with log.open("w") as stream:
            result = subprocess.run(command, cwd=ROOT, env=use_env or env, stdout=stream, stderr=subprocess.STDOUT)
        records.append({"name": name, "command": command, "exit_code": result.returncode,
                        "seconds": round(time.monotonic() - started, 3), "log": log.name, "sha256": sha(log)})
        (output / "commands.json").write_text(json.dumps(records, indent=2) + "\n")
        print(name + ": " + str(result.returncode), flush=True)
        if result.returncode:
            print(log.read_text()[-12000:], flush=True)
            raise RuntimeError("Gate failed: " + name)
        return log.read_text()

    common = ["-p:UseSharedCompilation=false", "-nr:false", "-m:1"]
    local_restore = (["--configfile", str(args.offline_config.resolve()), "-p:NuGetAudit=false"]
                     if args.offline_config else [])
    project = "tests/Data.Streaming/Korda.Data.Streaming.Tests.csproj"
    library = "src/Data.Streaming/Korda.Data.Streaming.csproj"
    api = "tests/Data.Streaming/ApiCheck/ApiCheck.csproj"
    sample = "samples/api/data-streaming/DataStreaming.csproj"
    fixture_dir = args.native_build.resolve() / "fixtures"
    fixture = fixture_dir / "libkorda_streaming_fixture.so"
    assembly = ROOT / "tests/Data.Streaming/bin/Release/net11.0/linux-x64/Korda.Data.Streaming.Tests.dll"
    streaming_assembly = ROOT / "src/Data.Streaming/bin/Release/net11.0/Korda.Data.Streaming.dll"
    streaming_xml = streaming_assembly.with_suffix(".xml")
    api_assembly = ROOT / "tests/Data.Streaming/ApiCheck/bin/Release/net11.0/Korda.Data.Streaming.ApiCheck.dll"
    sample_assembly = ROOT / "samples/api/data-streaming/bin/Release/net11.0/linux-x64/Korda.Data.Streaming.Sample.dll"
    server = None
    server_log = None
    status = "failed"
    try:
        run("toolchain-dotnet", ["dotnet", "--info"])
        tool_paths = [Path(shutil.which(tool)).resolve() for tool in ("dotnet", "clang++", "clang-format", "cmake")]
        (output / "tool-binaries.json").write_text(json.dumps([
            {"path": str(path), "sha256": sha(path), "size": path.stat().st_size} for path in tool_paths
        ], indent=2) + "\n")

        if args.design_root:
            design = args.design_root.resolve()
            manifest = json.loads((ROOT / "tests/Data.Streaming/design-inputs.json").read_text())
            revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=design, text=True).strip()
            if revision != manifest["design_commit"]:
                raise RuntimeError("Design checkout differs from the locked revision.")
            checked = {}
            for key, expected in {**manifest["api_inputs"], **manifest["contracts"]}.items():
                relative = key.split(":", 1)[-1]
                actual = sha(design / relative)
                if actual != expected:
                    raise RuntimeError("Locked Design input differs: " + relative)
                checked[relative] = actual
            (output / "design-check.json").write_text(json.dumps({"revision": revision, "files": checked}, indent=2) + "\n")

        provenance = prepare(run, args.native_build,
                             ["korda_streaming_fixture", "nw_streaming_tests"], r"^native\.streaming$",
                             [ROOT / "native/cpp/tests/fixtures/streaming.cpp", ROOT / "native/cpp/tests/streaming_tests.cpp"])
        (output / "compiler-provenance.txt").write_text(provenance)

        for label, path in [("library", library), ("api-check", api)]:
            run(label + "-restore", ["dotnet", "restore", path, "--locked-mode", *local_restore, *common])
            run(label + "-build", ["dotnet", "build", path, "-c", "Release", "--no-restore", *common])
        cs_files = [str(path.relative_to(ROOT)) for scope in OWNED if (ROOT / scope).is_dir()
                    for path in sorted((ROOT / scope).rglob("*.cs"))
                    if not EXCLUDED.intersection(path.relative_to(ROOT).parts)]
        run("managed-format", ["dotnet", "format", "whitespace", ".", "--folder", "--include", *cs_files,
                               "--verify-no-changes", "--verbosity", "quiet"])
        run("compiled-api-reference", ["dotnet", str(api_assembly), str(streaming_assembly), str(streaming_xml),
                                       str(ROOT / "src/Data.Streaming/api-reference.md")])
        publish = output / "aot"
        run("aot-publish", ["dotnet", "publish", project, "-c", "Release", "-r", "linux-x64",
                            "-p:PublishAot=true", "-p:RestoreLockedMode=true", *local_restore, *common, "-o", str(publish)])
        executable = publish / "Korda.Data.Streaming.Tests"
        native_env = dict(env, LD_LIBRARY_PATH=str(fixture_dir) + (":" + env["LD_LIBRARY_PATH"] if env.get("LD_LIBRARY_PATH") else ""))
        # The provider correctness run retains storage identity, transfer,
        # disposal, malformed-batch and race assertions. Allocation windows are
        # explicit local diagnostics and are not invoked by this CI verifier.
        if args.postgres_bin:
            pg = args.postgres_bin.resolve()
            data = output / "postgres-data"
            run("postgres-version", [str(pg / "postgres"), "--version"])
            run("postgres-init", [str(pg / "initdb"), "-D", str(data), "-U", "korda", "--auth=trust", "--no-locale", "--encoding=UTF8"])
            with socket.socket() as listener:
                listener.bind(("127.0.0.1", 0))
                port = listener.getsockname()[1]
            server_log = (output / "postgres.log").open("w")
            server = subprocess.Popen([str(pg / "postgres"), "-D", str(data), "-h", "127.0.0.1", "-p", str(port), "-k", ""],
                                      stdout=server_log, stderr=subprocess.STDOUT, env=env)
            for _ in range(300):
                if subprocess.run([str(pg / "pg_isready"), "-h", "127.0.0.1", "-p", str(port)],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
                    break
                if server.poll() is not None:
                    raise RuntimeError("PostgreSQL exited during startup.")
                time.sleep(.1)
            else:
                raise RuntimeError("PostgreSQL startup deadline exceeded.")
            # B02 accepts only typed connection settings. The fixture selects the
            # explicit local-development plaintext policy; URL query overrides are forbidden.
            native_env["KORDA_TEST_POSTGRES_URL"] = f"postgresql://korda@127.0.0.1:{port}/postgres"
        elif not native_env.get("KORDA_TEST_POSTGRES_URL"):
            raise RuntimeError("PostgreSQL binaries or explicit KORDA_TEST_POSTGRES_URL are required.")
        run("aot-providers", [str(executable), str(output / "aot-results"), "--require-aot", "--correctness-only"], native_env)
        sample_dir = output / "sample-aot"
        run("sample-aot-publish", ["dotnet", "publish", sample, "-c", "Release", "-r", "linux-x64",
                                  "-p:PublishAot=true", "-p:RestoreLockedMode=true", "-o", str(sample_dir), *local_restore, *common])
        sample_exe = sample_dir / "Korda.Data.Streaming.Sample"
        run("sample-sqlite", [str(sample_exe), "sqlite"], native_env)
        run("sample-postgresql", [str(sample_exe), "postgresql"], native_env)

        artifact_paths = [assembly, streaming_assembly, streaming_xml, executable, fixture, api_assembly, sample_assembly, sample_exe]
        (output / "artifacts.json").write_text(json.dumps([
            {"path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
             "sha256": sha(path), "size": path.stat().st_size} for path in artifact_paths
        ], indent=2) + "\n")
        # Bind the results to the bytes actually verified, including both provider adapters.
        current = [{"path": str(path.relative_to(ROOT)), "sha256": sha(path)} for path in source_files()]
        if current != inputs:
            raise RuntimeError("Source inputs changed during verification.")
        status = "passed"
    except Exception as error:
        (output / "failure.txt").write_text(str(error) + "\n")
    finally:
        if server is not None:
            subprocess.run([str(args.postgres_bin.resolve() / "pg_ctl"), "-D", str(output / "postgres-data"), "stop", "-m", "fast"],
                           stdout=server_log, stderr=subprocess.STDOUT)
            try:
                server.wait(timeout=30)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()
        if server_log is not None:
            server_log.close()
        summary = {
            "task": "B06", "platform": "linux-x64", "status": status, "commands": len(records),
            "source_manifest_sha256": sha(output / "source-inputs.json"),
            "offline_restore": args.offline_config is not None,
            "scope": "Retained native/managed bounded stream composition with actual C++ Host/libpq/SQLite providers, Linux Native AOT, compiled API/XML and sample. No pristine package, other-platform acceptance, or hard process RSS bound.",
        }
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps(summary), flush=True)
    return 0 if status == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
