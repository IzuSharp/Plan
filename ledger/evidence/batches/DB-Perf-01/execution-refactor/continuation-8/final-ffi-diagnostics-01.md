# Existing current-candidate FFI diagnostics — exact endpoint extraction

Candidate: `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`, tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc`. Read-only extraction date: 2026-11-26. No new measurement, build, test, profile or hash scan was performed. Recorded identity values below are copied from the existing receipts; this extraction does not freshly verify the artifact bytes.

**These are six independent instrumented 15-second, C1, persistent-session observations. They carry no timing or allocation comparison credit.** Numeric is a 32-row query with a 32-row batch, not a single-row primary-key query. The transaction cases are whole business operations. They are neither the 1/100/1000-row phase suite nor the final 30-minute mixed runs.

All counts below are integer `After - Before` deltas. Setup/warmup and later `Drained - After` cleanup are excluded. The JSON companion retains all 60 symbol names, exact before/after/delta Calls/Pending/OK values, original counter snapshots, actual durations, identities and poll counts.

## Actual counts

| Provider | Case | Completed | FFI calls | FFI calls/completed | SQL dispatches | libpq submissions |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| sqlite | numeric | 77,192 | 1,003,496 | 13.000000 | 77,192 | 0 |
| sqlite | tx-rollback | 16,758 | 1,016,565 | 60.661475 | 117,306 | 0 |
| sqlite | tx-commit | 10,028 | 633,374 | 63.160550 | 80,224 | 0 |
| postgresql | numeric | 39,577 | 514,501 | 13.000000 | 39,577 | 158,308 |
| postgresql | tx-rollback | 8,414 | 527,650 | 62.710958 | 50,484 | 227,178 |
| postgresql | tx-commit | 6,067 | 390,541 | 64.371353 | 42,469 | 194,144 |

The raw outcomes record zero Failed, zero OracleFailures and all eight Drained owner counters zero for every observation. Source/consumer identities and the original command outcome fields are retained in the companion; no ordinary timing metric is copied from these instrumented runs.

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

## Identity and original paths

| Provider | Raw directory | Diagnostic build receipt | ABI source commit |
| --- | --- | --- | --- |
| sqlite | `/workspace/scratch/fd78534029f7/measurements/sqlite-single-diagnostic-01` | `/tmp/DB-Exec-10-diag-sqlite-ffi-01/diagnostic-build.json` | `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` |
| postgresql | `/workspace/scratch/fd78534029f7/measurements/postgresql-single-diagnostic-01` | `/tmp/DB-Exec-10-diag-postgresql-ffi-01/diagnostic-build.json` | `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` |

Each raw directory contains `diagnostic-numeric.json`, `diagnostic-tx-rollback.json` and `diagnostic-tx-commit.json`, together with their `.command.json` records and frozen `plan.json`. Both diagnostic build receipts identify the corresponding `builds/candidate-{provider}-02/consumer-workload` source consumer and recorded package/native identities. Actual executed diagnostic ELFs differ from their ordinary source consumers and remain labelled instrumented.

## Unavailable quantities and separate evidence

Ordinary phase/mixed raw records contain `SqlExecutions` and `ProtocolSubmissions` endpoints, but no FFI arrays and no counts of required protocol replies. These separate single-case FFI measurements therefore fill a current-candidate diagnostic scope; they do not fill those missing metrics for the ordinary phase suite or long mixed workload. Dapper ordinary consumers do not expose corresponding internal FFI/SQL/reply counters.

The real PostgreSQL proxy correctness tests have actual protocol-group and forwarded ReadyForQuery observations. They are separate narrow windows with their own source/receipt identities; the proxy does not count every ParseComplete, BindComplete, DataRow or CommandComplete. A source-derived call map or pull-count assertion is not a workload runtime trace. Successful libpq submissions, poll calls, Pending returns, readiness notifications, protocol replies and physical RTT are different quantities.

Historical `ffi-single-command-{provider}-01` observations under `/workspace/scratch/4a65d70f0fe1/measurements` remain bound to `8789a45a52cc0cc0a0b62737542d9c120b753c9b`; they are not these six current-candidate records. Their counts need not be reused to describe 17da.

Companion: `final-ffi-diagnostics-01.json`. Source semantics reference: `continuation-7/counter-semantics.md`. The final archive should retain this extraction beside the originals and source-bound evidence, without interpreting it as a new run.
