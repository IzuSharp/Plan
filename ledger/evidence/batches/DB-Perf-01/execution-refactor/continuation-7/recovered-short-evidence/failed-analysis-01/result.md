# Single-case ordinary and ABI observations

Validation: **incomplete_or_invalid**.

C1, persistent session, requested prepared mode, 15 seconds per case. Transactions include ordinary CRUD construction because these APIs have no prepared overload.

Ordinary metrics include the complete business operation. CPU, managed allocation and GC cover the whole consumer process between steady endpoints; business and harness allocations are included. Framework-only allocation remains unproven.

| Provider | Cohort | Case | Ops | Ops/s | p50 / p95 / p99 (µs) | CPU µs/op | Managed B/op | GC 0/1/2 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| sqlite | korda | numeric | 79225 | 5281.649 | 178.176 / 292.864 / 432.128 | 337.975 | 2747.311 | 104/2/1 |
| sqlite | dapper | numeric | 790386 | 52692.039 | 16.640 / 21.248 / 70.144 | 18.926 | 1776.025 | 669/2/1 |
| sqlite | korda | tx-rollback | 11695 | 779.655 | 1212.416 / 1671.168 / 3080.192 | 1902.430 | 61794.783 | 348/2/1 |
| sqlite | dapper | tx-rollback | 204857 | 13657.010 | 62.464 / 111.104 / 292.864 | 73.126 | 14968.101 | 1465/2/1 |
| sqlite | korda | tx-commit | 8130 | 541.942 | 1761.280 / 2408.448 / 4046.848 | 2062.737 | 65306.946 | 256/2/1 |
| sqlite | dapper | tx-commit | 48923 | 3261.451 | 262.144 / 573.440 / 897.024 | 146.546 | 17248.425 | 402/2/1 |
| postgresql | korda | numeric | 45858 | 3057.167 | 307.200 / 471.040 / 700.416 | 366.667 | 2755.730 | 59/2/1 |
| postgresql | dapper | numeric | 125302 | 8353.437 | 104.960 / 179.200 / 284.672 | 98.393 | 2183.848 | 130/2/1 |
| postgresql | korda | tx-rollback | 6784 | 452.249 | 2146.304 / 2818.048 / 4259.840 | 2113.543 | 62099.844 | 202/2/0 |
| postgresql | dapper | tx-rollback | 23727 | 1581.741 | 585.728 / 864.256 / 1212.416 | 575.211 | 13738.346 | 155/2/1 |
| postgresql | korda | tx-commit | 5252 | 350.080 | 2768.896 / 3604.480 / 5341.184 | 2300.659 | 65492.862 | 165/2/1 |
| postgresql | dapper | tx-commit | 13189 | 879.230 | 1064.960 / 1458.176 / 2408.448 | 706.132 | 15741.226 | 97/2/1 |

## Separate ABI diagnostics

These are independent instrumented processes. Only After−Before count deltas are used. Pending counts attempts, not unique operations or timer expirations; no diagnostic latency or allocation is credited.

| Provider | Case | Business ops | Generic starts | Mandatory starts | Conditional tx close | Retire calls | Pending | OK | Structure |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |

## Evidence boundaries

Numeric SQL is checked against the actual manifest and generated Dapper source, retaining the distinct placeholder spelling. Matched lifecycle builds additionally bind their static SQL contract, actual emitted command factories, complete generated source and input hashes; historical builds without that proof retain their earlier SQL limitation. Driver transaction controls remain distinct, and no runtime wire trace is inferred from generated source or a lifecycle description. Each successful business operation passed the source-bound sticky oracle; an independent aggregate actual digest is not serialized.

Every requested directory and validation failure is retained below. JSON includes raw receipt/command/input hashes, source package commit metadata, owner drain, per-second business counts, RSS and ordinary cumulative CPU/allocation arithmetic. No long-run or host qualification is granted.

- `/workspace/scratch/4a65d70f0fe1/measurements/single-command-sqlite-01`: valid
- `/workspace/scratch/4a65d70f0fe1/measurements/single-command-postgresql-01`: valid
- `/workspace/scratch/4a65d70f0fe1/measurements/ffi-single-command-sqlite-01`: invalid_or_missing
  - `diagnostic-tx-rollback`: structure_mismatch; see structural mismatches in JSON
  - `diagnostic-tx-commit`: structure_mismatch; see structural mismatches in JSON
- `/workspace/scratch/4a65d70f0fe1/measurements/ffi-single-command-postgresql-01`: invalid_or_missing
  - `diagnostic-tx-rollback`: structure_mismatch; see structural mismatches in JSON
  - `diagnostic-tx-commit`: structure_mismatch; see structural mismatches in JSON

Pair comparisons: sqlite/numeric=missing_invalid_or_ambiguous, sqlite/tx-rollback=missing_invalid_or_ambiguous, sqlite/tx-commit=missing_invalid_or_ambiguous, postgresql/numeric=missing_invalid_or_ambiguous, postgresql/tx-rollback=missing_invalid_or_ambiguous, postgresql/tx-commit=missing_invalid_or_ambiguous
