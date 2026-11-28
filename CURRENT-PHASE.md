# Current phase and recorded scope

## Independent proposed direction

[Korda-Orm-01](docs/korda-orm/README.md) defines a new jOOQ-derived pure C# SQL
framework with independent rendering and mature .NET driver execution. Its
implementation graph is isolated from the historical graphs below. Research and
bounded prototype results are recorded in the [Linux handoff](ledger/evidence/batches/Korda-Orm-01/handoff-linux.md).
All new product tasks remain planned candidates; this study does not authorize
implementation, cutover, deletion or merge.

## Existing product and historical records

Korda is a C# Fluent ORM for PostgreSQL and SQLite with Native AOT and a C++20
execution layer using libpq/sqlite3. Ordinary C# model/DTO changes reuse native
assets. Provider packages remain independently installable. The historical Rust
and Server plans remain task definitions; they are not the current product scope.

## Recorded delivery

- DB-Scope-01 reduced the product to the database scope; [final result](ledger/evidence/batches/DB-Scope-01/results/linux-acceptance-summary.md).
- DB-CPP-01 completed the behavior-compatible native migration; [migration result](ledger/evidence/batches/DB-CPP-01/migration-report-linux.md) and [contract mapping](ledger/evidence/batches/DB-CPP-01/migration-table.md).
- DB-API-01 completed the Fluent ORM experience work and independent provider package consumption; [plan and outcome](ledger/evidence/batches/DB-API-01/plan.md).
- DB-Rename-01 records the `Db*` attribute naming scope and compatibility boundary; [plan](ledger/evidence/batches/DB-Rename-01/plan.md).
- DB-Exec-11 records the selected 17da execution path, four local 1,800-second comparisons, normal delivery and remaining gaps; [final report](ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/final-report.md).

The final recorded comparison does not establish Dapper.AOT parity, maximum
sustainable throughput, zero framework allocation, or exhaustion of optimization
ideas. The three [remaining attribution directions](ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-7/remaining-hot-path-costs.md)
remain hypotheses until separately measured and reviewed. Earlier shorter
before/current measurements retain their own scope.

## Interpretation of historical task data

The graphs preserve R01–R34 and D01–D32 accepted design/research states and
A01–A24/B01–B24 planned-candidate states. Later batch outcomes do not rewrite the
original graph nodes into new product acceptance. Historical source commits and
PRs identify the work; raw logs, copied snapshots and receipt bindings are no
longer part of this documentation repository's current-tree contract.

Document CI validates current structure and dependencies only. Product tests,
packaging, publication and performance execution belong to Korda's own authorized
work. This documentation cleanup authorizes no product change or resumed campaign.
