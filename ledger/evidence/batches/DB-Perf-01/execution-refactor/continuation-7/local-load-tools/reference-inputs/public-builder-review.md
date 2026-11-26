# Read-only review of the independent public-input builder

Reviewed `candidate-build-tools/build_public_inputs.py` together with the actual
`eng/task07_native.py`, `eng/ci/bundles.py`, `eng/ci/consume.py`, package packer and
`tests/Data.NativeHost/run.py` callers. Their exact reviewed bytes are identified
in the reference archive manifest. No builder, correctness test or workload was
started by this review.

No blocking mismatch was found in the intended invocation. The adapter checks
the supplied full clean commit/tree before creating an output and after each
stage, verifies the actual diff/module plan, and delegates native building,
correctness, public package composition, independent AOT package consumption and
external ordinary consumers to existing repository drivers. Arguments and
provider spelling match those drivers. It does not execute benchmark consumers.
Consumer application packages remain isolated and their projects have no
product project references. Build-only .NET concurrency settings do not become
measurement settings through this script.

Two invocation boundaries should remain explicit:

- A fresh `--output` does not make the producer checkout's ignored
  `artifacts/public` staging feed fresh. The existing packer rejects an occupied
  version; use an independent clean producer worktree per provider/attempt to
  avoid retry collisions and concurrent staging interference. A failure must
  keep its earlier output and use a new attempt.
- `--postgres-bin` configures the isolated PostgreSQL correctness wrappers.
  `eng/task07_native.py` selects libpq from the retained task environment's
  `NW_POSTGRES_BIN`/`pg_config` and validates its pinned 18.0 provenance. Those
  locations must refer to the intended same PostgreSQL installation. The
  wrapper starts/stops its test server in one process namespace.

The adapter's strict CI-plan shape is a deliberate stop condition. If module
selection changes, the selected checks need explanation before adjusting this
local adapter. Its existence does not authorize performance work in CI.
