#!/usr/bin/env python3
"""Read actual release artifacts; bind CI receipts to downloaded archive bytes.

This does not execute a consumer, repeat cryptographic verification, or add a CI
gate. Signature acceptance is the existing CI verifier's retained observation.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text())


def one(items, description):
    assert len(items) == 1, (description, items)
    return items[0]


def read_provider(root, provider, artifacts):
    candidate = read_json(root / f"candidate-{provider}" / "release.json")
    package = one(candidate["packages"], "independent provider package")
    identity, version = package["id"], package["version"]
    artifact = one([a for a in artifacts if a["name"] ==
                    f"public-consumption-{provider}-{version}"], "public artifact")
    data = (root / "downloads" / f"public-{provider}.zip").read_bytes()
    assert "sha256:" + sha(data) == artifact["digest"]
    assert len(data) == artifact["size_in_bytes"]
    assert artifact["workflow_run"]["head_sha"] == candidate["source_commit"]
    output = root / f"public-{provider}"
    output.mkdir(exist_ok=False)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = [n for n in archive.namelist() if not n.endswith("/")]
        assert len(names) == len(set(names))
        assert all(not PurePosixPath(n).is_absolute() and ".." not in PurePosixPath(n).parts
                   for n in names)
        release_name = one([n for n in names if n.endswith("/release.json") or n == "release.json"], "release")
        release = json.loads(archive.read(release_name))
        assert release == candidate
        assert not release["source_dirty"] and package["dependencies"] == {}
        plan_name = one([n for n in names if n.endswith("/plan.json") or n == "plan.json"], "plan")
        plan = json.loads(archive.read(plan_name))
        assert plan["versions"][provider] == version
        assert plan["inputs"][provider] == candidate["inputs"][provider]
        verification_name = one([n for n in names if n.endswith(f"/{identity}.verification.json")], "registry verification")
        verification = json.loads(archive.read(verification_name))
        assert verification["package"] == identity and verification["version"] == version
        assert verification["source_commit"] == candidate["source_commit"]
        assert verification["mode"] == "repository-signature-and-accepted-payload"
        assert all(verification[k] is True for k in ("verified", "resume_allowed", "unsigned_entries_equal"))
        assert verification["upload_sha256"] == package["upload_archive_sha256"]
        package_name = one([n for n in names if n.endswith(".nupkg")], "retained signed package")
        package_bytes = archive.read(package_name)
        registry_sha = sha(package_bytes)
        assert registry_sha == verification["registry_sha256"]
        signature = verification["signature"]
        assert signature["verified"] is True and signature["archive_sha256"] == registry_sha
        assert signature["route"] == "repository-primary"
        assert signature["service_index"] == "https://api.nuget.org/v3/index.json"
        assert signature["owners"] == ["dekueon"]
        assert signature["certificate_sha256"] == "1f4b311d9acc115c8dc8018b5a49e00fce6da8e2855f9f014ca6f34570bc482d"
        expected_url = f"https://api.nuget.org/v3-flatcontainer/{identity.lower()}/{version}/{identity.lower()}.{version}.nupkg"
        assert verification["download_url"] == expected_url
        with zipfile.ZipFile(io.BytesIO(package_bytes)) as package_archive:
            native = package["native"]
            assert sha(package_archive.read(native["path"])) == native["sha256"]
            metadata = json.loads(package_archive.read("korda/public.json"))
            assert metadata["inputs"] == candidate["inputs"][provider]
            assert metadata["payload_inputs"] == plan["payload_inputs"][provider]
            (output / "public-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        consumer_name = one([n for n in names if n.endswith(f"/consumer-evidence/public/{provider}.json")], "public consumer")
        consumer = json.loads(archive.read(consumer_name))
        assert consumer["task"] == "DB-API-01" and consumer["result"] == "passed"
        assert consumer["package"] == identity and consumer["version"] == version
        assert consumer["tutorial_package_sha256"] == registry_sha
        assert consumer["same_native_after_dto_edit"] is True
        assert consumer["tutorials_compiled_against_candidate"] is True
        assert len(consumer["tutorials"]) == 4
        assert len(consumer["commands"]) == 6 and len(consumer["rows"]) == 3
        assert {(c["revision"], c["stage"]) for c in consumer["commands"]} == {
            (revision, stage) for revision in ("scaffold", "original", "edited")
            for stage in ("publish", "execute")}
        rows = {r["Phase"]: r for r in consumer["rows"]}
        assert set(rows) == {"scaffold", "original", "edited"}
        assert all(r["Aot"] is True and r["ProjectReferences"] == 0 and
                   r["NativeSha256"] == native["sha256"] for r in rows.values())
        before, after = rows["original"], rows["edited"]
        assert before["ModelsSha256"] != after["ModelsSha256"]
        assert before["ExecutableSha256"] != after["ExecutableSha256"]
        assert before["ScaffoldSha256"] == after["ScaffoldSha256"]
        assert before["TutorialSources"] == after["TutorialSources"]
        tutorial_hashes = {t["compiled_file"]: t["compiled_sha256"] for t in consumer["tutorials"]}
        assert len(tutorial_hashes) == 4 and before["TutorialSources"] == tutorial_hashes
        assert set(before["Sources"]) == set(after["Sources"])
        assert [k for k in before["Sources"] if before["Sources"][k] != after["Sources"][k]] == ["Models.cs"]
        prefix = str(PurePosixPath(consumer_name).parent)
        for command in consumer["commands"]:
            assert command["exit_code"] == 0
            log_bytes = archive.read(prefix + "/" + command["log"])
            assert sha(log_bytes) == command["sha256"]
            if command["stage"] == "execute":
                receipts = [json.loads(line.removeprefix("DB_API_RESULT "))
                            for line in log_bytes.decode().splitlines() if line.startswith("DB_API_RESULT ")]
                observed = one(receipts, "actual business result")
                fields = {"Provider", "Aot", "Dto", "Checks", "SqlExecutions", "ProtocolSubmissions", "NativeSha256"}
                assert set(observed) == fields
                assert observed == {k: rows[command["revision"]][k] for k in fields}
        retained = []
        for name in names:
            if name.endswith(".nupkg"):
                continue
            payload = archive.read(name)
            payload.decode("utf-8")
            target = output / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)
            retained.append({"path": name, "bytes": len(payload), "sha256": sha(payload)})
    return {"provider": provider, "artifactId": artifact["id"], "artifactSha256": sha(data),
            "package": identity, "version": version, "sourceCommit": candidate["source_commit"],
            "sourceTree": candidate["source_tree"], "uploadPackageSha256": package["upload_archive_sha256"],
            "registryPackageSha256": registry_sha, "nativeSha256": native["sha256"],
            "inputs": candidate["inputs"][provider], "payloadInputs": metadata["payload_inputs"],
            "signature": signature, "registryVerification": verification,
            "consumerResult": consumer["result"], "successfulCommands": 6, "aotRows": 3,
            "sameNativeAfterDtoEdit": True, "tutorialPackageMatchesSignedRegistry": True,
            "retainedText": retained, "omittedSignedPackage": {"path": package_name, "bytes": len(package_bytes), "sha256": registry_sha}}


parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, required=True)
args = parser.parse_args()
artifacts = read_json(args.root / "public-artifact-inventory-01.json")["artifacts"]
observations = [read_provider(args.root, provider, artifacts) for provider in ("sqlite", "postgresql")]
result = {"scope": "Read-only artifact-byte and retained-receipt binding; signature and AOT execution performed by the unchanged CI", "providers": observations}
(args.root / "public-artifact-observations-01.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"providers": [{k: p[k] for k in ("provider", "package", "version", "registryPackageSha256", "consumerResult")} for p in observations]}, indent=2))
