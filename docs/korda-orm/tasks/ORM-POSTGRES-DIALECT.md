# ORM-POSTGRES-DIALECT — PostgreSQL SQL profile

Status: `planned_candidate`; product implementation is **not authorized**.

## Objective and fixed inputs

Implement the pure PostgreSQL 18 profile. Follow Design
`docs/korda-orm/implementation-spec.md` and `contracts.md` at the immutable Design
revision recorded in the batch handoff; consume ORM-C01, ORM-C02, ORM-C03 and
ORM-C06. The shared API is `Query<T>`, `Projection<T>`, `RenderedTemplate<T>`,
`ParameterValues` and `BoundCommand<T>`. This packet fixes profile decisions;
implementers must not substitute a provider-driven SQL generator.

Start: `ORM-FOUNDATION`. Acceptance: `ORM-RENDER`, `ORM-ADVANCED-TYPES` and
`ORM-NESTED`. Work on profile data and fixtures against the fixed contracts while
those peers are developed; final acceptance integrates their actual node handlers. The PostgreSQL lane is mandatory in the
final matrix, independently selectable from other providers.

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

## Source inheritance and files

All jOOQ references are the Apache-2.0 public source at commit
`3c58109e7ab69772de75e640852935ee7e284177` (3.21.10), under
`jOOQ/src/main/java/org/jooq/impl/`. Retain upstream notices for adapted bodies and
record the exact source symbol and local test in the adaptation manifest.

| Source symbol | Required local translation |
| --- | --- |
| `SelectQueryImpl.toSQLReference0`, `unionParenthesis` | Clause order, grouped set operands and local versus outer pagination; use the shared immutable nodes, not its mutable Java builder |
| `CommonTableExpressionImpl.accept` | CTE names/column lists and native materialization keywords |
| `InsertQueryImpl.accept1`, `acceptOnConflictWhere` | Explicit conflict target, target predicate, assignments and update predicate in their distinct positions |
| `AbstractDMLQuery.toSQLReturning`, `nativeSupportReturning` | Native projection rendering for each DML kind; no generated-key fallback |
| `SortFieldImpl.accept`, `acceptFieldAndOrder` | Native `NULLS FIRST/LAST` without repeated expression evaluation |
| `DefaultBinding` JSON/JSONB/array/enum handling | Preserve type identities in render descriptors; provider binding remains outside this project |

Own `src/Orm/Dialects/PostgreSql/` and `tests/Orm/Dialects/PostgreSql/` only.
Foundation owns the project file; the initial project is
`Korda.Orm.Dialects.PostgreSql.csproj`. Add these files with these responsibilities:

| File / type | Required methods and output |
| --- | --- |
| `Profile.cs` / `PostgreSqlProfile` | `Create()` returns PostgreSql, minimum 18.0, maximum exclusive 19.0, numbered placeholders; settings include `standard_conforming_strings=on` and `max_parameters=65535` |
| `CapabilityTable.cs` | `Resolve(NodeKind, context)` returns Native, Lowered with rule ID, or a diagnostic; no Boolean that loses the reason |
| `Lowering.cs` / `PostgreSqlLowering` | `ValidateProfile`, `ValidateConflict`, `ValidateReturning`, `Lower`; return immutable nodes and capability evidence |
| `TypeNames.cs` / `PostgreSqlTypeNames` | `WriteType(SqlTypeDescriptor, ISqlWriter)` and `WriteQualifiedType(SqlName, ISqlWriter)`; no driver assembly |
| `PostgreSqlWriter.cs` | `WriteSelect`, `WriteInsert`, `WriteUpdate`, `WriteDelete`, `WriteCte`, `WriteSet`, `WriteSort`; call shared `Visit`, `Quote` and `NextParameter` |
| `PostgreSqlLiteralWriter.cs` | `Write(TypedLiteral, ISqlWriter)`; explicit SQL literals only, never captured invocation values |
| Test files | `ProfileTests`, `ParameterLayoutTests`, `ConflictTests`, `ReturningTests`, `SetAndCteTests`, `UnsupportedTests`; fixture files named `pg-<case>.json` |

The profile object is immutable and participates in the template fingerprint.
Pure rendering trusts the supplied profile. The driver separately verifies actual
server family/version/settings; it must not mutate the rendered template.

## Native inventory and exact rejection boundary

Native baseline: inner/left/right/full/cross joins; declared lateral inner/left
joins; ordinary and recursive SELECT CTEs; materialized/not-materialized CTEs;
UNION/INTERSECT/EXCEPT with DISTINCT or ALL; ROWS/RANGE/GROUPS windows and EXCLUDE;
LIMIT/OFFSET; native NULL ordering; `IS [NOT] DISTINCT FROM`; single-table
INSERT/UPDATE/DELETE RETURNING; and explicit PostgreSQL ON CONFLICT. `DISTINCT ON`
is admitted only as its explicit node with the ORDER BY prefix validation below.
CTE bodies containing accepted DML are admitted only in the explicit DML-CTE
context, with a declared RETURNING shape and no recursive self-reference.

Unsupported baseline: QUALIFY, MERGE, vendor optimizer hints, procedural SQL,
implicit generated-key queries, and any feature missing a registered writer.
No generic “PostgreSQL supports advanced SQL” flag enables these families. Lock
clauses are limited to the explicitly modeled `FOR UPDATE` / `FOR SHARE`, optional
OF relation list and NOWAIT or SKIP LOCKED; mutually exclusive wait policies fail.

## Rendering and lowering recipe

1. Run shared scope/type/degree validation. Check family/version/settings before
   inspecting individual nodes. Reject an unsupported node before emission; a
   failed render returns no SQL/template/parameter list.
2. Use quoted identifier segments everywhere: `a.b` supplied as one segment is
   `"a.b"`; two segments are `"a"."b"`; double an embedded `"`. Never split user
   identifier text on dots. An explicit result alias is always quoted.
3. Call `NextParameter` at every final emitted parameter occurrence. Output `$1`,
   `$2`, ...; layout `Ordinal` remains zero-based and `Name` is empty. Repeating
   one `SlotId` creates another physical parameter with the same type/value
   identity. Check the final count against 65,535 before publishing the template.
4. Emit ordinary comparisons unchanged, including `field = $n` for a typed NULL
   argument. Only an explicit null-test node emits `IS NULL`; equality to NULL is
   SQL UNKNOWN. Empty IN/NOT IN is the shared FALSE/TRUE lowering.
5. Emit LIMIT then OFFSET as typed Int32 parameters in final SQL order. LIMIT 0
   remains zero. A nonnegative OFFSET without LIMIT emits only OFFSET. Reject
   negative pagination values before writing; no sentinel unlimited number.
6. Preserve each set node's grouping. Parenthesize a child set whenever its tree
   grouping or local ORDER/LIMIT differs from the surrounding set; outer ORDER/
   LIMIT follows the complete set. Validate equal degree and registered compatible
   SQL types before quoting aliases; output aliases come from the left operand.
7. Validate DISTINCT ON with PostgreSQL's sort-group rule: collect its normalized
   expression identities; walk distinct ORDER BY identities in order, marking when
   the first non-DISTINCT-ON expression is encountered. A later DISTINCT-ON key is
   invalid; a missing DISTINCT-ON key after a non-key sort item is also invalid.
   A shorter ORDER BY containing only a subset of DISTINCT-ON keys is legal, as is
   omitted ordering, but does not promise a reproducible chosen representative.
   Duplicate ORDER identities are ignored for this validation only, as the native
   sort-group references do. Preserve emitted SQL. For keys (a,b), ORDER BY b,a,c
   and ORDER BY a are admitted; ORDER BY a,c and ORDER BY a,c,b fail. This rule
   follows inspected PostgreSQL 18.7 parse_clause.c::transformDistinctOnClause,
   not an invented complete-prefix restriction. A caller needing deterministic
   representatives supplies the complete tie-breaking order.
8. Render CTE names and declared columns before their bodies. `WITH RECURSIVE`
   appears once when any member is recursive. Materialization is a planner
   directive supported by this profile, not a promise of execution cost. Scope
   and recursion shape checks stay in the relational validator.
9. Emit casts as `CAST(expression AS type)` to avoid precedence surprises.
   Built-in names: Int32 `integer`, Int64 `bigint`, Boolean `boolean`, Text `text`,
   Binary `bytea`, Decimal `numeric(p,s)`, UUID `uuid`, JSON `json`, JSONB `jsonb`,
   date/time/timestamp according to their declared temporal identity. Array suffix
   follows its element type. Enum/domain names use quoted catalog segments and
   never a caller-provided SQL fragment. Unsupported facets fail TYPE diagnostics.
10. Explicit Text literals use ordinary single quotes with doubled apostrophes
    under the required standard-conforming-strings setting. Reject U+0000 because
    PostgreSQL text cannot contain it. Binary literals use a deterministic hex
    bytea encoding. Ordinary runtime text, including attack-shaped text, stays in
    `ParameterValues` and cannot reach this literal writer.

### Conflict and RETURNING algorithm

The DML node must distinguish `TargetColumns(columns,predicate?)`,
`TargetConstraint(name)`, and `AnyUniqueKey`. `DO UPDATE` requires one of the first
two; `DO NOTHING` may omit a target. Column targets must be nonempty, belong to the
insert target, have no duplicate column identity, and match the declared unique
key/index intent when metadata is available. A target predicate is rendered inside
ON CONFLICT's target section; it is never moved into the DO UPDATE WHERE section.
Constraint and column-target forms are mutually exclusive.

Excluded-value references are an explicit node and emit `"excluded"."column"`.
They are legal only inside the conflict update context and must reference an
insertable target column. Assignment targets are unique. The update predicate
retains its normal three-valued logic. There is no attempt to infer which unique
constraint the application meant from an eventual server error.

RETURNING emits the supplied projection in its declared order with explicit
aliases. It produces the same result-shape contract as SELECT. A zero-row DML
result is a valid empty sequence; affected count, generated identity and result
row count are separate concepts. RETURNING reads target-row columns and accepted
expressions; no implicit old/new pseudo-table feature is added by PostgreSQL 18.

## Exact fixtures and diagnostics

The fixture schema is `users(id bigint primary key, name text not null, score
bigint null, email text unique)`. Use rows `(1,'Ada',10,'a')`, `(2,'Bo',NULL,'b')`,
`(3,'Cy',30,'c')`; database fixtures reset their own tables.

| Case | Exact expectation |
| --- | --- |
| `pg-repeat` | `SELECT "u"."id" AS "Id" FROM "users" AS "u" WHERE ("u"."score" >= $1 OR "u"."id" = $2) ORDER BY "u"."id" ASC`; both occurrences refer to the same Int64 slot with value 2; result IDs 1,2,3 |
| `pg-null` | `"u"."score" = $1` with typed NULL yields no rows; `"u"."score" IS NULL` yields ID2; no SQL rewrite based on the runtime value |
| `pg-null-order` | `ORDER BY "u"."score" ASC NULLS LAST, "u"."id" ASC`; IDs 1,3,2 |
| `pg-upsert` | `INSERT INTO "users" ("id", "name", "score", "email") VALUES ($1, $2, $3, $4) ON CONFLICT ("id") DO UPDATE SET "name" = "excluded"."name" RETURNING "id" AS "Id", "name" AS "Name"`; inserting `(1,'Ada2',99,'a')` returns `(1,'Ada2')` and leaves score 10 |
| `pg-set-grouping` | `A EXCEPT (B EXCEPT C)` retains right grouping; A={1,2,3}, B={2,3}, C={3} produces {1,3}; flattened form would be wrong |
| `pg-dml-cte` | A declared INSERT RETURNING CTE feeds a SELECT, uses one statement and one transaction; same body marked recursive fails |
| `pg-budget` | 65,535 final placeholders admitted; 65,536 fails before a template exists, including repeated uses of one logical slot |

Diagnostic message templates are fixed; fill braces with invariant text and add
node-path/profile properties from the common diagnostic type:

| Code | Message and condition |
| --- | --- |
| `KORM-DIALECT-001` | `Feature '{feature}' is not supported by profile '{profile}'.` Unknown/unsupported writer or clause |
| `KORM-DIALECT-002` | `Parameter count {actual} exceeds profile limit {limit}.` Final occurrence count |
| `KORM-DIALECT-003` | `Profile setting '{setting}' must be '{required}'.` Incorrect family/version or required setting uses the relevant setting name |
| `KORM-DIALECT-004` | `Conflict policy '{policy}' cannot preserve its declared target on '{profile}'.` Invalid or ambiguous conflict intent |
| `KORM-DIALECT-005` | `RETURNING form '{form}' is not supported by profile '{profile}'.` Illegal returning context |
| `KORM-DIALECT-006` | `Lowering '{rule}' cannot preserve evaluation semantics at '{path}'.` DISTINCT ON prefix/order or an unavailable semantic rewrite |

## Acceptance and handoff

Run pure positive/negative fixtures, exact SQL/layout/result snapshots and the
eligible pinned jOOQ differential cases. Independently assert semantic outputs;
Java SQL text equality alone is insufficient. Publish/run a Native AOT renderer
consumer that references no Npgsql or execution assembly. Execute the server
fixtures only in the PostgreSQL integration lane, recording the exact 18.x build.
The research fixture server was PostgreSQL 18.7; that observation does not accept
future product handlers.

Deliver capability entries, lowerings, diagnostics and fixture paths to RENDER,
DML, RELATIONAL, ADVANCED-TYPES, NESTED and POSTGRES-DRIVER. Routine pure checks
select no database. Keep raw logs in scratch. Stop at the reviewed task PR; no
provider protocol, production execution loop, merge, publication or legacy change.

Primary semantics: [PostgreSQL SELECT](https://www.postgresql.org/docs/18/sql-select.html),
[INSERT / ON CONFLICT](https://www.postgresql.org/docs/18/sql-insert.html),
[WITH](https://www.postgresql.org/docs/18/queries-with.html),
[lexical structure](https://www.postgresql.org/docs/18/sql-syntax-lexical.html).

## Exact local runner contract

This task owns `tests/Orm/Dialects/PostgreSql/verify.py`,
`tests/Orm/Dialects/PostgreSql/Korda.Orm.Dialects.PostgreSql.Tests.csproj` and its Program/fixture files.
The CI command, from repository root with no additional flags, is:

```sh
python3 tests/Orm/Dialects/PostgreSql/verify.py
```

The runner compiles the packet's positive/negative declaration cases, publishes
its actual consumer with `dotnet publish tests/Orm/Dialects/PostgreSql/Korda.Orm.Dialects.PostgreSql.Tests.csproj -c Release -r linux-x64 -p:PublishAot=true`,
then executes that native consumer and asserts RuntimeFeature.IsDynamicCodeSupported
is false. Use the repository's pinned SDK/restore settings; place outputs under
artifacts, never beside source. Run this packet's enumerated pure fixtures and
report individual case failures with nonzero exit. The runner does not start a
database, accept an absent peer as a passing stub, or claim live SQL correctness.
Real four-server rows, faults and SQL execution remain ORM-INTEGRATION's gate.
