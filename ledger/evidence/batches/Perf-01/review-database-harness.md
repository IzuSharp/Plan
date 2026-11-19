# Perf-01 independent database harness source review

Reviewer: protocol agent, independent of the database harness author.
Scope: read-only review; no database workload, profile or build was run by this
reviewer. Product source remains baseline
`ea5fa528035d025bd7a28698ee7c71194432236c`.

Reviewed harness lineage:

- `54660113015771c89fbcfabfadc5f993cf487a62`: initial database application adapter.
- `c57a684eb55faeade60270981773bd15133e4f53`: fresh locked comparison artifacts.
- `a585ba0f82236f4b7f64c2b25c459574b0862553`: independent persisted counts on failure.
- `fc97d2fe56b8501b008d2114a8fc5f7de3859ddd`: continued classified overload policy,
  read before commit and then bound to the author's supplied commit.

## Findings and disposition

| Item | Source basis | Review conclusion |
| --- | --- | --- |
| Equivalent initial state | `tests/Perf01.Database/target.py` derives from the B23 Target; seed calls the unchanged 128-row initializer. `run.py` fixes seed, scenario mix, rate, concurrency, warmup and a new database per target. | Suitable for same-fixture before/after cells. Root still must bind exact packages, database durability and machine/CPU policy. |
| Whole-application correctness | `src/Benchmarks.Domain/http_target.py:391–486,540–568` validates complete typed response/business cycle and then independent persisted scope/hash/status/response bytes, outbox and item cardinality. `run.py` supplies A21 expected values. | Correctness oracle was reused rather than replaced by a checksum of driver inputs. Successful cycle throughput is distinct from create mutations that committed before a later cycle failure. |
| Actual durable volume on failed cells | `PerfTarget.persisted_counts` independently SELECTs operation keys and item/outbox rows, classifies seed/warmup/measurement/recovery prefixes, and records before recovery and shutdown. | Useful, truthful committed-volume evidence even if exact B23 cardinality later fails. This does not upgrade a failed business cycle to a success. |
| Open-loop duration | `run.py:94–108,186–203` preserves A21 scheduling, adds a long-run lag guard and validates actual first-to-last dispatch span at least 1800 seconds. | Duration does not count warmup, recovery or idle. Dispatch saturation still invalidates a sample. |
| Recovery and retirement | `PerfTarget.finish` executes 32 new low-rate cycles on the same application, independently checks durability, then records 60 seconds idle before the original stop/owner-close path. | Recovery is actual work, not a new process or process exit alone. Recovery remains separate from timed throughput. |
| Provider evidence | Exception observer catch/log/rethrow records actual provider code; SQLite primary code is decoded from the extended code. | Correctly avoids inferring BUSY from HTTP 500. Counts cover the complete process, including setup/recovery, as documented. |
| Retry accounting | No application retry was introduced. The explicit same-key replay remains part of the business cycle. | `business_retry_attempts=0` is a policy fact. Internal SQLite/sqlx busy-handler attempts are separately unavailable and must not be reported as measured zero. |

### Resolved overload blocker

The initial inherited B23 `Target.run` sets `halt_dispatch=True` after any request
exception (`http_target.py:615–623`). Subsequent arrivals are canceled without
HTTP dispatch (`:599–605`). This is reasonable for historical finite correctness
acceptance, but a canceled tail cannot establish sustained offered overload or
its recovery behavior. This finding was sent to the database author and root
before acceptance of the new overload path.

The reviewed fix is scoped to `tests/Perf01.Database`; it changes no historical
B23 source or durable correctness oracle. Non-smoke cells require the frozen
`--continue-classified-overload` policy. A complete HTTP 408/429/500/502/503/504
response, or a declared HTTPX timeout, may permit subsequent real arrivals.
These remain failed observations with original error evidence and failed
zero-error/capacity verdicts. They do not establish that overload caused a 500,
and do not infer SQLite BUSY.

The override executes synchronously in the existing exception path after B23
sets its halt. It clears that halt only for the explicit continued category,
with the policy enabled and a permanent integrity-halt latch still false.
Successful-response protocol/content violations, authentication/validation
responses and unclassified failures set the permanent latch. A concurrent
ordinary service failure therefore cannot reset a previously observed integrity
halt. The policy is stored in target/frozen inputs, and classifications have
their own evidence file. This resolves the sustained-arrival source blocker
while preserving the strict failed-cell verdict.

### Remaining execution/reporting obligations

The A21 worker still holds its detailed scheduled/dispatch ledger in memory until
the cell completes. On an interruption, exact dispatch history may be unavailable
beyond preserved raw events and supervision records. Partial attempts must remain
partial/invalid; do not reconstruct unobserved dispatch counts as exact values.
Do not combine provider counts over the whole process with per-measurement
counts without labeling their scope. Database execution time, lock/pool wait,
native allocator usage and internal busy-handler retries require independent
instrumentation or an explicit unavailable marker.

Source-review disposition: passed for the scoped continuous-overload policy,
duration, B23 oracle reuse, durable-volume evidence and same-process recovery/
retirement design, subject to the explicit remaining limitations above. The
author reports Python syntax and eight pure classifier cases; this reviewer did
not execute those checks. Native AOT/package execution, baseline/final profiling,
timed saturation/recovery measurements and both 30-minute provider segments are
separate root-owned gates, not implied by this review.

## Subsequent isolated-generator source review

Reviewed implementation commit
`659a871d06029a7800385f477a85a5fe2ef2361f` after inspecting the author's
uncommitted source. No builds or loads were run by this reviewer. The optional
generator split starts the disposable PostgreSQL server while the controller is
still on service CPUs 2,3, then moves the controller/worker side to generator
CPUs 0,1. A hash-pinned `taskset` launcher puts the actual application on service
CPUs before its runtime threads start. The observed `/proc/<pid>/exe` SHA-256 is
checked against the original executable's frozen descriptor artifact hash,
rather than treating the taskset wrapper as the application binary.

Observations require exact process main masks and nonempty live-thread subsets
of the corresponding declared CPU pair. PostgreSQL postmaster identity includes
start ticks, and live server children are checked. Cleanup restores the
controller before PostgreSQL shutdown. No-option behavior leaves affinity
untouched. Mask/identity failures remain invalid or partial attempts; the source
does not upgrade them to valid measurements. This source review found no blocker
in the optional isolation, provenance or cleanup policy. Actual isolated runs and
the choice of final resource cohort remain root-owned gates.

## A07 regression specification review

Reviewed the test-only patch now committed as
`8b50b175810dfa40127c18217ab79b7e4f255398` in
`tests/Interop.Async/{Fixture.cs,Program.cs}`. These new cases intentionally
describe the proposed bounded post-result retirement retry and are not claimed
to pass the unmodified baseline runtime. This reviewer ran no tests.

The `AfterRetire` fixture hook follows the real native retirement verdict while
the async operation's cleanup control lease still protects its pointer. Dropping
the source handle releases the native work lease without synthesizing a wake
callback. The manual scheduler's single-pass control makes the quiet-after-
Pending, one-budget persistent-Pending fallback, immediate scheduler
reject/throw, and preterminal-Pending cases deterministic. Assertions cover one
result take, retained input/root/slot ownership while pending, a maximum of one
queued pass and exactly one final release. The preterminal test completes the
native fixture through a still-protected pointer after normal admission closes;
that operation is legal under the fixture's retained cleanup lease.

The critical assertions occur synchronously before awaiting completion, so a
minute-scale fallback timer cannot make the expected second queued pass appear.
Scheduler rejection/throw keeps ownership until explicit retry, while a
preterminal Pending does not consume the later post-result retry allowance.
Existing tests retain the null hook and their previous scheduler behavior.
Source-review disposition: no blocker found. Parent integration must still run
these cases against both the baseline failure expectation and the proposed
runtime change, along with the required existing async regression gate.


## Procfs resource observer follow-up

Reviewed implementation commit
`edda7e7bcf27d2f3cb2d3279b25b74aa449c1094` in
`tests/Perf01.Database/{perf01_resources.py,target.py,run.py,README.md}`.
This was source-only review on CPU 8; no database, application, build, test, or
new benchmark was executed by this reviewer.

The old shared sampler could clear an already measured CPU field when a later
/proc descriptor scan failed. Readback of preserved functional evidence found
one missing CPU row among 421 SQLite application rows and one among 376
PostgreSQL rows, with RSS still present; the latter occurred during measurement.
Those rows did not preserve a descriptor exception, so they are consistent with
the source hazard but do not prove its cause.

The scoped helper (`perf01_resources.py:14–57`) samples CPU/start identity,
A21 memory, affinity and file descriptors independently. Descriptor iteration
and readlink races retain CPU and memory; vanished descriptors are counted as
non-atomic misses, while other descriptor errors leave uncertain FD/socket
totals unavailable. No historical B23 or product implementation was changed.

`target.py:81–119,253–292` adds a nominal one-second observer for the actual
HTTPX target, its A21 scheduler parent, and the frozen controller identity.
Each role has PID/start ticks and phase labels, flushed raw rows and initial/
final observer receipts. The task is stopped and awaited in finalization.
A definite bound identity mismatch marks the observer and extra verdict
failed; it cannot become a valid sample under the intended role.

Two review findings were corrected before acceptance: bound identities that
cannot be confirmed are excluded from role-attributed aggregates while raw
evidence remains, and a definite PID/start mismatch invalidates the observation.
The aggregate helper (`perf01_resources.py:60–110`) selects memory and CPU
independently and leaves completely unobserved descriptor misses null. Existing
application summary fields remain, with separate
`generator_resources[role][phase]` CPU/RSS/FD results in `run.py`.
New observer source is included in the frozen driver identity. Source-review
disposition: no remaining blocker in the scoped sampling, identity, aggregation
or cleanup changes. Actual generator health and final timing validity remain
root-owned measurements.

## PostgreSQL diagnostic observer cleanup follow-up

Reviewed implementation commit
`55f40b1e21c4292de2094722bb070ad406a3bb52` in
`tests/Perf01.Database/profile_postgresql.py`. The earlier
`2f20b2f628d2bb4ada88478a53dccc971247d264` version had a real ownership
gap: observer spawn and initial stdin setup could fail before entering the
cleanup guard. This note records the later fix; it does not retroactively claim
the earlier version covered that edge.

The fixed profile function writes an initial receipt before spawn and places
stderr ownership, subprocess creation, initial command/drain and sampler
creation inside the guarded region (`:72–158`). Input/output waits, sampler
join, observer close, kill and reap are bounded. Finalization attempts the
receipt even on setup failure, retains cleanup failures, and preserves the
primary setup/load exception if receipt or summary generation also fails.

The summary path (`:239–256`) labels missing receipt/files unavailable or
failed; absent evidence cannot be interpreted as a passed observer. The main
cleanup path (`:295–312`) does not hide the primary exception behind a later
summary error. Statement Parse/Bind/Execute accounting and sampled wait-state
interpretation are unchanged: they are not independent business operations or
exact per-query waits. The profile remains ineligible for formal timing.
Source-review disposition: no remaining blocker in this scoped ownership and
exception-preservation fix. No observer process, SQL, application or load was
run by this reviewer. Author-side record is Plan
`9da04ba60cf19471389e7c9284ec516fa721f76f`.
