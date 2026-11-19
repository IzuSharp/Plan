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
