# Task-06 Linux x64 handoff

## Scope and current state

The user explicitly authorized implementation, required tests, documentation, branches,
commits, pushes, PRs, normal checked merges and existing postmerge preview closeout for
Task-06 on Linux x64. This platform record supplements the historical research graph;
it does not rewrite accepted research or claim global product acceptance.

All external Linux dependencies are reused from the accepted
[Task-01](../Task-01/handoff-linux.md), [Task-02](../Task-02/handoff-linux.md),
[Task-03](../Task-03/handoff-linux.md) and [Task-04](../Task-04/handoff-linux.md)
records. No historical component acceptance is rerun. No Task-06 implementation or
PR was present at recovery. Task-05 and Task-06 have no mutual dependency.

| Task | State | Owner | Start dependencies | Acceptance dependencies |
| --- | --- | --- | --- | --- |
| B15 | in_progress | root | A02, A07, A10 | B17 |
| B16 | accepted_component_linux | server_track | A07 | None |
| B17 | in_progress | server_track | A07, A10, A11, B16, A02 | None |
| B18 | waiting_for_batch_dependency | root (queued) | B15, B17 | None |
| B19 | waiting_for_batch_dependency | root (queued) | B15, B17 | None |
| B20 | waiting_for_batch_dependency | root (queued) | B17 | None |

## Exact baseline and recovery

- Implementation: `aa16521d609c0749d7c199f70eedad833b0d24c8`; verified remote main.
- Plan: `43b98b17b17ed291e42c821ee162e138eb8987df`; verified remote main.
- Read-only Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
- Toolchains: .NET SDK 11.0.100, C# 15, Rust 1.100.0.
- Batch branches: `task/Task-06-linux` in NativeWeave and Plan.
- Batch worktrees: `ROOT/.worktree/Task-06-linux/NativeWeave` and `ROOT/.worktree/Task-06-linux/Plan`.
- Per-task branches/worktrees and integrated/pending commits: [status-linux.json](status-linux.json).
- Implementation PR: https://github.com/IzuSharp/NativeWeave/pull/16 (Draft).
- Plan PR: https://github.com/IzuSharp/Plan/pull/21 (Draft).

## Verification and next action

Recovery established exact repository identities and dependency records; it is not new
product execution evidence. Implement the ready assigned tasks in isolated worktrees,
queue other ready tasks against available agent slots, and compose shared manifests
serially. Preserve every component checkpoint and actual failure/result before final
acceptance. Final PR checks, merge CI and existing preview publication/consumption are
not yet run for this batch. Windows and other platforms are outside this run.

## Integrated checkpoint

B16 Linux component acceptance is recorded in [its independent review](../../B16/review-linux.json): 16 native tests, 81 JIT and 82 actual NativeAOT assertions, five public XML/reference symbols, and zero final operation/buffer/credit owners. The additive prepared-write integration preserves create-time input copying and unstarted rollback; its two targeted tests are retained without repeating unrelated historical acceptance.

B15 is implemented through application lifecycle/typed routing/results and optional Generic Host integration; 35 managed component assertions pass. Generated registration, complete API/reference checks and real B17 acceptance remain in progress. B17 is active on its own worktree, implementing the exact pinned ABI and native TCP HTTP/TLS Host. B18/B19 wait for B15+B17; B20 waits for B17. No database completion is required.

Local source commits are integrated into the batch branch; remote GitData transport commits preserve exact trees and retain distinct identities. Native source and evidence uploads continue on the existing PRs.
