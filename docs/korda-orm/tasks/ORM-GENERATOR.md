# ORM-GENERATOR — compiled mappings over the Dapper.AOT runtime

Status: `planned_candidate`; `implementation_authorized: false`.

## Fixed outcome and inputs

Implement the selected one-pass incremental frontend in the graph-pinned Design
`generation-integration.md` sections 1–5 and 7. Use ORM-C01, ORM-C03–ORM-C06 and
`implementation-spec.md`; use Dapper.AOT 1.1.0 at
`0e071bf05e54caecfa98c885b075fa3e247f3ecc`, specifically `RowPlan`, `ParamPlan`,
`DapperInterceptorGenerator` row/argument emission, `CommandFactory<T>` and
`RowFactory<T>`. The runtime dependency is Dapper.AOT; this task must not invent an
execution engine, fork its row loop or require its interceptor generator to see
Korda generator output.

The result is ordinary `Query<T>.ToListAsync(session, token)`/`StreamAsync` use
with known Entity/DTO/record results. Users add `[DbRow]` to a declared DTO or use
an already-generated row. They do not write Dapper calls, factories, reflection
configuration or a mapping method for each ordinary DTO.

Start after `ORM-FOUNDATION`. Final acceptance requires `ORM-TYPES`, `ORM-SCHEMA`
and `ORM-EXECUTION`. Work against the fixed contract fixtures immediately; there
is no dependency on the live schema tool or every provider being implemented.

## Files, targets and ownership

Own these files and their tests under the existing graph scope:

| File/module | Required contents |
| --- | --- |
| `src/Orm/Generation/Korda.Orm.Generators.csproj` | netstandard2.0 analyzer target; C# 15 build; Roslyn Common/CSharp 4.14.0 private build references; no runtime project output reference in applications |
| `RowGenerator.cs` | `IIncrementalGenerator.Initialize`; independent attributed-DTO and AdditionalFiles pipelines |
| `Model/RowPlan.cs`, `Model/MemberPlan.cs`, `Model/ConstructorPlan.cs` | Structurally equatable output models; fully qualified names, exact aliases, types/nullability, conversion IDs and constructor order |
| `Analysis/RowPlanBuilder.cs` | Symbol-to-model projection, constructor selection and accessibility checks |
| `Analysis/TerminalMappingAnalyzer.cs` | Exact known terminal recognition and ORMGEN006/010 diagnostics; no method-name-only matching |
| `Emission/RowFactoryWriter.cs` | Direct Dapper `RowFactory<T>` source; strict tokenization and typed reads |
| `Emission/RegistrationWriter.cs` | Public per-row registrars, compiled markers and sorted EnsureRegistered calls |
| `Emission/SchemaDeclarationWriter.cs` | Tables/fields/keys/optional DTOs from the validated neutral snapshot |
| `Diagnostics/OrmGeneratorDiagnostics.cs` | Exact ORMGEN001–010 descriptors from Design, stable locations and safe messages |
| `Input/` linked Schema format sources | Reuse the Schema owner's parser/validator/model; register the linked-source dependency |
| `tests/Orm/Generation/` | Real generator-driver tests, compilation fixtures, native consumers and `check.sh` |

The portable source boundary is fixed. `Model/SchemaPlanBuilder.cs` converts a
validated snapshot into neutral row/table models. `Emission/SchemaSourceEmitter.cs`
provides `internal static ImmutableArray<GeneratedSource> Generate(SchemaSnapshot
snapshot)`, where `GeneratedSource` is an internal record `(string HintName,
string Text)`. Keep these models and emission files free of Roslyn ISymbol,
Compilation, SyntaxNode and Location values. C# syntax parsing/escaping may use the
fixed Roslyn 4.14 utility APIs; user code is never compiled or executed by this
facade.

The analyzer links `src/Orm/Schema/Model/`, `Format/`, `Generation/` and
`Diagnostics/` portable source files and adds its netstandard IsExternalInit shim.
It does not ProjectReference/load the net11 SchemaModel assembly. SchemaTool
instead references that real net11 assembly and links this generator's neutral
Model/Emission source subset, excluding RowGenerator, Analysis and generator
Diagnostics. Do not reference Generators.dll from SchemaTool: the analyzer contains
a linked copy of SchemaSnapshot, so such a reference would create a second CLR
assembly identity for the same model name. Each host compiles the emitter against
its own one schema-model definition. CI declares both linked-source dependencies.

Schema-generated DTOs have no DbRow attribute: the schema pipeline already has
their row plans and emits mappings directly when requested. Both incremental and
physical generation emit CompiledRow/registrar output from that plan. This prevents
physical generated DTOs from being mapped twice by the attributed-row pipeline.
If physical generated types and an enabled AdditionalFile claim the same schema
or CLR output identity, report ORMGEN009. `KordaOrmGeneration=None` disables only
that AdditionalFile, leaving attributed DTOs and registrar rooting active.

Execution owns `DbRowAttribute`, `DbConstructorAttribute`, `CompiledMapping<T>`,
`Mapping<T>`, shared parameter-layout binding and terminal signatures. Request a
contract amendment if they disagree; do not emit an alternative local version.
The generator owns no driver catalog queries, execution cleanup loop, root
project registry or package producer. The CI owner integrates the proposed
`orm-generator` registration.

## Fixed annotation and closed-row registration contracts

Execution owns `MappingAttributes.cs`; the generator consumes these exact public
attributes in `Korda.Orm.Execution`:

```csharp
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Struct,
    AllowMultiple = false, Inherited = false)]
public sealed class DbRowAttribute : Attribute { }
[AttributeUsage(AttributeTargets.Constructor, AllowMultiple = false, Inherited = false)]
public sealed class DbConstructorAttribute : Attribute { }
[AttributeUsage(AttributeTargets.Property | AttributeTargets.Field,
    AllowMultiple = false, Inherited = false)]
public sealed class DbColumnAttribute : Attribute
{
    public DbColumnAttribute(string? alias = null) => Alias = alias;
    public string? Alias { get; }
    public string? ConversionId { get; set; }
}
[AttributeUsage(AttributeTargets.Property | AttributeTargets.Field,
    AllowMultiple = false, Inherited = false)]
public sealed class DbIgnoreAttribute : Attribute { }
[AttributeUsage(AttributeTargets.Assembly, AllowMultiple = true)]
public sealed class DbCompileRowAttribute : Attribute
{
    public DbCompileRowAttribute(Type rowType) => RowType = rowType;
    public Type RowType { get; }
}
[AttributeUsage(AttributeTargets.Assembly, AllowMultiple = true)]
public sealed class CompiledRowAttribute : Attribute
{
    public CompiledRowAttribute(Type rowType, Type registrarType)
        => (RowType, RegistrarType) = (rowType, registrarType);
    public Type RowType { get; }
    public Type RegistrarType { get; }
}
```

`DbCompileRow` is an explicit source input for a closed built-in Row arity;
`CompiledRow` is generated evidence for a compiled mapper. The runtime does not
scan either attribute. Public instance properties are mapped unless ignored;
static/indexed properties are not columns. Fields participate only with
`DbColumn`; conflicting ignore/column annotations and hidden duplicate members
fail ORMGEN003. An overriding property replaces its base declaration; a hidden
`new` property is not an override. The selected declaration's mapping annotations
apply. Order inherited members base-to-derived and then by ordinal CLR member
name within each declaring type; constructor parameter order is separate.

Emit an assembly `CompiledRow(typeof(T), typeof(Registrar))` marker for every
valid generated DTO and closed Row mapping. DTO registrars are public static
infrastructure classes named `Korda.Orm.Generated.RowRegistrar_<hash>`; hash is the
full lowercase SHA-256 of the row's fully qualified CLR metadata name. Each
has an explicit static constructor containing the sole Mapping<T>.Register call,
and a public parameterless void EnsureRegistered method marked NoInlining.
The declaring module initializer invokes that registrar. The final consumer also
runs the generator: at compile time it reads pre-existing CompiledRow attributes from its source
assembly and referenced assembly symbols, validates the public registrar method, deduplicates identical
registrar identities, and emits direct EnsureRegistered calls in its own module
initializer. Local generated rows feed registration descriptors directly without
asking Roslyn to rediscover another source-output stage. A closed Row marker
points to its corresponding RowMappings<T1,...,TN> type.

These consumer calls are required static reachability, not runtime attribute
scanning. A native negative control showed that registration only in a library
whose helper was optimized away can be absent although the same managed fixture
passes. Do not infer registration retention merely from a referenced DLL or an
output marker. Do not use RunModuleConstructor as a Native AOT repair. A consumer
without the generator must deliberately invoke the public registrar/RowMappings
entry point or pass an explicit static mapping. Normal annotated DTO use installs
the generator in both the DTO compilation and final application; it requires no
handwritten registration. The analyzer accepts source-local DbRow declarations
whose row plan succeeded, referenced-assembly CompiledRow markers, the fixed
Execution scalar set, and explicit mapping overloads. A referenced DbRow marker
alone does not prove its assembly ran the generator. A deliberately handwritten
mapping remains usable through the explicit terminal overload.

For built-in `Row<T1,...,TN>`, N=1..8, the consumer generator collects actual closed
Row symbols from source type syntax and semantic invocation/argument/result types.
Only exact `Korda.Orm.Row` metadata identities count. Inspect nested generic
arguments of `Query`, `Projection`, terminal return types and arguments; never
classify an unrelated class named Row. Reject any remaining type parameter,
unbound generic or unsupported arity. Include explicit
`[assembly: DbCompileRow(typeof(Row<long,string>))]` inputs for generic library
paths where a closed result shape is otherwise absent from consumer source.
Project the closed type names into equatable data and deduplicate by full CLR
metadata identity before emitting registrations.

Execution supplies `public static class RowMappings<T1,...,TN>` for each arity,
with `public static void EnsureRegistered()`. Its explicit static constructor
creates the one matching `RowCompiledMapping<T1,...,TN>` and calls
`Mapping<Row<T1,...,TN>>.Register` once. Each generated module initializer calls
`RowMappings<closed arguments>.EnsureRegistered()`. Multiple assemblies may make
that call safely; generic static initialization performs the registration once.
Do not weaken ordinary DTO duplicate-registration errors. Without the generator,
an advanced caller may explicitly call this same EnsureRegistered entry point.
A fully generic library helper emits no open registration; a missing eventual
closed mapping fails KORM-MAP-001 before dispatch.

A malformed/open/non-Row DbCompileRow request is ORMGEN001. A known closed terminal
with neither a valid generated registration nor a supported scalar/manual mapping
is ORMGEN006. Duplicate identical hints coalesce; conflicting generated mappings
are errors. Known scalar mappings come from Execution's fixed BCL/nullable list,
with degree one and alias from the actual ResultShape, never a hard-coded Value
alias. This does not advertise a provider codec that the chosen profile lacks.

Source-generated type descriptors call the public
`SqlTypes.Define<T>(SqlTypeDescriptor)` entry point. The descriptor CLR type must
be exactly typeof(T), its nullability must agree with nullable value types, and
facets must be valid. Column nullability is represented in the emitted descriptor;
no application calls an internal SqlType constructor. An explicit type binding
names an existing static SqlType<T> member and the generator applies the validated
column facets/nullability to a copied descriptor. Complete physical identity is
retained in schema metadata; generated SQL qualifies PostgreSQL/MySQL/MariaDB and
SQLite names with the profile's schema/database alias plus local name. It never
blindly renders all catalog/schema/name identity segments.

## Implement in this order

1. Create the netstandard2.0 analyzer project and compile a trivial generated
   declaration in the SDK 11.0.100 host. Do not reference SDK-local Roslyn DLLs in
   the product project; use the fixed private package references. Keep the
   generator assembly out of application runtime dependency closure.
2. Build the attributed row pipeline with `ForAttributeWithMetadataName` for
   `Korda.Orm.Execution.DbRowAttribute`. Select source declarations only; a
   consumer of another assembly's DTO does not emit a second default mapper.
3. Project all symbol information into equatable data immediately. Use a sequence
   comparer for immutable arrays; default `ImmutableArray<T>` reference equality
   is not sufficient. Do not retain a Compilation/Symbol/SyntaxNode in an output
   cache or perform per-keystroke assembly-wide inheritance scans.
4. Implement the fixed constructor algorithm: a unique marked accessible
   constructor, otherwise a unique valid non-parameterless constructor, otherwise
   an accessible parameterless constructor plus complete init/setter assignments.
   A candidate's every parameter must match one mapped CLR member (exact name,
   then unique ordinal-ignore-case fallback), have a compatible declared type and
   not be ref/in/out. Every mapped member not passed to that constructor must be
   assignable. A constructor without SetsRequiredMembers requires generated
   initializer assignments for every C# required member, including any also passed
   as an argument; reject inaccessible required assignments. Exclude record copy constructors. Ambiguity and
   missing required members are errors, not selection heuristics.
5. Build the JSON AdditionalFiles pipeline. Validate/normalize the schema through
   the shared format code. Emit table/type/key declarations and optional rows;
   feed a generated row's neutral model directly into row emission rather than
   relying on a second generator to inspect generated declarations.
6. Emit each compiled mapping independently. `Bind(ResultShape, ProviderServices)`
   validates the declared projection and produces an immutable bound row factory
   with ordered aliases/member indexes/codecs. For each scalar member of known CLR
   type TMember, call `services.ValidateResult(column, member)`. This validates
   the effective read-conversion rule: a null member ID uses the column ID; a
   null column ID uses the member ID; two Ordinal-equal non-null IDs use that ID
   once; two different non-null IDs fail KORM-MAP-002 in Bind before command
   creation. After successful validation compute
   `var effectiveReadConversion = member.ConversionId ?? column.ConversionId`
   and call `services.BindReader<TMember>(column.Type, effectiveReadConversion)`
   once. Store the
   returned `Func<DbDataReader,int,TMember>` in a typed readonly field of that bound
   factory; never look up a codec per row. `Tokenize` validates the actual
   first-row field count and exact alias at each expected ordinal, then writes the
   already-selected member indexes into the runtime token buffer and calls
   `services.ValidateReaderColumn(reader, ordinal, expectedColumn, member)` for
   actual representation checks. `Read` uses cached tokens and the already-bound
   typed delegates, typed locals and one constructor/object initializer. The typed
   delegate alone handles DBNull: a non-null descriptor fails KORM-MAP-003; a
   permitted nullable representation returns default(TMember). The generator does
   not introduce a second null-conversion policy. No reflection, `Activator`, dynamic IL or `Convert.ChangeType` path
   is emitted.
7. Emit the immutable mapping descriptor alongside the factory. Its aliases,
   CLR/nullability requirements and conversion IDs are the execution preflight
   input. Multiple SQL types may map to one CLR type only through the declared
   compatible conversion; do not reject that legitimate case merely because SQL
   IDs differ.
8. Collect only registration descriptors and emit one module initializer in
   ordinal CLR-name order. Call each generated registrar EnsureRegistered; its explicit static constructor
   registers once in `Mapping<T>`. Add the compile-time referenced-registrar roots
   described above; no runtime `Type` dictionary or assembly scan. Compiled mapping descriptors are singletons; bound row factories are immutable
   per-projection/provider values and per-reader token state is local. No global
   shape cache or singleton mutation is introduced.
9. Add exact terminal diagnostics for known closed DTO use. A generic helper
   need not become an interceptor: default mapping lookup remains in the runtime,
   with its missing-map preflight error. An explicit manual-mapping overload is
   accepted without requiring `[DbRow]`.
10. Emit deterministic source, XML comments and escaped names. A hint name is
    formed from a stable metadata ID/hash, not an absolute filesystem path or
    traversal counter. Preserve source/NOTICE attribution for adapted upstream
    algorithms. Do not copy an upstream source tree into the module.

The effective read-conversion algorithm is shared with the Execution scalar,
closed Row, explicit mapping and dynamic-record factories. Apply it to every
generated DTO and nested scalar leaf. Preserve the projection's ID even when a
DTO member has no DbColumn.ConversionId: explicit Cast projections carry
`cast.int16.checked` or `cast.int32.checked`, and aggregates carry their fixed
`aggregate.*` IDs. For a nested scalar leaf, assemble its logical column with the
leaf's conversion ID before validation/binding; actual reader validation still
uses its physical column descriptor. Equal IDs do not create two conversion
steps. A custom composed codec requires one explicitly registered ID; two
different metadata IDs never imply composition or precedence. A null effective
ID selects the ordinary strict reader.

Nested mapping is a separate explicit input contract from `ORM-NESTED`.
`NestedRow<T>` requires its declared presence discriminator; `NestedCollection<T>`
requires its explicit payload schema and generated typed decoder. A normal
`[DbRow]` does not imply recursive property scanning or Dapper multi-mapping.
Without the required `[DbNested]`/`Nested.Project<T>`/`Collect<T>` shape descriptor,
a nested property is rejected with ORMGEN004. The nested module owns payload and
presence semantics; this generator emits a call to that statically planned decoder
inside `Read`, without adding a reader loop.

The implementation uses normal `RegisterSourceOutput`, not experimental
`RegisterPreCompilationSourceOutput`, recursive generator execution, a custom
MSBuild compile stage or custom interceptors. Those are researched alternatives,
not tasks still waiting for an architectural decision.

## Exact schema-generated API and name scopes

For generation namespace N, emit `N.Tables`, descriptor wrapper classes in
`N.TableRefs`, result records in `N.Rows`, and declared enum/type metadata in
`N.Types`. `SchemaIdentifierMap` preserves each legal original spelling unless
an explicit override applies. It does not guess singular English words or change
case. For relation name R:

- `N.Tables.R` is a public static get-only property of `N.TableRefs.R`.
- `N.TableRefs.R` is a public sealed class with an internal constructor accepting
  Table, a public get-only Table property, one public get-only Field<TColumn>
  property per visible column, a public `R As(string alias)` method, and a public
  static get-only SchemaRelation Metadata property. As creates a new wrapper over
  Table.As(alias); it keeps every field on the alias's new RelationId.
- Its default instance calls `Table.Define(qualifiedSqlName, keys)`. Emit each
  real primary/unique column key as TableKeyDefinition(ordered SQL column names,
  IsPrimary, AllNotNull, IsPartial=false). Schema v1 emits only complete simple-column
  keys; it does not pretend a filtered/expression index is such a key. Primary/unique
  semantics and nullable columns come from the snapshot. Hand-declared partial keys
  do not prove presence/cardinality; an
  expression index is never fabricated as a list of simple column names.
- When GenerateRows=true, `N.Rows.R` is a public sealed positional record with
  one parameter/property for each visible column in ordinal order. CLR names
  come from the same column name map; row mapping aliases remain exact original
  SQL column names. Hidden columns stay in Metadata but are not projected into
  the default row. The corresponding table-wrapper fields use those same types.
- Metadata is emitted as immutable constructor data, including ordered keys/FKs;
  the generated application does not parse its schema JSON or connect to discover
  metadata at startup. Unknown/unresolved bindings fail generation.

A wrapper is used as `Sql.Select(Tables.R.Id, Tables.R.Name).From(Tables.R.Table)`;
an alias is `var u = Tables.R.As("u")` followed by fields from u and `.From(u.Table)`.
Do not add a generated inheritance hierarchy, per-table execution facade or
conversion to a different query object. The ordinary generic Query<T> terminal
remains unchanged.

The identifier allocator groups relation names in each Tables/TableRefs/Rows
scope, type names in Types, and columns within their owning relation. Equal column
names in different relations are not collisions. Each input snapshot allocates
its complete scopes deterministically. Collect small output-name claims across
AdditionalFiles before emission; two files claiming the same fully qualified CLR
output name produce ORMGEN003 unless their explicit namespace/name overrides
separate them. Do not rename one according to file traversal order. Reserve Table, As and Metadata,
and record/object member names Clone, EqualityContract, PrintMembers, Deconstruct,
ToString, GetHashCode, Equals, GetType, MemberwiseClone and Finalize. An automatic
name colliding with a reserved/emitted name gets the stable ID hash suffix;
a conflicting explicit override is ORMSCHEMA006. Enum label names use the same
escaping/collision rule within their enum, with identity encoded from owning type
ID plus original label. Their numeric CLR values are zero-based declaration order;
original labels are emitted as an immutable typed value/label array, never inferred
through Enum.GetValues or Enum.Parse. Provider conversion still requires its
explicitly declared static binding.

Emit column descriptors through a private generated generic helper that calls
SqlTypes.Define<TColumn> and uses typeof(TColumn). This allows the offline emitter
to express a nullable custom type as `CustomType?` without guessing whether the
CLR symbol is a struct or class; the consuming compiler closes TColumn correctly.
Use the bound static member's declared base descriptor, then apply the schema's
validated facets/nullability and the advanced contract's exact domain/enum/range
identity encoding. A domain does not collapse to the base type's SQL ID just
because its CLR representation is the same. If an explicit binding contradicts
that identity/codec contract, fail validation rather than silently changing it.

Hint names are ASCII role prefixes plus the full lowercase SHA-256 of the stable
schema/CLR metadata identity and `.g.cs`; no absolute path or source traversal
number enters the name. Registrars hash the fully qualified CLR metadata name,
so offline generation does not need the eventual application's assembly version.
CLR symbol comparisons and compiled-marker validation still include assembly
identity. Two different referenced types that cannot be named unambiguously by
the emitted fully qualified C# name fail ORMGEN001; no arbitrary winner is selected.

## Nested and custom-codec boundary

For a flat DTO, each logical member has one physical column. For nested results,
use the exact Contracts ResultShape.Members, ResultMember and
NestedShapeDescriptor declarations in ORM-NESTED. Match the DTO's logical member
count/names to Members; Columns remains the physical reader layout. DbNested
requires the explicit RequiredRow/OptionalRow/Collection contract. Collection
scalar elements are valid and use one-cell row arrays. Parent factories generate
private ReadChild methods and typed ChildReadPlan values, with no call to a
standalone child's Tokenize. Respect the fixed external-child accessibility error
and physical-versus-logical nullability distinction; presence0 skips all child
getters. Call NestedJsonDecoder with a generated static element reader for the
single collection payload. No runtime member scan or object JSON deserializer is
introduced.

Generation validates a custom SqlTypeMember's static symbol, its closed SqlType<T>
type, the target CLR type, and the explicit conversion declaration's syntax. It
cannot prove an arbitrary runtime ProviderServices configuration contains that
codec. ORMGEN004 applies to statically known mismatches or a missing required
conversion declaration. A complete declaration whose selected provider has no
closed codec fails execution preflight with KORM-MAP-002 before command creation. A declared conversion whose
body subsequently fails is KORM-TYPE-005; required DBNull remains KORM-MAP-003. Do not load application plugins or execute user code in the
generator/schema tool to manufacture a compile-time guarantee.

## Required fixtures and exact expected outcomes

| Fixture | Expected result |
| --- | --- |
| `RecordCtor` with `(long Id, string Name, long? Score)` | Compiled factory invokes that constructor; a database NULL produces `null`, never 0 |
| `InitClass` with public init properties | Compiled object initializer; no runtime setter reflection |
| `MarkedConstructor`, `AmbiguousConstructor`, `RequiredWithoutSetsRequiredMembers` | Unique valid mark succeeds; two candidates/marks fail ORMGEN002; required members compile with complete initializer assignments |
| `PrivateNested`, `AbstractRow`, `OpenGenericRow` | ORMGEN001, no executable mapper |
| `WrongCodecSymbol`, `NullableToRequired`, `DuplicateAlias` | Static SqlType<T>/CLR mismatch gives ORMGEN004; known nullable-to-required mismatch gives ORMGEN005; duplicate alias gives ORMGEN003 |
| `MissingRuntimeReadCodec` | Declared fixture.missing conversion compiles; BindReader lookup fails exactly KORM-MAP-002 before CreateCommand |
| `ProjectionReadConversion` | An ordinary DTO with short Small/int Medium and no member conversion IDs consumes projection IDs cast.int16.checked/cast.int32.checked; each BindReader receives the corresponding ID and reads values 123/456. Repeat through supported scalar, closed Row and generated nested scalar-leaf plans; no custom member annotation is required. |
| `AggregateReadConversion` | A nullable decimal DTO member without a conversion ID receives projection ID aggregate.int-sum.decimal; BindReader receives that exact ID once, and an all-NULL integer SUM remains null. |
| `MemberOnlyReadConversion`, `MatchingReadConversions`, `OrdinaryReadWithoutConversion` | A registered fixture.identity.int64 codec receives member-only ID or equal member/column IDs; its counter increments exactly once for each materialized value. With both IDs null, BindReader receives null and uses the ordinary reader. |
| `ConflictingReadConversions` | Column ID cast.int16.checked and member ID fixture.other.int16 fail exactly KORM-MAP-002 in Bind, even when both codecs are individually registered; BindReader calls=0 and CreateCommand calls=0. Run for DTO and nested scalar-leaf bindings. |
| `PhysicalAndIncrementalSameSchema` | ORMGEN009; no duplicate C# types/factories emitted |
| `MissingMappingTerminal`, `RuntimeTypeTerminal` | ORMGEN006 and ORMGEN010; no vanilla Dapper fallback |
| `SchemaNoExecution` | Pure table/field/DTO generation compiles with core only; requesting mappings fails ORMGEN008 |
| `ReorderedProjection`, `UnexpectedActualOrder`, `DuplicateActualColumn`, `MissingActualColumn` | A reordered declared projection gets a corresponding bound plan; any actual ordinal/alias mismatch against that plan fails before first materialization |
| `WrongShapeEmptyResult` | Declared preflight errors still fail; an otherwise valid descriptor with an empty actual reader does not claim runtime schema-drift detection |
| `ExternalModelsGenericTerminal`, `ExternalAnnotationWithoutCompiledMarker` | Consumer SG roots the DTO registrar across a generic helper; an annotation without emitted mapping evidence fails ORMGEN006 at known closed use |
| `LibraryOnlyRegistrationNegative`, `ConsumerRegistrarRoots` | Managed-only success must not be counted as Native AOT retention; consumer-emitted direct roots pass the native case with no handwritten registrar call |
| `ClosedRowTwoAssemblies`, `ClosedRowHint`, `OpenRowHint`, `ManualRowRegistration` | Same closed shape registers once across assemblies; an explicit closed hint works; an open hint fails ORMGEN001; explicit EnsureRegistered works without SG |
| `ScalarArbitraryAlias`, `ScalarNullable`, `UnknownScalar` | Supported scalar accepts the declared one-column alias/nullability; unknown CLR scalar needs an explicit mapping |
| `IncrementalUnrelatedEdit`, `OneRowEdit`, `InputReorder` | Unchanged row outputs are cached; only affected row/registration data changes; canonical order is byte-stable |
| `NoGenerator`, explicit static mapping | Query and execution work through the documented manual overload; no analyzer is a runtime dependency |

The native fixture must use a real database and run fixed/dynamic WHERE, changed
parameter counts, nullable data, expanded/empty lists, two result types, buffered
async, streaming early disposal, cancellation before execution, and a borrowed
transaction/rollback. The local generator fixture uses a small test-only ProviderServices adapter with
closed SQLite scalar codecs from ORM-SQLITE-DRIVER's declared table, over the real
pinned Microsoft.Data.Sqlite connection and the common Execution factory. It does
not require the production provider task to finish, and does not count as that
provider's acceptance. Inspect emitted factories and actual runtime dependency
files. The research's 21-check native slice is evidence of feasibility, not a
replacement for these product fixtures.

## Local commands, CI selection and completion

The task creates and runs these entry points from the product root:

```sh
bash tests/Orm/Generation/check.sh
python3 eng/ci/impact.py origin/main --output artifacts/orm-generation-plan.json
```

`check.sh` builds the actual generator, runs driver/diagnostic/incremental tests,
compiles positive and expected-negative consumers, publishes and executes the
selected Linux native fixture, and returns nonzero on any unexpected diagnostic
or fallback. It must not count a build-failed consumer as a runtime pass. Native
publish warnings are reviewed and treated as failures unless a specific justified
baseline is explicitly part of the contract; no blanket trimming suppression.

Register the generator's source, tests, linked Schema inputs and exact consumers.
A generator change reaches generated native consumers and package acceptance;
a provider-local codec change does not rebuild unrelated providers. Ordinary
prose edits select no product build. Final package-asset acceptance belongs to
`ORM-PACKAGE` and consumes the exact nupkg, not this task's project references.

Stop after its reviewed implementation PR and the declared checks. Do not redesign
terminals, publish packages, add a runtime mapper fallback or start migration.
