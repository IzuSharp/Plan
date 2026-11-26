# Worker-D: isolated execution scheduling experiment

Decision at this checkpoint: select a narrow, independently identified experiment,
not an adopted product strategy. Product implementation must follow this Plan and
its companion Design record. Ready-row-C has just been rejected: two reversed PG
thousand-row rounds increase CPU4.91/8.55% and p506.77/6.56%; SQLite is inconsistent.
Its actual code and successful764 AOT assertions stay as evidence, not integrated.

## Measured motivation and falsifiable mechanism

The completed Stage1 table binds full1000/B32 to32 delivered batches and34 native
jobs, native enqueue/worker/ready/managed-take timelines, substantial AOT RhSpinWait
samples and runtime-setting sensitivity. Complete Host SQL does not remove the
execution CPU gap. Common-A's second-continuation-hop reduction is actually proved,
but has no stable ordinary endpoint benefit. Those results motivate a distinct
causal variable: run the already-admitted native pull and take its result inside
the same bounded managed ThreadPool work item, rather than making that work item
wait for readiness from a separate native queue. ThreadPool spin reduction is a
hypothesis, not a proven assignment of every sampled spin instruction.

The first variant reuses the existing finite CallbackCoordinator reservation and
never-inline shared ThreadPool scheduling. It does not introduce a dedicated
managed pool, change global runtime knobs, inline public native waits, combine
common-A or ready-C, change batch32, or alter SQL/provider algorithms. Source pool
admission, management, cursor final close, Source join and transaction finish keep
their independent existing native execution paths. The C++ libpq/sqlite3 execution
layer and two independently installable public packages remain.

## Required internal contract before implementation

1. Keep all original synchronous input snapshots, source/Session gate checks and
   error order. A new nonblocking prepare/admit boundary must register generation,
   Cancel, source pending and independent channel/source retirement tickets before
   the managed queue can be committed. It executes no provider I/O on the caller.
2. A prepared work obligation has exactly one transition to running or canceled/
   abandoned. Queue rejection, Source/Session close or failure before execution
   must settle the same obligation and release its tickets. Merely marking Cancel
   while no worker will run is not retirement. No unbounded self-owning cycle or
   borrowed OwnerLease/pointer may escape the synchronous ownership scope.
3. The private synchronous run consumes one admitted generation. Reuse the original
   CursorPull::run, full metadata validation, second admission, Cursor::fetch,
   cancellation detach, complete/error enrichment and one-time take. Do not clone
   these engine algorithms into a divergent path. Old request ABI semantics stay
   unchanged for other consumers, including the untouched Go draft.
4. The ordinary managed path may retain the existing bounded ready callback for
   internal state notification. It must never publish user code while native run
   is still on the stack. Same-work-item take/publish is eligible only after the
   synchronous native call returns and original setup, controls, cancellation
   registration and callback drain conditions hold. Keep MRVTS asynchronous
   continuation behavior; callback count reduction is not required or presumed.
5. Native retirement tickets must cover every new exported-run local accessor,
   not just the old inner Worker. Source join cannot report quiet while a new ABI
   frame still holds and can access channel/session/source/provider state. Final
   notification and result availability remain distinct from full retirement.
6. New private extension symbols/capability/layout negotiation must be explicit in
   both provider builds. Preserve the frozen existing ABI and public C# signatures.
   EngineLocalAsync remains the declared instance-owned native admission/control
   model, with the proposed managed pull executor accurately described in Design.

Native ownership/interface details receive root and managed/native cross-review
before implementation is committed. The experiment must reject unsafe shortcuts
listed in worker-execution-strategy-review.md, including Task.Run(oldRequest+wait),
late pending reservation, raw-provider bypass, shared blocking close/transaction
pool, and canceling a managed Task as if its native work were released.

## Evidence gates

A separate diagnostic identity must bind generation/TID/monotonic boundaries for
public invocation, prepare/admit, managed queue, synchronous native enter/leave,
ready, take, publish and retirement. Demonstrate the initiating stack does not
wait for deliberately held native execution. Count actual native posts, managed
work items, callbacks, FFI, SQL/protocol, batches and payload. Native execute and
take should share the admitted managed work item; no claim is made in advance
about remaining native task totals, instruction costs, CPU or allocation.

Correctness includes prepare accepted then scheduling rejection, cancellation
before/during work, source close before work, queued-work abandonment, duplicate/
stale generations, failure during owner adoption, held read plus Dispose, late
old work, cancellation registration drain, DDL/metadata errors, error enrichment,
PG late-row error and protocol drain, and unchanged transaction Unknown semantics.
The ordinary variants need actual separate NuGet packages and Release AOT ELF/
debug/generated-code identities, both provider checks, committed impact review,
then same-host reverse A/B before adoption. Run no performance work in CI.

If the causal mechanism cannot be implemented within the current contracts,
record that specific counterexample. If repeated ordinary benefit is absent,
reject the candidate rather than merging an architectural rewrite on aspiration.
