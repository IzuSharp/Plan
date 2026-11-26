# DB-Exec-02: private typed-fetch reuse candidate

Status: proposed implementation, authorized by root for an isolated worktree;
no allocation or latency result is claimed. Base product commit is
`a27ff3189bd48b9c08d58e38338b2bfde7669bdd`. Worktree:
`worktrees/DB-Exec-02-typed-fetch`, branch `task/DB-Exec-02-typed-fetch`.
The before/B/C/R4 sources, binaries and allocation overlays remain independent.

## Decision

Use a cursor-private fetch controller and generation-checked, synchronous span
view for the formal Fluent/Prepared/typed SQL enumeration path. Keep the existing
one-shot raw `IStreamBatch` path for consumers that may retain a
`ReadOnlyMemory<byte>` or an independent fetch result. Do not add arbitrary reset
to `AsyncOperation`, reuse a disposed `SafeHandle`, or rebind an old memory
manager to a new allocation.

The new success path has one controller and one finalizable batch lifetime owner
per cursor. Each fetch creates its native operation and native batch as before,
but transfers their raw creating-module handles into those stable private owners.
Its await result is a value receipt `(owner, long generation)` with no public
escape. No fresh managed operation handle, operation context, two operation
locks, native buffer handle wrapper or memory manager is needed on that path.
This is a source design target, **not measured 0 B**. Runtime pool misses,
cancellation races, failure objects, configured codecs, query construction and
application results remain separately attributable.

## Exact completion states

| State | Native ownership and transition |
| --- | --- |
| Idle/consumed | No active operation, root, registration or coordinator reservation. The previous receipt has been consumed. A retained frame must be released before another fetch. |
| Setup | Create operation; root controller and reserve coordinator before callback admission. Registration may run inline before assignment. Setup failure compensates the operation if no native obligation was accepted; uncertain setup quarantines it. |
| Accepted | Operation exists and is rooted. Logical control count prevents release while a start/cancel/take/retire call is using its pointer. Terminal callback only copies POD and signals; it does not map or publish. |
| Draining | Setup has settled, registration has drained, accepted terminal outcome is copied. Take/map runs under a control lease. Cancellation is a request; native success may win it. |
| Retiring | `TryRetire == OK`, zero controls and callback entries, registration drained, result processed. Only then release operation, free root and release coordinator slot. Pending stays pending; failures retain quarantine and poison. |
| Published/unconsumed | Observer runs after retirement, then the completion core publishes under a private publication gate. The core uses asynchronous continuations. The cursor cannot begin another fetch yet. |
| Idle/consumed | The private internal `GetResult` takes the same publication gate, validates the token and completion, and marks consumption. A later fetch resets the core under that gate only after both retirement and consumption. |

The publication gate is necessary even with `RunContinuationsAsynchronously`:
another worker may enter `GetResult` before the producer's `SetResult` returns.
It must not reset that core while the old setter still uses it. No state for the
old generation may be written after leaving the final publication gate.

`CoordinatedCallback` scheduling bits belong to the whole cursor and are never
reset per fetch. It is not completed when one fetch retires. A next fetch that
starts while the previous `IThreadPoolWorkItem.Execute` is finishing only marks
the existing context dirty. Its existing tail reads dirty/scheduled under one
gate and schedules that next generation; it cannot erase a reset schedule state.
Only permanent cursor cleanup completes scheduling. Reservation/root lifetime
still covers each active operation only: an idle cursor is not self-rooted and
can be abandoned safely.

The internal fetch ValueTask never escapes `TypedStream.MoveAsync`. The public
MoveNext ValueTask remains the existing .NET pooled async-method box, which is
returned only when its own GetResult is consumed. A completed but unconsumed old
public move, or its AsTask result, therefore cannot be overwritten by fetch reuse.
The core's short version is a protocol check, not a proof of safe arbitrary
pooling; single private consumption and the long receipt generation supply the
actual boundary.

## Batch and row ownership

The stable cursor batch owner holds a sentinel SafeHandle lifetime and a separate
current native buffer handle. It is disposed once at final cursor cleanup and
never reopened. Each attach increments a long generation. A read scope verifies
the generation and takes a physical lifetime reference plus a reader count.
ReleaseBatch immediately makes new reads fail, but defers the native release
until the last active synchronous scope exits. A new frame cannot attach until
the previous pointer has actually been released and the reader count is zero.

The scoped row lease keeps only shape metadata, row count and owner/generation.
It uses the same complete NWDB validation implementation over a span, then
materializes rows synchronously. RowReader still checks live lease, projection
and table token, ordinal and exact codec/nullability. ValueCodec receives the
same span with the same NULL and conversion exception rules. No unchecked public
API is added. Strings, arrays, JSON and DTOs own their results as before.

Raw batches retain their immutable one-shot NativeBuffer + HostStreamBatch
identity. MemoryManager.CreateMemory stores the manager object with no generation
token; reusing that object would revive old memory against new bytes. Existing
raw held-scope/dispose/abandon tests remain mandatory, unchanged.

The typed enumerator already reuses one RowBatchLease and uses a pooled MoveAsync
state machine. The proposal does not count those existing optimizations as new.
Both QueryContext's stop wrapper and Prepared streams must select the new private
transport seam; wrapping must not hide it. EOF retains source admission, token
and native cursor admission checks and does not perform extra prefetch.

## Native retirement latency is a separate issue

`DbOperation::complete` invokes its terminal callback before `lease.reset()`.
The callback source can therefore still be live after the UCO entry has returned.
Neither `_callbackEntries == 0` nor a terminal batch is permission to publish.
The reusable controller uses the source coordinator's actual retry policy and
waits for successful native TryRetire. The generic 10 ms timer, a database-only
1 ms policy, and an eventual explicit native quiet notification are separate
candidates: source reuse alone does not eliminate their wait. This work does not
change native notification, coordinator timing or the B/C timing evidence.

## What is known about allocation

Current source constructs these six managed objects per successful raw fetch:
OperationHandle; RetiredValueTask; its control gate; CoordinatedCallback's
scheduling gate; NativeBuffer; HostStreamBatch. This is a construction inventory,
not a byte-size observation. GCHandle and coordinator slots are not claimed as
managed objects. CancellationTokenSource can reuse its callback-node freelist;
ThreadPool queues an existing IThreadPoolWorkItem; .NET's async box pool only
allocates on misses. Neither is counted as a mandatory per-fetch object.

At query/cursor scope there remain parameter frame snapshots, stream/factory and
enumerator state, open/close Task bridges, native owner wrappers, close controller,
one row lease, cancellation/linked sources when required, and cleanup completion.
List/DTO/string allocations are measured by the already frozen mapper/List seam.
The roughly 20.8 KB non-seam difference in a reported 1,000-row run is not assigned
to these six objects by inference and is not called framework allocation.

## Required deterministic gates

1. Accepted result waits for actual native quiet, registration drain, no callback
   or physical/logical control leases, and the creating operation destructor.
2. Delay old work-item tail while a consumer starts the next generation; no lost
   dirty notification, premature release, cross-generation status or root reuse.
3. Delay publication setter return; private GetResult/next start cannot reset its
   core. Keep an old completed public MoveNext unconsumed and verify it and AsTask.
4. Inline cancellation, held cancellation callback, OK winning cancel, native
   cancellation token/task identity, enriched OCE identity, observer override.
5. Rejected setup vs indeterminate start, duplicate callbacks, take/validation
   failure, TryRetire failure, quarantine and source poison retain real ownership.
6. Current frame active/read-held prevents replacement. Dispose invalidates new
   reads immediately, held span survives until scope exit, old generation never
   reads new bytes, finalizer releases abandoned frame once.
7. All shape/type/NULL/UTF8/row quota and foreign-token errors preserve order and
   cleanup; mapper failure and early stop preserve the connection contract.
8. Source/session/query close after known EOF retains existing error boundaries.
9. Public typed consumer 1/100/1000 on both providers; no extra SQL/step/prefetch.
   Existing raw MemoryManager lifetime tests continue on their independent path.

Allocation-only verification follows correctness: separate exact synchronous
scopes for new controller setup, per-fetch setup, take/adopt, validation/attach,
and publication, with instrumentation overhead and whole-process bytes/GC retained.
Each scope uses same-thread before/after counters and preallocated traces; no
async thread-local total, cross-run subtraction or estimated DTO graph. Formal
timing binaries have no allocation instrumentation. A measured remaining object
or runtime pool miss is reported rather than rounded to zero.

## Primary runtime evidence

Actual installed runtime and NativeAOT package pin dotnet/dotnet VMR
`297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`; the runtime v11.0.0 mirror commit is
`deae2e32bf0e018e09d64597b7c59b62b73bb3ce`. Exact source hashes and mirror byte
comparison are in `upstream/source-receipt.json`.

- [MRVTSC](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Threading/Tasks/Sources/ManualResetValueTaskSourceCore.cs): Reset/version and asynchronous continuation publication.
- [Pooling async builder](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Runtime/CompilerServices/PoolingAsyncValueTaskMethodBuilderT.cs): cache return occurs in GetResult.
- [CancellationTokenSource](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Threading/CancellationTokenSource.cs): callback-node freelist, registration identity and drain.
- [MemoryManager](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Buffers/MemoryManager.cs): memory retains manager identity, not a generation.

No runtime source behavior above is used to assert a measured allocation count.
