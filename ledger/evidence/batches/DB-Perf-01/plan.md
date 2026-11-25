# DB-Perf-01 — Linux database and Fluent ORM performance

## Serializer implemented; current ordinary CI passed — 2026-11-25, f0078da7

**Resume this checkpoint before the historical observations below.** Continue
[Korda #37](https://github.com/IzuSharp/Korda/pull/37),
[Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and
[Plan #34](https://github.com/IzuSharp/Plan/pull/34). Product head is
[`f0078da720e07031bc56464995af6791c41aaae8`](https://github.com/IzuSharp/Korda/commit/f0078da720e07031bc56464995af6791c41aaae8),
tree `1e56f5466fa02640dcb68389f283e5c03c2c09ec`; actual CI producer is
`46ef09477b75dd5ce05e1941a739652bc685a9e2`. The
[checkpoint and source-bound receipts](query-optimization/serializer-f0078da7/README.md)
retain the prior allocation regression and both unexplained failures.

The selected single-root serializer is now implemented, with local Binding
**165 assertions / 13 cases**, including **81 command-only assertions**, and
**1321 Fluent assertions across SQLite/PostgreSQL, 14 cases each**. Public API
checks retain 221 Fluent symbols/13 typed cases and 42 frozen Cdecl signatures.
The path requires no dependencies, private uncaptured origins and, when sealing,
no pending origin-publication gates. It uses a 4096-byte bounded stack frame;
larger or shared/captured/CTE/imported commands retain the generic encoder.
This slice changes neither the native protocol nor callback timing. **No new
measurement yet establishes that it removes the earlier 8.4 KB/op regression.**

[CI 45624813071](https://github.com/IzuSharp/Korda/actions/runs/45624813071) now
passes all required ordinary gates. Both providers remain independent package
runners; the shared scope includes Fluent and aggregate API validation. Modules
and publish are skipped by normal PR rules, with zero benchmark jobs. The prior
run `45622268417` failed SQLite B03 AOT with exit -6 and missing uploaded exception
stderr. Eleven fresh local gate invocations did not reproduce it; the binary
identities differ, and the cause remains unknown. The follow-up only retains
precise provider diagnostic files. All 45 existing Tooling tests executed
successfully, with unchanged planner fields, routing and thresholds.

The original PostgreSQL prepared-query failure also remains unexplained. Three
bounded diagnostics did not reproduce it; one separate missing-table run only
validated Provider/42P01 failure reporting. Neither the new CI pass nor these
local successes retroactively accept a failed attempt.

Six exact-package external Native AOT applications are built under
`final-local-v5`; four 35-case mixes pass **280/280** scheduled operations, and six
cancellation/concurrent-conflict checks pass with owners drained. Six before
resource processes are qualified for diagnostic scope only. The previous freeze
`f493d3d…` ended with all **867 files / 16 apps unchanged**. The current freeze
`f83df84a57af07a927f4955b91e8a64561bccafa8f92d2bd7181bc3a83efa269` binds
**926 files / 16 apps**. The new SQLite-then-PostgreSQL same-query phase sequence
has started; its result is pending. The four final local 1800-second Korda/Dapper.AOT
cells still have **zero accepted seconds**, and final comparison/stopping reasons
remain open. Preserve frozen inputs and the earlier unrun plan sets.

Nine workload-option bindings and unique stdout/result equality were checked
with four positive receipts and 48 rejected negative mutations before the new
freeze. Their helper and the numeric extraction tools are now immutable campaign
inputs. [Recovery paths](handoff-linux.md) identify the active artifacts. This
checkpoint reuses the prior 20 Plan/two Design historical gates and adds only
fresh link, JSON, diff and historical-byte checks; no old acceptance is changed.

## First measured SQLite phase checkpoint — 2026-11-25, before serializer follow-up

**Resume from this observation and the selected follow-up before further product edits.**
[Korda #37](https://github.com/IzuSharp/Korda/pull/37) remains at
[`034b40ea0635027aa2132a4feb90343cf80a3081`](https://github.com/IzuSharp/Korda/commit/034b40ea0635027aa2132a4feb90343cf80a3081),
tree `fbb71d978af30999afb21c86d42b5237bbfbcb62`; [Design #20](https://github.com/IzuSharp/Korda-Design/pull/20)
remains `439c9c2005e1633c08afce07c7652b35b31647a3`. Continue [Plan #34](https://github.com/IzuSharp/Plan/pull/34).
The complete required ordinary [CI 45614292641](https://github.com/IzuSharp/Korda/actions/runs/45614292641)
now passes, including shared Linux, both independent provider jobs and Verify.
The [CI receipt](query-optimization/phase-sqlite-r0-034b40ea/ordinary-ci.json)
retains exact source/package identities and zero benchmark jobs. This resolves the
preceding pending CI observation; it grants no performance or long-load acceptance.

The first complete local SQLite comparison is recorded in
[provisional r0 evidence](query-optimization/phase-sqlite-r0-034b40ea/README.md).
The pre-measurement freeze SHA is
`f493d3d315f7e1c9411d05cf41d94c0d15bdb0fc1c8270324348280df7e2f7b4`.
The original baseline is preview.3 (`771bc77`), recovered package input is
`7f67b43`, and the current candidate producer is `b3f475a` for head `034b40ea`.
Only the first complete repetition is summarized here; later repetitions and
PostgreSQL are not yet included in this analysis. Existing frozen inputs and
all original result receipts remain unchanged.

| Whole-process managed allocation, B/op | Original baseline | Recovered input | Current candidate |
| --- | ---: | ---: | ---: |
| Ordinary Fluent | 72,662.45 | 21,460.75 | 29,879.16 |
| Warm Prepare | 53,803.01 | 14,430.32 | 14,435.28 |
| Complete parameterized Host SQL | 61,909.63 | 17,899.57 | 17,981.26 |

Each cell uses three 256-operation windows after 64 warmups. All routes materialize
and verify the same 100-row DTO list with Int64 tenant values alternating 1/2;
within each product run they share one session and C++ Host. Product runs reuse
the same seeded database/connection argument. Fluent and prepared SQL match;
SQLite raw-template compilation spells its sole ordinal parameter `?1` instead
of `?`, which is retained as an explicit comparison limitation. The
[numeric receipts](query-optimization/phase-sqlite-r0-034b40ea/sqlite-r0.json)
preserve cumulative allocation endpoints before division, GC, CPU/RSS/native
counters and separate construction, submit-to-first-row, read-complete and release
phase durations. Preparation/first executions are separate observations after
shared setup; they are not independent process-cold measurements.

**High priority: the dynamic path regresses against the recovered input by
8,418.41 B/op (+39.23%) in this first repetition.** Prepare and Host SQL allocations
remain close to their recovered values. The selected next slice is a strict
exclusive single-root serializer that avoids generic temporary traversal and
indexing collections when there are no dependencies and every origin is private
and uncaptured. Keep the native frame, required dense scalar origin IDs, typed
root model sidecar, limits and cleanup unchanged. CreateCte, shared/captured
origins, snapshots and imports retain the generic path. The existing ordinary
`LockOrigins(false)` already returns its shared empty gate; do not claim its cold
HashSets as ordinary-lane savings. This is a planned implementation detail under
the current complete-command contract, **not an implemented or measured success**.
See the [evidence, impact and guard conditions](query-optimization/phase-sqlite-r0-034b40ea/followup-priorities.json).

Read-complete accounts for 90.5–94.1% of window wall across the nine r0 cells;
process CPU is about 1.77–1.98 ms/op against 12.22–14.44 ms/op wall. The source
contains a default 10 ms callback retry timer, but there are no instrumented retry
counts or callback timelines here. Its contribution is **unproven**, and no
spin/timer change is selected. Prior runtime-spin diagnostics and the withdrawn
callback-dispatch change remain preserved historical evidence.

Complete all repetitions/two-provider analysis, then validate and measure any new
serializer candidate against the preserved inputs. Retain the remaining physical
statement/parameter-copy/mapping gaps until actual evidence resolves them.
The four final Korda/Dapper.AOT local 1800-second mixed cells have zero accepted
seconds. Final comparative metrics, remaining-gap assessment and stopping basis
are still pending; no merge/release or final performance acceptance is claimed.

## Aggregate reference follow-up — 2026-11-25, 034b40ea

**Resume from this later checkpoint.** The earlier candidate sections below are
preserved as historical observations. Continue [Korda #37](https://github.com/IzuSharp/Korda/pull/37),
[Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and
[Plan #34](https://github.com/IzuSharp/Plan/pull/34). Current Korda is
[`034b40ea0635027aa2132a4feb90343cf80a3081`](https://github.com/IzuSharp/Korda/commit/034b40ea0635027aa2132a4feb90343cf80a3081),
tree `fbb71d978af30999afb21c86d42b5237bbfbcb62`; Design remains
[`439c9c2005e1633c08afce07c7652b35b31647a3`](https://github.com/IzuSharp/Korda-Design/commit/439c9c2005e1633c08afce07c7652b35b31647a3).
The [new evidence checkpoint](query-optimization/candidate-034b40ea/README.md)
records a documentation-only correction. The complete-query implementation,
public Fluent API, additive capability 26 and prior native/managed correctness
boundaries remain as described in the preceding implementation checkpoint.

[CI 45610610153](https://github.com/IzuSharp/Korda/actions/runs/45610610153)
passed the existing full formatter, API checks and all 20 native CTests, then
failed `Interop.Execution` because the committed source was no longer clean.
The uploaded diagnostics do not include the nested `source-status.stdout`, so its
actual dirty-file list is unavailable. Local execution of the three existing
aggregate API generators reproduced **only three tracked `reference/database.md`
changes** from the new Fluent XML: Data.NativeHost, Data.Migrations and Orm.Relations.
These retained stale immediate-per-node descriptions while the compiled XML
already described complete-command submission. The
[failure record](query-optimization/candidate-034b40ea/ci-source-failure.json),
[selected job lines](query-optimization/candidate-034b40ea/ci-source-excerpts.log)
and [reproduction/fix](query-optimization/candidate-034b40ea/aggregate-reference-fix.json)
keep observed CI facts separate from the local causal reproduction.

The published correction changes those three generated documents only:
**87 additions and 87 deletions**, no signatures or implementation changes.
All three original API scripts ran twice with the pinned Design contract and
current compiled XML; all six invocations passed. The second round left all
**14 tracked references** and the full diff byte-identical. NativeHost verifies
523/32/15/3 exact signatures across its four assemblies; Migrations verifies
523 assembly signatures including 94 required members; Relations verifies
523 Database and 163 Data signatures, including all 81 required members.
The clean-source check remains unchanged and must pass in normal CI.

The [actual new plan](query-optimization/candidate-034b40ea/ci-plan.json) still uses
`interop`, shared `linux`, `postgresql` and `sqlite` scopes. Existing ownership of
the three references adds **`api.tool`, `migrations.api`, `relations.api`** to the
six previous Linux actions; `fluent.api` remains selected. PostgreSQL and SQLite
continue independent package/Native AOT checks. Compatibility remains skipped
because its verifier bytes match current main. Benchmark ownership records select
**zero benchmark execution modules or jobs**. These are ordinary registered checks,
not a new CI route. See the [selection delta](query-optimization/candidate-034b40ea/ci-selection.json).

The prior `4ed20b09` packages now have six externally built Linux Native AOT
consumers: mixed, phase and resource for each provider. Their short mixed
correctness completed **280/280** scheduled operations across dynamic/prepared
modes and both databases, with zero failures/oracle mismatches and all owners
returned to zero. Both providers passed pre-cancellation, active cancellation
and overlapping optimistic-conflict checks. The
[extracted evidence](query-optimization/candidate-034b40ea/v2-local-correctness.json)
preserves their actual package/producer/binary identities. Phase/resource apps
have not been formally measured; short correctness overlapped preparation and
does not count as performance evidence.

New normal [CI 45614292641](https://github.com/IzuSharp/Korda/actions/runs/45614292641)
uses merge producer `b3f475aa05fa6c8a0c156be548e838286f10ae3d`, tree `fbb71d978`.
Its required outcome and fresh v3 exact-producer applications are pending at this
checkpoint. All 30 consumer/build input files match v2, but the older binaries
are not relabeled as final source-bound results. Continue with fresh package
correctness, local same-SQL phase/resource comparisons, and the four uninterrupted
1800-second local final-Korda/Dapper.AOT cells. All four cells retain zero accepted
seconds. Physical statement reuse and the other measured-gap/stop decisions remain
pending. No final performance, package, merge or release acceptance is claimed.

## Published implementation candidate — 2026-11-25, 4ed20b09

**Resume from this checkpoint.** The lower continuation and diagnostics sections
retain their earlier observations and pending-state wording. They do not override
this later state. The current work remains in [Korda #37](https://github.com/IzuSharp/Korda/pull/37),
[Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and
[Plan #34](https://github.com/IzuSharp/Plan/pull/34), preserving C++ execution and
the public C# Fluent API.

The current published candidate is Korda
[`4ed20b09a245a787a3efccc9dcf2ab3c9f85d4d9`](https://github.com/IzuSharp/Korda/commit/4ed20b09a245a787a3efccc9dcf2ab3c9f85d4d9),
tree `1c95420b34a2291e4b63fdc08caf32409a3eb4ee`. It follows the implementation attempt
[`dd990f2379c95bde25531de69f7b6f3be5aec3b0`](https://github.com/IzuSharp/Korda/commit/dd990f2379c95bde25531de69f7b6f3be5aec3b0),
tree `2643545ab41562bebe6c8d1f1811da9d3ced5257`. The aligned Design candidate is
[`439c9c2005e1633c08afce07c7652b35b31647a3`](https://github.com/IzuSharp/Korda-Design/commit/439c9c2005e1633c08afce07c7652b35b31647a3).
The [checkpoint](query-optimization/candidate-4ed20b09/checkpoint.json) distinguishes
published identities, local component observations and pending exact-package work.
No final performance, merge or release acceptance is claimed.

### Required CI failure and observed routing

[CI run 45608927004](https://github.com/IzuSharp/Korda/actions/runs/45608927004)
does **not** pass. Shared Linux reached the existing
`dotnet format artifacts/db-scope/database.slnx --verify-no-changes --no-restore`
gate after native and managed compilation, then the formatter returned 2.
The complete formatter log contains exactly **180 WHITESPACE diagnostics**:
173 in `QueryCommand.Clauses.cs` and 7 in `QueryCommand.cs`. Managed compilation
has zero warnings and errors. The PostgreSQL/SQLite package jobs, interop and
security jobs succeeded; their success does not replace the failed shared gate.
Modules/publication skipped, and aggregate Verify failed. The
[failure receipt](query-optimization/candidate-4ed20b09/ci-format-failure.json)
retains the actual producer merge, job/artifact identities, complete-log hashes
and independently recounted diagnostics. That failed attempt and its consumer
artifacts remain diagnostic inputs; the existing gate was not weakened or bypassed.

The follow-up `4ed20b09` changes only those two files through the same SDK 11.0.100
whitespace formatter. Repository-folder formatting and its idempotence check both
returned zero; an independent comparison confirms identical non-whitespace
character streams. The exact generated-solution formatter invocation was blocked
locally by Roslyn BuildHost's Unix socket permission error, so it is not recorded
as a local pass. The [correction receipt](query-optimization/candidate-4ed20b09/formatting-followup.json)
retains that limitation. Normal [CI 45610610153](https://github.com/IzuSharp/Korda/actions/runs/45610610153)
has started with merge producer `8626e714534119909ff978c34d2af515bf10694c` and the
same `1c95420b` tree. Plan passed and modules skipped; the ordinary independent
jobs were in progress at this observation. The full required gate and final CI
result remain pending. New exact-producer consumer preparation is also pending.

The retained [actual plan](query-optimization/candidate-4ed20b09/ci-plan.json) was
generated from the local equivalent tree against main
`e063f2eb6e2e857e3f19f96bf263cae372651a27`. Its
[selection explanation](query-optimization/candidate-4ed20b09/ci-selection.json)
has four ordinary build scopes:

| Scope | Selected checks and reason |
| --- | --- |
| `interop` | `interop.async` remains selected by the inherited async retirement/handle changes. |
| `linux` | Native, managed build, database API, dependency and regression checks cover the shared query/Host changes. `fluent.api` is also selected because the compiled API checker and generated reference changed. |
| `postgresql` | Build, dependencies, packed API, provider tests, pack, exact-package Native AOT consumption and metadata validation run on the existing independent provider runner. |
| `sqlite` | Its own build/dependency/API/test/pack/AOT/metadata actions run independently and in parallel with PostgreSQL. |

`database.compatibility` is absent for an explained committed-diff reason. The
main rename merge restored `tests/Verification.Compatibility/verify.py` to the
same Git blob as main, `62da12f55c237fbfc6b7958de5d012ba58c3455b`; the recovered
starting head had blob `2f1f6171f13d56ce7e3fb41e32afceb6c50faa3e`.
No compatibility-owned path remains changed and no checker was manually disabled.
The separate API/reference edits select `fluent.api`. Both benchmark modules
retain path ownership only: the plan has zero execution modules, module packages
or custom run steps, and no benchmark jobs. Ordinary Native AOT consumers execute
directly on the existing Linux runners. PR validation does not release; main still
decides publication separately for each package's changed inputs.

### Implemented candidate versus the initial gaps

| Priority | Candidate state and evidence | Remaining work |
| --- | --- | --- |
| P0 CI isolation | Five task benchmark workflows and both module execution registrations were removed at `42f852c`; the current plan still selects only ordinary independent checks. The two-file formatter correction is published at `4ed20b09`. | Observe the actual full gate and required CI result at that head. Performance stays local Linux. |
| P1 complete query | C# records a bounded NWQC command; C++ replays the existing operation inventory, including all 22 clause opcodes and topological subquery blocks. Typed model/plan/CTE sidecars are registry/source checked; bytes never contain native pointers. | Finish final exact-package and real-provider validation at the successful corrected head. There is no product fallback to per-node composition. |
| P1 earlier fixed work | `.Prepare()` now finishes native SQL/argument compilation before returning. Immutable execution-parameter expectation, schema/hash and descriptor data are cached in the compiled plan. | Every execution still validates values and performs copies/encoding. The final measurement must show which remaining work matters. This is runtime preparation, not arbitrary build-time SQL generation. |
| P1 origin and lifetime | Bounded origin bindings preserve shared scalar identity across clone/CTE compilation. Captures use owner leases, without a global literal pool or native owner cycle. | Retain capture/body-snapshot memory cost in measurements; do not call this SQL-placeholder deduplication. |
| P1 contention | `ShapeCache` now locks its own lookup/LRU/counts/clear bookkeeping. Compilation/key calculation and per-call parameter parse/copy/encode are outside that mutex. Concurrent render/clear/evict tests pass. | Measure contention and queueing; local correctness is not a throughput or p99 result. Admission, retirement and per-row gates remain. |
| P1 physical statements | Provider statement reuse remains unimplemented. SQLite still prepares/finalizes and PostgreSQL uses unnamed prepare/describe per command. | Any later cache must preserve schema/Describe error timing, transaction/session state, cancellation and drain/discard; never replay writes or unknown transactions to repair a cache. |
| P1 phase attribution | Same-Host ordinary Fluent, warm Prepare and parameterized SQL probes exist; four v2 before/recovered applications and two before resource applications are built. | They are not measured at this checkpoint. Bind final candidate applications and measure construction, first row, remaining read and release under matched conditions. |
| P2 mapping and generation | Existing allocation work and generated table/projection readers remain; no new fixed-query template generator is claimed. | Measure remaining batch/DTO allocation, GC, CPU and memory before another optimization; preserve optional generator work as a separate future item. |

Review fixed several concrete semantic hazards before publication: aborted JOIN
aliases no longer let invalidated deep expressions poison a later valid snapshot;
window creation charges its native-equivalent expanded node; failed mutators do
not intern validation shapes before quota admission; an Enter/Dispose race calls
the common exit path so the last command lease is released. Snapshot import avoids
a second complete clone. Shared subquery snapshots participate in first-capture
coordination even when an individual record's reference count is one. The final
tests cover disposal of original builders/owners followed by reuse of surviving
snapshots and CTEs.

The cross-CTE budget failure was reproduced, not inferred from timing. Under a
9000-byte limit, a constructed but unused escaped LIKE literal retains 6002 bytes
on the direct path. Independent replay without its origin binding retains 12004
bytes and fails with status 13. The corrected seeded path succeeds with 6002
bytes; both providers report owned bytes 7028 and expanded nodes 18. Independent
equal values remain distinct, and an over-budget rejected import leaves the
previous query usable. See the [failure](query-optimization/candidate-4ed20b09/origin-reproduction.log)
and [actual differential counts](query-optimization/candidate-4ed20b09/native-correctness.json).
This is ownership/value-budget preservation, not placeholder-count reduction.

### Local correctness and exact evidence limits

| Check | Actual observation |
| --- | --- |
| Native query | 926 checks and 52 SQL/ordered-argument goldens, combined across SQLite/PostgreSQL; release and ASan/UBSan pass. |
| Native Host review | Existing `all` mode passes. Shared-cache tests use four render workers, three prepared shapes and a two-entry cache with concurrent clear/eviction. |
| Native ABI/assets | 24 frozen C ABI rejection cases match with all six native owner counters zero. Both local ELF profiles have exactly 48 exports and maximum GLIBC 2.38. The 42 frozen declarations/fingerprint remain unchanged; three additive extension exports use capability bit 26. |
| Binding Native AOT | 137 assertions in 13 cases, including 53 command-only assertions with direct composition exports unavailable; native owners/operations/buffers finish at zero. |
| Real-provider Fluent Native AOT | 1321 combined assertions across both providers and 502 managed retirements, including dynamic filters, joins, CTEs, changing prepared values, streams and mutation/row-lock cases. |
| Compiled public API/XML | Binding exposes zero public types and preserves 42 Cdecl calls; Fluent retains 221 exact symbols and 13 valid/negative typed-consumer checks. |

The [evidence index](query-optimization/candidate-4ed20b09/evidence-index.json),
[native results](query-optimization/candidate-4ed20b09/native-correctness.json),
[binding result](query-optimization/candidate-4ed20b09/binding-result.json) and
[Fluent correctness extraction](query-optimization/candidate-4ed20b09/fluent-correctness.json)
bind the reported values to original result hashes and retained logs. Native files
match both published trees. Managed runtime tests ran before final XML/comment/
generated-guide-only edits; final product libraries and API/XML checks were rebuilt
after those edits. The retained AOT executable is not relabeled as an exact build
of the entire comment-final or later formatting tree. These are component observations, not
final exact-package acceptance or a performance comparison.

LeakSanitizer remains unverified. An earlier run completed 866 assertions and then
LSan failed under the environment's ptrace restriction. The final ASan/UBSan pass
used `detect_leaks=0`; no system restriction was changed. The
[failure excerpt](query-optimization/candidate-4ed20b09/lsan-limitation-excerpts.log)
is retained, and zero owner counters are not substituted for a leak-detector pass.

Only checked synthetic outcomes, ABI/export metadata, selected result/log content,
hashes and the requested CI plan are attached. The [publication note](query-optimization/candidate-4ed20b09/README.md)
distinguishes exact copies from extractions. Broad source, restore, environment,
command-line and binary archives are not copied into Plan.

### Pending local measurement and acceptance

[Prepared-application identities](query-optimization/candidate-4ed20b09/prepared-applications.json)
record the six before/recovered phase/resource builds without claiming execution.
Three SQLite mixed/phase/resource consumers were subsequently built from the
failed `dd990f23` attempt's CI artifacts, then preparation stopped for the formatter correction;
those remain diagnostic inputs. No local PostgreSQL mixed/phase/resource consumer
build or performance measurement is credited to that attempt. Current `4ed20b09` exact-producer
applications are pending. The earlier 560/560 mixed smoke belongs
to its before/Dapper source identities and is not reassigned to the NWQC candidate.

All four required local 1800-second cells remain **pending, 0 accepted effective
seconds**: PostgreSQL candidate/Dapper.AOT and SQLite candidate/Dapper.AOT. First
bind the corrected successful head and its independently verified packages, finish
real-provider correctness, stop competing builds, and run the matched local short
phase/resource comparisons. Then run the four uninterrupted segments sequentially
on the same environment, reporting allocation, process-wide GC, CPU, memory,
successful throughput, p99, failures and all actual source/package/binary identities.
Final gaps and the stopping decision require these results. No historical
acceptance, long-test credit or verifier is changed by this checkpoint.

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
