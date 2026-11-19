#!/usr/bin/env python3
"""Read existing diagnostic logs and preserve bounded, source-bound subsets."""
import argparse
import base64
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

CONFIG_SHA = "550bbeadb7f58424a4d8fcb377783ba8bc186fa542bfab2d9ddf059997e1395a"
HOOK_SHA = "0c26d224e8da07644f08196d7293332f3f0dfc937dceb57caf5e6cd1832cedd2"
A21_SHA = "dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53"
MAX_LINE = 4 * 1024**2


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stamp(path):
    stat = path.stat()
    return [stat.st_size, stat.st_mtime_ns, stat.st_ino]


def write_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def event_metadata(raw, number):
    wire = base64.b64decode(raw["wire_base64"], validate=True)
    event = json.loads(wire)
    return {"source_line": number, "observed_ns": raw["observed_ns"],
            "kind": event.get("kind"), "id": event.get("id"),
            "status": event.get("status"), "wire_bytes": len(wire),
            "wire_sha256": hashlib.sha256(wire).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root, output = args.run.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    config_path = root / "configuration.json"
    assert sha(config_path) == CONFIG_SHA
    config = json.loads(config_path.read_text())
    assert config["hook_sha256"] == HOOK_SHA and config["a21_sha256"] == A21_SHA
    assert sha(Path(config["hook_path"])) == HOOK_SHA
    assert sha(Path(config["controller_path"])) == config["controller_sha256"]
    assert sha(Path(config["a21_path"])) == A21_SHA
    assert not list((root / "gc").glob("attachment-error-*"))
    changed = [index for index, pair in enumerate(zip(config["original_command"], config["command"]))
               if pair[0] != pair[1]]
    assert len(config["original_command"]) == len(config["command"])
    assert changed == sorted(config["original_command"].index(flag) + 1 for flag in ("--output", "--variant"))
    plan_path = root / "cell/plan.json"
    plan_sha = sha(plan_path)
    plan = json.loads(plan_path.read_text())
    assert plan["timing"]["requests"] == 259526 and plan["timing"]["period_ns"] == 6944444
    assert plan["timing"]["max_dispatch_lag_ns"] == 100000000
    assert plan["settings"]["features"]["concurrency"] == 16
    raw_path = root / "cell/observation.events.jsonl"
    with raw_path.open("rb") as stream:
        first_line = stream.readline(MAX_LINE + 1)
    assert len(first_line) <= MAX_LINE
    first = event_metadata(json.loads(first_line), 1)
    assert first["kind"] == "admitted" and first["id"] == 0
    first_ns = first["observed_ns"]
    (output / "first-measurement-event.jsonl").write_bytes(first_line)
    inputs = {}
    roles = {}
    gen2_pairs = {}
    for path in sorted((root / "gc").glob("*.jsonl")):
        before = stamp(path)
        assert before[0] < 16 * 1024**2
        digest = hashlib.sha256()
        header = None
        previous = None
        sequence = 0
        active = {}
        counts = Counter()
        pairs = []
        selected = []
        selected_numbers = []
        with path.open("rb") as stream:
            for number, line in enumerate(stream, 1):
                assert len(line) <= MAX_LINE
                digest.update(line)
                row = json.loads(line)
                if header is None:
                    header = row
                    assert row["kind"] == "attached"
                    role = row["role"]
                    expected = next(item for item in config["roles"] if item["role"] == role)
                    assert row["configuration_sha256"] == CONFIG_SHA
                    assert row["hook_sha256"] == HOOK_SHA and row["a21_sha256"] == A21_SHA
                    assert row["entry"] == expected["entry"] and row["argv"] == expected["argv"]
                    assert row["entry_sha256"] == expected["entry_sha256"]
                    assert sha(Path(expected["entry"])) == row["entry_sha256"]
                    assert row["plan_sha256"] == plan_sha
                    assert row["python_executable"] == config["python_realpath"]
                    assert row["cpu_affinity"] == [0, 1] and row["gc_enabled"] is True
                    assert row["gc_threshold"] == [700, 10, 10]
                    assert row["preexisting_gc_callbacks"] == 0
                    assert row["formal_timing_eligible"] is False
                    selected.append(line); selected_numbers.append(number)
                    continue
                assert row["kind"] == "gc", "Log exhausted or unexpected record kind"
                assert row["sequence"] == sequence + 1
                sequence += 1
                assert all(row[key] == header[key] for key in ("pid", "start_ticks", "role"))
                if previous is not None:
                    assert row["monotonic_ns"] >= previous["monotonic_ns"]
                    assert row["process_cpu_ns"] >= previous["process_cpu_ns"]
                previous = row
                generation = row["generation"]
                counts[str(generation) + ":" + row["phase"]] += 1
                if row["phase"] == "start":
                    assert generation not in active
                    active[generation] = row
                else:
                    assert row["phase"] == "stop"
                    begin = active.pop(generation)
                    assert row["native_thread_id"] == begin["native_thread_id"]
                    assert row["start_monotonic_ns"] == begin["monotonic_ns"]
                    assert row["callback_entry_duration_ns"] == row["monotonic_ns"] - begin["monotonic_ns"]
                    assert row["callback_entry_duration_ns"] == row["start_hook_ns"] + row["collection_interval_ns"]
                    assert row["callback_entry_cpu_ns"] == row["process_cpu_ns"] - begin["process_cpu_ns"]
                    if generation == 2:
                        pairs.append({"start": begin, "stop": row})
                if generation == 2:
                    selected.append(line); selected_numbers.append(number)
        assert not active, "Incomplete GC pairs cannot be used for a no-pause claim"
        assert stamp(path) == before
        name = "gc-" + role + "-headers-and-gen2.jsonl"
        with (output / name).open("xb") as stream:
            stream.writelines(selected)
        inputs[str(path)] = {"bytes": before[0], "sha256": digest.hexdigest(), "stat_identity": before}
        roles[role] = {"header": header, "phase_counts": dict(counts),
                       "last_record": previous, "pairing_and_sequence_errors": [],
                       "incomplete_pairs": [], "selected_source_lines": selected_numbers,
                       "selection": name}
        gen2_pairs[role] = pairs
    assert set(roles) == {"scheduler", "target"}
    measured_scheduler = [pair for pair in gen2_pairs["scheduler"]
                          if pair["start"]["monotonic_ns"] >= first_ns]
    assert len(measured_scheduler) == 1
    pause = measured_scheduler[0]
    begin, end = pause["start"]["monotonic_ns"], pause["stop"]["monotonic_ns"]
    assert pause["stop"]["collection_interval_ns"] == 240004324
    lower, upper = begin - 20_000_000, end + 50_000_000
    raw_before = stamp(raw_path)
    digest = hashlib.sha256()
    previous = None
    before_pause = after_pause = None
    before_bytes = after_bytes = None
    during = 0
    selected_events = []
    previous_ns = None
    last_ns = None
    row_count = 0
    near_max_gap = None
    with raw_path.open("rb") as source, (output / "events-around-scheduler-gen2.jsonl").open("xb") as sink:
        for number, line in enumerate(source, 1):
            assert len(line) <= MAX_LINE
            digest.update(line)
            raw = json.loads(line)
            now = raw["observed_ns"]
            assert previous_ns is None or now >= previous_ns
            previous_ns = last_ns = now
            row_count += 1
            if now < begin:
                before_pause, before_bytes = (number, raw), line
            elif now <= end:
                during += 1
            elif after_pause is None:
                after_pause, after_bytes = (number, raw), line
            if lower <= now <= upper:
                event = event_metadata(raw, number)
                selected_events.append(event)
                assert len(selected_events) <= 1024
                sink.write(line)
                if previous is not None:
                    gap = now - previous[1]["observed_ns"]
                    if near_max_gap is None or gap > near_max_gap["gap_ns"]:
                        near_max_gap = {"gap_ns": gap,
                                        "before": event_metadata(previous[1], previous[0]), "after": event}
            previous = (number, raw)
    assert stamp(raw_path) == raw_before
    inputs[str(raw_path)] = {"bytes": raw_before[0], "sha256": digest.hexdigest(), "stat_identity": raw_before}
    assert before_pause is not None and after_pause is not None
    (output / "last-event-before-scheduler-gen2.jsonl").write_bytes(before_bytes)
    (output / "first-event-after-scheduler-gen2.jsonl").write_bytes(after_bytes)
    before_event = event_metadata(before_pause[1], before_pause[0])
    after_event = event_metadata(after_pause[1], after_pause[0])
    burst = {}
    for width in (1_000_000, 10_000_000):
        values = [event for event in selected_events
                  if after_event["observed_ns"] <= event["observed_ns"] < after_event["observed_ns"] + width]
        burst[str(width)] = {"anchor": "first raw observation after the scheduler GC stop",
                             "events": len(values),
                             "kinds": dict(Counter(event["kind"] for event in values)),
                             "admitted_ids": [event["id"] for event in values if event["kind"] == "admitted"]}
    for role, pairs in gen2_pairs.items():
        measured = [pair for pair in pairs if first_ns <= pair["start"]["monotonic_ns"]
                    and pair["stop"]["monotonic_ns"] <= last_ns]
        roles[role]["gen2_pairs_after_first_event_before_last_event"] = measured
        roles[role]["measured_gen2_count"] = len(measured)
        roles[role]["maximum_measured_gen2_collection_ns"] = max(
            (pair["stop"]["collection_interval_ns"] for pair in measured), default=None)
    copy_names = ("configuration.json", "launch.json", "cell/control.json", "cell/profile-driver.json",
                  "cell/summary.json", "cell/progress.json", "cell/plan.json",
                  "cell/supervision/receipt.json", "cell/supervision/owned-processes.jsonl")
    copies = output / "source-small"
    copies.mkdir()
    for name in copy_names:
        path = root / name
        assert path.stat().st_size <= 131072
        data = path.read_bytes()
        target = copies / name.replace("/", "--")
        target.write_bytes(data)
        inputs[str(path)] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                             "copy": str(target.relative_to(output))}
    supervisor = json.loads((root / "cell/supervision/receipt.json").read_text())
    assert supervisor["failure"] == "operator stop control"
    assert supervisor["live_owned_processes_after_cleanup"] == [] and supervisor["worker_exit_code"] == -15
    assert all(item["signal"] == 15 for item in supervisor["signals"])
    marker = json.loads((root / "cell/profile-driver.json").read_text())
    assert marker["formal_timing_eligible"] is False and marker["duration_credit_seconds"] == 0
    for name in ("hook_path", "controller_path", "a21_path"):
        path = Path(config[name])
        inputs[str(path)] = {"bytes": path.stat().st_size, "sha256": sha(path)}
    result = {
        "schema_version": 1, "task": "Perf-01", "formal_timing_eligible": False,
        "accepted": False, "duration_credit_seconds": 0,
        "started_utc": started, "ended_utc": datetime.now(timezone.utc).isoformat(),
        "extractor_sha256": sha(Path(__file__)), "inputs": inputs,
        "first_measurement_event": first, "last_raw_event_observed_ns": last_ns,
        "raw_event_rows": row_count, "roles": roles, "scheduler_measured_gen2": pause,
        "scheduler_gen2_start_offset_from_first_event_ns": begin - first_ns,
        "raw_events_during_scheduler_gen2": during,
        "last_event_before_scheduler_gen2": before_event,
        "first_event_after_scheduler_gen2": after_event,
        "bracketing_observation_gap_ns": after_event["observed_ns"] - before_event["observed_ns"],
        "nearby_maximum_event_gap": near_max_gap, "post_stop_observation_bursts_ns": burst,
        "event_selection": {"lower_ns": lower, "upper_ns": upper,
                            "rows": selected_events, "scope": "Observed admission/completion times, not dispatch times"},
        "partial_dispatch_ledger_absent": not (root / "cell/observation.json").exists(),
        "supervision_cleanup_empty": True,
        "postmaster_pid_files_present_at_analysis": [str(path) for path in (root / "cell/postgres").rglob("postmaster.pid")],
        "limits": [
            "This is an instrumented, intentionally interrupted, zero-credit diagnostic.",
            "GC callback intervals are observations including scheduling effects, not exclusive collector CPU.",
            "Raw events contain admission/completion observations; the final exact dispatch ledger is absent.",
            "A scheduler GC pause is temporally associated with this diagnostic event gap and catch-up observations.",
            "This does not establish the cause of both clusters in the separate uninstrumented failed run.",
            "The roughly six-minute diagnostic scope cannot exclude causes near the original 1028-second cluster.",
            "Any scheduler-only GC policy remedy needs prospective driver identity, equivalence and resource validation."
        ],
        "outputs": {str(path.relative_to(output)): sha(path) for path in output.rglob("*") if path.is_file()}
    }
    write_json(output / "analysis.json", result)
    print(json.dumps({"status": "completed", "scheduler_collection_interval_ns": pause["stop"]["collection_interval_ns"],
                      "raw_observation_gap_ns": result["bracketing_observation_gap_ns"],
                      "events_during_gc": during, "post_stop_bursts": burst,
                      "target_gen2_maximum_ns": roles["target"]["maximum_measured_gen2_collection_ns"],
                      "formal_timing_eligible": False, "duration_credit_seconds": 0}))


if __name__ == "__main__":
    main()
