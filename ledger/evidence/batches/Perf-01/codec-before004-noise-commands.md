# Before-004 codec noise commands

Status: **source preparation only**. No command below has been executed by this
document's author. The root integration owner runs one cell at a time in the
exclusive measurement window and records its actual argv, timestamps, exit and
evidence location. The companion
[command arrays](codec-before004-noise-commands.json) contain six complete
measurement argv arrays and two complete `codec_compare.py freeze` argv arrays,
using absolute workspace paths. They are data for the existing execution
ledger, not a new controller or unattended script.

This concretizes the approved
[short-cohort recipe](codec-short-cohorts-linux.md). The final
[before-004 producer](builds/before-codec-004/README.md) replaces the older
producer reference in the historical short-selection note. The selected short
rates remain W1=134/s and W2=268/s; the later 384/s capacity and 307/s long-load
selection do not retune these fixed-load noise cohorts.

## Exact inputs

Before dispatch, source
`/workspace/scratch/01c249676f47/perf01-toolchain/env.sh` in the root's execution
environment. The arrays use Python 3.12.14 at
`/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3`.
The runtime is clean main `ea5fa528035d025bd7a28698ee7c71194432236c`; the driver
producer is `aa3399f0418a6d0910cc56697abfaa3769f32b54`.

| Input | SHA-256 |
| --- | --- |
| `perf01-codec-checks/package-before-004/manifest.json` | `d34298ebc8dc82b525f19860555947a1a04eff2bf8aecc38cede2922c81285a7` |
| `perf01-codec-checks/corpus/manifest.json` | `92932f7ecba2b3a7104b19344d22a42c3c40605f23eb158a0941d48bfff0465d` |
| `tests/Perf01.Codec/driver.py` | `95e15eb609dc761e9de95bcef5b1bb84af9fcc3711ecdf5632ad6e34856c0165` |
| `src/Benchmarks.Harness/nativeweave_bench.py` | `dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53` |
| `codec_compare.py` | `6f09ac17bc60544ef97c147a47cada66344f6ea068318821f204da0a6e468663` |

These small metadata/source inputs and the complete nine-file codec driver
inventory were read and hash-checked while preparing the arrays. Binaries and
payload files were not scanned again. Their producer hashes are unchanged in
the manifest; the existing driver checks them, all consumer inputs and actual
loaded native mappings before measurement. The companion JSON also records the
complete driver inventory and the executable/native hashes from that manifest.
An unrelated product Git HEAD change is not substituted for these exact source
and artifact bindings.

## Six cells and two freezes

Every measurement uses target CPUs 2,3, generator CPUs 0,1, the full mixed corpus,
queue 64, pending limit 256, a 1,000 ms deadline and 100 ms dispatch-lag bound.
Warmup is 20 seconds; recovery is 10 seconds at 1/s; short idle observation is
five seconds. Every output path must be new.

| Command IDs | Workers | Rate (/s) | Measurement (s) | Planned measurement / warmup / recovery counts | Output directories under `ROOT/perf01-evidence/noise/` |
| --- | ---: | ---: | ---: | --- | --- |
| `codec-before004-w1-noise-1` through `-3` | 1 | 134 | 120 | 16,095 / 2,695 / 12 | `codec-before004-w1/noise-1`, `noise-2`, `noise-3` |
| `codec-before004-w2-noise-1` through `-3` | 2 | 268 | 60 | 16,108 / 5,388 / 12 | `codec-before004-w2/noise-1`, `noise-2`, `noise-3` |

The counts are schedule arithmetic from the existing 100 ms guard and rounded
periods, not observations. Run the six measurement arrays in their listed
order. Stop on any failed or interrupted cell, retain its evidence, and verify
shutdown before reusing the resource. No automatic retry or overwrite is
introduced.

After measurements stop, the two freeze arrays run the existing extractor on
CPU 8. Each names only its own three completed before cells, before-004 build
manifest, corpus **manifest file**, exact A21 source, a 1,000 ns analysis floor,
500 ms whole-cell p99 and 256 MiB sampled target RSS limit. Their outputs are:

- `ROOT/perf01-evidence/noise/codec-before004-w1/noise.json`
- `ROOT/perf01-evidence/noise/codec-before004-w2/noise.json`

## Expected checks and resulting evidence

Require a zero driver exit, valid and complete result, successful service and
recovery, no invalid reasons, full declared dispatch span and complete phase
counts. Actual measurement successes must equal the planned count and be at
least 16,000; all 32 groups must have `successes == offered >= 100` and a
non-null p99. Require the frozen global latency/RSS/dispatch-lag limits, expected
affinity, actual native identity, AOT readiness, zero native owners/capacity/
active calls at drain, completed short idle and zero target exit. Keep each
`plan.json`, `result.json`, `summary.json`, `operations.jsonl`, `events.jsonl`,
`resources.jsonl`, command and affinity-restoration record.

Successful extraction independently reconciles raw hashes, clocks, phase and
row counts, summary tails, sampled resources and ownership. It requires three
distinct process identities and disjoint measurement windows with the same
within-stratum contract. The noise band remains the existing per-row/metric
maximum of 1,000 ns and the range of the three before process means, with zero
relative band. Record and commit each actual `noise.json` SHA before any later
confirmation/candidate observations. W1 and W2 receipts remain separate; neither
the capacity confirmations nor the earlier W1 smoke replaces these new cells.

These short cells and freezes receive zero 30-minute acceptance credit.
