#!/usr/bin/env python3
"""Read completed SQLite diagnostic receipts only; never execute a consumer."""
from pathlib import Path
import collections
import hashlib
import json

ROOT = Path('/workspace/scratch/4a65d70f0fe1')
DIRECTORY = ROOT / 'measurements/allocation-sqlite-01'
OUTPUT = ROOT / 'validation-evidence/allocation-sqlite-independent-audit.json'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


records = []
builds = {}
base_by_name = {}
totals = collections.Counter()
for path in sorted(DIRECTORY.glob('*.allocation.json')):
    data = json.loads(path.read_text())
    assert data['SchemaVersion'] == 1 and data['NativeAot'] is True
    assert data['TimingCredit'] is False and data['Failed'] is False
    base_path = Path(data['BaseReceiptPath'])
    assert base_path.parent == DIRECTORY and digest(base_path) == data['BaseReceiptSha256']
    base = json.loads(base_path.read_text())
    assert base['Scope'].startswith('ALLOCATION-INSTRUMENTED; TimingCredit=false.')
    assert base['NativeAot'] and base['Provider'] == 'Sqlite'
    assert base['ResultRows'] == data['ResultRows'] in [1, 100, 1000]
    assert base['ExecutableSha256'] == data['ExecutableSha256']
    build_path = Path(data['BuildReceiptPath'])
    assert digest(build_path) == data['BuildReceiptSha256']
    build = json.loads(build_path.read_text())
    assert build['status'] == 'built-not-run' and build['timingCredit'] is False
    assert build['executableSha256'] == data['ExecutableSha256']
    output = Path(build['output'])
    executable = output / 'out' / ('DbPerf.QueryPhases' if data['RouteFamily'] == 'korda' else 'DbPerf.DapperQueryPhases')
    assert digest(executable) == data['ExecutableSha256']
    assert executable.read_bytes()[:4] == b'\x7fELF'
    assert digest(Path(build['consumer']) / 'build-receipt.json') == build['inputBuildReceiptSha256']
    assert digest(base['NativePath']) == base['NativeSha256']
    if str(build_path) not in builds:
        for name, expected in build['instrumentedSources'].items():
            assert digest(output / name) == expected, name
        for name, hashes in build['generatedSources'].items():
            assert digest(output / 'generated-original' / name) == hashes['originalSha256'], name
            assert digest(output / 'generated-instrumented' / name) == hashes['instrumentedSha256'], name
        for command in build['commands']:
            assert command['exitCode'] == 0 and digest(output / command['log']) == command['logSha256']
        builds[str(build_path)] = {
            'sha256': data['BuildReceiptSha256'], 'executable': str(executable),
            'executableSha256': data['ExecutableSha256'], 'generatedFilesVerified': len(build['generatedSources']),
            'instrumentedSourceHashes': build['instrumentedSources'],
        }
    family = base_path.name.split('-rows')[0]
    expected_routes = {'fluent', 'prepared', 'host-sql'} if family != 'dapper' else {'dapper-aot'}
    assert set(w['Route'] for w in data['Windows']) == expected_routes
    assert len(data['Windows']) == len(base['Windows']) == 3 * len(expected_routes)
    originals = {(w['Route'], w['Index']): w for w in base['Windows']}
    route_totals = collections.defaultdict(collections.Counter)
    for window in data['Windows']:
        original = originals[(window['Route'], window['Index'])]
        operations = window['Operations']
        assert operations == original['Operations'] == 256
        assert window['RowsPerOperation'] == data['ResultRows']
        assert window['MapperCalls'] == window['ListAddCalls'] == operations * data['ResultRows']
        assert window['ListConstructorCalls'] == operations
        assert window['FrameworkOnlyBytes'] is None
        assert window['ObservedMapperAndListBytes'] == window['MapperBytes'] + window['ListConstructorBytes'] + window['ListAddBytes']
        assert window['ProcessAllocatedBefore'] == original['AllocatedBefore']
        assert window['ProcessAllocatedAfter'] == original['AllocatedAfter']
        assert window['ProcessAllocatedBytes'] == original['AllocatedAfter'] - original['AllocatedBefore'] >= 0
        assert len(original['Samples']) == operations
        assert all(sample['Rows'] == data['ResultRows'] for sample in original['Samples'])
        for generation in range(3):
            assert window[f'ProcessGen{generation}'] == original[f'Gen{generation}'] >= 0
        if family != 'dapper':
            assert original['NativeAfter']['SqlExecutions'] - original['NativeBefore']['SqlExecutions'] == operations
            for label in ['NativeBefore', 'NativeAfter']:
                assert all(original[label][name] == 0 for name in ['Operations', 'Cursors', 'Buffers'])
                if family == 'candidate':
                    assert original[label]['PullChannels'] == 0
        aggregate = route_totals[window['Route']]
        for field in ['Operations', 'MapperCalls', 'ListConstructorCalls', 'ListAddCalls', 'MapperBytes',
                      'ListConstructorBytes', 'ListAddBytes', 'ObservedMapperAndListBytes',
                      'ProcessAllocatedBytes', 'ProcessGen0', 'ProcessGen1', 'ProcessGen2']:
            aggregate[field] += window[field]
        totals['windows'] += 1
        totals['operations'] += operations
        totals['mapperCalls'] += window['MapperCalls']
        totals['listConstructors'] += window['ListConstructorCalls']
        totals['listAdds'] += window['ListAddCalls']
    if family == 'dapper':
        assert base['ConnectionClosed'] is True
        contract = base['Contract']
        assert digest(contract['KordaReceiptPath']) == contract['KordaReceiptSha256']
        assert base['Sql'] == base['RawTemplate'] == contract['RawTemplate']
    else:
        assert all(base['Drained'][key] == 0 for key in ['Sources', 'Sessions', 'Operations', 'Cursors', 'Buffers', 'Owners'])
        if family == 'candidate':
            assert base['Drained']['PullChannels'] == 0
    base_by_name[(family, data['ResultRows'])] = base
    records.append({
        'file': str(path), 'sha256': digest(path), 'baseReceipt': str(base_path),
        'baseReceiptSha256': data['BaseReceiptSha256'], 'family': family, 'rows': data['ResultRows'],
        'routes': {route: dict(values) for route, values in route_totals.items()},
        'allDeclaredInvariantsPassed': True,
    })
assert len(records) == 9
for rows in [1, 100, 1000]:
    before, candidate, dapper = [base_by_name[(family, rows)] for family in ['before', 'candidate', 'dapper']]
    assert before['Sql'] == candidate['Sql'] == dapper['Contract']['KordaSql']
    assert before['RawTemplate'] == candidate['RawTemplate'] == dapper['Sql']

# The completed, hash-bound source executes these row/order/nullable-field checks
# before recording a successful sample. Retain the exact source proof separately
# from the JSON sample-count evidence; there is no invented per-row digest field.
oracle_files = []
for directory, name in [('allocation-before-sqlite-05', 'Program.cs'),
                        ('allocation-candidate-sqlite', 'Program.cs'),
                        ('allocation-dapper-sqlite-05', 'PhaseProbe.cs')]:
    path = ROOT / 'consumers' / directory / name
    text = path.read_text()
    assert 'rows[i].Id != i + 1 || rows[i].Note != _notes[tenant - 1][i]' in text
    assert 'id % 5 == 0 ? null : $"note-{tenant}-{id}"' in text
    assert 'if (rows.Count != ' in text and 'throw new InvalidOperationException("Incomplete result.")' in text
    oracle_files.append({'path': str(path), 'sha256': digest(path),
                         'checks': ['exact full count', 'Id ascending position', 'tenant-specific Note', 'every fifth Note is null']})
report = {
    'scope': 'Independent read-only SQLite allocation receipt/source/hash audit; no build, test or consumer execution',
    'scriptSha256': digest(__file__),
    'status': 'passed', 'files': len(records), 'totals': dict(totals),
    'timingCredit': False, 'frameworkOnlyBytes': None,
    'gcScope': 'Original process-wide GC.CollectionCount deltas in each measured window, matched exactly; not per-thread and not a reconstructed whole-lifetime total including setup/warmup gaps',
    'resultOracleEvidence': 'All sample counts and operations checked; completed hash-bound original source performs per-row Id/order/Note/null assertions before reporting success. JSON contains no independent per-row digest.',
    'builds': builds, 'oracleSources': oracle_files, 'records': records,
    'postgresAllocationRead': False,
}
OUTPUT.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'status': report['status'], 'files': len(records), 'totals': dict(totals),
                  'report': str(OUTPUT), 'reportSha256': digest(OUTPUT)}))
for record in records:
    print(record['family'], record['rows'], {route: {
        'scopeBytesPerOp': values['ObservedMapperAndListBytes'] / values['Operations'],
        'processBytesPerOp': values['ProcessAllocatedBytes'] / values['Operations'],
        'processGC': [values[f'ProcessGen{i}'] for i in range(3)],
    } for route, values in record['routes'].items()})
