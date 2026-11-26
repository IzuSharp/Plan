#!/usr/bin/env python3
"""Retain raw local measurements and pinned inputs without executing a workload."""

import argparse
import datetime
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import sys
import tarfile

CHUNK = 1024 * 1024
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
EXCLUSION_REASONS = {
    "database": "Rebuildable database or database sidecar; retain original path and actual byte hash.",
    "package": "Package bytes remain at the original path; this evidence archive is not a binary distribution.",
    "binary": "Compiled executable, native/object, or symbol bytes remain at the original path.",
    "package-cache": "Explicitly excluded package-cache bytes; original path and actual byte hash are retained.",
    "binary-build-output": "Explicitly excluded rebuildable build output; original path and actual byte hash are retained.",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + "\n").encode()


def digest_stream(stream):
    digest = hashlib.sha256()
    while block := stream.read(CHUNK):
        digest.update(block)
    return digest.hexdigest()


def digest_file(path):
    with path.open("rb") as stream:
        return digest_stream(stream)


def absolute_path(value):
    path = Path(value)
    require(path.is_absolute() and ".." not in path.parts, "Use an absolute path without '..': " + str(path))
    return path


def under(path, root):
    return path == root or root in path.parents


def fingerprint(path):
    own = path.lstat()
    target = path.stat()
    require(stat.S_ISREG(target.st_mode), "Input is not a regular file: " + str(path))
    def fields(value):
        return (value.st_dev, value.st_ino, value.st_mode, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
    return (fields(own), fields(target), os.readlink(path) if path.is_symlink() else None)


def walk_files(root):
    require(root.is_dir() and not root.is_symlink(), "Input root must be a real directory: " + str(root))
    result = []
    def walk_error(error):
        raise error
    for current, directories, files in os.walk(root, followlinks=False, onerror=walk_error):
        directories.sort()
        files.sort()
        for directory in directories:
            child = Path(current) / directory
            require(not child.is_symlink(), "Directory symlink needs an explicitly retained real root: " + str(child))
            require(directory != ".git", "Do not archive repository metadata: " + str(child))
        for name in files:
            path = Path(current) / name
            fingerprint(path)
            result.append(path)
    return tuple(sorted(result))


def pointer_value(value, pointer):
    require(pointer.startswith("/"), "Inventory field must be an absolute JSON pointer")
    for component in pointer[1:].split("/"):
        require(not re.search(r"~(?![01])", component), "Invalid JSON pointer escape")
        component = component.replace("~1", "/").replace("~0", "~")
        require(isinstance(value, dict) and component in value, "Missing inventory field: " + pointer)
        value = value[component]
    return value


def exclusion(path, prefix, excluded_roots, excluded_files):
    if str(path) in excluded_files:
        return excluded_files[str(path)]
    for reason, root in excluded_roots:
        if under(path, root):
            return reason
    name = path.name.lower()
    if name.endswith((".nupkg", ".snupkg")):
        return "package"
    database_suffixes = (".db", ".sqlite", ".sqlite3")
    if prefix.startswith(b"SQLite format 3\x00") or any(
        name.endswith(suffix + tail) for suffix in database_suffixes for tail in ("", "-wal", "-shm", "-journal")
    ):
        return "database"
    if prefix.startswith(b"\x7fELF"):
        # Preserve a core dump as raw failure evidence, even though it also has an ELF header.
        endian = "little" if len(prefix) > 5 and prefix[5] == 1 else "big"
        if len(prefix) >= 18 and int.from_bytes(prefix[16:18], endian) == 4:
            return None
        return "binary"
    if prefix.startswith(b"MZ") or name.endswith((".dll", ".exe", ".pdb", ".o", ".obj", ".a", ".lib")) or re.search(r"\.so(?:\.[0-9]+)*\Z", name):
        return "binary"
    return None


class HashingReader:
    def __init__(self, stream):
        self.stream = stream
        self.digest = hashlib.sha256()
        self.bytes = 0

    def read(self, size=-1):
        block = self.stream.read(size)
        self.digest.update(block)
        self.bytes += len(block)
        return block


def add_tar_file(archive, name, size, stream):
    require(not name.startswith("/") and ".." not in Path(name).parts, "Unsafe archive member")
    info = tarfile.TarInfo(name)
    info.size = size
    info.mode = 0o644
    info.uid = info.gid = info.mtime = 0
    info.uname = info.gname = ""
    archive.addfile(info, stream)


def publish_new(source, destination):
    # Atomic no-replace publication also rejects dangling symlinks and a name
    # created after the caller's initial fresh-output check.
    os.link(source, destination, follow_symlinks=False)
    source.unlink()


def retain(args, started):
    measurements = absolute_path(args.measurements)
    roots = [measurements] + [absolute_path(value) for value in args.retain_root]
    output = absolute_path(args.output_dir)
    require(len(set(roots)) == len(roots), "Duplicate retained root")
    require(all(not under(output, root) and not under(output.resolve(strict=False), root.resolve(strict=True))
                for root in roots), "Output must be outside all retained roots")
    excluded_roots = []
    for reason, value in args.exclude_root:
        require(reason in EXCLUSION_REASONS, "Unknown exclusion reason: " + reason)
        excluded_roots.append((reason, absolute_path(value)))
    excluded_files = {}
    for reason, value in args.exclude_file:
        require(reason in EXCLUSION_REASONS, "Unknown exclusion reason: " + reason)
        path = str(absolute_path(value))
        require(path not in excluded_files, "Duplicate explicit excluded file")
        excluded_files[path] = reason
    records = {}
    inventories = []
    snapshots = {}

    def register(path, origin, expected=None):
        path = absolute_path(path)
        require(not under(path, output), "Input cannot be inside the new output directory")
        record = records.setdefault(str(path), {"source": str(path), "origins": [], "expectedSha256": None})
        if origin not in record["origins"]:
            record["origins"].append(origin)
        if expected is not None:
            require(isinstance(expected, str) and SHA256.fullmatch(expected), "Malformed expected SHA-256 for " + str(path))
            require(record["expectedSha256"] in (None, expected), "Conflicting expected hashes: " + str(path))
            record["expectedSha256"] = expected

    for root in roots:
        snapshots[str(root)] = walk_files(root)
        for path in snapshots[str(root)]:
            register(path, {"retainedRoot": str(root)})
    for value in args.retain_file:
        register(absolute_path(value), {"explicitFile": True})
    for path, reason in excluded_files.items():
        register(Path(path), {"explicitExcludedFile": reason})
    register(Path(__file__).absolute(), {"archiveTool": True})
    for path_text, pointer, expected in args.inventory:
        path = absolute_path(path_text)
        require(SHA256.fullmatch(expected), "Inventory requires its exact lowercase SHA-256")
        before = fingerprint(path)
        data = path.read_bytes()
        require(before == fingerprint(path), "Inventory changed while reading: " + str(path))
        require(hashlib.sha256(data).hexdigest() == expected, "Inventory file hash differs: " + str(path))
        inventory = pointer_value(json.loads(data), pointer)
        require(isinstance(inventory, dict) and len(inventory) > 0, "Inventory must be a nonempty path-to-SHA256 object")
        register(path, {"inventoryDocument": pointer}, expected)
        for original, digest in inventory.items():
            register(absolute_path(original), {"inventory": str(path), "pointer": pointer}, digest)
        inventories.append({"path": str(path), "pointer": pointer, "sha256": expected, "entries": len(inventory)})

    initial = {path: fingerprint(Path(path)) for path in records}
    partial = output / "evidence.tar.gz.partial"
    with partial.open("xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=6) as compressed:
            with tarfile.open(mode="w|", fileobj=compressed, format=tarfile.PAX_FORMAT) as archive:
                for key in sorted(records):
                    path = Path(key)
                    record = records[key]
                    require(fingerprint(path) == initial[key], "Input changed before reading: " + key)
                    with path.open("rb") as source:
                        prefix = source.read(64)
                        source.seek(0)
                        reason = exclusion(path, prefix, excluded_roots, excluded_files)
                        record["size"] = os.fstat(source.fileno()).st_size
                        record["symlinkTarget"] = initial[key][2]
                        record["resolvedSource"] = str(path.resolve(strict=True))
                        reader = HashingReader(source)
                        if reason:
                            record["disposition"] = "excluded"
                            record["reasonCode"] = reason
                            record["reason"] = EXCLUSION_REASONS[reason]
                            while reader.read(CHUNK):
                                pass
                        else:
                            relative = path.relative_to(measurements) if under(path, measurements) else Path(*path.parts[1:])
                            member = ("measurements/" if under(path, measurements) else "original-inputs/") + relative.as_posix()
                            record["disposition"] = "archived"
                            record["archiveMember"] = member
                            add_tar_file(archive, member, record["size"], reader)
                        require(reader.bytes == record["size"] and source.read(1) == b"", "Input length changed: " + key)
                        record["sha256"] = reader.digest.hexdigest()
                    require(initial[key] == fingerprint(path), "Input changed during reading: " + key)
                    require(record["expectedSha256"] in (None, record["sha256"]), "Pinned input hash differs: " + key)
                    record["origins"].sort(key=lambda value: json.dumps(value, sort_keys=True))
                manifest = {
                    "schemaVersion": 1, "scope": args.scope,
                    "purpose": "Original evidence retention; no correctness, performance, or final-duration credit.",
                    "measurementRoot": str(measurements), "retainedRoots": sorted(map(str, roots)),
                    "explicitExclusionRoots": [{"reason": reason, "path": str(root)} for reason, root in excluded_roots],
                    "explicitExclusionFiles": excluded_files,
                    "inventoryDocuments": inventories, "records": [records[path] for path in sorted(records)],
                    "binaryRecoveryClaim": False, "productExecutions": 0,
                    "compression": {"format": "tar+pax+gzip", "gzipMtime": 0, "gzipFilename": "", "level": 6,
                                    "memberOrder": "source path lexicographic, manifest last", "memberMtime": 0},
                }
                manifest_bytes = encode(manifest)
                add_tar_file(archive, "manifest.json", len(manifest_bytes), io.BytesIO(manifest_bytes))
    archived = {record["archiveMember"]: record for record in records.values() if record["disposition"] == "archived"}
    require(len(archived) == sum(record["disposition"] == "archived" for record in records.values()), "Archive path collision")
    expected_members = {name: (record["sha256"], record["size"]) for name, record in archived.items()}
    expected_members["manifest.json"] = (hashlib.sha256(manifest_bytes).hexdigest(), len(manifest_bytes))
    seen = set()
    with gzip.open(partial, "rb") as compressed:
        with tarfile.open(mode="r|", fileobj=compressed) as archive:
            for member in archive:
                require(member.isfile() and member.name in expected_members and member.name not in seen, "Unexpected archive member")
                expected, size = expected_members[member.name]
                require(member.size == size and member.uid == member.gid == member.mtime == 0, "Archive member metadata differs")
                stream = archive.extractfile(member)
                require(stream is not None and digest_stream(stream) == expected, "Archive member bytes differ")
                seen.add(member.name)
        # Reach gzip EOF so its trailer is checked as well as the tar members.
        while compressed.read(CHUNK):
            pass
    require(seen == set(expected_members), "Archive member missing")
    for path, record in records.items():
        require(fingerprint(Path(path)) == initial[path], "Input changed after archive: " + path)
        require(digest_file(Path(path)) == record["sha256"], "Input bytes changed after archive: " + path)
        require(fingerprint(Path(path)) == initial[path], "Input changed during final rehash: " + path)
    for root in roots:
        require(walk_files(root) == snapshots[str(root)], "Retained root inventory changed: " + str(root))
    require(all(fingerprint(Path(path)) == value for path, value in initial.items()), "Input changed during the final verification pass")
    with (output / "manifest.json").open("xb") as stream:
        stream.write(manifest_bytes)
    destination = output / "evidence.tar.gz"
    publish_new(partial, destination)
    excluded = [record for record in records.values() if record["disposition"] == "excluded"]
    receipt = {
        "schemaVersion": 1, "status": "retained-and-verified", "scope": args.scope,
        "startedUtc": started, "endedUtc": utc(), "outputDirectory": str(output),
        "archive": {"path": str(destination), "sha256": digest_file(destination), "bytes": destination.stat().st_size},
        "manifest": {"path": str(output / "manifest.json"), "sha256": hashlib.sha256(manifest_bytes).hexdigest()},
        "archivedOriginalFiles": len(archived), "archivedOriginalBytes": sum(record["size"] for record in archived.values()),
        "excludedOriginalFiles": len(excluded), "excludedOriginalBytes": sum(record["size"] for record in excluded),
        "originalInputsUnchanged": True, "completeArchiveReadback": True,
        "workloadsExecuted": 0, "binaryRecoveryClaim": False, "finalAcceptanceCredit": False,
    }
    with (output / "receipt.json").open("xb") as stream:
        stream.write(encode(receipt))
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measurements", required=True)
    parser.add_argument("--inventory", action="append", nargs=3, required=True, metavar=("JSON", "POINTER", "SHA256"))
    parser.add_argument("--retain-file", action="append", default=[])
    parser.add_argument("--retain-root", action="append", default=[])
    parser.add_argument("--exclude-root", action="append", nargs=2, default=[], metavar=("REASON", "PATH"))
    parser.add_argument("--exclude-file", action="append", nargs=2, default=[], metavar=("REASON", "PATH"))
    parser.add_argument("--scope", default="DB-Exec-10 continuation-7 local evidence")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output = absolute_path(args.output_dir)
    roots = [absolute_path(args.measurements)] + [absolute_path(value) for value in args.retain_root]
    require(all(not under(output, root) and not under(output.resolve(strict=False), root.resolve(strict=True))
                for root in roots), "Output must be outside all retained roots")
    require(not output.exists(), "Never overwrite an existing output directory")
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    started = utc()
    try:
        receipt = retain(args, started)
    except Exception as error:
        failure = {"schemaVersion": 1, "status": "failed", "startedUtc": started, "endedUtc": utc(),
                   "errorType": type(error).__name__, "error": str(error),
                   "partialOutputsPreserved": True, "workloadsExecuted": 0, "finalAcceptanceCredit": False}
        with (output / "failure.json").open("xb") as stream:
            stream.write(encode(failure))
        print(json.dumps(failure), file=sys.stderr)
        return 1
    print(json.dumps(receipt))
    return 0


if __name__ == "__main__":
    sys.exit(main())
