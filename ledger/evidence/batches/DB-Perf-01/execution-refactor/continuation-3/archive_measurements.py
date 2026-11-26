#!/usr/bin/env python3
"""Archive completed local observations without changing or qualifying them."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    root, target = args.workspace.resolve(), args.output.resolve()
    if target.exists() or target.with_suffix(".manifest.json").exists():
        raise ValueError("Use a new archive; previous evidence is immutable")
    files = {}

    def add(path, name):
        if name in files:
            raise ValueError("Duplicate archive path: " + name)
        files[name] = path.read_bytes()

    for kind in ("phases", "ffi", "allocation"):
        for provider in ("sqlite", "postgresql"):
            name = f"{kind}-{provider}-01"
            directory = root / "measurements" / name
            commands = sorted(directory.glob("*.command.json"))
            expected = 6 if kind == "ffi" else 9
            if len(commands) != expected:
                raise ValueError(f"{name}: incomplete command count")
            for path in commands:
                if not json.loads(path.read_text())["success"]:
                    raise ValueError("Unsuccessful observation must be indexed separately: " + str(path))
            for path in sorted(directory.iterdir()):
                if path.is_file():
                    add(path, "measurements/" + name + "/" + path.name)
            add(root / "measurements/plans" / (name + ".json"), "measurements/plans/" + name + ".json")
    for name in ("host-before-phases.json", "ordinary-inputs-before.json", "ordinary-inputs-after-01.json"):
        add(root / "measurements" / name, "measurements/" + name)

    diagnostics = [
        "ffi-before-sqlite-02", "ffi-before-postgresql", "ffi-candidate-sqlite-02", "ffi-candidate-postgresql-02",
        "allocation-before-sqlite-05", "allocation-before-postgresql",
        "allocation-candidate-sqlite", "allocation-candidate-postgresql",
        "allocation-dapper-sqlite-05", "allocation-dapper-postgresql",
    ]
    allowed = {".cs", ".csproj", ".json", ".props", ".targets", ".Config", ".patch", ".log", ".c", ".py"}
    for name in diagnostics:
        directory = root / "consumers" / name
        for path in sorted(directory.rglob("*")):
            relative = path.relative_to(directory)
            if not path.is_file() or any(part in {"packages", "feed", "obj", "bin", "out", ".git"} for part in relative.parts):
                continue
            if path.suffix in allowed:
                add(path, "consumers/" + name + "/" + relative.as_posix())
        provenance = directory / "out/allocation-build-receipt.json"
        if provenance.exists():
            add(provenance, "consumers/" + name + "/out/allocation-build-receipt.json")

    source = root / "worktrees/DB-Exec-02-candidate-0f3816c"
    for relative in ("benchmarks/db-perf/run.py", "benchmarks/db-perf/query-phases/summarize.py",
                     "benchmarks/db-perf/allocation-diagnostics/build.py",
                     "benchmarks/db-perf/allocation-diagnostics/BusinessAllocation.cs"):
        path = source / relative
        if path.exists():
            add(path, "tools/public0f/" + relative)
    for relative in ("benchmarks/db-perf/cursor-diagnostics/build.py", "benchmarks/db-perf/cursor-diagnostics/probe.c.in"):
        add(root / "worktrees/DB-Exec-02-continuation" / relative, "tools/local7d6d5f8/" + relative)

    entries = [{"path": name, "bytes": len(data), "sha256": digest(data)} for name, data in sorted(files.items())]
    manifest = {"schemaVersion": 1, "scope": "Actual intermediate candidate 0f observations; no final long-run credit. Instrumented FFI/allocation measurements have no timing credit.",
                "productSource": "0f3816c4006488821f40afde91bbbd717d57ccd6",
                "beforeProductSource": "f0078da720e07031bc56464995af6791c41aaae8",
                "files": entries, "excluded": ["Reproducible PostgreSQL/SQLite data", "Package caches", "Binary outputs; their exact hashes remain in receipts"]}
    files["MANIFEST.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode="w|") as archive:
            for name, data in sorted(files.items()):
                info = tarfile.TarInfo(name)
                info.size, info.mode, info.mtime = len(data), 0o644, 0
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                archive.addfile(info, io.BytesIO(data))
    with tarfile.open(target, "r:gz") as archive:
        for entry in entries:
            stream = archive.extractfile(entry["path"])
            actual = stream.read()
            if len(actual) != entry["bytes"] or digest(actual) != entry["sha256"]:
                raise ValueError("Archive verification failed: " + entry["path"])
    external = {"archive": target.name, "archiveBytes": target.stat().st_size, "archiveSha256": digest(target.read_bytes()),
                "entryCount": len(entries), "uncompressedBytes": sum(entry["bytes"] for entry in entries),
                "verifiedAllArchivedBytes": True, **manifest}
    target.with_suffix(".manifest.json").write_text(json.dumps(external, indent=2) + "\n")
    print(json.dumps({key: external[key] for key in ("archive", "archiveBytes", "archiveSha256", "entryCount", "uncompressedBytes", "verifiedAllArchivedBytes")}))


if __name__ == "__main__":
    main()
