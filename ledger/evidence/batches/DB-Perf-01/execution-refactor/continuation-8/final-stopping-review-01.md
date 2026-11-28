# Independent stopping review — selected 17da path

The 2026-11-26 review found no new blocking correctness defect in the selected
execution-path refactor. It did not establish framework-only zero allocation,
Dapper.AOT parity or exhaustion of every possible improvement. Retaining the
best validated alternative and reporting its limits is supported; calling the
whole execution path optimal is not. Source review is distinct from new execution.

## What was completed

The public Fluent route reaches complete-command native compilation, direct
bounded batches, typed non-row completion and the normal generated DTO readers.
Redundant adaptation frames/private builder clones were removed. The bounded
NWQC command and its semantic traversal remain real work. Prepared execution
reuses compiled parameter/projection layout; arbitrary fixed-method generated
SQL templates were not implemented.

Private Find uses a source-owned exact-Table shape and independent key values,
bypassing the general shape cache without retaining a Session or physical statement.
Compatibility ABI/oracle paths still have real callers. Borrowed native batches
avoid a whole-frame managed copy while keeping ownership and validation.

## Allocation and unresolved cost

The stream path still constructs transport/controller/enumerator state and
execution values; framework allocation is not zero. The separate instrumented
mapper/List scopes include codec/driver temporary work and cannot be subtracted
from a different mixed workload to obtain exclusive framework bytes.

Immutable shape hashing, SQL/Expectation copies, dynamic command representation,
value ownership and per-batch dispatch remain attribution questions. Safety
responsibilities do not prove every current buffer, object or queue is necessary.
See the [three focused directions](../continuation-7/remaining-hot-path-costs.md).

## Rejected alternatives and reasons

The quiet-final-close experiment preserved existing cleanup proofs but failed
its prospectively declared two-round criterion. PostgreSQL single-row prepared
read-complete changed direction between rounds; SQLite 1,000-row pooled total
p50 regressed 6.78%, beyond the 5% guard. This rejects that specific alternative,
not every possible scheduling change.

The inline-completion alternative was rejected before AOT/performance measurement.
Completion publication happens before fallible continuation dispatch. Re-setting
a generation, publishing another error or disposing a delivered batch cannot
repair that post-publication boundary. User code must remain off the unmanaged
ready stack.

## Accepted conclusion boundary

The [final report](final-report.md) owns the four-cell outcomes and observed
delivery. Separate [FFI diagnostics](final-ffi-diagnostics-01.md) count calls in
six 15-second instrumented cases; they do not supply missing counters for the
ordinary phase suite or long campaign. libpq submissions are not server replies
or RTT. No performance credit is granted merely by this review.
