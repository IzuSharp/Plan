# ORM-QUERY: Immutable relational queries and typed projections

Status: `planned_candidate` / implementation not authorized.

## Objective

Implement composable SELECT, relation, join, subquery and projection models with
the semantics and ownership established in the jOOQ source study.

## Design and source inputs

Use the exact Design revision bound by `../implementation-graph.json`: ORM-C01,
ORM-C02 and ORM-C03 in `contracts.md`, plus `language-model.md`. Read pinned jOOQ
3.21.10 (`3c58109e7ab69772de75e640852935ee7e284177`) `Field`, `Table`,
`SelectImpl`, `SelectQueryImpl`, `TableAlias`, `FieldAlias` and
`ConditionProviderImpl`; retain the source-to-semantic-case mapping.

## Start and acceptance dependencies

Start after `ORM-FOUNDATION` accepts the shared contracts and separate implementation
authorization exists. Acceptance depends on `ORM-TYPES`. Development can use the
accepted type contract and fixture implementations without waiting for that task's
completion; do not ship competing type definitions.

## Scope and ownership

Own `src/Orm/Query/**` and `tests/Orm/Query/**`. Coordinate with expression and
relational owners through ORM-C01. Propose module registrations to the CI owner;
do not edit shared registrations, renderer files, provider execution, generators,
advanced relational nodes or legacy product code.

## Implementation requirements

- Implement typed fields, relations, SELECT/projection, joins, WHERE, grouping/
  HAVING, ordering and basic paging composition. Keep syntax nodes independent of
  rendering and execution. Advanced CTE/set/window-clause coordination belongs to
  `ORM-RELATIONAL`; scalar/window expressions belong to `ORM-EXPRESSIONS`.
- Make reusable queries immutable. Internal builders must freeze owned collections;
  shared subqueries and aliases cannot acquire another query's mutations.
- Separate relation identity from rendered names. Validate legal scopes and
  correlation; support self-joins and derived tables without accidental capture.
- Derive result descriptors and outer-join nullability without mutating schema
  metadata. Preserve projection ordinal/type information and explicit nested-row
  presence rules. Runtime-shaped projections must state their weaker guarantees.
- Model optional clause absence explicitly. Do not attach connection state,
  execution callbacks or runtime reflection mapping to query nodes.

## Validation and acceptance

Use driver-free semantic fixtures for nested SELECT, correlated and invalid
subqueries, self-joins, duplicate aliases, optional predicates and projection
ordering. Verify independent reuse and simultaneous rendering of query snapshots.
Compile correct and incompatible projection/type examples and run the native
consumer. Supply representative SQL-semantic fixtures to ORM-C06's integrated
conformance harness. This module's acceptance checks model invariants; actual SQL
differential validation belongs to integration once the renderer is available.
Measure bounded construction allocations and AOT size without preselecting pooling.
Confirm module routing and affected public API checks.

## Integration and stop

Deliver immutable query fixtures and result descriptions to renderer, DML and
relational owners. Integrate accepted types, remove stubs and submit the authorized
PR. Stop after scoped checks; do not merge, start another task, publish packages
or modify/delete the legacy implementation.
