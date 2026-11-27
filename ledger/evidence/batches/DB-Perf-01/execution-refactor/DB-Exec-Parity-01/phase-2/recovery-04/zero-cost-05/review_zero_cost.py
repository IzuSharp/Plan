#!/usr/bin/env python3
"""Independent lightweight reconciliation of already completed zero-cost cells."""
from pathlib import Path
import datetime
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
checks, inputs = [], []


def read(path):
    data = path.read_bytes()
    inputs.append({'path': str(path.relative_to(ROOT)), 'bytes': len(data),
                   'sha256': hashlib.sha256(data).hexdigest()})
    return json.loads(data)


def check(name, value):
    checks.append({'name': name, 'passed': bool(value)})
    if not value:
        raise AssertionError(name)


def close(a, b):
    return math.isclose(a, b, rel_tol=1e-11, abs_tol=1e-9)


def quantile(histogram, percent):
    target = math.ceil(sum(histogram) * percent / 100)
    seen = 0
    for i, count in enumerate(histogram):
        seen += count
        if seen >= target:
            lower = 2 ** (i // 128)
            return (lower + lower * ((i % 128 + 1) / 128)) / 1000
    raise AssertionError('Missing histogram quantile')


def utc(text):
    return datetime.datetime.fromisoformat(text)


plan = read(HERE / 'series-01.plan.json')
state = read(HERE / 'series-01.plan.resume.json')
summary = read(HERE / 'summary.json')
check('controller completed 12 passing cells', state['stage'] == 'completed' and state['passed']
      and len(state['cells']) == len(plan['cells']) == len(summary['cells']) == 12)
check('controller plan identity', state['planSha256'] == inputs[0]['sha256'])
check('controller order equals plan', [x['id'] for x in state['cells']] == [x['id'] for x in plan['cells']])
check('controller sequential lifetime order', all(utc(a['finishedUtc']) <= utc(b['startedUtc'])
      for a, b in zip(state['cells'], state['cells'][1:])))
check('first cell reused exactly once', state['cells'][0]['reusedCompletedEvidence'] is True
      and sum(bool(x.get('reusedCompletedEvidence')) for x in state['cells']) == 1)
check('no final acceptance credit', summary['ordinaryTiming'] and not summary['finalCredit']
      and not state['finalCredit'] and not plan['finalCredit'])

summary_cells = {x['id']: x for x in summary['cells']}
rows, canonical_cases, oracles = [], None, {}
actual_identities = {}
for entry, controller in zip(plan['cells'], state['cells']):
    label = entry['id']
    folder = Path(entry['output'])
    v = read(folder / 'validation.json')
    validation_sha = inputs[-1]['sha256']
    raw = read(folder / 'measurement/result.json')
    raw_sha = inputs[-1]['sha256']
    s = summary_cells[label]
    c, resource, condition = v['normalized']['counts'], v['resources'], v['conditions']
    local_check = lambda name, value: check(label + ': ' + name, value)
    local_check('controller and summary bind actual validation', validation_sha == controller['validationSha256'] == s['validationSha256'])
    local_check('validation binds actual raw', v['rawFiles'][str(folder / 'measurement/result.json')]['sha256'] == raw_sha)
    local_check('completed ordinary eligible screening', controller['passed'] and controller['exitCode'] == 0 and v['passed']
                and v['ordinaryTiming'] and raw['TimingComparisonEligible'] and raw['NativeAot']
                and not v['finalCredit'] and not v['newFinalCellCredit'] and v['freeze'] is None)
    local_check('conditions match planned cost lane', condition['provider'] == entry['provider']
                and condition['seconds'] == 30 and condition['rate'] == 500 and condition['queue'] == 64
                and condition['idle'] == 5 and condition['warmup'] == 64 and condition['rows'] == condition['batchRows'] == 32
                and condition['tenants'] == 8 and condition['ordersPerTenant'] == 1024
                and condition['mode'] == 'prepared' and condition['session'] == 'persistent'
                and condition['concurrency'] == (4 if entry['provider'] == 'sqlite' else 8))
    local_check('inputs unchanged across cell', v['prePostInputIdentitiesEqual'])
    local_check('complete zero-error ledger', all(c[k] == 15000 for k in ['planned','attempted','sent','started','completed','succeeded'])
                and all(c[k] == 0 for k in ['failed','rejected','retries']) and c['rows'] == 366067
                and raw['Errors'] == raw['OfferedLoad']['Errors'] == [] and raw['OracleFailures'] == 0)
    local_check('raw/controller/summary counts agree', c == controller['counts'] == s['counts']
                and raw['Started'] == raw['Completed'] == 15000 and raw['Rows'] == c['rows'])
    ids, cases = raw['ActualCaseIds'], raw['Cases']
    if canonical_cases is None:
        canonical_cases = ids
    local_check('all 35 case IDs and contracts', len(ids) == len(set(ids)) == 35 and ids == canonical_cases
                and [x['Name'] for x in cases] == ids and set(raw['ExpectedResults']) == set(ids)
                and set(raw['CaseModeContracts']) == set(ids) and v['normalized']['fullCaseCoverage']
                and not v['normalized']['missingExecutedCaseIds'])
    local_check('case success and row aggregation', all(428 <= x['Succeeded'] <= 429 and x['Failed'] == 0
                and x['Rows'] == x['Succeeded'] * raw['ExpectedResults'][x['Name']]['Rows'] for x in cases)
                and sum(x['Succeeded'] for x in cases) == c['succeeded'] and sum(x['Rows'] for x in cases) == c['rows'])
    oracle = {k: (x['Rows'], int(x['Digest'])) for k, x in raw['ExpectedResults'].items()}
    if entry['provider'] not in oracles:
        oracles[entry['provider']] = oracle
    local_check('same provider business oracles across all variants and rounds', oracle == oracles[entry['provider']])
    before, after = raw['ProcessBefore'], raw['ProcessAfter']
    user = after['UserCpuSeconds'] - before['UserCpuSeconds']
    system = after['SystemCpuSeconds'] - before['SystemCpuSeconds']
    cpu_us = (user + system) / c['succeeded'] * 1e6
    allocated = raw['AllocatedAfter'] - raw['AllocatedBefore']
    bytes_per_op = allocated / c['succeeded']
    pause = (after['TotalGcPauseTicks'] - before['TotalGcPauseTicks']) / 10000000
    local_check('client process CPU arithmetic', close(user, raw['UserCpuSeconds']) and close(system, raw['SystemCpuSeconds'])
                and close(cpu_us, resource['clientCpuSecondsPerSuccess'] * 1e6)
                and close(cpu_us, s['clientCpuMicrosecondsPerSuccess'])
                and close(cpu_us, controller['cpuSecondsPerSuccess'] * 1e6))
    local_check('managed process allocation arithmetic', allocated == raw['AllocatedBytes'] == resource['managedAllocatedBytes']
                and close(bytes_per_op, resource['managedBytesPerSuccess']) and close(bytes_per_op, s['managedBytesPerSuccess'])
                and close(bytes_per_op, controller['managedBytesPerSuccess']))
    local_check('GC process delta and counts', close(pause, resource['gcPauseSecondsProcessScope'])
                and close(pause, s['gcPauseSecondsProcessScope'])
                and {k: raw[k] for k in ('Gen0','Gen1','Gen2')} == resource['gcCountsProcessScope'] == s['gcCountsProcessScope'])
    local_check('peak/idle RSS and idle interval', after['PeakRssBytes'] == resource['peakRssThroughMeasurementBytes'] == s['peakRssBytes']
                and raw['Idle']['After']['RssBytes'] == resource['releasedIdleRssBytes'] == s['releasedIdleRssBytes']
                and raw['Idle']['RequestedSeconds'] == 5 and raw['Idle']['ObservedSeconds'] >= 4.99)
    owner_keys = ('ApplicationConnections',) if entry['variant'] == 'dapper' else (
        'Sources','Sessions','Operations','Cursors','Buffers','Owners','PullChannels','CommandCompletions')
    local_check('tracked owners drained', all(raw['Drained'][key] == 0 for key in owner_keys))
    local_check('native/framework-only allocation explicitly unknown', raw['NativeAllocationProfile'] is None
                and resource['nativeAllocationProfile'] is None and resource['frameworkOnlyManagedBytes'] is None
                and s['nativeAllocationProfile'] is None and s['frameworkOnlyManagedBytes'] is None)
    quantiles = {}
    for name, key in [('service','SuccessServiceHistogram'),('scheduled','SuccessScheduledHistogram'),('startDelay','StartDelayHistogram')]:
        histogram = raw['OfferedLoad'][key]
        local_check(name + ' histogram contains all successes', sum(histogram) == 15000)
        quantiles[name] = {'p' + str(p) + 'MicrosecondsUpper': quantile(histogram, p) for p in (50,95,99)}
        local_check(name + ' quantile reconstruction', all(close(value, v['quantiles'][name][q])
                    and close(value, s['quantiles'][name][q]) for q, value in quantiles[name].items()))
    local_check('service and outer histogram are the same', raw['Latencies']['Histogram'] == raw['OfferedLoad']['SuccessServiceHistogram'])
    local_check('no time-series truncation', not raw['TimeSeriesTruncated'] and not raw['OfferedLoad']['TimeSeriesTruncated'])
    identity = (raw['ExecutableSha256'], raw['LoadedNativeSha256'], raw['PackageVersion'], raw['Route'])
    identity_key = (entry['provider'], entry['variant'])
    if identity_key not in actual_identities:
        actual_identities[identity_key] = identity
    local_check('actual ELF/native/package identity stable between rounds', identity == actual_identities[identity_key])
    pg = resource['postgres']
    server = None
    if entry['provider'] == 'postgresql':
        intervals = pg['visibleSteadyIntervals']
        local_check('PG non-exact scope and endpoints available', pg['observedInnerOuterAvailable']
                    and pg['exactSteadyCpuProven'] is False and intervals['exactSteadyCpuProven'] is False
                    and pg['unobservedExitedChildrenOrNonAtomicTransferLoss'] == 'unknown')
        server = {'observed': {}, 'wait4LifetimeUserPlusSystemSeconds': sum(pg['wait4Lifetime'][k] for k in ('processLifetimeUserCpuSeconds','processLifetimeSystemCpuSeconds')),
                  'exactSteadyCpuProven': False}
        for side in ('inner','outer'):
            endpoint = intervals[side]
            ticks = intervals['ticksPerSecond']
            user_delta = (endpoint['lastCounters']['ownAndReapedUserTicks'] - endpoint['firstCounters']['ownAndReapedUserTicks']) / ticks
            system_delta = (endpoint['lastCounters']['ownAndReapedSystemTicks'] - endpoint['firstCounters']['ownAndReapedSystemTicks']) / ticks
            local_check('PG ' + side + ' endpoint arithmetic', endpoint['allObservedCountersMonotonic']
                        and close(user_delta, endpoint['userCpuSecondsObserved']) and close(system_delta, endpoint['systemCpuSecondsObserved'])
                        and close(user_delta + system_delta, s['postgresObservedIntervalCpuSeconds'][side]))
            server['observed'][side] = user_delta + system_delta
    else:
        local_check('SQLite has no separate server CPU', pg is None and s['postgresObservedIntervalCpuSeconds'] is None)
    rows.append({'id': label, 'provider': entry['provider'], 'variant': entry['variant'], 'round': int(label.split('-')[1]),
        'counts': c, 'validationSha256': validation_sha, 'rawSha256': raw_sha, 'conditions': condition,
        'inputIdentitySha256': v['inputIdentitySha256'], 'actualArtifactIdentity': identity,
        'actualSteadyStartMonotonicNs': v['normalized']['steadyStartMonotonicNs'], 'actualDrainedMonotonicNs': v['normalized']['drainedMonotonicNs'],
        'cpuMicrosecondsPerSuccess': cpu_us, 'managedBytesPerSuccess': bytes_per_op, 'gcPauseSecondsProcessScope': pause,
        'gcCountsProcessScope': resource['gcCountsProcessScope'], 'peakRssBytes': after['PeakRssBytes'],
        'releasedIdleRssBytes': raw['Idle']['After']['RssBytes'], 'quantiles': quantiles, 'postgres': server})

check('actual measured windows do not overlap', all(a['actualDrainedMonotonicNs'] <= b['actualSteadyStartMonotonicNs'] for a,b in zip(rows,rows[1:])))
check('all variants have the same oracles in both databases', oracles['sqlite'] == oracles['postgresql'])
totals = {k: sum(r['counts'][k] for r in rows) for k in rows[0]['counts']}
check('summary aggregate counts', totals['succeeded'] == 180000 == summary['successes'] and totals['rows'] == 4392804 == summary['rows']
      and totals['rejected'] == summary['rejections'] == 0 and totals['failed'] == summary['businessErrors'] == 0 and totals['retries'] == 0)
pair_index = {(x['provider'],x['round']): x for x in summary['pairedComparisons']}
pairs = []
for provider in ('sqlite','postgresql'):
    for round_no in (1,2):
        group = {r['variant']: r for r in rows if r['provider'] == provider and r['round'] == round_no}
        a,b,d = (group[k] for k in ('candidate','before','dapper'))
        original = pair_index[(provider,round_no)]
        pair = {'provider': provider, 'round': round_no, 'metrics': {}, 'quantiles': {}}
        for metric, key in [('cpuMicrosecondsPerSuccess','clientCpuMicrosecondsPerSuccess'),('managedBytesPerSuccess','managedBytesPerSuccess'),('peakRssBytes','peakRssBytes'),('releasedIdleRssBytes','releasedIdleRssBytes')]:
            delta, ratio = (a[metric]/b[metric]-1)*100, a[metric]/d[metric]
            check(provider + ' round ' + str(round_no) + ' summary comparison ' + metric,
                  close(original[key]['candidateVsBeforePercent'],delta) and close(original[key]['candidateVsDapperRatio'],ratio))
            pair['metrics'][metric] = {'candidate':a[metric],'before':b[metric],'dapper':d[metric],
                'candidateMinusBefore':a[metric]-b[metric],'candidateVsBeforePercent':delta,'candidateVsDapperRatio':ratio}
        for boundary in ('service','scheduled'):
            pair['quantiles'][boundary] = {}
            for q in ('p50MicrosecondsUpper','p95MicrosecondsUpper','p99MicrosecondsUpper'):
                av,bv,dv = (x['quantiles'][boundary][q] for x in (a,b,d))
                delta = (av/bv-1)*100
                check(provider + ' round ' + str(round_no) + ' ' + boundary + '/' + q,
                      close(original[boundary][q]['candidateVsBeforePercent'],delta))
                pair['quantiles'][boundary][q] = {'candidate':av,'before':bv,'dapper':dv,'candidateVsBeforePercent':delta,'candidateVsDapperRatio':av/dv}
        pairs.append(pair)

report = {'task':'DB-Exec-Parity-01','reviewer':'recovery_audit','reviewedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'passed':True,'scope':'Independent parsing and arithmetic of small sealed JSON/plan/controller data; no workload, build, archive, ELF hash or resource-JSONL replay',
    'checkCount':len(checks),'checks':checks,'inputs':inputs,'totals':totals,'cells':rows,'pairedComparisons':pairs,
    'originalCaseIds':canonical_cases,'controller':{'planIdentityMatched':True,'all12Passed':True,'serialControllerAndMeasurementIntervals':True,
        'firstCellReusedExactlyOnce':True,'firstCellWrapperVersionIsDifferent':True,'firstWrapperSha256':plan['cells'][0]['priorWrapperSha256'],
        'laterWrapperSha256':plan['wrapperSha256'],'artifactIdentitiesStableAcrossRounds':True},
    'finalCredit':False,'executionPathParityProven':False,'frameworkOnlyZeroAllocationProven':False,
    'limitations':[
        'Both rounds used 500 offered operations/s for 30 seconds. This supports a finite zero-refusal cost comparison, not sustained capacity, confidence intervals or long acceptance.',
        'The dedicated arrivals producer spins when the remaining delay is at most 2ms. Process CPU includes that producer, harness, framework/driver and business work. A common additive cost can compress ratios; neither subtract a theoretical producer budget nor relabel the ratio as isolated execution-path CPU.',
        'Native allocation and framework-only managed bytes remain unknown. Managed allocation totals include DTO/string/JSON and harness state.',
        'Peak RSS is through the post-measurement snapshot; release RSS is a later 5-second idle sample with no forced GC. These are different boundaries and do not prove all-native release.',
        'PostgreSQL inner/outer values are non-atomic visible-process endpoint observations, not guaranteed bounds of exact steady CPU. Wait4 lifetime is a separate total and is not added.',
        'The first SQLite candidate was retained from wrapper v1; other cells used v2 controls. Actual consumer artifact identities and business conditions match across rounds, but wrapper provenance is intentionally retained.',
        'This review checks raw declared artifacts and existing small-file identity links; it does not reread large ELF/native files, replay all /proc sample JSONL, or independently prove external machine quietness.']}
(HERE/'zero-cost-independent-review.json').write_text(json.dumps(report,indent=2)+'\n')

md = ['# Zero-cost-05: independent reconciliation of 12 cells','',
      '**Result: the 12-cell raw/validation/controller/summary reconciliation passes. These observations show lower whole-process CPU and managed allocation than the earlier Korda build; they do not establish execution-path parity with Dapper.AOT.**','',
      f'The independent reviewer completed {len(checks)} checks by reading small sealed JSON files and arithmetic fields. No workload, build, profiler, archive, large binary hash, or resource-JSONL replay ran.','',
      '## Completeness and identity','',
      'All 12 cells have 35 unique case IDs, all cases succeeded 428 or 429 times, identical seeded row/digest oracles across both providers and all variants, and untruncated time series. Each cell records 15,000 successes and 366,067 consumed rows. The total is **180,000 successes and 4,392,804 rows, with zero rejection, business failure, retry or outstanding request**. Tracked owners returned to zero.','',
      'The controller plan/hash, per-cell validation hashes and raw-result hashes match. Controller intervals and actual measured intervals are serial. The first SQLite candidate cell was reused exactly once from its earlier completed run; its controller reuse timestamp is not a second execution. Wrapper v1/v2 provenance remains explicit. Actual ELF/native/package/route identities are stable between rounds for each provider/variant.','',
      'All cells are 30 seconds at 500 offered operations/s, queue 64, 32 rows/batch, 8 tenants and 1,024 orders/tenant, prepared/persistent mode, 64 warmup operations per worker outside measurement and five idle seconds after release. SQLite uses four workers and PostgreSQL eight. No cell grants final 30-minute credit.','',
      '## Client process CPU and managed allocation','',
      '| Provider / round | Before CPU µs/op | Candidate CPU µs/op | Dapper CPU µs/op | Candidate vs before | Candidate / Dapper | Managed B/op saved vs before |','|---|---:|---:|---:|---:|---:|---:|']
for x in pairs:
    c=x['metrics']['cpuMicrosecondsPerSuccess'];m=x['metrics']['managedBytesPerSuccess']
    md.append(f"| {x['provider']} / {x['round']} | {c['before']:.3f} | {c['candidate']:.3f} | {c['dapper']:.3f} | {c['candidateVsBeforePercent']:+.3f}% | {c['candidateVsDapperRatio']:.4f}× | {-m['candidateMinusBefore']:.3f} |")
md += ['', 'The four CPU differences are all negative, from **−2.758% to −9.528%**. Candidate managed allocation is lower by **4,888.965–4,898.989 B/op**; this is about 18.79–19.09% of the earlier process allocation. Candidate still allocates about 20.74–21.16 KB/op, against Dapper about 7.47–7.57 KB/op, so its process allocation ratio remains approximately 2.74–2.83×. Native allocation and framework-only managed allocation are explicitly unknown.','',
      'The process CPU ratios of **1.2323–1.2807× Dapper** include the dedicated `db-perf-arrivals` producer. Its `WaitUntil` spins with `Thread.SpinWait(32)` when the remaining delay is at most `Stopwatch.Frequency / 500` (2 ms), as well as including harness, driver/framework and business DTO work. A shared additive CPU cost can make the aggregate ratio look closer to one than the database execution components are. This review neither subtracts an assumed producer budget nor calls that aggregate ratio execution-path parity.','',
      '## Tail latency and retained-memory regressions','',
      '| Provider / round | Service p99 vs before | Scheduled p99 vs before | Released idle RSS vs before | Peak RSS vs before |','|---|---:|---:|---:|---:|']
for x in pairs:
    md.append(f"| {x['provider']} / {x['round']} | {x['quantiles']['service']['p99MicrosecondsUpper']['candidateVsBeforePercent']:+.3f}% | {x['quantiles']['scheduled']['p99MicrosecondsUpper']['candidateVsBeforePercent']:+.3f}% | {x['metrics']['releasedIdleRssBytes']['candidateVsBeforePercent']:+.3f}% | {x['metrics']['peakRssBytes']['candidateVsBeforePercent']:+.3f}% |")
md += ['', 'SQLite service/scheduled p50, p95 and p99 improve in both rounds. PostgreSQL p50/p95 improve in both rounds, but its scheduled p99 rises in both rounds and service p99 changes direction. Candidate released-idle RSS is higher than before in all four comparisons; peak RSS changes direction. These observations must remain beside the CPU/allocation improvements. Lower allocation volume does not itself prove lower retained RSS. No mechanism is assigned to these regressions from these cells alone.','',
      'All service, scheduled-to-completion and start-delay p50/p95/p99 values were independently reconstructed from their raw histograms, each accounting for all 15,000 successful operations. The values are bin upper bounds rather than exact individual latency order statistics. Two rounds show observed direction and variability, not a confidence interval.','',
      '## GC, RSS and PostgreSQL server scope','',
      '| Cell | Process GC pause (s) | Gen0 / Gen1 / Gen2 | Peak RSS through snapshot (B) | Released idle RSS (B) |','|---|---:|---|---:|---:|']
for r in rows:
    g=r['gcCountsProcessScope'];md.append(f"| {r['id']} | {r['gcPauseSecondsProcessScope']:.6f} | {g['Gen0']} / {g['Gen1']} / {g['Gen2']} | {r['peakRssBytes']} | {r['releasedIdleRssBytes']} |")
md += ['', 'Every GC-pause value equals the raw post/pre process-tick delta divided by 10,000,000. GC counts and pauses retain process scope. Released RSS follows tracked-owner release and about five seconds idle without forced GC; the peak snapshot precedes that idle period, so the two observations need not have identical peak boundaries.','',
      '| PostgreSQL cell | Observed inner CPU (s) | Observed outer CPU (s) | Separate wait4 lifetime CPU (s) |','|---|---:|---:|---:|']
for r in rows:
    if r['postgres']:
        pg=r['postgres'];md.append(f"| {r['id']} | {pg['observed']['inner']:.2f} | {pg['observed']['outer']:.2f} | {pg['wait4LifetimeUserPlusSystemSeconds']:.6f} |")
md += ['', 'The visible inner/outer endpoint arithmetic and monotonic flags match each validation. Candidate observations are higher than before in both rounds, but these non-atomic process-tree observations are not exact steady CPU bounds or a causal server-cost attribution. The separate wait4 lifetime also includes startup, fixture initialization, warmup, idle and shutdown. None of these server values are added to the client CPU metric or to each other; unobserved exits/transfer loss remain unknown.','',
      '## Recommendation and recovery','',
      'Retain the repeated CPU/allocation improvements and continue the planned pressure/final measurements under their own frozen conditions. Do not claim complete performance alignment, improved PostgreSQL tails, lower retained memory, framework-only 0 B, or exact PostgreSQL steady cost. At this lane\'s fixed arrival rate, roughly 500 completed operations/s is delivery of the offered load, not measured sustainable capacity.','',
      'The machine-readable review contains all per-cell inputs, hashes, 35 case IDs, checks, resource values and recomputed comparisons. The full source-of-truth raw/validation/controller files are unchanged. Later pressure measurements are separate and were not read or included in this review.','',
      '## Exact primary small-input identities','']
for item in inputs[:3]:
    md.append(f"- `{item['path']}`: SHA256 `{item['sha256']}` ({item['bytes']} B).")
(HERE/'zero-cost-independent-review.md').write_text('\n'.join(md)+'\n')
print(json.dumps({'passed':True,'checks':len(checks),'cells':len(rows),'totals':totals,
                  'inputBytesRead':sum(x['bytes'] for x in inputs),
                  'cpuChangesPercent':[x['metrics']['cpuMicrosecondsPerSuccess']['candidateVsBeforePercent'] for x in pairs],
                  'managedByteChanges':[x['metrics']['managedBytesPerSuccess']['candidateMinusBefore'] for x in pairs]}))
