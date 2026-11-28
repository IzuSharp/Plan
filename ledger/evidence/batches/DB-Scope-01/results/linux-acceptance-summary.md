# DB-Scope-01 — final Linux x64 result

The accepted candidate was `7255040b9501a1898d008c793f9b1777d8394d65`.
All fourteen scoped acceptance claims and seven phases completed. Product
[PR20](https://github.com/IzuSharp/Korda/pull/20), Design
[PR14](https://github.com/IzuSharp/Korda-Design/pull/14) and Plan
[PR24](https://github.com/IzuSharp/Plan/pull/24) merged with successful observed
PR/main CI. This is the historical Rust-stage database-only result; the later
C++ migration has its own result.

## Product scope

The database product retains PostgreSQL, SQLite, Database Host, sources and pools, sessions, transactions, migrations, parameter binding, strongly typed Fluent queries, static models and DTO mapping, relations and CRUD, streaming, cancellation, errors, disposal, C#–Rust bindings and precompiled Native AOT assets. Rust SeaQuery and SQLx remain the execution engines. Ordinary application business query methods can be called by the application's chosen standard HTTP or gRPC host.

NativeWeave-owned HTTP/gRPC servers, routing/protocol wrappers, MCP, server examples, independent compression/proof engines, HelloWorld, orphan generic generators/analyzers, benchmarks and scaffold products were removed from the current source/default build/test/package/docs chain. Unique database validations from mixed services remain finite direct C# tests. Database runtime/API/ABI implementation and external dependency versions were preserved; necessary regression repairs are disclosed in the review chain.

## Ordinary NuGet consumers

| Provider | JIT | Native AOT | Data and asset checks |
|---|---|---|---|
| PostgreSQL | Passed | Passed | Typed Fluent/DTO results, independent SQL, actual provider package/output/loaded-library hashes |
| SQLite | Passed | Passed | Typed Fluent/DTO results, independent SQL, actual provider package/output/loaded-library hashes |

Consumers live outside the source tree and use ordinary PackageReference with the twelve exact candidate packages. SQLite, PostgreSQL and combined dependency graphs all run. Ordinary model/DTO source edits also pass without native rebuilding. The genuine pinned SDK container has no Rust toolchain before isolation; all 24 refusal guards pass in both ordinary and pristine full consumer flows. Four transferred AOT runs pass in the pinned runtime-only image without dotnet, Cargo, rustc, rustup, clang or cc.

The candidate's only native leaves are `NativeWeave.Database.PostgreSql.Native` and `NativeWeave.Database.Sqlite.Native`; package dependencies, publish directories and actual loaded maps exclude removed Server/gRPC/MCP/demo products.
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


## Limitations

The public result does not claim performance improvement, long-running load,
new-platform acceptance or public NuGet publication. Source review, execution
and independent review retain their distinct meanings. Raw command output,
package copies and receipt inventories are no longer maintained in this tree.
