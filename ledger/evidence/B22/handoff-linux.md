# B22 Linux checkpoint

Implementation is in progress after accepted B21. The batch coordinator owns
this ledger; source work is split between the external fault/observer/soak owner
and the root public API consumer in separate worktrees. See the
[batch handoff](../batches/Task-07/handoff-linux.md) for source commits and PRs.

`checkpoint-preservation-001.json` binds retained development evidence, including
unsuccessful attempts. It is not an acceptance record. The SQLite busy and scoped
libc ENOSPC pilots use actual B21 packages/native engines with independent durable
SQL observations. Exact provider classification, resource accounting, PostgreSQL
fault ordering and crash barriers are still being refined. `ptrace` is unavailable
in the container; the failure to inject is retained rather than counted as a pass.

The packed public API probe compiles/runs actual JIT and NativeAOT consumers. Its
pilot failures revealed fixture assumptions about certificate loading, SQL null
semantics, native output location, post-header stream abort and optional base64
padding. Fixes preserve the pinned contracts. SQLite JIT pilot007 passes67 cases;
the frozen two-provider/two-runtime matrix and independent review are next.

No 30-minute,24-hour or72-hour profile is complete. A short process run, flat RSS,
EOF, successful Close receipt, or missing counter does not prove aggregate owner
retirement. Missing managed roots must be reported unavailable, not zero. No B22
Linux acceptance or performance/release correctness gate is asserted here.

Private configurations, ephemeral test keys, databases and binary artifacts are
omitted from Git. Receipts preserve exact package/native/executable hashes and
commands. Source and locks are retained on the Task-07 branches; producer inputs
remain the inherited accepted component versions.
