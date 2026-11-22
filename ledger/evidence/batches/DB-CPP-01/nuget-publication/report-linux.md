# DB-CPP-01 — public NuGet delivery follow-up, Linux x64

**Status: publication preparation reviewed; public delivery pending.** The C++ database migration is already accepted. This separately authorized follow-up has not yet established a successful public package upload/readback, public four-cell consumer run, or HelloWorld withdrawal. The successful preparation checks below do not establish any of those pending outcomes.

The owner authorized delivery to the existing NuGet account `dekueon` through the existing GitHub trusted publisher: repository `IzuSharp/NativeWeave`, workflow `release.yml`, environment `nuget`. No browser sign-in, new account, new long-lived secret, or publisher-permission change belongs to this implementation. The [handoff](handoff-linux.md), [source binding](source-binding.json), [independent technical review](reviews/publication-source-review.json), and [pre-publication registry observation](public-registry-before.json) preserve the preparation evidence.

## Product and package scope

NativeWeave is one database product with PostgreSQL and SQLite providers. The twelve package IDs below are its previously accepted transitive dependency closure. A normal application installs its selected provider facade; NuGet restores the required shared components and that provider's precompiled native leaf. An application using both databases references both facades. No package consolidation, new database provider, ORM feature, API redesign, or performance work is included.

The native implementation remains C++20, with libpq for PostgreSQL and SQLite for SQLite execution. Public C# APIs, the C ABI, source generators, ordinary entity/DTO builds, database formats and the native payloads remain those accepted in the [migration report](../migration-report-linux.md). Only Linux x64 is accepted here. Application HTTP/gRPC hosting remains the application's choice; the retired HelloWorld demonstration is not part of this database closure.

| Package ID | Frozen version | Role | Verified public ZIP SHA-256 |
| --- | --- | --- | --- |
| NativeWeave.Core | `0.1.0-db-cpp.1.1` | Shared ownership and interop facade | Pending |
| NativeWeave.Interop.Abi | `0.1.0-db-cpp.1.1` | Shared ABI declarations | Pending |
| NativeWeave.Data | `0.1.0-db-cpp.1.1` | Shared database abstractions | Pending |
| NativeWeave.Data.Streaming | `0.1.0-db-cpp.1.1` | Shared streaming surface | Pending |
| NativeWeave.Database.Transactions | `0.1.0-db-cpp.1.1` | Shared transaction surface | Pending |
| NativeWeave.Query.Binding | `0.1.0-db-cpp.1.1` | Shared query binding | Pending |
| NativeWeave.Query.Generator | `0.1.0-db-cpp.1.1` | Shared compile-time convenience | Pending |
| NativeWeave.Database | `0.1.0-db-cpp.1.2` | Shared Database Host facade | Pending |
| NativeWeave.Database.Sqlite | `0.1.0-db-cpp.1.2` | SQLite application entry package | Pending |
| NativeWeave.Database.Sqlite.Native | `0.1.0-db-cpp.1.2` | SQLite precompiled native leaf | Pending |
| NativeWeave.Database.PostgreSql | `0.1.0-db-cpp.1.2` | PostgreSQL application entry package | Pending |
| NativeWeave.Database.PostgreSql.Native | `0.1.0-db-cpp.1.2` | PostgreSQL precompiled native leaf | Pending |

The original archive hashes and exact dependency edges are fixed in the [publication manifest](https://github.com/IzuSharp/NativeWeave/blob/4349b4998bed0724d277bb14857c72756fe3a624/packaging/releases/DB-CPP-01-nuget.json). NuGet repository signing changes the enclosing ZIP; the public ZIP hash must be recorded separately. Every unsigned entry, package version, dependency edge, repository commit and native payload must still match the accepted original. An existing exact version with different payload bytes is a conflict, not a successful resume.

## Source and artifact identities

The delivered native/package source and the publication automation source have different identities. Promoting the original archives does not rebuild them from the later publication-code commit.

| Input | Exact identity |
| --- | --- |
| Accepted C++ product and package source | `3badc05be503991b5591732629dd7e5b0dbad111`, [product PR21](https://github.com/IzuSharp/NativeWeave/pull/21) |
| Accepted product tree | `3264de79b73c8a89f1cac1eff57d0c0ff2c841c2` |
| Original successful main build | [44977773509](https://github.com/IzuSharp/NativeWeave/actions/runs/44977773509), attempt 1 |
| Original candidate artifact | `14738115742`, `nativeweave-database-linux-44977773509-1` |
| Original artifact size / SHA-256 | 6,169,499 bytes / `bb63f9fe71ea4c2f68dd63b748af3820c8bc0174199ce6fa7e2a92197f31e8b9` |
| Promoted artifact directory | `db-scope/prepared/candidate`; the separate `.clean.*` test packages are excluded |
| SQLite native payload SHA-256 | `35b7a51e844e7cfe936d8fea22dd42fa26fba0eeb0412bc5ba98cb51b2547384` |
| PostgreSQL native payload SHA-256 | `27df06d78b3226d09ca412530abd1013e6a86c299e5d0db028c7ae9e3789fb72` |
| Publication automation PR/head | [product PR23](https://github.com/IzuSharp/NativeWeave/pull/23), `4349b4998bed0724d277bb14857c72756fe3a624` |
| Reviewed publication tree | `b43259a919e2e9de789dc851fb32502bc7271d71` |
| Local reviewed publication commit | `762fe8bf6915271244792e9bff69939767e00229`; identical tree, different commit metadata |
| Completed migration evidence | [Plan PR27](https://github.com/IzuSharp/Plan/pull/27), merge `5be447a868be78713ada52f46cee16409f0edc13` |
| Publication evidence PR | [Plan PR28](https://github.com/IzuSharp/Plan/pull/28), draft at this checkpoint |

Original `local_unsigned_only` receipts remain historical producer records. They are not rewritten to claim NuGet publication. Public registry, signature, listing and consumer receipts are separate evidence.

## Observed preparation and remaining execution

The independent source review covered all ten publication changes and their fixed hashes. It independently reran 18 publisher and 9 consumer rejection controls, checked the original artifact and all twelve package digests, and confirmed that the existing migration verifiers, build workflow and business sample remain unchanged. These are same-team non-author technical checks, not another GitHub account's approval, and the synthetic controls did not upload a package or execute a business application.

The actual [PR publication preflight 44994423577](https://github.com/IzuSharp/NativeWeave/actions/runs/44994423577), job `137122267455`, passed. Its log observed `Existing NuGet publication switch: true`, successful rejection controls, and successful live source/artifact/package checks. The credential-bearing publisher was correctly skipped because this was a pull request. The [source binding](source-binding.json) distinguishes that observed preflight from the still-pending public mutations.

| Delivery gate | Observation at this preparation checkpoint | Final receipt / identity to record |
| --- | --- | --- |
| Product PR23 source review | Passed for head `4349b499…`, tree `b43259a9…` | [Review and source binding](source-binding.json) |
| PR publication preflight | Passed; existing enable switch observed `true` | [44994423577](https://github.com/IzuSharp/NativeWeave/actions/runs/44994423577) |
| Required product PR CI | Pending; [44994423565](https://github.com/IzuSharp/NativeWeave/actions/runs/44994423565) was in progress | Exact final jobs/steps and tested head: pending |
| Normal product merge | Pending | Actual merge commit/tree: pending |
| Product merged-main CI | Pending | Actual push/main run, attempt, jobs/steps: pending |
| Existing trusted-publisher exchange | Pending | Actual release run and exchange result: pending |
| Twelve package uploads or exact existing-version readbacks | Pending | `publication.json`, registry hashes, signatures, owner/listing results: pending |
| Four public PackageReference consumer cells | Pending | `consumer/receipt.json`, actual runtime and native-load results: pending |
| HelloWorld withdrawal | Pending | `helloworld-unlist.json`, final full version inventory: pending |
| Publication evidence PR28 | Draft; completion not claimed | Exact PR checks, normal merge and own main CI: pending |

The final successful migration CI does not establish these new public-delivery gates. The publication workflow requires database publication, public consumption and retirement outcomes independently; a successful upload alone is insufficient.

## Public consumer matrix

The new `eng/verify_nuget_public.py` uses the unchanged accepted `samples/api/packaging-domain/Program.cs`. Each cell creates a fresh project and empty package/HTTP caches outside the checkout. NuGet.org is the only source, fallback folders are disabled, and the selected provider uses an exact PackageReference. Each provider resolves ten accepted NativeWeave packages; their union is the twelve-package closure.

The controller checks actual restore metadata and dependency closure, every restored NativeWeave package's unsigned payload and real repository signature, and the exact signed `dekueon` owner and official certificate. It then performs normal managed build or Native AOT publish and executes typed entity, Fluent DTO and resource-retirement operations. Runtime receipts report the actually mapped native library and its hash. Native AOT additionally requires the real Linux x64 ELF, `dynamicCodeSupported=false` and the execution witness. No product-native compilation is performed.

| Database | Execution | Public restore / signed payload | Business operations / release | Actual mapped native hash | Result |
| --- | --- | --- | --- | --- | --- |
| SQLite | JIT | Pending | Pending | Pending | Pending |
| SQLite | Linux Native AOT | Pending | Pending | Pending | Pending |
| PostgreSQL 18 | JIT | Pending | Pending | Pending | Pending |
| PostgreSQL 18 | Linux Native AOT | Pending | Pending | Pending | Pending |

The accepted local-feed executions remain in the migration history. They are not substituted for this table. This preparation session had no local .NET/Clang execution; public runtime results must come from the actual release run. Public consumer subprocesses do not inherit NuGet/GitHub credentials or the runner's OIDC/runtime token channel.

## HelloWorld withdrawal

The [before observation](public-registry-before.json) records ten `NativeWeave.HelloWorld` versions, all listed. It is a pre-mutation inventory. A successful NuGet unlist removes normal discovery while retaining exact-version restore for existing consumers; this report does not promise permanent package deletion.

| Version | Listed before | Confirmed listed after | Withdrawal result |
| --- | --- | --- | --- |
| `0.1.0-preview.1` | `true` | Pending | Pending |
| `0.1.0-preview.2.1` | `true` | Pending | Pending |
| `0.1.0-preview.4.1` | `true` | Pending | Pending |
| `0.1.0-preview.5.1` | `true` | Pending | Pending |
| `0.1.0-preview.6.1` | `true` | Pending | Pending |
| `0.1.0-preview.7.1` | `true` | Pending | Pending |
| `0.1.0-preview.8.1` | `true` | Pending | Pending |
| `0.1.0-preview.9.1` | `true` | Pending | Pending |
| `0.1.0-preview.10.1` | `true` | Pending | Pending |
| `0.1.0-preview.11.1` | `true` | Pending | Pending |

The actual existing credential's unlist authorization is pending. No live scope was inferred from push permission. A real refusal, incomplete final registration inventory, or newly observed unattempted version must remain an incomplete withdrawal result even if database publication succeeds. The workflow does not silently alter publisher scopes.

## Application installation after confirmed public delivery

The following commands are intended for the exact published versions once the public gates above pass. They are not evidence that the versions are available at this checkpoint. Choose the provider used by the application:

```sh
dotnet add package NativeWeave.Database.Sqlite --version "[0.1.0-db-cpp.1.2]" --source https://api.nuget.org/v3/index.json
```

For PostgreSQL, select its facade instead:

```sh
dotnet add package NativeWeave.Database.PostgreSql --version "[0.1.0-db-cpp.1.2]" --source https://api.nuget.org/v3/index.json
```

The corresponding exact project reference is one of:

```xml
<PackageReference Include="NativeWeave.Database.Sqlite" Version="[0.1.0-db-cpp.1.2]" />
<PackageReference Include="NativeWeave.Database.PostgreSql" Version="[0.1.0-db-cpp.1.2]" />
```

Use both only when the application needs both providers. Ordinary entity, DTO or query changes rebuild C# and reuse the precompiled native package; consumers do not need a Rust or product C++ build. Native AOT retains its normal platform compiler/linker prerequisites.

## Maintainer reproduction and final receipt collection

Use the reviewed publication checkout with the accepted `3badc05…` object available in Git history. The [release workflow](https://github.com/IzuSharp/NativeWeave/blob/4349b4998bed0724d277bb14857c72756fe3a624/.github/workflows/release.yml) uses the existing `nuget` environment and `NuGet/login` exchange, not a browser session. Required PR checks must pass before normal merge. An explicit dispatch of the same workflow on main can resume the immutable release; previously existing versions still require exact verified readback.

Read-only original-source preparation requires GitHub access to the fixed Actions artifact:

```sh
python3 eng/publish_nuget.py preflight \
  --manifest packaging/releases/DB-CPP-01-nuget.json \
  --work-dir artifacts/nuget-publication
```

The following registry mutations run inside the authorized existing trusted-publisher job. Its temporary credential is supplied through `NUGET_API_KEY`, never as a command argument or recorded receipt field:

```sh
python3 eng/publish_nuget.py unlist-helloworld \
  --manifest packaging/releases/DB-CPP-01-nuget.json \
  --work-dir artifacts/nuget-publication
python3 eng/publish_nuget.py publish \
  --manifest packaging/releases/DB-CPP-01-nuget.json \
  --work-dir artifacts/nuget-publication
```

After all twelve versions have authenticated public readbacks, run the actual public consumers with SDK `11.0.100`, ordinary Linux Native AOT prerequisites and a disposable PostgreSQL 18 service selected by `NW_TEST_POSTGRES`. The output directory must be new:

```sh
python3 eng/verify_nuget_public.py \
  --release-record artifacts/nuget-publication/source/db-scope/prepared/candidate/release.json \
  --signature-policy artifacts/nuget-publication/signature-policy.json \
  --expected-source 3badc05be503991b5591732629dd7e5b0dbad111 \
  --owner dekueon \
  --output artifacts/nuget-publication/consumer
```

These commands document the reviewed entry points; this report draft did not execute them. The final evidence update must bind the actual release run/attempt and source, original and public archive identities, signed owner/certificate verification, four completed consumer cells and final HelloWorld inventory. Record failed or partially completed operations separately, then complete Plan PR28's own review, CI, normal merge and merged-main CI. Public delivery remains **pending** until those observations are available; the accepted migration remains unchanged.
