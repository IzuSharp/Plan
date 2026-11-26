#!/usr/bin/env python3
"""Read-only independent arithmetic/identity review of the completed Go cells.
Does not import or run verify_result.py; writes only new review artifacts.
"""
import bisect
import collections
import datetime
import hashlib
import itertools
import json
import math
from pathlib import Path
import subprocess

ROOT = Path('/workspace/scratch/166b48a091b9/go-comparison-01')
REPO = Path('/workspace/scratch/166b48a091b9/worktrees/DB-Go-01-korda')
MANIFEST_SHA = '76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2'
OLD_URL = 'https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/final-metrics-01.json'


def strict_pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('duplicate JSON key ' + key)
        result[key] = value
    return result


def load(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=strict_pairs,
                      parse_constant=lambda s: (_ for _ in ()).throw(ValueError(s)))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def file_id(path):
    p = Path(path)
    return {'path': str(p), 'bytes': p.stat().st_size, 'sha256': digest(p)}


def timestamp(value):
    return datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))


def close_enough(a, b):
    return math.isclose(a, b, rel_tol=1e-11, abs_tol=1e-8)


checks = []
inputs = {}


def proof(name, passed, detail=None):
    record = {'name': name, 'passed': bool(passed)}
    if detail is not None:
        record['detail'] = detail
    checks.append(record)


def identify(name, path):
    value = file_id(path)
    inputs[name] = value
    return value


def hist_summary(bins):
    assert len(bins) == 8192 and all(type(n) is int and n >= 0 for n in bins)
    cumulative = list(itertools.accumulate(bins))
    total = cumulative[-1]
    quantiles = {}
    for percentile in (50, 95, 99):
        # Integer ranks, independently selected by cumulative binary search.
        rank = (total * percentile + 99) // 100
        index = bisect.bisect_left(cumulative, rank)
        exponent, fraction = divmod(index, 128)
        upper_ns = (1 << exponent) * (129 + fraction) / 128
        quantiles['p'+str(percentile)] = upper_ns / 1000
    return {'observations': total, 'microsecondsUpper': quantiles}


freeze = load(ROOT/'freeze.json')
events = [json.loads(line, object_pairs_hook=strict_pairs) for line in (ROOT/'campaign-events.jsonl').read_text().splitlines()]
host = load(ROOT/'host-before-final.json')
identify('freeze', ROOT/'freeze.json')
identify('campaignEvents', ROOT/'campaign-events.jsonl')
identify('hostBefore', ROOT/'host-before-final.json')
identify('independentCalculator', Path(__file__))
proof('exactly38 frozen files', len(freeze['files']) == 38)
proof('frozen paths unique', len({x['path'] for x in freeze['files']}) == 38)
frozen_readback = []
frozen_map = {}
for item in freeze['files']:
    observed = file_id(item['path'])
    match = observed['bytes'] == item['bytes'] and observed['sha256'] == item['sha256']
    frozen_readback.append({**observed, 'expectedSha256': item['sha256'], 'expectedBytes': item['bytes'], 'matched': match})
    frozen_map[item['path']] = item
    proof('frozen input ' + item['path'], match)
previous = freeze['previousCampaignFreeze']
previous_observed = identify('historicalFreeze', previous['path'])
proof('historical freeze unchanged', previous_observed['bytes'] == previous['bytes'] and previous_observed['sha256'] == previous['sha256'])
proof('campaign event monotonic order', all(a['monotonicNs'] < b['monotonicNs'] for a, b in zip(events, events[1:])))
proof('campaign freeze hash bound before execution', events[0]['kind'] == 'campaign-start' and events[0]['freezeSha256'] == inputs['freeze']['sha256'])
proof('supervisor actual affinity8', events[0]['cpuAffinity'] == [8])
starts = [e for e in events if e['kind'] == 'cell-start']
finishes = [e for e in events if e['kind'] == 'cell-finished']
proof('exactly two provider starts and completions', [e['provider'] for e in starts] == ['sqlite','postgresql'] and [e['provider'] for e in finishes] == ['sqlite','postgresql'])
proof('supervisor provider intervals serial', finishes[0]['monotonicNs'] < starts[1]['monotonicNs'])
proof('two actual child exits0', all(e['exitCode'] == 0 for e in finishes))
proof('campaign terminal exit0', events[-1]['kind'] == 'campaign-finished' and events[-1]['exitCode'] == 0)
proof('host identity matches reused historical machine/boot', host['hostname'] == '89394ab90f06' and host['bootId'] == '3c3f3b1f-818d-4772-85df-bafb4e207403')

runtime_sources = []
for item in freeze['files']:
    path = Path(item['path'])
    if 'benchmarks/db-perf/go' not in str(path):
        continue
    if path.name.endswith('_test.go') or path.name not in ('go.mod','go.sum','spin_amd64.s') and path.suffix != '.go':
        continue
    relative = str(path.relative_to(REPO))
    original = subprocess.check_output(['git','-C',str(REPO),'show',freeze['source']['runtimeBuildCommit']+':'+relative])
    equal = hashlib.sha256(original).hexdigest() == item['sha256']
    runtime_sources.append({'path': relative, 'buildCommitSha256': hashlib.sha256(original).hexdigest(), 'matchesFrozen': equal})
    proof('compiled-commit source blob '+relative, equal)
proof('runtime source closure checked', len(runtime_sources) == 11, len(runtime_sources))
local_tree = subprocess.check_output(['git','-C',str(REPO),'rev-parse',freeze['source']['localFinalCommit']+'^{tree}'],text=True).strip()
proof('local final tree equals recorded published tree', local_tree == freeze['source']['localFinalTree'] == freeze['source']['publishedTree'])

manifest_path = next(Path(x['path']) for x in freeze['files'] if x['sha256'] == MANIFEST_SHA)
manifest = load(manifest_path)
identify('manifest', manifest_path)
proof('manifest cryptographic binding', digest(manifest_path) == MANIFEST_SHA)
queries = manifest['queries']
names = [q['name'] for q in queries]
proof('35 unique frozen queries', len(names) == len(set(names)) == 35)
proof('full-cycle known row/SQL oracle', sum(q['expectedRows'] for q in queries) == 854 and sum(q['queryExecutionsPerOperation'] for q in queries) == 57)
cells = []

for provider, concurrency, rate in [('sqlite',4,3000),('postgresql',8,3600)]:
    before_check = len(checks)
    directory = ROOT/'measurements'/(provider+'-final-01')
    stem = 'go-c'+str(concurrency)
    r = load(directory/(stem+'.json'))
    c = load(directory/(stem+'.command.json'))
    p = load(directory/'plan.json')
    observer = load(directory/'runner.json')
    for name, file in [('result',stem+'.json'),('command',stem+'.command.json'),('plan','plan.json'),('runner','runner.json')]:
        identify(provider+':'+name,directory/file)
    proof(provider+' recorded plan is frozen', inputs[provider+':plan']['sha256'] == digest(freeze['plans'][provider]))
    proof(provider+' observer identities', observer['runnerSha256'] == '296e6b802d8bc1bcf964d7faa71d4adaa37226a867c17a9a3b5f00284f769b86' and observer['planSha256'] == inputs[provider+':plan']['sha256'] and observer['cpuAffinity'] == [8])
    proof(provider+' fixture and only Go timed', len(p['commands']) == 2 and p['commands'][0]['phase'] == 'fixture' and p['commands'][1]['cohort'] == 'go' and p['commands'][1]['phase'] == 'final')
    fixture = p['commands'][0]['argv']
    proof(provider+' initializer operations0', '--initialize' in fixture and fixture[fixture.index('--operations')+1] == '0')
    proof(provider+' external success evidence', c['exitCode'] == 0 and c['timedOut'] is False and not c['observerErrors'])
    argv = c['argv']
    proof(provider+' actual affinity/runtime env', argv[:7] == ['taskset','-c','0-3','env','GOGC=100','GOMEMLIMIT=off','GODEBUG='])
    flags = dict(zip(argv[8::2],argv[9::2]))
    expected_flags = {'--provider':provider,'--concurrency':str(concurrency),'--gomaxprocs':'4','--warmup':'64','--queue-capacity':'64','--seconds':'1800','--rate':str(rate),'--idle-seconds':'15'}
    proof(provider+' exact actual command flags', all(flags.get(k)==v for k,v in expected_flags.items()))
    proof(provider+' command path binding', Path(flags['--output']) == directory/(stem+'.json') and digest(flags['--manifest']) == MANIFEST_SHA)
    identity = file_id(argv[7])
    proof(provider+' executable independent hash', identity['sha256'] == r['ExecutableSha256'] == p['inputs']['consumer']['sha256'] == frozen_map[str(Path(argv[7]))]['sha256'])
    proof(provider+' core frozen runtime fields', r['Provider'] == r['CompiledProvider'] == provider and r['Runtime'] == 'go1.27.4' and r['Mode'] == 'prepared' and r['SessionMode'] == 'persistent' and r['Concurrency'] == concurrency and r['WarmupPerWorker'] == 64 and r['GOMAXPROCS'] == 4)
    proof(provider+' full ordered manifest coverage', r['ActualCaseIds'] == names and [x['Name'] for x in r['Cases']] == names)
    proof(provider+' fixed dataset/result dimensions', (r['RequestedRows'],r['BatchRows'],r['Tenants'],r['OrdersPerTenant']) == (32,32,8,1024))
    build = {x['Key']:x['Value'] for x in r['BuildInfo']['Settings']}
    deps = {x['Path']:x for x in r['BuildInfo']['Deps']}
    proof(provider+' build revision identity', build['vcs.revision'] == freeze['source']['runtimeBuildCommit'] and build['vcs.modified'] == 'false')
    proof(provider+' Linux amd64 native build', build['GOOS'] == 'linux' and build['GOARCH'] == 'amd64' and build['CGO_ENABLED'] == '1' and build['-buildmode'] == 'exe')
    driver = 'github.com/mattn/go-sqlite3' if provider=='sqlite' else 'github.com/jackc/pgx/v5'
    other = 'github.com/jackc/pgx/v5' if provider=='sqlite' else 'github.com/mattn/go-sqlite3'
    proof(provider+' one driver only', driver in deps and other not in deps and not deps[driver].get('Replace'))
    proof(provider+' pinned driver version', deps[driver]['Version'] == ('v1.14.53' if provider=='sqlite' else 'v5.11.0'))
    proof(provider+' exclusive provider build tags', set(build['-tags'].split(',')) == ({'sqlite','libsqlite3'} if provider=='sqlite' else {'postgresql'}))
    db = r['Database']
    if provider == 'sqlite':
        proof('SQLite exact mapped native image', digest(r['LoadedSQLite']['Path']) == r['LoadedSQLite']['Sha256'] == '2f693e43707c8174c862283185610abca5c671bbf17b6b1af7866bfbcd290282')
        proof('SQLite exact version/pragmas', (db['DatabaseVersion'],db['JournalMode'],db['Synchronous'],db['ForeignKeys'],db['BusyTimeoutMilliseconds']) == ('3.51.3','wal',2,1,5000))
    else:
        proof('PostgreSQL version/isolation/exec-cache policy', db['DatabaseVersion'].startswith('PostgreSQL 18.0 ') and (db['DefaultIsolation'],db['DefaultReadOnly'],db['QueryExecMode'],db['StatementCacheCapacity'],db['DescriptionCacheCapacity'],db['NamedPreparedStatementsOnVerificationConnection']) == ('read committed','off','exec',0,0,0))
        owner = load(directory/'postgres-owner.json')
        identify('postgresOwner',directory/'postgres-owner.json')
        proof('PostgreSQL real owner lifetime and successful shutdown', owner['exitCode'] == 0 and owner['startedMonotonicNs'] < c['startedMonotonicNs'] < c['finishedMonotonicNs'] < owner['finishedMonotonicNs'])
        proof('PostgreSQL server affinity', owner['argv'][:3] == ['taskset','-c','4-7'])
        settings = (directory/'postgres-settings.txt').read_text().splitlines()
        proof('PostgreSQL frozen durability/locale', settings[2:] == ['on','on','on','128MB','read committed','64','UTF8','UTF8','C|C'])
        identify('postgresSettings',directory/'postgres-settings.txt')
    o = r['OfferedLoad']
    counts = {k:o[k] for k in ('Planned','Attempted','Sent','Started','Completed','Succeeded','Failed','Rejected','Retries','Rows','SQLExecutions','OracleFailures')}
    proof(provider+' nonnegative integral raw counts', all(type(v) is int and v >= 0 for v in counts.values()))
    proof(provider+' fixed planned/attempted population', counts['Planned'] == counts['Attempted'] == 1800*rate)
    proof(provider+' admission/drain identities', counts['Sent']+counts['Rejected'] == counts['Attempted'] and counts['Sent']==counts['Started']==counts['Completed']==counts['Succeeded']+counts['Failed'])
    proof(provider+' no business/oracle/retry/cleanup failures', counts['Failed']==counts['OracleFailures']==counts['Retries']==r['Failed']==r['OracleFailures']==r['Retries']==0 and not r['Errors'] and not o['Errors'] and not o['ErrorClasses'] and not r['CleanupErrors'])
    proof(provider+' real observed application connections zero', r['ApplicationConnectionsAfterClose'] == [0]*concurrency and all(type(n) is int for n in r['ApplicationConnectionsAfterClose']))
    proof(provider+' top-level totals agree', all(r[k] == counts[k] for k in ('Planned','Started','Rejected','Failed','Rows','SQLExecutions','OracleFailures')) and r['Completed']==counts['Succeeded'])
    proof(provider+' no duplicate nested case population', r['Cases'] == o['Cases'])
    weighted_rows = weighted_sql = expected_xor = 0
    per_case = []
    for i,(case,q) in enumerate(zip(r['Cases'],queries)):
        n = case['Succeeded']
        expected_rows = n*q['expectedRows']
        expected_sql = n*q['queryExecutionsPerOperation']
        weighted_rows += expected_rows
        weighted_sql += expected_sql
        if n & 1:
            expected_xor ^= int(q['expectedDigestHex'],16)
        ok = case['Name']==q['name'] and type(n) is int and n>0 and case['Failed']==0 and case['Started']==n and case['Started'] <= (counts['Planned']+34-i)//35 and case['Rows']==expected_rows and case['SQLExecutions']==expected_sql
        proof(provider+' independent case '+q['name'],ok)
        per_case.append({'name':q['name'],'succeeded':n,'rows':case['Rows'],'expectedRows':expected_rows,'sql':case['SQLExecutions'],'expectedSQL':expected_sql,'verified':ok})
    proof(provider+' independent weighted rows/SQL', counts['Rows']==weighted_rows and counts['SQLExecutions']==weighted_sql,{'rows':weighted_rows,'sql':weighted_sql})
    proof(provider+' sum of case populations', sum(x['Started'] for x in r['Cases'])==counts['Started'] and sum(x['Succeeded'] for x in r['Cases'])==counts['Succeeded'] and sum(x['Failed'] for x in r['Cases'])==0)
    proof(provider+' independent global successful digest XOR', o['ResultDigestHex']==f'{expected_xor:016x}',f'{expected_xor:016x}')
    histograms = {key:hist_summary(o[key]) for key in ('SuccessServiceHistogram','SuccessScheduledHistogram','AllCompletedScheduledHistogram','StartDelayHistogram')}
    proof(provider+' four histogram populations', all(x['observations']==counts['Succeeded'] for x in histograms.values()))
    proof(provider+' successful/all-terminal populations identical', o['SuccessScheduledHistogram']==o['AllCompletedScheduledHistogram'])
    for key,raw in [('SuccessServiceHistogram','SuccessServiceLatencyMicrosecondsUpper'),('SuccessScheduledHistogram','SuccessScheduledLatencyMicrosecondsUpper')]:
        proof(provider+' independently selected '+key+' quantiles',all(close_enough(v,r[raw]['P'+k[1:]]) for k,v in histograms[key]['microsecondsUpper'].items()))
    series = o['Seconds']
    proof(provider+' contiguous full second indices', [s['Second'] for s in series]==list(range(len(series))) and len(series)>=1801)
    proof(provider+' all1800 offered seconds scheduled and progressing', all(series[i]['Planned']==rate and series[i]['Succeeded']>0 and series[i]['Rows']>0 and series[i]['Failed']==0 for i in range(1800)))
    proof(provider+' no offered work fabricated after deadline', all(s['Planned']==0 for s in series[1800:]))
    second_sums = {k:sum(s[k] for s in series) for k in ('Planned','Sent','Started','Succeeded','Failed','Rejected','Rows')}
    proof(provider+' independent per-second totals', all(v==counts[k] for k,v in second_sums.items()),second_sums)
    proof(provider+' per-second counts nonnegative integers', all(type(v) is int and v>=0 for s in series for v in s.values()))
    elapsed=(o['DrainedTicks']-o['StartedTicks'])/o['TimerFrequency']
    offered_seconds=(o['OfferedEndTicks']-o['StartedTicks'])/o['TimerFrequency']
    proof(provider+' continuous1800s clock then complete drain', o['TimerFrequency']==10**9 and o['DeadlineTicks']-o['StartedTicks']==1800*10**9 and o['StartedTicks']<o['DeadlineTicks']<=o['OfferedEndTicks']<=o['DrainedTicks'] and elapsed>=1800)
    proof(provider+' raw monotonic boundary consistency', r['SteadyStartMonotonicNs']==o['StartedTicks'] and r['SteadyEndMonotonicNs']==o['DrainedTicks'] and close_enough(r['EffectiveSeconds'],elapsed))
    proof(provider+' external command encloses actual operations', c['startedMonotonicNs'] < o['StartedTicks'] < o['DrainedTicks'] < c['finishedMonotonicNs'])
    proof(provider+' command finite timeout not reached', (c['finishedMonotonicNs']-c['startedMonotonicNs'])/1e9 < c['timeoutSeconds']==2115)
    mem_before,mem_after=r['MemoryBefore'],r['MemoryAfter']
    total_alloc=mem_after['TotalAlloc']-mem_before['TotalAlloc']
    gc=mem_after['NumGC']-mem_before['NumGC']
    pause=mem_after['PauseTotalNs']-mem_before['PauseTotalNs']
    proof(provider+' independently computed allocation delta', total_alloc==r['AllocatedBytes']==r['AllocatedAfter']-r['AllocatedBefore'] and total_alloc>=0)
    proof(provider+' independently computed process GC delta', gc==r['GoGCCount'] and pause==r['GoGCPauseNs'] and mem_after['NumForcedGC']==mem_before['NumForcedGC'] and r['GoForcedGCCount']==0)
    proof(provider+' offered-end memory within operation boundary', all(mem_before[k]<=o['MemoryAtOfferedEnd'][k]<=mem_after[k] for k in ('TotalAlloc','NumGC','NumForcedGC','PauseTotalNs')))
    user=r['ProcessAfter']['UserCpuSeconds']-r['ProcessBefore']['UserCpuSeconds']
    system=r['ProcessAfter']['SystemCpuSeconds']-r['ProcessBefore']['SystemCpuSeconds']
    cpu=user+system
    proof(provider+' independent CPU deltas', user>=0 and system>=0 and close_enough(user,r['UserCpuSeconds']) and close_enough(system,r['SystemCpuSeconds']))
    throughput=counts['Succeeded']/elapsed
    proof(provider+' throughput/CPU/alloc successful denominators', close_enough(throughput,r['SuccessPerSecond']) and close_enough(cpu/counts['Succeeded'],r['CpuSecondsPerSuccessfulOperation']) and close_enough(total_alloc/counts['Succeeded'],r['BytesPerSuccessfulOperation']))
    idle=r['Idle']
    proof(provider+' actual post-disposal idle interval', idle['RequestedSeconds']==15 and idle['ObservedSeconds']>=15 and timestamp(idle['StartedUtc'])>=timestamp(r['FinishedUtc']) and timestamp(idle['FinishedUtc'])<=timestamp(c['finishedUtc']))
    proof(provider+' idle without forced collection', idle['MemoryAfter']['NumForcedGC']==idle['MemoryBefore']['NumForcedGC']==0)
    proof(provider+' RSS and wait4 resource endpoints available', c['processLifetimeMaxRssBytes']>0 and idle['After']['RssBytes']>0 and r['ProcessAtExit']['PeakRssBytes']<=c['processLifetimeMaxRssBytes'])
    proof(provider+' wait4 CPU covers measured process CPU', c['processLifetimeUserCpuSeconds']>=user and c['processLifetimeSystemCpuSeconds']>=system)
    for filename,expected in c['files'].items():
        entry=identify(provider+':'+filename,directory/filename)
        proof(provider+' external retained file '+filename,entry['sha256']==expected)
    sample_count=steady_samples=missing_mem=0
    first_sample=last_sample=last_acquired=None
    max_gap_ns=0
    max_client_rss=0
    quota_available=[]
    with (directory/c['resourceSamples']).open() as stream:
        for line in stream:
            sample=json.loads(line,object_pairs_hook=strict_pairs)
            if first_sample is None:first_sample=sample['monotonicNs']
            if last_sample is not None:
                max_gap_ns=max(max_gap_ns,sample['monotonicNs']-last_sample)
                assert sample['monotonicNs']>last_sample
            assert sample['acquiredThroughMonotonicNs']>=sample['monotonicNs']
            last_sample=sample['monotonicNs'];last_acquired=sample['acquiredThroughMonotonicNs']
            sample_count+=1
            if r['SteadyStartMonotonicNs']<=sample['monotonicNs'] and sample['acquiredThroughMonotonicNs']<=r['SteadyEndMonotonicNs']:steady_samples+=1
            if sample['clientTotals']['rssComplete']:max_client_rss=max(max_client_rss,sample['clientTotals']['sampledRssBytes'])
            else:missing_mem+=1
            quota_available.append(sample['guestQuota']['available'])
    proof(provider+' sampled resource interval encloses steady window', first_sample <= r['SteadyStartMonotonicNs'] and last_acquired >= r['SteadyEndMonotonicNs'] and steady_samples>0)
    cell_checks=checks[before_check:]
    cells.append({'provider':provider,'passed':all(x['passed'] for x in cell_checks),'checks':len(cell_checks),'cases':per_case,
        'counts':counts,'expectedWeightedRows':weighted_rows,'expectedWeightedSQL':weighted_sql,'expectedXorDigest':f'{expected_xor:016x}',
        'independentlyDerived':{'throughDrainSeconds':elapsed,'actualOfferedSeconds':offered_seconds,'postOfferedDrainSeconds':elapsed-offered_seconds,
            'successfulOperationsPerSecond':throughput,'rejectionPercent':100*counts['Rejected']/counts['Attempted'],
            'histograms':histograms,'CPUSeconds':cpu,'CPUUserSeconds':user,'CPUSystemSeconds':system,'CPUMicrosecondsPerSuccess':cpu*1e6/counts['Succeeded'],
            'goHeapAllocatedBytes':total_alloc,'goHeapBytesPerSuccess':total_alloc/counts['Succeeded'],'goGCCount':gc,'goGCPauseNs':pause,
            'wait4PeakRSSBytes':c['processLifetimeMaxRssBytes'],'idleRSSBytes':idle['After']['RssBytes'],'idlePSSBytes':idle['After']['PssBytes'],
            'actualIdleSeconds':idle['ObservedSeconds'],'zeroApplicationConnections':r['ApplicationConnectionsAfterClose'],
            'successfulProgressSeconds':sum(s['Succeeded']>0 for s in series[:1800])},
        'interval':{'startedUtc':r['StartedUtc'],'finishedUtc':r['FinishedUtc'],'idleFinishedUtc':idle['FinishedUtc'],
            'steadyStartNs':r['SteadyStartMonotonicNs'],'steadyEndNs':r['SteadyEndMonotonicNs'],
            'commandStartNs':c['startedMonotonicNs'],'commandEndNs':c['finishedMonotonicNs']},
        'resources':{'samples':sample_count,'samplesFullyInsideOperations':steady_samples,'firstSampleNs':first_sample,'lastAcquiredNs':last_acquired,
            'maximumGapSeconds':max_gap_ns/1e9,'maximumCompleteSampleClientRSSBytes':max_client_rss,'memoryIncompleteSamples':missing_mem,
            'anyVisibleQuota':any(quota_available),'scope':'Raw non-atomic sampled process trees retained; sampled RSS is not substituted for wait4 peak, and server CPU is not inferred from PID snapshots.'},
        'driver':{'module':driver,'version':deps[driver]['Version'],'compiledProvider':r['CompiledProvider'],'executable':identity,'buildCommit':build['vcs.revision']}})

first,second=cells
proof('actual Go operation intervals nonoverlapping',first['interval']['steadyEndNs']<second['interval']['steadyStartNs'])
proof('actual Go whole command intervals nonoverlapping',first['interval']['commandEndNs']<second['interval']['commandStartNs'])
proof('actual post-disposal idle finishes before next Go operation',timestamp(first['interval']['idleFinishedUtc'])<timestamp(second['interval']['startedUtc']))

failed=[x for x in checks if not x['passed']]
accepted=not failed and len(cells)==2 and all(c['passed'] for c in cells)
review={'schemaVersion':1,'reviewedUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'independentOfVerifier':True,'method':'Separate Python calculation; never imports/runs verify_result.py or trusts accepted/status flags. Raw files, integer weighted oracles, cumulative histogram binary-search quantiles, per-second sums, monotonic/UTC boundaries, frozen SHA-256 bytes and git build-commit blobs were read independently.',
    'actualFinalCells':2,'requiredFinalCells':2,'allTwoFinalCellsAccepted':accepted,
    'delivery':'record-only/open; Korda#39 and Plan#35 remain draft; no merge, deployment, further benchmark or optimization is authorized by this review.',
    'source':freeze['source'],'inputs':inputs,'freezeFilesReadBack':len(frozen_readback),'frozenFiles':frozen_readback,'runtimeSourceBlobs':runtime_sources,
    'cells':cells,'checks':checks,'failedChecks':failed,
    'serial':{'wholeCommandGapSeconds':(second['interval']['commandStartNs']-first['interval']['commandEndNs'])/1e9,
        'idleToNextOperationGapSeconds':(timestamp(second['interval']['startedUtc'])-timestamp(first['interval']['idleFinishedUtc'])).total_seconds(),
        'campaignStartedUtc':events[0]['utc'],'campaignFinishedUtc':events[-1]['utc']},
    'limitations':['Same visible hostname/boot and frozen workload are verified; exclusive physical tenancy and inaccessible cgroup quotas are not established.',
        'SQL count is successful business SQL/control API calls, not provider-internal dispatches, wire replies or physical RTT.',
        'Go TotalAlloc/NumGC are runtime-specific heap/cycle observations; no .NET generation equivalence or framework-only allocation claim.',
        'Peak RSS is whole-command wait4; idle is actual post-close observation without forced GC; CPU is client operations through admitted-work drain.',
        'Per-operation raw DTO values are not persisted; fixed executable/source and per-operation validation code support the aggregate result/oracle evidence.'],
    'historicalComparisonSource':OLD_URL}

json_path=ROOT/'final-independent-review.json'
md_path=ROOT/'final-independent-review.md'
if json_path.exists() or md_path.exists():raise RuntimeError('Review output already exists; preserve prior evidence')
json_path.write_text(json.dumps(review,indent=2,ensure_ascii=False)+'\n')
lines=['# Independent review — completed Go comparison','',
       f'**Actual completed final cells: 2 / 2. Independent acceptance: {accepted}.**',
       '',f'{len(checks)} independently calculated checks; {len(failed)} failures. All38 frozen files were reread byte-for-byte through length and SHA-256, and11 runtime/module/assembly source blobs match the measured build commit.',
       '', 'This review uses a separate calculation program. It did not import or execute verify_result.py, run a database, build, test, change frozen source, or accept a result from status flags.',
       '', '**Delivery: record-only/open. Korda#39 and Plan#35 remain draft; no merge is part of this comparison.**','',
       '## Actual outcomes','',
       '| Provider | Success | Rejected | Rejected % | Success/s | Business rows | Business SQL/control | Digest XOR |',
       '|---|---:|---:|---:|---:|---:|---:|---|']
for c in cells:
    d=c['independentlyDerived'];n=c['counts']
    lines.append(f"| {c['provider']} | {n['Succeeded']:,} | {n['Rejected']:,} | {d['rejectionPercent']:.9f} | {d['successfulOperationsPerSecond']:.9f} | {n['Rows']:,} | {n['SQLExecutions']:,} | `{c['expectedXorDigest']}` |")
lines+=['','Each cell has all35 cases, zero business/oracle/retry/cleanup failures, complete admitted-work drain, and successful row-consuming work in each of1800 required seconds. Actual connection arrays are four/eight zeroes.','',
        '## Independently derived latency and resources','',
        '| Provider | Scheduled p50 / p95 / p99 ms upper | Service p50 / p95 / p99 ms upper | CPU µs/success | Go heap B/success | Go GC cycles | wait4 peak RSS MiB | Idle RSS MiB |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
for c in cells:
    d=c['independentlyDerived'];h=d['histograms'];scheduled=' / '.join(f"{h['SuccessScheduledHistogram']['microsecondsUpper'][key]/1000:.6f}" for key in ('p50','p95','p99'));service=' / '.join(f"{h['SuccessServiceHistogram']['microsecondsUpper'][key]/1000:.6f}" for key in ('p50','p95','p99'))
    lines.append(f"| {c['provider']} | {scheduled} | {service} | {d['CPUMicrosecondsPerSuccess']:.6f} | {d['goHeapBytesPerSuccess']:.6f} | {d['goGCCount']:,} | {d['wait4PeakRSSBytes']/1048576:.9f} | {d['idleRSSBytes']/1048576:.9f} |")
lines+=['','## Time, identity and scope','']
for c in cells:
    d=c['independentlyDerived'];i=c['interval'];lines.append(f"- {c['provider']}: operations {i['startedUtc']} → {i['finishedUtc']}; through-drain {d['throughDrainSeconds']:.9f}s; post-disposal idle {d['actualIdleSeconds']:.9f}s; idle finished {i['idleFinishedUtc']}.")
lines += [f"- Whole client commands are separated by {review['serial']['wholeCommandGapSeconds']:.9f}s; SQLite idle finishes {review['serial']['idleToNextOperationGapSeconds']:.6f}s before PostgreSQL operations begin.",
          '- SQLite uses external SQLite3.51.3, WAL/FULL/FK/5000ms and only its own driver. PostgreSQL uses18.0, READ COMMITTED/read-write, unnamed exec, zero statement/description cache, only its own driver, and normal owned-server shutdown.',
          '- The same visible host/boot is recorded as the earlier campaign, but invisible cgroup quota and exclusive hardware are not proved.',
          '- Historical Korda/Dapper measurements are reused from the earlier08:38–10:39UTC campaign; no previous measured cohort was rerun. The fixture initializer has operations0 and receives no performance credit.',
          '', '## Evidence and limits','',
          '[Detailed independent checks](final-independent-review.json) retain input hashes, all38 readback identities,11 source-commit matches,35 per-case weighted calculations per provider and raw resource-stream summaries.',
          '',f'[Historical exact metrics]({OLD_URL}) remain a separate reused source. Heap allocation and GC semantics differ between Go and .NET; no framework-only0B or global language-performance conclusion follows.',
          '', 'No failed checks.' if not failed else 'Failed checks: '+json.dumps(failed,ensure_ascii=False)]
md_path.write_text('\n'.join(lines)+'\n')
print(json.dumps({'accepted':accepted,'actualFinalCells':len(cells),'checks':len(checks),'failedChecks':failed,'frozenFilesReadBack':len(frozen_readback),'runtimeBlobs':len(runtime_sources),
    'metrics':[{k:c[k] for k in ('provider','counts','expectedXorDigest','independentlyDerived','resources')} for c in cells],
    'reviewJSON':str(json_path),'reviewMarkdown':str(md_path)},ensure_ascii=False))
