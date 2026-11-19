# Perf-01 codec short-cohort commands

Status: source-prepared recipe, not an execution receipt. Run each command only
under the root's exclusive measurement control after the current profiling or
calibration window ends. This recipe launches the existing frozen
`tests/Perf01.Codec/driver.py`; it adds no driver, target or supervisor. Keep the
actual command arrays, output paths, timestamps and return codes in the root
execution ledger. Do not run this document as an unattended shell script.

The actual before-only W1 smoke and recorded W1/W2 fixed selections are in
[the short-load decision](codec-short-selection-linux.md). Noise and confirmation
processes remain separate from that selection smoke.

## One mixed process covers all 32 rows

The frozen `tests/Perf01.Codec/driver.py:62–72` `cycle()` has weights **10, 5, 4, 1** for 256 B, 4 KiB, 1 MiB and
4 MiB. Both entropy classes, both actions and both interfaces give eight copies
of those weights: `(10+5+4+1)*8 = 160` requests per complete cycle. A 4 MiB
case/action/interface row appears once per cycle. Therefore **16,000 successful
measurement operations per process** contain at least 100 observations of every
one of the 32 rows. Each row's per-process p99 then satisfies A21's minimum
population. Counts from separate processes are not substituted for a deficient
individual process, and failed operations do not satisfy the minimum.

For rate `R`, the unchanged scheduler (`driver.py:370–375`) uses integer period
`P = round(1_000_000_000/R)` ns. Select
`D = ceil(16000*P/1_000_000_000)` seconds. Its existing dispatch guard adds
requests; do not rely on that addition to reach the minimum. Validate actual
success counts after completion. At 268/s, `P=3,731,343` and `D=60`; at 134/s,
`P=7,462,687` and `D=120`. These are count calculations, not measured throughput.

Use separate cohorts and before-only noise receipts for **one worker** and
**two workers**. Conditional row extraction from the same fixed mixed process
is comparable across before/after/direct at the same worker count and load;
it does not create an isolated all-small or all-large throughput result.

## Prospective short-cell configuration

| Setting | Fixed value |
| --- | --- |
| Corpus / sequence | Existing seeded corpus; complete mixed action and interface; no `--case` filter |
| Target / generator CPUs | Target 2,3; controller 0,1 via the existing all-thread affinity option |
| Workers | 1 or 2, separate strata |
| Queue / maximum in flight | 64 / 256 |
| Warmup | 20 seconds, separate from measurement |
| Recovery | 10 seconds at 1 operation/s, in the same live process |
| Short idle observation | 5 seconds after drain; no 30-minute acceptance claim |
| Request deadline / generator lag | 1000 ms / 100 ms |
| Service standard | Zero unexpected outcomes, whole-cell arrival p99 ≤500 ms, sampled target RSS ≤256 MiB |
| Minimum observations | 16,000 successful measurement operations and ≥100 in each of 32 rows, in each full process |
| Noise floor | Explicit 1000 ns analysis granularity, then unchanged A21 process-mean comparison |

The five-second short idle is a separate short-study choice. Long cells keep
their frozen 60-second idle and common long-verifier requirements. Freeze this
short configuration before product edits; do not silently inherit a changed
CLI default. Sampled RSS does not establish an unsampled instantaneous bound.

For one worker, start with a **before-only 10-second smoke at 134/s**, a proposed
half-rate of the selected two-worker 268/s long load. This is a proposed starting
rate, not a claim it passes. Read the actual complete result, generator lag,
whole-cell p99 and resource samples. If it fails, retain it and choose a lower
before-only rate. No new capacity ladder is required for this low-concurrency
layer. Record the accepted rate before any candidate observation, then collect
new full-duration calibration cells. The smoke does not enter the noise triplet
or confirmation cohort. Root selected 268/s for the two-worker fixed-load
cohort. Reconfirm the baseline capacity near 336/s separately after the final
harness preparation; those capacity observations do not enter the fixed-load
noise triplet or replace the fresh 268/s confirmation cells.

## Exact existing-driver command

Set these variables to the actual integration checkout and prepared artifacts.
The driver takes the **corpus directory**; the extractor takes its manifest.
The before producer must use clean main
ea5fa528035d025bd7a28698ee7c71194432236c. Root requires a fresh before preparation
after the reviewed A21 retention change is tested and frozen: the old before-002
manifest pins earlier A21 bytes and stays preparatory diagnostic evidence.
Do not edit its manifest to bypass the source check. Both final versions use
the same driver checkout and A21 hash. `PERF_AFTER_BUILD` is supplied only for the later confirmation stage and must
point to an actual fresh after producer from the after-build recipe.

```sh
PERF_ROOT=/workspace/scratch/01c249676f47
source "$PERF_ROOT/perf01-toolchain/env.sh"
PERF_DRIVER="$PERF_ROOT/.worktree/Perf-01-linux/NativeWeave"
PERF_ANALYSIS="$PERF_ROOT/.worktree/Perf-01-linux/Plan/ledger/evidence/batches/Perf-01"
PERF_PYTHON=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
PERF_BEFORE_BUILD="${PERF_BEFORE_BUILD:?Set the actual fresh post-A21-freeze before manifest path}"
PERF_CORPUS_DIR="$PERF_ROOT/perf01-codec-checks/corpus"
PERF_A21="$PERF_DRIVER/src/Benchmarks.Harness/nativeweave_bench.py"

# Freeze these for one worker stratum before collecting its noise triplet.
# For W1 smoke only, set PERF_SECONDS=10 and choose a fresh smoke output.
# After a passing actual smoke, set the full D using the formula above.
PERF_WORKERS=1
PERF_RATE=134
PERF_SECONDS=120

# This function only expands one existing-driver command. Root invokes one
# cell at a time under its existing exclusive resource control.
codec_cell() {
  taskset -c 2,3 "$PERF_PYTHON" "$PERF_DRIVER/tests/Perf01.Codec/driver.py" run \
    --manifest "$2" --corpus "$PERF_CORPUS_DIR" --route "$3" \
    --interface mixed --action mixed --workers "$PERF_WORKERS" \
    --queue 64 --inflight 256 --rate "$PERF_RATE" \
    --duration-seconds "$PERF_SECONDS" --warmup-seconds 20 \
    --recovery-seconds 10 --recovery-rate 1 --idle-seconds 5 \
    --deadline-ms 1000 --max-lag-ms 100 --generator-cpus 0,1 --output "$1"
}
```

Choose a new `PERF_STRATUM` directory for each worker/rate selection. Every cell
path below must be new. The existing driver refuses overwrites and verifies its
own full source inventory, A21, actual prepared artifact/consumer hashes and
corpus bytes before target startup. The root must preserve interruption records
and verify shutdown before using the resource again; this function deliberately
adds no alternative interruption or retry policy.

## Before-only noise, then a recorded decision boundary

Run each of these commands separately. Stop on any nonzero exit or failed
correctness, generator, service-standard or minimum-count check. Do not continue
a shell block merely because a later command could still succeed.

```sh
codec_cell "$PERF_STRATUM/noise-1" "$PERF_BEFORE_BUILD" nativeweave
codec_cell "$PERF_STRATUM/noise-2" "$PERF_BEFORE_BUILD" nativeweave
codec_cell "$PERF_STRATUM/noise-3" "$PERF_BEFORE_BUILD" nativeweave

taskset -c 8 "$PERF_PYTHON" "$PERF_ANALYSIS/codec_compare.py" freeze \
  --cells "$PERF_STRATUM/noise-1" "$PERF_STRATUM/noise-2" "$PERF_STRATUM/noise-3" \
  --build "$PERF_BEFORE_BUILD" --corpus "$PERF_CORPUS_DIR/manifest.json" \
  --a21 "$PERF_A21" --resolution-ns 1000 --p99-max-ms 500 --rss-max-mib 256 \
  --output "$PERF_STRATUM/noise.json"
sha256sum "$PERF_STRATUM/noise.json"
```

Record the actual noise SHA, this worker/rate/duration selection, command arrays,
source/producer/corpus identities and all three cell identities in Plan before
confirmation. Assign that recorded value to `PERF_NOISE_SHA`; do not derive a
new noise receipt from candidate results. Repeat the entire before-only step
for W2 with its own directory/rate/duration. Do not use the W2 band for W1.

## Three fresh interleaved confirmation processes per route

Use this exact order at each worker stratum. A row in this table represents a
separate fresh target process. Before confirmation is fresh, not the earlier
noise triplet. The managed column is optional valid-corpus observation only.

| Repetition | Execution order | Directory suffixes |
| --- | --- | --- |
| 1 | Before, after, direct, managed | before-1, after-1, direct-1, managed-1 |
| 2 | Managed, direct, after, before | managed-2, direct-2, after-2, before-2 |
| 3 | Before, after, direct, managed | before-3, after-3, direct-3, managed-3 |

Use `codec_cell` with the table's actual suffix and these route/build arguments:

```sh
# Examples show repetition 1; execute the table's full order one cell at a time.
codec_cell "$PERF_STRATUM/before-1" "$PERF_BEFORE_BUILD" nativeweave
codec_cell "$PERF_STRATUM/after-1" "$PERF_AFTER_BUILD" nativeweave
codec_cell "$PERF_STRATUM/direct-1" "$PERF_BEFORE_BUILD" direct-rust
codec_cell "$PERF_STRATUM/managed-1" "$PERF_BEFORE_BUILD" managed-zlib
```

At completion of **each full cell**, check `summary.json` and `result.json` for
valid/complete status, zero unexpected outcomes, actual full dispatch duration,
recovery/drain, `summary.successes >=16000`, exactly 32 groups, each group's
`successes == offered >=100`, and non-null per-row p99. Inspect actual resource
samples against the same RSS bound. The extractor later verifies the raw bytes,
phase completeness, all resource samples and immutable identity. It rejects
any individual process below the total or per-row population minimum; summary
review alone is not that independent verification. Keep every failed or interrupted
cell and its reason. It cannot contribute a successful observation, and any
replacement requires a new path and explicit root execution-ledger entry.

After all cells and the root's measurement window have ended:

```sh
taskset -c 8 "$PERF_PYTHON" "$PERF_ANALYSIS/codec_compare.py" compare \
  --noise "$PERF_STRATUM/noise.json" --noise-sha256 "$PERF_NOISE_SHA" \
  --before "$PERF_STRATUM/before-1" "$PERF_STRATUM/before-2" "$PERF_STRATUM/before-3" \
  --after "$PERF_STRATUM/after-1" "$PERF_STRATUM/after-2" "$PERF_STRATUM/after-3" \
  --direct "$PERF_STRATUM/direct-1" "$PERF_STRATUM/direct-2" "$PERF_STRATUM/direct-3" \
  --managed "$PERF_STRATUM/managed-1" "$PERF_STRATUM/managed-2" "$PERF_STRATUM/managed-3" \
  --before-build "$PERF_BEFORE_BUILD" --after-build "$PERF_AFTER_BUILD" \
  --direct-build "$PERF_BEFORE_BUILD" --managed-build "$PERF_BEFORE_BUILD" \
  --corpus "$PERF_CORPUS_DIR/manifest.json" --a21 "$PERF_A21" \
  --output "$PERF_STRATUM/comparison"
```

If managed observation is not selected or is ineligible, omit both `--managed`
and `--managed-build`, retain any failed managed cells separately, and report
unavailability/reason. Do not lower only its rate and present it as this cohort.
ZLibStream's strict trailing-input contract differs and its owned label aliases
an array; its valid-corpus call times/ratios/allocations never become an overall
arrival/ownership performance ranking. Direct uses the original pinned miniz
reference executable even when the after preparation also emits another one.

The resulting two 32-row tables are conditional fixed-mixture comparisons.
Their successful wall MiB/s and summed-call MiB/s have different denominators;
neither establishes maximum sustainable load. Report the separate capacity
ladder and ten required long-segment verifier receipts independently.

## Independent source review

The protocol reviewer checked the exact existing-driver arguments, corpus
directory versus analysis manifest, 160-cycle count proof and rounded-period
durations, separate worker-specific bands, fresh interleaving, managed scope
and per-cell ownership. The reviewer also checked the extractor's new population
gate after raw success reconciliation and its negative finite fixture. Required
final-producer input and explicit toolchain environment were clarified during
review. This was source inspection only; no new test, extraction or workload
was run by either author or reviewer.
