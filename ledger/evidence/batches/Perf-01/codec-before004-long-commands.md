# Before-004 codec long-load commands

Status: **planned commands only; not executed**. Root runs these two existing
command arrays only after the global Perf-01 freeze is committed and the
exclusive measurement resource is clear. The companion
[JSON document](codec-before004-long-commands.json) contains the complete
measurement argv and separate post-run verification argv, with absolute paths
and source/producer/selection pins. It adds no controller or driver behavior.

The completed [before-004 calibration](observations-before/codec-final004-calibration/README.md)
selected 384 operations/s and the paired long rate **307/s**. This command uses
that selected rate with **two workers**, the complete 160-operation mixed cycle,
both actions and interfaces, and the unchanged eight-payload corpus. The W1/W2
short noise rates remain separate.

## Commands and immutable inputs

Source `ROOT/perf01-toolchain/env.sh` in the root execution environment first.
The measurement argv begins with
`/usr/bin/flock --nonblock ROOT/perf01-evidence/timing.lock`, then `taskset -c 2,3`
and the exact Python 3.12.14 executable. It calls only the existing
`tests/Perf01.Codec/driver.py run`, with generator CPUs 0,1. Lock contention
prevents startup and is an orchestration result, not an application error.

| Input | Exact identity |
| --- | --- |
| Before product commit | `ea5fa528035d025bd7a28698ee7c71194432236c` |
| Driver producer commit | `aa3399f0418a6d0910cc56697abfaa3769f32b54` |
| Before-004 manifest SHA-256 | `d34298ebc8dc82b525f19860555947a1a04eff2bf8aecc38cede2922c81285a7` |
| Corpus manifest SHA-256 | `92932f7ecba2b3a7104b19344d22a42c3c40605f23eb158a0941d48bfff0465d` |
| Final capacity selection SHA-256 | `b08ea7b9816e9f55f78c8fe3dd292d6705142ceb1153fff6500702a0e7922ef5` |
| Final capacity controller SHA-256 | `c92ccaef5ffb5b37ccf6c9ac61b9d19f6e96bddbde0311153c411ec2d9323876` |
| Codec driver SHA-256 | `95e15eb609dc761e9de95bcef5b1bb84af9fcc3711ecdf5632ad6e34856c0165` |
| A21 SHA-256 | `dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53` |
| Separate main verifier SHA-256 | `3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82` |

The JSON records all nine codec inventory hashes, environment/policy hashes and
the producer's actual package/executable/native digests. Only source and small
metadata were read during this preparation. No binary, payload or raw-ledger
scan was performed. The unchanged driver verifies prepared artifacts, consumer
inputs and corpus bytes before startup and records the actual loaded native
library. Keep those identities intact; do not edit an old manifest.

## Frozen long configuration and planned counts

| Setting | Value |
| --- | --- |
| Rate / workers | 307 operations/s / 2 |
| Requested measurement / dispatch guard | 1,802 seconds / existing 0.1 second |
| Integer period | 3,257,329 ns |
| Measurement operations | 553,246 |
| Planned first-to-last schedule span | 1,802,100,982,605 ns |
| Warmup | 20 seconds; 6,172 operations |
| Recovery | 10 seconds at 1/s; 12 operations in the same live process |
| Separate idle observation | 60 seconds |
| Queue / pending bound | 64 / 256 |
| Deadline / maximum generator dispatch lag | 1,000 ms / 100 ms |
| Service standard | Zero unexpected errors; whole-measurement arrival p99 at most 500 ms; sampled target RSS at most 256 MiB |

Counts use the unchanged scheduler formula
`ceil((seconds + 0.1) * 1e9 / period_ns) + 1`. Warmup, measurement and recovery
total 559,430 planned operations. These are source calculations, not actual
dispatch/completion observations or duration credit.

The measurement output is
`ROOT/perf01-evidence/long/before/codec-001`. After its target exits, run the
separate main `tests/Perf01/verify_long.py` on CPU 8 with `--group codec`; the
new receipt path is
`ROOT/perf01-evidence/long/before/codec-001-verification.json`. Both paths must
be fresh. Stop on failure or interruption, retain all partial evidence and
verify target shutdown before another load. Neither command is an unattended
retry policy.

## Required actual evidence

A zero driver exit alone is insufficient. Require valid/complete/service/recovery
flags, complete expected phase counts, zero unexpected outcomes, correct payload
and limit checks, actual native identity and fixed affinity. The measured
dispatch span must reach the requested 1,802 seconds. Require one correct drain
record with zero native live owners, capacity and active calls, no target
correctness errors, the full separately timed idle interval and zero target exit.

The common verifier must return zero and `accepted=true`, reconcile the full
hashed operation/event/resource ledgers, preserve recovery and all original
service limits, and prove at least 1,800 seconds from the earliest successful
ordinary-operation completion to the last ordinary dispatch, as well as at
least 1,800 seconds of original dispatch span. Nominal schedule length does not
prove acceptance. Preserve its exact source hash and the complete receipt.

The eventual after command must keep this driver/A21/corpus, selected rate,
workers, schedule, CPU masks, limits, phases and outer lock. Its actual after
producer and fresh output are bound separately after that build exists. No
after identity or command is invented here. This document earns zero long-run
acceptance credit.

## Independent source review

The database subagent passed a bounded independent source/metadata review of
both argv arrays, this configuration and the count arithmetic. It checked all
15 source/small-metadata pins and both final selection/controller pins against
current bytes. The reviewed command JSON SHA-256 is
`3f1dcae40457ed147efc1c5125555e6eaa8863b72d1209eac0064af3417dad32`.
Neither author nor reviewer executed a command from this document, a test,
build or workload, or scanned a binary, payload or raw ledger.
