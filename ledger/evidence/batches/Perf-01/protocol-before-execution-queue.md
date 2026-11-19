# Perf-01 remaining before protocol execution queue

Source-prepared commands only. Execute after DB session 50107 has ended, root has
cleared the measurement resource, integrated the reviewed protocol/verifier
commits, and passed the finite gates. This document creates no new controller or
load matrix. Root owns the entire queue, including extraction between cells.

## Fixed inputs

```bash
PERF01_ROOT=/workspace/scratch/01c249676f47
source "$PERF01_ROOT/perf01-toolchain/env.sh"
PERF01_NW="$PERF01_ROOT/.worktree/Perf-01-linux/NativeWeave"
PERF01_PLAN="$PERF01_ROOT/.worktree/Perf-01-linux/Plan"
PERF01_E="$PERF01_PLAN/ledger/evidence/batches/Perf-01"
PERF01_PYTHON=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
PERF01_BEFORE="$PERF01_ROOT/perf01-build/before/protocols-v2/build.json"
PERF01_DIRECT="$PERF01_ROOT/perf01-build/direct/protocols-v3/build.json"
PERF01_CERT="$PERF01_ROOT/perf01-evidence/functional/before-grpc-001/certificate.pem"
PERF01_KEY="$PERF01_ROOT/perf01-evidence/functional/before-grpc-001/private-key.pem"
PERF01_LOCK="$PERF01_ROOT/perf01-evidence/timing.lock"
PERF01_NOISE="$PERF01_ROOT/perf01-evidence/protocol-short/noise-before-001"
```

The following small metadata/source/TLS files were hash-checked during this
source-only preparation. Executable/native hashes are taken from those pinned
producer manifests; existing `prepare` rechecks the actual artifacts before use.

| Input | SHA-256 |
|---|---|
| Before/common-client `build.json` | `818643898f04803f3070cb55f6bf0894dc23c1f9c21ff7d556a8e99b6b96d8c3` |
| Common client executable | `acb1c163cd51e291f58dbe51ae12c04f82c2b51538aa36e446a05890e06aadd0` |
| Before server executable | `5ba1df0946ece4a490d7bb43b295b7c720c3d32159c7e47e0cd28f0a3098460d` |
| Before loaded Server native library | `4827a6ecc76f871e0b4828f4ff6fe23a0d0a4ca1c57c5fc89a10a8e4d83ffe69` |
| Direct `build.json` | `0f6fb40d3310e873231276527ffac3621980981b719b6fc438ee03e5fdf1bdbf` |
| Certificate PEM | `9c5c88b63e03a095061b6af052a3c8aa714a96bcf3a01fde9124bbd781b57b35` |
| Private-key PEM, local bytes only | `c9238030f5a0b9c7352007b3edca6ca75b92a85291e7d56d8918e2ee3dbd789a` |
| `prospective-policy.json` revision 4 | `0c7cd866b1ad0fc86d647e31dd1b6fe0b148d2e7ca54d83b7286cec09f11cafc` |
| `protocol_calibrate.py` | `32db840b1ec8374d66086b298e53055aed9ee9c9e71d2e5f54c6295ae8d039b7` |
| `protocol_cohorts.py` | `1aa0ca003d0cdc9af00d8c09bac52f0224dd7f74883f7b410724a74e576e0702` |
| `protocol_compare.py` | `a8cead371ceed5b2d6a865c1e6b113110005db7880af7566d5125f46429c032f` |
| `protocol-layered/catalog.json` | `1cbd2faff27e1158fef07b88740567a24711112e9b6b67947813a9cf10f4b787` |

Before runtime source remains `ea5fa528035d025bd7a28698ee7c71194432236c`.
Protocol driver `run.py` is `ee5867cfd5c29b52595b96a69328fc612c88ebdd38fd5796ed7582102c4c49b4`;
A21 is `dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53`.
The final protocol noise stage must see the reviewed post-run reader
`3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82` in main
before recording its source contract. Keep those relevant driver/reader/profile
bytes unchanged through the matched short cohorts. The separate frozen DB
timing checkout retains its original parser; it is not this protocol input.

## 1. Fresh final before HTTP and gRPC calibration

```bash
taskset -c 2,3 "$PERF01_PYTHON" "$PERF01_E/protocol_calibrate.py" \
  --nativeweave "$PERF01_NW" \
  --policy "$PERF01_E/prospective-policy.json" \
  --policy-sha256 0c7cd866b1ad0fc86d647e31dd1b6fe0b148d2e7ca54d83b7286cec09f11cafc \
  --build "$PERF01_BEFORE" \
  --build-sha256 818643898f04803f3070cb55f6bf0894dc23c1f9c21ff7d556a8e99b6b96d8c3 \
  --client-build "$PERF01_BEFORE" \
  --client-build-sha256 818643898f04803f3070cb55f6bf0894dc23c1f9c21ff7d556a8e99b6b96d8c3 \
  --certificate "$PERF01_CERT" --private-key "$PERF01_KEY" \
  --exclusive-lock "$PERF01_LOCK" --variant before --groups http grpc \
  --attempt v5 --output-root "$PERF01_ROOT/perf01-evidence/calibration"
```

Outputs are `calibration/before-http-v5/selection.json` and
`calibration/before-grpc-v5/selection.json`, with their original controller,
per-cell commands, results and failures. The existing wrapper preserves the
30-second ladder/refinement and three complete 60-second confirmations at 64
slots. Only `exit == 0`, completed, valid and service-qualified cells can select
a point. Each selection's `long_rate` is the before-only
`max(1, min(500, floor(0.8 * selected_rate)))`. Record the actual selection and
controller hashes in the final freeze; no rate is supplied by this recipe.

If only one group remains, use that single `--groups` value. Output directories
were absent at preparation; an interrupted attempt stays immutable and requires
a fresh label after root verifies descendant cleanup. The thin calibration
wrapper's documented interruption ownership limits remain in effect.

## 2. Six C4 before-only noise triplets and extraction

```bash
taskset -c 8 "$PERF01_PYTHON" "$PERF01_E/protocol_cohorts.py" \
  --stage noise --nativeweave "$PERF01_NW" \
  --catalog "$PERF01_E/protocol-layered/catalog.json" \
  --before-build "$PERF01_BEFORE" --direct-build "$PERF01_DIRECT" \
  --client-build "$PERF01_BEFORE" \
  --certificate "$PERF01_CERT" --private-key "$PERF01_KEY" \
  --exclusive-lock "$PERF01_LOCK" --output "$PERF01_NOISE"
```

The existing controller runs this exact catalog order and invokes the existing
`protocol_compare.py freeze-noise` after each completed triplet:

| Partition | Rate/s | Seconds per process | Processes | Planned minimum per row if all succeed |
|---|---:|---:|---:|---:|
| `http1-small` | 16 | 20 | 3 | 107 |
| `http2-small` | 16 | 20 | 3 | 107 |
| `http1-large` | 8 | 30 | 3 | 121 |
| `http2-large` | 8 | 30 | 3 | 121 |
| `grpc-unary` | 16 | 20 | 3 | 161 |
| `grpc-streams` | 16 | 20 | 3 | 107 |

This is **18 fresh before processes and 420 scheduled seconds**, plus separate
warmup/recovery/idle. Each process uses 24 warmup calls, 32 recovery calls and
five-second idle. Small HTTP partitions contain tiny/1 MiB upload/download;
large ones contain completed 8 MiB upload/download. The gRPC partitions retain
both unary sizes and all three streaming cardinalities with identity encoding.
The ordinary-only partitions are distinct from the mixed capacity/long profiles.
The table contains planned populations; actual successful observations and every
original acceptance check remain required before reporting a p99 or noise band.

Actual cell paths are `$PERF01_NOISE/PARTITION/{0,1,2}-before`. Each extraction
is `$PERF01_NOISE/PARTITION/noise/noise.json`; the completed aggregate is
`$PERF01_NOISE/noise-index.json`. The direct manifest is pinned at freeze, but no
direct timings affect before-only noise. A failed cell stops this controller;
do not replace it by selecting favorable prior rows. Preserve the prescribed
whole triplet and any failed/partial attempts.

For an already completed explicit triplet whose extraction alone needs a new
output directory, the exact existing extractor form is:

```bash
PERF01_PARTITION=http1-small
taskset -c 8 "$PERF01_PYTHON" "$PERF01_E/protocol_compare.py" \
  --nativeweave "$PERF01_NW" \
  --output "$PERF01_NOISE/$PERF01_PARTITION/noise-reextract-001" \
  freeze-noise \
  --before "$PERF01_NOISE/$PERF01_PARTITION/0-before" \
           "$PERF01_NOISE/$PERF01_PARTITION/1-before" \
           "$PERF01_NOISE/$PERF01_PARTITION/2-before" \
  --direct-build "$PERF01_DIRECT" \
  --direct-build-sha256 0f6fb40d3310e873231276527ffac3621980981b719b6fc438ee03e5fdf1bdbf
```

Normal successful orchestration already performed that extraction; do not run
it a second time. After these before-only measurements, commit the actual six
noise receipts and aggregate index/hash to Plan before runtime edits or candidate
observations. Later comparisons use the
exact committed `--noise-index-sha256`, the same source contract and three fresh
interleaved processes per route; noise-calibration processes are not reused as
the fresh comparison triplet. No future hash or measured value is invented here.

## 3. Eventual paired long-load before commands

Run these one group at a time only after root commits the complete final freeze.
Read each actual v5 selection's `long_rate`; preserve that same rate for after.
The original mixed profiles below explicitly retain **idle 60 seconds, warmup
24 and recovery 32**. These are profile fields, not extra `prepare` flags. Do not
use calibration's generated `profile-short.json` for a long run.

```bash
PERF01_HTTP_RATE="$(taskset -c 8 "$PERF01_PYTHON" -c 'import json,sys; print(json.load(open(sys.argv[1]))["long_rate"])' \
  "$PERF01_ROOT/perf01-evidence/calibration/before-http-v5/selection.json")"
PERF01_HTTP_LONG="$PERF01_ROOT/perf01-evidence/long/before-http-001"
taskset -c 2,3 "$PERF01_PYTHON" "$PERF01_NW/tests/Perf01.Protocols/run.py" prepare \
  --build "$PERF01_BEFORE" --client-build "$PERF01_BEFORE" \
  --profile "$PERF01_NW/tests/Perf01.Protocols/profile-v1.json" \
  --group http --rate "$PERF01_HTTP_RATE" --duration 1802 --concurrency 64 \
  --generator-cpus 0,1 --certificate "$PERF01_CERT" --private-key "$PERF01_KEY" \
  --output "$PERF01_HTTP_LONG"
taskset -c 2,3 "$PERF01_PYTHON" "$PERF01_NW/tests/Perf01.Protocols/run.py" run \
  --plan "$PERF01_HTTP_LONG/plan.json" --exclusive-lock "$PERF01_LOCK"
taskset -c 8 "$PERF01_PYTHON" "$PERF01_NW/tests/Perf01/verify_long.py" \
  --group http --output "$PERF01_HTTP_LONG" --receipt "$PERF01_HTTP_LONG/long-verification.json"
```

After that process tree has stopped and its result is preserved:

```bash
PERF01_GRPC_RATE="$(taskset -c 8 "$PERF01_PYTHON" -c 'import json,sys; print(json.load(open(sys.argv[1]))["long_rate"])' \
  "$PERF01_ROOT/perf01-evidence/calibration/before-grpc-v5/selection.json")"
PERF01_GRPC_LONG="$PERF01_ROOT/perf01-evidence/long/before-grpc-001"
taskset -c 2,3 "$PERF01_PYTHON" "$PERF01_NW/tests/Perf01.Protocols/run.py" prepare \
  --build "$PERF01_BEFORE" --client-build "$PERF01_BEFORE" \
  --profile "$PERF01_E/grpc-budget-profile-v2.json" \
  --group grpc --rate "$PERF01_GRPC_RATE" --duration 1802 --concurrency 64 \
  --generator-cpus 0,1 --certificate "$PERF01_CERT" --private-key "$PERF01_KEY" \
  --output "$PERF01_GRPC_LONG"
taskset -c 2,3 "$PERF01_PYTHON" "$PERF01_NW/tests/Perf01.Protocols/run.py" run \
  --plan "$PERF01_GRPC_LONG/plan.json" --exclusive-lock "$PERF01_LOCK"
taskset -c 8 "$PERF01_PYTHON" "$PERF01_NW/tests/Perf01/verify_long.py" \
  --group grpc --output "$PERF01_GRPC_LONG" --receipt "$PERF01_GRPC_LONG/long-verification.json"
```

HTTP mixed profile SHA is
`b523306d177fe23a9c32025fdb97fa8efb422a182320a64d8f037905e31efa6a`;
gRPC mixed profile SHA is
`fcd529ae210b57a6c3030f7521127204f665f33978ec50d848d13259a7b697af`.
Both have global managed/native caps of 64 MiB, the original TLS/client/data/mix,
and the same error/p99/RSS criteria. Their per-request caps remain 4 MiB for HTTP
and the prospectively selected 64 MiB for gRPC. Preserve the direct-Rust actual
frame-credit accounting qualification in later comparisons.

Only actual successful ordinary-operation duration proof of at least 1800
seconds, complete outcomes, recovery, idle-owner drain and all original checks
can credit a long result. The 1802-second schedule does not itself prove a pass.
Do not overwrite a partial directory or its receipt. These two long output
paths were absent during source preparation; they are proposed fresh paths,
not claims that either long run has started or completed.

The codec reviewer independently checked this queue against the existing
calibration/cohort/comparison argument parsers and actual driver/profile fields.
The command/schema review passed, including automatic extraction paths and the
separate long-run idle profile. The reviewer did not execute commands, tests or
loads, rehash binaries/TLS, or read raw ledgers.
