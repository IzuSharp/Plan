# Perf-01 database resource observation preparation

Status: **source changes and independent source review only**. No sampler,
application, PostgreSQL instance, build or test was executed by this task during
the integration owner's exclusive calibration window.

## Independent process fields and generator roles

NativeWeave commit `edda7e7bcf27d2f3cb2d3279b25b74aa449c1094` changes only
`tests/Perf01.Database`. The new `perf01_resources.py` helper preserves A21's
memory observations while reading CPU, descriptor entries and main-thread
affinity independently. The historical B23 helper's single exception block
could erase a valid CPU reading when a descriptor disappeared during its later
scan (`src/Benchmarks.Domain/common.py:91–105`). A disappearing descriptor now
has its own observed-miss count; other descriptor errors, CPU errors and memory
notes remain distinct. FD/socket scans remain explicitly non-atomic.

The historical B23/A21 source files and all application/runtime sources remain
unchanged. The Perf-01 target process substitutes only B23's process observation
function. The existing application observation cadence remains nominal 20 Hz.
An additional target-owned task samples the HTTPX target, A21 scheduler and
controller at nominal 1 Hz, with one final observation. It uses the same
application phase labels and writes flushed `generator-resources.jsonl` batches.
The controller PID/start identity and observer intervals are included in frozen
inputs; target and scheduler identities are bound before application startup.
Every row retains actual timestamps, process identity, CPU ticks, memory fields,
descriptor observations and main-thread affinity.

The new summary path is `generator_resources.<role>.<phase>`, where role is
`target`, `scheduler` or `controller`. Fields include `cpu_seconds`,
`cpu_percent_one_core`, `cpu_span_seconds`, `rss_peak_bytes`, `fd_peak_count`,
`socket_peak_count`, error counts, identities and observed masks. Application
summaries retain their `resources.<phase>.app_cpu_*` aliases. CPU deltas select
their first/last valid CPU-bearing observations independently of RSS peaks;
fewer than two valid CPU observations produce null CPU summaries.

A definite bound role identity mismatch fails the observer and the Perf-01
receipt. Temporarily unverifiable bound identities remain raw evidence and are
excluded from attributed aggregates. Unbound application memory fields can
remain observable despite a CPU read failure. The sampler is stopped and joined
in target finalization; initial/final observer receipts and flushed partial
records distinguish completion from interruption. This adds no arrival,
functional oracle, dispatch-lag, latency or RSS threshold changes. The separate
PostgreSQL profiling namespace needs no additional argument.

The independent protocol reviewer requested the two identity rules above and
then passed the final source diff. `git diff --check` passed; neither author nor
reviewer compiled or executed the changed Python driver. Integration reported
the cherry-pick as `ef24787`; actual per-cell manifests must establish the exact
driver and artifacts used for any subsequent result.

## PostgreSQL observer setup ownership

NativeWeave commit `55f40b1e21c4292de2094722bb070ad406a3bb52` separately fixes the
profiling script's early setup cleanup. The previous preparation commit
`2f20b2f628d2bb4ada88478a53dccc971247d264` spawned the independent psql observer
and wrote its initial setup before entering its ownership `try/finally`.

The new ownership block covers stderr opening, spawn, initial stdin setup/drain
and sample-task creation. It writes an initial receipt before spawn, applies
finite drain/join/exit/kill/reap bounds, and retains a final observer receipt on
ordinary early failures. A missing observer receipt cannot pass profiling;
missing evidence files are explicit. Secondary receipt or summary errors do not
replace an existing setup/load exception. SQL, Parse/Bind/Execute grouping,
activity sampling, database durability and the always-ineligible-for-formal-
timing classification are unchanged.

The independent protocol agent reviewed and passed this source diff separately.
`git diff --check` passed; no syntax invocation, build, test or actual profile was
run by either reviewer or author. The integration owner must execute and retain
the planned real PostgreSQL profile before claiming attribution evidence.
