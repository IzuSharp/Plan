# ORM-NESTED — nested projections and result materialization

Status: `planned_candidate`; product implementation is **not authorized**.

## Fixed outcome and dependencies

Implement explicit nested rows and nested collections without relationship loading,
an identity map, implicit grouping of unrelated result rows or follow-up queries.
Use Design `implementation-spec.md`, `contracts.md`, `mature-execution.md` and
`java-execution-options.md` at the immutable batch revision; consume ORM-C01 and
ORM-C03–ORM-C06. Start: `ORM-FOUNDATION`; acceptance: `ORM-RELATIONAL`,
`ORM-ADVANCED-TYPES`, `ORM-GENERATOR` and `ORM-RENDER`.

The local task accepts neutral descriptors, static decoders and pure SQL fixtures.
Actual dialect/provider behavior belongs to the independent integration lanes.
Do not infer this feature from Dapper's multi-mapping overloads: the selected
Dapper.AOT integration composes an explicit generated RowFactory, and retains the
mature runtime's reader/disposal/async loop unchanged.

## Inherited semantics and exact files

Use jOOQ public commit `3c58109e7ab69772de75e640852935ee7e284177` (3.21.10):

| Source symbol | Fixed adaptation |
| --- | --- |
| `Multiset.acceptDefaultJSONEmulation`, `jsonxArrayaggEmulation` | Positional arrays of arrays, duplicate preservation, explicit collection cardinality and empty collection representation |
| `JSONArray.accept`, `JSONArrayAgg.accept0` | Cell-specific JSON construction and dialect aggregation; keep SQL NULL/JSON null separate |
| `Records.mapping(FunctionN)` | Direct typed constructor invocation in declared ordinal order |
| `Functions.nullOnAllNull`, `nullOnAnyNull` | Explicit policies only; a nullable joined DTO does not silently select one of these policies |
| `DefaultRecordMapper` constructor/member branches | Move known mapping decisions to generation; no runtime reflective constructor search |
| `ListAgg.accept` | Evidence that jOOQ's MySQL/Maria GROUP_CONCAT workaround can prepend/append session SET statements; do not import that behavior into one RenderedTemplate |

Own `src/Orm/Nested/` and `tests/Orm/Nested/`. Required implementation files:

| File / type | Required members |
| --- | --- |
| `AssemblyInfo.cs` | Explicit InternalsVisibleTo for Korda.Orm.Dialects.PostgreSql, Korda.Orm.Dialects.Sqlite, Korda.Orm.Dialects.MySql and Korda.Orm.Dialects.MariaDb; Contracts friendship is not transitive |
| `NestedRow.cs` | readonly `NestedRow<T>` with `HasValue`, guarded `Value`, `None`, `Some(T)` |
| `NestedOptions.cs` | immutable budgets: MaxBytes=1,048,576, MaxItems=10,000, MaxDepth=32; accepted ranges MaxBytes 2..1,048,576, MaxItems 0..10,000, MaxDepth 1..32; template-hash contribution |
| `NestedShape.cs` | `NestedShapeId`, ordered cell descriptors, logical member paths, physical widths, presence policy and static element mapping ID |
| `Nested.cs` | `Row<T>(Projection<T>)`, `Optional<T,TKey>(Projection<T>,Field<TKey> presenceKey)`, `NullOnAllNull<T>(Projection<T>)`, `Collect<T>(Query<T>,NestedOptions?)`, `Multiset<T>(Query<T>,NestedOptions?)` |
| Shared `Contracts/Nodes/Nested.cs` | `NestedRowNode`, `NestedOptionalRowNode`, `NestedMultisetNode`; immutable child/projection/contract-budget fields, coordinated through the contract owner |
| `NestedValidator.cs` | `ValidatePresence`, `ValidateCollectionSource`, `ValidateOrdering`, `ValidateCellEncoding` |
| `NestedProjectionLowering.cs` | `ExpandRow`, `AllocatePhysicalAliases`, `BuildShape`; no SQL string splicing |
| `NestedJsonDecoder.cs` | bounded reader-loop over one JSON value; delegate to generated per-cell readers and constructor calls, not a DbDataReader loop |
| `NestedDiagnostics.cs` | Exact messages below |
| Tests | `PresenceTests`, `OrdinalLayoutTests`, `CollectionDecoderTests`, `EncodingTests`, `BudgetTests`, `NativeConsumer` and four dialect SQL fixture sets |

NestedLowering and its Lower(SqlNode,SqlProfile) method remain internal; do not
make a public method expose internal SqlNode. The four explicit friend assemblies
can invoke it through AssemblyInfo.cs. Shared NestedShape/Budget descriptors
contain only immutable BCL/contract data,
not decoder delegates or references to this assembly. They live with the shared
node records. NestedProjectionLowering is a pure SqlNode-to-SqlNode transformation
and does not reference RenderContext; each explicit IDialectRules.Lower invokes
it before that profile's own lowering. Dialect writers consume the shared descriptors. This prevents a
Contracts/Language/Rendering reverse dependency on runtime decoder implementation.

Row returns a logical `Field<T>` with a nested-row SQL identity. Optional and
NullOnAllNull return `Field<NestedRow<T>>`. Collect and Multiset return
`Field<ImmutableArray<T>>`; their distinct node flags preserve ordered-sequence
versus unordered-bag intent. T is an explicitly generated [DbRow] type, a supported generated Row arity,
or a registered built-in scalar carrier. No runtime type/member discovery is added.

## Exact generator and result-shape seam

The contract owner adds the following pure data declarations in Contracts, with
the same namespace/accessibility policy as ResultShape. ResultShape.Columns is
physical reader columns; ResultShape.Members is the ordered logical projection.
The common CompiledMapping preflight compares DTO logical members against Members,
not against Columns.Length.

```csharp
public enum ResultMemberKind { Scalar, RequiredRow, OptionalRow, Collection }
public enum NestedPresencePolicy { Required, Key, AllNull }
public sealed record NestedBudget(int MaxBytes, int MaxItems, int MaxDepth);
public sealed record ResultMember(string Name, int FirstOrdinal, int Width,
    ResultMemberKind Kind, SqlTypeDescriptor LogicalType,
    NestedShapeDescriptor? Nested = null);
public sealed record NestedJsonMember(int CellIndex, string Name,
    ResultMemberKind Kind, SqlTypeDescriptor LogicalType,
    NestedShapeDescriptor? Nested = null);
public sealed record NestedShapeDescriptor(string Id,
    ImmutableArray<ResultColumn> RowColumns,
    ImmutableArray<ResultMember> RowMembers,
    ImmutableArray<NestedJsonMember> JsonMembers,
    NestedPresencePolicy Presence, NestedBudget Budget, string MappingId);
public sealed record ResultShape(ImmutableArray<ResultColumn> Columns,
    ImmutableArray<ResultMember> Members);
```

At the outer ResultShape, FirstOrdinal is absolute. Inside NestedShape.RowColumns
and RowMembers it is relative to that group's physical start. Required row begins
at relative 0. Optional row's presence discriminator is relative 0 and its payload
begins at 1. ReadChild computes absolute ordinal = outer group start + relative
ordinal. A collection's outer physical Width is exactly 1; its element descriptor
is not another DbDataReader column range. JsonMembers.CellIndex is a separate
zero-based JSON element-cell index, and JSON row arity is JsonMembers.Length,
never RowColumns.Length. A nested required row is one recursive JSON-array cell;
an optional row is one `[presence,payload]` cell; neither expands JSON parent arity.

Every physical ResultColumn keeps its physical SQL type/nullability. LogicalType
retains the DTO member's requirement. Optional payload columns are physically
nullable through join extension, while a non-null child member remains logically
non-null. BindReader uses the logical member requirement for its eventual typed
read delegate. ValidateReaderColumn uses the physical descriptor to validate actual
provider representation. Do not globally reject the logical child because the
physical joined column is nullable; only presence=1 reaches that child's non-null
reader and DBNull then fails KORM-MAP-003.

Execution owns the attribute declaration (no reference from Contracts to Nested):

```csharp
[AttributeUsage(AttributeTargets.Property | AttributeTargets.Field |
                AttributeTargets.Parameter, AllowMultiple = false, Inherited = false)]
public sealed class DbNestedAttribute : Attribute
{
    public DbNestedAttribute(ResultMemberKind kind) => Kind = kind;
    public ResultMemberKind Kind { get; }
}
```

Scalar is invalid for this attribute (ORMGEN004). RequiredRow requires a declared
child T; OptionalRow requires NestedRow<T>; Collection requires ImmutableArray<T>.
A record may use `[property: DbNested(ResultMemberKind.Collection)]`. The child must
be a known [DbRow] type or supported Row arity with one fixed constructor/member
plan, or a registered built-in scalar. Scalar collection elements use a one-cell
row array and return the decoded scalar directly; they do not inspect a constructor
or create another global scalar mapper. A cycle or static shape depth >32 is ORMGEN004. A conflicting property and
constructor-parameter annotation is ORMGEN004; matching annotations describe one
member. The generator follows only these explicit type-symbol edges, never an
assembly-wide or runtime member scan.

For nested row reads, generate a private method in the **parent** factory:

```csharp
private static Child ReadChild(DbDataReader reader, ReadOnlySpan<int> tokens,
    int groupStart, ChildReadPlan plan);
```

ChildReadPlan is a generated immutable type with one typed reader delegate and
relative physical offset per cell. ReadChild reads typed cells and calls the known
constructor/init setters. It never calls the child's standalone RowFactory.Tokenize;
only the outer factory tokenizes and checks the whole reader. The child constructor
and setters must be accessible from the parent's generated assembly. Accessible
internal members in that assembly work; inaccessible members of an external child
produce ORMGEN002 even if that external child has its own standalone mapper. This
is the fixed baseline; no cross-assembly reflective/accessibility workaround or
second registry is introduced.

The pure Nested module's JSON decoder seam is:

```csharp
public delegate T NestedElementReader<T>(ref Utf8JsonReader reader,
    NestedReadContext context);
public sealed record NestedReadContext(ReadOnlyMemory<byte> Payload,
    NestedShapeDescriptor Shape, string Path, int RemainingDepth);
public static class NestedJsonDecoder
{
    public static ImmutableArray<T> ReadCollection<T>(ReadOnlyMemory<byte> utf8,
        NestedReadContext context, NestedElementReader<T> readElement);
    public static ImmutableArray<T> ReadCollectionValue<T>(ref Utf8JsonReader reader,
        NestedReadContext context, NestedElementReader<T> readElement);
}
```

These are declaration signatures; method bodies follow the decoder algorithm
below. ReadCollection requires utf8 to be the same payload memory carried in the
context, validates its budget, initializes the one reader and calls ReadCollectionValue.
The value overload starts on an array/root error object and leaves the reader on
its matching end token. NestedReadContext is immutable; a child context keeps the
same Payload, selects its child Shape, appends its logical Path and decreases
RemainingDepth. Root remaining depth equals the configured MaxDepth; nonpositive
child depth fails KORM-NESTED-005. The same reader separately enforces actual JSON
container depth, so a new context cannot reset that limit. Each collection counts
its own MaxItems; the entire encoded subtree shares the root byte budget. Generated code
passes a cached static method group; it does not allocate a closure per element.
ReadCollection positions the reader at each element's StartArray; readElement
consumes exactly that row and returns with the reader on its EndArray. The outer
loop advances next. Recursive generated element readers share the same ref reader
and a child context path/budget; they never create a reader with reset depth limits.
Primitive cell readers are direct typed Utf8JsonReader methods; JSON-value cells
copy the exact source slice between TokenStartIndex and BytesConsumed into owned
JsonText after a bounded TrySkip. Nothing borrowed escapes the decoder call.

## Nested row layout and presence algorithm

A required row flattens its cells depth-first into the outer SELECT projection.
An optional row adds one physical Int32 discriminator immediately before that
row's flattened payload. Physical result ordinals are consecutive. Use aliases
`__korda_n{nodeIndex}_p` for presence and `__korda_n{nodeIndex}_c{cellIndex}` for
payload, reserving these names against user output aliases. Node indices are
assigned in final projection traversal order and included in the result shape.
The logical DTO member path remains in NestedShape; it is not reconstructed by
splitting a returned SQL alias on dots.

`Optional(child,presenceKey)` requires a key proven non-null in the child relation
before outer-join null extension. A base primary/unique non-null column qualifies;
a nullable expression or an arbitrary COALESCE does not. It must belong to the
same nullable relation scope as the child payload. Emit
`CASE WHEN key IS NULL THEN 0 ELSE 1 END` for the discriminator. A present child
whose projected nullable values are all NULL still has discriminator 1.

`NullOnAllNull(child)` is a separate explicit policy. Emit discriminator 0 only
when every flattened child value is SQL NULL, otherwise 1. Require stable cells
under the shared expression-stability rule because the SQL null tests repeat the
payload expressions. It intentionally treats a present all-null payload as absent;
callers choosing it accept that meaning. Do not infer it from T's CLR nullability.

The generated row-factory recipe is fixed:

1. Tokenize validates the complete physical field count, aliases and accepted
   provider/SQL representations before materializing the first row. It binds
   presence/payload ordinals from the invocation's expected result shape. Empty
   outer results follow Dapper's no-Tokenize behavior and do not promise a schema
   drift exception without a row.
2. Read discriminator with a non-null typed Int32 getter. Values other than 0/1
   fail `KORM-NESTED-002`.
3. For 0, assign NestedRow<T>.None and skip reading/constructing that child payload.
   This prevents non-nullable child members from throwing on an absent join row.
4. For 1, read cells in declared ordinal order, enforce each child's own null and
   conversion contract, call its generated constructor/init assignments, then
   wrap Some(value). Required row omits steps 2/3 and constructs directly.
5. Do not instantiate absent objects, group by aliases, deduplicate keys or retain
   a DbDataReader reference. The generated mapping method is called by the mature
   Dapper.AOT RowFactory.Read, never by a second execution loop.

Physical payload descriptors account for outer-join null extension. Logical
non-null child members are checked conditionally when presence=1; declaring every
child member nullable to work around an absent join is not the implementation.

## Collection query subset and order contract

The first accepted collection source is a SELECT with a fixed typed projection,
FROM/joins, WHERE/correlation and optional ORDER BY. Reject source DISTINCT,
GROUP BY/HAVING, set operations, CTE-local mutations, windows already in the source,
LIMIT/OFFSET, locks and arbitrary scalar subquery cells with `KORM-NESTED-004`.
They require additional semantic lowerings and are not silently stripped. Parent
queries may still use their independently supported SQL families.

Collect requires a nonempty explicit stable ORDER BY. Preserve the requested
sort-tuple order; ties have the SQL query's ordinary unspecified relative order.
A caller needing reproducible order across equal keys must supply a unique tie
breaker explicitly. The renderer does not invent such a key or require optional
schema metadata to infer one. A projection may omit order-key columns from its
transported DTO. Multiset accepts no order guarantee; if its source explicitly
contains an order, preserve it through the same ordered lowering. Tests compare
unordered output as a bag with counts, never as a set that erases duplicates.
The canonical ordered fixture uses id,seq to make its exact result reproducible.

All cell and sort expressions must be stable under the shared rule (columns,
parameters, literals and registered deterministic compositions). This permits
MariaDB's guard to evaluate the row JSON expression twice without changing
meaning. Volatile/unknown functions fail before rendering; no hidden materialized
query is invented. Correlation is an explicit outer relation reference in the
source WHERE and follows the common lexical scope validator.

## Fixed wire encoding and lossless cell codecs

A collection is one SQL result column containing a JSON array of row arrays.
An empty child result is `[]`, a one-row result is `[[cells...]]`, and duplicate
rows are repeated entries. The collection itself is non-null. A server SQL NULL
payload outside an explicitly nullable cell is a failure, not an empty collection.
A row array's arity is exactly NestedShape.JsonMembers.Length; object-member aliases
never participate in positional decoding.

| Cell type | Wire representation and read algorithm |
| --- | --- |
| Int32/Int64 | JSON integer token; TryGetInt32/TryGetInt64 with range checks, never convert through Double |
| Boolean | JSON true/false; Use the explicit 0/1-to-JSON-Boolean construction below for SQLite/MySQL/Maria; PG keeps its native Boolean |
| Text | JSON string; decode JSON escapes, including Unicode/embedded NUL, into an owned string |
| Decimal | Invariant decimal string in every dialect, with declared p/s; parse checked decimal without exponent/thousands separators, then exact facet validation |
| UUID | Lowercase canonical D-format string; parse exact D form |
| Binary | Uppercase hexadecimal string; even-length and valid-digit checks, then owned bytes |
| Date/time/instant | Fixed ISO string from the registered advanced codec; enforce declared precision and temporal kind, never local-time parsing |
| SQL NULL | JSON null only for a nullable ordinary scalar cell |
| JSON / JSONB | Two-item cell envelope `[present,value]`: `[0,null]` is SQL NULL; `[1,null]` is JSON literal null; `[1,"null"]` is JSON string "null"; present value is embedded JSON, not JSON-quoted text |
| Nested optional row cell | `[presence,[child cells]]`; when presence=0 child payload is null, when 1 it has exact arity |
| Nested collection cell | The same array-of-row-arrays recursively; no double-encoded JSON string |

SQL writers use JSON constructors, not hand-escaped SQL concatenation. Decimal/
UUID/binary/temporal casts are explicit provider-approved lossless expressions;
an unsupported cell/profile pair fails `KORM-NESTED-006`. PG JSONB aggregation may
normalize JSON formatting/key order without changing values. SQLite/MySQL/Maria
must explicitly re-tag nested JSON after CASE/subquery boundaries: SQLite
`json(value)`, MySQL `CAST(value AS JSON)`, MariaDB `JSON_EXTRACT(value,'$')`.
Do not rely on an optimizer preserving a transient JSON subtype.

### Exact scalar encoder choices

For each nullable cell, retain SQL NULL with an outer CASE/null-preserving native
function. In particular SQLite hex(NULL) must not become an empty byte string.
The following table fixes the encoder; it is not an invitation to pick an
implementation at integration time.

| Value | PostgreSQL | SQLite | MySQL / MariaDB |
| --- | --- | --- | --- |
| Decimal | `CAST(x AS text)` | Existing validated decimal TEXT x; NUMERIC/REAL-backed source rejected for lossless nested decimal | `CAST(x AS CHAR CHARACTER SET utf8mb4)` |
| Binary | `upper(encode(x,'hex'))` | `CASE WHEN x IS NULL THEN NULL ELSE hex(x) END` | `HEX(x)` |
| UUID | `lower(CAST(x AS text))` | `lower(x)` for declared canonical UUID TEXT | `lower(x)` for declared CHAR(36) transport; binary UUID cell encoding is outside this baseline |
| Date | `to_char(x,'YYYY-MM-DD')` | Canonical date TEXT x | `DATE_FORMAT(x,'%Y-%m-%d')` |
| Time | `to_char(x,'HH24:MI:SS.US')` | Canonical time TEXT x | `TIME_FORMAT(x,'%H:%i:%s.%f')` |
| Local timestamp | `to_char(x,'YYYY-MM-DD"T"HH24:MI:SS.US')` | Canonical local timestamp TEXT x | `DATE_FORMAT(x,'%Y-%m-%dT%H:%i:%s.%f')` |
| UTC instant | `to_char(x AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.US"Z"')` | Canonical UTC TEXT ending Z | `DATE_FORMAT(x,'%Y-%m-%dT%H:%i:%s.%fZ')` under the verified UTC session |

Canonical temporal strings contain exactly six fractional digits in nested
transport (zero-pad lower precision), date-only has none; decode to the declared
p<=6 precision and reject nonzero discarded digits. SQLite provider storage for
these nested-enabled identities uses that exact canonical text convention.
Do not route arbitrary legacy timestamp strings through this identity.

For SQLite/MySQL/Maria Boolean x, build a JSON fragment from
`CASE WHEN x=0 THEN 'false' WHEN x=1 THEN 'true' ELSE
'{"$korda_invalid_boolean":true}' END`, then tag with SQLite json, MySQL CAST AS
JSON, or MariaDB JSON_EXTRACT(...,'$'). Apply an outer SQL-null branch when x is
NULL. The invalid object deliberately fails the Boolean token decoder instead of
coercing an arbitrary nonzero integer to true. PG's typed Boolean column has no
integer-coercion branch. For JSON cell envelopes use the same dialect tagging on
the original JSON payload and the explicit SQL-NULL presence bit.

## Four exact SQL lowerings

Let R be the dialect JSON constructor for the row's encoded cells, O the checked
sort list, F the source FROM/joins and W its WHERE including parent correlation.
Emit complete expressions from nodes; the symbols below describe the algorithm.
There is no additional round trip or per-parent query.

| Profile | Fixed correlated scalar expression |
| --- | --- |
| PostgreSQL | `COALESCE((SELECT jsonb_agg(R ORDER BY O) FROM F WHERE W), '[]'::jsonb)`; use jsonb_build_array for R |
| SQLite >=3.45 | `(SELECT json_group_array(R ORDER BY O) FROM F WHERE W)`; use json_array for R; native empty aggregate is `[]` |
| MySQL 8.4 | `COALESCE((SELECT JSON_ARRAYAGG(R) OVER (ORDER BY O ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) FROM F WHERE W LIMIT 1), JSON_ARRAY())` |
| MariaDB 11.8 | The guarded native aggregate CASE below; use JSON_ARRAY for R and JSON_ARRAYAGG with ORDER BY O |

For an unordered Multiset, omit aggregate ORDER BY on PG/SQLite/Maria; MySQL uses
ordinary JSON_ARRAYAGG without the window/LIMIT wrapper. MySQL's plain aggregate
order is unspecified, so it is never selected for Collect. The full window frame
is mandatory: its default frame could produce a prefix instead of the complete
collection. LIMIT 1 selects one identical full-frame result, not one child row
before the window operation.

MariaDB's exact single-statement CASE is:

```sql
SELECT CASE
  WHEN COUNT(*) = 0 THEN JSON_ARRAY()
  WHEN SUM(OCTET_LENGTH(R)) + COUNT(*) + 1
       > LEAST(B, @@session.group_concat_max_len)
    THEN JSON_OBJECT('$korda_error', 'nested-budget')
  ELSE JSON_ARRAYAGG(R ORDER BY O)
END
FROM F
WHERE W
```

B is the validated MaxBytes shape constant (at least 2), rendered as an invariant
integer and included in the template fingerprint. JSON_ARRAYAGG combines N encoded
row values using N-1 commas and two brackets; the sum of the UTF-8 row byte lengths
plus N+1 is the required upper bound. The actual constructor output is the measured
input to OCTET_LENGTH, so JSON escapes and multi-byte characters are counted after
encoding. The empty branch avoids SUM(NULL) and distinguishes no rows from an
aggregate failure. Do not replace the ELSE result's unexpected NULL with `[]`.
Each appearance of a parameter inside R is a separate final parameter occurrence.

The guard rejects before a truncated payload is accepted even if a truncated value
would parse as JSON. It does not promise MariaDB never allocates/intermediately
computes the aggregate; the contract is result integrity and bounded client
materialization. It issues no SET. The reserved error object cannot collide with
a valid collection because valid collections have an array root. Recognize its
exact key/value as `KORM-NESTED-005`; any other root object is `KORM-NESTED-003`.

## Generated decoder algorithm and ownership

The provider's static JSON codec supplies owned UTF-8 for one column. The generated
RowFactory calls the known NestedJsonDecoder.ReadCollection<T> and known static element reader;
no reflected generic construction, dynamic JSON mapping, serializer discovery or
callback per database row is introduced.

1. Check the payload byte count <= MaxBytes before allocating any child DTO/list.
   Configure Utf8JsonReader with MaxDepth and strict JSON settings. Validate the
   reserved error object first; otherwise require StartArray.
2. For each element require StartArray, check the next item count <= MaxItems, and
   read exactly JsonMembers.Length cells using generated typed methods. Each
   nullable cell tests JSON null explicitly; a non-nullable cell rejects it.
3. Read integer/decimal/text/JSON envelopes as specified above. Recursive shapes
   share a decreasing depth budget and the parent payload byte budget; they cannot
   reset limits by constructing another reader with default options.
4. Require EndArray after the last cell. Call the known DTO constructor and init
   setters in generated order, append to the local ImmutableArray builder, then
   advance to the next child. No all-null child row is dropped from a collection.
5. Require the outer EndArray and only trailing whitespace. Freeze to an owned
   ImmutableArray<T>. On failure discard the builder/temporary payload; allow the
   mature runtime's finally/disposal path to close reader/command.

No span, pooled byte buffer, JsonDocument element, provider buffer or reader state
escapes into a returned DTO. A provider can buffer a field before its typed codec
sees it; these limits are accepted-payload/object-count bounds, not a promise that
all driver/server allocations stop at MaxBytes. A streaming outer query still buffers each one nested
field. MaxBytes bounds encoded payload and MaxItems bounds object count; these are
not an exact managed-RSS or database working-memory promise. The template and
nested shape are reusable; decoder builders and payloads are invocation-local.

## Exact fixtures, diagnostics and acceptance

Use parents `(1),(2)` and children `(seq,id,parent,name,score)`:
`(0,3,1,'z',30)`, `(1,1,1,'a',NULL)`, `(2,1,1,'a',NULL)`. Total order is id,seq.
Collect for parent1 must return exactly `[[1,"a",null],[1,"a",null],[3,"z",30]]`;
parent2 returns `[]`. The repeated row remains twice. A nullable optional address
fixture has non-null key but all nullable projected fields NULL; it is present.
A missing key under left join is absent, even when child fields are non-nullable.

| Code | Fixed message and fixture |
| --- | --- |
| `KORM-NESTED-001` | `Nested row '{path}' has no valid presence proof.` Nullable/mismatched relation key |
| `KORM-NESTED-002` | `Nested presence at '{path}' must be 0 or 1.` NULL/-1/2 discriminator |
| `KORM-NESTED-003` | `Nested payload at '{path}' does not match shape '{shape}'.` Wrong arity, root token, cell kind or unexpected SQL NULL |
| `KORM-NESTED-004` | `Nested query feature '{feature}' has no accepted lowering for '{profile}'.` Missing requested order, volatile cell, unsupported source clause |
| `KORM-NESTED-005` | `Nested payload at '{path}' exceeds its declared item/byte/depth budget.` Local decoder overflow or Maria sentinel |
| `KORM-NESTED-006` | `Nested cell '{type}' has no lossless encoding for '{profile}'.` Unsupported scalar/profile conversion |

Mandatory decoder cases: zero/one/many, duplicate rows, reordered/missing/extra
cells, Int64 9,007,199,254,740,993 and extrema, decimal limits, embedded NUL/Unicode,
SQL NULL versus JSON-null envelopes, malformed UTF-8/JSON, arrays at every depth,
MaxItems+1, MaxBytes+1 and MaxDepth+1. A present invalid child must throw, not become
absent. Independently verify outputs after the outer reader/session is disposed.

The local 2026-11-28 research probe ran the ordered correlated SQL on PostgreSQL
18.7, MySQL 8.4.11 and MariaDB 11.8.10, preserving duplicates/nulls/empty parents.
A separate MariaDB guard probe used three rows including a multi-byte `猫`: sum
bound and actual payload were both 46 bytes; cap=budget=46 returned full data,
cap45 or budget45 returned the error object, and empty input with cap4/budget2
returned `[]`. These are evidence for the selected lowering, not product acceptance.
A second seven-value witness included empty text, double quote, backslash,
newline, NUL, emoji+CJK and text "null"; bound and actual were 88 bytes, cap 88
preserved all values and cap 87 returned the error object. Future implementation
must repeat these boundaries through actual generated parameter/layout paths on
every accepted build.

Run pure shape/generator fixtures and a driver-free Native AOT decoder consumer.
Integration separately runs actual SQL/provider layouts, nested errors during
streaming, early outer disposal and ordinary transaction/cancellation ownership.
Retain Dapper's execution loop; the only generated work is typed cell/DTO decoding.
Stop at the reviewed task PR, without product authorization, publication, merge,
legacy removal or implicit relationship loading.

Primary sources: [jOOQ Multiset](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/impl/Multiset.java),
[JSONArrayAgg](https://github.com/jOOQ/jOOQ/blob/3c58109e7ab69772de75e640852935ee7e284177/jOOQ/src/main/java/org/jooq/impl/JSONArrayAgg.java),
[MySQL aggregate/window semantics](https://dev.mysql.com/doc/refman/8.4/en/aggregate-functions.html),
[MariaDB aggregate limit](https://mariadb.com/docs/server/reference/sql-functions/aggregate-functions/json_arrayagg),
[SQLite JSON](https://www.sqlite.org/json1.html).

## Exact local runner contract

This task owns `tests/Orm/Nested/verify.py`,
`tests/Orm/Nested/Korda.Orm.Nested.Tests.csproj` and its Program/fixture files.
The CI command, from repository root with no additional flags, is:

```sh
python3 tests/Orm/Nested/verify.py
```

The runner compiles the packet's positive/negative declaration cases, publishes
its actual consumer with `dotnet publish tests/Orm/Nested/Korda.Orm.Nested.Tests.csproj -c Release -r linux-x64 -p:PublishAot=true`,
then executes that native consumer and asserts RuntimeFeature.IsDynamicCodeSupported
is false. Use the repository's pinned SDK/restore settings; place outputs under
artifacts, never beside source. Run this packet's enumerated pure fixtures and
report individual case failures with nonzero exit. The runner does not start a
database, accept an absent peer as a passing stub, or claim live SQL correctness.
Real four-server rows, faults and SQL execution remain ORM-INTEGRATION's gate.
