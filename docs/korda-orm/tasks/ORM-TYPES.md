# ORM-TYPES: SQL types and typed parameter identities

Status: `planned_candidate` / implementation not authorized.

## Objective

Implement the driver-independent SQL type system underlying the jOOQ-derived
C# language model. Preserve SQL distinctions that a CLR `Type` alone cannot express.

## Design and source inputs

Use the exact Design revision bound by `../implementation-graph.json`, especially
ORM-C01 and ORM-C03 in `contracts.md`, and `language-model.md`'s source table.
The jOOQ baseline is 3.21.10, commit
`3c58109e7ab69772de75e640852935ee7e284177`: `DataType`, `DefaultDataType`,
`SQLDataType`, `Nullability`, `Param` and `Val`. Apply `upstream-policy.md`.

## Start and acceptance dependencies

Start after `ORM-FOUNDATION` accepts the shared contracts and separate product
implementation authorization exists. Acceptance depends on `ORM-FOUNDATION`.
Query, expression and renderer developers can proceed against these contracts
while this module is implemented.

## Scope and ownership

Own `src/Orm/Types/**` and `tests/Orm/Types/**`. Provide the agreed module-registration
proposal to the foundation/CI owner. Do not edit shared registry files, driver
adapters, renderers, generators, legacy database code or other owners' modules.

## Implementation requirements

- Implement `SqlType<T>` with canonical SQL identity, domain/element identity,
  applicable length/precision/scale and explicit nullability metadata. Preserve
  JSON/JSONB, timestamp policies and signed/unsigned distinctions.
- Keep `Param<T>` definition identity separate from per-invocation values. SQL NULL
  retains a declared type; names do not replace slot identity or binding order.
- Define checked conversion/promotion and result-nullability rules through ORM-C01.
  Do not treat nullable-reference annotations as runtime NULL validation, or permit
  arbitrary type relabelling to bypass compatibility checks.
- Keep provider codecs, `DbType`/provider enums, reflection registries and connection
  state outside this module. Expose only the stable descriptors consumers need.
- Document immutable ownership and structural identity; do not derive type/cache
  identity from debugging SQL or mutable request values.

## Validation and acceptance

Compile and run a Linux x64 Native AOT consumer without provider assemblies.
Cover SQL types sharing one CLR type, typed NULL, domain incompatibility, array
element mismatches, decimal dimensions and temporal conversion boundaries.
Compile negative generic-type examples and verify diagnostic expectations.
Exercise descriptor equality and concurrent reuse. Record allocation and native
size for a bounded representative type set; do not claim universal zero allocation.
Validate API baselines and the module's registered source/test impact using the
maintained product entry point.

## Integration and stop

Publish the accepted descriptor fixtures and migration notes for parallel owners;
remove development stubs when integrating. Resolve only defects within this task's
scope, submit the authorized PR and stop. Do not merge, execute another task,
publish packages or delete the legacy implementation.
