# Task-06 Linux x64 handoff

## Scope and current state

All six Linux x64 components are accepted and integrated. Final normal PR checks, merges, exact merge CI and the existing automatic preview publication/consumption remain the delivery steps. No other-platform acceptance is claimed.

The user explicitly authorized implementation, tests, documentation, worktrees, commits, pushes, PRs, normal checked merges and postmerge closeout for Task-05 and Task-06. Historical research-only statuses do not revoke that authorization. Design remains read-only at `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`; toolchains are .NET SDK11.0.100, C#15 and Rust1.100.0. External A02/A07/A10/A11 Linux dependency evidence is reused.

Task-05 and Task-06 were developed in parallel without adding a database prerequisite to Server. Task-05 is complete: implementation PR17 merged as `275aa5e0f9eba70c637d1a32fb399108635137ce`, Plan PR20 as `667ed2720eda44c31da787d1126961c79a76f90e`; exact merge CI and existing preview `0.1.0-preview.9.1` publication/registry JIT+AOT consumption passed. Their main branches are integrated into this batch.

| Task | Linux state | Owner/review | Start dependencies | Acceptance dependencies | Evidence |
| --- | --- | --- | --- | --- | --- |
| B15 | accepted_component_linux | root | A02, A07, A10 | B17, satisfied | [B15](../../B15/review-linux.json) |
| B16 | accepted_component_linux | server_track | A07 | None | [B16](../../B16/review-linux.json) |
| B17 | accepted_component_linux | server_track | A02, A07, A10, A11, B16 | None | [B17](../../B17/review-linux.json) |
| B18 | accepted_component_linux | root/native composition; server_track/managed review; database_host/package proof | B15, B17 | None | [B18](../../B18/review-linux.json) |
| B19 | accepted_component_linux | query_track/product; database_host/compiler; server_track/independent review; root/composition | B15, B17 | None | [B19](../../B19/review-linux.json) |
| B20 | accepted_component_linux | server_track | B17 | None | [B20](../../B20/review-linux.json) |

## Branches, worktrees and recovery

- Both batch branches: `task/Task-06-linux`.
- Worktrees: `ROOT/.worktree/Task-06-linux/NativeWeave` and `ROOT/.worktree/Task-06-linux/Plan`.
- Per-task branches/worktrees, owners and integrated commits: [status-linux.json](status-linux.json).
- Implementation PR: https://github.com/IzuSharp/NativeWeave/pull/16.
- Plan PR: https://github.com/IzuSharp/Plan/pull/21.
- Implementation local head: `24e760e0083a9a05828ff56c8a3ff88cd43407f3`.
- Remote transport head: `849ec7b6c52e98108991dfd78098031393b2a047`.
- Verified equal Git tree: `245de26bad38ab62547d422eeb83267e7520ca92`.

All owned component changes are integrated; no pending agent implementation or acceptance work remains. Local execution and GitData transport commits retain distinct identities with explicit equal-tree mappings. Recover from these existing remote batch branches and PRs, not a new implementation from main.

## Accepted verification

| Component | Actual Linux evidence |
| --- | --- |
| B15 |85 assertions each JIT/AOT;278 exact API/XML/reference symbols; independent NuGet with transitive generation, optional Hosting, HTTP1/HTTP2 and ordinary DTO edits without Rust |
| B16 |16 native tests;81 JIT/82 AOT assertions; zero owners/credits; focused formatter-owner and payload-free flush checks |
| B17 |19 formal stages; eight native tests;85 assertions/43 dispatches each runtime;48 exports, eight records,103 offsets |
| B18 |17 formal commands;308 JIT/309 AOT assertions;332 managed retirements each;71 API symbols/five compile-negative cases;25-command independent five-package proof, two Protobuf services, four cardinalities over HTTP2/TLS and managed-only edits with unchanged native |
| B19 |21 formal commands;291 JIT/291 AOT assertions;180 managed retirements each;65 API symbols/five static compile fixtures; nine native preparse rejections with SDK=0/Handler=0 plus a positive case;22-command independent five-package proof |
| B20 |33 formal stages;110 assertions each runtime; five native unit tests/one actual Host test;48 exports/10 context symbols; four matched cost modes each runtime; independent NuGet JIT/AOT without Rust |

All API/XML, guide/sample, ownership and error/lifecycle requirements belong to the component evidence linked above. Matched cost results are retained without an unconditional performance advantage claim. Previously accepted component/package matrices are reused, not rerun as new evidence.

B19's compiler passes65 assertions and80 in each runtime, covering private/base/generic/external metadata and actual public registration. Its independent consumer blocks repository imports and traps Rust. A private-only edit in an external DTO project preserves reference DLL bytes, regenerates the proof and changes node admission4640 to8736, then passes actual JIT/AOT HTTP1+HTTP2 using unchanged native bytes. Root rehashed137 formal source inputs,190 native build inputs,16 additional packaging inputs,24 compiler source files and101 compiler artifacts, plus every command log and package: zero mismatches.

The [sealed independent B19 review](../../B19/linux-final/independent/final-review.md) closes complete CLR inline-storage under-reservation and private-name startup expansion. The original long-name graph now rejects before expansion with8,016 allocated bytes in JIT and30,056 in AOT, and a189-character bounded diagnostic. The correction preserves exact registered schema/ABI semantics, pre-admits field/identity metadata and output boxing, regenerates private-field proofs without Rust, and observes actual retirement. The managed close-tail fix retains the original total deadline. Original failed and superseded evidence remains separate.

## Composition and integration corrections

Selected final protocol rows use native SHA256 `f446c1263e67a7f9a38b3be3e3fdf22f48b0ac2dd15cd46bd4cecea1e6331b21` (8,162,736 bytes,48 exports). The original composed build is source `7ce4f482a1d9935cddfdd0026b9120e6c72350f5`. A fresh full Server build at `874001186635d1f58ecc2d1ad2aae736b9a9421d` reproduced identical bytes; its only native-input difference is the test isolation patch below.

- [Host/diagnostics/gRPC composition](composition-stage/review-scope.json): B17 JIT85/43 dispatches, B20 JIT110, B18 JIT308/AOT308. Formal B18 AOT309 includes one CLI assertion not requested by this runner; the runner independently checks dynamic=False.
- [Final MCP composition](composition-mcp-final/review-scope.json):291 JIT/291 AOT and180 retirements each;405 source hashes and all immutable log/executable inputs verified. Later commits add only a regression script and proof documentation.
- The shared solution, Cargo workspace and static binding inventories were integrated serially. Full125-project locked restore passed after separate ordinary and Linux AOT compiler-witness lock graphs; the original failure is retained.
- [Counter test isolation](integration-counter-fix/review.json): remote CI exposed independently scheduled SQLite/PostgreSQL cases sharing process-global counters. Ten test-only lines isolate five cases while retaining within-case contention and every cleanup assertion. All eight actual provider tests pass with test-threads=8. Independent review confirms no production change, skipped assertion or counter reset.

The compiler-only B19 witness's earlier native asset is explicitly a build input; actual final product/package rows use the composed binary above. Managed/native/package source and asset identities remain separate and explicit.

## Delivery checks and next action

Final implementation PR CI is running at https://github.com/IzuSharp/NativeWeave/actions/runs/44086853306 on remote head `849ec7b6c52e98108991dfd78098031393b2a047`. Complete existing required checks and normal merges without bypassing protection. Confirm exact merge CI and the normal automatic preview publication, repository signature and downloaded registry package JIT/AOT consumption.

The existing public release scope remains HelloWorld only; this task does not newly publish Server/Database packages or add platforms/CI matrices. Then finalize the Plan record, normally merge PR21 and confirm its merge CI. No next task package or unrelated acceptance rerun is authorized by completion.
