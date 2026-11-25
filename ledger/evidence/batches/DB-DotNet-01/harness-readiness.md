# Managed harness recovery and adaptation

## Exact source location

The product commit [`da153c22ef1093fccc3233ec76bfda96e6cc59df`](https://github.com/IzuSharp/Korda/tree/da153c22ef1093fccc3233ec76bfda96e6cc59df/benchmarks/db-perf) is present in the full product clone. It contains the later published managed harness and the immutable `benchmarks/db-perf/reproduction-inputs/by-sha256/` archive. Current main intentionally has no `benchmarks/db-perf` directory. Do not silently restore that whole old tree, including its C++ comparator and native allocation hooks, into the current product.

The Plan `DB-Perf-01/checkpoints/managed-final-v1/applications/{korda-sqlite,korda-postgresql,dapper-sqlite,dapper-postgresql}/*.source-reference.json` records have pending commit fields from their original publication checkpoint. Their 56 entries, representing 27 unique contents, were actually matched by size and SHA-256 against the archive in the product commit above. The original local Plan recovery commit `b279f426...` and its original blobs are not present in the current full Plan clone; no dependency on that lost local state is required. Historical record bytes remain unchanged.

A reproducible read-only extraction is:

```bash
git -C /absolute/Korda show \
  da153c22ef1093fccc3233ec76bfda96e6cc59df:benchmarks/db-perf/managed/Shared/OfferedLoad.cs
```

For an exact historical variant, take `source.path`, `source.sha256` and `source.bytes` from its Plan source-reference record, read that path at the fixed product commit, and verify both identity fields before using it. The active managed files at that commit can differ from earlier archived variants; do not relabel one as the other.

## What can be carried forward

| Fixed product path | Useful behavior | Required adaptation for this batch |
| --- | --- | --- |
| `benchmarks/db-perf/managed/Korda/{Workload,AdvancedCases,Dataset,Models}.cs` | Formal public Fluent construction, prepared queries, deterministic dataset and complete row digests | Build against the frozen first compatible .NET packages; confirm SQL/results against both existing and new oracles |
| `benchmarks/db-perf/managed/Dapper/{Workload,Contracts.generated,Models,Oracles}.cs` | Thirty read operations, typed decimal/JSON handlers, module DapperAot opt-in and independent seed formulas | Audit every emitted interceptor/row factory/parameter factory against the current build; add exactly-100-DTO list and missing current matrix cases |
| `benchmarks/db-perf/managed/{Korda,Dapper}/LifecycleCases.cs` | Five lifecycle cases: commit, rollback, partial NULL update, stale conflict and early stop | Preserve actual transaction semantics and isolate expected conflict counts; remove native ownership dependencies |
| `benchmarks/db-perf/managed/Shared/ReadStream.cs` | Full result consumption, deterministic digest and retention of read/cleanup failures | Keep matched consumption/results on both routes; report the intentionally partial early-stop case separately |
| `benchmarks/db-perf/managed/Shared/OfferedLoad.cs` | Common arrival clock, bounded FIFO, explicit rejection, per-second offered/started/success/failure counts and latency from planned start | Revalidate the scheduler in AOT, preserve queue-inclusive latency, match worker/pool limits and select sustainable load under common tail/error constraints |
| `benchmarks/db-perf/managed/{Korda,Dapper}/Measurement.cs` | Whole-process allocated-byte start/end, process Gen 0/1/2, CPU/RSS and timed raw count recording | Replace native ownership/allocation machinery; add the current attribution categories and ensure raw start/end counters are retained |
| `benchmarks/db-perf/workload/{queries-v3,queries-v2,lifecycle-v1}.json` | Thirty reads plus five explicit lifecycle business contracts | Input material only; rebind to current 31-case matrix and newly verified SQL, plans, types, field counts and row counts |

The old Dapper project uses Dapper 2.1.100, Dapper.AOT 1.1.0 and Npgsql 11.0.0. Its SQLite route instead uses `Microsoft.Data.Sqlite.Core` 11.0.0 with `SQLitePCLRaw.provider.sqlite3` 3.0.5 and an explicit library resolver. That deployment must change to the same standard `Microsoft.Data.Sqlite` dependency closure as Korda. Re-record the actually loaded SQLite engine identity, version and compile options. The old custom SQLite library cannot serve as the new shared-engine baseline.

The old managed suite has `[module: DapperAot]`, explicit type handlers, `InterceptorsNamespaces` and `EmitCompilerGeneratedFiles`; those source settings alone do not prove generated code is used. Preserve generated output and compiler diagnostics from the new build, map each measured overload/call-site to its interceptor, and reject any measured fallback to ordinary Dapper. Current business results must use identical CLR types on both routes, including DTO/list/string costs.

## Evidence boundaries and remaining work

The current protocol in [workloads.md](workloads.md) and [workload-cases.json](workload-cases.json) controls the new campaign. The previous eight-cell campaign, C++ routes, previous package versions, old GC/allocation values and all retained old duration counters remain history. They contribute zero duration to the four required new 1,800-second effective segments.

Before any headline comparison, both new routes must pass current real-database correctness and their ordinary external PackageReference AOT builds. Freeze the first compatible Korda .NET packages before measured optimization. Raw E2E allocation includes business DTO/list/string objects. Library-extra, business-result, driver/runtime and unresolved harness bytes require supported attribution; unseparated residuals remain explicit. No subtraction can justify a zero-byte claim without compatible raw counts and an attribution method.

A short before/after control must precede each optimization, with interleaved repetitions and unchanged business semantics. Dedicated long measurements run only after package freeze and environment admission, one route/database segment at a time. Warmup and calibration are outside each continuous effective interval; endpoint artifacts, original counts and reproducible commands are mandatory.
