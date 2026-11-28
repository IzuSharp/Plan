# ORM-ACCEPTANCE: Independently accept the new product candidate

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Review the actual new implementation and evidence as an independent product before
any switch from the existing architecture. Acceptance covers a declared feature/
profile/version matrix, not hypothetical complete jOOQ parity.

## Design and source inputs

Use the immutable Design/Plan inputs, ORM-C01 through ORM-C06, actual integrated
source/package commits, provenance ledger and recorded validation. Read the current
user authorization and product guidance; document review is not merge permission.

## Start and acceptance dependencies

Start: ORM-INTEGRATION, ORM-PERFORMANCE and ORM-DOCS. Acceptance: those same tasks
and their pinned transitive inputs. The reviewer must not simply approve its own
implementation without an independent check. Optional ORM-PARSER does not gate a
release that explicitly excludes parser/translator support.

## Scope and ownership

Own the final acceptance record and release/migration recommendation in the
authorized product/Plan locations. Read every affected implementation boundary;
request targeted fixes from owners. No cutover, old-code removal, release upload
or branch merge is inherent in this task.

## Implementation requirements

Reconcile promised SQL/API features with real tests, driver/server versions,
package closure, AOT consumers and known restrictions. Review direct/adapted
upstream source, notices and semantic deviations. Confirm pure DSL isolation,
parameter/result integrity, lifecycle, generation hosting, public API/XML/examples,
unsupported diagnostics and module diff routing.

Evaluate controlled performance against the predeclared comparable workloads and
budgets. Distinguish render-only, binding/mapping and end-to-end costs; report any
budget misses and ensure no broad parity/zero-allocation claim exceeds evidence.
Check that test data, result row counts, preparation and pooling were comparable.

## Validation and acceptance

Inspect actual compiled outputs and exact nupkg consumers; reproduce representative
positive and negative semantic/AOT/lifetime cases independently. Re-run affected
checks for fixes rather than replaying historical campaigns. Verify every mandatory
task status has corresponding current evidence; unimplemented/unsupported cells
stay labelled. Require no blocking correctness, ownership, license, API or routing
findings before approving the candidate for a separate cutover decision.

## Integration and stop

Record finding IDs, severity, resolutions, final reviewed commits/packages,
remaining limitations and explicit recommendation. Stop at review. A failed gate
returns to the owning task; a pass permits consideration of ORM-CUTOVER and does
not automatically execute it or retire the old product.
