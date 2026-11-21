# DB-CPP-01 — C++ database migration, Linux x64

## Authorized outcome

The owner authorizes implementation, tests, documentation, commits, pushes, pull requests and normal protected merges in this batch. The same versioned C# business consumer must retain the merged Rust product's behavior on PostgreSQL and SQLite using the C++ candidate. Normal native production, packaging and execution must require no Rust. DB-API-01, DB-Perf-01, new ORM features, public package publication, hosting products and Windows/macOS acceptance are outside this batch.

Start from the observed main commits in [baseline.json](baseline.json). Only merged capabilities count. Historical acceptance remains attached to its original bytes; an old passing result is not a new migration result. The user explicitly authorized clearing old local worktrees and build/tool copies before continuing. [cleanup-linux.json](cleanup-linux.json) records the completed cleanup.

## Execution boundary

- Branch in each repository: `task/DB-CPP-01-linux`.
- Worktrees: `ROOT/.worktree/DB-CPP-01-linux/{NativeWeave,NativeWeave-Design,Plan}`.
- Fixed Rust reference: `ROOT/baseline/rust`, detached at the product baseline and not edited. Build outputs, packages and hashes have separate reference provenance.
- C# public API, namespace, entity/DTO generation, Fluent syntax, async/cancellation/errors/disposal and the twelve package identities remain compatible.
- The C++ implementation preferentially implements the existing C ABI: symbols, calling convention, layout, capabilities, handles, buffer and callback ownership. Exceptions terminate at the ABI error boundary.
- Unknown business tables remain runtime metadata. A new C# model/DTO or query must not require a new native binary.
- SQLite files and PostgreSQL database state, including migration history/checksums, remain directly usable.

## Migration table

| Existing contract | C++ module responsibility | Reusable verification | Status |
|---|---|---|---|
| Bootstrap, ABI layout and negotiated exports | Shared interop and exported C tables | Interop.Abi, Negotiation, compatibility and loaded-asset checks | Implemented; final regression/CI acceptance pending |
| Handle generations, lifetime, owned buffers, callback/async retirement | Shared interop resources | Lifetime, Memory, Callbacks, Async, Execution and error suites | Implemented; final regression/CI acceptance pending |
| Data source, pool, session and close/drain | Database Host and provider connections | Data.NativeHost, Data.Postgres, Data.Sqlite | Implemented; final regression/CI acceptance pending |
| Fluent arena, immutable query plan, cloning, expression ownership | Runtime query model and dialect compiler | Query.Binding, Query.Native, Query.Fluent and SQL golden assertions | Implemented; final regression/CI acceptance pending |
| Explicit SQL, parameter order/types, prepared execution | SQL lexer, codecs and prepared plans | Data.Codecs, Query.Native and host execution tests | Implemented; final regression/CI acceptance pending |
| Bounded row batches, DTO materialization, early disposal | Cursor and batch ownership | Data.Streaming, Data.Materialization, resource/failure oracles | Implemented; final regression/CI acceptance pending |
| CRUD, relationships, batching and optimistic concurrency | Relational plans and mutation execution | Orm.Relations, reference business consumer | Implemented; final regression/CI acceptance pending |
| Transactions, savepoints and unknown commit outcome | Session transaction coordinator | Data.Transactions and independent PostgreSQL fault oracles | Implemented; final regression/CI acceptance pending |
| Migrations, history/checksums and catalog reads | Migration and provider catalog implementation | Data.Migrations, history handover and independent SQL | Implemented; final regression/CI acceptance pending |
| PostgreSQL TLS, state, cancellation/drain/disconnect | libpq asynchronous execution | Existing provider TLS/process/proxy regressions | Implemented; final regression/CI acceptance pending |
| SQLite locks, BUSY/LOCKED, transaction modes/durability | sqlite3 prepared statement worker | Existing lock and persistence regressions | Implemented; final regression/CI acceptance pending |
| Core/provider precompiled packages and dependency closure | CMake install, package production and provenance | Packaging.Domain, Packaging.Linux, Packaging.Release | Implemented; final regression/CI acceptance pending |
| Same consumer on old/new engines, JIT/AOT, changed model | Versioned out-of-tree business consumer | PostgreSQL/SQLite × JIT/AOT and unchanged native hash | Passed on candidate `3e49cee`; fresh candidate `7ad56394` rerun and final CI/merge pending |

## Implementation decision to record in Design

Finite source research favors C++20 runtime query metadata/AST with direct libpq and sqlite3 execution. SeaQuery 1.0.2 and the actual NativeWeave validation/compiler are the behavioral reference, not a new public query language. KDb demonstrates runtime schemas; sqlpp11/23 emphasize compile-time schemas and are not required. Drogon informs the asynchronous split, ADBC informs independent batch ownership and WCDB informs SQLite bridging; none is automatically a dependency.

Use LLVM Clang/clang++ on Linux, the same upstream LLVM with Apple SDK on formal macOS builds (record Apple Clang separately for local builds), and clang-cl/MSVC ABI/runtime/Windows SDK on Windows. Lock LLVM/format/tidy to a common stable version where feasible. Actual acceptance is Linux x64 only. NativeWeave configuration is independently written for this repository, using the specified DesktopPlatform commit as a reference.

## Stages and gates

1. Clean old local work, freeze merged sources and read the effective contracts. Publish this Plan checkpoint before changing Design/product.
2. Record the source-backed implementation decision, API/ABI/package/data compatibility and dependency/toolchain locks in Design. Preserve historical accepted records.
3. Bring the original C# consumer through C++ query construction, execution, row reading and release for one provider, then finish both providers and all retained contracts.
4. Replace Rust production and useful native test assertions with CMake/CTest, format/tidy and ASan/UBSan gates. Remove replaced Rust source/build/maintenance paths only after equivalent retained behavior exists.
5. Execute the original regressions plus the same versioned business source in separate reference/candidate processes and equivalent databases. Compare values/types/order/rejections, independent SQL, old data/history handover, failures, cancellation, pool/stream bounds and deterministic disposal.
6. Build and pack in a clean Linux environment without Rust, consume the unchanged package identities outside the source tree in all four provider/JIT/AOT cells, and verify binary/dependency/export/load provenance. Modify C# metadata and show that the candidate native hash remains unchanged.
7. Complete independent technical reviews, normal required PR checks, merges and actual merged-main CI. Commit the complete final migration report and observed evidence to Plan, then stop.

No full-result buffering may stand in for a stream. No public breaking change, skipped provider, weakened assertion or old bug silently reclassified as success is acceptable. Record any confirmed old defect separately. A key capability or validation gap means incomplete.

## Evidence and continuation

Update and publish [handoff-linux.md](handoff-linux.md) after each handover-ready stage. It identifies the active branches, exact commits, PRs, completed commands and next work. [acceptance.json](acceptance.json) starts pending and requires actual hashed evidence for every passed check. The final report belongs at `ledger/evidence/batches/DB-CPP-01/migration-report-linux.md`; it must include source transition, dependency decisions, compatibility, actual four-cell results, limitations, presets/reproduction commands and PR/CI links.
