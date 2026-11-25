# Korda Plan

The Design repository is now [IzuSharp/Korda-Design](https://github.com/IzuSharp/Korda-Design), renamed from `IzuSharp/NativeWeave-Design`. Use the canonical name for current links, remotes and CI repository selection. This repository remains [IzuSharp/Plan](https://github.com/IzuSharp/Plan).

## Repository maintenance and historical verification

The owner has stopped DB-Perf-01. The current maintenance only updates references for the Design repository rename; the task instructions below are retained as history. Existing acceptance states, source commits, graphs, packets and evidence remain unchanged.

New working checkouts can use sibling `Plan/` and `Korda-Design/` directories. Frozen verification tools still require the original `NativeWeave-Design/` directory and repository-qualified evidence keys. When reproducing those checks, check out the canonical `IzuSharp/Korda-Design` repository at the recorded commit into that historical directory name. The old name in a pinned input, review, log, archived command or historical tool is part of its provenance, not the current GitHub repository name.

The [paired integrity workflow](.github/workflows/native-slices-final-check.yml) fetches Design from the canonical repository while retaining its historical checkout path and fixed source commit. It runs the unchanged DB-Perf-01 record and schema checks at Plan `38f8ce8a01f88e6e4c4459926f197c5438c2f6fc`, alongside the existing frozen DB-Rename-01, DB-CPP-01, DB-Scope-01 and research/design gates. These checks verify the historical snapshot's recorded incomplete state; they do not resume performance work or grant acceptance.

## Prior task instructions (historical; original text preserved)

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

# DB-Scope-01 — current database product scope

The owner authorized DB-Scope-01 on 2026-11-21: stop Perf-01, retain the PostgreSQL/SQLite strong-typed Fluent ORM with Rust SeaQuery/SQLx and Native AOT, remove NativeWeave-owned Server/gRPC/MCP and non-database engines/demos, run real Linux consumers, review and merge, then stop. Ordinary C# applications choose their own hosting; no new HTTP/gRPC wrapper or ORM feature is in scope.

**Start here:** [current execution plan](ledger/evidence/batches/DB-Scope-01/plan.md), [Linux handoff](ledger/evidence/batches/DB-Scope-01/handoff-linux.md), [acceptance](ledger/evidence/batches/DB-Scope-01/acceptance.json), and `delivery-graph.json.current_execution`. These supersede older phase/authorization/product-scope statements. Database Host remains part of the database execution layer. Performance optimization and 30-minute load tests are deferred.

The three legacy graphs, 114 packets, prior source-driven baseline, original acceptance bindings and delivered Task-01 through Task-07 evidence remain historical. Do not alter them to invent acceptance or resume removed components. Current acceptance requires new source-bound DB-Scope-01 evidence; unchanged historical gates run against their exact original inputs.

**Delivered snapshot accepted:** Design PR14, product PR20 and Plan PR24 are merged with their exact tested trees and successful required main CI. All fourteen source-bound acceptance claims and seven execution phases are complete. This evidence-only record checks its own PR/main CI separately and does not predict that result. See the [Linux acceptance summary](ledger/evidence/batches/DB-Scope-01/results/linux-acceptance-summary.md) and [handoff](ledger/evidence/batches/DB-Scope-01/handoff-linux.md). Stop after the record checks; performance work remains deferred.

## Historical planning text (superseded for current product scope)

# NativeWeave Plan — Existing Research, Specification, and Future Implementation Graphs

The current phase is research, detailed design, and future Codex development planning; **do not write to the NativeWeave product repository or execute A/B Delivery tasks**. The recovery entry point is [source-driven-baseline.json](source-driven-baseline.json); the existing three graphs, exact evidence, and reviews determine the actual state.

**The Public API refinement has its own versioned review and exact acceptance bindings.** The preceding 34 Research / 32 Documentation / 21-contract acceptance is preserved at its exact committed inputs in the [prior acceptance manifest](ledger/public-api-2026-11-14/prior-acceptance.json). Current graph/registry status, actual scoped reviews, exact binding attestations and [current completion validation](verification/completion.json) determine whether the new revision is accepted. Follow the [Public API acceptance and merge workflow](public-api-acceptance-workflow.md); Design merges first and Plan binds its actual merge commit. All 48 Delivery tasks remain `planned_candidate / not_authorized`.

NativeWeave uses Source-Driven Deep Native Integration. C# is the application development language, providing strongly typed Fluent APIs, static metadata/DTOs, and business handlers; database drivers, query/dialect/ORM relational execution, and Server networking/protocols/runtimes must reuse mature Rust engines. Kestrel, Npgsql, and similar implementations serve only as comparison baselines. Ordinary applications do not require handwritten Rust/FFI or native recompilation when an Entity/DTO/Handler is added. Preserve normal dotnet build/run and actual Native AOT publishing; do not build a C# SQL AST, a full LINQ Provider, or a monolithic Core runtime.

## Three Graphs and Their Responsibilities

| Graph | Existing scope | Current completion requirements |
| --- | --- | --- |
| research-graph.json | R01–R34, 34 tasks | Actual pinned source, appropriate experiments, normal/failure/boundary conclusions, and independent technical review |
| documentation-graph.json | D01–D32, 32 tasks | 21 specifications, 10 implementation-detail fragments, and 1 final review, sufficient to guide implementation |
| delivery-graph.json | A01–A24 / B01–B24, 48 tasks | This round only refines interfaces, steps, ownership, local dependencies, parallelism, and acceptance; implementation is not authorized |

Each of the [114 independent task packets](task-index.md) records its exact revision and packet hash. `fragments/` elaborates existing Delivery tasks; it is not a fourth task graph. `start_dependencies` constrain starting, and `acceptance_dependencies` constrain final acceptance; research/specification references provide traceability only and do not automatically impose waiting. Contracts have exact versions and content hashes; research, design acceptance, and product verification are recorded separately.

## Established Division of Responsibilities

The primary Database path uses maintainer-precompiled SeaQuery+SQLx with dynamic business metadata. Mature SeaORM dynamic projection/static relationship capabilities are reused within their source-defined boundaries; optional specialized static Entity packages must not become prerequisites for ordinary entities. B01 exclusively owns shared Data interfaces, B07 exclusively owns fallible codecs, B09 only defines query-operation bindings, B11 owns native queries and dialects, B12 owns C# DTO materialization, B13 owns natural strongly typed Fluent APIs, and B14 owns native explicit relationships.

B15 is the **C# Server.Application / Handler interface**, and B17 is the **required Rust Server Host**; they complement one another. B16 provides Body/Bytes and budget components, and B17 reuses actual Tokio/Hyper/Tower/Axum engine capabilities; applications may independently opt into B18 Tonic and B19 rmcp, but both use only B17's Rust Host. The old Kestrel-versus-Rust exclusive-choice group has been retired; it is not an undecided product architecture.

## Working Method

First verify the actual GitHub HEAD and baseline pairing, then read the corresponding packet and Design specifications. Recheck complete results without repeating successful experiments. Use one independent worktree per task and modify only its owned scope; integrate small root solution/Cargo workspace patches through A13, without creating a global worker lock. Async/database/server work each has independently testable local components and final assembled acceptance; do not make the future reference application a circular prerequisite for every component's acceptance.

```bash
python3 tools/verify_public_api_history.py
python3 tools/verify_public_api_plan.py
python3 tools/validate_graphs.py --root . --output verification/graph-validation.json
python3 tools/mutation_checks.py
python3 tools/host_selection_checks.py
python3 tools/verify_completion.py
python3 tools/verify_completion.py --require-complete
```

The two repositories should be sibling directories named `Plan/` and `NativeWeave-Design/`. Current verification tools check structure, hashes, and gates; they cannot authenticate actual human identities or turn research experiments into product execution. Historical frozen validation runs against original commits, whereas current acceptance validation runs against the exact inputs for this round; the two must not be confused.

First check out the full Design SHA specified by the baseline. `--require-complete` requires acceptance of all 34 Research / 32 Documentation tasks and 21 contracts, and verifies every current exact input entry, 114 packets, 10 fragments, and actual independent bindings; it does not run native experiments or start Delivery.

## Continuation and Implementation Entry Points

See the [current API acceptance workflow](public-api-acceptance-workflow.md), historical [D32](ledger/reviews/D32.md), the [current phase](CURRENT-PHASE.md), and the [acceptance register](acceptance-register.md) for exact progress and independent review. Once the product phase is explicitly authorized in the future, A01, A19, A21, and B01 may be implemented in parallel first; the rest proceed according to actual local dependencies. Implementation still requires independent NuGet/clean no-Rust consumption, actual Windows/Linux AOT, real databases/networking, error/cancellation/resource behavior, and long-running-load/performance verification.

Source selection does not depend on ArcForges business logic or architecture. Merging research does not automatically publish packages, change permissions/licenses, or bypass Required Checks. Independent subagent technical review is not approval by another GitHub account.

## Public API implementation and documentation obligations

The existing 48 Delivery packets now bind the complete C# public API specification, native operation mapping and versioned documentation standard in the pinned Design repository. Read [API execution requirements](api-execution-requirements.md) and [execution policy](execution-policy.md). Each module owns XML/API Reference/guides/examples together with implementation; A13/A22/A24 install the shared rules and A16/B24 verify package consumption and release composition. These refinements preserve the three graphs and do not authorize Delivery execution.
