# Zero-cost-05: independent reconciliation of 12 cells

**Result: the 12-cell raw/validation/controller/summary reconciliation passes. These observations show lower whole-process CPU and managed allocation than the earlier Korda build; they do not establish execution-path parity with Dapper.AOT.**

The independent reviewer completed 373 checks by reading small sealed JSON files and arithmetic fields. No workload, build, profiler, archive, large binary hash, or resource-JSONL replay ran.

## Completeness and identity

All 12 cells have 35 unique case IDs, all cases succeeded 428 or 429 times, identical seeded row/digest oracles across both providers and all variants, and untruncated time series. Each cell records 15,000 successes and 366,067 consumed rows. The total is **180,000 successes and 4,392,804 rows, with zero rejection, business failure, retry or outstanding request**. Tracked owners returned to zero.

The controller plan/hash, per-cell validation hashes and raw-result hashes match. Controller intervals and actual measured intervals are serial. The first SQLite candidate cell was reused exactly once from its earlier completed run; its controller reuse timestamp is not a second execution. Wrapper v1/v2 provenance remains explicit. Actual ELF/native/package/route identities are stable between rounds for each provider/variant.

All cells are 30 seconds at 500 offered operations/s, queue 64, 32 rows/batch, 8 tenants and 1,024 orders/tenant, prepared/persistent mode, 64 warmup operations per worker outside measurement and five idle seconds after release. SQLite uses four workers and PostgreSQL eight. No cell grants final 30-minute credit.

## Client process CPU and managed allocation

| Provider / round | Before CPU µs/op | Candidate CPU µs/op | Dapper CPU µs/op | Candidate vs before | Candidate / Dapper | Managed B/op saved vs before |
|---|---:|---:|---:|---:|---:|---:|
| sqlite / 1 | 3258.737 | 2948.235 | 2382.410 | -9.528% | 1.2375× | 4888.965 |
| sqlite / 2 | 3106.337 | 2928.883 | 2376.806 | -5.713% | 1.2323× | 4896.716 |
| postgresql / 1 | 3100.712 | 3015.192 | 2354.366 | -2.758% | 1.2807× | 4895.018 |
| postgresql / 2 | 3247.526 | 2981.220 | 2352.630 | -8.200% | 1.2672× | 4898.989 |

The four CPU differences are all negative, from **−2.758% to −9.528%**. Candidate managed allocation is lower by **4,888.965–4,898.989 B/op**; this is about 18.79–19.09% of the earlier process allocation. Candidate still allocates about 20.74–21.16 KB/op, against Dapper about 7.47–7.57 KB/op, so its process allocation ratio remains approximately 2.74–2.83×. Native allocation and framework-only managed allocation are explicitly unknown.

The process CPU ratios of **1.2323–1.2807× Dapper** include the dedicated `db-perf-arrivals` producer. Its `WaitUntil` spins with `Thread.SpinWait(32)` when the remaining delay is at most `Stopwatch.Frequency / 500` (2 ms), as well as including harness, driver/framework and business DTO work. A shared additive CPU cost can make the aggregate ratio look closer to one than the database execution components are. This review neither subtracts an assumed producer budget nor calls that aggregate ratio execution-path parity.

## Tail latency and retained-memory regressions

| Provider / round | Service p99 vs before | Scheduled p99 vs before | Released idle RSS vs before | Peak RSS vs before |
|---|---:|---:|---:|---:|
| sqlite / 1 | -38.776% | -55.263% | +6.784% | +0.353% |
| sqlite / 2 | -4.516% | -7.514% | +3.762% | -2.637% |
| postgresql / 1 | -1.075% | +26.238% | +7.310% | +0.714% |
| postgresql / 2 | +8.247% | +17.593% | +9.869% | -0.450% |

SQLite service/scheduled p50, p95 and p99 improve in both rounds. PostgreSQL p50/p95 improve in both rounds, but its scheduled p99 rises in both rounds and service p99 changes direction. Candidate released-idle RSS is higher than before in all four comparisons; peak RSS changes direction. These observations must remain beside the CPU/allocation improvements. Lower allocation volume does not itself prove lower retained RSS. No mechanism is assigned to these regressions from these cells alone.

All service, scheduled-to-completion and start-delay p50/p95/p99 values were independently reconstructed from their raw histograms, each accounting for all 15,000 successful operations. The values are bin upper bounds rather than exact individual latency order statistics. Two rounds show observed direction and variability, not a confidence interval.

## GC, RSS and PostgreSQL server scope

| Cell | Process GC pause (s) | Gen0 / Gen1 / Gen2 | Peak RSS through snapshot (B) | Released idle RSS (B) |
|---|---:|---|---:|---:|
| round-01-sqlite-candidate | 0.108343 | 98 / 16 / 2 | 44220416 | 42295296 |
| round-01-sqlite-before | 0.151635 | 139 / 21 / 2 | 44064768 | 39608320 |
| round-01-sqlite-dapper | 0.053510 | 53 / 3 / 1 | 30806016 | 30670848 |
| round-01-postgresql-candidate | 0.124793 | 95 / 8 / 2 | 50278400 | 46661632 |
| round-01-postgresql-before | 0.149937 | 141 / 16 / 2 | 49922048 | 43483136 |
| round-01-postgresql-dapper | 0.059324 | 33 / 4 / 2 | 38965248 | 38973440 |
| round-02-postgresql-dapper | 0.070077 | 35 / 4 / 2 | 39378944 | 39387136 |
| round-02-postgresql-before | 0.200164 | 139 / 25 / 2 | 48238592 | 41418752 |
| round-02-postgresql-candidate | 0.133091 | 98 / 10 / 2 | 48021504 | 45506560 |
| round-02-sqlite-dapper | 0.062301 | 53 / 3 / 1 | 30953472 | 30777344 |
| round-02-sqlite-before | 0.117672 | 131 / 23 / 2 | 45207552 | 39960576 |
| round-02-sqlite-candidate | 0.111367 | 98 / 13 / 2 | 44015616 | 41463808 |

Every GC-pause value equals the raw post/pre process-tick delta divided by 10,000,000. GC counts and pauses retain process scope. Released RSS follows tracked-owner release and about five seconds idle without forced GC; the peak snapshot precedes that idle period, so the two observations need not have identical peak boundaries.

| PostgreSQL cell | Observed inner CPU (s) | Observed outer CPU (s) | Separate wait4 lifetime CPU (s) |
|---|---:|---:|---:|
| round-01-postgresql-candidate | 7.88 | 8.16 | 9.216934 |
| round-01-postgresql-before | 7.13 | 7.34 | 8.296673 |
| round-01-postgresql-dapper | 7.06 | 7.51 | 8.176929 |
| round-02-postgresql-dapper | 6.16 | 6.71 | 7.339855 |
| round-02-postgresql-before | 7.59 | 8.02 | 8.760771 |
| round-02-postgresql-candidate | 8.09 | 8.42 | 9.282264 |

The visible inner/outer endpoint arithmetic and monotonic flags match each validation. Candidate observations are higher than before in both rounds, but these non-atomic process-tree observations are not exact steady CPU bounds or a causal server-cost attribution. The separate wait4 lifetime also includes startup, fixture initialization, warmup, idle and shutdown. None of these server values are added to the client CPU metric or to each other; unobserved exits/transfer loss remain unknown.

## Recommendation and recovery

Retain the repeated CPU/allocation improvements and continue the planned pressure/final measurements under their own frozen conditions. Do not claim complete performance alignment, improved PostgreSQL tails, lower retained memory, framework-only 0 B, or exact PostgreSQL steady cost. At this lane's fixed arrival rate, roughly 500 completed operations/s is delivery of the offered load, not measured sustainable capacity.

The machine-readable review contains all per-cell inputs, hashes, 35 case IDs, checks, resource values and recomputed comparisons. The full source-of-truth raw/validation/controller files are unchanged. Later pressure measurements are separate and were not read or included in this review.

## Exact primary small-input identities

- `experiments/recovery/zero-cost-05/series-01.plan.json`: SHA256 `79c346fe2ba0283ffcc475e0e38e5c380fa9200d8d5fd2c9a6f4619e9eba4d8f` (4955 B).
- `experiments/recovery/zero-cost-05/series-01.plan.resume.json`: SHA256 `29b850fcb1ab54d2c4e43474481d5548aa3b95d2fee03fcbb8675da2607a57b5` (19939 B).
- `experiments/recovery/zero-cost-05/summary.json`: SHA256 `f804253e2ccf8baa74165c7ca4597e355eb2da8dd3549c0bbf5ef24f044d4728` (29542 B).
