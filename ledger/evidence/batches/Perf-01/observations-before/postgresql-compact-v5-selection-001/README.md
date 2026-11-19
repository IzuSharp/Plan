# Final PostgreSQL v5 selection and frozen before-only noise

The completed before calibration selected **180 logical operations/s** for the mixed/C16 short anchor and **144/s** for the paired long load. This is the final journal-based v5 driver cohort. The source product is clean `ea5fa528035d025bd7a28698ee7c71194432236c`; the measured driver was clean `ce2a3c75cbd535490897d062b6cbb7c095408307`.

The final three predetermined 60-second confirmations each completed **10,801 / 10,801** operations: 5,401 durable cycles and 5,400 typed pages. Independent SQL counts confirmed 5,401 measured commits per process. Every provider error count is zero, explicit business retries are zero, and all durable/owner/shutdown receipts passed. Internal provider retry counts remain unavailable.

| Final confirmation | Mixed p99 (ms) | Cycle p99 (ms) | Page p99 (ms) | App CPU (% one core) | App RSS peak (B) |
|---|---:|---:|---:|---:|---:|
| `14-confirmation-0-180` | 155.462124 | 211.411925 | 125.704641 | 86.144156 | 50352128 |
| `15-confirmation-1-180` | 120.373713 | 140.709601 | 73.498483 | 86.507281 | 44822528 |
| `16-confirmation-2-180` | 158.974390 | 178.478432 | 92.016506 | 86.880819 | 48480256 |

CPU/RSS describe the whole mixed application, not conditional slices. PostgreSQL server-process CPU/RSS, pool wait and lock-wait duration are unavailable in these timing summaries. Separate profiling is not substituted for timed measurements. Each target journal includes all measurement operations plus 16 warmups and is sealed, closed and published without error. Recovery has its separate receipt.

`controller.json` and `selection.json` are verbatim originals. `audit.json` checks the prior controller→summary→frozen→plan/extra-receipt pins, identical configuration and producer hashes, distinct application PID/start pairs, durable commits and complete journal metadata. All failed cells remain in the controller and audit:
- `06-ladder-320`: 6,956/9,601 successes, p99 2712.780707 ms, valid=false, qualified=false; generator saturation: in-flight capacity.
- `07-refine-240`: 7,055/7,201 successes, p99 2687.081756 ms, valid=false, qualified=false; generator saturation: in-flight capacity.
- `09-refine-220`: 6,601/6,601 successes, p99 1929.920053 ms, valid=true, qualified=false; service standard failed.
- `12-confirmation-2-200`: 12,001/12,001 successes, p99 850.807314 ms, valid=true, qualified=false; service standard failed.
- `13-confirmation-step-down-180`: 5,401/5,401 successes, p99 814.295873 ms, valid=true, qualified=false; service standard failed.

The final failing bracket is 200/s. Generator-limited points are not server-capacity upper bounds. No failed result is reclassified. These short cells provide **zero 30-minute acceptance credit**.

## Immutable timing driver and separate final verifier

Root created and verified the clean detached timing checkout at:

`/workspace/scratch/01c249676f47/.worktree/Perf-01-frozen-drivers-linux/NativeWeave`

It remains exact `ce2a3c75cbd535490897d062b6cbb7c095408307`, with A21 `dfb57cf6…` and reader `8034692b…`. All later DB before/after/direct/managed timing and this noise extraction use those same helper bytes. A later post-run-only common verifier may advance separately. Full-file source checks are not waived; the comparison extractor already normalizes unchanged source paths. The audit records all full hashes.

## Executed noise freeze

The exact command was:

```sh
bash /workspace/scratch/01c249676f47/.worktree/Perf-01-db-linux/Plan/ledger/evidence/batches/Perf-01/observations-before/postgresql-compact-v5-selection-001/freeze-noise.sh
```

It exited **0** from `2026-11-19T13:10:16.392584+00:00` to `2026-11-19T13:10:20.116721+00:00`, on CPU8, using Python3.12.14. The script is retained byte-for-byte as executed, including its original preparation comment; that comment is superseded by this actual execution record. The destination was newly created and is not overwritten.

Output: `/workspace/scratch/01c249676f47/perf01-evidence/noise/postgresql-mixed-c16-r180-v5-001.json`

SHA-256: `5bb25871bdd4863158f6b0aa0791b321b8ae147f122ec4ff9400c5b1106f7585`

The script checks literal selection/controller pins, exact driver commit and all repository helper hashes before importing the reader. Its unchanged reviewed extraction body validates every successful raw logical record, dataset/configuration, three distinct application instances and non-overlapping measurement windows. The [actual command/log/receipt packet](../../checks/database-noise-freeze-001/README.md) retains the exact result bytes. No workload, test or build was run by the extraction.

| Slice | Three independent before process means (ms) | Frozen absolute band (ms) |
|---|---|---:|
| mixed | 28.337432, 27.805341, 30.305233 | 2.499892 |
| cycle | 42.904572, 42.625293, 45.793158 | 3.167865 |
| page | 13.767595, 12.982644, 14.814440 | 1.831796 |

The predeclared absolute band is `max(1000 ns, range of the three before process means)`; relative noise is zero. This is a process-mean noise allowance, not a p99 confidence interval. Fresh later interleaved comparison processes remain separate from this calibration triplet. Conditional cycle/page bands apply only to the same mixed/C16 load; descriptive C1/C4/C8 cells cannot borrow them.
