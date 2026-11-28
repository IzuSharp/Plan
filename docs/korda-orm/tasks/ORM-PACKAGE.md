# ORM-PACKAGE — seven fixed products and exact archive consumers

Status: `planned_candidate`; `implementation_authorized: false`.

## Fixed package boundary

Use the graph-pinned Design architecture, `implementation-spec.md`,
`generation-integration.md`, `mature-execution.md`, ORM-C05/ORM-C06 and provenance
policy. Package boundaries are decided here; the implementer does not choose a
new product split or silently swap the execution backend.

| NuGet ID | Shipped managed/build assets | Normal dependency closure |
| --- | --- | --- |
| `Korda.Orm` | net11.0 pure Core/language/render/declared dialect/neutral Schema assemblies, XML docs and public metadata | BCL only; no Dapper, ADO/provider, generator runtime, Java or native executor |
| `Korda.Orm.Execution` | The single net11.0 execution assembly, generated-mapping infrastructure and exact runtime adapter | Matching core product plus Dapper.AOT 1.1.0 runtime; no database driver or requirement to use Fluent/source generation |
| `Korda.Orm.PostgreSql` | PostgreSQL provider/metadata adapter | Matching Execution, Npgsql 11.0.0 and its actual closure only |
| `Korda.Orm.Sqlite` | SQLite provider/metadata adapter | Matching Execution, Microsoft.Data.Sqlite 11.0.0 and its declared SQLitePCLRaw/native closure only |
| `Korda.Orm.MySql` | MySqlConnector adapter with separate MySQL/MariaDB profiles | Matching Execution, MySqlConnector 3.0.0 and its closure only |
| `Korda.Orm.Generators` | `analyzers/dotnet/cs/Korda.Orm.Generators.dll`, required private helper dependencies and `buildTransitive` property registration | Optional build tooling; no `lib/` runtime payload, driver or runtime Roslyn dependency |
| `Korda.Orm.Schema` | net11.0 framework-dependent .NET tool, command `korda-orm-schema`, static acquisition adapters and offline emitter | Tool-owned closure of the three adapters and their drivers; not an application dependency |

Provider packages depend on the same Execution package. They must not each bundle
another assembly with the same Execution identity. Internal modules remain
independently buildable/testable; they are not individually published products.
The schema tool's multi-provider closure is intentional for explicit acquisition;
it must not leak into a provider or pure-core application.

`Korda.Orm.Execution` is independently usable: an application can supply a rendered
command/typed values, a `DbConnection` and explicit static factories without using
Fluent queries, the Korda generator or a Korda-specific provider package. Its
archive consumer must prove that use case.

## Exact internal assembly and module manifests

Every normal managed asset below is `lib/net11.0/<AssemblyName>.dll` plus the
matching XML file. The names are fixed; an implementation owner does not choose
a different split during packaging.

| Package module | `includes` | Initial managed assembly names |
| --- | --- | --- |
| `orm-package-core` | orm-contracts, orm-types, orm-language, orm-render, orm-postgres-dialect, orm-sqlite-dialect, orm-mysql-dialect, orm-mariadb-dialect, orm-schema, orm-advanced-types, orm-nested | Korda.Orm.Contracts, Korda.Orm.Types, Korda.Orm.Language, Korda.Orm.Rendering, Korda.Orm.Dialects.PostgreSql, Korda.Orm.Dialects.Sqlite, Korda.Orm.Dialects.MySql, Korda.Orm.Dialects.MariaDb, Korda.Orm.SchemaModel, Korda.Orm.AdvancedTypes, Korda.Orm.Nested |
| `orm-package-execution` | orm-execution | Korda.Orm.Execution |
| `orm-package-postgres` | orm-postgres-driver | Korda.Orm.PostgreSql |
| `orm-package-sqlite` | orm-sqlite-driver | Korda.Orm.Sqlite |
| `orm-package-mysql` | orm-mysql-driver | Korda.Orm.MySql |
| `orm-package-generator` | orm-generator | No lib asset; Korda.Orm.Generators under analyzers/dotnet/cs |
| `orm-package-schema-tool` | orm-schema-tool | Korda.Orm.SchemaTool and its private tool closure under tools/net11.0/any |

`orm-language` includes query/expressions/DML/relational leaves once. Source projects
are `src/Orm/<Module>/<AssemblyName>.csproj`, with the fixed exceptions
`Schema/Korda.Orm.SchemaModel.csproj`, `Generation/Korda.Orm.Generators.csproj`,
`SchemaTool/Korda.Orm.SchemaTool.csproj`, dialects under `Dialects/<Family>/`, and
provider projects under `Providers/<Family>/`. The optional Parser assembly is
not an initial mandatory payload; accepting it later does not create an eighth
public micro-package.

The generator's archive also contains exactly
`buildTransitive/Korda.Orm.Generators.props`. That file registers
CompilerVisibleItemMetadata for AdditionalFiles metadata `KordaOrmGeneration`.
Its exact content is:

```xml
<Project>
  <ItemGroup>
    <CompilerVisibleItemMetadata Include="AdditionalFiles"
                                MetadataName="KordaOrmGeneration" />
  </ItemGroup>
</Project>
```

The consumer explicitly supplies its input, for example:

```xml
<ItemGroup>
  <AdditionalFiles Include="schema/app.korda-schema.json"
                   KordaOrmGeneration="Incremental" />
</ItemGroup>
```

The generator reads `build_metadata.AdditionalFiles.KordaOrmGeneration` from
AnalyzerConfigOptionsProvider.GetOptions(file). Omitted or exact `Incremental`
means enabled; exact `None` means ignore that schema input. Any other value is
ORMGEN007. Do not glob every JSON file or run a target that connects to a database.
Physical CLI output uses None/omission of the corresponding AdditionalFile and
contains no DbRow attributes that would trigger duplicate mapping generation.

## Owned dependency staging in the existing runner

The current product runner assumes one standalone owned package. The new public
Core/Execution/provider dependency edges require the narrow ORM-CI extension
below; silently passing an empty dependency map would fail the existing
compatibility validator before restore. Preserve the existing runner and its old
product branch.

Each new orm-package entry sets `package_manifest` to its reviewed
`packaging/orm/<NuGetId>.json`. The manifest contains `ownedDependencies`, a map
from owned NuGet ID to `{ "module": "orm-package-...", "version": "candidate" }`
or a reviewed exact previously accepted version. `candidate` is the only token
and resolves to NW_VERSION for the first coordinated cohort. No ranges/floating
versions are accepted. `externalDependencies` maps external IDs to exact pinned
versions permitted in the nuspec. The initial owned edges are:

- Core, Generators and the tool archive with its private dependency payload: no owned NuGet edge.
- Execution: Korda.Orm → orm-package-core.
- Each provider: Korda.Orm.Execution → orm-package-execution; Core is transitive.

The tool bundles its own declared managed/native tool closure, not application
lib assets, and therefore does not acquire the provider packages as NuGet-owned
edges. It still records their source/module inputs and exact external versions.
The direct runtime Execution edge needs Dapper.AOT 1.1.0 only; that package's
net10.0 runtime group has no Dapper dependency. Dapper 2.1.100 belongs to the
original-SqlMapper/DynamicParameters compatibility fixture, not the default
runtime product. Provider pins remain Npgsql 11.0.0, Microsoft.Data.Sqlite 11.0.0
and MySqlConnector 3.0.0. The inspected net11 resolved SQLite closure is
Microsoft.Data.Sqlite.Core 11.0.0, SQLitePCLRaw.bundle_e_sqlite3,
SQLitePCLRaw.config.e_sqlite3, SQLitePCLRaw.core and
SQLitePCLRaw.provider.e_sqlite3 all at 3.0.5, and SQLite 3.53.4. Npgsql/MySqlConnector
in the inspected net11 closure add no other external runtime package. SDK
ILCompiler/ILLink 11.0.0 are build inputs, never runtime nuspec dependencies.

ORM-CI adds stage_owned_dependencies to the existing module_job path. It walks
this manifest DAG, produces each candidate dependency using its normal single-ID
pack entry into a separate directory, or reuses an exact accepted archive after
verifying its metadata/hash. It exposes a read-only NW_DEPENDENCY_FEED and
NW_DEPENDENCY_MANIFEST. NW_FEED continues to contain exactly the requested target
nupkg; do not put dependencies, manifests or logs into it.

The dependency manifest is schema_version=1 and contains packages in ordinal
ID order. Each item records id, version, module, origin (`candidate` or `published`),
source_commit, inputs, archive (relative filename within NW_DEPENDENCY_FEED),
upload_archive_sha256, unsigned_entries and dependencies. These digest/edge fields
reuse the compatibility validator's package-record spelling and meaning. It binds
each exact archive and its declared edges; absolute/escaping archive paths fail. The consumer creates a temporary
NuGet.Config with the target feed and this verified dependency feed, plus only the
explicitly permitted external closure. It restores into the isolated cache and
requires the resolved owned package set/versions to equal the manifest closure.
No project reference, unverified global-cache DLL or same-version different archive
can satisfy a dependency. Missing/wrong/undeclared archives fail before execution.

release.json retains schema_version=1 and contains the target plus its complete
owned closure. Each package entry has real nuspec-owned dependencies, source_commit,
archive hash and unsigned entries. The target source is current HEAD; an accepted
published dependency retains its own verified source provenance, not a fabricated
HEAD. The declared input fingerprint must match that dependency's accepted inputs.
Reuse compat.validate_closure on the whole graph. ORM-CI's new package_manifest
branch of validate_public computes the exact closure, checks both directories and
allowed external dependencies, and returns/publishes only the requested target.
The existing products retain their unchanged standalone branch.

Before publication, every owned dependency must already have a verified registry
archive. First-cohort publication is dependency-first; subsequent reviewed
manifests pin unchanged dependencies to their accepted versions instead of
republishing Core merely to force version equality. Publishing remains separately
authorized. The package consumer uses this same exact-version protocol for an
already-published root; it never silently substitutes the latest dependency.

Required CI fixtures: missing dependency, wrong version, wrong hash, undeclared
owned dependency, cycle, old-product unchanged behavior, and successful fresh-cache
Execution and provider archive consumers. Tests verify the target feed still has
one nupkg and no dependency archive is accidentally published as that target.

## Start, acceptance and file ownership

Start after `ORM-FOUNDATION`. Final aggregate acceptance requires the language,
expression/DML/relational/render modules, all four dialect tasks, generator,
schema tool, advanced/nested modules, three provider tasks, `ORM-DOCS` and
`ORM-CI`, exactly
as recorded in the graph. Each package can be built and consumed independently
as its own inputs become ready. Package work does not wait for the whole product
before testing the first archive.

Own `eng/orm-package/**`, `packaging/orm/**` and the package consumer fixtures
under the task's reviewed scope. The CI owner integrates shared registry entries;
module owners retain assembly/API semantics and root project settings. Use:

- `packaging/orm/<NuGetId>.json`: one manifest per product with package ID, public
  assembly names, source/metadata/include inputs, internal module list, dependency
  pins, license/NOTICE files and intended consumer command.
- `eng/orm-package/pack.py`: producer following the existing `NW_PACKAGE`,
  `NW_VERSION`, `NW_FEED`, `NW_INPUTS` protocol; reuse existing packaging helpers.
- `eng/orm-package/inspect.py`: archive/dependency/native-asset/public-API checks.
- `eng/orm-package/consume.py`: one exact-ID/version consumer lane per product.
- `packaging/orm/consumers/<NuGetId>/`: maintained consumer source and assertions;
  restored archives/caches/output go only under local `artifacts/`/temporary paths.

The product CI's `eng/ci/modules/README.md` defines that pack/consume protocol.
Do not rename it, introduce a second dispatcher or move routing into YAML.

## Manifest and dependency implementation

1. Use the exact public assembly names and archive paths below and in the central spec.
   A provider manifest contains its adapter only; Execution and Core are package
   dependencies. Include actual XML docs with every public managed assembly.
2. Pin external versions from the reviewed source/package inventory. Model-only
   consumers must not acquire a provider or Dapper dependency. Exclude Dapper.AOT
   analyzer/build assets from the runtime dependency edge; an application that
   explicitly opts into original Dapper interception can reference that tooling
   independently.
3. The generator targets netstandard2.0 with Roslyn Common/CSharp 4.14.0 private
   build references. Do not bundle Microsoft.CodeAnalysis assemblies or the host's
   System.Collections.Immutable beside the analyzer. Ship required private JSON
   parser dependencies beside it, never in application `lib/` or runtime targets.
4. The initial System.Text.Json 11.0.0 netstandard2.0 helper closure includes
   Microsoft.Bcl.AsyncInterfaces 11.0.0, System.IO.Pipelines 11.0.0,
   System.Text.Encodings.Web 11.0.0, System.Buffers 4.6.1, System.Memory 4.6.3,
   System.Runtime.CompilerServices.Unsafe 6.1.2 and
   System.Threading.Tasks.Extensions 4.6.3. Resolve/inspect their exact nuspec
   closure; an unexpected dependency is a failed manifest check, not permission
   to copy every restore-cache DLL. NETStandard.Library is a build reference and
   is not shipped as an analyzer DLL.
5. BuildTransitive props expose only the fixed AdditionalFiles metadata
   registration above. They must not run a database
   command, download tooling, write generated source into the project directory
   or enable an experimental compiler API.
6. Produce exactly one nupkg for the requested ID/version into `NW_FEED`. Include
   `korda/public.json` with the exact `NW_INPUTS` fingerprint. Preserve the existing
   distinction between metadata and managed-payload fingerprints.
7. Inspect every archive entry: reject traversal/absolute paths, raw research
   material, caches/logs, unintended sources, duplicate assembly identities and
   obsolete C++/Rust executor assets. SQLite's reviewed driver-owned native asset
   is expected and checked separately; it is not an old Korda executor.
8. Validate license expression, upstream notices and copied/adapted generator
   source notices. The package README describes this product and its exact
   dependency/feature limits. Do not claim unsupported IDE/OS/RID/database ranges.

## Exact archive consumption protocol

For each candidate, create a fresh isolated cache and consumer directory.
Use NW_FEED for the one requested target and the verified dependency staging
protocol above for its exact closure. Clear implicit package sources and restore the exact candidate version;
never use project references, an older global cache artifact, a floating version
or a locally built DLL in the final acceptance path.

Build, inspect dependencies, publish the intended Linux Native AOT application
and run the native binary. Confirm `RuntimeFeature.IsDynamicCodeSupported` is
false. Record a concise result; keep raw logs, nupkgs, binaries and caches local.
Do not upload research materials as package/Actions artifacts.

| Consumer | Required behavior and dependency assertion |
| --- | --- |
| Core | Construct/render fixed and runtime-composed SQL with typed layouts and a negative profile case; no driver/native library/Dapper/Roslyn in closure |
| Execution | Execute a manually declared C03 command through an application-supplied mature driver and explicit factories; no Fluent or generator required; runtime is the single packaged Execution assembly |
| PostgreSql | Native query with nullable parameters/results and selected advanced codec against its PostgreSQL fixture; no SQLite/MySQL driver |
| Sqlite | Native query and streaming/disposal fixture; inspect/load exact SQLite native asset on the claimed RID; no Npgsql/MySQL driver |
| MySql | One independently reported MySQL fixture and one MariaDB fixture; driver sharing does not combine support claims |
| Generators | Restore the analyzer archive in both Models and final consumer, compile DTO/schema and explicit registrar roots, inspect actual generated factories, run the native consumer, and confirm analyzer/Roslyn/JSON helper DLLs did not enter runtime closure |
| Schema tool | Install the exact tool archive into an isolated tool path; `--help`, `validate`, `generate` work offline, then selected acquisition lanes work; generated application publishes/runs natively |

Also consume PostgreSql+Sqlite and PostgreSql+MySql together in one application.
Require a single coherent Core/Execution assembly version; duplicate packaged
runtime identities or divergent dependencies fail. Test required/init/record DTOs
from another assembly through the packaged generator/runtime, not only monolithic
samples.

The tool itself is framework-dependent by design; do not call its successful
`dotnet tool run` a Native AOT tool test. The generated application remains subject
to the native gate. Likewise, successful restore is not archive-consumer acceptance.

## API, XML, selection and commands

Reuse the existing product API and packed-DLL validators. Compare compiled public
signatures/nullability/defaults, shipped DLLs and XML docs for source/generator/API
changes. Metadata-only edits verify nupkg ID/version/README/description and
fingerprints without unrelated API/database work. Re-run the documentation task's
real examples against candidate archives; a project-reference example pass is not
a substitute.

```sh
NW_PACKAGE=Korda.Orm NW_VERSION=<candidate> NW_FEED=<local-feed> NW_INPUTS=<fingerprint> \
  python3 eng/orm-package/pack.py
python3 eng/orm-package/inspect.py --package <candidate.nupkg>
NW_PACKAGE=Korda.Orm NW_VERSION=<candidate> NW_FEED=<local-feed> \
  python3 eng/orm-package/consume.py
```

The registry's pack and consume command arrays are respectively
`["python3","eng/orm-package/pack.py"]` and
`["python3","eng/orm-package/consume.py"]`; both read the existing NW_* identity/feed
protocol. consume.py additionally accepts the local explicit triple
`--package ID --version VERSION --feed PATH`, but all three must be supplied and
must agree with any runner identity variables. Dependency staging uses the two
NW_DEPENDENCY_* inputs above. The owner implements the exact product IDs from the
manifest table. Reject missing/mismatched environment/arguments instead of
silently choosing defaults. Shared input changes select actual shipped consumers;
provider-local changes select that provider's package and real dependents only.

Stop at reviewed candidate archives and their scoped acceptance. No publication,
release attachment, merge, old-product replacement or new package split is
implicitly authorized by this task.
