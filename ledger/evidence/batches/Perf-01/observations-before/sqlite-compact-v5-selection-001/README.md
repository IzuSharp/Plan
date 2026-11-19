# Final SQLite v5 selection and frozen before-only noise

The completed before calibration selected **50 logical operations/s** for the mixed/C16 short anchor and **40/s** for the paired long load. This is the final journal-based v5 driver cohort. The source product is clean `ea5fa528035d025bd7a28698ee7c71194432236c`; the measured driver was clean `ce2a3c75cbd535490897d062b6cbb7c095408307`.

The final three predetermined 60-second confirmations each completed **3,001 / 3,001** operations: 1,501 durable cycles and 1,500 typed pages. Independent SQL counts confirmed 1,501 measured commits per process. Every provider error count is zero, explicit business retries are zero, and all durable/owner/shutdown receipts passed. Internal provider retry counts remain unavailable.

| Final confirmation | Mixed p99 (ms) | Cycle p99 (ms) | Page p99 (ms) | App CPU (% one core) | App RSS peak (B) |
|---|---:|---:|---:|---:|---:|
| `08-confirmation-0-50` | 295.961647 | 417.291117 | 39.431056 | 40.492313 | 41422848 |
| `09-confirmation-1-50` | 219.822617 | 309.903726 | 43.291691 | 39.779385 | 39493632 |
| `10-confirmation-2-50` | 168.307978 | 219.952395 | 31.606908 | 38.607944 | 41697280 |

CPU/RSS describe the whole mixed application, not conditional slices. PostgreSQL server-process CPU/RSS, pool wait and lock-wait duration are unavailable in these timing summaries. Separate profiling is not substituted for timed measurements. Each target journal includes all measurement operations plus 16 warmups and is sealed, closed and published without error. Recovery has its separate receipt.

`controller.json` and `selection.json` are verbatim originals. `audit.json` checks the prior controller→summary→frozen→plan/extra-receipt pins, identical configuration and producer hashes, distinct application PID/start pairs, durable commits and complete journal metadata. All failed cells remain in the controller and audit:
- `04-ladder-80`: 1,733/2,401 successes, p99 2150.714540 ms, valid=false, qualified=false; target exit: 1.
- `05-refine-60`: 1,801/1,801 successes, p99 510.401344 ms, valid=true, qualified=false; service standard failed.
- `07-refine-55`: 1,652/1,652 successes, p99 599.668574 ms, valid=true, qualified=false; service standard failed.

The final failing bracket is 55/s. Generator-limited points are not server-capacity upper bounds. No failed result is reclassified. These short cells provide **zero 30-minute acceptance credit**.

## Immutable timing driver and separate final verifier

Root created and verified the clean detached timing checkout at:

`/workspace/scratch/01c249676f47/.worktree/Perf-01-frozen-drivers-linux/NativeWeave`

It remains exact `ce2a3c75cbd535490897d062b6cbb7c095408307`, with A21 `dfb57cf6…` and reader `8034692b…`. All later DB before/after/direct/managed timing and this noise extraction use those same helper bytes. A later post-run-only common verifier may advance separately. Full-file source checks are not waived; the comparison extractor already normalizes unchanged source paths. The audit records all full hashes.

## Executed noise freeze

The exact command was:

```sh
bash /workspace/scratch/01c249676f47/.worktree/Perf-01-db-linux/Plan/ledger/evidence/batches/Perf-01/observations-before/sqlite-compact-v5-selection-001/freeze-noise.sh
```

It exited **0** from `2026-11-19T13:10:14.014705+00:00` to `2026-11-19T13:10:16.391687+00:00`, on CPU8, using Python3.12.14. The script is retained byte-for-byte as executed, including its original preparation comment; that comment is superseded by this actual execution record. The destination was newly created and is not overwritten.

Output: `/workspace/scratch/01c249676f47/perf01-evidence/noise/sqlite-mixed-c16-r50-v5-001.json`

SHA-256: `c3cd91e963ff3390d58821487a628cf7c311d367f085eb63b13437fca034ec68`

The script checks literal selection/controller pins, exact driver commit and all repository helper hashes before importing the reader. Its unchanged reviewed extraction body validates every successful raw logical record, dataset/configuration, three distinct application instances and non-overlapping measurement windows. The [actual command/log/receipt packet](../../checks/database-noise-freeze-001/README.md) retains the exact result bytes. No workload, test or build was run by the extraction.

| Slice | Three independent before process means (ms) | Frozen absolute band (ms) |
|---|---|---:|
| mixed | 45.064080, 38.167835, 32.532086 | 12.531994 |
| cycle | 75.190915, 61.692793, 52.511714 | 22.679202 |
| page | 14.917161, 14.627192, 12.539139 | 2.378022 |

The predeclared absolute band is `max(1000 ns, range of the three before process means)`; relative noise is zero. This is a process-mean noise allowance, not a p99 confidence interval. Fresh later interleaved comparison processes remain separate from this calibration triplet. Conditional cycle/page bands apply only to the same mixed/C16 load; descriptive C1/C4/C8 cells cannot borrow them.
