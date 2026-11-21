# Perf-01: interim completed gRPC comparison

The original reader reports a **server-stream mean-latency regression**: 43.159840 → 51.431850 ms, **+19.165987%**. The original 95% independent-process bootstrap interval for the absolute change is 4.354283 to 12.005806 ms against a 4.320883 ms noise band. Unary increases remain **within_band** under their original calibration; client-stream and duplex increases remain **inconclusive**. All adverse observations are retained. These combined-version comparisons do not identify a causal patch.

Both current-epoch profiles completed, with three independent processes per role and zero recorded unexpected errors or correctness failures. This is an interim short-test report: it grants no maximum-capacity, 30-minute, cancellation/deadline, trailers or other-domain acceptance. The separate SQLite C16 failure remains unaccepted.

## Versions and evidence scope

| Role | Product source | Common driver source | Package version |
| --- | --- | --- | --- |
| before | `ea5fa528035d025bd7a28698ee7c71194432236c` | `2e3995df8d86583ee9443348276ca8d918056bfc` | 0.1.0-perf01.recovery002.before.1 |
| after | `2f40348c3db80a4fbee7a99e721b374a597b16df` | `2e3995df8d86583ee9443348276ca8d918056bfc` | 0.1.0-perf01.recovery004.after.1 |
| direct | N/A: common direct driver | `2e3995df8d86583ee9443348276ca8d918056bfc` | N/A: direct Rust executable |

Final binding: `final-binding-004.json`, SHA-256 `8f8616f2932dd1c033309e177efa63429829f9ffa2b728a182406d943efdfa8d`. Measurement caller source index: `6b1d1e8ec6ee80271fdbbeb1c6d13909b92ca13c7a28cbc4fd4085f98f6a4c2c`.

All cases retain `http2-tls`: independent client, real HTTP/2 sockets and the frozen TLS setup. The selected product guide, `protocols-grpc.md` at the after product commit above, implements **identity payload compression only** (guide SHA-256 `6f6b01b042173a86fbf621cf482c26fb5eaf633cee2c486025c1c72ee791167e`). These metadata supply no per-request negotiated-compression flag and establish no network compression benefit. Standalone codec results are separate.

## Measurement definitions

- Independent processes are the statistical units. Aggregate mean/p50/p95/p99 are equal-weight means of three process values. Aggregate p99 is a **mean of process p99 values**, never a pooled percentile.
- Original A21 decisions and intervals apply only to before-to-after process means. After-to-direct gaps are arithmetic; this reader supplies no separate direct-comparison noise test. No p99 or resource significance is inferred.
- Call, message and payload rates share the whole mixed-profile measurement denominator. They are not isolated-case throughput or maximum capacity. Configured concurrency is four; an independently measured simultaneous HTTP/2 stream count is unavailable in this comparison.
- CPU, RSS, allocation and gauges cover the entire profile. Headline RSS is the **maximum of process peaks**; the original mean of process peaks is retained separately.
- Managed allocation uses `GC.GetTotalAllocatedBytes(false)` over the recorded partial bracket, not exact bytes/call. Direct Rust managed-GC fields remain null/N/A.
- Counts remain integers. Encoded protobuf bytes are not HTTP/2/TLS wire bytes or compression evidence. For client-stream summary responses, a zero counted data payload can coexist with nonzero encoded fields.

## Frozen load and completion

| Profile | Offered calls/s | Concurrency | Requested seconds/process | Processes/role | Actual execution start UTC | Actual execution end UTC |
| --- | --- | --- | --- | --- | --- | --- |
| grpc-unary | 16 | 4 | 20 | 3 | 2026-11-21T07:53:59.184458+00:00 | 2026-11-21T07:59:42.876353+00:00 |
| grpc-streams | 16 | 4 | 20 | 3 | 2026-11-21T07:59:46.220509+00:00 | 2026-11-21T08:05:47.591021+00:00 |

Each profile records 19 finite owner commands: prepare/run for nine cells plus comparison extraction. All 38 command summaries report exit zero and retirement. All 18 workload processes are eligible and pass the original service standard. Warmup, recovery and idle observation remain outside the measurement interval. Unary mixes 64 B and 64 KiB calls; the streaming profile mixes server, client and duplex streams using 32 configured 4 KiB messages.

## Before/after means, p99 and direct Rust gaps

Latencies are milliseconds. Percentages and mean decisions are retained from the original reader.

| Profile | Case | Before mean | After mean | Direct mean | B→A mean % | Original mean decision | Before p99 | After p99 | Direct p99 | After−direct mean % |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| grpc-unary | unary 64 B | 5.568694 | 7.255127 | 2.026938 | 30.284167 | within_band | 32.136038 | 40.409345 | 4.823471 | 257.935331 |
| grpc-unary | unary 64 KiB | 5.710156 | 8.058588 | 2.666082 | 41.127290 | within_band | 32.611289 | 42.682104 | 6.455553 | 202.263285 |
| grpc-streams | server stream · 32 × 4 KiB | 43.159840 | 51.431850 | 2.718831 | 19.165987 | regression | 190.506705 | 221.094788 | 5.555705 | 1791.689676 |
| grpc-streams | client stream · 32 × 4 KiB | 23.288990 | 25.427680 | 3.170508 | 9.183266 | inconclusive | 113.104874 | 105.626725 | 17.337695 | 702.006427 |
| grpc-streams | duplex stream · 32 × 4 KiB | 60.975104 | 70.648081 | 3.180722 | 15.863814 | inconclusive | 187.316054 | 234.482824 | 8.361555 | 2121.133306 |

## Full aggregate latency and rate values

JSON retains each process value, original counts and outcomes, payload totals, time windows, result hash and basename/hash records for the source files already bound by that result.

| Profile | Case | Role | Mean ms | p50 ms | p95 ms | p99 ms | Successful calls/s | Request messages/s | Response messages/s | Errors, three-process total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| grpc-unary | unary 64 B | before | 5.568694 | 2.627802 | 22.661671 | 32.136038 | 8.047430 | 8.047430 | 8.047430 | 0 |
| grpc-unary | unary 64 B | after | 7.255127 | 2.675007 | 27.771600 | 40.409345 | 8.048719 | 8.048719 | 8.048719 | 0 |
| grpc-unary | unary 64 B | direct | 2.026938 | 1.933324 | 2.962730 | 4.823471 | 8.049089 | 8.049089 | 8.049089 | 0 |
| grpc-unary | unary 64 KiB | before | 5.710156 | 3.144494 | 22.413408 | 32.611289 | 7.997754 | 7.997754 | 7.997754 | 0 |
| grpc-unary | unary 64 KiB | after | 8.058588 | 3.274649 | 31.723292 | 42.682104 | 7.999036 | 7.999036 | 7.999036 | 0 |
| grpc-unary | unary 64 KiB | direct | 2.666082 | 2.398971 | 3.952542 | 6.455553 | 7.999403 | 7.999403 | 7.999403 | 0 |
| grpc-streams | server stream · 32 × 4 KiB | before | 43.159840 | 32.297391 | 100.454356 | 190.506705 | 5.355316 | 5.355316 | 171.370124 | 0 |
| grpc-streams | server stream · 32 × 4 KiB | after | 51.431850 | 38.205121 | 155.612185 | 221.094788 | 5.356741 | 5.356741 | 171.415723 | 0 |
| grpc-streams | server stream · 32 × 4 KiB | direct | 2.718831 | 2.496410 | 3.960014 | 5.555705 | 5.365577 | 5.365577 | 171.698460 | 0 |
| grpc-streams | client stream · 32 × 4 KiB | before | 23.288990 | 17.088580 | 67.854910 | 113.104874 | 5.305730 | 169.783364 | 5.305730 | 0 |
| grpc-streams | client stream · 32 × 4 KiB | after | 25.427680 | 16.958142 | 79.481921 | 105.626725 | 5.307142 | 169.828540 | 5.307142 | 0 |
| grpc-streams | client stream · 32 × 4 KiB | direct | 3.170508 | 2.644337 | 4.964728 | 17.337695 | 5.315896 | 170.108659 | 5.315896 | 0 |
| grpc-streams | duplex stream · 32 × 4 KiB | before | 60.975104 | 52.211270 | 141.180611 | 187.316054 | 5.355316 | 171.370124 | 171.370124 | 0 |
| grpc-streams | duplex stream · 32 × 4 KiB | after | 70.648081 | 61.517377 | 175.097571 | 234.482824 | 5.356741 | 171.415723 | 171.415723 | 0 |
| grpc-streams | duplex stream · 32 × 4 KiB | direct | 3.180722 | 2.889680 | 5.252038 | 8.361555 | 5.365577 | 171.698460 | 171.698460 | 0 |

## Whole-profile server resources

RSS max is max-of-process-peaks; RSS mean is the original mean-of-process-peaks. CPU/allocation changes have no additional significance test and are not assigned to individual RPC modes.

| Profile | Role | Mean CPU seconds | Mean CPU % of one core | RSS max MiB | RSS mean MiB | Mean observed allocation MiB/s |
| --- | --- | --- | --- | --- | --- | --- |
| grpc-unary | before | 0.620000 | 3.251316 | 60.140625 | 59.759115 | 17.289902 |
| grpc-unary | after | 0.646667 | 3.389113 | 55.828125 | 52.809896 | 17.303952 |
| grpc-unary | direct | 0.110000 | 0.576769 | 13.246094 | 13.196615 | N/A |
| grpc-streams | before | 2.503333 | 13.123557 | 54.578125 | 49.222656 | 352.230419 |
| grpc-streams | after | 2.746667 | 14.394039 | 103.058594 | 63.877604 | 351.615132 |
| grpc-streams | direct | 0.186667 | 0.978737 | 13.109375 | 13.084635 | N/A |

| Profile | Before → after allocation MiB/s | Allocation-rate change % | CPU-seconds change % | Mean-of-peak-RSS change % |
| --- | --- | --- | --- | --- |
| grpc-unary | 17.289902 → 17.303952 | 0.081264 | 4.301075 | -11.628718 |
| grpc-streams | 352.230419 → 351.615132 | -0.174683 | 9.720373 | 29.772769 |

## Calls, messages, payload and protocol observations

Totals below are per role across three process runs. Every before/after/direct value is displayed; JSON also retains encoded-byte totals and all per-process integer counts.

| Profile | Case | Calls B/A/direct | Request messages B/A/direct | Response messages B/A/direct | Request payload bytes B/A/direct | Response payload bytes B/A/direct |
| --- | --- | --- | --- | --- | --- | --- |
| grpc-unary | unary 64 B | 486 / 486 / 486 | 486 / 486 / 486 | 486 / 486 / 486 | 31104 / 31104 / 31104 | 31104 / 31104 / 31104 |
| grpc-unary | unary 64 KiB | 483 / 483 / 483 | 483 / 483 / 483 | 483 / 483 / 483 | 31653888 / 31653888 / 31653888 | 31653888 / 31653888 / 31653888 |
| grpc-streams | server stream · 32 × 4 KiB | 324 / 324 / 324 | 324 / 324 / 324 | 10368 / 10368 / 10368 | 1327104 / 1327104 / 1327104 | 42467328 / 42467328 / 42467328 |
| grpc-streams | client stream · 32 × 4 KiB | 321 / 321 / 321 | 10272 / 10272 / 10272 | 321 / 321 / 321 | 42074112 / 42074112 / 42074112 | 0 / 0 / 0 |
| grpc-streams | duplex stream · 32 × 4 KiB | 324 / 324 / 324 | 10368 / 10368 / 10368 | 10368 / 10368 / 10368 | 42467328 / 42467328 / 42467328 | 42467328 / 42467328 / 42467328 |

The original per-process wire-status maps contain `GrpcOK` counts matching successful calls. Original client/controller outcomes are `ok`, and correctness-failure counts are zero. Separate per-request protobuf, content-hash or trailer-verification flags are not present in these comparison documents and are not invented. Neither profile contains an expected-probe row; all recorded intentional deadline/cancellation counts are zero. Those zeros do not independently validate deadline behavior, cancellation or post-cancellation release. Earlier B18 functional evidence stays a separate acceptance scope.

## Sampled native gauges and idle return

Native payload values are integer bytes in repetition order. Maxima are sampled process observations, not transfer totals or exact high-water marks. Active/queued/retiring after-idle values are the recorded three counters for each repetition.

| Profile | Role | Native payload sampled maxima | Native payload after idle | Active / queued / retiring after idle |
| --- | --- | --- | --- | --- |
| grpc-unary | before | [3656783, 368320, 3657807] | [0, 0, 0] | [[0, 0, 0], [0, 0, 0], [0, 0, 0]] |
| grpc-unary | after | [0, 2239882, 2239950] | [0, 0, 0] | [[0, 0, 0], [0, 0, 0], [0, 0, 0]] |
| grpc-streams | before | [7493726, 6445145, 6445145] | [0, 0, 0] | [[0, 0, 0], [0, 0, 0], [0, 0, 0]] |
| grpc-streams | after | [6578974, 7770275, 5530393] | [0, 0, 0] | [[0, 0, 0], [0, 0, 0], [0, 0, 0]] |

Direct Rust byte owners, retained native bytes, pending requests and connection observations are retained separately in JSON, including actual idle values. Positive available-permit counters are capacities, not outstanding owners. One-Hz sampling can miss peaks; these observations do not alone prove a cleanup root cause or exact retained-byte cost.

## Interpretation and unresolved work

The server-stream regression is an original process-mean decision and remains an adverse result. Client and duplex process means also rise, but their original decisions remain inconclusive. Unary means and mean-process p99 values rise despite the original wide noise bands; the within-band decisions are preserved rather than relabeled. All five after means remain above direct Rust, with arithmetic gaps retained explicitly.

Observed allocation is nearly unchanged for these mixed gRPC profiles, unlike the separate HTTP allocation observations. Streaming CPU and mean-of-peak RSS rise; unary mean-of-peak RSS falls. Resource and p99 changes are descriptive. This interim report supports no general gRPC performance-win claim, no attribution to one patch, and no overall retain/revert decision. The task owner must consider the original regression, remaining profiles, resource limits and outstanding high-load/long-duration checks.

## Binary identities

| Role | Actual server executable filename and SHA-256 | Actual loaded NativeWeave native library SHA-256 |
| --- | --- | --- |
| before | `Perf01.ProtocolServer`: `0ac4867e2cfd626bdfcd453801c8b2646d9e4c20f1191c496fb5837252cf9462` | `libnativeweave_server.so`: `63c4950fceab5fe52017b5457b04759201de5a261d8087939cb177a20a5b88e2` |
| after | `Perf01.ProtocolServer`: `4f2715587cbf3bd7be05bdd4419fc2be73fe7dfc20fba8a66186b5a2753397f9` | `libnativeweave_server.so`: `8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0` |
| direct | `perf01-direct-protocols`: `5953ed7a9823c33965892ac6c9acb2c2712a29f8924c960e9e8d791de3fb020b` | N/A: direct Rust executable |

Package filenames/hashes, build-manifest hashes, dependency-lock identities and the common actual client hash are retained in JSON. No binary, package, raw outcome file or payload was opened or rehashed while preparing this projection.

## Input receipts and public boundary

| Profile | Filename | Recorded comparison SHA-256 |
| --- | --- | --- |
| grpc-unary | `comparison.json` | `c544ae3300f5d1cf0f98753f499efe778c1143383c85c9d1d9555e70e7eaedc7` |
| grpc-streams | `comparison.json` | `b30a662f0726a8c9f9222744dcc44f3c6e12acb034c3696ad6bb041a64ca3405` |

`comparison-grpc-001.sources.json` binds the public JSON and Markdown, checked small execution-metadata hashes, original comparison/noise identities and guide source. Only explicitly selected numeric/enum fields and filenames with hashes are published. Operational paths/maps, PIDs, environment values, addresses and TLS certificate/key material are excluded. Original bound evidence is not rewritten.

Authorship used bounded completed-metadata and guide reads on CPU 8. No project-code import, build, workload, raw scan, payload hashing, archive creation, new noise test or remote write occurred. No capacity or 30-minute credit is granted.
