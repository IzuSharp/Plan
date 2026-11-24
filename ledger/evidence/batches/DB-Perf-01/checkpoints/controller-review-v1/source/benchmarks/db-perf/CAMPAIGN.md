# DB-Perf-01 Linux campaign controller

This directory contains an executable campaign path, not a completed performance
claim. The checked-in request is disabled. The batch ledger and accepted evidence
live in `IzuSharp/Plan`, `ledger/evidence/batches/DB-Perf-01/handoff-linux.md`.
Only observations actually recorded on the admitted VM can receive long-segment
credit. Eight observed segments do not establish whole-framework zero allocation,
complete native-memory instrumentation, package publication, or batch completion.

## Inputs and preparation

`campaign-request.json` freezes the original main commit, final package-producing
commit, successful normal CI runs, provider artifact IDs, ZIP/package/native
SHA-256 values, consumer commit, workload bytes and case sequence. The original
main is `771bc77cbd68d3f932b99ed2497c0697bbba5f02`. PostgreSQL and SQLite remain
independent packages. An artifact is accepted only after its original unsigned
package entries, producer manifest, source commit and Git tree agree.

The harness commit is frozen before the opt-in request is enabled. A later request
commit may change only the request within the benchmark source directory; all
compiled benchmark inputs must remain tracked and identical to the frozen
commit. The preparation job downloads the four original candidate artifacts,
publishes identical ordinary external C# applications against before/after
`PackageReference` inputs, publishes the independent ORM applications, and builds
the direct C++ comparator with the locked compiler and drivers. Source files,
restore graphs, generated Dapper mapping sources when available, build logs,
package manifests and runtime hashes accompany the relocatable bundle.

The original and optimized applications use the same consumer source and project
bytes. Their package versions are command-line properties, rather than edits to
the consumer project. A package's native source commit may be older than its C#
source commit when the normal build legitimately reuses an unchanged native input;
the exact native payload hash remains required.

Commands below validate or prepare inputs. A disabled request cannot start a
preparation or a measurement:

```bash
python3 benchmarks/db-perf/campaign.py validate-request benchmarks/db-perf/campaign-request.json --allow-disabled
python3 benchmarks/db-perf/test_controller.py
python3 benchmarks/db-perf/campaign.py prepare \
  --request benchmarks/db-perf/campaign-request.json \
  --repo "$GITHUB_WORKSPACE" --output "$RUNNER_TEMP/db-perf-prepared"
```

Preparation requires read-only GitHub Actions artifact access through `gh` and the
repository's pinned toolchain/PostgreSQL installation. It runs in a separate job,
outside all timing boundaries. No credential is written to the bundle.

## Dedicated measurement environment

`.github/workflows/db-perf-campaign.yml` currently has only a manual dispatch
trigger. The final reviewed opt-in may add a task-branch push trigger restricted
to `campaign-request.json`; ordinary pull-request CI must remain short. The
measurement job has a 360-minute timeout. All eight sequential long steps run in
that single job and therefore on the same hosted VM. Every step uploads a distinct
checkpoint artifact, so a later failure cannot delete an earlier checkpoint.

The controller admits Linux x64 on a GitHub-hosted VM only after recording its
boot ID, image version, CPU model, visible CPU set, quotas, throttling counters,
memory limits, idle CPU and steal. Client, PostgreSQL server and observer CPU
affinities are disjoint. SQLite runs inside the client process. Both preparation
and measurement must report the same image version. Runtime ELF dependencies are
resolved and hashed on the measurement VM; consumers additionally hash their
actual dynamically loaded provider or SQLite library. Physical-host exclusivity
is not asserted merely because the guest job is dedicated.

A failed idle admission is retained and cannot be bypassed with `--resume`.
Independent before processes must also pass the frozen noise limit. Guest quota
changes, throttle events, excessive total/interval steal, uncertain CPU counters
or failed error/tail criteria prevent a long observation from qualifying.

## Workload and comparison boundaries

Each process starts from a hash-bound snapshot created through the before public
consumer. PostgreSQL starts with fixed durability/isolation/settings and reserves
administrative connections beyond the maximum client concurrency. SQLite copies
the same seed files. Startup, initialization, warmup, calibration, drain and idle
observations are separate from the requested 1,800 seconds of offered load.
Every accepted request is drained after the offered interval, and that drain time
remains visible in throughput and scheduled latency.

After a successful, fully validated process and joined database owner, the
controller records the private database clone's file hashes and sizes and retires
that reproducible clone. This bounds disk/WAL retention across the many independent
processes. The immutable seed and every source, binary, result, resource sample and
owner receipt remain. Failed attempts retain their database copy for investigation.

The case sequence is identical across routes. Per-case started/succeeded/failed
and row totals must reconcile with the process totals. Declared cases with no
accepted execution may remain in an overload diagnostic, where every rejection
is retained. A qualifying long segment must actually execute all frozen cases.
Mixed-write IDs must be backed by `writesDatabase: true` in the workload manifest;
a read-only case cannot receive a write label in the request to pass this gate.

The primary prepared C++ column reuses physical statements and performs the
driver's ordinary complete result drain. Dynamic C++ constructs and prepares each
operation. It does not inherit Korda's extra protocol-confirmation traffic merely
to make the gap smaller. Explicit short native layers separately measure
per-operation preparation and product-style confirmation, so their contribution
can be isolated. SQL executions, libpq submissions and confirmation calls remain
separate counters; none is relabeled as a physical network round trip.

The calibration has distinct purposes:

1. Independent processes interleave the four routes to estimate before-process
   noise on the admitted VM.
2. A single-connection and concurrency ramp measures closed-loop service latency.
   It is explicitly a capacity estimate and not a scheduled-latency throughput
   limit.
3. A scheduled-rate grid runs at the frozen long concurrency and the best
   concurrency observed in the closed-loop ramp. It reports the highest observed
   success throughput satisfying the same error/rejection and scheduled-p99
   thresholds. The finite grid is retained; it is not a proof of a global maximum
   over every possible concurrency or arrival rate.
4. The common sustainable rate is frozen using the before, native and independent
   ORM results at the actual long concurrency. The optimized route cannot lower
   its comparison load after a regression. Every route then runs at that rate,
   overloads, and returns to that rate.

Current overload/recovery commands are separate processes. They demonstrate
fresh-process recovery after overload; they do not establish recovery of the
same saturated pool without a process restart. That remaining obligation must
be reported or fulfilled separately.

The shared managed scheduler and native scheduler use `ceil(rate * seconds)`
planned arrivals, absolute deadlines, a bounded FIFO, non-waiting admission and
explicit rejection. Counters retain planned, attempted, sent, started, successful,
failed, rejected and retried requests. Four histograms retain service latency,
successful scheduled latency, all completed scheduled latency including failures,
and start delay. Per-second and per-case ledgers are independently reconciled.
No queue or harness allocation is blindly subtracted from measured totals.

## Measurement, interruption and reuse

`run.py` is also usable for a short frozen command plan. It does not independently
qualify a host or grant long credit:

```bash
python3 benchmarks/db-perf/run.py plan.json --output /absolute/fresh/evidence --sample-seconds 0.5
```

It retains stdout, command receipts, raw resource samples, process identity and
OS `wait4` lifetime CPU/peak RSS for successful and failed commands. Every command
has a finite deadline. Exceptions and timeouts terminate, kill if necessary, and
join the owned client. PostgreSQL shutdown also has a bounded join; an unretired
owner aborts the campaign. Result files cannot overwrite another command's
output or observer evidence.

CPU/RSS/PSS samples have acquisition start/end times and PID start identities.
Steady summaries use only complete sample intervals inside the application's
recorded monotonic boundary; unsampled edges are not extrapolated. Process-tree
samples remain explicitly non-atomic. Missing RSS/PSS is unavailable, not zero.
OS lifetime CPU/peak RSS, sampled steady peaks, application-reported CPU, native
allocator observations and idle retention are distinct measurements.

After unpacking the immutable runtime bundle, the workflow uses:

```bash
python3 "$DB_PERF_BUNDLE/harness/campaign.py" measure \
  --bundle "$DB_PERF_BUNDLE" --output "$RUNNER_TEMP/db-perf-campaign" --short-only
python3 "$DB_PERF_BUNDLE/harness/campaign.py" measure \
  --bundle "$DB_PERF_BUNDLE" --output "$RUNNER_TEMP/db-perf-campaign" --resume --next-segment
```

Repeat the second command for the eight segments on the same still-running VM.
Resume requires identical request, bundle, source hashes, image and boot/job
identity. Every reused normalized result rechecks its raw result, stdout, command,
resource samples, plan and controller hashes. A partial attempt does not silently
rerun. A reviewed retry on the same live VM requires an explicit step and reason,
is bounded by the frozen attempt limit, and retains the previous attempt:

```bash
python3 "$DB_PERF_BUNDLE/harness/campaign.py" measure \
  --bundle "$DB_PERF_BUNDLE" --output "$RUNNER_TEMP/db-perf-campaign" --resume \
  --retry-step postgresql/long-korda_after --retry-reason "Recorded investigation of the retained failure"
```

A qualifying long result cannot be replaced with a preferred sample. Successful
calibration samples cannot be retried to improve the noise estimate. Lost owner
retirement receipts require investigation instead of a retry. A new VM needs a
new campaign; observations remain available for analysis but are not rebound to
the new environment. The controller reserves the end of the six-hour job for
drain and artifact upload, and refuses a new measurement that exceeds its finite
campaign budget.

## Acceptance remains in Plan

The campaign's final state is `long_campaign_observed_batch_acceptance_separate`.
`wholeBatchAccepted` remains false. Public allocation coverage, narrow regression
proofs, cancellation and failure paths, native whole-heap metrics, same-pool
recovery, SQL/plan review, normal CI/review/merge, automatic preview and actual
public-package AOT verification must be reconciled in Plan before batch completion
is claimed. The controller does not turn missing measurements into zeros or use
document generation as evidence of execution.
