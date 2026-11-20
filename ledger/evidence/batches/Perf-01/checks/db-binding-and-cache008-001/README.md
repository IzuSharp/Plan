# DB binding recovery and compiler-cache cleanup008

The existing before diagnostic consumers were successfully rebound without rebuilding. This is preparation evidence, with no formal comparison, capacity or long-duration credit.

## Actual zero-producer verification

The reviewed recovery002 source ran from **2026-11-20 17:19:17.006088 UTC** through **17:19:18.795298 UTC**. It verified the original five successful producer commands and the two successful consumer continuations, retaining their distinct source and execution identities. No producer command ran again. The completed receipt is `930bc9e84f2dcf11ed8d38fbdb950cde58ffb74255b4db2d7f55da6da2f8f4ab`; the full local binding is `afe39bc5065f079625d109823c3fdfa188d874facf7e11a34c29fffd60303039`.

The diagnostic source remains `58e70549052816c1a8b9e135b76282d7f936e974`, over frozen product `ea5fa528035d025bd7a28698ee7c71194432236c`. Package version is `0.1.0-perf01.db-phases-002-before.1`. There are 17 selected NativeWeave packages; the observer actually resolves 22 packages, including 15 NativeWeave packages. These are different populations.

Archive SHA-256, archive SHA-512/sidecars and NuGet metadata/assets content hashes retain their separate checks. Seven exact signed external-package tuples use the original successful archive proof; unsigned NativeWeave packages still require archive/content equality and the selected feed. The [earlier failed binding and codec observations](../codec-and-binding-interruptions-001/README.md) remain unchanged.

After protocol capacity recording reduced available storage to 305,504,256 bytes, root explicitly used a **268,435,456-byte caller floor for this zero-producer verification only**. Its source already accepts a positive caller-supplied floor. This path streams existing ZIPs and writes metadata, without extraction, compilation or workload execution; it has no strict serialized-output bound. The build-final and measure invocations retain their **1,073,741,824-byte floor**. No source, hash, signing, workload or runtime resource check was relaxed. A mistyped source-index argument failed before any owned stage existed; correcting that literal created no replacement measurement and is separately recorded.

## Actual cleanup008

The independently reviewed selection contains 1,704 files, totaling 1,088,946,298 apparent bytes:

| Reproducible category | Files | Apparent bytes |
| --- | ---: | ---: |
| Rust intermediates | 686 | 770,149,200 |
| Archive-backed SDK members | 1,016 | 254,532,498 |
| Two exact producer-bound AOT objects | 2 | 64,264,600 |

The inventory rehashed 4,728 protected artifacts and retained 181 metadata files, 5,463 absolute references and 10 package archives. All selected paths were outside the protected closure. Candidate hashing and full ZIP decode/CRC comparison belonged to cleanup, rather than the earlier metadata census.

Cleanup ran from **2026-11-20 17:25:31.282815 UTC** through **17:25:47.694881 UTC**, removed all 1,704 selected files, fully compared all 1,016 SDK members and rechecked the protected inputs. The existing finite owner and adopted-descendant guard completed without cleanup signals or residual children. Available space increased from **300,400,640** to **1,386,237,952 bytes**, an actual increase of **1,085,837,312 bytes**. Tested outputs, raw evidence and package archives were not removed.

The exact inventory is `d375c8dc3d8acfd62312f3c90837a0adab8f1f0604c0f62de222f23b6886de6b`; cleanup source is `debb9e44f5bc6f01c37580721c22d15dab757119239c30c5a03bba917adf413e`. The source freeze changed only the selected inventory digest. The completed cleanup receipt is `a384912c4ce89ce1bbf2400279d6cf608953504003f0879f67e001a431f54fca`; its journal is `47b0367723fd95cdcf9e0cbca41c8c3ad5903eec8a0dc50367c01b2789aad1ce`. Archive restore records and retained producer outputs support reconstruction before any selected cache reuse.

## Retention and limits

This folder contains the readable outcome and synthetic numerical/hash checklist, retained with Plan Git history. Private operational controls and the exact restore journal remain under the task's `perf01-run` storage; their digests above identify them. This publication does not claim those raw operational records were uploaded as a public artifact. Actual future build headroom remains a separate admission check; no future savings, fit, timing result or new test pass follows from this cleanup.
