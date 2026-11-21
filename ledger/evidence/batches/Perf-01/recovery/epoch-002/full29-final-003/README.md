# Epoch-002 final selected Server: 29-command regression

The final selected Server regression caller completed **29/29 original outer commands**, all exit zero and fully retired, from `2026-11-21T05:01:03.936455+00:00` to `2026-11-21T05:12:16.247284+00:00`. Every owner recorded no remaining owned process or owner child and no cleanup signal. The selected product is `2f40348c3db80a4fbee7a99e721b374a597b16df` with Server SHA-256 `8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0` (**8815464 bytes**).

This execution reused the actual selected native asset from [after-004](../built-after-004/README.md), following the separate [final B18 verification](../functional-after-004/README.md). It grants **0 performance seconds and 0 formal 30-minute credit**. No prior ccff result is transferred.

## Actual functional scope and results

| Domain | Outer commands | Actual JIT / Debug | Actual Native AOT | API and package scope |
|---|---:|---|---|---|
| B17 HTTP host | 6 | 105 checks; 43 dispatches | 105 checks; 43 dispatches | Managed transport/lifetime fixtures; native producers and benchmark modes excluded |
| B15 application | 1 | 85 actual Rust Host assertions | 85 actual Rust Host assertions | Original selected-native verifier, API and five-package consumer proof |
| B19 MCP | 10 | 291 assertions; 180 managed retirements | 291 assertions; 180 managed retirements | 65 public symbols; five static compile fixtures; five-package consumer proof |
| B20 diagnostics | 12 | Debug: 5 assertions; Release JIT: 122 | 122 assertions | 10 RequestContext declarations/XML; original Debug sample; four-package consumer proof |

**Scope of “29”:** six B17 commands, one unchanged B15 verifier, ten B19 commands and twelve B20 commands. The B15 verifier records 15 child commands, including a package probe with 14 commands. B19 and B20 package probes record 22 and nine commands respectively. These are nested receipts, not additional outer commands. B19 native unit/preparse and generator-specific suites, B20 native suites/cost modes, and performance workloads are outside this caller.

B15 separately ran **492 fake-transport managed component assertions in JIT and 492 in AOT**. These counts are not added to the actual Rust Host assertions. Its API output confirms **278 exact symbols**, deterministic positive generated consumers and **seven negative consumer fixtures**.

## Transport and lifecycle observations

B17 JIT and Native AOT logs confirm HTTP/1.1 and HTTP/2, their actual TLS combinations, and request-admission/final-lease retirement across HTTP/1.1 and HTTP/2 TLS.

B19 JIT and Native AOT each observed the finite close wait retaining pending managed cancellation tails, nested callbacks retaining request/scope until the application returns, and global-pressure/cancel termination draining native and managed credits. The exact marker counts remain in the JSON projection.

B20 Release JIT and Native AOT each executed both HTTP/1.1 and HTTP/2 Close/Finish regressions. In each mode, each protocol-specific Content-Length marker appears once; each shared lifecycle marker below appears twice, once per protocol:

- The peer receives the exact Content-Length payload before managed Finish.
- Close retains the admitted dispatch while Finish is gated, before its deadline.
- Accepted Finish succeeds during graceful close.
- The response ends exactly, without extra payload.
- One success Activity is emitted without a failure warning.
- Close joins Finish and releases every business owner.

The existing default-diagnostics ownership join and throwing-listener retirement markers also passed. These are constructed functional-boundary observations. They do not establish the cause of an earlier high-load drain failure or quantify a performance improvement.

## Original Debug sample confirmation

| Mode | Exit | Activities | Measurements | Expected `/failure` 5xx warnings | Unexpected failure warnings | Completed-2xx failure warnings |
|---|---:|---:|---:|---:|---:|
| disabled | 0 | 0 | 0 | 0 | 0 | 0 |
| explicit local | 0 | 2 | 44 | 4 | 0 | 0 |

The explicit-local sample completed with exactly four `application_failure` warnings, all for the intentional `/failure` route with HTTP/1.1 5xx status. Both sample stderr logs were empty. No completed-2xx application-failure warning appeared in this execution. These sample counters are diagnostic observations, not throughput or error-rate measurements.

## Package and ordinary-edit reuse

| Package proof | Original commands | Package count | Selected SDK modes | Native reuse / application checks |
|---|---:|---:|---|---|
| B15 | 14 | 5 | JIT, AOT | Minimal/advanced HTTP1/HTTP2, transitive generator, ordinary DTO edit, no consumer Rust |
| B19 | 22 | 5 | JIT, AOT, external JIT, external AOT | Ordinary DTO and external private-only edit; regenerated layout proof; no explicit analyzer reference or repository build imports; no consumer Rust |
| B20 | 9 | 4 | JIT, AOT | Disabled and local diagnostics modes; no parent repository imports or consumer Rust |

All eight recorded SDK output identities retain the same selected Server native hash. B15/B19 ordinary-edit proof and B20 diagnostics-consumer proof are their original component-package scopes; they do not constitute public B24 domain-package release acceptance. Package names and archive identities below come from the successful original collectors. This documentation pass did not rehash archive payloads.

| Proof | Package archive | SHA-256 |
|---|---|---|
| B15 | NativeWeave.Interop.Abi.0.1.0-preview.1.nupkg | `aceee947224f1f003a2e1f8dbe610805a4bd13aa9364b9b81a8fd244786e9930` |
| B15 | NativeWeave.Core.0.1.0-preview.1.nupkg | `9fb5921c953e86a48045a021a33bfc035ee21700a002b00ca8acf277f23e19cf` |
| B15 | NativeWeave.Server.Generator.0.1.0-preview.1.nupkg | `cab5b717b3dc38acffa3127b9672597012cb98f62d0019f70e39a5baed5d3fbc` |
| B15 | NativeWeave.Server.0.1.0-preview.1.nupkg | `8c7afe76d463388b3b6e458da6cf8d1683301ae360eff3cadf7db202ec4e39fc` |
| B15 | NativeWeave.Server.Hosting.0.1.0-preview.1.nupkg | `54483ad9c0d7fd0ec8697e163b49ffcb572b59235626b446c82d681f24dd6c02` |
| B19 | NativeWeave.Interop.Abi.0.1.0-preview.1.nupkg | `aceee947224f1f003a2e1f8dbe610805a4bd13aa9364b9b81a8fd244786e9930` |
| B19 | NativeWeave.Core.0.1.0-preview.1.nupkg | `9fb5921c953e86a48045a021a33bfc035ee21700a002b00ca8acf277f23e19cf` |
| B19 | NativeWeave.Server.Generator.0.1.0-preview.1.nupkg | `cab5b717b3dc38acffa3127b9672597012cb98f62d0019f70e39a5baed5d3fbc` |
| B19 | NativeWeave.Server.0.1.0-preview.1.nupkg | `8c7afe76d463388b3b6e458da6cf8d1683301ae360eff3cadf7db202ec4e39fc` |
| B19 | NativeWeave.Server.Mcp.0.1.0-preview.1.nupkg | `19af7dfd5c84e3491e361729922e072a84c9f60e360c0424be6d2c8628a24bde` |
| B20 | NativeWeave.Interop.Abi.0.1.0-preview.1.nupkg | `aceee947224f1f003a2e1f8dbe610805a4bd13aa9364b9b81a8fd244786e9930` |
| B20 | NativeWeave.Core.0.1.0-preview.1.nupkg | `9fb5921c953e86a48045a021a33bfc035ee21700a002b00ca8acf277f23e19cf` |
| B20 | NativeWeave.Server.Generator.0.1.0-preview.1.nupkg | `cab5b717b3dc38acffa3127b9672597012cb98f62d0019f70e39a5baed5d3fbc` |
| B20 | NativeWeave.Server.0.1.0-preview.1.nupkg | `8c7afe76d463388b3b6e458da6cf8d1683301ae360eff3cadf7db202ec4e39fc` |

## Actual outer command retirement

| Command | Start UTC | End UTC | Seconds | Exit | Retired |
|---|---|---|---:|---:|---|
| b17-jit-restore | 2026-11-21T05:01:04.700414+00:00 | 2026-11-21T05:01:18.197152+00:00 | 13.497 | 0 | yes |
| b17-jit-build | 2026-11-21T05:01:18.901711+00:00 | 2026-11-21T05:01:44.458504+00:00 | 25.557 | 0 | yes |
| b17-jit-execute | 2026-11-21T05:01:45.451780+00:00 | 2026-11-21T05:01:46.468156+00:00 | 1.016 | 0 | yes |
| b17-aot-restore | 2026-11-21T05:01:47.364309+00:00 | 2026-11-21T05:02:01.426663+00:00 | 14.062 | 0 | yes |
| b17-aot-publish | 2026-11-21T05:02:02.115860+00:00 | 2026-11-21T05:02:43.342360+00:00 | 41.227 | 0 | yes |
| b17-aot-execute | 2026-11-21T05:02:44.024673+00:00 | 2026-11-21T05:02:44.869344+00:00 | 0.845 | 0 | yes |
| b15-selected-native | 2026-11-21T05:02:45.629900+00:00 | 2026-11-21T05:05:15.145285+00:00 | 149.515 | 0 | yes |
| b19-restore-jit | 2026-11-21T05:05:15.887114+00:00 | 2026-11-21T05:05:17.316311+00:00 | 1.429 | 0 | yes |
| b19-build-jit | 2026-11-21T05:05:18.186090+00:00 | 2026-11-21T05:06:06.444486+00:00 | 48.258 | 0 | yes |
| b19-actual-jit | 2026-11-21T05:06:07.163000+00:00 | 2026-11-21T05:06:08.802374+00:00 | 1.639 | 0 | yes |
| b19-api-restore | 2026-11-21T05:06:09.509910+00:00 | 2026-11-21T05:06:10.941421+00:00 | 1.432 | 0 | yes |
| b19-api-build | 2026-11-21T05:06:11.653968+00:00 | 2026-11-21T05:06:15.455051+00:00 | 3.801 | 0 | yes |
| b19-api-exact | 2026-11-21T05:06:16.170857+00:00 | 2026-11-21T05:06:17.240608+00:00 | 1.070 | 0 | yes |
| b19-restore-aot | 2026-11-21T05:06:18.034457+00:00 | 2026-11-21T05:06:19.824293+00:00 | 1.790 | 0 | yes |
| b19-publish-aot | 2026-11-21T05:06:20.504715+00:00 | 2026-11-21T05:07:43.920626+00:00 | 83.416 | 0 | yes |
| b19-actual-aot | 2026-11-21T05:07:45.111497+00:00 | 2026-11-21T05:07:45.921870+00:00 | 0.810 | 0 | yes |
| b19-package-consumer | 2026-11-21T05:07:46.821546+00:00 | 2026-11-21T05:09:39.347729+00:00 | 112.526 | 0 | yes |
| b20-managed-debug-build | 2026-11-21T05:09:40.281080+00:00 | 2026-11-21T05:10:04.959980+00:00 | 24.679 | 0 | yes |
| b20-actual-debug | 2026-11-21T05:10:05.939196+00:00 | 2026-11-21T05:10:06.249263+00:00 | 0.310 | 0 | yes |
| b20-managed-release-build | 2026-11-21T05:10:06.953585+00:00 | 2026-11-21T05:10:14.318551+00:00 | 7.365 | 0 | yes |
| b20-actual-jit | 2026-11-21T05:10:15.027202+00:00 | 2026-11-21T05:10:19.486412+00:00 | 4.459 | 0 | yes |
| b20-api-build | 2026-11-21T05:10:20.237123+00:00 | 2026-11-21T05:10:23.661326+00:00 | 3.424 | 0 | yes |
| b20-api-public-xml | 2026-11-21T05:10:24.381893+00:00 | 2026-11-21T05:10:24.802242+00:00 | 0.420 | 0 | yes |
| b20-sample-debug-build | 2026-11-21T05:10:25.512907+00:00 | 2026-11-21T05:10:30.026136+00:00 | 4.513 | 0 | yes |
| b20-sample-debug-disabled | 2026-11-21T05:10:30.722621+00:00 | 2026-11-21T05:10:31.413712+00:00 | 0.691 | 0 | yes |
| b20-sample-debug-explicit-local | 2026-11-21T05:10:32.195518+00:00 | 2026-11-21T05:10:32.508296+00:00 | 0.313 | 0 | yes |
| b20-publish-aot | 2026-11-21T05:10:33.341249+00:00 | 2026-11-21T05:11:15.284639+00:00 | 41.943 | 0 | yes |
| b20-actual-aot | 2026-11-21T05:11:15.977106+00:00 | 2026-11-21T05:11:19.777237+00:00 | 3.800 | 0 | yes |
| b20-package-consumer | 2026-11-21T05:11:20.513856+00:00 | 2026-11-21T05:12:14.992640+00:00 | 54.479 | 0 | yes |

## Provenance and public projection

- Actual execution SHA-256: `5496af175783b034a44459a83409835ba384152f64115255a905bbe92719bb50`.
- Actual result SHA-256: `f6b82ca413ea73d944f8cd4fab9e3dc93dc210ccdaf5f07a0454ea780b09c824`.
- Selected-native caller source index: `9e58869e945097a8dac9360bd1b13a55fe73f69002e3a922cbca33d38874a6db`.
- Measurement admission source index: `6b1d1e8ec6ee80271fdbbeb1c6d13909b92ca13c7a28cbc4fd4085f98f6a4c2c`.
- Original immutable baseline admission: `56725c0a0167e04bb021210d879b6616f85523705bc19bd04bc11e2cbb42d380`.
- Run-specific admission inventory: `93ee220fe073679248cfb7c7554a839e2c68a5c2549ac95397acc92c3f601f3b`.
- Final selected-after descriptor: `8f8616f2932dd1c033309e177efa63429829f9ffa2b728a182406d943efdfa8d`.

[projection.json](projection.json) records all 29 owner receipt hashes, 58 owner output-log hashes, the original nested command identities, package/native reuse and exact repair markers. This pass checked **60 nested child logs**, the small result/summary documents and **11 before/after binary-inventory records**. Every inventory reports identical inputs after its fixture; the full **412-entry payload map was not rehashed** in this pass.

Only curated observations, filenames, counts and source/content hashes are public. Operational paths, command environments, TLS material and process identifiers are omitted. This curation did not launch a producer, fixture, profile or workload, and claims no archive upload, durable readback, capacity, high-load root cause or measured performance benefit.
