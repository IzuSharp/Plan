# Perf-01 gRPC frame credit: source proof for releasing unused reservation

## Decision and scope

A narrow source-supported candidate exists: after `CreditedBody` finishes its
existing independent frame copy and drops the Tonic frame, reduce the original
maximum-sized output grant to the complete new `Box<[u8]>` backing length.
Keep the original native `Reserve(E)` / `E+5` admission, the separate codec
scratch grant, the copy, yield threshold one, and the escaped owner lifetime.
Do not shrink any generic `Bytes` slice merely to its visible length.

This note analyzes unchanged product main
`ea5fa528035d025bd7a28698ee7c71194432236c`; it makes no runtime edit and reports no
optimization result. The old 4 MiB-cap rejections and later 64 MiB-cap overload
observations remain in [the original observation](grpc-baseline-quota-observation.md).
They motivate the study but do not identify the exact failed native grant.
The managed weak scratch proposal is separate in
[the writer study](source-grpc-writer-reuse.md); neither candidate depends on
accepting the other.

## Current owners, in order

Here `E` is the configured encoded-message maximum, `L` the actual protobuf
length, and `F=L+5` the complete identity-compressed gRPC frame length.

| Boundary at the pinned product source | Live payload backing | Credit retained |
| --- | --- | --- |
| `call.rs:173–199`, reservation | No message allocation yet; one output queue permit | Full `E+5`, acquired atomically against request and global native budgets before allocating payload |
| `call.rs:83–101`, synchronous preparation | Exact independent protobuf `Box<[u8]>` of L bytes, wrapped in owned `Bytes` | The same `Arc<Credit>` is held by both the backing `Allocation` and the queued `Item` |
| `call.rs:340–344`, output poll | Item's protobuf `Bytes` is moved into Tonic; no clone is made | Item's other credit reference moves into the one-element `FrameCredits` slot |
| `codec.rs:168–179`, encoder | Message bytes copy into Tonic's existing encode buffer; `drop(item)` destroys the original message backing | Full `E+5` remains in `FrameCredits`; Tonic scratch is independently covered by `CodecMemory` |
| `codec.rs:200–211`, body wrapper | Tonic frame aliases its encode buffer while a new F-byte boxed copy is made; then `drop(data)` ends that Tonic alias | Original `E+5` covers the independent copy; separate codec scratch grant remains intact |
| `codec.rs:212–215`, escaped owner | Only the new complete F-byte boxed frame escapes to Hyper | Current product retains the full `E+5` in that owner's `Allocation` until its final alias drops |

The exact code is
[`call.rs`](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/native/protocols/grpc/src/call.rs)
and
[`codec.rs`](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/native/protocols/grpc/src/codec.rs).
`RawEncoder` takes its `Bytes` argument by value and drops it after the copy.
No original-message clone is exported by these paths. The outer body guard's
`_memory` field is declared after `inner`, keeping the shared codec grant through
destruction of Tonic's internal backing (`codec.rs:186–191`).

The separate unchanged codec grant is `2*E + 2*C + 10`, with `C` the bounded
incoming chunk size (`codec.rs:65–85`). It continues to cover the eager receive
and encode capacities. Shrinking the output grant after the copied frame exists
does not reduce that codec credit or claim that Tonic's backing is F bytes.

## Locked upstream backing and alias proof

The actual before native producer manifest identifies rustc 1.100.0, commit
`0ef1bc386059596dada8fb65b50425aab2ea637a`; its compiler binary SHA-256 is
`5073422953727c9427a76b7fce03aa9404da46315e5a1e4965389512a41e8db0`.
The manifest is `ROOT/perf01-build/before/native-stable/manifest.json`, SHA-256
`2d61e61b003cd09084e0cd28f5744b06b2a226425b51c7c414566e15a0c41f3f`.
The following Rust standard-library sources were actually fetched at that exact
commit, rather than inferred from a current stable tag.

| Pinned Rust primary source | Git blob | Relevant proof |
| --- | --- | --- |
| [alloc/slice.rs](https://github.com/rust-lang/rust/blob/0ef1bc386059596dada8fb65b50425aab2ea637a/library/alloc/src/slice.rs) | `438549160a1c63fce11adf84fbba59953638a40a` | Lines 372–376 select the Global allocator. The trivial-copy specialization at 444–457 allocates `Vec::with_capacity_in(slice.len())`, copies the bytes and sets that exact length. |
| [alloc/raw_vec/mod.rs](https://github.com/rust-lang/rust/blob/0ef1bc386059596dada8fb65b50425aab2ea637a/library/alloc/src/raw_vec/mod.rs) | `2a1c30509ebaf25f273d8b99b2d5e15b292e03b6` | Lines 466–503 allocate the requested array layout and retain the exact requested logical capacity, with no geometric growth in this construction. |
| [alloc/vec/mod.rs](https://github.com/rust-lang/rust/blob/0ef1bc386059596dada8fb65b50425aab2ea637a/library/alloc/src/vec/mod.rs) | `ddc65e17bae0ba0ce91c6d31821557a6247a4062` | Lines 1514–1520 do not shrink when capacity already equals length; 1643–1650 convert that existing backing into `Box<[T]>`. There is no second conversion allocation in this exact `u8` copy path. |

Consequently the existing `data.as_ref().to_vec().into_boxed_slice()` in
`CreditedBody` creates independent F-byte logical backing. During its copy,
the still-live Tonic frame is covered by the unchanged codec grant, while the
new boxed storage fits under the original `E+5` grant. After `drop(data)`, no
Tonic alias is exported by the wrapper. Allocator metadata, arena rounding and
process RSS remain outside the project's controlled payload ledger, as before;
the shrink must use the entire Box length, not an assumption based on a sliced
transport view.

The exact locked registry sources read are under
`ROOT/perf01-toolchain/cargo/registry/src/index.crates.io-1949cf8c6b5b557f/`:

| Package / source file | Source-file SHA-256 | Read behavior |
| --- | --- | --- |
| Tonic 0.14.9, `src/codec/encode.rs` | `3bd57e6af594c00bab515f0ca8d2cb231fe448fc70984700f75dd8a994fd27b2` | Lines 69–83 allocate the configured encode backing; identity does not allocate a compression buffer. Lines 131–145 consume one item and yield immediately when the threshold is one. Lines 174–175 and 196–203 add the five-byte header and invoke the encoder by value. |
| bytes 1.12.1, `src/bytes.rs` | `eee15c02105022837d6ed01c6863fee58802ce7bd7c300e158521c9ae61257fc` | Lines 247–289 transfer the `Allocation` into a single owner. Lines 1114–1126 clone its reference-counted owner and 1144–1163 drop it only after the final reference. Therefore a retained one-byte slice still owns the complete F-byte Box. |
| Tokio 1.54.1, `src/sync/semaphore.rs` | `458bf1436ad8254aff8a40faf74e8ff2e724680eed09c008f519fcc9caa41f08` | Lines 1355–1387 provide `OwnedSemaphorePermit::split`; 1407–1410 return the remaining permit count on Drop. This is a mature partial-return primitive, but it is not the type used by NativeWeave's paired byte ledger. |

Cargo.lock's package archive checksums are respectively
`e2cdfc673aabd30fe8fee92e65837b644c37c5d47f0f97ae6d5e0f1237d15e1b`,
`fc652a48c352aef3ea3aed32080501cf3ef6ed5da78602a020c991775b0aff04`, and
`b52fd3255258d26fac7264ab5a76b53c13367136dc011d3d6ad4f8ed070396a3`.
No upstream implementation is copied into the product by this study, and no
new dependency or distributed third-party code is proposed. Existing locked
crate/runtime licensing and notices continue to apply.

## Minimal ledger operation and safe placement

`native/server/streaming/src/lib.rs:118–142,173–192` uses NativeWeave's own unique
`Credit`, with one capacity and two mutex-protected usage counters. Admission
and final Drop always lock global usage before request usage. It is not a Tokio
semaphore permit. Replacing this with two independent semaphores would introduce
new acquisition and rollback semantics and is unnecessary for this candidate.

A small unique-credit reduction can validate `0 < remaining <= current`, compute
the unused difference, acquire the same global-then-request locks, subtract the
difference from both usage counters, and set the credit's remaining capacity.
All validation and checked arithmetic must happen before changing either
counter. An equal-capacity call can be a no-op. Final Drop then returns only the
remaining capacity. This adds no payload waiter, callback, allocation, retry,
quota increase or request reopening; returning an existing grant remains legal
after the business request closes.

The only proposed caller is after both the existing boxed copy and
`drop(data)` in `CreditedBody::poll_frame`. Take its `Arc<Credit>` as a mutable
local and use `Arc::get_mut`. Source ownership indicates it is unique there:
the queued item's other reference moved into `FrameCredits`, and the original
message's `Allocation` reference dropped in `RawEncoder`. If an unexpected alias
prevents uniqueness, **retain the full original grant** and publish the frame
unchanged. Do not add interior mutability to a shared credit, assume uniqueness
from a reference count, or turn a missed optimization into a protocol error.

Shrink to `storage.len()` while that complete boxed owner is local, then publish
the same `Allocation { storage, _credit }`. Its field order drops storage before
the final credit. Keep the existing assertion that the frame fits the original
pregrant. Empty protobuf messages still have a five-byte frame and need a
positive grant; trailers and errors follow their unchanged non-data paths.
Do not change the generic HTTP `OwnedBuffer::slice` or metadata owner policy.

## Targeted regression and measurement gates

The source proof is sufficient to prepare a candidate, not to skip execution.
Root must retain the before package and implement only after the common freeze.
The following tests distinguish unused reservation from live backing:

- Unique credit: smaller/equal reductions, invalid zero/increase rejection with
  unchanged counters, repeated reduction, close-before-return, and final Drop
  must reconcile both request and global ledgers exactly. Exercise two request
  budgets sharing one global budget so reduction/drop/acquisition use the same
  atomic lock order and never exceed either cap.
- Actual Tonic identity frames: empty, small and exact-maximum protobuf messages
  must keep the full initial reservation before encoding. After the independent
  frame copy, the owner retains F; an exact-maximum frame remains E+5.
- Retained alias: hold a one-byte slice, drop the original frame, body, call and
  request scope, and require the complete F-byte charge until that final slice
  drops. The existing `escaping_framed_slice_holds_full_grant_after_response_and_call_retire`
  test near `native/protocols/grpc/src/tests.rs:462–510` already supplies the
  right lifecycle; its current 1,029-byte expectation for a ten-byte frame must
  be deliberately updated with an explicit full-frame backing assertion.
- Unexpected credit alias: retain an additional Arc in a focused fixture and
  require the conservative full-grant fallback. Do not use unsafe mutation to
  make this test pass.
- Failure/cancellation/backpressure: encoding failure or dropped body before
  the copy must release the unchanged full grant. Multiple retained frames must
  each keep their own complete backing; a full request/global cap must still
  reject the next initial E+5 admission without retry or waiting.
- Shared regressions: ordinary HTTP retained-slice and queue/flush tests must
  keep their existing whole-backing expectations; only gRPC's proven independent
  frame transition calls the new reduction operation. Repeat B18 protocol,
  metadata, deadline, cancellation and close checks against the actual package.

Finally compare the same frozen before/after gRPC mixed and isolated-cardinality
profiles, resource limits, TLS and direct producer. There is an extra pair of
ledger locks per successfully reduced frame, which may cost CPU even when no
quota pressure exists. Measure that cost and any changed success capacity;
keep original failures and distinguish fewer unnecessary resource rejections
from latency or allocation improvements. No improvement percentage or final
retention decision follows from this source proof alone.

The queue permit can become free before the framed-copy/shrink boundary. A new
initial E+5 reservation racing that interval can still fail against the old
full grant; no waiter or retry is being added to hide that outcome. The unchanged
per-call codec floor can also exhaust the global budget by itself at sufficient
concurrency. This candidate releases only unused capacity proven at one later
ownership transition, and does not guarantee that every resource rejection in
the preparatory calibrations disappears.

## Independent source review

The codec reviewer independently read the baseline managed/Rust ownership and
paired-credit code, fetched all three Rust standard-library files at the exact
compiler commit and matched their Git blob IDs, and checked the locked Tonic
and bytes sources/file hashes. It found no source blocker in the copy/drop,
unique-credit reduction or conservative alias fallback proof. This review did
not edit runtime code or execute a candidate, test, build or protocol load.
