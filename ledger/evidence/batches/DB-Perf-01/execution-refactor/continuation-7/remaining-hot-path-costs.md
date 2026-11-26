# Remaining hot-path costs to attribute before selecting more work

This is a read-only source inventory. No further product change, profiling run
or benchmark is selected here. The stable reference is public
[47fe650](https://github.com/IzuSharp/Korda/commit/47fe650dfed5d7bba1c4d74c4a127c5d08b66082);
the in-progress Find candidate still calls these same render/pull paths. Its
final source identity and actual phase results must be bound separately.

## 1. Repeating compiled-shape cache lookup work

`capture_execution` calls `NativePlan::render(..., &source->shapes)` for each
accepted Fluent/prepared/Find execution. `ShapeCache::acquire` obtains the already
compiled immutable shape, allocates a `Bytes` buffer containing ABI hash plus
complete shape identity, computes SHA-256, takes the cache mutex, scans for the
key, verifies exact identity on a hit and rotates its LRU entry.

The ABI/profile/source/generation/query/parameter/projection identity and
literal-value exclusion are required. Exact comparison is the collision guard;
bounded entries/bytes, concurrency and survival of eviction/clear are required.
The source alone does not demonstrate that reconstructing and hashing the same
immutable key for every execution is necessary.

Protected assertions are `plans_and_cache()` and `concurrent_shape_cache()` in
[query_tests.cpp](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/native/cpp/tests/query_tests.cpp):
literal values never become cached execution data, a different operator gets a
different shape, finite eviction and uncached oversize behavior remain, acquired
shapes survive clear, and concurrent renders preserve SQL/values/cache bounds.
Source mismatch and ordinary-plan one-shot behavior are checked there too.

**Missing attribution:** no isolated time, CPU or native allocation has been
assigned to this hash/lookup. The next decision needs current render/admission
phase samples or native allocation/call-stack evidence, especially with both
one hot shape and a realistic bounded shape set. Do not infer a material win
merely from eliminating a hash call.

## 2. Repeating immutable command and batch metadata ownership

In
[query.cpp](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/native/cpp/src/query.cpp),
`NativePlan::render` returns the cached `shape->sql` and `shape->expectation` by
value into `RenderedQuery`. `SqlPlan::rendered` then moves those owned values
into the per-execution `SqlPlan`. This is one copy at the render boundary, not a
second copy at the move. The same render builds an owned vector of Scalars,
including one independent byte vector for each non-null input and retained
literal argument. `ProviderConnection::prepare` additionally makes a
NUL-terminated SQL string and text parameter storage for libpq; SQLite performs
its typed binding and TRANSIENT ownership transfer.

For rows,
[BatchWriter](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/native/cpp/src/contracts.cpp)
is constructed for each actual batch. Its constructor currently copies the
Expectation (including descriptor storage), validates it and writes the fixed
NWDB header/descriptors. Each cell then appends validated canonical bytes. The
partial-batch finish compacts the reserved cell-table gap only when necessary.
The batch is transferred by owner/view through `TakePullBatch`; there is no
managed whole-frame copy in that formal pull path.

The independent execution snapshot is required: callers can change parameter
sets after submission, run one prepared shape on different sessions, dispose a
wrapper or clear a cache while accepted work continues. Canonical scalar
validation, configured codecs, result descriptors, one live batch, finite row/
byte grants and no borrowed pointer across await are also required. These
contracts do not inherently require copying immutable SQL/descriptors again,
but replacing ownership must retain an explicit immutable owner for as long as
any provider or batch reader can access it. Variable-value snapshot ownership
must not be removed together with immutable metadata copies.

Protected assertions include prepared snapshot/concurrency cases in
[Query.Fluent tests](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/tests/Query.Fluent/Program.cs),
`plans_and_cache`, `bounded_batches`, `batch_outlives_cursor`,
`arena_lookahead_and_end`, field/shape error ordering in
[streaming_tests.cpp](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/native/cpp/tests/streaming_tests.cpp),
and managed held-mapper/borrowed-batch tests. The Find candidate adds independent
key/DTO byte ownership and Source-close/eviction checks; review their final
commit before assigning them execution credit.

**Missing attribution:** current source proves the allocations/copies exist,
not their share of total latency. Separate immutable command overhead from
necessary value encoding, driver conversion, canonical row construction and
business DTO allocation in the 1/100/1000-row evidence. Avoid describing
BatchWriter's necessary partial-frame compaction as unconditional re-encoding.

## 3. Per-batch readiness and continuation scheduling

The current pull route has an actual native fetch worker, a readiness callback,
`CoordinatedCallback.Signal`/ThreadPool processing, a typed take and asynchronous
ValueTask continuation. It coalesces notifications and already avoids the
empty initial scheduling offer when a healthy accepted request is not ready.
Later readiness still signals progress; stop, rejected scheduling, uncertain
acceptance and setup/drain boundaries retain independent notifications.

This boundary protects callbacks returning safely, asynchronous continuation
behavior, one take/publication per generation, cancellation-registration drain,
source-owned callback roots and independent parent notification-tail joins.
`ReadySchedulingTests` checks early ready overlapping setup, three accepted late
generations, scheduler rejection/retry and a delayed synchronization-context
tail. The native `pull_generations_and_tail`, close-tail, queued-cancel and
source-close cases enforce generation/backpressure and retirement. New one-shot
command tests also explicitly reject executing user code on the unmanaged ready
stack and hold the independent native notification tail during parent closure.

The preceding local inline-completion experiment was rejected before AOT
execution. Its pinned runtime source publishes the ValueTask completion sentinel
before continuation dispatch; dispatch is not a no-throw primitive. An exception
after publication cannot be recovered by setting an exception again, changing
the reusable generation or disposing an already delivered batch. Moving a
setter unconditionally into the native callback is not a selected shortcut.
See the retained
[continuation-5 record](https://github.com/IzuSharp/Plan/blob/b748d89ed0173843b182703d6affa534d6c43aa0/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-5/README.md).

**Evidence boundary:** historical 1000-row phase samples show substantial
remaining read-phase time, but combine driver read, native batch encoding,
managed scheduling, mapping and release. They are not a per-queue measurement
and do not belong to the final candidate. Use the new candidate's batch counts,
readiness/take/mapping/release intervals and whole-process CPU before deciding
whether a further architecture change has a measurable benefit.

## Constraints outside this shortlist

Fresh PostgreSQL Parse/Describe confirmation before Execute still protects
metadata/error and cursor-open side-effect contracts, including DDL mismatch.
Post-COMMIT confirmation and safe reuse proofs are independent of the selected
pre-COMMIT probe saving. Those waits are not treated as free deletions. The
remaining representation/work is explicit in the formal native-path review;
this shortlist is an attribution priority, not additional implementation scope
or a claim that every listed cost can be removed.
