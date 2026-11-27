#!/usr/bin/env python3
"""Immutable staged-closure coordination, separate from a public registry uploader.

This component owns ordering, readback, resume and catalog promotion. A reviewed
registry adapter must supply real upload/readback/signature verification; the
local directory adapter never claims public publication or signer authentication.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("korda_compatibility", ROOT / "src/Verification.Compatibility/compatibility.py")
compat = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compat)


def atomic_json(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=path.name + ".", delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(record, stream, sort_keys=True, indent=2)
        stream.write("\n")
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def order(record):
    """Return exact dependency leaves before their facades, rejecting cycles."""
    packages = {p["id"].lower(): p for p in record["packages"]}
    compat.require(packages and len(packages) == len(record["packages"]), "NWPKG001", "Empty or duplicate package closure")
    visited, active, result = set(), set(), []
    def visit(identity):
        compat.require(identity not in active, "NWPKG001", "Package closure cycle")
        if identity in visited:
            return
        active.add(identity)
        item = packages[identity]
        for target, version in sorted(item["dependencies"].items()):
            compat.require(target.lower() in packages and packages[target.lower()]["version"] == version,
                           "NWPKG001", "Owned edge points outside its exact package closure")
            visit(target.lower())
        active.remove(identity)
        visited.add(identity)
        result.append(item)
    for identity in sorted(packages):
        visit(identity)
    return result


def publish(record, staging, destination, journal_path, catalog_path, verify_readback, consume, fault=None):
    """Coordinate a local immutable feed; verify callbacks are mandatory and fail closed.

    No catalog is exposed until every destination package is verified and the
    complete destination closure is actually consumed. Interrupted leaves remain
    immutable. A resumed existing version always takes the same readback gate.
    """
    staging, destination = Path(staging), Path(destination)
    source_packages = {item["id"]: staging / f"{item['id']}.{item['version']}.nupkg" for item in record["packages"]}
    compat.validate_closure(record, source_packages)
    expected_builder = "korda-local-reviewed-staging"
    compat.require(record.get("builder_identity") == expected_builder, "NWPKG015", "Unknown staging builder identity")
    compat.require(record.get("rid") == "linux-x64", "NWPKG003", "This staged release row is Linux x64 only")
    for item in record["packages"]:
        compat.require(compat.file_hash(source_packages[item["id"]]) == item["upload_archive_sha256"],
                       "NWPKG004", "Staged provenance subject digest differs from accepted artifact")
    destination.mkdir(parents=True, exist_ok=True)
    journal = {"schema_version": 1, "status": "partial-unadvertised", "public_publication": False,
               "source_commit": record["source_commit"], "packages": []}
    atomic_json(journal_path, journal)
    downloaded = {}
    for item in order(record):
        original = source_packages[item["id"]]
        target = destination / original.name
        existed = target.exists()
        if not existed:
            # Exclusive creation is the local counterpart of an immutable-registry
            # conflict. It does not overwrite a version raced by another writer.
            try:
                with target.open("xb") as sink, original.open("rb") as source:
                    shutil.copyfileobj(source, sink)
            except FileExistsError:
                existed = True
            except Exception:
                target.unlink(missing_ok=True)
                raise
        row = {"id": item["id"], "version": item["version"], "upload_sha256": compat.file_hash(original),
               "outcome": "existing-needs-verification" if existed else "uploaded-needs-verification"}
        journal["packages"].append(row)
        atomic_json(journal_path, journal)
        if fault:
            fault("uploaded", item)
        verification = verify_readback(original, target, item)
        compat.require(verification.get("verified") is True, "NWPKG015", "Readback verification did not accept the package")
        compat.package_payload(target, item)
        row.update(outcome="readback-verified", downloaded_sha256=compat.file_hash(target), verification=verification)
        downloaded[item["id"]] = target
        atomic_json(journal_path, journal)
    compat.validate_closure(record, downloaded)
    consumed = consume(record, downloaded)
    compat.require(consumed.get("passed") is True and consumed.get("rid") == record["rid"]
                   and consumed.get("source_commit") == record["source_commit"]
                   and consumed.get("packages") == {name: compat.file_hash(path) for name, path in downloaded.items()},
                   "NWPKG001", "Complete destination consumption is missing or bound to different packages")
    journal.update(status="complete-local-closure", consumption=consumed)
    atomic_json(journal_path, journal)
    # Local atomic catalog promotion is deliberately after nontransactional uploads.
    atomic_json(catalog_path, {"schema_version": 1, "source_commit": record["source_commit"],
                             "packages": journal["packages"], "journal_sha256": compat.file_hash(journal_path),
                             "scope": "local staging only; no public registry or signer claim"})
    return journal


def verify_local(upload, readback, expected):
    """Exact unsigned local staging bytes; explicitly not publisher authentication."""
    compat.require(compat.file_hash(upload) == compat.file_hash(readback) == expected["upload_archive_sha256"],
                   "NWPKG004", "Conflicting local package ID/version requires a new version")
    compat.package_payload(readback, expected)
    return {"verified": True, "mode": "reviewed-local-exact-bytes", "signer_authenticated": False}


def verify_registry(upload, readback, expected, policy, logs):
    """Use A22's actual NuGet cryptographic identity and unsigned-payload verifier."""
    result = compat.verify_existing(upload, readback, expected, policy, logs)
    return {"verified": result["resume_allowed"], "mode": "repository-signature-and-accepted-payload", **result}


def rollback(record, package_map, prior_consumption, active_processes):
    """Select a complete, already-consumed prior local closure for a new process."""
    compat.require(active_processes == 0, "NWPKG017", "Rollback requires a new deployment; no native hot replacement")
    compat.validate_closure(record, package_map)
    compat.require(prior_consumption.get("passed") is True
                   and prior_consumption.get("rid") == record["rid"]
                   and prior_consumption.get("source_commit") == record["source_commit"]
                   and prior_consumption.get("packages") == {name: compat.file_hash(path) for name, path in package_map.items()},
                   "NWPKG001", "The whole rollback package set, RID and source must match actual consumption evidence")
    return {"complete": True, "deployment": "new-process-only", "packages": prior_consumption["packages"]}
