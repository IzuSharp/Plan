# Perf-01 completed protocol cohorts and comparison

Status: source-prepared utilities and finite synthetic test source. Neither the
extractor, its tests, nor the short-cohort controller was executed by the protocol
author during preparation. These files contain no claimed before/after results.
Root owns finite utility tests, exclusive measurement resources, actual execution,
and publication of the resulting evidence.

`protocol_compare.py` is an offline reader. It never starts a server, client, or
load. `protocol_cohorts.py` is an optional serial execution entry point using the
existing immutable package-built fixtures and driver. Root may instead execute
one cell at a time and supply the resulting explicit directories to the offline
reader. Neither utility grants capacity or 30-minute acceptance.

## Exact comparisons and units

The six ordinary partitions in `protocol-layered/catalog.json` cover HTTP/1.1 and
HTTP/2 tiny, completed 1 MiB upload/download, completed 8 MiB upload/download,
two unary payload sizes, and all three streaming gRPC cardinalities. They use
the same before-v2 common client, exact TLS certificate, service CPUs 2,3 and
generator CPUs 0,1. Each partition has client concurrency four. The gRPC-only
64 MiB per-request budget is selected prospectively in
`grpc-budget-profile-v2.json`; HTTP retains 4 MiB. Both global payload caps remain
64 MiB and the RSS cap remains 256 MiB. See
`grpc-baseline-quota-observation.md` for the preserved old-cap rejection and the
existing direct-Rust versus NativeWeave frame-reservation difference.

The key is the complete frozen Oracle token:
`scenario|protocol|configured_payload_bytes|configured_messages`. Thus HTTP/1.1
and HTTP/2, 1 MiB and 8 MiB, and unary versus stream shapes cannot silently merge.
Each actual process gets ordinary successful arrival mean, p50, p95, and p99;
planned/dispatched/admitted counts; controller outcomes; independent client
outcomes; calls/s; request/response messages/s; and actual request/response
payload and encoded byte totals and rates. A process needs at least 100 successful
ordinary observations for each row to enter comparative interpretation. Failed
or incomplete explicitly supplied cells remain visible and make the comparison
inconclusive. The tool never averages only the two favorable members of a
three-process cohort.

Arrival latency uses the existing A21 controller clock from scheduled arrival
to observed completion. Successful business bytes/messages require both an
on-time A21 `ok` and the independent client's correct ordinary result. A response
prefix observed before an expected cancellation remains in raw totals but is
excluded from successful business throughput. Expected cancellation/deadline
probes have their own rows. Protobuf encoded bytes exclude the five-byte gRPC
envelope, HTTP/2 frames, and TLS; HTTP encoded-protobuf fields are zero.

Each scenario rate uses its process's **whole measurement window**. It is that
scenario's contribution to the selected partition, not standalone capacity.
The same denominator includes ordinary failures and dispatched work. The output
retains all independent process metrics and uses equal-weight arithmetic means
for a compact comparison. A mean of three process p99 values is labeled exactly
that: it is not a pooled p99 or a p99 confidence interval. Whole-profile
server/client/adapter/controller CPU, sampled peak RSS, available descriptors and
thread counts are separate. Per-scenario CPU/RSS/GC are unavailable.

Managed allocation is the existing approximate
`GC.GetTotalAllocatedBytes(false)` delta over the observed measurement-phase
snapshot bracket. The reader records that bracket and its actual duration;
allocation MiB/s uses the bracket, not the entire scheduled cell. Leading or
trailing fractions of a second may be absent. It does not turn that delta into
exact allocation per call. Direct Rust's managed GC is N/A. Existing fixture
preallocated memory remains included in RSS; no inferred subtraction is made.

## Before-only noise and fresh interleaving

Before any product edit, collect three independent **before-only** processes for
each exact partition/configuration. For each ordinary row, freeze
`absolute_noise_ns = max(1000, range of the three process arrival means)` and
`relative_noise = 0`, with seed 20261119. The receipt records the actual profile,
Oracle, common client, fixture and driver file hashes, producing before package
closure, loaded native library, compiler/SDK/ISA/dependency/profile metadata,
and process identities and windows. It does not compare the whole driver git
HEAD, which can legitimately change for product edits or unrelated tests.

The direct producer's executable, source, locks and compiler settings are pinned
at this freeze, but direct timing samples do not influence the noise band. The
native Rust ISA remains generic x86-64-default, matching the before producer;
managed AOT and common client remain explicit x86-64-v2.

Commit the actual noise receipt/index SHA-256 values in Plan **before after
timing**. A local creation timestamp alone is not evidence that a band was
published before observing the candidate. Later comparison requires three fresh
before, three after, and three direct processes, disjoint from the noise
calibration processes. Suggested repetition order is before/after/direct,
direct/after/before, before/after/direct. The optional controller implements that
order and never reruns a failed cell automatically.

The offline reader rejects repeated result bytes, repeated actual server
PID/start identities, overlapping process measurement windows, changed workload
or measured driver bytes, differing before package content, changed before/after
toolchain settings, changed frozen reference, or mismatched externally supplied
noise SHA. It recomputes the declared before-only range from the stored process
means. It invokes the **unchanged A21 `noise_comparison`** only on the independent
process arrival means. p99, rates, CPU, RSS, and Rust gaps remain descriptive.
All percentage changes use `(new-old)/old*100`; zero or unavailable denominators
remain N/A. Direct gaps use direct Rust as the denominator.

These consistency checks do not reexecute correctness or prove that arbitrary
historical files were never edited. Existing evidence hashes are checked, and
all consumed inputs are newly hashed. Original producer metadata must remain
available or be restored byte-for-byte at `cell/bindings/build.json` and
`cell/bindings/native.json`. Raw logs and binary/producer archives remain part of
root's separately managed evidence retention.

## Commands after root releases the measurement resource

Use the actual integrated NativeWeave/Plan worktrees. The following assigns only
task-specific shell variables. Source the locked environment first; do not run
builds during the cohort. The final after build must already exist and have
passed the package/API/ownership gates described in the separate after recipe.

```bash
ROOT=/workspace/scratch/01c249676f47
source "$ROOT/perf01-toolchain/env.sh"
NW="$ROOT/.worktree/Perf-01-linux/NativeWeave"
PLAN="$ROOT/.worktree/Perf-01-linux/Plan"
E="$PLAN/ledger/evidence/batches/Perf-01"
PY=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3
BEFORE="$ROOT/perf01-build/before/protocols-v2/build.json"
DIRECT="$ROOT/perf01-build/direct/protocols-v3/build.json"
CERT="$ROOT/perf01-evidence/functional/before-grpc-001/certificate.pem"
KEY="$ROOT/perf01-evidence/functional/before-grpc-001/private-key.pem"
LOCK="$ROOT/perf01-evidence/timing.lock"
```

First execute the finite offline test only when root permits it. Its temporary
timestamps, process identities and values are explicitly synthetic and must
never enter measurement evidence:

```bash
PERF01_NATIVEWEAVE="$NW" taskset -c 8 "$PY" "$E/test_protocol_compare.py"
```

Before-only noise stage for all six C4 partitions (18 fresh processes):

```bash
taskset -c 8 "$PY" "$E/protocol_cohorts.py" \
  --stage noise --nativeweave "$NW" --catalog "$E/protocol-layered/catalog.json" \
  --before-build "$BEFORE" --direct-build "$DIRECT" --client-build "$BEFORE" \
  --certificate "$CERT" --private-key "$KEY" --exclusive-lock "$LOCK" \
  --output "$ROOT/perf01-evidence/protocol-short/noise-before-001"
```

Root must retain exclusive ownership across this entire invocation, including
offline extraction between cells: the existing driver acquires its file lock
for a cell, not for all controller postprocessing. Each execution uses the
existing `prepare` and `run` commands, with the service launched on 2,3 and
generators on 0,1. Results failing generation, correctness or the service
standard stop the controller and remain saved. A rate/profile replacement is a
new prospective choice and requires a new before-only noise stage for that
configuration; do not widen the old band from the failed comparison.

After the actual noise index and its SHA are saved in Plan, set
`PERF01_NOISE_SHA` to that **already committed** SHA and select the actual final
after manifest. The following placeholders are required inputs, not fabricated
receipt values:

```bash
PERF01_NOISE_INDEX="$ROOT/perf01-evidence/protocol-short/noise-before-001/noise-index.json"
: "${PERF01_NOISE_SHA:?Set the actual noise-index SHA already committed before after timing}"
: "${PERF01_AFTER_BUILD:?Set the actual final after protocol build.json path}"
taskset -c 8 "$PY" "$E/protocol_cohorts.py" \
  --stage compare --nativeweave "$NW" --catalog "$E/protocol-layered/catalog.json" \
  --before-build "$BEFORE" --after-build "$PERF01_AFTER_BUILD" \
  --direct-build "$DIRECT" --client-build "$BEFORE" \
  --certificate "$CERT" --private-key "$KEY" --exclusive-lock "$LOCK" \
  --noise-index "$PERF01_NOISE_INDEX" --noise-index-sha256 "$PERF01_NOISE_SHA" \
  --output "$ROOT/perf01-evidence/protocol-short/compare-final-001"
```

This is 54 fresh processes, three per route per partition, with 140 scheduled
seconds per route per repetition plus warmup, recovery and idle. The completed
index points to actual per-partition `comparison.json` and `comparison.md` files.
There are no future measurement numbers or success flags in these source files.

For manual one-cell execution or an interrupted controller, the extractor also
accepts explicit completed directories. Use its `freeze-noise --before DIR0
DIR1 DIR2 --direct-build MANIFEST --direct-build-sha256 SHA` subcommand, then
`compare --before B0 B1 B2 --after A0 A1 A2 --direct R0 R1 R2 --noise RECEIPT
--noise-sha256 PRECOMMITTED_SHA`. Put `--nativeweave "$NW" --output NEW_DIR`
before the subcommand. No directory glob chooses or excludes results. Explicit
selection still has to follow the predeclared cohort policy.

SIGTERM/interrupts are forwarded to the active driver for its normal partial
receipt and adapter/workload cleanup. If a driver fails to exit within 60 seconds,
the short controller force-reaps its process group and records that cleanup of
the adapter's separate session is **unproved**. Root must check and stop any
surviving process before reusing the timing resource. A forced stop is not a
valid cell. The optional wrapper does not replace root's one-cell supervision
policy or claim uninterrupted execution after its own supervisor is killed.

## Small concurrency check without a full Cartesian expansion

Use only `http2-small` and `grpc-streams` as representatives at C1, C4, C16, C32,
and C64. Reuse the exact matching C4 cohorts above. Preserve the same mixed
partition and all resource/TLS/client controls. A prospective initial schedule
for the remaining exploratory points is:

| Concurrency | Candidate arrival rate/s | Effective scheduled duration | Planned minimum observations per each of 3 equal rows |
| --- | ---: | ---: | ---: |
| 1 | 4 | 75 s | at least 100 |
| 4 | 16 | 20 s | 107, reuse the C4 cohorts |
| 16 | 64 | 20 s | at least 426 |
| 32 | 128 | 20 s | at least 853 |
| 64 | 256 | 20 s | at least 1,706 |

These are offered-load candidates, not measured sustainable capacities. An
overloaded or generator-invalid cell remains a recorded failure; its p99 may
have fewer than 100 successful observations. Root first runs the before points
and records the accepted schedule before any candidate timing. A later changed
rate is a new cohort. One independent exploratory process per route/point gives
descriptive load/recovery evidence only; any selected point receiving a noise
verdict requires its own three-process before-only freeze and fresh comparison
triplets. The C4 band does not apply at a different concurrency or arrival rate.

Use the existing `run.py prepare` command with that profile, `--rate`,
`--duration`, `--concurrency`, `--generator-cpus 0,1`, the immutable build/common
client and certificate, followed by `run --plan ... --exclusive-lock "$LOCK"`.
The driver already preserves actual dispatch lag, outcomes, same-server recovery
and drain. This compact check supplements the root's separately measured mixed
capacity ladders and five before/after 30-minute groups; it replaces none of them.

## Independent source review

The codec reviewer checked wire counters, complete token grouping, probe/ordinary
separation, managed GC bracket and whole-process resource scope, producing
metadata/toolchain/locks, immutable common client, and the direct producer pin.
The database reviewer checked exact triplets, fresh/disjoint process identities,
measurement-window ordering, reader/algorithm hashes, before-only bands,
denominators and mean-only A21 inference. Both found no remaining blocker in
those source scopes after refinements. The codec reviewer also checked the
optional short controller's command order, source identities, SIGTERM handling,
normal child cleanup and forced-cleanup limitation. No reviewer executed these
utilities or workloads during that review; finite execution remains a root gate.
