#!/usr/bin/env python3
"""Audit existing main CI/public artifacts only; never build, publish or run a workload."""
from pathlib import Path
import datetime, hashlib, json, re, zipfile
import audit_artifacts

ROOT = Path(__file__).resolve().parent
MERGE = "36bd5ba169b628ba4d61dd9fe260eaef5ff15599"
TREE = "f7660759bba43ae83324620e2fb731efd479c3b5"
RUN = 46007977394


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    run = json.loads((ROOT / "main-run-final.json").read_bytes())
    jobs = json.loads((ROOT / "main-jobs-final.json").read_bytes())["jobs"]
    artifacts = json.loads((ROOT / "main-artifacts-final.json").read_bytes())["artifacts"]
    plan = json.loads((ROOT / "main-plan.json").read_bytes())
    preparation = json.loads((ROOT / "preparation.json").read_bytes())
    checks = []

    def require(name, condition):
        checks.append({"check": name, "passed": bool(condition)})
        if not condition:
            raise ValueError(name)

    require("completed main push CI", run["id"] == RUN and run["head_sha"] == MERGE and run["head_branch"] == "main" and run["event"] == "push" and run["status"] == "completed" and run["conclusion"] == "success")
    require("all selected jobs complete without failure", all(j["status"] == "completed" and j["conclusion"] in {"success", "skipped"} for j in jobs))
    for name in ["plan", "build (linux) / Run linux actions", "build (postgresql) / Run postgresql actions", "build (sqlite) / Run sqlite actions", "security / Secret scan", "security / CodeQL (csharp)", "security / CodeQL (python)", "Verify"]:
        require(name + " successful", any(j["name"] == name and j["conclusion"] == "success" for j in jobs))
    require("independent package checks selected", plan["public_checks"] == ["postgresql", "sqlite"] and set(plan["build_scopes"]) == {"linux", "postgresql", "sqlite"})
    for entry in preparation["sourceFiles"]:
        require("reviewed source " + entry["path"], sha(ROOT / "source" / entry["path"]) == entry["sha256"])

    packages = []
    payload_checks = 0
    for provider, job_id in [("postgresql", 140540738780), ("sqlite", 140540738813)]:
        payload = audit_artifacts.inspect(provider, "public")
        payload_checks += len(payload["checks"])
        (ROOT / ("public-" + provider + "-payload-consumer-audit.json")).write_text(json.dumps(payload, indent=2) + "\n")
        identity, version = payload["package"], payload["version"]
        directory = ROOT / ("public-" + provider)
        candidate = ROOT / ("candidate-" + provider)
        # plan_run.py writes the full plan to its log and strips only reasons
        # from GITHUB_OUTPUT; release.yml archives that exact workflow output.
        require(provider + " public plan equals exact workflow plan", json.loads((directory / "plan.json").read_bytes()) == {k: v for k, v in plan.items() if k != "reasons"})
        require(provider + " release record equals tested candidate", (directory / "publication/release.json").read_bytes() == (candidate / "release.json").read_bytes())
        artifact = next(a for a in artifacts if a["name"] == "public-consumption-" + provider + "-" + version)
        archive = ROOT / ("public-" + provider + "-" + str(RUN) + ".zip")
        require(provider + " artifact API digest and size", artifact["digest"] == "sha256:" + sha(archive) and artifact["size_in_bytes"] == archive.stat().st_size and artifact["expired"] is False)
        job = next(j for j in jobs if j["id"] == job_id)
        require(provider + " publish job successful", job["conclusion"] == "success")
        required_steps = ["Verify the tested tree, package allowlist and bytes", "Check for superseding package changes", "Push verified preview to nuget.org", "Wait for indexing and verify signed registry package", "Consume the public database packages in Native AOT", "Preserve actual registry bytes and public consumption receipts"]
        for step in required_steps:
            require(provider + " " + step, any(s["name"] == step and s["conclusion"] == "success" for s in job["steps"]))
        pub = directory / "publication"
        verification = json.loads((pub / "registry-readback" / (identity + ".verification.json")).read_bytes())
        package = pub / "registry-readback" / (identity + "." + version + ".nupkg")
        expected_url = "https://api.nuget.org/v3-flatcontainer/" + identity.lower() + "/" + version + "/" + package.name.lower()
        require(provider + " verified exact official package", verification["package"] == identity and verification["version"] == version and verification["source_commit"] == MERGE and verification["download_url"] == expected_url)
        require(provider + " verified signed payload receipt", verification["verified"] is True and verification["resume_allowed"] is True and verification["unsigned_entries_equal"] is True and verification["mode"] == "repository-signature-and-accepted-payload")
        require(provider + " upload and readback bytes", verification["upload_sha256"] == payload["uploadSha256"] and verification["registry_sha256"] == sha(package) == payload["packageSha256"])
        signature = verification["signature"]
        policy = preparation["signaturePolicy"]
        require(provider + " allowed signature identity", signature["verified"] is True and signature["archive_sha256"] == sha(package) and all(signature[k] == policy[k] for k in ["route", "service_index", "owners", "certificate_sha256"]))
        signature_out = (pub / "registry-readback" / identity / "verify.stdout").read_text()
        require(provider + " original cryptographic verifier success", "Successfully verified package '" + identity + "." + version + "'." in signature_out)
        require(provider + " original signature route/service/owner", re.findall(r"^Signature type: (.+)$", signature_out, re.M) == ["Repository"] and re.findall(r"^Service index: (.+)$", signature_out, re.M) == [policy["service_index"]] and re.findall(r"^Owners: (.+)$", signature_out, re.M) == [", ".join(policy["owners"])])
        require(provider + " original certificate subject/fingerprint", "Subject Name: " + policy["subject"] in signature_out and "SHA256 hash: " + policy["certificate_sha256"].upper() in signature_out)
        with zipfile.ZipFile(package) as packed:
            require(provider + " actual signature member present", ".signature.p7s" in packed.namelist())
        logs = (ROOT / ("publish-" + provider + "-" + str(job_id) + ".log")).read_text()
        require(provider + " actual public invocation", 'python3 eng/ci/consume.py "$CANDIDATE/release.json" artifacts/plan.json --public' in logs)
        b24 = [json.loads(line.split("B24_RESULT ", 1)[1]) for line in logs.splitlines() if "B24_RESULT {" in line]
        require(provider + " one public B24 AOT result", len(b24) == 1 and b24[0]["provider"] == provider and b24[0]["dynamicCodeSupported"] is False and {"actual-native-aot", "database-local-owners-retired"}.issubset(b24[0]["checks"]))
        require(provider + " B24 exact native image", b24[0]["nativeLibraries"] == [{"file": "libnw_database_" + provider + ".so", "sha256": payload["nativeSha256"]}])
        receipt = json.loads((pub / "consumer-evidence/public" / (provider + ".json")).read_bytes())
        packages.append({"provider": provider, "id": identity, "version": version, "sourceCommit": MERGE, "sourceTree": TREE, "inputs": plan["inputs"][provider], "payloadInputs": plan["payload_inputs"][provider], "publicationJobId": job_id, "publicationJobUrl": job["html_url"], "publicationJobConclusion": job["conclusion"], "artifactId": artifact["id"], "artifactSha256": sha(archive), "artifactBytes": archive.stat().st_size, "officialDownloadUrl": expected_url, "uploadSha256": verification["upload_sha256"], "signedRegistrySha256": verification["registry_sha256"], "nativeSha256": payload["nativeSha256"], "unsignedEntriesEqual": True, "unsignedEntryCount": payload["unsignedEntries"], "signature": signature, "publicPayloadAndConsumerChecks": len(payload["checks"]), "publicConsumerResult": receipt["result"], "aotPhases": [r["Phase"] for r in receipt["rows"]], "publicAotCommandExitCodes": [c["exit_code"] for c in receipt["commands"]], "sameNativeAfterDtoEdit": receipt["same_native_after_dto_edit"], "b24": b24[0], "consumerReceiptSha256": payload["consumerReceiptSha256"], "indexingAndSignatureStep": next(s for s in job["steps"] if s["name"] == "Wait for indexing and verify signed registry package"), "publicConsumerStep": next(s for s in job["steps"] if s["name"] == "Consume the public database packages in Native AOT")})

    report = {"task": "DB-Exec-Parity-01", "observedUtc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "status": "both-public-packages-verified-and-consumed-in-native-aot", "mergeCommit": MERGE, "sourceTree": TREE, "runId": RUN, "runUrl": run["html_url"], "runConclusion": run["conclusion"], "payloadAndConsumerChecks": payload_checks, "additionalReleaseChecks": len(checks), "allChecksPassed": True, "packages": packages, "newBuildOrWorkloadExecuted": False, "ciDispatchOrRerunExecuted": False, "packagePublishExecutedByThisAuditor": False, "limitations": ["Cryptographic verification was performed by the successful existing CI job; this reader independently checked its policy, raw signature logs, package hashes and unsigned payload. No local crypto/build/test rerun was performed.", "The release separately proves each standalone public package, not a combined two-package public consumer.", "Temporary Native AOT executable bytes, restored NuGet.Config and project.assets are not retained by the existing artifact recipe. AOT/public-source/cache isolation is bound to the exact reviewed source, public invocation, native/package hashes and raw execution receipts; no absent artifact is invented.", "This publication verification grants no new performance, sustained throughput, zero framework allocation or Dapper parity credit."], "checks": checks}
    path = ROOT / "public-release-audit-final.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"path": str(path), "sha256": sha(path), "allChecksPassed": True, "payloadChecks": payload_checks, "additionalChecks": len(checks)}))


if __name__ == "__main__":
    main()
