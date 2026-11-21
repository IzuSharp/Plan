# Perf-01: occupied-prefix callback scan — independent source review

**Disposition: accepted for an isolated source experiment at `2c88e5dbbc197079c48c3c41d51101b2d58bb3a5`.** No blocking source issue remains after the test-only correction. This is not a compilation, fixture, performance or final-product acceptance. No build, target import, test, workload, raw-series read or binary hashing was performed for this review.

## Exact reviewed sources

| Role | Commit / SHA-256 |
| --- | --- |
| Comparison base | `a5748ad4e03825e3da7706d074887952da6c2d43` |
| Initial scan implementation | `59eec092eb33ec780bd02cf0d51bdfa9e1c24041` |
| Reviewed test correction | `2c88e5dbbc197079c48c3c41d51101b2d58bb3a5` |
| `src/Interop.Callbacks/CallbackCoordinator.cs` | `c21a46424c7f401f0ddeb9f7d5c14716c13df7b619c671349ec96d1afd6d8667` |
| `tests/Interop.Callbacks/Program.cs` | `260f8bf930b467705e099eea413a5e700b54d815ed923588a09986861725691a` |

The complete base-to-candidate diff contains exactly these two files. Native inputs/ABI, `Interop.Async`, the 1 ms Data/Server constructor arguments, dependencies and public APIs are unchanged. The entire `CoordinatedCallback` scheduling-state-machine class is byte-identical to the base. Removing only the new test seam, probe, two methods and two invocations recovers the original fixture file byte-for-byte, including its existing bounded-queue assertions. The working tree was clean and `git diff --check` passed.

## Production concurrency and cost assessment

The invariant is `_scanLimit == highest occupied slot + 1`, or zero for an empty array. Reserve retains the first-null search and raises the limit inside the existing reservation gate. Release preserves its exact-owner check, clears the slot/count under that gate, and only scans backward when removing the current highest slot. No occupancy writer or limit read escapes that gate.

Retry snapshots the limit under the gate, then retains the original individual slot-read locks and calls each context outside the gate. A concurrently shrinking limit only makes an older scan examine extra null slots; fixed array capacity bounds all indices. A reservation beyond a captured limit can wait for a later scan, while its ordinary Signal path still runs. This does not promise a same-tick or strictly 1 ms wakeup. Slot reuse and a locally retained old context retain the original strong-reference/completion checks; no new retirement decision is derived from the limit.

Count, capacity admission, closing behavior and timer disposal are unchanged. Closing still keeps admitted contexts runnable until real release; the timer stops only under the original closing/zero-count condition. No callback or scheduler call was moved under the reservation gate. Concurrent timer callbacks use separate local snapshots; no shared scan cursor or new allocation is introduced.

The tail-shrink loop can hold the gate for O(capacity) in one release after many lower slots were cleared. With first-null allocation, a successful reserve can extend the limit by only one; total backward decrements are bounded by preceding extensions, so added shrink work amortizes over reservations. Retry still scans holes within the occupied prefix and gains nothing from a retained high slot. These are source bounds, not measured CPU or tail benefits.

## Test finding and resolution

The initial `59eec092` tests were not executed. Source review found possible false failures: `CoordinatedCallback.Retry` checks state and subsequently calls Signal, so an overlapping/stalled timer callback may cause another harmless Process after the first. Exact `Runs == 1` progress waits were therefore too strong. A shared scheduler could also retain an already accepted completed-probe item, or let an old in-flight TryQueue consume the next probe's reset rejection counter. A global multi-probe queue maximum of one was not the intended per-context invariant.

`2c88e5db` resolves these issues without changing the product scan code: all new progress waits use `Runs >= 1`; each original probe has its own scheduler and the reused probe gets a fresh one; only the new aggregate queue assertion was removed. Existing fixture assertions remain unchanged. The blocking scheduler hook is guarded by one `Interlocked.Exchange`, so later stale attempts do not touch disposed test events.

The sparse test meaningfully exercises a high occupied index beyond Count, removal of that tail while a low sentinel remains, an empty-to-reused transition, rejected-scheduling recovery and continued retry after admission closes. It asserts actual release to Count zero, rather than a private scan-limit value.

The concurrent test reaches the real timer Retry via an initially rejected schedule, blocks its first acceptance using the existing scheduler interface, and reserves a new tail from another task. The reservation has a 15-second deadline; the hook's independent 30-second bound and finally-set release prevent the ordinary hook timeout from being the intended successful path. It then checks eventual progress for both contexts and actual slot release. It does not claim which overlapping timer invocation accepted the new tail or exact scheduling latency.

## Remaining execution boundary

Compilation and the original JIT/Native AOT callback/async conformance fixtures remain pending for this commit, as do affected consumer regressions and any equivalent performance comparison. The existing lifecycle, cancellation, native-quiet, quarantine and lost-wake checks must retain their meaning. The new source tests add no public/product hook and no new benchmark or acceptance policy. Performance retention remains the root integrator's decision after actual measurements. This independent technical review is not a GitHub approval.
