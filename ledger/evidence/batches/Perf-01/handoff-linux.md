# Perf-01 Linux x64 handoff

## Current state

Status: source baseline frozen; execution environment and reusable measurement drivers in preparation. No product optimization has been applied. No performance improvement is claimed. No Perf-01 timed segment has started.

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

The execution host is Linux x64 / Debian 13. A retained `.NET SDK 11.0.100` is available under `ROOT/../58d2a6adf1c3/dotnet-sdk`. The exact Rust 1.100.0 toolchain and PostgreSQL 18.0 are being prepared under `ROOT/perf01-toolchain`; their successful installation/build is not yet claimed. No remote Linux host tool is exposed in the current session. GitHub read access and source checkout succeeded.

## Package and scope cautions

B24 normally preserves eight COMMON packages between its own previous/candidate pair. Perf-01 shared implementation changes must instead reconstruct a fresh complete closure for each tested product version and verify every loaded managed/native identity. Reusing an old common package would invalidate an affected optimization result.

The current gRPC implementation supports identity compression only. Independent A17 codec performance is separate from negotiated network compression. Public domain package publication remains a separate task; the existing normal HelloWorld preview flow is checked after an accepted merge. The 24h/72h stages remain deferred.

## Durable evidence and resume

`baseline-source.json` binds the starting source and lock files. English source analyses and frozen executable profiles are added here as work completes. Only authorized synthetic project samples and allowlisted host metadata may be uploaded; keys, credentials, database contents and unrelated data stay out of evidence. No old rejected publication is retried by this task.

Resume by checking this handoff, existing Perf-01 branches/PRs and exact segment receipts. Reuse only completed segments whose binaries, cases and configuration match the reported version. At this checkpoint no PR, product change, passed test, successful profiling run, timed segment, merge or preview is claimed.
