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
| B18 | accepted_component_linux | root native/composition review; server_track managed review; database_host package proof | B15, B17 | None |
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

B16 remains accepted. Its additive formatter-owner and payload-free flush checks are preserved beside B17's final logs. B20 is independently accepted:33 formal stages,110 actual assertions in each runtime, five native unit tests and one actual Host test,48 exact exports and10 public context symbols, four matched cost modes per runtime and independent NuGet JIT/AOT consumers without Rust. Its immutable source/log/artifact hashes were independently checked; see `ledger/evidence/B20/review-linux.json`. B18 is now accepted; B19 remains active on the same request scope and native runtime.

Remote Build CI identified stale exact Cargo input hashes in the existing HelloWorld build profile after workspace composition; those hashes were refreshed without weakening its input gate. Exact public design digests and a documented recovery identifier were classified in secret scanning; local pinned Gitleaks full-history scan passed. New remote checkpoints and final checks remain required.

B18 is independently accepted:17 formal commands;308 JIT /309 NativeAOT assertions with332 separately observed A07 retirements in each mode;71 exact API/XML/reference declarations and five compile-negative fixtures;48 exports, eight records and103 offsets. The independent25-command NuGet proof executes two static Protobuf services and all four cardinalities over clear HTTP2/TLS, then changes ordinary proto/DTO/Handler code and executes JIT/AOT with unchanged native bytes and no Rust invocation. Separate native/component/package source identities and the original package provenance correction are preserved under `ledger/evidence/B18/`.

B19's final04 exposed a managed close-tail race. The shared bounded join correction is integrated as `a91ebf4`; a deterministic HTTP1/HTTP2 regression fails on the previous implementation and passes with the correction. Independent review also reproduced a missing inline-value DTO width term; B19 remains unaccepted until its pre-SDK allocation admission is corrected and verified. The preliminary combined Server asset is not final acceptance. The immutable independent finding and actual public-Host reproducers are preserved at `ledger/evidence/B19/independent-review-open/`; the close-tail negative/fixed logs are at `ledger/evidence/B19/managed-close-tail/`. B19 implementation, static layout metadata and independent review proceed in isolated worktrees. The accepted B18 managed review separately identifies its author/reviewer roles at `ledger/evidence/B18/linux-final/independent-managed-review.md`.

The Task-05 implementation was normally merged into main as `275aa5e0f9eba70c637d1a32fb399108635137ce`. Task-06 integrates that main with local merge `3ce32dd`; all seven shared resolutions retain both modules. Full static Server binding generation was refreshed as `e265fa6` after formatting changed native inventory provenance. This integration is not another prerequisite or rerun of Task-05 acceptance.

Next: finish B19, combine module verification, finalize the existing PRs, and complete normal checked merges and the existing postmerge preview/consumer workflow. No Windows or other-platform acceptance is claimed. Local execution commits and GitData transport commits retain separate identities with identical verified Git trees.
