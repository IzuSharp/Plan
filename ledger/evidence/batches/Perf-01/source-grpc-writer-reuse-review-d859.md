# Perf-01: independent gRPC writer reuse review at d859

## Evidence and decision boundary

This is a source-only review of a prospective implementation, not an applied
patch, executed regression, allocation measurement, or performance acceptance.
The reviewer fetched the two complete files below through the read-only GitHub
connector at NativeWeave commit
`d859b79eedb87dfc372be6c07e516d173c96124b`. The returned identifiers are Git blob
SHA-1 values, not binary or package SHA-256 values.

| Actual source read | Git blob SHA-1 |
| --- | --- |
| [src/Protocols.Grpc/NativeTransport.cs](https://github.com/IzuSharp/NativeWeave/blob/d859b79eedb87dfc372be6c07e516d173c96124b/src/Protocols.Grpc/NativeTransport.cs) | `75ea13973aab925620b563ff9525c0910028dbd4` |
| [src/Protocols.Grpc/Contracts.cs](https://github.com/IzuSharp/NativeWeave/blob/d859b79eedb87dfc372be6c07e516d173c96124b/src/Protocols.Grpc/Contracts.cs) | `51cd55a3b83f1562551548c65ca3219bbcea877a` |

No external .NET, Rust, Tonic, or third-party binding source was independently
fetched in this review pass. The earlier [writer reuse study](source-grpc-writer-reuse.md)
records its own upstream reads and historical evidence; this review does not
repeat or extend those execution claims. No third-party code is imported or
redistributed by this memo.

## Concrete implementation constraints

The proposed exact-E, per-transport weak reference has no identified inherent
concurrency or ownership blocker if the following constraints all hold. The
actual implementation must still receive review and execution evidence.

1. **Keep the existing complete write gate.** `NativeTransport.cs:106-130`
   rejects a second writer and releases `_writing` only after operation
   retirement. Retrieve a strong array reference, clear, encode, pin, and create
   only inside synchronous `EncodeAndCreate:132-148`. Do not capture the array
   in an asynchronous state machine or retain it in a strong idle field.
2. **Keep admission and ownership ordering.** At line 134, acquire the existing
   E-byte managed credit before `TryGetTarget` or `new byte[E]`. Preserve the
   native reservation at line 123 and pin/create/transfer/stream accounting at
   lines 141-146. Construct or update the weak handle and construct the writer
   before native operation creation: no newly introduced allocating step may
   strand an already-created native operation before `Engine.Begin`.
3. **Dispose on every encode/create exit.** Use an ordinary `MessageWriter(byte[])`
   constructor, one nullable array field, and a scoped disposal that clears that
   field on success, encoder exception, cumulative-limit rejection, and native
   create failure. Avoid an implicit primary-constructor array capture. Dispose
   the writer before releasing managed credit; reject subsequent writer access.
4. **Preserve the complete visible destination.** The current writer at lines
   228-237 allocates a zeroed exact-E array and returns all remaining capacity.
   Clear the full reused array, including tails beyond the preceding committed
   length. Preserve negative/zero/positive size hints, full-capacity behavior,
   Advance bounds, and ResourceExhausted classification. Do not grow, pool, rent
   a larger array, reduce Reserve(E), or change native copy/pin/credit ownership.
5. **State the borrowed-memory lifetime accurately.** `Contracts.cs:87-92`
   already forbids retaining the scoped destination but does not explicitly
   cover its returned Memory. Clarify that the writer and returned Span/Memory
   are borrowed only for that synchronous encoding callback and cannot escape
   or be used asynchronously. Clearing the writer field cannot revoke an
   already-escaped Memory; do not claim runtime enforcement of that contract.

## Targeted regression obligations

Reuse the existing B18 regression surface; this memo creates no test framework.
The meaningful checks are ordered messages of different lengths with full-E
initialization, slow-consumer isolation of prior payloads, exact capacity/hint/
Advance boundaries, and encoder failure followed by a successful clean write.
Also cover native-create rejection and credit compensation, a retained disposed
writer not strongly retaining storage, collection of a weak target followed by
correct fallback allocation, competing writes, backpressure cancellation,
retirement/drain, and isolation between transports with different caps.

Weak targets may disappear at any collection, so tests must not require cache
hits or an allocation improvement. A complete clear, weak-handle operations,
and each new writer still have costs. In particular, a one-response transport
has no later response to reuse its array. Keep all original quotas and protocol
semantics, and decide retention only after equivalent-load allocation, CPU,
latency, throughput, RSS, correctness, and drain measurements. This review does
not establish a speedup, causal explanation of a profile, or long-test credit.
