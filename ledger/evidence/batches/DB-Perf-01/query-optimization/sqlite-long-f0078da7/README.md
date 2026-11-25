# SQLite long comparison — halfway checkpoint, f0078da7

**SQLite candidate and Dapper.AOT each completed one validated 1800-second mixed-load segment. The campaign is 2/4 complete; PostgreSQL has no completed result at this checkpoint.** This record preserves the actual SQLite gap and numeric evidence. It grants no final performance acceptance, merge or release.

## Identity and recovery

Continue [Korda #37](https://github.com/IzuSharp/Korda/pull/37), [Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and [Plan #34](https://github.com/IzuSharp/Plan/pull/34). Product head remains [`f0078da720e07031bc56464995af6791c41aaae8`](https://github.com/IzuSharp/Korda/commit/f0078da720e07031bc56464995af6791c41aaae8), tree `1e56f5466fa02640dcb68389f283e5c03c2c09ec`, actual CI package producer `46ef09477b75dd5ce05e1941a739652bc685a9e2`. Ordinary [CI 45624813071](https://github.com/IzuSharp/Korda/actions/runs/45624813071) passed; independent PostgreSQL/SQLite package validation and zero benchmark CI jobs remain unchanged.

At **2026-11-25 15:10:38 UTC**, root started PostgreSQL coordinator session **34628**, running Dapper.AOT 1800 seconds followed by candidate 1800 seconds. Inspect that existing coordinator and local results before resuming; no parallel consumer, build or heavy gate belongs in the measurement window. Both PostgreSQL result slots remain pending/null here. The archive was captured **before** this launch and retains three `not_observed` entries: PostgreSQL setup and both long cells.

The [previous checkpoint](../prelong-f0078da7/README.md) remains unchanged, including its 18 phase processes / 41,472 steady queries, 36 short cells / 3,004,197 successful operations, 12 qualified resource processes and earlier archive. Its Plan [CI 45634587096](https://github.com/IzuSharp/Plan/actions/runs/45634587096) passed for parent `8cb3f6d0970ef18894ea5bb02022916f9710772b`; it is not the future CI result for this new checkpoint or the final documents.

## SQLite results and actual remaining gap

The same frozen prepared-mode C8, 35-case hotspot workload completed **882,740 candidate** and **24,682,301 Dapper.AOT** business operations, returning **21,539,310 / 602,248,666 rows**. Both have zero failed/retried operations and zero oracle errors. The raw receipts contain no independent `Rejected` counter: the helper's retained `rejected: 0` is a closed-loop normalization default, not a measurement of externally offered arrival rejections. Full-case, count, row/digest, second-bucket, histogram, duration and cleanup validation passed. Every case succeeded 25,216–25,224 times for candidate and 705,203–705,211 times for Dapper.

| Route | Actual seconds | Successful ops | ops/s | B/op | GC 0/1/2 | CPU µs/op | p99 ms | Steady RSS/PSS MiB |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| candidate | 1800.086514 | 882,740 | 490.39 | 33,855.12 | 6812/1424/18 | 1,326.08 | 220.201 | 47.82/46.31 |
| dapper | 1800.004579 | 24,682,301 | 13,712.35 | 7,080.69 | 42483/431/18 | 266.49 | 4.915 | 34.52/33.01 |

Candidate allocation is **4.7813×**, CPU/op **4.9760×** and p99 **44.8×** Dapper; achieved throughput is **3.576%** of Dapper. Steady RSS/PSS are **38.56% / 40.29% higher**. These observed gaps do not support Dapper parity or a uniform resource improvement.

GC must be interpreted with completed work. Per 1,000 successes, candidate Gen0/1/2 is **7.71688 / 1.61316 / 0.020391**; Dapper is **1.72119 / 0.017462 / 0.000729**. Raw GC counts and cumulative allocation/CPU endpoints remain in the numeric archive and [state](state.json); more absolute Dapper Gen0 collections do not mean more GC per operation.

All **30 full minute buckets** show positive business progress: candidate **27,798–31,661** operations/minute; Dapper **783,571–865,095**. The post-1800-second tail is separately reconciled: **eight operations / 87 rows** for candidate and **eight operations / 139 rows** for Dapper. The 1,802 second buckets per cell are not truncated. Full 35-case coverage is established over each whole cell; per-minute/per-worker case identities were not serialized.

**Ownership instrumentation is asymmetric.** Korda's six tracked native/framework owner categories are zero. Dapper's observed `ApplicationConnections` is zero; its internal commands, readers and native owners are not instrumented. Do not label that as symmetric proof of all native owners being zero.

Each route has one continuous long observation, without independent repetitions, confidence intervals or causal attribution. SQLite has one writer and these cases contend on tenant 1; this is closed-loop achieved capacity/service latency. Requested prepared mode means Korda plan reuse where offered and Dapper constant shape/generated `CacheCommand` reuse; physical preparation parity is not established. Raw/related/CRUD/transaction paths keep their documented construction costs. Allocation/CPU includes DTOs, JSON, harness state and in-process native work. Steady sampled RSS/PSS, final-window readings and process-lifetime peaks remain separate. Exclusive CPU or a stable cgroup quota is unproven; no missing server CPU/native heap attribution is synthesized.

## Evidence and immutable capture boundary

| Evidence | SHA-256 / size |
|---|---|
| [Numeric archive](DB-Perf-01-evidence-v4-sqlite-long-numeric.tar.gz) | `8a9ec3f27dc3199d2e530dc03cc105cc4693bfd8554c06ea358848e9e41726eb`; **1,569,537 bytes** |
| [Index](index.json) | `78c45acae547aafb916719a09ea2fbc9e9d6fbe80ca1613c8f48a4fc014343d4`; 37,853 bytes |
| [Archive review](archive-review.json) | `e5725753392afb819a485c7d70036f3b16b42f30bf5b921781177f7d697def08`; 830 bytes |
| Frozen helper's SQLite summary, retained locally | `43c8dbbcd080ea7dc80c4c63c50b7dae09a92996f022019a1e9505a5cdb447f4`; 108,888 bytes |
| Independent SQLite comparison, retained locally | `86f618c5439f660723a686c05508ecb0f0380914d72ebd3874fb01e042d9762d`; 101,214 bytes |

The archive is the exact approved **149-member** projection, Git blob `82f50f4e8bfc80a03f6226f11148b8621dd2f447`. Its index contains **68 completed results + three completed setups + three not-observed entries**. Every member matches the index hash and size. It retains original result/observer hashes and public producer/ELF/package identity; the full input manifest, source/generated/restore/environment files, command arguments, connection strings and complete logs are not published. Original raw inputs remain local. The [existing extraction method](../prelong-f0078da7/tools/README.md) describes the numeric whitelist and recomputation boundary; no tool or CI route changes here.

The same freeze still binds **16 apps / 926 files**, SHA `f83df84a57af07a927f4955b91e8a64561bccafa8f92d2bd7181bc3a83efa269`. Full post-run verification, the remaining PostgreSQL cells, final numeric archive and final document CI remain pending. Never mutate this archive's earlier missing states when later results arrive.

## Remaining work and preserved failures

Complete and independently verify both PostgreSQL long cells, then reconcile all four actual results, rehash frozen inputs and align final Plan/Design. Preserve ordinary Fluent's **+25.31% phase allocation versus recovered**, cumulative-before versus current differences, the short/resource memory/GC/CPU regressions, unimplemented physical statement reuse and arbitrary build-time Fluent SQL, and unproven lock/timer attribution. No buffer pool or callback change enters the frozen candidate.

The original PostgreSQL prepared abort and earlier SQLite B03 CI −6 remain unexplained. Later successes, three PG diagnostic non-reproductions, eleven local SQLite non-reproductions and the separate deliberate missing-table error do not establish their cause or repair. Earlier evidence, acceptance, tools and historical bodies stay unchanged. [Validation](validation.json) records only lightweight evidence/document checks; it does not supply the missing PostgreSQL result or final performance acceptance.
