# Before-only codec calibration, package before-004

The completed calibration selected **384 operations/s** as the highest sampled
rate that passed all three confirmations. Policy 4 therefore selects
**307 operations/s** (`floor(384 * 0.8)`) for the paired long load. The first
failing bracket is 416/s. These are measurements of the unchanged before
runtime, not optimization results or a theoretical capacity limit. This
calibration earns **zero 30-minute acceptance credit** and does not freeze a
before-only noise band.

The original controller completed at `2026-11-19T12:34:03.613158+00:00`.
[controller.json](controller.json) and [selection.json](selection.json) are the
verbatim records retained by root. [audit.json](audit.json) records all 14 cells,
their metadata hashes, raw-ledger hashes reported by the driver, file sizes,
and the bounded resource audit. This note adds no execution: its work was
limited to source, small metadata and resource reads on CPU 8. No benchmark,
build, test, binary scan or operation/event-ledger scan was run by this audit.

## Selected confirmations and failed points

All cells used two workers, a 64-item target queue, 256 maximum pending requests,
target CPUs 2,3 and generator CPUs 0,1. The fixed 160-operation cycle contains
compression and decompression through array and owned-buffer interfaces over
the eight frozen payloads. The deadline was 1,000 ms and maximum dispatch lag
100 ms. Each confirmation used five seconds of warmup, a separately counted
four-second recovery phase at 1/s, and five seconds of idle observation.

The service criterion requires zero unexpected errors/rejections, p99 at most
500 ms and target RSS at most 256 MiB, together with a valid generator and
successful recovery. The following p99 values are successful arrival-to-
completion latency, not codec-call-only latency. All times are UTC on
2026-11-19.

| Confirmation | Measurement start to last completion | Actual dispatch span (s) | Successful/offered | Successful throughput (/s) | Arrival p99 (ms) |
| --- | --- | ---: | ---: | ---: | ---: |
| `11-confirmation-0-384` | 12:30:21.311122–12:31:21.413027 | 60.101491157 | 23,080/23,080 | 384.010681 | 110.590555 |
| `12-confirmation-1-384` | 12:31:37.227262–12:32:37.329862 | 60.102025309 | 23,080/23,080 | 384.006445 | 116.248592 |
| `13-confirmation-2-384` | 12:32:53.134589–12:33:53.236201 | 60.101332249 | 23,080/23,080 | 384.011602 | 110.282025 |

The three target PID/start-time identities differ and the measured windows do
not overlap. Each confirmation contains all 32 case/action/interface groups,
with at least 144 successes in every group. Every planned measurement operation
was sent, admitted and completed successfully. Warmup completed 1,960/1,960
and recovery 6/6 in each process; the extra dispatch guard explains counts above
the nominal rate-times-duration product. All three targets exited zero, and
their results record valid observation, successful service and recovery, drain
and idle completion. The driver checks pending requests and native live owners,
capacity, active calls and correctness errors at drain. This audit did not
independently replay the raw drain or idle events.

Every failed service point is retained below. These observations remained
valid; none has a recorded generator-invalid reason. The nonzero `rejected`
counts fail the zero-error criterion even though successful p99 is below the
latency bound.

| Cell | Offered rate (/s) | Successful/offered | Rejected | Successful arrival p99 (ms) | Recovery |
| --- | ---: | ---: | ---: | ---: | --- |
| `07-ladder-512` | 512 | 15,395/15,413 | 18 | 124.230093 | Passed |
| `09-refine-448` | 448 | 13,478/13,486 | 8 | 132.067930 | Passed |
| `10-refine-416` | 416 | 12,520/12,523 | 3 | 133.585851 | Passed |

In the pinned consumer source, `Program.Main` emits this normal `rejected`
status when `BlockingCollection<Work>.TryAdd` cannot admit to the bounded
queue. This supports a queue-rejection interpretation; it does not establish a
universal saturation threshold. The passing 30-second ladder points were
4, 8, 16, 32, 64, 128 and 256/s, followed by a passing 384/s refinement. The
4/s prefix contains only 29 groups, so it is not full 32-row comparison evidence.

## Observed memory and evidence sizes

Each final process has 76 resource samples, including 60 during measurement.
The three resource files were read and their SHA-256 values checked against
the existing driver summaries; each file is approximately 205 KB. Every
available target/generator thread mask stayed within the assigned CPU pair.

| Confirmation | Generator measurement first/last/peak RSS (bytes) | Target measurement peak RSS (bytes) | Target CPU (% of one core) | Target final sampled RSS (bytes) |
| --- | ---: | ---: | ---: | ---: |
| 0 | 24,150,016 / 24,150,016 / 24,150,016 | 88,514,560 | 132.457064 | 68,005,888 |
| 1 | 24,145,920 / 24,145,920 / 24,145,920 | 97,222,656 | 131.374129 | 73,019,392 |
| 2 | 24,145,920 / 24,145,920 / 24,145,920 | 80,322,560 | 133.389125 | 55,640,064 |

Thus measured generator RSS was flat at approximately 23.03 MiB in each
confirmation. Target final RSS exceeded its approximately 48.4 MB initial
sample; successful owner drain is not proof that the native or managed allocator
returned to its initial RSS. Whole sampled-lifetime target peaks were
88,514,560, 124,956,672 and 122,142,720 bytes, respectively, including warmup and
idle. The CPU figures cover the target process bracket, including its bounded
validation/telemetry work, and cannot be assigned to individual codec actions.

Each completed confirmation has about 13.88 MB of `events.jsonl`, 13.15 MB of
`operations.jsonl`, a 5,835-byte `result.json`, and a 41,478–41,492-byte
`summary.json`. File sizes were obtained from metadata; this audit did not read
or rehash the large ledgers. Their original producer hashes remain in
`audit.json`.

## Source-derived long-load memory estimate

The following is source arithmetic, not an observed long-run RSS measurement.
The pinned `tests/Perf01.Codec/driver.py` deletes each pending entry immediately
after writing and flushing its completed scalar record (`reader`, lines
310–341); at most 256 entries are pending. Events and resource samples are
streamed to JSONL. The target holds the eight-case corpus once: 10,494,464 raw
bytes and 5,263,812 encoded bytes, plus objects and engine workspace. Its bounded
64-item work queue holds identifiers and flags. Completed messages contain
scalars/status, not the raw or encoded payload arrays.

After load and drain, `summarize` (lines 511–565) streams the operation ledger
one record at a time. It retains seven unsigned 64-bit latency elements per
successful measured operation: one all-outcome arrival, five group latencies
and one global successful arrival. At 307/s for 1,802 requested seconds, with
the frozen 100 ms dispatch guard and rounded 3,257,329 ns period, the planned
measurement population is 553,246. The resulting array element payload is
**30,981,776 bytes (29.546524 MiB)**. This excludes array over-allocation,
Python object overhead, allocator retention and sorting workspace.

A21 `percentile` (lines 215–221) sorts a temporary Python list; its largest
population is 553,246 values. Exact sorting/allocator peak RSS is unavailable.
The resource sampler stops before summary generation, so the flat measured
generator RSS above must not be presented as the postprocessing peak. The
summary serializes 32 aggregate rows rather than all operation objects, and
A21 `sha256` (lines 41–47) hashes files in 1 MiB blocks. The source therefore
does not expose the full-page object retention and whole-observation JSON
serialization path found in the separate database driver. It still provides
no hard RSS ceiling or completed long-load memory guarantee.

Linear disk planning from the three actual confirmations gives about 597 MB
for the two measurement ledgers at 553,246 operations. Assuming the driver's
20-second warmup, 10-second recovery and 60-second idle defaults, while retaining
the selected 100 ms guard, gives about 604 MB for events plus operations across
559,430 total completions. The final long command is frozen separately; these
defaults are an explicit planning assumption. Resource samples and other
metadata add disk use, and wider values or different telemetry can change the
estimate. None of these disk sizes is a memory measurement or a hard bound.

## Producer identity and retention

The unchanged runtime is `ea5fa528035d025bd7a28698ee7c71194432236c`; the driver
producer is `aa3399f0418a6d0910cc56697abfaa3769f32b54`. Exact .NET SDK 11.0.100
and Rust 1.100.0 build details are in the
[before-004 preparation receipt](../../builds/before-codec-004/README.md).
Each cell records the same actual loaded native hash. This metadata audit did
not hash the executable or native binary again.

| Input | SHA-256 |
| --- | --- |
| Controller | `c92ccaef5ffb5b37ccf6c9ac61b9d19f6e96bddbde0311153c411ec2d9323876` |
| Selection | `b08ea7b9816e9f55f78c8fe3dd292d6705142ceb1153fff6500702a0e7922ef5` |
| Before-004 producer manifest | `d34298ebc8dc82b525f19860555947a1a04eff2bf8aecc38cede2922c81285a7` |
| Corpus manifest | `92932f7ecba2b3a7104b19344d22a42c3c40605f23eb158a0941d48bfff0465d` |
| Prospective policy | `0c7cd866b1ad0fc86d647e31dd1b6fe0b148d2e7ca54d83b7286cec09f11cafc` |
| A21 source | `dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53` |
| AOT consumer | `d71cb44e6bf7868ea150d9b98fe78e779675aeff59e6a990dbaa8ea47ae9253e` |
| Loaded native library | `3a472d8e51ad5d69a28ade2b00cd23fc9a2bb8d9fa1e2c4df47b769316acff79` |

Original cell directories remain under
`ROOT/perf01-evidence/calibration/before-codec-final004`. The producer remains
at `ROOT/perf01-codec-checks/package-before-004`. This directory retains the
small evidence notes and metadata in repository history without a task-specific
expiry, subject to repository retention policy. No raw-ledger or binary upload
is claimed here. Per-cell commands and source/metadata hashes are identified by
`audit.json`; the unchanged calibration invocation is documented in
[codec-calibration-linux.md](../../codec-calibration-linux.md).
