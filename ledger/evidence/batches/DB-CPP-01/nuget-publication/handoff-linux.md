# DB-CPP-01 — authorized NuGet publication follow-up

## Current state: reviewed publication PR; live preflight passed; public delivery pending

The C++ migration is already delivered and accepted. Product PR21 merged as `3badc05be503991b5591732629dd7e5b0dbad111`; the final migration evidence PR27 merged into Plan as `5be447a868be78713ada52f46cee16409f0edc13`, with its own PR and merged-main CI successful. This follow-up does not reopen implementation or transfer a local candidate result into a public-release claim.

The owner subsequently authorized publishing the required database packages to their existing NuGet account `dekueon` and removing the retired `NativeWeave.HelloWorld` listing. They clarified that the destination must be their actual NuGet account, that their CI/trusted publisher is already configured, and that a browser sign-in is unnecessary. The existing publisher matches repository `IzuSharp/NativeWeave`, workflow `release.yml` and environment `nuget`. No new account, credential, scope or publisher policy is created here.

NativeWeave remains one database product with PostgreSQL and SQLite providers. The twelve package IDs are the already accepted dependency closure, not twelve databases or new products. Ordinary consumers install the selected provider entry package; NuGet restores its required components. Package consolidation would change the frozen package contract and is not part of this publication.

## Frozen publication input

| Input | Exact identity |
| --- | --- |
| Product source | `3badc05be503991b5591732629dd7e5b0dbad111` |
| Source tree | `3264de79b73c8a89f1cac1eff57d0c0ff2c841c2` |
| Successful main build | [CI44977773509](https://github.com/IzuSharp/NativeWeave/actions/runs/44977773509), attempt 1 |
| Candidate artifact | `14738115742`, `nativeweave-database-linux-44977773509-1` |
| Archive | 6,169,499 bytes; SHA-256 `bb63f9fe71ea4c2f68dd63b748af3820c8bc0174199ce6fa7e2a92197f31e8b9` |
| Selected root | `db-scope/prepared/candidate`, excluding the separate `.clean.*` test closure |
| Provider versions | `NativeWeave.Database.Sqlite` and `NativeWeave.Database.PostgreSql` at `0.1.0-db-cpp.1.2` |
| Shared versions | The seven accepted common packages at `0.1.0-db-cpp.1.1`; all exact edges preserved |

The source package and native bytes were verified in the completed migration. This follow-up promotes those same original archives. NuGet repository signing is verified separately because it changes the outer ZIP. Original local-only build records remain unchanged.

## Preparation and observations

- The current product main had no `release.yml`; DB-Scope-01 removed the old HelloWorld publisher. Existing build CI therefore produced verified artifacts without uploading the database packages to NuGet.org.
- Public NuGet registration currently has ten HelloWorld versions, all `listed: true`. The SQLite provider flat-container endpoint currently returns 404. These are pre-publication observations, not final results.
- Product changes restore a database-only trusted-publisher workflow, an immutable release manifest, strict registry promotion/readback, and an independent source-external public-feed consumer. They do not rebuild or alter accepted native assets, modify the old acceptance verifier, or expand product scope.
- The independent consumer will use the existing versioned C# sample, NuGet.org as the only source, empty caches, actual SQLite/PostgreSQL JIT/AOT runs and native load hashes. Current local tools do not include .NET/Clang; execution must be observed in the official release run, not claimed from unit tests.
- HelloWorld withdrawal is a separate receipt. NuGet delete means unlist, preserving exact-version restore. Actual existing-key authorization is checked normally; an unlist refusal will remain an explicit incomplete result even if database uploads succeed.

## Worktrees and next actions

Worktrees remain `ROOT/.worktree/DB-CPP-01-linux/{NativeWeave,Plan}` on `task/DB-CPP-01-linux`, fast-forwarded to their current merged mains. The old orphan worktree/tool cleanup was completed in the migration closeout; current verified archives are retained for this authorized promotion.

The publication source is now reviewed in [product PR23](https://github.com/IzuSharp/NativeWeave/pull/23), head `4349b4998bed0724d277bb14857c72756fe3a624`, tree `b43259a919e2e9de789dc851fb32502bc7271d71`. This is byte-identical to the locally reviewed commit `762fe8bf6915271244792e9bff69939767e00229`; only the Git commit metadata differs. The [independent review](reviews/publication-source-review.json) covers all ten changed files and independently reruns the 18 publisher and 9 consumer refusal controls. Root separately checked the final file hashes and GitHub tree.

[PR publication preflight44994423577](https://github.com/IzuSharp/NativeWeave/actions/runs/44994423577), job `137122267455`, passed. Its actual log reports `Existing NuGet publication switch: true`, both test groups successful, and successful live GitHub/original-archive/package checks. The credential-bearing publisher is correctly skipped for a pull request. This is not a public-release result. Required [product CI44994423565](https://github.com/IzuSharp/NativeWeave/actions/runs/44994423565) is still running at this checkpoint.

Next: observe every required PR check, merge normally, observe the real NuGet publication and all four public-consumer cells, verify all HelloWorld versions are unlisted, then commit actual public receipts, PR/run links and the final publication result. Any missing operation or failed test remains incomplete. DB-API-01 and DB-Perf-01 remain excluded.
