# ORM-ADVANCED-TYPES — explicit advanced database representations

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Define driver-free advanced SQL value representations and statically reachable
codec contracts. Keep their semantics usable before a provider adapter exists,
without treating a neutral representation as proof of database transport support.

## Design and source inputs

Use the batch's pinned Korda-Design `contracts.md` (ORM-C01, ORM-C03–ORM-C06), `language-model.md`/`dialects-and-generation.md` and `execution-aot.md`. Follow the pinned jOOQ type/JSON/array source
map and provider annotations. Npgsql's `NpgsqlSlimDataSourceBuilder` explicitly
restricts arbitrary composites, dynamic JSON and unmapped types under Native AOT.

## Start and acceptance dependencies

Start after `ORM-FOUNDATION` against type and command fixtures. Acceptance requires
`ORM-EXPRESSIONS` only. Driver codec implementation and real-database gates belong
to the provider tasks and integration; neither this neutral module nor nested
projection development waits for all providers to complete.

## Scope and ownership

Own `src/Orm/AdvancedTypes/**` and `tests/Orm/AdvancedTypes/**`. Consume registered
SQL type and expression contracts; coordinate shared additions with their owners.
Do not reference driver assemblies, implement catalog queries or provider codecs,
rewrite protocols, or silently enable provider dynamic-code features.

## Implementation requirements

For each declared JSON, array, enum, range, temporal or user-defined representation,
define SQL identity, CLR representation, NULL behavior, precision/loss policy and
static conversion/codec requirements. Keep transport binding and provider read
operations behind separate adapter contracts. Support explicit JSON text/bytes and
source-generated `JsonSerializerContext`/`JsonTypeInfo<T>` inputs without runtime
type discovery. Preserve SQL NULL versus JSON null and empty versus NULL
collections. Reject implicit numeric narrowing and timezone changes. Describe
unsupported representations explicitly; driver profiles independently declare
which neutral representations they can actually transport.

## Validation and acceptance

Compile and run driver-free native consumers for the declared representation and
static-codec families. Test deterministic conversions, NULLs, empty values,
numeric/time boundaries, static JSON metadata and missing-codec diagnostics.
Inspect trimming/dynamic-code warnings and verify no provider assembly is required.
Supply per-provider conformance fixtures, but mark transport support unverified
until its driver/integration gate runs real database round trips. Measure only
focused conversion allocation/size where choosing an implementation. Submit module
registration inputs to the shared owner and inspect affected consumer selection.

## Integration and stop

Deliver neutral capabilities and deterministic conversion fixtures to provider,
nested-result and package tasks. Stop at the declared driver-free contract and
representation set. Do not claim provider acceptance, add reflection/native
engines, publish packages or introduce silent fallbacks to broaden coverage.
