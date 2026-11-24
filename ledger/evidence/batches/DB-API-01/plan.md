# DB-API-01 — C# Fluent ORM experience, Linux x64

## Outcome and fixed inputs

Start from the observed main commits in [baseline.json](baseline.json). Korda supplies independent Native AOT NuGet providers for PostgreSQL and SQLite. Enhance the existing database ORM only: C# owns business models, DTOs and Fluent syntax; the existing C++20 kernel, libpq and sqlite3 own query semantics, dialects and execution. Extend the versioned C ABI compatibly only where an observed gap requires it. Do not repeat the completed native migration, replace the query engine or add a LINQ provider.

The owner authorizes source and documentation changes, local and normal CI execution, pushes, PRs, protected normal merges and inspection of this batch's triggered publications. Korda AGENTS.md and the committed module registry are authoritative for checks and release behavior. This batch has no blanket requirement for JIT consumers, clean images, minimum-CPU emulation, Windows/macOS acceptance, a benchmark campaign or a server product.

## Ordering and progress

1. **Baseline — complete:** actual remote main inputs read; requested task branches and handoff were absent; fresh task worktrees created without clearing prior work.
2. **Plan first — complete:** published checkpoint `21e98f7591b4cf1f7fd5b7d5e791ab0be4271515` before the Design overlay and product changes.
3. **Design contract — complete:** published additive checkpoint `3b270347d37f2bef0e6e5c6baefc9235e39bf7c2`, with its own gate, Plan-first pin and unchanged historical validation. Implementation acceptance remains separate.
4. **Implementation — complete:** both existing samples were compared; existing optional filters, joins, aggregate, keyed CRUD and checked writes are retained. Generated DTO/codec policy, complete cursors, bounded batches, callbacks and schema workflows are implemented, with API/XML inventories, English guides and registered checks.
5. **AOT consumers — complete:** independent external PackageReference consumers passed against real PostgreSQL and SQLite as Linux x64 Native AOT. Scaffold/original/edited phases checked business results, compiled reverse mappings, exactly two page/detail SQL dispatches and unchanged native payloads after the DTO edit.
6. **Review and merge — complete:** scoped non-author reviews and normal required checks are recorded. Korda PR35, original Design PR16 plus documentation erratum PR17, and Plan PR29 merged normally with their tested trees unchanged. Historical authoring review and fresh post-merge review keep their actual timing.
7. **Main and release — complete:** every delivered main run passed. Both Korda.Database.PostgreSql and Korda.Database.Sqlite 0.1.0-preview.2 were verified from the signed NuGet registry and passed public-feed Native AOT consumption, including all three ORM phases. This evidence-only closeout checks its own subsequent CI separately.

[acceptance.json](acceptance.json) records all seventeen passed delivered-source claims. [Observed delivery](results/observed-delivery.json) binds actual commits, trees, CI, artifacts and publication, and [review followup](results/review-followup.json) records exact review scopes and corrections. A document gate does not perform product execution. The closeout record does not predict its own future CI.

## Business comparison before additions

Use a customer, order and order-line model, a narrow immutable order-list DTO and an order-with-lines result. The implementation audit must show the existing call, desired complete call, precise missing behavior, owning module and acceptance oracle for each item below. Existing behavior should be reused and demonstrated rather than replaced. The comparison is now captured in Korda `docs/guides/orm-experience.md` and the executable `samples/api/orm-experience/` sources; the final source-bound execution results are recorded in [observed delivery](results/observed-delivery.json).

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

## Evidence and CI selection

Every executed claim records the exact source commit/tree, command, result and output digest or observed GitHub URL. Keep failed attempts with their source identity; a later pass does not erase them. Check module routing using `python3 eng/ci/impact.py origin/main` after committing source. Register new module paths, edges, checks and outputs; changes inside existing registered roots need no duplicate module. Run required checks once, independently in parallel where applicable. API signatures/XML and packed binaries follow Korda's changed-module selection.

Each provider package has its own producer/consumer runner. Consumer projects live outside the source tree and reference only their requested top-level provider using PackageReference, with an isolated restore cache and exact version. Their real business assertions cover the table above. Record loaded native assets and package hashes before and after a DTO-only edit; reusing a differently built native binary is not the same-native proof. Run the published AOT executable directly.

Main compares every registered package with last published inputs and chooses exact next previews. Observe that plan, verified artifacts and the trusted release job. If policy disables publication or no package is changed, record the observed skip and reason; never claim a release or change publication configuration just to make a result green. Do not bypass required checks or impersonate an approval identity.

## History and resume

Preserve accepted DB-CPP-01, DB-Scope-01, 34R/32D/48-task records, original hashes and raw evidence. New contracts are additive current overlays, not edits to accepted historical meaning. Run the original completed C++ gate at the frozen Plan baseline and retain every previously configured historical check. A new gate validates links, phase dependencies and source-bound claims, with negative controls for premature or malformed acceptance.

Resume from the actual PR heads and [handoff-linux.md](handoff-linux.md); do not restart completed work or overwrite evidence. An evidence-only closeout records delivered PR/main identities and checks its own subsequent CI separately, avoiding claims about its own future commit.
