# Independent stopping-basis review — frozen 17da candidate

Review date: 2026-11-26. Reviewer: `implementation_review`, a continuation worker that did not author the selected implementation. This is a source and existing-evidence review performed on CPU 8 during the final serial workload campaign. It does not execute or requalify the product.

## Decision

**No new concrete correctness defect was found that requires interrupting the frozen campaign. The selected execution-path refactor can be assessed as an implemented, specifically validated set of changes. The available evidence does not establish zero framework allocation, performance parity with Dapper.AOT, or exhaustion of all further measurable improvements.**

The strongest defensible stopping statement is: retain the best validated candidate among the alternatives actually evaluated, publish its measured improvements and remaining gaps, and reject the evaluated alternatives that failed their stated criteria. A statement that the entire execution path is now optimal, or that no further measurable gain exists, would exceed the evidence. If final acceptance requires that stronger statement, this review leaves that acceptance condition unresolved.

This distinction matters for the user's full-refactor request. Keeping an internal boundary can be a considered implementation decision after examining upstream and actual callers. Its continued existence does not make it a public contract or prove its present encoding, copying and allocation cost irreducible. Conversely, a remaining allocation or slower result is not by itself evidence of a correctness defect.

The fourth long-run observation and its final evidence checks were still pending when this review began. This document grants neither final campaign acceptance nor merge/publication credit. Final result figures should come from the campaign's verified raw records, not progress messages or this source review.

## Exact source and review scope

| Identity | Value retained from the preceding identity review |
| --- | --- |
| Product worktree | `/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-korda` |
| Local HEAD | `040911c5abdee740c0cd9fbf8295bf511c9cc69d` |
| Local tree | `bc9087d843d8d741d83d44f53d0b2c5af26dcffc` |
| Public frozen candidate | [`17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`][product] |
| Public candidate tree in the existing receipts | `bc9087d843d8d741d83d44f53d0b2c5af26dcffc` |

This pass did not rehash files or recheck Git identities during the long run. It used the source/tree binding already recorded in `review-implementation-01.md` and the unchanged current allocation audit. It read the selected source paths listed below, the current allocation audit, the rejected final-close experiment, the historical native-path review, and the previously rejected inline-completion explanation. Earlier evidence is attributed to its own source rather than relabelled as a new 17da measurement.

No product or repository file was changed. No build, test, profiler, benchmark, compression or hash scan was run. The new artifacts are this intermediate review draft and, following a separate request, its Markdown/JSON extraction of existing FFI records.

## What the selected refactor has actually completed

The earlier independent implementation review found the public Fluent entry selecting the complete-command path, with no silent fallback to the previous per-node native composition route. The complete command compiles directly into an executable native plan. The selected implementation removes redundant command adaptation frames and private builder clones; it does not remove the bounded NWQC command language or its native semantic traversal.

The current private `FindAsync` body uses a bounded source-owned immutable shape, exact Table/mapper identity, an independently owned key frame and the ordinary typed pull path. It bypasses the general native shape-cache hash/LRU lookup. It does not cache Sessions, cancellation state, prior values or physical database statements. The historical native-path review predates this Find change and must not be quoted as a description of the final Find route.

Prepared execution retains the compiled parameter layout and the immutable stream projection layout. General immutable command shape reuse is implemented at runtime. The evidence does not demonstrate source-generated SQL templates for arbitrary fixed Fluent method bodies. Generated model/projection/DTO readers, runtime `.Prepare()` and the specialized Find shape are the actual mechanisms; they should be named accurately.

The provider, native batching, pull transport, generated DTO mapping, non-row command completion and selected transaction paths are connected to formal public APIs. Native batches are exposed as an owned view rather than copied wholesale into a second managed frame. The old direct ABI wrappers still have invoked compatibility and behavior-oracle test callers, so their existence is not proof of an unused production fallback. The prior review gives the related entry, ownership and assertion locations.

## Allocation evidence and the 0 B target

The current [allocation audit][allocation-local] explicitly reports `timingCredit=false` and `FrameworkOnlyBytes=null`. It contains 12 instrumented records covering two providers, candidate/Dapper and 1, 100 and 1,000 rows; candidate records include Fluent, prepared and full SQL routes. Its 72 windows account for 18,432 operations. It has no current before-allocation overlay and no standalone Find allocation result.

That audit separates two instrumented scopes: actual generated-reader mapping, and the actual result List constructor plus Add calls. The mapper scope includes temporary allocations made inside the generated reader's codec or driver calls. It is therefore not a pure retained-business-object size. Process allocation covers the whole measured window, including the instrumentation's semantics and the consumed business results. The audit deliberately does not subtract the two scopes from the process total to label the remainder framework allocation.

Selected examples illustrate why the remaining gap is real but cannot be assigned to an individual layer by subtraction:

| Provider and rows | Fluent process B/op | Prepared process B/op | Full SQL process B/op | Dapper process B/op | Mapper plus List scopes B/op |
| --- | ---: | ---: | ---: | ---: | ---: |
| SQLite, 1 | 19,551.8125 | 2,569.3229 | 8,119.3125 | 2,131.3646 | 136.0000 |
| PostgreSQL, 1 | 19,555.8021 | 2,568.0625 | 8,116.9896 | 2,108.1250 | 136.0000 |
| SQLite, 100 | 26,651.4062 | 9,769.3646 | 15,338.2604 | 9,251.3646 | 7,256.0000 |
| PostgreSQL, 100 | 26,640.4375 | 9,742.4167 | 15,314.9792 | 9,246.0625 | 7,256.0000 |

These are the existing instrumented phase workload's observations, not ordinary latency measurements or the final mixed-workload B/op. In particular, the approximately 25 KB/op process total discussed for the mixed campaign cannot be reduced by subtracting a single-row or 100-row mapper scope from this different workload. The mixed operation population, business results, async work, harness and observation boundaries differ. No numeric framework-only result follows from that calculation.

Source inspection nevertheless prevents a claim that framework allocation is already zero. The ordinary stream path constructs a `TypedStream`, a transport wrapper and cancellation ownership; transport construction creates a scoped batch owner, a close controller and a pull controller. Enumeration creates an Enumerator with a gate. The command completion path creates a controller with a gate and `TaskCompletionSource<T>`. Parameterized Find and prepared executions create a value frame. Those are framework allocations in the implementation, although this review does not assign their exact size or frequency within the mixed operation population.

The allocation goal is therefore **not established as achieved, and the general selected paths still contain framework allocations**. `FrameworkOnlyBytes=null` means the exclusive numeric attribution is unavailable; it does not mean zero, and it does not mean every observed process byte is framework overhead.

Evidence locations: allocation audit lines 3–18 and 37–66; `QueryContext.cs:175`, `HostStreamTransport.cs:16`, `HostCommandController.cs:38`, `TypedStream.cs:95` and `FindPlan.cs:160`. See the fixed-source links below.

## Remaining responsibilities: contract versus implementation choice

| Remaining work | Actual selected behavior and contract purpose | What the evidence does not establish |
| --- | --- | --- |
| Dynamic command construction and NWQC parsing | `QueryCommand` owns records and imported dependencies. The small single-root route copies the records into stack scratch. The general graph route constructs indices/origins/owners and one bounded final byte envelope. `QueryCommandReplay` validates that envelope and drives the authoritative native semantic builder. Source, capabilities, limits, scalar origin identity, import ownership and error behavior still need enforcement. | The record buffer, its final copy and the NWQC format are implementation choices. They have been retained after deleting redundant adaptation, rather than eliminated. Neither their individual current cost nor a faster semantics-equivalent alternative has been established by this review. They are not permission to describe dynamic execution as encoding-free or parse-free. Prepared execution does not rebuild this command on every execution. |
| Value snapshot and native argument ownership | Prepared parameter encoding holds the parameter gate across validation and writing one result frame. Parameterless prepared calls share an immutable empty frame. Find builds a separate frame per execution. Native render parses the caller frame against the compiled expectation and copies each value into owned `Scalar` storage before asynchronous execution can outlive the input view. | Snapshot isolation and lifetime independence are required. The exact combination of managed frame plus individually owned native cells is not proved to be the minimum-copy representation. A redesigned ownership transfer or borrowed representation needs an explicit lifetime proof, not merely deletion of a copy. No isolated timing or allocation is attached to these copies here. |
| Immutable SQL and metadata reuse | Parameter descriptors and schema identity are compiled once for prepared execution. Prepared and Find streams reuse a frozen projection layout. Ordinary stream construction still builds its expectation and descriptor structures. Native render copies the compiled SQL and expectation into its owned result; `SqlPlan::rendered` moves that result onward. General shape acquisition still assembles ABI plus identity bytes, hashes them, locks and searches the bounded cache. Find already skips that cache. | Rechecking source identity, collision identity and bounded ownership is valid. Rebuilding a hash input for an already immutable shape and copying immutable SQL/expectation on each render are concrete remaining redundant-work candidates, not requirements implied by those checks. Their measurable benefit, implementation complexity and regression risk have not been isolated. It is inaccurate to say all metadata is reconstructed on every prepared call, or that all metadata work is already hoisted. |
| Dispatch, callback and retirement state | Pull and non-row command routes retain setup/control/callback ownership, cancellation-registration drain, generation accounting and independent notification-tail proof. Business continuations stay off the unmanaged ready callback stack. The rejected inline experiment exposed a real post-publication exception boundary. | The safety responsibilities are justified; every current object or queue hop is not independently proved necessary. Phase `read-complete` includes more than dispatch and cannot attribute an individual queue's cost. Pooling or combining state would need to preserve those proofs. This review makes no claim that dispatch dominates the remaining gap. |
| Provider description, execution and connection reuse | PostgreSQL sends Parse and Describe together and waits for their common Sync confirmation. Bind/Execute starts at first fetch. Fresh description preserves the existing open-side-effect and DDL/error behavior. SQLite prepares/binds without stepping at open; its temporary text/blob binding storage uses `SQLITE_TRANSIENT`. Natural PostgreSQL EOF reuses its actual completion proof, while unfinished execution and transaction publication retain required drain/confirmation. | A warmed physical statement or a different metadata policy might be faster, but cannot be substituted merely by copying a driver optimization without checking Korda's public error and side-effect semantics. The evidence supports the selected conservative policy; it does not prove no equivalent connection-local cache could ever be designed. A libpq submission counter is not a count of network round trips. |
| Result transcoding and batching | Provider values are validated/encoded into the bounded native batch. `BatchWriter` writes the row frame directly and compacts a partial batch when its reserved cell-table gap would remain. Managed take receives the native owner/view directly, then generated mapping constructs owned CLR values. This protects row lifetime, byte limits and the prohibition on borrowed spans escaping across awaits. | Result materialization and native-to-owned-value transfer have real responsibilities. The chosen canonical frame and partial-batch compaction are not individually timed in the available phase result. There is no evidence for claiming either that all copies have disappeared or that a hypothetical direct mapper would be semantics-equivalent and faster. |
| Full SQL capture | The explicit SQL plan owns decoded argument cells and retains the original parameter frame. `host_abi.cpp:263` compares any subsequently supplied execution bytes with that captured frame and rejects changed raw command arguments. | The retained raw frame has an actual caller and is not dead memory. A different exact-match or ownership design may reduce retention, but deleting it outright would remove an observable argument-capture check. Its performance share is not isolated. |

Precise source points are `QueryCommand.cs:18,55`, `QueryCommand.Submission.cs:13,34`, `QueryCommandReplay` at `query.cpp:2599` and its actual compile callers at `2933` and `2954`; `QueryContext.cs:251,287`; `TypedStream.cs:30,41,64`; `query.cpp:3083,3182`; `host.cpp:1545,1571`; `provider.cpp:747,827,945`; `contracts.cpp:1106,1207`; and `NativeHost.cs:162`.

The native scalar Count path also parses its fixed scalar projection in `SqlPlan::rendered` at `host.cpp:1561`. That is another concrete metadata-reuse question. This review does not claim that removing it would materially change the mixed result.

The contract evidence is not purely commentary: current Find assertions check equal-metadata mapper identity and independent snapshots (`tests/Orm.Relations/FindShapes.cs:54`), mutable binary-key ownership (`:130`) and warm DDL rejection with reusable-session cleanup (`:304`). The PostgreSQL protocol assertions check the actual Parse/Describe/Sync group, no Execute at metadata completion and safe physical reuse (`native/cpp/tests/postgres_sync_tests.cpp:1097`). The independent implementation review records the command completion, cancellation, held mapping and transaction proof assertions. Reading these sources is not a new execution of those tests.

## What the rejected alternatives prove

The [already-released final-close experiment][close-local] is a useful bounded stopping decision. It started from exact 17da, changed only control dispatch when existing closed-admission/fetch-fence/cleanup proof already showed release, kept the fallback, and declared its selection rule before measurements. Its ordinary paired observations were eligible and correct, but the change did not meet the rule: PostgreSQL single-row prepared read-complete p50 regressed in the first round and improved in the second; SQLite 1,000-row pooled per-operation total p50 regressed by 6.78%, beyond the 5% guard. Retaining 17da rather than selecting the experiment is supported by those observations.

That outcome rejects the particular dispatch change under the recorded conditions. It does not measure all dispatch costs or reject precomputed immutable metadata, value ownership changes, dynamic-command changes or other unrelated hypotheses. The experiment record itself says its phase timer does not separately attribute each queue.

The [earlier inline-completion experiment][inline-local] was rejected for a different reason, before AOT execution or performance measurement. Review of the pinned runtime found that completion publication precedes continuation dispatch, and dispatch is not a no-throw operation. Re-setting the generation, setting an exception again or disposing an already delivered batch does not repair a post-publication failure. This is a concrete correctness constraint on that proposed shortcut. It supplies no performance credit and no blanket proof that the current scheduling design is optimal.

The historical native-path inventory identifies additional copies and cache work, but is a source inventory, not an attribution profile. The final evidence should retain that distinction and the historical source identity.

## FFI, SQL dispatch and required protocol replies

The requested quantities have different evidence coverage. The current ordinary phase and mixed consumers serialize native `SqlExecutions` and `ProtocolSubmissions` endpoints. Their ordinary records do not serialize FFI call arrays or counts of required protocol replies. `SqlExecutions` counts actual provider dispatches, including internal controls in the window; it does not prove that every dispatched statement completed successfully on the server. `ProtocolSubmissions` counts successful libpq send/Sync API calls. It is neither a server reply counter nor a network RTT counter.

**Actual current-candidate FFI evidence does exist separately.** The six existing files under `/workspace/scratch/fd78534029f7/measurements/{sqlite,postgresql}-single-diagnostic-01/diagnostic-{numeric,tx-rollback,tx-commit}.json` contain `Before/After/Drained.Ffi.Calls`, `PendingReturns` and `OkReturns`. Their `diagnostic-build.json` receipts under `/tmp/DB-Exec-10-diag-{provider}-ffi-01` identify `abiSourceCommit=17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` and the current candidate-02 ordinary consumer/package/native identities. This review extracted the exact existing integer endpoint deltas into `final-ffi-diagnostics-01.json` and a concise table in `final-ffi-diagnostics-01.md`. It did not rehash the binaries or execute the consumers.

Those six observations are 15-second, C1, persistent-session, instrumented single-case runs. Numeric requests 32 rows, and the other cases are full commit/rollback operations. They have no timing or allocation comparison credit. They are not the 1/100/1000-row phase suite or the 30-minute mixed campaign. Their measured call arrays fill that precise diagnostic scope; they cannot silently fill the absent ordinary-workload fields. The older `ffi-single-command-*` observations remain separately bound to command candidate `8789a45a52cc0cc0a0b62737542d9c120b753c9b`.

The current diagnostic inventory has 60 wrapped symbols, but 60 is a static inventory size rather than a count of calls per query. Each array counts managed-to-native Korda ABI invocations; it excludes native-to-managed notifications, internal C++ libpq/sqlite calls and the diagnostic counter reads themselves. A release invocation is not necessarily a distinct non-null buffer release. `NW_PENDING`, managed suspension and `poll()` counts do not count mandatory server replies.

The real PostgreSQL proxy tests separately observe protocol groups and selected forwarded `ReadyForQuery` replies. Their narrow healthy commit/retirement window observes the change from 2 to 1 SQL dispatch, 6 to 4 forwarded `ReadyForQuery` replies, and 10 to 6 successful libpq submissions, with 2 standalone Sync messages retained. Those historical negative-control and selected commit-proof receipts have their own source identities; retaining their assertions in final 17da does not relabel the original executions. The proxy does not individually count all ParseComplete, BindComplete, DataRow and CommandComplete messages. It does not provide final long-workload reply totals or RTT.

`BatchResultTests` pull-count assertions and the source protocol map establish specific call/EOF behavior, not measured whole-workload FFI or required-reply totals. Dapper's ordinary consumers also lack corresponding internal SQL/FFI/reply instrumentation. These limits remain unmet measurement scope, rather than quantities that can be supplied by multiplying a source diagram or renaming a submission counter. The existing `continuation-7/counter-semantics.md` describes the endpoint and counter definitions in detail.

## Defensible final acceptance language

Final reporting can say that the selected public execution route was replaced and validated, name the removed redundant paths, state the ordinary and long-run improvements against the matched baseline, state the remaining Dapper gap, and explain why the specific tested alternatives were not selected. Throughput under a frozen arrival rate should retain offered, completed, failed and rejected counts; it should not be relabelled as the maximum sustainable throughput without a separate saturation result.

Final reporting should also state that zero extra framework managed allocation remains unmet/unproven numerically, with actual per-execution allocations still present. The instrumented mapper/List scopes and process allocation measurements remain useful evidence without being converted into an unsupported exclusive framework number.

For GC, the actual frozen mixed consumers support two different process-wide scopes already documented in `review-implementation-01.md`: absolute cumulative counts through the end of the offered-arrival window, and the delta from measurement start through completion of the admitted workload. The latter includes the queue drain. Neither is an absolute counter at process exit or after the subsequent idle interval; those endpoints are not recorded. The two scopes must remain separately labelled.

There is no new correctness blocker from this source pass. There **is** a limit on the completion claim: selected refactor completion and global performance exhaustion are different propositions. The measured selection process supports the former and a bounded decision to retain this candidate. It does not establish the latter. Further optimization questions above are concrete but unmeasured; none should be given fabricated per-layer costs or assumed benefits, and none justifies silently changing the frozen candidate during the final campaign.

## Source and evidence references

All product links below pin the frozen public candidate. Local evidence references identify the exact existing review inputs; they should acquire their final Plan commit links when this draft is archived.

- [Managed command construction][command] and [submission][submission].
- [Fluent stream and prepared parameter layout][context]; [private Find execution][find].
- [Typed stream projection layout and enumeration][stream]; [host stream transport][transport]; [command completion controller][completion].
- [Native command compiler, rendering and shape cache][query].
- [Native SQL plan and host][host]; [raw captured-argument check][abi].
- [Provider preparation, binding and execution][provider]; [native batch writer][contracts]; [managed native batch take][native].
- [Current instrumented allocation audit][allocation-local].
- [Rejected final-close experiment][close-local].
- [Rejected inline-completion explanation][inline-local].
- Current diagnostic extraction: `/workspace/scratch/166b48a091b9/recovery/final-ffi-diagnostics-01.md` and `/workspace/scratch/166b48a091b9/recovery/final-ffi-diagnostics-01.json`.
- Counter definitions and separate protocol-test scopes: `/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/counter-semantics.md`.
- Prior independent source/contract/GC review: `/workspace/scratch/166b48a091b9/recovery/review-implementation-01.md`.
- Historical native-path inventory: `/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/native-path-review.md`.

[product]: https://github.com/IzuSharp/Korda/commit/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa
[command]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Query.Binding/QueryCommand.cs#L18
[submission]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Query.Binding/QueryCommand.Submission.cs#L13
[context]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Query.Fluent/QueryContext.cs#L175
[find]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Orm.Relations/FindPlan.cs#L160
[stream]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Data.Streaming/TypedStream.cs#L30
[transport]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Data.NativeHost/HostStreamTransport.cs#L16
[completion]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Data.NativeHost/HostCommandController.cs#L38
[query]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/src/query.cpp#L2599
[host]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/src/host.cpp#L1545
[abi]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/src/host_abi.cpp#L263
[provider]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/src/provider.cpp#L747
[contracts]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/native/cpp/src/contracts.cpp#L1106
[native]: https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Data.NativeHost/NativeHost.cs#L162
[allocation-local]: /workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/current-measurements/allocation/README.md
[close-local]: /workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/close-quiet-experiment.md
[inline-local]: /workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-plan/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-5/README.md
