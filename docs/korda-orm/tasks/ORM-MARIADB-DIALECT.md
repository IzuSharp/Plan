# ORM-MARIADB-DIALECT — MariaDB SQL profile

Status: `planned_candidate`; product implementation is **not authorized**.

## Objective and dependencies

Implement MariaDB 11.8 as a distinct pure dialect. Follow Design
`implementation-spec.md`, `contracts.md` and `dialects-and-generation.md` at the
immutable batch revision; consume ORM-C01, ORM-C02, ORM-C03 and ORM-C06. Start:
`ORM-FOUNDATION`; acceptance: `ORM-RENDER`, `ORM-ADVANCED-TYPES` and `ORM-NESTED`. Development is independent from the
MySQL dialect. MariaDB is a separate mandatory lane in final acceptance even though
both families use the same mature .NET driver.

Own `src/Orm/Dialects/MariaDb/` and `tests/Orm/Dialects/MariaDb/`. The provider owner
implements actual connections/codecs/catalog inspection; this project depends
only on rendering/type contracts. Foundation owns its project/root registration.

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

## Exact files and source symbols

Pin jOOQ 3.21.10 commit `3c58109e7ab69772de75e640852935ee7e284177`, public
`jOOQ/src/main/java/org/jooq/impl/` sources. Keep source/license/test attribution
for translated bodies and distinguish a source-inspired adaptation from unchanged
runtime reuse.

| Local file / type | Fixed methods | Source input |
| --- | --- | --- |
| `Profile.cs` / `MariaDbProfile` | `Create`, `ValidateSettings` | Explicit server profile; not a MySQL alias |
| `CapabilityTable.cs` | `Resolve(NodeKind,context)` | `AbstractDMLQuery.nativeSupportReturning` and native server references |
| `Lowering.cs` / `MariaDbLowering` | `Lower`, `LowerNullSort`, `ValidateAssignments`, `ValidateConflict`, `ValidateReturning` | `SortFieldImpl.accept`, `InsertQueryImpl.accept1` |
| `MariaDbWriter.cs` | `WriteSelect`, `WriteSet`, `WriteDml`, `WriteCte`, `WriteSort` | `SelectQueryImpl.toSQLReference0`, `unionParenthesis`, `CommonTableExpressionImpl.accept` |
| `TypeNames.cs`, `MariaDbLiteralWriter.cs` | `WriteType`, `Write` | `DefaultBinding` MariaDB branches; driver conversion is separate |
| `MariaDbNestedWriter.cs` | `WriteOrderedMultiset`, `WriteByteGuard` | `Multiset.acceptDefaultJSONEmulation`, `JSONArrayAgg.accept0`; replace the session-setting GROUP_CONCAT workaround with the validated rule below |
| Test files | `ReturningTests`, `AssignmentTests`, `ConflictTests`, `ModeTests`, `NestedBudgetTests`, `ParameterLayoutTests`, `UnsupportedTests` | Every source-derived branch has a local positive/negative fixture |

## Fixed profile and native inventory

`Create` uses family MariaDb, [11.8.0,11.9.0), named parameters,
`max_parameters=65535`, utf8mb4 connection text, `time_zone=+00:00` for instant values, NO_BACKSLASH_ESCAPES,
ONLY_FULL_GROUP_BY and STRICT_TRANS_TABLES required. HIGH_NOT_PRECEDENCE and EMPTY_STRING_IS_NULL are required off. SIMULTANEOUS_ASSIGNMENT and
Oracle compatibility mode are not enabled by this profile. The driver verifies
settings; neither the pure renderer nor execution quietly changes them.
`lower_case_table_names` is an explicit observed profile setting. Pure rendering
requires no live server.

| Family | 11.8 rule |
| --- | --- |
| Joins | INNER/LEFT/RIGHT/CROSS native; FULL and explicit SQL LATERAL derived joins rejected |
| CTEs | Ordinary/recursive SELECT CTEs; explicit MATERIALIZED/NOT MATERIALIZED rejected; top-level WITH before UPDATE/DELETE is rejected in 11.8 |
| Set operations | UNION/INTERSECT/EXCEPT, DISTINCT/ALL, with explicit child grouping preserved |
| Windows | Registered ROWS/RANGE functions; GROUPS/EXCLUDE and JSON_ARRAYAGG as a window function rejected |
| Returning | Native INSERT RETURNING and single-table DELETE RETURNING; UPDATE RETURNING and multi-table DELETE RETURNING rejected |
| Conflict | Explicit AnyUniqueKeyUpdate only; native VALUES(column) refers to inserted values |
| JSON | Text representation with JSON functions; JSON_ARRAYAGG supports ORDER BY and is constrained by group_concat_max_len |
| Locking/other | FOR UPDATE or LOCK IN SHARE MODE, Wait only and empty OF list; explicit wait modifiers, QUALIFY, DISTINCT ON and MERGE rejected |
| Comparison | `<=>` for null-safe equality, NOT around it for distinctness; explicit NULL ordering via safe discriminator lowering |

The documentation for newer MariaDB releases is not a feature flag for 11.8.
In particular, newer UPDATE RETURNING and WITH-DML forms remain unsupported here.
Catalog JSON identity is preserved by the metadata adapter; JSON text storage does
not imply it has MySQL binary JSON's operator/storage behavior.

## Algorithm and SQL policy

The exact public entry points, lock subset and relational frame/materialization
policies are fixed in ORM-QUERY/ORM-RELATIONAL. Numeric widening uses SIGNED and
DOUBLE. Explicit int16/int32 casts use SIGNED plus the closed checked read
conversion IDs in ORM-EXPRESSIONS; ordinary result readers remain strict.

Quote identifier segments with backticks and double embedded backticks. After
common Ordinal alias validation, reject ASCII-case-equivalent result aliases.
Relation aliases use exact comparison for lower_case_table_names=0 and ASCII-case
folding for 1/2; report collisions as KORM-SCOPE-002. Preserve quoted catalog
spelling; no current-culture normalization is permitted. Under
required NO_BACKSLASH_ESCAPES, explicit text literals double apostrophes; reject
literal U+0000 and preserve bound NUL as data. Binary literals use `X'hex'`.
Boolean expressions use TRUE/FALSE as applicable. Every final parameter occurrence
is `@p0`, `@p1`, ... and gets a physical parameter, even when its logical slot
already appeared. Count after lowering, before freezing the template.

Use native LIMIT/OFFSET; offset-only emits the fixed
`LIMIT 18446744073709551615 OFFSET @pN`. Casts use a MariaDB-specific closed name
table, not MySQL's `CAST(... AS JSON)`: JSON text passes through the appropriate
JSON function when semantic validation is required. PG array/domain/range/enum
identities require explicit supported transport declarations and are not renamed
TEXT to hide a missing capability.

For explicit NULLS FIRST emit `(expr IS NOT NULL) ASC, expr DIR`; for NULLS LAST
emit `(expr IS NULL) ASC, expr DIR`. Admit duplication only for stable expressions
as defined in ORM-MYSQL-DIALECT. An existing projected alias may avoid re-evaluation;
otherwise fail `KORM-DIALECT-006`. Parameters duplicated by this lowering remain
separate occurrences. Volatile functions must never be evaluated twice silently.

Shared DML assignment meaning is old-row simultaneous evaluation. Apply the exact
ORM-MYSQL-DIALECT cross-dependency check: RHS of target x may read x and unwritten
columns, but reading another assigned target y fails `KORM-DIALECT-007`. The
baseline does not depend on MariaDB's optional SIMULTANEOUS_ASSIGNMENT mode.

### Duplicate key and RETURNING

Admit only explicit AnyUniqueKeyUpdate. Emit `ON DUPLICATE KEY UPDATE` and use
`VALUES(` + quoted column + `)` for the Excluded node. MySQL's row alias after
VALUES is not emitted by this profile. Column-target/index-predicate/constraint
intent, DO NOTHING and an update WHERE are rejected with `KORM-DIALECT-004`;
INSERT IGNORE and no-op updates are not semantic substitutes. Apply the old-row
cross-assignment check to references to the existing row.

INSERT RETURNING projects accepted expressions in caller order with quoted
aliases; DELETE RETURNING is single-target only. The result uses the ordinary
strict generated row mapping path. UPDATE RETURNING fails before command creation;
no fallback SELECT is appended. DELETE with joins/USING and RETURNING fails even
if a superficially similar SQL string parses on another server version. Affected
rows and returned rows retain their native distinct meanings.

### Ordered nested collections and truncation guard

The exact projection/decoder wire grammar is owned by ORM-NESTED. MariaDB uses
native `JSON_ARRAYAGG(JSON_ARRAY(cells...) ORDER BY keys...)`, not jOOQ's automatic
session-setting GROUP_CONCAT workaround. It must include that packet's checked
single-statement byte guard using the actual `@@group_concat_max_len` and configured
nested budget. No implicit SET, warning-only acceptance, silent truncation or empty
array replacement on aggregate failure is allowed. If the guard fails, emit the
reserved JSON error envelope and let the generated decoder throw
`KORM-NESTED-005`. Empty input follows the separate empty-collection branch.

This is essential even when truncated output happens to be syntactically valid
JSON: valid JSON does not prove that every row/value survived. The guard uses a
conservative UTF-8 byte upper bound, validated with exact boundary and Unicode
fixtures. The maximum nested bytes is a render/shape constant included in the
template fingerprint; it is not a new request argument or a session mutation.

## Required concrete fixtures

Use bigint primary ID, utf8mb4 name, nullable score, unique email, with the same
three initial users as the other dialects. Snapshot complete SQL plus ordered
layout/result columns; only structural aliases may differ from the Java oracle.

| ID | Expected behavior |
| --- | --- |
| `maria-repeat` | Reusing one Int64 logical slot in two predicates emits @p0/@p1, both type/identity-equal, with two physical parameters |
| `maria-null-order` | `` ORDER BY (`u`.`score` IS NULL) ASC, `u`.`score` ASC, `u`.`id` ASC `` returns IDs 1,3,2 |
| `maria-upsert` | `` INSERT INTO `users` (`id`, `name`, `score`, `email`) VALUES (@p0, @p1, @p2, @p3) ON DUPLICATE KEY UPDATE `name` = VALUES(`name`) `` preserves the declared any-key behavior |
| `maria-insert-return` | `` INSERT INTO `users` (`id`, `name`, `score`, `email`) VALUES (@p0, @p1, @p2, @p3) RETURNING `id` AS `Id`, `name` AS `Name` `` returns exactly the projection order |
| `maria-delete-return` | `` DELETE FROM `users` WHERE `id` = @p0 RETURNING `id` AS `Id` `` returns the deleted ID; zero matches yields an empty result |
| `maria-return-negative` | UPDATE RETURNING and multi-table DELETE RETURNING fail `KORM-DIALECT-005` before emitting a template |
| `maria-cte-negative` | WITH ... UPDATE/DELETE and requested MATERIALIZED fail `KORM-DIALECT-001`; an ordinary SELECT CTE succeeds |
| `maria-cross-assignment` | `a=b,b=a` and `a=1,b=a+1` fail `KORM-DIALECT-007`; `a=a+1` succeeds |
| `maria-json-order` | Ordered duplicates/nulls produce `[[1,"a",null],[1,"a",null],[3,"z",30]]`; empty child input produces `[]` |
| `maria-json-limit` | Set an intentionally tiny session group_concat_max_len in test setup; guard produces the reserved error envelope, decoder raises `KORM-NESTED-005`; no truncated value is returned |
| `maria-budget` | 65,536 final placeholder occurrences fail `KORM-DIALECT-002` |

Codes `KORM-DIALECT-001` through `-006` use the exact templates in
ORM-POSTGRES-DIALECT; `-007` uses the exact assignment message in ORM-MYSQL-DIALECT.
SQL NULL, JSON literal null, JSON string "null", absent outer row and empty
collection are separate assertions, not one nullable-object test.

## Acceptance and handoff

Pass pure snapshots/diagnostics, eligible pinned jOOQ differential fixtures and a
Native AOT renderer consumer that references no driver. Real MariaDB tests must
be a separate server lane with exact build/mode records, including conflict on
multiple unique keys, INSERT/DELETE RETURNING, affected counts and nested byte
boundaries. The research MariaDB 11.8.10 fixture verified ordered duplicate/null
JSON and exposed actual truncation at a small limit; the future product guard
and full shape decoder still require their implementation tests.

Provide capabilities, mode requirements, guarded nested SQL and diagnostic fixtures
to RENDER, DML, RELATIONAL, NESTED and MYSQL-DRIVER. No extra provider must be built
for pure checks. Stop at the reviewed task PR; this plan does not authorize product
implementation, publication, merge, legacy changes or a new execution engine.

Primary references: [MariaDB statement reference](https://mariadb.com/docs/server/reference/sql-statements),
[UPDATE evaluation and versioned CTE syntax](https://mariadb.com/docs/server/reference/sql-statements/data-manipulation/changing-deleting-data/update),
[JSON_ARRAYAGG order and byte limit](https://mariadb.com/docs/server/reference/sql-functions/aggregate-functions/json_arrayagg),
[INSERT RETURNING](https://mariadb.com/docs/server/reference/sql-statements/data-manipulation/inserting-loading-data/insertreturning),
[DELETE](https://mariadb.com/docs/server/reference/sql-statements/data-manipulation/changing-deleting-data/delete).

## Exact local runner contract

This task owns `tests/Orm/Dialects/MariaDb/verify.py`,
`tests/Orm/Dialects/MariaDb/Korda.Orm.Dialects.MariaDb.Tests.csproj` and its Program/fixture files.
The CI command, from repository root with no additional flags, is:

```sh
python3 tests/Orm/Dialects/MariaDb/verify.py
```

The runner compiles the packet's positive/negative declaration cases, publishes
its actual consumer with `dotnet publish tests/Orm/Dialects/MariaDb/Korda.Orm.Dialects.MariaDb.Tests.csproj -c Release -r linux-x64 -p:PublishAot=true`,
then executes that native consumer and asserts RuntimeFeature.IsDynamicCodeSupported
is false. Use the repository's pinned SDK/restore settings; place outputs under
artifacts, never beside source. Run this packet's enumerated pure fixtures and
report individual case failures with nonzero exit. The runner does not start a
database, accept an absent peer as a passing stub, or claim live SQL correctness.
Real four-server rows, faults and SQL execution remain ORM-INTEGRATION's gate.
