# A09 independent technical review — Linux x64

**Result: accepted for the scoped Linux component at `b459fdedb0a71be564a0dbb16355d0baa429d80c`.** Reviewer `/root/environment_review` did not author A09 implementation or fixes. This is a technical review; repository-required GitHub reviews and protected-branch checks remain separate.

The final source, API applicability, immutable canonical model, strict JSON/schema boundary, Rust/sidecar/linked inventory equivalence, ownership pairs, asynchronous input lifetimes, notification authority and current D05/D06 profile rules were inspected. The component performs maintainer build-time parsing/validation only; it does not invoke Cargo/network/database work inside a compiler generator and creates no runtime ownership machinery.

## Evidence binding

The final author receipt is `artifacts/A09/review-fixed-002/result.json` on the clean reviewed commit. All 64 source hashes were checked against both Git objects and working files; all 74 raw command log hashes and eight native/managed/extractor/AOT artifact hashes matched. All 37 formal commands passed. JIT executed 220 assertions and the real Linux Native AOT executable executed 221, with 81 actual native calls per runtime and dynamic code unavailable in AOT. Three-process canonical bytes/digest equality and the real csbindgen1.9.8 tuple-omission negative are present.

A09 exports zero public types/members. All 30 metadata-only A02 symbol signatures were independently compared with the locked Design public-api inventory and matched exactly; no domain entrypoints or public plumbing were invented.

Fourteen independent input probes were run against the final compiled test/model binaries, and those binary hashes match the formal receipt. Positive cases include the original valid owner/operation/notification contract, a real explicit source-to-result clone, a retirement-borrowed mutable inout parameter, and readonly callback payload. Invalid cases now fail with location-bearing NWOWN001/NWASYNC001 diagnostics.

## Findings and resolution

| Finding | Original defect | Verified resolution |
| --- | --- | --- |
| A09-R1 | Callback close/drain merely named existing exports, allowing unrelated ABI or result-taking functions as retirement authority | Both operations borrow the exact notification owner; D06 notification authorities bind its cancel/try-retire steps |
| A09-R2 | Output-only creation could be labeled as clone | Exactly one source-owner borrow and one same-kind transferred output with status return |
| A09-R3 | Mutable inout async pointer escaped the input lifetime filter | Both in and inout inputs require the declared copy or retirement lifetime |
| A09-R4 | Owner name labels could disagree with physical pointer targets or omit the output-owner indirection | Exact opaque owner pointer and mutable pointer-to-owner output slot are required |
| A09-R5 | A D06 start/other nonrelease step could return void cleanup instead of acceptance/status information | All five nonrelease D06 steps return u32 status; release remains exact no-fail cleanup |
| A09-R6 | Notification could transfer an owner or retain payload storage beyond the callback | D05 notification pointer payloads are readonly callback-scoped borrows; owned results use later typed take |

R1–R4 were fixed in `eceff371f4893f5637e3f86ac732813bdc45a672`; R5–R6 in the final reviewed commit. The original accepted-invalid inputs, canonical outputs, stderr/stdout, source/binary identities and prior formal passes remain preserved under this review directory. They were not overwritten by successful rechecks.

## Limits

Only Linux x64 is accepted. The actual native fixture validates layout/extent consumption; ownership/callback/operation probes validate build descriptions. Runtime protocol implementations, A10/A11 generator output, pristine NuGet distribution, other platforms and performance/load claims remain their documented owners. The single-input Rust parser does not recursively import arbitrary source; final linked-symbol equality is mandatory for externally introduced exports. No full historical acceptance suite was repeated by the reviewer; receipt auditing, focused adversarial executions and final source review address the concrete review risks.

`final-review.json` is the machine-readable final decision; `final-formal-audit.json`, `final-probes/result.json` and `api-map-audit.json` bind its evidence. `review.json` and `review-followup.json` intentionally preserve the earlier changes-requested decisions.
