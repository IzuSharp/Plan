# Task-02 Linux x64 handoff

## Authorized scope and baseline

The current user instruction authorizes implementation, scoped verification, commits,
publication, normal PR review/merge and existing post-merge CI/preview closeout for
**A02, A05, A09, B05, B07, B09, B02, B03 and B06 on Linux x64**. It supersedes
historical research-only authorization text for this batch. It does not authorize
the next batch, other platform execution, a new release scope or protection bypass.

Existing A01/B01 Linux completion is reused from [Task-01](../Task-01/handoff-linux.md).
NativeWeave starts at `10915d26b13a5ffd0b1abbe06d5934dfb0f2d771`; Plan starts at
`5536d6d02cb7b99cd2100d6e73d701d676547ce2`. The read-only Design pin is
`c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. There were no existing Task-02 worktrees,
branches, PRs or evidence at recovery. Accepted research graphs and bindings remain
historical inputs; this batch record is the platform-scoped execution overlay.

## Current task state

| Task | State | Owner | Start dependencies | Additional acceptance dependencies |
| --- | --- | --- | --- | --- |
| A02 | Implementing | negotiation worker | A01 complete | None |
| A05 | Implementing | main executor | A01 complete | None |
| A09 | Ready, queued | main executor | A01 complete | None |
| B05 | Implementing | transactions worker | B01 complete | B02, B03 |
| B07 | Implementing | codecs worker | B01 complete | None |
| B09 | Ready, queued | main executor | B01 complete | None |
| B02 | Waiting for B07 | Unassigned | B01 complete; B07 pending | None |
| B03 | Waiting for B07 | Unassigned | B01 complete; B07 pending | None |
| B06 | Waiting for B07 | Unassigned | B01 complete; B07 pending | B02, B03 |

Three subordinate workers can run concurrently. Newly available slots take the
next ready task. B07 has priority because it unlocks B02/B03/B06. B05 can proceed
independently but final acceptance remains pending actual providers. Complete B04
Host composition is downstream, not an extra prerequisite or a completion claim.

## Worktrees and recovery

ROOT is `/workspace/scratch/0898a75257bc`. Batch worktrees are
`ROOT/.worktree/Task-02-linux/{NativeWeave,Plan}` on `task/Task-02-linux`; the sibling
`NativeWeave-Design` is detached at the locked commit. Initial task worktrees are
`ROOT/.worktree/Task-02-<ID>-linux/NativeWeave` with branches
`task/Task-02-<ID>-linux` for A02/A05/A09/B05/B07/B09. Provider/streaming worktrees
will start from the integrated B07 dependency. Root integrates shared solution,
Cargo and project-reference changes serially and records component commits here.

No Task-02 implementation or validation has yet been accepted. Retained Rust1.100.0
and .NET11 SDK packages are available. The previous .NET SDK path is absent;
restoring SDK11.0.100, PostgreSQL18.0 and the pinned SQLx dependency closure is in
progress. No Task-01 acceptance is rerun to repair that environment.

## PRs and next step

Implementation PR: not created yet; first task-owned implementation checkpoint pending.

Plan PR: initial handoff publication pending.

Next: finish current implementations and environment recovery, publish each
handoffable checkpoint, then start newly unlocked tasks. Record actual run logs,
source identities and independent review before any completion claim. Follow both
PRs through normal merge, exact merge CI and the existing HelloWorld-only automatic
preview process; do not publish new module packages or start Task-03.
