#!/usr/bin/env python3
"""Finite synthetic controls only; no real measurement or consumer is read."""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
import tarfile
import tempfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    results = []
    scenarios = ("positive", "symlink-file", "core-dump", "report-so-name", "exclude-db-archive",
                 "wrong-inventory-sha", "wrong-file-sha", "missing-field", "empty-inventory",
                 "malformed-digest", "relative-input", "missing-input", "directory-input",
                 "existing-output", "nested-output", "aliased-output", "directory-symlink")
    with tempfile.TemporaryDirectory(prefix="DB-Exec-10-archive-controls-") as temporary:
        for scenario in scenarios:
            root = Path(temporary) / scenario
            measurement = root / "measurements"
            measurement.mkdir(parents=True)
            source = root / "Program.cs"
            source.write_bytes(b"// synthetic source\n")
            raw = b'{"SyntheticOnly": true}\r\n'
            failure = b"\xff failed original bytes\r\n"
            (measurement / "raw.json").write_bytes(raw)
            (measurement / "failure.stdout").write_bytes(failure)
            (measurement / "fixture.db").write_bytes(b"SQLite format 3\x00" + b"synthetic")
            elf = bytearray(64); elf[:6] = b"\x7fELF\x02\x01"; elf[16:18] = (2).to_bytes(2, "little")
            (measurement / "consumer").write_bytes(elf)
            (measurement / "Korda.nupkg").write_bytes(b"PK\x03\x04synthetic package")
            inventory = {"inputFiles": {str(source): sha(source.read_bytes())}}
            output = root / "archive"
            extra = []
            positive = scenario in scenarios[:5]
            if scenario == "symlink-file":
                (measurement / "source-link.cs").symlink_to(source)
            elif scenario == "core-dump":
                elf[16:18] = (4).to_bytes(2, "little")
                (measurement / "core").write_bytes(elf)
            elif scenario == "report-so-name":
                (measurement / "copy.so.report.json").write_text('{"not": "a library"}\n')
            elif scenario == "exclude-db-archive":
                database_archive = measurement / "retained-db.tar.gz"
                database_archive.write_bytes(b"synthetic database archive")
                extra = ["--exclude-file", "database", str(database_archive)]
            elif scenario == "wrong-file-sha":
                inventory["inputFiles"][str(source)] = "0" * 64
            elif scenario == "missing-field":
                inventory = {"different": {}}
            elif scenario == "empty-inventory":
                inventory = {"inputFiles": {}}
            elif scenario == "malformed-digest":
                inventory["inputFiles"][str(source)] = {"sha256": "0" * 64}
            elif scenario == "relative-input":
                inventory["inputFiles"] = {"Program.cs": sha(source.read_bytes())}
            elif scenario == "missing-input":
                source.unlink()
            elif scenario == "directory-input":
                inventory["inputFiles"] = {str(measurement): "0" * 64}
            elif scenario == "existing-output":
                output.mkdir()
                (output / "sentinel").write_bytes(b"unchanged")
            elif scenario == "nested-output":
                output = measurement / "nested"
            elif scenario == "aliased-output":
                (root / "alias").symlink_to(measurement, target_is_directory=True)
                output = root / "alias" / "nested"
            elif scenario == "directory-symlink":
                (measurement / "outside").symlink_to(root, target_is_directory=True)
            inventory_file = root / "inventory.json"
            inventory_file.write_text(json.dumps(inventory) + "\n")
            expected = "0" * 64 if scenario == "wrong-inventory-sha" else sha(inventory_file.read_bytes())
            run = subprocess.run([sys.executable, str(args.tool.resolve()), "--measurements", str(measurement),
                                  "--inventory", str(inventory_file), "/inputFiles", expected,
                                  "--scope", "Synthetic control; zero measurement credit",
                                  "--output-dir", str(output), *extra], capture_output=True, text=True)
            assert (run.returncode == 0) == positive, (scenario, run.stdout, run.stderr)
            if positive:
                manifest = json.loads((output / "manifest.json").read_text())
                records = {record["source"]: record for record in manifest["records"]}
                assert records[str(measurement / "fixture.db")]["reasonCode"] == "database"
                assert records[str(measurement / "consumer")]["reasonCode"] == "binary"
                assert records[str(measurement / "Korda.nupkg")]["reasonCode"] == "package"
                with tarfile.open(output / "evidence.tar.gz", "r:gz") as archive:
                    assert archive.extractfile("measurements/raw.json").read() == raw
                    assert archive.extractfile("measurements/failure.stdout").read() == failure
                    if scenario == "symlink-file":
                        assert archive.extractfile("measurements/source-link.cs").read() == source.read_bytes()
                    if scenario == "core-dump":
                        assert archive.extractfile("measurements/core").read() == elf
                    if scenario == "report-so-name":
                        assert archive.extractfile("measurements/copy.so.report.json").read().startswith(b'{"not"')
                if scenario == "exclude-db-archive":
                    assert records[str(database_archive)]["disposition"] == "excluded"
            else:
                assert not (output / "evidence.tar.gz").exists()
                if scenario == "existing-output":
                    assert (output / "sentinel").read_bytes() == b"unchanged"
            results.append({"scenario": scenario, "expected": "retain" if positive else "reject",
                            "exitCode": run.returncode, "passed": True})
        publish = runpy.run_path(str(args.tool))["publish_new"]
        for target_kind in ("absent", "existing-file", "dangling-symlink"):
            root = Path(temporary) / ("publication-" + target_kind)
            root.mkdir()
            original = root / "archive.partial"
            original.write_bytes(b"verified synthetic archive bytes")
            target = root / "archive"
            if target_kind == "existing-file":
                target.write_bytes(b"must not change")
            elif target_kind == "dangling-symlink":
                target.symlink_to(root / "does-not-exist")
            try:
                publish(original, target)
            except FileExistsError:
                assert target_kind != "absent" and original.read_bytes() == b"verified synthetic archive bytes"
                if target_kind == "existing-file":
                    assert target.read_bytes() == b"must not change"
                else:
                    assert target.is_symlink() and not target.exists()
            else:
                assert target_kind == "absent" and not original.exists()
                assert target.read_bytes() == b"verified synthetic archive bytes"
            results.append({"scenario": "publication-" + target_kind,
                            "expected": "publish" if target_kind == "absent" else "reject", "passed": True})
    result = {"schemaVersion": 1, "toolSha256": sha(args.tool.read_bytes()),
              "controls": results, "passed": len(results), "measurementFilesRead": 0,
              "productExecutions": 0, "realArchivesCreated": 0, "finalAcceptanceCredit": False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2); stream.write("\n")
    print(json.dumps({key: value for key, value in result.items() if key != "controls"}))


if __name__ == "__main__":
    main()
