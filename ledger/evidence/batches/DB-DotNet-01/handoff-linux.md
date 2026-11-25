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
