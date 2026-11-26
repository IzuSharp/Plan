# DB-Exec-Parity-01 — read-only Plan recovery and baseline audit

Audit role: `plan_recovery`. This audit read repository records through the GitHub connector; it did not run a product build, benchmark, profiler, CI job, or mutation. All measurements below are historical observations, not new DB-Exec-Parity-01 evidence. Temporary copies of the main source reports are under `analysis/recovered/` for integration into the task's Plan worktree.

## 1. Recovery decision and authoritative sources

The observed latest Plan main is `03efe57ffbe3046bd89919ddb2c16c90a377954d`, tree `56dbe91bfbf0732863d0f65630bbee872ef22045`. Plan #34 is normally merged. Its accepted head is `bd0fbfb589e4380dbd15e5346fde81a9111bea03`, with the same tree. Its final existing PR check was run `45816173710`; main integrity run `45817545243` passed according to the observed final PR body. These are historical delivery receipts; this audit has not independently downloaded those logs.

- [Plan #34 full PR body](https://github.com/IzuSharp/Plan/pull/34)
- [Plan main identity](https://github.com/IzuSharp/Plan/commit/03efe57ffbe3046bd89919ddb2c16c90a377954d)
- [Current final report](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/final-report.md)
- [Full phase and short-before extraction](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/preexisting-measurement-summary-01.md)

A search for `DB-Exec-Parity-01` across the three repositories returned no PRs. Plan branch search for `DB-Exec-Parity` returned no branches. This does not replace root's filesystem/process and full three-repository branch inspection.

Plan main AGENTS.md still starts with DB-Exec-02 authority and retains older stop instructions as history. The current user's explicit DB-Exec-Parity-01 request supersedes the old task name and authorizes the newly specified local observations, implementation, normal reviewed merges, existing-rule release verification, and final public-package consumption. It does not permit relabeling old results or resuming the unselected Go task.

## 2. Local inputs were deliberately removed

The latest observed [Plan #35](https://github.com/IzuSharp/Plan/pull/35) is open Draft at `89804888b2e4967da69c18f09851ab6139717602`, branch `db-go-01-evidence`. Its full PR body records completed cleanup: 65 worktrees unregistered/removed; source and recovery trees, mirrors, upstream clones, builds, databases, task toolchains, NuGet and Go caches removed; 46 final staging entries removed. A follow-up retained receipt reports zero project-source files, Git markers, known task caches, or observed database/build/benchmark processes in the inspected accessible locations.

Therefore the paths in continuation-7/8 handoffs are historical paths, not a current ready-to-run environment. Historical archives retain source/receipts/raw numeric evidence, but explicitly exclude database, package, and compiled binary bytes with identity records. Rebuilt consumers must receive new binary/build identities even if source trees match. A hash receipt is not an executable recovery.

The Go draft's follow-up CI was last described as in progress in its PR body; this audit does not claim that run's eventual state. Keep Plan #35 and Korda #39 Draft, unmerged, with auto-merge disabled; do not edit them during DB-Exec-Parity-01.

- [Go closeout](https://github.com/IzuSharp/Plan/blob/89804888b2e4967da69c18f09851ab6139717602/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-9-go/closeout.md)
- [Final residual cleanup receipt](https://github.com/IzuSharp/Plan/blob/89804888b2e4967da69c18f09851ab6139717602/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-9-go/cleanup/final-residual-cleanup-receipt.json)

## 3. CI obligations read before recovery

Read Korda main [AGENTS.md](https://github.com/IzuSharp/Korda/blob/main/AGENTS.md), [module registration](https://github.com/IzuSharp/Korda/blob/main/eng/ci/modules/README.md), and [existing CI](https://github.com/IzuSharp/Korda/blob/main/.github/workflows/ci.yml). Their observed Git blob identities were respectively `4ce83c4eee019e702cebfcc0496f439de71ff97c`, `1e079f5ba9a9c5df2c3c5ac808174d381387b5c6`, and `c1d42c06d7151de6d2b6e84fd086ee1aab265049`.

Required properties:

- Direct Release Native AOT consumers; skip JIT consumer builds/tests. No clean-image or CPU emulation unless separately requested.
- Independently installable top-level PostgreSQL and SQLite packages, each with its own runner; internal modules remain buildable/testable.
- Committed-diff/module dependency selection. Before product push run `python3 eng/ci/impact.py origin/main --output artifacts/plan.json`, inspect actual selected paths, scopes, actions and independent package closures.
- No benchmark, profile, calibration or pressure action in ordinary CI, in a new workflow, manual button, schedule, hidden correctness check, release script, or indirect trigger.
- Main compares each registered package against last-published inputs, builds/consumes the exact next preview, then existing trusted release jobs publish verified artifacts. Do not replace existing routing to force release.

The historical product impact selected `interop`, `linux`, `postgresql`, and `sqlite`; that was correct for its historical product diff. It is not the required answer for today's unchanged main or any future narrower diff.

## 4. Exact prior source and dependency identities

| Input | Historical identity |
| --- | --- |
| Measured final product | `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`, tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc` |
| Product normal merge | `7ff7b57b907b689defb880b8af62d83679608603`, same tree |
| Design accepted head / merge | `7b78cf98e29b5e4c67362a5c33d1fadbaf77ca55` / `ca9348ad0b5cc93bc75c502460d8e1b75843d109` |
| Design merge tree | `ffe6f94306985bacde708e75d1e93a29e096c724` |
| Earlier before product | `f0078da720e07031bc56464995af6791c41aaae8` |
| Dapper mixed-consumer harness | `05fdd6b507bbfa9e971caa739784cf42dfb7199c` |
| .NET SDK / runtime | `11.0.100` / `11.0.0` |
| Dapper / Dapper.AOT | `2.1.100` / `1.1.0` |
| Npgsql | `11.0.0` |
| Microsoft.Data.Sqlite.Core | `11.0.0` |
| SQLitePCLRaw.core / provider.sqlite3 | `3.0.5` / `3.0.5` |
| PostgreSQL server / libpq | `18.0` |
| SQLite | `3.51.3` |
| Final ordinary SQLite package SHA-256 | `059a0df6b2ed428788b2bf5a7212dd4d73d43cd642eee0de152b975efaf03d6a` |
| Final ordinary PostgreSQL package SHA-256 | `46d5757c6dc48c721167476e2975f025b6884dc0c54b6956b9677a8eb4b29dec` |
| Original final input freeze SHA-256 | `fc1dae9be0a76b0de38c4f94c3836e47b398e10b5ff23f3c8f82313a3cb4bc1a` |
| Historical host | `89394ab90f06`, Linux `6.18.57`, x86_64, AMD EPYC 9V74 |
| Historical CPU placement | Client CPUs 0–3; PostgreSQL 4–7; observer 8 |

The recorded host cannot establish exclusive physical hardware or invisible cgroup quotas; cgroup-v2 mount was unavailable. New observations must qualify the current environment independently.

The [SDK pin](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/dotnet-sdk-pin.json) is the Linux x64 SDK archive at `https://builds.dotnet.microsoft.com/dotnet/Sdk/11.0.100/dotnet-sdk-11.0.100-linux-x64.tar.gz`, SHA-512 `1bec9cca2ec689b1e80245b84f2b53c9441d1aa6daccf2ceb27490768bffa95954fa585bd275def31069d874d543d9ba9e6591fe9ade2dbd9f34ec5c0fd0050c`.

[Build recovery](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/build-recovery.json) retains each restored archive SHA-256, signed-content hash comparison, generated consumer SHA, native library SHA, and AOT ELF SHA. Package archive hashes and NuGet signed-content hashes have different semantics; preserve that distinction.

Historical direct SQLite compile definitions were: `SQLITE_CORE`, `SQLITE_DEFAULT_FOREIGN_KEYS=1`, `SQLITE_ENABLE_API_ARMOR`, `SQLITE_ENABLE_COLUMN_METADATA`, `SQLITE_ENABLE_DBSTAT_VTAB`, `SQLITE_ENABLE_FTS3`, `SQLITE_ENABLE_FTS3_PARENTHESIS`, `SQLITE_ENABLE_FTS5`, `SQLITE_ENABLE_JSON1`, `SQLITE_ENABLE_LOAD_EXTENSION=1`, `SQLITE_ENABLE_MEMORY_MANAGEMENT`, `SQLITE_ENABLE_RTREE`, `SQLITE_ENABLE_STAT4`, `SQLITE_SOUNDEX`, `SQLITE_THREADSAFE=1`, `SQLITE_USE_URI=1`, `SQLITE_ENABLE_UNLOCK_NOTIFY`, `HAVE_USLEEP=1`, `HAVE_ISNAN`, `_POSIX_THREAD_SAFE_FUNCTIONS`, `HAVE_LOCALTIME_R`. This list is historical; recheck the actual loaded library and its compile options for the new consumers.

## 5. Original 35-case business workload

Read current [queries-v3.json](https://github.com/IzuSharp/Korda/blob/main/benchmarks/db-perf/workload/queries-v3.json), blob `86276c62f5935b41667235e399fd75536884ea46`. It has schemaVersion 3, 8 tenants × 1024 orders, 256 customers, requestedRows 32 and batchRows 32. Preserve SQL, typed parameters, materialization, deterministic digests, and transaction persistence oracles, not merely case names.

| Business family | Original cases |
| --- | --- |
| Narrow / scalar / text / JSON / wide | `numeric`, `text`, `money`, `json`, `wide` |
| Dynamic filters / range / NULL / literal | `optional-filter`, `range`, `null-notes`, `literal-note` |
| Join / association | `left-join`, `inner-join`, `three-join`, `anti-association`, `related` |
| Aggregation | `customer-totals`, `product-totals`, `empty-sum` |
| Paging / ordering | `cursor`, `offset`, `nullable-order` |
| Relational subqueries and sets | `exists`, `in-subquery`, `cte`, `window`, `union-all`, `union`, `intersect`, `except`, `running-total` |
| Full SQL | `raw-sql` |
| Writes / transaction controls | `tx-commit`, `tx-rollback`, `partial-update`, `stale-conflict` |
| Premature termination | `early-stop` |

Most reads return 32 rows; `customer-totals` returns 9, `empty-sum` and `exists` 1, `union` 24, `intersect`/`except` 8, `related` 53, three write/transaction cases 3, stale conflict 2, early-stop 3 DTOs. Do not compare raw Go/native boundary totals across different workloads or populations.

The original mixed runs used prepared mode, persistent sessions, queue capacity 64, warmup 64 per worker, SQLite C4/R3000 and PostgreSQL C8/R3600. Each final cohort ran 1800 seconds and requested a separate 15-second post-disposal idle with no forced GC. Those are the historical-reference settings required by the new request, not the zero-rejection settings or newly measured capacity point.

## 6. Historical final 1800-second measurements

All four historical runs had zero business/oracle errors and retries, admitted requests drained, every required second had progress, and all 35 cases ran. Korda's eight owner categories returned to zero; Dapper tracked only its application logical connections, not symmetric internal owners.

| Provider / framework | Successes | Rejected | Success/s through drain | Client CPU µs/success | Total managed B/success | Peak / idle RSS MiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SQLite / Korda | 4,872,560 | 527,440 | 2,706.936 | 997.290 | 24,790.092 | 43.652 / 37.184 |
| SQLite / Dapper.AOT | 5,389,886 | 10,114 | 2,994.376 | 582.990 | 7,431.767 | 33.836 / 29.844 |
| PostgreSQL / Korda | 6,120,073 | 359,927 | 3,400.012 | 840.060 | 25,490.045 | 50.234 / 41.258 |
| PostgreSQL / Dapper.AOT | 6,465,624 | 14,376 | 3,591.997 | 463.269 | 7,316.433 | 41.031 / 32.641 |

| Provider / framework | Scheduled p50 / p95 / p99 ms | Service p50 / p95 / p99 ms |
| --- | ---: | ---: |
| SQLite / Korda | 20.185 / 33.423 / 49.545 | 0.545 / 4.882 / 12.976 |
| SQLite / Dapper.AOT | 0.208 / 3.031 / 8.585 | 0.111 / 1.597 / 4.325 |
| PostgreSQL / Korda | 14.877 / 27.132 / 38.273 | 0.889 / 10.551 / 16.581 |
| PostgreSQL / Dapper.AOT | 0.371 / 3.326 / 8.520 | 0.342 / 2.753 / 4.588 |

These are histogram upper bounds and accepted/successful populations. Scheduled includes arrival scheduling and queue delay; rejected arrivals receive no invented completion latency. Fixed-offer throughput is not sustainable maximum capacity. Peak is whole-command wait4 maximum, including setup/cleanup, not an interchangeable consumer endpoint VmHWM. CPU is client-only operation interval through completion of admitted work. All-process managed bytes include DTO/string/JSON/list/harness/framework/driver; exclusive framework bytes remain null. A complete steady per-cell PostgreSQL server CPU denominator was not obtained.

## 7. Same-query phase evidence selects what must be observed next

The phase harness compared ordinary Fluent, hot Prepare, Host complete SQL, and Dapper.AOT for 1/100/1000 rows. Each route pooled all three 256-operation windows, with no best-window selection. First-row includes first DTO mapping; four-phase total is computed per operation before quantiling, not by summing phase quantiles. Dapper cleanup may occur within ReadComplete.

| Provider / rows | Hot Prepare total p50 µs | Dapper total p50 µs | Hot Prepare client CPU µs/op | Dapper client CPU µs/op | Hot Prepare / Dapper total managed B/op |
| --- | ---: | ---: | ---: | ---: | ---: |
| SQLite / 1 | 127.669 | 6.760 | 259.484 | 9.711 | 2,576.104 / 2,131.365 |
| SQLite / 100 | 350.357 | 47.150 | 767.975 | 56.689 | 9,779.042 / 9,251.365 |
| SQLite / 1000 | 1,887.428 | 367.447 | 4,047.661 | 396.393 | 80,603.677 / 79,810.188 |
| PostgreSQL / 1 | 215.590 | 96.273 | 270.792 | 91.613 | 2,575.490 / 2,112.781 |
| PostgreSQL / 100 | 546.614 | 160.440 | 662.664 | 123.237 | 9,738.125 / 9,240.875 |
| PostgreSQL / 1000 | 2,704.440 | 462.550 | 4,307.207 | 542.667 | 80,541.625 / 79,986.031 |

PG 1000-row hot Prepare adds only 555.594 managed B/op while client CPU is about 7.94× Dapper; Host complete SQL CPU is 4308.611 µs/op and total p50 2634.807 µs, close to hot Prepare's 4307.207/2704.440. This supports prioritizing observation below construction. It does not establish whether any specific decode, scheduler, allocation, cancellation, scan or copy dominates. SQLite also has both a large fixed single-row cost and repeated 1000-row cost: the 1000-row CPU ratio is about 10.21×.

The historical four same-condition 120-second before/current mixed observations improved SQLite 542.872→2668.577 successes/s and PostgreSQL 1241.453→3458.224, but are separate short data. They compare f0078da→17da, not a new DB-Exec-Parity candidate. They do not provide new before evidence or justify skipping current source/binary/environment qualification.

## 8. Counter and attribution limits that the new stage must close

- Existing numeric32 instrumented Korda single-case diagnostics measured 13 managed-to-native FFI calls and one SQL dispatch per successful query; PG measured four libpq submissions. A second pull at exact batch capacity was not a second SQL execution.
- Those were 15-second C1 instrumented runs, with no ordinary timing/allocation credit. Their arrays do not cover new 1/100/1000 phases or 30-minute mixed operations.
- `SqlExecutions` counts provider dispatches including internal controls, not successful server statements. `ProtocolSubmissions` counts successful libpq send/Sync API calls, not packets, replies, blocking waits, or RTT.
- Ordinary Dapper counters and internal FFI/reply totals were unavailable, not zero. Existing generated-source/normalized SQL proof retained `runtimeSqlTraceVerified=false`; no runtime byte-for-byte wire SQL equality was established.
- Existing PG proxy evidence separately proved a narrow healthy commit window changed SQL dispatches 2→1, forwarded ReadyForQuery 6→4, and submissions 10→6. This is not a complete long-run protocol census.
- Source/phase data does not isolate individual thread handoffs or per-row codec cost. No matched-ELF hotspot and scheduler evidence is created by this audit. Mark those unknown until new stage observations are recorded.

## 9. Failed or rejected paths to preserve

[Independent stopping review](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/final-stopping-review-01.md) distinguishes contract from implementation:

- Already-released final-close shortcut: ordinary two-round paired rule failed; PG single-row read-complete changed sign and SQLite 1000-row pooled total p50 regressed 6.78%, beyond the 5% guard. This rejects that exact shortcut, not all dispatch redesign.
- Inline completion: rejected before AOT execution/timing due to completion publication preceding potentially throwing continuation dispatch; resetting generation, publishing a second exception or disposing a delivered batch cannot repair that ownership error. No performance credit.
- PG cross-execution physical prepared/description cache: unselected because external DDL can make cached Describe raise 0A000/abort a transaction where fresh Parse differs. No hidden retry/replay may repair the semantic change.
- SQLite cross-execution physical statement caching: unselected absent schema/reset/clear-bindings compatibility proof. sqlite3 automatic reprepare alone does not establish preserved error order and cleanup.
- Earlier AF_UNIX/named-pipe restriction blocked Roslyn formatting and multi-node restore. A task-local build retry used `DOTNET_PROCESSOR_COUNT=1`, `DOTNET_CLI_USE_MSBUILD_SERVER=0`, `UseSharedCompilation=false`; no formatter/CI rule was disabled.
- Original phase LIMIT added an unexpected parameter and raw-SQL harness rejected it; the replacement used two explicit Int64 predicates for 1/100/1000. Preserve failed run rather than calling it a product fault or erasing it.
- Historical unexplained native/managed aborts and initial PG public-NuGet indexing timeout remain in receipts. A later pass does not retroactively pass a failed attempt.

Remaining source candidates have no isolated proof yet: repeated immutable shape hash/lock/LRU and SQL/expectation copies, snapshot value/frame ownership, batch partial compaction, per-cell validation/codec work, and scheduling/control/retirement objects. Necessary snapshot/lifetime/error guarantees do not prove every representation/queue/object is minimal; retained representations are not measured hotspots simply because they exist.

## 10. Go evidence: use for attribution, leave drafts unchanged

Read [Go final report at the unchanged draft](https://github.com/IzuSharp/Plan/blob/89804888b2e4967da69c18f09851ab6139717602/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-9-go/final-report.md). Go compiler 1.27.4; SQLite `github.com/mattn/go-sqlite3 v1.14.53` uses external exact SQLite image; PG `github.com/jackc/pgx/v5 v5.11.0` via database/sql uses Go protocol. Runtime source `94eb3a7675a44e30c6f9ed6c7a7edda987fe36db`, published record `d5f4f9d6616bad54a08aebb7d1aca7937b18eb93` with unchanged runtime source.

| Go historical ordinary cell | SQLite | PostgreSQL |
| --- | ---: | ---: |
| Successes / 1800s | 5,386,460 | 6,468,551 |
| Rejected | 13,540 | 11,449 |
| Success/s | 2,992.478 | 3,593.636 |
| Client CPU µs/success | 556.721 | 388.867 |
| Go heap B/success | 3,139.808 | 4,132.255 |
| Runtime.NumCgoCall delta | 222,218,466 | 0 |
| Successful business SQL/control calls | 8,771,576 | 10,533,858 |
| Consumed business rows | 131,430,355 | 157,833,343 |

Go SQLite retains prepared read statements; WAL, synchronous FULL, foreign keys, 5000ms busy timeout, BEGIN IMMEDIATE. PG exec mode disables statement/description caches and retained named statements, analogous to Npgsql MaxAutoPrepare=0; text parameter encoding remains a driver difference. Go uses handwritten typed DTO readers, not a Go ORM. Its batch32 is reference metadata, not database/sql batching. Go NumGC is non-generational and TotalAlloc cannot be relabeled CLR/native-allocation or exclusive framework data. 222 million crossings do not by themselves explain or refute any particular Korda crossing cost.

The old Go long runs are complete. Add only bounded diagnostics for a specific unresolved causality question, using separate identities; do not rerun them merely to restate the comparison.

## 11. Reusable local build and campaign tools

Existing [candidate build driver](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/candidate-build-tools/build_public_inputs.py) accepts clean source commit/tree/provider/fresh output/PG install. It runs source impact, native build/correctness, independent bundle, exact-package AOT consumption, public validation, and ordinary external phase/workload builds. Its actual build stages use the repository's `eng/task07_native.py`, `eng/ci/bundles.py`, `eng/ci/consume.py`, `eng/ci/validate_public.py`, and `benchmarks/db-perf/managed/build.py`.

Important: the archived driver asserts the historical four-scope impact plan. Starting latest main has no such diff. Inspect today's actual planner, then adapt only the independent local build driver for the new baseline/rebuild purpose. Do not change CI to satisfy the old assertion or call a changed driver an identical historical input. Every new attempt needs a fresh output/worktree and preserved failure receipt.

Existing [local load tool guide](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/local-load-tools/README.md) uses:

```sh
python3 "$DB_PLAN_ROOT/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-4/generate_local_plan.py" \
  --source "$DB_KORDA_SOURCE" --provider postgresql --lane final \
  --before-dir "$DB_BEFORE_BIN" --candidate-dir "$DB_CANDIDATE_BIN" \
  --dapper-dir "$DB_DAPPER_BIN" --postgres-bin "$DB_POSTGRES_BIN" \
  --concurrency "$DB_CONCURRENCY" --rate "$DB_ARRIVAL_RATE" --queue-capacity 64 \
  --plan "$DB_ORIGINAL_PLAN" --output "$DB_UNUSED_ORIGINAL_OUTPUT"

python3 "$DB_PLAN_ROOT/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/local-load-tools/select_load_cohorts.py" \
  --input "$DB_ORIGINAL_PLAN" --input-sha256 "$DB_ORIGINAL_PLAN_SHA256" \
  --generator "$DB_PLAN_ROOT/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-4/generate_local_plan.py" \
  --source-commit "$DB_RUNNER_SOURCE_COMMIT" --kind final \
  --plan "$DB_DERIVED_PLAN" --output "$DB_NEW_EVIDENCE_DIRECTORY"

taskset -c 8 python3 "$DB_KORDA_SOURCE/benchmarks/db-perf/run.py" \
  "$DB_DERIVED_PLAN" --output "$DB_NEW_EVIDENCE_DIRECTORY"
```

For SQLite use `--provider sqlite --sqlite-library "$DB_SQLITE_LIBRARY"` in place of PG bin. Do not run original three-cohort plans if using the derived final pair. Revalidate actual affinity rather than assume CPU8 remains available. Warmup and idle stay outside the measurement interval; no overlapping build/profile/workload/compression. The old >=90% offered-validation criterion is superseded for this task by the user's zero-rejection-first and graduated-pressure requirement. Retain the old settings as a separate historical comparison.

After real completion, existing arithmetic analysis and `audit_final_identity.py` provide useful independent identity/owner checks but do not themselves prove package producer identity, framework 0 B, source-level timing, complete server CPU, or parity. Only fresh actually observed records may close new gates.

## 12. Historical release receipts and new closeout boundary

The [delivery record](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/delivery-01/README.md) reports product main CI `45807237435` success and both independent `0.1.0-preview.4` signed registry readbacks/public AOT consumers passed. First PostgreSQL indexing verification failed; a normal retry reused the same candidate/version, skipped upload, and passed. SQLite remained its original successful execution. These release bytes remain distinct from the ordinary measured ci.1 package bytes.

The old candidate is correctly described as improved, validated and delivered, with substantial remaining Dapper gaps and no proved framework-only 0 B or global optimality. It is not DB-Exec-Parity-01 acceptance. The new task must publish its own dual-database observation table before product path edits, preserve old evidence, implement only supported hypotheses, freeze/measure all four new ordinary 1800-second cells, then review/merge and observe actual existing-rule CI/release/public AOT results.

No permission request is needed to continue this authorized work. If environment recovery blocks execution, preserve an exact blocker and keep acceptance unfulfilled; do not compensate with CI benchmarks or unmeasured product changes.

## 13. Actual tracked-file and archive binary-availability check

After root cloned the latest three mains into the task worktrees, this audit inspected 14,978 tracked files (Korda 1,403; Design 2,957; Plan 10,618), all recognised tracked ZIP/nupkg/tar archives, and the archive nested inside the final evidence archive. It checked the first bytes for ELF/PE magic and binary/tool names, and read archive members without extracting or executing them. The actual detailed result is `analysis/tracked-binary-availability.json`; the scan recorded zero errors.

No current Korda/Dapper database-consumer ELF, .NET SDK, PostgreSQL installation, libpq/sqlite3 build dependency image, or required native toolchain was found in these tracked inputs or inspected archive members. The DB-Perf Plan archives contain evidence/source/receipts, with no ELF/PE members. This supports a rebuild dependency blocker, not a claim about every untracked or remote file anywhere.

The only executable-format members were unrelated historical Design artifacts: two copies of `NativeWeave.Research.Codec.0.0.1.nupkg` containing `Codec.dll` and `libnw_codec_research.so`; a public-API CI ZIP containing `NativeWeave.Api.Consumers` plus a same-named `.dbg`; and its Windows executable/PDB counterpart. The Linux old API ELF is 3,460,608 bytes and `.dbg` is 5,689,688 bytes. Their shared archive/name does not itself verify matching Build-IDs; no execution or source/machine-code attribution was performed. They cannot substitute for either database benchmark or locked toolchain.
