# DB-Perf-01 Linux workload and comparison contract

## Status and fixed source

All campaign execution statuses in this document are **pending**. Source inspection identifies callable API paths and existing tests; it is not a receipt for this batch, a performance result, or proof of zero allocation. Minimal native connectivity probes, if recorded separately, do not complete any campaign cell.

The pre-optimization product is Korda commit [`771bc77cbd68d3f932b99ed2497c0697bbba5f02`](https://github.com/IzuSharp/Korda/commit/771bc77cbd68d3f932b99ed2497c0697bbba5f02), which includes DB-Rename-01. Read its [repository instructions](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/AGENTS.md), [C++ implementation guide](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/docs/guides/cpp-native.md), and [order workflow](https://github.com/IzuSharp/Korda/tree/771bc77cbd68d3f932b99ed2497c0697bbba5f02/samples/api/orm-experience). The current user authorization owns DB-Perf-01; older task exclusions remain historical.

Implementations and benchmark programs belong in Korda. This document specifies the workload, measurement boundaries, oracles, and evidence obligations. It does not change a public API or authorize treating an unsupported path as implemented.

## Four comparison columns

| Column | Required entry and identity | Execution status |
| --- | --- | --- |
| Direct native C++ | C++20, the same pinned Clang Release toolchain and sqlite3/libpq versions; direct driver calls, no Korda C ABI or managed wrapper. Record source, compiler, archive, executable, runtime dependency, and actual server hashes/versions. | pending |
| Before Korda | Build both independent provider candidate packages from the fixed commit. Copy an ordinary consumer outside the source tree; use only PackageReference and the public Fluent/ORM APIs, generated mappings, and Linux x64 Native AOT. | pending |
| After Korda | The same consumer sources, data, load schedule, compiler, and package-consumption route, switching only to final candidate packages. Record exact package, executable, and actually loaded native-library SHA-256. | pending |
| Independent C# ORM | Fix a mature ORM and provider per database only after a minimal real-database Native AOT query succeeds. Record exact versions, provider-native dependencies, code generation, and per-case unsupported features. A raw SQL driver probe is a separately labelled supplementary result. | pending |

One database's four columns must share the same data definition, indexes, durability, transaction isolation, connection limits, workload seed, projected columns, result counts, and ownership obligations. PostgreSQL and SQLite retain their documented provider semantics; do not pretend their isolation implementations are identical. If the independent ORM cannot use the exact same SQLite engine build, record the mismatch and retain an additional driver-controlled comparison; do not silently attribute an engine difference to ORM overhead.

## Source-confirmed capabilities and limits

The [Fluent implementation](https://github.com/IzuSharp/Korda/tree/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Fluent), [Fluent tests](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/tests/Query.Fluent/Program.cs), and [ORM methods](https://github.com/IzuSharp/Korda/tree/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Orm.Relations) expose optional filtering, inner/left joins, grouping/HAVING, ordered offset and composite cursors, batched relationships, generated projections, streaming, NULL operations, IN subqueries, independent EXISTS, CTEs, bounded recursive CTEs, windows, set operations, checked mutations, transactions, savepoints, bulk inserts, and upserts. Every proposed batch case still needs compilation and real execution through each candidate package.

- Type-safe JSON serialization through `Codecs.Json(JsonTypeInfo<T>)` is source-confirmed. A public Fluent JSON-path/filter operation is not established; test JSON-path SQL separately if needed.
- PostgreSQL uses `Codecs.Decimal(18, 2)` in the order example. SQLite uses `Codecs.FixedScaleMoney(2)`. Compare exact decoded monetary values, not a floating-point approximation.
- Independent `EXISTS` and `IN` subqueries are source-confirmed. Outer-reference correlation is not established by this inspection; do not mark correlated subqueries as Fluent-supported without a real public-API test.
- SQLite rejects the advertised row-lock operation. PostgreSQL `ForUpdate` is a provider-specific case and is not part of the common two-database pass set.
- Offset paging requires a deterministic order containing the complete root primary key. Preserve that constraint in every column.
- A capability advertised by a module does not by itself prove that a planned query, mapping, or type combination succeeds.

## Data and oracle contract

Use the order/customer/detail domain and current `Db*` mappings. Freeze a versioned seed manifest containing table definitions, all indexes, exact row counts, a deterministic PRNG algorithm/seed, load parameters, and input-file hashes before the first comparable run.

Required data properties:

- Multiple tenants with composite order keys; repeat the same local order IDs across tenants to detect accidental cross-tenant matches.
- Fixed skew in tenant, customer, and order selection; a bounded hot-key set for mixed writes.
- Repeated creation timestamps so composite cursor ties are exercised.
- Orders with zero details, NULL customer references, and nullable business fields; preserve NULL versus missing association semantics.
- Narrow rows and a wide-review population with long memos, typed JSON, and exact money values. Fix field lengths and JSON value distributions.
- A large-result population that crosses many batches. It must be consumed fully for the export case.
- At minimum, evaluate indexes on `(TenantId, Id)`, `(TenantId, CreatedAt, Id)`, `(TenantId, CustomerId, CreatedAt, Id)`, and detail `(TenantId, OrderId)`. Commit the final indexes and statistics state, rather than changing them between columns.

Prepare an independent canonical oracle outside the timed region. For ordered reads, compare the full ordered sequence of canonical typed values; for unordered sets, canonicalize ordering before comparison. Include exact column count, names where contractually relevant, row count, NULL flags, keys, decimal scale/value, typed JSON members, and a digest of the complete consumed result. Digest equality is supplementary to representative full-value verification.

For writes, preserve a deterministic operation ID and submitted parameters, then verify affected rows, returned fields, transaction outcome, and durable state. Concurrent hot-key scheduling can produce different valid interleavings; validate committed-operation invariants and account for every conflict/retry rather than requiring identical final version numbers across different schedules. Restore the same database snapshot before each campaign segment. Keep a deterministic read-oracle partition when evolving hot-write state would otherwise invalidate exact read comparison.

## Execution modes and inclusion rules

`D` means construct the query and bind current values for every measured operation. Include equivalent composition work in all four columns. `R` means construct/prepare the reusable query or statement before the measured steady state and rebind values for each execution. Report actual reuse at each layer; native plan reuse does not imply physical statement reuse. `O` means an operation API whose current public contract has no separate reusable terminal; measure its normal per-call setup and completion. `S` means an additional parameterized SQL route, reported separately from Fluent/ORM.

Dynamic and reusable variants are modes of one semantic business case, not additional cases toward the minimum of 24. Reusing a command string in one column while constructing a query in another is not a matched dynamic comparison. Do not call `ToSql()` in every measured operation unless producing SQL text is itself the explicitly measured business requirement.

The normal mixed workload includes Q01-Q24 and Q26, Q28-Q30 with weights frozen after calibration. Q25 is a separately reported contention scenario with expected conflicts; Q27 is a separately reported rollback scenario. Either may have a declared, fixed frequency in a mixed failure campaign, but neither may be silently counted as an ordinary successful request. The normal mix must contain both reads and durable writes, as well as short and heavy reads. Exact weights are **pending calibration** and must be identical across the comparable four-column segments for one database.

## Thirty semantic business cases

For every row below, PostgreSQL execution, SQLite execution, before/after packages, direct C++, independent ORM, SQL comparison, and final oracle results are **pending**. `Available` below refers only to the public source surface. An independent ORM feature gap must retain an explicit missing cell and reason.

| ID | Business operation and normal/fault scope | Public Fluent/ORM route and reuse boundary | Parameterized SQL comparison and oracle |
| --- | --- | --- | --- |
| Q01 | Composite-key order lookup, including an absent key; normal | Available: `FindAsync` (`O`), plus a matching generated narrow projection (`D/R`). Distinguish full-entity from narrow-projection measurements. | `S`: tenant and order predicates. Verify 0/1 row, all selected fields, exact key, version, and absence. |
| Q02 | Order search with optional customer, minimum amount, and time range; normal | Available: `WhereIf` and typed predicates (`D`); a finite reusable shape per enabled-filter combination (`R`). Bind only active predicates. | `S`: actually construct the same enabled predicates. An all-purpose nullable-OR SQL shape is a different plan and must be labelled. Compare ordered matches and optional-filter truth tables. |
| Q03 | Order page with nullable customer display name; normal | Available: `LeftJoin`, nullable join projection (`D/R`). | `S`: equivalent LEFT JOIN. Check missing customer separately from a matched customer with a NULL field, stable order, and exact page. |
| Q04 | Order/customer/detail three-table item view; normal | Available: two explicit joins and a generated projection (`D/R`). | `S`: three-table JOIN with tenant/order composite association. Check multiplicity, item values, and no cross-tenant leakage. |
| Q05 | Customer spending and order counts filtered by HAVING; normal heavy read | Available: `GroupBy`, `CountRows`, `Sum`, `Having` (`D/R`). | `S`: identical grouping and HAVING. Check NULL-customer group, exact monetary total, count, and group ordering. |
| Q06 | Product sales-quantity ranking; normal heavy read | Available: detail root, product grouping, quantity sum, deterministic rank order (`D/R`). | `S`: equivalent aggregate and top-N. Check every group, ties, secondary ordering, and integer overflow bounds in the seeded data. |
| Q07 | Next order page across repeated timestamps; normal | Available: complete composite `QueryCursor`/`SeekAfter` ordering (`D`). A separate `R` variant may declare the equivalent typed lexicographic predicate with query parameters only after equivalence is verified; do not assume the cursor helper itself exposes reusable placeholders. | `S`: identical lexicographic continuation predicate. Check first, middle, and final pages without duplicate or missing rows. |
| Q08 | Deep offset page of the same ordered order list; normal heavy read | Available: complete unique `OrderBy`/`ThenBy`, `Skip`, `Take` (`D/R` for a fixed page shape). | `S`: same OFFSET/LIMIT and index/statistics state. Compare the exact slice from the canonical full sequence. |
| Q09 | Order page followed by bounded batch loading of details; normal | Available: `LoadRelatedAsync` with composite `EntityKey` list (`O`), page query `D/R`. Include key construction/grouping required by the normal API. | `S`: page plus the same association batching contract. Check parent input order, duplicate keys, empty associations, child order if promised, SQL count, and empty-input no-SQL behavior. |
| Q10 | Narrow reconciliation queue containing only keys and versions; normal | Available: generated narrow `DbProjection` (`D/R`). | `S`: return exactly the same columns. Fully consume and verify all keys/versions; do not let native fetch fewer fields or skip decoding. |
| Q11 | Wide manual-review detail with memo, JSON, and money; normal | Available: generated wide `DbProjection` (`D/R`). | `S`: exact wide projection. Materialize equivalent owned strings/JSON/money; verify lengths, bytes or typed values, NULLs, and no silent truncation. |
| Q12 | Large streaming ledger export; normal heavy read | Available: `AsAsyncEnumerable` (`D/R`). Keep ownership until enumeration/disposal completes. | `S`: direct streamed result. Consume every row into the same business digest/aggregate, record rows/batches and peak retained buffers; counting rows alone is insufficient. |
| Q13 | Orders having no detail rows; normal | Available: LEFT JOIN with `HasMatch().Not()` (`D/R`). | `S`: matching anti-join. Verify all empty associations and no false positives from nullable child fields. |
| Q14 | Customers missing contact details with a display fallback; normal | Available: `IsNull` plus `CoalesceReference` (`D/R`). | `S`: matching NULL/COALESCE expression. Compare canonical string values and count; distinguish NULL from empty string. |
| Q15 | Typed order settings and exact monetary values; normal | Available: `DbCodec`, source-generated JSON context, provider-specific money codec (`D/R`). This is typed JSON mapping, not a JSON-path claim. | `S`: same columns and decoding. Compare JSON members semantically, exact decimal value/scale, and nullable values. |
| Q16 | Orders containing a qualifying product/quantity selected by a subquery; normal | Available: typed `IN(QuerySelection<T>)` (`D/R`). Constrain the same tenant in both inner and outer queries. | `S`: same IN subquery. Check duplicate inner matches, empty inner result, and reused local IDs in other tenants. |
| Q17 | Filtered work queue built through a bounded CTE; normal heavy read | Available: `CommonTable<T>.Create` and `With` (`D/R`). Preserve immutable CTE-body and declared projection rules. | `S`: same CTE body and outer filter. Verify exact selected fields/order; capture materialization/inlining plan differences. |
| Q18 | Per-customer running spending and row number; normal heavy read | Available: `Window`, `Sum(...).Over`, `RowNumber` (`D/R`). | `S`: identical PARTITION BY, full tie-breaking ORDER BY, and ROWS frame. Verify each cumulative amount and sequence number. |
| Q19 | Combined order population from two business partitions; normal | Available: `Combine(UnionAll)` (`D/R`). | `S`: UNION ALL with the same final deterministic ordering. Preserve duplicates and verify partition contributions and total rows. |
| Q20 | Intersection of two independently filtered order groups; normal | Available: `Combine(Intersect)` (`D/R`). | `S`: INTERSECT. Verify duplicate elimination, exact common keys, and the empty-intersection case. |
| Q21 | Distinct active-customer population or distinct count; normal | Available: `Distinct` or `Count(..., distinct: true)` (`D/R`). Freeze one chosen result contract per case variant. | `S`: matching DISTINCT/COUNT DISTINCT. Verify NULL rules and repeated-customer deduplication; do not compare a list producer to a scalar count producer. |
| Q22 | Escaped literal customer/product search; normal | Available: `ContainsLiteral`, `StartsWithLiteral`, or explicit `Like` (`D/R`). Freeze the chosen business predicate. | `S`: identical escaping and allowed collation. Seed `%`, `_`, escape characters, and empty values; keep an explicitly comparable primary character set and report Unicode edge cases separately. |
| Q23 | Create an order and consume returned fields; normal write | Available: `InsertReturningAsync` (`O`). Include normal entity/parameter preparation and completion; list application-owned entity allocation separately. | `S`: matching INSERT RETURNING and transaction boundary. Verify affected row, returned values, and durable row; include equivalent decoding. |
| Q24 | Patch only note/version, including explicit NULL; normal write | Available: `Changes<T>.Set` and `UpdateAsync` (`O`), or root-only Fluent update (`D`). | `S`: exactly the same SET columns and predicates. Verify written NULL versus omitted columns; money/settings must remain unchanged. |
| Q25 | Two writers race an optimistic version update; separate contention scenario | Available: `UpdateCheckedAsync` (`O`). Freeze the shared key/version and retry policy. | `S`: matching version predicate and affected-row check. Record both planned operations, winner, stale-version conflict, retries, durable values, and final version; never omit losers from counts. |
| Q26 | Transaction reads validation state, updates order/detail, then commits; normal write | Available: `InTransactionAsync` or explicit `BeginTransactionAsync` (`O`). Use the same public route before/after. | `S`: same BEGIN/isolation, read/write order, COMMIT, and acknowledgment boundary. Verify cross-table invariant and durable state. |
| Q27 | Business failure after partial transaction work, followed by rollback; separate fault scenario | Available: transaction callback/explicit rollback (`O`). Preserve original business exception and recorded transaction outcome. | `S`: same partial work and ROLLBACK. Check no partial durability, reusable connection or documented discard, and original error versus cleanup error. |
| Q28 | Bounded batch insertion of order details; normal write | Available: `InsertManyAsync` (`O`). Freeze batch size, all-versus-per-batch atomicity, input enumeration, and generated/owned results. | `S`: same insert batching and parameter counts. Native COPY is a separate optimization comparison, not the equivalent primary cell. Verify rows, batch progress, atomicity, and duplicates/errors. |
| Q29 | Upsert using an explicit unique conflict target; normal write | Available: `UpsertAsync` (`O`). Freeze update columns and insert/update branch distribution. | `S`: same conflict target and update expressions. Verify both insert and update branches, affected rows as each provider defines them, and durable business values. |
| Q30 | Version-checked deletion of a detail record; normal write | Available: `DeleteCheckedAsync` (`O`). Expected-conflict variants belong to the separate contention classification. | `S`: matching key/version delete. Verify affected row, parent retention, stale version handling, and durable deletion. |

## Lifecycle, cancellation, and overload scenarios

These are separately measured boundary scenarios. They do not inflate the count of thirty semantic business cases and are not silently mixed into zero-allocation normal-path claims. All statuses are **pending**.

| ID | Boundary | Required observation and oracle |
| --- | --- | --- |
| E01 | Cancellation after genuine asynchronous suspension | Prove work started and suspended; pre-cancellation is a different cell. Observe business cancellation, callback completion, native drain/retirement, transaction state, and connection reuse/discard. |
| E02 | Early break after a fixed row of a large stream | Count rows actually consumed and batches transferred; await enumerator disposal; verify cursor/buffer retirement and transaction usability. Do not introduce PostgreSQL cancel-key semantics that abort a previously usable enclosing transaction. |
| E03 | Pool exhaustion and bounded admission timeout | Preserve planned, started, completed, rejected, and timed-out requests; record waiters, pool capacity/high water, and timeouts. Report exceptional allocations separately. |
| E04 | Saturation followed by admission stop and recovery | Freeze overload duration and recovery probes; record drain time, restored success/latency, native owners, CPU while idle, RSS/PSS, and retained capacity. |
| E05 | Savepoint rollback followed by successful outer commit | Verify only the savepoint-local work is undone, remaining work persists, and transaction/session state remains correct. |

Provider-specific supplementary cases may include PostgreSQL row locks and expert-SQL JSON-path/correlated subqueries. Mark unsupported Fluent cells explicitly. Error, cancellation, initialization, capacity growth, and steady-state success are separate allocation categories.

## Actual preparation and protocol boundaries

The fixed [managed terminals](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Query.Fluent/Terminals.cs), [native query implementation](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/native/cpp/src/query.cpp), and [provider implementation](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/native/cpp/src/provider.cpp) establish these distinctions:

1. `PreparedQuery<T>` reuses a source-bound `NativePlan` and bounded compiled shape. Each execution still binds/copies its own values and creates a stream/operation through the current API.
2. SQLite currently prepares a new `sqlite3_stmt` with `sqlite3_prepare_v3`, binds parameters, steps rows, and finalizes the statement. `SQLITE_PREPARE_PERSISTENT` alone does not establish a statement cache.
3. PostgreSQL currently sends unnamed Prepare and waits for completion, sends DescribePrepared and waits, then sends QueryPrepared at first fetch and enables single-row mode. Unknown extension metadata can require an extra catalog query and re-prepare.
4. Protocol confirmation uses an explicit Sync/ReadyForQuery exchange where required by session/cleanup semantics. Do not remove confirmation from one column without reporting a changed contract.
5. The native diagnostics export counts SQL dispatches and libpq submissions separately. Neither counter is a TCP-packet count or a measured physical round-trip count. Measure/trace physical request-response boundaries independently when that metric is claimed.

A direct C++ reusable variant may retain a native prepared statement under its normal driver contract; this is a real difference from current Korda and must remain visible. Add a matched physical-statement lifecycle subtest to isolate it. Do not relabel a shape-cache comparison as database-statement reuse.

## Direct C++ semantic obligations

- Use the same locked Clang Release profile, C++ standard library, SQLite source/compile options, and libpq source/patch provenance. Link only direct database dependencies, not the Korda execution layer.
- Build dynamic queries and bind values within `D` timing. Reuse prepared statements only within an explicitly declared `R` mode. Save the actual SQL and ordered parameter types/values outside the hot loop.
- Decode and consume equivalent results, including owned strings, JSON members, exact monetary values, NULLs, and DTO-equivalent fields. For scalar/no-result operations, match the scalar/affected-row contract.
- Preserve parameter lifetime and copying guarantees. A borrowed native buffer may differ from the framework's immediate snapshot; record the difference and add a matched ownership subtest instead of hiding it.
- Match libpq result formats: current Korda requests binary results. A text-only direct probe is connectivity evidence, not the final matched business baseline.
- Preserve begin/commit/rollback boundaries, durability, early-disposal drain, cancellation, and finite connection/pool limits. Drain to the final result boundary and discard an unconfirmed protocol session.
- Record native allocation/free counters and peak native heap separately. Managed allocation metrics for direct C++ are not applicable, never zero-valued managed achievements.
- `poll` with a twenty-millisecond timeout is event-driven and can return earlier. Source inspection alone does not prove a fixed twenty-millisecond delay or identify a measured bottleneck.

## SQL, plans, and execution accounting

Capture query text, ordered parameter types and values (or a reproducible non-secret input manifest), result shape, SQL execution count, protocol submission count, and separately established physical network round trips. PostgreSQL and SQLite must each retain four real-route columns even when SQL differs.

For PostgreSQL, collect `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` outside timing with the same parameters and statistics. For mutating statements use a dedicated copy or a transaction with verified rollback so plan collection does not alter the measurement seed. Save actual rows, plan tree, buffers, and server settings. For SQLite, save `EXPLAIN QUERY PLAN`, the schema/statistics/compile-option state, and relevant statement-status counters; add bytecode `EXPLAIN` where a concrete discrepancy needs explanation.

If an ORM emits different SQL or selects a different plan, retain that real result and add a same-SQL layer. Do not replace its real route with hand-written SQL in the main ORM column. SQL preparation, metadata probes, administrative queries, business queries, and transaction commands need separate counts when available.

## Allocation boundaries

For every supported normal path record per-operation, per-batch, and per-row framework allocation, as well as end-to-end managed allocation. The report starts with raw cumulative bytes, operations, batches, rows, and generation collection counts; ratios come afterwards. Include callbacks, native completion adapters, ThreadPool work, and other managed worker threads using independent consumer processes and precise process-total allocation counters after warmup.

Application-requested DTOs, strings, lists, and result arrays are separate named categories. Framework temporary arrays, closures, boxing, async/wait state, leases, and pool growth remain framework costs. Use allocation stacks, an empty-driver control, or isolated path verification for attribution. Zero observed collections, a missed sample, and a rounded zero mean do not establish zero bytes.

The existing [Fluent test cost probe](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/tests/Query.Fluent/Program.cs) performs only sixty-four synchronous composition/SQL-render iterations using current-thread allocated bytes. The [streaming fixture](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/tests/Data.Streaming/Program.cs) records a broader fixture-lifetime total. Neither completes this batch's real-provider, public-package, asynchronous steady-state requirement.

Report finite pool capacities, native bytes/copies, heap/RSS/PSS peaks, and idle retention with any allocation reduction. For normal, genuinely suspended, and high-concurrency cases, a zero claim requires exact version/input/boundary bindings and repeatable raw counts. A remaining framework allocation is `not_met`; uncertain attribution is `unproven`.

## Load sequence and eight long segments

Use an exclusive, dedicated Linux measurement environment. Calibration, warmup, draining, and idle observation are outside the thirty-minute valid load interval. Interleave independent short-run processes to estimate noise before freezing the sustainable offered-load schedule. Compare latency at that common sustainable load, then separately search maximum successful throughput under identical error-rate and tail-latency limits.

The long-run order must be fixed before execution and should alternate columns/databases to expose drift, with each segment restoring its matching database seed. No two measured clients or unrelated benchmark campaigns share the assigned resources. This document does not assert that a dedicated host is available.

| Segment | Database | Column | Valid mixed load | Status |
| --- | --- | --- | --- | --- |
| L01 | PostgreSQL | Direct C++ | at least 1,800 continuous seconds | pending |
| L02 | PostgreSQL | Before Korda | at least 1,800 continuous seconds | pending |
| L03 | PostgreSQL | After Korda | at least 1,800 continuous seconds | pending |
| L04 | PostgreSQL | Independent C# ORM | at least 1,800 continuous seconds | pending |
| L05 | SQLite | Direct C++ | at least 1,800 continuous seconds | pending |
| L06 | SQLite | Before Korda | at least 1,800 continuous seconds | pending |
| L07 | SQLite | After Korda | at least 1,800 continuous seconds | pending |
| L08 | SQLite | Independent C# ORM | at least 1,800 continuous seconds | pending |

IDs identify cells, not a mandated chronological order. Require at least 14,400 seconds of valid exclusive mixed load overall; shorter probes cannot be added together and called a complete continuous segment.

For each segment save machine/kernel/CPU and allowed-core identity, affinity and quotas, database and driver versions, package/native/executable hashes, seed and load manifest, UTC start/end, monotonic elapsed interval, raw time series, and validation outcomes. Record planned starts, actual starts, completions, failures by class, rejections, retries, and pending work. Measure latency from planned admission and actual start separately so queueing and rejected work cannot disappear.

Report success ops/s, rows/s, p50/p95/p99, client user/system CPU seconds, CPU seconds/successful operation, idle CPU, steady/peak RSS, PSS when available, native heap peak, and post-drain retained memory. Managed columns also report cumulative managed bytes and GC counts with per-operation/per-row ratios. PostgreSQL server CPU/memory are separate from client values; SQLite engine cost is in-process. Save diagnostics proving that cursors, operations, buffers, leases, and native owners return to zero or the declared source/pool steady state.

## Reusable production and verification tooling

The [dependency lock](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/native/dependencies.lock.json) pins LLVM/libc++ 23.1.5, CMake 4.3.3, Ninja 1.13.2, libpq/PostgreSQL 18.0, SQLite 3.51.3, nlohmann/json 3.12.0, archive hashes, and the libpq explicit-configuration patch. Collect actual build/runtime evidence as well; a lock file is not a run receipt.

- `eng/cpp_toolchain.py`, `eng/postgres-tools.sh`, and `eng/task07_native.py` supply the locked native producer paths.
- `eng/build.py` and `eng/ci/bundles.py` produce independent provider candidates.
- [Package consumers](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/eng/ci/consume.py) and [order consumer verification](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/eng/ci/orm_experience.py) already copy consumers outside the tree, use PackageReference, check Native AOT ELF output, verify provider isolation and native SHA, and prove DTO-only edits reuse the packaged native image.
- The order sample finds the actually mapped native image in `/proc/self/maps`; preserve this identity check outside the timed region.
- `nw_db_diagnostic_count_v1` supplies six native owner/handle counts and separate SQL/protocol counts. Existing test helpers allocate an array on every read; use a non-allocating measurement adapter if reading during allocation timing.
- [Module registration](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/eng/ci/modules/README.md) and `eng/ci/impact.py` own affected-module routing. Register short correctness/allocation/AOT regressions. Keep the dedicated long campaign out of ordinary PR CI.

No benchmark execution, eight-segment completion, independent ORM coverage, package acceptance, or zero-allocation claim is established by this workload specification.
