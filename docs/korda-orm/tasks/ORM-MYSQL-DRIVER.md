# ORM-MYSQL-DRIVER — MySqlConnector execution and schema adapter

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Provide MySqlConnector-based execution and schema acquisition with distinct MySQL
and MariaDB capability profiles and no duplicated Fluent API.

## Design and source inputs

Use the batch's pinned Korda-Design `contracts.md` (ORM-C01, ORM-C03–ORM-C06),
`execution-aot.md` and `dialects-and-generation.md`. Review MySqlConnector 3.0.0 at
`95875a195369f0dd804f63ded2f95da3fed59ec2`, including `MySqlCommand`,
`MySqlParameter`, the project AOT settings and native-consumer source.

## Start and acceptance dependencies

Start after `ORM-FOUNDATION` publishes fixtures. Acceptance requires
`ORM-EXECUTION`, `ORM-SCHEMA` and `ORM-ADVANCED-TYPES`. Basic scalar work and
server validation can proceed before advanced contracts are implemented; final
declared codec cells consume the accepted neutral contracts. No PostgreSQL or
SQLite task blocks this adapter's development.

## Scope and ownership

Own `src/Orm/Drivers/MySql/**`, `src/Orm/SchemaAdapters/MySql/**`,
`tests/Orm/Drivers/MySql/**` and `tests/Orm/SchemaAdapters/MySql/**`.
The adapter can share transport implementation between MySQL and MariaDB, but
schema/version profiles stay explicit. Do not edit SQL renderers, unrelated drivers,
shared contract definitions, package assembly or historical native modules.

## Implementation requirements

Bind ordered values with explicit provider typing when inference is ambiguous.
Declare decimal, unsigned integer, date/time, zero-date, binary and JSON
representation policies and relevant connection settings. SQL dialect identity
must not be inferred solely from the driver class. Reuse the driver's data source,
pooling, async I/O, preparation and cancellation. Propagate database errors and
preserve safe context. Enforce transaction/connection association and clean up
streams on early exit. Schema acquisition records server family/version, identifiers,
types, nullability, keys and defaults without driver types in the neutral model.
Do not promise no boxing at the driver's object-based parameter boundary.
Own MySQL/MariaDB transport/read codecs for each declared advanced representation;
declare family-specific differences and reject unsupported mappings explicitly.
Neutral advanced-types code remains driver-free and does not supply these codecs.

## Validation and acceptance

Publish/run a native Linux x64 consumer against the declared MySQL and MariaDB
versions independently. Cover NULL/precision/unsigned limits, prepared and ordinary
commands, rollback/savepoints, timeout, pre-cancel/in-flight cancel and stream
disposal. Prove connection reuse after mapped failures. Validate schema fixtures for
both server families, including a deliberately unsupported feature. After neutral
contract integration, validate each declared advanced codec with real Native AOT
round trips and negative cases on its supported server family; scalar success
does not accept advanced mappings. Compare output
with direct MySqlConnector under identical SQL/parameters. Register provider paths,
schema-adapter paths and true dependencies; an isolated MySQL change must not select
PostgreSQL or SQLite checks.

## Integration and stop

Deliver the adapter, fixtures and separate support profiles for advanced type and
package-consumption tasks. Stop after the reviewed scope; do not add a new protocol,
retry engine, global scheduler, package publication or product cutover.
