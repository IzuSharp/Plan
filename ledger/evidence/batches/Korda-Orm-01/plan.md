# Korda-Orm-01 research and design plan

Status: research/design/plan delivered for user review; required document checks passed. This task authorizes research, design, an implementation plan,
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
