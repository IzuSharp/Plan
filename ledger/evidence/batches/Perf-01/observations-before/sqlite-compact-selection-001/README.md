# SQLite compact calibration selection and prepared noise extraction

This is a read-only audit of the completed **before** SQLite calibration. The
policy selected **54 offered business operations/s at concurrency 16** for the
short mixed anchor and **43/s** for the paired long load. This records a sampled
policy selection; the 1802-second run and its independent 1800-second duration
acceptance are still outstanding.

The original directory is
`/workspace/scratch/01c249676f47/perf01-evidence/calibration/before-sqlite-compact-v4`.
`selection.json` and `controller.json` here are verbatim copies. `audit.json`
records the original file hashes, the final cells' actual command lines,
summary/frozen/plan hashes, loaded-file identities and every failed cell.

## Actual completed confirmation triplet

The final three predetermined 60-second confirmations were completed by separate
application PID/start identities. Each offered and successfully completed 3,241
logical operations: 1,621 durable cycles and 1,620 typed pages. Each independent
SQL oracle found 1,621 measured committed operations; provider exceptions, BUSY,
LOCKED and explicit business retries were all zero. Internal SQLite busy-handler
attempts are unavailable. Each application receipt released the consumer and
database owners and reached server `Disposed`.

| Cell | Mixed p99 (ms) | Cycle p99 (ms) | Page p99 (ms) | App CPU (% of one core) | App RSS peak (bytes) |
|---|---:|---:|---:|---:|---:|
| `12-confirmation-0-54` | 286.206671 | 480.557631 | 46.551693 | 44.280741 | 43,180,032 |
| `13-confirmation-1-54` | 214.076054 | 273.418669 | 38.802313 | 40.640033 | 42,041,344 |
| `14-confirmation-2-54` | 257.418997 | 400.338976 | 39.073628 | 42.285407 | 43,114,496 |

These values are copied from completed cell summaries. CPU and RSS describe the
whole mixed application process, not the individual cycle or page slice. The
application PID/start pairs are `(579, 2095994)`, `(627, 2103552)` and
`(675, 2111091)`. Raw measurement-window non-overlap and process means are gates
of the prepared extraction below; this metadata-only audit did not read the raw
observation arrays during concurrent PostgreSQL timing.

The source product is clean
`ea5fa528035d025bd7a28698ee7c71194432236c`; the measurement driver is clean
`aa3399f0418a6d0910cc56697abfaa3769f32b54`. All three cells bind the same compact
mode, driver/helper content, dataset, seed, settings, producer/observer metadata,
resource/SLO limits and service/generator CPU masks. The loaded application and
native-library hashes are retained in `audit.json` rather than inferred from a
package label. Both copied controller/selection receipts bind prospective policy
4 SHA-256 `0c7cd866b1ad0fc86d647e31dd1b6fe0b148d2e7ca54d83b7286cec09f11cafc`.

## Failed evidence remains part of the selection

The 80/s cell remains invalid, including its one failed logical cycle and
halted-dispatch tail; the narrow interpretation is recorded in the sibling
`sqlite-80-replay-failure-001` directory. The 70/s and 65/s refinements and all
three 60/s confirmations failed the 500 ms service limit.

**The earlier 54/s, 30-second step-down also failed:** p99 was 574.634457 ms with
all 1,621 operations successful. It is preserved in the copied full controller
and the audit's failed-cell list. The selection's original `higher_failed_points`
field only includes rates above the selected anchor, so it does not itself show
this equal-rate failed cell. The later three required 60-second confirmations
passed; this does not establish that every 54/s run will pass.

## Prepared command; not executed

The final confirmation triplet can supply the **before-only** noise bands at this
exact mixed/C16/54/s anchor, as specified in `../../database-layered-runbook.md`.
The Python body in `freeze-noise.sh` is copied verbatim from that reviewed,
committed runbook; its command and body hashes are recorded in `audit.json`.
There is no new measurement-driver implementation here.

After the current exclusive measurement window ends, execute:

```sh
bash /workspace/scratch/01c249676f47/.worktree/Perf-01-linux/Plan/ledger/evidence/batches/Perf-01/observations-before/sqlite-compact-selection-001/freeze-noise.sh
```

The script selects the exact toolchain environment and Python 3.12.14, pins the
original selection/controller and A21/stream-reader bytes, and runs on CPU 8. It
checks prior controller pins for summary/frozen inputs, the frozen dataset/plan
chain, exact shared configuration, every successful raw logical record, three
unique application instances and non-overlapping measurement windows. It then
writes a **new** receipt at:

`/workspace/scratch/01c249676f47/perf01-evidence/noise/sqlite-mixed-c16-r54-001.json`

The predeclared band for each of mixed, cycle and page is the larger of 1,000 ns
and the range of its three before-process means, with relative noise zero. No
means or bands have been computed by this audit. Freeze the produced receipt and
its SHA before any after comparison. Later comparison uses fresh interleaved
before/after/direct-Rust processes; these calibration processes must not be reused
as the fresh before comparison triplet. The C1/C4/C8 exploratory points remain
descriptive and cannot borrow the C16 noise band.

No application load, build, finite test, new SQL query or noise extraction was
performed to produce this selection audit. It gives no 30-minute acceptance
credit and does not alter any original invalid verdict.
