#!/usr/bin/env python3
"""Extract completed Perf-01 DB cohorts; never build, run, or rewrite a cell.

Use outside measurement windows. Source preparation is not an execution claim.
All explicitly supplied processes remain in the report, including failed cells.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import statistics

ROUTES = {"before": "nativeweave-aot-rust", "after": "nativeweave-aot-rust",
          "direct": "direct-rust", "managed": "managed-aot"}
LATENCY = ("mean_ns", "median_ns", "p50_ns", "p95_ns", "p99_ns")
RESOURCE = ("app_cpu_seconds", "app_cpu_percent_one_core", "rss_peak_bytes", "fd_peak_count", "socket_peak_count")
MAX_PROCESSES = 32


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value):
    return type(value) in (int, float) and math.isfinite(value)


def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def stamp(path):
    value = path.stat()
    return value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns


def logical_hashes(files):
    """Keep logical names/content and multiplicity, independent of checkout roots."""
    rows = []
    for name, digest in files.items():
        path = Path(name)
        marker = next((part for part in ("src", "tests") if part in path.parts), None)
        logical = "/".join(path.parts[path.parts.index(marker):]) if marker else (
            path.parent.name + "/" + path.name if path.name == "__init__.py" else path.name)
        rows.append((logical, digest))
    return sorted(rows)


def route_signature(route):
    source = route.get("source", {})
    return {"id": route["id"], "artifacts": logical_hashes(route.get("artifacts", {})),
            "lock_hashes": logical_hashes(route.get("lock_hashes", {})),
            "executable_sha256": route.get("artifacts", {}).get(route.get("command", [None])[0]),
            "command_arguments": route.get("command", [])[1:], "environment": route.get("environment", {}),
            "source_commit": source.get("commit", source.get("base_commit")), "source_scope_status": source.get("scope_status"),
            "source_files": logical_hashes(source.get("files", {})),
            "toolchain": {key: value for key, value in route.get("toolchain", {}).items() if key != "isolated_nuget_cache"},
            "native": sorted((Path(name).name, value["sha256"]) for name, value in route.get("native", {}).items()),
            "supported": route.get("supported"), "transport": route.get("transport"), "query_route": route.get("query_route"),
            "instrumented": route.get("instrumented"), "exception_observer": route.get("perf01_exception_observer", False)}


def utc(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(result.tzinfo is not None, "Naive evidence timestamp")
    return result


def metric(values, a21):
    return {"successful": len(values), "sum_arrival_ns": sum(values),
            "mean_ns": statistics.mean(values) if values else None,
            "median_ns": statistics.median(values) if values else None,
            **{name: a21.percentile(values, quantile) for name, quantile in (("p50_ns", .5), ("p95_ns", .95), ("p99_ns", .99))}}


def signature(summary, frozen, plan):
    compact = plan["settings"].get("features", {}).get("compact_observation", False)
    require(type(compact) is bool and type(frozen.get("compact_observation", False)) is bool
            and compact == frozen.get("compact_observation", False), "Compact-observation identity differs between plan and freeze")
    return {"provider": summary["provider"], "scenario": summary["scenario"], "rate": summary["rate"],
            "compact_observation": compact,
            "concurrency": summary["concurrency"], "seed": plan["seed"], "dataset_sha256": frozen["dataset_sha256"],
            "timing": plan["timing"], "settings": plan["settings"], "service_standard": frozen["service_standard"],
            "host": {key: value for key, value in frozen["host"].items() if key != "background_load"},
            "python_libraries": frozen["python_libraries"],
            "affinity": {key: frozen["affinity"].get(key) for key in ("mode", "service_cpus", "generator_cpus")}}


def read_cell(path, role, a21, reader, a21_sha):
    evidence = reader.Evidence(path)
    summary = evidence.load("summary.json")
    require(summary["task"] == "Perf-01" and summary["variant"] == role and summary["route"] == ROUTES[role],
            "Cell role/route differs from its explicit cohort")
    require(summary["provider"] in ("sqlite", "postgresql") and summary["scenario"] in ("cycle", "page", "mixed"), "Unknown DB workload")
    progress = evidence.load("progress.json")
    require(progress["state"] in ("completed", "completed-invalid") and progress["summary_sha256"] == evidence.files["summary.json"],
            "Cell is incomplete or summary identity differs")
    frozen = evidence.load("frozen-inputs.json", summary["frozen_inputs_sha256"])
    plan = evidence.load("plan.json", frozen["plan_sha256"])
    a21_pins = [value for name, value in frozen["source_files"].items() if name.endswith("/src/Benchmarks.Harness/nativeweave_bench.py")]
    require(a21_pins == [a21_sha], "Requested A21 source differs from the actual frozen driver")
    data = evidence.pin(evidence.root / "dataset.json", frozen["dataset_sha256"])
    require(plan["oracle"]["sha256"] == frozen["dataset_sha256"], "Dataset identity differs between plan and freeze")
    for marker in ("profile-driver.json", "postgres-profile-summary.json", "profiling.json"):
        if (evidence.root / marker).exists():
            evidence.load(marker)
    # Preserve the existing package/durable/drain verdict, and bind its original
    # receipts. This extractor does not replay network or persistence oracles.
    original_root = Path(plan["oracle"]["dataset"]).parent
    app_path = evidence.local(summary["application_receipt"]["path"], original_root)
    extra_path = evidence.local(summary["perf01_receipt"]["path"], original_root)
    evidence.pin(app_path, summary["application_receipt"]["sha256"])
    evidence.pin(extra_path, summary["perf01_receipt"]["sha256"])
    expected = plan["timing"]["requests"]
    require(type(expected) is int and 0 < expected <= reader.MAX_RECORDS, "Invalid finite request count")
    metadata = dict.fromkeys(("valid", "invalid_reasons", "route", "repetition", "offered", "admitted", "completed",
                              "successful", "outcome_counts", "exit_code", "measurement_window_ns", "hello"))
    kinds = ("whole", "cycle", "page") if summary["scenario"] == "mixed" else ("whole",)
    latencies, outcomes = {key: [] for key in kinds}, {key: Counter() for key in kinds}
    dispatched = attempts = max_lag = count = 0
    origin = None
    observation = evidence.pin(evidence.root / "observation.json")
    for index, (row, entry) in enumerate(zip(reader.array_records(observation, "records", metadata),
                                           reader.array_records(data), strict=True)):
        require(index < expected and row["id"] == index and row["status"] in a21.OUTCOMES, "Unknown/missing ordered A21 operation")
        scheduled = row["scheduled_ns"]
        require(type(scheduled) is int and scheduled >= 0, "Missing scheduled timestamp")
        origin = scheduled if origin is None else origin
        require(scheduled == origin + index * plan["timing"]["period_ns"], "Scheduled arrival sequence changed")
        item = json.loads(base64.b64decode(entry["input"], altchars=b"-_", validate=True))
        require(item["kind"] in ("cycle", "list"), "Unknown frozen DB operation")
        kind = "cycle" if item["kind"] == "cycle" else "page"
        require(summary["scenario"] in ("mixed", kind), "Dataset differs from the declared scenario")
        keys = ("whole", kind) if summary["scenario"] == "mixed" else ("whole",)
        for key in keys:
            outcomes[key][row["status"]] += 1
        if row["dispatch_ns"] is not None:
            require(type(row["dispatch_ns"]) is int and row["dispatch_ns"] >= scheduled, "Invalid dispatch timestamp")
            dispatched += 1
            max_lag = max(max_lag, row["dispatch_ns"] - scheduled)
        require(type(row["attempts"]) is int and row["attempts"] >= 0, "Invalid dispatch-attempt count")
        attempts += row["attempts"]
        if row["status"] == "ok":
            require(all(type(row[name]) is int for name in ("dispatch_ns", "admission_ns", "completion_ns")) and
                    scheduled <= row["dispatch_ns"] <= row["admission_ns"] <= row["completion_ns"], "Successful timestamp order differs")
            require(row["value"] == entry["expected"] and row["completion_ns"] == row["target_completion_observed_ns"],
                    "Successful raw result or controller completion identity differs")
            for key in keys:
                latencies[key].append(row["completion_ns"] - scheduled)
        count += 1
    require(count == expected == metadata["offered"] == summary["offered"] and metadata["route"] == summary["route"], "Raw offered count/route differs")
    require(dict(outcomes["whole"]) == metadata["outcome_counts"] == summary["outcomes"], "Outcome counts differ")
    require(len(latencies["whole"]) == metadata["successful"] == summary["successful"] and dispatched == summary["dispatched"], "Raw success/dispatch counts differ")
    window = metadata["measurement_window_ns"]
    elapsed = window["elapsed"]
    require(type(elapsed) is int and elapsed > 0 and window["start"] == origin and window["end"] - origin == elapsed, "Invalid A21 observation window")
    scopes = {}
    for key in kinds:
        value = metric(latencies[key], a21)
        value.update(offered=sum(outcomes[key].values()), errors=sum(n for status, n in outcomes[key].items() if status != "ok"),
                     outcomes=dict(outcomes[key]), successful_per_second=len(latencies[key]) * 1e9 / elapsed,
                     scope="Whole application load" if key == "whole" else "Conditional successful operations inside the same mixed load; no separate resource attribution")
        scopes[key] = value
    require(scopes["whole"]["p99_ns"] == summary["p99_ns"], "Raw p99 differs from summary")
    require(math.isclose(scopes["whole"]["successful_per_second"], summary["successful_per_second"], rel_tol=1e-12), "Raw success rate differs from summary")
    for key in ("cycle", "page") if summary["scenario"] == "mixed" else ():
        old = summary["by_kind"]["list" if key == "page" else key]
        require(all(scopes[key][field] == old[field] for field in ("offered", "successful", "p50_ns", "p95_ns", "p99_ns", "outcomes")),
                "Raw conditional metrics differ from summary")
    phase = summary["resources"].get("measurement", {})
    instances = {(row["pid"], row["start_ticks"]) for row in phase.get("identities", [])
                 if type(row.get("start_ticks")) is int and row["pid"] == metadata["hello"]["application_pid"]}
    require(len(instances) == 1, "Cannot establish one application PID/start identity for this process cell")
    pid, start_ticks = next(iter(instances))
    resources = {key: phase.get(key) for key in RESOURCE}
    require(all(value is None or finite(value) and value >= 0 for value in resources.values()), "Invalid measured resource value")
    resources.update(cpu_span_seconds=phase.get("cpu_span_seconds"), cpu_unavailable_reason=phase.get("cpu_unavailable_reason"),
                     error_samples=phase.get("error_samples"), scope="Whole application measurement phase; CPU percent is relative to one core",
                     postgresql_service_cpu_seconds=None, postgresql_service_rss_bytes=None,
                     database_service_resource_reason="PostgreSQL service not sampled; SQLite executes inside the application process")
    persisted = summary.get("persisted_before_recovery") or {}
    commits = persisted.get("committed_operations_by_phase", {}).get("measurement", 0) if persisted.get("availability") == "measured" else None
    errors = summary.get("provider_errors") or {}
    closed = summary.get("closed") or {}
    eligible = (summary["valid"] is True and summary["qualifies_service_standard"] is True and metadata["valid"] is True
                and not metadata["invalid_reasons"] and metadata["exit_code"] == 0 and summary["supervision"] == "completed"
                and scopes["whole"]["errors"] == 0 and dispatched == expected and max_lag <= plan["timing"]["max_dispatch_lag_ns"]
                and (summary.get("durable_oracle") or {}).get("passed") is True and closed.get("databaseResourcesReleased") is True
                and closed.get("consumerResourcesReleased") is True
                and closed.get("serverState") == ("Disposed" if role in ("before", "after") else "Stopped"))
    evidence.unchanged()
    return {"directory": str(evidence.root), "role": role, "repetition": metadata["repetition"], "eligible": eligible,
            "recorded_valid": summary["valid"], "service_standard_met": summary["qualifies_service_standard"],
            "invalid_reasons": summary.get("invalid_reasons", []), "raw_invalid_reasons": metadata["invalid_reasons"],
            "configuration": signature(summary, frozen, plan), "driver_source_files": frozen["source_files"],
            "route_identity": frozen["route"], "loaded_files": summary["loaded_files"],
            "created_utc": frozen["created_utc"], "finished_utc": summary["finished_utc"],
            "application_identity": metadata["hello"], "observation_seconds": elapsed / 1e9,
            "application_instance": {"pid": pid, "start_ticks": start_ticks},
            "measurement_window_ns": window,
            "dispatch_attempts": attempts, "dispatched": dispatched, "maximum_dispatch_lag_ns": max_lag,
            "scopes": scopes, "resources": resources, "generator_resources": summary.get("generator_resources"),
            "durable_measurement_commits": commits, "durable_oracle": summary.get("durable_oracle"),
            "provider_errors": errors, "sqlite_busy": errors.get("sqlite_busy") if errors.get("availability") == "measured" else None,
            "sqlite_locked": errors.get("sqlite_locked") if errors.get("availability") == "measured" else None,
            "business_retry_attempts": summary.get("business_retry_attempts"), "sqlite_internal_busy_retry_attempts": None,
            "retry_scope": "Explicit benchmark business retries across the run; same-key replay is a declared operation. Internal SQLite busy-handler attempts are unobserved.",
            "provider_error_scope": "Catch/log/rethrow counts cover the complete application lifetime, including seed/warmup/recovery; not a measurement-only BUSY count",
            "classified_error_counts": summary.get("classified_error_counts"), "evidence_sha256": evidence.files}


def aggregate(values):
    if not values or any(value is None for value in values):
        return {"mean": None, "minimum": None, "maximum": None, "values": values, "availability": "incomplete"}
    require(all(finite(value) for value in values), "Nonfinite process metric")
    return {"mean": statistics.mean(values), "minimum": min(values), "maximum": max(values), "values": values, "availability": "complete"}


def cohort(cells):
    require(cells and len(cells) <= MAX_PROCESSES, "Use 1..32 explicit independent cells per role")
    require(all(route_signature(cell["route_identity"]) == route_signature(cells[0]["route_identity"]) for cell in cells), "One role contains differing package/application identities")
    scopes = {}
    for scope in cells[0]["scopes"]:
        scopes[scope] = {key: aggregate([cell["scopes"][scope][key] for cell in cells])
                         for key in (*LATENCY, "successful_per_second", "offered", "successful", "errors")}
        scopes[scope]["outcomes_total"] = dict(sum((Counter(cell["scopes"][scope]["outcomes"]) for cell in cells), Counter()))
    return {"process_count": len(cells), "eligible": len(cells) == 3 and all(cell["eligible"] for cell in cells), "scopes": scopes,
            "eligibility_note": "Comparative eligibility requires the declared three independent processes; other supplied counts remain descriptive",
            "resources": {key: aggregate([cell["resources"][key] for cell in cells]) for key in RESOURCE},
            "counts": {key: aggregate([cell[key] for cell in cells]) for key in
                       ("durable_measurement_commits", "sqlite_busy", "sqlite_locked", "business_retry_attempts")},
            "aggregation": "Equal-weight arithmetic means of independent process metrics; a mean of process p99 values is not a pooled p99 or a confidence interval",
            "processes": cells}


def change(baseline, candidate):
    available = baseline is not None and candidate is not None
    return {"baseline": baseline, "candidate": candidate, "absolute": candidate - baseline if available else None,
            "percent": 100 * (candidate - baseline) / baseline if available and baseline != 0 else None,
            "percent_unavailable_reason": "Baseline is zero" if available and baseline == 0 else "Missing metric" if not available else None}


def applicable_band(noise, key, before, after):
    problems = []
    config = before[0]["configuration"]
    frozen = noise.get("configuration", {})
    for field in ("seed", "dataset_sha256", "timing", "settings", "service_standard"):
        if frozen.get(field) != config[field]: problems.append("Frozen band configuration differs: " + field)
    for field in ("provider", "rate", "concurrency"):
        if noise.get(field) != config[field]: problems.append("Frozen band load differs: " + field)
    if logical_hashes(frozen.get("source_files", {})) != logical_hashes(before[0]["driver_source_files"]): problems.append("Before driver source differs from band calibration")
    if not frozen.get("route") or route_signature(frozen["route"]) != route_signature(before[0]["route_identity"]): problems.append("Before package/application identity differs from band calibration")
    if utc(noise["created_utc"]) >= min(utc(cell["created_utc"]) for cell in after): problems.append("Band receipt was not frozen before supplied after cells")
    band = noise.get("bands", {}).get(key)
    if not isinstance(band, dict) or not isinstance(band.get("baseline_id"), str) or not band["baseline_id"]:
        problems.append("Missing named frozen band")
    elif not all(finite(band.get(field)) and band[field] >= 0 for field in ("absolute_noise_ns", "relative_noise")):
        problems.append("Invalid frozen band values")
    return band, problems


def compare(cohorts, baseline_role, candidate_role, scope, band, problems, a21, seed):
    baseline, candidate = cohorts[baseline_role], cohorts[candidate_role]
    reasons = list(problems)
    if baseline["process_count"] != 3 or candidate["process_count"] != 3: reasons.append("The declared comparison requires three independent processes in each cohort")
    if not all(cell["eligible"] for cell in baseline["processes"] + candidate["processes"]): reasons.append("At least one explicitly supplied process failed validity, correctness, or the service standard; no process was dropped")
    left = baseline["scopes"][scope]; right = candidate["scopes"][scope]
    means_left, means_right = left["mean_ns"]["values"], right["mean_ns"]["values"]
    if any(value is None for value in (*means_left, *means_right)): reasons.append("At least one process has no successful latency samples")
    noise = {"decision": "inconclusive", "reasons": reasons} if reasons else a21.noise_comparison(means_left, means_right, band, seed)
    result = {"baseline_role": baseline_role, "candidate_role": candidate_role, "scope": scope,
              "eligible": not reasons, "noise_on_process_means": noise,
              "metrics": {key: change(left[key]["mean"], right[key]["mean"]) for key in (*LATENCY, "successful_per_second", "errors")}}
    result["resources"] = {key: change(baseline["resources"][key]["mean"], candidate["resources"][key]["mean"])
                           if scope == "whole" else change(None, None) for key in RESOURCE}
    return result


def display(value, scale=1, digits=3):
    return "N/A" if value is None else f"{value / scale:.{digits}f}"


def markdown(report):
    lines = ["# Perf-01 database cohort comparison", "", "This report reads completed cells only. It does not replay correctness or grant 30-minute acceptance.", "",
             "Latency is scheduled arrival to successful controller completion. Tables show equal-weight means of process metrics; p99 is the mean of process p99 values, not a pooled p99. Failed processes remain included and prevent a performance verdict.", "",
             "Compact observation: " + str(report["configuration"]["compact_observation"]).lower() + ". This is a frozen measurement-tool setting, not a product optimization.", "",
             "| Role | Slice | Processes | Eligible | Success/s | Mean ms | Median ms | p95 ms | p99 ms | CPU % of one core | Mean peak RSS MiB | Errors (total) |",
             "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for role, item in report["cohorts"].items():
        for scope, values in item["scopes"].items():
            fields = [role, scope, str(item["process_count"]), str(item["eligible"]).lower(), display(values["successful_per_second"]["mean"]),
                      *[display(values[name]["mean"], 1e6) for name in ("mean_ns", "median_ns", "p95_ns", "p99_ns")],
                      display(item["resources"]["app_cpu_percent_one_core"]["mean"]) if scope == "whole" else "N/A",
                      display(item["resources"]["rss_peak_bytes"]["mean"], 1024**2) if scope == "whole" else "N/A",
                      str(sum(values["errors"]["values"]))]
            lines.append("| " + " | ".join(fields) + " |")
    lines += ["", "## Absolute changes and direct Rust gaps", "", "A negative latency change means lower latency. Direct gaps use Rust as the denominator. Differences remain descriptive when a comparison is inconclusive.", "",
              "| Baseline → candidate | Slice | Mean Δ ms | Mean Δ % | p99 Δ ms | p99 Δ % | Success/s Δ | Mean-noise verdict |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for row in report["comparisons"]:
        values = row["metrics"]
        lines.append("| " + " | ".join([row["baseline_role"] + " → " + row["candidate_role"], row["scope"],
                    display(values["mean_ns"]["absolute"], 1e6), display(values["mean_ns"]["percent"]),
                    display(values["p99_ns"]["absolute"], 1e6), display(values["p99_ns"]["percent"]),
                    display(values["successful_per_second"]["absolute"]), row["noise_on_process_means"]["decision"]]) + " |")
    lines += ["", "## Independent process rows", "", "Whole-load resource and persistence counts are intentionally separate from conditional cycle/page latency slices.", "",
              "| Role / process | Slice | Success / offered | Mean ms | Median ms | p95 ms | p99 ms | Success/s |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for role, cohort_row in report["cohorts"].items():
        for index, cell in enumerate(cohort_row["processes"]):
            for scope, values in cell["scopes"].items():
                lines.append("| " + " | ".join([f"{role}/{index}", scope, f"{values['successful']} / {values['offered']}",
                             *[display(values[name], 1e6) for name in ("mean_ns", "median_ns", "p95_ns", "p99_ns")],
                             display(values["successful_per_second"])]) + " |")
    lines += ["", "## Whole-load persistence, errors and resources", "",
              "| Role / process | Eligible | Durable measurement commits | SQLite BUSY lifetime | SQLite LOCKED lifetime | Explicit business retries | CPU % of one core | Peak RSS MiB | Errors |",
              "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for role, cohort_row in report["cohorts"].items():
        for index, cell in enumerate(cohort_row["processes"]):
            lines.append("| " + " | ".join([f"{role}/{index}", str(cell["eligible"]).lower(),
                *[display(cell[key], digits=0) for key in ("durable_measurement_commits", "sqlite_busy", "sqlite_locked", "business_retry_attempts")],
                display(cell["resources"]["app_cpu_percent_one_core"]), display(cell["resources"]["rss_peak_bytes"], 1024**2),
                str(cell["scopes"]["whole"]["errors"])]) + " |")
    lines += ["", "## Scope and limitations", "", *["- " + item for item in report["limitations"]], "",
              "Exact input hashes, process paths, artifact identities, generator resources, outcome classifications, percentile ranges and bootstrap intervals are in the adjacent JSON report.", ""]
    return "\n".join(lines)


def extract(args):
    product = args.nativeweave.resolve()
    a21_path = product / "src/Benchmarks.Harness/nativeweave_bench.py"
    reader_path = product / "tests/Perf01/verify_long.py"
    a21, reader = module(a21_path, "perf01_compare_a21"), module(reader_path, "perf01_compare_reader")
    sources = {str(path): sha(path) for path in (Path(__file__).resolve(), a21_path, reader_path)}
    noise_path = args.noise_receipt.resolve()
    require(noise_path.stat().st_size <= 64 * 1024**2 and sha(noise_path) == args.noise_sha256, "Frozen noise receipt identity differs")
    noise_before = stamp(noise_path)
    noise = json.loads(noise_path.read_text())
    require(noise["task"] == "Perf-01" and len(noise.get("processes", [])) >= 3, "Noise receipt needs its before-only independent-process provenance")
    cohorts, paths = {}, set()
    for role in ROUTES:
        selected = getattr(args, role)
        if selected is None: continue
        resolved = [path.resolve() for path in selected]
        require(len(set(resolved)) == len(resolved) and not paths.intersection(resolved), "A process directory was repeated within/across cohorts")
        paths.update(resolved)
        cohorts[role] = cohort([read_cell(path, role, a21, reader, sources[str(a21_path)]) for path in resolved])
    all_cells = [cell for item in cohorts.values() for cell in item["processes"]]
    instances = [(cell["application_instance"]["pid"], cell["application_instance"]["start_ticks"]) for cell in all_cells]
    require(len(set(instances)) == len(instances), "Two cells report the same application process instance")
    windows = sorted((cell["measurement_window_ns"]["start"], cell["measurement_window_ns"]["end"]) for cell in all_cells)
    require(all(windows[index - 1][1] <= windows[index][0] for index in range(1, len(windows))), "Measurement windows overlap on the shared machine")
    config = all_cells[0]["configuration"]
    require(all(cell["configuration"] == config for cell in all_cells), "Cohorts differ in workload, service limits, host, toolchain, or CPU layout")
    require(all(logical_hashes(cell["driver_source_files"]) == logical_hashes(all_cells[0]["driver_source_files"]) for cell in all_cells), "Cohorts used different frozen measurement drivers/dependencies")
    require(route_signature(cohorts["before"]["processes"][0]["route_identity"])["toolchain"] ==
            route_signature(cohorts["after"]["processes"][0]["route_identity"])["toolchain"], "Before/after application toolchain metadata differs")
    comparisons = []
    for scope in cohorts["before"]["scopes"]:
        band_key = config["scenario"] if scope == "whole" else scope
        band, reasons = applicable_band(noise, band_key, cohorts["before"]["processes"], cohorts["after"]["processes"])
        for left, right in [("before", "after"), ("direct", "before"), ("direct", "after"), *([("direct", "managed")] if "managed" in cohorts else [])]:
            comparisons.append(compare(cohorts, left, right, scope, band, reasons, a21, config["seed"]))
    require(stamp(noise_path) == noise_before and sha(noise_path) == args.noise_sha256, "Noise receipt changed while extracting")
    require(all(sha(Path(path)) == digest for path, digest in sources.items()), "Extractor/statistical source changed while extracting")
    return {"schema_version": 1, "task": "Perf-01", "created_utc": datetime.now(timezone.utc).isoformat(),
            "status": "completed", "scope": "Read-only completed database cohorts; no workload execution or new measurement acceptance",
            "configuration": config, "source_sha256": sources, "noise_receipt": {"path": str(noise_path), "sha256": args.noise_sha256},
            "bootstrap_seed": config["seed"], "cohorts": cohorts, "comparisons": comparisons,
            "limitations": ["Latency includes real HTTP, authentication, typed application work, C#/Rust binding, SQL and I/O; it is not isolated database execution latency.",
                "Independent processes are the comparison units. No failed or missing-valued supplied process is dropped; incomplete metrics are N/A. Percent change from a zero baseline is N/A.",
                "A21 nearest-rank p50/p95/p99 are withheld below their sample-count limits. Median uses the conventional mean of the two center values for an even count.",
                "The unchanged A21 bootstrap concerns process means only, not p99. Frozen noise bands are never recalibrated or widened from these comparison results.",
                "Whole-load CPU/RSS and generator resources are not assigned to conditional cycle/page slices. PostgreSQL service CPU/RSS, exact SQL/pool/lock wait durations and internal SQLite busy-handler retries are unavailable.",
                "SQLite BUSY/LOCKED and explicit retry observations cover the complete application lifetime; independently queried durable measurement commits exclude seed, warmup and recovery mutations.",
                "Equal successful throughput at one offered rate does not establish equal maximum capacity. Capacity ladders and overload/recovery results remain separate.",
                "This checks recorded consistency and hashes, not historical authenticity or actual network/persistence correctness again. Inputs with prior hashes are compared; all consumed inputs receive new hashes.",
                "The provided noise SHA must already be bound in the before-only frozen Plan record; a JSON creation timestamp alone cannot prove publication chronology."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nativeweave", type=Path, required=True)
    for role in ROUTES:
        parser.add_argument("--" + role, type=Path, nargs="+", required=role != "managed")
    parser.add_argument("--noise-receipt", type=Path, required=True)
    parser.add_argument("--noise-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True, help="New output directory containing comparison.json and comparison.md")
    args = parser.parse_args()
    require(not args.output.exists(), "Output must be new; raw cells and earlier reports are never overwritten")
    require(not any(args.output.resolve().is_relative_to(path.resolve()) for role in ROUTES
                    for path in (getattr(args, role) or [])), "Report output must be outside every selected raw cell")
    report = extract(args)
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output / "comparison.json").open("x") as stream:
        json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False); stream.write("\n")
    (args.output / "comparison.md").write_text(markdown(report))
    print(json.dumps({"status": report["status"], "output": str(args.output.resolve()), "processes": sum(item["process_count"] for item in report["cohorts"].values())}))


if __name__ == "__main__":
    main()
