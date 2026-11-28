# ORM-SQLITE-DIALECT — SQLite SQL profile

Status: `planned_candidate`; product implementation is **not authorized**.

## Objective

Implement the SQLite profile, initially validating runtime libraries at version
3.45 or later with exact build information recorded. Keep capabilities explicit
and rendering independent of SQLitePCLRaw or Microsoft.Data.Sqlite.

## Design and source inputs

Read Design `docs/korda-orm/contracts.md` and `dialects-and-generation.md` at the
immutable revision in the batch handoff; consume ORM-C01, ORM-C02, ORM-C03, and
ORM-C06. Inspect jOOQ 3.21.10 commit
`3c58109e7ab69772de75e640852935ee7e284177`, `SelectQueryImpl.unionParenthesis`,
`InsertQueryImpl`, `CommonTableExpressionImpl`, `JSONArray`, and
`AbstractDMLQuery.nativeSupportReturning`. Check the SQLite references for
[RETURNING](https://www.sqlite.org/lang_returning.html) and
[limits](https://www.sqlite.org/limits.html).

## Start and acceptance dependencies

Start: `ORM-FOUNDATION`. Acceptance: `ORM-RENDER`. Profile fixtures and supported
node handlers can develop alongside shared rendering; later SQL-family tasks
integrate additional nodes without requiring changes to execution scheduling.

## Scope and ownership

Own `src/Orm/Dialects/Sqlite/` and matching tests. Native-library selection,
connections, transactions, and result codecs belong to the SQLite-driver task.
Propose shared-contract/CI registrations through their designated owners.

## Implementation requirements

Implement structured names, parameter occurrence layout, supported expression
semantics, native RETURNING, and explicit conflict clauses. Preserve nested set
operation precedence using valid derived tables when parentheses alone are
invalid. Record parameter limits and optional engine features in the profile.
Distinguish SQL NULL, JSON null, SQLite affinity, and declared type intent.
Reject unsupported syntax or facets rather than dropping them. RETURNING must
not promise trigger-modified values, row order, composability as a DML CTE, or
bounded engine buffering that SQLite does not guarantee.

## Validation and acceptance

Use pure rendering and Java-reference cases for nested UNION/EXCEPT, recursive
CTE, window frames, NULL ordering, quotes, repeated parameters, and explicit
MATERIALIZED support. Negative cases include unsupported nodes, excessive
parameters, malformed conflict keys, and invalid RETURNING contexts. Publish and
run a Native AOT renderer without a driver. Supply real SQLite fixtures for the
driver/integration lane, recording its exact library and compile options before
claiming server correctness. Keep benchmarks bounded and outside ordinary CI.

## Integration and stop

Deliver capability/profile metadata and semantic fixtures to the SQLite-driver
and advanced-query owners. Pure checks remain service-free and independently
selected. Stop at the reviewed task PR; do not modify PostgreSQL/MySQL code,
replace legacy packages, merge, or expand into a performance campaign.
