# Bounded PostgreSQL generator GC diagnostic

Status: diagnostic helper source, not an executed profile or a runtime change.
The original PostgreSQL144/C16 long cell remains invalid for generator dispatch
lag, with zero long-duration credit. Its complete successful application results
do not waive the fixed100ms generator rule.

## Exact attachment and retained workload

`prepare` reads the unchanged published freeze85061c4e and database command
document9604544d. It checks the actual frozen ce2 entry points/helpers and the
locked Python executable. It copies the original PostgreSQL command and changes
only the output directory and variant label to `diagnostic`. The before package,
observer, PostgreSQL18, durable workload,144/s,C16,1802s requested duration,
259,526 planned operations,20ms scheduler lead,CPU masks,limits,warmup16,
recovery32,and idle60 remain unchanged. No shorter CLI cell preserves this full
planned count/initial Oracle/RunState heap: `run.py:157` derives it from duration.

Only the diagnostic child environment prepends this directory to PYTHONPATH.
`sitecustomize.py` accepts the exact source path,hash,argv,Python version/path,
generator affinity,and generated full plan. It installs `gc.callbacks` in:

| Role | Actual entry point | Existing supervision role |
| --- | --- | --- |
| scheduler | `src/Benchmarks.Domain/cell_worker.py` | `cell-worker` |
| target | `tests/Perf01.Database/target.py` | `http-adapter` |

The outer controller and other Python commands do not attach. C#/Rust and
PostgreSQL receive no instrumentation. Each attached header binds PID,PPID,
procfs start_ticks,native thread ID,role,source/plan/hook/config hashes,and argv.
Correlate these identities with the existing owned-process registry and
generator-resource observations; never identify a process by PID alone.

The hook does not force collection,disable GC,change thresholds,replace time or
scheduling functions,inspect business objects,or install signal handlers. It
logs start/stop of all generations with actual monotonic and process-CPU clocks,
thread ID,collection counters,and bounded fixed-shape scalar fields. Each
process has a16MiB append limit. Writes use `os.write`,not a buffered Python
file object,so already written events survive an intentional SIGTERM. A killed
collection may have only its start; this is incomplete evidence,not zero time.
Write/callback failure stops that logger,not the workload. Missing attachments,
log exhaustion,and incomplete pairs limit any negative inference.

The callback-entry interval includes observer work. `start_hook_ns` separately
records start-hook cost; `collection_interval_ns` excludes that start cost but
is still an observed interval,not a proven exclusive collector CPU measurement.
The process-CPU delta includes all threads. No pause classification is asserted
until actual diagnostic records and dispatch/event/resource windows agree.

## Root commands

Run only after the integration owner declares the measurement resource free.
Do not execute this README as an unattended shell script. The source author did
not run any of these commands or any load.

```bash
PERF01_ROOT=/workspace/scratch/01c249676f47
source "$PERF01_ROOT/perf01-toolchain/env.sh"
PERF01_PY=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
PERF01_PLAN="$PERF01_ROOT/.worktree/Perf-01-linux/Plan"
PERF01_DIAG="$PERF01_PLAN/ledger/evidence/batches/Perf-01/diagnostics/db-generator-gc/gc_diagnostic.py"
PERF01_OUT="$PERF01_ROOT/perf01-evidence/profile/postgresql-generator-gc-001"
taskset -c 8 "$PERF01_PY" "$PERF01_DIAG" prepare \
  --freeze "$PERF01_PLAN/ledger/evidence/batches/Perf-01/frozen-execution.json" \
  --command-document "$PERF01_PLAN/ledger/evidence/batches/Perf-01/database-before-long-commands.json" \
  --output "$PERF01_OUT"
```

After checking the new configuration,launch the workload in one owned session:

```bash
taskset -c 8 "$PERF01_PY" "$PERF01_DIAG" run \
  --config "$PERF01_OUT/configuration.json"
```

`run` execs the original nonblocking flock/taskset2,3/DB command. The integration
owner must supervise this diagnostic and inspect only bounded/incremental GC
records on CPU8. There is no automatic watcher or new process supervisor.
First confirm both `gc-*.jsonl` headers say `attached`, bind the expected source
and PID/start_ticks, and have no `attachment-error-*.json` file. Stop if either
role is missing or the logger fails/exhausts; incomplete observation cannot
exclude collector pauses.

Use the first complete `cell/observation.events.jsonl` line's `observed_ns` as
the measured-event observation start. Read only that first bounded line to
establish the start, not the full raw file. A qualifying event has `phase:stop`,
`generation:2`, `start_monotonic_ns` at or after that first observation, and
`collection_interval_ns > 100000000`. Allow at most2seconds after observing
the first qualifying event for subsequent admitted/completed events to flush,
then request stop below. Stop no later than360seconds after the first measured
event even if no qualifying collection appears. If startup produces no first
event within300seconds, stop and record startup/instrumentation failure.

The six-minute bound is effective observation,not a complete
1802second run,and cannot reach the original second cluster around1028seconds.
If this diagnostic has no relevant collection,it does not exclude an unobserved
second-cluster cause or establish that all generator stalls are non-GC.

For an explicit manual stop,use the same existing control protocol:

```bash
taskset -c 8 "$PERF01_PY" "$PERF01_DIAG" stop \
  --config "$PERF01_OUT/configuration.json" \
  --reason 'Operator stopped zero-credit GC diagnostic'
```

This creates `cell/control.json` with `stop:true`; it never signals a guessed PID.
`supervision.py:stop_requested/supervised_command` observes that flag every0.1s,
signals identity-bound registered descendants with SIGTERM,and escalates after
the existing5second grace if necessary. Keep the outer DB process alive so its
finally restores affinity and its PostgreSQL context tears down. Observe its
actual exit and the final supervision receipt; confirm no owned descendants or
PostgreSQL service remain before another load. If supervision has not
acknowledged the stop within45seconds, report cleanup unproved and inspect the
owned session; do not start another load or signal a guessed process.
This is bounded process cleanup,not proof of native graceful retirement.

## Evidence and limits

`configuration.json`,per-process `gc/*.jsonl`,and attachment errors live outside
the cell,so application cleanup does not remove them. Save the bounded manual
observation/stop receipt alongside them, including the actual first-event and
trigger timestamps, stop command time/reason, and observed cleanup outcome.
The cell
receives `profile-driver.json` with `formal_timing_eligible:false`; the unchanged
common long verifier must reject it even if it accidentally runs to completion.
Every helper receipt records duration credit0. Preserve all original raw files,
including the failed formal long cell; do not edit their flags or hashes.

Intentional interruption may prevent A21 from writing its final
`observation.json`,which normally carries the exact dispatch ledger. The
persisted `observation.events.jsonl` contains actual admission/completion
observation timestamps and exact wire bytes,but is not an exact dispatch log.
GC/event gaps are correlation evidence; do not claim reconstructed dispatch
timestamps or complete absence of generator pauses. The original long cell's
already extracted exact dispatch bursts remain a separate source of evidence.

No frozen source or generic driver/report constraint is changed by this helper.
Root must review measured callback/process/resource evidence before selecting
any remedy. A future instrumentation change or generator fix needs its own
prospective identity and equivalence decision; it is never a product gain.
