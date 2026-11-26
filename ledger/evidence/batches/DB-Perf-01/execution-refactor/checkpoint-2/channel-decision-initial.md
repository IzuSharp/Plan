# DB-Exec-02: cursor pull channel decision (supersedes operation draft)

The root's measured database-only 1 ms retry candidate still shows material
per-batch waits. The previous `DESIGN.md` operation-controller target would remove
managed wrappers but keep a native operation and retirement retry for every batch.
That is superseded before compilation or measurement. Its exact unvalidated
source is retained as `TypedFetchController-operation-draft.cs`; it was removed
from the isolated product worktree. No result is attributed to that draft.

## Corrected caller boundary

The claim in the earlier design that a *public managed raw cursor* needs
HostStreamBatch was incorrect. At a27 its only product caller is
HostStreamTransport. HostStreamTransport is created in DataSession (two sites)
and Orm.Relations (Crud and Relations, two sites); QueryTransport forwards it.
Query.Binding/Query.Native do not expose those managed batches. Public
QueryCursor<TEntity> is a keyset pagination value, not a result memory reader.

After all those entries use scoped channel results, HostStreamBatch,
NativeHost.TakeBatch, Source.StartRetiredValueTask and the unused streaming raw
memory branch must leave production. Existing C ABI result-batch compatibility
checks can use private test fixtures. The general Interop async bridge keeps its
other real Task users and conformance tests.

## Proposed shortest native contract

Precise names are being coordinated with the native owner. Conceptually:

1. `create(cursor)` or lazy `create(session, plan, parameters)` creates one channel
   owner. It does not install a permanent callback cookie. Lazy creation defers
   preparation/open and first execution to the first request, preserving public
   lazy enumeration and standalone open-without-Execute behavior.
2. `request(channel, generation, rows, bytes, callbacks)` admits one fetch. It
   copies one request's callbacks only on successful admission. A request can be
   rejected without any callback obligation; uncertain admission quarantines.
3. Worker finishes all provider access, destroys CursorReadAdmission and relevant
   session/fetch guards, then stores the owned Buffer/error. Under the channel
   lock it moves out and clears this generation's callback slot before invoking
   its single ready notification.
4. The notification receives cookie, generation, status and bounded error POD.
   Managed UCO only copies those fields and signals its coordinator. Native code
   after that invocation uses only independent channel worker/callback tickets;
   it never reads the consumed cookie again or sends another notification for
   that generation.
5. `take_batch(channel,generation)` transfers Buffer owner/view/knownEOF once;
   `take_error` preserves SQLSTATE/provider/cleanup diagnostic payload. Generation
   checks prevent old cancel/take from affecting a later request.
6. Stop/close joins channel worker/callback tickets and cursor cleanup. A single
   generic close operation per cursor is acceptable and reuses the established
   Task retirement bridge. It is not repeated per batch. Final owner release is
   nonblocking and retains native cleanup obligations if the managed owner is
   abandoned.

## Managed reachability and publication

The per-cursor controller and stable span storage are reusable **objects**.
Normal GCHandle roots, coordinator reservations and cancellation registrations
are active-request obligations, not permanent idle self-roots. An idle cursor
has none of those strong roots; its channel SafeHandle can be finalized.

For an accepted request, root/slot exist before native callback admission. A
terminal copy is not sufficient by itself: setup must have returned, request
controls must be zero, cancellation registration fully drained, and the managed
callback must have finished its final access to request state. The native
one-shot/detached callback rule above proves no further source use of that cookie;
therefore this request does not need generic `TryRetire` polling. Native channel
tail tickets, still live when necessary, are joined at channel close.

This changes the private completion contract. It does not publish an existing
RetiredValueTask early or redefine generic AsyncSnapshot.NativeQuiet. Existing
TestRetirement counts cover actual generic operations; new channel readiness
tests must name that separate boundary instead of fabricating per-fetch generic
retirement records.

The publication gate, consume-before-reset rule and whole-cursor scheduling bits
from DESIGN.md still apply. Old public MoveNext ValueTasks retain their existing
runtime-pooled-box behavior. Callback duplication before consumption poisons;
native tests must prove exactly one detached callback for each accepted request.
As with existing retirement, arbitrary late callbacks after a proven no-future-
callback boundary violate the native contract and cannot be made safe by checking
an already freed cookie.

The stable HostTypedBatchOwner uses a sentinel SafeHandle, a separate Buffer
pointer, generation and synchronous reader count. It never reopens a SafeHandle,
rebinds a MemoryManager or exposes Memory. ReleaseBatch invalidates new reads
immediately; captured spans remain valid until the last physical read scope exits.
One generation cannot attach while that old pointer remains retained.

## Required new tail proof

A deterministic native barrier must hold the independent callback-return/worker
tail after ready. Taking the batch and starting the next generation should still
work; channel close must remain pending until that tail exits. No later worker
tail may write request-generation/result/cookie fields of the next generation.
This test is the evidence that removes the per-fetch retirement wait rather than
merely changing its timing.

Still unmeasured: allocation bytes for the new path, whole-query fixed cost,
latency, throughput and RSS. Neither source-level deletion of six `new` sites nor
the native operation removal is a substitute for those observations.
