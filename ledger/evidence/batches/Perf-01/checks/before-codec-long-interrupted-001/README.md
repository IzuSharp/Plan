# Interrupted before codec long attempt001

This attempt has **zero accepted duration**. The execution connection reset
while measurement was still active. Its original supervisor receipt remains
unchanged with a stale `running` state; no exit status is reconstructed.

The original started at 2026-11-19T20:52:54.535057Z. At 21:11:01Z and
21:11:30Z, operation/event/resource file sizes and modification times were
unchanged, with their last writes around 21:10:16Z. A nonblocking probe of the
same timing lock succeeded at 21:11:30Z and released it immediately. The prior
execution session could no longer be accessed. These observations establish
an incomplete, stopped window; they do not establish a normal child exit or
native-resource drain. No attempt was made to address old PIDs from another
execution namespace.

The actual offline audit completed at 21:15:45Z with exit0. It reads every
completed operation, checks unique IDs and stable input sizes/timestamps, and
hashes all original output files. It found 3,861 warmup operations and
196,142 measurement operations. Recorded measurement dispatch spans
1,021.572841888s; all those completed rows say `ok`. ID199993 is absent within
the observed ID prefix through200003. The outcome of that operation and any
unrecorded in-flight work is unavailable. Recovery and final drain did not
produce evidence. No whole-run success, accepted throughput or p99 is claimed.

The recorded maximum measurement dispatch lag was75.625164ms, with no recorded
lag over the original100ms threshold. This does not rescue a shortened run.
An initial audit incorrectly required a complete ID prefix, failed with an
AssertionError and wrote no result; its original source and failure receipt
remain in the local execution records. The corrected audit explicitly reports
the missing prefix IDs instead of declaring completeness.

The same before004 package/native identity, fixed corpus, rate192, two workers
and frozen thresholds were used. `summary.json` contains an explicit numerical
projection and original content hashes; no copied raw process controls are
published here. The original raw files remain under
`ROOT/perf01-evidence/long/before/codec-001`.

Reproduce the offline audit into a fresh output, outside a timing window:

```sh
taskset -c 8 "$PERF01_PYTHON" \
  ledger/evidence/batches/Perf-01/checks/before-codec-long-interrupted-001/audit.py \
  --root "$ROOT" --output "$FRESH_AUDIT_JSON"
```

A future attempt must run a new full continuous1800s-or-longer measurement,
with its own new directory, actual exit, recovery and drain verification. The
partial record cannot be stitched to another segment. The unchanged original
completed-run verification command was not run because its completion
precondition was not met.
