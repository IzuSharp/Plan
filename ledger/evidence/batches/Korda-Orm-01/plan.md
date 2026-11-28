# Korda-Orm-01 research and design plan

Status: in progress. This task authorizes research, design, an implementation plan,
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
| Core language | jOOQ DSL, model, types, nullability, mutability, JDBC coupling, licenses | Core researcher | Source inspection in progress |
| SQL and generation | Rendering, dialects, transformations, advanced SQL, schema/codegen, parser and available tests | Dialect researcher | Source inspection in progress |
| Execution and AOT | Dapper.AOT, drivers, generated binding/mapping, toolchain, dynamic SQL boundaries | Execution researcher | Source inspection in progress |
| Integration | Repository norms, contracts, experiments, CI, implementation DAG, cross-review | Coordinating researcher | Repository baseline established |

These are actual concurrent research assignments. Confirmed independent sections
move into Design and Plan authoring while remaining research continues. Each author
owns distinct files; the coordinator owns shared contracts, the plan, and this batch's
single [handoff](handoff-linux.md). Reviews examine other authors' actual deliverables.

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

The initial toolchain check found no `dotnet` on PATH. Availability of an installable
SDK and Native AOT prerequisites is being checked; no compiled or AOT result is
claimed at this stage. Lack of an executable environment must become an explicit
validation limitation and a future task gate, not a fabricated success.

## Document CI and persistence

Existing `ledger/*.md` and `docs/*.md` prose rules cover authored documents and
select zero checks. The legacy graph schema requires historical task identities;
an isolated new implementation graph may need a small registered schema/check
extension. Preserve each repository's current PR diff semantics and Python entrypoint.
No product build, database benchmark or evidence upload belongs in document CI.

Commit and push formal milestones as they become reviewable. Keep only decisions,
source references, concise results, reproduction methods and next work in Git.
All upstream checkouts, experiments, logs, scripts, samples and intermediate agent
material stay outside the document worktrees and are never uploaded elsewhere.
