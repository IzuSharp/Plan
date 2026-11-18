# B23 corrected-artifact execution checkpoint

Status: the exact reviewed controller and all corrected application artifacts are ready. No operating-point search, fresh calibration, or confirmation measurement has started. Wait for the root executor to release the B22 load/build window before executing the commands below.

## Immutable inputs

- Controller worktree: `/workspace/scratch/58d2a6adf1c3/.worktree/Task-07-B23-finish-f889-linux/NativeWeave`, commit `9406093`.
- Predeclared plan: `src/Benchmarks.Domain/operating-point-plan-v1.json`. Independent review approved the narrowed, finite search; do not add rates or retry candidates after observing results.
- Corrected B21 application source: `1566ea4260ddf53dd8314aa983a75c49025547ca`, independently reviewed. The remote integrated source is `f4068469b9bb9a6cda6eaa64949a19aa2efb3331`.
- Ordinary package consumer: `/workspace/scratch/58d2a6adf1c3/task07-package-probe/retirement-1566ea4-f889`.
- Ordinary consumer progress SHA-256: `499cb7b70a76554ce7e33e292988b08199ef946341d7f703199c6d5a6ebd3b09`.
- Diagnostic/DI artifact manifest: `/workspace/scratch/58d2a6adf1c3/task07-b23/instrumented-retirement-1566ea4-f889/manifest.json`.
- Comparator manifest: `/workspace/scratch/58d2a6adf1c3/.worktree/Task-07-B23-comparators-linux/NativeWeave/src/Benchmarks.Domain/comparators/comparators.json`.
- Readiness receipt: `corrected-artifacts-readiness.json`, SHA-256 `aa4426a9b2be02b59f3413e089046046a25c32039e33d18e77b5d76690042244`.

The ordinary JIT/AOT and diagnostic Release/Debug builds are complete. Exactly three application files changed: `DatabaseService.cs`, `Maintenance.cs`, and `OutboxWorker.cs`. All 12 accepted NuGet package hashes, three native-module hashes, TLS inputs, and comparator files remain unchanged. B22 owns the focused correctness and resource regression; previous B21 acceptance is retained at its original identities.

## First execution after root grants the exclusive window

Run from the controller worktree above. Replace the isolation note with the actual root-granted window and observed absence of overlapping build/fault loads. This note is evidence, not a substitute for coordination.

```sh
source /workspace/scratch/58d2a6adf1c3/task07-toolchain/env.sh
export PYTHONPATH=/workspace/scratch/58d2a6adf1c3/task07-toolchain/python

python3 src/Benchmarks.Domain/cohorts.py prepare \
  --package-probe /workspace/scratch/58d2a6adf1c3/task07-package-probe/retirement-1566ea4-f889 \
  --comparators /workspace/scratch/58d2a6adf1c3/.worktree/Task-07-B23-comparators-linux/NativeWeave/src/Benchmarks.Domain/comparators/comparators.json \
  --instrumented /workspace/scratch/58d2a6adf1c3/task07-b23/instrumented-retirement-1566ea4-f889/manifest.json \
  --postgres-bin /workspace/scratch/58d2a6adf1c3/task07-toolchain/postgres/bin \
  --isolation-note 'REPLACE WITH THE ACTUAL EXCLUSIVE EXECUTION WINDOW' \
  --output /workspace/scratch/58d2a6adf1c3/task07-b23/operating-point-cohorts-retirement-f889

python3 src/Benchmarks.Domain/cohorts.py search \
  --output /workspace/scratch/58d2a6adf1c3/task07-b23/operating-point-cohorts-retirement-f889

python3 src/Benchmarks.Domain/cohorts.py matrix \
  --output /workspace/scratch/58d2a6adf1c3/task07-b23/operating-point-cohorts-retirement-f889

python3 src/Benchmarks.Domain/cohorts.py report \
  --output /workspace/scratch/58d2a6adf1c3/task07-b23/operating-point-cohorts-retirement-f889
```

Keep the long-running orchestration session alive and retain its output. Inspect `cohorts.json` between stages; do not run the next stage if cleanup, isolation, or input validation blocks continuation. Interrupted directories are not authorized retries. A source or frozen-input change requires a new output directory and honest provenance.

## Finite scope and reporting

The approved search is 72 process measurements over the previously invalid workload families, with no additional tuning. The unchanged original 30-case matrix has at most 198 calibration and 198 eligible independent confirmation process measurements. Failed/invalid calibration cases retain their adverse observations and explicitly skip confirmation; they cannot support a performance claim. Original high-rate failures and unavailable native allocator/FFI/copy measurements remain explicit.

After actual measurement, use `export_measurements.py` in this directory to create a new allowlisted numeric export. Review it before the root executor copies it into Plan. Do not upload the old 4.5 MB adverse raw report, old rejected binary/trace archives, private keys/configurations, database files, or HTTP bodies. The prior concise adverse numeric summary is already retained by the root executor.

B23 does not claim 24-hour or 72-hour validation. Those durations are deferred by the user's current instruction. B24 and final release acceptance remain root-owned downstream work.
