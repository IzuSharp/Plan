# Additional Go database comparison — completed 30-minute SQLite and PostgreSQL runs

## Result and scope

Both additional Go cells completed the requested 1,800-second offered interval, drained every admitted request, and passed the independent final arithmetic, identity, business-result, and resource-closure checks. SQLite achieved **2,992.478 successful operations/s**; PostgreSQL achieved **3,593.636/s**. Both had **zero failed business operations, zero oracle failures, zero retries, no command timeout, and no observer error**. Rejected arrivals remain part of the result: **13,540 SQLite** and **11,449 PostgreSQL** arrivals were not admitted. All 35 cases ran, with successful business progress in every required second. Sources: [SQLite raw result](measurements/sqlite-final-01/go-c4.json), [SQLite command receipt](measurements/sqlite-final-01/go-c4.command.json), [SQLite independent analysis](analysis/sqlite-final-01.json); [PostgreSQL raw result](measurements/postgresql-final-01/go-c8.json), [PostgreSQL command receipt](measurements/postgresql-final-01/go-c8.command.json), [PostgreSQL independent analysis](analysis/postgresql-final-01.json).

These are two new Go measurements. The four Korda/Dapper.AOT comparison cells are the previously completed 30-minute observations and were reused without rerunning them. The Go implementation is **database/sql with manually written typed DTO readers and business-result checks**; it is not a Go ORM. Each provider has its own executable and selected driver. The requested comparison is now complete; this report proposes no additional optimization, test, or workload. The frozen verifier passed 453 SQLite and 463 PostgreSQL checks. A separate calculation program, which did not import or execute that verifier, passed another 248 checks and reread all 38 frozen inputs. [Independent final review](final-independent-review.md), [detailed independent review](final-independent-review.json).

The measured Go operation intervals were **2026-11-26 13:09:31.178–13:39:31.179 UTC for SQLite**, then **13:39:49.078–14:09:49.080 UTC for PostgreSQL**. The serial campaign finished at **14:10:04.740 UTC**, including idle observation and normal owned-server shutdown. Both independent analyses explicitly set finalThirtyMinuteAccepted=true; preparation-only five-second runs receive no 30-minute credit. [Campaign state](campaign-state.json), [SQLite analysis](analysis/sqlite-final-01.json), [PostgreSQL analysis](analysis/postgresql-final-01.json).

## Conditions preserved

| Setting | SQLite | PostgreSQL |
| --- | --- | --- |
| Offered rate | 3,000 requests/s | 3,600 requests/s |
| Persistent workers / physical client connections | 4 | 8 |
| Offered interval | 1,800 seconds | 1,800 seconds |
| Queue / retries | Bounded FIFO 64; no retries | Same |
| Warmup | Every case verified, then 64 mixed operations per worker | Same |
| Dataset / requested rows | 8 tenants × 1,024 orders; 32 requested rows | Same |
| Post-disposal idle | Requested 15 seconds, no forced GC | Same |
| CPU placement | Client 0–3; observer 8 | Client 0–3; server 4–7; observer 8 |
| Go runtime | GOMAXPROCS=4, GOGC=100, GOMEMLIMIT=off | Same |
| Database | Exact frozen SQLite 3.51.3 shared image | Exact frozen PostgreSQL 18.0 tools |

SQLite retains prepared read statements and uses WAL, synchronous FULL, foreign keys, a 5,000 ms busy timeout, and BEGIN IMMEDIATE transactions. PostgreSQL uses pgx exec mode with statement/description caches disabled and no retained named server statement, preserving the reference Npgsql MaxAutoPrepare=0 policy. Pgx's text parameter encoding is recorded as a driver difference. Business SQL, parameter declarations, DTO/JSON materialization, related-child buffering/grouping, full-query early stop after three DTOs, transaction restore/rollback, and every-operation row/digest assertions follow the frozen manifest. database/sql iterates rows individually; the reference batch-row value 32 is metadata, not a configurable Go driver batch size. [SQLite raw identity/settings](measurements/sqlite-final-01/go-c4.json), [PostgreSQL raw identity/settings](measurements/postgresql-final-01/go-c8.json), [recorded source](https://github.com/IzuSharp/Korda/tree/d5f4f9d6616bad54a08aebb7d1aca7937b18eb93/benchmarks/db-perf/go).

The recorded local host is 89394ab90f06, Linux 6.18.57, x86_64, with the same boot identity and CPU placement as the earlier campaign. The readiness review rehashed all 38 frozen inputs and found no active local build, database, or other benchmark process before launch. The campaign supervisor reverified frozen inputs after each serial cell. The host record does not establish exclusive physical tenancy or a quota that cannot be observed through the unavailable cgroup-v2 mount. [Host observation](host-before-final.json), [readiness review](final-readiness-review.json), [input freeze](freeze.json), [campaign events](campaign-events.jsonl).

## New Go outcomes

Throughput is successful work divided by the observed offered-start-to-drain interval. This includes the completion of admitted work and excludes subsequent connection disposal and idle sampling. It is achieved throughput at a fixed arrival rate, not a maximum-capacity measurement.

| Provider | Planned / attempted | Successful | Rejected | Rejected % | Success/s | Through-drain seconds |
| --- | --- | --- | --- | --- | --- | --- |
| SQLite | 5,400,000 | 5,386,460 | 13,540 | 0.25074% | 2,992.478 | 1,800.000112125 |
| PostgreSQL | 6,480,000 | 6,468,551 | 11,449 | 0.17668% | 3,593.636 | 1,800.001636491 |

Accepted counts reconcile exactly with started and completed counts; planned equals attempted equals admitted plus rejected. All four latency histograms, every per-case total, and every per-second total reconcile independently. Both commands exited zero, and each worker's application connection count was observed as zero after close. Sources: [SQLite raw result](measurements/sqlite-final-01/go-c4.json), [SQLite command receipt](measurements/sqlite-final-01/go-c4.command.json), [SQLite independent analysis](analysis/sqlite-final-01.json); [PostgreSQL raw result](measurements/postgresql-final-01/go-c8.json), [PostgreSQL command receipt](measurements/postgresql-final-01/go-c8.command.json), [PostgreSQL independent analysis](analysis/postgresql-final-01.json).

## Historical comparison at the same fixed conditions

Historical values are reused from the [verified four-cell metrics at Plan 03efe57](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/final-metrics-01.json). No historical cohort was rerun.

| Provider / implementation | Evidence | Success/s | Successful requests | Rejected requests | Rejected % |
| --- | --- | --- | --- | --- | --- |
| SQLite / Korda | Reused historical | 2,706.936 | 4,872,560 | 527,440 | 9.76741% |
| SQLite / Dapper.AOT | Reused historical | 2,994.376 | 5,389,886 | 10,114 | 0.18730% |
| SQLite / Go database/sql | New Go run | 2,992.478 | 5,386,460 | 13,540 | 0.25074% |
| PostgreSQL / Korda | Reused historical | 3,400.012 | 6,120,073 | 359,927 | 5.55443% |
| PostgreSQL / Dapper.AOT | Reused historical | 3,591.997 | 6,465,624 | 14,376 | 0.22185% |
| PostgreSQL / Go database/sql | New Go run | 3,593.636 | 6,468,551 | 11,449 | 0.17668% |

Go and Dapper.AOT both complete almost all offered arrivals at these rates. Their small completion-throughput differences do not establish their relative maximum capacity. Go SQLite completed 3,426 fewer operations than historical Dapper over the interval; Go PostgreSQL completed 2,927 more. The lower completion rates of the historical Korda cells and their larger rejected counts remain visible rather than being removed from the comparison.

### Latency

All values below are **histogram upper bounds in milliseconds**. Scheduled response spans planned arrival to completion, including producer scheduling and queue delay. Service latency spans worker start to completion. Rejections have no invented completion latency. The two distributions answer different questions and must not be combined.

| Provider / implementation | Scheduled p50 / p95 / p99 ms | Service p50 / p95 / p99 ms |
| --- | --- | --- |
| SQLite / Korda | 20.185 / 33.423 / 49.545 | 0.545 / 4.882 / 12.976 |
| SQLite / Dapper.AOT | 0.208 / 3.031 / 8.585 | 0.111 / 1.597 / 4.325 |
| SQLite / Go database/sql | 0.253 / 2.146 / 6.586 | 0.104 / 1.425 / 3.441 |
| PostgreSQL / Korda | 14.877 / 27.132 / 38.273 | 0.889 / 10.551 / 16.581 |
| PostgreSQL / Dapper.AOT | 0.371 / 3.326 / 8.520 | 0.342 / 2.753 / 4.588 |
| PostgreSQL / Go database/sql | 0.408 / 2.867 / 5.898 | 0.305 / 2.458 / 4.063 |

Go's scheduled-response median was above the corresponding historical Dapper median on both databases, while its p95/p99 and service p99 were lower in these observations. In particular, SQLite Go scheduled p99 was **6.586 ms** versus Dapper **8.585 ms**, and PostgreSQL Go scheduled p99 was **5.898 ms** versus Dapper **8.520 ms**. This is a statement about the observed mixed workload and accepted populations, not a claim that Go is uniformly faster across individual queries. Exact upper bounds in microseconds and start-delay histograms are retained in [comparison.json](comparison.json). Sources: [SQLite raw result](measurements/sqlite-final-01/go-c4.json), [SQLite command receipt](measurements/sqlite-final-01/go-c4.command.json), [SQLite independent analysis](analysis/sqlite-final-01.json); [PostgreSQL raw result](measurements/postgresql-final-01/go-c8.json), [PostgreSQL command receipt](measurements/postgresql-final-01/go-c8.command.json), [PostgreSQL independent analysis](analysis/postgresql-final-01.json). Historical values are reused from the [verified four-cell metrics at Plan 03efe57](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/final-metrics-01.json). No historical cohort was rerun.

### Client CPU, RSS, and runtime allocation

Client CPU sums user and system CPU over steady work through admitted-work drain, including the producer, all client threads, and GC. Mean cores is total client CPU seconds divided by elapsed wall seconds. PostgreSQL server CPU is outside these figures. Peak RSS is the final **wait4 whole-command high-water**, including startup, warmup, output, and cleanup; idle RSS is the observed value after closing resources and the requested unforced idle period. Memory uses MiB = 1,048,576 bytes.

| Provider / implementation | Client CPU s | Client CPU µs/success | Mean CPU cores | wait4 peak RSS MiB | Idle RSS MiB | Runtime heap B/success |
| --- | --- | --- | --- | --- | --- | --- |
| SQLite / Korda | 4,859.354 | 997.290 | 2.700 | 43.652 | 37.184 | 24,790.092 |
| SQLite / Dapper.AOT | 3,142.248 | 582.990 | 1.746 | 33.836 | 29.844 | 7,431.767 |
| SQLite / Go database/sql | 2,998.755 | 556.721 | 1.666 | 23.730 | 21.625 | 3,139.808 |
| PostgreSQL / Korda | 5,141.226 | 840.060 | 2.856 | 50.234 | 41.258 | 25,490.045 |
| PostgreSQL / Dapper.AOT | 2,995.325 | 463.269 | 1.664 | 41.031 | 32.641 | 7,316.433 |
| PostgreSQL / Go database/sql | 2,515.403 | 388.867 | 1.397 | 21.539 | 15.488 | 4,132.255 |

The historical **SQLite Dapper wait4 peak is 35,479,552 bytes (33.836 MiB)**. Its earlier consumer endpoint reported 33,923,072 bytes; that earlier value is not used as the whole-command maximum. The JSON comparison preserves both fields with separate names. [Historical wait4 and endpoint records](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/final-metrics-01.json), [SQLite Go command](measurements/sqlite-final-01/go-c4.command.json), [PostgreSQL Go command](measurements/postgresql-final-01/go-c8.command.json).

The final column is Go TotalAlloc/success for the new cells and CLR managed allocation/success for the historical cells. Both are process-wide observations including business DTO/string/JSON, driver, and harness work. They do not isolate framework overhead or account for all native allocation. Ordinary Go DTOs may stay on the stack where escape analysis permits; C# and Go object-placement and GC semantics are different. These values must not be presented as equivalent counts of logical objects, framework-only bytes, or proof of a 0 B framework path.

### Descriptive percentage differences

Each entry is (new Go / historical comparator − 1) × 100. Negative latency, CPU, or memory values mean the observed Go value was lower; a negative throughput value means fewer achieved completions per second. These are single-run descriptive differences, without a repeated-run confidence interval or a saturation search.

| New Go vs historical baseline | Throughput | Scheduled p50 | Scheduled p99 | Service p99 | Client CPU µs/success | Reported runtime heap B/success | wait4 peak RSS |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SQLite vs Korda | +10.549% | -98.747% | -86.706% | -73.485% | -44.177% | -87.334% | -45.638% |
| SQLite vs Dapper.AOT | -0.063% | +21.675% | -23.282% | -20.455% | -4.506% | -57.752% | -29.866% |
| PostgreSQL vs Korda | +5.695% | -97.260% | -84.589% | -75.494% | -53.710% | -83.789% | -57.123% |
| PostgreSQL vs Dapper.AOT | +0.046% | +9.945% | -30.769% | -11.429% | -16.060% | -43.521% | -47.506% |

The allocation percentages compare each runtime's reported heap-allocation observation under the scopes above. They do not turn Go NumGC into a .NET generation count or identify an exclusive framework component.

## Go runtime and execution counters

| Observation | SQLite Go | PostgreSQL Go |
| --- | --- | --- |
| Go TotalAlloc delta, bytes | 16,912,450,224 | 26,729,703,808 |
| Go heap bytes / successful operation | 3,139.808 | 4,132.255 |
| Go NumGC before → after | 1 → 9187 | 2 → 10114 |
| Go NumGC delta | 9,186 | 10,112 |
| Forced GC delta | 0 | 0 |
| Cumulative GC stop-the-world pause delta, ms | 2,844.410 | 3,169.734 |
| Go-to-C calls during steady work | 222,218,466 | 0 |
| Successful-operation business SQL/control calls | 8,771,576 | 10,533,858 |
| Consumed business rows | 131,430,355 | 157,833,343 |
| Requested / observed idle seconds | 15 / 15.000357361 | 15 / 15.014834403 |
| Idle RSS, exact bytes | 22,675,456 | 16,240,640 |
| Idle PSS, exact bytes | 21,919,744 | 15,639,552 |
| wait4 lifetime peak RSS, exact bytes | 24,883,200 | 22,585,344 |
| wait4 process-lifetime CPU, seconds | 2,998.886 | 2,515.553 |

Go's NumGC values are whole-process **non-generational** counters. The pause column is the cumulative stop-the-world GC pause delta across the steady interval; it is not all concurrent GC CPU time and is not an operation-latency percentile. Forced collection was zero. Idle observations were recorded at their actual durations rather than rounded into an assertion of an exact 15-second wait. Sources: [SQLite raw result](measurements/sqlite-final-01/go-c4.json), [SQLite command receipt](measurements/sqlite-final-01/go-c4.command.json), [SQLite independent analysis](analysis/sqlite-final-01.json); [PostgreSQL raw result](measurements/postgresql-final-01/go-c8.json), [PostgreSQL command receipt](measurements/postgresql-final-01/go-c8.command.json), [PostgreSQL independent analysis](analysis/postgresql-final-01.json).

For reference, the reused .NET generation counts remain separate:

| Reused historical cell | .NET Gen0 / Gen1 / Gen2 steady delta |
| --- | --- |
| SQLite / Korda | 42,245 / 12,822 / 20 |
| SQLite / Dapper.AOT | 19,390 / 180 / 18 |
| PostgreSQL / Korda | 51,230 / 17,717 / 19 |
| PostgreSQL / Dapper.AOT | 10,949 / 6,996 / 122 |

These arrays are process-wide steady-window Gen0/Gen1/Gen2 deltas from the historical CLR consumers. There is no common “number of GCs” ranking across these arrays and Go's cycle counts. Historical cumulative start/end GC pairs and final exit endpoints were not all serialized, so none are reconstructed from other boundaries. [Historical GC scope](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/final-metrics-01.json).

The Go-to-C count measures runtime.NumCgoCall during steady work. SQLite's count includes real cgo crossings in its external-library driver; PostgreSQL's zero reflects this pgx workload's Go protocol path. It does not mean zero SQL, zero kernel calls, or zero network replies. Business SQL/control counts cover successful Go operations only, including transaction controls and independent persisted-state reads. Driver-internal messages, required protocol replies, and equivalent Korda command-FFI counts were not instrumented in these ordinary Go long runs and remain unavailable.

The owned PostgreSQL server's separate lifetime receipt records **2,279.963 CPU seconds**, including fixture creation and the complete Go command lifecycle. Its parent/live/reaped-child snapshots are non-atomic and do not prove full server-tree visibility. It is not a steady-operation server-CPU denominator and is not added to the client-per-success comparison. [PostgreSQL independent analysis](analysis/postgresql-final-01.json).

## Identity, retained preparation evidence, and record-only delivery

| Input | Identity |
| --- | --- |
| Go compiler | Go 1.27.4, Linux amd64; optimized native executables |
| SQLite Go driver | github.com/mattn/go-sqlite3 v1.14.53; external libsqlite3 build |
| PostgreSQL Go driver | github.com/jackc/pgx/v5 v5.11.0 through database/sql |
| Runtime source commit | 94eb3a7675a44e30c6f9ed6c7a7edda987fe36db |
| Published record source commit | d5f4f9d6616bad54a08aebb7d1aca7937b18eb93 |
| SQLite executable SHA-256 | 11d6ffcfcc93a1d4459d6da2f92c6e7b7d48ce788ff26ac4ca331cca02defd2a |
| PostgreSQL executable SHA-256 | a75f351d2e01c530442a93fc1d7d129bd2b38911b269a95f30ce677dcaec2eaa |
| SQLite shared image | 3.51.3; SHA-256 2f693e43707c8174c862283185610abca5c671bbf17b6b1af7866bfbcd290282 |
| PostgreSQL server | 18.0, same frozen tool executables as the historical campaign |
| Workload manifest SHA-256 | 76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2 |
| Input freeze SHA-256 | fc08a113b690b55a38aee9c1f295c65475058c81ed8ee4be0e1ec19d16a63fe8 |

The published record tree matches the final local tree. Compared with the exact runtime build commit, only independent tests and the result-analysis script were added afterward; the measured runtime source did not change. The source-history bundle retains the exact local build commits. [Freeze source explanation](freeze.json), [final readiness audit](final-readiness-review.json), [Korda record PR #39](https://github.com/IzuSharp/Korda/pull/39).

Preparation records are retained separately: the first build attempt failed to obtain VCS status in the scratch staging directory; the source was then placed and committed in the task worktree and built with normal VCS stamping. An initial `go test ./...` invocation also failed during test setup because it ran outside the module directory (`build/final-unit-tests-01.log` in the Go archive); subsequent invocations from the correct module directory passed. This preparation failure is retained and is not a failure of either final 1,800-second run. Both earlier combined-driver five-second runs and the final independent-provider five-second runs remain preparation records. Only the two completed final 1,800-second cells receive new long-run credit. No Korda/Dapper historical timing was rerun or relabelled.

Per the user's latest instruction, **Korda #39 and Plan #35 are records only and must remain open drafts; neither is to be merged and auto-merge must remain disabled**. Their source and evidence publication does not authorize a product release. The observed CI plan for #39 selected existing ownership/tooling/security checks; package build and release selections were empty. The complete values and source identities for this record are in [comparison.json](comparison.json). Archival and the requested local task cleanup are delivery steps handled separately; this measurement report does not claim filesystem cleanup has already occurred.
