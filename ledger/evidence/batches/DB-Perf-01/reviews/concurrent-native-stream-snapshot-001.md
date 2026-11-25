# DB-Perf-01: independent review of concurrent snapshot 001

## Decision and evidence status

**Status: source-only review of an uncommitted intermediate snapshot. This is not an accepted candidate, a successful test run, an allocation result, or a performance measurement.**

The localized `TypedStream` change is acceptable to take forward to correctness and allocation verification. I found no new cancellation, concurrent-move, disposal, or ownership defect in the change inspected. This decision does not approve a merge or establish zero framework allocation.

The direct native consumer is suitable for further validation of its five individual read projections. Its current `--case mixed` result must not be compared with the managed consumer's `--case mixed` result: the snapshot executes five native cases and thirty managed cases. Error handling also differs between the two runners. These are acceptance blockers for a common mixed-load campaign, not reasons to discard the isolated stream optimization.

Native allocation metrics are explicitly incomplete rather than fabricated: cumulative native allocation/free counts and whole-process native heap peak are `null` with explanations. Consequently, this executable cannot yet supply those required acceptance measurements.

Review date: 2026-11-24 UTC. Reviewer: independent `native_and_workloads` agent. No source in the concurrent workspace was changed, no binaries were built, and no database load was run for this review.

## Snapshot identity and review boundary

The reviewed snapshot is `/workspace/scratch/754bc732518e/concurrent-snapshot-001`, captured at `2026-11-24T09:25:45.953000+00:00` from `/workspace/scratch/b94e2a0e0c3f/Korda-DB-Perf-01-linux`. Its declared base is Korda commit `771bc77cbd68d3f932b99ed2497c0697bbba5f02`. A statement about this snapshot does not apply automatically to subsequently edited files in that source workspace.

The snapshot receipt records a stable second read for each copied source file. During this review, all 23 copied files and `candidate-observed.diff` were rehashed; all 24 hashes matched the receipt. This binds the review to the copied bytes, without proving that the original concurrent checkout was an atomic or buildable revision.

| Snapshot-relative file | SHA-256 |
| --- | --- |
| `src/Data.Streaming/TypedStream.cs` | `91294bd51fcba16aec116512ce89f08866108de73751dd47ef255218201bf6af` |
| `candidate-observed.diff` | `a7bc6961c5a2fb6b8cf3e98d0a0e9090017e7c1b19e3ea3d2843c7c869fadd3b` |
| `tests/Data.Streaming/AllocationProbeRaces.cs` | `4454d2c7731f31c525e1d31f18f90200f15fe95a3c89bd5067a0f136147c6ffe` |
| `benchmarks/db-perf/native/main.cpp` | `c2c5d767cb7ea174de2cafebe589fa21d0107f4bf213fdc4e14391ebb06ff7aa` |
| `benchmarks/db-perf/native/README.md` | `bcf4403f1b78b3f7efbf4dc1e1fcf7e8f6a6a62a614b86e0d3433c064ee259c1` |
| `benchmarks/db-perf/native/build.py` | `aa24472928cbdaa840b4153f3cb7c094c8c556f46ae7d78cd51295e85339090a` |
| `benchmarks/db-perf/workload/manifest.py` | `b65ed7e5adf1a83227e2adca9df4ebadbebff86971f4bb70db6725308bdc8fd5` |
| `benchmarks/db-perf/workload/queries-v1.json` | `4e02854ed69aa36b34dc9c8f742b9068ec2e586dbc63874d895c67a267cbb5d8` |
| `benchmarks/db-perf/managed/Korda/Workload.cs` | `ad455ffd39c89a3b2a978a742f3cf21fbcc013985cfe6c2e5bf493dd0973e6bd` |
| `benchmarks/db-perf/managed/Korda/Measurement.cs` | `0732825bee80ad1a3ec5e3dfc03af22e059a3c888e3d4cf9e1486762f4a9c2dc` |
| `benchmarks/db-perf/managed/Korda/Digest.cs` | `fe47ba23ed9f7c7cbcbdd2f202793625d1cc528db7e835c6a06c093bd8c8ae00` |
| `benchmarks/db-perf/managed/Korda/Models.cs` | `56af58130abffd7b4cc0b7f4f82d4a591ecd66ce248b435f41ef1a910ce099ec` |
| `benchmarks/db-perf/managed/Korda/Dataset.cs` | `211083033651ce526a88bee130ab8f817a41b72dcc0b211dbcf287e190cc3f0a` |

Line references below are to those snapshot files unless a fixed base-commit source is explicitly named. The snapshot is partial: for example, `candidate-observed.diff` adds a call to `AllocationProbeGate.RunAsync` at line 129, but the snapshot does not contain that class's source. The diff includes unrelated abstraction-test changes as well. This review therefore does not assert that applying the displayed diff alone yields a complete candidate.

## Findings that affect measurement acceptance

### P1 — The two `mixed` modes execute different business workloads

**Locations:** native `main.cpp` lines 202, 216 and 516; managed `Workload.cs` lines 7–11 and 73; `manifest.py` lines 26–33.

The native loader permits the five v1 projections (`numeric`, `text`, `money`, `json`, `wide`), requires five query entries, and cycles over that vector. The managed consumer has thirty case names and cycles over all thirty. Joins, aggregates, paging, set operations and related loading occur only in the managed mix in this snapshot.

A throughput or tail-latency comparison that supplies the same spelling `--case mixed` to both programs would compare different work. The native result's explicit five-case scope at line 594 is good disclosure, but does not make the two mixes equivalent.

**Required before a common mixed campaign:** define the chosen case IDs, weights, parameters and ordering in one versioned input, have every route execute that input, and record the input hash. Until then, compare only an explicitly selected common single case, or label a five-case exploration separately. The five projections do not satisfy the requested minimum of 24 semantically different business queries.

### P2 — Failure and recovery policy differs between runners

**Locations:** native `main.cpp` lines 545–552; managed `Measurement.cs` lines 65–69.

After an operation fails, the native worker records the failure and stops. This conservatively avoids reusing a connection whose protocol drain was not proven. The managed worker records the failure and continues its loop. A run with errors therefore changes its admitted concurrency and subsequent offered work differently across routes. This affects sustainable-throughput, error-rate, saturation and recovery comparisons even when the SQL case is otherwise equal.

**Required for those comparisons:** use a shared fail-fast policy, or define and implement the same bounded discard/reconnect/retry policy with all attempts counted. Do not make native continue on an uncertain connection just to equalize counters. A correct error-free exploratory run is not invalidated by this difference, but cannot prove error recovery.

### P2 — SQLite configuration records requested values without reading back the results

**Location:** native `main.cpp` lines 387–393.

The constructor executes the SQLite pragmas and writes a literal configuration object. `sqlite3_exec` discards the `journal_mode` result, so the JSON object is not itself proof that the requested journal mode took effect. A successful command can still return a different journal mode for a database where WAL is unavailable.

**Required for frozen durability settings:** query the effective `journal_mode`, `synchronous`, `foreign_keys` and busy timeout on the actual connection, preserve those values, and reject an unexpected setting before measurement. Record PostgreSQL server-side transaction and durability settings separately as well. The current receipt's configuration must be described as requested until verified.

### P2 — Native allocation and heap-peak acceptance remains unimplemented

**Locations:** native `main.cpp` lines 115–127 and 611–617; native `README.md` lines 118–124.

The executable explicitly emits `null` for cumulative native allocation/free calls and whole-process native heap peak. This is honest and should remain so until instrumentation exists. `mallinfo2` snapshots describe current glibc block accounting; they cannot recover cumulative allocations or an intervening peak. SQLite's high-water value covers its engine allocator only. Custom live connection, statement and `PGresult` counters prove only those counted owners returned to zero, not all native owners or all heap retention.

**Required for full acceptance:** obtain a version-bound native allocation/free trace or equivalent counters, identify the instrumented allocator domains and overhead, and report engine-only values separately. Keep the uninstrumented timing binary as a separate result when instrumentation changes performance. Do not relabel `ownersReturnedToZero` or SQLite's high-water mark as complete native memory accounting.

## Stream change: cancellation, concurrency and lifetime reasoning

The change removes an eagerly created `TaskCompletionSource` for every move and uses `_moving` plus a lazily allocated `_moveJoin`. It does not replace `MoveAsync` with a reusable mutable completion source: `MoveAsync` remains `async Task<bool>` at line 136.

| Boundary | Source reasoning | Review result |
| --- | --- | --- |
| Concurrent `MoveNextAsync` | The closed check, active-move check and `_moving = true` are within the same `_gate` lock, lines 126–134. | A second active move still receives `ConcurrentUse`. |
| Dispose races with move completion | Dispose reads `_moving` and creates/reuses `_moveJoin` under `_gate`, lines 227–236. The move clears `_moving`, detaches `_moveJoin`, and completes it under the same lock, lines 186–193. | No new lost-wakeup interval was found. A disposer either observes the completed move or owns the task that its finalizer completes. |
| Multiple disposers | All overlapping disposers receive the same pending join task. `_closed` is set before releasing the lock, preventing a newly admitted move. Cleanup retains its separate single-flight task, lines 196–205. | No join reuse across independent moves or duplicate cleanup was introduced. |
| Continuations and lock ownership | The lazy join uses `RunContinuationsAsynchronously`, line 236. Cleanup's completion source preserves the same option, line 202. | Completing the join under the gate does not synchronously invoke its continuations inside that gate. |
| Dispose during asynchronous start | A successful start publishes `_transport`, registers cancellation, and rechecks `_closed`, lines 144–148. The move remains active through any cleanup. | Late-created transport is still stopped and joined before disposal completes. The join does not manufacture retirement. |
| Dispose during fetch | The move owns a fetched batch and checks closure before mapping, lines 154–168. Dispose waits for the active move before calling shared cleanup, lines 247–250. | Disposal cannot release a batch while the active move is still taking ownership of it. |
| Dispose during synchronous mapping | The active move remains marked until after mapping and its `finally`, lines 176–193. | An already admitted mapper retains its batch; disposal waits. A row already being mapped may succeed, as before the change. |
| Cancellation | Token registration still calls `RequestStop`; cleanup still disposes the registration and awaits `JoinAsync`, lines 146 and 213–218. | Stop request and confirmed native retirement remain distinct. The optimization does not make cancellation equivalent to immediate cleanup. |
| Mapping plus cleanup failure | The original exception is rethrown; cleanup failure is attached under `Korda.Database.StreamCleanup.v1`, lines 179–184. Disposers await the shared cleanup task. | Original exception identity and cleanup observability are preserved in the inspected code. |
| Object lifetime | The active async method retains its enumerator state; the transport/batch fields and shared cleanup task are unchanged. | Removing the eager completion source does not remove the active operation's ownership of the enumerator. |

No blocking regression was identified in this localized change. This conclusion is limited to the inspected synchronization and ownership paths. It is not a proof of all interleavings or a statement about unreviewed concurrent edits.

The source still contains allocation sites and potentially allocating asynchronous suspension: the enumerator, batch leases, cleanup completion source, linked cancellation source when required, overlapping-dispose join, and the `Task<bool>` async operation have not all been removed. Avoid inferring whole-framework zero allocation from removal of one per-move completion owner. Initializations, cancellation and overlapping disposal also need their own accounting boundaries.

An unchanged cleanup limitation remains visible: if `_batch.Dispose()` throws at line 212, control reaches the cleanup catch before cancellation registration disposal and transport join. This is not introduced by the lazy-join change. Whether it is a reachable supported path depends on the batch-owner disposal contract; the new tests exercise join failure, not a throwing batch disposer. Do not interpret this review as proving cleanup after every possible exception from arbitrary owner code.

## New race tests: coverage and limits

`AllocationProbeRaces.cs` uses explicit completion gates instead of timing delays. Its meaningful covered boundaries are:

| Test location | What the source asserts |
| --- | --- |
| Lines 25–49 | Two disposers remain pending during delayed start, no untransferred batch is disposed, later transport retirement is joined once, and repeated disposal reuses completion. |
| Lines 51–77 | Pending fetch rejects concurrent move, both disposers wait, a completed batch is released once without mapping after closure, and no next move is admitted. |
| Lines 79–125 | An active synchronous mapper keeps its owner; dispose waits for mapper exit and retirement; original mapper exception identity and shared cleanup exception are preserved. |
| Lines 127–150 | Cancellation requests stop without synthesizing completion, retains the admitted token, and waits for the controlled retirement signal. |

The fixture's owner throws on double disposal and guards access after release, which gives these assertions useful ownership sensitivity. In the canceled-fetch case, the fixture itself releases the batch that was never returned to the enumerator; this tests the transport ownership contract rather than attributing that compensation to `TypedStream`.

The base test project uses the SDK's default source inclusion and excludes only `ApiCheck/**/*.cs`; therefore a complete candidate containing the new file does not require an additional explicit compile item. The diff wires the race suite into the normal test path and exposes a dedicated `--allocation-probe-races` entry. The absent `AllocationProbeGate` source still prevents treating this copied subset as the complete build input.

These tests have not been executed by this review. Before accepting the change, run the complete streaming test program as Native AOT against the final candidate. The new deterministic tests should accompany the existing successful completion, early enumeration termination and cleanup tests. Additional focused cases are useful where not already covered: successful mapping followed by cleanup failure, `RequestStop` failure, and a start operation that faults or is canceled while dispose is waiting. A high-concurrency provider test is still necessary because the controlled transport does not reproduce actual native callbacks or provider scheduling.

## Native result consumption and preparation contract

### What is aligned in the five read cases

`manifest.py` defines explicit columns, aliases, two typed Int64 parameters, result count and a digest of all business fields. Its default output was regenerated during this review and compared structurally with `queries-v1.json`; they were identical. That is a pure input-consistency check, not a database result check.

Native `main.cpp` lines 130–180 and 283–293 materialize numeric values or owned typed DTOs, nullable strings and owned typed settings, then consume every field before destruction. The digest encodes signed Int64 values in little-endian form, NULL strings with a negative length, nullable integers with a presence byte, exact cents, and both settings fields. Managed `Workload.cs` lines 107–139 consumes corresponding fields and disposes its enumerator. The source-level digest and ownership contract agrees for the fixed seeded data.

Both native database loops consume every row. SQLite steps through `SQLITE_DONE`, resets and clears bindings, then finalizes a per-operation statement or retains a bounded cached statement. PostgreSQL uses binary single-row results, destroys each `PGresult`, requires its terminal result, drains through the final null and checks transaction-idle status. The rows and digest are checked on every execution at native line 488, including ordinary measured executions.

This is a materially stronger comparator than counting rows without DTO construction. Exact allocator layouts naturally differ: C++ small-string optimization and object layout need not mimic CLR object layout. Record their costs separately while holding values, nullability, ownership lifetime and result consumption equal.

### Bounded materialization domain

The native JSON SAX mapper accepts the fixed `Channel`/`Gift` settings shape and constructs a typed settings object. It does not implement the full deserialization behavior of `System.Text.Json` for arbitrary unknown properties, missing properties, nested input or malformed payloads. The PostgreSQL binary numeric decoder at lines 254–275 uses exact scaled arithmetic and rejects unsupported scale, rounding and overflow; this is consistent with the declared fixed `numeric(18,2)`/signed-cents domain, not general decimal-provider equivalence. The five-case result must retain those input limits. The separate earlier preflight probe's numeric-as-text result does not validate this new binary numeric implementation.

### Query construction and physical preparation are separate layers

Native dynamic mode constructs SQL inside each operation at lines 440–442. Prepared mode reuses the SQL shape. Default physical preparation remains per operation; physical statement reuse is explicitly a separate option and uses at most one statement per declared case per connection. The executable rejects dynamic construction combined with physical reuse. These distinctions should be preserved in every table and receipt.

The existing Korda `PreparedQuery` route reuses the query plan and does not imply that the physical driver statement is reused. Native physical reuse must therefore be reported as an additional lower-layer comparison, not silently substituted for Korda plan reuse.

There is a further SQLite preparation-count distinction. In fixed base commit `771bc77...`, [host.cpp](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/native/cpp/src/host.cpp) at lines 1477–1489 first calls `describe_sqlite` and then `query`. [provider.cpp](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/native/cpp/src/provider.cpp) at lines 649–660 prepares and closes the description statement, then separately prepares the query. Native `main.cpp` lines 446–460 prepares once and obtains the result shape from that statement. Normal read results can still be equivalent; the extra product description work is a framework cost to identify. The shared label `per-operation` does not mean identical physical prepare-call counts. An optional matched-description layer can isolate that cost if needed; the direct-driver result should retain its real behavior.

### PostgreSQL protocol submissions are not physical round trips

The native `product` confirmation mode implements explicit description and retirement `Sync` confirmations. That choice has a real product source basis: fixed-base `host.cpp` calls `confirm_description` at line 1489 and `close(true)` at line 1708; fixed-base `provider.cpp` lines 1011–1057 perform the corresponding synchronization. Prepare and describe are also separate submissions in that provider at lines 764 and 777.

Native `main.cpp` lines 349–375 and 464–486 retain those logical boundaries for the product-confirmation layer. Its additional `drain-only` layer must stay separately labeled. Protocol submission, SQL execution and poll-wait counters are distinct; physical network round trips are correctly emitted as unmeasured at line 601. No packet trace or execution-plan comparison was performed here.

## Resource and load-boundary limitations

The result names the native route, scope, construction mode, physical preparation mode, confirmation mode, executable, manifest, build-receipt and loaded SQLite identities. This is a useful basis for later reproducibility, but the review did not build the executable or validate those runtime identities.

The runner is explicitly closed loop: each worker starts its next operation after the preceding one completes. For time-based runs, the recorded `planned` value is the actual started count. This does not measure independently scheduled arrivals or requests that would have queued outside the client. It cannot by itself establish the requested fixed offered-load tail-latency comparison or sustainable saturation point. No transaction, write, conflict, rollback, cancellation or early-enumeration benchmark is implemented in these five native cases.

The native deadline/poll implementation is its own bounded read mechanism, not a proof of Korda's caller-visible cancellation semantics. The native failure path discards the connection instead of attempting unsafe reuse. That is reasonable for a limited reader and must be reconciled with the common campaign policy before recovery comparisons.

User/system CPU deltas and elapsed time are reported separately. The explicit idle CPU delta at lines 557–558 and 610 is a pre-load idle observation; post-drain process readings are also recorded, but should not be confused with that idle interval. Process peak RSS includes startup and warmup. Drain and retention observations still include surviving harness arrays and worker bookkeeping. PostgreSQL service CPU and memory require a separate server process measurement; the client receipt alone does not provide them.

Dataset metadata verifies declared tenant/order counts, while per-query digests verify selected values. Neither proves the entire seed, indexes or execution plans match across implementations. Preserve actual SQL and typed bindings, collect real PostgreSQL/SQLite plans, and validate the database state under the campaign's frozen configuration before accepting timing comparisons.

## Required next evidence and acceptance boundary

1. Assemble a complete candidate, freeze its commit or source manifest, and run the new plus existing affected streaming correctness tests as Native AOT. Bind every test receipt to its actual executable and native library hashes.
2. Measure the lazy-join change with matched before/after binaries, inputs and environment. Preserve cumulative whole-process allocated bytes before calculating per-query, per-batch and per-row values; include truly asynchronous and concurrent paths. Keep framework-only attribution distinct from end-to-end allocation.
3. Validate the five shared read cases against both real databases, including the new binary PostgreSQL numeric path, all result digests, effective configuration, exact SQL and execution plans. This review supplies no successful execution receipt for the snapshot.
4. Resolve the mixed-case and error-policy differences before accepting cross-route mixed-load results. Expand the common workload contract to the required business matrix and mutation/boundary cases.
5. Add the missing allocation/free and native heap observations, finish client/server resource accounting and dedicated-load control, and then run the required eight qualifying 30-minute segments. None is marked complete by this review.

**Review disposition:** proceed with isolated correctness and allocation verification of the stream optimization; proceed with limited native five-case correctness probes; hold cross-route mixed-load and full DB-Perf-01 acceptance pending the findings and evidence above.
