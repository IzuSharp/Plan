# Perf-01: completed callback-scan functional evidence reconciliation

This read-only review confirms actual completed **A06 and assembled B18** runs for `092e5e2c74d7419772f2455a2922ae4238f389de`. It does not relabel them as executions of the currently reviewed `2c88e5dbbc197079c48c3c41d51101b2d58bb3a5` test source. No build, test, workload, target import or timing-lock operation was performed by this reviewer.

## Source identity and limited reuse

A Git tree comparison shows that tested `092e5e2` and initial scan-bound commit `59eec092eb33ec780bd02cf0d51bdfa9e1c24041` have identical trees. Between that tree and current `2c88e5d`, the only changed file is `tests/Interop.Callbacks/Program.cs`. Production sources, including the callback coordinator, are equal.

| Source | Executed bytes | Current reviewed bytes |
|---|---|---|
| `src/Interop.Callbacks/CallbackCoordinator.cs` | `c21a46424c7f401f0ddeb9f7d5c14716c13df7b619c671349ec96d1afd6d8667` | Same |
| `tests/Interop.Callbacks/Program.cs` | `9c93dde1805ecc26d5c963bbbb23d76acd1a04386659b656c095427338a8bc06` | `260f8bf930b467705e099eea413a5e700b54d815ed923588a09986861725691a` |

The current test-only revision gives each probe an independent scheduler, permits progress at `Runs >= 1`, removes only the new aggregate queue assertion, and guards the blocking hook once. The executed initial fixture calls both `SparseCoordinatorRetryAndReuse` and `CoordinatorReservationDuringRetry` from `Main`. Its actual pass does not disprove the previously identified possible test scheduling race. The corrected test bytes have **no execution credit from these receipts**.

## Actual A06 execution

The existing finite controller ran the unchanged `tests/Interop.Callbacks/verify.py --offline` from 2026-11-21 **10:51:14.048848 to 10:52:46.614169 UTC**. The actual result records a clean source and unchanged source inventory.

| Executed check | Actual result |
|---|---|
| Managed Release JIT conformance | 6,343 assertions; 43 owners; 32 controlled GC races; pending/active/roots all zero |
| Native AOT conformance | 6,344 assertions; 43 owners; 32 controlled GC races; pending/active/roots all zero |
| Rust Release callback tests | 5 passed, 0 failed, 0 filtered |
| Maintainer sample | JIT and AOT passed |
| Invalid UCO runtime fixtures | JIT and AOT exited −6 as expected; `InvalidProgramException` present; callback body not entered |
| Invalid UCO compile fixture | Exit 1 as expected, with `CS8894` |
| Original verifier command inventory | 35 commands: 32 exit zero and the three expected negative fixtures above |
| Outer finite-owner closure | Exit 0; retired; 78 observed owned/descendant identities; no live owned processes or owner children remaining |

The assertion markers were checked against their retained stdout hashes, and the expected negative markers against the retained logs. The unchanged inner verifier records command exit statuses and log hashes rather than individual pidfd retirement receipts. Retirement is therefore supported by the outer finite-owner closure and its empty final child sets; this review adds no claim about unobserved process identities.

## Actual assembled B18 execution

The existing controller then completed supplied-native B18 from 2026-11-21 **11:03:33.219243 to 11:07:21.188535 UTC** for the same actual managed source `092e5e2`.

| Executed check | Actual result |
|---|---|
| JIT gRPC fixture | 1,036 assertions; 595 managed retirements |
| Native AOT gRPC fixture | 1,037 assertions; 596 managed retirements |
| Assembled verifier commands | 18/18 exited zero |
| Independent package consumer commands | 25/25 exited zero |
| Outer finite-owner closure | Exit 0; retired; 103 observed owned/descendant identities; no live owned processes or owner children remaining |

The supplied Server asset is `8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0`, with native source `2f40348c3db80a4fbee7a99e721b374a597b16df`. The verifier reused the existing native-component receipt (`79a36155…`), whose component binary is `83b57ab5…`; that binary is distinct from the supplied product asset, and those native tests were **not rerun in this B18 execution**. Binary hashes are quoted from the completed receipts and were not recomputed by this review.

## Existing sequence and remaining scope

At inspection, the existing `callback-prefix-protocol-build-001` controller receipt reported `running`, with its B18 prerequisite and B24 package command already complete and retired. Its bound plan is `callback-prefix-recipes-004/protocol-build.actual-001.json` (`0c24409139f2cc821dbd5ba605dbfb43809b9cb0490b745390a47aa2ddcbb149`). No duplicate producer was prepared or executed, and this review makes no completion claim for that active build.

A bounded inspection of the immediate epoch directory and the 13 small JSON recipes in `callback-prefix-recipes-001` through `-004` found no A07 command or nearby named A07/Async output. This is a local search result, not proof that no other controller has scheduled or executed A07. Coordination remains necessary before any further execution.

These receipts support functional coverage of the actual recorded source and identical production bytes. They provide no performance, capacity, 30-minute, pristine-machine, public-release or GitHub-approval credit. The test-only revision still requires its own execution if that revised fixture is selected.

## Evidence

The accompanying JSON contains exact artifact-relative paths and SHA-256 bindings; artifact paths are relative to the retained epoch-002 recovery collection.

| Record | SHA-256 |
|---|---|
| A06 plan | `dae2afcfba34105fa3f43d6ae17cb3f7875ef7918bed7e4cd0907e0cc5d7cf34` |
| A06 outer execution | `52d27e626c23101251153ca40f540af3fe5f1d80d9a87aca31d6f15ce506dbfd` |
| A06 result | `1c6c8086c149899307909fee683cc243a9f1abe6b3e25a9cb687a7a0512511af` |
| B18 plan | `394ac8a707126f75e7bbbe26f6665abe8034f8485d2dee36ff061cf679bad4e5` |
| B18 outer execution | `2ac30e536735ed61a0d37963e4cad4207d370a486943e2ed9360b47865827e38` |
| B18 result | `be0c9ccabaa0b675b5d2ede4ab2fecf3ef231adb21390e5773a7359b5e01d9c1` |

Both original completed records remain unchanged. [Machine-readable review](callback-scan-executed-evidence-review-001.json).
