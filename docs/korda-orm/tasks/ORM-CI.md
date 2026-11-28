# ORM-CI — register exact module ownership in the existing product runner

Status: `planned_candidate`; product implementation is not authorized.

## Inputs and scope

Start and accept registry scaffolding after Foundation. Read the graph-pinned
Design architecture/contracts/validation and product `eng/ci/modules/README.md`,
impact.py, catalog.py, worker.py and existing module JSON. The inspected product
commit is 36bd5ba169b628ba4d61dd9fe260eaef5ff15599; reconcile any subsequently
reviewed changes before applying the fixed entries. Do not create another runner.

Own `eng/ci/modules/orm.json`, narrowly required eng/ci selection integration,
`tests/Tooling/test_orm_impact.py`, root solution/build registry integration and
workflow orchestration. Module workers own their local verify scripts. Foundation
creates project files initially, then hands shared root ownership to this task.
No historical database/Rust/Server graph or acceptance state is rewritten.

## Exact module catalogue

Use these module IDs, not dotted variants. Source and test roots are repository
relative; an entry ending `/` is a directory prefix. The exact command arrays below override any inferred filename; do not generate
verify.py wrappers for modules whose packet fixes check.py or check.sh. Resources
for ordinary managed/AOT checks are `["dotnet"]`; database lanes additionally
request only their own declared service resource through existing Action support.

| Module ID | Source root / special ownership | Test root / command | Extra semantic dependencies |
| --- | --- | --- | --- |
| orm-contracts | src/Orm/Contracts/ | tests/Orm/Contracts | none |
| orm-types | src/Orm/Types/ | tests/Orm/Types | orm-contracts |
| orm-language | Language project file only; includes next four modules | no duplicate aggregate test command | query/expressions/dml/relational includes |
| orm-query | src/Orm/Language/Query/ | tests/Orm/Query | contracts, types |
| orm-expressions | src/Orm/Language/Expressions/ | tests/Orm/Expressions | contracts, types |
| orm-dml | src/Orm/Language/Dml/ | tests/Orm/Dml | query, types |
| orm-relational | src/Orm/Language/Relational/ | tests/Orm/Relational | query, expressions |
| orm-render | src/Orm/Rendering/ | tests/Orm/Rendering | language, types |
| orm-postgres-dialect | src/Orm/Dialects/PostgreSql/ | tests/Orm/Dialects/PostgreSql | contracts, types, language, advanced-types, nested |
| orm-sqlite-dialect | src/Orm/Dialects/Sqlite/ | tests/Orm/Dialects/Sqlite | contracts, types, language, advanced-types, nested |
| orm-mysql-dialect | src/Orm/Dialects/MySql/ | tests/Orm/Dialects/MySql | contracts, types, language, advanced-types, nested |
| orm-mariadb-dialect | src/Orm/Dialects/MariaDb/ | tests/Orm/Dialects/MariaDb | contracts, types, language, advanced-types, nested |
| orm-schema | src/Orm/Schema/ | tests/Orm/Schema | contracts, types |
| orm-execution | src/Orm/Execution/ | tests/Orm/Execution | contracts, types, language, render, schema |
| orm-generator | src/Orm/Generation/ | tests/Orm/Generation | contracts/schema declarations as linked input; execution factory API; build-only dependency |
| orm-postgres-driver | src/Orm/Providers/PostgreSql/ | tests/Orm/Providers/PostgreSql | execution, schema, advanced-types, postgres-dialect |
| orm-sqlite-driver | src/Orm/Providers/Sqlite/ | tests/Orm/Providers/Sqlite | execution, schema, advanced-types, sqlite-dialect |
| orm-mysql-driver | src/Orm/Providers/MySql/ | tests/Orm/Providers/MySql | execution, schema, advanced-types, mysql-dialect, mariadb-dialect |
| orm-advanced-types | src/Orm/AdvancedTypes/ | tests/Orm/AdvancedTypes | contracts, types, language |
| orm-nested | src/Orm/Nested/ | tests/Orm/Nested | contracts, types, language, advanced-types; no runtime Execution/Rendering reference |
| orm-schema-tool | src/Orm/SchemaTool/ | tests/Orm/SchemaTool | schema, three drivers and shared neutral generation emitter |
| orm-parser | src/Orm/Parser/ | tests/Orm/Parser | language, render, schema; optional |
| orm-oracle | eng/orm-oracle/ | tests/Orm/Conformance | contracts; native conformance consumers also declare the modules actually used |
| orm-docs | samples/orm/ executable samples only | samples/orm/check.sh | actual package/source dependencies per sample |
| orm-integration-{postgres,sqlite,mysql,mariadb} | test-only entries | tests/Orm/Integration/check.py --profile <profile-id> | only selected driver/dialect plus common language, generation, advanced/nested |
| orm-performance | benchmarks/Orm/ | explicit manual command in performance packet | integration inputs; no ordinary PR timing run |

In the dependencies column, short names expand to `orm-<name>`. Literal managed
ProjectReferences are read from Git by the existing runner; add depends for linked,
conditional, generated or runtime-loaded inputs invisible to that analysis. Do not
invent a reverse Rendering edge on dialects or on Nested. Generator test projects
consume Execution, but runtime Execution does not depend on the generator.

Language's single project is an aggregate with includes. Source ownership of each
language directory stays at the leaf. A leaf edit reaches real assembly consumers
and package acceptance; it does not automatically run independent sibling test
suites just because they share a shipped DLL. Register shared project-level inputs
on the aggregate. Tests changing only a fixture select its owning check.

The shared orm-mysql-driver source entry has two existing-runner Action records,
one for mysql-8.4/KORDA_TEST_MYSQL and one for mariadb-11.8/KORDA_TEST_MARIADB. Each
action invokes the packet's single-profile check.py and requests only its service.
Family-only fixtures live in separate MySql and MariaDb subdirectories under the
driver test root, owned by test-only orm-mysql-driver-tests and
orm-mariadb-driver-tests entries respectively. Exclude those subdirectories from
the shared test-prefix ownership; keep common test sources on the shared module.
A shared source/common-test edit reaches both actions; a family fixture reaches
only its owning action. Use the existing registry source/test distinction and
Action resources, without a second dispatcher or a wrapper that silently runs both.

### Exact ordinary command arrays

| Modules | run array |
| --- | --- |
| contracts/types/query/expressions/dml/relational/render | `["python3","tests/Orm/<Contracts|Types|Query|Expressions|Dml|Relational|Rendering>/verify.py"]`, choosing the listed matching directory |
| four dialects | The corresponding packet's `python3 tests/Orm/Dialects/<family>/verify.py` command; preserve its exact fixture flags |
| orm-execution | `["python3","tests/Orm/Execution/check.py","--mode","native"]` |
| orm-postgres-driver | `["python3","tests/Orm/Providers/PostgreSql/check.py","--mode","native","--connection-env","KORDA_TEST_POSTGRES"]` |
| orm-sqlite-driver | `["python3","tests/Orm/Providers/Sqlite/check.py","--mode","native"]` |
| orm-mysql-driver | One owned check.py wrapper invokes its exact mysql-8.4 and mariadb-11.8 native lanes; family-specific test entries invoke only the matching `--profile`/connection-env |
| orm-schema | `["bash","tests/Orm/Schema/check.sh"]` |
| orm-generator | `["bash","tests/Orm/Generation/check.sh"]` |
| orm-schema-tool | `["bash","tests/Orm/SchemaTool/check.sh","--offline"]`; four explicit acquisition entries use `--provider postgresql|sqlite|mysql|mariadb` and only their service |
| orm-docs | `["bash","samples/orm/check.sh","--case","render-only"]` plus separately registered real sample lanes from ORM-DOCS |
| orm-oracle | `["python3","tests/Orm/Conformance/verify.py"]`; Java regeneration remains explicit |
| advanced-types/nested/parser | Exact verify command from its owning packet; native/data lanes remain separate from network Integration |

Generator links portable Schema Model/Format/Generation source; it does not
ProjectReference net11 SchemaModel. SchemaTool references net11 SchemaModel and
links the neutral emitter source subset, excluding analyzer/type-symbol frontend;
it does not reference the analyzer DLL containing duplicate schema type identities.
These linked-source inputs are explicit selection dependencies. They are not
runtime cycles or a requirement for product applications to load Roslyn.

## Package entries and resource routing

Create seven aggregate package entries named orm-package-core, execution, postgres,
sqlite, mysql, generator and schema-tool. Use the IDs and include lists in
ORM-PACKAGE. Pack/consume are the exact no-argument arrays invoking
eng/orm-package/pack.py and consume.py; they read the runner's NW variables rather
than requiring an incompatible extra positional package key.
Pack receives NW_PACKAGE/NW_VERSION/NW_FEED/NW_INPUTS,
produces exactly one matching nupkg and embeds korda/public.json with inputs.
Consume restores that exact candidate from NW_FEED into an isolated cache. Host-only
analyzer/tool checks are declared; runnable AOT consumers execute the native binary.

Package README/license/description inputs use metadata, while API/signature/source
inputs use sources. Ordinary `docs/orm/**/*.md` keeps the existing documentation
classification with zero product builds. Sample code is explicitly different.
A provider test/source edit must not start unrelated database services. A genuinely
shared schema CLI input can select all its driver dependencies as actual consumers;
that is explained in the selection reason, not hidden as an accidental global gate.

### Owned NuGet dependency closure: required narrow runner extension

The inspected existing module_job/validate_public assumes one self-contained
package and rejects all nuspec dependencies. Its compatibility.validate_closure
already supports an exact owned-package DAG. Reuse that checker and extend only
the existing runner branch for registered package manifests; do not weaken old
provider policy or create another dispatcher.

1. Add optional `package_manifest` to catalog's allowed fields. It is one validated
   repository-relative `packaging/orm/<NuGetId>.json` path, required for the new
   orm-package-* entries. Identity/module must match their existing package entry.
2. The manifest fixes `ownedDependencies` as NuGet ID → `{module,version}` and
   `externalDependencies` as the exact allowed NuGet pins. Owned version is either
   literal `candidate` (resolved to NW_VERSION for the initial cohort) or one
   reviewed exact published version. Reject ranges, floating/latest, undeclared
   IDs and cycles. Later independent releases pin unchanged accepted dependencies
   explicitly; they do not force unrelated Core publication just to share a number.
3. module_job.stage_owned_dependencies walks this DAG in topological order. Build
   an unpublished candidate through the existing pack command in its own isolated
   single-output feed, or obtain the declared exact published archive from verified
   package metadata/cache. Check each archive's identity/version/input fingerprint,
   unsigned entries, provenance and owned edges. Reuse verified builds where valid.
4. Stage only that owned closure in a separate read-only NW_DEPENDENCY_FEED and
   write NW_DEPENDENCY_MANIFEST with ID/version/module/source commit/input fingerprint/
   archive SHA256/owned dependencies. NW_FEED still contains exactly the target
   archive. Consumer NuGet.Config uses these two explicit feeds and the declared
   pinned external source; an isolated NUGET_PACKAGES prevents accidental fallback.
5. release.json keeps schema_version1 and records target plus the full owned
   closure in packages, with each real dependencies map and existing hash/entries
   fields. The target source is current HEAD; a verified previously published
   dependency retains its own source commit, never a fabricated current commit.
   Its declared fingerprint must match the accepted input required by the target.
6. Invoke existing compatibility.validate_closure on the entire closure. Add a
   package_manifest branch in validate_public which computes the expected closure,
   checks allowed external nuspec dependencies, exact target/dep feed membership
   and all hashes/provenance, then returns **only the target** for publication.
   The old product branch and its no-dependency rule remain unchanged.
7. Before publishing a target, verify every owned dependency is already published
   as the validated exact version. Initial cohort publication therefore follows
   dependency order; failure to publish Core prevents publishing dependent Execution.
   PR checks stage/consume candidates only and never publish. Normal verified
   product package transfer may use the existing CI mechanism; research artifacts
   are never introduced into it.

Add fixtures CI-15 through CI-21: fresh-cache Execution and provider consumers with
candidate dependencies pass; missing/wrong-version/wrong-hash/undeclared dependency
fails; cyclic owned graph fails; published unchanged dependency retains its actual
provenance; legacy self-contained provider behavior remains unchanged. Verify the
final consumer's assets JSON resolves the exact owned closure and pinned external
versions, rather than only inspecting a successful restore exit code.

## Ordered implementation and exact routing fixtures

1. Register all new paths without changing existing ownership. check-index must
   reject unknown/ambiguous paths before installing compilers or starting services.
2. Add the managed project/include/dependency edges above. Use the current catalog
   model, not a hard-coded substring test in YAML or a duplicate package list.
3. Keep local module commands independently runnable from the repository root.
   Store reusable internal build outputs only in artifacts/modules/<module>/.
4. Add actual temporary Git repository fixtures with base/head commits, not mocked
   changed-path lists. Assert selected checks, packages and required resources.
5. Validate the following required cases before accepting the registry:

| Case | Expected selection |
| --- | --- |
| CI-01 Markdown-only docs/orm edit | Zero product compilation/database/performance checks |
| CI-02 PostgreSql driver test-only edit | PostgreSQL owning checks; no SQLite/MySQL/Maria service |
| CI-03 PostgreSql driver source edit | Driver and actual PostgreSQL/schema-tool consumers plus affected package; unrelated provider tests excluded |
| CI-04 Contracts source edit | All actual managed consumers and affected exact-package checks |
| CI-05 Schema snapshot/emitter input | Generator/schema-tool and generated consumers through explicit edges |
| CI-06 Generator private dependency/version edit | Host-load, emitted native consumer and analyzer package closure |
| CI-07 Core package description/license edit | Metadata fingerprint/package checks; no unrelated API baseline rerun |
| CI-08 Rename driver source across modules | Both deleted and added ownership processed |
| CI-09 Delete referenced module/project | Surviving dependency validation fails clearly |
| CI-10 Multi-commit PR and merge-base diff | All relevant changes selected once, not only last commit |
| CI-11 Unknown path/ambiguous ownership/cycle | Planner fails before resource setup |
| CI-12 Language leaf versus aggregate project edit | Leaf consumers without sibling test fan-out; aggregate edit exercises included components |
| CI-13 MySQL lane versus Maria lane | Shared driver change reaches both; family-specific fixture selects only that family |
| CI-14 Benchmark-source edit | Build/correctness where applicable; long timing campaign remains explicit |

Run the existing commands unchanged:

```bash
python3 eng/ci/worker.py check-index
python3 -m unittest discover -s tests/Tooling -v
python3 eng/ci/impact.py origin/main --output artifacts/plan.json
python3 eng/ci/worker.py run artifacts/plan.json linux
```

Registry acceptance proves selection mechanics and a fixture native consumer, not
unimplemented product modules. Every later owner supplies its real run command;
Integration/Package exercise the completed graph. Keep workflow YAML limited to
checkout/tool setup/cache/runner invocation. Stop after integration of these
registered checks; this task grants no release upload or product migration.
