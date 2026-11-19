# Perf-01: first gRPC calibration rejection and ownership bounds

Status: source and bounded existing-result inspection only. No new workload,
profiling run, product edit, or reclassification of the failed cell was performed
for this note. The root measurement owner retains the original failed service
standard result. This is not a completed optimization or a 30-minute receipt.

## Observed result

The cell is
`ROOT/perf01-evidence/calibration/before-grpc-v3r1/00-ladder-8`.
It used the immutable before Native AOT server and common client described in
`protocol-layered/README.md`, with 8 scheduled calls/s and the frozen mixed gRPC
profile. The product producer is main
`ea5fa528035d025bd7a28698ee7c71194432236c`; the loaded Server native library is
`4827a6ecc76f871e0b4828f4ff6fe23a0d0a4ca1c57c5fc89a10a8e4d83ffe69`.

| Existing file | SHA-256 |
| --- | --- |
| `result.json` | `a7ec0d5c097b06607a7b68f9c1c098bb24e8b5ad5db064e05c0122dba24563a7` |
| `profile.json` | `19490e76a164d65098868f3cd51d576ba8bc22a581a57b563dc27786a336ae16` |
| `execution/client/operations.jsonl` | `4af259ad70bde24fda5a782029e25a31463aba60e37c7705ad6b822b3a4834ca` |

All 242 scheduled calls were dispatched, admitted, and completed. The controller
recorded 240 `ok` and two `rejected` results. The independent client recorded the
following ordinary server-stream failures; these are neither deadline nor
cancellation probes:

| ID | Expected responses | Received responses | Received payload bytes | Wire status | Client elapsed |
| --- | ---: | ---: | ---: | --- | ---: |
| 124 | 32 | 1 | 4,096 | `ResourceExhausted` | 2.626525 ms |
| 161 | 32 | 28 | 114,688 | `ResourceExhausted` | 14.554964 ms |

Both rows have `intentional_cancellation=false`, `intentional_deadline=false`,
`correctness_failure=false`, and `failure=RpcException`. The other 37 measured
server-stream calls succeeded. All five cancellation and eight deadline probes
had their expected logical success. Recovery passed, idle owner/request gauges
returned to zero, and final close reported no pending requests or retained
managed/native bytes. The existing result is `valid=true` because it is usable
overload/error evidence, while `service_standard_met=false` because zero
unexpected errors was required. The two ordinary failures alone violate that
gate (`tests/Perf01.Protocols/run.py:504-512`). No exception is being added to
the zero-error rule.

## Source-proved overlap bound

The following locations refer to the same unchanged product implementation at
the before producer commit.

1. `src/Protocols.Grpc/NativeTransport.cs:117-136` reserves the configured maximum
   encoded message size before marshaling every output. It then allocates a
   managed `MessageWriter` of that maximum size. The fixture's streaming payload
   is 4,096 bytes, but this reservation uses `E=1,048,576`, not its eventual
   approximately 4,103-byte protobuf representation.
2. `native/protocols/grpc/src/codec.rs:65-85` reserves
   `2*E + 2*C + 10` for the call's receive and encode scratch. With
   `C=32,768`, this is **2,162,698 native bytes**. The separate mandatory request
   metadata floor is `2*H + 200*48 + 2048 = 77,184` for `H=32,768`
   (`src/policy.rs:148-153` and `src/metadata.rs:minimum_capacity`).
3. `native/protocols/grpc/src/call.rs:173-199` first waits for the one-element
   output queue permit and then attempts a nonwaiting native grant of `E+5`,
   **1,048,581 bytes**. There is no payload-credit retry or waiter.
4. The output queue permit becomes available when Tonic consumes the message
   (`call.rs:337-345`). The full reservation's credit moves through `FrameCredits`
   into the independently owned outgoing frame
   (`codec.rs:200-215`). It remains charged until that `Bytes` owner and its
   aliases are destroyed by the transport. The actual exact-size frame does not
   reduce the original maximum-size credit.
5. `native/server/streaming/src/lib.rs:118-145` rejects a grant if either the
   request or global side would exceed its remaining credit. No allocation or
   quota weakening happens on failure.

Ignoring optional metadata and messages, one outstanding output grant requires
at least `2,239,882 + 1,048,581 = 3,288,463` native bytes and fits the configured
4,194,304-byte per-request cap. Two simultaneously retained output grants require
at least **4,337,044**, exceeding that cap by **142,740 bytes**. Thus a legal
transport schedule in which an earlier frame is still owned after the queue
slot becomes free can reject the next output reservation. Queue capacity one
does not imply that only one frame remains owned outside the queue.

The B18 ownership proof explicitly distinguishes the unconditional admission
floor from optional simultaneous outputs (`native/protocols/grpc/README.md`,
"Message and codec capacity"). The startup floor passing does not promise that
every allowed streaming shape fits this particular runtime budget.

## Attribution limit and next decision

This is a source-proved possible rejection path, not a captured native throw
stack for IDs 124 or 161. The existing client preserves status code 8 and the
exception type, but not the originating native grant or per-request ledger at
that instant. The 1 Hz gauge peak cannot exclude a shorter global-quota spike.
The exact failed grant and request-versus-global distinction remain unavailable
from this cell.

The quiet retirement timer alone is not established as the cause. Both output
reservation and output operation already await `operation.Retirement`
(`NativeTransport.cs:123-127`, `Server.Native/NativeRequest.cs:247-251`). Native
operation retirement and destruction of an escaped transport-owned frame are
different boundaries. In particular, delaying operation retirement can delay a
subsequent write; it is not proof that old output reservations accumulate inside
completed operation records.

Any prospective profile revision must retain this cell and its original failure,
use a new profile/selection hash, and apply exactly the same cap/message settings
to before, after, and direct producers. Increasing a cap just enough for two
grants is not proof that all 32 messages can coexist under transport backpressure.
Reducing a configured message maximum changes admission/codec allocation policy
even if the current fixed payloads still fit; such a choice must be explicit.
Neither option is a product performance gain, and neither can retroactively
make this cell satisfy the original service standard.

## Root-proposed prospective gRPC budget

Before any product modification, the root selected a **gRPC-only** profile clone
with `retained_bytes_per_request=67,108,864`. Global native and managed payload
limits remain 67,108,864 each, whole-process RSS remains 268,435,456, encoded and
decoded message limits remain 1,048,576, and payloads, message counts, TLS, and
the mix stay fixed. HTTP retains its original 4,194,304-byte per-request cap.
This is a prospective benchmark configuration decision, requiring new hashes
and fresh gRPC calibration, rather than a product change or measured gain.
The source-only mixed profile is `grpc-budget-profile-v2.json`; its only
functional difference from `NativeWeave/tests/Perf01.Protocols/profile-v1.json`
is that per-request cap. The two gRPC partition profiles and their catalog
hashes use the same cap. Root must execute the low-rate diagnostic and fresh
calibration; this note does not claim either has passed.

The managed configuration check accepts this positive cap without reducing any
other bound (`src/Server.Application/Configuration.cs:252-259`). The native
request ledger has no smaller hardcoded per-request ceiling. Conservatively
retaining all 32 maximum-size outgoing grants gives:

`2,162,698 + 77,184 + 32*1,048,581 = 35,794,474 bytes`.

For the ordinary fixture's three success trailers, the encoded metadata block is
at most 72 bytes (`perf-completed=yes`, `perf-inputs<=32`,
`perf-outputs<=32`). Its native metadata grant is therefore at most
`8*72 + 3*4096 + 1024 = 13,888` bytes. Adding the 1,024-byte empty initial-header
grant and even one full 1,048,576-byte decoded-message owner gives
**36,857,962 bytes**, below 64 MiB. This bound intentionally combines maxima that
the particular unary/server/client/duplex fixtures need not reach together. It
does not assert all arbitrary user metadata, unbounded stream message counts,
or transport/TLS/process RSS fit inside this controlled-payload ledger.

The unchanged 64 MiB **global** quota can still reject several simultaneous
calls; calibration must establish a stable offered rate under that constraint.
The proof above removes one obvious single-call overlap shortfall, not every
possible overload failure.

The direct Rust fixture reads the same per-request and global caps
(`tests/Perf01.Protocols/DirectRust/src/main.rs:23-27,69-91`). It reserves the
same fixed codec/request-metadata allowance. Its outgoing `GuardBody` instead
charges the actual frame length (`main.rs:115-119`), while NativeWeave retains
the configured maximum grant. Thus numeric limits match, but their existing
per-frame reservation policies are different. Report this difference when
interpreting capacity or direct-Rust gaps; do not describe their quota admission
paths as identical. This finite fixture comparator is not an arbitrary-protobuf
or arbitrary-metadata conformance proof.

## Later 64 MiB-cap calibration: 224/s probe-header failure

Root subsequently executed the prospective profile in
`ROOT/perf01-evidence/calibration/before-grpc-v4/07-refine-224`.

| Existing file | SHA-256 |
| --- | --- |
| `result.json` | `8a6bc34003d85fce9d1299668df43a9c3ae978211517684fe3b4e1638b8064e3` |
| `execution/client/operations.jsonl` | `0b2e274de1f3a9c6a8b684565cc8fd573f43836ea4781c434d224f60b778d57a` |
| `oracle.json` | `703ea1298e78bfcd765d11ba8a8feb947a9abe141af9f1fce36a9be56bf88e6e` |
| `requests.jsonl` | `e93ea733bc39de5104d24b6c7f600c83655c4936d4916c474f342ac4668af6aa` |

The original result remains invalid with
`response/protobuf/hash correctness failure`; this note does not loosen or
reclassify the frozen driver's check. Its aggregate measured outcomes are
6,744 offered, 6,727 `ok`, 12 `rejected`, four `cancelled`, and one `failed`.
The twelve explicit rejections are ordinary calls with the actual recorded
`ResourceExhausted` wire status. The four unexpected cancellations are ordinary
duplex calls, not the intended cancellation probes.

The one integrity failure is ID **228**, whose frozen Oracle input and expected
value are both `grpc-cancel|http2-tls|64|1`. Its independent client row records
`wire_status=IntegrityFailure`, `failure="Wait headers were not committed."`,
zero received messages/bytes, and both intentional-probe completion flags false.
Its client elapsed time is 0.531893 ms. The A21 request row preserves `failed`
with the same expected token, no retry, and completion equal to the observed
target-completion timestamp.

`tests/Perf01.Protocols/Client/Program.cs:202-206` awaits the `Wait` call's initial
headers and requires `perf-started=yes` before reading a protobuf message or
requesting cancellation. That particular assertion failed. Thus the available
evidence establishes a missing required initial header for the probe, **not an
observed corrupted payload, protobuf field or content hash**. The raw row does
not retain its underlying terminal status/trailers after that early assertion,
so it cannot prove `ResourceExhausted` for ID 228, despite the neighboring
ordinary calls' explicit code-8 errors. The exact cause of the missing header
remains unobserved. Keep this narrower explanation beside the unchanged invalid
verdict in the capacity table.
