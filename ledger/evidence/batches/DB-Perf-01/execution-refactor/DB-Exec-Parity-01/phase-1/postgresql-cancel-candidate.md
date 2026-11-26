# PostgreSQL cancellation hook experiment

Selected after measured Stage1 Plan gate d463730 and Design da15cf2, before implementation. The observed thousand-row path calls Cancel.install1002 times. Actual Clang/libc++ machine code uses small-buffer storage for the weak_ptr lambda; it is **not**1002 proven heap allocations.

A whole-source read of baseline7ff7b57 finds ProviderConnection::Impl.interrupted defined, reset in prepare and set by interrupt, with no reads. ProviderConnection::interrupt affects the engine only inside the SQLite branch (sqlite3_interrupt). PostgreSQL cancellation already depends on CallContext::check around every row and nonblocking receive/flush/poll, followed by the existing bounded drain or physical discard. It sends no cancel-key packet.

Isolated PG-A hypothesis: install provider interrupt hooks only for SQLite. Preserve PG per-row checks, old-token detach, poll deadlines, server execution/drain, error ordering and COMMIT Unknown. Remove the unused interrupted field/stores if independent review confirms the exhaustive source proof. Predict PG install1002→0 while SQL/protocol/batch/row count and SQLite behavior remain unchanged. Measure actual counts, mutex/weak-reference CPU and ordinary interleaved A/B; make no native-allocation reduction promise.

Unconditional libpq chunk32 was rejected before coding because a partial chunk may lose already-produced rows on later server error, and provider lookahead/byte ownership would grow beyond the current one-row bound. No benchmark-only SQL special case is allowed.

Use its own task worktree/commit/native/package/ordinary AOT identity. Run actual PostgreSQL cancellation, later-row error, early-stop, cleanup deadline, protocol synchronization and unknown-commit regressions; preserve independent affected-provider package selection. A failure or benefit within noise remains recorded and can reject the candidate.
