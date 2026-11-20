# SQLite before long: accepted numerical and resource report

The actual driver and verifier both exited zero. The final verifier accepts **1,802.209932916 seconds** of ordinary work with **72,091** successful full-row checks, zero failed checks, independent durable reconciliation, recovery and normal cleanup. The reviewed projector actually completed with **outer exit 0** at **2026-11-20 02:02:31.984924 UTC**. It passed 132,337 bounded metadata/resource guards and read 13 bound inputs, including 35,774 application and 5,571 generator resource snapshots. These guards do not constitute new tests or a repeated full-row business audit.

| Measure | SQLite before |
|---|---:|
| Frozen arrival rate / concurrency | 40/s / 16 |
| Successful measured operations | 72,091 / 72,091 |
| Committed business cycles / paging operations | 36,046 / 36,045 |
| Successful throughput | 39.99909657397195/s |
| Arrival p50 / p95 / p99 | 20.623039 / 79.360110 / 115.857606 ms |
| Maximum dispatch-start lag | 28.537958 ms |
| Surfaced SQLite BUSY / LOCKED | 0 / 0 |
| Business retry attempts | 0 |
| Independent rows per table before recovery / shutdown | 36,182 / 36,214 |
| Recovery operations | 32 successful |

The target observed load from **2026-11-20 01:14:52.137680 UTC** to **01:44:54.421688 UTC**. These are target timestamps, not substitutes for the A21 credited lower bound. The requested duration is 1,802 seconds; the frozen plan span is 1,802.25 seconds from `(72091 - 1) * 25000000 ns`. Recovery ended at **01:45:02.845887 UTC**; the separately timed idle interval ran **01:45:03.177125–01:46:03.177303 UTC**. Final successful supervisor completion was **01:47:42.776620 UTC**.

| Observed role | Measurement CPU seconds | CPU observation span, seconds | Measurement RSS peak, bytes | Idle RSS peak, bytes |
|---|---:|---:|---:|---:|
| Application | 544.00 | 1,802.295253603 | 43,560,960 | 34,918,400 |
| Scheduler | 180.70 | 1,801.701209676 | 597,512,192 | 607,092,736 |
| Target client | 281.57 | 1,801.693616014 | 226,889,728 | 232,407,040 |
| Controller | 11.78 | 1,801.708458848 | 60,649,472 | 60,649,472 |

BUSY/LOCKED counts are surfaced provider exceptions observed across the process, including setup/recovery. SQLite internal busy-handler attempts are **unavailable**, so zero surfaced exceptions does not establish zero internal waits. The application gate is 256 MiB; generator RSS is separate. Cyclic-GC deferral recorded zero in-scope collections and restoration, but sampler termination precedes final replay/restoration. Managed allocation/GC and post-restoration generator RSS are unavailable. This before-only run establishes neither optimization gain nor a direct-Rust gap.

## Shared portable projector

Use the source and detailed projection contract in [the PostgreSQL report](../../before-postgresql-observer-long-002/results-001/README.md). This provider uses the same helper and creates its own two exclusive output files. Exact final verifier and supervisor hashes are `65b05e2ebda307c4d892d1374fbbe2550fc9fe3c977ea981f06aa0f238f2efd5` and `c439cdccfe93b536f0c1139b200f1c51f18e9c4c48fb104a6ad2b67b6b6a04b1`. Other inputs are bound separately in `binding-final-001.json`.

The following command actually ran with the local variables from the shared runbook and measurement-owner clearance. Reproduction must select a fresh output directory because the completed output files are exclusive and retained:

```sh
/usr/bin/flock --nonblock "$ROOT/perf01-evidence/timing.lock" /usr/bin/taskset -c 8 "$PERF_PY" "$PG_REPORT/project_results.py" \
  --source-sha256 c151273e130f2aec14b94d212e59effd006cee90dba01e74fe085b8f3a802fbd \
  --binding "$SQLITE_REPORT/binding-final-001.json" --binding-sha256 fa238f1bcd6548858c1b3d656cc547c4e59eb404f58dc8e4aa80cc8d71ee39f1 \
  --cell "$ROOT/perf01-evidence/long/before/sqlite-observer-001" \
  --execution "$ROOT/perf01-run/before-sqlite-observer-001-long-execution.json" \
  --verification "$ROOT/perf01-evidence/long/before/sqlite-observer-001-verification.json" \
  --output "$SQLITE_REPORT" --resource-buckets
```

Only small metadata and the two resource streams are read. No huge operation/event receipt is replayed, and no benchmark or build is run. The public projection excludes paths, process identities, invocation/control metadata and environment data. It contains 61 numerical buckets for each of the four process roles, with explicit sampling coverage. No bucket reported an identity change/failure or CPU-counter regression. `outer-execution.json` records the actual outer exit and log hashes separately from the projector receipt.

## Stored public results

[public-summary.json](public-summary.json) contains the fixed numerical report and all 30-second buckets. [projection-execution.json](projection-execution.json) binds the actual input hashes and extraction clocks. [outer-execution.json](outer-execution.json) confirms the observed process exit without exposing its private invocation. Raw operation evidence was not republished or replayed in this extraction. Original accepted credit is carried through, not counted a second time.
