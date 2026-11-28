# ORM-SCHEMA — canonical offline schema v1

Status: `planned_candidate`; `implementation_authorized: false`.

## Fixed outcome and dependencies

Implement exactly the schema v1 format, naming algorithm and canonicalization in
the graph-pinned Design `generation-integration.md` section 7. Read ORM-C01,
ORM-C05/ORM-C06 and the fixed type/identity definitions in `implementation-spec.md`.
Use jOOQ 3.21.10 `Database`, `AbstractDefinition`, table/column/key definitions,
`PostgresDatabase` and `SQLiteTableDefinition` as metadata-semantic sources.
The format is a C#-appropriate offline contract; do not claim jOOQ exposes this
JSON format or transplant JDBC objects into it.

Start after `ORM-FOUNDATION`; acceptance requires `ORM-TYPES`. No database,
provider adapter, schema CLI or generator implementation is a startup dependency.
Typed test fixtures are sufficient to implement the full neutral format.

## Exact files and public surface

Own `src/Orm/Schema/**` and `tests/Orm/Schema/**`:

| File | Responsibility |
| --- | --- |
| `Korda.Orm.SchemaModel.csproj` | net11.0 pure model/format assembly bundled into the core product; no Dapper/ADO/provider package |
| `Model/SchemaSnapshot.cs` | Version/profile/generation options, type/relation arrays and overrides |
| `Model/SchemaType.cs` | Stable type identity, store name, scalar/array/domain/enum/range/unresolved kind, facets and codec requirement |
| `Model/SchemaRelation.cs` | Exact qualified name, ordered columns, keys, foreign keys and provider-neutral options |
| `Model/SchemaIdentity.cs` | Length-prefixed identity construction and equality |
| `Format/SchemaSnapshotCodec.cs`, `SchemaReader.cs`, `SchemaWriter.cs` | Public codec facade, strict JSON read and deterministic UTF-8 write using System.Text.Json |
| `Format/SchemaValidator.cs` | Structural/type/reference/profile validation and stable diagnostic ordering |
| `Format/SchemaNormalizer.cs` | Collection order, override application and canonical writer input |
| `Generation/SchemaBindingResolver.cs` | Resolve column override, type override and stored type binding in that order; no CLR reflection |
| `Generation/IdentifierMap.cs` | Fixed C# escaping/collision algorithm; retains original SQL identity |
| `Diagnostics/SchemaDiagnostic.cs` | Stable code, safe message, JSON pointer and optional object ID |

Provide `SchemaSnapshotCodec.Read(ReadOnlySpan<byte>) : SchemaReadResult`,
`SchemaSnapshotCodec.Write(SchemaSnapshot) : byte[]`,
`SchemaSnapshotCodec.Fingerprint(SchemaSnapshot) : string`, and
`SchemaIdentifierMap.Create(SchemaSnapshot) : IReadOnlyDictionary<SchemaId,string>`.
`SchemaReadResult` contains either a validated snapshot or structural errors plus
an immutable diagnostic list. It cannot contain a successful snapshot with fatal
errors. `Write` validates manually created inputs and throws the shared schema
validation exception before producing bytes when they are invalid. All public
models are immutable; constructors copy supplied mutable collections.

The generator links the small Format/model/naming source subset rather than
loading the net11 runtime assembly into its netstandard2.0 host. Keep that subset
portable and free of driver/network/filesystem operations. The generator owner
owns its build references and package closure; this task owns format semantics.

## Exact portable declarations and wire representation

The following declaration slice was compiled against net11.0 and netstandard2.0
reference assemblies with warnings treated as errors; both produced zero warnings.
It fixes the shared model names and parameter order. The `NotImplementedException`
bodies are declaration-check placeholders, not proposed implementations. Implement
them with the algorithms below. The generator links these same source definitions,
using its internal `IsExternalInit` shim when targeting netstandard2.0.

```csharp
using System;
using System.Collections.Generic;
using System.Collections.Immutable;

namespace Korda.Orm.Schema;

public readonly record struct SchemaId(string Value);
public sealed record SchemaQualifiedName(string? Catalog, string? Schema, string Name);
public sealed record SchemaSetting(string Name, string Value);
public sealed record SchemaProfile(string Id, string Family, string ServerVersion,
    ImmutableArray<SchemaSetting> Settings);
public sealed record SchemaGenerationOptions(string Namespace,
    bool GenerateRows, bool GenerateMappings);
public sealed record SchemaNameFilter(string? CatalogPattern,
    string? SchemaPattern, string NamePattern);
public enum UnresolvedTypePolicy { Error, Record }

public sealed record SchemaTypeBinding(string ClrTypeName, string SqlTypeMember,
    string? CodecId = null);
public sealed record SchemaOverride(SchemaId Target, string? ClrName = null,
    SchemaTypeBinding? TypeBinding = null);
public enum SchemaTypeKind { Scalar, Array, Domain, Enum, Range, Unresolved }
public sealed record SchemaTypeFacets(int? Length = null, int? Precision = null,
    int? Scale = null, bool? Unsigned = null, int? FractionalSeconds = null,
    string? CharacterSet = null, SchemaQualifiedName? Collation = null);
public sealed record SchemaType(SchemaId Id, SchemaQualifiedName StoreName,
    SchemaTypeKind Kind, SchemaId? BaseTypeId, SchemaId? ElementTypeId, SchemaId? RangeSubtypeId,
    ImmutableArray<string> EnumLabels, ImmutableArray<int?> Dimensions,
    SchemaTypeFacets Facets, SchemaTypeBinding? Binding);

public enum SchemaRelationKind { Table, View }
public enum SchemaColumnGenerationKind
{
    None, Default, IdentityAlways, IdentityByDefault,
    ComputedStored, ComputedVirtual
}
public sealed record SchemaIdentityOptions(string? Start, string? Increment,
    string? Minimum, string? Maximum, string? Cache, bool? Cycle);
public sealed record SchemaColumnGeneration(SchemaColumnGenerationKind Kind,
    string? Expression, SchemaIdentityOptions? Identity);
public sealed record SchemaColumnOptions(bool? SqliteRowIdAlias = null,
    bool? SqliteAutoIncrement = null);
public sealed record SchemaColumn(SchemaId Id, int Ordinal, string Name,
    SchemaId TypeId, bool Nullable, SchemaTypeFacets Facets,
    ImmutableArray<int?> Dimensions, SchemaColumnGeneration Generation,
    bool Hidden, SchemaColumnOptions Options, string? ClrName = null);
public enum SchemaKeyKind { Primary, Unique }
public sealed record SchemaKey(SchemaId Id, string? Name, SchemaKeyKind Kind,
    ImmutableArray<SchemaId> Columns);
public enum SchemaReferentialAction { NoAction, Restrict, Cascade, SetNull, SetDefault }
public enum SchemaForeignKeyMatch { Unspecified, Simple, Full, Partial }
public sealed record SchemaForeignKeyTargetColumn(SchemaId Id, string Name,
    SchemaId TypeId, SchemaTypeFacets Facets, ImmutableArray<int?> Dimensions);
public sealed record SchemaForeignKey(SchemaId Id, string? Name,
    ImmutableArray<SchemaId> SourceColumns, SchemaId TargetRelationId,
    SchemaQualifiedName TargetRelationName,
    ImmutableArray<SchemaForeignKeyTargetColumn> TargetColumns,
    SchemaId? TargetKeyId, bool ExternalTarget,
    SchemaReferentialAction OnUpdate, SchemaReferentialAction OnDelete,
    SchemaForeignKeyMatch Match, bool? Deferrable, bool? InitiallyDeferred);
public sealed record SchemaRelationOptions(bool? WithoutRowId = null,
    bool? Strict = null);
public sealed record SchemaRelation(SchemaId Id, SchemaRelationKind Kind,
    SchemaQualifiedName Name, ImmutableArray<SchemaColumn> Columns,
    ImmutableArray<SchemaKey> Keys, ImmutableArray<SchemaForeignKey> ForeignKeys,
    SchemaRelationOptions Options);
public sealed record SchemaSnapshot(int FormatVersion, SchemaProfile Profile,
    SchemaGenerationOptions Generation, ImmutableArray<SchemaType> Types,
    ImmutableArray<SchemaRelation> Relations, ImmutableArray<SchemaOverride> Overrides);

public enum SchemaDiagnosticSeverity { Warning, Error }
public sealed record SchemaDiagnostic(string Code, SchemaDiagnosticSeverity Severity,
    string Message, string JsonPointer, SchemaId? ObjectId = null);
public sealed record SchemaReadResult(SchemaSnapshot? Snapshot,
    ImmutableArray<SchemaDiagnostic> Diagnostics);
public sealed class SchemaValidationException : Exception
{
    public SchemaValidationException(ImmutableArray<SchemaDiagnostic> diagnostics)
        : base("Schema validation failed.") => Diagnostics = diagnostics;
    public ImmutableArray<SchemaDiagnostic> Diagnostics { get; }
}

public static class SchemaSnapshotCodec
{
    public static SchemaReadResult Read(ReadOnlySpan<byte> utf8) => throw new NotImplementedException();
    public static byte[] Write(SchemaSnapshot snapshot) => throw new NotImplementedException();
    public static string Fingerprint(SchemaSnapshot snapshot) => throw new NotImplementedException();
}
public static class SchemaSnapshotValidator
{
    public static ImmutableArray<SchemaDiagnostic> Validate(SchemaSnapshot snapshot,
        UnresolvedTypePolicy unresolvedTypes = UnresolvedTypePolicy.Record)
        => throw new NotImplementedException();
}
public static class SchemaSnapshotTransform
{
    public static SchemaReadResult Apply(SchemaSnapshot snapshot,
        ImmutableArray<SchemaNameFilter> includes,
        ImmutableArray<SchemaNameFilter> excludes,
        ImmutableArray<SchemaOverride> overrides,
        UnresolvedTypePolicy unresolvedTypes)
        => throw new NotImplementedException();
}
public static class SchemaIdentifierMap
{
    public static IReadOnlyDictionary<SchemaId, string> Create(SchemaSnapshot snapshot)
        => throw new NotImplementedException();
}

public static class SchemaIdentity
{
    public static SchemaId Type(SchemaQualifiedName name) => throw new NotImplementedException();
    public static SchemaId Relation(SchemaRelationKind kind, SchemaQualifiedName name) => throw new NotImplementedException();
    public static SchemaId Column(SchemaId relation, string name) => throw new NotImplementedException();
    public static SchemaId Key(SchemaId relation, SchemaKeyKind kind, string? name,
        ImmutableArray<SchemaId> columns) => throw new NotImplementedException();
    public static SchemaId ForeignKey(SchemaId relation, string? name,
        ImmutableArray<SchemaId> sourceColumns, SchemaId targetRelation,
        ImmutableArray<SchemaId> targetColumns) => throw new NotImplementedException();
}
public static class SchemaBindingResolver
{
    public static SchemaTypeBinding? Resolve(SchemaSnapshot snapshot, SchemaId target)
        => throw new NotImplementedException();
}
```

All arrays must be initialized immutable arrays; `default(ImmutableArray<T>)` is
invalid and is not normalized silently to empty. `SchemaId` is a portable database
metadata identity, distinct from the query AST's runtime `RelationId`/`SlotId`.
No schema model contains `System.Type`, `DbConnection`, a driver object or a runtime
core-assembly reference. `SchemaProfile.Family` accepts exactly `PostgreSql`,
`Sqlite`, `MySql`, or `MariaDb`; the execution adapter converts this closed set to
`DatabaseFamily` and rejects a mismatch. `ServerVersion` records the provider's
nonsecret product-version text; the adapter also verifies the normalized version
against the requested `SqlProfile` before returning it.

Every record property is a required JSON property, written in the declaration
order above with its first ASCII character lowercased. Thus `TypeId` is `typeId`,
`SqliteRowIdAlias` is `sqliteRowIdAlias`, and `TargetRelationId` is
`targetRelationId`. A `SchemaId` is a JSON string containing `Value`, not an object.
Enums are their exact first-character-lowercase spelling, except the four profile
family strings above. Arrays are JSON arrays; nullable fields are explicit null.
No serializer reflection or dictionary iteration chooses property order.

`SchemaType.Binding` is the resolved built-in or explicit CLR/SQL-type binding;
null is retained when resolution needs an override. `ClrTypeName` is a fully
qualified C# type name, `SqlTypeMember` is a fully qualified static field/property
of `SqlType<T>`, and `CodecId` identifies the explicit conversion when required.
The generator resolves those symbols and requires exact T compatibility; arbitrary
C# expressions, invocation text and unregistered conversion IDs are rejected.
SchemaBindingResolver.Resolve accepts a column or type ID. It first selects a
column-specific TypeBinding override, then its type's override, then the type's
stored Binding; unsupported/absent bindings remain null. A type-ID request skips
the column step. This lookup is not a runtime provider registration check.
Overrides replace only generation spelling/binding, never the physical type ID,
store name, facets or foreign-key identity. A column override takes precedence
over its type's binding; two overrides of the same target are an error.

Type-level facets describe the declared type/domain. Column facets describe the
column's typmod or storage declaration; null fields inherit applicable type-level
facets. Consequently varchar(40) and varchar(80) may share one physical TypeId and
still generate different validated descriptors. Dimensions retain declared order;
null means a dimension length is unspecified. Empty dimensions mean no declared
array rank information, not a scalar cast. Enum labels retain source order. Range types retain RangeSubtypeId; unsupported
multiranges remain an explicit unresolved requirement.

Identity numeric fields are invariant integer strings (`0` or an optional minus
followed by a nonzero digit and digits), retaining exact size without floating
point. Null means the database does not expose that structural attribute. Never
capture a sequence's current/next value or a table's current auto-increment counter.
`generation.kind=default` with `expression="NULL"` differs from `none` with a null
expression. SQLite rowid alias and AUTOINCREMENT are independent column options;
only SQLite populates them and the two relation options, otherwise all are null.

`TargetColumns` retains source-declared order with complete target identity and
type usage. If a target is internal, every target column must match its relation.
If `TargetKeyId` is supplied it must match that internal key; a null key ID does
not invent uniqueness when a dialect permits a nonstandard referenced index.
An external target keeps the same metadata and has `ExternalTarget=true`; no
internal relation is fabricated to satisfy resolution. Nullable deferrability
means not exposed/applicable, not a false claim that the constraint is immediate.

### Stable identity and selection algorithms

Build an ID as the lowercase kind token plus `|`, followed by each part encoded
as `<UTF8-byte-count>:<exact-text>`, or `-1:` for null. Do not join unescaped names
with dots. Type/relation IDs use `(catalog,schema,name)`; column IDs use
`(relationId.Value,name)`; named or unnamed key IDs use
`(relationId.Value,kind,name,ordered column IDs...)`; foreign-key IDs use
`(relationId.Value,name,ordered source IDs...,targetRelationId.Value,ordered target
IDs...)`, with the two degrees included as decimal parts before their sequences.
Kind tokens are `type`, `table`, `view`, `column`, `key`, and `foreign-key`.
A key's column count is likewise an explicit part before its sequence. Null and
empty names remain different. A byte-count prefix prevents delimiter ambiguity.

`SchemaSnapshotTransform.Apply` performs these steps once, in order:

1. Validate the unfiltered snapshot structurally with unresolved declarations
   allowed, and build relation/type maps. The supplied overrides argument is the
   complete authoritative list, replacing snapshot.Overrides rather than appending
   it. Reapplying the same list is idempotent; duplicate targets within that list
   are errors. An acquisition adapter calls this transform once before returning;
   SchemaTool does not apply it a second time.
2. Select every relation when `includes` is empty; otherwise select relations
   matched by at least one include. Remove anything matching any exclude.
3. Preserve selected relations' foreign keys. Mark a target outside the selection
   external and copy its ordered target-column metadata from the coherent input.
   Retain the transitive closure of type/base/element/range-subtype references needed by selected
   columns, keys and external target columns. Do not reinclude the target relation.
4. Resolve overrides only against the retained identities. An absent/excluded
   target, duplicate target or incompatible override produces ORMSCHEMA006.
5. Store the validated override list on the copied snapshot, resolve effective
   spellings/bindings through the shared resolver and validate again using the
   requested unresolved policy. Error diagnostics produce `Snapshot=null`;
   warnings may accompany a non-null snapshot. Normalize before returning.

A filter contains three patterns, corresponding exactly to catalog/schema/name.
Null matches only a null catalog/schema; an empty string matches only an empty
segment. `*` matches zero or more Unicode scalars within one non-null segment;
`\*` and `\\` match literal asterisk and backslash. Other backslash escapes
or a trailing backslash are invalid. Match ordinally without Unicode/case
normalization. Use the standard single-star-backtrack matcher (input index,
pattern index, last-star index and retry input index), never a regex or SQL LIKE.
Advance UTF-16 indexes by a complete validated Unicode scalar, including surrogate
pairs; a wildcard retry does not split a supplementary character.

## Required data, without implementation discretion

The root fields are `formatVersion`, `profile`, `generation`, `types`, `relations`
and `overrides`. Implement every required field and tagged value in Design.
Version is integer 1. The profile records its family/version and relevant
nonsecret semantic settings. It never contains a connection string or a timestamp.

Stable qualified identities retain catalog/schema/local text and null-segment
identity. SQL type identity is not inferred from a CLR name. Columns retain ordinal,
nullability, type reference, exact default/computed/identity kind and hidden state.
Keys and foreign keys retain declared column order. Explicitly external FK
targets preserve qualified names and ordered column/type metadata; only internal
targets require a relation present in the snapshot. Enums retain label order;
domains/arrays retain base/element identity. SQLite `withoutRowId`, `strict`,
generated/hidden columns and INTEGER PRIMARY KEY distinctions are independent.

An unresolved SQL type is represented explicitly, never converted to `object` or
string. Structural read/write can preserve it for review, but generation requires
a valid explicit type/codec mapping and fails otherwise. This is distinct from an
unknown JSON field or invalid format version, which is a structural error.

## Implementation sequence

1. Add immutable records/tagged values and constructors that enforce local field
   invariants. Use the shared SQL type/identity primitives; do not duplicate them.
2. Implement the reader with maximum JSON depth 64. Disallow comments, trailing
   commas, duplicate properties, unknown version-1 fields, nonfinite numeric
   facets and malformed Unicode. Track JSON pointers while reading. A malformed
   property produces a safe diagnostic without including its raw value.
3. Build ID maps once. Reject duplicate IDs/ordinals; resolve type, base/element,
   key, foreign-key and override targets. Check equal foreign-key degrees and
   valid referenced internal target keys. External targets require complete
   explicit identity/column metadata and must not pretend to be resolved internal
   references. Detect illegal array/domain/range-subtype reference cycles.
4. Apply reviewed overrides to copied values. Validate target existence, exact
   naming constraints and explicit conversion/codec IDs. A spelling override
   cannot change a SQL object's identity or hide a collision.
5. Normalize types/relations/keys/foreign keys/overrides by stable ID using ordinal
   comparison. Normalize columns by ordinal. Preserve semantic sequences such as
   key columns, enum labels and dimensions.
6. Write fields in the exact Design order with explicit nulls, two-space
   indentation, UTF-8 without BOM, LF newlines and one trailing LF. An unchanged
   snapshot produces identical bytes on repeated writes and different cultures.
7. Hash exactly those canonical bytes with SHA-256; return 64 lowercase hex digits.
   Never insert the hash into the content being hashed.
8. Implement C# names: validated override, legal original spelling, `_uXXXX_`
   escaping of illegal scalars, leading `_`, keyword `@`, then deterministic
   stable-ID hash suffix for collisions. Check the final emitted identifier with
   Roslyn in generator tests; Schema itself does not depend on Roslyn.
9. Provide a hand-authored descriptor fixture that produces the same canonical
   model as its JSON form. Neither path requires a live database.

## Diagnostic IDs and required fixtures

| ID | Trigger | Required fixture/result |
| --- | --- | --- |
| ORMSCHEMA001 | Malformed JSON, duplicate property or unknown field | Safe pointer diagnostic; no snapshot |
| ORMSCHEMA002 | Unsupported format version/profile | Version 0/2 and unknown profile fail deterministically |
| ORMSCHEMA003 | Duplicate ID/name/ordinal | Two case-distinct SQL names remain distinct; an exact duplicate fails |
| ORMSCHEMA004 | Missing reference or invalid FK degree/target | Dangling key/type/FK and mismatched source/target degree fail |
| ORMSCHEMA005 | Illegal recursive domain/array or invalid facet | Domain cycle and negative length/precision fail |
| ORMSCHEMA006 | Invalid override or unresolved naming collision | Unknown target, invalid CLR name and conflicting override fail |
| ORMSCHEMA007 | Unresolved SQL type/codec requirement | Preserved explicitly by the model; generation/strict acquisition rejects it until mapped |
| ORMSCHEMA008 | Catalog changed during acquisition or cannot be read coherently | Provider reader fails; no snapshot replacement, CLI exit 3 |

Maintain fixtures `CompositeKeyOrder`, `EnumOrder`, `DomainIdentity`,
`SqliteRowIdKinds`, `GeneratedAndDefault`, `NullVsAbsentCatalog`, `QuotedUnicode`,
`KeywordCollision`, `EscapedNameCollision`, `UnknownType`, `UnknownVersion`,
`DuplicateJsonProperty`, `ReferenceCycle`, `TypmodSamePhysicalType`,
`NullEmptyWildcardFilter`, `ExternalForeignKeyTypeClosure`,
`UnknownOverrideAfterSelection`, `IdentityStructuralOnly` and `CanonicalRoundTrip`.

Expected assertions include: a key `[tenant_id, id]` never becomes `[id, tenant_id]`;
a nullable SQL column stays nullable; default NULL differs from no default;
INTEGER PRIMARY KEY does not imply AUTOINCREMENT; an empty catalog and no catalog
have different IDs; different input object ordering yields the same canonical
bytes; enum label order changes yield different bytes/fingerprint. No timestamp,
secret or machine path is serialized. `Read(Write(valid))` preserves every declared
semantic field, not only names and counts.

## Local commands, selection and stop

```sh
bash tests/Orm/Schema/check.sh
python3 eng/ci/impact.py origin/main --output artifacts/orm-schema-plan.json
```

The task creates `check.sh` to run model/reader/writer/naming fixtures and a
Linux Native AOT consumer of maintained offline snapshots. Use explicit JSON
reading/writing or generated System.Text.Json metadata; do not introduce a
reflection serializer fallback. That consumer has no provider or Dapper package.
A bounded large-schema fixture checks deterministic completion and allocation
regressions; it is not a throughput benchmark.

Propose module `orm-schema` with source/test paths and its actual type-model
prerequisite to the CI owner. Schema source changes reach generator linked-source
consumers and the schema tool; schema tests alone select the schema check. No
unrelated provider service is required. Deliver canonical fixtures to generator
and tool owners without waiting for acquisition.

Stop at the reviewed implementation PR. Do not add a migration/diff engine,
connect to a database, change the format ad hoc or publish a package.
