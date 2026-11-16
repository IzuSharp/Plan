# Task-02 Linux x64 handoff

## Scope and baselines

The current user authorizes all nine Task-02 items, implementation, tests, docs,
commits, remote checkpoints, PR review/normal merge and existing automatic preview
closeout on Linux x64. Historical research-only text does not revoke that concrete
authorization. Do not start Task-03 or add other platforms/release packages.

A01/B01 are reused from [Task-01](../Task-01/handoff-linux.md), without reimplementation
or repeated historical acceptance. NativeWeave baseline is
`10915d26b13a5ffd0b1abbe06d5934dfb0f2d771`; Plan baseline is
`5536d6d02cb7b99cd2100d6e73d701d676547ce2`. Read-only Design is exactly
`c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. This Linux ledger overlays unchanged
historical source bindings and accepted research graphs.

## Current task status

| Task | Linux state | Owner / evidence |
| --- | --- | --- |
| A02 | Implemented and verified; independent review pending | Negotiation worker; [packet](../../A02/linux-task02/) |
| A05 | Component accepted after independent review | Main executor; [run](../../A05/linux-run-001/result.json), [review](../../A05/linux-independent-review/review.json) |
| A09 | Implementing | Main executor |
| B05 | Component verified; actual B02/B03 composition and independent review pending | Transactions worker; [run](../../B05/linux-component-001/result.json) |
| B07 | Component accepted; review precision finding fixed | Codecs worker; [full run](../../B07/linux-run-001/summary.json), [fix](../../B07/linux-review-fix-001/summary.json), [review](../../B07/review-linux.json) |
| B09 | Ready, queued | Main executor |
| B02 | Implementing | Negotiation worker; B01/B07 available |
| B03 | Implementing | Transactions worker; B01/B07 available |
| B06 | Implementing; final acceptance awaits B02/B03 | Codecs worker; B01/B07 available |

A02 passed 108 commands, exact 84 public API/XML symbols, 26 isolated JIT and 26
actual NativeAOT scenarios (428 assertions per mode), and test-only NuGet consumers
with zero Rust calls. The consumer is explicitly not a pristine-machine claim.
A05 passed 39 commands and independent 23-probe review, with exact source, raw-log
and artifact hashes. B07 passed 22 full-run gates, then 9 focused review-fix commands,
7 native tests, actual PostgreSQL 18.0/SQLite 3.51.3 codec roundtrips for 120 vectors
per JIT/AOT mode, and 4,189 malformed-input rejections per fixture mode. The focused
run records its unchanged managed binary reuse. B05 passed 30 component commands,
13 Rust lifecycle tests and 29 managed assertions in each JIT/AOT mode; it remains
pending real providers. B05's previously uncommitted root manifest/lock bytes are
now committed unchanged in its source checkpoint; the original dirty-tree fact is
preserved in its evidence.

Full B04 owning-host composition remains its downstream gate per the packets' DAG
rationale. Provider options/native adapters and ABI fixtures may be accepted here;
no fake host types or Design-stub execution may stand in for product execution.
Other platforms remain unexecuted, and global/all-platform acceptance is false.

## Recovery and commits

ROOT is `/workspace/scratch/0898a75257bc`. Batch worktrees are
`ROOT/.worktree/Task-02-linux/{NativeWeave,Plan}` on `task/Task-02-linux`; the sibling
`NativeWeave-Design` is detached at the pinned commit. Every task has its own
`ROOT/.worktree/Task-02-<ID>-linux/NativeWeave` and `task/Task-02-<ID>-linux` branch.
B02/B03/B06 started from integrated `f20707d7f687985a164a04e0da4373b97bdc60be`.
The root alone integrates shared solution/Cargo/build entries. See
[status-linux.json](status-linux.json) for exact task checkpoints and integration
commits, and [retention inventory](evidence-retention-linux.json) for raw evidence
hashes. Compiled binaries, caches, temporary database clusters and private TLS keys
are not copied to Plan; artifacts are identified by content hashes and verifier
commands retained in NativeWeave. Evidence text is preserved verbatim.

Implementation PR: https://github.com/IzuSharp/NativeWeave/pull/13 (Draft).
Remote checkpoint `2916b9a7817399cabbdbf81d4fe5dca45d9c2afd` has the exact tree
`4bf46a6478963ab0e9774d17154357fcd0953417` of local
`f20707d7f687985a164a04e0da4373b97bdc60be`. Git Data API publication preserves exact
file bytes but produces a different commit identity; source-evidence mappings are
explicit, never relabeled.

Plan PR: https://github.com/IzuSharp/Plan/pull/14 (Draft). Continue the same PRs.

SDK 11.0.100, Rust 1.100.0, PostgreSQL 18.0 and pinned SQLx are restored.
Use `ROOT/task02-toolchain/env.sh`; local-only offline NuGet configuration does not
change repository/CI audit policy. Start temporary TCP PostgreSQL and tests within
one verifier invocation: background processes do not remain accessible across
executor invocations. Full solution formatting remains a normal CI gate because
this local runtime denies formatter-host Unix sockets; local folder whitespace
checks do not claim equivalent full formatting.

## Next step

Continue A09/B09 and the three provider/stream workers immediately. Review A02,
finish real-provider B05/B06 acceptance inside this batch, integrate and run the
scoped regression. Publish checkpoints and update both PRs, then normal required
checks/review/merge. Verify exact merge CI and the existing HelloWorld-only automatic
preview publication/consumption. Do not declare this batch complete before that
closeout, and do not add repeated commits merely to record each check poll.
