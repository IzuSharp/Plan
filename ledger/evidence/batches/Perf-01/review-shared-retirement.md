# Perf-01 shared retirement source review and regression strategy

Scope: independent source review by the database task owner. The integration
owner executes profiling, selects runtime changes and owns formal timing.
Reviewed product behavior is the unchanged baseline
`ea5fa528035d025bd7a28698ee7c71194432236c`; the integration test snapshot was
`d252fc589d1559b7cdbb907c2dfa25bc7ea8c2ef`. No runtime change was made by this
reviewer. The strategy below is a candidate pending measured validation.

## Evidence and precise interpretation

The integration owner executed `tests/Perf01.Shared/RetirementProbe` against the
baseline package, pinned to CPUs 2 and 3. The retained result is
`/workspace/scratch/01c249676f47/perf01-evidence/profiling/before/shared-sqlite-001.json`,
SHA-256 `f3bc102e9a5e1639221ded1958834c5ce26613b6c73bc1c5cfd3f80df150dbad`.
This reviewer read the result: 1,000 public scalar calls, 4,000 observed native
operations and `SourceReleased=true`. The integration owner reported a public
mean of 1.195915 ms, take-to-retirement mean of approximately 0.15414 ms and
64 of 4,000 take-to-retirement intervals above 5 ms. These are instrumented
profiling observations, not the formal before/after cohort.

The `Retired` timestamp is taken in `DataSource.Complete` **after awaiting** the
operation's retirement task (`src/Data.NativeHost/DataSource.cs:77–87`). Therefore
the measured take-to-retirement interval contains result mapping, native/managed
retirement work and asynchronous continuation scheduling. It is not an exact
native-retirement wait or a direct count of `Pending` responses. The scalar loop
keeps one session open; physical session acquisition and pool waiting are outside
that loop. Start-to-terminal includes the native engine path and I/O, rather than
isolated SQL execution.

The observer's serial discipline is consistent with the source's await chain.
Useful additional diagnostic checks are nonzero boundary timestamps and:

- `StartReturned >= Start` and `Terminal >= Start`.
- `BeforeTake >= max(StartReturned, Terminal)`.
- `Retired >= BeforeTake`.
- The complete `AsyncSnapshot` assertions used by the existing A07 `Finish`
  helper: setup settled, registration ready/drained, result processed, native
  quiet, released, no live root/quarantine/controls/callback entries/input bytes.

A terminal callback can legitimately occur before `StartReturned`; an ordering
assertion forbidding that would reject the supported synchronous-completion
contract. The count of four native operations per public scalar is observed
data, not an invariant that a future optimization should be forced to preserve.

## Why a retry delay is possible

| Source location | Observation |
| --- | --- |
| `native/database/host/src/operation.rs:170–188` | An asynchronous database operation calls `complete` while retaining its `WorkLease`, then drops that lease. |
| `native/interop/async/src/lib.rs:129–151` | Terminal status/result commit precedes the callback. A native callback lease remains live until callback delivery returns. |
| `native/interop/async/src/lib.rs:181–194` | Native retirement returns `Pending` while either callback entries or source leases remain. |
| `native/interop/async/src/lib.rs:220–237` | Callback/source lease destruction decrements native counters; it sends no new managed wake. |
| `src/Interop.Async/AsyncOperation.cs:521–530` | A `Pending` retirement response requests retry. The temporary cleanup control releases with `notify:false`. |
| `src/Interop.Callbacks/CallbackCoordinator.cs` | `RequestRetry` sets `_retry`; the current work-item tail reschedules only `_dirty`. Without another real signal, the fixed coordinator timer is the next opportunity. Its default interval is 10 ms. |

This provides a source-defined explanation consistent with the observed tail.
It does not prove that every long sample encountered `Pending`; that value
remains unavailable in this unmodified package probe. A permitted profiler
observing return values of the exported
`nw_db_operation_try_retire_v1` could measure it separately, but no such result
is claimed here.

## Minimal candidate and nonnegotiable invariants

Start with **one extra queued attempt per retiring context**, only after a real
`RequestRetry`. Mark the existing dirty state under the existing scheduling gate
and retain the timer fallback. Do not reset the immediate budget on every signal
or timer tick. Avoid an inline recursive `Process`, an unbounded polling loop,
new per-retry tasks or a globally shorter timer. The chosen budget is a proposal
to measure, not a promised performance gain.

The implementation must preserve these facts:

1. A context has at most one admitted work item. `_dirty` and `_scheduled` are
   rechecked atomically at the current work-item handoff; genuine concurrent
   signals must never be lost or suppressed by an exhausted retry budget.
2. Scheduler rejection or a pre-acceptance exception keeps pending work rooted
   and retryable. A rejected immediate attempt falls back to the existing timer.
3. Setup settlement, cancellation-registration drain and live control leases
   still gate processing. Cancellation does not select an application outcome
   before the native terminal result, and first terminal/take remains once-only.
4. Successful task publication does not establish quiescence. Native `Ok`,
   processed result, drained registration, zero controls and zero callback
   entries remain required before owner/input/root/coordinator-slot release.
5. Non-`Pending` retirement errors and indeterminate setup remain quarantined
   and poison ordinary admission. They must not report retirement success.
6. `CompleteScheduling` prevents later signals/timer attempts from creating new
   work. Closing a coordinator keeps existing contexts rooted until actual drain.

A change in the shared scheduling base also affects `CallbackRegistration`
(`src/Interop.Callbacks/CallbackRegistration.cs:319–378`). Its native quiet,
active-handler, pending-item and retained-byte release conditions must remain
intact; A06 regressions are required alongside A07 and affected domain checks.

## Deterministic regression recipe

Use the existing real native A07 fixture, a coordinator interval of one minute
and `ManualScheduler`. Tests should establish ordering and bounded work counts,
not rely on a stopwatch threshold or a favorable thread schedule.

1. Start a normal operation, retain a real `SourceHandle`, and commit completion.
   A test-only `FixtureCalls.AfterRetire(status)` hook releases the source only
   after the first actual native `Pending` return. That source drop sends no
   managed signal. Run one scheduled work item and verify that result publication
   did not release root/input/slot. One follow-up item must now exist. Running it
   must retire with exactly two probes, one take and one release; maximum queued
   items remains one. The original implementation cannot pass without a timer.
2. Retain the source through all allowed immediate attempts. Running the manual
   queue must stop at the finite attempt cap, with retirement incomplete and
   ownership retained. Release the source, explicitly call `Retry` to simulate
   one coordinator tick, then verify genuine successful retirement.
3. Reject, and separately throw before accepting, the immediate follow-up queue
   attempt. Verify retained ownership, one rejection count and recovery on an
   explicit later `Retry`, without a spin or fabricated release.

Retain the existing `LostWakeRegression`, `ResultBeforeNativeQuiet`, cancellation
registration drain, duplicate/take failure, retire-fault quarantine, rejected
scheduler, discarded-task and A06 active-handler/stalled-worker checks. They
cover distinct safety boundaries and must not be replaced by a timing assertion.

## Database attribution beyond the boundary

The new harness producer at NativeWeave commit
`2f20b2f628d2bb4ada88478a53dccc971247d264` adds
`tests/Perf01.Database/profile_postgresql.py`. It is source-prepared only by this
reviewer: syntax/help checks and a synthetic log/wait-parser check passed; no
PostgreSQL or application load was started by this task.

It reuses the existing private PostgreSQL 18.0 supervisor and exact package
application, preserving fsync, synchronous commit and full-page writes. The
profiling-only cluster enables statement-duration logging, records Parse/Bind/
Execute separately and samples `pg_stat_activity`. Raw logs and observer query
start/end timestamps remain available. Statements from the independent psql
oracle are excluded from application aggregates. The output is always marked
ineligible for formal timing because the observers add overhead.

Server elapsed time includes waits; sampled activity is not an exact per-request
lock duration. Concurrent SQL durations cannot be subtracted from application
wall time to infer boundary overhead. Exact NativeWeave admission/SQLx pool-wait
durations, SQLite SQL execution/lock durations and pure database CPU remain
unavailable. PostgreSQL source documentation was read from the pinned 18.0
`doc/src/sgml/config.sgml` and `monitoring.sgml`. SQLite's locked SQLx
`connection/establish.rs:177–184` installs `sqlite3_busy_timeout`: application
retries are zero, but internal busy-handler attempts are unobserved and must not
be reported as zero.
