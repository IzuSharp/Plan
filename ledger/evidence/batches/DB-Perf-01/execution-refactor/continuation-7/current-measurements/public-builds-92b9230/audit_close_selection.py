#!/usr/bin/env python3
"""Independently recompute the precommitted close selection from raw phase ticks."""
import argparse
import datetime
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess

COMMITS = {'before': '17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa',
           'candidate': '92b923075952bac347619ee7817c372ee6e415cb'}
OWNERS = ('Sources', 'Sessions', 'Operations', 'Cursors', 'Buffers', 'Owners', 'PullChannels', 'CommandCompletions')
PHASES = ('ConstructTicks', 'SubmitToFirstRowTicks', 'ReadCompleteTicks', 'ReleaseTicks')


def require(value, why):
    if not value:
        raise ValueError(why)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurements', type=Path, required=True)
    parser.add_argument('--plan-repository', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); require(not args.output.exists(), 'Never overwrite evidence')
    inputs = {}
    def read(path, expected=None):
        data = path.read_bytes(); actual = hashlib.sha256(data).hexdigest()
        require(expected is None or expected == actual, 'Input differs: ' + str(path))
        inputs[str(path)] = actual
        return json.loads(data)
    selection_path = args.measurements / 'close-paired-selection-01.json'
    selection = read(selection_path)
    require(selection['commits'] == COMMITS and selection['ruleCommit'] == '9d1d072'
            and selection['inputsUnchanged'] is True, 'Wrong selection source or rule')
    git_info = subprocess.check_output(['git', '-C', str(args.plan_repository), 'show', '-s', '--format=%H%n%cI', '9d1d072'], text=True).splitlines()
    rule_path = 'ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/close-quiet-experiment.md'
    rule = subprocess.check_output(['git', '-C', str(args.plan_repository), 'show', git_info[0] + ':' + rule_path])
    require(b'at least 10%' in rule and b'no more than 5%' in rule and b'no automatic extra retries' in rule, 'Prospective rule changed')
    samples, round_results, pooled_results, starts, observed = {}, [], [], [], 0
    def quantiles(values):
        ordered = sorted(values)
        return {f'p{percent}Microseconds': float(ordered[(len(ordered) * percent + 99) // 100 - 1])
                for percent in (50, 95, 99)} | {'samples': len(ordered)}
    def compare_stats(actual, stored):
        require(actual.keys() == stored.keys(), 'Statistic inventory differs')
        for key in actual:
            require(math.isclose(actual[key], stored[key], rel_tol=0, abs_tol=1e-8), 'Statistic differs: ' + key)
    for number in (1, 2):
        report_path = args.measurements / f'close-paired-analysis-r{number}'
        report = read(report_path, selection['inputs'][str(report_path)])
        require(report['inputsChangedDuringAnalysis'] == [] and len(report['observations']) == 18,
                'Arithmetic inputs changed or observations missing')
        require(all(x['timingCredit'] is True and x['final'] is False and x['issues'] == []
                    for x in report['observations']), 'Ineligible ordinary phase observation')
        require(all(x['comparableRecordedContract'] is True for x in report['phaseComparisons']), 'Contract differs')
        observed += len(report['observations'])
        starts += [x['invocation']['record']['startedUtc'] for x in report['observations']]
        for provider in ('sqlite', 'postgresql'):
            for rows in (1, 100, 1000):
                item = {'round': number, 'provider': provider, 'rows': rows, 'routes': {}}
                for role, commit in COMMITS.items():
                    path = args.measurements / f'close-paired-{provider}-r{number}' / f'{role}-rows{rows}.json'
                    raw = read(path, selection['inputs'][str(path)])
                    require(raw['PackageVersion'] == '0.1.0-ci.1+' + commit, 'Wrong measured product commit')
                    require(all(type(raw['Drained'][name]) is int and raw['Drained'][name] == 0 for name in OWNERS), 'Owner did not drain')
                    frequency = raw['StopwatchFrequency']; require(type(frequency) is int and frequency > 0, 'Bad timer frequency')
                    windows = [w for w in raw['Windows'] if w['Route'] == 'prepared']
                    require(len(windows) == 3 and {w['Index'] for w in windows} == {0, 1, 2}, 'Prepared window inventory differs')
                    require(all(w['Operations'] == 256 and len(w['Samples']) == 256 for w in windows), 'Prepared sample count differs')
                    values = {'total': [], 'readComplete': []}
                    for window in windows:
                        for sample in window['Samples']:
                            require(type(sample['Rows']) is int and sample['Rows'] == rows, 'Partial result')
                            require(all(type(sample[key]) is int and sample[key] >= 0 for key in PHASES), 'Bad phase ticks')
                            values['total'].append(Fraction(sum(sample[key] for key in PHASES) * 1_000_000, frequency))
                            values['readComplete'].append(Fraction(sample['ReadCompleteTicks'] * 1_000_000, frequency))
                    samples[number, provider, rows, role] = values
                    item['routes'][role] = {name: quantiles(v) for name, v in values.items()}
                ratio = item['routes']['candidate']['readComplete']['p50Microseconds'] / item['routes']['before']['readComplete']['p50Microseconds']
                item.update(readCompleteP50Ratio=ratio, singleRowGate=ratio <= 0.90 if rows == 1 else None)
                stored = next(x for x in selection['rounds'] if (x['round'], x['provider'], x['rows']) == (number, provider, rows))
                for role in COMMITS:
                    for name in ('total', 'readComplete'):
                        compare_stats(item['routes'][role][name], stored['routes'][role][name])
                require(item['singleRowGate'] is stored['singleRowGate'], 'Round gate differs')
                round_results.append(item)
    for provider in ('sqlite', 'postgresql'):
        for rows in (1, 100, 1000):
            item = {'provider': provider, 'rows': rows, 'routes': {}}
            for role in COMMITS:
                item['routes'][role] = {name: quantiles(samples[1, provider, rows, role][name] + samples[2, provider, rows, role][name])
                                        for name in ('total', 'readComplete')}
            ratio = item['routes']['candidate']['total']['p50Microseconds'] / item['routes']['before']['total']['p50Microseconds']
            item.update(totalP50Ratio=ratio, nonRegressionGate=ratio <= 1.05)
            stored = next(x for x in selection['pooled'] if (x['provider'], x['rows']) == (provider, rows))
            for role in COMMITS:
                for name in ('total', 'readComplete'):
                    compare_stats(item['routes'][role][name], stored['routes'][role][name])
            require(item['nonRegressionGate'] is stored['nonRegressionGate'], 'Pooled gate differs')
            pooled_results.append(item)
    selected = all(x['singleRowGate'] is not False for x in round_results) and all(x['nonRegressionGate'] for x in pooled_results)
    require(selected is selection['selected'] is False and selection['selectedCommit'] == COMMITS['before'], 'Selection decision differs')
    first = min(datetime.datetime.fromisoformat(t.replace('Z', '+00:00')) for t in starts)
    require(datetime.datetime.fromisoformat(git_info[1]) < first, 'Rule commit did not precede measurements')
    require(all(hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected for path, expected in inputs.items()), 'Input changed')
    result = {'schemaVersion': 1, 'status': 'passed', 'scope': __doc__,
              'scriptSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'checkedUtc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'rule': {'commit': git_info[0], 'committedUtc': git_info[1], 'path': rule_path, 'sha256': hashlib.sha256(rule).hexdigest()},
              'firstMeasuredStartUtc': first.isoformat(), 'observationsTimingEligible': observed,
              'rounds': round_results, 'pooled': pooled_results, 'selected': selected, 'selectedCommit': COMMITS['before'],
              'candidateCorrectnessPassed': True, 'candidatePerformanceRejected': True,
              'earlier0aaTimedInThisPair': False, 'earlier0aaNotTimedBeforeThisPair': 'Root continuation record; no earlier timing is reassigned here.',
              'inputs': inputs, 'inputsUnchanged': True, 'binaryHashSweep': False,
              'productExecutions': 0, 'performanceAcceptanceCredit': False}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('rounds', 'pooled', 'inputs')}))


if __name__ == '__main__':
    main()
