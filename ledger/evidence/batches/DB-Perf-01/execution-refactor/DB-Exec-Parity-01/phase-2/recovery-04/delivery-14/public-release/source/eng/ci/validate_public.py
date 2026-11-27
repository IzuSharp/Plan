"""Validate the public allowlist, provenance and exact package payload before NuGet login."""

import argparse
import json
from pathlib import Path
import sys
from catalog import ROOT, git, load_catalog
from impact import inputs
from facts import PROVIDERS
import provider_metadata
import xml.etree.ElementTree as ET
import zipfile


sys.path.insert(0, str(ROOT / "src/Verification.Compatibility"))
import compatibility as compat


def validate(folder, plan, version, module):
    tree = git("rev-parse", "HEAD^{tree}").decode().strip()
    record = compat.read_json(folder / "release.json")
    identities = load_catalog().packages
    if module not in set(plan["public_checks"] + plan["module_packages"]):
        raise ValueError("Module is outside the release plan")
    expected = {identities[module]}
    if (
        record["source_tree"] != tree
        or record["source_commit"] != git("rev-parse", "HEAD").decode().strip()
        or record["inputs"] != inputs("HEAD")
        or record["source_dirty"] is not False
    ):
        raise ValueError("Provider artifact is for a different source tree")
    packages = {p["id"]: p for p in record["packages"]}
    if not expected or set(packages) != expected or len(packages) != len(record["packages"]):
        raise ValueError("Provider selection differs from the main release plan")
    paths = {}
    for name, item in packages.items():
        if (
            item["dependencies"]
            or item["version"] != version
            or item["source_commit"] != record["source_commit"]
        ):
            raise ValueError("Unexpected version, source or external component dependencies")
        path = folder / "feed" / f"{name}.{version}.nupkg"
        if compat.file_hash(path) != item["upload_archive_sha256"]:
            raise ValueError("Candidate changed after consumption")
        provider = next(p for p, identity in identities.items() if identity == name)
        with zipfile.ZipFile(path) as archive:
            package_inputs = json.loads(archive.read("korda/public.json"))
            if package_inputs["inputs"] != record["inputs"][provider]:
                raise ValueError("Packaged provider fingerprint differs from the tested inputs")
            metadata = ET.fromstring(archive.read(name + ".nuspec")).find("{*}metadata")
            if metadata.findtext("{*}id") != name or metadata.findtext("{*}version") != version:
                raise ValueError("Packed NuGet identity differs from the release plan")
            if module in PROVIDERS:
                provider_metadata.verify(archive, metadata, module, name, version)
                if package_inputs.get("payload_inputs") != plan["payload_inputs"][module]:
                    raise ValueError("Packaged provider has different non-metadata inputs")
            if metadata.find(".//{*}dependency") is not None:
                raise ValueError("Public provider requires another package")
        paths[name] = path
    if set(paths.values()) != set((folder / "feed").iterdir()):
        raise ValueError("Unexpected file in publication feed")
    compat.validate_closure(record, paths)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("version")
    parser.add_argument("--module", required=True)
    args = parser.parse_args()
    for path in validate(
        args.directory, json.loads(args.plan.read_text()), args.version, args.module
    ).values():
        print(path)
