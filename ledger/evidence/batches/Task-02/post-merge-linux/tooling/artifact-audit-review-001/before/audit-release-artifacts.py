#!/usr/bin/env python3
"""Read-only consistency audit of existing HelloWorld release artifact ZIPs.

No network, subprocess, extraction, credential access, publication or test execution.
The output is a fresh evidence directory; the input archives remain untouched.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import re
import stat
import sys
import zipfile


PACKAGE = "NativeWeave.HelloWorld"
RID = "linux-x64"
HEX = re.compile(r"[0-9a-f]{64}")
INTEROP_PASS = ("PASS: default, named/delegate calls, Unicode, NUL, empty, size "
                "boundaries, invalid input and 1000 concurrent greetings.")
# Local reader bounds, not new product/release acceptance limits.
MAX_MEMBER = 256 * 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def stream_sha(stream):
    value = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        value.update(block)
    return value.hexdigest()


def safe_name(name):
    path = name[:-1] if name.endswith("/") else name
    return (bool(path) and not path.startswith("/") and "\\" not in path
            and not re.match(r"^[A-Za-z]:", path)
            and all(part not in ("", ".", "..") for part in path.split("/"))
            and not any(ord(character) < 32 or ord(character) == 127 for character in name))


def index_zip(archive):
    names = {}
    for info in archive.infolist():
        name = info.filename
        if (info.orig_filename != name or not safe_name(name) or name in names
                or stat.S_ISLNK(info.external_attr >> 16) or info.flag_bits & 1):
            raise ValueError(f"Unsafe, duplicate, symlink or encrypted ZIP member: {name!r}")
        names[name] = info
    return names


def read_member(archive, names, name):
    info = names[name]
    if info.is_dir() or info.file_size > MAX_MEMBER:
        raise ValueError(f"Expected a bounded regular ZIP member: {name!r}")
    with archive.open(info) as stream:
        data = stream.read(MAX_MEMBER + 1)
    if len(data) > MAX_MEMBER or len(data) != info.file_size:
        raise ValueError(f"ZIP member length differs or exceeds local reader bound: {name!r}")
    return data


def bundle_prefix(names, filename):
    matches = [name for name in names if name == filename or name.endswith("/" + filename)]
    if len(matches) != 1:
        raise ValueError(f"Expected one unambiguous {filename}; found {len(matches)}")
    return matches[0][:-len(filename)]


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def parse_json(data):
    def reject_constant(value):
        raise ValueError(f"Non-JSON numeric constant: {value}")
    result = json.loads(data.decode("utf-8"), object_pairs_hook=object_pairs,
                        parse_constant=reject_constant)
    if not isinstance(result, dict):
        raise ValueError("Expected a JSON object")
    return result


class Audit:
    def __init__(self, args):
        self.args = args
        self.output = args.output.resolve()
        self.output.mkdir(parents=True, exist_ok=False)
        (self.output / "raw").mkdir()
        self.report = {
            "schemaVersion": 1,
            "purpose": "Read-only audit of retained existing Linux HelloWorld release evidence",
            "createdUtc": datetime.now(timezone.utc).isoformat(),
            "expectedMergeCommit": args.merge, "expectedVersion": args.version,
            "scriptSha256": sha(Path(__file__).read_bytes()),
            "inputs": {}, "retained": [], "checks": [], "errors": [],
            "scope": {
                "packageId": PACKAGE, "rid": RID,
                "independentlyHashed": "Input ZIPs, selected raw records/logs, candidate nupkg and its native asset",
                "publisherAttested": ["Registry signature verification", "Unsigned candidate/registry payload entry equality",
                                       "Exact registry package consumer execution and isolation"],
                "limitations": [
                    "Registry nupkg is absent from the publication artifact; signature and payload comparison are not rerun.",
                    "The publishing job log separately records dotnet nuget verify --all; confirm its successful workflow context.",
                    "This script does not establish GitHub artifact provenance, workflow conclusions or PR merge status.",
                    "Registry pristineMachine is declared false; separate candidate container evidence is not registry pristine evidence.",
                    "This covers the existing HelloWorld preview only, with no other Task-02 package/platform claim."],
            },
        }

    def check(self, label, passed, actual=None):
        self.report["checks"].append({"check": label, "passed": bool(passed), "actual": actual})

    def retain(self, source, member, name, data):
        target = self.output / "raw" / name
        target.write_bytes(data)
        self.report["retained"].append({"input": source, "member": member,
                                         "path": "raw/" + name, "bytes": len(data), "sha256": sha(data)})

    def record_json(self, source, archive, names, member, retained_name):
        data = read_member(archive, names, member)
        self.retain(source, member, retained_name, data)
        return parse_json(data), data

    def open_archive(self, source, path, inspect):
        with path.open("rb") as stream:
            initial = stream_sha(stream)
            self.report["inputs"][source] = {"path": str(path.resolve()), "bytes": stream.tell(), "sha256": initial}
            stream.seek(0)
            try:
                with zipfile.ZipFile(stream) as archive:
                    names = index_zip(archive)
                    self.report["inputs"][source]["members"] = [
                        {"path": name, "bytes": info.file_size} for name, info in names.items()]
                    inspect(archive, names)
            finally:
                stream.seek(0)
                self.check(source + " archive unchanged during audit", stream_sha(stream) == initial)

    def candidate(self, archive, names):
        prefix = bundle_prefix(names, "manifest.json")
        package_name = f"{PACKAGE}.{self.args.version}.nupkg"
        manifest, manifest_data = self.record_json("candidate", archive, names, prefix + "manifest.json", "candidate-manifest.json")
        self.manifest = manifest
        sums_data = read_member(archive, names, prefix + "SHA256SUMS")
        self.retain("candidate", prefix + "SHA256SUMS", "candidate-SHA256SUMS", sums_data)
        sums = {}
        for line in sums_data.decode("utf-8").splitlines():
            parts = line.split("  ", 1)
            if len(parts) != 2 or not HEX.fullmatch(parts[0]) or parts[1] in sums:
                raise ValueError("Malformed or duplicate candidate checksum entry")
            sums[parts[1]] = parts[0]
        self.check("Candidate checksum inventory", set(sums) == {package_name, "manifest.json"}, sorted(sums))
        self.check("Candidate external manifest checksum", sums.get("manifest.json") == sha(manifest_data), sha(manifest_data))
        package = read_member(archive, names, prefix + package_name)
        self.candidate_sha = sha(package)
        self.report["candidatePackage"] = {"member": prefix + package_name, "bytes": len(package), "sha256": self.candidate_sha}
        self.check("Candidate nupkg checksum", sums.get(package_name) == self.candidate_sha, self.candidate_sha)
        for key, expected in (("packageId", PACKAGE), ("packageVersion", self.args.version),
                              ("rid", RID), ("sourceCommit", self.args.merge)):
            self.check("Candidate " + key, manifest.get(key) == expected, manifest.get(key))
        self.check("Candidate sourceDirty is false", manifest.get("sourceDirty") is False, manifest.get("sourceDirty"))
        self.check("Candidate native SHA-256 syntax", isinstance(manifest.get("nativeSha256"), str)
                   and HEX.fullmatch(manifest["nativeSha256"]) is not None, manifest.get("nativeSha256"))
        native_path = manifest.get("nativePath")
        if not isinstance(native_path, str) or not safe_name(native_path):
            raise ValueError("Invalid nativePath in candidate manifest")
        self.check("Candidate native path is Linux x64", native_path.startswith("runtimes/linux-x64/native/"), native_path)
        with zipfile.ZipFile(io.BytesIO(package)) as payload:
            members = index_zip(payload)
            embedded, _ = self.record_json("candidate nupkg", payload, members, "nativeweave/manifest.json", "candidate-embedded-manifest.json")
            self.check("Embedded and external manifests match", embedded == manifest)
            native = read_member(payload, members, native_path)
            self.check("Actual candidate native bytes match manifest", sha(native) == manifest.get("nativeSha256"), sha(native))
            self.report["candidateNative"] = {"member": native_path, "bytes": len(native), "sha256": sha(native)}

    def publication(self, archive, names):
        prefix = bundle_prefix(names, "publication.json")
        published, _ = self.record_json("publication", archive, names, prefix + "publication.json", "publication.json")
        consumer, _ = self.record_json("publication", archive, names, prefix + "consumer-result.json", "consumer-result.json")
        self.check("Final publication status", published.get("status") == "published-and-consumed", published.get("status"))
        self.check("Publication version", published.get("version") == self.args.version, published.get("version"))
        for key in ("signatureVerified", "unsignedPayloadEntriesEqual", "registryPackageJitAndAotExecuted"):
            self.check("Publication " + key + " is true", published.get(key) is True, published.get(key))
        for key in ("uploadSha256", "registrySha256"):
            self.check("Publication " + key + " syntax", isinstance(published.get(key), str)
                       and HEX.fullmatch(published[key]) is not None, published.get(key))
        self.check("Upload hash matches retained candidate nupkg", published.get("uploadSha256") == getattr(self, "candidate_sha", None)
                   and hasattr(self, "candidate_sha"), published.get("uploadSha256"))
        self.check("Registry consumer status", consumer.get("status") == "passed", consumer.get("status"))
        for key, expected in (("rid", RID), ("package", f"{PACKAGE}.{self.args.version}.nupkg")):
            self.check("Registry consumer " + key, consumer.get(key) == expected, consumer.get(key))
        self.check("Registry consumer package hash matches registry receipt", consumer.get("packageSha256") == published.get("registrySha256")
                   and isinstance(consumer.get("packageSha256"), str), consumer.get("packageSha256"))
        self.check("Registry consumer native hash matches candidate", consumer.get("nativeSha256") == getattr(self, "manifest", {}).get("nativeSha256")
                   and isinstance(consumer.get("nativeSha256"), str), consumer.get("nativeSha256"))
        for key in ("ridFreeBuildAndRun", "nativeAotExecuted", "isolatedNugetCache", "outsideSourceTree", "rustInvocationTrap"):
            self.check("Registry consumer " + key + " is true", consumer.get(key) is True, consumer.get(key))
        self.report["scope"]["registryPristineMachine"] = consumer.get("pristineMachine")
        self.check("Registry pristineMachine matches current declared false scope", consumer.get("pristineMachine") is False, consumer.get("pristineMachine"))
        self.report["hashRelationship"] = {
            "uploadSha256": published.get("uploadSha256"), "registrySha256": published.get("registrySha256"),
            "equalityRequired": False, "reason": "NuGet repository signing may change ZIP bytes; the publisher compares unsigned payload entries."}
        for app, expected in (("HelloWorld", "Hello, World! From Rust."), ("InteropTests", INTEROP_PASS)):
            for mode in ("package-run", "aot-run", "aot-publish"):
                filename = app + "-" + mode + ".log"
                member = prefix + "logs/" + filename
                data = read_member(archive, names, member)
                self.retain("publication", member, filename, data)
                content = data.decode("utf-8")
                if mode == "aot-publish":
                    generated = "Generating native code" in content
                    published_path = re.search(r"(?m)^\s*" + app + r" -> .*/publish/\s*$", content) is not None
                    self.check(app + " AOT publish log corroborates native generation", generated and published_path,
                               {"nativeGenerationMarker": generated, "publishedOutputMarker": published_path})
                else:
                    self.check(app + " " + mode + " actual output", content.strip() == expected, content.strip())

    def finish(self):
        passed = not self.report["errors"] and all(item["passed"] for item in self.report["checks"])
        self.report["status"] = "artifact-consistency-passed" if passed else "artifact-consistency-incomplete-or-failed"
        target = self.output / "audit.json"
        target.write_text(json.dumps(self.report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        files = sorted(path for path in self.output.rglob("*") if path.is_file())
        (self.output / "SHA256SUMS").write_text("".join(
            sha(path.read_bytes()) + "  " + path.relative_to(self.output).as_posix() + "\n" for path in files), encoding="utf-8")
        print(json.dumps({"status": self.report["status"], "report": str(target),
                          "reportSha256": sha(target.read_bytes()), "failedChecks": [
                              item["check"] for item in self.report["checks"] if not item["passed"]],
                          "errors": self.report["errors"]}, indent=2))
        return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True, help="Downloaded nativeweave-linux-* ZIP")
    parser.add_argument("--publication", type=Path, required=True, help="Downloaded nativeweave-publication-* ZIP")
    parser.add_argument("--merge", required=True, help="Actual merged main commit SHA, not the PR head")
    parser.add_argument("--version", required=True, help="Version allocated by the release identity job")
    parser.add_argument("--output", type=Path, required=True, help="New evidence directory; never overwritten")
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.merge):
        parser.error("--merge must be a complete lowercase 40-character Git SHA")
    if (not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[0-9a-z-]+(?:\.[0-9a-z-]+)*)?", args.version)
            or ("-" in args.version and any(part.isdigit() and len(part) > 1 and part.startswith("0")
                for part in args.version.split("-", 1)[1].split(".")))):
        parser.error("--version must match eng/release.py's canonical lowercase version syntax")
    audit = Audit(args)
    for source, path, inspect in (("candidate", args.candidate, audit.candidate),
                                  ("publication", args.publication, audit.publication)):
        try:
            audit.open_archive(source, path, inspect)
        except (OSError, ValueError, KeyError, RuntimeError, zipfile.BadZipFile) as error:
            audit.report["errors"].append({"input": source, "error": str(error)})
    return audit.finish()


if __name__ == "__main__":
    sys.exit(main())
