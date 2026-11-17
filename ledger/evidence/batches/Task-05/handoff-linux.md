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
| B04 | awaiting_acceptance | database_host | B01, B07, A03, A04, A05, A07, A10, A11, A02 | B02, B03, B05, B06 |
| B08 | in_progress | database_host | B01, B05 | B02, B03, B04 |
| B10 | in_progress | root | B09 | B12, B13 |
| B11 | awaiting_acceptance | query_track | B09, B07 | B02, B03, B04 |
| B12 | awaiting_acceptance | query_track | B07, B09 | B06, B04, B02, B03 |
| B13 | in_progress | query_track | B09, B11 | B04, B06, B12 |
| B14 | ready_queued | database_host (queued) | B05, B11, B12 | B02, B03, B04, B06 |

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

**B04** — Actual SQLite/PostgreSQL18 Host JIT132 and NativeAOT132 assertions; all six native owner counters zero; 112 exact pinned public signatures with XML/reference checked; final expanded/package evidence active. Evidence: `ledger/evidence/B04/`.

**B08** — Worktree created at d283584; independent migration implementation started. Evidence: `ledger/evidence/B08/`.

**B10** — Seven generated/manual metadata and typed DTO parity assertions pass; compiler diagnostic/incremental gate active. Evidence: `ledger/evidence/B10/`.

**B11** — 11 native tests against real SQLite/PostgreSQL18; direct SQL and result oracles pass; Independent imported-plan budget and nested recursive-reference findings fixed; managed actual Host receipt active. Evidence: `ledger/evidence/B11/`.

**B12** — Real SQLite/PostgreSQL18 JIT231 and NativeAOT232 assertions; 18 cases per provider and all six native counters zero; Generated-path parity and final package/source evidence active. Evidence: `ledger/evidence/B12/`.

**B13** — Isolated Fluent implementation worktree based on ce38ff4. Evidence: `ledger/evidence/B13/`.

**B14** — B11/B12 implementation inputs are integrated; queued after B08 against available agent slot. Evidence: `ledger/evidence/B14/`.

Local source and remote transport commits retain separate identities with verified identical Git trees. The four existing Draft PRs are updated in place. Per-task final immutable source/log/hash reviews and package composition remain necessary before marking the whole batch accepted; Windows and other platforms remain outside this run.
