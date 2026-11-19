# Perf-01 codec comparison extraction

Status: comparison extraction has not run. Root reported the original six
finite fixtures passed; the later minimum-population gate and seventh fixture
await the next execution window. No raw cohort was read and no performance
result was generated while preparing this tool. Run extraction, hashing and finite tests outside measurement windows.
The utility builds nothing and launches no workload.

`codec_compare.py` consumes the existing `tests/Perf01.Codec/driver.py` output
and pinned A17 producer/corpus manifests. It emits `comparison.json` and
readable `comparison.md` from real completed input cells only. Missing,
incorrect, saturated, profiling-only or changed inputs cause a nonzero exit;
the original failed/partial records remain intact and cannot establish a
comparison. It does not replace the common 30-minute verifier or a separate
capacity ladder report.

## Fixed rows and metric meanings

The 32 rows are the eight frozen corpus cases × compression/decompression ×
array/owned interface partitions. The cases remain 256 B, 4 KiB, 1 MiB and
4 MiB, each compressible or pseudorandom, with the original seeded mixed
sequence. Zlib format, level 6, Adler32 and all raw/encoded/decoded limits come
from the exact corpus manifest. The utility neither generates data nor fills
missing observations with synthetic rows.

| Field | Actual interval or denominator |
| --- | --- |
| `call_ns` | Public codec call on a dedicated synchronous worker. Array calls include the result copy and native free; owned calls publish a `NativeBuffer` and defer consumption/disposal. |
| `consume_ns`, `release_ns`, `operation_ns` | Exact output byte comparison and owner retirement remain separately counted. `operation` is call + consume + release, with the existing two-nanosecond conversion tolerance. |
| `arrival_ns` | External observer completion minus scheduled arrival, including generator delay, IPC, queue/admission, codec, correctness consumption and result observation. |
| Dispatch-to-admission | Both timestamps belong to the observer. This includes IPC and observation scheduling; it is not an isolated native queue-wait measurement. |
| Raw MiB/s wall | Successful original bytes divided by the sum of full process measurement windows, through the last completion. Each row is its contribution to the frozen mixed workload. |
| Raw MiB/s summed call | Successful original bytes divided by the sum of codec-call durations. Concurrent call time is not elapsed wall time or sustainable throughput. |
| Raw/encoded ratio | Measured successful raw bytes divided by measured encoded bytes. Decompression describes its input corpus; managed compression can produce different bytes and ratios. |
| Managed allocated bytes | The thread allocation-counter delta enclosing the codec call; an additional raw counter includes consumption/validation. Neither attributes all allocations to the loader. Rust managed allocation is unavailable/inapplicable, not zero. |
| Derived copy/FFI fields | Source-defined output payload copy bytes and codec/result-free boundary calls from the target records. They exclude native `Vec` growth/initialization, compressor internals, telemetry, allocator traffic and other runtime copies. |
| CPU/RSS | Whole mixed target process, with fixture/oracle/telemetry/runtime costs. Per-process target/generator sampled intervals and RSS endpoint changes remain in JSON. Per-row CPU/native allocator counters are unavailable. |

`summary.json` pins the original plan, result and three JSONL ledgers. The tool
streams their bytes, verifies those hashes, checks frozen mix and IDs, complete
phase counts, clock ordering, generator lag/deadline limits, successful payload
byte counts, actual AOT/direct readiness, mapped native hashes and drained
owners. It recomputes every successful latency population and validates the
summary's arrival tails. Metadata stat identities must remain unchanged while
reading. Exact payload/hash and rejection checks were executed by the frozen
driver; extraction does not replay them.

The public report uses pooled exact nearest-rank p50/p95/p99 over each route's
three processes, and retains all three process means/percentiles separately.
A21 withholds an individual tail when its observed population is insufficient:
for p99 that means fewer than 100 successes. The formal short-cohort extractor
now rejects any process with fewer than 16,000 total successes or fewer than
100 in any of the 32 rows. Pooled counts cannot repair a deficient process.
Do not describe the mean of three process p99s as a pooled p99. The full JSON provides either representation's
inputs; the Markdown names its pooled convention explicitly.

## Before-only noise and confirmation

First collect exactly three independent baseline calibration processes at the
prospectively chosen comparison load, using the clean pre-change main
`ea5fa528035d025bd7a28698ee7c71194432236c`. This is separate from three fresh
before confirmation processes. Freeze the receipt and record its SHA in Plan
before running any confirmation cohort. The tool checks that chronology and
requires unique target PID/start-tick pairs, unique source receipts and
nonoverlapping measurement windows across calibration and all confirmations.

For each row and each of call, arrival and whole-operation means, the noise band
is **max(declared analysis resolution floor, observed range of the three before
process means)**, with zero relative band. The formula is fixed by this source;
no after or direct measurement enters the band. `--resolution-ns` is explicit;
1000 ns in the example is a declared analysis granularity, not a claim that the
timer's actual uncertainty was measured as 1000 ns. The selected floor must be
at least the monotonic clock's advertised resolution in the recorded host.

Confirmation supplies exactly three fresh processes for before, after and
direct Rust, plus an optional three-process managed valid-corpus cohort. Use
root's frozen interleaved ordering, reversing order for the next repetition;
the extractor verifies nonoverlap but cannot infer an unrecorded execution
policy. It invokes the unchanged, hash-pinned A21 `noise_comparison` with the
three independent process means, its 2000 seeded bootstrap resamples and
original decision rules. It also verifies the frozen band's derivation and
extractor source hash. Noise decisions apply to those means. Tail, throughput,
allocation and ratio percentage changes remain descriptive observations.

Before/after product commits, package contents and native hashes may differ.
Matching uses the complete codec driver inventory, upstream lock hashes,
toolchain and recorded build environment, corpus, fixed sequence/limits,
arrival rate, concurrency/queues, phase durations, deadlines, CPU masks and
recorded stable host fields. Background load is retained in original plans but
does not become an equality key. The original before producer and direct
reference executable remain pinned. Actual NativeWeave mappings must match the
respective producer. This metadata establishes the recorded configuration;
the execution ledger still owns physical-machine identity and exclusive use.

The current common standards are zero unexpected outcomes, whole-cell arrival
p99 ≤500 ms and sampled target RSS ≤256 MiB. They are written into the frozen
noise receipt and shared by all compared routes. Sampled RSS is not proof of
an unsampled instantaneous memory bound. The extractor does not infer a maximum
sustainable rate from a fixed-rate observation.

Direct miniz uses a `Vec` for both interface labels, with the frozen strict
single-stream oracle and release outside its call interval. The managed route
uses arrays for both labels; its `owned` label is an alias. `.NET ZLibStream`
does not expose the same strict trailing/concatenated-input consumption rule,
and managed compression adds a decode check outside `call_ns`. Consequently its
isolated valid-corpus calls, ratios and allocations are retained with an
explicit limitation. The tool emits no managed full-operation or arrival
ranking, noise verdict, or NativeBuffer implementation claim. Missing managed
input remains unavailable; it is not filled from NativeWeave or direct Rust.

## Commands after the separate validation gate

The seven small tests cover changed-product versus changed-driver identity,
wall/summed-call denominators, insufficient p99/unknown allocation, the fixed
noise formula, process/window reuse, zero denominators and sampled resource
intervals, plus rejection of an incomplete mixed cohort or a deficient rare
row. They contain only temporary synthetic arithmetic fixtures. Root reported
the original six tests passed together with the fourteen archive tests; the
new population fixture remains unexecuted pending the next validation window.
This source note is not that execution receipt. They import the existing A21 source from the sibling NativeWeave
checkout, and launch no application.

```sh
PERF_ROOT=/workspace/scratch/01c249676f47
source "$PERF_ROOT/perf01-toolchain/env.sh"
PERF_DRIVER="$PERF_ROOT/.worktree/Perf-01-linux/NativeWeave"
PERF_ANALYSIS="$PERF_ROOT/.worktree/Perf-01-linux/Plan/ledger/evidence/batches/Perf-01"
PERF_PYTHON=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
PERF_BEFORE_BUILD="${PERF_BEFORE_BUILD:?Set the actual fresh post-A21-freeze before manifest path}"
PERF_CORPUS="$PERF_ROOT/perf01-codec-checks/corpus/manifest.json"
PERF_A21="$PERF_DRIVER/src/Benchmarks.Harness/nativeweave_bench.py"

taskset -c 8 "$PERF_PYTHON" "$PERF_ANALYSIS/test_codec_compare.py"

# Supply actual completed calibration directories in these three variables.
taskset -c 8 "$PERF_PYTHON" "$PERF_ANALYSIS/codec_compare.py" freeze \
  --cells "$PERF_CAL_1" "$PERF_CAL_2" "$PERF_CAL_3" \
  --build "$PERF_BEFORE_BUILD" --corpus "$PERF_CORPUS" --a21 "$PERF_A21" \
  --resolution-ns 1000 --p99-max-ms 500 --rss-max-mib 256 \
  --output "$PERF_NOISE"

# Record PERF_NOISE_SHA in Plan before collecting the fresh confirmation cells.
# PERF_AFTER_BUILD is the actual fresh after producer, not a source-only path.
taskset -c 8 "$PERF_PYTHON" "$PERF_ANALYSIS/codec_compare.py" compare \
  --noise "$PERF_NOISE" --noise-sha256 "$PERF_NOISE_SHA" \
  --before "$PERF_BEFORE_1" "$PERF_BEFORE_2" "$PERF_BEFORE_3" \
  --after "$PERF_AFTER_1" "$PERF_AFTER_2" "$PERF_AFTER_3" \
  --direct "$PERF_DIRECT_1" "$PERF_DIRECT_2" "$PERF_DIRECT_3" \
  --managed "$PERF_MANAGED_1" "$PERF_MANAGED_2" "$PERF_MANAGED_3" \
  --before-build "$PERF_BEFORE_BUILD" --after-build "$PERF_AFTER_BUILD" \
  --direct-build "$PERF_BEFORE_BUILD" --managed-build "$PERF_BEFORE_BUILD" \
  --corpus "$PERF_CORPUS" --a21 "$PERF_A21" --output "$PERF_COMPARISON"
```

Use new output paths and actual existing cell variables. These commands are a
recipe, not evidence of executions. Publish the frozen noise receipt and its
preconfirmation Plan commit/hash, the comparison JSON/Markdown, every referenced
cell's archive and producer/corpus manifests, and this extractor/A21 source
identity. Recompute after archive readback with those exact bytes; the original
timestamps, source labels and timing receipts stay unchanged.

## Source review

The independent protocol reviewer checked the invariant/changed producer
identity split, recorded driver/corpus/toolchain binding, fixed direct binary,
actual native mappings and independent process identities. The raw byte/rate
denominators, pooled-tail versus process-mean labeling, before-only noise
derivation and restricted managed scope passed source review. The review
requested two explicit guards: successful `terminal_status` as well as observed
and target status, and finite/nonnegative resource arithmetic. Both are now in
source, with a malformed CPU sample added to the finite resource test. No
extraction, large-ledger read, finite test, workload or build was executed by
the author or reviewer while preparing this change.

## Whole-mixture execution recipe

[codec-short-cohorts-linux.md](codec-short-cohorts-linux.md) provides the exact
unchanged-driver command, 160-cycle count derivation, one-worker baseline smoke,
separate worker-specific before-only bands and fresh interleaved confirmations.
It launches one process per complete mixture and requires at least 100 actual
successes in every row of every process. Short idle observation is explicitly
separate from the five groups of long acceptance.

The root's later A21 retention change requires fresh codec producer binding
after that harness is reviewed, tested and frozen. Before-002 remains historical
preparatory calibration; its manifest cannot be edited or used with different
A21 bytes. Final before still uses clean main ea5fa528035d025bd7a28698ee7c71194432236c,
and both final variants use the same driver checkout and exact A21 source.
