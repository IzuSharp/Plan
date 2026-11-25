# CI correctness separation: committed change and affected validation

The cleanup is committed as **`e125bcd8bebb27e60a1172ab64d9dec3a996e4e2`**, tree **`898ff6959cabfeab4c4725e2c9c277973b4ae30c`**, on `task/DB-Exec-02-ci-correctness` in `/workspace/scratch/17ac3f8f2fbf/worktrees/DB-Exec-02-ci-correctness`. It changes twelve existing test/documentation/local-harness files, 119 insertions and 115 deletions. The worktree is clean. Frozen B remains unchanged at a27ff31.

This is **affected default AOT entry validation**. It does not replace the final complete component verifiers or accept the unresolved original `native.sqlite14` failure. It runs no benchmark or profiling window.

## Change

Default verifiers no longer launch the four Abstractions, two Binding or three Streaming allocation subprocesses. Fluent's three cost windows become finite behavior checks. Streaming no longer includes allocation windows or process RSS/B telemetry in ordinary execution. Host snapshot allocation budgeting moves to the existing explicit local snapshot probe.

All existing local flags remain available. Complete scalar/control/wire/projection oracles, finite quotas, cancellation, failures, races and owner retirement stay in ordinary tests. OwnedBatch's original correctness checks now run by default, together with two complete batches in each copied/owned lane; every value and all transfer/release counts are checked without sampling counters.

Interop `Supports` publicly promises no per-call allocation or native dispatch. Its ordinary test retains that guarantee through initialized known/unknown cases, a thread-byte equality assertion and unchanged bootstrap call count. It drops the 100-warmup/10,000-call window. No public XML/signature promise is removed.

The local empty-parameters harness's two stale `ParameterDefinition.Encode` references now use the existing `PreparedParameterLayout`; no obsolete production wrapper is restored. Historical reproduction snapshots are unchanged.

## Actual default entries executed

Evidence root: `/workspace/scratch/17ac3f8f2fbf/managed-research/test-results/ci-cleanup-e125bcd`. `summary.json` references every per-entry receipt, complete argv, executable hash and raw log. Every accepted test application is an ELF Native AOT executable with no adjacent application DLL. No JIT consumer test was executed.

| Entry | Actual result | Retained behavior reached |
| --- | --- | --- |
| Data.Streaming, attempt 02 | PASS; two actual providers, 60 provider cases / 615 main assertions; 19 borrowed-lifetime, 118 join-race, 539 owned-batch and 442 row-reuse assertions | Original mapper/owner/finalizer/NULL/shape/failure/cancel cases; complete copied and owned batches; independent enumerators. Final managed-live-bytes and native wrapper counts are zero |
| Query.Fluent | PASS; 28 provider cases, 1,169 assertions, 427 managed retirements | New lazy construction and composition checks, complete empty-parameter golden, captured values, foreign/missing/extra/NULL parameter errors, mutation/transaction/streaming cases. Composition checks complete SQL equality and literal frame size; it does not claim a byte-for-byte literal-payload oracle |
| Data.NativeHost | PASS; 5,942 parser oracle inputs; main suite 610 assertions / 206 observed retirements, all owner categories zero | 21 batch-record assertions; each provider's 16 held-mapper cases / 287 assertions, 67 fetch-boundary and 34 parent-transaction assertions; unknown/known EOF, session/source close, cancellation, malformed ownership and exact row-limit behavior |
| Query.Binding | PASS; 13 cases / 165 main assertions; 625 projection encoding assertions | Complete projection goldens, binder/error order, 4 MiB limits, scratch poisoning and synchronous native borrow, disposal/source gates, exact schema, relation close. The 81 command-only assertions are included in its main assertion count |
| Data.Abstractions | PASS; all 25 managed families | Configured scalar correctness, 73 control-record assertions, 10,958 wire validation assertions, complete new parameter-layout comparisons/rejections and existing codec/copy/NULL goldens |
| Interop.Negotiation | PASS; all 26 default cases / 330 assertions; Coexist has 21 assertions | Published finite Supports result/no-allocation/no-bootstrap-reentry guarantee, capability/version/hash/export validation, concurrent inspection, failure/retry and output-record contracts |

Streaming's actual application argv is precisely its executable, the fresh result directory and `--require-aot`. It does **not** use `--correctness-only` or a profiling flag. NativeHost uses its original default entry; Fluent uses result directory plus `--require-aot`. All three run through the original `tests/Data.NativeHost/run.py` with a fresh PostgreSQL18 TCP cluster in the same subprocess namespace. The wrapper stops each cluster in its finally block. Streaming forwards that same endpoint into its existing `KORDA_TEST_POSTGRES_URL` environment name.

The remaining entries use their established default arguments. Negotiation runs the exact 26-case list read from its unchanged verifier and copies retained fixture binaries to a fresh directory before cases can create repaired/corrupt fixture files. It does not mutate the earlier evidence.

The actual artifacts confirm the new default boundary: Streaming emits only its correctness result; Fluent's result contains AOT/assertion/retirement/case/native-hash fields; Abstractions and Binding emit no allocation reports; Host emits its parser oracle count and no snapshot allocation window.

## Bound native inputs

All 113 native producer input hashes match the e125bcd worktree before each entry. Native source is unchanged from clean producer `dc82792c519ee90be30f5c49b2f785ecd33ad915`. Tests reuse the already produced B fixtures/assets by explicit paths and hash them before and after execution. No CMake cache is reconfigured from a different worktree.

- SQLite Host: `49e8f8ea68a17a63d2c25f367338498c3ac602ecb1c7af2498d36e15cd799ca5`.
- PostgreSQL Host: `2d34f1dce999b69545d0fdd8a12e28252b33f76aed00eb5148aa921be13bfdf5`.

Every receipt records the fixture hashes separately, the clean producer manifest and executable hash. The controller uses the locked .NET11.0.100/LLVM23.1.5 environment, one MSBuild node, no shared compilation, and actual Release AOT publish with AOT warnings treated as errors. Exact commands, including asset properties and fresh outputs, are recorded rather than inferred.

## Failures and limits retained

Streaming attempt 01 failed during restore with NU1004. The standalone controller used `dotnet restore -r`, while this test project chooses its AOT lock path from `RuntimeIdentifier`; restore's shorthand set `RuntimeIdentifiers`. The corrected controller additionally passes `-p:RuntimeIdentifier=linux-x64`. The failed log, receipt and exact controller source are retained; lock files were not changed. No test or PostgreSQL process ran in the failed attempt. Attempt 02 is a separate fresh directory.

A supplementary whitespace check over the seven touched C# files returned exit 2. Its errors are all in preexisting nested-loop indentation in `SnapshotProbe.cs` and two existing long record declarations in the local empty-parameters harness. The diff at this commit adds only the snapshot probe call and changes the two encoder references in those areas; it did not introduce those formatting errors. The remaining changed C# files produced no formatting diagnostics. This is not a passing formatting result. The raw log is retained as `changed-csharp-whitespace.log`. No formatting edits or source changes were made during these six AOT validations.

The original B full driver failed `native.sqlite14` after case4 returned with source/session owner counters still live. That original failure remains recorded and under a separate native completion-fence investigation. These managed successes must not be used to hide or relabel it. The final integrated candidate still needs the complete existing native/provider/default/verifier/package checks.

## CI routing

`python3 eng/ci/impact.py origin/main --output artifacts/plan.json` was run at this commit. `impact-comparison.json` records that actions are identical to B. The additional Negotiation test reason is correctly covered and deduplicated by the existing `database.regressions` rule in `eng/ci/database_plan.py`; no new workflow, job, action, switch or performance route was added.

Static AST checks of the three changed Python verifiers confirm that all nine former profiling process invocations are absent. `default-verifier-routing.json` records the actual remaining literal run labels and source hashes. This is a static routing proof, separate from the executed application entries.

The broader audit is `proposals/ci-audit/README.md`, with the exact selected action closure, all raw search matches, counter/timeout/quota classification and active-harness deleted-symbol scan. The earlier mistaken claim that Abstractions flags were not called by default was explicitly corrected in the original review.

No further optional AOT execution is needed for this isolated cleanup. After the coordinator chooses the native/managed final candidate and integrates this commit, run the final complete existing verifier against that committed source and its matching native/package producers.
