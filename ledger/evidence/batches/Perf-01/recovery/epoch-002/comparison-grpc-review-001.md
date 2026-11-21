# Perf-01 — independent review of the interim gRPC projection

**Decision: accepted presentation only; no blocking finding.** The public Markdown and JSON accurately preserve the two completed gRPC comparisons, including the adverse server-stream result. This review does not attribute that result to a particular patch or make an overall retain/revert decision. It grants no new measurement, capacity, protocol-semantic or 30-minute acceptance.

## Exact reviewed files

| File | SHA-256 |
|---|---|
| `comparison-grpc-001.md` | `9233961eb142305b570b34e66cc0bb03a60dc5d32c1bdb3a3cb7fc6d28977c60` |
| `comparison-grpc-001.json` | `0ac8f673eb6204331ed20168902e15a6dd84ac55994d201250b3452ee711016e` |
| `comparison-grpc-001.sources.json` | `aa3c9ac156c6e0c903a513e65d0d2b132138afe249c22df57281e5789cc2ce74` |

The reviewer checked the public file hashes and the actual small completed execution/comparison JSON hashes against their recorded identities. The selected `protocols-grpc.md` hash also matches. Input comparison hashes are `c544ae3300f5d1cf0f98753f499efe778c1143383c85c9d1d9555e70e7eaedc7` (unary) and `b30a662f0726a8c9f9222744dcc44f3c6e12acb034c3696ad6bb041a64ca3405` (streams). No raw request/outcome/resource series, payload, package or binary was read or hashed.

## Numerical and noise checks

All 3,717 retained-field comparisons and 360 arithmetic checks matched the completed source metadata. This covered 18 workload processes, 45 process-case observations, five aggregate cases and 38 finite owner command summaries. The processes are eligible and report the original service standard met; all 38 command summaries report exit zero and retirement.

| Case | Before mean ms | After mean ms | Direct mean ms | Original B→A mean % | Original decision |
|---|---:|---:|---:|---:|---|
| `grpc-unary|http2-tls|64|1` | 5.568694 | 7.255127 | 2.026938 | 30.284167 | within_band |
| `grpc-unary|http2-tls|65536|1` | 5.710156 | 8.058588 | 2.666082 | 41.127290 | within_band |
| `grpc-client|http2-tls|4096|32` | 23.288990 | 25.427680 | 3.170508 | 9.183266 | inconclusive |
| `grpc-duplex|http2-tls|4096|32` | 60.975104 | 70.648081 | 3.180722 | 15.863814 | inconclusive |
| `grpc-server|http2-tls|4096|32` | 43.159840 | 51.431850 | 2.718831 | 19.165987 | regression |

The server-stream original independent-process interval is +4.354283 to +12.005806 ms, with a 4.320883 ms noise band. The original `regression` decision is correctly retained. Unary remains `within_band`; client-stream and duplex remain `inconclusive`. No significance is inferred for p99/resources, and no direct-Rust noise test is fabricated. All after/direct arithmetic gaps remain visible.

P99 values are means of process p99 values, not pooled percentiles. Original per-process integer call/message/payload counts, encoded bytes, client/controller outcomes and literal `GrpcOK` maps match. Whole-profile CPU, GC, allocation and resource samples are not attributed to individual RPC modes. RSS uses maximum-of-process-peaks for the headline and preserves the original mean peaks separately. Null GC values and zero-denominator percentages are preserved. Sampled native and idle gauges also match.

## Semantic and privacy limits

All recorded unexpected errors and correctness-failure counts are zero. Every `GrpcOK` map matches the corresponding successful-call count. Neither profile has an expected-probe row, and all intentional deadline/cancellation counts are zero. The report correctly says these facts do not independently validate deadline or cancellation behavior. Separate per-request protobuf, content-hash and trailer-verification flags are absent from these comparison documents and are not invented. Configured concurrency is four; actual simultaneous HTTP/2 stream count is unavailable.

The selected guide documents identity-only gRPC payload compression. Per-request negotiation flags are absent; encoded protobuf bytes are not TLS wire bytes, and the report claims no protocol compression benefit. Standalone codec results stay separate.

The explicit public field selection excludes operational paths/maps, PIDs, environment values, addresses and TLS certificate/key material. Result/source provenance remains filename plus hash. The projection preserves the recorded after-idle values without treating them as a cleanup root cause or a cancellation-release test.

All work used bounded completed-metadata/source reads and review-file writes on CPU 8. No target import, restore, build, workload, raw/binary scan or hashing, timing lock, new noise algorithm, archive or remote write occurred. The SQLite C16 failure remains separate and unaccepted; outstanding capacity and long runs are not credited.
