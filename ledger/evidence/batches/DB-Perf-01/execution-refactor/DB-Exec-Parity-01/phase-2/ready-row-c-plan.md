# DB-Exec-Parity-01 — ready-row-c isolated hypothesis

Status: root/recovery/PG independent source reviews found no blocker. Original
and candidate products have passed the new behavior checks in actual Release
Native AOT. Ordinary package/consumer builds are in progress; no performance or
allocation credit yet.
The candidate starts independently from product `7ff7b57`, not from lease-b or
the PostgreSQL configuration candidate.

## Existing count and actual machine-code evidence

The already measured `analysis/lease-b-count-gate.json` contains each request's
actual batch generations and materialized row ordinals. Its 150 successful
queries cover both providers. In full 1/32/100/1000-row queries, the count of
rows after the first materialized row of a batch is 0/31/96/968 respectively;
the 1000-row query stopped after one row has zero such rows. These are the
possible ready-row cases, not a CPU saving prediction.

In the frozen ordinary baseline SQLite ELF SHA-256
`76be826f4ffb7585eff7a0037d1850ead6907403f4f41b1874916e76cbfe7f87`, matching debug
symbols identify MoveNextAsync at `0x21ad50` (163 B), MoveAsync at `0x21ae00`
(156 B), and the generated MoveAsync state machine at `0x21c070` (3562 B).
Actual MoveNextAsync unconditionally tail-jumps to MoveAsync. Actual MoveAsync
reserves 152 B of stack and zeroes a 144 B area with nine 16-byte stores before
calling shared AsyncMethodBuilderCore.Start and reading the pooling builder's
Task. These are machine instructions observed in the actual ordinary ELF;
instruction counts/stack writes are not attributed CPU cycles or allocation.

## Required context and failure semantics

The ILCompiler11.0.0 nuspec/VMR binding already fixes
`dotnet/dotnet@297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`. Source read at that
exact commit confirms:

- `src/runtime/src/libraries/System.Private.CoreLib/src/System/Runtime/CompilerServices/AsyncMethodBuilderCore.cs`:
  Start saves and restores the current ExecutionContext and SynchronizationContext.
- `.../AsyncValueTaskMethodBuilderT.cs`: Create returns default; Start calls only
  AsyncMethodBuilderCore.Start. Task/SetResult/SetException are separate paths.
- `.../PoolingAsyncValueTaskMethodBuilderT.cs`: the existing pooling builder uses
  the same Start context guard.
- `.../Threading/Tasks/Sources/ManualResetValueTaskSourceCore.cs`: an
  OperationCanceledException gives Canceled, not Faulted.

Therefore a plain synchronous mapper shortcut is rejected. It would leak
AsyncLocal/SynchronizationContext modifications into the caller. The proposed
small IAsyncStateMachine contains only its Enumerator and ValueTask result and
is run through a default public AsyncValueTaskMethodBuilder<bool>.Start. No
builder.Task is read and no SetResult/SetException is used on success. Ordinary
allocation A/B must still confirm no new steady-state object cost.

## Candidate boundary

MoveNextAsync retains the existing synchronous admission gate and its direct
closed/concurrent-use exceptions. Finished/no-transport/no-batch cases directly
use the original MoveAsync. The small guarded state checks the token, current
batch state/Rows and the closing gate in the original order, then invokes the
unchanged Materialize/MaterializeBuffered branch. All lease, generation, row,
column, quota and read-scope protections remain.

Exhausted/inactive batches use the original MoveAsync; they therefore retain a
documented extra token and batch-eligibility check at the boundary. Successful
ready rows complete through the exact existing finally gate, extracted as
FinishMove. Its failures must not enter mapper-failure cleanup: an outer
exception-to-ValueTask boundary preserves that distinction.

Mapper/read/token failures start FailReadyMoveAsync *inside* the guarded
state's catch. Thus the original mapper ExecutionContext is still current when
cleanup starts. That helper sets finished, awaits existing cleanup, attaches its
failure to the original error, rethrows the same error with preserved stack,
and only then executes FinishMove. Its async builder preserves OCE cancellation
status and retains moving until actual cleanup finishes. Slow MoveAsync keeps
its original body/catch behavior; only its finally delegates to FinishMove.

## Source review and required verification

Product candidate is `bd9c307434d1d901752fd4353758041e38510ef1`, with the
behavior tests added in `498fb329c897dac8d58479d218969eff99eeb8e5`. The same
test commit is replayed on the unchanged product baseline in the separate
`task/DB-Exec-Parity-01-ready-row-c-baseline-checks` worktree, commit `962c401`.
Its `src/` diff from `7ff7b57` is required to be empty by the build driver.

Exact upstream builder files are now retained under
`diagnostics/runtime-source-297acf/src/runtime/src/libraries/System.Private.CoreLib/src/System/Runtime/CompilerServices/`;
`ready-row-builders-identity.json` binds SHA-256, byte counts and the GitHub blob
SHAs of the retrieved full source. The sources were previously read through
the GitHub connector but were not all present in the local runtime directory.

`diagnostics/ready-row-c/check_streaming.py` runs baseline and candidate AOT
behavior checks separately. It keeps the original product versions and frozen
NuGet locks, retains output/debug/generated inputs, and records hashes before
retiring only its own reproducible intermediate files. The candidate also runs
the existing scoped-batch, row-lease and active-move/borrow-race checks.

`diagnostics/ready-row-c/build_provider.py` will publish independent local
packages `0.1.0-db-exec-parity-ready-row-c.1`, reusing native artifacts only
after every recorded native input and output hash matches. The ordinary phase
and workload consumers retain the exact original harness; the root-owned
final GC-metric harness transformation is intentionally not part of this
isolated hypothesis. No package publication is performed by this script.

Actual correctness receipts (all commands exit 0 on first attempt) are
`builds/ready-row-c-baseline-streaming-correctness-01/receipt.json` and
`builds/ready-row-c-candidate-streaming-correctness-01/receipt.json`. Both pass
the same 233 new behavior assertions; the candidate also passes 30 stable
batch, 364 row-lease, 19 borrowed-lifetime and 118 lazy stream/race assertions,
for 764 assertions in total. The baseline product diff is empty. These runs
establish behavior only and do not measure or credit CPU, allocation or latency.

Before build, root and an independent agent review the exact source. Necessary
new correctness cases observe baseline and candidate AsyncLocal and
SynchronizationContext isolation on a genuinely ready second row, also under
suppressed execution-context flow; mapper context remains visible at cleanup
entry. Exception tests cover synchronous ValueTask fault/cancellation status,
the original exception/token, delayed cleanup and overlapping Dispose. Existing
Streaming lifetime/reentrancy/forced-GC tests remain mandatory. A direct
synchronous-mapper negative control demonstrates why the guard is needed.

After source approval and measurement-lane release: build two independent
canonical packages and real Release Native AOT phase/workload consumers. Bind
actual generated code/ELF/debug/native/commands. Root owns ordinary interleaved
A/B and will decide whether the wrapper reduction produces useful CPU or
endpoint improvement. No code-size, 968-entry count, zero internal window or
instrumented run establishes a performance claim. No CI performance entry,
workflow change or Go-draft change is permitted.
