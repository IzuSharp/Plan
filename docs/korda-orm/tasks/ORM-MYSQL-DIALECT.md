# ORM-MYSQL-DIALECT — MySQL SQL profile

Status: `planned_candidate`; product implementation is **not authorized**.

## Objective, inputs and dependencies

Implement the distinct MySQL 8.4 profile using Design `implementation-spec.md`,
`contracts.md` and `dialects-and-generation.md` at the batch's immutable revision;
consume ORM-C01, ORM-C02, ORM-C03 and ORM-C06. This track develops independently of
PostgreSQL/SQLite but is **mandatory in the final four-profile acceptance matrix**.
Start: `ORM-FOUNDATION`; acceptance: `ORM-RENDER`, `ORM-ADVANCED-TYPES` and `ORM-NESTED`. Do not infer MariaDB semantics
from the fact that both profiles use MySqlConnector in the provider layer.

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

## Source inheritance and owned files

Pin jOOQ public source 3.21.10 commit
`3c58109e7ab69772de75e640852935ee7e284177`. Source paths below are under
`jOOQ/src/main/java/org/jooq/impl/`. Adapt public algorithm bodies with notices and
source/test manifest entries; unsupported/commercial transformation bodies are not
available implementation code.

| Source symbol | Fixed use in this task |
| --- | --- |
| `InsertQueryImpl.accept1` | Distinguish native duplicate-key intent from explicit target ON CONFLICT; preserve MySQL row-alias spelling |
| `SortFieldImpl.accept`, `acceptFieldAndOrder` | Null discriminator then original sort expression, subject to the evaluation-safety precondition below |
| `SelectQueryImpl.toSQLReference0`, `unionParenthesis` | Correct clause/set grouping and local pagination |
| `AbstractDMLQuery.nativeSupportReturning`, `toSQLReturning` | Keep unsupported RETURNING distinct from JDBC generated-key fallback; this renderer rejects it |
| `JSONArrayAgg.accept0`, `groupConcatEmulation`; `ListAgg.accept` | Source evidence for JSON/order behavior and session-setting hazards; do not copy automatic group_concat_max_len SET statements |

Own `src/Orm/Dialects/MySql/` and `tests/Orm/Dialects/MySql/`. Required files:
`Profile.cs` (`MySqlProfile.Create`), `CapabilityTable.cs` (`Resolve`),
`Lowering.cs` (`MySqlLowering.Lower`, `LowerNullSort`, `ValidateAssignments`,
`ValidateConflict`), `TypeNames.cs` (`WriteType`), `MySqlWriter.cs`
(`WriteSelect`, `WriteSet`, `WriteInsert`, `WriteUpdate`, `WriteDelete`,
`WriteSort`), `MySqlLiteralWriter.cs` (`Write`) and `MySqlNestedWriter.cs`
(`WriteOrderedMultiset`, per ORM-NESTED). Tests: `ModeTests`, `ConflictTests`,
`NullOrderTests`, `AssignmentTests`, `SetAndWindowTests`, `ParameterLayoutTests`,
`NestedSqlTests` and `UnsupportedTests`.

## Profile settings and capability decisions

`Create` returns family MySql, minimum 8.4.0, maximum exclusive 8.5.0, named
placeholders and `max_parameters=65535`. Settings fix `character_set_connection`
to utf8mb4, `time_zone=+00:00` for the instant codec contract, `NO_BACKSLASH_ESCAPES=on`, `ONLY_FULL_GROUP_BY=on`,
`STRICT_TRANS_TABLES=on`, `HIGH_NOT_PRECEDENCE=off`, and `lower_case_table_names` to an explicit observed
value 0, 1 or 2. The renderer quotes identifiers and does not rely on ANSI_QUOTES
or PIPES_AS_CONCAT. The driver verifies required modes when opening/borrowing the
session; it does not silently issue mode-changing SQL. A caller can configure
its own connection before creating the session. Case-sensitive relation identity
remains the schema/metadata resolver's responsibility; do not use universal
OrdinalIgnoreCase for catalog names.

| Family | Fixed 8.4 support |
| --- | --- |
| Joins | INNER/LEFT/RIGHT/CROSS and declared LATERAL derived relations; FULL rejected |
| Sets | UNION, INTERSECT, EXCEPT, each DISTINCT/ALL; preserve explicit tree grouping |
| CTEs | SELECT/recursive SELECT and accepted read-only WITH preceding supported SELECT/UPDATE/DELETE; materialization hints rejected |
| Windows | Registered ROWS/RANGE functions; GROUPS, EXCLUDE, unsupported IGNORE NULLS and QUALIFY rejected |
| DML | Single-target INSERT/UPDATE/DELETE and explicit AnyUniqueKeyUpdate; no RETURNING and no implicit generated-key SELECT |
| Comparison | `IS NOT DISTINCT FROM` -> `<=>`; `IS DISTINCT FROM` -> `NOT (a <=> b)` |
| Sorting | Explicit NULL order lowered below; plain ordering retains server default |
| Other | DISTINCT ON, MERGE and unknown hints rejected; locking follows ORM-QUERY: UPDATE/SHARE with Wait/NOWAIT/SKIP LOCKED, empty OF list |

The required modes are part of the profile fingerprint and offline fixtures.
Application compatibility with arbitrary mode combinations is not claimed. Read
capabilities separately for statement kind, clause, function and context.

## Fixed rendering and lowering recipe

Run all shared validation and profile checks before publication. Quote each name
segment with backticks; double embedded backticks. A dot inside one segment remains
inside that quoted segment. Every result field has its explicit quoted alias. After the common Ordinal alias
check, reject ASCII-case-equivalent output aliases (Id/id). Relation aliases use
exact comparison when lower_case_table_names=0 and ASCII-insensitive comparison
when it is 1/2; u/U then fails KORM-SCOPE-002 in the latter profiles. Keep quoted
catalog spelling intact and do not use the current culture for normalization.
Text literals double apostrophes under the required NO_BACKSLASH_ESCAPES mode;
backslashes remain ordinary characters. Runtime values, including embedded NUL
and quote/backslash combinations, remain parameters. Explicit literal U+0000 is
rejected. Binary literals use `X'hex'`; Boolean literals use TRUE/FALSE.

Every final parameter appearance calls `NextParameter` and emits `@p0` onward;
layout names omit `@`. Duplicate logical slots produce distinct physical
parameters referring to the same immutable typed value. Limit the final count to
65,535. LIMIT and OFFSET values are Int32 parameters in their final occurrence
order. Offset-only emits `LIMIT 18446744073709551615 OFFSET @pN`; the fixed unsigned
sentinel is syntax, not a user value. LIMIT 0 is not rewritten to unlimited.

Casts use a closed type table: signed integer -> SIGNED, unsigned -> UNSIGNED, floating widening -> DOUBLE,
Decimal(p,s) -> DECIMAL(p,s), Text -> CHAR CHARACTER SET utf8mb4, Binary -> BINARY,
JSON -> JSON, date/time/datetime according to the explicit temporal identity.
Never emit unsupported `CAST(... AS BOOLEAN)` or pretend CHAR implies a JSON type.
JSONB/PG arrays/enums/domains are unsupported identities unless an explicit portable
text representation was selected by ADVANCED-TYPES; changing identity is not an
implicit fallback.

### Null ordering — do not re-evaluate volatile expressions

For explicit NULLS FIRST, emit `(expression IS NOT NULL) ASC, expression DIR`;
for NULLS LAST, emit `(expression IS NULL) ASC, expression DIR`. The original
ascending/descending direction applies only to the second key. Constants and
column references are safe. Registered immutable/deterministic scalar expressions
are safe if every child is safe. Parameters are safe but each emitted occurrence
gets a new physical ordinal. Functions marked volatile, sequence operations,
user-defined functions without an explicit stability declaration and subqueries
are unsafe to duplicate.

For an unsafe key, the baseline supports only an already projected unique alias
that can be referenced as the order key without repeating the original expression.
If the surrounding query would require inventing another projection layer to make
that alias valid, fail `KORM-DIALECT-006`. Do not silently reorder evaluation or
hide a new field from DISTINCT/aggregation semantics. A later independent lowering
can widen this boundary only with its own evidence and contract revision.

### UPDATE assignments — shared old-row semantics

The shared DML model defines every RHS against the row before this SET operation.
MySQL evaluates single-table assignments left-to-right. Build the set W of target
column identities; walk every RHS for reads of target columns. If RHS of target x
references y in W with y != x, reject `KORM-DIALECT-007` before rendering. A reference
to x itself is legal, as are references to an unwritten column. Do not reorder
assignments, use temporary variables, add a SELECT, or accept the query depending
on its current values. Tests cover `a=a+1`, `a=b,b=a`, and `a=1,b=a+1`.

### Duplicate-key policy — explicit all-keys meaning

Admit only the DML node `AnyUniqueKeyUpdate(assignments)` for native ON DUPLICATE
KEY UPDATE. A conflict column list, index predicate, constraint name, conditional
update WHERE, or target-specific DO NOTHING fails `KORM-DIALECT-004`. Do not
translate DO NOTHING to INSERT IGNORE or a no-op UPDATE: those change error,
trigger and affected-row semantics.

For VALUES inserts, allocate unique row alias `__korda_new_N`, avoiding the target
and existing aliases. Emit it immediately after the last VALUES tuple and before
ON DUPLICATE KEY UPDATE. Excluded-value nodes emit that alias's quoted field.
Example:

```sql
INSERT INTO `users` (`id`, `name`, `score`, `email`)
VALUES (@p0, @p1, @p2, @p3) AS `__korda_new_0`
ON DUPLICATE KEY UPDATE `name` = `__korda_new_0`.`name`
```
Use this alias syntax, not deprecated VALUES(column). The initial insert-select
upsert subset admits no excluded-value references; those require an explicit,
separately validated derived-source alias lowering and are rejected here.

Apply the same cross-assignment dependency check to duplicate-key assignments
that read the existing target row. References to the new-row alias do not read
previously updated old-row columns. Return native affected-row behavior through
execution metadata; do not normalize counts into “one row changed.”

## Exact fixtures

Use users with bigint primary ID, utf8mb4 name, nullable score and unique email.
Initial rows: `(1,'Ada',10,'a')`, `(2,'Bo',NULL,'b')`, `(3,'Cy',30,'c')`.

| ID | Required SQL/layout/result or failure |
| --- | --- |
| `mysql-repeat` | `` SELECT `u`.`id` AS `Id` FROM `users` AS `u` WHERE (`u`.`score` >= @p0 OR `u`.`id` = @p1) ORDER BY `u`.`id` ASC ``; both occurrences use one logical Int64 slot=2, result IDs 1,2,3 |
| `mysql-null-order` | `` ORDER BY (`u`.`score` IS NULL) ASC, `u`.`score` ASC, `u`.`id` ASC ``; IDs 1,3,2 |
| `mysql-null-safe` | `` `u`.`score` <=> @p0 `` with typed NULL yields only ID2; ordinary `=` yields none |
| `mysql-upsert` | `` INSERT INTO `users` (`id`, `name`, `score`, `email`) VALUES (@p0, @p1, @p2, @p3) AS `__korda_new_0` ON DUPLICATE KEY UPDATE `name` = `__korda_new_0`.`name` ``; explicit AnyUniqueKey intent; preserve score |
| `mysql-secondary-conflict` | An email collision with another ID invokes native any-key behavior; target-ID-only intent is rejected before the database |
| `mysql-cross-assignment` | `a=b,b=a` and `a=1,b=a+1` fail `KORM-DIALECT-007`; `a=a+1,b=5` is admitted |
| `mysql-returning` | INSERT/UPDATE/DELETE RETURNING all fail `KORM-DIALECT-005`, with no extra command emitted |
| `mysql-window-multiset` | ORM-NESTED's ordered window/full-frame scalar lowering yields `[[1,"a",null],[1,"a",null],[3,"z",30]]`; parent with no children yields `[]` |
| `mysql-budget` | Final occurrence count 65,536 fails; application values never become literals to avoid the limit |

Whitespace in authoritative snapshots follows the shared canonical renderer.
The table contains complete SQL strings; create full snapshots, not runtime SQL
fragment concatenation.
Use the common dialect codes `-001` unsupported, `-002` parameter count, `-003`
profile setting, `-004` conflict intent, `-005` returning and `-006` unsafe lowering.
Add exact message `KORM-DIALECT-007: Assignment to '{target}' reads another assigned
column '{source}' under non-simultaneous update semantics.` Report both identities
and the RHS node path; the first such pair in assignment/expression order wins.

## Acceptance and handoff

Pure rendering, negative modes/capabilities, exact SQL/layout/type snapshots and
eligible pinned Java differential fixtures must pass. Run a Native AOT renderer
consumer with no MySqlConnector reference. The MySQL integration lane runs real
mode/secondary-unique/affected-row/null/window tests on the recorded exact 8.4
build. The research MySQL 8.4.11 ordered-window test passed; it is evidence for the
chosen lowering, not acceptance of an unimplemented product writer.

Deliver fixtures and profile requirements to RENDER, DML, RELATIONAL, NESTED and
MYSQL-DRIVER. Pure checks select no server and no MariaDB lane. Stop at the reviewed
task PR; no protocol, scheduler, implicit query, production change, publication,
merge or old-code deletion is authorized here.

Primary references: [8.4 INSERT](https://dev.mysql.com/doc/refman/8.4/en/insert.html),
[duplicate-key behavior](https://dev.mysql.com/doc/refman/8.4/en/insert-on-duplicate.html),
[alias transition](https://dev.mysql.com/worklog/task/?id=13325),
[UPDATE evaluation](https://dev.mysql.com/doc/refman/8.4/en/update.html),
[aggregate/window JSON](https://dev.mysql.com/doc/refman/8.4/en/aggregate-functions.html),
[SQL modes](https://dev.mysql.com/doc/refman/8.4/en/sql-mode.html).

## Exact local runner contract

This task owns `tests/Orm/Dialects/MySql/verify.py`,
`tests/Orm/Dialects/MySql/Korda.Orm.Dialects.MySql.Tests.csproj` and its Program/fixture files.
The CI command, from repository root with no additional flags, is:

```sh
python3 tests/Orm/Dialects/MySql/verify.py
```

The runner compiles the packet's positive/negative declaration cases, publishes
its actual consumer with `dotnet publish tests/Orm/Dialects/MySql/Korda.Orm.Dialects.MySql.Tests.csproj -c Release -r linux-x64 -p:PublishAot=true`,
then executes that native consumer and asserts RuntimeFeature.IsDynamicCodeSupported
is false. Use the repository's pinned SDK/restore settings; place outputs under
artifacts, never beside source. Run this packet's enumerated pure fixtures and
report individual case failures with nonzero exit. The runner does not start a
database, accept an absent peer as a passing stub, or claim live SQL correctness.
Real four-server rows, faults and SQL execution remain ORM-INTEGRATION's gate.
