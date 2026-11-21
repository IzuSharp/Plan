# Perf-01 recovery-002: actual layered profile comparison

This report compares the completed diagnostic profiles of baseline `ea5fa528035d025bd7a28698ee7c71194432236c` with selected final `2f40348c3db80a4fbee7a99e721b374a597b16df`, using common driver `2e3995df8d86583ee9443348276ca8d918056bfc`. Each role attempted 13 profiles: 12 completed and the PostgreSQL business-cycle profile was invalid because the generator reached its in-flight capacity. The 26 profile invocations contain 44 owned finite-command receipts: 42 exited 0 and the two invalid cycle producers exited 1. All 44 retired with no live owned processes or owner children. In-process readers are not counted as separate owned commands.

**These are layered diagnostics, with zero formal performance or long-test credit.** Except for three independent Inspect processes per role, each profile has one process per role. Values and descriptive differences below do not establish significance, a stable throughput limit, or an end-to-end speedup. The separately frozen formal comparisons and ten long segments remain separate evidence.

## Findings

- Repeated public `EngineDescriptor.Inspect(null)` calls allocated **2,624 → 0 calling-thread bytes/call** in all three processes. First-use work remains and is reported separately. This is metadata lookup, not a codec operation or a general native-call benchmark.
- Typed full-page materialization allocated about **12.3% fewer managed bytes/page** in both databases. The observed one-process wall cost increased for both providers; this profile does not establish a latency improvement.
- HTTP JSON whole-server approximate allocation fell **32.452 → 0.892 MiB/s (−97.25%)**. Both protocol-specific mean and p99 values fell in this run. HTTP tiny did not show a similar allocation reduction.
- gRPC allocation rates were essentially unchanged: server-stream and duplex remained about **513–520 MiB/s** in the observed managed snapshot brackets. Latency and RSS moved in both directions. These profiles leave gRPC allocation as an unresolved hotspot; they do not establish a gRPC performance gain.
- The PostgreSQL business-cycle load was invalid in both versions. Its undispatched work, successful durable operations and completed teardown are preserved in the failure diagnostic below.

## Shared metadata and database paths

### Inspect: three independent processes

Each process completed 10,000 warmup calls and ten measured batches of 100,000 calls. The table sums only that process's measured batch counters. Process ordinal pairs are descriptive; the runs were not an interleaved significance experiment. CPU observes a wider bracket than the calling-thread allocation and wall counters. Tiny after CPU intervals are resolution-sensitive.

| Process | Wall ns/call before → after | Wall change | Allocated B/call | Process CPU ms | Gen0 collections |
| --- | --- | --- | --- | --- | --- |
| 0 | 596.492 → 1.532 | -99.74% | 2,624 → 0 | 596.456 → 1.534 | 1255 → 0 |
| 1 | 622.580 → 1.474 | -99.76% | 2,624 → 0 | 622.555 → 1.475 | 1255 → 0 |
| 2 | 586.306 → 1.367 | -99.77% | 2,624 → 0 | 586.287 → 1.369 | 1255 → 0 |

Gen1 and Gen2 counts were zero in all measured Inspect loops. First-use allocation was 21,752 → 21,720 B; first-use wall times, in process order, were 447.613 → 454.623 µs, 724.320 → 1,128.056 µs, 485.189 → 452.020 µs. No first-use latency improvement is claimed.

### Full typed pages

Each provider completed 20 warmup pages and 1,000 measured pages, each containing 100 exactly verified rows. Timing includes the public query, DTO/list materialization, stream cleanup, exact row validation and loop/runtime work. The committed seed was checked through a new logical session; a one-connection pool may reuse the physical connection, so this check is not the independent application durability oracle.

| Provider | Managed B/page | Allocation change | Wall ms/page | Wall change | Process CPU ms | GC Gen0/1/2 |
| --- | --- | --- | --- | --- | --- | --- |
| SQLite | 72,782.256 → 63,861.488 | -12.26% | 6.400 → 8.250 | +28.92% | 1,994.406 → 2,005.233 | [36, 0, 0] → [31, 0, 0] |
| PostgreSQL | 72,778.056 → 63,857.656 | -12.26% | 2.933 → 5.467 | +86.42% | 716.824 → 980.657 | [35, 0, 0] → [31, 0, 0] |

All seed, transaction/session/source release and table-drop flags passed. The native database library hashes were unchanged between roles. Lower allocation did not translate to lower wall time in these individual profiles. RSS, exact pool wait, SQL-only duration and native allocation bytes were not measured by this probe.

### Instrumented retirement

Each provider completed 1,000 measured scalar calls after 20 warmup calls and recorded 4,000 native-operation observations in both roles. These are existing internal test-boundary observations, not a count of every FFI call. The mean below divides the sum of public-call durations by 1,000; the producer does not report an outer elapsed window. Allocation and CPU include observer overhead.

| Provider | Instrumented mean ms/call | Mean change | Managed B/call incl. observer | Allocation change | Process CPU ms |
| --- | --- | --- | --- | --- | --- |
| SQLite | 2.180 → 5.492 | +151.97% | 17,542.080 → 17,359.472 | -1.04% | 418.552 → 696.723 |
| PostgreSQL | 2.327 → 2.870 | +23.32% | 17,526.648 → 17,348.352 | -1.02% | 449.194 → 537.823 |

Both roles reported source release. GC counts were `[8, 0, 0]` in every retirement process. Pending-retirement count, native allocation and exact wakeup/scheduling attribution remain unavailable. These measurements show no retirement latency improvement.

## PostgreSQL application and observer

The frozen diagnostic request was HTTP/1.1, 180 arrivals/s, concurrency 16, 20 seconds, with PostgreSQL statement-duration logging and a requested 100 ms backend-state sampler. The original application profiler shares CPUs 2–3 across generator, service, database and wait observer; this differs from the formally split generator/service timing configuration.

### Page application: valid diagnostic load

| Metric | Before | After | Descriptive change |
| --- | --- | --- | --- |
| Offered / dispatched / successful | 3601 / 3601 / 3601 | 3601 / 3601 / 3601 | 0 |
| Successful calls/s | 179.977 | 179.690 | -0.16% |
| Arrival p50 / p95 / p99 ms | 9.252 / 24.631 / 35.085 | 9.286 / 24.177 / 37.902 | p99 +8.03% |
| App CPU seconds / percent of one core | 8.980 / 44.936 | 8.180 / 40.896 | Sampled CPU endpoints |
| Sampled peak app RSS MiB | 41.566 | 42.613 | Sampled peak |
| Peak file descriptors / sockets | 48 / 33 | 48 / 33 | No observed change |

Both application durable oracles passed and both reported database/consumer resources released and server disposed. There were no provider exceptions or business retries. The observed p99 increased despite lower sampled CPU; one diagnostic process per role is insufficient for a stable latency conclusion.

### Failure diagnostic: PostgreSQL business cycle

Both runs have `valid: false`, `invalid_reasons: ["generator saturation: in-flight capacity"]`. Their owned producer exited 1 after a completed supervised run and retired with no live owned processes. The failed runs are not replacement noise samples and are excluded from performance deltas.

| Role | Offered | Dispatched / successful | Not dispatched (rejected) | Dispatch span s | Invalid-load p99 ms | Oracle operations | Owner exit / retired |
| --- | --- | --- | --- | --- | --- | --- | --- |
| before | 3601 | 3119 / 3119 | 482 | 20.000 | 4,371.603 | 3263 | 1 / true |
| after | 3601 | 3025 / 3025 | 576 | 19.999 | 4,561.546 | 3169 | 1 / true |

The generator rejected 482 before and 576 after scheduled operations without dispatching them. All dispatched operations succeeded, with zero observed provider exceptions and zero business retries. Independent durability checks passed: before had 3,263 items/operations/outbox entries, after had 3,169. These whole-fixture oracle totals include work outside the measured dispatch window and must not replace the 3,119 / 3,025 measured successful-call counts. Both runs reported consumer/database release and server `Disposed`.

All four PostgreSQL observer summaries reported wait sampling and load statement logging present, zero unparsed duration lines, and no missing observer files. The JSON preserves producer statement groups and backend wait samples. Server elapsed durations include waits; Parse/Bind/Execute are distinct protocol steps, not extra business operations. Concurrent durations and sampled states **cannot be subtracted from application wall time** to estimate C#/Rust overhead. Sample counts cannot be multiplied by the requested interval to obtain exact wait duration.

## HTTP and gRPC over real TLS sockets

HTTP tiny/JSON requested 32 calls/s at concurrency 4, split between HTTP/1.1 TLS and HTTP/2 TLS. Each gRPC mode requested 16 calls/s at concurrency 4 over independent HTTP/2 TLS. All requested 20-second profiles retain their actual original measurement-window denominators. Unary used one 64-byte payload; streaming used 32 messages of 4,096 payload bytes. gRPC remained identity-compressed.

All protocol rows below are one process per role. The p99 values are the original reader's within-process arrival percentiles, not pooled or mean-process percentiles. Both roles validated all 645 HTTP calls per HTTP profile (323 H1, 322 H2) and all 323 calls per gRPC profile with zero unexpected errors.

| Scenario / protocol | Success/s before → after | Arrival mean ms | Arrival p99 ms | p99 change | Errors before / after |
| --- | --- | --- | --- | --- | --- |
| http-tiny / http1-tls | 16.048 → 16.048 | 2.033 → 2.186 | 11.289 → 9.741 | -13.71% | 0 / 0 |
| http-tiny / http2-tls | 15.998 → 15.998 | 1.875 → 2.371 | 4.977 → 22.959 | +361.30% | 0 / 0 |
| http-json / http1-tls | 16.048 → 16.048 | 2.512 → 1.948 | 8.709 → 6.924 | -20.49% | 0 / 0 |
| http-json / http2-tls | 15.998 → 15.998 | 2.462 → 1.877 | 7.860 → 5.609 | -28.64% | 0 / 0 |
| grpc-unary / http2-tls | 16.047 → 16.048 | 8.041 → 11.382 | 41.885 → 40.676 | -2.89% | 0 / 0 |
| grpc-server / http2-tls | 16.025 → 15.978 | 37.722 → 37.899 | 124.071 → 143.562 | +15.71% | 0 / 0 |
| grpc-client / http2-tls | 16.026 → 16.012 | 36.754 → 33.612 | 200.103 → 168.488 | -15.80% | 0 / 0 |
| grpc-duplex / http2-tls | 16.010 → 16.043 | 62.909 → 59.851 | 204.123 → 226.357 | +10.89% | 0 / 0 |

HTTP JSON improved in this diagnostic while HTTP tiny was mixed. gRPC client-stream mean/p99 fell, server-stream p99 rose, duplex mean fell while p99 rose, and unary mean rose despite a slightly lower p99. These are descriptive observations, not statistically established gains or regressions.

### Whole-profile server resources

CPU, RSS and GC cannot be attributed to an individual HTTP protocol or message. CPU percentages are percentages of one core. RSS is a sampled peak. Allocation rate uses the existing reader's approximate partial measurement snapshot bracket (`GC.GetTotalAllocatedBytes(false)`), not exact bytes/call. The JSON retains the bracket length, sample count, allocation delta, other process resources, GC counts, queue/owner gauges and post-idle samples.

| Profile | Server CPU % | Peak RSS MiB | Approx. allocation MiB/s | Allocation-rate change | GC Gen0/1/2 |
| --- | --- | --- | --- | --- | --- |
| http-tiny | 3.454 → 3.664 | 65.824 → 65.867 | 0.404 → 0.406 | +0.44% | 4/1/0 → 4/1/0 |
| http-json | 4.611 → 3.145 | 56.758 → 65.742 | 32.452 → 0.892 | -97.25% | 71/69/68 → 9/1/0 |
| grpc-unary | 3.197 → 3.510 | 58.129 → 48.246 | 16.329 → 16.331 | +0.01% | 34/33/33 → 40/39/38 |
| grpc-server | 15.714 → 17.033 | 47.039 → 100.508 | 514.175 → 513.399 | -0.15% | 965/944/943 → 1000/977/976 |
| grpc-client | 6.717 → 6.212 | 68.402 → 68.391 | 21.076 → 21.075 | -0.00% | 86/33/33 → 91/38/38 |
| grpc-duplex | 19.069 → 20.463 | 77.742 → 42.840 | 518.037 → 519.866 | +0.35% | 930/855/855 → 1079/1000/1000 |

Every recorded after-idle gauge was zero in all 12 protocol profiles: active/queued/retiring requests, payload owners, diagnostic queues and observed failure/rejection counters. This reports the observed idle samples; it does not replace the required 30-minute resource trend and drain tests. Native allocated bytes and transient ownership peaks are not established by these counters.

### Successful gRPC message and byte accounting

Both roles had the same successful counts and payload totals below. Protobuf-encoded byte totals are retained in JSON and exclude the gRPC envelope, HTTP/2 framing and TLS overhead. No online compression benefit is claimed.

| Mode | Calls per role | Request / response messages | Request / response payload B | Request / response protobuf B |
| --- | --- | --- | --- | --- |
| grpc-unary | 323 | 323 / 323 | 20672 / 20672 | 21964 / 21964 |
| grpc-server | 323 | 323 / 10336 | 1323008 / 42336256 | 1324623 / 42407962 |
| grpc-client | 323 | 10336 / 323 | 42336256 / 0 | 42407962 / 23256 |
| grpc-duplex | 323 | 10336 / 10336 | 42336256 / 42336256 | 42407962 / 42407962 |

These isolated mode profiles contain ordinary successful calls; they do not add deadline/cancellation acceptance coverage. That coverage remains in the functional and formal mixed-profile suites. Direct Rust and pure C# controls were not run in this layered-profile queue, so their gaps are N/A here. Codec computation/throughput was not measured by the Inspect probe.

## Source, build and actual loaded identities

Before uses the immutable initial-main admission. After uses `final-binding-004.json` for the separately built selected final. The common before-built protocol client was retained. The report copies actual loaded identities from completed probe/observer receipts and does not re-hash payload binaries during formal timing. The JSON preserves reported executable/native/package identities, the other probes' build-manifest hashes, and exact small-result file hashes.

| Actual loaded library | Before SHA-256 | After SHA-256 |
| --- | --- | --- |
| Syncproof engine | 225891ba2e8ab97381bfb7b35814aea00a16135da01b9afcd6de8e97a58a6d15 | 225891ba2e8ab97381bfb7b35814aea00a16135da01b9afcd6de8e97a58a6d15 |
| libnw_database_sqlite.so | 63f01de214b727a6b7c976902e7f508f568ac08629a64c0332d67da028295346 | 63f01de214b727a6b7c976902e7f508f568ac08629a64c0332d67da028295346 |
| libnw_database_postgresql.so | 9ec17b5fe5fc675b35edef503d3eacf1597aa814879236bf5e97621c70fd3f65 | 9ec17b5fe5fc675b35edef503d3eacf1597aa814879236bf5e97621c70fd3f65 |
| libnativeweave_server.so | 63c4950fceab5fe52017b5457b04759201de5a261d8087939cb177a20a5b88e2 | 8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0 |

| Control source / binding | SHA-256 |
| --- | --- |
| before_admission_sha256 | 56725c0a0167e04bb021210d879b6616f85523705bc19bd04bc11e2cbb42d380 |
| final_binding_sha256 | 8f8616f2932dd1c033309e177efa63429829f9ffa2b728a182406d943efdfa8d |
| final_profile_queue_sha256 | 9d2289f8557fd638c42e7f830141cfc0e3b39aae83e0f4c978c1e53276488e16 |
| measurement_source_index_sha256 | 6b1d1e8ec6ee80271fdbbeb1c6d13909b92ca13c7a28cbc4fd4085f98f6a4c2c |
| profiling_plan_sha256 | 45c1a8faa86fdfa17fe9c6912a2e3cb523db42d4db241a1dd6e67c9f9817c37f |
| profiling_source_index_sha256 | 6e0a16a6b4f84afc811b559dcdb1d62bfb32032c59bd3bd6aa030a0e778a4b42 |

## Actual diagnostic invocation ledger

All timestamps below are UTC on 2026-11-21. These are outer invocation boundaries, including preparation/warmup/readers/cleanup where applicable; they are not uninterrupted load durations. Each entry is bound to its completed or failed `execution.json` hash. The JSON also binds each owned command receipt and small numeric result.

| Role | Profile | Status | Start UTC | End UTC | Execution SHA-256 |
| --- | --- | --- | --- | --- | --- |
| before | inspect | completed | 05:15:36.344021+00:00 | 05:16:04.930861+00:00 | bfdd60225591425b78839eba74201c85fcd88a7f690f6750821cfe361945f277 |
| before | page-sqlite | completed | 05:16:49.836032+00:00 | 05:16:59.350912+00:00 | 76e8ad158546d0699cc7f85102036d3e1617a28766543b031ea1780a9c6424ee |
| before | page-postgresql | completed | 05:19:35.161949+00:00 | 05:19:41.734188+00:00 | a68b2c704770273c311b246460976219f839ce65889932c918f40eafe869b812 |
| before | retirement-sqlite | completed | 05:21:50.726311+00:00 | 05:21:55.037198+00:00 | 49c19db417f63faa11115c211186e12bd6734f8038fe81f8466747713ac358c3 |
| before | retirement-postgresql | completed | 05:23:34.922737+00:00 | 05:23:40.585333+00:00 | 801f61eba8dcc0a0ff3f5c1247768ca74dcd943425d108d7470f114347cc6f74 |
| before | postgresql-cycle | failed | 05:24:28.796932+00:00 | 05:25:01.994345+00:00 | dd0369f9f5b2931f4f4d7dc538793470d54856df4507ee60846ce445e421c353 |
| before | postgresql-page | completed | 05:27:38.250240+00:00 | 05:28:08.077654+00:00 | c6ddf0ad75875393bc7bcf78ebf42b578e91fb36f757acbc3bb2c26e5274c2b8 |
| before | http-tiny | completed | 05:29:00.687833+00:00 | 05:29:39.414767+00:00 | 1fdb093543dd37c94c60b58ca0e4f846555caf454d699defaab31e66df73ea2f |
| before | http-json | completed | 05:29:41.527848+00:00 | 05:30:20.604206+00:00 | 048c4125eaf173990f5f047d10456307280e2fdee37a553b77128d67bb9f5c97 |
| before | grpc-unary | completed | 05:30:22.775084+00:00 | 05:31:01.733684+00:00 | 50254640820893fec66b7ba548e4c0a994fae1b2a032d1ab1958ac8e3f79ddb7 |
| before | grpc-server | completed | 05:31:03.826588+00:00 | 05:31:44.852251+00:00 | f4f21bf5cd336309b16f1de262cac2fc8f6cc8de97870bd095f5d248bf1822f3 |
| before | grpc-client | completed | 05:31:47.280612+00:00 | 05:32:28.800293+00:00 | 2b37acbd7f47246ee67d1678a418338b9fd5cdd9b6fe312a69470c3397cc0bb0 |
| before | grpc-duplex | completed | 05:32:31.118135+00:00 | 05:33:14.378827+00:00 | 222172c53de0432a5b70d5f69edee99a53e6108675758213419be6ab0291d3f6 |
| after | inspect | completed | 05:33:45.641335+00:00 | 05:34:03.714205+00:00 | 167d2cba31a7ca1d5cff52dc97dce7b825f816daf4fd9bd8a2b02d5b3d69cc16 |
| after | page-sqlite | completed | 05:34:06.297262+00:00 | 05:34:17.070309+00:00 | bcb6ea802660a59e2a0a8f44a0ce634d09380737f2c04ac11465a6613417fb54 |
| after | page-postgresql | completed | 05:34:19.697576+00:00 | 05:34:28.994848+00:00 | 844d83df742fb15c18099909d3327c18452cdb02b66e960c815526451f98bb55 |
| after | retirement-sqlite | completed | 05:34:31.658327+00:00 | 05:34:39.397904+00:00 | c8cd412b1a4768a3c915f7fd1b7e91d1b1004f770533669a7892f8b1c74247c4 |
| after | retirement-postgresql | completed | 05:34:42.191300+00:00 | 05:34:48.689071+00:00 | 3476f09946bbd361e0a531400871b42ec464ce13c9a7ad54dbf748137f4c66fa |
| after | postgresql-cycle | failed | 05:34:51.257978+00:00 | 05:35:24.174187+00:00 | cc6d0f3473f795b1cd91a38085b2db02ea999e008ea8cc7879b3a5cc64be1eb5 |
| after | postgresql-page | completed | 05:41:08.053881+00:00 | 05:41:37.975648+00:00 | 4a7237c4d51bd066429bdc937b321367bee52fc0c0d27523aedb6e68f9cdf909 |
| after | http-tiny | completed | 05:41:40.710610+00:00 | 05:42:19.824350+00:00 | fdba8d0f723e3166ff9b0fd14bef3436143899c0340a005ac2f008b3cffed8b8 |
| after | http-json | completed | 05:42:22.344532+00:00 | 05:43:01.146886+00:00 | 92031495bca0398ddf4228f57adbc445b4580db037cd5adfb63fbde7e071ee53 |
| after | grpc-unary | completed | 05:43:03.895474+00:00 | 05:43:43.477702+00:00 | 92c2dc1d9e2fedfc1c01262fd8ce71fbaec46dc72a319be947e8cdc62a326981 |
| after | grpc-server | completed | 05:43:46.158817+00:00 | 05:44:28.027969+00:00 | 5efb109f97f81a78f3f7cf1b65fa1230b3cd9e353d321326ce405455989c16cf |
| after | grpc-client | completed | 05:44:30.728644+00:00 | 05:45:11.616957+00:00 | 491e66e414a6c5fa836e678a59ead1e36b485e6527e6f0b043ce986f5b1da511 |
| after | grpc-duplex | completed | 05:45:14.175166+00:00 | 05:45:57.321357+00:00 | 46980b51c0769a9919dcf66bdf55b7de00d67dc939bb822ed4fb1e7f2d76be38 |

## Projection and interpretation limits

- [Numeric summaries and exact evidence identities](layered-profile-comparison-004.json), SHA-256 `ec4064caf2bfbfa0f903c9b9a8c9a9ab79fadbb22649046121bfe333cc1ddea6`.
- [Field names and denominator specification](layered-profile-summary-fields.md); machine-readable mapping SHA-256 `e13d9caae5350752be6a31dc3f533b8b7ac909057d342ed4da5a73698b852ac0`.
- Only completed, bounded summary/receipt JSON was read, on CPU 8. No active formal/noise raw was read, no binary payload was hashed, and no product module was imported or workload/build launched by this projection.
- The public projection contains numeric samples and filename-plus-hash provenance. Operational path maps, command argv, proxy settings, raw process maps and TLS material remain outside this report.
- Failed loads remain failed. Missing metrics remain N/A. Percent changes are descriptive arithmetic against before, not significance tests. Resource brackets and operation denominators remain distinct.
- This report grants **0 seconds** of formal timing or long-duration acceptance. It does not decide whether product changes should be retained before equivalent formal workload evidence is available.
