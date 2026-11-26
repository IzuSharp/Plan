# Independent review of actual public package delivery

## Finding

**Both independently installable provider packages have accepted public-delivery evidence for `0.1.0-preview.4`. No blocking inconsistency was found in the reviewed artifacts, retained verification records, public AOT consumer receipts or successful job logs.**

The accepted evidence is bound to Korda main commit `7ff7b57b907b689defb880b8af62d83679608603`, source tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc`, and CI run `45807237435`, whose recorded second attempt completed successfully. This is the same previously established source tree as measured candidate `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`. Public preview archives and application AOT executables are distinct release artifacts; this review does not relabel them as the binaries used in the earlier performance campaign.

This review inspected the parent's downloaded GitHub artifacts, inventories, attempt/job metadata, registry verification logs, public consumer logs and artifact-reader output. It independently recomputed the downloaded artifact/archive/native/log byte hashes used below and compared retained text with the corresponding ZIP members. It did **not** rebuild or execute code, run tests or benchmarks, repeat cryptographic signature verification, trigger workflows, mutate repositories or change archived recovery evidence. Cryptographic verification and AOT executions are observations from the existing CI, supported by its retained logs and receipts.

## 1. Accepted artifacts and preserved failure history

| Provider | Accepted artifact | Producing successful evidence | Actual public-consumer interval, UTC |
| --- | --- | --- | --- |
| SQLite | `15113598366`, `public-consumption-sqlite-0.1.0-preview.4`, 2,189,644 bytes | Original publisher job `139871492392`; latest-attempt job listing also exposes `139887662491` with the same original step timestamps. | 2026-11-26 11:42:05–11:42:57 |
| PostgreSQL | `15114795427`, `public-consumption-postgresql-0.1.0-preview.4`, 1,584,185 bytes | Attempt 2 publisher job `139887660195`. | 2026-11-26 11:47:41–11:48:29 |

Artifact selection is by the IDs printed in successful upload logs and their run/source identity, not by artifact name alone:

- `sqlite-publish-success.log:446–448` identifies `15113598366`, finalized at 11:42:59 UTC.
- `postgresql-publish-attempt-2.log:504–506` identifies `15114795427`, finalized at 11:48:31 UTC.
- Both inventory entries identify run `45807237435`, branch `main`, and the main merge commit above. Their ZIP byte sizes and SHA-256 values agree with the retained inventory and the parent's artifact-reader observations.

SQLite is one original successful public execution retained in the second-attempt job listing. Its older timestamps must not be described as a new SQLite public execution during the PostgreSQL retry.

PostgreSQL attempt 1 is a real, preserved failure. Job `139871492163` pushed the package, then its existing indexing wait ended with `TimeoutError: ['Korda.Database.PostgreSql']` at 11:44:22 UTC. The public AOT step was skipped. The `always()` upload produced same-named partial artifact `15113029173`, only 3,495 bytes, containing `publication/release.json` and `plan.json`. It has no signed registry package or public consumer receipt and receives no acceptance credit. These facts are retained in `product-main-attempt-1.json`, its job metadata/log, the full artifact inventory, and `partial-artifact-observation-01.json`.

On PostgreSQL attempt 2, the existing publication-state check logged `publish=False, verify=True` at 11:47:31 UTC. Login/push were skipped; verified registry readback, public Native AOT consumption and evidence upload all succeeded. This is successful completion of the same already-pushed version, not a second upload or a changed package version. `product-main-attempt-2.json` records run completion with `conclusion=success` at 11:48:35 UTC.

## 2. Exact package and byte identities

Both public `release.json` files equal their corresponding verified candidate release records. Each contains exactly its own provider package, empty package dependencies, `source_dirty=false`, Linux x64 identity, the merge source commit and the source tree above. The signed packages' native manifests also contain the same merge commit for `sourceCommit` and `packagingProducerCommit`, `sourceDirty=false`, the correct provider/version, ABI major 1 and the expected native path.

| Identity | SQLite | PostgreSQL |
| --- | --- | --- |
| Package | `Korda.Database.Sqlite` | `Korda.Database.PostgreSql` |
| Version | `0.1.0-preview.4` | `0.1.0-preview.4` |
| Public artifact ZIP SHA-256 | `2f66ac8719dec125de7ccf9ad8733b6b17f017edfe2940dfce33f3746d32db42` | `842eb154578309216e2e6ad959824bda5eae0e978b41b1bb7915c4b915d86927` |
| Upload package SHA-256 | `0a7b4f74fcf610e2600ca1a33eb55f93a039a5e7fa4ecc98b1d274e58b82673c` | `c6a3db442864eb7e2964c8bfd249c002e87a7ad39623145a7e0912a022a8e09f` |
| Signed registry package SHA-256 | `aefa5d1079170843469a5fc44a140dc2446126f3928d1a187581208ae8d44a8a` | `04a5305f733acfb1cf6f287237b0752816746b737470c59b2308b7604dd08962` |
| Signed package bytes | 2,187,947 | 1,583,493 |
| Native image SHA-256 | `fa971d8476f1d74d414cd0e92f3c8ed561bc87887e51ec8c0f7f9de8f3dac482` | `81a6dd1fb338e56579f9176031cc680c078ccf3d88d60c4b39efaaf8d89ec4f8` |
| Full package `inputs` | `41ca933c2990a2184613e459c21440486549884634ef4678ad80e45bc6b50941` | `f1727c1a6fd91c691fd35559b6314764d05f611de5907b1cf62e6e3f4b5cbff3` |
| `payload_inputs` | `1c5b746255a494352fb38117fd7f4a94689230b8df2069626a7a475f7d8376ec` | `5e7f3f23ecbadb9bccedfe7a3280c995d6f137c887b15c92dc88e3e852cdf3dc` |

The actual signed archive bytes equal the hash in the registry verification, nested signature record, public consumer's `tutorial_package_sha256`, and root observation. The native member bytes hash to the release/native manifest value and all corresponding runtime receipts. Archive `korda/public.json` fingerprints equal the public plan and release input fingerprints, with metadata-excluding `payload_inputs` bound separately.

The upload and registry archive hashes differ, as expected for the existing repository-signing process. Existing CI verification records `unsigned_entries_equal=true`; this review did not substitute whole-archive equality for that accepted-payload rule or repeat the cryptographic verifier.

The signed `.nupkg` files remain present inside `downloads/public-{provider}.zip`. Their omission from the extracted text-only review folders is explicit in `omittedSignedPackage`; it does not mean those bytes were absent from the downloaded evidence.

## 3. Registry and signature evidence

For both providers, `publication/registry-readback/{PackageId}.verification.json` reports:

- The exact selected package/version, merge source commit and official NuGet flat-container URL.
- `mode=repository-signature-and-accepted-payload`.
- `verified=true`, `resume_allowed=true`, `unsigned_entries_equal=true`.
- Upload, registry and nested signature archive hashes consistent with the identities above.
- `signature.verified=true`, route `repository-primary`, official NuGet v3 service index and owner set `['dekueon']`.
- Certificate SHA-256 `1f4b311d9acc115c8dc8018b5a49e00fce6da8e2855f9f014ca6f34570bc482d`, matching the existing source policy.

Both retained `verify.stdout` files show the repository signature, exact service index/owner/certificate identity, certificate and timestamp verification output, and the final `Successfully verified package` line for their exact version. Both `verify.stderr` files are empty. Their successful workflow step conclusions corroborate these records.

SQLite's successful log records `Verified Korda.Database.Sqlite 0.1.0-preview.4` at 11:42:05 UTC. PostgreSQL's second-attempt log records the corresponding successful line at 11:47:41 UTC. The signed package timestamp appearing in the verifier output is not a substitute for the later successful readback/consumer completion time.

## 4. Public package Native AOT consumption

Both successful publisher logs explicitly invoke `eng/ci/consume.py ... --public`. Under the unchanged source implementation, this uses public NuGet sources and an isolated application package cache without the candidate feed. Actual receipt command paths are outside the repository: `/tmp/korda-public-91twt_f1/orders-sqlite` and `/tmp/korda-public-u80pi45_/orders-postgresql`. Each public restore package hash is bound to the accepted signed registry archive as described above.

### B24 standalone consumer

The successful job logs contain one provider-specific `B24_RESULT` each:

| Provider | Runtime result time, UTC | Observed proof |
| --- | --- | --- |
| SQLite | 11:42:24.172 | `task=DB-CPP-01`, provider `sqlite`, `dynamicCodeSupported=false`; native receipt `libnw_database_sqlite.so` with the native hash above. |
| PostgreSQL | 11:48:01.076 | `task=DB-CPP-01`, provider `postgresql`, `dynamicCodeSupported=false`; native receipt `libnw_database_postgresql.so` with the native hash above. |

Both include `actual-native-aot`, `generated-table-descriptor`, `typed-entity-materialization`, `typed-native-database-roundtrip`, `typed-fluent-dto-query`, `actual-database-native-mapping`, and `database-local-owners-retired`. The selected-module/path checks are also present. This is recorded runtime behavior, not merely a restore or successful compiler invocation.

These independent release jobs do not execute the combined two-provider graph. The review accepts standalone public-package consumption for each provider and does not claim broader combined-graph execution or infer additional owner counters beyond the named checks.

### DB-API-01 scaffold, original and edited consumers

Both public business JSON files end with `task=DB-API-01`, `result=passed`, the exact provider/version, `same_native_after_dto_edit=true`, and `tutorials_compiled_against_candidate=true`. The latter is the existing generic field name; the actual `--public` invocation, evidence path and signed-archive hash binding establish public consumption.

Each receipt has exactly six distinct command entries: publish and execute for each of `scaffold`, `original`, and `edited`. Every command exits zero. Each publish specifies Release, Linux x64, `PublishAot=true`, exact preview version, the proper provider and AOT warnings as errors. Each execute directly invokes its produced `OrmExperience` executable. All twelve retained command-log byte hashes match their receipts. Each of the six execute logs has exactly one seven-field `DB_API_RESULT`, fully equal to the corresponding receipt row projection.

| Provider | Three rows | Business assertions | Counters in each row |
| --- | --- | --- | --- |
| SQLite | `Aot=true`, `ProjectReferences=0`; DTO original/original/edited | 19 scaffold checks, 21 original checks, 21 edited checks | `SqlExecutions=2`, `ProtocolSubmissions=0` |
| PostgreSQL | `Aot=true`, `ProjectReferences=0`; DTO original/original/edited | 19 scaffold checks, 21 original checks, 21 edited checks | `SqlExecutions=2`, `ProtocolSubmissions=8` |

The checks include pagination, composite cursors, empty batches/pages, the same immutable DTO through Fluent and parameterized SQL, typed aggregates, custom mappings/nullability, stale versions, insert/confirmed callbacks, original error/confirmed rollback, pre-cancellation, explicit destructive migration selection and scaffolding. Original/edited additionally compile and execute both scaffolded entities and composite keys.

The counters refer to the sample's defined page/detail observation window. They do not count all SQL issued by the process, all FFI calls, or required server replies. PostgreSQL's eight submissions must not be described as eight round trips.

For both providers, original/edited have different `ModelsSha256` and different `ExecutableSha256`; the source map differs only at `Models.cs`. The two scaffold source hashes remain equal. The four tutorial entries have distinct compiled filenames, and their manifest hashes exactly equal both original and edited `TutorialSources` maps. All three phases retain the same native image hash, also matching the actual packaged and B24-loaded image. These records substantiate the application DTO/source edit and corresponding AOT regeneration without rebuilding or replacing the packaged native provider.

## 5. Reader outcome and scope of acceptance

The parent's corrected `read_public_artifacts.py` ran at 11:52:16 UTC with exit code 0 and empty stderr, producing accepted observations for both providers. This review independently corroborated the archive/native/log bindings and runtime records rather than treating the script's exit code alone as acceptance.

The main plan selected both providers and their public checks, with `build_scopes` of interop, linux, postgresql and sqlite. Recorded plan/build/Verify results and the final successful publisher steps are consistent with that plan. The second attempt preserved the earlier successful jobs; it did not constitute a fresh execution of every selected check.

The evidence is sufficient to report that both `0.1.0-preview.4` packages were delivered through the existing release path, read back and accepted as signed official registry packages, and consumed independently from public NuGet in successful Native AOT processes. The original PostgreSQL indexing failure and partial artifact remain explicitly preserved.

This is delivery and package-consumption acceptance. It does not alter the performance review's limits: the validated selected refactor is not a proof of global optimality, framework-only zero allocation was not established, and release consumption does not add new long-run performance or required-reply measurements.

## Evidence locations

All paths below are relative to `delivery-01`:

- `all-artifact-inventory-01.json`, `public-artifact-inventory-01.json`, `public-artifact-selection-01.json`.
- `product-main-attempt-{1,2}.json`, `product-main-attempt-{1,2}-jobs.json`.
- `sqlite-publish-success.log`, `postgresql-publish-attempt-{1,2}.log`.
- `partial-artifact-observation-01.json`, `downloads/partial-postgresql-attempt1.zip`.
- `downloads/public-{sqlite,postgresql}.zip` and matching extracted `public-{provider}/` trees.
- `public-{provider}/publication/release.json`, `plan.json` in the containing `public-{provider}/` directory, registry verification/signature logs, and `publication/consumer-evidence/public/` business receipts/logs.
- `public-artifact-reader-01.command.json`, `.stdout`, `.stderr`, and `public-artifact-observations-01.json`.

No additional product or release correction is requested by this review.
