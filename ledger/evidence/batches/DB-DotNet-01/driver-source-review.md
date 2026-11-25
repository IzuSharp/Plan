# Driver source review — research input, not execution acceptance

Observed upstream package pages on 2026-11-25 show [Npgsql 11.0.0](https://www.nuget.org/packages/Npgsql/11.0.0), [Microsoft.Data.Sqlite 11.0.0](https://www.nuget.org/packages/Microsoft.Data.Sqlite/11.0.0) and [Dapper.AOT 1.1.0](https://www.nuget.org/packages/Dapper.AOT/1.1.0). Resolve and hash the actual restored packages before product acceptance; both benchmark routes must use the same versions. The existing repository SDK remains a separately inspected input.

## SQLite in-flight cancellation

The EF Core `v11.0.0` tag resolves to `9e685c7a52d1a344d133a3d370e458db97417b3f`. In that exact [SqliteCommand.cs](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteCommand.cs), `ExecuteReaderAsync` checks the cancellation token before synchronously executing the command; `Cancel()` has an empty implementation. [Microsoft's async documentation](https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/async) also describes synchronous SQLite async methods. Upstream `main` source observed during research already contains interruption logic; its behavior must not be attributed to the published 11.0.0 package.

Therefore calling the driver async API or testing an already-cancelled token is insufficient. Investigate a .NET compatibility adapter using supported driver/native-dependency APIs, without adding Korda-owned C++/ABI/P/Invoke. Any cancellation registration must retain the exact active connection until it is removed and its callback joins; it must never interrupt a subsequent pooled lease. Recheck cancellation around admission and first execution so an interrupt made before SQLite starts does not disappear. Busy-retry waiting and reader stepping require separate tests from CPU-heavy execution. Do not dispose/return the connection merely because the caller stopped awaiting. These are design risks to resolve and execute, not an approved implementation or a measured guarantee.

The standard `Microsoft.Data.Sqlite` package declares `Microsoft.Data.Sqlite.Core`, `SQLitePCLRaw.bundle_e_sqlite3` and `SQLitePCLRaw.core` dependencies. Keep normal NuGet dependency deployment and verify the runtime engine version/loaded asset; do not ship Korda's old SQLite build beside it.

## Npgsql AOT and JSON

[Npgsql compatibility notes](https://www.npgsql.org/doc/compatibility.html) document Native AOT support with explicitly opt-in incompatible features. [JSON mapping](https://www.npgsql.org/doc/types/json.html) distinguishes raw JSON text from dynamic POCO mapping. Retain Korda's explicit source-generated `JsonTypeInfo<T>` serialization, use the correct PostgreSQL json/jsonb parameter type, and avoid enabling dynamic JSON/reflection as an implicit fallback. Static DTO mapping must read the .NET reader directly while preserving existing codec/nullability rules.

A driver exception or cancellation around COMMIT cannot by itself prove rollback. Preserve Korda's unknown-outcome state and validate a real lost-ack scenario against durable server state. Cleanup success is a separate fact from transaction outcome.

## Dapper.AOT activation and audit

The official [getting started](https://aot.dapperlib.dev/gettingstarted) and [generated-code](https://aot.dapperlib.dev/generatedcode) pages require an explicit DapperAot opt-in and SDK interceptor support; merely installing the package is insufficient. Use module/type/method opt-in at each measured call's scope, the appropriate `InterceptorsNamespaces` property and `EmitCompilerGeneratedFiles`. Retain generated interceptors, command factories and row factories; map every measured call-site to generated output and execute the actual published Linux x64 Native AOT program. The [FAQ](https://aot.dapperlib.dev/faq) notes that unintercepted calls remain ordinary Dapper; treat unsupported measured overloads or uninferred parameter shapes as missing coverage, never successful AOT comparison.

Dapper is used only in benchmark applications. Driver-only controls may diagnose allocations or SQL-plan differences but are not additional headline performance comparators.

## Released SQLite transaction and busy-retry details

The same fixed release's [SqliteConnection.cs](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteConnection.cs) maps `BeginTransaction(IsolationLevel.Serializable)` to a nondeferred transaction. [SqliteTransaction.cs](https://github.com/dotnet/efcore/blob/9e685c7a52d1a344d133a3d370e458db97417b3f/src/Microsoft.Data.Sqlite.Core/SqliteTransaction.cs) executes `BEGIN IMMEDIATE` for that selection and tracks external rollback with the standard SQLite dependency's rollback hook. Reuse this driver transaction rather than recreating a Korda-owned transaction handle. If the driver has already observed an automatic rollback after interruption, do not fabricate a secondary cleanup error; preserve any errors actually observed and verify durable database state.

Released `SqliteCommand.PrepareAndEnumerateStatements` and `SqliteDataReader.NextResult` retry BUSY/LOCKED with a 150 ms delay and compare elapsed time to `CommandTimeout` in whole seconds; zero means no timeout. Setting `sqlite3_busy_timeout` alone does not end those outer retries when it returns BUSY. The existing Korda whole-millisecond `BusyTimeout`, including zero as immediate rejection, therefore needs dedicated adapter behavior and actual contention tests. No claim that raw busy_timeout is sufficient has been accepted.
