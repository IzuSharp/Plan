# Perf-01 — actual baseline B18 verification

The original B18 native component and assembled managed/package verifiers completed successfully for the fixed baseline `ea5fa528035d025bd7a28698ee7c71194432236c`. The actual stage ran on 2026-11-21 from **02:15:08.867358 to 02:28:03.448719 UTC**. Both owned commands exited zero and retired, with no remaining owned processes or adopted children. This document projects existing results; its preparation ran no new build, test, or workload.

[projection.json](projection.json) contains the exact receipt, command-log, native-library, executable, and package hashes, without operational file maps, environment values, TLS material, or process identifiers.

## Actual commands and results

| Original entrypoint | Actual UTC interval | Recorded outcome |
|---|---|---|
| `native/protocols/grpc/verify-native.py` | 02:15:09.452295–02:24:16.912260 | Eleven successful commands. The leaf had 12 passing tests in Debug and Release. The host gRPC selection had seven passing tests in each configuration, with ten unrelated tests filtered out. Forty-eight Server exports recorded. |
| `tests/Protocols.Grpc/verify.py` | 02:24:17.079047–02:28:03.199751 | Eighteen successful assembled commands, including actual JIT/AOT runs, ABI and public API checks, and the original independent package probe. The package probe recorded another 25 successful commands. |

| Assembled consumer | Assertions | Managed retirements | Dynamic code supported | Executable SHA-256 |
|---|---:|---:|---|---|
| Release JIT | 308 | 336 | `true` | `66b6a55a1cf7d1d36a5ca69494d34c3a220a8a2a1f91d0a0b6a1744c134ce6ab` |
| Native AOT | 309 | 332 | `false` | `0aaec7ae3dc7f6bcbec8bbe2ff2739b82fe4a6085c28a282b0b22dd19315c7f5` |

The original assembled verification also checked 48 exports, eight ABI records, 103 offsets, 71 public API symbols, and five compile-negative fixtures. Its source was clean and its Design input was `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.

## Native identity and ordinary application edits

The component test build produced an 8,178,544-byte Server library with SHA-256 `30dd73d733c71989cb5a79422f69decc9404f115c2b4513613460863eb8bae2f`. The assembled tests and package consumers used the actual baseline role's 8,814,696-byte Server asset with SHA-256 `63c4950fceab5fe52017b5457b04759201de5a261d8087939cb177a20a5b88e2`.

These whole-library identities are intentionally recorded separately. The original assembled verifier permits the component build to have a different surrounding Server/MCP composition, checks its eleven matching gRPC source files, binds the accepted native-component receipt, and separately checks the supplied baseline application asset. Both receipts identify the same baseline source commit.

The independent package probe used five actual `0.1.0-preview.1` packages: `NativeWeave.Interop.Abi`, `NativeWeave.Core`, `NativeWeave.Server.Generator`, `NativeWeave.Server`, and `NativeWeave.Server.Grpc`. This is the original B18 consumer package set; the seventeen-package B24 baseline closure is recorded separately.

The probe executed minimal, advanced cleartext, and advanced TLS consumers in both JIT and AOT modes. Advanced runs checked all four gRPC cardinalities, explicit input half-close, duplex output before input half-close, binary metadata, terminal status/trailers, the whole-call deadline after committed response headers, and bounded owner cleanup. It then added a protobuf `tag` field and changed the typed Handler/client, regenerated the DTOs, and executed the edited JIT and AOT consumers over TLS.

All four SDK-selected output records—original JIT/AOT and edited JIT/AOT—retain the same baseline native SHA-256. The edited managed JIT and AOT executable hashes differ from their original counterparts. The probe recorded package-only references, an isolated NuGet cache, no parent repository imports, no accessible Rust toolchain, no triggered Rust trap, two static protobuf services, and no root descriptors or trim suppressions. The actual command logs and source-defined checks support these observations.

## Readback and scope

Readback verified all **338 files / 85,710,115 bytes** in the private functional binding, the **54 original child-command logs**, and all **four outer owner output logs**. Both outer receipts report zero live owned processes and zero remaining owner children; no cleanup signals were sent.

| Record | SHA-256 |
|---|---|
| Completed outer execution | `eee3fe936c4df67e6374e284d4ea1c40fff288e8a6a9e00261e83d574252f57d` |
| Functional binding | `75d6dfa6371812b0b78b483836055130ff346246b5f6cdb2dd5b871f62dbcc00` |
| Original component result | `6700b5d358b59f6fac32fd95dcccf7e20d7ba7e0113f4548a8847b1af8d76ed8` |
| Original assembled result | `ab172290ada444f6e5f13853edb236d662deee58aa47fb5d70225affe0585d2d` |
| Independent package summary | `9ab69068b626b796ce495c867191425932fdae8222cea865d73e0b53b8294382` |

The execution retains the accepted build/B18 caller source index `268d10b6b058f6c599fc1128b8a2a7ad7949f723d842647756e542ba70756795` and the epoch-002 freeze, input, and toolchain hashes recorded in the projection. Its originals remain the authoritative detailed records; this projection does not archive binaries or full raw logs.

This is **B18 Linux x64 functional evidence only**. Other changed-module regressions remain separate. No pristine-machine, public-release, performance, capacity, or thirty-minute acceptance is claimed. The completed stage grants **zero** of the ten formal thirty-minute groups.
