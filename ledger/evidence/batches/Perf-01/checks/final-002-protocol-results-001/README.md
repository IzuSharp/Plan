# Perf-01 final002 protocol numerical checkpoint

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
| http1-small / http-tiny / 0 / 1 | before | validated | 5.366 | 10.27 | 0 |
| http1-small / http-tiny / 0 / 1 | after | validated | 5.366 | 12.96 | 0 |
| http1-small / http-tiny / 0 / 1 | direct | validated | 5.366 | 5.677 | 0 |
| http1-small / http-upload / 1048576 / 1 | before | validated | 5.316 | 20.21 | 0 |
| http1-small / http-upload / 1048576 / 1 | after | validated | 5.316 | 19.11 | 0 |
| http1-small / http-upload / 1048576 / 1 | direct | validated | 5.316 | 7.077 | 0 |
| http1-small / http-download / 1048576 / 1 | before | validated | 5.366 | 20.88 | 0 |
| http1-small / http-download / 1048576 / 1 | after | validated | 5.366 | 9.858 | 0 |
| http1-small / http-download / 1048576 / 1 | direct | validated | 5.366 | 6.721 | 0 |
| http2-small / http-tiny / 0 / 1 | before | validated | 5.366 | 12.46 | 0 |
| http2-small / http-tiny / 0 / 1 | after | validated | 5.366 | 5.384 | 0 |
| http2-small / http-tiny / 0 / 1 | direct | validated | 5.366 | 3.639 | 0 |
| http2-small / http-upload / 1048576 / 1 | before | validated | 5.316 | 26.96 | 0 |
| http2-small / http-upload / 1048576 / 1 | after | validated | 5.316 | 27.9 | 0 |
| http2-small / http-upload / 1048576 / 1 | direct | validated | 5.316 | 12.91 | 0 |
| http2-small / http-download / 1048576 / 1 | before | validated | 5.366 | 17.63 | 0 |
| http2-small / http-download / 1048576 / 1 | after | validated | 5.366 | 19.25 | 0 |
| http2-small / http-download / 1048576 / 1 | direct | validated | 5.366 | 8.15 | 0 |
| http1-large / http-upload / 8388608 / 1 | before | validated | 4.014 | 75.27 | 0 |
| http1-large / http-upload / 8388608 / 1 | after | validated | 4.01 | 75.68 | 0 |
| http1-large / http-upload / 8388608 / 1 | direct | validated | 4.015 | 31.65 | 0 |
| http1-large / http-download / 8388608 / 1 | before | validated | 4.014 | 112.5 | 0 |
| http1-large / http-download / 8388608 / 1 | after | validated | 4.01 | 94.66 | 0 |
| http1-large / http-download / 8388608 / 1 | direct | validated | 4.015 | 36.17 | 0 |
| http2-large / http-upload / 8388608 / 1 | before | validated | 4.012 | 104.5 | 0 |
| http2-large / http-upload / 8388608 / 1 | after | validated | 4.013 | 69.09 | 0 |
| http2-large / http-upload / 8388608 / 1 | direct | validated | 4.014 | 61.16 | 0 |
| http2-large / http-download / 8388608 / 1 | before | validated | 4.012 | 82.39 | 0 |
| http2-large / http-download / 8388608 / 1 | after | validated | 4.013 | 74.34 | 0 |
| http2-large / http-download / 8388608 / 1 | direct | validated | 4.014 | 45.21 | 0 |
| grpc-unary / grpc-unary / 64 / 1 | before | validated | 8.048 | 41.17 | 0 |
| grpc-unary / grpc-unary / 64 / 1 | after | validated | 8.047 | 49.54 | 0 |
| grpc-unary / grpc-unary / 64 / 1 | direct | validated | 8.049 | 4.551 | 0 |
| grpc-unary / grpc-unary / 65536 / 1 | before | validated | 7.998 | 47.23 | 0 |
| grpc-unary / grpc-unary / 65536 / 1 | after | validated | 7.997 | 46.61 | 0 |
| grpc-unary / grpc-unary / 65536 / 1 | direct | validated | 7.999 | 6.403 | 0 |
| grpc-streams / grpc-server / 4096 / 32 | before | validated | 5.357 | 166.9 | 0 |
| grpc-streams / grpc-server / 4096 / 32 | after | validated | 5.361 | 194.5 | 0 |
| grpc-streams / grpc-server / 4096 / 32 | direct | validated | 5.366 | 15.83 | 0 |
| grpc-streams / grpc-client / 4096 / 32 | before | validated | 5.307 | 113.5 | 0 |
| grpc-streams / grpc-client / 4096 / 32 | after | validated | 5.311 | 126.7 | 0 |
| grpc-streams / grpc-client / 4096 / 32 | direct | validated | 5.316 | 18.78 | 0 |
| grpc-streams / grpc-duplex / 4096 / 32 | before | validated | 5.357 | 257.9 | 0 |
| grpc-streams / grpc-duplex / 4096 / 32 | after | validated | 5.361 | 227.5 | 0 |
| grpc-streams / grpc-duplex / 4096 / 32 | direct | validated | 5.366 | 19.32 | 0 |

### Protocol changes and direct Rust gaps

| Profile / scenario / bytes | p99 after−before ms | p99 after−before % | p99 before−direct % | p99 after−direct % | Success/s after−before | Mean-noise decision |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| http1-small / http-tiny / 0 | 2.696 | 26.26 | 80.86 | 128.3 | 4.564e-05 | inconclusive |
| http1-small / http-upload / 1048576 | -1.1 | -5.442 | 185.6 | 170 | 4.522e-05 | within_band |
| http1-small / http-download / 1048576 | -11.02 | -52.79 | 210.7 | 46.67 | 4.564e-05 | inconclusive |
| http2-small / http-tiny / 0 | -7.078 | -56.8 | 242.4 | 47.95 | 0.0001203 | inconclusive |
| http2-small / http-upload / 1048576 | 0.9435 | 3.5 | 108.8 | 116.1 | 0.0001192 | inconclusive |
| http2-small / http-download / 1048576 | 1.615 | 9.161 | 116.4 | 136.2 | 0.0001203 | within_band |
| http1-large / http-upload / 8388608 | 0.405 | 0.5381 | 137.9 | 139.1 | -0.004311 | inconclusive |
| http1-large / http-download / 8388608 | -17.84 | -15.86 | 211 | 161.7 | -0.004311 | inconclusive |
| http2-large / http-upload / 8388608 | -35.46 | -33.91 | 70.93 | 12.96 | 0.0002024 | within_band |
| http2-large / http-download / 8388608 | -8.059 | -9.781 | 82.26 | 64.44 | 0.0002024 | inconclusive |
| grpc-unary / grpc-unary / 64 | 8.368 | 20.33 | 804.7 | 988.6 | -0.001213 | inconclusive |
| grpc-unary / grpc-unary / 65536 | -0.6255 | -1.324 | 637.7 | 627.9 | -0.001205 | inconclusive |
| grpc-streams / grpc-server / 4096 | 27.63 | 16.56 | 954.1 | 1129 | 0.004013 | inconclusive |
| grpc-streams / grpc-client / 4096 | 13.2 | 11.63 | 504.1 | 574.4 | 0.003976 | within_band |
| grpc-streams / grpc-duplex / 4096 | -30.39 | -11.78 | 1235 | 1078 | 0.004013 | inconclusive |

### Whole-profile protocol resources

These means describe three complete mixed-profile server processes, not an individual path; per-process clients, generators and managed GC remain in JSON.

| Profile | Role | Status | Server CPU % one core | Server peak RSS MiB (mean) | Allocated MiB (sample delta mean) | Gen2 delta (mean) |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| http1-small | before | validated | 6.774 | 66.9 | 130.8 | 8 |
| http1-small | after | validated | 6.548 | 66.88 | 27.44 | 1 |
| http1-small | direct | validated | 1.136 | 12.62 | N/A | N/A |
| http2-small | before | validated | 8.468 | 67.65 | 130.8 | 8 |
| http2-small | after | validated | 7.824 | 67.48 | 27.52 | 1 |
| http2-small | direct | validated | 1.783 | 12.94 | N/A | N/A |
| http1-large | before | validated | 23.93 | 67.04 | 259.4 | 9.333 |
| http1-large | after | validated | 23.12 | 67.14 | 145.8 | 1 |
| http1-large | direct | validated | 6.045 | 12.58 | N/A | N/A |
| http2-large | before | validated | 32.27 | 67.56 | 268.2 | 9.333 |
| http2-large | after | validated | 32.03 | 67.66 | 146.7 | 1 |
| http2-large | direct | validated | 8.711 | 12.93 | N/A | N/A |
| grpc-unary | before | validated | 4.673 | 58.58 | 341.3 | 31.33 |
| grpc-unary | after | validated | 4.329 | 51.36 | 341.7 | 36.33 |
| grpc-unary | direct | validated | 0.5767 | 13.17 | N/A | N/A |
| grpc-streams | before | validated | 16.2 | 62.52 | 6828 | 551 |
| grpc-streams | after | validated | 12.34 | 88.26 | 423.8 | 35 |
| grpc-streams | direct | validated | 1.135 | 13.09 | N/A | N/A |


## Evidence boundary

The adjacent numeric files preserve source/package/native identities, every selected-stage observation, deltas, noise and resource scope. Every original report-bound input read by this checkpoint is hash-checked through the unchanged projector; no database raw journal is opened by protocol, codec or capacity selection. The actual input hashes, original projector hash and this wrapper hash are recorded separately. Other domains and all ten long acceptance records remain separate.

## Interrupted attempt and fixed continuation

This checkpoint combines 52 immutable completed original cells with exactly two fresh suffix cells, final-repetition after then direct Rust. The original interrupted after attempt remains preserved with zero acceptance credit. The original controller and its five completed reports are unchanged; the three streaming triplets use the separately completed continuation controller and its original-reader report. The adjacent coverage records both controller hashes, the retained-prefix hash, interrupted evidence hashes and separate helper/projector identities. It does not describe this as one uninterrupted original controller execution.
