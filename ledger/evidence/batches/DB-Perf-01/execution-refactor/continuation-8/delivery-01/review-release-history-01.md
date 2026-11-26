# DB-Exec-11: independent release-history review

## Conclusion and scope

The finalized [delivery README](README.md) and [delivery summary](delivery-summary-01.json) accurately preserve the failed first PostgreSQL indexing/readback attempt, distinguish the later successful same-version verification and public consumption, and retain SQLite's original successful execution. The final delivery conclusion is supported by the observed main-run conclusion, successful publisher steps, explicitly selected artifact IDs, registry verification records and actual public Native AOT receipts. No unresolved inconsistency was found within this review's scope.

This review read existing metadata, publisher logs, extracted JSON and documentation only. It did not invoke GitHub, rerun a workflow, rebuild a package or consumer, execute a test or benchmark, recompute a hash, rerun signature verification, or change a repository, frozen file or archived recovery record. The only new file is this review. Downloaded-byte verification remains attributed to the parent's successful retained artifact reader; cryptographic verification and Native AOT execution remain attributed to the actual CI jobs.

## 1. The failed attempt is preserved and receives no acceptance credit

[Attempt 1](product-main-attempt-1.json) records run `45807237435`, event `push`, branch `main`, merge SHA `7ff7b57b907b689defb880b8af62d83679608603`, `run_attempt=1`, and final `conclusion=failure`. The [attempt-1 job metadata](product-main-attempt-1-jobs.json) identifies the specific failure: PostgreSQL publisher `139871492163`, not the product build, correctness checks or aggregate Verify.

The original [PostgreSQL publisher log](postgresql-publish-attempt-1.log) records `publish=True, verify=True` at 11:16:10 UTC and a successful push at 11:16:21 UTC. The subsequent **Wait for indexing and verify signed registry package** step failed at 11:44:22 UTC with `TimeoutError: ['Korda.Database.PostgreSql']`. The public Native AOT step was skipped. A successful push therefore does not grant signature/readback/public-consumption acceptance to this attempt.

The log contains the unchanged retry implementation: a 30-minute monotonic deadline, 404 responses leaving the package pending, and a guard that raises before another 120-second sleep would exceed that deadline. The observed step was approximately 28 minutes 1 second, from 11:16:21 to 11:44:22. The README correctly distinguishes this observed wait from the configured 30-minute budget. There is no basis here to call this a signature-policy rejection or a business/AOT failure; neither acceptance step completed in this attempt.

The always-run evidence upload produced partial artifact `15113029173` at 11:44:23 UTC. The [partial observation](partial-artifact-observation-01.json) gives it `acceptanceCredit=false` and records exactly two members: `publication/release.json` and `plan.json`. The extracted copies are retained under `partial-postgresql-attempt1/`. There is no verification JSON, signature acceptance, or public consumer result in this partial artifact. Its release and plan JSON are equal to the corresponding final PostgreSQL records; preserving them documents the same pending candidate, not a separately accepted package.

## 2. Exact chronology and retry scope

All times below are UTC on 2026-11-26 and are taken from retained logs and job/attempt metadata.

| Event | Observed time and outcome | Identity |
| --- | --- | --- |
| Main attempt 1 starts | 11:04:44 | Run `45807237435`, same merge SHA |
| Selected correctness gate finishes | Verify succeeds at 11:15:42 | Original Verify job `139871341986` |
| PostgreSQL upload finishes | Push succeeds at 11:16:21 | Original publisher `139871492163` |
| SQLite signed readback | Verified at 11:42:05 | Original publisher `139871492392` |
| SQLite public AOT and evidence | AOT succeeds at 11:42:57; artifact upload at 11:42:59; job completed at 11:43:01 | Accepted artifact `15113598366` |
| PostgreSQL first readback expires | Step fails at 11:44:22; partial artifact at 11:44:23; job failure at 11:44:25 | Partial artifact `15113029173` |
| Main attempt 2 starts | Attempt started at 11:46:53; PostgreSQL job starts at 11:47:00 | Retry publisher `139887660195` |
| PostgreSQL retry decision | `publish=False, verify=True` at 11:47:31 | Same `0.1.0-preview.4` candidate |
| PostgreSQL final acceptance | Signed readback at 11:47:41; public AOT succeeds at 11:48:29; upload at 11:48:31 | Accepted artifact `15114795427` |
| Main attempt 2 completes | Job/run conclusion `success` at 11:48:35 | Run `45807237435`, attempt 2 |

The [successful PostgreSQL log](postgresql-publish-attempt-2.log) and [attempt-2 jobs](product-main-attempt-2-jobs.json) show NuGet login and package upload **skipped**. The job downloads the existing candidate, successfully validates the tested tree/package allowlist/bytes, then performs signed official readback and `eng/ci/consume.py ... --public`. No new version, candidate package build, re-upload, relaxed signature policy or performance run is evidenced by this retry. Rebuilding and running the normal public consumer is its required correctness work.

The attempt-2 job listing assigns fresh IDs to carried-forward successful entries. SQLite's listed ID `139887662491` has the original start/end and step timestamps from publisher `139871492392`; its [successful log](sqlite-publish-success.log) selects the original artifact `15113598366`. This is not a second SQLite execution. The same caution applies to the carried-forward plan/build/security/Verify entries: their original successful timestamps are not evidence that they all reran during the short second attempt. Skipped matrices/security steps retain their recorded skipped state rather than being described as successful executions.

Both attempt records reference `.github/workflows/ci.yml` at the same `head_sha`. The reusable workflow reference sets for build, release, security and modules are also the same SHA `7ff7b57b907b689defb880b8af62d83679608603`; their array order differs, which has no semantic effect. This supports an existing-run retry without a workflow-source change.

The historical [pause](pause-handoff-01.json) remains preserved, and [resumption](resume-handoff-01.json) records the owner's request to continue, the already-observed successful attempt, `rerunTriggeredByThisResumedTurn=false` and `performanceRerun=false`. This audit does not attribute the external retry's initiation to an actor beyond what these retained control records establish.

## 3. Duplicate artifact names are resolved by execution and ID

The [complete inventory](all-artifact-inventory-01.json) retains both artifacts named `public-consumption-postgresql-0.1.0-preview.4`. The [selection record](public-artifact-selection-01.json) chooses explicit IDs from successful upload log lines, not by name alone. Those IDs also agree with the run, branch and source commit in the inventory.

| Artifact | Role and result | Recorded GitHub artifact ZIP digest |
| --- | --- | --- |
| `15113029173` | PostgreSQL attempt 1; partial, excluded from acceptance | `9d64ccdd3d8b8567267ef776dd9b845a04d9be9f9830efa381b2e4fb422742db` |
| `15113598366` | SQLite original successful public consumption | `2f66ac8719dec125de7ccf9ad8733b6b17f017edfe2940dfce33f3746d32db42` |
| `15114795427` | PostgreSQL attempt 2 successful public consumption | `842eb154578309216e2e6ad959824bda5eae0e978b41b1bb7915c4b915d86927` |

The final [public observations](public-artifact-observations-01.json) agree with the accepted inventory and the parent's artifact-reader receipt. I did not repeat the byte/hash checks. The original partial package/plan values match the successful PostgreSQL values, and both final provider release records are JSON-equal to their corresponding earlier candidate `release.json`. The public artifact plans contain the same values as the actual main plan; only the explanatory `reasons` map is absent, as expected for the workflow's reusable output. Neither a different version nor a replacement candidate is hidden by the duplicate name.

## 4. Final public package and consumer binding

For each provider, the extracted verification JSON records the exact official NuGet flat-container URL, merge commit, package ID and version, together with `verified=true`, `resume_allowed=true`, `unsigned_entries_equal=true`, and mode `repository-signature-and-accepted-payload`. The signature records use `repository-primary`, official NuGet service index, owner `dekueon`, and certificate fingerprint `1f4b311d9acc115c8dc8018b5a49e00fce6da8e2855f9f014ca6f34570bc482d`. These values agree with the existing policy and the retained reader observations.

| Package, version `0.1.0-preview.4` | Candidate upload SHA-256 | Signed registry SHA-256 |
| --- | --- | --- |
| `Korda.Database.Sqlite` | `0a7b4f74fcf610e2600ca1a33eb55f93a039a5e7fa4ecc98b1d274e58b82673c` | `aefa5d1079170843469a5fc44a140dc2446126f3928d1a187581208ae8d44a8a` |
| `Korda.Database.PostgreSql` | `c6a3db442864eb7e2964c8bfd249c002e87a7ad39623145a7e0912a022a8e09f` | `04a5305f733acfb1cf6f287237b0752816746b737470c59b2308b7604dd08962` |

Signed archive hashes differ from upload hashes; accepted unsigned entries and native payloads agree. The final public receipt's `tutorial_package_sha256` equals the matching signed registry archive hash, not the earlier candidate upload hash. Its three row-native hashes equal the release native SHA: SQLite `fa971d8476f1d74d414cd0e92f3c8ed561bc87887e51ec8c0f7f9de8f3dac482`, PostgreSQL `81a6dd1fb338e56579f9176031cc680c078ccf3d88d60c4b39efaaf8d89ec4f8`.

Both actual successful publisher logs contain the `--public` invocation and a `B24_RESULT` with `dynamicCodeSupported=false`, typed real-database roundtrip, typed Fluent DTO and retired-owner checks. The [smoke extraction](public-smoke-observations-01.json) matches those runtime payloads. Each final public business receipt has `result=passed`, six zero-exit command entries, and scaffold/original/edited rows with `Aot=true` and `ProjectReferences=0`. Only `Models.cs` changes between original and edited source maps; native, scaffold and tutorial hashes remain equal while executable hashes change.

The README correctly limits this to two independently consumed provider graphs. It does not claim that a combined provider graph ran, that the page/detail counters describe all SQL, or that the PostgreSQL submission counter measures RTTs. The generic `tutorials_compiled_against_candidate` field is not used to infer feed provenance; actual `--public` execution and the signed archive binding establish that provenance.

The artifact reader's recorded command exited zero at 11:52:16 UTC with empty stderr. Its scope is existing artifact bytes and receipt relationships, not new cryptographic or AOT execution. The finalized README also correctly states that binary ZIP/nupkg data are omitted from the Git text-evidence directory, with retained exact identities and official versioned URLs; it does not claim that the text directory alone is a binary restoration bundle.

## 5. CI and performance evidence boundaries

The actual plan still selects the existing interop/Linux/provider correctness/package actions and both independent providers. No benchmark, calibration, profiling or high-pressure action appears in that plan. The previously inspected performance directory declarations register ownership without `run` actions. Both retry attempts use the same workflow source, and the public plans preserve the same selection. There is no evidence that delivery/retry added a performance workflow, scheduled job, manual performance dispatch or hidden load; this history audit does not execute or introduce any such work.

The product merge tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc` and package full/payload fingerprints equal the frozen implementation inputs, as established in the earlier [candidate review](review-release-candidates-01.md). However, preview package/native bytes differ from the frozen `0.1.0-ci.1` producers. The final README and summary preserve that distinction: `measuredPackagesReboundToRelease=false`, `frameworkOnlyZeroBytesClaimed=false`, and `globalOptimizationExhaustionClaimed=false`.

The four 1800-second local measurements remain measurements of their original frozen workload executables and package/native identities. Public release success does not rebind their throughput/tails, refusal counts, GC/allocation/RSS values or unchanged-input audit to rebuilt or signed preview archives. The README continues to distinguish prepared-mode long load, the separate 1/100/1000-row Fluent/prepared/full-SQL phases, and the matched 120-second before/current comparison. It preserves remaining allocation/performance gaps and rejected alternatives without claiming that all possible measurable improvements have been exhausted.

## 6. Final document assessment

The current README resolves the previously pending product delivery claim using actual completed evidence. It keeps the original failure and partial artifact, explains the same-version retry accurately, distinguishes SQLite's carried-forward alias, and separates data-reader completeness fixes/local transfer observations from product or public-consumption failures. Earlier preliminary reviews and pause/run snapshots remain historical evidence rather than being overwritten as if they had observed the later success.

The containing Plan evidence commit's own CI and normal merge remain explicitly separate from product delivery; the README does not predict that future result or invent its own eventual commit identity. The links to independent reviews are to the intended companion reports, including this report. No source change, package rebuild, new performance campaign or adjustment of existing acceptance rules is required by this history review.

Review written (UTC): 2026-11-26T11:57:31.542103+00:00

## Storage mapping for the subsequent Plan copy

After this evidence review, the parent specified that captured GitHub job logs and the two signature-verifier stdout files will be stored losslessly compressed in the Plan copy because their original captured bytes contain trailing whitespace. The original logical source names used in this review identify the unmodified observations read above. Human-facing links in the Plan copy should resolve through the retained original/stored SHA-256 and readback-equality manifest to the compressed storage names. Consumer JSON/log hash bindings remain to their original bytes.

This is a storage mapping, not permission to trim captured evidence, rewrite receipts, relax whitespace gates or change `.gitattributes`. This reviewer did not compress or hash these files and makes no claim that the later storage operation has already passed; its actual manifest and readback receipt supply that separate proof.
