# Task-04 Linux x64 handoff

## Scope and recovered inputs

Task-04 covers A06, A07, A08, A14, A15, A16, A17, A18, A20, A23 and A24.
The current user explicitly authorizes all Linux-applicable work and normal paired
PR/merge/CI/automatic-preview closeout. A15 is deferred; A23 is Linux-only.
No other task package is authorized by this handoff. Global historical design and
delivery graphs remain unchanged; this platform record is not global acceptance.

Implementation baseline: `5ca367a2fa53e0a756b4c5bcb506113d5c1371a1`.
Plan baseline: `dcf74c700a14fa1983defe2aaef1ca043b9dbc3d`.
Read-only Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.

A02/A05/A09 are reused from [Task-02](../Task-02/handoff-linux.md).
A03/A04/A10/A11/A13/A22 are reused from [Task-03](../Task-03/handoff-linux.md).
All required package-external Linux prerequisites have accepted component evidence.
Do not repeat their implementation or historical acceptance. The initial remote
branch/PR and local worktree checks found no existing Task-04 work to recover.

## Current task state

| Task | Linux state | Owner | Next step |
| --- | --- | --- | --- |
| A06 | accepted_linux_component | callbacks | Reuse accepted component; A14/A16/A18 compose it without repeating historical acceptance. |
| A07 | accepted_linux_component | callbacks | Reuse accepted Task bridge immediately in A08/A18/A20 and final A14 composition. |
| A08 | accepted_linux_component | packaging | Reuse accepted executor; no repeated component acceptance. |
| A14 | accepted_linux_assembled | packaging | Reuse actual checkpoint4 Ubuntu/CPU/fresh-SDK/runtime-transfer evidence; final merged CI remains batch closeout. |
| A15 | deferred_other_platform | none | Windows is explicitly deferred by the user. |
| A16 | accepted_linux_assembled | packaging | Reuse actual checkpoint4 Ubuntu/CPU/fresh-SDK/runtime-transfer evidence; final merged CI remains batch closeout. |
| A17 | accepted_linux_component | sync_engine | Reuse accepted real synchronous engine for A24 generated package conformance. |
| A18 | accepted_linux_component | callbacks | Reuse accepted actual Hyper/Tokio HTTP component; no repeat of component acceptance. |
| A20 | accepted_linux_component | root | Reuse accepted Linux cross-language properties, bounded races, supported sanitizer profile and isolated controls; no historical rerun. |
| A23 | accepted_linux_component | sync_engine | Reuse accepted Linux affinity probe; unavailable device/other-platform rows remain explicit. |
| A24 | accepted_linux_assembled | packaging | Reuse accepted heterogeneous A17/A18 generated-package pair; final merged CI/release remains batch closeout. |

Exact branches, worktrees, dependencies, commits and new validation outcomes are
tracked in [status-linux.json](status-linux.json). A06, A07, A08, A17, A20 and A23 Linux component acceptance and independent review are recorded
in their original evidence directories. A07 may be consumed immediately; do not wait
for whole-batch closeout or repeat these completed component checks. A14/A16 assembled Linux acceptance is also recorded from actual checkpoint4 CI.
A18 real HTTP and the heterogeneous A24 generated-package pair are now independently
reviewed and accepted. All ten Linux-applicable components are accepted; batch delivery
remains open until final integration checks, normal merges and automatic preview closeout.

## Workspaces and integration

Reuse the existing checkout parent as ROOT. Batch branches in both repositories
are `task/Task-04-linux`; batch worktrees are
`ROOT/.worktree/Task-04-linux/{NativeWeave,Plan}`. Each component uses its listed
isolated `task/Task-04-<ID>-linux` branch/worktree. The sibling Design worktree is
read-only at the exact pinned commit. Root integrates shared solution, Cargo and
build registrations serially as minimal A13 patches; component work remains parallel.

Use SDK 11.0.100 / C# 15 / Rust 1.100.0 and the existing local toolchain/cache.
The local host is Debian 13, so it cannot establish the declared Ubuntu 24.04
baseline by assertion. A14/A16 target-baseline and pristine no-Rust checks passed the existing Ubuntu
CI/container flow with scoped additions and no new matrix; see ci-checkpoint4-linux.json.

## Evidence and delivery

Keep exact raw execution receipts, failures and artifact identities. Public Plan
records should be bounded summaries and source/hash/recovery indices without raw
source/log/certificate dumps or unrelated machine details. Retain complete raw
bytes separately when necessary; never rewrite a failed record as success.

Implementation PR: https://github.com/IzuSharp/NativeWeave/pull/15 (ready; final checks running).
Plan PR: https://github.com/IzuSharp/Plan/pull/18 (final acceptance checkpoint; final checks pending).

Next: The bounded shared-registration review passed at Native source29fa773
(remote11bb5a39, identical tree). Submit the final Plan acceptance checkpoint,
require final-head checks, merge normally and verify exact merged CI
and the existing automatic preview/registry consumers. Component acceptance is complete;
do not repeat it. Stop after Task-04; no Task-05/Task-06 execution is authorized here.

## Recovery and retained bytes

All ten accepted component source trees are preserved on their prescribed remote
branches. [source-recovery-linux.json](source-recovery-linux.json) maps original
execution commits to remotely fetchable, byte-identical tree snapshots. Transport
commit metadata differs and is not presented as fresh execution evidence.

[raw-evidence-index-linux.json](raw-evidence-index-linux.json) identifies the
retained raw logs, failures, corpus and runtime/package bytes by archive SHA-256.
Final A18/A24 and merge/publication evidence is retained during delivery closeout.
