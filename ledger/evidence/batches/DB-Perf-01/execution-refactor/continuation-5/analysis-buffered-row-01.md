# Buffered public-terminal A/B

Validation: **passed**.

All explicitly supplied attempts are listed. No first-row latency is observable. Submit-to-list includes complete result creation and cursor retirement; release covers later explicit query disposal.

CPU, allocation and GC are whole-process window observations, including result validation and business/harness allocations. No business subtraction, framework-only allocation claim, retry selection or long-run acceptance is made.

- `/workspace/scratch/4a65d70f0fe1/measurements/buffered-row-sqlite-01`: passed
- `/workspace/scratch/4a65d70f0fe1/measurements/buffered-row-postgresql-01`: passed

## sqlite

All entries are before → candidate; time is microseconds.

| Rows | Route | List p50/p95/p99 before | List p50/p95/p99 candidate | CPU/op | B/op | GC 0/1/2 |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fluent | 178.686/295.634/448.278 | 175.421/338.554/1392.091 | 334.587 → 393.595 | 19896.417 → 19903.917 | 6/1/0 → 6/1/0 |
| 1 | prepared | 110.755/201.115/273.261 | 110.154/202.661/374.057 | 208.945 → 239.100 | 2901.312 → 2920.302 | 1/0/0 → 1/0/0 |
| 1 | host-sql | 128.662/220.272/286.086 | 146.755/249.010/581.455 | 243.967 → 310.882 | 8461.792 → 8467.312 | 3/0/0 → 3/0/0 |
| 100 | fluent | 342.330/473.275/819.024 | 350.642/526.404/1388.592 | 687.845 → 697.126 | 27817.000 → 27799.688 | 9/1/0 → 9/1/0 |
| 100 | prepared | 281.339/403.881/632.477 | 282.660/564.139/1013.469 | 576.988 → 581.208 | 10886.958 → 10883.240 | 4/0/0 → 4/0/0 |
| 100 | host-sql | 295.199/454.426/678.054 | 335.249/774.848/1778.807 | 563.723 → 763.326 | 16438.990 → 16483.115 | 6/0/0 → 7/0/0 |
| 1000 | fluent | 1788.853/2460.711/5968.032 | 1821.951/2386.956/2953.735 | 3701.490 → 3872.697 | 105864.052 → 105875.802 | 40/0/0 → 39/0/0 |
| 1000 | prepared | 1761.126/2574.442/4172.650 | 1766.248/2382.004/3474.309 | 3783.089 → 3718.742 | 88960.240 → 88956.083 | 33/0/0 → 33/0/0 |
| 1000 | host-sql | 1924.554/2633.830/3092.457 | 1877.017/2572.727/4045.890 | 4005.434 → 3884.904 | 94720.979 → 94721.542 | 34/0/0 → 35/0/0 |

## postgresql

All entries are before → candidate; time is microseconds.

| Rows | Route | List p50/p95/p99 before | List p50/p95/p99 candidate | CPU/op | B/op | GC 0/1/2 |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 1 | fluent | 313.837/452.167/662.330 | 332.946/453.991/789.314 | 378.241 → 376.574 | 19896.292 → 19891.323 | 6/0/0 → 6/0/0 |
| 1 | prepared | 194.434/279.706/411.843 | 218.074/347.566/572.206 | 266.757 → 263.773 | 2895.688 → 2893.135 | 1/0/0 → 1/0/0 |
| 1 | host-sql | 222.181/311.419/404.027 | 253.467/364.207/442.208 | 298.940 → 304.206 | 8454.833 → 8456.792 | 3/0/0 → 3/0/0 |
| 100 | fluent | 592.129/842.675/2220.695 | 627.321/842.830/1581.602 | 784.759 → 789.941 | 27785.677 → 27787.146 | 10/0/0 → 10/0/0 |
| 100 | prepared | 528.484/676.339/1028.537 | 543.651/818.595/1610.560 | 644.155 → 695.659 | 10868.885 → 10880.010 | 4/0/0 → 4/0/0 |
| 100 | host-sql | 547.683/690.645/1002.888 | 594.172/893.621/2222.588 | 698.734 → 717.842 | 16452.865 → 16435.135 | 6/1/0 → 6/1/0 |
| 1000 | fluent | 2577.941/3446.007/5834.955 | 2434.916/3241.670/5420.967 | 4605.531 → 4138.986 | 105821.042 → 105812.823 | 37/0/0 → 39/0/0 |
| 1000 | prepared | 2717.533/3462.725/6130.919 | 2465.859/3236.910/4195.328 | 4493.008 → 4219.307 | 88925.260 → 88901.510 | 34/0/0 → 32/0/0 |
| 1000 | host-sql | 2496.859/3152.385/4634.234 | 2470.504/3266.617/4868.344 | 4427.383 → 4347.432 | 94694.719 → 94689.344 | 36/0/0 → 36/0/0 |

The JSON retains every phase p50/p95/p99, untrimmed three-phase totals, raw summed CPU/allocation/GC counters, throughput including validation, RSS, SQL/protocol counts and all verified file identities.
