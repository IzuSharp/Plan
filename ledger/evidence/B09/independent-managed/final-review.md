# B09 independent managed binding review — Linux x64

**Decision: accepted for the B09 managed/internal binding component at commit
`5bfaaa2e15726321be8b06a21557f3f62cb389e9`. No managed findings remain open.**

Reviewer: `/root/environment_review`. Author: `/root/plan_requirements`.
Native query semantics received a separate review by `/root/b07_codecs`; this
report does not replace that review or accept any reviewer-authored B03/B05 work.
The reviewer made no changes to the B09 product, tests, documentation, or Plan.

## Authority and scope

The task authority is `Plan/tasks/B09.md` and its related `fragments/orm.json`
entry. Design is pinned to `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
The exact internal declarations come from `docs/api/database.md` section 9;
ownership and logical admission were reviewed against
`docs/contracts/lifetime-v0.1.md` sections 3–9. The task's dependency rationale
keeps full B04 host operation coordination and B11 SQL execution downstream.

Reviewed product source: `src/Query.Binding/Owners.cs`, `QueryBinding.cs`,
`MetadataBindings.cs`, `OperandEncoding.cs`, `NativeCalls.g.cs`, the project and
API applicability/reference files. Reviewed supporting source: the actual managed
test harness, native operation fixture, compiled API gate, verifier, and minimal
and self-composition sample. The source and binary identities are recorded in
`receipt-audit.json`; canonical product source is retained by its Git commit.

## M1: physical SafeHandle lifetime incorrectly reopened logical admission

This was a blocking finding on clean candidate
`c5bbd96be936e159de67ed5c08d10f889d87f3b9`.
`DatabaseOwner.Borrow` originally checked only `SafeHandle.IsClosed` around
`DangerousAddRef`. An earlier access lease kept the physical SafeHandle open after
`Dispose`, so both a new borrow and a new native model registration were admitted
after logical disposal. This is the counterexample explicitly described by D04
section 3; the query-specific disposal flag did not protect source/session/model
helpers.

The independent probe references the actual compiled product DLL and native
fixture. It is not a copy of the managed owner implementation. With an old source
lease held, it disposes the source, attempts another borrow, then attempts
`MetadataBindings.RegisterModel`, and finally releases all owners.

Original observed output:

```text
after_dispose physical_owners=2 safehandle_is_closed=False
prior_lease_keeps_physical_owner=True; new_lease_after_dispose=True; new_native_model_after_dispose=True; after_prior_lease=1; final_owners=0
```

The probe exited 1. Final native owners returning to zero distinguishes the
logical admission defect from a manufactured dangling-pointer call.

The author's fix publishes a separate atomic Closing flag before base SafeHandle
disposal. A borrow checks it before retention and again after acquiring the
physical reference. A failed second check releases the newly acquired reference.
Successful admission can linearize at the final Open observation while its
SafeHandle reference is already held; a later closure therefore cannot free that
call's owner. Calls observing Closing cannot proceed to pointer extraction.
The protocol adds no scheduler, owner registry, or public lease object.

The unchanged independent probe passed against the fixed DLL:

```text
after_dispose physical_owners=2 safehandle_is_closed=False
prior_lease_keeps_physical_owner=True; new_lease_after_dispose=False; new_native_model_after_dispose=False; after_prior_lease=1; final_owners=0
```

Both the fixed product DLL and native fixture match the final formal receipt's
artifact hashes. The original failing inputs/results and the fixed inputs/results
remain separate. The author added the exact held-source-lease regression to the
formal JIT and Native AOT harness. This closes M1; no prior failure was overwritten.

## Other reviewed boundaries

- **Owner and source identity:** each wrapper retains the creating `SourceBinding`
  and module-local release function. Cross-source metadata/import checks precede
  native extraction. Owner kind checks and the logical closing protocol apply to
  source, session, model, plan and relation helpers. Native owners retain their
  required parent state; managed variable reachability is not used as a lease.
- **Query admission:** `QueryBinding.Enter` independently rejects concurrent or
  reentrant mutation, rechecks disposal, and balances its owner lease and active
  flag on failure. Default and foreign expression/arena references reject before
  FFI; native generation/type checks remain authoritative. Self-composition ends
  source admission before importing into the destination, including self-import,
  and disposes temporary plan/query owners in reverse order.
- **Borrowed inputs and results:** byte views are pinned only for the synchronous
  call. B01 canonical metadata/control/wire encoders supply the payloads;
  projection fields are captured once. Native persistent snapshots own their
  copies. The relation-load helper returns a Created operation for immediate
  adoption by the documented B04 owner; it does not invent a second asynchronous
  runtime or expose a public raw pointer API.
- **Callbacks and late cancellation:** the test-only native fixture snapshots its
  terminal result independently of later cancel requests and keeps retirement
  Pending while the callback is active. The actual managed UCO callback probes
  this Pending state; the harness separately observes start return, successful
  retirement, result transfer and final release. Late cancellation after a
  successful terminal callback preserves the transferred cursor result. Wrong
  take kind does not consume it, and operation retirement does not destroy it.
- **Exact ABI and documentation:** independently extracting the pinned C section
  reproduces all 42 inventory signatures. Each managed field and its resolver cast
  has the corresponding parameter widths, pointer indirections, return type and
  explicit Cdecl convention. The actual compiled gate additionally checks PE
  field/function-pointer/Cdecl header bytes `06 1b 01`, compiled parameter/return
  types, zero exported CLR types, all 42 XML entries and the exact reference.
  The project reuses A01 records and B01 application types; it adds no managed SQL
  AST or public facade.
- **Consumption and costs:** the maintainer sample explicitly receives a
  precompiled test fixture and executes static metadata plus self-composition.
  The guide identifies control/value encoding allocations, native copies and
  downstream host obligations. It makes no zero-copy, performance, full-host,
  distribution or pristine-consumption claim.

## Actual evidence reviewed

Author formal run: `artifacts/B09/attempt-002/status.json` in the B09 worktree.
SHA-256: `fe7e75fdc6ed3e990885aa4d2d69ffab0e8463ecdcf3caa892ec18667a673741`.

- 31 commands succeeded from clean committed source; all 90 recorded source
  inputs are unchanged and match their current committed files.
- Six recorded artifact hashes and two Native AOT response-file hashes match.
- JIT executed 66 assertions in 10 groups. Native AOT executed 67 assertions in
  the same 10 groups with `DynamicCodeSupported=false` asserted at runtime.
- Each mode observed four actual terminal callbacks and zero final native owner,
  operation and buffer counts. Both minimal/self-composition sample modes passed.
- Compiled API/XML/reference gate reports zero public symbols and 42 exact Cdecl
  declarations. Locked restores and format/clippy/C-header gates passed.

The reviewer read the actual logs and rehashed their inputs/artifacts; no accepted
formal suite or previous Task-02 task was rerun. Only the new independent owner
probe was built and executed before and after M1's correction, in the reviewer's
own artifact directory.

`ownership-pre-fix-result.json` preserves the failure; `ownership-fixed-result.json`
preserves the passing three-command probe. `audit.py` is the independent read-only
evidence/signature audit, and `receipt-audit.json` preserves its result and log
hashes. `final-review.json` records the machine-readable decision and references.

## Limits

This is Linux x64 component acceptance, not Windows or all-platform acceptance.
The operation transport is explicitly a test fixture exercising real B09 binding
and validation code. It does not establish full B04 asynchronous host cleanup,
production GCHandle coordination, B11 provider SQL execution, NuGet distribution,
or pristine package consumption. The focused owner probe reproduces the concrete
held-lease closure boundary; it does not claim exhaustive scheduler or weak-memory
state-space exploration. Those limits do not introduce extra B09 dependencies.
