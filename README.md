# Korda Plan

This repository holds plans, tasks, dependencies, progress and final conclusions
for [Korda](https://github.com/IzuSharp/Korda). Architecture and interface contracts
live in [Korda-Design](https://github.com/IzuSharp/Korda-Design).

## Current records

- [Korda.Orm independent implementation plan](docs/korda-orm/README.md): mature-runtime reuse and detailed execution specifications; 30 planned candidates, no product authorization
- [Korda-Orm-01 research and Linux handoff](ledger/evidence/batches/Korda-Orm-01/handoff-linux.md)
- [Current phase and historical boundaries](CURRENT-PHASE.md)
- [Task index](task-index.md): 34 research, 32 documentation and 48 delivery definitions
- [Acceptance register](acceptance-register.md): recorded outcomes and limitations
- [DB execution plan and outcome](ledger/evidence/batches/DB-Perf-01/plan.md)
- [Final DB-Exec-11 comparison](ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/final-report.md)
- [Three remaining cost-attribution directions](ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/remaining-hot-path-costs.md)

The three historical JSON graphs retain their task IDs, recorded states and dependencies.
The 114 task packets and ten fragments retain technical requirements and historical
scope. Those historical definitions do not authorize implementation or revive
retired product directions. Later delivered batches are documented separately.

## Document CI

[eng/ci/registry.py](eng/ci/registry.py) registers paths, document types, checks and
affected types. [eng/ci/run.py](eng/ci/run.py) selects checks from the real PR/push
diff. [The guide](eng/ci/README.md) explains local use and extension.

Ordinary prose requires zero checks. Graph edits select schema and task-reference
checks; packet or fragment changes select their reference checks; schema changes
validate current graph users. CI changes run CI self-tests. Each check runs once.
There are no historical acceptance replays, cross-repository checkouts, benchmark
jobs or artifact uploads.

The `ledger/evidence/` prefix is retained for existing authored plan/result links;
it contains concise documents, not raw evidence. Temporary logs, traces, samples,
archives, receipts and execution-machine recovery state are no longer stored in
the current tree. Their removal does not change the meaning of past decisions or
claim new execution. Git history is not rewritten.

Read [AGENTS.md](AGENTS.md) before adding or moving documents.
