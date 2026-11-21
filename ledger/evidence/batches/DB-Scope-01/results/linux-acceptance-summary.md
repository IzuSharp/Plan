# DB-Scope-01 Linux x64 acceptance results

The final product candidate is `7255040b9501a1898d008c793f9b1777d8394d65`, tree `5f5d74ec7cfa502a4f8d119bb89e2e2776d4b65b`. Its complete [CI44919645468](https://github.com/IzuSharp/NativeWeave/actions/runs/44919645468) and two independent evidence reviews passed. [acceptance.json](../acceptance.json) records the actual delivered identities and closeout state; this result summary does not predict any future merge or CI.

## Product scope

The database product retains PostgreSQL, SQLite, Database Host, sources and pools, sessions, transactions, migrations, parameter binding, strongly typed Fluent queries, static models and DTO mapping, relations and CRUD, streaming, cancellation, errors, disposal, C#–Rust bindings and precompiled Native AOT assets. Rust SeaQuery and SQLx remain the execution engines. Ordinary application business query methods can be called by the application's chosen standard HTTP or gRPC host.

NativeWeave-owned HTTP/gRPC servers, routing/protocol wrappers, MCP, server examples, independent compression/proof engines, HelloWorld, orphan generic generators/analyzers, benchmarks and scaffold products were removed from the current source/default build/test/package/docs chain. Unique database validations from mixed services remain finite direct C# tests. Database runtime/API/ABI implementation and external dependency versions were preserved; necessary regression repairs are disclosed in the review chain.

## Ordinary NuGet consumers

| Provider | JIT | Native AOT | Data and asset checks |
|---|---|---|---|
| PostgreSQL | Passed | Passed | Typed Fluent/DTO results, independent SQL, actual provider package/output/loaded-library hashes |
| SQLite | Passed | Passed | Typed Fluent/DTO results, independent SQL, actual provider package/output/loaded-library hashes |

Consumers live outside the source tree and use ordinary PackageReference with the twelve exact candidate packages. SQLite, PostgreSQL and combined dependency graphs all run. Ordinary model/DTO source edits also pass without native rebuilding. The genuine pinned SDK container has no Rust toolchain before isolation; all 24 refusal guards pass in both ordinary and pristine full consumer flows. Four transferred AOT runs pass in the pinned runtime-only image without dotnet, Cargo, rustc, rustup, clang or cc.

The candidate's only native leaves are `NativeWeave.Database.PostgreSql.Native` and `NativeWeave.Database.Sqlite.Native`; package dependencies, publish directories and actual loaded maps exclude removed Server/gRPC/MCP/demo products. Candidate library SHA256 values are PostgreSQL `47ccb6e5752e74140a104fb3e2bc2558290f180528a0691771b01df2c963e3a7` and SQLite `a003326ce24eff467af1b88f40b03dcacf665fc71710db0ca85b29595471f0e9`.

Four lifecycle/business rows, 32 finite database faults, 14 local immutable publication/recovery/rollback cases and final zero-owner cleanup passed. These candidate publication simulations do not claim public NuGet publication, new-domain signer authentication, performance improvement or long-running load acceptance.

## Retained workspace and regression checks

All 56 ordered database regression gates passed. Rust reported 86 passed tests, zero failed or ignored tests. Full locked .NET restore/build, Rust formatting/Clippy, full .NET formatting and exact API/XML/DocFX/negative checks executed successfully. The full .NET build recorded zero warnings/errors.

| Full two-provider suite | JIT assertions | AOT assertions |
|---|---:|---:|
| Database Host | 482 | 486 |
| Migrations | 205 | 205 |
| Materialization | 996 | 997 |
| Fluent | 1,057 | 1,059 |
| Relations | 1,669 | 1,684 |

Actual PostgreSQL18 and SQLite checks include pool/session admission and cancellation, transaction/savepoint failure and recovery, stream retirement, mapping cleanup, disposal and ownership counters. Independent-process migration contention, kill/replay and idempotency passed in both runtime modes. PostgreSQL conflict-snapshot and COMMIT-acknowledgement-loss oracles remain covered by the external business fixtures.

The successful full formatter emitted its generic workspace-loading warning; Cargo emitted a manifest dependency warning. Both are preserved in the regression review. No concrete omitted required gate was found, and no warning-free-loading claim is made.

## Evidence and review

- [Semantic review](candidate10-final-ci-semantic/final-review.json): unchanged validator/v3 contract, 2,959 predicates, 17 sections and 34 exact source inputs; actual JSON exports and complete artifact identities are adjacent.
- [Workspace/regression review](candidate10-final-ci-regressions/review.json): all 56 raw outer logs rehashed, 668 immutable-source comparisons across 426 paths, 26 byte-identical safe JSON exports.
- [Package/runtime receipt](../receipts/candidate10-ci-packages-and-runtime.json), [workspace/regression receipt](../receipts/candidate10-ci-workspaces-and-regressions.json) and [independent review receipt](../receipts/candidate10-independent-reviews.json) bind actual evidence hashes and the exact source.
- [Authenticated CI/artifact observation](../ci/44919645468/final-ci-observation.json): both GitHub ZIP digest/size checks passed; each reviewer independently rehashed both ZIPs and all 1,046 extracted files.

The evidence ZIP is `739861abfcfa60ca684f8f988a4f678d56a23969d5dd0c6830af200d88aa26c4`; the exact candidate ZIP is `d36cf8fe8cca979aa8ad0a050bfcd89b26081a2c3c2f1ee559125a439237da69`. Archives and binaries are retained as GitHub run artifacts and in the task validation directory, not copied into Git. Selected JSON bytes and their SHA256 inventories are committed here. Missing nested raw logs, previous package archives and standalone transferred binaries are explicitly bounded in the reviews rather than claimed to have been independently rehashed.

Source review, CI execution and independent evidence review remain distinct. Agent reviews are technical reviews and do not impersonate a second GitHub approval account. Failed, cancelled and development/local-only attempts retain their original identities in the handoff and failures directory. Only the accessible Linux execution host was inspected and cleaned; no inaccessible-host claim is made.

Final delivery is governed by the exact PR/head/main receipts in [acceptance.json](../acceptance.json) and the current [handoff](../handoff-linux.md). Performance work remains deferred, and no new ORM feature, hosting wrapper or public package release is included.


## Observed Design and implementation delivery

Design [PR14](https://github.com/IzuSharp/NativeWeave-Design/pull/14) merged as `8298dc4128b745cf1809bad0c3cf02c45eb7f522`; its current and historical main workflows44923513282/44923513318 passed. Product [PR20](https://github.com/IzuSharp/NativeWeave/pull/20) merged as `465cd0f90e6af05ec50eb581156240377cf0825b`; complete [main CI44924918463](https://github.com/IzuSharp/NativeWeave/actions/runs/44924918463) passed. Each merged tree exactly equals the tested/reviewed candidate tree. Main CI metadata is separate from the downloaded PR-candidate artifacts and is not relabeled as an independent second artifact review. Plan's final delivery state remains governed by acceptance.json and the observed postmerge policy.


## Accepted delivered snapshot

Plan [PR24](https://github.com/IzuSharp/Plan/pull/24) delivered the reviewed head `c0068e00d67ee04d79d0d14785eb5aa81075b5d6` as merge `d35bf8e9dd556e7aa11265a3dae7e1f32f778633`, with the identical tree. Its [PR CI44928013016](https://github.com/IzuSharp/Plan/actions/runs/44928013016) and [main CI44928611963](https://github.com/IzuSharp/Plan/actions/runs/44928611963) both passed. All fourteen acceptance claims now bind the observed three-repository delivery snapshot; every current execution phase is complete.

This evidence-only record's own PR and main CI are checked separately and linked from Plan PR24. It does not self-attest a future containing commit. Once those record checks pass, stop DB-Scope-01. Performance optimization remains for a later authorized task.
