# ORM-SCHEMA-TOOL — Explicit local schema acquisition workflow

Status: `planned_candidate`; product implementation is **not authorized**.

## Objective

Provide a local tool that explicitly acquires database metadata or reads a
maintained offline snapshot and produces deterministic schema inputs. Ordinary
builds and Roslyn generators must not connect to databases.

## Design and source inputs

Read Design `docs/korda-orm/contracts.md` and `dialects-and-generation.md` at the
immutable handoff revision; consume ORM-C05 and ORM-C06. Inspect jOOQ 3.21.10
commit `3c58109e7ab69772de75e640852935ee7e284177`,
`GenerationTool.run0`, `JavaGenerator.generate0`, and `DDLDatabase.export/load`.
The last path executes parsed SQL and is not an offline-schema-parser template.

## Start and acceptance dependencies

Start: `ORM-FOUNDATION`. Acceptance: `ORM-SCHEMA`, `ORM-POSTGRES-DRIVER`,
`ORM-SQLITE-DRIVER`, and `ORM-MYSQL-DRIVER`. Develop CLI, offline conversion,
diagnostics, and fixture adapters immediately after the contracts. Final
acquisition acceptance uses each driver's maintained metadata adapter. Generators
can independently consume fixtures and do not wait for this tool.

## Scope and ownership

Own `src/Orm/SchemaTool/` and matching tests. Driver tasks own their catalog queries
and provider metadata adapters; this tool orchestrates them. Do not put tool
dependencies into the runtime DSL, perform database migrations, or modify shared
CI registration directly. Consumer snapshots are maintained project inputs, not
raw dumps for the Design/Plan repositories.

## Implementation requirements

Support explicit connection/profile selection, include/exclude scope, naming and
type overrides, diagnostics, deterministic output, and offline input validation.
Read credentials through an intentional local configuration mechanism; never
write them to snapshots or logs. Open and dispose acquisition resources with
clear cancellation/failure behavior. Reject unknown types without a declared
mapping. Preserve composite-key order, generated columns, enums/domains, SQLite
identity distinctions, and MySQL/MariaDB profile differences. Tool execution must
be opt-in and must not silently change a live database.

## Validation and acceptance

Test offline fixtures, idempotent output, exclusions, naming collisions, stale
formats, cancellation, unreachable servers, missing permissions, and redaction.
Run the tool against each accepted provider profile and compile its outputs into
a Native AOT consumer without any subsequent database access during generation.
Validate the tool's own declared deployment/AOT policy explicitly. Use bounded
large-schema tests; database lanes and tool tests remain independently selected.

## Integration and stop

Document the local acquire-review-build-publish-run sequence and hand inputs to
the generator owner. Stop at the reviewed task PR; no CI-only workflow, hidden
build-time network access, migration engine, legacy deletion, publication, or merge.
