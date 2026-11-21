# Perf-01: completed SQLite application retry diagnostic

The isolated `a5748ad4` candidate completed the original SQLite mixed business/page workload with lower latency in all three descriptive process pairs, and with higher application CPU during load and post-recovery idle. Each of the six cells completed 3,001 scheduled business operations, including 1,501 independently reconciled durable mutations and 1,500 page operations. All original per-cell service predicates passed and all seven finite commands retired.

**Status: diagnostic evidence only; zero formal performance or duration credit.** This compares the current `2f40348c` product with isolated `a5748ad4`, using the same ordinary application and measurement driver. It is not the round-original EA5 before/final-after comparison, a direct Rust comparison, a capacity result, or a 30-minute test. The prior selected2f C16 result of **567.131236 ms p99**, compared with **232.540914 ms** for EA5, remains recorded as a failure. These later cells do not replace it or establish its cause.

[Exact projection](projection.json) preserves the original nanosecond values, scope counts, per-cell resources, input hashes, and runtime-loaded artifact identities. [Independent evidence verification](verification.md) describes what was checked and what was inherited from the completed original reader.

## Frozen workload and interpretation

| Property | Executed configuration |
|---|---|
| Order | current r1, candidate r1; candidate r2, current r2; current r3, candidate r3 (AB/BA/AB), fresh application processes and databases |
| Load | 50 scheduled business operations/s, C16 client pool, 60-second plan, 3,001 arrivals per cell; no rate or error-policy change |
| Mix | 1,501 create → same-key replay → operation-recovery business cycles and 1,500 keyset-page operations |
| Database | SQLite WAL, `synchronous=FULL`, `BEGIN IMMEDIATE`, 5,000 ms busy timeout, foreign keys enabled; 128 seed rows and 16 warm-up business operations |
| Transport | Actual HTTP/1.1 sockets, persistent bounded HTTPX client pool; application URI scheme `http`, no TLS in this database workload |
| Application | Ordinary typed Fluent queries, static JSON and DTO materialization; Release Native AOT; identical exception catch/log/rethrow observer |
| CPU affinity | Application CPUs 2–3; generator/controller/target CPUs 0–1; `DOTNET_PROCESSOR_COUNT=2` |
| Host/toolchain | Linux x64, kernel 6.18.57; AMD EPYC 9V74, nine visible logical CPUs; .NET SDK 11.0.100; original portable x86-64 build profile |
| Original service criteria | p99 ≤ 500 ms, application RSS ≤ 256 MiB, unexpected errors = 0, generator dispatch lag ≤ 100 ms |
| Resources | External procfs application sampler nominally 20 Hz; generator samplers nominally 1 Hz; original threaded sampling policy |
| Recovery/idle | 16 further business cycles, independent persistence reconciliation, then nominally 5 seconds idle before shutdown |

Latency is **completion minus scheduled arrival** for successful operations, preserving the original A21/database reader. The cycle and page rows are conditional subsets of the same mixed load; their CPU usage is not measured separately. `p50` is the original A21 percentile. The JSON also retains the original `statistics.median`, which differs from p50 for the even-sized page subset. Displayed milliseconds are rounded to six decimals and percentages to two; the JSON contains the original values. Changes below are `100 × (candidate/current − 1)`.

No new percentile, bootstrap, significance, or noise-classification method is introduced. The original per-cell predicates were reused by the diagnostic adapter without constructing a formal admission context. Three paired observations are reported individually; they are not pooled into a new acceptance result.

## Latency by paired process

### Whole mixed business workload

| Pair | Current mean ms | Candidate mean ms | Mean change | Current p50 ms | Candidate p50 ms | Current p99 ms | Candidate p99 ms | p99 change |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 35.368155 | 16.465751 | -53.44% | 19.733247 | 13.447028 | 187.392029 | 48.223489 | -74.27% |
| 2 | 32.846692 | 16.686517 | -49.20% | 22.435122 | 13.845969 | 151.600765 | 47.223354 | -68.85% |
| 3 | 32.479935 | 16.921575 | -47.90% | 22.322200 | 14.380664 | 177.929689 | 47.121026 | -73.52% |

### Durable business cycles

| Pair | Current mean ms | Candidate mean ms | Mean change | Current p50 ms | Candidate p50 ms | Current p99 ms | Candidate p99 ms | p99 change |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 57.458543 | 24.694820 | -57.02% | 44.657048 | 22.722777 | 278.046404 | 54.588361 | -80.37% |
| 2 | 51.893875 | 25.134382 | -51.57% | 44.677742 | 23.540239 | 172.238173 | 50.577345 | -70.64% |
| 3 | 51.163955 | 25.474740 | -50.21% | 42.307059 | 24.027137 | 211.891831 | 51.529426 | -75.68% |

### Keyset pages

| Pair | Current mean ms | Candidate mean ms | Mean change | Current p50 ms | Candidate p50 ms | Current p99 ms | Candidate p99 ms | p99 change |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 13.263040 | 8.231196 | -37.94% | 11.243643 | 7.269096 | 36.956476 | 20.367573 | -44.89% |
| 2 | 13.786812 | 8.233020 | -40.28% | 12.564647 | 7.019644 | 37.659860 | 18.712158 | -50.31% |
| 3 | 13.783460 | 8.362707 | -39.33% | 13.941242 | 7.432229 | 35.444306 | 19.878192 | -43.92% |

All six cells have exactly 3,001/3,001 successful measured business operations. The measured completion rate ranges from 49.936047 to 50.001308 successful business operations/s at the same offered 50/s; the small difference reflects the original finite observation window. This experiment does not test the maximum sustainable rate.

## Application resource cost

CPU percentages are relative to **one core**, not the two-core affinity allocation. They include the managed host, Rust/SQLite, HTTP server, and the application work. CPU samples span a slightly different interval from the request observation window. RSS is the original peak including the original overlap rule; no RSS trend slope is inferred from a one-minute cell.

| Pair | Load CPU current → candidate | CPU relative change | Load CPU seconds current → candidate | Peak RSS MiB current → candidate | Sampled idle CPU current → candidate | Idle last RSS MiB current → candidate |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 34.148601% → 38.764029% | +13.52% | 20.50 → 23.24 | 39.277344 → 35.781250 | 3.214995% → 5.429086% | 37.582031 → 35.562500 |
| 2 | 35.665474% → 38.559553% | +8.11% | 21.40 → 23.12 | 40.496094 → 35.265625 | 3.627632% → 8.072616% | 37.953125 → 35.304688 |
| 3 | 34.827923% → 40.348105% | +15.85% | 20.91 → 24.21 | 41.664062 → 35.140625 | 3.224286% → 7.716847% | 38.027344 → 35.203125 |

The original `post-load-idle` summaries already provide CPU measurements: their first/last CPU samples span 4.924–4.977 seconds within the nominal five-second phase. These are the values used above. The JSON separately records the explicit idle-phase UTC start/end and arithmetic from the before/after CPU endpoints, whose brackets include endpoint sampling overhead. The two intervals should not be mixed. Idle means after load and recovery while the server still listens; it precedes final shutdown.

During measurement the application observed 65–66 descriptors and 17 sockets at peak. During the sampled idle phase every cell observed 49 descriptors and one listening socket. The final consumer and database release flags were true, both completion statuses were `Succeeded`, and the server state was `Disposed`; the finite owner then recorded no remaining owned processes or children. Native byte-owner, pending-task, and callback-queue gauges are unavailable in this route, so the descriptor observations are not a substitute for those gauges.

**Managed GC collections and managed allocation counts are unavailable.** This application route is uninstrumented except for the identical exception observer. The deferred GC execution contract refers to the Python scheduler only; it does not measure or change application .NET GC. Database execution/lock/pool wait times, internal SQLite busy-handler attempts, per-operation FFI calls, and copied bytes are also unavailable in these cells.

### Generator observations

| Executed cell | Maximum dispatch lag ms | Controller CPU % of one core | Scheduler CPU % of one core | HTTP target CPU % of one core |
|---|---:|---:|---:|---:|
| current r1 | 18.655248 | 0.737068 | 6.908069 | 18.204441 |
| candidate r1 | 15.595453 | 0.658073 | 7.019457 | 17.784576 |
| candidate r2 | 7.536187 | 0.675388 | 6.449933 | 16.766401 |
| current r2 | 9.201143 | 0.652035 | 6.949736 | 18.360889 |
| current r3 | 5.919191 | 0.624479 | 6.903037 | 18.227919 |
| candidate r3 | 7.209270 | 0.708558 | 7.051917 | 18.018131 |

The original dispatch-lag predicate passed in every cell; all 3,001 planned operations were dispatched. These observations do not establish an untested generator saturation limit. Generator descriptor scans recorded transient misses from non-atomic procfs enumeration; their original counts remain in the JSON. Application CPU/memory/identity/affinity/descriptor error-sample counts are retained separately rather than treating every field as an atomic snapshot.

## Correctness, persistence, recovery, and retirement

For every cell, measured outcomes contain only `ok`: 1,501 cycles and 1,500 pages, with zero observed application errors/timeouts/cancellations, zero classified error outcomes, zero provider exceptions, zero SQLite BUSY/LOCKED observations, and zero explicit benchmark business retries. Same-key replay is an intentional business operation. Provider counts cover the complete application lifetime including startup/warm-up/recovery; they are not a measurement-only database-error count. Internal SQLite busy-handler attempts remain unobserved, so zero provider BUSY does not prove that no internal wait happened.

Independent SQLite queries saw **1,637 rows in each of items, operations, and outbox** after measured load: 128 seed + 8 warm-up mutations + 1,501 measured commits. The unchanged durable oracle passed. All 16 recovery cycles then succeeded; the independent pre-shutdown read and recovery oracle saw **1,653 rows in each table**. There were no attachment/blob operations in this mix. Across the six cells this is 18,006 successful measured business operations, 9,006 measured durable mutations, 9,000 page operations, and 96 separate recovery cycles.

| Executed cell | Original load start UTC | Last measured completion UTC | Original observation seconds | Original idle start → end UTC |
|---|---|---|---:|---|
| current r1 | 10:55:32.520506Z | 10:56:32.614346Z | 60.096867053 | 10:56:36.444458Z → 10:56:41.444873Z |
| candidate r1 | 10:56:48.252616Z | 10:57:48.269625Z | 60.018429617 | 10:57:52.077720Z → 10:57:57.078905Z |
| candidate r2 | 10:58:03.241038Z | 10:59:03.257657Z | 60.019570182 | 10:59:07.074528Z → 10:59:12.074943Z |
| current r2 | 10:59:19.086530Z | 11:00:19.146757Z | 60.062112707 | 11:00:22.981015Z → 11:00:27.981872Z |
| current r3 | 11:00:34.268756Z | 11:01:34.348676Z | 60.081482696 | 11:01:38.172482Z → 11:01:43.174339Z |
| candidate r3 | 11:01:49.223256Z | 11:02:49.256569Z | 60.035453174 | 11:02:53.082910Z → 11:02:58.083671Z |

All times above are on **2026-11-21 UTC**. The finite batch began at `10:55:26.769695Z` and completed, including its original-reader verification, at `11:03:10.257880Z`. The six short cells do not form a continuous 30-minute load and provide no 30-minute credit.

## What changed, and what the observations can support

The common typed application and driver come from `2e3995df8d86583ee9443348276ca8d918056bfc`. Managed product packages are current `2f40348c3db80a4fbee7a99e721b374a597b16df` versus candidate `a5748ad4e03825e3da7706d074887952da6c2d43`. Both consume the exact current2f precompiled Rust libraries. The candidate build check preserves the external lock closure, ordinary application source, exception observer source, and absence of consumer Rust compilation.

For public source navigation, the measured local commit `a5748ad4e03825e3da7706d074887952da6c2d43` maps to public commit `92fafc9146b86515689e99e48ec2ad651738a242` on `task/Perf-01-retry-linux`. The owner verified the identical Git tree `f2816e3364b90512958ca51e5d2c4c3f02766bb9` and byte equality of the eight changed source files. The links below use that public commit. The recorded build, loaded-artifact, measurement, projection, and verification identities remain the original local identities; this navigation mapping grants no measurement credit to a different tree.

In the tested candidate, [the database host](https://github.com/IzuSharp/NativeWeave/blob/92fafc9146b86515689e99e48ec2ad651738a242/src/Data.NativeHost/NativeHost.cs) and [server host](https://github.com/IzuSharp/NativeWeave/blob/92fafc9146b86515689e99e48ec2ad651738a242/src/Server.Native/NativeHost.cs) explicitly select a 1 ms coordinator retry interval, instead of the existing 10 ms default. [DataSource.Complete](https://github.com/IzuSharp/NativeWeave/blob/92fafc9146b86515689e99e48ec2ad651738a242/src/Data.NativeHost/DataSource.cs) awaits operation retirement; [AsyncOperation](https://github.com/IzuSharp/NativeWeave/blob/92fafc9146b86515689e99e48ec2ad651738a242/src/Interop.Async/AsyncOperation.cs) requests another retry when native retirement is pending. Shorter retirement retry delay is therefore a plausible contributor to the observed application latency change. This experiment does not measure that contribution separately, and it changes both active DB and Server hosts.

[CallbackCoordinator.Retry](https://github.com/IzuSharp/NativeWeave/blob/92fafc9146b86515689e99e48ec2ad651738a242/src/Interop.Callbacks/CallbackCoordinator.cs) in this candidate still scans the full fixed slot array and takes the reservation gate for each slot on every timer tick, including when many slots are empty. The observed higher active and idle CPU makes this a concrete follow-up target. Source inspection suggests a reason to investigate timer/scan work, but does not establish its exact share of measured CPU. A later scan optimization needs its own binary-bound repeat.

The candidate tree also contains the preceding gRPC buffer change. This workload runs HTTP/1.1 SQLite operations and does not exercise gRPC, but the complete source difference is recorded rather than presenting the experiment as a single database-only edit. These results establish a latency/CPU tradeoff for the specific tested candidate; they do not decide final retention or extend to PostgreSQL, TLS, codecs, or other concurrency levels.

## Actual artifacts and evidence identity

| Role | Tested package version | Runtime-loaded Native AOT executable SHA-256 |
|---|---|---|
| current | `0.1.0-perf01.recovery004.after.1` | `8257d25a2fa53e0f7d307e6541434b93b498a8c2ff8cc3617b2c9f12fd1d47b9` |
| candidate | `0.1.0-perf01.retry001.1` | `5107c9cf094124922bc224a235dcae352995ad89ef55324f717c3e916f5b5b3d` |

Both runtime load receipts identify these exact shared libraries:

| Loaded module | SHA-256 |
|---|---|
| `libnw_database_sqlite.so` | `63f01de214b727a6b7c976902e7f508f568ac08629a64c0332d67da028295346` |
| `libnativeweave_server.so` | `8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0` |

The PostgreSQL native asset is present in the package closure but was not loaded by these SQLite cells. The actual 17 tested `.1` package archives are listed in the projection from consumer receipts and are cross-checked against the package manifest **`previous`** member. The manifest `candidate` member contains a separate `.2` update witness and must not be reported as the tested version.

| Evidence | SHA-256 |
|---|---|
| `binding-retry-application-load-001/execution.json` | `d4283ad89fd634114c287424d1987c26fcd93f5c251eb3771847a2a15c77ae79` |
| `binding-retry-application-load-001/original-cell-checks.json` | `ad0375fb236a9eaa44b6addd0c46a6842c978aed96c8322d8eb136f02c932a46` |
| Actual six-cell plan | `f3fe22f1f3dddbde72634a016e8c6b22c140c06d56a8271a0e9e17e2fb193fbe` |
| Candidate ordinary application build check | `93ec52e4cda0952b74c3f0179c4b446ec3606374ecb85cbc040b6e08d267d80b` |
| This `projection.json` | `2115a4080ca67c8e0e5f76427b4814464b329907dee1120af2fd12c42277e40b` |

Raw evidence paths in the projection are relative to the owner’s `perf01-recovery/epoch-002` evidence root. Every original cell input, producer receipt, and finite control receipt is hash-bound there. The Git-tracked projection and review are directly readable with this commit. Raw archive storage/retention is tracked by the owner in the [Perf-01 handoff](../../../handoff-linux.md); this review does not claim a new archive upload.

## Reproduction

Use the committed common driver, the exact cohort package probe/observer paths in the projection, and a fresh output location. The original finite-plan recipe and six-cell mapping are in `diagnostics/binding-retry-application-001`; the plan SHA above identifies the executed population. The original per-cell command shape is:

```bash
taskset -c 2,3 "$PYTHON" "$COMMON_DRIVER/tests/Perf01.Database/run.py" \
  --package-probe "$COHORT_PACKAGE_PROBE" --observer "$COHORT_OBSERVER_MANIFEST" \
  --provider sqlite --protocol http1 --scenario mixed --stage short \
  --route nativeweave-aot-rust --variant after --rate 50 --seconds 60 \
  --concurrency 16 --generator-cpus 0,1 --warmup 16 --idle-seconds 5 \
  --recovery-requests 16 --continue-classified-overload --compact-observation \
  --scheduler-gc-policy deferred --resource-sampling-policy threaded \
  --max-p99-ms 500 --max-rss-mib 256 --seed 20261119 \
  --repetition "$REPETITION" --output "$FRESH_OUTPUT" \
  --isolation-note "Perf-01 isolated current2f/candidatea5748 ordinary application diagnostic; no formal comparison or duration credit"
```

The executed environment set `DOTNET_PROCESSOR_COUNT=2` and `PYTHONDONTWRITEBYTECODE=1`. The finite owner serializes cells in the recorded AB/BA/AB order and invokes the original `verify_cells.py --spec cells.spec.json` adapter after all six cells. Keep `--variant after`: it selects the existing native application route inside the driver, not a declaration that the isolated candidate is the final after version. Do not retarget old completed output directories or grant their results to another binary.
