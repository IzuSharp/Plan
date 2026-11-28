# ORM-POSTGRES-DRIVER — Npgsql execution and schema adapter

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Connect the independent command boundary to Npgsql and acquire PostgreSQL schema
metadata without introducing provider dependencies into the DSL or schema model.

## Design and source inputs

Use the batch's pinned Korda-Design `contracts.md` (ORM-C01, ORM-C03–ORM-C06),
`execution-aot.md` and `dialects-and-generation.md`. Read Npgsql 11.0.0 at
`4d174200ed48e3e3ab16419dbf84dd655da59de6`, especially `NpgsqlCommand.ProcessRawQuery`,
`NpgsqlParameter<T>`, `NpgsqlSlimDataSourceBuilder` and its native-consumer example.

## Start and acceptance dependencies

Start after `ORM-FOUNDATION`, using command and schema fixtures. Acceptance requires
`ORM-EXECUTION`, `ORM-SCHEMA` and `ORM-ADVANCED-TYPES`. Basic scalar paths can be
implemented and verified earlier; final declared advanced transport cells use the
accepted neutral codec contracts. Other providers remain independent.

## Scope and ownership

Own `src/Orm/Drivers/PostgreSql/**`,
`src/Orm/SchemaAdapters/PostgreSql/**` and corresponding tests under
`tests/Orm/Drivers/PostgreSql/**` and `tests/Orm/SchemaAdapters/PostgreSql/**`.
Do not edit renderer semantics, shared contracts, other drivers, package assembly
or old native database modules.

## Implementation requirements

Bind native positional parameters in layout order, retain SQL NULL/type identity,
and use typed values where Npgsql supports them. Reuse Npgsql's data source,
pooling, preparation and I/O; do not add connection or worker pools. Define caller
ownership, same-connection transactions, streaming disposal and cancellation/error
classification. Detect mismatched dialect profiles before execution. Schema
acquisition preserves qualified names, SQL types, nullability, keys and relevant
version/capability metadata without leaking Npgsql classes into its output.
Keep annotated dynamic JSON, arbitrary composites, unmapped types and tuple-record
mapping outside the default AOT profile. Own the PostgreSQL transport/read codecs
for each declared advanced representation, including safe static registrations.
The neutral advanced-types module does not implement these provider codecs.
Reject any unavailable mapping explicitly rather than enabling a dynamic fallback.

## Validation and acceptance

Run a native Linux x64 consumer against a declared PostgreSQL version. Verify
parameters including typed NULL and repeated slots, result types, rollback,
savepoints, timeout, pre-cancel/in-flight cancel and early stream break. Verify
reader/command cleanup and subsequent connection reuse. Round-trip a schema fixture
and reject unsupported type metadata explicitly. Run real PostgreSQL Native AOT
round trips and negative cases for every declared advanced codec after its neutral
contract is integrated; basic scalar success does not accept those cells.
Compare a small identical query
with direct Npgsql as a correctness/control path; do not claim performance parity.
Register only PostgreSQL source, tests and true shared dependencies in product CI.

## Integration and stop

Provide fixtures to generation, advanced types and later package consumption.
Stop after adapter acceptance. Package assembly/publication, advanced composites,
cross-provider validation and old-engine removal are separate tasks.
