# DB-Perf-01: shared workload adaptation plan

## Scope and current status

This is an implementation plan derived from the frozen, uncommitted `concurrent-snapshot-001` source, not a measurement or a claim that its thirty queries already run successfully. It supplements [workloads.md](workloads.md) and the [snapshot review](reviews/concurrent-native-stream-snapshot-001.md). All new shared-contract cases and adapters below are **pending**.

Use the snapshot's thirty read names as the first common integration set. Keep the existing five-case results explicitly scoped to those five cases. Do not compare a thirty-case Korda mix with a five-case native mix. Add transaction, mutation and boundary scenarios as explicit new IDs rather than changing an existing read ID's meaning.

Source bindings:

| Source | SHA-256 |
| --- | --- |
| Snapshot `managed/Korda/Workload.cs` | `ad455ffd39c89a3b2a978a742f3cf21fbcc013985cfe6c2e5bf493dd0973e6bd` |
| Snapshot `managed/Korda/AdvancedCases.cs` | `f26c7634e4cc12b4f14a608272b5dcbc290e406947e4eb0660fd5b67ad16d427` |
| Snapshot `managed/Korda/Dataset.cs` | `211083033651ce526a88bee130ab8f817a41b72dcc0b211dbcf287e190cc3f0a` |
| Snapshot `managed/Korda/Models.cs` | `56af58130abffd7b4cc0b7f4f82d4a591ecd66ce248b435f41ef1a910ce099ec` |
| Snapshot `managed/Korda/Options.cs` | `828098643b57cdc04b06890ed108d5d04a5958814bd8a02cd29df628977ebbdc` |
| Actual independent ORM probe `orm-probe/evidence/result.json` | `2c5140c773461e2852579698d41e9127f8de8d2f57e5569af3fb1e175a71bd09` |

The snapshot-relative prefix for the first five files is `benchmarks/db-perf/`. The actual probe is in `/workspace/scratch/754bc732518e/orm-probe`. Its successful support check used Dapper 2.1.79, Dapper.AOT 1.1.0, Npgsql 11.0.0, and Microsoft.Data.Sqlite.Core 11.0.0 with SQLitePCLRaw.provider.sqlite3 2.1.11. The snapshot's separate Dapper project requests different Dapper and SQLitePCLRaw versions; it must not inherit that probe's validation status. Freeze exact package archives and lock files for the chosen implementation.

## Freeze one contract before writing adapters

The shared manifest must describe the business work independently of any one runner. A single checked-in generator can emit provider SQL, typed parameter vectors, result metadata and independent expected digests from the seed formulas. Actual Korda `ToSql()` and actual execution bindings must be compared with this input outside timing; inferred SQL is not sufficient evidence. Preserve casts, NULL ordering, aliases, set-operation ordering and parameter order. PostgreSQL aggregate casts are particularly relevant: the fixed product's `native/cpp/src/query.cpp` lines 1391–1424 apply type-dependent casts, so a handwritten `SUM(bigint)` must not silently change its result type.

Minimum manifest fields:

| Field group | Required content |
| --- | --- |
| Identity | Schema version, manifest hash, semantic case ID, implementation variant ID, seed/schema/index hashes, provider dialect. |
| Operation | Ordered SQL steps, transaction boundary and isolation, query-construction mode, public Korda entry, direct-native preparation mode, Dapper API entry. |
| Construction | Case-specific clause/fragments or a bounded structured query description that can be assembled inside a dynamic operation; a pre-rendered SQL string for reuse mode. |
| Parameters | Ordered names/placeholders, logical and physical types, NULL flags, fixed values or deterministic input-sequence references; decimal precision/scale and JSON representation. |
| Results | Ordered aliases, logical types, provider physical types/OIDs where relevant, nullability, materialization kind, row ordering, expected row count and independent digest. |
| Grouped results | Parent input sequence, composite keys, ordinal encoding, empty-group and duplicate-key behavior, child sort rule, total row count. |
| Mutations | Expected affected rows, expected conflict category, returned fields, pre-state and durable post-state oracle, transaction acknowledgment boundary. |
| Scheduling | Exact case/parameter sequence or weights and PRNG algorithm/seed; worker assignment; offered-load schedule and recovery policy. |
| Limits | Maximum input/result/batch rows, byte limits, statement-cache capacity, connection count, timeout and cancellation boundary. |

Every executable should reject an unsupported case or mismatched manifest hash before announcing readiness. A missing case is a visible capability gap, not an opportunity to run another query under its name. Record results by semantic ID and route, retaining distinct before/after Korda columns even though their consumer source is shared.

## Thirty read mappings

The table transcribes the frozen source semantics. `N` is orders per tenant, `R` requested rows, and `B` maximum parent batch rows. Unless otherwise specified, reads are for tenant 1 and have deterministic final ordering. `D/R` means construct a query inside the operation or reuse its immutable shape respectively; it does not imply physical driver statement reuse. `O` is a normal operation API without a public prepared-plan overload.

For all rows, native uses direct libpq/sqlite3, while Dapper uses a statically typed AOT-intercepted call site and the actual provider. Both must materialize the listed business shape and consume all fields. The SQL shown by descriptions below is semantic notation, not an asserted byte-for-byte exported query.

| ID / snapshot name | Frozen semantics and result shape | Native / Dapper adaptation and oracle | Mode |
| --- | --- | --- | --- |
| R01 `numeric` | First `R` order IDs, ascending. Scalar Int64. | Existing scalar reader; consume all IDs and row count. | D/R |
| R02 `text` | Same population; `Id`, nullable `Note`. | Owned `TextRow`, preserving NULL versus empty; hash both fields. | D/R |
| R03 `money` | Same population; `Id`, exact `Total`. | Owned `MoneyRow`; PostgreSQL numeric(18,2), SQLite integer cents; hash exact signed cents. | D/R |
| R04 `json` | Same population; `Id`, typed `Settings`. | Owned settings object with Channel and Gift; include decoding before digest. | D/R |
| R05 `wide` | All nine order fields for the same first `R` rows. | Full owned order DTO, nullable customer/note, exact money, JSON and memo; consume every field. | D/R |
| R06 `optional-filter` | `WhereIf(true)` restricts CustomerId to 2, then first `R` IDs. | Same optional predicate construction and result. Add false/NULL variants with separate variant IDs; the frozen case alone does not cover omitted filtering. | D/R |
| R07 `range` | CreatedAt in `[1700000100,1700000200)`, first `R` IDs. | Int64 bounds; expected IDs from seed timestamps, including tied timestamps. | D/R |
| R08 `left-join` | Order left join customer by nullable CustomerId; first `R` orders. | `JoinRow(Id, Name?)`; retain unmatched orders with NULL name. | D/R |
| R09 `inner-join` | Same join with only matching customers, first `R` joined orders. | Same DTO shape; exclude NULL foreign keys; do not change LIMIT placement. | D/R |
| R10 `null-notes` | Orders with NULL Note, first `R` IDs. | Scalar Int64; compare exact multiples-of-five population from seed. | D/R |
| R11 `literal-note` | Non-NULL note containing literal `note-1`, first `R` IDs. | Preserve literal-search escaping and collation. This fixed input lacks wildcard characters; broader escaping checks are separate variants. | D/R |
| R12 `customer-totals` | Group by nullable CustomerId; HAVING count greater than 3; order customer ascending with NULL last. | `CustomerTotal(CustomerId?, Count, Total?)`; all groups, no implicit `R` limit. Presence markers distinguish NULL aggregate from zero. | D/R |
| R13 `product-totals` | Group tenant-1 lines by Product; HAVING summed Quantity greater than 10; product ascending. | `ProductTotal(Product, Quantity?)`; all groups; preserve product ordinal ordering and product's Int64 aggregate cast. | D/R |
| R14 `empty-sum` | SUM(Total) for nonexistent tenant -1. | One nullable-money scalar row whose value is NULL. Empty result and zero-valued result are wrong. | D/R |
| R15 `cursor` | Seek after `(CreatedAt(N/2), 1, N/2)` with CreatedAt/TenantId/Id ordering; take `R`. | Preserve full lexicographic cursor predicate and tie breakers; expected IDs are the suffix after `N/2`. | D/R |
| R16 `offset` | Same order tuple; skip floor(3N/4), take `R`. | Apply deep OFFSET before materialization; expected page differs from the cursor case. | D/R |
| R17 `exists` | Return first customer ID if an uncorrelated tenant-1 order subquery contains Id at least 32. | This is explicitly uncorrelated in the snapshot. Expected one row `1` for admitted N at least 32; do not substitute a correlated EXISTS. | D/R |
| R18 `in-subquery` | Customer IDs present among non-NULL CustomerId values of tenant-1 orders with Id greater than 128; ascending, take `R`. | SQL membership deduplicates customers; preserve SQL NULL behavior and subquery tenant restriction. | D/R |
| R19 `cte` | CTE selects tenant-1 order IDs greater than 16; outer ID order and limit `R`. | Same CTE body/projection; hash selected IDs and preserve actual planner choice. | D/R |
| R20 `window` | ROW_NUMBER partitioned by nullable CustomerId, ordered CreatedAt/Id; final Id order, take `R`. | `RankRow(Id, Rank)`; compute ranks over the full qualifying partition before outer LIMIT. | D/R |
| R21 `union-all` | IDs 1..16 combined with IDs 9..24, preserving duplicates; final ID order. | Scalar Int64 stream; exactly 32 rows for admitted N; eight overlapping IDs appear twice. | D/R |
| R22 `union` | Same two inputs with duplicate elimination. | IDs 1..24 once, 24 rows. | D/R |
| R23 `intersect` | Intersection of the same inputs. | IDs 9..16 once, eight rows. | D/R |
| R24 `except` | First input minus second input. | IDs 1..8 once, eight rows; preserve operation direction. | D/R |
| R25 `running-total` | Tenant-1 order lines; running SUM(Quantity), ROWS unbounded preceding through current row, line Id order; take `R`. | `RunningRow(Id, Quantity?)`; window calculation precedes limit and retains the expected result type. | D/R |
| R26 `three-join` | Orders inner join customers and lines; order by order Id then line Id; take `R` joined rows. | `DetailRow(OrderId, Name, Product, Quantity)`; all selected fields, LIMIT on joined rows rather than parent orders. | D/R |
| R27 `anti-association` | Orders whose ID is not in tenant-1 lines having Quantity at least 5; first `R` IDs. | This includes empty associations and orders whose lines all have smaller quantities. It is not merely an empty-child query. | D/R |
| R28 `nullable-order` | Orders sorted CustomerId NULL first then Id; take `R` IDs. | Explicit NULL ordering and within-group Id ordering in both dialects. | D/R |
| R29 `raw-sql` | Parameterized expert SQL returns Id/Note for the first `R` tenant-1 orders. | Same result as R02 through the public raw-SQL route; retain as an API-layer variant, not an additional semantic business query when counting coverage. | D/R command |
| R30 `related` | Composite keys for parents 1..min(R,B,N); one bounded UNION ALL association query, one group per input parent. | Materialize all child DTOs and owned groups, including empty groups; sort each group by child Id before the same parent/count/child digest. Preserve ordinal and child count. | O |

The base five materializers can be extended with nullable money, JoinRow, CustomerTotal, ProductTotal, RankRow, RunningRow, DetailRow and an ordinal-bearing child row. A common type dispatcher is useful inside the native implementation, but it must create the equivalent owned DTO and any requested collection before consumption, not merely fold provider bytes directly into a digest.

For Dapper, avoid a generic open-ended `Query<T>` helper that has not demonstrated AOT interception. Use explicit, statically typed call sites for each row shape, preserve generated interceptor output, and fail AOT warnings. Query construction can still supply a runtime SQL string. Source-generated JSON decoding and exact money conversion must occur inside the measured materialization path; any transport DTO or helper allocation required by the adapter remains visible in end-to-end allocation and must not be silently classified as user-requested business storage.

R30 deserves its own allocation decomposition. The current public API snapshots keys, composes one native query, buffers indexed child rows, and constructs groups. [RelationBatch.cs](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/src/Orm.Relations/RelationBatch.cs) defines owned group lists, no implied child order, duplicate input keys retaining separate positions, and an empty-input no-SQL result. Native/Dapper should return the same group contract and perform the same caller sort. The operation still constructs its query in both current managed modes; there is no public `PreparedQuery` overload to imitate. Capture its actual generated SQL instead of retaining the descriptive placeholder currently used in `Workload.Sql`.

The read matrix should additionally exercise duplicate parent keys and empty key input as variants, and large `R` values for streaming. Those variants improve coverage without inflating the number of semantic cases. Likewise, D/R, two providers, and before/after binaries are separate measurement cells, not extra business queries.

## Transaction, mutation and cancellation extension

Preserve the first thirty read IDs and create new scenario IDs. Reserve a mutation partition outside the immutable tenant-1 oracle population, or include state evolution explicitly in every expected read. A separate worker-owned key range keeps ordinary success workloads deterministic; a deliberately shared hotspot belongs to the contention scenario. Freeze the same initial state before each independent process and every long segment.

| Proposed ID | Classification and public Korda entry | Native / Dapper equivalent and verification |
| --- | --- | --- |
| W01 `insert-returning` | Normal write: `InsertReturningAsync`. | Same bound INSERT RETURNING fields, one owned returned DTO, affected-row check and persistence check. Use deterministic unique keys and bounded data lifecycle. |
| W02 `partial-update` | Normal write: `Changes<Order>.Set` plus `UpdateAsync`; include explicit NULL. | Exact SET columns and composite key; verify affected rows and that omitted money/settings/memo remain unchanged. Do not replace with full-row update. |
| W03 `transaction-read-write-commit` | Normal transaction: public `InTransactionAsync` or explicit transaction, frozen once for both Korda versions. | Same BEGIN/isolation, validation read, update, returned/read-back data and COMMIT acknowledgment; durable cross-field/table invariant checked after completion. |
| W04 `bounded-bulk` | Normal write: `InsertManyAsync`, fixed batch size and declared atomicity. | Same input enumeration, row and parameter counts, statement batching and transaction boundaries. Direct COPY or a different bulk protocol is an additional layer. |
| W05 `upsert` | Normal write: `UpsertAsync` with explicit conflict target. | Same unique target, SET expressions and frozen insert/update branch distribution; verify affected-state behavior per provider. |
| W06 `checked-delete` | Normal write with a current expected version: `DeleteCheckedAsync`. | Same key/version predicate and affected-row check; verify parent and unrelated state. Stale-version behavior is a separate conflict variant. |
| X01 `optimistic-conflict` | Contention scenario: two admitted writers call `UpdateCheckedAsync` against one version. | One winning transition, one expected conflict, identical retry policy. Count both attempted operations and all retries; verify final version and value. |
| X02 `rollback-after-partial-write` | Fault scenario: callback throws a known business error after update. | Same partial operations followed by confirmed ROLLBACK; original business failure remains identifiable, no partial durability, and connection state is checked. |
| X03 `cancel-after-suspension` | Boundary: caller cancellation after an observed real asynchronous wait. | Define the admitted operation, cancel point, terminal outcome, drain/rollback and reuse/discard policy per provider. A pre-canceled token or artificial `Task.Run` wrapper does not prove provider suspension. Missing ORM/provider support remains an explicit gap. |
| X04 `early-stream-stop` | Boundary: end enumeration after a fixed consumed row count. | Equivalent borrowed/owned result release and protocol retirement; count actual fetched and consumed rows separately and verify transaction usability. Do not substitute a PostgreSQL cancel-key abort for an ordinary reader drain. |
| X05 `savepoint-rollback` | Boundary: rollback inner work, then commit surviving outer work. | Same savepoint statements, transaction scope and post-state invariant. |

W01–W06 can participate in the normal mixed campaign after their state model and fixed distribution are validated. X01–X05 remain separately reported contention/fault/boundary measurements; expected conflicts or cancellations must not disappear from the planned/started/terminal counters or masquerade as normal success allocation.

The existing sample establishes current public mutation and transaction routes at fixed commit [orm-experience/Program.cs](https://github.com/IzuSharp/Korda/blob/771bc77cbd68d3f932b99ed2497c0697bbba5f02/samples/api/orm-experience/Program.cs), including partial version update, stale conflict, insert-returning, preservation of the business exception, and confirmed rollback. The independent ORM probe demonstrated a small real commit and rollback; it did not validate the proposed combined scenario, contention or cancellation.

## Construction, preparation, errors and accounting

Dynamic mode assembles the actual query inside each operation from its semantic clauses and the current parameter inputs. Loading or copying a complete prepared SQL string is not dynamic construction. Reuse mode keeps the compiled Korda plan or the native/Dapper SQL shape per worker, then performs fresh binding and full result consumption. Physical driver statement reuse is a separate flag and layer; native and Npgsql settings must state it explicitly. Keep capacities finite and record warm-cache entry counts.

Default recovery should be common across all runners: classify the failed attempt, complete or abort its transaction, confirm protocol retirement or discard the uncertain connection, reestablish the worker connection if allowed by the frozen policy, and continue with the next scheduled operation. Retrying the same operation is a separate admitted attempt with a bounded count. Never continue using a connection whose protocol or transaction state is unknown. The previous native stop-on-first-error and managed continue-on-error loops are not a shared policy.

Count planned admissions, actual starts, successes, expected business conflicts, cancellations, unexpected failures, retries, not-started work and in-flight operations. Keep an invariant that accounts for every admitted operation. Measure both scheduled-to-completion and actual-start-to-completion latency. Record successful latency and unsuccessful outcomes separately; failure-heavy throughput must not appear better because rejected or queued requests were omitted.

Each operation digest should be validated against the independent oracle, not only against a different adapter's output. For stateful operations, the completion journal and a post-run database check establish the durable oracle. Capture exact per-case SQL, typed bindings, provider plan, SQL execution count and protocol submission count outside the timing window. Physical network round trips remain unmeasured unless separately instrumented.

## Minimal implementation sequence and ownership

1. **Freeze contract v2 and a validator.** Export all thirty Korda SQL/parameter/result contracts from a fixed source and real provider; reconcile against the independent seed formulas. Add unique case/semantic IDs, exact parameter and column metadata, statement-lifecycle flags, group semantics and a schedule hash. Reject duplicate IDs and unsupported types before running.
2. **Implement one native consumer in this session only.** Authorized directory: `Korda-DB-Perf-01-linux/benchmarks/Database/campaign/native`. Reuse the reviewed source's direct-driver techniques only after adapting them to the new contract. Extend typed materializers and SQL construction; preserve actual runtime identity, effective configuration, bounded caches and resource accounting. Do not modify the earlier validated `benchmarks/Database/native` probe.
3. **Implement Dapper from the successful support probe.** Use its actual locked package versions, explicit typed AOT call sites, the same SQLite library identity/compile options and the shared schema. Add the thirty-case dispatch and complete consumption; record generated interceptor files and loaded libraries. Do not claim a LINQ/Fluent translator for this micro-ORM column.
4. **Adapt the common Korda consumer.** Feed the identical schedule to before/after independent PackageReference applications; assert exact manifest support and preserve real public Fluent/operation routes. Capture SQL without moving per-operation construction outside timing.
5. **Run a short semantic gate first.** Every case on both databases must match row/digest/NULL/type/ordering/owner expectations. Probe the dynamic and reuse variants, empty/duplicate association input, numeric boundaries and large streaming input. Treat these as correctness results, not a campaign.
6. **Add the mutation state model and boundary adapters.** Implement W01–W06 and X01–X05 with explicit state, transaction and recovery semantics. Confirm durable database state and terminal owner counts. Keep unsupported cancellation/suspension cells visible.
7. **Complete campaign metering.** Add shared offered-load timing, per-case accounting, native allocation/free and peak observations, whole-process managed allocation/GC, actual configuration read-back, independent PostgreSQL server samples and drain/idle observations. Calibrate and interleave short independent processes before freezing the long-run schedule.
8. **Run qualifying long segments only after the preceding gates.** Use the exclusive dedicated Linux environment and the eight-cell schedule in `workloads.md`; no compilation or other route may compete for its assigned resources during a measured interval.

The native adapter needs the frozen manifest path and process protocol before implementation: CLI/stdin input format, ready/start/stop/drain handshake, output schema, shared recovery rules, driver/toolchain paths and connection settings. This planning record makes those dependencies explicit; it does not create or modify shared runner files or source in the concurrent workspace.
