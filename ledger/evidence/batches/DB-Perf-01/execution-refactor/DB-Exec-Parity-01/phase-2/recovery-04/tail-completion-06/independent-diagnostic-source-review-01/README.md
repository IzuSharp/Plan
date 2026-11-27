# tail06 completion ledger — independent source review

Reviewer: `/root/candidate_contract_review`. Overlay author: `/root/worker_boundary_review`.

**No blocking source defect found for the proposed bounded mechanism experiment. Proceed to the separate diagnostic PackageReference builds.** This is a source review, not a completed build, runtime-validation or mechanism result.

The actual before overlay is commit `197f0d3444cf3cfc120982273d48d1dcf74f60db`, tree `37615cdc87f1df5d223bd95714094d87f9b63028`, based on ordinary integrated05 `2ea67ce1902f330679c3ebff4d6d5733be20f69c`. The tail overlay is `ba4e7ec9bf93ad313dbbb167457189a5f95429da`, tree `924a6c2958e4bcb8a9b3992bb8ecb9eddb05a84b`, based on ordinary candidate `4a9e4435ea5c836be44fb00dc4219301567072c6`. Each clean worktree changes only HostPullController, CallbackCoordinator and the new local CallbackDispatchDiagnostics ledger. Both use the identical ledger implementation. Native code and ordinary source inputs are unchanged.

## Reviewed event and ownership boundaries

- Each diagnostic request is one immutable reference containing controller identity, 64-bit generation and MRVTS version. The native Run/Abandon request key is captured while claiming that same generation under the controller gate, as recorded by `diagnostic-source/committed-02.json`. Earlier applied-overlay receipts remain historical and are not the committed source identity.
- The actual setter is bracketed by a thread-local nested frame with its own ID and captured immutable request. Both exception and normal paths emit an exit. Setter and executor `finally` blocks consult only captured diagnostic locals; they do not read the controller or generation after a continuation may have started g2. Restoring the prior TLS frame supports nested publications.
- OnCompleted records the original flags and the effective scheduler kind: it honors UseSchedulingContext, excludes the base SynchronizationContext, and otherwise distinguishes a non-default TaskScheduler. A trampoline records continuation entry/exit while forwarding the original state and flags. It does not suppress or replace the core's context capture.
- OnCompleted normal-return evidence occurs after the actual core call returns. Only a successful exit strictly before setter entry can prove pre-registration. Interleaved or overlapping intervals must remain unknown; entry-before-setter alone is insufficient.
- Native Run return is distinguished from the later diagnostic frame-exit point after the execution borrow and control retirement. Take and the zero-obligation retirement snapshot occur before setter entry. These probes support this ordering; they do not expose every OS scheduling or driver-internal stage.
- Actual scheduler TryQueue offers have distinct IDs and accepted/rejected/throw outcomes. Execute carries both its current request key and the request key captured for its offer. Coalescing or generation progress can make those keys differ; the parser must retain the relationship and must not force one offer per generation. These are coordinator offers, not direct instrumentation of MRVTS's internal completion queue.

## Clock, loss and observer boundaries

Each emitted event retains monotonic Stopwatch ticks, thread CPU nanoseconds from CLOCK_THREAD_CPUTIME_ID, and managed/native thread IDs. Native IDs are cached per managed thread. The clock calls, diagnostic allocations, trampoline, global writer lock and file formatting all perturb the process. Their time and allocation belong to this diagnostic identity; the trace cannot provide ordinary performance or framework-allocation credit.

The timestamp is sampled before acquiring the ledger write lock. Therefore global sequence order is file-serialization order, not a global timestamp ordering. A strict parser must validate unique contiguous file sequence while using captured timestamps and TLS/request identities for dynamic intervals. Per-thread ordering can be checked separately. A phase's elapsed-minus-thread-CPU difference does not independently identify OS scheduling, protocol wait, or logger-lock wait.

The bounded record count, dropped/error counters, active-scope counters, pending offers, final footer and late-event sidecar make incomplete captures rejectable. ProcessExit waits at most five seconds only for diagnostic frames to retire, then writes its final ledger. This is outside the measured business loop and is not a change to the ordinary runtime. A valid experiment must reject a missing/inconsistent footer, overflow, clock errors, active or pending work, or any late sidecar; absent records must never become zero counts.

## Remaining validation contract

The strict parser and runtime driver must bind these exact source identities to the actual diagnostic nupkg, PackageReference consumer, generated C#, ELF/debug/native artifacts and command/process. They must validate business rows/digest, SQL/native Run/take/batch counts, zero owner balances, the ledger's loss/lifecycle invariants, and correct one-time publication/GetResult. Inline evidence requires the same request and version, matching managed/native thread IDs, and the matching nested setter frame during the actual continuation/GetResult dynamic interval. A timestamp or thread-ID match alone is insufficient.

MRVTS completion enqueue attribution remains a separate claim: the observed eligibility conditions plus matching runtime source and actual ELF branch can establish the selected path; this library ledger does not directly count runtime-internal enqueue calls. Captured schedulers, late registration, overlap and absent registration must be reported separately. Before and tail eligibility proportions may differ because instrumentation changes racing schedules; neither proportion can be assigned to the uninstrumented ordinary consumers.

`validation.json` records 23 passing identity and scope checks, including both source trees, all six changed-file hashes, the identical logger hash, native-source equality, and impact plans with independent SQLite/PostgreSQL public groups and empty runtime steps. This reviewer ran no build, database, profiler, or benchmark. The ordinary `4a9e443` source remains frozen and no CI performance task is added.
