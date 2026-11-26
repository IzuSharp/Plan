# Same-condition 120-second supplement

All four records passed the unchanged arithmetic/identity checks, all 35
business cases and zero failed operations. No final-duration credit is assigned.
Before is `f0078da720e07031bc56464995af6791c41aaae8`; current is public
`17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`. Rates/concurrency remain the selected
SQLite C4/R3000 and PostgreSQL C8/R3600, queue64, identical offered schedule.

| Provider / cohort | Completed | Completed/s through drain | Rejected | p50 / p95 / p99 scheduled latency, ms upper | Client CPU us/success | Process B/success | GC0/1/2 | Peak client RSS B |
| --- | ---: | ---: | ---: | --- | ---: | ---: | --- | ---: |
| SQLite before | 65213 | 542.872 | 294787 / 360000 | 118.489 / 213.910 / 276.824 | 2943.625 | 34006.138 | 808/162/3 | 47321088 |
| SQLite current | 320305 | 2668.577 | 39695 / 360000 | 21.103 / 34.341 / 50.856 | 1014.138 | 24845.945 | 2783/816/3 | 45891584 |
| PostgreSQL before | 149007 | 1241.453 | 282993 / 432000 | 52.953 / 100.663 / 133.693 | 1738.849 | 34856.686 | 1674/501/3 | 56135680 |
| PostgreSQL current | 415044 | 3458.224 | 16956 / 432000 | 13.763 / 25.297 / 34.341 | 829.188 | 25542.453 | 3496/1200/3 | 54632448 |

Latency includes planned-arrival scheduling and queue delay for successful
operations; rejected arrivals receive no fabricated latency. Offered fractions
and errors remain separate. Completed case populations differ after refusals;
raw per-case counts are retained. This pressure result is not a claim of maximum
capacity or identical completed sample populations.

CPU is actual client process cumulative endpoints during steady operations
through drain. PostgreSQL server raw PID/start-tick observations are separate;
no unavailable complete server/cgroup CPU total is inferred. Allocation and GC
are process-wide interval differences including business results and harness,
not framework-only bytes or entire-lifetime GC. Peak RSS is OS process-lifetime
highwater sampled after the interval. These supplemental plans have no idle
phase; final plans separately require 15 seconds after disposal.

All six legacy before owner counters drain to zero; missing newer
PullChannels/CommandCompletions remain null, not invented zero. Both current
records explicitly drain all eight owners to integer zero. The companion
JSON/Markdown arithmetic files preserve exact inputs, raw counters and limits.
