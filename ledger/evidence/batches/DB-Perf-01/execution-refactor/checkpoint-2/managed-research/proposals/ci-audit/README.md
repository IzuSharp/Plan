# Selected default CI measurement audit

Base: Korda `a27ff3189bd48b9c08d58e38338b2bfde7669bdd`, tree `8baba7285c0f4ccaa15e88e02c2327e9bc3c6b58`. No change is applied to that checkout. `manifest.json` binds this audit to the existing `artifacts/plan.json`, the exact action list, the search scopes and hashes of the matched source files. `all-matches.txt` preserves all 771 matches in 76 files; matching a word such as “profile” is not evidence of a performance workload.

## Independent integration checkpoint

The coordinator approved the proposal. It was applied and committed only in `/workspace/scratch/17ac3f8f2fbf/worktrees/DB-Exec-02-ci-correctness` as `e125bcd8bebb27e60a1172ab64d9dec3a996e4e2`, tree `898ff6959cabfeab4c4725e2c9c277973b4ae30c`. Frozen B remains at a27ff31. Affected default AOT entry validation is underway; Streaming, Fluent and NativeHost have passed, with the exact existing B native producer hashes. This is separate from the final complete verifier, which remains pending after final native integration.

## Correction to the earlier review

The initial `ci-measurement-review.md` incorrectly said the Data.Abstractions component verifier did not call its profiling flags. Its default `verify.py` does call four such processes. That statement is explicitly corrected in the original review and in the managed gate ledger. This audit follows both the C# flag dispatch and the Python call sites; a diagnostic being behind a flag does not by itself keep it out of CI.

## Actual selected action closure

| Selected actions | Default execution reviewed |
| --- | --- |
| `interop.async` | `tests/Interop.Async/verify.py`, actual Async AOT cases, native execution fixture, compiler/API and sample checks |
| `database.native`, `database.dependencies` | `eng/build.py`, `eng/task07_native.py`, native graph/provenance/format checks, full CMake test inventory and native tests |
| `database.build` | Workspace library/compiler/API projects; restore/build/format. It excludes ordinary consumer applications |
| `database.api`, `api.tool`, `fluent.api`, `migrations.api`, `relations.api` | API documentation composer/negative fixtures, exact compiled API/XML checks, generator API check; no benchmark application |
| `database.regressions` | `eng/database_regressions.py`: native CTest, isolated actual PG administration/input/synchronization, ABI generation, Negotiation/Execution, Abstractions/Transactions/Streaming/Codecs/Binding/Query.Native component verifiers, AOT Host/Migrations/Materialization/Fluent/Relations, cross-process migration and negative relation compilation |
| Each provider's `build`, `dependencies`, `test`, `packed-api` | Existing independent native producer/profile, selected ABI CTest, actual provider failure/correctness fixtures, extracted shipped DLL/XML API checks |
| `public.pack`, `public.consume-aot`, `public.validate` | Bundle composition, `eng/ci/consume.py`, independent/combined package samples, the order workflow's actual generated ORM cases, package identity/dependency/native-payload validation |

The action list contains no benchmark workflow or performance action. This does not excuse the profiling calls found inside the ordinary component verifiers below. The proposal changes those call sites; it does not change workflows, action selection, package scope or publishing policy.

The public consumer route also includes `eng/ci/orm_experience.py`, `samples/api/orm-experience`, and `samples/api/packaging-domain`. Their tests check generated SQL, DTO results, transactions, cancellation, no-dispatch cases, scaffolding and tutorial compilation. Per-command elapsed seconds in Python receipts describe command execution and failure timeouts; they do not repeat/score workload latency, CPU, RSS or throughput. They remain unchanged.

## Default profiling removed or rerouted

| Default route at the base commit | Sampling behavior | Default correctness retained | Explicit local home |
| --- | --- | --- | --- |
| Abstractions `managed-allocation-regression` | Nine scalar lanes, 100,000 operations, warmup and three allocation/GC/time windows | Existing scalar/JSON/UTF8/decimal malformed and differential suites | Existing `--allocation-probe --allocation-regression` |
| Abstractions `owned-wire-allocation-regression` | Owned rows at 0/1/128/4,096; warmup and three 256-operation windows; exact-zero assertion | `WireValidationTests.Run`: every supported storage mode, arbitrary nonoverlapping order, overlap/range rejection, NULL/empty, descriptors; complete wire tests in Program | Existing `--owned-wire-allocation-regression` |
| Abstractions `control-record-allocation-regression` | 2,048 warmup, three 8,192-operation windows, 136 B/op ceiling | `ControlRecordTests.Run`: fixed full goldens, input/output identity, independent copies, error order, exact 4 MiB boundary and arithmetic limits | Existing `--control-record-allocation-regression` |
| Abstractions `managed-configured-scalar-regression` | Eleven configured scalar lanes, 100,000 operations and three windows | `ConfiguredScalarProbe.Verify`: all configured codecs, precision/scale and malformed representation matrix | Existing `--configured-scalar-probe --allocation-regression` |
| Binding `projection-allocation-aot` | Warmup and three 8,192-operation windows, calibrated byte ceiling and elapsed ticks | `ProjectionEncodingTests.Run`/`RunSelection`: independent complete golden bytes, descriptor/binder order, failures, scratch poison, ownership, concurrent outputs, native synchronous borrow, exact byte bounds | Existing `--projection-allocation` |
| Binding `projection-scratch-allocation-aot` | Scratch window counters, time and exact zero | Same default projection/scratch/selection tests | Existing `--projection-scratch-allocation` |
| Streaming `aot-allocation-gate` and implicit ordinary entry | Sixteen numeric in-batch windows; exact-zero process allocation | Stable batch contracts, independent row leases, exact mapped results, finite cancellation/disposal race tests | Existing `--allocation-gate-only` / `--allocation-probe` |
| Streaming `aot-owned-batch-gate` and implicit ordinary entry | Copy/owned lanes, warmup and three batch windows, byte-delta/512 B ceiling | Every original `OwnedBatchProbe.Correctness` assertion moves into the default path. Two batches per storage lane additionally consume every row, check full numeric values/count/checksum and each owner's exact take/release counts without counters | Existing `--owned-batch-probe-only` |
| Streaming `aot-row-lease-reuse-gate` | Three attachment windows, whole-process exact-zero criterion | `RowLeaseReuseChecks.RunAsync`: owned/unmarked/native storage, reattachment, stale state, malformed later batch, independent enumerators, custom/reentrant mapping and public codec/token/lifetime checks | Existing `--row-lease-reuse-probe-only` |
| Streaming ordinary process receipt | Start/end allocated bytes, working set and peak working set around all provider correctness tests | Explicit row/byte reservations, fetch/operation counters, native/managed owner retirement, SQL reuse and provider cases remain | Explicit allocation probes already record raw counters with their narrower scope |
| Fluent `MeasureEmptyParameters` | Warmup/16,384 calls, timing/GC and allocation records | Independent complete 96-byte empty frame, repeated byte equality, source/declared/foreign/missing/extra validation, immutable shared frame, no SQL/native owners | Existing `benchmarks/db-perf/empty-parameters` |
| Fluent `MeasurePreparedConstruction` | Three 10,000-construction windows, GC/time and calibrated allocation ceilings | First/repeated zero- and one-parameter lazy construction, no SQL/native owners, existing captured values and lazy error-order tests | Existing `managed/PreparedProbe` |
| Fluent `MeasureComposition` | Repeated composition timing and allocation/GC receipt | Repeated complete SQL equality and composition literal frame size; the separate empty-parameter case checks the complete golden; no execution, all query owners released | Existing `query-phases` |
| Host default `SnapshotProbe.VerifyAllocationBudget` | Two 10,000-operation allocation windows, normal/provider byte ceilings | The separate default `SnapshotProbe.Verify()` remains, including complete differential parser, truncated/mutated/unknown/control-field tests | Existing `--snapshot-probe` now invokes the preserved budget check before its explicit windows |

These are thirteen named default probe groups plus Streaming's aggregate process telemetry. Default Python routes to nine flag-driven processes are recorded verbatim in `profiling-entry-routing.txt`; Fluent and Host calls are direct C# calls. The proposal preserves the explicit local commands and documents them under the existing local benchmark README. None is automatically invoked by a workflow, default verifier, release or package-build script after the proposed change.

## Counter and clock uses deliberately retained

### A published no-allocation contract

`EngineInfo.Supports` has an explicit public XML promise in `src/Interop.Negotiation/EngineMetadata.cs`: no native call and no per-call allocation. The API reference and guide repeat it. This differs from a calibrated internal allocation objective.

The proposed `Coexist` change replaces 100 warmup and 10,000 sampling iterations with initialized known/unknown capability calls. It asserts both boolean values, equal thread allocation counters, and the unchanged native bootstrap call count. There is no timing, repeated sampling, GC generation report or B/op result. This keeps the published contract in ordinary correctness checks. The guide is updated to describe the finite check rather than the removed 10,000-call window. Public XML and signatures stay unchanged.

### Resource quotas and rejection before copying

`Orm.Relations/SnapshotBounds.cs::CapacityAllocation` measures one rejected operation against an already allocated oversized input. It checks `ResourceLimit` and absence of a copy proportional to that oversized input, along with exact admitted wire boundaries, no-dispatch counts and original converter-error precedence. It is a finite input-admission safety assertion, not a throughput/allocation sampling campaign. Retain it. No per-operation performance report or warmup window is added.

`Data.Migrations/Program.cs::ManifestBounds` similarly checks aggregate UTF8 size rejection before script-sized allocation and the exact 4 MiB encoded boundary. Its focused `--manifest-bounds` entry is not called by the selected default driver; it remains available. Its allocation delta is a rejection-before-copy oracle, not a repeated hot-path budget.

### Finalizers, race control and timeouts

The GC collections in Interop.Async/Execution, Transactions and Streaming borrowed-owner tests deliberately force finalizer or owner-lifetime pressure while a callback, batch or close is live. There are no bytes/time/throughput measurement windows around those collections. Keep all of them.

`AllocationProbeRaces` uses a diagnostic fixture to test deterministic handoff, stop, cancellation, mapper/consumer failures, held readers and release ordering. Despite its name, the default race entry does not call the measurement windows. `StableBatchTests`, `RowLeaseReuseChecks`, `BorrowedBatchHostTests`, and all controlled race or lifetime assertions remain.

Stopwatch/steady-clock uses for bounded waits in Data.Streaming, Data.NativeHost, Query.Native and native fixtures remain. Migration cancellation/backoff timing, SQLite busy timeout, PG init/drain deadlines, forced fault holds, and the provider's first-row-before-full-materialization assertions protect behavior. They do not calculate throughput, percentiles, CPU or memory results. Their finite waits and minimum/maximum bounds are not removed.

Native `Clock::now` in SQLite fixture path uniqueness does not measure performance. Native fixture delayed retirement models the quiet/owner-release protocol and remains. Terms such as `profile` in provider capabilities, codec profile IDs, packaging platform baselines and dependency manifests do not mean profiling. Data.Codecs, Query.Native, Materialization, provider tests, API tests and public consumers have no additional default pure-performance windows in the reviewed closure.

## Patch and verification status

`../ci-default-measurement-separation.patch` supersedes the two earlier smaller proposals. It changes twelve existing files; `../ci-default-measurement-separation.json` records every before/after SHA and the base commit/tree. At the initial proposal checkpoint it was apply-checked against the frozen candidate; subsequent independent integration and AOT checks are recorded above. It is not applied to frozen B. The preview directory is scratch only. Native and production implementation files are untouched.

The active empty-parameters harness is the only remaining non-archived caller of deleted `ParameterDefinition.Encode`; its two references are fixed through existing `PreparedParameterLayout`, without restoring the deleted wrapper. Reproduction snapshots under `benchmarks/db-perf/reproduction-inputs/by-sha256` are historical byte evidence and are not edited. Their old references remain intentionally bound to old source snapshots.

Final acceptance requires applying the combined patch only after the coordinator selects and freezes the final native/managed candidate, then rerunning the affected default AOT/API gates and existing impact planning. This scratch apply-check is not a passing C# or integration result. No measured B/C/R4 binary is changed by this proposal.
