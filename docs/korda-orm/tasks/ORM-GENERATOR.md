# ORM-GENERATOR — typed binding and result generation

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Generate AOT-visible binders, result projectors and typed schema declarations from
deterministic metadata and accessible C# declarations. Keep compiler generation
independent of live database access and keep runtime DSL use independent of the
generator.

## Design and source inputs

Use the batch's pinned Korda-Design `contracts.md` (ORM-C01, ORM-C03–ORM-C06),
`execution-aot.md`, and `dialects-and-generation.md`. Review Dapper.AOT's pinned `ParamPlan`,
`RowPlan`, generator `WriteArgs`/`WriteTokenizeMethod` and nonconstant-SQL fixtures.
Reuse its two-phase materialization insight without relying on Dapper interception
to recognize Korda methods.

## Start and acceptance dependencies

Start after `ORM-FOUNDATION` provides contract fixtures. Generate against those
fixtures in parallel with schema and execution. Acceptance requires `ORM-TYPES`,
`ORM-SCHEMA` and `ORM-EXECUTION`; it does not require every SQL feature or provider.

## Scope and ownership

Own `src/Orm/Generation/**` and `tests/Orm/Generation/**`. Read schema metadata;
do not own database acquisition adapters, runtime type definitions, root module
registration or package assembly. Coordinate any shared contract change.

## Implementation requirements

Use an incremental, equatable generation model; do not retain Roslyn symbols in
long-lived output models. Emit direct constructor/member access and explicit
typed conversion calls. Support known DTO/record and parameter shapes and stable
diagnostics for inaccessible types, ambiguous aliases, missing required members,
NULL mismatch and unsupported construction. Validate actual reader shape before
reading rows. Distinguish dynamic SQL text from runtime-selected CLR types. Refuse
unsupported generation visibly; never fall back to object reflection or emitted IL.
Keep handwritten typed declarations and explicit projectors available. Schema
inputs are deterministic files or declarations, not network requests during build.

## Validation and acceptance

Compile generated outputs, not only snapshot strings. Cover incremental rebuild
stability, deterministic output, changed schema shape and diagnostics. Publish and
execute Native AOT consumers with dynamic optional predicates and static DTOs;
include deliberate missing-mapper and wrong-type failures. Check trimming and
dynamic-code warnings without blanket suppressions. Measure representative
generated code/binary size as shape count grows. Register generator dependencies
so changes select actual consumers without rebuilding unrelated providers.

## Integration and stop

Integrate metadata and execution contracts, then give provider and nested-result
tasks compilable generated fixtures. Stop when the declared generation surface and
negative diagnostics are accepted. Do not add a general reflection mapper, database
migration system or product cutover.
