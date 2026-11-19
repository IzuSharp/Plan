# Codec binding proposed for the final Perf-01 freeze

Status: **proposal only**, prepared in the independent Plan audit worktree from
`3715d8eb2a4e5d98f51ed6994dbeefb497d55c53`. This document neither creates the
immutable global freeze nor authorizes a runtime edit or long measurement. No
benchmark, build, test, extractor, or raw-ledger scan was run by this author.

## Actual before-only receipts

The W1 receipt already existed at inspection, so the conditional request to run
its existing extractor was unnecessary. The W2 receipt was produced by the actual
owner after the whole prospective replacement triplet completed. The exact
receipts and small per-process control files are copied without rewriting their
contents under `observations-before/`. The [metadata audit](checks/final-freeze-proposal-001/metadata-audit.json)
records source paths, exact copy hashes, actual counts and the limits of this
inspection. Original event, operation and resource ledgers were not rescanned.

| Stratum | Offered rate | Measurement per process | Actual successful operations in each of 3 processes | Minimum successes in each of 32 rows | Receipt SHA-256 |
| --- | ---: | ---: | ---: | ---: | --- |
| W1 | 134/s | 120 s | 16,095 | 100 | `998e5701b312198e2a91e68ae62070d261e6bc2ae161561b4f9d535aaaf5f83c` |
| W2, whole replacement cohort | 241/s | 67 s | 16,173 | 101 | `749238affbb591e90f5f8801cf952b51e575222c227d8ed07d66b32ab404196b` |

Both groups have three distinct process identities, nonoverlapping windows,
zero unexpected outcomes, successful recovery and target exit, and native
active/capacity/live counters of zero after drain. Actual result, plan and summary
hashes agree with the existing receipt. W1 whole-process p99 values are
126.411708, 131.175493 and 154.254477 ms; W2 values are 111.844453, 116.555985 and
112.880009 ms. These are different before-only load strata, not before/after
improvement claims. Target peak sampled RSS is at most 82,137,088 bytes for W1
and 108,556,288 bytes for W2; the receipts retain every process value.

Receipt copies:

- [W1](observations-before/codec-before004-w1-noise-001/noise.json)
- [W2 at 241/s](observations-before/codec-before004-w2-r241-noise-001/noise.json)

The original owner ran W2 process 1. The resumed owner ran processes 2 and 3 and
the existing extractor, all with recorded exit 0. Their actual argv, timestamps,
logs and hashes are in Plan commit `411bd7757cfe2972eee51d146012685bd90c9771`,
`checks/recovery-codec-w2-r241-remaining-001/execution.json`. Root must integrate
that receipt. The noise creation timestamps alone are not substituted for this
execution history or for publishing the bands before candidate timing.

## Unchanged comparison contract

Use W1 `workers=1, rate=134, duration=120` and W2
`workers=2, rate=241, duration=67` for the three fresh before/after/direct processes
per route, disjoint from noise calibration. The existing
[short-cohort recipe](codec-short-cohorts-linux.md) supplies the driver and
interleaving; this proposal explicitly supersedes its historical W2=268/s,
60-second scalar values. Its older W1 smoke remains diagnostic history. Do not
reuse the failed W2 process or join favorable processes from different cohorts.

| Setting | Same values for both short strata and all matching routes |
| --- | --- |
| Producer / actual before source | `package-before-004/manifest.json`; `ea5fa528035d025bd7a28698ee7c71194432236c` |
| Before manifest SHA-256 | `d34298ebc8dc82b525f19860555947a1a04eff2bf8aecc38cede2922c81285a7` |
| Codec driver SHA-256 | `95e15eb609dc761e9de95bcef5b1bb84af9fcc3711ecdf5632ad6e34856c0165` |
| A21 SHA-256 | `dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53` |
| Extractor SHA-256 | `6f09ac17bc60544ef97c147a47cada66344f6ea068318821f204da0a6e468663` |
| Corpus SHA-256 | `92932f7ecba2b3a7104b19344d22a42c3c40605f23eb158a0941d48bfff0465d` |
| Data seed / operation cycle | 2654435769; unchanged complete 160-operation cycle |
| Format / level / checksum | zlib / 6 / Adler32 |
| Raw / decoded / encoded byte limits | 4,194,304 / 4,194,304 / 4,259,840 |
| Actions / interfaces / cases | mixed compression and decompression / mixed arrays and ownership / all 8 cases |
| Queue / in flight | 64 / 256 |
| Target / generator CPUs | 2,3 / 0,1 |
| Warmup / recovery / short idle | 20 s / 10 s at 1 operation/s / 5 s |
| Deadline / allowed generator lag | 1000 ms / 100 ms |
| Service limits | zero unexpected errors; whole-process p99 at most 500 ms; sampled target RSS at most 256 MiB |

The direct executable remains the exact before manifest's original miniz_oxide
producer. Managed ZLibStream observations retain their existing narrower scope.
The immutable future after package manifest will be supplied only after an
actual build and the required regressions. Do not insert fictitious hashes or
rewrite the frozen before or noise metadata. Standalone codec measurements do
not establish network compression; gRPC remains identity only.

## Prospective paired long load: 192/s

Commit `23bea899c95d92fffac965d7b059c461af1cb0ab` declared the complete W2
replacement rule before those replacement samples: `floor(0.9 * 268)=241`,
with three fresh full processes, and `floor(0.8 * 241)=192` for the paired long
load if all three passed. The [original command arrays](codec-before004-w2-stepdown-commands.json)
and [selection proposal](observations-before/codec-before004-w2-r241-noise-001/paired-long-selection-proposal.json)
bind the actual qualifying receipt. There is no new capacity claim.

Preserve the original 268/s cell as valid but service-failing: 16,105 of 16,108
operations succeeded and 3 were rejected by the bounded target queue. Preserve
the actual 384/s capacity result, which used warmup 5 s and recovery 4 s, and its
307/s proposed long calculation. The unchanged original
[307/s command document](codec-before004-long-commands.json) is historical; the
final-freeze proposal selects the new [192/s command document](codec-before004-r241-long-commands.json).
Neither short anchor proves a successful long segment.

The prospective long arguments remain two workers, 1802 requested seconds,
20-second warmup, 10-second recovery at 1/s, 60-second idle, and all common
limits/mix/CPU masks. Exact schedule arithmetic is:

| Field | Value |
| --- | ---: |
| Integer period | 5,208,333 ns |
| Planned measurement operations | 346,005 |
| First-to-last scheduled span | 1,802,104,051,332 ns |
| Separate warmup operations | 3,861 |
| Separate recovery operations | 12 |
| Total planned operations across phases | 349,878 |

The existing driver determines actual dispatch/completion and correctness. The
post-run verifier must independently establish both the ordinary-success
`D-C >= 1800 s` bound and actual dispatch span at least 1800 s. All long accepted
seconds remain zero in this proposal. Stop, retain and classify any failed or
interrupted segment; no nominal schedule duration creates acceptance credit.
