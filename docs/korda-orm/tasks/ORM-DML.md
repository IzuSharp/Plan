# ORM-DML: Implement fixed typed mutations and native returning semantics

Status: `planned_candidate`; product implementation remains unauthorized.

Use the immutable Design commit in `../implementation-graph.json`, contracts v0.2.0,
and `docs/korda-orm/implementation-spec.md`. The packet fixes implementation work;
contradictions return to the contract owner before changing an interface or policy.

## Gate, scope and source

Start after Foundation; accept after Query. Own `src/Orm/Language/Dml/` and
`tests/Orm/Dml/`. Use ORM-C01/C02/C03/C06, implementation-spec, dialect packets and
pinned jOOQ `InsertQueryImpl`, `InsertImpl`, `FieldMapsForInsert`, `UpdateQueryImpl`,
`DeleteQueryImpl`, `AbstractDMLQuery` at
`3c58109e7ab69772de75e640852935ee7e284177`.

| File | Fixed deliverable |
| --- | --- |
| `Sql.Dml.cs`, `InsertBuilder.cs` | InsertInto(target, columns), Values rows, FromSelect source, DefaultValues |
| `UpdateBuilder.cs`, `Assignment.cs` | Update(target), Set<T>(Field<T>,T/Param<T>/Field<T>), Where, From |
| `DeleteBuilder.cs` | DeleteFrom(target), Where, Using |
| `ConflictClause.cs` | Explicit target columns/constraint, DoNothing or DoUpdate assignments; no guessed conflict target |
| `DmlOperations.cs`, `Returning.cs` | Returning(Projection<T>) creates ReturningMutation<T> |
| `DmlValidator.cs` | Target/column/type/source/assignment/returning capability validation |

Builders are immutable snapshots like Query<T>. A mutation without returning has
an affected-row-count result; returning has the declared Projection<T>. Freeze row
collections and captured values. Execute uses the same rendered-command contract
and mature Dapper command runtime; do not add a mutation-specific reader loop.

## Exact public surface and cross-module result types

Contracts declares `abstract Mutation` with internal `DmlNode Node` and captured
values; sealed InsertBuilder/UpdateBuilder/DeleteBuilder derive from it.
ReturningMutation<T> is a separate immutable handle with its DmlNode, captures and
Projection<T>. None exposes a public unchecked node constructor. Language owns
these factories/extensions (bodies follow the algorithms below):

```csharp
// Sql.Dml.cs, the existing Language-owned partial Sql facade
public static InsertBuilder InsertInto(Table target, params IField[] columns);
public static UpdateBuilder Update(Table target);
public static DeleteBuilder DeleteFrom(Table target);
public static Field<T> Value<T>(T value, SqlType<T> type);
public static Field<T> Value<T>(Param<T> value);
public static Field<T> Excluded<T>(Field<T> targetColumn);
public static Cte<T> Cte<T>(string name, ReturningMutation<T> command);
public static Assignment Set<T>(Field<T> column, Field<T> value);
public static Assignment Set<T>(Field<T> column, Param<T> value);
public static Assignment Set<T>(Field<T> column, T value);

// DmlOperations extension methods, all immutable
public static InsertBuilder Values(this InsertBuilder command, params IField[] row);
public static InsertBuilder FromSelect<T>(this InsertBuilder command, Query<T> source);
public static InsertBuilder DefaultValues(this InsertBuilder command);
public static ConflictBuilder OnConflict(this InsertBuilder command, params IField[] columns);
public static ConflictBuilder OnConflictConstraint(this InsertBuilder command, SqlName constraint);
public static ConflictBuilder OnAnyUniqueKey(this InsertBuilder command);
public static ConflictBuilder TargetWhere(this ConflictBuilder conflict, Condition predicate);
public static InsertBuilder DoNothing(this ConflictBuilder conflict);
public static InsertBuilder DoUpdate(this ConflictBuilder conflict, params Assignment[] assignments);
public static InsertBuilder ConflictUpdateWhere(this InsertBuilder command, Condition predicate);
public static UpdateBuilder Set<T>(this UpdateBuilder command, Field<T> column, T value);
public static UpdateBuilder Set<T>(this UpdateBuilder command, Field<T> column, Param<T> value);
public static UpdateBuilder Set<T>(this UpdateBuilder command, Field<T> column, Field<T> value);
public static UpdateBuilder From(this UpdateBuilder command, params TableLike[] tables);
public static UpdateBuilder Where(this UpdateBuilder command, Condition predicate);
public static UpdateBuilder AllRows(this UpdateBuilder command);
public static DeleteBuilder Using(this DeleteBuilder command, params TableLike[] tables);
public static DeleteBuilder Where(this DeleteBuilder command, Condition predicate);
public static DeleteBuilder AllRows(this DeleteBuilder command);
public static ReturningMutation<T> Returning<T>(this Mutation command, Projection<T> projection);
public static InsertBuilder With(this InsertBuilder command, params Cte[] definitions);
public static UpdateBuilder With(this UpdateBuilder command, params Cte[] definitions);
public static DeleteBuilder With(this DeleteBuilder command, params Cte[] definitions);
public static ReturningMutation<T> With<T>(this ReturningMutation<T> command, params Cte[] definitions);
```

Insert columns/row arrays are the explicitly runtime-validated degree API; each
IField retains its typed descriptor. Values appends one row; repeated calls build
multi-row input. Values, FromSelect and DefaultValues are mutually exclusive.
Sql.Value captures a parameter, never a literal. Set preserves its target T at
compile time and validates SQL domain compatibility at construction. Where replaces
the previous predicate; AllRows clears it and sets the deliberate all-rows flag.
Calling Where clears that flag. DoUpdate requires at least one unique assignment.
ConflictUpdateWhere without DoUpdate, TargetWhere on a named constraint or an
any-key target, and duplicate conflict declarations fail KORM-QUERY-002.

Rendering owns these exact overloads in SqlRenderer: `Render(Mutation,SqlProfile,
RenderShape?=null):RenderedMutationTemplate`, `RenderAndBind(Mutation,SqlProfile,
ParameterValues?=null):BoundMutation`, and the corresponding generic overloads
for ReturningMutation<T> returning RenderedTemplate<T>/BoundCommand<T>. A
RenderedMutationTemplate has Id/Sql/Profile/Parameters but no row mapping. Its
Bind(ParameterValues) returns a fresh BoundMutation with the same one-consumption
state as BoundCommand<T>. Both classes have internal constructors. Shared internal
render code is reused; no copied renderer implementation is introduced.

Execution provides `int Execute(this Mutation,OrmSession)`, `int Execute(this
BoundMutation,OrmSession)`, and Task<int> ExecuteAsync overloads with a final default
CancellationToken. ReturningMutation<T> supplies ToList/ToListAsync/StreamAsync
with the same signatures as Query<T>; it renders then calls the existing typed
BoundCommand terminal. It cannot be passed to Execute, which would discard rows.
The optional parser returns concrete builders for nonreturning statements and
ReturningMutation<T> only with an explicit expected projection.

ReturningProjectionNode(Target,Items) is a shared node; each ProjectionItem holds
Expression/Alias/SqlTypeDescriptor. Its common visitor pushes a returning-clause
context and restores it in finally. SQLite's context emits target column names
without table qualification and rejects columns from another relation with KORM-DIALECT-005. Other
profiles apply their explicit returning rules. This is operation-local state,
not a mutable global flag or a second projection traversal.

### Complete mutation payloads and construction rules

Foundation declares these internal records in Contracts/Nodes/Dml.cs. Public
Assignment/ConflictBuilder handles have internal constructors and frozen payloads;
Assignment holds AssignmentNode plus Captured. ConflictBuilder holds the base
InsertNode, selected conflict target and Captured, and is not itself executable.
Every below SqlNode tag is included in the closed shared visitor dispatch.

```csharp
public enum ConflictTargetKind { Columns, Constraint, AnyUniqueKey }
public enum ConflictAction { DoNothing, DoUpdate }
internal sealed record AssignmentNode(ColumnNode Target, SqlNode Value);
internal sealed record ConflictTargetNode(ConflictTargetKind Kind,
    ImmutableArray<ColumnNode> Columns, SqlName? Constraint, SqlNode? Predicate);
internal sealed record ConflictNode(ConflictTargetNode Target, ConflictAction Action,
    ImmutableArray<AssignmentNode> Assignments, SqlNode? UpdateWhere);
internal abstract record InsertSource;
internal sealed record ValuesSource(ImmutableArray<ImmutableArray<SqlNode>> Rows)
    : InsertSource;
internal sealed record QuerySource(QueryNode Query) : InsertSource;
internal sealed record DefaultValuesSource : InsertSource;
internal sealed record InsertNode(TableNode Target, ImmutableArray<ColumnNode> Columns,
    InsertSource? Source, ConflictNode? Conflict, ReturningProjectionNode? Returning,
    ImmutableArray<CteDefinitionNode> Ctes) : DmlNode(NodeKind.Insert);
internal sealed record UpdateNode(TableNode Target,
    ImmutableArray<AssignmentNode> Assignments, ImmutableArray<SqlNode> From,
    SqlNode? Where, bool AllowAllRows, ReturningProjectionNode? Returning,
    ImmutableArray<CteDefinitionNode> Ctes) : DmlNode(NodeKind.Update);
internal sealed record DeleteNode(TableNode Target, ImmutableArray<SqlNode> Using,
    SqlNode? Where, bool AllowAllRows, ReturningProjectionNode? Returning,
    ImmutableArray<CteDefinitionNode> Ctes) : DmlNode(NodeKind.Delete);
internal sealed record ExcludedNode(RelationId Target, SqlName Column,
    SqlTypeDescriptor Type) : SqlNode(NodeKind.Excluded);
internal sealed record ProjectionItem(SqlNode Expression, string Alias,
    SqlTypeDescriptor Type);
internal sealed record ReturningProjectionNode(RelationId Target,
    ImmutableArray<ProjectionItem> Items) : SqlNode(NodeKind.ReturningProjection);
```

Source=null is only an unfinished insert builder and fails KORM-QUERY-002 at render.
ValuesSource contains one or more copied nonempty equal-degree rows; QuerySource
contains one query; DefaultValuesSource contains neither rows nor query. No enum
plus contradictory payload combinations are permitted. DefaultValues requires an
empty InsertInto column list; other sources require a nonempty target list. An
unfinished update with no assignments similarly fails before rendering. From and
Using replace their arrays. These are ordered relation sources: join predicates
are written explicitly in Where in this baseline; there is no hidden joined-DML
builder or vendor multi-target mutation. Returning replaces no mutation state and
cannot be called twice because ReturningMutation<T> is not a Mutation.

OnConflict(columns) requires one or more unique target columns. OnConflictConstraint
requires one validated identifier; OnAnyUniqueKey stores neither columns nor a
constraint. TargetWhere is available only for the Columns target. OnAnyUniqueKey
plus DoNothing means native targetless PostgreSQL/SQLite DO NOTHING; MySQL/Maria
reject it. OnAnyUniqueKey plus DoUpdate is the only accepted duplicate-key update
intent for MySQL/Maria; PostgreSQL/SQLite reject that missing-target update.
DoNothing has empty assignments and null UpdateWhere. DoUpdate has a nonempty
unique target assignment array; ConflictUpdateWhere requires that action.

Sql.Excluded validates a physical target ColumnNode, keeps its exact type/domain,
and creates ExcludedNode. It is legal only inside that insert's conflict-update
assignment RHS or update predicate, with matching target RelationId. Use in VALUES,
ordinary SELECT/UPDATE/DELETE, a conflict target predicate, or RETURNING fails
KORM-SCOPE-001. The dialects spell it `excluded.column` (PG/SQLite), the allocated
inserted-row alias (MySQL VALUES-source only), or `VALUES(column)` (MariaDB). This
is structural intent, never a user string pasted into SQL.

With appends copied definitions in the declared order and merges captures using
the same duplicate/name/visibility algorithm as Query.With. Cte(name, returning)
allocates one CteId, freezes the returning shape and mutation, and uses a
CteDefinitionNode with Recursive=false and Materialization.Default. It requires a
nonnull explicit RETURNING projection and cannot be made recursive; a callback or
reflection over T is never used to discover columns. The resulting Cte<T>.As(alias)
exposes the same typed Column<U> lookup as a SELECT CTE.

| Context | Admitted exact behavior |
| --- | --- |
| PostgreSQL outer INSERT/UPDATE/DELETE With | Emit one top-level WITH before the mutation; SELECT and accepted nonrecursive RETURNING DML CTE bodies are allowed |
| PostgreSQL SELECT With containing DML body | Allowed only in the statement's top-level WITH; a DML CTE nested in a scalar/derived/CTE body fails KORM-DIALECT-001, feature `DmlCteTopLevel` |
| SQLite outer INSERT/UPDATE/DELETE With | Read-only SELECT CTE bodies only; a DML CTE body always fails KORM-DIALECT-001 |
| MySQL outer UPDATE/DELETE With | Read-only SELECT CTE bodies; outer InsertBuilder.With is excluded with KORM-DIALECT-001 |
| MariaDB outer mutation With | Excluded with KORM-DIALECT-001 in the fixed 11.8 profile |
| MySQL/Maria INSERT ... SELECT with sourceQuery.With(cte) | Keep WITH inside the QuerySource after the INSERT target/column prefix; do not move it before INSERT |

PostgreSQL/SQLite can retain source-query WITH in INSERT ... SELECT as well; no
CTE is hoisted through a scope boundary. A CTE body that already carries its own
CTEs is legal only under these same statement-context checks. PostgreSQL executes
a data-modifying CTE according to native statement/snapshot semantics; there is no
promise of a chosen execution order among independent mutations. Do not emulate
the operation with a transaction and two commands on another profile.

## Fixed operation algorithms

1. InsertInto validates one physical target and a unique ordered column list from
   that target. Values validates identical degree and compatible SQL type per row.
   An empty values collection is a validation error, not DEFAULT VALUES. The latter
   has its own explicit operation and dialect check.
2. Visit insert rows in row-major column order. Each scalar binding occurrence is
   recorded in that exact order. FromSelect checks output degree/types and preserves
   its nested query scopes; do not parse generated SQL to discover columns.
3. Update stores assignments in declaration order, rejects the same target twice,
   and validates that every target belongs to the mutation relation. Its public
   semantic contract is old-row evaluation. Self `x=x+1` is allowed; cross-assignment
   dependencies on another written target are rejected for MySQL/Maria by
   KORM-DIALECT-007. Never reorder assignments to hide this semantic difference.
4. Delete preserves one explicit target. From/Using/join forms are separate node
   data and profile capabilities; no renderer silently drops a requested join.
5. A missing WHERE is an explicit all-rows mutation, not an automatically invented
   predicate. Provide the named `AllRows()` builder marker and require it when
   Update/Delete has no Where; otherwise KORM-QUERY-003. This makes the deliberate
   operation explicit without an external confirmation flow.
6. Conflict targets and updates are structural SQL data. PostgreSQL/SQLite use the
   declared ON CONFLICT form. MySQL/Maria may use ON DUPLICATE KEY only for the
   explicitly compatible any-unique-key semantics specified in their packets;
   a named target that cannot be honored fails before rendering.
7. Returning appends the exact ordered projection and aliases. Native support is
   per operation/profile: do not infer UPDATE RETURNING from INSERT RETURNING.
   No generated-key lookup, follow-up SELECT, hidden transaction or LastInsertId
   reconstruction is performed by this packet.
8. Render only one SQL command with a complete result/parameter layout. Mutations
   with no returning use the mature Execute/ExecuteAsync endpoint; returning uses
   the same generated RowFactory as SELECT.
9. Keep actual server affected-row conventions visible through provider metadata;
   do not equate MySQL changed rows with matched rows without its configured mode.

## Required fixture matrix

| ID | Case | Expected |
| --- | --- | --- |
| DML-01 | Two rows × three insert columns | Six occurrences in row-major order |
| DML-02 | Duplicate insert/update target column | KORM-QUERY-002 |
| DML-03 | Values degree differs from column list | Negative compile where expressible, otherwise KORM-QUERY-002 |
| DML-04 | InsertFromSelect wrong SQL type/domain | Explicit type failure |
| DML-05 | Int64 target x assigned x.Add(1L) | Valid native assignment; source value is old x |
| DML-06 | Set a=b, b=a on MySQL/Maria | KORM-DIALECT-007; no reordered SQL |
| DML-07 | Update/Delete no Where and no AllRows marker | KORM-QUERY-003 |
| DML-08 | Explicit AllRows marker | Single all-row mutation allowed; exact rowcount verified in Integration |
| DML-09 | PostgreSQL insert returning Id/Name | One command, declared DTO layout |
| DML-10 | MySQL returning requested | Explicit unsupported; not clause omission |
| DML-11 | SQLite conflict target mismatch or unsupported constraint form | Exact profile failure |
| DML-12 | Native RETURNING empty result | Empty typed collection; no synthesized last-insert row |
| DML-13 | Upsert assignment Sql.Set(users.Name, Sql.Excluded(users.Name)) | Matching target ExcludedNode; exact per-profile spelling above |
| DML-14 | Sql.Excluded(otherTable.Name) in users conflict update | KORM-SCOPE-001 |
| DML-15 | PG Cte("changed", Update(users).Set(score,1).AllRows().Returning(idProjection)); Select(changed.As("c").Column("Id",Int64)).With(changed) | One WITH ... UPDATE ... RETURNING ... SELECT statement; output comes only from the CTE's declared returning relation |
| DML-16 | Same DML body on SQLite/MySQL/Maria, or nested PG DML WITH | KORM-DIALECT-001 before template publication |
| DML-17 | MySQL sourceQuery.With(readCte) passed to Insert.FromSelect | `INSERT INTO ... (...) WITH ... SELECT ...`; outer Insert.With fails explicitly |
| DML-18 | DefaultValues with explicit target column list; empty Values row | KORM-QUERY-002; neither is silently rewritten |

## Validation and stop

`python3 tests/Orm/Dml/verify.py` runs native node/validation/layout assertions and
negative compiler cases. Supply exact insert/update/delete fixtures to each dialect
owner; Integration executes them against real disposable databases, including
transaction rollback and affected-row modes. Register `orm-dml` and only its actual
shared Language inputs/consumers. Stop after the DML module; do not implement
multi-command RETURNING, bulk loaders, legacy migrations or package publication.
