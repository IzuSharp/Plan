# Worker-D — completed execution-boundary and count audit

Task: `DB-Exec-Parity-01`. Diagnostic only. **No ordinary CPU, latency, allocation,
RSS, throughput or final mixed35 acceptance credit.**

## Recovered scope and identities

The earlier interruption left more local work than the published Plan checkpoint
described. Existing `observations/worker-d-diagnostic/counts-sqlite-01` and
`counts-postgresql-01` each contained six successful diagnostic processes. These
are retained and analyzed. Recovery 04 discovered them after launching a new
finite observation, so the new 12 processes are explicitly separate corroboration,
not claimed as newly missing coverage. There is no need to rerun these cells.

All 24 processes use the same four actual Native AOT diagnostic consumers in
`consumers/worker-d-diagnostic/{baseline,candidate}-{sqlite,postgresql}`. Each
process has two measured businesses, following an initial execution and two
warmups. The consumer runs public Fluent hot Prepare, the original generated
`PhaseRow(long Id, string? Note)` reader, original SQL/parameters and complete
Id/Note/null oracle. Early stop maps one row and then explicitly disposes its
cursor; it does not claim to reach EOF.

| Diagnostic source | Exact source commit | Product input |
| --- | --- | --- |
| Baseline | `47aaa0f67cb6867360155d327a6c363bfc4b2669` | unchanged main `7ff7b57b907b689defb880b8af62d83679608603` |
| Candidate | `1a95ed315337582243803ce95c54750a75311051` | isolated Worker-D `5844c3035bfd9b678c39a5c6a8150f8e2de5f48c` |

| Native library | SHA256 |
| --- | --- |
| Baseline SQLite | `08d051bce3e6921118a3b0aae69b852977ce9a3c3829290d2b44f66c46f1f950` |
| Candidate SQLite | `8b2448d1375ad9d44d1e3a0180b04b5b9eb47978ed2673d470b1c4c9f3ed84b9` |
| Baseline PostgreSQL | `4c43ae6159c341953cf4b80299396f5ca40c74ebad0c7ecd2ceb2d76727a7861` |
| Candidate PostgreSQL | `96bbf7ea29afa373ffc8330c5d3914c8f4713ed57410956a34970375c4da1ea1` |

`summary.json` binds every actual loaded native file to its package bytes, runtime
module/BuildID, current hash, AOT ELF and matching split debug information. It also
checks the consumer and generated C# input hashes. `machine/manifest.json` binds
22 optimized native symbols to the actual diagnostic ELF, source locations and
`objdump -d -C -l` output. This is code/boundary binding, not a sampled hotspot.

## Actual per-business counts

The following values repeat across both databases and both recorded observation
batches. There are four measured businesses for each database/case/variant.

| Business | Rows materialized / batches actually built | Native run / ready / take, each | WorkerPool accepted posts, baseline → candidate | C ABI entries, baseline → candidate | Encoded batch bytes, both |
| --- | --- | ---: | ---: | ---: | ---: |
| Complete 1,000 rows | 1,000 / 31 × 32 + 8 | 32 → 32 | 34 → 2 | 104 → 136 | 68,008 |
| Exactly 32 rows | 32 / 32 + 0 | 2 → 2 | 4 → 2 | 13 → 15 | 2,274 |
| Early stop after one mapped row | 1 / one native batch of 32 | 1 → 1 | 3 → 2 | 10 → 11 | 2,146 |

Each measured business still executes one SQL statement. Candidate admission,
original native run, batch-build, readiness, take and Worker retirement all have
the same expected generation count. No unexpected abandon is observed.

Every baseline pull posts one work item to the native Source workers pool.
Worker-D instead prepares the admitted obligation, runs it synchronously from an
already admitted managed work item and takes the result after run returns. This
removes exactly one native worker post per batch. Two native posts remain in
every measured business: one workers-pool cleanup and one controls-pool final
close. The observer labels pools using their actual process-local addresses.

**FFI count increases.** Baseline uses request + take per batch; the candidate
uses prepare + run + take. Full1000 therefore adds 32 actual C ABI entries while
removing 32 native posts. The performance hypothesis is the cost of the native
queue/handoff and work-item representation, not the total number of foreign
calls. Both full1000 variants make only one `nw_db_cursor_pull_check_read_v1`
entry, at final EOF admission; the recorded path does not make that FFI call
once per row. `ffiByEntry` in `requests.json` preserves all entries, including
the cleanup buffer, cursor close and owner release.

Managed scheduling is not eliminated. Full1000 records 33 offers/executions in
all candidate businesses, and 33 in all but one SQLite baseline business (34).
Exact32 normally records three, but one old SQLite candidate business coalesces
to two. Early stop records two on both sides. These are actual coalescing and
notification outcomes. Do not infer one fixed managed-item reduction from source
structure or ignore the extra observed baseline item.

## Ordering and ownership evidence

For each candidate generation, the markers prove the following actual order:

1. Prepare is accepted and the managed scheduler accepts its work item.
2. The original `CursorPull::run` executes inside the exported prepared execution
   frame on that managed work item's thread.
3. Native readiness occurs. The native run and Worker retirement complete, then
   the exported run frame and the managed `RunReturned` boundary return.
4. The same managed work item reaches `BeforeTake` and the actual native take.

Every candidate run/take pair is enclosed by one actual admitted managed work
item. No run frame overlaps a synchronous `MoveNextAsync` invocation on the same
thread. Same-thread reuse after a MoveNext call returns is permitted; different
thread IDs are not used as a substitute for the never-inline contract.

Every process finishes with Sources, Sessions, Operations, Cursors, Buffers,
Owners, PullChannels and CommandCompletions all zero. All selected operations
retain the full row/field/null oracle. These observations supplement the existing
correctness suites; they do not replace cancellation, queue refusal, forced
close, failure precedence or retirement-fence regressions.

## Engine work and PostgreSQL wire scope

SQLite's full1000 example retains prepare-v3 1, bind-int64 2, step 1,001,
column-int64 1,000, column-text 800, column-bytes 800, finalize 1, and identical
dynamic-type/other engine observations. The 68,008 output bytes do not fall.
`nativeCounters` preserves all counters instead of selecting only favorable
ones. Some counter IDs are generic provider calls shared across providers; read
their source maps rather than classifying every ID ≥300 as PostgreSQL-only work.

In every PostgreSQL full1000/exact32 measured business, both variants observe
Parse 1, Describe 2, Bind 1, Execute 1 and Sync 2. Both observe the expected 1,000
or 32 DataRow messages. Early stop retains Parse 1, Describe 2, Bind 1, Execute 1
and Sync 3, including close/drain, and the server still sends 1,000 DataRow
messages. One mapped row and 32 native fetched rows therefore do not imply only
32 rows of server/protocol work. These observations do not assign proxy arrival
delay to client wait or infer a physical network RTT count.

## What is visible about CPU and waiting

The marker stream records monotonic and raw-clock time, OS TID, thread CPU,
counts and bytes. `requests.json` retains paired native admission/run/build/
retirement and managed-item/MoveNext scopes for each request/generation. CPU
deltas are calculated only within the same thread. These intervals overlap and
nest: a candidate managed-item interval contains its synchronous native run.
Their CPU values must not be added as exclusive components, and wall minus CPU
does not uniquely identify scheduling or protocol wait.

The independent raw decoder reproduces every saved perf record. There are 17,713
self switch records within the 48 measured business intervals, all registration,
loss, buffer, marker and observed-thread coverage checks passing. These records
show a process's own switch-in/out events; they do not identify a wakeup source,
global runqueue competition or kernel instruction cost.

The intentionally sparse 100 ms sampling period collected **zero leaf samples
inside these finite measured businesses**. It is plumbing for complete boundary
and count collection, not a useful CPU profile. This audit supplies no new
`RhSpinWait` attribution and does not explain the ordinary money1 CPU regression.
The earlier ordinary-ELF money1 sample has no callchains and its native-library
category excludes C++ work executing in libc/libcrypto. Those limits remain.

## Validation and retained failures

`summary.json`: **24 processes, 48 measured businesses, 2,510 checks passed**.
No result or validator was weakened to pass a failed experiment.

The recovery-04 first attempt preloaded the sampler into `taskset`, which created
the fresh trace directory before exec. The target consumer then correctly refused
to overwrite that directory and emitted no manifest. Its result/owner receipt
passed, but the trace has no coverage credit. It is retained in
`../counts-recovery-04/failure.json`. The new runner places `LD_PRELOAD` in an `env`
command after `taskset` has started, leaving fresh-output-only behavior intact.
The successful new batch is `../counts-recovery-04-attempt-02` with client CPUs
0–3, PostgreSQL CPUs 4–7 and observer CPU 8. Concurrent builds were permitted, so
pinning grants no ordinary timing credit or host-exclusivity claim.

The first analyzer incorrectly paired phase712 MoveNext boundaries by generation;
a call can advance generation internally. Its 48 failures and exact analyzer
source are retained in `../analysis-recovery-04`. Pairing now uses the unique
call ID and same TID, requires both boundaries and retains all negative-delta
checks. The recorded failed analyzer is not a product/test failure.

## Next boundary

The previously pending Worker-D exact post/run/take mechanism observation is
complete. Supported product selection can now combine this mechanism with the
separate uninstrumented reverse-A/B results and correctness receipts. Existing
short ordinary screens still show a large thousand-row CPU gap to Dapper.

No Worker-D + decimal combined consumer or measured integrated identity was found
in the recovered consumers inventory. The next ordinary selection gate must
measure that actual combination, especially PG money1, rather than adding isolated
percentage savings. If CPU sampling is needed, root should reserve a quiet window
for the current ordinary ELF and bind thread roles/call sites; these marker-heavy
executions cannot supply that result. Final mixed35 remains outside this audit.

For persistence, retain the two original observations, the new successful and
failed output directories, the diagnostic source commits/patches and all four
consumer ELF/.dbg/native/package inputs along with this analyzer and report.
