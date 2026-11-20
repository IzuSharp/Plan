# Perf-01 retained product source review: 2e3995df

## Verdict and scope

**The retained implementation has no newly identified definite source defect in the boundaries reviewed below. Final product acceptance is held.** During this review, final003 gRPC capacity results introduced two `IntegrityFailure` probe classifications and two unexpected duplex `Cancelled` outcomes. Their exact failed event messages have not yet been inspected in this review. They require resolution before a final correctness or long-run acceptance claim; the successful finite gates do not override them.

This is an independent technical source assessment on 2026-11-20, not a GitHub approval, performance decision or merge authorization. It compares frozen baseline `ea5fa528035d025bd7a28698ee7c71194432236c` with retained public commit `2e3995df8d86583ee9443348276ca8d918056bfc`, tree `246de1eb9368efbc62f46ce10c4a8a894d646152`. Explicit Git objects were used: the canonical local product working tree remained clean at the earlier `0715ffb6` and was not mistaken for the retained head.

The source tree equals the actually tested corrected control `db95a9fbdd18c208ba8fa3fdb6dabaa2bcc073c0`. CI127's actual merge checkout `d4a51f16c8154ee026a8fe0e1975f7ce087d90d5` also has that exact tree. These equalities permit source comparison; they do not rename either producer or equate their binaries, compiler environments or package versions.

Only source, existing reviews and bounded result/checklist metadata were read on CPU 8. No tests, builds, modules, verifiers, payload readers, profilers or workloads were executed, and no artifact payloads were rehashed. The full final003 short matrix, capacity conclusion and five final 30-minute groups remain outside this review's acceptance credit.

## Retained source boundaries

### Default metadata reuse and Native AOT import ownership

`EngineDescriptor.Inspect` in `src/Interop.Negotiation/EngineMetadata.cs` caches only a successfully completed default inspection. Its volatile read and compare-exchange publish the immutable `EngineInfo` after `EngineModuleLoader.Inspect` returns. `EngineInfo` owns a read-only capability snapshot; the descriptor manifest is immutable. Non-null options still enter the original snapshot, explicit-path, capability and module-identity checks. A failed inspection cannot populate the descriptor cache, and another descriptor still reaches the original conflicting-module checks.

`EngineModuleLoader.AssemblyResolver` retains the validated immutable `LoadedModule`, not merely a borrowed handle. Each recognized cold import callback obtains a separate OS reference using the single-argument `NativeLibrary.Load(module.Path)` and transfers it only when the returned handle equals the resident handle. A mismatched acquisition is freed and rejected; an unknown alias still returns zero. No resident reference is freed and there is no recursive resolver call. This matches the locked Native AOT CAS-loser ownership path previously reviewed in [resolver ownership](../source-aot-resolver-ownership.md), rather than relying on import warming. It adds work to cold fixups, not every already-fixed native call.

The historical [A02 regression](../checks/R1-A02-001/README.md) covers concurrent default first use, premapping repair, explicit options after cache priming and independent descriptor conflicts at its own recorded commit. The retained source was reread here; that older gate is not relabeled as a run of `2e3995df`. The cold-import differential controls and later CI/AOT evidence retain their separate identities.

### Lazy stream waiter and JSON buffer ownership

`TypedStream<T>.Enumerator` in `src/Data.Streaming/TypedStream.cs` preserves the active move under `_gate`, including synchronous row materialization. Disposal creates a shared completion source only if a move is active, marks the enumerator closed under the same gate, requests stop and awaits that move before cleanup. The move clears its active flag and detaches the waiter in `finally`, then completes it outside the gate. Successful, failing and EOF paths retain the same once-only cleanup task and actual provider retirement join. A second move is still rejected, and no buffer is released while the admitted mapper is running.

`tests/Data.Streaming/Program.cs` has deterministic blocked-mapper success and failure cases: two disposers remain pending while a native batch is live, another move is rejected, exactly one batch disposal and provider join occur, and disposal still waits for the provider retirement receipt. This assessment reuses the reasoning in [the earlier retained-source review](final-retained-source-0715ffb6.md); these runtime files have no changes between `0715ffb6` and the retained head.

`BoundedJsonBuffer` in `src/Server.Application/Response.cs` starts at 16 KiB only when the configured maximum is at least 20 KiB, then grows once to the original maximum. `Ensure` validates the requested minimum against the configured remaining limit before allocation; `Advance` also validates the actual backing capacity. The committed prefix is copied before replacement. `WriteJsonCoreAsync` still obtains the original `3 * maximum` managed credit before serialization and keeps the buffer and credit alive through the awaited write. Static `JsonTypeInfo<T>`, precommit failure behavior and one response writer remain intact. The temporary old-plus-new array overlap is covered by the existing unchanged peak grant; a lower allocation on small responses is not an increased admission allowance.

`JsonBufferFixtures` covers fragmented exact-limit writes, rejected hints/advances, converter failure and retry before commit, failed credit admission, retained borrowed bytes during a pending write, cancellation/failure cleanup and streamed-item credit release. These fixtures establish the intended boundaries; source inspection does not turn them into a new execution.

### Per-transport gRPC writer reuse

`NativeGrpcTransport.WriteAsync` still permits one pending write per transport. `_writing` remains set until both the operation result and actual `Retirement` have joined. `EncodeAndCreate` obtains the complete encoded-limit managed credit before promoting or allocating its weak exact-capacity array. Reused backing is fully cleared before the synchronous marshaller. A fresh scoped `MessageWriter` becomes unusable when the callback/native-copy scope ends; the native `grpc::write` validates the reservation and operation slot before transferring the token and preparing its owned message.

The existing error, stream-byte, reservation, native-create and cancellation paths remain. An idle transport keeps only a weak reference, so collection can eliminate reuse without changing correctness. The public callback contract explicitly makes the writer and returned memory borrowed for that synchronous callback. Runtime disposal rejects later writer method calls; it cannot revoke a `Memory<byte>` deliberately retained outside that contract. This is a documented lifetime limit, not a newly promised enforcement mechanism.

`WriterContracts` and `WriterAcrossCalls` retain exact-capacity/full-zero assertions, concurrent-direction rejection, encoder exceptions, real managed-credit and native-create denial, distinct simultaneous backing, writer invalidation, cancellation while encoding, protobuf checks and the original three-second idle gate. [Functional gates 004](../checks/grpc-functional-gates-004/README.md) executed the full supplied-native B18 verifier for both corrected roles.

### Request-owned metadata and HPACK

`native/protocols/grpc/src/metadata.rs::retain_headers` preserves the existing immutable `Bytes::from_owner` value/credit ownership and adds `HeaderValue::set_sensitive(true)` to each retained value. The flag prevents these request-owned values from entering the connection-owned HPACK dynamic table. Global HPACK remains enabled; an existing exact/static index does not retain the new request's owner. Header contents and the native ABI are unchanged. Repeated custom metadata can cost more wire bytes; no network-compression benefit is claimed, and gRPC message compression remains identity only.

The Rust clone-credit test checks that sensitive values and clones retain their complete grant until the last owner drops. `PersistentHeaderCredits` uses real TLS HTTP/2, one active request slot, two independent clients, repeated calls on the first connection, exact protobuf/ASCII/binary metadata and zero gauges while clients stay connected. Earlier failed idle gates and the two-client admission reproduction remain failures/diagnostics in their original records; the correction does not retroactively make them successful.

### Managed tail, admission and physical release

The new ordering is confined to `NativeRequest` and `NativeHost.HostTicket`:

1. `NativeRequest.CompleteCoreAsync` ends logical request use, releases managed metadata, completes native dispatch and joins registered operation retirement until native `TryRetire` succeeds.
2. It closes cancellation admission and joins the existing cancellation task. The ready marker is set in that join's `finally`, including when an application cancellation registration faults. The fault remains observable through the host path.
3. `HostTicket.RunAsync` awaits the complete dispatcher, nested continuation and request completion before arming physical release. Scheduling ends first. A pre-quiescence failure keeps the request rooted in its ticket rather than freeing a live owner.
4. The request-specific `SafeHandle` stores a typed ticket only after that ready boundary. Its final release, including one delayed by a physical lease, takes the separate admission gate, calls the native request destructor, then releases the coordinator slot and removes the managed ticket.
5. New-request `Notify` takes that same admission gate before the host dictionary gate, so it cannot observe a returned native admission slot with the previous managed ticket still counted.

The host control/dictionary gate is not held across native destruction. Native request cleanup can reap under the native request registry, and native close can deliver cancellation while holding that registry; control and kind-3 continuation notifications do not take the new admission gate. The two native new-request notification paths release their registry insertion lock before calling managed `Notify`. Thus the reviewed source does not introduce the earlier identified registry/host-gate inversion. `NativeResourceOwner` also invokes its destructor outside its own logical admission lock and publishes retirement only after physical release returns.

Constructor/adoption failure retains the original raw-pointer compensation route until ownership is established. A successfully adopted request with later metadata failure still reaches completion through its ticket. Unarmed handle release follows the existing native retirement predicate. Pre-quiescence failures are fail-closed and may retain ownership; this review does not interpret a fatal/quarantined owner as successful cleanup or authorize forced release.

The finite public `CloseAsync` continues counting a ticket until physical release, even if native state is stopped and payload gauges are zero. `RetirementFixtures.DispatcherTailAsync` proves that an independent second TLS client queues behind the complete managed dispatcher tail. `FinalLeaseAsync` holds a real owner lease through a faulted cancellation callback, requires the host fault to remain visible, establishes native stopped/zero-payload state, and checks a 100 ms close remains Pending before releasing the lease and observing completion. Both HTTP/1.1 and HTTP/2 TLS are covered. The existing MCP managed-tail/nested-cancellation and throwing diagnostic-listener fixtures were preserved.

### Shutdown, module boundaries and rejected changes

`native/server/host/src/engine.rs::acceptor_finished` treats a successfully completed acceptor after normal stop as normal, while an unexpected completion or task error still faults the host. The same handling is applied while draining the join set. The Rust ordered-outcome test and 64 actual-network shutdown iterations are included in the CI127 Host suite.

No production Core, `NativeResourceOwner`, `AsyncOperation`, database engine, codec engine, native ABI, toolchain lock or existing engine dependency lock changes occur in this retained diff. The added direct-codec benchmark lock is a measurement consumer, not an upgraded product engine. Public application signatures remain strongly typed C#, Fluent and async/await; no runtime reflection compiler or consumer Cargo requirement is introduced. Compiled API/XML and ordinary Entity/DTO/Handler package consumption remain separate finite gates.

The rejected per-method cross-call scratch is absent: `CallContext.cs`, `Registration.cs` and the transport exactly match the corrected control, and the full `src/Protocols.Grpc` subtree matches `0715ffb6`. The retained transport-local weak buffer described above remains. The [frozen scratch screen](../checks/grpc-scratch-comparison-004/README.md) rejected the later three-file candidate despite its allocation improvement; no source-only argument overrides that decision.

The proposed SQLite cleanup Ping removal is also absent. `native/database/sqlite/src/session.rs::probe` still calls `connection.ping().await?`, then verifies tracked transaction depth against the guarded native autocommit flag. The entire production database subtree is unchanged from the frozen baseline. The previously rejected extra `AsyncOperation` retry is absent as well.

## Existing executed evidence and its limits

| Evidence | Actual source/execution relationship | What it supports here |
| --- | --- | --- |
| [CI127 canonical/package](../checks/ci127-canonical-001/README.md) | Actual checkout `d4a51f16`, exact retained tree; all seven jobs passed | Eleven canonical gates, Host 19 tests, compiled API/XML, AOT, package guards, 17-package/six-graph consumption and ordinary managed edits with Rust absent. Archived B24 metadata is not an independent rehash of package payloads absent from that ZIP. |
| [CI127 A20](../checks/ci127-a20-001/README.md) | Same actual checkout/tree; all 48 expected command outcomes | JIT/AOT each 8,925 assertions and 72 finite orders; expected quarantine/stale-cookie/fatal outcomes preserved. Sanitizers cover the C decoder/oracles, not Rust/CLR/AOT runtime. |
| [B17 managed retirement](../checks/server-retirement-managed-001/README.md) | Candidate `9de3f744`; relevant retirement runtime/tests match the retained tree | JIT/AOT each 105 checks and 43 dispatches, including real TLS tail/lease fixtures. This is not a rerun of the full native-producing B17 verifier. |
| [Functional gates 004](../checks/grpc-functional-gates-004/README.md) | Control `db95a9fb` has the exact retained tree; both B18 roles ran; shared B15/B19/B20 ran on the scratch candidate | All 31 commands succeeded; control B18 JIT 948/AOT 949, all four gRPC cardinalities and package edits. B19/B20 are explicitly managed/API/package subsets, not full original native-producing verifier replays. Their shared retirement code is identical; the candidate's three gRPC scratch files are not silently relabeled final. |
| [Final003 actual build/admission](../checks/after-long-build-003/README.md) | Actual retained `2e3995df`, package version `0.1.0-perf01.after.5` | Nine completed producers, 17 selected feed packages, actual 15-package observer resolution equal to the reference set and actual native/application bindings. Build/admission is not measurement credit. |

Old A20 environmental failures and B18 failures remain in history. Later passing, source-bound gates provide new finite evidence; they do not erase or relabel the failures. No exhaustive race proof, 24/72-hour test, public domain-package release or final performance acceptance follows from this table.

## Open final003 gRPC capacity finding

The following are existing aggregate result fields, not a raw-event replay:

| Final003 after cell | Offered / completed | Logical successes | Other outcomes | Exact failed probe population |
| --- | ---: | ---: | --- | --- |
| `after-grpc-final003/05-ladder-256` | 7,707 / 7,707 | 7,696 | 10 `ResourceExhausted`; one `IntegrityFailure` | Deadline: 231 calls, 230 expected deadline checks, one correctness failure. |
| `after-grpc-final003/06-refine-192` | 5,781 / 5,781 | 5,774 | Four `ResourceExhausted`; two unexpected duplex `Cancelled`; one `IntegrityFailure` | Cancel: 116 calls, 115 expected cancel checks, one correctness failure. |

Both original results are `valid=false`, `service_standard_met=false`, with invalid reason `response/protobuf/hash correctness failure`, even though their drivers exited zero and all offered calls completed. These cells cannot establish a successful supported load. `Logical successes` includes the expected probe checks and is not ordinary business throughput. Evidence locations are the corresponding `result.json` files under `perf01-evidence/capacity/final-003/`; actual controller/raw bindings remain with their original owner.

The aggregate reason does **not** identify a payload mismatch or prove a product protocol defect. The frozen client at `tests/Perf01.Protocols/Client/Program.cs::GrpcAsync` can produce `IntegrityFailure` for a missing `perf-started` response header (line 207), protobuf/order mismatch (214), or a clean Wait-stream end without its required cancellation/deadline (218). The expected exception filters also require exactly one message, and the cancel filter requires that the client initiated cancellation. Those assertions and classifications remain unchanged.

A concrete classification possibility is visible in source: the header assertion precedes reading the stream/status. Native gRPC may legitimately return a trailers-only ResourceExhausted before the managed Wait handler for queue, request-budget or metadata admission. That response has no handler-produced `perf-started` header. Only the queue-full branch increments the native rejected gauge; request-budget/metadata denials do not. Therefore the observed zero rejected gauge cannot disprove that possibility. It is a hypothesis pending the original failed event messages, not a reclassification permission.

Both results report zero native callback failures, and after-idle active, queued, retiring and managed/native byte gauges recede to zero. These observations do not show recurrence of the diagnosed old ticket-capacity callback rejection or persistent HPACK credit retention. They also do not prove correct wire termination. The retained ticket fix waits for the complete managed dispatch before final owner release; the existing `GrpcCallContext.CompleteAsync` direction/status path and native `GrpcBody::poll_frame` cancellation/terminal path remain separate places to inspect if the failed message identifies unexpected EOF or status. No causal attribution to either retained correction is established.

The next discriminating action is the root-owned bounded inspection of the two already-recorded failed event messages and the unexpected duplex statuses at an idle boundary. Preserve these invalid cells, distinguish legitimate overload rejection from a strict probe expectation or genuine protocol failure, and then decide whether a targeted correction/regression is necessary. Do not weaken the frozen probe assertions, replay until success, or treat ordinary overload rejection as equivalent to a demonstrated semantic fault. Final source/product acceptance remains conditional on that resolution and the still-required final matrix, capacity and five final long-run receipts.

## Exact production source identifiers

These are Git blob object IDs at retained commit `2e3995df`, not newly computed artifact SHA-256 values.

| Path | Git blob |
| --- | --- |
| `src/Interop.Negotiation/EngineMetadata.cs` | `b838cd8ccadafbf2b2bdaf5cfafe74cc1e514794` |
| `src/Interop.Negotiation/EngineModuleLoader.cs` | `04303ad22cbb1b4d31c70132f0299ade9bbe7987` |
| `src/Data.Streaming/TypedStream.cs` | `7e414faf1c74f7fbe3080c0218fa9f6728bd362a` |
| `src/Server.Application/Response.cs` | `781c3ada04c2afca6bf9872ca8cd79a7d6820df0` |
| `src/Protocols.Grpc/NativeTransport.cs` | `f6da3e6c24a9d17f846f63ca173e84b71eff381a` |
| `src/Server.Native/NativeHost.cs` | `b868697bd5fe4d21598e718b1ee8abbd29a855bc` |
| `src/Server.Native/NativeRequest.cs` | `194aaa35003f7269179b7744ee54633365c37bb9` |
| `native/protocols/grpc/src/metadata.rs` | `00a0c45d85f00100cf742c3699e6b688aabbe4f5` |
| `native/server/host/src/engine.rs` | `df0cc23261b0e43375ff254f9dee96ef49b12f38` |
| `native/database/sqlite/src/session.rs` | `ae4df22286985ee628d6fa8d20c59065a9c39937` |
| `src/Interop.Async/AsyncOperation.cs` | `340f5fd19ba4ee45017a083d03f7d1b17e073653` |
| `src/Interop.Lifetime/NativeResourceOwner.cs` | `2f439bbb863b919c5bc80b702e3453a4cd6c9953` |
| `src/Protocols.Grpc/CallContext.cs` | `f7a10ae004c71eda27413b4f7b87a9d90b38a1c2` |
| `src/Protocols.Grpc/Registration.cs` | `0c8c25d91b1d7e64e7e639f1773e45c78b30a5d9` |
