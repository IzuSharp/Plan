# ORM-FOUNDATION: Implement the fixed shared surface and module ownership

Status: `planned_candidate`; product implementation remains unauthorized.

Use the immutable Design commit in `../implementation-graph.json`, contracts v0.2.0,
and `docs/korda-orm/implementation-spec.md`. The packet fixes implementation work;
contradictions return to the contract owner before changing an interface or policy.

## Inputs and gate

Start only after the user accepts the paired Design/Plan revisions and authorizes
product changes. There is no historical R/D/A/B prerequisite. Read the current
product AGENTS, CONTRIBUTING and `eng/ci/modules/README.md`; preserve existing
products. This task implements the specified data contracts and project seams.
It does not select an execution backend, invent public API names, or defer those
choices to the other task owners.

Normative inputs: implementation-spec §§1–9; contracts ORM-C01–C06;
`mature-execution.md` public Runtime protocol; `generation-integration.md` schema,
mapper and analyzer-host contracts; the six execution/provider task signatures.

## Exact files and initial ownership

| File / directory | Deliverable |
| --- | --- |
| `src/Orm/Contracts/Korda.Orm.Contracts.csproj` | net11.0/C#15, nullable, deterministic, XML, BCL only; no driver/Dapper/Roslyn reference |
| `src/Orm/Contracts/{Identity,SqlTypeDescriptor,Field,Condition,Query,Projection,ParameterValues,ParameterLayout,ResultShape,Diagnostics}.cs` | Immutable data handles and the exact shared signature surface from Design |
| `src/Orm/Contracts/Nodes/` | Shared immutable node records/tags listed by Design; records carry data, not SQL emission or I/O |
| `src/Orm/Contracts/AssemblyInfo.cs` | Exact named friend assemblies from implementation-spec, including four dialects/AdvancedTypes/Nested/Parser/SchemaModel and provider leaves; no wildcard access |
| `src/Orm/*/*.csproj` and Dialects/Providers leaf project files | The fixed project/reference map; later implementation owners fill their scoped sources |
| `tests/Orm/Contracts/Surface.Reference/` | A compile-only reference declaration of the reviewed public surface for positive/negative API fixtures; never packaged or executed as a working library |
| `tests/Orm/Contracts/Program.cs`, `verify.py` | Native data-contract assertions plus positive/negative compiler fixtures |
| `Korda.slnx`, `eng/ci/modules/orm.json` | Initial project membership and actual path/dependency registration; ownership transfers to ORM-CI after this task |

Foundation creates project files once. It does not create placeholder successful
executors, renderers or database tests. A not-yet-implemented module has no passing
behavioral acceptance entry. Its independent owner compiles against the shared
Contracts and its own implementation; integration waits for real peers.

## Ordered implementation

1. Copy the declared names, generic constraints, nullability/default values and
   accessibility from Design. Core data handles remain in Contracts; Fluent
   operators are Language extension methods; rendering/binding extensions live in
   Rendering. Do not put partial classes in different assemblies.
2. Add immutable record descriptors, NodeKind and node data records with exactly
   the ordered fields in Design. Every collection constructor copies to an
   ImmutableArray. Construction validates empty IDs, negative facets, duplicate
   ordinals and malformed names before publishing a usable descriptor.
3. Allocate SlotId and RelationId with Interlocked.Increment; keep constructors
   internal. They are process identities, not schema IDs or emitted SQL names.
   Two parameters with the same label must still receive distinct IDs. Include
   TableKeyDefinition and both Table.Define overloads from Design; freeze ordered
   key columns, reject empty/duplicate columns and multiple primary keys, preserve
   metadata through As, and keep expression/partial keys outside proof eligibility.
4. Implement typed `BoundValue<T>` cells and the generic visitor protocol from
   ORM-EXECUTION. ParameterValues.Build consumes a builder once and freezes its
   lookup/array; With returns an independent replacement snapshot; Add rejects a
   duplicate. List and mutable byte/array inputs are copied once. Never store an
   active DbCommand, reader, driver type or unbounded runtime type factory here.
5. Put one shared atomic InvocationState inside each BoundCommand. Expose only the
   internal admission seam to Execution; copying a public record must not create a
   second token. Templates remain reusable, and Bind creates a new invocation.
6. Add the seven public-product project/dependency records specified by ORM-PACKAGE;
   no internal assembly gets a separate tiny NuGet package. Core has no Dapper
   dependency; Execution owns the one shared Dapper.AOT-backed runtime assembly.
7. Register source/test roots and literal ProjectReference dependencies using the
   existing registry format. Use the CI packet's module IDs and command arrays.
   Do not replace the dispatcher or YAML routing.
8. Compile the exact public declarations and consumer fixtures, then publish/run
   the actual data-contract consumer natively. The reference-only declaration
   compile is a signature check; it does not satisfy a missing behavioral module.
9. Record the shared-contract commit, API baseline and ownership transfer. Dependent
   owners use that concrete commit; a contract change has a versioned coordinated
   patch, not local divergent copies.

## Mandatory fixtures

| ID | Input | Expected result |
| --- | --- | --- |
| FND-01 | Two Param<long> values both named `id` | Distinct SlotId values |
| FND-02 | Mutate caller array after constructing a descriptor/list binding | Frozen contract stays unchanged |
| FND-03 | Copy then replace one ParameterValues slot | New snapshot changes; original does not |
| FND-04 | Builder Add same SlotId twice | KORM-BIND-002; no partially frozen value set |
| FND-05 | Field<long>.Eq(Param<string>) | Compile failure; no implicit object widening |
| FND-06 | Matching Field<long>/Param<long> and nullable long slot | Positive consumer compiles |
| FND-07 | Concurrent identity allocation, 10,000 IDs | All unique; no reliance on labels |
| FND-08 | Contracts dependency closure | No Dapper, provider, Roslyn, hosting or old native engine |
| FND-09 | Same BoundCommand admission token claimed twice | First succeeds; second fails; new template Bind has a fresh token |
| FND-10 | All declared project edges | No cycle; unrelated provider absent from each leaf closure |
| FND-11 | Table.Define with a nonpartial key; alias twice; mutate input key array | Aliases have distinct RelationIds and equal frozen key metadata; original array mutation has no effect |
| FND-12 | Empty/duplicate key columns or two primary keys | KORM-TYPE-001 before exposing a Table; manual keys remain declared assertions, never an implicit database query |

## Local validation, integration and stop

Create the maintained `tests/Orm/Contracts/verify.py` entry to compile the positive
and negative fixtures, publish `Korda.Orm.Contracts.Tests.csproj` with
`dotnet publish -c Release -r linux-x64 -p:PublishAot=true`, and execute the produced
native binary. Assert RuntimeFeature.IsDynamicCodeSupported is false. Use the
repository's actual toolchain and lockfile conventions; outputs stay under artifacts.
Run `python3 eng/ci/worker.py check-index` and inspect
`python3 eng/ci/impact.py origin/main --output artifacts/orm-plan.json`.

Acceptance requires the actual shared data contracts and the listed fixtures,
not complete queries or databases. Stop after the reviewed foundation commit and
ownership handoff. It does not authorize beginning another task, merging or publishing.
