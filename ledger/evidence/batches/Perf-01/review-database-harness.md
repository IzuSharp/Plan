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
