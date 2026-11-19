# Perf-01 TypedStream move-completion review

Status: **source analysis and proposed concurrency regression review**. No
runtime patch, build, fixture execution or timing was performed by this reviewer.
The source examined is `src/Data.Streaming/TypedStream.cs` inherited unchanged
from product baseline `ea5fa528035d025bd7a28698ee7c71194432236c`.

## Candidate cost and scope

`Enumerator.MoveNextAsync` constructs a new non-generic `TaskCompletionSource`
on every admitted move (`TypedStream.cs:125–135`). It does so even for the next
row already present in the retained batch. A complete 100-row `ToListAsync`
normally makes 101 moves, including the final false result, and therefore
executes this constructor 101 times. This is a source-derived construction
count, not a measured allocation-byte total or latency attribution.

The eager object exists so concurrent `DisposeAsync` can join an active move.
The proposed candidate keeps `MoveAsync`, all await/cleanup behavior and the
existing `_cleanup` guard, but uses a gate-protected active-move Boolean for
admission and allocates one shared completion waiter only when disposal actually
overlaps an active move. It does not remove the normal move task, transport
future, batch ownership or cleanup task.

## Required concurrency and ownership invariants

1. Set active-move admission under `_gate` before invoking `MoveAsync`.
   Reject a second move while that Boolean is set, including when no disposal
   waiter has ever been allocated. Waiter-null is not a concurrency predicate.
2. `DisposeAsync` sets `_closed` and reads active state under the same gate. If
   active, it creates or reuses the one waiter before leaving the gate. If the
   move has already finished, it can join `Task.CompletedTask` and proceed to
   the existing once-only cleanup path.
3. Clear active state and detach/complete any waiter only in the move's existing
   `finally`, after synchronous materialization and any exception cleanup have
   finished. Preserve `RunContinuationsAsynchronously`. A waiter publication
   racing with move completion must not be lost.
4. Disposal may request native stop during a materializer, but cannot release
   its retained batch or start final transport join until that materializer has
   returned. A move admitted before disposal can still produce its owned result,
   matching existing behavior. Do not add a new post-materialization rejection.
5. Multiple disposals share the active waiter and the existing `_cleanup` task.
   Keep registration drain, linked-token disposal, native `JoinAsync`, cleanup
   failure attachment and original materializer exception semantics intact.
   The move waiter cannot replace the separate cleanup completion owner.

## Independently reviewed test proposal

The codec agent authored a baseline-compatible test-only diff in
`tests/Data.Streaming/Program.cs`, independently reviewed here before commit.
It uses the actual SQLite and PostgreSQL fixture transports. The first row primes
a retained batch; a dedicated worker blocks the second synchronous materializer.
Before disposal, a concurrent move must reject with `ConcurrentUse`. Two
disposals then must remain pending without releasing the batch or starting
transport join; subsequent admission must reject as disposed.

The frozen wire layout fits the two initial rows in one batch:
`96 + 2*16 + 4*24 + 2*(8+5) = 250` bytes, below the existing 256-byte bound.
The test also checks `Fetches == 1`, so an unintended second fetch cannot silently
replace the synchronous cached-row case. A test-only wrapper gates the genuine
provider join receipt after materialization, verifying exactly one batch release
and one join. The success variant reads the second row's owned values; the
throwing variant preserves the original exception after cleanup. Failure paths
release both gates before bounded disposal.

The source review passed the fixture/lease lifetime, move admission, waiter and
once-only cleanup assertions. Existing `NativeFixtureTransport`, `RowBatchLease`
and broader B06 cases remain in use. Neither the author nor this reviewer had
compiled or run the new tests at review time. Their eventual commit identity and
actual baseline/candidate JIT/Native AOT results belong in the integration
handoff. This review does not establish that the proposed optimization is useful;
the same frozen application workload must measure that decision.
