# ORM-NESTED — nested projections and result materialization

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Implement neutral nested row/collection shapes and static decoders using jOOQ's
semantic model, with AOT-visible result types and bounded, documented materialization.
Actual dialect encodings and provider behavior earn support at integration.

## Design and source inputs

Use the batch's pinned Korda-Design `contracts.md` (ORM-C01, ORM-C03–ORM-C06), `language-model.md`/`dialects-and-generation.md` source maps and `execution-aot.md`. Follow the inspected jOOQ row/multiset/nested
projection semantics, including dialect encodings. Do not infer Dapper.AOT support
from Dapper's multi-mapping APIs: its pinned supported-call surface excludes relevant
overloads and does not supply this complete contract.

## Start and acceptance dependencies

Start after `ORM-FOUNDATION` with nested shape fixtures. Acceptance requires
`ORM-RELATIONAL`, `ORM-ADVANCED-TYPES`, `ORM-GENERATOR` and `ORM-RENDER`.
Develop projection metadata, generator diagnostics and materializer fixtures in
parallel. This node accepts neutral descriptors, static decoders and rendering
contract fixtures; real emitted SQL/provider matrices belong to `ORM-INTEGRATION`
and cannot be marked passed here without an actual run.

## Scope and ownership

Own `src/Orm/Nested/**` and `tests/Orm/Nested/**`. Use declared renderer and
generator extension points; proposals touching shared nodes, factories or schema
models go through their owners. Do not introduce hidden relationship loading,
change tracking, an identity map or implicit follow-up queries.

## Implementation requirements

Specify parent/child cardinality, duplicate preservation, ordering, absent outer-join
rows, SQL NULL, empty collections and nested field nullability. Specify required
encoding semantics and decoder inputs; dialect owners implement actual SQL
lowerings, while provider owners implement transport codecs. Make
collection buffering and ownership visible; a streaming outer sequence does not
guarantee a nested collection is allocation-free or unbuffered. Generate static
DTO/record construction and conversions, rejecting unsupported result types.
Avoid ambiguous alias-based grouping and prohibit arbitrary runtime type discovery.
Enforce the command's result descriptor and capability proof.

## Validation and acceptance

Compare neutral semantic fixtures with the pinned jOOQ behavior. Include
zero/one/many children, duplicates, ordering, nested NULLs, outer-join presence
and correlated-projection descriptors. Compile/run driver-free Native AOT static
decoders/materializers and deliberate invalid shapes using maintained reader/codec
fixtures. Validate owned-result memory bounds and failure cleanup. Supply real SQL,
stream-disposal and per-provider test cases to integration; record those cells as
unexecuted until the actual dialect/driver combination runs. Submit dependency
registration inputs without adding unrelated database requirements to pure checks.

## Integration and stop

Integrate rendering contracts, advanced representations and generated static
decoders into the declared neutral path. Stop at that scoped acceptance; complete
nested-query support requires the separate real-database integration gate. Do not
expand into a full ORM tracking system, implicit N+1 execution, migrations, old-code
deletion or product publication.
