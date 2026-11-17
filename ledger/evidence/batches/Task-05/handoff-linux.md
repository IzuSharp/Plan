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
| B04 | accepted_component_linux | database_host | B01, B07, A03, A04, A05, A07, A10, A11, A02 | B02, B03, B05, B06 |
| B08 | accepted_component_linux | database_host | B01, B05 | B02, B03, B04 |
| B10 | accepted_component_linux | root | B09 | B12, B13 |
| B11 | accepted_component_linux | query_track | B09, B07 | B02, B03, B04 |
| B12 | accepted_component_linux | query_track | B07, B09 | B06, B04, B02, B03 |
| B13 | accepted_component_linux | query_track | B09, B11 | B04, B06, B12 |
| B14 | accepted_component_linux | database_host | B05, B11, B12 | B02, B03, B04, B06 |

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

## Accepted Linux components

B04 remains accepted from its existing independent source and package review:484 JIT /486 NativeAOT assertions,175/176 separately observed managed retirements, six native counters zero,112 exact public signatures and11 exact package consumers.

B08 is accepted:205 JIT /207 NativeAOT assertions,62/63 managed retirements, both native providers and all seven native tests, actual independent-process contention/SIGKILL/replay/idempotency,155 exact assembly signatures including93 owned signatures, rich primary-error plus failed-cleanup preservation. Independent review also fixed and focused-tested the separate PostgreSQL connect deadline and aggregate migration UTF8 encoding preflight. The original provider/process matrix is retained without claiming it ran on the later narrow fixes.

B11 is accepted:12 native tests and52 actual cases for each runtime;180 JIT /181 NativeAOT assertions,254 native retirement receipts and234 buffer releases in each mode. Direct SQL/result oracles cover SQLite and PostgreSQL18.

B12 is accepted:996 JIT /997 NativeAOT assertions,342 managed retirements per mode,22 cases per provider, six native counters zero and independent exact NuGet consumers in both modes with Rust invocation traps unused.

B13 is accepted:1062 JIT /1063 NativeAOT assertions,420 managed retirements per mode,219 exact API/XML/reference symbols,13 negative compile fixtures and independent exact NuGet consumers in both modes. Costs count all15 inspected direct ABI calls; no performance advantage is inferred.

B10 is accepted after B12/B13:32 formal commands, eight generated/manual x original/edited x JIT/NativeAOT execution rows, two entities and ordinary mapped DTO changes with unchanged native SHA256.13 API signatures,15 negative diagnostic fixtures, seven parity assertions and static incremental generation passed. Original JIT artifact hashes were recorded before edited builds; each original AOT binary remains hash-verified.

B14 is accepted:1673 JIT /1678 NativeAOT assertions,570/572 separately observed managed retirements and all six native counters zero on SQLite and PostgreSQL18.81 exact API symbols, six compile-negative fixtures and the independent10-package consumer passed in both runtimes/providers without Rust. Independent review found and corrected the exact relation/projection cursor retention gap; a separately identified actual SQLite ABI regression passed Debug/Release, both provider builds and SQLite-only strict Clippy. The baseline matrix is retained under its original source and asset identities.

Each accepted component has an independent review and SHA-indexed receipts under its existing `ledger/evidence/Bxx/` directory. Those are Linux component results, not all-platform acceptance or completed batch delivery.

## Active work and next action

All seven Linux components are accepted and integrated. The batch remains open for final composition, PR checks, checked merges and the existing postmerge publication/consumption workflow.

The shared solution builds with zero warnings/errors. Its two Database Host profiles are now staged by the existing maintainer build, and the existing Linux CI job supplies a pinned local PostgreSQL18 service for the actual provider tests. The local full solution formatter is blocked by the execution environment's denied Unix-domain socket used by Roslyn's build host; this is not recorded as a successful formatter run. The unchanged required GitHub CI formatter remains the final gate. No check or protection is bypassed.

Next: finish the batch composition gate, update the existing implementation/Plan PRs, complete normal checked merges, then verify merge CI and the existing preview publication/consumption workflow. Windows and other platforms are outside this run. Task-06 proceeds independently.

Local source and remote transport commits retain separate identities with verified identical Git trees. Use this table and per-task reviews for recovery; do not repeat accepted historical component matrices.
