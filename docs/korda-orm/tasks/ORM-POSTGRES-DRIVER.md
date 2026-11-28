# ORM-POSTGRES-DRIVER — exact Npgsql adapter and catalog acquisition

Status: `planned_candidate`; product implementation is **not authorized**.

## Fixed decision and dependencies

Use Npgsql **11.0.0**, source commit
`4d174200ed48e3e3ab16419dbf84dd655da59de6`, with the unchanged Dapper.AOT 1.1.0
runtime and ORM-EXECUTION's LayoutCommandFactory. Follow the graph-pinned Design
`implementation-spec.md`, `mature-execution.md`, `generation-integration.md` and
ORM-C01/C03–C06. The SQL profile is `postgres-18`, PostgreSQL [18.0,19.0); the research server was
18.7. Do not turn its successful subset into a claim that all future codecs passed.

Start after ORM-FOUNDATION. Acceptance requires ORM-EXECUTION, ORM-SCHEMA and
ORM-ADVANCED-TYPES. Implement scalar transport and catalog fixtures against shared
contracts first; advanced acceptance waits for the real neutral values. Other
providers are not startup dependencies. This task owns no SQL rendering or query
iteration engine.

## Files, API and upstream symbol map

Own `src/Orm/Providers/PostgreSql/` and `tests/Orm/Providers/PostgreSql/`.
The project is `Korda.Orm.PostgreSql.csproj`, namespace `Korda.Orm.PostgreSql`.
References: Execution, SchemaModel, AdvancedTypes, the pure PostgreSQL dialect and
Npgsql; no other driver. Foundation creates the project and the CI owner registers
its actual dependencies. Required files are fixed:

| File / type | Exact responsibility | Mature implementation reused |
| --- | --- | --- |
| `SessionFactory.cs` / `PostgreSqlSession` | OpenAsync and BorrowAsync below; no hidden data-source ownership | NpgsqlDataSource.OpenConnectionAsync and NpgsqlConnection |
| `ProviderServices.cs` / `PostgreSqlServices` | Immutable profile, `(true,true,true)` capabilities, closed codecs and one LayoutCommandFactory | Public Dapper factory protocol |
| `ParameterCodec.cs` / `PostgreSqlParameterEncoder` | Override Create<T>; select the static codec, create an unnamed typed parameter, retain facets/null identity | NpgsqlParameter<T>.TypedValue and explicit NpgsqlDbType |
| `ReaderCodec.cs` | Closed typed reader delegates and declared user/store conversions | NpgsqlDataReader.GetFieldValue<T> and generated Dapper Tokenize/Read |
| `ServerProfile.cs` | ReadAsync, Validate; version/settings check before session admission | Driver's actual server connection; no SQL rewriting |
| `Codecs/ScalarCodecs.cs`, `JsonCodecs.cs`, `ArrayCodecs.cs`, `RangeCodecs.cs`, `TemporalCodecs.cs` | The exact tables/algorithms below | Npgsql's built-in statically reachable converters |
| `MetadataReader.cs` / `PostgreSqlCatalogReader` | ISchemaCatalogReader.ReadAsync; one catalog statement and neutral model construction | PostgreSQL catalogs; jOOQ PostgresDatabase metadata semantics |
| `Metadata/Catalog.sql` | The fixed catalog statement below, embedded as a resource | pg_class/attribute/type/constraint/enum/range |
| `Metadata/TypeDecoder.cs` | Store identity, facets, enum order, domain/array dependencies | pg_type metadata; no CLR-name guessing |

```csharp
public static class PostgreSqlSession
{
    public static Task<OrmSession> OpenAsync(NpgsqlDataSource dataSource,
        CommandOptions? options = null,
        CancellationToken cancellationToken = default);
    public static Task<OrmSession> BorrowAsync(NpgsqlConnection connection,
        NpgsqlTransaction? transaction = null, CommandOptions? options = null,
        CancellationToken cancellationToken = default);
}
public sealed class PostgreSqlCatalogReader : ISchemaCatalogReader
{
    public Task<SchemaSnapshot> ReadAsync(DbConnection connection,
        SchemaReadOptions options, CancellationToken cancellationToken = default);
}
```

Read these pinned source symbols before translating the small adapters:
[NpgsqlCommand.ProcessRawQuery](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlCommand.cs),
[NpgsqlParameter](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlParameter.cs),
[NpgsqlDataReader](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlDataReader.cs),
[NpgsqlSlimDataSourceBuilder](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlSlimDataSourceBuilder.cs).
The parameter collection and protocol retain upstream ownership. Do not copy their
internal resolver chain or invoke Reflection.Emit/MakeGenericType.

## Session/profile algorithm

1. Validate arguments, timeout and pre-cancel before opening anything. OpenAsync
   borrows the caller's data source and obtains one connection from it; it owns
   that connection only. BorrowAsync requires State=Open and a transaction whose
   Connection is that same instance; it never opens/closes the caller connection.
2. Run one read-only profile command on the open connection, enlisting the supplied
   transaction when present:
   `SELECT current_setting('server_version_num')::integer,
   current_setting('standard_conforming_strings'), current_database()`.
   Parse 180000 <= version < 190000 and require standard_conforming_strings=on.
   Reject mismatch with KORM-EXEC-001; never issue a corrective SET.
3. Construct PostgreSqlProfile.Create() with numbered placeholders and immutable
   verified settings. Preserve the actual server version only in diagnostic/schema
   metadata; do not narrow the template's [18,19) interval to a single patch version.
4. Construct PostgreSqlServices, its closed codecs and LayoutCommandFactory. Return
   OrmSession.Own for the acquired connection, or Borrow for the caller connection
   and transaction. On initialization failure dispose only an acquired connection,
   preserving the original error if disposal also fails, as in ORM-EXECUTION.
5. The application owns the data source and transaction. The session does not
   dispose either, enlist an ambient transaction, retry commit, call Prepare or
   alter connection pooling. For tests, the caller explicitly creates its source
   with pooling off. Normal pooling remains Npgsql's policy.

A test helper may build NpgsqlSlimDataSourceBuilder with EnableArrays,
EnableRanges and EnableTransportSecurity before Build. Do not enable dynamic JSON,
unmapped types, composite discovery, record-as-tuple mapping or global type scans.
Ordinary user-created sources are admitted only when their declared codecs pass
actual provider validation; a source lacking a required built-in mapping fails its
codec case instead of enabling a fallback.

## Parameter and read codec contract

ProviderServices.ValidateConnection(DbConnection,DbTransaction?) performs static
`is` checks for NpgsqlConnection/NpgsqlTransaction and checks an optional transaction's
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

The LayoutCommandFactory already iterates every physical occurrence. Create<T>
checks the command is NpgsqlCommand, exact SQL identity/nullability/facets and a
statically compiled matching codec. It returns a parameter without adding it.
Use `ParameterName = ""`, Direction=Input, explicit NpgsqlDbType, validated
Precision/Scale, then TypedValue. Leave input text/binary Size=0 (unlimited); never
copy a SQL character-length facet into the driver's truncating UTF-16 Size. Each textual `$n` has a separate parameter;
repeated logical slots never reuse a physical name. No SQL-token scan is involved.

Keep one immutable catalog of statically constructed typed codecs, indexed by SQL
identity and nullability; verifying a closed generic codec interface is allowed.
There is no runtime CLR-Type-to-created-code dictionary. A declared codec can use
a different statically known TStore after its explicit StaticConversion. The
parameter is then NpgsqlParameter<TStore>. Nullable values use the corresponding
closed nullable/reference codec with explicit NpgsqlDbType; absence never triggers
an untyped SQL-type inference. Unsupported identity/codec fails KORM-BIND-005 before SQL is sent.

| SQL identity / CLR | Parameter type | Read and validation |
| --- | --- | --- |
| int16 / short | Smallint | GetInt16; no implicit narrowing |
| int32 / int | Integer | GetInt32; no implicit Int64 narrowing |
| int64 / long | Bigint | GetInt64; full signed range |
| boolean / bool | Boolean | GetBoolean |
| text / string | Text, or Varchar for an explicit length facet | GetString; ordinal text; reject U+0000 before binding |
| binary / byte[] | Bytea | GetFieldValue<byte[]> into owned bytes; input snapshot belongs to ParameterValues |
| decimal(p,s) / decimal | Numeric | GetDecimal; p=1..28, s=0..p and exact value-fit checks before/after conversion |
| float32 / float; float64 / double | Real; Double | GetFloat/GetDouble only for the explicitly declared floating identity; nonfinite policy comes from its accepted type contract |
| uuid / Guid | Uuid | GetGuid, with no text/binary byte-order guess |
| json / JsonText | Json, transport string | Validate owned UTF-8 before writing; read text and construct JsonText |
| pg.jsonb / JsonbText | Jsonb, transport string | Validate on write/read; compare decoded structure, not property order or original formatting |
| date / DateOnly | Date | Closed GetFieldValue<DateOnly>; reject infinity/out-of-range |
| local time / TimeOnly | Time | Closed typed getter; precision 0..6, exact tick divisibility |
| local timestamp / DateTime | Timestamp | Kind=Unspecified and exact declared precision |
| instant / DateTimeOffset or declared UTC DateTime | TimestampTz | Offset=0 or Kind=Utc only; no preservation of input timezone |

The nullable variant retains the same SQL identity and tests IsDBNull before its
getter. Required NULL is KORM-MAP-003; a non-null conversion failure preserves the
underlying cause. Generated bound factories use the execution reader-binding seam;
codecs do not own reader iteration. Actual reader metadata is checked at first-row
Tokenize according to the declared provider storage contract; empty results follow
the common no-Tokenize promise.

Aggregate reader conversions are registered under these exact IDs:
`aggregate.int-sum.decimal` accepts the declared native bigint/numeric SUM result
and returns checked decimal?; `aggregate.decimal-sum.decimal` and
`aggregate.numeric-avg.decimal` accept native numeric; `aggregate.floating.double`
accepts its declared floating aggregate representation. A non-null result outside
CLR decimal fails TYPE-005; an empty aggregate returns null. Do not CAST a numeric
SUM to bigint or use Convert.ChangeType. Ordinary decimal getters do not acquire
these wider source-representation permissions accidentally.

### Initial advanced closures

Ship only statically rooted array element families int, long, string and their
specified nullable-element forms, plus int4range and int8range. Bind SqlArray<T>
through a copied T[] and NpgsqlDbType.Array | the element type. Empty arrays remain
empty scalar parameters; an IN list is a different contract. SqlArray is a one-dimensional sequence: writing uses PostgreSQL lower bound1;
reading preserves provider element order and normalizes the source lower bound.
Reject unsupported rank, but do not promise to detect/reject a non-1 lower bound
that Npgsql has already discarded. Arrays.Element means one-based sequence
position and the pure PG dialect emits array[array_lower(array,1)+index-1], with
SQL NULL on out-of-range. Preserving arbitrary database bounds is a different,
unsupported full SQL-array-value contract.

For SqlRange<int>/SqlRange<long>, map Empty to NpgsqlRange<T>.Empty; otherwise use
its finite/infinite and inclusion flags to construct the matching NpgsqlRange<T>.
Read the closed driver range and reconstruct neutral bounds. Compare canonical
server semantics: PostgreSQL can normalize discrete finite endpoints, so input
spelling need not round-trip byte-for-byte. Required NULL and empty range differ.

Known enum/domain identities remain distinct. Baseline native arbitrary enum and
composite mapping is unsupported unless an explicit closed codec is supplied and
accepted; no EnableUnmappedTypes or dynamic registration is permitted. A portable
EnumMap<TEnum> text conversion validates supplied labels and is a distinct declared
conversion, not a native enum claim. Domain validation runs before its explicit
base-store conversion; preserve the domain identity in descriptors and metadata.

## Catalog acquisition: exact read protocol

ReadAsync accepts the shared SchemaReadOptions in Execution.Metadata. Require an
open NpgsqlConnection, no active caller operation/transaction and the PostgreSQL profile; borrow it without Open/Close,
DDL, transaction begin/commit/rollback or data-row sampling. Profile validation
precedes acquisition. Use one statement so its catalog reads share a PostgreSQL
statement snapshot. Catalog OIDs are temporary lookup keys only; persisted IDs
come from SchemaIdentity's length-prefixed qualified names.

Catalog.sql uses this fixed projection. Add fields only through a reviewed schema
contract change; do not replace it with generic GetSchema/reflection discovery.

```sql
WITH RECURSIVE rel AS (
  SELECT c.oid, n.nspname, c.relname, c.relkind
  FROM pg_catalog.pg_class c
  JOIN pg_catalog.pg_namespace n ON n.oid=c.relnamespace
  WHERE c.relkind IN ('r','p','v','m','f')
    AND n.nspname <> 'information_schema'
    AND n.nspname !~ '^pg_'
), col AS (
  SELECT a.*, d.adbin, r.nspname, r.relname
  FROM pg_catalog.pg_attribute a
  JOIN rel r ON r.oid=a.attrelid
  LEFT JOIN pg_catalog.pg_attrdef d
    ON d.adrelid=a.attrelid AND d.adnum=a.attnum
  WHERE a.attnum>0 AND NOT a.attisdropped
), type_ids(oid) AS (
  SELECT DISTINCT atttypid FROM col
  UNION
  SELECT child.oid FROM type_ids i
  JOIN pg_catalog.pg_type t ON t.oid=i.oid
  LEFT JOIN pg_catalog.pg_range g ON g.rngtypid=t.oid
  CROSS JOIN LATERAL unnest(ARRAY[t.typelem,t.typbasetype,g.rngsubtype]) child(oid)
  WHERE child.oid IS NOT NULL AND child.oid<>0
), rows AS (
  SELECT 'relation' AS kind, r.oid::text AS object_key,
    jsonb_build_object('oid',r.oid,'schema',r.nspname,'name',r.relname,
      'kind',r.relkind) AS payload FROM rel r
  UNION ALL
  SELECT 'column',a.attrelid::text||':'||a.attnum::text,
    jsonb_build_object('relation',a.attrelid,'attnum',a.attnum,'name',a.attname,
      'type',a.atttypid,'typmod',a.atttypmod,'dimensions',a.attndims,
      'notNull',a.attnotnull,'identity',a.attidentity,
      'generated',a.attgenerated,
      'expression',pg_catalog.pg_get_expr(a.adbin,a.attrelid),
      'collationSchema',cn.nspname,'collationName',cl.collname,
      'characterSet',current_setting('server_encoding'),
      'sequenceStart',sq.seqstart,'sequenceIncrement',sq.seqincrement,
      'sequenceMin',sq.seqmin,'sequenceMax',sq.seqmax,
      'sequenceCache',sq.seqcache,'sequenceCycle',sq.seqcycle)
  FROM col a
  LEFT JOIN pg_catalog.pg_collation cl ON cl.oid=a.attcollation
  LEFT JOIN pg_catalog.pg_namespace cn ON cn.oid=cl.collnamespace
  LEFT JOIN pg_catalog.pg_depend dp
    ON dp.refclassid='pg_catalog.pg_class'::regclass
   AND dp.refobjid=a.attrelid AND dp.refobjsubid=a.attnum
   AND dp.classid='pg_catalog.pg_class'::regclass AND dp.deptype='i'
  LEFT JOIN pg_catalog.pg_sequence sq ON sq.seqrelid=dp.objid
  UNION ALL
  SELECT 'type',t.oid::text,
    jsonb_build_object('oid',t.oid,'schema',n.nspname,'name',t.typname,
      'kind',t.typtype,'category',t.typcategory,'base',t.typbasetype,
      'element',t.typelem,'typmod',t.typtypmod,'notNull',t.typnotnull,
      'subtype',g.rngsubtype,'collationSchema',tcns.nspname,
      'collationName',tc.collname,'characterSet',current_setting('server_encoding'))
  FROM type_ids i JOIN pg_catalog.pg_type t ON t.oid=i.oid
  JOIN pg_catalog.pg_namespace n ON n.oid=t.typnamespace
  LEFT JOIN pg_catalog.pg_range g ON g.rngtypid=t.oid
  LEFT JOIN pg_catalog.pg_collation tc ON tc.oid=t.typcollation
  LEFT JOIN pg_catalog.pg_namespace tcns ON tcns.oid=tc.collnamespace
  UNION ALL
  SELECT 'enum',e.enumtypid::text||':'||e.oid::text,
    jsonb_build_object('type',e.enumtypid,'order',e.enumsortorder,'label',e.enumlabel)
  FROM pg_catalog.pg_enum e JOIN type_ids i ON i.oid=e.enumtypid
  UNION ALL
  SELECT 'constraint',k.oid::text,
    jsonb_build_object('relation',k.conrelid,'name',k.conname,'kind',k.contype,
      'columns',k.conkey,'target',k.confrelid,'targetColumns',k.confkey,
      'update',k.confupdtype,'delete',k.confdeltype,
      'match',k.confmatchtype,'deferrable',k.condeferrable,
      'initiallyDeferred',k.condeferred,'index',k.conindid)
  FROM pg_catalog.pg_constraint k JOIN rel r ON r.oid=k.conrelid
  WHERE k.contype IN ('p','u','f')
)
SELECT kind,object_key,payload::text FROM rows ORDER BY kind,object_key;
```

Model construction is fixed:

1. Parse the three columns with explicit JsonDocument property access or generated
   JSON metadata. Resolve all OID references before filtering; actual catalog name
   is current_database(), schema/local names retain exact text. Generated SQL uses
   schema+local qualification; catalog remains part of stable metadata identity.
2. Columns are ordered by attnum but get dense zero-based visible ordinals after
   dropped attributes are removed. Never treat attnum-1 as dense after a drop.
3. attidentity a/d maps to identityAlways/identityByDefault; populate exposed
   pg_sequence start/increment/min/max/cache/cycle as structural values (integer
   strings in SchemaIdentityOptions), never current/next sequence data. Then attgenerated s/v maps
   to computedStored/computedVirtual; otherwise a non-null expression is default,
   including the text NULL, and no expression is none. Preserve actual column/type
   collation qualified names and server character encoding for collatable types;
   noncollatable types have null collation/charset facets. Serial defaults remain
   defaults; do not infer identity merely from a sequence expression.
4. Resolve domain/array/base/range dependencies transitively; SchemaTypeKind.Range
   uses RangeSubtypeId for the declared subtype, not ElementTypeId. Preserve enum labels
   by enumsortorder, not alphabetically. Preserve attndims as declared metadata;
   runtime array shape is separately validated. Unknown/composite/multirange types
   become unresolved codec requirements rather than string/object mappings.
5. Decode varchar length as typmod-4 for valid nonnegative typmods. Numeric uses
   precision=((typmod-4)>>16)&65535 and signed scale=(((typmod-4)&2047)^1024)-1024.
   Negative scale or precision beyond the declared CLR decimal subset is preserved
   as unsupported metadata, not clamped. Domain base typmod is retained. Timestamp/
   time typmod=-1 means server default precision; persist that fact, while a chosen
   CLR codec uses an explicit precision policy.
6. Keys retain conkey array order. Foreign keys zip conkey/confkey by index, retain
   referential actions and target identities. Map action a/r/c/n/d to
   NoAction/Restrict/Cascade/SetNull/SetDefault; match s/f/p to Simple/Full/Partial.
   Preserve condeferrable/condeferred. Build index-OID→SchemaKeyId from primary/
   unique constraints' conindid; use it for a foreign key's referenced TargetKeyId
   when present, otherwise keep null without inventing uniqueness. Excluded targets remain external
   with enough target column/type data; do not drop the constraint. Visible catalog
   permission gaps/missing targets are ORMSCHEMA004, never guessed keys.
7. SchemaSnapshotTransform.Apply runs once for selection, type closure and
   overrides. If its result has errors or Snapshot=null, throw SchemaValidationException;
   otherwise return the validated Snapshot. The SchemaTool does not apply filters/
   overrides again. Canonical serialization remains SchemaSnapshotCodec's job. Unresolved error mode fails with
   ORMSCHEMA007; explicit Record mode keeps the requirement. Read permission/catalog
   failures propagate with safe context; no partial successful snapshot is emitted.

The collected kind tags include materialized views/foreign tables so an explicitly
selected unsupported relation kind can fail ORMSCHEMA007 instead of pretending it
is absent. The accepted schema v1 relation inventory is ordinary/partitioned tables
and views. Apply exact include/exclude selection to the raw kind/name list before
constructing supported relations; retain metadata needed by selected FK/type
closure. System schemas remain outside acquisition. Partial/expression index
metadata is outside v1's unconditional column-key inventory and is never invented
as an ordinary key. No
implicit DDL transaction or attempt to lock every table is added.

## Required fixture files and exact acceptance

Create `Fixture.sql`, `ScalarTests.cs`, `AdvancedTests.cs`, `LifetimeTests.cs`,
`CatalogTests.cs`, `NativeConsumer.csproj` and `check.py` under this task's tests.
Use the five-user/two-department fixture from ORM-INTEGRATION plus schema objects:

```sql
CREATE TYPE mood AS ENUM ('sad','ok','happy');
CREATE DOMAIN positive_id AS bigint CHECK (VALUE>0);
CREATE TABLE parent_key(tenant_id bigint,id bigint,
  PRIMARY KEY(tenant_id,id));
CREATE TABLE child_key(id bigint GENERATED ALWAYS AS IDENTITY,
  tenant_id bigint NOT NULL,parent_id bigint NOT NULL,
  label varchar(12) DEFAULT NULL,
  doubled bigint GENERATED ALWAYS AS (parent_id*2) STORED,
  status mood, domain_id positive_id,
  FOREIGN KEY(tenant_id,parent_id) REFERENCES parent_key(tenant_id,id));
```

| Case | Required observation |
| --- | --- |
| PG01 | `$1/$2` with two physical occurrences of one Int64 slot returns the same value twice; both parameter names empty and order exact |
| PG02 | long extrema, typed NULL, string apostrophe/backslash and byte[] round-trip; required NULL/narrowing/unknown codec reject with exact BIND/MAP/TYPE code |
| PG03 | JsonText SQL NULL / JSON null / JSON string "null" differ; JsonbText normalizes structure without losing values |
| PG04 | int/long/text arrays, empty and permitted nullable elements; source mutation cannot change captured values; unsupported rank fails; a non-1 server lower bound normalizes to ordered sequence values |
| PG05 | empty, unbounded and finite int4/int8 ranges; canonical `[1,5)` semantic result; missing codec rejected |
| PG06 | decimal(5,2) 999.99 passes, 1000/1.001 fail before send; local/UTC precision p=6 exact succeeds, extra tick and wrong kind fail |
| PG07 | Transaction insert ID6, savepoint, rollback-to, release and outer rollback via NpgsqlTransaction preserve exact fixture; session never commits/disposes caller transaction |
| PG08 | Pre-cancel sends nothing; running pg_sleep(10) cancelled after 250ms stops before 5s in bounded local gate; fresh query succeeds; timeout=1 surfaces driver timeout and reuse succeeds |
| PG09 | Early stream break disposes reader/command and permits next fresh invocation; borrowed connection remains open |
| PG10 | Catalog has enum order sad/ok/happy, domain identity, varchar length12, nullable default NULL, stored expression, identityAlways and ordered composite FK; excluded parent stays external |
| PG11 | Profile version/mode mismatch→EXEC-001; denied catalog access or unsupported relation/type never emits a silently partial accepted snapshot |

```sh
python3 tests/Orm/Providers/PostgreSql/check.py --mode managed --connection-env KORDA_TEST_POSTGRES
python3 tests/Orm/Providers/PostgreSql/check.py --mode native --connection-env KORDA_TEST_POSTGRES
python3 eng/ci/impact.py origin/main --output artifacts/orm-postgres-plan.json
```

The checker publishes/runs the actual net11.0 Linux x64 Native AOT consumer with
warnings-as-errors and dynamic-code-disabled assertion; it does not substitute
mock success for a server lane. Missing explicit test connection is a configuration
error. It initializes only its owned fixture schema and cleans it in finally.
Register orm-postgres-provider and its PostgreSQL metadata lane with only its true prerequisites;
shared Execution/Schema changes select it, an unrelated provider leaf does not.
Stop after its scalar, declared advanced, catalog and lifetime gates pass. Package
publication, whole-product performance and cutover are separate tasks.
