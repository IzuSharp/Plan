# Perf-01: actual Native AOT cold-import ownership failure

Status: baseline correctness failure reproduced and isolated with finite controls. No NativeWeave runtime implementation was changed, and these runs provide no performance or long-duration credit.

## Observed failure and controls

Root's A02 verifier used the unchanged ea5 runtime with the new public-behavior regressions at test-source commit `a723bac2274ea760ef5afbe025edbee32589b9ae`. JIT cases passed. Native AOT reached `default-concurrent`, then exited with signal 11 and empty stdout/stderr. Running the exact already-built executable/arguments again on CPUs 2,3 reproduced exit -11 at 11:25:27 UTC. The native fixture SHA-256 was `f40d6b9d44948562385b1174fee671212de40190dc5d6488f3423ef6dad87194` in both runs.

The test starts eight dedicated threads, waits for all of them, then exercises first default inspection and the first generated `LibraryImport` together. `DefaultAsset` copies the fixture before starting the threads and unlinks its copy only during cleanup; it never rewrites a mapped file. The earlier concurrency case first invokes the native counter after all inspections have joined, so it does not exercise the same cold-import overlap.

Finite plain-.NET controls used the same fixture with no NativeWeave managed project reference. Initial cold/serial/warm/function-pointer controls and late resolver-installation/late load/ConditionalWeakTable controls passed. Each successful AOT cold variant reported only one resolver callback, so they did not disprove a race between overlapping callbacks. The JIT cold variant reported three callbacks and passed; the locked Native AOT implementation is the scope of the subsequent diagnosis.

A final control introduced a finite rendezvous *inside* the resolver. All eight first callers must enter the callback before any can return. Each mode ran in a fresh process with the same AOT executable (`30631326517134ee550097f95d3d1805a56a512c25ea0589eebcc2bf5cc7c267`) and the same CPU mask.

| Mode | Callback result | Actual outcome at 2026-11-19 11:43:10 UTC |
| --- | --- | --- |
| `borrowed` | Same sole resident handle every time | Eight entries observed; exit -11 |
| `owned` | `NativeLibrary.Load` of the exact loaded path for each callback | Exit 0; 64 correct calls; eight completed callbacks; original handle/export remains valid |
| `owned-unlink` | Same per-callback load, after unlinking only the freshly loaded test copy | Exit 0; same 64/eight checks; same handle/export and original inode mappings marked `(deleted)` |

Every copy was byte-hashed against the untouched input before loading. Owned callbacks assert equality with the original handle and exported function pointer. After the concurrent calls, the control verifies that the original handle still resolves that pointer, calls it directly, and rechecks the input fixture hash. This demonstrates the Linux behavior on the measured environment; it is not a cross-platform unlink guarantee.

## Locked source and reference ownership

The actual `runtime.linux-x64.Microsoft.DotNet.ILCompiler` 11.0.0 nuspec identifies `dotnet/dotnet` commit `297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`. The installed runtime version record identifies the same commit. The installed nuspec is retained with the controls.

| Read source | Pinned identity and relevant behavior |
| --- | --- |
| [Native AOT InteropHelpers.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/coreclr/nativeaot/System.Private.CoreLib/src/Internal/Runtime/CompilerHelpers/InteropHelpers.cs#L256-L339) | Git blob `91c53377081701a00b0a5ccb293664e35714aaf0`; `ResolvePInvokeSlow` reads the module cell, `FixupModuleCell` obtains the callback handle and publishes it with CAS; every losing publication calls `FreeLibrary(hModule)` |
| [NativeLibrary.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Runtime/InteropServices/NativeLibrary.cs) | Git blob `04ec2888f4ae6689c7d9fc4f98e06cce82d08e26`; the callback result is returned unchanged, while `NativeLibrary.Load(string)` directly uses `LoadFromPath` and does not invoke the per-assembly callback recursively |
| [NativeLibrary.NativeAot.cs](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/coreclr/nativeaot/System.Private.CoreLib/src/System/Runtime/InteropServices/NativeLibrary.NativeAot.cs) | Git blob `219ad79e4283d59afea9542366c8d52b70684cbd`; native AOT loading/export helpers |
| [NativeWeave EngineModuleLoader.cs](https://github.com/IzuSharp/NativeWeave/blob/ea5fa528035d025bd7a28698ee7c71194432236c/src/Interop.Negotiation/EngineModuleLoader.cs) | Lines 78–89 retain the first OS load for process lifetime; lines 233–270 bind/import the same handle without obtaining another OS reference |

These sources were fetched at the exact commits and the reported Git blob IDs were recomputed from their bytes. The upstream manifest also records SHA-256 values. The .NET files are MIT licensed. They were read and retained locally for inspection; no upstream implementation was imported into the product. The Plan evidence contains identity metadata, the installed nuspec and task-authored diagnostic source, without vendoring the .NET implementation.

The observed locked AOT path requires a releasable reference for each nonzero callback result: a losing resolver may release it. The public delegate documentation merely describes a loaded-library handle; this note does not invent a more explicit ownership sentence in those docs. NativeWeave's resolver returns a borrowed reference to its sole resident load, and its lookup lock ends before the runtime's CAS. Serializing the lookup therefore does not protect the reference from a later losing callback's `FreeLibrary`. The source path and forced-overlap differential controls support this ownership mismatch as the cold crash cause. Native stack capture was unavailable: strace could not launch the tracee because ptrace was denied, and no bypass was attempted.

## Prospective correction and required gates

Root owns the future implementation after the frozen before cohort. The minimal correctness direction is to retain the original validated resident module separately and have each matching resolver callback acquire an OS reference for the exact resident path. The returned handle must equal the resident handle. A mismatch must release only the newly acquired reference and fail; it must not return a different binary or fall back to default search. A load failure must leave the original resident reference untouched. The measured unlink case means an extra file-presence/hash requirement inside this resident callback would change existing lifetime behavior.

No warm-up workaround is proposed. Keep the cold concurrent public test and the existing explicit-option revalidation, capability mutation, repaired premapping failure, descriptor identity conflict, basename conflict and mapped-resident lifetime cases. Re-run the complete A02 JIT/Native AOT and package-consumer gates on the candidate. Preserve the original failing acceptance receipt independently of steady-state benchmark cells whose preinitialized application paths and correctness oracles pass. The descriptor success-cache hypothesis remains a separate allocation experiment; this failure is a correctness prerequisite for the shared loader candidate.

## Evidence and reproduction

[checks/a02-cold-import-001/README.md](checks/a02-cold-import-001/README.md) maps the original failed verifier, exact reproduction, unavailable trace, initial controls and decisive forced-overlap controls. It includes the actual source/project/lock files and commands, not only hashes. Every copied file was hashed again; `review.json` pins the 63 copied files and records the independent source review by the protocol agent. That review did not repeat execution.

The original local roots are `ROOT/perf01-evidence/functional/before-A02-001`, `ROOT/perf01-evidence/diagnostic/a02-*`, and `ROOT/perf01-codec-checks/a02-import-diagnostic-{001,002,003}`. Binaries remain at those roots with their identities recorded; no binary upload is claimed. Git retains the small source/numerical/command evidence without a task-specific expiration, subject to repository policy.
