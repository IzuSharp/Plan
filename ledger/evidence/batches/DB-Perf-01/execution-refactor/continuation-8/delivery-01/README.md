# DB-Exec-11 normal merge and package delivery

## Observation status

The four frozen, serial 1,800-second Linux x64 Native AOT measurements and their
unchanged arithmetic/identity acceptance are complete. Their exact results,
remaining Dapper gaps, rejected alternatives and stopping scope are in the
[final local report](../final-report.md). This directory records the separate
normal merge, existing main CI and actual package delivery observations.

**Product and Design are normally merged, existing product main CI is successful,
and both independent `0.1.0-preview.4` packages have passed signed official NuGet
readback and actual public-package Native AOT consumption.** This was observed
on resumption at **2026-11-26 11:49:40 UTC**. The retained artifact reader passed
at 11:52:16 UTC; its result binds downloaded bytes to the actual CI receipts.
See the [machine-readable delivery summary](delivery-summary-01.json).

The initial PostgreSQL indexing attempt failed and remains preserved. The
already-completed second attempt reused the same candidate/version, skipped
upload, and passed readback and consumption. SQLite passed in its original
execution; the latest attempt's carried-forward SQLite job entry is not a
second SQLite run. The owner-requested [pause](pause-handoff-01.json) and later
[resumption](resume-handoff-01.json) are separate historical control records.
No performance measurement was restarted during delivery.

## Normal merges and exact source trees

| Repository / PR | Accepted PR head | Normal merge commit | Observed merge tree |
| --- | --- | --- | --- |
| [Korda #37](https://github.com/IzuSharp/Korda/pull/37) | `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` | [`7ff7b57b907b689defb880b8af62d83679608603`](https://github.com/IzuSharp/Korda/commit/7ff7b57b907b689defb880b8af62d83679608603) | `bc9087d843d8d741d83d44f53d0b2c5af26dcffc` |
| [Korda-Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) | `7b78cf98e29b5e4c67362a5c33d1fadbaf77ca55` | [`ca9348ad0b5cc93bc75c502460d8e1b75843d109`](https://github.com/IzuSharp/Korda-Design/commit/ca9348ad0b5cc93bc75c502460d8e1b75843d109) | `ffe6f94306985bacde708e75d1e93a29e096c724` |

The Git commit API was read after each merge. The product tree equals the
measured candidate tree exactly; the Design tree equals the reviewed final
documentation tree. [Merge receipts](merge-receipts-01.json) and
[tree/run observations](merged-trees-and-main-runs-01.json) preserve the actual
parents and the then-observed main run state. Merges used the expected PR heads
and the normal merge method. No force update, check bypass or impersonated
review approval was used.

The final Plan evidence checkpoint preceding this delivery record is
[`adcdc9172bf47a0df8fe5fcb8259357625526280`](https://github.com/IzuSharp/Plan/commit/adcdc9172bf47a0df8fe5fcb8259357625526280),
tree `e154ad070a7ca2dcc8078385afc6f22fa3c51b91`. Its existing
[PR check](https://github.com/IzuSharp/Plan/actions/runs/45805402319) passed.
The containing delivery-record commit's own later CI and normal merge are
observed separately in [Plan #34](https://github.com/IzuSharp/Plan/pull/34);
this file does not predict its own future check result or commit identity.

## What the existing CI selected and why

Product main [run 45807237435](https://github.com/IzuSharp/Korda/actions/runs/45807237435)
is the existing `CI` push run at the actual product merge. The
[main job log](product-main-plan.log.gz),
[extracted complete plan](product-main-impact-plan-01.json), and
[extraction receipt](product-main-impact-plan-01.receipt.json) preserve the
actual selection, including all changed-path reasons, inputs and payload inputs.
The previously required local `impact.py origin/main` result remains in
[impact-current-01.json](../impact-current-01.json).

| Actual selected scope | Why the existing graph selected it | Actual verification family |
| --- | --- | --- |
| `interop` | Changed ABI, callback/async admission and their registered dependants | Interop async and callback correctness |
| `linux` | Managed database/Fluent/relations and native Host/provider/query changes, plus their shared verification dependants | Native database build/API/dependency/regression and Fluent/API-tool/migration/relation checks |
| `postgresql` | PostgreSQL dependency closure and changed public database package inputs | Provider build/dependency/API/tests, independent public pack, package AOT consumption and validation |
| `sqlite` | SQLite dependency closure and changed public database package inputs | Provider build/dependency/API/tests, independent public pack, package AOT consumption and validation |

`modules`, `module_packages` and `deferred` are empty. The two independent
public database packages and public checks are selected. Registry reconciliation
selects both providers for publication; each independently resolves to
`0.1.0-preview.4`. Their different complete and payload fingerprints are retained
in the plan and package metadata. The plan also records benchmark-source
ownership, which adds no performance execution action. All benchmark,
calibration, profiling and mixed-load execution remained local Linux work.
No performance workflow, job, dispatch button, schedule or hidden load was added.

The existing plan/ownership checks, three security jobs, all four selected build
scopes and aggregate Verify completed successfully. Dependency review was
normally skipped on the main push, and the empty modules matrix was skipped.
The provider publishers are the existing reusable `release.yml` jobs in this
same run, not a separately dispatched workflow. The final run conclusion is
`success` on attempt 2; the original attempt's `failure` is preserved alongside
it in [attempt 1](product-main-attempt-1.json),
[attempt 1 jobs](product-main-attempt-1-jobs.json),
[attempt 2](product-main-attempt-2.json), and
[attempt 2 jobs](product-main-attempt-2-jobs.json).

Design main checks both passed on its actual merge:
[current database API design](https://github.com/IzuSharp/Korda-Design/actions/runs/45807224705)
and [historical English/contract acceptance](https://github.com/IzuSharp/Korda-Design/actions/runs/45807224623).
The prior PR checks and local unchanged document gates remain separately bound
to their original revisions. Historical Plan gates retain their fixed source
commits; this delivery does not change their rules or assign current execution
credit to a historical document check.

## Independently built candidate packages

[Candidate artifact metadata](candidate-artifact-inventory-01.json) and
[actual byte/receipt observations](candidate-artifact-observations-01.json)
bind each downloaded GitHub ZIP to its reported artifact digest, then each
package and native entry to its release record. Retained candidate text includes
`release.json`, `korda/public.json` metadata and all business consumption receipts
and logs under `candidate-sqlite/` and `candidate-postgresql/`.

| Package | Version | Upload archive SHA-256 | Native SHA-256 |
| --- | --- | --- | --- |
| `Korda.Database.Sqlite` | `0.1.0-preview.4` | `0a7b4f74fcf610e2600ca1a33eb55f93a039a5e7fa4ecc98b1d274e58b82673c` | `fa971d8476f1d74d414cd0e92f3c8ed561bc87887e51ec8c0f7f9de8f3dac482` |
| `Korda.Database.PostgreSql` | `0.1.0-preview.4` | `c6a3db442864eb7e2964c8bfd249c002e87a7ad39623145a7e0912a022a8e09f` | `81a6dd1fb338e56579f9176031cc680c078ccf3d88d60c4b39efaaf8d89ec4f8` |

Each release contains exactly its one provider package with no NuGet
dependencies. Candidate consumption passed six publish/execute commands across
scaffold, original DTO and edited DTO, producing three actual AOT result rows
with zero project references. Only `Models.cs` changed between original and
edited sources; native image and scaffold/tutorial sources remained identical.
See the [independent candidate review](review-release-candidates-01.md).

Candidate inputs and payload fingerprints equal the frozen measurement
producers' metadata. The release commit and preview package bytes remain
distinct from the measured `0.1.0-ci.1` packages. Native binaries were rebuilt
and their hashes also differ. The four long results continue to identify their
original frozen packages and workload executables; this source/input continuity
does not relabel them as measurements of the rebuilt preview packages.

## Official registry and public Native AOT observations

The successful artifact IDs are selected from the actual publisher upload logs,
not from duplicate artifact names. [The complete inventory](all-artifact-inventory-01.json)
retains both the partial and final PostgreSQL artifacts;
[selection](public-artifact-selection-01.json) and
[accepted metadata](public-artifact-inventory-01.json) bind the two accepted IDs
to the successful executions. [Actual byte/receipt observations](public-artifact-observations-01.json)
record the downloaded ZIP digests, signed nupkg/native hashes and retained text
hashes. The ZIP digests match the GitHub artifact metadata exactly.

| Provider | Successful public artifact | Signed registry archive SHA-256 | Actual public business result |
| --- | --- | --- | --- |
| SQLite | `15113598366` | `aefa5d1079170843469a5fc44a140dc2446126f3928d1a187581208ae8d44a8a` | `passed`; six commands, three AOT rows |
| PostgreSQL | `15114795427` | `04a5305f733acfb1cf6f287237b0752816746b737470c59b2308b7604dd08962` | `passed`; six commands, three AOT rows |

For both providers, registry records contain `verified=true`,
`resume_allowed=true`, `unsigned_entries_equal=true`, and mode
`repository-signature-and-accepted-payload`. The existing verifier accepted the
repository-primary signature, official NuGet service index, owner `dekueon` and
the unchanged policy certificate fingerprint. Its actual stdout/stderr and
verification JSON are retained beneath `public-{provider}/publication/registry-readback/`.
Upload and signed registry archive hashes differ as expected; native entry
hashes and accepted unsigned contents agree. The signature receipt's archive
hash equals the actual signed archive hash.

Both successful job logs execute `eng/ci/consume.py ... --public` and contain
an actual `B24_RESULT` with `dynamicCodeSupported=false`, real typed database
roundtrip, typed Fluent DTO query and retired-owner checks. The native image
hashes match the corresponding release records. The extracted
[smoke observations](public-smoke-observations-01.json) retain the exact runtime
payloads and source-log hashes.

The public business receipts and six logs per provider are retained beneath
`public-{provider}/publication/consumer-evidence/public/`. They prove standalone
Release Linux x64 AOT publish and direct execution for scaffold, original DTO
and edited DTO, each with `ProjectReferences=0`. The original/edited application
source map changes only `Models.cs`; executable hashes change while native,
scaffold and tutorial source hashes remain the same. All four extracted tutorial
sources are bound to their compiled hashes, and `tutorial_package_sha256` equals
the corresponding **signed registry** archive hash above. This establishes the
actual restored public package identity, independently of the earlier local
candidate-feed consumption.

These are two independently installed provider graphs. The release jobs did
not execute the combined two-provider graph. The sample's `SqlExecutions=2` and
provider protocol submissions describe only its page/detail observation window,
not all process SQL or a count of mandatory replies. The consumer's generic
`tutorials_compiled_against_candidate` field remains true in public mode; the
actual `--public` invocation and signed archive binding determine its scope.

### Retained initial failure and exact retry

PostgreSQL's original publisher job `139871492163` ran its indexing step from
11:16:21 to 11:44:22 UTC and ended with `TimeoutError`. The existing script has
a 30-minute retry budget and refuses a further 120-second sleep that would
exceed it, explaining the approximately 28-minute observed wait. No signature
or public AOT pass is inferred from this attempt. Its public AOT step was skipped.
The preserved [failure log](postgresql-publish-attempt-1.log.gz) and
[partial artifact observation](partial-artifact-observation-01.json) show that
artifact `15113029173` contains only `release.json` and `plan.json`.

The successful PostgreSQL retry job `139887660195` records
`publish=False, verify=True`; credentials and upload were skipped. It verified
the same `0.1.0-preview.4` at 11:47:41 UTC, then completed public AOT consumption
at 11:48:29 UTC. [The successful retry log](postgresql-publish-attempt-2.log.gz)
binds artifact `15114795427` to that result. There was no version bump,
candidate rebuild, relaxed policy or re-upload in this retry.

SQLite's original publisher `139871492392` verified its registry package at
11:42:05 UTC and completed public AOT consumption at 11:42:57 UTC. Its
[successful log](sqlite-publish-success.log.gz) binds artifact `15113598366`.
Attempt 2 lists carried-forward job alias `139887662491` with those original
timestamps. The records distinguish this from PostgreSQL's actual retry.

The [independent public delivery review](review-public-delivery-01.md) and
[independent release-history review](review-release-history-01.md) accompany
these observations. The [source-derived guide](release-observation-guide.md)
remains an earlier checklist and is not itself execution evidence.

The artifact reader [read_public_artifacts.py](read_public_artifacts.py) binds
downloaded ZIP, signed nupkg/native bytes and retained CI receipts. It does not
rerun cryptographic verification or AOT execution. Its
[independent pre-execution review](review-public-artifact-reader-01.md) records
three receipt-completeness corrections made before use. Those corrections were
not product/CI failures. The actual
[reader command](public-artifact-reader-01.command.json),
[stdout](public-artifact-reader-01.stdout), and
[stderr](public-artifact-reader-01.stderr) record exit 0. Cryptographic verification
and AOT execution remain attributed to the unchanged successful CI jobs.

Downloaded ZIP and nupkg binaries are omitted from this Git evidence directory;
their exact identities, official versioned download URLs and artifact IDs remain
in the retained inventories/verification records. All extracted text is kept. Raw GitHub job logs and signature-verifier stdout
are stored with lossless `.gz` compression to preserve their captured trailing
whitespace without changing the repository whitespace rules. The
[storage manifest](storage-manifest-01.json) maps every original logical path to
its stored path, byte count and SHA-256; decompressing a `.gz` yields the exact
reviewed original bytes. Review and machine receipt source paths retain those
original logical names. Consumer command logs remain directly readable.
The signed packages remain obtainable from the official exact-version registry;
GitHub candidate/public artifacts have their original finite retention windows.
This directory is not a binary-restoration bundle.

## Documentation reconciliation and retained observations

The [final continuity review](review-final-doc-continuity-01.md) found three
stale current-navigation headers and one current Design link. The
[navigation edit receipt](plan-navigation-edit-01.json) identifies the new root
README, current phase and execution-refactor entry sections. Previous checkpoint
text remains beneath explicit historical headings. The current implementation
link now selects the merged Design target path. Historical source pins are not
rewritten.

The [large-log transfer failure](log-transfer-failure-01.json) records a local
`E2BIG` command-argument limit while copying a successful CI log. Ordered smaller
writes retained the full log. [In-progress log availability](in-progress-log-unavailable-01.json)
records GitHub `BlobNotFound` responses before publisher jobs completed. Neither
observation is relabelled as a product, package or CI failure. The completed
campaign's failures/rejected experiments and immutable raw archive remain in
their original evidence locations.

This delivery closes only the measured and reviewed scope. Whole-framework
0 B remains unmet/unproven; the source still contains framework allocations.
The long workload is prepared mode, the ordinary Fluent/prepared/full-SQL
1/100/1000-row phases remain separate, and the before/current improvement is
the matched 120-second comparison. The evaluated quiet-close candidate failed
its prospective rule, and the earlier inline-completion candidate had an
ownership defect. Retaining the selected candidate does not establish that no
further measurable improvement can exist. No new performance run is credited
to this delivery record.
