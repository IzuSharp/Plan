# DB-CPP-01 — final native migration result

**The Linux x64 migration was accepted.** The Rust reference
`465cd0f90e6af05ec50eb581156240377cf0825b` was replaced by C++ candidate
`39b5b72ff9bf4d8a485b55debf940f4ded83bbe2`, merged as
`3badc05be503991b5591732629dd7e5b0dbad111` through
[product PR21](https://github.com/IzuSharp/Korda/pull/21).
The C# API, C ABI, twelve package identities and stored formats remained compatible.
All 21 acceptance checks and seven phases completed. The same business consumer
passed PostgreSQL/SQLite × JIT/Native AOT against both implementations; DTO edits
left native binaries unchanged. Design PR15 and Plan PR26 also delivered normally.

## Implementation choices and reasons

The maintained implementation is C++20, with C17 ABI callers and the existing C# facade. Business tables, columns, expressions, entities and DTO shapes remain runtime metadata. The query arena owns mutable builders and generation-bearing expression/alias identities; freezing produces immutable plans and ordered parameter descriptors. The application does not compile C++ when an ordinary C# model or DTO changes.

| Existing responsibility | C++ implementation | Selected upstream and reason |
| --- | --- | --- |
| Core ABI, handles, lifetime, owned buffers, errors, callbacks, async completion and executor retirement | `native/cpp/src/interop.cpp`, maintained fixtures and original public headers | C++ standard ownership/threading primitives; preserve the existing ABI and lifecycle contracts |
| Metadata, canonical schemas, scalar conversion, parameter and row-batch wire format | `contracts.cpp`, `scalar.cpp`, generated schema | nlohmann/json 3.12.0 for checked metadata parsing; retain db-wire/1 and the existing codec registry |
| Fluent builders, freeze/clone, aliases, ordered parameters, dialects and prepared query plans | `query.cpp` | Port the fixed NativeWeave validator and SeaQuery 1.0.2 semantics; keep all 52 exact SQL/parameter goldens |
| Relations, CRUD, bulk operations and optimistic concurrency | `mutations.cpp`, Host execution | Runtime relational metadata and actual provider statements; retain the current C# surface |
| PostgreSQL connections, TLS, prepared execution, incremental rows and cleanup | `provider.cpp` | PostgreSQL/libpq 18.0 asynchronous APIs, prepare/describe and single-row mode |
| SQLite connections, locks, prepared execution and persistence | `provider.cpp` plus static engine | SQLite 3.51.3 amalgamation, byte-identical to the fixed Rust libsqlite3-sys 0.37.0 engine sources |
| Source/pool/session ownership, admission, transactions, savepoints, streams and C entry points | `host.cpp`, `host_abi.cpp` | Finite queues and workers with explicit close/join boundaries; no new public execution abstraction |
| Migrations, catalog, history/checksum, concurrency and nontransactional recovery | `administration.cpp` | Direct provider APIs with the existing ledgers, SHA-384 migration checksums and dedicated administrative lease |
| Native production, package inventory and runtime closure | root CMake/presets and existing Packaging components | Pinned Clang/Ninja/CMake, Release installation, source and linked-input inventories; existing provider package split |

The finite source comparison is documented in [ADR-0006](https://github.com/IzuSharp/NativeWeave-Design/blob/main/docs/decisions/ADR-0006-database-cpp-native.md) and [the migration specification](https://github.com/IzuSharp/NativeWeave-Design/blob/main/docs/database/cpp-migration.md). KDb demonstrates runtime schema descriptions, but would add Qt and a second schema contract. sqlpp11/sqlpp23 emphasize C++ schema types and do not fit arbitrary business schemas admitted through C# metadata. Drogon provided an asynchronous provider reference, but its SQLite result collection does not satisfy the retained bounded stream behavior. Arrow ADBC informed independent stream/batch ownership. WCDB was a SQLite/bridge reference. None of those frameworks is a runtime dependency.

### Provider semantics

PostgreSQL prepares and describes the statement before exposing result metadata, starts execution on the first fetch and frees each single-row `PGresult`. It drains through the final null result on early exit. The fixed SQLx implementation did not send a cancel-key request when stopping a reader; preserving that behavior prevents ordinary reader disposal from newly aborting an enclosing transaction. Cancellation and deadlines stop business admission while the native owner remains responsible for bounded cleanup. Failure to prove a clean protocol state causes physical discard. An error received while draining unread results also discards the connection.

Loss of COMMIT acknowledgement remains `Unknown`; an independent connection seeing durable data does not rewrite that client outcome. A failed-transaction `25P02` probe followed by explicit rollback yields a known rolled-back outcome. The retained tests include a real framed TCP proxy which observes successful server COMMIT/idle messages, suppresses their acknowledgement and checks persistence independently.

The selected libpq source has a small hash-locked configuration patch which ignores ambient `PG*` defaults inside that library. The Host still rejects its original thirteen prohibited environment overrides. This preserves the fixed SQLx configuration boundary without modifying the process environment. Explicit TLS trust, hostname checks, plaintext opt-in and client-file behavior remain controlled by the provider configuration; tests include invalid default files under an isolated child process home.

SQLite executes prepare/bind/step/finalize on finite workers. The observable busy timeout, BUSY/LOCKED handling, transaction modes, read-only/query-only behavior, isolation refusal, journal/synchronous settings and actual autocommit state are retained. Early exit finalizes the statement without collecting all remaining rows. A real commit hook holds COMMIT beyond the configured 20 ms deadline: the public outcome becomes `Unknown`, then an independent connection confirms persistence after the hook is released, without rewriting that outcome. Old files keep the same SQLite engine and on-disk format.

Streams retain one bounded batch and bounded lookahead; transferred batches keep their reservation until release, including after cursor closure. Column shape is checked completely before decoding, and each field consumes the remaining aggregate row budget. These are the existing NativeWeave resource contracts, not a new whole-process RSS or performance claim.


## Corrections retained as lessons

Earlier candidates failed actual compatibility checks and were not accepted.
Savepoint disposal after rollback/release could close the outer transaction while
a later Commit owned the Session gate. The fix recognizes closed/missing tokens
before acquiring the gate and distinguishes ordering errors from parent closure.
Stream completion now publishes only after cleanup and the worker's owner release;
Source retirement updates the last pending owner under the join mutex. These
barriers preserve immediate resource-credit return and prevent lost wakeups.

SQLite physical-input admission, provider encoding widths, error ordering, elapsed
budgets and transaction confirmations required corrections. Lost COMMIT acknowledgement
remains Unknown even when independent SQL later confirms durable data. Necessary
protocol-cleanup proofs were preserved. Later documentation/diagnostic-literal
fixes were kept separate from changed runtime behavior.

The final [PR CI](https://github.com/IzuSharp/Korda/actions/runs/44974091036) and
[main CI](https://github.com/IzuSharp/Korda/actions/runs/44977773509) passed their
applicable gates. The fixed-Rust comparison belongs to its actual candidate/local
execution, not a newly repeated main run. Public release, other platforms,
DB-API-01 and performance improvements were outside this batch. The
[contract mapping](migration-table.md) records retained responsibilities.
