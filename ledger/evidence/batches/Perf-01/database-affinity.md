# Perf-01 optional database generator CPU isolation

Status: **implemented and independently source reviewed; no workload or affinity
mutation executed by this preparation task**. Integration owns calibration,
the frozen before/after cohort, timing and acceptance.

## Implementation and resource scope

NativeWeave commit `659a871d06029a7800385f477a85a5fe2ef2361f` adds the optional
`--generator-cpus` argument in `tests/Perf01.Database/run.py`, application launch
and actual executable checks in `target.py`, and read-only Linux process/thread
observations in `perf01_affinity.py`. The existing B23 and runtime sources are
unchanged. No package rebuild is needed.

The controller must start on two service CPUs. For the proposed diagnostic
layout, prefix the normal invocation with `taskset -c 2,3` and add
`--generator-cpus 0,1`. Both masks must contain exactly two CPUs and be disjoint.
The private PostgreSQL cluster starts before the controller changes its main
thread mask. A21's cell worker and the HTTPX adapter inherit the generator
mask. Only the actual application command is prefixed with the separately
hash-pinned `taskset --cpu-list 2,3`; it execs the real Native AOT/Rust application
in the same PID before runtime threads are created. Existing application
processor-count settings remain unchanged.

This provides two service CPUs shared by the application and PostgreSQL, plus
two generator CPUs. It changes the measurement resource layout and therefore
requires a new calibration and frozen cohort. The same layout must be used for
before, after and comparable direct-Rust/managed routes; older shared-CPU cells
cannot be treated as equivalent observations.

## Identity, verification and failure handling

Frozen inputs and the target manifest record the masks and launcher SHA-256.
The loaded application executable is read through `/proc/<application-pid>/exe`
after READY and checked directly against the original route's frozen artifact
SHA-256. The launcher does not replace this original executable/package pin.

The driver observes the controller, A21 scheduler, HTTPX target, application
and currently live PostgreSQL descendants. Main thread masks must equal the
declared mask; other surviving threads must have a nonempty subset of that
mask. PostgreSQL's root PID is bound to its procfs start time. Target observations
are saved after seeding, after load and after the idle/drain observation. The
controller saves its own before, end and restored observations separately.
These are live snapshots and do not claim continuous coverage of transient
threads or backends.

Verification exceptions fail the cell. Frozen inputs, already collected
observations and external supervision records remain available; a failed
verification may leave no final summary and must receive no successful or
long-duration measurement credit. The controller restores its main-thread
service mask in `finally`, before PostgreSQL teardown. With no option, the driver
performs no affinity mutation. The separate PostgreSQL profiling script does
not set this option and retains its existing CPU behavior.

## Executed checks and independent review

The author ran Python syntax compilation for the driver, target, affinity helper
and PostgreSQL profiler; CLI help; `git diff --check`; pure CPU-list parsing and
synthetic invalid-mask rejection checks; and read-only procfs inspection of the
checking Python process. All passed. No application, database workload, formal
timer, CPU-affinity mutation or package build was run for these checks.

The separate Perf-01 protocol agent reviewed the uncommitted final diff before
commit, including the final direct comparison of the actual executable hash to
the frozen route artifact. The review passed the startup inheritance, process
and thread verification, identity, failure and restoration paths. The reviewer
performed source inspection only and did not run tests or workloads. This is an
independent technical review, not a second GitHub identity or an approval that
substitutes for repository-required checks.

The integration handoff must link actual calibrated cells and resulting
affinity evidence before claiming the proposed layout was observed during a
workload. This document grants no performance or 30-minute acceptance credit.
