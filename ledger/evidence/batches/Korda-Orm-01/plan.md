# Korda-Orm-01 research and design plan

Status: reopened by the user for mature execution reuse research and implementation-ready specifications. The first delivery remains recorded below. This task authorizes research, design, an implementation plan,
and necessary document CI changes only. It does not authorize product work or a merge.

## Objective and boundaries

Design Korda.Orm as a Native AOT-first, type-safe SQL framework for C#: a source-informed
semantic rewrite of jOOQ's open-source SQL language, with a driver-free DSL and an
explicit SQL/typed-parameter boundary to mature .NET execution. Dapper.AOT is the
execution and mapping reference, not a presumed solution to every dynamic query.

Only IzuSharp/Korda-Design and IzuSharp/Plan may change. Both use
`task/Korda-Orm-01-linux` in separate task/repository-named worktrees. IzuSharp/Korda
is read-only. Historical database, C++, Rust and Server tasks provide context only;
their task graphs and acceptance states do not govern this direction.

## Work and ownership

| Workstream | Scope | Owner | Initial state |
| --- | --- | --- | --- |
| Core language | jOOQ DSL, model, types, nullability, mutability, JDBC coupling, licenses | Core researcher | Source mapping, design and bounded generator probe complete |
| SQL and generation | Rendering, dialects, transformations, advanced SQL, schema/codegen, parser and available tests | Dialect researcher | Source mapping, design and bounded Java/SQLite probes complete |
| Execution and AOT | Dapper.AOT, drivers, generated binding/mapping, toolchain, dynamic SQL boundaries | Execution researcher | Source mapping, design and bounded Dapper.AOT/SQLite probe complete |
| Integration | Repository norms, contracts, experiments, CI, implementation DAG, cross-review | Coordinating researcher | Shared contracts and 30-task graph reviewed; local and substantive PR CI passed |

These are actual concurrent research assignments. Confirmed independent sections
move into Design and Plan authoring while remaining research continues. Each author
owns distinct files; the coordinator owns shared contracts, the plan, and this batch's
single [handoff](handoff-linux.md). Reviews examine other authors' actual deliverables.

Paired deliverables: [Design #23](https://github.com/IzuSharp/Korda-Design/pull/23)
and [Plan #39](https://github.com/IzuSharp/Plan/pull/39). The maintained handoff
records exact revisions, CI runs, bounded experiments and remaining product gates.
All seven research milestones below are complete within those recorded limits;
the proposed product tasks remain unimplemented and unauthorized.

## Milestones and evidence gates

1. Establish source snapshots, repository boundaries and this persistent plan.
2. Inspect implementation paths and distinguish reusable OSS behavior, deliberate
   C# adaptations, unavailable commercial code, and unresolved questions.
3. Set shared model, rendering, parameter/result and generator contracts. Record
   public promises separately from internal implementation suggestions.
4. Run feasible local experiments for dynamic DSL/AOT, typing, SQL/parameter
   correctness, generators and execution. Record exact environment, commands and
   bounded results; identify every unexecuted gate explicitly.
5. Author isolated architecture, semantics, API, provenance and verification
   specifications in Korda-Design, and parallelizable task packets/DAG in Plan.
6. Independently review source claims, contract consistency, task dependencies,
   document routing and final file purpose. Repair substantive findings.
7. Run selected local checks and normal PR CI, open one mutually linked PR in each
   writable repository, update the handoff, and stop without merging.

The final plan must separate start dependencies from integration/acceptance
dependencies so implementation can proceed against agreed interfaces. Schema,
generator, renderer, provider and verification work must not inherit irrelevant
historical prerequisites. Product migration and old-code removal are later gates.

## Source and validation policy

Pin release tags and full commit SHAs, then cite implementation symbols and the
specific behavior they establish. Do not equate API documentation, open-source
stubs, or a commercial feature description with available implementation.
Tests should compare semantics, parameter order/types and negative cases, not only
SQL text. Measure construction/rendering separately from execution and mapping.

The initially missing SDK was installed in an isolated local toolchain from official
.NET 11.0.100 metadata with archive checksum verification. Bounded pure-DSL, offline
Schema Generator and Dapper.AOT/SQLite Native AOT probes ran, including negative
compilation cases. The exact conditions, results and limitations are maintained in
[Design validation](https://github.com/IzuSharp/Korda-Design/blob/0c5f2c20cca4e386ac8f18c7a3d4c777f7f985d5/docs/korda-orm/validation.md).
No product, full database matrix or performance parity is claimed.

## Document CI and persistence

Existing `ledger/*.md` and `docs/*.md` prose rules cover authored documents and
select zero checks. The legacy graph schema requires historical task identities;
the isolated [implementation graph](../../../../docs/korda-orm/implementation-graph.json)
therefore has its own registered schema and reference checks, without changing the
legacy graph or the existing dispatcher/workflow. Preserve each repository's current PR diff semantics and Python entrypoint.
No product build, database benchmark or evidence upload belongs in document CI.

Commit and push formal milestones as they become reviewable. Keep only decisions,
source references, concise results, reproduction methods and next work in Git.
All upstream checkouts, experiments, logs, scripts, samples and intermediate agent
material stay outside the document worktrees and are never uploaded elsewhere.

## Authorized continuation: mature execution reuse and implementation-ready packets

The 2026-11-28 continuation keeps PRs Design #23 / Plan #39 and the existing task
branches. The earlier default of independent Korda binder/projector execution is
reopened; it is a comparison/fallback candidate, not a settled architecture. Keep
valid jOOQ language work and earlier bounded results without rerunning them merely
to reproduce evidence. Product implementation and merge remain unauthorized.

| Parallel owner | Investigation and formal output | Initial state |
| --- | --- | --- |
| Mature .NET execution | Original Dapper.AOT dynamic bags; public runtime CommandFactory/RowFactory; complete native DSL-to-SQLite path and minimum source adaptations | Active |
| Generator integration | Direct factory generation, natural Fluent terminals, same-compilation visibility, staged generation alternatives and precise generated-code contracts | Active |
| Java/jOOQ execution | Binding/mapping/cursor source semantics, GraalVM/JDBC shared-library path, ownership/GC/deployment costs and hybrid alternatives | Active |
| Coordinator | Shared fixtures, other mature candidates, independent server matrix, controlled execution comparisons, exact contracts, packet completeness and reviews | Active |

Each promising route must cross the complete typed DSL → SQL/typed parameters →
mature execution → real database → known C# result boundary in a native consumer.
Report library/compiler/driver/license/environment limitations separately. A public
API or generator limitation does not by itself establish technical impossibility.
Prefer reuse, then extension, then source translation; new execution mechanisms
require a specific remaining gap and an explicit reason.

The implementation plan must become an execution specification: fixed public and
internal signatures, file/module boundaries, upstream symbol mappings, ordered
algorithms, state/ownership transitions, exact diagnostics, positive and negative
fixtures with expected values, local commands, integration seams and stop gates.
Shared design decisions belong in Design and are pinned from each packet; packet
implementers must not choose the architecture or invent missing protocols. Compile
representative specification surfaces in disposable experiments before describing
them as compile-checked. Do not label unchecked pseudocode as working product code.

Continuation milestones: (1) record this reopening; (2) verify substantive mature
reuse routes and native end-to-end behavior; (3) compare representative costs and
maintenance responsibilities; (4) select and specify the implementation in detail;
(5) cross-review actual sources, evidence and packets; (6) pin final Design from
Plan, pass normal local/PR document checks, update the same handoff and stop for
review. Stop the research only when a supported route merits implementation, or
when remaining reasonable routes have substantiated blockers and recovery conditions.
