# Perf-01: TypedStream move-completion allocation candidate

Status: source-only concurrency review and focused test preparation. No runtime
implementation, build, test execution or load was performed by this review.
Root owns the candidate implementation and equivalent-load measurement.

## Baseline and existing contract

At NativeWeave `ea5fa528035d025bd7a28698ee7c71194432236c`,
`src/Data.Streaming/TypedStream.cs:125-135` allocates a
`TaskCompletionSource` for every admitted `MoveNextAsync`, including a row
already available in the retained batch. That completion object serves two
purposes: exclusive move admission and a lifecycle signal for concurrent
disposal. Its result is always successful; the caller separately receives the
actual `MoveAsync` result or original exception.

Relevant inspected paths are `MoveAsync:137-190`,
`CleanupAsync`/`CompleteCleanupAsync:192-222`, and
`DisposeAsync`/`RequestStop`/`DisposeAfterMoveAsync:223-243`.
`src/Data.Streaming/StreamTransport.cs:45-100` makes the row lease's lifetime
observable: disposal invalidates the wire reader and releases its owning batch.
`docs/guides/data-streaming.md:108-132` requires one active move, synchronous
mapping, original constructor errors and provider-confirmed retirement.

Existing `tests/Data.Streaming/Program.cs` exercises concurrent move rejection
and disposal during a pending native fetch, mapper errors, early break, final
EOF, cancellation, cleanup failure and unused-enumerator disposal. Its real
SQLite/PostgreSQL fixture remains the source of bytes and retirement receipts.
It lacked a controlled concurrent disposal during synchronous materialization
of a row already resident in the current batch.

## Narrow replacement and invariants

An admission boolean and a lazily allocated disposal waiter can separate the
two existing purposes. Keep the current async `MoveAsync` method and independent
cleanup completion gate. This removes a source-visible per-move completion
allocation without introducing a reusable value-task source, changing the
public API, or proving a measured application gain.

| Boundary | Required behavior |
| --- | --- |
| Admission | Under `_gate`, reject closed/concurrent use and set `_moveActive` before invoking `MoveAsync`; synchronous mapping can block before that invocation returns a task |
| Disposal during an active move | Under the same gate, close further admission and obtain/create one shared waiter with asynchronous continuations; request native stop outside the gate |
| Disposal after a completed move | Observe `_moveActive == false` and use an already-completed wait; the existing cleanup gate still serializes retirement |
| Move completion | Keep the bit true through the entire move, including catch-path awaited cleanup; in `finally`, clear the bit and complete/clear any captured waiter under the existing ordering discipline |
| Multiple disposals | All callers observing the active move share its waiter; callers arriving later still share the same cleanup completion |
| Exceptions | The lifecycle waiter completes successfully even when `MoveAsync` fails; preserve original move exceptions and separately reported cleanup failures |

The same lock must cover the bit and waiter. Otherwise a disposer can miss the
last completion, or cleanup can invalidate the batch while the mapper still
uses its `RowReader`. Closing admission in that lock prevents a new move from
starting after a disposer has selected its wait target. Completing the waiter
with `RunContinuationsAsynchronously` preserves the existing separation between
publication under the lock and disposal continuation work.

Using the actual `MoveAsync` task as the disposal waiter would change exception
behavior: a mapper fault would be rethrown by `DisposeAfterMoveAsync` before its
own cleanup await, even when the provider cleaned up successfully. Similarly,
recording that task only after calling `MoveAsync` leaves a gap when a fully
synchronous mapper has entered but the call has not returned its task. The
explicit admission bit covers that gap.

Keep cleanup independent from the active-move waiter: `MoveAsync` already awaits
cleanup on EOF or failure. Making cleanup itself await that move would create
a cycle. Keep cancellation-registration draining and provider joins outside
`_gate`, and retain the existing late transport publication/closed check after
the start factory returns. Blocking synchronously on the same enumerator's
`DisposeAsync` from inside its own materializer would also wait for that
materializer to return; this change does not introduce support for that pattern.

## Focused baseline-compatible regression

Test-only commit `ec5d16dc650abaf565d35e9363dfef727bc3d718` adds two cases for each existing real provider:
`blocked-mapper-dispose` and `blocked-mapper-failure-dispose`.

Each case first fetches and maps one row. A dedicated long-running worker then
enters the second row's synchronous mapper in the same batch, signaled by an
explicit barrier. While the mapper is blocked, another move must reject
concurrent use, two disposals must remain pending, no batch disposal or join may
start, and a later move must reject closed admission. After releasing the
mapper, a test transport wrapper counts batch disposal/join and temporarily
holds the actual provider join receipt. Both disposals must still wait.

The successful mapper reads the second DTO after disposal has been requested.
The throwing mapper preserves the exact original exception, publishes it only
after cleanup, and allows both disposals to succeed when cleanup succeeds.
Repeated disposal must retain one batch release and one transport join. The
existing `Clean` check then verifies actual native owners, budgets, operation,
session/lease retirement and connection-reuse evidence. Failure cleanup releases
both controlled barriers before bounded disposal, so no intentional test gate
remains held.

The wrapper does not synthesize rows or retirement; it forwards the existing
native fixture. It adds no product API or implementation dependency. The normal
B06 verifier includes the cases in both JIT and actual Linux Native AOT runs.
They have not been compiled or executed during root's exclusive calibration.
The database agent independently read the test, `RowBatchLease` and native
fixture ownership paths and reported no source blocker. It also confirmed the
exact two-row wire size is 250 bytes under the 256-byte fixture cap, making the
second move a genuine already-buffered synchronous path. Source whitespace
verification passed. Neither review nor whitespace verification constitutes
execution evidence.

## Remaining decision

Retain the existing delayed-start/pending-fetch cancellation paths and cleanup
failure tests when evaluating the candidate. If the runtime patch changes
transport publication, cancellation registration or cleanup error propagation,
add a separately controlled delayed-start or failing-retirement concurrency
case for that specific changed boundary. This narrow proposal does not change
those paths. The baseline allocation profile and same-driver application runs
must determine whether eliminating this completion object is worth retaining.
