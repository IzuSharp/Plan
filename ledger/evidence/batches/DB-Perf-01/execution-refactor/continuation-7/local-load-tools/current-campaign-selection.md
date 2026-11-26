# Current final campaign selection

Product: public `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`, tree
`bc9087d843d8d741d83d44f53d0b2c5af26dcffc`. The last isolated quiet-close
experiment failed its predeclared ordinary selection and does not change this
source or its independently built consumer identities.

## Measured closed-loop calibration

All 18 ordinary 15-second mixed observations cover the same 35 cases with zero
business errors and valid original arithmetic/identity checks. These are short
observations, not long-run acceptance. Candidate completed operations per second:

| Provider | C1 | C4 | C8 | Selected C |
| --- | ---: | ---: | ---: | ---: |
| SQLite | 1981.808 | 3161.926 | 3429.734 | 4 |
| PostgreSQL | 1135.587 | 3038.466 | 3992.521 | 8 |

SQLite C8 adds only 8.5% throughput over C4 while p99 rises from 10.748 to
25.821 ms. PostgreSQL C8 adds 31.4% over C4, with p99 rising from 6.521 to
12.976 ms; the additional throughput is material for this mixed pressure test.
Keep provider-specific concurrency identical across before/current/Dapper.

## Prospective offered validation

Run the fixed generator's 30-second offered plan at SQLite C4/R3000 and
PostgreSQL C8/R3600, queue capacity 64, batch/requested rows 32, 8 tenants and
1024 orders per tenant. Same SQL, parameters, persistent sessions, complete
results and assertions apply to each implementation. No parallel benchmark,
profiler, build or bulk archive process may overlap.

If the current candidate has zero business errors, complete owner drain and
at least 90% of the selected offered rate completed, retain that C/R for the
120-second before/current supplement and the final candidate/Dapper pair.
Otherwise record the result, lower only that provider's R to 80% of its observed
completed rate rounded down to a positive multiple of 100, and perform one
fresh 30-second validation. A second failure remains an explicit blocker; no
automatic unbounded search. Baseline refusals at the current rate are measured
capacity evidence and do not trigger lowering the current candidate's rate.

The source-bound final selector will exclude before from each 1800-second pair;
there are exactly four serial final cells. Every segment includes 15 seconds of
post-disposal idle observation. Freeze source/package/native/ELF/generated SQL
identities before creating either final output directory. No assumption of
exclusive hardware or observable cgroup quota is added.

## Offered observation and retained settings

Both candidate observations satisfy the prospective rule: SQLite completes
2820.323 operations/s (94.01% of R3000), PostgreSQL 3338.452/s (92.73% of R3600).
Both have zero failed operations and all eight owners zero. SQLite rejects
5335/90000 arrivals (5.93%); PostgreSQL rejects 7792/108000 (7.21%). These
refusals are explicit bounded-queue pressure results, not successful operations
and not erased by the successful command exits. Dapper rejects 70/90000 and
410/108000 respectively under the same offered settings. All six comparisons
pass the unchanged arithmetic input/contract checks and all 35 cases execute.

Retain SQLite C4/R3000 and PostgreSQL C8/R3600 for the separate 120-second
before/current supplement and four final cells. No additional rate retry is
selected. Offered p99 is scheduled-arrival-to-completion, includes scheduling
and queue delay, and does not assign a completion latency to rejected arrivals.
