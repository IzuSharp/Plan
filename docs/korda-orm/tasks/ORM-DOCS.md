# ORM-DOCS — public contracts and compilable local workflows

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Provide an accurate public API reference and usable local workflow for the accepted
Korda.Orm surface, including driver-free SQL construction and optional execution,
generation and schema tooling.

## Design and source inputs

Use the graph-pinned Design `architecture.md`, `contracts.md` ORM-C01–ORM-C06,
language/dialect specifications, `execution-aot.md` and `validation.md`. Validate
examples against the actual reviewed C# API; research sketches and proposed package
names are not installable-product documentation.

## Start and acceptance dependencies

Start after `ORM-FOUNDATION` to prepare documentation structure and explicit example
contracts. Acceptance requires `ORM-QUERY`, `ORM-GENERATOR`, `ORM-EXECUTION` and
all four dialect tasks. Only examples supported by actual available modules can be
marked compiled. Provider/package instructions remain identified drafts until their
modules exist. `ORM-PACKAGE` and final acceptance recheck all public examples
against shipped candidates; this avoids a cyclic docs/package dependency.

## Scope and ownership

Own `docs/orm/**` and `samples/orm/**`. Propose root project/registry inputs to their
owner. Coordinate XML comments and public API corrections with module owners; do
not invent signatures in documentation or change code solely to hide a limitation.

## Implementation requirements

Document namespaces, signatures, nullability, SQL semantics, profile/version support,
capability diagnostics, cancellation, disposal, threading and exception behavior.
Cover pure rendering, typed/dynamic query composition, parameters, projections,
fixed/dynamic execution, streaming, transactions, schema acquisition, offline
generation and Native AOT publishing. Explain SQLite's sync/cancel limits and
advanced driver mapping restrictions. Provide explicit handwritten alternatives
to generation. Show local acquire-review-build-publish-run commands; CI is optional.
Describe package/API compatibility and migration boundaries without claiming the
old architecture has already been removed.

## Validation and acceptance

Compile real samples and run their native outputs where they claim execution.
Classify every sample as compiled/run, compilation-only, illustrative or blocked
with a reason. Verify negative diagnostics and resource cleanup examples. Test
standalone DSL examples without drivers. Cross-check reference pages against
compiled APIs and XML docs, and confirm links/profile claims. Keep provider-specific
examples independently selectable; ordinary prose changes select no product build.
Fake generator output or uncompiled sketches cannot satisfy example acceptance.

## Integration and stop

Hand package/acceptance owners the example matrix and unresolved instructions for
their final archive-based recheck. Stop at the scoped documentation deliverable;
do not mark unavailable provider features complete, publish products, delete old
code, merge or start migration work.
