#!/usr/bin/env python3
"""Apply the committed prospective two-round close selection, without retries."""
import argparse
import hashlib
import json
import math
from pathlib import Path

OWNERS = ('Sources', 'Sessions', 'Operations', 'Cursors', 'Buffers', 'Owners', 'PullChannels', 'CommandCompletions')
PHASES = ('ConstructTicks', 'SubmitToFirstRowTicks', 'ReadCompleteTicks', 'ReleaseTicks')
COMMITS = {'before': '17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa',
           'candidate': '92b923075952bac347619ee7817c372ee6e415cb'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--measurements', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists()
    inputs, raw, rounds, pooled = {}, {}, [], []

    def read(path):
        data = path.read_bytes()
        inputs[str(path)] = hashlib.sha256(data).hexdigest()
        return json.loads(data)

    def q(values):
        values = sorted(values)
        return {f'p{p}Microseconds': values[math.ceil(len(values) * p / 100) - 1]
                for p in (50, 95, 99)} | {'samples': len(values)}

    for number in (1, 2):
        report = read(args.measurements / f'close-paired-analysis-r{number}')
        assert not report['inputsChangedDuringAnalysis']
        assert len(report['observations']) == 18 and all(x['timingCredit'] and not x['issues'] for x in report['observations'])
        assert all(x['comparableRecordedContract'] for x in report['phaseComparisons'])
        for provider in ('sqlite', 'postgresql'):
            for rows in (1, 100, 1000):
                comparison = {'round': number, 'provider': provider, 'rows': rows, 'routes': {}}
                for role in ('before', 'candidate'):
                    receipt = read(args.measurements / f'close-paired-{provider}-r{number}' / f'{role}-rows{rows}.json')
                    assert receipt['PackageVersion'].endswith('+' + COMMITS[role])
                    assert all(type(receipt['Drained'][key]) is int and receipt['Drained'][key] == 0 for key in OWNERS)
                    windows = [x for x in receipt['Windows'] if x['Route'] == 'prepared']
                    assert len(windows) == 3 and all(x['Operations'] == 256 for x in windows)
                    samples = [sample for w in windows for sample in w['Samples']]
                    assert len(samples) == 768 and all(x['Rows'] == rows for x in samples)
                    scale = 1_000_000 / receipt['StopwatchFrequency']
                    values = {'total': [sum(s[key] for key in PHASES) * scale for s in samples],
                              'readComplete': [s['ReadCompleteTicks'] * scale for s in samples]}
                    raw[number, provider, rows, role] = values
                    comparison['routes'][role] = {name: q(items) for name, items in values.items()}
                ratio = comparison['routes']['candidate']['readComplete']['p50Microseconds'] / comparison['routes']['before']['readComplete']['p50Microseconds']
                comparison['readCompleteP50Ratio'] = ratio
                comparison['singleRowGate'] = ratio <= 0.90 if rows == 1 else None
                rounds.append(comparison)
    for provider in ('sqlite', 'postgresql'):
        for rows in (1, 100, 1000):
            item = {'provider': provider, 'rows': rows, 'routes': {}}
            for role in ('before', 'candidate'):
                item['routes'][role] = {name: q(raw[1, provider, rows, role][name] + raw[2, provider, rows, role][name])
                                        for name in ('total', 'readComplete')}
            ratio = item['routes']['candidate']['total']['p50Microseconds'] / item['routes']['before']['total']['p50Microseconds']
            item.update(totalP50Ratio=ratio, nonRegressionGate=ratio <= 1.05)
            pooled.append(item)
    unchanged = all(hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest for path, digest in inputs.items())
    assert unchanged
    selected = all(x['singleRowGate'] is not False for x in rounds) and all(x['nonRegressionGate'] for x in pooled)
    result = {'schemaVersion': 1, 'ruleCommit': '9d1d072', 'commits': COMMITS,
              'selected': selected, 'selectedCommit': COMMITS['candidate' if selected else 'before'],
              'method': 'Nearest rank; all 768 samples per round and all 1536 pooled samples; per-sample totals, no sum of percentiles.',
              'scope': 'Narrow ordinary short selection only; no final acceptance, exact dispatch-cost attribution or framework-only allocation claim.',
              'rounds': rounds, 'pooled': pooled, 'inputs': inputs, 'inputsUnchanged': unchanged}
    with args.output.open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
