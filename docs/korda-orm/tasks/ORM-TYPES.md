# ORM-TYPES: Implement fixed SQL types, value policies and conversions

Status: `planned_candidate`; product implementation remains unauthorized.

Use the immutable Design commit in `../implementation-graph.json`, contracts v0.2.0,
and `docs/korda-orm/implementation-spec.md`. The packet fixes implementation work;
contradictions return to the contract owner before changing an interface or policy.

## Inputs, dependencies and owned files

Start after Foundation. Acceptance requires the actual Foundation contracts, not
providers. Own `src/Orm/Types/` and `tests/Orm/Types/`; shared handles in Contracts
are consumed, not redefined. Inputs: ORM-C01/C03/C06, implementation-spec §§3–5,
`language-model.md`, advanced-type packet and the pinned jOOQ sources below.

| File | Exact responsibility |
| --- | --- |
| `SqlTypes.cs` | Static predefined descriptors and explicit custom/domain creation |
| `SqlType.cs` | Descriptor compatibility, CLR carrier/nullability and facet validation |
| `ConversionCatalog.cs` | Immutable explicit converter IDs, snapshot/read/write policy; no runtime type discovery |
| `LiteralValue.cs` | Typed literal canonical data used by fingerprinting; not bound values |
| `tests/Orm/Types/Program.cs` | Native semantic assertions |
| `tests/Orm/Types/CompileCases/` | Matching/mismatched/nullability generic consumers |
| `tests/Orm/Types/verify.py` | Local compile-negative and native entry |

## Source inheritance

Use jOOQ `DataType`, `AbstractDataType`, `DefaultDataType`, `SQLDataType`, `Val`,
`AbstractParam` and Converter at commit `3c58109e7ab69772de75e640852935ee7e284177`.
Preserve SQL identity/facets/nullability and explicit conversion composition.
Replace Java class/reflection/JDBC state with static CLR carriers and provider-free
metadata. The source paths and symbol explanations are in Design's language map;
record deliberate differences beside their tests.

## Fixed type table

| SQL identity | CLR carrier | Required policy |
| --- | --- | --- |
| int16/int32/int64 | short/int/long; nullable variants | No implicit cross-width operand coercion; explicit Cast required |
| uint64 | ulong / ulong? | MySQL/Maria transport only when the selected profile declares it; other profiles reject or use explicitly declared numeric conversion |
| boolean | bool / bool? | SQL truth/nullability remains distinct from C# control flow |
| float32/float64 | float/double | Preserve supported nonfinite values only on a profile with an explicit literal/transport policy |
| decimal | decimal / decimal? | Precision 1..38 and scale 0..precision in model; provider narrower limits checked separately |
| text/binary | string / byte[] with nullable descriptor variants | Length positive if supplied; text length counts Unicode scalar values, binary length counts bytes; snapshot byte arrays |
| uuid/date/time/timestamp/timestamptz | Guid/DateOnly/TimeOnly/DateTime/DateTimeOffset | Timestamp policies and precision exactly as the advanced packet; no machine-local timezone assumption |
| json/array/range/enum/domain | Declared neutral carrier from advanced packet | Distinct SQL identity even when CLR carrier equals a scalar type |

`SqlType<T>` always has Descriptor.ClrType==typeof(T). CLR nullable value types and
SqlNullability must agree. Reference annotations alone cannot establish SQL
nullability. Unknown nullability cannot be silently promoted to NonNull.

## Exact public construction and static conversion policy

`SqlTypes.Define<T>(SqlTypeDescriptor):SqlType<T>` validates exact typeof(T), SQL ID,
nullability and facets. `Nullable<T>(SqlType<T>) where T:struct` returns SqlType<T?>;
`NullableReference<T>(SqlType<T>) where T:class` returns SqlType<T?> while preserving
the runtime typeof(T). No provider encoding is invented by either factory. Include
Int16/Int32/Int64/UInt64/Boolean/Float32/Float64/Decimal/Text/Binary/Uuid/Date/Time/
Timestamp/TimestampTz static members and their declared nullable variants. The
built-in execution scalar mapping list includes short and ulong, but a mapper does
not grant uint64 transport on an unsupported profile.

Text input length validation uses strict Rune.DecodeFromUtf16 iteration, rejects
an unpaired surrogate and never counts UTF-16 code units as SQL characters. Provider
input Size remains unset/0 after this validation; do not truncate text/binary to
satisfy a facet or let Npgsql's Substring-based Size split a surrogate pair.
Converters and snapshots have fixed closed input/output types. Conversion bodies
must be deterministic, pure and free of observable side effects. Preflight and
parameter creation may validate through the same converter; no per-invocation
mutable conversion cache is introduced. A custom mutable input is snapshotted
first, before asynchronous execution or repeated validation. Unsupported source
symbols/declarations fail generation; a codec absent from the selected runtime
provider fails preflight. Do not claim a build-time symbol check proves a runtime
codec registration exists.

## Ordered implementation

1. Validate the descriptor and facet combinations before constructing SqlType<T>.
   Empty SQL IDs, negative length, scale without precision, invalid decimal facets
   and an array without an element identity fail KORM-TYPE-001.
2. Build the static predefined table once. Descriptor equality includes SQL identity,
   nullability and facets; it never uses only typeof(T). Read conversion IDs belong
   to ResultColumn/RowMember and are compared separately. Write codecs are unique
   for the explicitly registered (SqlTypeId, closed T) pair.
3. Implement compatibility as exact SQL type identity/facets unless an explicit
   conversion edge is declared. Cast nodes represent SQL casts; a CLR codec alone
   does not change SQL comparison semantics.
4. Store registered converter IDs in immutable metadata. A converter has fixed
   typed input/output, forward/write, reverse/read, null handling and snapshot
   policy. Compose forward converters in declaration order and read converters in
   reverse order. Verify the declared endpoints before accepting the composition.
5. Required input NULL fails KORM-BIND-004. Nullable input NULL retains declared SQL
   type and bypasses non-null converter bodies unless their explicit policy says
   otherwise. Required result NULL is KORM-MAP-003, not a default value.
6. Snapshot mutable arrays/bytes once. Immutable scalar/string values use identity
   snapshot. Custom mutable references without a declared copier fail KORM-BIND-005.
7. Implement explicit typed-literal encoding for the canonical fingerprint, using
   invariant UTF-8/decimal/numeric/date representations. Driver-specific SQL literal
   spelling remains a dialect responsibility. Distinguish Literal(1) from Literal(2).
8. Add the public XML and positive/negative type consumer cases together. Keep
   NpgsqlDbType, SqliteType, MySqlDbType, DbConnection and Dapper out of this project.

## Required fixtures and expected results

| ID | Case | Expected |
| --- | --- | --- |
| TYP-01 | int32 field vs string param | Compile failure |
| TYP-02 | int32 field vs int64 param | Compile failure without explicit cast |
| TYP-03 | Two text domains with same CLR string | Different SQL identities; no automatic interchange |
| TYP-04 | decimal(12,2), decimal(2,12), length=-1 | First valid; others KORM-TYPE-001 |
| TYP-05 | Nullable Int64 bound NULL | Declared int64/null type preserved; no integer zero |
| TYP-06 | Required text bound null | KORM-BIND-004 before command creation |
| TYP-07 | Converter A→B→C and C→B→A | Exact ordered calls; no converter invoked on bypassed NULL |
| TYP-08 | Byte array mutated after capture | Bound snapshot unchanged |
| TYP-09 | Culture tr-TR/fr-FR vs invariant | Same identity/facets/canonical literal bytes |
| TYP-10 | SqlType<T> descriptor with wrong ClrType | Reject before usable descriptor |

## Validation and stop

`python3 tests/Orm/Types/verify.py` compiles both positive and negative fixtures,
publishes the native console consumer, runs its assertions and checks pure
reference closure. Register module `orm-types` with dependency `orm-contracts`;
no database service is installed for these checks. Return the accepted descriptor
and converter fixtures to language/render/provider owners. Stop after this module's
reviewed implementation; no provider codec, query executor or product switch.
