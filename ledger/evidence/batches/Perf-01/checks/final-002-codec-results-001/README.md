# Perf-01 final002 codec numerical checkpoint

This partial-domain report reuses the exact existing fixed-matrix projector and its unchanged domain validators. All fixed cells for the named stage are retained. Other domains are not evaluated by this checkpoint; whole-matrix completion is not claimed.

| Domain inventory | Expected | Terminal | Evidence validated | Service eligible |
| --- | ---: | ---: | ---: | ---: |
| codec_w1 | 12 | 12 | 12 | 12 |
| codec_w2 | 12 | 12 | 12 | 12 |

Complete selected-stage evidence: **true**. No workload or long-duration credit is produced.

DB/protocol aggregate tails are means of process percentiles; codec aggregate tails are pooled. Original A21 decisions concern independent process means, while tail and throughput changes are descriptive. Resources belong to whole processes. Ineligible, invalid, incomplete and missing observations retain their original distinctions.

## Codec

Raw MiB/s uses the complete observation wall denominator. Summed-call MiB/s is separate in JSON. Managed ZLibStream is a valid-corpus call-only supplement; its owned label aliases arrays and is not ranked for full arrival/ownership semantics. Process allocation/copy counters retain their original derived/observed distinction.

| Workers / case / action / interface | Before MiB/s | After MiB/s | Direct MiB/s | Before p99 ms | After p99 ms | p99 Δ % | After vs direct p99 % | Call-mean decision | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1 / 0 / compress / array | 0.002043 | 0.002043 | 0.002043 | 134 | 122.9 | -8.3 | 4.884 | inconclusive | validated |
| 1 / 0 / compress / owned | 0.002047 | 0.002047 | 0.002047 | 96.42 | 95 | -1.476 | 12.57 | inconclusive | validated |
| 1 / 0 / decompress / array | 0.002043 | 0.002043 | 0.002043 | 127.9 | 113 | -11.67 | 8.109 | improvement | validated |
| 1 / 0 / decompress / owned | 0.002047 | 0.002047 | 0.002047 | 104.4 | 97.54 | -6.612 | 8.32 | improvement | validated |
| 1 / 1 / compress / array | 0.002043 | 0.002043 | 0.002043 | 143.6 | 131.4 | -8.522 | 10.45 | improvement | validated |
| 1 / 1 / compress / owned | 0.002047 | 0.002047 | 0.002047 | 110.5 | 102 | -7.714 | 6.745 | inconclusive | validated |
| 1 / 1 / decompress / array | 0.002039 | 0.002039 | 0.002039 | 86.15 | 69.81 | -18.96 | 22.84 | improvement | validated |
| 1 / 1 / decompress / owned | 0.002047 | 0.002047 | 0.002047 | 113.7 | 112.6 | -1.012 | 14.17 | improvement | validated |
| 1 / 2 / compress / array | 0.01629 | 0.01629 | 0.01629 | 116.3 | 104.7 | -9.945 | 11.05 | inconclusive | validated |
| 1 / 2 / compress / owned | 0.01636 | 0.01636 | 0.01636 | 121.1 | 116.5 | -3.805 | 12.31 | inconclusive | validated |
| 1 / 2 / decompress / array | 0.01639 | 0.01639 | 0.01639 | 122.6 | 121.7 | -0.7905 | 7.949 | within_band | validated |
| 1 / 2 / decompress / owned | 0.01636 | 0.01636 | 0.01636 | 128.6 | 129.1 | 0.4026 | 7.482 | inconclusive | validated |
| 1 / 3 / compress / array | 0.01633 | 0.01633 | 0.01633 | 37.48 | 19.52 | -47.93 | 192.2 | inconclusive | validated |
| 1 / 3 / compress / owned | 0.01639 | 0.01639 | 0.01639 | 111.7 | 85.66 | -23.3 | 7.492 | within_band | validated |
| 1 / 3 / decompress / array | 0.01639 | 0.01639 | 0.01639 | 30.39 | 23.65 | -22.17 | 18.42 | improvement | validated |
| 1 / 3 / decompress / owned | 0.01633 | 0.01633 | 0.01633 | 42.48 | 35.06 | -17.46 | 45.57 | inconclusive | validated |
| 1 / 4 / compress / array | 3.355 | 3.355 | 3.355 | 73.35 | 51.64 | -29.6 | 26.77 | within_band | validated |
| 1 / 4 / compress / owned | 3.355 | 3.355 | 3.355 | 25.18 | 18.64 | -25.99 | 81.42 | inconclusive | validated |
| 1 / 4 / decompress / array | 3.355 | 3.355 | 3.355 | 130 | 131.7 | 1.304 | 8.516 | within_band | validated |
| 1 / 4 / decompress / owned | 3.347 | 3.347 | 3.347 | 138.4 | 114.5 | -17.25 | 2.951 | inconclusive | validated |
| 1 / 5 / compress / array | 3.339 | 3.339 | 3.339 | 158.8 | 136.2 | -14.24 | 8.408 | within_band | validated |
| 1 / 5 / compress / owned | 3.364 | 3.364 | 3.364 | 136.2 | 136.3 | 0.1021 | 6.465 | within_band | validated |
| 1 / 5 / decompress / array | 3.355 | 3.355 | 3.355 | 19.33 | 10.87 | -43.79 | 24.66 | inconclusive | validated |
| 1 / 5 / decompress / owned | 3.355 | 3.355 | 3.355 | 100.9 | 84.73 | -16.06 | 13.36 | within_band | validated |
| 1 / 6 / compress / array | 3.364 | 3.364 | 3.364 | 25.58 | 21.48 | -16.01 | 19.52 | within_band | validated |
| 1 / 6 / compress / owned | 3.364 | 3.364 | 3.364 | 34.95 | 47.68 | 36.43 | 33.95 | inconclusive | validated |
| 1 / 6 / decompress / array | 3.33 | 3.33 | 3.33 | 47.33 | 37.77 | -20.2 | 65.91 | inconclusive | validated |
| 1 / 6 / decompress / owned | 3.33 | 3.33 | 3.33 | 13.98 | 15.49 | 10.79 | 50.75 | within_band | validated |
| 1 / 7 / compress / array | 3.364 | 3.364 | 3.364 | 210 | 158.4 | -24.59 | 3.624 | within_band | validated |
| 1 / 7 / compress / owned | 3.33 | 3.33 | 3.33 | 201.9 | 151.9 | -24.79 | 3.199 | inconclusive | validated |
| 1 / 7 / decompress / array | 3.364 | 3.364 | 3.364 | 40.14 | 37.59 | -6.354 | 55.44 | within_band | validated |
| 1 / 7 / decompress / owned | 3.33 | 3.33 | 3.33 | 135.4 | 82.97 | -38.74 | 10.54 | within_band | validated |
| 2 / 0 / compress / array | 0.003678 | 0.003678 | 0.003678 | 35.43 | 35.43 | 0.002024 | 17.56 | inconclusive | validated |
| 2 / 0 / compress / owned | 0.003675 | 0.003675 | 0.003675 | 38.53 | 27.67 | -28.19 | 23.79 | inconclusive | validated |
| 2 / 0 / decompress / array | 0.003675 | 0.003675 | 0.003675 | 50.33 | 45.33 | -9.931 | 21.12 | improvement | validated |
| 2 / 0 / decompress / owned | 0.003678 | 0.003678 | 0.003678 | 35.39 | 23.12 | -34.69 | 42.43 | within_band | validated |
| 2 / 1 / compress / array | 0.003675 | 0.003675 | 0.003675 | 47.85 | 42.5 | -11.18 | 29.52 | inconclusive | validated |
| 2 / 1 / compress / owned | 0.003678 | 0.003678 | 0.003678 | 37.28 | 34.87 | -6.465 | 48.52 | improvement | validated |
| 2 / 1 / decompress / array | 0.003678 | 0.003678 | 0.003678 | 41.99 | 34.95 | -16.76 | 33.21 | inconclusive | validated |
| 2 / 1 / decompress / owned | 0.003678 | 0.003678 | 0.003678 | 45.84 | 34.4 | -24.96 | 12.18 | inconclusive | validated |
| 2 / 2 / compress / array | 0.02945 | 0.02946 | 0.02945 | 33.57 | 37.12 | 10.57 | 30.71 | inconclusive | validated |
| 2 / 2 / compress / owned | 0.0294 | 0.0294 | 0.0294 | 45.53 | 36.81 | -19.15 | 35.36 | inconclusive | validated |
| 2 / 2 / decompress / array | 0.02945 | 0.02946 | 0.02945 | 30.26 | 24.49 | -19.06 | 142.8 | inconclusive | validated |
| 2 / 2 / decompress / owned | 0.0294 | 0.0294 | 0.0294 | 37.67 | 31.81 | -15.57 | 10.4 | inconclusive | validated |
| 2 / 3 / compress / array | 0.02945 | 0.02946 | 0.02945 | 29.8 | 19.28 | -35.32 | 295 | inconclusive | validated |
| 2 / 3 / compress / owned | 0.02945 | 0.02946 | 0.02945 | 51.64 | 42.56 | -17.59 | 143.8 | inconclusive | validated |
| 2 / 3 / decompress / array | 0.02951 | 0.02951 | 0.02951 | 34.23 | 13.87 | -59.48 | 139 | inconclusive | validated |
| 2 / 3 / decompress / owned | 0.0294 | 0.0294 | 0.0294 | 36.92 | 22.77 | -38.32 | 337.1 | within_band | validated |
| 2 / 4 / compress / array | 6.02 | 6.02 | 6.02 | 51.98 | 37.2 | -28.45 | 43.13 | within_band | validated |
| 2 / 4 / compress / owned | 6.035 | 6.035 | 6.035 | 39.43 | 27.86 | -29.35 | 147.6 | within_band | validated |
| 2 / 4 / decompress / array | 6.02 | 6.02 | 6.02 | 50.99 | 46.49 | -8.825 | 30.14 | inconclusive | validated |
| 2 / 4 / decompress / owned | 6.02 | 6.02 | 6.02 | 36.33 | 29.88 | -17.74 | 109.2 | inconclusive | validated |
| 2 / 5 / compress / array | 6.02 | 6.02 | 6.02 | 81.2 | 74.47 | -8.285 | 33.88 | within_band | validated |
| 2 / 5 / compress / owned | 6.02 | 6.02 | 6.02 | 70.11 | 57.04 | -18.64 | 16.1 | within_band | validated |
| 2 / 5 / decompress / array | 6.035 | 6.035 | 6.035 | 30.14 | 14.71 | -51.19 | 125.3 | inconclusive | validated |
| 2 / 5 / decompress / owned | 6.02 | 6.02 | 6.02 | 52.68 | 43.14 | -18.11 | 26.22 | inconclusive | validated |
| 2 / 6 / compress / array | 6.02 | 6.02 | 6.02 | 53.6 | 23.8 | -55.61 | 8.769 | inconclusive | validated |
| 2 / 6 / compress / owned | 6.02 | 6.02 | 6.02 | 69.62 | 41.29 | -40.69 | 28.23 | within_band | validated |
| 2 / 6 / decompress / array | 6.02 | 6.02 | 6.02 | 64.71 | 31.6 | -51.16 | 116.3 | inconclusive | validated |
| 2 / 6 / decompress / owned | 6.02 | 6.02 | 6.02 | 41.48 | 21.17 | -48.97 | 97.71 | inconclusive | validated |
| 2 / 7 / compress / array | 6.02 | 6.02 | 6.02 | 196.8 | 189.1 | -3.916 | 28.88 | inconclusive | validated |
| 2 / 7 / compress / owned | 6.02 | 6.02 | 6.02 | 165.7 | 168.8 | 1.902 | 6.613 | within_band | validated |
| 2 / 7 / decompress / array | 6.02 | 6.02 | 6.02 | 74.89 | 32.71 | -56.32 | 143.8 | inconclusive | validated |
| 2 / 7 / decompress / owned | 6.02 | 6.02 | 6.02 | 54.12 | 49.26 | -8.979 | 224.5 | inconclusive | validated |

### Whole mixed codec resources

CPU uses summed process CPU divided by summed observation time. RSS is the maximum observed process peak. These values are not assigned to individual codec partitions.

| Workers | Role | Status | CPU % one core | Peak RSS MiB | Errors |
| ---: | --- | --- | ---: | ---: | ---: |
| 1 | before | validated | 45.16 | 93.99 | 0 |
| 1 | after | validated | 44.25 | 77.49 | 0 |
| 1 | direct | validated | 41.25 | 29.18 | 0 |
| 1 | managed | validated | 43.27 | 117.1 | 0 |
| 2 | before | validated | 81.63 | 123.1 | 0 |
| 2 | after | validated | 80.56 | 126.2 | 0 |
| 2 | direct | validated | 79.52 | 35.56 | 0 |
| 2 | managed | validated | 74.31 | 174.7 | 0 |


## Evidence boundary

The adjacent numeric files preserve source/package/native identities, every selected-stage observation, deltas, noise and resource scope. Every original report-bound input read by this checkpoint is hash-checked through the unchanged projector; no database raw journal is opened by protocol, codec or capacity selection. The actual input hashes, original projector hash and this wrapper hash are recorded separately. Other domains and all ten long acceptance records remain separate.
