# DB-Runtime-Compare-01 — temporary local comparison record

## Current owner scope

The owner stopped Korda optimization and requested a new comparison record on
2026-11-27 (America/Los_Angeles). This task does not resume the three optimization
directions from DB-Exec-Parity-01. The owner explicitly authorized closing all
non-Dependabot open pull requests and creating one temporary recording PR.
Keep this new PR as a draft record; no product merge or package release is selected.

The owner clarified that the 128 MB budget belongs to the **C# client**, not the
database. PostgreSQL is outside that client budget. Preserve the existing
database configuration; do not describe its `shared_buffers` as a client limit.
An actual enforced memory limit must be distinguished from GC heap configuration,
sampled RSS and total process memory. Do not credit an unverified configuration.

## Repository checkpoint and completed PR cleanup

Latest main source snapshots are recorded in [preparation.json](preparation.json).
Korda #40 and Korda-Design #21 are already merged. Plan #36 was still open.
The following user-authored PRs were observed closed and unmerged by this task:

| Repository | PR | Preserved head |
| --- | --- | --- |
| IzuSharp/Plan | 36 | `4c887258d585c0c127e16850bdc5d155bfcf0de3` |
| IzuSharp/Plan | 35 | `89804888b2e4967da69c18f09851ab6139717602` |
| IzuSharp/Korda | 39 | `d5f4f9d6616bad54a08aebb7d1aca7937b18eb93` |

The connected inventory contained 24 repositories under ArcForges, IzuSharp and
IzuLoom. Scoped open-PR searches found no other non-Dependabot open PRs.
Dependabot PRs and all source branches were preserved. The current owner request
supersedes the previous instruction to keep the two Go PRs open; their evidence
and source heads remain available and were not merged.

## Requested matrix and execution order

Each row has two separate serial 1,800-second offered-load intervals, SQLite
first and PostgreSQL second. Warmup, drain and released-idle observation are
additional. The matrix is four implementations and **eight long cells**.

The owner's subsequent instruction enables
`<Features>$(Features);runtime-async=on</Features>` in both EF Core JIT variants.
Both use async/await, Task and ValueTask. Rebuild both providers and both runtime
variants, verify the actual compiler feature, and keep earlier build receipts
under their earlier identities. This does not select a change to the restored
Dapper.AOT consumer.

| Order | Implementation | Runtime | Query path |
| --- | --- | --- | --- |
| 1–2 | Dapper.AOT | .NET 11 Release Native AOT | Existing generated readers and workload |
| 3–4 | EF Core | .NET 11 JIT, Workstation GC | Fluent LINQ and explicit documented exceptions |
| 5–6 | EF Core | .NET 11 JIT, Satori runtime | Identical application source to Workstation |
| 7–8 | jOOQ | Java 25, GraalVM Native Image | Fluent DSL, explicit typed DTO mapping |

No Korda optimization, additional Korda comparator or Go rerun is selected.
The latest completed 30-minute baseline is Korda #37 / Plan #34, not #40, whose
long measurements were cancelled. Historical results are not new test results.

## Restored workload

Use `Korda/benchmarks/db-perf`, not the historical `benchmarks/Database/campaign`.
The original plans at Plan main are
`execution-refactor/continuation-7/current-measurements/campaign-17da/plans/sqlite-final-01.json`
and `postgresql-final-01.json` in the parent DB-Perf-01 evidence batch.
The full result is `execution-refactor/continuation-8/final-report.md`.

| Setting | SQLite | PostgreSQL |
| --- | --- | --- |
| Offered interval | 1,800 s | 1,800 s |
| Concurrency | 4 | 8 |
| Offered rate | 3,000/s | 3,600/s |
| Planned arrivals | 5,400,000 | 6,480,000 |
| Bounded FIFO capacity | 64 | 64 |
| Query/session mode | prepared/persistent | prepared/persistent |
| Rows/batch rows | 32/32 | 32/32 |
| Fixture | 8 tenants × 1,024 orders | Same |
| Warmup | All cases verified, then 64 operations per worker | Same |
| Released idle | 15 s, no forced collection | Same |
| Client/server/observer CPUs | 0–3 / n/a / 8 | 0–3 / 4–7 / 8 |

The exact 35-case manifest has SHA256
`76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2`.
Retain absolute scheduled arrivals, non-waiting admission, explicit refusals,
no retries, global case ordering and complete drain. Keep service and scheduled
latency separate. Client CPU includes the in-process load scheduler.

Retain exact DTO/hash/null/decimal/JSON contracts. In particular, early-stop
queries 1,024 complete rows and consumes three before disposal; it is not a
LIMIT 3 query. Empty SUM remains NULL. `nullable-order` uses CustomerId NULLS
FIRST; other ordering follows its exact manifest, not a blanket null rule.
The related result retains empty parents and child order. All four write cases
perform their real transaction, conflict, persisted-state and restoration work.
Equivalent Fluent SQL improvements are permitted by the owner, but SQL changes
and any unavoidable raw-SQL exceptions must be explicit.

## Version preparation

Use .NET SDK 11.0.100 and EF Core/provider 11.0.0. Preserve Dapper 2.1.100,
Dapper.AOT 1.1.0, Npgsql/Microsoft.Data.Sqlite.Core 11.0.0 and
SQLitePCLRaw.provider.sqlite3 3.0.5 for the restored reference.
The original engines are SQLite 3.51.3 and PostgreSQL 18.0.

Satori's actual NuGet feed supplies
`PublishWithSatoriGC/11.0.2-satori.45942668844.1`, release
`20261127.1-net11.0`. The XML SDK replaces CoreCLR runtime assets, including JIT
assets, so the comparison is stock Workstation runtime versus the selected
Satori runtime build; not every observed difference can be attributed only to GC.
Verify `GC.GetConfigurationVariables()["SatoriGC"]` and actual loaded binaries.

The latest checked Java-25 feature distribution is GraalVM 25.6.5.1,
based on Java 25.0.5.1. The Oracle download returned HTTP 403; the official
Community distribution was downloaded and its published SHA256 matched.
The Fluent consumer uses jOOQ 3.21.10, pgJDBC 42.7.15 and sqlite-jdbc 3.51.3.0.
Its JNI wrapper must use the same SQLite 3.51.3 library as the C# consumers.
Version lookup is not a successful build or a successful workload execution.

## Current preparation state and recovery

Long measurements completed: **0/8**. No formal measurement is running at this
checkpoint. Source worktrees were created from the three current main snapshots.
The .NET SDK, both actual Dapper.AOT consumers, SQLite 3.51.3 and PostgreSQL 18.0
were built. Both database fixtures passed row/schema/index validation, and their
normalized order digests match. Dapper passed all 35 cases on each provider with
zero business/oracle errors and zero remaining application connections. These
were finite correctness checks, not 30-minute runs. The earlier SQLite attempt
used an invalid warmup of zero and is preserved beside the corrected attempt.
The new Fluent consumers and runtime-async build verification remain in progress.

The current Linux x64 execution environment exposes CPUs 0–8 but no cgroup mount
or `memory.max`. [Actual bounded probes](memory-verification/README.md) establish
that stock Workstation enforces the 128 MiB GC heap setting, while the selected
Satori runtime reports that setting but successfully retains 192 MiB of managed
arrays. A common enforceable C# client memory budget has not been established.
Stock GC heap enforcement also does not imply a 128 MiB total-process bound.
Database memory is outside the owner-requested client restriction.

Before any long cell: finish all builds, verify the exact runtime/GC identities,
execute all 35 correctness cases, bind source/dependency/generated/native hashes,
prepare one common database fixture and check actual memory enforcement. Keep
all builds and diagnostics outside the timed intervals. Save partial failures;
do not shorten a required interval or turn missing counters into zero.

All performance work is local. Existing CI is unchanged and may only perform
its existing document/integrity/correctness/security work. No benchmark,
calibration, profiling or load invocation is added to or triggered through CI.
