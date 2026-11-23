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

# Acceptance Register and Evidence Boundaries

The three graphs and the Design registry determine the current actual state; see ledger/reviews/D32.md and verification/completion.json for summaries. The historical 10 Research partial / 24 Research planned and 4 Documentation partial / 28 Documentation draft counts were only takeover records; they must neither obscure the pre-existing 17 complete triplets and 16 specifications nor automatically count them as accepted.

## Current Public API refinement 0.4.0

The current API/contract/packet revision is governed by its own exact acceptance
records. Original accepted subjects remain available through the prior snapshots in
[ledger/public-api-2026-11-14/prior-acceptance.json](ledger/public-api-2026-11-14/prior-acceptance.json).
Current acceptance requires new independent scoped reports, exact committed
inputs and reviewer-authored binding attestations; see
[the acceptance workflow](public-api-acceptance-workflow.md). The graph and registry
are authoritative; the historical counts below do not accept the new API bytes.
All 48 Delivery nodes remain planned_candidate and not_authorized.

## Historical Research and Design Acceptance on 2026-11-13

| Scope | State at that historical acceptance | Authoritative record |
| --- | --- | --- |
| R01–R34 | 34 accepted | research-graph.json, ledger/acceptance/R*.json |
| D01–D32 | 32 accepted | documentation-graph.json, ledger/acceptance/D*.json |
| 21 technical contracts at 0.3.0 | 21 accepted | docs/contracts/registry.json and acceptance-index.json in the pinned Design revision |
| A01–A24 / B01–B24 | 48 planned_candidate / not_authorized | delivery-graph.json, 48 task packets, 10 fragments |

The Design input is the merged `08e3aaee73aad174620dcff18ed21b3b14c5e632`; Plan task semantics and file inputs are pinned at `c3947b378e0a251f8dfeaf7fd7d4acc636631974`. Each task's status and acceptance record are separate from its original input commit, avoiding self-referential hashes. The formal task index is [ledger/completion-acceptance.json](ledger/completion-acceptance.json); final confirmations from the three actual independent executors are in [ledger/reviews/final-2026-11-13/](ledger/reviews/final-2026-11-13/).

That historical complete validation verified 840 input entries (266 for contracts and 574 for Research/Documentation tasks), 114 packets, 10 fragments, and the actual review/attestation chain. Acceptance covers existing research conclusions, detailed designs, and future implementation guidance; native research slices have not been copied into product acceptance results. See [Design #10](https://github.com/IzuSharp/NativeWeave-Design/pull/10) and [Plan #8](https://github.com/IzuSharp/Plan/pull/8) for the final external records of the PRs and CI at their exact heads.

## Acceptance Semantics

Research acceptance: questions have been answered through pinned source and necessary actual experiments, with clear failure/boundary behavior, applicability, and independent technical review. Design acceptance: interfaces/state/ownership/errors/platforms/implementation acceptance are sufficient to guide development and agree with research and other specifications. Product acceptance: actual acceptance of the real implementation, target environment, and release combination; all current 48 Delivery tasks remain unexecuted/unauthorized.

An acceptance manifest binds the current task revision/node+packet hash, source commit, dependency acceptance hashes, and selection snapshot; a contract binds its version/specification hash/actual review. Evidence records alone cannot authenticate personal identity, so the specific inputs and finding resolutions from actual subagent review reports are also preserved. Subagents are not separate GitHub approval accounts.

Any hash/version/dependency change requires rechecking the affected scope; do not change hashes to conceal stale reviews. Preserve all experiment failures, unexecuted platforms, and future production obligations as they are; acceptance counts for the current phase must come from actual file validation, not manually chosen totals.
