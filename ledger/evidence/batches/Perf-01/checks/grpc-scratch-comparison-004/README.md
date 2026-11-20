# Perf-01 scratch 004: reject cross-call scratch retention

**Reject the three-file managed scratch candidate under the frozen policy.** All 18 actual processes were valid and met the absolute correctness, recovery, drain and service standards. All 38 owned commands exited zero and retired their groups/adopted descendants without signals or cleanup errors. Collection ran from 2026-11-20T13:22:08.756109+00:00 through 2026-11-20T13:33:11.660166+00:00. The separate prospective tail/resource screens rejected both profiles.

## Exact retention decision

| Profile / failed observation | Candidate minus control mean | Candidate minus control maximum | Frozen A-only range |
| --- | ---: | ---: | ---: |
| grpc-unary / grpc-unary / http2-tls / 64 / 1/arrival_p99_ns | 15294992 | 44842672 | 15979342 |
| grpc-streams / grpc-duplex / http2-tls / 4096 / 32/arrival_p99_ns | 33104443 | 16796486 | 3873278 |
| grpc-streams / server/rss_bytes_maximum | 16259754.666666657 | 16265216 | 4882432 |

Latency values above are nanoseconds; RSS values are bytes. Unary 64-byte p99 fails the maximum-delta condition despite its mean delta fitting the range. Duplex p99 and streams RSS fail both conditions. These are the predeclared descriptive screens, not newly fitted thresholds or claims of statistical confidence.

Allocation improved substantially, using the original approximate whole-profile GC observation:

| Profile | Control allocation mean (MiB/s) | Candidate allocation mean (MiB/s) | Existing reader change (%) |
| --- | ---: | ---: | ---: |
| grpc-unary | 17.298986271239258 | 1.27091238452294 | -92.65325514110663 |
| grpc-streams | 21.647251381166548 | 17.6485490752982 | -18.472101771531527 |

The unary allocation primary screen passed, and both CPU screens passed. The original A21 mean-latency decisions were inconclusive for four scenarios and within-band for duplex; none established a mean-latency improvement. The allocation reduction does not override the independently frozen tail/RSS veto. No failed or slow observation was replaced, averaged away or retried.

## Implementation follow-up

Restore only these three files from corrected control `db95a9fbdd18c208ba8fa3fdb6dabaa2bcc073c0` in a forward commit:

- `src/Protocols.Grpc/CallContext.cs`
- `src/Protocols.Grpc/NativeTransport.cs`
- `src/Protocols.Grpc/Registration.cs`

The expected resulting product tree is `246de1eb9368efbc62f46ce10c4a8a894d646152`. Exact tested/restore file hashes are in [comparison.json](comparison.json). Preserve the native per-value metadata-credit correction, the managed request final-release/admission correction, and their correctness fixtures and documentation. This projection performs no product mutation.

The candidate uses one weak exact-capacity slot per unary/client-streaming method. It acquires the full managed credit before renting; a scoped writer is invalidated before the synchronous native copy's backing is cleared and returned. Concurrent calls never wait for this slot, and losing compare-exchange returns do not retain a strong cache owner. B18 exercised the relevant failure/cancel/credit boundaries in both roles. These lifetime properties do not guarantee lower retained RSS or stable tails; the actual resource tradeoff above is why this candidate is not retained. The measurements do not identify a unique cause for an individual tail excursion.

## Original reader tables

The following tables are copied from the existing readers, with only heading levels adjusted. Their `Interpretation eligible: true` means valid comparable cohorts; it does not override the additional fixed retention screens. Aggregate p99 is the mean of three independent process percentiles, never a pooled percentile. Full vectors and all 18 actual outcomes remain in comparison.json.

## grpc-unary

Interpretation eligible: **true**.

Equal weight per independent process. Aggregate p50/p95/p99 are means of three process percentiles, with vectors/ranges; never pooled percentiles.

Successful scenario rates share their whole-profile measurement denominator; CPU/RSS/GC are available only for whole processes. No capacity or long-duration acceptance is inferred.

### Ordinary operations

| Frozen scenario / protocol / payload bytes / messages | Route | Success/s | Mean ms | Mean process p50 / p95 / p99 ms | Unexpected errors | Request / response messages/s | Request / response MiB/s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| grpc-unary / http2-tls / 64 / 1 | before | 8.04514 | 6.67471 | 3.2527 / 20.9422 / 37.7318 | 0 | 8.04514 / 8.04514 | 0.000491037 / 0.000491037 |
| grpc-unary / http2-tls / 64 / 1 | after | 8.04844 | 10.1452 | 3.46639 / 31.1252 / 53.0268 | 0 | 8.04844 / 8.04844 | 0.000491238 / 0.000491238 |
| grpc-unary / http2-tls / 64 / 1 | direct | 8.04887 | 2.33466 | 2.07275 / 3.34187 / 7.7816 | 0 | 8.04887 / 8.04887 | 0.000491264 / 0.000491264 |
| grpc-unary / http2-tls / 65536 / 1 | before | 7.99548 | 7.27665 | 4.18551 / 22.3058 / 39.8554 | 0 | 7.99548 / 7.99548 | 0.499718 / 0.499718 |
| grpc-unary / http2-tls / 65536 / 1 | after | 7.99876 | 10.3453 | 4.24246 / 31.2538 / 40.3905 | 0 | 7.99876 / 7.99876 | 0.499923 / 0.499923 |
| grpc-unary / http2-tls / 65536 / 1 | direct | 7.99918 | 2.97431 | 2.63434 / 4.96287 / 10.3994 | 0 | 7.99918 / 7.99918 | 0.499949 / 0.499949 |

### Changes and direct Rust distance

Negative after-minus-before latency means lower latency. Rust gaps use direct Rust as denominator. These are descriptive differences; A21's verdict applies only to independent-process arrival means.

| Scenario | After − before mean ms / % | After − before p99 ms / % | Before / after p99 gap to Rust % | A21 mean verdict |
| --- | ---: | ---: | ---: | --- |
| grpc-unary / http2-tls / 64 / 1 | 3.47045 / 51.994 | 15.295 / 40.5361 | 384.885 / 581.438 | inconclusive |
| grpc-unary / http2-tls / 65536 / 1 | 3.06865 / 42.1712 | 0.535134 / 1.34269 | 283.248 / 288.394 | inconclusive |

### Whole-profile process resources

Each row is one process; these values cannot be assigned to an individual scenario. GC allocation rates cover only the observed approximate snapshot bracket.

| Route / process | Server CPU % of one core | Sampled peak RSS MiB | GC observed allocation MiB/s | Source / native identity |
| --- | ---: | ---: | ---: | --- |
| before / 0 | 3.98139 | 50.2305 | 17.2863 | db95a9fbdd18c208ba8fa3fdb6dabaa2bcc073c0 / 28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2 |
| before / 1 | 4.81595 | 66.0078 | 17.3202 | db95a9fbdd18c208ba8fa3fdb6dabaa2bcc073c0 / 28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2 |
| before / 2 | 4.29417 | 49.8359 | 17.2904 | db95a9fbdd18c208ba8fa3fdb6dabaa2bcc073c0 / 28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2 |
| after / 0 | 3.92846 | 68.2461 | 1.27343 | 9de3f74444246e356a2b12ab664ef99286309aaf / 28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2 |
| after / 1 | 4.34424 | 68.4492 | 1.27089 | 9de3f74444246e356a2b12ab664ef99286309aaf / 28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2 |
| after / 2 | 4.18673 | 68.3047 | 1.26842 | 9de3f74444246e356a2b12ab664ef99286309aaf / 28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2 |
| direct / 0 | 0.628132 | 13.1836 | N/A | 4f4b2204f321b80cc45bac9c5ba7a3452dad8aa6 / 6c7c4053a6a7e141dc044e13185e6f54a8b59741ea4835ebcf92327b940e2da0 |
| direct / 1 | 0.57645 | 13.1953 | N/A | 4f4b2204f321b80cc45bac9c5ba7a3452dad8aa6 / 6c7c4053a6a7e141dc044e13185e6f54a8b59741ea4835ebcf92327b940e2da0 |
| direct / 2 | 0.576702 | 13.1719 | N/A | 4f4b2204f321b80cc45bac9c5ba7a3452dad8aa6 / 6c7c4053a6a7e141dc044e13185e6f54a8b59741ea4835ebcf92327b940e2da0 |

### Expected control probes

Expected cancellations/deadlines are excluded from business success/byte rates. Observed prefix bytes remain in JSON raw totals.

No expected probes were present in the selected ordinary-only profile.

### Evidence and limitations

The JSON contains exact cell directories, input hashes, producer/package/native identities, each process's latency/count/rate vectors, actual payload/encoded-byte totals, all resource summaries and failures. Fewer than 100 successes gives no per-process p99. Missing fields stay N/A; a failed process is never replaced by averaging only successful processes.

## grpc-streams

Interpretation eligible: **true**.

Equal weight per independent process. Aggregate p50/p95/p99 are means of three process percentiles, with vectors/ranges; never pooled percentiles.

Successful scenario rates share their whole-profile measurement denominator; CPU/RSS/GC are available only for whole processes. No capacity or long-duration acceptance is inferred.

### Ordinary operations

| Frozen scenario / protocol / payload bytes / messages | Route | Success/s | Mean ms | Mean process p50 / p95 / p99 ms | Unexpected errors | Request / response messages/s | Request / response MiB/s |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| grpc-client / http2-tls / 4096 / 32 | before | 5.30946 | 30.0461 | 20.4002 / 90.9873 / 118.887 | 0 | 169.903 / 5.30946 | 0.663683 / 0 |
| grpc-client / http2-tls / 4096 / 32 | after | 5.31234 | 31.3641 | 19.3438 / 95.7313 / 141.691 | 0 | 169.995 / 5.31234 | 0.664043 / 0 |
| grpc-client / http2-tls / 4096 / 32 | direct | 5.31601 | 3.39157 | 2.80375 / 4.96902 / 17.8877 | 0 | 170.112 / 5.31601 | 0.664501 / 0 |
| grpc-duplex / http2-tls / 4096 / 32 | before | 5.35908 | 67.8666 | 56.7225 / 186.185 / 223.601 | 0 | 171.491 / 171.491 | 0.669886 / 0.669886 |
| grpc-duplex / http2-tls / 4096 / 32 | after | 5.36199 | 76.5851 | 62.7551 / 192.888 / 256.706 | 0 | 171.584 / 171.584 | 0.670249 / 0.670249 |
| grpc-duplex / http2-tls / 4096 / 32 | direct | 5.36569 | 3.42059 | 3.11294 / 5.33425 / 7.33204 | 0 | 171.702 / 171.702 | 0.670711 / 0.670711 |
| grpc-server / http2-tls / 4096 / 32 | before | 5.35908 | 42.3394 | 25.1262 / 137.713 / 231.061 | 0 | 5.35908 / 171.491 | 0.0209339 / 0.669886 |
| grpc-server / http2-tls / 4096 / 32 | after | 5.36199 | 45.8402 | 31.7449 / 139.198 / 183.109 | 0 | 5.36199 / 171.584 | 0.0209453 / 0.670249 |
| grpc-server / http2-tls / 4096 / 32 | direct | 5.36569 | 3.1723 | 2.69993 / 4.84336 / 16.0541 | 0 | 5.36569 / 171.702 | 0.0209597 / 0.670711 |

### Changes and direct Rust distance

Negative after-minus-before latency means lower latency. Rust gaps use direct Rust as denominator. These are descriptive differences; A21's verdict applies only to independent-process arrival means.

| Scenario | After − before mean ms / % | After − before p99 ms / % | Before / after p99 gap to Rust % | A21 mean verdict |
| --- | ---: | ---: | ---: | --- |
| grpc-client / http2-tls / 4096 / 32 | 1.31802 / 4.38666 | 22.8033 / 19.1806 | 564.632 / 692.113 | inconclusive |
| grpc-duplex / http2-tls / 4096 / 32 | 8.71851 / 12.8465 | 33.1044 / 14.8051 | 2949.64 / 3401.15 | within_band |
| grpc-server / http2-tls / 4096 / 32 | 3.50079 / 8.26839 | -47.9515 / -20.7528 | 1339.26 / 1040.58 | inconclusive |

### Whole-profile process resources

Each row is one process; these values cannot be assigned to an individual scenario. GC allocation rates cover only the observed approximate snapshot bracket.

| Route / process | Server CPU % of one core | Sampled peak RSS MiB | GC observed allocation MiB/s | Source / native identity |
| --- | ---: | ---: | ---: | --- |
| before / 0 | 12.9203 | 84.5273 | 21.7689 | db95a9fbdd18c208ba8fa3fdb6dabaa2bcc073c0 / 28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2 |
| before / 1 | 11.8683 | 80.5781 | 21.7568 | db95a9fbdd18c208ba8fa3fdb6dabaa2bcc073c0 / 28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2 |
| before / 2 | 11.9531 | 87.6055 | 21.4161 | db95a9fbdd18c208ba8fa3fdb6dabaa2bcc073c0 / 28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2 |
| after / 0 | 12.926 | 103.117 | 17.9657 | 9de3f74444246e356a2b12ab664ef99286309aaf / 28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2 |
| after / 1 | 12.9265 | 93.4727 | 17.6584 | 9de3f74444246e356a2b12ab664ef99286309aaf / 28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2 |
| after / 2 | 11.0292 | 102.641 | 17.3216 | 9de3f74444246e356a2b12ab664ef99286309aaf / 28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2 |
| direct / 0 | 1.04828 | 13.1367 | N/A | 4f4b2204f321b80cc45bac9c5ba7a3452dad8aa6 / 6c7c4053a6a7e141dc044e13185e6f54a8b59741ea4835ebcf92327b940e2da0 |
| direct / 1 | 1.04809 | 13.0859 | N/A | 4f4b2204f321b80cc45bac9c5ba7a3452dad8aa6 / 6c7c4053a6a7e141dc044e13185e6f54a8b59741ea4835ebcf92327b940e2da0 |
| direct / 2 | 1.04767 | 13.1367 | N/A | 4f4b2204f321b80cc45bac9c5ba7a3452dad8aa6 / 6c7c4053a6a7e141dc044e13185e6f54a8b59741ea4835ebcf92327b940e2da0 |

### Expected control probes

Expected cancellations/deadlines are excluded from business success/byte rates. Observed prefix bytes remain in JSON raw totals.

No expected probes were present in the selected ordinary-only profile.

### Evidence and limitations

The JSON contains exact cell directories, input hashes, producer/package/native identities, each process's latency/count/rate vectors, actual payload/encoded-byte totals, all resource summaries and failures. Fewer than 100 successes gives no per-process p99. Missing fields stay N/A; a failed process is never replaced by averaging only successful processes.


## Frozen identities and scope

Complete original comparison-index SHA-256: `2eedad4d6a4eb8f465f182e0f3d05cb6d602131b3fb39d24e58717b7a1e9244b`. Complete original noise-index SHA-256: `c5afdc5a893b2927150c6db26bb3823a44d21ad43b51df01900e6d8848117de0`. The noise identity was published/read back in Plan `9469e0cf7d22c70b469dbd7358b53c258d7310cb` before comparison. Owner receipt SHA-256: `90ed6eb3249da8fbac19f392205a956043b526726358d83ac77c8b7dee4ce854`.

The control was `db95a9fbdd18c208ba8fa3fdb6dabaa2bcc073c0`; the tested candidate was `9de3f74444246e356a2b12ab664ef99286309aaf`. Both used Server native SHA-256 `28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2`. This diagnostic does not replace the original Perf-01 before/after matrix, capacity testing or five final 30-minute groups. Identity-only gRPC payload compression remains unchanged.

Only README.md, comparison.json and manifest.json form the public data allowlist. Numeric values and screen objects are copied unchanged; no reader or workload was replayed. Process identifiers, command arguments, environment and TLS material remain private in the bound originals. These curated files are retained while Git history is retained; no remote full-raw archive is claimed.
