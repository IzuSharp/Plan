#!/usr/bin/env python3
"""Render the current Plan summary from preserved, already verified reports."""
import json
from pathlib import Path

ROOT = Path('/workspace/scratch/166b48a091b9/recovery')
PLAN = Path('/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan')
DEST = PLAN / 'ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8'
METRICS = json.loads((ROOT / 'final-metrics-01.json').read_text())
BASELINE = json.loads(Path('/workspace/scratch/fd78534029f7/measurements/baseline-analysis-01.json').read_text())
PHASE = json.loads(Path('/workspace/scratch/fd78534029f7/measurements/phase-analysis-01.json').read_text())
AUDIT = json.loads((ROOT / 'final-identity-audit-01.json').read_text())


def label(item):
    return ('SQLite' if item['provider'] == 'sqlite' else 'PostgreSQL') + ' / ' + ('Korda' if item['cohort'] == 'candidate' else 'Dapper.AOT')


def triple(hist, scale=1):
    return ' / '.join(f'{hist[key] / scale:,.3f}' for key in ('p50_us_upper', 'p95_us_upper', 'p99_us_upper'))


lines = ['''# Final local campaign and selected execution-path result — DB-Exec-11

## Observed outcome and delivery boundary

The four frozen, serial Linux x64 Native AOT cells completed on **2026-11-26**,
from **08:38:19 to 10:39:24 UTC (16:38:19–18:39:24 Asia/Shanghai)** including
fixture setup, drain, idle observations and normal PostgreSQL shutdown. Every
cell contains at least 1,800 seconds of steady work, all 35 mixed-workload cases,
and successful business progress in every required second. All four command
receipts have exit0, no timeout and no observer error. Business failures and
sticky-oracle failures are zero. Rejected arrivals are retained below.

The unchanged arithmetic analyzer reports four complete raw receipts and the
same recorded host with no overlap, including recorded post-disposal idle.
The unchanged identity/owner supplement passes: it rederives the original
**373 frozen inputs** and verifies **394 total inputs** when final evidence is
included, with `inputsUnchanged=true`. Both Korda cells return all eight tracked
owner categories to zero. Both Dapper cells return application-owned logical
connections to zero; their internal driver owners are not instrumented.

This accepts the specified four-cell measurement evidence. It does not establish
framework-only 0 B, Dapper parity, a maximum sustainable throughput, or exhaustion
of every possible optimization. The selected execution-path implementation and
its public package correctness are separately reviewed. Normal merge, existing
main CI and each provider's registry readback/public AOT outcome are tracked in
the later delivery receipt; they are not inferred from this local report.

Primary records: [arithmetic](final-analysis-01.json),
[identity/owner audit](final-identity-audit-01.json),
[exact metric extraction](final-metrics-01.json),
[supervisor](campaign-supervisor-01.json), and the three `*.command.json`
postprocessing receipts. The original analyzer's Markdown is retained as
[final-analysis-01.md](final-analysis-01.md). Its generic historical wording is
qualified by the exact scopes in this report.

## Frozen sources and workload

| Item | Exact binding |
| --- | --- |
| Measured product | [`17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`](https://github.com/IzuSharp/Korda/commit/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa), tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc` |
| Before product for the separate short comparison | `f0078da720e07031bc56464995af6791c41aaae8` |
| Reused Dapper mixed-consumer harness | `05fdd6b507bbfa9e971caa739784cf42dfb7199c`; its actual generated sources, restore, AOT executable and provider bindings remain distinct from the product commit |
| Original freeze SHA-256 | `fc1dae9be0a76b0de38c4f94c3836e47b398e10b5ff23f3c8f82313a3cb4bc1a` |
| SQLite candidate package SHA-256 | `059a0df6b2ed428788b2bf5a7212dd4d73d43cd642eee0de152b975efaf03d6a` |
| PostgreSQL candidate package SHA-256 | `46d5757c6dc48c721167476e2975f025b6884dc0c54b6956b9677a8eb4b29dec` |
| Runtime libraries | Frozen libpq/PostgreSQL18.0 and SQLite3.51.3, Dapper.AOT1.1.0, Npgsql11.0.0 / Microsoft.Data.Sqlite11.0.0; full source, package and executable identities are in the identity audit |
| Local machine | Node `89394ab90f06`, Linux6.18.57, x86_64, AMD EPYC9V74; CPU affinity client0–3, PostgreSQL4–7, observer8 |
| Workload | Prepared mode, persistent sessions, queue64, requested/batch rows32, 8 tenants × 1,024 orders, warmup64 per worker, all35 cases |
| SQLite | C4, offered3,000 operations/s, 1,800 seconds per cohort |
| PostgreSQL | C8, offered3,600 operations/s, 1,800 seconds per cohort |

The host observation does not establish exclusive physical hardware or invisible
cgroup quotas. The cgroup-v2 mount was unavailable. Light source/document reads
were confined to the observer CPU during timing; there was no concurrent local
build, profile, compression or second workload. The two provider runners and
their cohorts ran serially. The [before](host-before-final-recovery-01.json) and
[after](host-after-final-01.json) records preserve the actual environment.

Both ordinary consumers use the same business manifest and result assertions.
The source/generated-factory audit verifies typed parameters and normalized
business SQL. The original arithmetic report still exposes 35 diagnostic SQL
text differences per provider; named versus ordinal placeholders and diagnostic
representations are not silently erased. The source audit retains
`runtimeSqlTraceVerified=false`: no runtime wire trace or byte-for-
byte SQL equality is claimed. Provider transaction/health controls retain their
normal independent semantics.

## Final mixed-load outcomes

Throughput below is successful work divided by the observed offered-start-to-
drain duration. It is achieved completion throughput at the frozen arrival rate,
not a saturation search. Planned equals attempted; accepted requests drain
completely; retries, business failures and oracle failures are zero.

| Cell | Attempted | Succeeded | Rejected | Rejected % | Success/s through drain | Through-drain seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |''']
for item in METRICS['observations']:
    c = item['counts']
    lines.append(f"| {label(item)} | {c['attempted']:,} | {c['succeeded']:,} | {c['rejected']:,} | {100*c['rejected']/c['attempted']:.4f} | {item['successfulOperationsPerSecond']:,.3f} | {item['elapsedThroughDrainSeconds']:.9f} |")
lines += ['''
### Latency populations

Values are histogram **upper bounds**, in milliseconds. Scheduled-to-completion
includes producer scheduling and queue delay. Service covers worker start to
completion. Start delay is not pure queue residence. Rejected arrivals have no
invented completion latency. With zero failed accepted operations, the accepted
terminal and successful populations coincide in these records.

| Cell | Scheduled-to-completion p50 / p95 / p99 ms | Service p50 / p95 / p99 ms | Planned-arrival-to-start p50 / p95 / p99 ms |
| --- | ---: | ---: | ---: |''']
for item in METRICS['observations']:
    h = item['histograms']
    lines.append(f"| {label(item)} | {triple(h['offered'], 1000)} | {triple(h['service'], 1000)} | {triple(h['start_delay'], 1000)} |")
lines += ['''
### CPU, memory and allocation

CPU is the **client process** operation interval through completion of admitted
work, before worker/Source disposal, including its threads. This workload drain
is distinct from the later native `Drained` owner snapshot. It is not
client-plus-PostgreSQL-server CPU. No complete per-cell server
CPU total is inferred from non-atomic PID snapshots or the unavailable cgroup.
Peak RSS below uses the runner's final **wait4 whole-command maximum**, including
startup and cleanup. The raw endpoint VmHWM and sampled RSS remain separately
available; SQLite Dapper's endpoint VmHWM is33,923,072 B, whereas its final wait4
maximum is35,479,552 B. Do not interchange those observations.

Managed B/success is whole-process end-to-end allocation, including business
DTO/string/JSON/List, harness, framework and driver. It is not exclusive framework
allocation. Framework-only bytes remain null. Memory is MiB (1,048,576 bytes).

| Cell | Client CPU s | Client CPU µs/success | Whole-command peak RSS MiB | Post-disposal idle RSS MiB | Actual idle seconds | Total managed B/success |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |''']
for item in METRICS['observations']:
    cpu = item['cpu']; peak = item['resourceObservation']['processLifetimeWait4']['processLifetimeMaxRssBytes']
    lines.append(f"| {label(item)} | {cpu['userCpuSeconds']+cpu['systemCpuSeconds']:,.3f} | {cpu['seconds_per_success']*1e6:,.3f} | {peak/1048576:.3f} | {item['idleRssBytes']/1048576:.3f} | {item['idle']['ObservedSeconds']:.9f} | {item['managed']['bytes_per_success']:,.3f} |")
lines += ['''
Each cell requested15 seconds of post-disposal idle without forced GC. Actual
observations are preserved rather than rounded into a claim that every interval
was exactly or at least15 seconds. All four steady intervals independently
exceed1,800 seconds.

### Process-wide GC, two explicitly different boundaries

The first column is the process-wide **delta** from measurement start through
completion of admitted work, before worker/Source disposal. The later native
`Drained` owner snapshot has a different boundary. The
second is the process-wide **absolute cumulative count at the actual end of
offered arrivals**, including setup/warmup. Neither is a thread-local count.
The absolute process-exit or post-idle GC endpoint was not recorded. The generic
analyzer note about absent cumulative endpoints means no before/after absolute
pair; it does not erase the serialized offered-end cumulative arrays.

| Cell | Steady-through-drain GC0 / GC1 / GC2 delta | Absolute GC0 / GC1 / GC2 at offered end |
| --- | ---: | ---: |''']
for item in METRICS['observations']:
    m=item['managed']; delta=' / '.join(f'{v:,}' for v in m['gc_delta_counts']); cumulative=' / '.join(f'{v:,}' for v in m['offered_and_drain_raw']['gc_cumulative_at_actual_offered_end'])
    lines.append(f'| {label(item)} | {delta} | {cumulative} |')
lines += ['''
### SQL, FFI and protocol quantities

The ordinary Korda counters below are actual `After - Before` endpoints. SQL
means provider dispatch, including internal controls; it is not a server-side
successful-statement trace. libpq submissions count successful send/Sync API
submissions; they are not reply counts, packets or physical RTT. Dapper internal
counts are unavailable, not zero.

| Cell | SQL dispatches during operations | libpq submissions during operations | Additional submissions in Drained−After |
| --- | ---: | ---: | ---: |''']
for item in METRICS['observations']:
    n=item['nativeCounters']; a=n['After']; b=n['Before']; d=n['Drained']
    if 'SqlExecutions' in a:
        lines.append(f"| {label(item)} | {a['SqlExecutions']-b['SqlExecutions']:,} | {a['ProtocolSubmissions']-b['ProtocolSubmissions']:,} | {d['ProtocolSubmissions']-a['ProtocolSubmissions']:,} |")
    else:
        lines.append(f'| {label(item)} | unavailable | unavailable | unavailable |')
lines += ['''
The [six current17da FFI diagnostics](final-ffi-diagnostics-01.md) retain actual
symbol-indexed call/Pending/OK endpoints. They are separate15-second C1
instrumented processes without timing or allocation credit. Numeric32 observes
13 managed-to-native FFI calls and one SQL dispatch per successful32-row query;
PostgreSQL observes four libpq submissions per such query. The exact batch-boundary
second pull is not a second SQL execution. These counts are not relabelled as
1/100/1000-row phase or long mixed-workload counters.

[Counter semantics](../continuation-7/counter-semantics.md) separately retain the
real PostgreSQL proxy observations and fixed-source correctness assertions. The
healthy-commit experiment reduced its narrow-window dispatches2→1 and forwarded
ReadyForQuery replies6→4 under the exact confirmed-state predicate. Those are
the historical experiment's observed windows, not new30-minute reply traces.
The ordinary final consumers do not record FFI arrays or required reply counts.

## Same-condition before/current comparison, separately120 seconds

The four before/current observations use the same selected C4/R3000 SQLite and
C8/R3600 PostgreSQL conditions, data, result contract, queue and consumption.
They keep their original host record and source identity; they were not rebound
to the later recovery host record or relabelled as long measurements.
All four have zero business failures. The complete extraction retains exact
raw/report pointers in [preexisting-measurement-summary-01.json](preexisting-measurement-summary-01.json).

| Provider / cohort | Succeeded | Rejected | Success/s | Offered p50 / p95 / p99 ms upper | Client CPU µs/success | Total managed B/success |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |''']
for item in BASELINE['observations']:
    m=item['metrics']; c=m['measurement']['normalized']['counts']; name=('SQLite' if item['provider']=='sqlite' else 'PostgreSQL')+' / '+item['cohort']
    lines.append(f"| {name} | {c['succeeded']:,} | {c['rejected']:,} | {m['successfulThroughputThroughDrain']:,.3f} | {triple(m['measurement']['histograms']['offered'],1000)} | {m['client']['cpu']['seconds_per_success']*1e6:,.3f} | {m['client']['managed']['bytes_per_success']:,.3f} |")
lines += ['''
The same-condition short throughput improvement is approximately4.916× for
SQLite and2.786× for PostgreSQL. These are separate before/current comparisons;
no long-before value or long-run improvement ratio is fabricated.

## Single-row and DTO query phases

The same C++ Host's ordinary Fluent, warmed `.Prepare()` and complete parameterized
SQL routes were each measured for1/100/1000 rows, with actual Dapper.AOT consumers
as the external comparison. Every route pools three256-operation windows without
best-window selection. First-row time starts at submission and includes the first
DTO mapping. Four-phase total is the quantile of each operation's summed phases,
not a sum of individual quantiles. Dapper may perform cleanup within ReadComplete.
The full three-route tables, CPU, B/op, tails and original identities are retained
in [preexisting-measurement-summary-01.md](preexisting-measurement-summary-01.md).

| Provider / rows | Before prepared total p50 µs | Current prepared total p50 µs | Dapper.AOT total p50 µs | Before/current first-row p50 µs |
| --- | ---: | ---: | ---: | ---: |''']
for provider in ('sqlite','postgresql'):
    for rows in (1,100,1000):
        items={o['cohort']:o for o in PHASE['observations'] if o['provider']==provider and o['rows']==rows}
        routes={c:next(r for r in o['metrics']['routes'] if r['route']==('dapper-aot' if c=='dapper' else 'prepared')) for c,o in items.items()}
        total=[routes[c]['fourPhaseTotal']['p50Microseconds'] for c in ('before','candidate','dapper')]
        first=[routes[c]['phases']['SubmitToFirstRowTicks']['p50Microseconds'] for c in ('before','candidate')]
        lines.append(f"| {'SQLite' if provider=='sqlite' else 'PostgreSQL'} / {rows:,} | {total[0]:,.3f} | {total[1]:,.3f} | {total[2]:,.3f} | {first[0]:,.3f} / {first[1]:,.3f} |")
lines += ['''
## Implemented decisions from driver to Fluent

The fixed-source Design record is
[execution-path-17da.md](https://github.com/IzuSharp/Korda-Design/blob/ca1933e93678039b492f10a8b47045b11827f1a4/docs/database/execution-path-17da.md).
Its upstream sources, actual generated-consumer distinctions and contract/test
map remain authoritative. This continuation changes evidence/status, not the
frozen product path.

| Layer | Reuse, rewrite or delete | Retained contract/cost |
| --- | --- | --- |
| PostgreSQL | Reuse libpq18. Combine unnamed Parse+Describe under one Sync; delete redundant prepare confirmation; reuse observed natural EOF; omit only the proved healthy pre-COMMIT probe | Complete metadata before Execute, failed/unknown transaction handling, unfinished-reader drain and post-COMMIT/safe-return proofs remain |
| SQLite | Reuse sqlite3; prepare, inspect and bind one statement; delete duplicate describe/prepare | No step at open; finalize on completion/error; a cross-execution statement cache is not selected |
| Dynamic Fluent | Compile one bounded NWQC command directly through the native semantic compiler; delete repeated clause/schema wrapping, token patching and private builder clones | NWQC composition/traversal is still real work; C++ remains SQL authority |
| Prepared execution / Find | Reuse compiled parameter/projection layout; fixed-key Find uses a Source-owned exact-Table bounded shape and mapper, bypassing the general shape cache | Each execution captures independent values; arbitrary Fluent method SQL generation is not implemented |
| Execution values | Move typed Scalar ownership to the executable plan; delete native second NWDB encoding and Host reparsing | Mutable input snapshots and actual raw-SQL argument-capture checks remain |
| Native batches / DTOs | Direct bounded BatchWriter arena and scoped borrowed batch; delete per-cell vectors, row staging and whole managed frame copy; generated readers construct DTOs | Extent/NULL/UTF-8/numeric checks, lease generations and business result allocations remain |
| Scalar/control completion | Typed request/ready/take for Count/Any, nonreturning CRUD, transaction/savepoint and child close | Genuine administrative/uncertain-acceptance generic callers remain |
| Retirement | Reuse actual EOF and independent cleanup/notification/borrow fences | Queued final close remains; the narrower quiet-close experiment was rejected by its prospective performance rule |

Public APIs reach the new path through Query.Fluent → Query.Binding → C++ Host
→ HostStreamTransport → TypedStream → generated/static DTO reader. Existing
formal-entry and public package tests prevent silent fallback. The compatibility
ABI and differential-testing oracle have real callers and are not falsely
reported as dead code. Historical retirement and PostgreSQL completion guarantees
remain mapped to maintained C++ tests in the fixed Design record.

## Remaining gaps and bounded stopping decision

At the frozen offered rates, final Korda completion throughput is90.40% of
Dapper's SQLite result and94.66% of its PostgreSQL result. That does not mean
near-equivalent latency or maximum capacity: the latency and refusal tables show
the remaining gap. Korda client CPU/success is about1.71×/1.81×, and total managed
B/success about3.34×/3.48× the corresponding Dapper result. Prepared phase latency
also remains materially higher, especially the SQLite single-row path.

Framework-only0 B is not achieved/proven. Source still constructs execution
ownership/transport/controller/enumerator objects and nonempty value frames.
The separate mapper/List allocation overlay records actual scopes but includes
codec/driver temporary work; subtracting those scopes from a different mixed
workload would not establish exclusive framework allocation.

The [independent stopping review](final-stopping-review-01.md) distinguishes
necessary snapshot/lifetime/admission/retirement responsibilities from current
encoding, copying, hashing and queue choices. Remaining candidates include the
general immutable shape-cache lookup, SQL/Expectation copies, dynamic composition,
value ownership and per-batch dispatch. Their individual cost and the benefit of
a safe replacement have not been isolated. Physical statement caching and
source-generated SQL for arbitrary fixed Fluent methods remain unselected.

The evaluated quiet-close alternative failed its predeclared two-round rule:
PostgreSQL single-row read-complete changed direction, and SQLite1000-row pooled
total p50 regressed6.78% beyond the5% guard. The earlier inline-completion idea
had a real post-publication exception/ownership problem and supplied no timing
credit. Retain the selected, validated17da candidate rather than credit either
rejected alternative. Preserve the measured gains, remaining gaps and unmeasured
questions. This is a bounded decision about the alternatives actually evaluated;
it is **not a proof that no further measurable improvement can exist**.

## CI, review and delivery

The required `python3 eng/ci/impact.py origin/main --output artifacts/plan.json`
was rerun on the exact product-equivalent tree. The retained [actual plan](impact-current-01.json)
selects interop, linux, postgresql and sqlite, with independent provider package
checks. Benchmark ownership introduces no execution action. There is no new
performance workflow, job, button, schedule or hidden load in ordinary tests.

The existing product PR CI succeeded at exact17da:
[run45772470391](https://github.com/IzuSharp/Korda/actions/runs/45772470391).
Its actual synthetic merge commit177eb3d has parents main e063f2e and17da and
the same product treebc9087d. Exact independently built17da package/AOT gates
already passed for both providers; development assertion counts are not relabelled
as newly run package tests. Product code remains unchanged by this continuation.

The three source reviews, [final arithmetic/identity review](review-final-results-01.md),
[final implementation/scope review](review-final-implementation-01.md) and
[stopping review](final-stopping-review-01.md) are independent technical reviews,
not impersonated GitHub approvals. Existing document/history gates retain their
original scopes. The known old-current-tree Plan verifier failure and its correct
fixed38f8ce8 historical replay remain preserved; no threshold or verifier is changed.

Normal merges and observation of existing main publication are authorized.
Each provider's selected version, source tree, registry readback and actual public
Native AOT consumer must be observed separately. A future rebuilt preview package
is not assigned the exact measured ci.1 binary hashes; tree/source equivalence
and release-byte verification have distinct receipts.

## Evidence retention

The unchanged archive helper is used after all workloads and independent result
reads. It retains original final JSON/JSONL/stdout, commands, generated/source
identities, restore/validation text, analysis, reviews and the already verified
pre-final archive as an explicitly identified historical dependency. Package,
database and compiled binary bytes are excluded with actual identity records;
the archive is not a ready-to-run binary/database bundle.
''']
archive=Path('/workspace/scratch/166b48a091b9/final-evidence-01/receipt.json')
if archive.exists():
    receipt=json.loads(archive.read_text())
    lines.append('The actual archive receipt and manifest are retained under [final-evidence-01](final-evidence-01/README.md). Full top-level archive-member readback, original rehash and root-inventory checks must be read from that receipt. The nested pre-final archive is checked as a byte object; its earlier inner-member verification remains a separate historical receipt.\n')
else:
    lines.append('At this local report preparation checkpoint, the final archive is pending. Its completed receipt, exact hashes and readback result will be added before publication; no archival success is inferred here.\n')
DEST.mkdir(parents=True,exist_ok=True)
(DEST/'final-report.md').write_text('\n'.join(lines).rstrip()+'\n')
print(json.dumps({'report':str(DEST/'final-report.md'),'observations':len(METRICS['observations']),'archivePresent':archive.exists()}))
