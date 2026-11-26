# DB-Exec-10: independent review of main release candidates

## Outcome and review scope

The two existing main-run candidate artifacts are internally consistent with the actual main impact plan, the merged product source tree, and their independent Native AOT consumer receipts. I found no mismatch among the inspected candidate identity, fingerprint, provider-isolation, and DTO-edit records. This is a **candidate delivery review**. The inspected records do not yet establish successful completion of the entire main CI run, official registry publication, accepted signed registry readback, or consumption from the public feed.

This review only read existing JSON, selected small execution logs, and the relevant fingerprint/module declarations. It did not run a build, test, benchmark, planner, workflow, package execution, hash computation, or archive operation. The archive/package/native byte checks are the already-recorded observations in `candidate-artifact-observations-01.json`; I compared their recorded values independently with the inventory and receipts without repeating those checks. No repository, frozen input, gate, or archived recovery file was changed.

The evidence set is the files in this delivery directory: `candidate-artifact-inventory-01.json`, `candidate-artifact-observations-01.json`, `product-main-impact-plan-01.json` and its `.receipt.json`, `merged-trees-and-main-runs-01.json`, both `candidate-{provider}/release.json` and `public-metadata.json`, both `consumer-evidence/candidate/{provider}.json`, and the six corresponding execute logs. The existing `release-observation-guide.md` supplies the source-derived final release procedure. The source references below are fixed to the measured public product commit, whose tree is the merged tree.

## 1. Source and actual-plan binding

| Item | Observed identity |
| --- | --- |
| Main workflow | [IzuSharp/Korda CI run 45807237435](https://github.com/IzuSharp/Korda/actions/runs/45807237435), main push |
| Main plan job | `139865593783` |
| Product merge and both candidate source commits | `7ff7b57b907b689defb880b8af62d83679608603` |
| Measured public product commit | `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` |
| Product tree in both release records and merge observation | `bc9087d843d8d741d83d44f53d0b2c5af26dcffc` |
| Candidate release records | `schema_version=1`, `source_dirty=false`, `rid=linux-x64` |
| Actual plan source-log SHA-256 | `5d010959b6c60cbcb2a55444524cd351d16851fe162536d722d0abe0f045c2c2` |
| Each selected version | `0.1.0-preview.4` |

The merge observation records parents `e063f2eb6e2e857e3f19f96bf263cae372651a27` and the measured public commit. Each release's package-level and native-level `source_commit` also equals the merge commit. The source tree is identical to the frozen implementation tree; this establishes source continuity across the normal merge. I did not independently refetch GitHub or recompute a Git tree in this review.

The inspected main plan selects `build_scopes=[interop,linux,postgresql,sqlite]`, `packages`, `candidates`, and `public_checks` for both providers, and two `releases` records, each with `database=true`. `deep=false`, `deferred=[]`, `module_packages=[]`, and `run_steps={}` are recorded. Its provider actions include `public.pack`, `public.consume-aot`, and `public.validate`, alongside the appropriate build/dependency/API/correctness actions. The Linux actions cover database/native/API/dependencies/regressions and Fluent/migrations/relations API checks; interop covers async and callbacks.

The reasons identify changed database/Fluent/native/interop/correctness/public-consumer files and separately register benchmark directories. The two performance module declarations contain directory ownership under `tests` but no `run` actions. The actual action lists contain no benchmark, calibration, profiling, or high-pressure campaign action. This review did not run the planner and does not add a new CI check. In the inspected run-state snapshot the main CI run remained `in_progress`; successful candidate artifacts alone cannot stand in for its still-required complete selected-job/Verify result.

## 2. Full-input and payload fingerprint reconciliation

The following values match across the actual plan, each candidate's extracted `public-metadata.json`, and the corresponding local frozen package's restored `korda/public.json`. The full-input values also match both candidate `release.json.inputs` maps and both frozen `release.json.inputs` maps.

| Provider | Full `inputs` | `payload_inputs` |
| --- | --- | --- |
| SQLite | `41ca933c2990a2184613e459c21440486549884634ef4678ad80e45bc6b50941` | `1c5b746255a494352fb38117fd7f4a94689230b8df2069626a7a475f7d8376ec` |
| PostgreSQL | `f1727c1a6fd91c691fd35559b6314764d05f611de5907b1cf62e6e3f4b5cbff3` | `5e7f3f23ecbadb9bccedfe7a3280c995d6f137c887b15c92dc88e3e852cdf3dc` |

The recorded unsigned-entry hash for `korda/public.json` is likewise unchanged between the frozen and main candidate packages: SQLite `c9ca2cc1b2d1be646dbf852f21d84df78ade0049f76d5b21d0e01f1f387c99e3`; PostgreSQL `4e700fd6aa3fc03cff1850a783228eb5614dfe1d9d3446bbdc45f397aa8767c0`.

These are package-input fingerprints, not package archive hashes or signatures. The inspected [`facts.py`](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/eng/ci/facts.py) constructs them from dependency-owned Git entries, package identity, relevant artifact/run declarations and pack declarations. Its `include_metadata` option distinguishes full input from payload input. An equal fingerprint is therefore meaningful source/package-input continuity, but does not make two separately produced ELF or NuGet archives byte-identical.

The original frozen release records read for this comparison are:

- `/workspace/scratch/fd78534029f7/builds/candidate-sqlite-02/public/release.json`, recorded by the original freeze with SHA-256 `4bbc8484fc7fbe1143a2a3359b0ba6742b21674d2e00eaf4f6e631dfdf32d2c2`.
- `/workspace/scratch/fd78534029f7/builds/candidate-postgresql-02/public/release.json`, recorded with SHA-256 `601022d6deb455fc3697334185f14cc8c6400af19ef8290e181723cc380c47f6`.

Their restored `consumer-workload/packages/korda.database.{provider}/0.1.0-ci.1/korda/public.json` records were also read directly. No listed source or package hash was recomputed for this review.

## 3. Candidate artifact and package isolation

| Property | SQLite | PostgreSQL |
| --- | --- | --- |
| Existing artifact ID | `15110013168` | `15109977803` |
| Artifact name | `candidate-sqlite` | `candidate-postgresql` |
| Artifact ZIP SHA-256 | `99e8ccb19abfc13c2d1d5866ddf7f6becf4f2adb61f42d1d93b240835cbeaba8` | `1454a0170757c3724ff8cb90cec69a0658a7c12e7765b414ef45dfbeec1a85f7` |
| Package ID | `Korda.Database.Sqlite` | `Korda.Database.PostgreSql` |
| Upload nupkg SHA-256 | `0a7b4f74fcf610e2600ca1a33eb55f93a039a5e7fa4ecc98b1d274e58b82673c` | `c6a3db442864eb7e2964c8bfd249c002e87a7ad39623145a7e0912a022a8e09f` |
| Native SHA-256 | `fa971d8476f1d74d414cd0e92f3c8ed561bc87887e51ec8c0f7f9de8f3dac482` | `81a6dd1fb338e56579f9176031cc680c078ccf3d88d60c4b39efaaf8d89ec4f8` |
| Recorded unsigned entries | 40 | 41 |
| NuGet dependency map | `{}` | `{}` |

The artifact inventory's digests match the archive observation values; each artifact belongs to run `45807237435`, branch `main`, and the merge SHA. The observed package/archive/native values match their corresponding release fields. Both artifacts were nonexpired in that inventory.

Each release contains exactly one `packages` entry. Its native entry is respectively `runtimes/linux-x64/native/libnw_database_sqlite.so` or `runtimes/linux-x64/native/libnw_database_postgresql.so`, with `abi_major=1`. Its unsigned entry map contains that provider's native image, managed provider assembly and build-transitive target, and no other provider's corresponding payload. Shared managed/runtime/generator payloads are present inside each package. There are no declared NuGet dependencies; this statement does not mean there are no platform/runtime library requirements.

The top-level `publish=[postgresql,sqlite]` is the shared planning scope. It does not mean either candidate bundles both provider packages. Package isolation is evidenced by the single-package record, the recorded entry inventory, empty dependency map, and separate consumer results below.

## 4. Existing candidate consumer evidence

Both consumer JSON files have `task=DB-API-01`, `result=passed`, the exact provider ID and `version=0.1.0-preview.4`. Each contains six commands: publish and execute for `scaffold`, `original`, and `edited`. All twelve command exit codes are zero. The publish commands use `-c Release -r linux-x64 -p:PublishAot=true`, the exact version and provider, and AOT warnings as errors; the execution commands invoke the published executable directly from a temporary consumer directory.

| Receipt property | SQLite | PostgreSQL |
| --- | --- | --- |
| AOT result rows | scaffold/original/edited, all `Aot=true` | scaffold/original/edited, all `Aot=true` |
| Project references | 0 in each row | 0 in each row |
| Declared checks | 19 scaffold; 21 original; 21 edited | 19 scaffold; 21 original; 21 edited |
| Page/detail SQL counter | 2 in each row | 2 in each row |
| Protocol submission counter | 0 in each row | 8 in each row |
| Native image through DTO edit | all three hashes equal release native hash | all three hashes equal release native hash |
| Changed original-to-edited source entries | only `Models.cs` | only `Models.cs` |
| Tutorial sources | four compiled sources; unchanged through edit | four compiled sources; unchanged through edit |

I also read each of the six execute logs: every file contains exactly one `DB_API_RESULT` line, and its provider, AOT, DTO, native hash and two counters match the corresponding receipt. No log hash was recomputed.

The checks cover a page plus a detail query, empty association/batch/page behavior, composite cursor boundaries, optional filters, the same immutable DTO through Fluent and parameterized SQL, typed aggregate/custom/nullable mappings, mutation omission versus null, stale versions, insert-returning/callbacks, rollback/error behavior, precancellation, and migration/scaffold behavior. Original and edited phases also record successful compilation and execution of generated scaffold entities and composite keys. These are the checks this consumer actually records, not a claim that it reruns every database contract test.

Both consumers record `same_native_after_dto_edit=true` and `tutorials_compiled_against_candidate=true`. Original and edited model hashes and executable hashes differ; scaffold hashes, tutorial sources, and native hashes remain equal within the provider. The `tutorial_package_sha256` values equal the respective candidate upload nupkg hash above, binding the tutorial consumption receipt to this candidate archive. The package README source hashes also equal the recorded `README.md` entry hashes.

`SqlExecutions=2` covers the sample's page/detail observation window, not all SQL in the consumer. `ProtocolSubmissions=8` for PostgreSQL is neither an RTT count nor the number of mandatory server waits. These counters cannot be substituted for the frozen protocol/phase measurements.

The evidence path is `consumer-evidence/candidate/`. Temporary directory names containing `korda-public` and the generic `tutorials_compiled_against_candidate` field do not establish public-feed restore. The existing orchestration's candidate mode uses the candidate feed. The public mode must be evidenced separately by its actual `--public` invocation and retained public receipt.

## 5. What carries forward from the frozen campaign

The exact source tree and full/payload input fingerprints carry forward to this merge and candidate package definition. The completed long campaign remains valid evidence for the retained frozen package/consumer/native identities and their implementation source. Candidate correctness and packaging evidence now separately exercise the newly built preview candidate artifacts.

The binary identity boundary is explicit:

| Provider | Frozen 0.1.0-ci.1 nupkg SHA-256 | Frozen native SHA-256 |
| --- | --- | --- |
| SQLite | `059a0df6b2ed428788b2bf5a7212dd4d73d43cd642eee0de152b975efaf03d6a` | `7b5291667a731d2b48647079ced0588003ba3d6c0f9edfb2648e3e581c2f0c53` |
| PostgreSQL | `46d5757c6dc48c721167476e2975f025b6884dc0c54b6956b9677a8eb4b29dec` | `21db7c5ee102163e42786e73f3a86081d367b049b133509a91dbb511edbf115f` |

These differ from the preview.4 hashes in section 3. The measured workload executables were SQLite `1ce8d74112e6dff217bb69d39c1f939474d04617b4f7961fb4e9b7edc5bf8953` and PostgreSQL `3e22e2ce1e9912f190b643b172360539d25d1b0558de3a253a3c19a67726c0b8`; the candidate business consumers are different programs with their own executable hashes. This review makes no claim that binary differences are confined to metadata.

Consequently, do not relabel the four 1800-second measurements, throughput/tails, allocation/GC/RSS results, refusal counts, or 373-input unchanged audit as measurements of these newly built or subsequently signed preview archives. They remain attributed to the frozen campaign, its declared host/load settings and binaries. Source continuity supports the relationship between tested implementation and delivery; it does not create new performance measurements, prove binary reproducibility, or close any remaining performance gap.

Likewise, the long campaign is not proof of official NuGet availability, registry signature acceptance, independent public-feed installation, or the complete current main CI conclusion. The candidate consumer results provide new package-consumption evidence, but still do not supply those publication facts.

## 6. Required final crosscheck when public artifacts arrive

For each selected provider, retain the actual selected-build/Verify/publisher outcomes and the `public-consumption-{provider}-0.1.0-preview.4` artifact. Its existence alone is insufficient because the existing workflow can retain partial failure evidence. Follow the existing procedure; do not dispatch a new workflow or add performance work.

Crosscheck the public artifact's release record and retained plan against this candidate's merge SHA/tree, exact provider/version, full/payload fingerprints, upload nupkg hash, native hash and unsigned-entry map. Inspect the official registry verification JSON for `verified=true`, `resume_allowed=true`, `unsigned_entries_equal=true`, mode `repository-signature-and-accepted-payload`, and the reviewed signature policy. `upload_sha256` must equal the corresponding candidate upload hash. Retain the actual registry archive hash separately; repository signing can change the archive hash while accepted unsigned entries remain equal.

Then inspect the public-mode Native AOT invocation and its final business receipt: exact provider/version; all six commands successful; all three AOT rows and zero project references; correct native payload; only the intended DTO source changed; and `tutorial_package_sha256` equal to the retained signed registry archive hash. Retain the standalone public smoke consumer's actual successful AOT/database result from the job log as well. These independent provider jobs do not by themselves demonstrate that a combined two-provider public consumer graph ran.

The existing supersession step may publish, reuse the same already-published exact version, or skip a superseded package. Preserve its actual state and reason. Only accepted official readback plus successful public consumption for the applicable selected version closes this final delivery boundary. No candidate-record inconsistency found in this review requires changing product source or rerunning the frozen campaign.

Review written (UTC): 2026-11-26T11:18:34.318039+00:00
