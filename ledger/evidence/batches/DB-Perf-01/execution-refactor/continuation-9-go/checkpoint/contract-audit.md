# Go comparison: frozen workload contract audit

## Scope and source precedence

The user requested only one additional Go SQLite 1,800-second run followed by one Go PostgreSQL 1,800-second run. Previously completed Korda and Dapper cohorts must not be rerun. This audit performed file reads and SHA-256 verification only; no workload, build, original-source edit, or deletion occurred.

The actual four-cell campaign is `benchmarks/db-perf`, **not** `benchmarks/Database/campaign`. Use these source identities:

- Frozen implementation/runner commit `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`, tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc`.
- Runner `/tmp/DB-Exec-10-pack-sqlite-02/benchmarks/db-perf/run.py`, SHA-256 `296e6b802d8bc1bcf964d7faa71d4adaa37226a867c17a9a3b5f00284f769b86`.
- Exact SQL/data/result manifest `.../benchmarks/db-perf/workload/queries-v3.json`, SHA-256 `76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2`.
- Actual matched Dapper consumer directories `/workspace/scratch/4a65d70f0fe1/consumers/dapper-matched-sqlite-01` and `dapper-matched-postgresql-01`, built from harness commit `05fdd6b507bbfa9e971caa739784cf42dfb7199c`. All 17 sources in each `build-receipt.json` were rehashed and matched; both workload manifests match the hash above.
- Actual Dapper behavior comes from those directories' `Workload.cs`, `Contracts.generated.cs`, `LifecycleCases.cs`, `Oracles.cs`, `Digest.cs`, `ReadStream.cs`, `Measurement.cs`, `OfferedLoad.cs`, `Driver.cs`, and `Models.cs`. Generated lifecycle factories were already bound by `generated-sql-contract.json`.
- The manifest includes historical prose under `lifecycle.actualProviderOverhead`/`independentOrmSql` saying Dapper omits LIMIT 2. **Do not use that stale prose as the matched SQL contract.** Matched `LifecycleCases.cs` plus `lifecycle-sql-policy.json` and `sql-contract.json` contain the fully qualified projections and LIMIT 2; the manifest's canonical `lifecycle.steps[].sql` matches this business SQL.

## Frozen operating conditions

| Setting | SQLite | PostgreSQL |
|---|---|---|
| Offered duration | 1,800 s | 1,800 s |
| Client workers / persistent connections | 4 | 8 |
| Offered rate | 3,000/s | 3,600/s |
| Planned arrivals | 5,400,000 | 6,480,000 |
| Admission queue | Bounded FIFO, 64 jobs | Same |
| Client CPU affinity | 0–3 | 0–3 |
| Database CPU affinity | In client | 4–7 |
| Observer affinity | 8 | 8 |
| Warmup | Verify all 35 once, then 64 mixed operations per worker | Same |
| Idle sample | After worker/connection/pool disposal, 15 s, no forced GC | Same |
| Dataset | 8 tenants, 1,024 orders per tenant, 256 customers | Same |
| Requested rows / batch rows | 32 / 32 | 32 / 32 |
| Mode | prepared + persistent | prepared + persistent |

Use the exact selected SQLite shared library `/workspace/scratch/4a65d70f0fe1/consumers/direct-native/libsqlite3.so`, SHA-256 `2f693e43707c8174c862283185610abca5c671bbf17b6b1af7866bfbcd290282`; another bundled amalgamation is not an identical database build. SQLite connections enable foreign keys, WAL, synchronous FULL, busy timeout 5,000 ms. Transactions use BEGIN IMMEDIATE. Exact mapped library identity and compile options should be captured.

PostgreSQL executable directory is `/workspace/scratch/4a65d70f0fe1/tools/postgres/install/bin`. Reuse the frozen runner's database context: `initdb -U korda -A trust --no-locale --encoding=UTF8`; TCP localhost, no Unix socket; max_connections=64, fsync=on, synchronous_commit=on, full_page_writes=on, timezone=UTC, shared_buffers=128MB, default_transaction_isolation=read committed. No statement logging/profiling in formal timing. Do not claim exclusive physical host or a known cgroup quota without new evidence.

## What prepared and persistent actually mean

Dapper's read call sites use constant SQL, reusable parameter records, and generated `[CacheCommand]` factories. PostgreSQL explicitly sets `MaxAutoPrepare=0`; its receipt does not assert server-prepared retention. The four transaction cases use `[CacheCommand(false)]` and include command/parameter construction in each operation. Go must report its actual driver and cache/preparation policy rather than claim that every route's internal prepared mechanism is identical. Do not omit transactions' construction cost or flatten the transaction into one multi-statement request. Use ordinary public driver calls and fully await/finish result cleanup before ending an operation.

Each worker owns one persistent connection. Warmup runs concurrently across workers, but each worker runs its own operations serially. The retained connection also services the transaction's independent persisted-state lookup after transaction completion/disposal.

## SQL, types, materialization and digest

The manifest is machine-complete: `queries[]` contains provider SQL, ordered parameters with `kind` and `value`, result-column name/alias/kind/nullability, expected row count and digest, materialization, and execution counts. Read this directly or generate fixed Go source from it; do not regenerate SQL using another query builder. PostgreSQL uses the exact `$N` SQL. SQLite uses exact ordinal `?`; the historical Dapper-only permitted named-placeholder rewrite is not necessary for Go.

Read every ordinary result to exhaustion, map the declared typed result, hash the owned values, then check row count and digest on **every** operation. JSON must actually deserialize to Channel/Gift; do not hash raw JSON or substitute known fixture values. PostgreSQL money is exact numeric/decimal and must convert to signed integer cents without binary floating-point loss; SQLite already stores integer cents. Null is distinct from zero/empty. Nullable integer/money hashes a presence byte before the value. Strings hash signed Int64 UTF-8 byte length followed by bytes; null length is -1. Int64 is eight little-endian bytes; bool one byte 0/1. FNV-1a starts at 14695981039346656037, multiplies by 1099511628211 after XOR, modulo 2^64, with no row separators.

Full Order field order: TenantId, Id, CreatedAt, nullable CustomerId, Total cents, nullable Note, Version, Settings.Channel, Settings.Gift, InternalMemo. Other columns follow manifest order. Stream DTOs are consumed one at a time; do not replace DTO/JSON mapping with untyped driver-value hashing. Go allocation escape behavior may naturally differ from C# heap objects and should remain visible in results.

`related` is special: one UNION ALL query for exactly 32 parent keys, 96 parameters with parent ordinal Int32 then tenant/id Int64. Buffer and retain all 53 child DTOs, group by `__korda_parent_index` (0–31), retain empty groups, sort each group by child Id. Digest each parent Id, child count, then child Id/TenantId/OrderId/Product/Quantity; do not hash internal ordinal. Rows=53 excludes group headers. A streaming-only digest would omit required materialization work.

`early-stop` issues the full 1,024-limit wide query, consumes exactly three DTOs, and closes the reader before returning. Remaining protocol/native cleanup is included in operation latency. Do not change SQL LIMIT to 3.

## Transaction and exceptional-path contract

All four transaction cases target tenant 1 / Id 1,024. Verify the full original row equals the seed, not only the fields being changed; original Version=1, Note=note-0, TotalCents=38,997. Reads use LIMIT 2 and require exactly one row. Check each update's affected count. Complete transaction retirement before independent persisted-state lookup and require all nine fields to equal the original.

- `tx-commit`: begin, find original/hash, update Note=perf-mutated and Version=2 (affected1), find changed/hash, restore original Note/Version (affected1), commit, independent find persisted/hash. Seven business SQL/control executions; three result rows.
- `tx-rollback`: begin, original/hash, update+affected1, changed/hash, rollback, persisted/hash. Six executions; three rows.
- `partial-update`: like tx-commit but only Note becomes NULL; Version and all omitted fields remain unchanged; restore Note only. Seven executions; three rows.
- `stale-conflict`: begin, original/hash, checked update expectedVersion1 -> Version2 (affected1); stale Note write expectedVersion1 must affect0; hash boolean true, rollback, persisted/hash. Six executions; two rows. The expected optimistic conflict is successful business behavior, not a failed request. No retries.

Cancellation and simultaneous optimistic-conflict diagnostics are **not among the timed 35 cases**. `LifecycleVerification.cs` separately tests pre-cancel; active PG cancellation with pg_sleep(2) and cancel after30ms plus connection reuse; SQLite active async-token interruption was explicitly unsupported in that comparison; simultaneous two-session CAS expects one winner and one conflict and restores seed. Go may run only its own relevant correctness diagnostics outside timing, preserving supported/unsupported differences. Do not insert cancellation jobs into formal mixed arrivals. Unexpected errors, cleanup errors and oracle failures must remain distinguishable; failure while retiring a failed reader must not erase the original failure.

## Scheduler and measurement port

The actual scheduler is the copied consumer `OfferedLoad.cs`, SHA-256 `2adb14584476da8b8a49bb2e5db6bd85b136f3823aee5e2f004bc263eb2bc92b`.

1. Preallocate queue, worker state, per-second arrays and histograms outside the allocation/timing boundary. Producers/consumers wait on a start gate.
2. Planned arrivals = ceil(seconds * rate). Arrival i is due at start + trunc(i * timer_frequency / rate). Case index = **global arrival i modulo 35**, so rejected arrivals still advance case selection. Do not use per-worker iteration counters.
3. Dedicated producer waits until each due instant; original sleeps 1ms only when more than2ms remains, otherwise spins32 per check. Then nonblocking FIFO admission: enqueue if capacity permits, else count an explicit rejection. It never waits for capacity and never retries. If delayed, it still attempts every planned arrival rather than silently dropping schedule slots. Producer waits until deadline after last scheduled job, closes queue; consumers drain all accepted work.
4. Reconcile planned=attempted=sent+rejected; sent=started=succeeded+failed; completed=succeeded+failed. Record actual dispatch/start/completion/rejection by elapsed second, planned count by scheduled second; capture rows, per-case counts, error classes, oracle failures, retries=0.
5. Four histograms: successful service (start→finish), successful scheduled response (planned→finish), all completed scheduled response, start delay (planned→start). Rejections have no invented latency. Failure responses belong only in all-completed histogram; service histogram contains successes only.
6. Histograms have8192 bins: nanoseconds clamp >=1; exponent=floor(log2(ns)); index=exponent*128 + floor((ns-2^exponent)*128/2^exponent). Quantile rank=ceil(N*q); report selected bin upper bound `2^e*(1+(fraction+1)/128)/1000` microseconds (<0.782% width), not interpolated exact percentiles.
7. End-to-end duration ends when all admitted work drains, before worker/connection/source disposal. Throughput is succeeded / this duration, not planned duration alone. The existing historical four-cell figures use this boundary.
8. Process CPU reads immediately before/start and after operation drain; includes producer, harness, all Go threads and GC, excludes PG server CPU. Whole-command wait4 CPU/maxRSS is a separate lifetime metric. After all DB resources close, take before/after15s idle RSS/PSS and idle CPU without forcing collection.
9. Go `runtime.MemStats.TotalAlloc` delta and NumGC/process pause counters can provide whole-process allocation/GC data, but label them as Go heap bytes/Go GC; do not fabricate .NET Gen0/1/2 or say this is framework-only allocation. Preserve business DTO/string/JSON + harness overhead in raw allocation. Goroutine scheduling/cgo/native allocation are not the .NET suspension counter; report unavailable rather than falsely zero-equivalent.

## Reuse boundaries and evidence

Reuse frozen `run.py` for external resource JSONL, wait4 lifetime peakRSS, PostgreSQL ownership/settings and command receipts. Its plan can contain fixture+Go only and fresh output paths. The fixture candidate executable's `--initialize --operations 0` is initialization, not another measured Korda cohort; its warmup remains outside Go timing. Alternatively reproduce exactly the initializer schema/data from `managed/Korda/Dataset.cs`, with independent fixture verification. Preserve fixture provenance either way.

Plans are `/workspace/scratch/fd78534029f7/measurements/plans/{sqlite,postgresql}-final-01.json`; full freeze is `/workspace/scratch/fd78534029f7/measurements/final-freeze-01.json`. SQLite plan SHA-256 `2cc385eebeb2d02b23dee2dd29559a667ea2723051967928ac8bd24a45684718`; PG `c5568d3fb78b7c11c888dcf0d458ec2559d23862d764fe27aa14e43dba780bc2`.

Resource/accounting helpers live under `benchmarks/db-perf/analysis` (`raw_metrics.py`, `resource_metrics.py`, `strict_io.py`, `identity_binding.py`). Plan `continuation-3/analysis/analyze_execution.py` provides arithmetic; `continuation-7/recovered-short-evidence/tools/analyze_command_single_v2.py` reads existing consumer schema. These may assume route/schema names: adapt explicitly for Go and retain the original; do not claim old acceptance validators automatically cover a new runtime. Keep source hashes, module versions, binary identity, command, environment, SQL/parameter contract check, raw outcomes/histograms/time series and rejection/failure evidence. All resulting artifacts must be durably archived and read back before the requested local cleanup.

## Ordered cases and exact oracle

| Index | Case | Rows | FNV-1a hex | Business SQL/control executions |
|---:|---|---:|---|---:|
| 0 | numeric | 32 | `68dd9f773b4eaf45` | 1 |
| 1 | text | 32 | `ad4cf192ab829540` | 1 |
| 2 | money | 32 | `090e9bbb08f81c71` | 1 |
| 3 | json | 32 | `5d85e9fa1058a30d` | 1 |
| 4 | wide | 32 | `c164e0de5cac73ca` | 1 |
| 5 | optional-filter | 32 | `93ba583f1d550f3e` | 1 |
| 6 | range | 32 | `1e687d7ee1b01f45` | 1 |
| 7 | left-join | 32 | `8098d14e347e12ff` | 1 |
| 8 | inner-join | 32 | `b514f9c828776c83` | 1 |
| 9 | null-notes | 32 | `047ecbc755943285` | 1 |
| 10 | literal-note | 32 | `960414b0f379ef8e` | 1 |
| 11 | customer-totals | 9 | `32ef708e4ab6105a` | 1 |
| 12 | product-totals | 32 | `d8f8be91929cef24` | 1 |
| 13 | empty-sum | 1 | `af63bd4c8601b7df` | 1 |
| 14 | cursor | 32 | `22bcfc48e69b5245` | 1 |
| 15 | offset | 32 | `bc492b2e59009ac5` | 1 |
| 16 | exists | 1 | `89cd31291d2aefa4` | 1 |
| 17 | in-subquery | 32 | `7c5f7ec6c1ff260d` | 1 |
| 18 | cte | 32 | `e0a534056f1e1045` | 1 |
| 19 | window | 32 | `6913cf7bd98734c3` | 1 |
| 20 | union-all | 32 | `373ba57117d2a6a5` | 1 |
| 21 | union | 24 | `d57dad5c7153e63d` | 1 |
| 22 | intersect | 8 | `1d2181af31a9863d` | 1 |
| 23 | except | 8 | `c4485a69ea81a02d` | 1 |
| 24 | running-total | 32 | `c4bf4fa4e24f2f39` | 1 |
| 25 | three-join | 32 | `d8acb960a36af980` | 1 |
| 26 | anti-association | 32 | `014dabe6105edf0c` | 1 |
| 27 | nullable-order | 32 | `14e14329da4216a5` | 1 |
| 28 | raw-sql | 32 | `ad4cf192ab829540` | 1 |
| 29 | related | 53 | `2785315d2691783f` | 1 |
| 30 | tx-commit | 3 | `2990469b2476bc94` | 7 |
| 31 | tx-rollback | 3 | `2990469b2476bc94` | 6 |
| 32 | partial-update | 3 | `7403e160cdb7c5f9` | 7 |
| 33 | stale-conflict | 2 | `9da1fc7a0bdd78e6` | 6 |
| 34 | early-stop | 3 | `9734757769760219` | 1 |

The execution count is the manifest business contract, not a claim about provider-internal protocol messages or uninstrumented driver SQL.

## Implemented Go boundary (local candidate, pending execution verification)

Implementation files are `harness/manifest.go`, `digest.go`, and `worker.go`, package main. `LoadManifest` requires the frozen SHA-256 and rejects different manifests. `NewWorker(ctx, provider, connection, manifest, workerID)` pins one database/sql connection; `Warmup(64)` verifies all35 then runs64; `Execute(globalArrivalIndex)` validates results and business SQL/control counts each time; `Close` closes cached SQLite statements, pinned connection and pool. `VerifyDatabase` shares DSN construction and records actual database metadata/settings. Assertions use `OracleError`; driver/cleanup errors remain ordinary errors.

Pinned choices supplied by the environment audit are pgx/v5 v5.11.0 and mattn/go-sqlite3 v1.14.53. PG is configured `default_query_exec_mode=exec`, `statement_cache_capacity=0`, `description_cache_capacity=0`, sslmode=disable and never invokes PrepareContext. This uses an unnamed parameterized exec path and text parameter encoding; the report must retain this driver distinction. SQLite uses exact external libsqlite3 with the libsqlite3 build tag and cached public prepared statements for31 read cases; four transaction cases construct command argument slices inside each operation and use driver BEGIN IMMEDIATE.

One completely successful35-case cycle produces854 business result rows and57 manifest business SQL/control executions. A load with rejections must derive these totals from the actual succeeded case counts, not multiply total successes by the cycle average. No Go workload or build was run by the contract/worker implementer; the coordinating agent performs one unified build and correctness check before timing.
