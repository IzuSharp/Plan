# Perf-01 frozen before-only protocol noise

This directory preserves the exact completed index, controller and six noise receipts
from `ROOT/perf01-evidence/protocol-short/noise-before-001`. Root executed the
18 serial fresh processes and the existing extractor before product changes.
This archival task only read/copied small metadata on CPU 8; it did not rerun an
extractor, workload, test, build, or raw-ledger scan. `copy-manifest.json` records
every original path, byte count and SHA-256. The index and controller are
byte-identical at completion.

**Future comparison index pin:** `af9b4a68014c231fbc8c6b3e651a310045e155d83bd06d1bd9cbf4fe3b5bed20`. Pass it with the original
index path to `protocol_cohorts.py --stage compare --noise-index ...
--noise-index-sha256 ...`; preserve every per-profile receipt hash below.
Fresh before/after/direct comparison processes must remain disjoint from these
calibration instances, retain the frozen profile/client/fixture/source identities,
and run after noise creation. This receipt is not a comparison result or long
duration acceptance.

Actual cohort interval: **2026-11-19T13:42:22.523649+00:00 to 2026-11-19T13:54:18.039915+00:00**.
All 18 cells are completed, valid and service-qualified in the saved index and
eligible in the six saved extractor receipts. All observed checks in these
partitions are ordinary business successes; expected probes are absent.

## Eighteen actual process counts

Each row is derived from the saved per-scenario offered/successful counts, not
from the planned formula. All cells used C4; small HTTP/gRPC partitions used
16/s for 20 scheduled seconds, and 8 MiB HTTP partitions used 8/s for 30 seconds.
Warmup 24, recovery 32 and idle 5 seconds are separate from these counts.

| Profile | Repetition | Offered | Ordinary successful calls | Successful per-scenario counts |
| --- | ---: | ---: | ---: | --- |
| http1-small | 0 | 323 | 323 | download=108, tiny=108, upload=107 |
| http1-small | 1 | 323 | 323 | download=108, tiny=108, upload=107 |
| http1-small | 2 | 323 | 323 | download=108, tiny=108, upload=107 |
| http2-small | 0 | 323 | 323 | download=108, tiny=108, upload=107 |
| http2-small | 1 | 323 | 323 | download=108, tiny=108, upload=107 |
| http2-small | 2 | 323 | 323 | download=108, tiny=108, upload=107 |
| http1-large | 0 | 242 | 242 | download=121, upload=121 |
| http1-large | 1 | 242 | 242 | download=121, upload=121 |
| http1-large | 2 | 242 | 242 | download=121, upload=121 |
| http2-large | 0 | 242 | 242 | download=121, upload=121 |
| http2-large | 1 | 242 | 242 | download=121, upload=121 |
| http2-large | 2 | 242 | 242 | download=121, upload=121 |
| grpc-unary | 0 | 323 | 323 | unary/64=162, unary/65536=161 |
| grpc-unary | 1 | 323 | 323 | unary/64=162, unary/65536=161 |
| grpc-unary | 2 | 323 | 323 | unary/64=162, unary/65536=161 |
| grpc-streams | 0 | 323 | 323 | client=107, duplex=108, server=108 |
| grpc-streams | 1 | 323 | 323 | client=107, duplex=108, server=108 |
| grpc-streams | 2 | 323 | 323 | client=107, duplex=108, server=108 |

**Total actual ordinary successful calls: 5,328.**
Every per-process scenario has at least 100 successful observations. The
full precision timing/resource/build identities remain in the individual
noise receipts; this table grants no new raw correctness verification.

## Frozen bands

The unchanged method is `max(1000 ns, range of three before process ordinary
arrival means)` with relative noise 0. The table displays milliseconds rounded
for reading; the exact floating-point nanosecond values in each copied JSON
are the authoritative frozen inputs. These bands apply only to their exact
profile/arrival/CPU/fixture/source cohort, not another concurrency, mixed long
profile or scenario measured alone. A21 noise comparison operates on independent
process means; these are not p99 confidence intervals.

| Profile | Full scenario key | Absolute noise (ms) |
| --- | --- | ---: |
| http1-small | `http-download\|http1-tls\|1048576\|1` | 0.457137 |
| http1-small | `http-tiny\|http1-tls\|0\|1` | 0.127014 |
| http1-small | `http-upload\|http1-tls\|1048576\|1` | 1.648245 |
| http2-small | `http-download\|http2-tls\|1048576\|1` | 1.216725 |
| http2-small | `http-tiny\|http2-tls\|0\|1` | 0.278419 |
| http2-small | `http-upload\|http2-tls\|1048576\|1` | 1.152756 |
| http1-large | `http-download\|http1-tls\|8388608\|1` | 1.469172 |
| http1-large | `http-upload\|http1-tls\|8388608\|1` | 1.733077 |
| http2-large | `http-download\|http2-tls\|8388608\|1` | 1.982778 |
| http2-large | `http-upload\|http2-tls\|8388608\|1` | 4.508969 |
| grpc-unary | `grpc-unary\|http2-tls\|64\|1` | 2.308949 |
| grpc-unary | `grpc-unary\|http2-tls\|65536\|1` | 2.213313 |
| grpc-streams | `grpc-client\|http2-tls\|4096\|32` | 9.475813 |
| grpc-streams | `grpc-duplex\|http2-tls\|4096\|32` | 16.214745 |
| grpc-streams | `grpc-server\|http2-tls\|4096\|32` | 9.445655 |

## Exact per-profile noise receipt pins

| Profile | SHA-256 |
| --- | --- |
| http1-small | `45590c6849fb4f4f93b3ccf9d439ccf9cb6cc54edbe900252431e4b42dc605a3` |
| http2-small | `ca615ff73f4cd798cb69c587af7584b409f2bf9457fabe65007ac4780395a6ca` |
| http1-large | `1891b31cc1500f4475e3357ebcb49cdbb1ad6f6f6093f2b9f8e9ca039a2b8c68` |
| http2-large | `7b20a095372659db098fb23c13ada5bd459bd5649365a1b8b4815ca2adb4f5af` |
| grpc-unary | `98077f898c6947e0611734bcc7a286c2bd250bfe5694d627ba9162fa504bd892` |
| grpc-streams | `651608f1f1c6d7ab59a1e1758f45cd26e1cafc834bd05f5142ae14013830de81` |

The common before producer is clean main `ea5fa528035d025bd7a28698ee7c71194432236c`,
with build/common-client manifest SHA-256
`818643898f04803f3070cb55f6bf0894dc23c1f9c21ff7d556a8e99b6b96d8c3`.
The generic Rust comparator is frozen by producer manifest
`0f6fb40d3310e873231276527ffac3621980981b719b6fc438ee03e5fdf1bdbf`;
no direct or after measurements contributed to these bands. Extractor, A21,
bounded-reader, profile, actual loaded-native and client executable pins are
preserved inside every receipt. TLS paths/hashes are metadata only; no key or
certificate contents were copied.

## Independent saved-evidence review

The codec reviewer passed a bounded small-metadata/source review. All eight
retained data files matched the copy manifest and original small-file bytes;
the six receipt pins matched the index. The reviewer checked 18 distinct
server PID/start identities with disjoint windows, all actual per-scenario
counts, the 5,328-call total, at least 100 observations per row, and all 15
bands against the three saved process means. No raw ledger was rescanned and
no extractor, test, build or workload was rerun. The exact copied JSON bytes
remain unchanged after review.
