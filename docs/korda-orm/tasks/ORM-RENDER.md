# ORM-RENDER — Pure SQL rendering and capability evaluation

Status: `planned_candidate`; product implementation is **not authorized**.

## Objective

Implement the database-independent rendering pipeline that turns a validated
query and explicit target profile into SQL, typed parameter occurrences, and
result metadata. Keep SQL construction usable without any driver or connection.

## Design and source inputs

Read `docs/korda-orm/contracts.md` and `dialects-and-generation.md` at the immutable
Korda-Design revision recorded in the batch handoff. Consume ORM-C01, ORM-C02,
ORM-C03, and ORM-C06. Inspect jOOQ 3.21.10 commit
`3c58109e7ab69772de75e640852935ee7e284177`, `DefaultRenderContext.visit0/scopeEnd0`,
`Val.accept`, and `ParamCollector.bindInternal`; these separate rendering order
from a simple named-parameter dictionary.

## Start and acceptance dependencies

Start: `ORM-FOUNDATION`. Acceptance: `ORM-TYPES`. Contract stubs and test cases can
be developed concurrently with the type implementation; final acceptance uses
the real shared types.

## Scope and ownership

Own `src/Orm/Rendering/` and matching `tests/Orm/Rendering/`. Dialect folders,
drivers, generators, public shared contracts, and the root CI registry are owned
elsewhere. Submit module registration changes to the CI owner for integration.

## Implementation requirements

Use operation-local contexts and return an owned immutable result. Distinguish
logical slots from emitted occurrences; rewrites may duplicate or reorder them.
Validate profile capabilities before issuing a command. Preserve structured
identifiers, explicit literal policy, SQL type facets, and result column order.
Unknown capabilities and parameter-limit failures produce actionable diagnostics;
no silent clause removal or automatic value inlining. Define bounded cache keys
without caller values, credentials, or connection state. Measure before adding
pooling or a second specialized rendering representation.

## Validation and acceptance

Run pure positive/negative cases for aliases, nested scopes, repeated parameters,
typed NULLs, malformed nodes, missing or invalid parameter descriptors,
unsupported capabilities, and rewrite-introduced occurrences. Verify concurrent renders do not share mutable
state. Publish and run a Native AOT consumer with only language/render modules
and no provider dependency. Record allocations separately for new SQL and cached
shape paths; a small bounded measurement suffices. Inspect dependency metadata
and selected CI checks; a driver change must not be needed to run these tests.

## Integration and stop

Deliver the renderer contract to independent dialect and execution owners. Stop
after this slice's reviewed checks and normal PR; do not implement provider I/O,
change legacy code, merge, or start follow-on tasks without their authorization.
