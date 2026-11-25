# Independent review: Core compatibility

Task: DB-DotNet-01. Reviewer: api_compatibility, independent of the implementation author.
Reviewed commit: `770486c0ed1a178cbfcbc2b00dc2c7e81d306bf4`.

## Result

No blocking correctness defect found in the reviewed change. This is a source
review plus an independent rerun of the author's frozen Linux x64 Native AOT
executable; it is not a claim that legacy native loading remains supported.

## Checked contracts

- `src/Interop.Memory/BufferLease.cs`: admission and `DangerousAddRef` share a
  gate; logical disposal closes admission before dropping the original handle;
  caller destruction runs outside the gate; every admitted operation releases
  its reference even after a callback error. An active read remains protected
  through concurrent or reentrant disposal.
- `src/Interop.Memory/NativeBuffer.cs`: synchronous validation and lease lifetime,
  overlap-safe copies, exception paths, cancellation before allocation, one
  bounded async staging allocation, and transfer of the single reference into
  the async method. The `SafeHandle` owns fallback finalization.
- `src/Interop.Memory/NativeBufferFactory.cs`: validation precedes ownership
  transfer; null/extent/overflow checks retain the published surface. The caller
  must retain any finalizer-specific context in its own handle, as documented.
- `src/Interop.Negotiation/EngineMetadata.cs` and `EnginePackage.cs`: immutable
  descriptors and capability lists, bounded snapshots, strict capability
  validation, platform checks, and no driver connection or native loading during
  inspection. The three public signature baseline files are unchanged.
- `src/Korda.Core/Korda.Core.csproj`: the zero-public ABI assembly and private
  callbacks/executors/loaders are removed; public metadata, errors, and buffer
  compatibility types remain. The SeaQuery MIT notice remains in the notices.

## Independent execution

Executable:
`../DB-DotNet-01-packaging/artifacts/DB-DotNet-01/core-770486c/compatibility-aot/Korda.Interop.Memory.Tests`

SHA256: `ed33a7d212ef7bf056ce6b9adc51ae9a765752ba51ef12a17f98f901d6bec169`.

Run with `--require-aot`: 259 assertions passed; owners, backings, and charged
capacity were zero after completion; 14 owner releases and 14 backing releases.
The author's clean-source receipt records commit and tree hashes, compiler/run
commands, executable hash, and successful public sample execution. Its API tool
log records all 23 memory symbols unchanged and four negative compilation cases.
The complete published Core signature comparison (133 symbols) is separate
author-generated evidence; this review did not regenerate that complete report.

## Compatibility limitation to disclose

`EngineDescriptor.Inspect` on a legacy native manifest or with `NativeAssetPath`
now reports `EngineLoadFailure.InvalidManifest`. Retaining the 133 public
signatures does not imply retention of the retired native loader's behavior.
This retirement is required by the database migration scope and is explicit in
the current API documentation. Database providers use their compiled .NET
descriptors, with no Korda module loading or ABI negotiation.
