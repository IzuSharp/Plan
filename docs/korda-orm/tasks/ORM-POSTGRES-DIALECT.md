# ORM-POSTGRES-DIALECT — PostgreSQL SQL profile

Status: `planned_candidate`; product implementation is **not authorized**.

## Objective

Implement the PostgreSQL 18 validation profile and its pure rendering/lowering
rules. Database availability must not be a prerequisite for generating SQL.

## Design and source inputs

Use the immutable Design revision recorded in the batch handoff:
`docs/korda-orm/contracts.md`, `language-model.md`, and
`dialects-and-generation.md`; consume ORM-C01, ORM-C02, ORM-C03, and ORM-C06.
Inspect jOOQ 3.21.10 commit `3c58109e7ab69772de75e640852935ee7e284177`,
`SelectQueryImpl`, `InsertQueryImpl.accept1`, `AbstractDMLQuery.toSQLReturning`,
`CommonTableExpressionImpl`, and PostgreSQL type implementations. Use the
[PostgreSQL 18 SQL reference](https://www.postgresql.org/docs/18/sql.html) for
server semantics; commercial jOOQ transformation gaps are not available code.

## Start and acceptance dependencies

Start: `ORM-FOUNDATION`. Acceptance: `ORM-RENDER`. Develop profile tables and
contract fixtures while rendering is implemented. Advanced feature owners later
integrate their node families against this profile.

## Scope and ownership

Own `src/Orm/Dialects/PostgreSql/` and matching tests. Do not add Npgsql or
connection ownership here. Changes to shared nodes and registry entries go to
their owners; PostgreSQL execution and codecs belong to the driver task.

## Implementation requirements

Implement quoting/qualification, explicit positional parameter layout, casts,
pagination, native NULL ordering, supported CTE/windows/set operations, explicit
ON CONFLICT intent, and native RETURNING for accepted nodes. Preserve PostgreSQL
type identity for JSON/JSONB, arrays, enums, domains, and temporal facets without
referencing driver classes. Mark unimplemented feature families unsupported.
Reject ambiguous conflict keys, invalid scope/arity, and unavailable transforms.
Do not imply all newer PostgreSQL features are covered by the 18 profile.

## Validation and acceptance

Run driver-free rendering/diagnostic cases and eligible Java jOOQ differential
cases. Include repeated parameters, NULL semantics, self-join aliases, CTE scope,
set precedence, conflict targets and predicates, and RETURNING projection order.
Add compile-negative typed examples and a Native AOT renderer consumer. Publish
server-side semantic fixtures for the independent PostgreSQL integration lane;
do not claim them executed without that run. Measure only a bounded representative
render case, with SQL/parameter shape fixed, if implementation choices need evidence.

## Integration and stop

Provide the explicit supported-feature inventory and integration fixtures to the
query-family and PostgreSQL-driver owners. Ensure pure tests select no database
service. Stop at the reviewed task PR; no driver implementation, old-code deletion,
publication, merge, or unrelated provider changes.
