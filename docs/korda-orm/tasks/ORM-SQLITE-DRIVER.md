# ORM-SQLITE-DRIVER — Microsoft.Data.Sqlite execution and schema adapter

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Implement SQLite execution and schema acquisition through Microsoft.Data.Sqlite
while preserving the independent DSL and honest SQLite capability boundaries.

## Design and source inputs

Use the batch's pinned Korda-Design `contracts.md` (ORM-C01, ORM-C03–ORM-C06),
`execution-aot.md` and `dialects-and-generation.md`. Read Microsoft.Data.Sqlite
11.0.0 in EF Core commit `9e685c7a52d1a344d133a3d370e458db97417b3f`, especially
`SqliteCommand`, `SqliteParameter`, `SqliteDataReader` and packaging dependencies.
This adapter uses the ADO.NET provider, not the EF Core ORM.

## Start and acceptance dependencies

Start after `ORM-FOUNDATION` against command/schema fixtures. Acceptance requires
`ORM-EXECUTION`, `ORM-SCHEMA` and `ORM-ADVANCED-TYPES`. Basic scalar work can be
verified before neutral advanced contracts are implemented; final declared codec
cells use those real contracts. Work independently of PostgreSQL/MySQL drivers
and complete SQL DSL feature delivery.

## Scope and ownership

Own `src/Orm/Drivers/Sqlite/**`, `src/Orm/SchemaAdapters/Sqlite/**`,
`tests/Orm/Drivers/Sqlite/**` and `tests/Orm/SchemaAdapters/Sqlite/**`.
Do not edit other providers, shared renderer semantics, package assembly or old
sqlite3/C++ modules. Required shared changes go to the contract owner.

## Implementation requirements

Bind the declared parameter layout and implement explicit SQLite storage conversion
policies for common CLR types. Preserve typed NULLs and reject unsupported output
directions, narrowing or missing mappings. Describe async APIs as potentially
synchronous: this driver checks cancellation before execution, while `Cancel()`
does not interrupt a native step. Honor pre-cancel and documented application
boundaries without hidden `Task.Run`, worker pools or false interruption guarantees.
Implement connection/transaction ownership, disposal, busy/timeout error propagation
and schema extraction with keys, nullability and declared type information.
Use the mature package's native dependencies; do not create a new native executor.
Own SQLite storage/transport codecs for the declared advanced representations.
Preserve SQL NULL versus JSON null and declared conversion facets. Reject
unavailable representations explicitly; neutral codec availability does not imply
SQLite has a corresponding native SQL type.

## Validation and acceptance

Publish and run a Linux x64 Native AOT consumer with the pinned provider. Exercise
fixed/dynamic SQL, NULLs, parameters, required-result mismatch, rollback, savepoints,
early disposal and connection reuse. Test documented cancellation limits and
busy/timeout behavior explicitly. Round-trip date/time, decimal, GUID and boolean
storage policies rather than assuming `DbType` enforces conversion. Acquire and
reconsume schema fixtures. Verify every declared advanced storage codec through
real SQLite Native AOT round trips and negative cases after contract integration;
never infer those results from basic scalar tests. Check native asset loading through an independent
consumer in the later packaging integration; this packet supplies its fixtures.
Register SQLite paths and real dependencies without selecting unrelated providers.

## Integration and stop

Deliver the adapter, schema fixtures and provider capability statement. Stop at
acceptance. Do not change SQLite scheduling to imitate network-driver async I/O,
publish packages or delete the old product implementation.
