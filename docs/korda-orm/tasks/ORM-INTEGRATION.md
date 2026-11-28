# ORM-INTEGRATION: Compose real modules and validate each database profile

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Replace contract doubles with real language/render/generation/execution modules
and validate the composed behavior. Accept profiles independently while maintaining
one explicit final matrix; optional parser work does not block the initial product.

## Design and source inputs

Use all six pinned Design contracts, the language/dialect/execution mappings and
the maintained conformance cases from ORM-ORACLE. Read current module and package
contracts; do not use historical product acceptance as evidence for this stack.

## Start and acceptance dependencies

Start: ORM-FOUNDATION, allowing fixture/interface planning while modules develop.
Acceptance: all mandatory language/type/render/dialect/schema/generator/execution/
driver/advanced/nested tasks, ORM-ORACLE, ORM-CI and ORM-PACKAGE listed in the graph.
PostgreSQL/SQLite submatrices may complete before MySQL/MariaDB; final task
acceptance requires every profile this release claims. ORM-PARSER is optional.

## Scope and ownership

Own `tests/Orm/Integration/` and the integration manifest. Fixes inside leaf modules
are coordinated with their owners; do not casually expand write scopes or overwrite
worktrees. No old-product deletion or application cutover occurs here.

## Implementation requirements

Compose a pure SQL-only consumer, generated and manual metadata consumers,
dynamic/fixed query clients and independently restored provider packages. Check
SQL/layout/result contracts across each boundary, including repeated slot names,
argument supersets, list-arity changes, typed NULL, outer joins and source-linked
unsupported cases. Test advanced types/nested rows only for the declared profiles;
reject unavailable ones without silently dropping requested behavior.

Run real databases with disposable fixtures. Verify transaction ownership and
commit failure semantics, streaming early exit, cancellation before/during work,
timeouts, concurrent reuse of immutable templates and resource release. Apply
each driver's real limitations. Ensure Schema acquisition stays outside Roslyn
and the DSL does not transitively load a driver or native query engine.

## Validation and acceptance

Run native consumers and semantic comparisons for exact documented server/runtime
versions. A successful AOT link alone is insufficient. Compile API/negative examples
and inspect generated binders/projectors, actual parameter metadata and returned
rows/errors. Confirm independent nupkg input/output closure. Publish concise
profile results and remaining unsupported cells; never relabel planned features
as accepted merely to complete the matrix. Controlled performance follows in its
own task; no Dapper parity claim is made here.

## Integration and stop

Provide a content-pinned integrated candidate for performance and independent
acceptance. Resolve cross-module defects with owning tasks and rerun only affected
gates. Stop after the integration review; do not cut over, delete old code or merge
outside the implementation session's explicit authority.
