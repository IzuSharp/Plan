# Independent source review: DB scheduler GC policy

Verdict: **passed source review**, bound to NativeWeave commit
0b2af54419ecf6a11ec83a45725b1c5fbbaeb0d0 and the exact file hashes in review.json.
This review did not execute the candidate module, a test, a build, a database,
or a workload. Separate execution receipts are distinct evidence and are not
claimed by this source-review record.

The producer and reviewer were separate agents. The review covered the four
changed/new files under tests/Perf01.Database and narrowly necessary unchanged
callers and source contracts. No product C#/Rust runtime was changed.

## Finding fixed before approval

The initial candidate's prepare function accessed args.scheduler_gc_policy
directly. The existing profile_postgresql.py calls driver.prepare with a
Namespace that does not contain that new field, so the candidate would have
broken that existing profiling entry point with AttributeError.

The producer changed policy selection to:

    scheduler_gc_policy(getattr(args, "scheduler_gc_policy", "automatic"))

The reviewer reread the correction and recalculated all four final file hashes.
This preserves automatic GC for the existing profiling caller without adding
another source change. The initial run.py SHA-256 was
4b211258470871122ceef0e253a576c9af4fe01a9885029e0ba3dd7683617e74;
the final run.py SHA-256 is
d5c7172b1f595a15a969562e05bb1843e2861c5a8da7e8e5436014df9ae28ce1.
There are no remaining source-review blockers.

## Reviewed behavior

- The wrapper runs the unchanged original cell_worker.main with its original
  arguments. It changes only the DB scheduler process's automatic cyclic-GC
  policy for the complete finite worker call. Reference-count cleanup remains,
  and the original target starts a fresh Python interpreter without a wrapper
  environment mutation. Target, .NET, Rust and database execution are unchanged.
- The actual receipt binds policy and stable policy hash, plan hash, wrapper /
  original worker / common / A21 source hashes, supervised PID and procfs start
  identity. The parent checks completed status, exit code zero, expected
  identity, unchanged thresholds, restored enabled state and collection deltas.
  Deferred mode requires zero collection deltas for all three generations.
- Normal return occurs after original drain, raw replay, observation publication
  and asyncio shutdown. Normal return, Python exceptions and KeyboardInterrupt
  run the restoration finally. Default TERM/KILL may bypass it; an incomplete
  receipt cannot become valid. Existing bounded supervisor cleanup remains and
  does not imply graceful application retirement or successful GC restoration.
- The same wrapper path applies to NativeWeave, direct-Rust and managed DB
  routes. It does not change dispatch clocks, planned counts, scheduling, record
  retention, functional oracles, durable reconciliation, error policy or the
  100 ms dispatch-lag gate.
- A21, cell_worker.py, common.py, supervision.py, target.py and the frozen
  verify_long.py were independently hashed and match the ce2 frozen driver
  byte-for-byte. Their exact hashes are retained in review.json.
- The finite test source covers normal and exceptional restoration, ordinary
  refcount cleanup, possible retained cycles, a fresh child interpreter's GC
  state, and receipt rejection for incomplete/policy/source/identity mismatch.
  This bullet describes inspected test coverage, not test execution by the
  reviewer.

## Prospective execution boundary

The README's first fixed-package comparison is PostgreSQL mixed at 144/s, C16,
120 seconds, seed 20261119, warmup 16, recovery 32, idle 60, compact observation,
and the original split CPU masks. Both cells must use the same committed
driver and actual before package. They differ in automatic versus deferred
scheduler policy and fresh output paths, using stage short and variant
diagnostic. Neither cell earns long-duration credit.

That pair is a correctness/equivalence/resource gate. Required comparisons
include dataset and package/native identities, planned/offered/successful
counts, mix, durable results, normal drain, valid policy receipts, generator
dispatch behavior and per-role resources. Invalid results remain invalid. This
review does not authorize relabeling old samples or silently retrying failures.

A 120-second cell has a different planned count and preallocated state size from
the 259,526-entry full long plan. It cannot establish the long-plan memory trend
or absence of a later stall. Deferral can retain unreachable cycles until
collection resumes or process exit; no constant-memory or memory-neutral claim
is supported. Keep the original resource limits, reject resource pressure or
continuing growth, and complete a prospectively frozen full DB long measurement.

This is a measurement-policy change, not a product performance improvement.
All new before/after/direct-Rust/managed DB noise, capacity and long cohorts must
use one explicitly frozen policy and exact source identity. Earlier automatic
samples cannot be pooled or relabeled as deferred. Existing accepted HTTP/gRPC
results keep their independent unchanged driver identities.

The actual GC evidence motivating this candidate is retained separately at Plan
7394f2be4d3bbf6c7930796ec503f72ff7cef64b, under
checks/postgresql-generator-gc-001/analysis-001. Its measured scheduler collection
reclaimed 3,969 objects; this reinforces the need to measure deferral's memory
effect rather than assuming it is free.

This small record contains source findings and hashes only. It does not edit the
main handoff, change a frozen policy, grant formal timing credit, or substitute
for actual finite-gate, pair, resource, calibration and long-run receipts.
