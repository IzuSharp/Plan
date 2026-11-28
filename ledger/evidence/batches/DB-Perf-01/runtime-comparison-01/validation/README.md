# Existing static gates: actual outcomes and scope

No benchmark, calibration, profiling, load, or build was invoked by these checks.
No existing verifier, historical acceptance record, graph, schema, or CI workflow
was modified to accommodate the new recording task.

## Current-branch invocation: preserved failure

The requested old command was actually run on the current Plan worktree with
its optional frozen-history flag:

```text
python3 tools/verify_db_perf.py --verify-frozen-history
```

It exited 1 in `validate_history`, before entering the optional frozen-history
worktree. Its error is `Unrelated/historical input changed`. The complete
[receipt](plan-static-01/receipt.json), [stdout](plan-static-01/stdout.log), and
[stderr](plan-static-01/stderr.log) are preserved.

The old verifier restricts every path changed since
`bc1956936ee77a997a016856c97def6aabc0bbc6` to its historical allowlist.
The following disallowed paths are **identical on the task's published parent
and the unchanged starting main `03efe57ffbe3046bd89919ddb2c16c90a377954d`**:

- `.github/workflows/logical-admission-plan.yml`
- `.github/workflows/native-slices-checkpoint.yml`
- `.github/workflows/research-assets-reference-migration.yml`
- `.github/workflows/rust-1100-align.yml`
- `.github/workflows/source-driven-recovery.yml`
- `.github/workflows/verify-merged-design.yml`
- `CURRENT-PHASE.md`
- `README.md`

This is the old command's scope on the already existing main history, not a
failure of a new timed workload. The failure is not suppressed or relabelled.
The task does not widen the historical allowlist, revert main history, or change
the verifier to manufacture a pass.

## Existing CI's actual immutable performance-record input: passed

The unchanged `.github/workflows/native-slices-final-check.yml` explicitly checks
out Plan commit `38f8ce8a01f88e6e4c4459926f197c5438c2f6fc` for its historical
performance-record gate. A fresh detached local worktree at that exact commit
ran the exact command `python3 tools/verify_db_perf.py` and exited **0**.
The worktree was removed normally afterward. See the complete
[execution receipt](plan-historical-perf-01/receipt.json) and
[gate output](plan-historical-perf-01/gate.stdout.log).

That immutable input correctly retains `state=in_progress`,
`accepted_long_segments=0`, 13 negative controls and four source-reference
negative controls. Those are its historical facts, not the current eight-cell
campaign. No new performance acceptance is inferred from a document gate.

The new campaign is checked separately by the local analysis, exact raw archive
readback and independent final review. Its strict state remains seven passes and
one reviewed released-idle deviation, with eight valid 1,800-second business
windows. These local tools are not attached to CI.

## Product impact before publication

The exact required command was run again in the unchanged Korda worktree:

```text
python3 eng/ci/impact.py origin/main --output artifacts/plan.json
```

It exited 0. Korda's committed HEAD equals its observed `origin/main`; both Korda
and Korda-Design have empty working and committed diffs. The impact selected no
actions, modules, top-level packages, public checks or releases. Thus there are
no affected product packages to validate in parallel or publish for this record.
The [actual plan](final-korda-impact.json) and
[identity/selection receipt](final-korda-impact-receipt.json) retain the exact
output and explain why zero is the expected selection.

## CI observation

The frozen input commit's CI run `46126507300` was cancelled while checking out
the immutable DB-Rename-01 input; its first historical performance-record gate
had passed and later historical steps were skipped. Original metadata and logs
are under [ci/frozen-dc048-01](../ci/frozen-dc048-01/receipt.json).

The final result commit's head and CI outcome are recorded in the body of
[Plan #37](https://github.com/IzuSharp/Plan/pull/37), after publication. A local
gate pass is not presented as a GitHub Actions pass.
