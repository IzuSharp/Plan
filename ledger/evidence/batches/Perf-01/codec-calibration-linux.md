# Perf-01: common codec capacity controller

Status: source-only parameterization, not executed by its author. Root owns the next calibration window and the final before/after/direct selections. The codec driver and product implementation are unchanged.

`codec_calibrate.py` derives from the existing scratch `ROOT/perf01-run/calibrate-codec-v3.py` (SHA-256 `9948a1c64692eab0353b3c72c3010b30e254a984f8959fec710dc6b4e1754246`) and its `final003` binding/exit-code correction (`2bfb8f97921d6604745e52e0c43670280cf8f8209e9341afefc714268013d51f`). It makes product checkout, producer manifest, variant, corpus, policy and fresh output explicit arguments. It does not introduce a new scheduler, process supervisor or timing implementation.

## Preserved algorithm and gates

The command remains the ordinary committed `tests/Perf01.Codec/driver.py run`: two dedicated workers; mixed 160-action cycle; queue64/inflight256; target CPUs2,3 and generator CPUs0,1; deadline1000ms; maximum dispatch lag100ms; 5s warmup, 4s recovery at1/s and 5s idle. Every stage has a fresh target process. The wrapper never filters a case/action/interface or changes the corpus, algorithm, format, level or limits.

The policy-4 sequence remains: start at the lowest listed codec rate; use30s stages; double beyond the listed ladder while the original finite extension bound allows; bisect the first failing/highest passing bracket until its width is at most10% or one operation/s; require three fresh60s confirmations; if any fail, step down10% and reconfirm for at most ten rounds. Reaching the extension bound without a failed high point yields a measured lower bound. A generator failure never establishes the application's capacity upper bound.

The inherited extension check uses `rate * 30 <= 1,000,000`; it does not by itself prove that a subsequent60s confirmation has at most one million observations. Keep this limitation explicit if an extreme all-passing extension approaches that boundary: it cannot establish policy-compliant capacity beyond the frozen finite bound. The current codec bracket around336/s is far below it. This source-only parameterization leaves the existing algorithm intact; it does not authorize a larger observation population or reinterpret a boundary failure.

A point qualifies only when the driver process exits0, `valid`, service standard and recovery standard are all true, successful arrival p99 is available and at most500ms, and observed measurement-window target RSS is available and at most256MiB. This is the original v3 result rule plus the already-required exit0 check. Actual outcome/error/throughput/CPU/p99/RSS fields remain in `controller.json`; every full cell is retained. Resource rows are read incrementally after the child exits, using the same scheduled interval and maximum as v3.

Only `--variant before` derives the prospective paired long rate: floor80% of the confirmed point, at least1/s and capped at500/s. `after` and `direct` use the same capacity algorithm but record no new paired long rate. The fixed long and short comparison rates continue to come from the frozen before selection.

## Identity and lifecycle

The supplied policy/build/corpus digests are checked before any child is started and between cells. The exact Python3.12.14 executable, boot identity and inherited service CPU mask are checked. The prepared manifest's codec source inventory and A21 digest must match the current driver checkout. Before requires clean ea5 runtime source; after is allowed to name its different clean product commit. The existing driver still rehashes all actual binaries/packages/consumer inputs/corpus payloads and validates loaded native mappings. Each returned cell must identify the supplied producer/corpus/driver/A21/route before the wrapper accepts its result.

A fresh output directory is mandatory. The wrapper checkpoints each command before launch, final exit/result fields afterward, and caught exceptions as `interrupted-or-failed`. Missing final evidence stops the controller and preserves partial files. A Python timeout kills/reaps its immediate driver through `subprocess.run`; it does not prove all descendants retired. SIGTERM or an externally forced wrapper termination can leave a `running` receipt and live known descendants. Root must inspect and stop any survivors before reusing measurement resources. These are the existing thin-controller lifecycle limits; the wrapper does not claim an additional supervisor or automatic resume. Do not rerun into an existing directory or promote an incomplete cell.

## Exact fresh before-004 command

This command was prepared from source only. Run it when root has the exclusive measurement window. `PERF01_ROOT` is the task root; `PERF01_PLAN` is the integration Plan checkout and `PERF01_PRODUCT` is the unchanged driver checkout. The literal SHA values below bind the actual current inputs rather than recomputing a new identity at launch.

```sh
export PERF01_ROOT=/workspace/scratch/01c249676f47
export PERF01_PLAN="$PERF01_ROOT/.worktree/Perf-01-linux/Plan"
export PERF01_PRODUCT="$PERF01_ROOT/.worktree/Perf-01-linux/NativeWeave"
source "$PERF01_ROOT/perf01-toolchain/env.sh"
taskset -c 2,3 /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  "$PERF01_PLAN/ledger/evidence/batches/Perf-01/codec_calibrate.py" \
  --nativeweave "$PERF01_PRODUCT" \
  --policy "$PERF01_PLAN/ledger/evidence/batches/Perf-01/prospective-policy.json" \
  --policy-sha256 0c7cd866b1ad0fc86d647e31dd1b6fe0b148d2e7ca54d83b7286cec09f11cafc \
  --variant before \
  --build "$PERF01_ROOT/perf01-codec-checks/package-before-004/manifest.json" \
  --build-sha256 d34298ebc8dc82b525f19860555947a1a04eff2bf8aecc38cede2922c81285a7 \
  --corpus "$PERF01_ROOT/perf01-codec-checks/corpus" \
  --corpus-sha256 92932f7ecba2b3a7104b19344d22a42c3c40605f23eb158a0941d48bfff0465d \
  --output "$PERF01_ROOT/perf01-evidence/calibration/before-codec-final004"
```

For `after`, supply the fresh actual after manifest/digest and a new output. For `direct`, use the frozen before-004 direct miniz fixture/manifest with `--variant direct` and a new output. Keep the same policy, corpus, driver source and resource layout. Supplementary .NET ZLibStream remains limited to the separate valid-corpus comparison; this wrapper does not rank it as a strict bounded-operation capacity comparator.

The before-004 producer is documented in [builds/before-codec-004](builds/before-codec-004/README.md): clean runtime ea5, driver `aa3399f0418a6d0910cc56697abfaa3769f32b54`, A21 `dfb57cf6f09b3c585e886d97d7653d938d3eebf907e741c1400b23890461db53`. No old before-003/002 calibration is relabeled by this wrapper. Final formal cells still require the separate completed freeze and appropriate validity/retention checks.


## Review disposition

Root and the database agent independently read the wrapper against the existing v3/final003 command/selection loop and current codec driver schemas. No blocking source issue was found in the stated policy-4 measurement range. The review specifically retained exit-code qualification, immutable input/actual cell binding, all-three confirmations, before-only paired long selection, and the documented finite-extension/interruption limitations. These were source reviews: neither reviewer nor the author executed this new wrapper, tests or a load during the active database calibration. Root will run CLI/finite gates at the next non-timing boundary before executing fresh before-004 calibration.
