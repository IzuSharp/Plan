"""Finite, synthetic-only archive checks; never start an application or database.

Source-prepared during the exclusive measurement window. Run only after root
opens the separate validation window; these fixtures claim no load acceptance.
"""
from __future__ import annotations

import argparse
import base64
import contextlib
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("perf01_archive", Path(__file__).with_name("pack_evidence.py"))
archive = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(archive)


class ArchiveChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.cell = self.root / "cell"
        self.cell.mkdir()
        self.receipt = self.root / "verification.json"
        self.bundle = self.root / "bundle"
        self.group = "codec"
        self.raw = {
            "summary.json": b'{"fixture_only": true}\n',
            "plan.json": b'{"domain": "codec", "fixture_only": true}\n',
            "result.json": b'{"complete": true, "fixture_only": true}\n',
            "operations.jsonl": '{"id":0,"value":"synthetic-\u03bb"}\n'.encode(),
            "events.jsonl": b'{"id":0,"kind":"completed"}\n',
            "resources.jsonl": b"",
            "phase-progress.json": b'{"phase":"finished","fixture_only":true}\n',
        }
        for name, value in self.raw.items():
            (self.cell / name).write_bytes(value)
        self.pin()

    def tearDown(self):
        self.temp.cleanup()

    def pin(self):
        self.receipt.write_text(json.dumps({"task": "Perf-01", "group": self.group, "accepted": False,
            "duration_credit_seconds": 0, "verifier_sha256": "0" * 64,
            "limitations": ["Synthetic archive fixture; no measurement was performed."],
            "evidence_sha256": {name: archive.sha(self.cell / name) for name in self.raw}}))

    def pack(self, **changes):
        values = dict(group=self.group, cell=self.cell, receipt=self.receipt, output=self.bundle, shard_mib=1, binding=[])
        values.update(changes)
        with contextlib.redirect_stdout(io.StringIO()):
            archive.pack(argparse.Namespace(**values))

    def database_fixture(self):
        self.group = "postgresql"
        original = "/synthetic-original/Perf-01/cell"
        prefix = "applications/nativeweave-aot-rust-fixture"
        values = {
            "summary.json": {"provider": self.group, "fixture_only": True,
                "application_receipt": {"path": original + "/" + prefix + "/receipt.json"}},
            "progress.json": {"state": "completed", "fixture_only": True},
            "plan.json": {"oracle": {"dataset": original + "/dataset.json"}, "fixture_only": True},
            "target.json": {"postgres_base": "postgresql://nativeweave@127.0.0.1:15432/postgres", "fixture_only": True},
            "frozen-inputs.json": {"fixture_only": True},
            "dataset.json": [{"input": "synthetic", "expected": "synthetic"}],
            "observation.json": {"fixture_only": True},
            prefix + "/receipt.json": {"fixture_only": True},
            prefix + "/perf01.json": {"fixture_only": True},
            prefix + "/generator-observer-receipt.json": {"fixture_only": True},
        }
        self.raw = {name: (json.dumps(value) + "\n").encode() for name, value in values.items()}
        self.raw.update({name: b'{"fixture_only":true}\n' for name in (
            "observation.events.jsonl", prefix + "/generator-resources.jsonl", prefix + "/application/resources.jsonl")})
        for name, value in self.raw.items():
            path = self.cell / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(value)
        excluded = self.cell / "supervision/receipt.json"; excluded.parent.mkdir()
        excluded.write_text('{"token":"synthetic-excluded-registration"}')
        self.pin()
        return prefix

    def test_exact_bytes_multichunk_empty_jsonl_and_exclusions(self):
        block = '{"id":0,"value":"synthetic-\u03bb"}\n'.encode()
        self.raw["operations.jsonl"] = block * (1024**2 // len(block) + 5)
        (self.cell / "operations.jsonl").write_bytes(self.raw["operations.jsonl"])
        (self.cell / "private-key.pem").write_text("synthetic excluded private input")
        (self.cell / "config.private.json").write_text('{"token":"synthetic-excluded-value"}')
        self.pin()
        self.pack()
        manifest = archive.verify(self.bundle)
        self.assertFalse(manifest["original_accepted"])
        self.assertEqual(0, manifest["original_duration_credit_seconds"])
        self.assertEqual(set(self.raw) | {"duration-verification.json"}, {row["path"] for row in manifest["files"]})
        self.assertEqual(2, len(next(row for row in manifest["files"] if row["path"] == "operations.jsonl")["chunks"]))
        restored = self.root / "restored"
        archive.verify(self.bundle, restored)
        for name, value in self.raw.items():
            self.assertEqual(value, (restored / name).read_bytes())
        self.assertEqual(self.receipt.read_bytes(), (restored / "duration-verification.json").read_bytes())

    def test_private_scalars_and_nested_wire_are_rejected(self):
        private_wire = base64.b64encode(b'{"authorization":"synthetic-secret"}').decode()
        for index, value in enumerate(({"password": "fixture"}, {"data": "-----BEGIN PRIVATE KEY-----"},
                {"data": "https://user:fixture@example.invalid/test"}, {"wire_base64": private_wire},
                {"stderr": "unreviewed failure log"})):
            with self.subTest(index=index):
                (self.cell / "plan.json").write_text(json.dumps(value)); self.pin()
                with self.assertRaises(ValueError):
                    self.pack(output=self.root / f"rejected-{index}")

    def test_changed_verifier_input_is_rejected(self):
        (self.cell / "operations.jsonl").write_text('{"id":1}\n')
        with self.assertRaisesRegex(ValueError, "Bound input changed"):
            self.pack()

    def test_short_rejected_receipt_still_binds_original_driver_raw_hashes(self):
        driver_pins = {"operations.jsonl": archive.sha(self.cell / "operations.jsonl")}
        (self.cell / "summary.json").write_text(json.dumps({"fixture_only": True, "files": driver_pins}))
        self.pin()
        receipt = json.loads(self.receipt.read_text())
        receipt["evidence_sha256"] = {name: value for name, value in receipt["evidence_sha256"].items()
                                     if name in {"summary.json", "plan.json", "result.json"}}
        self.receipt.write_text(json.dumps(receipt))
        (self.cell / "operations.jsonl").write_text('{"id":42}\n')
        with self.assertRaisesRegex(ValueError, "Bound input changed"):
            self.pack()

    def test_missing_ledger_is_rejected(self):
        (self.cell / "operations.jsonl").unlink()
        with self.assertRaises(FileNotFoundError):
            self.pack()

    def test_nonfinalized_cell_is_rejected(self):
        (self.cell / "result.json").write_text('{"complete":false}')
        with self.assertRaisesRegex(ValueError, "not finalized"):
            self.pack()

    def test_symlinked_cell_file_and_external_parent_are_rejected(self):
        (self.cell / "plan.json").unlink()
        (self.cell / "plan.json").symlink_to(self.receipt)
        with self.assertRaisesRegex(ValueError, "symlinks"):
            self.pack()
        (self.cell / "plan.json").unlink(); (self.cell / "plan.json").write_bytes(self.raw["plan.json"])
        alias = self.root / "alias"; alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlinks"):
            self.pack(receipt=alias / self.receipt.name)

    def test_unsafe_verifier_path_and_oversized_scalar_are_rejected(self):
        value = json.loads(self.receipt.read_text()); value["evidence_sha256"]["../outside.json"] = "0" * 64
        self.receipt.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, "Unsafe evidence path"):
            self.pack()
        oversized = self.root / "oversized.json"; oversized.write_text(json.dumps("x" * 65))
        with patch.object(archive, "MAX_VALUE", 64), self.assertRaisesRegex(ValueError, "Oversized JSON scalar"):
            archive.inspect_json(oversized)

    def test_tampered_compressed_bytes_are_rejected(self):
        self.pack()
        manifest = archive.verify(self.bundle); chunk = manifest["files"][0]["chunks"][0]
        target = self.bundle / chunk["path"]; data = target.read_bytes()
        target.write_bytes(bytes([data[0] ^ 1]) + data[1:])
        with self.assertRaisesRegex(ValueError, "Compressed shard changed"):
            archive.verify(self.bundle)

    def test_decompression_bound_even_with_rewritten_metadata(self):
        self.pack()
        path = self.bundle / "manifest.json"; manifest = json.loads(path.read_text())
        chunk = manifest["files"][0]["chunks"][0]; target = self.bundle / chunk["path"]
        compressed = gzip.compress(b"x" * (chunk["raw_bytes"] + 1), mtime=0)
        target.write_bytes(compressed); chunk["gzip_bytes"] = len(compressed)
        chunk["gzip_sha256"] = hashlib.sha256(compressed).hexdigest()
        path.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "exceeds recorded bound"):
            archive.verify(self.bundle)

    def test_restore_does_not_overwrite_or_write_inside_bundle(self):
        self.pack()
        with self.assertRaisesRegex(ValueError, "must be new and outside"):
            archive.verify(self.bundle, self.cell)
        with self.assertRaisesRegex(ValueError, "must be new and outside"):
            archive.verify(self.bundle, self.bundle / "restored")

    def test_database_original_absolute_paths_survive_relocation(self):
        prefix = self.database_fixture()
        self.pack()
        restored = self.root / "relocated"
        manifest = archive.verify(self.bundle, restored)
        selected, _ = archive.select(self.group, restored)
        self.assertEqual(restored / prefix / "receipt.json", selected[prefix + "/receipt.json"])
        self.assertEqual(set(self.raw), set(selected))
        self.assertNotIn("supervision/receipt.json", {item["path"] for item in manifest["files"]})
        for name, value in self.raw.items():
            self.assertEqual(value, (restored / name).read_bytes())

    def test_database_escaping_application_receipt_is_rejected(self):
        self.database_fixture()
        summary = json.loads((self.cell / "summary.json").read_text())
        summary["application_receipt"]["path"] = "/outside/receipt.json"
        (self.cell / "summary.json").write_text(json.dumps(summary)); self.pin()
        with self.assertRaises(ValueError):
            self.pack()

    def test_database_changed_connection_uri_is_rejected(self):
        self.database_fixture()
        for index, uri in enumerate(("postgresql://nativeweave:synthetic-fixture@127.0.0.1:15432/postgres",
                "postgresql://nativeweave@192.0.2.1:15432/postgres", "postgresql://other@127.0.0.1:15432/postgres",
                "postgresql://nativeweave@127.0.0.1:15432/other", "postgresql://nativeweave@127.0.0.1:0/postgres")):
            with self.subTest(index=index):
                (self.cell / "target.json").write_text(json.dumps({"postgres_base": uri})); self.pin()
                with self.assertRaises(ValueError):
                    self.pack(output=self.root / f"uri-rejected-{index}")


if __name__ == "__main__":
    unittest.main()
