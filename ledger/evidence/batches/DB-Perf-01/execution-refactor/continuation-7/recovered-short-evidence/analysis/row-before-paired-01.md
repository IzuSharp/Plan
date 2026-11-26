# Single-case ordinary and ABI observations

Validation: **valid_observations**.

C1, persistent session, requested prepared mode, 15 seconds per case. Transactions include ordinary CRUD construction because these APIs have no prepared overload.

Ordinary metrics include the complete business operation. CPU, managed allocation and GC cover the whole consumer process between steady endpoints; business and harness allocations are included. Framework-only allocation remains unproven.

| Provider | Cohort | Case | Ops | Ops/s | p50 / p95 / p99 (µs) | CPU µs/op | Managed B/op | GC 0/1/2 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| sqlite | korda | numeric | 82473 | 5498.156 | 169.984 / 294.912 / 430.080 | 317.670 | 2742.337 | 108/2/1 |
| sqlite | dapper | numeric | 804438 | 53629.111 | 16.768 / 18.688 / 44.032 | 18.619 | 1776.025 | 681/2/1 |
| sqlite | korda | tx-rollback | 2260 | 150.581 | 2424.832 / 19791.872 / 27262.976 | 2197.453 | 63005.097 | 68/2/1 |
| sqlite | dapper | tx-rollback | 201542 | 13435.891 | 62.464 / 115.200 / 319.488 | 74.284 | 14968.103 | 1441/2/1 |
| sqlite | korda | tx-commit | 1893 | 126.117 | 5898.240 / 20578.304 / 29884.416 | 2500.192 | 67060.636 | 61/2/1 |
| sqlite | dapper | tx-commit | 47667 | 3177.760 | 268.288 / 630.784 / 856.064 | 147.286 | 17248.436 | 391/2/1 |
| postgresql | korda | numeric | 47762 | 3184.119 | 294.912 / 444.416 / 679.936 | 368.948 | 2765.164 | 62/2/1 |
| postgresql | dapper | numeric | 132134 | 8808.883 | 100.864 / 168.960 / 261.120 | 98.426 | 2183.867 | 137/2/1 |
| postgresql | korda | tx-rollback | 2947 | 196.424 | 2359.296 / 17563.648 / 20578.304 | 2133.375 | 63310.702 | 89/2/1 |
| postgresql | dapper | tx-rollback | 24492 | 1632.745 | 577.536 / 823.296 / 1105.920 | 556.676 | 13739.709 | 160/2/1 |
| postgresql | korda | tx-commit | 2197 | 146.358 | 3866.624 / 19005.440 / 28835.840 | 2947.686 | 67168.757 | 71/2/1 |
| postgresql | dapper | tx-commit | 13047 | 869.747 | 1097.728 / 1417.216 / 2023.424 | 746.101 | 15739.594 | 96/2/1 |

## Separate ABI diagnostics

These are independent instrumented processes. Only After−Before count deltas are used. Pending counts attempts, not unique operations or timer expirations; no diagnostic latency or allocation is credited.

| Provider | Case | Business ops | Generic starts | Mandatory starts | Conditional tx close | Retire calls | Pending | OK | Structure |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |

## Evidence boundaries

Numeric SQL is checked against the actual manifest and generated Dapper source, retaining the distinct placeholder spelling. Matched lifecycle builds additionally bind their static SQL contract, actual emitted command factories, complete generated source and input hashes; historical builds without that proof retain their earlier SQL limitation. Driver transaction controls remain distinct, and no runtime wire trace is inferred from generated source or a lifecycle description. Each successful business operation passed the source-bound sticky oracle; an independent aggregate actual digest is not serialized.

Every requested directory and validation failure is retained below. JSON includes raw receipt/command/input hashes, source package commit metadata, owner drain, per-second business counts, RSS and ordinary cumulative CPU/allocation arithmetic. No long-run or host qualification is granted.

- `/workspace/scratch/4a65d70f0fe1/measurements/single-row-matched-sqlite-01`: valid
- `/workspace/scratch/4a65d70f0fe1/measurements/single-row-matched-postgresql-01`: valid

Pair comparisons: sqlite/numeric=valid, sqlite/tx-rollback=valid, sqlite/tx-commit=valid, postgresql/numeric=valid, postgresql/tx-rollback=valid, postgresql/tx-commit=valid
