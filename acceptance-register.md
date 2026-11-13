# Acceptance register and evidence boundaries

The actual current status is computed from the three graphs and the Design registry; summaries are in ledger/reviews/D32.md and verification/completion.json. Historical 10R partial/24R planned and 4D partial/28D draft figures were merely the takeover register; they must not obscure the existing 17 complete triplets and 16 specifications or automatically count them as accepted.

## Formal research/design acceptance on 2026-11-13

| Scope | Current status | Authoritative record |
| --- | --- | --- |
| R01–R34 | 34 accepted | research-graph.json, ledger/acceptance/R*.json |
| D01–D32 | 32 accepted | documentation-graph.json, ledger/acceptance/D*.json |
| 21 technical contracts at 0.3.0 | 21 accepted | docs/contracts/registry.json and acceptance-index.json in pinned Design |
| A01–A24 / B01–B24 | 48 planned_candidate / not_authorized | delivery-graph.json, 48 task packets, 10 fragments |

The Design input is merged commit `08e3aaee73aad174620dcff18ed21b3b14c5e632`; Plan task semantics and file inputs are pinned to `c3947b378e0a251f8dfeaf7fd7d4acc636631974`. Each task's status and acceptance record are separate from the original input commit to avoid self-referential hashes. The formal task index is [ledger/completion-acceptance.json](ledger/completion-acceptance.json); final confirmations by the three actual independent executors are in [ledger/reviews/final-2026-11-13/](ledger/reviews/final-2026-11-13/).

Complete validation verifies 840 input entries (266 for contracts and 574 for R/D tasks), 114 packets, 10 fragments and actual review/attestation chains. The accepted work consists of existing research conclusions, detailed designs and future implementation guidance; native research slices have not been copied into product acceptance results. Final external records for the PRs and CI on the exact heads are at [Design #10](https://github.com/IzuSharp/NativeWeave-Design/pull/10) and [Plan #8](https://github.com/IzuSharp/Plan/pull/8).

## Acceptance semantics

Research acceptance: pinned source and necessary actual experiments answer the questions, exceptional/boundary behavior and applicability are clear, and independent technical review exists. Design acceptance: interfaces/states/ownership/errors/platforms/implementation acceptance criteria are sufficient for development and consistent with research and other specifications. Product acceptance: actual acceptance of the implementation, target environment and release combination; all 48 current Delivery tasks remain unexecuted/unauthorized.

Acceptance manifests bind the current task revision/node+packet hash, source commits, dependency acceptance hashes and selection snapshots; contracts bind version/spec hash/actual review. Evidence records alone cannot authenticate a person's identity, so the concrete inputs and finding resolutions from actual subagent review reports are also retained. A subagent is not another GitHub approval account.

Any hash/version/dependency change requires review of the affected scope; changing hashes must not conceal an old review. All experimental failures, unexecuted platforms and future production obligations remain as originally recorded; current-phase acceptance counts must come from actual file validation, not manually written totals.
