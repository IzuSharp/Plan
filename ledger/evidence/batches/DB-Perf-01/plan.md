# DB-Perf-01 — Linux database and Fluent ORM performance

## Authority, scope and current state

The owner authorizes baseline recovery, profiling, production improvements, real
database load tests, scoped independent review, commits, PRs, normal merges,
repository-triggered preview publication and verification of the actual public
packages. The scope is Linux x64 PostgreSQL and SQLite, C# Fluent ORM, generated
mapping and Native AOT over the current C++20/libpq/sqlite3 implementation.
Preserve the existing public API, `Db*` attributes, two independently installable
provider packages, ownership, cancellation, backpressure and thread safety.
Ordinary Entity/DTO edits must continue to rebuild only C#.

Use `task/DB-Perf-01-linux` and task-named worktrees. Implementation and benchmark
sources belong in Korda; plans, raw measurement indexes, decisions and the
[recovery entry](handoff-linux.md) belong here. Synchronize NativeWeave-Design
before accepting any public contract change. The current authorization supersedes
earlier task exclusions and review-only stop instructions; it does not authorize
bypassing checks, altering historical evidence or claiming unexecuted acceptance.

The [baseline](baseline.json) fixes Korda main
`771bc77cbd68d3f932b99ed2497c0697bbba5f02` and Plan main
`bc1956936ee77a997a016856c97def6aabc0bbc6`. Both original provider candidate
archives from that exact Korda main have been recovered and independently hashed.
No DB-Perf-01 performance result is established by their earlier correctness
checks. The separate [before diagnostics](checkpoints/before-internal/summary.json)
now retain actual internal allocation counters; they are not public-provider
acceptance. Current accepted long-test credit is **0/8, 0 effective seconds**.
The [acceptance record](acceptance.json) remains incomplete.

Concurrent Plan commit `ba380202e7b36cbfe8dcd4bc2cfa0afe86048d92` was discovered
after the first local checkpoints. Its `preflight/` observations and reviews are
preserved alongside the local `checkpoints/` records. The original overlapping
reports, read-only artifact verification and reuse limits are retained in the
[reconciliation record](reconciled-remote/ba380202/README.md). Source-bound narrow
public zero-byte rows from its lazy-only experimental candidate remain useful;
they are not rebound to the final optimized package. Maintain both histories and
use a normal expected-head fast-forward when publishing reconciled records.

## Comparable four-column baseline

| Column | Required executed entry and accounting boundary |
| --- | --- |
| Direct native C++ | The same pinned Clang Release configuration, directly using the same libpq or sqlite3 version. Construct or reuse equivalent queries, bind parameters, consume every selected row, materialize equivalent data, commit/roll back and release resources. Include this work in the measured business operation. |
| Korda before | The exact fixed-main original candidate package for each provider, consumed by an ordinary C# project outside the source tree through PackageReference, public Fluent APIs and Linux Native AOT. |
| Korda after | The same consumer application, driver settings and dataset, changing only the final candidate package. Retain package, executable and actual loaded-native SHA-256 identities. |
| Independent C# ORM | A mature ORM demonstrated by a minimal Native AOT query against the real database before the campaign. Pin version and provider; select separately by database if necessary. Report actual unsupported business cases and reasons. A raw-SQL driver short test is separately labeled and does not fill an unexecuted ORM cell. |

Freeze machine identity, available cores and quotas, database/driver versions,
dataset and indexes, transaction isolation and durability, connection/pool policy,
cache temperature, result shape and row count. Dynamic-query cells construct on
every route; prepared-query cells reuse on every route. Never compare a native
scalar result with a fully materialized managed DTO/list without accounting for
the difference. Verify emitted SQL, parameter order/types/values, execution plans,
complete results and independently observed persisted state.

When the independent ORM generates a different plan, retain its actual result
and add a same-SQL layered comparison. Report SQL execution count, protocol
submission count and measured physical network round trips separately; neither
existing Korda counter is a network round-trip measurement.

## Environment admission and recovery

The current sandbox is useful for source inspection, builds and short diagnostics,
but has **not** been qualified as the dedicated long-test environment. The
[read-only observation](recovery-observations.json) records nine visible affinity
CPUs and a /proc memory total; those observations do not establish exclusive
physical cores, stable CPU/memory quotas, service isolation or a host lifetime.
The observed `/sys` CPU and cgroup quota files were absent. There is no recorded
exclusive reservation, isolated PostgreSQL service accounting or before-only
noise calibration. Inspected repository workflows use ordinary `ubuntu-24.04`
jobs, not a configured dedicated benchmark runner.

Admission must establish and retain a single measurement environment identity,
resource ownership, fixed affinity/quota policy, database placement and independent
client/service measurement, free storage for binaries and raw time series, tool
versions, and baseline noise from interleaved independent processes. Build and
background tasks must stop during each admitted measurement. All eight long
segments use that same admitted resource set exclusively. Do not spend four hours
on an unqualified host and later label the duration accepted.

On interruption, read this batch's handoff, actual remote branch/PR heads and
completed receipts before acting. Reuse a result only when its source/binaries,
workload, dataset, input parameters and admitted environment match. Preserve
failed and rejected runs. Recovered toolchains and package bytes are useful
inputs; recovered old observations do not inherit new source or host identities.
Historical Perf-01 long credit was already zero and its Rust/server measurements
do not transfer to this C++ database batch.

## Framework allocation acceptance

Start from the [source allocation inventory](allocation-inventory.md), then
measure both providers through normal public APIs. Cover dynamic construction,
prepared-plan reuse, binding, submission/completion, refill batches, row reading,
generated mapping, transaction start/commit/rollback and connection return. Each
has synchronous-completion, genuinely suspended asynchronous and concurrent
variants where applicable. Record framework bytes per operation, batch and row;
zero bytes per row does not erase query or refill cost.

After warmup, measure whole-process managed allocated bytes in an independent
consumer process, with operation/row totals and each generation's GC count. The
boundary includes callbacks, thread-pool continuations and other worker threads.
Record cumulative integer byte counters **before** division. Combine empty-driver
controls, allocation stacks or narrowly isolated experiments to attribute costs.
Sampling with no hit, rounded means and absence of a GC collection are not zero
allocation evidence. Give every passed production path a short reproducible
regression gate with the original raw counters, exact version/input and boundary.

Report end-to-end allocation and framework-owned allocation separately. Required
business DTOs, strings, lists and result arrays are explicitly charged to the
business result; temporary arrays, closures, boxing, asynchronous state, wait
objects, leases and pool growth remain framework costs. Initialization, failures,
cancellation and pool exhaustion have separate rows. Check bounded pool capacity,
native allocation and copying, steady/peak/retained memory and ownership drain;
unbounded retention or shifting bytes into native memory cannot establish success.

The existing public `Task<T>` APIs expose independently retainable completion
objects. Their genuinely asynchronous per-operation result/completion paths
cannot be reset and reused arbitrarily without changing caller-visible Task
semantics. Current code also explicitly creates TaskCompletionSource owners.
This is a concrete source/contract limitation, not a measured byte count. Preserve
the API while removing avoidable costs and record any remaining Task allocation
as framework-owned. A zero-allocation row path must never be described as a
zero-allocation framework. Any residual allocation is **unmet**; attribution that
cannot be established is **unproven**. Both remain visible in the final report.

## Business correctness and short workloads

Implement at least **24 semantically distinct business cases on both databases**
in a frozen manifest, including optional filters, multi-table joins,
aggregation/HAVING, composite-key cursors with ties and empty boundaries, deep
offset pages, batched association loads including empty relations, narrow/wide
DTOs, large streaming results, NULL, typed JSON and decimal. Include transaction
reads/writes, partial updates, concurrency conflicts, rollback, cancellation and
early enumeration disposal. Add subquery, CTE, window or set-operation cases
according to actual support; list Fluent and handwritten SQL coverage separately.
Unsupported capabilities must be explicit rather than silently dropped.

Use a fixed skewed/hotspot dataset with empty associations. Exercise short and
heavy queries and mixed concurrent reads/writes, single connection, concurrency
ramp, saturation and post-saturation recovery. Interleave independent processes
to estimate noise. Freeze a sustainable offered load for before/after tail-latency
comparisons; separately determine maximum successful throughput under the same
error-rate and tail-latency limits. Retain planned, actually issued, completed,
failed, rejected and retried request counts so queued/rejected work cannot vanish.

## Eight continuous long segments

Run all four columns on both databases for **at least 1,800 effective continuous
seconds per cell**, totaling at least **14,400 seconds**. Warmup, calibration,
drain and idle observation are additional time. No overlap on the shared admitted
measurement resources is allowed. Each cell retains its source and binary hashes,
environment and workload identity, offered-load settings, start/end times, raw
time series, operation ledger, error classification and result/state oracle.
The [acceptance record](acceptance.json) lists all eight required cells even while
they remain unexecuted.

For each column and database report:

- Successful operations/s and rows/s; p50/p95/p99 with the exact measurement
  boundary and missing/rejected requests accounted for.
- User and system CPU seconds, CPU time per successful operation, and idle CPU.
- Steady/peak RSS, available PSS, native heap peak, and retained bytes after drain
  and idle observation. Record unavailable metrics and their reasons explicitly.
- Managed cumulative bytes, B/operation, B/row and generation-specific GC counts
  for managed routes. Direct C++ managed metrics are not applicable; report its
  native allocations and frees.
- PostgreSQL client and server resource usage separately. SQLite's engine is
  inside the application process and is not counted as an external service.
- Cursor, connection, lease and native-owner counts after drain: zero where the
  contract requires release, otherwise an explicitly bounded steady-state pool.

## Evidence-led optimization and stopping

Trace each measured hotspot from C# through C ABI, the C++ implementation and the
actual driver source. Prioritize per-row waiting, batch copies and DbWire parsing,
generated projection, repeated plan/binding work, pool contention and callback
wakeup. Inspect old Korda19/Plan23 only as hypotheses and revalidate on the fixed
C++ baseline. Change one demonstrated bottleneck, perform a small before/after
comparison, then return beneficial changes to the mixed workload.

Retain only reproducible improvements with bounded resources and passing
correctness. Revert noise-level changes and unacceptable regressions. Stop when
major remaining hotspots are understood and further improvements would weaken
semantics, shift costs into another layer or repeatedly fail to exceed measured
noise. Record every retained/rejected attempt, absolute before/after values,
deltas, gap from direct C++, raw sources and reproduction command. The stop report
must disclose residual nonzero/unproven paths; it cannot turn an incomplete
campaign into an accepted result.

## Delivery gates

Run the dependency-selected Korda correctness, short allocation regression,
compiled API/XML and independent package AOT checks. Register new benchmark/test
ownership and verify `eng/ci/impact.py` selects the correct consumers. Ordinary
PR CI does not run the eight long segments. Consumer checks use Native AOT, not
JIT; unrelated platforms, clean-image and CPU-emulation campaigns remain excluded.

Obtain scoped non-author technical review with truthful authorship disclosure.
Submit and push actual tested source, open/update PRs, fix failures without
weakening requirements, merge normally after required checks, and observe actual
merged-main results. Follow the existing automatic preview workflow. Download
actual published NuGet archives and verify payload/native identities and real
Native AOT consumption. If package inputs are unchanged, verify and document the
existing fingerprint-based publication skip. Do not alter publication settings,
rules, credentials or approval identities to manufacture acceptance.

The containing evidence commit's own checks are observed separately; no file may
predict its future CI/merge/publication result. Finish with a Chinese report of
allocation coverage, CPU/memory/latency/throughput changes, all eight long cells,
remaining gaps and merge/publication links, then stop.

## Local record verification

```sh
python3 tools/verify_db_perf.py
python3 tools/verify_db_perf.py --verify-frozen-history
python3 tools/verify_db_perf.py --archives /absolute/path/to/baseline-artifacts
```

These commands validate record integrity, negative controls, immutable history
and optional original archive bytes. They do not run or accept the performance
campaign. Actual benchmark build/run commands must be copied from executed,
source-bound receipts once the Korda harness exists.
