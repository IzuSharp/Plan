# Existing task acceptance supplement — logical admission research

This is future implementation guidance, NOT permission to execute A/B Delivery. Current phase remains research/design/planning. Research source, experiments and raw evidence are exclusively in NativeWeave-Design; no executable project is copied here.

Input: Design merge `3767f3c932ebf95bd82f6ed1c9bafc9eec1c5b1e`, `docs/research/topics/R07/logical-admission.md`, `verification/logical-admission/primary-results.json`; actual primary run43373306474/source28f6cf7e6e4e80b9f32a92ad587a528d82911bd0. Both x64 platforms executed the negative control and gated positive facade in normal and actual Native AOT mode. The incidental identical-input CI rerun43374127432 is retained but adds no new research coverage. Existing D04 protocol0.1.0-draft remains proposed; exact spec hash is in the pinned registry.

## A03 — private owner and logical call admission

Preserve the existing module/file scopes from its task packet. Do not create a second ownership runtime. The future generated or handwritten facade owns a private SafeHandle; ordinary APIs do not expose the owner or raw pointer. For each synchronous operation: enter the local admission gate, reject Closing, acquire the SafeHandle reference, obtain the pointer, leave the gate, invoke the exact native operation, and release the successfully acquired reference in finally. Place the try/finally so failures after acquisition cannot leak the reference. No per-call GCHandle or native retain/release is required for this synchronous profile.

Dispose transitions Open→Closing under the same admission protocol and releases its owning reference outside the gate. Repeated Dispose must not decrement again. FFI, native stop, user callbacks and waiting for completion must not execute under that gate. An already-admitted call may finish after Dispose; a new ordinary call may not. GC finalization and parent/child owners retain their separate packet requirements.

Acceptance must include the actual negative-control witness: with an older lease still alive, a bare SafeHandle facade may accept a new call after Dispose. Then prove the generated candidate rejects both normal and held operations after logical close while native ownership remains live for the earlier call. Verify correct old-call result, final native owner count, exception after lease acquisition, exception/error return after FFI, repeated concurrent Dispose and managed allocation failure before owner publication. Do not use arbitrary invalid native addresses as a normal negative test.

## A20 — adversarial lifetime validation

Reuse the existing primary fixture rather than presenting it as new product acceptance. Extend it with randomized call/close schedules and recorded seeds, high contention across independent owners, parent/child close, finalizer/GC cases and injected failure at every ownership-transfer point. Assert both logical rejection and physical safety; a zero live count alone is insufficient if a disallowed call slipped through. Keep tests isolated where fatal native/ABI faults are intentionally exercised. Capture OS/RID, exact source/toolchains and actual AOT executable hashes/results. Windows evidence cannot replace Linux, and guided64-round traces cannot substitute for weak-memory/race/sanitizer or soak evidence.

## A06 / A07 — asynchronous control lane and retirement

Do not extend the synchronous lock by holding it across await or callbacks. Before returning from native start, establish all input/context/native operation owners. Business close rejects new starts, but already-admitted completion/cancel/retirement control operations need a separately scoped internal lifetime until their protocol ends. Root release requires proof that no future callback may begin AND all in-flight callbacks/control calls have retired. Task completion, cancellation request, callback exit and physical reclamation are distinct facts.

Required schedules include completion before start returns, cancellation during registration, Dispose from a callback, duplicate completion, late notification, simultaneous completion/stop and failure while publishing a result owner. Use static non-generic UCO entry points with fixed ABI types and contained managed exceptions. This study did not implement or validate those async schedules; existing A06/A07/Verification packet obligations remain mandatory.

## B11 — native builder mutation and rendering

SeaQuery continues to own dynamic statements, expressions, Values and backend rendering. A thin C# Fluent facade must not grow a parallel SQL AST/dialect engine. Supported C# entities arrive as validated metadata; ordinary entity additions must reuse the precompiled native binary. Source generation remains optional static metadata/DTO assistance.

For the chosen thread-safe builder profile, obtain a shared reference to the live native owner and mutable query access through its own guard. Never create aliased `&mut QueryOwner` before the guard is acquired. A thread-affine Engine may route commands to its owner worker instead; state this capability explicitly. The managed admission gate only protects close/reference ordering and is not the query writer lock.

Specify prevalidation, mutation, consistent rendering, owned SQL/argument transfer and builder release as separate steps. Do not hold a synchronous mutation guard across SQLx await, network I/O or reverse managed callbacks. An explicit clone/fork operation may clone native state; do not require whole-AST cloning after every Fluent operator without evidence. Define partial-batch failure behavior and keep owned state valid even if a panic occurs; Mutex poison detection is advisory, not unsafe memory soundness.

Acceptance: concurrent mutate/mutate, mutate/render and close/render; explicit clone independence; partial operation failure with declared unchanged/invalidated semantics; provider capability rejection; checked parameter ordering/type/NULL handling; same-native-hash second-entity AOT consumer; PostgreSQL/SQLite differential results and existing transaction uncertainty/fault tests. The six migrated SQLite tests are a research input, not completion of this list. SeaORM dynamic construction/projection remains a separately evidenced comparison; do not claim a static Entity constructor proves all runtime ORM paths impossible.

## B17 / B16 / B20 — foreign handler, body and retained bytes

Reuse native Hyper/Tower Service/Body and engine connection/protocol machinery. Native request admission closes before new managed dispatch, but existing handler/native Future completion, body streams, borrowed/owned chunks and callback contexts remain alive until their own retirement conditions. Tower's ResponseFuture permit is not the resulting Body's owner; its actual destruction time must not be confused with a single Poll::Ready observation.

Acceptance requires a real C# Handler→native Future bridge, not only the Rust oneshot used by the research fixture. Exercise slow/aborted handlers and body producers, response headers completed while body lives, oversized chunks, retained bytes after protocol credit is returned, callback reentrancy, cancellation and shutdown races. Count active requests/streams, retained bytes and pending cleanup separately. No queue-length or semaphore-slot observation establishes whole-process RSS. Preserve Actix thread affinity and avoid a mandatory shared Database/Server runtime. Kestrel remains a comparable AOT baseline; performance claims need equivalent workloads.

## Research/documentation progression

R07/D04 can now rely on actual synchronous logical-admission evidence rather than only source analysis. R08/R09/D05/D06 remain the natural async continuation. R25/D16 and R27/D18 may refine their native owner/handler designs in parallel without waiting for every production task. The graph and contract status determine future technical acceptance; the current research-only phase independently forbids starting Delivery even when a candidate becomes technically ready. Independent D32 review remains pending.
