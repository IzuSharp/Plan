# Separate short query-phase summary

This preserves completed short comparison results for before `f0078da720e07031bc56464995af6791c41aaae8`
and candidate `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`. It runs no new workload.
The [final report](final-report.md) includes the separate 120-second before/current
mixed comparison and the later four-cell long comparison; they are not pooled.

## Measurement boundaries

Phase values pool all three original windows (256 complete operations per window, 768 per route). Quantiles use nearest-rank observed durations without trimming or best-window selection. First-row time begins at submission/enumerator acquisition and includes first DTO mapping; construction is separate. `fourPhaseTotal` is the quantile of each sample's sum of four phases, not a sum of phase quantiles.

CPU and managed allocation are process-wide sums within the route windows. They include business results and verification/harness work. Route GC totals are sums of process-wide window deltas, not full process-lifetime GC counts. Preparation/first execution are separate and are not independently cold-process observations. Dapper cleanup can occur during ReadComplete. No phase-local or framework-only allocation is claimed.

The before package is `f0078da720e07031bc56464995af6791c41aaae8`; the current package is `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` in the phase contracts. Dapper uses the original recorded AOT executable and driver identities in each observation contract. The underlying report retains same-host, SQL-template, database-version and complete-result comparisons.

| Provider | Rows | Route | Four-phase total p50 µs | CPU µs/op | Total managed B/op |
| --- | --- | --- | ---: | ---: | ---: |
| SQLite | 1 row | candidate / fluent | 213.968 | 367.207 | 19,551.812 |
| SQLite | 1 row | candidate / prepared | 127.669 | 259.484 | 2,576.104 |
| SQLite | 1 row | candidate / host-sql | 169.442 | 314.827 | 8,117.323 |
| SQLite | 1 row | dapper / dapper-aot | 6.760 | 9.711 | 2,131.365 |
| SQLite | 100 rows | candidate / fluent | 404.242 | 729.797 | 26,687.010 |
| SQLite | 100 rows | candidate / prepared | 350.357 | 767.975 | 9,779.042 |
| SQLite | 100 rows | candidate / host-sql | 372.930 | 765.456 | 15,337.427 |
| SQLite | 100 rows | dapper / dapper-aot | 47.150 | 56.689 | 9,251.365 |
| SQLite | 1,000 rows | candidate / fluent | 2,012.454 | 3,859.861 | 97,478.083 |
| SQLite | 1,000 rows | candidate / prepared | 1,887.428 | 4,047.661 | 80,603.677 |
| SQLite | 1,000 rows | candidate / host-sql | 1,754.535 | 3,606.382 | 86,356.760 |
| SQLite | 1,000 rows | dapper / dapper-aot | 367.447 | 396.393 | 79,810.188 |
| PostgreSQL | 1 row | candidate / fluent | 370.621 | 380.536 | 19,546.260 |
| PostgreSQL | 1 row | candidate / prepared | 215.590 | 270.792 | 2,575.490 |
| PostgreSQL | 1 row | candidate / host-sql | 272.695 | 305.318 | 8,118.906 |
| PostgreSQL | 1 row | dapper / dapper-aot | 96.273 | 91.613 | 2,112.781 |
| PostgreSQL | 100 rows | candidate / fluent | 647.825 | 789.697 | 26,645.438 |
| PostgreSQL | 100 rows | candidate / prepared | 546.614 | 662.664 | 9,738.125 |
| PostgreSQL | 100 rows | candidate / host-sql | 581.621 | 747.105 | 15,316.167 |
| PostgreSQL | 100 rows | dapper / dapper-aot | 160.440 | 123.237 | 9,240.875 |
| PostgreSQL | 1,000 rows | candidate / fluent | 2,810.648 | 4,503.792 | 97,452.604 |
| PostgreSQL | 1,000 rows | candidate / prepared | 2,704.440 | 4,307.207 | 80,541.625 |
| PostgreSQL | 1,000 rows | candidate / host-sql | 2,634.807 | 4,308.611 | 86,273.604 |
| PostgreSQL | 1,000 rows | dapper / dapper-aot | 462.550 | 542.667 | 79,986.031 |

All three original 256-operation windows contribute to each route. These totals
include the workload and business results and cannot establish exclusive framework
allocation. The substantial prepared/Fluent versus Dapper gaps remain. Required
ownership and provider behavior constrain alternatives, but this table does not
attribute individual copies, queues or native calls. Detailed raw observations,
command/resource samples and recovery identities are not retained in this tree.
