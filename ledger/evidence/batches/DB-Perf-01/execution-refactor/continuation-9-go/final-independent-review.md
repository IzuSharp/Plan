# Independent review — completed Go comparison

**Actual completed final cells: 2 / 2. Independent acceptance: True.**

248 independently calculated checks; 0 failures. All38 frozen files were reread byte-for-byte through length and SHA-256, and11 runtime/module/assembly source blobs match the measured build commit.

This review uses a separate calculation program. It did not import or execute verify_result.py, run a database, build, test, change frozen source, or accept a result from status flags.

**Delivery: record-only/open. Korda#39 and Plan#35 remain draft; no merge is part of this comparison.**

## Actual outcomes

| Provider | Success | Rejected | Rejected % | Success/s | Business rows | Business SQL/control | Digest XOR |
|---|---:|---:|---:|---:|---:|---:|---|
| sqlite | 5,386,460 | 13,540 | 0.250740741 | 2992.477591371 | 131,430,355 | 8,771,576 | `755849b7578d6975` |
| postgresql | 6,468,551 | 11,449 | 0.176682099 | 3593.636177248 | 157,833,343 | 10,533,858 | `9bb99dba0f17ed2a` |

Each cell has all35 cases, zero business/oracle/retry/cleanup failures, complete admitted-work drain, and successful row-consuming work in each of1800 required seconds. Actual connection arrays are four/eight zeroes.

## Independently derived latency and resources

| Provider | Scheduled p50 / p95 / p99 ms upper | Service p50 / p95 / p99 ms upper | CPU µs/success | Go heap B/success | Go GC cycles | wait4 peak RSS MiB | Idle RSS MiB |
|---|---:|---:|---:|---:|---:|---:|---:|
| sqlite | 0.252928 / 2.146304 / 6.586368 | 0.104448 / 1.425408 / 3.440640 | 556.720960 | 3139.808005 | 9,186 | 23.730468750 | 21.625000000 |
| postgresql | 0.407552 / 2.867200 / 5.898240 | 0.305152 / 2.457600 / 4.063232 | 388.866609 | 4132.255247 | 10,112 | 21.539062500 | 15.488281250 |

## Time, identity and scope

- sqlite: operations 2026-11-26T13:09:31.17815649Z → 2026-11-26T13:39:31.178607379Z; through-drain 1800.000112125s; post-disposal idle 15.000357361s; idle finished 2026-11-26T13:39:46.183873758Z.
- postgresql: operations 2026-11-26T13:39:49.077827636Z → 2026-11-26T14:09:49.079686602Z; through-drain 1800.001636491s; post-disposal idle 15.014834403s; idle finished 2026-11-26T14:10:04.099168358Z.
- Whole client commands are separated by 2.677236293s; SQLite idle finishes 2.893954s before PostgreSQL operations begin.
- SQLite uses external SQLite3.51.3, WAL/FULL/FK/5000ms and only its own driver. PostgreSQL uses18.0, READ COMMITTED/read-write, unnamed exec, zero statement/description cache, only its own driver, and normal owned-server shutdown.
- The same visible host/boot is recorded as the earlier campaign, but invisible cgroup quota and exclusive hardware are not proved.
- Historical Korda/Dapper measurements are reused from the earlier08:38–10:39UTC campaign; no previous measured cohort was rerun. The fixture initializer has operations0 and receives no performance credit.

## Evidence and limits

[Detailed independent checks](final-independent-review.json) retain input hashes, all38 readback identities,11 source-commit matches,35 per-case weighted calculations per provider and raw resource-stream summaries.

[Historical exact metrics](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/final-metrics-01.json) remain a separate reused source. Heap allocation and GC semantics differ between Go and .NET; no framework-only0B or global language-performance conclusion follows.

No failed checks.
