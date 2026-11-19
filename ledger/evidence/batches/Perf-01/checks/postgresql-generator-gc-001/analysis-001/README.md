# Independent analysis of the PostgreSQL generator GC diagnostic

**This is an intentionally interrupted, instrumented diagnostic with zero formal
duration credit.** Its persistent raw logs show a scheduler Gen2 collection
lasting 240.004324 ms, within a 243.210043 ms gap between adjacent event
observations. Event observations resume in a short burst. This supports testing
a scheduler-only GC policy remedy; it is neither a product performance gain nor
proof of the causes of both clusters in the earlier uninstrumented failed run.

## Source identity and exact workload

The actual configuration is SHA-256
550bbeadb7f58424a4d8fcb377783ba8bc186fa542bfab2d9ddf059997e1395a.
It copies the frozen PostgreSQL 144/s, C16, requested 1802-second command,
including the before package, database settings, seed, 16 warmups, 32 recovery
operations, 60-second idle setting, and CPU masks. Only the output directory and
variant label differ. The generated plan retains 259,526 requests, period
6,944,444 ns and the unchanged 100,000,000 ns dispatch-lag gate.

The scheduler attached as PID 39 / start_ticks 4504735, and the target as PID 40 /
start_ticks 4506556. Their exact role, entry point, argv, configuration, plan,
source hashes, Python path, and CPUs 0,1 match the recorded configuration.
The owned-process registry records the target identity; the supervisor receipt
and its identity-bound termination record identify the scheduler worker.
Both headers report GC enabled, thresholds 700/10/10, and zero preexisting
callbacks. No attachment-error or log-limit record was found.

The hook SHA-256 is
0c26d224e8da07644f08196d7293332f3f0dfc937dceb57caf5e6cd1832cedd2;
the original A21 SHA-256 is
dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53.
The extraction verified those actual source bytes and the role entry-point
hashes. The helper only installed GC observation callbacks; it did not disable,
force, or retune collection.

## Paired GC observation

The first persisted measured event is source line 1, admitted operation 0,
observed_ns **45067971164323**. Warmup does not enter this event ledger.
The scheduler's sole complete Gen2 pair within the observed measurement range
starts 215.678371707 seconds after that event:

| Field | Actual value |
| --- | ---: |
| Start callback monotonic ns | 45283649536030 |
| Stop callback monotonic ns | 45283889718042 |
| Callback-entry interval | 240,182,012 ns |
| Measured start-hook cost | 177,688 ns |
| Collection interval after subtracting start-hook cost | **240,004,324 ns** |
| Callback-entry process CPU delta | 236,357,890 ns |
| Collection-interval process CPU delta | **236,181,418 ns** |
| Objects reported collected / uncollectable | 3,969 / 0 |

The start and stop have matching role, PID/start identity, native thread,
generation, and start timestamp. Their duration and CPU arithmetic agrees with
the raw records. Across both complete GC logs, sequences are contiguous,
monotonic and CPU clocks do not decrease, and every start has a matching stop.
The scheduler log contains 14 Gen2 pairs in total, of which 13 precede the first
measured event. The target has 26 Gen2 pairs within the observed measurement
range; its largest collection interval is **37,866,763 ns**.

The observed collection interval still includes scheduling effects and any
other callback work. Process CPU covers the process, not exclusive collector
CPU. Those limitations do not change the observed 240 ms interval or its
position relative to the adjacent event records.

## Exact adjacent event evidence

The extractor streamed all 78,535 complete raw event rows, preserving the full
source-file digest. The following rows are adjacent in that ledger:

| Source line | Event | Operation | Observed monotonic ns |
| --- | --- | ---: | ---: |
| 62134 | completed, ok | 31062 | 45283647891808 |
| 62135 | completed, ok | 31067 | 45283891101851 |

Their observation gap is **243,210,043 ns**. No event-observation timestamp
falls between the scheduler GC start and stop. Within the first 10 ms after
line 62135, there are 18 observations: 2 completions and 16 admissions with
continuous IDs 31068–31083. The first 1 ms contains 3 observations.

The retained window spans 20 ms before the GC start through 50 ms after its
stop and contains 38 original JSONL rows. The exact source lines, decoded
kind/ID/status fields, wire hashes, and window bounds are in analysis.json.
The first measured event and the two gap-bracketing rows are also retained as
separate verbatim files.

**These are scheduler-observed admission/completion events, not exact dispatch
timestamps.** The diagnostic was intentionally stopped before A21 wrote its
final observation.json dispatch ledger. Buffered or delayed event observation
is part of this correlation; the subset cannot establish when each request
was physically dispatched or reached the application.

## Cleanup, claim boundary, and next decision

The retained supervisor receipt reports operator stop control, worker exit
-15, SIGTERM for the three registered identities, and an empty
live_owned_processes_after_cleanup array. No postmaster.pid remained when this
analysis ran. These establish the recorded bounded process cleanup; they are
not a graceful native-retirement or durable-business acceptance result.
The profile marker explicitly forbids formal timing credit.

The original uninstrumented PostgreSQL long run remains invalid. This separate
profile provides a concrete scheduler-side GC stall to address, while leaving
the target GC policy and product runtime untouched. A prospective automatic
versus deferred scheduler policy comparison must retain the same planned
operation graph, business load, source/package identities, and 100 ms gate,
and must observe scheduler memory and actual correctness. In particular, the
observed scheduler collection reclaimed 3,969 objects: deferral cannot be
declared memory-neutral without measurement.

This profile did not run to the earlier failed run's second cluster near 1028
seconds. It does not prove that both original clusters had this cause or that
all generator pauses are caused by GC. No volatile manual-monitor arrays are
used as evidence here; the root's separate manual-stop reconstruction records
operator actions, while this analysis relies on the persistent source files.

## Artifact and reproduction inventory

- extract_gc_correlation.py is the read-only diagnostic extractor.
- extraction-execution.json and extraction.log preserve its actual CPU-8-only
  execution: 2026-11-19 19:03:05.303213–19:03:07.320554 UTC, exit 0.
- extracted/analysis.json contains verified inputs, exact pair arithmetic,
  GC counts, event correlation, decoded subset rows, output hashes and limits.
- extracted/gc-*-headers-and-gen2.jsonl retain original headers and every Gen2
  start/stop row, with source line numbers recorded in analysis.json.
- extracted/events-around-scheduler-gen2.jsonl and the three single-event files
  preserve original raw bytes.
- extracted/source-small/ contains exact small configuration, launch,
  plan, profile-marker, control, summary, progress, and supervision copies.

Use the exact argv in extraction-execution.json with a fresh, nonexistent output
directory to reproduce this projection, only outside exclusive timing windows.
No service, database, benchmark, build or test is launched by the extractor.

The original full raw logs remain under:

    /workspace/scratch/01c249676f47/perf01-evidence/profile/postgresql-generator-gc-001

Their independently streamed SHA-256 values are:

| Original file | SHA-256 |
| --- | --- |
| gc/gc-scheduler-39-4504735.jsonl | 5bc50aad99f1518d9cd83aec64847296e992786c29004e0fc1c31e948cf71b80 |
| gc/gc-target-40-4506556.jsonl | 8544b4dcbb47471083874bb1e3e4ce4fb95d8e0237a14129c6971e07ab6f90ce |
| cell/observation.events.jsonl | 2c2bd96a014c4d857d7699ca2242dc2e08932b47da8a2ebd0af24389133b68f1 |

This subtree adds only an independent analysis and small preserved subsets.
It does not overwrite the root's configuration/review/manual-stop records,
modify the original logs, or create a new formal acceptance claim.
