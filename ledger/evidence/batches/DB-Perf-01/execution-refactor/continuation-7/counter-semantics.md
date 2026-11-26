# Execution counter semantics at the selected product source

This is a source review of Korda
[`17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`](https://github.com/IzuSharp/Korda/commit/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa).
It records the scope of the existing ordinary workload, FFI diagnostic and
PostgreSQL protocol tests. Writing this record did not run a build, test,
benchmark, compression or evidence rehash. The protocol observations below
refer to the previously reviewed raw evidence, not a new execution.

The three requested quantities are distinct. The ordinary Korda consumer
records actual SQL dispatch and libpq submission counter endpoints. A separate
instrumented consumer records managed-to-native ABI calls. A real PostgreSQL
proxy counts protocol groups and selected replies in correctness tests; those
proxy counters are not collected in the ordinary 30-minute workload. None of
these records measures physical network round trips.

## Measurement inventory

| Quantity | Actual observation | Scope and limit |
| --- | --- | --- |
| Managed-to-native FFI | Diagnostic `Ffi.Calls[]`, `PendingReturns[]` and `OkReturns[]`, indexed by the diagnostic build's symbol inventory. | Calls to the wrapped Korda ABI entry points. No such arrays exist in the ordinary consumer. Native-to-managed notifications, internal C++ calls to libpq/sqlite and diagnostic counter reads are excluded. |
| SQL activity | Ordinary `Before`, `After` and `Drained` snapshots of `SqlExecutions`, from `provider_dispatch_count()`. | Actual module-local provider dispatches, including internal control SQL in the selected interval. This is not a server-side count of successfully completed SQL statements. |
| libpq submissions | The same ordinary snapshots of `ProtocolSubmissions`, from `provider_protocol_count()`. | Successful libpq send/Sync API submissions. One API call can contain multiple protocol messages. These are not reply counts, packet counts or RTT. |
| PostgreSQL confirmation replies | `SyncProxy`'s actual description groups, execution groups, standalone Sync messages and forwarded ReadyForQuery replies. | Real TCP protocol frames in the dedicated correctness tests. No per-case or long-workload reply trace is implied. |
| OS waits | Diagnostic `ProviderPollCalls`, `ProviderPollTimeouts`, `ProviderPollErrors` and `ProviderPollNanoseconds`. | Actual `poll()` observations whose immediate caller is a `libnw_database_*` image. Readiness waits do not count mandatory protocol replies or RTT. |
| Business completions | Ordinary per-case Started, Succeeded, Failed, Rows and suspension observations. | Actual application outcomes. The native SQL/protocol counters are not partitioned by case. |
| Static expected SQL legs | Manifest `queryExecutionsPerOperation` multiplied by successful business operations. | A derivation from the specified successful flow, not an observed SQL trace. Partial failures and provider control SQL require separate treatment. |

Primary source: [ordinary Korda measurement](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/benchmarks/db-perf/managed/Korda/Measurement.cs),
[provider counter declaration](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/include/nw/provider.hpp),
[provider implementation](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/src/provider.cpp),
and [ABI diagnostic export](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/src/host_abi.cpp).

## Ordinary workload endpoints and SQL meaning

The ordinary Korda record has this native diagnostic shape:

```text
Sources, Sessions, Operations, Cursors, Buffers, Owners,
SqlExecutions, ProtocolSubmissions, PullChannels?, CommandCompletions?
```

The last two ownership counters are available when their corresponding product
exports are present. They do not count completed business operations.

Worker/session setup, validation and warmup precede the `Before` read. The
consumer waits for the workload tasks to finish before reading `After`, then
disposes workers and Source before `Drained`. Therefore:

- `After - Before` is the actual operation-interval SQL/submission delta.
- `Drained - After` is the separately observable close/retirement delta.
- `Drained - Before` includes both intervals and must not silently replace the
  operation-only denominator.

These are source-ordered endpoint reads, not a claim that all diagnostic fields
and the elapsed-time boundary were sampled atomically. The phase consumer uses
analogous `NativeBefore`/`NativeAfter` snapshots per window. Its successful
per-operation path does not add a native-counter read to every phase sample.

Despite its serialized name, `SqlExecutions` has precise dispatch semantics:

| Provider path | Increment point |
| --- | --- |
| SQLite statement | Once before the first `sqlite3_step` of that statement execution. Subsequent rows/steps do not each increment it; the first step may still fail. |
| PostgreSQL prepared execution | After `PQsendQueryPrepared` accepts the submission. A successful send does not prove successful server execution. |
| PostgreSQL extension-type lookup | After its `PQsendQueryParams` succeeds. This internal query contributes to the same total. |
| PostgreSQL direct SQL path | After `PQsendQuery` succeeds. The unit is that dispatch, not an independently counted set of server statements. |

Prepare/Describe without execution does not increment the SQL dispatch counter.
Repeated batch fetches from the same execution do not each represent another
SQL execution. SQL controls used for admission, transactions, recovery or
connection health contribute whenever they run inside the measured interval.
The record does not identify each dispatch as business SQL versus control SQL.

`ProtocolSubmissions` increments after successful `PQsendPrepare`,
`PQsendDescribePrepared`, `PQpipelineSync`, `PQsendQueryPrepared`, extension-type
`PQsendQueryParams`, and direct `PQsendQuery` calls on the paths above. SQLite
leaves this network-protocol counter at zero. Zero here does not mean absence of
SQLite lock, scheduler or storage waits.

Sources: [provider implementation](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/src/provider.cpp),
[phase windows and their stated scope](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/benchmarks/db-perf/query-phases/Program.cs),
and [raw metric classification](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/benchmarks/db-perf/analysis/raw_metrics.py).

## The 60-symbol FFI diagnostic

Reading the selected source's signature files gives this inventory. These are
static counts of callable symbols, not measurements of how often they execute.

| Signature inventory | Symbols |
| --- | ---: |
| `signatures-v1.json` | 42 |
| `query-command-v1.json` | 3 |
| `cursor-pull-v1.json` | 10 |
| `command-completion-v1.json` | 4 |
| `find-shape-v1.json` | 1 |
| Total | 60 |

The generator also supports an optional `result-batch-v1.json`; it is absent
from this exact source and contributes no extra symbols. The actual arrays
must be interpreted with their own `diagnostic-build.json` symbol list rather
than a hard-coded historical array length.

For each declared function, the wrapper increments Calls before forwarding to
the real function. A function returning `nw_status` additionally increments
PendingReturns for `NW_PENDING` or OkReturns for `NW_OK`; other statuses still
contribute to Calls. Functions with another return type, including `void`, do
not get a synthetic OK count. The wrappers are returned during actual `dlsym`
resolution; already-resolved pointers are not rebound. The diagnostic requires
preloading before ABI resolution and checks that Source creation was observed.

The 60-symbol inventory excludes `nw_db_diagnostic_count_v1`. Calls to the
diagnostic shim's own `db_perf_ffi_count` are also not product ABI observations.
Native-to-managed ready/quiet/retired notifications are not intercepted. Thus
the result is managed-to-native Korda API traffic, not all language-boundary
crossings in the process.

The overlay uses an independently instrumented copy of an external successful
PackageReference Native AOT consumer with the same provider package/image. It
marks itself instrumented, `TimingComparisonEligible=false`, `timingCredit=false`
and `allocationCredit=false`. Its atomic increments and probe reads can change
the workload's cost. Its timing/allocation results cannot replace ordinary
consumer comparisons.

The poll hook records calls, returned timeouts/errors and elapsed monotonic
nanoseconds only when `dladdr` identifies the immediate caller as a Korda native
provider. A buffered reply may require no poll; one reply may require multiple
polls. Poll elapsed time does not separately identify server execution,
transport, readiness, cancellation or scheduler costs. Similarly, a managed
MoveNext suspension or ABI `NW_PENDING` is not a network reply count.

Sources: [signature-driven overlay builder](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/benchmarks/db-perf/cursor-diagnostics/build.py)
and [actual dlsym/poll wrapper](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/benchmarks/db-perf/cursor-diagnostics/probe.c.in).

## Real PostgreSQL reply counts and mandatory confirmation

The selected [PostgreSQL protocol tests](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/tests/postgres_sync_tests.cpp)
use a real TCP proxy. `SyncProxy` reads complete frontend/backend frames and can
hold or drop selected confirmations. At a frontend Sync it distinguishes a
Parse+Describe group without Execute, an execution group, or a standalone Sync.
It records actual Parse SQL and increments `ready_responses` for forwarded
ReadyForQuery (`Z`) replies. A deliberately dropped reply is not counted as
forwarded; the fault is recorded separately. The proxy does not separately
count every ParseComplete, BindComplete, DataRow or CommandComplete frame.

The previously reviewed candidate passed **432 assertions**. That number is a
test-check count, not a protocol-message, reply or round-trip count. The raw
observations and negative-control identity are retained in
[the native-path review](native-path-review.md#real-protocol-checks-and-negative-control).
This document does not rerun or rehash them.

`healthy_commit_dispatch` snapshots counters immediately before
`tx->finish(true)` and reads them after `tx->join()`. Both the ordinary nonquery
route and a route that previously consumed a cursor's real EOF check the
following narrow commit/retirement window:

| Observed count | Historical old implementation with the negative assertion | Commit-proof candidate |
| --- | ---: | ---: |
| Provider SQL dispatches | 2 | 1 |
| Description groups | 2 | 1 |
| Execution groups | 2 | 1 |
| Standalone Sync messages | 2 | 2 |
| Forwarded ReadyForQuery replies | 6 | 4 |
| Successful libpq submissions | 10 | 6 |

The old implementation is the retained failing negative control, not a passing
current candidate. Its source is `cb86d949e591b482f55bf7f497477bc8b0f8d35d`;
the reviewed commit-proof source is
`d2c137bf44eb0b8490c8c4f59f12f34d2df75ac2`. The selected `17da07e` source retains
the same count assertions. Historical receipt and log identities remain in the
linked review; their old source identity is not replaced with `17da07e`.

The actual assertions require `descriptions == dispatches`,
`executions == dispatches`, `standalone_syncs == 2`,
`ready == 2 * dispatches + 2`, `submissions == 4 * dispatches + 2`, and finally
`dispatches == 1`. They also verify that an independent physical connection
observes the committed write and that the original backend PID is reused.
These are measured test observations plus asserted conservation equations,
not inferred long-workload counts. The window excludes transaction BEGIN,
earlier business reads/writes and the later independent durability query.

The other real protocol tests distinguish the retained waits:

| Boundary | Actual assertion or fault behavior |
| --- | --- |
| Parse + Describe + Sync | The replies are consumed before exposing metadata. Holding the actual metadata ReadyForQuery exercises an independent finite cleanup budget. |
| Natural stream EOF | The actual Execute group's ReadyForQuery supplies completion. No extra standalone stream-health Sync is submitted. |
| Exact row limit / early stop | A row count does not manufacture EOF. The unfinished stream keeps its drain obligation and an independent Sync. |
| Delivered row with lost Execute confirmation | A transferred batch remains valid; failure to finish the actual Execute reply leaves the native-retired connection quarantined. |
| Transaction after cursor EOF | A completed stream does not replace the transaction's separate COMMIT confirmation. |
| Healthy commit | The pre-COMMIT probe can be skipped under the exact confirmed-state predicate, while post-COMMIT and independent recovery Sync remain. |

For example, `stream_completion` observes one execution dispatch/submission
after its cursor is opened. A naturally exhausted stream observes the actual
execution group and ReadyForQuery without a standalone Sync; a row-limit stop
adds one standalone Sync during close. Its snapshot begins after description,
so those numbers cannot be presented as the total query-open-to-close cost.

These tests establish why the waits remain. They do not assign latency or CPU
to each reply in the final mixed-load run. Successful send counts, group counts,
ReadyForQuery counts and physical network round trips stay separate quantities.

## Dapper SQL contracts and static per-case derivations

The [ordinary Dapper measurement](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/benchmarks/db-perf/managed/Dapper/Measurement.cs)
has no provider SQL, FFI or protocol counters. Its Before/After/Drained values
are [application-owned logical connection counts](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/benchmarks/db-perf/managed/Dapper/Driver.cs).
The lifecycle record's nullable SqlExecutions is explicitly null when internal
dispatch counts are unavailable; it is not zero. The separate Dapper phase
consumer also states that provider/native owners, FFI and protocol waits are
not instrumented.

The [SQL contract validator](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/benchmarks/db-perf/workload/check_dapper_contract.py)
checks source SQL against the frozen manifest and separately reads the actual
successful AOT build's emitted factories. It verifies typed parameter bindings,
value members, Find's nine-column matching and complete Order construction.
Its twelve generated lifecycle call locations comprise nine workload locations
and three verification locations. Twelve is an emitted call-site inventory,
not twelve calls per operation or a runtime counter.

Both the static and generated-factory receipts retain
`runtimeSqlTraceVerified=false`. The SQL-matched contract requires PostgreSQL
business SQL and ordered parameters to match after named-to-positional rewrite.
For SQLite, the documented ordinal `?` to unique `@name` difference is permitted;
byte-identical raw placeholder syntax is not claimed. Each provider uses its
normal transaction API; Korda-specific probe SQL, Sync and PRAGMA controls are
not inserted into Dapper to force matching internal behavior.

The [frozen workload manifest](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/benchmarks/db-perf/workload/queries-v3.json)
specifies one logical query leg for read cases and early-stop, seven for
tx-commit/partial-update and six for tx-rollback/stale-conflict. The transaction
totals include BEGIN and transaction-ending steps in the specified sequence;
they do not include all provider health or recovery SQL. Multiplying these
constants by actual successes is a static successful-flow expectation. Failed
operations can stop partway through a SQL sequence. Ordinary Korda does not
publish per-case native execution totals, and Dapper does not publish native
execution totals at all.

The separate direct-native C++ harness has additional actual prepare, describe,
confirmation-Sync, poll and unmaterialized-drain counters. Its
[`protocol` record](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/benchmarks/db-perf/native/main.cpp)
and the native-only conservation checks in
[raw_metrics.py](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/benchmarks/db-perf/analysis/raw_metrics.py)
do not add those fields to the ordinary Korda or Dapper schemas.

## Reporting boundary

Report ordinary workload activity, independent FFI diagnostics, real protocol
test observations and static flow derivations as separate evidence classes.
Do not replace an unavailable count with a derived number without labeling it.

Remaining attribution limits are the lack of per-case SQL/reply provenance in
the mixed-load native counters, lack of native-to-managed notification counts,
lack of Dapper internal SQL/FFI/reply counters, and lack of physical RTT
measurements. ActualDiagnosticSql strings describe constructed SQL/contracts;
they are not a wire trace. The available phase timestamps and poll observations
do not independently attribute SQL copying, native transcoding, batching,
managed wakeup, DTO mapping or release costs to individual protocol replies.

This record supplies counter semantics, not new performance acceptance,
zero-allocation evidence or permission to reinterpret a diagnostic run as an
ordinary timing result.
