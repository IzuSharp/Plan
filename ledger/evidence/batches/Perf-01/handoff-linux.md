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

### Recovery checkpoint: completed target validation and live calibration

Recovered at 2026-11-19T12:57:29.573020+00:00. The 120-second target-journal PostgreSQL diagnostic
completed at 2026-11-19T12:37:48.497253Z with 20,522/20,522 correct operations,
arrival p99 74.715633 ms, valid generation and service checks, an independent
10,261-commit durable oracle, 16 successful same-process recovery operations,
and complete consumer/database/server release. The complete journal/receipt
audit is in `observations-before/db-target-journal-001/`; this is test-harness
validation, never a product performance gain. No repeat is required.

SQLite's final compact-v5-target calibration completed three passing 60-second
processes at 50/s, each 3,001/3,001, arrival p99
295.961647/219.822617/168.307978 ms. The policy-derived long rate is 40/s with
16 slots. Codec final004 completed three passing 60-second processes at
384/s, each 23,080/23,080; its long rate is 307/s with two workers. Exact
controllers and selections are retained under observations-before. Failed
higher points remain unchanged. Codec short comparisons remain their separately
declared 134/s one-worker and 268/s two-worker cells; they need their own
before-only noise and must use actual producer before-004.

The original PostgreSQL final-v5 controller is still live: its files progressed
during recovery, even though a new command's PID namespace cannot observe the
old process tree. It must not be duplicated or terminated based on that local
PID inventory. At this checkpoint it has 9 recorded cells and
controller state `running`. Wait for its immutable selection before the
next exclusive workload. The database Python controller itself covers only
SQLite/PostgreSQL; inspect for any further outer-shell activity before starting
the remaining final protocol calibration and before-only noise.

Current product/test commit is ce2a3c75cbd535490897d062b6cbb7c095408307. Runtime
implementation and native source still equal fixed main ea5fa528. The policy4,
A21, DB final driver, before codec producer and current kernel-boot hashes all
matched their recorded inputs on recovery. The historical A02 concurrent
Native AOT borrowed-resolver-handle failure remains unfixed baseline evidence.
`frozen-execution.json` remains pending; **0/10 long segments are credited**.
Do not restart completed calibration, claim optimization gains, merge, or publish
until the actual remaining comparisons, ten long segments and required gates pass.

### Execution checkpoint: final DB and codec selections; bounded protocol verification

The final database target journal and receipt projection are in product commit
ce2a3c75cbd535490897d062b6cbb7c095408307. Runtime C#/Rust still matches immutable
before main ea5fa528035d025bd7a28698ee7c71194432236c. The actual same-load
171/s, 120-second target diagnostic completed all 20,522 operations, with arrival
p99 74.715633 ms. Measured target RSS fell from 152,498,176 to 55,144,448 bytes
during load and from 181,960,704 to 78,344,192 bytes during sampled reconciliation;
the complete 42,562,221-byte receipt stayed equivalent. An independent full audit
matched every outcome and 389,918 counters. These are measurement-tool diagnostics,
not product optimization gains or long-duration credit. Actual targeted gates
passed 8 outcome-journal, 6 streaming and 15 common-verifier tests.

Final codec before-004 calibration selected 384 offered operations/s after three
23,080/23,080-success confirmations, with p99 110.590555, 116.248592 and
110.282025 ms. The paired long load is 307/s. Higher 512/448/416 points retained
18/8/3 rejected operations respectively. The complete compact calibration and
observed-versus-estimated memory audit are in observations-before/codec-final004-calibration/.

Final compact-v5-target database calibration finished both providers. SQLite
selected 50/s, with three 3,001-success confirmations and p99 295.961647,
219.822617 and 168.307978 ms; its paired long load is 40/s. PostgreSQL selected
180/s, with three 10,801-success confirmations and p99 155.462124, 120.373713 and
158.974390 ms; its paired long load is 144/s. The 200/s third PostgreSQL
confirmation failed the p99 limit, and all higher failed/invalid observations
remain unchanged. Selection completion was 2026-11-19T13:07:52.613515+00:00.
Before-only final-v5 noise extraction is next; earlier v4 bands/recipes are not
substituted for these final identities.

A source-proved protocol acceptance risk was fixed before long measurement:
sparse result histograms can exceed the old 64 MiB summary-reader limit. The
post-run verifier now streams its required metadata, hashes the entire original
file and preserves every original acceptance check. Independent review passed;
all 18 actual common-verifier tests passed at 2026-11-19T13:08:22Z. The final
verifier SHA is 3f5eec2ffa18d0622463bda571ffdfd063c500d5aa5169cc92273d185201de82.

Because DB timing imports and pins the earlier common parser file, root actually
created and verified a clean detached ce2a3c7 checkout at
ROOT/.worktree/Perf-01-frozen-drivers-linux/NativeWeave. Every later DB before,
after, direct-Rust and managed timed cell will use this same snapshot, retaining
reader SHA 8034692b643f4dbb1385cd61e25c9d4d6f084d7b71268fec02411b5c2fcdbeb4
and A21 SHA dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53.
The separately updated post-run verifier does not replace the timed parser.
Creation and exact hashes are recorded with the actual 18-test gate in
checks/protocol-result-verifier-001/.

Product ce2a3c7 CI run 44525871378 passed every job; Plan e223451 CI run
44523760735 passed. Local protocol-verifier and evidence changes await the next
push checkpoint. Final HTTP/gRPC calibration and short before-only noise still
follow. No C#/Rust runtime optimization has been applied. The final global freeze
is still absent and **0/10 long segments are credited**.

### Execution checkpoint: recovered DB final selection and protocol continuation

PostgreSQL compact-v5-target completed at 2026-11-19T13:07:52.613515+00:00. Its
200/s third confirmation failed the fixed tail limit (p99 850.807314 ms). The
predeclared step-down retained that failure and all earlier failures. The final
180/s confirmations each completed 10,801/10,801 correct operations, with arrival
p99 155.462124/120.373713/158.974390 ms. The paired long load is 144/s at16 slots.

The already-reviewed runbook extraction was actually executed against the final
SQLite/PG confirmation triplets. It verified original summary/frozen/dataset
hashes, complete normalized successful records, independent process identities,
nonoverlapping windows and equal configurations. New before-only noise receipts
are in `observations-before/{sqlite,postgresql}-final-v5-calibration/noise.json`.
The source-bound execution record is
`observations-before/database-final-noise-extraction-001.json`. Future formal
comparison triplets are fresh processes; these confirmations are not relabeled
as before comparison runs.

The resumed root started existing `protocol_calibrate.py` for HTTP then gRPC
using immutable before protocol-v2 server/common client, original TLS files,
policy4 and final A21 source. Current shell session is21557; output roots are
`ROOT/perf01-evidence/calibration/before-{http,grpc}-final-v5`, and the outer log
is `before-protocol-final-v5-controller.log` in the calibration directory. No
other workload or build may overlap; source-only work remains onCPU8. After
this controller completes, run the six protocol and two codec before-only noise
cohorts, then bind the immutable execution freeze before any runtime edits.

Product ce2a3c7 passed CI44525871378; recovered Plan bc5cb49 passed CI44528943177.
Both PR descriptions were updated and the SQLite final selection was read back
from GitHub. Neither CI run substitutes for candidate acceptance. Runtime still
matches ea5fa528, the final global freeze is absent, and **0/10 long segments
are credited**.

The two final DB before-only noise extractions actually passed at
2026-11-19T13:10:14–13:10:20Z using the immutable ce2 driver and original parser.
SQLite noise receipt SHA is c3cd91e963ff3390d58821487a628cf7c311d367f085eb63b13437fca034ec68;
PostgreSQL noise receipt SHA is 5bb25871bdd4863158f6b0aa0791b321b8ae147f122ec4ff9400c5b1106f7585.
The final protocol calibration began 2026-11-19T13:11:05.069792Z, session76449,
HTTP then gRPC under unchanged policy4, attemptv5. No other task loads/builds/tests
overlap; source-only CPU8 work is permitted. NativeWeave ab8357dd7e3d924e267f584056e5fba6d3a59265
is pushed and tree-equal to local verifier checkpoint824879e; its CI is pending.
Plan checkpointbc5cb49bd8cd21fff6e32053af25f73d6482a971 passed CI44528943177.

### Concurrent-session coordination checkpoint

At 2026-11-19T13:13:54.265612+00:00, the resumed turn in workspace c7a50ab71f57 detected another
active execution session updating the same product/Plan branches and attempting
protocol calibration (`before-http-v5`) while its own `before-http-final-v5`
controller held the shared timing lock. The resumed turn requested Ctrl-C for
session21557 and received exit130. Its last32/s cell has no final result and
receives zero credit; last resource output was13:11:07.345065Z. The original
controller file may still say running and is not proof of a live or accepted run.
The resumed turn stops launching workloads and avoids further product/branch
edits to let one integration owner continue. Full coordination details are in
`ROOT/perf01-run/recovery-session-coordination-20261119T1312.json`.

Completed DB/codec selections and new DB noise receipts remain available. Use
the existing clean ce2a3c7 frozen-driver checkout for future DB timed cells, as
their calibration source map pins verifier8034692b. The noise extraction read
the later3f5eec2f file, whose change affects only protocol post-run metadata;
no DB reader semantics or measurement values were changed. Do not relabel the
historical driver identity or rerun completed DB calibration unnecessarily.
Before any next load, the continuing owner must resolve current controller and
process ownership. **No runtime gain or long-segment acceptance is claimed.**

The first protocol v5 attempt stopped at 13:11:06Z before any application load:
the existing timing lock was held and run.py correctly rejected concurrent use.
The original lock was later acquired and released at 13:13:40.924060Z, unchanged
device/inode. The holder was not identifiable in the per-exec PID namespace; no
inheritance or product-defect attribution is made. No lock replacement/deletion
or process signal occurred. The failed zero-credit attempt and exact logs are
in checks/timing-lock-contention-001/. Fresh v5r1 began 13:14:33.288914Z in
session98397 with unchanged controller/driver/producer/profile inputs. At the
latest observation HTTP 8/16/32 offered requests/s passed and64/s was running.
Keep this invocation exclusive. Future DB and codec formal invocations will also
use the same existing resource lock through a standard outer flock guard; protocol
already owns that lock internally and must not be double-locked.

### Execution checkpoint: final protocol calibration and all protocol noise passed

Protocol v5r1 completed normally in session98397. HTTP selected 1,088/s after
three 65,390-success confirmations with p99 285.246995, 274.753607 and
280.616883 ms. Its capped paired long rate is 500/s. gRPC selected 160/s after
three 9,617-success confirmations with p99 154.982480, 153.711915 and
155.846419 ms; its paired long rate is 128/s. Exact selection/controller files
are in checks/protocol-{http,grpc}-v5r1-selection/. The complete five long rates
are PostgreSQL144, SQLite40, HTTP500, gRPC128 and codec307 logical operations/s.
These selections alone do not provide any long-duration credit.

The authorized post-calibration bounded extracts completed with exit0 before
starting another timed cell. HTTP controller sampled peak RSS was about103.9MB
at65,390 operations, gRPC about34.9MB at9,617 operations. The illustrative HTTP
901,051-operation scaling is about1.43GB, not a memory bound; postprocessing
peak and Python GC pauses remain unavailable. Server allocation snapshots are
explicitly server-only. No speculative protocol-retention change was made.
protocol-controller-memory-review.md records the source/measurement distinction.

Actual high-load gRPC classification is preserved:256/s had61 ResourceExhausted,
14 unexpected Cancelled and3 missing required Wait-header observations. Those
three calls received no response messages and recorded no underlying terminal
status; no payload/protobuf mismatch was observed.192/s and176/s had5 and2
ResourceExhausted outcomes. No invalid or service-failed point was relabeled.
protocol-grpc-failure-inspection.md binds exact operations and saved extraction
source. Plan local8678fc6 integrates these reviewed actual records.

The six ordinary protocol noise triplets completed successfully in session89255
at2026-11-19T13:55Z: all18 fresh cells were valid and met the service standard.
The completed noise index is ROOT/perf01-evidence/protocol-short/noise-before-001/noise-index.json,
SHA af9b4a68014c231fbc8c6b3e651a310045e155d83bd06d1bd9cbf4fe3b5bed20.
No extractor rerun or comparison-cell reuse is needed. Small exact receipt
copies and the final protocol long argv are being prepared for Plan.

Codec fixed-load before noise started at2026-11-19T13:56:09.428108Z, session32211,
W1 noise-1 at134/s for120 seconds plus separate20s warmup,10s recovery and5s idle.
It uses the reviewed exact argv and an outer nonblocking flock on the original
shared timing.lock. Its launch/result receipt is in
ROOT/perf01-evidence/noise/codec-before004-command-receipts/. Five more cells and
two existing extractor commands remain. Keep all other local loads/builds/tests
stopped; source/small-metadata work may useCPU8. The final global execution
freeze is still pending, runtime remains immutable main ea5fa528 and **0/10
long segments are credited**.

### Resumed integration checkpoint 2026-11-19T15:20:54.011987+00:00

The resumed root workspace c7a50ab71f57 now owns the single integration and timing queue. Shared Plan tracked files were unchanged and clean at3715d8e before integration. Archive commits411bd77/226f928/814b496 were fast-forwarded, and final-freeze proposal0692455 was applied as2d71265. Original untracked raw archive files and all prior failed/partial measurements were preserved. Coordination receipt: ROOT/perf01-run/resumed-integration-owner-20261119.json. Do not launch a second workload.

The r241 W2 remaining queue completed at2026-11-19T14:35:31.779294Z: all three processes succeeded16173/16173, final noise SHA749238affbb591e90f5f8801cf952b51e575222c227d8ed07d66b32ab404196b. W1 remains134/s with three16095/16095 processes. The predeclared stepdown selects192/s for the paired codec long group; the268/s failure and former384/s capacity/307/s proposal remain original history.

Archive transport is now actually verified at Plan commitde38d6ed6e8ff919d9263edffc2fdf29b3b2a8f9 on task/Perf-01-archive-readback-linux:14 remote files,10 restored raw files,23921929 bytes, all exact. Historical verifierfc179 reproduces the original rejection; this smoke has0 long credit. See checks/archive-readback-recovery-001/. Current archiver057e33d streams protocol control metadata and passed19 finite tests plus independent review; no timed driver changed.

Product remains ab8357d with runtime source unchanged from baseline ea5fa528. CI44530911423 attempt2 succeeded after the original APT network failure; that failure remains preserved. Five before long loads are HTTP500/s C64, gRPC128/s C64, PostgreSQL144/s C16, SQLite40/s C16, codec192/s W2. Finalize and publish the distinct immutable configuration next, then run all five before long groups before runtime edits. During each long window all other local work pauses except necessary supervision. All current long acceptance is0/10; no runtime improvement is claimed.

### Immutable configuration created 2026-11-19T15:27:09.191434+00:00

Final frozen-execution.json now binds the completed before noise, exact producers, timed sources, two integrated archive helpers and actual transport smoke readback. SHA-256: 85061c4e01b28fc72a5b20519ce2d8c01d79cae271238ba36e0a3465b0b8f4a3. Product runtime remains unchanged at baseline ea5fa528; current product head ab8357d contains harness/regression preparation only. All five before long groups must pass before runtime edits. The separate publication receipt must confirm fixed-commit remote byte readback before the first formal long command. No long credit is granted by this configuration.

### Before HTTP long accepted 2026-11-19T16:05:11.422894+00:00

Exact published freeze85061c4e at Plan4b0a5a78 passed CI44555266985 and fixed-commit byte readback. Supervisor session29388 completed successfully; raw HTTP output is ROOT/perf01-evidence/long/before/http-001. Independent verifier accepted1802.091185499 seconds,901051/901051 checks,856000 ordinary successes,45051 expected probes,arrival p99 260.565040ms. Recovery32/32 and final idle owner/request recession passed. Metadata and exact verifier are retained in checks/before-http-long-001/. Full raw archive publication is still pending. Next group is gRPC128/s C64 using the exact published selectors. Current acceptance1/10; no runtime edits. During the next long window all local work pauses except supervision.

### Before gRPC128 long rejected; prospective gRPC115 candidate 2026-11-19T16:50:03.764975+00:00

Session2681 completed230670 dispatches at128/s but had17 rejected,5 unexpected cancelled and1 required Wait-header failure. Exact post-run verifier rejected the valid flag and grants0 seconds. Raw output ROOT/perf01-evidence/long/before/grpc-001 and original supervisor receipt remain unchanged. checks/grpc-before-long-failed-operations-001/ contains complete joined23 failure evidence, verifier and bounded extraction receipt. All errors were in the first403.205s; no payload/protobuf content mismatch was recorded. No quota-cause attribution is made. Recovery32/32 and final zero owner/request gauges passed, which does not rescue the failed segment.

A separate prospective amendment freezes one new115/s gRPC candidate,207243 planned calls over1802s+C64, with all other inputs/limits unchanged. It applies identically to final after; originalfreeze85061c4e remains immutable. Amendment SHA b784cfbc97e65c2b4e1932b4347c66a96d86005773064e95be76345b33381c43. Publish/readback before execution. If this candidate fails, stop rate-only selection and analyze the cause; do not repeat until lucky. HTTP remains accepted, total1/10. Next after a passing gRPC candidate is originalPostgreSQL144,SQLite40,codec192. No product runtime edits.

### Pre-execution gRPC supervision correction 2026-11-19T16:54:19.762029+00:00

Publishedamendment001 at c90f982c was not executed. Independent review found the supervisor must keep any actual outer-driver nonzero exit disqualifying even if the domain verifier could pass a finalized result. New immutable amendment002 supersedes001 only for this supervisor binding; original001 and parent85061 remain unchanged. Corrected supervisor additionally requires all actual command exit codes0, otherwise credit0. No timed driver,rate115,case orresource limit changes and no extra attempt is granted. New amendment SHA 2c4d5a0a00cf2f763e4641043f7d6908319ea4d3e7fdbaf2760039bc6808b513. Publish/readback before launch; totalaccepted remains1/10.

### Before gRPC115 long accepted 2026-11-19T17:31:04.611523+00:00

The unique amendment002 candidate completed successfully in session38750. All three actual commands exited0, and the independent verifier accepted1802.101046909 effective seconds. Dispatch timestamps were2026-11-19T16:57:34.317798Z to17:27:36.421953Z. All207243 checks succeeded:196880 ordinary business calls plus4145 expected cancellation and6218 deadline checks. Arrival p99152.456566ms, ordinary throughput109.2462153101036/s, server CPU45.9817113089409%of one core, sampled RSS peak115073024B. Recovery32/32,60s idle and final zero request/owner gauges passed. Exact control copies and per-scenario message/byte summaries are in checks/before-grpc-long-002/. Complete raw archive publication/readback remains pending.

The 128/s failure stays rejected with0 credit, amendment001 stays unexecuted, and adopted002 SHA2c4d5a0a remains immutable. Its published Plan head e2683c13 passed CI44571766325; root read the actual successful run. Product runtime still equals baseline ea5fa528. Current acceptance2/10. Next is PostgreSQL144/s C16 under the original published freeze and ce2a3c7 timed-driver checkout, followed by SQLite40 and codec192. All other local work pauses during each formal long window except necessary supervision.

### Before PostgreSQL long invalid: dispatch delay 2026-11-19T18:21:47.546225+00:00

Original supervisor session4824 ended2026-11-19T18:10:40.759738Z with outer driver exit1. The immutable before PostgreSQL144/s C16 segment completed259526/259526 target operations, with129763 typed pages and129763 durable business cycles. Independent persistence matched129763 measurement commits; recovery32/32 and final resource release passed. Arrival p99104.185227ms; measured service CPU1309.32s and sampled RSS peak58556416B. These product observations do not rescue generator validity.

The sole summary invalid reason is generator saturation: dispatch lag. Actual full-stream audit found52 dispatches exceeding the unchanged100ms gate, clustered at IDs30352-30370 and148071-148103, approximately210.778s and1028.271s into load. Max lag326.111321ms. All operations eventually succeeded. Existing1Hz process samples do not establish whether these subsecond pauses were PythonGC, host scheduling or other generator work; no causal claim is made. The raw output ROOT/perf01-evidence/long/before/postgresql-001 remains unchanged. Summary SHA e8433d3af096b45ae7d4d5ab01bd5b345a92f053d0d7792db9e517d5bf476f4d.

Root executed the exact frozen post-run verifier separately at18:13:47Z; it exited1 and rejected valid=false, credit0. Verifier receipt SHA1c1f69590dd0c3d0ac8a1dde88709922f6c9df8dd645bc232e825606686e0959. This early rejection does not claim that later verifier gates ran. Original supervisor remains failed. Accepted long groups remain2/10; invalid groups are original gRPC128 and this PostgreSQL144. No runtime edits.

Read-only audit and failed evidence extraction are assigned to task/Perf-01-db-generator-linux, an independent Plan worktree. A separate diagnostic helper is being prepared in task/Perf-01-db-profile-linux to record actual Python generator GC start/stop times without altering frozen A21/DB source or product packages. No diagnostic load has started. Before another formal group, determine the pause cause and freeze any necessary driver-only amendment prospectively; preserve the original failure and unchanged service/resource/dispatch gates. The already accepted HTTP and gRPC115 binaries/cases/configurations stay reusable.

### Generator GC diagnostic prepared 2026-11-19T18:38:31.256501+00:00

The minimal three-file helper was integrated from afc19c4a after two independent source reviews. Actual prepare exited0 and produced configuration SHA550bbeadb7f58424a4d8fcb377783ba8bc186fa542bfab2d9ddf059997e1395a at ROOT/perf01-evidence/profile/postgresql-generator-gc-001/configuration.json; exact copy and review are in checks/postgresql-generator-gc-001/. It retains the full1802s144/s C16 plan and before package, observes only the actual scheduler/target Python GC callbacks, and changes no GC policy or frozen source. Root will run it exclusively and stop after a relevant observed measured-phase Gen2 pause or360s effective observation. Stop uses the existing control.json TERM/KILL path; partial output has0 formal credit and may lack the final dispatch ledger. No diagnostic workload has started as of this prepared checkpoint.

### Generator GC diagnostic completed; DB-only remedy under review 2026-11-19T19:12:20.108635+00:00

The bounded diagnostic actually ran from2026-11-19T18:40:28.447650Z and was intentionally stopped after the measured scheduler Gen2 observation. The raw first event is45067971164323ns and the actual stop helper clock45340558962654ns, giving272.587798331s; an earlier manual-monitor sample reported272.090073947s. Incremental volatile monitor arrays were unavailable at persistence and are not represented as evidence. Original raw GC/event/control files remain authoritative.

Independent analysis7394f2be, integrated as55a1d87, records a scheduler Gen2 interval240.004324ms after excluding its177688ns start hook, with236.181418ms process CPU. It lies inside a243.210043ms adjacent raw event observation gap, with zero observations during GC and16 consecutive admissions in the first10ms after resumption. This is observed correlation, not an exact final dispatch ledger or proof of both original uninstrumented failure clusters. Target measured Gen2 maximum was37.866763ms. See checks/postgresql-generator-gc-001/analysis-001/.

Actual outer driver exit1 and supervisor cleanup left no live owned processes; no PostgreSQL postmaster.pid remained. This forced cleanup is not graceful native retirement. The unchanged long verifier actually ran at18:59:51Z, exited1 and rejected profiling-only evidence; verifier SHAabcc35b25a0f7278d2b9fb1b8d6798e303a8b7589f98cca1bcf9a282bafbd80c. The diagnostic has0 duration credit. Accepted long groups remain2/10; product runtime remains unchanged.

A separate DB-local wrapper candidate defers automatic cyclic GC only around the original scheduler worker, leaves refcount cleanup and target/application GC unchanged, and records the actual policy/PID/source/restoration result. It is under independent review; no candidate load has run. A same-before-package120s automatic/deferred pair is a semantic and resource check only, not long acceptance. Any adopted DB policy requires prospective driver/controller/configuration bindings and fresh matching DB noise/capacity cells, preserving old automatic-policy failures. Common A21/protocol/codec sources remain unchanged so accepted protocol longs stay reusable.

Complete raw HTTP and gRPC archives have passed local streaming full-file/shard verification with final4MiB raw shards and compressed blobs below1000000B; PostgreSQL archive preparation is in progress under timing.lock. Full raw remote publication/readback is pending. Do not delete originals or start another timing window while archive CPU work holds the lock.
