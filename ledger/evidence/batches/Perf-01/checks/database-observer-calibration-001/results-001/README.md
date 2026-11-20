# Perf-01: completed deferred-GC / threaded-observer DB calibration

This is a numerical projection of the actual **before** calibration, using the unchanged precompiled product package. PostgreSQL confirmed 220 offered operations/s and SQLite confirmed 60 offered operations/s in three independent 60-second processes each. The paired long rates remain **144/s and 40/s**. This report grants **zero long-test credit** and makes no product-optimization, direct-Rust comparison, or sustained-capacity claim.

## Execution and scope

| Group | Actual calibration start UTC | Actual calibration end UTC | Controller exit | Cells | Qualified cells | Confirmed offered rate | Next sampled valid SLO failure |
|---|---|---|---:|---:|---:|---:|---:|
| postgresql | 2026-11-19T23:27:44.057629+00:00 | 2026-11-19T23:39:37.391370+00:00 | 0 | 13 | 11 | 220/s | 240/s |
| sqlite | 2026-11-19T23:39:37.393492+00:00 | 2026-11-19T23:49:21.297169+00:00 | 0 | 11 | 8 | 60/s | 65/s |

All cells used concurrency 16, the mixed persistent business-cycle/paging workload, 16 warmup requests, 16 recovery mutations, and a separate approximately 5-second idle interval. Ladder/refinement cells requested 30 seconds; final confirmations requested 60 seconds. These are the calibration settings, not the later 1,802-second long command. PostgreSQL retained synchronous commit, fsync and full-page writes; SQLite retained WAL, FULL synchronous mode, IMMEDIATE transactions and the 5,000 ms busy timeout.

The original service gates remain whole-load arrival p99 ≤ 500 ms, application RSS ≤ 256 MiB, maximum generator dispatch lag ≤ 100 ms and zero unexpected errors. The generator retains its 512 in-flight bound. Successful throughput uses the original A21 observation duration; target load UTC endpoints and controller start/end are separately preserved in the JSON and are different observation boundaries. CPU values cover each named process, not whole-host CPU or a separately attributed PostgreSQL server cost.

## Every sampled load point

`valid` and service qualification remain separate. All four valid SLO failures retain their actual driver exit 0; PostgreSQL 320/s retains actual driver exit 1 and its generator-invalid status.

| Provider / phase / index | Offered rate/s | Successful / offered | Success/s | Whole p99 ms | App CPU % of one core | App peak RSS MiB | Recorded result |
|---|---:|---:|---:|---:|---:|---:|---|
| postgresql / ladder / 0 | 5 | 151 / 151 | 5.031053 | 106.207211 | 7.183 | 33.090 | qualified |
| postgresql / ladder / 1 | 10 | 301 / 301 | 10.024640 | 91.677085 | 9.842 | 36.074 | qualified |
| postgresql / ladder / 2 | 20 | 601 / 601 | 20.001962 | 84.020256 | 14.803 | 37.277 | qualified |
| postgresql / ladder / 3 | 40 | 1,201 / 1,201 | 39.998334 | 77.823117 | 25.078 | 36.660 | qualified |
| postgresql / ladder / 4 | 80 | 2,401 / 2,401 | 79.893244 | 70.467414 | 43.222 | 38.605 | qualified |
| postgresql / ladder / 5 | 160 | 4,801 / 4,801 | 159.763958 | 72.025938 | 74.189 | 40.934 | qualified |
| postgresql / ladder / 6 | 320 | 7,931 / 9,601 | 247.781419 | 2241.829165 | 100.476 | 56.605 | generator_invalid |
| postgresql / refine / 7 | 240 | 7,201 / 7,201 | 232.109387 | 1118.012777 | 95.683 | 53.246 | service_standard_failed |
| postgresql / refine / 8 | 200 | 6,001 / 6,001 | 199.786707 | 258.996449 | 90.450 | 46.059 | qualified |
| postgresql / refine / 9 | 220 | 6,601 / 6,601 | 219.655727 | 168.204430 | 94.329 | 45.590 | qualified |
| postgresql / confirmation / 10 | 220 | 13,201 / 13,201 | 219.948584 | 124.763984 | 94.603 | 49.066 | qualified |
| postgresql / confirmation / 11 | 220 | 13,201 / 13,201 | 219.913004 | 70.706392 | 92.283 | 43.410 | qualified |
| postgresql / confirmation / 12 | 220 | 13,201 / 13,201 | 219.932425 | 391.044979 | 93.428 | 51.699 | qualified |
| sqlite / ladder / 0 | 5 | 151 / 151 | 5.026024 | 117.378960 | 7.966 | 31.766 | qualified |
| sqlite / ladder / 1 | 10 | 301 / 301 | 10.021767 | 113.790471 | 11.381 | 33.926 | qualified |
| sqlite / ladder / 2 | 20 | 601 / 601 | 20.009472 | 95.934420 | 17.671 | 38.035 | qualified |
| sqlite / ladder / 3 | 40 | 1,201 / 1,201 | 40.016243 | 126.669967 | 30.453 | 38.383 | qualified |
| sqlite / ladder / 4 | 80 | 2,401 / 2,401 | 79.520853 | 1947.241101 | 53.083 | 39.164 | service_standard_failed |
| sqlite / refine / 5 | 60 | 1,801 / 1,801 | 59.766156 | 211.906189 | 42.131 | 39.906 | qualified |
| sqlite / refine / 6 | 70 | 2,102 / 2,102 | 69.096915 | 586.783146 | 49.141 | 40.551 | service_standard_failed |
| sqlite / refine / 7 | 65 | 1,952 / 1,952 | 64.598959 | 810.536971 | 44.271 | 39.504 | service_standard_failed |
| sqlite / confirmation / 8 | 60 | 3,601 / 3,601 | 59.911492 | 377.839309 | 41.262 | 41.387 | qualified |
| sqlite / confirmation / 9 | 60 | 3,601 / 3,601 | 59.953679 | 279.342387 | 42.799 | 38.648 | qualified |
| sqlite / confirmation / 10 | 60 | 3,601 / 3,601 | 59.779683 | 287.805384 | 43.000 | 40.652 | qualified |

PostgreSQL 320/s had **1,670 generator in-flight rejections**: 832 cycle and 838 paging operations. The 7,931 dispatched operations succeeded, and their durable result and recovery passed. This invalid point is preserved and is **not a server-capacity upper bound**. PostgreSQL 240/s completed all 7,201 operations but missed the p99 gate. SQLite 65/s, 70/s and 80/s likewise completed all offered operations but missed that gate. The sampled points need not form a monotonic latency curve.

## Three final confirmations per provider

All six processes passed full-row validation in the existing offline noise extractor. No full raw journal was replayed again by this report generator. Maximum dispatch lag below is from that extractor, not inferred from resource-sampling intervals.

| Provider / confirmation | Effective observation s | Success/s | p50 ms | p95 ms | p99 ms | Max dispatch lag ms | Successful cycle / page |
|---|---:|---:|---:|---:|---:|---:|---:|
| postgresql / 0 | 60.018572271 | 219.948584 | 22.821832 | 62.648166 | 124.763984 | 18.135148 | 6,601 / 6,600 |
| postgresql / 1 | 60.028282865 | 219.913004 | 20.227894 | 52.255211 | 70.706392 | 22.002742 | 6,601 / 6,600 |
| postgresql / 2 | 60.022982192 | 219.932425 | 28.050321 | 297.679418 | 391.044979 | 42.345420 | 6,601 / 6,600 |
| sqlite / 0 | 60.105330014 | 59.911492 | 21.363017 | 123.898544 | 377.839309 | 9.591332 | 1,801 / 1,800 |
| sqlite / 1 | 60.063036789 | 59.953679 | 21.635508 | 109.982523 | 279.342387 | 8.750679 | 1,801 / 1,800 |
| sqlite / 2 | 60.237857439 | 59.779683 | 22.116777 | 115.978893 | 287.805384 | 31.840003 | 1,801 / 1,800 |

Four-role measurements below use **application / target / scheduler / controller** order. CPU is the sum of process user/system time between the first and last usable CPU observations in that phase. RSS uses the conservative worker-start measurement phase **or** any read interval overlapping the actual A21 measurement window; the same rule covers all four roles. The JSON also retains recovery/idle observations, sample counts, CPU bracket duration, descriptor scan misses and error counters.

| Provider / confirmation | CPU seconds: app / target / scheduler / controller | Measurement peak RSS MiB: app / target / scheduler / controller | App / each generator measurement samples |
|---|---|---|---:|
| postgresql / 0 | 56.71 / 37.82 / 6.32 / 0.74 | 49.066 / 46.070 / 86.242 / 35.031 | 1104 / 59 / 59 / 59 |
| postgresql / 1 | 55.37 / 36.84 / 6.60 / 0.72 | 43.410 / 46.117 / 86.191 / 35.016 | 1103 / 59 / 59 / 59 |
| postgresql / 2 | 56.01 / 41.08 / 6.87 / 0.87 | 51.699 / 45.969 / 86.168 / 35.012 | 1073 / 59 / 59 / 59 |
| sqlite / 0 | 24.78 / 12.49 / 4.30 / 0.41 | 41.387 / 51.508 / 44.090 / 27.141 | 1144 / 60 / 60 / 60 |
| sqlite / 1 | 25.69 / 12.88 / 4.52 / 0.42 | 38.648 / 52.789 / 44.098 / 27.164 | 1143 / 60 / 60 / 60 |
| sqlite / 2 | 25.88 / 12.80 / 4.39 / 0.43 | 40.652 / 51.641 / 44.078 / 27.160 | 1143 / 60 / 60 / 60 |

CPU sample brackets cover approximately 59.95–60.19 seconds for the application and 58.53–59.28 seconds for the three generator roles in the six confirmations. Sampling is finite and non-atomic; these durations are not complete coverage of every resource transition. App peak RSS fell from its measurement peak to the sampled idle peak in every confirmation, while scheduler/target RSS did not return to their measurement start. The scheduler observer stops before final A21 replay and GC-policy restoration; this report does not establish finalization peak RSS, post-restoration heap release, memory neutrality, or a 30-minute memory bound.

## Correctness, provider outcomes and cleanup

All 24 small summaries report the original independent durable oracle and recovery oracle as passed. Each complete outcome journal was sealed and closed; journal digests and row counts remain bound. The six final confirmations additionally passed the existing full-row noise reader; the remaining 18 cells here are projected from their original driver summaries and receipts, without a second raw replay.

For each PostgreSQL confirmation, independent tables contained **6,737 rows each before recovery and 6,753 before shutdown**, matching 128 seed + 8 warmup + 6,601 measured commits + 16 recovery commits. SQLite confirmations contained **1,937 and 1,953** respectively, with 1,801 measured commits. Paging contributes no mutation. Both providers had zero observed provider exceptions and zero business retry attempts in every cell. SQLite reported zero surfaced BUSY and LOCKED exceptions. Internal SQLite busy-handler attempts are **unavailable**, so zero surfaced BUSY must not be interpreted as zero internal waits or retries.

All 24 scheduler receipts report deferred automatic cyclic GC, collections `[0, 0, 0]` during the complete wrapped worker scope and restoration of the initial enabled state. Restoring the policy does not prove that all cycles were collected. Application managed GC/allocation, native live allocation, FFI calls, copied bytes, separate database execution, lock wait and pool-wait attribution are unavailable in these DB observations.

Every cell completed 16/16 recovery operations, then its separate approximately 5-second idle interval. The original normal-close receipt reports successful consumer/database resource release and a disposed server. Supervision reports worker exit 0, no cleanup signals, no registry errors and zero live owned processes after cleanup. The invalid generator sample retains these functional facts without being accepted as a performance result.

## Frozen before-only noise bands

Offline extraction actually ran from **2026-11-19T23:51:05.096942+00:00 to 2026-11-19T23:51:12.711018+00:00** under the timing lock on CPU 8. PostgreSQL and SQLite extractor commands both exited 0; each output binds 59 source/input digests and three complete 60-second processes. The unchanged rule is `max(1,000 ns, max(process means) - min(process means))`, with relative noise 0. The bands below are latency-mean variability, not latency improvement or p99 thresholds.

| Provider / scope | Process means ms: 0 / 1 / 2 | Absolute noise band ms |
|---|---|---:|
| postgresql / mixed | 27.341824 / 23.533921 / 57.572657 | 34.038736 |
| postgresql / cycle | 41.592528 / 36.408828 / 74.799708 | 38.390880 |
| postgresql / page | 13.088961 / 10.657064 / 40.342996 | 29.685932 |
| sqlite / mixed | 41.992789 / 39.112781 / 39.485057 | 2.880009 |
| sqlite / cycle | 71.148698 / 65.479790 / 65.727242 | 5.668908 |
| sqlite / page | 12.820683 / 12.731123 / 13.228292 | 0.497169 |

The PostgreSQL mixed band is **34.039 ms**, with 38.391 ms for cycles and 29.686 ms for paging: this is a material limitation on later mean-latency claims. It is retained without narrowing the rule or discarding the third process. Cycle/page values are conditional slices of the same mixed workload, with no separate CPU/RSS attribution. The service gate applies to the whole mixed load; a conditional cycle p99 above 500 ms does not redefine that frozen gate.

## Source identities and evidence

- Actual measured driver commit: `a3ce0f6295c535b0a81de95fc0f98aa19deb259c`; product source remains `ea5fa528035d025bd7a28698ee7c71194432236c`.
- Controller source: `b1c9156ab1e72f46ca551ff92a5c7d88f0bdafa69d6762d9b2b5303a5445d4d9`; offline noise extractor: `d4c2a887452985697b3ec69d45500b4cf87185c9b54433ed887224047524f3de`.
- [public-summary.json](public-summary.json) contains all 24 points, the six confirmations, source/policy/loaded-binary hashes and exact small-receipt digests. [projection-execution.json](projection-execution.json) binds 152 actual small inputs plus the projector and output hashes.
- The public JSONs contain fixed keys and numeric, boolean, UTC, fixed-enum, hash or null values only. They contain no operational absolute paths, process/thread identities, raw commands, environment contents or control tokens.
- Original raw journals and receipts remain unchanged in their recorded evidence layout. This directory publishes the narrow projection and digest inventory; it does not claim the full raw set has been publicly archived or independently fetched.

## Reproduce this projection

Run only after the exclusive measurement owner releases the machine. Supply the existing evidence/receipt directories and a fresh output directory. The projector caps every opened JSON at 1 MiB and rejects unexpected hashes or values. It opens no full observation, outcome or resource journal.

```sh
mkdir "$PERF_REPORT_OUTPUT"
flock --nonblock "$PERF_TIMING_LOCK" taskset -c 8 "$PERF_PYTHON_31214" project_results.py \
  --postgresql "$PERF_CALIBRATION/before-postgresql-gc-deferred-threaded-v1" \
  --sqlite "$PERF_CALIBRATION/before-sqlite-gc-deferred-threaded-v1" \
  --noise "$PERF_NOISE/database-gc-deferred-threaded-v1" \
  --calibration-execution "$PERF_RECEIPTS/database-observer-before-calibration-001-execution.json" \
  --noise-execution "$PERF_RECEIPTS/database-observer-noise-001-execution.json" \
  --output "$PERF_REPORT_OUTPUT"
```

The final metadata projection actually executed at 2026-11-19T23:56:12.571130+00:00–2026-11-19T23:56:12.698838+00:00 on CPU 8, exit 0. Its 21,457 counted checks include scalar/key type guards as well as cross-document consistency; they are not new application tests. A preliminary projection attempt exited 1 because it expected `completed` for the preserved invalid point; the actual `completed-invalid` state was then explicitly projected without changing any measurement input. That failed metadata-only attempt and its source hash are retained in the execution receipt. No new workload, build, benchmark or raw replay was executed for this report.
