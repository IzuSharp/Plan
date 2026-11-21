#!/usr/bin/env python3
"""Read-only DB-Scope-01 package/mixed-database receipt review; executes no tests.

The reviewed expected-contract.json is source evidence, never execution evidence.
Every required output must exist, have its real terminal state, and bind the exact
supplied Git commit/tree. This tool writes only its explicit review output.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile


class Invalid(Exception):
    pass


class Missing(Invalid):
    pass


def need(value, message):
    if not value:
        raise Invalid(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def hash_value(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None and value != "0" * 64


def pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, "Duplicate JSON object member")
        result[key] = value
    return result


def decode(data):
    return json.loads(data, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(Invalid("Non-finite JSON number")))


def relative(root, name):
    need(isinstance(name, str) and name and "\\" not in name and ":" not in name,
         "Noncanonical evidence path")
    need(not PurePosixPath(name).is_absolute() and all(part not in ("", ".", "..") for part in name.split("/")),
         "Evidence path escapes its declared root")
    path = root / name
    need(path.resolve().is_relative_to(root.resolve()), "Evidence symlink escapes its declared root")
    return path


def exact_rows(rows, key, names, *, ordered=False):
    need(isinstance(rows, list) and all(isinstance(row, dict) and key in row for row in rows),
         "Malformed named receipt rows")
    observed = [row[key] for row in rows]
    need(len(observed) == len(set(observed)), "Duplicate named receipt row")
    need(observed == list(names) if ordered else set(observed) == set(names),
         "Missing or unexpected named receipt row")
    return {row[key]: row for row in rows}


def hash_map(value, *, nonempty=True):
    need(isinstance(value, dict) and (bool(value) or not nonempty), "Missing hash inventory")
    need(all(isinstance(key, str) and hash_value(item) for key, item in value.items()), "Invalid SHA-256 inventory")


def sanitize(value):
    private = {"argv", "command", "config", "configuration", "database", "connectionstring",
               "connection_string", "password", "secret", "cursorkey", "cursor_key"}
    if isinstance(value, dict):
        return {key: sanitize(item) for key, item in value.items() if key.lower() not in private}
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, str):
        return re.sub(r"postgres(?:ql)?://[^\s\"'<>]+", "<database-uri>", value)
    return value


@dataclass
class Document:
    data: object
    digest: str
    raw_digest: str


class Source:
    def __init__(self, repo, commit, tree):
        self.repo, self.commit, self.tree = repo, commit, tree
        self.cache = {}
        need(re.fullmatch(r"[0-9a-f]{40}", commit) and re.fullmatch(r"[0-9a-f]{40}", tree),
             "An exact commit and tree are required")
        actual = self.git("rev-parse", commit + "^{tree}").decode().strip()
        need(actual == tree, "Supplied source commit/tree pair disagrees with Git")
        self.blobs = {}
        for line in self.git("ls-tree", "-r", "-z", commit).split(b"\0"):
            if not line:
                continue
            metadata, name = line.split(b"\t", 1)
            mode, kind, blob = metadata.split()
            if kind == b"blob":
                self.blobs[name.decode()] = blob.decode()

    def git(self, *args):
        process = subprocess.run(["git", "-C", str(self.repo), *args], capture_output=True)
        need(process.returncode == 0, "Requested immutable Git source object is unavailable")
        return process.stdout

    def read(self, name):
        need(name in self.blobs, "Evidence names a source path absent from the supplied commit")
        if name not in self.cache:
            self.cache[name] = self.git("cat-file", "blob", self.blobs[name])
        return self.cache[name]

    def hashes(self, names):
        names = list(names)
        unknown = [name for name in names if name not in self.cache]
        if unknown:
            need(all(name in self.blobs for name in unknown), "Source inventory contains absent commit paths")
            process = subprocess.run(["git", "-C", str(self.repo), "cat-file", "--batch"],
                                     input=("\n".join(self.blobs[name] for name in unknown) + "\n").encode(),
                                     capture_output=True)
            need(process.returncode == 0, "Immutable source batch read failed")
            data, position = process.stdout, 0
            for name in unknown:
                end = data.index(b"\n", position)
                header = data[position:end].split()
                need(len(header) == 3 and header[1] == b"blob", "Invalid source batch response")
                size = int(header[2]); start = end + 1
                self.cache[name] = data[start:start + size]
                position = start + size + 1
            need(position == len(data), "Unexpected source batch tail")
        return {name: digest(self.cache[name]) for name in names}

    def matching(self, prefixes, files=()):
        return sorted(name for name in self.blobs if name in files or any(name.startswith(prefix + "/") for prefix in prefixes))


class Review:
    def __init__(self, args, contract):
        self.args, self.contract = args, contract
        self.root = args.evidence_root.resolve()
        self.source = Source(args.source_repo.resolve(), args.source_commit, args.source_tree)
        self.inputs, self.sections, self.failures = {}, [], []
        self.producer = None
        self.closures, self.releases, self.natives, self.matrices = {}, {}, {}, {}
        self.checks = 0

    def check(self, value, message):
        self.checks += 1
        need(value, message)

    def section(self, name, action):
        before = self.checks
        try:
            action()
            self.sections.append({"name": name, "status": "passed", "predicates": self.checks - before})
        except (Invalid, KeyError, IndexError, TypeError, ValueError, OSError) as error:
            # Never copy arbitrary fixture/CLI values or secret-bearing exceptions.
            reason = str(error) if isinstance(error, Invalid) else "Malformed or unavailable evidence (" + type(error).__name__ + ")"
            status = "missing" if isinstance(error, Missing) else "failed"
            self.sections.append({"name": name, "status": status, "predicates": self.checks - before})
            self.failures.append({"section": name, "status": status, "reason": reason})

    def doc(self, name, *, wrapped=False):
        path = relative(self.root, name)
        if not path.is_file():
            raise Missing("Required receipt is absent: " + name)
        self.check(path.stat().st_size <= 64 * 1024 * 1024, "Receipt exceeds bounded JSON inspection size")
        raw = path.read_bytes(); value = decode(raw); file_digest = digest(raw)
        source_digest = file_digest
        if wrapped:
            self.check(isinstance(value, dict) and value.get("sanitized") is True and set(value) == {"sanitized", "source_artifact_sha256", "data"},
                       "Fixture export is missing its exact sanitizer envelope")
            source_digest = value["source_artifact_sha256"]
            self.check(hash_value(source_digest), "Fixture export lacks a raw-source SHA-256")
            value = value["data"]
            self.check(sanitize(value) == value, "Fixture export retains prohibited private fields")
            if self.args.raw_fixture_root:
                self.check(name.startswith("db-scope/database-"), "Unexpected raw fixture lookup")
                raw_name = name.removeprefix("db-scope/")
                original = relative(self.args.raw_fixture_root.resolve(), raw_name)
                if not original.is_file():
                    raise Missing("Explicit raw fixture root lacks a required original")
                original_bytes = original.read_bytes()
                self.check(digest(original_bytes) == source_digest and sanitize(decode(original_bytes)) == value,
                           "Sanitized fixture differs from its independently rehashed raw receipt")
        self.inputs[name] = {"sha256": file_digest, **({"raw_artifact_sha256": source_digest} if wrapped else {})}
        return Document(value, file_digest, source_digest)

    def index(self, folder, name):
        document = self.doc(folder + "/" + name)
        files = document.data["files"]; hash_map(files)
        base = relative(self.root, folder)
        # Nested consumer indexes are ordinary hashed inputs of the outer release index.
        actual = {path.relative_to(base).as_posix() for path in base.rglob("*") if path.is_file() and path != base / name}
        self.check(set(files) == actual, "Evidence index omits or adds files")
        for relative_name, expected in files.items():
            self.check(sha(relative(base, relative_name)) == expected, "Evidence index file hash differs")

    def applicable(self):
        expected = self.contract["reviewed_source_sha256"]
        self.check(self.source.hashes(expected) == expected, "Receipt predicates require review against changed producer/consumer source")
        self.check(self.contract.get("runtime_execution_claim") is False, "Expected contract is not runtime evidence")

    def verify_source_inventory(self, observed, expected_names):
        hash_map(observed)
        self.check(set(observed) == set(expected_names), "Source inventory is incomplete or contains unexpected paths")
        self.check(self.source.hashes(expected_names) == observed, "Receipt source hashes differ from the supplied immutable commit")

    def producer_check(self):
        base = "db-scope/prepared/evidence"
        self.index(base, "evidence-index.json")
        doc = self.doc(base + "/manifest.json"); manifest = doc.data
        self.check(manifest.get("task") == "DB-Scope-01" and manifest.get("rid") == "linux-x64" and manifest.get("scope") == "local-only", "Wrong producer task/platform/scope")
        self.check(manifest.get("sourceCommit") == self.args.source_commit == manifest.get("nativeSourceCommit") and manifest.get("sourceDirty") is False, "Wrong producer source identity or dirty state")
        self.check(manifest.get("publicDomainReleaseAccepted") is False and manifest.get("newDomainSignerAuthenticated") is False and manifest.get("historicalMeasurementTransfer") is False, "Producer exceeds its actual candidate/publication scope")
        ordinary = self.doc("db-scope/prepared/manifest.json")
        self.check(ordinary.digest == doc.digest, "Prepared and exported candidate manifests differ")
        source_inventory = self.doc(base + "/source-inventory.json").data
        self.check(source_inventory.get("sourceCommit") == self.args.source_commit, "Producer inventory source mismatch")
        expected_names = self.source.matching(["src"], ["Directory.Build.props", "Directory.Build.targets", "Cargo.toml", "Cargo.lock", "global.json", "rust-toolchain.toml"])
        self.verify_source_inventory(source_inventory["files"], expected_names)
        native_doc = self.doc("db-scope/native-build/manifest.json"); native = native_doc.data
        self.check(native.get("sourceCommit") == self.args.source_commit and native.get("sourceDirty") is False and native.get("rid") == "linux-x64" and native.get("target") == "x86_64-unknown-linux-gnu", "Native build source/platform mismatch")
        self.check(native_doc.digest == manifest.get("nativeInputManifestSha256"), "Producer native input manifest hash differs")
        self.verify_source_inventory(native["inputSha256"], self.source.matching(["native", ".cargo"], ["Cargo.toml", "Cargo.lock", "rust-toolchain.toml"]))
        self.check(native.get("cargoLockSha256") == self.source.hashes(["Cargo.lock"])["Cargo.lock"], "Native Cargo lock identity differs")
        stripped = {key: value for key, value in native.items() if key not in ("cargoHome", "CargoHome", "rustSysroot", "assets", "builds")}
        self.check(self.doc(base + "/native-build-input.json").data == stripped, "Exported native build input differs from its original manifest")
        assets = exact_rows(native["assets"], "engineId", self.contract["engines"])
        builds = exact_rows(native["builds"], "label", ["sqlite", "postgresql"])
        for engine, definition in self.contract["engines"].items():
            asset, label = assets[engine], engine.removeprefix("database.")
            self.check(Path(asset["path"]).name == definition["asset"] and hash_value(asset["sha256"]) and asset["buildLabel"] == label, "Native asset identity/profile mismatch")
            build = builds[label]
            expected_feature = "nativeweave-database-host/" + ("postgres" if label == "postgresql" else "sqlite")
            self.check(build.get("defaultFeatures") is False and build.get("features") == [expected_feature], "Native profile merged or changed its provider features")
            inventory = self.doc(base + "/native/" + engine + ".json").data
            self.check(inventory.get("sourceCommit") == self.args.source_commit and inventory.get("sourceDirty") is False and inventory.get("nativeSha256") == asset["sha256"] and inventory.get("engineId") == engine, "Native inventory source/hash mismatch")
            self.check(inventory["inputSha256"] == native["inputSha256"] and inventory["metadataSha256"] == build["metadataSha256"] and inventory["buildMessagesSha256"] == build["buildMessagesSha256"], "Native inventory compiler-input binding differs")
            self.check(inventory["elf"]["sha256"] == asset["sha256"] and "nw_database_" + label + "_get_abi_v1" in inventory["elf"]["exports"], "Native inventory lacks actual provider ABI export/hash")
            self.check(bool(inventory["cargoPackages"]), "Empty selected native dependency inventory")
            for package in inventory["cargoPackages"]:
                self.check(not package["name"].startswith(("nativeweave-server", "nativeweave-protocol", "nativeweave-hello", "nativeweave-sync-proof", "nativeweave-async-proof", "nativeweave-extension-proof")), "Retired native product entered selected inputs")
                if package.get("source") is None:
                    self.check(package.get("sourceCommit") == self.args.source_commit, "Owned native input has wrong source commit")
                else:
                    self.check(hash_value(package.get("cargoLockChecksum")) and package["archiveSha256"] == package["cargoLockChecksum"], "External native input lost locked archive identity")
            self.natives[definition["asset"]] = asset["sha256"]
        for label in ("previous", "candidate"):
            items = exact_rows(manifest[label]["packages"], "id", self.contract["packages"])
            release = self.doc(base + "/" + label + "/release.json").data
            self.check(release.get("source_commit") == self.args.source_commit and release.get("source_dirty") is False and release.get("local_unsigned_only") is True and release.get("rid") == "linux-x64", "Release closure source/scope mismatch")
            released = exact_rows(release["packages"], "id", items)
            closure = self.doc(base + "/" + label + "/closure.json").data
            graph = exact_rows(closure["packages"], "id", items)
            for identity, item in items.items():
                expected_deps = {name: items[name]["version"] for name in self.contract["packages"][identity]}
                self.check(item.get("sourceCommit") == self.args.source_commit and item.get("externalDependencies") == {} and item.get("dependencies") == expected_deps and hash_value(item.get("sha256")), "Package identity/dependency edge differs from the exact database graph")
                record = released[identity]
                self.check(record.get("source_commit") == self.args.source_commit and record.get("upload_archive_sha256") == item["sha256"] and all(record[key] == item[key] for key in ("id", "version", "dependencies")), "Package handoff and release archive identities disagree")
                self.check(graph[identity]["version"] == item["version"] and graph[identity]["dependencies"] == expected_deps, "Build closure and package handoff differ")
                entries = record["unsigned_entries"]; hash_map(entries)
                if identity.endswith(".Native"):
                    definition = next(value for value in self.contract["engines"].values() if identity == value["facade"] + ".Native")
                    asset_name = definition["asset"]; expected_path = "runtimes/linux-x64/native/" + asset_name
                    self.check(item["native"]["sha256"] == self.natives[asset_name] and item["native"]["path"] == expected_path and item["native"]["rid"] == "linux-x64", "Native leaf differs from the built provider")
                    self.check(record["native"]["sha256"] == self.natives[asset_name] and entries[expected_path] == self.natives[asset_name], "Native package-entry hash differs from producer bytes")
                if self.args.package_root:
                    self.rehash_package(relative(self.args.package_root.resolve(), item["path"]), item, record)
                elif self.args.candidate_feed and label == "candidate":
                    self.rehash_package(relative(self.args.candidate_feed.resolve(), identity + "." + item["version"] + ".nupkg"), item, record)
            self.closures[label], self.releases[label] = items, released
        for identity, previous in self.closures["previous"].items():
            candidate = self.closures["candidate"][identity]
            self.check(previous["version"] == manifest["previous"]["version"], "Previous closure version split is invalid")
            expected_version = previous["version"] if identity in self.contract["common_packages"] else manifest["candidate"]["version"]
            self.check(candidate["version"] == expected_version, "Candidate common/changed version split is invalid")
            if identity in self.contract["common_packages"]:
                self.check(candidate["sha256"] == previous["sha256"], "Unchanged common package bytes were replaced")
        self.producer = doc

    def rehash_package(self, path, item, record):
        if not path.is_file():
            raise Missing("Explicit package root lacks a required package archive")
        self.check(sha(path) == item["sha256"], "Actual package archive hash differs")
        with zipfile.ZipFile(path) as archive:
            infos = archive.infolist()
            self.check(len(infos) <= 20000 and sum(info.file_size for info in infos) <= 2 * 1024**3, "Package inspection bounds exceeded")
            self.check(len({info.filename for info in infos}) == len(infos), "Duplicate package archive entry")
            entries = {}
            for info in infos:
                relative(Path("/synthetic-package-root"), info.filename)
                self.check(info.file_size <= 512 * 1024**2 and (info.external_attr >> 16) & 0o170000 != 0o120000, "Invalid package entry kind/size")
                with archive.open(info) as stream:
                    entries[info.filename] = hashlib.file_digest(stream, "sha256").hexdigest()
            entries.pop(".signature.p7s", None)
            self.check(entries == record["unsigned_entries"], "Actual package payload differs from frozen release inventory")
            metadata = ET.fromstring(archive.read(item["id"] + ".nuspec")).find("{*}metadata")
            expected = {name: "[" + version + "]" for name, version in item["dependencies"].items()}
            dependencies = metadata.findall(".//{*}dependency")
            self.check(len(dependencies) == len(expected) and {node.attrib["id"]: node.attrib["version"] for node in dependencies} == expected, "Actual nuspec has undeclared/nonexact dependencies")
            self.check(not metadata.findall(".//{*}frameworkReference") and not metadata.findall(".//{*}frameworkAssembly"), "Actual nuspec adds a server framework")

    def top_level(self):
        self.check(self.producer is not None, "Producer evidence must pass before final binding")
        value = self.doc("verification.json").data
        self.check(value.get("task") == "DB-Scope-01" and value.get("status") == "passed" and value.get("rid") == "linux-x64", "Verification terminal state is not passed")
        self.check(value.get("source") == {"commit": self.args.source_commit, "tree": self.args.source_tree}, "Final verification source commit/tree mismatch")
        self.check(value.get("candidateManifestSha256") == self.producer.digest and value.get("nativeManifestSha256") == self.inputs["db-scope/native-build/manifest.json"]["sha256"], "Final verification manifest hash mismatch")
        self.check(value.get("pristineMachine") is False and value.get("independentReview") is False and value.get("publiclyPublished") is False, "Local orchestration overclaims pristine/public/independent acceptance")
        required = {"scope", "rustfmt", "clippy", "rust-workspace-tests", "locked-restore", "managed-workspace-build", "dotnet-format", "compiled-api-and-xml", "postgresql-and-sqlite-regressions", "nuget-closure", "external-fluent-dto-jit-and-aot"}
        self.check(set(value.get("checks", [])) == required, "Final verification omits a required gate")

    def closure_for(self, label, graph):
        roots = {"sqlite": ["NativeWeave.Database.Sqlite"], "postgresql": ["NativeWeave.Database.PostgreSql"], "combined": ["NativeWeave.Database.Sqlite", "NativeWeave.Database.PostgreSql"]}[graph]
        result = set()
        def visit(name):
            if name not in result:
                result.add(name)
                for child in self.contract["packages"][name]:
                    visit(child)
        for root in roots:
            visit(root)
        return {name: self.closures[label][name]["version"] for name in sorted(result)}

    def package_runtime_row(self, value, provider, mode, *, edited=False):
        self.check(value.get("task") == "DB-Scope-01" and value.get("provider") == provider and value.get("dynamicCodeSupported") is (mode == "jit"), "Package runtime row identity/mode mismatch")
        required = set(self.contract["package_check_ids"])
        if mode == "aot":
            required.add("actual-native-aot")
        if edited:
            required.add("ordinary-added-entity-dto-query")
        self.check(required.issubset(value.get("checks", [])) and "only-selected-database-module" in value["checks"], "Package runtime omitted typed data/lifetime/actual-map assertions")
        filename = self.contract["engines"]["database." + provider]["asset"]
        self.check(value.get("nativeLibraries") == [{"file": filename, "sha256": self.natives[filename]}], "Actually mapped native library differs from the exact provider package")

    def elf(self, audit, expected_hash):
        self.check(audit.get("sha256") == expected_hash and audit.get("executable") is True and audit.get("machine") == "x86_64" and audit.get("format") == "ELF64-little-endian", "AOT ELF executable identity/profile mismatch")
        self.check(set(audit.get("needed", [])) <= set(self.contract["aot_system_dependencies"]), "AOT output adds an undeclared native dependency")
        maximum = audit.get("maximum_glibc")
        self.check(maximum is None or tuple(map(int, maximum.split("."))) <= (2, 39), "AOT output exceeds the required glibc ceiling")

    def package_consumer(self, filename, environment, *, closure="candidate", mode="full"):
        self.check(self.producer is not None, "Producer evidence must pass before package consumption")
        document = self.doc(filename); value = document.data
        self.check(value.get("passed") is True and value.get("task") == "DB-Scope-01" and value.get("rid") == "linux-x64" and value.get("architecture") == "x86_64", "Package consumer did not complete on Linux x64")
        self.check(value.get("source_commit") == self.args.source_commit and value.get("manifestSha256") == self.producer.digest and value.get("closure") == closure and value.get("mode") == mode, "Package consumer source/closure binding differs")
        expected_packages = {name: item["sha256"] for name, item in self.closures[closure].items()}
        self.check(value.get("packages") == expected_packages, "Consumer archive hashes differ from the frozen closure")
        self.check(value.get("consumer_environment") == environment and value.get("pristine_machine") is (environment == "pristine"), "Consumer local/pristine scope differs")
        self.check(value.get("outside_source_tree") is True and value.get("rust_invocation_trap_fired") is False and value.get("rust_absence_before_trap") == dict.fromkeys(("cargo", "rustc", "rustup"), True), "Consumer lacks outside-tree/no-Rust execution evidence")
        if environment == "pristine":
            self.check(value.get("image") == self.contract["sdk_image"] and value.get("host_rust_absence_before_isolation") == dict.fromkeys(("cargo", "rustc", "rustup"), True), "Pristine claim lacks pinned SDK image and initial Rust absence")
        else:
            self.check(value.get("image") is None, "Local PATH isolation is incorrectly labeled as a pristine image")
        self.check(value.get("publicDomainReleaseAccepted") is False and value.get("newDomainSignerAuthenticated") is False, "Consumer overclaims public distribution/signing")
        source_inputs = value["sourceInputs"]; hash_map(source_inputs)
        expected_source_paths = {"samples/api/packaging-domain/Program.cs", "samples/api/packaging-domain/AddedModels.cs.template", "src/Packaging.Domain/consume.py", "src/Packaging.Domain/model.py", "src/Packaging.Linux/linux_profile.py", "tests/Packaging.Domain/consumer_cases.py", "tests/Packaging.Domain/negative_cases.py", "tests/Packaging.Domain/registry_cases.py", "tests/Packaging.Domain/runtime_verify.py"}
        self.check(set(source_inputs) == expected_source_paths, "Consumer source-input inventory is incomplete")
        self.check(self.source.hashes(source_inputs) == source_inputs, "Consumer controller/sample source identity differs")
        commands = value.get("commands", [])
        self.check(bool(commands) and all(row.get("processExited") is True and hash_value(row.get("stdoutSha256")) and hash_value(row.get("stderrSha256")) for row in commands), "Consumer command terminal/log-hash evidence is incomplete")
        command_index = exact_rows(commands, "label", [row["label"] for row in commands])
        graphs = value["graphs"]
        self.check(set(graphs) == ({"sqlite", "postgresql", "combined"} if mode == "full" else {"combined"}), "Consumer graph selection is incomplete")
        for graph, row in graphs.items():
            providers = [graph] if graph != "combined" else ["sqlite", "postgresql"]
            self.check(row.get("selectedPackages") == self.closure_for(closure, graph), "Actual restored selection differs from the provider-only graph")
            self.check(len(row["initialJit"]) == len(providers), "JIT graph omitted a provider")
            for receipt, provider in zip(row["initialJit"], providers):
                self.package_runtime_row(receipt, provider, "jit")
            labels = [graph + "-restore", graph + "-build", *[graph + "-jit-" + provider for provider in providers]]
            for field in (["nativeBefore", "nativeAfter"] if mode == "full" else ["nativeBefore"]):
                native = row[field]
                self.check(set(native) == {"database." + provider for provider in providers}, "Published graph has extra/missing native output records")
                for provider in providers:
                    engine = "database." + provider; definition = self.contract["engines"][engine]; item = native[engine]
                    self.check(item["sha256"] == self.natives[definition["asset"]] and Path(item["relativePath"]).name == definition["asset"] and item["facade"] == definition["facade"] and item["facadeVersion"] == self.closures[closure][definition["facade"]]["version"] and item["record"] == "NativeWeave." + engine + ".assets.json" and hash_value(item["recordSha256"]), "Native output record/version/hash differs from the chosen leaf")
            if mode == "full":
                self.check(row.get("offlineAfterRestore") is True and row.get("addedEntityDto") is (graph == "combined") and hash_value(row.get("executableSha256")), "Managed-edit/offline-AOT proof is incomplete")
                self.elf(row["aotElfAudit"], row["executableSha256"])
                self.check(len(row["aot"]) == len(providers), "AOT graph omitted a provider")
                for receipt, provider in zip(row["aot"], providers):
                    self.package_runtime_row(receipt, provider, "aot", edited=graph == "combined")
                if graph == "combined":
                    self.check(len(row["editedJit"]) == 2, "Managed edit omitted a provider")
                    for receipt, provider in zip(row["editedJit"], providers):
                        self.package_runtime_row(receipt, provider, "jit", edited=True)
                    labels.extend([graph + "-offline-managed-edit-build", *[graph + "-edited-jit-" + provider for provider in providers]])
                labels.extend([graph + "-aot-restore", graph + "-offline-aot-publish", *[graph + "-aot-" + provider for provider in providers]])
                hash_map(row["locks"]); hash_map(row["finalSourceSha256"])
            self.check(all(label in command_index and command_index[label].get("exitCode") == 0 for label in labels), "A required actual package build/execute command did not pass")
        payloads = value["packagePayloadAudit"]
        self.check(set(payloads) == set(expected_packages), "Whole-package payload audit is incomplete")
        for name, payload in payloads.items():
            item = self.closures[closure][name]
            expected_native = [item["native"]["path"]] if item.get("native") else []
            expected_assemblies = [] if name.endswith(".Native") or name == "NativeWeave.Query.Generator" else [name + ".dll"]
            self.check(payload == {"dependencies": {key: "[" + version + "]" for key, version in item["dependencies"].items()}, "managedRuntimeAssemblies": expected_assemblies, "nativeAssets": expected_native}, "Payload audit contains a retired/undeclared dependency, assembly or native asset")
        if mode == "full":
            negatives = exact_rows(value["negativeCases"], "name", self.contract["package_negative_ids"])
            self.check(all(row.get("passed") is True for row in negatives.values()), "Package negative gate did not pass")
            self.check(negatives["override-suppressed"].get("noWarnSuppressed") is True and negatives["override-visible"].get("actualNuGetWarnings"), "NuGet override/no-warning guard evidence is absent")
            self.check(negatives["actual-domain-bootstrap-incompatible-abi"].get("domainOwnerCreated") is False and negatives["runtime-native-content-tamper"].get("hashCheckedBeforeDomainOwner") is True, "ABI/hash rejection did not precede database owner creation")
        return document

    def matrix(self, fixture):
        self.check(self.producer is not None, "Producer evidence must pass before fixture binding")
        folder = "database-lifecycle" if fixture == "api" else "database-business"
        doc = self.doc("db-scope/" + folder + "/progress.json", wrapped=True)
        value = doc.data
        self.check(value.get("task") == "DB-Scope-01" and value.get("platform") == "linux-x64" and value.get("fixture") == fixture, "Fixture matrix identity differs")
        self.check(value.get("source", {}).get("commit") == self.args.source_commit and value["source"].get("scope_status") == "", "Fixture source is dirty or from another commit")
        self.check(value.get("required_rows") == self.contract["rows"] and set(value.get("rows", {})) == set(self.contract["rows"]), "Fixture four-row matrix is incomplete")
        self.check(value.get("all_four_rows_passed") is True and value.get("public_api_matrix_complete") is True and value.get("failures") == [] and value.get("consumer_rust_invocations") == [], "Fixture terminal state or Rust trap failed")
        inputs = value["inputs"]; packages = inputs["packages"]
        self.check(set(packages) == set(self.closures["candidate"]) and inputs.get("native_sha256") == self.natives, "Fixture candidate package/native selection differs")
        for identity, item in packages.items():
            expected = self.closures["candidate"][identity]
            dependencies = item["dependencies"]
            self.check(item.get("version") == expected["version"] and item.get("sha256") == expected["sha256"] and item.get("repository", {}).get("commit") == self.args.source_commit, "Fixture package version/hash/source mismatch")
            self.check(len(dependencies) == len(expected["dependencies"]) and {entry["id"]: entry["version"] for entry in dependencies} == {key: "[" + version + "]" for key, version in expected["dependencies"].items()}, "Fixture nuspec has a missing, relaxed or retired dependency")
        prefix = "src/Verification.EndToEnd/ApiProbe" if fixture == "api" else "src/Reference.TaskService"
        expected_source = {name.removeprefix(prefix + "/"): item for name, item in self.source.hashes(self.source.matching([prefix])).items()}
        self.check(inputs.get("source_sha256") == expected_source, "Frozen fixture source differs from the supplied commit")
        expected_helpers = self.source.hashes(["tests/Verification.EndToEnd/api_probe.py", "tests/Reference.TaskService/package_probe.py", "global.json"])
        self.check(inputs.get("controller_sha256") == expected_helpers["tests/Verification.EndToEnd/api_probe.py"] and inputs.get("accepted_identity_helper_sha256") == expected_helpers["tests/Reference.TaskService/package_probe.py"] and inputs.get("global_json_sha256") == expected_helpers["global.json"], "Fixture controller/helper/SDK source binding differs")
        self.check(set(value.get("builds", {})) == {"jit", "aot"}, "Fixture lacks a required build mode")
        assembly = "NativeWeave.Verification.EndToEnd.ApiProbe" if fixture == "api" else "NativeWeave.Reference.TaskService"
        for mode, build in value["builds"].items():
            artifacts, metadata = build["artifacts_sha256"], build["metadata_sha256"]
            hash_map(artifacts); hash_map(metadata)
            lock = "packages.lock.json" if mode == "jit" else "packages.linux-x64.aot.lock.json"
            self.check(set(metadata) == {"project.assets.json", lock, "resolved-archive-hashes.json"}, "Fixture restore metadata hash inventory is incomplete")
            for basename, expected in self.natives.items():
                copies = [item for name, item in artifacts.items() if Path(name).name == basename]
                self.check(bool(copies) and all(item == expected for item in copies), "Fixture published native bytes differ")
            for name in artifacts:
                basename = Path(name).name
                if basename.endswith(".so"):
                    self.check(basename in self.natives, "Fixture output contains an undeclared native library")
                if basename.startswith("NativeWeave.") and basename.endswith(".dll"):
                    self.check(basename[:-4] in self.contract["packages"] or basename == assembly + ".dll", "Fixture output contains a retired managed product")
            executable = assembly + (".dll" if mode == "jit" else "")
            self.check(executable in artifacts, "Fixture executable is absent from the build inventory")
            for provider in ("sqlite", "postgresql"):
                entry = value["rows"][provider + "-" + mode]
                self.check(entry.get("status") == "passed" and entry.get("executable_sha256") == artifacts[executable], "Fixture runtime row is incomplete or uses another executable")
        commands = value.get("commands", [])
        self.check(bool(commands) and all(row.get("exit_code") == 0 and hash_value(row.get("log_sha256")) for row in commands), "Fixture controller command did not complete successfully")
        self.matrices[fixture] = value

    def lifecycle(self, provider, mode):
        self.check("api" in self.matrices, "Lifecycle matrix must pass before row reconciliation")
        row = provider + "-" + mode; base = "db-scope/database-lifecycle/rows/" + row
        entry = self.matrices["api"]["rows"][row]
        receipt = self.doc(base + "/receipt.json", wrapped=True)
        independent = self.doc(base + "/independent-sql.json", wrapped=True)
        value = receipt.data
        self.check(entry.get("receipt_sha256") == receipt.raw_digest and entry.get("independent_sql_sha256") == independent.raw_digest, "Lifecycle raw receipt/independent SQL hash linkage differs")
        self.check(value.get("task") == "DB-Scope-01" and value.get("provider") == provider and value.get("dynamicCodeSupported") is (mode == "jit") and value.get("failures") == [], "Lifecycle row identity/mode/terminal failures differ")
        cases = exact_rows(value["cases"], "id", self.contract["lifecycle_case_ids"][provider])
        self.check(all(case.get("status") == "passed" for case in cases.values()) and entry.get("assertions") == len(cases), "Lifecycle named assertions did not all pass")
        self.check(value.get("nativeDatabaseOwners") == {name: [0] * 6 for name in self.natives}, "Final native ownership counters are nonzero/incomplete")
        self.check(cases["nullable-composite-foreign-key-direct-query"].get("observations", {}).get("actual") == "1|2,4|0", "Nullable/composite relation values differ")
        self.check(cases["actual-failed-transaction-primary"].get("observations", {}).get("kind") == "Constraint", "Failed transaction did not preserve its primary constraint error")
        cancellation = cases["commit-pre-admission-cancellation"].get("observations", {})
        self.check(cancellation.get("commitAttempted") == "False" and cancellation.get("outcome") != "Committed", "Pre-admission cancellation dispatched or confirmed COMMIT")
        expected = {"rows": 5, "canceled_commit_absent": 0, "nullable_children": 2, "complete_fk_children": 1}
        for key, number in expected.items():
            observed = independent.data[key]
            self.check(observed.get("expected") == number and observed.get("observed") == number and bool(observed.get("query")), "Independent lifecycle durable-data oracle differs")
        if provider == "sqlite":
            self.check(independent.data.get("integrity") == [["ok"]] and independent.data.get("foreign_keys") == [], "SQLite integrity/foreign-key oracle differs")

    def business(self, provider, mode):
        self.check("reference" in self.matrices, "Business matrix must pass before row reconciliation")
        row = provider + "-" + mode; base = "db-scope/database-business/rows/" + row
        entry = self.matrices["reference"]["rows"][row]
        result_doc = self.doc(base + "/reference/result.json", wrapped=True)
        runtime_doc = self.doc(base + "/reference/verify/receipt.json", wrapped=True)
        result, runtime = result_doc.data, runtime_doc.data
        self.check(result_doc.raw_digest == entry.get("result_sha256"), "Business result raw hash differs from its matrix controller")
        self.check(result.get("task") == "DB-Scope-01" and result.get("passed") is True and result.get("provider") == provider and result.get("mode") == mode and not result.get("failure"), "Business row did not complete for the selected provider/mode")
        self.check(runtime.get("case") == "--verify" and runtime.get("dynamicCodeSupported") is (mode == "jit") and runtime.get("databaseResourcesReleased") is True and runtime.get("consumerResourcesReleased") is True, "Business runtime/resource-retirement witness is incomplete")
        checks = result["checks"]
        self.check(checks == runtime.get("checks") == entry.get("checks") and set(checks) == set(self.contract["business_check_ids"]) and all(value == "passed" for value in checks.values()), "Business assertion set differs across actual runtime and controllers")
        maintenance = result["maintenance_checks"]
        self.check(set(maintenance) == set(self.contract["maintenance_check_ids"]) and all(value == "passed" for value in maintenance.values()), "A unique business maintenance/recovery oracle is missing or failed")
        data = result["independent_sql"]
        for name, number in {"items": 3, "operations": 4, "outbox": 4, "attachments": 1, "stale_rollback": 0, "delivered_outbox": 4, "item_versions": 4}.items():
            self.check(data[name] == {"expected": number, "observed": number}, "Independent business durable-data counts differ")
        self.check(data.get("outbox_consumer") == [4, 4, 4], "Independent consumer effect/delivery counts differ")
        replies = runtime["replies"]
        self.check(len(replies) == 5 and replies[0]["status"] == 201 == replies[1]["status"] and replies[0]["bytesHex"] == replies[1]["bytesHex"], "Returned durable idempotency bytes/status differ")
        first = bytes.fromhex(replies[0]["bytesHex"])
        self.check(digest(first) == data.get("replay_sha256") and decode(first).get("operationId") == replies[0]["operationId"], "Returned replay does not bind independently stored response bytes")
        keyset = result["keyset_checks"]
        expected_order, observed_order = keyset["expected_item_order"], keyset["observed_item_order"]
        self.check(keyset.get("passed") is True and keyset.get("tie_created_at") == 1790000000000 and len(expected_order) >= 8 and expected_order == observed_order and len(set(observed_order)) == len(observed_order), "Complete keyset traversal lost, duplicated or reordered tied rows")
        keychecks = keyset["checks"]
        self.check(all(keychecks.get(name) == "passed" for name in self.contract["keyset_check_ids"]), "Keyset termination/authority checks are incomplete")
        self.check(keychecks.get("keyset-observed-item-order") == ",".join(observed_order), "Keyset returned sequence differs from independent SQL")
        bounds = {int(name.removeprefix("keyset-page-bound-")) for name in keychecks if name.startswith("keyset-page-bound-")}
        ties = {int(name.removeprefix("keyset-real-tie-")) for name in keychecks if name.startswith("keyset-real-tie-")}
        self.check(bounds == ties == set(range(len(bounds))) and len(bounds) >= 4 and all(value == "passed" for name, value in keychecks.items() if name != "keyset-observed-item-order"), "Keyset per-page real-tie/bound evidence is incomplete")
        if provider == "postgresql":
            oracle = self.doc(base + "/reference/postgres-oracles/result.json", wrapped=True).data
            self.check(oracle == result["postgres_oracles"], "Standalone and embedded PostgreSQL oracle results differ")
            self.postgres_oracles(oracle)
        faults = self.doc(base + "/faults/receipt.json", wrapped=True)
        self.check(faults.raw_digest == entry.get("fault_receipt_sha256"), "Fault receipt raw hash differs from its matrix controller")
        self.faults(faults.data, provider, mode, entry)

    def durable(self, value):
        self.check(all(value.get(name) == 1 for name in ("operation_count", "item_count", "outbox_count")), "PostgreSQL independent singleton effects differ")
        self.check(hash_value(value.get("request_hash")) and hash_value(value.get("response_sha256")), "PostgreSQL durable replay lacks hashes")
        raw = bytes.fromhex(value["response_hex"]); data = decode(raw)
        self.check(digest(raw) == value["response_sha256"] and data.get("operationId") == value.get("operation_id") and data.get("itemId") == value.get("item_id"), "PostgreSQL durable bytes/identity reconciliation differs")

    def postgres_oracles(self, value):
        self.check(value.get("task") == "DB-Scope-01" and value.get("platform") == "linux-x64" and value.get("passed") is True and value.get("active_case") is None and set(value["cases"]) == {"conflict_snapshot", "commit_ack_loss"}, "PostgreSQL independent oracle pair did not finish")
        conflict = value["cases"]["conflict_snapshot"]
        self.check(conflict.get("passed") is True and conflict.get("separate_select") is True and type(conflict.get("winner_pid")) is int and type(conflict.get("loser_pid")) is int and conflict["winner_pid"] > 0 and conflict["loser_pid"] > 0 and conflict["winner_pid"] != conflict["loser_pid"], "PostgreSQL conflict lacks distinct actual sessions and a new SELECT")
        witness = conflict["lock_wait"]
        self.check(len(witness) == 3 and int(witness[0]) == conflict["loser_pid"] and witness[1] == "Lock" and bool(witness[2]), "PostgreSQL conflict lacks the actual blocking-lock witness")
        count = conflict["sqlx_metadata_query_count_before_select"]
        self.check(type(count) is int and count in (0, 1) and len(conflict["sqlx_metadata_before_select"]) == count, "Conflict snapshot admits an unreviewed query between INSERT and SELECT")
        self.durable(conflict["durable"])
        unknown = value["cases"]["commit_ack_loss"]
        self.check(unknown.get("passed") is True and unknown.get("unknown_status") == 503 and unknown.get("unknown_code") == "outcome_unknown" and unknown.get("commit_then_idle_discarded") is True and unknown.get("authorized_recovery") is True and unknown.get("protected_same_key_replay") is True, "PostgreSQL lost-COMMIT response was not preserved as protected Unknown")
        self.check(unknown.get("operation_id") == unknown["durable"]["operation_id"] and type(unknown.get("backend_pid")) is int and unknown["backend_pid"] > 0, "Unknown recovery lost its actual backend/operation identity")
        self.durable(unknown["durable"])

    def faults(self, value, provider, mode, entry):
        expected = self.contract["fault_case_ids"][provider]
        identity = value["identity"]
        self.check(value.get("status") == "passed" and value.get("completedOuterLifecycle") is True and value.get("outerFailure") is None and value.get("selectedCasesComplete") is True and value.get("notSelected") == [] and value.get("selectedNotExecuted") == [], "Finite fault controller did not complete its entire lifecycle")
        self.check(identity.get("mode") == mode and identity.get("provider") == provider and identity.get("executableSha256") == entry["executable_sha256"] and identity.get("performanceMeasurement") is False, "Fault consumer source row/mode/scope differs")
        self.check(identity.get("requiredFaultCasesForProvider") == expected == identity.get("selectedFaultCases") and entry.get("fault_cases") == len(expected), "A required finite fault case was not selected")
        self.check(identity["artifacts"] == self.matrices["reference"]["builds"][mode]["artifacts_sha256"], "Fault execution mutated or substituted frozen consumer artifacts")
        for field, prefix in (("controller", "tests/Verification.EndToEnd"), ("referenceController", "tests/Reference.TaskService")):
            recorded = identity[field]; hash_map(recorded)
            self.check(self.source.hashes(prefix + "/" + name for name in recorded) == {prefix + "/" + name: expected for name, expected in recorded.items()}, "Fault controller source hashes differ")
        shim_source = "src/Verification.EndToEnd/FilesystemFaults/fs_fault.c"
        self.check(value.get("filesystemShim", {}).get("sourceSha256") == self.source.hashes([shim_source])[shim_source] and hash_value(value["filesystemShim"].get("sha256")), "Filesystem fault mechanism lacks source-bound actual shim identity")
        cases = exact_rows(value["cases"], "id", expected, ordered=True)
        for name, case in cases.items():
            assertions = case["assertions"]
            self.check(case.get("status") == "passed" and [item.get("id") for item in assertions] == self.contract["fault_assertion_ids"][name] and all(item.get("status") == "passed" for item in assertions), "Fault case lost a specific ordered durable/boundary assertion")
            for assertion in assertions:
                kind, observation = assertion["id"], assertion["observations"]
                if kind == "operation-cardinality":
                    self.check(type(observation.get("expected")) is int and observation["expected"] in (0, 1) and observation.get("observed") == observation["expected"], "Fault atomic cardinality observation differs")
                elif kind == "atomic-item-result-outbox":
                    self.check(observation == {"items": 1, "outbox": 1}, "Fault atomic effect counts differ")
                elif kind == "stored-response-bytes":
                    self.check(type(observation.get("bytes")) is int and observation["bytes"] > 0 and hash_value(observation.get("sha256")), "Fault replay assertion lacks actual stored-byte evidence")
                elif kind == "no-incomplete-reference":
                    self.check(observation == {"references": 0, "itemVersion": 1}, "Interrupted attachment left an incomplete reference")
                elif kind == "proxy-has-no-controller-failure":
                    self.check(observation == {"count": 0}, "Fault protocol controller itself failed")
                elif kind == "discarded-connection-is-not-reused":
                    pids = observation["claimBackends"]
                    self.check(len(pids) == 2 and pids[0] == observation["failedBackendPid"] and pids[1] not in (None, pids[0]), "Failed PostgreSQL physical connection was reused")
                elif kind == "actual-native-wal-write-was-faulted":
                    self.check(len(observation["injection"]) == 1 and observation["injection"][0].get("event") == "injected-libc-enospc", "SQLite storage fault lacks actual native WAL injection")
                elif kind == "at-least-once-one-effect":
                    observed = observation["receipts"]
                    self.check(len(observed) == 1 and len(observed[0]) == 3 and observed[0][1:] == [2, 1], "Outbox redelivery did not preserve exactly one effect")
                elif kind == "staged-content-incomplete":
                    sizes = observation["sizes"]
                    self.check(len(sizes) == 1 and 0 < sizes[0] < observation["expectedLength"], "Upload interruption lacks a real partial first write")
                elif kind == "crash-inside-actual-collection":
                    self.check(type(observation.get("remaining")) is int and 0 < observation["remaining"] < 8, "Collector crash lacks partial real deletion")

    def release(self):
        base = "db-scope/release/evidence"
        self.index(base, "evidence-index.json")
        value = self.doc(base + "/result.json").data
        self.check(self.producer is not None and value.get("sourceCommit") == self.args.source_commit and value.get("manifestSha256") == self.producer.digest and value.get("rid") == "linux-x64", "Release result producer/source binding differs")
        self.check(value.get("passed") is True and value.get("status") == "completed" and value.get("consumer_environment") == "pristine" and value.get("pristine_machine") is True, "Release/recovery CI did not complete in the pristine SDK environment")
        self.check(value.get("publicDomainReleaseAccepted") is False and value.get("newDomainSignerAuthenticated") is False, "Release evidence overclaims registry/signature authorization")
        cases = exact_rows(value["cases"], "name", self.contract["release_case_ids"])
        self.check(all(row.get("passed") is True for row in cases.values()), "A required release/recovery case failed")
        copies = {}
        for name, closure, mode in (("previous-destination", "previous", "smoke"), ("candidate-destination", "candidate", "full"), ("rollback-destination", "previous", "smoke")):
            copies[name] = self.package_consumer(base + "/" + name + ".receipt.json", "pristine", closure=closure, mode=mode)
            self.index(base + "/" + name, "index.json")
            self.check(self.doc(base + "/" + name + "/receipt.json").digest == copies[name].digest, "Release callback and safe consumer receipt copies differ")
        for case, name in (("resume-and-actual-previous-consumption", "previous-destination"), ("candidate-upgrade-and-actual-full-consumption", "candidate-destination"), ("complete-previous-closure-fresh-process-rollback", "rollback-destination")):
            self.check(cases[case].get("receiptSha256") == copies[name].digest, "Release case does not bind its actual consumer receipt")

    def runtime_only(self):
        transfer = self.doc("db-scope/release/evidence/candidate-destination/runtime-transfer-manifest.json")
        runtime = self.doc("db-scope/runtime/evidence/receipt.json").data
        expected_packages = {name: item["sha256"] for name, item in self.closures["candidate"].items()}
        self.check(transfer.data.get("task") == "DB-Scope-01" and transfer.data.get("source_commit") == self.args.source_commit and transfer.data.get("packages") == expected_packages and transfer.data.get("rid") == "linux-x64", "Runtime transfer source/package identity differs")
        self.check(runtime.get("passed") is True and runtime.get("task") == "DB-Scope-01" and runtime.get("source_commit") == self.args.source_commit and runtime.get("packages") == expected_packages and runtime.get("manifestSha256") == transfer.digest, "Runtime-only result does not bind the actual candidate transfer")
        self.check(runtime.get("image") == self.contract["runtime_image"] and runtime.get("toolAbsence") == dict.fromkeys(("dotnet", "cargo", "rustc", "rustup", "clang", "cc"), True), "Runtime-only result lacks the pinned image/absence of build tools")
        expected_pairs = {(graph, provider) for graph, providers in {"sqlite": ["sqlite"], "postgresql": ["postgresql"], "combined": ["sqlite", "postgresql"]}.items() for provider in providers}
        cases = runtime["cases"]
        self.check(len(cases) == 4 and {(case["graph"], case["provider"]) for case in cases} == expected_pairs, "Runtime-only provider/graph matrix is incomplete")
        self.check(set(transfer.data["graphs"]) == {"sqlite", "postgresql", "combined"}, "Transferred graph set is incomplete")
        candidate = self.doc("db-scope/release/evidence/candidate-destination.receipt.json").data
        for graph, transferred in transfer.data["graphs"].items():
            original = candidate["graphs"][graph]
            providers = [graph] if graph != "combined" else ["sqlite", "postgresql"]
            self.check(transferred.get("providers") == providers and transferred.get("selectedPackages") == self.closure_for("candidate", graph) and transferred.get("native") == original["nativeAfter"], "Transfer changed selected packages/native output identities")
            files = transferred["files"]; hash_map(files)
            self.check(transferred.get("executable") == graph + "/B24Consumer" and files.get("B24Consumer") == original["executableSha256"], "Transferred executable is not bound to the actual published AOT binary")
            self.elf(transferred["aotElfAudit"], files["B24Consumer"])
            native_files = {name: value for name, value in files.items() if name.endswith(".so")}
            self.check(native_files == {item["relativePath"]: item["sha256"] for item in transferred["native"].values()}, "Runtime transfer contains an undeclared or changed native library")
            for name in files:
                relative(Path("/synthetic-transfer-root"), name)
                self.check(not any(name.lower().startswith(prefix) for prefix in self.contract["retired_package_prefixes"]), "Retired product entered runtime transfer")
        for case in cases:
            graph, provider = case["graph"], case["provider"]
            self.check(case.get("passed") is True and case.get("processExited") is True and case.get("executableSha256") == transfer.data["graphs"][graph]["files"]["B24Consumer"] and hash_value(case.get("stdoutSha256")) and hash_value(case.get("stderrSha256")), "Runtime-only process lacks exact executed binary/terminal evidence")
            self.package_runtime_row(case["receipt"], provider, "aot", edited=graph == "combined")
        images = self.doc("db-scope/evidence/images.json").data
        for pinned in (self.contract["sdk_image"], self.contract["runtime_image"]):
            image, expected_digest = pinned.split("@", 1)
            expected_repo = image.rsplit(":", 1)[0]
            matches = [value for value in images if expected_repo + "@" + expected_digest in value.get("RepoDigests", [])]
            self.check(len(matches) == 1 and matches[0].get("Architecture") == "amd64" and matches[0].get("Os") == "linux" and str(matches[0].get("Id", "")).startswith("sha256:"), "Inspected container digest/platform differs from the required image")

    def run(self):
        self.section("reviewed-source-applicability", self.applicable)
        if self.failures:
            return self.report()
        self.section("producer-package-native-source-bindings", self.producer_check)
        self.section("top-level-committed-verification", self.top_level)
        self.section("lifecycle-matrix", lambda: self.matrix("api"))
        self.section("business-matrix", lambda: self.matrix("reference"))
        for provider in ("sqlite", "postgresql"):
            for mode in ("jit", "aot"):
                self.section("lifecycle-" + provider + "-" + mode, lambda p=provider, m=mode: self.lifecycle(p, m))
                self.section("business-faults-" + provider + "-" + mode, lambda p=provider, m=mode: self.business(p, m))
        self.section("local-package-consumers", lambda: self.package_consumer("db-scope/local-consumer/evidence/receipt.json", "local"))
        self.section("local-package-evidence-index", lambda: self.index("db-scope/local-consumer/evidence", "index.json"))
        if self.args.suite == "ci":
            self.section("pristine-sdk-release-and-rollback", self.release)
            self.section("runtime-only-transfer-and-images", self.runtime_only)
        return self.report()

    def report(self):
        status = "passed" if not self.failures else ("incomplete" if any(item["status"] == "missing" for item in self.failures) else "failed")
        return {"schema_version": 1, "task": "DB-Scope-01", "kind": "independent_read_only_receipt_review",
                "created_utc": datetime.now(timezone.utc).isoformat(), "status": status,
                "source": {"commit": self.args.source_commit, "tree": self.args.source_tree},
                "suite": self.args.suite, "contract_sha256": sha(self.args.contract),
                "validator_sha256": sha(__file__), "reviewed_source_files": len(self.contract["reviewed_source_sha256"]),
                "checked_predicates": self.checks, "sections": self.sections, "failures": self.failures,
                "input_receipts": self.inputs,
                "scope": {"independent_technical_evidence_review": True, "executed_product_tests": False,
                          "direct_package_bytes_rehashed": self.args.package_root is not None or self.args.candidate_feed is not None,
                          "direct_package_rehash_closures": ["previous", "candidate"] if self.args.package_root else (["candidate"] if self.args.candidate_feed else []),
                          "raw_fixture_sanitization_rechecked": self.args.raw_fixture_root is not None,
                          "pristine_sdk_and_runtime_receipts_required": self.args.suite == "ci",
                          "authored_provider_guides_are_outside_this_review": True},
                "limitations": ["Validates existing receipts and immutable source; performs no database/build/process execution.",
                                "The expected contract and evidence map are source-derived predicates, never runtime pass evidence.",
                                "Safe exports attest package/archive/output bytes through source-bound controllers and hash-linked receipts; direct archive rehashing requires --package-root or --candidate-feed.",
                                "A sanitized fixture's raw SHA-256 is checked against its parent pointers; raw bytes are independently rehashed only with --raw-fixture-root.",
                                "Typed DTO values are asserted before receipt emission in the exact reviewed sample source; the receipt exports named assertions, not DTO payload copies.",
                                "Local PATH isolation is not a pristine machine. The CI suite additionally requires actual pristine SDK, runtime-only and pinned-image receipts.",
                                "Does not authenticate artifact-download origin, GitHub run conclusion, PR review, merge status or merged-main CI; those need separate repository closeout evidence."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-root", type=Path, required=True, help="Artifacts directory containing verification.json and db-scope/")
    parser.add_argument("--source-repo", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-tree", required=True)
    parser.add_argument("--suite", choices=("local", "ci"), default="local")
    parser.add_argument("--contract", type=Path, default=Path(__file__).with_name("expected-contract.json"))
    parser.add_argument("--package-root", type=Path, help="Optional actual prepared/ root containing candidate/feed and previous/feed")
    parser.add_argument("--candidate-feed", type=Path, help="Optional candidate-only feed downloaded from the exact CI package artifact")
    parser.add_argument("--raw-fixture-root", type=Path, help="Optional actual _consumers/ root containing both database fixture matrices")
    parser.add_argument("--output", type=Path, required=True, help="New review JSON outside the repository and evidence roots")
    args = parser.parse_args()
    try:
        need(not args.output.resolve().is_relative_to(args.source_repo.resolve()) and not args.output.resolve().is_relative_to(args.evidence_root.resolve()), "Review output must be outside source and evidence trees")
        need(not args.output.exists(), "Review output already exists; preserve previous reviews")
        contract = decode(args.contract.read_bytes())
        result = Review(args, contract).run()
    except (Invalid, OSError, ValueError) as error:
        reason = str(error) if isinstance(error, Invalid) else "Invalid input or unavailable source (" + type(error).__name__ + ")"
        print(json.dumps({"status": "failed", "kind": "input-validation", "reason": reason}), file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "checked_predicates": result["checked_predicates"], "failed_sections": len(result["failures"]), "review_output": str(args.output), "executed_product_tests": False}))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
