# CI120: complete A20 functional verification

This records actual hosted Linux x64 execution on CI run [44669770570](https://github.com/IzuSharp/NativeWeave/actions/runs/44669770570), job [136067682275](https://github.com/IzuSharp/NativeWeave/actions/runs/44669770570/job/136067682275). The product head is `7b588c48e2898d93423ff278814370cdd7b49030`; the actual checkout is PR merge `89ca409b980996a7d1989d644282bd6bfaaae17a`. GitHub reports the same tree, `781d60048c1ea2f6dd507f285e00e81db47a6a27`, for both.

The unchanged A20 harness actually ran from **2026-11-20 03:45:10 UTC to 03:46:10 UTC**. Its result reports passed, clean source, unchanged final source/native assets, and no preparation-only mode. All 48 command outcomes match their declared expected exits; none timed out. The bounded audit independently verified all 96 named stdout/stderr hashes from the retained ZIP.

| Actual check | Observed result |
| --- | --- |
| JIT property/race suite | 8,925 assertions; 72 finite orders; exit 0 |
| Native AOT property/race suite | 8,925 assertions; 72 finite orders; exit 0 |
| JIT samples | Basic 2 checks; advanced 886 checks; both exit 0 |
| Native AOT samples | Basic 2 checks; advanced 886 checks; both exit 0 |
| Fuzz run | 20,000 units, terminal DONE, exit 0; coverage 104, features 183 |
| Deliberate oracle negatives | Original and retained counterexample both exit 77 with the expected assertion |
| Oracle minimizer and corrected replay | Both exit 0; retained counterexample is 61 bytes, equal to the original size |
| Quarantine/stale-cookie children | Both JIT and AOT produce their expected 43/42 exits and required markers |
| Fatal invalid-pointer/wrong-release children | Both produce expected exit 1 and the required AddressSanitizer diagnostics |
| API, formatting and source-drift checks | Completed with their expected successful outcomes |

ASan, UBSan and leak detection are all enabled in the actual result. The harness's default halt settings were checked. Instrumentation covers the C decoder, independent oracles and fatal-child driver. Stable Rust libraries, CLR and the Native AOT runtime remain uninstrumented, as declared by the unchanged harness. This is bounded functional coverage, not full FFI sanitizer instrumentation or a performance measurement.

The actual CI tools report .NET SDK 11.0.100, Rust 1.100.0 and Ubuntu Clang 18.1.3. This hosted functional environment is separate from the frozen local performance toolchain. The prior local LSan ptrace failure remains a failed local attempt; this fresh successful CI execution supplies its own evidence.

## Retained evidence and independent readback

Artifact [14598984040](https://github.com/IzuSharp/NativeWeave/actions/runs/44669770570/artifacts/14598984040) contains 203 members. The full ZIP was downloaded through the normal GitHub integration and verified:

- Size: **9,642,643 bytes**.
- ZIP SHA-256: `addec29fa1773d82301d3f8f6441eda3fe3f5dc92003506ccf154e396cab6b45`.
- Result SHA-256: `f9748ea3151f0153b06819a24639ecac6c132d4cd9c0a116be9ea8794d37f2ec`.
- Expiry reported by GitHub: **2026-12-04 03:46:11 UTC**, under the workflow's 14-day retention.

The ZIP and private audit receipts are retained in the task workspace. There was no full extraction. Besides all command logs, the audit independently rehashed the seven declared artifacts present in this archive and every initial/final corpus file. The other twelve declared tool, staged-native and JIT artifacts are outside this ZIP and were not independently rehashed by this readback. Their original identities and the source/native stability checks remain recorded by the executed harness. The retained counterexample was not smaller; no size-reduction claim is made.

`summary.json` contains only numbers, booleans, fixed public role labels and reviewed SHA identities. It includes the complete 48-role outcome/hash checklist. No command vectors, host paths, process identifiers, raw logs or control records are copied into that public projection. `manifest.json` pins the two report files and the actual input archive/result.

This receipt establishes the A20 lane only. At the 03:58:43 UTC status read, the build lane was cancelled and the aggregate Verify job failed. A normal subsequent PR update to `3db42f3131c72be217e49e386ba61ece7cee27fb` superseded this run under the existing cancellation policy. CI120 is therefore not a whole-workflow pass. The successful A20 execution and its original artifact identity remain valid for the exact tree recorded above. The full canonical build and pristine package gates require their own completed evidence on the final head; final performance comparisons and after long-run acceptance retain their separate local identities.
