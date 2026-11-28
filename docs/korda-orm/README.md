# Korda.Orm implementation specification and task plan

Status: **30 planned candidates; product implementation not authorized**. Research
has selected a supported mature-runtime route. These packets fix implementation
choices in enough detail to execute against one reviewed contract; they are not
production implementations or evidence that those future product gates passed.

The [implementation graph](implementation-graph.json) is the scheduling authority.
Its current immutable Design input is
[`b67317b2a89245fe82337b9b69e2748626ac67cb`](https://github.com/IzuSharp/Korda-Design/tree/b67317b2a89245fe82337b9b69e2748626ac67cb/docs/korda-orm),
with **ORM-C01–ORM-C06 version 0.2.0**. Final consistency corrections are being
reviewed in the same paired PRs; update this exact pin when those corrections are
published, before accepting this delivery. Branch links are navigation, not an
immutable implementation input. Any later contract change must update the graph
pin and affected packets together.

The [research plan](../../ledger/evidence/batches/Korda-Orm-01/plan.md) and single
[Linux handoff](../../ledger/evidence/batches/Korda-Orm-01/handoff-linux.md) record
actual research, revisions, review findings and document CI. This independent
ORM graph has no historical R/D/A/B, DB-Exec-Parity-01, C++, Rust, Server or Go
scheduling prerequisite.

## Fixed route and first reading order

The default is pure C# SQL semantics translated from reviewed jOOQ sources,
unmodified **Dapper.AOT 1.1.0 Runtime**, a small typed-layout CommandFactory adapter,
normal incremental generation of RowFactory subclasses, and mature .NET drivers.
The plan does not delegate a new reader loop, connection pool, scheduler, retry
engine or ORM architecture decision to an implementer. Original explicit-bag
Dapper.AOT and stable prebuild generation remain demonstrated alternatives; they
do not create two competing default implementations.

Read the pinned Design files in this order:

1. `architecture.md` and `execution-aot.md`: selected route, alternatives and limits.
2. `contracts.md` and `implementation-spec.md`: exact shared types, internal seams,
   dependency direction, immutable values/templates, diagnostics and algorithms.
3. `mature-execution.md`, `generation-integration.md` and the applicable source
   mapping: actual upstream mechanisms to reuse, exact source adaptations and
   generator/driver ownership.
4. The assigned task packet, its graph edges, the neighboring interface-owning
   packets and `validation.md`: concrete work and the evidence needed to accept it.

Each packet fixes owned paths, API signatures, representations, ordered algorithms,
state/ownership transitions, error codes, positive/negative fixtures and expected
results, exact local entrypoints, integration inputs and stop conditions. Those
sections are an execution specification. An actual contradiction goes back to the
contract owner for a coordinated patch; an implementer must not choose an
unrecorded fallback, introduce a parallel interface or label a stub as complete.

## Authorization and launch

Before ORM-FOUNDATION, require the user's acceptance of the paired Design/Plan
revisions and authorization for product implementation. Read the then-current
Korda AGENTS, module and CI rules. Resolve actual conflicts through reviewed
contract updates while preserving unrelated products and accepted work.

Every graph node remains `planned_candidate`; `implementation_authorized` remains
false. Editing a flag grants no permission. Passing product acceptance does not
itself authorize package publication, cutover or deletion; those later actions
retain the concrete scope gates in their packets.

## Parallel scheduling and ownership

`start_dependencies` permit substantive work against accepted shared contracts.
`acceptance_dependencies` require real peer implementations before accepting that
work. Check both edge sets for cycles, without turning acceptance inputs into a
serial start queue. ORM-FOUNDATION compiles the full agreed shared surface, initial
project/reference map and data invariants. It is not the implementation of every
language, renderer, driver or generator module.

After Foundation, the following owners can work concurrently:

| Parallel group | Packets | Interface and acceptance responsibility |
| --- | --- | --- |
| Language and types | [TYPES](tasks/ORM-TYPES.md), [QUERY](tasks/ORM-QUERY.md), [EXPRESSIONS](tasks/ORM-EXPRESSIONS.md), [DML](tasks/ORM-DML.md), [RELATIONAL](tasks/ORM-RELATIONAL.md) | Shared immutable nodes in Contracts; disjoint Language subdirectories; exact typed composition and validation |
| Pure SQL | [RENDER](tasks/ORM-RENDER.md), [POSTGRES](tasks/ORM-POSTGRES-DIALECT.md), [SQLITE](tasks/ORM-SQLITE-DIALECT.md), [MYSQL](tasks/ORM-MYSQL-DIALECT.md), [MARIADB](tasks/ORM-MARIADB-DIALECT.md) | Rendering depends on a Contracts strategy seam; dialect factories attach rules; dialects accept actual advanced/nested lowerings |
| Schema and generation | [SCHEMA](tasks/ORM-SCHEMA.md), [GENERATOR](tasks/ORM-GENERATOR.md), [SCHEMA-TOOL](tasks/ORM-SCHEMA-TOOL.md) | Offline portable schema and emitters; static factories/consumer roots; explicit provider-owned acquisition |
| Execution and transport | [EXECUTION](tasks/ORM-EXECUTION.md), [POSTGRES](tasks/ORM-POSTGRES-DRIVER.md), [SQLITE](tasks/ORM-SQLITE-DRIVER.md), [MYSQL](tasks/ORM-MYSQL-DRIVER.md) | Mature runtime adaptation, exact admission/cleanup, strict codecs and provider catalog readers |
| Advanced language/results | [ADVANCED-TYPES](tasks/ORM-ADVANCED-TYPES.md), [NESTED](tasks/ORM-NESTED.md), optional [PARSER](tasks/ORM-PARSER.md) | Pure representations, deterministic lowering and bounded typed decoding; parser excluded from initial mandatory package scope |
| Engineering and composition | [ORACLE](tasks/ORM-ORACLE.md), [CI](tasks/ORM-CI.md), [PACKAGE](tasks/ORM-PACKAGE.md), [DOCS](tasks/ORM-DOCS.md), [INTEGRATION](tasks/ORM-INTEGRATION.md), [PERFORMANCE](tasks/ORM-PERFORMANCE.md) | Harnesses start early; acceptance waits for their actual modules, exact archives and database inputs |

[FOUNDATION](tasks/ORM-FOUNDATION.md) owns initial Contracts, node declarations,
project files and module entries. After its acceptance, ORM-CI owns shared routing,
registry, solution and root build files. Language owners edit separate Query,
Expressions, Dml and Relational directories; facade partial files stay in one
assembly. Packaging owns composition; leaf owners own their source/API baselines.
Use one task/repository worktree per owner and return shared changes to that owner.

No test double creates an alternative shipping interface. Rendering has no hard
reference to concrete dialects; each profile factory attaches immutable rules via
Contracts. Nested lowering is pure. Provider metadata readers live in Providers,
SchemaTool consumes them, and the analyzer links the portable schema/emitter
sources appropriate to its netstandard2.0 host. These directions prevent project
cycles and leave the agreed independent work genuinely startable.

PostgreSQL, SQLite, MySQL and MariaDB are all mandatory final profiles, as are the
specified advanced and nested slices. PostgreSQL/SQLite may be the first live wave;
that sequencing does not block other workers or authorize a smaller release.
Parser remains an explicit optional module. Seven public products share one core
and one Execution assembly; provider packages do not copy either implementation.
The exact dependency-feed staging and existing-runner extension are fixed in
ORM-PACKAGE and ORM-CI, including hashes, exact versions and dependency-first
publication. Packaging is not an invitation to redesign the existing dispatcher.

## Acceptance and migration

Module acceptance requires actual outputs from its graph dependencies. The
aggregate [INTEGRATION](tasks/ORM-INTEGRATION.md) gate executes the four real native
provider lanes and exact package consumers. [PERFORMANCE](tasks/ORM-PERFORMANCE.md)
uses declared comparable public paths and prospective budgets; research medians
are not product parity evidence. [ACCEPTANCE](tasks/ORM-ACCEPTANCE.md) independently
reviews source, packages, behavior, resources, generation, CI and costs.

Only then may a separately authorized [CUTOVER](tasks/ORM-CUTOVER.md) switch a
concrete consumer/file manifest. [RETIRE](tasks/ORM-RETIRE.md) removes only the
reviewed obsolete closure after successful cutover and separate deletion scope.
No task inherits permission to merge, publish, migrate or remove old code simply
because its tests pass.

## Validation and stop policy

Distinguish declaration compilation, pure semantic fixtures, actual rendering,
real databases, real generated output, Native AOT execution and exact shipped
package consumption. A completed harness cannot count missing product outputs as
passing. Use the pinned Design and each packet's literal commands/fixtures; record
unsupported cells and invalid measurements explicitly. Long campaigns remain
outside ordinary CI. Product evidence must use the final public path, including
strict mapping and invocation ownership, rather than only the small research
adapter that justified this design.

## Document CI

The maintained Python runner registers this direction independently. Graph edits
select `orm-graph-schema` and `orm-task-links`; packet edits select their reference
check; ordinary prose selects zero checks. Schema changes reach their registered
graph users, and CI infrastructure changes run self-tests/current content checks.
The historical graph is unchanged and is not an ORM prerequisite.

```sh
python3 eng/ci/run.py --event pull_request --base origin/main --head HEAD --list
python3 eng/ci/run.py --event pull_request --base origin/main --head HEAD
```

Document CI does not fetch another repository, compile the product, start a
service or run benchmarks. The immutable Design binding and semantic consistency
are reviewed separately. All research checkouts, generated code, scripts, binaries,
raw logs and benchmark outputs remain outside both document repositories.
