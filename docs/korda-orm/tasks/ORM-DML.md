# ORM-DML: Typed mutation semantics and returning projections

Status: `planned_candidate` / implementation not authorized.

## Objective

Implement INSERT, UPDATE, DELETE, upsert intent and RETURNING as typed SQL models,
with explicit capability requirements and no hidden execution strategy.

## Design and source inputs

Use the exact Design revision bound by `../implementation-graph.json`, ORM-C01
through ORM-C03, and the source maps in `language-model.md` and
`dialects-and-generation.md`. Inspect jOOQ 3.21.10 commit
`3c58109e7ab69772de75e640852935ee7e284177`, especially `InsertQueryImpl`,
`UpdateQueryImpl`, `DeleteQueryImpl`, `AbstractDMLQuery`, assignment and conflict
handling. Public source availability is governed by `upstream-policy.md`.

## Start and acceptance dependencies

Start after accepted `ORM-FOUNDATION` contracts and separate product implementation
authorization. Acceptance depends on `ORM-QUERY`. Begin model and diagnostic work
against accepted relation/projection contracts while query implementation proceeds.
The renderer/provider tasks remain independent consumers of this task's fixtures.

## Scope and ownership

Own `src/Orm/Dml/**` and `tests/Orm/Dml/**`. Do not own dialect SQL lowering,
driver execution, transaction creation or query-model shared files. Supply module
registration proposals to the foundation/CI owner. Leave all legacy code intact.

## Implementation requirements

- Model assignment type checking, multirow VALUES, INSERT SELECT, default values,
  update predicates, deletion targets and typed returning projections. Distinguish
  an omitted/default column from a supplied SQL NULL.
- Make the conflict target, key metadata and update action explicit. A missing key
  needed for an emulation is a diagnostic, never an invented identifier or a
  silently omitted clause. Preserve multi-column key order and predicate scope.
- Describe required dialect capabilities through ORM-C02. PostgreSQL, SQLite,
  MySQL and MariaDB may implement different upsert/RETURNING behavior; do not
  relabel one engine's behavior as another's or make a same-driver assumption.
- Keep one SQL command's semantic boundary. Any emulation requiring additional
  statements or transactional guarantees must be explicitly specified and gated;
  this task cannot hide it inside the DSL or choose its own scheduler.
- Preserve result shape, parameter slot identity and occurrence requirements when
  mutation expressions are reused. Separate affected-row counts from returned rows.

## Validation and acceptance

Cover wrong assignment types, duplicate/missing target columns, mixed defaults and
NULLs, INSERT SELECT shape mismatches, compound conflict keys, unsupported actions
and RETURNING projections. Run model/diagnostic tests without a database and
compile/run native consumers. Supply dialect-specific semantic fixtures for real
database integration, including conflict and affected-row behavior; do not accept
string plausibility as correctness. Check bounded construction allocations,
published API impact and module routing. No driver is required for model tests.

## Integration and stop

Integrate accepted query/result descriptors; deliver DML capability fixtures to
each renderer and provider owner. Resolve scoped integration failures and submit
the authorized PR. Stop without merging, starting another task, publishing
packages or deleting/replacing the existing product.
