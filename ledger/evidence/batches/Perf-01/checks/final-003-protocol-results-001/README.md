# Perf-01 final003 protocol numerical checkpoint

This partial-domain report reuses the exact existing fixed-matrix projector and its unchanged domain validators. All fixed cells for the named stage are retained. Other domains are not evaluated by this checkpoint; whole-matrix completion is not claimed.

| Domain inventory | Expected | Terminal | Evidence validated | Service eligible |
| --- | ---: | ---: | ---: | ---: |
| protocol | 54 | 54 | 54 | 54 |

Complete selected-stage evidence: **true**. No workload or long-duration credit is produced.

DB/protocol aggregate tails are means of process percentiles; codec aggregate tails are pooled. Original A21 decisions concern independent process means, while tail and throughput changes are descriptive. Resources belong to whole processes. Ineligible, invalid, incomplete and missing observations retain their original distinctions.

## Protocol ordinary paths

All protocols use real TLS sockets. These 15 ordinary short scenarios exclude expected cancellation/deadline probes; the retained mixed capacity and long evidence covers those controls. Whole-profile server/client/controller/adapter CPU, RSS and managed GC remain separate from scenario rows.

| Profile / scenario / bytes / messages | Role | Status | Success/s | p99 ms | Unexpected errors |
| --- | --- | --- | ---: | ---: | ---: |
| http1-small / http-tiny / 0 / 1 | before | validated | 5.366 | 8.059 | 0 |
| http1-small / http-tiny / 0 / 1 | after | validated | 5.366 | 6.966 | 0 |
| http1-small / http-tiny / 0 / 1 | direct | validated | 5.365 | 17.85 | 0 |
| http1-small / http-upload / 1048576 / 1 | before | validated | 5.316 | 13 | 0 |
| http1-small / http-upload / 1048576 / 1 | after | validated | 5.316 | 11.94 | 0 |
| http1-small / http-upload / 1048576 / 1 | direct | validated | 5.316 | 10.05 | 0 |
| http1-small / http-download / 1048576 / 1 | before | validated | 5.366 | 10.81 | 0 |
| http1-small / http-download / 1048576 / 1 | after | validated | 5.366 | 11.92 | 0 |
| http1-small / http-download / 1048576 / 1 | direct | validated | 5.365 | 12.98 | 0 |
| http2-small / http-tiny / 0 / 1 | before | validated | 5.366 | 4.843 | 0 |
| http2-small / http-tiny / 0 / 1 | after | validated | 5.366 | 5.925 | 0 |
| http2-small / http-tiny / 0 / 1 | direct | validated | 5.366 | 9.616 | 0 |
| http2-small / http-upload / 1048576 / 1 | before | validated | 5.316 | 20.2 | 0 |
| http2-small / http-upload / 1048576 / 1 | after | validated | 5.316 | 17.98 | 0 |
| http2-small / http-upload / 1048576 / 1 | direct | validated | 5.316 | 11.05 | 0 |
| http2-small / http-download / 1048576 / 1 | before | validated | 5.366 | 16 | 0 |
| http2-small / http-download / 1048576 / 1 | after | validated | 5.366 | 17.92 | 0 |
| http2-small / http-download / 1048576 / 1 | direct | validated | 5.366 | 12.56 | 0 |
| http1-large / http-upload / 8388608 / 1 | before | validated | 4.014 | 90.26 | 0 |
| http1-large / http-upload / 8388608 / 1 | after | validated | 4.014 | 77.27 | 0 |
| http1-large / http-upload / 8388608 / 1 | direct | validated | 4.015 | 47.14 | 0 |
| http1-large / http-download / 8388608 / 1 | before | validated | 4.014 | 91.93 | 0 |
| http1-large / http-download / 8388608 / 1 | after | validated | 4.014 | 80.58 | 0 |
| http1-large / http-download / 8388608 / 1 | direct | validated | 4.015 | 37.03 | 0 |
| http2-large / http-upload / 8388608 / 1 | before | validated | 4.013 | 87.23 | 0 |
| http2-large / http-upload / 8388608 / 1 | after | validated | 4.014 | 86.65 | 0 |
| http2-large / http-upload / 8388608 / 1 | direct | validated | 4.014 | 64.29 | 0 |
| http2-large / http-download / 8388608 / 1 | before | validated | 4.013 | 63.83 | 0 |
| http2-large / http-download / 8388608 / 1 | after | validated | 4.014 | 53.53 | 0 |
| http2-large / http-download / 8388608 / 1 | direct | validated | 4.014 | 34.1 | 0 |
| grpc-unary / grpc-unary / 64 / 1 | before | validated | 8.043 | 37.94 | 0 |
| grpc-unary / grpc-unary / 64 / 1 | after | validated | 8.045 | 49.67 | 0 |
| grpc-unary / grpc-unary / 64 / 1 | direct | validated | 8.049 | 8.253 | 0 |
| grpc-unary / grpc-unary / 65536 / 1 | before | validated | 7.994 | 36.39 | 0 |
| grpc-unary / grpc-unary / 65536 / 1 | after | validated | 7.995 | 47.98 | 0 |
| grpc-unary / grpc-unary / 65536 / 1 | direct | validated | 7.999 | 18.68 | 0 |
| grpc-streams / grpc-server / 4096 / 32 | before | validated | 5.357 | 178 | 0 |
| grpc-streams / grpc-server / 4096 / 32 | after | validated | 5.361 | 154.5 | 0 |
| grpc-streams / grpc-server / 4096 / 32 | direct | validated | 5.366 | 6.917 | 0 |
| grpc-streams / grpc-client / 4096 / 32 | before | validated | 5.308 | 103.4 | 0 |
| grpc-streams / grpc-client / 4096 / 32 | after | validated | 5.311 | 124.2 | 0 |
| grpc-streams / grpc-client / 4096 / 32 | direct | validated | 5.316 | 8.655 | 0 |
| grpc-streams / grpc-duplex / 4096 / 32 | before | validated | 5.357 | 250.7 | 0 |
| grpc-streams / grpc-duplex / 4096 / 32 | after | validated | 5.361 | 186.5 | 0 |
| grpc-streams / grpc-duplex / 4096 / 32 | direct | validated | 5.366 | 14.58 | 0 |

### Protocol changes and direct Rust gaps

| Profile / scenario / bytes | p99 after−before ms | p99 after−before % | p99 before−direct % | p99 after−direct % | Success/s after−before | Mean-noise decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| http1-small / http-tiny / 0 | -1.093 | -13.56 | -54.85 | -60.98 | -5.421e-05 | inconclusive |
| http1-small / http-upload / 1048576 | -1.064 | -8.181 | 29.4 | 18.82 | -5.37e-05 | within_band |
| http1-small / http-download / 1048576 | 1.115 | 10.31 | -16.7 | -8.114 | -5.421e-05 | inconclusive |
| http2-small / http-tiny / 0 | 1.082 | 22.34 | -49.64 | -38.38 | 0.0002158 | within_band |
| http2-small / http-upload / 1048576 | -2.213 | -10.96 | 82.79 | 62.76 | 0.0002138 | within_band |
| http2-small / http-download / 1048576 | 1.917 | 11.98 | 27.42 | 42.69 | 0.0002158 | within_band |
| http1-large / http-upload / 8388608 | -12.99 | -14.39 | 91.48 | 63.93 | -0.0003461 | inconclusive |
| http1-large / http-download / 8388608 | -11.35 | -12.35 | 148.2 | 117.6 | -0.0003461 | improvement |
| http2-large / http-upload / 8388608 | -0.5881 | -0.6742 | 35.69 | 34.78 | 7.926e-05 | within_band |
| http2-large / http-download / 8388608 | -10.31 | -16.15 | 87.19 | 56.96 | 7.926e-05 | within_band |
| grpc-unary / grpc-unary / 64 | 11.73 | 30.92 | 359.7 | 501.9 | 0.001168 | inconclusive |
| grpc-unary / grpc-unary / 65536 | 11.59 | 31.86 | 94.83 | 156.9 | 0.001161 | inconclusive |
| grpc-streams / grpc-server / 4096 | -23.45 | -13.18 | 2473 | 2134 | 0.003638 | inconclusive |
| grpc-streams / grpc-client / 4096 | 20.72 | 20.03 | 1095 | 1335 | 0.003605 | within_band |
| grpc-streams / grpc-duplex / 4096 | -64.22 | -25.61 | 1620 | 1180 | 0.003638 | inconclusive |

### Whole-profile protocol resources

These means describe three complete mixed-profile server processes, not an individual path; per-process clients, generators and managed GC remain in JSON.

| Profile | Role | Status | Server CPU % one core | Server peak RSS MiB (mean) | Allocated MiB (sample delta mean) | Gen2 delta (mean) |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| http1-small | before | validated | 7.04 | 66.88 | 130.9 | 8 |
| http1-small | after | validated | 6.412 | 66.94 | 27.56 | 1 |
| http1-small | direct | validated | 1.222 | 12.59 | N/A | N/A |
| http2-small | before | validated | 8.522 | 67.61 | 130.9 | 8 |
| http2-small | after | validated | 8.363 | 67.88 | 27.5 | 1 |
| http2-small | direct | validated | 1.869 | 12.95 | N/A | N/A |
| http1-large | before | validated | 25.78 | 67.24 | 259.4 | 9.667 |
| http1-large | after | validated | 24.97 | 67.3 | 147.2 | 1 |
| http1-large | direct | validated | 6.264 | 12.55 | N/A | N/A |
| http2-large | before | validated | 33.38 | 68.12 | 266.7 | 11.33 |
| http2-large | after | validated | 32.4 | 67.77 | 147.5 | 1 |
| http2-large | direct | validated | 8.651 | 12.94 | N/A | N/A |
| grpc-unary | before | validated | 4.104 | 64.03 | 339.8 | 31 |
| grpc-unary | after | validated | 4.798 | 50.92 | 341.7 | 35.67 |
| grpc-unary | direct | validated | 0.5765 | 13.13 | N/A | N/A |
| grpc-streams | before | validated | 17.52 | 60.48 | 6959 | 576.3 |
| grpc-streams | after | validated | 12.07 | 89.73 | 424.8 | 37.67 |
| grpc-streams | direct | validated | 0.9778 | 13.07 | N/A | N/A |


## Evidence boundary

The adjacent numeric files preserve source/package/native identities, every selected-stage observation, deltas, noise and resource scope. Every original report-bound input read by this checkpoint is hash-checked through the unchanged projector; no database raw journal is opened by protocol, codec or capacity selection. The actual input hashes, original projector hash and this wrapper hash are recorded separately. Other domains and all ten long acceptance records remain separate.
