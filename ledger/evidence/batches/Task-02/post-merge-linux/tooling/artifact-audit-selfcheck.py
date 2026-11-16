#!/usr/bin/env python3
"""Synthetic reader checks only; no product, registry or workflow execution."""
import copy
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "artifact-audit-selfcheck-data-review-fixed-001"
WORK.mkdir(exist_ok=False)
SHA = "a" * 40
VERSION = "0.1.0-preview.999.1"
PACKAGE = f"NativeWeave.HelloWorld.{VERSION}.nupkg"
NATIVE = b"SYNTHETIC native payload; never executed\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2) + "\n").encode()


def archive(entries):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as package:
        for name, data in entries:
            package.writestr(name, data)
    return output.getvalue()


manifest = {"schemaVersion": 1, "packageId": "NativeWeave.HelloWorld", "packageVersion": VERSION,
            "rid": "linux-x64", "sourceCommit": SHA, "sourceDirty": False,
            "nativePath": "runtimes/linux-x64/native/libnativeweave_hello.so", "nativeSha256": digest(NATIVE)}
manifest_bytes = encoded(manifest)
package = archive([("nativeweave/manifest.json", manifest_bytes), (manifest["nativePath"], NATIVE)])
candidate_entries = [("manifest.json", manifest_bytes), (PACKAGE, package),
                     ("SHA256SUMS", (digest(manifest_bytes) + "  manifest.json\n" + digest(package) + "  " + PACKAGE + "\n").encode())]
registry_hash = digest(b"SYNTHETIC distinct signed registry ZIP identity")
publication = {"status": "published-and-consumed", "version": VERSION, "uploadSha256": digest(package),
               "registrySha256": registry_hash, "signatureVerified": True,
               "unsignedPayloadEntriesEqual": True, "registryPackageJitAndAotExecuted": True}
consumer = {"status": "passed", "rid": "linux-x64", "package": PACKAGE, "packageSha256": registry_hash,
            "nativeSha256": digest(NATIVE), "ridFreeBuildAndRun": True, "nativeAotExecuted": True,
            "isolatedNugetCache": True, "outsideSourceTree": True, "rustInvocationTrap": True, "pristineMachine": False}
logs = []
for app, output in (("HelloWorld", "Hello, World! From Rust."),
                    ("InteropTests", "PASS: default, named/delegate calls, Unicode, NUL, empty, size boundaries, invalid input and 1000 concurrent greetings.")):
    for mode in ("package-run", "aot-run"):
        logs.append((f"logs/{app}-{mode}.log", (output + "\n").encode()))
    logs.append((f"logs/{app}-aot-publish.log", f"  Generating native code\n  {app} -> /synthetic/{app}/publish/\n".encode()))
results = []
for name, expected in (("distinct-signed-hash-and-declared-false-scope", 0),
                       ("wrong-actual-merge", 1), ("integer-not-json-true", 1),
                       ("traversal-member", 1), ("missing-actual-aot-log", 1),
                       ("embedded-number-versus-external-boolean", 1)):
    fixture = WORK / name
    fixture.mkdir()
    pub = copy.deepcopy(publication)
    entries = list(candidate_entries)
    run_logs = list(logs)
    if name == "integer-not-json-true":
        pub["signatureVerified"] = 1
    if name == "traversal-member":
        entries.append(("../../escaped.txt", b"MUST NEVER EXTRACT"))
    if name == "missing-actual-aot-log":
        run_logs = [(path, data) for path, data in run_logs if path != "logs/InteropTests-aot-run.log"]
    if name == "embedded-number-versus-external-boolean":
        changed = copy.deepcopy(manifest)
        changed["sourceDirty"] = 0
        changed_package = archive([("nativeweave/manifest.json", encoded(changed)), (manifest["nativePath"], NATIVE)])
        entries = [("manifest.json", manifest_bytes), (PACKAGE, changed_package),
                   ("SHA256SUMS", (digest(manifest_bytes) + "  manifest.json\n" + digest(changed_package) + "  " + PACKAGE + "\n").encode())]
        pub["uploadSha256"] = digest(changed_package)
    candidate = fixture / "candidate.zip"
    published = fixture / "publication.zip"
    candidate.write_bytes(archive(entries))
    published.write_bytes(archive([("publication.json", encoded(pub)), ("consumer-result.json", encoded(consumer))] + run_logs))
    command = [sys.executable, str(ROOT / "audit-release-artifacts.py"), "--candidate", str(candidate),
               "--publication", str(published), "--merge", "b" * 40 if name == "wrong-actual-merge" else SHA,
               "--version", VERSION, "--output", str(fixture / "audit")]
    result = subprocess.run(command, capture_output=True, text=True)
    (fixture / "stdout.log").write_text(result.stdout)
    (fixture / "stderr.log").write_text(result.stderr)
    receipt = fixture / "audit/audit.json"
    parsed = json.loads(receipt.read_text()) if receipt.is_file() else {}
    exact_type_failure = name != "embedded-number-versus-external-boolean" or (
        not parsed.get("errors") and [item["check"] for item in parsed.get("checks", []) if not item["passed"]]
        == ["Embedded and external manifests match"])
    results.append({"case": name, "syntheticOnly": True, "expectedExit": expected, "actualExit": result.returncode,
                    "passed": result.returncode == expected and receipt.is_file() and exact_type_failure,
                    "command": command, "auditSha256": digest(receipt.read_bytes()) if receipt.is_file() else None})
report = {"scope": "Synthetic artifact-reader checks only; no release/product acceptance claim", "scriptSha256": digest((ROOT / "audit-release-artifacts.py").read_bytes()),
          "selfcheckSourceSha256": digest(Path(__file__).read_bytes()), "cases": results,
          "escapedFileAbsent": not (WORK / "escaped.txt").exists() and not (ROOT / "escaped.txt").exists()}
report["passed"] = all(case["passed"] for case in results) and report["escapedFileAbsent"]
(ROOT / "artifact-audit-selfcheck.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"passed": report["passed"], "cases": len(results)}, indent=2))
sys.exit(0 if report["passed"] else 1)
