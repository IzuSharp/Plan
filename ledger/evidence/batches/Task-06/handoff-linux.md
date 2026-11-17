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
| B15 | accepted_component_linux | root | A02, A07, A10 | B17 |
| B16 | accepted_component_linux | server_track | A07 | None |
| B17 | accepted_component_linux | server_track | A07, A10, A11, B16, A02 | None |
| B18 | in_progress | root managed application; server_track native Tonic helper | B15, B17 | None |
| B19 | in_progress | query_track | B15, B17 | None |
| B20 | accepted_component_linux | server_track | B17 | None |

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

B15 and B17 are independently accepted Linux components. B15 passed 85 actual assertions in each of JIT and NativeAOT, 278 exact API/XML/reference checks, and independent NuGet consumers with transitive generation, optional Hosting, HTTP/1 and HTTP/2. All Rust invocation traps remained unused and an ordinary DTO edit preserved the native asset. B17 passed 19 formal stages, eight native regressions, 85 assertions and 43 dispatches in each managed mode, and 48 exact exports / eight records / 103 field offsets. Component receipts and independent reviews are in `ledger/evidence/B15/` and `ledger/evidence/B17/`.

B16 remains accepted. Its additive formatter-owner and payload-free flush checks are preserved beside B17's final logs. B20 is independently accepted:33 formal stages,110 actual assertions in each runtime, five native unit tests and one actual Host test,48 exact exports and10 public context symbols, four matched cost modes per runtime and independent NuGet JIT/AOT consumers without Rust. Its immutable source/log/artifact hashes were independently checked; see `ledger/evidence/B20/review-linux.json`. B18/B19 remain active and use the same request scope and native runtime.

Remote Build CI identified stale exact Cargo input hashes in the existing HelloWorld build profile after workspace composition; those hashes were refreshed without weakening its input gate. Exact public design digests and a documented recovery identifier were classified in secret scanning; local pinned Gitleaks full-history scan passed. New remote checkpoints and final checks remain required.

Next: finish B18/B19, combine module verification, finalize the existing PRs, and complete normal checked merges and the existing postmerge preview/consumer workflow. No Windows or other-platform acceptance is claimed. Local execution commits and GitData transport commits retain separate identities with identical verified Git trees.
