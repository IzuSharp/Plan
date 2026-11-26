# Bounded retirement scheduling experiments

These are local decision experiments, not final acceptance. The formal B package input remains a27ff318 (public tree-identical c2df05ff). Candidate C1 is 81a9fd6a50c7cf2ec0d5c1052a07aba0d535dd94: one separately queued retry after actual native Pending plus scanning only the occupied coordinator-slot prefix. R4 is fdf1cb12822792094d6ba9bc96c61732293ee9d7: at most four separately queued retries, with the same occupied-slot scan. Neither releases native ownership or publishes the private result before real native quiet. Both fall back to the existing 10 ms timer after exhausting prompt retries.

`source-identities.json` binds each local commit/tree to its complete patch from B. These experiment commits are local, not invented public GitHub commit links. The source patches, independent package consumer receipts, actual loaded native hashes, original run plans and raw observer/consumer records are retained. Their native producer inputs are unchanged from B.

## Runs and selection

The B/C1 run completed 46 commands (23 per provider); C1/R4 completed 50 (25 per provider). Every command exited zero and every consumer's result/owner oracle passed. Runs were serial, with task-owned build/test activity paused and clients pinned to CPUs 0–5; PostgreSQL used CPUs 6–8. The observer retains host/cgroup visibility limits. The measurement duration is five seconds per mixed process, so case-cycle composition and small samples limit allocation and tail comparisons.

Each table cell is the median of three separate mixed C8 processes. It is not a confidence interval or a pooled long run. p99 is the original histogram's upper bound.

| Campaign | Candidate | ops/s | Process CPU µs/op | p99 upper ms |
| --- | --- | ---: | ---: | ---: |
| paired-c-sqlite | candidate-b | 687.6 | 1054.1 | 145.75 |
| paired-c-sqlite | candidate-c | 768.7 | 966.4 | 121.11 |
| paired-c-postgresql | candidate-b | 1094.3 | 917.7 | 50.59 |
| paired-c-postgresql | candidate-c | 1275.9 | 936.4 | 42.21 |
| paired-r4-sqlite | candidate-c | 699.8 | 950.9 | 168.82 |
| paired-r4-sqlite | candidate-r4 | 880.0 | 993.7 | 119.54 |
| paired-r4-postgresql | candidate-c | 1287.7 | 919.7 | 47.19 |
| paired-r4-postgresql | candidate-r4 | 1523.4 | 925.1 | 36.44 |

C1/R4 also repeat the 1000-row phase in three fresh processes, reversing order in the middle repeat. For prepared SQLite the C1 read-complete p50s are 50.35, 67.98 and 78.93 ms; R4 is 50.37, 57.31 and 84.11 ms. PostgreSQL C1 is 38.52, 38.87 and 19.52 ms; R4 is 24.15, 26.11 and 44.13 ms. R4 improves most mixed observations but does not consistently eliminate large-result waits. It is not accepted as the final end-to-end solution. Increasing retry count does not by itself prove the timer caused every slow sample.

## Database-only 1 ms fallback

R1ms (`6afbeeb`, full commit/tree in `source-identities.json`) changes only the database source coordinator interval from R4's 10 ms to 1 ms. The generic coordinator default and native provider images remain unchanged. Its 42-command serial comparison completed with all command exits, SQL/result checks and owner oracles passing. `r1ms-summaries.json` retains the separate mixed and phase observations.

| Provider | R4 median C8 ops/s | R1ms median C8 ops/s | R4 / R1ms process CPU µs/op | R4 / R1ms p99 upper ms |
| --- | ---: | ---: | ---: | ---: |
| SQLite | 840.3 | 1416.2 | 1085.5 / 984.9 | 108.53 / 82.84 |
| PostgreSQL | 1493.3 | 2308.0 | 902.9 / 815.1 | 35.65 / 22.94 |

There are three five-second C8 processes per candidate/provider. The 1000-row prepared read-complete p50 remains variable: SQLite R4 69.19/74.21 ms versus R1ms 8.94/33.99 ms; PostgreSQL R4 47.04/40.16 ms versus R1ms 23.69/15.13 ms. This supports a real scheduling cost but does not establish that every slow sample is a timer wake or that a shorter polling interval is the final design.

The separate open-source idle diagnostic compares C1 and R1ms, which share occupied-slot scanning but differ in both retry count and timer interval. One-second observed process CPU is 35.12/32.99 ms on SQLite and 17.34/36.38 ms on PostgreSQL. These single observations are neither a CPU confidence interval nor proof of a general idle regression. They preserve the cost concern: a permanently periodic timer can wake an otherwise idle source. This comparison is not mislabeled as a clean R4/R1ms resource experiment.

The next target is a cursor-scoped typed pull channel, following a driver's reader lifetime rather than creating a generic native operation for each batch. It must finish all provider access before making a batch ready, retain independent worker/callback tail accounting until final channel/cursor join, preserve generation and stale-reader checks, and avoid permanently rooting an abandoned idle cursor. This proposal deletes the per-batch operation lifetime; it does not allow early publication or release of an existing generic operation. Its implementation and measurements are still pending. A synchronous span row view and stable batch owner are being implemented separately from timing experiments.

## Scope and reproduction

`analyze_pairs.py` derives all mixed and phase rows in `summaries.json` directly from the retained receipts. It preserves executable/native identities, whole-process allocation/GC, real error/oracle fields, and the raw sample count. Phase p50 is the median; p95/p99 select sorted sample `floor((n-1)*p)`. Phase timing is not per-function CPU or allocation attribution. Process bytes include complete business DTO/list results; framework-only bytes remain null. Closed-loop observations do not measure external arrival rejection, which also remains null.

From this directory:

```bash
python3 analyze_pairs.py raw/paired-c-sqlite raw/paired-c-postgresql \
  raw/paired-r4-sqlite raw/paired-r4-postgresql --output reproduced-summaries.json
python3 analyze_pairs.py raw/paired-r1ms-sqlite raw/paired-r1ms-postgresql \
  --output reproduced-r1ms-summaries.json
```

The outputs are byte-identical to `summaries.json` and `r1ms-summaries.json` respectively. The original plan files retain exact executable arguments, setup, SQL/data choices, timeouts, affinity and PostgreSQL configuration. To rerun on another path, explicitly remap their recorded absolute input paths to the corresponding rebuilt, hash-verified consumers and use fresh output/database directories; do not silently overwrite old evidence.

Required current-candidate 1800-second cells remain **0/4**. The older four-cell campaign under query-optimization is separate historical evidence.
