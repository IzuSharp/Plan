# Pre-long checkpoint — f0078da7

The current comparison has completed **18 same-query phase processes / 41,472 steady queries**, **36 short mixed-load cells / 3,004,197 successful business operations**, and **12 qualified resource-diagnostic processes**. All completed current cells retain their original counters and identities. Four required 1800-second candidate/Dapper.AOT cells have **no completed result at this checkpoint**. This is a recovery and evidence record, not final performance acceptance.

At the reported **2026-11-25 14:09 UTC** launch, SQLite candidate prepared mixed load started, with Dapper.AOT scheduled next in the same serial run. PostgreSQL long load had not started. The immutable numeric archive was captured before launch, so its four long results and two long setups correctly remain `not_observed`. Inspect the live coordinator before resuming; never infer current completion from this snapshot or replace it silently.

## Candidate, CI and evidence custody

Continue [Korda #37](https://github.com/IzuSharp/Korda/pull/37), [Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and [Plan #34](https://github.com/IzuSharp/Plan/pull/34). Product head is [`f0078da720e07031bc56464995af6791c41aaae8`](https://github.com/IzuSharp/Korda/commit/f0078da720e07031bc56464995af6791c41aaae8), tree `1e56f5466fa02640dcb68389f283e5c03c2c09ec`; the actual package-producing CI merge is `46ef09477b75dd5ce05e1941a739652bc685a9e2`. Current Design is [`d65bf803f03342443b36c3b90e90816d4d4a5575`](https://github.com/IzuSharp/Korda-Design/commit/d65bf803f03342443b36c3b90e90816d4d4a5575).

[Ordinary CI 45624813071](https://github.com/IzuSharp/Korda/actions/runs/45624813071) passed. PostgreSQL and SQLite remain independent package runners with direct Linux Native AOT consumers; ordinary module routing is unchanged and there are **zero benchmark CI jobs**. The [previous checkpoint](../serializer-f0078da7/README.md) retains the detailed component tests, 280-operation correctness, six lifecycle checks, exact package identities, diagnostic-only workflow change and old failures. The later published [Plan gate](https://github.com/IzuSharp/Plan/actions/runs/45628004489), [Design history gate](https://github.com/IzuSharp/Korda-Design/actions/runs/45628020854) and [Design API gate](https://github.com/IzuSharp/Korda-Design/actions/runs/45628020784) passed for their previous published commits, not this future checkpoint commit.

The active freeze binds **16 applications / 926 files**, SHA-256 `f83df84a57af07a927f4955b91e8a64561bccafa8f92d2bd7181bc3a83efa269`. Full identity/input manifests stay local. The archive's `identity.numeric.json` retains public producer, ELF, package, native-image and SDK identities. Final post-run rehash and long-result qualification remain pending.

| Published evidence | Size / SHA-256 | Scope |
|---|---|---|
| [Numeric archive](DB-Perf-01-evidence-v4-prelong-numeric.tar.gz) | 1,192,178 bytes; `e3c364546cbb85204d941c152a47c6970ba7e1ef4559b6d1285894daab9a48e9` | Exact approved 146-member archive; no repacking |
| [Index](index.json) | 37,356 bytes; `ccf89747c7fbf2703c27a39aab00d66c0fc22dddac922c63b90b29cfc70a5580` | Every numeric member's SHA/size; 66 completed results, two completed setups, six unobserved entries |
| [Archive review](archive-review.json) | 830 bytes; `b4e91459da25f3ba97a3d791cd07b41aa5a783424704f010e6a91b307aa6ecf4` | Member/index equality, numeric/schema checks and publication boundary |
| [Selected metrics](metrics-summary.json) | Original analysis SHA/size and selected medians/ranges/totals | Readable projection of the complete numeric observations; no dropped failed event |
| [Extraction method](tools/README.md), [extractor](tools/extract.py), [manifest builder](tools/make_manifest.py) | Original frozen bytes; hashes in [validation](validation.json) | Evidence-analysis utilities only; no CI registration or product execution |

The archive contains all phase samples, mixed histograms/seconds/case counters, cumulative allocation/GC/CPU, resource samples, observer states and source-file hashes selected by the strict whitelist. It contains no source/generated/restore/environment copies, command arguments, connection strings or full logs. Original raw files stay local; a hash is not a claim that those full inputs are publicly downloadable. Exception text is retained only by fingerprint, with bounded public error fields where observed. The Chinese tool manual is preserved verbatim from its earlier preparation; this README states the actual completed pre-long scope.

## Same-query phase: cumulative improvement and a remaining regression

Each provider/producer ran three fresh processes. Within each process, ordinary Fluent, warmed `.Prepare()` and whole parameterized SQL use the same C++ Host/session, alternating typed tenant values 1/2 and fully checking 100 DTO rows. Across the three processes, each route aggregates nine steady windows / 2,304 operations. The earliest baseline, recovered implementation and current candidate all remain visible.

| Provider | Route | Earliest baseline B/op | Recovered B/op | Candidate B/op | Candidate vs recovered |
|---|---|---:|---:|---:|---:|
| sqlite | fluent | 72,661.63 | 21,471.08 | 26,904.63 | +25.31% |
| sqlite | prepared | 53,801.29 | 14,422.50 | 14,455.57 | +0.23% |
| sqlite | host-sql | 61,911.91 | 17,902.81 | 17,947.08 | +0.25% |
| postgresql | fluent | 72,663.47 | 21,473.64 | 26,909.31 | +25.31% |
| postgresql | prepared | 53,803.46 | 14,435.78 | 14,466.33 | +0.21% |
| postgresql | host-sql | 61,908.48 | 17,902.21 | 17,948.57 | +0.26% |

Ordinary Fluent remains **+25.31%** versus recovered, about **5.43 KB/op** on each provider. It is **62.97% lower than the earliest baseline**, and prepared is about **73.1% lower**. These are cumulative #37 comparisons; they cannot all be credited to the latest serializer. The older candidate's approximately 29.9 KB/op and this candidate's approximately 26.9 KB/op came from different frozen campaigns and do not establish a paired causal effect.

The candidate's four measured stages are shown below. Means are microseconds; total p99 is milliseconds, calculated from each operation's summed stages rather than the sum of stage percentiles.

| Provider | Route | Construct µs | Submit to first row µs | Read complete µs | Release µs | Total p99 ms |
|---|---|---:|---:|---:|---:|---:|
| sqlite | fluent | 164.98 | 1,168.85 | 10,378.23 | 2.78 | 32.39 |
| sqlite | prepared | 10.29 | 1,038.24 | 9,695.33 | 1.01 | 32.62 |
| sqlite | host-sql | 68.64 | 987.05 | 10,898.03 | 0.96 | 32.47 |
| postgresql | fluent | 161.45 | 1,388.48 | 8,063.72 | 3.48 | 30.33 |
| postgresql | prepared | 14.42 | 1,485.20 | 8,663.65 | 0.86 | 30.86 |
| postgresql | host-sql | 70.54 | 1,364.73 | 7,120.22 | 0.79 | 29.88 |

Full stage samples for all three producers remain in the archive. Timing ranges between processes are broad; no particular lock or timer is established as the cause. Phase timing excludes result verification while window allocation/GC/CPU/throughput includes it. First execution has stage timestamps only, after preparation/render/setup; it is not independent cold-process allocation or CPU. SQLite uses equivalent positional `?` versus Host `?1` spelling; PostgreSQL uses `$1`. These single-session observations do not replace mixed C8 or resource C16 workloads.

## Short mixed load: complete three-round comparison

All **36 cells** and both setups succeeded, with **zero failed operations, retries or oracle failures**. Each cell actually covered all 35 cases and passed count/digest/owner checks. The workload uses C8 persistent sessions, 20 requested seconds, 32 requested rows/batch, the same deterministic fixture and warmup; the completion tail is included. It contends on tenant 1 and includes writes to the same order. It does not establish independent-tenant scaling.

Each table entry is the median of three independent cells; GC is the three generation-count medians and RSS/PSS are medians of steady samples. [Selected metrics](metrics-summary.json) preserve min/max and pooled results; the archive preserves every observation. Ranges are descriptive, not confidence intervals. A median cell p99 differs from a volume-weighted pooled-histogram p99.

### SQLite

| Route | Mode | B/op | CPU µs/op | ops/s | Cell p99 ms | GC 0/1/2 | RSS MiB | PSS MiB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| before | dynamic | 91,443.18 | 1,483.66 | 468.26 | 239.08 | 209/2/1 | 39.63 | 38.11 |
| before | prepared | 68,084.75 | 1,383.85 | 485.83 | 201.33 | 162/2/1 | 42.93 | 41.41 |
| candidate | dynamic | 53,175.27 | 1,426.80 | 478.74 | 240.12 | 118/7/1 | 44.54 | 43.02 |
| candidate | prepared | 33,683.11 | 1,354.90 | 477.96 | 247.46 | 72/2/1 | 47.86 | 46.35 |
| dapper | dynamic | 10,786.61 | 277.40 | 13,052.16 | 5.21 | 692/2/1 | 32.00 | 30.52 |
| dapper | prepared | 7,080.37 | 269.29 | 13,004.69 | 5.01 | 447/1/1 | 33.06 | 31.59 |

### PostgreSQL

| Route | Mode | B/op | CPU µs/op | ops/s | Cell p99 ms | GC 0/1/2 | RSS MiB | PSS MiB |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| before | dynamic | 92,648.67 | 1,243.33 | 1,058.66 | 58.46 | 477/2/1 | 36.61 | 34.08 |
| before | prepared | 69,108.57 | 1,109.55 | 1,083.27 | 58.46 | 364/2/1 | 40.87 | 38.34 |
| candidate | dynamic | 53,197.13 | 1,182.12 | 1,052.90 | 57.67 | 245/72/1 | 42.23 | 39.71 |
| candidate | prepared | 33,792.59 | 1,084.94 | 1,102.45 | 58.46 | 163/31/1 | 45.53 | 43.01 |
| dapper | dynamic | 10,532.47 | 147.20 | 8,279.82 | 7.01 | 424/2/1 | 29.22 | 27.63 |
| dapper | prepared | 6,485.12 | 133.33 | 9,016.28 | 6.49 | 193/168/3 | 35.27 | 33.67 |

Candidate allocation falls **41.85%/50.53%** versus before for SQLite dynamic/prepared and **42.58%/51.10%** for PostgreSQL. It remains **4.93×/4.76×** Dapper.AOT on SQLite and **5.05×/5.21×** on PostgreSQL. Throughput and tail-latency gaps remain large; these observations do not establish Dapper parity or a uniform speedup over before.

Retain the memory and GC regressions: candidate steady RSS rises **12.39%/11.49%** on SQLite and **15.37%/11.41%** on PostgreSQL versus before. Some candidate cells have more Gen1 collections. Absolute GC counts depend on completed work; per-1,000-operation values and full counters are retained. Whole-process allocation/CPU includes DTOs, JSON, async state, verification and same-process native execution; PostgreSQL backend CPU is excluded. No framework-only subtraction or native heap attribution is available. Dapper's prepared route uses constant shape and generated `CacheCommand` reuse; physical preparation is not established, and Npgsql `MaxAutoPrepare` is zero. Mixed SQL/typed manifests are validated, without claiming a dispatch trace of identical SQL bytes for every case.

## Resource diagnostics: twelve qualified processes, with regressions retained

Six before and six candidate processes completed with original receipts marked qualified, exit 0, no observer errors and all six native-owner counts zero. Each process recorded one pending cancellation, two expected ResourceLimit outcomes and 16 incomplete first-Move returns in every raw burst. The expected exhaustion failures remain failed outcomes. No qualifier, consumer or build was rerun to produce this read-only comparison.

This is C16, processor override 4, three fresh processes per provider/version. Prepared resource queries return eight scalars without parameters; raw queries return one scalar after recursive work. Those workloads differ from the DTO phase and 35-case mix. Values below are descriptive medians across the three processes; repeated groups first calculate per-process ratios across all three repetitions.

| Boundary | Unit | SQLite before → candidate | PostgreSQL before → candidate |
|---|---|---:|---:|
| Cold source build | B/build | 280,792 → 300,000 (+6.84%) | 269,008 → 286,744 (+6.59%) |
| Cold 16-session open | B/interval | 36,112 → 37,416 | 36,232 → 37,368 |
| First Prepare + query dispose | B/interval | 34,352 → 28,664 (−16.56%) | 34,352 → 28,664 (−16.56%) |
| Warm raw, all three repetitions | B/query | 17,941.33 → 7,472.50 | 17,949.67 → 7,465.17 |
| Prepared c1, all three repetitions | B/query | 13,056 → 4,834.67 | 13,056 → 4,834.67 |
| Prepared c16, all three repetitions | B/query | 12,672 → 4,852.17 | 12,672 → 4,874.67 |
| Entire client process CPU | seconds | 2.552095 → 3.245132 (+27.16%) | 0.215314 → 0.190919 (−11.33%) |
| After-close-idle RSS | bytes | 17,670,144 → 18,092,032 | 15,269,888 → 15,437,824 |
| After-close-idle PSS | bytes | 16,078,848 → 16,502,784 | 12,636,160 → 12,802,048 |
| After-close-idle managed delta from before-source | bytes | 139,424 → 127,688 | 127,216 → 128,272 |

Allocation reductions coexist with more cold-build allocation, higher after-close-idle RSS/PSS and higher SQLite lifecycle CPU. All operation-window GC deltas are zero, but the separate forced-GC observations produce **18–19 collections per generation**; the whole process is not GC-free. Retained memory includes probe/runtime/async state and does not identify a pool or leak. CPU covers initialization, all bursts and idle periods. Raw tick windows lack a recorded Stopwatch frequency, so no per-window elapsed seconds, throughput or p99 is inferred. Native malloc/free costs, complete per-window PostgreSQL server CPU and an exclusive/stable CPU quota remain unproven. These resource processes provide no long-duration credit.

## Remaining gaps and why this candidate stays frozen

| Priority | Area | Implemented boundary and remaining work |
|---|---|---|
| P0 | Complete evidence | Finish and independently qualify all four 1800-second cells, verify full-case/error/retirement/duration conditions, rehash frozen inputs, then align Plan/Design and state the final limits. Current short/resource observations grant no long credit. |
| P1 | Dynamic construction | Complete NWQC submission, 22 clauses, topological blocks and typed sidecars are implemented; the private single-root serializer avoids generic temporary collections only for exclusive uncaptured commands. Ordinary Fluent still allocates about 25.31% more than recovered; remaining object-level allocation has not been attributed. |
| P1 | Parameter work | Eager runtime Prepare and immutable parameter expectation are implemented. Values still undergo managed frame construction and native parse/map/cell/encode transformations. Plan reuse is not in-place parameter binding or zero copying. |
| P1 | Physical statements | Connection-level physical statement reuse is **not implemented**. SQLite still prepares/finalizes; PostgreSQL uses unnamed prepare/describe/execute. Any future bounded cache must preserve source/connection/type/schema/session identity, error timing, transaction state and cancellation drain. No write replay or unknown-transaction retry is proposed. |
| P1 | Locks, queues and callbacks | ShapeCache only locks its internal LRU/accounting. Compile/hash and value processing are outside that lock; other admission/retirement/row gates remain. Missing wait/hold/queue and retry-timeline evidence prevents assigning the measured gap to a lock or the 10 ms retry timer. Historical spin sensitivity and the withdrawn dispatch experiment remain historical. |
| P2 | Batches and DTO mapping | Existing bounded batches, typed mapping, projection layouts and ownership cleanup remain. Batch validation/encoding and DTO/string/list allocation still cost work; phase read time is not proof of mapper-only cost. |
| P2 | Generator scope | Fixed-shape metadata can be generated, while Prepare is currently runtime/source/profile-aware compilation. Arbitrary Fluent build-time SQL compilation is not implemented. |

Do not add an unmeasured buffer pool to this frozen candidate. The static nine-record example allocates 1,792 bytes of array payload over 256/512/1024-byte arrays and copies 768 bytes during growth; headers/alignment were not measured. Even an ideal sequential hit cannot explain the full approximately 5.43 KB/op gap. C8 hit rate, clearing/atomic cost, retained capacity, clone/snapshot/failure recovery and late Dispose need separate evidence. Pooling remains unselected and unimplemented.

Stopping source changes now preserves a concrete candidate for the promised comparison. It does **not** mean the optimization space is exhausted, all performance goals are met, or Dapper parity is reached. Any later physical-cache, callback or pooling experiment needs its own design, correctness checks and newly frozen inputs.

Preserve both unresolved failures: the original PostgreSQL `r1-recovered` prepared abort −6, and SQLite B03 AOT CI `45622268417` abort −6 whose exception stderr was not uploaded. Three bounded PG diagnostics and eleven local SQLite invocations did not reproduce them. The deliberate PG missing-table Provider/42P01 failure validates the reporter, not the original cause. Current passes cannot replace those failures or claim they were fixed.

## Recalculation and validation

Use the exact numeric members listed by [index.json](index.json). Throughput is successful operations divided by effective seconds through drain; B/op is cumulative allocation delta divided by successful operations. Preserve failed/retry/oracle and every-second/every-case totals. For mixed p99, sum the retained 8192 bins and choose the first cumulative bin reaching `ceil(0.99*N)`; the upper-bound microseconds are `2^(i // 128) * (129 + i % 128) / 128000`. Pooled p99 requires summing bins first. Phase p99 uses individual summed-stage samples and the recorded Stopwatch frequency. No stage p99 addition or conversion to open-loop queue delay is valid.

The strict extractor retains raw-source SHA/size and explicit missing/failure states. Its `numericAndSchemaChecksPassed` verifies numeric/schema preservation; `performanceAcceptance` remains false. The archive's original SHA/index remain immutable as later long files arrive. Publish a new separately identified extraction for final results.

[Validation](validation.json) checks new JSON, links, archive/member hashes, selected metrics and preservation of the complete prior plan/handoff bodies. Existing historical gate results are explicitly reused; they were not rerun during measurement. Historical tools, graphs, acceptance and prior evidence are unchanged. This checkpoint adds no product, CI routing or workflow code.
