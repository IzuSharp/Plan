# Perf-01: independent occupied-prefix callback review

## Disposition and exact scope

**Accepted for controlled functional and equivalent-load evaluation; no source-level correctness blocker found.** This is an independent source review, not an executed test, performance result, final product selection or GitHub approval. The reviewer ran no builds or workloads and changed no product files. Root remains the only integration and execution owner.

The immutable reviewed implementation is NativeWeave commit `092e5e2c74d7419772f2455a2922ae4238f389de`, parent `a5748ad4e03825e3da7706d074887952da6c2d43`. Its complete delta is two files, 110 insertions and one deletion. The root copied a previously uncommitted candidate into an isolated worktree before committing it; this review binds the committed bytes rather than relying on the old mutable directory.

| Reviewed file | SHA-256 |
| --- | --- |
| `src/Interop.Callbacks/CallbackCoordinator.cs` | `c21a46424c7f401f0ddeb9f7d5c14716c13df7b619c671349ec96d1afd6d8667` |
| `tests/Interop.Callbacks/Program.cs` | `9c93dde1805ecc26d5c963bbbb23d76acd1a04386659b656c095427338a8bc06` |

Both hashes were checked directly against `git show` at the reviewed commit. The implementation adds one integer scan bound and updates it under the existing reservation gate. It does not change retry intervals, scheduling/coalescing rules, native retirement, public APIs, cancellation, queue or payload limits. The inherited parent contains the separate one-millisecond Data/Server constructor change and per-message gRPC writer; those earlier changes are not new work in this delta.

## Invariant and race analysis

`_scanLimit` is zero when no slot is occupied; otherwise it is one beyond the greatest occupied index. All mutations of slots, count and bound happen under `_gate`. Reservation raises the bound after installing an owner. Release only contracts it when removing the current tail, walking backward over empty slots. A hole below a live tail therefore cannot hide that tail, unlike incorrectly using `Count` as the scan endpoint.

`Retry` snapshots the bound under the same gate, then retrieves each individual slot under that gate and invokes its context after releasing the gate. The following interleavings preserve the original ownership rules:

| Interleaving | Source conclusion |
| --- | --- |
| Tail released after the scan snapshot | The old bound remains within the fixed array capacity. Later reads see null or a replacement owner; no index can escape the array. Extra empty reads are harmless. |
| A new tail appears beyond the snapshot | It retains its ordinary `Signal` path. A rejected signal or requested native-retirement retry remains dirty and appears in a later timer snapshot. This can defer service by a tick; it does not discard the reservation. |
| A hole is reused within the snapshot | The scan may see the old or new object according to its individually locked read. The new object's ordinary signal and future scans remain available. Ownership is never inferred solely from a slot number. |
| A context is read just before release | Successful callback, async-operation and Server ticket retirement call `CompleteScheduling` before relinquishing the slot. The old captured managed reference remains valid and ignores later `Retry`/`Signal` once completed. The unchanged `Release` owner-identity check prevents releasing a replacement. |
| Timer callbacks overlap | The unchanged per-context `_scheduleGate`, `_scheduled` and `_completed` checks still coalesce accepted work. The prefix snapshot adds no new call while holding the reservation gate. |
| Dispose races with reserve/release | The existing gate orders closing and admission. Dispose stops the timer only at count zero; otherwise already admitted contexts keep their timer. The final release after closing disposes it. Shrinking the bound does not substitute for count or native-quiescence proof. |
| Dispose returns while a timer callback is already in progress | Timer disposal was already non-joining. The fixed managed array remains valid, and the context completion guards still apply. The delta introduces no native dereference or premature native release. |

Relevant unchanged paths were read in `CallbackRegistration.cs` (quiescence and completion before coordinator release), `AsyncOperation.cs` (Pending retirement requests a retry, then native/control/callback/root drain before release), and `Server.Native/NativeHost.cs` (host control, tickets and continuation slots). The coordinator contains no callback invocation under `_gate` and introduces no lock-order reversal.

The review does not strengthen existing caller contracts. A caller that releases an active context without its original lifetime proof would already be invalid. Constructor-failure release paths remain unchanged; the new scan bound is not a substitute for their original setup rules.

## Regression design and fragility review

The two added tests exercise behavior relevant to the optimization:

- `SparseCoordinatorRetryAndReuse` creates holes while retaining a tail beyond `Count`, rejects scheduling once, removes the tail, verifies the remaining head still retries, drains to zero, reuses the first slot, and closes while an admitted rejected item still needs retry. It also rejects new admission after close and checks that work was not duplicated.
- `CoordinatorReservationDuringRetry` pauses accepted scheduling inside an active timer scan, reserves a new tail while that scan is paused, and verifies eventual processing after rejection. Its reservation must complete while the context callback is paused, which checks that the coordinator gate is not held during that call.

The committed test uses a **30-second** scheduler-pause safety timeout and a **15-second** reservation timeout. This ordering matters: the safety timeout cannot ordinarily release an incorrectly held gate before the reservation assertion times out. No timeout shortening is recommended. The pause is released in `finally` around the awaited reservation. Tests use a `ConcurrentQueue` and the unchanged coalescing scheduler rather than adding production instrumentation or reflection-based invariant assertions.

The tests check safety/liveness, not the amount of scanning. They may also pass the original full-array implementation; that is appropriate for equivalence regressions. They are not exhaustive interleaving proofs. In particular, every possible tail contraction and reuse during an already captured prefix is covered by the invariant analysis rather than a new exhaustive scheduler. Existing native drain, callback/GC/cookie reuse and async lifetime tests remain necessary when executing the shared-code change.

## Cost and remaining evidence

The motivating completed one-millisecond TLS ablation recorded higher active CPU in all six profile pairs, about 1.40–2.30 percentage points of one core, while many tails improved and two server-stream p99 pairs worsened. It did not isolate timer/scan CPU. This review therefore treats reduced scan work as a source-supported hypothesis, not an established cause of those observations.

The delta changes a timer tick from scanning capacity slots to scanning the occupied prefix, with one additional snapshot lock. Holes inside that prefix remain scanned. Removing a tail may walk a long empty suffix under `_gate`; this is bounded by the existing capacity and adds no allocation, but high churn with sparse tails can move work into release. The timer still fires while idle, and the permanently reserved Server control can keep a nonzero prefix. This is not a timer-elimination or idle-CPU proof. Dense occupancy approaches the original scan cost; overlapping timer callbacks and ThreadPool scheduling remain possible.

Proceed with the original A06 callback verifier on the immutable commit, retaining its JIT/AOT, native callback and API checks under the finite owner. Since the implementation is shared, evaluate affected async retirement plus existing AsyncProof/extension use as part of the relevant regression suite, and bind any selected package's Data/Server/B18 results to its actual bytes. The original coordinator default remains 10 ms outside explicitly changed Data/Server hosts, although all consumers share the new scan algorithm.

After those prerequisites, compare the prefix candidate against its exact parent with the same package/application producer and frozen TLS/scalar/application loads. Preserve the two adverse server-stream observations, compare CPU as well as latency, and separately obtain idle-resource evidence rather than relabeling active CPU. Formal EA5-before/final comparisons, capacity, and all ten required continuous long segments remain separate outstanding acceptance obligations. No previously measured mixed-provenance binary inherits this commit's performance credit.
