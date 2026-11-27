#!/usr/bin/env python3
"""Read-only audit of downloaded, existing CI artifact bytes; never run a workload."""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parent
MERGE = "36bd5ba169b628ba4d61dd9fe260eaef5ff15599"
TREE = "f7660759bba43ae83324620e2fb731efd479c3b5"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inspect(provider, stage):
    directory = ROOT / (stage + "-" + provider)
    if stage == "public":
        directory = directory / "publication"
    plan = json.loads((ROOT / "main-plan.json").read_bytes())
    release = json.loads((directory / "release.json").read_bytes())
    checks = []

    def check(name, condition):
        checks.append({"check": name, "passed": bool(condition)})
        if not condition:
            raise ValueError(name)

    check("source commit", release["source_commit"] == MERGE)
    check("source tree", release["source_tree"] == TREE)
    check("clean source", release["source_dirty"] is False)
    check("full planned input map", release["inputs"] == plan["inputs"])
    check("one independent package", len(release["packages"]) == 1)
    record = release["packages"][0]
    identity = "Korda.Database." + ("Sqlite" if provider == "sqlite" else "PostgreSql")
    check("package ID", record["id"] == identity)
    check("planned version", record["version"] == plan["versions"][provider])
    check("no top-level package dependency", record["dependencies"] == {})
    check("package source commit", record["source_commit"] == MERGE)
    packages = list(directory.rglob("*.nupkg"))
    check("one downloaded package archive", len(packages) == 1)
    package = packages[0]
    package_bytes = package.read_bytes()
    package_hash = sha(package_bytes)
    if stage == "candidate":
        check("upload archive SHA", package_hash == record["upload_archive_sha256"])
    with zipfile.ZipFile(package) as archive:
        names = archive.namelist()
        check("ZIP names unique", len(names) == len(set(names)))
        entries = {n: sha(archive.read(n)) for n in names if n != ".signature.p7s"}
        check("all unsigned entries match accepted candidate", entries == record["unsigned_entries"])
        public = json.loads(archive.read("korda/public.json"))
        check("embedded inputs", public["inputs"] == plan["inputs"][provider])
        check("embedded payload inputs", public["payload_inputs"] == plan["payload_inputs"][provider])
        spec = ET.fromstring(archive.read(identity + ".nuspec"))
        ns = {"n": spec.tag.split("}")[0].lstrip("{")} if "}" in spec.tag else {}
        prefix = "n:" if ns else ""
        metadata = spec.find(prefix + "metadata", ns)
        check("nuspec ID", metadata.findtext(prefix + "id", namespaces=ns) == identity)
        check("nuspec version", metadata.findtext(prefix + "version", namespaces=ns) == record["version"])
        check("nuspec repository commit", metadata.find(prefix + "repository", ns).attrib["commit"] == MERGE)
        native = record["native"]
        check("native bytes", sha(archive.read(native["path"])) == native["sha256"])
        check("native source", native["source_commit"] == MERGE)
        native_hash = native["sha256"]

    receipt_path = directory / "consumer-evidence" / stage / (provider + ".json")
    receipt = json.loads(receipt_path.read_bytes())
    check("consumer passed", receipt["result"] == "passed")
    check("consumer package/version", (receipt["package"], receipt["version"]) == (identity, record["version"]))
    check("consumer used exact downloaded package", receipt["tutorial_package_sha256"] == package_hash)
    check("tutorial compilation recorded", receipt["tutorials_compiled_against_candidate"] is True)
    check("native reuse recorded", receipt["same_native_after_dto_edit"] is True)
    commands = receipt["commands"]
    check("six actual commands", len(commands) == 6)
    check("publish/execute order", [(c["revision"], c["stage"]) for c in commands] == [(r, s) for r in ("scaffold", "original", "edited") for s in ("publish", "execute")])
    for command in commands:
        tag = command["revision"] + "/" + command["stage"]
        check(tag + " exit0", command["exit_code"] == 0)
        log = receipt_path.parent / command["log"]
        check(tag + " actual log SHA", sha(log.read_bytes()) == command["sha256"])
        if command["stage"] == "publish":
            argv = command["command"]
            check(tag + " Release NativeAOT linux-x64", "-p:PublishAot=true" in argv and "Release" in argv and "linux-x64" in argv and "-p:KordaVersion=" + record["version"] in argv)
        else:
            check(tag + " direct executable", Path(command["command"][0]).name == "OrmExperience")

    tree = ast.parse((ROOT / "source/eng/ci/orm_experience.py").read_text())
    required = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "REQUIRED" for t in n.targets))
    rows = receipt["rows"]
    check("three actual phases", [r["Phase"] for r in rows] == ["scaffold", "original", "edited"])
    for row in rows:
        phase = row["Phase"]
        checks_required = required | ({"scaffolded-entity-compiled-and-executed", "scaffolded-composite-key-compiled-and-executed"} if phase != "scaffold" else set())
        check(phase + " provider", row["Provider"] == ("Sqlite" if provider == "sqlite" else "PostgreSql"))
        check(phase + " AOT result", row["Aot"] is True)
        check(phase + " DTO result", row["Dto"] == ("edited" if phase == "edited" else "original"))
        check(phase + " required business checks", checks_required.issubset(row["Checks"]))
        check(phase + " SQL count", row["SqlExecutions"] == 2)
        check(phase + " protocol count", row["ProtocolSubmissions"] == 0 if provider == "sqlite" else row["ProtocolSubmissions"] >= 2)
        check(phase + " actual native", row["NativeSha256"] == native_hash)
        check(phase + " no project references", row["ProjectReferences"] == 0)
        command = next(c for c in commands if c["revision"] == phase and c["stage"] == "execute")
        business = [json.loads(line.removeprefix("DB_API_RESULT ")) for line in (receipt_path.parent / command["log"]).read_text().splitlines() if line.startswith("DB_API_RESULT ")]
        check(phase + " one original business result", len(business) == 1)
        check(phase + " raw business result matches receipt", all(row[k] == v for k, v in business[0].items()))
    original, edited = rows[1:]
    check("DTO source changed", original["ModelsSha256"] != edited["ModelsSha256"])
    check("AOT executable hash changed as reported", original["ExecutableSha256"] != edited["ExecutableSha256"])
    check("only Models.cs changed", original["Sources"].keys() == edited["Sources"].keys() and {k for k in original["Sources"] if original["Sources"][k] != edited["Sources"][k]} == {"Models.cs"})
    check("scaffold reused", original["ScaffoldSha256"] == edited["ScaffoldSha256"])
    tutorials = {t["compiled_file"]: t["compiled_sha256"] for t in receipt["tutorials"]}
    check("four same compiled tutorials", len(tutorials) == 4 and original["TutorialSources"] == tutorials and edited["TutorialSources"] == tutorials)
    return {"provider": provider, "stage": stage, "package": identity, "version": record["version"], "packagePath": str(package.relative_to(ROOT)), "packageBytes": len(package_bytes), "packageSha256": package_hash, "uploadSha256": record["upload_archive_sha256"], "nativeSha256": native_hash, "unsignedEntries": len(record["unsigned_entries"]), "inputs": public, "consumerReceiptSha256": sha(receipt_path.read_bytes()), "checks": checks, "passed": all(c["passed"] for c in checks), "publicOriginOrSignatureVerifiedByThisScript": False, "scope": "Reads existing CI package/receipt/log bytes only. Public origin and cryptographic signature receipts are separately checked against the completed release job. Temporary AOT ELF bytes and restored NuGet.Config/project.assets are not archived here; their identities are reported by the bound CI code and logs."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("candidate", "public"))
    args = parser.parse_args()
    result = {"task": "DB-Exec-Parity-01", "sourceCommit": MERGE, "sourceTree": TREE, "stage": args.stage, "scriptSha256": sha(Path(__file__).read_bytes()), "packages": [inspect(p, args.stage) for p in ("sqlite", "postgresql")], "newBuildOrWorkloadExecuted": False}
    path = ROOT / (args.stage + "-artifact-audit.json")
    if path.exists():
        raise FileExistsError(path)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(path), "sha256": sha(path.read_bytes()), "packages": [{"id": p["package"], "version": p["version"], "passed": p["passed"], "checks": len(p["checks"])} for p in result["packages"]]}))
