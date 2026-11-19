# Perf-01 codec before-004 preparation

Status: actual package preparation completed at `2026-11-19T11:44:57.783919+00:00`; this step ran no timed codec workload and earns zero long-duration credit.

The unchanged clean runtime is `ea5fa528035d025bd7a28698ee7c71194432236c`. The final test-driver source is `aa3399f0418a6d0910cc56697abfaa3769f32b54`, tree `46431456e32e6c295aa3cac0c2b80344c25b6880`. Its A21 SHA-256 is `dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53`. This fresh producer binds the compact observation streaming work without editing before-003 or other prior receipts. Root confirmed remote reachability before execution; clean source status and identities were checked before and after preparation.

## Actual verification

All 25 recorded commands matched their expected outcomes: 23 successful exits and the two intentional compiler-failure exits (`negative-null-limit` and `negative-span-escape`). Package JIT, the ordinary managed-edit JIT rerun and actual Native AOT each passed 139 assertions, with releases=102, live=0, capacity=0 and active=0. The Rust invocation trap did not fire. The dedicated performance consumer and direct miniz fixture were compiled without running a performance scenario.

All five manifest artifacts and all five consumer inputs were read back and hashed. Current codec source inventory and A21 hashes matched the manifest. Compared with before-003, codec driver inventory, product locks, toolchain, recorded build environment, native library and direct executable are unchanged. The actual newly produced package and managed executable hashes are recorded below; prior hashes are not substituted.

The build used exact SDK 11.0.100, Rust 1.100.0, the existing A17 Release/Native AOT arguments and default ISA, fresh package feeds and consumer/direct target output, and `CARGO_BUILD_JOBS=3`. Existing source build caches were consumed only through the normal locked builders. The original corpus is a separate unchanged input: prepare does not generate or consume it. Every later run must still validate the frozen corpus and actual loaded native mappings.

## Exact identities

| Artifact | SHA-256 |
| --- | --- |
| `Producer manifest` | `d34298ebc8dc82b525f19860555947a1a04eff2bf8aecc38cede2922c81285a7` |
| `Command receipt` | `4afad41da8ea0392c4e810f5ce1091e758b86c7a1bd880896f24b9412b84cdbb` |
| `NativeWeave.Engines.SyncProof.Tests` | `d71cb44e6bf7868ea150d9b98fe78e779675aeff59e6a990dbaa8ea47ae9253e` |
| `libnativeweave_engine_syncproof.so` | `3a472d8e51ad5d69a28ade2b00cd23fc9a2bb8d9fa1e2c4df47b769316acff79` |
| `perf01-codec-direct` | `f91076cf2a31c895914ff7333289210a191d8ef1eaf99f1f6cadabf128831477` |
| `NativeWeave.Core.0.1.0-proof.1.nupkg` | `e664d0611e4f5f98f62fed352a2eb7f22920c1c9f6e32da8bc526550eacaef96` |
| `NativeWeave.Engines.SyncProof.0.1.0-proof.1.nupkg` | `387ab88f17adac74946c4d4158862a557a720982639b273491988508b1ace78a` |

## Evidence and reproduction

`verification.json` records the exact interpreter/argv, source checks, comparison with before-003, original artifact location and hashes of the verbatim copies. This directory retains the original manifest, 25-command receipt, package closure/consumption receipts and three short conformance stdout files. Each copied file was hashed again after writing.

The complete local output is `ROOT/perf01-codec-checks/package-before-004`. Executable, native and package binaries remain there; no durable binary upload is claimed in this receipt. Git history retains these metadata and stdout copies without a task-specific expiration, subject to repository retention policy.

After sourcing `ROOT/perf01-toolchain/env.sh` and exporting `CARGO_BUILD_JOBS=3`, reproduce the command in `verification.json` with the recorded driver, a clean ea5 runtime checkout and a new output directory. Keep the existing deterministic corpus. Fresh before-only noise, fixed-load and long cells must name this producer and the final unchanged A21/codec source; the earlier before-003 smoke retains its original preparatory status.
