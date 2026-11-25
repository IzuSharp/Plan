# Immediate-before local short observations

This is the newly rebuilt `f0078da720e07031bc56464995af6791c41aaae8` implementation on the current Linux x64 host. It is not a recovered executable and it is not the historical final run. The reference is the actual restored Dapper.AOT 1.1.0 consumer described in [build-recovery.json](../build-recovery.json).

Both providers completed all 13 serial commands with exit 0 and no observer errors. All mixed cells report zero failures and zero oracle failures. Builds and other benchmarks were paused throughout this measurement window. Client affinity was CPUs 0–5, PostgreSQL CPUs 6–8, and `DOTNET_PROCESSOR_COUNT=4`. The observer retains the restricted host/cgroup visibility; no exclusive-host claim is made.

## Closed-loop calibration

Each point is one five-second run, 35 warmup operations per worker, persistent session, prepared mode, 35-case mixed workload, requested rows 32 and batch rows 32. C1 additionally executes the full `--verify` suite. These short points select the next experiment; they do not establish final performance or an external arrival/rejection rate.

| Database | Concurrency | Before ops/s | Dapper.AOT ops/s | Before p99 ms | Dapper p99 ms | Before managed B/op | Dapper B/op |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| sqlite | 1 | 123.3 | 5685.1 | 39.846 | 0.967 | 32864.9 | 7082.2 |
| sqlite | 4 | 393.8 | 13023.2 | 91.750 | 2.146 | 33470.7 | 7081.7 |
| sqlite | 8 | 555.8 | 13804.6 | 141.558 | 3.424 | 33460.6 | 7080.7 |
| sqlite | 16 | 622.1 | 12874.4 | 641.729 | 3.703 | 33452.1 | 7079.7 |
| postgresql | 1 | 111.2 | 2330.2 | 52.953 | 1.606 | 33799.4 | 6598.9 |
| postgresql | 4 | 500.7 | 6743.6 | 48.759 | 2.998 | 33427.6 | 6591.6 |
| postgresql | 8 | 929.2 | 6679.3 | 63.963 | 8.782 | 33290.4 | 6577.0 |
| postgresql | 16 | 1372.6 | 7557.6 | 137.363 | 21.758 | 33457.2 | 6585.2 |

The larger C16 tail in Korda and the lack of consistent Dapper throughput growth beyond C8 support checking C8 first for the candidate. Final concurrency and offered rate are not frozen by this table. Offered-rate calibration is still required.

All B/op values are observed whole-process totals, including business results and harness state. Generation 0/1/2 counts, CPU endpoints, histograms, exact executable/native hashes and raw filenames are in [summary.json](summary.json). Closed-loop rejected-arrival counts are explicitly unavailable rather than synthesized as zero.

## Single row and DTO phases

The same public package consumer runs ordinary Fluent, warmed `.Prepare()`, and full parameterized SQL for 1, 100 and 1,000 two-column DTOs. Each lane has 64 warmups and three rotated windows of 16 measured operations. SQL, two Int64 parameters, full-list consumption and expected DTO/null values match; SQLite anonymous versus numbered parameter marker spelling remains disclosed. See [phase-summary.json](phase-summary.json) and the original provider phase receipts.

First-row medians are mostly below one millisecond while 1,000-row completion medians reach tens of milliseconds. This points to later batch construction, wakeup, retirement and repeated-fetch costs as hypotheses requiring candidate measurements, not yet measured causal attribution.

## Resource probe and retained failures

The resource probe holds the source open during its one-second idle observation and checks concurrent ownership, admission exhaustion, cancellation and final owner settlement. Both probes passed. Its idle CPU scope differs from the mixed harness `--idle-seconds`, which observes after worker/source closure.

The initial phase harness used `Take(rows)`, unintentionally adding a third parameter to the supposedly two-parameter raw route; it failed for SQLite 100 rows. The corrected v2 harness uses the typed primary-key/range predicate and passed 1/100/1,000 rows on both providers. That harness failure, package-build recovery failures and historical unexplained aborts remain recorded; no old unexplained failure is declared fixed by these passes.

No candidate long-run cell has been completed at this checkpoint.
