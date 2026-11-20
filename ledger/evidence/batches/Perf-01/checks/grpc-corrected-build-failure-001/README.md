# Perf-01 corrected-control build: observed partial failure

**The assembled B18 check failed. No performance comparison, capacity result,
scratch retention decision or long-test credit is accepted from this attempt.**
The actual build supervisor ran from 2026-11-20 11:27:38.397585 UTC through
11:40:35.141697 UTC. Four outer commands completed successfully; the fifth,
`control-b18`, failed with exit code 1 after its actual Native AOT child exited
with code -6. All five started process groups and adopted descendants retired.
The four candidate outer commands did not start.

| Observed stage | Actual outcome | Scope |
| --- | --- | --- |
| Corrected native component | 11 commands, all exit 0 | Component-only evidence from candidate source `1207b8d3b0c273752a28dabdf3e7a2b54c933571` |
| Control native assets | Completed | Three retained native assets from clean control source `da48ccf9d263155ebcbc2a6eea986f6b05972f51` |
| Control B24 packages | Completed | 17 selected `.1` packages; 17 unused upgrade `.2` packages were also produced |
| Frozen protocol application | Release Native AOT build completed | Build identities are recorded; no performance process was run |
| Assembled B18 JIT | Exit 0; 948 assertions; 578 managed retirements | The completed JIT observation remains valid as a partial functional result |
| Public API and XML | 71 exact declarations and 5 negative fixtures | Completed before the AOT failure |
| Assembled B18 Native AOT | **Exit -6 after 0.566 seconds** | Failed during the second persistent HTTP/2 call |
| Ordinary B18 package proof | **Not started** | The AOT failure stopped the verifier before package acceptance |
| Candidate native/packages/protocol/B18 | **All four outer commands unstarted** | No candidate assembled or performance acceptance |

## Exact failed boundary

The AOT output contains one completed call in `PersistentHeaderCredits`. Its
last five fixture assertions establish one handler entry, exact protobuf and
OK status, initial and trailing ASCII/binary metadata, and release of the first
call's request slots and byte credits while the TLS HTTP/2 clients remain
connected. The subsequent call raised an `Internal` gRPC status with detail
`managed dispatch unavailable`. The fixture's final drain assertion did not
run. The log contains 594 `PASS` lines before the abort; this is not a completed
assertion count or an AOT pass.

This spontaneous failure is separate from the later deliberately held
ticket-tail diagnostic recorded in `perf01-run/grpc-ticket-tail-001/execution.json`
(SHA-256 `21ac50d2cf6271816468b0716b62c1822bcb78f138481e6b36335e488e510d2a`).
That later reproduction must not replace this failed B18 result. Subsequent
product fixes require fresh assembled verification and performance identities.

## Source and actual binary identities

The control source is `da48ccf9d263155ebcbc2a6eea986f6b05972f51`, tree
`409f2e9e690f6c218d90fe38500933e619d850ec`. The candidate source is
`1207b8d3b0c273752a28dabdf3e7a2b54c933571`, tree
`86c4ac7a7c4d17f705d3fa52af4fafdb6959d2da`.

The assembled control actually loaded Server SHA-256
`28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2`.
The native-only component uses different whole-Server bytes,
`0542a7766a79091c6ea2d51daad74c257fcc7e9f902619bf4eebcc129b6a2e5b`,
retained separately with their original component receipt. B18 records 11
matching gRPC source files; different whole-Server composition is not relabeled
as an identical product asset. The failed AOT executable SHA-256 is
`3f61bc171f6754513d7ad29eafb09e37f201f4115bb53ef56a8fd5a6046034e6`.

`summary.json` retains all five outer outcomes, all 17 B18 command outcomes and
log hashes, all 11 component command outcomes, the actual 27-file JIT and
12-file AOT input inventories, all three produced native assets, the 17 selected
package identities, and the six frozen protocol application artifacts. The
projection hash-checked 116 retained inputs, including logs and actual selected
executables/packages/native files. It ran no workload or verifier replay.

## Retained evidence

The original failed receipt remains at
`perf01-run/grpc-scratch-ablation-003/build/execution.json`, SHA-256
`7448091c8272160f261c4b6b2f9756ecc4e98f4dee10049e60bf4f28105568f4`.
The B18 result remains at
`perf01-evidence/diagnostics/grpc-scratch-003-control/B18/result.json`, SHA-256
`d961a8783a1023231b027c00bd3d87332b92622de99edb53b59cb22bf4e60006`.
The exact AOT log SHA-256 is
`2b02f9678357a558c4a66189a9b43634b2930e0bc6a0f39162cad59fd486c659`.
The projection receipt is
`perf01-run/grpc-corrected-build-failure-projection-001.json`, SHA-256
`696c14fbfb80203097f8b450a4e2fd4926633eb189450a9d886c7ead11491f25`.

These three curated report files are the publication allowlist. Full local
receipts, command environments, logs, input inventories, source and binaries
remain in their original locations; this report does not publish operational
bundles or grant a public package release.
