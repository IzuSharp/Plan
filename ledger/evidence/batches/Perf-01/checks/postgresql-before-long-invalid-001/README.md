# Perf-01: PostgreSQL BEFORE long run rejected by the generator lag gate

This is retained failure evidence, with **zero accepted duration credit**. The
original 144 operations/second, concurrency 16 run completed its business
operations and durable checks, but violated the already frozen generator
dispatch-lag limit. No original evidence, acceptance limit, product runtime,
workload, or baseline identity was changed by this diagnostic extraction.

## Actual execution and rejection

The long command ran from 2026-11-19 17:35:41.030850 UTC to
18:10:40.759738 UTC and returned exit code 1. The measurement application and
A21 worker completed normally: the supervision receipt records worker exit
code 0, status completed, and no failure; the observation records target exit
code 0 and empty stderr. The outer driver wrote completed-invalid.

The original supervisor stopped at the nonzero driver exit and did not run its
next command. The root agent then executed the exact frozen rejection-verifier
command once, without modifying the run. Its actual execution at
18:13:47.200961–18:13:47.250306 UTC returned exit code 1. The verifier reports
accepted=false, duration_credit_seconds=0, and:

> ValueError: Required acceptance flag is not true: valid

The independent verifier rejects the invalid summary before replaying the full
raw correctness ledger. This directory does not claim that this early-rejection
verification revalidated every business result. Business, durability, recovery,
and shutdown findings below are the actual completed application's and driver's
evidence, plus the separate bounded timing extraction.

The original global execution freeze remains SHA-256
85061c4e01b28fc72a5b20519ce2d8c01d79cae271238ba36e0a3465b0b8f4a3.
The command-document SHA-256 is
9604544d24953430ed90ec20f460565d41fa706202d21e397f56194c491594d7.

## Exact reason the sample is invalid

The only summary invalid reason is **generator saturation: dispatch lag**.
The frozen A21 condition at nativeweave_bench.py lines 733–734 is strictly:
dispatch_ns minus scheduled_ns greater than 100,000,000 nanoseconds. A single
offending row invalidates the cell. This is a generator-validity classification;
the label alone does not establish sustained CPU saturation.

The bounded extractor streamed all 259,526 observation records using the
unchanged frozen JSON reader. It found 52 rows above 100 ms, 75 above 50 ms,
and a mean dispatch lag of 875,727.2782572844 ns. All records had status ok.
The largest lag was **326,111,321 ns**, on operation 148071.

| Offending operation IDs | Count | First scheduled ns | First dispatched ns | Last dispatched ns | Dispatch span |
| --- | ---: | ---: | ---: | ---: | ---: |
| 30352–30370 | 19 | 41391078455048 | 41391306275312 | 41391306514083 | 238,771 ns |
| 148071–148103 | 33 | 42208571458284 | 42208897569605 | 42208897969859 | 400,254 ns |

The two groups begin approximately 210.778 and 1028.271 seconds after the first
scheduled arrival. They are two in-run delay clusters, not a startup-only
event. Their compressed dispatch spans show the delayed arrivals being sent in
catch-up bursts. The complete 52 offending timing rows, including operation
kind, scheduled/dispatch/admission/completion timestamps and calculated lag, are
retained in projection/offending-timing-rows.jsonl.

## Resource observations and attribution limits

The projection retains the original bytes of 30 generator-resource JSONL rows
bracketing the two groups. The windows begin 2.3 seconds before each group's
first scheduled offender and end 2.3 seconds after its last dispatched offender.
The analysis records original source line numbers and the complete source-file
SHA-256, so these are traceable subsets rather than reconstructed samples.

All selected generator identities and CPU affinities remain consistent. The
controller RSS is 73,580,544 bytes. Around the first group, scheduler RSS is
approximately 397.6–397.8 MB; around the second, 565.9–566.0 MB. One-second
bracketing intervals show approximately 0.26 and 0.47 seconds of scheduler CPU,
and 0.34 and 0.44 seconds of target CPU, respectively. The generator processes
share the frozen CPUs 0,1.

These one-hertz observations do **not** identify a subsecond pause as garbage
collection, host interference, instantaneous CPU competition, or another
scheduler operation. No such cause is asserted here. The application CPU and
RSS statistics likewise cannot repair a failed generator-validity condition.

## Business, durability, and cleanup observations

| Observation | Actual result |
| --- | --- |
| Offered / dispatched / successful | 259,526 / 259,526 / 259,526 |
| Operation mix | 129,763 durable cycles; 129,763 list operations |
| Unexpected operation/provider errors | 0 / 0 |
| p50 / p95 / p99 | 21.363369 / 59.497206 / 104.185227 ms |
| Actual dispatch span | 1802.176781682 seconds |
| Driver duration_valid | true; this does not override overall valid=false |
| Successful operations per second | 143.99380537238235 |
| Measurement application CPU | 1309.32 seconds; 72.6479574300719% of one core |
| Measurement application RSS peak | 58,556,416 bytes |
| Independent pre-recovery persisted measurement commits | 129,763, matching successful cycle operations |
| Pre-recovery rows in each of items/operations/outbox | 129,899, including 128 seed and 8 warmup commits |
| Recovery operations | 32, all ok |
| Pre-shutdown rows in each of items/operations/outbox | 129,931 |
| Original durable oracles | passed before recovery and after recovery |
| Shutdown | Consumer and database resources released; both statuses Succeeded; server Disposed |
| Accepted long-duration credit | **0 seconds** |

The table describes this invalid run. It is not an accepted capacity or paired
BEFORE/AFTER result.

## Files and provenance

- summary.json, progress.json, plan.json, frozen-inputs.json, perf01.json,
  supervision-receipt.json, driver.log, and long-execution.json are exact
  small-file copies from the original execution.
- verification.json and rejection-verifier-execution.json/.log preserve the
  actual frozen verifier's rejection and the separate manual execution.
- copied-inputs.json records every copied file's original path, byte count, and
  matching source/copy SHA-256.
- extract_dispatch_lag.py is a diagnostic projection, not a measurement
  driver. It bounds retained offenders, reads each observation record
  separately, preserves selected resource rows verbatim, checks its fixed
  reader/A21/failed-summary identities, and checks that inputs were unchanged.
- extraction-execution.json and extraction.log record the actual CPU-8-only
  execution, argv, times, exit code, source hash, and output log hash.
- projection/analysis.json records full streamed input hashes, output hashes,
  counts, groups, and limitations. The extraction executed successfully from
  18:19:59.582735 to 18:20:21.732075 UTC on 2026-11-19.

The frozen reader used for this projection is SHA-256
8034692b643f4dbb1385cd61e25c9d4d6f084d7b71268fec02411b5c2fcdbeb4.
The original A21 source is SHA-256
dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53.
The separate rejection verifier is SHA-256
3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82.
These are different roles; the post-run verifier is not substituted into the
timed driver's source identity.

## Reproduction and retention

The actual absolute command is retained in extraction-execution.json. To
reproduce the projection, use that argv with a new, nonexistent output
directory; the script deliberately refuses to overwrite an existing output.
Run only outside any exclusive timing window. It reads existing evidence and
does not launch a service, database, workload, build, or test.

All original large files remain at:

    /workspace/scratch/01c249676f47/perf01-evidence/long/before/postgresql-001

This checkpoint does not copy or remove the 1.859 GB observation, 1.338 GB event
ledger, 538 MB application receipt, or 488 MB dataset. The original application
receipt hash remains in summary.json. The source observation and generator
resource hashes were independently streamed for this projection.

Small receipts and diagnostic subsets are retained in Plan git history, with no
new automatic expiration configured by this change. Publication and successful
readback of the complete large raw archive are still pending; local raw paths
must not be described as a verified remote archive or assigned an invented
remote retention period.

This checkpoint changes neither the main handoff nor the original immutable
freeze and grants no repeat attempt or new load configuration.
