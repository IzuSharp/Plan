# EF Core JIT comparison client

Task: `DB-Runtime-Compare-01`. This is a local comparison client, not a Korda
product change and not a CI benchmark. The current owner request explicitly
authorizes .NET 11 JIT comparison despite older product instructions targeting
Native AOT only.

## Scope and admission status

One application source implements the existing 35 DB-Perf-01 business cases
against SQLite and PostgreSQL. Publish the same project with `UseSatoriGC=false`
for the Microsoft Workstation runtime or `UseSatoriGC=true` for the pinned Satori
runtime. The database provider is selected with `Provider=Sqlite` or
`Provider=PostgreSql`. No Dapper dependency or Dapper execution remains.

The owner's latest instruction accepts a **192 MiB GC configuration budget for
C# clients without cgroup enforcement**. This replaces the earlier 128 MiB
admission policy; it does not turn the setting into an enforced process-memory
cap. The project records `System.GC.HeapHardLimit=201326592` in runtimeconfig,
and the finite runs additionally used `DOTNET_GCHeapHardLimit=0xC000000`.
Startup requires the actual GC configuration to report that value.

The executable keeps `ClientMemoryBudgetEnforced=false` and
`GcHeapBudgetEnforcementProven=false`, and records
`OwnerAcceptedUnenforcedMemoryPolicy=true`. Requested/configured GC budget,
`GcTotalAvailableMemoryBytesAtStartup`, and process RSS/peak RSS are separate
fields. Satori's available-memory value remains the host amount in the observed
attempt03 run even though its configuration reports 192 MiB. Actual excess
memory must be reported, not rejected or hidden as though a hard cap existed.

The previous rejection of 1,800-second runs solely for lacking a cgroup has
been removed under this explicit owner authorization. `TimingComparisonEligible`
now means the runtime/configuration identity matches the accepted policy, the
business/oracle checks have no failures, connections were returned, and the run
is neither allocation-instrumented nor an empty-driver diagnostic. It does not
certify a completed 30-minute duration. The external formal runner must check
the duration, frozen identities, database conditions and complete outcomes.

## Current bounded validation result

All four provider/runtime combinations were republished with the requested
`<Features>$(Features);runtime-async=on</Features>` and passed the limited
`attempt03` correctness run under the accepted 192 MiB configuration policy. Each run verified every business case, executed
64 warmup operations, then completed one operation for each of the 35 cases,
with zero failed operations, zero oracle failures, four successful independent
connection checks for the write cases, and zero remaining application-owned
connections. SQLite was 3.51.3; PostgreSQL was 18.0. PostgreSQL used a separate
`db_perf_efcore_preflight03` database cloned from the canonical seed; the server
was stopped successfully after the two sequential checks.

| Provider | Actual runtime | GC identity | Runtime Async methods in application | Finite 35-case check |
| --- | --- | --- | --- | --- |
| SQLite | .NET 11.0.0 | Workstation; `IsServerGC=false`, no Satori marker | 19 | Passed |
| SQLite | .NET 11.0.2-ci | `SatoriGC=true`; actual `IsServerGC=true` | 19 | Passed |
| PostgreSQL | .NET 11.0.0 | Workstation; `IsServerGC=false`, no Satori marker | 19 | Passed |
| PostgreSQL | .NET 11.0.2-ci | `SatoriGC=true`; actual `IsServerGC=true` | 19 | Passed |

`verification/attempt03-summary.json` links the complete receipts by SHA-256 and
records source, lock-file, apphost, DLL, PDB, runtimeconfig, dependency-manifest,
loaded CoreCLR/JIT and native SQLite identities. Each compiler argument receipt
contains the actual `/features:runtime-async=on` option. Startup reads the
evaluated feature property from generated assembly metadata and checks actual
`MethodImplAttributes.Async` method flags in the loaded application. This proves
more than the presence of XML text: the feature was emitted and those binaries
executed the 35 business cases on both runtime builds. The check does not claim
that prebuilt EF/driver dependencies were recompiled with this feature.

These are bounded correctness results, not 30-minute performance acceptance.
In attempt03, both stock runs report GC total available memory of 201,326,592 B;
both Satori runs report 10,451,427,328 B. All four report a configured GC heap
limit of 201,326,592 B. This difference is preserved in each runtime identity.

Historical evidence is immutable: `verification/admission-attempt02.json` still
records the earlier 128 MiB policy's rejection checks; that policy is superseded
for new runs. `verification/attempt02-source.zip`, its four published binaries,
and its original receipts remain separate from attempt03. The earlier SQLite
`attempt01` receipts, `verification/pre-runtime-async-source.zip`, and all 128 MiB
memory probes also retain their original identities. No old receipt has been
relabeled as a 192 MiB run.

## Fixed dependencies

| Component | Version |
| --- | --- |
| .NET SDK | 11.0.100 |
| Microsoft stock runtime | 11.0.0 |
| Microsoft.EntityFrameworkCore | 11.0.0 |
| SQLite EF/provider packages | 11.0.0 |
| Npgsql EF/provider packages | 11.0.0 |
| SQLitePCLRaw.provider.sqlite3 | 3.0.5 |
| PublishWithSatoriGC | 11.0.2-satori.45942668844.1 |

Each provider/GC combination has its own NuGet lock file under `locks/`.
The Satori package replaces runtime assets including CoreCLR and the JIT, so this
comparison cannot attribute every observed difference solely to the collector.
Actual loaded runtime images and SHA-256 values, managed assembly SHA-256,
`RuntimeFeature.IsDynamicCodeSupported`, `IsDynamicCodeCompiled`,
`GCSettings.IsServerGC`, and every `GC.GetConfigurationVariables()` entry are
recorded before the measurement boundary. Satori is identified by the actual
`SatoriGC=true` configuration entry; its `IsServerGC` may be true even with the
project's server-GC property disabled.

## Build

Use the .NET installation pinned by `global.json`. Example commands, run from
this directory:

```sh
dotnet publish DbPerf.EfCore.csproj -c Release -r linux-x64 \
  --self-contained true --disable-build-servers -m:1 \
  -p:Provider=Sqlite -p:UseSatoriGC=false \
  -o bin/publish/sqlite-workstation-attempt03

dotnet publish DbPerf.EfCore.csproj -c Release -r linux-x64 \
  --self-contained true --disable-build-servers -m:1 \
  -p:Provider=Sqlite -p:UseSatoriGC=true \
  -o bin/publish/sqlite-satori-attempt03
```

Use `Provider=PostgreSql` and distinct output directories for PostgreSQL. Publish
sequentially when sharing this project's `obj/` directory. After lock files have
been reviewed, `-p:RestoreLockedMode=true` makes subsequent restores fail on an
unexpected dependency change. Execute the published apphost, not an unrelated
system `dotnet` executable. `PublishAot` and `PublishReadyToRun` remain false.

## Query and materialization choices

Prepared mode reuses an `IQueryable` expression graph per worker and allows
EF Core's ordinary query cache to reuse translations/materializers. This is not
`EF.CompileQuery`, a cached SQL-only wrapper, or an explicit server-prepared
statement claim. Dynamic mode reconstructs the equivalent expression graph per
operation; normal EF query caching still applies. The reusable full-order
projection is an explicitly shared expression. Queries use `AsNoTracking` and
typed scalar/DTO projections. A worker owns one `DbContext`; it is never used
concurrently. Per-operation session mode constructs a context for the newly
opened provider connection.

Most queries stream with `AsAsyncEnumerable` through the unchanged shared
`ReadStream` digest consumer. Related rows intentionally buffer, matching the
original related-results contract. Settings are mapped with an EF value
converter to the typed `OrderSettings(Channel, Gift)` record. SQLite keeps money
as integer cents in the database and aggregates integers before an exact final
decimal conversion; PostgreSQL uses `numeric(18,2)`. No floating point money or
opaque JSON-string digest substitutes for the typed business result.

### Explicit SQL exceptions

| Business case | Execution | Reason |
| --- | --- | --- |
| `window` | Parameterized `Database.SqlQuery<RankRow>` | Preserve the existing `ROW_NUMBER` partition/order expression; EF's general public LINQ window API remains an open upstream issue. |
| `running-total` | Parameterized `Database.SqlQuery<RunningRow>` | Preserve the ordered unbounded-preceding/current-row SUM window. |
| `raw-sql` | Parameterized `Database.SqlQuery<TextRow>` | The original business case explicitly tests raw SQL. |

The remaining 32 cases use Fluent IQueryable/EF transaction APIs. The two
window exceptions are declared exceptions, not described as Fluent support.
They still use EF's typed materialization and parameter binding. The upstream
window API issue was checked as open/backlog on 2026-11-28 UTC:
<https://github.com/dotnet/efcore/issues/12747>.

### Allowed equivalent SQL changes

| Business case | Difference | Preserved contract |
| --- | --- | --- |
| `cte` | Fluent filtered derived query rather than named nonrecursive CTE | Same tenant, predicate, sorted IDs and limit; the source CTE has no required materialization boundary. |
| `related` | One indexed range query for the fixed contiguous parent keys instead of one UNION branch per parent | Same parents 1..N, one SQL execution, identical child columns, parent grouping, empty parents and ascending child IDs. This optimization is only for this fixed workload's known contiguous input keys. |
| `empty-sum` | Grouped SUM and nullable scalar default when there is no group | Returns one business scalar with NULL, not EF SumAsync's default zero. |
| `customer-totals` | Boolean null discriminator plus key ordering | NULL customer group last. |
| `nullable-order` | Boolean null discriminator plus key and ID ordering | NULL customer IDs first, as required by the actual manifest. |

Early stopping requests the full Order projection with
`Take(OrdersPerTenant)` (1024 in the frozen workload), consumes three rows and
disposes the enumerator. It never rewrites the query to `LIMIT 3` or returns a
narrow numeric DTO.

The four write cases target tenant 1 / the configured last order (1024 in the
frozen workload). They issue real updates, verify the full DTO including omitted
fields/NULL/version, restore or roll back, await transaction disposal and read
the full persisted order. Optimistic conflict is an affected-row check on the
stale version predicate. `--verify` additionally reads each restored write
target through an independent connection **before timing**; no extra check is
inserted into the historical steady operation count.

## Shared measurement and oracle

The arrival scheduler, bounded FIFO admission, digest, sticky correctness oracle,
reader cleanup and native-allocation-profile helper are copied from the fixed
Korda worktree. `source-provenance.json` identifies each original file and its
SHA-256. Measurement and options are adapted for EF/JIT metadata. Process-wide
allocation/CPU/GC totals still include driver, DTO and harness costs. Native
allocation profiling remains a separate explicit instrumented process; no
framework-only allocation attribution is invented.

GC pause totals come from the runtime's cumulative GC API. Satori includes
thread-local collection behavior, so this duration is retained as a runtime
counter and is not asserted to equal global application stop time or the stock
GC's accounting. Runtime evidence and startup hashing are outside timing.

Schema initialization remains in the canonical existing initializer. This client
rejects `--initialize`, historical `--lifecycle-checks`, and `--recovery-checks`
rather than pretending those separate diagnostic suites were ported. All 35
business cases and their transaction/early-stop semantics are implemented.

## Bounded correctness invocation

Copy the canonical seed to a dedicated SQLite file first. The exact original
SQLite library must be passed with `--native-library`; its mapped path and hash
are checked. PostgreSQL uses a dedicated preflight database on the prepared
server; no server memory setting is changed.

```sh
DOTNET_GCHeapHardLimit=0xC000000 bin/publish/sqlite-workstation-attempt03/DbPerf.EfCore \
  --connection /absolute/path/to/preflight-copy.sqlite \
  --native-library /absolute/path/to/matching/libsqlite3.so \
  --case mixed --mode prepared --session persistent \
  --concurrency 1 --warmup 64 --operations 35 --verify --idle-seconds 0 \
  --output /absolute/path/to/unique-preflight-result.json
```

This performs the 35-case verification sweep, 64 warmup operations and 35
bounded measured operations. Those short timing fields are diagnostic bookkeeping
only. Keep all failed attempts, build logs and observed receipts; do not relabel
them as 30-minute runs. The stdout startup record explicitly exposes the runtime
and owner-accepted configuration-only memory policy, including the absence of an enforced client memory cap.
