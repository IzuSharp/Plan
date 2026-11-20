# Before database anchor mean-noise observations

Six fresh before processes completed successfully: PostgreSQL at **180 arrivals/s**, SQLite at **50 arrivals/s**, both at concurrency **16**. Each process measured approximately 60 seconds of the same mixed cycle/page workload. These are fixed-load before-only noise controls. They do not measure capacity, p99 noise or optimization gain; they receive **zero long-test credit and zero credit toward the 48 formal comparison processes**.

The rates differ from the earlier 220/s and 60/s capacity confirmations and from the accepted 144/s and 40/s long loads. Their evidence and statistical purposes remain separate.

## Actual process results

All times are UTC on 2026-11-20. Execution endpoints include setup, warmup, recovery and shutdown; measured seconds below come from each actual A21 measurement window. Process numbers use the execution receipt index, not operating-system identities or the within-cell repetition field.

| Provider | Process | Execution start–end UTC | Measured s | Success / offered | Errors | Success/s | Mean ms | p99 ms |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| postgresql | 1 | 02:28:50.920420–02:30:12.793447 | 60.029977216 | 10801 / 10801 | 0 | 179.926771605 | 24.277708643 | 90.702742 |
| postgresql | 2 | 02:30:12.798409–02:31:34.725162 | 60.017855709 | 10801 / 10801 | 0 | 179.963110518 | 25.243069272 | 133.999209 |
| postgresql | 3 | 02:31:34.731853–02:32:56.553926 | 60.019272549 | 10801 / 10801 | 0 | 179.958862233 | 25.171060492 | 107.257854 |
| sqlite | 1 | 02:32:56.558796–02:34:12.186591 | 60.012684691 | 3001 / 3001 | 0 | 50.006094802 | 35.109425709 | 181.328938 |
| sqlite | 2 | 02:34:12.196539–02:35:27.703006 | 60.020079682 | 3001 / 3001 | 0 | 49.999933621 | 30.744473861 | 164.269953 |
| sqlite | 3 | 02:35:27.707106–02:36:44.437093 | 60.033810113 | 3001 / 3001 | 0 | 49.988498054 | 34.525510046 | 186.903355 |

Each process passed its original validity, service-standard and independent durability checks. Each provider has three distinct application instances and three nonoverlapping fresh execution intervals. The six actual driver exits are zero. SQLite surfaced BUSY/LOCKED and business retries are zero; internal busy-handler attempts remain unavailable. The JSON also retains the cycle/page conditional counts, means, tails, successful rates and five input-receipt hashes for each process. Cycle/page statistics describe subsets of this same mixed workload, not separately timed workloads or separately attributable resource usage.

## Frozen mean-noise bands

For each provider and view, the unchanged rule is:

```text
absolute_noise_ns = max(1000, max(three process means) - min(three process means))
relative_noise = 0
```

| Provider | Mixed band, ms | Cycle band, ms | Page band, ms |
|---|---:|---:|---:|
| postgresql | 0.965360629 | 1.202557131 | 0.728120201 |
| sqlite | 4.364951848 | 7.874522282 | 0.853041700 |

The rule uses the range of independent process **means** with a 1,000 ns floor. It is not a confidence interval and must not be applied as a measured p99 noise threshold. The measured p99 values are reported separately without inventing a tail-noise band. No candidate-versus-before comparison has been performed here.

## Evidence and projection scope

The workload execution ran **2026-11-20T02:28:50.920151+00:00–2026-11-20T02:36:44.487826+00:00**. The already completed full-row freeze ran **2026-11-20T02:38:59.951143+00:00–2026-11-20T02:39:07.767248+00:00**, both provider commands exited zero, and each bound 93 input hashes. The present publication step reads only the two existing noise JSON files and these two small execution receipts; it does not repeat the full-row audit or generate load.

[public-summary.json](public-summary.json) is a fixed-key numerical/boolean/enum/UTC/hash projection. [projection-execution.json](projection-execution.json) records the four actual input hashes. No operational path, process/session ID, argv, application-instance object or control metadata is copied. The original full local records are retained. Loaded before application/native-library hashes are preserved as fixed module roles.

Extractor source SHA-256: `bb16306df930ce89c5a3c9d911e77bd80d70822b360532330a6764765fecffc4`.

Anchor contract SHA-256: `c7688d0d8765e6e4ef23d81fcd5a36cbce8b4601d39cc804d7a67c9953c23178`.
