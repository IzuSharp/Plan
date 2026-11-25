# DB-DotNet-01 Linux x64 handoff

## Recovery entry

Read this file, [plan.md](plan.md), [baseline.json](baseline.json), [acceptance.json](acceptance.json), [workloads.md](workloads.md) and the current three remote branch heads before continuing. Work branch and worktree marker: `DB-DotNet-01`. The fixed starting main SHAs are in baseline.json; subsequent validated commits and receipts append here without erasing failures.

## Initial checkpoint

The owner authorized the complete PostgreSQL/SQLite .NET migration, compatibility checks, Dapper.AOT-only external performance comparison, independent review, normal merges, automatic preview and public NuGet AOT verification. No permission re-request is needed for those authorized actions. Plan and Design preparation are underway. Compilation, package migration, real-database compatibility, internal .NET baseline, optimization, four long segments and public consumption are **not yet accepted**.

The prior DB-Perf-01 is cancelled and stays source-bound history. Its C++ candidates, short measurements and 0/8 long state are not this batch's optimization baseline or long-test credit. Source inspection found no DB-DotNet-01 entry in the initial three main trees.

## Resume sequence

1. Freeze last published package bytes and the unchanged external business consumer; produce old-schema/file/migration fixtures before changing execution.
2. Record this Plan commit and the new Design commit, then implement the provider migration and behavior-test replacements.
3. Validate each top-level package in its own Native AOT runner; record real cancellation after execution begins, early-stream cleanup, rollback, lost-COMMIT-ack and old-data continuation.
4. Fix the first compatible .NET package versions/hashes as the internal pre-optimization baseline. Preserve that immutable snapshot.
5. Recover useful old harness sources only by their source-reference hashes, port them to the new managed execution boundary and audit all generated Dapper call sites. Revalidate; old results do not transfer.
6. Execute repeated short equivalent comparisons, keep measured changes, freeze the final candidate and admit dedicated long-test resources.
7. Run 4 × continuous 30-minute effective mixed load sequentially; review, normal merge, observe main/publication and consume actual public NuGet packages.

## Execution environment preparation

The root agent reported successful official SDK installation and an actual `dotnet --info` for .NET SDK 11.0.100 / runtime 11.0.0. All three full-history checkouts and task worktrees exist. Published preview.3 archives are being recovered; Clang/PostgreSQL preparation is in progress. These preparation facts do not accept a compiler, database or benchmark lane. No dedicated long-test environment has been admitted.

## Known source-level risk

Microsoft.Data.Sqlite 11.0.0's published `SqliteCommand.Cancel()` is a no-op and `ExecuteReaderAsync` only checks before a synchronous call. Upstream main has different cancellation code, which is not evidence about the released package. See [driver-source-review.md](driver-source-review.md). A managed compatibility adapter and actual execute/read/busy-lock cancellation tests are required; unsupported behavior stays explicitly unresolved.

## Evidence discipline

Record exact commands, exit codes, source/package/executable hashes, dependency graph, database seed, raw counters and environment identity. Update acceptance statuses only after observed evidence exists. Store secrets outside committed evidence. No source review, successful document gate or historical measurement establishes current product execution. The containing evidence commit's CI result is tracked after it actually completes.

## Record checks

The initial current-record validation and four negative controls passed. `--require-complete` correctly failed with incomplete product phases. An initial attempt to replay `verify_db_perf.py` at current main `c73943c` failed its immutable change allowlist because the later repository-rename maintenance is outside that old batch. The new wrapper now uses the already established historical workflow pin `38f8ce8a01f88e6e4c4459926f197c5438c2f6fc` for that unchanged gate; source baseline remains current main. No historical verifier was modified.

The corrected `python3 tools/verify_db_dotnet.py --verify-frozen-history` completed successfully: current record/4 negative controls and unchanged DB-Perf-01 record/13 negative controls/4 source-reference negative controls passed. Both records still report zero accepted long segments; no product execution is inferred.

## Local implementation checkpoint — 2026-11-25

The Plan-first commit is `0ad57adddd2ace06621ef8d263a7e444a8f25bcd`; the corresponding current Design commit is `4a428b876f52a554e2ca3b3732aeed575979bf0c`. Their record gates passed; they do not accept product behavior. The implementation owner is integrating the following local product commits, originally made in the `DB-DotNet-01-migrations` worktree:

| Commit | Scope | Validation at this checkpoint |
| --- | --- | --- |
| `8ca8200` | Managed migration/catalog execution, retained SQLx SHA-384 and phase history, persistent bundle/draft identity, managed schema diff, real-database behavioral test replacements | Source review, `git diff --check`, Python syntax; .NET compilation and database execution still pending |
| `4725852` | Remove Data.Abstractions execution protocol; retain scalar validation, codec registry, exact finite limits and persisted metadata hashes; typed SQL template segments | Source review and diff check; companion RawCommand adaptation required |
| `4f88ddc` | Preserve materialization behavior over actual .NET readers, independent CLR row fixtures, generated/manual mapping, failure cleanup and source diagnostics | Diff check and Python syntax; .NET execution pending |

The root implementation supplies a separately admitted administrative connection, independent of ordinary `MaxConnections`, with source-owned shutdown. This preserves the existing test where a request transaction owns the only ordinary connection while migration still succeeds. PostgreSQL administrative connections must be unpooled so disposal releases the session advisory lock. Existing `_sqlx_migrations` and `_nativeweave_migration_phases` names and retained hashes are database-compatibility state, not execution infrastructure to remove.

The new migration cancellation test waits for actual uncommitted SQLite WAL spill over 128 KiB before cancelling. The PostgreSQL test waits for the actual sleeping backend in `pg_stat_activity` before cancelling. Both tests remain unexecuted in this checkpoint; their presence is not proof of cancellation. Actual source/reader/operation disposal and a subsequent successful database call replace native callback/ABI ownership assertions.

## Execution safety and environment continuity

An initial ordinary local `dotnet publish` was rejected by automatic approval review because the build unexpectedly attempted a cloud metadata/possible credential endpoint. The initiating code was not identified from that log. The same request was not retried. After package target/task inspection, the implementation owner used a materially safer offline build: `unshare --user --map-root-user --net`, `--no-restore`, `--disable-build-servers`, and telemetry disabled. The original SQLite preview.3 external Native AOT consumer then published with observed exit code 0. This establishes feasibility of the safer build path; it does not establish migrated-package compatibility.

PostgreSQL must be started and consumed in the same execution-controller lifetime in this environment, using TCP and no Unix socket directory. A server started in an earlier tool process disappeared when that process ended. This was an environment ownership issue, not a final database blocker. The old dedicated campaign also failed its pinned runner `ImageVersion` admission; no long-test credit is recorded. A new dedicated environment still needs explicit admission/noise evidence before any of the four effective segments.

## Reusable benchmark source

[Harness recovery and adaptation](harness-readiness.md) identifies a published product commit containing the old managed business harness and the historical reproduction archive. All 56 managed-final source-reference records (27 unique contents) matched their exact SHA-256 and size at that product commit during local read-only recovery. Only source recovery is verified: no old correctness, performance or long duration is credited to DB-DotNet-01.

## Root integration and observed failures — 2026-11-25

Remote task branches now exist: Plan initial record commit `2ac40da8dbd833072cca0b0832193f533612a443`, Design `f6eb1c1959b2ca949ee3e083e95c912a1de8c2c1`. The remote Git trees matched the corresponding verified local trees exactly; the author/commit identities differ because the authenticated GitHub Git-data API was used. Plain local git push had no credentials. Plan's follow-up implementation notes were replayed on that remote record parent.

Product integration checkpoint `403fcc1` replaces the owned execution path with standard .NET drivers. `a177b0f` adds bounded shared metadata admission, finite PostgreSQL temporal values without process-global Npgsql switches, strict TLS trust/hostname policy, pending-stream-start cancellation, full row-shape preflight and remaining-field byte budgets. These commits are implementation checkpoints, **not** the first accepted .NET baseline. The baseline remains unset.

The two actual public `0.1.0-preview.3` packages were downloaded before migration. Their ordinary PackageReference order consumers published as Linux x64 Native AOT using the offline network namespace and each executed all 18 original business checks successfully. Original consumer file hashes and package SHA-256 values are frozen in the local `baseline/source-original.json`; the full same-source before/after and existing-file/schema/history continuation acceptance is still pending. PostgreSQL local correctness used standard 17.12; no performance equality or final engine selection is inferred.

New provider/source AOT execution has begun and exposed real failures, which must not be erased from the record:

- SQLite provider profile initially failed because bare read-only PRAGMA statements were overclassified as mutations. Query fix `a31b17e` (integrated `0c5f3ca`) restores the known read-only forms and rejects session-changing forms. Its Query.Binding Native AOT suite passed 28 cases / 209 assertions; provider rerun is pending.
- The real two-provider session suite first failed accepted-cancellation token identity. The managed admission layer now preserves the original caller token; this fix is in `a177b0f`.
- The next session run and the independently executed codec suite both found SQL NULL turning into an empty ReadOnlyMemory<byte> through a conditional-expression implicit conversion. `828a850` makes the nullable return explicit. Codec scalar cases before the nullable vectors had run; the entire codec suite was not accepted from that partial run.
- Transaction tests are being moved from controlled C++ fixtures to actual drivers and transparent PostgreSQL scheduling faults. The new controller records COMMIT/idle acknowledgment loss and independently reads persisted effects through psql. It also tests admission-token cancellation after actual dispatch and a deadline that retains the physical cleanup owner. These new transaction cases are not yet accepted.

No optimization has been accepted. No 30-minute segment has started: **0/4**. Recovered Dapper harness short runs are development correctness checks only. Allocation attribution remains unknown unless supported by raw counts/control experiments; neither source inspection nor a component-only zero-allocation count establishes a database path at 0 B.
