# DB-Exec-11 — final measured execution-path result

## Accepted scope

Four serial Linux x64 Native AOT cells completed on 2026-11-26, each with at least
1,800 seconds of steady work across 35 mixed cases. Business and oracle failures
were zero. Both Korda cells returned all eight tracked owner categories to zero;
Dapper application connections returned to zero, while its internal driver owners
were not instrumented. This accepts the specified measurement scope, not Dapper
parity, maximum sustainable throughput, framework-only zero allocation or an
optimality claim.

Measured product: [`17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`](https://github.com/IzuSharp/Korda/commit/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa),
tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc`. SQLite used C4/R3000; PostgreSQL
used C8/R3600. Both used prepared persistent sessions, queue 64, batch/requested
rows 32, eight tenants × 1,024 orders and warmup 64 per worker. Runtime versions
were libpq/PostgreSQL 18.0, SQLite 3.51.3, Dapper.AOT 1.1.0, Npgsql 11.0.0 and
Microsoft.Data.Sqlite 11.0.0. The host was Linux x86_64/AMD EPYC 9V74 with client,
server and observer affinity separated. Physical hardware exclusivity and invisible
cgroup quotas were not established.

Both consumers used the same business manifest and result assertions. Normalized
business SQL and typed parameters were audited, but runtime wire SQL equality
was not established. Named/ordinal diagnostic differences and provider control
semantics were not erased. Separate short-before results below remain separate.

## Final mixed-load outcomes

Throughput below is successful work divided by the observed offered-start-to-
drain duration. It is achieved completion throughput at the frozen arrival rate,
not a saturation search. Planned equals attempted; accepted requests drain
completely; retries, business failures and oracle failures are zero.

| Cell | Attempted | Succeeded | Rejected | Rejected % | Success/s through drain | Through-drain seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SQLite / Korda | 5,400,000 | 4,872,560 | 527,440 | 9.7674 | 2,706.936 | 1800.027754542 |
| SQLite / Dapper.AOT | 5,400,000 | 5,389,886 | 10,114 | 0.1873 | 2,994.376 | 1800.002836842 |
| PostgreSQL / Korda | 6,480,000 | 6,120,073 | 359,927 | 5.5544 | 3,400.012 | 1800.014960741 |
| PostgreSQL / Dapper.AOT | 6,480,000 | 6,465,624 | 14,376 | 0.2219 | 3,591.997 | 1800.008237597 |

### Latency populations

Values are histogram **upper bounds**, in milliseconds. Scheduled-to-completion
includes producer scheduling and queue delay. Service covers worker start to
completion. Start delay is not pure queue residence. Rejected arrivals have no
invented completion latency. With zero failed accepted operations, the accepted
terminal and successful populations coincide in these records.

| Cell | Scheduled-to-completion p50 / p95 / p99 ms | Service p50 / p95 / p99 ms | Planned-arrival-to-start p50 / p95 / p99 ms |
| --- | ---: | ---: | ---: |
| SQLite / Korda | 20.185 / 33.423 / 49.545 | 0.545 / 4.882 / 12.976 | 19.137 / 30.802 / 43.778 |
| SQLite / Dapper.AOT | 0.208 / 3.031 / 8.585 | 0.111 / 1.597 / 4.325 | 0.035 / 0.942 / 4.784 |
| PostgreSQL / Korda | 14.877 / 27.132 / 38.273 | 0.889 / 10.551 / 16.581 | 12.976 / 22.282 / 32.244 |
| PostgreSQL / Dapper.AOT | 0.371 / 3.326 / 8.520 | 0.342 / 2.753 / 4.588 | 0.015 / 0.391 / 5.800 |

### CPU, memory and allocation

CPU is the **client process** operation interval through completion of admitted
work, before worker/Source disposal, including its threads. This workload drain
is distinct from the later native `Drained` owner snapshot. It is not
client-plus-PostgreSQL-server CPU. No complete per-cell server
CPU total is inferred from non-atomic PID snapshots or the unavailable cgroup.
Peak RSS below uses the runner's final **wait4 whole-command maximum**, including
startup and cleanup. The original endpoint VmHWM and sampled RSS were separate observations; SQLite Dapper's endpoint VmHWM is33,923,072 B, whereas its final wait4
maximum is35,479,552 B. Do not interchange those observations.

Managed B/success is whole-process end-to-end allocation, including business
DTO/string/JSON/List, harness, framework and driver. It is not exclusive framework
allocation. Framework-only bytes remain null. Memory is MiB (1,048,576 bytes).

| Cell | Client CPU s | Client CPU µs/success | Whole-command peak RSS MiB | Post-disposal idle RSS MiB | Actual idle seconds | Total managed B/success |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SQLite / Korda | 4,859.354 | 997.290 | 43.652 | 37.184 | 15.000038471 | 24,790.092 |
| SQLite / Dapper.AOT | 3,142.248 | 582.990 | 33.836 | 29.844 | 15.002442593 | 7,431.767 |
| PostgreSQL / Korda | 5,141.226 | 840.060 | 50.234 | 41.258 | 15.003852230 | 25,490.045 |
| PostgreSQL / Dapper.AOT | 2,995.325 | 463.269 | 41.031 | 32.641 | 14.999423321 | 7,316.433 |

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
| --- | ---: | ---: |
| SQLite / Korda | 42,245 / 12,822 / 20 | 42,248 / 12,823 / 20 |
| SQLite / Dapper.AOT | 19,390 / 180 / 18 | 19,391 / 180 / 18 |
| PostgreSQL / Korda | 51,230 / 17,717 / 19 | 51,235 / 17,717 / 19 |
| PostgreSQL / Dapper.AOT | 10,949 / 6,996 / 122 | 10,951 / 6,997 / 122 |

### SQL, FFI and protocol quantities

The ordinary Korda counters below are actual `After - Before` endpoints. SQL
means provider dispatch, including internal controls; it is not a server-side
successful-statement trace. libpq submissions count successful send/Sync API
submissions; they are not reply counts, packets or physical RTT. Dapper internal
counts are unavailable, not zero.

| Cell | SQL dispatches during operations | libpq submissions during operations | Additional submissions in Drained−After |
| --- | ---: | ---: | ---: |
| SQLite / Korda | 8,380,640 | 0 | 0 |
| SQLite / Dapper.AOT | unavailable | unavailable | unavailable |
| PostgreSQL / Korda | 9,903,990 | 42,366,008 | 16 |
| PostgreSQL / Dapper.AOT | unavailable | unavailable | unavailable |

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
All four have zero business failures. The [short comparison summary](preexisting-measurement-summary-01.md) retains its separate scope.

| Provider / cohort | Succeeded | Rejected | Success/s | Offered p50 / p95 / p99 ms upper | Client CPU µs/success | Total managed B/success |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SQLite / before | 65,213 | 294,787 | 542.872 | 118.489 / 213.910 / 276.824 | 2,943.625 | 34,006.138 |
| SQLite / candidate | 320,305 | 39,695 | 2,668.577 | 21.103 / 34.341 / 50.856 | 1,014.138 | 24,845.945 |
| PostgreSQL / before | 149,007 | 282,993 | 1,241.453 | 52.953 / 100.663 / 133.693 | 1,738.849 | 34,856.686 |
| PostgreSQL / candidate | 415,044 | 16,956 | 3,458.224 | 13.763 / 25.297 / 34.341 | 829.188 | 25,542.453 |

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
| --- | ---: | ---: | ---: | ---: |
| SQLite / 1 | 556.918 | 127.669 | 6.760 | 201.090 / 67.160 |
| SQLite / 100 | 8,324.360 | 350.357 | 47.150 | 259.732 / 107.440 |
| SQLite / 1,000 | 50,129.461 | 1,887.428 | 367.447 | 331.033 / 117.444 |
| PostgreSQL / 1 | 379.244 | 215.590 | 96.273 | 289.130 / 155.962 |
| PostgreSQL / 100 | 746.447 | 546.614 | 160.440 | 392.484 / 304.283 |
| PostgreSQL / 1,000 | 13,301.054 | 2,704.440 | 462.550 | 697.845 / 368.015 |

## Implemented decisions from driver to Fluent

The fixed-source Design record is
[execution-path-17da.md](https://github.com/IzuSharp/Korda-Design/blob/ca9348ad0b5cc93bc75c502460d8e1b75843d109/docs/database/execution-path-17da.md).
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


## Recorded delivery

[Product PR37](https://github.com/IzuSharp/Korda/pull/37) and
[Design PR20](https://github.com/IzuSharp/Korda-Design/pull/20) delivered the selected
path; Plan results were recorded in [PR34](https://github.com/IzuSharp/Plan/pull/34).
Product merge `7ff7b57b907b689defb880b8af62d83679608603` and Design merge
`ca9348ad0b5cc93bc75c502460d8e1b75843d109` were observed.
[Product main CI](https://github.com/IzuSharp/Korda/actions/runs/45807237435)
passed both independent provider publication/readback and public-package Native
AOT consumers at `0.1.0-preview.4`, after a PostgreSQL indexing timeout and
successful same-version retry. Long timings remain attached to the frozen ci.1
packages; they were not reassigned to rebuilt preview bytes.

All profiling and comparisons ran locally. Product CI selected its ordinary
correctness/package work. This document retains final results, reasons and
limitations; raw output, per-second samples, binaries, archives, upload manifests
and interrupted-session state are omitted from the current documentation tree.
