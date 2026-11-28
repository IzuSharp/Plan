# ORM-FOUNDATION: Compile shared contracts and establish isolated module ownership

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Establish the minimal compiled contract surface and project ownership that lets
independent language, dialect, generator and execution work start concurrently.
Do not implement a complete DSL or require providers to finish first.

## Design and source inputs

Use the immutable Design revision in `implementation-graph.json`, especially
`architecture.md`, `contracts.md` ORM-C01 through ORM-C06, and the source-mapping
tables in `language-model.md`, `dialects-and-generation.md` and `execution-aot.md`.
Read current product AGENTS, CONTRIBUTING and module registration guidance.

## Start and acceptance dependencies

Start: user acceptance of the Design/Plan revisions and a separate authorization
to modify Korda. There are no historical R/D/A/B prerequisites. Acceptance: the
shared contracts compile, the proposed graph/ownership matches those contracts,
and independent owners can build against the published contract snapshot.

## Scope and ownership

Own `src/Orm/Contracts/`, `tests/Orm/Contracts/`, the new solution entries and one
initial `eng/ci/modules/orm.json` registration. Coordinate root build-file changes
with the CI owner. Preserve existing product modules and packages. No provider,
business DSL or native-engine replacement is in this task.

## Implementation requirements

Freeze exact names/signatures for SQL type descriptors, query handles, profiles,
value-free rendered templates, typed occurrences/result descriptors, bound
invocations, schema snapshots and generated/manual binder/projector contracts.
Resolve list arity, explicit literal cache identity, typed argument supersets and
connection ownership. Keep test doubles behind the same contracts. Do not publish
dummy successful execution as a usable product implementation.

Pin stable SDK/language versions; define nullable, AOT/trimming and API/XML rules.
Maintain a small source-provenance ledger for adapted symbols. Assign shared
registry/API-baseline responsibility and separate per-module worktrees. Version
contract changes before dependent owners adopt them.

## Validation and acceptance

Compile positive and negative consumer examples for all shared generic boundaries.
Run a pure native consumer with no drivers, runtime reflection or code generation.
Validate that forbidden driver/generator/hosting references cannot enter the pure
contract projects. Check the actual committed diff selects only registered new
modules and true consumers; a prose change must not build products. Acceptance
does not claim any SQL family or database behavior is implemented.

## Integration and stop

Publish one reviewed contract commit and ownership map for the independent task
worktrees. Record actual validation and any remaining restrictions in Plan. Stop
after this task's review boundary; do not start other tasks or merge without the
authorization governing the implementation session.
