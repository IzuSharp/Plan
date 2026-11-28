# ORM-CI: Integrate independently selected product validation

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Extend Korda's existing module registry and Python runners for the new managed
modules while preserving independent checks, local execution and actual dependency
impact. This is future product CI work, not the document CI change in this PR.

## Design and source inputs

Use pinned Design `architecture.md`, `contracts.md` ORM-C06 and `validation.md`.
Inspect the current product `eng/ci/impact.py`, `catalog.py`, module guide,
`worker.py`, package input/packed API logic and workflows before modifying them.

## Start and acceptance dependencies

Start: ORM-FOUNDATION. Acceptance: ORM-FOUNDATION. Register stable module ownership
and check contracts early; individual product tasks supply their real commands.
Registry acceptance is not acceptance of modules that have not been implemented.

## Scope and ownership

Own `eng/ci/modules/orm.json`, routing integration and its tooling tests; root
workflow/build-file edits require this owner. Independent modules own local
verification scripts under their own paths. Do not rewrite legacy module graphs,
remove their gates, or copy new checks into another competing dispatcher.

## Implementation requirements

Register source/test ownership, real project/runtime/generator dependencies,
package membership and resources. Pure DSL checks need no database service.
Provider database checks and Native AOT consumers run independently. A provider
leaf selects itself and true consumers; a shared contract/generator selects every
actual dependent. Use the existing distinction between source, test and metadata
inputs; packed metadata-only changes do not require unrelated API signature checks.

Reuse checked build outputs where valid and select exact package consumption from
the actual changed shipped inputs. Ordinary Markdown must not trigger compilation.
YAML orchestrates tool setup and runners, while Python owns selection. Keep long
performance/profiling work explicit. Every command must also work locally.

## Validation and acceptance

Use real Git fixtures for added/deleted/renamed modules, multi-commit diffs,
shared dependency changes, provider leaf changes, schema/generator effects and
metadata-only package updates. Unknown/ambiguous paths and cycles must fail.
Assert PostgreSQL edits do not start unrelated SQLite/MySQL services and pure
render changes select the affected runtime consumers. Exercise a fixture AOT
consumer and package selection, with full implemented module results deferred to
their own tasks and ORM-INTEGRATION. Record selected checks and reasons.

## Integration and stop

Integrate module registration proposals from independent owners in a controlled
sequence. Hand off the registry contract and local commands; do not duplicate
validation work simply because it can run in CI. Stop after the CI task's review
and required checks, without implementing unrelated modules or publishing packages.
