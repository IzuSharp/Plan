# DB-Perf-01 — Linux handoff

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

## Live update — 2026-11-24 17:56 UTC

The current campaign is [45452087158](https://github.com/IzuSharp/Korda/actions/runs/45452087158),
workflow source `75db602c59f3c3366488df9f1c1717934f7d850f`, unchanged collector
`4ee348d8b9834a14327dcf68a105e34f52f81795`, request SHA
`c32ab5e50fb38cfd1c9a45748e6085c903456bbd8f745112651a9767e84f93bb`.
Its first preparation attempt rejected the older runner image before building;
preparation retry `138653923314` passed the explicit `20261116.376.1` image
check and completed successfully. Measurement job `138657301659` passed the
same image check and is now in VM admission and load calibration. No qualified
long segment has completed: **0/8** remains the only accepted count. Inspect the
live run before any retry. The earlier `45449544703` measurement-only retry
also rejected its image mismatch and remains uncredited.

Latest product branch head is `c7c0347e30faa9e1d54a201dada7210ee7cd49b8`;
the last commit only registers the new environment diagnostic workflow with
its existing CI module. Local tracked-ownership, impact and Tooling checks passed
(44 tests, one skip); [normal CI 45453261268](https://github.com/IzuSharp/Korda/actions/runs/45453261268)
is still being observed. This does not change the measured production packages,
consumer business source, workload or any performance threshold.

The prior handoff-only commit `62ac70899a4add051c48dcdcf54ff96ce25cc8ed`
passed [Plan CI 45451305502](https://github.com/IzuSharp/Plan/actions/runs/45451305502).
Full raw checkpoint publication continues independently and is not yet complete.

## Latest live recovery observation — 2026-11-24 17:41 UTC

Read this newer observation before the historical checkpoints below. The user
confirms that **0 B is the steady-state target for additional framework
allocation; required business DTO/List/string/typed JSON objects need not be
zero**. Shared-process GC collection events are not split into fictitious
framework and business GC counts.

- Product branch head: `663ceb97b3d20c38048ce17869259a6b9df62492`.
  The measured final package producer remains
  `3d5ba3f9884308caa691718f73a74aa42be19d94`, tree
  `74a76bc5d00671a48221d0ed19002a3ffffd319f`, from successful
  [CI 45438460386](https://github.com/IzuSharp/Korda/actions/runs/45438460386).
  Both separate providers are version `0.1.0-ci.1`. Do not replace the measured
  candidate with later harness-only CI packages.
- Active isolated campaign:
  [45449544703](https://github.com/IzuSharp/Korda/actions/runs/45449544703),
  harness `4ee348d8b9834a14327dcf68a105e34f52f81795`, request SHA
  `4c5c751d8fd8708ade19e1f1cf291a156f9dd24c84eaa7b33e7afb4f469d88f6`.
  Preparation succeeded. The first measurement attempt stopped before admission
  because preparation used image `20261116.133.1` and measurement was allocated
  `20261116.376.1`. Only failed measurement job `138645902342` was rerun; it
  reuses the same verified runtime bundle. The image-equality gate is unchanged.
  Re-read its live state and checkpoint artifacts before retrying. Do not overlap
  campaigns. **Accepted long segments remain 0/8** until actual qualification.
- Two earlier startup failures remain uncredited:
  [45442350170](https://github.com/IzuSharp/Korda/actions/runs/45442350170)
  found Python bytecode writes inside the immutable bundle; bytecode writes are
  now disabled. [45444706914](https://github.com/IzuSharp/Korda/actions/runs/45444706914)
  failed quota ancestry observation before any workload and did not preserve
  its quota snapshot. A [new read-only VM observation](https://github.com/IzuSharp/Korda/actions/runs/45447986595)
  reproduced EACCES reading PID 1's namespace while all quota ancestors were
  visible. The independently reviewed fixed read-only namespace helper preserves
  the original error and all existing admission rules; [its new-VM validation](https://github.com/IzuSharp/Korda/actions/runs/45449083846)
  passed the unchanged quota assessment. Neither diagnostic establishes full
  admission or earns long-test credit.
- Final ordinary-package scalar diagnostics are complete: each provider has
  384 complete 256-row dynamic queries and 384 prepared queries, with unchanged
  original baseline processes reused. Total managed allocation fell about
  71.7% dynamic and 90.8% prepared. Only the already-buffered 127-row window is
  measured at raw 0 B; the final refill-plus-first-row window remains 512 B.
- Buffered business results are complete across eighteen independent processes:
  actual List100, one hundred DTOs, eighty distinct strings and twenty NULLs.
  Korda whole-query totals fell about 50% to 34.73–34.74 KB/query; Dapper.AOT is
  10.91–11.17 KB/query. The 7,480 B same-graph business control is not an exact
  in-query attribution and its subtraction is not exact framework allocation.
- Twelve before/final resource processes passed real pool pressure, pending and
  unconsumed operations, cancellation and zero-owner retirement. Preserve cold
  Fluent preparation +696 B and PostgreSQL exhaustion/cancellation +8.607%
  allocation regressions. Local diagnostic CPU/retention values do not replace
  the dedicated four-column mixed-load results.

Detailed new raw checkpoints have passed local integrity/source gates and are
being uploaded as verified content-addressed Git objects. Their publication is
not yet complete: do not assume missing paths are public. The frozen local Plan
checkpoint is `a0b455b8c391b75fcdc8cef754fe8b0ab2c806f5`, tree
`d317bd4d33438251b2608659b7f673129f145833`; later resource and environment receipts
are being appended. Local task worktrees remain under
`/workspace/scratch/b94e2a0e0c3f/`, with upload recovery manifests under
`/workspace/scratch/37c4f8cc3a91/plan-upload/`. Reuse their unchanged matched
measurements. No normal merges, automatic preview or public NuGet acceptance
are claimed yet; these remain authorized outstanding work.

## Current recovery point

This is an **in-progress measurement and implementation checkpoint**, not batch
acceptance. Read [plan.md](plan.md), [baseline.json](baseline.json),
[allocation-inventory.md](allocation-inventory.md) and
[acceptance.json](acceptance.json). Long-test credit is **0/8**, with **0 accepted
effective seconds**. No framework-wide zero-allocation claim is established.

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

## Concurrent checkpoint reconciled without replacement

**Publication recovery:** automatic approval review rejected new full
implementation/controller source snapshots being uploaded to Plan. The
[source-location correction](source-scope-correction/README.md) replaces only
93 locally added source copies with exact Korda source references. Raw measured
files and all pre-existing remote evidence remain unchanged. The complete local
snapshot is preserved at `b279f42674eb3e8db48b423482f38c6b955c4d82`; 82 references
to 45 immutable archive inputs still await the actual Korda commit/tree. Do not
publish the superseded full-source tree or invent those commit identities.

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
the final candidate stays unset until that decision and its measurements are
complete. The eight qualifying long segments remain **0/8**.

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
the scheduled-rate SLO ladder. The current overload/recovery commands use fresh
processes, so same-pool recovery remains a separate requirement.

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
remains allocating. Strict malformed UTF-8 and canonical/noncanonical decimal
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
owners. Native full-heap allocation/free call counts remain uninstrumented; glibc
snapshots and SQLite allocator high-water values are narrower observations.
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

## Continue from here

1. Reconcile remote branch/PR heads and all newly retained receipts. Preserve
   current work and recovered baseline binaries; do not start a second campaign.
2. Reuse the completed original-package and minimal independent-ORM AOT receipts.
   Finish equivalent expanded workloads and bind one unchanged consumer source
   set to both the original and final candidate packages.
3. Freeze the workload/data/SQL/result manifest, define at least 24 business cases
   per database, and complete correctness before timing.
4. Admit the dedicated resource set, quantify before noise, then measure baseline
   allocation and short/maximum-throughput curves. Production edits follow actual
   measured hotspots, one isolated comparison at a time.
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
