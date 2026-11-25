# DB-Perf-01 — Linux handoff

## Active checkpoint — f0078da7, phase/short/resource complete, SQLite long started

Read [pre-long evidence](query-optimization/prelong-f0078da7/README.md), then
continue [Korda #37](https://github.com/IzuSharp/Korda/pull/37),
[Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and
[Plan #34](https://github.com/IzuSharp/Plan/pull/34). Branches and frozen product
identity below remain unchanged. Phase **18/18**, short **36/36** and resource
**12/12** have completed their distinct scopes; four long cells remain pending.

At **2026-11-25 14:09 UTC**, root started the existing SQLite long coordinator
(session `61233`): candidate 1800 seconds, then Dapper.AOT 1800 seconds.
PostgreSQL long had not started. Check that coordinator and
`/tmp/DB-Perf-01-measurements-v4/results` before any resumption; do not start
parallel consumers, builds or heavyweight gates. The pre-launch numeric archive
is an immutable snapshot with six long/setup entries still `not_observed`.
Final post-run rehash and a new final extraction are still required.

The [selected metrics and provenance](query-optimization/prelong-f0078da7/metrics-summary.json)
retain the ordinary allocation regression, Dapper gap, RSS/GC/CPU regressions,
resource qualification and both unresolved old aborts. Do not label current
passes as cause fixes, infer timer causality, or add a buffer pool/physical cache
to the frozen candidate. Design is unchanged while the long results are pending.
No final performance acceptance or long-duration credit is assigned here.

## Active checkpoint — f0078da7, new freeze and phase diagnostic in progress

Resume [the current plan](plan.md) and
[serializer checkpoint](query-optimization/serializer-f0078da7/README.md), then
check [Korda #37](https://github.com/IzuSharp/Korda/pull/37),
[Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and
[Plan #34](https://github.com/IzuSharp/Plan/pull/34). Product branch remains
`task/DB-Perf-01-linux`; companion branches remain
`task/DB-Perf-01-query-optimization`. Published source is
`f0078da720e07031bc56464995af6791c41aaae8`, tree
`1e56f5466fa02640dcb68389f283e5c03c2c09ec`, actual CI producer
`46ef09477b75dd5ce05e1941a739652bc685a9e2`. Full ordinary
[CI 45624813071](https://github.com/IzuSharp/Korda/actions/runs/45624813071) passed;
its receipt is `/tmp/DB-Perf-01-final-local-v5/ci-gate.json`.

The private-root stack serializer is implemented with local correctness and exact
API checks. Its effect on the allocation regression is not established. Preserve
both unexplained incidents: original PG `r1-recovered` prepared failure and CI
`45622268417` SQLite B03 AOT -6. Three PG diagnostics and eleven local SQLite gate
invocations did not reproduce those incidents. The separate forced PG 42P01 run
only validates failure reporting. All attempts retain their own source/ELF identity.

Current paths and custody:

- `/tmp/DB-Perf-01-measurements-v4/identity.json`: SHA
  `f83df84a57af07a927f4955b91e8a64561bccafa8f92d2bd7181bc3a83efa269`, 16 apps/926 files.
  Phase diagnostics have started, SQLite nine processes then PostgreSQL nine.
  Inspect the existing coordinator/results before starting another process;
  do not create a parallel measurement or build load.
- `/tmp/DB-Perf-01-final-local-v5`: six exact-package external Native AOT apps;
  `summary.json`/`readiness.json` bind 280 correct operations and six lifecycle
  checks, drained owners, and unchanged preparation inputs. Baseline/recovered
  phase apps are under `/tmp/DB-Perf-01-phase-v3`.
- `/workspace/scratch/787156d4dd76/DB-Perf-01-resource-results-v4`: six before
  diagnostic processes qualified, zero long credit; candidate comparison remains
  to be completed against the new input set.
- `/tmp/DB-Perf-01-measurement-tools-v4.py`: SHA
  `feabf37ceea2d834419b8588d661032bd79d1297c29178fc5c0d623c4b8b34a7`;
  `measurements-v4/summary-guard-validation.json` binds four positive/48 negative
  checks. `/tmp/DB-Perf-01-evidence-tools/extract.py` and `make_manifest.py` are
  also frozen; create a new version and explicit record if a real defect is found.
- `/tmp/DB-Perf-01-measurements/identity-post-phase-verification.json` binds the
  old freeze's unchanged 867 files; old results are immutable. Preserve
  `measurements-v4/plans-3e2bda3-not-run` without assigning execution credit.
- `/tmp/DB-Perf-01-phase-diagnostic-recovered-pg/review.json` and
  `/tmp/DB-Perf-01-sqlite-ci-repro/{run-1,repeats}.json` retain unresolved-failure
  and local non-reproduction evidence. `/tmp/DB-Perf-01-ci-diagnostics/receipt.json`
  binds the upload-only fix and unchanged routing checks.

Next: finish phase/resource/short analyses, retaining all failures; execute and
assess the four final local 30-minute candidate/Dapper.AOT cells; report remaining
allocation/CPU/memory/throughput/p99 gaps and the stopping basis. All four long
cells currently have zero accepted credit. Physical statement reuse and optional
fixed-query generation remain unimplemented. No merge/release or final performance
acceptance is claimed. Preserve every prior section below byte-for-byte.

## Active checkpoint — ordinary CI passed; first SQLite allocation regression recorded

Read the newest [plan section](plan.md) and
[first-phase evidence](query-optimization/phase-sqlite-r0-034b40ea/README.md).
Product is still `034b40ea0635027aa2132a4feb90343cf80a3081`, tree `fbb71d978af30999afb21c86d42b5237bbfbcb62`;
Design is `439c9c2005e1633c08afce07c7652b35b31647a3`. All required ordinary
[CI 45614292641](https://github.com/IzuSharp/Korda/actions/runs/45614292641)
checks now pass, with independent providers and no benchmark jobs. Keep the earlier
failed attempts and pending-state snapshots below unchanged.

The frozen local input identity is
`f493d3d315f7e1c9411d05cf41d94c0d15bdb0fc1c8270324348280df7e2f7b4` at
`/tmp/DB-Perf-01-measurements/identity.json`. Three complete r0 receipts live under
`/tmp/DB-Perf-01-measurements/results/phase-sqlite`; do not modify them or the
frozen apps. Later SQLite/PG receipts are not aggregated by this checkpoint.
Dynamic Fluent allocates 29,879.16 B/op versus recovered 21,460.75:
**+8,418.41 B/op (+39.23%)**. Warm Prepare is 14,435.28 versus 14,430.32;
Host SQL is 17,981.26 versus 17,899.57. Preserve the original baseline column and
all cumulative counters in [the numeric extraction](query-optimization/phase-sqlite-r0-034b40ea/sqlite-r0.json).

Next selected product slice: strict no-dependency single-root encoding, only with
private uncaptured origins; retain all generic CTE/shared/snapshot/import behavior
and native framing/sidecar/origin/limit contracts. Plan and Design must record this
before the product edit. It has not been implemented or measured at this checkpoint.
The separate read-complete/wall observation does not prove the 10 ms callback
retry timer causes the delay; no spin/timer change is selected.

Finish full short comparisons, bind any follow-up to fresh source/packages, and
run the required local final Korda/Dapper.AOT long cells. All four 30-minute cells
remain without accepted credit; no final performance or stopping conclusion yet.

## Active checkpoint — aggregate API references corrected, new CI pending

Resume the [newest plan section](plan.md) and
[034b40ea checkpoint](query-optimization/candidate-034b40ea/README.md).
Korda [#37](https://github.com/IzuSharp/Korda/pull/37) current source is
[`034b40ea0635027aa2132a4feb90343cf80a3081`](https://github.com/IzuSharp/Korda/commit/034b40ea0635027aa2132a4feb90343cf80a3081),
tree `fbb71d978af30999afb21c86d42b5237bbfbcb62`; Design
[#20](https://github.com/IzuSharp/Korda-Design/pull/20) remains `439c9c2005e1633c08afce07c7652b35b31647a3`.
Plan [#34](https://github.com/IzuSharp/Plan/pull/34) and Design use
`task/DB-Perf-01-query-optimization`; Korda uses `task/DB-Perf-01-linux`.
The earlier handoff below is unchanged and records earlier observations.

The first CI failed formatting. The second, run `45610610153`, passed formatting,
API checks and 20/20 native CTests, then correctly rejected dirty source at
`Interop.Execution`. The uploaded artifact omits the dirty-file stdout; exact
local regeneration separately reproduced three stale aggregate API documents.
The published fix changes those documents only, 87/87 lines. Two runs of each
original generator passed, preserving all 14 reference bytes and full diff on
the second round. Keep both failure records and the
[causal evidence boundary](query-optimization/candidate-034b40ea/aggregate-reference-fix.json);
do not weaken the clean-source gate.

Current [CI 45614292641](https://github.com/IzuSharp/Korda/actions/runs/45614292641)
producer is `b3f475aa05fa6c8a0c156be548e838286f10ae3d`, tree `fbb71d978`.
Its outcome remains pending here. The actual planner keeps four ordinary scopes,
independent provider runners and no benchmark jobs; reference ownership adds
`api.tool`, `migrations.api`, `relations.api` to the shared Linux actions.

Under `/tmp/DB-Perf-01-final-local-v2`, six consumers built against the prior
`4ed20b09` producer and short correctness passed 280/280 scheduled operations,
plus both-provider cancellation/optimistic-conflict checks with owners drained.
These are diagnostic correctness inputs, not formal performance. Preserve their
[exact identities](query-optimization/candidate-034b40ea/v2-local-correctness.json).
Under `/tmp/DB-Perf-01-final-local-v3`, the new source audit confirms all 30
consumer/build inputs are unchanged; fresh current-producer applications are
still pending at this checkpoint. Do not relabel v2 binaries as v3 results.

Next: observe all required ordinary CI checks, complete fresh package correctness,
then run local same-Host phase/resource comparisons and the four local 30-minute
Korda/Dapper.AOT cells. No formal performance has started or been accepted; all
four cells remain pending. Prior implementation tests, physical statement reuse
and other remaining gaps stay as recorded in the earlier checkpoint.

## Active checkpoint — published formatting follow-up, CI in progress

Resume [Korda #37](https://github.com/IzuSharp/Korda/pull/37),
[Design #20](https://github.com/IzuSharp/Korda-Design/pull/20) and
[Plan #34](https://github.com/IzuSharp/Plan/pull/34). Product branch is
`task/DB-Perf-01-linux`; Design and Plan use
`task/DB-Perf-01-query-optimization`. The current Plan worktree is
`/tmp/DB-Perf-01-worktrees/DB-Perf-01-Plan`, also reached through the original
`/workspace/scratch/787156d4dd76/DB-Perf-01-Plan` symlink. Read the newest
[implementation checkpoint](plan.md)
before the earlier starting-state and recovery records below. Preserve their bytes.

Current published candidate:
[`4ed20b09a245a787a3efccc9dcf2ab3c9f85d4d9`](https://github.com/IzuSharp/Korda/commit/4ed20b09a245a787a3efccc9dcf2ab3c9f85d4d9),
tree `1c95420b34a2291e4b63fdc08caf32409a3eb4ee`. Preserve the prior attempt:
[`dd990f2379c95bde25531de69f7b6f3be5aec3b0`](https://github.com/IzuSharp/Korda/commit/dd990f2379c95bde25531de69f7b6f3be5aec3b0),
tree `2643545ab41562bebe6c8d1f1811da9d3ced5257`. Aligned Design:
[`439c9c2005e1633c08afce07c7652b35b31647a3`](https://github.com/IzuSharp/Korda-Design/commit/439c9c2005e1633c08afce07c7652b35b31647a3).
Final acceptance is pending required CI and actual source-bound measurement.

[CI 45608927004](https://github.com/IzuSharp/Korda/actions/runs/45608927004)
failed the shared Linux `dotnet format` gate: two files, 180 WHITESPACE diagnostics
(173 `QueryCommand.Clauses.cs`, 7 `QueryCommand.cs`), formatter exit 2. Native and
managed compilation succeeded with zero managed warnings/errors; independent
provider jobs succeeded, but the aggregate result is a failure. Retain the
[actual receipt](query-optimization/candidate-4ed20b09/ci-format-failure.json).
Do not mark that attempt accepted or bypass the gate. The two-file correction is
published in `4ed20b09`. The same SDK's repository-folder formatter and idempotence
check pass, with identical non-whitespace character streams. The exact generated
solution invocation was locally blocked by the Roslyn BuildHost Unix socket
restriction; its required CI gate remains in force. See the
[correction receipt](query-optimization/candidate-4ed20b09/formatting-followup.json).
Normal [CI 45610610153](https://github.com/IzuSharp/Korda/actions/runs/45610610153)
uses merge producer `8626e714534119909ff978c34d2af515bf10694c`, tree `1c95420b`.
Plan passed/modules skipped; independent jobs were in progress when observed.
Current exact-producer applications under the task's `final-local-v2` work area
remain pending. Do not substitute the old SQLite diagnostic binaries.

The [actual committed-diff plan](query-optimization/candidate-4ed20b09/ci-plan.json)
selects interop, shared Linux and separate PostgreSQL/SQLite checks. `fluent.api`
is selected by API-checker/reference edits. `database.compatibility` is absent
because main's rename merge restored its verifier to byte equality with main;
the [blob comparison](query-optimization/candidate-4ed20b09/ci-selection.json)
explains the change from the initial plan. Benchmark paths remain owned, with
zero execution modules/jobs. Keep Native AOT consumers directly on ordinary
Linux runners; all performance work stays local Linux.

Implemented candidate: one NWQC command with bit 26/three additive exports,
22 clause operations/topological imports, typed owner sidecars, eager `.Prepare()`
SQL/parameter-metadata compilation, bounded origin sharing across clone/CTE
owners, and ShapeCache locking limited to LRU bookkeeping. Physical statement
reuse and arbitrary build-time Fluent SQL generation remain unimplemented.
Origin sharing preserves literal budgets and ownership; it does not deduplicate
SQL placeholders. The direct/unseeded/seeded 9000-byte case is 6002/12004/6002
retained literal bytes, with status 0/13/0 on both providers.

Local component checkpoint: native query 926 checks/52 goldens in release and
ASan/UBSan; Host review all; Binding AOT 137 assertions/13 cases including 53
command-only assertions; two-provider Fluent AOT 1321 combined assertions;
API/XML 221 symbols/13 typed consumers. Native C ABI 24 rejection cases and six
zero owner counts pass. The [index and limitations](query-optimization/candidate-4ed20b09/README.md)
retain exact hashes and distinguish runtime-tested behavior from later comment/XML
edits. LSan remains blocked by the environment's ptrace restriction; it did not
pass. These results are not final packaged-consumer or performance acceptance.

Next work, in order:

1. Observe the full existing formatter and required CI result at published
   `4ed20b09`; its fetch/impact/check-index selection already passed. Keep the
   prior failed attempt and its artifact identities separate.
2. Bind the final PostgreSQL and SQLite packages and execute their actual external
   Native AOT consumers. Three SQLite consumers built from the failed attempt's
   CI artifacts remain diagnostic; local PostgreSQL final workload builds have
   not started. These are distinct from the provider CI package consumers.
3. Reuse the six prebuilt before/recovered phase/resource applications at their
   recorded identities. They have not been measured. Build final equivalents
   outside measurement windows, then stop competing builds for local comparison.
4. Finish same-SQL ordinary Fluent / warm Prepare / same-Host SQL phase attribution
   and resource checks, then the four local candidate/Dapper.AOT 1800-second cells.
   All four cells currently have zero accepted effective seconds.
5. Record complete metrics, remaining physical-statement/parameter/mapping gaps,
   design consistency and the measured stopping reason. Preserve the historical
   eight-cell record and acceptance/tool bytes unchanged.

## Current continuation — query optimization, 2026-11-25

The owner resumed this task and explicitly clarified that performance tests run
**locally on Linux, never in CI**. Ordinary CI keeps the existing Python impact
planner and independent PostgreSQL/SQLite package jobs. Remove the five
task-specific benchmark workflows and the two benchmark module `run`
registrations added by #37. Do not replace them with another manual benchmark
workflow. Read the current section of [plan.md](plan.md) before the historical
snapshots below.

Observed starting points are Korda #37 head
`c1aca12cadfe3f4e2431ded24c13f7afb58453a0`, Korda main
`e063f2eb6e2e857e3f19f96bf263cae372651a27`, Design main
`dcf4cee8ed4d02a606733aec11bbb36a411d05a9` and Plan main
`c73943c72b77cca0398e4034cb82663db0d20bd0`. Plan #32 and the two rename PRs
are merged. No subsequent query-optimization Plan or Design PR existed when
searched; new companion PRs will be linked here.

Task worktrees are `/workspace/scratch/787156d4dd76/DB-Perf-01-Korda`,
`DB-Perf-01-Design` and `DB-Perf-01-Plan`. Other local DB-DotNet-01 worktrees
belong to a different task and are not implementation inputs. The present
direction retains C++ and public C# Fluent APIs.

The requested `fetch` and impact plan succeeded; [ci-before.json](query-optimization/ci-before.json)
is the actual committed-diff plan. The image-guard failure is explained in the
plan and earns zero measured seconds. Current .Prepare() does not yet eagerly
compile SQL or reuse a physical connection's statement; current dynamic Fluent
still issues per-node FFI calls. The new plan separates these gaps from #37's
existing allocation work. Product optimization waits for the design/plan
checkpoint, and no new load test or performance acceptance is claimed here.

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

## Historical continuation records preserved below

## Live continuation — 2026-11-25 05:45 UTC (13:45 Asia/Shanghai)

This is an **in-progress evidence checkpoint**, not final batch acceptance. The
owner explicitly replied **“允许，现在继续 该合并的合并”** to the eleven-file
raw-log disclosure request and authorized continuation and ordinary eligible
merges. The earlier rejection below is historical and is retained unchanged.
No approval identity, required check, performance threshold or ownership contract
has been bypassed.

### Recovery and its exact limits

The replacement executor is usable. The old `/home/agent/DB-Perf-01-*` and
`/workspace/scratch/b94e2a0e0c3f/` trees are absent. Do not interpret old local
paths in the preserved sections below as files available on the current machine.
Current repositories/worktrees are under
`/workspace/scratch/37c4f8cc3a91/{repositories,worktrees}/`; use
`worktrees/Korda-DB-Perf-01-linux` and `worktrees/Plan-DB-Perf-01-linux`.
Both task worktrees use `task/DB-Perf-01-linux`.

The [recovery manifest](recovery/20261125/recovery-manifest.json) and
[recovery README](recovery/20261125/README.md) distinguish:

- 32 original blobs recovered exactly from two previously successful Git trees,
  totaling 448,617 bytes. The two trees were independent, not cumulative.
- Three of the eleven authorized files recovered with their previously recorded
  SHA-256 values; two retrieved again from the same original job, with new hashes
  and no claim that their serialization equals the lost old local bytes.
- Six original files still missing. No substitutes were invented. The additional
  `prepareLog.json` outside the eleven-name scope was not added.

The 37 restored evidence payloads total 588,834 bytes. This is not the full lost
Plan snapshot, not all historical raw evidence, and not additional measurement
credit. Source-reference validation currently sees 93 references, of which 82
remain pending. Original reported results whose raw local files have not been
recovered remain historical summaries with their original limitations.

The exact historical campaign runtime and final checkpoint ZIPs were downloaded
again from their original GitHub artifacts. A new read-only
`verify_current.py --require-eight-long` verification passed with 241 observations,
74 retained ordinary SLO failures and all eight original 1,800-second intervals.
Its new result SHA is
`2b22701a0cfbaa6e9377ef83cf6c2e3da6e7d072eff3b5a6648d45189c327406`;
it does not replace the lost original verifier file/hash recorded below.
Recovery root: `recovery-20261125/original-campaign/` in the current workspace.
Historical after remains `3d5ba3f`, image `20261116.376.1`; final-candidate
acceptance remains separate.

### Current final candidate and the new isolated matrix

The reviewed production/harness snapshot remains
`db0f674f3849fa86f69d86eea2c830dc1c84da83`, tree
`f2193bf688ce5460810d47be577cdddeadfde763`. Actual candidate package producer
`3df4f4f3ac455cb8bae8901c80a4fefb33021970` has the same tree and successful
[normal CI 45511550343](https://github.com/IzuSharp/Korda/actions/runs/45511550343).
The provider package/native hashes below are unchanged and were reverified from
actual downloads in this continuation. The candidate artifacts are not a public
NuGet release.

Two preparation attempts of
[45553940210](https://github.com/IzuSharp/Korda/actions/runs/45553940210) stopped
at the exact image guard: both actually received `ubuntu24/20261116.133.1`,
while the earlier guard required `20261116.376.1`. Neither performed a build or
measurement. One failed-job retry was attempted; both failures remain recorded
and earn zero effective seconds.

After independent exact-diff review, activation commit
`456140129c3ef3ff1ea0412b2b8cb3da82d099fd`, tree
`dcc806523bf7c48fdd95b6bea8b8ec645a7b1b39`, freezes both jobs on actual
`ubuntu24/20261116.133.1` for a **new full matrix**. The only changes from its
parent `bce370e` are the two exact workflow image constants and an explanatory
request note. Harness, packages, workload, database/compiler versions, CPU
partitions, admission/noise/quota rules, SLOs, operation accounting and eight
continuous 1,800-second durations are unchanged. No real ImageVersion variable
is overwritten; preparation/measurement image equality and full VM identity
binding remain required. Do not resume or combine the old-image matrix.

- [Final campaign 45555341689](https://github.com/IzuSharp/Korda/actions/runs/45555341689)
  has started. Preparation job `139005934425` passed the actual image guard and
  frozen-request checks; compilation/preparation is in progress at this checkpoint.
- Request SHA-256:
  `62a32d2bcf460d33dab1834805658e2ee576a0c4f41bf52eedbfb251f18c6749`.
- Independent two-file review SHA-256:
  `feca89c858bfbba9c1b923f6f3655a953e024038527483db74e590746424c42d`.
- [Normal head CI 45555351833](https://github.com/IzuSharp/Korda/actions/runs/45555351833)
  is tracked separately. Parent activation CI 45553951455 succeeded.

**Historical verified matrix: 8/8. Current final candidate: 0/8 accepted at this
checkpoint.** The acceptance record intentionally remains `in_progress`, with
unfulfilled checks and public publication pending. A passing document gate does
not promote those statuses.

### Allocation ownership and remaining work

The target is zero avoidable **library-internal extra allocation** on measured
steady paths. Business List storage, DTOs, strings and typed JSON are business
results, including objects constructed by source-generated mapping. Their cost
is expected to remain positive. End-to-end totals retain business, library,
runtime and harness bytes; uncertain attribution remains uncertain. Process-wide
GC counts cannot be split into framework collections and business collections.
The separate 7,480 B result-graph clone is not an exact allocation trace inside a
real query and cannot be subtracted to prove exact framework bytes.

The current local Debian 13/glibc 2.41 executor has a hash-verified .NET 11.0.100,
Clang 23.1.5 and PostgreSQL 18.0 toolchain at `tooling/env.sh`. It is not the
qualified performance VM. Fresh external PackageReference Native AOT List100
diagnostics are being prepared with separately labeled source/package/ELF/native
and fixture identities, because previous local ELF/raw files were lost. These
local runs can establish their actual correctness/allocation observations, not
formal CPU/latency/throughput or long-test credit.

Continue by observing the final campaign and preserving each raw checkpoint,
finishing exact remaining-hotspot/stopping analysis, reviewing recovered/current
evidence, and performing normal eligible merges. Korda merge awaits the matching
final matrix; automatic preview, actual NuGet download and public Native AOT
consumption follow the merge. Plan may merge this explicitly incomplete recovery
checkpoint after its own review and CI; doing so does not accept the batch.

## Previous continuation snapshot — preserved below

## Live continuation — 2026-11-25 00:01 UTC (08:01 Asia/Shanghai)

Resume from the observed results in this section. The local execution environment
became unavailable during the next isolated baseline build. Do not assume that a
pending publish or local handoff write completed. The GitHub connector remains
available, so this recovery checkpoint is being saved directly to the existing
Plan branch; it contains conclusions and recovery references, not rejected raw logs.

### Current product and actual package verification

[Korda #37](https://github.com/IzuSharp/Korda/pull/37) remains draft at
`db0f674f3849fa86f69d86eea2c830dc1c84da83`, tree
`f2193bf688ce5460810d47be577cdddeadfde763`.
[Normal CI 45511550343](https://github.com/IzuSharp/Korda/actions/runs/45511550343)
completed successfully. The merge preserves both bounded projection scratch
(`359b215`) and the separately delivered source-only continuation probe
(`0410da7`). Actual package producer
`3df4f4f3ac455cb8bae8901c80a4fefb33021970` has the same tree and was independently
verified as a Git object; it is not relabeled as the branch commit. Both independent
provider packages were downloaded, fully inventoried and consumed outside the
source tree through ordinary PackageReference Native AOT. Public API/ABI are unchanged.

| Provider | Actual nupkg SHA-256 | Actually loaded native SHA-256 |
| --- | --- | --- |
| PostgreSQL | `f4e8ddbbd154d513ba4f78f11ec99ff9973f49f87465899ba4183418134cb0b3` | `73f725104fb1bee5fc86a9bc371e556ea8358ac3a2d774c4823185e6da8984c6` |
| SQLite | `2724680534384262e5a289e741da506a9ad40d4e37bc21c47ed14f77683feefc` | `970a8868290cec37c353bbd8e48bb7bf4ef18cfa1da9e495fc06d7eb08d71d40` |

Independent direct-source scratch review passed, receipt SHA
`0341a288e968528f79d42958370074dff2f1a9de4dcad95a9169561d93046554`.
The normal B09 gate passed 25 commands (84 direct and 625 encoder assertions);
normal Fluent passed 1,265 assertions on both real providers with Native AOT;
the affected benchmark gate also passed. Failure receipts from earlier unsuccessful
invocations remain preserved. Wide projection fallback and public owned encoding
remain intact; borrowed stack storage is confined to a synchronous native call.

### Allocation ownership and the new actual public comparison

List/backing-array/DTO/string/typed-JSON objects are business-result allocation,
including generated mapping. GC counts describe the shared process heap and are
never split into framework GC and business GC. Whole-query totals include business,
library, runtime and harness. Unknown attribution remains unknown. The separate
7,480 B same-graph clone is not an exact allocation trace inside the real query and
must not be subtracted as a precise framework total.

The previously completed six-process internal encode-and-consume comparison and
nine regression windows establish literal all-thread 0 B only for the measured
fitting scratch-encoding paths. This operation constructs no business result.
The 32-expression 4,266-byte frame retains 4,296 B/call and 128-field fallbacks
retain 13,824/16,896 B. This does not establish zero allocation for a public query.

Twelve interleaved scalar processes compare the unchanged actual prior `6f827`
and new `3df4` consumers. Source/package/ELF/native identities, complete results,
all-thread cumulative allocation arithmetic and final owner cleanup were checked.

| Scalar public query | Before B/query | After B/query | Delta B/query |
| --- | ---: | ---: | ---: |
| PostgreSQL dynamic | 12182.145833 | 11051.395833 | -1130.750000 |
| SQLite dynamic | 12157.833333 | 11056.666667 | -1101.166666 |
| PostgreSQL prepared | 5191.125000 | 5176.187500 | -14.937500 |
| SQLite prepared | 5188.125000 | 5184.375000 | -3.750000 |

Prepared execution does not re-encode projections; its small changes remain
unattributed. Two final scalar cells overlapped an unrelated List100 AOT compilation
for about 8.1 seconds; the overlap is recorded. No CPU/latency/throughput acceptance
is taken from these shared-host allocation diagnostics. Strict comparison SHA:
`85ca9b24a186a10131c4a53aa5d06938d0a20b76f4338ffba57f1697c807cf3a`.

Twelve additional List100 processes ran sequentially and interleaved before/after.
Every result has 100 DTOs, list capacity 128, 80 strings, 20 nulls, 668 UTF-16
characters and digest `12366612025187139697`. Each provider/lane measures
1,152 queries and 115,200 rows.

| Same business result | Before total B/query | After total B/query | Process GC 0/1/2 before → after |
| --- | ---: | ---: | --- |
| PostgreSQL | 22738.375000 | 21218.958333 | 6/0/0 → 6/0/0 |
| SQLite | 22730.291667 | 21227.423611 | 6/0/0 → 6/0/0 |

The independent graph control remains 7,480 B on its measuring thread. Additional
whole-process bytes vary and remain in the records. Exact business allocation
inside the real query and exact framework-only bytes remain unproved/null.
Comparison SHA:
`b31aa95528379617a7e8b7b9b3e068116cc591de113e3491bb159a716377e314`.

Recovery artifacts under /home/agent/DB-Perf-01-artifacts/:
`candidate-db0f674/`,
`projection-scratch-public-allocation-db0-v1/`,
`projection-scratch-public-allocation-interleaved-v1/`,
`projection-scratch-business-results-db0-v1/`.
All completed consumer/DB processes had exited and validation finished at
23:57:41 UTC before the next baseline was started.

### Original full four-column / two-provider matrix: 8/8 verified

[Original campaign 45461269267](https://github.com/IzuSharp/Korda/actions/runs/45461269267)
attempt 2 completed successfully at 23:52:07 UTC. Archive, unchanged-member delta
and full independent `verify_current.py --require-eight-long` all passed.
The verifier recomputes 241 observations, retaining 74 ordinary preflight SLO
failures. There are **8 actual continuous 1,800-second segments, 14,400 effective
seconds**, on the same admitted VM/boot with no overlap. Warmup, calibration,
drain and idle are additional. All 35 mixed business cases ran; each long segment's
planned/attempted/sent/started/completed/success counts match, with zero errors,
rejections, retries and oracle failures.

This complete historical matrix compares fixed before
`771bc77cbd68d3f932b99ed2497c0697bbba5f02` with original after
`3d5ba3f9884308caa691718f73a74aa42be19d94`. It cannot be relabeled as
`2e9`, `6f827`, `3df4` or a later package. A complete matching final
candidate matrix remains outstanding.

| Original long metric | Direct C++ | Fixed before Korda | Original after Korda | Independent C# ORM |
| --- | ---: | ---: | ---: | ---: |
| SQLite success ops/s | 193.814379 | 193.813334 | 193.813870 | 193.814287 |
| SQLite p50/p95/p99 ms | 0.101888/0.630784/1.376256 | 0.708608/21.102592/44.826624 | 0.696320/21.495808/46.923776 | 0.159744/0.991232/1.400832 |
| SQLite CPU user/system s | 754.713448/6.862146 | 1102.856381/96.555582 | 1097.552831/96.379242 | 798.969268/10.759949 |
| SQLite client CPU ms/success | 2.183003 | 3.438031 | 3.422323 | 2.321032 |
| SQLite managed B/success | N/A | 68402.335636 | 47223.985324 | 7368.832824 |
| SQLite process GC 0/1/2 | N/A | 1439/127/14 | 987/87/10 | 154/14/2 |
| PostgreSQL success ops/s | 180.627184 | 180.627050 | 180.627047 | 180.627071 |
| PostgreSQL p50/p95/p99 ms | 0.268288/0.966656/1.720320 | 1.064960/17.432576/32.112640 | 1.056768/17.039360/31.326208 | 0.387072/1.720320/2.375680 |
| PostgreSQL CPU user/system s | 442.305458/10.032169 | 797.205778/172.250985 | 785.409011/171.127154 | 531.018909/28.219851 |
| PostgreSQL client CPU ms/success | 1.391256 | 2.981760 | 2.942020 | 1.720052 |
| PostgreSQL managed B/success | N/A | 69440.626951 | 47322.259042 | 6858.972088 |
| PostgreSQL process GC 0/1/2 | N/A | 1362/120/14 | 922/81/9 | 133/23/2 |

Each SQLite segment has 348,866 successes / 8,512,405 rows; each PostgreSQL
segment has 325,129 successes / 7,933,200 rows. These fixed offered rates are not
maximum-throughput claims. Old-after allocation changes are -30.961443% SQLite
and -31.852201% PostgreSQL; CPU/success changes are -0.456881% and -1.332767%.
The SQLite p99 regression +4.678363% remains recorded; PostgreSQL p99 is -2.448980%.
Do not infer CPU or tail-latency gains merely from reduced allocations.

All Korda six exported owner categories and direct C++ connection/statement/result
categories drain to zero. The independent ORM proves application connection closure
only, not all internal ownership. PostgreSQL server CPU/RSS/PSS is measured
separately; all four service cgroups are empty after shutdown. SQLite engine costs
remain inside the application process. Guest isolation is observed; physical-host
exclusivity and physical network RTT are not established. SQL executions and
protocol submissions remain separately recorded.

The full matrix retains steady/peak/drained/idle RSS and PSS, idle CPU, actual
package/ELF/native identities, result checks and all raw references. Native
allocation has 16 separate short instrumented companions, not 148 profiles and
not primary-long heap totals. The 148-second number is a configured time budget.
Public glibc allocation instrumentation is not a complete address-space or
PostgreSQL-server native-heap measurement. Original primary GC fields are actual
generation differences; full start/end GC endpoints were not serialized.

Final original checkpoint: artifact `14976622248`, 20,543,568 B, SHA
`fe96228a5d9c40d873c405dd52c8609491af745c0af0d401350ccf23a09cd142`.
Full independent result SHA:
`6f840ea5b4c1d728749fd4e933a278907f131fa2714fec56e4019721e642f132`.
Matrix SHA:
`4f80495aa8e7c312de227931e0422e92ef6aa92c523d487914605dff84adbce3`.
Recovery/audit/reproduction entry:
`/workspace/scratch/37c4f8cc3a91/campaign-attempt5-long-checkpoint8/`.
The original ZIP remains under
`/home/agent/DB-Perf-01-artifacts/campaign-45461269267/checkpoint-8.zip`.

### Exact interruption and continuation

The next dynamic-empty-parameter experiment has **not modified production**.
Prepared execution already caches its empty frame. Baseline v1 retained its
240-second restore timeout and eight MSBuild named-pipe permission failures.
Baseline v2 added an explicit single MSBuild node with no parallel restore/build
server. Its offline restore actually passed at 23:58:03.755417–23:58:05.574694 UTC,
log SHA `b618c14dd7dbdc5f92c53303dba05d7559f9188ac6510998914553178b59dfb4`.
AOT publish session `25856` was still pending when the environment reported
transport disconnection and became unavailable. No completed ELF or six-process
baseline is claimed.

Recovery: inspect `publish-1.json`, `publish-1.log`, published ELF and any raw
results under `/home/agent/DB-Perf-01-artifacts/empty-parameters-baseline-v2/`
before running anything. Do not blindly restart its exclusive-create total script.
Runner SHA `32f6c11a34184387692765f7e8c7f2362ec76c6dd14d2cc2523b8b7b509d1b4a`.
The Source-scoped private immutable-frame proposal remains conditional on the actual
before baseline, preserving validation precedence, lazy execution and ownership.

The separate Find same-SQL diagnostic has 13 source-only files under
`/home/agent/DB-Perf-01-worktrees/Korda-find-sql-layer-DB-Perf-01-linux/benchmarks/db-perf/find-sql-layer/`.
No AOT or query execution occurred. Its existing initializer Dataset.cs identity
differs from the frozen current source and is deliberately rejected; inspect the
actual diff or select a matching existing initializer before executing.

The completed 36-cell runtime-spin diagnostic remains runtime sensitivity only.
No production default was changed. Directly disabling retired continuation dispatch
was withdrawn because actual callback exception handling and subsequent admission
changed; the four source-only consumer files are preserved. Remaining ownership/
native-cache/render/parameter-buffer hotspots are under source review; no claim is
made that every further optimization has been excluded. The interrupted reviewer
has not yet written its remaining-hotspots files.

A new final campaign must freeze the actual final reviewed harness and actual
normal-CI package producer, then use a separate request-only activation commit.
The older full benchmark-tree gate must not be weakened. Preserve all existing
successful measurements that match their binary/workload/environment. Do not merge
or claim final acceptance/public preview before the remaining actual gates.

### Existing raw-publication approval block

Automatic approval rejected raw Plan upload batch 0003 because it includes runner,
environment and failure-log metadata and the reviewer required more specific
disclosure authorization. No later same-class raw upload, alternate transport,
encoding or content-review verdict overrides this rejection. Original bytes and
the refusal receipt remain local. This checkpoint contains no rejected raw payload.

The blocked eleven files are under
`ledger/evidence/batches/DB-Perf-01/checkpoints/campaign-image-recovery-v1/raw/campaign-attempt3/`:

- ci-registration-index.log
- ci-registration-publication.json
- ci-registration-tooling-v2.log
- ci-registration-tooling.log
- image-pin-publication.json
- image-pin-validation.json
- measureAttempt1Log.decoded-original.log
- measureAttempt1Log.json
- measureAttempt2Log.decoded-original.log
- measureAttempt2Log.json
- prepareLog.decoded-original.log

Exact scope/hash receipt:
`/workspace/scratch/37c4f8cc3a91/remaining-binary-review-v1/supplement/blocked-0003-scope.json`,
SHA `aecf0e5f56eb3dc4defbd422db88afa7b25447701c5304fdcfdc07f09c73210c`.
Finish unaffected work and resolve this exact disclosure block before raw delivery.

The full local Plan remains at `56289444cb1cb94d1d4ac16a83622102ed802fb3` as last
observed. A local prefix-v11 write was interrupted and is unconfirmed. After recovery,
integrate this prefix into the full history without resetting it to the thin public
branch. Preserve schema-5 evidence, prior failures and both histories.

---

## Live continuation — 2026-11-24 23:17 UTC (2026-11-25 07:17 Asia/Shanghai)

Resume from actual receipts below, not from an earlier pending-state paragraph.
[Korda #37](https://github.com/IzuSharp/Korda/pull/37) is draft at
`33d6cc8fd422f6213eae8cca820ffefd5df5fda1`, tree
`ddf670dab41d582ff78eb30f3381ee26a6cfef13`.
[CI 45502134936](https://github.com/IzuSharp/Korda/actions/runs/45502134936)
passed. This adds the reviewed owned-buffer projection encoder and corrects the
interleaved allocation runner's failure/cleanup receipt ordering. The original
measurement loop is unchanged. The next stack-buffer experiment remains isolated;
it has not been published as a provider package or accepted in mixed load.
Both PRs remain draft; no merge, public preview or public-NuGet acceptance is claimed.

### Allocation accounting remains explicit

Business `List`, backing arrays, DTOs, strings and typed JSON objects remain
business-result allocation even when a generated mapper creates them. The objective
is zero steady-state extra allocation introduced by library machinery where the
actual scoped counters and attribution support it. Whole-query totals include all
business, library, runtime and harness allocation; unknown components remain
unknown. The independent 7,480 B same-graph clone is not an exact allocation trace
inside the real query and must not be subtracted as a precise framework total.
GC generations describe the shared process heap, never separate business/framework
GC. No whole-framework or business-result zero-allocation claim is made.

### Six original long segments fully verified; the final candidate is different

The original [campaign 45461269267](https://github.com/IzuSharp/Korda/actions/runs/45461269267),
attempt 2, job `138688263792`, remains active on boot
`a1dda7dd-2e7f-4168-b019-1ade81b9da65` and original after producer `3d5ba3f`.
**Six actual continuous 1,800-second segments are independently verified: 10,800
effective seconds, 6/8.** All four SQLite columns and PostgreSQL/direct_cpp and
PostgreSQL/korda_before are complete. The PostgreSQL independent ORM segment is
running; preserve the VM and original binaries. The fixed before remains
`771bc77cbd68d3f932b99ed2497c0697bbba5f02`. These original after observations cannot
be relabeled as `2e9`, `6f827` or a later candidate. A complete matching final
candidate matrix remains outstanding.

The latest original checkpoint artifact is `14972238045`, 18,832,403 B, SHA-256
`8331aab1f1423e66409a44b3aeb52886b0caf5ff60d755648623ceb716d93a0c`.
It retains 2,310 unchanged earlier members, replaces campaign state and adds the
11 new PostgreSQL/before members. The archive and incremental semantic audits
passed. Full independent raw verification recomputed 239 observations, six long
segments and retained 74 ordinary SLO failures; its matrix-complete flag is false.
Result SHA `e6d61c8a3a9e50f180c25f550e91110bbad3ab58256b51218ed4a7c4268c0972`.
The initial premature local audit start (file not yet downloaded) and a later
full-verifier SIGKILL (-9) remain separate failure receipts. The serial unchanged
read-only full verification retry passed at 22:59:15 UTC; the kill cause is unproved.
No measurement was rerun to replace either failure.

| New PostgreSQL original segment | Direct C++ | Fixed before Korda |
| --- | ---: | ---: |
| Actual planned-arrival interval (UTC) | 21:51:12.208439–22:21:12.209396 | 22:21:25.8648479–22:51:25.8648968 |
| Planned / sent / successful operations | 325129 / 325129 / 325129 | 325129 / 325129 / 325129 |
| Rows | 7933200 | 7933200 |
| Success ops/s | 180.627184 | 180.627050 |
| p50 / p95 / p99 ms | 0.268288 / 0.966656 / 1.720320 | 1.064960 / 17.432576 / 32.112640 |
| Client CPU user / system seconds | 442.305458 / 10.032169 | 797.205778 / 172.250985 |
| Client CPU ms / success | 1.391256 | 2.981760 |
| Steady / sampled-peak RSS bytes | 11767808 / 11767808 | 54956032 / 58163200 |
| Managed B / success | N/A | 69440.626951 |
| Process GC 0 / 1 / 2 | N/A | 1362 / 120 / 14 |

Both have zero failures, rejections and retries, exact 1,800-second offered windows
and drained observed owners. PostgreSQL service metrics remain separate in the raw
records. Native heap companion profiles are separately instrumented; primary long
runs do not claim an exact native heap peak. The preceding four SQLite values and
its observed old-after p99 regression remain unchanged below.

Original ZIPs: `/home/agent/DB-Perf-01-artifacts/campaign-45461269267/checkpoint-6.zip`.
Audit/retry records: `/workspace/scratch/37c4f8cc3a91/campaign-attempt5-long-checkpoint6/`.
Full read-only reproduction uses `benchmarks/db-perf/analysis/verify_current.py`
with runtime ZIP SHA `aecbd4e949e333399704ba141f7d52e9225323e658f6180262355831b5aec7e8`,
this checkpoint SHA, expected run `45461269267`, attempt `2`; do not use
`--require-eight-long` until all eight original records exist.

### Owned projection encoder: actual two-package and public Native AOT results

The source-tree-external consumers use actual `0.1.0-ci.1` packages built from
producer `6f8272c48ac170230ef44b79a5138836d92b1155`, whose exact tree equals `33d6`.
Signed Git object identity, package contents and actual loaded native SHA were
verified. Package IDs remain independently installable and public APIs are unchanged.

| Provider | Actual nupkg SHA-256 | Actual loaded native SHA-256 |
| --- | --- | --- |
| PostgreSQL | `16f5ddb5454183f2417e4b24290726b1c423a15b50ed173f887f999c36427518` | `73f725104fb1bee5fc86a9bc371e556ea8358ac3a2d774c4823185e6da8984c6` |
| SQLite | `f310fb2edf1c6fc763a9b6d532b7ab0fa0b8db6925cb27a22260200d64decf26` | `970a8868290cec37c353bbd8e48bb7bf4ef18cfa1da9e495fc06d7eb08d71d40` |

Normal B09 gate passed 24 commands with 155 unchanged registered source inputs,
42 C ABI signatures, API/golden/native fixture/AOT/sample checks and the calibrated
allocation regression. Gate log SHA
`72575f492a276dd965d52d8f8fc92e44003985d0b244980bb1deee2e3bf4ea76`.
The measured owned-buffer regression budget is 9,438,704 B per 8,192-operation
window, retaining observed whole-process overhead; it does not assert zero.

Twelve newly interleaved scalar processes compare actual prior `2e9` and `6f827`
packages with unchanged source, same local data and raw all-thread allocation/GC
counters. Strict post-cleanup validation passed:

| Scalar public query | Prior `2e9` B/query | `6f827` B/query | Change B/query |
| --- | ---: | ---: | ---: |
| PostgreSQL dynamic | 14795.479167 | 12170.833333 | -2624.645834 |
| SQLite dynamic | 14799.145833 | 12146.812500 | -2652.333333 |
| PostgreSQL prepared | 5237.583333 | 5163.104167 | -74.479166 |
| SQLite prepared | 5243.895833 | 5163.895833 | -80.000000 |

Prepared execution does not re-encode its projection; its small changes remain
unattributed, not a proven benefit of this encoder. Actual ELF/package/source
identities and raw counts are in `projection-public-allocation-interleaved-v1/`.

Twelve separately interleaved business processes return the same 100-order list,
capacity 128, 80 strings, 20 nulls and digest `12366612025187139697`:

| Business result query | Prior `2e9` total B/query | `6f827` total B/query | Process GC 0/1/2 before → after |
| --- | ---: | ---: | --- |
| PostgreSQL | 26783.743056 | 22720.263889 | 9/0/0 → 6/0/0 |
| SQLite | 26791.097222 | 22741.430556 | 9/0/0 → 6/0/0 |

Each lane/provider has 1,152 queries and 115,200 rows in three independent
processes. The separate graph clone remains 7,480 B in all processes, with 144 B
of extra whole-process overhead retained in each 9,216-graph window. Framework
exclusive attribution remains null. Comparison SHA
`e392331ae209b11d73a46be2d8a0816c6d5c1a86ce7aaec132cfba33aca262a0`.
Original artifacts are under `/home/agent/DB-Perf-01-artifacts/`, in
`candidate-33d6cc8/`, `projection-component-gate-v1/`,
`projection-public-allocation-33d6-v1/`,
`projection-public-allocation-interleaved-v1/` and
`projection-business-results-33d6-v1/`. Shared-host timing is not throughput acceptance.

### Current isolated stack-buffer experiment and completed runtime diagnosis

Worktree: `/home/agent/DB-Perf-01-worktrees/Korda-projection-stack-DB-Perf-01-linux`,
base `33d6`. Current product files are `OperandEncoding.cs` SHA
`63501990982a3767bec56218a14ded677827a1997dd9a811bbe4ab1a8b5fae24`,
`MetadataBindings.cs` SHA
`b425e1fc43d6772b5b78191b825b3566dbcf0eca3b57637fba6a617ec5776c3f`,
and `QueryContext.cs` SHA
`9684c9baf344e35068469a30beadfee6d032e42779cc6c8f9bc37ff6a2e2c39b`.
The proposed immediate synchronous ABI calls borrow at most 4 KiB caller stack
space, explicitly initialize reserved wire bytes, preserve two expression
validation passes and codec binding order, and retain owned-array fallback.
Independent review and poison/boundary/error/lifetime tests are pending.

Three actual before processes ran before any product edit. Six further interleaved
AOT processes compare identical encode-and-consume source. All ten complete wire
shapes, input fingerprints and owned-encoder error outputs match. Actual after
whole-process increments are zero in every 4,096-operation window for fitting
1/4/8-field metadata/expression and 32-field metadata cases. The 32-expression
4,266-byte frame still allocates 4,296 B/operation, and both 128-field fallbacks
retain 13,824/16,896 B. This is a prebuilt internal encoder with no business result,
not zero allocation for a public query. Retain the before 1,096 B/window extra in
four-field metadata. No subtraction or rounded-zero inference is used.
Artifacts: `projection-scratch-v1/`; comparison SHA
`c5c02b3c5a772619bba00983070c9c3bf665863bf710eb51d8b1d9214158e073`.

The [runtime-spin diagnostic 45498304114](https://github.com/IzuSharp/Korda/actions/runs/45498304114)
finished all 36 cells, zero errors and zero unstarted cells. Artifact `14969063762`,
2,473,436 B, SHA
`5157596381f2b8802c97228e06d92052e8b26a24e7f54902edc7fb655b211fdf`.
Original runtime inventory remained unchanged. This separately admitted diagnostic
changes only runtime spin settings and earns no formal long-segment or production
optimization credit. Independent raw recomputation remains pending; keep observed
SQLite Dapper p99 increase. Production defaults and formal workload are unchanged.

### Durable evidence and exact recovery work

Full local Plan is at reviewed schema-5 integration
`f2318a5050f868e6c51942bb616a7a1c8cf77077` before this handoff-only update.
The independent readable-storage review and complete old/new/frozen-history gates
passed; original UTF-8 bytes, fixed predecessor indexes, historical failures and
acceptance claim values are preserved. Thin public Plan is `b5e5a37` before this
handoff update. Preserve both full and thin histories and the `00f8` and `403c`
review/withdrawal documents; never reset the full worktree to the thin tree.
The queue at `plan-readable-publication-v1/queue-f2318a5/` targets the frozen full
`f2318a5` tree. Reconcile this newer handoff after those source-bound objects;
never overwrite it with the older queue copy. Previously rejected opaque uploads
remain stopped. Readable original UTF-8 objects and previously successful blobs
are being queued separately. Twenty-one original binary objects and one deferred
capsule inventory remain explicit holds pending path/hash-bound actual-content
review. Incomplete object publication is not complete evidence publication.

Continue in this order: close stack experiment review/correctness and actual
public-package benefit; freeze the final candidate and run its matching complete
four-column/two-provider long campaign; complete raw evidence publication,
remaining SQL/plan/source review and stopping justification; normal PR merges,
main checks, automatic preview and actual NuGet-download AOT consumption. The final
Chinese report must state unknown attribution, retained regressions and exact
measurement scopes alongside actual improvements.

## Live continuation — 2026-11-24 22:18 UTC (2026-11-25 06:18 Asia/Shanghai)

Continue from the current worktrees and original receipts. The product task branch
is `ef998f6f716412b3bf3bcf4434949c6b595b2f18`; product inputs are those of
`fe56abc2b55fa851de3651b1cec228ed1ce83a0a` because `ef998` only adds a bounded
runtime-spin diagnostic. The actual newly consumed provider packages were built
from GitHub merge producer `2e9e0c040403510cd50c725e31f94dd08f167a5c`, tree
`295440dbf50a4b29d0452160b0d24b2925ebc605`, byte-equal to the `fe56` tree.
The further projection encoder experiment is still isolated and uncommitted.
Both PRs remain draft: [Korda #37](https://github.com/IzuSharp/Korda/pull/37),
[Plan #32](https://github.com/IzuSharp/Plan/pull/32). No merge, public preview or
downloaded-public-NuGet acceptance is claimed.

### Four original long segments independently checked; final candidate still open

The original [campaign 45461269267](https://github.com/IzuSharp/Korda/actions/runs/45461269267),
attempt 2 / job `138688263792`, remains on its admitted VM and original `3d5ba3f`
runtime. **Four SQLite segments are independently qualified: 7,200 effective
seconds, 4/8.** PostgreSQL/direct_cpp is in progress. Do not change the running VM,
relabel these old after binaries as the new `2e9` package, or credit pending time.
The fixed before remains `771bc77cbd68d3f932b99ed2497c0697bbba5f02`.

Each completed segment has 348,866 planned, sent and successful operations,
8,512,405 rows, zero failures/rejections/retries, and an exact 1,800-second
planned-arrival window. All use the frozen sustainable rate and concurrency 4.

| SQLite original route | Success ops/s | p50 / p95 / p99 ms | CPU user / system s | CPU ms/success | Managed B/success | GC 0/1/2 |
| --- | ---: | --- | --- | ---: | ---: | --- |
| Direct C++ | 193.814379 | 0.101888 / 0.630784 / 1.376256 | 754.713448 / 6.862146 | 2.183003 | N/A | N/A |
| Fixed before Korda | 193.813334 | 0.708608 / 21.102592 / 44.826624 | 1102.856381 / 96.555582 | 3.438031 | 68402.335636 | 1439/127/14 |
| Independent Dapper AOT | 193.814287 | 0.159744 / 0.991232 / 1.400832 | 798.969268 / 10.759949 | 2.321032 | 7368.832824 | 154/14/2 |
| Original `3d5` after Korda | 193.813870 | 0.696320 / 21.495808 / 46.923776 | 1097.552831 / 96.379242 | 3.422323 | 47223.985324 | 987/87/10 |

Retain the old after p99 increase from 44.826624 to 46.923776 ms; these observations
do not support an all-metric improvement. Whole mixed-workload allocation includes
business results, framework, runtime and harness; exact components remain unknown.
GC events describe the entire shared managed heap, not separate business/framework
GC. The six Korda owner counters return to zero. Dapper's application connection
counter drains to zero; provider-internal/native owner counts remain unobserved.
Steady / sampled-peak RSS in route order are 19,222,528 / 19,402,752 B;
61,562,880 / 62,201,856 B; 50,155,520 / 50,630,656 B;
56,283,136 / 56,868,864 B. Separate wait4 lifecycle peaks include earlier exec
images and must not be called exact isolated application/native-heap peaks.

Checkpoint 4 artifact `14967952995`, 17,153,749 B, has SHA-256
`da74260271d08f0f9a4be0e5754ba4542da32fbf746292d4f171ad62c783ac55`.
Its 2,300-member archive and incremental observations were audited under
`/workspace/scratch/37c4f8cc3a91/campaign-attempt5-long-checkpoint4/`;
segment audit SHA `b821d501ba99c0761f621c5492ab68b96d58b4861e86e24e75ebf5beae555152`.
Original ZIPs are under `/home/agent/DB-Perf-01-artifacts/campaign-45461269267/`.
The independent full raw verifier recomputed 237 observations, four long segments
and retained 74 ordinary SLO failures; its `matrixAccepted` remains false.
Receipt: `independent-checkpoint4-v1/verification.json` in that artifact root,
SHA `a6e92e2799beb0226287030ccba081c706cb9d5628de7884a2b839567a0c1b88`.
The complete final-candidate eight-segment requirement remains open.

### ControlRecord improvement: actual packages and public business consumption

The sorted-field ControlRecord fast path is retained in `fe56`. Original unordered
and invalid paths preserve validation/sorting; output arrays remain framework
allocation. Independent review and the normal abstraction correctness/API/native
and Native AOT gate passed. [CI 45491468585](https://github.com/IzuSharp/Korda/actions/runs/45491468585)
passed. The actual two packages are `0.1.0-ci.1`, produced by `2e9` above:

| Provider | Actual nupkg SHA-256 | Actual loaded native SHA-256 |
| --- | --- | --- |
| PostgreSQL | `94a874df65129de4ee205b1ef5a3323a11319e3216c60a58e8f915361dfc0095` | `73f725104fb1bee5fc86a9bc371e556ea8358ac3a2d774c4823185e6da8984c6` |
| SQLite | `2967ed60f5e3a6ca7486e5c815d77804f962bfbf2017274cc5810640c5b2dfb3` | `970a8868290cec37c353bbd8e48bb7bf4ef18cfa1da9e495fc06d7eb08d71d40` |

Package payloads, producer Git tree, ELF identities and loaded native bytes were
verified; originals are under `candidate-fe56abc/` in the artifact root. Ordinary
source-tree-external PackageReference Native AOT consumers use unchanged source.
Twelve interleaved old/new scalar processes use the same database and source:

| Scalar public query | Original `3d5` B/query | New `2e9` B/query |
| --- | ---: | ---: |
| PostgreSQL dynamic | 19649 | 14803.375 |
| SQLite dynamic | 19663.354167 | 14794.958333 |
| PostgreSQL prepared | 5185.479167 | 5249.854167 |
| SQLite prepared | 5163.979167 | 5251.229167 |

The prepared increases of 64.375 and 87.25 B/query remain observations with
unresolved attribution; do not erase them as noise. Buffered first-batch windows
remain 0 B only in their measured scope; refill windows remain 512 B. This scalar
fixture produces no business DTO/list/string result. Public whole-query framework
exclusive attribution is still unknown. Source, counters and strict validation are
under `control-public-allocation-interleaved-v1/` in the artifact root.

Twelve separately interleaved business-result processes return the same
`List<OrderDto>` of 100 DTOs, capacity 128, 80 strings and 20 nulls, with identical
content digest `12366612025187139697`. Whole-process totals fall from
34,749.256944 to 26,776.784722 B/query for PostgreSQL and 34,759.881944 to
26,796.097222 B/query for SQLite. Each lane/provider has 1,152 queries and
115,200 rows; GC totals stay 9/0/0 in both lanes. An independent same-graph clone
is 7,480 B/graph in every process. This establishes a business graph fixture cost,
not an exact in-query allocation trace: do not subtract it as precise framework
bytes. Original results and analysis are under `control-business-results-fe56-v1/`;
comparison SHA `b673fdfd77ba0a44cac3fabcc3347e2875814ce3c48fec3d5304f70f04cdcd6f`.
Two failed PostgreSQL AOT compile attempts (exit 137) remain recorded. A subsequent
serial, build-only processor-count-two compilation passed; measurement processes
unset that build override. No shared-host timing is used for throughput acceptance.

### Next product experiment and runtime CPU diagnosis

Projection encoding at
`/home/agent/DB-Perf-01-worktrees/Korda-projection-encoding-DB-Perf-01-linux`
has one product edit, `src/Query.Binding/OperandEncoding.cs`, SHA
`ac85d745e3613a9c9438d29d338f38d10a4c116c75213b53bd9153bae1b8210f`.
The direct writer preserves the old fallback for oversized or invalid metadata,
binding order, exact wire bytes and an independently owned output array. Six
interleaved original Native AOT microprocesses show 8-expression fields falling
from 12,184 to 1,152 B/encode, and 32-expression fields from 48,088 to 4,296.
Ten complete golden shapes and exception results match. Retain the unexplained
1,096 B per 4,096-operation-window observation in two small cases; no universal
zero-allocation claim is made. Results: `projection-encoding-v1/interleaved-v1/`,
comparison SHA `e5ebda3b63249799d1507487f07b47e6afbc12688125c459bd0c0d031c85753f`.
Independent source review found no blocker. Newly frozen boundary/concurrency
tests are now being compiled and calibrated in `projection-regression-v1/`;
formal module gates, public candidate packages and composite validation are pending.
Do not credit the internal ProjectReference probe as a public-package acceptance.

The separate [runtime-spin diagnostic 45498304114](https://github.com/IzuSharp/Korda/actions/runs/45498304114)
is running on a separate admitted VM. It changes only the original process runtime
spin setting in 36 bounded, interleaved cells using original AOT binaries; it is
not a product setting change or formal long-run segment. The v2 independent review
closed the interrupted atomic-state-write failure with the original fault injection;
review SHA `384712153e5afb7f24d859ed4acc9f32030102bf8737327ae4bdd9cc4f314f12`.
Normal [ef998 CI 45498319936](https://github.com/IzuSharp/Korda/actions/runs/45498319936)
is still running. Source-only remaining-hotspot notes are not a final stop decision.

### Evidence publication and recovery

The full Plan worktree is
`/home/agent/DB-Perf-01-worktrees/Plan-DB-Perf-01-linux`; retain its full history.
The thin public head `403c061e7c4110eb17a4a4e2817856ebe3044067` adds the
PreparedQuery forwarding withdrawal decision to `53105de`; preserve both documents
and the earlier `00f8` review files. Its thin status is not complete raw evidence.
Schema 5 readable storage is being reviewed independently in
`/home/agent/DB-Perf-01-worktrees/Plan-readable-schema5-DB-Perf-01-linux`.
It preserves original UTF-8 bytes, fixed predecessor indexes and claim values;
original binary/capsule identities remain separate. The earlier opaque upload queue
stays stopped. Do not retry rejected compressed records or repackage denied source,
helper or runtime archives. The 21 original binary objects and one deferred capsule
inventory representation remain explicit work; neither a sparse tree nor a count
of uploaded chunks is full publication or eight completed long runs.

Continue with projection AOT regression and actual public-package validation,
new checkpoint audits and runtime-spin interpretation, then freeze a final package
candidate and run its complete matching four-route/two-provider campaign. Complete
readable evidence integration, correctness/SQL-plan/source review, independent PR
review, normal merges, main CI and actual downloaded preview AOT consumption before
declaring this batch complete.


## Live continuation — 2026-11-24 21:17 UTC

The original formal campaign [45461269267](https://github.com/IzuSharp/Korda/actions/runs/45461269267)
remains on attempt 2 / job `138688263792`, the same admitted VM and frozen
`3d5ba3f` candidate. **Two original long segments are independently qualified:
SQLite/direct_cpp and SQLite/korda_before, 3,600 effective seconds (2/8).**
Segment 3 is in progress. Keep this VM and its original runtime immutable.

Checkpoint 2 artifact `14964600687` is 16,096,804 B, SHA-256
`e701a017000e8c1c88471e7a7ee67ebb739166e5d9f911af1163e8e5ea7d6c17`.
Its SQLite before interval is 20:20:31.0672606Z through 20:50:31.0755121Z,
with an exact 1,800-second planned-arrival window. All 348,866 planned/sent
operations succeeded; failures, rejections and retries are zero; 8,512,405 rows.
Success throughput is 193.813334 ops/s; p50/p95/p99 histogram upper bounds are
0.708608/21.102592/44.826624 ms. Client CPU user/system is
1,102.856381/96.555582 seconds, or 3.438031 ms per successful operation.
Whole-process allocated bytes are 23,863,249,224, or 68,402.335636 B/op and
2,803.349843 B/row; GC generation deltas are 1439/127/14. These mixed-workload
totals include business objects, framework, runtime and harness: exact business
and framework components remain unknown. GC events are process-wide.

The six Korda owner counters return to zero. Steady sampled RSS/PSS medians
are 61,562,880/52,329,472 B; sampled peaks are 62,201,856/52,972,544 B.
The separate wait4 lifecycle RSS peak is 64,045,056 B, including earlier exec
images; it is not an exact isolated application or native-heap peak. The complete
2,284-member ZIP audit and raw-count recomputation are retained locally under
`/workspace/scratch/37c4f8cc3a91/campaign-attempt5-long-checkpoint2/`.
The segment audit SHA is
`706975c0731a676dc1eeffa4f6e853e0fcd7aafaf61cac742e65e815c8d019a6`;
the original archive is under
`/home/agent/DB-Perf-01-artifacts/campaign-45461269267/checkpoint-2.zip`.
The first two segment captures and acceptance-index bindings still await the
reviewed readable-storage integration; do not infer a completed batch from them.

### A new measured production experiment is not yet a released candidate

An isolated task worktree,
`/home/agent/DB-Perf-01-worktrees/Korda-control-encoding-DB-Perf-01-linux`,
starts at `7cf6c7db4957fdb27ea408b56d52ce1b28235a5b`.
Only `src/Data.Abstractions/DbWire.cs` changes product behavior: already positive,
strictly increasing control-field IDs skip temporary Distinct/sort state.
Unordered/invalid inputs retain the old validation/sorting fallback; payload
arithmetic remains checked. Public APIs and encoded bytes are unchanged.

The actual isolated Native AOT comparison uses three independent processes per
lane and 8,192 measured encodes per case after 2,048 warmups. A five-field frame
falls from 1,064 to 136 managed B/op, four fields from 1,016 to 120, and 32 fields
from 3,568 to 1,080; each lane's three processes agree exactly. Whole golden
frames and seven exception type/message observations match; caller arrays remain
unchanged. The output byte[] is **framework allocation**, including the remaining
136 B. Business-result allocation is zero only in this prepared-input encoder
fixture. This is neither an entire-encoder 0 B claim nor a public-package/DB test.

The experiment is at `/home/agent/DB-Perf-01-artifacts/control-encoding-v1/`.
Original comparison SHA:
`cd07281aa0651eb8d1cd3ea0f4ad88849d76730203bb073d300e52c2dcfe8516`.
Before/after product source SHA:
`d9b3101900038e81707dea2d0d82ec793fd83b0e52d3b5de785ad8a896c101f4` /
`a0178f6ccc63f0431e5f7af03caec691eefa90661e1cd591c920a3e6ed02eaa6`.
Independent review found no blocker; receipt
`/workspace/scratch/37c4f8cc3a91/control-encoding-independent-review-v1/independent-review.json`,
SHA `9f99516aab4a68723f3ffe8666bcc2f8f32ccefbeaadc6afc1a8977bf48ec59c`.
Short correctness/allocation regression integration is being prepared before
normal affected-module checks and actual provider-package consumption.
If retained, this new product change needs measurements bound to its actual new
packages/ELFs. Never relabel the running old candidate's after measurements.
The broader remaining-hotspot/stop decision is still open.

### Readable publication recovery

The old compressed upload queue remains stopped. A materially safer alternative
was actually reviewed and accepted for the two specifically rejected records:
their original UTF-8 NuGet assets metadata and successful publish log, under
explicit paths, without content rewriting. The resulting unreferenced Git tree is
`cc860978d154c52165231079074c11ed4a647dd1`; no incomplete full-evidence branch
was published. Exact-byte, whole-index migration controls and independent review
are retained; the full local storage correction commit is
`1b6da786b03080536343529270d58a2d2f8e97d2`.
Broader readable records and a complete original-member representation are under
individual content and schema review. Do not restart the old opaque queue or
repackage rejected implementation/helper/runtime archives.

The full Plan worktree now resides at
`/home/agent/DB-Perf-01-worktrees/Plan-DB-Perf-01-linux`;
the old `/workspace/scratch/b94e2a0e0c3f/Plan-DB-Perf-01-linux` path is a compatible
symlink. Preserve its full local history and the concurrent `00f8` review files.
The thin public Plan `c90ad9cdf33ab36b25607c865648968ab3f9fae1` has passed
[CI 45482414872](https://github.com/IzuSharp/Plan/actions/runs/45482414872).
Both PRs remain draft and unmerged. No preview/public-NuGet acceptance is claimed.
The runtime-spin source/ELF review is frozen; the separate sensitivity experiment
has not executed or changed the formal workload.

## Live continuation — 2026-11-24 20:31 UTC

The sole formal run remains [45461269267](https://github.com/IzuSharp/Korda/actions/runs/45461269267),
attempt 2 / job `138688263792`, on its original admitted VM. **One long segment is
independently accepted: SQLite/direct_cpp, 1,800 effective seconds (1/8).**
Its original start/end are 19:50:19.084887Z / 20:20:19.086406Z; all 348,866 planned
operations succeeded, zero failed/rejected/retry, 8,512,405 rows, p99 1.376256 ms,
and all observable native owners returned to zero. Checkpoint 1 artifact
`14959984432` has SHA `35bfafc773c1fa63621ff356b44e0b6c3670e094dce544d8e28707e2a6075c3f`.
The second segment is running. Do not restart the VM, overlap formal work, or
credit the other seven planned durations. The independent segment receipt is
currently local at `campaign-attempt5-long-checkpoint1/long-segment-audit.json`,
SHA `10f264efe5e032a78a97d790530397543a6e7e155925be0668d7cb185b2c75fd`;
its Plan capture remains pending.

The preflight semantic checkpoint (`checkpoints/campaign-preflight-semantic-v1/README.md`, local evidence verified; publication pending)
independently checks all 233 actual cells, 2,268 original members, 7,863 measurement
samples and 122 PostgreSQL owners including seed initialization. Frozen rates are
PG 180.627 and SQLite 193.814 planned ops/s. Full counts include deliberate
overload; do not misreport its rejection total as ordinary-load errors.
Fixed 15-second E2E allocation fell 31.963% (PG) and 30.968% (SQLite), but PG
client CPU/op rose 10.101% in that short window. Preserve this and all other
regressions; neither one short window nor allocation alone settles overall performance.

The CPU/preparation checkpoint (`checkpoints/cpu-and-preparation-diagnostics-v1/README.md`, local evidence verified; publication pending)
preserves the original ACK failure, two successful native plan comparisons,
five real CPU sampling windows and their original zero-exit/empty-report errors.
Offline recovery [45478326583](https://github.com/IzuSharp/Korda/actions/runs/45478326583)
succeeded without new workloads or samples; all 165 retained original members
match byte-for-byte. Its artifact is `14961052236`, ZIP SHA
`a134dd2d3c4d2ef0fdeace739deee398e9b281311098443b97bf836681653657`.
Actual period-weighted RhSpinWait self shares are after 50.76%, before 49.35%,
Dapper 66.69%, with per-thread rounding retained. Runtime spin can be induced by
framework scheduling; it is not excluded from E2E cost. A separate bounded
runtime spin sensitivity candidate is being prepared, not executed or substituted
for the formal measurements. No new production modification is implied.

Current Korda task head is `7cf6c7db4957fdb27ea408b56d52ce1b28235a5b`, tree
`4415bcec0595390513b52e945194097becd670d8`; normal CI
[45478344194](https://github.com/IzuSharp/Korda/actions/runs/45478344194) succeeded.
Measured production/package inputs remain the exact `3d5ba3f` candidate.
Korda `9acd` CI 45473109770 and thin Plan `a9e19` CI 45474742579 also succeeded.
No merge, automatic preview or downloaded public preview validation is claimed yet.

**Evidence upload is stopped after automatic approval review rejected two opaque
gzip blob calls.** Original 1,406 objects and the first 193 a0 increment objects
are verified remotely. Rejected indexes 193/194 are the Dapper SQLite consumer's
NuGet `project.assets.json.gz` (5,930 B compressed / 48,320 B original) and
`publish.log.gz` (184 B / 347 B). The reviewer could not see a path, manifest binding
or readable content proving the disclosure scope. Full rejection and verified
content metadata remain in `plan-upload/incremental-a0b455b/auto-review-stop-20261124T202554.json`,
SHA `56e1152fc4859c3e0c24596b06e7c12ca0dd02646bbd5f8abd6c2cc0976cc66a`.
The original [automatic-review stop receipt](publication/upload-review-stop-20261124.json) is also retained as readable JSON.
Do not clear STOP or resend these opaque payloads. A transparently readable,
path-bound measurement representation is being evaluated before any further
publication. All later compressed queues, including the new pure-measurement
capsule, remain unsent. Never repackage the separately rejected historical
implementation/helper archives into Plan.

Thin public Plan remains `a9e19a15b18ce71bcc537da6e8c1973a68d8effe`; full local
Plan contains the pending raw/source-bound checkpoints. Preserve the full local
tree and all 00f8 concurrent reviews when eventually publishing against the actual
remote head. Large new intermediate artifacts are stored under
`/home/agent/DB-Perf-01-artifacts/` with exact hashes and local path receipts;
repository sources remain in their task worktrees.

Business List/DTO/string/typed-JSON objects are required business allocations,
including those created by generated mappers. Framework overhead targets 0 B;
unknown residuals remain unknown. GC counts are shared process events. The only
measured zero claim remains the already-buffered scalar advancement window.
Wait4 high-water includes child lifecycle across exec; sampled RSS/PSS and
application-reported peak are separate. Original samples contain no VmHWM, so an
exact native post-exec RSS high-water cannot be reconstructed retroactively.


Publication transport checkpoint: the full verified local Plan commit is
`f0ba275fd759047f352d41d19379ae52193088bf`, tree `0a44b271746b0173db2d387bce50ed10b445f967`.
The queued diagnostic-tools-v1 increment adds 41 binary objects after the
existing queues. This remote checkpoint publishes only the recovery text;
paths marked pending below are not yet available at this remote revision.

## Live continuation — 2026-11-24 19:47 UTC

The sole formal campaign remains
[45461269267](https://github.com/IzuSharp/Korda/actions/runs/45461269267),
attempt 2 / measure job `138688263792`, observed in admission/calibration.
**Accepted long segments remain 0/8, effective accepted seconds 0.** Do not
start an overlapping formal campaign or count its planned durations. Its frozen
runtime, actual packages, eight application ELF hashes, request and dedicated VM
have not been changed by the separate diagnostics below.

Korda task head is now `9acdc6a8cef25d6f51feaf69e553b36027ab3975`, tree
`53600057025a1739c6c7521ddc4ab4f77e0cb1e9`. The measured production remains the
exact `3d5ba3f` candidate; subsequent changes add release receipt retention,
diagnostic controls and evidence validation. CPU entry `275920fa` passed normal
CI [45470772884](https://github.com/IzuSharp/Korda/actions/runs/45470772884).
Read the latest normal CI for dcb371 and 9acdc6 before claiming their completion.

The separate CPU run
[45470764239](https://github.com/IzuSharp/Korda/actions/runs/45470764239) preserves
two unsuccessful sampling attempts. Attempt 1 rejected image `133.1` before
checkout/build. Attempt 2 used required image `376.1` and recovered exact matching
Native AOT symbols for before, after and Dapper. However, actual perf returned
five bytes `61 63 6b 0a 00`; the original entry expected four bytes without the
terminal NUL. All five original workload processes remained gated, every owned
collector and PostgreSQL owner retired, and no CPU workload result is credited.
The original ZIP `14956787494` is preserved with SHA
`c53cc46d2fb2d00c0af1726aa46b7eabbb3ff07085388aced3b0464b49b994e7`.
The first informal byte counts were off by one; the explicit correction addendum
keeps the original ACK strings and source records unchanged.

The two independent native plan cells in that same second attempt did complete:
each reports 35 measured operations, 854 rows, 350 warmup operations, full 35-case
coverage and drained owners. Their SQL/parameter/eleven-execution comparison is
being independently finalized. They must not be discarded merely because CPU
sampling failed, and they do not count as qualified throughput or long segments.

The minimal ACK fix is independently reviewed against all five actual raw frames
and 25 finite controls. Only parser handling and the request activation note
changed; sampling privileges, PID scope, immutable executable inputs and workload
contracts remain fixed. New separate run
[45473095059](https://github.com/IzuSharp/Korda/actions/runs/45473095059),
job `138726028027`, passed its image/source/control checks and entered tool/profile
preparation. Actual stack collection remains unproven until its result is read.

The `checkpoints/diagnostic-tools-v1/README.md` (verified locally; publication pending)
retains original reviews, finite controls, the initial image failure and Plan CI
repair. The archive auditor is fixed at Korda `dcb371f567dfa0d0b692ff76c2f5fed311a6b014`,
tree `ed24130a128ae34abc41db6f62d03a22d884c179`. Its independent review resolved a
deflate-tail payload defect. The Plan gate now requires the reviewed Git bytes,
an index-bound receipt and all chunk records, then actually reconstructs and
reads ZIP members. Ten finite integration tests and the existing full source/raw
gate passed. No real new campaign capsule existed in that invocation; its first
capture must still undergo the actual archive audit. This does not permit source,
helper, runtime, ELF or package archives to be repackaged into Plan.

Plan's thin remote head is `48aca52fac5540616807a23e0f09edf2c2797d80`. Its normal
CI [45470976223](https://github.com/IzuSharp/Plan/actions/runs/45470976223) passed
after pending local-only checkpoint links were explicitly marked. Full local
evidence still awaits the existing blob queues: original queue most recently
1,323/1,406, then a0b455b, c5dfd24, 56371d3 and e900daa; 0858d1a is a text-only
overlay preserving the concurrent 00f8 review. Never replace that full local
tree with the thin remote tree. Re-read the actual remote parent before publishing.

Allocation interpretation remains: required DTO/List/string/JSON graphs are
business costs; framework temporary work remains overhead. Process GC events
are shared-heap observations. Full queries remain positive and partly unattributed;
the measured zero claim is confined to the already-buffered scalar row window.

## Live continuation — 2026-11-24 19:11 UTC

Read this section before the historical observations below. The active campaign
is still [45461269267](https://github.com/IzuSharp/Korda/actions/runs/45461269267),
attempt 2, measurement job `138688263792`. Preparation `138685089344` completed
successfully. The latest observed measurement step is admission/calibration;
**accepted long segments remain 0/8 and accepted effective seconds remain 0**.
Do not launch an overlapping formal campaign or credit planned durations.

The actual runtime artifact is `14953201071`, ZIP SHA
`aecbd4e949e333399704ba141f7d52e9225323e658f6180262355831b5aec7e8`,
tar SHA `735b47e883859edb9efaa615d00d93aca843c06522c757aa94c870ecd3c7f85c`,
manifest SHA `5a2eba0796a009bfa316dfc07c66919c8b3e14f600faa808e96cd32da617885c`.
Checkout remains `d665c0c9629922cfff0e48fa535d6f21393f8162`, executing harness
`da153c22ef1093fccc3233ec76bfda96e6cc59df`. The
`checkpoints/campaign-runtime-45461269267-v1/README.md` (verified locally; publication pending)
checks all 2,257 file entries and eight application cells. All application ELF,
package and native-library bytes equal the preceding runtime; only controller,
request and build/CI receipts differ. This supports identity reuse, not reuse of
qualified performance across VM boots. The first rejected image attempt remains.

Product branch head is now `272036290cae784e2c085e768fd0cf896e8fb37e`, tree
`fa0fc051456f9310f47f4c5bfb9e8633f038996e`. Its only change from d665 is
release artifact retention: actual signed NuGet downloads, verification JSON,
signature logs and existing public Native AOT receipts will survive the runner.
The independently reviewed bytes and publication responses are in
`checkpoints/public-receipt-retention-v1/README.md` (verified locally; publication pending).
Normal CI [45464901812](https://github.com/IzuSharp/Korda/actions/runs/45464901812)
passed all selected checks and Verify; PR publication correctly skipped.
Normal CI for da153 and d665 also completed successfully. No merge or public
NuGet release has yet been accepted, and the measured product remains 3d5ba3f.

`checkpoints/actual-pg-plan-comparison-v1/README.md` (verified locally; publication pending)
reparsed the original four-route server logs from failed preflight 45452087158.
Both Korda variants have identical plans. Dapper's 31 non-CRUD cases match them;
its CRUD Find omits a Limit node over the same one-row primary-key Index Scan.
Two Korda pre-commit SELECT 1 executions per 35-case cycle remain explicit.
Direct C++ has a different later access path for range, offset and early-stop
with the same SQL and ordered values; generic/custom plan selection is a
hypothesis because the original counters/OIDs are unavailable. Existing native
timing/protocol layers contain no actual plan records and cannot close this gap.
The next separate diagnostic holds protocol confirmation constant while comparing
per-operation versus reused preparation; the formal workload stays unchanged.

An independent CPU diagnostic is being implemented for another VM using the same
frozen ELF bytes. The original runtime omitted Native AOT .dbg files, so symbols
must be recovered from a rebuild whose ELF bytes and debug identity exactly
match before claiming managed method attribution. No CPU stack profile has yet
been observed. Do not close the optimization stopping obligation from source
review alone. The framework/business allocation distinction remains unchanged:
required business graphs are business allocation; shared-process GC events are
not mechanically divided into framework and business collections.

Raw Plan publication continues from its durable content-addressed queues. A host
interruption lost some responses; five original in-flight objects were recovered
by read-only SHA/byte verification, one confirmed absent object was then uploaded.
No already-confirmed object was resent. The original queue most recently had
1,009/1,406 verified objects, followed by the existing a0b455b, c5dfd24 and
56371d3 incremental queues. Keep every manifest and prior raw checkpoint.
New measurement ZIP byte-chunk storage is being prepared with an explicit
archive/member audit; it must not package source/helper/runtime archives or
weaken existing checks. Until that implementation is actually reviewed and used,
ordinary schema3 gzip validation is not an archive-aware audit.

## Independent review update — 2026-11-24 19:03 UTC

The [current candidate/harness review checkpoint](reviews/current-candidate-harness-20261124/README.md)
preserves actual byte verification of both `0.1.0-ci.1` provider candidates from
CI `45438460386`, including all 81 unsigned members and native ELF payloads.
It separately confirms the current sticky correctness-oracle and PostgreSQL
cgroup CPU implementations at `d665c0c`. Only review records, hashes and an
existing historical raw-counter observation are added; no new runtime or
historical source archive is included. Candidate artifacts remain distinct from
actual public NuGet acceptance.

At this live observation, the sole campaign `45461269267` had completed
preparation and remained in VM admission/calibration. All eight long steps were
pending: **0/8 accepted segments, 0 effective seconds**. Current product branch
head `272036290cae784e2c085e768fd0cf896e8fb37e` adds preservation of future
public registry/consumption receipts; it does not change the frozen campaign
request, measured packages or consumer workloads. Re-read the live run before
any continuation and do not start an overlapping campaign.

## Live continuation — 2026-11-24 18:38 UTC

The measured product remains actual package producer
`3d5ba3f9884308caa691718f73a74aa42be19d94`, tree
`74a76bc5d00671a48221d0ed19002a3ffffd319f`; the new work changes only the
calibration controller and its request. Business List/DTO/string/typed JSON
objects remain business allocation, including mapper-created results. Framework
additional allocation targets steady-state 0 B; shared-process GC counts are
reported once and are not split into invented framework/business collections.

[Campaign 45452087158](https://github.com/IzuSharp/Korda/actions/runs/45452087158)
ended at 2026-11-24 18:16 UTC before any long segment. Its exact checkpoint 0 ZIP
is artifact `14952080637`, SHA
`bc4f1195eba7fcd518120e8e3c61b0e1f6304f8a76dd1992ba7d3da4ebc1cb39`:
783 original records, 69 completed PostgreSQL preflight cells. Initial idle and
quota checks passed, and before-process noise CV was 0.024485870646359646 against
0.1. Full campaign admission and fixed offered rates were not completed.
At frozen concurrency 4, all four before-Korda scheduled rates failed the
unchanged rejection threshold; only the lowest rate also exceeded the p99 limit.
The C8 success cannot substitute for C4. Original planned/attempted/completed/
failed/rejected counts, all histograms, time series and failed points remain.
**Accepted long segments remain 0/8 and accepted effective seconds remain 0.**

The independently reviewed controller repair is public commit
`da153c22ef1093fccc3233ec76bfda96e6cc59df`, tree
`3b3597bc5fbf28e28e7bd5fd9d91e575531b9266`. When every tested rate fails,
it can halve the lowest observed rate using the existing maximum of three
five-second refinement windows, then use midpoints once a success/failure
bracket exists. It preserves every failed observation, the hard iteration
budget, fixed concurrency, SLO and resource gates; if no rate passes it still
fails calibration. Its 43 controller tests and selected routing checks passed.
The source-only combined production review also found no concrete lifecycle
blocker; this does not replace qualified comparative performance evidence.

Activation commit `d665c0c9629922cfff0e48fa535d6f21393f8162`, tree
`f979890608ba0c3f65d4575f55c59c8e5afdacb6`, changes only the request's
harness commit and activation note. Request SHA is
`189fc14ab799b152256c2d92c497c507a6ded2431cad8bdbd362bdc7538adfab`.
The current campaign is
[45461269267](https://github.com/IzuSharp/Korda/actions/runs/45461269267).
Its first preparation job `138684157567` rejected the older runner image before
building; only that failed job was retried. Preparation `138685089344` has passed
the frozen image guard and is building the runtime bundle. Re-read the live run
before continuing; do not overlap campaigns or claim preparation as measurement.
Original/final packages, compiled business consumers, data/workload, queue size,
SLO and eight full 1,800-second durations are unchanged.

[Normal CI 45453261268](https://github.com/IzuSharp/Korda/actions/runs/45453261268)
completed successfully including Verify. The controller's
[normal CI 45461107207](https://github.com/IzuSharp/Korda/actions/runs/45461107207)
is being observed. The previous handoff-only Plan commit `a2c9149b07a37c6dd71a900010203e3de4bc992a`
passed [CI 45454262082](https://github.com/IzuSharp/Plan/actions/runs/45454262082).
Full raw publication remains in progress; content-addressed uploads retain their
manifests/progress, while these handoff-only commits keep the recovery entry live.
Local-only review commits are not asserted publicly fetchable: the reviewed
local b4e9120 tree equals actual public da153c2, and local 5dbd06a equals d665c0c.

## Current recovery point

This is an **in-progress measurement and implementation checkpoint**, not batch
acceptance. Read [plan.md](plan.md), [baseline.json](baseline.json),
[allocation-inventory.md](allocation-inventory.md) and
[acceptance.json](acceptance.json). Long-test credit is **0/8**, with **0 accepted
effective seconds**. No framework-wide zero-allocation claim is established.

## Active campaign and final package inputs — 2026-11-24

**Latest live observation: 2026-11-24 17:56 UTC.** Product branch head is
`c7c0347e30faa9e1d54a201dada7210ee7cd49b8`; that final metadata-only commit
registers the environment workflow with the existing benchmark CI module.
[Normal CI 45453261268](https://github.com/IzuSharp/Korda/actions/runs/45453261268)
is being observed. The current dedicated campaign is
[45452087158](https://github.com/IzuSharp/Korda/actions/runs/45452087158),
workflow source `75db602c59f3c3366488df9f1c1717934f7d850f`, collector/harness
`4ee348d8b9834a14327dcf68a105e34f52f81795`, request SHA
`c32ab5e50fb38cfd1c9a45748e6085c903456bbd8f745112651a9767e84f93bb`.
Both jobs now require the actually observed Ubuntu image `20261116.376.1`
without overwriting actual runner variables or weakening the original bundle
image-equality gate. Its first preparation attempt rejected the older image;
retry `138653923314` passed the image guard and finished preparation. Measurement
job `138657301659` passed the same guard and is executing admission/calibration.
No effective long segment has completed: **0/8** remains the accepted count.

The preceding campaign `45449544703` and its measurement-only retry both failed
before admission: preparation image `20261116.133.1` differed from measured
image `20261116.376.1`. They reuse one unchanged runtime bundle and earn no
credit. Retain their original job logs; these are separate from the earlier
Python inventory and namespace observation defects. The extra workflow's CI
registration omission was corrected without changing the measured harness,
production packages or workload. The first local registration checks correctly
failed because they inspect committed HEAD; after committing the registry fix,
tracked ownership and impact passed and Tooling ran 44 tests with one CMake
availability skip. The actual final CI is checked separately.

The full raw checkpoint upload remains in progress. Remote Plan recovery-only
commits `62ac70899a4add051c48dcdcf54ff96ce25cc8ed` and
`a2c9149b07a37c6dd71a900010203e3de4bc992a` keep the live entry available while
verified content-addressed objects upload; the first passed Plan CI
`45451305502`. The complete local evidence history and pending manifests must
be preserved until the full verified tree is published. Do not assume local
Plan commit `a0b455b8c391b75fcdc8cef754fe8b0ab2c806f5` is publicly fetchable.

Read this section before the older recovery observations below. The measured
product is now frozen to normal CI
[45438460386](https://github.com/IzuSharp/Korda/actions/runs/45438460386), which
completed successfully. Both independent candidate packages are `0.1.0-ci.1`;
their actual clean packaging producer is PR merge
`3d5ba3f9884308caa691718f73a74aa42be19d94`, tree
`74a76bc5d00671a48221d0ed19002a3ffffd319f`. That tree is identical to reviewed
product head `cf7c080aeef01e3b012d0564e6f930b77e9c697f`. Do not replace these
inputs with a later harness-only CI package or label them as the branch commit.

The published harness is `f91f3d24579d7c65199df1c4cdd60a577cdcd8f9`, tree
`9b30108299d80658fb3cc612e0240f88692fe61e`. The task-only workflow was activated
at `2d6db0be65d54f9d3031ac091c406788f76fd748`; its first campaign
[45442350170](https://github.com/IzuSharp/Korda/actions/runs/45442350170) built
all native/AOT consumers, then failed before admission when three Python import
bytecode files changed the immutable bundle inventory. It earns no measurement
credit. The actual archive reproduced that defect; disabling bytecode writes
passed all 2,257 original content/mode/link checks without weakening validation.
The independently reviewed two-file correction is published as
`45da57f62cf89987da400dabde2dc7c3959eb7b1`.

The second campaign
[45444706914](https://github.com/IzuSharp/Korda/actions/runs/45444706914)
completed preparation and immutable bundle verification, then failed at
2026-11-24 17:10:27 UTC because the original quota assessment could not prove
complete cgroup-v2 ancestry. No workload or long segment ran. Its original
`campaign.json` binds request SHA `24597547a7d851c37f2a5aed89a0d8a67971ea9b1267bbca1e21e8e458686c29`
and bundle manifest SHA `3dd608d97e2b3bc14d639ea94bbbb9f2aa1fc0e0f072b0da2422f73f912de8f7`.
It did not save the failed VM's cgroup snapshot; that gap remains explicit.

A separate read-only diagnostic on a new VM,
[45447986595](https://github.com/IzuSharp/Korda/actions/runs/45447986595),
reproduced the failure: all three quota ancestry nodes were observable and
unlimited, but the unprivileged PID 1 namespace read returned `EACCES` 13.
A fixed noninteractive `sudo readlink` observed the original observer and PID 1
in the same namespace. This new observation is not the missing failed-VM snapshot.
The reviewed collector correction is commit
`4ee348d8b9834a14327dcf68a105e34f52f81795`, tree
`cf707c9da12d2bf98df4c2110d41566809918fdc`. It preserves the original error,
strictly verifies two namespace links and the stable original observer identity,
records the read-only helper duration, and saves the raw quota snapshot before
assessment. It changes no quota, namespace, permission, affinity or admission
threshold. Its 41 controller tests passed; new-VM observation
[45449083846](https://github.com/IzuSharp/Korda/actions/runs/45449083846)
then passed the unchanged quota assessment. Full VM admission and performance
qualification remain separate.

The preceding campaign was
[45449544703](https://github.com/IzuSharp/Korda/actions/runs/45449544703),
activated at `663ceb97b3d20c38048ce17869259a6b9df62492`, tree
`2bc751d8b62e1b3a795c9cdad7687ec69bd09c16`. Its request SHA is
`4c5c751d8fd8708ade19e1f1cf291a156f9dd24c84eaa7b33e7afb4f469d88f6`,
with collector/harness frozen to `4ee348d8b9834a14327dcf68a105e34f52f81795`.
Its later image mismatch and retry are recorded in the newer live observation
above; re-read the current live run and never overlap campaigns.
The actual before/after packages, business consumer source, workload, CPU
partition, SLO, resource thresholds, segment order and eight 1,800-second
measurement durations remain unchanged. There is still **0/8** long credit.
Normal merges and public preview verification also remain outstanding.
The `checkpoints/candidate-and-campaign-activation-v1/README.md` (verified locally; publication pending)
retains the package/CI/DTO-edit receipts and first startup failure; the second
failure and environment repair receipts are retained separately in
`checkpoints/campaign-attempt-2-v1/README.md` (verified locally; publication pending).

Two narrowly completed acceptance obligations are now bound to independently
verified `results/completed-claims-v1/README.md` (verified locally; publication pending): real independent
ORM Native AOT queries on both providers, and both actual final candidate packages'
external AOT/ordinary DTO-edit/native-reuse checks. The claims point to 72 existing
original gzip records and twenty original argv sequences. They do not accept any
long segment, qualified performance, merge or public NuGet publication. Dapper is
2.1.100 with Dapper.AOT 1.1.0; actual providers are Npgsql 11.0.0 and
Microsoft.Data.Sqlite.Core 11.0.0 / SQLitePCLRaw 3.0.5.

Two final-package allocation comparisons are complete and must be reused:

- `checkpoints/final-public-allocation-cf7-v1/files.json` (verified locally; publication pending):
  two new external AOT builds and six final processes, with the unchanged original
  six-process baseline reused. Dynamic 256-row query totals fall about 71.7%;
  prepared totals fall about 90.8%. Each provider retains 384 exactly-zero raw
  127-row in-batch windows; every final refill-plus-first-row window is 512 B.
- `checkpoints/business-results-v1/README.md` (verified locally; publication pending):
  six external AOT builds, 18 independent processes and 108 measured windows.
  Both managed routes return the same List with 100 DTOs, 80 independent strings
  and 20 NULLs. Korda totals fall about 50% to 34.73–34.74 KB/query; the isolated
  retained business-graph control remains 7,480 B. Its subtraction is an unresolved
  estimate, not exact framework allocation. All original process GC counts remain.

Neither comparison establishes whole-framework 0 B or qualified timing. The
final cold/concurrent/resource inventory completed twelve independent
processes and passed independent raw review. Its full archive is in
`checkpoints/resources-final-v1/README.md` (verified locally; publication pending). It retains
cold-prepare and PostgreSQL cancellation allocation regressions explicitly. The
independent reviewers checked actual package, ELF, native, source and raw-count
identities; preserved failure records and historical source identities remain
unchanged. Newly completed evidence is being published through the normal Plan
branch; inspect its actual remote head rather than assuming local commits landed.

The active user has authorized production changes, required measurements, normal
PR merges and automatic preview/public-package verification. Earlier DB-Rename
review-only instructions are historical. Their original files and verifier bytes
remain unchanged and are checked at Plan
`bc1956936ee77a997a016856c97def6aabc0bbc6`; the new task does not relabel their
recorded `awaiting_review` state as new acceptance.

| Identity | Fixed source |
| --- | --- |
| Korda before main | `771bc77cbd68d3f932b99ed2497c0697bbba5f02` |
| Korda complete tree | `ddc4ec36cdade1749127fe5d50cbbf218b2878e6` |
| Starting Plan main | `bc1956936ee77a997a016856c97def6aabc0bbc6` |
| Starting Plan tree | `3dda25b1c0fd6ecb799d3c7359c68ef604b8f9d8` |
| Branch | `task/DB-Perf-01-linux` |
| Product worktree | `/workspace/scratch/b94e2a0e0c3f/Korda-DB-Perf-01-linux` |
| Plan worktree | `/workspace/scratch/b94e2a0e0c3f/Plan-DB-Perf-01-linux` |

At the initial remote check there was no existing DB-Perf-01 branch, PR or handoff.
Re-read live branch/PR state before publishing or resuming; this statement does
not predict the containing checkpoint's eventual commit, PR or CI.

## Recovery on 2026-11-24: allocation accounting

The owner confirmed the intended accounting: steady-state framework overhead
targets 0 B; required business results do not. DTOs, lists, result arrays,
strings and typed JSON outputs remain business allocation even when Korda's
generated mapper constructs them. Keep all of them in the end-to-end process
total. Temporary buffers, discarded growth arrays, boxing, copies, async/wait
objects and ownership machinery remain framework costs. Unresolved attribution
is not silently assigned to either side.

Report process-wide Gen0/Gen1/Gen2 counts separately from this object/byte
attribution. Collection events concern the shared heap and cannot be divided
mechanically into business and framework GC counts. Final reports must reconcile
raw bytes with business, framework, other attributed and unattributed bytes;
they must not require business 0 B or infer framework 0 B from no collections,
rounded averages or subtraction of an unrelated control.

At recovery, the latest local Korda checkpoint was `c6f41fb` and Plan was
`f6a8e78`, with additional uncommitted production/campaign work and the
seventeenth evidence checkpoint. These are recovery identities, not a frozen
final candidate or claims that all local changes were published. Preserve both
existing workspaces, failed attempts and the explicit local-only historical
helper disclosures. The original baseline remains `771bc77...`; acceptance
remains in progress, with **0/8 accepted long segments**.

A read-only recovery check executed
`python3 tools/verify_db_perf.py --korda-source /workspace/scratch/b94e2a0e0c3f/Korda-DB-Perf-01-linux --archives /workspace/scratch/b94e2a0e0c3f/baseline-artifacts`
successfully before these documentation updates. It verified 2,180 losslessly
compressed original records, the original candidate archives, 93 original and
5,346 supplemental source references against actual local Git bytes, five
compressed source inventories and 55 negative controls. No pending referenced
source remained in that scope. Separately disclosed local-only historical
helpers are not thereby made public or counted as fixed source references. This
was record verification only: it ran no new database workload, did not execute
the optional frozen-history gate, and grants no final-package or long-test
credit. Later checkpoints must retain their own counts and source identities.

## Latest persisted observations and resume boundary

Korda's normal two-parent merge
[`a245f843a0d296e28dcaa075300b3a90525cd242`](https://github.com/IzuSharp/Korda/commit/a245f843a0d296e28dcaa075300b3a90525cd242)
has tree `8d9a11fe758b7b0362c920a406f58f6cffe1332e` and parents
`1364b92282105bb45a71bb4f807b4b43b1bde809` and
`4f945fb8a4652eb71efa66e8a67e8b381dc2d089`. The GitHub Git-data response and local
objects were checked. Both histories and their raw evidence are preserved.
This is an intermediate merge, not the final performance candidate. Its actual
[CI 45400646996](https://github.com/IzuSharp/Korda/actions/runs/45400646996)
passed the affected Linux, package, API, AOT and required checks. Subsequent
Snapshot/Fetch work and the cgroup observer have separately fixed intermediate
objects; the final combined package and campaign are still pending.

The 368 previously pending historical source references now bind by actual
`git show` byte/hash checks to historical ancestor `1364b922...`, tree
`7604dd0893b476fa0fe65c8e00a4609a811b23cc`. All 138 unique archive paths match.
The eleven references that already used earlier published sources remain intact.
These bindings identify reproduction inputs only; they do not promote that
ancestor to the final canonical package or campaign source.

Concurrent Actions run
[45393596205](https://github.com/IzuSharp/Korda/actions/runs/45393596205) failed in
PostgreSQL dataset initialization; smoke, calibration and all eight long steps
were skipped. It earns no long credit. Both dataset initializers used transaction
outcome before the required DisposeAsync retirement join and then issued DDL;
the setup correction is retained in the normal merge. The chosen formal campaign
is `benchmarks/db-perf`. The second automatic workflow is preserved byte-for-byte
under `benchmarks/Database/campaign/archived-workflows`; it no longer supplies a
second automatic long-run trigger. Different 36/35-case contracts, datasets and
arrival models are not combined into one comparison.

Plan's new lossless evidence format now rejects missing gzip identities,
duplicate paths/origins and missing source inventories. The earlier v3 gate
verified 989 compressed originals and 37 negative cases before the historical
source bindings; its raw pending counts remain unchanged. The v4 gate verified
1,310 compressed originals and 39 negative cases, with all 93 original and 904
supplemental source references fixed. Independent review found no remaining
blocker. After adding the two controller commit receipts and seven fixed source
references, the actual v5 gate verified 1,312 originals and 911 supplemental
references with the same 39 negative cases. These are record-integrity results,
not database/performance acceptance or a prediction of the containing commit's CI.
The v6 gate then verified 1,378 originals and 1,540 supplemental references,
all fixed, after the twelfth checkpoint. Its exact raw output is retained with
the thirteenth checkpoint; later checkpoint counts do not rewrite that output.
The v7/v8 gates respectively verified 1,522/1,525 compressed originals and the
same 2,798 fixed supplemental references, with 39 negative cases. Their actual
stdout/receipts are retained in the fourteenth checkpoint. Large authored source
inventories may now use lossless gzip with compressed and original hashes/lengths;
this representation changes no source values or measurement bytes. Exactly one
inventory is required, and compressed metadata is not counted as an extra raw run.
The exact Plan-owned `35b22ae3...` verifier used by v7/v8 is retained in the
`verifier-snapshots/index.json` (verified locally; publication pending). It is not Korda
implementation and is not the active CI script. This preserves its original
source identity while skipping only unpublished large author-index formatting
trees in the eventual remote publication chain; old raw receipts remain intact.

The previously published Plan checkpoint is
`05bbd07dfc4b503eaf2596188dca53414711e5b6`, tree
`aeeeacaed44c19cf13e7a99675aaaf5d005fedb9`, with normal parent
`ba380202e7b36cbfe8dcd4bc2cfa0afe86048d92`. [Plan PR32](https://github.com/IzuSharp/Plan/pull/32)
is open and draft. Its actual
[paired-integrity job](https://github.com/IzuSharp/Plan/actions/runs/45392377806/job/138439174420)
passed for that exact HEAD; this does not predict this newer record's future CI.
The `checkpoints/iterations-04-09-v1/plan-pr-status-observed.json` (verified locally; publication pending)
retains the source URLs, HEAD and check result. No merge is claimed.

Read the `checkpoints/iterations-04-09-v1/README.md` (verified locally; publication pending)
and `checkpoints/iteration-10-v1/README.md` (verified locally; publication pending),
then the `checkpoints/merge-and-iteration-11-v1/README.md` (verified locally; publication pending)
and `checkpoints/iteration-12-and-provenance-v1/README.md` (verified locally; publication pending)
and `checkpoints/iteration-13-v1/README.md` (verified locally; publication pending),
then `checkpoints/iteration-14-v1/README.md` (verified locally; publication pending)
and `checkpoints/iteration-15-v1/README.md` (verified locally; publication pending)
before rebuilding or repeating measurements. These checkpoints keep lossless compressed raw
files, exact original hashes/counts, failed attempts, command/build receipts and
Korda-only source references. The gate decompresses and verifies every original
byte stream. The original source-location correction and all concurrent remote
evidence remain intact.

The fourteenth source object is `5b076164e73b82412db938fdeffe69db1655f4db`
(tree `4787f7b678e3ed34fd5e26eb60c4c8b4ce65cc41`); its historical helper/archive
object is `fc64ee1663667a84f1939e69cd13442e5160cf05`
(tree `8db66ecd6ba2bf58fab58516e3f1915682ce59d8`). The unchanged public Fluent
FetchProbe measured both databases, three fresh processes per version/provider.
Complete 256-row allocation falls about 40.72%; common refill is 2,256→1,104 B,
while the batch lease grows 72→80 B. All raw totals, positive windows and the
original SQL_ASCII correctness-fixture failure remain. This is a local
source-project allocation result; final PackageReference/timing remains pending.
The fifteenth private-Move source object is
`4a0dbffce55053d967874d5ba6962c95236f1c79`, tree
`013363fde2b8d05bc7da56b6d670c94095b12d95`; its archive object is
`06f0de33397fd43f6fd377cfcd9c27a2163ec165`, tree
`bbb4d3108be2c75b0ad103313632b7a7c6e94f59`. It explicitly reuses the fourteenth
AFTER six-process baseline and adds six fresh AFTER processes. Full 256-row
query allocation falls another 10.59%, while refill remains about 944 B and
the lease remains 80 B/batch. The runtime cache cold/miss/thread-growth/unconsumed
and idle-retention paths remain unmeasured. Read its exact build/consumer source,
raw data and ownership tests before continuing the next internal completion
experiment. These intermediate objects are not final package/campaign acceptance.

The fourth public SQLite PackageReference AOT comparison has 30 real read-only
query processes and two empty controls. All completed 200 operations / 6,400 rows
per process with zero failures and tracked owner drain. Median whole-process
end-to-end allocation reductions are 22.24% numeric, 25.32% text, 15.17% money,
24.85% JSON and 28.33% wide DTO. These are intermediate-package allocation
observations; framework-only attribution and qualified timing remain unproven.

Prepared parameter/projection metadata reuse has repeatable positive allocation
reductions without a zero claim. The JSON/configured-codec isolated validation
windows record exact raw zero at their stated scalar boundaries. The ninth owned
numeric wire validation records raw 0 B across 36 windows / 9,216 parses; fetch,
copy, lease, mapping and full-query costs are excluded. The tenth control parser
remains allocating: 1,296→48 B/normal control and 1,360→80 B/provider control.
Normal public session.Cleanup observations are 1,544→296.0539556 B/op on SQLite
and 1,544→296.0357333 B/op on PostgreSQL, including all first-window excess.
They use a source-referenced AOT test assembly, not the final independently packed
consumer. The complete per-window totals, independent reviews and scope limits
are in the linked checkpoints.

The PostgreSQL recovery failure was a harness cleanup-order violation: a next read
was started after transaction outcome but before DisposeAsync retirement. Both
managed routes now use the same public cleanup contract. Three exact original
Korda package repetitions complete with zero business failures, retained warm
owners and final drain. Earlier failures remain invalid lifecycle-order records,
not evidence of a product defect or valid timing. Native v7 recovery has no
between-phase idle and one final idle; retained v6 commands actually used idle=0.

Production changes through the eleventh isolated optimization are locally measured
and reviewed, including the merged four-module AOT check. The eleventh Cleanup
boundary retains 79,930,336→23,772,600 B on SQLite and 79,931,288→23,770,304 B
on PostgreSQL, each over 270,000 operations. Roughly 88 B/operation remains.
The twelfth Fetch-delegate checkpoint retains complete SQLite queries, including
the +16.108796 B/empty-query (+0.3290%) regression and −750.921296 B/256-row-query
reduction. Its refill modal difference is the observed 96 B, correcting the old
128 B estimate; all raw variation and controls remain. The candidate passed real
Host correctness on both providers. These source-project observations do not
establish final independent-package or long-test acceptance. Its 620 actual build
inputs match fixed intermediate Git bytes; seven historical helpers/recovered
validator inputs bind to archive object `9d9d9cdbb98717df41e6b4d396dbdf831beb3c1b`.
Final combined source/package identities still need to be
bound before the dedicated campaign. The campaign request stays disabled at this
checkpoint. The earlier frozen controller has 26 passing short checks and independent
review; the actual `check.py` invocation also verified 294 archived-source
references and published/executed the Native AOT scheduler tests. Its immutable
receipt/log are retained under the fourth–ninth checkpoint. The earlier wrapper
attempt pointed at a nonexistent build.py and failed before tests; its empty
directory supplies no execution credit.

The thirteenth default-frame optimization has a separate final v3 comparison:
default public Begin/rollback/disposal falls by 27.75–30.37% in whole-process
steady allocation on both providers at C1/C4, while remaining about 3.37–3.67
KB/transaction. Explicit reused-options controls, 24 cold observations and 72
array/empty controls remain separate. All 144 final steady windows save immediate
API-completion and subsequent physical-drain counters; settling adds raw 0 B in
this run. The original v1 failure is still unclassified, and v2/100-window runs
remain diagnostic only. Final source object `e7d4d293...` and archive object
`b7e00c37...` identify those exact bytes without relabeling the dirty builds.

Optimization is still in progress. The first native-to-managed batch copy and
internal lease remain measured allocation candidates; their presence is not a
proof that they are required by the public API. A separate fourteenth borrowing
experiment is underway with its own before identity and lifetime/escape checks.
It has no acceptance credit here, and the current batch does not claim that
remaining hotspots are exhausted.

The subsequent controller cgroup v1 candidate has 34 passing short tests and an
independent source/receipt review without a remaining blocker. It
creates only a new child of the existing cgroup, enters before PostgreSQL exec,
records cumulative user/system CPU including exited backends, and retains
process-tree and wait4 cross-checks. It does not change ancestor controllers,
limits or permissions. Its seven exact sources now bind to intermediate Git
object `7673f2083b007965e7bb60e4882511ed56969ae7`, tree
`2eef29df0aab00a5f78a46bae20caa498d24a566`. Final candidate publication and real VM admission are
separate outstanding requirements at this checkpoint; this local test is not
evidence that a real cgroup was successfully admitted.

The final-allocation validator now separates package and native producer commits
and verifies the complete native input set at both real revisions. The retained
four old-package checks and twelve synthetic controls passed; an earlier missing
Git-object rejection remains. Fetch both source commits before reproduction.
This is provenance verification, not native incompatibility or final package
performance acceptance. The exact older validator bytes were recovered and hash
matched; they are never relabeled as the newer validator version.

The planned ordinary timing cells now enforce quota/throttle/steal/CPU quality
separately from the workload SLO. Short dynamic/prepared projections and complete
8,192-row streams use all four routes and both databases. Capacity refinement is
bounded to three midpoint samples per selected concurrency, preserving failures
and explicit brackets. Same-process source/session/worker recovery replaces the
redundant future fresh-process recovery pair; historical evidence is retained.
All allocator profiling stays separate from ordinary timing. The configured
single-attempt schedule is 18,534 seconds including idle; hard limits are
85-minute preflight, 340-minute controller and 360-minute hosted job. Overhead
and explicitly reviewed retries consume the remaining budget, never shorten the
eight required 1,800-second segments. Dedicated admission and long credit remain
unestablished: **0/8, 0 effective accepted seconds**.

## Concurrent checkpoint reconciled without replacement

**Publication recovery:** automatic approval review rejected new full
implementation/controller source snapshots being uploaded to Plan. The
[source-location correction](source-scope-correction/README.md) replaces only
93 locally added source copies with exact Korda source references. Raw measured
files and all pre-existing remote evidence remain unchanged. The complete local
snapshot is preserved at `b279f42674eb3e8db48b423482f38c6b955c4d82`. The original
82 pending references to 45 immutable archive inputs have since been verified
against historical published ancestor `1364b922...`, as described above. Do not
publish the superseded full-source Plan tree or label these historical identities
as the final package candidate.

The later read found Plan branch commit
`ba380202e7b36cbfe8dcd4bc2cfa0afe86048d92` (tree
`cf94ab3a81351271a7dc0c7eaf49ea3acdbd2a02`) from a separate execution under
`/workspace/scratch/754bc732518e`. It contains real public-package allocation,
native/ORM capability and review records. This checkpoint merges that work
additively with local recovery commits `5a7525437d17000952d553d662920582df6469a1`
and `509e1b7c58172834b02795c7329e841a5b6effb0`; it does not overwrite the remote
branch or edit the other active worktree. The three original overlapping reports
and their provenance are retained under
[reconciled-remote/ba380202](reconciled-remote/ba380202/README.md). Both `preflight/`
and `checkpoints/` layouts remain intact.

A new [read-only reconciliation](reconciled-remote/ba380202/public-preflight-verification.json)
checked all twelve original raw result files, actual packages/executables/native
images, unchanged consumer sources, complete package-member hashes, 386 producer
inputs, cumulative allocation/GC counters and tracked ownership drain. These
executions were recovered from the concurrent checkpoint; this executor did not
rerun them. The original before packages match the fixed main. The after package
is **`0.1.0-perf-lazy.1` at `28110ee03391831c737a54204730730a01b77a34`**, not the
combined `ci.1` candidate or any later final candidate.

For each provider, those three after processes contain 384 synchronous numeric
in-batch windows / 48,768 rows with exactly **0 raw allocated bytes**. The matching
before windows total 4,291,584 B / 48,768 rows, exactly 88 B/row. No control bytes
were subtracted. The acceptance inventory now retains this narrowly bounded
public path as a historical candidate result. Query construction, binding, first
fetch, refill, final false, disposal, connection acquisition/return, concurrency,
cancellation and exceptions are excluded from that zero claim. Complete-query
and refill totals remain positive, with their exact framework fraction unproven;
see the [original comparison](preflight/korda-allocation-after-lazy-join/comparison.md).
No elapsed-time comparison from this shared sandbox is qualified.

Korda [PR37](https://github.com/IzuSharp/Korda/pull/37) and the compatible concurrent
preflight commit `f9f0d6438feb9b29a9fdac05f3c10bdc86ed5d85` now exist. Re-read live
heads before any write. A further owned-batch-copy experiment is under evaluation;
the final candidate stays unset until all retained improvements and their final
package identities are complete. The owned-copy experiment has since passed its
scoped checks as detailed in the latest checkpoint above. The eight qualifying
long segments remain **0/8**.

## Expanded correctness and campaign implementation checkpoint

The following observations extend the earlier five/30-read-case checkpoints; the
older receipts below remain unchanged historical observations. **Long credit is
still 0/8.** Final optimized-package comparison, qualified host admission, merge,
preview and public-package verification are not established by this checkpoint.

The [managed final correctness index](checkpoints/managed-final-v1/summary.json)
binds the original-package Korda and independent Dapper.AOT consumers to exact
source, restore graph, executable and raw result hashes. Both databases and both
managed routes completed all 35 cases in dynamic and prepared modes: **35
successful operations, 854 consumed rows, zero failures per pass**. Each also
completed the C4 mixed-write correctness probe with 36 successes and 276 rows.
These counts are correctness evidence, not stable throughput estimates. Korda's
source/project bytes match across providers, as do Dapper's.

The shared workload is `queries-v3.json`, SHA-256
`76443b1c88bf011f57b3c9819dc85a8bedb5376121d3ef2670304f96b6d2aae2`.
It adds committed read/write transactions with restoration, rollback, partial
updates, an expected stale concurrency exception, and early enumeration end.
All write paths check the complete persisted original row after restoration or
rollback. PostgreSQL normal35 observed 59 SQL executions and 276 protocol
submissions for Korda; SQLite observed 61 SQL executions and no network protocol
submissions. These counters are not physical network round trips.

PostgreSQL final managed binaries passed genuinely suspended cancellation followed
by connection reuse, pre-cancellation and overlapping optimistic conflict checks.
SQLite Korda's cancellation/conflict verifier is explicitly bound to an earlier
v5 executable with the same verifier, while the final v6 normal35 and mixed-write
probes ran independently. Dapper/Microsoft.Data.Sqlite active cancellation is
**unsupported in the observed path**: the real recursive database computation
completed synchronously despite timed cancellation. Its prior failed probe and
the final explicit unsupported receipt are retained. Dapper's ownership check
covers application connections and cleared pools, not uninstrumented provider
internals. Korda's tracked six native owner categories returned to zero.

Direct native [SQLite](checkpoints/native35-sqlite-v3/summary.json) and
[PostgreSQL](checkpoints/native35-postgresql-v3/summary.json) each passed three
35-case correctness processes plus a C4 lifecycle process. Each normal35 pass
consumed 854 rows in 35 successful operations with 57 business SQL statements;
each lifecycle process completed 100 operations and 280 rows. Executable SHA-256
is `055539a43c11a6e41a92ee0f54fdd1ac3245b7f2ce13f2921124d53dfc53e96d`.
Prepared native reuse with ordinary complete driver drain is the primary
comparison contract. Per-operation preparation/product confirmation remain
separate attribution layers; they do not exactly reproduce Korda's internal
transaction control SQL. Native whole-heap allocation/free counters and peak
remain uninstrumented in these binaries.

Independent review found a remaining workload gap: this frozen mixed35 contract
fully consumes at most 53 rows per operation, usually 32; early-stop consumes only
three of 1,024 requested rows. It does **not** prove a fully consumed large-result
or heavy materialization lane. Add a separate validated large-stream contract
instead of relabeling these results.

The [controller checkpoint](checkpoints/controller-review-v1/summary.json)
preserves 15 passing short tests, exact source snapshots, and independent source
review notes. Korda contains the manual-only hosted workflow and a disabled
request. Preparation binds four exact original/candidate artifacts and builds
external consumers in a separate job. Measurement reserves one Ubuntu 24.04 VM
for the eight sequential 30-minute segments, with a 360-minute job limit and
distinct upload checkpoints. No workflow activation or remote long execution is
claimed here.

Admission checks actual cgroup-v2 membership plus every visible ancestor's CPU
quota/throttle counters, disjoint client/server/observer affinity, VM boot/image
identity, idle load/steal and interleaved before noise. The kernel defines
[cpu.max on non-root groups and local bandwidth counters](https://docs.kernel.org/admin-guide/cgroup-v2.html#cpu-interface-files);
checking only the mount root could miss a limited descendant. Missing/hidden
ancestry, including this sandbox's unavailable `/sys`, cannot qualify. Resume
revalidates raw/source hashes and rejected admission. Failed attempts require an
explicit bounded retry with a retained reason; prior valid samples cannot be
replaced by preferred samples. Closed-loop service calibration is distinct from
the scheduled-rate SLO ladder. This historical controller snapshot's
overload/recovery commands used fresh processes. The latest implementation above
adds actual same-process source/session/worker recovery and removes the redundant
future fresh-process pair; the old snapshot and observations remain unchanged.

## Exact original candidate archives recovered

Fixed-main [CI45356659607](https://github.com/IzuSharp/Korda/actions/runs/45356659607)
built both original `0.1.0-preview.3` provider candidates. The parent downloaded
the actual artifacts; a separate read-only review rehashed each artifact ZIP,
each nupkg, every unsigned package member (41 PostgreSQL / 40 SQLite) and native
payload, and checked source_commit/source_tree and the exact member set. The
unchanged producer manifests and [archive review](baseline/archive-review.json)
are retained here. This was byte/provenance inspection, not new execution.

| Original candidate | nupkg SHA-256 | Native SHA-256 |
| --- | --- | --- |
| Korda.Database.PostgreSql 0.1.0-preview.3 | `458c115e12d65ca0719f542ea262aeb3347f5bc3269f99d5ba14f3e36c038e0f` | `73f725104fb1bee5fc86a9bc371e556ea8358ac3a2d774c4823185e6da8984c6` |
| Korda.Database.Sqlite 0.1.0-preview.3 | `584d46aa5b08b1e0af46a454ac9f41704c28fe502884017e856ad1b66ca53ef5` | `970a8868290cec37c353bbd8e48bb7bf4ef18cfa1da9e495fc06d7eb08d71d40` |

Local archives are under
`/workspace/scratch/b94e2a0e0c3f/baseline-artifacts/{postgresql,sqlite}/feed/`.
The original artifact ZIPs are beside those provider directories. Their artifact
IDs/digests are in [baseline.json](baseline.json); official expiry was
2026-12-08. These are unsigned original candidate archives from fixed main, not
downloaded NuGet-signed substitutes. Do not conflate artifact ZIP, nupkg,
individual native payload or signed public archive hashes.

The previous release jobs also succeeded for the same main:
[PostgreSQL public AOT](https://github.com/IzuSharp/Korda/actions/runs/45356659607/job/138320638625)
and [SQLite public AOT](https://github.com/IzuSharp/Korda/actions/runs/45356659607/job/138320638635).
They establish previous correctness/publication observations. They do not execute
the new benchmark consumer or provide DB-Perf allocation, latency or duration data.

## Recovered local tools and their limits

[Recovery observations](recovery-observations.json) retain original clean worktree
identities, actual old package rehashes and executable tool hashes/version output.
The former workspace `/workspace/scratch/82a414196324` still contains .NET
11.0.100, Clang 23.1.5, CMake 4.3.3, Ninja 1.13.2, PostgreSQL 18.0, pinned SQLite
and JSON sources, and the required .NET 11 Native AOT/Roslyn cache. The old local
`0.1.0-ci.1` archives match the same source tree but retain producer commit
`9aa0b909…`; they are recovery aids, not the selected before packages now that
the exact main archives have been recovered.

Use a task-specific environment and independent consumer directories. Do not
source the old serial-build launcher unchanged: it appends to the old task's
invocation log. Preserve telemetry opt-out and ordinary single-process compiler
settings when needed. Old logs include a genuine full-workspace formatter failure
from the sandbox's Unix socket restrictions; later unchanged GitHub CI passed.
Do not claim that historical CI removes a current local limitation or rerun a
denied action through a disguised launcher.

The sandbox is **not qualified for the dedicated long campaign**. Visible affinity
0–8 and `/proc` memory are not proof of exclusive cores, fixed quotas, client/
PostgreSQL service isolation or stable host identity. The observed `/sys` CPU and
cgroup quota files were absent. No dedicated admission or before-only noise study
is recorded, and repository CI uses ordinary hosted Linux jobs. Root-owned
environment investigation may qualify a suitable host later; until then no long
segment may receive acceptance credit.

A **single separate GitHub-hosted `ubuntu-24.04` campaign job** is a viable next
admission candidate. Lack of a self-hosted runner is not itself a blocker.
[GitHub's runner reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
describes a fresh VM per ordinary hosted job and the public Linux x64 resource
class; its [limits](https://docs.github.com/en/actions/reference/limits) permit up
to six hours per job. Build all exact package/consumer/native inputs in a separate
preparation job, then reserve one VM for the eight sequential segments. Record
guest CPU affinity, quotas, boot identity, image, disk and tool/binary hashes;
separate client, PostgreSQL and observer CPUs; admit measured idle/steal/noise and
monitor them continuously. This is VM exclusivity within the job, not a claim of
exclusive physical host cores. The proposed manual/opt-in workflow is still
being implemented and has not run. Ordinary PR CI remains short. Acceptance is
still 0/8 until actual admitted, matching observations are retained.

## Source findings and before diagnostics

The fixed baseline allocates a TaskCompletionSource on every
`TypedStream<T>.Enumerator.MoveNextAsync` call, copies each native batch into a
managed array, and copies again while parsing DbWire. Parameter-shape rebuilding,
validation-only UTF-8 strings, decimal re-encoding and async operation completion
owners are additional source candidates. See the inventory for exact pinned
paths and required controls; these are not measured saving estimates.

Actual isolated before diagnostics are now retained under
[checkpoints/before-internal](checkpoints/before-internal/summary.json): 62 original
JSON/log files and their byte hashes, 30 successful command records, three
interleaved independent processes per streaming lane, and the exact AOT binary
identities. The fixed production source diff was recorded empty before the
candidate edits began. In-batch advance records 23,063,040 raw allocated bytes for
262,080 measured rows in each repeat (88 B/row), with a separate matching control
of exactly zero raw bytes. Full synchronous internal stream operations record
24,584,456 bytes per 64 queries / 131,072 rows. Asynchronous internal stream totals
are 24,731,504 / 24,736,680 / 24,736,680 bytes, with 576 observed suspensions each;
the separate asynchronous driver control is 55,560 bytes per repeat. Do not
silently subtract control totals to assert exact framework attribution.

The [inventory summary](allocation-inventory.md) also preserves scalar lanes and
the exploratory scalar probe's first 672-byte empty-driver contamination. These
internal measurements establish a specific investigation baseline; they do not
complete normal public-provider, independent ORM, direct-native or dedicated
long-run acceptance. Candidate implementation is proceeding from these observed
hotspots; no final candidate improvement is yet accepted by this checkpoint.

The isolated lazy-join candidate has three retained repeats under
[after-lazy-join](checkpoints/after-lazy-join/summary.json): in-batch advance is
exactly 0 raw bytes for 262,080 measured rows per repeat, while full synchronous
stream work remains 13,013,944 bytes per 64 queries / 131,072 rows. The corresponding
before value was 24,584,456 bytes. All 46 deterministic join/disposal race assertions
passed. This is a bounded internal transport measurement, with stream creation,
fetch and disposal excluded from the zero-byte window; it does not establish
public-query or whole-framework zero allocation. A separate
[short regression execution](checkpoints/after-gate/summary.json) records 0 raw
bytes / 65,520 rows / 16 windows, with the same 46 race assertions and a preserved
build log. Source hashes and binaries distinguish these candidate builds.

The before AOT build's original stdout was observed in the execution transcript,
not redirected to a file. Its retained observed-build receipt states this limit
and labels the small Program.cs harness reconstruction. The untouched allocation
probe source and fixed-main TypedStream snapshot are hashed separately. The
[scalar-v2 checkpoint](checkpoints/before-scalar-v2/summary.json) preserves a
revised diagnostic setup and all nine zero-byte empty-driver windows. Its first
UTF-8 window still contains an extra 1,136 bytes; that result is retained without
normalization. Original v1 contamination remains visible.

Further scalar comparisons use an unchanged source-bound v3 probe, three
independent AOT processes and three windows of 100,000 calls per process:

| Internal validation lane | Before raw bytes / window | After UTF-8 change | After decimal change |
| --- | ---: | ---: | ---: |
| Empty driver | 0 | 0 | 0 |
| Strict UTF-8 | 8,000,000 | 0 | 0 |
| Canonical 96-bit decimal | 28,000,000 | 28,000,000 | 0 |
| Canonical decimal zero | 4,000,000 | 4,000,000 | 0 |
| Typed JSON validation | 28,000,000 | 15,200,000 | 15,200,000 |

Every corresponding window has the listed raw value; cumulative before/after
counters, GC counts, build logs and exact source snapshots are retained in
[before-scalar-v3](checkpoints/before-scalar-v3/summary.json),
[after-scalar-utf8-aot](checkpoints/after-scalar-utf8-aot/summary.json) and
[after-scalar-decimal-aot](checkpoints/after-scalar-decimal-aot/summary.json).
These are isolated validation paths, not complete provider operations. JSON
remained allocating at this third-change snapshot; the later sixth change has
its own source/binary/raw record above. Strict malformed UTF-8 and canonical/noncanonical decimal
correctness checks passed in the corresponding actual AOT binaries. The initial
UTF-8 launch omitted PublishAot and exited before its managed body because the
apphost could not find a runtime; its failure log has zero measurement credit.

## Real public and native correctness checkpoints

The original fixed-main packages have now executed through normal out-of-tree
PackageReference Native AOT applications on both real databases. The
[five-projection smoke receipts](checkpoints/before-public-smoke/summary.json)
bind packages, generated projection sources, executables and loaded native bytes.
The subsequent ten short cells per database (five projections × dynamic/prepared)
completed 1,000 operations and consumed 32,000 rows on each provider, with no
failures and all tracked owners at zero after drain. Their raw end-to-end bytes
are retained in [SQLite](checkpoints/sqlite-before-short/summary.json) and
[PostgreSQL](checkpoints/postgresql-before-short/summary.json). Framework-only
attribution remains unproven. These v1 applications are not silently interchangeable
with later expanded consumers.

The expanded [SQLite v2 read workload](checkpoints/sqlite-before-public-v2/summary.json)
completed all 30 query scenarios once in each construction mode, 840 consumed rows
per pass, with zero failures and owners returned to zero. It adds joins,
aggregations/HAVING, NULL cases, cursor/offset pagination, relationships,
subqueries, CTEs, windows and set operations. Raw SQL in prepared mode reuses only
the SqlCommand object; relation loading has no prepared overload. Transaction
writes, conflicts, rollback, cancellation and early enumeration remain separate
obligations. PostgreSQL's expanded workload was still being investigated when
this checkpoint was written; do not infer its success from SQLite.

Direct C++20 with Clang 23.1.5 has completed 13 correctness processes per database:
the same five projections in both construction modes and three separately labeled
physical-preparation/confirmation layers. The exact build receipt and raw
[SQLite](checkpoints/native-correctness-sqlite/summary.json) and
[PostgreSQL](checkpoints/native-correctness-postgresql/summary.json) observations
are retained. All consumed the complete expected results and drained tracked
owners. These initial native runs did not instrument full allocation/free calls;
glibc snapshots and SQLite allocator high-water values are narrower observations.
Later separate allocator diagnostics are recorded above with their public-allocator
coverage limits, without relabeling these older runs.
PostgreSQL protocol submission counts are not physical network round trips.

Dapper.AOT 1.1.0 / Dapper 2.1.100 has passed minimal real Native AOT buffered and
32-row streaming queries with [Microsoft.Data.Sqlite.Core 11.0.0](checkpoints/dapper-sqlite-minimal/summary.json)
and [Npgsql 11.0.0](checkpoints/dapper-postgresql-minimal/summary.json). SQLite used
the exact comparator's pinned SQLite 3.51.3 shared image. This proves basic real
ORM support, not the full comparison workload. The first SQLite probes aborted
while the workspace had zero free bytes; their empty logs and later successful
argv observations are preserved. Only reproducible build intermediates and
checksum-verified compressed tool downloads were removed to recover space;
[cleanup provenance](tool-download-cache-cleanup.json) records the latter.

These are correctness and exploratory diagnostics. No four-column comparative
campaign, admitted fixed offered load, saturation/recovery study, or qualified
long segment is complete.

Public Task-returning genuinely asynchronous calls expose independently
retainable non-resettable completion objects. Bounded reuse cannot silently
change those semantics. A measured allocation-free row path may be achievable
while per-query/refill/transaction costs remain. Report the latter as framework
bytes and unmet or unproven paths instead of claiming whole-framework 0 GC.

## Sixteenth allocation checkpoint and publication limits

`checkpoints/iteration-16-v1/files.json` (verified locally; publication pending) preserves 136 original
records and 437 fixed source references: the four actual builds share 339 source,
configuration and test-driver inputs; 95 native fixture inputs are independently
matched; two previously published auxiliary inputs and the exact old observer
complete the referenced scope. The candidate source object is
`1361e5e5faef21b4dc43b60281aac76d6b7f634f`, tree
`1379b3cf4f8c4203c15db55cc8f2d2399a767498`. The actual measured build remains
`bf5a1cd8e5d0f87ca5ab6da79f89a5c1f4be2804`, sourceDirty=true, with Host ELF
`943166e44d2cafcfe492afb2a47b695ca5376f72ca7cbcc0999fc72cb5f2c25e`.
These identities have separate purposes and are not relabeled.

Before is exactly the six original iteration15 AFTER processes. All 38 preserved
file identities in its reuse receipt were rehashed; no new before process is
credited. After adds three independent processes per provider. Over 3,456 full
256-row queries per provider, SQLite cumulative allocation falls from
42,092,720 to 33,461,184 B (−20.5060%); PostgreSQL falls from 42,097,456 to
33,502,536 B (−20.4167%). Full queries still cost roughly 9,682/9,694 B each.
Across 384 refills, raw bytes fall from 362,320/362,496 to exactly 261,120 B in
each provider: **680 B per refill remains**. Each provider retains raw 0 B for
11,904 synchronous in-batch rows, a narrower boundary. No control subtraction,
CPU/latency comparison or final package acceptance is inferred.

The private single-consumption completion bridge publishes only after actual
retirement; ordinary public Task behavior retains early outcome and later cleanup.
Interop AOT passed 471 assertions with all tracked owners released; the original
result-before-native-quiet test and cancellation semantics remain covered. Four
isolated quarantine probes retain uncertain operations as pending. Streaming and
two-provider Host AOT correctness, mapping barriers and ownership gates passed.
The first Streaming build helper failed while constructing metadata after a
successful compiler exit; the original incomplete receipt and helper identity,
then the same-ELF repair, remain separate. The independent reader's initial
wrong-key failure is also preserved as a verification failure, not a database
rerun or product failure.

### Explicit historical-helper publication gap

Automatic approval review rejected the proposed 16-file Korda historical archive
because it included source/scripts/patches, workspace paths and potentially
nonpublic provenance outside the reviewer's understood publication scope. The
full rejection response and scope-exclusion receipt are retained. The rejected
files were not retransmitted, split into blobs, moved into Plan, or included in
subsequent remote trees. Local `fac34e2...` history and staging remain recovery
inputs and are **not claimed public**.

The actual old observer is already available byte-for-byte at
`4a0dbffce55053d967874d5ba6962c95236f1c79:benchmarks/db-perf/run.py`, SHA
`1290fbca3845816fad3ab511282e7938b8c1cadc6d48c9ab8a90c955d1df839b`.
The `checkpoints/iteration-16-v1/read-only-verification.json` (verified locally; publication pending)
separately records **17 historical origins / 14 unique helper or patch files** as
`local_only_unpublished`, with exact SHA, byte length and role. Their full text
has no claimed fixed public source. The 437 fixed-reference count describes the
published build/observer scope and does not hide these separate missing texts.
Original executable argv, source/configuration inventory, consumer closure and
raw output remain the public reproduction inputs. Replaying those commands is
not the same claim as publishing every original temporary helper.

Plan's accepted-state conditions are unchanged. The task and this checkpoint
remain in progress, final reproduction review remains pending, and no full
historical-helper publication or final-candidate credit is granted. Normal CI
[45424519067](https://github.com/IzuSharp/Korda/actions/runs/45424519067) was
independently read back: 11 successful jobs including Verify, Linux and both
providers, plus two rule-based skips. It is an intermediate iteration15/UTF8-fix
candidate. The earlier SQL_ASCII Unicode failure remains retained; neither CI
result is relabeled as the final package or any long test.

## Seventeenth allocation checkpoint

`checkpoints/iteration-17-v1/files.json` (verified locally; publication pending) reuses the six original
iteration16 AFTER processes as before and preserves six new after processes.
The final passing 341-file source/configuration inventory matches safe source
object `fd3ffb45c4a84ce14b34477e0c90dc548514d1d1`, tree
`9f8049d8fd96deef535d76a84e8094f5bc2a34b8`. The actual after build remains local
`fac34e2fc0e5b92fa15c7f5ed26ecf4d47f1bc07`, sourceDirty=true; its Host ELF is
`30d237e026089915524b9bea3f1678b8b35bb1d21a3b9c9e2bea663839a9eb2a`.
The safe remote source does not include the rejected historical archive or claim
that local build producer has been published.

Each enumerator now reuses one internal inactive row lease between batches,
releasing the previous owner before attaching the next. Every batch still
validates wire identity, ranges and limits. The first lease still costs 80 B.
A separate precreated-owner/lease Attach-read-Dispose gate measures exactly zero
all-thread bytes across three windows, 192 batches and 24,576 rows. It excludes
initial lease/owner/input creation and actual provider fetch. Real database
refills remain **600 B per batch**, exactly 230,400 B over 384 batches in each
provider, down from 261,120 B / 680 B per batch. The unchanged in-batch boundary
still records zero cumulative bytes for 11,904 rows per provider/version.

Across 3,456 complete 256-row queries, SQLite changes from 33,461,184 to
31,239,432 B (−6.6398%); PostgreSQL changes from 33,502,536 to 31,282,248 B
(−6.6272%). Full-query costs remain approximately 9,039/9,052 B. SQLite empty
queries increase from 14,683,384 to 14,738,000 B, **+15.803241 B/query /
+0.371958%**, without an established allocation attribution; this is not silently
called noise or removed from the comparison. Gen0 counts for the 256-row window
increase 6→9 and 7→9 despite the smaller allocated totals. Original counts,
controls and GC data are all retained.

The first new Streaming fixture failed at `DbWire.Encode` with `Int64 width`
after successful AOT compilation. A separate ordinary dotnet DLL/JIT diagnostic
explains the nullable-memory expression; it is not Native AOT acceptance. Only
the new test fixture was corrected to explicit if/else plus width/null checks.
Final v2 AOT passed 373 new checks and the new zero gate, existing ownership/race
gates, full Streaming two-provider correctness and Host mapper barriers. The
original source review's overstatement about the earlier conditional correction
is explicitly corrected by its retained addendum.

Four build archives contain two distinct 341-file manifests. All final v2
members match existing public sources; the failed v1 manifest has one unpublished
historical `RowLeaseReuseChecks.cs` variant. The fixed-reference inventory has
683 entries, with **19 local-only historical origins / 16 unique texts** disclosed
separately, including the failed fixture, temporary helpers and JIT-only inputs.
No new full historical source archive was created or uploaded. The original
failure, JIT diagnostic, final AOT and independent read-only verification retain
their separate identities and scopes. This remains an intermediate source-project
allocation result, not final PackageReference, CPU, throughput, p99 or long-run
acceptance. Long credit stays **0/8**.

## SQL and execution-plan diagnostic checkpoint

The separate `checkpoints/query-plan-diagnostics-v1/files.json` (verified locally; publication pending)
preserves 74 exact original records and six fixed Korda source references. Its
successful helper sources and 35-case manifest bind to
`cc8af8cd1060e68b125951453412eaab8f952a6f`; the actual old successful controller
and the preserved intermediate collector bind to archive commit
`0a878344c1d1311509dc97aec3f756b3e3709eec`, tree
`e9038e4683a0cd7bccb3a57dab26a909ae3e854a`. All six source byte sequences and 32
artifact references in the author's final validation index were rehashed without
running another database process.

The direct C++, original Korda package and independent Dapper.AOT routes each
actually completed PostgreSQL plan diagnostics with 350 warmup operations and
35 measured operations. The 35 semantic cases expand to 57 SQL/control legs;
the helper required 627 business-statement observations and 539 plan observations
including warmup. Exact SQL and ordered parameter values were checked against
actual server JSON; extra startup/provider statements remain visible. Actual
statement/plan counts were 666/578 for direct C++, 659/569 for Korda before and
633/548 for the independent route. The locked PostgreSQL 18.0 auto_explain build
verified 1,663 installed inputs and produced an 18,416-byte library with SHA-256
`b9d4203500d494928dbeaafdf167ed131a141f6975270a03675ea4e70f67d82e`.
It is enabled only for this separate diagnostic scope. These records do not
supply final optimized-package, generic/custom plan-count or server parameter-OID
acceptance.

SQLite used the exact 3.51.3 shared engine already fixed for the comparison.
Each of the same three SQL contracts produced 49 read-only EQP observations and
retained eight nonexecuted control legs with typed bindings. This is replay of
the SQL contract; it does not observe the actual ORM's prepared statement cache.
The final helper gate passed 18 synthetic integrity tests. Initial SHOW failure,
empty-WAL behavior, startup multi-statement parsing failures and the intermediate
collector are preserved. Full source for the earliest SQLite/WAL collector,
early synthetic v1/v2 and the initial SHOW-failure controller was not archived;
those attempts remain failed or incompletely source-bound diagnostics and are
never assigned the final helper's source identity.

The checkpoint also preserves the actual Plan v10 integrity gate at source
`024babc2274250b3ab85d9109c0382bc51a9b632ca8e9c315cc9a66edf3537d4`:
1,835 compressed originals, 93 original plus 4,220 supplemental fixed source
references, three compressed authored inventories and 55 negative cases. Its
counts precede this newly added checkpoint and are not rewritten. Formal
four-route comparison, actual dedicated-VM admission, final package consumption
and all eight long segments remain pending, with **0/8** long credit.

## Eighteenth allocation checkpoint

`checkpoints/iteration-18-v1/files.json` (verified locally; publication pending) preserves 117 exact original
records, including the six new AFTER processes, the initial Host compiler failure,
the actual passing AOT gates, two source reviews, the independent raw-count audit,
and the source-free publication API responses. The original iteration17 AFTER
processes remain this iteration's BEFORE; all 40 reused file identities were
rechecked without rerunning or relabeling those processes. Their original producer
is `fac34e2fc0e5b92fa15c7f5ed26ecf4d47f1bc07`, sourceDirty=true, and their original
phase remains `after`.

The measured Host v2 build remains `c6f41fb5007639ddf16612ce788a1e5df77430e9`,
sourceDirty=true, with ELF
`a450ecb2c13eb1b0d02c019c3ec1338d4bb420ced0f2390f30e3c017c921cabd` and 342-file
manifest `2e5c6abf39e69dc7a4a10be537f675233ae11b1cbabf68f8c4239e927b644742`.
Every final manifest member now has an exact byte match at the published Korda
source commit [`cf7c080aeef01e3b012d0564e6f930b77e9c697f`](https://github.com/IzuSharp/Korda/commit/cf7c080aeef01e3b012d0564e6f930b77e9c697f),
tree `74a76bc5d00671a48221d0ed19002a3ffffd319f`. This later source binding does not
change the original local build identity or claim an independently packed result.
The two loaded native libraries and the measured Fetch probe remain unchanged.

The private retired-fetch bridge now transfers a fresh exclusive OperationHandle
directly, removing the redundant NativeResourceOwner and its gate. The ordinary
public Task path keeps its owner. Logical controls still enclose physical
SafeHandle AddRef/Release, physical retirement precedes private result publication,
and cancellation and indeterminate native obligations retain their isolation.
There is no new pool, cache, public API, C ABI or native-image change.

The stable actual-refill window changes from **230,400 to 196,608 B over 384
refills per provider: 600 to 512 B/refill, an observed reduction of 88 B**.
Every after refill window is exactly 512 B. The separate synchronous in-batch
window remains exactly zero raw all-process bytes over 384 windows / 11,904 rows
per provider/version. Neither excludes a positive refill cost from a whole-query
zero claim: complete queries and refills remain allocating.

| Provider | Rows/query | Before raw B | After raw B | Queries | Before B/query | After B/query |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SQLite | 0 | 14,738,000 | 14,467,976 | 3,456 | 4,264.467593 | 4,186.335648 |
| SQLite | 1 | 16,760,608 | 16,153,400 | 3,456 | 4,849.712963 | 4,674.016204 |
| SQLite | 256 | 31,239,432 | 28,552,288 | 3,456 | 9,039.187500 | 8,261.657407 |
| PostgreSQL | 0 | 14,703,200 | 14,413,184 | 3,456 | 4,254.398148 | 4,170.481481 |
| PostgreSQL | 1 | 16,728,848 | 16,125,336 | 3,456 | 4,840.523148 | 4,665.895833 |
| PostgreSQL | 256 | 31,282,248 | 28,538,592 | 3,456 | 9,051.576389 | 8,257.694444 |

The 256-row reductions are 8.601770% and 8.770648%; each provider/version consumes
884,736 rows. Gen0 remains 9 to 9 for these windows, with Gen1/Gen2 zero. Empty
and one-row windows retain Gen0 3 to 3. The original raw result format supplies
per-window generation deltas, so the independent audit does not claim to have
recomputed unseen generation start/end counters. It did recompute every retained
cumulative allocated-byte difference, operation/row/checksum count, retirement,
command exit and observer identity in all 12 before/after process records.

This probe consumes scalar long values into checked sums; it creates no business
DTO, List, string or result-array objects in the measured intervals. Its business
output allocation is zero by this narrow result contract. Ordinary business result
objects remain expected allocations, including objects created by a generated
mapper. Complete-query raw bytes still include framework plus runtime/harness
activity; they are not an exact framework-only remainder. No control is subtracted,
no separate business/framework GC collection count is invented, and no qualified
CPU, native-allocation, RSS, latency or throughput gain follows from these windows.

The original Host v1 compiler command exited 1 with CS0122 because its fixture used
methods returning inaccessible internal Streaming types; its interrupted top-level
receipt is retained as written. V2 changes only that fixture to exercise the same
private bridge with an accessible NativeBuffer and join the existing CloseController.
Actual Host v2 AOT passed 636 assertions, 219 retirements, 5,942 parser oracle inputs,
12 mapper lifetime scenarios and zero final native owners. The already matched
Interop and Streaming v1 AOT gates are reused with their original hashes; no JIT
consumer was added or rerun. The independent production reviewer authored none of
the eight reviewed production/test inputs and found no blocking ownership,
cancellation or result-publication issue.

Five original source archives were read locally and their members checked, producing
two distinct 342-file manifests. The reference inventory contains 700 fixed source
entries / 328 distinct texts. Its 13 local-only historical origins / 10 distinct
texts include the failed Host fixture, temporary helpers and redundant diffs. Those
texts are disclosed without assigning another version's public identity. The three
source-bearing publication API records also remain local because they contain full
source or patches. Original source-free create-tree/create-commit/update-ref responses,
the publication receipt and its initial CI observation are retained verbatim. Full
source archives, patches, helpers and binaries were not copied into Plan; the before
raw files continue to be referenced from the unchanged iteration17 checkpoint.

The source publication receipt includes source-only resource-probe inputs; their
presence grants no resource-probe execution credit here. The retained initial
[normal CI observation](https://github.com/IzuSharp/Korda/actions/runs/45438460386)
is **in_progress**, not a prediction of success. PR merge, merged-main checks,
automatic preview, actual public NuGet consumption and final combined-package
allocation/campaign acceptance remain separate obligations. Long credit stays
**0/8**. Resume from the published source identity and the preserved raw index;
do not repeat this iteration's already matched measurements.

## Continue from here

1. Reconcile remote branch/PR heads and all newly retained receipts. Preserve
   current work and recovered baseline binaries; do not start a second campaign.
2. Reuse the complete 35-case, recovery, heavy-consumption and allocation records
   only at their actual source/binary identities. Bind all pending reproduction
   references to the published final Korda commit/tree; keep the immutable original
   771bc77 packages and all intermediate experimental/CI candidates distinct.
3. Obtain final combined CI packages, independently restore/publish the unchanged
   consumer source against before/after packages, verify hashes/API/ownership and
   complete final public allocation attribution. The 35-case manifest has 29
   Fluent cases, four public CRUD/transaction cases, one hand-written SQL case
   and one public related-batch case. Dapper.AOT is an independent micro-ORM SQL
   route, not a second Fluent implementation.
4. Activate the reviewed task-specific workflow only with complete actual input
   identities. Admit the dedicated VM, quantify before-only noise, freeze the
   sustainable rate and measure the four-column short/heavy/capacity layers.
   Retain the best tested SLO capacity and bracket; do not claim a mathematical
   maximum from a finite coarse/refined grid.
5. Run the four routes × two databases as eight independent continuous effective
   30-minute mixed segments on the admitted resource set; warmup/drain/idle are
   extra. Keep raw bytes/time series and source/parameter/environment hashes.
6. Finish scoped correctness/API/AOT/allocation checks and non-author review,
   normally merge verified changes, observe main/preview, and consume actual
   public NuGet packages. Keep incomplete paths and stopping reasons explicit.

The new Plan record gate is `python3 tools/verify_db_perf.py`; optional
`--verify-frozen-history` runs the unchanged DB-Rename and nested DB-API gates at
their original inputs. `--archives /absolute/path/to/baseline-artifacts` rechecks
the selected original package bytes. A document/integrity pass is not a benchmark
result. The current evidence commit's own future CI is always checked separately.

