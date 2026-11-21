# Perf-01: gRPC allocation and cancellation-probe source follow-up

## Scope and status

This is a source-only investigation of the restored weak-writer comparison.
No product implementation, driver, frozen range, or historical result was
changed. No build, test, profile, or load was executed for this report. It earns
no functional, formal-comparison, capacity, or long-duration acceptance credit.

The inspected product commits are OFF
`4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4` and ON
`2e3995df8d86583ee9443348276ca8d918056bfc`. The common client source is ON.
The approximately 351.68 versus 21.54 MiB/s allocation observation prompted
this investigation; it was supplied by the completed comparison, not
recomputed here. Source consistency does not establish allocation-stack
attribution or explain the observed RSS difference.

## The actual allocation path

In OFF, [`NativeGrpcTransport.EncodeAndCreate`, lines 132–150](https://github.com/IzuSharp/NativeWeave/blob/4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4/src/Protocols.Grpc/NativeTransport.cs#L132-L150)
acquires the configured encoded-limit grant **E** and allocates `new byte[E]`
for every outgoing message. Its writer checks a fixed backing; it never grows.
ON [lines 133–162](https://github.com/IzuSharp/NativeWeave/blob/2e3995df8d86583ee9443348276ca8d918056bfc/src/Protocols.Grpc/NativeTransport.cs#L133-L162)
uses the same grant and exact-E array, weakly reused per transport and fully
cleared on a cache hit. The difference does not modify cancellation or native
ownership.

Both paths first reserve native output capacity, execute the encoder once,
pin only the committed span around synchronous native create, then await the
operation and its retirement. Rust validates the reservation and operation
slot before transferring the reservation and copying the message into native
storage ([`exports.rs:54–99`](https://github.com/IzuSharp/NativeWeave/blob/2e3995df8d86583ee9443348276ca8d918056bfc/native/protocols/grpc/exports.rs#L54-L99)).
The managed grant ends at the synchronous boundary; native frame ownership can
last longer.

The inspected fresh stream configuration has E=1,048,576 bytes, separate
64 MiB managed/native budgets, planned 16 calls/s, concurrency four, and equal
server/client/duplex weights with 32 messages and 4,096-byte Data. The ideal
outgoing count is `(32 + 1 + 32) / 3` per call: approximately 346.67 MiB/s of
E-sized writer backing at the planned rate, before other allocations. This is
a source-and-configuration consistency calculation, not actual issued load or
exact bytes allocated by this method.

## Smaller initial storage: previously deferred, not measured and rejected

R3 commit [`bf0755977b16d049ee35a192f456779ce74c3767`](https://github.com/IzuSharp/NativeWeave/commit/bf0755977b16d049ee35a192f456779ce74c3767)
contains two distinct changes. JSON's
[`BoundedJsonBuffer`, lines 241–263](https://github.com/IzuSharp/NativeWeave/blob/2e3995df8d86583ee9443348276ca8d918056bfc/src/Server.Application/Response.cs#L241-L263)
starts at 16 KiB when its maximum is at least 20 KiB, then grows once to the
full maximum. Its unchanged **3M** pregrant at line 149 covers overlapping
backings. gRPC instead retains its single **E** managed grant and exact-E
weak scratch.

A gRPC `S -> E` replacement temporarily retains `S + E` capacity. Acquiring
extra S credit can reject an incremental message that the original E-only
admission accepts near quota. Lowering E or forbidding larger messages changes
the contract. This is the existing deferred-design reason in
[source-protocols.md](../../../source-protocols.md), under “gRPC: lazy writer
with explicit overlap credit”; the [JSON source study](../../../source-json-buffer.md)
separately explains why its larger original grant permits the JSON change.

The public [`GrpcMarshaller<T>` SPI, lines 87–107](https://github.com/IzuSharp/NativeWeave/blob/2e3995df8d86583ee9443348276ca8d918056bfc/src/Protocols.Grpc/Contracts.cs#L87-L107)
has an encoder and decoder, with no independent encoded-size callback. Running
an application encoder twice is not equivalent when it has side effects.
The actual benchmark encoder uses `value.WriteTo(writer)`.

The installed Google.Protobuf **3.36.2** nuspec identifies commit
`2c74169b34066ceb8ddb6b882fcb3fb32d737a55`. Its actually read
[`MessageExtensions.cs:150–157`](https://github.com/protocolbuffers/protobuf/blob/2c74169b34066ceb8ddb6b882fcb3fb32d737a55/csharp/src/Google.Protobuf/MessageExtensions.cs#L150-L157)
does not call `CalculateSize`; it initializes the write context, encodes once,
and flushes. [`WriteBufferHelper.cs:46–50,97–112`](https://github.com/protocolbuffers/protobuf/blob/2c74169b34066ceb8ddb6b882fcb3fb32d737a55/csharp/src/Google.Protobuf/WriteBufferHelper.cs#L97-L112)
starts empty and refreshes with `GetSpan()` using the default zero hint.
The first hint therefore does not reveal this workload's encoded size.

Scratch-002/003/004 proposed cross-call **exact-E weak reuse**, not smaller
initial backing. The [completed scratch-004 report](../../../checks/grpc-scratch-comparison-004/README.md)
rejects measured candidate `9de3f74444246e356a2b12ab664ef99286309aaf`
(public tree-equivalent `12c477f0cdbc01fb026e98ac0e26eb45617424ed`) against
`db95a9fbdd18c208ba8fa3fdb6dabaa2bcc073c0` for p99/RSS vetoes despite allocation
reductions. Restoration returned to ON's tree. The
[historical layered report](../../../checks/final-layered-profiles-001/results-001/README.md)
also preserves the weak writer's RSS cost and explicitly unproven adaptive
growth. These observations do not constitute a measurement of a small-initial
gRPC writer. No trivial equivalent replacement was established here.

## Uninitialized arrays are not an equivalent drop-in

The public borrowing/bounds documentation and `IBufferWriter<byte>` alone do
not explicitly promise zero-valued bytes. Nevertheless, both actual product
paths expose zero-filled E-byte backing before the callback: OFF allocates a
fresh zeroed array; ON either does so or clears the entire recovered target.
The accepted regression source explicitly checks the complete destination
before every encoding ([`WriterContracts.cs:229–240`](https://github.com/IzuSharp/NativeWeave/blob/2e3995df8d86583ee9443348276ca8d918056bfc/tests/Protocols.Grpc/WriterContracts.cs#L229-L240)).
The preceding encoder deliberately dirties unused tail bytes
([lines 136–142](https://github.com/IzuSharp/NativeWeave/blob/2e3995df8d86583ee9443348276ca8d918056bfc/tests/Protocols.Grpc/WriterContracts.cs#L136-L142)).

[`MessageWriter`, lines 242–259](https://github.com/IzuSharp/NativeWeave/blob/2e3995df8d86583ee9443348276ca8d918056bfc/src/Protocols.Grpc/NativeTransport.cs#L242-L259)
returns the available backing through `GetSpan`/`GetMemory`. `Advance` checks
bounds, not initialization; `Dispose` only nulls its reference and does not
clear. Changing the fresh allocation to `GC.AllocateUninitializedArray<byte>(E)`
would therefore expose potentially stale bytes to application callbacks. If
such bytes become part of the committed prefix, the existing native copy does
not sanitize them. This is a compatibility and possible disclosure risk, not
a claim that a disclosure was observed.

The installed Native AOT **11.0.0** nuspec identifies dotnet/dotnet commit
`297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`. Its actual Native AOT
[`GC.NativeAot.cs:810–846`](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/coreclr/nativeaot/System.Private.CoreLib/src/System/GC.NativeAot.cs#L810-L846)
uses ordinary allocation for reference-containing types or small unpinned
arrays; larger byte arrays request `GC_ALLOC_ZEROING_OPTIONAL`. The 1 MiB case
cannot rely on implicit zeroing. Explicitly clearing the full new array would
restore the behavior, but provides no source basis to claim zeroing work was
removed. E bytes are still allocated per write. No such patch or test was made.

## Header-status classification is separate from native retirement

The common [client, lines 194–225](https://github.com/IzuSharp/NativeWeave/blob/2e3995df8d86583ee9443348276ca8d918056bfc/tests/Perf01.Protocols/Client/Program.cs#L194-L225)
asserts the special Wait response header before reading its response stream.
A trailers-only rejection can lack that marker. The assertion can therefore
report `IntegrityFailure` before the actual non-OK status reaches the existing
`RpcException` classifier. This is not proof of protobuf corruption.

Installed Grpc.Net.Client/Core.Api **2.85.0** nuspecs identify commit
`a7767e28a2c2f4e89a17e9efb95f75e8a82637d0`. The following exact sources were read:

- [`GrpcCall.cs:304–318,487–555`](https://github.com/grpc/grpc-dotnet/blob/a7767e28a2c2f4e89a17e9efb95f75e8a82637d0/src/Grpc.Net.Client/Internal/GrpcCall.cs): HTTP response publication precedes gRPC header-status validation; the headers accessor returns metadata without awaiting terminal status.
- [`HttpContentClientStreamReader.cs:86–96,129–134`](https://github.com/grpc/grpc-dotnet/blob/a7767e28a2c2f4e89a17e9efb95f75e8a82637d0/src/Grpc.Net.Client/Internal/HttpContentClientStreamReader.cs): `MoveNext` surfaces the stored non-OK status.
- [`HttpClientCallInvoker.cs:95–108,232–235`](https://github.com/grpc/grpc-dotnet/blob/a7767e28a2c2f4e89a17e9efb95f75e8a82637d0/src/Grpc.Net.Client/Internal/HttpClientCallInvoker.cs) and `GrpcCall.cs:189–248,415–435`: the call wrapper's disposal invokes actual cleanup, cancels unfinished work, and disposes the HTTP response, including the post-header reset path.

Both the call and cancellation source are already lexical `using` declarations
before the assertion. Thus the observed assertion does **not** bypass their
disposal. The retained native owner remains a separate unresolved observation;
neither its cause nor the missing-header call's actual terminal status is
proved by this source analysis.

A narrow diagnostic correction for root review is to observe one bounded
`MoveNext` only when the marker is absent, propagate a real `RpcException`, and
retain the integrity failure if a message or successful EOS appears without
the marker. It leaves the normal cancellation path unchanged and must not turn
early failures into successful intentional cancellations. No correction was
implemented here, and no historical failed sample is reclassified or credited.

## Source and license boundary

The upstream files above were read at the package-declared commits, not inferred
from current main branches. Protobuf is BSD-3-Clause, grpc-dotnet Apache-2.0,
and the inspected .NET runtime source MIT. No upstream implementation, package,
private environment map, or raw operational evidence is redistributed by this
report. Source review does not replace the pending native retirement diagnosis
or root-owned equivalent-load measurements.
