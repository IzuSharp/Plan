# Independent review of the recovered single-case analyzer

Reviewer: native_review, 2026-11-26. Scope is source inspection and finite offline
controls over copies of the retained diagnostic JSON. No consumer, database,
benchmark, product build, CI job or original evidence mutation was performed.

## Disposition

Accept `analyze_command_single_v2.py` at SHA-256
`0cec15c40be5a8c1db900d884daf2bc83f9f84fc5ff930c30d9ebac38d5a5730`
for this recovered evidence analysis. The source correction is necessary; the
original rule incorrectly required a child-close command for every transaction.
This is not evidence of a failed product transaction and does not justify
discarding the original failed analysis or its first failed negative control.

The actual
[CloseController.Request](https://github.com/IzuSharp/Korda/blob/47fe650dfed5d7bba1c4d74c4a127c5d08b66082/src/Data.NativeHost/DataSource.cs)
observes native cleanup before calling `source.CloseOwner(owner)`. When
`LocalResourcesReleased` is already true, it completes from that proof and
releases its managed owner without issuing a close command. Its `_task` guard
permits at most one close request from this controller. Both branches are valid.

The case source and this branch support these aggregate constraints:

- Numeric (32 rows) uses zero one-shot commands.
- Rollback has three mandatory commands per completed business operation: begin,
  one nonreturning mutation and finish. Commit has four: begin, two mutations
  and finish.
- Each transaction can add zero or one child-close command. Across `n` completed
  operations, `request - mandatory*n` must remain in `[0,n]`.
- Take calls equal request calls. Both must have exactly one OK return per call.
  The independent return-count validation consequently excludes Pending and
  unaccounted status returns for these calls.
- Every `nw_db_operation_*` call, generic close creation, command cancellation
  and command error-take must be zero in this healthy direct-completion lane.
  In particular, a generic retirement call returning only Pending is rejected.
- Cursor pull/create/close counts, business oracle, case totals, source/binary/
  stdout identities and all final owner counters retain their checks.

The diff from the retained original analyzer is confined to `ffi_counts`.
Identity, ordinary timing arithmetic and business validation were not relaxed.
The revised output explicitly labels child-close attribution as inferred from
aggregate counters: these counters do not identify individual command kinds or
prove that a particular transaction followed a specific branch. Per-operation
trace claims would require other evidence.

## Actual retained diagnostics

These counts are independent instrumented processes and carry no latency or
allocation comparison credit. All request and take calls below returned OK;
all generic-operation call deltas are zero.

| Provider | Case | Business completions | Request = take | Inferred conditional close |
| --- | --- | ---: | ---: | ---: |
| SQLite | Numeric, 32 rows | 80,666 | 0 | 0 |
| SQLite | Rollback | 11,775 | 36,713 | 1,388 |
| SQLite | Commit | 7,919 | 31,984 | 308 |
| PostgreSQL | Numeric, 32 rows | 44,648 | 0 | 0 |
| PostgreSQL | Rollback | 6,198 | 21,790 | 3,196 |
| PostgreSQL | Commit | 4,857 | 20,774 | 1,346 |

## Independent verification

The final hash above passed both finite checks, each with process exit 0:

1. Independently reran the evidence author's 146 controls. Result:
   `analyzer-controls-independent-02.json`.
2. Wrote and ran `check_analyzer_independent_v2.py`, adding 186 controls. Result:
   `analyzer-independent-extra-02.json`.

The second set independently tests minimum/maximum command boundaries,
request-only and take-only skew, Pending replacing OK, an unexplained status
return, every generic operation in the validated ABI inventory (including every
status-returning variant with Pending), short/long counter vectors, negative,
Boolean, fractional and decreasing cumulative counters. The six original
diagnostic inputs are rehashed before and after; none changed. The first set
also checks missing mandatory commands, extra child closes, individual owner
leaks, sticky oracle failures and nonzero business errors/failures through the
whole-command analyzer.

Initial review found one diagnostic-only inconsistency: direct transactions
correctly rejected generic close creation but printed a legacy `[0,n]` range.
The author corrected this to `[0,0]`. Both control sets were then rerun against
the final analyzer hash above. The earlier `-01` outputs remain intermediate
records and are not assigned to that final hash.

These controls validate the analyzer's finite source-based inference. They do
not add an operation-kind wire trace, qualify the host, execute a fresh product
candidate, prove framework-only zero allocation, or satisfy a long-run gate.
