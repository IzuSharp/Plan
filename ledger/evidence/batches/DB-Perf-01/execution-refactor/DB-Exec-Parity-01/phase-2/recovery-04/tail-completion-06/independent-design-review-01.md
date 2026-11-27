# tail-completion06 — independent contract review of the proposed design

Reviewer: `/root/candidate_contract_review`. Author of the reviewed design and prospective implementation: `/root/worker_boundary_review`. This is a read-only review of the new proposal, not reuse of the previous reviewer's role for a new implementation.

Reviewed design: `design-01.md`, SHA-256 `a53b144c53ad5ca589035f9bac96c652014deea9819e56410e110d203dd8f265`. Intended product base: integrated05 `2ea67ce1902f330679c3ebff4d6d5733be20f69c`, tree `4e3989f2ce9e0c554585aab5a8bbb656e689b18d`.

## Decision

No implementation-blocking contract omission was found in this design. Proceeding to one separately identified synthesis is justified, subject to root authorization. There is no new candidate, build, correctness result, causal observation or performance acceptance in this review.

The old Common-A rejection remains valid for its old source/native identity. The combined Worker-D path still calls the pull MRVTS setter inside `Process`, inside the coordinator's `SchedulingFault` catch, and before clearing the coordinator's `_scheduled` state. Merely disabling asynchronous continuations would be unsafe: a continuation or custom `Post` may consume generation 1, start generation 2, then throw into that old exception handler.

The proposal addresses that specific fault with an immutable publication local to one processing invocation. It is an appropriate bounded experiment; the current eligible fraction and ordinary performance effect remain unproved.

## Sources actually read

- Current `worktrees/Korda/src/Interop.Callbacks/CallbackCoordinator.cs`: reservation, dirty/retry coalescing, queue rejection and the processing exception/tail boundary.
- Current `src/Data.NativeHost/HostPullController.cs`: setup, unreserved `Resume`, actual `Run`/`Abandon`, ready callback, cancellation registration, take/publication, cold-close recovery and one-time result consumption.
- Current `HostStreamTransport.cs` and `HostCursorCloseController.cs`: final stop/close proof, original stop-error observation and separate native notification safety.
- Current `tests/Data.NativeHost/ReadySchedulingTests.cs`, `WorkerExecutionTests.cs`, and relevant private pull/failure/held-read tests in `Program.cs`.
- Locked `restored-stage1/diagnostics/runtime-source-297acf/src/runtime/src/libraries/System.Private.CoreLib/src/System/Threading/Tasks/Sources/ManualResetValueTaskSourceCore.cs`, especially `OnCompleted`, `SignalCompletion` and `InvokeContinuationWithContext`.
- Plan's `phase-1/common-candidate-review-01.md`, `phase-2/common-a-implementation-01.md`, `phase-2/continuation-20261126.md`, and new `phase-2/recovery-04/tail-completion-hypothesis-06.md`; Design's actual `execution-parity-01.md` publication contract.

The locked MRVTS implementation first exchanges the completion sentinel, captures and clears continuation state/context, then dispatches. Without a captured scheduler, eligible pre-registered continuations can be called inline when the asynchronous flag is disabled. Captured scheduler dispatch still follows the runtime's `Post`/TaskScheduler rules, and registration after completion still queues. The ExecutionContext branch restores its prior thread context before rethrowing a continuation failure. None of these runtime context restorations requires a Korda owner or generation mutation after the setter.

## Invariants to check again in the actual candidate

| Boundary | Required behavior | Existing concrete counterexample or gate |
| --- | --- | --- |
| Provider execution | Preserve `ExecutePrepared`'s `using` borrow, complete native Run/Abandon return, then release the execution control. No setter or user work on the native callback/PInvoke frame. | Setup/real-ready and held native callback tail tests; WorkerExecution failure at BeforeRun/RunReturned. |
| Registration/control drain | Keep registration disposal, callback-entry and control counts, accepted-ready checks and unknown-safety retention. | Full NativeHost cancellation, source-close, indeterminate execution and borrowed mapper tests. |
| Publication preparation | Complete native take, original failure selection, root/slot release, Published observer exceptions and failed-result disposal before freezing the local result/error. | PrivateFetchOwnerFailures at all ten existing boundaries. |
| Coordinator tail | Complete dirty/scheduled/retry bookkeeping and any required offer before publication. No tail `finally` may touch those fields after the setter. | Real held Post barrier; new generation must complete while the old publisher is still held. |
| Publication ownership | Bind publisher, full generation, MRVTS version, result reference and selected error in the invocation's readonly local value. Never read a shared pending publication. | Delayed/empty old processing turn and g1→g2 reentrancy tests. |
| Dispatch failure | Keep setter outside `SchedulingFault`; preserve the original managed dispatch/execution exception. No second setter, batch disposal, poison, native stop, retry or new-generation mutation from the old frame. | Controlled Post consumes g1, creates g2, then throws; a baseline-only negative must distinguish this boundary. |
| Unreserved setup | Apply the same final boundary to `Resume`; do not make setup-failure cleanup depend on a successful scheduler offer. | BeforeRoot/RootAllocated × held Stop success/failure with all queue offers rejected, in both providers. |
| Error ordering | Pull returns the original setup failure; separate stop failure remains the final-close error after independent cleanup. | Existing RejectedPullScheduler preserves both exact exception objects and verifies no SQL execution. |
| Ownership reuse | Consume once, reject stale versions, and preserve the same batch owner without replacing storage while a read lease is held. | ReusablePullBatches, RejectConsumed and HeldPull. |
| Other coordinator subclasses | Signature-only adaptation with empty publication; command, generic async and close completion policies remain unchanged. | Existing Interop.Callbacks/Interop.Async, NativeHost command/close/transaction and API gates. |

A pre-reservation setup failure happens before token registration, but it can overlap an explicit Stop control or a forced close. That fact does not permit removing the current control/close proof. Likewise, “no managed callback entries” is not by itself proof that the complete native Run frame returned; Worker-D's existing outer execution control is essential.

## What the new tests and measurements must establish

The design preserves the useful barriers in the old held-Post test and explicitly changes only its old scheduling assumption. Four independently held, already-consumed publisher frames and eventual release/fifth generation provide a useful bounded regression. They do not prove bounded stack/thread use for arbitrarily blocking user code. The later ordinary mixed tests must retain fairness, p95/p99 and retained/peak RSS findings.

New correctness tests must establish actual inline continuation, ExecutionContext restoration, late registration queuing, Post failure before dispatch, and Post failure after g1 consumption/g2 creation. The baseline negative should use only the new exception-boundary test with unchanged baseline product bytes. A failure merely because baseline completion stays asynchronous would not prove an old contract fault.

The proposed independent diagnostic is appropriately conservative: correlate generation/version, actual OnCompleted return, setter dynamic interval, continuation/GetResult, TID and processing offer/Execute counts. Same TID alone is insufficient. Overlapping registration/setter intervals and logger loss stay unknown. Count actual coordinator offers separately from MRVTS enqueue paths inferred from observed preconditions plus matching source/machine code. The necessary next-batch provider execution work item remains.

Instrumentation can change registration/completion timing. Its eligible fraction belongs to that diagnostic identity and must not become an ordinary percentage by assumption. Native SQL/Run/take, row/batch/column/byte and final-owner counts must remain the same. New ordinary consumers must preserve the existing native bytes and business/source inputs, and only uninstrumented reversed comparisons may select the candidate.

## Remaining unknowns and stopping decision

Current integrated05 eligibility is unknown. Even if the dispatch is demonstrably removed, repeatable CPU/end-to-end benefit is unknown. Current ThreadPool spin samples are not an exact removable CPU budget, and the fixed-arrival producer remains in mixed-process totals. Post-scheduler dispatch failures remain subject to the managed executor/runtime's ordinary exception semantics; the library must not invent successful dispatch or a new global FailFast policy.

The design's stop conditions are sufficient: reject an unsatisfied ownership/error boundary, a missing or unobserved mechanism after adequate observation, nonrepeating ordinary benefit, or a material repeated regression. This review does not authorize additional unrelated execution changes.
