# DB-Exec-Parity-01 — PostgreSQL source audit

## Status and scope

This is a read-only source and historical-evidence audit. It is **not** a completed PostgreSQL profile, a new workload result, a stage-one acceptance, or authorization to select an optimization from speculation. No product file, CI definition, remote branch, or Go draft was modified by this audit. No benchmark was started.

Korda's `AGENTS.md`, `eng/ci/modules/README.md`, and `.github/workflows/ci.yml` were read first. Native AOT consumers, the committed-diff module planner, independent top-level provider validation, and existing publication rules remain applicable. Performance diagnostics, calibration, and load work remain local Linux work. There is no recommendation here to trigger any of them in CI.

The root agent is separately validating the current environment. No current Korda/Dapper Native AOT ELF, matching machine-code annotations, backend PID timeline, runtime wire trace, per-stage thread CPU, or measured copy/allocation counters were produced by this source audit. Those columns remain unknown.

## Source identities and prior delivery

| Input | Observed identity | Use in this audit |
| --- | --- | --- |
| Korda main | `7ff7b57b907b689defb880b8af62d83679608603` | Current C#/C++ implementation; normal merge of #37 |
| Korda-Design main | `ca9348ad0b5cc93bc75c502460d8e1b75843d109` | Current execution contracts and #20 final body |
| Plan main | `03efe57ffbe3046bd89919ddb2c16c90a377954d` | Historical phase and allocation audit; normal merge of #34 |
| Go source draft #39 | `d5f4f9d6616bad54a08aebb7d1aca7937b18eb93` | Read-only reference; remains open Draft; no merge/auto-merge |
| Dapper.AOT | package `1.1.0`, source `0e071bf05e54caecfa98c885b075fa3e247f3ecc` | Query implementation and actual archived generated reader |
| Dapper | current db-perf consumer declaration `2.1.100`; older Database/campaign lock `2.1.79` | Different harness identities; current restore graph must be generated and locked, never inferred from the older lock |
| Npgsql | package `11.0.0`, source `4d174200ed48e3e3ab16419dbf84dd655da59de6` | Command/write/read/buffer paths |
| libpq / PostgreSQL | `18.0`, source `3d6a828938a5fa0444275d3d2f67b64ec3199eb7` | Extended protocol, partial results, backend dispatch and plan revalidation |
| pgx | `v5.11.0`, tag resolved to `5e583fa7aabfa88b796292f849fc9d7d75ac159d` | Go exec mode, row lifetime, database/sql conversion |
| Go toolchain declared by the reference | `go 1.27.4` | Identity only; not installed or executed by this audit |

The product native dependency lock also pins LLVM `23.1.5`, CMake `4.3.3`, Ninja `1.13.2`, SQLite `3.51.3`, nlohmann/json `3.12.0`, archive hashes and the explicit libpq configuration patch. These pins must govern reproduction rather than whatever system libraries happen to be installed. The older `benchmarks/Database/campaign` PostgreSQL lock resolves .NET ILCompiler and ILLink `11.0.0`; it is a separate harness from current `benchmarks/db-perf/managed`, whose complete restore graph must be preserved from its own build. Current Dapper source declares `2.1.100`; the earlier `2.1.79` lock is not current-consumer evidence.

Design #20 reports completion of the prior local final runs, normal merges, existing main CI, and both independent `0.1.0-preview.4` public-package AOT consumers. Those are prior delivery observations, not this task's after measurements. Its implemented design explicitly retains fresh PostgreSQL metadata before Execute and the tested queued final-close path; physical statement caches remain unselected.

The Go draft records a completed source/worktree/cache cleanup. Absence of its earlier build directories should not be interpreted as a missing benchmark result, nor should historical Go runs be restarted merely to restore a local directory.

Sources: [Korda #39](https://github.com/IzuSharp/Korda/pull/39), [Design #20](https://github.com/IzuSharp/Korda-Design/pull/20), [implemented strategy](https://github.com/IzuSharp/Korda-Design/blob/ca9348ad0b5cc93bc75c502460d8e1b75843d109/docs/database/execution-path-17da.md), [dependency lock](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/native/dependencies.lock.json), [Dapper PostgreSQL package lock](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/benchmarks/Database/campaign/dapper/postgresql/packages.lock.json).

## Historical counterexample that determines the next observation

The retained phase extraction reports the following PostgreSQL 1,000-row observations. They pool three original windows of 256 operations each. CPU and managed allocation are process-wide window deltas including harness and business results, not component attribution.

| Route | CPU µs/operation | Total managed B/operation | Four-phase p50 µs |
| --- | ---: | ---: | ---: |
| Current-at-that-run ordinary Fluent | 4,503.792 | 97,452.604 | 2,810.648 |
| Current-at-that-run hot Prepare | 4,307.207 | 80,541.625 | 2,704.440 |
| Current-at-that-run Host SQL | 4,308.611 | 86,273.604 | 2,634.807 |
| Dapper.AOT | 542.667 | 79,986.031 | 462.550 |

Thus the historical hot-Prepare allocation difference is 555.594 B/operation while CPU is about 7.94 times Dapper. Host SQL has essentially the same reported CPU as hot Prepare. This supports inspecting the shared execution/result path before attempting another broad query-construction rewrite. It does **not** identify any particular lock, copy, callback, or driver function as the CPU hotspot.

The separate historical allocation overlay attributes 69,760 B/operation to the Korda 1,000-row mapper scope and 8,056 B/operation to its List construction/Add scope. Dapper PostgreSQL's mapper scope was 69,773.5417 B/operation in that diagnostic run. These scope measurements are not subtracted from total process allocation to manufacture a framework-only figure. The historical report explicitly retains `FrameworkOnlyBytes=null` and `timingCredit=false` for the overlay.

Sources: [historical phase extraction](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/preexisting-measurement-summary-01.md), [historical allocation audit](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/current-measurements/allocation/README.md). The phase extraction identifies its source JSON SHA-256 as `4cf173c561ecbac7726132fafc24ea1059b6969eabe1d7a18efb3111884426b2`; it is not a newly revalidated raw measurement in this audit.

## Protocol path: API calls, wire messages, and actual waiting are different quantities

### Korda normal successful typed SELECT

`CursorPull::request` queues work; first `CursorPull::run` calls `Session::open_cursor`, then `Cursor::fetch`. Provider creation encodes typed parameters to owned text strings. `ProviderConnection::prepare` enters libpq pipeline mode, sends an unnamed Parse, a statement Describe, and Sync; it consumes through `PGRES_PIPELINE_SYNC` and exits pipeline mode before the first execution fetch. It validates complete metadata before Bind/Execute. Unknown extension types can add a catalog query and another Parse, so those need a separately counted workload class.

The first `ProviderStatement::Impl::advance` invokes `PQsendQueryPrepared` with text parameters and binary result format. Direct inspection of libpq's `PQsendQueryGuts` establishes that this **one** API call sends Bind, Describe **portal**, Execute, and Sync outside pipeline mode. Korda then enables single-row mode.

For a normal one-statement query with known built-in types, the source-derived frontend sequence is therefore:

1. Parse + Describe statement + Sync; consume preparation completion.
2. Bind + Describe portal + Execute + Sync; receive the result and final ReadyForQuery.

This is seven frontend messages and two logical response barriers, but is not proof of two kernel blocking calls or two equal-duration network round trips. Messages can be coalesced and responses may already be buffered. Existing `protocol_count` increments four times for this path (three preparation APIs and one execution API); its value is **not** a wire-message count. `dispatch_count` increments once for the business execution; it is **not** an FFI count.

The exact wait point is `receive`: `PQflush` first; then `PQconsumeInput`, `PQisBusy`, and `PQgetResult` when ready. `wait_socket` enters `poll(POLLIN/POLLOUT)` only when required, with cancellation/deadline checks and bounded 1–20 ms poll timeouts. A `receive` call or an awaited outer task cannot itself be labeled waiting. Its thread CPU and the poll interval must be measured separately.

### Dapper.AOT → Npgsql

The main and phase Dapper drivers set `MaxAutoPrepare=0`. The generated phase factory reuses a command/parameters under `[CacheCommand]`; this is not by itself evidence that the server statement is explicitly prepared. The actual selected calls are `QueryUnbufferedAsync`, with generated ordinal parameter updates and a generated row factory. No explicit application Prepare is in that phase probe.

Npgsql's normal unprepared `NpgsqlCommand.WriteExecute` queues Parse + Bind + Describe portal + Execute + Sync in one sequence. `ExecuteReader` starts the send and proceeds to reader work without globally awaiting the entire send, which is necessary for multi-statement send/read overlap. Time in send and read must therefore not be blindly added as independent critical-path intervals.

`NpgsqlDataReader.ReadAsync` first tries `TryRead`. Already buffered rows use cached true/false tasks and direct buffer/message parsing. Only a fallback enters `Read` and its nested cancellation scope. `NpgsqlReadBuffer.Ensure` returns immediately if bytes are already available; `EnsureLong` is the path that can read from the underlying socket/stream, and can compact unread bytes. Instrumenting every `ReadAsync` as an OS wait would be wrong.

Npgsql's command connection setter merely changes the logical connection/transaction association; its source does not equate that action with a server Unprepare. The observed phase still disables automatic preparation and does not call explicit Prepare. Runtime command and statement counters must validate any proposed reuse comparison.

Sources: [Korda provider](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/native/cpp/src/provider.cpp), [Korda Host](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/native/cpp/src/host.cpp), [libpq fe-exec.c](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/interfaces/libpq/fe-exec.c), [NpgsqlCommand](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlCommand.cs), [NpgsqlDataReader](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlDataReader.cs), [NpgsqlReadBuffer](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/Internal/NpgsqlReadBuffer.cs).

## Source comparison table for the combined two-database ledger

Counts below are **source-derived expectations**, not observed runtime counters. Assume one successful SELECT, built-in types, no retries, complete consumption, `batchRows=32`, and no byte-capacity split. Every CPU/wait/allocation-byte delta in this task remains unmeasured.

| Business stage | Korda source / counterpart | Expected repetition and work | Current evidence / unknown | Protected contract and next observation |
| --- | --- | --- | --- | --- |
| Construct / reuse | Query Fluent/Prepare/Host SQL; Dapper generated command factory | Query-scoped; phase factory updates two ordinal Int64 parameters | Historical four-route counterexample; no current component CPU | Preserve input snapshots; record build/render/snapshot/submit independently |
| Encode parameters | `postgres_encode`, `ProviderConnection::prepare`; Npgsql parameter processing/write | One conversion per parameter; Korda owns optional text strings, values-pointer array | Text parameters and binary results confirmed from source; actual bytes/allocation unknown | Decimal/date/JSON/domain/null/error semantics; count encoded and copied bytes |
| Submit / native work admission | `CursorPull::request`, `WorkerPool::post`; Npgsql command/reader | Korda creates Cancel + Worker and queues one action per pull generation | Queue path confirmed; queue/wakeup/runnable delays unknown | One accepted generation/notification, cancellation and source retirement; timestamp enqueue/start/ready/take |
| Fresh description | Korda Parse/Describe statement/Sync; Npgsql inline Parse/Bind/Describe portal/Execute/Sync | Korda one extra description and one pre-Execute response barrier per ordinary query | Seven vs five frontend messages predicted; actual waits/messages not traced | DDL fresh shape and no execution before validation; sample poll and backend message events |
| Driver rows | `Impl::advance`, libpq `pqRowProcessor`; Npgsql `TryRead`/`Read` | Korda single-row PGresult per row; Npgsql buffered-row fast path | Actual native allocation, CPU, read syscalls and bytes unknown | Row/field quotas, cancellation, errors; count PGresult clone/free and buffer misses |
| Native row checks | `advance`, `Cancel::install`, `preflight_row`, `postgres_decode_into` | Cancel hook install once per advance; shape preflight per row/column; decode/check per non-null cell | Mutex/string/type/codec operations confirmed; expense unknown | Cancellation order, type/NULL/error precedence; phase-local thread CPU and lock hold/wait timeline |
| Batch construction | `BatchWriter::{begin_row,append_validated,commit_row,finish}` | One NWDB payload write per admitted non-null value; one final cell-offset pass; partial batches compact payload | No measured copied-byte totals; byte overflow can cause held-row retry | Fully validate held/lookahead row before publishing earlier rows; instrument writes/memmove/retries |
| Batch transfer | `NativeHost.TakePullBatch`, `ScopedStreamBatch.Attach` | Native view and owner attachment, no whole-batch managed byte-array copy in selected pull success path | This absence is source-confirmed, not a whole-path zero-copy claim | Generation lifetime, compensation on failure, no borrow across await; record native ownership and release |
| Managed batch validation | `RowBatchLease.Attach`, `DbWire.Validate` | Once per received batch, with descriptor/cell/scalar validation over all cells | Full validation exists; CPU contribution unknown | All cells validated before first exposed row, bound codec/shape/byte ranges |
| DTO materialization | `TypedStream.MoveAsync`, `RowBatchLease.Materialize`, `Projection.ReadBatch`, generated `row.Read`; Dapper generated RowFactory | Korda several managed gate entries per row, read-scope acquisition/release, per-column descriptor/lifetime/delegate decode; Dapper Tokenize once, typed reads per row | Historical mapper allocations available; no current instructions or per-call CPU | Owned DTO values, read/close races, exact null/type semantics; inspect actual new generated reader and ELF |
| EOF | `Cursor::fetch`, `Impl::advance`; Dapper reader completion | Normal full 32 rows needs a second empty pull to discover EOF; 100 rows needs 4 pulls; 1,000 rows needs 32 pulls if byte quota does not split | Source expectations only | `CommandComplete` or full batch alone is not ReadyForQuery; measure empty generation separately |
| Early stop / release | `ProviderStatement::close`, `protocol_sync`, queued CursorPull close; Npgsql reader cleanup | Korda drains the same Execute and may Sync/confirm; it does not issue a cancel-key simply to stop enumeration | Fixed close scheme verified in source; no new close latency | Preserve usable surrounding transaction, failed-drain discard, independent native worker/notification fences |
| Transaction result | narrow `postgres_transaction_ready_for_commit`, transaction worker | Normal proven INTRANS can skip old pre-COMMIT probe; uncertain states retain controls | Existing selected strategy, no new timing | Lost/delayed post-COMMIT confirmation remains Unknown; do not infer from successful send |

## What can make 1,000 rows amplify a gap

The source has distinct scaling dimensions. Fresh metadata preparation is query-fixed. Native queue handoff is batch-scaled. PGresult cloning/free, cancellation hook installation, managed move/lifetime gates are row-scaled. Native type checks, libpq field copy, canonical codec decoding, NWDB descriptor writes, managed scalar validation and generated reader accesses are column-scaled. Payload compaction, UTF-8/JSON checks and string/array result creation additionally scale with bytes.

At two columns and 1,000 rows, source expectations include roughly 2,000 column preflights, 2,000 NWDB cell finalizations, 2,000 managed cell validations, and 2,000 generated reader accesses, alongside 1,000 libpq single-row result deliveries. This is a map for counting; it does not establish relative cost or prove that these calls survive inlining as separate machine-code calls. Optimized assembly and actual counters are still required.

`Cancel::install` takes a native mutex and replaces a `std::function`; its weak-owner callback capture is recreated in each applicable `advance`. The exact heap allocation behavior of that function object depends on its compiled representation and library implementation, so this audit does not call it a proven heap allocation per row. Similarly, managed monitors may be uncontended; lock count is not lock-wait time.

libpq `pqRowProcessor` clones result metadata for each partial result, allocates field storage from the PGresult arena, and copies non-null field bytes out of its input buffer. Single-row mode limits each partial result to one row. PostgreSQL 18 exposes `PQsetChunkedRowsMode`; it reduces the frequency of result metadata/result ownership operations in source terms, but changes retained rows, error timing, and early-stop memory exposure. A chunk candidate needs dedicated quota, mid-chunk error, cancellation, exact-batch EOF, and early-stop tests before selection. No chunk optimization is selected by this audit.

The selected Korda pull seam reads the native NWDB buffer through a scoped span, so a proposed explanation of “one full native-to-managed byte[] copy per batch” is incorrect for its normal success path. Observable byte-copy candidates are libpq's input-to-PGresult copy, decoded/canonical payload insertion into NWDB, BatchWriter capacity growth, partial-batch memmove, and ownership-required CLR string/array creation. Their totals must be counted individually.

## Generated readers and symbol identity

The retained original phase generator files were read directly in Plan:

- `continuation-3/allocation-recovery/consumers/allocation-dapper-sqlite-05/generated-original/.../DbPerf.DapperQueryPhases.generated.cs`: `RowFactory0.Tokenize` maps Id/Note names and field types once, then `RowFactory0.Read` uses `GetInt64`, `IsDBNull`, `GetString` or its flexible typed fallback and constructs `PhaseRow`. Two command-factory instances serve the two SQL call sites; both update ordinal Int64 parameters and reuse command storage.
- `continuation-3/allocation-recovery/consumers/allocation-before-sqlite-05/generated-original/.../PhaseRow.e0f2c2a3341791d870b28338754b000612832ee7f94e849bf9013bc19fbe4f8e.Projection.g.cs`: Korda's generated delegate constructs the same two-column DTO using `row.Read(0, Int64)` and `row.Read(1, nullable String)`.

These are **historical SQLite-labelled generation identities** and are not silently promoted to newly built PostgreSQL artifacts. The previous allocation audit explains that provider-specific receipts bind reused generated sources to their original AOT builds. A current PostgreSQL build must preserve its actual emitted source, lock/restore graph, compiler command, exact package/native image, ELF build ID and symbols. The nine-column Order RowFactory from the mixed campaign must not substitute for this two-column PhaseRow reader.

Machine-code mapping remains pending. When binaries exist, annotate the actual native `Cancel::install`, `ProviderStatement::Impl::advance`, `pqRowProcessor`, `BatchWriter::finish`, scalar conversion loops, and managed AOT `TypedStream`/`RowBatchLease`/generated reader/codec sites. Do not attribute a sample to an uninlined source call without matching the ELF and symbols.

## Go reference: useful control with a different protocol encoding

The unchanged Go consumer uses one persistent `database/sql` connection per worker. SQLite prepares retained public statement objects; PostgreSQL passes `default_query_exec_mode=exec`, `statement_cache_capacity=0`, and `description_cache_capacity=0` and does not populate its per-query prepared statement array. The application uses hand-written `rows.Next`/`rows.Scan` DTO mapping and checks result layout once per query shape. Its mapping is neither Dapper generated reading nor Korda generated reading.

In the pinned pgx implementation, exec mode calls `ExtendedQueryBuilder.Build` with no statement description. Parameters are encoded as text and the result-format list stays empty. `PgConn.ExecParams` queues Parse + Bind, then its suffix queues Describe portal + Execute + Sync and flushes before reading metadata. Although the database/sql adapter supplies a preferred format-by-OID option, this exec branch passes the builder's empty result-format list. Consequently its source-selected result format is default text. Korda requests binary results. Runtime wire evidence should confirm the observed build before using this distinction quantitatively.

pgx `ResultReader.NextRow` takes borrowed DataRow value slices, valid until the next row/close; the database/sql adapter prepares per-column conversion functions and the consumer scans into owned Go values. `ResultReader.Close` drains through ReadyForQuery and preserves a deferred error that arrives after CommandComplete. This is useful for analyzing send grouping, read buffering, and release, while its absolute CPU cannot be treated as an identical binary-decoding control.

The Go 30-minute throughput/cgo totals are historical mixed-workload aggregates, not normalized per-query FFI cost. The same business query's statement lifetime, rows, columns, bytes, DTO handling, and early-stop policy must be matched before comparing cross-boundary work. No rerun of the completed Go long tests is proposed.

Sources: [Go worker](https://github.com/IzuSharp/Korda/blob/d5f4f9d6616bad54a08aebb7d1aca7937b18eb93/benchmarks/db-perf/go/worker.go), [Go dependency identity](https://github.com/IzuSharp/Korda/blob/d5f4f9d6616bad54a08aebb7d1aca7937b18eb93/benchmarks/db-perf/go/go.mod), [pgx conn.go](https://github.com/jackc/pgx/blob/5e583fa7aabfa88b796292f849fc9d7d75ac159d/conn.go), [extended builder](https://github.com/jackc/pgx/blob/5e583fa7aabfa88b796292f849fc9d7d75ac159d/extended_query_builder.go), [pgconn](https://github.com/jackc/pgx/blob/5e583fa7aabfa88b796292f849fc9d7d75ac159d/pgconn/pgconn.go), [stdlib adapter](https://github.com/jackc/pgx/blob/5e583fa7aabfa88b796292f849fc9d7d75ac159d/stdlib/sql.go).

## Backend and correctness boundaries

Pinned PostgreSQL `postgres.c` directly separates `exec_parse_message`, `exec_bind_message`, `exec_describe_statement_message`, `exec_describe_portal_message`, and `exec_execute_message`. Bind obtains a plan through `GetCachedPlan`; Execute runs the portal; Sync finishes the command boundary and schedules ReadyForQuery. The additional Korda statement Describe returns parameter description plus row metadata, whereas portal Describe returns metadata with the selected result formats. These server operations should not be folded into client CPU.

`plancache.c::RevalidateCachedQuery` invalidates/rebuilds analysis when dependencies change. A long-lived fixed-result prepared statement can produce a changed-result-type error that fresh parsing would not produce. Consequently “cache the physical statement” is not semantically free. The current design deliberately reparses unnamed SQL and validates new metadata before execution. A replacement requires evidence for DDL invalidation, first error order, and absence of unintended execution before rejection.

Cancellation, early stop, and final native retirement are different outcomes. Stopping row enumeration must not cancel an otherwise usable surrounding transaction. A row limit, a full batch, a command tag, or a successful socket send does not prove ReadyForQuery or safe connection reuse. Failed drain discards the lease; failure to confirm COMMIT may leave outcome Unknown. Independent worker/notification fences survive result readiness because callbacks and captured source ownership can still be live.

Sources: [backend dispatcher](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/tcop/postgres.c), [plan cache](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/utils/cache/plancache.c), [current cursor binding contract](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/native/database/binding/cursor-pull-v1.md), [command completion contract](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/native/database/binding/command-completion-v1.md).

## Required local diagnostic sequence before product optimization

1. Build the locked PostgreSQL Korda and Dapper Release Native AOT consumers and retain actual generated source, ELF, native image, symbols, compiler commands, restore locks and hashes. Use separate diagnostic and ordinary-timing identities. Preserve the original SQL, parameter types, DTOs, dataset, server configuration, batch size and queue settings.
2. Instrument a request ID plus pull generation at C# construction/snapshot/submit, C++ enqueue/start, metadata send/completion, execution send, each actual poll begin/end, first row, batch finish, readiness callback, managed take, batch validation, DTO mapping, EOF, close and return. Record monotonic wall time, native thread ID, thread CPU, count, rows, columns and bytes. Timestamp and counter recording must avoid per-event IO/allocation; measure observer overhead.
3. Distinguish wall time in the diagnostic boundary from thread CPU. Wall-minus-thread-CPU includes descheduling, blocking and preemption; it is not automatically socket wait. If scheduler events cannot be observed, label runnable queue/wakeup/scheduling time unknown. Parent/child async spans may overlap; report critical-path intervals instead of adding every span.
4. Record frontend messages independently of libpq API calls and SQL execution counters. For PG diagnostics, `PQtrace` or decoded socket/protocol instrumentation can identify message order; log binary-safe lengths and avoid database credentials/data leakage. Count send calls, actual bytes, reads, buffer hits/misses, PGresult create/clone/clear and materialization separately.
5. Correlate every physical connection to backend PID (`PQbackendPID` for libpq and the corresponding Npgsql connector/ProcessID), and retain a diagnostic server plan and `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` for equivalent SQL/parameters. A separate EXPLAIN executes its own diagnostic query; it cannot be labeled the exact timed operation. Per-backend CPU/context switches and any sampling/auto_explain overhead remain separate from client measurements.
6. Run four routes (ordinary Fluent, hot Prepare, Host SQL, Dapper.AOT), then direct libpq/Npgsql only for unresolved attribution. Cover 1/32/100/1,000 rows, a byte-split case, and early stop. Decompose the existing 35-case mixed load by business case; retain dynamic filters, joins/aggregates, wide/JSON results, writes, and transactions.
7. Prioritize observing the row/batch result path, then actual metadata wait, then parameter encoding and query construction. This is an **observation order**, not a ranking of proven CPU hotspots. Select a product experiment only after the dual-database Plan table contains measured deltas. Revalidate causal CPU/bytes/wait change under interleaved same-machine A/B, then endpoint and contract behavior.

## Handoff conclusion

The PG source chain, fixed/row/batch/column work map, protocol-message distinction, historical counterexample, generated-reader limitations, and Go control limitations are now explicit. The remaining unknowns are precisely the stage CPU, actual blocking/wakeup timelines, allocation call sites and byte totals, backend plan/buffer/cost correlation, and matched ELF instructions. This source audit supports completing first-stage observability; it does not satisfy that stage or select a product refactor.
