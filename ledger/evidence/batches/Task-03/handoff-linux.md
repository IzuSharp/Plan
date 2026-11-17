# Task-03 Linux x64 handoff

## Scope and recovered baseline

The current user authorizes Task-03 A03, A04, A10, A11, A12, A13 and A22 implementation,
necessary verification/documentation, separate worktrees, commits, remote checkpoints,
normal PR review/merge and the existing automatic preview closeout for Linux x64.
Historical research-only authorization fields remain historical and do not revoke this
specific scope. Other platforms are unexecuted; global acceptance remains false.

Implementation starts from `22b467667bcf44aa8b22e964937446b225e87e61` and Plan from
`7bd04e898344cadc1ae4b331202b4908449f4446`. Read-only Design is exactly
`c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9` as locked by Plan. Remote branch/PR search
found no earlier Task-03 checkpoint. Older local design checkouts were reused; the
product and Plan were restored from their current remote main commits.

A01 is reused from [Task-01](../Task-01/handoff-linux.md); A02, A05 and A09 are reused
from [Task-02](../Task-02/handoff-linux.md). Their accepted component evidence and
completed merge/CI/preview results are not rerun or relabelled. All seven Task-03
start dependencies are satisfied; the graph has no extra acceptance dependency for
these tasks. A10/A11 may use explicitly labelled component conformance fixtures;
actual later host/dependency-closure acceptance stays with its named downstream owner.

## Current task status

| Task | Linux state | Owner | Next step |
| --- | --- | --- | --- |
| A03 | In progress: inputs/environment | Lifetime worker | Implement logical admission and physical leases |
| A04 | Ready, queued within worker limit | Lifetime worker | Owned buffers and asynchronous retained leases |
| A10 | In progress | Bindings worker | Static imports, callback guards and metadata emission |
| A11 | Ready, queued within worker limit | Bindings worker | Exports and final linked inventory checks |
| A12 | In progress | Analyzers worker | Stable diagnostics and compiler-host/consumer tests |
| A13 | In progress | Main executor | Maintainer build/provenance and shared registration |
| A22 | Ready, queued within worker limit | Main executor | Compatibility and immutable closure validation |

No Task-03 component is accepted at this initial checkpoint. Actual test results,
source identities and independent findings will be linked here as they become available.

## Worktrees and integration

ROOT is `/workspace/scratch/58d2a6adf1c3`. Batch worktrees are
`ROOT/.worktree/Task-03-linux/{NativeWeave,Plan}`, both using `task/Task-03-linux`.
Each subtask owns `ROOT/.worktree/Task-03-<ID>-linux/NativeWeave` and
`task/Task-03-<ID>-linux`. The sibling batch Design worktree is pinned and read-only.
Only the main executor changes shared solution, Cargo and build registration files.
The existing Cargo workspace is at repository root; A13 integrates that actual path
instead of creating a conflicting `native/Cargo.toml` workspace.

[Status](status-linux.json) tracks owners, commits, evidence and integration.
The fixed .NET SDK 11.0.100 is recovered; Rust 1.100.0 and native prerequisites are
being restored into `ROOT/task03-toolchain` without changing repository pins.

Implementation PR: not created yet (no implementation checkpoint).

Plan PR: pending initial handoff publication.

## Next step

Complete the seven owned components, their documentation and actual Linux verification.
Integrate and independently review each completed component while other ready work
continues. Publish initial Draft PRs as soon as concrete checkpoints exist, then update
those same PRs. After required checks/review pass, merge normally, confirm exact-merge
CI and the existing automatic preview/consumption, record necessary closeout and stop.
Do not start another task package or extend the release/platform scope.
