# Existing current-candidate FFI diagnostics — exact endpoint extraction

Candidate: `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`, tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc`. Read-only extraction date: 2026-11-26. No new measurement, build, test, profile or hash scan was performed. This summary records earlier observations and does not freshly verify executable bytes.

**These are six independent instrumented 15-second, C1, persistent-session observations. They carry no timing or allocation comparison credit.** Numeric is a 32-row query with a 32-row batch, not a single-row primary-key query. The transaction cases are whole business operations. They are neither the 1/100/1000-row phase suite nor the final 30-minute mixed runs.

All counts below are integer `After - Before` deltas. Setup/warmup and later `Drained - After` cleanup are excluded. The final table retains only the useful aggregate outcomes.

## Actual counts

| Provider | Case | Completed | FFI calls | FFI calls/completed | SQL dispatches | libpq submissions |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| sqlite | numeric | 77,192 | 1,003,496 | 13.000000 | 77,192 | 0 |
| sqlite | tx-rollback | 16,758 | 1,016,565 | 60.661475 | 117,306 | 0 |
| sqlite | tx-commit | 10,028 | 633,374 | 63.160550 | 80,224 | 0 |
| postgresql | numeric | 39,577 | 514,501 | 13.000000 | 39,577 | 158,308 |
| postgresql | tx-rollback | 8,414 | 527,650 | 62.710958 | 50,484 | 227,178 |
| postgresql | tx-commit | 6,067 | 390,541 | 64.371353 | 42,469 | 194,144 |

The raw outcomes record zero Failed, zero OracleFailures and all eight Drained owner counters zero for every observation. No ordinary timing metric is copied from these instrumented runs.

## Selected path calls

Each paired column below reports the count of **each** named function; request and take are separate invocations already included separately in the total FFI count.

| Provider | Case | Pull create | Pull request = take | Pull close request = take | Command request = take | Generic operation calls |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| sqlite | numeric | 77,192 | 154,384 | 77,192 | 0 | 0 |
| sqlite | tx-rollback | 50,274 | 50,274 | 50,274 | 52,491 | 0 |
| sqlite | tx-commit | 30,084 | 30,084 | 30,084 | 40,434 | 0 |
| postgresql | numeric | 39,577 | 79,154 | 39,577 | 0 | 0 |
| postgresql | tx-rollback | 25,242 | 25,242 | 25,242 | 29,804 | 0 |
| postgresql | tx-commit | 18,201 | 18,201 | 18,201 | 25,932 | 0 |

For these six observations, the request/take values shown as equal are equal in the raw endpoint deltas. Their status-returning request/take calls have one OK return per invocation and no Pending return. All `nw_db_operation_*`, `nw_db_close_create_v1`, command cancellation and command-error-take deltas are zero. Cold compile/Find-plan creation is outside the steady window; a zero steady factory count does not establish that no factory was ever called.

Numeric records two pull request/take pairs per completed 32-row operation. This is compatible with the exact batch-boundary EOF pull; it must not be reported as two SQL executions. Its measured SQL dispatch count is one per completed operation. Buffer-release invocations are also call counts, not a count of distinct non-null result batches.

For transactions, the number of command request/take invocations is an aggregate. The difference from the known mandatory command flow can be attributed to conditional child close only as a flow-derived inference, not an observed per-command-kind trace. This extraction does not manufacture such a trace.


See [counter semantics](../continuation-7/counter-semantics.md). These measurements
do not fill missing ordinary phase/long-run FFI or server-reply fields. Raw arrays,
command receipts and execution-machine paths are omitted from this document.
