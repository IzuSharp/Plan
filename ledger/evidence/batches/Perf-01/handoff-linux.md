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
