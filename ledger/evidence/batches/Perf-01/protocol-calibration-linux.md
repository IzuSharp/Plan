# Perf-01: common HTTP/gRPC short calibration command loop

`protocol_calibrate.py` parameterizes the existing
`ROOT/perf01-run/calibrate-apps-v4.py` protocol loop for **before**, **after** and
**direct** producers. It invokes the same committed `tests/Perf01.Protocols/run.py`
`prepare` and `run` commands. It adds no server, client, scheduler, lifecycle
supervisor or resume mechanism. This document and wrapper were prepared from
source; they are not an executed calibration result.

## Frozen behavior

Policy revision 4 supplies the original rates, 30-second stages, three fresh
60-second confirmations, at most ten confirmation rounds, and five seconds of
post-load idle. The loop extends a fully passing ladder by doubling, refines the
first passing/failing bracket to at most 10% or adjacent integer rates, and steps
down by 10% after a failed confirmation triplet. Every triplet executes all three
processes; it does not stop after the first failure and select favorable rows.
The existing driver rate/one-million-operation bounds limit extension; an
unbracketed result is reported as a measured lower bound.

Both groups use 64 client slots, service CPUs 2,3 and generator CPUs 0,1. Profiles
are the reviewed mixed `profile-v1.json` (HTTP) and
`grpc-budget-profile-v2.json` (gRPC), pinned by SHA-256 in the wrapper. Only their
idle duration is changed to five seconds for calibration. TLS files, connection
reuse, four H2 connections, 32 streams/connection, data/mix, resource budgets,
100-ms dispatch-lag limit and 500-ms/256-MiB/zero-unexpected-error standard remain
unchanged. The gRPC request budget remains 64 MiB while HTTP retains 4 MiB.
Direct Rust's actual-frame credit accounting difference remains a comparison
qualification; see `grpc-baseline-quota-observation.md`.

A selected cell must have **process exit 0**, a completed result, `valid == true`
and `service_standard_met == true`. The original result and all invalid cells
remain visible. `successes`/`throughput` count successful logical checks,
including declared probes; `business_successes`/`business_throughput` separately
report ordinary successful calls. Capacity is the highest consistently passing
sampled offered rate. Generator-limited failures do not establish a server
capacity upper bound.

Only a **before** selection emits `long_rate = max(1, min(500, floor(0.8*rate)))`.
After/direct capacity results cannot retune the paired long load. Actual long
runs invoke the existing domain driver directly, one group at a time, with the
independent long-duration proof.

## Exact before invocation

Run only when root owns the complete exclusive resource window. These are the
actual existing before server/common-client and policy identities; choose a new
attempt label if the named output already exists.

```bash
PERF01_ROOT=/workspace/scratch/01c249676f47
source "$PERF01_ROOT/perf01-toolchain/env.sh"
PERF01_PRODUCT="$PERF01_ROOT/.worktree/Perf-01-linux/NativeWeave"
PERF01_PLAN="$PERF01_ROOT/.worktree/Perf-01-linux/Plan"
PERF01_PYTHON=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
taskset -c 2,3 "$PERF01_PYTHON" \
  "$PERF01_PLAN/ledger/evidence/batches/Perf-01/protocol_calibrate.py" \
  --nativeweave "$PERF01_PRODUCT" \
  --policy "$PERF01_PLAN/ledger/evidence/batches/Perf-01/prospective-policy.json" \
  --policy-sha256 0c7cd866b1ad0fc86d647e31dd1b6fe0b148d2e7ca54d83b7286cec09f11cafc \
  --build "$PERF01_ROOT/perf01-build/before/protocols-v2/build.json" \
  --build-sha256 818643898f04803f3070cb55f6bf0894dc23c1f9c21ff7d556a8e99b6b96d8c3 \
  --client-build "$PERF01_ROOT/perf01-build/before/protocols-v2/build.json" \
  --client-build-sha256 818643898f04803f3070cb55f6bf0894dc23c1f9c21ff7d556a8e99b6b96d8c3 \
  --certificate "$PERF01_ROOT/perf01-evidence/functional/before-grpc-001/certificate.pem" \
  --private-key "$PERF01_ROOT/perf01-evidence/functional/before-grpc-001/private-key.pem" \
  --exclusive-lock "$PERF01_ROOT/perf01-evidence/timing.lock" \
  --variant before --groups http grpc --attempt v5 \
  --output-root "$PERF01_ROOT/perf01-evidence/calibration"
```

For direct Rust, keep the common client, policy, TLS and profiles identical;
change `--variant` to `direct` and select
`ROOT/perf01-build/direct/protocols-v3/build.json`, whose existing SHA-256 is
`0f6fb40d3310e873231276527ffac3621980981b719b6fc438ee03e5fdf1bdbf`.
For after, use `--variant after` and the actual newly built after `build.json`
with its recorded SHA-256. The wrapper rejects a build with the wrong route or
ISA, an ineligible build, a dirty NativeWeave runtime producer, or a before
producer that is not the fixed `ea5` main. The common client remains the original
before Native AOT build. Existing driver preparation verifies its full artifact,
fixture-source, lock and package/producer closure hashes before running a cell.

Use `--groups http` or `--groups grpc` to select just one pending group. A new
attempt always starts its group's declared ladder from the low point; no
incomplete prior sequence is silently resumed or credited.

## Receipts, interruption and review limits

The wrapper writes `VARIANT-GROUP-ATTEMPT/controller.json`, per-command logs,
unchanged driver cell directories and a completed `selection.json`. The
controller pins policy, driver/helper source, build manifests, TLS identities,
profile bytes, host boot and CPU layout, and checks them between cells. Final
result/plan hashes bind the actual producer selected by preparation. Private key
bytes are never printed or copied into Plan; local path and hash metadata are
recorded.

Root must keep exclusive ownership across preparation and the entire command
loop, including gaps outside each driver's file lock. This thin subprocess
wrapper deliberately retains the existing interruption model: **SIGTERM or a
forced wrapper termination may leave an active driver/adapter process**. A
caught exception records a partial controller where possible, but is not proof
that descendants were reaped. After any interruption, root inspects and stops
the known supervised process tree, preserves partial evidence and confirms the
measurement resource is clear before another load. There is no automatic retry
or ownership-recovery claim.

No test, syntax execution, calibration, build or application load was performed
by the source author while preparing this wrapper. Root will run finite gates
when the resource window permits. The script must be reviewed and its final
bytes frozen before it is used for formal selection.

The codec agent independently reviewed the source against the actual protocol
driver, both producer schemas and the original apps-v4 loop. Its bounded review
passed the command, producer/common-client binding, finite confirmation bound,
exit/validity/SLO selection and interruption scope. The reviewer also performed
no execution, build or application load.
