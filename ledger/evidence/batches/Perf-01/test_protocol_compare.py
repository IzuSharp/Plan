"""Finite synthetic extractor fixtures; never run a protocol server or client.

All timestamps, counters, identities and latency values are invented test inputs
inside a temporary directory. They are never Perf-01 measurement evidence.
"""
from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("perf01_protocol_comparison", HERE / "protocol_compare.py")
compare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compare)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))


class ProtocolComparisonFixtures(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.product = Path(os.environ.get("PERF01_NATIVEWEAVE", str(HERE.parents[3].parent / "NativeWeave")))
        a21_path = self.product / "src/Benchmarks.Harness/nativeweave_bench.py"
        reader_path = self.product / "tests/Perf01/verify_long.py"
        self.a21, self.reader = compare.module("protocol_fixture_a21", a21_path), compare.module("protocol_fixture_reader", reader_path)
        self.a21_hash, self.reader_hash = compare.sha(a21_path), compare.sha(reader_path)
        self.builds = {variant: self.build(variant) for variant in ("before", "after", "direct")}
        self.tokens = ["http-download|http1-tls|1048576|1", "http-download|http1-tls|8388608|1",
                       "http-tiny|http2-tls|0|1", "http-cancel|http2-tls|8388608|1"]

    def tearDown(self):
        self.temp.cleanup()

    def build(self, variant):
        directory = self.root / "builds" / variant
        path = directory / "build.json"
        executable = str(directory / "synthetic-executable")
        native_path = str(directory / "libnativeweave_server.so")
        native_hash = ("1" if variant == "before" else "2") * 64
        toolchain = {"sdk": "11.0.100", "dotnet_sha256": "3" * 64, "configuration": "Release", "aot": True, "isa": "x86-64-v2"}
        value = {"fixture_only": True, "eligible_for_measurement": True, "server": executable, "toolchain": toolchain,
                 "artifacts_sha256": {executable: ("4" if variant == "before" else "5") * 64},
                 "driver_source_commit": "synthetic-driver-not-product-evidence", "driver_source_sha256": {"fixture.rs": "6" * 64},
                 "lock_hashes": {"synthetic/Cargo.lock": "7" * 64}, "producer_manifests_sha256": {}}
        if variant == "direct":
            value.update(route="direct-rust", toolchain={"rustc": "synthetic pinned Rust\n", "configuration": "Release", "isa": "x86-64-default"})
        else:
            source = compare.BASELINE if variant == "before" else "a" * 40
            producer_path = directory / "native/manifest.json"
            producer = {"sourceCommit": source, "sourceDirty": False, "rid": "linux-x64", "target": "x86_64-unknown-linux-gnu", "profile": "release",
                        "cargoLockSha256": "7" * 64, "inputSha256": {"Cargo.toml": "8" * 64, "Cargo.lock": "7" * 64},
                        "tools": {"rustc": {"version": "synthetic pinned Rust", "sha256": "9" * 64}},
                        "environment": {"RUSTFLAGS": "", "CARGO_ENCODED_RUSTFLAGS": "", "CARGO_BUILD_JOBS": "3"},
                        "builds": [{"label": "synthetic", "defaultFeatures": False, "features": []}],
                        "assets": [{"engineId": "server", "sha256": native_hash}]}
            save(producer_path, producer)
            value.update(product_source_commit=source, product_source_dirty=False, nativeweave_package_version="0.1.0-synthetic." + variant,
                         producer_manifests_sha256={str(producer_path): compare.sha(producer_path)},
                         package_archives_sha256={str(directory / ("NativeWeave.Server.0.1.0-synthetic." + variant + ".nupkg")): "b" * 64})
        save(path, value)
        return {"path": path, "value": value, "native": {} if variant == "direct" else {native_path: native_hash}}

    def cell(self, variant, serial, latency_ms=20, calibration=False):
        root = self.root / ("cell-" + str(serial))
        build = self.builds[variant]
        count, period, origin = 400, 10_000_000, serial * 60_000_000_000
        profile = {"formal_timing_eligible": True, "fixture_only": True}
        save(root / "profile.json", profile)
        oracle = [{"input": self.tokens[index % 4], "expected": self.tokens[index % 4]} for index in range(count)]
        save(root / "oracle.json", oracle)
        records, operations = [], []
        for index, entry in enumerate(oracle):
            name, protocol, size, _ = entry["input"].split("|")
            scheduled = origin + index * period
            records.append({"id": index, "scheduled_ns": scheduled, "dispatch_ns": scheduled + 1000,
                            "admission_ns": scheduled + 2000, "completion_ns": scheduled + latency_ms * 1_000_000,
                            "target_completion_observed_ns": scheduled + latency_ms * 1_000_000, "status": "ok", "value": entry["input"]})
            probe = name == "http-cancel"
            operations.append({"id": index, "scenario": name, "protocol": protocol, "logical_status": "ok", "wire_status": "ExpectedCanceledUpload" if probe else "HTTP200",
                "correctness_failure": False, "intentional_cancellation": probe, "intentional_deadline": False,
                "request_messages": 1, "response_messages": 0 if probe else 1, "request_payload_bytes": 32768 if probe else 0,
                "response_payload_bytes": 0 if probe else 16 if name == "http-tiny" else int(size), "request_encoded_bytes": 0, "response_encoded_bytes": 0})
        jsonl(root / "requests.jsonl", records)
        jsonl(root / "execution/client/operations.jsonl", operations)
        jsonl(root / "execution/process-resources.jsonl", [{"fixture_only": True}])
        if variant != "direct":
            snapshots = [{"phase": "measurement", "timestamp": origin + index * 1_000_000_000, "timestamp_frequency": 1_000_000_000,
                          "managed_allocated_bytes": index * 1048576} for index in (1, 3)]
            jsonl(root / "execution/server/managed-resources.jsonl", snapshots)
        artifacts = {"/synthetic/" + name: self.a21_hash if name == compare.DRIVERS[3] else "c" * 64 for name in compare.DRIVERS}
        artifacts.update({str(build["path"]): compare.sha(build["path"]), build["value"]["server"]: build["value"]["artifacts_sha256"][build["value"]["server"]]})
        adapter = {"server": build["value"]["server"], "native_sha256": build["native"]}
        save(root / "adapter.json", adapter)
        schedule = {"group": "http", "rate": 100, "period_ns": period, "duration_seconds": 4, "concurrency": 4,
                    "client_executable_sha256": "d" * 64, "profile_sha256": compare.sha(root / "profile.json"), "oracle_sha256": compare.sha(root / "oracle.json"),
                    "service_cpus": [2, 3], "generator_cpus": [0, 1], "application_sources_sha256": {"fixture.cs": "e" * 64}}
        plan = {"route": "direct-rust" if variant == "direct" else "nativeweave-aot-rust", "schedule": schedule,
                "comparison_identity_sha256": compare.canonical(schedule), "build_manifest": str(build["path"]), "artifacts": artifacts,
                "manifest_sha256": compare.sha(root / "adapter.json"), "profile_sha256": compare.sha(root / "profile.json"), "oracle": {"sha256": compare.sha(root / "oracle.json")},
                "timing": {"requests": count, "period_ns": period, "timeout_ns": 25_000_000_000, "max_dispatch_lag_ns": 100_000_000},
                "settings": {"warmup_requests": 24, "recovery_requests": 32}, "histogram": {"resolution_ns": 1000, "maximum_ns": 60_000_000_000},
                "service_standard": {"arrival_p99_maximum_ms": 500, "whole_process_rss_bytes_maximum": 256 * 1024**2, "unexpected_error_rate_maximum": 0}}
        save(root / "plan.json", plan)
        pid = 1000 + serial
        receipt = {"status": "passed", "errors": [], "server_pid": pid, "client_pid": pid + 1000, "client_hello": {"dynamic_code_supported": False},
                   "loaded_native_sha256": build["native"], "affinity": {"ready": {"server": {"pid": pid, "start_ticks": 10000 + serial}}}}
        save(root / "execution/receipt.json", receipt)
        elapsed = records[-1]["completion_ns"] - origin
        start = datetime(2026, 1, 1 if calibration else 3, tzinfo=timezone.utc) + timedelta(seconds=serial * 60)
        result = {"status": "completed", "valid": True, "service_standard_met": True, "idle_owner_and_request_gauges_receded": True, "exit_code": 0,
                  "plan_sha256": compare.sha(root / "plan.json"), "comparison_identity_sha256": plan["comparison_identity_sha256"], "invalid_reasons": [],
                  "controller_pid": pid + 2000, "offered": count, "actually_dispatched": count, "successful": count, "recovery": {"status": "passed"},
                  "host": {"os": "Linux", "arch": "x86_64", "fixture_only": True},
                  "measurement_window": {"start_monotonic_ns": origin, "end_monotonic_ns": origin + elapsed, "elapsed_ns": elapsed,
                                         "start_utc": start.isoformat(), "end_utc": (start + timedelta(seconds=elapsed / 1e9)).isoformat()},
                  "resources": {"server": {"cpu_seconds": .5, "cpu_percent_one_core": 25.0, "rss_bytes_maximum": 32 * 1024**2}},
                  "managed_gc": None if variant == "direct" else {"managed_allocated_bytes_delta": 2 * 1048576, "gen0_delta": 1, "gen1_delta": 0, "gen2_delta": 0}}
        result["evidence_sha256"] = {str(path.relative_to(root)): compare.sha(path) for path in root.rglob("*") if path.is_file()}
        save(root / "result.json", result)
        return root

    def read(self, path, variant):
        return compare.read_cell(path, variant, self.a21, self.reader, self.a21_hash)

    def cohorts(self):
        calibration = [self.read(self.cell("before", index, 20 + index, True), "before") for index in range(3)]
        direct = compare.direct_reference(self.builds["direct"]["path"], compare.sha(self.builds["direct"]["path"]))
        noise = compare.freeze(calibration, self.a21_hash, self.reader_hash, direct)
        noise["created_utc"] = "2026-01-02T00:00:00+00:00"  # Synthetic chronology, not a saved real freeze.
        cohorts = {name: [] for name in ("before", "after", "direct")}
        for repetition in range(3):
            for offset, variant in enumerate(cohorts):
                serial = 10 + repetition * 3 + offset
                latency = {"before": 20, "after": 10, "direct": 5}[variant] + repetition
                cohorts[variant].append(self.read(self.cell(variant, serial, latency), variant))
        return cohorts, noise

    def test_actual_schema_sizes_probe_bytes_and_gc_bracket(self):
        cell = self.read(self.cell("before", 50), "before")
        self.assertTrue(cell["eligible"], cell["issues"])
        self.assertEqual(4, len(cell["scenarios"]))
        small, large = [cell["scenarios"][token] for token in self.tokens[:2]]
        self.assertEqual(100 * 1048576, small["successful_totals"]["response_payload_bytes"])
        self.assertEqual(100 * 8388608, large["successful_totals"]["response_payload_bytes"])
        probe = cell["scenarios"][self.tokens[3]]
        self.assertEqual(100 * 32768, probe["raw_observed_totals"]["request_payload_bytes"])
        self.assertEqual(0, probe["successful_calls"])
        self.assertEqual(1, cell["resources"]["managed_gc_observation"]["allocated_mib_per_second"])

    def test_fixed_band_fresh_triplets_and_direct_denominator(self):
        cohorts, noise = self.cohorts()
        report = compare.compare(cohorts, noise, self.a21, self.a21_hash, self.reader_hash)
        self.assertTrue(report["comparative_interpretation_eligible"], report["issues"])
        row = report["ordinary_scenarios"][self.tokens[0]]
        self.assertEqual(-10_000_000, row["changes"]["arrival_mean_ns"]["after_minus_before"]["absolute"])
        self.assertAlmostEqual(100 * 5 / 6, row["changes"]["arrival_mean_ns"]["after_minus_direct"]["percent"])
        self.assertEqual("improvement", row["noise"]["decision"])
        self.assertIsNone(report["whole_profile_resources"]["metrics"]["server_gen0_delta"]["routes"]["direct"]["mean"])
        self.assertIn("Mean process p50", compare.markdown(report))

    def test_failed_process_is_retained_and_never_averaged_away(self):
        cohorts, noise = self.cohorts()
        cohorts["after"][1]["eligible"] = False
        cohorts["after"][1]["issues"] = ["synthetic correctness failure"]
        report = compare.compare(cohorts, noise, self.a21, self.a21_hash, self.reader_hash)
        self.assertFalse(report["comparative_interpretation_eligible"])
        self.assertEqual(3, len(report["cohorts"]["after"]))
        self.assertTrue(all(row["noise"]["decision"] == "inconclusive" for row in report["ordinary_scenarios"].values()))
        self.assertIsNone(compare.aggregate([1, None, 3])["mean"])

    def test_changed_clock_bytes_parser_and_calibration_reuse_are_rejected(self):
        cohorts, noise = self.cohorts()
        with self.assertRaisesRegex(ValueError, "parser"):
            compare.compare(cohorts, noise, self.a21, self.a21_hash, "0" * 64)
        changed = copy.deepcopy(cohorts)
        changed["before"] = copy.deepcopy(noise["before_processes"])
        self.assertFalse(compare.compare(changed, noise, self.a21, self.a21_hash, self.reader_hash)["comparative_interpretation_eligible"])
        changed = copy.deepcopy(cohorts)
        changed["after"][0]["build"]["toolchain_contract"]["managed_aot"]["sdk"] = "different"
        self.assertFalse(compare.compare(changed, noise, self.a21, self.a21_hash, self.reader_hash)["comparative_interpretation_eligible"])
        path = self.cell("before", 60)
        records = [json.loads(line) for line in (path / "requests.jsonl").read_text().splitlines()]
        records[0]["target_completion_observed_ns"] += 1
        jsonl(path / "requests.jsonl", records)
        result = json.loads((path / "result.json").read_text())
        result["evidence_sha256"]["requests.jsonl"] = compare.sha(path / "requests.jsonl")
        save(path / "result.json", result)
        self.assertFalse(self.read(path, "before")["eligible"])

    def test_zero_denominator_and_invalid_cardinality_are_explicit(self):
        self.assertIsNone(compare.delta(0, 1)["percent"])
        item = compare.scene("grpc-client|http2-tls|4096|32")
        row = dict(zip(compare.TOTALS, (32, 1, 131072, 0, 131200, 75)))
        compare.require_wire_counts(item, row)
        row["response_messages"] = 2
        with self.assertRaisesRegex(ValueError, "counts"):
            compare.require_wire_counts(item, row)


if __name__ == "__main__":
    unittest.main()
