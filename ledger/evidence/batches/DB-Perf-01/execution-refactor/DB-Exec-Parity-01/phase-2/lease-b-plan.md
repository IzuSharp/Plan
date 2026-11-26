# DB-Exec-Parity-01 — lease-b isolated causal experiment

Status: diagnostic preparation only. No candidate or performance acceptance.

## Source and actual machine-code evidence

Base product is `7ff7b57b907b689defb880b8af62d83679608603`. The independently
reviewed source is `src/Data.Streaming/StreamTransport.cs`:
`ScopedBatchRead.Dispose` calls `ScopedStreamBatch.EndRead`; the latter drops
its read count under `_gate` and unconditionally calls `Release(release)`.
Ordinary active-batch reads have `release == 0`, but `Release(0)` enters the
same `_gate` again to check finalizer suppression.

`analysis/sqlite-read-release-review-01/identity.json` binds baseline actual ELF
SHA-256 `76be826f4ffb7585eff7a0037d1850ead6907403f4f41b1874916e76cbfe7f87`
and debug SHA-256 `9c6c3d9b0fb4213a956e7a14a0e93edd3cee6e9a468594134ba272ec543244c7`.
`EndRead` at `0xac8c0` (179 bytes) unconditionally tail-jumps to `Release` at
`0xac980` (264 bytes); its zero-owner branch retains Monitor.Enter/Exit. The
existing leaf samples lack caller chains, so they do not assign inclusive CPU
or contention to this call.

## Hypothesis and prospective count gate

Hypothesis: skipping `Release(0)` *only from EndRead* removes one unnecessary
managed Monitor pair per successful synchronous read scope without changing
generation admission, logical liveness or physical native storage retirement.
No CPU, latency or allocation improvement is assumed.

The diagnostic baseline will count native-owner cursor ID, generation/batch,
validation reads, row-materialization reads, EndRead calls and the disposition
of each release argument. Existing sampler markers supply monotonic time, TID
and thread CPU; diagnostic runs receive count/ordering credit only. The normal
successful full-consumption count model is EndRead = result rows + batches,
including terminal empty batches. At batch capacity 32, rows 1/32/100/1000
predict 2/34/104/1032. Early stop is distinct. These numbers remain predictions
until actual markers and result checks agree with them.

Only after the diagnostic count gate passes may the candidate change the last
line of EndRead to `if (release != 0) Release(release);`. No other execution
change is part of this candidate. The ordinary candidate contains no observer.

## Lifetime argument and correctness

When EndRead observes zero release under `_gate`, either the generation is
still active or other readers remain. Later Close/Dispose owns its normal
release/suppression path, or the last remaining reader detaches and releases.
The nonzero owner still runs Release and its existing `_releasing`, KeepAlive
and finalizer logic. ReleaseBatch/Close/Release themselves remain unchanged.

Retain Native AOT correctness in Data.Streaming: StableBatchTests (nested reads,
permanent Close, reuse/generation, once-only release), RowLeaseReuseChecks
(inactive rejection, mapper self-disposal, malformed later batch, reentrancy),
AllocationProbeRaces (concurrent disposal, forced GC, mapper/cleanup exception
ordering, cancellation and delayed ValueTask consumption). Both real public
provider packages and actual generated-reader consumers are required.

## Identities and local execution

- Diagnostic worktree/branch: `Korda-lease-b-diagnostic` /
  `task/DB-Exec-Parity-01-lease-b-diagnostic`.
- Candidate worktree/branch: `Korda-lease-b-candidate` /
  `task/DB-Exec-Parity-01-lease-b-candidate`.
- Diagnostic package version: `0.1.0-db-exec-parity-lease-b-diagnostic.1`.
- Ordinary candidate package version: `0.1.0-db-exec-parity-lease-b.1`.
- Ordinary consumers: `consumers/lease-b-{sqlite,postgresql}`.
- Diagnostic consumers: `consumers/lease-b-diagnostic-{sqlite,postgresql}`.

Native input hashes must match the existing locked baseline manifests before
native ELF reuse. Producer packages remain the independent canonical SQLite and
PostgreSQL top-level packages; consumers use PackageReference only. Preserve
source/commit/tree, package, actual generated C#, ELF/debug/native hashes and
commands. Do not modify Korda's main task worktree, Plan, Design, Go drafts or CI.

Builds wait for the root agent's disk/measurement-lane release. Instrumented
counts may overlap builds only with explicit no timing credit. Ordinary A/B
and final measurements are root-serialized with no overlapping builds.
