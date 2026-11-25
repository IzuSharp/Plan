# DB-Perf-01 — allocation inventory at the fixed baseline

Source: Korda `771bc77cbd68d3f932b99ed2497c0697bbba5f02`, tree
`ddc4ec36cdade1749127fe5d50cbbf218b2878e6`. This is a source inventory and set of
measurement obligations, **not a public-provider allocation profile or a zero-byte
acceptance result**. The separately retained internal diagnostics below do not
close public-path measurement obligations. The same public-path inventory applies to
PostgreSQL and SQLite; provider-specific driver/transport costs must be measured
separately.

## Normal public-path inventory

| Stage / source | Observable allocation candidates | Required boundary and variants |
| --- | --- | --- |
| Fluent construction: `QueryContext`, `Query<TEntity>` | Query owners, dictionaries, expression/parameter collections, lambda captures and encoded control-record arrays | Dynamic construction charged per operation; distinguish prepared-plan creation from actual prepared reuse. Include optional clauses and wide joins. |
| Plan reuse/binding: `ParameterDefinition.Encode`, `PreparedQuery<T>` | Sorting/materializing parameter definitions and snapshots, rebuilding descriptors/shape metadata and encoded parameter payload | Warm prepared plan with varying values; empty/nonempty parameters; NULL, decimal and typed JSON. A cached plan does not by itself eliminate binding work. |
| Submit/complete: `DataSource.Start<T>` | Per-operation callbacks/captures, asynchronous operation/owner adapters and completion objects | Session open, query start, refill, writes and return; synchronous callback and genuinely delayed callback; concurrent submit/cancel/retire. |
| Async ownership: `AsyncOperationBase`, `AsyncOperation<TResult>` | `_retirement` and `_result` TaskCompletionSource objects, callback registration/rooting, continuation state | Whole-process counters including callback/thread-pool activity, result completion plus eventual retirement, and both success and cancellation. |
| Stream creation: `TypedStream<T>` constructor / enumerator | WireDescriptor array, configured-codec dictionary, shape conversion, empty encoded validation payload, enumerator/gate, linked cancellation owner when needed | Per query separate from row/refill cost; method token, enumeration token, both distinct tokens and no token. |
| Row advance: `TypedStream<T>.Enumerator.MoveNextAsync` | Baseline unconditionally constructs a TaskCompletionSource for each call, even when the next row is already buffered; `MoveAsync` and cleanup asynchronous state | Count each row plus end-of-stream call. Test in-batch synchronous completion, actual start/refill suspension, simultaneous dispose and prohibited concurrent MoveNext. |
| Native batch acquisition: `HostStreamTransport.FetchAsync`, `HostStreamBatch` | Fetch delegates, batch owner, `NativeBuffer.Copy` full managed byte-array copy | One fetch/batch, zero/one/many rows, narrow/wide payloads, bounded maximum bytes and concurrent consumers. Record native-to-managed copied bytes. |
| Wire validation: `DbWire.Parse` | Another `bytes.ToArray()` ownership copy plus range List/HashSet/validation structures | Per batch after transport copy; valid/corrupt envelopes, row/column bounds and ownership compensation. Preserving validation is mandatory. |
| Scalar validation: `DbWire` | UTF-8 `GetString` creates a temporary string during validation; decimal/JSON configuration parsing performs extra work | Per string/decimal/JSON cell; separate required owned DTO string from a validation-only temporary. Establish whether each code path allocates by measurement. |
| Decimal decoding: `DecimalBytes.Decode` in `Codecs.cs` | Canonicality check calls `Encode`, creating a 16-byte payload array in the baseline | Per non-NULL decimal value, signs/scales/limits, valid and rejected encodings; preserve canonical checks and errors. |
| Generated mapping: generator output / projection factories | Required DTO/reference/string/JSON results; temporary argument arrays, boxing or closures where emitted | Compare value-only projection with business DTO projection, narrow/wide records and nullable joins. Required result bytes are separately charged; framework temporaries stay framework-owned. |
| Buffering terminals: `ToListAsync`, `ToArrayAsync`, `First*`, `Single*` | Required list/array/result objects, intermediate buffers, returned Task and cleanup state | Per operation plus rows; classify a requested result container separately from unnecessary intermediate containers. Include absence and multi-row rejection cases separately. |
| Transactions and connection return | Session/transaction/close owners, completion objects, leases, registrations and pool growth | Begin/read/write/commit, explicit rollback, concurrency conflict, dispose, callback transaction overloads and eventual return. Separate committed business results from framework control objects. |
| Pool/wakeup and resource bounds | Preallocated owners versus growth, contention continuations, callback wakeups and native retained capacity | Warm bounded capacity, high concurrency, saturation, exhaustion, recovery and idle retention. Record capacity and cumulative growth, not only the final heap size. |

Source links:

- [TypedStream](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Streaming/TypedStream.cs)
- [HostStreamTransport](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/HostStreamTransport.cs)
- [DbWire](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/DbWire.cs)
- [Codecs](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/Codecs.cs)
- [QueryContext](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Fluent/QueryContext.cs)
- [Fluent terminals](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Fluent/Terminals.cs)
- [DataSource](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/DataSource.cs)
- [AsyncOperation](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Interop.Async/AsyncOperation.cs)

## Task-returning public API constraint

`DataSource.OpenSessionAsync`, `CanConnectAsync`, query `CountAsync`/`AnyAsync`
and the list/scalar terminals return `Task<T>`. A caller may retain and await a
Task after its operation has finished. The public contract offers no caller
release signal that permits resetting that Task for another operation, and a
Task's identity/result/completion are not resettable. In particular, returning a
fresh reference result after actual asynchronous suspension cannot be made
universally allocation-free by recycling a bounded Task object pool while
preserving those semantics. Baseline AsyncOperation already makes the ownership
cost explicit through two TaskCompletionSource fields.

This does not establish a numerical lower bound or imply every synchronous Task
return allocates: completed scalar results may have runtime caches, and individual
internal ValueTask paths may be allocation-free. It does establish why removing
the per-row waiter can succeed without making every public query zero bytes.
Do not silently replace Task with ValueTask, require callers to surrender retained
Tasks, or exclude framework completion state from the accounting to claim 0 B.
Record measured remaining completion costs as unmet paths, and record any
unestablished attribution as unproven.

## Required allocation receipt

Every measured path binds provider, source/package/executable/native hashes,
projection and parameter input, operation/batch/row counts, warmup, measured
boundary, whole-process cumulative allocated-byte start/end values, each GC
generation delta, actual suspended-operation count and concurrency. Preserve
raw integer totals, end-to-end bytes, attributed required business-result bytes,
attributed framework bytes and unresolved bytes before presenting normalized
rates. Include driver/control results and source-stack or isolation attribution.

For a claimed zero path, framework total must be exactly zero with no unresolved
bytes; zero samples, no GC, integer division, rounding or subtracting an unrelated
process are not proofs. Per-row 0 B must still show per-query and per-batch totals.
First initialization, errors, cancellation and exhausted pools are reported
separately without dropping them from correctness and resource ownership tests.

## Review order and correctness risks

1. Establish real out-of-tree AOT before measurements, then isolate the baseline
   row waiter with value-only projections and full-process counters.
2. Remove avoidable row/codec work only after preserving overlap rejection,
   cancellation, active-move/dispose coordination and eventual native retirement.
3. Examine batch copy ownership: a borrowed native span must never outlive its
   owner or cross an await; removing a copy must preserve corruption validation,
   bounded bytes and deterministic owner release.
4. Separate stable projection/parameter metadata from per-execution values,
   while preserving source/codec identity and concurrency isolation.
5. Validate improvements under actual asynchronous refill, mixed concurrent
   transactions and saturation; then inspect all remaining per-operation costs.

No candidate fix, regression threshold, byte saving or final zero-byte coverage
is accepted by this source review alone.

## Observed before diagnostics — internal transport only

The [raw index](checkpoints/before-internal/files.json),
[commands](checkpoints/before-internal/commands.json),
[production/binary identity](checkpoints/before-internal/manifest.json) and
[counter summary](checkpoints/before-internal/summary.json) preserve 30 successful
independent-process commands: three interleaved repeats of nine streaming/scalar
probe lanes and three separate exploratory scalar processes. The before manifest
records an empty production diff at the fixed main; test harness work and binary
hashes remain explicitly separate from that production source identity.

| Diagnostic lane, per process | Raw whole-process allocated bytes | Operations / rows | Boundary |
| --- | ---: | --- | --- |
| `sync-inbatch`, all three repeats | 23,063,040 | 64 windows / 262,080 rows | After each batch's first row through its last row; excludes stream creation, fetch, parsing and disposal. This is exactly 88 raw bytes per measured row. |
| `inbatch-control`, all three repeats | 0 | 64 windows / 262,080 rows | Matching empty in-batch control; this is not a public-provider result. |
| `stream-sync`, all three repeats | 24,584,456 | 64 queries / 131,072 rows | TypedStream construction, all fetches, enumeration, completion and cleanup; excludes synthetic payload creation. |
| `driver-sync`, all three repeats | 104 | 64 queries / 131,072 rows | Synthetic driver-only control, reported separately. |
| `stream-async`, repeats 0 / 1 / 2 | 24,731,504 / 24,736,680 / 24,736,680 | Each 64 queries / 131,072 rows | Each observes 576 actually incomplete moves/refills from one bounded worker. |
| `driver-async`, all three repeats | 55,560 | 64 queries / 131,072 rows | Driver-only actual asynchronous control; each observes 576 incomplete operations. |
| `utf8-validation`, all three repeats | 2,621,440 | 16,384 validations / no rows | Immutable scalar input and codec preparation excluded. |
| `decimal-validation`, all three repeats | 14,811,136 | 16,384 validations / no rows | Scalar validation, including its current configuration/codec work. |
| `scalar-control`, all three repeats | 0 | 16,384 iterations / no rows | Control only; does not establish a production zero path. |

The copied raw windows retain cumulative start/end counters and GC generation
deltas; each difference and sum was checked against its recorded total. All stream
diagnostics report zero live synthetic batches and pending completions after
drain. The value projection creates no business reference DTO/string/list output.
Raw totals still include any runtime/driver/harness activity inside the boundary;
separate driver totals are not silently subtracted to claim exact attribution.

The separate `scalar-*` exploratory probe retains a first empty-driver observation
of **672 bytes**. Its later zero observations and `ZeroRegression` category flag
do not erase that contamination or establish a zero pass. Keep the original bytes
and distinguish that probe from the streaming probe's isolated controls.

These data justify investigating the baseline row waiter and scalar validation.
They provide no actual PostgreSQL/SQLite public-provider zero-allocation
acceptance, direct C++ or independent ORM comparison, final-candidate performance
gain, business throughput/tail latency, or long-duration credit.
