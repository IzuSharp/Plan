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
- Implementation PR: https://github.com/IzuSharp/NativeWeave/pull/17 (merged as `275aa5e0f9eba70c637d1a32fb399108635137ce`).
- Plan PR: https://github.com/IzuSharp/Plan/pull/20 (this final delivery record; normal checked merge is the remaining record-delivery step).

## Accepted Linux components

B04 remains accepted from its existing independent source and package review:484 JIT /486 NativeAOT assertions,175/176 separately observed managed retirements, six native counters zero,112 exact public signatures and11 exact package consumers.

B08 is accepted:205 JIT /207 NativeAOT assertions,62/63 managed retirements, both native providers and all seven native tests, actual independent-process contention/SIGKILL/replay/idempotency,155 exact assembly signatures including93 owned signatures, rich primary-error plus failed-cleanup preservation. Independent review also fixed and focused-tested the separate PostgreSQL connect deadline and aggregate migration UTF8 encoding preflight. The original provider/process matrix is retained without claiming it ran on the later narrow fixes.

B11 is accepted:12 native tests and52 actual cases for each runtime;180 JIT /181 NativeAOT assertions,254 native retirement receipts and234 buffer releases in each mode. Direct SQL/result oracles cover SQLite and PostgreSQL18.

B12 is accepted:996 JIT /997 NativeAOT assertions,342 managed retirements per mode,22 cases per provider, six native counters zero and independent exact NuGet consumers in both modes with Rust invocation traps unused.

B13 is accepted:1062 JIT /1063 NativeAOT assertions,420 managed retirements per mode,219 exact API/XML/reference symbols,13 negative compile fixtures and independent exact NuGet consumers in both modes. Costs count all15 inspected direct ABI calls; no performance advantage is inferred.

B10 is accepted after B12/B13:32 formal commands, eight generated/manual x original/edited x JIT/NativeAOT execution rows, two entities and ordinary mapped DTO changes with unchanged native SHA256.13 API signatures,15 negative diagnostic fixtures, seven parity assertions and static incremental generation passed. Original JIT artifact hashes were recorded before edited builds; each original AOT binary remains hash-verified.

B14 is accepted:1673 JIT /1678 NativeAOT assertions,570/572 separately observed managed retirements and all six native counters zero on SQLite and PostgreSQL18.81 exact API symbols, six compile-negative fixtures and the independent10-package consumer passed in both runtimes/providers without Rust. Independent review found and corrected the exact relation/projection cursor retention gap; a separately identified actual SQLite ABI regression passed Debug/Release, both provider builds and SQLite-only strict Clippy. The baseline matrix is retained under its original source and asset identities.

Each accepted component has an independent review and SHA-indexed receipts under its existing `ledger/evidence/Bxx/` directory. Those are Linux component results; the completed implementation integration and existing release closeout are recorded below. No all-platform acceptance is claimed.

## Final Linux implementation delivery and release

All seven Linux components are accepted and integrated. Implementation PR17 was normally merged with all applicable checks passed; no protection, required check or approval identity was bypassed. The final local source checkpoint `67605f0afd28d058597645874fe6cab9c8fba411` and remote transport checkpoint `28dfa455d42e00f9fa5a332adae695e927549067` have the identical tree `a04a5fb6b37b6394c70ab1b7553fc56b866e1ea0`. Main merge: `275aa5e0f9eba70c637d1a32fb399108635137ce`.

- [Final PR CI](https://github.com/IzuSharp/NativeWeave/actions/runs/44072697209): passed, including full formatting, native workspace checks, managed build, packaging, NativeAOT, pristine no-Rust container consumption, existing package closure/runtime transfer and security.
- [Exact merge CI](https://github.com/IzuSharp/NativeWeave/actions/runs/44074361624): passed on the merge SHA.
- [Existing automatic release](https://github.com/IzuSharp/NativeWeave/actions/runs/44074361782): passed on the same SHA. The normal pipeline allocated `NativeWeave.HelloWorld` version `0.1.0-preview.9.1`, validated the retained candidate, published it, verified its repository signature and unchanged unsigned payload, and executed the downloaded registry package in JIT and NativeAOT with an isolated NuGet cache and unused Rust invocation traps.

The release still covers the existing HelloWorld preview only; it does not newly publish the Database/ORM components. Their separate exact NuGet consumer acceptance is in the component evidence above. No platform or release scope was added.

The publication receipt and original consumer logs are retained in [postmerge-release](postmerge-release/). The downloaded GitHub artifact ZIP matched SHA256 `39d9705a15c2f0536b4776c85a409cc3a080734d396b2a9ca7a30c50488a82f7`; the signed registry package SHA256 is `21833aa1a16025d54e3eec00215a2d40162114de9a2540d41c0618c0c5b87607`. The registry consumer explicitly records `pristineMachine:false`; the separate required CI container check supplies its own pristine-consumption evidence.

The shared solution and both Database Host provider profiles are included in the existing build. PostgreSQL18 is a digest-pinned local test service in the Linux workflow. Local full solution formatting was blocked by the environment's denied Roslyn build-host Unix socket; the unchanged complete GitHub formatter passed and supplies the actual gate result.

## Final Plan record and recovery

At creation of this final record, only the normal checked merge of [Plan PR20](https://github.com/IzuSharp/Plan/pull/20) and observation of its merge CI remain. If the linked PR is merged and that CI is green, Task-05 Linux delivery is complete: do not rerun component acceptance or append another commit merely to repeat the linked final check result. Task-06 proceeds independently. Windows and other platforms are outside this run, and no subsequent task package is authorized by this completion.

Local execution commits and GitData transport commits retain separate identities with verified equal Git trees. Use this table and the per-task reviews for recovery.
