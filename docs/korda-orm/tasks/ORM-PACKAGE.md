# ORM-PACKAGE — independent packages and shipped consumer validation

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Produce independently usable candidate packages for the declared products and
validate what is actually shipped. Internal modules remain independently testable;
they need not become individually published packages.

## Design and source inputs

Use the graph-pinned Design `architecture.md` package candidates, `contracts.md`
ORM-C05/ORM-C06 and `execution-aot.md` dependency/license boundaries. Follow the
existing product's package input selection, metadata, API and independent-consumer
rules; do not introduce a second CI dispatcher.

## Start and acceptance dependencies

Start after `ORM-FOUNDATION` to define package manifests and consumer harnesses.
Final acceptance requires `ORM-QUERY`, `ORM-EXPRESSIONS`, `ORM-DML`,
`ORM-RELATIONAL`, `ORM-RENDER`, `ORM-GENERATOR`, `ORM-SCHEMA-TOOL`,
`ORM-ADVANCED-TYPES`, `ORM-NESTED`, the PostgreSQL/SQLite/MySQL driver tasks,
all four dialect tasks and `ORM-CI`. This node aggregates the final declared
package set; individual packages can be built and consumed independently as their
own inputs become ready. Do not wait for whole-product integration or use this
aggregate gate to block leaf-module development.

## Scope and ownership

Own `eng/orm-package/**` and `packaging/orm/**`. Coordinate root project files,
module registration and API-baseline edits with their owners. Do not change module
semantics, upstream dependencies or publication settings without their review.

## Implementation requirements

Maintain exact shipped-input and dependency closure per package. Keep drivers out
of the pure core, unrelated drivers out of provider packages and live database
discovery out of normal compilation. Bundle internal components appropriately and
validate generator/analyzer packaging, tool invocation, XML docs, metadata,
license/NOTICE obligations and SQLite native assets. Distinguish runtime dependencies
from analyzer/build assets. Never substitute a project reference for the candidate
archive in the final consumption check.

## Validation and acceptance

Build an exact candidate version, then restore each top-level archive in an isolated
cache and publish/run its intended Native AOT consumer. Verify SQL-only use without
drivers, separate provider closures, generated DTOs, schema-tool use and shipped
native loading. Check packaged DLL/API/XML correspondence and public instructions
against these archives. Recheck documentation examples after packaging even if
the documentation task passed earlier. Select checks by actual package inputs;
metadata-only changes must not trigger unrelated API work.

## Integration and stop

Deliver package manifests, independent-consumer results and scoped limitations to
integration/acceptance. Stop at reviewed candidate archives. No external publishing,
release attachment, raw-evidence upload, merge or old-product replacement is
authorized by this packet.
