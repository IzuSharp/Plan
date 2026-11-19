"""Finite synthetic report fixtures; never start an application or a database.

Prepared during exclusive timing; execute only in a separately permitted window.
Fixture timestamps, latencies and identities are invented test inputs, not data.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("perf01_database_compare", HERE / "database_compare.py")
compare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compare)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


class CompletedDatabaseReports(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.product = Path(os.environ.get("PERF01_NATIVEWEAVE", str(HERE.parents[3].parent / "NativeWeave")))
        self.a21_path = self.product / "src/Benchmarks.Harness/nativeweave_bench.py"
        self.a21 = compare.module(self.a21_path, "perf01_fixture_a21")
        self.cells = {role: [] for role in ("before", "after", "direct")}
        for role_index, role in enumerate(self.cells):
            for repetition in range(3):
                path = self.root / (role + "-" + str(repetition))
                path.mkdir()
                self.cells[role].append(path)
                self.make_cell(path, role, repetition, (20 if role == "before" else 10 if role == "after" else 5) + repetition,
                               1000 + role_index * 10 + repetition)
        self.noise = self.root / "frozen-noise.json"
        frozen = json.loads((self.cells["before"][0] / "frozen-inputs.json").read_text())
        plan = json.loads((self.cells["before"][0] / "plan.json").read_text())
        save(self.noise, {"task": "Perf-01", "created_utc": "2026-01-02T00:00:00+00:00", "provider": "sqlite",
            "rate": 100.0, "concurrency": 16, "processes": [{"directory": str(path), "fixture_only": True} for path in self.cells["before"]],
            "configuration": {"seed": plan["seed"], "dataset_sha256": frozen["dataset_sha256"], "service_standard": frozen["service_standard"],
                "timing": plan["timing"], "settings": plan["settings"], "source_files": frozen["source_files"], "route": frozen["route"]},
            "bands": {key: {"baseline_id": "synthetic-fixture/" + key, "absolute_noise_ns": 2_000_000, "relative_noise": 0}
                      for key in ("mixed", "cycle", "page")},
            "inputs_sha256": {str(path / "summary.json"): compare.sha(path / "summary.json") for path in self.cells["before"]}})

    def tearDown(self):
        self.temp.cleanup()

    def args(self):
        return argparse.Namespace(nativeweave=self.product, **self.cells, managed=None,
                                  noise_receipt=self.noise, noise_sha256=compare.sha(self.noise))

    def make_cell(self, path, role, repetition, latency_ms, pid, failed=False):
        count, origin, period = 200, pid * 100_000_000_000, 10_000_000
        dataset, records = [], []
        for index in range(count):
            kind = "cycle" if index % 2 == 0 else "list"
            item = {"kind": kind, "fixture_only": True}
            expected = {"fixture_id": index, "kind": kind}
            dataset.append({"input": base64.urlsafe_b64encode(json.dumps(item).encode()).decode(), "expected": expected})
            scheduled = origin + index * period
            status = "failed" if failed and index == 0 else "ok"
            records.append({"id": index, "scheduled_ns": scheduled, "dispatch_ns": scheduled + 1000,
                "admission_ns": scheduled + 2000, "completion_ns": scheduled + latency_ms * 1_000_000,
                "target_completion_observed_ns": scheduled + latency_ms * 1_000_000, "attempts": 1,
                "status": status, "value": expected if status == "ok" else {"fixture_error": True}})
        save(path / "dataset.json", dataset)
        timing = {"requests": count, "period_ns": period, "max_dispatch_lag_ns": 100_000_000}
        plan = {"seed": 20261119, "oracle": {"dataset": str(path / "dataset.json"), "sha256": compare.sha(path / "dataset.json")},
                "timing": timing, "settings": {"features": {"scenario": "mixed", "concurrency": 16}, "fixture_only": True}}
        save(path / "plan.json", plan)
        frozen = {"source_files": {str(self.a21_path): compare.sha(self.a21_path)},
                  "route": {"id": compare.ROUTES[role], "source": {"commit": "synthetic-" + role}, "fixture_only": True},
                  "plan_sha256": compare.sha(path / "plan.json"), "dataset_sha256": compare.sha(path / "dataset.json"),
                  "host": {"arch": "x86_64", "background_load": [repetition, 0, 0]}, "python_libraries": {},
                  "affinity": {"mode": "split", "service_cpus": [2, 3], "generator_cpus": [0, 1]},
                  "service_standard": {"max_unexpected_errors": 0, "max_p99_ms": 500, "max_app_rss_mib": 256},
                  "created_utc": "2026-01-03T00:00:00+00:00" if role == "after" else "2026-01-01T00:00:00+00:00"}
        save(path / "frozen-inputs.json", frozen)
        app = path / "applications/synthetic/receipt.json"
        extra = app.with_name("perf01.json")
        save(app, {"fixture_only": True}); save(extra, {"fixture_only": True})
        successes = [row for row in records if row["status"] == "ok"]
        elapsed = records[-1]["completion_ns"] - origin
        outcomes = dict(Counter(row["status"] for row in records))
        observation = {"records": records, "valid": True, "invalid_reasons": [], "route": compare.ROUTES[role],
                       "repetition": repetition, "offered": count, "admitted": count, "completed": count,
                       "successful": len(successes), "outcome_counts": outcomes, "exit_code": 0,
                       "measurement_window_ns": {"start": origin, "end": origin + elapsed, "elapsed": elapsed},
                       "hello": {"application_pid": pid, "fixture_only": True}}
        save(path / "observation.json", observation)
        by_kind = {}
        for key in ("cycle", "list"):
            selected = [row for row in records if (row["id"] % 2 == 0) == (key == "cycle")]
            values = [row["completion_ns"] - row["scheduled_ns"] for row in selected if row["status"] == "ok"]
            by_kind[key] = {"offered": len(selected), "successful": len(values), "outcomes": dict(Counter(row["status"] for row in selected)),
                           **{name: self.a21.percentile(values, q) for name, q in (("p50_ns", .5), ("p95_ns", .95), ("p99_ns", .99))}}
        summary = {"task": "Perf-01", "variant": role, "route": compare.ROUTES[role], "provider": "sqlite", "scenario": "mixed",
                   "rate": 100.0, "concurrency": 16, "valid": not failed, "qualifies_service_standard": not failed,
                   "supervision": "completed", "frozen_inputs_sha256": compare.sha(path / "frozen-inputs.json"),
                   "application_receipt": {"path": str(app), "sha256": compare.sha(app)},
                   "perf01_receipt": {"path": str(extra), "sha256": compare.sha(extra)},
                   "offered": count, "successful": len(successes), "dispatched": count, "outcomes": outcomes,
                   "successful_per_second": len(successes) * 1e9 / elapsed,
                   "p99_ns": self.a21.percentile([row["completion_ns"] - row["scheduled_ns"] for row in successes], .99),
                   "by_kind": by_kind, "invalid_reasons": ["synthetic logical failure"] if failed else [],
                   "resources": {"measurement": {"identities": [{"pid": pid, "start_ticks": pid * 100}],
                       "app_cpu_seconds": .5, "app_cpu_percent_one_core": 25.0, "rss_peak_bytes": 32 * 1024**2,
                       "fd_peak_count": 12, "socket_peak_count": 4, "cpu_span_seconds": 2}},
                   "persisted_before_recovery": {"availability": "measured", "committed_operations_by_phase": {"measurement": 100}},
                   "provider_errors": {"availability": "measured", "sqlite_busy": int(failed), "sqlite_locked": 0},
                   "business_retry_attempts": 0, "durable_oracle": {"passed": True, "fixture_only": True},
                   "closed": {"databaseResourcesReleased": True, "consumerResourcesReleased": True, "serverState": "Disposed"},
                   "loaded_files": {"synthetic": {"sha256": "0" * 64}}, "finished_utc": "2026-01-03T00:01:00+00:00"}
        save(path / "summary.json", summary)
        save(path / "progress.json", {"state": "completed-invalid" if failed else "completed", "summary_sha256": compare.sha(path / "summary.json")})

    def test_raw_cohort_math_slices_and_direct_denominator(self):
        report = compare.extract(self.args())
        row = next(row for row in report["comparisons"] if row["baseline_role"] == "before" and row["scope"] == "whole")
        self.assertEqual(-10_000_000, row["metrics"]["mean_ns"]["absolute"])
        self.assertEqual("improvement", row["noise_on_process_means"]["decision"])
        gap = next(row for row in report["comparisons"] if row["baseline_role"] == "direct" and row["candidate_role"] == "after" and row["scope"] == "whole")
        self.assertAlmostEqual(100 * 5 / 6, gap["metrics"]["mean_ns"]["percent"])
        conditional = next(row for row in report["comparisons"] if row["scope"] == "cycle")
        self.assertIsNone(conditional["resources"]["rss_peak_bytes"]["candidate"])
        self.assertEqual([100, 100, 100], report["cohorts"]["after"]["counts"]["durable_measurement_commits"]["values"])
        self.assertIn("Mean peak RSS", compare.markdown(report))

    def test_failed_process_remains_and_blocks_comparison(self):
        self.make_cell(self.cells["after"][1], "after", 1, 11, 1011, failed=True)
        report = compare.extract(self.args())
        self.assertEqual(3, report["cohorts"]["after"]["process_count"])
        self.assertEqual([0, 1, 0], report["cohorts"]["after"]["scopes"]["whole"]["errors"]["values"])
        row = next(row for row in report["comparisons"] if row["baseline_role"] == "before" and row["scope"] == "whole")
        self.assertEqual("inconclusive", row["noise_on_process_means"]["decision"])

    def test_changed_before_source_band_is_descriptive_only(self):
        noise = json.loads(self.noise.read_text())
        noise["configuration"]["source_files"][str(self.a21_path)] = "0" * 64
        save(self.noise, noise)
        report = compare.extract(self.args())
        self.assertTrue(all(row["noise_on_process_means"]["decision"] == "inconclusive" for row in report["comparisons"]))
        self.assertIsNotNone(report["comparisons"][0]["metrics"]["mean_ns"]["absolute"])

    def test_zero_denominator_and_repeated_process_are_not_hidden(self):
        self.assertIsNone(compare.change(0, 1)["percent"])
        args = self.args()
        args.after = [self.cells["after"][0], self.cells["after"][0]]
        with self.assertRaisesRegex(ValueError, "repeated"):
            compare.extract(args)

    def test_two_processes_are_descriptive_and_paths_are_not_identities(self):
        args = self.args()
        args.after = args.after[:2]
        report = compare.extract(args)
        row = next(row for row in report["comparisons"] if row["baseline_role"] == "before" and row["scope"] == "whole")
        self.assertFalse(row["eligible"])
        self.assertEqual("inconclusive", row["noise_on_process_means"]["decision"])
        self.assertEqual(compare.logical_hashes({"/one/NativeWeave/tests/Perf01.Database/run.py": "a"}),
                         compare.logical_hashes({"/two/NativeWeave/tests/Perf01.Database/run.py": "a"}))

    def test_changed_raw_oracle_is_rejected(self):
        path = self.cells["after"][0] / "observation.json"
        raw = json.loads(path.read_text()); raw["records"][0]["value"] = {"fixture_wrong": True}; save(path, raw)
        with self.assertRaisesRegex(ValueError, "raw result"):
            compare.extract(self.args())

    def test_compact_mode_is_explicit_and_cannot_disagree_with_frozen_inputs(self):
        path = self.cells["before"][0]
        summary = json.loads((path / "summary.json").read_text())
        frozen = json.loads((path / "frozen-inputs.json").read_text())
        plan = json.loads((path / "plan.json").read_text())
        self.assertFalse(compare.signature(summary, frozen, plan)["compact_observation"])
        plan["settings"]["features"]["compact_observation"] = True
        with self.assertRaisesRegex(ValueError, "Compact-observation identity"):
            compare.signature(summary, frozen, plan)
        frozen["compact_observation"] = True
        self.assertTrue(compare.signature(summary, frozen, plan)["compact_observation"])
        plan["settings"]["features"]["compact_observation"] = 1
        with self.assertRaisesRegex(ValueError, "Compact-observation identity"):
            compare.signature(summary, frozen, plan)


if __name__ == "__main__":
    unittest.main()
