# DB-Exec-Parity-01 — relation batch allocation investigation

Status: measured diagnostics completed in recovery 03; a narrow private temporary-branch transfer experiment is now selected before product implementation. See [measured selection and ownership proof](recovery-03/relations-selection/selection.md). The earlier source-only plan below is retained as history. No reusable-plan cache is selected; no ordinary performance acceptance is claimed.

## Measured priority, not yet allocation-site proof

The original per-case receipts are `measurements/case-baseline-01/{sqlite,postgresql}/prepared-related-{korda,dapper}.json`. Each is ordinary Native AOT, warmup32, C1, 128 successes, zero failures/oracle failures, 32 composite parent keys, batch32 and 53 materialized children per business. The expected digest is identical (`2847736615530494015`).

| Provider | Korda managed B/business | Dapper managed B/business | Difference | Difference / 35 equally weighted businesses |
| --- | ---: | ---: | ---: | ---: |
| SQLite | 686,325.9375 | 74,274.1250 | 612,051.8125 | 17,487.1946 |
| PostgreSQL | 686,277.5625 | 51,243.2500 | 635,034.3125 | 18,143.8375 |

The near-equal Korda values on both providers prioritize shared managed work. Dividing the isolated difference by35 is a useful mixture-weight estimate; it is not exact allocation attribution for the concurrent mixed run, whose completion weights and worker/GC behavior must be checked independently. These receipts establish a large per-business total, not which function allocated it.

## Actual consumer work and source chain

`benchmarks/db-perf/managed/Korda/AdvancedCases.cs:RelatedCase` constructs immutable `EntityKey<Order>[]` and `Relation<Order,OrderLine>` once outside each measured operation. Every Execute calls the normal `session.LoadRelatedAsync(_keys, _relation)`; the prepared flag does not provide a prepared relation-batch overload. It awaits grouped results, sorts each group by child Id and hashes parent position, group count and child fields. Input key construction is not repeated in the measured hot path.

The actual Dapper frozen reader uses constant Sql29 plus a cached generated command factory in prepared mode and one immutable RelatedParameters object. Its result is buffered into IndexedLine objects, then copied into OrderLine lists by parent ordinal, sorted and hashed. The explicit guard requires Rows==32 and BatchRows>=32. It has its own driver/DTO/grouping costs; its lower total is not an allocation-free reference and cannot be subtracted as exact Korda framework cost.

The Korda batch entry synchronously validates relation/source/capabilities/cancellation, bounds and snapshots the input collection, creates one IndexedChild projection, then creates one From/QueryContext per parent. Each branch writes predicates and projection into a managed QueryCommand tape. Each subsequent branch is cloned once and imported into the first branch; UNION ALL retains input ordinal semantics. The final Stream seals/encodes one dependency graph and invokes the C++ compiler before the asynchronous result stream finishes. GroupRelated awaits complete bounded results, builds one list per nonempty input position and releases the query owner.

## Source-count predictions to verify

For the fixed workload: N=32 parents, K=2 key components, C=5 child fields, projected width C+1=6. The table below is a source prediction, not a runtime counter receipt.

| Boundary | Predicted invocations/business | Allocation or copy sites visible in source |
| --- | ---: | --- |
| Input key collection snapshot | 1 array, 32 CheckKey calls | New EntityKey reference array. EntityKey values already own snapshots; no fresh key encoding here. |
| IndexedChild projection construction | 1 | Field array, ordinal ResultField, materializer closure, canonical projection bytes/hash. |
| From / QueryContext / QueryBinding / original QueryCommand | 32 | Query wrappers, CTS, dictionaries/lists/sets, retained model owner and initial tape. |
| Source.RegisterModel | 32 hot lookups | Existing table hash cache normally returns the model; no repeated model canonical serialization on a hot hit. |
| Per-key ExpressionValues encoding | 64 | WireExpectation, descriptor/hash/cell arrays and owned wire frame before copy into command tape. |
| Per-parent ordinal Value encoding | 32 | Similar one-cell frame for Int32 ordinal; new value origin. |
| Binding.Column | 224 | 2 predicate columns + 5 selected columns per branch; Expression/Node/shape metadata. |
| Binding.Value / Binary | 96 / 64 | Origins and expression/node records; Binary creates Boolean shape metadata. |
| WHERE / Select / UNION clause | 64 / 32 / 31 | Small control frames for WHERE/UNION; Select writes stack scratch but allocates selection/codec metadata arrays and copies into tape. |
| SelectParent | 32 | The above key/column/value/select work plus delegates and expression arrays. |
| Combine → SnapshotAndImport | 31 | One clone of the new single branch each time, including tape bytes, mutable containers and retained origins; import metadata/record and UNION record. |
| Final graph Encode / Seal | 1 | Graph lists/maps/origin tables, one combined command byte buffer, owner vector, compiled-plan metadata, native compile call. |
| RegisterProjection | 1 | Source registration call uses stack scratch for this six-column shape; native registration/canonical metadata validation remains real work. |
| Source.BindCodec | 300 direct calls predicted | 64 keys + 32 ordinals + 192 selection fields + 6 registration fields + 6 stream-bound codec entries. Hot codec dictionary hits need not allocate. |
| GroupRelated | 1 | IndexedChild buffering, per-position lists and final IReadOnlyList array; actual child DTOs/group sorting remain necessary results/harness work. |

There are32 original branch commands plus31 cloned branch commands. The command's byte-array field initializer allocates256 bytes even in the clone constructor, which immediately replaces it with an exact tape copy; this is a concrete avoidable-looking source site, but its actual bytes and importance are not yet measured. Tape growth, Node/Expression records, dictionary capacities and final graph encoding may be larger. Do not label all686KB as cloning or serialization from source inspection alone.

### Corrections to plausible but unsupported explanations

- `Table.CanonicalBytes` and `MetadataHash` are computed at Table construction (`Data.Abstractions/Metadata.cs`). `DataSource.RegisterModel` checks its cached hash before binding codecs or calling MetadataBindings. Thirty-two From calls do not imply thirty-two model JSON serializations or registrations in the hot case.
- The batch constructs one IndexedChild Projection, not32. Its canonical bytes/hash are stored in that immutable object. The same projection is passed to32 context.Select calls.
- `OperandEncoding.TrySelectionInto` already uses4KB stack scratch for <=32 fields; the workload has6. Its WriteProjection does repeat UTF-8/name/header writing and BindCodec calls, but it does not allocate a complete heap projection buffer on this normal path.
- `QueryCommand.Clauses.Fields` is a readonly ref struct over a borrowed span. Its scans are CPU work, not a heap allocation per field. The Select clause does allocate its Expression[] and CodecDescriptor[].
- Each Combine clones its newly created source branch. It does not clone the entire accumulated32-parent union on every iteration. The final dependency graph is encoded once. The snapshot copy preserves the public Combine contract that its source query remains independently mutable; that general contract cannot be weakened for a relation optimization.
- Batched LoadRelated does not call `DataSource.RegisterRelation`; that belongs to the single-key path. Its per-call relation CanonicalBytes/hash work cannot be assigned to this batch workload.

## Approved first-layer diagnostic — narrow and sufficient to choose the next boundary

Use a clean task-tagged independent C# diagnostic worktree based on the baseline product commit. Reuse the existing baseline provider-native manifest and byte-identical native image; do not compile native code. Build only one provider diagnostic package/real AOT workload consumer at a time. Start with SQLite, retain exact generated code/out ELF/.dbg/native/package identity, and remove only documented completed duplicate bin/.o intermediates before PostgreSQL if required. Expected extra transient build footprint is roughly400–500MB per provider; stop and notify root before consuming remaining disk headroom. Source estimates are a budget, not a measured guarantee.

The first layer modifies only RelationBatch and a diagnostic-only observer, plus consumer start/finish hooks. It does not bypass a validation, replace a query, alter a result or enable a cache.

Record one request ID per LoadRelated call, phase, parent ordinal where relevant, start/end OS TID, monotonic timestamps and current-thread allocated-byte delta. Preallocate fixed record storage before the measurement gate; start/finish reset and snapshot outside the measured window. A record is written after the allocation end read. Empty prewarmed scope controls must show zero observed allocations. Overflow, unmatched/unfinished scopes, thread-ID mismatch or a nonzero control invalidates the observation.

| First-layer scope | Boundary and interpretation |
| --- | --- |
| Whole synchronous public invocation | Entry until returning its Task; same initiating thread only. Inclusive control, not the entire asynchronous business allocation. |
| Validation + key snapshot | Existing entry checks through owned reference-array construction. Preserve the original check and pre-cancellation order. |
| Projection construction | Exactly the one IndexedChild projection/canonicalization block. |
| From | Aggregate32 calls with per-parent IDs; includes QueryContext/QueryCommand setup and hot model lookup. |
| SelectParent | Aggregate32 synchronous branch-construction calls. |
| Combine | Aggregate31 synchronous clone/import/UNION calls. |
| Temporary branch disposal | Aggregate31 disposal calls, measured independently from clone/import when useful. |
| ToListAsync synchronous return | Includes synchronous Stream/registration/Seal/compiled-plan setup and any synchronous initial async-method prefix. It is not labeled purely driver CPU or purely compilation. |
| Grouping after await | Begin after the awaited rows arrive; end before returning groups. This is a separate synchronous same-thread scope on the actual continuation TID. Never subtract a current-thread allocation counter across await. |
| Final query disposal | Synchronous disposal on the continuation/failure path, separate from grouping. |

Do not sum whole invocation with its inner phases or any other nested inclusive scopes. Grouping may happen inline before invocation return if the Task is already complete; TID/monotonic parentage must reveal that case before computing any disjoint total. Whole-process ordinary managed allocation remains the reference total; current-thread scopes may omit work on native/managed worker threads, which must be reported as unattributed residual rather than assumed zero.

Execute the original related32 case on the real database after ordinary warmup with multiple individually identified requests, fixed key positions and complete original digest/row validation. Keep one process/request inventory for any observation rejection. Require expected53 children per business, the exact original digest, zero errors/retries/oracle failures, one SQL execution per nonempty business, unchanged SQL/parameter shape and all supported owners safely drained. Only allocation/call counts are eligible; concurrent builds invalidate ordinary latency/CPU interpretation by design.

## Adaptive second layer, only after the first layer

Instrument only the largest unexplained synchronous phase. If From dominates, isolate QueryContext/QueryCommand construction and hot RegisterModel to distinguish new owner/containers from cached registration. If SelectParent dominates, split key frame encoding, command Value/Column/Binary, and context.Select; then split Select's stack writer from command-side metadata arrays/tape growth. If Combine dominates, isolate `QueryCommand.Clone`, `Metadata`, dependency import and clause append. If terminal setup dominates, isolate `LockOrigins`, final `Encode`, metadata/codec registration, managed wrapper construction and native Compile; native allocations require their own separately attributed shim and must not be inferred from managed GC bytes.

Log tape capacity growth and copied logical bytes only at the selected layer. Preserve calls, exception/ownership order and all wire bytes. A cheap local change should precede full plan caching if it explains the observed majority: examples to test only after proof are removing wasted clone-initializer storage, avoiding repeated owned frame containers with a bounded synchronous writer, or avoiding unnecessary copies for a privately consumed branch. The public Combine remains snapshot-based; any private ownership-transfer helper needs its own complete failure/disposal proof and cannot be assumed safe from the immediate `using next` alone.

## Can the existing Prepared contract support shape reuse?

It supplies useful components, not permission to skip the proof. `PreparedQuery<T>` owns an immutable exact-source native plan; execution snapshots its exact parameter set synchronously before await, checks source/session identity and retains independent accepted operation/cursor owners. `PreparedParameterLayout` caches canonical layout and emits one owned frame under the QueryParameters gate. Provider execution still prepares/describes actual schema freshly; PG's unnamed statement deliberately avoids stale result-schema behavior. These are compatible building blocks for a relation shape in principle.

A relation cache would still need exact relation/table/materializer identity, source binding, parent-count-dependent shape, per-position parameters and original ordinal semantics. Same metadata hashes do not prove same mapper identity. Duplicate keys must retain separate branches/groups, collation stays in native SQL, empty input remains SQL-free, and there is still one UNION ALL statement with aggregate row/byte budgets. Parameter order/types, actual SQL and admission errors must remain equivalent. No retained QueryContext may capture the first caller's session, cancellation source or values.

A per-source reusable-plan cache also needs finite entry/byte charging, safe eviction and source close, in-flight leases, changed key snapshots, unknown/custom codecs, count changes, large key payloads, DDL/result-shape rejection and failure ordering. The existing FindPlan is a relevant ownership/limit precedent: it explicitly preserves former logical/wire quota ordering and does not keep sessions. Merely reusing a shared mutable QueryParameters dictionary across callers is unsafe. A prepared implementation must snapshot each caller independently before dispatch; avoiding parameter IDs by private bounded slots would be a further design decision, not part of this diagnosis.

Root therefore prefers the measured narrow synchronous allocation site over immediately building this cache. Keep full shape reuse deferred unless first-layer/second-layer evidence and ordinary A/B show that narrower fixes leave it necessary.

## Existing semantic regression anchors for any later implementation

`tests/Orm.Relations/FluentExperience.cs:RelationBatches` covers collection mutation immediately after invocation, exact composite matches, repeated keys in separate positions, empty groups/input, foreign/incomplete keys, pre-cancel/no SQL, input MaxBatchRows, shared duplicate result-row budget, mapper exception identity and subsequent session reuse. Its collation case checks that differently cased equal keys remain distinct result positions and comparison is done by SQLite.

`tests/Query.Fluent/Program.cs` covers prepared parameter snapshots, accepted operation versus plan disposal, lazy stream construction and parameter errors before row-capacity validation. `tests/Orm.Relations/FindShapes.cs` provides precedents for same-metadata/different-mapper identity, bounded LRU/byte eviction, key snapshot bytes, source-close/accepted-pull safety, logical quota/failure ordering and DDL changes. Those precedents do not substitute for a new batched-relation cache regression if one is later selected.

## Current limitations and next action

The byte numbers are real process totals; the call counts and candidate allocation sites above are source-derived predictions. No per-site runtime allocation count, actual relation-hotspot machine-code mapping or new causal optimization result exists yet. Start the approved independent first-layer diagnostic. Commit the diagnostic source identity, preserve original product unchanged, and retain failed/rejected observations before deciding which synchronous function to change.


## Recovery 03: measured selection before product implementation

Both databases now have same-thread, zero-control-allocation Native AOT measurements for all first-layer phases. SQLite second-layer counts prove 31 branch clones allocate 120,776 B and copy 54,932 tape bytes per related32 business. This is 17.6% of the roughly 686 KB whole-process total; SelectParent remains a larger independent cost. Shared Combine allocation is exactly 181,760 B on both databases. SQL stays one statement, 53 rows and the original digest, with no errors and zero final owners. Concurrent builds are allowed for these allocation/count observations, so CPU and latency are ineligible.

Select only an internal consuming import for the privately owned branch in RelationBatch. Public Combine still clones and keeps its mutable source usable. Consume the source only after the entire existing command SnapshotAndImport has succeeded, including appended tape and metadata updates; failed validation, finite budgets, wrong-source, unsupported mode and admission failure leave it usable. Retain the destination dependency before releasing the original source owner; no fallible work belongs between successful import and source invalidation. A later union failure is disposed by the private outer caller. Preserve every key snapshot, ordinal/duplicate group, native collation, SQL count, result budget and error ordering.

The complete measured tables, source identities, evidence hashes, targeted regressions and A/B acceptance conditions are in the linked selection. New code may now be implemented in the isolated task worktree. It remains a candidate until mechanism counts, Query.Binding AOT, dual-provider Relations, and ordinary repeated A/B pass.
