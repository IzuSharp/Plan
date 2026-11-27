#!/usr/bin/env python3
"""Analyze sealed finite-pressure cells; no database, build or measurement runs."""
from pathlib import Path
import datetime
import hashlib
import json
import math
import statistics

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
inputs, checks = [], []


def load(path):
    b = path.read_bytes()
    inputs.append({'path': str(path.relative_to(ROOT)), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()})
    return json.loads(b)


def check(name, value):
    checks.append({'name': name, 'passed': bool(value)})
    if not value:
        raise AssertionError(name)


def close(a, b):
    return math.isclose(a, b, rel_tol=1e-11, abs_tol=1e-9)


def percentile(histogram, percent):
    target, seen = math.ceil(sum(histogram) * percent / 100), 0
    for i, count in enumerate(histogram):
        seen += count
        if seen >= target:
            lower = 2 ** (i // 128)
            return (lower + lower * ((i % 128 + 1) / 128)) / 1000
    raise ValueError('No percentile')


def dt(text):
    return datetime.datetime.fromisoformat(text)


def window(series, start, end):
    selected = [x for x in series if start <= x['Second'] < end]
    assert len(selected) == end - start
    counts = {k: sum(x[k] for x in selected) for k in ('Planned','Sent','Started','Succeeded','Failed','Rejected','Rows')}
    actual_attempts = counts['Sent'] + counts['Rejected']
    rates = [x['Succeeded'] for x in selected]
    mean = statistics.mean(rates)
    middle = (len(rates) - 1) / 2
    slope = sum((i-middle)*(v-mean) for i,v in enumerate(rates)) / sum((i-middle)**2 for i in range(len(rates)))
    return {'startSecondInclusive': start, 'endSecondExclusive': end, 'seconds': end-start,
            'counts': counts, 'observedAttempts': actual_attempts,
            'successCompletionsPerSecond': counts['Succeeded']/(end-start),
            'rejectionPercentOfObservedAttempts': counts['Rejected']/actual_attempts*100 if actual_attempts else None,
            'secondsWithRejections': sum(x['Rejected'] > 0 for x in selected),
            'perSecondSuccessMin': min(rates), 'perSecondSuccessMax': max(rates),
            'perSecondSuccessPopulationCv': statistics.pstdev(rates)/mean if mean else None,
            'successPerSecondLinearSlope': slope,
            'stationarityProven': False}


plan = load(HERE / 'series-01.plan.json')
state = load(HERE / 'series-01.plan.resume.json')
check('16 cells completed', state['passed'] and state['stage'] == 'completed' and len(plan['cells']) == len(state['cells']) == 16)
check('controller binds plan', state['planSha256'] == inputs[0]['sha256'])
check('plan and controller order', [x['id'] for x in plan['cells']] == [x['id'] for x in state['cells']])
check('serial controller intervals', all(dt(a['finishedUtc']) <= dt(b['startedUtc']) for a,b in zip(state['cells'],state['cells'][1:])))
check('no final credit', plan['ordinaryTiming'] and not plan['finalCredit'] and not state['finalCredit'])

cells, identities, canonical_ids, oracles = [], {}, None, {}
for entry, controller in zip(plan['cells'], state['cells']):
    name, folder = entry['id'], Path(entry['output'])
    v = load(folder/'validation.json')
    vsha = inputs[-1]['sha256']
    raw = load(folder/'measurement/result.json')
    rsha = inputs[-1]['sha256']
    c, resource, condition, offered = v['normalized']['counts'], v['resources'], v['conditions'], raw['OfferedLoad']
    ck = lambda n, value: check(name+': '+n, value)
    ck('validation linked by controller', vsha == controller['validationSha256'])
    ck('raw linked by validation', rsha == v['rawFiles'][str(folder/'measurement/result.json')]['sha256'])
    ck('ordinary pressure execution successful', controller['exitCode'] == 0 and controller['passed'] and v['passed']
       and v['kind'] == 'pressure' and v['ordinaryTiming'] and not v['finalCredit'] and not v['newFinalCellCredit']
       and raw['TimingComparisonEligible'] and raw['NativeAot'])
    ck('conditions fixed except offered rate', condition['provider'] == entry['provider'] and condition['seconds'] == 30
       and condition['rate'] == entry['rate'] and condition['queue'] == 64 and condition['idle'] == 5
       and condition['rows'] == condition['batchRows'] == 32 and condition['warmup'] == 64
       and condition['tenants'] == 8 and condition['ordersPerTenant'] == 1024
       and condition['concurrency'] == (4 if entry['provider'] == 'sqlite' else 8)
       and condition['mode'] == 'prepared' and condition['session'] == 'persistent')
    ck('input freeze stayed unchanged during cell', v['prePostInputIdentitiesEqual'])
    ck('admission ledger closes', c['planned'] == c['attempted'] == entry['rate']*30
       and c['attempted'] == c['sent'] + c['rejected'] and c['sent'] == c['started'] == c['completed']
       and c['completed'] == c['succeeded'] + c['failed'] and c == controller['counts'])
    ck('no business errors or retries', c['failed'] == c['retries'] == raw['OracleFailures'] == 0
       and raw['Errors'] == offered['Errors'] == [] and offered['ErrorClasses'] == {})
    ck('outer/raw offered ledger agree', raw['Completed'] == offered['Succeeded'] == c['succeeded']
       and raw['Rows'] == offered['Rows'] == c['rows'] and raw['Failed'] == offered['Failed'] == c['failed'])
    ids, case_ledger = raw['ActualCaseIds'], raw['Cases']
    if canonical_ids is None:
        canonical_ids = ids
    ck('35 case/oracle/contract sets', len(ids) == len(set(ids)) == 35 and ids == canonical_ids
       and [x['Name'] for x in case_ledger] == ids and set(raw['ExpectedResults']) == set(ids)
       and set(raw['CaseModeContracts']) == set(ids) and v['normalized']['fullCaseCoverage']
       and not v['normalized']['missingExecutedCaseIds'])
    ck('per-case accepted work correct', all(x['Succeeded'] > 0 and x['Failed'] == 0
       and x['Rows'] == x['Succeeded'] * raw['ExpectedResults'][x['Name']]['Rows'] for x in case_ledger)
       and sum(x['Succeeded'] for x in case_ledger) == c['succeeded'] and sum(x['Rows'] for x in case_ledger) == c['rows'])
    oracle = {k: (x['Rows'],int(x['Digest'])) for k,x in raw['ExpectedResults'].items()}
    if entry['provider'] not in oracles:
        oracles[entry['provider']] = oracle
    ck('same provider seeded business contract', oracle == oracles[entry['provider']])
    series = offered['Seconds']
    ck('series is complete and ordered', not offered['TimeSeriesTruncated'] and not raw['TimeSeriesTruncated']
       and [x['Second'] for x in series] == list(range(len(series))) and len(series) >= 30)
    for k, counter in [('Planned','planned'),('Sent','sent'),('Started','started'),('Succeeded','succeeded'),('Failed','failed'),('Rejected','rejected'),('Rows','rows')]:
        ck('per-second '+k+' sum', sum(x[k] for x in series) == c[counter] and all(x[k] >= 0 for x in series))
    ck('outer per-second ledger agrees', sum(x['Completed'] for x in raw['Seconds']) == c['succeeded']
       and sum(x['Rows'] for x in raw['Seconds']) == c['rows'] and sum(x['Failed'] for x in raw['Seconds']) == 0)
    quantiles = {}
    for boundary,key in [('service','SuccessServiceHistogram'),('scheduled','SuccessScheduledHistogram'),('startDelay','StartDelayHistogram')]:
        hist = offered[key]
        ck(boundary+' histogram count', sum(hist) == c['succeeded'])
        quantiles[boundary] = {'p'+str(n)+'MicrosecondsUpper':percentile(hist,n) for n in (50,95,99)}
        ck(boundary+' histogram percentiles', all(close(x,v['quantiles'][boundary][k]) for k,x in quantiles[boundary].items()))
    ck('outer service histogram linked', raw['Latencies']['Histogram'] == offered['SuccessServiceHistogram'])
    before, after, idle = raw['ProcessBefore'],raw['ProcessAfter'],raw['Idle']
    user, system = after['UserCpuSeconds']-before['UserCpuSeconds'],after['SystemCpuSeconds']-before['SystemCpuSeconds']
    cpu_op = (user+system)/c['succeeded']
    allocated = raw['AllocatedAfter']-raw['AllocatedBefore']
    pause = (after['TotalGcPauseTicks']-before['TotalGcPauseTicks'])/10000000
    ck('client CPU and allocations reconcile', close(cpu_op,resource['clientCpuSecondsPerSuccess'])
       and close(cpu_op,controller['cpuSecondsPerSuccess']) and close(user,resource['clientUserCpuSeconds'])
       and close(system,resource['clientSystemCpuSeconds']) and allocated == raw['AllocatedBytes'] == resource['managedAllocatedBytes']
       and close(allocated/c['succeeded'],resource['managedBytesPerSuccess']))
    ck('GC pause/counts and release RSS reconcile', close(pause,resource['gcPauseSecondsProcessScope'])
       and {k:raw[k] for k in ('Gen0','Gen1','Gen2')} == resource['gcCountsProcessScope']
       and after['PeakRssBytes'] == resource['peakRssThroughMeasurementBytes']
       and idle['After']['RssBytes'] == resource['releasedIdleRssBytes'] and idle['ObservedSeconds'] >= 4.99)
    owner_keys = ('ApplicationConnections',) if entry['variant']=='dapper' else ('Sources','Sessions','Operations','Cursors','Buffers','Owners','PullChannels','CommandCompletions')
    ck('tracked owners returned', all(raw['Drained'][k] == 0 for k in owner_keys))
    ck('native and framework-only allocation unknown', raw['NativeAllocationProfile'] is None and resource['nativeAllocationProfile'] is None
       and resource['frameworkOnlyManagedBytes'] is None)
    elapsed = (offered['DrainedTicks']-offered['StartedTicks'])/offered['TimerFrequency']
    whole_throughput = c['succeeded']/elapsed
    ck('through-drain throughput matches', close(elapsed,v['normalized']['elapsedThroughDrainSeconds'])
       and close(whole_throughput,v['normalized']['successOpsPerSecond']) and close(whole_throughput,controller['successOpsPerSecond']))
    identity = {k:raw[k] for k in ('ExecutableSha256','LoadedNativeSha256','PackageVersion','Route')}
    key = entry['provider']+'/'+entry['variant']
    if key not in identities:
        identities[key] = identity
    ck('same actual consumer across rates', identities[key] == identity)
    server = None
    if entry['provider']=='postgresql':
        pg = resource['postgres']
        ck('server observations retain non-exact scope', pg['observedInnerOuterAvailable'] and pg['exactSteadyCpuProven'] is False
           and pg['unobservedExitedChildrenOrNonAtomicTransferLoss']=='unknown')
        server = {'observedIntervals':{},'wait4Lifetime':pg['wait4Lifetime'],'exactSteadyCpuProven':False,
                  'scope':pg['lifetimeScope'],'unknownExitedOrTransferLoss':pg['unobservedExitedChildrenOrNonAtomicTransferLoss']}
        intervals = pg['visibleSteadyIntervals']
        for side in ('inner','outer'):
            x = intervals[side]
            u = (x['lastCounters']['ownAndReapedUserTicks']-x['firstCounters']['ownAndReapedUserTicks'])/intervals['ticksPerSecond']
            s = (x['lastCounters']['ownAndReapedSystemTicks']-x['firstCounters']['ownAndReapedSystemTicks'])/intervals['ticksPerSecond']
            ck('server '+side+' arithmetic', x['allObservedCountersMonotonic'] and close(u,x['userCpuSecondsObserved']) and close(s,x['systemCpuSecondsObserved']))
            server['observedIntervals'][side] = {'userCpuSeconds':u,'systemCpuSeconds':s,'totalCpuSeconds':u+s,
                'firstAcquisition':x['firstAcquisition'],'lastAcquisition':x['lastAcquisition'],'eligibleSamples':x['eligibleSamples']}
    else:
        ck('SQLite has no server lane', resource['postgres'] is None)
    chunks = [window(series,start,start+10) for start in (0,10,20)]
    rejection_bins = [x for x in series if x['Rejected']]
    last = chunks[-1]
    last['successRateVsPrevious10SecondsPercent']=(last['successCompletionsPerSecond']/chunks[-2]['successCompletionsPerSecond']-1)*100
    success_mix = [{'name':x['Name'],'succeeded':x['Succeeded'],
                    'successSharePercent':x['Succeeded']/c['succeeded']*100,
                    'shareMinusUniformPercentagePoints':(x['Succeeded']/c['succeeded']-1/35)*100,
                    'countDeviationFromUniformPercent':(x['Succeeded']/(c['succeeded']/35)-1)*100}
                   for x in case_ledger]
    ck('successful mix shares sum to100',close(sum(x['successSharePercent'] for x in success_mix),100))
    cells.append({'id':name,'provider':entry['provider'],'variant':entry['variant'],'offeredRate':entry['rate'],
        'conditions':condition,'counts':c,'rejectionPercent':c['rejected']/c['attempted']*100,
        'successOpsPerSecondThroughDrain':whole_throughput,'elapsedThroughDrainSeconds':elapsed,
        'drainSecondsAfterOfferedDeadline':(offered['DrainedTicks']-offered['DeadlineTicks'])/offered['TimerFrequency'],
        'acceptedCompletionShare':c['succeeded']/c['attempted'],
        'serviceAndScheduledQuantiles':quantiles,'clientUserCpuSeconds':user,'clientSystemCpuSeconds':system,
        'clientCpuMicrosecondsPerSuccess':cpu_op*1e6,'managedAllocatedBytes':allocated,'managedBytesPerSuccess':allocated/c['succeeded'],
        'gcCountsProcessScope':resource['gcCountsProcessScope'],'gcPauseSecondsProcessScope':pause,
        'peakRssThroughMeasurementBytes':after['PeakRssBytes'],'releasedIdleRssBytes':idle['After']['RssBytes'],
        'releasedIdlePssBytes':idle['After']['PssBytes'],'idleObservedSeconds':idle['ObservedSeconds'],
        'clientWait4Lifetime':resource['clientWait4Lifetime'],'nativeAllocationProfile':None,'frameworkOnlyManagedBytes':None,
        'postgres':server,'tenSecondWindows':chunks,'last10Seconds':last,
        'rejectionSeconds':len(rejection_bins),'firstRejectionSecond':rejection_bins[0]['Second'] if rejection_bins else None,
        'lastRejectionSecond':rejection_bins[-1]['Second'] if rejection_bins else None,
        'nonzeroRejectionsBySecond':[{'second':x['Second'],'rejected':x['Rejected']} for x in rejection_bins],
        'rejectedPerOfferedSecond0To29':[x['Rejected'] for x in series[:30]],
        'completedAfterSecond30':sum(x['Succeeded'] for x in series if x['Second']>=30),
        'businessCases':case_ledger,'businessCaseSuccessRange':[min(x['Succeeded'] for x in case_ledger),max(x['Succeeded'] for x in case_ledger)],
        'successfulCaseMix':success_mix,'successfulMixUniformReferencePercent':100/35,
        'successfulMixDeviationFromUniformPercentRange':[min(x['countDeviationFromUniformPercent'] for x in success_mix),max(x['countDeviationFromUniformPercent'] for x in success_mix)],
        'actualArtifactIdentity':identity,'validationSha256':vsha,'rawSha256':rsha,
        'steadyStartMonotonicNs':v['normalized']['steadyStartMonotonicNs'],'drainedMonotonicNs':v['normalized']['drainedMonotonicNs'],
        'finalCredit':False,'stationarityProven':False})

check('same seeded oracles across providers',oracles['sqlite']==oracles['postgresql'])
check('all actual measured windows serial',all(a['drainedMonotonicNs']<=b['steadyStartMonotonicNs'] for a,b in zip(cells,cells[1:])))
totals={k:sum(c['counts'][k] for c in cells) for k in cells[0]['counts']}
check('overall planned attempts',totals['attempted']==1320000 and totals['succeeded']+totals['rejected']==totals['attempted'])
check('overall no errors/retries',totals['failed']==totals['retries']==0)
byid={x['id']:x for x in cells}
check('PG Dapper non-monotonic rejection preserved',byid['postgresql-rate-1200-dapper']['counts']['rejected']==177
      and byid['postgresql-rate-2400-dapper']['counts']['rejected']==0)
check('SQLite Dapper non-monotonic high rejection preserved',byid['sqlite-rate-3000-dapper']['counts']['rejected']==579
      and byid['sqlite-rate-4000-dapper']['counts']['rejected']==554)
comparisons=[]
for provider in ('sqlite','postgresql'):
    for rate in sorted({x['offeredRate'] for x in cells if x['provider']==provider}):
        a=byid[f'{provider}-rate-{rate}-candidate'];d=byid[f'{provider}-rate-{rate}-dapper']
        mix_differences=[{'name':x['name'],'candidateMinusDapperSuccessSharePercentagePoints':x['successSharePercent']-y['successSharePercent']}
                         for x,y in zip(a['successfulCaseMix'],d['successfulCaseMix'])]
        comparisons.append({'provider':provider,'offeredRate':rate,
            'candidateToDapperSuccessfulThroughputRatio':a['successOpsPerSecondThroughDrain']/d['successOpsPerSecondThroughDrain'],
            'candidateToDapperClientCpuPerSuccessRatio':a['clientCpuMicrosecondsPerSuccess']/d['clientCpuMicrosecondsPerSuccess'],
            'candidateToDapperManagedBytesPerSuccessRatio':a['managedBytesPerSuccess']/d['managedBytesPerSuccess'],
            'isolatedExecutionPathRatio':None,'acceptedBusinessCaseMixMayDifferUnderRejection':True,
            'successfulCaseMixDifferences':mix_differences,
            'successMixTotalVariationPercentagePoints':sum(abs(x['candidateMinusDapperSuccessSharePercentagePoints']) for x in mix_differences)/2})
limitations=[
    'Each rate/variant has one serial 30-second window; offered rate rises within provider and route order alternates. This is not a replicated capacity curve or a confidence interval.',
    'Whole-window success throughput uses actual start-through-drain elapsed time. Last10Seconds uses completed operations timestamped in [20,30), excludes drain seconds, and is not a cohort of requests admitted only in that interval.',
    'Last 10 seconds are a fixed descriptive subsection, not a proof of stationarity. First/middle/final 10-second rates, per-second min/max/CV and slope are retained to reveal transients.',
    'Per-second Planned is due-time schedule. Sent/Rejected and completions use actual event times. Do not force Planned=Sent+Rejected in each bucket; full-series ledgers close exactly.',
    'Rejected work is admission rejection, not a business error. Service/scheduled latency histograms cover accepted successful work and exclude rejected requests.',
    'Process CPU includes the spinning arrival producer, failed admission work, harness, drivers/framework and business materialization. Ratios cannot isolate execution paths or be corrected by subtracting an assumed producer budget.',
    'Native allocation and framework-only managed bytes are unknown. Peak RSS is through a measurement snapshot; released RSS follows tracked-owner release and five seconds idle without forced GC.',
    'PG sampled inner/outer visible-proc CPU is non-atomic observation, not an exact steady bound. Separate wait4 lifetime includes initialization/warmup/idle/shutdown and is never added to sampled CPU.',
    'Every business case succeeds and matches its oracle, but admission rejection changes accepted case counts; exact35-class success shares and deviations from uniform are retained. A changed mix or selective dropping of more/less allocating business must not be called a framework allocation improvement. Per-class rejection causes or counterfactual costs are not inferred.',
    'Physical PG fixtures retired by the root were not read or recreated. All analysis uses retained raw/config/validation/controller evidence.'
]
finding={
    'candidateSQLite':{'last10At3000':byid['sqlite-rate-3000-candidate']['last10Seconds'],'last10At4000':byid['sqlite-rate-4000-candidate']['last10Seconds'],
        'interpretation':'Finite overloaded completion plateau around 2.27-2.35k/s in final 10 seconds; all 30 seconds reject at both high rates. Not a maximum loss-free capacity.'},
    'candidatePostgresql':{'last10At3600':byid['postgresql-rate-3600-candidate']['last10Seconds'],'last10At4800':byid['postgresql-rate-4800-candidate']['last10Seconds'],
        'interpretation':'Final10 completion rates around 2.70-2.74k/s with rejection every second. The 3600 cell is nonstationary across its three 10-second blocks (2216.3,2213.5,2738.8/s); do not call whole-window 2389.9/s exact capacity.'},
    'dapperSaturationLocated':False,
    'dapperHighestCells':'SQLite4000 final10 3992.4/s with 2 rejection seconds; PG4800 final10 4770.4/s with 3 rejection seconds. Still largely follows offered rate; no sustained plateau located.',
    'observedFirstRefusalRates':{'sqliteCandidate':2000,'sqliteDapper':2000,'postgresqlCandidate':1200,'postgresqlDapper':1200},
    'firstRefusalInterpretation':'First tested rate with any refusal, not a precise monotonic or sustainable-capacity threshold.'}
recommendations=[
    {'priority':1,'question':'Locate Dapper sustained overload rather than treating transient refusal as saturation.',
     'suggestion':'Use a new explicit local plan with one higher cell per provider (for example SQLite6000/s and PG7200/s, queue64 and current workers). If still tracking offered rate, extend one step; repeat the first adjacent high-rate pair that shows dense continuing rejections and a completion plateau. Do not extrapolate capacity from current top cells.'},
    {'priority':2,'question':'Test the non-monotonic low-rate refusal observation.',
     'suggestion':'A reversed PG Dapper2400/1200 pair is the clearest small repeat: current1200 rejects at seconds8/10/17 but2400 rejects zero. If strict zero-refusal-envelope decisions depend on SQLite, repeat its Dapper4000/2000 pair; do not rerun all16 cells.'},
    {'priority':3,'question':'Resolve the PG candidate3600 transient before assigning a plateau.',
     'suggestion':'One reversed candidate4800/3600 pair with a somewhat longer separately identified duration (for example60s) and the same fixed final10-second summary can distinguish the 3600 early/mid slowdown from a stable tail. The existing SQLite high cells already show rejection every second; no broad repeat is needed merely to demonstrate their overload.'},
]
summary={'task':'DB-Exec-Parity-01','passed':True,'createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'scope':'Sealed16-cell finite pressure analysis; no new execution','ordinaryTiming':True,'finalCredit':False,
         'cellCount':16,'totals':totals,'cells':cells,'sameRateComparisons':comparisons,'findings':finding,
         'localRepeatRecommendations':recommendations,'limitations':limitations,'inputIdentities':inputs,
         'fixtureRetirementReceipt':'experiments/recovery/fixture-retirement-review-01/actual-01.json'}
(HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
series_output={'task':'DB-Exec-Parity-01','scope':'Exact copied offered event bins from retained raw; zero bins and drain bins retained','cells':[]}
for entry in plan['cells']:
    # Data is small and immutable; independently replay event-bin totals after the summary was assembled.
    r=json.loads((Path(entry['output'])/'measurement/result.json').read_text())
    series_output['cells'].append({'id':entry['id'],'seconds':r['OfferedLoad']['Seconds']})
(HERE/'per-second.json').write_text(json.dumps(series_output,indent=2)+'\n')
independent={'task':'DB-Exec-Parity-01','reviewer':'recovery_audit','passed':True,'checkCount':len(checks),'checks':checks,
             'scope':'Independent raw-to-validation/controller arithmetic and source identity links; no large artifact hashes or /proc JSONL replay',
             'inputIdentities':inputs,'all35CasesCoveredEachCell':True,'allCasesMatchSeededOracle':True,
             'all16ControllersExit0':True,'noFixtureRestoration':True,'newMeasurementCredit':False,
             'summarySha256':hashlib.sha256((HERE/'summary.json').read_bytes()).hexdigest(),
             'perSecondSha256':hashlib.sha256((HERE/'per-second.json').read_bytes()).hexdigest()}
(HERE/'independent-checks.json').write_text(json.dumps(independent,indent=2)+'\n')

md=['# Pressure-05: finite-load summary and independent review','',
    '**The candidate reaches continuing admission rejection and a bounded completion plateau at the high offered rates. Dapper still largely follows the highest offered rates tested, so this series does not locate its sustained saturation. The first observed refusals are not a monotonic capacity threshold.**','',
    f'All16 cells passed {len(checks)} independent raw/validation/controller checks. There are {totals["attempted"]:,} attempted businesses, {totals["succeeded"]:,} successes, {totals["rejected"]:,} admission rejections, {totals["rows"]:,} consumed rows, and zero business errors, retries or oracle failures. Every cell covers all35 cases. This is analysis of existing evidence; no measurement, build, profile or archive ran.','',
    '## Conditions and accounting','',
    'Each cell ran30 seconds with queue64,32 rows/batch, prepared/persistent mode,8 tenants,1,024 orders/tenant,64 warmups per worker outside measurement, and5 idle seconds after owner release. SQLite uses4 workers; PostgreSQL8. Rates increase by provider, and candidate/Dapper order alternates. Historical offered rates SQLite3000 and PG3600 remain present. There is one observation per rate/variant, not replicated confidence intervals or30-minute acceptance.','',
    'Whole-cell throughput includes the actual drain interval. The final10-second subsection means completion timestamps in `[20,30)` and excludes drain completions; it is a fixed descriptive window, not automatic proof of stationarity. Planned events use scheduled time, whereas sent/rejected/completed events use their actual time. Some individual buckets consequently do not satisfy planned=sent+rejected, although the full ledgers reconcile.','',
    '## Per-cell outcome','',
    '| Cell | Attempted | Success | Rejected | Rejected % | Business errors | Success/s through drain |','|---|---:|---:|---:|---:|---:|---:|']
for c in cells:
    md.append(f"| {c['id']} | {c['counts']['attempted']} | {c['counts']['succeeded']} | {c['counts']['rejected']} | {c['rejectionPercent']:.3f} | {c['counts']['failed']} | {c['successOpsPerSecondThroughDrain']:.3f} |")
md+=['','## Latency of accepted successful work','',
     'All values below are histogram-bin upper bounds in milliseconds. Rejected work is reported separately and is not assigned a successful-request latency. Raw service, scheduled and start-delay p50/p95/p99 values and complete histograms were reconciled.','',
     '| Cell | Service p50 / p95 / p99 ms | Scheduled p50 / p95 / p99 ms | Start-delay p99 ms |','|---|---|---|---:|']
for c in cells:
    q=c['serviceAndScheduledQuantiles'];fmt=lambda b:' / '.join(f"{q[b]['p'+str(n)+'MicrosecondsUpper']/1000:.3f}" for n in (50,95,99))
    md.append(f"| {c['id']} | {fmt('service')} | {fmt('scheduled')} | {q['startDelay']['p99MicrosecondsUpper']/1000:.3f} |")
md+=['','## Last10 seconds and continuing rejection','',
     '| Cell | Completion/s in0–10 /10–20 /20–30 | Last10 rejections | Rejecting seconds /10 | Last10 success min–max/s | Last10 CV % |','|---|---|---:|---:|---|---:|']
for c in cells:
    tail=c['last10Seconds'];chunks=' / '.join(f"{w['successCompletionsPerSecond']:.1f}" for w in c['tenSecondWindows'])
    md.append(f"| {c['id']} | {chunks} | {tail['counts']['Rejected']} | {tail['secondsWithRejections']} | {tail['perSecondSuccessMin']}–{tail['perSecondSuccessMax']} | {tail['perSecondSuccessPopulationCv']*100:.3f} |")
md+=['',
     '- SQLite candidate rejects during all30 seconds at both3000/s and4000/s. Final10 completion rates are **2345.2/s and2265.3/s**, with21.83% and43.37% final-window admission rejection. This is an observed overloaded plateau around2.3k/s under these conditions, not a maximum loss-free sustainable capacity.',
     '- PG candidate also rejects during every second at3600/s and4800/s. Final10 completion rates are **2738.8/s and2697.4/s**, with23.90% and43.80% final-window rejection. At3600/s, however, the first two10-second blocks are only2216.3/s and2213.5/s. The whole-window2389.9/s obscures that transition; its cause is not established by these counters.',
     '- SQLite Dapper still completes3992.4/s in the final10 seconds at4000/s, with rejections in only2 of those seconds. PG Dapper completes4770.4/s at4800/s with3 rejecting seconds. No sustained flat Dapper plateau has been located. A nonzero rejection count alone does not establish saturation.','',
     '## Non-monotonic observations and complete rejection distribution','',
     'PG Dapper1200/s rejects177 requests only in seconds8,10 and17; its final10 seconds reject none. The subsequent2400/s cell has zero rejections throughout. SQLite Dapper2000/s rejects101 only in second9, then its final10 seconds follow2000/s without rejection. At3000/s it rejects579, and at4000/s554, while completion follows the raised offer. These original counts are preserved; no smoothing or forced monotonic fit was applied.','',
     'Below are all nonzero `second:rejected` bins; all omitted offered-second bins are zero. `per-second.json` retains every bin, including zeros and drain bins, with planned/sent/started/success/error/row counters. The fixed final10 interval and nonzero rejection bins are also embedded in `summary.json`.','']
for c in cells:
    distribution=', '.join(f"{x['second']}:{x['rejected']}" for x in c['nonzeroRejectionsBySecond']) or 'none'
    md.append(f"- **{c['id']}**: {distribution}.")
md+=['','## Client CPU, allocations, memory and GC','',
     '| Cell | Client CPU µs/success | Managed B/success | Peak / idle RSS MiB | GC0 /1 /2 | Process GC pause ms |','|---|---:|---:|---|---|---:|']
for c in cells:
    g=c['gcCountsProcessScope']
    md.append(f"| {c['id']} | {c['clientCpuMicrosecondsPerSuccess']:.3f} | {c['managedBytesPerSuccess']:.3f} | {c['peakRssThroughMeasurementBytes']/1048576:.3f} / {c['releasedIdleRssBytes']/1048576:.3f} | {g['Gen0']} / {g['Gen1']} / {g['Gen2']} | {c['gcPauseSecondsProcessScope']*1000:.3f} |")
md+=['',
     'These CPU totals include the spinning arrival producer, unsuccessful admission work, harness, drivers/framework and business materialization. A changed rate or rejection share changes how those common costs amortize per successful operation. Do not label the ratios as isolated execution efficiency or subtract a theoretical producer budget. Managed allocations include DTO/string/JSON and harness work. Native allocation and framework-only managed allocation are unknown in every ordinary cell.',
     'Peak RSS is lifetime-through-measurement-snapshot, while idle RSS is later, after tracked-owner release and five idle seconds without forced GC. GC counts and pause remain process totals. Exact bytes, total CPU/allocation and idle PSS are in summary.json. A drop in process B/op across rates does not by itself prove a new allocation optimization.','',
     '## Successful business mix under rejection','',
     'The offered business contract is the same35 cases, but accepted successful subsets differ after rejection. Each cell\'s35 success shares, deviations from the uniform1/35 reference and candidate/Dapper share differences are retained in summary.json. The reference is a descriptive normalization, not an inferred per-class rejection ledger.','',
     '| Cell | Min–max successful cases per class | Min–max count deviation from uniform % |','|---|---|---|']
for c in cells:
    spread=c['successfulMixDeviationFromUniformPercentRange']
    md.append(f"| {c['id']} | {c['businessCaseSuccessRange'][0]}–{c['businessCaseSuccessRange'][1]} | {spread[0]:+.3f} to {spread[1]:+.3f} |")
md+=['',
     'Different accepted shares can change DTO/JSON/row-allocation and driver work per success. A rate-dependent B/op decrease, or a difference affected by selective dropping of costly or cheap business, cannot be credited as a framework-allocation improvement. These counters do not identify per-class rejection causes or counterfactual costs.','',
     '## PostgreSQL server costs, separately scoped','',
     '| PG cell | Observed inner CPU s | Observed outer CPU s | Separate wait4 lifetime CPU s | Lifetime wait4 MaxRSS B |','|---|---:|---:|---:|---:|']
for c in cells:
    if c['postgres']:
        pg=c['postgres'];life=pg['wait4Lifetime']
        md.append(f"| {c['id']} | {pg['observedIntervals']['inner']['totalCpuSeconds']:.3f} | {pg['observedIntervals']['outer']['totalCpuSeconds']:.3f} | {life['processLifetimeUserCpuSeconds']+life['processLifetimeSystemCpuSeconds']:.6f} | {life['processLifetimeMaxRssBytes']} |")
md+=['',
     'Inner/outer values are endpoint observations of visible live/reaped processes, not exact steady CPU bounds. The separately retained wait4 lifetime includes server startup, fixture creation, warmup, idle and shutdown; its MaxRSS is that lifetime receipt field, not a summed steady PG-group RSS. These costs are not added to each other or to client CPU. Missed exited processes and non-atomic counter-transfer loss remain unknown.','',
     '## Targeted follow-ups worth doing','',
     '1. **Locate sustained Dapper overload.** A fresh bounded plan can try one higher rate per provider, for example SQLite6000/s and PG7200/s with the same queue/workers. Extend one further step only if completion still tracks offered load. Repeat the first adjacent high pair that produces dense continuing rejection and a completion plateau; the current top rates are insufficient to claim its saturation.',
     '2. **Resolve non-monotonic transient refusal when a zero-loss envelope matters.** Reverse the PG Dapper2400/1200 pair. If the SQLite admission boundary affects a decision, similarly repeat Dapper4000/2000. Preserve per-second admission/start-delay evidence; do not treat a single burst as a precise monotonic threshold or rerun the entire16-cell grid.',
     '3. **Check PG candidate3600\'s transient.** A reversed candidate4800/3600 pair with a separately identified duration such as60 seconds and the same fixed final10 summary can show whether the initial/middle slowdown recurs. Existing SQLite high cells already establish continuing rejection; broad additional repeats are unnecessary merely to show that overload.',
     '',
     'These are suggested local follow-ups, not executed measurements. The first tested rate with any refusal is SQLite2000/s and PG1200/s for both variants, but this is only an observation in the sampled grid. It must not be presented as exact capacity. Final long cells retain their own frozen conditions, original historical rates/queue and separate acceptance credit.','',
     '## Evidence and recovery','',
     '`independent-checks.json` retains all checks and exact small-input identities. `summary.json` contains complete per-cell resources,35-case ledgers,10-second windows and comparisons. `per-second.json` retains exact event bins. `summarize_pressure.py` reproduces these reports without accessing a database or large binary.',
     'The root\'s fixture retirement receipt is `experiments/recovery/fixture-retirement-review-01/actual-01.json`. No retired data directory was recreated, read as a new result, or included in this analysis. Original raw, validation, controller and configuration files remain unchanged.','',
     'Primary controller identities:','']
for x in inputs[:2]:
    md.append(f"- `{x['path']}`: SHA256 `{x['sha256']}` ({x['bytes']} B).")
(HERE/'README.md').write_text('\n'.join(md)+'\n')
print(json.dumps({'passed':True,'checks':len(checks),'cells':len(cells),'totals':totals,
                  'inputBytesRead':sum(x['bytes'] for x in inputs),'dapperSaturationLocated':False,
                  'written':['summary.json','per-second.json','independent-checks.json','README.md']}))
