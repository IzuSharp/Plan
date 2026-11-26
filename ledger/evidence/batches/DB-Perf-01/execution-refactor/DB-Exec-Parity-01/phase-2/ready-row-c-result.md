# DB-Exec-Parity-01 — ready-row-c build and behavior handoff

## State and scope

The isolated candidate is built and behavior-verified, and is ready for the
root-owned ordinary interleaved A/B. **No performance, allocation parity or
selection claim is made by these build/behavior results.** All build, test and
machine-code inspection processes have ended; this agent is quiet during the
ordinary measurements.

The source starts directly from `7ff7b57b907b689defb880b8af62d83679608603`.
Product commit `bd9c307434d1d901752fd4353758041e38510ef1` changes only
`src/Data.Streaming/TypedStream.cs`. Test commit
`498fb329c897dac8d58479d218969eff99eeb8e5` adds behavior checks and their normal
correctness entry point. The candidate tree is clean. Neither lease-b nor the
PostgreSQL numeric configuration candidate is included. Native code and the
native execution schedule are unchanged.

The full frozen manifest is `analysis/ready-row-c-candidate-identity.json`.
The plan remains `analysis/ready-row-c-plan.md`; actual machine code and symbol
bindings are in `analysis/ready-row-c-machine-01/identity.json`.

## Measured reason for this candidate

The earlier request-bound lease observation counted actual rows and batches
for 150 successful queries across both providers. A full 1000-row query has
32 batches and 968 rows after the first row of their batch. The corresponding
counts are 0, 31 and 96 for 1, 32 and 100 rows; an early stop after one row has
zero. Baseline actual machine code enters the full MoveAsync wrapper for every
one of those rows. This establishes repeat work to isolate, not its share of
CPU or a predicted endpoint improvement.

The candidate keeps the existing synchronous admission gate, row lease,
generation checks, cancellation, column reads, mapper and buffered quotas. A
small synchronous state structure processes only an already available row.
Its public `AsyncValueTaskMethodBuilder<bool>.Start` invokes the same
`AsyncMethodBuilderCore.Start` context boundary used by the original async
method. No builder-owned Task is created or read on that successful path.

First start, fetch, EOF and exhausted/inactive batches still use the original
async method. A mapper failure starts the async failure/cleanup helper inside
the guarded catch, retaining the mapper context at cleanup entry. That helper
keeps the move admitted until cleanup ends, attaches cleanup failure to the
original exception, preserves OCE cancellation state, and then finishes the
move. Successful FinishMove remains an independent finally boundary; its
failure is not sent back through mapper cleanup.

## Exact runtime and actual code

The fixed ILCompiler package binds to
`dotnet/dotnet@297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`. Exact full source for
AsyncMethodBuilderCore, AsyncValueTaskMethodBuilderT and
PoolingAsyncValueTaskMethodBuilderT is retained under
`diagnostics/runtime-source-297acf/src/runtime/src/libraries/System.Private.CoreLib/src/System/Runtime/CompilerServices/`.
`diagnostics/runtime-source-297acf/ready-row-builders-identity.json` records
SHA-256, byte counts and independently matching Git blob SHA identities.

Actual SQLite and PostgreSQL phase ELF/debug pairs have the same respective
function sizes below, at provider-specific addresses. Stack reservation and
initialization are taken from the real x64 instructions, not inferred from C#
field sizes.

| Function | Baseline | Candidate | Meaning |
|---|---:|---:|---|
| Enumerator.MoveNextAsync | 163 B; 24 B stack reservation | 304 B; 104 B reservation, 80 B initial clear | Candidate pays extra fixed dispatch work, including on first/EOF moves |
| MoveAsync wrapper | 156 B; 152 B reservation, 144 B cleared | Same wrapper size/clear | Already available rows skip this wrapper; slow cases retain it |
| Original async MoveNext body | 3562 B; 216 B reservation | 3475 B; same reservation | Candidate uses it only for slow cases; common finally was extracted |
| ReadyRowMove.MoveNext | Absent | 752 B; 120 B reservation, 88 B initial clear | New guarded synchronous body, including its cold exception handling |
| FinishMove | Originally inline in the async finally | 103 B | Same lock, moving flag and join-completion statements |

The candidate ready-state result also receives a 16-byte clear in the caller.
Thus it would be incorrect to describe the observed machine-code change as
simply replacing a 144-byte clear with a 24-byte clear. Core.Start/context
protection still runs. Successful ready branches do not call public
builder.Task or an added allocation helper; application DTO allocation inside
Materialize is unchanged. Ordinary warmed allocation A/B still must verify
the absence of a new per-row managed object cost.

## Behavior checks

The exact new test source is present both on the original product and on the
candidate. The independent original-product test worktree is
`task/DB-Exec-Parity-01-ready-row-c-baseline-checks`, commit `962c401`; its src
diff from the baseline is empty. Both were restored with locked dependencies,
published in Release Native AOT, and directly executed with `--require-aot`.

| Run | Assertions | Result |
|---|---:|---|
| Original product + new context/completion checks | 233 | Pass |
| Candidate + same context/completion checks | 233 | Pass |
| Candidate existing stable-batch checks | 30 | Pass |
| Candidate existing row-lease checks | 364 | Pass |
| Candidate existing borrowed-lifetime checks | 19 | Pass |
| Candidate existing active-move/borrow races | 118 | Pass |

The candidate total is 764 assertions. All restore/publish/run commands passed
on their first attempt. The new checks enter the genuine second row of a
three-row native batch. They cover AsyncLocal and SynchronizationContext
isolation, normal and suppressed execution-context flow, ordinary mapper
failures, OCE with canceled and absent tokens, canceled admission, cleanup
entry under the mapper context, pending cleanup, concurrent MoveNext and
Dispose, original/cleanup exception ordering, buffered limits, and 32/33-row
batch boundaries. An active second-row mapper retains native storage until
completion despite concurrent disposal.

Two executable negative controls demonstrate that a plain synchronous mapper
leaks its context changes and that FromException(OCE) gives Faulted instead of
the required Canceled state. Context observations occur synchronously inside
the test method, before an enclosing async method could conceal a leak.

Receipts and complete outputs are in
`builds/ready-row-c-baseline-streaming-correctness-01/` and
`builds/ready-row-c-candidate-streaming-correctness-01/`.

## Independent packages and consumers

Both local packages use version `0.1.0-db-exec-parity-ready-row-c.1`. They were
built independently by the canonical bundler, with each recorded baseline
native source/tool/output input checked before native artifact reuse. No
publication was performed.

| Package | SHA-256 |
|---|---|
| Korda.Database.Sqlite | `b8348ec63dd792cddebb24768ddabe7276b188b892e3921428762c8805ec3d9f` |
| Korda.Database.PostgreSql | `5fd32fcc3628be573566b2cad976ee5647181e0a645fa1a9a6bca45cc6ab37fc` |

Package builds, committed impacts, local version-only plan derivations, native
reuse proof and canonical package receipts are under
`builds/ready-row-c-{sqlite,postgresql}/`. Both committed impact plans select
linux plus the independent SQLite/PostgreSQL package actions and public
checks, because the changed implementation is shared Data.Streaming. No CI
workflow or performance entry point was changed.

Four real PackageReference-only ordinary Release AOT consumers are retained:

- `consumers/ready-row-c-sqlite/korda-query-phases/`
- `consumers/ready-row-c-sqlite/korda-workload/`
- `consumers/ready-row-c-postgresql/korda-query-phases/`
- `consumers/ready-row-c-postgresql/korda-workload/`

Their original harness, generated C#, actual ELF/debug files, native libraries,
package graph, commands and hashes are preserved. No new GC metrics transform
was applied to this isolated A/B. Consumer bin/obj intermediates were recorded
before removal, and the final manifest records another 16,472,700 bytes of
this candidate's own reconstructible source-build intermediates retired after
their hashes/generated inputs were retained. Unique ELF/debug/package/source
outputs were preserved.

## Decision still required

Root owns ordinary zero-refusal cost, CPU/operation, allocations and endpoint
comparison. In particular, one-row and batch-boundary cases may regress from
the larger MoveNextAsync dispatch even if 1000-row cases improve. A code-size
reduction in one body, the 968 count, and successful correctness tests are not
acceptance metrics. This candidate remains unselected until repeat ordinary
measurements establish its effect and its tradeoff across the original work.
