#!/usr/bin/env python3
"""Build a separate allocation-only overlay from a successful external phase consumer.

This command compiles but never runs the diagnostic. Original consumer files,
native libraries, packages, production sources, CI and default tests are untouched.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"Expected one unchanged phase-consumer anchor, found {text.count(old)}: {old!r}")
    return text.replace(old, new, 1)


def matching(text: str, start: int, opening: str, closing: str) -> int:
    """Find the end of a generated expression/body, ignoring C# comments/strings."""
    if text[start] != opening:
        raise ValueError("Missing generated opening delimiter")
    depth = 0
    index = start
    while index < len(text):
        if text.startswith("//", index):
            index = text.find("\n", index)
            if index < 0:
                break
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            if end < 0:
                raise ValueError("Unterminated generated comment")
            index = end + 2
            continue
        if text[index] in ('"', "'"):
            quote = text[index]
            index += 1
            while index < len(text):
                if text[index] == "\\":
                    index += 2
                elif text[index] == quote:
                    index += 1
                    break
                else:
                    index += 1
            continue
        if text[index] == opening:
            depth += 1
        elif text[index] == closing:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    raise ValueError("Unbalanced generated expression/body")


def instrument_mapper(text: str, family: str) -> tuple[str, int]:
    if family == "korda":
        needle = "static @row => new global::PhaseRow("
        if text.count(needle) != 2:
            raise ValueError("Expected the actual Korda generated Row and Bind mapper bodies")
        for _ in range(2):
            start = text.index(needle)
            expression_start = start + len("static @row => ")
            opening = start + len(needle) - 1
            end = matching(text, opening, "(", ")")
            expression = text[expression_start:end + 1]
            text = text[:start] + "static @row => { using var __allocationScope = global::BusinessAllocation.Mapper(); return " + expression + "; }" + text[end + 1:]
        return text, 2
    needle = "public override global::PhaseRow Read("
    if text.count(needle) != 1 or not all(token in text for token in ["Tokenize(", "reader.GetInt64(", "reader.GetString(", "CommandFactory"]):
        raise ValueError("Expected the actual Dapper.AOT generated typed RowFactory<PhaseRow>")
    opening = text.index("{", text.index(needle))
    matching(text, opening, "{", "}")
    return text[:opening + 1] + "\n                using var __allocationScope = global::BusinessAllocation.Mapper();" + text[opening + 1:], 1


def instrument_consumer(app: Path, family: str) -> None:
    program = app / "Program.cs"
    text = program.read_text(encoding="utf-8-sig")
    if family == "korda":
        text = replace_once(text, "var diagnostics = new FailureDiagnostics(args[1]);",
                            'BusinessAllocation.Configure(args[1], resultRows, "korda");\nvar diagnostics = new FailureDiagnostics(args[1]);')
        text = replace_once(text, "    var nativeBefore = identity.Read();",
                            "    BusinessAllocation.BeginWindow(PhaseProbe.Names[lane], window, iterations, resultRows);\n    var nativeBefore = identity.Read();")
        text = replace_once(text, "    diagnostics.CompletedWindows++;",
                            "    BusinessAllocation.EndWindow(allocatedBefore, allocatedAfter, end0 - gc0, end1 - gc1, end2 - gc2);\n    diagnostics.CompletedWindows++;")
        text = replace_once(text, 'Console.WriteLine("DB_PERF_QUERY_PHASES " + args[1]);',
                            'BusinessAllocation.Write();\nConsole.WriteLine("DB_PERF_QUERY_PHASES " + args[1]);')
        text = replace_once(text, '"Local phase diagnostic. Construction includes',
                            '"ALLOCATION-INSTRUMENTED; TimingCredit=false. Local phase diagnostic. Construction includes')
        text = replace_once(text, "rows = new List<PhaseRow>(_resultRows);", "rows = BusinessAllocation.CreateList<PhaseRow>(_resultRows);")
        if text.count("rows.Add(reader.Current);") != 2:
            raise ValueError("Expected the unchanged first-row and remaining-row List.Add sites")
        text = text.replace("rows.Add(reader.Current);", "BusinessAllocation.Add(rows, reader.Current);")
    else:
        text = replace_once(text, "var options = Options.Parse(args);",
                            'var options = Options.Parse(args);\nBusinessAllocation.Configure(options.Output, options.Rows, "dapper-aot");')
        text = replace_once(text, "        var samples = new Sample[options.Iterations];",
                            '        var samples = new Sample[options.Iterations];\n        BusinessAllocation.BeginWindow("dapper-aot", window, options.Iterations, options.Rows);')
        text = replace_once(text, "            started, ended, samples);",
                            "            started, ended, samples);\n        BusinessAllocation.EndWindow(allocatedBefore, allocatedAfter, end0 - gc0, end1 - gc1, end2 - gc2);")
        text = replace_once(text, '    Console.WriteLine("DB_PERF_DAPPER_QUERY_PHASES " + options.Output);',
                            '    BusinessAllocation.Write();\n    Console.WriteLine("DB_PERF_DAPPER_QUERY_PHASES " + options.Output);')
        text = replace_once(text, '"Local Dapper.AOT phase diagnostic, one connection',
                            '"ALLOCATION-INSTRUMENTED; TimingCredit=false. Local Dapper.AOT phase diagnostic, one connection')
        probe = app / "PhaseProbe.cs"
        body = probe.read_text(encoding="utf-8-sig")
        body = replace_once(body, "rows = new List<PhaseRow>(resultRows);", "rows = BusinessAllocation.CreateList<PhaseRow>(resultRows);")
        if body.count("rows.Add(reader.Current);") != 2:
            raise ValueError("Expected the unchanged Dapper first-row and remaining-row List.Add sites")
        probe.write_text(body.replace("rows.Add(reader.Current);", "BusinessAllocation.Add(rows, reader.Current);"))
    program.write_text(text)


def offline_feed(original: dict, app: Path, assets: dict) -> list[dict]:
    feed = app / "offline-feed"
    feed.mkdir()
    packages = []
    required = dict(assets["libraries"])
    for framework in assets["project"]["frameworks"].values():
        for dependency in framework.get("downloadDependencies", []):
            bounds = dependency["version"].strip("[]").split(",")
            if len(bounds) != 2 or bounds[0].strip() != bounds[1].strip():
                raise ValueError("SDK download dependency is not an exact version: " + repr(dependency))
            version = bounds[0].strip()
            identity = dependency["name"] + "/" + version
            required.setdefault(identity, {"type": "package", "path": identity.lower(), "downloadDependency": True})
    for identity, data in required.items():
        if data["type"] != "package":
            raise ValueError("A diagnostic must originate from an external package-only consumer")
        name, version = identity.split("/", 1)
        filename = name.lower() + "." + version.lower() + ".nupkg"
        candidates = [Path(folder) / data["path"] / filename for folder in assets["packageFolders"]]
        archive = next((path.resolve() for path in candidates if path.is_file()), None)
        if archive is None:
            raise FileNotFoundError("Original restored package archive is unavailable: " + identity)
        # NuGet's asset-graph contentHash is not the raw signed archive hash.
        # Preserve and compare both identities using their original records.
        metadata = json.loads((archive.parent / ".nupkg.metadata").read_text())
        if data.get("sha512") and metadata.get("contentHash") != data["sha512"]:
            raise ValueError("Restored NuGet metadata differs from the original asset graph: " + identity)
        digest = sha(archive)
        prior = original.get("packages", {}).get(identity, {}).get("sha256")
        if identity == original.get("package", "") + "/" + original.get("version", ""):
            prior = original["package_sha256"]
        if prior and digest != prior:
            raise ValueError("Package archive differs from its successful build receipt: " + identity)
        (feed / filename).symlink_to(archive)
        packages.append({"identity": identity, "path": str(archive), "sha256": digest,
                         "nugetContentHash": metadata.get("contentHash"), "downloadDependency": data.get("downloadDependency", False)})
    configuration = ET.Element("configuration")
    sources = ET.SubElement(configuration, "packageSources")
    ET.SubElement(sources, "clear")
    ET.SubElement(sources, "add", key="captured-packages", value=str(feed))
    ET.ElementTree(configuration).write(app / "NuGet.Config", encoding="utf-8", xml_declaration=True)
    return packages


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consumer", type=Path, required=True, help="Successful ordinary external query-phases consumer directory")
    parser.add_argument("--output", type=Path, required=True, help="Fresh diagnostic directory outside every Korda source worktree")
    args = parser.parse_args()
    consumer, app = args.consumer.resolve(), args.output.resolve()
    if platform.system() != "Linux" or platform.machine() not in ("x86_64", "amd64"):
        parser.error("The diagnostic is limited to the requested Linux x64 environment")
    if app.exists() or app == ROOT or ROOT in app.parents or consumer == app or consumer in app.parents:
        parser.error("Use a fresh external output; input consumers and source trees are immutable")
    # A separate worktree may be outside this tool checkout but is still source.
    # Ask Git about the existing destination parent, respecting mount boundaries.
    existing_parent = next(parent for parent in app.parents if parent.is_dir())
    discovery = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=existing_parent,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=False)
    if discovery.returncode == 0 and discovery.stdout.strip() == "true":
        parser.error("Diagnostic output cannot be inside a git checkout")
    app.mkdir(parents=True)
    receipt: dict = {"schemaVersion": 1, "scope": "Independent allocation-only diagnostic build; no timing credit and no execution by this builder",
                     "timingCredit": False, "consumer": str(consumer), "output": str(app), "commands": [],
                     "builderSha256": sha(Path(__file__).resolve()), "observerSha256": sha(HERE / "BusinessAllocation.cs")}

    def write_receipt() -> None:
        (app / "allocation-build-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")

    def run(name: str, command: list[str], environment: dict) -> None:
        log = app / (name + ".log")
        started = time.monotonic()
        with log.open("w") as stream:
            result = subprocess.run(command, cwd=app, env=environment, stdout=stream, stderr=subprocess.STDOUT, check=False)
        receipt["commands"].append({"name": name, "command": command, "exitCode": result.returncode,
                                    "seconds": round(time.monotonic() - started, 6), "log": log.name, "logSha256": sha(log)})
        write_receipt()
        print(f"{name}: {result.returncode}", flush=True)
        if result.returncode:
            raise RuntimeError("Diagnostic compilation failed; retained log: " + str(log))

    try:
        original_receipt = consumer / "build-receipt.json"
        original = json.loads(original_receipt.read_text())
        if original.get("kind") != "query-phases" or original.get("exit_code", original.get("exitCode")) != 0 or "postValidationError" in original or "post_validation_error" in original:
            raise ValueError("A successful ordinary query-phases build receipt is required")
        receipt["inputBuildReceiptSha256"] = sha(original_receipt)
        receipt["inputBuildReceipt"] = original
        projects = list(consumer.glob("*.csproj"))
        if len(projects) != 1:
            raise ValueError("Expected one external phase project")
        source_project = projects[0]
        project_xml = ET.parse(source_project)
        if project_xml.getroot().findall(".//ProjectReference"):
            raise ValueError("Only public package consumers can be instrumented")
        expected_project = original.get("project_sha256", original.get("projectSha256"))
        if sha(source_project) != expected_project:
            raise ValueError("Consumer project no longer matches its successful receipt")
        family = "korda" if source_project.name == "DbPerf.QueryPhases.csproj" else "dapper-aot" if source_project.name == "DbPerf.DapperQueryPhases.csproj" else None
        if family is None:
            raise ValueError("Unsupported phase consumer")
        receipt["family"] = family
        provider = original["provider"]
        if provider not in ("sqlite", "postgresql"):
            raise ValueError("Unsupported provider")
        receipt["provider"] = provider
        receipt["inputSources"] = original["sources"]
        for name, digest in original["sources"].items():
            source = consumer / name
            if source.parent != consumer or sha(source) != digest:
                raise ValueError("Consumer source no longer matches its successful receipt: " + name)
            shutil.copy2(source, app / name)
        for name in (source_project.name, "global.json", "Directory.Build.props"):
            if (consumer / name).is_file():
                shutil.copy2(consumer / name, app / name)
        if not (app / "Directory.Build.props").exists():
            (app / "Directory.Build.props").write_text("<Project />\n")
        original_assets = consumer / "obj/project.assets.json"
        expected_assets = original.get("assets_sha256", original.get("assetsSha256"))
        if sha(original_assets) != expected_assets:
            raise ValueError("Consumer asset graph no longer matches its receipt")
        assets = json.loads(original_assets.read_text())
        receipt["packages"] = offline_feed(original, app, assets)
        instrument_consumer(app, family)
        shutil.copy2(HERE / "BusinessAllocation.cs", app / "BusinessAllocation.cs")
        project = app / source_project.name
        environment = os.environ | {"NUGET_PACKAGES": str(app / "packages"), "DOTNET_PROCESSOR_COUNT": "1",
                                    "DOTNET_CLI_USE_MSBUILD_SERVER": "0", "MSBUILDDISABLENODEREUSE": "1"}
        common = ["-c", "Release", "-r", "linux-x64", "-p:Provider=" + ("Sqlite" if provider == "sqlite" else "PostgreSql"),
                  "-p:PublishAot=true", "-p:UseSharedCompilation=false", "-m:1", "-nr:false", "-p:NuGetAudit=false",
                  "-p:RestorePackagesWithLockFile=true", "-p:EmitCompilerGeneratedFiles=true",
                  "-p:CompilerGeneratedFilesOutputPath=obj/allocation-generated"]
        if family == "korda":
            common += ["-p:KordaVersion=" + original["version"]]
        run("generate", ["dotnet", "build", str(project), *common], environment)
        overlay_assets = json.loads((app / "obj/project.assets.json").read_text())
        if overlay_assets["libraries"] != assets["libraries"]:
            raise ValueError("The diagnostic restore graph differs from its ordinary consumer")
        generated = app / "obj/allocation-generated"
        generated_files = sorted(generated.rglob("*.cs"))
        if not generated_files:
            raise ValueError("The real source generators emitted no captured source")
        original_dir = app / "generated-original"
        captured_dir = app / "generated-instrumented"
        patches = []
        generated_hashes = {}
        mapper_methods = 0
        for path in generated_files:
            relative = path.relative_to(generated)
            before = path.read_text(encoding="utf-8-sig")
            after = before
            mapper = family == "korda" and path.name.startswith("PhaseRow.") and path.name.endswith(".Projection.g.cs")
            mapper |= family == "dapper-aot" and path.name == "DbPerf.DapperQueryPhases.generated.cs"
            if mapper:
                after, count = instrument_mapper(before, "korda" if family == "korda" else "dapper")
                mapper_methods += count
                patches.extend(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                                    fromfile="generated-original/" + str(relative), tofile="generated-instrumented/" + str(relative)))
            original_copy, captured = original_dir / relative, captured_dir / relative
            original_copy.parent.mkdir(parents=True, exist_ok=True); captured.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, original_copy); captured.write_text(after)
            generated_hashes[str(relative)] = {"originalSha256": sha(original_copy), "instrumentedSha256": sha(captured), "mapper": bool(mapper)}
        if mapper_methods != (2 if family == "korda" else 1):
            raise ValueError("Did not instrument the expected actual generated mapper bodies")
        receipt["mapperMethods"] = mapper_methods
        receipt["generatedSources"] = generated_hashes
        (app / "generated-mapper.patch").write_text("".join(patches))
        tree = ET.parse(project)
        item = ET.SubElement(tree.getroot(), "ItemGroup")
        ET.SubElement(item, "Compile", Remove="generated-original/**/*.cs;generated-instrumented/**/*.cs")
        target = ET.SubElement(tree.getroot(), "Target", Name="CompileCapturedAllocationSources", BeforeTargets="CoreCompile",
                               Condition="'$(AllocationCapturedGeneration)' == 'true'")
        item = ET.SubElement(target, "ItemGroup")
        ET.SubElement(item, "Analyzer", Remove="@(Analyzer)")
        ET.SubElement(item, "Compile", Include="generated-instrumented/**/*.cs")
        tree.write(project, encoding="utf-8", xml_declaration=True)
        receipt["instrumentedSources"] = {path.name: sha(path) for path in sorted(app.glob("*.cs"))}
        receipt["instrumentedProjectSha256"] = sha(project)
        receipt["generatedMapperPatchSha256"] = sha(app / "generated-mapper.patch")
        run("publish", ["dotnet", "publish", str(project), *common, "--no-restore", "-p:AllocationCapturedGeneration=true",
                        "-p:RestoreLockedMode=true", "-p:IlcTreatWarningsAsErrors=true", "-o", str(app / "out")], environment)
        executable = app / "out" / ("DbPerf.QueryPhases" if family == "korda" else "DbPerf.DapperQueryPhases")
        with executable.open("rb") as stream:
            if stream.read(4) != b"\x7fELF" or executable.with_suffix(".dll").exists():
                raise ValueError("Expected a standalone Linux Native AOT ELF")
        receipt["executableSha256"] = sha(executable)
        receipt["nativeImages"] = {str(path.relative_to(app / "out")): sha(path) for path in sorted((app / "out").rglob("libnw_database_*.so"))}
        if family == "korda" and receipt["nativeImages"] != original["native_images"]:
            raise ValueError("Allocation instrumentation must not replace the ordinary consumer's native images")
        receipt["assetGraphSha256"] = sha(app / "obj/project.assets.json")
        receipt["lockFileSha256"] = sha(app / "packages.lock.json")
        receipt["status"] = "built-not-run"
        write_receipt()
        shutil.copy2(app / "allocation-build-receipt.json", app / "out/allocation-build-receipt.json")
        print(str(app / "allocation-build-receipt.json"))
        return 0
    except Exception as error:
        receipt["status"] = "failed"
        receipt["failure"] = {"type": type(error).__name__, "message": str(error)}
        write_receipt()
        print(str(app / "allocation-build-receipt.json"), file=sys.stderr)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
