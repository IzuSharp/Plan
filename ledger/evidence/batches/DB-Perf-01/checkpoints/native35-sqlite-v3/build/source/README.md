# Direct native database comparator

This C++20 Linux x64 consumer implements the shared contracts in
[`../workload/queries-v3.json`](../workload/queries-v3.json): thirty Fluent,
handwritten-SQL and related-batch reads plus commit, rollback, partial update,
stale optimistic conflict and early read termination. The read-only v1 and v2
manifests remain supported. Every operation consumes the specified logical
results, validates the shared FNV-1a digest, drains the protocol and releases or
resets statements. Query support alone does not establish active cancellation,
same-process saturation recovery or long-run acceptance.

## Build and input identity

Use Korda's installed, pinned Clang toolchain and dependency sources. The build
validates the compiler executable, SQLite amalgamation, nlohmann headers and
patched PostgreSQL client provenance against `native/dependencies.lock.json`.
It uses the same SQLite feature definitions as the product and links the exact
patched static libpq archives. C++ uses the toolchain's static libc++ and
libc++abi. OpenSSL, libc and other system libraries remain system dependencies.

```sh
python3 benchmarks/db-perf/native/build.py \
  --sqlite-source artifacts/dependencies/sqlite/sqlite-amalgamation-3510300 \
  --json-source artifacts/dependencies/nlohmann-json/json \
  --postgres-prefix artifacts/postgres-tools/install \
  --output artifacts/db-perf/native-v1
```

Use a new output directory for each build. `build-receipt.json` preserves the
input hashes, source hashes, compiler invocation, exit status, build logs and
executable/library hashes. The executable resolves its adjacent `libsqlite3.so`
with `$ORIGIN`. Its result records the actually loaded SQLite path and hash,
executable hash, query-manifest hash and build-receipt hash. It never initializes
or replaces the database; initialize the shared dataset with the managed
consumer first.

When only the comparator source changes, `--reuse-sqlite-build <prior-output>`
can reuse a previously built SQLite library. The builder rechecks its receipt,
compiler, source hashes, feature definitions, dependency lock and actual library
hash before copying it into the new output. The new receipt records the reuse;
the earlier build and evidence remain unchanged.

## Comparable construction and preparation modes

Query construction and physical statement preparation are independent:

| Option | Work inside each measured operation |
| --- | --- |
| `--mode dynamic --physical-prepare per-operation` | Construct SQL from the projection, prepare the physical statement, bind, execute, materialize, validate and release. |
| `--mode prepared --physical-prepare per-operation` | Reuse the SQL shape; prepare the physical statement, bind, execute, materialize, validate and release. This matches the current Korda compiled-plan reuse boundary. |
| `--mode prepared --physical-prepare reuse` | Reuse each warmed physical statement on its connection; bind, execute, materialize, validate and reset. Report as an additional layer. |

`--physical-prepare` defaults to `per-operation`. A cached native physical
statement is not described as equivalent to Korda's compiled query-shape cache.
The native cache has one slot per declared read or transaction SQL leg per
connection and is released when the connection closes. Its finite slot bound is
reported. Dynamic construction with physical reuse is rejected.

The five core dynamic projections construct their clauses from column metadata.
Advanced dynamic queries assemble SQL identifiers, parameter placeholders and
literal syntax from the shared manifest's token recipe. Prepared mode reuses the
assembled text. This measures direct SQL text construction; Korda also constructs
its Fluent query graph. The related-batch public API has no prepared overload, so
its direct counterpart rebuilds the SQL text in both modes while reusing only
the immutable parent-key inputs.

The transaction CRUD APIs also lack prepared overloads. Their SQL is constructed
in both modes; the physical-preparation option remains a distinct driver layer.
For a direct-native primary comparison, select physical reuse plus `drain-only`
for prepared reads and per-operation preparation plus `drain-only` for dynamic
reads. Retain the product-confirmation variants as separate controls for the
cost of Korda's current protocol shape; do not silently impose that cost on the
direct-native primary column.

PostgreSQL defaults to `--protocol-confirmation product`. Each operation uses
the product's explicit pre-execution and retirement pipeline `Sync`
confirmations, and the result records them separately. `drain-only` is an
additional layer that drains ordinary libpq results and checks transaction idle
without these extra confirmation commands.

| Physical preparation | Confirmation | Warm measured PostgreSQL submissions per query |
| --- | --- | ---: |
| Per operation | Product | 5: prepare, describe, confirmation Sync, execute, retirement Sync |
| Reuse | Product | 3: confirmation Sync, execute, retirement Sync |
| Per operation | Drain only | 3: prepare, describe, execute |
| Reuse | Drain only | 1: execute |

The table describes one read SQL statement. Transaction operations execute
multiple SQL legs and report their actual aggregate submissions. These are
protocol submission counts. `poll` wakeups and submissions are not
physical network round-trip measurements. SQLite reports zero network protocol
submissions and separately counts physical preparations and SQL executions.

## Execution

Run against the same initialized, indexed database and manifest as the managed
consumer. This example performs a short correctness probe; its timings do not
establish a production comparison:

```sh
artifacts/db-perf/native-v1/db-perf-native \
  --provider sqlite --connection /absolute/path/db-perf-v1.sqlite \
  --manifest benchmarks/db-perf/workload/queries-v3.json \
  --case mixed --mode prepared --physical-prepare per-operation \
  --verify --warmup 5 --operations 10 --idle-seconds 0 \
  --output /absolute/path/native-correctness.json
```

For PostgreSQL, use `--provider postgresql` and the local PostgreSQL connection
URI. `../run.py` can launch PostgreSQL and the consumer under the same parent,
preserve its configuration and sample client/server resources separately.
The client explicitly disables TLS for this local dedicated database, uses
UTF-8 and a 30-second statement timeout. SQLite uses WAL, FULL durability,
foreign keys, private cache, full mutex and a five-second busy timeout. Neither
route adds an explicit transaction around ordinary individual read statements.
Write cases use PostgreSQL READ COMMITTED / READ WRITE or SQLite BEGIN IMMEDIATE.

Use `--cases numeric,text,money,json,wide` together with `--case mixed` to freeze
an explicit ordered common mix. The default mix consists of all cases in the
selected manifest; consumers with different supported sets must not silently
use different default mixes. `declaredCaseIds`, `executedCaseIds` and per-case
started/succeeded/failed/row counts preserve the actual measured coverage.

`--explain` records a diagnostic plan for every selected case, before warmup,
using the exact SQL and parameter types/values. For transaction cases this is
the initial full-order lookup only; the complete executed leg list appears in
`transactionSqlSteps`. PostgreSQL uses `EXPLAIN (FORMAT
JSON, ANALYZE FALSE)`; SQLite uses `EXPLAIN QUERY PLAN`. This does not assert that
a later reused PostgreSQL statement chooses the same custom/generic plan.

The supported session mode is `persistent`, one connection per worker.
`--concurrency` is bounded to 1–256. `--operations N` sets a finite total across
workers; `--seconds N` runs a finite closed-loop duration. Each worker selects
the selected mixed cases in the same fixed order. Warmup and the optional idle
observations are outside the measured interval. All connections are drained and
closed before the final ownership counters are reported. A failed operation
ends that worker without retrying an unverified protocol state; planned,
started, failed and unstarted operations remain visible.

## Fixed offered load

Add `--rate R --seconds S --queue-capacity Q` to select deterministic offered
load. `--arrival-rate` is an alias for `--rate`. The planned count is exactly
`ceil(R * S)`, and operation `i` is due at `start + i/R`. One producer waits for
these absolute deadlines, attempts every planned arrival, and places accepted
jobs in a bounded FIFO ring. A full queue rejects immediately; a delayed
producer still attempts its overdue arrivals and their planned timestamps are
preserved. Queue capacity defaults to four times concurrency and is bounded to
65,536. Queue storage, worker histograms and time-series arrays exist before the
measurement starts.

Workers select the query by the global arrival index, consume all accepted jobs
and validate their results. The producer waits through the configured offered
deadline, closes arrivals and lets accepted work drain. The receipt includes the
planned deadline, actual offered end and final drain timestamps separately.
All planned, attempted, sent, started, succeeded, failed and rejected counts must
reconcile. No retries are hidden. After a failed operation leaves protocol reuse
unproven, that worker reports subsequent accepted jobs as failures instead of
silently dropping or retrying them.

The `offeredLoad` object contains four raw histograms: successful service time,
successful planned-arrival-to-completion latency, all completed response times
including failures, and planned-arrival-to-actual-start delay. Rejections have
their own counts; they are not zero-latency successes. Primary p50/p95/p99 values
use successful scheduled response time in offered mode, with service quantiles
reported separately. Per-second planned/sent/started/succeeded/failed/rejected/
row counts retain overload and recovery observations. The finite time-series
capacity covers the offered interval plus 300 seconds; truncation is explicit.

The arrival clock follows the managed harness's one-millisecond sleeps above a
two-millisecond margin and short processor pauses near a deadline. Its CPU and
scheduling delay are included. `--empty-driver` preserves the schedule and
expected-result counters while omitting database execution/materialization in
the measured operations. This is an explicitly labeled harness control; its
cost is not blindly subtracted from another process's result.

## Materialization and measurements

Numeric output is a value. Other projections construct owned C++ DTOs and
nullable strings. JSON uses nlohmann SAX parsing to construct an owned
`Settings` object with `Channel` and `Gift`; no DOM is needed for this fixed
shape. Money is a signed integral number of cents with fixed scale two.
PostgreSQL uses binary single-row results; its numeric decoder rejects
overflow or rounding. Every DTO is consumed before destruction. Allocation
mechanisms and string layouts naturally differ from CLR objects; the logical
values, ownership lifetime and digest contract are the comparison boundary.
Nullable aggregate values preserve the presence byte used by the shared digest.
Related batches retain all owned child DTOs, allocate one group per requested
parent including empty groups, sort children by Id and consume parent/group
headers plus every child field before releasing the batch.

Transaction cases retain owned original, changed and persisted full-order
objects through the operation. All nine fields, including NULL, typed money and
typed JSON, are checked against the shared state contract. Updates check exact
affected counts; the stale checked update constructs and catches a native
concurrency-conflict exception after observing zero affected rows. Commit cases
restore the original row inside the transaction before committing; rollback
cases roll back, then all cases read and verify the persisted original. This
includes 7, 6, 7 and 6 business SQL legs respectively. Korda-specific
`query_only=OFF` or the pre-commit `SELECT 1` are framework overhead and are not
added to the direct business contract. A failed operation closes its connection
promptly so an unfinished write is rolled back and cannot hold a lock throughout
the remaining offered interval; subsequent accepted jobs on that worker remain
explicit failures without retry.

Early termination consumes three owned wide rows from the full 1,024-row query.
SQLite resets/finalizes immediately without stepping the remainder. PostgreSQL
drains remaining single-row results through the terminal null and checks idle,
without materializing them or sending a cancel-key. This matches the current
product's disposal rule and avoids aborting an enclosing transaction. The
additional PostgreSQL rows drained are reported separately from business rows.

The raw JSON includes completed operations and rows, success throughput,
base-two latency histograms with 128 subdivisions per exponent, p50/p95/p99
upper bounds, per-second completion counts, error strings, process user/system
CPU, CPU per successful operation, idle CPU, RSS/PSS observations, process peak
RSS and drain counters. Controller samples are needed for time-resolved
client/server memory and CPU; process peak RSS also includes startup and warmup.
CPU uses `getrusage` immediately around start release and joined completion,
outside memory-probe reads. Monotonic timestamps use `CLOCK_MONOTONIC` nanoseconds.
The input manifest is hashed before and after execution; a changed input or
unreconciled schedule fails the run. Existing output files are never overwritten.

Managed allocation and GC are **not applicable**. Native allocation/free call
counts and a whole-process native heap peak are explicitly **unmeasured** in
this timing binary. `mallinfo2` values are current glibc allocated/reserved block
observations. SQLite's allocator high-water mark covers the SQLite engine only.
None of these substitutes for a complete native allocation trace. The output
does not establish sustainable saturation, active-cancellation semantics,
execution-plan equality or a 30-minute qualifying interval by itself. Those
claims require the corresponding frozen campaign inputs, qualifying duration,
error/tail conditions and raw observations from a dedicated host.
