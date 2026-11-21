# Perf-01: reservation-owned gRPC writer feasibility

**Decision: DEFER.** A native payload loan can reuse existing Rust ownership, but
it is not yet a small, demonstrated improvement with equivalent pin, quota and
retention behavior. Do not implement or select it on this source review alone.
No product code, builds, tests, profiles or loads were run for this study.

## Evidence and exact source scope

The preserved weak-comparison projection reports OFF streaming allocation
samples of 352.4663999312545, 351.7395931917278 and 350.83548985297955 MiB/s;
their existing mean is **351.68049432532064 MiB/s**, at C4, 16 arrivals/s and
20-second cells. This is a partial whole-process
`GC.GetTotalAllocatedBytes(false)` bracket, not exact allocation per message or
proof that every observed byte comes from the writer. The projection SHA is
`08978e38686a49df7f50ead6f61c5e5a4d0d48f9bb1ca38242d5a19788bdc84f`.
Its ON/OFF roles are not the main/final product comparison; this study awards
zero formal duration credit. See the existing
[comparison projection](../../recovery/epoch-001/weak-comparison-001/comparison.json).

The measured OFF source is `4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4`.
The read repair snapshot was `7bc9ea574729ad5cb0184d95f675b2bb9da0089f`;
the product paths listed in `sources.json` have no diff from that OFF commit.
Source identities below bind actual files read, not an unexecuted candidate.

Let **E** be the encoded cap and **N** the encoded message length, N <= E.
[`NativeTransport.cs`](https://github.com/IzuSharp/NativeWeave/blob/4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4/src/Protocols.Grpc/NativeTransport.cs)
reserves native queue/payload admission, joins reservation retirement, acquires
the original E managed credit, allocates `byte[E]`, invokes the synchronous
encoder, checks the stream limit and creates the write operation. The write
direction remains serialized until operation retirement.

On Rust's side,
[`Call::reserve` and `Reservation::prepare`](https://github.com/IzuSharp/NativeWeave/blob/4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4/native/protocols/grpc/src/call.rs)
hold one channel permit and an E+5 native credit. `prepare` currently copies N
bytes into an N-sized boxed slice, wraps it with `Bytes::from_owner`, and shares
the credit through the message and subsequent framed owner. The
[write export](https://github.com/IzuSharp/NativeWeave/blob/4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4/native/protocols/grpc/exports.rs)
checks creator/request identity, protocol phase, bounds and operation admission
before transferring the reservation. These ownership and failure boundaries
must remain intact.

## What upstream can supply

The locked bytes **1.12.1**, commit
`76c0fbb54ed4336caf9d2311658a2f4a5627c21d`, already supplies
[`Bytes::from_owner`](https://github.com/tokio-rs/bytes/blob/76c0fbb54ed4336caf9d2311658a2f4a5627c21d/src/bytes.rs).
It holds the supplied owner until the final clone drops, without copying its
payload; its own small owner allocation remains. A private owner containing
the initialized vector, visible N prefix and existing credit could use that
API. No replacement byte library or Tonic fork is needed.

Rust **1.100.0**, commit `0ef1bc386059596dada8fb65b50425aab2ea637a`, has the
existing fallible `Vec::try_reserve_exact` path. The inspected
[`RawVec::grow_exact`](https://github.com/rust-lang/rust/blob/0ef1bc386059596dada8fb65b50425aab2ea637a/library/alloc/src/raw_vec/mod.rs)
requests the exact capacity and records it. Initializing every E byte afterward
preserves the present zeroing contract. Keep the vector owner to avoid an
unnecessary shrink conversion. A payload allocation failure can use existing
`NW_OUT_OF_MEMORY` (5), which Server maps to `OutOfMemoryException`; this does
not make all surrounding small metadata allocations fallible.

This only removes the C# payload allocation and its first N-byte transfer.
[`RawEncoder` and `CreditedBody`](https://github.com/IzuSharp/NativeWeave/blob/4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4/native/protocols/grpc/src/codec.rs)
still copy into Tonic's codec buffer and then into a credited outgoing frame.
Locked Tonic **0.14.9**, commit
`4c0f455c264fe2ec9f9ab5d0cc7fd2824d5daf70`, writes its five-byte header and
invokes the encoder into its own
[`BytesMut` buffer](https://github.com/hyperium/tonic/blob/4c0f455c264fe2ec9f9ab5d0cc7fd2824d5daf70/tonic/src/codec/encode.rs).
Its [`EncodeBuf`](https://github.com/hyperium/tonic/blob/4c0f455c264fe2ec9f9ab5d0cc7fd2824d5daf70/tonic/src/codec/buffer.rs)
does not expose a whole-message ownership swap for the C# encoder. Lending its
scratch allocation across this FFI boundary would enlarge the scope and is
rejected here.

## Equivalence risks

### Pins and callback lifetime

The actual
[`GrpcEncoder<T>` contract](https://github.com/IzuSharp/NativeWeave/blob/4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4/src/Protocols.Grpc/Contracts.cs)
restricts the writer and returned spans/memory to the synchronous callback and
forbids retention, asynchronous use and access afterward. Synchronously pinning
and unpinning inside that callback must continue to work.

A private `MemoryManager<byte>` can reject later `Memory.Span` and `Memory.Pin`
access after sealing: .NET **11.0.0**
[`Memory`](https://github.com/dotnet/runtime/blob/v11.0.0/src/libraries/System.Private.CoreLib/src/System/Memory.cs)
routes those operations through the manager. It cannot revoke an already
returned span or the pointer in an outstanding
[`MemoryHandle`](https://github.com/dotnet/runtime/blob/v11.0.0/src/libraries/System.Private.CoreLib/src/System/Buffers/MemoryHandle.cs).
The handle calls `Unpin` on disposal, not on callback return. Merely clearing a
pointer field or setting a disposed flag does not establish physical safety.

Using a retained pointer after the callback violates the existing borrow
contract. However, rejecting commit solely because a handle remains alive is
a newly observable failure: the current array implementation succeeds in that
case, including when the caller only disposes the handle later. The contract
does not explicitly name derived pin handles. Treat this as a compatibility
decision requiring review, not as an automatically harmless check.

Safe handling needs physical leases while a pin exists, closure of all new
access and a proven transfer boundary. Keeping a pin alive may keep E native
bytes and their credit alive indefinitely. Freeing on cancellation/return is
unsafe; waiting synchronously for a leaked pin can deadlock cleanup. Copying N
and retaining the pinned E owner preserves more behavior but adds the overlap
described below. An unguarded pointer-backed manager, universal Pin rejection,
or a claim that all escaped views are automatically revoked is rejected.

[`NativeBuffer`](https://github.com/IzuSharp/NativeWeave/blob/4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4/src/Interop.Memory/NativeBuffer.cs)
provides a useful lease/callback pattern, not a mutable writer. Its
[`Adopt` seam](https://github.com/IzuSharp/NativeWeave/blob/4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4/src/Interop.Memory/NativeBufferFactory.cs)
explicitly excludes mutable ownership. Repurposing it would break its contract.

### E-sized retention and E-to-N alternatives

| Variant | Actual native backing and lifetime | Admission consequence | Assessment |
|---|---|---|---|
| Current OFF | Managed E during encoding; native N after copy; later framed N+5 | Original managed E and native E+5 grants | Reference behavior |
| Transfer initialized E owner, expose prefix N | E remains until the message owner drops; truncating visible length does not free capacity | Existing native E+5 covers E; retain original managed E admission for equivalence | Removes first copy and managed E allocation, but can add E-N live native bytes per queued message |
| Shrink E before transfer | May retain E or move storage; exact allocator behavior must be proved | A moving shrink can overlap old E and new N; no assumption that it fits E+5 | No free or guaranteed copyless shortcut |
| Allocate N and copy from the E loan | E+N overlap until source release; E can remain longer for live pins | Requires an additional native grant before the N allocation, or another explicitly reviewed accounting design | Added admission can reject where OFF succeeds; cannot silently use unused managed credit as native quota |

The
[`RequestBudget` ledgers](https://github.com/IzuSharp/NativeWeave/blob/4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4/native/server/streaming/src/lib.rs)
track native and managed sides separately and do not revoke existing owners
when the request closes. Actual backing, not only visible N, must remain
charged. An allocator might shrink in place, but no such guarantee was
established here. A later copy may be affordable only with fresh admission;
that is not an equivalent rejection boundary by default.

The E-owner option keeps the existing quota upper bound yet changes actual
memory residence and allocator behavior. The bounded queue does not make E-N
zero. Operation retirement establishes queue submission/control retirement,
not destruction of all downstream payload references, so it is not permission
to reuse the buffer. Neither RSS improvement nor a pass of the frozen RSS veto
can be inferred from removing managed allocations.

## Smallest credible scope, if reconsidered

An explicit Server-local acquire-view and commit-create pair would avoid
overloading unrelated handles or silently changing the old copy entry. It is
**two new ABI symbols and a net additional synchronous call per message**:
view plus commit replace one write-create. Keep the two existing async
reservation/write operations, their retirement, queue/backpressure and TLS/
Tonic ownership. Every span/Advance access should remain managed; do not add
one FFI call per small protobuf field. The extra call, manager checks and
native E allocation/zeroing require measurement, especially for small unary
responses. No new runtime, engine boundary, public C# signature or consumer
Cargo step is needed, but bindings, export coverage and precompiled Server
assets would genuinely change.

Allocate only after the original E managed grant succeeds. Preserve operation
slot validation before transfer, encoder exceptions, cancellation with a
blocked synchronous encoder, stream limits, exact zeroing, empty messages,
non-power-of-two caps, independent concurrent calls and failure rollback.
`WriterContracts.cs` and `WriterAcrossCalls.cs` currently inspect exact arrays
with `TryGetArray`; those internal storage checks would need equivalent
owner/physical-release checks, while all semantic assertions remain. XML cost
text would also need an accurate update.

**Retain:** existing bytes/Tonic APIs and the current OFF writer while other
measured work proceeds. **Defer:** the explicit native-loan candidate pending
pin semantics, complete backing accounting and isolated allocation/CPU/p99/RSS
evidence under the frozen load. **Reject:** unrevoked mutable aliases, early
credit release, uncharged shrink/copy overlap, using operation retirement as
payload destruction, or presenting zero-copy/throughput benefits as measured.

## Sources and licensing

`sources.json` records the actual reviewed product, measurement and upstream
file hashes. bytes and Tonic package manifests declare **MIT**; the inspected
.NET 11.0.0 source carries **MIT** headers. Rust source is referenced at the
repository-pinned commit under its existing **MIT OR Apache-2.0** project
licensing. This study imports no implementation and adds no dependency. A
future implementation can call the already shipped upstream APIs; existing
package notices remain required, and copying upstream code would require its
own source/notice entry. No MXC identity or implementation was assumed.
