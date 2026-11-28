# ORM-MYSQL-DRIVER — exact MySqlConnector transport and two server profiles

Status: `planned_candidate`; product implementation is **not authorized**.

## Fixed outcome and dependencies

Use MySqlConnector **3.0.0**, source commit
`95875a195369f0dd804f63ded2f95da3fed59ec2`, and the unchanged Dapper.AOT 1.1.0
runtime through ORM-EXECUTION's typed layout factory. MySQL `mysql-8.4`
[8.4.0,8.5.0) and MariaDB `mariadb-11.8` [11.8.0,11.9.0) are distinct mandatory
profiles. One driver does not imply equal SQL or metadata semantics. The research
servers were MySQL 8.4.11 and MariaDB 11.8.10.

Read the graph-pinned implementation-spec, mature-execution, generation-integration
and contracts ORM-C01/C03–C06, plus the two pure dialect packets and
ORM-ADVANCED-TYPES/ORM-NESTED. Start after ORM-FOUNDATION; acceptance requires
ORM-EXECUTION, ORM-SCHEMA and accepted advanced value contracts. Scalar work can
start from shared fixtures without waiting for another provider.

## Files, public endpoints and source reuse

Own `src/Orm/Providers/MySql/` and `tests/Orm/Providers/MySql/`.
The project is `Korda.Orm.MySql.csproj`, namespace `Korda.Orm.MySql`, referencing
Execution, SchemaModel, AdvancedTypes, both pure MySQL/MariaDB dialects and
MySqlConnector. Foundation/CI own root/project registration. Add these exact files:

| File / type | Required implementation |
| --- | --- |
| `SessionFactory.cs` / `MySqlSession` | The explicit-family OpenAsync/BorrowAsync below |
| `ProviderServices.cs` / `MySqlServices` | Verified immutable family/profile, `(true,true,true)` capabilities, codec catalog and LayoutCommandFactory |
| `ParameterCodec.cs` / `MySqlParameterEncoder` | Create<T>; explicit MySqlDbType, Direction=Input, validated facets and storage value |
| `ReaderCodec.cs` | Closed typed getter/conversion delegates; family-specific storage checks |
| `Codecs/ScalarCodecs.cs`, `JsonCodec.cs`, `TemporalCodecs.cs` | Exact declared support and validation tables below |
| `ServerProfile.cs` | Family/version/mode/client-option verification; never issue SET |
| `MetadataReader.cs` / `MySqlCatalogReader` | Borrowed read-only acquisition, full-pass comparison and shared transform |
| `Metadata/CatalogQueries.cs` | Fixed table/column/key/FK queries, with explicit family-specific projection where necessary |
| `Metadata/DdlScanner.cs` | Bounded SHOW CREATE column/default/generated/JSON recognition; no arbitrary SQL execution |
| `Metadata/TypeDecoder.cs` | Signedness/facets/charset/collation/native JSON versus MariaDB text distinctions |

```csharp
public static class MySqlSession
{
    public static Task<OrmSession> OpenAsync(MySqlDataSource dataSource,
        DatabaseFamily family, CommandOptions? options = null,
        CancellationToken cancellationToken = default);
    public static Task<OrmSession> BorrowAsync(MySqlConnection connection,
        DatabaseFamily family, MySqlTransaction? transaction = null,
        CommandOptions? options = null,
        CancellationToken cancellationToken = default);
}
public sealed class MySqlCatalogReader : ISchemaCatalogReader
{
    public Task<SchemaSnapshot> ReadAsync(DbConnection connection,
        SchemaReadOptions options, CancellationToken cancellationToken = default);
}
```

The only admitted family arguments are MySql and MariaDb. Missing/other family is
an argument error carrying KORM-EXEC-001; do not infer it solely from the driver
class. The catalog reader takes the explicit family from options.Profile.

| Mature source symbol | Local use |
| --- | --- |
| [MySqlCommand](https://github.com/mysql-net/MySqlConnector/blob/95875a195369f0dd804f63ded2f95da3fed59ec2/src/MySqlConnector/MySqlCommand.cs) | Real sync/async execution, command timeout, cancellation, transaction association |
| [MySqlParameter](https://github.com/mysql-net/MySqlConnector/blob/95875a195369f0dd804f63ded2f95da3fed59ec2/src/MySqlConnector/MySqlParameter.cs) | Explicit MySqlDbType before Value prevents unintentional inference; retain mature text/binary protocol serialization |
| [MySqlDataReader](https://github.com/mysql-net/MySqlConnector/blob/95875a195369f0dd804f63ded2f95da3fed59ec2/src/MySqlConnector/MySqlDataReader.cs) | Typed values, result metadata and ownership |
| [MySqlConnectionStringBuilder](https://github.com/mysql-net/MySqlConnector/blob/95875a195369f0dd804f63ded2f95da3fed59ec2/src/MySqlConnector/MySqlConnectionStringBuilder.cs) | Named conversion-related options; never dump connection strings |
| jOOQ MySQLDatabase/MariaDBDatabase at the pinned 3.21.10 source | Catalog semantics and family distinctions; no port of JDBC execution/pooling |

## Opening, borrowing and compatibility verification

1. Validate public arguments, family, timeout and pre-cancellation. OpenAsync gets
   one connection from the caller-owned data source and owns only that connection.
   BorrowAsync requires it already open and verifies same-instance transaction
   association. Both must be called without another active operation on that
   connection; the returned session subsequently enforces its own operation lease.
2. Inspect only the named client conversion settings using the driver's builder:
   TreatTinyAsBoolean=false, GuidFormat=None, DateTimeKind=Unspecified,
   AllowZeroDateTime=false, ConvertZeroDateTime=false, IgnoreCommandTransaction=false.
   Reject mismatch with EXEC-001. Do not change these settings or silently coerce
   all CHAR(36) to Guid or TINYINT(1) to bool. The application configures its source.
3. Execute one read-only command, associated with the supplied transaction:

```sql
SELECT VERSION(), @@version_comment, @@session.sql_mode,
       @@session.character_set_connection, @@lower_case_table_names,
       @@session.time_zone, @@session.group_concat_max_len;
```

4. Parse the actual product version: a MariaDB marker must match family MariaDb;
   parse its actual 11.8 version rather than a compatibility prefix such as 5.5.5.
   MySql requires a MySQL 8.4 server, with no MariaDB marker. Reject another product
   or interval. Split sql_mode on commas using ordinal case-insensitive keyword
   comparison; require NO_BACKSLASH_ESCAPES, ONLY_FULL_GROUP_BY and STRICT_TRANS_TABLES.
   Both families reject HIGH_NOT_PRECEDENCE. MariaDB additionally rejects ORACLE,
   SIMULTANEOUS_ASSIGNMENT and EMPTY_STRING_IS_NULL modes in this profile. Require utf8mb4 and time_zone=`+00:00`; an unexpanded `SYSTEM` value is
   not proof of the required timezone. Keep the observed lower_case_table_names
   value 0/1/2 in the immutable profile.
5. Retain group_concat_max_len as a verified MariaDB nested-transport limit; never
   raise it with SET. The ORM-NESTED SQL guard returns its dedicated error envelope
   when actual bytes exceed either that limit or the declared payload budget.
   Treat the setting as semantic metadata for the relevant nested profile; never
   infer successful complete JSON solely because the command returned a string.
6. Construct services and return Own/Borrow. On failure dispose an acquired
   connection while preserving the primary exception, and leave borrowed resources
   untouched. The session never disposes the caller data source/transaction,
   commits, retries, enables automatic prepare or manages a private pool.

The pure profiles and templates include semantic mode/timezone settings. A caller
changing them on the underlying connection must create a newly verified session;
mutating a profile or template in place is forbidden. Do not add a verification
round trip before every application query. Sources on which these constraints
cannot be established fail closed rather than selecting a guessed profile.

## Exact codecs and binding sequence

ProviderServices.ValidateConnection(DbConnection,DbTransaction?) performs static
`is` checks for MySqlConnection/MySqlTransaction and checks an optional transaction's
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

Create<T> requires MySqlCommand. Resolve a statically registered codec by SQL type
identity/nullability and any explicit conversion ID. Run source validation,
ToStore, store validation, then create MySqlParameter. Assign ParameterName
`p0` onward, MySqlDbType before Value, Direction=Input and validated precision/
scale. Leave input text/binary Size at its default0; validate length without using
parameter Size as a truncation mechanism. A
nullable SQL value uses DBNull.Value with that same explicit type. The caller adds
the parameter exactly once. Size/precision/scale never silently truncate or round.
The driver's object Value boundary boxes value types; no no-boxing claim is made.

| Identity / CLR | MySqlDbType / transport | Closed read/validation |
| --- | --- | --- |
| int16 / short | Int16 | GetInt16; no implicit narrowing |
| int32 / int | Int32 | GetInt32; signed Int64 narrowing needs an explicit checked conversion |
| int64 / long | Int64 | GetInt64, exact signed range |
| declared uint64 / ulong | UInt64 | GetFieldValue<ulong>; 2^63 is not silently read as negative Int64 |
| boolean / bool | Byte, stored sbyte 0/1 | Read the declared integral storage and require 0/1; TINYINT(1) alone is not metadata proof of Boolean intent |
| text / string | VarChar or Text according to declared type/length | GetString, validated character length and charset; do not infer Guid |
| binary / byte[] | VarBinary/Blob according to descriptor | Owned byte[]; no text conversion |
| decimal(p,s) / decimal | NewDecimal | GetDecimal, p<=28 and exact p/s fit; reject larger unsupported decimal metadata until an explicit codec exists |
| float32 / float; float64 / double | Float; Double | Closed typed getter for declared floating identity only |
| UUID / Guid | String transport of canonical lowercase D text into CHAR(36) | GetString then ParseExact D; binary UUID/byte-order variants outside this baseline |
| JSON / JsonText on MySQL | JSON, validated string transport | Read JSON text and validate neutral JsonText; compare decoded structure |
| JSON / JsonText on MariaDB | JSON parameter with validated text storage | Do not claim MySQL binary JSON storage; retain MariaDB catalog representation |
| date / DateOnly | Date | Exact supported calendar range; zero/invalid date fails |
| local time / TimeOnly | Time | [00:00,24:00), p<=6; negative or >=24h TIME needs a separate duration identity and is rejected |
| local timestamp / DateTime | DateTime | Kind=Unspecified; year1000..9999 and exact fractional precision |
| instant / UTC DateTime or zero-offset DateTimeOffset | Timestamp, explicit UTC store conversion | Session +00:00 required; reject offsets/kinds/ranges outside the declared baseline |

Register the built-in result codecs `cast.int16.checked` and
`cast.int32.checked`. The first accepts only logical int16 with short/short?, the
second only int32 with int/int?. The expression/dialect emits CAST AS SIGNED;
MySQL and MariaDB expose its result as signed Int64. ValidateResult uses Execution's
effective read-ID rule, so a member without an attribute consumes the column ID.
ValidateReaderColumn permits that signed Int64 representation only for these
explicit IDs, and BindReader returns one cached delegate that applies DBNull
policy, calls GetInt64, then `checked((short)value)` or `checked((int)value)`.
Overflow is TYPE-005 retaining OverflowException; required DBNull is MAP-003;
unsigned, decimal, floating/text storage, wrong logical ID/T or conflicting
member/column conversion IDs are MAP-002. Do not use Convert.ChangeType or a
driver getter that silently changes the allowed native representation.

Ordinary int16/int32 column codecs continue to require their declared native
signed integer width. These cast codecs do not make an arbitrary BIGINT projection
compatible with a short/int DTO. Promoted arithmetic uses its Int64/Double/Decimal
descriptor and null ConversionId, never either narrowing ID. Native server errors
from the SQL cast propagate unchanged.

Run the exact same fixtures on both families: CAST(32767 AS SIGNED) and
CAST(-32768 AS SIGNED) to short, CAST(2147483647 AS SIGNED) to int, nullable NULL
to int?, and 32768/-32769/2147483648 under the corresponding declared cast ID.
Boundary values pass; the three out-of-range results fail TYPE-005. A plain BIGINT
column mapped as short without the explicit cast ID fails MAP-002, even when its
current value would fit. Equal member/column IDs execute the conversion once;
different non-null IDs fail before CreateCommand.

The common portable instant baseline is 1970-01-01T00:00:01Z through
2038-01-19T03:14:07.499999Z, subject to declared precision. MariaDB may support a
wider native range; this profile does not silently widen a portable descriptor.
The local DATETIME baseline likewise caps its final day at
9999-12-31T23:59:59.499999, following the documented supported fractional range.
Zero dates and automatic MinValue conversion are prohibited. Required/nullable
and conversion NULL policy are applied by the typed reader delegate exactly once.
A false precision claim is rejected before send even if the server could round it.

BindReader<T> returns a closed getter/conversion delegate during mapping Bind;
Read invokes the cached delegate without a per-row catalog lookup. Tokenize calls
ValidateReaderColumn once for each actual ordinal/type/name. A decoder encountering
invalid data or a required NULL produces MAP-003 for required NULL or TYPE-005 for a failed known conversion with safe ordinal/type
context and the original exception. An absent codec is BIND-005 for parameter-codec lookup, never
reflection mapping. Arrays/ranges/pg.jsonb/composites and arbitrary native enum/
domain codecs are unsupported here; an explicit portable text conversion is a
separate declared representation.

Timestamp reading uses GetDateTime under the required Unspecified driver setting,
then DateTime.SpecifyKind(value,Utc) (or its zero-offset DateTimeOffset) only for
the explicit instant descriptor and verified +00:00 session. Local DATETIME stays
Unspecified. This reattaches the known storage timezone; it never guesses the
application machine's local timezone. Supported boundary references are the
[MySQL 8.4 date/time ranges](https://dev.mysql.com/doc/refman/8.4/en/datetime.html).

Aggregate IDs `aggregate.int-sum.decimal`, `aggregate.decimal-sum.decimal` and
`aggregate.numeric-avg.decimal` read the native exact decimal result into checked
decimal?, preserving empty NULL and rejecting values outside the CLR subset.
`aggregate.floating.double` reads the native approximate result. No CAST AS SIGNED
or Convert.ChangeType narrows a SUM merely to share an Int64 DTO. These are explicit
result conversions and do not weaken ordinary parameter/storage identity checks.

## Read-only catalog acquisition and coherent model construction

ReadAsync requires an open MySqlConnection, explicit profile and no active caller
operation/transaction. The tool owns the open connection; the adapter never opens,
closes, starts/commits a transaction, issues SET, DDL or samples application rows.
Use only metadata visible to the caller. Retain TABLE_CATALOG (normally `def`) in
stable identities and TABLE_SCHEMA as the database/schema name. Generated SQL
qualification is schema+local name, not catalog.schema.local. Case behavior is
validated against lower_case_table_names; never apply universal lowercase to IDs.

Execute the following fixed queries for every complete catalog pass. All collect
the same selected user-schema set conservatively; shared filtering is performed
later. No include/exclude pattern becomes an SQL fragment.

```sql
SELECT TABLE_CATALOG,TABLE_SCHEMA,TABLE_NAME,TABLE_TYPE,ENGINE
FROM information_schema.TABLES
WHERE TABLE_SCHEMA NOT IN ('mysql','information_schema','performance_schema','sys')
ORDER BY TABLE_SCHEMA,TABLE_NAME;

SELECT TABLE_CATALOG,TABLE_SCHEMA,TABLE_NAME,COLUMN_NAME,ORDINAL_POSITION,
       COLUMN_DEFAULT,IS_NULLABLE,DATA_TYPE,COLUMN_TYPE,
       CHARACTER_MAXIMUM_LENGTH,NUMERIC_PRECISION,NUMERIC_SCALE,
       DATETIME_PRECISION,CHARACTER_SET_NAME,COLLATION_NAME,
       EXTRA,GENERATION_EXPRESSION
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA NOT IN ('mysql','information_schema','performance_schema','sys')
ORDER BY TABLE_SCHEMA,TABLE_NAME,ORDINAL_POSITION;

SELECT tc.CONSTRAINT_CATALOG,tc.CONSTRAINT_SCHEMA,tc.TABLE_NAME,
       tc.CONSTRAINT_NAME,tc.CONSTRAINT_TYPE,kcu.ORDINAL_POSITION,
       kcu.COLUMN_NAME,kcu.REFERENCED_TABLE_SCHEMA,kcu.REFERENCED_TABLE_NAME,
       kcu.REFERENCED_COLUMN_NAME,kcu.POSITION_IN_UNIQUE_CONSTRAINT
FROM information_schema.TABLE_CONSTRAINTS tc
JOIN information_schema.KEY_COLUMN_USAGE kcu
  ON tc.CONSTRAINT_CATALOG=kcu.CONSTRAINT_CATALOG
 AND tc.CONSTRAINT_SCHEMA=kcu.CONSTRAINT_SCHEMA
 AND tc.TABLE_NAME=kcu.TABLE_NAME AND tc.CONSTRAINT_NAME=kcu.CONSTRAINT_NAME
WHERE tc.CONSTRAINT_SCHEMA NOT IN ('mysql','information_schema','performance_schema','sys')
  AND tc.CONSTRAINT_TYPE IN ('PRIMARY KEY','UNIQUE','FOREIGN KEY')
ORDER BY tc.CONSTRAINT_SCHEMA,tc.TABLE_NAME,tc.CONSTRAINT_NAME,kcu.ORDINAL_POSITION;

SELECT CONSTRAINT_CATALOG,CONSTRAINT_SCHEMA,CONSTRAINT_NAME,TABLE_NAME,
       UNIQUE_CONSTRAINT_CATALOG,UNIQUE_CONSTRAINT_SCHEMA,UNIQUE_CONSTRAINT_NAME,
       REFERENCED_TABLE_NAME,MATCH_OPTION,UPDATE_RULE,DELETE_RULE
FROM information_schema.REFERENTIAL_CONSTRAINTS
WHERE CONSTRAINT_SCHEMA NOT IN ('mysql','information_schema','performance_schema','sys')
ORDER BY CONSTRAINT_SCHEMA,TABLE_NAME,CONSTRAINT_NAME;
```

For every selected ordinary table, execute `SHOW CREATE TABLE <schema>.<table>`
using only the shared validated backtick quoting helper. For a view, use SHOW
CREATE VIEW and its corresponding metadata shape; never treat a view definition
as executable discovery input. The captured definition is input to DdlScanner,
not part of schema identity or an emitted migration. Normalize away neither SQL
identifier spelling nor default/generated expressions. Ignore current AUTO_INCREMENT
counter values; they are mutable data state, not structural identity attributes.

Construct models with this fixed order:

1. Build table/column maps, keeping zero-based dense column order from
   ORDINAL_POSITION-1. Resolve physical SQL identity from DATA_TYPE plus COLUMN_TYPE
   signedness and declared character/precision/scale/time facets. Keep charset and
   collation as qualified metadata. Unknown or unsupported types are unresolved,
   never guessed string/object bindings.
2. Detect AUTO_INCREMENT from EXTRA and declare identityByDefault with unavailable
   sequence attributes null. Detect STORED/VIRTUAL GENERATED and use the explicit
   generation expression. INVISIBLE is a separate hidden-column flag. Do not infer
   generated or identity columns from current row values.
3. Recover default presence from SHOW CREATE, because COLUMN_DEFAULT alone can
   conflate absence and NULL. DdlScanner uses Normal, quoted-string, backtick-name,
   comment and parenthesis-depth states; split table columns only at outer commas.
   Match the first decoded identifier to the known column, find a DEFAULT keyword
   outside quoted text and retain its expression span until the next top-level
   column modifier. The known terminating modifiers are NOT NULL, NULL, COLLATE,
   COMMENT, AUTO_INCREMENT, PRIMARY KEY, UNIQUE, REFERENCES, CHECK, GENERATED,
   VIRTUAL, STORED, INVISIBLE and ON UPDATE. Parenthesized expressions are retained
   whole. ON UPDATE column generation is outside schema v1 and produces
   ORMSCHEMA007 rather than being discarded or folded into its default.
   An unrecognized/ambiguous form fails ORMSCHEMA007 rather than guessing.
4. Schema discovery records the server's normalized effective definition, not the
   original authoring spelling: a nullable column normalized by SHOW CREATE to
   DEFAULT NULL has a default NULL. A nonnullable column lacking DEFAULT remains
   none. Keep default SQL string quoting; do not replace text `'NULL'` with NULL.
5. MySQL DATA_TYPE=json selects native JSON. MariaDB JSON aliases can be exposed as
   longtext plus JSON_VALID constraints: recognize the SHOW CREATE column/constraint
   structure and retain JSON intent only when established by that normalized
   metadata or an explicit type override. Ordinary longtext is never universally
   reclassified as JSON. If alias intent is irrecoverable, keep physical text and
   require a declared SchemaTypeBinding for JsonText.
6. Parse ENUM/SET label tokens only with the fixed quoted-token scanner and retain
   declaration order. Their physical identities remain distinct; unsupported CLR
   mapping is unresolved. Do not use Enum.Parse/GetValues. Partial/expression
   indexes are outside schema v1's unconditional column-key inventory and are not
   invented as ordinary keys.
7. Group keys/FKs by complete catalog/schema/table/constraint identity. Keep source
   order by ORDINAL_POSITION and target metadata from REFERENCED_* columns.
   POSITION_IN_UNIQUE_CONSTRAINT informs target-key association, not a reason to
   reorder the source columns. A missing target remains an acquisition error;
   a deliberately filtered target becomes an external target in the shared pass.
8. Capture the complete catalog twice, including SHOW CREATE definitions and the
   profile settings, and compare deterministic canonical pre-filter models. Any
   difference is ORMSCHEMA008 and no snapshot; do not retry automatically. This is
   a bounded change detector, not transactionally locked DDL isolation. Acquisition
   requires a stable schema; permission/DDL errors fail with safe context.
9. Apply SchemaSnapshotTransform.Apply exactly once for selection, external-FK/type
   closure, overrides and validation. Errors/null Snapshot throw
   SchemaValidationException; otherwise return its Snapshot. SchemaTool does not
   apply the transform again. Error mode rejects unresolved types with
   ORMSCHEMA007; explicit Record mode preserves them. The CLI owns atomic output
   replacement and exit codes; this adapter returns no partial successful model.

Primary metadata references are the official
[MySQL 8.4 COLUMNS](https://dev.mysql.com/doc/refman/8.4/en/information-schema-columns-table.html),
[TABLES](https://dev.mysql.com/doc/refman/8.4/en/information-schema-tables-table.html),
and [MySqlConnector conversion options](https://mysqlconnector.net/connection-options/).
Use the family-specific catalog fixtures to verify MariaDB fields/normalizations
rather than assuming matching column names imply equal semantics.

## Exact tests, server lanes and commands

Create `ProfileTests.cs`, `ScalarTests.cs`, `AdvancedTests.cs`, `LifetimeTests.cs`,
`CatalogTests.cs`, `DdlScannerTests.cs`, separate `mysql-fixture.sql` /
`mariadb-fixture.sql`, `NativeConsumer.csproj` and `check.py`.
Use the ORM-INTEGRATION users/departments plus composite keys, unsigned BIGINT,
DECIMAL(5,2), DATETIME(6), nullable DEFAULT NULL, absent default, generated stored/
virtual values, invisible column, JSON and enum `('sad','ok','happy')` fixtures.
Fixture setup explicitly configures its own session to the required modes/UTC;
the adapter must not do it secretly. No test touches unrelated databases/services.

| Case | Exact assertion on each admitted family |
| --- | --- |
| MY01 | p0/p1 physical order and repeated logical slot; zero/one/many values; typed NULL and apostrophe/backslash/NUL data remain values |
| MY02 | signed extrema and UInt64 18446744073709551615 round-trip; signed descriptor cannot read 9223372036854775808 through an unchecked cast |
| MY03 | Boolean 0/1 works; 2 fails; CHAR36 ordinary text stays text; UUID uses only declared conversion |
| MY04 | Decimal(5,2)999.99 passes;1000/1.001 fail; local/UTC microsecond exact values pass; wrong kind/offset/extra tick/zero dates fail |
| MY05 | JSON extracts17 and O'Reilly; SQL NULL vs JSON null vs JSON string null; MySQL/Maria storage distinction retained |
| MY06 | Caller transaction insert/savepoint/rollback-to/release/commit or rollback has exact fixture effects; session never owns that transaction |
| MY07 | Pre-cancel sends nothing; `SELECT id FROM users WHERE SLEEP(10)=0 ORDER BY id` with token250ms ends before5s in the bounded gate; a fresh query succeeds |
| MY08 | Same SQL timeout1 produces provider timeout and then connection reuse; standalone SLEEP return value is not used as an error oracle |
| MY09 | Early stream break cleans up and admits a fresh invocation; wrong transaction/profile/client settings fail before user SQL |
| MY10 | Catalog preserves composite order, unsigned/decimal/time facets, effective default NULL versus absence, generated/hidden/identity flags and separate family version |
| MY11 | Metadata pass mutation→ORMSCHEMA008; unresolved mapping→ORMSCHEMA007; denied catalog access never yields accepted partial output |
| MY12 | Maria nested byte guard succeeds exactly at budget and returns the prescribed error envelope one byte below; MySQL ordered-window JSON lane uses its distinct SQL |

```sh
python3 tests/Orm/Providers/MySql/check.py --profile mysql-8.4 --mode native --connection-env KORDA_TEST_MYSQL
python3 tests/Orm/Providers/MySql/check.py --profile mariadb-11.8 --mode native --connection-env KORDA_TEST_MARIADB
python3 tests/Orm/Providers/MySql/check.py --profile mysql-8.4 --mode managed --connection-env KORDA_TEST_MYSQL
python3 eng/ci/impact.py origin/main --output artifacts/orm-mysql-plan.json
```

Both native lanes are mandatory, use explicit environment-variable names instead
of command-line credentials, publish with warnings-as-errors and assert native
execution. Missing configured service is a configuration error, not a passing
skip. Register orm-mysql-provider with separate MySQL/MariaDB check nodes and its
actual prerequisites; an isolated leaf change does not select PostgreSQL/SQLite.
Stop after the specified transport/catalog/lifetime/declared-codec gates. Do not
add protocol code, retries, a scheduler, package publication or product cutover.
