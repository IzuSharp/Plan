"""Small synthetic arithmetic/identity tests; no codec, database or load runs."""
from array import array
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("codec_comparison", HERE / "codec_compare.py")
comparison = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(comparison)
A21 = comparison.a21_module(Path(__file__).resolve().parents[4].parent / "NativeWeave/src/Benchmarks.Harness/nativeweave_bench.py")


class CodecComparisonChecks(unittest.TestCase):
    def test_contract_allows_product_changes_but_not_fixture_or_load_changes(self):
        plan = {name: "fixed-fixture" for name in comparison.PLAN_KEYS}
        plan.update(source_commit="before", manifest_sha256="old", actual_loaded_native=["old"],
                    host={"os": "Linux", "background_load": [1, 2, 3]},
                    affinity_policy={"mode": "split", "target_cpus": [2, 3], "generator_cpus": [0, 1]})
        build = {name: "fixed-build" for name in ("driver_sha256", "a21_sha256", "toolchain", "build_environment", "product_locks")}
        build["source_commit"] = "before"
        changed, rebuilt = copy.deepcopy(plan), copy.deepcopy(build)
        changed.update(source_commit="after", manifest_sha256="new", actual_loaded_native=["new"])
        changed["host"]["background_load"] = [3, 2, 1]; rebuilt["source_commit"] = "after"
        self.assertEqual(comparison.contract(plan, build), comparison.contract(changed, rebuilt))
        rebuilt["driver_sha256"] = "changed-fixture"
        self.assertNotEqual(comparison.contract(plan, build), comparison.contract(changed, rebuilt))
        changed["planned_rate"] = "changed-load"
        self.assertNotEqual(comparison.contract(plan, build), comparison.contract(changed, build))

    def test_wall_and_summed_call_throughput_remain_distinct(self):
        item = comparison.group(); item.update(count=2, raw=2 * 1048576, encoded=1048576)
        for key in comparison.METRICS: item["latency"][key] = array("Q", [2_000_000, 4_000_000])
        item["known"]["managed_allocated_bytes"] = False
        value = comparison.metrics(item, 2, A21)
        self.assertEqual(1, value["raw_mib_per_second_wall"])
        self.assertAlmostEqual(2 / .006, value["raw_mib_per_second_summed_call"])
        self.assertEqual(2, value["raw_over_encoded_ratio"])
        self.assertEqual(3_000_000, value["latency"]["call_ns"]["mean_ns"])
        self.assertIsNone(value["latency"]["call_ns"]["p99"])
        self.assertIsNone(value["counter_per_success"]["managed_allocated_bytes"])

    def test_mixed_population_requires_each_process_and_rare_row(self):
        groups = {comparison.group_key(case, action, interface): {"count": (10, 5, 4, 1)[case // 2] * 100}
                  for case in range(8) for action in "cd" for interface in "ao"}
        comparison.require_population(groups, 16_000)
        bad = copy.deepcopy(groups); bad["c/a/case-0"]["count"] -= 1
        with self.assertRaisesRegex(ValueError, "16000"):
            comparison.require_population(bad, 15_999)
        bad = copy.deepcopy(groups); bad["c/a/case-6"]["count"] -= 1; bad["c/a/case-0"]["count"] += 1
        with self.assertRaisesRegex(ValueError, "100 successes"):
            comparison.require_population(bad, 16_000)
        bad = copy.deepcopy(groups); del bad["d/o/case-7"]
        with self.assertRaisesRegex(ValueError, "Missing real"):
            comparison.require_population(bad, 16_000)

    def test_before_range_and_declared_floor(self):
        cells = [{"groups": {"fixture": {"latency": {key: {"mean_ns": mean} for key in comparison.NOISE_METRICS}}}}
                 for mean in (100, 140, 80)]
        self.assertEqual(100, comparison.noise_bands(cells, 100)["fixture"]["call_ns"]["absolute_noise_ns"])
        self.assertEqual(60, comparison.noise_bands(cells, 10)["fixture"]["arrival_ns"]["absolute_noise_ns"])
        self.assertEqual(0, comparison.noise_bands(cells, 10)["fixture"]["operation_ns"]["relative_noise"])

    def test_independent_process_and_window_guards(self):
        cells = [{"process_identity": [index, index * 100], "summary_sha256": str(index), "window_ns": [index * 10, index * 10 + 10]}
                 for index in (1, 2, 3)]
        comparison.independent(cells)
        bad = copy.deepcopy(cells); bad[2]["process_identity"] = bad[0]["process_identity"]
        with self.assertRaisesRegex(ValueError, "Repeated process"):
            comparison.independent(bad)
        bad = copy.deepcopy(cells); bad[2]["window_ns"] = [29, 40]
        with self.assertRaisesRegex(ValueError, "overlap"):
            comparison.independent(bad)

    def test_unknown_and_zero_denominator_are_not_fabricated_percentages(self):
        self.assertIsNone(comparison.change(None, 1)["absolute"])
        self.assertIsNone(comparison.change(0, 1)["percent"])
        self.assertEqual({"absolute": -25, "percent": -25}, comparison.change(100, 75))

    def test_resources_use_only_their_measured_snapshot_window(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); path = root / "resources.jsonl"
            rows = []
            for index, rss in enumerate((900, 100, 200, 150, 1000)):
                value = {"rss_bytes": {"value": rss}, "cpu_seconds": index}
                rows.append({"observer_ns": index * 1_000_000_000, "target": value, "generator": value})
            path.write_text("".join(json.dumps(row) + "\n" for row in rows))
            summary = {"target_cpu_seconds": 2, "target_cpu_percent_one_core": 100, "rss_before_bytes": 100, "rss_after_bytes": 150}
            value = comparison.resources(root, {"resources.jsonl": comparison.sha(path)}, 1_000_000_000, 3_000_000_000, summary)
            self.assertEqual(200, value["target"]["rss_sample_peak_bytes"])
            self.assertEqual(1500, value["target"]["rss_endpoint_change_bytes_per_minute"])
            self.assertEqual(100, value["generator"]["cpu_percent_one_core_snapshot_interval"])
            self.assertEqual([1_000_000_000, 3_000_000_000], value["generator"]["cpu_snapshot_interval_ns"])
            rows[2]["target"]["cpu_seconds"] = float("nan")
            path.write_text("".join(json.dumps(row) + "\n" for row in rows))
            with self.assertRaisesRegex(ValueError, "Invalid CPU scalar"):
                comparison.resources(root, {"resources.jsonl": comparison.sha(path)}, 1_000_000_000, 3_000_000_000, summary)


if __name__ == "__main__":
    unittest.main()
