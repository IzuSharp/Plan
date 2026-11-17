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
| A07 | in_progress | callbacks | Complete Task state machine and actual cancellation/take/retire tests; root shared registration and locked graph ready. |
| A08 | waiting_dependency | queued | Start when A07 is ready. |
| A14 | pending_assembled_acceptance | packaging | Run complete A07 composition on Ubuntu baseline and transfer to runtime-only environment. |
| A15 | deferred_other_platform | none | Windows is explicitly deferred by the user. |
| A16 | pending_assembled_acceptance | packaging | Finish exact closure/publication cases and independent review; await A14 Ubuntu and SDK/runtime containers. |
| A17 | pending_review | sync_engine | Finish clean-source evidence and root review; preserve exact generated/native/package identities. |
| A18 | waiting_dependency | queued | Start when A07 is ready. |
| A20 | waiting_dependency | queued | Start when A07 is ready. |
| A23 | in_progress | root | Implement actual Linux owner-thread/callback/lease probe; no display/device certification. |
| A24 | pending_assembled_acceptance | root | Resolve independent scaffold review findings and run actual A17/A18 generated package consumers. |

Exact branches, worktrees, dependencies, commits and new validation outcomes are
tracked in [status-linux.json](status-linux.json). A06 Linux component acceptance and independent review are recorded in
[its evidence](../../A06/acceptance-linux.json); assembled packaging and the remaining
components are still in progress. Accepted A06 can be consumed immediately.

## Workspaces and integration

Reuse the existing checkout parent as ROOT. Batch branches in both repositories
are `task/Task-04-linux`; batch worktrees are
`ROOT/.worktree/Task-04-linux/{NativeWeave,Plan}`. Each component uses its listed
isolated `task/Task-04-<ID>-linux` branch/worktree. The sibling Design worktree is
read-only at the exact pinned commit. Root integrates shared solution, Cargo and
build registrations serially as minimal A13 patches; component work remains parallel.

Use SDK 11.0.100 / C# 15 / Rust 1.100.0 and the existing local toolchain/cache.
The local host is Debian 13, so it cannot establish the declared Ubuntu 24.04
baseline by assertion. A14/A16 target-baseline and pristine no-Rust checks will
use the existing Ubuntu CI/container flow with scoped additions, no new matrix.

## Evidence and delivery

Keep exact raw execution receipts, failures and artifact identities. Public Plan
records should be bounded summaries and source/hash/recovery indices without raw
source/log/certificate dumps or unrelated machine details. Retain complete raw
bytes separately when necessary; never rewrite a failed record as success.

Implementation PR: https://github.com/IzuSharp/NativeWeave/pull/15 (Draft).
Plan PR: https://github.com/IzuSharp/Plan/pull/18 (Draft).

Next: finish A07 and A23 while A17 completes review and A14/A16/A24 prepare
assembly. Immediately dispatch A08/A18/A20 when A07 is ready. Complete package
and scaffold assembly, independent reviews, both PRs and normal post-merge checks.
Stop after Task-04; no Task-05/Task-06 execution is authorized by this record.
