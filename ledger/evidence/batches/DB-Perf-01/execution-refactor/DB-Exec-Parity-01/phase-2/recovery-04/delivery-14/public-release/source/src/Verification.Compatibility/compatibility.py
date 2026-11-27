#!/usr/bin/env python3
"""Read-only, fail-closed maintainer checks for immutable Korda updates.

The input is a reviewed release/component record, not a source of trust by itself.
This tool never downloads, publishes, edits a lockfile, unlists, or unloads code.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile


class Rejected(ValueError):
    """A hard compatibility or provenance failure, with a stable diagnostic code."""


def require(condition, code, message):
    if not condition:
        raise Rejected(f"{code}: {message}")


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "NWCMP001", f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    path = Path(path)
    require(path.stat().st_size <= 16 * 1024 * 1024, "NWCMP001", "Manifest exceeds 16 MiB")
    return json.loads(path.read_text(encoding="utf-8-sig"), object_pairs_hook=pairs)


def canonical_path(value):
    require(isinstance(value, str) and value and "\\" not in value and ":" not in value and
            not value.startswith("/") and all(part not in ("", ".", "..") for part in value.split("/")),
            "NWCMP001", "Expected a canonical relative artifact path")
    return value


def checked_file(root, record):
    path = (Path(root) / canonical_path(record["path"])).resolve()
    require(path.is_relative_to(Path(root).resolve()), "NWCMP001", "Artifact escapes the evidence root")
    require(re.fullmatch(r"[0-9a-f]{64}", record["sha256"]) is not None,
            "NWCMP001", "An exact lower-case SHA-256 is required")
    require(path.is_file() and file_hash(path) == record["sha256"], "NWCMP002",
            f"Missing, stale or substituted artifact: {record['path']}")
    return path


def source_profile(manifest):
    """Read archived v1 Rust records and current v2 language-neutral provenance.

    Version 1 keeps its original opaque cargo_lock and msrv fields. Version 2
    explicitly names a native dependency lock and a structured toolchain. New
    C++ records never label their dependency manifest as a Cargo artifact.
    """
    version = manifest["schema_version"]
    require(version in (1, 2), "NWCMP001", "Unknown component manifest schema")
    if version == 1:
        return "cargo_lock", manifest["upstream"]["msrv"]
    toolchain = manifest["upstream"].get("toolchain")
    require(isinstance(toolchain, dict) and toolchain.get("language") == "c++"
            and type(toolchain.get("standard")) is int and toolchain["standard"] >= 20
            and toolchain.get("compiler") == "Clang" and toolchain.get("version"),
            "NWCMP005", "C++ provenance needs its language standard and exact Clang version")
    require(manifest.get("native_lock_format") == "korda-cpp-dependencies-v1",
            "NWCMP001", "Version 2 requires an explicit native dependency-lock format")
    return "native_lock", toolchain


def validate_component(manifest, root):
    lock_name, _ = source_profile(manifest)
    require(manifest["rid"] in ("linux-x64", "win-x64"), "NWCMP001", "Unknown v1 component target profile")
    require(re.fullmatch(r"[0-9a-f]{40}", manifest["source_commit"]) is not None,
            "NWCMP001", "A full source commit is required")
    require(re.fullmatch(r"[0-9a-f]{40}", manifest["upstream"]["commit"]) is not None,
            "NWCMP005", "Upstream source maps require a full exact commit, not a branch or tag")
    for name in ("managed", "native", "api", "api_assembly", lock_name, "source_inventory", "behavior_receipt"):
        checked_file(root, manifest["artifacts"][name])
    if manifest["schema_version"] == 2:
        lock = read_json(checked_file(root, manifest["artifacts"][lock_name]))
        require(lock.get("schemaVersion") == 1 and isinstance(lock.get("dependencies"), list)
                and isinstance(lock.get("toolchain"), dict),
                "NWCMP002", "Native dependency lock has an unexpected format")
    api = read_json(checked_file(root, manifest["artifacts"]["api"]))
    require(api["assembly"].split(",", 1)[0] == Path(manifest["artifacts"]["api_assembly"]["path"]).stem,
            "NWCMP006", "Compiled API inventory names a different assembly")
    inventory = read_json(checked_file(root, manifest["artifacts"]["source_inventory"]))
    require(inventory["commit"] == manifest["source_commit"] and inventory["files"],
            "NWCMP002", "Source inventory does not bind the exact source commit")
    for entry in inventory["files"]:
        checked_file(root, entry)
    receipt = read_json(checked_file(root, manifest["artifacts"]["behavior_receipt"]))
    require(receipt["passed"] is True and receipt["native_sha256"] == manifest["artifacts"]["native"]["sha256"]
            and receipt["managed_sha256"] == manifest["artifacts"]["managed"]["sha256"],
            "NWCMP003", "Behavior receipt is not bound to the observed managed/native artifacts")
    caps = manifest["abi"]["capabilities"]
    require(len(set(caps.values())) == len(caps) and all(type(x) is int and 0 <= x < 64 for x in caps.values()),
            "NWCMP004", "Capability bits must be unique fixed v1 bits")
    require(set(manifest["abi"]["required"]) <= set(caps), "NWCMP004", "Unknown required capability")
    for field in ("public_seams", "private_seams"):
        for value in manifest["upstream"][field].values():
            source_file = checked_file(root, value)
            if field == "private_seams":
                require(value.get("visibility") and value.get("symbol") and value.get("assumptions")
                        and type(value.get("start_line")) is int and type(value.get("end_line")) is int
                        and 0 < value["start_line"] <= value["end_line"], "NWCMP005",
                        "Private seams need exact source locations, visibility and behavior assumptions")
                with source_file.open(encoding="utf-8") as source:
                    line_count = sum(1 for _ in source)
                require(value["end_line"] <= line_count, "NWCMP005", "Private seam points outside its pinned source file")
    for patch in manifest["upstream"]["patches"]:
        require(patch["upstream_commit"] == manifest["upstream"]["commit"] and patch["owner"]
                and patch["upstream_issue"] and patch["exit_condition"], "NWCMP005",
                "Fork patches need exact upstream, owner, issue, and exit condition")
        require(patch["public_replacement_available"] is False, "NWCMP005",
                "An available public replacement requires retiring/reviewing the private fork")
        checked_file(root, patch["patch"])
        differential = read_json(checked_file(root, patch["differential_receipt"]))
        require(differential["passed"] is True and differential["upstream_commit"] == patch["upstream_commit"]
                and differential["patch_sha256"] == patch["patch"]["sha256"]
                and differential["native_sha256"] == manifest["artifacts"]["native"]["sha256"],
                "NWCMP005", "Fork differential evidence is stale or belongs to another patch/artifact")
    return manifest


def compare_api(previous, candidate):
    """Consume A13 compiled snapshots; exact declarations include null/default/constraints."""
    if "assembly" in previous and "assembly" in candidate:
        require(previous["assembly"] == candidate["assembly"], "NWCMP006",
                "Compiled assembly identity changed; binary identity requires an explicit migration decision")
    def symbols(document):
        result = {}
        for symbol in document["symbols"]:
            require(symbol["id"] not in result, "NWCMP006", "Duplicate API symbol")
            result[symbol["id"]] = symbol["signature"]
        return result
    before, after = symbols(previous), symbols(candidate)
    removed = sorted(set(before) - set(after))
    changed = sorted(key for key in set(before) & set(after) if before[key] != after[key])
    added = sorted(set(after) - set(before))
    require(not removed and not changed, "NWCMP006",
            f"Existing API changed; removed={removed}, signatures/nullability/defaults/constraints={changed}")
    return {"added": added, "retained": len(before), "source_and_binary_proof": "requires executable consumers"}


def validate_regression(root, record, previous, candidate):
    """A successful file hash cannot turn failed or unrelated tests into evidence."""
    receipt = read_json(checked_file(root, record))
    require(receipt.get("passed") is True and receipt.get("source_commit") == candidate["source_commit"],
            "NWCMP007", "Complete regression receipt failed or names unrelated source")
    require(receipt.get("rid") == previous["rid"] == candidate["rid"], "NWCMP007", "Matrix evidence belongs to a different target profile")
    api = receipt.get("api", {})
    require(api.get("previous_assembly_sha256") == previous["artifacts"]["api_assembly"]["sha256"]
            and api.get("candidate_assembly_sha256") == candidate["artifacts"]["api_assembly"]["sha256"]
            and api.get("previous_snapshot_sha256") == previous["artifacts"]["api"]["sha256"]
            and api.get("candidate_snapshot_sha256") == candidate["artifacts"]["api"]["sha256"],
            "NWCMP007", "Complete regression receipt does not bind the compared compiled APIs")
    manifests = {"old": previous, "new": candidate}
    observed = set()
    for row in receipt.get("rows", []):
        require(isinstance(row, dict) and row.get("passed") is True, "NWCMP007", "Complete regression contains a failed matrix row")
        if row.get("scenario") != "pass":
            continue
        generation, native_generation, mode = row.get("generation"), row.get("native"), row.get("mode")
        require(generation in manifests and native_generation in manifests and mode in ("jit", "aot"),
                "NWCMP007", "Unknown complete-regression matrix row")
        identity = mode, generation, native_generation
        require(identity not in observed and row.get("passed") is True, "NWCMP007", "Duplicate or failed matrix row")
        observed.add(identity)
        profile, native, executable = row.get("managed_profile", {}), row.get("native_artifact", {}), row.get("managed_artifact", {})
        require(profile.get("sha256") == manifests[generation]["artifacts"]["managed"]["sha256"]
                and native.get("sha256") == manifests[native_generation]["artifacts"]["native"]["sha256"],
                "NWCMP007", "Matrix row belongs to a different managed/native artifact pair")
        checked_file(root, profile)
        checked_file(root, native)
        checked_file(root, executable)
        require(mode != "aot" or row.get("dynamicCode") is False, "NWCMP007", "AOT matrix row did not execute Native AOT")
        require(mode != "jit" or executable["sha256"] == profile["sha256"], "NWCMP007", "JIT row executed a different managed artifact")
    require({("aot", managed, native) for managed in manifests for native in manifests}.issubset(observed),
            "NWCMP007", "Complete regression needs all old/new Native AOT cross-pairs")


def compare_components(previous_path, candidate_path, root, review_path, now=None):
    """An update review binds both whole manifests and immutable regression evidence."""
    previous = validate_component(read_json(previous_path), root)
    candidate = validate_component(read_json(candidate_path), root)
    review = read_json(review_path)
    require(review["previous_sha256"] == file_hash(previous_path)
            and review["candidate_sha256"] == file_hash(candidate_path)
            and review["reviewer"] and review["decision"] == "compatible",
            "NWCMP007", "Review must name the exact old/new manifest digests and a reviewer")
    validate_regression(root, review["regression_receipt"], previous, candidate)
    require(previous["component"] == candidate["component"] and previous["rid"] == candidate["rid"],
            "NWCMP004", "Component or target identity changed")
    a, b = previous["abi"], candidate["abi"]
    require(a["major"] == b["major"] and b["minor"] >= a["minor"], "NWCMP004", "Incompatible ABI version")
    require(a["layout_sha256"] == b["layout_sha256"], "NWCMP004", "Existing wire layout changed")
    require(all(b["capabilities"].get(name) == bit for name, bit in a["capabilities"].items()),
            "NWCMP004", "Existing capability was removed or reassigned")
    require(set(b["required"]) <= set(a["capabilities"]), "NWCMP004", "New required feature breaks old native")
    require(previous["domain"] == candidate["domain"], "NWCMP003",
            "Domain schema/error/cancellation/behavior version changed; a new compatibility decision is required")
    api = compare_api(read_json(checked_file(root, previous["artifacts"]["api"])),
                      read_json(checked_file(root, candidate["artifacts"]["api"])))
    changed = [key for key in ("commit", "public_seams", "private_seams", "features", "dependencies", "patches")
               if previous["upstream"][key] != candidate["upstream"][key]]
    previous_lock, previous_toolchain = source_profile(previous)
    candidate_lock, candidate_toolchain = source_profile(candidate)
    historical = previous["schema_version"] == candidate["schema_version"] == 1
    if previous["schema_version"] != candidate["schema_version"]:
        changed.append("source_schema")
    if previous_toolchain != candidate_toolchain:
        changed.append("msrv" if historical else "toolchain")
    if previous["artifacts"][previous_lock]["sha256"] != candidate["artifacts"][candidate_lock]["sha256"]:
        changed.append("cargo_lock" if historical else "native_lock")
    require(sorted(review["reviewed_upstream_changes"]) == sorted(changed), "NWCMP007",
            "Review does not enumerate the exact source/seam/feature/MSRV/dependency/license/patch changes")
    available = candidate.get("available_utc")
    require(available is not None, "NWCMP008", "Missing availability time is not covered by the cooldown")
    available = datetime.fromisoformat(available.replace("Z", "+00:00"))
    require(available.tzinfo is not None, "NWCMP008", "Availability must have an explicit timezone")
    now = now or datetime.now(timezone.utc)
    require(now >= available, "NWCMP008", "Availability time is in the future")
    if now - available < timedelta(days=7):
        exception = review.get("security_exception", {})
        require(bool(exception.get("advisory")) and bool(exception.get("rationale"))
                and bool(exception.get("risk_decision")), "NWCMP008",
                "The seven-day cooldown requires an explicit reviewed security exception")
        checked_file(root, exception["lock_diff"])
        validate_regression(root, exception["regression_receipt"], previous, candidate)
    return {"compatible": True, "api": api, "reviewed_upstream_changes": changed,
            "previous_sha256": file_hash(previous_path), "candidate_sha256": file_hash(candidate_path)}


def package_entries(path):
    """Compare every unsigned entry; only a cryptographically checked envelope may differ."""
    result = {}
    with zipfile.ZipFile(path) as archive:
        require(len(archive.infolist()) <= 20000, "NWPKG010", "Too many package entries")
        total = 0
        for entry in archive.infolist():
            name = canonical_path(entry.filename)
            require(name not in result, "NWPKG010", "Duplicate archive entry")
            require((entry.external_attr >> 16) & 0o170000 != 0o120000, "NWPKG010", "Symlink package entry")
            total += entry.file_size
            require(entry.file_size <= 512 * 1024 * 1024 and total <= 2 * 1024 * 1024 * 1024,
                    "NWPKG010", "Package expanded size exceeds the bounded inspection profile")
            with archive.open(entry) as stream:
                result[name] = hashlib.file_digest(stream, "sha256").hexdigest()
    result.pop(".signature.p7s", None)
    return result


def package_payload(path, expected):
    """Payload validation alone is deliberately not publisher authentication."""
    entries = package_entries(path)
    with zipfile.ZipFile(path) as archive:
        nuspecs = [name for name in entries if name.endswith(".nuspec")]
        require(len(nuspecs) == 1, "NWPKG010", "Exactly one nuspec is required")
        require(archive.getinfo(nuspecs[0]).file_size <= 1024 * 1024, "NWPKG010", "Nuspec exceeds the bounded profile")
        raw = archive.read(nuspecs[0])
        require(b"<!DOCTYPE" not in raw.upper() and b"<!ENTITY" not in raw.upper(), "NWPKG010", "Nuspec DTD rejected")
        metadata = ET.fromstring(raw).find("{*}metadata")
        require(metadata is not None, "NWPKG010", "Missing package metadata")
        identity = metadata.findtext("{*}id")
        version = metadata.findtext("{*}version")
        require(identity == expected["id"] and version == expected["version"], "NWPKG011", "Nuspec identity differs from closure")
        edges = {}
        for dep in metadata.findall(".//{*}dependency"):
            package = dep.attrib["id"]
            if not package.lower().startswith("korda."):
                continue
            wanted = dep.attrib["version"]
            require(re.fullmatch(r"\[[^,\[\]()]+\]", wanted) is not None, "NWPKG012", "Owned dependency must use [exact-version]")
            require(package not in edges or edges[package] == wanted[1:-1], "NWPKG012", "Conflicting framework dependency edges")
            edges[package] = wanted[1:-1]
        require(edges == expected["dependencies"], "NWPKG012", "Nuspec owned edges differ from closure")
        require(entries == expected["unsigned_entries"], "NWPKG013", "Package payload differs from the accepted unsigned entries")
        if expected.get("native"):
            native = expected["native"]
            require(entries.get(native["path"]) == native["sha256"], "NWPKG013", "Native payload hash mismatch")
            if native["rid"] == "linux-x64":
                with archive.open(native["path"]) as stream:
                    header = stream.read(64)
                require(len(header) == 64 and header[:7] == b"\x7fELF\x02\x01\x01"
                        and int.from_bytes(header[16:18], "little") == 3 and int.from_bytes(header[18:20], "little") == 62,
                        "NWPKG014", "Native bytes are not the declared Linux x64 shared library")
            require(archive.getinfo("korda/manifest.json").file_size <= 16 * 1024 * 1024,
                    "NWPKG010", "Internal manifest exceeds the bounded profile")
            manifest = json.loads(archive.read("korda/manifest.json"))
            require(manifest["packageId"] == identity and manifest["packageVersion"] == version
                    and manifest["nativePath"] == native["path"] and manifest["nativeSha256"] == native["sha256"]
                    and manifest["rid"] == native["rid"] and manifest["abiMajor"] == native["abi_major"]
                    and manifest["sourceCommit"] == native.get("source_commit", expected["source_commit"]) and manifest["sourceDirty"] is False,
                    "NWPKG014", "Internal native/source manifest is not the accepted payload identity")
            repository = metadata.find("{*}repository")
            require(repository is not None and repository.get("url") == expected["repository"]
                    and repository.get("commit") == expected["source_commit"], "NWPKG014", "Nuspec source provenance differs")
    return {"id": identity, "version": version, "archive_sha256": file_hash(path), "unsigned_entries": entries}


def verify_signature(path, policy, log_directory, dotnet="dotnet"):
    """Verify NuGet crypto/trust first, then the exact reviewed signing identity.

    This version supports the repository-primary route actually used by the
    accepted bootstrap packages. It fails closed for author/countersign routes;
    they need a separately reviewed policy and executable fixtures before use.
    """
    require(policy["route"] == "repository-primary" and policy["service_index"].startswith("https://")
            and policy["owners"] and policy["certificate_sha256"], "NWPKG015", "Unsupported or empty signing policy")
    log_directory = Path(log_directory)
    log_directory.mkdir(parents=True, exist_ok=True)
    command = [dotnet, "nuget", "verify", str(Path(path).resolve()), "--all", "--certificate-fingerprint",
               policy["certificate_sha256"], "--verbosity", "detailed", "--force-english-output"]
    result = subprocess.run(command, text=True, capture_output=True, timeout=120)
    (log_directory / "verify.stdout").write_text(result.stdout)
    (log_directory / "verify.stderr").write_text(result.stderr)
    require(result.returncode == 0, "NWPKG015", "NuGet cryptographic signature/chain/fingerprint verification failed")
    output = result.stdout
    require(re.findall(r"^Signature type: (.+)$", output, re.M) == ["Repository"], "NWPKG015", "Unexpected primary signature route")
    require(re.findall(r"^Service index: (.+)$", output, re.M) == [policy["service_index"]], "NWPKG015", "Unpermitted repository service index")
    owner_rows = re.findall(r"^Owners: (.+)$", output, re.M)
    require(len(owner_rows) == 1 and sorted(x.strip() for x in owner_rows[0].split(",")) == sorted(policy["owners"]),
            "NWPKG015", "Unpermitted signed repository owner set")
    match = re.search(r"Verifying the repository primary signature with certificate:\s*\n"
                      r"  Subject Name: (?P<subject>[^\n]+)\n  SHA1 hash: [^\n]+\n  SHA256 hash: (?P<hash>[0-9A-F]+)", output)
    require(match is not None and match["hash"].lower() == policy["certificate_sha256"].lower()
            and match["subject"] == policy["subject"], "NWPKG015", "Unpermitted primary signing certificate")
    return {"verified": True, "route": policy["route"], "service_index": policy["service_index"],
            "owners": policy["owners"], "certificate_sha256": match["hash"].lower(), "archive_sha256": file_hash(path)}


def validate_closure(record, packages, assets=None):
    """Check immutable graph and actual resolved owned packages, separate from signing."""
    require(record["schema_version"] == 1 and record["packages"], "NWPKG011", "Empty or unknown closure")
    expected = {item["id"].lower(): item for item in record["packages"]}
    require(len(expected) == len(record["packages"]), "NWPKG011", "Duplicate closure package")
    require({key.lower() for key in packages} == set(expected), "NWPKG011", "Incomplete or undeclared package set")
    observed = {}
    for identity, path in packages.items():
        item = expected[identity.lower()]
        for target, version in item["dependencies"].items():
            require(target.lower() in expected and expected[target.lower()]["version"] == version,
                    "NWPKG012", "Dependency edge points outside the exact closure")
        observed[identity] = package_payload(path, item)
    # A cycle is not a release-validation ordering.
    visited, active = set(), set()
    def visit(identity):
        require(identity not in active, "NWPKG012", "Owned dependency cycle")
        if identity in visited:
            return
        active.add(identity)
        for dependency in expected[identity]["dependencies"]:
            visit(dependency.lower())
        active.remove(identity)
        visited.add(identity)
    for identity in expected:
        visit(identity)
    if assets is not None:
        actual = {}
        for name, value in assets["libraries"].items():
            identity, version = name.rsplit("/", 1)
            if value["type"] == "package" and identity.lower().startswith("korda."):
                actual[identity.lower()] = version
        require(actual == {key: value["version"] for key, value in expected.items()}, "NWPKG016",
                "Resolved Korda graph differs even if NuGet warnings were suppressed")
    return {"complete": True, "packages": observed}


def verify_release(record, packages, policy, logs, assets=None):
    result = validate_closure(record, packages, assets)
    for identity, path in packages.items():
        result["packages"][identity]["signature"] = verify_signature(path, policy, Path(logs) / identity)
        expected = next(x for x in record["packages"] if x["id"].lower() == identity.lower())
        require(expected["registry_archive_sha256"] == file_hash(path), "NWPKG013", "Registry archive changed since the signed release record")
    return result


def verify_existing(upload, downloaded, expected, policy, logs):
    """A 409/skip-duplicate outcome is accepted only after immutable read-back checks."""
    before = package_payload(upload, expected)
    after = package_payload(downloaded, expected)
    signature = verify_signature(downloaded, policy, logs)
    require(before["unsigned_entries"] == after["unsigned_entries"], "NWPKG013", "Same-version payload conflict; select a new version")
    return {"resume_allowed": True, "upload_sha256": file_hash(upload), "registry_sha256": file_hash(downloaded),
            "signature": signature, "unsigned_entries_equal": True}


def rollback(record, packages, policy, logs, active_processes):
    require(active_processes == 0, "NWPKG017", "Rollback requires a fresh deployment; no native hot-swap or unload")
    result = verify_release(record, packages, policy, logs)
    result["deployment"] = "new-process-only"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    compare = commands.add_parser("compare")
    for name in ("previous", "candidate", "root", "review"):
        compare.add_argument(name, type=Path)
    closure = commands.add_parser("closure")
    for name in ("record", "package_map", "policy", "logs"):
        closure.add_argument(name, type=Path)
    closure.add_argument("--assets", type=Path)
    api = commands.add_parser("api")
    api.add_argument("previous", type=Path)
    api.add_argument("candidate", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "compare":
            result = compare_components(args.previous, args.candidate, args.root, args.review)
        elif args.command == "api":
            result = compare_api(read_json(args.previous), read_json(args.candidate))
        else:
            result = verify_release(read_json(args.record), read_json(args.package_map), read_json(args.policy),
                                    args.logs, read_json(args.assets) if args.assets else None)
        print(json.dumps(result, indent=2, sort_keys=True))
    except (Rejected, KeyError, TypeError, ValueError, OSError, ET.ParseError, zipfile.BadZipFile, subprocess.TimeoutExpired) as error:
        parser.exit(1, f"Compatibility rejected: {error}\n")


if __name__ == "__main__":
    main()
