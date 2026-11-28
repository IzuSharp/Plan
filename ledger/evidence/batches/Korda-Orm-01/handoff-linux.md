# Korda-Orm-01 Linux handoff

Status: delivered for user review. Source research, proposed design, implementation
plan and required document checks are complete within the limits below. No product
implementation, merge, cutover or deletion is authorized.
This is the single maintained progress and continuation entry for this task.

## Scope and formal entries

- [Research plan](plan.md).
- Paired open review PRs: [Korda-Design #23](https://github.com/IzuSharp/Korda-Design/pull/23) and [Plan #39](https://github.com/IzuSharp/Plan/pull/39); neither is merged.
- [Implementation plan](../../../../docs/korda-orm/README.md), [independent graph](../../../../docs/korda-orm/implementation-graph.json) and 30 task packets.
- [Design entry at the reviewed content milestone](https://github.com/IzuSharp/Korda-Design/tree/0c5f2c20cca4e386ac8f18c7a3d4c777f7f985d5/docs/korda-orm).
- [Shared contracts](https://github.com/IzuSharp/Korda-Design/blob/0c5f2c20cca4e386ac8f18c7a3d4c777f7f985d5/docs/korda-orm/contracts.md): ORM-C01–ORM-C06, proposed version 0.1.0.
- [Actual experiment results and reproduction methods](https://github.com/IzuSharp/Korda-Design/blob/0c5f2c20cca4e386ac8f18c7a3d4c777f7f985d5/docs/korda-orm/validation.md).

Only IzuSharp/Korda-Design and IzuSharp/Plan are writable. Both use
`task/Korda-Orm-01-linux` in isolated task/repository worktrees. Korda was inspected
read-only at `36bd5ba169b628ba4d61dd9fe260eaef5ff15599`; no product files, remote
branches, PRs, workflows or settings have been changed.

## Confirmed repository revisions

| Repository | Confirmed revision and role |
| --- | --- |
| Korda-Design initial main | `80746769f11874ae917e17a0f02f5ee47a3e250d` |
| Korda-Design formal design milestone | `62b3cbf5aa8da10e66ad5405bfad6a9a05ef9795`; source mappings, architecture, contracts and bounded validation |
| Korda-Design final proposed design | `0c5f2c20cca4e386ac8f18c7a3d4c777f7f985d5`; final profile-scope clarification, pinned by the implementation graph |
| Plan initial main | `911c9764d0bfe10e78862251b43fcf108a8696e8` |
| Plan initial persisted plan/handoff | `5719606db7205d3d98e6cd903271f02c973dfa59` |
| Plan substantive delivery | `0d19841d142ba49b2cafe27640c9347b0515ccc6`; complete implementation graph, packets and CI extension |
| Plan final handoff revision | The commit containing this document at [PR #39 head](https://github.com/IzuSharp/Plan/pull/39); follow-up changes only record delivery/progress metadata |

A file cannot contain the hash of the commit that first contains that exact file.
The recorded substantive milestones and the current GitHub task-branch/PR head
together identify the continuation point; never assume an older recorded hash is
the latest branch state. The PR heads and Checks tabs identify any later handoff-only
commit and its current CI result without a self-referential hash in this file.

## Confirmed direction and research state

| Area | State and result |
| --- | --- |
| jOOQ core/types | Selected-source review complete at 3.21.10 / `3c58109e7ab69772de75e640852935ee7e284177`; mature SQL concepts retained, Java JDBC/binding coupling separated |
| Rendering/dialects/schema | Source mapping complete for listed symbols; commercial transformation gaps, unavailable full test corpus and execution-dependent RETURNING identified |
| Dapper.AOT/drivers | Fixed-source review complete; default independent generated/manual typed execution selected, with optional Dapper bridge separately gated |
| Architecture/contracts | Drafted and cross-reviewed; driver-free model/rendering, immutable template, per-invocation arguments, offline generation and profile-specific capabilities |
| Implementation plan | 30 planned candidates in an isolated graph; start/acceptance dependencies separate, parser optional, cutover/retirement separate |
| Document CI | Independent graph schema/reference checks added only in Plan; existing Python dispatcher/YAML and legacy graphs unchanged |
| Final review | Independent source/semantic/execution/graph/CI reviews complete for actual authored files; findings repaired and rechecked |

Selected architecture: pure C# DSL → semantic model/types → profile validation and
renderer → SQL/typed occurrence/result template → independent binding/mapping →
Npgsql, Microsoft.Data.Sqlite or MySqlConnector. No C++/Rust compiler or executor
is a prerequisite. Existing product removal is deferred until separate acceptance
and authorized cutover.

Cross-review already resolved several real issues: render-template validation
must not require request values; literal constants belong to shape cache identity;
expanded-list arity is a structural render input; unused members of a known argument
superset are permitted; same-name slots retain distinct identity; accessible init/
record construction is supported; advanced neutral types do not wait for every
driver; each provider now owns its declared advanced codec implementation; nested
module fixtures are not represented as real database acceptance; package acceptance
includes every actually shipped module. Contract references and root-file ownership
were reconciled with the packets. Migration/deletion requires a concrete reviewed
file manifest before expanding the currently recorded write scopes.

## Actual bounded validation

- Java jOOQ SQL-only oracle: two runtime branches, 34 assertions each; no JDBC driver or database connection.
- Actual jOOQ SQLite output: five in-memory SQLite 3.53.1 semantic assertions passed.
- Pure C# DSL: two Linux Native AOT runs, 11 assertions each; incompatible generic operand failed with CS1503; two emitted-SQL SQLite cases passed.
- Offline incremental Schema Generator: native consumer passed eight assertions; invalid schema failed KO001 and wrong typed comparison failed CS0411.
- Dapper 2.1.100 / Dapper.AOT 1.1.0 / Microsoft.Data.Sqlite 11.0.0: runtime SQL with known argument/DTO types ran natively, returned 3/2 rows and matched direct-driver results; unsupported CommandDefinition call failed DAP057.

These are research probes, not product acceptance. PostgreSQL/MySQL/MariaDB live
execution, the complete Korda generator/semantic corpus, streaming/cancellation
matrix, exact shipped packages and controlled Dapper performance comparisons remain
future implementation gates. No parity or zero-GC claim has been established.

## Completed checks and review

| Gate | Observed result |
| --- | --- |
| Design local committed diff | Registered prose, zero checks selected; no product jobs |
| Plan required full check | All five registered checks passed with pinned dependencies; 48 CI self-tests, 114 historical task IDs and 30 ORM IDs valid |
| Plan committed PR diff | All five checks passed; local run completed in 27.72 seconds |
| Design GitHub PR CI | [Run 46168738533](https://github.com/IzuSharp/Korda-Design/actions/runs/46168738533) succeeded at `0c5f2c20cca4e386ac8f18c7a3d4c777f7f985d5` |
| Plan substantive GitHub PR CI | [Run 46168697427](https://github.com/IzuSharp/Plan/actions/runs/46168697427) succeeded at `0d19841d142ba49b2cafe27640c9347b0515ccc6` |
| Final metadata follow-up | This handoff/progress-only commit retains the checked graph/CI/design inputs; consult [Plan PR checks](https://github.com/IzuSharp/Plan/pull/39/checks) for its exact current head result |
| File-purpose and link audit | Design 10 changed files; Plan 42 changed files; only formal Markdown, the isolated graph/schema and maintained CI Python; checked local links resolve |
| Cross-repository binding | Plan graph pins the actual final Design head; all ORM nodes remain planned candidates and authorization remains false |

Independent source/model, SQL/schema and execution reviewers examined other
owners' actual design/packet files. Final graph reviews checked start/acceptance
DAGs, contract inputs, scope ownership and the advanced/nested/provider split.
A separate SQL/schema reviewer examined the CI author's actual registry/checker/
schema/test changes. Found issues were repaired and the relevant revisions read
again. This is an actual scoped cross-review, not a claim of exhaustive jOOQ
coverage, independent product implementation or unperformed database tests.

## Stop and continuation conditions

This research task stops with the two open PRs. No further research campaign,
product implementation, package publication, merge or old-code removal starts
implicitly. The next action is the user's paired design/plan review.

If the user later accepts these revisions and separately authorizes product work,
start ORM-FOUNDATION from the then-current product main using the pinned contracts.
After its shared signatures/ownership pass, launch the independent language,
render/dialect, schema/generator, execution/provider and verification worktrees
according to start dependencies. Acceptance dependencies still require real
implementations. Parser remains optional. This plan's final aggregate includes
four profiles and mandatory advanced/nested slices; any smaller release proposal
must explicitly revise and review that scope. Cutover and retirement remain
separate authorized stages with concrete file manifests.

To resume this documentation task after an interruption, fetch both task branches,
inspect their actual heads and PR checks, and use this document's remaining limits.
Do not repeat completed source studies or bounded probes merely to recreate logs.

No raw logs, prototypes, upstream copies, generated code, samples, command dumps,
agent intermediate material, runtime state or recovery caches belong in either
documentation repository. Reproduction recipes are concise maintained documents.
