# DB-Go-01 local cleanup inventory

Observed: 2026-11-26T12:39:07.925963+00:00.

This is a read-only preparation inventory. This agent performed no deletion, build, workload, or GitHub mutation. The root agent may separately remove the specifically inventoried rebuildable caches to make room for the Go SDK; its receipt is authoritative for that action.

## Scope and timing

The user authorized final removal of all local task-related directories, worktrees, and caches after the Go SQLite and PostgreSQL 30-minute measurements, result reporting, and durable evidence readback. Final cleanup must wait for those conditions. New Go worktrees and files created after this snapshot require a short final refresh.

| Exact task root | Contents |
|---|---|
| `/workspace/scratch/4a65d70f0fe1` | Historical DB-Exec repositories, worktrees, local compiler/database tools, consumers, and measurements |
| `/workspace/scratch/fd78534029f7` | Continuation implementation/design/Plan worktrees, native/AOT builds, frozen measurements and validation |
| `/workspace/scratch/166b48a091b9` | Final prior delivery/archive receipts plus current Go comparison source, toolchain, caches and evidence |

The inventory contains **60 registered historical worktrees**: Korda 51, Korda-Design 4, and Plan 5. Their owning bare repositories are under `/workspace/scratch/4a65d70f0fe1/repos`. Exact worktree and temporary paths are in `cleanup-inventory.json`; do not use an unrestricted wildcard against `/tmp` or `/workspace/scratch`.

## Publication and untracked-work check

| Repository | Public merged commit | Final local tree |
|---|---|---|
| IzuSharp/Korda | `7ff7b57b907b689defb880b8af62d83679608603` | `bc9087d843d8d741d83d44f53d0b2c5af26dcffc` |
| IzuSharp/Korda-Design | `ca9348ad0b5cc93bc75c502460d8e1b75843d109` | `ffe6f94306985bacde708e75d1e93a29e096c724` |
| IzuSharp/Plan | `03efe57ffbe3046bd89919ddb2c16c90a377954d` | `56dbe91bfbf0732863d0f65630bbee872ef22045` |

The local final trees match the published trees. Local commit SHA values differ from public commit values because publication preserved tree content through Git Data API commits. The completed-delivery receipt records all three merged PRs and successful existing main checks. The Plan final raw measurement archive is 9,895,505 bytes, with SHA-256 `a2163d52068b9fb062b140339b183c3626c2e8ad935c3ee2f75b35f9ef2c95bb`.

Only the old Plan worktree had untracked entries: three status items containing 32 files. Every file is byte-identical to a tracked file at the same relative path in the final Plan tree. `untracked-evidence-check.json` records the hashes and comparisons. No unique untracked work was found. A clean worktree is not, by itself, proof that every old local experiment commit was published; final-tree equality and evidence receipts are the actual publication checks.

Prior archives explicitly exclude build binaries, package caches, and database data directories. Cleanup must not be reported as lossless retention of those binary bytes.

## Keep until both Go measurements and archival finish

- `/workspace/scratch/4a65d70f0fe1/consumers/direct-native/libsqlite3.so`: Exact SQLite 3.51.3 shared library required by Go cgo comparator.
- `/workspace/scratch/4a65d70f0fe1/tools/native-dependencies/sqlite/sqlite-amalgamation-3510300/sqlite3.h`: Matching SQLite 3.51.3 header.
- `/workspace/scratch/4a65d70f0fe1/tools/postgres/install`: Same PostgreSQL 18.0 server/client installation as the frozen baseline.
- `/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-korda/benchmarks/db-perf`: Frozen runner, SQL/workload manifest and correctness oracle source.
- `/workspace/scratch/fd78534029f7/measurements`: Original frozen workload settings, prior raw outcomes and current comparison inputs.
- `/workspace/scratch/166b48a091b9/recovery`: Prior completed campaign analysis and archive provenance.
- `/workspace/scratch/166b48a091b9/go-comparison-01`: Current Go source/build/runtime/cache/result files remain live until final evidence publication and review.

The new Go SDK, module cache, build cache, temporary compiler directory, GOPATH, and dependency seed are all scoped beneath `/workspace/scratch/166b48a091b9/go-comparison-01/toolchain`. The environment agent confirmed that no shared HOME/system caches are used. The installed system GCC and shared platform runtimes are outside the cleanup scope.

## Early space recovery candidates

The three old LLVM/CMake/.NET download archives were separately removed by the root agent after confirmation that they were already extracted and unused by Go. See `early-cache-cleanup.json`; do not repeat that deletion or claim the compressed bytes were part of the published raw measurement archive.

`cache-reclaim-candidates.json` lists 12 rebuildable `bin`, `obj`, `packages`, and `offline-feed` directories inside the four old allocation/FFI diagnostic consumer directories. Their observed allocated size was **1,275,609,088 bytes** at 2026-11-26T12:35:40.186216+00:00. Removing only these children preserves diagnostic sources, generated source snapshots, patches, logs, receipts, manifests, and `out` binaries. The Go environment agent confirmed none are reused by Go.

Filesystem free space must be measured after actual deletion. Overlay storage accounting and concurrent SDK extraction mean the sum of cache file sizes does not guarantee the same free-space increase.

## Final cleanup order

1. Both requested Go timed cells are complete, business/count assertions are checked, and final results plus failure records are reported.
2. Go implementation, exact versions, measurement raw data, source/binary identities, comparison report and this cleanup inventory are durably archived and read back.
3. Refresh new/changed worktrees and reserve any unpublished edits before removal; do not infer archive coverage solely from clean git status.
4. All task-owned benchmark and PostgreSQL processes are stopped; never terminate platform PIDs 1, 2 or 5 on the basis of their working directory.
5. Remove exact registered worktrees using the owning bare repository while it still exists, then remove task-owned bare repos/tool/cache/build/data roots.
6. Remove old task roots and exact known /tmp paths; process the current task workspace contents last from a safe external cwd, keeping the framework usable.
7. Save a final cleanup receipt outside the soon-to-be-deleted roots or publish it directly, including actually removed paths, missing paths, retained shared infrastructure and observed free-space change.

## Shared resources that must remain

- `/opt/codex`, `/usr`, `/usr/local`, unrelated task roots, unrelated temporary files, shared HOME caches/configuration, and credential material remain outside this task.
- Platform processes with observed PIDs 1, 2, and 5 use the current workspace as cwd. They are framework processes, not benchmark leftovers. Never terminate them because of that cwd.
- Keep the framework working directory usable. Remove the current task-owned contents last from an external cwd; an empty platform workspace leaf may remain if the execution framework depends on it.

No deletion was performed by this inventory agent.
