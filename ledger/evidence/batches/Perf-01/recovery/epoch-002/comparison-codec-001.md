# Perf-01: completed codec short comparisons

This is an interim public projection of completed, frozen codec comparison metadata. It preserves the original A21 decisions and observed values. It grants no new correctness, statistical, capacity, long-run or overall acceptance. The final selected product still has separate unresolved acceptance work in other domains.
Observed outcome: codec-w1: 5/32 public-call means and 5/32 full-operation means have the original improvement decision; 0 public-call and 0 full-operation regression decisions. codec-w2: 11/32 public-call means and 11/32 full-operation means have the original improvement decision; 0 public-call and 0 full-operation regression decisions. The remaining mean decisions and every adverse or inconclusive direct-Rust comparison stay in the tables below. No before/after arrival-mean improvement is established in either completed profile. Fixed-rate wall throughput does not establish higher capacity.


## Scope and identities

Before: `ea5fa528035d025bd7a28698ee7c71194432236c`. Selected after: `2f40348c3db80a4fbee7a99e721b374a597b16df`. Common driver: `2e3995df8d86583ee9443348276ca8d918056bfc`. Linux x64, Release Native AOT, .NET 11.0.100, Rust 1.100.0, locked miniz_oxide 0.9.1. Both NativeWeave roles actually loaded the same codec native bytes, SHA-256 `225891ba2e8ab97381bfb7b35814aea00a16135da01b9afcd6de8e97a58a6d15`. The local Core/SyncProof proof packages are distinct from the B24 domain packages. Their actual package and executable hashes are in the JSON companion.

Each worker-count profile contains three independent processes per before/after/direct/managed cohort, run by the existing serial owner. Direct and managed comparators use their actually recorded before-build artifacts. The direct engine has the same locked miniz version and strict bounded single-stream contract; `.NET ZLibStream` is a valid-corpus isolated-call comparator with a narrower semantic scope.

## What the numbers mean

- Each row is one compression/decompression, array/owned, size/entropy partition. Successes, bytes and errors remain integers. The JSON retains every per-process value, including p50/p95/p99, counters, phase counts and original validity/service/recovery flags.
- Row latency tails are pooled nearest-rank percentiles across the three processes. The original noise decisions use three independent **process means**, not those pooled tails. All original before/after, before/direct and after/direct decisions are preserved; no new noise test is run here.
- Row successful throughput and raw MiB/s use the sum of full process observation windows. They are contributions to the frozen mixed workload. Raw MiB/s based on summed codec-call time is a different metric and is not concurrent wall throughput or maximum capacity.
- Array public-call timing includes the managed output copy and native-result retirement. NativeBuffer public-call timing excludes the later `Read` validation and `Dispose`; consume, release and full-operation timings remain separate. Direct array/owned labels partition the same Vec path. Managed owned labels alias the array path.
- `.NET ZLibStream` cannot expose strict consumed-input accounting for rejecting trailing or concatenated streams in this wrapper. Its public-call and observed encoded-size data remain descriptive valid-corpus comparisons; there is no managed full-operation/arrival/NativeBuffer ranking.
- Managed allocation counters are actual per-thread observations for the public call and for call plus validation. Copy and FFI counters are derived output-copy and codec/result-free counts; they do not observe all allocator activity, engine-internal copies or hardware memory traffic. Unknown values remain null/N/A.
- CPU and RSS cover the whole mixed target process, including fixture, oracle and runtime work. Headline RSS is the maximum sampled process RSS, not the mean of process peaks; sampled intervals may miss peaks. Drain GC totals and allocated bytes are cumulative lifecycle counters, including warmup/recovery, not measurement-only GC deltas. Missing direct/managed native counters remain N/A.

## Frozen corpus and limits

The corpus uses seed 2654435769, zlib format, compression level 6 and Adler32. Raw and decoded limits are 4,194,304 bytes; encoded input/output limit is 4,259,840 bytes. Every case retains the recorded raw and encoded SHA-256 in the JSON. No payload was re-read or re-hashed to author this projection.

Observed row means also pool the recorded operations; per-process means are retained separately and remain the inputs to the original noise test.

| Case | Raw bytes | Entropy | Frozen encoded bytes | Raw/encoded |
| --- | --- | --- | --- | --- |
| 0 | 256 | compressible | 109 | 2.349 |
| 1 | 256 | pseudorandom | 267 | 0.959 |
| 2 | 4096 | compressible | 126 | 32.508 |
| 3 | 4096 | pseudorandom | 4107 | 0.997 |
| 4 | 1048576 | compressible | 3165 | 331.304 |
| 5 | 1048576 | pseudorandom | 1048752 | 1.000 |
| 6 | 4194304 | compressible | 12311 | 340.696 |
| 7 | 4194304 | pseudorandom | 4194975 | 1.000 |

## Completed execution and original decisions

| Profile | Actual start → end (UTC) | Commands exit 0 / retired | BA call means I / R / band / inconclusive | BA operation means I / R / band / inconclusive |
| --- | --- | --- | --- | --- |
| codec-w1 | 2026-11-21T08:05:51.542910+00:00 → 2026-11-21T08:37:50.590726+00:00 | 13/13 | 5 / 0 / 10 / 17 | 5 / 0 / 9 / 18 |
| codec-w2 | 2026-11-21T08:37:55.285871+00:00 → 2026-11-21T08:59:15.984476+00:00 | 13/13 | 11 / 0 / 4 / 17 | 11 / 0 / 4 / 17 |

## codec-w1

The frozen plan has 1 worker(s), target CPUs [2, 3], generator CPUs [0, 1], 134.0 planned calls/s, 120.0 scheduled seconds per process, queue capacity 64, maximum in-flight 256, 1000.0 ms deadline and 100.0 ms generator-lag limit. Warmup is 20.0 s; recovery is 10.0 s at 1.0 call/s; idle observation is 5 s. The exact 160-entry fixed operation sequence and actual dispatch/observation windows are retained per process in JSON. The original service limit is p99 ≤ 500 ms and sampled RSS ≤ 256 MiB.

### Whole-profile resources and counts

| Cohort | Measurement successes | Errors | Sum observation s | Mixed successes/s | Target CPU % of one core | Maximum sampled RSS MiB |
| --- | --- | --- | --- | --- | --- | --- |
| before | 48285 | 0 | 360.316 | 134.007 | 43.048 | 82.441 |
| after | 48285 | 0 | 360.317 | 134.007 | 43.348 | 78.211 |
| direct | 48285 | 0 | 360.316 | 134.008 | 41.172 | 29.172 |
| managed | 48285 | 0 | 360.315 | 134.008 | 37.906 | 114.570 |

The managed row is a resource observation of its complete valid-corpus harness, not a claim that its full semantics or validation cost are equivalent. No row-level CPU attribution is made.

### Public codec call means and original noise decisions

Values are μs. Percent changes use `(new − reference) / reference`; negative call-time changes are faster. AD is selected after versus direct. Managed call means are included only within the stated valid-corpus scope.

| Partition | Before μs | After μs | Direct μs | Managed μs | BA % | Original BA | AD % | Original AD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| c/a/case-0 (256 B, compressible) | 47.713 | 36.199 | 31.517 | 24.334 | -24.132% | inconclusive | +14.855% | within_band |
| c/o/case-0 (256 B, compressible) | 42.363 | 34.385 | 28.666 | 23.095 | -18.832% | inconclusive | +19.953% | within_band |
| d/a/case-0 (256 B, compressible) | 24.238 | 13.850 | 9.740 | 24.929 | -42.857% | improvement | +42.196% | within_band |
| d/o/case-0 (256 B, compressible) | 21.272 | 13.133 | 9.068 | 26.861 | -38.261% | improvement | +44.825% | inconclusive |
| c/a/case-1 (256 B, pseudorandom) | 45.740 | 39.206 | 34.525 | 37.447 | -14.284% | within_band | +13.558% | within_band |
| c/o/case-1 (256 B, pseudorandom) | 39.761 | 34.858 | 31.026 | 34.588 | -12.331% | within_band | +12.350% | within_band |
| d/a/case-1 (256 B, pseudorandom) | 14.754 | 6.732 | 1.860 | 26.455 | -54.370% | improvement | +261.958% | regression |
| d/o/case-1 (256 B, pseudorandom) | 11.483 | 5.803 | 2.034 | 24.676 | -49.460% | within_band | +185.262% | within_band |
| c/a/case-2 (4096 B, compressible) | 54.215 | 41.324 | 36.015 | 30.714 | -23.777% | inconclusive | +14.742% | within_band |
| c/o/case-2 (4096 B, compressible) | 51.482 | 44.953 | 38.247 | 34.395 | -12.682% | improvement | +17.534% | regression |
| d/a/case-2 (4096 B, compressible) | 22.446 | 19.439 | 13.982 | 29.681 | -13.399% | within_band | +39.024% | inconclusive |
| d/o/case-2 (4096 B, compressible) | 27.958 | 17.061 | 13.776 | 40.891 | -38.976% | improvement | +23.852% | regression |
| c/a/case-3 (4096 B, pseudorandom) | 100.409 | 104.339 | 88.885 | 101.251 | +3.914% | inconclusive | +17.387% | inconclusive |
| c/o/case-3 (4096 B, pseudorandom) | 84.944 | 81.349 | 77.693 | 86.716 | -4.233% | inconclusive | +4.705% | inconclusive |
| d/a/case-3 (4096 B, pseudorandom) | 21.706 | 12.939 | 3.873 | 32.482 | -40.390% | inconclusive | +234.066% | regression |
| d/o/case-3 (4096 B, pseudorandom) | 18.359 | 9.374 | 5.901 | 26.844 | -48.940% | within_band | +58.843% | within_band |
| c/a/case-4 (1048576 B, compressible) | 1991.614 | 2001.976 | 1970.347 | 375.808 | +0.520% | within_band | +1.605% | inconclusive |
| c/o/case-4 (1048576 B, compressible) | 1989.734 | 2013.509 | 1969.381 | 398.741 | +1.195% | inconclusive | +2.241% | inconclusive |
| d/a/case-4 (1048576 B, compressible) | 1372.838 | 1179.811 | 474.611 | 1389.949 | -14.060% | inconclusive | +148.585% | regression |
| d/o/case-4 (1048576 B, compressible) | 484.360 | 486.200 | 489.131 | 1337.630 | +0.380% | within_band | -0.599% | within_band |
| c/a/case-5 (1048576 B, pseudorandom) | 27358.226 | 27641.744 | 27145.591 | 21194.093 | +1.036% | inconclusive | +1.828% | inconclusive |
| c/o/case-5 (1048576 B, pseudorandom) | 26917.358 | 27231.312 | 27136.919 | 21322.934 | +1.166% | inconclusive | +0.348% | inconclusive |
| d/a/case-5 (1048576 B, pseudorandom) | 1038.642 | 945.686 | 317.973 | 1352.949 | -8.950% | inconclusive | +197.411% | regression |
| d/o/case-5 (1048576 B, pseudorandom) | 204.346 | 191.825 | 199.533 | 1134.036 | -6.127% | inconclusive | -3.863% | within_band |
| c/a/case-6 (4194304 B, compressible) | 7685.513 | 8059.768 | 8094.331 | 1308.437 | +4.870% | inconclusive | -0.427% | inconclusive |
| c/o/case-6 (4194304 B, compressible) | 7811.577 | 7937.197 | 8016.246 | 1348.221 | +1.608% | inconclusive | -0.986% | inconclusive |
| d/a/case-6 (4194304 B, compressible) | 4574.137 | 4176.135 | 1865.701 | 5825.016 | -8.701% | within_band | +123.837% | regression |
| d/o/case-6 (4194304 B, compressible) | 1756.202 | 1800.165 | 1764.505 | 4904.472 | +2.503% | within_band | +2.021% | within_band |
| c/a/case-7 (4194304 B, pseudorandom) | 111435.000 | 111882.773 | 109365.147 | 85134.154 | +0.402% | inconclusive | +2.302% | inconclusive |
| c/o/case-7 (4194304 B, pseudorandom) | 107974.461 | 109489.002 | 109321.230 | 85508.556 | +1.403% | inconclusive | +0.153% | inconclusive |
| d/a/case-7 (4194304 B, pseudorandom) | 4547.409 | 4413.792 | 1030.921 | 4332.591 | -2.938% | inconclusive | +328.141% | regression |
| d/o/case-7 (4194304 B, pseudorandom) | 844.446 | 871.432 | 889.524 | 3476.659 | +3.196% | within_band | -2.034% | within_band |

### Full operation and owned lifetime costs

Full operation is public call + consume + release. These means do not replace the separate public-call measure. Managed full-operation ranking is intentionally absent.

| Partition | Before operation μs | After operation μs | Direct operation μs | BA % | Original BA | After consume μs | After release μs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| c/a/case-0 (256 B, compressible) | 47.803 | 36.312 | 31.757 | -24.039% | inconclusive | 0.113 | 0.000 |
| c/o/case-0 (256 B, compressible) | 43.208 | 35.370 | 28.905 | -18.141% | inconclusive | 0.544 | 0.440 |
| d/a/case-0 (256 B, compressible) | 24.392 | 14.079 | 10.081 | -42.282% | improvement | 0.229 | 0.000 |
| d/o/case-0 (256 B, compressible) | 22.315 | 14.518 | 9.503 | -34.939% | improvement | 0.900 | 0.486 |
| c/a/case-1 (256 B, pseudorandom) | 45.837 | 39.320 | 34.729 | -14.218% | within_band | 0.114 | 0.000 |
| c/o/case-1 (256 B, pseudorandom) | 40.655 | 35.826 | 31.202 | -11.876% | within_band | 0.572 | 0.396 |
| d/a/case-1 (256 B, pseudorandom) | 14.853 | 6.918 | 2.115 | -53.427% | improvement | 0.186 | 0.000 |
| d/o/case-1 (256 B, pseudorandom) | 12.377 | 7.318 | 2.304 | -40.872% | within_band | 0.702 | 0.813 |
| c/a/case-2 (4096 B, compressible) | 54.261 | 41.528 | 36.201 | -23.465% | inconclusive | 0.204 | 0.000 |
| c/o/case-2 (4096 B, compressible) | 52.369 | 45.895 | 38.431 | -12.362% | improvement | 0.505 | 0.436 |
| d/a/case-2 (4096 B, compressible) | 22.898 | 19.881 | 14.458 | -13.176% | inconclusive | 0.442 | 0.000 |
| d/o/case-2 (4096 B, compressible) | 29.414 | 18.539 | 14.534 | -36.972% | improvement | 1.013 | 0.464 |
| c/a/case-3 (4096 B, pseudorandom) | 100.929 | 104.982 | 89.506 | +4.015% | inconclusive | 0.643 | 0.000 |
| c/o/case-3 (4096 B, pseudorandom) | 85.934 | 82.370 | 78.493 | -4.147% | inconclusive | 0.721 | 0.300 |
| d/a/case-3 (4096 B, pseudorandom) | 22.435 | 13.689 | 4.718 | -38.984% | inconclusive | 0.750 | 0.000 |
| d/o/case-3 (4096 B, pseudorandom) | 20.256 | 11.666 | 6.788 | -42.408% | within_band | 1.575 | 0.717 |
| c/a/case-4 (1048576 B, compressible) | 1992.270 | 2002.808 | 1971.207 | +0.529% | within_band | 0.832 | 0.000 |
| c/o/case-4 (1048576 B, compressible) | 1992.053 | 2016.190 | 1970.013 | +1.212% | inconclusive | 1.948 | 0.733 |
| d/a/case-4 (1048576 B, compressible) | 1507.997 | 1278.577 | 560.347 | -15.214% | inconclusive | 98.766 | 0.000 |
| d/o/case-4 (1048576 B, compressible) | 596.120 | 577.487 | 555.047 | -3.126% | inconclusive | 90.511 | 0.776 |
| c/a/case-5 (1048576 B, pseudorandom) | 27470.156 | 27734.525 | 27234.300 | +0.962% | inconclusive | 92.781 | 0.000 |
| c/o/case-5 (1048576 B, pseudorandom) | 27021.420 | 27327.685 | 27224.181 | +1.133% | inconclusive | 94.269 | 2.104 |
| d/a/case-5 (1048576 B, pseudorandom) | 1173.596 | 1050.522 | 399.197 | -10.487% | inconclusive | 104.836 | 0.000 |
| d/o/case-5 (1048576 B, pseudorandom) | 262.728 | 250.017 | 239.883 | -4.838% | within_band | 57.367 | 0.825 |
| c/a/case-6 (4194304 B, compressible) | 7687.500 | 8061.694 | 8095.973 | +4.868% | inconclusive | 1.926 | 0.000 |
| c/o/case-6 (4194304 B, compressible) | 7815.995 | 7940.714 | 8017.766 | +1.596% | inconclusive | 2.715 | 0.801 |
| d/a/case-6 (4194304 B, compressible) | 5081.982 | 4696.548 | 2278.997 | -7.584% | within_band | 520.412 | 0.000 |
| d/o/case-6 (4194304 B, compressible) | 2054.066 | 2139.906 | 2045.246 | +4.179% | within_band | 338.036 | 1.706 |
| c/a/case-7 (4194304 B, pseudorandom) | 111769.457 | 112227.887 | 109768.897 | +0.410% | inconclusive | 345.113 | 0.000 |
| c/o/case-7 (4194304 B, pseudorandom) | 108451.784 | 109966.216 | 109714.250 | +1.396% | inconclusive | 473.852 | 3.362 |
| d/a/case-7 (4194304 B, pseudorandom) | 4935.000 | 4819.709 | 1383.641 | -2.336% | inconclusive | 405.918 | 0.000 |
| d/o/case-7 (4194304 B, pseudorandom) | 1130.926 | 1158.813 | 1157.490 | +2.466% | within_band | 286.495 | 0.886 |

### Pooled tails and wall success rates

Call and arrival p99 values below are pooled, descriptive milliseconds. Their percent differences have no separate significance test. Wall success rates are the contribution of each row to the fixed mix. Full p50/p95/p99 and all counters remain in JSON.

| Partition | Call p99 B / A / D ms | Arrival p99 B / A / D ms | Wall successes/s B / A / D |
| --- | --- | --- | --- |
| c/a/case-0 (256 B, compressible) | 0.243 / 0.155 / 0.120 | 117.454 / 117.665 / 113.108 | 8.368 / 8.368 / 8.368 |
| c/o/case-0 (256 B, compressible) | 0.140 / 0.126 / 0.095 | 88.997 / 92.742 / 84.279 | 8.384 / 8.384 / 8.384 |
| d/a/case-0 (256 B, compressible) | 0.112 / 0.067 / 0.037 | 108.001 / 110.571 / 104.463 | 8.368 / 8.368 / 8.368 |
| d/o/case-0 (256 B, compressible) | 0.104 / 0.064 / 0.030 | 90.687 / 92.706 / 89.719 | 8.384 / 8.384 / 8.384 |
| c/a/case-1 (256 B, pseudorandom) | 0.150 / 0.143 / 0.123 | 123.402 / 123.791 / 116.180 | 8.368 / 8.368 / 8.368 |
| c/o/case-1 (256 B, pseudorandom) | 0.138 / 0.137 / 0.091 | 94.672 / 96.683 / 85.750 | 8.384 / 8.384 / 8.384 |
| d/a/case-1 (256 B, pseudorandom) | 0.077 / 0.041 / 0.005 | 58.490 / 62.963 / 55.133 | 8.351 / 8.351 / 8.351 |
| d/o/case-1 (256 B, pseudorandom) | 0.051 / 0.030 / 0.005 | 103.619 / 107.582 / 99.068 | 8.384 / 8.384 / 8.384 |
| c/a/case-2 (4096 B, compressible) | 0.215 / 0.138 / 0.096 | 96.786 / 102.957 / 92.958 | 4.171 / 4.171 / 4.171 |
| c/o/case-2 (4096 B, compressible) | 0.245 / 0.195 / 0.102 | 104.415 / 107.873 / 98.919 | 4.188 / 4.188 / 4.188 |
| d/a/case-2 (4096 B, compressible) | 0.092 / 0.091 / 0.058 | 110.881 / 112.166 / 108.852 | 4.196 / 4.196 / 4.196 |
| d/o/case-2 (4096 B, compressible) | 0.121 / 0.081 / 0.052 | 118.297 / 119.480 / 116.284 | 4.188 / 4.188 / 4.188 |
| c/a/case-3 (4096 B, pseudorandom) | 0.225 / 0.368 / 0.238 | 7.151 / 6.299 / 4.083 | 4.180 / 4.180 / 4.180 |
| c/o/case-3 (4096 B, pseudorandom) | 0.226 / 0.216 / 0.150 | 75.561 / 79.248 / 68.873 | 4.196 / 4.196 / 4.196 |
| d/a/case-3 (4096 B, pseudorandom) | 0.098 / 0.093 / 0.009 | 19.178 / 21.406 / 18.921 | 4.196 / 4.196 / 4.196 |
| d/o/case-3 (4096 B, pseudorandom) | 0.116 / 0.055 / 0.015 | 25.203 / 28.381 / 17.701 | 4.180 / 4.180 / 4.180 |
| c/a/case-4 (1048576 B, compressible) | 4.203 / 4.200 / 3.725 | 41.330 / 39.726 / 31.762 | 3.355 / 3.355 / 3.355 |
| c/o/case-4 (1048576 B, compressible) | 3.974 / 4.341 / 3.703 | 12.027 / 21.977 / 6.837 | 3.355 / 3.355 / 3.355 |
| d/a/case-4 (1048576 B, compressible) | 5.215 / 4.042 / 0.991 | 121.458 / 124.292 / 114.773 | 3.355 / 3.355 / 3.355 |
| d/o/case-4 (1048576 B, compressible) | 1.021 / 1.117 / 1.101 | 108.605 / 111.432 / 105.044 | 3.347 / 3.347 / 3.347 |
| c/a/case-5 (1048576 B, pseudorandom) | 40.941 / 44.472 / 37.849 | 124.278 / 127.210 / 117.857 | 3.339 / 3.339 / 3.339 |
| c/o/case-5 (1048576 B, pseudorandom) | 40.678 / 40.802 / 39.092 | 127.264 / 130.826 / 121.771 | 3.364 / 3.364 / 3.364 |
| d/a/case-5 (1048576 B, pseudorandom) | 6.585 / 4.786 / 1.277 | 11.565 / 8.150 / 3.697 | 3.355 / 3.355 / 3.355 |
| d/o/case-5 (1048576 B, pseudorandom) | 0.498 / 0.465 / 0.491 | 72.453 / 75.334 / 65.726 | 3.355 / 3.355 / 3.355 |
| c/a/case-6 (4194304 B, compressible) | 12.206 / 14.657 / 15.043 | 13.258 / 16.024 / 16.345 | 0.841 / 0.841 / 0.841 |
| c/o/case-6 (4194304 B, compressible) | 12.841 / 13.385 / 12.686 | 30.115 / 38.564 / 25.655 | 0.841 / 0.841 / 0.841 |
| d/a/case-6 (4194304 B, compressible) | 16.896 / 14.026 / 4.185 | 18.079 / 17.323 / 9.137 | 0.833 / 0.833 / 0.833 |
| d/o/case-6 (4194304 B, compressible) | 4.009 / 3.661 / 3.823 | 8.070 / 6.652 / 5.881 | 0.833 / 0.833 / 0.833 |
| c/a/case-7 (4194304 B, pseudorandom) | 146.708 / 143.232 / 138.113 | 149.743 / 155.211 / 141.692 | 0.841 / 0.841 / 0.841 |
| c/o/case-7 (4194304 B, pseudorandom) | 144.477 / 143.667 / 130.055 | 148.587 / 144.964 / 132.369 | 0.833 / 0.833 / 0.833 |
| d/a/case-7 (4194304 B, pseudorandom) | 16.795 / 16.194 / 4.912 | 25.939 / 28.194 / 10.652 | 0.841 / 0.841 / 0.841 |
| d/o/case-7 (4194304 B, pseudorandom) | 2.009 / 2.500 / 2.307 | 77.971 / 72.928 / 64.324 | 0.833 / 0.833 / 0.833 |

### Raw bandwidth, ratio, allocation and derived boundary counts

Bandwidth counts raw input bytes for compression and raw output bytes for decompression. Wall and summed-call MiB/s are deliberately shown separately. Ratios are raw/encoded; managed compression may produce different encoded bytes. Allocation is the public call only; JSON separately preserves allocation including validation.

| Partition | Raw MiB/s wall B / A / D | Raw MiB/s summed-call B / A / D | Raw/encoded A / managed | Allocated B/call B / A | After copied B/call (derived) | After FFI calls/operation (derived) |
| --- | --- | --- | --- | --- | --- | --- |
| c/a/case-0 (256 B, compressible) | 0.002 / 0.002 / 0.002 | 5.117 / 6.744 / 7.746 | 2.349 / 3.241 | 2920.356 / 298.096 | 109.000 | 2.000 |
| c/o/case-0 (256 B, compressible) | 0.002 / 0.002 / 0.002 | 5.763 / 7.100 / 8.517 | 2.349 / 3.241 | 2784.000 / 160.249 | 0.000 | 2.000 |
| d/a/case-0 (256 B, compressible) | 0.002 / 0.002 / 0.002 | 10.073 / 17.627 / 25.065 | 2.349 / 2.349 | 3065.597 / 440.000 | 256.000 | 2.000 |
| d/o/case-0 (256 B, compressible) | 0.002 / 0.002 / 0.002 | 11.477 / 18.590 / 26.923 | 2.349 / 2.349 | 2784.000 / 160.000 | 0.000 | 2.000 |
| c/a/case-1 (256 B, pseudorandom) | 0.002 / 0.002 / 0.002 | 5.338 / 6.227 / 7.071 | 0.959 / 0.959 | 3082.027 / 456.000 | 267.000 | 2.000 |
| c/o/case-1 (256 B, pseudorandom) | 0.002 / 0.002 / 0.002 | 6.140 / 7.004 / 7.869 | 0.959 / 0.959 | 2786.958 / 162.688 | 0.000 | 2.000 |
| d/a/case-1 (256 B, pseudorandom) | 0.002 / 0.002 / 0.002 | 16.548 / 36.265 / 131.264 | 0.959 / 0.959 | 3064.000 / 440.000 | 256.000 | 2.000 |
| d/o/case-1 (256 B, pseudorandom) | 0.002 / 0.002 / 0.002 | 21.261 / 42.068 / 120.004 | 0.959 / 0.959 | 2784.000 / 160.000 | 0.000 | 2.000 |
| c/a/case-2 (4096 B, compressible) | 0.016 / 0.016 / 0.016 | 72.051 / 94.527 / 108.462 | 32.508 / 33.574 | 2936.910 / 316.391 | 126.000 | 2.000 |
| c/o/case-2 (4096 B, compressible) | 0.016 / 0.016 / 0.016 | 75.876 / 86.896 / 102.132 | 32.508 / 33.574 | 2784.000 / 160.000 | 0.000 | 2.000 |
| d/a/case-2 (4096 B, compressible) | 0.016 / 0.016 / 0.016 | 174.026 / 200.952 / 279.371 | 32.508 / 32.508 | 6904.947 / 4280.000 | 4096.000 | 2.000 |
| d/o/case-2 (4096 B, compressible) | 0.016 / 0.016 / 0.016 | 139.716 / 228.954 / 283.564 | 32.508 / 32.508 | 2785.362 / 160.000 | 0.000 | 2.000 |
| c/a/case-3 (4096 B, pseudorandom) | 0.016 / 0.016 / 0.016 | 38.903 / 37.438 / 43.947 | 0.997 / 0.997 | 6920.000 / 4296.000 | 4107.000 | 2.000 |
| c/o/case-3 (4096 B, pseudorandom) | 0.016 / 0.016 / 0.016 | 45.986 / 48.019 / 50.278 | 0.997 / 0.997 | 2784.000 / 160.000 | 0.000 | 2.000 |
| d/a/case-3 (4096 B, pseudorandom) | 0.016 / 0.016 / 0.016 | 179.958 / 301.894 / 1008.525 | 0.997 / 0.997 | 6904.000 / 4280.000 | 4096.000 | 2.000 |
| d/o/case-3 (4096 B, pseudorandom) | 0.016 / 0.016 / 0.016 | 212.776 / 416.720 / 661.932 | 0.997 / 0.997 | 2784.000 / 160.000 | 0.000 | 2.000 |
| c/a/case-4 (1048576 B, compressible) | 3.355 / 3.355 / 3.355 | 502.105 / 499.507 / 507.525 | 331.304 / 144.811 | 5978.303 / 3361.833 | 3165.000 | 2.000 |
| c/o/case-4 (1048576 B, compressible) | 3.355 / 3.355 / 3.355 | 502.580 / 496.645 / 507.774 | 331.304 / 144.811 | 2784.000 / 160.000 | 0.000 | 2.000 |
| d/a/case-4 (1048576 B, compressible) | 3.355 / 3.355 / 3.355 | 728.418 / 847.593 / 2106.987 | 331.304 / 331.304 | 1051384.000 / 1048760.000 | 1048576.000 | 2.000 |
| d/o/case-4 (1048576 B, compressible) | 3.347 / 3.347 / 3.347 | 2064.580 / 2056.767 / 2044.443 | 331.304 / 331.304 | 2784.000 / 160.000 | 0.000 | 2.000 |
| c/a/case-5 (1048576 B, pseudorandom) | 3.339 / 3.339 / 3.339 | 36.552 / 36.177 / 36.838 | 1.000 / 1.000 | 1051572.422 / 1048947.172 | 1048752.000 | 2.000 |
| c/o/case-5 (1048576 B, pseudorandom) | 3.364 / 3.364 / 3.364 | 37.151 / 36.722 / 36.850 | 1.000 / 1.000 | 2806.125 / 216.383 | 0.000 | 2.000 |
| d/a/case-5 (1048576 B, pseudorandom) | 3.355 / 3.355 / 3.355 | 962.796 / 1057.433 / 3144.922 | 1.000 / 1.000 | 1051384.000 / 1048760.000 | 1048576.000 | 2.000 |
| d/o/case-5 (1048576 B, pseudorandom) | 3.355 / 3.355 / 3.355 | 4893.669 / 5213.080 / 5011.714 | 1.000 / 1.000 | 2790.213 / 160.000 | 0.000 | 2.000 |
| c/a/case-6 (4194304 B, compressible) | 3.364 / 3.364 / 3.364 | 520.460 / 496.292 / 494.173 | 340.696 / 146.757 | 15120.000 / 12496.000 | 12311.000 | 2.000 |
| c/o/case-6 (4194304 B, compressible) | 3.364 / 3.364 / 3.364 | 512.061 / 503.956 / 498.987 | 340.696 / 146.757 | 2817.320 / 160.000 | 0.000 | 2.000 |
| d/a/case-6 (4194304 B, compressible) | 3.330 / 3.330 / 3.330 | 874.482 / 957.823 / 2143.966 | 340.696 / 340.696 | 4197112.000 / 4194488.000 | 4194304.000 | 2.000 |
| d/o/case-6 (4194304 B, compressible) | 3.330 / 3.330 / 3.330 | 2277.642 / 2222.019 / 2266.925 | 340.696 / 340.696 | 2784.000 / 160.000 | 0.000 | 2.000 |
| c/a/case-7 (4194304 B, pseudorandom) | 3.364 / 3.364 / 3.364 | 35.895 / 35.752 / 36.575 | 1.000 / 1.000 | 4197784.000 / 4195160.000 | 4194975.000 | 2.000 |
| c/o/case-7 (4194304 B, pseudorandom) | 3.330 / 3.330 / 3.330 | 37.046 / 36.533 / 36.589 | 1.000 / 1.000 | 2784.000 / 160.000 | 0.000 | 2.000 |
| d/a/case-7 (4194304 B, pseudorandom) | 3.364 / 3.364 / 3.364 | 879.622 / 906.250 / 3880.026 | 1.000 / 1.000 | 4197112.000 / 4194488.000 | 4194304.000 | 2.000 |
| d/o/case-7 (4194304 B, pseudorandom) | 3.330 / 3.330 / 3.330 | 4736.832 / 4590.145 / 4496.788 | 1.000 / 1.000 | 2785.227 / 185.387 | 0.000 | 2.000 |

### Original independent-process decision counts

| Original family | Mean scope | Improvement | Regression | Within band | Inconclusive |
| --- | --- | --- | --- | --- | --- |
| after_vs_before | arrival_ns | 0 | 0 | 7 | 25 |
| after_vs_before | call_ns | 5 | 0 | 10 | 17 |
| after_vs_before | operation_ns | 5 | 0 | 9 | 18 |
| after_vs_direct | arrival_ns | 0 | 3 | 5 | 24 |
| after_vs_direct | call_ns | 0 | 8 | 12 | 12 |
| after_vs_direct | operation_ns | 0 | 8 | 10 | 14 |
| before_vs_direct | arrival_ns | 0 | 3 | 6 | 23 |
| before_vs_direct | call_ns | 0 | 15 | 4 | 13 |
| before_vs_direct | operation_ns | 0 | 15 | 3 | 14 |

## codec-w2

The frozen plan has 2 worker(s), target CPUs [2, 3], generator CPUs [0, 1], 241.0 planned calls/s, 67.0 scheduled seconds per process, queue capacity 64, maximum in-flight 256, 1000.0 ms deadline and 100.0 ms generator-lag limit. Warmup is 20.0 s; recovery is 10.0 s at 1.0 call/s; idle observation is 5 s. The exact 160-entry fixed operation sequence and actual dispatch/observation windows are retained per process in JSON. The original service limit is p99 ≤ 500 ms and sampled RSS ≤ 256 MiB.

### Whole-profile resources and counts

| Cohort | Measurement successes | Errors | Sum observation s | Mixed successes/s | Target CPU % of one core | Maximum sampled RSS MiB |
| --- | --- | --- | --- | --- | --- | --- |
| before | 48519 | 0 | 201.313 | 241.013 | 78.594 | 126.047 |
| after | 48519 | 0 | 201.314 | 241.012 | 77.163 | 124.867 |
| direct | 48519 | 0 | 201.314 | 241.012 | 73.924 | 35.629 |
| managed | 48519 | 0 | 201.313 | 241.013 | 65.977 | 151.496 |

The managed row is a resource observation of its complete valid-corpus harness, not a claim that its full semantics or validation cost are equivalent. No row-level CPU attribution is made.

### Public codec call means and original noise decisions

Values are μs. Percent changes use `(new − reference) / reference`; negative call-time changes are faster. AD is selected after versus direct. Managed call means are included only within the stated valid-corpus scope.

| Partition | Before μs | After μs | Direct μs | Managed μs | BA % | Original BA | AD % | Original AD |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| c/a/case-0 (256 B, compressible) | 43.075 | 34.157 | 32.237 | 23.020 | -20.703% | improvement | +5.957% | inconclusive |
| c/o/case-0 (256 B, compressible) | 39.448 | 32.872 | 28.983 | 23.437 | -16.670% | inconclusive | +13.419% | inconclusive |
| d/a/case-0 (256 B, compressible) | 21.911 | 13.342 | 8.174 | 24.601 | -39.111% | improvement | +63.211% | regression |
| d/o/case-0 (256 B, compressible) | 19.761 | 12.504 | 7.978 | 30.070 | -36.724% | improvement | +56.734% | regression |
| c/a/case-1 (256 B, pseudorandom) | 44.156 | 40.429 | 33.575 | 37.787 | -8.440% | inconclusive | +20.414% | regression |
| c/o/case-1 (256 B, pseudorandom) | 39.833 | 36.369 | 32.419 | 40.544 | -8.697% | inconclusive | +12.184% | inconclusive |
| d/a/case-1 (256 B, pseudorandom) | 11.575 | 6.390 | 1.694 | 24.189 | -44.793% | improvement | +277.214% | regression |
| d/o/case-1 (256 B, pseudorandom) | 15.164 | 4.631 | 1.820 | 23.777 | -69.461% | improvement | +154.374% | regression |
| c/a/case-2 (4096 B, compressible) | 50.582 | 44.618 | 38.783 | 26.806 | -11.791% | inconclusive | +15.045% | inconclusive |
| c/o/case-2 (4096 B, compressible) | 51.081 | 40.571 | 39.310 | 29.785 | -20.576% | improvement | +3.207% | inconclusive |
| d/a/case-2 (4096 B, compressible) | 26.275 | 18.958 | 12.858 | 39.216 | -27.848% | improvement | +47.438% | regression |
| d/o/case-2 (4096 B, compressible) | 22.513 | 18.203 | 12.280 | 35.141 | -19.147% | inconclusive | +48.235% | regression |
| c/a/case-3 (4096 B, pseudorandom) | 102.766 | 89.656 | 83.052 | 89.691 | -12.758% | improvement | +7.951% | inconclusive |
| c/o/case-3 (4096 B, pseudorandom) | 93.692 | 84.477 | 80.991 | 96.181 | -9.835% | improvement | +4.304% | inconclusive |
| d/a/case-3 (4096 B, pseudorandom) | 21.296 | 9.002 | 3.799 | 32.360 | -57.730% | improvement | +136.951% | regression |
| d/o/case-3 (4096 B, pseudorandom) | 15.949 | 7.176 | 5.345 | 33.788 | -55.007% | improvement | +34.239% | inconclusive |
| c/a/case-4 (1048576 B, compressible) | 2092.442 | 2040.622 | 2038.861 | 385.937 | -2.477% | inconclusive | +0.086% | within_band |
| c/o/case-4 (1048576 B, compressible) | 1977.134 | 1974.530 | 1996.132 | 369.046 | -0.132% | within_band | -1.082% | within_band |
| d/a/case-4 (1048576 B, compressible) | 1197.563 | 1062.724 | 508.742 | 1100.989 | -11.259% | inconclusive | +108.892% | regression |
| d/o/case-4 (1048576 B, compressible) | 494.162 | 481.062 | 476.501 | 1010.529 | -2.651% | inconclusive | +0.957% | within_band |
| c/a/case-5 (1048576 B, pseudorandom) | 28321.474 | 28161.249 | 27588.050 | 21770.298 | -0.566% | inconclusive | +2.078% | inconclusive |
| c/o/case-5 (1048576 B, pseudorandom) | 27733.270 | 27269.078 | 26970.302 | 21563.478 | -1.674% | inconclusive | +1.108% | inconclusive |
| d/a/case-5 (1048576 B, pseudorandom) | 911.555 | 933.795 | 341.270 | 944.133 | +2.440% | within_band | +173.624% | regression |
| d/o/case-5 (1048576 B, pseudorandom) | 214.494 | 210.616 | 200.994 | 1028.532 | -1.808% | inconclusive | +4.787% | inconclusive |
| c/a/case-6 (4194304 B, compressible) | 7618.645 | 7622.014 | 7579.314 | 1325.020 | +0.044% | inconclusive | +0.563% | inconclusive |
| c/o/case-6 (4194304 B, compressible) | 7956.366 | 7914.325 | 7995.252 | 1333.973 | -0.528% | within_band | -1.012% | inconclusive |
| d/a/case-6 (4194304 B, compressible) | 3893.053 | 3957.603 | 1947.685 | 5403.476 | +1.658% | within_band | +103.195% | regression |
| d/o/case-6 (4194304 B, compressible) | 1843.541 | 1731.830 | 1914.406 | 4748.148 | -6.060% | inconclusive | -9.537% | improvement |
| c/a/case-7 (4194304 B, pseudorandom) | 113591.348 | 111519.465 | 107468.362 | 85377.250 | -1.824% | inconclusive | +3.770% | regression |
| c/o/case-7 (4194304 B, pseudorandom) | 111190.481 | 108780.012 | 108913.717 | 86221.813 | -2.168% | inconclusive | -0.123% | inconclusive |
| d/a/case-7 (4194304 B, pseudorandom) | 3826.876 | 3522.655 | 1174.928 | 3893.350 | -7.950% | inconclusive | +199.819% | regression |
| d/o/case-7 (4194304 B, pseudorandom) | 968.116 | 1051.187 | 943.260 | 3551.522 | +8.581% | inconclusive | +11.442% | inconclusive |

### Full operation and owned lifetime costs

Full operation is public call + consume + release. These means do not replace the separate public-call measure. Managed full-operation ranking is intentionally absent.

| Partition | Before operation μs | After operation μs | Direct operation μs | BA % | Original BA | After consume μs | After release μs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| c/a/case-0 (256 B, compressible) | 43.146 | 34.262 | 32.443 | -20.590% | improvement | 0.105 | 0.000 |
| c/o/case-0 (256 B, compressible) | 40.388 | 33.744 | 29.186 | -16.451% | inconclusive | 0.431 | 0.440 |
| d/a/case-0 (256 B, compressible) | 22.053 | 13.519 | 8.486 | -38.697% | improvement | 0.178 | 0.000 |
| d/o/case-0 (256 B, compressible) | 20.950 | 13.582 | 8.349 | -35.168% | improvement | 0.543 | 0.536 |
| c/a/case-1 (256 B, pseudorandom) | 44.259 | 40.545 | 33.755 | -8.392% | inconclusive | 0.116 | 0.000 |
| c/o/case-1 (256 B, pseudorandom) | 40.743 | 37.405 | 32.621 | -8.194% | inconclusive | 0.386 | 0.650 |
| d/a/case-1 (256 B, pseudorandom) | 11.683 | 6.547 | 1.933 | -43.958% | improvement | 0.157 | 0.000 |
| d/o/case-1 (256 B, pseudorandom) | 16.531 | 5.696 | 2.087 | -65.544% | improvement | 0.559 | 0.506 |
| c/a/case-2 (4096 B, compressible) | 50.664 | 44.736 | 38.984 | -11.699% | inconclusive | 0.119 | 0.000 |
| c/o/case-2 (4096 B, compressible) | 51.962 | 41.482 | 39.488 | -20.169% | improvement | 0.388 | 0.523 |
| d/a/case-2 (4096 B, compressible) | 26.733 | 19.427 | 13.427 | -27.327% | improvement | 0.469 | 0.000 |
| d/o/case-2 (4096 B, compressible) | 23.794 | 19.963 | 12.872 | -16.103% | inconclusive | 1.130 | 0.630 |
| c/a/case-3 (4096 B, pseudorandom) | 103.357 | 90.160 | 83.488 | -12.768% | improvement | 0.504 | 0.000 |
| c/o/case-3 (4096 B, pseudorandom) | 94.907 | 85.708 | 81.402 | -9.692% | improvement | 0.828 | 0.403 |
| d/a/case-3 (4096 B, pseudorandom) | 21.966 | 9.642 | 4.434 | -56.104% | improvement | 0.641 | 0.000 |
| d/o/case-3 (4096 B, pseudorandom) | 17.625 | 8.966 | 6.024 | -49.132% | improvement | 1.088 | 0.702 |
| c/a/case-4 (1048576 B, compressible) | 2093.184 | 2041.262 | 2039.544 | -2.480% | inconclusive | 0.641 | 0.000 |
| c/o/case-4 (1048576 B, compressible) | 1979.002 | 1976.302 | 1996.659 | -0.136% | within_band | 1.129 | 0.644 |
| d/a/case-4 (1048576 B, compressible) | 1291.510 | 1150.204 | 590.729 | -10.941% | inconclusive | 87.480 | 0.000 |
| d/o/case-4 (1048576 B, compressible) | 561.715 | 551.915 | 538.350 | -1.745% | within_band | 69.810 | 1.043 |
| c/a/case-5 (1048576 B, pseudorandom) | 28414.455 | 28251.805 | 27665.011 | -0.572% | inconclusive | 90.556 | 0.000 |
| c/o/case-5 (1048576 B, pseudorandom) | 27850.535 | 27358.265 | 27049.568 | -1.768% | inconclusive | 87.831 | 1.356 |
| d/a/case-5 (1048576 B, pseudorandom) | 989.995 | 1018.412 | 415.812 | +2.870% | within_band | 84.617 | 0.000 |
| d/o/case-5 (1048576 B, pseudorandom) | 270.322 | 265.175 | 240.592 | -1.904% | inconclusive | 53.858 | 0.701 |
| c/a/case-6 (4194304 B, compressible) | 7620.576 | 7623.761 | 7580.956 | +0.042% | inconclusive | 1.747 | 0.000 |
| c/o/case-6 (4194304 B, compressible) | 7959.379 | 7917.292 | 7996.822 | -0.529% | within_band | 2.338 | 0.629 |
| d/a/case-6 (4194304 B, compressible) | 4286.269 | 4395.053 | 2288.807 | +2.538% | inconclusive | 437.450 | 0.000 |
| d/o/case-6 (4194304 B, compressible) | 2150.367 | 2059.143 | 2222.125 | -4.242% | inconclusive | 325.144 | 2.169 |
| c/a/case-7 (4194304 B, pseudorandom) | 113983.683 | 111850.086 | 107906.212 | -1.872% | inconclusive | 330.621 | 0.000 |
| c/o/case-7 (4194304 B, pseudorandom) | 111554.262 | 109130.489 | 109355.123 | -2.173% | inconclusive | 348.785 | 1.692 |
| d/a/case-7 (4194304 B, pseudorandom) | 4213.241 | 3909.777 | 1461.953 | -7.203% | inconclusive | 387.122 | 0.000 |
| d/o/case-7 (4194304 B, pseudorandom) | 1292.517 | 1397.125 | 1207.816 | +8.093% | inconclusive | 344.388 | 1.550 |

### Pooled tails and wall success rates

Call and arrival p99 values below are pooled, descriptive milliseconds. Their percent differences have no separate significance test. Wall success rates are the contribution of each row to the fixed mix. Full p50/p95/p99 and all counters remain in JSON.

| Partition | Call p99 B / A / D ms | Arrival p99 B / A / D ms | Wall successes/s B / A / D |
| --- | --- | --- | --- |
| c/a/case-0 (256 B, compressible) | 0.182 / 0.107 / 0.090 | 30.076 / 29.905 / 29.463 | 15.066 / 15.066 / 15.066 |
| c/o/case-0 (256 B, compressible) | 0.147 / 0.108 / 0.080 | 22.763 / 22.686 / 21.585 | 15.051 / 15.051 / 15.051 |
| d/a/case-0 (256 B, compressible) | 0.118 / 0.046 / 0.027 | 35.231 / 35.565 / 33.840 | 15.051 / 15.051 / 15.051 |
| d/o/case-0 (256 B, compressible) | 0.084 / 0.054 / 0.020 | 12.758 / 13.048 / 11.862 | 15.066 / 15.066 / 15.066 |
| c/a/case-1 (256 B, pseudorandom) | 0.135 / 0.138 / 0.083 | 30.189 / 30.242 / 29.399 | 15.051 / 15.051 / 15.051 |
| c/o/case-1 (256 B, pseudorandom) | 0.129 / 0.128 / 0.090 | 22.373 / 22.559 / 21.396 | 15.066 / 15.066 / 15.066 |
| d/a/case-1 (256 B, pseudorandom) | 0.045 / 0.034 / 0.004 | 25.987 / 26.126 / 25.218 | 15.066 / 15.066 / 15.066 |
| d/o/case-1 (256 B, pseudorandom) | 0.108 / 0.025 / 0.004 | 31.320 / 30.947 / 29.797 | 15.066 / 15.066 / 15.066 |
| c/a/case-2 (4096 B, compressible) | 0.140 / 0.196 / 0.089 | 26.588 / 27.271 / 25.678 | 7.541 / 7.540 / 7.540 |
| c/o/case-2 (4096 B, compressible) | 0.242 / 0.132 / 0.092 | 28.870 / 27.679 / 26.075 | 7.526 / 7.526 / 7.526 |
| d/a/case-2 (4096 B, compressible) | 0.131 / 0.071 / 0.039 | 6.452 / 5.637 / 4.964 | 7.541 / 7.540 / 7.540 |
| d/o/case-2 (4096 B, compressible) | 0.092 / 0.072 / 0.033 | 25.402 / 24.137 / 24.087 | 7.526 / 7.526 / 7.526 |
| c/a/case-3 (4096 B, pseudorandom) | 0.343 / 0.271 / 0.169 | 3.738 / 2.751 / 2.424 | 7.541 / 7.540 / 7.540 |
| c/o/case-3 (4096 B, pseudorandom) | 0.269 / 0.173 / 0.174 | 11.438 / 11.458 / 6.370 | 7.541 / 7.540 / 7.540 |
| d/a/case-3 (4096 B, pseudorandom) | 0.100 / 0.041 / 0.008 | 3.428 / 2.876 / 3.000 | 7.555 / 7.555 / 7.555 |
| d/o/case-3 (4096 B, pseudorandom) | 0.075 / 0.043 / 0.019 | 4.737 / 3.357 / 2.243 | 7.526 / 7.526 / 7.526 |
| c/a/case-4 (1048576 B, compressible) | 4.472 / 3.846 / 3.430 | 20.104 / 19.914 / 16.391 | 6.020 / 6.020 / 6.020 |
| c/o/case-4 (1048576 B, compressible) | 3.593 / 4.130 / 3.644 | 7.979 / 7.481 / 7.079 | 6.035 / 6.035 / 6.035 |
| d/a/case-4 (1048576 B, compressible) | 6.302 / 4.751 / 0.953 | 37.310 / 36.351 / 34.380 | 6.020 / 6.020 / 6.020 |
| d/o/case-4 (1048576 B, compressible) | 0.996 / 0.978 / 0.887 | 13.566 / 12.250 / 10.260 | 6.020 / 6.020 / 6.020 |
| c/a/case-5 (1048576 B, pseudorandom) | 41.211 / 43.011 / 38.426 | 48.499 / 47.155 / 41.230 | 6.020 / 6.020 / 6.020 |
| c/o/case-5 (1048576 B, pseudorandom) | 37.347 / 40.001 / 37.525 | 41.518 / 41.739 / 39.114 | 6.020 / 6.020 / 6.020 |
| d/a/case-5 (1048576 B, pseudorandom) | 4.144 / 3.953 / 1.126 | 6.172 / 6.347 / 2.803 | 6.035 / 6.035 / 6.035 |
| d/o/case-5 (1048576 B, pseudorandom) | 0.513 / 0.533 / 0.418 | 29.523 / 28.627 / 28.231 | 6.020 / 6.020 / 6.020 |
| c/a/case-6 (4194304 B, compressible) | 13.393 / 13.691 / 12.651 | 14.290 / 15.287 / 13.520 | 1.505 / 1.505 / 1.505 |
| c/o/case-6 (4194304 B, compressible) | 13.590 / 12.624 / 13.297 | 23.056 / 22.321 / 20.986 | 1.505 / 1.505 / 1.505 |
| d/a/case-6 (4194304 B, compressible) | 15.559 / 14.127 / 7.411 | 17.075 / 15.791 / 9.963 | 1.505 / 1.505 / 1.505 |
| d/o/case-6 (4194304 B, compressible) | 4.697 / 4.330 / 4.491 | 6.864 / 9.613 / 6.569 | 1.505 / 1.505 / 1.505 |
| c/a/case-7 (4194304 B, pseudorandom) | 150.557 / 140.123 / 128.121 | 152.051 / 141.052 / 129.025 | 1.505 / 1.505 / 1.505 |
| c/o/case-7 (4194304 B, pseudorandom) | 144.256 / 142.251 / 132.419 | 145.114 / 144.226 / 133.569 | 1.505 / 1.505 / 1.505 |
| d/a/case-7 (4194304 B, pseudorandom) | 15.993 / 14.733 / 4.089 | 17.701 / 16.098 / 6.464 | 1.505 / 1.505 / 1.505 |
| d/o/case-7 (4194304 B, pseudorandom) | 3.534 / 4.400 / 1.479 | 15.765 / 12.155 / 3.760 | 1.505 / 1.505 / 1.505 |

### Raw bandwidth, ratio, allocation and derived boundary counts

Bandwidth counts raw input bytes for compression and raw output bytes for decompression. Wall and summed-call MiB/s are deliberately shown separately. Ratios are raw/encoded; managed compression may produce different encoded bytes. Allocation is the public call only; JSON separately preserves allocation including validation.

| Partition | Raw MiB/s wall B / A / D | Raw MiB/s summed-call B / A / D | Raw/encoded A / managed | Allocated B/call B / A | After copied B/call (derived) | After FFI calls/operation (derived) |
| --- | --- | --- | --- | --- | --- | --- |
| c/a/case-0 (256 B, compressible) | 0.004 / 0.004 / 0.004 | 5.668 / 7.148 / 7.573 | 2.349 / 3.241 | 2920.000 / 296.000 | 109.000 | 2.000 |
| c/o/case-0 (256 B, compressible) | 0.004 / 0.004 / 0.004 | 6.189 / 7.427 / 8.424 | 2.349 / 3.241 | 2784.000 / 160.000 | 0.000 | 2.000 |
| d/a/case-0 (256 B, compressible) | 0.004 / 0.004 / 0.004 | 11.142 / 18.299 / 29.866 | 2.349 / 2.349 | 3064.000 / 440.000 | 256.000 | 2.000 |
| d/o/case-0 (256 B, compressible) | 0.004 / 0.004 / 0.004 | 12.355 / 19.525 / 30.602 | 2.349 / 2.349 | 2784.000 / 160.000 | 0.000 | 2.000 |
| c/a/case-1 (256 B, pseudorandom) | 0.004 / 0.004 / 0.004 | 5.529 / 6.039 / 7.271 | 0.959 / 0.959 | 3080.000 / 456.000 | 267.000 | 2.000 |
| c/o/case-1 (256 B, pseudorandom) | 0.004 / 0.004 / 0.004 | 6.129 / 6.713 / 7.531 | 0.959 / 0.959 | 2784.000 / 160.000 | 0.000 | 2.000 |
| d/a/case-1 (256 B, pseudorandom) | 0.004 / 0.004 / 0.004 | 21.092 / 38.205 / 144.113 | 0.959 / 0.959 | 3064.000 / 440.000 | 256.000 | 2.000 |
| d/o/case-1 (256 B, pseudorandom) | 0.004 / 0.004 / 0.004 | 16.100 / 52.721 / 134.108 | 0.959 / 0.959 | 2784.021 / 160.000 | 0.000 | 2.000 |
| c/a/case-2 (4096 B, compressible) | 0.029 / 0.029 / 0.029 | 77.227 / 87.549 / 100.721 | 32.508 / 33.574 | 2936.000 / 312.000 | 126.000 | 2.000 |
| c/o/case-2 (4096 B, compressible) | 0.029 / 0.029 / 0.029 | 76.471 / 96.283 / 99.371 | 32.508 / 33.574 | 2784.000 / 160.000 | 0.000 | 2.000 |
| d/a/case-2 (4096 B, compressible) | 0.029 / 0.029 / 0.029 | 148.666 / 206.045 / 303.789 | 32.508 / 32.508 | 6904.000 / 4280.000 | 4096.000 | 2.000 |
| d/o/case-2 (4096 B, compressible) | 0.029 / 0.029 / 0.029 | 173.509 / 214.597 / 318.106 | 32.508 / 32.508 | 2784.000 / 160.000 | 0.000 | 2.000 |
| c/a/case-3 (4096 B, pseudorandom) | 0.029 / 0.029 / 0.029 | 38.011 / 43.570 / 47.034 | 0.997 / 0.997 | 6920.264 / 4296.000 | 4107.000 | 2.000 |
| c/o/case-3 (4096 B, pseudorandom) | 0.029 / 0.029 / 0.029 | 41.693 / 46.240 / 48.230 | 0.997 / 0.997 | 2784.079 / 160.000 | 0.000 | 2.000 |
| d/a/case-3 (4096 B, pseudorandom) | 0.030 / 0.030 / 0.030 | 183.429 / 433.949 / 1028.247 | 0.997 / 0.997 | 6904.121 / 4280.000 | 4096.000 | 2.000 |
| d/o/case-3 (4096 B, pseudorandom) | 0.029 / 0.029 / 0.029 | 244.927 / 544.371 / 730.759 | 0.997 / 0.997 | 2784.000 / 160.000 | 0.000 | 2.000 |
| c/a/case-4 (1048576 B, compressible) | 6.020 / 6.020 / 6.020 | 477.911 / 490.047 / 490.470 | 331.304 / 144.811 | 5995.294 / 3368.033 | 3165.000 | 2.000 |
| c/o/case-4 (1048576 B, compressible) | 6.035 / 6.035 / 6.035 | 505.783 / 506.450 / 500.969 | 331.304 / 144.811 | 2785.106 / 185.679 | 0.000 | 2.000 |
| d/a/case-4 (1048576 B, compressible) | 6.020 / 6.020 / 6.020 | 835.029 / 940.978 / 1965.632 | 331.304 / 331.304 | 1051408.627 / 1048773.261 | 1048576.000 | 2.000 |
| d/o/case-4 (1048576 B, compressible) | 6.020 / 6.020 / 6.020 | 2023.626 / 2078.733 / 2098.633 | 331.304 / 331.304 | 2787.287 / 183.030 | 0.000 | 2.000 |
| c/a/case-5 (1048576 B, pseudorandom) | 6.020 / 6.020 / 6.020 | 35.309 / 35.510 / 36.248 | 1.000 / 1.000 | 1051564.198 / 1048941.512 | 1048752.000 | 2.000 |
| c/o/case-5 (1048576 B, pseudorandom) | 6.020 / 6.020 / 6.020 | 36.058 / 36.672 / 37.078 | 1.000 / 1.000 | 2784.000 / 160.000 | 0.000 | 2.000 |
| d/a/case-5 (1048576 B, pseudorandom) | 6.035 / 6.035 / 6.035 | 1097.026 / 1070.899 / 2930.232 | 1.000 / 1.000 | 1051384.000 / 1048760.000 | 1048576.000 | 2.000 |
| d/o/case-5 (1048576 B, pseudorandom) | 6.020 / 6.020 / 6.020 | 4662.127 / 4747.970 / 4975.278 | 1.000 / 1.000 | 2790.165 / 162.152 | 0.000 | 2.000 |
| c/a/case-6 (4194304 B, compressible) | 6.020 / 6.020 / 6.020 | 525.028 / 524.796 / 527.752 | 340.696 / 146.757 | 15120.000 / 12496.000 | 12311.000 | 2.000 |
| c/o/case-6 (4194304 B, compressible) | 6.020 / 6.020 / 6.020 | 502.742 / 505.413 / 500.297 | 340.696 / 146.757 | 2833.320 / 198.125 | 0.000 | 2.000 |
| d/a/case-6 (4194304 B, compressible) | 6.020 / 6.020 / 6.020 | 1027.471 / 1010.713 / 2053.720 | 340.696 / 340.696 | 4197134.469 / 4194488.000 | 4194304.000 | 2.000 |
| d/o/case-6 (4194304 B, compressible) | 6.020 / 6.020 / 6.020 | 2169.737 / 2309.696 / 2089.421 | 340.696 / 340.696 | 2784.000 / 160.000 | 0.000 | 2.000 |
| c/a/case-7 (4194304 B, pseudorandom) | 6.020 / 6.020 / 6.020 | 35.214 / 35.868 / 37.220 | 1.000 / 1.000 | 4197863.604 / 4195186.535 | 4194975.000 | 2.000 |
| c/o/case-7 (4194304 B, pseudorandom) | 6.020 / 6.020 / 6.020 | 35.974 / 36.771 / 36.726 | 1.000 / 1.000 | 2820.224 / 213.545 | 0.000 | 2.000 |
| d/a/case-7 (4194304 B, pseudorandom) | 6.020 / 6.020 / 6.020 | 1045.239 / 1135.507 / 3404.465 | 1.000 / 1.000 | 4197112.000 / 4194488.000 | 4194304.000 | 2.000 |
| d/o/case-7 (4194304 B, pseudorandom) | 6.020 / 6.020 / 6.020 | 4131.738 / 3805.222 / 4240.612 | 1.000 / 1.000 | 2784.000 / 160.000 | 0.000 | 2.000 |

### Original independent-process decision counts

| Original family | Mean scope | Improvement | Regression | Within band | Inconclusive |
| --- | --- | --- | --- | --- | --- |
| after_vs_before | arrival_ns | 0 | 0 | 4 | 28 |
| after_vs_before | call_ns | 11 | 0 | 4 | 17 |
| after_vs_before | operation_ns | 11 | 0 | 4 | 17 |
| after_vs_direct | arrival_ns | 0 | 5 | 3 | 24 |
| after_vs_direct | call_ns | 1 | 13 | 3 | 15 |
| after_vs_direct | operation_ns | 1 | 13 | 3 | 15 |
| before_vs_direct | arrival_ns | 0 | 13 | 1 | 18 |
| before_vs_direct | call_ns | 0 | 22 | 3 | 7 |
| before_vs_direct | operation_ns | 0 | 24 | 2 | 6 |

## Correctness, shutdown and limits of this projection

All included original comparison executions completed and their declared commands exited zero and retired. Original per-process validity, service/recovery results, integer phase counts and operation outcomes are retained verbatim from their completed result metadata. This projection does not rerun those checks.

The source-bound common driver runs its preflight before emitting readiness. Native and direct paths check bounded zlib behavior and strict single-stream rejection; every measured successful operation verifies its output bytes in the separately timed consume phase. Native compression matches the frozen encoded corpus and decompression matches the raw corpus; managed compression is checked by a decode round trip because its encoded representation may differ. The comparison reader checked the original byte counts, ledger consistency, ready declarations and drained lifecycle counters. These are descriptions of the bound driver/reader checks, not newly invented per-case booleans: individual over-limit and round-trip test counts were not separately retained in the comparison JSON.

For included NativeWeave processes, recorded native live buffers, retained buffer capacity and active operations are zero at drain. The `released` counter is cumulative, not a measurement-only call count. Direct and managed native counters are unavailable. The configured queue limit is known, but observed queue occupancy, native allocator counts, all internal copying, context switches and async-wakeup counts are unavailable here. No such value is filled with zero.

Network compression is outside this codec experiment. No gRPC/HTTP network compression benefit is inferred. These short fixed-rate observations do not establish the highest sustainable rate, do not replace a 30-minute segment and do not repair or erase another domain’s failed or adverse measurements.

## Provenance and publication boundary

The JSON companion preserves explicit numeric fields, original decisions, version commits, package/native/executable identities, metadata filename/hash provenance, and each process’s recorded raw evidence filename/hash map. Raw evidence contents were not opened to author this report. Absolute paths, operational identity/build maps, PIDs, environment maps, addresses and TLS material are excluded. Unavailable counters remain null/N/A. Metadata hashes in the sources index bind the actual completed inputs; raw hashes are recorded provenance from those inputs, not a fresh payload verification.

- [Complete public numeric projection](comparison-codec-001.json)
- [Source and public file identities](comparison-codec-001.sources.json)

Presentation-only scope: no new acceptance or statistical decision.
