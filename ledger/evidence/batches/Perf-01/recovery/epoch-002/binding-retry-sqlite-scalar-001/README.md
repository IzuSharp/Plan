# Perf-01 — completed SQLite scalar retirement observations

**All six original scalar probes completed and retired. The candidate has lower descriptive call mean and p99 in each of the three process pairs.** These are instrumented, serial `SELECT 1` observations. They do not resolve the original SQLite C16 business-load failure, select a final product, or award formal comparison, capacity or long-duration credit.

This independent continuation review examined the completed small result files, original finite-owner receipts, producer metadata, package locks and exact source. It ran no application, build, fixture or workload. [projection.json](projection.json) preserves exact process observations, arithmetic definitions, source identities and filename/SHA-256 provenance. No raw per-operation timestamps or local operational paths are published here.

## What actually ran

The seven-command controller started **2026-11-21T10:43:19.002986+00:00** and ended **2026-11-21T10:43:37.268886+00:00**. Six commands ran fresh probe processes; the last checked their original outputs. All seven exited zero, retired, and reported no remaining owned process or owner child. The six processes completed **6,000 checked scalar calls and 24,000 recorded native operations** in total. Each result records source release.

| Identity | Current | Candidate |
| --- | --- | --- |
| Managed product source | `2f40348c3db80a4fbee7a99e721b374a597b16df` | `a5748ad4e03825e3da7706d074887952da6c2d43` |
| Native source | `2f40348c3db80a4fbee7a99e721b374a597b16df` | Same `2f40348c` source |
| Package version | `0.1.0-perf01.recovery004.after.1` | `0.1.0-perf01.retry001.1` |
| Recorded Native AOT executable SHA-256 | `7804b2281dbb49fb8ee4a571fd274a8057ea6e0ca05e507e90d4135d461e412f` | `dcba60831c9a0e632343818b6b3b693cceef6ab45934b9cb41fcfa5c4ee7ae71` |
| Actually loaded SQLite SHA-256 | `63f01de214b727a6b7c976902e7f508f568ac08629a64c0332d67da028295346` | Identical |

The original common source is `2e3995df8d86583ee9443348276ca8d918056bfc`. Both producers copied the identical `tests/Perf01.Shared/RetirementProbe/Program.cs`, SHA-256 `d642d024ced08a2c5a6392e797b6de6ca904f59c7141e57ad0e5cf33a3fb3774`. Their external package-lock rows match. Release Native AOT, `linux-x64`, `x86-64-v2`, the original producer and precompiled native assets were retained. The projection checks recorded manifest identities against the executed plan and loaded-module observations; it does not claim a new binary rehash or execution.

Each process opens one session, performs 20 untimed warmup scalars, then awaits 1,000 scalar calls sequentially. Every call must return exactly one from `SELECT CAST(1 AS BIGINT)`. The unchanged observer records four native operations per measured scalar. Source configuration keeps `MaxConnections=2`, `MaxBatchRows=128` and the other original defaults; application affinity is CPUs 2–3, the controller uses CPU 8, and the inherited execution environment sets `DOTNET_PROCESSOR_COUNT=2`. Each process has a separate new SQLite path and output. Order is current-1, candidate-1, candidate-2, current-2, current-3, candidate-3.

Current means the already selected `2f40348c` candidate, **not the round's original EA5 baseline**. The a5748 package has truthful mixed managed/native provenance. Neither role contains a direct Rust comparator in this diagnostic.

## Per-process scalar observations

Means are arithmetic means within one process. The descriptive p99 is nearest rank over that process's 1,000 original `PublicCallMilliseconds` values. No independent process samples are pooled. Changes below are `(candidate / current - 1) × 100`; they are not A21 decisions or confidence intervals.

| Pair | Current mean, ms | Candidate mean, ms | Mean change | Current p99, ms | Candidate p99, ms | p99 change |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2.324734 | 0.838876 | −63.92% | 22.7482 | 7.6759 | −66.26% |
| 2 | 4.408944 | 1.696305 | −61.53% | 28.8434 | 8.8409 | −69.35% |
| 3 | 6.068212 | 1.682625 | −72.27% | 28.5874 | 11.9090 | −58.34% |

The current means range from 2.325 to 6.068 ms and candidate means from 0.839 to 1.696 ms across these short processes. That variation remains visible; the paired arithmetic is not proof of a stable percentage gain. The process medians are much closer: current/candidate p50 values are 0.2974/0.2932, 0.5030/0.4491 and 0.6723/0.3347 ms. The original timestamps and values permit descriptive localization but do not supply arrival scheduling latency or sustainable throughput.

## Observed native-operation intervals

There are 4,000 observations per process. Values below are mean milliseconds per recorded native operation. These are internal observer boundaries, not independent database execution-time measurements.

| Pair | Role | Start → terminal fields copied | Terminal fields copied → before take | Before take → retirement observed |
| --- | --- | ---: | ---: | ---: |
| 1 | Current | 0.057328 | 0.012810 | 0.496043 |
| 1 | Candidate | 0.051017 | 0.012359 | 0.134412 |
| 2 | Current | 0.089514 | 0.011689 | 0.982188 |
| 2 | Candidate | 0.067518 | 0.009866 | 0.333074 |
| 3 | Current | 0.104909 | 0.015441 | 1.379464 |
| 3 | Candidate | 0.053177 | 0.016486 | 0.336500 |

The largest of these mean intervals remains before-take to retirement-observed in every process, and its candidate value is lower in each pair. It includes result taking/materialization, native quiescence, retry scheduling and the managed continuation observing retirement. The probe does not record native `TryRetire(Pending)` counts, each timer tick, physical SQLite lock waits or pool waits. It cannot assign all of this interval to the retry timer.

Every recorded interval checked here has nonnegative duration and all required timestamps are present. Terminal callbacks sometimes precede `StartReturned`; the source explicitly allows that ordering. The original `OperationTracker.Retired` accepts an observation only when Released and NativeQuiet are true, RootLive is false, and controls, callback entries and retained input bytes are zero. Its final check requires the recorded operation count to equal the retired count. The actual outputs and exit-zero receipts show those original checks completed; the result schema does not contain a separate status/error histogram.

## CPU and allocation: original measured-loop scope

| Pair | Current CPU, ms | Candidate CPU, ms | CPU change | Current allocated bytes | Candidate allocated bytes | GC gen0/gen1/gen2, both roles |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 457.226 | 432.636 | −5.38% | 17,358,888 | 17,358,032 | 8 / 0 / 0 |
| 2 | 660.155 | 523.937 | −20.63% | 17,361,448 | 17,356,888 | 8 / 0 / 0 |
| 3 | 728.673 | 446.364 | −38.74% | 17,359,768 | 17,351,768 | 8 / 0 / 0 |

CPU is the process CPU time recorded around the measured loop, not utilization or idle CPU. Managed allocation includes observer work in that interval. Initialization, warmup, final drain, module hashing and result serialization lie outside both counters. Allocated-byte changes are below 0.05% in all three pairs. A shorter elapsed loop can lower accumulated CPU even if timer activity per second increases, so these CPU totals do not remove the full-application timer-cost question. RSS, queues, descriptor/thread counts, idle CPU and a post-close resource time series are unavailable in this original probe.

## Source interpretation and next decision

The relevant database delta is the existing `CallbackCoordinator` argument in `Data.NativeHost/NativeHost.cs`: the domain selects 1 ms instead of the unchanged 10 ms default. `DataSource.Complete` still awaits each operation's `Retirement`. `AsyncOperation.Process` still requests a coordinator retry when native `TryRetire` returns Pending, and the unchanged coordinator's periodic scan calls eligible contexts again. This source chain supplies a plausible scheduling mechanism to investigate; the present traces do not prove which events incurred timer waits.

The complete a5748 versus 2f source diff also contains the earlier gRPC buffer implementation and the Server retry argument. The standalone scalar program creates only a database source, and each actual loaded-native list contains only SQLite. These processes provide no Server, gRPC or PostgreSQL execution result. The shared coordinator implementation remains unchanged here, including its complete-slot-array scan and lack of a whole-scan overlap guard. Any later scan-bound change is a different candidate requiring its own actual evidence.

The appropriate next decision uses the existing full C16 application workload and its independent persistent-state oracle, with the same offered rate, concurrency, BUSY/retry accounting, tail standard, resources and drain checks. It must also examine open-idle CPU and the other affected database/Server paths before final selection. These scalar probes issue no writes or transactions, contain no dedicated cancellation case and cannot establish persistent-business equivalence. Their success does not replace the original 567 ms failed C16 sample or the separate 186/167 ms instrumented business probes.

## Reproduction and retention

The original command shape is:

```sh
taskset --cpu-list 2,3 ACTUAL_ROLE_AOT_EXECUTABLE \
  sqlite FRESH_SQLITE_PATH 1000 FRESH_RESULT_JSON
```

Use the already reviewed `binding-retry-retirement-002` finite recipe, actual source/package identities and original owner for any new execution. A changed binary or workload requires new output; this report does not request another scalar run. The candidate consumer was prepared from the existing exact B24 `.1` feed through the unchanged `tests/Perf01.Shared/prepare.py --probe retirement` producer.

Exact result, receipt, execution, producer, lock and source hashes are retained in the JSON. Paths there are relative to `epoch-002` unless explicitly identified as repository source paths. This curated projection is intended for Plan Git history retention; original raw-file retention and any archive readback remain the owning handoff's responsibility. No raw archive persistence is asserted here. The earlier recipe-001 source-admission failure remains separate and unchanged.
