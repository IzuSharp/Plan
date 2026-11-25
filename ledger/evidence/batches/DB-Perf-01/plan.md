# DB-Perf-01 — Linux database and Fluent ORM performance

## Current continuation: query optimization, 2026-11-25

This continuation supersedes the execution location and long-test scope of the
historical plan below. The owner explicitly requires **local Linux x64 performance
tests**, preserving C++ execution and the existing C# Fluent API. There is no
authorization to migrate this task to .NET database drivers. Korda [PR #37](https://github.com/IzuSharp/Korda/pull/37)
is the implementation PR. Plan #32 is merged; this Plan branch and a companion
Korda-Design branch continue from the latest main. Existing results retain their
original source, package and environment identities.

### CI prerequisite: observed before changing product code

The three required main files were read: Korda `AGENTS.md`,
`eng/ci/modules/README.md`, and `.github/workflows/ci.yml`. Inspection followed
`impact.py`, `catalog.py`, `database_plan.py`, `plan_run.py`, `worker.py`,
`runner.py`, and the existing reusable build/module workflows.

In the task worktree, `git fetch origin main` and
`python3 eng/ci/impact.py origin/main --output artifacts/plan.json` succeeded for
product head `c1aca12cadfe3f4e2431ded24c13f7afb58453a0` against main
`e063f2eb6e2e857e3f19f96bf263cae372651a27`. The retained
[actual plan](query-optimization/ci-before.json) selected:

| Selection | Observed cause and purpose |
| --- | --- |
| `interop` / `interop.async` | Changes to `AsyncOperation.cs` and its retirement/handle tests. |
| `linux` / database native, build, API, compatibility, dependencies, regressions | Shared Fluent, binding, codecs, NativeHost, streaming and transaction source/test changes. |
| `postgresql` | Affected standalone provider package: build, dependency/API checks, provider tests, pack, exact-package Native AOT consumption and metadata validation. |
| `sqlite` | The second affected standalone provider package, on its own independent runner with its own build/pack/AOT validation. |
| Two benchmark module jobs | The prior PR registered `database-perf-probes` and `db-perf-benchmarks` with `run` commands. These extra CI jobs are now explicitly rejected by the owner and will be removed. Paths remain owned for planner validation. |

No release, clean-image, CPU emulation or long benchmark was selected by this
plan. Python reads committed Git trees and dependency edges; YAML provisions
only the declared tools, restores the existing caches and carries internal or
verified package artifacts. PR validation does not publish. On main, each
registered public package is separately compared with its last published input
fingerprint before the existing build/consume/publish path runs.

The branch predated main's repository rename, explaining the old
`NativeWeave-Design` checkout references visible in a direct two-tree diff.
Merge latest main to preserve the existing `Korda-Design` references; do not
reintroduce renamed URLs.

The [reported failed job](https://github.com/IzuSharp/Korda/actions/runs/45568390591/job/139048722985)
exited before checkout because observed hosted image `20261116.133.1` did not
equal the hardcoded `20261116.376.1`. It produced zero effective measurement
seconds. The existing [PostgreSQL package job](https://github.com/IzuSharp/Korda/actions/runs/45594188737/job/139135963900)
already succeeded. Do not add another benchmark CI layer: remove all five
task-specific benchmark workflows and both benchmark `run` registrations. Keep
the existing provider jobs and verify routing with the existing Tooling suite,
including that benchmark-only changes select no package or benchmark job.

### Current gaps, evidence and ordered implementation

These are source observations at the recovered head, not new measured claims.
Earlier allocation improvements in #37 are inherited and must not be repeated.

| Priority | Current evidence | Impact and selected next step |
| --- | --- | --- |
| P0 | Extra benchmark registrations and five task-specific workflows in #37; failed image guard above | Remove the unnecessary CI work. Run performance locally; record actual environment instead of requiring a hosted image build number. |
| P1 | `src/Query.Fluent/QueryContext.cs` immediately calls `QueryBinding.Column/Value/Binary/Clause`; `src/Query.Binding/QueryBinding.cs` crosses FFI per operation | Define and implement a bounded, versioned complete-query command composed in C#. C++ retains semantic validation, SQL dialect generation and execution. Submission count is distinct from batched result reads. |
| P1 | `NativeQuery::seal` snapshots query data; `NativePlan::compiled` uses `call_once` only when rendering | Explicitly compile fixed query shape at `.Prepare()` where valid, retain immutable SQL/parameter order/result layout, and distinguish initial preparation from warmed execution. Generated metadata/binders/mappers are not arbitrary compile-time Fluent translation. |
| P1 | `provider.cpp` prepares and finalizes SQLite statements per execution; PostgreSQL uses unnamed prepare/describe per execution | Investigate bounded physical-connection statement reuse with schema/session invalidation, cancellation and ownership preserved. Measure it separately from logical `.Prepare()` reuse. |
| P1 | `NativePlan::render` parses input, copies cells, re-encodes a batch before Host decoding; `host_abi.cpp` holds a shape mutex during render | Measure and reduce repeated parameter encoding and avoidable serialization without weakening validation or retirement. |
| P1 | Existing mixed harness times full operations; the raw SQL case is a separate semantic case | Add a local same-SQL comparison for ordinary Fluent, warmed `.Prepare()` and parameterized SQL through the same C++ Host, recording construction, submit-to-first-row, remaining read and release. |
| P2 | #37 already reduces batch copies, private iteration state, projection scratch and empty parameter frames | Reuse existing evidence, then verify remaining batch/DTO costs at first use, steady state and concurrent use. Keep business object allocation separate from uncertain attribution. |
| P2 | Current-candidate acceptance is incomplete | Run both real databases, preserve raw observations, compare final candidate with Dapper.AOT, and record remaining gaps and a measured stopping reason. |

Review SqlSugar's condition composition and complete SQL submission, EF Core's
parameterized query-shape reuse and Dapper.AOT's generated parameter/row factories.
Bind research conclusions to their actual source versions in the design. Publish
this gap/priority record and the selected design before optimizing product code.

### Local measurement and acceptance

Use one local Linux environment per comparison group. Keep SQL, ordered typed
parameters, complete results, dataset/indexes, connections/pool limits,
transactions, warmup and workload identical. Build outside measured windows;
record actual SDK, compiler, runtime, database/library, OS, CPU/affinity and
available quota observations. Report unavailable metrics or shared-host noise
explicitly; do not fabricate a dedicated host or require a GitHub image identity.

Short comparisons cover original fixed before, recovered #37 and final candidate
as applicable; the same-Host SQL route isolates query composition from execution.
Report cold preparation, warmed steady execution and concurrency separately.
Use real external PackageReference Native AOT consumers for both public packages
and Dapper.AOT. Validate dynamic filters, changing prepared parameters,
transactions, cancellation and streaming/early disposal before load measurement.

Final long measurements are four local cells: PostgreSQL candidate and
Dapper.AOT, SQLite candidate and Dapper.AOT, each for 1,800 continuous effective
seconds. They are not ordinary PR checks. On shared resources measure routes
sequentially. Retain operation counts, failures/rejections, raw allocation/GC,
CPU, steady/peak memory, throughput and p99, and source/package/executable hashes.
Earlier eight-cell campaign records remain historical; they are not silently
rebound to this candidate or relabeled as the new four-cell acceptance.

Final review must align Design, product code and observations, link all three
PRs, disclose remaining gaps and explain the stopping decision. Until then this
continuation is in progress, with no new performance acceptance claimed.

## CI correction and local diagnostics checkpoint

The three active PRs are [Korda #37](https://github.com/IzuSharp/Korda/pull/37),
[Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and
[Plan #34](https://github.com/IzuSharp/Plan/pull/34). The initial paragraphs above
record the starting state; the CI correction is now complete. Implementation
commit `42f852cd1999a198d7f844f5261144649ef5b12b` removed all five benchmark
workflows and both benchmark execution registrations, and merged current main.
The ordinary [CI run](https://github.com/IzuSharp/Korda/actions/runs/45598220233)
passed. Existing Tooling routing tests verify benchmark-only changes select no
jobs/packages, provider-only changes stay isolated, and shared query changes
select both public packages and their Native AOT consumers. The original suite
passed 44 tests with one missing-CMake skip; that exact remaining case then passed
with locked CMake 4.3.3 ([log](query-optimization/environment/cmake-routing-test.log)).
All 45 test cases have now executed successfully; no benchmark CI was introduced.

Local tools and exact before/recovered package identities are recorded under
[environment](query-optimization/environment/toolchain-observation.json), including
[package hashes](query-optimization/environment/package-inputs.json).
The observed environment is Debian 13, .NET SDK 11.0.100, Clang 23.1.5,
PostgreSQL 18.0 and SQLite 3.51.3. Native executables match the repository's locked
hashes. The installed LLVM subset contains the required compiler/tools/headers
and runtimes; its compressed inventory is retained. The local PostgreSQL server
uses TCP and is started, exercised and stopped within one observer process.
No hosted image build number is required or invented.

The same-Host phase diagnostic is committed locally as
`b410cbd2415b3a704683f245563415e81901c45c`. The existing public consumer builder
publishes it outside Korda with only PackageReference, and records source,
package, executable and loaded-native identities, retaining generated code. Its
[committed benchmark-only plan](query-optimization/phase-only-plan.json) selects
no build scopes, modules, packages or public checks. Baseline and recovered #37
packages both passed all three routes on both databases, validating the complete
100-row result and draining all six native ownership counts. See the
[smoke summary](query-optimization/phase-smoke-summary.json) and linked raw records.
These are correctness observations during ongoing builds, not performance claims.
SQLite's existing Fluent `?` versus raw-template `?1` marker difference is disclosed;
the ordinal, typed value and relational query are identical. PostgreSQL uses `$1`
in both. A failed first diagnostic marker assumption is also preserved.

The published Design decision precedes the new product implementation. Complete
query-command transport and eager prepared-shape compilation are in development;
new product coverage and final-candidate performance remain unclaimed. Next:
finish/review that implementation, run existing module and real-provider/AOT
checks, then local interleaved short comparisons and four final 1,800-second
candidate/Dapper.AOT segments. Record physical statement-cache and parameter/
locking gaps that remain; do not relabel source observations as measured gains.

### Local mixed-consumer correctness checkpoint

The original package and Dapper.AOT are now built as four external Linux Native
AOT consumers, using the existing mixed harness. [The checked summary](query-optimization/mixed-smoke/summary.json)
records eight provider/mode cells: **560/560 successful scheduled operations**,
zero failures and zero result-oracle failures. All 35 cases execute twice in each
cell with the frozen complete row/digest expectations. Dynamic filters, varying
parameters, transaction commit/rollback, optimistic updates, full streams and
early stop are covered. These short runs overlapped builds and earn no timing or
long-test acceptance.

The four lifecycle diagnostics passed 11 checks. Dapper with Microsoft.Data.Sqlite
reports active cancellation as unsupported because its synchronous engine call
was not interrupted; that limitation remains in the raw result. Its pre-cancel
and conflict checks pass. Korda passes pre-cancel, active-cancel and conflict checks
on both databases; Dapper passes all three on PostgreSQL. Native owners/application
connections drain and the task-owned PostgreSQL 18 server exits successfully.

[The publication note](query-optimization/mixed-smoke/README.md) and
[correctness ledger](query-optimization/mixed-smoke/correctness-ledger.json) retain
the synthetic case outcomes and hashes. The ledger is an explicit extraction of
the unchanged raw results, excluding local paths, command lines, generated source,
restore graphs and host-environment logs. Automatic approval review rejected
attaching the broader archive; it is not included in this PR. Current-tool baseline
package validation also passed for both original packages without bypassing their
integrity checks or downgrading validators. The phase smoke's compiled inputs are
publicly retained at Korda
[`5e0bf89`](https://github.com/IzuSharp/Korda/commit/5e0bf8929a8873e7620eb814e44b27ee84dfab08).

## Historical plan preserved below

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
