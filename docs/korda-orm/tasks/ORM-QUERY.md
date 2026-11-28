# ORM-QUERY: Implement immutable queries, aliases and typed projection assembly

Status: `planned_candidate`; product implementation remains unauthorized.

Use the immutable Design commit in `../implementation-graph.json`, contracts v0.2.0,
and `docs/korda-orm/implementation-spec.md`. The packet fixes implementation work;
contradictions return to the contract owner before changing an interface or policy.

## Gate and scope

Start after Foundation; acceptance requires Types. Own
`src/Orm/Language/Query/` and `tests/Orm/Query/`. The project file is Foundation/CI
owned. Core Field/Condition/Query/Projection handles and node data contracts are
shared; implement their Language extension/factory bodies here without redefining
public types. Use ORM-C01/C02/C03/C06 and implementation-spec §§3–6.

## Source-to-file mapping

| C# file | Pinned jOOQ source and inherited behavior |
| --- | --- |
| `QueryOperations.cs`, `Sql.Query.cs` | `SelectQueryImpl`, `SelectImpl`: clause collections and composition; C# returns new snapshots instead of mutating one builder |
| `ProjectionBuilder.cs` | `SelectFieldList`, `FieldAlias`, `AbstractField`: ordered typed columns and explicit aliases |
| `RelationBindings.cs` | `TableImpl`, `TableAlias`, `TableFieldImpl`, `DerivedTable`: relation identity versus emitted name |
| `QueryValidator.cs`, `ScopeValidator.cs` | `AbstractContext`, `ScopeStack`, `SelectQueryImpl`: lexical scope, correlation and clause visibility |
| `QuerySnapshotTests.cs` | C# immutable adaptation cases plus source-linked alias/scope cases |

Source pin: jOOQ `3c58109e7ab69772de75e640852935ee7e284177`.

## Fixed API behavior

`Sql.Select(Projection<T>)` creates Query<T>; `Sql.Select(Field<T>)` creates Query<T>;
Select arities2–8 create the corresponding Row<T...> projection. Explicit Row<T>
remains available through a declared Projection<Row<T>>. Generated `<DtoName>Projection.Create` is the
compile-time checked DTO entry; `Sql.Project<T>(IField[])` is the explicit runtime
projection-validation entry. Both preserve the typed descriptors. There is no
SELECT * for a typed result.

`From`, `Where`, `GroupBy`, `Having`, `OrderBy`, `Limit`, `Offset`, `Distinct` and
`Join` are the extension signatures in Design. From/Where/Having/GroupBy/OrderBy
replace that clause in the returned query; Join appends one join; Distinct sets a
distinct specification; Limit/Offset replace their captured Int32 parameter. Repeated Where calls do
not secretly AND; callers use Condition.And. Limit/Offset reject negative counts.
All input arrays/collections are frozen at the call boundary.

## Ordered implementation

1. Create a SelectNode with nonempty projection and empty optional clauses. Preserve
   every projected Field node and its captures; ResultShape aliases are deterministic.
   A generated DTO helper assigns the exact member alias. Row<T...> assigns Value1..
   ValueN. Explicit field aliases override automatic physical-column labels.
2. Implement each operation as one new immutable node/wrapper sharing unchanged
   children. Copy a caller collection before storing it. Never attach a session,
   mapping factory, command or mutable render context to a query.
3. Merge captured values by slot identity; keep only final-layout slots when binding.
   Distinct slots with equal label/value remain distinct. An unused argument superset
   is allowed and never becomes a database parameter.
4. Table aliases allocate a distinct RelationId and rebind that table's fields.
   Generated table aliases expose correspondingly rebound typed properties. A self
   join uses two such relations; referencing the original relation inside an aliased
   FROM fails KORM-SCOPE-001.
5. Traverse lexical ScopeFrame data from Design. FROM relations become available in
   order. Nonlateral derived tables cannot capture siblings. Lateral joins may
   capture preceding relations only. Correlated scalar/EXISTS subqueries may use
   declared enclosing scopes. Unknown relations/CTEs fail with expression path.
6. Validate aliases in each emitted scope with Ordinal comparison. Empty alias,
   NUL, an identifier with an empty segment or a duplicate same-scope alias is
   KORM-SCOPE-002. Quote segments later in Rendering; do not concatenate user SQL.
7. Validate grouping: nonaggregate output/having/order expressions must consist of
   grouping keys and constants; do not infer functional dependencies from primary
   keys. Aggregates in WHERE and invalid window contexts fail KORM-QUERY-001.
8. Before constructing a template, require a complete source binding, legal joins,
   nonempty result shape and unique projection aliases. A Cross join has no ON;
   Inner/Left/Right/Full/Lateral joins require the appropriate ON contract.
9. Return structural descriptors to Rendering and generated projection compatibility
   to Execution; do not perform driver validation here.

## Required fixtures

| ID | Input | Expected result |
| --- | --- | --- |
| QRY-01 | Base query → age-filter query; render both after modification | Base has no age predicate; filtered snapshot does |
| QRY-02 | Query built from array, then caller mutates array | Original field order/types unchanged |
| QRY-03 | users.As(u) joined users.As(manager) | Two distinct relations, correct column qualifications |
| QRY-04 | Reference original users.Id after FROM users.As(u) | KORM-SCOPE-001 |
| QRY-05 | Same-scope duplicate alias u | KORM-SCOPE-002 |
| QRY-06 | Scalar correlated subquery vs nonlateral derived sibling capture | First valid with enclosing binding; second rejected |
| QRY-07 | Projection Name/Id/Age for known User | Descriptor retains that order; generated compatibility may map members without changing SQL |
| QRY-08 | Projection duplicate alias Id | Reject before execution |
| QRY-09 | GROUP BY department, select name | KORM-QUERY-001 without a declared aggregate |
| QRY-10 | WHERE then WHERE | Second replaces first; And explicitly produces conjunction |
| QRY-11 | Negative Limit/Offset | ArgumentOutOfRangeException with query code |
| QRY-12 | 100 concurrent renders of one frozen query | Identical SQL/layout; no mutation or active I/O state |

## Local validation and handoff

Create `tests/Orm/Query/verify.py` and a native console consumer; its positive/negative
compile cases consume Foundation's reviewed API. Native behavior uses actual Types
and Query, with deterministic stub render-contract inputs until Rendering integrates.
The accepted module must pass its own immutable/scope/projection assertions; a fake
renderer does not claim SQL correctness. Register `orm-query`, its real shared
Language project inputs and contract/type dependencies. Stop after this module;
other language folders, providers and shared build files remain their owners' work.

## Explicit scalar, runtime-selected and pagination surfaces

Sql.Select<T>(Field<T>) returns Query<T>, using the fixed scalar mapping policy.
Sql.SelectDynamic(params IField[]) returns Query<DynamicRecord> with only explicitly
supported scalar cells. Freeze fields/captures; duplicate aliases and unknown or
nested dynamic cells fail before execution. DynamicRecord stores ResultShape plus
ImmutableArray<DynamicCell>; each DynamicCell<T> retains SqlType<T>/T. Get<T>(ordinal
or alias,SqlType<T>) verifies exact SQL/CLR type metadata and returns the typed cell;
no dynamic CLR type, reflection getter or object dictionary is generated. Register
its prebound provider readers in Execution as specified there. Test QUERY-DYNAMIC
with runtime fields Id/Name then Name/Age, including Carol's null Age and an
invalid Get<int> of Int64; expected owned cells and KORM-MAP-002 on mismatched Get.

Limit(int) captures an Int32 slot. LimitLiteral(int) is the explicit structural
literal form, validates the same nonnegative range and contributes its numeric
value to template identity. Only LimitLiteral(0/1), not an ordinary runtime limit
slot, can prove the SQLite scalar-subquery at-most-one condition. Offset remains
parameterized Int32. No implicit scalar rewrite inserts a limit for the caller.

## Complete query surface and ordered node contract

Add the following methods to the existing Language-owned QueryOperations class;
the declarations supplement, rather than rename, Design's existing methods. Enums
and immutable node records belong to Contracts. Public operations never accept a
SqlNode. A facade fragment is partial only inside the Language assembly.

```csharp
// QueryOperations
public static Query<T> CrossJoin<T>(this Query<T> query, TableLike table);
public static Query<T> DistinctOn<T>(this Query<T> query, params IField[] keys);
public static Query<T> Qualify<T>(this Query<T> query, Condition predicate);
public static Query<T> IntersectAll<T>(this Query<T> query, Query<T> other);
public static Query<T> ExceptAll<T>(this Query<T> query, Query<T> other);
public static Query<T> ForUpdate<T>(this Query<T> query, params TableLike[] of);
public static Query<T> ForShare<T>(this Query<T> query, params TableLike[] of);
public static Query<T> NoWait<T>(this Query<T> query);
public static Query<T> SkipLocked<T>(this Query<T> query);

// Contracts: closed public policy values
public enum SelectDistinctKind { All, Distinct, On }
public enum LockStrength { Update, Share }
public enum LockWait { Wait, NoWait, SkipLocked }
public enum SetOperationKind { Union, UnionAll, Intersect, IntersectAll, Except, ExceptAll }

// Contracts/Nodes/Query.cs: ordered immutable data, no capture sidecars
internal sealed record SortNode(SqlNode Expression, SortDirection Direction, NullOrder Nulls);
internal sealed record DistinctSpecNode(SelectDistinctKind Kind, ImmutableArray<SqlNode> Keys);
internal sealed record LockClauseNode(LockStrength Strength,
    ImmutableArray<RelationId> Of, LockWait Wait);
internal sealed record SelectNode(
    ImmutableArray<ProjectionItem> Projection,
    SqlNode? From, ImmutableArray<JoinNode> Joins, SqlNode? Where,
    ImmutableArray<SqlNode> GroupBy, SqlNode? Having,
    ImmutableArray<NamedWindowNode> Windows, SqlNode? Qualify,
    ImmutableArray<SortNode> OrderBy, SqlNode? Limit, SqlNode? Offset,
    DistinctSpecNode Distinct, ImmutableArray<CteDefinitionNode> Ctes,
    LockClauseNode? LockClause) : QueryNode(NodeKind.Select);
internal sealed record JoinNode(JoinKind JoinKind, SqlNode Right, SqlNode? On)
    : SqlNode(NodeKind.Join);
internal sealed record SetNode(SetOperationKind Operation, QueryNode Left,
    QueryNode Right, ImmutableArray<SortNode> OrderBy, SqlNode? Limit,
    SqlNode? Offset, ImmutableArray<CteDefinitionNode> Ctes)
    : QueryNode(NodeKind.Set);
```

ProjectionItem is the shared Expression/Alias/Type record also used by RETURNING.
The explicit JoinNode above refines Design's compact `left/right` illustration:
SelectNode.From and preceding joins are its left prefix; do not store or revisit a
second copy of that prefix. Join traversal emits Right then On exactly once. From,
Right and CTE/derived relation handles retain their immutable relation nodes.
SortField's IField wrapper is converted to a SortNode before storage. Optional
clauses use null; absent lists use ImmutableArray.Empty, never default arrays.
Initial Distinct is `(All, [])`. Limit permits only Int32 ParameterNode or the
explicit nonnegative LimitLiteral node; Offset permits only Int32 ParameterNode.

Distinct() replaces the specification with `(Distinct, [])`; DistinctOn replaces
it with `(On, copied keys)` and requires at least one key. It does not modify
ORDER BY. PostgreSQL applies its exact sort-group validation in the dialect packet;
the other three profiles reject this explicit node with KORM-DIALECT-001. Do not
substitute GROUP BY, MIN, ROW_NUMBER or an arbitrary representative row.

CrossJoin appends `(Cross, relation, null)`. The existing Join overload requires a
nonnull Condition and rejects JoinKind.Cross; callers use CrossJoin for that form.
LateralInner/LateralLeft remain explicit JoinKind values. Qualify replaces only
the Qualify condition and merges its captures. It survives every common pass; all
four initial profiles reject it with KORM-DIALECT-001, feature `Qualify`. No derived
table transformation is part of this baseline. The explicit node permits a future
reviewed rule without an untyped raw clause today.

Union/UnionAll/Intersect/IntersectAll/Except/ExceptAll construct a binary SetNode,
freeze both operand snapshots, preserve the left result aliases, and verify equal
degree, logical member layout, SQL identity, facets, nullability and CLR carriers.
There is no implicit common-type widening. Its initial tail is empty. Subsequent
OrderBy/Limit/LimitLiteral/Offset/With modify the set's tail, not either operand.
OrderBy on a compound requires an output alias or an exact projected expression
resolved to that alias; an unrelated source expression fails KORM-QUERY-001.
From/Where/Join/GroupBy/Having/Distinct/DistinctOn/Qualify/Window/lock operations on
a SetNode fail KORM-QUERY-001; use AsTable and an outer Select to apply them. A
child's already declared order/pagination/CTEs remain on that child and are subject
to the dialect's parenthesized-operand rule. Never flatten the operation tree.

ForUpdate/ForShare replace the lock strength and copied OF relations and reset the
wait policy to Wait. Duplicate OF identities, unknown relations, NoWait/SkipLocked
without a lock, and applying the other wait policy after one was chosen fail
KORM-QUERY-002. Applying the same wait policy twice is idempotent. OF entries must
be physical Table instances already bound in this SELECT, never outer/CTE/derived
relations. The initial lockable SELECT subset has physical FROM and physical
INNER/CROSS joins, no DISTINCT/group/aggregate/window/set form. Other combinations
fail KORM-DIALECT-001, feature `LockShape`; no clause is silently dropped. Locks
use the caller's transaction lifetime. Rendering/execution neither starts a hidden
transaction nor guarantees a lock remains after an autocommit statement finishes.

| Profile | Exact admitted lock spelling |
| --- | --- |
| PostgreSQL | `FOR UPDATE` / `FOR SHARE`, optional `OF <quoted local aliases>`, optional `NOWAIT` / `SKIP LOCKED` |
| SQLite | Every lock node fails KORM-DIALECT-001 |
| MySQL 8.4 | `FOR UPDATE` / `FOR SHARE`, optional `NOWAIT` / `SKIP LOCKED`; nonempty OF fails KORM-DIALECT-001 in this bounded surface |
| MariaDB 11.8 | `FOR UPDATE` / `LOCK IN SHARE MODE`, Wait only; nonempty OF and explicit wait modifiers fail KORM-DIALECT-001 in this baseline |

Key-share/no-key-update, numeric WAIT and lock-timeout session mutations have no
public entry in this version. This table defines the previously vague “modeled
native forms”; it is not a claim that a server lacks other locking syntax.

### Surface fixtures added to this gate

| ID | Input | Required node/result |
| --- | --- | --- |
| QRY-13 | Select(Id).DistinctOn(Department).OrderBy(Department.Asc(), Id.Desc()) | One On key; PG native DISTINCT ON; other profiles KORM-DIALECT-001 |
| QRY-14 | DistinctOn(a,b), order a / order b,a,c / order a,c / order a,c,b | PG accepts first two and rejects last two; follow the pinned PG sort-group algorithm |
| QRY-15 | Qualify(RowNumber().Over(w).Ge(1L)) | Qualify node retained; all four profile renders fail before a template is returned |
| QRY-16 | ForUpdate(users).NoWait() and ForShare().SkipLocked() | Exact PG lock text above; second form also native MySQL; SQLite/Maria wait forms rejected |
| QRY-17 | NoWait without lock; NoWait then SkipLocked | KORM-QUERY-002 |
| QRY-18 | A.IntersectAll(B).OrderBy(projectedAlias.Asc()).Limit(2) | IntersectAll binary node, root order/limit, unchanged operands; SQLite rejects ALL |
| QRY-19 | A.Union(B).Where(predicate) | KORM-QUERY-001; explicit outer AsTable variant is accepted |
| QRY-20 | CrossJoin(table) vs Join(table, condition, Cross) | First has no ON; second KORM-QUERY-002 |
