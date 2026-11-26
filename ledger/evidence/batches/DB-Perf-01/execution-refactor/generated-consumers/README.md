# Actual generated Dapper.AOT consumers

These are the generated sources retained by the successful external Native AOT builds in [build-recovery.json](../build-recovery.json). Their complete generated-source, restore graph and original build receipt hashes are in [manifest.json](manifest.json). They describe the 35-case workload and lifecycle PK query, not the separate later same-SQL two-column phase consumer.

| Query | PostgreSQL generated path | SQLite generated path | Parameter and row behavior |
| --- | --- | --- | --- |
| Composite PK, nine-field `Order` | `QuerySingleAsync45` → `CommandFactory10.Instance` | `QuerySingleAsync47` → the same factory shape | Two `DbType.Int64` values at ordinals 0 and 1; no `[CacheCommand]` at this call site; `RowFactory3` |
| Ordered 100/1,000 DTOs, workload wide case | `QueryUnbufferedAsync4` → `CommandFactory0.Instance4` | Same named generated path | Two Int64 values (`Tenant`, `Rows`); generated command caching at the fixed call site; `RowFactory3` |
| Simple text DTO | `RowFactory0` | `RowFactory0` | Column names/types are tokenized once, then typed `GetInt64`, nullable `GetString`, and direct constructor |

`RowFactory3.Tokenize` matches the nine real names and database types once and prepares decimal/JSON handler tokens. `Read` uses the resulting ordinal/type tokens and directly constructs `Order`. The generated cached factory reuses managed `DbCommand`/parameter objects; it does not imply physical PostgreSQL server statement caching. The PK factory differs and must not be described as sharing that cache policy.

The actual restored versions are Dapper 2.1.100, Dapper.AOT 1.1.0, and Npgsql 11.0.0 or Microsoft.Data.Sqlite.Core 11.0.0 plus SQLitePCLRaw 3.0.5. The SDK/runtime are 11.0.100/11.0.0. Older campaign locks and upstream generated fixtures are separate evidence.

The original build receipts are retained unmodified. The supplemental package binding in `build-recovery.json` distinguishes a signed NuGet package content hash from the full archive hash and includes the Microsoft.Data.Sqlite.Core archive omitted by the original receipt collector; no changed package bytes or repaired measurement are implied.
