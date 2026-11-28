# ORM-EXPRESSIONS: Typed expressions, predicates and SQL truth semantics

Status: `planned_candidate` / implementation not authorized.

## Objective

Implement the composable expression families that carry jOOQ's SQL semantics
into C#, including SQL three-valued logic and aggregate/window expression shape.

## Design and source inputs

Use the exact Design revision bound by `../implementation-graph.json`, ORM-C01,
ORM-C02 and ORM-C06, and `language-model.md`. Fixed jOOQ 3.21.10 commit
`3c58109e7ab69772de75e640852935ee7e284177` anchors include `AbstractField`,
`AbstractCondition`, `Eq`, `And`, `IsDistinctFrom`, `Cast`, `Coerce`, `Row2`,
`RowIsNull` and `RowIsNotNull`. Advanced operation sources are enumerated in
`dialects-and-generation.md`; inspect their actual public bodies before porting.

## Start and acceptance dependencies

Start after accepted `ORM-FOUNDATION` contracts and separate implementation
authorization. Acceptance depends on `ORM-TYPES`. Query, DML and renderer work may
proceed in parallel using the common expression fixtures; no completed renderer
is required to build and test expression semantics.

## Scope and ownership

Own `src/Orm/Expressions/**` and `tests/Orm/Expressions/**`. Own scalar, predicate,
row, aggregate and window-function expression nodes; the relational task owns
named-window/query-clause coordination. Send registration proposals to the CI
owner. Do not edit shared type definitions, dialect implementations, driver code
or legacy Fluent code.

## Implementation requirements

- Preserve comparison, boolean composition, CASE, arithmetic/string operations,
  explicit SQL casts, membership and row expressions. Declare supported families
  and semantic preconditions rather than accepting operations through raw text.
- Keep `.Eq(NULL)`, `.IsNull()` and null-safe distinctness different. Represent
  UNKNOWN without CLR short-circuit evaluation or accidental boolean conversion.
- Preserve typed operands, result SQL type/nullability, aggregate FILTER and
  window-function descriptors. Reject invalid operand/type combinations and frame
  relationships at the documented compile-time or semantic-validation boundary.
- Retain expression sharing; transformations produce replacement nodes. Do not
  implement a second renderer or silently simplify nullable expressions using
  ordinary two-valued boolean algebra.
- Treat volatile functions and parameter occurrence multiplicity as semantic
  constraints on later lowering; identify operations requiring database validation.

## Validation and acceptance

Cover all true/false/unknown combinations; nullable IN/NOT IN and empty lists;
mixed-null rows; numeric/temporal casts; aggregation over empty inputs; window
frame constraints; and incompatible expression types. Supply source-linked SQL
cases to the jOOQ/real-database integration harness; model acceptance does not
claim that an unavailable renderer has passed them. Run a
driver-free Native AOT consumer, negative compilation cases, bounded allocation/
binary-size checks and affected public API validation. No renderer string match
alone proves the SQL truth-table contract.

## Integration and stop

Deliver operation descriptors and positive/negative fixtures to query, relational
and renderer owners. Reconcile accepted types without changing shared contracts
unilaterally. Submit the authorized PR and stop; do not merge, execute another
task, publish packages or modify the legacy implementation.
