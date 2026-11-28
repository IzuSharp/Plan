# DB-Rename-01 — retained naming plan

This historical task defines the naming change and review criteria; it is not
current authorization to modify the product or publish a package.

Rename the ten database attributes to `DbTableAttribute`, `DbColumnAttribute`, `DbKeyAttribute`, `DbVersionAttribute`, `DbIgnoreAttribute`, `DbProjectionAttribute`, `DbConstructorAttribute`, `DbParameterAttribute`, `DbCodecAttribute` and `DbUseCodecAttribute`. Tutorials and business code use the short forms, for example `[DbTable]` and `[DbProjection]`. The Design [naming contract](https://github.com/IzuSharp/Korda-Design/blob/main/docs/database/db-attribute-names.md) owns the complete upgrade mapping and explicit source/binary compatibility break.

Preserve existing `Korda.Data` namespaces, constructor parameters/defaults, attribute targets and behavior. Assembly `[DbCodec]` remains general conversion registration; `[DbUseCodec]` remains selection. JSON keeps existing source-generated metadata. C++20/libpq/sqlite3 execution, native ABI and stored database identifiers are unchanged. Other current public names follow responsibilities; future `[QmlProperty]` and `[AgentTool]` are naming examples only.

## Implementation and documentation

1. Inventory content with `git grep -in weave` and filenames with `git ls-files | rg -i weave`.
2. Update declarations, Roslyn semantic matching, generated and reverse-generated C#, diagnostics, compiled API/XML baselines, tests and samples together.
3. Update maintained repository/package README files, tutorials, API references, XML comments, source examples, filenames, links and anchors. Generate reference output from its source. Keep Korda's root contribution naming rule and short AGENTS link.
4. Synchronize current Design and Plan guidance. Preserve upgrade mappings, real repository URLs, immutable accepted snapshots and physical `_nativeweave_migration_phases` hits, and classify them in PR descriptions.
5. Review the diff, inspect committed module selection and run the required local checks before pushing.

## Acceptance evidence

The product PR must identify the tested source commit/tree, actual commands and exit results. Required observations are:

- New attributes generate compilable entities and immutable DTOs; reverse scaffolding produces compilable attributed entities.
- Original ambiguity, invalid mapping/codec and other retained negative fixtures give the expected diagnostics.
- Both actual `Korda.Database.Sqlite` and `Korda.Database.PostgreSql` candidate packages run the existing order sample through source-tree-external PackageReference projects as Linux x64 Native AOT executables against real databases, including reads and writes.
- Candidate DLL/XML/README contents expose all ten new declarations, contain no old public attribute types, and support tutorial source compilation.
- Final tracked content/filename scans explain every remaining old-name category.
- Current PR checks pass after any failures in this change are corrected.

Use each provider's independent package runner. Follow current Korda AGENTS for dependency-selected checks and avoid JIT consumer execution, clean-image/CPU-emulation or unrelated performance/platform campaigns. A document gate proves no compiler, database or AOT execution. Never replace unperformed local results with historical CI evidence.


The original delivery boundary was reviewed PRs, then maintainer review without
automatic merge/publication. Later tasks have separate authority and results.
