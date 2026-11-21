# Perf-01: completed gRPC buffer ablation

**Recommendation: keep `ea006711` isolated; do not select it for the final product on this result alone.** The candidate sharply reduced allocation and streaming CPU, while all three server-stream and client-stream p99 pairs increased. Its RSS after the fixed idle was higher in every pair. All 12 short TLS cells passed the unchanged correctness, service-standard and drain checks. This is an actual diagnostic result, with no formal A21, capacity or 30-minute acceptance credit.

## Actual scope and identity

Execution ran from **2026-11-21T09:40:02.826807+00:00** to **2026-11-21T09:47:27.184760+00:00**. All **37 finite commands exited 0 and retired**, with no live owned process or owner child remaining in their receipts. Each profile ran three interleaved current/candidate process pairs: current then candidate, candidate then current, current then candidate. Each cell offered, dispatched and successfully completed **323 ordinary calls**, for **3,876** measured successful calls in total. Warmup (24 calls), recovery (32 calls) and idle (5 seconds) were separate.

Current managed code was `2f40348c3db80a4fbee7a99e721b374a597b16df`; candidate managed code was `ea0067114346af4f13383f24df165456bcabe344`. Both actually loaded the same precompiled Server from native source `2f40348c3db80a4fbee7a99e721b374a597b16df`, SHA-256 `8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0`. The common application/client driver was `2e3995df8d86583ee9443348276ca8d918056bfc`. The actual shared independent client SHA-256 was `ae59038f6d83b0cdc60677f5d65f50f06298b53a168bee65f73a6599d7832f8e`. The reused native component-test binary (`83b57ab5…`) is separate and was not the experiment's loaded Server.

Each profile requested 20 seconds at 16 calls/s, concurrency 4, four reusable HTTP/2 client connections and TLS. The original controller recorded 20.125 scheduled seconds in every cell and approximately 20.13–20.32 elapsed seconds. Server CPU affinity remained 2,3; generator affinity remained 0,1. Managed/native payload budgets stayed 64 MiB each, RSS cap 256 MiB, arrival-p99 limit 500 ms, and unexpected-error allowance zero. Compression stayed identity. Application, DTO, protobuf, arrival schedule and correctness predicates were unchanged. Builds used locked .NET 11.0.100, Release Native AOT, x86-64-v2.

Before these timings, the actual supplied-native B18 run passed **1036 JIT assertions / 602 retirements** and **1037 AOT assertions / 598 retirements**, including the added writer cases. The experiment used truthful managed/native source provenance; its mixed-source build is intentionally ineligible for the original formal comparison reader.

[projection.json](projection.json) contains every original result/receipt hash, selected server/client/package identity, 30 scenario observations, 12 process resource observations and all 37 command receipts. Values below are rounded for readability; JSON preserves exact integer nanoseconds/bytes and original recorded percentages. Raw request and resource series were not reprocessed for this report. Histogram maxima in JSON are configured bounds, not observed per-call maxima.

## Latency: all three process pairs

Latency runs from scheduled arrival to completion, including controller queue/IPC. Each triplet is replicate **0 / 1 / 2**, paired by replicate, not execution order. Changes are descriptive arithmetic only. **Mean latency is unavailable for every process/case:** completed metadata contains exact percentiles and counts, without a latency sum or mean. No mean was inferred from histogram bins.

| Case | Current p99, ms (0 / 1 / 2) | Candidate p99, ms (0 / 1 / 2) | Paired p99 change (0 / 1 / 2) |
| --- | --- | --- | --- |
| Unary, 64 B | 40.439 / 37.868 / 43.229 | 41.934 / 42.202 / 40.148 | +3.70% / +11.45% / -7.13% |
| Unary, 65536 B | 44.174 / 42.006 / 41.563 | 40.026 / 41.975 / 41.924 | -9.39% / -0.07% / +0.87% |
| Client stream, 32 × 4 KiB | 88.859 / 127.484 / 137.880 | 93.299 / 130.826 / 153.491 | +5.00% / +2.62% / +11.32% |
| Duplex, 32 × 4 KiB | 220.658 / 218.962 / 378.101 | 208.431 / 276.918 / 206.664 | -5.54% / +26.47% / -45.34% |
| Server stream, 32 × 4 KiB | 155.947 / 193.281 / 248.678 | 255.225 / 261.648 / 256.710 | +63.66% / +35.37% / +3.23% |

Server-stream and client-stream p99 were higher in every candidate pair. Duplex was mixed, including a lower candidate p99 in replicate 2 against a high current tail. Unary p99 was mixed. Every p99 remained below the existing 500 ms service limit; that absolute pass does not establish a comparative improvement. Exact p50/p95 and per-case rates for every process are in the JSON. As an adverse median example, unary 64 B p50 in replicate 2 rose from 15.760 to 17.330 ms, and unary 64 KiB p50 rose from 11.326 to 18.470 ms.

## Resource observations

CPU is the original sampled percentage of one core; 100% means one occupied core. Allocation/GC deltas span the first to last managed measurement samples, not every allocation through startup/shutdown. Each row preserves a current → candidate pair.

| Profile / replicate | Allocated MiB | Allocation change | CPU % of one core | CPU change | GC counts gen0/gen1/gen2 |
| --- | ---: | ---: | ---: | ---: | --- |
| unary / 0 | 338.07 → 186.98 | -44.69% | 3.98 → 3.67 | -7.82% | 46/37/36 → 30/17/16 |
| unary / 1 | 341.35 → 188.16 | -44.88% | 3.15 → 3.46 | +9.95% | 48/40/38 → 24/12/10 |
| unary / 2 | 338.08 → 188.19 | -44.34% | 3.46 → 3.62 | +4.54% | 48/39/37 → 29/17/15 |
| streams / 0 | 6911.82 → 190.00 | -97.25% | 12.89 → 7.65 | -40.68% | 637/586/586 → 98/2/1 |
| streams / 1 | 6915.15 → 190.34 | -97.25% | 15.76 → 7.80 | -50.51% | 714/662/662 → 98/1/1 |
| streams / 2 | 6977.51 → 192.55 | -97.24% | 14.04 → 7.81 | -44.34% | 689/637/637 → 99/2/1 |

| Profile / replicate | Sampled active RSS maximum, MiB | Last active RSS, MiB | After-idle RSS, MiB | Sampled managed heap maximum, MiB |
| --- | ---: | ---: | ---: | ---: |
| unary / 0 | 67.54 → 71.19 | 33.92 → 36.13 | 33.96 → 35.74 | 54.32 → 67.39 |
| unary / 1 | 51.58 → 71.41 | 33.81 → 36.33 | 33.95 → 35.88 | 54.30 → 67.45 |
| unary / 2 | 67.47 → 71.52 | 33.91 → 36.29 | 33.55 → 36.44 | 53.31 → 68.38 |
| streams / 0 | 74.32 → 69.48 | 39.55 → 52.55 | 39.04 → 52.64 | 20.73 → 43.39 |
| streams / 1 | 42.21 → 69.36 | 33.32 → 52.73 | 33.35 → 52.75 | 18.73 → 43.54 |
| streams / 2 | 76.43 → 69.16 | 33.28 → 52.53 | 40.18 → 52.55 | 28.20 → 43.40 |

Streaming managed allocation fell by about 97.25% in all three pairs, with lower sampled CPU in all three. Unary allocation fell by about 44–45%, while CPU was mixed. The candidate did **not** demonstrate a memory-footprint improvement: active RSS maxima were higher in every unary pair and mixed in streams; last-active and after-idle RSS were higher in all six candidate pairs. Managed-heap maxima were also higher in all six pairs. Lower GC frequency is observed alongside those outcomes; this experiment does not attribute their cause.

After-idle RSS is a separate procfs observation before final disposal. It is not the last active sample or an after-process-exit value. Native payload/request/retiring/queue gauges returned to zero in every cell; every final close was `Completed` / `Disposed` with zero pending requests and zero retained managed/native bytes. All 32 recovery calls passed in each cell. These finite-cell drain checks do not assert that RSS returned to its pre-load level. Native gauge maxima are sampled and can miss brief grants: sampled zero does not prove zero transient allocation.

## Work and correctness actually exercised

All measured wire statuses were `GrpcOK`; every process had zero correctness failures, unexpected errors, timeouts and intentional cancel/deadline probes. The original client verified protobuf content and completed-transfer acknowledgements. Every process within a profile had identical successful counts below. Payload bytes exclude protobuf field/envelope/TLS framing; exact encoded protobuf bytes are retained in JSON. These ordinary short mixes did not newly exercise deadline/cancel probes; B18 is the separate functional evidence.

| Case | Successful calls per process | Request / response messages | Request / response payload bytes |
| --- | ---: | ---: | ---: |
| grpc-unary 64 B | 162 | 162 / 162 | 10,368 / 10,368 |
| grpc-unary 65536 B | 161 | 161 / 161 | 10,551,296 / 10,551,296 |
| grpc-client | 107 | 3,424 / 107 | 14,024,704 / 0 |
| grpc-duplex | 108 | 3,456 / 3,456 | 14,155,776 / 14,155,776 |
| grpc-server | 108 | 108 / 3,456 | 442,368 / 14,155,776 |

Successful throughput was approximately 15.90–16.05 calls/s across cells at the fixed offered rate. This is not measured capacity. The generator reached at most four calls in progress for each streaming cell; unary maxima were one or two. Configured HTTP/2 limits and client calls in progress do not measure actual simultaneous transport streams.

## Decision and remaining risks

Preserve the candidate and adverse results as an isolated experiment; retain current `2f40348` as the selected product pending another evidence-based decision. The allocation/CPU reduction merits investigation, but this run does not justify a tail-latency or RSS win. No direct-Rust server or original EA5 server ran here, so it cannot revise those gaps. Formal A21 noise classification, same-commit producing-native proof, capacity and all 30-minute acceptance remain separate obligations.

Three source-confirmed costs remain unisolated: the small-buffer path adds a synchronous native grant/release pair, whose release calls `host.reap()`; it keeps an extra 16 KiB budget grant per concurrent small-mode output; and a growing unhinted message retains the old 16 KiB plus the full array and copies the advanced prefix. Optional-grant fallback also handles an internal `resource_limit` exception. None is established as the cause of the p99 pattern. Exact FFI/copy counts, tight-budget traffic failure boundaries and higher-concurrency behavior were not measured. Any later revision must preserve metadata/HPACK/admission/cleanup fixes and ownership checks.

The implementation rationale is `NativeWeave/tests/Perf01.GrpcBuffer/README.md` at `ea006711`. Original runtime evidence is identified by execution/result/build/receipt file names and SHA-256 in JSON. Those names are relative to execution evidence root `epoch-002` (explicit repository prefixes identify sources); raw files are not asserted to be committed beside this projection. Durable archive publication is recorded by the owning Perf-01 handoff. No binaries, raw request records, environment maps, machine paths, PIDs or TLS credentials are included here.
