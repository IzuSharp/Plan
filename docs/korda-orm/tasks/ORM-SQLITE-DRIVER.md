# ORM-SQLITE-DRIVER — exact Microsoft.Data.Sqlite adapter and catalog reader

Status: `planned_candidate`; product implementation is **not authorized**.

## Fixed outcome and dependencies

Use Microsoft.Data.Sqlite **11.0.0**, EF Core source commit
`9e685c7a52d1a344d133a3d370e458db97417b3f`, with the unmodified Dapper.AOT 1.1.0
runtime and ORM-EXECUTION's typed layout adapter. This uses the ADO.NET provider,
not the EF Core ORM. The pure profile is `sqlite-3.45`, engine interval [3.45,4.0).
Read the graph-pinned Design implementation-spec, mature-execution and generation-
integration documents, ORM-C01/C03–C06, ORM-ADVANCED-TYPES and ORM-NESTED.

Start after ORM-FOUNDATION; acceptance requires ORM-EXECUTION, ORM-SCHEMA and the
accepted neutral advanced types. Work independently of network providers. The
research engine was SQLite 3.53.4; the final module must validate the actual loaded
library instead of assuming the NuGet package version is the SQLite engine version.

## Exact owned files and public facade

Own `src/Orm/Providers/Sqlite/` and `tests/Orm/Providers/Sqlite/`.
The project is `Korda.Orm.Sqlite.csproj`, namespace `Korda.Orm.Sqlite`, referencing
Execution, SchemaModel, AdvancedTypes, the pure SQLite dialect and the mature
Microsoft.Data.Sqlite package/native asset closure. Foundation owns project/root
registration; this packet supplies its actual source/test/dependency paths.

| File / type | Fixed responsibility |
| --- | --- |
| `SessionFactory.cs` / `SqliteSession` | OpenAsync/BorrowAsync below; acquire or borrow one driver connection |
| `ProviderServices.cs` / `SqliteServices` | Immutable verified profile, capabilities `(false,false,true)`, closed codecs and LayoutCommandFactory |
| `ParameterCodec.cs` / `SqliteParameterEncoder` | Create<T> returns a typed SQLite storage parameter without adding it |
| `ReaderCodec.cs` | Strict INTEGER/REAL/TEXT/BLOB readers and canonical advanced text decoders |
| `Codecs/ScalarCodecs.cs`, `TextValueCodecs.cs`, `JsonCodec.cs` | Fixed storage/conversion table below; static typed closures only |
| `ServerProfile.cs` | Actual engine/source ID/compile options, variable limit and JSON availability checks |
| `MetadataReader.cs` / `SqliteCatalogReader` | Borrowed, read-only pragma/catalog collection and coherence detection |
| `Metadata/CatalogQueries.cs` | Exact queries below; parameters for names where SQLite exposes table-valued pragmas |
| `Metadata/DdlScanner.cs` | Bounded quoted-token/parenthesis scanner for information omitted by pragmas |
| `Metadata/TypeDecoder.cs` | Declared type identity plus independent storage affinity; unresolved remains explicit |

```csharp
public static class SqliteSession
{
    public static Task<OrmSession> OpenAsync(string connectionString,
        CommandOptions? options = null,
        CancellationToken cancellationToken = default);
    public static Task<OrmSession> BorrowAsync(SqliteConnection connection,
        SqliteTransaction? transaction = null, CommandOptions? options = null,
        CancellationToken cancellationToken = default);
}
public sealed class SqliteCatalogReader : ISchemaCatalogReader
{
    public Task<SchemaSnapshot> ReadAsync(DbConnection connection,
        SchemaReadOptions options, CancellationToken cancellationToken = default);
}
```

## Mature source map and session algorithm

| Source symbol | Required reuse/adaptation |
| --- | --- |
| [SqliteCommand.ExecuteReaderAsync and Cancel](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteCommand.cs) | Pre-cancellation, synchronous underlying work and no-op Cancel remain explicit capabilities |
| [SqliteParameter.Bind](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteParameter.cs) | Mature sqlite3 binding/native asset path; Korda supplies a known SqliteType and value |
| [SqliteDataReader](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteDataReader.cs) and SqliteDataRecord | Typed reading and resource ownership; the Korda codec tightens allowed storage/conversion |
| [SqliteConnection.Handle, CreateDbCommand, DefaultTimeout](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteConnection.cs) | Actual loaded connection handle and inherited command timeout; no new executor |
| jOOQ SQLiteDatabase/SQLiteTableDefinition at the pinned 3.21.10 source | Metadata distinctions and pragma use; translate semantics into the shared neutral model |

1. Validate arguments, timeout and cancellation. OpenAsync creates and opens one
   SqliteConnection; it owns disposal. BorrowAsync requires an already-open
   connection and a same-instance transaction; it never opens/closes or disposes
   caller resources. The facade does not print the connection string.
2. Read `SELECT sqlite_version(), sqlite_source_id()` and `PRAGMA compile_options`.
   Require the version interval. Check `SELECT json_valid('null'), json_array()`
   yields 1 and `[]`. Observe the actual current per-connection variable limit
   using the mature SQLitePCLRaw `sqlite3_limit(connection.Handle,
   SQLITE_LIMIT_VARIABLE_NUMBER,-1)` query. Never raise it. Set max_parameters to
   min(observed,32766) in the immutable session profile.
3. The factory-created connection explicitly disables DQS_DML and DQS_DDL before
   use with SQLitePCLRaw `raw.sqlite3_db_config(handle,flag,0,out current)` and
   checks SQLITE_OK plus current=0. BorrowAsync only queries each flag with -1
   and requires 0; it never changes caller settings. Both methods are present in
   the pinned mature SQLitePCLRaw package; no new native bridge is introduced.
   This enforces the profile's double_quoted_string_literals=disallowed setting:
   otherwise a misspelled quoted text column could become a string literal and
   falsely pass a DTO shape check. Reject mismatch with EXEC-001. Do not mutate
   caller foreign_keys, journal, synchronous, busy or extension-loading settings;
   applications configure those explicitly.
4. Construct SqliteServices and return Own/Borrow as appropriate. If initialization
   fails, dispose only an acquired connection, preserving an earlier exception
   when disposal fails. The actual driver restores initial operation open/closed
   state as specified in ORM-EXECUTION; facade-created sessions start open.
5. Forward transaction/savepoint work to SqliteTransaction. No background worker,
   Task.Run wrapper, native scheduling layer, retry engine or private pool is added.

The API remains async-shaped for composition, but AsyncIo=false and
InFlightCancellation=false are observable capability facts. A pre-cancelled token
fails before execution; cancellation after a native step starts is not promised to
interrupt it. SqliteCommand.Cancel does nothing in this pin. Busy timeout is a
driver lock-wait policy, not a general wall-clock deadline for arbitrary SQL.

## Storage codecs: fixed conversions

ProviderServices.ValidateConnection(DbConnection,DbTransaction?) performs static
`is` checks for SqliteConnection/SqliteTransaction and checks an optional transaction's
Connection is non-null and ReferenceEquals the supplied connection. Own/Borrow and
terminal preflight call it; mismatch/completed transaction is EXEC-001 before any
command. It performs no hidden network/settings query.

Codec diagnostics are fixed: missing parameter codec BIND-005; missing result
codec/unknown read conversion/wrong closed T MAP-002; known conversion failure or
checked result overflow TYPE-005; required DBNull MAP-003. Pure unsupported
advanced SQL operations retain TYPE-004. Lookup failure occurs before command
creation and never enables a runtime fallback.

BindDynamicReader(SqlTypeDescriptor,string?) selects only a statically closed
scalar read codec and wraps its typed result in DynamicCell<T>. It is prebound once
per declared dynamic-record column; no per-row type lookup, CLR type synthesis or
provider-specific dynamic mapper is permitted. Unsupported cells fail before
execution. BindReader/BindDynamicReader share DBNull, conversion and storage policy.

ProviderServices.ValidateValue<T>(SqlType<T>,T,ParameterOccurrence) uses the same
closed codec validation helper before session admission and command creation.
It checks the actual immutable value against provider range/precision/storage
requirements, with diagnostics containing type/facet context rather than values.
Create<T> calls the same helper defensively; it never discovers layout or selects
an unregistered fallback. Capture/freeze still owns mutable-value snapshotting.

The encoder checks SqliteCommand, the declared SQL identity/nullability and exact
facets, then creates SqliteParameter with ParameterName=occurrence.Name (`p0`,
`p1`, ...), Direction=Input and explicit SqliteType. Value is the converted storage
value or DBNull.Value. Boxing at this ADO.NET Value boundary is allowed and
measured. Size is not used to silently truncate; validate length before binding.
Each occurrence gets its own parameter; no SQL parsing or name deduplication.

| Declared identity / CLR | SQLite storage and binding | Required read behavior |
| --- | --- | --- |
| int16 / short | INTEGER, checked conversion to Int64 | Require INTEGER; checked Int64→Int16 |
| int32 / int | INTEGER, checked conversion to Int64 | Require INTEGER; checked Int64→Int32 |
| int64 / long | INTEGER | Require INTEGER; GetInt64 |
| boolean / bool | INTEGER 0/1 | Require INTEGER and exactly 0 or 1; other integers fail the known conversion with TYPE-005 |
| text / string | TEXT | Require TEXT; GetString, retaining embedded NUL in bound data |
| binary / byte[] | BLOB | Require BLOB; copy into owned bytes, never retain reader buffers |
| float64 / double | REAL | Require REAL for this identity; finite/nonfinite behavior follows its explicit type contract |
| float32 / float | REAL converted from float | Checked declared Float32 policy; no implicit integer/decimal-to-float conversion |
| decimal(p,s) / decimal | Canonical invariant TEXT, explicit SQLite decimal-text identity | Parse exactly; validate p/s; never route through double or infer exact SQL arithmetic/order |
| uuid / Guid | Lowercase canonical D-format TEXT | ParseExact D, require canonical reserialization; no inferred byte-order encoding |
| date / DateOnly | TEXT `yyyy-MM-dd` | Invariant ParseExact; no local timezone |
| time / TimeOnly | TEXT `HH:mm:ss.ffffff` | Exact six fractional digits; declared p<=6 requires representable ticks |
| local timestamp / DateTime | TEXT `yyyy-MM-ddTHH:mm:ss.ffffff` | Kind=Unspecified; no timezone suffix |
| instant / UTC DateTime or zero-offset DateTimeOffset | TEXT `yyyy-MM-ddTHH:mm:ss.ffffffZ` | UTC/offset-zero only; parse with an explicit UTC policy |
| json / JsonText | Validated JSON TEXT | Parse owned UTF-8 with AdvancedTypes byte/depth limits; SQL NULL differs from JSON null |

Register `cast.int16.checked` only for logical int16 with closed short/short?, and
`cast.int32.checked` only for logical int32 with closed int/int?. SQLite emits
CAST AS INTEGER for these explicit expressions. ValidateResult and mapping Bind
use Execution's effective read-ID rule; ordinary DTO members need no matching
attribute. ValidateReaderColumn accepts only INTEGER for these IDs, and the cached
delegate first applies its one DBNull policy, then requires INTEGER on every row,
calls GetInt64 and returns `checked((short)value)` or `checked((int)value)`.
Overflow is TYPE-005 with the underlying OverflowException; TEXT/REAL/BLOB is
MAP-002, and required DBNull is MAP-003. Nullable codecs return null for DBNull.
SQLite's ordinary int16/int32 transport already uses checked INTEGER reads because
the engine has one signed integer storage class. The explicit cast IDs reuse that
helper without adding REAL/text coercion or changing ordinary storage validation.
The cast consumes SQLite's native SQL conversion semantics; it cannot recover
information the SQL cast itself discarded.

Required fixtures are CAST(32767 AS INTEGER) to short, CAST(-32768 AS INTEGER) to
short, CAST(2147483647 AS INTEGER) to int and nullable NULL to int?. Values 32768,
-32769 and 2147483648 under the corresponding explicit result IDs fail TYPE-005.
An ordinary Int64 expression declared as int16 without an explicit Cast does not
gain a logical type-conversion edge. An INTEGER arithmetic result remains Int64;
overflow promoted by SQLite to REAL still fails MAP-002. A different non-null
member ConversionId conflicts with the cast ID and fails MAP-002 before sending.

Canonical decimal formatting is `value.ToString("G29", InvariantCulture)` followed
by the exact p/s validation from AdvancedTypes; negative zero is normalized to 0.
Read decimal text with NumberStyles.AllowLeadingSign | AllowDecimalPoint |
AllowExponent and InvariantCulture, then require equality with the canonical G29
reserialization plus the exact p/s check; reject rounding or a noncanonical input.
Decimal metadata remains decimal-text, not SQLite NUMERIC affinity. The dialect
rejects decimal-TEXT numeric comparisons/order/arithmetic/cast-to-numeric and exact
SUM/AVG with TYPE-004, as ORM-SQLITE-DIALECT specifies; transport success is not a
claim of exact SQL numeric semantics. Date/time
format strings above are literal .NET invariant format contracts; use the exact
separator characters and no current-culture formatting. Pad six fractional digits;
reject any nonzero tick below a microsecond and any precision-p loss before writing.
Nested codecs use these same stored strings and do not call strftime to reconstruct
microseconds or convert decimal through SQLite REAL.

The reader delegate owns IsDBNull exactly once. A required descriptor returns
MAP-003 on DBNull; a nullable closed codec returns its declared nullable T. Actual
storage class is validated per row because SQLite permits a later row to have a
different storage class than the first. First-row Tokenize still checks degree,
order/aliases and provider metadata; it is not a guarantee that all future rows
have the first row's storage. Getter/conversion failures keep the original cause.

The profile has no native pg.jsonb, PG arrays/ranges/composites or arbitrary enum/
domain codec. A deliberately registered portable text conversion is distinct and
retains its SQL/conversion identity. An unavailable codec fails BIND-005 for parameter-codec lookup;
never relabel an unsupported type as text automatically. Do not use SQLite's
permissive numeric getters to silently accept TEXT "123" for an Int64 descriptor.

The explicit aggregate conversion `aggregate.int-sum.decimal` reads SQLite's
native INTEGER SUM through GetInt64 and returns checked decimal?, retaining NULL
for empty input. A native integer overflow remains the provider error.
`aggregate.floating.double` reads the approved REAL aggregate. Exact decimal-TEXT
SUM/AVG and integer-to-exact-decimal AVG are rejected by the pure dialect;
`aggregate.decimal-sum.decimal` / `aggregate.numeric-avg.decimal` are not silently
enabled here. Ordinary decimal-TEXT decoding continues to require TEXT and cannot
accept INTEGER merely because the aggregate converter can. No Convert.ChangeType
or SQL CAST to REAL is used to disguise exact decimal arithmetic.

## Catalog collection and bounded DDL scanner

ISchemaCatalogReader requires an open SqliteConnection with no active operation.
It borrows without changing transaction state, opening/closing, attaching databases
or executing DDL. SchemaReadOptions is the shared Execution.Metadata type. Read
all existing attached schemas needed for requested objects/FK closure; acquisition
must not attach new files. Qualified identities use catalog=null, schema equal to
its actual database alias (main/temp/explicitly attached alias), and exact name.

Use these queries in this order for a full catalog pass:

```sql
SELECT seq,name FROM pragma_database_list ORDER BY seq;
SELECT schema,name,type,ncol,wr,strict FROM pragma_table_list
  WHERE name NOT LIKE 'sqlite_%' ORDER BY schema,name;
SELECT cid,name,type,"notnull",dflt_value,pk,hidden
  FROM pragma_table_xinfo(@table,@schema) ORDER BY cid;
SELECT seq,name,"unique",origin,partial
  FROM pragma_index_list(@table,@schema) ORDER BY seq;
SELECT seqno,cid,name,desc,coll,"key"
  FROM pragma_index_xinfo(@index,@schema) ORDER BY seqno;
SELECT id,seq,"table","from","to",on_update,on_delete,match
  FROM pragma_foreign_key_list(@table,@schema) ORDER BY id,seq;
```

For each schema, quote its identifier by doubling `"` and wrapping it in `"`.
Use that exact quoting helper for `PRAGMA <schema>.schema_version` and
`SELECT type,name,tbl_name,sql FROM <schema>.sqlite_schema ORDER BY type,name`.
Only these validated catalog identifiers are interpolated. Every table/index name
accepted as a table-valued pragma argument is a DbParameter. Never paste a filter
pattern or raw application SQL into an acquisition command.

The projection above uses the official
[pragma contracts](https://www.sqlite.org/pragma.html). A pragma returning no rows
must be distinguished from an empty user schema; check the expected column names
and ensure the requested relation exists in sqlite_schema. The default baseline
supports ordinary tables/views; virtual and shadow tables are explicit unresolved
requirements, not ordinary tables guessed from similar columns.

DdlScanner exists only to recover structural catalog information omitted by
pragmas. Its algorithm is fixed and fail-closed:

1. Scan the sqlite_schema CREATE text with states Normal, single-quoted string,
   double-quoted identifier, backtick identifier, bracket identifier, line comment
   and block comment. Doubled delimiters remain inside a token. Track parentheses
   only in Normal; split the outer column/constraint list on commas at depth one.
   Unbalanced quotes/comments/parentheses fail ORMSCHEMA007; never evaluate text.
2. Resolve a column declaration's first identifier against the exact pragma column
   name. Keep text spans, not normalized SQL, for generated/default expressions.
   Recognize table constraints separately; quoted tokens resembling keywords do
   not count as keywords.
3. For hidden=2/3, locate its GENERATED [ALWAYS] AS (...) or AS (...) clause outside
   quoted tokens; take the balanced expression span. Map 2→computedVirtual and
   3→computedStored. Do not guess the expression from generated values.
4. For an ordinary rowid table, INTEGER PRIMARY KEY aliases the rowid only with
   one primary column, declared type exactly INTEGER (case-insensitive keyword)
   and no inline PRIMARY KEY DESC exception. A table-level primary key ordering
   does not trigger that inline exception. AUTOINCREMENT is a separate token flag,
   never inferred merely from INTEGER PRIMARY KEY. WITHOUT ROWID and STRICT come
   from table_list and are independently retained.
5. Preserve dflt_value SQL text from table_xinfo; null means no default, whereas
   the text NULL means a default NULL. Effective result nullability accounts for
   rowid aliases and the explicit primary-key rules of STRICT/WITHOUT ROWID.
6. Use pk ordinal for the primary key. For simple, nonpartial unique indexes, use
   index_xinfo rows with key=1 in seqno order. Expression (`cid=-2`) and partial
   unique indexes are not misreported as unconditional column keys. These physical indexes are
   outside schema v1's unconditional column-key inventory; do not invent a key or
   an option field absent from that format.
7. Group foreign keys by id, order by seq, resolve omitted parent target names
   against the parent's ordered primary key, and preserve action semantics. An
   excluded target becomes an external target through the shared transform.

Declared SQL type text remains independent from SQLite affinity. Apply the exact
SQLite affinity order: contains INT→INTEGER; CHAR/CLOB/TEXT→TEXT; BLOB or empty→
BLOB; REAL/FLOA/DOUB→REAL; otherwise NUMERIC. This is storage behavior metadata,
not permission to identify every NUMERIC declaration as a lossless CLR decimal.
Explicit supported names/facets select registered descriptors; other names remain
unresolved until SchemaTypeBinding supplies a reviewed static mapping.

For coherence: read every relevant schema_version and database-alias list, perform
one full metadata pass, read them again, then repeat the complete pass and compare
canonical pre-filter models plus version/alias lists. Any difference produces
ORMSCHEMA008 and no snapshot; no automatic retry or partial write. Equal passes
are a bounded consistency check, not a claim of a transactionally locked snapshot
against arbitrary DDL that changes and changes back. The caller must run discovery
against a stable schema. Apply SchemaSnapshotTransform.Apply once after collection. Errors or a null
Snapshot cause SchemaValidationException; return its accepted Snapshot otherwise.
The SchemaTool validates/writes it without applying filters/overrides again.

## Exact fixtures, failure cases and commands

Create `StorageTests.cs`, `LifetimeTests.cs`, `CatalogTests.cs`, `DdlScannerTests.cs`,
`Fixture.sql`, `NativeConsumer.csproj` and `check.py`. Use a unique temporary file;
keep two connections only for the busy-lock test and delete the file in finally.
No system SQLite install or service change is required.

```sql
CREATE TABLE row_alias(id INTEGER PRIMARY KEY AUTOINCREMENT,value TEXT);
CREATE TABLE row_desc(id INTEGER PRIMARY KEY DESC,value TEXT);
CREATE TABLE strict_key(id TEXT PRIMARY KEY,value TEXT) STRICT;
CREATE TABLE ordered_key(tenant INTEGER,id INTEGER,PRIMARY KEY(tenant,id)) WITHOUT ROWID;
CREATE TABLE generated_value(id INTEGER PRIMARY KEY,amount INTEGER NOT NULL,
  doubled INTEGER GENERATED ALWAYS AS (amount * 2) STORED,
  default_null TEXT DEFAULT NULL, no_default TEXT);
CREATE TABLE fk_value(tenant INTEGER,id INTEGER,
  FOREIGN KEY(tenant,id) REFERENCES ordered_key(tenant,id));
```

| Case | Exact acceptance |
| --- | --- |
| SQ01 | Same logical slot twice creates p0/p1; Int64 extrema/NULL/text-with-apostrophe-and-NUL/blob round-trip; output direction and unknown codec rejected |
| SQ02 | INTEGER 0/1 maps Boolean; INTEGER2 fails TYPE-005; TEXT "123" is not silently Int64; wrong initial or later mixed storage fails MAP-002 |
| SQ03 | Canonical decimal999.99, UUID, date, local/UTC microsecond timestamps round-trip; Decimal(5,2)1000/1.001, wrong kind and extra tick fail before send |
| SQ04 | SQL NULL / JSON null / JSON string "null" remain different; malformed/uninitialized JSON and missing converter fail |
| SQ05 | Explicit rollback/savepoint/rollback-to/release uses SqliteTransaction; borrowed transaction survives session disposal |
| SQ06 | Pre-cancel sends no command; inspect capabilities false/false; no test claims running native SQL was interrupted by Cancel |
| SQ07 | Connection A holds a write transaction; B with timeout1 attempts a conflicting write and receives SQLITE_BUSY/LOCKED in a bounded test; releasing A permits a new B operation |
| SQ08 | Complete, early-break and failing streams clean up; fresh invocation succeeds and caller-owned open connection stays open |
| SQ09 | Catalog distinguishes row_alias from row_desc, STRICT and WITHOUT ROWID, stored expression, default NULL vs no default and composite FK order |
| SQ10 | Quoted commas/parentheses/keywords and comments in DDL do not confuse scanner; an unsupported/unbalanced form is ORMSCHEMA007, not a fabricated descriptor |
| SQ11 | Mutation injected between metadata passes→ORMSCHEMA008; metadata reads never change schema_version or execute DDL themselves |
| SQ12 | Borrow with DQS_DML/DDL enabled fails EXEC-001 without changing them; factory-created DQS is off and a missing quoted column errors; actual loaded version/source ID and native asset loading are asserted in a published Native AOT executable; test missing asset fails as dependency failure |

```sh
python3 tests/Orm/Providers/Sqlite/check.py --mode managed
python3 tests/Orm/Providers/Sqlite/check.py --mode native
python3 eng/ci/impact.py origin/main --output artifacts/orm-sqlite-plan.json
```

Both modes run the named fixtures; native publishes net11.0/linux-x64 with
warnings-as-errors and checks dynamic code is unsupported. The product CI module
is orm-sqlite-provider; SQLite leaf changes do not require network database
services. Shared Execution/Schema/advanced contracts select this lane as real
consumers. Package native-asset closure is checked again by ORM-PACKAGE's separate
consumer. Stop after these adapter gates; do not create a native execution layer,
publish packages or remove historical SQLite code.
