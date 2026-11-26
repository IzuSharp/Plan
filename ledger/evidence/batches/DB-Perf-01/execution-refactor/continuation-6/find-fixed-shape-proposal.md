# Fixed-key Find: next source-derived candidate

Read-only proposal against public `8789a45a52cc0cc0a0b62737542d9c120b753c9b`
(local `d8beff6`, tree `c8f398ae4db2d39302335a51a6378b737409f2fb`). No product
implementation or performance run is part of this audit. Measure the new
one-shot command candidate first. The earlier 316 transaction allocation total
does not isolate Find, so it cannot be assigned wholly to this path.

## What is repeated today

| Layer | Actual path and consequence |
| --- | --- |
| Public Find | `Orm.Relations/Crud.cs:19–41`: CheckKey → CheckOpen → pre-cancel; then `From(table)` for every call. Each key value becomes its own NWDB ExpressionValues frame, column/value/binary nodes and clause. SelectAll ends in SingleOrDefault. |
| Managed command | `QueryCommand.cs:14–56`, `QueryContext.cs:18–25`: each new command creates records and shape/dependency/origin collections; QueryContext adds parameter/projection state and cancellation ownership. `Query.cs:500–508` rebuilds all root column tokens. |
| Seal | `QueryCommand.Submission.cs:109–133` encodes/copies the complete NWQC command and calls compile. `query.cpp:2807–2822` replays and eagerly compiles it. The single-root scratch path avoids one heap envelope but still copies and replays the records. |
| Existing shape cache | `query.cpp:2876–2954,3039–3074`: each new NativePlan first compiles its own SQL/layout; only then ShapeCache.acquire hashes/looks up the immutable shape. It does not bypass current Find's builder, tape or compilation work. |
| Existing useful state | `Metadata.cs:137–144` already owns immutable keys, canonical model and Table.Row; DataSource caches registered models/codecs. PreparedQuery already caches a source-bound NativePlan, parameter layout and stream projection proof. |

The actual Korda generated Order mapping constructs Order directly through nine
typed `RowReader.Get` calls. Their ordinals are fixed column metadata, not a
per-row name search. Dapper's actual `RowFactory3` tokenizes columns once for a
reader, then uses typed getters/handlers and directly calls the nine-argument
Order constructor. The new matched Find factory writes tenant/id/take Int64
directly. Neither emitted reader proves zero allocations; Order, strings, JSON
and Dapper's handler-token state still have their own ownership/allocation.

## Recommended shortest target

Keep the public `FindAsync(table, key, token)` and its existing generated/manual
Table.Row. Introduce a **source/model-bound immutable Find shape** with the exact
current SELECT, ordered composite key slots and fixed Int64 LIMIT 2. Build it
once under bounded cache admission. Each Find then validates its already-owned
EntityKey snapshot, writes only changing key bytes into one existing validated
NWDB value frame, captures an independent execution and uses the existing lazy
CursorPull → TypedStream.SingleOrDefault → generated Table.Row path.

Cache SQL/expected parameter and projection metadata. Keep provider preparation
and result description fresh for each execution. Do not introduce another
operation completion channel, command-tape format, managed SQL compiler,
reflection fallback or boxed key decode/re-encode.

The lowest-risk implementation reuses NativePlan/CompiledShape/BatchView and
CursorPull business/lifetime helpers, with **private model-key slots**. A small
private fixed-Find factory may be appropriate; no new ABI is prescribed here.
If it returns an immutable plan, the existing plan-pull factory can consume it;
if it directly creates the lazy pull, it must reuse the same capture/open path.
Its cold compiler should reuse the C++ renderer and whole-key/codec validation,
not rebuild arbitrary Fluent operations every call. Retain source-bound
capability and finite-demand checks even on cache hits.

Simply wrapping current Find in public Parameter/Prepare is insufficient:

- `Source` creates a global ParameterRegistry bounded by MaxQueryNodes;
  `QueryCommandReplay::commit` registers every public parameter there. An
  implicit LRU plan that reallocates parameter IDs on each miss can exhaust a
  public registry that old Find never used. Internal fixed slots must not
  consume or collide with caller parameter identities.
- Terminal 3 currently imposes LIMIT 2 and is single-use; terminal 8 enables
  reuse and requires prepared capability. Ordinary Find must not silently gain
  a new prepared-capability requirement. Keep fixed shape reuse separate from
  public terminal/admission semantics. A private repeatable plan can retain
  terminal-3 SQL/cardinality without exposing its mutable submission flag.
- Adding `.Take(2)` to a new public builder emits the same SQL limit through
  Renderer.selection, but adds a builder node and can change low-limit
  admission. Cached shape accounting must retain the original logical demand.

Source ownership is the natural lifetime. A static Table must not hold a
native plan from one engine/source or a Session. Native cache entries can share
immutable SQL by exact model/profile/codec/projection identity; managed row
mapping must stay tied to the exact Table.Row/delegate. Two descriptors with
equal metadata hashes can have different materializers. Both entry count and
bytes require bounds; eviction/Source closure removes cache ownership while
already captured executions retain independent native references.

A model generator can later emit a deterministic key-slot template. It should
not be required for this first change: handwritten descriptors need the same
path, and runtime cold compilation amortizes the repeated structure already.
Source generation must never invoke the native compiler, database or getters
at build time. Further row-reader specialization should wait for isolated
evidence; current generated getters already know their ordinals.

## Contracts and concrete validation needed

| Obligation | Existing anchor / added case required |
| --- | --- |
| Identical SQL and business result | Existing queries-v3 full lifecycle SQL plus new matched Dapper contract. Require same quoted/qualified nine-column SQL, complete ordered tenant/key predicate and Int64 LIMIT 2; one dispatch per Find. |
| Absence and duplicates | Orm.Relations.Program Crud checks null and found row; Failures.SchemaMismatch creates two physical rows under a declared key and requires InvalidOperationException. Keep reading/validating the second row and actual cleanup. |
| Exact key and error timing | MutationEncoding.CheckKey and EntityKey.And/RequireComplete run before native work; preserve invalid/foreign/incomplete key before closed/canceled ordering. Test already-canceled cold Find without cache creation/provider dispatch. |
| Independent values | Retain Key/And snapshot copies before Find, configured codec and MaxLength validation; alternate key values, mutate caller-owned byte input after Key, and run the cached shape on two same-source sessions. No re-read of business getters after await. |
| Owner and mapper identity | Two equal metadata tables with different materializers must each run their own mapper. Test cross-source rejection, cache eviction while an accepted fetch is held, source close, mapper throw, cancellation, and all owners including 8/9 returning to zero. |
| Bounded cache and public identity | Repeated eviction must not consume public ParameterRegistry IDs or retain Sessions. Low MaxQueryNodes/MaxParameterBytes/MaxPreparedPlanBytes remain enforced for logical shape and each changing value; no warm-hit capacity bypass. |
| Fresh schema and side-effect timing | Provider preparation tests keep Parse+Describe+Sync without Execute at open, fresh external-DDL description rather than cached-plan 0A000, and first Parse SQLSTATE. Add warm Find followed by external DDL to prove shape mismatch/provider priority still precedes mapping and no SQL replay. |
| Transaction and lifecycle | Keep Session/compound gate, failed-transaction rejection, total deadline, immutable Source identity, accepted-stop cancellation priority, cursor ready/take/close fencing and rich-error cleanup. No inline callback publication experiment is implied. |

The normal physical statement still belongs to one connection and one execution.
Neither a source logical-shape cache nor a generated template authorizes sharing
PGresult/RowDescription or sqlite3_stmt across executions. Existing prepared
snapshot/dispose tests (`Query.Fluent/Program.cs:192–297`), native bounded shape
cache tests and cursor lifetime tests are reusable; the identity/eviction/DDL
cases above specifically address the automatic Find cache.

For a later isolated A/B, use the same new matched business SQL and full DTO,
separate cold miss from repeated values/hits, and record full query CPU/B/GC and
exact SQL/FFI counts. The target removes identifiable repeated construction;
the amount of saved CPU/allocation remains unmeasured until that run.
