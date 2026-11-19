# Perf-01 JSON buffer boundary study and regression specification

## Scope and evidence status

This is a source study and test-only regression specification. The product
implementation being analyzed is NativeWeave main
`ea5fa528035d025bd7a28698ee7c71194432236c`, with the locked .NET SDK
11.0.100 and runtime packages 11.0.0. No JSON allocation implementation, public
API, ABI, dependency, quota, benchmark fixture, or package binary was changed by
this subtask. No test, build, profile, or load was executed for these new cases
during the root-owned measurement window. A source review is not an execution
receipt or a performance result.

The source-only test patch is in
`tests/Server.Application/{JsonBufferFixtures.cs,Program.cs,verify.py}`.
Its committed identity is
`bb0fa6f2238918b768fb3db1c8b6dda247719d62`. The independent codec agent
source-reviewed the scoped patch and found no blocker in baseline compatibility,
quota/lifetime/error behavior, assertion propagation or the AOT execution gate.
That reviewer also performed no build, test or load. Required baseline and
candidate execution remain root-owned gates.

## Exact installed upstream source

The installed Native AOT runtime package identifies the producing repository as
`https://github.com/dotnet/dotnet`, commit
`297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`. This was read from
`microsoft.netcore.app.runtime.nativeaot.linux-x64/11.0.0/
microsoft.netcore.app.runtime.nativeaot.linux-x64.nuspec`; its SHA-256 is
`4423448f1aa83d96b92eaeae45c08040cce4e7a65fc30c68ecfb9bb55109ca96`.

The installed `runtimes/linux-x64/lib/net11.0/System.Text.Json.pdb` has
SHA-256
`e7b1d8214c78602e5b9f3ef95f9726bac5e90d9b81c6ffd33db0a572c1ae30d9`.
Its SourceLink JSON maps `/_/*` to that exact dotnet/dotnet commit, not an
assumed dotnet/runtime version tag. The files below were actually fetched from
that commit. Each listed SHA-256 digest is also present in the installed
portable PDB. Local read-only source copies are under
`ROOT/upstream/Perf-01-dotnet-dotnet-297acf930/`.

| Primary source read | SHA-256 | Relevant source |
| --- | --- | --- |
| [Utf8JsonWriter.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Text.Json/src/System/Text/Json/Writer/Utf8JsonWriter.cs) | `6a18cb27a8ee9ab3d22c5632157a391d52b0280edb4267199c3ea84c31f2a513` | Lines 35–36: growth constants; 448–482: Flush; 1206–1270: Grow and FirstCallToGetMemory. |
| [Utf8JsonWriter.WriteValues.Literal.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Text.Json/src/System/Text/Json/Writer/Utf8JsonWriter.WriteValues.Literal.cs) | `7ebf1d250786c5fa7e49e06a3d1407494f125f27518e46a592640ec3b4242127` | Lines 64–84: minimized literal capacity includes the potential separator. |
| [Utf8JsonWriter.WriteValues.Raw.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Text.Json/src/System/Text/Json/Writer/Utf8JsonWriter.WriteValues.Raw.cs) | `ffe50afcddcdbcd841e92edf2dd19d0fdba0b1b79cfa89eab28009b3299aa970` | Lines 228–279: raw-value capacity includes an extra separator byte. |
| [JsonSerializerOptions.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Text.Json/src/System/Text/Json/Serialization/JsonSerializerOptions.cs) | `6cad0e7a67341c77d21bb66eab9df209c3ff457fc3043701629d578ab91b8e54` | Lines 24, 91, 332: default buffer size is 16,384 bytes. |

Upstream files carry the .NET Foundation MIT headers. They were read for
analysis; no upstream implementation was imported into NativeWeave or
redistributed in this Plan change. The project continues to consume its locked
runtime package.

### Verified writer behavior

For an external `IBufferWriter<byte>`, the first memory request is at least
256 bytes. A later automatic growth request commits pending bytes, then asks
for `max(4096, requiredSize)`. A returned memory span smaller than that hint
is rejected. Explicit `Flush()` clears the writer's current memory and
advances pending bytes; the next write consequently uses the first-request
path again.

`JsonSerializerOptions.DefaultBufferSize` defaults to 16 KiB, but that
separate option does not set the capacity of NativeWeave's explicit
`BoundedJsonBuffer` or override the external writer's 256/4096-byte request
rules. A proposed 16 KiB initial allocation is still a product tuning choice
requiring measured justification.

## Current NativeWeave ownership and limits

The exact baseline
[`Response.cs`](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Server.Application/Response.cs#L134-L154)
validates the public call, acquires `maximum * 3` managed payload credit,
creates the bounded buffer, serializes once using explicit static metadata,
and retains both buffer and credit through the awaited body write. Its
[`BoundedJsonBuffer`](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Server.Application/Response.cs#L241-L252)
eagerly allocates the full configured maximum. Oversized/negative requests and
advances report `body_limit_exceeded`.

The same buffer is used per item in
[`Results.JsonStream`](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Server.Application/Results.cs#L235-L258).
Each item is fully serialized before its separator and bytes are sent; its
credit is released before advancing the source enumerator. The JSON cap is
per item, so the enclosing streamed array may exceed that cap.

The existing configuration admission floor is
`3 * MaxJsonBytes + MaxChunkBytes` against the lower of the managed and
per-request budgets
([`Configuration.cs:248–259`](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Server.Application/Configuration.cs#L248-L259)).
A route override retains the existing `3 * EffectiveMaxJsonBytes` floor
([`Routing.cs:283–287`](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Server.Application/Routing.cs#L283-L287)).
The actual managed credit remains a native grant obtained through
[`NativeRequest.cs:284–287`](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Server.Native/NativeRequest.cs#L284-L287).

## Compatibility issue and bounded candidate

**Verified hazard:** geometric buffer growth can make the writer request a
4096-byte next span near a finite non-power-of-two maximum. An eager full span
can have enough bytes for the actual remaining tokens while this newly
introduced growth request no longer fits. Simply retaining the same maximum
therefore does not establish unchanged success/error behavior.

**Source inference, not an accepted implementation:** a two-stage buffer can
avoid that particular hint mismatch by choosing an initial capacity `S`
only when maximum `M >= S + 4096`, then growing directly to the full `M`
at the first required expansion. Before that expansion, committed plus pending
bytes cannot exceed `S`; thus at least 4096 logical bytes remain available
when an automatic growth request commits pending bytes. Once the full buffer
is allocated, its absolute remaining span matches the eager implementation.
The smaller first request after an explicit Flush is also covered by this
bound. A first unusually large hint must still be checked against the same
logical remaining maximum before allocation.

The root is considering `S = 16384` only for maxima at least 20480,
retaining eager allocation for smaller maxima. Holding both the old and new
array during the one copy uses at most `S + M <= 2M` backing capacity;
the existing `3M` grant is retained unchanged. This source argument covers
the identified hint and old/new backing overlap issue. It is not proof of
performance benefit, a replacement for actual ownership/resource tests, or a
claim that arbitrary serializer behavior has already been executed.

No two-pass serialization is proposed: static converters may have side
effects. No pooling, extra credit acquisition, weakened admission, or gRPC
writer change is included. The separate gRPC writer currently has only its
single maximum-sized managed grant; acquiring extra growth credit could reject
a previously accepted near-quota message, as recorded in
[source-protocols.md](source-protocols.md).

## Test-only regression coverage

The new tests deliberately inspect observable bytes, limits, call count,
credit/lifecycle balance, and pending-operation behavior. They do not assert an
initial array size, allocation count, geometric factor, or selected growth
strategy.

| Case | Contract checked |
| --- | --- |
| Direct bounded writer at maxima 256, 5000, 10000, 65539 | Alternating GetMemory/GetSpan fragments satisfy requested minima; exact maximum commits all bytes; negative/oversized hints and advances fail without changing the committed prefix. |
| Public static WriteJson at 5000, 10000, 65539, with and without explicit Flush | Exact UTF-8 output, one complete parsed array, one serialization and one response completion. The largest non-power-of-two cap is beyond the proposed initial size plus 4096 and just above 64 KiB. |
| Small public Results.Json under a large route limit | Same maximum-based pregrant and balanced release even when the actual encoded body is small. |
| One-byte encoded overflow and a converter fault after 6000 small values | Failure before headers/body publication, release before handling the failure, and a successful new JSON write on the same response. |
| Credit one byte below the existing 3M request | Refusal before invoking the converter or committing headers; a later admitted call on the same response succeeds. This is a deterministic fake-transport grant observation, not a new native quota measurement. |
| Delayed asynchronous output of a multi-chunk exact-limit body | Existing full grant and borrowed encoded bytes remain valid while the first transport write is pending; dispatch/completion/disposal wait; exact bytes and one cleanup after release. |
| Injected output failure and caller cancellation while pending | Credit stays owned until the await resolves, then releases; a committed response aborts without a second response; lifecycle cleanup and dispatch completion occur once. |
| JsonStream with two exact-limit items, and with an oversized second item | Cap remains per item; prior credit is gone before the next MoveNext; the enumerator is disposed on success/error; failed item bytes and separator are never published. |
| Configuration and route freeze boundary | Existing global/per-request peak floors are accepted exactly and rejected one byte below; no admission relaxation is assumed. |

The exact-length fixture uses fragmented JSON arrays of `null` and
`false`. With `N` elements and `E` false values, its independent
canonical byte oracle is `5N + E + 1`. This avoids depending on a single
raw-value write: the locked raw-value implementation itself requests one extra
separator byte, which would make an exact-limit raw-value fixture reject even
on the old eager implementation. Explicit Flush occurs repeatedly while at
least 512 bytes of logical tail remain, preserving the old writer's 256-byte
post-Flush minimum; the final exact-limit tail is still serialized as small
tokens.

The helper records and rethrows unexpected handler exceptions after the real
component dispatcher performs cleanup. An assertion swallowed by the normal
HTTP failure handler therefore cannot silently pass. Controlled write waits
have bounded failure joins; their timeout is a failure guard, not a timer that
satisfies a required ownership transition.

Existing fake-transport behavior remains the default. Optional hooks record
credit requests/releases, hold or fail writes, and count aborts. The existing
verification script additionally runs the already-published component
executable as Native AOT, so this static-metadata fixture is exercised under
both JIT and AOT when that gate is actually run. Its existing real-socket
85-assertion gate and exact public API check remain separate.

## Remaining acceptance

These regressions are intended to pass the eager baseline and any equivalent
candidate, but they have not yet been compiled or executed. Root integration
must run them on the locked toolchain, retain any failure, and run the actual
native server and affected application/module regressions. The component fake
does not establish Rust owner retirement, native allocator peaks, real TLS
behavior, production RSS, or successful throughput.

A candidate should be retained only after separate profiling and equivalent
before/after loads show useful improvement without correctness, admission,
resource, streaming or tail-latency regression. No timing claim or 30-minute
acceptance credit is attached to this note.
