# Perf-01 scratch 004: frozen control-only noise

**All six actual control processes passed the unchanged validity, correctness, recovery, drain and service-standard checks.** The collection ran from 2026-11-20T13:06:07.598634+00:00 through 2026-11-20T13:09:50.261225+00:00. All 14 owned prepare/run/reader commands exited zero; their process groups and adopted descendants retired without signals or cleanup errors. Both required resource-calibration unavailable lists are empty.

This is the corrected control `db95a9fbdd18c208ba8fa3fdb6dabaa2bcc073c0`, using Server SHA-256 `28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2`. It is a diagnostic calibration after the common ownership fixes, not a replacement for the original Perf-01 baseline or a scratch retention decision. The [functional prerequisites](../grpc-functional-gates-004/README.md) retain their own identities.

## Complete freeze identity

The SHA-256 of the **entire original completed noise index** is:

```text
c5afdc5a893b2927150c6db26bb3823a44d21ad43b51df01900e6d8848117de0
```

Original location: `perf01-evidence/diagnostics/grpc-scratch-004/noise/noise-index.json`. This hash identifies the complete private original, including its source and process-identity bindings; it is not the hash of this data projection or either per-profile reader output. Commit and read back this exact identity before any comparison starts.

Measurement-input SHA-256: `17dda4d7989d04591e0ced28ef71d052553746dbace748e21f37ffd1a56bb3e5`. Build-binding SHA-256: `5168b214e1dae056e6eaffc9834b113bc2fdfd5e818f6bc8cce3ba18170fd5be`. The control-only observations use the already published `grpc-scratch-004-prospective-001` policy without changed formulas or thresholds.

## Actual observations

Both profiles retain 16 planned arrivals/s, concurrency 4, a 20-second offered-load target, HTTP/2 + TLS and the same independent Native AOT client. Unary covers equally weighted 64-byte and 65,536-byte payloads. Streams cover server, client and duplex calls with 4,096-byte messages and 32 messages per stream. Warmup, recovery and idle observation remain separate. The following values are copied from actual results and the existing reader:

| Process label | Successes / offered | Whole-cell p99 (ns) | Server RSS maximum (bytes) | Server allocation (MiB/s) |
| --- | ---: | ---: | ---: | ---: |
| grpc-unary/0-before | 323 / 323 | 47750329 | 52912128 | 17.326883865990492 |
| grpc-unary/1-before | 323 / 323 | 41073070 | 52285440 | 17.289915619860516 |
| grpc-unary/2-before | 323 / 323 | 54207860 | 69324800 | 17.299667429682813 |
| grpc-streams/0-before | 323 / 323 | 193836344 | 92262400 | 21.428562250351902 |
| grpc-streams/1-before | 323 / 323 | 207170940 | 90816512 | 21.729253284584452 |
| grpc-streams/2-before | 323 / 323 | 226942451 | 95698944 | 21.753839806364198 |

[noise.json](noise.json) retains all six processes, each ordinary scenario's existing counts/latency/throughput/message/byte observations, sampled server/client resources, exact per-profile A21 bands and the unchanged resource-screen calibration objects. Values are copied rather than recalculated. Actual PID/start identities remain privately bound; the projection records verified distinct-process count and nonoverlap only.

The resource ranges are descriptive ranges from three independent processes, not confidence intervals. Allocation uses the original sampled `GC.GetTotalAllocatedBytes(false)` bracket, so it is not exact bytes per call or per scenario. CPU and RSS observations cover the whole profile. The original A21 mean-latency interpretation and separately frozen resource/tail screens remain distinct.

## Scope and retention

There are no after or direct timing observations in this calibration. No performance improvement, scratch retention, capacity or 30-minute acceptance is inferred. All original failed attempts remain unchanged. The next stage must use the exact complete-index hash above and fresh interleaved processes.

Only `README.md`, `noise.json` and `manifest.json` form this publication allowlist. They contain synthetic numeric observations and source/result/receipt identities, with no host process identifiers, argv, environment dump or TLS material. Public files are retained while repository history is retained; complete originals and private identity proof remain in the measurement workspace. No remote full-raw archive is claimed.
