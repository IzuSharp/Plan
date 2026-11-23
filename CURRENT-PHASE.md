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

# Current phase — complete Public API refinement and exact acceptance

The active scope is the existing 34 Research, 32 Documentation and 48 future
Delivery tasks: source inspection, isolated Design verification, detailed public
API/native contracts, documentation standards, and the authorized Design/Plan
PRs and compliant merges. NativeWeave product files and the 48 Delivery
implementations remain outside this phase.

The 0.4.0 API obligations and contracts require actual independent technical
review and exact binding attestations. Their current states are recorded in the
graphs, Design registry and acceptance indices; candidate preparation alone does
not establish acceptance. Earlier 34R/32D/21-contract Accepted records remain immutable historical
facts, retained in `ledger/public-api-2026-11-14/prior-acceptance.json` and their
original committed evidence. They do not accept new API bytes. No recovered
script or prior successful run is counted as execution against changed inputs.

Database/ORM and Server execution require mature Rust engines. B15 owns the C#
application surface; B17 is the production Rust host. Kestrel is only a comparison
path. Ordinary Entity, DTO and Handler additions use precompiled native modules,
static C# metadata and normal dotnet build/run/publish without manual rd.xml or
user Rust builds. The existing 48 tasks now carry exact API inputs, type-policy
associations, document owners, module-specific guide/example scopes and concrete
consumer/Native AOT acceptance duties.

`public-api-acceptance-workflow.md` defines candidate freezing, actual independent
review, fresh contract/task evidence, per-reviewer binding attestations and the
single PR for each repository. Use original complete historical gates at their
original immutable pair and current gates at the actual pinned API candidate.
After review and CI, merge Design first, pin its returned merge SHA in the same
Plan PR, refresh the exact task bindings and validate again before merging Plan.

Design acceptance means implementation-guiding research and contracts have been
reviewed. Product execution, release, real-service fault/load behavior and
Windows/Linux package conformance retain their separately owned Delivery gates.
All 48 Delivery nodes stay `planned_candidate` with
`implementation_authorization.status: not_authorized` throughout this phase.
