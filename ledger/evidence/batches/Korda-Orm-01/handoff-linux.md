# Korda-Orm-01 Linux handoff

Status: source research, proposed design and implementation plan reviewed;
PR delivery and normal GitHub checks pending. No product implementation authorized.
This is the single maintained progress and continuation entry for this task.

## Scope and formal entries

- [Research plan](plan.md).
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
| Plan current authored plan | The commit containing this document; confirm the task branch/PR head before continuing |

A file cannot contain the hash of the commit that first contains that exact file.
The recorded substantive milestones and the current GitHub task-branch/PR head
together identify the continuation point; never assume an older recorded hash is
the latest branch state. PR numbers and final checks will be added after creation.

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

## Current checks and next work

Design's committed prose-only milestone selected zero checks through its normal
runner. Plan's independent schema/reference checks passed against the authored
30-node graph. The required `--all --install-dependencies` run passed all five
registered checks: 48 CI self-tests, current historical graph schema/references
(114 IDs), and independent ORM schema/references (30 IDs). Final committed-diff
selection and normal GitHub PR CI will be recorded after commit/PR creation.

Next: commit/push the reviewed formal Plan milestone, create one linked PR per
repository, record exact
heads/checks, and stop without merging or implementing products. To resume, fetch
both task branches, inspect their actual heads and this document, then continue
unfinished gates without repeating completed source studies or bounded probes.

No raw logs, prototypes, upstream copies, generated code, samples, command dumps,
agent intermediate material, runtime state or recovery caches belong in either
documentation repository. Reproduction recipes are concise maintained documents.
