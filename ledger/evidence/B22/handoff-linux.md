# B22 Linux checkpoint

B21 remains accepted and unchanged. B22 implementation and short validations are
complete; staged resource verification is still in progress. The batch root
owns this ledger and integration; separate branches own the fault/observer/soak
source and public API/transport consumers.

- Final public API matrix:4 provider/runtime rows,270 assertions, independent
  gRPC/MCP/metadata closure. See `api-matrix-002` and `api-independent-review`.
- External fault matrix:40 cases,428 assertions; actual PG dispatch/ack/physical
  session witnesses, scoped SQLite WAL ENOSPC, crash/restart/outbox/blob/GC and
  HTTP interruption. See `fault-final-001` and `fault-independent-review`.
- Slow-client/shutdown matrix:12 cases,88 assertions. See `transport-final-002`
  and `transport-independent-review`; earlier oracle findings remain retained.
- Observed build004 joins the actual application entry task/thread before final
  forced GC. All six counters in each exact native provider inventory and
  Server permit/payload gauges return to zero. JIT/AOT known-handle controls are
  in `eventpipe-controls-002`; this is not every managed object graph root.
- The first8-second probe and five-cycle200-second calibration passed their
  declared gates. They remain under `development`; the candidate is not frozen.
  Fresh per-window GC anchors and post-sampling generator time are required by
  review before corrected calibration and any long stage.

No30-minute,24-hour or72-hour profile is complete. Short tests, flat RSS,
EOF or a Close receipt do not replace any required duration. B22 Linux/full
acceptance remains false; final B23 and B24 gates remain blocked on these rows.

Sources, exact executed hashes, failed pilots and receipt-only correction
applicability are linked by the batch handoff. Original run identities are never
relabeled as later source. Private configuration, test keys, databases and
rebuildable binaries are excluded from Git. Raw EventPipe streams are preserved
losslessly compressed, with original hashes in the preservation inventory.
