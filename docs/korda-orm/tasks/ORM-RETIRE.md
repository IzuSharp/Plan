# ORM-RETIRE: Remove only the obsolete implementation after cutover

Status: `planned_candidate`; deletion is not authorized by this plan.

## Objective

Remove the superseded Fluent/native query compiler/C++ database execution path
after the new product is accepted and consumers are switched. Preserve useful
history, shared infrastructure and rollback to a published prior release.

## Design and source inputs

Use pinned Design `architecture.md` ORM-ADR-06 and ORM-C06, ORM-CUTOVER's actual
consumer inventory, current project references, runtime load paths, package
contents, CI module registrations and third-party license ownership.

## Start and acceptance dependencies

Start and acceptance: ORM-CUTOVER. Require explicit authorization for the concrete
deletion scope. A new product being built, or a documentation PR passing, cannot
satisfy this dependency or authorize deletion.

## Scope and ownership

Own a reviewed removal manifest and the proven-unused legacy implementation,
tests, native assets, package scripts and registrations it identifies. Coordinate
all shared CI/root files with their owners. No broad directory deletion based
solely on language or filename is allowed; shared consumers must remain intact.

The graph initially grants only the retirement document path. Before deletion,
complete the concrete file manifest, obtain the applicable scope authorization,
and update the reviewed graph/packet write scopes. A phrase such as "legacy code"
is not an executable deletion boundary.

## Implementation requirements

Trace source/project/runtime/package references and classify each old component
as unused, still shared or retained for an active consumer. Remove only unused
components through ordinary commits. Update current guidance to explain the new
product while preserving historical decisions and their acceptance scope.

Remove obsolete dependencies, native loaders/protocols, compiler tooling and
package assets only when the inventory proves them unnecessary. Preserve license
notices for any remaining adapted code or shipped native driver. Do not erase Git
history, old release availability or unrelated task branches/PRs.

## Validation and acceptance

Re-run affected module selection and exact new-package consumers. Inspect nupkg
and executable dependency closure to prove removed native engines are no longer
required, while SQLite's mature driver native dependency still works. Run the
new product's declared AOT/database matrix affected by removal. Verify no current
documentation, project, CI registry or release script points to deleted files.
Ordinary documentation changes must still avoid product builds.

## Integration and stop

Record deleted and retained components with the reason and current verification
scope. Submit the authorized retirement PR and stop at its requested boundary.
Do not restart historical performance, Rust, Server or Go tasks as cleanup work.
