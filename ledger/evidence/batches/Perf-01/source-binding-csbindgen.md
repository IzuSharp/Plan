# Perf-01: fixed-source csbindgen comparison

Status: source inspected; no upstream build, benchmark or test was executed.
No implementation, generated wrapper or package was imported. This note adds
a narrow C#/Rust binding comparison to the existing Wasmtime study. It does
not establish a NativeWeave improvement.

## Sources actually read

The inspected project is [Cysharp/csbindgen 1.9.8][repository], commit
`b9eb1e84bb8185b78a4e8364fd948fee300329a7`. The inspected Cargo manifest and
license identify this version and MIT licensing. The ambiguous name MXC was
not treated as a known binding implementation.

| Fixed source | Git blob | Inspected behavior |
| --- | --- | --- |
| [csbindgen/src/emitter.rs][emitter], lines 130–197 | `5252cfb560d724172d09e39e2326f66f6c211505` | Build-time generation of ordinary extern/DllImport declarations |
| [csbindgen-tests/src/lib.rs][rust], lines 226–267, 405–429, 524–599 | `e2f3acfeff7377b2889febe85c868444e91f0bdf` | Input slice copy, synchronous callback examples, matching allocation/free functions and explicit Vec pointer/length/capacity ownership |
| [dotnet-sandbox/Program.cs][managed], lines 71–81, 220–230 | `47064c3f2a95ac635c9305e2397296b2dd1ce596` | Static UnmanagedCallersOnly function pointer and a bounded unmanaged Span view |
| [Cargo.toml][cargo] | `406fcc4b9cd340735e76657cce1556dea607aafe` | Fixed package version and dependency declaration |
| [LICENSE][license] | `d8c40d9357355b1b50e369b6a75034aaf161d162` | MIT permission and notice conditions |

The sandbox ByteBuffer allocation/free example is commented out. Reading it
is not evidence that it executed. The generated declarations describe the ABI;
they do not by themselves supply asynchronous retirement, cancellation, thread
safety, error propagation or a payload memory limit.

## Connection to the measured NativeWeave costs

The existing before Inspect profile contains three independent processes of
one million calls each. Each reported 2,624 allocated managed bytes per default
Inspect call. Separately, the owned codec diagnostic repeatedly reported 2,784
managed bytes inside its complete public-call bracket. The second figure is
not an attribution of every byte to Inspect. The profile records and limits
are in [source-loader-cache.md](source-loader-cache.md) and
`checks/inspect-before-003`.

csbindgen prepares the ABI declaration at generation time, with no descriptor
validation or Task construction inserted by the inspected declaration emitter
into every native call. NativeWeave already has generated imports, so replacing
its binding generator would not remove a demonstrated missing capability. The
small transferable change is to publish one successful immutable default
EngineInfo per descriptor, after the existing full loader validation. Explicit
options still run through the original validation path; failures are not added
to this new cache. This is the proposed R1 change. Its performance and concurrent
first-use behavior still require NativeWeave's own executed tests.

The Rust examples expose ownership as pointer, length and capacity, and recover
the allocation in its creating module. NativeWeave already transfers a native
owner and immutable byte view through NativeBuffer and invokes the creator's
destructor. Its managed array codec API intentionally adds an output copy;
its owned API avoids that copy. Adopting the example's raw pointer surface
would lose NativeWeave's stronger scoped-read and concurrent-disposal contract
without a measured reason. The inspected input example itself uses
`slice.to_vec()`, so this project is not evidence of end-to-end zero-copy calls.

The synchronous function-pointer example also cannot replace NativeWeave's A07
state machine: NativeWeave permits callbacks, cancellation and published results
before all native work has retired. The proposed R2 change retains the native
quiet verdict and owner lifetime. It schedules at most one immediate retry
after a real post-result Pending verdict, while keeping the bounded timer
fallback. It does not infer retirement from a completed managed Task.

| Alternative | Boundary/copy effect | Lifetime and maintenance decision |
| --- | --- | --- |
| Keep generated imports and cache successful default metadata | Native operation/destructor counts unchanged; removes repeat managed preparation if measured | Small R1 candidate; explicit options and per-descriptor identity remain checked |
| Replace generated bindings with csbindgen | No demonstrated reduction for the already-generated imports | No new generator dependency; would require re-establishing all existing ABI/API/AOT obligations |
| Expose a raw pointer/length/capacity result | Can avoid an output copy, as the existing NativeBuffer route already does | Retain the existing typed owner and scoped read instead of weakening concurrent disposal |
| Replace A07 with a synchronous callback pattern | Does not address actual asynchronous quiet/retirement ordering | Inapplicable to the existing async engine contract |

These are source-based design comparisons, not measurements of csbindgen versus
NativeWeave. No comparative upstream throughput or allocation value is asserted.

## .NET resolver ownership cross-check

The separate Native AOT resolver correction was checked against .NET 11.0.0
source commit `deae2e32bf0e018e09d64597b7c59b62b73bb3ce`, not inferred from the
csbindgen example. [InteropHelpers.cs][interop] lines 291–340 publishes the
resolved module through compare/exchange and frees a losing handle. The
inspected blob is `91c53377081701a00b0a5ccb293664e35714aaf0`.
[NativeLibrary.cs][native-library] lines 40–44 routes the single-argument
path overload to LoadFromPath; inspected blob
`04ec2888f4ae6689c7d9fc4f98e06cce82d08e26`.

Therefore R1's resolver must transfer a fresh OS reference while the loader
keeps its original process-resident reference. Returning the borrowed resident
handle would allow the losing AOT publication to free an owner it did not
receive. The candidate reacquires by the validated absolute path outside the
alias lock, verifies the same module handle and frees only a mismatched new
reference. Concurrent cold imports, retryable failures and loaded-file removal
remain explicit regressions; source inspection is not their acceptance.

## License and redistribution

csbindgen and the inspected .NET source are MIT licensed. This task imports no
source or generated output from either project and adds no redistributed
dependency. The note is original analysis with fixed source links; no license
or NOTICE file is changed. If a later implementation actually copies third-
party code, its required notices must be carried with that implementation.

[repository]: https://github.com/Cysharp/csbindgen/tree/b9eb1e84bb8185b78a4e8364fd948fee300329a7
[emitter]: https://github.com/Cysharp/csbindgen/blob/b9eb1e84bb8185b78a4e8364fd948fee300329a7/csbindgen/src/emitter.rs
[rust]: https://github.com/Cysharp/csbindgen/blob/b9eb1e84bb8185b78a4e8364fd948fee300329a7/csbindgen-tests/src/lib.rs
[managed]: https://github.com/Cysharp/csbindgen/blob/b9eb1e84bb8185b78a4e8364fd948fee300329a7/dotnet-sandbox/Program.cs
[cargo]: https://github.com/Cysharp/csbindgen/blob/b9eb1e84bb8185b78a4e8364fd948fee300329a7/csbindgen/Cargo.toml
[license]: https://github.com/Cysharp/csbindgen/blob/b9eb1e84bb8185b78a4e8364fd948fee300329a7/LICENSE
[interop]: https://github.com/dotnet/runtime/blob/deae2e32bf0e018e09d64597b7c59b62b73bb3ce/src/coreclr/nativeaot/System.Private.CoreLib/src/Internal/Runtime/CompilerHelpers/InteropHelpers.cs
[native-library]: https://github.com/dotnet/runtime/blob/deae2e32bf0e018e09d64597b7c59b62b73bb3ce/src/libraries/System.Private.CoreLib/src/System/Runtime/InteropServices/NativeLibrary.cs
