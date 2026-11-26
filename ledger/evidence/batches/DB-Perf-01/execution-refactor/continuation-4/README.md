# Direct final-close continuation — measured, with a blocking cancellation failure

**Current status:** public [`bc6ba1a`](https://github.com/IzuSharp/Korda/commit/bc6ba1ae0ece02ecc2c0860776605f3c838f3ff8)
removes the observed final-close retirement tail, but its existing full CI
failed in `Orm.Relations.CallbackCancellation`. The unchanged public source and
assets reproduced that failure locally. This is a blocked intermediate
candidate, not merge or final performance acceptance. Final long-run credit is
still **0/4**. Resume with the cancellation correction before selecting a final
candidate or running the final mixed-load cells.

The earlier [`0f3816c` observations](../continuation-3/measured-checkpoint-0f3816c.md)
and the `f0078da7` original-before rebuild remain unchanged. **The `before`
cohort in this directory's phase comparison is `0f3816c`, not `f0078da7`.**

## Implemented path and exact inputs

Normal cursor close now uses `close_request -> ready(0) -> close_take`.
The native worker retires resources and releases its channel/Source accessors
before readiness; independent notification fences remain until the callback
returns. Public snapshot/join includes those fences for uncertain-acceptance
fallback. Direct close consumes a resource-only frozen snapshot and the managed
callback/control drain. Generic cleanup remains a lazy cold fallback for
rejection or uncertainty. The frozen 42 ABI declarations, three command
extension exports and ten cursor extension exports are separate inventories.

The published tree is `78e6c419a7e1ee2134a5c4aac86e5d5e21483eba`, identical to
reviewed local `3b7fd0259274135cc22eeea73c93e21c5619d46b`. Both native profiles
were rebuilt from the fetched public commit, followed by independent bundles
and four ordinary external PackageReference Release Native AOT consumers.
Producer source identities were not rewritten from an earlier development run.

| Input | SQLite SHA-256 | PostgreSQL SHA-256 |
| --- | --- | --- |
| Public native asset | `19f48a405354c765f0467bcd5e228f22bcfec283137c5cbab5b0d205cda093b8` | `5d9d1fd9729c49e03799a58768ba4dcc1aa105735d337897da1b850cccae2018` |
| Independent provider nupkg | `d6fda8169d23cf9aabe5ac018c3809d0dd5863dde77d23cacfd90ce22014a1e0` | `604c75f2e0fb09d8b66cb1fb219f6ab2ce3a405ce9a6ca7f9b660c1fbcd893f5` |
| Ordinary phase AOT ELF | `1f52ad412c5ddb14299084a24658ca14cd190ce5b3c4bc739b5cd363a914b1ef` | `d7940c5775bb591f06f057f216bc1e99d8e11861136c6b73b4ce5aa302f78a4e` |
| Ordinary mixed-load AOT ELF | `7dd6845d4b90a64da8e08c0684db2be8d52e9e5576fe8c8e0407d57bd2f7ffe7` | `b74f95b8a8248ac88aa1f17e9d3a7295da15b9977f9f794e97edffd9cc6e812b` |

Both existing `validate_public` checks passed on separate provider directories.
The package version is the isolated local verification version `0.1.0-ci.1`;
this is not a public NuGet release claim. The unchanged Dapper consumers use
Dapper 2.1.100, Dapper.AOT 1.1.0, Npgsql 11.0.0 or Microsoft.Data.Sqlite.Core
11.0.0/SQLitePCLRaw 3.0.5 and the pinned SQLite 3.51.3 library.

## Observed results

The ordinary campaign completed 20 commands: two explicitly excluded fixture
commands and 18 observations. Each route has 256 operations in three rotated
windows, returning the same full ordered DTO lists with exact values and NULL
checks. Six Dapper receipt hashes match the actual corresponding candidate
receipts. All commands exited zero with no observer error; tracked owners
drained. The [validated phase report](phases-close-analysis-02.md) and
[raw calculation](phases-close-analysis-02.json) retain every route/window.

Selected prepared-route observations, in microseconds unless stated:

| Provider / rows / quantity | Intermediate 0f | Direct close bc6 |
| --- | ---: | ---: |
| SQLite / 1 / read-through-EOF p95 | 7,750.136 | 102.910 |
| SQLite / 1 / read-through-EOF p99 | 11,899.126 | 188.122 |
| PostgreSQL / 1 / read-through-EOF p95 | 7,825.014 | 112.476 |
| PostgreSQL / 1 / read-through-EOF p99 | 11,535.136 | 190.021 |
| SQLite / 1000 / read-through-EOF p95 | 6,443.609 | 2,548.902 |
| SQLite / 1000 / process CPU per operation | 3,904.392 | 3,938.168 |
| PostgreSQL / 1000 / read-through-EOF p95 | 4,992.699 | 3,301.118 |
| PostgreSQL / 1000 / process CPU per operation | 4,077.911 | 4,907.936 |
| SQLite / 1 / whole-process B per operation | 3,002.760 | 2,575.969 |
| PostgreSQL / 1 / whole-process B per operation | 3,156.719 | 2,569.969 |

These are observations, not a universal causal CPU improvement. In particular,
the 1000-row CPU cost did not improve in this comparison. Dapper's corresponding
1000-row client CPU was 406.177/475.806 us per operation for SQLite/PostgreSQL.
EOF includes cursor cleanup; a short separate Release stage does not mean
cleanup was free. Do not add independently computed percentile values.

Twelve additional commands ran in separate ABI/allocation diagnostic processes.
The [diagnostic reconciliation](close-diagnostics-analysis-01.json) verifies all
18 ABI route aggregates and 54 allocation windows. Prepared 1/100/1000-row
queries use exactly **11/20/104 FFI calls**, 1/4/32 request-and-take pairs, one
read-admission check, one final close request/take and one business SQL execution
per query. All normal query generic operation starts, retirements, old fetch
creation and old close creation are zero. PostgreSQL reports four protocol
submissions per execution; OS poll calls and wait nanoseconds remain separate,
and are not relabeled network RTTs.

Observed generated mapper/List scopes remain 136/7,256/77,816 B per operation
for 1/100/1000 rows in both Korda providers. `FrameworkOnlyBytes` is null.
Raw whole-process allocation includes results, framework, driver and harness;
no subtraction across instrumented/ordinary processes proves framework zero.
The instrumentation has no timing credit.

## Correctness and the blocking failure

The [development archive](close-development-evidence-01.README.md) retains the
original native and managed runs. Native gates passed 341 streaming, 120
transaction and 469 actual C ABI checks plus the C17 ABI gate. The integrated
NativeHost AOT run passed the two-provider normal matrix (1,319 assertions per
provider, final generic count strictly zero), close lifecycle matrix (276 per
provider), existing mapper/parent-transaction/scheduler tests and B04's 546
assertions. Independent subtree comparison binds those tested product bytes to
bc6. Those passes do not replace other modules' tests.

The existing [CI 45742221278](https://github.com/IzuSharp/Korda/actions/runs/45742221278)
then failed in the Linux `database.regressions` action, specifically the unchanged
SQLite `Orm.Relations.CallbackCancellation` test. It starts a long Scalar query
inside a transaction and immediately cancels. It requires the original token's
`OperationCanceledException`, confirmed rollback, no commit attempt, released
resources and no persisted write. Actual execution threw `InvalidOperationException`
from `NativeHost.TakePullBatch` through `HostPullController.Process`.

An independent local exact-bc6 original-test AOT build succeeded, then its
original runner reproduced the same failure with exit 250. The PostgreSQL
part and final rollback/owner assertions were not reached and are not passes.
See `cancel-failure/` for the retained CI log and local result/hash/command files.
No assertion was relaxed and no general InvalidState-to-cancellation mapping
was introduced.

Source review identified a concrete pre-worker window: accepted `CursorPull`
work checks `closing_` before cancellation; `request_close` publishes closing
before invoking cancellation outside the channel lock. A stop can consequently
win before worker start yet be surfaced as Closed/InvalidState. The subordinate
`DB-Exec-04-cancel-native` worktree is preparing a deterministic native fixture
and the smallest correction, with parent Source/Session and existing provider
error priority retained. Do not claim that diagnosis or an unrelated fast-path
experiment is already the verified fix.

## Recovery, tools and next action

[observations-bc6ba1a.tar.gz](observations-bc6ba1a.tar.gz) preserves 603 original
observation/consumer/producer/tool files (15,643,099 uncompressed bytes); every
archived byte was read back and hash-verified. Its archive SHA-256 is
`66bfc8187528b3251b57a11094893b8bb7956d32e9943c115b0626ade4f1f084`.
The [manifest](observations-bc6ba1a.tar.manifest.json) excludes reproducible
database files, package caches and binary outputs while retaining their source
and binary identities. All 72 ordinary consumer inputs were unchanged after
the complete campaign. Client/PG/observer affinities were 0–3/4–7/8; all known
builds/tests stopped during these serial observations. No exclusive physical
host or visible cgroup quota is claimed.

Two preparation mistakes remain recorded: a repeated pack correctly rejected
an occupied immutable staging version; a fresh separate staging directory then
produced byte-identical SQLite nupkg bytes. The first phase index used incorrect
relative directory overrides and therefore reported missing files; corrected
absolute-path index `02` validates all 18 actual observations. Neither event was
silently overwritten. A disabled, own-process software CPU-clock event probe
returned ENOENT, and no perf executable was present; there is no sampled stack
attribution in this checkpoint. No privilege or sysctl was changed.

1. Finish the deterministic cancellation correction and rerun the original
   Native AOT Orm.Relations test with its unchanged assertions and real providers.
2. Independently review/test the isolated ready-drain experiment `bf974378` in
   `DB-Exec-04-ready-fast` and tests `535fb00` in `DB-Exec-04-ready-validation`.
   It attempts to remove the internal ready-to-coordinator queue hop while
   retaining asynchronous business continuations. It is not yet selected or
   measured, and must not be called the cancellation fix.
3. Freeze the corrected candidate, verify actual package consumption, and use
   measured A/B results to select or reject the experiment. Resume the existing
   [local plan generator](generate_local_plan.usage.md) for the fixed 35 cases,
   concurrency/arrival calibration and the four serial final 1800-second cells.
   Supplement matched f007 original-before mixed data separately.
4. Reconcile Design and Plan, then review and follow the existing CI, normal
   merge and independent package publication rules. The actual impact plan still
   selects interop, Linux, PostgreSQL and SQLite scopes; no benchmark action,
   workflow, job, button, schedule or hidden release/test load was added.

Design's implemented-source checkpoint is
[`4b22a75`](https://github.com/IzuSharp/Korda-Design/commit/4b22a75356b63bf203dffba16ed9c458c1b67acd),
whose two existing documentation CI runs passed. Korda's blocking failure above
still prevents completion. Final long-run credit remains **0/4**.
