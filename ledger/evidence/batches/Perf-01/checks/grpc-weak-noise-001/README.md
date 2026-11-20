# Perf-01 weak writer: fresh retained-ON noise freeze

**All six actual retained-ON processes passed the existing validity, service-standard, correctness, recovery and drain checks.** The collection ran from 2026-11-20T18:18:40.378312+00:00 through 2026-11-20T18:22:28.204923+00:00. All 14 owned prepare/run/reader commands exited zero; their process groups and adopted descendants retired without signals or cleanup errors. Both resource-calibration unavailable lists are empty.

This calibration measures retained weak-writer ON, managed source `2e3995df8d86583ee9443348276ca8d918056bfc` and actual native producer `2e3995df8d86583ee9443348276ca8d918056bfc`. The prospective OFF managed source is `963dfbc5a99a45b57d0ffa2c9fb21612d110aa1c`, reusing the explicitly bound actual ON native assets. The original pre-optimization Perf-01 main is `ea5fa528035d025bd7a28698ee7c71194432236c`; it is **not** the `before` role of this diagnostic. Stored reader labels remain `before=ON; after=OFF`. No OFF or direct timing occurs in this six-process calibration.

## Complete freeze and producing identities

The SHA-256 of the **entire original completed noise index** is:

```text
13cdfeaa09f02f0d4b6cb615ecc9d2fddd073b9c378968324392006634edf675
```

This binds the complete private original, including source and process identities. It is not the digest of this projection or either per-profile reader. Publish and read back this exact complete-index identity before starting the fresh interleaved comparison.

| Identity | SHA-256 |
| --- | --- |
| Actual noise owner receipt | `29fa28aad3019fc88078ad58ab5a428ae8ff8a96f45c6c14a6bd56f81915438c` |
| Actual measurement source index | `36314001faf7717ab2d50c5e0429f59610ac406121cb2fe22f610953037a013a` |
| Actual measurement inputs | `0f0de2a50f778d4fe8b85419886569914de71b02f21e89c854682458db5e75ab` |
| Completed measurement-binding-002 owner | `a552b7c4f0742ecac7712a61f72bbcbf31ea0290bd912c7a624d4858e96a937a` |
| Measurement binding | `704eaab1e0fc59bf288ad97958c1df4af767f36a680bb9a0fbe7c5f769b6bdb4` |
| Actual three-producer build owner | `8ce2a50ac65845740443cbe9c68ccd9da95819998e5db5fe8897013ac98ab710` |
| Actual build binding | `483112ed17c3015828657d06c136bdd96acefa0e6813b978230c25ff9d1a18fc` |
| Actual native source-equivalence proof | `3b8af8341b2fece7686ae2d16f6f5984857ffddd1352016b1fe6b23fd26bad36` |
| Actual ON protocol manifest | `4f7dff86d721151c22fa26385150081f72528b43901ad00497b3562cf9176c84` |
| Original unary noise reader | `90fba04fa4731c1021dc77a3ce01bb09267bc11bdb29630f747e18d9cbbcbce3` |
| Original stream noise reader | `aced1359f386089ad715ff51c74643a1a818fede905a6de6b6926f6e4c467225` |

The ON server executable is `98df4925172b006ae1ccc58a5730c7f8362ec7bd9ea65e97fcad3b0e7c30ac59`, the shared independent Native AOT client is `acb1c163cd51e291f58dbe51ae12c04f82c2b51538aa36e446a05890e06aadd0`, and the actual loaded Server library is `28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2`. Actual source/manifest/receipt identities are copied from current controls; no executable or package payload was rehashed for this projection.

## Actual observations and broad tail ranges

Both profiles retain 16 planned arrivals/s, concurrency 4, a 20-second offered-load target and real HTTP/2 + TLS. Unary equally weights 64-byte and 65,536-byte payloads. The stream profile covers server, client and duplex calls with 4,096-byte messages and 32 messages per stream. Warmup, 32-call recovery and idle observation are separate. All values below are copied from saved results/readers.

| Process | Successes / recorded offers | Whole-cell p99 (ns) | Server CPU (one-core %) | Server RSS maximum (bytes) | Server allocation (MiB/s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| grpc-unary/0-ON | 323 / 323 | 105160643 | 6.647894853966177 | 52731904 | 17.330240433098144 |
| grpc-unary/1-ON | 323 / 323 | 54783107 | 5.801789166144462 | 69148672 | 17.285073351008595 |
| grpc-unary/2-ON | 323 / 323 | 77660920 | 5.872727642677931 | 69484544 | 17.309595388240105 |
| grpc-streams/0-ON | 323 / 323 | 151615486 | 13.053679456420722 | 95858688 | 21.19431554710877 |
| grpc-streams/1-ON | 323 / 323 | 233291408 | 12.937951233230933 | 92766208 | 21.996470925614002 |
| grpc-streams/2-ON | 323 / 323 | 266362805 | 17.33029797661157 | 92897280 | 21.851582039497295 |

The current tail spread is broad and is retained without tightening, selected replacement or reuse of the older scratch calibration:

| Ordinary scenario | A21 absolute mean-noise band (ns) | Three observed p99 values (ns) | Frozen p99 range (ns) |
| --- | ---: | --- | ---: |
| grpc-unary\|http2-tls\|64\|1 | 2223374.8271604935 | [105160643, 61845519, 64520926] | 43315124 |
| grpc-unary\|http2-tls\|65536\|1 | 3164733.5652173907 | [109040521, 50943364, 95044266] | 58097157 |
| grpc-client\|http2-tls\|4096\|32 | 11268114.373831779 | [117323743, 152502683, 187187159] | 69863416 |
| grpc-duplex\|http2-tls\|4096\|32 | 9717890.194444448 | [186323635, 233292443, 315080376] | 128756741 |
| grpc-server\|http2-tls\|4096\|32 | 14583418.90740741 | [151615486, 202380659, 232588508] | 80973022 |

[noise.json](noise.json) preserves all six processes, all ordinary scenario count/latency/throughput/message/byte observations, whole-profile resources, all five A21 bands and the complete eleven resource/tail calibration objects. The two unavailable lists remain exactly empty. Resource ranges are descriptive three-process ranges, not confidence intervals. Allocation retains the original sampled `GC.GetTotalAllocatedBytes(false)` bracket, not exact bytes per call or per scenario. CPU/RSS/GC belong to the whole profile; the per-scenario unavailable labels remain explicit.

## Prospective decision scope

The unchanged current policy is `grpc-weak-001-prospective-001`. Its primary observations are **stream-profile RSS and separate fresh sustainable successful business capacity**. Allocation is descriptive; the old scratch unary-allocation primary does not apply. For ordinary p99 and whole-profile CPU/RSS, the future screen uses retained-ON minus OFF mean and maximum against the corresponding fresh ON-only range. The original A21 verdict direction and labels are preserved: an OFF mean-latency improvement is an adverse cost of retaining ON. Correctness, generator validity, absolute p99/RSS limits, payload credits and drain/recovery requirements remain mandatory. CPU/allocation gains cannot compensate for a failed veto. Missing/nonfinite or invalid observations remain unresolved/failed; screen eligibility alone never approves retention.

This freeze establishes no improvement, capacity result, final-matrix result or 30-minute credit. A future capacity observation is still required; the weak-writer retention decision remains pending. Earlier failed attempts and all existing final003 results remain unchanged.

Only `README.md`, `noise.json` and `manifest.json` are the publication allowlist. They contain project synthetic numeric observations and exact source/result/receipt digests, with no private filesystem paths, host process identifiers, argv, environment dump or TLS material. Public files remain available while repository history is retained; complete originals and private identity proof remain in the measurement workspace. No remote full-raw archive is claimed.
