# DB-Exec-Parity-01 — lease-b count, implementation and correctness receipt

Status: **isolated candidate available for ordinary interleaved A/B; no CPU,
latency, allocation, parity, mixed-campaign or release acceptance**.

## Measured mechanism

The independent baseline diagnostic is commit
`3cc32843c797b7fd8807e1c8d9e8dfa32fd7a613`, based on product
`7ff7b57b907b689defb880b8af62d83679608603`. It adds managed lease markers only,
not an execution optimization. Its two exact independent provider packages and
actual Native AOT generated-reader consumers are recorded under
`builds/lease-b-diagnostic-{sqlite,postgresql}` and
`consumers/lease-b-diagnostic-{sqlite,postgresql}`.

`analysis/lease-b-count-gate.json` validates 10 provider/case combinations and
150 sequential business queries. Every marker was retained; dropped and
inflight-at-finish counts were zero. The actual request markers, cursor IDs and
generation markers establish the following identical results for both providers:

| Business | Rows materialized | Batches attached | EndRead calls | Actual Release(0) calls immediately after EndRead | Nonzero native-owner releases |
| --- | ---: | ---: | ---: | ---: | ---: |
| Single row | 1 | 1 | 2 | 2 | 1 |
| Exact batch of 32 | 32 | 2 | 34 | 34 | 2 |
| 100 rows | 100 | 4 | 104 | 104 | 4 |
| 1,000 rows | 1,000 | 32 | 1,032 | 1,032 | 32 |
| 1,000-row query, stop after first row | 1 | 1 | 2 | 2 | 1 |

Each attached batch performs one validation borrow; each materialized row adds
one row borrow. EndRead and its immediate same-thread actual zero-owner Release
pair match the sum. The raw records include TID, monotonic clocks and thread CPU,
but these heavily instrumented runs receive **count/ordering credit only**.
Additional zero-owner Release calls from closure remain separate from the
EndRead pairs and are retained in per-request results. FFI release count is not
reduced by this candidate: the avoided Release(0) never invoked native release.

Raw per-case receipts, command/resource records and sampler records are under
`measurements/lease-b-count-01/{sqlite,postgresql}`. These runs use the existing
diagnostic query consumer with per-route warmup reduced to two; all queried
values and full/early-stop result checks remain explicit. This is not the
ordinary mixed workload and has no final-campaign credit.

## Ordinary implementation and machine code

Candidate commit: `06ca0cbd6226f978b0c2080981b4dbc2019e22e0`, branch
`task/DB-Exec-Parity-01-lease-b-candidate`, one changed product file:
`src/Data.Streaming/StreamTransport.cs`.

Only EndRead's final call changes to `if (release != 0) Release(release);`.
ReleaseBatch, Close and Release remain unchanged. Active storage or another
reader retains retirement responsibility; the last inactive reader or the
concurrent Close/Dispose still detaches the owner and executes the normal
physical release/finalizer-suppression path. In particular, the zero-owner
Release path remains available to Close/ReleaseBatch.

`analysis/lease-b-machine-01/identity.json` binds both providers' ordinary
baseline/candidate ELF and corresponding debug files to actual disassembly and
matching LLVM 23 symbol/source lookup. No ordinary candidate ELF contains the
diagnostic observer symbol. Baseline EndRead unconditionally jumps to Release;
candidate EndRead tests the release pointer and returns directly on zero. The
SQLite ordinary candidate's zero test is at `0xac94a`, the direct return at
`0xac957`; nonzero still jumps to Release. EndRead grows from 179 to 193 bytes;
Release stays 264 bytes. Code size is not interpreted as execution cost.

## Actual independent packages and consumers

Both packages use exact version `0.1.0-db-exec-parity-lease-b.1`, canonical
bundling and PackageReference-only Release Native AOT consumers. Unchanged
locked native assets are reused only after every recorded input and asset hash
matches; package closure verification remains active.

| Provider | Package SHA-256 | Phase ELF SHA-256 | Mixed-workload ELF SHA-256 |
| --- | --- | --- | --- |
| SQLite | `e2475ac08b878e1236ab8a1c963d0468719f176e659ea06a6841d52267c0f072` | `bc93a7d12713876d0b6e22617ac38f6cd7e43ce25814f5377e41aa9a9b1bdebc` | `59f7dd6725d1fbdaf51b296cd725bd97100fa398231f2d88ae22d5c649f71ad9` |
| PostgreSQL | `cdbdf3883a68dffb0e81d0cda0592d4223c05a5c732cad089326ec9f19b3177e` | `1f11e93fc3d5438e3a7c2d15ad90a833ae7c843490624855747ce4ff837ef89a` | `aed03538a28bb0fe6b1a7a0b9bd1d8f370b8b03b3f2bd082fb176235f8dce723` |

Ordinary consumer roots are `consumers/lease-b-{sqlite,postgresql}`; each contains
`korda-query-phases` and `korda-workload`. Receipts retain generated C#, actual
ELF/debug/native assets, restored graph, package identity and build commands.
Only reproducible consumer bin/obj intermediates were retired, after copied
generated sources/assets and output hashes were retained in the build receipt.

## Correctness and preserved failed attempt

`builds/lease-b-streaming-correctness-02/receipt.json` records actual Release
Native AOT execution of the existing focused tests:

- Stable scoped native owner: 30 assertions.
- Row lease reuse: 364 assertions.
- Borrowed native batch lifetime/validation: 19 assertions.
- Active-move join races: 118 assertions.

Coverage includes nested scopes, old-generation rejection, last-reader native
release, permanent Close, mapper self-disposal, forced GC, simultaneous
disposers, reentrant MoveNext rejection, malformed batches and original versus
cleanup exception ordering. These 531 assertions passed. No allocation probe
or performance program is invoked by this correctness helper.

Attempt 01 remains in `builds/lease-b-streaming-correctness`: `dotnet restore -r`
selected RuntimeIdentifiers, while this test project selects its AOT lock using
singular RuntimeIdentifier. NU1004 correctly rejected the ordinary lock. The
second helper uses explicit `-p:RuntimeIdentifier=linux-x64`, keeps the original
AOT lock and the project's existing version, and passes locked restore. No
lockfile or product rule was changed and no force-evaluate/unlocked restore was
used. Original attempt script/logs/receipt are retained.

## Routing and remaining work

`diagnostics/lease-b/candidate-impact.json` and each ordinary package's
`committed-impact.json` select `linux`, `postgresql`, `sqlite`, with both
independent provider public checks. The sole ownership reason is the shared
Data.Streaming source. No interop edit, benchmark action, workflow change or
performance CI entry is added. The root task still owns full selected checks,
ordinary same-host interleaved A/B, candidate selection/integration, final mixed
campaign and normal review/merge/release verification.

Independent source review by the recovery/CI agent found no ownership or
finalizer blocker and specifically confirmed that preserving Close and
ReleaseBatch's zero-owner Release behavior is necessary. That review does not
replace actual tests or the remaining A/B.

`analysis/lease-b-candidate-identity.json` binds the patch, source identity,
diagnostic count gate, machine evidence, package builds and both correctness
attempts. Product candidate worktree remains clean. The original Korda task
worktree, Plan, Design and both Go drafts are unchanged by this experiment.
