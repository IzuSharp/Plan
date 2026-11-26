# DB-Exec-Parity-01 — PostgreSQL measured stage report

This report completes the PG attribution handoff to the paired Stage 1 gate. It
does not claim parity, a selected optimization, or final 30-minute acceptance.
The ordinary product remains main `7ff7b57b907b689defb880b8af62d83679608603`.
The diagnostic product branch is local-only
`dc1b4d5fcc32ba3bec9b4b0292c8e9366f5804b6`, never a publication candidate.
All paths here are relative to
`/workspace/scratch/34ddfdb91b5c/DB-Exec-Parity-01`.

## Findings and what they establish

The ordinary 1,000-row hot Prepare path costs 4328.786 µs client CPU/business,
versus Dapper.AOT 495.197 µs (8.742×), with only 550.010 B more process-wide
managed allocation. Complete Host SQL remains 4329.647 µs. The cost is primarily
after query construction; these short phase receipts are descriptive, not final
sustained throughput results.

The same query has seven Korda frontend messages versus five Dapper messages;
both return exactly 1,000 DataRow frames and 30,912 DataRow bytes. Total wire
volume differs by only 71 B/business. With a direct connection, the observed
Korda query makes two actual `poll` calls, from one row through 1,000 rows. The
row-amplified gap is not 1,000 mandatory network replies or 1,000 socket waits.

Korda does deliver 1,000 single-row PGresults, installs cancellation hooks 1,002
times, and admits 32 native batches. At batch32 the diagnostic request has 34
worker tasks, 2,000 cell scans and 1,800 non-null offset rewrites. Stage timelines
separate native work, queue entry, ready notification and managed take. Larger
batch probes reduce delivery count while row controls remain constant. These
observations justify isolated causal experiments; their instrumented timing
cannot be substituted for the ordinary benchmark.

## Run identities, completeness and clock scope

`measurements/postgresql-stage-01` is the protocol observer run. It completed all
seven cases × Korda/Dapper = 14 processes, plus seven separate EXPLAIN requests.
`measurements/postgresql-stage-direct-01` repeated the same diagnostic ELFs and
sampler without the proxy, also 14 successful processes and seven EXPLAINs. Both
used 64 warmup requests per route and one window of eight measured requests per
route. Korda has Fluent, prepared and Host SQL routes; Dapper has its generated
route. Client CPUs were 0–3, server CPUs 4–7 and controller CPU 8. Root reserved
an exclusive local task measurement lane. No concurrent task build/load ran;
other host tenancy and kernel scheduler causes are not established.

All client exits were zero. All row, null, order, early-stop and exposed-owner
checks passed. Trace validators reported no observed marker loss, unregistered
threads, kernel/output/ring loss, identity errors or proxy frame loss. Capacity
was 1,048,576 markers and 64 MiB raw sample events/process, with a hard failure on
loss. Raw files, logs, identities and negative/failed earlier attempts remain.
The direct run occupies about 156 MiB; it passed its 400 MiB free-space gate.

Markers record CLOCK_MONOTONIC_RAW, CLOCK_MONOTONIC, TID and THREAD_CPUTIME_ID.
Only same-TID spans subtract thread CPU. Async phase wall intervals may cross
threads; they never subtract cross-thread CPU. Queue/ready/worker spans are
nested or overlapping and cannot be added as independent CPU or elapsed totals.
`poll` elapsed minus thread CPU also includes preemption and runnable delay; it
is not an observed kernel-blocked duration. Short spans can have CPU greater
than wall due to non-simultaneous clock sampling and marker overhead.

### Corrected attribution boundaries

The authoritative analyzers are `*-analysis-03.json`. Versions 01 and 02 are
retained as superseded derived outputs. Version 01 selected request IDs but
could include later generic work carrying stale native TLS. The corrected
analysis requires the explicit request's construction-to-close interval, bounded
by the next request and actual window end, and records excluded
`outsideRequestMarks`. For example, direct rows32/prepared request209 had a
later queue task about 4.4 ms after close: it is not charged to that request.
Final teardown can also inherit the last ID and is excluded.

One direct rows1000/prepared task starts inside the request and its diagnostic
WorkerSpan end follows the real close fence. This is explicitly retained as a
`knownTaskTailMarks` pair, identified by its task ID, batch and TID; its worker
CPU is associated with that known task, while request latency is not extended.
The wrapper surrounds the original worker ticket, so this diagnostic tail is
not evidence of a product retirement violation. Version02 had dropped that end
and left a partial span; version03 resolves it without relabeling unrelated work.

## Ordinary baseline: same contract, four routes

Each row aggregates three rotating windows of 256 operations. CPU is whole
client process CPU (including runtime threads), and allocation is whole-process
managed allocation; neither is a framework-exclusive number. Phase timing and
oracle bookkeeping remain part of this existing probe's stated scope.

| Rows | Route | Measured operations | Process CPU µs/business | Managed B/business |
| --- | --- | --- | --- | --- |
| 1 | fluent | 768 | 529.956 | 19547.135 |
| 1 | prepared | 768 | 398.818 | 2572.969 |
| 1 | host-sql | 768 | 455.372 | 8116.24 |
| 1 | dapper-aot | 768 | 124.238 | 2112.781 |
| 100 | fluent | 768 | 1012.539 | 26636.104 |
| 100 | prepared | 768 | 907.289 | 9748.24 |
| 100 | host-sql | 768 | 949.667 | 15305.865 |
| 100 | dapper-aot | 768 | 153.719 | 9242.229 |
| 1000 | fluent | 768 | 4541.16 | 97447.333 |
| 1000 | prepared | 768 | 4328.786 | 80552.521 |
| 1000 | host-sql | 768 | 4329.647 | 86251.375 |
| 1000 | dapper-aot | 768 | 495.197 | 80002.51 |


Source: `measurements/phase-baseline-01/postgresql/*-{1,100,1000}.json` and their
command/resource/build receipts. Generated PhaseRow readers and each actual
restore graph are under `consumers/baseline-postgresql/`. Actual packages are
Dapper2.1.100, Dapper.AOT1.1.0 and Npgsql11.0.0, not the separate old campaign's
Dapper2.1.79 lock. SDK11.0.100, runtime11.0.0, PostgreSQL18, LLVM23.1.5,
CMake4.3.3 and Ninja1.13.2 are pinned in the build receipts.

## Protocol messages, API calls, engine executions and real polling

For every full measured request in all Korda routes the frontend sequence is
`P D S B D E S`: Parse, Describe statement, Sync, Bind, Describe portal, Execute,
Sync. Dapper uses `P B D E S` with only portal Describe. Korda's preparation must
finish fresh shape validation before Execute. Its ordinary receipt records four
libpq protocol submissions/business; that is an API counter, not seven messages,
four round trips, or four waits. Each narrow request executes one business SQL.

Wire Parse SQL hashes match between both implementations:

- Ordered range: `23f553eac84caa18689621fe30ad65ba974ad7401873c7b34f97e2790576f553`.
- Complete composite primary key: `7e67cea46c2e66530882627b47e4b8e4f686664dd85c5ccb6cd00bd6eaa85e97`.

Both parameters are logical Int64. Korda encodes text parameter bytes (at1,000
rows, lengths1 and4); Dapper encodes two binary8-byte parameters. Both request
binary results. The one-thousand-row wire totals are Korda31,345 B and
Dapper31,274 B, including 30,912 DataRow bytes each. Row data and SQL execution
are equal even though metadata barriers and parameter formats differ.

Stopping after one DTO for the1,000-row SQL still yields1,000 DataRow frames on
both paths. Korda's sequence is `PDSBDESS`, with an additional cleanup Sync and
ReadyForQuery (+11 B versus its full query). Dapper remains `PBDES`. Korda admits
only its first32-row native batch, then drains the remaining PGresults. This is
different from SQLite early stop and cannot be normalized as the same amount
of engine work across databases.

The proxy changes packet delivery. Its measured Korda hot1,000/B32 query made
299.25 actual poll calls/business on average (range192–378); direct observation
made exactly2. Thus the proxy establishes message order/bytes, not the original
client waiting cost. The table below is from the **direct instrumented run**.
All values are means per hot Prepare business, in µs. Worker, prepare, poll and
batch spans overlap; do not sum these columns.

| Case | poll calls | poll wall | poll thread CPU | native worker CPU | prepare wall | prepare CPU | fetch/batch CPU |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rows32 | 2 | 183.385 | 12.888 | 181.043 | 113.601 | 37.201 | 69.936 |
| pk1 | 2 | 146.845 | 20.753 | 115.546 | 89.89 | 40.573 | 28.483 |
| rows100 | 2 | 202.952 | 19.727 | 260.4 | 109.701 | 42.625 | 107.339 |
| rows1000 | 2 | 245.777 | 16.848 | 1873.878 | 128.537 | 44.777 | 1062.499 |
| rows1000-stop1 | 3 | 277.76 | 28.759 | 766.316 | 110.432 | 37.643 | 60.209 |
| rows1000-b128 | 2 | 221.035 | 13.68 | 1413.233 | 104.712 | 32.859 | 1100.257 |
| rows1000-b256 | 2 | 253.322 | 19.681 | 905.323 | 110.148 | 38.13 | 770.518 |


Dapper's source has buffered `TryRead` and async `EnsureLong` paths, and its
actual generated AOT method symbols are preserved. This run does not instrument
inside Npgsql socket waits, so Dapper's per-call poll/OS-blocked count is unknown.
Its public phase markers establish submit/first row/read/close ordering without
inventing a symmetric native poll metric.

## Work counts and copies

The following counts are measured per hot Prepare request and are identical
across the eight requests in each case. `provider PQclear` counts only Korda's
explicit calls, not internal libpq allocations/frees. PGresult delivery is not
itself an allocation-event count. Root's independent allocator observations
provide the separate public-allocation evidence.

| Case | Batch row sequence | Worker tasks | Cancel.install | advance | SINGLE_TUPLE | provider PQclear | nonnull fields | NULL fields |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rows32 | [32, 0] | 4 | 34 | 33 | 32 | 36 | 58 | 6 |
| pk1 | [1] | 3 | 3 | 2 | 1 | 5 | 2 | 0 |
| rows100 | [32, 32, 32, 4] | 6 | 102 | 101 | 100 | 104 | 180 | 20 |
| rows1000 | 31×32+8 | 34 | 1002 | 1001 | 1000 | 1004 | 1800 | 200 |
| rows1000-stop1 | [32] | 3 | 33 | 32 | 1000 | 1005 | 58 | 6 |
| rows1000-b128 | 7×128+104 | 10 | 1002 | 1001 | 1000 | 1004 | 1800 | 200 |
| rows1000-b256 | 3×256+232 | 6 | 1002 | 1001 | 1000 | 1004 | 1800 | 200 |


Byte/cell totals below are exact sums at the instrumented boundaries. Payload
insertions and canonical scalar forwarding both total15,912 B at1,000 rows;
these are successive stages of the same values, not two copies to add blindly.
Borrowed PGresult field byte lengths are not claimed as extra copies. The
selected native-to-managed batch path attaches a scoped native view and does
not copy a whole native batch to a managed byte array.

| Case | payload insert B | vector growth copied B | finish memmove B | table zero B | finish scanned cells | nonnull offset writes |
| --- | --- | --- | --- | --- | --- | --- |
| rows32 | 482 | 0 | 0 | 3328 | 64 | 58 |
| pk1 | 16 | 0 | 16 | 1664 | 2 | 2 |
| rows100 | 1512 | 0 | 59 | 6656 | 200 | 180 |
| rows1000 | 15912 | 0 | 124 | 53248 | 2000 | 1800 |
| rows1000-stop1 | 482 | 0 | 0 | 1664 | 64 | 58 |
| rows1000-b128 | 15912 | 58352 | 1662 | 50176 | 2000 | 1800 |
| rows1000-b256 | 15912 | 53752 | 3706 | 49664 | 2000 | 1800 |


At batch32, vector-growth copy is0 B in this workload. A blanket claim that
batch-vector growth causes a huge copy per batch is contradicted by these data.
The final partial eight-row batch moves124 B; full-batch cell offset rewriting
does remain. B128/B256 growth-copy totals increase while handoff count falls,
which separates bytes moved from number of native/managed deliveries.

## Request critical path and overlap

Each pull generation has explicit publication, worker-begin, native-ready and
managed-take markers. These are paired by request, generation and task ID. The
following direct hot Prepare table sums the **non-overlapping pull path
intervals** per request; it does not sum nested CPU spans. Queue means queue
publication→worker start. Worker→ready includes engine/client work and polling.
Ready→take includes callback delivery, managed scheduling and any descheduling.
Take→next queue includes validation, mapping, loop and dispatch work. None is
a pure scheduler-wait or exclusive materialization measurement. Unclassified
includes construction, admission and final close outside this pull chain.

| Case | pull queue µs | worker→ready µs | ready→take µs | take→next queue µs | unclassified µs | request RAW µs |
| --- | --- | --- | --- | --- | --- | --- |
| rows32 | 37.507 | 322.927 | 66.003 | 24.069 | 147.125 | 597.631 |
| pk1 | 23.262 | 213.568 | 59.998 | 0 | 157.291 | 454.118 |
| rows100 | 128.012 | 389.714 | 188.609 | 75.494 | 138.359 | 920.187 |
| rows1000 | 827.624 | 1815.743 | 982.921 | 500.73 | 122.23 | 4249.247 |
| rows1000-stop1 | 30.4 | 349.05 | 47.653 | 0 | 835.204 | 1262.307 |
| rows1000-b128 | 380.841 | 1529.778 | 271.905 | 287.718 | 105.243 | 2575.485 |
| rows1000-b256 | 277.494 | 1095.122 | 148.929 | 299.415 | 244.818 | 2065.778 |


The raw timelines for each of the eight measured requests appear under
`routes.*.perRequest` in the analysis, including backend IDs, polls, same-TID
worker CPU, generation/TID pairs and exact clock values. Larger batch settings
are only sensitivity probes. Acceptance retains batch32 and the original SQL,
DTO and full-consumption contract.

All four public route phases, in direct diagnostic µs/business:

| Case | Route | construct | submit→first row | remaining reads/EOF |
| --- | --- | --- | --- | --- |
| rows32 | fluent | 110.62 | 343.514 | 202.803 |
| rows32 | prepared | 2.59 | 392.225 | 200.365 |
| rows32 | host-sql | 34.727 | 349.288 | 206.755 |
| rows32 | dapper-aot | 1.28 | 145.2 | 12.221 |
| pk1 | fluent | 102.824 | 330.4 | 77.361 |
| pk1 | prepared | 1.728 | 320.318 | 129.895 |
| pk1 | host-sql | 35.642 | 313.145 | 102.126 |
| pk1 | dapper-aot | 10.204 | 134.057 | 2.713 |
| rows100 | fluent | 157.88 | 1147.209 | 492.354 |
| rows100 | prepared | 1.867 | 402.445 | 513.801 |
| rows100 | host-sql | 40.285 | 452.014 | 460.392 |
| rows100 | dapper-aot | 1.397 | 228.096 | 30.147 |
| rows1000 | fluent | 172.792 | 483.784 | 3693.093 |
| rows1000 | prepared | 3.796 | 446.727 | 3793.931 |
| rows1000 | host-sql | 46.77 | 468.273 | 3442.718 |
| rows1000 | dapper-aot | 24.609 | 251.146 | 401.903 |
| rows1000-stop1 | fluent | 196.863 | 473.623 | 0.312 |
| rows1000-stop1 | prepared | 59.351 | 466.663 | 0.311 |
| rows1000-stop1 | host-sql | 136.896 | 467.134 | 0.257 |
| rows1000-stop1 | dapper-aot | 7.37 | 209.492 | 0.376 |
| rows1000-b128 | fluent | 102.456 | 652.172 | 1769.857 |
| rows1000-b128 | prepared | 3.141 | 540.924 | 2029.289 |
| rows1000-b128 | host-sql | 41.167 | 491.827 | 2077.936 |
| rows1000-b128 | dapper-aot | 28.976 | 225.538 | 422.671 |
| rows1000-b256 | fluent | 99.029 | 618.514 | 1122.517 |
| rows1000-b256 | prepared | 7.481 | 709.571 | 1346.061 |
| rows1000-b256 | host-sql | 52.319 | 840.468 | 1373.635 |
| rows1000-b256 | dapper-aot | 5.374 | 284.217 | 297.875 |


These phases include observer overhead. For scale, direct diagnostic1,000-row
process CPU is prepared6424.5 µs and Dapper780.25 µs, versus their ordinary
4328.786 and495.197 µs. No instrumented endpoint gain is credited to the product.

## PostgreSQL backend, plan and buffer correlation

The same pinned PG18 server and settings serve each controller's clients. The
server is owned by the controller's process family, not started in a disconnected
tool network namespace. Proxy startup BackendKeyData gives each path's actual
backend PID without recording its cancellation secret. Native direct markers
also record PQbackendPID for Korda. Direct Dapper did not expose its ProcessID
through this build; the wire run supplies its per-connection correlation, and
the missing direct Dapper PID is explicit.

| Case | wire Korda PIDs | wire Dapper PIDs | direct Korda PIDs | separate EXPLAIN PID |
| --- | --- | --- | --- | --- |
| rows32 | [56] | [72] | [52] | 70 |
| pk1 | [95] | [110] | [84] | 101 |
| rows100 | [132] | [147] | [115] | 133 |
| rows1000 | [169] | [185] | [147] | 166 |
| rows1000-stop1 | [208] | [223] | [180] | 197 |
| rows1000-b128 | [246] | [260] | [211] | 228 |
| rows1000-b256 | [284] | [298] | [242] | 259 |


`EXPLAIN (ANALYZE,BUFFERS,FORMAT JSON)` is a **separate extra request**, with
typed bigint parameters1 and row count, run after each pair. Its PID and
planning/execution milliseconds are not the timed client request's PID/cost.
At1,000 rows it uses query_phases_pkey, returns1,000 rows, hits12 shared blocks
and reads0. Plans for the small ranges include Sort over their chosen scan;
the complete nested JSON is retained rather than flattened into a claimed
single operator. Settings include shared_buffers128MB, work_mem4MB, auto plan
cache, jit on, fsync/synchronous_commit on, read committed and UTC.

| Case | EXPLAIN root | actual rows | shared hits | shared reads | planning ms | execution ms |
| --- | --- | --- | --- | --- | --- | --- |
| rows32 | Sort | 32.0 | 6 | 0 | 0.345 | 0.062 |
| pk1 | Index Scan | 1.0 | 3 | 0 | 0.303 | 0.026 |
| rows100 | Sort | 100.0 | 6 | 0 | 0.341 | 0.077 |
| rows1000 | Index Scan | 1000.0 | 12 | 0 | 0.325 | 0.163 |
| rows1000-stop1 | Index Scan | 1000.0 | 12 | 0 | 0.299 | 0.178 |
| rows1000-b128 | Index Scan | 1000.0 | 12 | 0 | 0.309 | 0.164 |
| rows1000-b256 | Index Scan | 1000.0 | 12 | 0 | 0.303 | 0.193 |


Each client also has separate server-tree snapshots and the original runner's
server accounting. These cover startup/warmup/process lifetimes and are
non-atomic observations. They are not subtracted from client CPU or relabeled
as precise per-query backend CPU. Original-request executor CPU, original-query
BUFFERS and global scheduler wait remain unknown. Parent's sustained campaign
will report PG server process cost separately.

## Source and actual machine-code binding

The paired source audit is `analysis/postgres-audit.md`. Main source chains are
`native/cpp/src/provider.cpp` (`advance`, `receive`, `wait_socket`, `close`),
`host.cpp` (CursorPull/WorkerPool/Cursor), `contracts.cpp` (BatchWriter), and
`scalar.cpp` (canonical decode), pinned to main7ff7b57. Dapper.AOT source is
`0e071bf05e54caecfa98c885b075fa3e247f3ecc`; Npgsql source is
`4d174200ed48e3e3ab16419dbf84dd655da59de6`; PG18/libpq source is
`3d6a828938a5fa0444275d3d2f67b64ec3199eb7` plus the recorded Korda patch.

The actual baseline Dapper RowFactory0.Read is at0xc3a20 (313 bytes), Tokenize
at0xc3880 (408 bytes), with correct newly generated source-line mappings in
`analysis/pg-machine/baseline-dapper-query-phases-llvm23/manifest.json`.
Npgsql's method symbols match actual machine code, but absent package PDBs
produce unrelated NullLoggerFactory line fallbacks; those lines are rejected.
The following native diagnostic O3+DWARF mappings are actual executable bytes,
not source-only hypotheses and not sampled instruction-cost claims:

| Symbol | Image address | Bytes | Source mapping |
| --- | --- | --- | --- |
| nw::BatchWriter::finish() | 0x3bfa0 | 1385 | /workspace/scratch/34ddfdb91b5c/DB-Exec-Parity-01/worktrees/Korda-diagnostic-postgresql/native/cpp/src/contracts.cpp:1212 |
| nw::postgres_decode_into(nw::Codec const&, unsigned int, std::__1::span<unsigned char const, 18446744073709551615ul>, nw::ScalarSink) | 0x9d4b0 | 2535 | /workspace/scratch/34ddfdb91b5c/DB-Exec-Parity-01/worktrees/Korda-diagnostic-postgresql/native/cpp/src/scalar.cpp:656 |
| nw::Cancel::install(std::__1::function<void ()>) | 0x9ed80 | 220 | /workspace/scratch/34ddfdb91b5c/DB-Exec-Parity-01/worktrees/Korda-diagnostic-postgresql/native/cpp/src/provider.cpp:267 |
| nw::ProviderStatement::Impl::advance(nw::CallContext const&) | 0xa6e90 | 2156 | /workspace/scratch/34ddfdb91b5c/DB-Exec-Parity-01/worktrees/Korda-diagnostic-postgresql/native/cpp/src/provider.cpp:399 |
| nw::WorkerPool::post(std::__1::function<void ()>) | 0xabce0 | 1044 | /workspace/scratch/34ddfdb91b5c/DB-Exec-Parity-01/worktrees/Korda-diagnostic-postgresql/native/cpp/src/host.cpp:316 |
| nw::Cursor::fetch(std::__1::shared_ptr<nw::Cancel>, unsigned long, unsigned long, bool) | 0xbc7b0 | 1565 | /workspace/scratch/34ddfdb91b5c/DB-Exec-Parity-01/worktrees/Korda-diagnostic-postgresql/native/cpp/src/host.cpp:2289 |
| nw::CursorPull::complete(unsigned long, std::__1::shared_ptr<nw::Buffer>, std::__1::optional<nw::Error>) | 0xc0d90 | 1305 | /workspace/scratch/34ddfdb91b5c/DB-Exec-Parity-01/worktrees/Korda-diagnostic-postgresql/native/cpp/src/host.cpp:2967 |
| nw::CursorPull::take(unsigned long) | 0xc1e10 | 634 | /workspace/scratch/34ddfdb91b5c/DB-Exec-Parity-01/worktrees/Korda-diagnostic-postgresql/native/cpp/src/host.cpp:3036 |
| pqRowProcessor | 0x11c120 | 537 | ??:0 |


The static libpq archive lacks DWARF, so pqRowProcessor's exact inline line is
unknown despite its real symbol/address. PG source is directly inspected at
the locked revision. Native SHA256 plus matching maps is used where GNU build
ID is absent.

### Cancellation callback allocation is not assumed

The actual Clang23/libc++ assembly of `advance` constructs its weak_ptr lambda
in std::function's small object buffer: addresses0xa7033–0xa7059 in diagnostic
`symbol-03.annotated.asm.txt` map to function.h's placement-new into the local
buffer. The `operator new` at0xa7130 instead maps to the first-execution
parameter pointer vector's reserve. Therefore1,002 Cancel.install calls do not
prove1,002 heap allocations. Repeated mutex entry, weak-control-block updates,
callback replacement and virtual destruction still exist. Their causal CPU
contribution needs the selected isolated experiment, not allocation folklore.

## Contracts and rejected PG result chunking

Fresh metadata and errors must precede Execute; complete validation/byte quotas
must precede batch publication; typed values/NULL/error order and input snapshots
remain unchanged. A complete row batch is not EOF: exactly32 rows produces
[32,0]. Early stop must drain through ReadyForQuery, preserve an otherwise usable
transaction, and discard an unsafe connection. A successful send or CommandComplete
does not prove return safety. COMMIT confirmation loss remains Unknown.

Unconditionally replacing PQsetSingleRowMode with PQsetChunkedRowsMode(32) is
rejected before product implementation. Locked libpq accumulates up to32 rows
before returning a partial PGresult. pqSaveErrorResult/pqClearAsyncResult discard
pending results, and the server ErrorResponse path replaces the pending result.
An error before the chunk fills can therefore suppress preceding rows that
single-row mode already delivered. Existing provider_tests.cpp's
`postgres_cancel_and_stream` requires a delivered row before a later division
error, and then safe discard on unread fatal drain.

The public/internal provider contract also explicitly holds at most the current
provider row; byte-bounded host batches retain at most one validated lookahead.
A32-row PGresult can retain rows beyond the byte-limited publication point and
beyond the existing conservative reservation. Shrinking only the logical batch
does not repair driver prefetch/error order. Changing generic drain acceptance
to allow PGRES_TUPLES_CHUNK would also be required, and would not by itself
repair these contracts. The rejection is about contract equivalence, not a
measured claim that chunking is slow. No benchmark-only SQL whitelist or weaker
contract is introduced.

The next PG/common candidate is repeated cancellation registration, after the
paired Plan gate: distinguish hook lifetime from statement lifetime, preserve
install-after-detach and mark/request races, and verify any predicted reduction
with counters and interleaved ordinary A/B. A plain same-Cancel pointer cache
is unsafe because Host detaches at preparation and every fetch while the
statement can retain the same context. Built-in narrow decode already uses a
16-byte stack scratch and borrowed strings; no per-cell Bytes allocation is
assumed for this selected path. All selected changes still need existing
correctness, public package and AOT-consumer verification.

## Evidence identities

| Artifact (relative to task root) | SHA-256 |
| --- | --- |
| `measurements/postgresql-stage-01/plan.json` | `58abd6145b56c8f98717b61081407af8e8af21b15a8c8185247ddc3ed3804eb9` |
| `measurements/postgresql-stage-01/completion.json` | `10ee44641c225f5d05027e6e38c382e5c9ff6bdf141ad98532d33ef0639f47da` |
| `measurements/postgresql-stage-direct-01/plan.json` | `bf363bdb0fb44a4b1b0e31cf1814e6d7cb6b756e6fbe3e67304b737195641be7` |
| `measurements/postgresql-stage-direct-01/completion.json` | `3a9c8c13874d500595e9413983afd303e387caf56262287caa23e62719cccfab` |
| `analysis/postgresql-stage-analysis-03.json` | `6d7920e7f2ae004705fe19ee49fa24de433b2de927c22184a5b7cbc5f120783a` |
| `analysis/postgresql-stage-direct-analysis-03.json` | `aeff343dce56b990be0510a1daea32ae309c61f2f59f0bfd7ba5c31deb963ac1` |
| `analysis/pg-machine/diagnostic-korda-native-01/manifest.json` | `0ab4fb6d78e43b04dbf444bf54e53819a50c316016d581e7b841b5c3fa5d7098` |
| `diagnostics/postgresql/analyze_phases.py` | `3e26e746074a5aad57b5df9b1f5d5326eaa1f1edf480fb2aedf332fbce1e7243` |
| `diagnostics/postgresql/run_phases.py` | `de54177037e2c960b6773bddf7053a8e822327e62bb15e76a7948464f681da07` |
| `diagnostics/postgresql/protocol_trace.py` | `7854f6b84d04d26d65d9c631e001ef6df6d6199fc31e9853c88b59f8f1a16ce6` |
| `consumers/diagnostic-postgresql/korda-native-markers/out/DbPerf.QueryPhases` | `18f62435169b2aa03f91998f38279fd67c7abed960c371bf3593a86f4a09e14f` |
| `consumers/diagnostic-postgresql/korda-native-markers/out/libnw_database_postgresql.so` | `3a555ff1e8fc34042c5fa8a3a43280394bf09c2ba312bf1b69aaf980288b7d82` |
| `consumers/diagnostic-postgresql/dapper-query-phases/out/DbPerf.DapperQueryPhases` | `d0494c1bdbb58d8b77200bb0fcd87607e8facbb809644546638ee0d4940db2b7` |
| `diagnostics/native_sampler/builds/03/libparity_sampler.so` | `896c0c8514b4a7f3112a9701543786473aa0e04e8c0485c72f41d8427b302d15` |


Commands are retained in controller plans and client command receipts. The
direct run command was:

```sh
source toolchain/environment.sh
taskset -c 8 python3 diagnostics/postgresql/run_phases.py \
  --output measurements/postgresql-stage-direct-01 \
  --library diagnostics/native_sampler/builds/03/libparity_sampler.so --no-proxy
```

The controller creates a fresh output directory; it cannot silently overwrite
the earlier wire run. All profiling, diagnostic builds and local measurements
stay out of CI. Source-driven recovery and correctness gates remain unchanged.
This report and analyzer are task evidence, not product performance instrumentation.
