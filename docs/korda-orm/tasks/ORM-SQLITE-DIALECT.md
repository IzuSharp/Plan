# ORM-SQLITE-DIALECT — SQLite SQL profile

Status: `planned_candidate`; product implementation is **not authorized**.

## Objective and dependencies

Implement the driver-free SQLite profile for runtime engines at least 3.45 and
less than 4.0. Follow Design `implementation-spec.md`, `contracts.md` and
`dialects-and-generation.md` at the batch's immutable Design revision. Consume
ORM-C01, ORM-C02, ORM-C03 and ORM-C06. Start: `ORM-FOUNDATION`; acceptance:
`ORM-RENDER`, `ORM-ADVANCED-TYPES` and `ORM-NESTED`. SQLite is mandatory in the final matrix and independently selectable.
Foundation owns project/root registration; the driver owns library distribution,
connections and actual-engine capability discovery.

## Shared rendering interface

Implement the Contracts-owned internal IDialectRules. Lower(SqlNode,SqlProfile)
returns a checked immutable tree. Write(SqlNode,ISqlWriter,int parentPrecedence)
handles the profile-specific node or calls writer.VisitCore for the common writer;
VisitCore must not dispatch back to this same dialect handler for that node.
ISqlWriter exposes Profile, Write, Visit, VisitCore, Quote and NextParameter. Its
state belongs to Rendering's private per-operation RenderContext. Profile.Create
sets Contracts.SqlProfile's internal Rules property to this profile's static,
stateless IDialectRules instance; its family must match. Rendering calls that
explicit instance and does not reference dialect assemblies, use a global registry,
load rules through reflection or rely on module initialization. A publicly built
metadata-only profile without Rules is usable for declared SQL but Fluent Render
fails KORM-DIALECT-001 and points to the appropriate Profile.Create factory.

This dialect references Contracts, Types, Language, AdvancedTypes and the pure Nested module,
**not Rendering**. Rules.Lower first calls NestedLowering(root,profile), then this
dialect's own lowering. Nested references Contracts/Types/Language/AdvancedTypes
and no Rendering or Execution assembly. Profile fingerprint/equality uses only
serialized content plus the fixed ruleVersion, never the Rules object identity.
Freezing a template copies its profile without Rules, so reusable templates retain
metadata rather than executable rule instances. No mutable global writer state.
All LIMIT/OFFSET public inputs are Int32 in 0..Int32.MaxValue; emitted parameters
retain that declared type. Larger pagination requires a separately added API.
RETURNING uses Contracts.ReturningProjectionNode(target,items). After writing the
keyword, Visit that node; the core writer enters/exits the operation-local returning
scope with try/finally, rather than exposing raw scope mutation to this module.

## Source map and exact file ownership

Use jOOQ 3.21.10 commit `3c58109e7ab69772de75e640852935ee7e284177`, public
`jOOQ/src/main/java/org/jooq/impl/` sources. Adapt the following semantic branches
with retained attribution; do not copy unrelated Java execution infrastructure.

| Source | Local responsibility |
| --- | --- |
| `SelectQueryImpl.unionParenthesis`, `derivedTableRequired` | Derived SELECT wrapping when SQLite cannot parenthesize a compound operand directly |
| `InsertQueryImpl.accept1`, `acceptInsertSelect` | Native ON CONFLICT and the SELECT/ON grammar ambiguity |
| `AbstractDMLQuery.nativeSupportReturning`, `toSQLReturning` | Native projection with SQLite-specific context limitations |
| `CommonTableExpressionImpl.accept` | Explicit MATERIALIZED / NOT MATERIALIZED spelling |
| `JSONArray.accept`, `JSONArrayAgg.accept0` | JSON constructor and ordered JSON aggregation; retain JSON subtype through deliberate `json(...)` re-tagging |
| `DefaultBinding` SQLite branches | Preserve declared intent despite dynamic storage classes; actual conversions belong to codecs |

Own `src/Orm/Dialects/Sqlite/` and `tests/Orm/Dialects/Sqlite/`. Required files:
`Profile.cs` (`SqliteProfile.Create`), `CapabilityTable.cs` (`Resolve`),
`Lowering.cs` (`SqliteLowering.Lower`, `WrapSetOperand`, `ValidateReturning`,
`ValidateConflict`), `TypeNames.cs` (`WriteType`), `SqliteWriter.cs`
(`WriteSelect`, `WriteSet`, `WriteDml`, `WriteSort`, `WriteCte`) and
`SqliteLiteralWriter.cs` (`Write`). Tests are `ProfileTests`, `SetOperandTests`,
`ConflictTests`, `ReturningTests`, `JsonSubtypeTests`, `ParameterLayoutTests` and
`UnsupportedTests`; source fixtures use `sqlite-<case>.json` names.

## Profile and capability table

`SqliteProfile.Create` sets family Sqlite, named placeholders, version interval
[3.45,4.0), `max_parameters=32766`, `json=required`, `returning=required`, and
`double_quoted_string_literals=disallowed`. A driver may supply a smaller observed
parameter limit; use the smaller limit in the immutable session profile. A larger
compiled limit is not used automatically. The driver's engine/build verification
is separate from rendering and records sqlite_version, source ID and relevant
compile options. Extension functions must be explicitly registered; SQL text
never probes or loads extensions.

| Family | Fixed support |
| --- | --- |
| Joins | INNER/LEFT/RIGHT/FULL/CROSS native; RIGHT/FULL require the stated >=3.45 profile; LATERAL is rejected |
| Set operations | UNION, UNION ALL, INTERSECT DISTINCT, EXCEPT DISTINCT; INTERSECT ALL and EXCEPT ALL rejected |
| CTEs | SELECT CTEs, recursive SELECT CTEs, explicit MATERIALIZED/NOT MATERIALIZED; DML statement as CTE body rejected |
| Windows | ROWS/RANGE/GROUPS and EXCLUDE for the registered window functions; unsupported function/frame combinations diagnosed |
| Comparison/sort | `IS [NOT] DISTINCT FROM`, native `NULLS FIRST/LAST`, ordinary SQL three-valued comparisons |
| DML | Single target INSERT/UPDATE/DELETE and native RETURNING, explicit ON CONFLICT; no DELETE USING or multi-target writes |
| Locking/other | FOR UPDATE/SHARE, QUALIFY, DISTINCT ON, MERGE and unsupported optimizer hints rejected |

Materialization keywords are honored as supported syntax, not guaranteed physical
planner behavior. Full joins are native; no UNION emulation is necessary. SQLite
NUMERIC affinity is not treated as a lossless decimal storage guarantee.

## Exact emitter and lowerings

Use the shared validation -> checked lowering -> second validation -> atomic
render pipeline. A failed lowering yields no reusable template. Quote each name
segment with `"` and double embedded quotes. After common Ordinal validation, recheck relation/output aliases with
SQLite's ASCII-insensitive identifier comparison; u/U and Id/id collide even when
quoted. Non-ASCII code points are not folded by this SQLite rule. Fail
KORM-SCOPE-002 before emission. String literals use doubled single
quotes; reject embedded U+0000 in an explicit SQL literal. Bound strings retain
embedded NUL through the driver; the literal restriction does not change binding.
Booleans in literal expression positions are `1` and `0` with Boolean descriptor.
Binary literals are uppercase `X'hex'`. No culture-dependent number formatting.

All final occurrences call `NextParameter` and emit `@p0`, `@p1`, ...; occurrence
names are `p0`, `p1`, ... without `@`. Repeated logical slots receive separate
physical parameters. A zero-length expanded IN becomes FALSE and consumes zero
parameters; typed NULL list elements retain UNKNOWN semantics. Count after all
lowering duplication against the profile limit. Pagination is LIMIT then OFFSET;
offset-only emits `LIMIT -1 OFFSET @pN` with the `-1` as a fixed grammar literal,
not an application value. Negative user pagination remains invalid.

### Closed type spelling and exact-decimal boundary

Native casts spell Int16/Int32/Int64/Boolean as INTEGER, Float32/Float64 as REAL,
Text as TEXT and Binary as BLOB. UUID/date/local-time/instant text transport keeps
its explicit advanced identity and canonical encoding; a storage-class name alone
does not validate those values. Decimal's supported SQLite representation is
validated canonical TEXT for parameter/result transport. Reject Decimal-typed
numeric comparison (including equality), numeric ORDER BY/arithmetic, exact SUM/
AVG and cast-to-SQL-numeric with KORM-TYPE-004. TEXT lexicographic comparison and
SQLite NUMERIC conversion are not an exact decimal implementation. An application
may explicitly choose Text operations or approximate Double semantics instead.
Integer SUM is the separately named `aggregate.int-sum.decimal` result conversion
from native Int64, not proof that SQLite decimal TEXT aggregates are supported.

### Compound operand wrapper — copy this algorithm

SQLite groups a compound SELECT left-to-right and does not accept every parenthesized
operand that PostgreSQL accepts. `WrapSetOperand(child)` is required when the AST's
right subtree is compound, when a child has local ORDER/LIMIT/OFFSET, or when its
explicit grouping otherwise changes association. Do not flatten or reorder sets.

1. Validate child degree/types first. Allocate relation alias `__korda_set_N` in
   depth-first order, skipping every already-declared relation alias.
2. Give the child's output fields unique internal aliases `__korda_c0`,
   `__korda_c1`, ... through an alias override, without changing their expressions.
   Transfer references to local projection aliases/ordinals to the corresponding
   overridden expression identities. Preserve child ORDER/LIMIT inside the child.
3. Build a derived table containing that child. Build an outer SELECT with one
   explicitly qualified field per ordinal and the parent-required result aliases.
   This wrapper has no extra DISTINCT, WHERE, LIMIT or ordering.
4. Use the outer SELECT as the operand. It preserves the child's bag/multiplicity
   and scope; no SELECT * or new request parameters are introduced by the wrapper.
5. Validate the resulting graph and use the ordinary renderer. The first-use
   parameter order is the emitted order of the rewritten tree.

For A={1,2,3}, B={2,3}, C={3}, `A EXCEPT (B EXCEPT C)` must render structurally as
`SELECT ... FROM A EXCEPT SELECT ... FROM (SELECT ... FROM B EXCEPT SELECT ...
FROM C) AS "__korda_set_0"` and produce {1,3}. This is a semantic assertion, not a
license to emit the abbreviated ellipses.

### INSERT SELECT, conflict and RETURNING

For an INSERT whose source is SELECT and has ON CONFLICT, ensure the source SELECT
has a WHERE clause to remove SQLite's ON/join parsing ambiguity. If its WHERE is
absent, add the pure TRUE predicate; if present, keep it unchanged. Do not attach
this predicate to HAVING or the conflict update. Source UNION/ORDER/LIMIT remains
inside its correct source query.

Support a nonempty explicit column target with optional index predicate, plus a
single final targetless DO NOTHING or DO UPDATE only when the application requested
AnyUniqueKey. Do not translate a named PostgreSQL constraint into a guessed SQLite
column list. Excluded references emit `"excluded"."column"`; conflict-update
predicates stay after SET. Validate target/assignment ownership and duplicates.

RETURNING is top-level DML only and references target columns/accepted scalar
expressions. The ReturningProjectionNode core scope renders target column references
without a table/alias qualifier. A reference to any other relation in that scope
fails KORM-DIALECT-005 with form 'NonTargetRelation'. This is required: SQLite 3.53.4 actually rejected
`UPDATE u AS x ... RETURNING x.id` while unqualified `RETURNING id` succeeded. Reject DML CTE bodies, aggregate/window RETURNING expressions and
UPDATE-FROM RETURNING references to auxiliary tables. The result projection keeps
exact ordinal/alias/type metadata. Do not promise trigger-after values, row order,
composability as a subquery, or bounded SQLite engine buffering. Client streaming
only changes consumption of the result that the engine already produces.

### Scalar subquery cardinality proof

The common Scalar contract is zero rows -> NULL, one row -> its value, and more
than one row -> a cardinality error. SQLite itself takes the first row, so arbitrary
Scalar nodes cannot be emitted as though they honored that contract. Admit only:
(a) a SELECT with no FROM/joins and only scalar expressions; (b) an aggregate query
with no GROUP BY; (c) an explicit **literal** LIMIT 0 or 1 produced by LimitLiteral(count) or parsed literal LIMIT; or (d) a single base
table with every column of one schema-generated declared non-null unique key equated in a top-level
AND to scalar literal/parameter expressions, with no joins/sets/disjunction over
the key proof. A hand-defined Table without key metadata cannot invent that proof.
Additional AND filters can only reduce cardinality.

LimitLiteral is the explicit QueryOperations extension specified in ORM-QUERY;
it stores a validated Int32 LiteralNode and includes the value in the template hash.
Ordinary runtime LIMIT parameters do not prove an upper bound, even when the
current bound value happens to be 1. No extra query, LIMIT, or post-result guess is
inserted to conceal multiple rows. Without one of these static proofs fail
KORM-DIALECT-006 with rule `ScalarCardinality`. The actual research SQLite 3.53.4
query over two rows returned the first ordered row; this is a verified semantic
difference, not an environment failure.

## Fixed fixtures and diagnostics

Reuse the three users from ORM-POSTGRES-DIALECT with `INTEGER`/`TEXT` storage.
Each fixture records SQL, final parameter `(SlotId, ElementIndex, Ordinal, Name,
SqlTypeId)` sequence, result descriptor, expected rows or exact diagnostic.

| ID | Required expectation |
| --- | --- |
| `sqlite-repeat` | `SELECT "u"."id" AS "Id" FROM "users" AS "u" WHERE ("u"."score" >= @p0 OR "u"."id" = @p1) ORDER BY "u"."id" ASC`; both slots reference the same Int64 value 2; IDs 1,2,3 |
| `sqlite-offset` | Offset 1 without limit ends `LIMIT -1 OFFSET @p0`; value 1 appears once in layout |
| `sqlite-set-right` | Right-nested EXCEPT uses the wrapper above and returns {1,3}; a negative snapshot forbids naked `EXCEPT (` |
| `sqlite-local-limit` | Child UNION operand ordered descending with LIMIT 1 retains the local limit, not an outer limit |
| `sqlite-insert-select` | Source without predicate becomes `... SELECT ... FROM ... WHERE 1 ON CONFLICT ...`; the TRUE is structural and not a new slot |
| `sqlite-returning` | Update ID1 name and `RETURNING "id" AS "Id", "name" AS "Name"` returns `(1,newName)`; no auxiliary SELECT |
| `sqlite-json-order` | `json_group_array(json_array(id,name) ORDER BY id,seq)` preserves ordered nested arrays, duplicate rows and JSON subtype on the actual accepted engine |
| `sqlite-scalar` | Unproven two-row scalar fails ScalarCardinality before emission; literal LIMIT1 and a no-GROUP aggregate are admitted; runtime LIMIT @p0 alone is not proof |
| `sqlite-budget` | At 32,766 occurrences succeeds; at 32,767 fails (or the smaller explicitly configured boundary) |
| `sqlite-null` | SQL NULL, JSON text `null`, JSON string `"null"`, absent outer row and empty multiset are distinct fixtures |

Use the common dialect messages defined in ORM-POSTGRES-DIALECT:
`KORM-DIALECT-001` unsupported syntax/feature; `-002` final parameter overflow;
`-003` profile setting mismatch; `-004` unpreservable conflict target; `-005`
unsupported RETURNING context; `-006` an unavailable semantics-preserving rewrite.
Node paths identify the failing compound operand or returning expression.

## Acceptance and handoff

Run exact pure fixtures, eligible pinned jOOQ cases and a driver-free Native AOT
renderer consumer. Test the wrapper with duplicate rows, equal projection names,
parameter occurrences inside both children, local ordering and nested correlations.
Native AOT proves the pure writer can be published; it does not prove SQLite SQL
acceptance. Real engine tests run in the independent SQLITE-DRIVER/integration
lane and record exact version/source/compile options. Never mark a future product
handler accepted because the separate JDBC/.NET research probe passed.

Hand off capability entries and deterministic fixtures to RENDER, RELATIONAL, DML,
NESTED, ADVANCED-TYPES and SQLITE-DRIVER. Pure checks select no native SQLite library
or other database. Stop at the reviewed task PR; no production implementation is
authorized by this plan, and no merge/publication/legacy change is included.

Primary references: [SELECT](https://www.sqlite.org/lang_select.html),
[UPSERT ambiguity](https://www.sqlite.org/lang_upsert.html),
[RETURNING limitations](https://www.sqlite.org/lang_returning.html),
[WITH materialization](https://www.sqlite.org/lang_with.html),
[limits](https://www.sqlite.org/limits.html),
[JSON](https://www.sqlite.org/json1.html),
[3.44 aggregate ordering](https://www.sqlite.org/releaselog/3_44_0.html).

## Exact local runner contract

This task owns `tests/Orm/Dialects/Sqlite/verify.py`,
`tests/Orm/Dialects/Sqlite/Korda.Orm.Dialects.Sqlite.Tests.csproj` and its Program/fixture files.
The CI command, from repository root with no additional flags, is:

```sh
python3 tests/Orm/Dialects/Sqlite/verify.py
```

The runner compiles the packet's positive/negative declaration cases, publishes
its actual consumer with `dotnet publish tests/Orm/Dialects/Sqlite/Korda.Orm.Dialects.Sqlite.Tests.csproj -c Release -r linux-x64 -p:PublishAot=true`,
then executes that native consumer and asserts RuntimeFeature.IsDynamicCodeSupported
is false. Use the repository's pinned SDK/restore settings; place outputs under
artifacts, never beside source. Run this packet's enumerated pure fixtures and
report individual case failures with nonzero exit. The runner does not start a
database, accept an absent peer as a passing stub, or claim live SQL correctness.
Real four-server rows, faults and SQL execution remain ORM-INTEGRATION's gate.
