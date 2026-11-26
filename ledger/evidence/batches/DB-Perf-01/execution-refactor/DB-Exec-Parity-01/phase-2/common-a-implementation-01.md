# DB-Exec-Parity-01 — common completion candidate A

Status: **causal candidate; no measured performance claim and no merge/release credit**.
Stage 1 was recorded before product edits in Plan `da20dc395ca44a0430f933aeb7a45a3ee13aa447`
(the parent's reconciled remote receipt is `d463730`, with the same gate tree), and the
adopted experiment was recorded in Design `8a6d967` (remote PR21 `da15cf2`).
The product baseline is `7ff7b57b907b689defb880b8af62d83679608603`.

## Exact implementation and scope

The isolated branch is `task/DB-Exec-Parity-01-common-a`, worktree
`worktrees/Korda-common-a`. Initial implementation is `702d228`; frozen candidate
is **`8ac1be5caa2d8d2c3d501da3bec3361f9f1dd1c2`**, which adds the repeated held-publisher
regression and documents the resource scope. The native engine, runtime settings,
batch limits, SQL, DTO generation, public API, dependency pins, CI and original
acceptance workloads are unchanged.

`CoordinatedCallback.Execute` now owns a stack-local immutable
`CallbackPublication`. Its fields bind the publisher, generation, MRVTS version,
result reference and chosen exception. Processing may prepare that value, but it
cannot publish through a mutable shared pending field. The coordinator first
finishes its dirty/scheduled bookkeeping and any already-required scheduling
offer. It then invokes the local value outside the `SchedulingFault` catch and
outside the bookkeeping `finally`.

`HostPullController.Process` retains its existing setup, acceptance, registration
drain, callback-entry, control, native take and ownership conditions. It frees the
root and cleanup slot, seals `_published`, chooses any test-observer failure and
prepares the local publication. The explicit publisher verifies the captured
generation/version before its final setter. No controller read, state update,
cleanup or observer follows either MRVTS setter. The unreserved setup-failure
`Resume` path has the same final publication boundary.

Only after this separation is the pull MRVTS asynchronous-continuation flag
removed. Native `OnReady` still records readiness and queues the managed
coordinator. It never runs the setter or user mapper. Pre-registered continuations
with no captured scheduler can execute on the coordinator thread; captured
contexts/task schedulers retain the runtime's dispatch behavior, and registration
after completion retains the runtime's queued path. The same-ELF runtime source
and machine-code evidence in `native-sampler-findings-01.md` defines these cases.

The other callback subclasses only adopt the `Process(ref CallbackPublication)`
signature and leave the publication empty. Their result completion policies are
unchanged. Touched files are:

- `src/Interop.Callbacks/CallbackCoordinator.cs`
- `src/Interop.Callbacks/CallbackRegistration.cs`
- `src/Interop.Async/AsyncOperation.cs`
- `src/Verification.Interop/RaceSuite.cs`
- `src/Data.NativeHost/HostPullController.cs`
- `src/Data.NativeHost/HostCommandController.cs`
- `src/Data.NativeHost/HostCursorCloseController.cs`
- `tests/Data.NativeHost/Program.cs`
- `tests/Data.NativeHost/ReadySchedulingTests.cs`

## Publication exceptions and resource limits

MRVTS completion becomes observable before it invokes a continuation or calls a
captured `SynchronizationContext.Post`. That user-controlled operation can consume
the old result, start a new generation and then throw. The candidate lets this
exception follow the managed executor's exception boundary. It does not report a
second provider error, call `SchedulingFault`, poison the source, dispose an
already-delivered batch, retry completion, swallow dispatch failure, or add a
direct `FailFast` policy. Controlled test executors observe the exact exception.
The runtime's normal treatment of an unhandled custom continuation exception is
not changed or claimed recoverable by the library.

The coordinator bounds one admitted processing turn and uses one reusable work
item per context. It **does not bound live stacks or threads held by arbitrary
user continuation/`Post` implementations**. Clearing processing ownership before
publication allows a later generation to finish while an earlier retired
publisher is still inside `Post`. The new regression deliberately holds four
such publisher frames, verifies four independent results with no queued drain or
old resource reservation, releases every frame, and verifies the next generation
and final native owner counts. This is a bounded correctness observation, not a
proof of a finite resource limit for unlimited user blocking. Sustained workload
fairness, peak/released RSS and client CPU remain acceptance work.

## Correctness evidence collected so far

The first `702d228` Native AOT build and complete real SQLite/PostgreSQL
`Data.NativeHost` executable passed. Its retained directory is
`builds/common-a/correctness/nativehost-01`; it is not relabeled as the final
candidate after the additional regression.

The frozen `8ac1be5` Native AOT executable was rebuilt with SDK11.0.100 and
ILCompiler11.0.0. Its complete two-provider suite passed, including:

- Existing early-ready/setup overlap, rejection/retry and native callback tails.
- Same batch owner, one-shot/stale result rejection, held synchronous read scopes,
  setup/take/publication fault precedence, rejected unreserved setup drains and
  concurrent Stop failures.
- Actual borrowed mapper cancellation/dispose/close/error cases, exact batch/EOF
  counts, transactions, cursor close and command completion regressions.
- New no-context inline continuation, registered ExecutionContext restoration,
  next-generation completion while the old continuation is held, and an exception
  thrown after old-result consumption.
- Captured `Post` throwing before dispatch or after synchronous consumption and
  next-request creation; registration after completion; four repeated held
  publisher frames with eventual complete release.

Each provider reports ten ready-scheduling scenarios and187 assertions. The
complete B04 suite reports438 assertions and36 independently observed managed
retirements, with final source/session/operation/cursor/buffer/handle/pull/command
counts zero. The authoritative command, ELF, source, log hashes and actual exit0
are in `builds/common-a/correctness/nativehost-02/full/run-receipt.json` and its
bound build receipt. These are correctness runs, not performance evidence.

### Deliberate baseline negative control

`worktrees/Korda-common-negative` is a separate branch from the exact baseline.
Its commit `f4bf5d0d7dcb8fd004690f8e9ebf50ddbe9cbc0d` changes only the two test
files; product sources remain baseline bytes. It runs only
`--pull-publication-failure-only`, avoiding a claim that candidate-specific
inlining assertions should pass against the asynchronous baseline.

The actual baseline AOT executable failed with the expected assertion:
`Post's exact failure escapes the managed executor once; it is not translated into SchedulingFault.`
The ordinary runner observed exit250 after the child exception. This negative
control demonstrates that the test distinguishes the original post-sentinel
exception boundary from the candidate. It is **not** a successful baseline
correctness run or a performance result. Evidence:
`builds/common-a/correctness/baseline-negative-01/dispatch-negative/run-receipt.json`.

## Committed impact and independent package inputs

After each candidate commit, `python3 eng/ci/impact.py origin/main --output
artifacts/plan.json` was run against the committed diff. The final plan selects
only C# changes and explains their ownership in its `reasons` field. It selects
Interop.Async/Callbacks, shared database build/API/dependency/property/regression
checks, and **separate SQLite and PostgreSQL** build/pack/packed-API/provider-test/
AOT-consume/metadata validation groups. No performance action is introduced or
invoked by CI.

Two independent clean producer worktrees at `8ac1be5` build
`Korda.Database.Sqlite.0.1.0-db-exec-parity-common-a.1.nupkg` and
`Korda.Database.PostgreSql.0.1.0-db-exec-parity-common-a.1.nupkg`. Local packaging
plans retain the committed plan verbatim except for the explicit per-provider
candidate version; derivation hashes are recorded. Native images are the exact
ordinary baseline images. All120 recorded source/profile input hashes per
provider match the candidate, and the real package inventory checks their
commands, archives, dependency pins, asset copies and ELF contract. The packages
retain the native producer's original commit and record the candidate packaging
producer separately.

The ordinary external consumer builder creates no ProjectReference. Each
provider's phase and original35-case mixed consumer restores only its own exact
public Korda package and compiles a real standalone Release Native AOT ELF. The
four original consumer source/manifest hashes and native image hashes are bound
by their build receipts. No diagnostic sampler or marker overlay is loaded by
these ordinary builds.

All paths, exact package/ELF hashes, the negative-control identity and final
NativeHost receipt are indexed in `analysis/common-a-ready-01.json`. Canonical
consumer roots are `consumers/common-a-{sqlite,postgresql}/{korda-query-phases,korda-workload}`.

## Remaining gates

The package builds and complete NativeHost tests are ready for the parent's
ordinary causal A/B window. This is not a statement that every selected CI check
has already passed. Remaining work includes component/API/property/provider and
ordinary package-smoke gates; independent mechanism observations identifying
eligible same-thread continuation delivery; repeated default-runtime A/B; and,
only for a retained candidate, mixed-load capacity, four serial1800-second final
cells, independent review, normal merge, existing CI and public-package readback.
Keep the original B32 business contract and the same native image for this
common-only experiment. Reject the complexity if handoff reduction does not
translate into reproducible ordinary benefits or if a contract regression appears.
