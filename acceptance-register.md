# DB-Scope-01 — current database product scope

The owner authorized DB-Scope-01 on 2026-11-21: stop Perf-01, retain the PostgreSQL/SQLite strong-typed Fluent ORM with Rust SeaQuery/SQLx and Native AOT, remove NativeWeave-owned Server/gRPC/MCP and non-database engines/demos, run real Linux consumers, review and merge, then stop. Ordinary C# applications choose their own hosting; no new HTTP/gRPC wrapper or ORM feature is in scope.

**Start here:** [current execution plan](ledger/evidence/batches/DB-Scope-01/plan.md), [Linux handoff](ledger/evidence/batches/DB-Scope-01/handoff-linux.md), [acceptance](ledger/evidence/batches/DB-Scope-01/acceptance.json), and `delivery-graph.json.current_execution`. These supersede older phase/authorization/product-scope statements. Database Host remains part of the database execution layer. Performance optimization and 30-minute load tests are deferred.

The three legacy graphs, 114 packets, prior source-driven baseline, original acceptance bindings and delivered Task-01 through Task-07 evidence remain historical. Do not alter them to invent acceptance or resume removed components. Current acceptance requires new source-bound DB-Scope-01 evidence; unchanged historical gates run against their exact original inputs.

**Observed delivery checkpoint:** final candidate10 CI44919645468 and independent source/runtime evidence reviews passed; all eleven product checks plus independent review are source-bound in acceptance.json. Design PR14 and product PR20 are merged with their exact tested trees; every required main check passed. Plan delivery review/merge and its exact main CI, followed by the evidence-only accepted-delivery record, remain in progress. See the [Linux acceptance summary](ledger/evidence/batches/DB-Scope-01/results/linux-acceptance-summary.md).

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
