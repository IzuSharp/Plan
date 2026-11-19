# Perf-01: independent resolver ownership review and candidate scope

Status: source-only review of the unchanged `ea5fa528035d025bd7a28698ee7c71194432236c`
runtime. No runtime change, build, test execution or performance measurement was
performed by this reviewer. The codec agent's independently executed failure and
forced-overlap controls are retained in [source-a02-cold-import.md](source-a02-cold-import.md)
and its linked evidence. This note focuses on the prospective correction.

## Confirmed ownership mismatch

At locked .NET producer commit `297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`,
[Native AOT InteropHelpers.cs, lines 256–339](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/coreclr/nativeaot/System.Private.CoreLib/src/Internal/Runtime/CompilerHelpers/InteropHelpers.cs#L256-L339)
calls the registered resolver, then publishes its result into the module cell
with CAS. A losing publication unconditionally calls `FreeLibrary(hModule)`,
including when the returned numeric handle equals the winner. The Git blob is
`91c53377081701a00b0a5ccb293664e35714aaf0`.

Baseline `src/Interop.Negotiation/EngineModuleLoader.cs` retains its initial OS
load at lines 78–89, while `AssemblyResolver` at lines 233–270 returns that same
handle without acquiring another OS reference. Its SHA-256 is
`61056860ba77902861298892deac00651388ca9513d914d42706cc6141a90d8d`.
The resolver lock ends before the caller's CAS; serializing this lookup cannot
protect a borrowed resident reference from a later losing callback's release.

The reviewer also read the exact primary-source continuation:

| Source at the same .NET commit | Verified Git blob / behavior |
| --- | --- |
| [NativeLibrary.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Runtime/InteropServices/NativeLibrary.cs) | `04ec2888f4ae6689c7d9fc4f98e06cce82d08e26`; single-argument `Load(string)` calls `LoadFromPath`; the callback stub returns the resolver result unchanged |
| [NativeLibrary.Unix.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Runtime/InteropServices/NativeLibrary.Unix.cs) | `d9e460692dd31687bf9923e6f644c2207ae21339`; direct `Interop.Sys.LoadLibrary` / `FreeLibrary` |
| [pal_dynamicload.c](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/native/libs/System.Native/pal_dynamicload.c) | `1f46763fbdb01aeecdb36ea9f812f565c26ce0ab`; `dlopen(filename, RTLD_LAZY)` / `dlclose(handle)` |

The two additional files were fetched at that exact commit, with their Git blob
identities recomputed. Their SHA-256 values are respectively
`8ec300e474de8a3c26d7d178616f8f30c0c6acde59068c62f9239f9826d3bd7d`
and `b5a377f390f5a6af36a084f1637bfe49d446721cf7d234e2aea37cc81647442c`.
They are retained locally under `ROOT/upstream/Perf-01-dotnet-dotnet-297acf930/`.
All referenced .NET source is MIT licensed; no upstream implementation is
imported into the product.

## Minimal future correction

Keep the original validated `LoadedModule` resident for the process lifetime.
Change the resolver's alias values from a bare handle to that immutable module
record so both the original handle and exact selected path are available.
Capture the record under the existing dictionary lock; it is safe to release
that lock before acquiring the additional OS reference because bindings do not
remove or unload modules.

For a recognized import name, call the **single-argument**
`NativeLibrary.Load(module.Path)` and require the returned handle to equal
`module.Handle`. This overload does not recursively invoke the registered
resolver. On equality, transfer that newly acquired reference to the runtime;
do not put it in a `using` scope or immediately free it. With N overlapping cold
callbacks, N references are acquired and N−1 losing publications are released,
leaving the original resident reference and the winning module-cell reference.
Additional cold module cells can own their own winning references. This is not
an additional OS load on every subsequent already-fixed business call.

Preserve filename/basename conflict checks using handle identity. Unknown names
still return zero. For a recognized name, a failed acquisition must propagate
failure while leaving the resident slot intact; returning zero would enable
unrelated default search. If an acquisition unexpectedly returns another handle,
free only that new reference and fail before returning it. Never free the
original resident reference, and never hand out one extra cached borrowed
reference repeatedly as a substitute for a reference per callback.

Use the exact stored `module.Path`, including the original selected explicit
path where applicable. Do not re-resolve package metadata, choose a search-path
variant, or introduce another filesystem presence/hash gate inside the callback.
Initial validation, explicit-option revalidation, capability checks, premapping
retry, and sticky postmapping failure remain separate existing contracts.

The codec control forced eight callbacks to enter before any returned: borrowed
references produced exit −11; fresh owned references produced 64 correct calls;
fresh owned references also worked after unlinking only a fresh fixture copy.
The reviewer read the control source and independently matched the three stdout
hashes against `controls-003/commands.json`. The unlink result proves behavior
on the measured Linux environment, not a general OS guarantee. Native stack
capture was unavailable. The public callback documentation does not contain an
explicit reference-transfer sentence; the ownership requirement here follows
from the locked runtime implementation and differential control.

Warming imports would change race exposure without repairing ownership. Replacing
all imports with function-pointer calls or introducing a new platform-specific
`RTLD_NOLOAD` binding would broaden the change beyond the demonstrated need.
The descriptor success-cache experiment remains separate from this correctness
fix and must preserve its existing default/explicit-option distinction.

## Additional affected gates beyond the already planned set

Root already plans A02, A07, A17, A18, B06, B15 and B18. The following source
paths identify additional distinct boundaries for a resolver change and the
separate proposed A07 retirement retry. Reuse a passing post-change gate when
its exact binaries, inputs and configuration already cover the same boundary.

| Boundary | Relevant source and focused existing gate |
| --- | --- |
| Executor close waits for actual A07 retirement | `src/Interop.Execution/ExecutorLifetime.cs:17–79`; A08 `tests/Interop.Execution/verify.py`, especially joined workers, canceled close observers and callback self-wait rejection |
| Async stale notices, source leases, failed setup and races | `src/Verification.Interop/RaceSuite.cs` and `ChildCases.cs` construct actual `AsyncOperation` instances; A20 `tests/Verification.Interop/verify.py` |
| Another real descriptor/import consumer with owner-thread semantics | `src/Verification.ExtensionProof/AffinityProbe.cs:21–35,115–123,151` and `Native.cs`; A23 `tests/Verification.ExtensionProof/verify.py` checks loader composition beyond the sync/async proof engines |
| Streaming owners and Core-operation fixture | B16 `tests/Server.Streaming/verify.py`: bounded body ownership, cancellation, write failure and retained backing credit |
| Actual HTTP Host control operations | `src/Server.Native/NativeHost.cs:227–254` constructs A07 operations; B17 `tests/Server.Native/Program.cs` adds TLS reload/held-chunk close checks. Reuse matching final B15 real-host/protocol coverage where exact cases overlap; no need to rerun B17's embedded performance benchmark for this correctness gate |
| Existing MCP/SSE module using the same Server operation path | `src/Protocols.Mcp/Endpoint.cs:137–169` joins `Retirement` and reserves protocol writes; B19 `tests/Protocols.Mcp/verify.py` covers actual Host cancellation, metadata/payload ownership and independent package consumption |

B24's already-required fresh complete package closure and final application
consumption remain the distribution check. A resolver/A07-only change does not
itself justify every query-generator/DTO matrix or repeated unchanged native
crate builds. If native frame-credit logic also changes, add its separately
identified native ownership/escaping-slice tests rather than treating the shared
loader gates as coverage for those different semantics.
