# Perf-01 — preserved B20 close/finish blocker

The selected runtime `ccff42c0df4141984ef9de497af7cd768753704a` has an actual B20 failure that blocks complete functional acceptance. A diagnostic then reproduced a failed managed response finish while graceful close was pending, after the peer had received the complete fixed-length response. Final ownership cleanup succeeded, but the admitted response operation failed. These are separate outcomes.

All four failed records below remain failed. [projection.json](projection.json) preserves their actual UTC intervals, finite-owner receipts and log hashes, successful subset observations, diagnostic source identities, and normalized exception locations. Preparation of this projection ran no build, test, or load.

## Original regression caller and completed subsets

The original 29-command caller, source index `20ebc83402a1ded7fcec377ad82805edb597fd0f9291eb01015b0f9618620a38`, ran from **03:10:51.975911 to 03:20:20.938829 UTC on 2026-11-21**. Twenty-five commands completed successfully. Command 26, `b20-sample-debug-explicit-local`, failed with exit `-6`; its owner retired with zero remaining owned processes or adopted children. The B20 AOT publish, AOT execution, and package consumer commands were not executed.

| Completed subset | Actual result |
|---|---|
| B17 Release JIT | 105 checks, 43 dispatches, dynamic code enabled. HTTP/1.1 and HTTP/2 clear/TLS transport markers and request-admission/final-lease retirement passed. |
| B17 Native AOT | 105 checks, 43 dispatches, dynamic code disabled; the same four transport markers and retirement checks passed. |
| B19 Release JIT | 291 assertions, 180 managed retirements, dynamic code enabled. |
| B19 Native AOT | 291 assertions, 180 managed retirements, dynamic code disabled. |
| B20 Debug fixture | Five assertions, dynamic code enabled. |
| B20 Release JIT fixture | 110 assertions, including the existing completed Content-Length finish check. |
| B20 Debug sample with diagnostics disabled | Zero activities and zero measurements; exit zero. |

The failed explicit-local sample logged four intentional `/failure` warnings plus an unexpected fifth warning for `/hello/{name}` with status class `2xx`. Its original terminal assertion was `Explicit diagnostic listener did not run.` at `samples/api/server-diagnostics/Program.cs:42`. The literal assertion text alone does not identify which listener condition failed. The subsequent diagnostic resolves that distinction without weakening the assertion.

The supplied actual Server asset was **8,814,544 bytes**, SHA-256 `1f023b7506bde3f8c4a13b12de92e3e9503004ca3afc2d41a53bec17e44f1d97`. The original binary inventory receipts preserve each fixture's input identities. Nine inventory receipts record unchanged bytes after successful execution; the failing sample inventory has only its original pre-execution record. This projection does not fabricate an after-execution check for that failed command or claim a continuous runtime mapping observation.

## Failed diagnostic attempts and observed close behavior

| Record | Actual UTC interval on 2026-11-21 | Observed outcome |
|---|---|---|
| `b20-diagnostic-001` | 03:28:08.216462–03:28:16.504937 | Restore failed with `NU1900`: vulnerability-data service index unavailable, treated as an error. The restore owner ran 03:28:09.235673–03:28:16.502614, exited 1, and retired. No diagnostic fixture executed. |
| `b20-diagnostic-002` | 03:29:18.221995–03:30:02.284397 | Restore/build completed. Eight fresh sample processes passed, then `sample-08` failed the unchanged assertion. It observed two activities, 44 measurements, and five warnings instead of four. Its owner exited `-6` and retired with no remaining children. |
| `b20-gated-001` | 03:34:19.374987–03:34:38.533033 | Restore/build completed. One gated HTTP/1.1 sample received and validated status 200 and the exact four-byte `body` response. After starting close with a two-second budget, it released the finish gate at **253.100 ms**, while close was still incomplete. Finish failed; subsequent close reported `Completed`, zero pending requests, zero retained native bytes, and zero retained managed bytes. The sample owner exited `-6` and retired. |

The first-chance diagnostic source is `82840baeb3849eac82f04aa5575a4834fce29929`. Its only change from the selected runtime source is the diagnostic sample's `Program.cs`. It retains the original 16-request sequence and assertion, collects bounded first-chance observations, and excludes the known intentional application exception. All eight passing processes observed two activities, 44 measurements, four warnings, and zero retained first-chance events. The failing ninth process observed five first-chance records carrying the native invalid-state exception through `ServerResponse.CompleteCoreAsync` at `src/Server.Application/Response.cs:178`, then `Results.cs:182` and `Application.cs:228`. These five records show exception propagation; they do **not** establish five failed requests or identify a native request ticket.

The gated source is `4730708f1c22a3ea0ef9421262316eee947f3573`. Its changes from the selected runtime are limited to sample `Program.cs` and the new diagnostic `GateFinish.cs`. The original runtime implementation is unchanged. Its handler writes a declared four-byte response, waits at a managed gate, then calls the ordinary public `CompleteAsync`. The peer validates the response before close starts. The sample deliberately releases the gate after a requested 250 ms delay. The failed sample's complete owner lifetime was **0.611842434 seconds**, shorter than the two-second close budget, so this observation is not a close-budget timeout. The later zero-owner close does not make the failed finish successful.

## Observed status and source hypothesis

Both diagnostics report `InvalidOperationException` with the exact message mapped from status 4 by the unchanged `src/Server.Native/NativeCodec.cs:50`; the ABI defines status 4 as `NW_INVALID_STATE`. The recorded managed stack reaches the awaited native finish at `Response.cs:178`. The numeric status itself was not separately logged; the status classification is an inference from that exact mapper and exception path.

Source inspection at `ccff42c0…` identifies a plausible close lifetime problem: `Host.run` returns after acceptors finish and one reap, the worker drops its Tokio runtime and clears the runtime handle, and `OpState.start` rejects a missing handle with `NW_INVALID_STATE`. A managed callback may still be waiting to initiate finish after the connection body has completed. **The diagnostic does not observe which native rejection branch ran.** This source hypothesis is distinct from the actual reproduced failure and is not a recorded runtime branch trace.

Repair work remains separate. These records contain no successful execution of a repaired runtime, no performance result, and no new final selection or global acceptance.

## Retrieval identities and scope

| Original execution record | SHA-256 |
|---|---|
| `server-regressions-002` | `6d8afc03415a5ea736c8e7a5ae6cf5ea1f75d2446b3abc3f96d82987852e3b46` |
| `b20-diagnostic-001` | `537b5baa0966a926f7f481799146f16c7b303ef7366770f1c82bbdf5770def14` |
| `b20-diagnostic-002` | `a908c94d6bf1ea52ec57d049b64fd040271b44a5d02d4f6b78966c164c8e617b` |
| `b20-gated-001` | `ad8e9cd3e3d4ab4b97f466e53abd9d4ece06473d9cc295d5567680aa7712ab33` |

All **41 command receipts** and **82 owner output logs** were rehashed against their recorded identities. Both completed diagnostic binary maps were rehashed locally; only principal filenames/hashes and map counts are projected. Source changes were checked using the exact Git commits. Original private maps, environment/proxy values, root paths, process identifiers and TLS material remain unpublished. The projection is a readable receipt/numerical record, not a complete binary or raw-log archive.

All observations here are functional or diagnostic. **Performance credit: zero seconds. Current 30-minute credit from this record: zero.** The successful B17/B19 subsets and passing B20 fixture process remain useful scoped evidence; the complete caller and the two executed diagnostic experiments retain their failure status.
