# DB-Perf-01 managed allocation source audit

## Evidence status and fixed input

**Status: source-only / unmeasured.** This is a source inventory and a set of measurement hypotheses, not a benchmark result, allocation attribution result, optimization acceptance, or whole-framework zero-allocation claim. No production change or performance run was made as part of this audit. All per-operation, per-batch, per-row, CPU, and retained-memory quantities remain **unmeasured**.

- Product repository: [IzuSharp/Korda](https://github.com/IzuSharp/Korda).
- Fixed product commit: [`771bc77cbd68d3f932b99ed2497c0697bbba5f02`](https://github.com/IzuSharp/Korda/commit/771bc77cbd68d3f932b99ed2497c0697bbba5f02), the DB-Rename-01 / PR 36 merge observed on `main` through the GitHub connector.
- Product branch: `task/DB-Perf-01-linux`.
- Current task worktree: `/workspace/scratch/754bc732518e/Korda-DB-Perf-01-linux`.
- Scope: the managed paths used by both PostgreSQL and SQLite through the public Fluent ORM, generated mapping, and Native AOT consumer. Provider-native work, public-package execution, and workload results need separate evidence.
- Instructions read: the fixed commit's [AGENTS.md][agents], including direct Native AOT consumers, affected-module checks, independent top-level package verification, and public naming compatibility.

An explicit allocation site establishes a source-level allocation obligation in the current implementation. It does not establish an exact byte count, frequency in a particular workload, dominance over another cost, or a performance improvement. Runtime caches, compiler transformations, asynchronous completion timing, and application output shapes must be resolved by the measured consumer.

## Normal-operation inventory

All rows below have status **source-only / unmeasured**. "Per operation" means the stated operation, not necessarily one SQL execution or one physical network round trip. A single business request can execute several native operations and consume several batches.

| ID | Boundary | Fixed source and lines | Source observation and accounting |
| --- | --- | --- | --- |
| A01 | Dynamic query creation | [QueryContext.cs:12-30][query-create] | A query context owns parameter and projection dictionaries and a cancellation source. Query binding and native owner wrappers have separate lifetimes. Charge creation to each dynamic query; explicit prepared-plan setup is measured separately. |
| A02 | Dynamic expressions and clauses | [QueryContext.cs:31-90][query-compose]; [OperandEncoding.cs:11-41][operand] | Capturing composition lambdas, control-field records, field arrays, per-field byte arrays, and combined control records appear along the normal path. Literal values are encoded into a value array and then into the wire record. Do not assign one universal object count to all expressions. |
| A03 | Generated Fluent projection binding | [ModelGenerator.cs:173-225][generator]; [ProjectionDefinition.cs:10-55][projection-definition] | Generated `Bind` creates a query-scoped builder. Its definition owns a token-identity object, two lists and an alias set, then freezes fields, expression references, canonical projection bytes and a hash. The current generated materializer is **static** and reads by ordinal; it does not capture column tokens. |
| A04 | Static generated row mapping | [ModelGenerator.cs:184-203][generator-static]; [Rows.cs:166-191][projection-shape] | Generated `Row` is a static initialized projection. Its creation and canonical metadata belong to initialization, not every subsequent read. User DTO construction inside its materializer is accounted as required business output. |
| A05 | Projection registration | [DataSource.cs:159-163][projection-register]; [MetadataBindings.cs:18-23][metadata-projection]; [OperandEncoding.cs:24-36][projection-encoding] | The managed registration path serializes projection metadata on every call; no managed projection-registration cache appears here. Serialization creates a stream/writer, field lists and records, field arrays, final payload arrays and a decoded shape hash. Native deduplication, if present, does not remove this managed preparation. |
| A06 | Explicit prepared plan setup and reuse | [Terminals.cs:117-156][prepared] | `Prepare` freezes the plan, codecs, projection ID and sorted parameter definitions. Each later execution still calls parameter encoding and constructs a typed stream and execution factory. Plan reuse must not be reported as allocation-free execution. |
| A07 | Parameter set and execution snapshot | [Projections.cs:193-222][parameters]; [QueryContext.cs:186-206][parameter-encoding] | `Set` encodes the value into owned bytes and creates a parameter snapshot record. Execution sorts/copies parameter snapshots and definitions, creates cell/descriptor arrays, builds canonical parameter JSON, encodes it as UTF-8, hashes it, and emits a complete wire buffer. Reusing the parameter-set object does not remove these sites. |
| A08 | Typed stream creation | [TypedStream.cs:19-45][stream-create] | A descriptor array, descriptor records, configured-codec dictionary, decoded shape hash and expectation are created. An empty encoded wire buffer is also built to check row-descriptor capacity. Its expectation validation has additional collection work. |
| A09 | Enumerator creation | [TypedStream.cs:97-123][enumerator] | The one-shot enumerator and its gate are new objects. A linked cancellation source is conditional on two distinct cancelable tokens. No query object or stream may be silently reused with a new identity. |
| A10 | Every row advance, including a buffered row | [TypedStream.cs:125-135,187-190][move] | `MoveNextAsync` unconditionally creates a `TaskCompletionSource` and its associated task for `_activeMove`. This occurs even when mapping the next row from an existing batch completes synchronously. The final `false` call also enters this path. |
| A11 | Truly suspended row advance | [TypedStream.cs:137-190][move-body] | `MoveAsync` returns `Task<bool>` and can suspend at start, fetch, or cleanup. Suspended state and task costs need separate measurement. A synchronously completed async `Task<bool>` can use runtime result caching; do not assert that this returned task allocates anew for every buffered row. The explicit A10 completion source remains a separate site. |
| A12 | Batch submission and completion | [HostStreamTransport.cs:14-24][host-fetch]; [DataSource.cs:65-87][operation] | Fetch constructs delegate-based native create/take operations and uses the common managed asynchronous bridge. Each received batch also has a native-buffer wrapper and a host-batch wrapper. These costs are charged per fetch, including an end batch where applicable. |
| A13 | Batch copying | [NativeHost.cs:30-47][native-copy]; [HostStreamTransport.cs:26-38][host-batch]; [StreamTransport.cs:43-66][row-batch]; [DbWire.cs:57-95][wire-parse] | Native bytes are first copied into the host batch's managed array. `DbWire.Parse` then makes a second `bytes.ToArray()` copy. The host batch retains the first array and native owner while the parsed wire retains the second array. Measure both managed copies and retained native bytes. |
| A14 | Batch wire validation | [DbWire.cs:57-126][wire-validation] | Parsing creates a `DbWire`, a list of nonempty cell ranges and its backing storage, and expectation-validation descriptor-ID set storage. Ranges are sorted and checked for overlap. Row count, shape, profile, codecs, limits and malformed-input rejection must survive any optimization. |
| A15 | String cells | [DbWire.cs:128-153][scalar-validation]; [Codecs.cs:96-108][primitive-codecs] | Wire validation calls strict UTF-8 `GetString` and discards the returned string. Actual string materialization decodes again. The discarded validation string is framework overhead; the returned DTO string is required business output. |
| A16 | Typed JSON cells | [DbWire.cs:148-152][json-validation]; [Codecs.cs:180-188][json-codec] | Validation contains a discarded UTF-8 string, a temporary BOM-check array, a payload copy, and a `JsonDocument`. Typed deserialization then produces the actual business value. Separate validation temporaries from business JSON result objects and serializer overhead; do not assume the latter is allocation-free. |
| A17 | Configured decimal and money validation | [DbWire.cs:128-153,165-180][configured-validation]; [Codecs.cs:126-141][configured-codecs] | Descriptor/cell validation parses codec JSON. It also reconstructs a codec through `Codecs.Decimal` or `FixedScaleMoney` to compare canonical configuration, introducing codec/descriptor/delegate/configuration work. Decimal fit validation parses configuration again. |
| A18 | Decimal canonical decoding | [Codecs.cs:237-269][decimal] | `Decode` calls `Encode(value)` to check canonical bytes, allocating a 16-byte array. Parts, scaling and precision checks use `BigInteger`; associated backing storage depends on the value. Large coefficients and scale/precision edges require their own measurements. |
| A19 | Primitive row mapping and synchronous pointer leases | [Rows.cs:198-209][projection-read]; [Codecs.cs:96-120][primitive-codecs]; [Owners.cs:35-57][owner-lease]; [NativeResourceOwner.cs:55-103][resource-lease] | `RowReader`/`OwnerLease` are value/ref-struct mechanisms and ordinary primitive decode paths have no explicit result-object allocation. Native-resource acquisition uses a caller-local Boolean. These observations identify isolation candidates; they are **not measured zero-byte results**. Do not invent a heap lease per borrow. |
| A20 | Each native asynchronous operation | [DataSource.cs:65-87][operation]; [AsyncOperation.cs:32-105][async-base]; [AsyncOperation.cs:577-598][async-result] | Creation allocates an operation handle, resource owner, async operation, gates, result completion source/task and retirement completion source/task. The operation holds a GC handle and coordinator slot until retirement. `DataSource.Complete` can add suspended async state while joining both completion and retirement. Open, execute, fetch, close and transaction controls all use this bridge. |
| A21 | Stream retirement | [TypedStream.cs:192-243][stream-cleanup] | The first cleanup creates another completion source/task. Registration drain, native stop/join, failure preservation and linked-token disposal are separate from obtaining the final row. Disposal must remain part of the operation boundary. |
| A22 | Session open and return | [DataSource.cs:95-102][session-open]; [DataSession.cs:10-17,132-139][session-lifetime]; [DataSource.cs:167-220][close-controller] | Opening returns a new session and owner with a close controller. Closing obtains snapshots and can create another asynchronous native operation, completion wrappers and cleanup observations. A returned physical connection does not imply that the managed session wrapper may be reused under an old public reference. |
| A23 | Transaction begin and control | [DataSession.cs:106-124][transaction-begin]; [DataTransaction.cs:48-96][transaction-control]; [HostTransactionTransport.cs:20-50][transaction-host] | Default options, encoded control records, owners/transports/transaction wrappers, gates, savepoint storage and initial snapshots are created at begin. Commit and rollback dispatch through captured actions, the common operation bridge and snapshot parsing. Commit also refreshes native state in `finally`. |
| A24 | Snapshot/diagnostic observation | [DataTransaction.cs:54-63][transaction-observation]; [HostTransactionTransport.cs:25-26][transaction-snapshot]; [NativeHost.cs:121-125][native-snapshot]; [HostEncoding.cs:37-62][snapshot-decoding]; [TransactionValues.cs:65-74][close-result] | Reading transaction state/outcome/cleanup can itself perform a native snapshot, allocate a buffer wrapper and managed copy, a dictionary and one array per control field, and a `DatabaseCloseResult` record class. Provider-code decoding can create a string. Repeated sampling inside allocation boundaries would contaminate the measurement. |
| A25 | Buffered list result | [TypedStream.cs:55-61][buffer] | The list requested by `ToListAsync`, including necessary result storage, is business output. Enumerator, task, wire and safety costs stay in the framework column. Record capacity growth and final unused capacity instead of hiding them in one bytes-per-row average. |
| A26 | Buffered array result | [TypedStream.cs:63-64][array] | `ToArrayAsync` first materializes a list and then copies it to an array. When the requested business output is the array, that final array is business output; the intermediate list and its backing arrays are framework temporaries. |

The common host/stream/wire paths apply to both providers. Codec capabilities and actual native completion timing differ, so PostgreSQL evidence cannot substitute for SQLite evidence or vice versa.

## Completion mode, concurrency and non-normal paths

### Synchronous completion versus a real suspension

Measure at least two distinct row boundaries: mapping within an already received batch and crossing a fetch boundary that actually suspends. A driver or fixture that always returns an already-completed task cannot validate allocation behavior on callback/worker-thread completion. The existing bridge publishes a result and a retirement signal separately; timing can determine how many async methods suspend. Preserve both boundaries when attributing costs. [Sources: stream movement][move-body], [operation join][operation], [result publication and retirement][async-retire].

### High concurrency

The source allows concurrent independent session opens; one session retains fail-fast command admission and a cursor keeps that session busy. The enumerator rejects overlapping `MoveNextAsync`. The source and coordinator gates, callback slots, cancellation registration drain, real native ownership and the caller's retained tasks must be included in concurrency tests. Pooling an object while an older task, cancellation callback, public session reference or cleanup observer can still access it changes safety semantics. [Sources: source/session contracts][session-contract], [enumerator admission][move], [operation retirement][async-retire], [bounded callback slots][callback].

Thread-pool scheduling already queues the operation as an `IThreadPoolWorkItem`; there is no explicit per-queue closure wrapper in that call. Runtime queue growth, worker creation and scheduler costs remain unmeasured. [Source: CallbackCoordinator.cs:78-103][callback-scheduler].

### Separate reporting categories

| Category | Keep outside the normal-success allocation number, but report separately | Source basis |
| --- | --- | --- |
| Initialization | Module loading/negotiation, source resources, model and codec registration, static generated metadata, first thread-pool/callback infrastructure use. State what warmup actually exercised. | [DataSource.cs:28-44,138-163][source-init]; [generated static mapping][generator-static] |
| Exception/mapping failure | Failure exceptions, copied native diagnostics, cleanup exceptions retained in `Exception.Data`, JSON conversion failures and malformed wire rejection. Never suppress these to reduce allocations. | [TypedStream.cs:180-185][move-body]; [HostAsyncCalls.MapFailure][failure] |
| Cancellation | Pre-canceled calls, accepted native cancellation, linked method/enumeration tokens, draining cancellation registrations, and early enumeration termination. Early enumeration termination also needs a normal-success cleanup measurement where the API permits it. | [TypedStream lifecycle][stream-cleanup]; [AsyncOperation cancellation registration][async-registration] |
| Pool/coordinator exhaustion | Rejection, waiter capacity, finite operation cleanup slots, native pool saturation, and recovery to steady state. The precise native pool policy requires provider evidence. | [CallbackCoordinator.cs:27-40][callback]; [DataSource resource capacity][source-init] |
| Explicit finite cleanup wait | Timeout tasks and exceptions, a `Pending` observation, and subsequent actual retirement. Expiration is not evidence of resource release. | [DataSource.cs:208-220][close-wait] |
| Savepoints and compound operations | Savepoint wrapper/storage, bulk ownership leases, and nested control operations, measured as their own workload paths rather than silently included in a simple transaction result. | [DataTransaction.cs:18-45,85-96][transaction-control]; [HostTransactionTransport.cs:51-79][savepoints] |

No category in this table has measured allocation totals in this audit.

## Idle CPU and bounded retention hypotheses

The callback coordinator constructs a periodic timer with a default **10 ms** interval. Its retry loop scans the entire fixed slot array and acquires the reservation gate per slot, even when there are no occupied slots. It stops the timer only when closure and retirement permit disposal. The source sets capacity from `MaxQueryNodes + MaxConnections + MaxWaiters + 2`. This is a concrete candidate for the required idle-CPU experiment, **not a measured CPU hotspot**. [Coordinator source][callback]; [capacity calculation][source-init].

A fixed bound is not proof that the bound is inexpensive. Record configured slot capacity, occupied slots, native pool limits, managed array capacities, live batch bytes, native batch ownership, peak RSS/PSS where available, and retention after drain. The two batch copies in A13 and the native byte permit must all remain visible in this accounting. Do not replace their cost with an unbounded global cache or move it into native memory and call the result a whole-framework improvement.

Keep repeated `State`/`Outcome`/`Cleanup` observations out of the allocation window unless diagnostic overhead is explicitly included. A24 shows that the observation itself creates framework data. Take required owner and persistence snapshots outside the counter boundary, or run a separate observation-cost control.

## Public-contract boundary for a zero-byte objective

The current public API exposes independently retained `Task<T>` results, one-shot streams, class-based sessions/transactions, and immutable cleanup observations. The corresponding implementations are visible in [query terminals][prepared], [session ownership][session-contract], [transaction ownership][transaction-control] and [cleanup observations][close-result]. Existing Task results can outlive a caller's first await; existing disposed owner references must not acquire new underlying ownership through object reuse.

This leads to the following design constraint, not a byte-count claim:

- Reducing row, batch, parameter and internal completion allocations while retaining these contracts is ordinary optimization.
- A reusable internal completion source requires a proven point at which every prior continuation, cancellation registration and native callback has retired. It must not reset a task already published to an arbitrary caller.
- Reusing a public session or transaction object so that an old reference begins operating on a new lease would change ownership and disposal semantics.
- Returning a new public `ValueTask`/reusable-execution contract, exposing a different streaming API, weakening cleanup, or excluding framework wrappers from accounting cannot be presented as an allocation improvement of the unchanged public API. Any justified public contract addition must be separately designed, documented and compared while the original entry remains measured.
- Exact all-path zero-byte acceptance cannot be inferred from eliminating A10 or observing a primitive row-read fast path. Remaining per-query, per-batch, transaction, admission and cleanup costs must stay marked unmeasured or not achieved until their own evidence exists.

This audit does not declare universal zero allocation impossible, achieved, or disproved by a benchmark. It identifies source-level obligations and contract restrictions that a valid implementation and measurement must address.

## Candidate experiments, after the public-package baseline

These are proposals only. None has been implemented or measured by this audit.

| Priority | Small experiment | Required semantic guard |
| --- | --- | --- |
| 1 | Remove the unconditional per-Move completion source; create a join waiter only when concurrent disposal actually needs one. Consider a `ValueTask<bool>` internal move body. | Preserve overlapping-Move rejection, disposal waiting for an active move, exception cleanup, one-shot enumeration, token identity, and batch lifetime. Compare buffered-row and truly suspended boundaries independently. |
| 2 | Validate strict UTF-8 without constructing a discarded string. | Keep malformed-input rejection and actual returned string ownership unchanged. Measure narrow and wide string DTOs. |
| 3 | Add an internal parse path over already owned immutable batch memory to avoid the second copy. | Do not delete the existing copy guarantee for a general borrowed `ReadOnlySpan<byte>` input. Keep the host batch owner alive, invalidate readers on disposal, and do not retain a native borrowed span across await. |
| 4 | Decode fixed transaction/cleanup control fields directly from a validated span. | Preserve version/type/range checks, strictly ordered IDs, required fields, full consumption, enum bounds and immutable public observations. |
| 5 | Freeze prepared parameter descriptors, order and metadata hashes at preparation. | Freeze submitted values before the first await, keep later `Set` independent of accepted work, support separate concurrent sessions, and cap retained storage. |
| 6 | Eliminate repeated temporary JSON/configuration validation objects and decimal re-encoding. | Preserve one JSON root, depth/BOM/UTF-8 rules, decimal precision/scale/canonical representation, and malformed-input behavior. Test large and boundary values separately. |
| 7 | Reduce empty callback-slot scanning. | Preserve reserve/release/retry wakeups and bounded cleanup even after scheduling rejection. Measure idle CPU before considering timer lifecycle changes. |

An experiment is retained only after a matching binary/workload/environment comparison shows a repeatable improvement and correctness/ownership checks pass. Small measurements cannot substitute for the required mixed-load campaign.

## Required measurement boundaries and existing-test limitation

For both providers, establish external `PackageReference` Native AOT consumers with the same business inputs and explicit dynamic/prepared modes. Record raw process-wide allocated bytes before dividing by operations, batches or rows; capture all GC generations; account for callback/thread-pool work and separate required result objects from framework temporaries. A matching empty-driver or isolation control and allocation stacks are attribution evidence, not permission to subtract unrelated noise until a total rounds to zero.

Minimum separate boundaries are:

1. Dynamic construction and projection binding.
2. Prepared parameter update and snapshot.
3. First move, native submission and initial fetch.
4. Primitive row mapping within a received batch.
5. String/JSON/decimal framework validation and required business materialization.
6. Each supplemental fetch and batch replacement.
7. Final `false`, early termination, and actual cursor cleanup.
8. Session open and return.
9. Transaction begin/commit/rollback, with outcome and persistence checks outside the timed/allocation interval unless explicitly included.
10. Synchronous completion, genuine asynchronous suspension and high concurrency as distinct cases.

The existing streaming test collects `GC.GetTotalAllocatedBytes(true)` before its functional scenarios and reports the final difference. It includes setup, fixtures, exceptional cases and result reporting; this is **not** a warmed steady-state public-consumer allocation gate. Its concurrent Move/disposal, linked-token, failure and owner-release cases remain useful semantic tests. They were inspected, not executed, during this audit. [Initial measurement boundary][stream-test-start]; [reported total][stream-test-end]; [concurrency and cleanup cases][stream-test-concurrency].

## Reproducing the source audit

Use a checkout that contains the immutable commit. These commands inspect sources and identity only; they do not run a benchmark:

```bash
KORDA_AUDIT_ROOT=/workspace/scratch/754bc732518e/Korda-DB-Perf-01-linux
KORDA_AUDIT_SHA=771bc77cbd68d3f932b99ed2497c0697bbba5f02
git -C "$KORDA_AUDIT_ROOT" show "$KORDA_AUDIT_SHA:AGENTS.md"
git -C "$KORDA_AUDIT_ROOT" show "$KORDA_AUDIT_SHA:src/Data.Streaming/TypedStream.cs" | nl -ba
git -C "$KORDA_AUDIT_ROOT" show "$KORDA_AUDIT_SHA:src/Data.NativeHost/HostStreamTransport.cs" | nl -ba
git -C "$KORDA_AUDIT_ROOT" show "$KORDA_AUDIT_SHA:src/Data.Abstractions/DbWire.cs" | nl -ba
git -C "$KORDA_AUDIT_ROOT" show "$KORDA_AUDIT_SHA:src/Interop.Async/AsyncOperation.cs" | nl -ba
git -C "$KORDA_AUDIT_ROOT" show "$KORDA_AUDIT_SHA:src/Interop.Callbacks/CallbackCoordinator.cs" | nl -ba
```

Every source link below names that same commit. A later changed implementation requires a new audit or an explicit diff against this inventory; this document must not be relabeled as evidence for unexamined bytes.

[agents]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/AGENTS.md
[query-create]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Fluent/QueryContext.cs#L12-L30
[query-compose]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Fluent/QueryContext.cs#L31-L90
[operand]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Binding/OperandEncoding.cs#L11-L41
[generator]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Generator/ModelGenerator.cs#L173-L225
[projection-definition]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Materialization/ProjectionDefinition.cs#L10-L55
[generator-static]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Generator/ModelGenerator.cs#L184-L203
[projection-shape]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/Rows.cs#L166-L191
[projection-register]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/DataSource.cs#L159-L163
[metadata-projection]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Binding/MetadataBindings.cs#L18-L23
[projection-encoding]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Binding/OperandEncoding.cs#L24-L36
[prepared]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Fluent/Terminals.cs#L117-L156
[parameters]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Fluent/Projections.cs#L193-L222
[parameter-encoding]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Fluent/QueryContext.cs#L186-L206
[stream-create]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Streaming/TypedStream.cs#L19-L45
[enumerator]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Streaming/TypedStream.cs#L97-L123
[move]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Streaming/TypedStream.cs#L125-L190
[move-body]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Streaming/TypedStream.cs#L137-L190
[host-fetch]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/HostStreamTransport.cs#L14-L24
[operation]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/DataSource.cs#L65-L87
[native-copy]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/NativeHost.cs#L30-L47
[host-batch]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/HostStreamTransport.cs#L26-L38
[row-batch]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Streaming/StreamTransport.cs#L43-L66
[wire-parse]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/DbWire.cs#L57-L95
[wire-validation]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/DbWire.cs#L57-L126
[scalar-validation]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/DbWire.cs#L128-L153
[primitive-codecs]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/Codecs.cs#L96-L120
[json-validation]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/DbWire.cs#L148-L152
[json-codec]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/Codecs.cs#L180-L188
[configured-validation]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/DbWire.cs#L128-L180
[configured-codecs]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/Codecs.cs#L126-L141
[decimal]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/Codecs.cs#L237-L269
[projection-read]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Abstractions/Rows.cs#L198-L209
[owner-lease]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Binding/Owners.cs#L35-L57
[resource-lease]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Interop.Lifetime/NativeResourceOwner.cs#L55-L103
[async-base]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Interop.Async/AsyncOperation.cs#L32-L105
[async-result]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Interop.Async/AsyncOperation.cs#L577-L598
[stream-cleanup]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Streaming/TypedStream.cs#L192-L243
[session-open]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/DataSource.cs#L95-L102
[session-lifetime]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/DataSession.cs#L10-L139
[close-controller]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/DataSource.cs#L167-L220
[transaction-begin]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/DataSession.cs#L106-L124
[transaction-control]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Transactions/DataTransaction.cs#L18-L96
[transaction-host]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/HostTransactionTransport.cs#L20-L50
[transaction-observation]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Transactions/DataTransaction.cs#L54-L63
[transaction-snapshot]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/HostTransactionTransport.cs#L25-L26
[native-snapshot]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/NativeHost.cs#L121-L125
[snapshot-decoding]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/HostEncoding.cs#L37-L62
[close-result]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Transactions/TransactionValues.cs#L65-L74
[buffer]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Streaming/TypedStream.cs#L55-L61
[array]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.Streaming/TypedStream.cs#L63-L64
[async-retire]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Interop.Async/AsyncOperation.cs#L394-L545
[session-contract]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/DataSession.cs#L7-L24
[callback]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Interop.Callbacks/CallbackCoordinator.cs#L7-L75
[callback-scheduler]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Interop.Callbacks/CallbackCoordinator.cs#L78-L103
[source-init]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/DataSource.cs#L28-L163
[failure]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/NativeHost.cs#L57-L82
[async-registration]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Interop.Async/AsyncOperation.cs#L121-L162
[close-wait]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/DataSource.cs#L208-L220
[savepoints]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Data.NativeHost/HostTransactionTransport.cs#L51-L79
[stream-test-start]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/tests/Data.Streaming/Program.cs#L7-L15
[stream-test-end]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/tests/Data.Streaming/Program.cs#L226-L241
[stream-test-concurrency]: https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/tests/Data.Streaming/Program.cs#L164-L225
