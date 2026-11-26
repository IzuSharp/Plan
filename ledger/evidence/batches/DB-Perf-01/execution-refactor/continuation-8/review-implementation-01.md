# Independent implementation reading review — frozen 17da candidate

Review date: 2026-11-26. Reviewer: `implementation_review`, a separate continuation worker that did not author the reviewed implementation.

## Disposition and scope

**No new concrete product-correctness, public-entry or independent-provider-package closure defect was found that requires interrupting the frozen long-run campaign.** Continue the already frozen candidate and consumer inputs. This reading review does not grant final performance acceptance, merge readiness or publication credit. Those decisions still require the actual four serial 1,800-second results and their final evidence checks.

The local product worktree was clean when inspected:

| Identity | Observed value |
| --- | --- |
| Worktree | `/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-korda` |
| Local HEAD | `040911c5abdee740c0cd9fbf8295bf511c9cc69d` |
| Actual local tree | `bc9087d843d8d741d83d44f53d0b2c5af26dcffc` |
| Published frozen candidate | [`17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`][product] |
| Published candidate tree in the existing receipts | `bc9087d843d8d741d83d44f53d0b2c5af26dcffc` |

The local tree matches the published candidate's recorded tree. The difference between the local and published commit identities is retained rather than concealed.

The reviewer read `AGENTS.md`, `eng/ci/modules/README.md`, relevant source changes from `origin/main`, the formal entry and ownership paths, related native and managed assertions, and existing validation/package/CI receipts. The review also checked the actual frozen mixed-workload consumer source and raw result fields for GC reporting. Twelve small source files—`Measurement.cs`, `OfferedLoad.cs` and `Program.cs` in each of the four frozen consumers—were checked against their existing build-receipt source hashes during that reading audit. All matched. No binary hash sweep was performed by this reviewer.

The reviewer did not edit product code, build, execute tests, profile, run a benchmark, change frozen inputs, push or merge. Saving this document is a subsequent documentation-only action. Existing executed tests and earlier independent reviews remain attributed to their original sources and actors; reading their receipts does not rerun them.

## Formal entry and implementation choices

| Layer | Observed implementation | Source location at the frozen tree |
| --- | --- | --- |
| Ordinary Fluent | `DataSession.From` explicitly requires `db.query.command.v1` and selects `QueryBinding.CreateBuffered`. No implicit fallback from the formal Fluent entry to per-node native composition was found. | `src/Query.Fluent/SessionQueries.cs:18–23` |
| Complete command | A small single-root command uses stack scratch. Complex dependency graphs retain bounded NWQC encoding and native semantic traversal. Compilation produces the executable plan directly rather than rendering a completed command and rebuilding it through another public SQL path. | `src/Query.Binding/QueryCommand.Submission.cs:13–31,105–132` |
| Private Find | The public `FindAsync` body replaces per-call Fluent construction with a retained source-owned shape and independent execution values. | `src/Orm.Relations/Crud.cs:18–27`; `src/Orm.Relations/FindPlan.cs:19–56,160–175` |
| Native immutable plan | A private complete command moves its validated `QueryData` into immutable plan storage. Independently callable legacy query handles retain their own state semantics. Private Find reuses its own compilation without another general `ShapeCache` lookup. | `native/cpp/src/query.cpp:1889–1900,1904–1979,3089` |
| Row execution and mapping | Fluent, Prepare, Find and explicit SQL converge on `CreatePull → HostStreamTransport → TypedStream`; list and stream consumption use the same typed row machinery. | `src/Data.NativeHost/DataSession.cs:92–110`; `src/Data.NativeHost/HostStreamTransport.cs:16–51`; `src/Data.Streaming/TypedStream.cs:183–234` |
| Batch ownership | Native code writes the bounded row frame directly. Managed code receives the exact owner/view without copying the entire frame. Partial-batch compaction remains when the reserved cell-table gap must be removed. | `native/cpp/src/contracts.cpp:1106–1230`; `src/Data.NativeHost/NativeHost.cs:162–181` |
| Non-row completion | Count, nonreturning mutations and selected transaction/control entries use the private command completion route. Source/admin and uncertain-acceptance cleanup retain their required generic retirement path. | `src/Data.NativeHost/DataSession.cs:42–43`; `src/Data.NativeHost/DataSource.cs:91–120`; `src/Data.NativeHost/HostCommandController.cs` |

The old direct ABI wrappers still have actual test consumers in `tests/Query.Native/Program.cs`, `tests/Query.Binding/Program.cs`, `tests/Query.Binding/CommandOnlyTests.cs` and `tests/Data.NativeHost/Program.cs:184`. They support the frozen ABI and explicit old/new behavior oracles; they are not an unnoticed fallback in the formal Fluent path. Their remaining callers should not be described as dead code.

The former Find production body is removed. Its literal construction remains only as an invoked behavior oracle in `tests/Orm.Relations/FindShapes.cs:238–261`. That oracle is relevant because a superficially similar convenience predicate has different bounded-admission and error-order behavior.

## Find ownership, isolation and admission

`FindPlan.cs:10–56` keys the cache by exact managed Table reference. Equal schema or projection hashes therefore cannot replace the caller's mapper identity. Acquisition, LRU mutation, byte accounting and cache release use the existing `_registrations` lock. The caller retains its own reference before leaving that lock and releases it after terminal completion. Cache eviction and Source closure release the cache reference, not an active caller's lease.

`FindPlan.cs:167–175` creates an independent values frame for each execution. The cache does not retain a Session, cancellation token, physical prepared statement or previous entity-key values. The execution uses the existing typed pull and exact `Table.Row` mapper. The native import check at `query.cpp:1193–1196` prevents private Find parameter slots from entering a public query.

The reviewed tests cover exact mapper identity, distinct Sessions, entry and byte eviction, execution through a lease retained across eviction, mutable binary-key snapshots, configured money and binary keys, DDL changes, cancellation and Source close. The old/new oracle compares actual exception type, database error kind and synchronous timing at quota boundaries rather than only checking that an error occurred.

The existing Find evidence remains separately bound to its original source and receipts: native query validation records 1,017 checks and 52 SQL/ordered-argument goldens; final Find-only Native AOT validation records 1,152 actual assertions and 118 actual managed retirements, including 192 Find assertions per provider. Those dynamic totals are not a fixed test-case inventory. The earlier count erratum and failed attempts remain part of that evidence. This review did not execute those tests.

## Command completion and notification safety

`native/cpp/src/host.cpp:1154–1196` destroys the action, gate, cancellation and Source execution accessors before publishing readiness. The result state is independent; the detached notification tail retains only its independent fences and lifetime ticket. It does not read the command state again after the callback.

`HostCommandController.cs:271–325,430–499` waits for request setup, active controls, callback access and cancellation-registration drain before publishing. A successful readiness notification must yield a transferable result. Uncertain acceptance or a bridge fault uses an actual close proof; a failed Task or copied diagnostic is not treated as a retirement certificate.

If a native transaction/savepoint owner has transferred but managed adoption fails, `AbandonResultAsync` keeps and retires that child before publishing failure. The failure path does not merely drop a wrapper and infer safety. Ordinary business continuations remain off the unmanaged ready stack.

## Cancellation, early stop and row lifetime

`CursorPull::run`, at `host.cpp:2908–2920`, rechecks Source and Session admission, cancellation and close after provider metadata validation and before fetch. This preserves the previous open/fetch side-effect boundary when those states change while description is in progress.

Execution accessors leave scope before readiness; final close still joins the independent notification tail. `TypedStream.cs:229–234` preserves an original business/mapping error and attaches a cleanup failure as diagnostic information. Its cleanup at `257–300` releases the batch, drains cancellation registration and waits for actual native retirement. Concurrent disposal waits for the active move's mapping and cleanup. No new path bypassing early-stop cleanup was found in the inspected flow.

## PostgreSQL pre-COMMIT proof

The optimized pre-COMMIT path remains narrowly guarded:

- `provider.cpp:160–166,1419–1431` requires a real healthy nonblocking connection, pipeline mode off, no live statement and exactly `PQTRANS_INTRANS`.
- `host.cpp:3537–3560` additionally requires no savepoint to omit the old `SELECT 1` probe. Failed, ambiguous and depth cases retain the original probe and SQLSTATE precedence, including the `25P02` rollback behavior.
- `host.cpp:3566–3569` retains post-COMMIT confirmation before publishing Committed. A successful send alone is not confirmation.

The actual protocol assertions beginning at `native/cpp/tests/postgres_sync_tests.cpp:606` distinguish IDLE, a live described/active statement, EOF while the statement is still owned, INERROR, rollback and physical closure. The retained integrated correctness receipt records 432 real PostgreSQL protocol checks and 13 transaction families/120 checks. Those receipts are existing execution evidence, not a new run by this reviewer.

Fresh PostgreSQL metadata validation before Execute and SQLite prepare/bind without step still have actual semantic callers. Cross-execution physical-statement caching is not silently introduced by the private Find cache.

## GC reporting from the actual frozen consumers

**The frozen inputs already record absolute process-wide GC counts at the end of the offered-arrival window. No consumer modification or supplemental measurement is needed to report that scope.** Report those values separately from the steady-workload delta.

The four inspected consumer roots are:

- `/workspace/scratch/fd78534029f7/builds/candidate-sqlite-02/consumer-workload`
- `/workspace/scratch/fd78534029f7/builds/candidate-postgresql-02/consumer-workload`
- `/workspace/scratch/4a65d70f0fe1/consumers/dapper-matched-sqlite-01`
- `/workspace/scratch/4a65d70f0fe1/consumers/dapper-matched-postgresql-01`

Both Korda copies of `Measurement.cs` match SHA-256 `7112c58bfef1dc09c0c2ad1fa7511650232a9cdfc922946c2b420d5378ef6ac2`. Both Dapper copies match `fdf8f6354f3eb33bb9a77030ee050cb846d1d3eca6bcc08512df8b0d6b837952`. All four `OfferedLoad.cs` files match `2adb14584476da8b8a49bb2e5db6bd85b136f3823aee5e2f004bc263eb2bc92b`. Their Program source hashes also match the respective receipts.

At `OfferedLoad.cs:118–123`, after waiting for the offered deadline and before completing the queue, the producer samples `GC.CollectionCount(0)`, `(1)` and `(2)` directly. `OfferedLoad.cs:204` writes them into the result; `225–227` defines the fields:

- `OfferedLoad.Gen0AtOfferedEnd`
- `OfferedLoad.Gen1AtOfferedEnd`
- `OfferedLoad.Gen2AtOfferedEnd`

These are un-subtracted process cumulative values. They include startup and warmup through that offered-window boundary and cover the process's threads. They are not per-thread measurements or business-only attribution.

The top-level `Gen0`, `Gen1` and `Gen2` have a different scope. Korda `Measurement.cs:280,291,355` and Dapper `Measurement.cs:219,230,295` calculate process-counter differences from the steady measurement start until all admitted workload jobs have completed. This includes the admitted queue tail after the offered window, but precedes subsequent worker/Source disposal and idle observation.

The existing **30-second offered-load validation files** demonstrate both fields independently. The exact source for every example is shown below; these are the `*-offered-01` records, not the separate 120-second `*-baseline-01` comparisons.

| Actual raw source file | Offered seconds | Effective seconds through workload completion | Completed operations | Process cumulative Gen0 / Gen1 / Gen2 at offered end | Measurement-start to workload-completion delta Gen0 / Gen1 / Gen2 |
| --- | --- | --- | --- | --- | --- |
| `/workspace/scratch/fd78534029f7/measurements/sqlite-offered-01/candidate-c4.json` | 30 | 30.018897652 | 84,665 | 729 / 206 / 2 | 726 / 205 / 2 |
| `/workspace/scratch/fd78534029f7/measurements/sqlite-offered-01/dapper-c4.json` | 30 | 30.000172135 | 89,930 | 322 / 3 / 1 | 321 / 3 / 1 |
| `/workspace/scratch/fd78534029f7/measurements/postgresql-offered-01/candidate-c8.json` | 30 | 30.015182255 | 100,208 | 846 / 274 / 2 | 842 / 274 / 2 |
| `/workspace/scratch/fd78534029f7/measurements/postgresql-offered-01/dapper-c8.json` | 30 | 30.000029201 | 107,590 | 191 / 94 / 2 | 187 / 93 / 2 |

Correction to this review draft: the initial prose incorrectly labeled these examples as 120-second runs. A targeted reread of those four actual JSON files confirmed `OfferedLoad.OfferedSeconds=30` for each, together with the exact durations and counts above. The GC values themselves were read from these files and are unchanged. No raw evidence was modified. The source-code conclusion about the two reporting scopes is unchanged.

Those numbers are examples from the completed 30-second offered-load validations, not the 120-second baseline comparisons or final 1,800-second results. Final reporting must use each final raw file's own fields and label the two scopes explicitly.

**Boundary:** cumulative GC after the 15-second idle period or at process exit is not saved. The offered-end absolute value and workload-window delta do not determine that missing later value: they sample different boundaries, and the initial baseline is not serialized. Do not label the offered-end counts as including shutdown/exit. Do not infer missing managed-runtime GC counters from `/proc` CPU/RSS readings. Preserve this limitation while retaining the frozen consumers unchanged.

## Independent packages and CI reading

The existing `completed-17da-02` SQLite and PostgreSQL build receipts both bind exact source `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`, tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc` and `sourceDirty=false`. Each records eight successful stages with `exitCode=0` and `sourceUnchanged=true`: impact, native build, native correctness, bundle, public Native AOT consumption, public validation, phase consumer build and mixed-workload consumer build.

The earlier two `cb233a7` package failures with `NWPKG005` remain valid failed-attempt evidence. The selected candidate adds the normative Find extension descriptor to the exact native-export inventory; it does not weaken the export audit. Those historical failures must not be reassigned to the corrected candidate, and earlier module-level correctness must not substitute for independent package consumption.

The reviewed CI diff preserves the existing architecture:

- `ci.yml` is unchanged.
- The two benchmark module registrations contain path ownership under `tests` and no `run` or `checks` command. They do not execute load in CI.
- Build workflow additions preserve correctness failure logs.
- Release workflow additions preserve actual registry bytes and public-consumption/verification receipts.
- Planner tests explicitly require benchmark-only edits to select no jobs while retaining affected product/package routing.

The prior actual CI receipt for 17da records the selected interop, Linux, SQLite and PostgreSQL checks succeeding, with publication skipped for the PR as intended. This is a reading of the retained receipt, not a live status query or proof of a later merge/release outcome.

## Material remaining claims and final acceptance

1. Current allocation evidence retains `FrameworkOnlyBytes=null`. Framework-only zero managed allocation is not established. Separately scoped business DTO/List evidence and end-to-end process totals must remain separate, without invented subtraction.
2. Dynamic NWQC semantic traversal, general ShapeCache lookup outside private Find, owned SQL/Expectation data, parameter snapshots, canonical batch validation and per-batch scheduling remain. This review supplies no isolated latency/CPU cost for those components.
3. PostgreSQL metadata-before-Execute and SQLite no-step-at-open behavior continue to protect the retained public contracts. A shorter upstream sequence is not automatically equivalent under those contracts.
4. The rejected close-quiet `92b` experiment remains distinct from frozen 17da. Correctness success did not satisfy its selected performance rule. Do not mix its consumers or results into the formal candidate.
5. Final stopping rationale must cite the actual reproducible measurements, retained failed experiments and remaining measured gaps. This source reading does not prove that every possible future optimization is exhausted.
6. Four final serial long-run cells, final evidence acceptance, reviewed normal merges, existing CI and rule-selected publication/readback remain separate delivery obligations. This review grants no credit for obligations not yet observed complete.

[product]: https://github.com/IzuSharp/Korda/commit/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa
