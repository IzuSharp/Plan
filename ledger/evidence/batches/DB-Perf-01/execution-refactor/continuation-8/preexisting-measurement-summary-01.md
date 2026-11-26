# Preexisting measurement extraction: 17da versus before and Dapper.AOT

This report copies completed analysis values. It runs no workload or new acceptance gate and includes no ongoing or completed final 1,800-second result. JSON retains full precision, original report pointers and the original raw/command/resource/host hashes. Markdown numbers are rounded only for display.

## Source reports

| Key | Completed source report | SHA-256 | Bytes |
| --- | --- | --- | ---: |
| phase | `/workspace/scratch/fd78534029f7/measurements/phase-analysis-01.json` | `4cf173c561ecbac7726132fafc24ea1059b6969eabe1d7a18efb3111884426b2` | 723482 |
| baseline | `/workspace/scratch/fd78534029f7/measurements/baseline-analysis-01.json` | `b15f32997b27ea70b6f1af2687aa18f4c0134defb84f2a44ce1616eb6b174feb` | 412585 |

Only these two report files were hashed for this extraction. Underlying raw and resource hashes are copied from their previously computed analysis identities; this is not a new raw-evidence revalidation.

## Measurement boundaries

Phase values pool all three original windows (256 complete operations per window, 768 per route). Quantiles use nearest-rank observed durations without trimming or best-window selection. First-row time begins at submission/enumerator acquisition and includes first DTO mapping; construction is separate. `fourPhaseTotal` is the quantile of each sample's sum of four phases, not a sum of phase quantiles.

CPU and managed allocation are process-wide sums within the route windows. They include business results and verification/harness work. Route GC totals are sums of process-wide window deltas, not full process-lifetime GC counts. Preparation/first execution are separate and are not independently cold-process observations. Dapper cleanup can occur during ReadComplete. No phase-local or framework-only allocation is claimed.

The before package is `f0078da720e07031bc56464995af6791c41aaae8`; the current package is `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` in the phase contracts. Dapper uses the original recorded AOT executable and driver identities in each observation contract. The underlying report retains same-host, SQL-template, database-version and complete-result comparisons.

## SQLite query phases

### 1 row

| Cohort / route | First row p50 / p95 / p99 (µs) | Four-phase total p50 / p95 / p99 (µs) | CPU µs/op | Total managed B/op | GC0/1/2 across windows | Source pointer |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| before / fluent | 202.961 / 12,015.211 / 16,925.101 | 534.225 / 20,091.361 / 26,507.822 | 832.125 | 22,430.229 | 7/1/0 | `phase:/observations/0/metrics/routes/0` |
| before / prepared | 201.090 / 12,107.318 / 12,411.465 | 556.918 / 20,240.053 / 20,631.271 | 701.117 | 6,032.115 | 1/0/0 | `phase:/observations/0/metrics/routes/1` |
| before / host-sql | 184.249 / 11,798.724 / 12,314.301 | 361.999 / 19,921.103 / 21,158.058 | 614.823 | 10,903.667 | 5/0/0 | `phase:/observations/0/metrics/routes/2` |
| candidate / fluent | 75.723 / 128.161 / 203.603 | 213.968 / 320.888 / 534.100 | 367.207 | 19,551.812 | 5/1/0 | `phase:/observations/3/metrics/routes/0` |
| candidate / prepared | 67.160 / 109.133 / 153.439 | 127.669 / 192.852 / 244.414 | 259.484 | 2,576.104 | 2/0/0 | `phase:/observations/3/metrics/routes/1` |
| candidate / host-sql | 76.589 / 121.992 / 207.860 | 169.442 / 238.966 / 356.265 | 314.827 | 8,117.323 | 3/0/0 | `phase:/observations/3/metrics/routes/2` |
| dapper / dapper-aot | 5.679 / 10.456 / 30.646 | 6.760 / 11.948 / 32.108 | 9.711 | 2,131.365 | 1/0/0 | `phase:/observations/6/metrics/routes/0` |

### 100 rows

| Cohort / route | First row p50 / p95 / p99 (µs) | Four-phase total p50 / p95 / p99 (µs) | CPU µs/op | Total managed B/op | GC0/1/2 across windows | Source pointer |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| before / fluent | 242.070 / 11,596.444 / 19,906.881 | 3,671.113 / 27,449.785 / 38,657.584 | 1,333.966 | 31,032.479 | 12/0/0 | `phase:/observations/1/metrics/routes/0` |
| before / prepared | 259.732 / 12,017.857 / 17,238.832 | 8,324.360 / 28,618.505 / 36,765.024 | 1,338.391 | 14,709.917 | 5/0/0 | `phase:/observations/1/metrics/routes/1` |
| before / host-sql | 232.285 / 11,215.853 / 19,982.844 | 932.608 / 28,490.564 / 32,669.295 | 1,165.626 | 19,579.896 | 7/1/0 | `phase:/observations/1/metrics/routes/2` |
| candidate / fluent | 103.814 / 173.338 / 320.287 | 404.242 / 606.488 / 942.052 | 729.797 | 26,687.010 | 8/0/0 | `phase:/observations/4/metrics/routes/0` |
| candidate / prepared | 107.440 / 214.840 / 469.168 | 350.357 / 632.121 / 1,760.757 | 767.975 | 9,779.042 | 4/0/0 | `phase:/observations/4/metrics/routes/1` |
| candidate / host-sql | 113.209 / 239.076 / 449.058 | 372.930 / 736.177 / 1,229.601 | 765.456 | 15,337.427 | 6/1/0 | `phase:/observations/4/metrics/routes/2` |
| dapper / dapper-aot | 10.746 / 18.627 / 49.363 | 47.150 / 91.185 / 164.175 | 56.689 | 9,251.365 | 3/0/0 | `phase:/observations/7/metrics/routes/0` |

### 1,000 rows

| Cohort / route | First row p50 / p95 / p99 (µs) | Four-phase total p50 / p95 / p99 (µs) | CPU µs/op | Total managed B/op | GC0/1/2 across windows | Source pointer |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| before / fluent | 301.769 / 10,058.025 / 19,311.471 | 31,777.672 / 112,796.440 / 159,560.294 | 6,363.013 | 116,120.250 | 40/5/0 | `phase:/observations/2/metrics/routes/0` |
| before / prepared | 331.033 / 10,257.736 / 12,528.701 | 50,129.461 / 120,187.367 / 161,031.206 | 6,689.332 | 99,821.833 | 39/3/0 | `phase:/observations/2/metrics/routes/1` |
| before / host-sql | 319.215 / 11,111.920 / 19,659.197 | 47,775.305 / 118,806.735 / 150,235.164 | 6,874.401 | 104,924.958 | 39/4/1 | `phase:/observations/2/metrics/routes/2` |
| candidate / fluent | 117.695 / 227.332 / 367.898 | 2,012.454 / 3,057.721 / 4,051.628 | 3,859.861 | 97,478.083 | 34/0/0 | `phase:/observations/5/metrics/routes/0` |
| candidate / prepared | 117.444 / 185.551 / 624.539 | 1,887.428 / 2,888.233 / 5,252.390 | 4,047.661 | 80,603.677 | 28/0/0 | `phase:/observations/5/metrics/routes/1` |
| candidate / host-sql | 111.246 / 179.142 / 304.883 | 1,754.535 / 2,418.599 / 2,922.448 | 3,606.382 | 86,356.760 | 33/1/0 | `phase:/observations/5/metrics/routes/2` |
| dapper / dapper-aot | 13.760 / 29.544 / 101.731 | 367.447 / 535.406 / 665.901 | 396.393 | 79,810.188 | 29/1/0 | `phase:/observations/8/metrics/routes/0` |

## PostgreSQL query phases

### 1 row

| Cohort / route | First row p50 / p95 / p99 (µs) | Four-phase total p50 / p95 / p99 (µs) | CPU µs/op | Total managed B/op | GC0/1/2 across windows | Source pointer |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| before / fluent | 397.601 / 11,969.741 / 20,180.953 | 629.797 / 19,547.415 / 20,815.011 | 710.915 | 22,428.292 | 7/1/0 | `phase:/observations/9/metrics/routes/0` |
| before / prepared | 289.130 / 7,335.088 / 12,537.165 | 379.244 / 12,206.744 / 20,428.150 | 482.301 | 5,989.292 | 3/0/0 | `phase:/observations/9/metrics/routes/1` |
| before / host-sql | 310.461 / 606.191 / 11,257.176 | 424.131 / 8,142.589 / 12,585.592 | 437.508 | 10,874.177 | 4/0/0 | `phase:/observations/9/metrics/routes/2` |
| candidate / fluent | 228.470 / 320.637 / 428.598 | 370.621 / 504.350 / 968.304 | 380.536 | 19,546.260 | 5/1/0 | `phase:/observations/12/metrics/routes/0` |
| candidate / prepared | 155.962 / 250.302 / 371.803 | 215.590 / 323.216 / 469.464 | 270.792 | 2,575.490 | 2/0/0 | `phase:/observations/12/metrics/routes/1` |
| candidate / host-sql | 188.480 / 276.190 / 348.874 | 272.695 / 381.457 / 458.963 | 305.318 | 8,118.906 | 3/0/0 | `phase:/observations/12/metrics/routes/2` |
| dapper / dapper-aot | 95.602 / 160.178 / 272.676 | 96.273 / 164.275 / 274.779 | 91.613 | 2,112.781 | 1/0/0 | `phase:/observations/15/metrics/routes/0` |

### 100 rows

| Cohort / route | First row p50 / p95 / p99 (µs) | Four-phase total p50 / p95 / p99 (µs) | CPU µs/op | Total managed B/op | GC0/1/2 across windows | Source pointer |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| before / fluent | 429.182 / 1,167.696 / 8,844.918 | 858.805 / 8,985.008 / 18,790.365 | 862.242 | 30,990.646 | 11/1/0 | `phase:/observations/10/metrics/routes/0` |
| before / prepared | 392.484 / 3,918.593 / 12,498.207 | 746.447 / 13,416.488 / 26,518.009 | 855.395 | 14,667.333 | 5/0/0 | `phase:/observations/10/metrics/routes/1` |
| before / host-sql | 449.379 / 6,899.959 / 12,386.502 | 863.466 / 18,363.329 / 27,083.217 | 993.190 | 19,564.375 | 7/0/0 | `phase:/observations/10/metrics/routes/2` |
| candidate / fluent | 303.121 / 413.586 / 517.110 | 647.825 / 870.486 / 1,179.411 | 789.697 | 26,645.438 | 8/0/0 | `phase:/observations/13/metrics/routes/0` |
| candidate / prepared | 304.283 / 407.937 / 563.939 | 546.614 / 717.298 / 1,165.055 | 662.664 | 9,738.125 | 4/0/0 | `phase:/observations/13/metrics/routes/1` |
| candidate / host-sql | 306.136 / 420.445 / 654.284 | 581.621 / 786.020 / 1,402.923 | 747.105 | 15,316.167 | 6/1/0 | `phase:/observations/13/metrics/routes/2` |
| dapper / dapper-aot | 142.914 / 226.088 / 347.380 | 160.440 / 258.757 / 373.259 | 123.237 | 9,240.875 | 2/1/0 | `phase:/observations/16/metrics/routes/0` |

### 1,000 rows

| Cohort / route | First row p50 / p95 / p99 (µs) | Four-phase total p50 / p95 / p99 (µs) | CPU µs/op | Total managed B/op | GC0/1/2 across windows | Source pointer |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| before / fluent | 742.066 / 10,568.298 / 19,052.444 | 28,003.131 / 90,162.639 / 110,514.656 | 6,293.465 | 116,142.323 | 43/2/0 | `phase:/observations/11/metrics/routes/0` |
| before / prepared | 697.845 / 10,477.503 / 18,397.889 | 13,301.054 / 90,509.797 / 117,282.660 | 5,922.789 | 99,802.427 | 37/3/0 | `phase:/observations/11/metrics/routes/1` |
| before / host-sql | 654.015 / 10,352.331 / 18,336.326 | 10,631.356 / 99,610.584 / 128,411.842 | 5,702.533 | 104,909.562 | 39/2/0 | `phase:/observations/11/metrics/routes/2` |
| candidate / fluent | 375.157 / 630.658 / 1,761.849 | 2,810.648 / 3,914.760 / 6,913.572 | 4,503.792 | 97,452.604 | 36/0/0 | `phase:/observations/14/metrics/routes/0` |
| candidate / prepared | 368.015 / 583.738 / 1,009.681 | 2,704.440 / 3,777.841 / 4,996.182 | 4,307.207 | 80,541.625 | 30/0/0 | `phase:/observations/14/metrics/routes/1` |
| candidate / host-sql | 356.848 / 536.818 / 1,174.492 | 2,634.807 / 3,730.626 / 8,826.037 | 4,308.611 | 86,273.604 | 31/0/0 | `phase:/observations/14/metrics/routes/2` |
| dapper / dapper-aot | 220.429 / 322.942 / 1,556.031 | 462.550 / 857.309 / 2,445.780 | 542.667 | 79,986.031 | 28/1/0 | `phase:/observations/17/metrics/routes/0` |

## Completed 120-second before/current mixed load

SQLite uses C4/R3000; PostgreSQL uses C8/R3600. Both keep queue 64, prepared mode, persistent sessions, requested/batch rows 32, 8 tenants × 1,024 orders, all 35 cases and 64 warmup operations per worker. The existing comparison records matching before/current business contracts, diagnostic SQL and settings. All four observations have zero business failures; refusals remain separate.

Throughput covers offered start through drain. Histogram values below are upper bounds. Scheduled-to-completion includes scheduling and queue delay; start-delay is planned-arrival-to-worker-start and is not a pure queue-time measurement. Rejected arrivals receive no invented completion latency.

| Observation | Succeeded / failed / rejected | Successful op/s through drain | CPU user / system s | CPU µs/success | Total managed B/success | GC0/1/2 in steady/drain | Source pointer |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| sqlite-baseline-01/before-c4 | 65,213 / 0 / 294,787 | 542.872 | 177.745 / 14.217 | 2,943.625 | 34,006.138 | 808/162/3 | `baseline:/observations/0` |
| sqlite-baseline-01/candidate-c4 | 320,305 / 0 / 39,695 | 2,668.577 | 270.317 / 54.516 | 1,014.138 | 24,845.945 | 2783/816/3 | `baseline:/observations/1` |
| postgresql-baseline-01/before-c8 | 149,007 / 0 / 282,993 | 1,241.453 | 211.682 / 47.419 | 1,738.849 | 34,856.686 | 1674/501/3 | `baseline:/observations/2` |
| postgresql-baseline-01/candidate-c8 | 415,044 / 0 / 16,956 | 3,458.224 | 261.290 / 82.859 | 829.188 | 25,542.453 | 3496/1200/3 | `baseline:/observations/3` |

| Observation | Population / boundary | Samples | p50 / p95 / p99 upper (µs) | Source pointer |
| --- | --- | ---: | ---: | --- |
| sqlite-baseline-01/before-c4 | offered | 65,213 | 118,489.088 / 213,909.504 / 276,824.064 | `baseline:/observations/0/metrics/measurement/histograms/offered` |
| sqlite-baseline-01/before-c4 | service | 65,213 | 1,376.256 / 28,573.696 / 82,313.216 | `baseline:/observations/0/metrics/measurement/histograms/service` |
| sqlite-baseline-01/before-c4 | all_terminal_offered | 65,213 | 118,489.088 / 213,909.504 / 276,824.064 | `baseline:/observations/0/metrics/measurement/histograms/all_terminal_offered` |
| sqlite-baseline-01/before-c4 | start_delay | 65,213 | 110,624.768 / 201,326.592 / 258,998.272 | `baseline:/observations/0/metrics/measurement/histograms/start_delay` |
| sqlite-baseline-01/candidate-c4 | offered | 320,305 | 21,102.592 / 34,340.864 / 50,855.936 | `baseline:/observations/1/metrics/measurement/histograms/offered` |
| sqlite-baseline-01/candidate-c4 | service | 320,305 | 548.864 / 5,013.504 / 13,238.272 | `baseline:/observations/1/metrics/measurement/histograms/service` |
| sqlite-baseline-01/candidate-c4 | all_terminal_offered | 320,305 | 21,102.592 / 34,340.864 / 50,855.936 | `baseline:/observations/1/metrics/measurement/histograms/all_terminal_offered` |
| sqlite-baseline-01/candidate-c4 | start_delay | 320,305 | 20,054.016 / 31,588.352 / 44,040.192 | `baseline:/observations/1/metrics/measurement/histograms/start_delay` |
| postgresql-baseline-01/before-c8 | offered | 149,007 | 52,953.088 / 100,663.296 / 133,693.440 | `baseline:/observations/2/metrics/measurement/histograms/offered` |
| postgresql-baseline-01/before-c8 | service | 149,007 | 2,441.216 / 24,903.680 / 48,234.496 | `baseline:/observations/2/metrics/measurement/histograms/service` |
| postgresql-baseline-01/before-c8 | all_terminal_offered | 149,007 | 52,953.088 / 100,663.296 / 133,693.440 | `baseline:/observations/2/metrics/measurement/histograms/all_terminal_offered` |
| postgresql-baseline-01/before-c8 | start_delay | 149,007 | 47,448.064 / 89,128.960 / 117,964.800 | `baseline:/observations/2/metrics/measurement/histograms/start_delay` |
| postgresql-baseline-01/candidate-c8 | offered | 415,044 | 13,762.560 / 25,296.896 / 34,340.864 | `baseline:/observations/3/metrics/measurement/histograms/offered` |
| postgresql-baseline-01/candidate-c8 | service | 415,044 | 897.024 / 10,158.080 / 15,859.712 | `baseline:/observations/3/metrics/measurement/histograms/service` |
| postgresql-baseline-01/candidate-c8 | all_terminal_offered | 415,044 | 13,762.560 / 25,296.896 / 34,340.864 | `baseline:/observations/3/metrics/measurement/histograms/all_terminal_offered` |
| postgresql-baseline-01/candidate-c8 | start_delay | 415,044 | 11,796.480 / 20,840.448 / 28,442.624 | `baseline:/observations/3/metrics/measurement/histograms/start_delay` |

| Observation | Planned / attempted | Actual attempted rate | Offered / through-drain seconds | Process-lifetime peak RSS B | Idle RSS |
| --- | ---: | ---: | ---: | ---: | --- |
| sqlite-baseline-01/before-c4 | 360,000 / 360,000 | 3,000.000 | 120.000 / 120.126 | 47,321,088 | not recorded |
| sqlite-baseline-01/candidate-c4 | 360,000 / 360,000 | 3,000.000 | 120.000 / 120.028 | 45,891,584 | not recorded |
| postgresql-baseline-01/before-c8 | 432,000 / 432,000 | 3,600.000 | 120.000 / 120.026 | 56,135,680 | not recorded |
| postgresql-baseline-01/candidate-c8 | 432,000 / 432,000 | 3,600.000 | 120.000 / 120.017 | 54,632,448 | not recorded |

Managed allocation is total business/harness/framework/driver cost; `framework_only_bytes=null`. Mixed-load CPU/allocation endpoints bracket steady work through drain. Its GC values are process-wide deltas over that interval, not full process-lifetime collections including setup and warmup. The JSON preserves wait4 process-lifetime CPU/maxRSS separately. These short observations have no post-idle RSS and cannot supply final long-run credit.

## Provenance and interpretation

The JSON `phaseObservations[*].sourcePointers` and `baselineObservations[*].sourcePointers` map each extracted value to an exact pointer in the report identified above. Route pointers append `/phases/SubmitToFirstRowTicks`, `/fourPhaseTotal`, `/processCpuMicrosecondsPerOperation` and `/bytesPerOperation` as shown in each route's map. Original receipt, command, runner, plan, resource and host identities are retained with their stored and content SHA-256 values.

All 18 phase observations were already marked `observed` with timing credit by the source report. This extraction does not upgrade that status, rerun assertions or validate final acceptance. It copies every route, including regressions and slower candidate/Dapper comparisons. Existing pairwise comparison evidence and raw ratios are included in JSON without selecting a best route or trial.

Recorded host identity comes from the original index-bound host records (node `89394ab90f06`, x86_64, Linux `6.18.57`). This does not establish exclusive hardware or invisible cgroup quota. Phase SQL templates and Korda rendered SQL are checked in the source comparisons; Dapper provider marker rewriting is not relabeled as byte-identical server wire SQL.
