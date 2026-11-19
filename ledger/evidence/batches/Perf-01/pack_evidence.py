#!/usr/bin/env python3
"""Pack allowlisted finalized Perf-01 JSON bytes; never run a workload or upload.

Source preparation only until the documented small fixture checks pass.
Chunks preserve exact input bytes and are independently gzip encoded. Private
files are never discovered through artifact paths or broad recursive globs.
"""
from __future__ import annotations

import argparse
import base64
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import urlsplit

HASH = re.compile(r"[0-9a-f]{64}\Z")
MAX_VALUE = 4 * 1024**2
MAX_CONTROL = 64 * 1024**2
MAX_BUNDLE = 16 * 1024**3
MAX_FILES = 128
MAX_CHUNKS = 20000
BINDINGS = {"build", "client-build", "direct-build", "packages", "native", "corpus", "policy", "source", "observer"}
FORBIDDEN_KEYS = {"password", "passwd", "pwd", "secret", "client_secret", "access_token", "refresh_token",
                  "token", "authorization", "cookie", "set-cookie", "cursorkey", "principals",
                  "headers_base64", "body_base64", "api_key", "apikey", "credentials", "credential",
                  "connectionstring", "connection_string", "private_key_pem", "privatekeypem"}
COMMON_OPTIONAL = ("controller-affinity-before.json", "controller-affinity-after.json",
                   "controller-affinity-end.json", "controller-affinity-restored.json",
                   "profile-driver.json", "postgres-profile-summary.json", "profiling.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def relative(name):
    require(isinstance(name, str), "Evidence path is not a string")
    path = PurePosixPath(name)
    require(name and not path.is_absolute() and "\\" not in name
            and all(part not in ("", ".", "..") for part in name.split("/")), "Unsafe evidence path")
    return path


def regular(root, name):
    relative(name)
    path = root
    for component in name.split("/"):
        path = path / component
        require(not path.is_symlink(), "Evidence symlinks are not publishable: " + name)
    require(path.resolve().is_relative_to(root), "Evidence path escaped selected root")
    require(stat.S_ISREG(path.stat().st_mode), "Evidence input is not a regular file: " + name)
    return path


def external_json(path):
    path = path.absolute()
    require(path.suffix == ".json", "Explicit metadata input must be JSON")
    anchor = Path(path.anchor)
    return regular(anchor, path.relative_to(anchor).as_posix())


def small(path):
    require(path.stat().st_size <= MAX_CONTROL, "Oversized control JSON")
    return json.loads(path.read_text())


def safe_value(value, key=None, depth=0):
    require(depth < 64, "Evidence nesting exceeds bound")
    if isinstance(value, dict):
        for name, child in value.items():
            require(name.lower() not in FORBIDDEN_KEYS, "Private field needs a separate reviewed projection: " + name)
            safe_value(child, name, depth + 1)
    elif isinstance(value, list):
        for child in value:
            safe_value(child, key, depth + 1)
    elif isinstance(value, str):
        require("-----BEGIN " not in value and not re.search(r"\bBearer\s+\S", value, re.I), "Credential-shaped text rejected")
        if key == "stderr":
            require(not value, "Nonempty embedded stderr needs explicit review outside this exact-byte packer")
        for match in re.finditer(r"(?:postgresql|postgres|https?)://[^\s\"<>]+", value):
            uri = urlsplit(match[0])
            if uri.username is not None or uri.password is not None:
                require(re.fullmatch(r"postgresql://nativeweave@127\.0\.0\.1:[0-9]{1,5}/postgres", match[0])
                        and uri.password is None and 0 < uri.port <= 65535,
                        "Unreviewed credential-bearing URI rejected")
        if key == "wire_base64":
            decoded = base64.b64decode(value, validate=True)
            require(len(decoded) <= MAX_VALUE, "Oversized raw IPC event")
            safe_value(json.loads(decoded), depth=depth + 1)
    elif isinstance(value, float):
        require(math.isfinite(value), "Nonfinite JSON value")
    else:
        require(value is None or type(value) in (bool, int), "Unexpected JSON scalar")


class JsonReader:
    """Walk JSON scalars without materializing DB's large top-level ledgers.

    Bounded reader pattern follows NativeWeave tests/Perf01/verify_long.py;
    here every scalar is checked and the original file remains unchanged.
    """
    def __init__(self, stream):
        self.stream, self.buffer, self.pos, self.eof = stream, "", 0, False
        self.decoder = json.JSONDecoder()

    def fill(self):
        self.buffer = self.buffer[self.pos:]
        self.pos = 0
        more = self.stream.read(65536)
        self.buffer += more
        self.eof = not more

    def peek(self):
        while True:
            while self.pos < len(self.buffer) and self.buffer[self.pos].isspace():
                self.pos += 1
            if self.pos < len(self.buffer):
                return self.buffer[self.pos]
            if self.eof:
                return ""
            self.fill()

    def take(self, char):
        require(self.peek() == char, "Malformed evidence JSON")
        self.pos += 1

    def scalar(self):
        self.peek()
        while True:
            try:
                value, end = self.decoder.raw_decode(self.buffer, self.pos)
                require(end - self.pos <= MAX_VALUE, "Oversized JSON scalar")
                if end < len(self.buffer) and self.buffer[end] in ",]}: \t\r\n" or self.eof and end == len(self.buffer):
                    self.pos = end
                    return value
            except json.JSONDecodeError:
                pass
            require(not self.eof and len(self.buffer) - self.pos <= MAX_VALUE, "Truncated or oversized JSON scalar")
            self.fill()

    def walk(self, key=None, depth=0):
        require(depth < 64, "Evidence nesting exceeds bound")
        first = self.peek()
        if first not in ("{", "["):
            safe_value(self.scalar(), key, depth)
            return
        close = "}" if first == "{" else "]"
        self.take(first)
        if self.peek() != close:
            while True:
                child_key = key
                if first == "{":
                    child_key = self.scalar()
                    require(isinstance(child_key, str) and child_key.lower() not in FORBIDDEN_KEYS,
                            "Private or malformed JSON key")
                    self.take(":")
                self.walk(child_key, depth + 1)
                if self.peek() == close:
                    break
                self.take(",")
        self.take(close)


def inspect_json(path):
    with path.open(encoding="utf-8") as stream:
        reader = JsonReader(stream)
        if path.suffix == ".jsonl":
            while reader.peek():
                reader.walk()
        else:
            reader.walk()
        require(reader.peek() == "", "Trailing bytes after JSON evidence")


def select(group, root):
    optional = list(COMMON_OPTIONAL)
    if group == "codec":
        required = ["summary.json", "plan.json", "result.json", "operations.jsonl", "events.jsonl", "resources.jsonl", "phase-progress.json"]
        optional += ["command.json"]
        require(small(regular(root, "result.json")).get("complete") is True, "Codec cell is not finalized")
    elif group in ("http", "grpc"):
        required = ["result.json", "plan.json", "adapter.json", "oracle.json", "profile.json", "requests.jsonl",
                    "dispatches.jsonl", "events.jsonl", "execution/receipt.json", "execution/ready.json", "execution/processes.json",
                    "execution/client/operations.jsonl", "execution/process-resources.jsonl", "execution/server/closed.json"]
        route = small(regular(root, "plan.json")).get("route")
        require(route in {"nativeweave-aot-rust", "direct-rust"}, "Unknown protocol route")
        required += ["execution/server/" + ("managed-resources.jsonl" if route == "nativeweave-aot-rust" else "native-resources.jsonl")]
        optional += ["started.json", "execution/server/native-resources.jsonl"] if route == "nativeweave-aot-rust" else ["started.json"]
        require(small(regular(root, "result.json")).get("status") == "completed", "Protocol cell is not finalized")
    else:
        required = ["summary.json", "progress.json", "frozen-inputs.json", "plan.json", "target.json", "dataset.json",
                    "observation.json", "observation.events.jsonl"]
        summary = small(regular(root, "summary.json"))
        require(summary.get("provider") == group, "Database group mismatch")
        require(small(regular(root, "progress.json")).get("state") in {"completed", "completed-invalid"}, "Database cell is not finalized")
        plan = small(regular(root, "plan.json"))
        original = Path(plan["oracle"]["dataset"]).parent
        recorded = Path(summary["application_receipt"]["path"])
        app = recorded.relative_to(original) if recorded.is_absolute() else recorded
        require(len(app.parts) == 3 and app.parts[0] == "applications" and app.name == "receipt.json", "Unexpected application receipt location")
        prefix = app.parent.as_posix()
        required += [prefix + "/" + name for name in ("receipt.json", "perf01.json", "generator-resources.jsonl",
                     "generator-observer-receipt.json", "application/resources.jsonl")]
        optional += [prefix + "/classified-errors.jsonl", "postgres/identity.json"]
        target = small(regular(root, "target.json"))
        if group == "postgresql":
            require(re.fullmatch(r"postgresql://nativeweave@127\.0\.0\.1:[0-9]{1,5}/postgres", target.get("postgres_base", "")),
                    "Database target is not the reviewed local trust URI")
    names = required + [name for name in optional if (root / name).exists()]
    return {name: regular(root, name) for name in names}, sorted(set(optional) - set(names))


def pack(args):
    root = args.cell.resolve(strict=True)
    output = args.output.resolve()
    require(not output.exists() and not output.is_relative_to(root), "Use a fresh bundle outside the cell")
    require(1 <= args.shard_mib <= 32, "Shard size must be 1..32 MiB of uncompressed bytes")
    receipt_path = external_json(args.receipt)
    receipt = small(receipt_path)
    require(receipt.get("task") == "Perf-01" and receipt.get("group") == args.group and type(receipt.get("accepted")) is bool,
            "Missing matching post-run verifier receipt")
    require(HASH.fullmatch(receipt.get("verifier_sha256", "")), "Missing verifier identity")
    selected, absent = select(args.group, root)
    expected = receipt["evidence_sha256"]
    require(isinstance(expected, dict) and expected, "Verifier input hashes are missing")
    expected = expected.copy()
    for name, digest in expected.items():
        relative(name)
        require(isinstance(digest, str) and HASH.fullmatch(digest), "Malformed verifier input hash")
    require(set(expected).issubset(selected), "Verifier consumed a file outside the reviewed publication allowlist")
    # A short cell can hit the long-duration gate before that verifier reads its
    # raw files. Still bind available producer hashes without following the
    # protocol result's private configuration/key entries.
    driver_hashes = (small(regular(root, "summary.json")).get("files", {}) if args.group == "codec" else
                     small(regular(root, "result.json")).get("evidence_sha256", {}) if args.group in {"http", "grpc"} else {})
    require(isinstance(driver_hashes, dict), "Malformed producer evidence hashes")
    original_driver_pins = {}
    for name, digest in driver_hashes.items():
        if name not in selected:
            continue
        require(isinstance(digest, str) and HASH.fullmatch(digest), "Malformed producer file hash")
        require(name not in expected or expected[name] == digest, "Verifier and producer hashes disagree")
        expected[name] = digest; original_driver_pins[name] = digest
    selected["duration-verification.json"] = receipt_path
    for item in args.binding:
        label, separator, name = item.partition("=")
        require(separator and label in BINDINGS and "bindings/" + label + ".json" not in selected, "Unknown or repeated binding label")
        path = external_json(Path(name))
        selected["bindings/" + label + ".json"] = path
    require(len(selected) <= MAX_FILES and sum(path.stat().st_size for path in selected.values()) <= MAX_BUNDLE,
            "Bundle exceeds the reviewed local file-count or byte bound")
    output.mkdir(parents=True)
    (output / "chunks").mkdir()
    records = []
    for ordinal, (name, path) in enumerate(sorted(selected.items())):
        before = path.stat()
        require(stat.S_ISREG(before.st_mode), "Input is not a regular file")
        inspect_json(path)
        total, newlines, raw = 0, 0, hashlib.sha256()
        chunks = []
        with path.open("rb") as stream:
            while block := stream.read(args.shard_mib * 1024**2):
                raw.update(block); total += len(block); newlines += block.count(b"\n")
                shard = "chunks/" + f"{ordinal:04d}-{len(chunks):06d}.gz"
                target = output / shard
                with target.open("xb") as destination:
                    with gzip.GzipFile(filename="", fileobj=destination, mode="wb", compresslevel=6, mtime=0) as compressed:
                        compressed.write(block)
                chunks.append({"path": shard, "raw_bytes": len(block), "raw_sha256": hashlib.sha256(block).hexdigest(),
                               "gzip_bytes": target.stat().st_size, "gzip_sha256": sha(target)})
        after = path.stat()
        require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
                (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) and total == before.st_size,
                "Evidence changed while packaging: " + name)
        require(name not in expected or raw.hexdigest() == expected[name], "Bound input changed: " + name)
        records.append({"path": name, "raw_bytes": total, "raw_sha256": raw.hexdigest(), "newline_count": newlines,
                        "transformation": "none; exact source bytes", "chunks": chunks})
    manifest = {"schema_version": 1, "task": "Perf-01", "group": args.group, "source_cell": str(root),
                "created_utc": datetime.now(timezone.utc).isoformat(), "packager_sha256": sha(Path(__file__)),
                "original_accepted": receipt["accepted"], "original_duration_credit_seconds": receipt.get("duration_credit_seconds"),
                "original_driver_file_sha256_checked": original_driver_pins,
                "source_verifier_sha256": receipt["verifier_sha256"], "shard_raw_limit_bytes": args.shard_mib * 1024**2,
                "encoding": "independent gzip members; concatenate decompressed chunks in listed order",
                "absent_optional": absent, "files": records,
                "scope": "Exact allowlisted synthetic evidence. Private configs, DB files, PEMs and binaries are excluded; conservative JSON guards still require owner review of the selected metadata. Packing does not grant measurement acceptance."}
    with (output / "manifest.json").open("x") as stream:
        json.dump(manifest, stream, indent=2, sort_keys=True); stream.write("\n")
    verify(output)
    print(str(output / "manifest.json"))


def verify(bundle, output=None):
    bundle = bundle.resolve(strict=True)
    manifest = small(regular(bundle, "manifest.json"))
    require(manifest.get("schema_version") == 1 and manifest.get("task") == "Perf-01", "Unknown bundle")
    limit = manifest["shard_raw_limit_bytes"]
    require(type(limit) is int and 0 < limit <= 32 * 1024**2, "Invalid decompression bound")
    require(isinstance(manifest.get("files"), list) and 0 < len(manifest["files"]) <= MAX_FILES, "Invalid file count")
    if output is not None:
        output = output.resolve()
        require(not output.exists() and not output.is_relative_to(bundle), "Restore destination must be new and outside the bundle")
        output.mkdir(parents=True)
    names, shard_names, all_bytes = set(), set(), 0
    for record in manifest["files"]:
        name = record["path"]; relative(name)
        require(name not in names and name.endswith((".json", ".jsonl")), "Unexpected or duplicate restored file")
        names.add(name)
        require(type(record["raw_bytes"]) is int and record["raw_bytes"] >= 0
                and isinstance(record["raw_sha256"], str) and HASH.fullmatch(record["raw_sha256"]), "Invalid raw file identity")
        all_bytes += record["raw_bytes"]
        require(all_bytes <= MAX_BUNDLE, "Bundle exceeds local total-byte bound")
        require(isinstance(record["chunks"], list), "Invalid chunk list")
        total, raw, target = 0, hashlib.sha256(), None
        try:
            if output is not None:
                target_path = output / name; target_path.parent.mkdir(parents=True, exist_ok=True)
                target = target_path.open("xb")
            for chunk in record["chunks"]:
                require(re.fullmatch(r"chunks/[0-9]{4,}-[0-9]{6,}\.gz", chunk["path"]), "Unexpected shard path")
                require(chunk["path"] not in shard_names, "Duplicate shard path")
                shard_names.add(chunk["path"])
                require(len(shard_names) <= MAX_CHUNKS, "Bundle exceeds local chunk-count bound")
                require(type(chunk["raw_bytes"]) is int and 0 < chunk["raw_bytes"] <= limit, "Invalid raw shard bound")
                require(type(chunk["gzip_bytes"]) is int and 0 < chunk["gzip_bytes"] <= limit + 65536,
                        "Invalid compressed shard bound")
                require(all(isinstance(chunk[key], str) and HASH.fullmatch(chunk[key])
                            for key in ("gzip_sha256", "raw_sha256")), "Invalid shard identity")
                path = regular(bundle, chunk["path"])
                require(path.stat().st_size == chunk["gzip_bytes"] and sha(path) == chunk["gzip_sha256"], "Compressed shard changed")
                observed, chunk_hash = 0, hashlib.sha256()
                with gzip.open(path, "rb") as compressed:
                    while block := compressed.read(65536):
                        observed += len(block)
                        require(observed <= chunk["raw_bytes"], "Decompressed shard exceeds recorded bound")
                        chunk_hash.update(block); raw.update(block); total += len(block)
                        require(total <= record["raw_bytes"], "Decompressed file exceeds recorded bound")
                        if target is not None: target.write(block)
                require(observed == chunk["raw_bytes"] and chunk_hash.hexdigest() == chunk["raw_sha256"], "Raw shard changed")
            require(total == record["raw_bytes"] and raw.hexdigest() == record["raw_sha256"], "Restored file differs")
        finally:
            if target is not None: target.close()
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("pack")
    create.add_argument("--group", choices=("codec", "http", "grpc", "sqlite", "postgresql"), required=True)
    create.add_argument("--cell", type=Path, required=True); create.add_argument("--receipt", type=Path, required=True)
    create.add_argument("--output", type=Path, required=True); create.add_argument("--shard-mib", type=int, default=8)
    create.add_argument("--binding", action="append", default=[], help="Reviewed JSON NAME=PATH; fixed labels only")
    check = commands.add_parser("verify"); check.add_argument("--bundle", type=Path, required=True)
    restore = commands.add_parser("restore"); restore.add_argument("--bundle", type=Path, required=True); restore.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "pack": pack(args)
    else:
        manifest = verify(args.bundle, getattr(args, "output", None))
        print(json.dumps({"verified_files": len(manifest["files"]), "original_accepted": manifest["original_accepted"]}))


if __name__ == "__main__":
    main()
