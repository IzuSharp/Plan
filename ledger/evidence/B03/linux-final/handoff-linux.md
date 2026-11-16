# B03 Linux x64 component handoff

## Current checkpoint

- Owner: `/root/environment_review`; independent review and integration owner: `/root`.
- Worktree: `/workspace/scratch/0898a75257bc/.worktree/Task-02-B03-linux/NativeWeave`.
- Branch: `task/Task-02-B03-linux`.
- Final task checkpoint: `c1d249b0d7b5fcec0403c864c64ff0e22652461e` (clean).
- Status: task-owned implementation, API/XML/reference, samples and actual Linux component verification passed. Root owns independent acceptance, B05/B06 package composition, Plan status, PRs and publication.
- No other platform acceptance, assembled B04 host, pristine NuGet consumer, performance or RSS advantage is claimed.

## Commits and scope

| Commit | Task-owned handoff |
| --- | --- |
| `1bc7ebd` | Bounded SQLite configuration, admission, physical-session actor, real SQLx operations, B05 driver and initial 12 provider scenario groups |
| `666185c` | Owned actual SQLx statement metadata via the same actor for empty-result B06 shape checks |
| `17fa499` | Provider-confirmed stopped flag separate from a late stop request |
| `e7fa3989fda3ccd829bb62af462357335bda2fba` | Exact options/Engine component API, JIT/AOT fixture, generated asset profile, docs and verifier; admission permit released before waiter wake |
| `22e077e141c26d5fc0597bfa040534966668da05` | Last-parent physical closure join and finite row handoff; 14 provider groups |
| `c1d249b0d7b5fcec0403c864c64ff0e22652461e` | Reject nonrepresentable monotonic acquisition deadlines before SQLx/file I/O |

Root authored shared Cargo/dependency registration changes independently. No task agent rewrote the solution or shared manifests.

## Exact public API and component boundary

The compiled component exposes 29 exact pinned symbols: standalone SQLite options/enums and `SqliteDataSource.Engine`. Full XML and generated reference pass against actual compiled metadata. `src/Data.Sqlite/host-composition.expected.json` maps the three exact B04 facade symbols (Create, UseSqlite and its extension container) without introducing fake DataSource/throwing host stubs. Their host runtime and normal package composition remain B04-owned under the packet DAG.

The Engine descriptor is metadata-only and advertises only the implemented SQLite profile bootstrap. A maintainer build consumes an already built native asset; MSBuild hashes that real asset and generates the profile/output record under `obj`. Ordinary consumer builds do not invoke Cargo, and no machine-local ELF hash is committed as a product constant. Both default and explicit preflight paths inspect the actual copied asset with the actual bootstrap.

## Native ownership and integration seams

The host supplies a Tokio runtime and checked-out SQLx connection. `Session` owns the physical connection through a retained actor; no default global runtime or second pool is created. Business queries have finite command/input reservations; protocol controls have independent capacity. Dropping a business waiter does not drop accepted SQLx work.

B06 consumes actual `SqliteRow` values through `RowStream`, separate `StopControl`, and independent `OperationReceipt`. `Session::describe` prepares metadata on the same actor; statement columns remain available for empty results. `OperationRetirement.stopped` records actual interruption/stop before natural completion; a late request alone cannot replace EOF.

The producer reserves existing channel capacity before polling SQLx for another row. With the one-row profile, producer plus queue is at most one row, and the receiver may hold one more during delivery. A per-row counter guard also handles a reserved send racing receiver teardown. This preserves the reported bound of two without a new resource layer and without changing B06 encoded row/batch budgets. SQLx's own one-row buffer and SQLite current cells are separately documented; this is not a universal process-memory bound.

B05 `SqliteTransactionDriver` uses the same physical session actor. COMMIT acknowledgement is authoritative before later recovery; Unknown remains Unknown after lost-waiter/late-success outcomes. Rollback-to preserves SQLx's tracked top savepoint. Retirement first removes the driver's parent Session lease, then observes whether any independent parent remains or close was requested. Last-parent/closing paths await the actual SQLx worker shutdown acknowledgement. Neither a prior owner-count check nor a close notification is reported as physical retirement. OS-thread JoinHandle is unavailable, so `os_thread_joined` remains false.

## Final actual verification

Final receipt: `artifacts/B03/attempt-003/result.json`.

- Source: `c1d249b0d7b5fcec0403c864c64ff0e22652461e`, clean before and after verification.
- 33 commands passed; 102 source/lock inputs unchanged; 66 raw stdout/stderr hashes and six final artifact/output-record hashes independently rechecked by `final-receipt-audit.json`.
- Fixed SDK 11.0.100 / Rust 1.100; SQLx 0.9.0, Tokio 1.54.1, libsqlite3-sys 0.37.0 and actual bundled SQLite 3.51.3.
- Native format/Clippy and three actual Rust test functions covering 14 provider groups passed.
- Exact 29 compiled API signatures, XML and generated reference passed.
- Ordinary JIT and actual Linux x64 Native AOT each passed 36 managed assertions and all 14 real SQLite/B05 groups. The AOT executable asserts that dynamic code is unavailable.
- Separate ordinary/AOT locked restore closure; real maintainer asset digest equals both generated output records and copied binaries; no tracked source/profile hash drift.
- Local folder whitespace was checked. Full solution formatting, normal NuGet audit, package integration/CI and release remain root's existing integration gates; the explicit local offline feed does not change repository policy.

The groups cover per-physical-connection profile/FK/WAL/synchronous/busy configuration; isolated single-connection private memory; typed B07 parameters and NULL; failed transaction state and repeated savepoint rollback; progress-handler cancellation and generation isolation; empty metadata and early stream stop; rollback, TEMP marker pool reuse and closure; actual COMMIT-hook pause with lost waiter/Unknown and durable late effect; count/byte/timeout admission; WAL reader/writer contention and atomic unique conflict; SQLx migration checksum and failing transactional DDL; read-only reset and unsupported isolation; last-parent retirement; and 40,000 rows crossing the bounded handoff. Migration probes use native SQLx APIs and do not implement B08's public administration layer.

## Preserved review failures and resolutions

1. `attempt-001` passed on e7fa398 but is superseded for acceptance. Root's independent review found premature local-resource release when the driver held the final Session parent. The actual test pauses destruction of SQLx ConnectionState via a test-only callback capture: old code reported local released=true, worker ACK=false, pool size=1. `last-parent-review/pre-fix.json` and raw logs retain the failure. Fixed formal executions report released=false before the gate and only complete after worker ACK/pool release.
2. B06 `development-2` observed provider row peak=3 on e7fa398. `stream-handoff-review` retains its raw execution/source receipts. The old channel capacity was released before receiver accounting, permitting one extra delivery handoff. Commit22e077e reserves before SQLx fetch; four rounds of 10,000 actual rows report peak2 in Rust, JIT and AOT.
3. `attempt-002` passed after those fixes. A further root boundary check found `Duration::MAX` accepted by Limits and an actual SQLx `connect_with` panic at its deadline addition. `acquire-timeout-review/pre-fix-cargo.json` preserves exact source/lock/probe/log identities. Commitc1d249b rejects zero/overflow before pool options, admission or file I/O; formal group9 verifies it.
4. Earlier development also found the error-delivery cancellation race, missing Engine output record and sequential capacity wake race. These were corrected before the first formal pass; earlier development diagnostics are implementation history rather than retained formal acceptance receipts. The `dev-jit-001` and `dev-jit-002` directories contain transient database fixtures and are excluded from retention. The post-review local tuple-poll compile error was corrected before22e077e and its failed raw log remains under `last-parent-review`.

No prior successful run is substituted for the final fixed-source receipt.

## Next integration step

Root should integrate through c1d249b, bind the independent B03/B05 review and final B06 composition receipts, copy this handoff/raw receipt evidence into Plan's existing B03 and Task-02 records, then complete the already authorized branch/PR/merge/post-merge pipeline. This task agent has not claimed or bypassed remote checks or review approvals.
