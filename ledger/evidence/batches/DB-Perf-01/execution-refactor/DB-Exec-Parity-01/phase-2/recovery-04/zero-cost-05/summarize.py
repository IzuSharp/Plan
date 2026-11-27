#!/usr/bin/env python3
"""Summarize the frozen mixed35 zero-rejection cells without rerunning them."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
plan = json.loads((HERE / 'series-01.plan.json').read_text())
state = json.loads((HERE / 'series-01.plan.resume.json').read_text())
assert state['passed'] is True and state['stage'] == 'completed'
assert len(state['cells']) == len(plan['cells']) == 12
rows = []
for entry, receipt in zip(plan['cells'], state['cells']):
    assert entry['id'] == receipt['id'] and receipt['passed'] is True
    path = Path(entry['output']) / 'validation.json'
    assert hashlib.sha256(path.read_bytes()).hexdigest() == receipt['validationSha256']
    v = json.loads(path.read_text())
    c, r = v['normalized']['counts'], v['resources']
    assert c['planned'] == c['succeeded'] == 15000 and c['rejected'] == c['failed'] == c['retries'] == 0
    pg = r['postgres']
    server = None if pg is None else {
        side: sum(pg['visibleSteadyIntervals'][side][k] for k in ('userCpuSecondsObserved', 'systemCpuSecondsObserved'))
        for side in ('inner', 'outer')}
    rows.append({'id': entry['id'], 'provider': entry['provider'], 'variant': entry['variant'],
                 'round': int(entry['id'].split('-')[1]), 'validationSha256': receipt['validationSha256'],
                 'counts': c, 'throughput': v['normalized']['successOpsPerSecond'],
                 'clientCpuMicrosecondsPerSuccess': r['clientCpuSecondsPerSuccess'] * 1e6,
                 'managedBytesPerSuccess': r['managedBytesPerSuccess'], 'quantiles': v['quantiles'],
                 'peakRssBytes': r['peakRssThroughMeasurementBytes'], 'releasedIdleRssBytes': r['releasedIdleRssBytes'],
                 'gcCountsProcessScope': r['gcCountsProcessScope'], 'gcPauseSecondsProcessScope': r['gcPauseSecondsProcessScope'],
                 'postgresObservedIntervalCpuSeconds': server, 'postgresExactSteadyCpuProven': False if pg else None,
                 'nativeAllocationProfile': None, 'frameworkOnlyManagedBytes': None})
pairs = []
for provider in ('sqlite', 'postgresql'):
    for round_no in (1, 2):
        group = {r['variant']: r for r in rows if r['provider'] == provider and r['round'] == round_no}
        a, b, d = (group[k] for k in ('candidate', 'before', 'dapper'))
        comparison = {'provider': provider, 'round': round_no}
        for name in ('clientCpuMicrosecondsPerSuccess', 'managedBytesPerSuccess', 'peakRssBytes', 'releasedIdleRssBytes'):
            comparison[name] = {'candidate': a[name], 'before': b[name], 'dapper': d[name],
                                'candidateVsBeforePercent': (a[name] / b[name] - 1) * 100,
                                'candidateVsDapperRatio': a[name] / d[name]}
        for boundary in ('service', 'scheduled'):
            comparison[boundary] = {
                q: {'candidate': a['quantiles'][boundary][q], 'before': b['quantiles'][boundary][q],
                    'dapper': d['quantiles'][boundary][q],
                    'candidateVsBeforePercent': (a['quantiles'][boundary][q] / b['quantiles'][boundary][q] - 1) * 100}
                for q in ('p50MicrosecondsUpper', 'p95MicrosecondsUpper', 'p99MicrosecondsUpper')}
        pairs.append(comparison)
result = {'task': 'DB-Exec-Parity-01', 'passed': True, 'ordinaryTiming': True, 'finalCredit': False,
          'conditions': {'secondsPerCell': 30, 'offeredRate': 500, 'queue': 64, 'sqliteConcurrency': 4,
                         'postgresqlConcurrency': 8, 'warmupPerWorker': '35-case verification plus 64, outside measurement',
                         'rows': 32, 'batchRows': 32, 'idleSecondsAfterOwnerRelease': 5},
          'cellCount': len(rows), 'successes': sum(r['counts']['succeeded'] for r in rows),
          'rows': sum(r['counts']['rows'] for r in rows), 'rejections': 0, 'businessErrors': 0,
          'cells': rows, 'pairedComparisons': pairs,
          'limitations': ['500/s is an offered rate with zero refusal in these finite cells, not a sustainable-capacity claim.',
                          'Process CPU includes the dedicated db-perf-arrivals producer, whose WaitUntil spins for remaining delays <=2 ms, plus harness, driver, framework and DTO work; do not blindly subtract its theoretical budget.',
                          'All allocation totals are process scope; framework-only 0 B and native allocation are unproven here.',
                          'Two reversed rounds expose direction/variation, not confidence intervals or long-duration acceptance.',
                          'PostgreSQL observed inner/outer CPU endpoints are non-atomic visible-process observations, not exact bounds; lifetime wait4 remains separately retained in each validation.',
                          'First SQLite candidate used preserved wrapper v1; subsequent cells used v2 interruption/lease controls with identical ordinary measurement commands.']}
(HERE / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'passed': True, 'cells': len(rows), 'successes': result['successes'], 'rows': result['rows'],
                  'cpuPairs': [dict(provider=x['provider'], round=x['round'], **x['clientCpuMicrosecondsPerSuccess']) for x in pairs]}, indent=2))
