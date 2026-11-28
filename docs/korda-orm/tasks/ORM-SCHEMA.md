# ORM-SCHEMA — Neutral schema model and deterministic inputs

Status: `planned_candidate`; product implementation is **not authorized**.

## Objective

Implement the neutral, versioned schema representation consumed by handwritten
metadata, acquisition tooling, and generators. The model must be usable without
database drivers and must preserve SQL identity beyond CLR type names.

## Design and source inputs

Read Design `docs/korda-orm/contracts.md`, `language-model.md`, and
`dialects-and-generation.md` at the immutable handoff revision; consume ORM-C01,
ORM-C05, and ORM-C06. Inspect jOOQ 3.21.10 commit
`3c58109e7ab69772de75e640852935ee7e284177`, `jOOQ-meta`'s `Database`, table/column/
key definitions, `PostgresDatabase.getEnums0`, and
`SQLiteTableDefinition.getElements0`. Preserve metadata semantics, not JDBC APIs.

## Start and acceptance dependencies

Start: `ORM-FOUNDATION`. Acceptance: `ORM-TYPES`. Format fixtures, canonicalization,
and diagnostic design can proceed with contract stubs; final model acceptance
uses actual shared SQL types. Neither a working database nor the schema tool is
a startup dependency.

## Scope and ownership

Own `src/Orm/Schema/` and matching tests. ORM-C05 format changes are coordinated
with the shared-contract owner. Driver catalog queries, command-line acquisition,
Roslyn generation, and mapping code have separate owners. Submit CI proposals
for integration instead of editing shared registry files concurrently.

## Implementation requirements

Represent catalog/schema/table identities, column ordinals, SQL type identity and
facets, nullability, defaults/computed expressions, identity semantics, ordered
keys/foreign keys, enums/domains, and profile provenance. Keep secrets and driver
objects out. Preserve unknown types as explicit unresolved/custom-codec demands.
Define deterministic ordering, format-version compatibility, naming overrides,
and reversible C# identifier mapping. Hand-authored descriptors remain supported.
Do not infer identity from database contents or conflate missing/default/NULL.

## Validation and acceptance

Test deterministic serialization round trips, composite-key order, duplicate names,
case/keyword collisions, unknown format versions, unresolved references, SQL type
facets, SQLite affinity/rowid distinctions, and enum ordering. Corrupt or
incompatible snapshots fail with stable diagnostics. Compile and run a Native AOT
consumer reading maintained fixtures without reflection-based type discovery or
driver packages. Assess size/allocation only for representative large-schema
fixtures; no long benchmark belongs in normal CI.

## Integration and stop

Deliver fixture-backed ORM-C05 inputs to generators and schema tooling, allowing
their independent development before database acquisition exists. Stop at the
reviewed task PR; no live schema changes, database migration engine, legacy
deletion, package publication, merge, or unrequested generator implementation.
