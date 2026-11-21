# Selected-native Server regression caller: independent source review

**Accepted for coordinated finite execution; no blocking source defect found.**
This is an independent source review of the additional B17/B15/B19/B20 caller,
not a test result. The reviewer did not import the caller or verifier modules,
build a product, run a fixture, or start load. Existing controller ownership
must continue to serialize its eventual execution.

## Reviewed identity

| Input | Identity |
| --- | --- |
| Regression caller source index | `20ebc83402a1ded7fcec377ad82805edb597fd0f9291eb01015b0f9618620a38` |
| Product used for source/schema review | `ccff42c0df4141984ef9de497af7cd768753704a` |
| Reused build/owner/helper index | `c7526f08d3c50c6d58f7336adae6ebab5fb82b606cce140108a48f6b54b3d0ab` |
| Baseline product role | `ea5fa528035d025bd7a28698ee7c71194432236c` |
| Common application/driver role | `2e3995df8d86583ee9443348276ca8d918056bfc` |
| Design role | `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9` |

The source index, all four indexed caller files, all four reused control files,
and all eighteen recipe-source hashes were read and checked against actual
local bytes. The three caller modules were inspected as text. Additional reads
covered the referenced project files, native-asset generation targets, original
component verifiers and package probes, and preserved B17/B20 result contracts.
Review reads and small-file hashes used CPU 8. No binary/toolchain inventory or
completed build receipt was rehashed by this reviewer while the controller ran;
those are admission checks required by the reviewed caller itself.

## Command and result contract

| Group | Outer commands | Source-review conclusion |
| --- | ---: | --- |
| B17 | 6 | Locked JIT restore/build/execute and locked AOT restore/publish/execute match the preserved managed subset. The selected asset is explicit in both builds. Separate TLS fixture directories avoid changing executable inventories. Four transport markers, the retirement marker, and the preserved 105-check/43-dispatch completion expectation are checked. |
| B15 | 1 | Runs the unchanged selected-native verifier, including JSON/component, real Host, API and independent package checks. Result fields and original `log`/`sha256` command records match the actual verifier schema. The 85/85 Host assertions and 278-symbol contract remain explicit. |
| B19 | 10 | Matches the original managed/API/package subset and excludes native producers, native unit/preparse and generator-specific suites. The original minimum of 230 assertions, equal JIT/AOT assertion totals, three lifecycle markers, 65 symbols and five static consumers are retained. Managed retirement totals are observed separately per mode rather than forced to a historical value. |
| B20 | 12 | Matches Debug defaults, Release JIT/AOT, API/XML, Debug samples and the original package probe. All cost modes are excluded. The 5/110/110 assertion and dynamic/configuration markers, ownership join, throwing-listener retirement and ten-declaration API contract agree with the committed fixture and preserved result. |

The 29 commands retain the documented original finite bounds. The package
reader correctly distinguishes B15/B19 `.log` files from B20 `.txt` files and
uses their actual `log_sha256` schema. Package dictionaries, native hashes,
JIT/AOT executable paths, SDK output records and B19 external-layout edit
outputs match the three unchanged package probes. These functional package
probes keep their original package construction; they do not replace the
separately bound B24 measurement packages.

## Binding and ownership

The existing timing lock is acquired nonblocking before expensive admission.
Both completed eight-producer build receipts are checked using the **original
build caller** source-index hash. The selected Server asset can only come from
the after binding, whose product commit must match the explicit final commit;
the baseline and common driver identities are not reassigned.

The SDK argument is the directory containing the admitted `dotnet` executable,
as required by the original API probes. Nested `python3` and `dotnet` resolution
is checked after constructing the child environment. Fresh output/cache/temp
directories, source cleanliness, source/file rechecks and disk floors are
retained. No command in the subset invokes a Rust producer.

Direct executable inventories check the propagated Server SDK record and the
actual native bytes immediately before and after execution. API-only probes
intentionally do not require a Server runtime record. B15 owns its nested
execution; its binary inventory is collected after its unchanged verifier
finishes, as documented. Failed or interrupted finite-owner receipts remain
attributed to the failed attempt. The caller delegates process/session/adopted
child retirement to the unchanged c752 pidfd/subreaper owner.

## Remaining acceptance

The reviewer found no source change needed before attempting the coordinated
run. Actual command completion, loaded native identity, assertions, child
retirement and result collection still need execution evidence. A source-only
approval neither grants a complete B17/B19/B20 native-verifier pass nor replaces
B18 assembled TLS verification. Functional acceptance, performance acceptance
and 30-minute measurement credit from this review are all zero. Preserve any
failure with its real output; do not substitute old assertion counts or an old
binary result.
