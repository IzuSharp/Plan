# Perf-01 — completed scalar retirement diagnostic 002

**Six diagnostic processes completed.** Each ran 1,000 sequential SQLite scalar calls using the unchanged common-driver retirement probe. The candidate has lower observed mean, p99 and fixed-work process CPU time in all three corresponding pairs. These observations carry **zero formal performance credit**; the current processes also show substantial variation between repetitions.

## Workload and identities

- Current: `2f40348c3db80a4fbee7a99e721b374a597b16df`, package `0.1.0-perf01.recovery004.after.1`.
- Candidate: `a5748ad4e03825e3da7706d074887952da6c2d43`, package `0.1.0-perf01.retry001.1`.
- Common driver: `2e3995df8d86583ee9443348276ca8d918056bfc`; the original `tests/Perf01.Shared/RetirementProbe/Program.cs` SHA-256 is `d642d024ced08a2c5a6392e797b6de6ca904f59c7141e57ad0e5cf33a3fb3774`.
- Both roles actually reported `libnw_database_sqlite.so` SHA-256 `63f01de214b727a6b7c976902e7f508f568ac08629a64c0332d67da028295346`, built from current2f.
- Release Native AOT, Linux x64, `x86-64-v2`, two application CPUs, 20 warmup calls, 1,000 measured calls, maximum two connections and 128 batch rows. SQL: `SELECT CAST(1 AS BIGINT)`. Independent process order: current/candidate, candidate/current, current/candidate.

The candidate selects the existing coordinator retry interval at 1 ms in the Data and Server hosts; current2f uses the existing 10 ms default. Candidatea5748 also includes the isolated gRPC buffer experiment. This scalar database probe does not execute that protocol writer. The actual package provenance preserves 14 candidate-managed rows and three current2f native rows; the external consumer lock rows and NativeWeave package ID sets match. The lock-comparison receipt calls the current2f lock `before_lock_sha256`; that name does not mean the frozen EA5 performance baseline.

## Per-process observations

| Order | Role / repetition | Mean (ms) | p50 (ms) | p99 (ms) | Process CPU (ms / 1,000 calls) | Allocated bytes, including observer |
|---:|---|---:|---:|---:|---:|---:|
| 1 | current / 1 | 2.3247342 | 0.2974 | 22.7482 | 457.226 | 17,358,888 |
| 2 | candidate / 1 | 0.8388759 | 0.2932 | 7.6759 | 432.636 | 17,358,032 |
| 3 | candidate / 2 | 1.6963049 | 0.4491 | 8.8409 | 523.937 | 17,356,888 |
| 4 | current / 2 | 4.4089441 | 0.5030 | 28.8434 | 660.155 | 17,361,448 |
| 5 | current / 3 | 6.0682121 | 0.6723 | 28.5874 | 728.673 | 17,359,768 |
| 6 | candidate / 3 | 1.6826252 | 0.3347 | 11.9090 | 446.364 | 17,351,768 |

Each row has 1,000 call observations, 4,000 native-operation observations, GC collections `[8, 0, 0]`, and `SourceReleased = true`. The unchanged probe checks scalar values and actual retirement invariants before writing the result. Across the build and diagnostic stages, all **10 finite child commands** exited zero and retired, including the six workload processes; every receipt has empty live-owned and owner-child lists after cleanup. This is not a count of ten workload processes.

Mean is the arithmetic mean within one process. p50 and p99 use the additive receipt’s nearest-rank definition within that process; they are neither a mean of process p99 values nor a pooled multi-process tail. Process CPU is the `TotalProcessorTime` delta for the fixed 1,000-call loop. Allocation includes observer overhead. Initialization, warmup, final drain, module hashing and serialization are outside those counters. The sum of call intervals remains in JSON for audit; it is not used to derive a response rate, utilization or business throughput.

RSS, idle CPU, handles, threads, connection/queue series, a dedicated idle duration, post-close resource time series, native `TryRetire(Pending)` counts and isolated physical SQLite lock/pool waits are unavailable. These data do not establish the cause of the earlier formal SQLite business-tail failure. No EA5/direct-Rust comparison, A21 noise result, capacity qualification or 30-minute acceptance is supplied.

## Preserved failures and collection limitation

1. The original `001` metadata prerequisite failed before building a consumer because it incorrectly demanded candidate-managed provenance for all packages. The three native leaves correctly retain current2f provenance. Its failure execution and exit-1, retired, child-free receipt remain unchanged.
2. The corrected `002` commands, input pins, consumer and result paths were correct, but both actual plans retained `001` in `output_globs`. Consequently, **both original outer `outputs_sha256` inventories are empty**. The previous source-only review missed that collection-path error and is preserved.
3. A separate post-execution observation, `actual-artifact-and-scalar-summary-001.json` (SHA-256 `8060373ae233f3fd5cc108025ce1ab0f1d48d481d390045663ed39f4a79ade04`), pins the actual 18 files at `2026-11-21T10:50:43.145184+00:00`. It does not rewrite the plans, execution records, results or receipts and is not a rerun. This independent review recomputed the hashes of all 14 JSON entries, including the six results, and checked the other four binary digests against the existing manifest and actual run input pins without opening binaries.

## Provenance

- Build execution: `control-build-001/execution.json`, SHA-256 `3c94ef3d44bc5a5b07ec5bc65ba392e8e625b09a9e2bf88e92bcdf1542a5ab26` (three finite commands).
- Probe execution: `control-probes-001/execution.json`, SHA-256 `cf22e5e106cd2a8d0a137540fe95e55123d6ce682f7062a6e71a3c34a247465b` (six probes and one validator).
- Actual build/run plan SHA-256 values: `581f496430ce2f083f1ed9ffba19cfc3556fa3c8448eacb9cd9059098142b5e8` and `f539562bc5e1b3864491a657c2869acc18c626de236d79ba9c20422254cddc08`.
- Frozen recipe source index: `1f19611171491ff2ab7909f3d92f4511eff0db095327744869d7cbdce1662bc5`.
- [projection.json](projection.json) retains exact numeric rows, each result/receipt hash, the 18-file additive provenance list, identities, unavailable fields and the preserved failure hashes. It excludes operational maps, machine paths, process IDs, environment and raw native timestamps.

Preparation of this public projection performed no build, restore, import of target code, workload, timing-lock operation or binary hashing. Independent presentation review remains separate from the completed diagnostic execution.
