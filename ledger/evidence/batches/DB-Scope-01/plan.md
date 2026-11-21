# DB-Scope-01 — database product scope, Linux x64

## Authority and product boundary

The owner terminated Perf-01 on 2026-11-21 and authorized this three-repository scope change through tested, reviewed merges. The only product is a strongly typed Fluent ORM for PostgreSQL and SQLite, using Rust SeaQuery and SQLx, usable from ordinary C# applications and Native AOT. A standard ASP.NET Core HTTP endpoint and a standard C# gRPC method may call the same C# business query method. The application selects its server; installing the database packages must not install a NativeWeave server or protocol runtime. No new HTTP/gRPC wrapper or ORM feature is authorized.

The active sequence and state live in `delivery-graph.json.current_execution`. The original 34 research, 32 documentation and 48 delivery nodes/packets, accepted bindings, and Task-01 through Task-07 ledgers remain historical records. The old `source-driven-baseline.json` continues to pin historical research acceptance; it is not current authorization or proof of the changed product. Perf-01 branches, binaries and timing results are not inputs to this batch. Performance optimization and 30-minute load tests are deferred to a later authorized task.

## Fresh inputs and working rules

| Repository | Fresh main input |
| --- | --- |
| Plan | `8afa0311f45ab8a8157fc45c51e95a0b17dd09f2` |
| NativeWeave-Design | `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9` |
| NativeWeave | `ea5fa528035d025bd7a28698ee7c71194432236c` |

All checkouts use `task/DB-Scope-01-linux` under `ROOT/.worktree/DB-Scope-01-linux/`. Root AGENTS.md in all three repositories were read. Their older research-only/bootstrap instructions are superseded by this explicit owner instruction; exact evidence, English documentation, independent review, normal GitHub protection and required checks still apply. No license/permission/protection change is authorized. Leave unrelated Dependabot PRs 3, 4 and 7 alone.

## Retain, based on actual dependency tracing

| Capability | Existing implementation and verification ownership |
| --- | --- |
| Data sources, pools and sessions | `src/Data.NativeHost`, both provider projects, `native/database/host`, `postgres`, `sqlite`; Database Host is retained execution, not a server |
| Transactions, migrations, parameter binding | `src/Data.Transactions`, `Data.Migrations`, `Data.Codecs`, `Query.Binding`; corresponding `native/database` crates and regression suites |
| Strongly typed Fluent, static models and DTOs | `src/Query.Fluent`, `Query.Native`, `Query.Generator`, `Data.Materialization`; SeaQuery native compiler and database static mapping/generator checks |
| Relations and CRUD | `src/Orm.Relations`, `native/database/relations`, relational/concurrency regressions |
| Streaming, cancellation, errors and disposal | `src/Data.Streaming`, Core-owned Interop ABI/async/callback/error/execution/lifetime/memory/negotiation modules and native interop dependencies |
| Precompiled native asset consumption and AOT | Core, Interop.Abi, database packages, actual APIReference/compose_docs/Core documentation checks, Packaging.Linux/Packaging.Release/compatibility helpers reached by real DB packaging gates |

The public provider projects reference Database/Core/Data and the static query generator; they do not reference Server. `NativeWeave.Database.csproj` compiles the existing Query.Native, Query.Fluent, Orm.Relations, Data.Migrations and Data.Materialization implementations. Its Rust Host composes the database crates and SeaQuery/SQLx. Keep this composition and every implemented database capability. Common components are retained by dependency and regression need, not by their generic names.

## Dependency audit correction — generic tooling

The initial Plan/Design inventory incorrectly listed `Generators.Model` as database model generation. The [fresh-main dependency audit](dependency-audit.json) records exact source hashes and every incoming project reference to the generic generator/analyzer families. Database static models use `src/Query.Generator`; database native prototypes use `tests/Query.Binding/generate.py` with `native/database/binding/signatures-v1.json`. No Data/Query/Orm project or retained twelve-package producer depends on `Generators.Model`, `Generators.CSharp` (including Metadata), `Generators.Rust` or the generic `Analyzers` product. Their remaining consumers are their own samples/tests and proof fixtures.

Remove those orphan generic generator/analyzer products, their exclusive tests/samples/docs/locks and solution/API-documentation configurations. Keep `Query.Generator`, its diagnostics and actual database generator tests. Standard SDK/compiler analyzers and the retained database API/documentation checks still run. This correction removes no database model, DTO, binding or runtime capability.

Split generic tool directories by actual use:

| Area | Keep for the database product | Retire after equivalent relevant guards are connected |
| --- | --- | --- |
| Build.Integration | `ApiReference`, `compose_docs.py`, `api/core.json`, API fixture data/project and `tests/Build.Integration/verify_docs.py` | `build_native.py`, generic `NativeWeave.Build.targets`, proof native profiles/fixtures/sample and generator/analyzer/metadata documentation configurations |
| Packaging.Release | `release.py`, `BuildTasks`, `buildTransitive`, `tests/Packaging.Release/ApiCheck` and safeguards used by real Packaging.Domain | Artificial `prepare.py`, conformance package consumer/native/sample and their obsolete default CI path |

Migrate the artificial package fixture's unique checks to the real database candidates before deleting its harness: invalid/duplicate closure schema and JSON, nonexact dependency edges, unsupported RID/CPU baseline, malformed ABI/identity, source/output traversal, missing/duplicate selected native files, hash drift before compile/build, duplicate native basenames, plus applicable publication/recovery safeguards. Run those assertions through the retained actual MSBuild packaging task and database release path. This is moving the checks to the product being shipped, not waiving a failing check.

The correction follows the same order as the batch: publish this Plan update, record the matching current Design checkpoint, then delete the newly identified orphan code and reconnect the retained guards. Existing authorized product pruning may continue; these additional orphan deletions wait for both checkpoints. Record the checkpoints in the handoff and `delivery-graph.json.current_execution.scope_refinements`. Historical generator/tooling acceptance remains unchanged historical evidence.

## Remove and reconcile

Remove managed `Server.Application`, `Server.Diagnostics`, `Server.Native`, `Server.Streaming`, `Protocols.Grpc`, `Protocols.Mcp`, `Engines.SyncProof`, `Engines.AsyncProof`, `Verification.ExtensionProof` and `NativeWeave.HelloWorld`; remove native `server`, `protocols`, `engines`, `hello-world`; remove their exclusive tests/examples/API docs/manifests. The independent SyncProof engine is miniz_oxide compression; AsyncProof is an HTTP proof. Neither is a database dependency. Retire HelloWorld-only `tools/ApiDocs`, default consumers and packaging rules.

Reconcile Cargo workspace/lock, .NET solution/lockfiles, friend-assembly entries, generated bindings/asset manifests, dependency inventories, NuGet graph, build/pack/release scripts, CI, security scans, README, API references and examples. Removed components must leave the default build/test/package chain. The default `eng/build.py` and release path currently target HelloWorld; replace that closure with actual database candidate packaging and consumers. The existing Packaging.Domain model has 17 IDs; prune the 5 server/protocol IDs to the existing 12-package database closure. Do not suppress a retained failing check or remove security/format/API/lock/provenance gates merely to get green CI.

No public database release is required by this batch: create and consume candidates. Retire the old demo publication product. Any retained publishing machinery must support only the retained database closure and preserve review/identity/signature safeguards; do not unexpectedly publish new domain packages on merge.

## Mixed reference and end-to-end coverage

Do not delete mixed reference/test directories wholesale. Preserve the unique database checks as direct C# business-query/console consumers with no NativeWeave server dependency:

- Verification.EndToEnd DatabaseCases: pre-admission commit cancellation with confirmed rollback and no durable row; actual failed transaction and rollback; same physical PostgreSQL session; early stream/session admission/release; data source/session/reference retirement.
- HttpCases database-specific assertions: nullable/composite foreign-key queries, moved to direct database calls.
- Reference.TaskService DatabaseService: typed idempotent create/replay, PostgreSQL ReadCommitted next-statement conflict lookup, typed pagination, recovery, optimistic CRUD and outbox transactions.
- PostgreSQL oracles: observed lock/concurrent conflict and lost COMMIT-ack durable-state checks. Adapt their driving process to direct database execution; keep the database fault proxy if needed, remove HTTP service coupling.

Existing tests remain evidence only for their original commits. Every retained/current verification row in this batch requires actual new execution.

## Required order and acceptance

1. **Stop and clean.** Close product PR19 and Plan PR23 unmerged, with scope-change reason. Inspect/stop old local workers/timers/autopush and clear only old task-owned directories. Record inaccessible hosts or actions honestly. Never clear the newly established DB-Scope-01 workspace on continuation.
2. **Plan first.** Commit and push this plan, task graph and acceptance/handoff entry; create Plan PR before editing Design or product source. Independent source inspection and new validation environment preparation may run meanwhile.
3. **Design.** Prune active design/API/package/reference documentation; explicitly retire Server/gRPC/MCP/compression/demo scope. Preserve exact historical accepted evidence at original immutable commits and run its unchanged historical gates there. Add current scope validation and independent scope review. Record the Design checkpoint before product edits.
4. **Implementation.** Prune the dependent source/build/package/test/docs surfaces and migrate unique database regression coverage. Only pruning and necessary regression repairs; no Perf-01 patches or new ORM features.
5. **Linux regression.** Build/test the retained Rust and C# workspaces, locked dependencies, format/analyzer/API checks. Run actual PostgreSQL and SQLite database/ORM regressions, including normal/failure/cancel/transaction/migration/relationships/streams/disposal cases. No skipped mandatory provider cells.
6. **External candidates.** Pack retained database NuGets from the pruned source. Outside the source tree, restore ordinary PackageReference consumers using a separate package cache and precompiled native assets. Run typed Fluent queries and DTO mapping for PostgreSQL JIT, PostgreSQL Native AOT, SQLite JIT and SQLite Native AOT. Assert persisted/read data, not merely exit code. Record source/package/native/executable identities.
7. **Dependency proof and completion.** Inspect every candidate nuspec, project.assets dependency graph, publish directory and actual mapped native libraries. Fail if Server/gRPC/MCP/proof/demo packages or assets are present. Block cargo/rustc/rustup in consumer builds and record zero invocations; use the existing genuinely no-Rust container check when available, distinguishing a local trap from a pristine machine. Review actual changes independently; fix scope regressions; create paired Design/product PRs, complete required checks, merge under existing rules, and inspect exact merged-main CI. Update this Plan PR with results, merge it, verify its main CI and stop.

## Evidence and stop condition

Use `handoff-linux.md` after every durable checkpoint. `acceptance.json` begins pending and may advance only with actual command logs, source identities and independent review. Keep failed attempts as failed. Record final PR URLs, head/merge commits and exact run URLs. Stop after pruning, tests, reviews and merges pass; do not start performance work or another task.
