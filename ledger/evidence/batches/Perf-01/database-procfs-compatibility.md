# Perf-01 PostgreSQL procfs observer compatibility

The first PostgreSQL revision-3 calibration attempt failed before timed work in
`perf01-evidence/calibration/before-postgresql-v3/00-ladder-5`. Preserve its
`00.log`, private cluster command receipts and server log as a failed setup; it
receives no valid-load or long-stage credit. The product/native source remains
the frozen before version.

## Observed cause

The observer tried to read `/proc/996/task/996/children`. PID996 was the actual
postmaster, not a demonstrated transient child: the server log records it ready
at 2026-11-19 09:24:21 UTC, followed by the supervisor's normal fast shutdown
after the observation exception. A separate bounded check of the live analysis
Python process found its `/proc/<pid>/stat` and `status` available while its own
`task/<pid>/children` file was also absent. This environment does not expose that
children interface. Suppressing the missing root file as a child-exit race would
have weakened the required root check.

## Scoped fix and limits

NativeWeave commit `38477e603bbe82761136c97523b99acfd5750385` replaces only
the Perf-01 observer's descendant discovery with a procfs `stat` snapshot of
parent PID, process start ticks and state. It traverses the complete captured
descendant graph and validates the captured PID/start identity, current parent
identity and current thread masks. Exited, reused or reparented descendants are
recorded explicitly as skipped. Processes that disappear before discovery can
establish their ancestry are recorded separately as discovery unavailability.

The postmaster must remain live with the same PID/start identity throughout;
root disappearance/reuse is still failure. Both its first and final observed
masks remain subject to strict validation, as do all retained child thread masks.
The previous root start tick remains checked by later phase observations.
The observer is a non-atomic snapshot; it does not claim continuous coverage of
newly spawned or already exited backends. It still does not measure PostgreSQL
service CPU/RSS.

No SQL, database durability, workload, native library, package, application,
runtime, error policy or performance threshold changed. The same final observer
source must be bound to formal before/after comparisons. Previously completed
codec/SQLite calibration remains preparatory selection evidence; it is not
silently relabeled as a formal comparison using a different source hash.

## Verification and review

The protocol-domain agent independently read the final observer and all six
finite tests and reported no remaining source blocker at the exact commit above.
That independent review executed no tests, syntax compilation or workload.

After root's exclusive SQLite PageProbe ended, the author executed:

```sh
taskset -c 8 /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  -m unittest discover -s tests/Perf01.Database -p test_affinity.py -v
```

All six synthetic tests passed (0.005 seconds reported by unittest). They cover
recursive descendants without a children interface, an exited parent and orphan,
child PID reuse, missing/reused root, invalid child/final-root masks, and mismatch
with the previously captured postmaster identity. Fixtures mock procfs identities
and masks; they start no process, database, socket or load.

A separate read-only invocation of `process_group(os.getpid())` followed by
`require_group` on the observed CPU8 mask also passed in the real environment:
one process observed, no skipped descendants or unavailable discovery entries.
`git diff --cached --check` passed. These are observer checks, not performance
measurements. Root subsequently integrated the fix as `5b2a876` and resumed
PostgreSQL/HTTP/gRPC calibration in fresh `v3r1` directories; the failed original
PostgreSQL setup remains preserved.
