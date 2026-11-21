# Perf-01: interim completed HTTP comparison

All four current-epoch HTTP profiles completed with three independent processes per role. Every supplied process passed its original service standard and correctness checks. Original before-to-after mean-latency decisions are **within_band** or **inconclusive**; these receipts establish no HTTP mean-latency improvement or regression. Managed allocation observations fall substantially. All unfavorable latency and resource observations remain visible.

This report grants no capacity or 30-minute acceptance credit. The separate SQLite C16 service-standard failure remains unaccepted. HTTP completion does not change it.

## Versions and evidence scope

| Role | Product source | Common driver source | Package version |
| --- | --- | --- | --- |
| before | `ea5fa528035d025bd7a28698ee7c71194432236c` | `2e3995df8d86583ee9443348276ca8d918056bfc` | 0.1.0-perf01.recovery002.before.1 |
| after | `2f40348c3db80a4fbee7a99e721b374a597b16df` | `2e3995df8d86583ee9443348276ca8d918056bfc` | 0.1.0-perf01.recovery004.after.1 |
| direct | N/A: common direct driver | `2e3995df8d86583ee9443348276ca8d918056bfc` | N/A: direct Rust executable |

Final binding: `final-binding-004.json`, SHA-256 `8f8616f2932dd1c033309e177efa63429829f9ffa2b728a182406d943efdfa8d`. Measurement caller source index: `6b1d1e8ec6ee80271fdbbeb1c6d13909b92ca13c7a28cbc4fd4085f98f6a4c2c`.

All cases use the transport identifier in their JSON row (`http1-tls` or `http2-tls`), real sockets and the existing frozen setup. Only transport identifiers are retained; no certificate/key material, addresses or operational maps are published. These HTTP metadata establish no negotiated network-compression benefit. Separate gRPC identity-only tests and standalone codec results are outside this report; codec gains must not be called HTTP compression gains.

## Measurement definitions

- Independent processes are the statistical units. Aggregate mean/p50/p95/p99 are equal-weight means of three process values. In particular, aggregate p99 is a **mean of process p99 values**, never a pooled percentile.
- Original A21 noise decisions and intervals apply to **before-to-after process means only**. This reader supplies arithmetic after-to-direct gaps without a separate direct-comparison noise decision. No p99 or resource significance is inferred.
- Case success rates use the whole mixed-profile measurement denominator; they are not isolated-case throughput or maximum capacity. Small profiles mix tiny/1 MiB upload/1 MiB download; large profiles mix 8 MiB upload/download.
- CPU, RSS, allocation and gauges cover the entire profile. Headline RSS is the **maximum of the three process peaks**; the original mean of process peaks is separately retained.
- `GC.GetTotalAllocatedBytes(false)` uses the recorded partial bracket, not exact bytes/call. Direct Rust managed-GC fields remain N/A. Per-process counts and byte counters remain integers in JSON.
- Sampled native-byte gauges are not exact byte high-water marks. Literal HTTP encoded-byte counters do not quantify TLS/framing overhead or establish compression.

## Frozen load and completion

| Profile | Offered/s | Concurrency | Requested seconds/process | Processes/role | Actual execution start UTC | Actual execution end UTC |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| http1-small | 16 | 4 | 20 | 3 | 2026-11-21T07:27:25.050601+00:00 | 2026-11-21T07:33:09.206458+00:00 |
| http2-small | 16 | 4 | 20 | 3 | 2026-11-21T07:33:12.571941+00:00 | 2026-11-21T07:38:57.337214+00:00 |
| http1-large | 8 | 4 | 30 | 3 | 2026-11-21T07:39:00.688341+00:00 | 2026-11-21T07:46:24.414288+00:00 |
| http2-large | 8 | 4 | 30 | 3 | 2026-11-21T07:46:28.365355+00:00 | 2026-11-21T07:53:55.128181+00:00 |

Each profile records 19 finite owner commands (prepare/run for nine process cells plus comparison extraction), all exit zero and retired. All 36 workload processes are eligible and service-standard-passing, with zero unexpected errors and correctness failures. Warmup, recovery and idle observation remain separate from measurement duration.

## Before/after means, p99 and remaining direct Rust gap

Latencies are in milliseconds. Percent changes and decisions are copied from the original reader.

| Profile | Case | Before mean | After mean | Direct mean | B→A mean % | Original mean decision | Before p99 | After p99 | Direct p99 | After−direct mean % |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| http1-small | download 1 MiB | 4.929685 | 4.575485 | 3.137838 | -7.185044 | inconclusive | 12.163567 | 9.997607 | 6.277249 | 45.816477 |
| http1-small | tiny | 2.681475 | 2.546799 | 2.066534 | -5.022430 | inconclusive | 11.011653 | 6.993736 | 6.194677 | 23.240143 |
| http1-small | upload 1 MiB | 6.351315 | 5.832450 | 3.397524 | -8.169413 | within_band | 12.498138 | 12.380033 | 11.433143 | 71.667672 |
| http2-small | download 1 MiB | 5.684684 | 5.631593 | 4.514797 | -0.933936 | within_band | 16.239435 | 11.590079 | 8.316643 | 24.736339 |
| http2-small | tiny | 2.415723 | 2.559789 | 2.373749 | 5.963709 | inconclusive | 7.362738 | 15.087253 | 5.256314 | 7.837419 |
| http2-small | upload 1 MiB | 7.826874 | 7.674682 | 4.687103 | -1.944488 | within_band | 19.254133 | 14.966151 | 10.268705 | 63.740414 |
| http1-large | download 8 MiB | 20.879858 | 20.496226 | 12.142110 | -1.837329 | within_band | 41.118139 | 41.807505 | 30.904751 | 68.802835 |
| http1-large | upload 8 MiB | 29.841023 | 29.728489 | 11.258090 | -0.377109 | within_band | 49.607400 | 58.779180 | 29.972349 | 164.063359 |
| http2-large | download 8 MiB | 27.068684 | 28.159272 | 17.231865 | 4.028965 | inconclusive | 45.036941 | 47.372362 | 28.794850 | 63.413955 |
| http2-large | upload 8 MiB | 38.188303 | 39.182475 | 21.439649 | 2.603341 | inconclusive | 65.224576 | 62.377284 | 47.138770 | 82.757071 |

## Full aggregate latency and rate values

JSON also preserves each individual process value, original integer counters, outcomes, payload totals, actual time window and result hash.

| Profile | Case | Role | Mean ms | p50 ms | p95 ms | p99 ms | Success calls/s | Errors, three-process total |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| http1-small | download 1 MiB | before | 4.929685 | 4.470836 | 7.741333 | 12.163567 | 5.365828 | 0 |
| http1-small | download 1 MiB | after | 4.575485 | 4.196673 | 6.627597 | 9.997607 | 5.365832 | 0 |
| http1-small | download 1 MiB | direct | 3.137838 | 3.007539 | 4.548222 | 6.277249 | 5.365942 | 0 |
| http1-small | tiny | before | 2.681475 | 2.375523 | 3.636416 | 11.011653 | 5.365828 | 0 |
| http1-small | tiny | after | 2.546799 | 2.435933 | 3.454884 | 6.993736 | 5.365832 | 0 |
| http1-small | tiny | direct | 2.066534 | 1.891721 | 3.043194 | 6.194677 | 5.365942 | 0 |
| http1-small | upload 1 MiB | before | 6.351315 | 5.855930 | 9.463862 | 12.498138 | 5.316144 | 0 |
| http1-small | upload 1 MiB | after | 5.832450 | 5.456789 | 8.393447 | 12.380033 | 5.316148 | 0 |
| http1-small | upload 1 MiB | direct | 3.397524 | 2.972250 | 4.883423 | 11.433143 | 5.316257 | 0 |
| http2-small | download 1 MiB | before | 5.684684 | 5.225409 | 7.682662 | 16.239435 | 5.365908 | 0 |
| http2-small | download 1 MiB | after | 5.631593 | 5.289101 | 8.024511 | 11.590079 | 5.365748 | 0 |
| http2-small | download 1 MiB | direct | 4.514797 | 4.294365 | 6.384385 | 8.316643 | 5.365882 | 0 |
| http2-small | tiny | before | 2.415723 | 2.019942 | 3.635795 | 7.362738 | 5.365908 | 0 |
| http2-small | tiny | after | 2.559789 | 2.071962 | 4.202815 | 15.087253 | 5.365748 | 0 |
| http2-small | tiny | direct | 2.373749 | 2.129939 | 3.329323 | 5.256314 | 5.365882 | 0 |
| http2-small | upload 1 MiB | before | 7.826874 | 7.187212 | 11.306889 | 19.254133 | 5.316224 | 0 |
| http2-small | upload 1 MiB | after | 7.674682 | 7.322279 | 10.741937 | 14.966151 | 5.316065 | 0 |
| http2-small | upload 1 MiB | direct | 4.687103 | 4.350976 | 7.371496 | 10.268705 | 5.316197 | 0 |
| http1-large | download 8 MiB | before | 20.879858 | 19.355822 | 29.315840 | 41.118139 | 4.013997 | 0 |
| http1-large | download 8 MiB | after | 20.496226 | 19.397372 | 28.660470 | 41.807505 | 4.013777 | 0 |
| http1-large | download 8 MiB | direct | 12.142110 | 11.402421 | 14.791804 | 30.904751 | 4.014957 | 0 |
| http1-large | upload 8 MiB | before | 29.841023 | 28.893794 | 37.186091 | 49.607400 | 4.013997 | 0 |
| http1-large | upload 8 MiB | after | 29.728489 | 28.509744 | 35.914931 | 58.779180 | 4.013777 | 0 |
| http1-large | upload 8 MiB | direct | 11.258090 | 10.462786 | 13.699208 | 29.972349 | 4.014957 | 0 |
| http2-large | download 8 MiB | before | 27.068684 | 26.206600 | 38.142504 | 45.036941 | 4.013210 | 0 |
| http2-large | download 8 MiB | after | 28.159272 | 27.076639 | 38.882968 | 47.372362 | 4.013116 | 0 |
| http2-large | download 8 MiB | direct | 17.231865 | 16.628436 | 23.231503 | 28.794850 | 4.013932 | 0 |
| http2-large | upload 8 MiB | before | 38.188303 | 37.981585 | 54.297678 | 65.224576 | 4.013210 | 0 |
| http2-large | upload 8 MiB | after | 39.182475 | 39.154430 | 53.920569 | 62.377284 | 4.013116 | 0 |
| http2-large | upload 8 MiB | direct | 21.439649 | 19.425658 | 34.032564 | 47.138770 | 4.013932 | 0 |

## Whole-profile server resources

RSS max is max-of-process-peaks; RSS mean is the original mean-of-process-peaks. Values are not assigned to individual cases. CPU/allocation changes have no additional significance test.

| Profile | Role | Mean CPU seconds | Mean CPU % of one core | RSS max MiB | RSS mean MiB | Mean observed allocation MiB/s |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| http1-small | before | 1.210000 | 6.341181 | 68.171875 | 68.113281 | 6.615134 |
| http1-small | after | 1.106667 | 5.799785 | 68.355469 | 68.322917 | 1.388364 |
| http1-small | direct | 0.230000 | 1.205133 | 12.601562 | 12.580729 | N/A |
| http2-small | before | 1.490000 | 7.806818 | 68.941406 | 68.828125 | 6.629738 |
| http2-small | after | 1.426667 | 7.474833 | 69.097656 | 69.009115 | 1.391007 |
| http2-small | direct | 0.323333 | 1.695008 | 12.984375 | 12.962240 | N/A |
| http1-large | before | 6.356667 | 21.823618 | 68.566406 | 68.348958 | 8.876953 |
| http1-large | after | 6.396667 | 21.962538 | 68.609375 | 68.358073 | 4.938285 |
| http1-large | direct | 1.683333 | 5.779236 | 12.625000 | 12.597656 | N/A |
| http2-large | before | 8.766667 | 30.096952 | 69.085938 | 68.891927 | 8.901492 |
| http2-large | after | 8.943333 | 30.711072 | 69.191406 | 68.963542 | 4.949963 |
| http2-large | direct | 2.446667 | 8.403021 | 12.972656 | 12.944010 | N/A |

| Profile | Before → after allocation MiB/s | Allocation-rate change % | CPU-seconds change % | Mean-of-peak-RSS change % |
| --- | ---: | ---: | ---: | ---: |
| http1-small | 6.615134 → 1.388364 | -79.012304 | -8.539945 | 0.307775 |
| http2-small | 6.629738 → 1.391007 | -79.018671 | -4.250559 | 0.262959 |
| http1-large | 8.876953 → 4.938285 | -44.369589 | 0.629261 | 0.013335 |
| http2-large | 8.901492 → 4.949963 | -44.391756 | 2.015209 | 0.103952 |

## Payload and correctness

Totals below are per role across three process runs. JSON retains integer request/response payload, message and encoded-byte counters per process/case. All per-process correctness-failure counts are zero. A separate per-request content-hash boolean is not preserved in comparison metadata; this projection invents no such flag and rehashes no payload.

| Profile | Case | Calls: before / after / direct | Request payload bytes: before / after / direct | Response payload bytes: before / after / direct |
| --- | --- | --- | --- | --- |
| http1-small | download 1 MiB | 324 / 324 / 324 | 0 / 0 / 0 | 339738624 / 339738624 / 339738624 |
| http1-small | tiny | 324 / 324 / 324 | 0 / 0 / 0 | 5184 / 5184 / 5184 |
| http1-small | upload 1 MiB | 321 / 321 / 321 | 336592896 / 336592896 / 336592896 | 29853 / 29853 / 29853 |
| http2-small | download 1 MiB | 324 / 324 / 324 | 0 / 0 / 0 | 339738624 / 339738624 / 339738624 |
| http2-small | tiny | 324 / 324 / 324 | 0 / 0 / 0 | 5184 / 5184 / 5184 |
| http2-small | upload 1 MiB | 321 / 321 / 321 | 336592896 / 336592896 / 336592896 | 29853 / 29853 / 29853 |
| http1-large | download 8 MiB | 363 / 363 / 363 | 0 / 0 / 0 | 3045064704 / 3045064704 / 3045064704 |
| http1-large | upload 8 MiB | 363 / 363 / 363 | 3045064704 / 3045064704 / 3045064704 | 33759 / 33759 / 33759 |
| http2-large | download 8 MiB | 363 / 363 / 363 | 0 / 0 / 0 | 3045064704 / 3045064704 / 3045064704 |
| http2-large | upload 8 MiB | 363 / 363 / 363 | 3045064704 / 3045064704 / 3045064704 | 33759 / 33759 / 33759 |

## Observed native gauges and idle return

Values below are integer bytes in repetition order. Maxima are sampled process maxima, not transfer totals. Idle values are actual recorded after-idle observations. Direct Rust byte-owner/retained-byte gauges are separately preserved in JSON; its positive available-permit capacities are not described as zero.

| Profile | Role | Native payload sampled maxima | Native payload after idle | Active / queued / retiring after idle |
| --- | --- | --- | --- | --- |
| http1-small | before | [0, 0, 0] | [0, 0, 0] | [[0, 0, 0], [0, 0, 0], [0, 0, 0]] |
| http1-small | after | [0, 0, 0] | [0, 0, 0] | [[0, 0, 0], [0, 0, 0], [0, 0, 0]] |
| http2-small | before | [0, 0, 0] | [0, 0, 0] | [[0, 0, 0], [0, 0, 0], [0, 0, 0]] |
| http2-small | after | [98304, 32768, 0] | [0, 0, 0] | [[0, 0, 0], [0, 0, 0], [0, 0, 0]] |
| http1-large | before | [0, 32768, 32768] | [0, 0, 0] | [[0, 0, 0], [0, 0, 0], [0, 0, 0]] |
| http1-large | after | [32768, 0, 0] | [0, 0, 0] | [[0, 0, 0], [0, 0, 0], [0, 0, 0]] |
| http2-large | before | [32768, 0, 0] | [0, 0, 0] | [[0, 0, 0], [0, 0, 0], [0, 0, 0]] |
| http2-large | after | [32768, 32768, 0] | [0, 0, 0] | [[0, 0, 0], [0, 0, 0], [0, 0, 0]] |

## Retention implications and limits

These data support retaining the observed allocation reduction while the full task continues; they do not establish a latency win. Preserve HTTP/2 tiny p99 rising 7.362738 → 15.087253 ms, HTTP/1.1 8 MiB upload p99 rising 49.607400 → 58.779180 ms, and HTTP/2 large mean changes of +4.028965% download and +2.603341% upload. Applicable mean decisions remain inconclusive/within_band; p99 has no separate significance test. These combined-version comparisons do not identify the contribution of each retained change.

Direct-Rust upload/download gaps remain substantial. Fixed-rate success throughput is not maximum capacity. These short ordinary-case profiles do not independently grant cancellation, backpressure, long-duration or other-domain acceptance beyond their existing checked cases.

## Binary identities

| Role | Actual server executable filename and SHA-256 | Actual loaded NativeWeave server library SHA-256 |
| --- | --- | --- |
| before | `Perf01.ProtocolServer`: `0ac4867e2cfd626bdfcd453801c8b2646d9e4c20f1191c496fb5837252cf9462` | `libnativeweave_server.so`: `63c4950fceab5fe52017b5457b04759201de5a261d8087939cb177a20a5b88e2` |
| after | `Perf01.ProtocolServer`: `4f2715587cbf3bd7be05bdd4419fc2be73fe7dfc20fba8a66186b5a2753397f9` | `libnativeweave_server.so`: `8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0` |
| direct | `perf01-direct-protocols`: `5953ed7a9823c33965892ac6c9acb2c2712a29f8924c960e9e8d791de3fb020b` | N/A: direct Rust executable |

Package filenames/hashes, build-manifest hashes, dependency-lock identities and the shared actual client executable hash are retained in JSON. No native/executable payload was opened or rehashed while authoring this projection.

## Input receipts

Comparison hashes were already recorded by completed executions. The source index also binds small execution-metadata hashes and frozen noise hashes using profile labels and filenames only.

| Profile | Filename | Recorded comparison SHA-256 |
| --- | --- | --- |
| http1-small | `comparison.json` | `eb29fd329644b1f807b325e236e3a66b5657fe5a00485ab022ea956486db5ca3` |
| http2-small | `comparison.json` | `1ed273bd1f53c3b9a995d7254ab2286bdd586a5bb39e3de69ccf0003b53940e4` |
| http1-large | `comparison.json` | `a3310bc4dd988a1b275f4ebc8f62784a71b6a4f256f0ac6c5a605267c771fadd` |
| http2-large | `comparison.json` | `ce7961e19119177289a34ebab77fefdf4800d4566c6f15c7ab579958e58dfea0` |

Associated files: `comparison-http-001.json` contains the public numeric/identity projection; `comparison-http-001.sources.json` binds both authored files and input metadata. Authorship used bounded completed-metadata reads and output schema/privacy checks on CPU 8. No project-code import, benchmark, build, raw scan, payload hashing, new statistical test or remote write occurred.
