# ORM-CUTOVER: Perform an explicitly authorized product migration

Status: `planned_candidate`; product implementation and cutover are not authorized
by this plan.

## Objective

Switch selected consumers and release guidance to the independently accepted
Korda.Orm product with a reviewed compatibility, package identity and rollback
plan. Keep deletion as the separate retirement task.

## Design and source inputs

Use pinned Design `architecture.md` ORM-ADR-06, contracts ORM-C04/ORM-C06, the final
ORM-ACCEPTANCE report and current existing-product public APIs/packages. Treat the
old implementation as a migration input, not a new language/execution dependency.

## Start and acceptance dependencies

Start and acceptance: ORM-ACCEPTANCE. Also require explicit authorization naming
the cutover/release actions. Read current repository/release rules before acting.
No historical permission to optimize, merge or publish another task applies.

## Scope and ownership

Own the new migration guide, selected consumer/sample conversions, current-product
entry points and authorized release metadata. Coordinate shared CI and package
changes with their owners. Retain old implementations and published-version
rollback information; do not delete native modules in this task.

Before changing current product entry points or consumers beyond the graph's
listed paths, record the exact authorized file manifest and update the reviewed
graph/packet scope. The current planning placeholders authorize no additional files.

## Implementation requirements

Document API/source differences, entity/DTO migration, SQL behavior changes,
provider/version requirements, cancellation/transaction differences and generator
adoption. Decide deliberately whether package names coexist or require a breaking
major version; do not replace an existing binary silently. Port representative
business flows and validate their actual semantics, not just successful builds.

Define rollback to a known supported prior release and identify state/schema
changes that would complicate it. Avoid irreversible schema changes as an incidental
side effect of adopting the query framework. Release only exact verified package
artifacts under the separately authorized process.

## Validation and acceptance

Execute migrated business scenarios using Native AOT, check schema/transactions/
returned values, independent package consumers and updated compiled examples.
Validate obsolete/new API guidance and actual shipped metadata. Confirm old and
new package coexistence or the explicit replacement policy, with no accidental
runtime link to the old query/compiler protocol. Review rollout and rollback
instructions against the real candidate version.

## Integration and stop

Record the actual authorized switch and remaining consumers. Stop after cutover
review and required release checks. Do not proceed to ORM-RETIRE until its separate
authorization and proof of unused old modules are present.
