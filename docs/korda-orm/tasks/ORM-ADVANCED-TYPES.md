# ORM-ADVANCED-TYPES — explicit advanced database representations

Status: `planned_candidate`; product implementation is **not authorized**.

## Fixed outcome and dependencies

Provide explicit SQL identities, immutable values, statically registered conversion
algorithms and a bounded advanced-expression family. Use Design
`implementation-spec.md`, `contracts.md`, `java-execution-options.md` and
`mature-execution.md` at the immutable batch revision; consume ORM-C01 and
ORM-C03–ORM-C06. Start: `ORM-FOUNDATION`; acceptance: `ORM-EXPRESSIONS` only.
Provider codecs and actual database round trips are independent acceptance gates.
A neutral value being constructible never sets a provider's supported capability.

Own `src/Orm/AdvancedTypes/` and `tests/Orm/AdvancedTypes/`. Reference Contracts,
Types and Language; do not reference Npgsql/MySqlConnector/Sqlite, implement a
reader loop, or enable dynamic provider type discovery. Register shared node tags and immutable record data in Contracts/Nodes/Advanced.cs
through the contract owner; local source files use the default project glob. Node
records contain only contract descriptors, primitives and other SqlNodes, never
an AdvancedTypes runtime codec. Public value/conversion algorithms remain in this
module, so Contracts has no reverse assembly reference.

## Source map and implementation file inventory

Use jOOQ 3.21.10 public source at commit
`3c58109e7ab69772de75e640852935ee7e284177` under `org/jooq` and `org/jooq/impl`.
This is selective semantic inheritance, not a claim that a Java Binding class is
an executable .NET codec.

| Mature symbol | Fixed adaptation |
| --- | --- |
| `Converter.to/from`, `Binding` | Separate user/store conversion from SQL rendering and driver transport; conversions are explicitly registered and statically called |
| `DefaultBinding.InternalBinding.set/get`, `setNull0` | Convert toward the store representation before choosing the typed setter/typed NULL; read typed storage and null state before converting toward the user value |
| `DefaultBinding` JSON/JSONB/array branches | Distinct identities, typed NULL versus JSON null, element/rank information and explicit dialect encoding |
| `DefaultRecordUnmapper` plus `Records.mapping` | Generate direct member reads/constructor calls for declared conversion shapes; do not port reflective member discovery |
| `JSONArray`, `JSONValue`, `JSONExists` and provider-specific binding branches | Preserve JSON value versus scalar extraction and existence semantics; only the fixed path subset below is admitted |

Required files and types:

| File | Methods/data to implement |
| --- | --- |
| `JsonText.cs` | readonly `JsonText`, `Parse(string)`, `ParseUtf8(ReadOnlySpan<byte>)`, `Utf8`, `ToString`; privately owned validated UTF-8 |
| `JsonbText.cs` | readonly `JsonbText` wrapping validated JSON bytes with a different SQL identity; no promise of textual equality after server normalization |
| `SqlArray.cs` | readonly `SqlArray<T>`, `Create(IEnumerable<T>)`, `Count`, indexer; snapshot once to ImmutableArray<T> with registered element snapshotting |
| `SqlRange.cs` | `RangeBound<T>`, `SqlRange<T>.Empty`, `Create(lower,upper,comparer)` and explicit infinite/inclusive flags |
| `EnumMap.cs` | `EnumMap<TEnum>.Create`, `ToLabel`, `FromLabel` using supplied exact pairs, not Enum.Parse/GetValues |
| `DomainType.cs` | `DomainType<T>.Create(SqlName,SqlType<T>,validator)` with distinct identity, store type and static validation |
| `StaticConversion.cs` | `StaticConversion<TStore,TUser>`, `NullConversionPolicy` and `ConvertToStore`/`ConvertFromStore` |
| `JsonCodec.cs` | `JsonCodec<T>.Create(JsonTypeInfo<T>)`, `Snapshot`, `Read`; always call metadata-taking System.Text.Json overloads |
| `AdvancedTypeCatalog.cs` | Closed registration entries keyed by SqlTypeId and conversion ID; immutable after construction, no runtime generic-type construction |
| Shared `Contracts/Nodes/Advanced.cs` plus local `AdvancedSql.cs` | `JsonPathNode`, `JsonValueNode`, `JsonTextNode`, `JsonExistsNode`, `ArrayElementNode`, `ArrayContainsNode`, `RangeContainsNode`; named methods below |
| `AdvancedTypeValidator.cs` | Identity/facet/nullability/path/rank/precision validation before render/bind |
| Tests | `JsonNullTests`, `ArraySnapshotTests`, `EnumDomainTests`, `RangeTests`, `TemporalPrecisionTests`, `ConversionOrderTests`, `AdvancedExpressionTests`, `NativeConsumer` |

## Exact value and identity rules

| Family | CLR representation / identity | Baseline and rejection boundary |
| --- | --- | --- |
| JSON | `JsonText`, SQL identity `json`; SQL-null value is `JsonText?` | Parse one complete strict JSON value; JSON token `null` remains a present JsonText value |
| JSONB | `JsonbText`, identity `pg.jsonb` | PostgreSQL binary JSON intent carried as text transport; other profiles reject unless the application explicitly selected `json` instead |
| Array | `SqlArray<T>` plus element SqlTypeId/rank=1 | Empty is Count=0, SQL NULL is nullable wrapper; one-dimensional sequence normalized on read, written with lower bound 1; original SQL lower bound is not retained |
| Enum | Known `TEnum` and `EnumMap<TEnum>` | Exact case-sensitive label map supplied statically; aliases/duplicate values or labels rejected; unknown numeric or database label fails |
| Domain | Existing CLR T plus DomainType<T> | Distinct qualified SQL identity and declared store/base type; same CLR type does not collapse domain identity |
| Range | `SqlRange<T>` and explicit SQL range identity | Empty, unbounded and finite bounds are separate; nullable range is SQL NULL; initial built-in adapters target PG int4range/int8range only |
| Temporal | DateOnly, TimeOnly, DateTime, DateTimeOffset according to distinct SqlTypeId | Date, local timestamp and instant are distinct; no implicit timezone conversion or precision loss |

Qualified enum/domain/range identities use a canonical prefix plus length-prefixed
UTF-8 catalog/name segments; e.g. `pg.enum|6:public|4:mood`. Never join unescaped
names with a dot and pretend identity is unambiguous. Schema generation emits
these identities and the catalog retains the original SqlName for quoting.
SqlTypeDescriptor stores `typeof(T)` only as static metadata; it is not permission
to inspect T's members at runtime.

`JsonText.ParseUtf8` checks the byte limit before copying the caller's bytes, then runs Utf8JsonReader with comments
and trailing commas disallowed, MaxDepth=64, and requires exactly one complete
value followed only by whitespace. String input uses strict UTF-8 encoding and
rejects unpaired UTF-16 surrogates. Max document input is 1,048,576 bytes in the
baseline; larger data requires an explicit revised type/shape budget. Default
uninitialized JsonText/JsonbText values are invalid, not SQL NULL. Exposed memory
is read-only and no provider/reader-owned buffer is retained.

A `JsonCodec<T>` snapshots T by serializing immediately with supplied
JsonTypeInfo<T>; the captured immutable JSON payload is what ParameterValues owns.
It does not keep a mutable T reference across await. Reading calls the matching
metadata-taking Deserialize overload. SQL NULL is handled by the declared null
policy; JSON token null follows the serializer's T contract. No call may use
reflection-only JsonSerializer overloads or Npgsql EnableDynamicJson.

SqlArray enumerates input once and snapshots mutable elements through their
registered converter. An array of a non-null element type rejects a null element;
a nullable element descriptor preserves null elements at their original positions.
Default uninitialized SqlArray/SqlRange values are invalid (KORM-TYPE-001); use
Create or SqlRange<T>.Empty explicitly. Array values are scalar slots and never silently expanded as IN lists. A list
parameter is a separate language construct with a structural length. SqlArray<T>
is a sequence representation: mature Npgsql array readers normalize element order
and do not expose the original SQL lower bound. Reading a database array with a
non-1 lower bound therefore intentionally returns the same sequence and rebinding
writes a 1-based array; it is not a round trip of arbitrary PostgreSQL array bounds.
Do not claim the normal int[] getter can detect and reject a discarded lower bound.
A bounds-preserving/multidimensional SQL-array representation is outside this
initial identity and cannot be enabled without a separate codec contract.

RangeBound has either IsInfinite=true (no value, IsInclusive=false) or a finite
value with an explicit inclusion flag. Empty range has no meaningful bounds.
Create rejects lower>upper and turns equal finite endpoints into Empty unless
both are inclusive. The supplied comparer is a known static comparer for the
registered element type. Do not perform guessed PostgreSQL discrete-range
canonicalization in this neutral module; server canonicalization is checked by
provider round-trip fixtures. A server result with unsupported bound/type/rank
fails explicitly instead of becoming a string.

## Conversion order, null policy and numerical precision

A registration fixes a unique conversion ID, typed ToStore/FromStore delegates,
store/user SqlType descriptors, snapshot function and one NullConversionPolicy.
The delegates are static method groups or explicit generated calls; no assembly
scan, reflected method lookup or Expression.Compile is allowed.

1. Validate source identity and nullability before invoking a conversion.
2. `Reject` fails on NULL. `Propagate` carries NULL without calling the delegate
   and requires nullable store and user descriptors. `Invoke` passes NULL through
   the declared nullable generic type and calls the delegate; registration rejects
   a non-nullable input type for this policy.
3. For a non-null value (or Invoke), call ToStore, then validate the converted
   store value/nullability/facets, then let the provider choose its typed setter or
   typed DbNull. A converter returning null cannot skip the store null check.
4. Reading performs the provider's typed getter and DBNull test first, then the
   same declared null-policy decision, then FromStore and the user-value validation.
5. Wrap conversion failures with `KORM-TYPE-005`, conversion ID, SQL identity,
   parameter or column path and InnerException. Never include full payloads in
   diagnostics. Already typed Korda diagnostics retain their original code.

Integer narrowing is checked and requires a registered explicit conversion.
Decimal(p,s) validates p in 1..28 and s in 0..p for the CLR decimal baseline; values
must fit the declared precision/scale exactly. Reject excess fractional digits
unless they are zero and therefore lose no value. Binary floating values are not
an implicit substitute. SQLite's decimal TEXT transport is explicit and does not
claim its SQL numeric affinity provides exact arithmetic/order.

DateOnly is a calendar date. TimeOnly/local DateTime use declared fractional
precision 0..6; at precision p, ticks must be divisible by 10^(7-p). Local timestamps
require DateTimeKind.Unspecified. Instant values use DateTimeOffset with Offset=0
or DateTimeKind.Utc through its explicit codec; nonzero offset is rejected until
the caller explicitly normalizes it. A database instant does not preserve the
original input timezone/offset. Server infinities, zero dates and out-of-CLR-range
values are unsupported unless a separate explicit representation is registered.
MySQL/Maria DATETIME and TIMESTAMP remain different identities, with session UTC
required for instant transport and documented native range limits.

## Advanced-expression surface and lowering contract

The initial named operations are `Json.Value(document,path)`,
`Json.Text(document,path)`, `Json.Exists(document,path)`, `Arrays.Element(array,
index)`, `Arrays.Contains(array,value)`, and `Ranges.Contains(range,value)`.
They create immutable nodes, never raw SQL. Element and contains type checking uses
the declared element type; array index is a one-based sequence position, Int32
and strictly positive. PG Element lowers to `array[array_lower(array,1)+index-1]`
so a stored non-1 lower bound does not change sequence indexing; the result type
is nullable because an empty/out-of-range subscript yields SQL NULL. Repeated
array/index expressions obey the shared stability and occurrence rules.
JSON paths are immutable sequences of Property(name) or Index(nonnegative int).
The portable Property subset is ASCII `[A-Za-z_][A-Za-z0-9_]*`; arbitrary quoted
keys, recursive descent, wildcards, filters and negative indices are rejected with
`KORM-TYPE-006`. Path identity is structural and included in the template hash.

| Operation | PostgreSQL | SQLite | MySQL / MariaDB |
| --- | --- | --- | --- |
| JSON value preserving JSON null | `doc #> text[] path` | `CASE json_type(doc,path) WHEN 'true' THEN 'true' WHEN 'false' THEN 'false' ELSE CASE WHEN json_type(doc,path) IS NULL THEN NULL ELSE json_quote(json_extract(doc,path)) END END` | `JSON_EXTRACT(doc,path)` |
| JSON text/scalar | `doc #>> text[] path` | `CASE json_type(...) WHEN 'true' THEN 'true' WHEN 'false' THEN 'false' WHEN 'array' THEN NULL WHEN 'object' THEN NULL ELSE CAST(json_extract(...) AS TEXT) END` | `JSON_UNQUOTE(JSON_EXTRACT(doc,path))` with explicit JSON-null -> SQL NULL CASE |
| JSON exists | `(doc #> path) IS NOT NULL` | `json_type(doc,path) IS NOT NULL` | `COALESCE(JSON_CONTAINS_PATH(doc,'one',path),0)=1` |
| Array element/contains | Offset-by-array_lower subscript / native typed contains | Unsupported | Unsupported |
| Range contains | Native typed range contains | Unsupported | Unsupported |

JSON Text has fixed NULL-on-nonscalar semantics: string returns its content,
number returns invariant server scalar text, Boolean returns `true`/`false`, and
JSON null/missing/SQL NULL/object/array return SQL NULL. For PG wrap `#>>` in CASE
on json_typeof/jsonb_typeof of `#>`: object/array -> NULL, otherwise `#>>`. For
MySQL/Maria wrap JSON_UNQUOTE in CASE on JSON_TYPE(JSON_EXTRACT(...)):
NULL/OBJECT/ARRAY -> SQL NULL, otherwise JSON_UNQUOTE. SQLite uses the CASE shown
in the table. These are explicit API semantics, not a forgotten type check.
JSON Value preserves containers and literal JSON null. If a lowering repeats the
document expression, admit only a stable expression or existing projected alias
under the same stability rule as null-order lowering; otherwise KORM-TYPE-006.
Every repeated parameter appearance still gets its own physical occurrence.
Compare decoded JSON structure, not formatting or object-key order.

Arrays.Contains(array,value) is exactly `value = ANY(array)`, retaining SQL
three-valued logic for a NULL array/value or a nonmatching NULL-bearing array;
it is not set containment of two arrays. Ranges.Contains(range,value) is PG's
`range @> value`, with its declared range/element identity and SQL NULL semantics.
Only the PG provider enables initial array/range transport after its actual static
codec round trips pass. An explicit portable enum-as-text conversion may be used
on any provider, but retains a distinct conversion ID and validates labels. Native
PG enum/domain support is independently declared; lack of an AOT mapping feature
is not permission to enable unmapped/dynamic types. Reuse the mature provider's
supported closed mapping API and typed values.

## Exact diagnostics and acceptance fixtures

| Code | Fixed message template |
| --- | --- |
| `KORM-TYPE-001` | `Type '{type}' has an invalid facet or uninitialized value at '{path}'.` |
| `KORM-TYPE-002` | `JSON at '{path}' is invalid or exceeds the declared byte/depth budget.` |
| `KORM-TYPE-003` | `Value at '{path}' cannot be represented exactly as '{type}'.` |
| `KORM-TYPE-004` | `No static codec for '{type}' is registered in profile '{profile}'.` |
| `KORM-TYPE-005` | `Conversion '{conversion}' failed at '{path}'.` |
| `KORM-TYPE-006` | `Advanced operation '{operation}' is outside the declared type/path/rank subset.` |
| `KORM-TYPE-008` | `Database label '{label}' is not declared by enum '{type}'.` |

Mandatory cases: SQL NULL vs JSON `null` vs JSON `"null"`; `{}` missing key vs
`{"x":null}` existing null; Boolean scalar text and NULL-on-container text extraction; empty and nullable-element arrays;
source array mutation after capture; a one-shot enumerable; unknown/duplicate enum
labels; two domains sharing Int64 but different SQL identities; empty/unbounded/
finite ranges; Int64 limits; Decimal(5,2) values 999.99 accepted, 1000 or 1.001
rejected; local/UTC/wrong-kind time; p=6 exact microsecond accepted and one extra
tick rejected; NULL-mapping converter call order; malformed UTF-8/JSON/depth65;
missing static JsonTypeInfo/codec; unsupported array rank and JSON path; non-1 PG lower bound read as normalized sequence and sequence-position Element lookup.

A driver-free Native AOT consumer constructs, binds/snapshots, converts and decodes
these values using real static System.Text.Json metadata. Inspect trimming and
dynamic-code warnings. Per-provider fixtures are supplied as data and remain
unaccepted until the corresponding actual codec/database lane passes. Do not add
a duplicate Korda execution loop to test codecs; compose the mature Dapper.AOT
factories and provider seams. Raw logs remain scratch.

Primary inputs: [jOOQ Converter](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/Converter.java),
[DefaultBinding](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/impl/DefaultBinding.java),
[Npgsql AOT restrictions](https://www.npgsql.org/doc/compatibility.html),
[Npgsql JSON mapping](https://www.npgsql.org/doc/types/json.html),
[PostgreSQL JSON operators](https://www.postgresql.org/docs/18/functions-json.html),
[SQLite JSON semantics](https://www.sqlite.org/json1.html).

## Exact local runner contract

This task owns `tests/Orm/AdvancedTypes/verify.py`,
`tests/Orm/AdvancedTypes/Korda.Orm.AdvancedTypes.Tests.csproj` and its Program/fixture files.
The CI command, from repository root with no additional flags, is:

```sh
python3 tests/Orm/AdvancedTypes/verify.py
```

The runner compiles the packet's positive/negative declaration cases, publishes
its actual consumer with `dotnet publish tests/Orm/AdvancedTypes/Korda.Orm.AdvancedTypes.Tests.csproj -c Release -r linux-x64 -p:PublishAot=true`,
then executes that native consumer and asserts RuntimeFeature.IsDynamicCodeSupported
is false. Use the repository's pinned SDK/restore settings; place outputs under
artifacts, never beside source. Run this packet's enumerated pure fixtures and
report individual case failures with nonzero exit. The runner does not start a
database, accept an absent peer as a passing stub, or claim live SQL correctness.
Real four-server rows, faults and SQL execution remain ORM-INTEGRATION's gate.
