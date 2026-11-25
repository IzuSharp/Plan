# DB-Perf-01 independent micro-ORM support probe

The two real Native AOT consumers passed. This is a minimum support check, not a
performance result, not a proof of complete workload support, and not an allocation
measurement. No Korda production source or GitHub ref was changed by this probe.

## Fixed inputs

- .NET SDK 11.0.100, Linux x64 Native AOT, actual runtime dynamic-code guard.
- Dapper 2.1.79, matching Dapper.AOT 1.1.0's upstream tested Dapper version.
- PostgreSQL: Npgsql 11.0.0 and real PostgreSQL server 18.0.
- SQLite: Microsoft.Data.Sqlite.Core 11.0.0,
  SQLitePCLRaw.provider.sqlite3 2.1.11, resolved SQLitePCLRaw.core 3.0.5.
- SQLite 3.51.3 source has the exact SHA-256 pinned by current Korda:
  `9512509b1bccb7461f79bea8aad6280ae4699e925fa4804381b71f59e7efb0c5`.
  This probe builds a separate shared library with Clang 23.1.5, `-O3 -DNDEBUG`,
  `SQLITE_THREADSAFE=1`, and `SQLITE_ENABLE_COLUMN_METADATA`.
  This does not assert equivalence of every compile option with Korda's static
  SQLite engine; freeze identical options before any performance comparison.

`package-downloads.json` records actual registry URLs, downloaded archive bytes and
SHA-256. Each project has a resolved `packages.lock.json`. The SDK's existing cache
was available as a fallback; Dapper and database provider packages were downloaded
for this probe. No Korda project reference or Korda package was used.

## Actual coverage

The public Dapper generic methods execute actual SQL, bind parameters, and use
generated DTO mapping. Each provider passes:

- create table, insert one row in a transaction and commit;
- `QuerySingleAsync<ProbeRow>` with typed `long`, `string`, nullable `string`, decimal;
- `QueryUnbufferedAsync<ProbeRow>` and complete result enumeration;
- update inside a transaction followed by rollback;
- `QuerySingle<ProbeRow>` checking the persisted original state after rollback;
- Unicode, NULL and exact decimal value `12.25` validation;
- table cleanup and connection disposal.

`generated-code.json` binds the emitted interceptors and package locks. The raw
publish logs show native code generation. Both processes reject execution when
`RuntimeFeature.IsDynamicCodeSupported` is true.

The `async_*` text in execution logs denotes asynchronous API spelling and
enumeration. It does **not** certify actual asynchronous suspension. In particular,
Microsoft.Data.Sqlite's ADO.NET async methods execute synchronously. This probe did
not measure concurrency, throughput, latency, GC, CPU, memory, native allocations,
network round trips, or lease retirement counters. JSON codecs, cancellation,
early enumeration termination and the complete business workload remain to be
validated before those paths can be reported as supported.

## Execution and recovery

`run_probe.py` records every command, working directory, start/end UTC, exit code,
raw output file and output SHA-256 in `commands.json`. All nine commands exited 0.
The dedicated disposable PostgreSQL cluster used TCP loopback with Unix sockets
disabled; it stopped successfully after the probe. The retained `pgdata` directory
belongs only to this probe. A fresh rerun should use a fresh probe output directory
or explicitly handle already initialized cluster and database files; blindly
rerunning the current driver is not idempotent.

Preserve the source files, package lockfiles, generated interceptors, raw logs and
receipts together. Binary hashes in `result.json` identify the actual measured
support executables; fresh builds are not promised byte-identical across paths.

## Source support and limitations

- Official Dapper.AOT release: https://github.com/DapperLib/DapperAOT/releases/tag/1.1.0
- Upstream classified API surface: https://github.com/DapperLib/DapperAOT/blob/1.1.0/test/Dapper.AOT.Test/ApiSurface.expected.txt
- Dapper.AOT setup: https://aot.dapperlib.dev/gettingstarted.html
- Npgsql AOT compatibility: https://www.npgsql.org/doc/compatibility.html
- SQLite custom library support: https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/custom-versions
- SQLite asynchronous behavior: https://learn.microsoft.com/en-us/dotnet/standard/data/sqlite/async

Dapper.AOT is a micro-ORM with real mapping, not merely an ADO.NET driver. It does
not provide a LINQ/Fluent query translator. Runtime SQL construction must be
included explicitly in dynamic-query comparison cells. Unsupported Dapper
overloads, especially `CommandDefinition`, multi-mapping and `QueryMultiple`, must
not be silently used as Native AOT equivalents. The tested generic methods are
intercepted; other call shapes require separate runtime proof.
