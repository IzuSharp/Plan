# Task-05 Linux x64 handoff

## Scope and current state

The user explicitly authorized implementation, required tests, documentation, branches,
commits, pushes, PRs, normal checked merges and existing postmerge preview closeout for
Task-05 on Linux x64. This platform record supplements the historical research graph;
it does not rewrite accepted research or claim global product acceptance.

All external Linux dependencies are reused from the accepted
[Task-01](../Task-01/handoff-linux.md), [Task-02](../Task-02/handoff-linux.md),
[Task-03](../Task-03/handoff-linux.md) and [Task-04](../Task-04/handoff-linux.md)
records. No historical component acceptance is rerun. No Task-05 implementation or
PR was present at recovery. Task-05 and Task-06 have no mutual dependency.

| Task | State | Owner | Start dependencies | Acceptance dependencies |
| --- | --- | --- | --- | --- |
| B04 | in_progress | database_host | B01, B07, A03, A04, A05, A07, A10, A11, A02 | B02, B03, B05, B06 |
| B08 | ready_queued | root (queued) | B01, B05 | B02, B03, B04 |
| B10 | ready_queued | root (queued) | B09 | B12, B13 |
| B11 | in_progress | query_track | B09, B07 | B02, B03, B04 |
| B12 | in_progress | query_track | B07, B09 | B06, B04, B02, B03 |
| B13 | waiting_for_batch_dependency | root (queued) | B09, B11 | B04, B06, B12 |
| B14 | waiting_for_batch_dependency | root (queued) | B05, B11, B12 | B02, B03, B04, B06 |

## Exact baseline and recovery

- Implementation: `aa16521d609c0749d7c199f70eedad833b0d24c8`; verified remote main.
- Plan: `43b98b17b17ed291e42c821ee162e138eb8987df`; verified remote main.
- Read-only Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
- Toolchains: .NET SDK 11.0.100, C# 15, Rust 1.100.0.
- Batch branches: `task/Task-05-linux` in NativeWeave and Plan.
- Batch worktrees: `ROOT/.worktree/Task-05-linux/NativeWeave` and `ROOT/.worktree/Task-05-linux/Plan`.
- Per-task branches/worktrees and integrated/pending commits: [status-linux.json](status-linux.json).
- Implementation PR: https://github.com/IzuSharp/NativeWeave/pull/17 (Draft).
- Plan PR: https://github.com/IzuSharp/Plan/pull/20 (Draft).

## Verification and next action

Recovery established exact repository identities and dependency records; it is not new
product execution evidence. Implement the ready assigned tasks in isolated worktrees,
queue other ready tasks against available agent slots, and compose shared manifests
serially. Preserve every component checkpoint and actual failure/result before final
acceptance. Final PR checks, merge CI and existing preview publication/consumption are
not yet run for this batch. Windows and other platforms are outside this run.

## Integrated checkpoint

B04 native runtime/source/session/operation/query composition and the typed C# facade are integrated. Native and managed builds pass; actual two-provider lifecycle and JIT/AOT acceptance remain active. B11 advanced SeaQuery tests pass all nine groups with real SQLite and locally built PostgreSQL18.0, with no skipped provider row. Its canonical C# ABI oracle driver compiles and publishes to Linux NativeAOT; execution awaits the corresponding Host binary and is not yet accepted. B12 is active in its own worktree, reusing B01 static row decoding and B06 stream cleanup. B08 and B10 remain ready in the concurrency queue; B13/B14 start at their actual component dependency checkpoints.

The PostgreSQL18.0 source archive was verified against its official SHA256 (`0d5b903b1e5fe361bca7aa9507519933773eb34266b1357c4e7780fdee6d6078`) and built locally. TCP loopback is available; Unix-domain socket creation is restricted, so fixtures disable Unix sockets explicitly. No repository toolchain or NuGet audit policy was weakened. Local source and remote transport commit identities are retained separately; transport uploads verify exact tree equality.
