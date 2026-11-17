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
| B17 | awaiting_acceptance | server_track | A07, A10, A11, B16, A02 | None |
| B18 | waiting_for_batch_dependency | root (queued) | B15, B17 | None |
| B19 | waiting_for_batch_dependency | root (queued) | B15, B17 | None |
| B20 | ready_queued | server_track (queued) | B17 | None |

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

**B15** — 39 managed component assertions; actual generated JSON dispatch; 278 exact pinned public symbols, XML/reference and seven generator negative consumers pass; actual B17 application acceptance active. Evidence: `ledger/evidence/B15/`.

**B16** — 16 native tests; JIT81 and NativeAOT82; owner/credit counters zero; Two prepared-write and one formatter Bytes-owner focused tests; root reviewed ownership proof. Evidence: `ledger/evidence/B16/review-linux.json`.

**B17** — Actual network JIT and NativeAOT: 69 assertions / 37 dispatches each, HTTP1/HTTP2/TLS/SSE and retirement; Strict Clippy and zero-warning managed builds pass; final ABI/fault/cost receipt active. Evidence: `ledger/evidence/B17/`.

**B20** — B17 implementation integrated; starts after its immutable verification checkpoint. Evidence: `ledger/evidence/B20/`.

Local source and remote transport commits retain separate identities with verified identical Git trees. The four existing Draft PRs are updated in place. Per-task final immutable source/log/hash reviews and package composition remain necessary before marking the whole batch accepted; Windows and other platforms remain outside this run.
