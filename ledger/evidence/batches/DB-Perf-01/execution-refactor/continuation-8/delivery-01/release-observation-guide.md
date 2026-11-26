# DB-Exec-10: normal main release observation guide

## Scope and identity

This is a source-derived observation guide, not a report that publication has already succeeded. It was prepared by reading the existing workflow and consumer implementation only. No build, test, benchmark, workflow dispatch, publication, or repository mutation was performed for this guide. Archived campaign evidence was not changed.

Reviewed product source: public candidate `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`; local checkout `/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-korda`, local commit `040911c5abdee740c0cd9fbf8295bf511c9cc69d`, previously established source tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc`. The parent reports that normal merge commit `7ff7b57b907b689defb880b8af62d83679608603` has that same tree, and main CI run `45807237435` is in progress. Those last two observations were supplied by the parent; this review did not fetch GitHub run state.

Observe the existing **CI** main-push run. `release.yml` is a reusable workflow called by CI's `publish` matrix; it is not a separate dispatch that needs triggering. Distinguish each provider's independently calculated preview version. Do not infer release versions from the measured local `0.1.0-ci.1` packages or assume the providers have the same preview number.

## 1. Main plan and the prerequisite correctness gate

Read the actual `plan` job's `plan_run.py` output and step summary. The full plan is printed to the log; the reusable-workflow output omits `reasons`. `artifacts/plan.json` is materialized by downstream jobs and retained in the public-consumption artifact. There is no separately declared plan upload in the plan job.

| Observed field or job | Required interpretation |
| --- | --- |
| Run `event`, `head_sha`, branch and repository | Main push in `IzuSharp/Korda`; record the actual merge SHA. Do not substitute the PR head SHA. |
| `inputs.sqlite`, `inputs.postgresql` | Full package input fingerprints used for public registry reconciliation and release identity. |
| `payload_inputs.sqlite`, `payload_inputs.postgresql` | Fingerprints excluding metadata inputs; retain separately from full `inputs`. |
| `packages`, `public_checks`, `build_scopes`, `actions`, `reasons` | Establish what this actual diff and main registry reconciliation selected and why. Do not infer the plan solely from changed filenames. |
| `candidates`, `releases` | `releases` contains `{module, database}` records for registry-pending packages. Main reconciliation checks registered package fingerprints, so a release selection can include unpublished changes beyond the immediate diff. |
| `versions[module]` | Use this exact version throughout candidate, push, readback, and consumer records. A pending package gets the next recognized `0.1.0-preview.N`; a nonpending package can have the CI-only default. |
| `plan`: **Validate tracked ownership and CI contracts** | Existing index check, Tooling tests and `git diff --check` must succeed. |
| `build` / **Run {scope} actions** | Selected module actions must succeed. For each selected public database candidate, the registered chain is `public.pack` → `public.consume-aot` → `public.validate`, after the provider build. The first consumption uses the local candidate feed. |
| `verify`: **Require selected jobs and verified package artifacts** | Checks plan/security success, selected build/modules success, and required nonexpired candidate artifacts. This gate does not itself prove registry publication or public NuGet consumption. |

The existing `publish` condition also requires successful Verify, main push, the expected repository, nonempty `releases`, and `NUGET_PUBLISH_ENABLED == 'true'`. If publication is skipped, establish which actual condition caused it. A successful main correctness gate with a skipped publisher is not evidence of a new preview delivery.

Source: [CI](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/.github/workflows/ci.yml), [build](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/.github/workflows/build.yml), [plan_run.py](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/eng/ci/plan_run.py), [impact.py](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/eng/ci/impact.py), [database_plan.py](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/eng/ci/database_plan.py), [fingerprint construction](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/eng/ci/facts.py#L22-L43).

## 2. Artifact inventory

| Artifact name | Producer and purpose | Retention |
| --- | --- | --- |
| `candidate-sqlite` | SQLite build job's **Retain independently verified package**; contents of `artifacts/public/`, including `release.json`, `feed/`, and candidate consumer evidence. | 14 days |
| `candidate-postgresql` | PostgreSQL equivalent, independently built and consumed. | 14 days |
| `public-consumption-sqlite-{actual-version}` | SQLite publisher, after `verify=true`; release record, plan, signed registry package/readback verification, and public consumer receipts/logs. | 30 days |
| `public-consumption-postgresql-{actual-version}` | PostgreSQL equivalent. | 30 days |
| `diagnostics-{scope}-{run_id}` | Build failure diagnostics where that upload condition applies; not a release acceptance artifact. | 7 days |
| `module-{scope}-{run_id}` | Other selected module checks where applicable; not a substitute for either provider candidate. | As declared by the build workflow |

Release downloads `candidate-{module}` into `artifacts/publication`. Public artifact inputs are `artifacts/publication/release.json`, `artifacts/plan.json`, `artifacts/publication/registry-readback/**`, and `artifacts/publication/consumer-evidence/public/**`. Inspect the actual artifact's relative paths: the common upload root can produce `publication/...` alongside `plan.json`. Do not reject a valid artifact merely for that prefix.

The public artifact upload uses `always()` when `verify=true`. Therefore an artifact can contain partial failure receipts. Its existence is not sufficient: inspect job/step conclusions and final receipt values.

## 3. Candidate package identity and fingerprint binding

The release step **Verify the tested tree, package allowlist and bytes** runs `validate_public.py` before acquiring a NuGet credential. A successful step establishes the following checks against the actual workflow checkout and plan:

| Record | Fields to retain and cross-check |
| --- | --- |
| `release.json` | `schema_version`, `source_commit`, `source_tree`, `source_dirty=false`, `rid`, `inputs`, `packages`. `source_commit` must be the current workflow checkout, and the tree must be its tree. |
| `packages[0]` | Exactly one allowlisted ID: `Korda.Database.Sqlite` or `Korda.Database.PostgreSql`; exact `version`; empty `dependencies`; `source_commit`; `repository`; `upload_archive_sha256`; `unsigned_entries`; `native`. |
| `feed/{PackageId}.{version}.nupkg` | Exact expected archive set; hash equals `upload_archive_sha256`; no extra provider or package substituted into the feed. |
| Archive `korda/public.json` | `inputs == release.inputs[module]`; `payload_inputs == plan.payload_inputs[module]`. Keep the two fingerprint roles separate. |
| Archive nuspec | Exact package ID/version, source repository/commit provenance and no NuGet dependencies. |
| Native record and manifest | `native.path`, `native.sha256`, `native.rid`, `native.abi_major`, `native.source_commit`; manifest provenance and the corresponding Linux x64 ELF payload. |

`native.source_commit` preserves the original native build's provenance. `korda/manifest.json` also records the current `packagingProducerCommit`. Do not require every provenance field to equal the packaging commit without examining whether an existing native artifact was legitimately reused. The verifier binds each field to its declared role.

The merge source tree can equal the measured candidate tree while release package bytes differ: preview version and merge-commit metadata differ, and NuGet applies repository signing. The existing campaign remains a measurement of its frozen packages/AOT consumers. The release checks establish source/package delivery and public consumption, not a rerun of that performance campaign on the signed preview.

Source: [validate_public.py](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/eng/ci/validate_public.py), [bundles.py](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/eng/ci/bundles.py#L86-L187).

## 4. Supersession, push, and actual registry readback

The step **Check for superseding package changes** compares the planned package fingerprint with latest main and the official registry head. Its log prints `{module}: publish={True|False}, verify={True|False}`.

| `publish` / `verify` | Meaning and required observation |
| --- | --- |
| `True` / `True` | Publish the planned version, then require signed registry readback and public consumption. |
| `False` / `True` | The exact planned version/fingerprint is already present. Push is skipped; readback and public consumption still run and can establish delivery. |
| `False` / `False` | Superseded package inputs, or matching published inputs under a different version. This run does not perform the readback/consumer proof for its planned version. Identify the appropriate current run/version before claiming completion. |

A registry version that advanced incompatibly since planning causes an error; it is not silently accepted. Preserve the actual reason rather than changing versions or bypassing checks.

For each provider observe these steps in the actual reusable publisher:

1. **Verify the tested tree, package allowlist and bytes** succeeds.
2. **Check for superseding package changes** produces the state above.
3. **Push verified preview to nuget.org** succeeds when required. `--skip-duplicate` by itself is not acceptance.
4. **Wait for indexing and verify signed registry package** succeeds and prints `Verified {PackageId} {version}`.
5. **Consume the public database packages in Native AOT** succeeds.
6. **Preserve actual registry bytes and public consumption receipts** succeeds, and its artifact is retained.

The readback step downloads the exact official flat-container URL, allowing up to the existing 30-minute indexing deadline with 404 retries. It retains the actual downloaded `.nupkg`, `{PackageId}.verification.json`, and signature verifier logs under `registry-readback/{PackageId}/verify.stdout` and `verify.stderr`.

Required verification JSON values:

| Field | Expected value or relationship |
| --- | --- |
| `package`, `version`, `source_commit`, `download_url` | Exact selected ID/version, release source commit, and official `https://api.nuget.org/v3-flatcontainer/...` URL. |
| `verified`, `resume_allowed`, `unsigned_entries_equal` | All `true`. |
| `mode` | `repository-signature-and-accepted-payload`. |
| `upload_sha256` | Equals candidate `upload_archive_sha256`. |
| `registry_sha256` | Hash of the retained downloaded archive. It need not equal the upload archive hash because the registry signs the package. |
| `signature.verified`, `signature.archive_sha256` | `true`; signed archive hash equals `registry_sha256`. |
| `signature.route`, `service_index`, `owners`, `certificate_sha256` | Match the existing reviewed signature policy, not an inferred or newly relaxed identity. |

Signature verification runs `dotnet nuget verify --all --certificate-fingerprint ... --verbosity detailed --force-english-output`. The implementation additionally checks exactly the repository signature route, service index, owner set, certificate fingerprint and subject. The current policy expects route `repository-primary`, the official NuGet v3 index, owner `dekueon`, and certificate SHA-256 `1f4b311d9acc115c8dc8018b5a49e00fce6da8e2855f9f014ca6f34570bc482d`. Consult the recorded source policy if investigating a failure; do not bypass it. Unsigned accepted entries must match exactly, including native payload and provenance. HTTP 200 and a successful push alone are insufficient.

Source: [release.yml](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/.github/workflows/release.yml#L54-L144), [registry.py](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/eng/ci/registry.py#L70-L95), [registry verifier](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Verification.Compatibility/compatibility.py#L316-L400), [signature policy](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/tests/Verification.Compatibility/signature-policy.json).

## 5. What proves actual public NuGet Native AOT consumption

The release command is `eng/ci/consume.py ... --public`. It creates application projects outside the source tree, uses exact public PackageReference versions and an isolated application package cache, and does not add the candidate feed. Only SDK package families can use its warm fallback cache; Korda packages cannot. Inspect the actual command and public evidence path to distinguish this from the earlier candidate-feed checks.

### Standalone package smoke consumer

The selected graph is published with `-c Release -r linux-x64 -p:PublishAot=true`, restored Korda identities/versions are checked against exactly the selected graph, and `B24Consumer --require-aot` is executed. The job log must contain a successful `B24_RESULT` JSON with the expected provider, `dynamicCodeSupported=false`, checks including `actual-native-aot`, the typed real-database round trip and Fluent DTO query, and the native library receipt (`file`, `sha256`). This generic smoke result is primarily in the workflow log; do not invent a separate archived B24 receipt file.

Each release record contains one provider. `consume.py` runs only graphs whose package set is a subset of that record: the SQLite job runs the SQLite graph and the PostgreSQL job runs the PostgreSQL graph. The combined graph requires both IDs and is skipped by these independent release jobs. Successful individual public consumers prove independent installability; they do not prove that this release workflow executed a combined public-package graph or the entire broader `tests/Packaging.Domain` harness.

### Business workflow, tutorials, scaffold and DTO edit

Expect `consumer-evidence/public/sqlite.json` or `postgresql.json`, plus six corresponding logs: `{provider}-{scaffold|original|edited}-{publish|execute}.log`. Job log markers are `RUN orders {Sqlite|PostgreSql} {revision} {stage}`. Every revision publishes a standalone Release Linux x64 AOT executable and executes it against the real provider. The PostgreSQL publisher supplies its existing PostgreSQL service; SQLite uses the real sqlite3-backed provider.

| Receipt data | Required proof |
| --- | --- |
| `task`, `result`, `package`, `version` | `DB-API-01`, `passed`, exact provider ID and preview version. An interim receipt lacking final `result=passed` is not sufficient. |
| `commands` | Six entries: publish and execute for scaffold/original/edited; all `exit_code=0`, retaining the exact commands, log names, elapsed seconds and log SHA-256. |
| `rows` | Three rows with `Phase` scaffold/original/edited, expected `Provider`, `Aot=true`, corresponding `Dto`, and `ProjectReferences=0`. |
| `Checks` | The implementation's required business checks: pagination/cursors/empty batches, same DTO through Fluent and parameterized SQL, typed aggregates and mappings, insert/rollback/cancellation semantics, migrations and scaffold writing. Original/edited also require both scaffold compile-and-execute checks. |
| `SqlExecutions`, `ProtocolSubmissions` | `SqlExecutions=2` is the sample's page/detail observation window, not the entire consumer's SQL count. SQLite requires zero protocol submissions; PostgreSQL requires at least two. Submission count is not an RTT or required-reply count. |
| `NativeSha256` | Matches the actual restored package's native entry and published native image. Compare with the matching release `native.sha256`. All three revisions use the same native image. |
| `ModelsSha256`, `ExecutableSha256`, `Sources`, `ScaffoldSha256` | The original/edited DTO source and AOT executable hashes differ; only `Models.cs` changes in the source map, while scaffold sources and native image stay identical. |
| `tutorials`, `TutorialSources`, `tutorial_package_sha256` | Four extracted tutorial sources are compiled; original/edited tutorial source hashes match. Compare the actual restored archive hash `tutorial_package_sha256` with the retained registry readback's `registry_sha256` to bind consumption to the signed public archive. |
| `tutorials_compiled_against_candidate`, `same_native_after_dto_edit` | Both `true`. The former is the existing generic field name even in public mode; the workflow command `--public` and evidence path establish public consumption. Do not rename its meaning without checking those facts. |

The consumer validates an ELF executable without a companion managed executable DLL, invokes that executable directly, and requires exactly one `DB_API_RESULT` business receipt per run. These facts, successful AOT publish/execute commands, exact package restore selection, native hashes and public restore mode form the public consumption proof. A `dotnet restore` log alone does not.

Source: [consume.py](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/eng/ci/consume.py), [smoke consumer](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/samples/api/packaging-domain/Program.cs), [business consumer orchestration](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/eng/ci/orm_experience.py#L120-L324).

## 6. Minimal final delivery record

For each selected provider retain the main CI URL/run ID/head SHA, actual plan version and fingerprints, selected build/Verify/publish conclusions, candidate and public artifact IDs, release source commit/tree, upload and registry archive hashes, signature acceptance fields, native hash, public business receipt result and all three AOT rows. Record actual skipped/superseded behavior separately. Preserve any failed attempt instead of replacing it with the eventual pass.

The completed delivery claim requires the applicable main plan and correctness gate, verified candidate bytes, accepted signed official registry readback, and successful fresh public-package AOT consumption for each provider. This guide adds no performance work to CI and supplies no claim of additional benchmark results.
