# DB-API-01 — Linux handoff

## Remote continuation — 2026-11-23 21:20 UTC

The current Korda [PR #35](https://github.com/IzuSharp/Korda/pull/35) head is
`1794fbae14855f28842354c9649a66e58f5001ef`, tree
`ea65de3644a170bb9b642157091a4b2279d4a373`.
[Current-head CI](https://github.com/IzuSharp/Korda/actions/runs/45267208518)
has passed both independent provider jobs; the shared Linux job is still running.
Twelve retained verifier/sample-lock files now remove neutral executable-consumer
builds and run the old Codecs sample directly as Native AOT. Product/native code
is unchanged from the previous fully passing candidate. Every changed remote file
was read back and matched the prepared text. Scoped non-author followup reviews
are in progress.

Design [PR #16](https://github.com/IzuSharp/NativeWeave-Design/pull/16) is at
`656d56688c2af391e463d83dbb626699590b11f9`, with its observed checks passing.
Plan [PR #29](https://github.com/IzuSharp/Plan/pull/29) retains the earlier Plan-first
checkpoint and recovery boundary. No repository is merged yet; publication remains
unobserved. Wait for current checks and reviews, merge normally, then observe
each merged-main run and every triggered release before accepting the batch.

[Retained progress](results/retained-progress.json) reconstructs the unavailable
local review observations with explicit provenance. It also preserves the first
candidate's failure, the subsequent successful run, independently audited first
provider artifacts, and exact decoded GitHub job logs with SHA-256 digests.
Historical candidate evidence is not relabeled as the current source.

The local executor remains unavailable. Continue through immutable GitHub source
reads, small Git Data tree updates with branch-head leases, exact remote readback
and normal CI. On future local recovery, preserve and reconcile all existing
worktree changes before use.


## Recovery checkpoint — 2026-11-23 21:04 UTC

Korda [PR #35](https://github.com/IzuSharp/Korda/pull/35) is at
`29801745d01abe3cfed8fc90d25afdaa62706f27`, tree
`363e669f657df638967058016bccd9c0ab660bb7`. Its
[complete PR CI](https://github.com/IzuSharp/Korda/actions/runs/45263070788)
passed, including separate PostgreSQL/SQLite public package checks and external
three-phase Native AOT order consumers. No repository has been merged for this
batch, and publication has not been observed.

The workspace became unavailable during final verifier cleanup. GitHub remains
available. Continue from the actual remote PR heads; preserve any recovered local
changes before fetching and reconciling them. Local Plan authoring/candidate
evidence copies and some harness edits were not uploaded. Their existence is not
claimed as committed evidence. See [the remote recovery record](recovery/checkpoint-20261123T2104.json).

The remaining product change is narrowly required by current Korda AGENTS:
remove neutral executable-consumer builds from the selected legacy verifiers,
retain library/API/compiler checks, and convert the old Data.Codecs sample JIT
execution to Native AOT. Root owns Interop.Execution, Interop.Negotiation,
Data.Abstractions, Query.Binding and Query.Native verifiers; the two scoped
reviewers own the provider verifiers and Transactions/Streaming/Codecs verifiers.
A focused local Interop.Negotiation harness check passed 26 AOT cases / 428
assertions and the external package asset-location oracles before environment
loss. This was uncommitted authoring evidence, not final candidate acceptance.

The first candidate's shared Linux failure is preserved: a wrong relation call
still failed compilation, but the new batch overload changed its diagnostic from
CS0411 to CS1503. The correction adds a separate batch type-error probe; all seven
negative cases and the subsequent complete PR CI pass. The first candidate's two
provider artifacts passed independently. Their immutable artifact IDs and hashes
are recorded separately; do not relabel them as the later candidate.

After the AOT-only harness correction, require current-head CI, merge normally,
observe each main run and every triggered release, and complete the source-bound
acceptance record. Acceptance remains in progress; future CI is checked separately.


## Prior checkpoint — preserved

Implementation and local authoring verification are in progress. Product acceptance,
PR checks, merges and release observation are still pending. Read [plan.md](plan.md),
[baseline.json](baseline.json) and [acceptance.json](acceptance.json). Do not clear
`.worktree/DB-API-01-linux/{Korda,NativeWeave-Design,Plan}`, all using
`task/DB-API-01-linux`.

Observed starting main: Korda `7275396176b928c8879d59f4bf20ad8fa7ffb62c`,
Design `de1f4796dc199250b405ea99f2129d611f17b1f6`,
Plan `5be447a868be78713ada52f46cee16409f0edc13`.
Plan-first was published as `21e98f7591b4cf1f7fd5b7d5e791ab0be4271515`, then
Design-before-product as `3b270347d37f2bef0e6e5c6baefc9235e39bf7c2`.
The Design gate and six negative cases pass, including the unchanged historical
gate at its frozen commit. The Plan progress gate and seven negative cases pass.

## Implementation state

Both existing samples were compared with an order/customer/detail workflow.
Existing optional filters, joins, aggregates, keyed CRUD, checked concurrency and
insert-returning are reused. New code adds generated immutable DTO binders,
constructor mapping, reusable codecs, complete composite cursors, bounded batch
associations, transaction callbacks and migration/scaffold workflows. Native
execution remains in C++20/libpq/sqlite3.

Korda `samples/api/orm-experience/` and `eng/ci/orm_experience.py` contain the
external standalone-package workflow, still awaiting actual AOT execution. It
edits DTO source, compiles a scaffolded entity in the second run, and compares
loaded native hashes with package bytes. SQL dispatches and libpq protocol
submissions are separate; neither is a measurement of physical network round trips.

The first authoring native build completed all 169 targets under
`artifacts/cmake/linux-x64-release`. Host and generator libraries compiled with
zero warnings/errors. Korda.Data preserves 149 frozen declarations and adds 14
declarations; its compiled/XML inventory passes. The Database inventory initially
failed required MigrationChange lifetime/cost remarks. Those remarks have been
added and the check must be rerun. These are authoring observations, not
clean-source acceptance receipts.

## Host and blocked attempts

Provisioned pinned .NET 11.0.100, Clang 23.1.5/CMake 4.3.3/Ninja 1.13.2,
repository-pinned SQLite sources and source-built PostgreSQL 18.0. Native paths
are under Korda `artifacts/`; the SDK is under workspace `.tools/dotnet`.

Two restore attempts were rejected by automatic approval review for unsolicited
metadata/telemetry network side effects. The safer local path explicitly opts out
of telemetry and uses a bounded feed of exact official NuGet archives with locked
offline restore. Canonical NuGet content hashes remain unchanged; raw signed-ZIP
hashes are recorded separately. Repository CI retains normal NuGet audit settings.
Rejected attempts and authoring logs remain in `artifacts/db-api-mapping-local/`.

For local .NET commands set `DOTNET_CLI_TELEMETRY_OPTOUT=1`,
`DOTNET_CLI_USE_MSBUILD_SERVER=0`, `MSBUILDUSESERVER=0` and
`MSBUILDDISABLENODEREUSE=1`, with `UseSharedCompilation=false`, `-nr:false`,
`-m:1`. Consumers run only as Native AOT; compiler/API tools may run managed.
Clean-image and CPU-emulation checks were not requested.

## Next work

Finish compiler diagnostics/AOT mapping checks, refresh exact additive API/XML
references, then run real PostgreSQL/SQLite suites and external package consumers.
Inspect committed-diff routing; run required checks on a clean candidate; obtain
scoped non-author review and normal PR checks before merging. Observe merged-main
CI and every triggered publication before accepting this batch.

Draft PR identities will be recorded at the next remote checkpoint. Git fetch
works but shell push lacks credentials. The GitHub Git Data connector publishes
exact trees with a branch-head lease, followed by local fetch/tree verification.
No protection, required check, identity or publication setting is changed.
The containing evidence commit's own future CI is always checked separately.
