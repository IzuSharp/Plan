# ORM-RELATIONAL: Implement fixed CTE, set, subquery and window semantics

Status: `planned_candidate`; product implementation remains unauthorized.

Use the immutable Design commit in `../implementation-graph.json`, contracts v0.2.0,
and `docs/korda-orm/implementation-spec.md`. The packet fixes implementation work;
contradictions return to the contract owner before changing an interface or policy.

## Inputs, dependencies and ownership

Start after Foundation. Acceptance requires actual Query and Expressions.
Own `src/Orm/Language/Relational/` and `tests/Orm/Relational/`; use ORM-C01/C02/C03/C06.
Read implementation-spec and the pinned jOOQ symbols at
`3c58109e7ab69772de75e640852935ee7e284177` listed below.

| File | Source basis and fixed output |
| --- | --- |
| `Cte.cs`, `Sql.Relational.cs` | `CommonTableExpressionImpl`, `DerivedColumnListImpl`, `WithImpl`: named/recursive definition and reference nodes |
| `SetOperations.cs` | `SelectQueryImpl` set operation tree and nested parentheses |
| `Subqueries.cs` | `ScalarSubquery`, `Exists`, `DerivedTable`, `Lateral`: scope-aware references |
| `Windows.cs`, `WindowFrames.cs` | `WindowSpecificationImpl`, `WindowDefinitionImpl`, `AbstractWindowFunction` |
| `RelationalValidator.cs` | Degree/types, recursive visibility, frames and operation-context rules |

## Fixed APIs

Create CTE definitions with `Sql.Cte(name, query)` and references with `cte.As(alias)`.
Recursive definitions use `Sql.RecursiveCte(name, columnDescriptors, build)` where
build receives the typed reference and returns the anchor.UnionAll(recursiveTerm)
query. The reference may be used only inside that build scope and subsequent
queries that explicitly include the resulting CTE. A normal CTE cannot self-reference.

`query.With(cte)` appends a definition; duplicate names fail. Union/UnionAll/Intersect/
IntersectAll/Except/ExceptAll use the Query<T> extension signatures and retain explicit tree grouping.
Subqueries use `Sql.Exists(query)`, `Sql.Scalar(query)` for degree1, and
`query.AsTable(alias)` with typed projection-column handles, never DTO reflection.

Window construction is `Sql.Window().PartitionBy(fields).OrderBy(sortFields)` then
`RowsBetween(start,end)`, `RangeBetween(start,end)` or `GroupsBetween(start,end)`.
An explicit `Exclude(WindowExclusion)` adds its frame exclusion. Bounds are named values
UnboundedPreceding, Preceding(nonnegative), CurrentRow, Following(nonnegative),
UnboundedFollowing. `function.Over(window)` associates it without mutating the
function or named window definition. Named windows are scoped per query.

### Exact handle signatures

Contracts owns Cte (abstract), Cte<T>, CteReference<T>, DerivedTable<T>, WindowSpec,
NamedWindow and WindowBound data. CteReference<T>/DerivedTable<T> derive TableLike;
Column<U>(string alias,SqlType<U> type) returns Field<U> after exact shape lookup.
No CLR member reflection is involved. Language supplies the following methods:

```csharp
// Sql partial facade
public static Cte<T> Cte<T>(string name, Query<T> query);
public static Cte<T> RecursiveCte<T>(string name, ResultShape columns,
    Func<CteReference<T>, Query<T>> build);
public static Condition Exists<T>(Query<T> query);
public static Field<T?> Scalar<T>(Query<T> query) where T : struct;
public static Field<T?> Scalar<T>(Query<T?> query) where T : struct;
public static Field<T?> ScalarReference<T>(Query<T> query) where T : class;
public static WindowSpec Window();
public static Field<long> RowNumber();
public static Field<long> Rank();
public static Field<long> DenseRank();
// RelationalOperations
public static Query<T> With<T>(this Query<T> query, params Cte[] definitions);
public static CteReference<T> As<T>(this Cte<T> cte, string alias);
public static Cte<T> Materialize<T>(this Cte<T> cte, CteMaterialization materialization);
public static DerivedTable<T> AsTable<T>(this Query<T> query, string alias);
public static WindowSpec PartitionBy(this WindowSpec window, params IField[] fields);
public static WindowSpec OrderBy(this WindowSpec window, params SortField[] fields);
public static WindowSpec RowsBetween(this WindowSpec window, WindowBound start, WindowBound end);
public static WindowSpec RangeBetween(this WindowSpec window, WindowBound start, WindowBound end);
public static WindowSpec GroupsBetween(this WindowSpec window, WindowBound start, WindowBound end);
public static WindowSpec Exclude(this WindowSpec window, WindowExclusion exclusion);
public static NamedWindow As(this WindowSpec window, string name);
public static Query<T> Window<T>(this Query<T> query, NamedWindow window);
public static Field<T> Over<T>(this Field<T> function, WindowSpec window);
public static Field<T> Over<T>(this Field<T> function, NamedWindow window);
```

WindowBound exposes static UnboundedPreceding/CurrentRow/UnboundedFollowing and
Preceding(long)/Following(long) factories; offsets are nonnegative. PartitionBy and
OrderBy replace their clauses. RecursiveCte invokes build once with a reserved
reference, freezes its query and verifies the supplied ResultShape exactly; it
never retains the callback. The constructor requires an explicit UNION ALL anchor
and recursive branch, with the self-reference prohibited in the anchor. Scalar
value/reference overload names differ because C# cannot overload only by struct
versus class constraints. Before constructing a scalar, require exactly one Scalar logical member whose
SQL/CLR carrier matches T (or T? for the nullable overload). Sql.Select(Field<T>)
returns Query<T>. A one-column DTO/Row carrier is not automatically its field type:
reject it with KORM-QUERY-002, without reflected member inference.
The scalar result has SQL Nullable regardless of whether
the source projection itself is NonNull; callers cannot retrieve an empty scalar
as a nonnullable value type accidentally.

### Closed policies and complete relational payloads

Foundation declares these enums/records in Contracts; Language's relational files
implement their factories/validation. Each public handle has an internal immutable
payload constructor and Captured sidecar, like Field/Query. Cte<T> stores its
CteDefinitionNode and Projection<T>; CteReference<T>/DerivedTable<T> store their
relation node and projection descriptor. CteId is a process-local monotonic identity,
allocated exactly as RelationId, and is normalized for a structural fingerprint.

```csharp
public readonly record struct CteId(long Value);
public enum CteMaterialization { Default, Materialized, NotMaterialized }
public enum WindowFrameUnit { Rows, Range, Groups }
public enum WindowBoundKind {
    UnboundedPreceding, Preceding, CurrentRow, Following, UnboundedFollowing
}
public enum WindowExclusion { NoOthers, CurrentRow, Group, Ties }
public sealed class WindowBound {
    public WindowBoundKind Kind { get; }
    public long Offset { get; }
    internal WindowBound(WindowBoundKind kind, long offset);
    public static WindowBound UnboundedPreceding { get; }
    public static WindowBound CurrentRow { get; }
    public static WindowBound UnboundedFollowing { get; }
    public static WindowBound Preceding(long offset);
    public static WindowBound Following(long offset);
}

internal sealed record CteDefinitionNode(CteId Id, string Name,
    ResultShape Columns, SqlNode Body, bool Recursive,
    CteMaterialization Materialization) : SqlNode(NodeKind.CteDefinition);
internal sealed record CteReferenceNode(CteId Cte, RelationId Relation,
    string Alias) : SqlNode(NodeKind.CteReference);
internal sealed record DerivedTableNode(QueryNode Query, RelationId Relation,
    string Alias) : SqlNode(NodeKind.DerivedTable);
internal sealed record WindowFrameNode(WindowFrameUnit Unit, WindowBound Start,
    WindowBound End, WindowExclusion? Exclusion);
internal sealed record WindowNode(ImmutableArray<SqlNode> Partition,
    ImmutableArray<SortNode> Order, WindowFrameNode? Frame)
    : SqlNode(NodeKind.Window);
internal sealed record NamedWindowNode(string Name, WindowNode Definition)
    : SqlNode(NodeKind.NamedWindow);
internal sealed record OverNode(SqlNode Function, WindowNode? InlineWindow,
    string? WindowName, SqlTypeDescriptor ResultType, string? ConversionId)
    : SqlNode(NodeKind.Over);
internal sealed record ExistsNode(QueryNode Query) : SqlNode(NodeKind.Exists);
internal sealed record ScalarSubqueryNode(QueryNode Query,
    SqlTypeDescriptor ResultType, string? ConversionId)
    : SqlNode(NodeKind.ScalarSubquery);
```

This CteDefinitionNode.Body replaces the compact earlier query-only field so that
the explicitly typed PostgreSQL DML-CTE surface in ORM-DML can reuse the same node.
Body is exactly QueryNode or a DmlNode with ReturningProjectionNode; no raw SQL or
delegate is retained. Normal Cte/RecursiveCte starts with Materialization.Default.
Materialize returns a new definition snapshot with the same CteId and changed
policy. Including two definitions with the same ID/name, even different snapshots,
fails KORM-SCOPE-002. A reference resolves the definition actually included in its
WITH scope. For a mutation body, nondefault materialization and recursive mode
are excluded from this baseline with KORM-DIALECT-001.

WindowSpec stores WindowNode. NamedWindow stores its name and immutable definition;
Over(named) stores only the scoped name in OverNode and merges the definition's
captures. Query.Window appends that exact definition; it never installs a global
name. OverNode has exactly one of InlineWindow/WindowName, retains the function's
result type/conversion ID, and never loses an aggregate result conversion. Using
an unregistered same-scope window name fails KORM-SCOPE-001. A repeated name fails
KORM-SCOPE-002. Named-window inheritance has no public entry in this version.

PartitionBy/OrderBy/frame builders replace their respective clause. A frame
builder resets any previous exclusion to null; Exclude requires an existing frame
and replaces only its exclusion. Null Exclusion emits no text; explicit NoOthers
emits `EXCLUDE NO OTHERS` and participates in capability checks/fingerprinting.
Frame offsets are nonnegative Int64 structural literals, not captured parameters.
The three non-offset bounds require Offset=0. Compare conceptual positions
`-infinity`, `-offset`, `0`, `offset`, `+infinity` without integer negation overflow;
start must not be after end. UnboundedFollowing as start and UnboundedPreceding as
end are invalid. Zero Preceding/Following compares at CurrentRow but keeps its
explicit spelling in the node. GROUPS requires nonempty ORDER BY. RANGE with an
offset requires exactly one numeric order key; temporal/interval RANGE offsets
have no implicit conversion in this initial long-offset surface.

RowNumber/Rank/DenseRank are WindowOnly functions and must have Over. They accept
partition/order but no explicit frame in this baseline: a frame would be ignored
by some servers, so diagnose KORM-QUERY-004 instead of suggesting it changes rank.
The registered COUNT/SUM/MIN/MAX/AVG aggregate functions may use Over with the
validated frame. Aggregate/window nesting follows the shared expression-context
validator; arbitrary scalar functions do not become window functions through Over.

| Capability | PostgreSQL | SQLite | MySQL 8.4 | MariaDB 11.8 |
| --- | --- | --- | --- | --- |
| Cte.Materialize(Materialized/NotMaterialized), SELECT body | Native keyword after AS | Native keyword after AS | KORM-DIALECT-001 | KORM-DIALECT-001 |
| GroupsBetween and all four explicit EXCLUDE values | Native | Native | KORM-DIALECT-001 | KORM-DIALECT-001 |
| IntersectAll / ExceptAll | Native | KORM-DIALECT-001 | Native | Native |
| Qualify | KORM-DIALECT-001 | KORM-DIALECT-001 | KORM-DIALECT-001 | KORM-DIALECT-001 |

Materialization is an explicit supported planner directive, not a guarantee that
a server executes one chosen physical plan. Every rejected capability is checked
before SQL/template publication. No marker is erased because it happens to resemble
a default. The lock surface and per-profile spellings are fixed in ORM-QUERY.

## Ordered implementation

1. CTE construction allocates stable CteId and typed ordered columns before building
   a recursive term. Scope validation allows the reserved self-reference only in
   that declared recursive term; validate anchor and recursive degrees/types.
2. Emit each CTE definition once in the query's declared order. A cycle involving
   two ordinary CTEs is invalid. Forward references are rejected in this baseline;
   do not silently reorder a graph with volatile or recursive meaning.
3. Keep set operations as a binary tree. Validate same degree and component type
   compatibility. Preserve `A UNION (B EXCEPT C)` versus `(A UNION B) EXCEPT C`.
   The root ORDER/LIMIT applies to the combined result; child ORDER/LIMIT requires
   a parenthesized child form supported by the profile.
4. Scalar subqueries require exactly one output field; their value type is nullable
   for an empty result. For PG/MySQL/Maria, more than one actual row remains a server cardinality
   error. SQLite instead takes the first row natively, so admit only a proved
   at-most-one source: explicit LimitLiteral(0/1) (ordinary parameterized Limit gives no proof), aggregate without GROUP BY, SELECT without
   FROM, or complete unique-key equality proof. Otherwise KORM-DIALECT-006 before
   rendering. Never add LIMIT1 or promise a SQLite error it does not produce. EXISTS returns a nonnull SQL condition.
5. Derived-table fields retain the derived RelationId and projection aliases.
   Lateral capture sees only preceding FROM bindings. Correlated scalar/EXISTS
   capture uses the parent lexical scope, not matching alias strings globally.
6. Validate window function context and frame ordering. Negative offsets, start
   after end, invalid unbounded positions and incompatible RANGE offset/order types
   are KORM-QUERY-004. RANGE with an offset requires one compatible ORDER expression.
7. Reuse named window definitions without retaining render-state counters. A window
   in WHERE or an aggregate nested in an illegal window context fails pure validation.
8. QUALIFY is represented explicitly and lowered only by a verified dialect rule.
   Do not copy unavailable commercial jOOQ transformation stubs; unsupported
   combinations fail rather than adding a guessed derived-table rewrite.
9. Return complete nodes to Rendering. Native/unsupported materialization and lock
   behavior is the dialect's explicit decision, never a dropped clause.

## Exact cases

| ID | Input | Expected |
| --- | --- | --- |
| REL-01 | 10 UNION (20 EXCEPT 30) | Result set 10/20; child grouping preserved |
| REL-02 | UNION degree/type mismatch | KORM-QUERY-002 |
| REL-03 | Recursive Int64 numbers anchor1L + recursive n.Add(1L) while n<3L | 1/2/3; anchor/term types match |
| REL-04 | Ordinary CTE self-reference or forward reference | KORM-SCOPE-001 |
| REL-05 | Scalar subquery degree2 | Pure validation failure |
| REL-06 | Scalar subquery no rows / >1 row | NULL / preserved PG-MySQL-Maria error; unproved SQLite multirow source rejected before render |
| REL-07 | Derived nonlateral sibling capture | Rejected; explicit legal lateral variant accepted by its profile |
| REL-08 | ROW_NUMBER order by id, partition department | Exact numbering from canonical fixture, independent of outer sort |
| REL-09 | ROWS preceding1 to current | Correct two-row rolling frame |
| REL-10 | RANGE offset with two ORDER columns or negative offset | KORM-QUERY-004 |
| REL-11 | Named window shadow/duplicate | Same-scope duplicate fails |
| REL-12 | Unsupported QUALIFY/materialization request | Capability error, no silent omission |
| REL-13 | Sql.Cte("x", Sql.Select(Sql.Literal(1, SqlTypes.Int32).As("Value1"))).Materialize(CteMaterialization.Materialized), then With(x) | PG/SQLite `WITH "x" ("Value1") AS MATERIALIZED (SELECT 1 AS "Value1") ...`; MySQL/Maria KORM-DIALECT-001 |
| REL-14 | Values (k,v)=(1,10),(1,20),(2,30); SUM(v) over order k GROUPS current/current EXCLUDE TIES | PG/SQLite values 10,20,30; ties excluded except the current row; native SUM conversion retained |
| REL-15 | Same input, GROUPS current/current EXCLUDE GROUP | NULL for all three rows; empty-frame aggregate semantics retained |
| REL-16 | GROUPS without order, Exclude before frame, Rank with explicit frame | KORM-QUERY-004 |
| REL-17 | A=[1,1,2], B=[1,2,2] | INTERSECT ALL bag [1,2]; EXCEPT ALL bag [1]; SQLite rejects both before emission |
| REL-18 | Rank/DenseRank over k for k=[1,1,2] | Rank [1,1,3], DenseRank [1,1,2]; outer order supplied explicitly |

## Validation, integration and stop

`python3 tests/Orm/Relational/verify.py` runs native node/scope/frame cases and
negative compiler cases. ORM-ORACLE owns shared expected SQL semantics; Integration
runs the recursive/set/window rows on each advertised profile. Register
`orm-relational` and its Query/Expressions/Contracts/Types dependencies. No database
service is required for the pure node checks. Stop at this module's gate; optional
Parser, nested materialization, provider execution and final integration remain
separate owners.
