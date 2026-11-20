# PostgreSQL before long: accepted numerical and resource report

The completed corrected verification accepts **1,802.212239616 seconds** of continuous ordinary business work. It verified all **259,526** measured logical operations. The original driver exited zero. The first wrapper exited one because it compared the requested duration with the independently derived planned span; that failed receipt remains unchanged and receives zero credit. Corrected verification 002 re-read the same raw run without rerunning its load, finished at **2026-11-20 01:07:04.658211 UTC**, and exited zero. The raw data and old receipts were not changed.

The reviewed projector actually completed with **outer exit 0** at **2026-11-20 02:02:31.133853 UTC**. It passed 129,876 bounded metadata/resource guards and read 15 bound inputs, including 35,012 application and 5,496 generator resource snapshots. These guard counts are not additional test cases or a repeated full-row business audit. `pending-binding.json` preserves the earlier pending snapshot. `binding-final-001.json` separately binds the actual accepted corrected receipt and successful re-verification. Neither file grants permission to overlap a timing window. The measurement owner runs the reviewed command under the existing exclusive lock.

## Actual small-receipt observations

| Measure | PostgreSQL before |
|---|---:|
| Frozen arrival rate / concurrency | 144/s / 16 |
| Successful measured operations | 259,526 / 259,526 |
| Committed business cycles / paging operations | 129,763 / 129,763 |
| Successful throughput | 143.99334723064322/s |
| Arrival p50 / p95 / p99 | 19.241708 / 57.667928 / 207.259125 ms |
| Maximum dispatch-start lag | 56.106435 ms |
| Dispatch lag above 50 ms / allowed maximum | 1 operation / 100 ms |
| Independent rows per table before recovery / shutdown | 129,899 / 129,931 |
| Recovery operations | 32 successful |
| Surfaced provider exceptions / business retries | 0 / 0 |

The target observed load from **2026-11-20 00:16:46.007007 UTC** to **00:46:48.258945 UTC**. These target timestamps are distinct observations from the A21 ordinary-operation lower bound used for the credited duration. Planned duration is 1,802.2568291 seconds: `(259526 - 1) * 6944444 ns`, not the requested 1,802 seconds. The unchanged frozen driver includes its existing scheduling guard.

| Observed role | Measurement CPU seconds | CPU observation span, seconds | Measurement RSS peak, bytes | Idle RSS peak, bytes |
|---|---:|---:|---:|---:|
| Application | 1,246.06 | 1,802.327393613 | 54,226,944 | 30,416,896 |
| Scheduler | 288.33 | 1,800.951609126 | 1,437,507,584 | 1,446,141,952 |
| Target client | 811.76 | 1,800.948752015 | 329,617,408 | 343,265,280 |
| Controller | 22.33 | 1,800.952185650 | 75,653,120 | 75,653,120 |

The 256 MiB gate applies to the application. It is not a generator or whole-host memory limit. Scheduler cyclic GC was deferred, recorded zero in-scope collections and restored its enabled state. Sampling ends before final replay/GC restoration; restoration does not prove all cycles were collected or bound the later heap. Managed allocation and managed GC, separate PostgreSQL server CPU, database execution time, pool and lock waits, native allocator usage, boundary calls and copied bytes are unavailable. This is before-only evidence, not product improvement or a direct-Rust comparison.

## Projection and resource bucket contract

`project_results.py` is shared by this cell and the SQLite sibling. It validates exact SHA-256 inputs, completed execution/acceptance, the immutable measured driver and loaded before binaries, original policy/limits, all successful counts, full-row verifier proof, independent durability, 32 recovery operations, at least 60 seconds idle, normal native retirement and no live owned process. It reads at most 2 MiB per metadata document. It does **not** load the large operation, application receipt or event journals and does not repeat the original correctness verification.

Optional 30-second buckets stream only the application and generator resource JSONL. Each input is hash checked. Buckets use bounded accumulators, are anchored to the **target load window**, and do not replace the frozen A21 phase summaries. A physical RSS read overlapping a bucket is included conservatively. CPU uses actual first/last CPU observations in that bucket, only for one stable identity and nondecreasing counters; it is not interpolated to 30 seconds. Empty/ambiguous CPU brackets remain null. Counts, coverage and unavailable observations remain visible. Identity values are used privately for checks and never exported.

Public JSON is constructed from fixed keys and validated to contain only numbers, booleans, nulls, enumerations, UTC values and hashes. No PID, thread ID, environment, control token, invocation or operational path is copied. `projection-execution.json` records the completed offline execution; `outer-execution.json` separately records the observed child-process exit and log hashes. Failures leave the original inputs intact and must retain the actual outer exit/log; no failed extraction may be presented as successful.

## Actual offline command and reproduction

Set `ROOT`, `PLAN`, and `PERF_PY` to the existing workspace, this reviewed Plan checkout, and the repository-locked Python 3.12.14 executable. These are local invocation parameters, not public evidence fields. `PG_REPORT` and `SQLITE_REPORT` are report directories below `PLAN`. Use the source and binding hashes printed for the final reviewed commit; do not substitute a changed script.

```sh
PG_REPORT="$PLAN/ledger/evidence/batches/Perf-01/checks/before-postgresql-observer-long-002/results-001"
SQLITE_REPORT="$PLAN/ledger/evidence/batches/Perf-01/checks/before-sqlite-observer-long-001/results-001"
/usr/bin/flock --nonblock "$ROOT/perf01-evidence/timing.lock" /usr/bin/taskset -c 8 "$PERF_PY" "$PG_REPORT/project_results.py" \
  --source-sha256 c151273e130f2aec14b94d212e59effd006cee90dba01e74fe085b8f3a802fbd \
  --binding "$PG_REPORT/binding-final-001.json" --binding-sha256 3004f4e3549053603f7a39e061a05b06133ebd7f684d8fb2d1e177e6166eccfd \
  --cell "$ROOT/perf01-evidence/long/before/postgresql-observer-002" \
  --execution "$ROOT/perf01-run/before-postgresql-observer-002-long-execution.json" \
  --original-verification "$ROOT/perf01-evidence/long/before/postgresql-observer-002-verification.json" \
  --verification "$ROOT/perf01-evidence/long/before/postgresql-observer-002-verification-corrected-002.json" \
  --reverification-execution "$ROOT/perf01-run/database-before-postgresql-observer-002-reverification-002-execution.json" \
  --output "$PG_REPORT" --resource-buckets
```

The program takes no inner lock. Do not wrap a command already holding the same exclusive lock a second time. The output files already exist for this completed run. To reproduce extraction, choose a fresh output directory; writing uses exclusive creation and refuses to overwrite these results. The shared helper accepts a relocated byte-identical cell and translates only paths inside the recorded original cell root.

## Evidence bindings

Corrected verifier: `ba6947c372a807cfa9d3c4d097096bff87a50def1fdf6772759592a93d2fdd96`. Successful re-verification execution: `f37613d5be8bb09f924d6758283d6ebf0f634eecfcf9be311ca3e33de9fd4f18`. Corrected amendment: `69e5e4733830f0efcb1181a024e70099ef0ab12117af1fc4ce72e1e61499110f`. Corrected wrapper source: `a8f39b4409d63343edcbcad1c8745c02e742d5da168d86460a2b23b3a784881e`. Other exact input hashes are in the final binding. The interrupted first offline re-verification has no completed result and is not granted credit.

## Stored public results

[public-summary.json](public-summary.json) contains the fixed numerical report and all 30-second buckets. [projection-execution.json](projection-execution.json) binds the actual input hashes and extraction clocks. [outer-execution.json](outer-execution.json) confirms the observed process exit without exposing its private invocation. Raw operation evidence was not republished or replayed in this extraction. Original accepted credit is carried through, not counted a second time.
