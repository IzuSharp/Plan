# Measured intermediate candidate and final-close decision

## Executed observations

Public product source
[`0f3816c4006488821f40afde91bbbd717d57ccd6`](https://github.com/IzuSharp/Korda/commit/0f3816c4006488821f40afde91bbbd717d57ccd6)
was built into both independent provider packages and external Release Native AOT
consumers. Its existing full CI passed. The immediate before product is
[`f0078da720e07031bc56464995af6791c41aaae8`](https://github.com/IzuSharp/Korda/commit/f0078da720e07031bc56464995af6791c41aaae8),
rebuilt here with the same locked dependencies and current observation harness.
All observations below are new local Linux x64 executions. They do not reuse the
historical final long-test cells.

The ordinary campaign completed 18 commands: before, candidate and Dapper.AOT,
for each provider and each 1/100/1000-row result. Every Korda route used 256
operations in each of three rotated windows, with identical complete DTO lists,
ordered values and NULL checks. Dapper's actual contract receipt hashes match
the corresponding candidate bytes. The six SQL/result cohorts passed the
comparison checks. Every Korda source/session/operation/cursor/buffer/owner
counter drained to zero; the supported candidate pull-channel counter also
drained to zero. All command exits were zero with no observer errors.

The [phase analysis](analysis/phases-analysis-01.md) and its JSON preserve all
routes, raw allocation totals, process-wide window GC, CPU, RSS, stage durations,
first executions and percentile calculations. Selected prepared-route results:

| Provider / rows | Before | Candidate 0f | Meaning |
| --- | ---: | ---: | --- |
| SQLite / 1000 | 41,098.31 us | 2,012.43 us | Four-stage total p50 |
| SQLite / 1000 | 111,749.98 us | 9,645.23 us | Four-stage total p95 |
| SQLite / 1000 | 6,457.70 us | 4,246.11 us | Process CPU per operation |
| SQLite / 1000 | 99,809.07 B | 81,194.49 B | Raw process allocation per operation, including result and harness |
| SQLite / 1 | 11,981.15 us | 208.37 us | Submit-to-first-row p95 |
| PostgreSQL / 1 | 883.04 us | 425.63 us | Submit-to-first-row p95 |
| PostgreSQL / 100 | 20,744.69 us | 1,806.88 us | Read-through-EOF p95 |

These are three-window observations on this host, not universal speedup claims.
The low single-row before PostgreSQL p95 also demonstrates why a selected
median or one tail percentile cannot replace the complete distributions.

The separate ABI diagnostic completed 12 commands. For SQLite prepared queries,
the actual managed-to-native call counts per operation were approximately
34.35 -> 16.95 for one row, 58.96 -> 23.77 for 100 rows, and 286.08 -> 108.05
for 1000 rows. Counter reads are outside the windows. Candidate request/take
counts were exactly 1, 4 and 32 per query; the read-admission call was once per
query. No candidate batch used a generic operation. Final close still used
0 or 1 generic operation, depending on the existing safe-snapshot fast path.
Provider `poll` attempts are OS waits, not protocol RTTs; SQL executions and
protocol submissions remain separate raw fields.

The allocation campaign completed 18 commands in separate instrumented
consumers. Actual generated mapper and List constructor/Add scopes consumed
136, 7,256 and 77,816 bytes per operation for 1, 100 and 1000 rows in the
SQLite routes and Korda PostgreSQL routes. Dapper/Npgsql's 1000-row mapper/List
scope averaged 77,892.09 B/op. Its extra observed 76.09 B/op cannot be called a
DTO-size difference: mapper scope includes any scratch inside the actual
generated body. It is not a live-object-size estimate. `FrameworkOnlyBytes`
remains null. Instrumented timing never enters the ordinary timing tables.
The raw whole-process allocation still includes all framework, driver, result
and harness work, so framework zero has not been demonstrated. Separate
[independent allocation audits](allocation-audits/index.json) bind both
providers' 63 windows, each with 16,128 operations and exact mapper/List counts.

## Why implementation continues

Candidate 0f still has an observable final-cleanup tail. For the prepared
single-row query, SQLite read-through-EOF p50/p95/p99 was
48.99/7,583.75/11,693.39 us, while PostgreSQL was
58.82/9,362.86/11,521.09 us. Release-after-EOF itself was short: cleanup already
occurred inside the final `MoveNextAsync` that returned false.

The actual path is `TypedStream.CleanupAsync -> HostStreamTransport.JoinAsync ->
CloseController -> DataSource.Complete -> AsyncOperation.Retirement`.
`AsyncOperation.Process` sets `RequestRetry` after native `try_retire` returns
Pending. Once the terminal notification has ended, no new notification is
required when the independent native tail finally becomes quiet. The remaining
retry is therefore the coordinator's default 10 ms timer. This is a concrete
source-confirmed waiting mechanism, although the uninstrumented raw receipts do
not timestamp native quiet and cannot assign every long sample to it. The ABI
diagnostic observed 15 Pending retire returns across 192 candidate prepared
single-row operations, with 165 actual final generic close operations.

The next implementation decision is to **replace normal cursor final close**
with a separate once-only close-ready protocol. It reuses the existing 24-byte
ready callback record and frozen cleanup snapshot/error encoding. Two private
extension exports request close and take its snapshot; callback generation 0
is reserved for close, while ordinary fetch generations remain positive.
The existing error take with generation 0 reads a distinct close-error state.
The original 42-function ABI and generic operation quiet semantics remain intact.

The native close worker must join earlier fetch work and cursor cleanup, freeze
its result, release all channel/cursor/Source accessors and its reservation, then
publish one detached ready notification. Its remaining channel and Source tail
fences complete after the callback. Public generic channel join and snapshot
also include the new notification tail, so a cold fallback cannot certify a
still-live callback cookie. The close worker uses a private resource-only join
and snapshot to avoid waiting for its own notification.

A separate managed close controller owns its once-only callback root, setup,
control and callback-entry drain. This keeps an accepted fetch and an overlapping
forced close as independent obligations. Normal final close creates no generic
operation. A request rejected before acceptance, including Source admission
already stopped, may use the existing trusted generic cleanup as a cold fallback.
Indeterminate acceptance retains its root until real notification or a complete
native join proves safety. Error, cancellation, early-stop, parent-close and
Source-join guarantees must pass deterministic tests before new package timing.

Task-marked `DB-Exec-03-close-*` worktrees are subordinate implementation work
for this same DB-Exec-02 continuation. The change was selected from the measured
remaining cost; it is not accepted merely because it was designed. The final
four continuous 1800-second cells remain **0/4**. Calibration, matched before
mixed load, final package measurements, final review and ordinary eligible
merges remain pending. No benchmark work was added to CI.

## Recovery and evidence boundaries

[observations-0f3816c.tar.gz](observations-0f3816c.tar.gz) contains all six
ordinary/ABI/allocation observation directories, plans, raw command/resource
receipts, host observation, before/after input hashes and diagnostic consumer
sources/provenance. Its [manifest](observations-0f3816c.tar.manifest.json) binds
661 source files and original outputs; every archived byte was read back and
verified. The raw fixture databases are deterministic and omitted. Exact binary
hashes are retained; binaries must be rebuilt from their recorded package/source
inputs if the current workspace is lost. The ordinary generated sources are in
the separate [consumer archive](consumer-inputs.tar.gz).

All 53 ordinary build-receipt, ELF/native/support-image inputs were rehashed
after the entire campaign and were unchanged. Client processes were pinned to
CPUs 0-3, PostgreSQL to 4-7, and the observer to 8. Builds/tests were stopped
during these serial observations. The available Linux namespace did not expose
a cgroup mount: this record does not invent a cgroup quota observation or claim
an exclusive physical host. Raw CPU/load/resource samples preserve that limit.

To recalculate on a restored workspace, extract the observation archive, then
run `analysis/prepare_phase_index.py --measurements-root RESTORED/measurements
--host-record RESTORED/measurements/host-before-phases.json --output NEW_INDEX`
and `analysis/analyze_execution.py --index NEW_INDEX --korda-root EXACT_0F_SOURCE
--output NEW_ANALYSIS.json`. Existing outputs are immutable; use fresh paths.
The Dapper receipt's embedded original contract paths are retained as provenance;
the analyzer resolves paired receipts from the newly prepared index and checks
their exact hashes.
