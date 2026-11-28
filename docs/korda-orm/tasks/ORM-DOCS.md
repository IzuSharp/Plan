# ORM-DOCS — exact API reference and executable local guides

Status: `planned_candidate`; `implementation_authorized: false`.

## Fixed outcome and dependencies

Document the graph-pinned Design API and behavior in `implementation-spec.md`,
`contracts.md` ORM-C01–ORM-C06, `generation-integration.md`, `mature-execution.md`
and the source-linked language/dialect specifications. The selected execution
backend is Dapper.AOT runtime with generated/static factories. Do not describe an
unimplemented custom executor or original-Dapper interception as the default.

Start after `ORM-FOUNDATION`. Author prose and sample contracts in parallel with
implementation, using the fixed signatures rather than inventing a new public
surface. Final acceptance requires the actual query, generator, execution, dialect,
provider, schema-tool and mandatory advanced/nested inputs named by the graph:
`ORM-QUERY`, `ORM-GENERATOR`, `ORM-EXECUTION`, all four dialect tasks,
`ORM-POSTGRES-DRIVER`, `ORM-SQLITE-DRIVER`, `ORM-MYSQL-DRIVER`,
`ORM-SCHEMA-TOOL`, `ORM-ADVANCED-TYPES` and `ORM-NESTED`.
A missing implementation keeps the corresponding sample pending; prose cannot
mark it compiled. The package task later repeats sample consumption against exact
archives, so this task does not depend on packaged archive acceptance.

## Owned files and required contents

Own `docs/orm/**` and `samples/orm/**`; module owners own source XML comments and
public signatures, and the CI owner owns shared module registration. Produce:

| Path | Required content |
| --- | --- |
| `docs/orm/README.md` | Seven product entry points, supported profiles, local workflow and explicit evidence labels |
| `getting-started.md` | Pure SQL first; provider execution, DTO annotation, build/publish/run and expected rows |
| `api/` | Compiled public signatures, type/member summaries, parameters/defaults, nullability, exceptions, ownership and XML links |
| `guides/sql-language.md` | Fields/parameters/literals, dynamic conditions, aliases/scope, rows, joins, CTE/set/window/DML and capability failures |
| `guides/execution.md` | Rendered template/value split, typed binding, default and manual mapping, async/streaming/transaction ownership |
| `guides/generation.md` | `[DbRow]`, `[DbConstructor]`, compiled registrar roots, Tables/TableRefs/Rows/Types output names, schema-only use, exact diagnostics and host boundaries |
| `guides/schema-tool.md` | Exact acquire/validate/generate commands, credentials by environment name, filtering, external FKs and output safety |
| `guides/providers.md` | Separate PostgreSQL/SQLite/MySQL/MariaDB profiles, codecs, native dependencies, async/cancel limits |
| `guides/native-aot.md` | SDK/RID/native linker prerequisites, local publish/run, actual generated code inspection and no fallback policy |
| `guides/errors-and-lifetimes.md` | Stable errors, first-row shape checks, empty results, early stream disposal, cancellations and unknown commit outcome |
| `guides/packages-and-compatibility.md` | Fixed dependency/asset closure, API/semantic compatibility and proposed migration boundary |
| `samples/orm/manifest.json` | Case ID, project, profile, dependencies, expected result, evidence state and native requirement |
| `samples/orm/check.sh` | Build/run one named case; accepts explicit candidate feed/version for archive rechecks |

Each public reference entry states what is checked at compilation, pure semantic
validation, binding, first materialized row and database execution. Do not imply
all invalid SQL is a C# compile error or every empty result detects schema drift.

## Exact sample suite

Reuse ORM-INTEGRATION's exact fixture and independent expected values. Departments
are `(1,"Engineering")`, `(2,"Operations")`. Users `(id,name,age,active,department_id)`
are `(1,"Alice",32,1,1)`, `(2,"Bob",18,1,1)`, `(3,"Carol",NULL,0,2)`,
`(4,"Dana",44,1,2)` and `(5,"Eve",18,1,NULL)`. Active is the fixture's Int64 0/1
column; a separate Boolean-codec sample must declare that storage explicitly.
Keep ordering explicit and source aliases equal to mapped DTO descriptor names.
Do not invent a second users/orders fixture for the documentation.

| Case / project directory | Required operations | Expected result/gate |
| --- | --- | --- |
| `render-only` / `01-render-only` | Core package only; typed parameter, optional age predicate, render SQL/layout for each profile | Bound values absent from SQL; layout has 1 or 2 declared slots as specified; no driver/Dapper/Roslyn/native executor dependency |
| `dto-query` / `02-dto-query` | `[DbRow]` record and public-init DTO; natural `Query<T>.ToListAsync` | INT-Q01/Q02: active IDs 1/2/4/5; age >=20 gives 1/4; Carol age remains null |
| `dynamic-shapes` / `03-dynamic-shapes` | Optional name filter, repeated logical slot, changed typed parameter combination, expanded IN | INT-Q03–Q07: Alice gives 1; IN(1,3,5) gives 1/3/5; empty IN gives none; same-name slots 1/2 remain distinct |
| `join-aggregate` / `04-join-aggregate` | Left join users/departments; group an inner join by department | INT-Q08/Q09: five joined rows, Eve.Department=null; Engineering count2/max32, Operations count2/max44 |
| `stream-lifetime` / `05-stream-lifetime` | Async stream, break after first row, then another command on borrowed connection | First id1; stream resources released; connection usable; pre-cancelled call sends no command |
| `transaction` / `06-transaction` | Borrowed transaction insert, read, rollback; separate committed example | INT-L09: insert ID6 gives count6, rollback restores5; explicit commit sets Alice age33; reset before another case |
| `schema-offline` / `07-schema-offline` | Validate/generate a committed schema fixture with no credentials/network | Generated declarations/DTO compile; application publishes and runs natively |
| `schema-acquire` / `08-schema-acquire` | Explicit local acquisition for each profile, review canonical snapshot, rebuild | Expected types/keys/defaults captured; subsequent build makes no database discovery call |
| `manual-mapping` / `09-manual-mapping` | No generator package; explicit static mapping overload | Same DTO values through packaged execution runtime; default global mapping is not replaced |
| `advanced-nested` / `10-advanced-nested` | Accepted JSON/array/domain/enum and nested presence/order slice for the selected profile | Exact JSON/array/range/presence/duplicate subcases below; unsupported profile cells fail before send |
| `negative-contracts` / `11-negative-contracts` | Wrong generic operand, missing mapping, ambiguous constructor, unsupported profile, unexpected NULL/reader shape | Exact compile/runtime diagnostic IDs; no reflection or vanilla Dapper fallback |

The advanced-nested project contains four fixed subcases, routed by profile:

- `json-four-states`: SQL NULL, JSON `null`, JSON string `"null"`, and `{}` remain
  distinct. Missing property versus existing-null follows INT-A04 and the typed
  JSON path contract; no object deserializer is substituted.
- `pg-array-range`: PostgreSQL-only INT-A01 uses SqlArray<int> `[2,4,8]`, JsonbText
  with `n=17` and `O'Reilly`, and SqlRange<int> `[1,5)`. Non-PostgreSQL profiles
  assert the declared unsupported diagnostic for native array/range identities.
- `optional-presence`: INT-A07 returns None for the missing key while skipping
  required child getters, Some for a present child whose projected nullable
  values are all null, and KORM-MAP-003 for presence1 plus a required NULL.
- `ordered-duplicates`: use ORM-NESTED's parents1/2 and children
  `(seq,id,parent,name,score)` `(0,3,1,"z",30)`, `(1,1,1,"a",null)`,
  `(2,1,1,"a",null)`, ordered by id,seq. Parent1 is exactly
  `[[1,"a",null],[1,"a",null],[3,"z",30]]`; parent2 is `[]`. Repeated rows remain
  repeated. Scalar collection `[1,2]` is transported as `[[1],[2]]` and decoded
  to ImmutableArray<long> with two elements.

The manifest records these exact integration/feature IDs and expectations.
Examples may be shortened in prose only after their maintained project has passed
its full case; a prose excerpt does not replace executable coverage.

## Authoring and implementation sequence

1. Copy public signatures from the compiled API baseline and XML output supplied
   by module owners. Include namespace and generic constraints. Raise a concrete
   mismatch if Design, compiled API and generated samples disagree; do not change
   code only to make an incorrect tutorial pass.
2. Write the no-driver guide and run its native sample before provider guides.
   Explain that runtime query structure and parameter count may change while
   CLR types and generated mappings remain known. Dynamic SQL is not dynamic IL.
3. Show annotated records/init DTOs without handwritten Dapper calls or mapper
   boilerplate. Install generator tooling in both an external DTO project and
   the final application so the latter emits explicit referenced-registrar roots;
   do not rely on a library-only initializer surviving Native AOT trimming. Show the explicit manual-mapping overload separately for deliberate
   custom mappings. Explain that generator tooling executes during build and is
   absent from application runtime dependencies.
4. Write resource ownership beside each relevant call: who opens/disposes the
   connection/transaction, when a stream begins, and what early disposal releases.
   State SQLite's actual synchronous async behavior/cancellation limitations;
   do not wrap database work in hidden `Task.Run` to make an example look async.
5. Make every runnable sample a real project using the declared public products.
   Avoid copied generated output as a substitute for loading the analyzer. Never
   use internals, research-only helper types or undeclared package references to
   make a public sample compile.
6. Implement the manifest runner. Each case has `pending`, `compiled`, `native_run`
   or `blocked` state with a scoped reason. A negative compilation case passes
   only on its exact expected diagnostic, not on any nonzero compiler exit.
7. Execute provider samples on disposable fixtures and compare complete typed
   values/order/nullability. Native samples must run the emitted executable and
   verify dynamic code is unavailable. Capture concise maintained results; keep
   raw outputs/builds local.
8. Cross-check dependency closures: core-only sample has no Dapper or driver;
   individual provider examples contain no unrelated provider; generator/compiler
   helpers do not appear in native application runtime closure.
9. Write the fixed local commands below and test them from a clean sample checkout.
   GitHub is not a prerequisite for developing, compiling, publishing or running.
10. Give `ORM-PACKAGE` the exact sample manifest and invocation protocol for its
    candidate-archive recheck. Only that later check establishes published-input
    fidelity; keep the distinction visible in the reference.

## Local command contract

```sh
bash samples/orm/check.sh --all
bash samples/orm/check.sh --case render-only
bash samples/orm/check.sh --case dto-query --profile sqlite-3.45
bash samples/orm/check.sh --case dto-query --profile postgres-18
bash samples/orm/check.sh --case schema-offline
bash samples/orm/check.sh --case dto-query --profile sqlite-3.45 \
  --feed <candidate-feed> --version <exact-candidate-version>
```

`--all` is mutually exclusive with --case and --profile. It iterates all eleven
manifest cases, every applicable profile, required negative cases and all fixed
advanced subcases, building each distinct native consumer once per profile. A
missing required network fixture endpoint is a configuration failure, not a skip
or a successful empty selection. It accepts the same optional exact archive
feed/version pair. Per-case --profile remains the scoped local/CI entry; the
aggregate --all is the complete documentation acceptance gate.

The script validates case/profile/feed/version before executing. Archive mode
creates an isolated cache and uses exact package versions; source-development mode
uses the reviewed product projects and reports that distinct evidence level.
Database credentials come only from each documented profile's environment
variable. No default production endpoint, hidden secret lookup or mandatory CI run.

The Native AOT guide includes `dotnet publish -c Release -r linux-x64` and the
actual executable invocation; it names required native linker/system prerequisites
and only the verified RID/OS support. It must not suggest that ordinary
`dotnet build` proves native execution.

## CI, acceptance and stop

Propose independently selectable sample source/test inputs and real module
prerequisites to the CI owner. A sample change compiles/runs that sample and its
required provider lane; ordinary guide prose selects no product compilation.
Compiled API/XML changes reach relevant reference and sample checks; do not
rebuild every provider for a spelling edit.

Acceptance requires every mandatory sample in the task scope to have its actual
compiled/native evidence, consistent API/XML references and checked local links.
Unsupported or future features are clearly labeled and cannot appear in runnable
examples as if shipped. Package and final acceptance re-run the sample matrix
against exact archives and complete provider profiles.

Stop at the reviewed documentation/sample PR. Do not publish packages, claim old
code was removed, merge, perform cutover or start a new research campaign.
