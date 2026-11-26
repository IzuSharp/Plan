# Generated mapper and result List allocation diagnostics

This is an explicit local Linux x64 diagnostic for the ordinary external
`query-phases` consumers. It supports the three Korda routes and the Dapper.AOT
consumer, with their existing 1, 100 and 1,000 row queries, parameters, connection
settings, full result Lists and field/NULL/order oracles.

`build.py` builds a separate Native AOT executable. It never runs that executable.
No product source, package, native image, ordinary consumer, CI action or default
test is changed. The original consumer remains the input for latency, throughput,
CPU, RSS and uninstrumented allocation measurements.

## What is observed

The overlay records the original whole-process `GC.GetTotalAllocatedBytes(true)`
window and the original process-wide GC collection deltas. It also records three
non-overlapping synchronous scopes:

| Scope | Actual code observed | Included allocations |
| --- | --- | --- |
| Generated mapper | Korda's generated `PhaseRows.Row` and `PhaseRows.Bind` reader bodies, or Dapper.AOT's generated `RowFactory<PhaseRow>.Read` body | DTO construction, string/field reads, and any codec or driver scratch allocated inside that generated body |
| List constructor | The original `new List<PhaseRow>(resultRows)` call | The List and its original backing array |
| List Add | The original first-row and remaining-row `List.Add` calls | Any allocation performed by those actual Add calls |

Each scope uses current-thread allocation counters around a synchronous body.
It checks that the body did not change managed thread. The sums are accumulated
with integer interlocked operations. First execution and warmup calls are outside
the reported deltas. Every completed window must observe exactly one List
constructor per operation and exactly `operations × resultRows` mapper calls and
List additions. The existing query oracle must still consume and check every row.

These are **observed allocation scopes**, including scratch allocations. They are
not estimates of the size of live DTO objects. `FrameworkOnlyBytes` stays `null`;
the tool does not subtract them from a separately instrumented process total and
does not claim that the remainder is the framework's production allocation.

The ordinary phase receipt is retained and explicitly prefixed with
`ALLOCATION-INSTRUMENTED; TimingCredit=false`. A separate
`<phase-receipt>.allocation.json` contains raw process and scope measurements,
the original phase receipt hash, executable hash and build-provenance hash.
Its `TimingCredit` is always `false`. Instrumented timings must not be mixed with
ordinary phase results. A failing process retains the original failure receipt
and additionally attempts an `.allocation.failure.json` report with completed
windows and the incomplete window's observed counts.

## Build an isolated overlay

Start with a successful ordinary consumer produced by
`benchmarks/db-perf/managed/build.py --kind query-phases` or
`benchmarks/db-perf/managed/build_orm.py --kind query-phases`. Both consumers must
still have their source files, successful `build-receipt.json`, asset graph and
the restored package archives.

```sh
python3 benchmarks/db-perf/allocation-diagnostics/build.py \
  --consumer /absolute/ordinary-korda-consumer \
  --output /absolute/new-korda-allocation-consumer

python3 benchmarks/db-perf/allocation-diagnostics/build.py \
  --consumer /absolute/ordinary-dapper-consumer \
  --output /absolute/new-dapper-allocation-consumer
```

Use the task's locked .NET 11 SDK and native toolchain environment. The output
must be fresh and outside source worktrees and input consumer directories.
Each failed build keeps its directory, logs and failure receipt; retry with a new
output path. The tool fixes MSBuild to one process and disables shared compilation.

The builder checks the original source/project/asset hashes. It constructs a
local-only NuGet feed from the exact package archives already used by that
consumer, checks the original NuGet content hashes and available archive hashes,
and records every archive SHA-256. It does not fetch replacement packages. The
resolved dependency graph must equal the original graph.

The first compilation runs the real source generators against the overlay's
source files. This regenerates Dapper interceptor locations after the List/window
edits. It then preserves every generated source file, patches only the actual
generated mapper bodies and publishes with those captured sources and no second
generator execution. SQL, parameter writing, column tokenization, command
factories and generated row-read expressions stay intact. Guarded source anchors
make an incompatible consumer or generator version fail explicitly.

`allocation-build-receipt.json` binds the original build receipt, package archives,
tool and observer source, patched consumer source, original and instrumented
generated sources, mapper patch, complete commands/logs and resulting AOT binary.
For Korda, every shipped native image must retain the ordinary consumer's exact
hash. `generated-mapper.patch` makes the inserted measurement scopes reviewable.

## Explicit diagnostic execution

Execute these only in a separate local diagnostic window, after all builds and
correctness runs have stopped. The builder does not perform this step. The
original argument formats are unchanged, so the same database setup, row count,
iteration count, SQL contract receipt and exact SQLite native library can be
passed to ordinary and diagnostic consumers.

```sh
# Existing Korda query-phases argument format; initialize a fresh diagnostic DB.
/absolute/new-korda-allocation-consumer/out/DbPerf.QueryPhases \
  /absolute/diagnostic.db /absolute/korda-allocation-100.json \
  256 3 initialize --rows 100

# Use the existing DapperQueryPhases options and the matching Korda SQL receipt.
/absolute/new-dapper-allocation-consumer/out/DbPerf.DapperQueryPhases \
  --connection /absolute/diagnostic.db \
  --output /absolute/dapper-allocation-100.json \
  --korda-receipt /absolute/korda-allocation-100.json \
  --rows 100 --iterations 256 --windows 3 \
  --native-library /absolute/locked/libsqlite3.so
```

Use the consumer's documented PostgreSQL arguments for that provider. Its
connection and transaction semantics are unchanged by this overlay. Use the same
procedure for before and candidate consumers; a new package/version always needs
a new ordinary consumer and a new diagnostic overlay. Compilation proves that
the generated-source instrument is buildable. It does not establish allocation
results, timing improvements, offered-load calibration or long-run acceptance.
