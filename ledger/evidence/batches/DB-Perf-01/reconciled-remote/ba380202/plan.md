# DB-Perf-01 — Linux x64 database performance campaign

## Authority and immutable inputs

The owner authorizes this batch's baseline, profiling, measured production changes, real database load, review, commits, PRs, normal merges, automatic preview follow-up and downloaded public-package Native AOT verification. This authority supersedes the earlier DB-Rename-01 stop-for-review restriction for this batch. It does not bypass branch rules or establish acceptance without execution.

| Repository | Observed main before this batch |
| --- | --- |
| [Korda](https://github.com/IzuSharp/Korda) | `771bc77cbd68d3f932b99ed2497c0697bbba5f02` |
| [Plan](https://github.com/IzuSharp/Plan) | `bc1956936ee77a997a016856c97def6aabc0bbc6` |
| [NativeWeave-Design](https://github.com/IzuSharp/NativeWeave-Design) | `d23fc89fb7436911b3f5a39995c7edb710a7be0a` |

Use `task/DB-Perf-01-linux` and task-named worktrees. The product baseline is immutable. Read [handoff-linux.md](handoff-linux.md) before resuming. A newer main does not silently replace this baseline. Public-contract changes require the corresponding Design update; implementation details with unchanged contracts do not require an invented API revision.

Scope: the existing C# Fluent ORM, source-generated mapping, Native AOT, independent PostgreSQL/SQLite packages and current C++20/libpq/sqlite3 execution on Linux x64. Preserve cancellation, ownership, backpressure, threading and result semantics. Ordinary Entity/DTO edits still require only a C# rebuild. No other platform or server product is part of this campaign.

## Evidence before optimization

The [allocation audit](allocation-audit.md) is source inspection, not a measurement. The [workload matrix](workloads.md) defines 30 business cases plus separate lifecycle cases; planned cases do not count as executed coverage.

1. Freeze toolchain, source and candidate package bytes. Validate the exact candidate `release.json`, nupkg entries, executable hashes and actually loaded native library hashes. Existing fixed-main producer artifacts may be reused only after all source and byte identities match; their prior correctness logs do not become DB-Perf-01 measurements.
2. Execute minimal real database Native AOT queries with the independent C# ORM. Record unsupported operations precisely. A raw driver probe is a separate diagnostic, never a substitute for the ORM column.
3. Implement the same dataset, seed, skew, indexes, transaction/durability policies, pool capacities, returned columns and complete result consumption in all four columns. Record both dynamic construction and query-structure reuse. Current Korda PreparedQuery reuses query shape; it does not currently retain a SQLite statement or a PostgreSQL named prepared statement.
4. Validate SQL, ordered typed parameters, results and durable state. Save PostgreSQL EXPLAIN and SQLite EXPLAIN QUERY PLAN outside the measured interval. Keep actual ORM results if plans differ, and add an identical-SQL diagnostic rather than replacing the ORM result.
5. Establish short full-process allocation and performance baselines before production edits. Compare multiple independent processes in an interleaved order. Use precise raw allocated byte differences and separately recorded GC generation counts. Never use rounded means, unobserved samples or absence of GC as a zero-allocation proof.

## Allocation accounting

Measure dynamic construction, plan reuse, binding, dispatch/completion, first and subsequent batches, batch-local rows, mapping, transaction control and session return. Exercise synchronous completion, actual asynchronous suspension and concurrency. Initialization, faults, cancellation and exhausted pools have separate records.

Every record states version, source hash, exact workload, measurement boundary, process, raw allocated bytes before/after, operation count, row count, known batch count and generation counters. End-to-end allocation and framework attribution are separate fields. A record whose attribution is unresolved remains `unproven`; it is not silently rounded or subtracted to zero. Requested DTOs/strings/lists/final arrays are business results. Temporary payloads, closures, boxing, operation tasks, retirement objects, leases and pool growth remain framework costs.

Use an empty driver/control, exact allocation stacks where available, or isolation to distinguish measurement and runtime activity. Put logging, identity hashing, SQL rendering, diagnostics that allocate, and result serialization outside the counter boundaries. A primitive result avoids business result allocation but does not by itself exclude harness/runtime allocation.

Zero-byte acceptance applies only to explicitly measured paths. Existing public Task and independently disposable object identities must not be reset or recycled in ways that change caller-visible semantics. A zero-byte batch-local row result cannot establish zero bytes per query, per batch or for the complete framework.

## Load and resource contract

Run short, heavy and mixed read/write workloads with a single connection, a concurrency ramp, saturation and recovery. Track planned arrivals, actual starts, completions, successes, failures, cancellations, rejections and retries without dropping queued or rejected work. Freeze one sustainable offered load for before/after latency comparisons, then independently find maximum successful throughput subject to the same error and tail-latency limits.

The acceptance campaign requires these eight serial segments on one dedicated Linux measurement resource. Each segment contains at least 1,800 seconds of effective mixed load; warmup, calibration, drain and idle observation are additional. Builds and unrelated workloads must not share the measured resources.

| Database | Direct C++ | Before Korda | After Korda | Independent C# ORM |
| --- | --- | --- | --- | --- |
| PostgreSQL | pending | pending | pending | pending |
| SQLite | pending | pending | pending | pending |

Each segment retains start/end times, effective duration, load/configuration hashes, raw time series, error taxonomy and result-validation receipts. Report successful ops/s, rows/s, p50/p95/p99, process user/system CPU seconds and CPU time per successful operation. Record steady/peak RSS, PSS where available, native heap allocation/free and peak, post-drain retained memory, idle CPU, and owner/connection/cursor return to zero or a specified steady state. PostgreSQL server and clients are separate; SQLite resides inside the application. Managed metrics are not applicable to direct C++; its native metrics remain required. SQL executions, protocol submissions and physical network round trips are distinct quantities.

## Iteration and release gates

For each measured bottleneck: retain the original raw run, make one scoped change, verify its local causal effect and correctness, then rerun the composite workload. Keep only repeatable improvements outside measured noise with bounded resources and acceptable tradeoffs. Record reverted attempts as well as accepted changes. Stop only with a documented accounting of the remaining hotspots and why further changes weaken semantics, transfer costs, or fail to produce repeatable improvement.

Normal PR CI runs affected correctness, short allocation regressions and independent-package AOT consumption. The eight long segments are a dedicated campaign, not routine PR CI. Preserve unchanged historical evidence and verifiers at their immutable inputs. Independent technical review does not impersonate another GitHub approver.

Merge verified code and its truthful evidence through normal repository rules. Observe merged-main checks and automatic preview publication. Download the actual public packages and verify AOT consumption of those bytes; if fingerprints are unchanged, record the actual release-skip decision. Missing measurements, a queued workflow, an open PR or a passing document gate are not product acceptance or publication.
