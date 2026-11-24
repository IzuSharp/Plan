# DB-Rename-01 — Linux x64 plan

## Scope and exact starting points

| Repository | Observed `main` |
| --- | --- |
| Korda | `ea72031db6f9111a31c6f743b5babc345f96862d` |
| NativeWeave-Design | `fcc2b3599066a467ce3d8bf52e4753bdeea6cd86` |
| Plan | `85f7f83e29e67f6865c14c64585139541b8a1a1f` |

All work uses `task/DB-Rename-01-linux` and task-marked worktrees. Resume existing branches, commits and PRs after interruption. The completed DB-API-01 graph entry and its evidence remain unchanged under `completed_executions`; this task does not reuse that acceptance for changed bytes.

Rename the ten database attributes to `DbTableAttribute`, `DbColumnAttribute`, `DbKeyAttribute`, `DbVersionAttribute`, `DbIgnoreAttribute`, `DbProjectionAttribute`, `DbConstructorAttribute`, `DbParameterAttribute`, `DbCodecAttribute` and `DbUseCodecAttribute`. Tutorials and business code use the short forms, for example `[DbTable]` and `[DbProjection]`. The Design [naming contract](https://github.com/IzuSharp/NativeWeave-Design/blob/task/DB-Rename-01-linux/docs/database/db-attribute-names.md) owns the complete upgrade mapping and explicit source/binary compatibility break.

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

## Delivery boundary

Push each reviewed branch, open a product PR and the needed companion PRs, and include a before/after annotation example, compatibility explanation, remaining-hit classification and actual results. Observe current PR CI. Stop awaiting maintainer review after a Chinese brief. **No merge, auto-merge or public package release is authorized by this task.**
