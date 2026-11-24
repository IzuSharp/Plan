"""Inspect exact candidate DLL/XML/README bytes with the existing compiled API gate."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

root = Path.cwd()
scope = sys.argv[1]
source = root.parent / "Korda-DB-Rename-01-linux"
sdk = root.parent / "tooling/dotnet"
record = json.loads((root / "artifacts/public/release.json").read_text())
package, = record["packages"]
archive = root / "artifacts/public/feed" / (package["id"] + "." + package["version"] + ".nupkg")
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert sha(archive) == package["upload_archive_sha256"]
assert record["source_commit"] == subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
assert record["source_commit"] == subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
mapping = json.loads((source / "src/Query.Generator/db-rename-01.names.json").read_text())["attributes"]
destination = root / "artifacts/db-rename-packed-api"
destination.mkdir(exist_ok=False)
with zipfile.ZipFile(archive) as packed:
    for ext in ("dll", "xml"):
        (destination / ("Korda.Data." + ext)).write_bytes(packed.read("lib/net11.0/Korda.Data." + ext))
    xml = packed.read("lib/net11.0/Korda.Data.xml")
    members = [node.attrib["name"] for node in ET.fromstring(xml).findall("./members/member")]
    expected = {"T:Korda.Data." + name for name in mapping.values()}
    assert expected.issubset(members)
    for name in packed.namelist():
        if name.endswith(".xml") and name.startswith(("lib/", "tools/")):
            text = packed.read(name).decode("utf-8")
            assert not any(re.search(r"\b" + re.escape(old) + r"\b", text) for old in mapping), name
    readme = packed.read("README.md")
    assert not re.search(rb"weave", readme, re.I)
    for name in (b"DbTable", b"DbKey", b"DbProjection", b"DbCodec", b"DbUseCodec"):
        assert name in readme, name
    native = json.loads(packed.read("korda/manifest.json"))
command = [str(sdk / "dotnet"), str(source / "tests/Data.Abstractions/ApiCheck/bin/Release/net11.0/ApiCheck.dll"),
           str(source), str(sdk), str(destination / "Korda.Data.dll")]
result = subprocess.run(command, capture_output=True, text=True)
(destination / "compiled-api.log").write_text(result.stdout + result.stderr)
print(result.stdout)
if result.returncode:
    print(result.stderr)
    raise SystemExit(result.returncode)
report = {"task": "DB-Rename-01", "result": "passed", "provider": scope,
          "source_commit": record["source_commit"], "source_tree": record["source_tree"],
          "package": package["id"], "version": package["version"], "archive_sha256": sha(archive),
          "data_dll_sha256": sha(destination / "Korda.Data.dll"),
          "data_xml_sha256": sha(destination / "Korda.Data.xml"),
          "readme_sha256": hashlib.sha256(readme).hexdigest(), "native_sha256": native["nativeSha256"],
          "new_attribute_types": sorted(expected), "old_public_attribute_types_absent": True,
          "old_attribute_xml_members_absent": True, "readme_current_names": True,
          "compiled_api_command": command, "compiled_api_exit_code": result.returncode,
          "compiled_api_log_sha256": sha(destination / "compiled-api.log")}
(destination / "receipt.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
