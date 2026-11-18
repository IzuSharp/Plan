# B23 interruption and continuation rules

This note describes the existing frozen controller at `9406093`; it changes no source, profile, threshold, completed receipt, or execution policy. Current retained execution is owned by `/root/b23_finish`, session `97908`. The session ID is local to its owning agent and may not be usable by another conversation. An unknown session ID does not prove that the process stopped.

## First recover the live execution

Read `ROOT/task07-b23/root-launch-retirement-f889/launch.json`, `exec-session.json`, and `ROOT/task07-b23/operating-point-cohorts-retirement-f889/cohorts.json`. Observe whether the live timestamps and process records advance. If they do, follow that same run and preserve its exclusive window. Do not launch another controller. The root launcher saves phase and current case every five seconds; the inner controller saves individual process observations and the cohort saves completed invocations.

The root launcher is deliberately a one-shot wrapper. Calling it again with the same request rejects the existing output directories. Do not delete or rename those directories to make a new wrapper run. Do not issue `prepare` again.

## Resume only a safely closed boundary

Direct existing cohort commands are conditional recovery routes, not instructions to run while the current launcher is active. The coordinator must first establish the original owner and children are finished, absence of a cleanup/stop blocker, an exclusive new window, unchanged frozen inputs, and the exact saved phase. Preserve a separate recovery receipt binding the previous state/hash and the actual new window; do not rewrite the old isolation note as if it described the new execution.

```sh
source /workspace/scratch/58d2a6adf1c3/task07-toolchain/env.sh
export PYTHONPATH=/workspace/scratch/58d2a6adf1c3/task07-toolchain/python
B23_CONTROLLER=/workspace/scratch/58d2a6adf1c3/.worktree/Task-07-B23-finish-f889-linux/NativeWeave/src/Benchmarks.Domain/cohorts.py
B23_OUTPUT=/workspace/scratch/58d2a6adf1c3/task07-b23/operating-point-cohorts-retirement-f889
```

The controller is `/workspace/scratch/58d2a6adf1c3/.worktree/Task-07-B23-finish-f889-linux/NativeWeave/src/Benchmarks.Domain/cohorts.py`; the existing output is `/workspace/scratch/58d2a6adf1c3/task07-b23/operating-point-cohorts-retirement-f889`.

- If search is incomplete at a safely closed boundary and the next unrecorded unit directory does not exist, `python3 "$B23_CONTROLLER" search --output "$B23_OUTPUT"` skips all unit IDs already recorded in `search` and starts only unstarted units. In the current execution, all eight search units are complete and the selected profile is frozen, so **do not run search again**.
- If selection is frozen, no blocker exists, and the next invocation was never started, `python3 "$B23_CONTROLLER" matrix --output "$B23_OUTPUT"` preserves completed case states (`completed-confirmation`, `retained-adverse-calibration`, `retained-incomplete-confirmation`) and skips them. A recorded valid calibration is reused for its still-unstarted confirmation, with its exact summary hash rechecked. An invalid calibration retains an explicitly unexecuted confirmation. No completed case is rerun to improve its outcome.
- When the matrix is terminal, `python3 "$B23_CONTROLLER" report --output "$B23_OUTPUT"` only analyzes the retained observations. It does not run applications or new benchmark cells. Read and reuse an existing valid final report first; analysis does not establish missing runtime cleanup.

## Active-invocation interruption is not automatically resumable

If an invocation output directory exists but the corresponding invocation was not recorded, the existing controller returns `interrupted-existing-directory` and records a cleanup blocker. A directory with an inner final summary alone is not automatically adopted. A `running` inner summary, an explicit stop, uncertain cleanup, source mismatch or existing cohort `execution_blocker` prevents all later measurement invocations. Preserve these observations and reconcile the exact exit/ownership/receipt gap independently; do not clear blockers, retry the same invocation, infer completed durations, or relabel a failed cohort. The controller has no generic resume-from-the-next-process option inside an interrupted calibration/confirmation invocation.

A browser connection interruption can leave the existing retained launcher progressing normally. Continue reading it in that case; it is the least disruptive way to preserve all completed and in-flight work.
