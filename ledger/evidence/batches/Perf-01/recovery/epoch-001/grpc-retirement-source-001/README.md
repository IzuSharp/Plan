# Perf-01: retained gRPC metadata diagnosis

## Status and observed boundary

This is an independent source investigation, with bounded reads of existing
ON capacity confirmation 2 at planned 240 calls/s. No product edit, build,
test, profile, load, acceptance result, or historical reclassification was
performed. Product sources inspected are OFF
`4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4` and the common ON client
`2e3995df8d86583ee9443348276ca8d918056bfc`. Their weak-array difference does not
change this native lifecycle. The root's reported 100,000-iteration completion
race diagnostic passed; that separate result does not exclude an allowed but
unobserved ordering.

Existing evidence inspected and hashed:

| Small input | SHA-256 |
|---|---|
| Failed capacity result | `b0c4a888ff53754bfa7a1baf9a749efb3c50f6653d90bb2fc2766ef4eb940e90` |
| Failed execution receipt | `f92f77eaa607592bac400ca93b09df566ff034d264d219711360a5fe9cefcef0` |
| Managed/native resource samples | `8f3d5973e0152db6d33c1cfa99595c0179f8ec9b8a0b98df5ec33a2b8c484d9b` |

The result is invalid: one generic integrity failure, nine rejected calls,
failed retirement, and adapter timeout. Recovery's 32 calls passed. The exact
active=0 / retiring=1 / managed=0 / native=92,096 signature first appears in
the inspected samples at **2026-11-20 23:18:59.507014 UTC**, during recovery,
and remains at the final **23:19:52.506728 UTC** drain sample. Active=0 is an
aggregate permit calculation, not proof of zero native operations or completed
request retirement.

The last sampled retiring=0 was 23:18:16.503517 UTC. The missing-header
`grpc-cancel` operation 9628 starts about 22.19 seconds after that sample;
every later resource sample has retiring>=1. Aggregate samples can describe
different overlapping requests, so this is not request identity correlation.
It prevents assuming that the single client failure marks the leak's onset.

## A concrete one-time-cleanup ordering remains allowed

[`RequestState`, engine.rs:799–909](https://github.com/IzuSharp/NativeWeave/blob/4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4/native/server/host/src/engine.rs#L799-L909)
updates two separate atomics. `mark_dispatch_done` swaps its flag with AcqRel;
`body_ended` stores its flag with Release. Each calls
[`release_metadata_if_done`, host.rs:147–153](https://github.com/IzuSharp/NativeWeave/blob/4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4/native/protocols/grpc/host.rs#L147-L153),
which checks both flags using Acquire loads. The following is a permitted
ordering, not a claimed observation of this failing cell:

1. The body thread stores body_done=true, but the store is not yet visible to
   the other thread, and reads dispatch_done=false. It skips metadata cleanup.
2. The dispatch thread swaps dispatch_done=true, then reads the still-old
   body_done=false. It also skips cleanup.
3. Both flags become visible as true. No further completion transition is
   necessary, and later reaping does not retry the cleanup.

Rust **1.100.0** is the repository lock. Its
[atomic model and Ordering documentation](https://github.com/rust-lang/rust/blob/1.100.0/library/core/src/sync/atomic.rs#L465-L526)
make the Acquire synchronization conditional on observing the Release value;
two loads of the old values create no cross-thread synchronization. AcqRel on
one separate flag does not supply a shared total-order completion decision.
The inspected source blob is `14e33019a45ff25f2107f175d6c9b26b9731cbfc`.

`Host::reap`, engine.rs:123–125, only tests `fully_retired`. That predicate
requires retired, body_done, zero live_ops, exactly the request-header anchor
remaining, and unshared metadata/head ownership. It does not call metadata
cleanup. `nw_server_dispatch_complete`, exports.rs:678–691, closes the budget,
discards input and reaps; it also does not retry cleanup. Thus this ordering
can leave a stable, unreapable metadata balance. It is a specific lifecycle
gap, not proof that it caused the historical sample.

## Publication and downstream owners

No normal late terminal-publication interleaving was established in the
exercised managed path. `GrpcCallContext.CompleteAsync` awaits admitted headers,
joins read/write directions, and awaits `StatusAsync`. The latter awaits both
the operation task and its physical retirement before common dispatch cleanup
([`CallContext.cs`](https://github.com/IzuSharp/NativeWeave/blob/4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4/src/Protocols.Grpc/CallContext.cs),
[`NativeTransport.cs:203–221`](https://github.com/IzuSharp/NativeWeave/blob/4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4/src/Protocols.Grpc/NativeTransport.cs#L203-L221)).
`Call::finish`, call.rs:221–250, installs terminal metadata and publishes its
queue item before returning. All four service traits publish input before
dispatch. `GrpcBody::end`, host.rs:494–503, drops the inner body before setting
body_done. `Call` alone has no permanently closed metadata latch, but that does
not establish a valid late publisher after these normal joins.

The 92,096 balance matches **77,184 request anchor + 1,024 empty initial
metadata + 13,888 three-entry 32/32 terminal metadata**. The terminal block has
72 encoded bytes; its grant is `8*72 + 4096*3 + 1024`. This is a source-derived
matching shape, not unique owner identification. `Call::release_metadata`,
call.rs:317–321, clears receiver, initial, terminal and pending frame credit.

The actual locked upstream sources further narrow one external-owner theory:

- **Tonic 0.14.9**, `src/codec/encode.rs:383–395`, converts a terminal Status
  into a trailers frame. NativeWeave attaches the terminal credit before ending
  its body. A retained complete `CodecMemory` would also retain the codec's
  greater-than-2-MiB grant under this configuration, rather than 92,096 alone.
- **http 1.5.0**, `src/header/value.rs:159–167`, adopts the supplied Bytes
  owner. NativeWeave `retain_headers`, metadata.rs:328–345, then marks every
  retained value sensitive.
- **h2 0.4.20**, `src/hpack/table.rs:231–235,274–275`, excludes those sensitive
  values from dynamic-table insertion. Existing index matches hold the supplied
  Header only in a temporary Index. `encoder.rs:110–136` keeps that Index local;
  `frame/headers.rs:992–1003` consumes the HeaderMap and returns only encoded
  BytesMut. Continuations retain encoded bytes, not the credited HeaderValues.
  Therefore this already-encoded header path does not leave request credits in
  HPACK. A not-yet-encoded external owner remains a different possibility.

The crates were read from the restored locked registry source. Cargo.lock
archive checksums are h2 `7d29020232d6aa3fb1daca64c1127cf662cf97f254ae16c18c05b8ab635fc118`,
http `918d3568bebf352712bc2ef3d46a8bcf1a75b373be6539de198e9105cbbf9ce0`,
and tonic `e2cdfc673aabd30fe8fee92e65837b644c37c5d47f0f97ae6d5e0f1237d15e1b`.
No upstream code is redistributed here.

## Minimal diagnostic that distinguishes the remaining cases

At stable idle/drain, capture the retained native request's id/method,
dispatch_done, body_done, retired, live_ops, budget pair, anchor capacity and
sharing/head-Arc counts. Capture Call phase; initial/terminal presence and
credit capacity; receiver/frame presence; and one diagnostic-only count of
**completed** `release_metadata` calls. Use try-lock classifications rather
than blocking diagnostic acquisition. Do not add per-message logging or alter
formal workload admission.

| Stable snapshot | Interpretation |
|---|---|
| Both done flags, retired, live_ops=0; initial/terminal present; completed cleanup count=0 | Cleanup never completed; distinguish a skipped helper from a still-locked cleanup using try-lock results. |
| Same quiescence, metadata present, completed cleanup count>0 | Inspect a late publisher or subsequent lifecycle defect. |
| Metadata absent but budget exceeds the anchor | Trace external metadata/frame/message credit owners. |
| A required retirement predicate remains false | Diagnose that exact outstanding operation/body/control path first. |

A reaper retry, if considered by root, must wait for retired + body_done + zero
live_ops and retain the original budget/anchor-sharing/head-owner checks. It
must not release active publisher or borrowed frame state merely to make
aggregate gauges zero. The snapshot above would establish which case actually
occurs before assigning a cause to the failed capacity result.

The [earlier source follow-up](../weak-source-followup-001/README.md) establishes
the independent missing-header classification issue and the actual client
Dispose chain. That error does not prove payload corruption, skipped disposal,
or ownership of the retained native request. Original failed evidence remains
invalid and unchanged.
