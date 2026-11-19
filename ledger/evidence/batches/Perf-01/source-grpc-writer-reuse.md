# Perf-01 gRPC managed writer: allocation evidence and bounded reuse proposal

## Status and scope

This is a source study, a read of an existing before calibration, and a
test-only regression specification. The product under analysis is main
`ea5fa528035d025bd7a28698ee7c71194432236c`. No runtime implementation, native
binary, dependency, benchmark payload, quota, or measurement result is changed
by this note. The root measurement owner has not accepted a writer optimization
or measured a reuse benefit. Test execution and any candidate implementation
remain separate gates after the configuration freeze.

The existing failure and prospective gRPC-only request-budget decision are
recorded in [the quota observation](grpc-baseline-quota-observation.md). Reusing
managed writer storage cannot remove the native transport-owned frame grants
described there. In particular, it does not establish that a resource rejection
was caused by the managed asynchronous retirement timer.

## Measured allocation evidence, with its attribution limit

The existing cell is
`ROOT/perf01-evidence/calibration/before-grpc-v3r1/00-ladder-8`. It used the
immutable before Native AOT server, the common independent client, and the old
4 MiB request-budget profile. Its two ordinary resource rejections remain
failures of the service standard; this diagnostic does not make the cell a
successful capacity result.

| Existing input | SHA-256 |
| --- | --- |
| `result.json` | `a7ec0d5c097b06607a7b68f9c1c098bb24e8b5ad5db064e05c0122dba24563a7` |
| `execution/client/operations.jsonl` | `4af259ad70bde24fda5a782029e25a31463aba60e37c7705ad6b822b3a4834ca` |
| `execution/server/managed-resources.jsonl` | `4b227b756347240867a3fd37fbcab830351e32fd11b8fdbe8161a5ef76052be0` |

The first and last measurement-tagged managed snapshots are:

| Snapshot | UTC | Stopwatch ticks / frequency | Cumulative allocated bytes |
| --- | --- | --- | ---: |
| First | `2026-11-19T10:11:59.5714971Z` | `14505783808847 / 1000000000` | 302,173,120 |
| Last | `2026-11-19T10:12:29.1183668Z` | `14535330678846 / 1000000000` | 2,856,527,880 |

There are 31 measurement-tagged snapshots. The two endpoints bracket
29.546869999 seconds and an approximate managed allocation increase of
**2,554,354,760 bytes**. The observer calls `GC.GetTotalAllocatedBytes(false)`
(`tests/Perf01.Protocols/Server/Program.cs:209–215`); it is a whole-process,
approximate interval counter, not an allocation stack trace or a per-call
instrument. This bracket is shorter than the complete load interval.

The 242 measured client calls received 2,470 messages and 11,004,736 payload
bytes in total. Restricting to calls whose client start and completion are
entirely inside the managed snapshot bracket leaves **2,402 received messages**
and 10,676,928 payload bytes: 117 unary, 1,181 server-stream, 1,056 duplex,
35 client-stream response messages, plus eight deadline and five cancellation
probe messages. These are received-message counts, not a server-side count of
every attempted marshal or outgoing frame.

At this profile's encoded cap `E=1,048,576`, one eager `byte[E]` for each of
those 2,402 messages alone corresponds to **2,518,679,552 bytes**, approximately
98.6% of the interval's reported allocation delta. The exact baseline source
does allocate that maximum array on each response
([`NativeTransport.cs:132–148,228–237`](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Protocols.Grpc/NativeTransport.cs#L132-L148)).
The agreement is strong evidence that this path deserves a bounded candidate.
It is **not** proof that precisely 98.6% of all allocation came from that source:
unreceived messages, calls crossing interval endpoints, approximate counter
updates, application codecs and other framework allocations are not separately
attributed by the available data.

## Existing ownership and the admissible reuse boundary

The unchanged managed write path is:

1. `WriteAsync` admits one writer under `_gate`; a second writer fails
   immediately. `WriteCoreAsync` yields before its asynchronous work, waits for
   the native reservation of the configured maximum `E`, and joins that
   reservation's retirement (`NativeTransport.cs:106–124` and
   `Server.Native/NativeRequest.cs:247–251`).
2. `EncodeAndCreate` acquires a separate **E-byte managed credit**, creates the
   maximum-sized writer, and invokes the application encoder once. The
   application callback is synchronous (`NativeTransport.cs:132–136`).
3. The writer's committed span is pinned only around the synchronous
   `nw_server_grpc_write_create` call. Rust validates the reservation and
   operation slot, copies the complete message into its own reserved storage,
   then publishes a never-started operation. Recoverable failures precede
   reservation transfer
   ([`native/protocols/grpc/exports.rs:54–99`](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/native/protocols/grpc/exports.rs#L54-L99)).
4. Only after success does managed code mark its reservation transferred.
   Managed byte credit ends as the synchronous encode/create method exits;
   native operation completion and retirement are awaited separately. A
   transport frame can outlive both managed scratch use and the operation.

The candidate is an **exact-E, per-transport weak reference to the scratch
array**, with a new scoped writer wrapper per encoding. Acquire the same E-byte
managed credit before calling `TryGetTarget`: a successful lookup promotes a
strong local owner and must already be covered by credit. If the target has
been collected, allocate the same `new byte[E]` fallback. Never retain a strong
idle array field, use a global pool, or rent a larger unaccounted array.

On a weak-cache hit, clear the **entire E-byte array** before calling the encoder.
Clearing only the previous committed length is insufficient: a valid encoder
may write into a borrowed tail and advance only a prefix. The old fresh-array
implementation exposes zeroes in later unwritten regions, so reuse must preserve
that behavior. The array remains strongly held only through the current
encoding and synchronous native copy, under the same original credit. The
existing one-writer gate is sufficient to exclude concurrent reuse on that
transport; it does not justify sharing a scratch buffer across transports.

Any weak-reference wrapper allocation or target update must occur **before** a
native create can transfer ownership. An allocation in a post-create return or
`finally` path could throw after Rust created an operation but before managed
code calls `Engine.Begin`, stranding that creator-owned operation. Constructing
the weak wrapper before the copy boundary avoids introducing that failure path.
A scoped writer may invalidate itself as the callback/copy scope ends, but must
not introduce a strong idle reference through its fields or closures.

This proposal does not grow buffers, change any size hint, change stream-byte
accounting, invoke an encoder twice, reduce native `Reserve(E)`, increase a
quota, or alter error/cancellation/backpressure handling. The previously
proposed geometric managed writer remains deferred because extra overlap credit
can reject a message accepted by the original single E-byte admission.

## Exact locked .NET source and callback contract

The installed Native AOT package's repository/SourceLink provenance was checked
in [the JSON buffer study](source-json-buffer.md): dotnet/dotnet commit
`297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`, SDK 11.0.100 and runtime 11.0.0.
The following primary files were actually fetched at that exact commit. Local
read-only copies are under `ROOT/upstream/Perf-01-dotnet-dotnet-297acf930/`.

| Primary source | Git blob / local SHA-256 | Read behavior |
| --- | --- | --- |
| [WeakReference.T.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/WeakReference.T.cs) | `cf19880b036a51aaaecba430ac38b3951dc92c5d` / `97e336dc0db6d0b573a4a82c8c4a3b4807070dc381deeb49422d620cadc9921b` | Lines 27–38 select a non-resurrection weak reference by default; 58–64 return one strong local target through `TryGetTarget`; 80–86 allocate a weak GC handle; 97–123 and 126–165 update/read it while keeping the wrapper alive. |
| [IBufferWriter.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Memory/src/System/Buffers/IBufferWriter.cs) | `b7b14d1cb4d4db1090bcd0abd796ada855fc70ad` / `aa14369349f1c24f45fb28107e69b9849d82dbce4ab3aab224b15fb18ba57426` | Lines 14–16, 30–32 and 46–48 require a fresh buffer request after `Advance` and forbid writing the old buffer; 19–29 and 35–44 require a nonempty span/memory at least as large as the hint or an exception, without a stable-buffer-identity promise. |

The files carry .NET Foundation MIT headers. No upstream implementation was
imported into NativeWeave or redistributed by this Plan change; the project
continues to use the locked runtime package. This is direct use of a runtime
ownership primitive, not adoption of a third-party buffer pool.

NativeWeave's existing `GrpcEncoder<T>` documentation explicitly calls the
destination scoped and forbids retaining the writer
([`Contracts.cs:86–92`](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Protocols.Grpc/Contracts.cs#L86-L92)).
It does **not** separately and explicitly say that a derived `Memory<byte>` must
not outlive that synchronous callback. Therefore the candidate should clarify
the XML contract to say that returned memory/span is borrowed for that encoding
scope and must not be retained or used afterward. Do not describe this sentence
as preexisting wording. Neither the old API nor `IBufferWriter` promises an
owned immutable snapshot of the destination. The tests below retain only weak
identity observations for an internal lifetime check; they do not use a borrowed
payload after the callback.

## Regression specification and remaining execution gates

The test-only source is product commit
`e77dfc1c7c463f562bcf9688cd4259b862ad1fd7`,
`tests/Protocols.Grpc/WriterContracts.cs`, invoked by the existing B18 program.
The independent codec reviewer passed its source-level baseline compatibility,
exact backing/credit assertions, failure compensation and creator cleanup. At
that source-review checkpoint neither author nor reviewer had executed a build,
JIT/AOT test or protocol load; only the committed source whitespace check ran.
Any later root-authorized baseline execution is recorded separately with its
actual command/result and binary identities. It uses a fresh real
NativeWeave H2/TLS host and the
independent locked grpc-dotnet/protobuf client for each non-power-of-two encoded
cap, 5,000, 10,000 and 65,539 bytes. It uses existing friend access to the
transport and native credit ledger; it does not add an application API or ABI.

| Case | Required behavior on both eager and candidate implementations |
| --- | --- |
| Exact maximum and incremental encoding | A valid protobuf message occupying exactly E bytes, written in small chunks, arrives byte/field-equivalent with the ordinary successful terminal status. |
| Hints and advancement | Negative hints/advances, E+1, remaining+1 and a nonempty request after filling E keep the existing `ResourceExhausted` classification. |
| Full initialization | Every encoder sees zeroes throughout E; a preceding encoder deliberately dirties the unused tail before committing only a short valid message. |
| Managed admission | Hold enough existing request credit to leave E−1 bytes. The next write rejects before invoking the encoder; held credit is unchanged, and a subsequent valid write succeeds after release. |
| Encoder exception | An encoder dirties its destination and throws; its reservation/managed credit unwind and a later valid message succeeds with clean storage. |
| Native create rejection | After encoding, hold all 40 actual operation-slot creators on the dedicated host. The real native create rejects before transfer; managed credit unwinds, every held creator is disposed and the next valid response succeeds. |
| No strong idle buffer | After a completed write and a separate continuation, force a full collection using only a weak backing observation; the old array is collectable and a later exact-size write succeeds through the fallback path. |
| One writer | Pause inside encoding, verify the original E-byte credit remains held, reject a second pending write, release and always join the first write. |
| Wire and close | Check all ordered protobuf responses and terminal status, then require zero pending requests and retained managed/native bytes after close. Server assertions are captured and rethrown outside protocol error redaction. |

The source-prepared native-create case uses the existing ABI without a
production hook: after normal output reservation and encoding, it retains a bounded set of
**never-started** close-operation creators until all host operation slots are
owned. The real gRPC create must then reject at its pre-transfer slot check.
The test releases all held creators, requires the original managed credit to
have unwound, and retries a valid message. `nw_server_close_create` only creates a job
(`native/server/host/src/exports.rs:341–357`); it does not initiate shutdown.
Never-started release is explicitly supported (`:576–588`). The exact host
capacity is `8*MaxActiveRequests+32` (`engine.rs:89–94`), so the dedicated
single-request test host needs only 40 held creators. The test requires all 40
to be actually owned, allowing at most two seconds for a transient preexisting
operation to retire. A first resource denial with fewer held creators is not
accepted as proof. Every creator uses a preallocated safe handle and is released
in failure/outer cleanup; no close operation is started. This is a recoverable
native create failure at the synchronous copy boundary, not an injected Rust
allocator OOM or a claim that process-aborting allocator failure is recoverable.

Before accepting a candidate, root must compile and run the B18 suite in both
Release/JIT and actual Native AOT against the unchanged baseline, then repeat
against the candidate. The existing H2/TLS protocol, deadline, cancellation,
metadata, pressure and retirement checks remain required. Tests should not assert
a cache-hit count or an allocation improvement; GC is permitted to discard the
target at any time.

Measure the frozen mixed and isolated unary/server/client/duplex profiles with
the same package closure and common client. Report CPU as well as allocation,
latency, throughput, RSS and drain. Clearing E bytes still costs memory writes;
weak-wrapper/GC-handle overhead may make unary calls worse because their
transport has no second response to reuse. A lower allocation counter alone is
insufficient to keep the change. Preserve native credit and protocol rejection
observations separately; this candidate does not fix them by changing quotas.

The independent codec reviewer also checked this source note against the
baseline managed path and the exact local .NET source files/hashes, and found no
source blocker. Its allocation review checked the stated arithmetic and scope,
not an independent replay of every historical client/resource row. The measured
counter and message inputs remain pinned above for that separate audit.
