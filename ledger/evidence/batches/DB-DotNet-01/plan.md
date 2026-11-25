# DB-DotNet-01 — compatible .NET execution, then Dapper.AOT comparison

## Authority and order

The owner's current instruction authorizes implementation, tests, independent technical review, PRs, normal merges, repository-triggered preview publication and public-package consumption. Only PostgreSQL and SQLite database products on Linux x64 are in scope. Work uses branch `DB-DotNet-01` and task-named worktrees. This is a new batch; the cancelled DB-Perf-01 campaign and its source-bound observations stay unchanged. Earlier Rust/C++ mandates and task-specific merge stops do not govern this new instruction.

Start with the exact current-main sources in [baseline.json](baseline.json). Read product `AGENTS.md`, `docs/guides/orm-experience.md` and `samples/api/orm-experience` before implementation. Publish this Plan checkpoint, then the .NET Design decision, then implement. Preserve all historical graphs, contracts, evidence and verifier bytes; the previous `current_execution` object is retained in `delivery-graph.json.prior_execution_snapshots`.

The acceptance record is initially **pending, 0/4 long segments, 0 effective seconds**. Source inspection and this record gate do not establish compilation, database execution, compatibility, measurements, merge or publication.

## Phase 1 — freeze the compatibility oracle

1. Download the last actual published archive for each of `Korda.Database.PostgreSql` and `Korda.Database.Sqlite`; record exact versions, archive SHA-256, assemblies, XML API, analyzers, targets, README, dependencies and assets. Do not substitute a locally rebuilt package for the published baseline.
2. Copy the current business consumer outside the source tree and freeze all C# source files by SHA-256. Exercise it against both original packages as Linux x64 Native AOT, including Fluent, all `Db*` attributes, entities, DTOs, joins and batch relations, streaming, parameterized SQL, JSON/decimal/NULL, CRUD, transactions and migrations. Preserve generator diagnostic negative cases separately.
3. Seed PostgreSQL schema and SQLite database files with the original implementation. Retain database versions, schema, indexes, rows, migration-history table contents and migration checksums. The new implementation must open these same persisted stores, read existing rows, write new rows and continue migration history. A fresh-only database smoke test is insufficient.
4. Inventory every native test before deletion. Map each business-significant assertion to a managed behavior test or a justified obsolete implementation-only assertion. Trace ownership and shared references before removing modules.

The same frozen business C# source accepts both old and new packages. Changes to native-image diagnostic tooling may be isolated outside that source; do not silently modify business behavior or relax assertions to make the migration pass.

## Phase 2 — migrate execution and prove compatibility

Use Npgsql for PostgreSQL and Microsoft.Data.Sqlite for SQLite. C# owns typed Fluent composition, provider SQL generation, parameter binding, connection/transaction orchestration and generated result mapping; drivers own their supported I/O and database integration. Dapper is benchmark-only. SQLite's normal driver dependency supplies its native SQLite engine through NuGet.

Remove Korda-owned database C++ sources, C ABI/P/Invoke, native Host, cross-language wire formats, exclusive build/test tools, obsolete CMake and CI routing, package assets and current documentation references after their retained behavior tests exist. Preserve package identities, public C# declarations, generator output contracts and observable behavior. Do not claim compatibility merely by keeping namespaces.

Maintain per-source admission limits, one active user operation per session, deterministic query disposal, cancellation ownership, bounded streams and resource return. Explicitly verify:

- pre-cancel and cancellation after server/SQLite execution has begun; SQLite execute, reader step and lock/busy waiting are separate scenarios;
- early stream break, mapping exception, decoder failure, session/source close, concurrent operations and pooled connection reuse;
- success commit, rollback, failed-transaction cleanup, savepoints and lost PostgreSQL COMMIT acknowledgment; unknown outcome stays unknown and is never automatically replayed;
- NULL versus omitted mutations, exact JSON/decimal policies, key/tenant boundaries, relation batch counts, empty groups and capability rejection;
- unchanged PostgreSQL schema, SQLite file and persisted migration identities/checksums.

[Driver source review](driver-source-review.md) records a material SQLite constraint: published Microsoft.Data.Sqlite 11.0.0 has synchronous async methods and a no-op `Cancel()`. Investigate a managed adapter over supported driver/native-dependency capabilities while preserving command/connection lifetime. A pre-call token check, abandoned Task, timer, or successful pre-cancel test does not prove in-flight cancellation. Keep any unresolved semantic difference explicit and block compatibility acceptance where it violates the retained contract.

Follow product module registration. Inspect `python3 eng/ci/impact.py origin/main --output artifacts/DB-DotNet-01-plan.json` against the committed diff; fix routing in this change if it misses affected consumers or selects unrelated work. Both top-level packages need separate runners. Run selected checks once; independent checks can run in parallel. Do not run JIT consumers or an unrequested clean-image/CPU-emulation campaign.

For each package independently, pack, inspect shipped DLL/XML APIs and metadata, restore an external ordinary PackageReference consumer, publish `-c Release -r linux-x64 -p:PublishAot=true`, and execute the resulting binary against the actual database. Capture resolved dependency graphs, generator output, final `.nupkg` assets and loaded dependencies. Edit an ordinary entity/DTO, rebuild only C# and re-run. No Korda native toolchain or handwritten foreign-language code may be required.

Only after both compatibility lanes pass, freeze immutable package/binary/consumer/dependency hashes as the **first compatible .NET internal baseline**. That baseline is the before-optimization comparison; previous C++ packages remain compatibility/history inputs only.

## Phase 3 — equivalent business and short optimization

Use [workloads.md](workloads.md) and [workload-cases.json](workload-cases.json). At least 24 distinct business operations must execute on each route and database; mode/size variations do not manufacture distinct cases. Korda uses its released Fluent API and source-generated mapping. Dapper uses Dapper.AOT-generated parameter and row factories; retain a call-site manifest, emitted generated C#, build diagnostics and actual Native AOT execution proving every measured call is intercepted.

Use identical .NET drivers, database engines, seed, indexes/statistics, durability/isolation, pool settings, concurrency and result contracts within each provider pair. Compare dynamic construction separately from reusable/precompiled query shapes. Complete all results and validate types, field counts, rows, values and durable effects. Retain real emitted SQL and plans; differing plans remain part of the business result, with an additional same-SQL diagnostic to locate the gap.

Measure short independent processes in an interleaved before/after order. Change one demonstrated hotspot, rerun correctness and compare repeated absolute metrics. Keep reproducible benefits only; resource retention must remain bounded. Stop when further changes repeatedly fall within measured noise or would weaken semantics. Preserve rejected attempts and remaining hotspots. Do not replace measurements with estimated performance claims.

## Allocation accounting

The general target is 0 B of extra library-owned managed allocation per operation on steady-state common paths. Record end-to-end process allocation first, using raw integer cumulative allocated bytes before and after a known number of successful/failed operations and rows. Use whole-process Gen 0/1/2 collection counts. A thread-local counter is insufficient for async/concurrent paths.

Report four attribution groups: required business results (including library-created lists, DTOs and strings), attributable Korda overhead, driver/runtime/tool overhead, and unattributed residual. Do not double-count groups or subtract noisy unrelated controls and label the remainder exact. Attribute with stacks, isolated path probes and matched controls; identify which method supports each number. Initialization, errors, cancellation, exhaustion and resize/pool growth have separate rows. Zero is established only by exact raw counters and bounded accounting for the named path; no collection, rounded averages or 0 B/row are insufficient.

The 100-DTO list query has a dedicated row. Both routes return the same `List<TDto>`-compatible business shape, 100 instances and identical selected fields/strings. Report total B/op, business result B/op, Korda extra B/op and unresolved driver/runtime bytes without hiding list or string ownership. Retain CPU, native/in-process engine costs and post-drain memory when reducing managed bytes.

## Phase 4 — four continuous dedicated long segments

Freeze final candidate packages before the campaign. Admit a dedicated Linux environment with recorded host/resource identity, exclusive measurement ownership, affinity/quotas, database placement, dependency versions, free storage and before-only noise calibration. An ordinary shared sandbox or PR runner is not admitted merely because it can run for 30 minutes. Build/calibration/warmup and unrelated work must stop during each measured segment.

Run four sequential exclusive cells: Korda × PostgreSQL, Dapper.AOT × PostgreSQL, Korda × SQLite, Dapper.AOT × SQLite. Each needs at least 1,800 **continuous effective mixed-load seconds**; total minimum is 7,200 seconds. Warmup, calibration, drain and idle retention are extra. IDs and a preregistered order appear in acceptance.json; restore matching seeds/settings before each segment. Do not combine interrupted short probes into long credit.

Retain package/executable/generated-code hashes, workload manifest, seed, driver/engine versions, source commits, offered-load parameters, monotonic interval and UTC timestamps, raw operation ledger and time series. Capture scheduled starts, actual starts, success, failure, rejection, retry and pending counts. At fixed offered rate latency starts at scheduled issue time and includes queueing. Separately determine sustainable successful throughput under the same p99 and error constraints.

For every route/database report success ops/s, rows/s, p50/p95/p99, errors/rejections/retries, client CPU seconds/success, steady/peak RSS, post-drain retained memory, whole-process managed B/op and B/row, Gen 0/1/2. PostgreSQL server CPU/RSS are separate; SQLite engine cost belongs to the client. Report unsupported counters as unavailable with reasons. Account for resource drain and residual bounded pool state.

## Phase 5 — review, normal delivery and public consumption

Bind independent non-author technical review to exact diff/source and resolve findings. Normal merge authority is already granted; obey required repository checks without changing protection or impersonating another approver. Observe actual merged-main CI, both automatic preview publication results and exact NuGet versions. Download the public archives; independently publish and execute each provider's ordinary external Native AOT consumer using those public packages. A local-feed success does not substitute for this gate.

Keep PRs, commits, CI/release URLs, package URLs, raw evidence and reproduction commands in this batch. No file predicts the containing commit's future CI result. Final Chinese delivery reports migration compatibility, four long cells, before/after gains, final absolute Dapper.AOT differences, remaining limitations and all delivery links. If a gate is blocked, preserve a concrete resumable handoff and do not mark the task complete.

## Executable record and product commands

```sh
# Plan; record structure/integrity, not product execution.
python3 tools/verify_db_dotnet.py
python3 tools/verify_db_dotnet.py --verify-frozen-history
# This must fail until all actual acceptance evidence exists.
python3 tools/verify_db_dotnet.py --require-complete

# Product; inspect the committed change and run groups actually listed by its plan.
python3 eng/ci/worker.py check-index
python3 eng/ci/impact.py origin/main --output artifacts/DB-DotNet-01-plan.json
python3 eng/ci/worker.py run artifacts/DB-DotNet-01-plan.json linux
python3 eng/ci/worker.py run artifacts/DB-DotNet-01-plan.json postgresql
python3 eng/ci/worker.py run artifacts/DB-DotNet-01-plan.json sqlite
```

The product worker commands use the existing registered interface; an absent group must not be invented. Exact benchmark executable arguments, data-seed commands, generated-code audit and public-consumption commands are recorded from their implemented/observed receipts. They are not asserted to exist or have executed by this initial Plan checkpoint.
