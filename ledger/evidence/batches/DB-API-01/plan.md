# DB-API-01 — plan and recorded outcome

The database-only work preserves the C# Fluent facade, C++20/libpq/sqlite3 execution,
Native AOT and independent PostgreSQL/SQLite packages. The Plan-first checkpoint
was `21e98f7591b4cf1f7fd5b7d5e791ab0be4271515`; design preceded implementation.

## Ordering and progress

1. **Baseline — complete:** actual remote main inputs read; requested task branches and handoff were absent; fresh task worktrees created without clearing prior work.
2. **Plan first — complete:** published checkpoint `21e98f7591b4cf1f7fd5b7d5e791ab0be4271515` before the Design overlay and product changes.
3. **Design contract — complete:** published additive checkpoint `3b270347d37f2bef0e6e5c6baefc9235e39bf7c2`, with its own gate, Plan-first pin and unchanged historical validation. Implementation acceptance remains separate.
4. **Implementation — complete:** both existing samples were compared; existing optional filters, joins, aggregate, keyed CRUD and checked writes are retained. Generated DTO/codec policy, complete cursors, bounded batches, callbacks and schema workflows are implemented, with API/XML inventories, English guides and registered checks.
5. **AOT consumers — complete:** independent external PackageReference consumers passed against real PostgreSQL and SQLite as Linux x64 Native AOT. Scaffold/original/edited phases checked business results, compiled reverse mappings, exactly two page/detail SQL dispatches and unchanged native payloads after the DTO edit.
6. **Review and merge — complete:** scoped non-author reviews and normal required checks are recorded. Korda PR35, original Design PR16 plus documentation erratum PR17, and Plan PR29 merged normally with their tested trees unchanged. Historical authoring review and fresh post-merge review keep their actual timing.
7. **Main and release — complete:** every delivered main run passed. Both Korda.Database.PostgreSql and Korda.Database.Sqlite 0.1.0-preview.2 were verified from the signed NuGet registry and passed public-feed Native AOT consumption, including all three ORM phases. This evidence-only closeout checks its own subsequent CI separately.

## Business comparison before additions

Use a customer, order and order-line model, a narrow immutable order-list DTO and an order-with-lines result. The implementation audit must show the existing call, desired complete call, precise missing behavior, owning module and acceptance oracle for each item below. Existing behavior should be reused and demonstrated rather than replaced. The comparison is now captured in Korda `docs/guides/orm-experience.md` and the executable `samples/api/orm-experience/` sources; the final outcome is summarized above.

| Requirement | Business use and acceptance |
| --- | --- |
| Model conventions | Plain class/record, nullable members and immutable constructor DTO; explicit overrides resolve duplicate names, computed columns and constructor parameters; static ambiguity fails compilation. |
| Reusable values | Declare custom ID, decimal precision and JSON mapping once, then use it in parameters, rows and applicable schema generation without provider-dependent silent conversion. |
| Query composition | Optional customer/status/time filters, order/customer join and totals; project only the needed columns; parameterized SQL can share the same DTO materializer. |
| Cursor and relations | Stable composite ordering with unique tie-breaker, correct next-page bounds and batch loading only for the selected page; empty parent/child sets; actual observed SQL count. |
| Writes | Find by key, selective updates distinguishing omission from SQL NULL, insert-returning result and row-version concurrency conflict. |
| Transactions | Callback returns a value while preserving explicit commit result; cancellation and callback faults roll back where outcome is known; unknown commit remains unknown and is not retried. |
| Adoption | Short provider-specific installation/DI/query/diagnostics tutorial; examples use published API and redact values by default. |
| Schema workflows | Generate a reviewable migration from models and compilable models from an existing table; refuse destructive steps until the developer explicitly selects them. |


## Validation and scope

The recorded external PackageReference consumers ran as Linux x64 Native AOT
against both real providers, including DTO-only edits with unchanged native assets.
Seventeen delivered-source claims were recorded. Korda PR35, Design PR16/17 and
Plan PR29 merged with their tested trees. The two provider packages at
`0.1.0-preview.2` passed signed registry readback and public-feed AOT consumption.

This record accepts its observed scope, not new platform/performance/server work.
Raw execution receipts and copied package outputs are omitted from the current
document tree. Product CI remains owned by Korda; document checks do not repeat it.
