# Perf-01 codec before-003 preparation

Status: actual package preparation completed; no timed codec workload or long acceptance ran in this step. The original before-002 bytes and diagnostics remain unchanged.

## Source and execution

- Clean runtime source: `ea5fa528035d025bd7a28698ee7c71194432236c`.
- Driver commit: `a5832628453b79b91043182188886aa564601aff`, tree `ca9770d43de42c01e02f08e70b970ee01e2eb990`. Root confirmed remote reachability before authorizing the build; local HEAD/tree/status were checked before and after.
- A21 source SHA-256: `a07dc5f338a13c8f9c4bedadb6d21cffd1e0f835d8381f16bb24f90d68ea98ad`.
- Completed UTC: `2026-11-19T10:54:02.568983+00:00`.
- Exact SDK 11.0.100 and Rust 1.100.0; locked Release Rust build, original A17 Native AOT arguments/default ISA, fresh package feeds/consumer caches/direct-target output, CARGO_BUILD_JOBS=3.
- Existing product target/bin caches were consumed only through the normal locked builders. No old manifest was edited and no prepared output directory was overwritten.
- The original codec driver inventory, product locks, reported toolchain and recorded build environment match before-002. The A21 source binding is new.

## Actual checks

All 25 recorded preparation commands matched their expected outcomes: 23 successful exits and the two intentional compiler-failure exits (`negative-null-limit` and `negative-span-escape`). The package JIT consumer, its ordinary managed-edit rerun and the Native AOT consumer each passed 139 assertions, with releases=102, live=0, capacity=0 and active=0. The Rust invocation trap did not fire. The dedicated performance consumer and direct miniz fixture were compiled; they were not timed or run as a performance scenario here.

Every file in the resulting manifest artifact and consumer-input maps was read back and hashed; all matched. The corpus was not regenerated. Its manifest remains `92932f7ecba2b3a7104b19344d22a42c3c40605f23eb158a0941d48bfff0465d`. Actual future performance-process native mappings remain a per-cell driver gate; this build receipt does not substitute for them.

## Exact artifact identities

| Artifact | SHA-256 |
| --- | --- |
| Producer manifest | `f7a766eb277d09a6f5d64fd3ecac2e83bf6dcbac41ab384c0b75affc234c775d` |
| Command receipt | `dc85751efcf1afbb47d25d40ba57ff9dbf0acb614f6e5ca22a0b1fac92013b8e` |
| `aot/NativeWeave.Engines.SyncProof.Tests` | `afdc1ea29c9de8b0b04d7956aefc6a4832d4c418ccf7f89dd1a82bd79714ab69` |
| `aot/libnativeweave_engine_syncproof.so` | `3a472d8e51ad5d69a28ade2b00cd23fc9a2bb8d9fa1e2c4df47b769316acff79` |
| `direct-target/release/perf01-codec-direct` | `f91076cf2a31c895914ff7333289210a191d8ef1eaf99f1f6cadabf128831477` |
| `packages/NativeWeave.Core.0.1.0-proof.1.nupkg` | `e664d0611e4f5f98f62fed352a2eb7f22920c1c9f6e32da8bc526550eacaef96` |
| `packages/NativeWeave.Engines.SyncProof.0.1.0-proof.1.nupkg` | `4eb01ac27f8e190661507d052679e2d52a065b1c613beca45fa5878ae6cbbcb4` |

## Evidence and reproduction

Verbatim metadata and three short conformance stdout files are retained in this directory. `verification.json` records their SHA-256 values, original locations, the actual command, source checks and build-002 comparison. These copies were hashed after writing. They contain no credentials or private configuration.

The complete local producer directory is `ROOT/perf01-codec-checks/package-before-003`. Binary/native/package files are not copied into this Plan record; this record makes no durable binary archive or upload claim. Repository history retains the metadata without a task-specific expiration, subject to repository retention policy.

After sourcing `ROOT/perf01-toolchain/env.sh`, reproduce with the exact interpreter/command in `verification.json`, a clean ea5 runtime checkout and the recorded driver commit, choosing a new output path. Preserve the existing corpus. This is a build command, not a benchmark or 30-minute run.
