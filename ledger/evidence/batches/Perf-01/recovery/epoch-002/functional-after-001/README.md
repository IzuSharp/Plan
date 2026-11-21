# Perf-01 — actual final candidate B18 verification

The original B18 native component and assembled managed/package verifiers completed successfully for the selected final candidate `ccff42c0df4141984ef9de497af7cd768753704a`. The actual stage ran on 2026-11-21 from **02:44:25.066185 to 02:57:51.290847 UTC**. Both owned commands exited zero and retired, with no remaining owned processes or adopted children. This document projects existing results; its preparation ran no new build, test, or workload.

[projection.json](projection.json) contains the exact receipt, command-log, native-library, executable, and package hashes, without operational file maps, environment values, TLS material, or process identifiers.

## Actual commands and results

| Original entrypoint | Actual UTC interval | Recorded outcome |
|---|---|---|
| `native/protocols/grpc/verify-native.py` | 02:44:26.044279–02:53:46.689715 | Eleven successful commands. The leaf had 12 passing tests in Debug and Release. The host gRPC selection had nine passing tests in each configuration, including both metadata retirement regressions, with 12 unrelated tests filtered out. Forty-eight Server exports recorded. |
| `tests/Protocols.Grpc/verify.py` | 02:53:46.871656–02:57:51.052711 | Eighteen successful assembled commands, including actual JIT/AOT runs, ABI and public API checks, and the original independent package probe. The package probe recorded another 25 successful commands. |

| Assembled consumer | Assertions | Managed retirements | Dynamic code supported | Executable SHA-256 |
|---|---:|---:|---|---|
| Release JIT | 948 | 578 | `true` | `fa83636347c29f828c2ac6deea376e7dbaa47c02cb41723e0f46d2c4db5f6154` |
| Native AOT | 949 | 580 | `false` | `f873c5cda2e40982d16d042e3abd1c25eb62a9210e2519cce120ef4b63cf802b` |

The original assembled verification also checked 48 exports, eight ABI records, 103 offsets, 71 public API symbols, and five compile-negative fixtures. Its source was clean and its Design input was `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. The final fixture includes additional writer ownership and admission regressions; its larger assertion total is a correctness observation, not an equal-work performance comparison with the baseline.

## Native identity and package reuse

The actual role Server asset was **8,814,544 bytes**, SHA-256 `1f023b7506bde3f8c4a13b12de92e3e9503004ca3afc2d41a53bec17e44f1d97`. The assembled fixture and package consumers used that asset. The separately produced native component library was **8,178,320 bytes**, SHA-256 `2229a1987fc6624196cf7f1f3cee350e3db6284e884c82f34b93caf437db2f9c`. These are different builds: the original assembled verifier accepted the matching 11-file gRPC source subset and independently checked the supplied role asset. The component library is not substituted for the measured application asset.

The original B18 package probe produced five `0.1.0-preview.1` packages and executed eight consumer configurations: initial minimal and advanced JIT/AOT consumers, the advanced HTTP/2 + TLS consumers, and edited DTO/Handler JIT/AOT consumers. The advanced runs observed unary, server-streaming, client-streaming and duplex calls; binary metadata, explicit status/trailers, a whole-call deadline after headers, and bounded managed/native close all passed. Native AOT consumers explicitly reported no dynamic code.

All four selected native output records—initial JIT, initial AOT, edited JIT and edited AOT—retain the same `1f023b75…` Server identity. Both edited managed executable hashes changed. The package probe recorded package-reference-only consumption, an isolated NuGet cache, no accessible Rust toolchain, and no Rust trap firing. This is actual reuse after ordinary application edits. The original pre-edit JIT output was intentionally replaced by the edited build; its immutable input snapshot and execution hash receipt remain, as stated by the original verifier.

This B18 five-package proof is separate from the [selected B24 build's 17-package candidate closure](../built-after-001/README.md). It does not grant pristine-machine or public-release acceptance.

## Evidence verification and limits

The projection rehashed **342 bound files (86,508,684 bytes)**, all **54 original child command logs**, and all **four finite-owner output logs**. Both original owner receipts report exit zero, successful retirement, zero remaining owned processes, zero adopted children, and no signals sent.

| Receipt | SHA-256 |
|---|---|
| Completed stage execution | `8b79ac99a39a5870053934abd68a6527fe3f98bbceca000708b1ddbd1229c47d` |
| Actual functional binding | `08432c45b4e4381ec302b356d0ecb1b8f8e4f9293248be866cbaa4d5a0bdf86d` |
| Original native component result | `861132250613ddc3ebc979c8a114a9dd8cb62d316e008fff0a96bee2b859aecc` |
| Original assembled result | `3a760ffac7a29f3386418e6fc2bc8dd0d9b7d35c9fb24c5cf298a4870689c780` |
| Original independent package summary | `f0369cf3ca6ef489f7aee9876f570150be5336f72c6258ff2e8c19a4708f8b16` |

The common build/B18 caller source index remains `268d10b6b058f6c599fc1128b8a2a7ad7949f723d842647756e542ba70756795`; the original verifier entrypoint hashes are recorded in the projection. Actual measurement uses the separately frozen common driver. This checkpoint covers B18 Linux x64 correctness only. Other affected module regressions, performance, capacity, and all current 30-minute acceptance segments remain separate. **This record contributes zero performance seconds and zero long-test credit.**
