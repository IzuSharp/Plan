# Perf-01: bounded Wasmtime .NET binding study

Status: source read only. No upstream build, test, native execution or benchmark
was performed, and no third-party implementation was imported. This study
supplies two design comparisons for the measured codec allocation observation;
it establishes neither a NativeWeave hotspot attribution nor an improvement.

## Exact sources and scope

The public binding is [bytecodealliance/wasmtime-dotnet, release v34.0.2][dotnet],
commit `dc5f3d7591aa3c1f6e7912095c3f5db4d6043ba6`, verified with
`git ls-remote` and a shallow detached checkout. Its release inputs specify
Wasmtime 34.0.2. The corresponding Rust source is
[bytecodealliance/wasmtime v34.0.2][rust], commit
`ed0d2fec1990469bff2b0346a3ba929f77a663bd`, also verified against the tag. This
is a deliberately fixed source snapshot, not a claim about the latest version.

The local binding checkout is
`ROOT/upstream/Perf-01-wasmtime-dotnet-v34.0.2/`. Three Rust C API source files
were retrieved directly from commit-pinned raw GitHub URLs into
`ROOT/upstream/Perf-01-wasmtime-v34.0.2-source-excerpts/`. No binary was fetched.

| Actually read source | Relevant behavior |
| --- | --- |
| [Directory.Build.props:3-7][props], [src/Wasmtime.csproj:95-118,183-184][project] | Release version, Linux native library selection and packaged native assets; the separate development-build download override was not executed |
| [src/Function.cs:421-490][function] | Native call, owner liveness, function-signature capture and native type cleanup |
| [src/Function.Wrap.cs:15-109][wrapper] | Successful typed-wrapper cache, binding-time signature/converter preparation, per-call stack storage |
| [src/Store.cs:111-149,283-316][store] | Single-thread-at-a-time contract, cached native context, disposal validation and creator destructor |
| [src/Memory.cs:140-272][memory] | Borrowed span bounds, memory-growth invalidation and native pointer/length access |
| [Rust crates/c-api/src/store.rs:63-119,160-165][rust-store] | Rust Store ownership and exported borrowed context |
| [Rust crates/c-api/src/memory.rs:106-132][rust-memory] | Actual Rust pointer/length exports and memory growth |

## 1. Prepare stable binding information once

`Function` obtains and copies its parameter/result kinds during construction,
then deletes the temporary native type. `WrapAction<T>` checks the requested
signature and obtains its converter before constructing a reusable delegate.
Its cached-wrapper branch reuses a previously validated matching delegate. The
delegate uses a bounded stack span and enters `wasmtime_func_call_unchecked`;
error/trap handling and owner liveness remain in the invocation path. `Store`
also captures the native context once, while its access property still checks
whether the owning handle has closed.

The transferable idea is to separate stable descriptor work from each operation
while keeping mutable lifetime checks. NativeWeave's
`ZlibCodec.Run` at baseline `ea5fa528` calls `Descriptor.Inspect()` on every call
before entering Rust. The descriptor's successful default metadata is a narrow
candidate for reuse, as described in [source-loader-cache.md](source-loader-cache.md).
This changes managed preparation, not the required native codec call and result
destructor. Wasmtime's wrapper cache supplies no proof of concurrent publication
for NativeWeave: its Store explicitly forbids simultaneous use. NativeWeave
still requires atomic publication after full successful loading, explicit-option
revalidation, retryable pre-map failure and new-descriptor identity checks.

## 2. Reuse native bytes with an explicit owner lifetime

Wasmtime's `Memory.GetSpan<T>` reads the native pointer and length through two
C API calls, validates the range, and exposes a borrowed view without an output
array copy. The inspected Rust functions return the actual Store-owned memory
address and length. The .NET owner uses a SafeHandle creator destructor and
`GC.KeepAlive` around native use. Its public span contract separately specifies
invalidation by memory growth or subsequent WebAssembly execution.

NativeWeave already returns its immutable pointer, length and creator-owned
handle in one codec call. `NativeBuffer.Read` adds a synchronous logical owner
lease and allows admitted reads to finish even when disposal closes new
admission; see baseline `src/Interop.Memory/NativeBuffer.cs:99-137,190`.
Retain that stronger concurrent-disposal contract. GC liveness alone would not
protect against an explicit concurrent `Dispose`, and an escaping span would
change the application contract. The measured owned route already avoids the
payload-sized array allocation/copy. The relevant next experiment concerns
the remaining fixed managed preparation cost, with the current owner lease and
creating-module destructor preserved.

## Measured connection and limits

Root's existing `codec-split-384-001` diagnostic completed 23,061 correct
operations with a 60.050331522-second actual dispatch span; it is not a
30-minute acceptance or a before/after comparison. Read-only aggregation of its
measurement rows found 11,516 of 11,531 owned calls reporting exactly 2,784
managed bytes allocated inside the public-call bracket. For 4 KiB decompression
case 2, the owned and array means were 2,784 and 6,904 bytes respectively. This
locates a repeatable cost worth profiling while separately observing the
payload-sized array difference. It does not assign the 2,784 bytes to the
loader; wrapper construction and other managed work share that bracket.

The exact diagnostic provenance and attribution caveat are recorded in
[source-loader-cache.md](source-loader-cache.md#observed-allocation-attribution-remains-open).
No Wasmtime-versus-NativeWeave timing or functional equivalence is claimed.

## License and copying record

The inspected binding's [LICENSE][license] is Apache-2.0 with the LLVM
exception; `src/Wasmtime.csproj:34` declares
`Apache-2.0 WITH LLVM-exception`. Its tracked tree contains no separate NOTICE
file. The inspected Rust [C API manifest:1-12][rust-manifest] declares the same
SPDX expression. Binding LICENSE SHA-256:
`a6c48161a09acc75a0e25503bab66a731eb5fba5392ed4bb4743e4ba5085327a`.

No code, generated wrapper, binary or package was copied into NativeWeave or
Plan. This note contains original analysis and source references only. No new
runtime dependency, redistribution or NOTICE change is part of the study.

[dotnet]: https://github.com/bytecodealliance/wasmtime-dotnet/tree/dc5f3d7591aa3c1f6e7912095c3f5db4d6043ba6
[rust]: https://github.com/bytecodealliance/wasmtime/tree/ed0d2fec1990469bff2b0346a3ba929f77a663bd
[props]: https://github.com/bytecodealliance/wasmtime-dotnet/blob/dc5f3d7591aa3c1f6e7912095c3f5db4d6043ba6/Directory.Build.props#L3-L7
[project]: https://github.com/bytecodealliance/wasmtime-dotnet/blob/dc5f3d7591aa3c1f6e7912095c3f5db4d6043ba6/src/Wasmtime.csproj#L95-L118
[function]: https://github.com/bytecodealliance/wasmtime-dotnet/blob/dc5f3d7591aa3c1f6e7912095c3f5db4d6043ba6/src/Function.cs#L421-L490
[wrapper]: https://github.com/bytecodealliance/wasmtime-dotnet/blob/dc5f3d7591aa3c1f6e7912095c3f5db4d6043ba6/src/Function.Wrap.cs#L15-L109
[store]: https://github.com/bytecodealliance/wasmtime-dotnet/blob/dc5f3d7591aa3c1f6e7912095c3f5db4d6043ba6/src/Store.cs#L283-L316
[memory]: https://github.com/bytecodealliance/wasmtime-dotnet/blob/dc5f3d7591aa3c1f6e7912095c3f5db4d6043ba6/src/Memory.cs#L140-L272
[rust-store]: https://github.com/bytecodealliance/wasmtime/blob/ed0d2fec1990469bff2b0346a3ba929f77a663bd/crates/c-api/src/store.rs#L63-L119
[rust-memory]: https://github.com/bytecodealliance/wasmtime/blob/ed0d2fec1990469bff2b0346a3ba929f77a663bd/crates/c-api/src/memory.rs#L106-L132
[license]: https://github.com/bytecodealliance/wasmtime-dotnet/blob/dc5f3d7591aa3c1f6e7912095c3f5db4d6043ba6/LICENSE
[rust-manifest]: https://github.com/bytecodealliance/wasmtime/blob/ed0d2fec1990469bff2b0346a3ba929f77a663bd/crates/c-api/Cargo.toml#L1-L12
