# DB-Exec-Parity-01 — read-only review of final-tail pull publication

**Status:** candidate analysis only. No product file was edited, compiled or executed for this review. The measured Stage 1 table must be committed to Plan before any execution-path implementation. The input hashes and repository heads are in [common-completion-review-inputs.json](common-completion-review-inputs.json). Korda source is `7ff7b57b907b689defb880b8af62d83679608603`.

## Decision supported by the available evidence

There is a credible common scheduling target, but changing `RunContinuationsAsynchronously` to false in place is not sufficient. A safe experiment would first separate **preparing an immutable, generation-bound publication** from **invoking it as the final action of its own managed coordinator execution**. Every previous-generation resource/control/scheduling access must be complete before the setter can run business continuation code. Publication exceptions must not be converted into another result or into the current generation's `SchedulingFault`.

The CPU sampler finds `RhSpinWait` at roughly 59% of Korda SQLite warm thousand-row samples and 51–53% of PostgreSQL samples. The same-ELF default/spin-0 experiment removes substantial CPU without a corresponding stable latency win. Actual batch diagnostics count 32 batches and 34 native worker entries for the thousand-row/B32 request. These facts justify measuring repeated handoffs; they do not by themselves measure the exact second managed scheduling hop or prove every batch has that hop. [Sampler findings](native-sampler-findings-01.md) · [SQLite measured counts](sqlite-measured-01.json) · [PostgreSQL stage analysis](postgresql-stage-analysis-01.json)

## Existing code and the historical counterexample

The current path is:

1. Native `OnReady` records readiness and its generation under `HostPullController._gate`. Its final managed access decrements `_callbackEntries` and signals the coordinator under that gate. It does not run user work.
2. `CoordinatedCallback.Execute` clears dirty/retry flags, calls `Process` inside `try/catch(SchedulingFault)`, then clears `_scheduled` and resubmits any dirty notification.
3. `HostPullController.Process` waits for setup, accepted readiness, cancellation-registration drain, and zero controls/callback entries; takes the native batch at most once; frees the callback root and releases the retry reservation; seals `_published`; applies publication observers and then calls the MRVTS setter.
4. The MRVTS uses `RunContinuationsAsynchronously=true`. For a pre-registered continuation without a captured scheduler, the setter queues a second managed work item. That setter still runs **inside** the coordinator's `Process` exception boundary and **before** the coordinator's scheduling tail.

Sources: [HostPullController](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Data.NativeHost/HostPullController.cs) and [CallbackCoordinator](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Interop.Callbacks/CallbackCoordinator.cs).

The earlier rejected `bf974378932ec3d42f31eb791e8bede6a69b41ea` proposal moved take/drain/setter work onto the native ready callback stack while leaving asynchronous continuations enabled. Its `.patch.gz` and unexecuted tests are retained in [Plan continuation 5](https://github.com/IzuSharp/Plan/blob/03efe57ffbe3046bd89919ddb2c16c90a377954d/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-5/README.md#unselected-inline-completion-experiment). It received no AOT execution or performance credit. Review found that the setter can publish completion before a later continuation-dispatch exception. Re-setting the source, setting another exception, disposing the delivered batch, or treating that exception as native take failure was invalid. General FailFast or silently claiming dispatch succeeded was explicitly not an accepted repair.

The actual current ILCompiler 11.0.0 package uses the same VMR pin already recovered for this task: `dotnet/dotnet@297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`, with runtime manifest commit `deae2e32bf0e018e09d64597b7c59b62b73bb3ce`. Its [MRVTS source](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Threading/Tasks/Sources/ManualResetValueTaskSourceCore.cs#L228-L263) confirms:

- `SignalCompletion` first exchanges the continuation field with its completion sentinel.
- It captures and clears continuation state/context before dispatching.
- With no context and asynchronous continuations disabled, it directly invokes the continuation.
- Captured synchronization/task schedulers still use `Post`/`Task.Factory.StartNew`; disabling the asynchronous flag does not override their contract.
- Registration that races after completion **still queues**, even with the flag disabled, to avoid stack dives. [Registration-after-completion path](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Threading/Tasks/Sources/ManualResetValueTaskSourceCore.cs#L171-L212)

The proposed experiment is different from the rejected one only if it retains the first managed coordinator handoff and makes completion its final managed tail action. No completion/mapper may run on `OnReady`, a cancellation callback, or a native worker's unmanaged callback stack.

## Required invariants

| Boundary | Invariant that must hold before publication | Failure if omitted |
| --- | --- | --- |
| Setup | Native acceptance is known, setup returned, registration handle is either known/drained or a confirmed close proof discharged the uncertainty | Freeing the root before early ready/registration setup finishes |
| Cancellation | Async registration disposal has completed; every current control/Stop call left; original provider/setup error precedence remains | Continuation races an active cancel/Stop path or masks the primary error |
| Callback | Zero managed callback entries after their last controller access, with the same existing gate synchronization | Native ready uses a freed cookie or old callback changes the next generation |
| Native ownership | Exactly one take; failed take/closed path has its existing compensation; live batch ownership is explicit | Double take, leaked permit, dispose-after-delivery, or using a replaced owner |
| Native notification tail | Retain the existing independent native worker/notification fences and final close join | Confusing “no more managed callback access” with complete native worker retirement |
| Root/reservation | Root freed and reserved cleanup slot released once before publication | Consumer starts another generation while old obligations are still charged |
| Controller generation | Prepared publication records the exact generation/version, batch reference and result/error locally | A delayed old Execute publishes or faults a new generation |
| Coordinator | Dirty/scheduled/retry bookkeeping and any necessary resubmission finish before invoking the local publication; no gate is held | Reentrant requests lose readiness, deadlock, or are overwritten by the old tail |
| Publication | Setter is outside `Process`/`SchedulingFault` catch; it is the last state-affecting action of that execution | Post-publication throw rewrites `_failure`, `_indeterminate`, `_stopping`, or a reused batch |
| Consumption | Existing single-consumer version checks and held-read admission remain unchanged | Stale ValueTask/result tokens read the replacement batch |
| Terminal close | Early stop, EOF, Source close, and transaction cleanup retain independent safety receipts | A faster ready result is mistaken for safe pool return |

The controller's current `_published` flag is sealed before its MRVTS sentinel is set. A candidate must describe that distinction explicitly (prepared/sealed versus externally complete) and preserve the existing fault-observer behavior before actual completion. Moving a field assignment is not proof that continuation publication happened at that point.

## A viable shape for an experiment

The following is design pseudocode, not an implementation approval:

```text
Execute:
    begin this admitted coordinator processing turn
    publication = PrepareWork() under pre-publication error handling
    finish this turn's scheduled/dirty/retry bookkeeping
    issue any already-required next scheduling offer
    publication.Invoke()  // final action; outside prior error handler
```

`publication` must be an execution-local value, not a mutable “pending publication” field fetched later. A small readonly internal struct can hold publisher target, generation/version, result reference and error; that avoids a new capturing delegate/allocation per batch. The concrete type/API is an implementation choice. All other `CoordinatedCallback` users must retain their existing behavior or return an empty publication; changing the common base affects Interop callbacks/async operations, command completion and cursor close tests even when their timing is not the optimization target.

A narrow concrete internal seam is `Process(ref CallbackPublication publication)`: `Execute` initializes a default stack-local publication and passes it by reference. Existing subclasses keep their void early-return control flow and leave it empty; HostPull fills it only at the final successful preparation point. An internal publisher interface can be implemented only by HostPull, while the value carries target, generation/version, result reference and error. This avoids a mutable shared completion slot and avoids rewriting every legacy `Process` body as a value-returning method. Scheduling bookkeeping can live in a `finally` that ends **before** the final invocation; the invocation itself must not be in that `try/catch/finally` scope. On a pre-publication processing exception, discard the local uncommitted publication before existing `SchedulingFault` handling.

The unreserved setup-failure `Resume` path also calls `Process` synchronously today. It needs the same separation between preparation and final publication, with the setter outside its local `SchedulingFault` catch. Simply updating `Execute` leaves this path unsafe. A queued concurrent Stop/drain and a local unreserved drain must still win the publication once under the existing generation gate.

Before invoking the setter, capture every needed field and finish all cleanup, observer calls, error selection and batch disposal for failed outcomes. After invocation starts, do not read/reset generation fields, free roots, release slots, call `Signal`, invoke a stateful observer, or dispose the result. No `finally` may perform one of those actions after arbitrary inline continuation code has consumed the result and called `Request` again.

### Why a shared pending-publication field is insufficient

A concrete interleaving is:

1. Execute A prepares generation 1 and releases scheduling ownership, then pauses before publishing.
2. Another already-admitted Execute B claims a shared pending slot and publishes generation 1.
3. The consumer synchronously consumes/releases generation 1 and starts generation 2.
4. Generation 2 becomes ready and its Execute C prepares a new shared pending slot.
5. Delayed Execute A resumes and consumes the generation-2 slot while Execute C still has a tail.

A per-Execute immutable publication value prevents this transfer of ownership between executions. Generation checks alone do not make a shared slot safe if an old execution is allowed to claim “whatever is current.”

### Post-publication exceptions need an explicit boundary

Both a direct custom continuation and `SynchronizationContext.Post` can throw after the sentinel becomes complete; `Post` can also queue the real continuation, let it consume/start the next generation, and then throw. Such an exception is **continuation dispatch/execution failure after completion**, not provider/setup/take failure. It must never cause a second setter, result disposal, old-result retry, or mutation of the next generation.

Keeping the setter as the final managed invocation permits an exception to follow the managed scheduler/caller's continuation exception semantics, instead of being translated into native state. The implementation must document and test that boundary rather than add a blanket swallow or a direct FailFast. A controlled test scheduler can record the exception from `Execute` and verify that the already-published result and subsequent generation are unchanged. This review does not claim every exotic scheduler can be recovered after it accepts work and throws; it requires preserving observation of the failure without inventing successful delivery or corrupting an already-complete result.

## Concrete regression matrix

Existing tests are source evidence only in this review; their prior results are not rerun/candidate credit.

| Existing/new scenario | Required assertion |
| --- | --- |
| `ReadySchedulingTests.EarlyReadinessDuringSetup` | Readiness before request return cannot take/publish until setup/control completion; root/slot remain held |
| `ReadySchedulingTests` three deliberately late generations | One take and publication per generation, correct order, same batch object, stale version rejected; no continuation inside unmanaged ready |
| `ReadySchedulingTests.RejectedReadyScheduling` | Rejected offer retains root/slot/live registration and unconsumed native result, bounded retry later publishes once |
| `ReadySchedulingTests.CoordinatorTailAndNextGeneration` | Keep real holding SynchronizationContext, current first-generation consumption and independent next ready; replace only the implementation-specific expectation that old `_scheduled` necessarily blocks a new Execute |
| New no-context inline continuation | Consume/dispose g1, call `Request` for g2 before g1 setter returns; g2 readiness is neither lost nor processed twice |
| New delayed publication from an old Execute | A delayed g1 tail cannot publish, dispose, cancel, or change prepared g2; no shared pending-slot theft |
| New continuation throws after consuming g1 | Controlled scheduler observes the same exception; old callback does not call `SchedulingFault`, set another result, dispose current batch or poison/reset g2 |
| New context queues/consumes then throws from `Post` | Already-delivered result and later-generation state remain valid; failure is recorded independently |
| New context throws before accepting continuation | MRVTS is already complete; no false claim of delivered continuation, no second completion or batch disposal; documented managed dispatch-failure behavior |
| New registration-after-completion race | Runtime-required queued path remains correct; no promise that every completed batch is inline |
| `Program.PrivateFetchOwnerFailures` | All ten setup/ready/take/publication fault boundaries retain original error identity and zero owner/control obligations |
| `Program.PrivatePullStopBeforeReservation` and rejected-scheduler matrix | Unreserved failure plus held/failed Stop completes once even if every queue offer is rejected; original error plus separate stop failure remain ordered; SQL count stays zero |
| `Program.ReusablePullBatches` and `HeldPull` | One SQL for multiple batches, one-shot ValueTasks, generation rejection, and no reattach until the last synchronous read releases native storage |
| `BorrowedBatchHostTests` | Held mapper + cancellation/close/error still retains exactly the current native owner; final owner counts zero |
| Interop.Callbacks and Verification.Interop race suites | One bounded queued drain, dirty-notification preservation, retry/close, root lifetime and native decision self-wait semantics remain intact |

References: [ReadySchedulingTests](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/tests/Data.NativeHost/ReadySchedulingTests.cs), [NativeHost Program](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/tests/Data.NativeHost/Program.cs), [BorrowedBatchHostTests](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/tests/Data.NativeHost/BorrowedBatchHostTests.cs), [Interop callback tests](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/tests/Interop.Callbacks/Program.cs), and [real coordinator race probe](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Verification.Interop/RaceSuite.cs).

There is also a resource/fairness change to assess: clearing `_scheduled` before publication allows generation 2 to run while a custom `Post` still holds generation 1's publisher frame. Current tests intentionally demonstrate such a held tail. The candidate may be correct with overlapping already-retired publisher frames, but “at most one queued drain” is then different from “at most one live Execute stack.” Bound/observe held publication tails and repeated synchronous reentrancy; do not merely delete the old test's meaningful barrier. High-concurrency mixed workloads must check worker fairness and tail/RSS behavior after the short causal test.

## Falsifiable measurement for the scheduling candidate

Keep default runtime settings, original batch capacity 32, the same SQL/types/DTO, input snapshots and generated readers. Add independent diagnostic markers for coordinator Execute begin/end, completion setter begin, await-continuation registration, and first managed take with generation/request/batch/TID. Count the actual pre-registered no-context eligible completions, not just calls to `SetResult`. A successful causal intervention should remove that second queue/handoff for eligible completions while retaining the first asynchronous coordinator hop, native worker count, SQL dispatches, protocol frames and batch/row counts.

For 1/32/100/1,000 rows and early stop, measure whether the removed handoff count scales with the actual number of returned batches. Then use same-machine interleaved ordinary A/B to check client CPU/op and service/queue p50/p95/p99, plus a repeated CPU diagnostic to see whether the corresponding spin/scheduling work falls. No-runtime-switch and same-limit comparisons are mandatory. If handoffs fall but ordinary CPU/wall does not improve reproducibly, the complexity has not earned retention. Captured-context cases are correctness coverage even if they intentionally retain scheduling.

## Lower-risk first experiments and implementation choices

### Existing batch capacity is already configurable

`DatabaseLimits.MaxBatchRows` defaults to 256 and admits up to 4,096; `MaxBatchBytes` defaults to 1 MiB. `TypedStream` requests the configured row limit for normal/buffered enumeration; Single/SingleOrDefault still request at most two rows. The historical phase harness explicitly uses 32. [Options](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Data.NativeHost/DatabaseOptions.cs) · [TypedStream](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/src/Data.Streaming/TypedStream.cs)

The actual SQLite diagnostic has the following thousand-row counts:

| Configured rows/batch | Native batches/op | Native workers/op | Frame cells scanned at finish | Table bytes zeroed/op | Finish payload memmove bytes/op |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 32 | 32 | 34 | 2,000 | 53,248 | 124 |
| 128 | 8 | 10 | 2,000 | 50,176 | 1,662 |
| 256 | 4 | 6 | 2,000 | 49,664 | 3,706 |

This is a low-risk configuration sensitivity experiment with no product change. Larger batches reduce fixed task/publication work but increase possible early-stop over-read, live payload, first-batch delay and partial-batch movement. Instrumented durations have no ordinary performance credit. Raising 32 to 256 is **not** a source optimization under identical resource settings, and an implementation must never exceed an explicitly configured limit. Keep original B32 historical/control cases and separate any configuration-tuning result.

### A small measured native finish fast path

`BatchWriter::finish` currently scans every cell and rewrites every non-NULL cell's payload offset even when the batch exactly fills its reserved cell table and no payload movement occurs. In the actual B32 thousand-row narrow result, the measured counters are **2,000 scanned cells and 1,800 rewritten offsets (14,400 bytes)**, while only the final eight-row batch compacts payload (124 bytes). Thirty-one full batches do not change the payload start. [BatchWriter source](https://github.com/IzuSharp/Korda/blob/7ff7b57b907b689defb880b8af62d83679608603/native/cpp/src/contracts.cpp#L1106-L1230)

A concrete lower-risk hypothesis is to emit a non-NULL empty cell's canonical offset as `payload_offset_` in `append_validated` (NULL keeps offset zero), and skip the finish scan when `payload == payload_offset_`. Nonempty offsets in a full batch already have their final value. Partial/byte-constrained batches keep the existing compaction and normalization. On this exact fixture the predicted counters become **16 scanned cells and 14 rewritten offsets**, with identical payload bytes, engine work, task count, SQL, resource bounds and final frames. That is an actual implementation experiment, unlike changing batch capacity.

This path has a much smaller apparent CPU ceiling: `BatchWriter::finish` is under roughly 1% of the present leaf samples, so no large end-to-end gain should be promised. Its appeal is a sharply testable byte/count reduction without changing asynchronous lifetime machinery. Required checks are byte-identical canonical frames and existing contract tests for full/partial/empty EOF, NULL versus empty TEXT/BLOB, zero payload, multi-column/wide DTOs, and byte-limited rows including a validated row held for the next batch. An unconditional `if (full) skip` without fixing empty non-NULL offsets is incorrect because current append writes their offset as zero and finish normalizes it.

### Metadata preallocation is a smaller, currently unmeasured allocation candidate

`Cursor::open` knows the projection field count but grows `cursor->codecs` and `cursor->expectation.descriptors` with `push_back` without reserving that count. Reserving the exact admitted count before those loops would avoid vector growth/copies while retaining the existing per-query metadata/DDL/error validation. It does not introduce cross-query schema reuse. However the current count reports do **not** attribute native allocations specifically to these two vectors; the narrow two-column case can save only a few growth events per query. Add allocation/capacity counters at these actual call sites before claiming a measured benefit. It is not presently a demonstrated hot-path win.

`BatchWriter` already reserves its bounded descriptor/cell prefix plus up to 1,024 payload bytes and grows only for actual admitted values. Do not replace this with reserving the entire MaxBatchBytes allowance: that reverses the current deliberate one-row/large-limit behavior and changes RSS/native allocation cost. Caching an immutable header/descriptor prefix per cursor may replace repeated validation/field stores, but needs its own measured allocation/copy benefit and must not hoist SQLite dynamic type checks or row-wide preflight ordering. Those checks preserve a later-column shape error ahead of an earlier-column conversion/size error.

## Recommendation before implementation

After the complete Stage 1 Plan gate, use the existing B32/B128/B256 sensitivity to quantify fixed per-batch cost and choose the first implementation by measured value. The bounded native full-batch finish fast path is the easier first causal change if publication-tail policy remains unsettled. The scheduling candidate targets a much larger measured CPU concentration, but should be implemented only with per-execution publication ownership, post-publication exception isolation, the unreserved drain path, and the concrete race matrix above. No global ThreadPool setting is part of either product candidate.
