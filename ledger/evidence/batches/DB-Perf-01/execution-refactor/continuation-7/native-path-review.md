# Native execution and complete-command review

Review date: 2026-11-26 (Asia/Shanghai). This independent review reads the
recovered source, original receipts, upstream source and raw observations. It
does not run a new product build or workload. The reviewed public product is
[47fe650](https://github.com/IzuSharp/Korda/commit/47fe650dfed5d7bba1c4d74c4a127c5d08b66082),
whose only change from public 8789a45 is formatting in two managed command files.
The PostgreSQL commit-proof experiment is separately bound to local
`d2c137bf44eb0b8490c8c4f59f12f34d2df75ac2`; integration and publication of that
experiment require their own source identity. The original evidence remains in
`/workspace/scratch/4a65d70f0fe1` (called `recovered/` below).

## Disposition

The PostgreSQL conditional commit probe is suitable for integration and the
existing affected correctness/package checks. Its source and real protocol
tests preserve the failed-transaction, savepoint, Unknown, cancellation and
connection-return contracts. The confirmed saving is one SQL execution and its
two ReadyForQuery replies on a healthy outer commit. The one recovered
15-second comparison does not establish a stable latency or throughput gain.

Gate E2 has a specific implemented decision: keep one bounded NWQC language
boundary, consume original operand spans through the authoritative C++ semantic
builder, and remove redundant control-frame adaptation and private-arena copies.
The `QueryCommandReplay` class and record traversal remain actual product
callers. This review does not claim that all replay, graph construction or
serialization has disappeared. Remaining copies and their callers are listed
below; no unmeasured cost is described as zero or negligible.

## PostgreSQL commit proof and upstream source

The isolated worktree is `recovered/worktrees/DB-Exec-08-pg-commit-proof`.
Its commits are:

| Local commit | Change |
| --- | --- |
| `cd8bf3d36743509eb6a50a1701e9b497180beb46` | Read confirmed libpq transaction state and conditionally skip the pre-COMMIT SELECT 1. |
| `bf2f3846b04cd0e8d9f8301bace672a77e672f6e` | Count actual SQL dispatch, description/execution groups and confirmation replies for ordinary and cursor-EOF commits. |
| `d2c137bf44eb0b8490c8c4f59f12f34d2df75ac2` | Prove excluded connection states and failed/savepoint fallback behavior. |

`ProviderConnection::postgres_transaction_ready_for_commit()` requires a live,
healthy, nonblocking PostgreSQL connection, pipeline mode OFF, no live statement
and exact `PQTRANS_INTRANS`. It holds the existing physical-lifetime mutex;
Session admission supplies exclusive protocol ownership. `Transaction::finish_worker`
additionally requires an empty savepoint stack. All other states retain the old
probe and its SQLSTATE precedence.

The fixed upstream basis is PostgreSQL/libpq 18.0 at
[3d6a8289](https://github.com/postgres/postgres/tree/3d6a828938a5fa0444275d3d2f67b64ec3199eb7):

- [fe-connect.c](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/interfaces/libpq/fe-connect.c),
  `PQtransactionStatus`, returns ACTIVE while `asyncStatus` is not IDLE and
  otherwise returns the transaction status recorded from the server.
- [fe-protocol3.c](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/interfaces/libpq/fe-protocol3.c),
  `getReadyForQuery`, distinguishes I/T/E as IDLE/INTRANS/INERROR.
- [utility.c](https://github.com/postgres/postgres/blob/3d6a828938a5fa0444275d3d2f67b64ec3199eb7/src/backend/tcop/utility.c)
  can report a failed transaction's COMMIT as a ROLLBACK command tag.
- [NpgsqlTransaction.cs](https://github.com/npgsql/npgsql/blob/4d174200ed48e3e3ab16419dbf84dd655da59de6/src/Npgsql/NpgsqlTransaction.cs)
  at actual Npgsql 11.0.0 source separates connector ownership and transaction
  control; its Commit uses an internal command. This is a reference for driver
  responsibility, not proof that Korda's outcome contract equals Npgsql's.

Using the existing Boolean `in_transaction()` to remove the probe would conflate
INTRANS and INERROR. The selected exact-state check avoids that error. A
successful local-state observation proves the preceding command boundary; it
does not prove the later COMMIT outcome or permit recovery to relabel Unknown.

The original archive is
`recovered/tools/postgres/postgresql-18.0.tar.bz2`; source indexes and excerpts are
retained in `recovered/artifacts/sql-parity-and-find-audit-01/upstream/`. This review rehashed
the PostgreSQL archive, its three cited full members and numbered excerpts,
and all six retained Npgsql/Microsoft.Data.Sqlite source files. All hashes match
the original indexes. The PostgreSQL archive SHA-256 is
`0d5b903b1e5fe361bca7aa9507519933773eb34266b1357c4e7780fdee6d6078`.
An attempted new web retrieval returned `DisabledError`; no new online-fetch
success is claimed. The preserved exact source supplies this review's evidence.

## Real protocol checks and negative control

The candidate receipt is
`recovered/validation-evidence/pg-commit-candidate-01/result.json`, SHA-256
`4dcebf80990d59fe46c85e058a640e4b8d76a267755bd0ea704e0fc35859c6f9`.
The negative-control receipt is
`recovered/validation-evidence/pg-commit-negative-01/result.json`, SHA-256
`0674791816c52a33244889068b5a344d46d472548f3af1081ecc562a7f7b0dc6`.
This review independently rehashed every referenced record: candidate 47/47 and
negative control 7/7 are present and unchanged.

The candidate's real PostgreSQL protocol suite passed 432 checks. The original
native transaction test and PostgreSQL provider fixtures also passed. The old
implementation with the counting assertion fails as intended: it dispatches
SELECT 1 and COMMIT. Its unmodified failed log has SHA-256
`a10deaa8a4e08cbbe1903195e152579626b75a7570bdb5d15eb63d07a0fab3f3`.
The negative source is local `cb86d949e591b482f55bf7f497477bc8b0f8d35d`;
its expected process exit is 1, not a successful product execution.

| Observed healthy commit | Old implementation | Commit-proof candidate |
| --- | ---: | ---: |
| SQL executions | 2 | 1 |
| Description groups | 2 | 1 |
| Execution groups | 2 | 1 |
| Standalone Sync messages | 2 | 2 |
| ReadyForQuery replies | 6 | 4 |
| Successful libpq send API submissions | 10 | 6 |

The last row counts the implementation's successful libpq submissions, not
individual wire messages. For example, one `PQsendQueryPrepared` call can emit
several protocol messages. The real proxy supplies the group/Sync/Ready counts.
Both nonquery and consumed-cursor-EOF commit routes verify actual durable data
through an independent connection and reuse of the original physical backend.

The state-exclusion tests cover no transaction, completed BEGIN, described but
unexecuted statement, active reader, live statement after EOF, closed reader,
INERROR before/after Sync, completed ROLLBACK and closed physical connection.
Fallback tests preserve the exact parsed SELECT 1/ROLLBACK sequence, 25P02
priority over savepoint depth, known RolledBack for the failed transaction and
the existing Unknown result for healthy retained-savepoint refusal. Existing
held/lost first post-COMMIT confirmation, recovery, pool-return, acquisition,
late-disconnect and partial-stream tests remain in the 432-check run.

## Recovered ordinary package and short observations

The independent package/input verifier is
`recovered/artifacts/commit-proof-input-verification-01.json`, SHA-256
`ab2dbb66265e0b46ec45f6322ba450c43e98733a0d2bf38d8570e78d675a43c5`.
The consumer has no project references and uses the ordinary product asset
without test hooks. Source parity is explicit: its managed source, business SQL
and DTO inputs match public 8789a45; its native source is the isolated candidate.

| Input | SHA-256 |
| --- | --- |
| Candidate native library | `ef0fae53f651b874e4f565e19c4b22a0811cd676af45c64e0d9cb2a4667c76a7` |
| Candidate standalone PostgreSQL nupkg | `d71529492dc6648c2b2d801cd6e0f633474fec50e8f2998cd7e5d31c2f395e17` |
| Candidate ordinary AOT executable | `9ff5526b993a9bf3ed90f52cd96fe33068c0332547aa4b57183dc61c8ce1c365` |

The verifier's `performanceExecuted=false` records its build-time state at
05:18:59Z. Later raw executions are present under
`recovered/measurements/single-commit-proof-postgresql-01/`; they must be recorded
as later evidence without altering that historical build receipt. The comparison
source is `single-command-postgresql-01/` from the same recovered measurement
directory. Each process has about 15 effective steady seconds.

**Case correction:** `numeric` in these ordinary single-case groups requests
32 rows. It is not the single-row primary-key/Find measurement. The transaction
cases include their own Find operations, but their timings cover the complete
transaction business sequence.

| Korda case | Old completed | Candidate completed | Old p50 / p95 / p99, microseconds | Candidate p50 / p95 / p99, microseconds |
| --- | ---: | ---: | --- | --- |
| Numeric, 32 rows | 45,858 | 44,431 | 307.2 / 471.04 / 700.416 | 315.392 / 491.52 / 782.336 |
| Transaction rollback business | 6,784 | 7,223 | 2146.304 / 2818.048 / 4259.84 | 2007.04 / 2621.44 / 3735.552 |
| Transaction commit business | 5,252 | 5,478 | 2768.896 / 3604.48 / 5341.184 | 2686.976 / 3375.104 / 4554.752 |

All six Korda records have zero failed operations, zero oracle failures, no
reported errors and final owners returned to zero. These are histogram upper
bounds, using the existing recording method. The commit raw files have SHA-256
`aa6f0135a78ad8b6541bf2d9089c9187b9dca87e52d69ae240e655bee9da3a47`
(old) and `cd256a57203b145d3809a02559d3d519435eba86e8392f7f880e855df7a2062d`
(candidate). Their observed whole-business allocation is approximately
65,492.86 and 65,468.02 B respectively, not framework-only allocation.

Commit completion count increased about 4.30%, but unchanged rollback improved
and the 32-row query worsened in the same single comparison. These observations
cannot isolate a stable speedup. The runners explicitly have
`hostQualifiedForLongRuns=false`. No 1,800-second, host-qualification or final
candidate credit is granted here.

## E2: actual complete-command path and deleted adaptation

Read the fixed public
[query.cpp](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/native/cpp/src/query.cpp),
[QueryCommand.cs](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/src/Query.Binding/QueryCommand.cs),
[submission](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/src/Query.Binding/QueryCommand.Submission.cs)
and [QueryBinding](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/src/Query.Binding/QueryBinding.cs).
The product selects `CreateBuffered`; the direct constructor remains an explicit
compatibility/differential-test route, never an implicit fallback.

| Layer or object | Actual decision | Contract and remaining work |
| --- | --- | --- |
| Fluent public validation and static mapping metadata | Reuse. | Preserve mutation-call error timing, typed ownership, capability refusal and generated/handwritten mapping. |
| NWQC frame and typed owner sidecar | Retain one bounded input representation. | It encodes supported operation records, topology and owner indexes; native code still traverses records and constructs semantic nodes. It is not precompiled SQL. |
| `command_clause` / `command_fields` adaptation | Deleted by [1f93c5a](https://github.com/IzuSharp/Korda/commit/1f93c5addeae962fee692f5d2a533c596efaa16c). | No rewritten control-frame copy, token-patching frame or second schema parse remains. `NativeQuery::clause` resolves a slot only when consuming its original operand span. Text fields parsed for origin identity are passed to the clause consumer. |
| Per-operation private `QueryData` snapshot | Rewritten to in-place `Edit` in 1f93c5a. | Private compile owns a fresh arena and shadow registry; failure discards it without publishing partial source parameter identities. Independently callable mutable ABI queries retain copy-on-success. |
| `QueryData.values` retained raw-frame collection | Deleted in 1f93c5a. | Durable typed literal slots remain; the extra complete raw-frame copies had no remaining consumer. |
| Private seal and CTE-body arena clone | Deleted by [ada2831](https://github.com/IzuSharp/Korda/commit/ada28311a384ad149fdc3f9db3b14473aedf0061). | A private arena moves into immutable plan storage. Public direct-query state and explicit snapshot semantics still require independent ownership. |
| `decode_values` whole-frame owning `Batch` | Replaced by borrowed `BatchView` in ada2831. | Validate the original bytes, then make one durable copy of each retained cell. The FFI caller's span cannot outlive the call. |
| `QueryCommandReplay` traversal and NativeQuery semantic methods | Retain; real callers are compile/render/CTE. | This is the authoritative decoder/compiler entry after adapter removal. Renaming or deleting the class alone would not remove compilation cost. |
| NativePlan repeated parameter-frame rendering | Rewritten to precompiled expectation/ordinals and typed owned arguments. | The public execution path no longer writes a second NWDB frame only to parse it into provider arguments. Per-execution independent values still exist. |
| Frozen per-node C ABI | Retain compatibility and differential fixtures. | Native ABI declarations/fingerprint and direct semantics remain required. The command-only resolver deliberately removes these exports while exercising the formal buffered path. |

The source-bound correctness cases are in
[native query tests](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/native/cpp/tests/query_tests.cpp)
and [command-only tests](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/tests/Query.Binding/CommandOnlyTests.cs).
They include SQL/ordered-argument differential goldens, overwritten command input
after plan/CTE compilation, source-parameter failure atomicity, public mutation
recovery, shared origin budget preservation, 4096/4097-byte serializer boundary,
retained owner lifetime and absence of per-node fallback. The origin negative
control distinguishes 6002 retained bytes from an incorrect 12004-byte duplicate
under a 9000-byte budget. These finite tests protect semantics; their passing
counts are not isolated timing measurements.

### Remaining copies and representations

| Remaining operation | Actual caller and protected behavior | Measured attribution |
| --- | --- | --- |
| Operand payload into managed `_records` | Query composition snapshots caller-owned value bytes before they can change. | Included in composition; no separate copy-only cost. |
| `_records` into final NWQC frame | Seal/Render: the private single-root path uses at most 4096 stack bytes; generic graphs use a heap envelope, graph ordering, origin indexes and sidecar fixups. | Included in construction/preparation; this review does not assign a separate cost. |
| Explicit managed Clone/Snapshot records and metadata | `CloneSelected` / `SnapshotAndImport` must remain independent of later source mutation. Shared immutable origins and owner leases are retained. | Complex-query snapshot cost remains observable, not separately attributed here. |
| Immutable native block/plan ownership | Imported plans/CTEs survive source builder disposal and enforce topology, source generation and budget semantics. | Private arena transfer is implemented; required owner/storage cost is not zero. |
| First native scalar-origin identity snapshot | Clone/CTE origins compare complete identity bytes and reuse the correct immutable slots; independently equal values remain distinct origins. | First identity copy remains; repeat comparisons borrow input segments. No isolated timing. |
| Durable decoded literal cells | A native plan survives the synchronous borrowed command input. | Whole-frame Batch copy removed; cell ownership remains. |
| Execution parameter frame into owned `Scalar` values | `capture_execution` synchronously snapshots arguments before asynchronous provider work and permits independently concurrent prepared executions. | Included in per-execution cost; no framework-zero claim. |
| SQL/Expectation copy into `RenderedQuery` / `SqlPlan` | Current execution owners retain complete command state independently. | Still present. Sharing immutable compiled shape is a possible later candidate, not an implemented or measured saving. |
| ShapeCache ABI+identity buffer and hash | `ShapeCache::acquire` concatenates ABI identity with shape identity, hashes it, then checks exact identity under bounded-cache bookkeeping. | Still performed per acquire. No isolated cost or selected replacement in this review. |

## Remaining waits and completion ownership

The fixed [provider](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/native/cpp/src/provider.cpp),
[Host](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/native/cpp/src/host.cpp)
and [protocol tests](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/native/cpp/tests/postgres_sync_tests.cpp)
bind the wait inventory:

| Boundary | Retained reason and proof |
| --- | --- |
| PostgreSQL Parse + Describe + Sync | Queued together before waiting. Fresh metadata/error precedence is checked before Execute, preserving cursor-open side-effect timing and external-DDL behavior. Physical prepared-statement caching is not selected. |
| First fetch / later provider read | Execute begins on first fetch. Real row data and terminal provider errors must be received before publication; row limits do not invent EOF. |
| Natural EOF close | The same execution's confirmed ReadyForQuery permits removal of a redundant stream-close Sync. Partial/unopened/failed readers retain their actual drain obligation. |
| Successful COMMIT confirmation | Keep the first post-COMMIT Sync. Lost/held acknowledgment preserves Unknown independently of eventual durable database outcome. |
| Recovery and pool return/acquire | Keep independent physical-protocol checks, cleanup disposition and discard on failed proof. A caller result does not certify a reusable connection. |
| Native ready callback tail | Execution accessors, cancellation hook, gate and Source pending reservation are released before notification. Independent command/pull fences protect parent joins after notification. |
| Early Unknown transaction | Its independent finish/deadline workers retain the admission gate and physical owner. The completion worker drops only its own reference. |
| Untaken new transaction/savepoint result | Command join performs real child cleanup; dropping a result wrapper does not declare resources released. |

`CommandCompletion::Worker::settle` does not access the command/provider/Source
after ready publication. Independent completion/parent tickets remain until its
notification tail ends. This preserves Source join without restoring a normal
command's generic retirement polling. Source/admin and indeterminate cold
cleanup still have genuine generic callers; they are not dead code.

SQLite retains one sqlite3 statement for prepare/description/binding/step, and
finalizes on success/failure under the existing path. The `query_only` control
cannot be removed merely because the last Korda transaction was writable: raw
PRAGMA can change connection state during preparation. Its retained source
reason and read-only/write cleanup tests are in
[the preceding SQL/probe audit](../continuation-6/sql-and-probe-audit.md).

## Remaining priority and acceptance boundary

The selected fixed-key Find work should first remove repeated construction,
NWQC encoding and native compilation for the same immutable metadata shape,
while retaining mapper identity, caller-key snapshots and fresh provider result
validation. Its eventual code and tests require an independent review and an
exact-package comparison; this document does not pre-accept that implementation.

After the fixed-key comparison, root should assess the remaining ShapeCache
ABI+identity hashing and SQL/Expectation copies using actual phase or allocation
evidence. They have not received cost attribution here. Do not assume their
removal is a measured win, omit their ownership constraints, or hide their cost
inside a claim that dynamic-command replay is gone.

Integrated product/package checks, same-condition short calibration and the four
serial local 1,800-second cells remain separate acceptance steps. This review
adds no CI action, changes no benchmark threshold and grants no final long-run,
zero-allocation, merge or release credit.
