#!/usr/bin/env python3
"""Archive completed local observations and build/source receipts, never execute them."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import tempfile


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--series", type=Path, required=True)
    parser.add_argument("--host", type=Path, required=True)
    parser.add_argument("--continuation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="new .tar.gz; adjacent .manifest.json is also new")
    args = parser.parse_args()
    root, continuation = args.root.resolve(), args.continuation.resolve()
    output = args.output.resolve()
    manifest_path = output.with_name(output.name.removesuffix(".tar.gz") + ".manifest.json")
    require(output.name.endswith(".tar.gz") and not output.exists() and not manifest_path.exists(), "Use new archive paths")
    payloads, entries, checked, exclusions = {}, {}, {}, {}
    text_suffixes = {".json", ".jsonl", ".log", ".txt", ".cs", ".py", ".c", ".h", ".hpp", ".cpp",
                     ".md", ".xml", ".nuspec", ".csproj", ".props", ".targets", ".config", ".patch", ".sh", ".in"}

    def check(path, expected=None):
        path = Path(path).resolve(strict=True)
        data = path.read_bytes()
        digest = sha(data)
        require(expected is None or digest == expected, "Changed input: " + str(path))
        checked[str(path)] = digest
        return path, data, digest

    def add(path, expected=None, name=None):
        path, data, digest = check(path, expected)
        require(not path.is_symlink(), "Unexpected evidence symlink")
        if data.startswith(b"\x7fELF") or path.suffix not in text_suffixes:
            exclusions[str(path)] = {"sha256": digest, "bytes": len(data), "reason": "binary/package/database/tool input, retained by hash"}
            return
        name = name or "inputs/" + str(path.relative_to(root))
        require(name not in payloads or payloads[name] == data, "Archive name collision")
        payloads[name] = data
        entries[name] = {"path": name, "sourcePath": str(path), "bytes": len(data), "sha256": digest,
                         "sourceMtimeNs": path.stat().st_mtime_ns}

    def bind(value):
        if isinstance(value, dict):
            if isinstance(value.get("path"), str) and "sha256" in value:
                add(value["path"], value["sha256"])
            for child in value.values():
                bind(child)
        elif isinstance(value, list):
            for child in value:
                bind(child)

    add(args.series, name="observation/outer-series.json")
    add(args.host, name="observation/host-before.json")
    series = json.loads(args.series.read_text())
    require(len(series) == 10 and len({item["name"] for item in series}) == 10, "Expected the complete ten-run series")
    command_count = 0
    for run in series:
        require(run["exitCode"] == 0 and run["command"][-2] == "--output", "Outer run did not complete successfully")
        folder = Path(run["command"][-1]).resolve(strict=True)
        plan = json.loads((folder / "plan.json").read_text())
        check(folder / "plan.json", run["planSha256"])
        check(run["command"][-3], run["planSha256"])
        add(run["command"][-3], run["planSha256"], "plans/" + folder.name + ".json")
        add(run["log"], run["logSha256"], "outer-logs/" + Path(run["log"]).name)
        bind(plan.get("inputs", {}))
        for item in plan["commands"]:
            command_count += 1
            command = json.loads((folder / (item["name"] + ".command.json")).read_text())
            require(command["success"] is True and command["exitCode"] == 0
                    and command["timedOut"] is False and command["observerErrors"] == [], "Command did not finish normally")
            for name, digest in command["files"].items():
                check(folder / name, digest)
        # No database directory walk: only the runner's top-level original records.
        for path in sorted(folder.iterdir()):
            if path.is_file() and path.suffix in {".json", ".jsonl", ".log", ".txt"}:
                add(path, name="raw/" + folder.name + "/" + path.name)

    for pattern in ("analysis-phase-*-01.*", "analysis-single-row-0[12].*", "analysis-buffered-row-01.*",
                    "phase-*-index-01.json", "ci-*-final.json", "*-publication-receipt.json"):
        for path in sorted(continuation.glob(pattern)):
            add(path, name="analysis/" + path.name)
    for name in ("analyze_single_case.py", "analyze_buffered.py", "generate_single_case_plan.py",
                 "generate_buffered_plan.py", "observe_host.py", "prepare_load_index.py"):
        add(continuation / name, name="analysis-tools/" + name)
    add(__file__, name="archive_ready_row_short.py")
    for path in sorted((root / "artifacts").glob("*buffered*execution.json")):
        add(path, name="analysis/" + path.name)

    # Preserve the failed analyzer bytes too. This is a hash-proven reconstruction
    # of its two wrong expectations, not a new execution or a claimed old file.
    failed = json.loads((continuation / "analysis-single-row-01.json").read_text())
    original_path = continuation / "analyze_single_case.py"
    expected = failed["inputFiles"][str(original_path)]
    current = original_path.read_text()
    new = ('        # FindAsync builds From(...).SelectAll().SingleOrDefaultAsync; it is a\n'
           '        # query pull. Mutation pull is for returning mutations, absent here.\n'
           '        "nw_db_cursor_pull_create_v1": pulls * count,\n'
           '        "nw_db_cursor_pull_mutation_create_v1": 0,')
    old = ('        "nw_db_cursor_pull_create_v1": count if case == "numeric" else 0,\n'
           '        "nw_db_cursor_pull_mutation_create_v1": 0 if case == "numeric" else 3 * count,')
    require(current.count(new) == 1, "Cannot reconstruct the recorded analyzer failure precisely")
    restored = current.replace(new, old).encode()
    require(sha(restored) == expected, "Failed analyzer reconstruction does not match its recorded hash")
    name = "analysis-tools/failed-01/analyze_single_case.py"
    payloads[name] = restored
    entries[name] = {"path": name, "bytes": len(restored), "sha256": expected,
                     "provenance": "Reconstructed by reversing the exact two expectation changes; matches failed analysis input hash"}

    meta = {"schemaVersion": 1, "scope": "Ten completed local short-run groups and actual input/build records; no long-run credit",
            "series": [{"name": item["name"], "exitCode": item["exitCode"], "planSha256": item["planSha256"]} for item in series],
            "commandCountIncludingFixtures": command_count, "finalLongCredit": "0/4",
            "files": sorted(entries.values(), key=lambda item: item["path"]), "excludedBoundFiles": exclusions,
            "excludedTrees": ["PostgreSQL data", "SQLite fixture files", "ELF/native images", "NuGet archives", "build obj/bin/restore caches"],
            "failedAnalysis01Retained": True, "sourceHashChecks": checked}
    payloads["manifest.json"] = (json.dumps(meta, indent=2, sort_keys=True) + "\n").encode()
    payloads["SHA256SUMS"] = "".join(item["sha256"] + "  " + item["path"] + "\n" for item in meta["files"]).encode()

    def encode():
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w", format=tarfile.PAX_FORMAT) as archive:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size, info.mode = len(data), 0o644
                info.mtime = info.uid = info.gid = 0
                info.uname = info.gname = ""
                archive.addfile(info, io.BytesIO(data))
        return gzip.compress(stream.getvalue(), compresslevel=9, mtime=0)

    encoded = encode()
    require(encoded == encode(), "Archive encodings differ")
    with output.open("xb") as stream:
        stream.write(encoded)
    with tempfile.TemporaryDirectory(prefix="ready-row-short-readback-") as temporary:
        destination = Path(temporary)
        with tarfile.open(output, "r:gz") as archive:
            require(set(archive.getnames()) == set(payloads), "Archive member set differs")
            for info in archive.getmembers():
                require(info.isfile() and not Path(info.name).is_absolute() and ".." not in Path(info.name).parts, "Unsafe archive member")
                data = archive.extractfile(info).read()
                require(data == payloads[info.name], "Archived bytes differ")
                target = destination / info.name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        for name, data in payloads.items():
            require((destination / name).read_bytes() == data, "Extracted bytes differ")
    for path, expected in checked.items():
        require(sha(Path(path).read_bytes()) == expected, "Original source changed during archiving: " + path)
    meta.update(archivePath=str(output), archiveBytes=len(encoded), archiveSha256=sha(encoded), members=len(payloads),
                twoEncodingsByteEqual=True, everyArchivedAndExtractedByteCompared=True, allSourceFilesStillUnchanged=True)
    with manifest_path.open("x") as stream:
        json.dump(meta, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"archive": str(output), "sha256": sha(encoded), "bytes": len(encoded), "members": len(payloads),
                      "commands": command_count, "readback": True}))


if __name__ == "__main__":
    main()
