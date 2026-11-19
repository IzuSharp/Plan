# Perf-01 long-load acceptance clarification

This note supplements prospective policy revision 3 without modifying the policy
file used by an already running calibration controller. It is a preparation
clarification before product implementation changes, not a new passing verdict
for earlier invalid cells. The final `frozen-execution.json` must bind this note
and the final common verifier source hash.

Use the same prospectively scheduled 1802 seconds for each before/after long
segment. The independent post-run verifier in `tests/Perf01/verify_long.py` must
prove at least 1800 seconds from the earliest fully validated ordinary-operation
completion observed by the controller to the last successful ordinary operation's
controller dispatch-start. This is conservative: completion follows real work,
and dispatch-start precedes its command's real work. Admission acknowledgements
alone establish only IPC ordering and are not exact network/codec start times.
The original dispatch span, full valid/correct load, frozen service/resource
limits, recovery and owner drain remain necessary. Protocol cancellation/deadline
probes stay checked but cannot extend the ordinary-operation duration endpoints.
The two-second guard is never automatically credited as elapsed valid load.

The SQLite phrase **“zero hidden retry”** in the prospective mix is clarified to
**“zero explicit application business retries; internal SQLite busy-handler/sqlx
retry counts unavailable.”** The catch/log/rethrow observer records actual
provider BUSY/LOCKED exception codes without changing transactions or retry
policy. It does not observe SQLite's internal busy-handler attempts. Independent
durable queries remain the authority for actual committed business volume.

The common verifier supplements the codec driver's existing completion flag with
the fixed 500 ms scheduled-arrival p99 and the maximum measured application RSS
across the load interval, capped at 256 MiB. It preserves original evidence and
writes a new receipt with input/source hashes, explicit failure reasons and zero
credit for failed or partial attempts. The code and its finite synthetic tests
are initially prepared and independently source-reviewed without execution during
the exclusive calibration window. Execution status must be recorded separately.

## Prepared source and independent review

NativeWeave commit `3ad5f10a25eb6f52dc6d6e583db48ff840d2ffe5` adds the
common verifier, finite synthetic tests, and corrected database duration/resource
documentation. The protocol-domain agent independently read the actual domain
schemas and reviewed the duration ordering, ordinary-token/client join, complete
counts, fixed raw arrival-p99 arithmetic, measured RSS peak, recovery/drain,
identity receipts, streamed DB array handling and failed-receipt paths. The final
source review found no remaining blocker. No syntax compilation, test execution,
verifier execution, product build or workload was performed in this preparation
step. `git diff --cached --check` passed as a source whitespace check only.

The first dispatched request can be admitted after a later request completes.
Therefore the original first-command admission-based IPC bound is reported but
does not add another duration threshold. The D − C ordinary-operation bound and
the original dispatch span remain mandatory. Continuous scheduled arrivals plus
complete lag/count gates establish offered load; this does not claim uninterrupted
CPU busy work. A focused synthetic case preserves that distinction.

Inputs with recorded prior hashes are compared against them; all consumed inputs
receive hashes in the new receipt. The existing DB summary does not contain prior
raw hashes for `observation.json` or application resource samples. The verifier
pins their current bytes and checks consistency, but cannot authenticate them
against arbitrary historical edits. Original domain oracles and external evidence
retention remain necessary.

Current database timing resource observations cover application CPU/RSS/fd and
the target, scheduler and controller generator roles. PostgreSQL process-tree
snapshots cover identity/affinity only: PostgreSQL service CPU/RSS time series are
unavailable in this cohort. SQLite engine resources are included in the application
process and are not isolated. The separate PostgreSQL statement-duration and
wait-state profile cannot be substituted for service CPU/RSS measurement.
