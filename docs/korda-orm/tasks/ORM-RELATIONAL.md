# ORM-RELATIONAL: CTEs, set operations and window coordination

Status: `planned_candidate` / implementation not authorized.

## Objective

Extend the shared query model with advanced relational structure while retaining
jOOQ's established scoping, row-shape and SQL semantic distinctions.

## Design and source inputs

Use the exact Design revision bound by `../implementation-graph.json`, ORM-C01,
ORM-C02, ORM-C03 and ORM-C06, plus `language-model.md` and
`dialects-and-generation.md`. Inspect jOOQ 3.21.10 commit
`3c58109e7ab69772de75e640852935ee7e284177` `CommonTableExpressionImpl`,
`SelectQueryImpl`, set-operation handling and window specifications. Preserve
source/semantic correspondence without assuming commercial transformation bodies
are present in the public snapshot.

## Start and acceptance dependencies

Start after accepted `ORM-FOUNDATION` contracts and separate product implementation
authorization. Acceptance depends on `ORM-QUERY` and `ORM-EXPRESSIONS`. Develop CTE,
set and named-window nodes concurrently against their accepted shared contracts;
completed renderers or providers are not development prerequisites.

## Scope and ownership

Own `src/Orm/Relational/**` and `tests/Orm/Relational/**`. Own CTE/recursive/set
structure and query-level window coordination. Query owns basic SELECT/join/
projection; expressions owns aggregate/window-function expressions. Propose module
registration to the CI owner. Do not edit those owners' files, dialect renderers,
driver adapters, the shared registry or historical implementation.

## Implementation requirements

- Model CTE declaration/reference identity, explicit output columns and recursive
  anchor/member structure. Validate scope, duplicate names and compatible row
  degrees/types. Document which recursive validity checks require a database.
- Preserve UNION/INTERSECT/EXCEPT and ALL/DISTINCT multiplicity. Keep parentheses,
  local versus final ORDER BY and LIMIT/OFFSET attached to their correct operands.
- Implement named-window declarations and references, inheritance/refinement
  constraints and query-level placement without duplicating expression definitions.
- Carry materialization hints and advanced clause intent as explicit capability
  requirements. Unsupported requested semantics fail; a renderer cannot silently
  discard them. New emulations require stated SQL preconditions and tests.
- Support composable nested relational structure with immutable ownership and
  stable result descriptors. Do not attach a database connection or turn a query
  transformation into an implicit multistatement execution plan.

## Validation and acceptance

Test nested and recursive CTEs, incompatible recursive outputs, duplicate/shadowed
names, set degree/type mismatches, ALL multiplicity, set precedence, operand/global
ordering, named-window references and unsupported materialization intent. Compile
and run driver-free Native AOT consumers plus negative type examples. Supply
jOOQ differential and real-database fixtures for actual semantics, including NULL,
duplicates and recursion termination conditions. Record bounded nested-query
construction allocations and binary size; verify module routing and API impact.

## Integration and stop

Integrate accepted query and expression implementations, remove contract fixtures
used as development substitutes and deliver stable test cases to renderer/provider
owners. Submit the authorized PR after scoped validation and stop. Do not merge,
start another task, publish packages or replace/delete the existing product.
