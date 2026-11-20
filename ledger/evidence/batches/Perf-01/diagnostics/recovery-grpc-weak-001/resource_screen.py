#!/usr/bin/env python3
"""Supplement the unchanged protocol statistics with frozen ON resource ranges.

This offline reader cannot approve retention or assign long-duration credit.
It consumes complete original reader outputs, never selected replacement cells.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
ON = '2e3995df8d86583ee9443348276ca8d918056bfc'
OFF = '4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4'
PROFILES = {'grpc-unary', 'grpc-streams'}


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def load(path, expected=None):
    path = Path(path)
    need(path.stat().st_size <= 64 * 1024**2, 'Oversized reader control')
    need(expected is None or sha(path) == expected, 'Reader identity differs: ' + str(path))
    def number(text):
        value = float(text)
        need(math.isfinite(value), 'Nonfinite control number')
        return value
    return json.loads(path.read_text(), parse_float=number, parse_constant=number)


def utc(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    need(result.tzinfo is not None, 'Timestamp lacks timezone')
    return result.astimezone(timezone.utc)


def numeric(value):
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def values(cell):
    result = {'p99/' + key: row['metrics']['arrival_p99_ns']
              for key, row in cell['scenarios'].items() if not row['expected_probe']}
    resources = cell.get('resources') or {}
    server = (resources.get('processes') or {}).get('server') or {}
    result['server_cpu_percent_one_core'] = server.get('cpu_percent_one_core')
    result['server_rss_bytes_maximum'] = server.get('rss_bytes_maximum')
    result['server_allocated_mib_per_second'] = (resources.get('managed_gc_observation') or {}).get('allocated_mib_per_second')
    return result


def checked_cells(cells, role, expected):
    need(len(cells) == 3, 'Exactly three original independent processes are required')
    need(all(c['variant'] == role and c['eligible'] is True
             and c['build']['product_source_commit'] == expected for c in cells), 'Actual role/source/eligibility differs')
    need(len({c['result_sha256'] for c in cells}) == 3, 'Reused result in process triplet')
    rows = [values(c) for c in cells]
    need(all(set(row) == set(rows[0]) for row in rows), 'Scenario/resource populations differ')
    return rows


def control(path, expected, stage):
    index = load(path, expected)
    need(index['task'] == 'Perf-01' and index['stage'] == stage and index['status'] == 'completed', 'Incomplete original cohort')
    need(set(index['profiles']) == PROFILES, 'Unexpected profile population')
    need(index['source_contract_sha256']['protocol_compare.py'] == sha(HERE / 'protocol_compare.py')
         and index['source_contract_sha256']['protocol_cohorts.py'] == sha(HERE / 'protocol_cohorts.py'), 'Original scoped reader/cohort source changed')
    need(index['service_cpus'] == [2, 3] and index['generator_cpus'] == [0, 1], 'Resource layout differs')
    expected_count = 6 if stage == 'noise' else 18
    need(len(index['cells']) == expected_count and all(c['state'] == 'completed' and c['valid'] is True
         and c['service_standard_met'] is True for c in index['cells']), 'Incomplete or ineligible actual process population')
    return index


def freeze(index, index_sha):
    profiles = {}
    for name in sorted(PROFILES):
        item = index['profiles'][name]
        original = load(item['receipt'], item['sha256'])
        need(original['kind'] == 'protocol-before-only-noise' and original['baseline_product_source_commit'] == ON
             and original['extractor_sha256'] == sha(HERE / 'protocol_compare.py'), 'Wrong original ON-only noise')
        rows = checked_cells(original['before_processes'], 'before', ON)
        bands, unavailable = {}, []
        for key in sorted(rows[0]):
            samples = [row[key] for row in rows]
            complete = all(numeric(v) for v in samples)
            bands[key] = {'process_values': samples, 'minimum': min(samples) if complete else None,
                          'maximum': max(samples) if complete else None,
                          'range': max(samples) - min(samples) if complete else None}
            if not complete:
                unavailable.append(key)
        profiles[name] = {'original_noise_sha256': item['sha256'], 'bands': bands, 'unavailable': unavailable}
    return {'task': 'Perf-01', 'epoch': 'recovery-001', 'kind': 'weak-ON-resource-range-freeze',
            'status': 'completed', 'created_utc': datetime.now(timezone.utc).isoformat(),
            'complete_noise_index_sha256': index_sha, 'policy_sha256': sha(HERE / 'policy.json'),
            'reader_sha256': sha(Path(__file__)), 'profiles': profiles,
            'method': 'Exact range of all three fresh ON processes; descriptive, not a confidence interval',
            'retention_approved': False, 'long_credit_seconds': 0}


def screen(noise_index, index_sha, comparison, ranges, ranges_sha):
    need(ranges['kind'] == 'weak-ON-resource-range-freeze' and ranges['status'] == 'completed'
         and ranges['complete_noise_index_sha256'] == index_sha
         and ranges['policy_sha256'] == sha(HERE / 'policy.json')
         and ranges['reader_sha256'] == sha(Path(__file__)), 'Supplemental freeze/source differs')
    regenerated = freeze(noise_index, index_sha)
    need(regenerated['profiles'] == ranges['profiles'], 'Resource ranges do not equal the complete ON-only observations')
    need(noise_index['source_contract_sha256'] == comparison['source_contract_sha256']
         and noise_index['common_client'] == comparison['common_client'] and noise_index['tls'] == comparison['tls'],
         'Common source/client/TLS differs')
    need(all(noise_index['builds'][role] == comparison['builds'][role] for role in ('before', 'direct')), 'ON/direct producer changed after noise')
    profiles, vetoes, unavailable = {}, [], []
    for name in sorted(PROFILES):
        item = comparison['profiles'][name]
        report = load(item['receipt'], item['sha256'])
        need(report['comparative_interpretation_eligible'] is True
             and report['noise_sha256'] == noise_index['profiles'][name]['sha256']
             and report['extractor_sha256'] == sha(HERE / 'protocol_compare.py'), 'Original comparison is not eligible or bound to this noise')
        on = checked_cells(report['cohorts']['before'], 'before', ON)
        off = checked_cells(report['cohorts']['after'], 'after', OFF)
        need(all(utc(c['measurement_window']['start_utc']) > utc(ranges['created_utc'])
                 for role in ('before', 'after', 'direct') for c in report['cohorts'][role]), 'Supplemental freeze did not precede fresh comparisons')
        need(set(on[0]) == set(off[0]) == set(ranges['profiles'][name]['bands']), 'Frozen metric population differs')
        observations = {}
        for key, band in ranges['profiles'][name]['bands'].items():
            left, right = [r[key] for r in on], [r[key] for r in off]
            complete = all(numeric(v) for v in left + right) and numeric(band['range'])
            mean_delta = statistics.mean(left) - statistics.mean(right) if complete else None
            max_delta = max(left) - max(right) if complete else None
            is_veto = key != 'server_allocated_mib_per_second'
            adverse = complete and is_veto and (mean_delta > band['range'] or max_delta > band['range'])
            observations[key] = {'on_process_values': left, 'off_process_values': right, 'frozen_ON_range': band['range'],
                                 'ON_minus_OFF_mean': mean_delta, 'ON_minus_OFF_maximum': max_delta,
                                 'veto_metric': is_veto, 'adverse_beyond_range': adverse if complete else None,
                                 'scope': 'Per-scenario process p99' if key.startswith('p99/') else 'Whole profile only'}
            if not complete:
                unavailable.append(name + '/' + key)
            if adverse:
                vetoes.append(name + '/' + key)
        a21 = {}
        for key, row in report['ordinary_scenarios'].items():
            need(row['expected_probe'] is False, 'Expected probe included in ordinary A21 decisions')
            decision = row['noise']['decision']
            need(decision in ('improvement', 'regression', 'within_band', 'inconclusive'), 'Unexpected original A21 verdict')
            a21[key] = {'original_OFF_minus_ON_decision': decision, 'adverse_for_retaining_ON': decision == 'improvement'}
            if decision == 'improvement':
                vetoes.append(name + '/A21/' + key)
        profiles[name] = {'comparison_sha256': item['sha256'], 'observations': observations, 'a21': a21}
    return {'task': 'Perf-01', 'epoch': 'recovery-001', 'kind': 'weak-ON-OFF-resource-screen', 'status': 'completed',
            'noise_index_sha256': index_sha, 'resource_freeze_sha256': ranges_sha, 'policy_sha256': sha(HERE / 'policy.json'),
            'reader_sha256': sha(Path(__file__)), 'profiles': profiles, 'vetoes': vetoes, 'unavailable': unavailable,
            'screen_eligible': not vetoes and not unavailable, 'capacity': 'required separately; not inferred from fixed load',
            'retention_approved': False, 'long_credit_seconds': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('freeze', 'screen'))
    parser.add_argument('--noise-index', type=Path, required=True)
    parser.add_argument('--noise-index-sha256', required=True)
    parser.add_argument('--comparison-index', type=Path)
    parser.add_argument('--comparison-index-sha256')
    parser.add_argument('--resource-freeze', type=Path)
    parser.add_argument('--resource-freeze-sha256')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    need(not args.output.exists(), 'Fresh output is required; preserve failures')
    result = {'task': 'Perf-01', 'epoch': 'recovery-001', 'status': 'failed', 'retention_approved': False, 'long_credit_seconds': 0}
    try:
        noise = control(args.noise_index, args.noise_index_sha256, 'noise')
        if args.command == 'freeze':
            result = freeze(noise, args.noise_index_sha256)
        else:
            need(args.comparison_index and args.comparison_index_sha256 and args.resource_freeze and args.resource_freeze_sha256,
                 'Screen needs exact fresh comparison and prepublished resource freeze')
            comparison = control(args.comparison_index, args.comparison_index_sha256, 'compare')
            result = screen(noise, args.noise_index_sha256, comparison, load(args.resource_freeze, args.resource_freeze_sha256), args.resource_freeze_sha256)
            result['comparison_index_sha256'] = args.comparison_index_sha256
    except (OSError, ValueError, KeyError, TypeError, IndexError, OverflowError) as error:
        result.update(failure=type(error).__name__ + ': ' + str(error))
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'output': str(args.output), 'sha256': sha(args.output)}))
    return 0 if result['status'] == 'completed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
