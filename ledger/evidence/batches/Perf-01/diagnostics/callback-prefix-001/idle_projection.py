#!/usr/bin/env python3
"""Project completed original post-recovery/after-idle CPU snapshots; no raw-series read."""
import argparse
import hashlib
import json
from pathlib import Path


def read(path):
    data = path.read_bytes()
    return json.loads(data), hashlib.sha256(data).hexdigest()


def observed(receipt):
    before = receipt.get('recovery_resources_after', {})
    after = receipt.get('after_idle_resources', {})
    fields = ('cpu_ticks', 'clock_ticks_per_second', 'time_ns')
    if any(before.get(key) is None or after.get(key) is None for key in fields):
        return {'available': False, 'reason': 'Original CPU/time snapshot unavailable'}
    for snapshot in (before, after):
        for key in (*fields, 'pid'):
            value = snapshot.get(key)
            minimum = 1 if key in ('clock_ticks_per_second', 'pid') else 0
            if type(value) is not int or value < minimum:
                return {'available': False, 'reason': 'Original CPU/time/process counter is invalid'}
    if before['pid'] != after['pid']:
        return {'available': False, 'reason': 'Snapshots identify different processes'}
    hz = before['clock_ticks_per_second']
    elapsed = after['time_ns'] - before['time_ns']
    ticks = after['cpu_ticks'] - before['cpu_ticks']
    if hz <= 0 or hz != after['clock_ticks_per_second'] or elapsed <= 0 or ticks < 0:
        return {'available': False, 'reason': 'Original CPU/time snapshot interval invalid'}
    seconds = ticks / hz
    idle_start, idle_end = receipt.get('idle_start_utc_ns'), receipt.get('idle_end_utc_ns')
    return {'available': True, 'before_cpu_ticks': before['cpu_ticks'],
            'after_cpu_ticks': after['cpu_ticks'], 'clock_ticks_per_second': hz,
            'elapsed_monotonic_ns': elapsed, 'cpu_seconds': seconds,
            'cpu_percent_one_core': seconds * 1e11 / elapsed,
            'configured_idle_utc_interval_ns': idle_end-idle_start
                if type(idle_start) is int and type(idle_end) is int
                and 0 <= idle_start <= idle_end else None}


def validate_cells(plan):
    expected = {(scene, replicate, role) for scene in ('unary', 'streams')
                for replicate in range(3) for role in ('current', 'candidate')}
    profile_hashes = {
        'unary': '88551fe7272de60c8686ab7a6b034c85af82b7dab3de8621c5c8be8ea612289f',
        'streams': 'f47045770f3178267a767351016cf72aabf97a542dfb806d16f9ed63a64fd878'}
    cells = plan['cells']
    if len(cells) != len(expected):
        raise ValueError('Expected exactly twelve original protocol cells')
    seen, outputs = set(), set()
    root = Path(plan['output']).resolve()
    for cell in cells:
        scene, replicate, role = cell['scene'], cell['repetition'], cell['role']
        key = (scene, replicate, role)
        if type(replicate) is not int or key not in expected or key in seen:
            raise ValueError('Expected two profiles and three unique current/candidate pairs per profile')
        output = Path(cell['output']).resolve()
        required = root / 'cells' / f'{scene}-{replicate}-{role}'
        if output != required or output in outputs:
            raise ValueError('Cell output does not match its unique owned execution path')
        if (Path(cell['profile']).name != f'grpc-{scene}.json'
                or cell['profile_sha256'] != profile_hashes[scene]):
            raise ValueError('Cell profile differs from the original unary/stream profile')
        seen.add(key)
        outputs.add(output)
    if seen != expected:
        raise ValueError('Original protocol cell matrix is incomplete')
    return cells


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError('Fresh projection output required')
    plan, plan_hash = read(args.plan)
    execution, execution_hash = read(Path(plan['output']) / 'execution.json')
    if execution['plan_sha256'] != plan_hash:
        raise ValueError('Completed execution belongs to a different actual plan')
    cells = validate_cells(plan)
    if (execution['status'] != 'diagnostic-completed' or not execution['commands']
            or not all(c['exit_code'] == 0 and c['retired'] is True for c in execution['commands'])):
        raise ValueError('Original twelve-cell owner must complete and retire before projection')
    rows, pairs = [], {}
    for cell in cells:
        result, result_hash = read(Path(cell['output']) / 'result.json')
        receipt, receipt_hash = read(Path(cell['output']) / 'execution/receipt.json')
        row = {'scene': cell['scene'], 'replicate': cell['repetition'], 'role': cell['role'],
               'result_sha256': result_hash, 'receipt_sha256': receipt_hash,
               'original_valid': result['valid'], 'original_service_standard_met': result['service_standard_met'],
               'active_cpu_percent_one_core': result['resources']['server'].get('cpu_percent_one_core'),
               'post_recovery_to_after_idle': observed(receipt)}
        rows.append(row)
        pairs.setdefault((row['scene'], row['replicate']), {})[row['role']] = row
    comparisons = []
    for (scene, replicate), pair in sorted(pairs.items()):
        current, candidate = [pair[role]['post_recovery_to_after_idle'] for role in ('current', 'candidate')]
        row = {'scene': scene, 'replicate': replicate, 'available': current['available'] and candidate['available']}
        if row['available']:
            left, right = current['cpu_percent_one_core'], candidate['cpu_percent_one_core']
            row.update(current_percent_one_core=left, candidate_percent_one_core=right,
                       change_percentage_points=right-left,
                       relative_change_percent=(right-left)*100/left if left else None)
        comparisons.append(row)
    output = {'task': 'Perf-01', 'kind': 'original-idle-bracket-cpu-projection',
              'plan_sha256': plan_hash, 'execution_sha256': execution_hash,
              'performance_credit_seconds': 0, 'new_measurement_performed': False,
              'scope': 'Descriptive process CPU from recovery_resources_after to after_idle_resources; '
                       'includes idle transition/diagnostic work, excludes final stop/disposal; '
                       'this is not an isolated timer cost or a new statistical/significance decision.',
              'rows': rows, 'paired_idle_bracket_comparisons': comparisons}
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'rows': len(rows), 'pairs': len(comparisons), 'performance_credit_seconds': 0}))


if __name__ == '__main__':
    main()
