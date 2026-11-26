# DB-Exec-Parity-01: measured dual-provider execution gate

Status: **Stage 1 evidence is sufficient to begin the ranked causal experiments below.**
This is not a parity claim, final campaign result, correctness waiver, or release acceptance.
The product is still the unmodified `7ff7b57b907b689defb880b8af62d83679608603` main.
Diagnostic branches are independent local observation builds, not product candidates.

## Evidence identities and scope

The eight ordinary consumers (mixed workload and query phases for each of four
provider/implementation combinations) were rebuilt with the locked SDK11.0.100,
runtime11.0.0, Dapper2.1.100, Dapper.AOT1.1.0, Npgsql11.0.0,
Microsoft.Data.Sqlite.Core11.0.0 and SQLitePCLRaw3.0.5. Actual generated C#,
ELF/debug files, restore assets, build commands, standalone local provider packages and native
images are retained in `evidence-packages/baseline/*-actual-artifacts.*`.
SQLite3.51.3 source and compile options match across the statically linked Korda
image and Dapper's shared image. Both PostgreSQL paths use the same local PG18
server/settings and typed SQL contract. No system SQLite3.46/libpq17 substitute
was used. Receipts identify rebuilt binaries, not historical originals.

The ordinary phase probes retain their own phase-clock overhead. They are useful
descriptive route costs, not the final mixed35 campaign. The native/managed stage
overlays, allocator interposition and sampler are explicitly diagnostic identities
with **no formal timing credit**. Observed spans may overlap: do not sum nested
native CPU, batch CPU, materialization, queue, or poll spans into a synthetic total.
All same-thread CPU deltas require matching TIDs. Extremely short spans can show
clock/marker overhead, including CPU slightly greater than raw elapsed time; they
are preserved rather than clipped into a fictional precise wait estimate.

## Actual ordinary route differences

Each entry below uses three rotating windows of256 measured operations,64 warmup
operations per route, one persistent session, client CPUs0–3, PostgreSQL CPUs4–7,
observer CPU8. No competing task compilation/load was admitted during these
measurements. Host tenancy and global kernel scheduling remain unproven.
All requests passed the same row oracle and Korda returned all exposed owners.

| Provider / rows | Route | Client CPU µs/business | Managed B/business | Total p50 µs | Read-after-first p50 µs |
| --- | --- | ---: | ---: | ---: | ---: |
| SQLite1 | Dapper.AOT | 14.387 | 2131.365 | 6.750 | 0.952 |
| SQLite1 | hot Prepare | 246.070 | 2588.062 | 115.147 | 49.534 |
| SQLite100 | Dapper.AOT | 57.353 | 9251.365 | 48.121 | 36.655 |
| SQLite100 | hot Prepare | 632.266 | 9765.094 | 304.476 | 206.598 |
| SQLite1000 | Dapper.AOT | 426.741 | 79810.188 | 371.670 | 352.251 |
| SQLite1000 | hot Prepare | 3754.876 | 80612.031 | 1720.626 | 1596.362 |
| SQLite1000 | Host SQL | 3784.777 | 86352.948 | 1741.759 | 1579.548 |
| SQLite1000 | ordinary Fluent | 3711.612 | 97469.458 | 1860.553 | 1647.152 |
| PostgreSQL1 | Dapper.AOT | 124.238 | 2112.781 | 130.925 | 1.232 |
| PostgreSQL1 | hot Prepare | 398.818 | 2572.969 | 349.280 | 71.086 |
| PostgreSQL100 | Dapper.AOT | 153.719 | 9242.229 | 203.573 | 21.852 |
| PostgreSQL100 | hot Prepare | 907.289 | 9748.240 | 716.096 | 292.225 |
| PostgreSQL1000 | Dapper.AOT | 495.197 | 80002.510 | 488.908 | 250.383 |
| PostgreSQL1000 | hot Prepare | 4328.786 | 80552.521 | 2648.951 | 2247.949 |
| PostgreSQL1000 | Host SQL | 4329.647 | 86251.375 | 2641.217 | 2178.469 |
| PostgreSQL1000 | ordinary Fluent | 4541.160 | 97447.333 | 2763.376 | 2283.175 |

The thousand-row Prepare CPU ratios are8.80× SQLite and8.74× PostgreSQL, while
extra managed allocation is about802 B and550 B respectively. Host SQL does not
remove the large execution cost. Dynamic construction has a real fixed allocation
cost but is not an adequate explanation of this row-amplified CPU gap.
Raw references: `measurements/phase-baseline-01`, provider summaries and
`diagnostics/summarize_phases.py`.

## One measured dual-database stage comparison table

All counts are per successful measured business request unless otherwise stated.
The diagnostic stage matrix covers1,32,100,1000 rows,1000 stopping after1, and
1000 with Korda batch capacities128/256 as **sensitivity probes**, not a changed
acceptance workload. Explicit request IDs and actual warm window boundaries
exclude startup, first-use, warmup and stale generic-worker TLS labels.
Actual generated code and machine-code binding are in the baseline artifact
manifests and `analysis/sampled-phases-02-verified`; native source/inline positions
are also bound by the independent O3+debug diagnostic build receipts.

| Business stage / provider | Actual source / generated code / sampled symbols | Measured executions and difference | CPU, waiting, allocation or copying evidence | Correctness contract | Next action |
| --- | --- | --- | --- | --- | --- |
| Construct, snapshot, submit / both | Korda QueryContext/Terminals, actual PhaseRow projection; Dapper generated command factory/row factory | One business SQL per narrow request on each route; ordinary Fluent, hot Prepare and complete Host SQL all observed | Above four-route results isolate the dominant gap after construction. Hot Prepare keeps only about0.55–0.80 KB extra managed allocation at1000 rows | Independent mutable-input snapshot, parameter order/type and error order | Keep Fluent public API; optimize the measured execution path first |
| Prepare/bind / SQLite | ProviderConnection::prepare→sqlite3_prepare_v3; SqliteCommand.PrepareAndEnumerateStatements→SQLitePCLRaw→sqlite3_prepare_v2 | Both prepare1, bind_int64=2, finalize1/query. Dapper reset1; Korda reset0. Both count RUN1 and same REPREPARE behavior | At1000 rows both execute1001 steps and VM_STEP6014/6015. No Dapper physical-statement reuse advantage exists in this contract. Public allocator32-row text: Korda185.039 calls/26361.56 B, Dapper0.211/103 B | Open validates metadata before effects; automatic schema reprepare; exact parameter and SQL semantics | Test only v3 flags=PERSISTENT→0: locked SQLite source disables lookaside under PERSISTENT despite measured per-query finalization. Require resource A/B; do not claim all allocation difference is framework-owned |
| Prepare/metadata and execute / PostgreSQL | Korda Cursor/ProviderConnection→PQsendPrepare/PQsendDescribePrepared/PQsendQueryPrepared; generated Dapper→Npgsql command/connector→server | Korda frontend P,D(statement),S,B,D(portal),E,S; Dapper P,B,D(portal),E,S. Korda4 libpq submissions are not4 round trips | Same Parse SQL hash, same1000 DataRow messages/30912 B. Korda wire difference only+71 B/query in this case. Direct actual poll calls2/query across1–1000 and batch probes | Fresh DDL shape; no Execute before metadata validation; parameter ownership; ReadyForQuery before reuse | Preserve metadata barrier. Evaluate libpq result allocation independently; protocol byte volume is not the thousand-row CPU explanation |
| Actual PG waiting / PostgreSQL | Direct native wait_for poll spans, thread CPU and TID; libpq PQisBusy/input consumption | Direct hot1000/B32 poll2/query; early-stop3. Proxy1000/B32 poll299.25/query is observer-disturbed | Direct diagnostic total poll wall245.8 µs/thread CPU16.8 µs per hot1000. Proxy microseconds are excluded from original-path attribution | Cancellation, drain, connection poisoning and transaction-unknown outcomes | Use direct timing for stage interpretation; use proxy only for message order/bytes; no RTT inference from API counts |
| Engine advance and columns / SQLite | sqlite3_step, sqlite3_column_type/int64/text; native advance/column preflight/codec |1000-row full:1001 advances,4000 column-type checks,1800 nonnull codecs. Cancel.install1002. These remain unchanged atB32/128/256 | Full engine work is equivalent; Korda adds repeated per-row/per-column control. Early-stop is different engine work: Korda32 steps/VM204 versus Dapper1 step/VM18 | Dynamic SQLite storage type, NULL, conversion/column validation order, cancellation between rows | Measure any removal of duplicate control at the exact source site and retain dynamic-type tests; do not normalize unlike early-stop engine work |
| PGresult and columns / PostgreSQL | PQgetResult/PQclear; native advance/column/preflight; libpq single-row mode |1000 SINGLE_TUPLE results,1001 advances,1002 Cancel.install and1004 provider PQclear/query;2000 cell scans |32-row text public allocator: Korda181.039 calls/123871.56 B; Dapper0 public-allocator calls in this warm scope (managed allocations separately reported). Result-object cost is a concrete candidate, not yet a causal result | Preserve row/error order, cancellation, borrow lifetime and complete drain before pool return | Evaluate pinned libpq chunked-row support as one native-only experiment, keeping logical batch/SQL/metadata contracts |
| Native frame/batch / both | BatchWriter::append/finish, actual native symbols and debug lines |1000 rows:32/8/4 batches forB32/128/256; native worker tasks34/10/6. AtB32,2000 finish-cell scans and1800 nonnull offset rewrites | Payload/canonical writes15912 B; only124 B partial-batch memmove. B32 growth-copy0. Larger batches add53752/58352 B vector-growth copying yet reduce handoffs | Failure-atomic row/byte quotas, no eager unvalidated lookahead, canonical offsets/empty cells, native ownership | Do not claim huge batch copying. Full-batch redundant offset rewrite is a separately measurable low-impact fallback |
| Native queue→ready→managed take / both | Native task enqueue/worker markers30/31, ready51, managed take52; HostPullController/CoordinatedCallback | Thousand-row B32 has32 deliveries; B128/256 has8/4. Exact32 emits[32,0], hence2 pulls | SQLite hot1000/B32 diagnostic mean pull-queue38.2 µs and ready→take36.5 µs/batch. PG direct corresponding totals827.6/982.9 µs/query; B128/256 ready→take271.9/148.9 µs. These intrusive spans explain ordering, not ordinary cost totals | Exactly one completion/generation; no cookie/native/control access after publication; no late cancel into next generation; safe concurrent Dispose | Highest-priority experiment: publish completion only after coordinator scheduling tail is finished, then avoid the unnecessary asynchronous continuation hop when safe |
| Managed row/list materialization / both | Actual generated PhaseRow readers; TypedStream.Enumerator, RowBatchLease, WireLayout.Cell; sampled Monitor/validation leaves |1000 generated mapper calls and list appends on both; Korda row/column lifetime checks remain | Actual instrumented mapper scope69760 B/query both SQLite paths and Korda PG; Dapper PG69789.625 B. List constructor8056 B, Add0. Mapper includes codec/driver scratch; framework-only remains null | Borrow held through arbitrary mapper; validation before reading; concurrent Dispose cannot free borrowed memory; buffered quotas before mapper | Keep matching generated-reader comparison. Optimize batch-local mapping only if its own CPU/count evidence and lifetime proof support it |
| CPU scheduling/spin / both | Actual ELF RhSpinWait, LowLevelLifoSemaphore.WaitAsWaiter/Wait, runtime config parser and inline machine code | Validated sampler with zero reported loss across recorded channels; warm leaves: SQLite Korda about59%, PG Korda about51–53%; Dapper PG about34%; SQLite Dapper no dominant spin | Two ordinary identical-ELF interleaved sensitivity rounds: SQLite Prepare CPU3655/3811→2087/2037 µs with spinlimit0, p50 essentially unchanged. PG CPU4105/4666→2845/2878 µs, latency not consistently better | Runtime default remains default for product and final acceptance. Leaf sampling alone cannot assign every spin to ThreadPool or prove lock cause | Confirms substantial spin-setting-sensitive CPU without a consistent end-to-end latency reduction; reduce application handoffs, never ship a global runtime knob as claimed product parity |
| EOF, early stop, close and return / both | Native close/drain, HostCursorCloseController, TypedStream cleanup; Dapper reader disposal/provider reset | Exact32 consumes an extra EOF batch. SQLite stop1 executes32 versus1 steps. PG both still receive1000 DataRows on stop1; Korda adds Sync and direct poll3 | All diagnostic and ordinary correctness oracles passed, Korda exposed owners0. Close/control work is query-fixed, plus early-stop drain | Drain before safe connection return; Unknown after COMMIT confirmation loss; no hidden retries; preserve failure and cleanup ordering | Retain early-stop/EOF/race regressions for every selected change; do not repeat rejected quiet-close or unsafe inline-completion patches |

The answer to “who works and who waits” is therefore specific: Dapper SQLite
executes synchronously through provider/SQLite on the caller (all314 verified warm
samples on one TID), while Korda runs engine/batch work on native workers, queues
a managed coordinator and currently schedules continuation delivery again. PG
adds actual network waits on both paths, but the direct Korda wait count stays2
while native single-row objects, row controls and32 batch handoffs amplify with
1000 rows. Queue/ready intervals and per-thread CPU corroborate this structure.
Poll spans enclose actual poll calls; they do not prove every call slept or isolate
kernel-blocked time. Global runqueue cause, kernel instructions and exclusive CPU-cycle ownership are
still unknown; the measured evidence does not silently fill these fields.

## Coverage beyond the narrow SELECT

The original manifest SHA256
`76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2`
retains all35 business kinds. `measurements/case-baseline-01` contains35 prepared
cases plus7 dynamic construction cases for each provider/implementation:168
processes,128 measured operations each,32 warmup each, no failures, oracle errors
or retries. Dynamic cases cover optional-filter, left-join, customer-totals, wide,
JSON, transaction commit and partial update. Every Korda process exposed owner0.
`measurements/native-allocation-baseline-01` separately contains140 instrumented
per-case processes; all allocator coverage/conservation/identity checks passed.

Representative ordinary client CPU µs/business (Korda / Dapper): SQLite numeric
358.48/38.63, wide695.96/119.97, aggregate712.39/290.65,
transaction commit3766.41/233.20; PostgreSQL numeric470.89/108.33,
wide678.53/222.15, aggregate535.18/156.09, transaction commit2614.62/853.80.
These are short closed-loop decomposition measurements, not sustainable mixed
capacity, and not equal to a prior concurrent offered-load allocation population.
The mature write/transaction source and correctness contracts remain in the source
audits and original regression suite. Detailed per-instruction allocation-stack
ownership for every business type is not proved. No such claim is needed to test
the shared, already observed batch-completion hypothesis.

## Go as an attribution control

`analysis/go-attribution-control.md` pins the actual Go1.27.4, go-sqlite3v1.14.53
and pgxv5.11.0 sources and unchanged draft evidence. This go-sqlite3 version uses
combined step/column and bind/first-step helpers, reusable argument/column buffers,
and retained worker read statements; its handwritten Scan is a different mapping
path from both generated C# readers. Its eager step and post-step reprepare
metadata behavior cannot be copied over Korda's metadata-before-effects contract.
The historical222,218,466 cgo calls/2992.478 successful business operations per
second are a mixed-workload observation, not a normalized count for this query.
Go pgx Exec uses its own buffered Go protocol with text results; it is not a libpq
control. Existing long Go runs are reused, the two Go drafts stay unchanged.

## Evidence quality and unknowns

The self-thread sampler build03 verifies raw binary→JSON decoding, all retained raw records/TIDs/clocks and available file-backed ELF bindings,
load bias, sized symbols/actual machine code and observed thread coverage,
all ring/output/marker counters and PERF_FORMAT_LOST. All four validated sampled
phase runs have zero observed losses. Earlier CLI empty output and build02's missing lost-readback remain incomplete
attempts. Deliberate overflow/unregistered-thread negative controls passed by
detecting the expected gaps. Native ordinary provider DSOs have no GNU BuildID/DWARF;
actual SHA256+maps/native receipt bindings are used, not invented symbol identity.
Some Npgsql/runtime DWARF source lines are invalid fallbacks; those line numbers
are unknown even where sized symbol/machine-code identity is sound.

Native allocator measurements cover interposed public glibc calls across process
threads and exclude private mmap, hidden allocator internals and the managed heap.
The fixed profiler table is reported separately. Managed mapper scopes include
codec/provider scratch and cannot be subtracted to produce pure framework0 B.
Whole-process GC counts/pauses retain process scope. Peak RSS and released RSS
will be reported with the ordinary sustained campaign, not instrumentation RSS.

## Ranked experiments and Stage 2 entry

1. **Common completion scheduling:** the generation-specific completion value
   must remain local to one Execute invocation. Finish dirty/scheduled bookkeeping
   and necessary rescheduling before the final publication call. Publication must
   be outside SchedulingFault catch and followed by no controller state access.
   Inline consumer/SyncContext exceptions must not corrupt the old or next
   generation or cross an unmanaged callback. Keep bounded scheduling, rejection
   retry, disposal/borrow, duplicate-generation and held-Post regressions. The
   detailed independent review is `analysis/common-candidate-review-01.md`.
2. **SQLite statement allocator setting:** only remove PERSISTENT for per-query
   finalized statements; keep v3, SQL, automatic reprepare and all metadata rules.
   Test malloc and lookaside counters and endpoint costs independently.
3. **PG native result granularity:** assess pinned libpq chunked rows, measure
   actual PGresult creation/clear and allocations, keep logical batch admission,
   first-row behavior, drain/error/cancellation semantics. Source possibility alone
   grants no performance acceptance.
4. **Repeated frame/row work:** if residual CPU remains measurable, isolate full-
   batch offset rescans, repeated cancel installation and built-in codec temporary
   allocation, each with its own count/byte proof. Do not bundle unrelated changes.

Each experiment gets a separate source/binary identity and same-host interleaved
ordinary A/B, plus diagnostics confirming the intended mechanism. Reject a
candidate if contract safety is lost, benefit reverses repeatedly or is within
noise. Product remains runtime-default. Preserve the original batch32 business
contract for acceptance;128/256 diagnostics are not hidden workload substitutions.
Normal correctness, public API and real independent NuGet AOT consumption follow
the selected implementation. All performance execution stays local; no CI edits
or indirect performance invocations are authorized.

Pending: implementations, adequate same-condition mixed before measurements,
zero-rejection cost, pressure ramp/historical arrival comparison, frozen candidate,
four serial ordinary1800-second cells, independent review, normal merges, existing
CI/release and public NuGet AOT readback. Current final credit remains **0/4**.
