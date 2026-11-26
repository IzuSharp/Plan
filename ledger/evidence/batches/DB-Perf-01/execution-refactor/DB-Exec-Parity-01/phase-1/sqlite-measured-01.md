# DB-Exec-Parity-01 — SQLite measured stage evidence, first matrix

## Decision supported by this evidence

The ordinary 1,000-row result does not expose a SQL execution-count or DTO-allocation explanation for Korda's CPU gap. Both frameworks execute the same ordered two-column query with the same parameters and equivalent engine work. Korda's additional work includes a native frame, repeated native and managed ownership/validation work, and a worker/readiness/continuation cycle per batch. The actual CPU sample concentration in `RhSpinWait`, the repeated runtime-spin sensitivity, and the measured batch-count isolation make completion/handoff frequency the leading **CPU** investigation. Separately, the SQLite prepare flag disables lookaside despite each cursor finalizing its statement; the new public-allocator measurements make that a high-value, narrowly isolatable **allocation** hypothesis.

This document records a completed SQLite diagnostic matrix, not an optimized product, final mixed-load acceptance, or a declaration that all remaining CPU is explained. Intrusive span costs below are expressly excluded from formal latency or parity claims. Product baseline remains `7ff7b57b907b689defb880b8af62d83679608603`; the instrumented worktree is local only. The root agent must combine this evidence with PostgreSQL, mixed-business observations, and the completion correctness review in Plan before changing product execution policy.

## Accepted run and artifact identity

All local paths are relative to `/workspace/scratch/34ddfdb91b5c/DB-Exec-Parity-01`.

The accepted matrix is [sqlite-native-diagnostic-02](../measurements/sqlite-native-diagnostic-02/runner.json): seven cases, each Korda Fluent/hot Prepare/Host SQL plus Dapper.AOT, eight measured requests per route after 64 warm requests per route. The fourteen processes ran serially on CPU affinity `0-3` in the exclusive local measurement lane. There are 28 measured route windows and 224 measured requests. Every process exited zero, checked all exposed DTO values, and all Korda ownership counters returned to zero. The wrapper and sampler report zero marker drops, kernel readback loss, emitted lost samples, ring overrun, malformed records, and clock/TID consistency errors; the largest process emitted 204,004 markers against a 1,048,576-record capacity. Commands, absolute RAW/MONOTONIC clocks, stdout, receipts, raw samples, markers, mappings and sampler manifests remain in that directory.

| Artifact | Identity |
| --- | --- |
| Ordinary baseline package, four AOT consumers and source binding | [sqlite-baseline-builds.md](sqlite-baseline-builds.md), [baseline identity inventory](../builds/baseline-sqlite/identity-01/baseline-identities.json) |
| Independent native diagnostic source commit | `8786e6ee62c49145ab25d2ef68b741d040a43ea8`, branch `task/DB-Exec-Parity-01-diagnostic-sqlite`; never intended for push/merge |
| Diagnostic standalone package | `Korda.Database.Sqlite.0.1.0-db-exec-parity-diag.1.nupkg`; SHA-256 `747cf7ff93a284f8378b26ac815caad6e0cfd6e88650fa0c1d46b83a3a196983` |
| Diagnostic Korda native image actually loaded | SHA-256 `956709a8246548c69ce505fd9df50060b542d29681885dd6c1a2dabbe3e0c9a0` |
| Diagnostic Korda AOT ELF | `consumers/diagnostic-sqlite-02/korda-query-phases/out/DbPerf.QueryPhases`; SHA-256 `f2d4617450d2a31d22c2bb843af9b8afb7b0013c81898d9588ac94467f8e0bd3` |
| Diagnostic Dapper AOT ELF | `consumers/diagnostic-sqlite-02/dapper-query-phases/out/DbPerf.DapperQueryPhases`; SHA-256 `9df550bdaf06a49166db90026205a880dda1c6e9760028755aee4faf0829bbf5` |
| Diagnostic Dapper SQLite image | SHA-256 `2ad87b0af5aa1531c6a863be153bd8e7730e6e5db5f0b69ff61b8ed008d3cfb7` |
| Accepted marker/sampler library | `diagnostics/native_sampler/builds/03/libparity_sampler.so`; SHA-256 `896c0c8514b4a7f3112a9701543786473aa0e04e8c0485c72f41d8427b302d15` |
| Parsed requests, counters and same-TID spans | [sqlite-measured-01.json](sqlite-measured-01.json), produced by [analyze_sqlite_native_matrix.py](analyze_sqlite_native_matrix.py); includes raw-file hashes |
| Exact optimized diagnostic native symbols, source/inline locations and machine calls | [diagnostic-identities.json](../builds/diagnostic-sqlite-02/identity-02/diagnostic-identities.json), produced by [inspect_sqlite_diagnostic.py](inspect_sqlite_diagnostic.py) |

Both diagnostic SQLite images use the locked 3.51.3 amalgamation and the real product engine compile recipe; the Dapper shared image's runtime source ID and compile options match the actual static engine archive. They retain different linkage and visibility, so this is not a claim of byte-identical machine images. C++ remains optimized Release with additional DWARF. The retained native build manifest, compile commands and image build receipt record exact commands. The two independent consumer `diagnostic-build-receipt.json` files bind actual generated C#, ELF/debug companions, package/assets and source-transform hashes. The consumer adaptation adds only the independent diagnostic surface: 32 rows, stop-after-one, the existing public batch-size setting, explicit identities and markers.

The first native diagnostic packaging attempt failed canonical inventory validation because a C17 wrapper had been put under the C++ inventory directory. The wrapper was moved to the already registered `native/database/diagnostics` path; no validator was weakened. The first runtime attempt is retained as `sqlite-native-diagnostic-01`: its consumer succeeded but sampler-manifest validation failed because the runner pre-created the sampler directory and preloaded `taskset`. The accepted runner applies the preload only to the consumer and supplies a nonexistent output directory. Neither failed attempt receives measurement credit.

## What the instrumentation covers

The engine translation unit renames the intercepted SQLite entry points; wrapper functions with the public names receive both Korda's static native callers and Dapper's shared-library callers. This explicitly covers the Korda hidden/static engine, where ordinary `LD_PRELOAD` SQLite interposition would be insufficient. The wrapper records actual external prepare/bind/step/column/reset/finalize calls and statement RUN/VM_STEP/REPREPARE/SORT/FULLSCAN deltas. Engine-internal calls are deliberately not counted as independent client API calls. Diagnostic-only `column_bytes` and `sqlite3_stmt_status` probes have separate counter identities and are not included as ordinary client work.

Native markers capture task admission/start/end, prepare, fetch/batch completion, readiness, take and close. Request identity and generation are explicitly restored for cursor work. Every marker has Linux TID, RAW, MONOTONIC and thread CPU. CPU differences are computed only within one TID; elapsed queue residence and ready-to-take are RAW differences across explicitly related events. They do not identify run-queue delay, wake source or a particular contended lock.

The batch markers count actual executed payload insert lengths, vector growth copies, finish memmoves, table zeroing, offset rewrites, per-column preflight and nonnull codec entries. A `column_text` byte length is a borrowed/exposed byte length, **not** a second proven copy. A codec result length is also not automatically an allocation or copy. TEXT is covered in this narrow query; no BLOB row occurs here. Public UTF-8 query entry points are covered; these wrappers do not yet cover every `sqlite3_exec`/internal control-statement or UTF-16 path needed to claim a complete 35-business engine-call census.

### Window-bound correction

Generic control-worker TLS scope can retain a prior request tag across an internal managed continuation. Filtering a whole-process trace solely by a request ID incorrectly charged a subsequent window's control work to the last prior request. The accepted analyzer uses explicit window RAW begin/end markers plus measured request IDs for SQL/batch events, and counts all complete native worker spans within each explicit window regardless of their stale generic tag. Per-request generic tags are retained as diagnostic context, not exclusive business ownership proof. The earlier request-only aggregate is retained as `sqlite-measured-01.request-scope-only.superseded.json`.

There are zero native worker spans crossing the accepted window boundaries and zero unmatched native prepare/batch span endpoints. Thus the window worker CPU totals include the observed complete worker spans without proration. Per-query SQL/batch counters are unchanged by this correction. Queue markers use a unique native task ID, and batch publication/take use the explicit request plus generation.

## Same business, actual engine work

The narrow DTO is `(Int64 Id, nullable string Note)`. Tenant alternates between 1 and 2. The one-row query binds the complete composite primary key; range queries use the same tenant plus upper Id bound and deterministic ordering. SQL and ordered parameter types are retained in the paired Korda/Dapper receipts. Dapper consumes the exact Korda SQL contract, with the explicit SQLite parameter-marker adaptation recorded by the driver.

The following are measured calls **per business request**, averaged over eight requests where tenant changes a VM count. Korda values are identical across its three construction routes.

| Case | Exposed rows K/D | Native rows K/D | Public prepare K/D | Int64 binds K/D | Step K/D | VM_STEP K/D | RUN K/D | REPREPARE K/D | Finalize K/D |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| PK 1, full | 1 / 1 | 1 / 1 | v3 1 / v2 1 | 2 / 2 | 2 / 2 | 17 / 17 | 1 / 1 | 0 / 0 | 1 / 1 |
| 32, full | 32 / 32 | 32 / 32 | v3 1 / v2 1 | 2 / 2 | 33 / 33 | 207 / 207 | 1 / 1 | 1 / 1 | 1 / 1 |
| 100, full | 100 / 100 | 100 / 100 | v3 1 / v2 1 | 2 / 2 | 101 / 101 | 615 / 615 | 1 / 1 | 1 / 1 | 1 / 1 |
| 1,000, full; any tested batch size | 1,000 / 1,000 | 1,000 / 1,000 | v3 1 / v2 1 | 2 / 2 | 1,001 / 1,001 | 6,014.5 / 6,014.5 | 1 / 1 | 1 / 1 | 1 / 1 |
| 1,000 query, stop after first DTO, B=32 | 1 / 1 | 32 / 1 | v3 1 / v2 1 | 2 / 2 | 32 / 1 | 204 / 18 | 1 / 1 | 1 / 1 | 1 / 1 |

Full reads have exactly one `SQLITE_DONE`; early-stop reads have none. Dapper calls reset once before finalize; Korda closes by finalizing directly. Korda's independent `SqlExecutions` delta is exactly eight in each eight-request route window. Pulls, worker tasks, SQL executions, SQLite API calls and FFI crossings are different counts. A SQLite wrapper entry is a managed/native transition for the SQLitePCLRaw call path, but an ordinary native/native call on Korda's side. This matrix does not claim a complete count of every Korda ABI entry/release or runtime reverse-P/Invoke transition.

The actual `REPREPARE=1` must not be concealed behind the single public prepare call. The locked amalgamation sets an affected statement's expiration bit when a planner-sensitive bound parameter changes (`sqlite3.c` around 94079–94090), and the statement recompilation path increments REPREPARE. These measurements are consistent with binding-sensitive automatic recompilation under the enabled STAT4 engine; no DDL was executed in these windows. The exact particular binding that triggers the recompile was not separately traced. The two tenant variants execute 6,014 and 6,015 VM instructions. Their equality across frameworks supplies a stronger engine-work check than API step count alone.

The physical-statement-cache assumption is now resolved for this path: Dapper's cached command still prepares/finalizes once per business, exactly as predicted by its actual machine call from `TryRecycleThreadStatic` to `SqliteCommand.set_Connection(null)` and prepared-statement disposal. Korda hot Prepare also reuses a logical query rather than the engine statement. A statement cache could improve either path, but an unequal prepare count is not the measured cause here.

### Dynamic type and value reads

For 1,000 rows, Korda makes 4,000 `sqlite3_column_type` calls against Dapper's 2,802. Korda executes 2,000 preflight column checks and then repeats the storage-class read during decoding. Both make 1,000 int64 reads and 800 text/byte-length reads, exposing 7,912 UTF-8 text bytes. Korda enters 1,800 nonnull codecs. Its one column-count read and two name/two declared-type reads contrast with Dapper's 204 column-count and two name reads. The Dapper column-count pattern includes provider null/ordinal checking; do not assume every driver operation is cheaper.

The type-call differences for 1/32/100 rows are 4/5, 128/92 and 400/282 respectively. The early-stop case is 128/5 because Korda validates the fetched 32-row batch before exposing one row. The count differences are established; exclusive CPU saved by removing any one validation has not been measured. Full-row shape validation before an earlier field's conversion error is an existing contract, so simply deleting preflight would change observable error ordering.

## Batch-size isolation, copies, and thread timeline

These three cases execute the same 1,000-row SQL with the same VM counts, scalar reads and exposed bytes. Only the existing public batch-row option changes. Dapper has no corresponding NWDB batch knob; its three repeated controls have identical engine counters.

| Measured Korda hot Prepare per request | B=32 | B=128 | B=256 |
| --- | ---: | ---: | ---: |
| Native batches / worker tasks | 32 / 34 | 8 / 10 | 4 / 6 |
| Engine rows / steps | 1,000 / 1,001 | 1,000 / 1,001 | 1,000 / 1,001 |
| Native cancel installs / detach calls | 1,002 / 97 | 1,002 / 25 | 1,002 / 13 |
| CallContext checks / preflight columns | 1,003 / 2,000 | 1,003 / 2,000 | 1,003 / 2,000 |
| Nonnull codec entries / finish scanned cells | 1,800 / 2,000 | 1,800 / 2,000 | 1,800 / 2,000 |
| Canonical payload inserted/copied | 15,912 B | 15,912 B | 15,912 B |
| Vector growth count / copied prior bytes | 0 / 0 B | 8 / 58,352 B | 4 / 53,752 B |
| Finish payload memmove | 124 B | 1,662 B | 3,706 B |
| Descriptor/cell table zero bytes | 53,248 B | 50,176 B | 49,664 B |
| Nonnull offset rewrite stores | 1,800 / 14,400 B | 1,800 / 14,400 B | 1,800 / 14,400 B |
| Emitted total native frame bytes | 68,008 B | 64,936 B | 64,424 B |
| Covered native worker CPU, intrusive | 1,689.344 µs | 830.426 µs | 603.118 µs |
| Nested native fetch/batch CPU, intrusive | 1,023.216 µs | 659.738 µs | 501.823 µs |
| Pull admission → worker begin, median | 36.309 µs | 28.493 µs | 16.455 µs |
| Native ready → managed take entry, median | 28.143 µs | 24.801 µs | 25.701 µs |
| Take → next batch admission, median | 16.855 µs | 45.148 µs | 61.357 µs |

The 15,912 payload bytes contain 8,000 fixed-width integer bytes plus the 7,912 UTF-8 bytes. They are an additional canonical frame representation before the final managed DTO/string representation. Frame payload insert, vector growth copy, finish memmove, zero-fill and offset stores are distinct operations; adding the exposed `column_text` bytes again would double-count a borrowed view. None of these counts includes every engine or managed string/list copy. The larger batch settings reduce handoffs but provoke buffer growth copies, so a blanket batch-size increase has a measurable resource tradeoff.

The intrusive native worker totals include added marker calls, counter flushing and a diagnostic function wrapper; fetch CPU is nested within worker CPU and must not be added to it. Queue residence includes workqueue/worker scheduling and the diagnostic admission machinery. Ready-to-take includes the notification/managed coordination path; it is not a measured OS wake latency. Take-to-next-admission includes batch validation, row materialization, application loop work and release/request operations, and is not pure mapper CPU. One B=32 hot-Prepare observation has managed take preceding the end of the native worker's notification tail by 195.515 µs. Consequently, even these coarse stages can overlap; their summed elapsed times are not a valid end-to-end partition.

The exact-full 32-row case produces two batches `[32, 0]`, four native worker tasks and 33 engine steps. Its second empty pull observes EOF; it does not execute a second SQL statement. The 100-row case uses four batches and six native worker tasks. The one-row full case uses one batch and three tasks. The early-stop case uses one 32-row native batch, three tasks and a close without draining the remaining 968 rows. It copies 482 canonical payload bytes and validates 64 cells even though the business accepts one DTO. This makes early-stop overfetch a real design tradeoff, not a basis for claiming equal engine cost from equal exposed row count.

## Relation to ordinary CPU and allocation evidence

The independent ordinary phase baseline gives Korda hot Prepare 3,754.876 µs process CPU/request, service p50 1,720.626 µs and 80,612.031 B managed allocation at 1,000 rows, versus Dapper 426.741 µs, 371.670 µs and 79,810.188 B. The process CPU ratio is 8.80 while the extra managed allocation is 801.844 B. Host SQL process CPU is similar to hot Prepare. Those uninstrumented short windows remain distinct from the native matrix and from final 30-minute acceptance. [Ordinary summary](../measurements/phase-baseline-01/sqlite-summary.json)

Actual warm-window leaf sampling attributes 59.43% of Korda hot Prepare samples to `RhSpinWait`, against zero Dapper SQLite samples there. Two same-ELF, uninstrumented runtime-setting comparisons reduce Korda CPU by approximately 1.57–1.77 ms/request when the ThreadPool semaphore spin setting is zero, with service p50 remaining near its original range. This causally establishes sensitivity to that runtime setting; it does not establish that every sampled spin came from that semaphore or that the saved CPU shortens the request's critical path. The real runtime static caller graph also contains lock-related callers. Native queue/readiness evidence above strengthens the case for reducing unnecessary handoffs, without authorizing a global runtime setting as the product solution. [Sampler and sensitivity evidence](native-sampler-findings-01.md)

The actual generated-mapper allocation observer measures **69,760 B** in mapper calls and **8,056 B** in the result-list constructor for both frameworks at 1,000 rows. The prepared whole-process managed allocation difference in that separate diagnostic is 818.625 B/request. Mapper scopes can contain driver/codec scratch, and these numbers do not establish framework-only allocation. They do establish that rewriting DTO/list construction cannot explain most of the observed CPU gap. [Allocation matrix](allocation-baseline-01.json)

The same allocation matrix's separate public-native-allocator observer reports the following 128-business warm windows. These are original mixed-business 32-row cases, not the 1,000-row phase matrix and not isolated SQLite allocator call stacks.

| Business | Korda public allocation calls / requested bytes per operation | Dapper calls / requested bytes per operation |
| --- | ---: | ---: |
| Numeric | 162.039 / 22,601.563 B | 0.188 / 133.813 B |
| Text | 185.039 / 26,361.563 B | 0.211 / 103.000 B |
| Wide | 1,234.039 / 88,489.563 B | 30.180 / 10,612.188 B |

The public allocator sees process/runtime/native-host/SQLite activity that passes those entry points; it does not count every logical allocation served from an already allocated SQLite lookaside slot. Very few Dapper public allocations therefore do not mean no driver allocation or no resource use. No subtraction in this table is labeled framework-only.

There is a precise source-backed hypothesis for part of this disparity: Korda `ProviderConnection::prepare` passes `SQLITE_PREPARE_PERSISTENT`, and the locked engine's `sqlite3Prepare` condition disables lookaside while preparing that statement (`sqlite3.c` around 146405). Dapper's v2 path uses no such public flag. Both measured phase paths finalize each business, so the long-lived-statement hint does not match this cursor lifetime. The isolated experiment should keep `sqlite3_prepare_v3`, SQL bytes, tail validation and lifetime unchanged and vary only `prepFlags=0`. The exact locked v2/v3 implementations retain `SQLITE_PREPARE_SAVESQL` and document v2 equivalence to v3 with zero flags, preserving automatic schema reprepare. Actual lookaside HIT/MISS_SIZE/MISS_FULL counters or allocation call-site sampling are still needed to quantify how much of the public allocator gap this flag causes; the current malloc delta alone cannot prove it.

This is also present in the actual diagnostic machine code: `ProviderConnection::prepare` at module-relative `0x9676e` loads flag `1` into `%ecx` and calls `sqlite3_prepare_v3` at `0x96773`; `sqlite3Prepare` at `0x165ab7` tests that flag, then updates the lookaside disable count and zeroes the usable slot size. The retained disassemblies bind those instructions to the exact diagnostic provider and locked amalgamation lines. This proves the selected branch exists in the executed image; it does not by itself measure its allocation or CPU impact.

## Source, generated code and actual-machine stage table

Native names below are present in the actual diagnostic ELF, with optimized source/inline call-site and machine excerpts in the diagnostic identity inventory. Ordinary AOT generated readers, Dapper factory calls and symbols are bound in the baseline identity inventory. Microsoft.Data.Sqlite methods in these inputs lack reliable own sequence points; a preceding generated-file line returned by `addr2line` is explicitly rejected. Ordinary native Release has symbols but no DWARF; the diagnostic image supplies source/inline correspondence without replacing the ordinary measured identity.

| Business stage | Both implementations / actual symbols and generated source | Measured repetition or difference | Correctness contract and next step |
| --- | --- | --- | --- |
| Query construction/reuse | Korda `Terminals.cs`, `QueryContext.cs`, actual `PhaseRow.*.Projection.g.cs`; Dapper actual interceptor and `CommandFactory.TryRecycleThreadStatic` | Three Korda lanes have identical native counts; hot Prepare/Host SQL ordinary CPU remain close | Preserve snapshot values and query reuse. Construction is not the first thousand-row execution target. |
| Prepare/bind | Native `ProviderConnection::prepare`; Dapper generated factory → `SqliteCommand.PrepareAndEnumerateStatements` → SQLitePCLRaw → actual `sqlite3_prepare_v2` | One physical prepare, two int64 binds, one finalize each; v3 PERSISTENT versus v2 zero flags; reprepare one for ranges | Isolate flags=0 plus allocator/lookaside counts; preserve SQL tail validation, metadata/error timing and DDL. Do not introduce caching simultaneously. |
| Engine advancement | `ProviderStatement::Impl::advance`; `SqliteDataReader.NextResult`, `SqliteDataRecord.Read` → wrapper `sqlite3_step` | Same 1,001 calls and VM counts for full 1,000 rows; Korda 1,002 cancel installs and 1,003 context checks | Later isolate per-advance cancellation/clock work. Preserve cancel-generation safety, deadline checks and no hidden execution before fetch. |
| Type/scalar reads | `ProviderStatement::preflight_row`, `sqlite_decode_into`; generated Dapper row factory → typed record getters | 4,000 versus 2,802 type calls; equal 1,000 int64/800 text reads; Korda 2,000 preflight columns, 1,800 codecs | Do not remove late-column shape/error precedence. Measure selected decoder/validation candidate CPU separately. |
| Native frame | `BatchWriter::append_validated`, `BatchWriter::finish`; Dapper reads typed values directly into its generated DTO | 15,912 payload copy B, 2,000 finish cell scans, 1,800 offset stores; growth and zeroing quantified by B above | Preserve wire bounds, byte-limited lookahead/error ordering and ownership. Avoid copying a borrowed engine view beyond its lifetime. |
| Queue/ready/take | `WorkerPool::post`, `CursorPull::request/run/complete/take`; C# `HostPullController`, completion coordination; Dapper SQLite synchronous provider work | 32/8/4 pulls and 34/10/6 worker jobs for B32/128/256; measured per-handoff gaps; ordinary RhSpinWait sensitivity | First CPU candidate: reduce redundant completion/continuation handoffs after the separate retirement/reentrancy review. Keep callback tails, registration roots and native notification lifetime safe. |
| Managed batch/DTO | `RowBatchLease.Attach`/`DbWire.Validate`, `TypedStream`, `RowReader`, generated projection; generated Dapper `RowFactory.Read` | Actual mapper 69,760 B and List 8,056 B equal; exclusive managed validation/lock CPU not yet isolated | Preserve borrowed lease lifetime, concurrent Dispose, custom codec exceptions and input validity. No blanket lock removal. |
| EOF/close/return | `Cursor::fetch/retire_provider`, `CursorPull` close and `HostCursorCloseController`; Dapper reader reset then command recycle/finalize | 32 exact rows need empty EOF batch; early stop engine advancement 32 versus 1; ownership counters drain to zero | Preserve no-drain early close, safe return, cancellation and error order. Increasing default B would change overfetch and is not accepted from this diagnostic. |

Exact source implementation references are in [sqlite-audit.md](sqlite-audit.md), with actual restore/source binding superseded by [sqlite-baseline-builds.md](sqlite-baseline-builds.md). `tests/Data.NativeHost/BatchResultTests.cs` already specifies full 0/1/32/64/100/1000 batch counts; native `streaming_tests.cpp` and SQLite fixtures specify dynamic-shape/error order, byte-full lookahead, metadata-first execution, early close and cancellation generation isolation. The matrix's success validates its business oracle and owner drain; it is not a rerun of all those race/error regressions.

## Priority and remaining unknowns

1. **Largest demonstrated CPU opportunity: completion/handoff policy.** Same SQL work, 32 repeated handoffs, actual spin leaf concentration and same-ELF spin sensitivity support this priority. Use the separate common completion review to choose one safe publication/continuation change, then use default-runtime, uninstrumented interleaved A/B plus request timeline counts. Require the proposed handoff count/CPU to actually fall. Never let inline continuation run before its prior generation's roots, control users, callback state and notification tail are safe.
2. **Small, independent resource experiment: prepare flags only.** The public-allocation disparity and exact engine branch justify a flags=0 candidate. It can be evaluated as the first narrow implementation experiment while the more complex completion ownership review is completed, but its CPU impact must be measured rather than assumed to explain the 8.80× gap. Keep allocation attribution at process scope until lookaside or call-site evidence resolves it.
3. **Next measured repeated work: per-row cancellation/type/codec and per-batch frame scans.** Counts are established; exclusive CPU and the safe replaceable portion remain unknown. Native worker/batch spans are nested and intrusive. Prefer eliminating repeated setup or combining a contract-preserving batch validation over dropping correctness checks.
4. **Do not accept larger default batches or a physical statement cache from these results alone.** Larger batches trade fewer handoffs for growth copies and early-stop overfetch. A physical cache changes DDL, parameter snapshot/reset and error lifecycle; both current paths already prepare once per business. Evaluate only after the preceding demonstrated costs and their contract gates.

Still unknown here are a complete attribution of every native allocator call, kernel wake/run-queue/lock causes, exact FFI totals for all ownership operations, CPU exclusive to each managed validation/codec/monitor, and instrumented engine/copy counts for every wide/JSON/write/transaction business. The mixed-business ordinary and allocator matrices add breadth but do not retrospectively provide those missing call sites. The Go comparison and PostgreSQL protocol/server evidence belong to their separately retained reports. No final throughput, rejection knee, RSS-release or 30-minute four-cell acceptance claim is made by this first matrix.
