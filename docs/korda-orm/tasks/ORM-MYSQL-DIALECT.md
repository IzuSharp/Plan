# ORM-MYSQL-DIALECT — MySQL SQL profile

Status: `planned_candidate`; product implementation is **not authorized**.

## Objective

Implement a distinct MySQL 8.4 rendering profile with explicit SQL modes and
capability outcomes. This optional provider track can proceed independently of
PostgreSQL and SQLite implementation.

## Design and source inputs

Read Design `docs/korda-orm/contracts.md` and `dialects-and-generation.md` at the
immutable handoff revision; consume ORM-C01, ORM-C02, ORM-C03, and ORM-C06.
Inspect jOOQ 3.21.10 commit `3c58109e7ab69772de75e640852935ee7e284177`,
`InsertQueryImpl.accept1`, `SortFieldImpl.accept`, `SelectQueryImpl`, and
`AbstractDMLQuery.toSQLReturning`. Consult the
[MySQL 8.4 statement reference](https://dev.mysql.com/doc/refman/8.4/en/sql-statements.html)
for version-specific syntax and SQL mode effects.

## Start and acceptance dependencies

Start: `ORM-FOUNDATION`. Acceptance: `ORM-RENDER`. Develop against stable contracts
and fixtures; do not wait for another provider's execution adapter. Additional
language-family acceptance remains with each node owner and final integration.

## Scope and ownership

Own `src/Orm/Dialects/MySql/` and matching tests. Do not reference MySqlConnector
or mutate its connections. MariaDB-specific behavior has a separate owner.
Shared helpers require an agreed contract and owner, not cross-editing sibling
folders. Submit module registration proposals to the CI owner.

## Implementation requirements

Implement names, parameters, supported joins/windows/CTEs/set operations, and
explicit duplicate-key behavior. Preserve null-safe comparison and NULL-ordering
emulation. Account for newer alias-based excluded-value syntax rather than
blindly emitting deprecated VALUES references. Do not translate a conflict-target
policy into an all-unique-keys policy without proof. Reject arbitrary RETURNING
and explicitly requested unsupported materialization hints; these must not vanish
from output. Keep generated-key retrieval outside the pure renderer.

## Validation and acceptance

Run disconnected Java-reference and contract cases for quoting, repeated binds,
NULLs, nested sets, conflict keys, conditional updates, and profile-specific
failures. Test SQL modes that affect admitted semantics, or reject unsupported
mode combinations. A Native AOT renderer consumer must have no driver dependency.
Supply real-server fixtures for independent MySQL integration, including multiple
unique keys and affected-row behavior; label unexecuted fixtures honestly. Measure
bounded rendering allocations only when comparing a concrete implementation choice.

## Integration and stop

Deliver the feature inventory and SQL/result-layout expectations to the MySQL
driver owner. Ensure MySQL-only paths do not select unrelated provider checks.
Stop at the reviewed task PR; no connection protocol, global scheduler, legacy
replacement, publication, merge, or unrequested cross-provider edits.
