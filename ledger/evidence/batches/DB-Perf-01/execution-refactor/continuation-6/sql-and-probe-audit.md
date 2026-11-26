# DB-Exec-07: SQL parity and transaction probe source audit

This is a read-only source/evidence audit, not a new benchmark. Current product:
[public 8789a45](https://github.com/IzuSharp/Korda/tree/8789a45a52cc0cc0a0b62737542d9c120b753c9b),
local `d8beff6dc31f6190caaed333a28847511b7adbc5`, tree
`c8f398ae4db2d39302335a51a6378b737409f2fb`. The PostgreSQL conditional-probe
experiment `cd8bf3d36743509eb6a50a1701e9b497180beb46` is separate and unselected
at this audit cut. This audit grants no latency, allocation, 0 B, or long-run credit.

## New Dapper lifecycle contract

The historical `queries-v3.json` remains SHA-256
`76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2`.
Its original `independentOrmSql`, old consumers, and old results remain unchanged.
The old Dapper Find omitted Korda's qualification, aliases, formatting, and
`LIMIT 2`; historical equal DTO digests therefore did not establish equal SQL.

The new benchmark-only change is local `419ead22b54878c48544680ac828d1e2f2bb0e48`,
integrated as `4532354b4a316285b21b463f6ca6eda670dd7a49` and included in current
public source. It covers five lifecycle constants and the verification Find.

| Part | Current proof |
| --- | --- |
| PostgreSQL business SQL | Matched constants retain all Korda SQL bytes except `@name`; pinned Npgsql rewrites names in SQL occurrence order to the exact `$1…$N` SQL. |
| SQLite business SQL | Only ordinal `?` to unique `@name` is permitted. All other SQL text is identical; raw SQLite statement bytes are explicitly different. |
| Find inputs | `tenant = 1L`, `id` is `long`, `take = 2L`; all three actual generated parameters are `DbType.Int64`, bound to their same-named members. |
| Updates | Same note/version/key/expected-version values; String, nullable String and Int64 types checked in actual factories. |
| Consumption | Complete nine-field Order; original, changed and restored/persisted state checks and full digests remain. Same transaction is disposed before the final read on the retained connection. |
| ORM behavior | `[CacheCommand(false)]` for transaction cases remains. No artificial SELECT 1, Sync, query_only or extra round trip is added to Dapper. |

`matched` is a separate supplement and checker mode. `observed` still validates
the exact old SQL. Static checks passed 17 cases, including both retained
consumers, wrong/missing LIMIT, wrong parameter position/value/type, altered
cache policy and manifest bytes, and actual old generated factories lacking
the new limit. The 17 protected historic files rehashed unchanged.

Root subsequently built both new consumers in Release Native AOT. The actual
builder receipt is `dapper-matched-builds-01.json` (copied here); outer builder
exit codes are both zero. Each actual generated receipt resolves nine timed
lifecycle call sites plus three verification Find sites, `CommandFactory10`
for Find and `RowFactory3` for full Order materialization. Emitted source hashes:

| Provider | Actual generated source SHA-256 |
| --- | --- |
| SQLite | `daa2d91d5b4b27b133e60167c669cb117af3cadaf230238384b0db2eb1823cf1` |
| PostgreSQL | `26efaa4adc2140e39acc23a39d659b57c37879dc37dfaa65065b598c142a151c` |

This proves emitted source/type bindings and successful AOT publication, not a
runtime wire trace or a workload result. Consumers must reject any
`postValidationError` even if `build-receipt.exitCode` (dotnet's own code) is zero.

Pinned upstream text is retained under `upstream/` with fixed URLs and SHA-256:
Npgsql `4d174200ed48e3e3ab16419dbf84dd655da59de6`, Microsoft.Data.Sqlite
`9e685c7a52d1a344d133a3d370e458db97417b3f`. `SqlQueryParser.cs` 187–218 establishes
SQL occurrence order; `NpgsqlDbType.cs` maps Int64 to bigint/int8 and String to
text. `SqliteParameter.cs` 205–224 explains named lookup. The actual Dapper.AOT
package remains 1.1.0, source `0e071bf05e54caecfa98c885b075fa3e247f3ecc`.

## Provider transaction controls remain visible

Both cases retain one physical connection and the same business sequence:
BEGIN → original Find → update → changed Find → (restore for commit) →
commit/rollback → dispose transaction → persisted Find. PostgreSQL isolation is
ReadCommitted; SQLite Serializable selects the immediate transaction mode.

Control SQL and scheduling are driver-specific. Pinned Npgsql prepends
`BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED` and sends it with the next
command; Korda executes `BEGIN ISOLATION LEVEL READ COMMITTED READ WRITE`.
Microsoft.Data.Sqlite executes `BEGIN IMMEDIATE;`; Korda also establishes its
query_only policy. These are not relabeled as byte-identical business statements.

## PostgreSQL pre-COMMIT SELECT 1

Current [Transaction::finish_worker](https://github.com/IzuSharp/Korda/blob/8789a45a52cc0cc0a0b62737542d9c120b753c9b/native/cpp/src/host.cpp)
probes before COMMIT. If SELECT 1 reports SQLSTATE 25P02, it rolls back and Syncs,
then publishes known RolledBack. It does not inspect COMMIT's command tag.

The guarantee is real: PG18 `utility.c` changes a failed transaction's COMMIT
completion tag to ROLLBACK. Removing the probe using the existing Boolean
`in_transaction()` would conflate INTRANS and INERROR and could misreport a
failed transaction as committed. The existing real-provider
`timeout_rollback` fixture deliberately fails SQL through the physical
connection before requesting commit and asserts RolledBack.

PG18's `PQtransactionStatus` returns ACTIVE until libpq is protocol idle; when
idle it returns the state recorded by ReadyForQuery (`I`, `T`, `E`). A source-derived
conditional candidate can therefore skip only the normal probe when the
exclusive physical owner proves: healthy/non-null connection, nonblocking,
pipeline OFF, no live statement, exact PQTRANS_INTRANS, and no savepoints. The
separate local `cd8bf3d` experiment follows that narrow rule. Its helper holds
the existing physical lifetime mutex while inspecting libpq; Session admission
supplies exclusive protocol ownership. Other states retain the old probe and
SQLSTATE priority.

COMMIT's following Sync remains mandatory in this candidate. The first missing
or delayed post-COMMIT confirmation must preserve Unknown and truthful cleanup;
the source audit is not permission to infer outcome from a successful send.
Required existing risk coverage is failed commit/25P02, savepoint depth,
held/lost first post-COMMIT Sync, actual durable outcome and same-connection reuse.
No PG-probe performance benefit is claimed here.

Numbered local excerpts pin the actual PostgreSQL 18.0 archive, its member
hashes, and upstream commit `3d6a828938a5fa0444275d3d2f67b64ec3199eb7`.
Source excerpt selector attempts are retained separately. The first matched
both failed-COMMIT and failed-PREPARE tag sites (its provisional explanation
incorrectly called the second site explicit ROLLBACK); a generic COMMIT-case
anchor also matched dispatch/classification switches. The final selector uses
the exact inspected `!EndTransactionBlock` line. These were source-extraction
selector failures, not database/test failures.

## SQLite query_only

Current Transaction::begin establishes `query_only=ON/OFF`; read-only cleanup
restores OFF. Existing `sqlite_savepoints_and_query_only` and `read_only`
fixtures protect rejected writes and a succeeding writable transaction.

SQLite 3.51.3 implements query_only as a connection flag. Its pragma handler
can change that flag while preparing the PRAGMA, independently of autocommit.
Korda exposes raw SQL, and the present provider has no provenance-aware
query_only cache. Neither `sqlite3_get_autocommit` nor “last Korda transaction
was writable” proves the current flag. Microsoft.Data.Sqlite's ordinary
transaction implementation does not supply Korda's explicit ReadOnly contract.

Unconditional deletion is therefore unsupported by current proof. Any future
skip requires exact known-state tracking and raw-PRAGMA invalidation, including
prepare-time side effects and failure. It must retain read-only→write,
raw-ON→normal-begin, cancellation, cleanup and pooled reuse behavior. This audit
does not add those Korda control statements to Dapper.
