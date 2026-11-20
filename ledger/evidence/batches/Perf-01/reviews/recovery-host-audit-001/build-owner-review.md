# Recovery build owner and provenance review

## Source verdict

**ACCEPT for source preparation at Plan
`04a9764e650d0ff6d922ae48429937ad8dd81206`.** The before-stage producer recipe and
binding have no remaining identified source blocker. Root must first obtain the
actual intended outcomes from the same three bounded ownership fixtures, then
decide whether to launch the baseline build. This review itself executes no
fixture, import, compiler, producer, raw reader or workload and grants no actual
functional or performance acceptance.

Scope: `ledger/evidence/batches/Perf-01/diagnostics/recovery-build-001`.

| Reviewed input | SHA-256 |
| --- | --- |
| `sources.json` | `c7526f08d3c50c6d58f7336adae6ebab5fb82b606cce140108a48f6b54b3d0ab` |
| `inputs.json` | `cbe098ff6ee957bfab7e826d5a6dff0a718e0d2e9602948c24030d5f418b4697` |
| `owner.py` | `6dddbc5e9d92e7f4ccc8ee05b600c4446707bb44b86f29b7eeceda73ad56bfcc` |
| `build.py` | `e070242d61a4c997d9d98e1c0db8a16c78b83aee30cd595c9108623136c560a0` |
| `bindings.py` | `5532c5554c0c52b3a31558d4f84f7552a070ff7e21ace902c2646a7aa913ef18` |
| `check_owner.py` | `72218b8ea34ffc3594c7709ccb54c88e23ee87b6386649ac88675cc1673349eb` |

All indexed preparation-file digests were read back and matched at the clean
reviewed commit. The existing toolchain prerequisite is separately pinned at
`663c591a1b69c46a7f3785b32e73de9874028ef531ac4b606a4c759e7b989b4d`; root owns its
actual binary/archive verification. The build code reads that manifest directly
and does not rely on an assumed activation-script filename.

## Process ownership and concrete corrections

The new owner truthfully identifies itself as new recovery code. It reuses
`src/Benchmarks.Domain/supervision.py` from product
`2e3995df8d86583ee9443348276ca8d918056bfc`, SHA-256
`c57b845fbbc2dd97015888fa7e251fb924040daf3a3b4c342e4fd0e5d1875de4`, for the
public `OwnedTree` PID/start-time and pidfd signalling primitive. It adds explicit
Linux subreaper admission, adopted-child discovery, zombie reaping, and a strict
normal-exit check. A zero-exit leader does not establish successful retirement
while owned or adopted children remain. Timeout and forced termination stay
distinct from normal native/application retirement.

The following narrow corrections were reviewed before product execution:

- The original fixture used a temporary-directory context that would delete
  failed-case evidence. The corrected fixture requires a fresh retained output
  and keeps each receipt and log on both success and failure.
- The same three cases now require their intended branches: normal exit zero
  without signals, an actual timeout with termination, and a zero-exit leader
  rejected because its detached descendant remains live. An unrelated error
  cannot satisfy a negative case merely because an exception occurred.
- Awaited subprocess creation exposed a cancellation window before the process
  tree was registered. The owner now performs `Popen` and registration before
  its first await, polls the worker in the existing async loop, and retains
  bounded waits after signalling. The normal-exit protected try also rejects
  remaining adopted/unreaped children before leaving cleanup protection.
- Root's first actual fixture invocation failed before a test child was
  launched because the executor omits the per-task children pseudo-file. Its
  reported receipt
  `d440b032368f2bbbe249c3b51f5cd79aab8dde80a7775568cfd0c626ec507d67` remains a
  separate failed attempt. Root confirmed numeric procfs enumeration and stat
  PPid/start-time fields are available. One strict `direct_children()` helper
  now selects current records whose PPid equals the current owner and replaces
  all four pseudo-file reads: initial admission, adoption, protected normal
  exit and final retirement. Only disappeared-process races are skipped;
  permission and malformed-record errors reject the gate. Fresh fixture002
  must establish the actual outcome of this adaptation.

Source approval before fixture001 was conditional on actual platform checks;
it did not prove that the children pseudo-file existed. Its failed result is
not relabeled, and the updated owner receives a distinct source identity.

All signalling authority belongs to the live original owner and its observed
process identities. Root reports that separate executor invocations can have
different PID namespaces. Saved process numbers from another invocation must
never be used to signal processes in a new invocation. The owner does not
provide an automatic historical-PID recovery mechanism.

## Fresh producer and consumer binding

The reviewer traced the actual original producer fields and paths used by
`bindings.role()` and `bindings.common()`. The recipe keeps eight unchanged
producer entry points per product role and three unchanged common commands;
pair binding has no producers. Product commits remain fixed EA5 before and
retained ON2e, while the public application/driver source remains ON2e.

Freshness requires absent `bin` and `obj` for every tracked managed project
initially and immediately before B24's managed producer, plus a fresh product
Cargo target. The original B24 producer restores the complete graph and builds
all 14 managed packages for the selected previous feed. Its later unused
candidate feed copies common archives only from that same invocation. No old
common managed assembly or historical feed is silently imported.

The source/schema comparison confirmed the B24 44-command receipt, reference
five-command JIT/AOT build-only receipt, observer two-command receipt, protocol
six-command receipt, codec original positive/negative/package proofs, shared
probe receipts, actual artifacts, source inventories and native metadata maps.
The reference's build-only `partial` status is required and is not mislabeled
as a service or long test pass. All 17 selected B24 packages and the actual
native producer inputs are bound to the actual product commit.

The observer explicitly uses the role's fresh reference cache. Resolution
accepts only that exact canonical package folder with zero or one trailing
slash. Its package identities and bytes must equal the actual reference AOT
resolution. Protocol, codec and shared consumers use their own actual isolated
resolution records. A small reviewed common-stage supplement applies the same
NuGet binding helper to the pure managed database comparator's actual cache and
assets file; the original comparator producer commands are unchanged.

NuGet raw archive bytes and signed content identity are deliberately separate.
Each resolved archive has actual raw SHA-256/SHA-512, a matching archive sidecar,
and matching assets/extraction content hashes. Local NativeWeave archives must
match the fresh selected feed and have equal raw/content hashes. Unsigned
external packages also require raw/content equality. Signed external packages
may differ; their actual restored metadata and signature-entry presence are
retained, and paired external populations must match actual archive and content
identities. This is not a new signature-verification implementation. It relies
on the unchanged successful restore/publish and recorded actual outputs, not a
claim that sidecar text alone establishes executable provenance.

The separate A17 experimental Core/codec package version remains in separate
role caches. Matching that version string does not substitute for source,
archive or executable identity. The actual codec package JIT/AOT and ordinary
managed-edit receipts remain distinct from performance execution.

## Admission and limitations

The stage owns the new epoch's exclusive lock, uses fresh control/output roots,
retains finite per-command receipts and refuses failed or unretired
prerequisites. The exact source/index, freeze, boot and toolchain inputs are
bound. A completed stage means its new producer artifacts are bound; it does
not mean product qualification, noise, capacity or any long group has passed.

The 16 GiB entry and 8 GiB between-producer floors are root-selected operational
guards. They are neither a peak-space guarantee nor a change to the formal
application resource SLO. A failed floor or producer preserves partial evidence
and stops; this preparation performs no automatic cleanup or silent resume.

The three bounded fixture executions, actual product builds, later functional
gates and measured-load admission remain root-owned. This source review does not
broaden the authorized fixture population or substitute a source verdict for an
actual process-retirement result.

## Subsequent actual fixture002 result

Root executed the unchanged three fixtures against source index
`c7526f08d3c50c6d58f7336adae6ebab5fb82b606cce140108a48f6b54b3d0ab` on
2026-11-20 from **19:43:09.709449 to 19:43:12.634338 UTC**. The actual wrapper
returned zero and its receipt reports all three checks passed. The independent
reviewer subsequently read the small wrapper/case receipts and logs, matched
their recorded digests and checked the exact outcome populations. No fixture
was rerun and no saved PID was inspected or signalled in the new invocation.

| Case | Actual command-owner outcome | Leader exit | Signals | Final retirement |
| --- | --- | ---: | --- | --- |
| Normal | Completed; no failure | 0 | None | No live owned or adopted children |
| Timeout | Expected failure: `TimeoutError: Finite producer deadline exceeded` | -15 | One SIGTERM | No live owned or adopted children |
| Detached child | Expected failure: `RuntimeError: Producer exited with live owned/adopted descendants` | 0 | One SIGTERM to the detached descendant | Both observed processes retired; no adopted children |

The two negative command-owner receipts remain `failed`, as intended. The
fixture suite passed because it observed and cleaned up those exact rejected
conditions; they are not three successful producer commands.

| Actual retained record | SHA-256 |
| --- | --- |
| Fixture002 execution | `548dce7313b67eec507bb271a7ba3a984ec18dd85213a1987087753bc6c21108` |
| Wrapper stdout | `d015b0ea8a30ff7fd7e071cc6e1f5bab7bf977537be8b62de7febf2e29088fcb` |
| Wrapper stderr, empty | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Normal case | `b0f41e46d97e93f030475b0d81d82c0b0506a57d46a7e53ef7e6511fbff797ad` |
| Timeout case | `c643796cc79c4890383763241334824de267a137749462123ff8378642337a23` |
| Detached-child case | `78eeca21edc19e3a05201550fdc617f0ac8987b1a1cdac8e662452924fee6b8e` |

These are bounded process-ownership checks, not a general stress proof or a
native application-retirement test. They grant zero workload/performance/long
credit. Initial failed fixture001 is preserved separately. Product build and
functional outcomes require their own actual receipts.
