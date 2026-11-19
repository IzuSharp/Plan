# Perf-01 shared candidate review checklist

Status: prospective source review, before product implementation. No build, test
or application load was run for this checklist. The baseline product remains
`ea5fa528035d025bd7a28698ee7c71194432236c`; its observed A02 cold-import failure
must remain a reported baseline failure. A correction belongs to the candidate,
not a rebuilt or silently repaired before package.

This checklist joins the existing
[resolver ownership proof](source-aot-resolver-ownership.md),
[actual A02 controls](source-a02-cold-import.md),
[descriptor cache study](source-loader-cache.md), and
[TypedStream concurrency study](source-streaming-move.md). Those documents retain
the detailed upstream/runtime evidence and independent reviews.

## Review the four changes independently

| Candidate | Required invariant | Reject the patch if it does this |
| --- | --- | --- |
| A02 resolver-owned reference | Keep the first validated `LoadedModule` resident. A recognized callback acquires a fresh OS reference using the exact stored absolute path and returns it only when its handle equals the resident handle. The runtime/caller owns that additional reference. | Return a borrowed or repeatedly reused extra reference; free the resident reference; warm imports to conceal the race; return zero after failure of a recognized alias; select another search path. |
| `EngineDescriptor.Inspect(null)` success cache | Cache only a fully successful call on that immutable descriptor, after identity/bootstrap and per-assembly resolver binding succeed. Publish safely to concurrent callers. Every non-null options object still takes the existing full path. | Cache an exception, use a global engine-ID shortcut, skip explicit path/capability snapshots, or publish before `AssemblyResolver.Bind` can fail. |
| A07 bounded retirement retry | After actual native `TryRetire == Pending` and `_resultProcessed == true`, request at most one extra scheduled pass for this operation. Keep ordinary retry eligibility and every existing release condition. | Consume the budget before result processing; reset it on another callback/retry/refusal; spin or call retirement twice inline; infer native quiet from managed result completion. |
| `TypedStream` lazy disposal waiter | Admit a move under `_gate` before calling the async method; create a shared waiter only if disposal joins an active move. Preserve the independent cleanup gate and the original mapper exception. | Record the move only after a synchronous mapper can run; invalidate a batch while its mapper is blocked; use a faulting move task as the successful lifecycle waiter; make cleanup await its own active move. |

### Resolver and default inspection

Relevant baseline code is `EngineModuleLoader.cs:70–126,231–270` and
`EngineMetadata.cs:106–133`. Preserve filename/basename conflict detection and
per-assembly ownership while changing alias values from a raw handle to the
immutable module record. A recognized acquisition failure must preserve the
resident slot; on a mismatching newly acquired handle, release only that new
reference and fail. Unknown aliases retain the existing zero return. The locked
single-argument `NativeLibrary.Load(path)` path is nonrecursive; do not use the
assembly-aware overload inside the resolver.

The descriptor cache is a separate performance experiment. Null/default success
may reuse resident metadata after the original file is unlinked, but explicit
overrides must still be checked. Never-mapped missing/corrupt assets remain
repairable on the same descriptor; mapped bootstrap failure remains sticky.
New conflicting descriptors must still reach identity checking. The existing
84-symbol A02 API/XML boundary must not change.

### A07 scheduling point

`AsyncOperation.Process` currently calls `RequestRetry()` at the Pending branch
(`AsyncOperation.cs:517–531`). `CoordinatedCallback.Execute` clears `_dirty/_retry`
before the pass, leaves `_scheduled` true while `Process` runs, then schedules
another pass only if `_dirty` is true (`CallbackCoordinator.cs:140–158`).

Therefore the minimal candidate keeps `RequestRetry()` for every Pending verdict
and additionally calls `Signal()` once at the eligible post-result verdict.
During the current pass that signal marks dirty; it does not execute native work
inline. The existing wrapper schedules the follow-up after the current native
control lease has left its `finally`. Decide/spend the per-operation budget under
the operation gate, then signal without retaining that gate. Do not change
`CallbackCoordinator` or `CallbackRegistration` for this narrow candidate.

Queue refusal/throw must leave dirty/retry state, owner, input, root and slot
retained for explicit/timer retry, even though the one immediate budget is spent.
Release still requires native quiet, result processed, registration drained,
zero controls/callback entries and no prior release. Preserve the distinct
application task and actual retirement completion, quarantine, poison, take-once
and original exception behavior.

### Typed stream

The move bit must cover the complete existing `MoveAsync`, including awaited
catch/EOF cleanup. Clearing it and capturing/completing the optional waiter must
use the same gate as disposal admission. Keep asynchronous waiter continuations,
shared cleanup completion, cancellation registration draining and provider join
outside the gate. A late start-factory result must still be published and stopped
when disposal already closed admission. No reusable task source, public API,
projection or native wire change is needed for this candidate.

## Execute once per final candidate identity

These are the direct component gates, not an instruction to execute during an
active measurement window. Use the existing locked verifiers and retain their
actual JIT/Native AOT, source and artifact receipts.

| Gate | Exact regression coverage to retain |
| --- | --- |
| A02 `tests/Interop.Negotiation/verify.py` | `default-concurrent`, `default-retry`, `default-options`, `default-conflict`; existing `concurrent`, `cached-override`, `preload-retry`, `latched-failure`, options/coexistence/resolver negatives, API/XML and actual NuGet JIT/AOT consumers. The new baseline cold-import failure must pass on the correction. Existing forced borrowed/owned controls already establish the runtime mechanism; do not rerun them merely to recreate that evidence. |
| A07 `tests/Interop.Async/verify.py` | Integrate test-only commit `8b50b175810dfa40127c18217ab79b7e4f255398` with the candidate: `ImmediateRetirementAfterPending`, `ImmediateRetirementBudgetIsBounded`, `RejectedImmediateRetirementScheduling`, `PreterminalPendingPreservesImmediateRetry`. Retain `ResultBeforeNativeQuiet`, registration drain, rejected scheduling, take/duplicate diagnostics, quarantine/fault children, self-wait and `LostWakeRegression`. The new cases intentionally require the candidate and are not claimed to pass baseline. |
| B06 `tests/Data.Streaming/verify.py` | Both actual providers in JIT/AOT: `blocked-mapper-dispose`, `blocked-mapper-failure-dispose`, concurrent/pending-fetch disposal, method/enumerator cancellation, mapper failure, cleanup-failure registration drain, EOF/early break, byte/row caps and owned DTOs. Test commit `ec5d16d…` is already integrated; its exact baseline pass is separate from the required candidate pass. |

Run one final A02 gate for both loader changes, and one final A07/B06 gate for
their respective implementation changes. Do not duplicate these component gates
for each domain. Reuse a passed gate only when its binary, case and configuration
match the reported candidate; baseline managed binaries cannot validate changed
Core behavior.

The distinct downstream boundaries already mapped in the resolver review remain
relevant: A08 executor close, A20 stale-notice/source-lease races, A23 owner-thread
engine, B16 body owners, B17 held-chunk/TLS host close and B19 MCP/SSE cancellation.
Also retain the already planned A17/A18 and applicable B15/B18 real-host/package
checks. Reuse exact overlapping candidate cases, rather than rerunning embedded
performance benchmarks or the same native-crate checks for every consumer.
A query-generator/DTO matrix is not newly implicated by these internal-only
changes. If the actual patch changes another boundary, revisit this scope.

Finally, rebuild the complete candidate B24 closure and test its actual package
entry points. Use the same frozen DB/protocol/codec drivers for formal comparisons;
PageProbe/RetirementProbe remain separate profiling evidence. Keep the owned-ref
correctness fix independently of steady-state timing. Decide whether to retain
the other three performance changes from actual latency/throughput/resource
comparisons and targeted allocation profiles, without attributing the entire
baseline cost to a single source-visible allocation or retry.
