"""Read the interrupted codec attempt without modifying any original evidence."""
import argparse
import collections
import datetime
import hashlib
import json
from pathlib import Path


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), 'Keep prior audits immutable'
    raw = args.root / 'perf01-evidence/long/before/codec-001'
    plan = json.loads((raw / 'plan.json').read_text())
    progress = json.loads((raw / 'phase-progress.json').read_text())
    assert plan['planned_rate'] == 192 and plan['duration_seconds'] == 1802
    assert plan['workers'] == 2 and not progress['measurement']['completed']
    assert not (raw / 'result.json').exists()
    before = {p.name: (p.stat().st_size, p.stat().st_mtime_ns)
              for p in raw.iterdir() if p.is_file()}
    phases = collections.Counter()
    outcomes = collections.Counter()
    actions = collections.Counter()
    first = last = None
    lag_max = 0
    over_limit = 0
    ids = set()
    with (raw / 'operations.jsonl').open() as stream:
        for line in stream:
            row = json.loads(line)
            assert row['id'] not in ids
            ids.add(row['id'])
            phases[row['phase']] += 1
            outcomes[row['phase'] + ':' + row['outcome']] += 1
            if row['phase'] != 'measurement':
                continue
            stamp = row['dispatch_ns']
            first = stamp if first is None else min(first, stamp)
            last = stamp if last is None else max(last, stamp)
            lag = stamp - row['scheduled_ns']
            lag_max = max(lag_max, lag)
            over_limit += lag > plan['max_lag_ms'] * 1_000_000
            actions[row['action'] + ':' + row['interface']] += 1
    missing_prefix = sorted(set(range(max(ids) + 1)) - ids)
    assert first is not None and last is not None
    assert phases['recovery'] == 0 and (last - first) < 1800 * 1_000_000_000
    files = {name: {'bytes': size, 'sha256': digest(raw / name)}
             for name, (size, _) in sorted(before.items())}
    assert before == {p.name: (p.stat().st_size, p.stat().st_mtime_ns)
                      for p in raw.iterdir() if p.is_file()}
    execution = args.root / 'perf01-run/before-codec-long-001-execution.json'
    result = {
        'task': 'Perf-01', 'schema_version': 1,
        'state': 'interrupted-incomplete', 'accepted': False,
        'duration_credit_seconds': 0,
        'audit_created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'audit_source_sha256': digest(Path(__file__)),
        'original_execution_sha256': digest(execution),
        'normal_exit_code': None, 'normal_drain': 'unavailable',
        'failure_reason': 'Execution connection reset; incomplete measurement and absent recovery/drain/result',
        'first_measurement_dispatch_ns': first,
        'last_measurement_dispatch_ns': last,
        'recorded_measurement_dispatch_span_seconds': (last - first) / 1_000_000_000,
        'recorded_operations_by_phase': dict(phases),
        'recorded_outcomes': dict(outcomes),
        'recorded_measurement_actions_interfaces': dict(actions),
        'recorded_max_dispatch_lag_ns': lag_max,
        'recorded_dispatch_lag_over_limit': over_limit,
        'recorded_ids_are_unique': True,
        'last_observed_id': max(ids),
        'unrecorded_ids_within_observed_prefix': missing_prefix,
        'measurement_completed': progress['measurement']['completed'],
        'rate': plan['planned_rate'], 'workers': plan['workers'],
        'manifest_sha256': plan['manifest_sha256'],
        'native_sha256': [x['sha256'] for x in plan['actual_loaded_native']],
        'corpus_manifest_sha256': plan['corpus_manifest_sha256'],
        'driver_sha256': plan['controller_sha256'],
        'files': files,
        'scope': 'Retained partial numerical evidence; no accepted performance or duration claim',
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
