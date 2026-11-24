# DB-Rename-01 — Linux handoff

Current state: Korda and Design are awaiting maintainer review after successful PR workflows. Plan PR 31 also passed at its preceding evidence commit `87ffe5de4deca258c69a4a600c29b2077bce8aff`. The [PR check checkpoint](pr-checks.json) records those observed identities and conclusions. This final evidence-only Plan update remains subject to its own [current PR checks](https://github.com/IzuSharp/Plan/pull/31); its result is not predicted by this file. No merge or public package publication has occurred as part of this task. The full formatter was blocked locally and subsequently passed unchanged in Korda PR CI.

Read [plan.md](plan.md) for the exact three starting `main` commits and authorization boundary. Work uses `task/DB-Rename-01-linux` and task-marked worktrees. The previous DB-API-01 graph entry and historical evidence remain unchanged and independently verifiable at frozen Plan `85f7f83e29e67f6865c14c64585139541b8a1a1f`.

## Tested source and PR source

| Identity | Observed value |
| --- | --- |
| Locally tested Korda commit | `9aa0b9092c6b2dfc19d5c98d82cb131699171d66` |
| Preserved local branch | `task/DB-Rename-01-linux-local-tested` |
| Korda PR 36 head | `b1e5706a12b7115255f465981ada4bbe839de4f4` |
| Complete tree shared by both commits | `ddc4ec36cdade1749127fe5d50cbbf218b2878e6` |
| Candidate version for each provider | `0.1.0-ci.1` |

CLI `git push` could not authenticate in this environment. The connected GitHub GitData API created a commit with the same complete tree and different commit metadata. Its returned tree and a subsequent local fetch were checked. The main task worktree now tracks the PR head and is clean; the two provider worktrees remain clean at the original tested commit. The [local Git observation](local/checks/tested-and-pr-tree.json) independently records both tree objects, an empty commit-to-commit file diff, the provider worktree identities and the original commit-object hash.

All original test, package and review receipts retain the local tested commit. They have **not** been rewritten to name the PR head. Tree equality binds the changed source bytes to that head; it does not replace PR CI. The [original commit object](local/checks/local-tested-commit.txt) is retained so the original local identity can be reconstructed after fetching the shared tree.

The executing parent agent observed [Design PR 18](https://github.com/IzuSharp/NativeWeave-Design/pull/18) at head `e4697af48958656257acef0b0786c34b1300393b`, tree `02148947c0a8e14b6194cfac94990a55fe621f1c`. Its two current PR runs, [45351400710](https://github.com/IzuSharp/NativeWeave-Design/actions/runs/45351400710) and [45351400577](https://github.com/IzuSharp/NativeWeave-Design/actions/runs/45351400577), both concluded `success`. That does not assert a Korda or Plan check result.

## Implementation and compatibility

The ten public database attributes now use the `Db` prefix in declarations, Roslyn matching, generated models, reverse scaffolding, diagnostics, current API projections, tests, samples and maintained documentation. The exact rename manifest projects frozen contracts into the current naming scheme without rewriting their historical bytes. Generated API references were regenerated from the current declarations and contract inputs.

This is an intentional source and binary API break for the removed attribute type names. Applications update their annotations to the current short forms and rebuild against a consistent package/generator version. There are no public aliases for the retired attributes. Namespace, constructor arguments/defaults, attribute targets and behavior remain unchanged: assembly `[DbCodec]` registers conversions, `[DbUseCodec]` selects a conversion, and JSON uses the existing source-generated metadata. Database files, the native ABI and the physical migration table name are unchanged. The upgrade mapping and before/after example are in the product upgrade guide and PR.

## Local verification actually observed

[files.json](local/files.json) records SHA-256 and byte length for every retained local evidence file. Raw source receipts and logs were copied byte for byte; the 32 regression log hashes and six generator log hashes were checked against their original command records. Existing task labels such as `DB-CPP-01`, `DB-API-01` and `B10` inside reused harness output remain intact and are not relabeled as new observations.

Raw log whitespace is preserved, consistent with Plan's existing exact-evidence policy; the task-local log attribute rule does not alter product/source formatting gates or convert any failed format result into a pass.

| Check | Observed result and retained evidence |
| --- | --- |
| Selected work | [Impact plan](local/checks/impact-plan.json) selects shared Linux checks and independent SQLite/PostgreSQL package sequences. The [shared final log](local/checks/DB-Rename-01-linux-checks.log) completes `database.regressions`, `generator.test`, `api.tool` and `relations.api`, ending without a traceback. Native build and API work were retained from the earlier source-bound attempt. |
| Database regressions | [Result](local/regressions/result.json) and [32 command records](local/regressions/commands.json) report `passed`, Linux x64, real PostgreSQL 18.0 and SQLite, and Native AOT execution. All 32 commands exited 0; the 20 native CTest cases passed. The retained query oracle has 52 cases. |
| Managed/native regression details | The actual two-provider runs report 482 NativeHost assertions, 357 migration assertions, 997 materialization assertions, 1,059 Fluent assertions and 2,207 relation assertions. Seven actual relation negative compilations passed. These are counts from individual harnesses, not a newly inferred count of independent scenarios. |
| Generator and scaffolder | [Status](local/generator/status.json) and [six commands](local/generator/commands.json) passed. The [Native AOT component log](local/generator/03-component-aot.log) records 26 total static DTO assertions, including 19 mapping-specific assertions. The [compiler log](local/generator/06-exact-api-diagnostics-incremental.log) records 31 convention/projection/policy and negative mapping checks, eight emitted scaffold compilation/order checks, and 15 negative cases covering all seven diagnostic IDs. |
| Exact API and documentation | The generator checker covers 26 public Attribute symbols across all ten new types, rejects retired names, and checks historical signatures plus additive contracts, XML/reference output, determinism and incremental invalidation. The shared API log verifies 523 exact `Korda.Database` signatures and 163 exact `Korda.Data` signatures, with complete XML/reference coverage. |
| SQLite provider sequence | [Package/consumer log](local/checks/DB-Rename-01-sqlite-checks.log) and [final remaining-check log](local/checks/DB-Rename-01-sqlite-final-checks.log) retain the actual package, consumer and validation results. The final retry completes `sqlite.packed-api`, the selected native ABI test and `sqlite.test`. |
| PostgreSQL provider sequence | [Provider log](local/checks/DB-Rename-01-postgresql-checks.log) completes `postgresql.test`, `public.consume-aot` and `public.validate` after the earlier build/package actions. |
| Tooling | [Tooling log](local/checks/tooling.log): 44 tests discovered, 43 passed and one skipped because CMake was unavailable on that targeted test invocation's PATH. This is not a claim that all 44 tests executed. |
| Limited whitespace check | `dotnet format whitespace --folder --verify-no-changes --include` over the 14 changed C# files exited 0, as directly observed by the executing parent agent. Its [empty stdout log](local/checks/changed-csharp-whitespace.log) is the formatter's successful silent output. This covers that file-scoped whitespace check only. |

### Candidate package, tutorial and business acceptance

Both provider archives were actually built from the tested commit. The [SQLite release](local/sqlite/release.json) and [PostgreSQL release](local/postgresql/release.json) identify the exact candidate bytes. Their `publish` field lists selected release modules; it is not a receipt of publication. This task ran no package upload or public publication command. No published package was substituted for these candidates.

| Candidate | Archive SHA-256 | Packaged native SHA-256 |
| --- | --- | --- |
| `Korda.Database.Sqlite.0.1.0-ci.1.nupkg` | `5078ad4f032cd3b7274156c42872f76489d184e4ced9ad6f3745e0582ebdda1a` | `89fa27f38be811d9e300c1745b6f13e83fbd73cea973c868b36d5ee48190875c` |
| `Korda.Database.PostgreSql.0.1.0-ci.1.nupkg` | `860550c3977585cab75a84d3caa269f57f29b9305dead1514fcdb80253069a57` | `e206b098cd9d6215db5641b06eccf3d05d8637e9c06c429f1ae6dec94eab693e` |

The [SQLite order receipt](local/sqlite/orders.json) and [PostgreSQL order receipt](local/postgresql/orders.json), together with their twelve publish/execute logs, record source-tree-external `PackageReference` consumers. Each provider completed `scaffold`, `original` and `edited` stages. All six native publishes and all six executions exited 0; publish logs report native code generation and execution results report `Aot: true`. The stages passed 19, 21 and 21 business checks respectively, exercising real database reads/writes, immutable DTOs, codecs/JSON, transactions, migration review and reverse-generated models.

The four tutorial source files compile in both the `original` and `edited` AOT stages. They are extracted from the actual archive `README.md`, current `docs/getting-started.md`, and the two complete model/query fences in `docs/guides/query-generator.md`. The receipts retain source-document, fence and emitted-file hashes; no hand-copied tutorial substitute is used. Between `original` and `edited`, the source-file set is identical and only `Models.cs` changes. Tutorial and scaffold hashes remain identical, AOT executable hashes differ, and the same packaged native bytes are reused.

The page-plus-detail observation is two SQL executions for each provider, with zero protocol submissions for SQLite and ten for PostgreSQL. These counters describe that measured operation only; they are not network packet counts, claimed round trips, or totals for the entire business run.

[SQLite packed API](local/sqlite/packed-api.json) and [PostgreSQL packed API](local/postgresql/packed-api.json) passed inspection of the exact archive DLL, XML and README. Each extracted `Korda.Data.dll` passed the 163-signature compiled API/XML/reference check. The [subsequent byte review](local/review/independent-package-review.json) independently recomputed every listed archive entry hash (40 for SQLite, 41 for PostgreSQL), parsed actual PE/CLI public type metadata, and found all ten new Attribute types with no retired public Attribute types. All ten XML type entries are present; packaged README/current tutorial names and their hash bindings were checked.

That review also rechecked all twelve retained publish/execute log hashes, the four tutorial extraction paths, the sole DTO source change and native reuse. Its author also implemented portions of the rename and tutorial harness; this is independent byte verification, not a separate implementation approval or a human review. The temporary consumers, their native executables and disposable databases had already been cleaned by the runner. The reviewer did not reopen or rerun those deleted executables. AOT execution claims rely on the retained real SDK output, successful execution logs, runtime AOT guard, receipts and package/source bindings; that limitation is preserved in the review.

## Host limitations and retained recovery attempts

The full workspace `dotnet format` check did **not** pass locally. Its [raw failure](local/attempts/dotnet-format.log) reports `SocketException (13): Permission denied` while the MSBuild host opens its Unix named pipe. The [first format failure](local/attempts/DB-Rename-01-linux-initial-format-failure.log) and subsequent socket/build-server interruptions remain in `local/attempts/`. The limited folder whitespace success above did not close the workspace formatter obligation. The unchanged complete formatter subsequently passed in [Korda Linux CI job 138297867132](https://github.com/IzuSharp/Korda/actions/runs/45351187416/job/138297867132), as recorded separately in the [PR checkpoint](pr-checks.json); the local failure record remains unchanged.

The retained recovery sequence also includes candidate-version mismatch, SDK-path lookup and immutable-output-directory failures. The final runs set the candidate version to the plan's `0.1.0-ci.1`, supplied the actual SDK layout to tools resolving that layout beside `dotnet`, and resumed the remaining checks after retaining failed attempts. The shared resume helper checks a clean source tree, exact native manifest commit/tree and native asset hashes before reusing previously completed build/API work. It explicitly reports the full formatter as unpassed.

The archived [SDK launcher](local/environment/dotnet-launcher.py), [resume helper](local/environment/resume_db_rename_checks.py) and [extra packed API audit helper](local/environment/audit_db_rename_package.py) document the actual local environment adaptation. They are scratch execution aids, not repository product gates. The launcher forwards to the actual pinned .NET 11.0.100 SDK with ordinary single-process/no-build-server options and `os.execv`; it does not synthesize compiler or test output. These exact archival files contain the original absolute paths and are not portable entry points without path adjustment.

## Omitted binaries and reproduction

This evidence directory deliberately omits `.nupkg`, DLL, native library and Native AOT executable binaries. The release manifests, order receipts and packed API receipts retain their archive/content hashes, including the two archive/native hashes above. Logs and JSON evidence remain reviewable without checking binary artifacts into Plan.

To repeat the verification, fetch the PR branch and use the recorded complete source tree in three independent Linux x64 worktrees. To recover the exact original local commit object, first fetch its shared tree and parent, then run `git hash-object -t commit -w` on [local-tested-commit.txt](local/checks/local-tested-commit.txt); its result must be `9aa0b9092c6b2dfc19d5c98d82cb131699171d66`. A detached worktree at that object restores the original source identity without changing any receipt.

Install the repository-pinned SDK and native dependencies, provide real PostgreSQL 18 server/tools, and retain the existing SQLite dependency. Use the committed impact planner against starting Korda `ea72031db6f9111a31c6f743b5babc345f96862d`; the [archived plan](local/checks/impact-plan.json) records the exact selected actions. In each independent worktree, run the normal worker for its scope with the candidate version matching the plan:

```sh
python3 eng/ci/impact.py ea72031db6f9111a31c6f743b5babc345f96862d --output artifacts/plan.json
export PACKAGE_VERSION=0.1.0-ci.1
python3 eng/ci/worker.py run artifacts/plan.json linux
# In the separate provider worktrees, use sqlite and postgresql instead of linux.
```

The provider sequences build the actual package, run the external AOT consumers and validate their receipts. The committed `eng/ci/orm_experience.py` drives all three order stages and extracts the tutorial sources. For the additional whole-archive audit, the retained helper shows the exact extraction and compiled API command, and the review JSON describes the independent PE/CLI and hash checks. Rebuild the API checker from the same source before repeating that audit. Exact archive hashes identify the observed candidates; fresh builds on different paths or tool installations are not promised to be byte-identical. No public publication is required for reproduction.

## Retained old-name categories

The tested product tree was rescanned with the required `git grep -in weave` and `git ls-files | rg -i weave`. It contains 369 matching physical content lines across 60 files and no matching tracked filenames. The mutually exclusive line classification is: 236 pinned Design input lines, 49 historical snapshot lines, 26 real repository/path provenance lines, 25 upgrade/rename validation lines, 17 historical compatibility or negative-test lines, 13 physical migration-table lines and three project-origin lines. No maintained current usage was left unclassified.

In Plan, the old attribute spellings in earlier graph nodes, `tasks/B10.md`, `fragments/orm.json`, the legacy refinement tool and completed ledger/logs belong to accepted, source-bound historical plans or observations. Their hashes and paths remain intact. Real `IzuSharp/NativeWeave-Design` URLs and immutable original repository references remain provenance; `_nativeweave_migration_phases` identifies an existing physical database table. Upgrade mappings intentionally list previous names. The local raw evidence may also contain historical harness labels or immutable paths; none has been edited merely to reduce a grep count.

## PR checkpoint and stop condition

[Korda PR 36](https://github.com/IzuSharp/Korda/pull/36) at `b1e5706a12b7115255f465981ada4bbe839de4f4` completed [CI run 45351187416](https://github.com/IzuSharp/Korda/actions/runs/45351187416) successfully. All nine selected jobs passed, including shared Linux checks, both independently built provider packages, the two CodeQL language jobs and final `Verify`. The original full workspace formatter ran successfully. The workflow tested GitHub's temporary integration commit `c3c5764e054049cfd7d095ab05c5fb414d186953`; a fetch confirmed that its tree is also `ddc4ec36cdade1749127fe5d50cbbf218b2878e6`. This temporary test ref is not a merge into `main`.

All twelve attached Korda check runs completed: nine success, two intentional skips (unselected modules and public publication), and one neutral CodeQL summary. The neutral summary reports that historical `nativeweave/csharp` and `nativeweave/python` configurations present on `main` were not found. Both current `korda/*` language jobs succeeded. The security workflow is byte-identical on starting main and the PR (Git blob `3f5f1c47b44955edc1d09007ecad662430f1ffa4`); no configuration was changed to suppress this historical notice.

[Design PR 18](https://github.com/IzuSharp/NativeWeave-Design/pull/18) at `e4697af48958656257acef0b0786c34b1300393b` passed both current and historical PR workflows and the branch-push naming check. [Plan PR 31](https://github.com/IzuSharp/Plan/pull/31) at the preceding checkpoint `87ffe5de4deca258c69a4a600c29b2077bce8aff` passed [run 45352187101](https://github.com/IzuSharp/Plan/actions/runs/45352187101), including every unchanged historical provenance and graph gate. Full check identities and results are in [pr-checks.json](pr-checks.json).

The graph now records `awaiting_review`. The final evidence-only Plan commit must pass its own PR checks before the delivery turn ends; consult the live PR and its description for the observed final head/result. This record does not claim a future check outcome or label the task accepted. Keep all three PRs open for maintainer review. **Do not merge, enable auto-merge or publish packages publicly.** Original failed attempts, local candidate identities and package hashes remain intact.
