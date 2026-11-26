# DB-Exec-Parity-01 — PostgreSQL-A isolated candidate

## Change, authority and causal question

Stage 1 evidence preceded this implementation. The paired Plan gate is
`da20dc395ca44a0430f933aeb7a45a3ee13aa447`; the PG-specific hypothesis is recorded
in Plan `2271ad0` and Design `9435043`. Product candidate
`459ec69b6d411cd40723f342f8e88c3cabe111eb` starts from main
`7ff7b57b907b689defb880b8af62d83679608603` on
`task/DB-Exec-Parity-01-postgresql-a`, in `worktrees/Korda-postgresql-a`.

Only `native/cpp/src/provider.cpp` changes: 11 added and six removed lines.
Three interrupt-hook registration sites are enabled only when the SQLite
provider is active. The unused `ProviderConnection::Impl::interrupted` field
and its two stores are deleted. The query, protocol, batch size, row/column
checks, cancellation checks and cleanup paths are otherwise unchanged. There
is no chunk mode, cancellation-token cache, runtime spin knob or public API
change. No diagnostic or performance code enters this product commit.

The causal prediction is specific: PostgreSQL's 1,000-row narrow hot Prepare
query should go from 1,002 `Cancel::install` calls to zero while retaining
1,001 advances, 1,000 single-row PGresults, 32 logical batches, the same SQL and
protocol sequence, and the same cancellation/drain behavior. The candidate
makes no allocation-reduction promise. Interleaved ordinary A/B must establish
any actual CPU or endpoint benefit; these build and correctness receipts do
not establish it.

## Proof for omitting the PostgreSQL hook

Before the change, all three hooks capture a weak ProviderConnection and call
`ProviderConnection::interrupt()`. That method sets `interrupted=true` and,
only for SQLite, takes the lifetime lock and calls `sqlite3_interrupt`. A
whole-native-tree search found no read of `interrupted`; its only references
were the member declaration, prepare's false store and interrupt's true store.
The PG branch never sends a cancel-key request and does not wake `poll`.

PostgreSQL already observes `CallContext::check()` before row admission and in
the nonblocking `receive`/`flush` loops. `wait_socket` checks before and after
each bounded poll; the requested timeout is capped at 20 ms. `Cancel::request`
still publishes the atomic requested flag. Metadata validation, lazy Execute,
deadline ordering, old-token detachment, first provider error, cleanup budget,
ReadyForQuery proof, pool discard and Unknown COMMIT outcome retain their
existing implementation.

SQLite still installs the original weak-pointer callback in prepare, advance
and execute_script when its handle is active. Its lifetime lock and
`sqlite3_interrupt` call are unchanged. In the combined native test build both
provider feature macros are enabled; the handle predicate keeps those paths
distinct. In each independent public provider image the existing feature
macros compile the unrelated engine out.

The alternative of caching the last `Cancel*` in a statement was rejected:
Host detaches after preparation and each fetch even if the statement retains
the same context. Such a cache could suppress required reinstallation. This
candidate adds no lifetime cache and does not change detach behavior.

The actual pinned Clang23/libc++ machine code uses std::function small-object
storage for the old lambda. It is not a measured heap allocation per row.
`analysis/pg-machine/diagnostic-korda-native-01/symbol-03.annotated.asm.txt`
maps addresses 0xa7033–0xa7059 to the placement-new/function call; the heap
allocation at 0xa7130 is the first-Execute parameter pointer vector reserve.
Repeated mutex entry, weak-reference changes and callback replacement are the
targeted work. Their exclusive CPU cost remains a causal measurement question.

## Committed-diff routing and package separation

Immediately after committing, the required command ran successfully:

```sh
python3 eng/ci/impact.py origin/main --output artifacts/plan.json
```

The preserved result is `builds/postgresql-a-postgresql/impact-01.json`.
`provider.cpp` is owned by `database-native`, so the plan selects the shared
Linux native/dependency/regression group and both independent top-level package
groups. PostgreSQL and SQLite each receive their own build, dependencies, pack,
packed API, test, AOT consumer and public validation actions. Both remain
independently installable; no publication candidates are emitted on this task
branch. The shared source ownership explains why SQLite checks remain selected
even though the intended runtime change is PG-specific. Nothing in CI, module
routing or the historical Go drafts was changed.

`clang-format --dry-run --Werror` and `git diff --check` passed. The native
producer uses the unchanged `eng/task07_native.py` and pinned toolchain. The
local package driver uses canonical bundle selection/composition/closure
validation with the already recorded single-node MSBuild flags. Its explicit
local version override is not a main release-plan result or CI pass.

## Ordinary candidate artifacts

All paths below are relative to the task root.

| Artifact | Identity |
| --- | --- |
| Native manifest | `builds/postgresql-a-postgresql/native-01/manifest.json`, SHA-256 `f05196c0949f686a2e27ebdde05f48793931e880629ca7ca785637f532d5b615` |
| Native image | SHA-256 `5a446d1a83b1460920a1cbe1ab159e4a054dbb6846df4018acfbda0f715d7854` |
| Public nupkg | `builds/postgresql-a-postgresql/public-01/feed/Korda.Database.PostgreSql.0.1.0-db-exec-parity-postgresql-a.1.nupkg`, SHA-256 `0be7b38f111eb90abd6654b6bc6e51cbc3d241f00e817decd2fc1e5dc11179fd` |
| Workload AOT | `consumers/postgresql-a-postgresql/korda-workload/out/DbPerf.Korda`, SHA-256 `350a4dcb0e0ee2e1b5bbe6e4a68c709316de166cbf167f0a9fd6a8066cd30cce` |
| Workload debug | SHA-256 `95d3dac21f5c1a46200e92a5c31bb824c3ef95395605eaed15911ea38f5d3b79` |
| Query phases AOT | `consumers/postgresql-a-postgresql/korda-query-phases/out/DbPerf.QueryPhases`, SHA-256 `3b3d1664402fcb439012936bb88805ec437444fcbed2389bd9eb6ead5efb5843` |
| Query phases debug | SHA-256 `9e4a35ae042c4ac1c19a582164d01c5fe5cfe1a4d8ddabbceae6cf2444ae21e0` |

Each consumer is outside the product tree and references the exact real package,
with no ProjectReference. Its retained evidence includes actual emitted C#,
restore graph, publish command/log, ELF, matching `.dbg`, native image and
`evidence-identity.json`. The canonical `eng/ci/validate_public.py` passed for
this exact package, source tree, version, README/description and closure.
Runtime package consumption and timing use the root-controlled ordinary lanes.

## Existing native correctness results

`analysis/build_postgresql_a_tests.py` builds existing targets in the ordinary
full Release preset and validates their native dependency graph. The build
receipt is `builds/postgresql-a-postgresql/native-tests-01/build-receipt.json`.
It does not create or change any product test or workflow.

`diagnostics/postgresql/run_candidate_correctness.py` uses the existing PG TLS
certificate helper, starts valid-TLS, expired-TLS and plaintext PG18 fixture
servers in the same controller family, and runs five existing targets in six
invocations. Raw results are `measurements/postgresql-a-correctness-01`.

| Existing target | Observed result and coverage |
| --- | --- |
| `nw_provider_tests` | 183 checks, zero failed cases, `postgres_verified=true`; includes actual TLS policies, SQLite interruption/deadlines/old token and preparation cancellation, PG cancellation/finite drain/reuse, delayed fatal error, fresh DDL, metadata-first and disconnect replacement |
| `nw_postgres_sync_tests` | 432 checks; actual protocol state, metadata confirmation, COMMIT lost/delayed confirmation and recovery, check-in/pool-return, acquisition cancellation, exact boundary/EOF, early stop, lost Execute ReadyForQuery and provider-error precedence |
| `nw_command_completion_tests` | 377 checks; complete existing one-shot completion suite passed, including Unknown versus retirement and retained primary errors |
| Same target with `--postgres-queued-cancel-only` | 8 checks; actual PostgreSQL queued-command cancellation passed |
| `nw_transaction_tests` | 120 checks; existing transaction lifecycle/failure/owner tests passed |
| `nw_postgres_fixture_tests` | All 11 retained PG component cases passed |

All six test invocations exited zero. All three servers stopped normally.
These are correctness runs during a build/diagnostic lane, with no timing credit.
The controller verifies that test binaries and product commit do not change
during execution. It does not claim the full repository CI suite passed; the
selected final implementation must still pass all impacted package/module gates.
The independent SQLite review is
`analysis/postgresql-a-sqlite-cross-review.md` and reports no source blocker.

## Separate mechanism diagnostic and next checkpoint

The already frozen baseline observation branch received the exact candidate
commit by cherry-pick into local-only
`task/DB-Exec-Parity-01-postgresql-a-diagnostic` (commit `2396f25`). Its O3+DWARF
native build is `builds/postgresql-a-postgresql/diagnostic-native-01`, manifest
SHA-256 `d872d91e6820c4ed22a4f5db20f201efe6e4d18c4a030ee00e0b1c9aac31289e`.
This preserves marker/counter definitions and the original baseline diagnostic
identity. It is not a product package or a source of ordinary timing credit.

At this checkpoint diagnostic packing/AOT and counter execution are paused for
the root's first ordinary A/B screen. No CPU workload or compiler remains
running from this agent. Resume only the selected hook-count control afterward,
then compare actual counts/CPU against the prediction. Product acceptance,
combination with any common/SQLite candidate, final sustained campaigns and
normal merges/releases remain pending.
