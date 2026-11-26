#!/usr/bin/env python3
"""Summarize observed allocation scopes without unsupported attribution."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = {
    'scope': 'Diagnostic only; native is public allocator process scope, mapper includes codec/driver scratch; no framework subtraction',
    'mapper': [], 'native': [], 'passed': True,
}
for p in sorted((root / 'measurements/mapper-allocation-baseline-01').glob('*/*.json.allocation.json')):
    j = json.loads(p.read_text())
    assert j['TimingCredit'] is False and not j['Failed']
    for w in j['Windows']:
        n = w['Operations']
        out['mapper'].append({
            'provider': p.parent.name, 'route': w['Route'], 'rows': j['ResultRows'], 'operations': n,
            'mapperCallsPerOperation': w['MapperCalls'] / n,
            'mapperBytesPerOperation': w['MapperBytes'] / n,
            'listConstructorBytesPerOperation': w['ListConstructorBytes'] / n,
            'listAddBytesPerOperation': w['ListAddBytes'] / n,
            'processBytesPerOperation': w['ProcessAllocatedBytes'] / n,
            'FrameworkOnlyBytes': w['FrameworkOnlyBytes'],
            'receipt': str(p.relative_to(root)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
        })
paths = sorted((root / 'measurements/native-allocation-baseline-01').glob('*/*-korda.json'))
paths += sorted((root / 'measurements/native-allocation-baseline-01').glob('*/*-dapper.json'))
for p in paths:
    j = json.loads(p.read_text())
    v = j['NativeAllocationProfile']
    assert v['passed'] and v['preloadedGlobalAllocatorIdentityVerified'] and not j['TimingComparisonEligible']
    assert j['Completed'] == 128 and j['Failed'] == 0 and j['OracleFailures'] == 0
    if j['Route'].startswith('korda'):
        assert j['OwnersReturnedToZero']
    n = j['Completed']
    out['native'].append({
        'provider': p.parent.name, 'cell': p.stem, 'operations': n,
        'allocationCallsPerOperation': v['allocationCalls'] / n,
        'requestedBytesPerOperation': v['allocatedRequestedBytes'] / n,
        'releasedBytesPerOperation': v['releasedRequestedBytes'] / n,
        'liveAfterDrainBytes': v['afterDrain']['live_requested_bytes'],
        'managedProcessBytesPerOperation': j['BytesPerSuccessfulOperation'],
        'FrameworkOnlyBytes': None, 'receipt': str(p.relative_to(root)),
        'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
    })
assert len(out['mapper']) == 24
assert len(out['native']) == 140
(root / 'analysis/allocation-baseline-01.json').write_text(json.dumps(out, indent=2) + '\n')
print('Mapper windows:', len(out['mapper']), 'native cells:', len(out['native']), 'passed:', out['passed'])
for row in out['mapper']:
    if row['rows'] == 1000:
        print(row['provider'], row['route'], 'mapper B/op', row['mapperBytesPerOperation'], 'list B/op', row['listConstructorBytesPerOperation'], 'process B/op', row['processBytesPerOperation'])
for row in out['native']:
    if any(t in row['cell'] for t in ['numeric', 'text', 'wide', 'tx-commit']):
        print(row['provider'], row['cell'], 'native alloc/op', row['allocationCallsPerOperation'], 'native B/op', row['requestedBytesPerOperation'])
