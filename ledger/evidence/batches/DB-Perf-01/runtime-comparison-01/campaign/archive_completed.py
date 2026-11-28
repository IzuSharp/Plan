#!/usr/bin/env python3
"""Offline, byte-preserving archive of this campaign after all eight terminal cells.

No benchmark, database, network, subprocess, original-file write, or extraction
onto the filesystem is performed. This utility is outside the frozen matrix.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tarfile
from typing import BinaryIO, Iterator
import zlib


CELLS = (
    "01-dapper-sqlite",
    "02-dapper-postgresql",
    "03-ef-workstation-sqlite",
    "04-ef-workstation-postgresql",
    "05-ef-satori-sqlite",
    "06-ef-satori-postgresql",
    "07-java-native-sqlite",
    "08-java-native-postgresql",
)
CELL_FIXED_FILES = (
    "result.json", "cell-status.json", "plan.json", "fixture-before.json",
    "fixture-after.json",
)
CELL_NAMED_SUFFIXES = (".command.json", ".resources.jsonl", ".stdout.log")
POSTGRES_FILES = (
    "postgres-owner.json", "postgres-stats-before.json", "postgres-stats-after.json",
    "postgres-init.log", "postgres.log", "postgres-settings.txt", "fixture.sql",
)
CAMPAIGN_FILES = (
    "host.json", "events.jsonl", "invocations.jsonl", "current.json",
    "execution-session.json", "continuation-03-session.json",
    "continuation-04-session.json", "continuation-05-session.json",
    "continuation-06-session.json", "continuation-07-session.json",
    "continuation-08-session.json",
)
ORIGINAL_FAILED_CELL = "02-dapper-postgresql"
ORIGINAL_FAILED_RESULT_SHA256 = "61f45dae1a6a687298e87e81bdae689fa26a9aae88cd25a60d62e8368de6a50c"
CHUNK = 1024 * 1024
METADATA_LIMIT = 1024 * 1024
GZIP_LEVEL = 9
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
FORBIDDEN_PARTS = frozenset(("pgdata", "target"))
FORBIDDEN_SUFFIXES = (".sqlite", ".sqlite-wal", ".sqlite-shm", ".db", ".elf", ".so", ".dll", ".exe")


class ArchiveError(RuntimeError):
    pass


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def safe_relative(value: str) -> tuple[str, ...]:
    """Reject unsafe names before either source opening or tar-member use."""
    if not isinstance(value, str) or not value or "\\" in value or "\0" in value:
        raise ArchiveError(f"Invalid relative record path: {value!r}")
    parts = tuple(value.split("/"))
    if any(part in ("", ".", "..") or ":" in part for part in parts):
        raise ArchiveError(f"Unsafe relative record path: {value!r}")
    if PurePosixPath(value).is_absolute() or any(part.lower() in FORBIDDEN_PARTS for part in parts):
        raise ArchiveError(f"Excluded record path: {value!r}")
    if any(part.lower().endswith(FORBIDDEN_SUFFIXES) for part in parts):
        raise ArchiveError(f"Excluded database/binary path: {value!r}")
    return parts


def absolute_without_symlinks(value: str | Path) -> Path:
    # abspath is lexical; unlike resolve(), it does not follow a symlink.
    raw = os.fspath(value)
    if "\0" in raw or ".." in Path(raw).parts:
        raise ArchiveError("Parent traversal is not an accepted directory argument")
    return Path(os.path.abspath(raw))


def open_absolute_directory(path: Path) -> int:
    """Open every absolute-directory component with O_NOFOLLOW."""
    if not path.is_absolute():
        raise ArchiveError("Directory must be absolute")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    descriptor = os.open("/", flags)
    try:
        for component in path.parts[1:]:
            child = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def snapshot(info: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns, info.st_mode)


class ReadOnlyTree:
    def __init__(self, path: Path):
        self.path = path
        self.fd = open_absolute_directory(path)
        self.identity = (os.fstat(self.fd).st_dev, os.fstat(self.fd).st_ino)

    def close(self) -> None:
        os.close(self.fd)

    @contextmanager
    def open(self, relative: str) -> Iterator[BinaryIO]:
        parts = safe_relative(relative)
        directory = os.dup(self.fd)
        descriptor = None
        try:
            for component in parts[:-1]:
                child = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                dir_fd=directory)
                os.close(directory)
                directory = child
            descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=directory)
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise ArchiveError(f"Required raw record is not a regular file: {relative}")
            with os.fdopen(descriptor, "rb") as stream:
                descriptor = None
                yield stream
        finally:
            if descriptor is not None:
                os.close(descriptor)
            os.close(directory)

    def check_root_identity(self) -> None:
        descriptor = open_absolute_directory(self.path)
        try:
            observed = os.fstat(descriptor)
            if (observed.st_dev, observed.st_ino) != self.identity:
                raise ArchiveError("Source campaign directory was replaced during archival")
        finally:
            os.close(descriptor)


@dataclass(frozen=True)
class Record:
    path: str
    size: int
    identity: tuple[int, int, int, int, int, int]


class HashingReader:
    def __init__(self, stream: BinaryIO):
        self.stream = stream
        self.hash = hashlib.sha256()
        self.count = 0

    def read(self, count: int = -1) -> bytes:
        data = self.stream.read(count)
        self.hash.update(data)
        self.count += len(data)
        return data


def read_small_json(tree: ReadOnlyTree, relative: str) -> tuple[dict, str]:
    with tree.open(relative) as stream:
        before = snapshot(os.fstat(stream.fileno()))
        if before[2] > METADATA_LIMIT:
            raise ArchiveError(f"Status metadata exceeds the bounded read limit: {relative}")
        data = stream.read(METADATA_LIMIT + 1)
        if len(data) > METADATA_LIMIT or snapshot(os.fstat(stream.fileno())) != before:
            raise ArchiveError(f"Status changed or exceeded its limit: {relative}")
    value = json.loads(data)
    if not isinstance(value, dict):
        raise ArchiveError(f"Expected a JSON object: {relative}")
    return value, sha256_bytes(data)


def terminal_outcomes(tree: ReadOnlyTree) -> list[dict]:
    outcomes = []
    for cell in CELLS:
        value, status_hash = read_small_json(tree, f"{cell}/cell-status.json")
        state = value.get("status")
        failures = value.get("failures")
        result_hash = value.get("resultSha256")
        finished = value.get("finishedUtc")
        if value.get("name") != cell or state not in ("passed", "failed"):
            raise ArchiveError(f"Cell is absent, nonterminal, or named incorrectly: {cell}")
        if not isinstance(finished, str) or not finished.strip():
            raise ArchiveError(f"Terminal cell lacks a completion timestamp: {cell}")
        if not isinstance(failures, list) or not all(isinstance(item, str) for item in failures):
            raise ArchiveError(f"Invalid recorded failures list: {cell}")
        if state == "passed" and failures:
            raise ArchiveError(f"Contradictory passed status with failures: {cell}")
        if not isinstance(result_hash, str) or not SHA256_RE.fullmatch(result_hash):
            raise ArchiveError(f"Missing/invalid resultSha256 in terminal status: {cell}")
        if cell == ORIGINAL_FAILED_CELL and (
            state != "failed" or failures != ["released_idle"] or result_hash != ORIGINAL_FAILED_RESULT_SHA256
        ):
            raise ArchiveError("The original 02 failed result/status was replaced; preserve that original evidence")
        outcomes.append({"name": cell, "status": state, "failures": failures, "finishedUtc": finished,
                         "recordedResultSha256": result_hash, "statusFileSha256": status_hash})
    return outcomes


def explicit_groups() -> dict[str, tuple[str, ...]]:
    groups = {}
    for cell in CELLS:
        names = list(CELL_FIXED_FILES) + [cell + suffix for suffix in CELL_NAMED_SUFFIXES]
        if cell.endswith("-postgresql"):
            names.extend(POSTGRES_FILES)
        groups[cell + ".tar.gz"] = tuple(sorted(f"{cell}/{name}" for name in names))
    groups["campaign-metadata.tar.gz"] = tuple(sorted(CAMPAIGN_FILES))
    paths = [path for members in groups.values() for path in members]
    if len(paths) != len(set(paths)):
        raise ArchiveError("Internal explicit allowlist contains duplicate paths")
    for path in paths:
        safe_relative(path)
    return groups


def inspect_records(tree: ReadOnlyTree, groups: dict[str, tuple[str, ...]]) -> dict[str, Record]:
    records = {}
    for path in sorted(path for members in groups.values() for path in members):
        with tree.open(path) as stream:
            info = os.fstat(stream.fileno())
            prefix = stream.read(16)
            if prefix.startswith(b"\x7fELF") or prefix.startswith(b"SQLite format 3\0"):
                raise ArchiveError(f"Excluded ELF/SQLite content under a raw-record name: {path}")
            if snapshot(os.fstat(stream.fileno())) != snapshot(info):
                raise ArchiveError(f"Raw record changed during inventory: {path}")
            records[path] = Record(path, info.st_size, snapshot(info))
    return records


def create_output(evidence: ReadOnlyTree, output: Path) -> int:
    if output.parent != evidence.path / "raw" or output.name in ("", ".", ".."):
        raise ArchiveError("--output must be a new direct child of EVID/raw")
    try:
        os.mkdir("raw", 0o755, dir_fd=evidence.fd)
    except FileExistsError:
        pass
    raw_fd = os.open("raw", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                     dir_fd=evidence.fd)
    try:
        # No reuse, replacement, or overwrite of a prior archival directory.
        os.mkdir(output.name, 0o755, dir_fd=raw_fd)
        return os.open(output.name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                       dir_fd=raw_fd)
    finally:
        os.close(raw_fd)


def new_output(output_fd: int, name: str) -> BinaryIO:
    if len(safe_relative(name)) != 1:
        raise ArchiveError("Output artifacts must be simple filenames")
    descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                         0o644, dir_fd=output_fd)
    return os.fdopen(descriptor, "wb")


def write_output(output_fd: int, name: str, data: bytes) -> dict:
    with new_output(output_fd, name) as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return {"path": name, "bytes": len(data), "sha256": sha256_bytes(data)}


@contextmanager
def existing_output(output_fd: int, name: str) -> Iterator[BinaryIO]:
    descriptor = os.open(name, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=output_fd)
    if not stat.S_ISREG(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise ArchiveError("Output artifact was replaced by a non-regular file")
    with os.fdopen(descriptor, "rb") as stream:
        yield stream


def archive_group(tree: ReadOnlyTree, output_fd: int, archive: str,
                  members: tuple[str, ...], records: dict[str, Record]) -> tuple[dict, list[dict]]:
    originals = []
    with new_output(output_fd, archive) as raw:
        with gzip.GzipFile(fileobj=raw, filename="", mode="wb", compresslevel=GZIP_LEVEL, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w|", format=tarfile.USTAR_FORMAT) as tar:
                for path in members:
                    record = records[path]
                    with tree.open(path) as source:
                        if snapshot(os.fstat(source.fileno())) != record.identity:
                            raise ArchiveError(f"Original changed since inventory: {path}")
                        reader = HashingReader(source)
                        info = tarfile.TarInfo(path)
                        info.size = record.size
                        info.type = tarfile.REGTYPE
                        info.mode = 0o644
                        info.uid = info.gid = 0
                        info.uname = info.gname = ""
                        info.mtime = 0
                        tar.addfile(info, reader)
                        if reader.count != record.size or snapshot(os.fstat(source.fileno())) != record.identity:
                            raise ArchiveError(f"Original changed while copying: {path}")
                        originals.append({"path": path, "bytes": reader.count,
                                          "sha256": reader.hash.hexdigest(), "archive": archive})
        raw.flush()
        os.fsync(raw.fileno())
    with existing_output(output_fd, archive) as compressed:
        reader = HashingReader(compressed)
        while reader.read(CHUNK):
            pass
    result = {"path": archive, "bytes": reader.count, "sha256": reader.hash.hexdigest(),
              "memberCount": len(originals), "originalPayloadBytes": sum(item["bytes"] for item in originals)}
    return result, originals


def verify_archive(output_fd: int, archive: dict, originals: list[dict]) -> list[dict]:
    expected = {item["path"]: item for item in originals}
    observed = []
    names = set()
    with existing_output(output_fd, archive["path"]) as raw:
        header = raw.read(10)
        if len(header) != 10 or header[:3] != b"\x1f\x8b\x08" or header[3] != 0 or header[4:8] != bytes(4):
            raise ArchiveError("Gzip header is not the required filename-free, mtime=0 encoding")
        raw.seek(0)
        with gzip.GzipFile(fileobj=raw, mode="rb") as zipped:
            # Read member contents only; never extract a member onto the filesystem.
            with tarfile.open(fileobj=zipped, mode="r:") as tar:
                for member in tar:
                    safe_relative(member.name)
                    if member.name not in expected or member.name in names or member.type != tarfile.REGTYPE:
                        raise ArchiveError(f"Unexpected, duplicate, or non-file tar member: {member.name}")
                    if (member.uid, member.gid, member.uname, member.gname, member.mtime, member.mode) != (0, 0, "", "", 0, 0o644):
                        raise ArchiveError(f"Nondeterministic tar metadata: {member.name}")
                    source = expected[member.name]
                    if member.size != source["bytes"]:
                        raise ArchiveError(f"Tar member length mismatch: {member.name}")
                    extracted = tar.extractfile(member)
                    if extracted is None:
                        raise ArchiveError(f"Tar member has no readable payload: {member.name}")
                    with extracted:
                        reader = HashingReader(extracted)
                        while reader.read(CHUNK):
                            pass
                    if reader.count != source["bytes"] or reader.hash.hexdigest() != source["sha256"]:
                        raise ArchiveError(f"Decompressed bytes differ from original SHA-256: {member.name}")
                    names.add(member.name)
                    observed.append({"archive": archive["path"], "path": member.name,
                                     "bytes": reader.count, "sha256": reader.hash.hexdigest(),
                                     "matchedOriginal": True})
            # Drain to gzip EOF to check CRC/trailer and reject nonzero trailing tar data.
            while tail := zipped.read(CHUNK):
                if tail.strip(b"\0"):
                    raise ArchiveError("Nonzero data appears after the tar end marker")
        raw.seek(0)
        compressed = HashingReader(raw)
        while compressed.read(CHUNK):
            pass
        if compressed.count != archive["bytes"] or compressed.hash.hexdigest() != archive["sha256"]:
            raise ArchiveError("Compressed archive bytes changed during readback")
    if names != set(expected):
        raise ArchiveError("Archive is missing one or more explicitly required raw members")
    return observed


def check_originals_unchanged(tree: ReadOnlyTree, records: dict[str, Record]) -> None:
    tree.check_root_identity()
    for path, record in records.items():
        with tree.open(path) as stream:
            if snapshot(os.fstat(stream.fileno())) != record.identity:
                raise ArchiveError(f"Original changed before completion: {path}")


def check_output_location(evidence: ReadOnlyTree, output: Path, output_fd: int) -> None:
    # Reopen the reported absolute path without following any symlink. Keeping an
    # fd alone is insufficient if a parent or output directory has been renamed.
    evidence.check_root_identity()
    descriptor = open_absolute_directory(output)
    try:
        observed, expected = os.fstat(descriptor), os.fstat(output_fd)
        if (observed.st_dev, observed.st_ino) != (expected.st_dev, expected.st_ino):
            raise ArchiveError("Reported output directory was replaced during archival")
    finally:
        os.close(descriptor)


def run(campaign: Path, evidence_root: Path, output: Path) -> dict:
    source = ReadOnlyTree(campaign)
    evidence = None
    output_fd = None
    try:
        # The existing lock is opened read-only, never created/truncated/replaced.
        with source.open("campaign.lock") as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise ArchiveError("Campaign writer is active; nonblocking shared lock was unavailable") from error
            outcomes = terminal_outcomes(source)
            groups = explicit_groups()
            records = inspect_records(source, groups)
            evidence = ReadOnlyTree(evidence_root)
            output_fd = create_output(evidence, output)
            write_output(output_fd, "INCOMPLETE", b"Archive in progress; this directory is not a completed archive.\n")
            archives = []
            originals = []
            checks = []
            for archive, members in groups.items():
                compressed, raw_records = archive_group(source, output_fd, archive, members, records)
                checks.extend(verify_archive(output_fd, compressed, raw_records))
                archives.append(compressed)
                originals.extend(raw_records)
            by_path = {item["path"]: item for item in originals}
            for outcome in outcomes:
                cell = outcome["name"]
                if by_path[cell + "/result.json"]["sha256"] != outcome["recordedResultSha256"]:
                    raise ArchiveError(f"Original result bytes do not match terminal resultSha256: {cell}")
                if by_path[cell + "/cell-status.json"]["sha256"] != outcome["statusFileSha256"]:
                    raise ArchiveError(f"Terminal status bytes changed after the terminal-state gate: {cell}")
            check_originals_unchanged(source, records)
            check_output_location(evidence, output, output_fd)
            manifest = {
                "schema": "DB-Runtime-Compare-01.raw-archive.v1",
                "sourceCampaignDirectoryName": campaign.name,
                "lock": "campaign.lock: LOCK_SH | LOCK_NB held throughout inventory/copy/readback/manifest",
                "allEightCellsTerminal": True,
                "recordedCellOutcomes": outcomes,
                "originalFailed02Preserved": True,
                "recordedOutcomeCounts": {state: sum(item["status"] == state for item in outcomes)
                                          for state in ("passed", "failed")},
                "scope": "Archive byte verification; recorded benchmark outcomes retain their original status and failures",
                "sourceFiles": sorted(originals, key=lambda item: item["path"]),
                "archives": sorted(archives, key=lambda item: item["path"]),
                "compression": {"format": "USTAR+gzip", "gzipMtime": 0, "gzipFilename": "",
                                "gzipLevel": GZIP_LEVEL, "tarUid": 0, "tarGid": 0, "tarMode": "0644",
                                "tarMtime": 0, "pythonVersion": sys.version.split()[0],
                                "zlibVersion": zlib.ZLIB_VERSION, "zlibRuntimeVersion": zlib.ZLIB_RUNTIME_VERSION},
                "selection": "Explicit mandatory filenames only; no globbing, directory recursion, symlink following, SQLite/pgdata/ELF/target inclusion",
            }
            manifest_file = write_output(output_fd, "manifest.json", canonical_json(manifest))
            verification = {
                "schema": "DB-Runtime-Compare-01.archive-readback.v1",
                "archiveVerificationStatus": "verified",
                "meaning": "Every decompressed member length and SHA-256 matched the original bytes read under the shared campaign lock",
                "originalFilesChangedByTool": False,
                "archiveCount": len(archives), "originalFileCount": len(originals),
                "verifiedMemberCount": len(checks),
                "manifestSha256": manifest_file["sha256"],
                "members": sorted(checks, key=lambda item: (item["archive"], item["path"])),
            }
            verification_file = write_output(output_fd, "verification.json", canonical_json(verification))
            sums = sorted(archives + [manifest_file, verification_file], key=lambda item: item["path"])
            write_output(output_fd, "SHA256SUMS", "".join(f'{item["sha256"]}  {item["path"]}\n' for item in sums).encode("ascii"))
            os.fsync(output_fd)
            check_output_location(evidence, output, output_fd)
            os.unlink("INCOMPLETE", dir_fd=output_fd)
            os.fsync(output_fd)
            check_output_location(evidence, output, output_fd)
            return {"output": str(output), "archiveCount": len(archives), "originalFileCount": len(originals),
                    "archiveVerificationStatus": "verified", "recordedOutcomeCounts": manifest["recordedOutcomeCounts"]}
    except BaseException as error:
        if output_fd is not None:
            # This also covers a late failure after INCOMPLETE was unlinked
            # (e.g. directory fsync or final path-identity validation failed).
            try:
                write_output(output_fd, "INCOMPLETE", b"Archival failed; this directory is incomplete.\n")
            except FileExistsError:
                pass
            except BaseException:
                pass
            try:
                write_output(output_fd, "failure.json", canonical_json({"archiveVerificationStatus": "incomplete",
                    "errorType": type(error).__name__, "error": str(error),
                    "originalsModified": False, "resume": "Do not reuse this directory; inspect the error and select a new output directory"}))
            except BaseException:
                pass
            try:
                os.fsync(output_fd)
            except BaseException:
                pass
        raise
    finally:
        if output_fd is not None:
            os.close(output_fd)
        if evidence is not None:
            evidence.close()
        source.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path, help="Original long-runs/campaign-01 directory")
    parser.add_argument("--output", required=True, type=Path, help="New direct child of this evidence directory's raw/")
    parser.add_argument("--cpu", type=int, default=8, help="Pin the offline archive process to this one CPU (default: 8)")
    options = parser.parse_args()
    if options.cpu < 0:
        parser.error("--cpu must be nonnegative")
    os.sched_setaffinity(0, {options.cpu})
    campaign = absolute_without_symlinks(options.campaign)
    output = absolute_without_symlinks(options.output)
    evidence_root = absolute_without_symlinks(Path(__file__).parent.parent)
    if output.parent != evidence_root / "raw":
        parser.error("--output must be a new direct EVID/raw child")
    result = run(campaign, evidence_root, output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ArchiveError, OSError, ValueError, tarfile.TarError, EOFError) as error:
        print(f"Archive refused or incomplete: {error}", file=sys.stderr)
        raise SystemExit(2)
