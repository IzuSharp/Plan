# Perf-01 Linux x64 handoff

## Current state

Status: real locked before packages/consumers built; domain drivers independently reviewed; first profiling and diagnostic calibration observations retained. Final execution configuration remains unfrozen. No product optimization has been applied. No performance improvement is claimed. No Perf-01 30-minute segment has started.

The current user instruction authorizes this implementation and performance task; historical research-only scope text remains historical and is not rewritten.

| Repository | Starting commit |
| --- | --- |
| NativeWeave | `ea5fa528035d025bd7a28698ee7c71194432236c` |
| Plan | `8afa0311f45ab8a8157fc45c51e95a0b17dd09f2` |
| Locked Design | `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9` |

The measured before version must be built from the product starting main commit above. Historical B22/B23 observations only locate hypotheses; they cannot supply the new before row or the new 30-minute acceptance. B24 candidate native hashes differ from historical B22/B23 hashes.

## Workspace and ownership

`ROOT` is `/workspace/scratch/01c249676f47` for this execution. Integration worktrees are `ROOT/.worktree/Perf-01-linux/{NativeWeave,Plan}` on `task/Perf-01-linux`. The immutable product source is `ROOT/.worktree/Perf-01-baseline-linux/NativeWeave`. Independent source/driver work uses `Perf-01-db-linux`, `Perf-01-protocol-linux` and `Perf-01-codec-linux` worktrees. Root owns shared implementation integration and the sole formal timing resource.

Parallel agents currently prepare source analysis and test drivers only. Product implementation changes must wait for the measurement configuration freeze. Builds/profiling and formal timing do not overlap. Every valid segment requires exact source, driver, executable, package and loaded-native hashes.

## Required execution

Five representative mixed groups (PostgreSQL, SQLite, HTTP, gRPC, compression/decompression) each need an actual 1,800-second before and after segment: **0 of 10 completed, 0 effective seconds credited**. Warmup, calibration and idle/drain are separate. Interrupted and invalid attempts remain immutable and receive no passing credit. Existing Task-07 segments do not match this baseline and are not reused.

The prospective configuration must freeze machine/CPU, dependency/build settings, package closures, durable database state, TLS, data, pool/connection policy, operation mix, arrival/concurrency ladder, failure rules, service constraints and generator saturation checks. Same driver inputs apply to both product versions. A21 independent-process noise analysis is reused where applicable. Direct Rust rows need semantic parity; unavailable metrics remain unavailable.

## Environment recovery

The execution host is Linux x64 / Debian 13 with nine available virtual CPU IDs. The prospective cohort pins every measured process tree to CPUs 2 and 3. A retained `.NET SDK 11.0.100` is available under `ROOT/../58d2a6adf1c3/dotnet-sdk`. Exact Rust 1.100.0, PostgreSQL 18.0 and local Native AOT linker prerequisites were installed/built successfully under `ROOT/perf01-toolchain`. Source `ROOT/perf01-toolchain/env.sh` for all reproduction commands. No remote Linux host tool is exposed. Physical-host scheduling and hardware power controls are unavailable; do not claim dedicated bare-metal isolation.

The clean main baseline produced full B24 package closures, B21 package JIT/AOT applications, the identical B23 exception observer, the shared retirement AOT profiler, the complete A17 codec package/consumer checks and fresh direct Rust/managed database comparators. Protocol package server/client AOT builds passed, with review fixes being rebuilt separately. Build success is not a measured performance result. Exact local manifests:

- `ROOT/perf01-build/before/native-stable/manifest.json` (fresh stable tool environment; native hashes also equal an earlier independent build).
- `ROOT/perf01-build/before/packages/manifest.json`; use its complete **previous** feed, version `0.1.0-perf01.before.1`.
- `ROOT/perf01-build/before/reference-002/progress.json` and `ROOT/perf01-build/before/db-observer/manifest.json`.
- `ROOT/perf01-build/before/shared-profile/manifest.json` (profiling-only; not yet executed).
- `ROOT/perf01-build/comparators/comparators.json` (fresh actual golden checks passed; live HTTP/SQL measurement pending).
- `ROOT/perf01-codec-checks/package-before-001/manifest.json` (clean source `ea5fa528`; A17 package/AOT/ordinary-edit-reuse/negative checks completed).

Failed setup attempts remain separate: initial PostgreSQL build before explicit M4 path, reference build before installing its pinned HTTP/2 client extras, and the direct protocol comparator's first compilation attempt. No measurement credit is assigned to setup attempts.

## Package and scope cautions

B24 normally preserves eight COMMON packages between its own previous/candidate pair. Perf-01 shared implementation changes must instead reconstruct a fresh complete closure for each tested product version and verify every loaded managed/native identity. Reusing an old common package would invalidate an affected optimization result.

The current gRPC implementation supports identity compression only. Independent A17 codec performance is separate from negotiated network compression. Public domain package publication remains a separate task; the existing normal HelloWorld preview flow is checked after an accepted merge. The 24h/72h stages remain deferred.

## Durable evidence and resume

`baseline-source.json` binds the starting source and lock files. English source analyses and frozen executable profiles are added here as work completes. Only authorized synthetic project samples and allowlisted host metadata may be uploaded; keys, credentials, database contents and unrelated data stay out of evidence. No old rejected publication is retried by this task.

Draft implementation PR: [NativeWeave#19](https://github.com/IzuSharp/NativeWeave/pull/19), currently test tooling only. Draft evidence PR: [Plan#23](https://github.com/IzuSharp/Plan/pull/23). Both use `task/Perf-01-linux`. The implementation checkpoint `d252fc589d1559b7cdbb907c2dfa25bc7ea8c2ef` has the identical tree to local test commits archived at `checkpoint/Perf-01-local-drivers-001`; source baseline remains unchanged.

`prospective-policy.json` records the first prospective CPU/resource/SLO rules,
ladder/refinement and long-rate selection. Final driver/profile/artifact hashes
and calibrated rates must still be bound before any runtime implementation edit.
Source studies, fresh build receipts and independent reviews are adjacent files.
The execution checkpoint below supersedes earlier preparation status. Resume only
from exact receipts; **0 of 10 long segments are credited**. No performance
improvement, merge or preview is yet claimed.

### Execution checkpoint: first profile and interrupted diagnostic calibration

The package AOT SQLite retirement probe completed 1,000 scalar calls / 4,000 native
operation observations with all release and timestamp-order checks passing.
`observations-before/shared-sqlite-profile-{summary,raw}.json` contains the actual
data. A21 exact percentiles give public mean 1.1959153 ms and p99 20.7677 ms.
Take-to-observed-retired has 64 of 4,000 observations above 5 ms. This includes
mapping and continuation scheduling and does not directly count native Pending;
it is a profile, not a formal timing row or an optimization result.

Actual baseline package application smoke checks also passed independently for
PostgreSQL and SQLite: 121/121 mixed logical operations, exact response/durable
oracles, 61 measured committed mutations, no observed provider exceptions, and
consumer/database/server release. Their source-bound local directories are
`ROOT/perf01-evidence/smoke/before-{sqlite,postgresql}-001`. Codec smoke passed at
`ROOT/perf01-evidence/smoke/before-codec-001` with actual native mapping/byte and
owner checks. These smoke cells do not count toward long acceptance.

Initial codec calibration shared CPUs 2 and 3 between target and generator.
Higher points and longer confirmations hit the declared 50-ms generator dispatch
lag bound even when output correctness passed. Those points are invalid, not
server capacity results. The compact diagnostic history is
`observations-before/codec-calibration-v1-partial.json`. After 17 completed cells,
the controller session was unavailable (`write_stdin: Unknown process id 66326`)
and the eighteenth cell had no final result. Last raw activity was
2026-11-19T07:24:10Z. Its partial logs and `interruption.json` remain in
`ROOT/perf01-evidence/calibration/before-codec`; no cause or clean exit is inferred.
Keep live session polls/heartbeat supervision during future long execution and
credit only fully completed, valid receipts.

An **optional diagnostic** is being added to give the external generator spare
CPUs 0 and 1 while preserving the application/database on CPUs 2 and 3. This has
not yet been executed or selected as the final configuration. If chosen, revise
the prospective policy explicitly and restart the baseline cohort; do not
retroactively relabel earlier shared-CPU rows or attribute resource-layout gains
to product optimization. SLO/correctness limits are unchanged. The current window
permits builds only: rebuild the final generic-x86-64 direct protocol comparator,
bind the reviewed optional codec controller to a fresh before package preparation,
then resume short diagnostics. Runtime source must remain unchanged until the
complete frozen-execution record is written.

### CPU-layout selection before final calibration

The split-generator codec diagnostic completed at2026-11-19T07:59:59Z:23,061/23,061 operations over60.050331522 actual dispatched seconds,arrival p99107.682662ms,exact output and owner checks,valid50ms generator bound and observed service2,3/generator0,1 masks. Policy revision2 selects this fixed four-CPU layout for the final baseline/after/direct cohort. Revision1 is archived as `prospective-policy-v1-diagnostic.json`; its shared-CPU cells remain diagnostic only. No product implementation change or30-minute segment has occurred. Exclusive final baseline calibration now starts; no builds or other loads may overlap.

### Execution checkpoint: prospective revision3 before runtime edits

All runtime/product implementation files still equal baseline main. Codec revision2 calibration was deliberately interrupted at2026-11-19T08:31:05Z after repeated generator-start-lag invalidity, including an otherwise-idle confirmation. Completed and partial results remain under `ROOT/perf01-evidence/calibration/before-codec-v2`; the last cell completed its load but not recovery/finalization and is not credited. Compact receipts and the separate same-interpreter GC/I/O observation are in `observations-before/codec-{calibration-v2-partial,generator-profile-summary,generator-profile-observer}.json`. Linux perf returnedzero samples; no CPU-stack profile is claimed.

Policy revision3 prospectively aligns codec with the existing database/protocol100ms dispatch-start guard, retains scheduled-arrival p99<=500ms/error0/RSS256MiB and all correctness/ownership limits, pins Python3.12.14 by executable SHA256, and keeps older50ms verdicts unchanged. This is a measurement-policy revision before product edits, not a fixed generator defect or measured product gain. Fresh revision3 calibration follows. Record actual lag distributions and >50ms excursions; generator-limited failures are not a server-capacity bound. Every long segment is prospectively scheduled for1802s, still requiring at least1800s verified effective sending. Final `frozen-execution.json` is still pending. **0/10 long segments credited.**

Latest pushed product test-only commit is `34b00cb3adfa1f204d046f8215a6c9d46b7a0e00`, tree-equal to local archive `checkpoint/Perf-01-local-drivers-003`. Earlier product commit `cd26f8c6fcb12edaf57f791a5df21cf79afda73d` passed every job in workflow run44480936232. Latest pushed Plan checkpoint is `e6ed82ebce1b53e028176edce1cb08b208a13b04`; its prospective-policy bytes were independently read back and matched local content. Subsequent local evidence/source notes will be pushed at the next checkpoint.

### Execution checkpoint: first final calibration selection

Codec revision3 completed its three fresh60s confirmations at336 offered operations/s, each with20195/20195 correct operations; arrival p99 was116.958,109.754 and125.431ms, with zero rejection and successful recovery. The predeclared80% rule selects268 operations/s with two workers for the eventual before/after long group. Higher actual rejection points remain retained; this is a measured sampled operating point, not a universal capacity guarantee. `observations-before/codec-calibration-v3-{controller,selection}.json` preserves the compact immutable calibration result. No long segment or product improvement is credited.

The serial controller continues with SQLite, PostgreSQL, HTTP and gRPC. In the SQLite ladder,40/s passed with arrival p99148.295ms;80/s yielded2400/2401 successful logical operations, arrival p994.699s and one directly observed SQLite BUSY exception (primary5). The independent SQL oracle verified1200 measurement commits;16 same-live-process recovery operations and all consumer/database/server release checks passed.60/s had no observed error but failed the500ms tail standard. The bracket is being confirmed; do not promote a provisional rate to the final freeze.

The public-page allocation probe and conservative common long-evidence verifier are integrated as test-only code. Their source reviews passed; local execution waits for the non-timing window. `long-verification-clarification.md` supplements policy3 without rewriting its active hash. It corrects SQLite retry-count scope and defines the stronger ordinary-operation duration proof.

Product test checkpoint `6b0c74de9c03e3c28c09398ae28e82932b7e4fda` is tree-equal to local archive `checkpoint/Perf-01-local-drivers-004`. Product predecessor34b00cb passed CI run44489855065. The source baseline remains ea5fa528; no runtime optimization has been applied. Continue polling the active controller, avoid builds or overlapping loads, and finish calibration/profiles/final freeze before runtime edits. **0/10 long segments credited.**

### Execution checkpoint: SQLite selected, profiling and PostgreSQL observer correction

SQLite completed three passing60s processes at49/s, with arrival p99194.453,251.595 and216.575ms; its final long rate is39/s at16 client slots.55/s failed one confirmation (p99567.404ms). The corresponding compact controller and selection are retained in observations-before.

At2026-11-19T09:24:21Z the first PostgreSQL calibration attempt failed during setup. PostgreSQL18.0 was ready; the observer assumed `/proc/<pid>/task/<pid>/children`, which this execution environment does not expose even for a live current process. Its finally path cleanly stopped the private postmaster. This is an observer failure, not a database performance sample or a missing-process claim. The failed attempt remains under `ROOT/perf01-evidence/calibration/before-postgresql-v3/00-ladder-5`. Test-only product commit5b2a876 integrates parent-PID/start-time procfs discovery with strict live-root and observed thread-mask checks. Independent review and six finite synthetic tests passed. Source/runtime packages are unchanged.

During the non-timing window, `before-B15-result.json` records passed new JSON regressions in JIT and actual AOT, real server85-assertion gates, exact278-symbol API and package consumer. The common long verifier's14 finite tests passed (`common-verifier-finite-001.json`). The baseline public page probe was built and executed serially for both providers; each verified1000 complete100-row pages and all public resource releases. Raw/profile summaries in observations-before report approximately72.8KB managed allocation per page; SQLite/PG mean6.173/5.985ms and p9925.077/25.862ms. These are profiles, not formal comparison or long-load credit.

Exclusive calibration resumed at2026-11-19T09:32:14Z for PostgreSQL, HTTP and gRPC, attemptv3r1. Current shell session is86401. Use the same policy3 bytes and unchanged immutable before artifacts; active driver files must not change. All builds/tests/other loads stop; source-only commands may useCPU8. The optional protocol selector has been integrated for later layered cells; its absence preserves the mixed long profile. Final freeze and all ten long segments remain pending. **0/10 long segments credited.**

### Execution checkpoint: PostgreSQL selection and generator diagnostic

PostgreSQL completed three fresh passing60s confirmations at153 offered logical operations/s; the selected long load is122/s at16 slots. The selection completed2026-11-19T09:53:33.576830Z. Higher190/s and171/s confirmations each included a generator-lag invalidity despite correct business completion. They are not server-capacity upper bounds. `postgresql-generator-lag-analysis.md` binds the exact two raw gaps, target progress during those gaps, and causal limits. The A21 scheduler/event-reader/sampler all pause together near10000 completions; retained nested record/counter objects and Python GC are a hypothesis requiring separate instrumentation, not an established cause. A dedicated profiling-only launcher is being prepared before any30-minute group.

The active serial controller remains86401 and has advanced to HTTP, then gRPC. Product checkpoint6e4ca71925559faf5d0725398f4a19e20ad6528e passed CI run44498028350. Plan checkpoint078987e5a1b81d77a9c7f583fa3823888de2802b and selected profile content were read back successfully. Source/product runtime remains main ea5fa528. Final frozen-execution record is absent; no runtime optimization or30-minute credit has occurred. **0/10 long segments credited.**

### Execution checkpoint: actual profiles and prospective gRPC budget correction

HTTP revision3r1 selected1152/s after three passing60s processes (arrival p99373.623/339.391/274.288ms).1280/s failed its third confirmation at785.035ms. The declared finite-accounting cap selects500/s for its long group, so no near-capacity claim is attached to that long load. Compact controller/selection are preserved in observations-before.

The first gRPC8/s revision3r1 cell completed242 calls, including two ordinary server-stream ResourceExhausted outcomes after1 and28 response messages. All declared deadline/cancel probes matched, and recovery/drain passed. This is a real service-standard failure, not a generator or intentional-probe relabel. `grpc-baseline-quota-observation.md` explains the source-proved overlapping configured-maximum frame grants that can exceed4MiB, while exact throw-site attribution remains unavailable. Before any product runtime edit, policy4 selects a gRPC-only64MiB request cap with unchanged global native64MiB/managed64MiB, RSS256MiB, maximum message1MiB, payloads, TLS and error/tail/generator standards. HTTP remains unchanged. Direct Rust's actual-frame charging versus NativeWeave's configured-maximum reservation is disclosed as an implementation difference. The old policy3 bytes and old failures remain immutable.

Exclusive gRPC-only revision4 calibration started2026-11-19T10:26:18.979265Z in session49533.8/16/32 offered calls/s passed; selection is not yet final. No other task loads/builds/tests may overlap. Source-only commands may useCPU8.

A separate actual171/s120s PostgreSQL generator profile completed20522/20522 correct operations but failed generator lag. Its four generation2 GC callback intervals were68.557/189.580/127.447/175.430ms and collectedzero objects; three exceed100ms. Instrumentation overhead and host descheduling remain limitations. Full diagnostic receipt is `observations-before/database-generator-profile-001.json`. A test-harness-only compact-retention candidate is being prepared in the DB worktree; A21/RunState default callers must retain semantics, and no GC disabling or threshold change is allowed. It needs exact replay/equivalence tests and fresh measurements before final freeze. Harness gains will never count as product gains.

The actual PostgreSQL statement/wait profile completed122/s20s with correctness/durable/recovery checks. `observations-before/postgresql-statements-profile-001.json` contains per-statement Parse/Bind/Execute and sampled wait states. It is profiling-only; exact lock duration, pool-wait duration and database CPU remain unavailable. Actual JSON/tiny diagnostics each completed645/645 requests. Their sampled managed allocated-byte deltas were674465840 and8363968 bytes respectively, with generation2 counts68 and0; they are separately run profiles, not paired optimization results. `observations-before/protocol-allocations-profile-001.json` records interval/identity/resource limits.

`measurement-tools-finite-002.json` records20 actual Plan archive/codec-helper checks and19 existing A21 checks passing with exactPython3.12.14. A proposed outer long-run wrapper was withdrawn before commit after review found unnecessary interruption-lifecycle complexity; use existing supervised domain commands one group at a time and freeze their exact arguments. Database soak recovery must be32 requests (not the16 used in calibration), with idle60s.

Product runtime still equals main ea5fa528; product local510409e only adds the separate profiling launcher. Plan last remote429c091 has passed CI44501673440. Current new evidence/profile/policy files await the next push checkpoint. Final frozen-execution.json remains absent and **0/10 long segments are credited**. Continue until actual before/after comparisons, all ten long groups, required verification/review and normal merges/preview complete.

### Execution checkpoint: compact observer verified, final producer refreshed

The test-only A21 compact observer passed29 actual finite harness tests and six
DB affinity tests, then the same171/s120s PostgreSQL generator profile completed
20522/20522 correct operations with valid generation and the service standard
(p99 arrival89.080751ms). No generation2 collection interval occurred during
measurement; the maximum measured GC callback interval was0.988382ms. Complete
values/counters were restored after load. This is a measurement-tool change,
not a NativeWeave runtime improvement. Fresh compact SQLite/PG calibration must
replace the older full-retention selection before the final freeze.

gRPC revision4 completed three passing60s confirmations at208 offered calls/s,
with arrival p99152.263/152.687/151.965ms. Its before-derived long rate is166/s.
The complete controller and selection are retained as
`observations-before/grpc-calibration-v4-{controller,selection}.json`. The224/s
probe failure is specifically a missing expected committed header, not proved
payload corruption or an inferred gRPC status. The256/s service failures remain
failed. HTTP's earlier mixed selection remains1152/s, with the prospective500/s
long cap.

Fresh final codec before producer `perf01-codec-checks/package-before-003` passed
all25 expected preparation outcomes, including139 assertions each for JIT,
ordinary managed-edit JIT reuse and actual Native AOT. It binds unchanged clean
product main ea5fa528 and current A21 SHAa07dc5f338a13c8f9c4bedadb6d21cffd1e0f835d8381f16bb24f90d68ea98ad.
Its immutable manifest SHA is
f7a766eb277d09a6f5d64fd3ecac2e83bf6dcbac41ab384c0b75affc234c775d;
full metadata is in `builds/before-codec-003/`. Do not rewrite before-002.
The new one-worker134/s smoke completed1355/1355 with p99110.687603ms and passed
resource/ownership checks; it is not a noise cohort or long segment.

Baseline B18 writer tests actually passed Release/JIT662 assertions and Native
AOT663 assertions against the unchanged server4827a6ec. The full scoped verifier
still runs its independent package proof in session25804, output
`ROOT/perf01-evidence/functional/before-b18-writer-002`. Attempt001 stopped before
managed tests because the literal clang-19 name was absent; a private launcher
now names the same installed19.1.7 compiler. Keep001 as a tooling failure.
After002 exits and all builds stop, run the reviewed compact DB calibration
controller and final before-only noise/cohorts before runtime edits.

Product branch a723bac2274ea760ef5afbe025edbee32589b9ae is tree-equal to local
archive `checkpoint/Perf-01-local-drivers-008`; it only adds B18 tests. The
predecessor a583 CI was superseded/cancelled during Task-07 package verification
when this new checkpoint was pushed; it is not claimed green. Plan8bae297 passed
CI44508237005 and its selected policy/profile bytes were read back exactly.
Current Plan additions await the next push. Runtime/src and native implementation
still equal ea5fa528 except benchmark-harness source. `frozen-execution.json` is
absent, and **0 of10 long segments are credited**.

### Execution checkpoint: final streamed harness and baseline ownership defect

The final test-only product checkpoint is aa3399f0418a6d0910cc56697abfaa3769f32b54
(tree46431456e32e6c295aa3cac0c2b80344c25b6880); all C#/Rust runtime implementation
still equals clean before main ea5fa528035d025bd7a28698ee7c71194432236c. The
compact path now streams dataset preparation, expected values and complete
observation finalization while retaining full correctness evidence on disk.
Actual finite gates passed33 A21,6 DB streaming and14 common verifier tests.
The final same-load171/s120s PostgreSQL diagnostic completed20522 correct
operations, p99 arrival101.755224ms, valid generation and service checks, and
90,337,280-byte worker lifetime RSS high water. Its single measurement Gen2 was
25.573027ms; post-window finalization had no Gen2. These are harness diagnostics,
not product improvements or long acceptance. The actual three-run comparison is
retained in observations-before/db-generator-compaction-001/.

Fresh codec before-004 completed25 expected preparation outcomes at
2026-11-19T11:44:57.783919Z, including139 assertions in each actual JIT, managed-edit
JIT and Native AOT consumer. Its manifest SHA is
d34298ebc8dc82b525f19860555947a1a04eff2bf8aecc38cede2922c81285a7; current
A21 source SHA is dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53.
Actual immutable package/native/consumer inventories are in builds/before-codec-004/.
Older producers and calibration results remain preparation-only; they are not
rewritten to the final driver identity.

Baseline B18's full independent package verification finished successfully, with
JIT662/AOT663 assertions and original command receipts retained. B06 also passed
its24 actual scoped commands, including real SQLite/PostgreSQL and Native AOT.
A02 is a real separate failure: aot-default-concurrent exited-11, reproducible
with the exact existing executable. Locked Native AOT FixupModuleCell frees
each losing callback result; the existing resolver returns its sole resident
handle without acquiring the reference transferred to that runtime fixup. An
independent forced-overlap control reproduced-11 with a borrowed handle and
passed64 calls with a fresh OS reference per callback, including the measured
Linux unlink case. No runtime fix or warmup workaround has been applied; retain
the before failure and fix ownership after configuration freeze.

Fresh final compact DB calibration started2026-11-19T11:49:07.255174Z in session78012,
SQLite then PostgreSQL, under unchanged policy4. Service/database CPUs2,3 and
generator CPUs0,1 are exclusive; other agents may read/edit source onCPU8 only.
No builds, tests or other workloads overlap. Fresh final-driver codec and
HTTP/gRPC calibration plus before-only noise remain next. The final immutable
frozen-execution.json is still absent and **0/10 long segments are credited**.

Plan checkpoint8c3972979af9926a1e16ea193a9b5a68652782cd passed CI44513900559.
Product aa3399f CI44516411426 was still running at this checkpoint. Both PRs
remain drafts; no merge, final performance gain or preview publication is claimed.

### Execution checkpoint: target retention must be fixed before final DB freeze

Both compact-v4 database calibration loops completed and their artifacts remain
immutable. SQLite's final54/s three60s confirmations had3241/3241 successes each
and p99286.206671/214.076054/257.418997ms; PostgreSQL's180/s triplet had10801/10801
and p99101.687186/100.874169/138.499745ms. The policy-derived rates43/s and144/s
are **preparation selections**, not the final DB freeze. SQLite also had an earlier
failed54/s short point, and every failed/higher sample is retained. Its80/s failed
logical cycle had committed create201, BUSY replay500 and matching recovery200;
there is no evidence of a corrupted successful recovery response. The PG200/s
first confirmation rejected117 operations before dispatch at the A21 outstanding
limit; every11884 dispatched operation succeeded. GC/native-queue/exact SQL wait
attribution is unavailable in those ordinary cells. Separate notes preserve both
failed verdicts and their actual evidence, without relabeling failure as success.

Source follow-up found a second, concrete measurement-tool memory risk: the
HTTPX target retains every full page in operation_outcomes, serializes the entire
receipt after drain, and its parent loads that receipt in full despite using only
small metadata. The existing171/s120s streamed profile actually sampled target
RSS152,498,176B during measurement and181,960,704B in final reconciliation, with
a42,562,221-byte final target receipt. Multi-GB long peaks are extrapolations, not
measurements. observations-before/http-target-retention-001/ records exact scope.
The DB agent is preparing only an explicit compact journal/streamed receipt and
parent projection fix; default B23 behavior and complete on-disk evidence must
remain equivalent. A21 SHA dfb57cf is frozen and will not change. Targeted gates,
independent review and the same120s diagnostic must pass before a fresh final DB
calibration. The prepared SQLite v4 noise script was not executed.

Fresh codec final004 calibration began2026-11-19T12:21:51.572954Z in session82291,
using actual before004 manifestd34298eb and unchanged policy4/corpus. No builds,
tests or other loads overlap; agents are source-onlyCPU8. Both common codec and
protocol wrappers actually passed CLI/import --help checks in
checks/calibration-wrapper-cli-001/; this is not a full finite/load gate claim.
The protocol final calibration and short before-only noise still follow.

Latest pushed Plan bc916f0cf8bcdd41bce590f4910231d6e9d3fa69 has the source proofs
and shared capacity wrappers; the A02 note was read back byte-for-byte. Product
runtime remains unchanged main ea5 and driver aa3399f. Final frozen-execution.json
is still absent. **0/10 long segments are credited; no runtime performance gain
or final acceptance is claimed.** Continue the authorized task after this checkpoint.
