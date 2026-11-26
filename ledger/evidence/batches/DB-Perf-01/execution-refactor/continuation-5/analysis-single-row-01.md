# Single-case ordinary and ABI observations

Validation: **incomplete_or_invalid**.

C1, persistent session, requested prepared mode, 15 seconds per case. Transactions include ordinary CRUD construction because these APIs have no prepared overload.

Ordinary metrics include the complete business operation. CPU, managed allocation and GC cover the whole consumer process between steady endpoints; business and harness allocations are included. Framework-only allocation remains unproven.

| Provider | Cohort | Case | Ops | Ops/s | p50 / p95 / p99 (µs) | CPU µs/op | Managed B/op | GC 0/1/2 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| sqlite | korda | numeric | 81033 | 5402.156 | 176.128 / 290.816 / 421.888 | 335.581 | 2750.593 | 106/2/1 |
| sqlite | dapper | numeric | 793769 | 52916.719 | 16.640 / 20.096 / 60.416 | 18.807 | 1776.025 | 672/2/1 |
| sqlite | korda | tx-rollback | 2073 | 138.112 | 6356.992 / 20185.088 / 24510.464 | 2364.371 | 63047.464 | 62/2/1 |
| sqlite | dapper | tx-rollback | 310656 | 20710.206 | 39.936 / 74.752 / 222.208 | 48.274 | 13072.067 | 1940/2/1 |
| sqlite | korda | tx-commit | 1637 | 109.123 | 7766.016 / 21889.024 / 31064.064 | 2394.867 | 67020.794 | 52/2/1 |
| sqlite | dapper | tx-commit | 51076 | 3404.999 | 238.592 / 626.688 / 933.888 | 120.868 | 15336.407 | 373/2/1 |
| postgresql | korda | numeric | 46178 | 3078.471 | 307.200 / 462.848 / 696.320 | 378.379 | 2764.575 | 60/2/1 |
| postgresql | dapper | numeric | 125103 | 8340.141 | 103.936 / 175.104 / 282.624 | 102.229 | 2183.820 | 129/2/1 |
| postgresql | korda | tx-rollback | 2460 | 163.888 | 2801.664 / 19136.512 / 26607.616 | 2397.881 | 63245.776 | 74/2/1 |
| postgresql | dapper | tx-rollback | 24055 | 1603.657 | 573.440 / 856.064 / 1376.256 | 572.380 | 11523.464 | 131/2/1 |
| postgresql | korda | tx-commit | 2430 | 161.856 | 3309.568 / 19267.584 / 28311.552 | 2587.524 | 67181.735 | 78/2/1 |
| postgresql | dapper | tx-commit | 13558 | 903.823 | 1044.480 / 1392.640 / 2179.072 | 709.431 | 13498.938 | 86/2/1 |

## Separate ABI diagnostics

These are independent instrumented processes. Only After−Before count deltas are used. Pending counts attempts, not unique operations or timer expirations; no diagnostic latency or allocation is credited.

| Provider | Case | Business ops | Generic starts | Mandatory starts | Conditional tx close | Retire calls | Pending | OK | Structure |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |

## Evidence boundaries

Numeric SQL is checked against the actual manifest and generated Dapper source, retaining the distinct placeholder spelling. Transaction receipts retain lifecycle descriptions, so matching business oracle results do not establish identical statement text. Each successful business operation passed the source-bound sticky oracle; an independent aggregate actual digest is not serialized.

Every requested directory and validation failure is retained below. JSON includes raw receipt/command/input hashes, source package commit metadata, owner drain, per-second business counts, RSS and ordinary cumulative CPU/allocation arithmetic. No long-run or host qualification is granted.

- `/workspace/scratch/4a65d70f0fe1/measurements/single-row-sqlite-01`: valid
- `/workspace/scratch/4a65d70f0fe1/measurements/single-row-postgresql-01`: valid
- `/workspace/scratch/4a65d70f0fe1/measurements/ffi-single-row-sqlite-01`: invalid_or_missing
  - `diagnostic-tx-rollback`: structure_mismatch; see structural mismatches in JSON
  - `diagnostic-tx-commit`: structure_mismatch; see structural mismatches in JSON
- `/workspace/scratch/4a65d70f0fe1/measurements/ffi-single-row-postgresql-01`: invalid_or_missing
  - `diagnostic-tx-rollback`: structure_mismatch; see structural mismatches in JSON
  - `diagnostic-tx-commit`: structure_mismatch; see structural mismatches in JSON

Pair comparisons: sqlite/numeric=missing_invalid_or_ambiguous, sqlite/tx-rollback=missing_invalid_or_ambiguous, sqlite/tx-commit=missing_invalid_or_ambiguous, postgresql/numeric=missing_invalid_or_ambiguous, postgresql/tx-rollback=missing_invalid_or_ambiguous, postgresql/tx-commit=missing_invalid_or_ambiguous
