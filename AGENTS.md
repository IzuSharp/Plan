# Current maintenance — Korda-Design repository rename

The owner authorizes updating current documentation and automation references after `IzuSharp/NativeWeave-Design` was renamed to [IzuSharp/Korda-Design](https://github.com/IzuSharp/Korda-Design), including reviewable PRs and normal merges. Use `docs/korda-design-rename` for this maintenance. The owner has stopped DB-Perf-01; the earlier task authorities below are historical and do not authorize resuming implementation or performance work.

Preserve all existing task acceptance states, source pins, graphs, packets, evidence and historical tool bytes. Current remote URLs and CI `repository` inputs use `IzuSharp/Korda-Design`; frozen tools retain `NativeWeave-Design` as their checkout-directory and evidence-key alias. See the [repository maintenance notes](README.md#repository-maintenance-and-historical-verification). The paired integrity workflow runs the original DB-Perf-01 record gate at frozen Plan `38f8ce8a01f88e6e4c4459926f197c5438c2f6fc` and retains every earlier frozen gate.

## Prior task instructions (historical; original text preserved)

# Current task — DB-Perf-01

The owner authorizes Linux x64 database and Fluent ORM performance work on the current C++20/libpq/sqlite3 Korda product: comparable baselines, profiling, implementation, real measurements, independent review, PRs, normal merges, automatic preview and actual public NuGet Native AOT consumption. Use `task/DB-Perf-01-linux` and task-named worktrees. Read the [plan](ledger/evidence/batches/DB-Perf-01/plan.md), [handoff](ledger/evidence/batches/DB-Perf-01/handoff-linux.md), [baseline](ledger/evidence/batches/DB-Perf-01/baseline.json) and [incomplete acceptance](ledger/evidence/batches/DB-Perf-01/acceptance.json).

Preserve current public APIs, `Db*` attributes, separate provider packages, ownership/cancellation/backpressure/thread safety and ordinary C#-only Entity/DTO edits. Implementation and benchmarks belong in Korda; measurements, raw evidence indexes and recovery state belong in this batch. Synchronize Design if a public contract changes. Follow current Korda module routing and Native AOT package checks; do not add JIT consumers or run the four-hour campaign in ordinary PR CI.

All four comparison columns and both databases require actual equivalent measurements. Retain raw cumulative allocation counts before division, process-wide async/concurrent attribution, CPU/memory/native costs and explicit unmet/unproven paths. Internal or per-row zero bytes never establish whole-framework zero GC. The eight continuous effective 30-minute mixed-load segments require an admitted dedicated Linux resource set and remain 0/8 until actual source/binary/workload/environment-bound evidence exists.

Run `python3 tools/verify_db_perf.py`; use `--verify-frozen-history` for the unchanged previous task gate at frozen Plan `bc1956936ee77a997a016856c97def6aabc0bbc6`. The CI workflow separately checks that immutable DB-Rename snapshot and every existing historical gate. Preserve earlier verifier/evidence bytes and the original `awaiting_review` snapshot without relabeling it. This owner's new authority supersedes older task exclusions/review-only stop instructions below.

Normal merge/publication authority is already granted, but acceptance requires actual correctness, measurements, review and observed CI/release results. Never bypass checks, change permissions or impersonate an approval account. Finish the Chinese evidence-backed report after verified delivery and stop. The containing evidence commit's own future CI is checked separately.

## Earlier task authority (historical; original text preserved)

# Current task — DB-Rename-01

The owner authorizes renaming Korda's database attributes to natural `Db` names, preserving behavior, synchronizing current documentation, testing Linux x64 Native AOT consumers against both real databases, and pushing reviewable PRs. Read the [current plan](ledger/evidence/batches/DB-Rename-01/plan.md) and [handoff](ledger/evidence/batches/DB-Rename-01/handoff-linux.md). Use `task/DB-Rename-01-linux` and task-marked worktrees.

`delivery-graph.json.current_execution` identifies this task; the completed DB-API-01 execution and all source-bound historical evidence remain unchanged. Run `python3 tools/verify_db_rename.py`. It validates current scope and runs the original completed DB-API-01 gate at frozen Plan `85f7f83e29e67f6865c14c64585139541b8a1a1f`; existing earlier historical CI gates remain intact.

Stop with passing PR checks and a Chinese delivery brief, awaiting maintainer review. **Do not merge or publish publicly.** Product acceptance requires observed source-bound evidence; a documentation check is not an AOT or database execution result. The earlier merge/publication authorities below are historical.

## Earlier task authority (historical)

# Current task — DB-API-01

The owner authorizes Korda's existing PostgreSQL/SQLite Fluent ORM experience enhancements on Linux x64, including implementation, tests, English documentation, pushes, PRs, normal merges and verification of repository-triggered publication. Read the [current plan](ledger/evidence/batches/DB-API-01/plan.md), [handoff](ledger/evidence/batches/DB-API-01/handoff-linux.md) and [acceptance](ledger/evidence/batches/DB-API-01/acceptance.json). `delivery-graph.json.current_execution` owns this batch. Use `task/DB-API-01-linux` and `.worktree/DB-API-01-linux/{Korda,NativeWeave-Design,Plan}`.

Plan comes before Design; the new Design contract precedes product changes. Compare the existing query and relationship samples against order/customer/detail business calls before filling actual gaps. Preserve C++20/libpq/sqlite3 execution and Native AOT, package isolation, native compatibility and ordinary DTO-only native reuse. Korda's current AGENTS.md owns module routing, checks and publication: direct AOT consumers, no JIT consumer checks, and no clean-image or CPU-emulation campaign unless separately requested. Product acceptance is evidence-based, not a document status.

Run `python3 tools/verify_db_api.py` for this batch. Old DB-CPP-01 gates run unchanged at Plan `5be447a868be78713ada52f46cee16409f0edc13`, including its completed acceptance; all earlier frozen gates remain in CI. Retain previous graphs, evidence, failure states and verifier bytes. The previous task exclusions below are historical and do not prohibit this newly authorized work. No performance campaign, server wrapper or additional platform acceptance is authorized.

## Previous task authority (historical)

# Current task — DB-CPP-01

The owner authorizes the behavior-compatible C++ migration of the merged PostgreSQL/SQLite database product on Linux x64, including tests, documentation, pushes, PRs and normal merges. Read [the current plan](ledger/evidence/batches/DB-CPP-01/plan.md), [handoff](ledger/evidence/batches/DB-CPP-01/handoff-linux.md) and `delivery-graph.json.current_execution`. Preserve C# API, ABI, package identities and stored data. DB-API-01 and DB-Perf-01 are excluded. Prior DB-Scope-01 completion remains historical, verified at its immutable commit. Do not claim unexecuted migration acceptance.

---

# DB-Scope-01 — current database product scope

The owner authorized DB-Scope-01 on 2026-11-21: stop Perf-01, retain the PostgreSQL/SQLite strong-typed Fluent ORM with Rust SeaQuery/SQLx and Native AOT, remove NativeWeave-owned Server/gRPC/MCP and non-database engines/demos, run real Linux consumers, review and merge, then stop. Ordinary C# applications choose their own hosting; no new HTTP/gRPC wrapper or ORM feature is in scope.

**Start here:** [current execution plan](ledger/evidence/batches/DB-Scope-01/plan.md), [Linux handoff](ledger/evidence/batches/DB-Scope-01/handoff-linux.md), [acceptance](ledger/evidence/batches/DB-Scope-01/acceptance.json), and `delivery-graph.json.current_execution`. These supersede older phase/authorization/product-scope statements. Database Host remains part of the database execution layer. Performance optimization and 30-minute load tests are deferred.

The three legacy graphs, 114 packets, prior source-driven baseline, original acceptance bindings and delivered Task-01 through Task-07 evidence remain historical. Do not alter them to invent acceptance or resume removed components. Current acceptance requires new source-bound DB-Scope-01 evidence; unchanged historical gates run against their exact original inputs.

**Delivered snapshot accepted:** Design PR14, product PR20 and Plan PR24 are merged with their exact tested trees and successful required main CI. All fourteen source-bound acceptance claims and seven execution phases are complete. This evidence-only record checks its own PR/main CI separately and does not predict that result. See the [Linux acceptance summary](ledger/evidence/batches/DB-Scope-01/results/linux-acceptance-summary.md) and [handoff](ledger/evidence/batches/DB-Scope-01/handoff-linux.md). Stop after the record checks; performance work remains deferred.

## Historical planning text (superseded for current product scope)

# NativeWeave Plan Working Rules

NativeWeave uses Source-Driven Deep Native Integration. C# is the application development language, providing strongly typed Fluent APIs, static metadata/DTOs, and business handlers; database drivers, query/dialect/ORM relational execution, and Server networking/protocols/runtimes must reuse mature Rust engines. Kestrel, Npgsql, and similar implementations serve only as comparison baselines. Ordinary applications do not require handwritten Rust/FFI or native recompilation when an Entity/DTO/Handler is added. Preserve normal dotnet build/run and actual Native AOT publishing; do not build a C# SQL AST, a full LINQ Provider, or a monolithic Core runtime.

1. The current scope is research, design, and refinement of future implementation plans only. The user has authorized the necessary Design/Plan commits, PRs, and merges that comply with repository rules; do not ask repeatedly. Do not write to the NativeWeave product repository.
2. Preserve the 34 Research / 32 Documentation / 48 Delivery tasks and the three graphs; `fragments/` only elaborates existing tasks. Read existing results and actual reviews before filling gaps.
3. Every packet/graph has an exact revision/hash; acceptance binds actual sources, dependencies, and independent review. Do not merely change status or add fabricated evidence.
4. Technical designs may be accepted before product implementation; track product AOT/real-service/long-running-load/release obligations separately. Strictly distinguish source read, upstream tests read, actual execution, and product acceptance.
5. Write only within your own scope. Work in parallel in independent worktrees; integrate shared root build manifests through small A13 integration patches, without a global lock.
6. After changing current graphs/packets/registry, run structural, current-completion, and negative-case gates; run historical frozen checks at their original commits. Do not treat an old proposed snapshot as a rule permanently prohibiting acceptance.
7. Preserve failure records, raw bytes, and separate Windows/Linux identities; when binaries are omitted, state their archive/content hashes and reproduction method explicitly.
8. Subagents may perform actual independent technical review, but the same GitHub identity must not impersonate another approval account. Do not bypass Required Checks or change permissions/licenses to make a merge pass.

## Mandatory C# public API and documentation standard

Every existing Delivery task must follow the exact Design commit pinned in source-driven-baseline.json, including `docs/standards/csharp-public-api-and-documentation.md` and `docs/api/README.md`. The packet's API inputs and documentation owner are acceptance requirements, not optional follow-up work.

1. Research the relevant current stable .NET/C# public API families and actual fixed source; never confuse Preview or upstream capability with NativeWeave product support.
2. Provide complete exact C# signatures, natural minimum/advanced consumers, nullability/defaults, ownership/lifetime, async/cancellation, errors, concurrency, capabilities and cost. Map the public member through managed adapter, C ABI, Rust adapter and actual Engine operation.
3. Keep SQL/network/domain execution in Rust and Core minimal; ordinary Entity/DTO/Handler additions must reuse precompiled native assets with normal dotnet build/run/publish.
4. The implementing task owns XML documentation, generated API Reference, guides, examples, compatibility and the required compilation/AOT/consumer checks. Record justified applicability for internal-only work; do not add unreviewed public scaffolding.
5. Independently review API completeness, usability, correctness, allocation/copy cost, compatibility and documentation. Preserve historical accepted inputs and bind materially changed content to fresh review and hashes.
6. New Engines and independent repositories must actually adopt the versioned standard and install its checks using the Design templates; AGENTS.md is not inherited across repositories. Product adoption is a future A13/A22/A24 obligation, not permission to write product code in this phase.

For the Public API 0.4.0 refinement, follow `public-api-acceptance-workflow.md`.
Preserve original acceptance bytes; current mandatory gates include
`verify_public_api_history.py`, `verify_public_api_plan.py` and exact
`prepare_acceptance.py`/`verify_completion.py` binding checks. API inputs are
individually SHA-256 pinned in each Delivery node and the Design repository is
commit-pinned. A changed input invalidates its current binding; no recovered
script, historical translation review or design stub is new acceptance evidence.
