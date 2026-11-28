# ORM-MARIADB-DIALECT — MariaDB SQL profile

Status: `planned_candidate`; product implementation is **not authorized**.

## Objective

Implement the MariaDB 11.8 validation profile as an explicit dialect. Sharing
MySqlConnector does not imply identical MySQL syntax, capabilities, or results.

## Design and source inputs

Read Design `docs/korda-orm/contracts.md` and `dialects-and-generation.md` at the
immutable revision in the handoff; consume ORM-C01, ORM-C02, ORM-C03, and ORM-C06.
Inspect jOOQ 3.21.10 commit `3c58109e7ab69772de75e640852935ee7e284177`,
`InsertQueryImpl`, `SelectQueryImpl`, `SortFieldImpl`, `JSONArray`, and
`AbstractDMLQuery`. Review the [MariaDB statement documentation](https://mariadb.com/docs/server/reference/sql-statements)
for the selected profile. MariaDB 13.0's newer UPDATE RETURNING is not evidence
for 11.8 support.

## Start and acceptance dependencies

Start: `ORM-FOUNDATION`. Acceptance: `ORM-RENDER`. Work from profile fixtures and
the shared renderer contract without a hard dependency on MySQL's dialect task.
Where common helpers are useful, agree them through the shared owner.

## Scope and ownership

Own `src/Orm/Dialects/MariaDb/` and matching tests. Driver execution and metadata
acquisition belong to the MySQL-driver owner. Do not change MySQL's profile,
shared AST definitions, root registration, or public names without coordination.

## Implementation requirements

Implement admitted names, parameters, CTEs, sets, windows, null-safe comparisons,
NULL ordering, and explicit duplicate-key intent. Treat INSERT/DELETE RETURNING
and UPDATE RETURNING as separate capabilities. Reject unsupported update-returning
and multi-table-returning forms for this profile; do not use an extra SELECT
silently. Preserve MariaDB JSON representation/NULL differences and test any
JSON-array lowering independently. Unsupported materialization hints and
commercial-only transformation paths produce explicit diagnostics.

## Validation and acceptance

Run pure rendering/negative cases plus eligible Java-reference cases. Include
named versus positional bind layouts, NULL sorting through NVL2 or an equivalent,
CTE/set nesting, conflicts on multiple keys, unsupported RETURNING forms, and
SQL NULL/JSON null/absent distinctions. Publish and run a driver-free Native AOT
consumer. Provide exact-profile integration fixtures to the shared driver lane;
do not mark those fixtures executed merely because SQL rendering passed. Record
limited allocation evidence only for justified implementation choices.

## Integration and stop

Deliver profile checks and semantic fixtures to the MySQL-driver/integration
owner, retaining a separately selectable MariaDB test lane. Stop at the reviewed
task PR. Do not extend to 13.x, rewrite other dialects, implement a protocol,
replace legacy code, publish, or merge without separate authorization.
