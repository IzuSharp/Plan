# B18 documentation and package-consumer handoff

Status: assigned documentation, static two-service example and Linux x64 ordinary NuGet consumption passed. The parent owns complete B18 integration/semantic/API review and Plan/PR/merge handling.

## Source and exact asset

The clean execution source is `f2ca354547d9c9114fe4473b2953e6e000b0f6d6` on `task/Task-06-B18-docs-linux`. It includes the parent's `f8153b5` disposal/header-admission fixes (local cherry-pick `947c00c`). The exact Design pin is `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.

Use only the parent-selected product native asset SHA256 `b7ee6eed112490b4ddb040b12dfb762e7afa334493db658e8b61325a66695ecf`. Its native source identity is `6ba04525255132840f4673820d98a62f2c45d3dc`, recorded separately with every native input hash in `package-final/summary.json`. The independent native helper's different MCP composition/asset is not substituted here.

Owned commits are `bdb3ef9` (guide, two protobuf services and probe), `86300c2` (local TLS SHA256 fingerprint), `ccf0e0a` (EOF/cancellation race documentation) and `f2ca354` (exact native provenance). The first commit was already integrated by the parent; cherry-pick the remaining owned commits as needed. No shared project/packaging files were edited.

## Delivered behavior and actual checks

The guide `docs/guides/protocols-grpc.md` explains ordinary package use, explicit static codec/service registration, all four cardinalities, one host/runtime, TLS, metadata, protocol statuses, whole-call deadlines, permitted request access and ownership/cost boundaries. It expressly distinguishes decompressed payload limits from arbitrary application DTO/private-codec allocation, and describes cancellation racing with successful EOF.

The runnable `samples/api/protocols-grpc` builds generated DTOs and independent clients from two actual `.proto` services. Minimal mode executes both services; advanced mode covers unary, server/client/duplex streaming, half-close, ordered messages, binary metadata, explicit error trailers, a native250ms timeout after response headers, and a close with no pending requests or retained payload bytes. Local TLS trusts only the generated certificate's SHA256 fingerprint. No managed server transport, reflection-discovered service or Rust schema compilation is introduced.

The accepted A14 packer produced five coherent NativeWeave packages with exact dependency edges. The copied consumer has only PackageReference entries, isolated NuGet state and explicit Directory.Build boundaries. Actual restore/build and explicit linux-x64 NativeAOT publish/execute all passed with audit and warning-as-error settings. Both AOT dynamic-code flags are false. Rust tools were removed from its usable PATH and invocation traps never fired.

Baseline JIT and AOT each execute minimal, advanced HTTP2-clear and advanced HTTP2+rustls modes. The probe then adds a real protobuf field and matching typed handler/client behavior, regenerates C#, and executes changed JIT and AOT programs. Both executable hashes change while every package and the native asset remain identical. No assembly-root or trimming-warning suppression is used. Every one of the 25 recorded commands exited0.

`package-final/summary.json` contains package/native/executable hashes and actual SDK-selected output records. Ordinary build retains the SDK's selected native path; AOT uses its selected flattened publish path. Neither path is guessed by a resolver. The probe recorded input hashes before execution and checked them afterward.

## Evidence and limitations

`evidence-linux.json` SHA256 `3c8575428dc69f8945f27f4861c32150bc612143439de4867051e55f97a303fc` references all source, snapshot and command/log identities. The corrected package summary SHA256 is `ba0991b1f2a55a40fa4ab4fc646bc22287687c65f51801273311f583f2cc598a`. Original command logs preserve the initially supplied f8153b5 identity; `native-provenance-correction.json` records the parent's exact actual build commit6ba0452, compares all139 native runtime/manifest inputs byte-for-byte and lists the five documentation/proof-only differences. No consumer result or original command log was rewritten. Actual logs include `consumer-aot-advanced-tls.log` and `edited-aot-execute.log`; immutable source/lock/config snapshots and before-execution binary hashes are under `package-final/snapshots`.

Baseline JIT bytes were subsequently rebuilt for the explicit ordinary-edit test; their before-execution digest and immutable source/lock snapshot remain. The original and edited AOT outputs, edited JIT output, candidate packages and frozen native asset remain on disk. This is component NuGet proof, not an OS image without a maintainer toolchain, final pristine A16/B24 release acceptance or another platform's result.

Next: parent imports this receipt into `Plan/ledger/evidence/B18/`, composes its complete B18 native/managed/API evidence and continues Task-06's authorized PR/check/merge workflow. The child is now adding the parent's requested reusable managed/ABI verifier, which will reference accepted native evidence and this package proof without repeating historical native acceptance.
