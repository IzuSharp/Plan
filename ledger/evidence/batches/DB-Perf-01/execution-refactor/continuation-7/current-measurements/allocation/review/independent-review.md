# Independent allocation audit review

This review reads `audit_current_allocation.py` and its finite control runner at
Plan `5e5924a`. It independently executed the existing **152 in-memory controls**
once, during an authorized analysis gap. All 152 passed against audit source
SHA-256 `fe171bc3de57460d27d45e8356216fd967d60d9d9aa6b50b22be592e787012da`.
The original independent output is preserved without alteration as
[allocation-controls-independent-01.json](allocation-controls-independent-01.json).
Its counters state productExecutions=0, measurementFilesRead=0, hashSweeps=0 and
timingCredit=false. The runner reads and hashes its small target source; it does
not scan measurement artifacts or invoke the full audit.

## Reviewed behavior

The auditor binds Korda `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`, the selected
public build review, package/native/executable identities, successful diagnostic
build receipts and the pinned instrumentation builder. It requires two providers,
candidate/Dapper, and 1/100/1000-row inputs: twelve observations from four
diagnostic builds. Instrumentation is replayed into memory and compared to the
recorded consumer/generated mapper sources. Dapper's SQL reference must identify
the current ordinary Korda phase receipt; its historical build identity is not
relabeled as a newly executed build. PostgreSQL command arguments bind the
observed owner port and the configured data directory/CPU selection.

`window_check` requires 256 operations and 256 complete result samples per
window, correct row counts, conserved mapper/List invocation counts, the exact
whole-process allocation endpoint difference and original process GC deltas.
Candidate window endpoints require zero Operations, Cursors, Buffers,
PullChannels and CommandCompletions. Final Drained requires all eight owner
counts to be present, exact nonnegative integers and zero. SQL dispatch changes
by 256 in these isolated successful query windows. This is not a rule for the
mixed transaction workload.

The controls reject Boolean/floating/string/null numeric substitutes, negative
counts, missing or nonzero owners, wrong sample counts, wrong result rows,
allocation/GC/SQL skew, duplicate JSON fields and nonfinite JSON. They require
`FrameworkOnlyBytes` to be explicitly null and reject a substituted numeric
value. The review found no blocking issue in these arithmetic and ownership
checks or the source-level identity chain.

## Evidence limits

The independent rerun exercised arithmetic, owner and strict-JSON helpers using
synthetic in-memory inputs. It did **not** independently re-execute the full
twelve-observation identity audit, replay its filesystem hashes, rerun a
diagnostic consumer, build a product or perform a database operation. The
author's existing full-audit output remains its own execution evidence. Source
inspection of that identity chain is not a second successful full audit.

Observed mapper/List allocation scopes include codec or driver scratch inside
those bodies and are not the retained size of DTO objects. Their sum is reported
separately from whole-process allocation; no subtraction produces a framework
allocation number. GC values are process-wide deltas in each original window,
not per-thread counts or reconstructed whole-process lifetime totals across
unobserved gaps. No timing or zero-framework-allocation claim follows.

The rejected close-quiet experiment at `92b9230` is unrelated to this selected
`17da07e` allocation evidence. Neither its source review nor its correctness
runs are additional execution credit for these twelve observations.
