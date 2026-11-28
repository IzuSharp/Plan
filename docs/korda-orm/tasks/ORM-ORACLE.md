# ORM-ORACLE: Maintain source-linked SQL semantic cases and the jOOQ oracle

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Build the reusable conformance corpus independently of the renderer implementation.
Make source-derived SQL semantics and intentional Korda differences reviewable;
do not equate SQL string snapshots with database correctness.

## Design and source inputs

Use pinned Design `validation.md`, `language-model.md`, `dialects-and-generation.md`
and `upstream-policy.md`; contracts ORM-C01, ORM-C02, ORM-C03 and ORM-C06. Start from
the fixed jOOQ release/symbol mappings, not an assumed private upstream test suite.

## Start and acceptance dependencies

Start: ORM-FOUNDATION. Acceptance: ORM-FOUNDATION. The harness can generate and
validate upstream/reference cases before Korda modules exist. Korda comparison
results remain unexecuted until ORM-INTEGRATION runs the real implementations.

## Scope and ownership

Own `tests/Orm/Conformance/` and `eng/orm-oracle/`, including authored fixtures,
case schema and disposable Java oracle runner. No changes to language/renderer
implementations, unrelated providers or shared CI dispatch. Submit a registration
proposal to ORM-CI. Temporary oracle outputs stay outside tracked source.

## Implementation requirements

Define cases with typed operands, relation scopes, semantic expectation, fixed
upstream symbol, dialect/version, parameter order/types and expected result shape.
Cover NULL/3VL/rows, alias shadowing, nested sets/CTEs, windows, DML conflicts and
RETURNING, list arity, quoting, JSON/arrays and nested-presence semantics as each
family is introduced. Include illegal/unsupported cases and deliberate strict
rejections where upstream omits a clause or performs execution work.

Normalize formatting and declared placeholder syntax only. Preserve ordering,
NULL, coercion and cardinality distinctions. Keep database fixtures and dialect
profiles independent. Provide an offline normal test path using maintained small
expectations; explicit oracle regeneration may require Java and upstream artifacts,
which ordinary C# consumers do not need. Honor source licenses for reused cases.

## Validation and acceptance

Demonstrate positive and intentionally perturbed cases: wrong occurrence order,
wrong NULL result, missing clause and changed projection must fail. Run the Java
runner on pinned artifacts and real SQLite for a representative subset. The case
format and its C# consumer must compile for Native AOT; it cannot deserialize
unknown CLR types by reflection. Native Korda differential results belong to the
later integration gate and cannot be marked passed by fixture validation alone.

## Integration and stop

Deliver stable case IDs/schema and an adapter contract usable by each dialect and
provider worker. Record unavailable upstream coverage and outstanding database
cells. Stop after corpus/harness review; do not implement a renderer to make a
case pass or launch an unbounded benchmark campaign.
