# Task-07 Linux x64 handoff

## Scope and current state

The current user explicitly authorizes B21, B22, B23 and B24 on Linux x64,
including implementation, necessary verification, documentation, independent
review, commits, pushes, draft PRs, checked merges and the existing postmerge
preview closeout. Historical research-only graph fields remain historical;
this platform ledger records the authorized product work. Design is read-only.

| Task | Linux state | Owner | Start dependencies | Acceptance dependencies |
| --- | --- | --- | --- | --- |
| B21 | original_matrix_passed; final_boundary_supplement_pending | b21_service; root integration/tests; task07_requirements review | B04, B08, B13, B14, B15, B17: satisfied | B20: satisfied |
| B22 | waiting_for_B21 | unassigned | B21 | None |
| B23 | waiting_for_B21 | unassigned | B21; A21: satisfied | B22 |
| B24 | waiting_for_B22_B23 | root | B22, B23 | A16, A22, B18, B19: satisfied on Linux |

All completed dependencies are inherited from their existing records, without
reimplementation or historical acceptance reruns. The source recovery found no
Task-07 remote branch, PR, or retained implementation worktree. Earlier local
Design/Plan checkouts and the .NET SDK survived; current product sources were
restored from the existing merged commits.

## Immutable inputs and inherited evidence

- Implementation starting commit: `bc4f769b2bd3022df13c180d6ce3a6cea9b8faa1`.
- Plan starting commit: `28498bae4c13bd536489511707bc74c26bd68d73`.
- Locked Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
- Toolchains: .NET SDK 11.0.100, C# 15, Rust 1.100.0.
- Task packets: [B21](../../../../tasks/B21.md),
  [B22](../../../../tasks/B22.md), [B23](../../../../tasks/B23.md),
  [B24](../../../../tasks/B24.md), with `fragments/end-to-end.json`.
- B04/B08/B13/B14: [Task-05 handoff](../Task-05/handoff-linux.md).
- B15/B17/B18/B19/B20: [Task-06 handoff](../Task-06/handoff-linux.md).
- A21: [existing handoff](../../A21/handoff-linux.md).
- A16: [Linux acceptance](../../A16/acceptance-linux.json).
- A22: [Task-03 handoff](../Task-03/handoff-linux.md).

Task-05 implementation PR17 and Plan PR20 are merged. Task-06 implementation
PR16 and Plan PR21 are merged. Their accepted Linux component evidence is reused.
The existing automatic release publishes only the HelloWorld preview; Task-07
must not silently expand publication to the domain packages.

## Branches, worktrees and persistence

- Reused checkout parent (ROOT): `/workspace/scratch/58d2a6adf1c3`.
- Batch branches, both repositories: `task/Task-07-linux`.
- Batch worktrees: `ROOT/.worktree/Task-07-linux/NativeWeave` and
  `ROOT/.worktree/Task-07-linux/Plan`.
- B21 implementation branch: `task/Task-07-B21-linux`.
- B21 implementation worktree: `ROOT/.worktree/Task-07-B21-linux/NativeWeave`.
- Implementation PR: https://github.com/IzuSharp/NativeWeave/pull/18 (Draft).
- Plan PR: https://github.com/IzuSharp/Plan/pull/22 (Draft).
- Integrated Task-07 controller checkpoints: `ec619c1` (independent byte/HTTP/SQL
  oracle), `119d67e` (PostgreSQL protocol oracles), `8fdb096` (redelivery,
  retention, blob boundary and restart cases).
- B21 application `ebef00c` is integrated as `9e0cb8d`; package controller
  `7a5987f` is integrated as `cd4b6b0`; the corrected real PostgreSQL oracle
  `f43698a` is integrated as `275ee8f`. Final recovery/maintenance source
  `074b771` is integrated as `acb5be5`; its complete immutable matrix passed.
  The response-vector-only helper `d491a8a` is integrated as `11b7d27`, with
  independent literal vectors `15ec950`. Boundary-controller supplementation
  remains pending, so B21 is not yet accepted.
- CLI push is unavailable because no Git HTTPS credential is configured. The
  authorized GitHub connector persists GitData commits; each transported tree is
  compared with its local execution tree. Initial product local `ec619c1` and
  remote `5118f5ffddb3520541212f28b98694c0e1bde9ea` share tree
  `9a49fdb2673e187317eb1bd1194bbd0914ec1683`. Initial Plan local `5029ac7` and
  remote `ed729d51012d1e2c08c35a37c6873ecd73995dc7` share tree
  `abecbc17393bc289aca17675d991f52267278f3a`.

## Verification and remaining sequence

The initial read-only dependency audit found all external Linux prerequisites
satisfied. B21 now has actual exploratory product results listed below; none is
promoted to the final immutable matrix or B22–B24 acceptance.
The required maintainer tools and isolated database environment are restored.
Twelve exact local NuGet packages and three native assets were prepared from the
unchanged implementation baseline; building them is preparation, not new
acceptance. Native asset identities and restore/build logs are temporarily under
`ROOT/task07-toolchain/`; the eventual B21 evidence will bind its actual inputs.
Independent executor calls cannot reach each other's loopback service; each
controller therefore starts its database and application in one process tree.

Actual exploratory checks:

- [Initial SQLite smoke](../../B21/initial-sqlite-smoke/summary.json): 83 passing
  HTTP/independent-SQL assertions using the packaged JIT application. Its
  [provenance](../../B21/initial-sqlite-smoke/provenance.json) explicitly records
  that no pre-run executable hash was captured; this is not final acceptance.
- Standalone package pilots built baseline/ordinary-managed-edit JIT and AOT
  consumers. The ordinary real PostgreSQL JIT row passed the same 83 assertions.
  Failed integration attempts are retained under `ROOT/task07-package-probe/`.
- Actual packaged PostgreSQL specialized oracles passed a witnessed transaction
  lock conflict, separate ReadCommitted business SELECT, and a discarded real
  COMMIT/idle acknowledgement followed by 503 Unknown, authorized recovery and
  exact replay. The oracle reports SQLx's one bounded catalog-metadata query
  explicitly, rather than claiming literal wire adjacency. Diagnostic attempts
  remain under `ROOT/task07-toolchain/logs/b21-proxy-product-diagnosis-*`.
- The review regression passed 21 checks for fair maintenance past 100 protected
  records, orphan-temporary grace, protected references, actual concurrent
  failed-CAS rollback and cleanup joined before graceful CLOSED. Exact source
  hashes/results are at `ROOT/task07-runs/b21-review-regressions/`; final review
  still needs binding to the frozen source.
- Actual HTTP/2 frame observation confirmed status 413 for oversized JSON after
  the original HTTPX upload behavior obscured the early response. A reset or
  client-side exception alone is not a passing rejection oracle.

The latest transported implementation checkpoint `c9bb00ca9b122b8e5a9b0a3181bc1d264c72b77c`
has [passing CI44244176714](https://github.com/IzuSharp/NativeWeave/actions/runs/44244176714).
Plan checkpoint `6c62b08900e8b62750de7c944962f42a8ad73412` has
[passing CI44243404717](https://github.com/IzuSharp/Plan/actions/runs/44243404717).
Later local checkpoints are to be transported with the frozen source. Both PRs
remain Draft; no Task-07 merge or postmerge publication has occurred.

### Completed immutable B21 matrix and remaining supplement

The [original matrix](../../B21/package-matrix/summary.json) passed all 16 rows:
two databases, JIT/NativeAOT, HTTP1/HTTP1-TLS/HTTP2-TLS, plus four ordinary
managed-edit HTTP2-TLS consumers. Its 1,856 per-row assertions, two PostgreSQL
specialized cases in each runtime, exact native/package/executable identities,
runtime witnesses, isolated restore graphs and raw logs are retained in
[progress.json](../../B21/package-matrix/progress.json). No consumer Rust command
ran. This is isolated package consumption on a host with Rust available, not
B24's pristine-machine or release gate.

The matrix executed `acb5be54f6a6af4e26048af6f98553a4ac7e41ad` from
2026-11-18T05:44:54Z to 05:54:02Z. Its exact source
[independent review](../../B21/source-review/review.json) resolves all six
recovery, cleanup and maintenance findings. The
[response-vector supplement review](../../B21/source-review/response-golden-supplement-001/review.json)
binds the later CLI-only delta and approves reuse of unaffected matrix rows;
it does not relabel their old executable hashes as new ones. The
[TLS readback](../../B21/package-matrix/tls-transport-readback.json) confirms
actual HTTPS startup for every original TLS row, closing the gap in the old
controller's configuration-derived TLS summary.

Independent controller review identified missing true over-limit, inside-window
retention, shared-content authorization, attachment binding and durable replay
assertions. A strengthened controller has passed a focused 151-case SQLite/JIT
run. The final four provider/runtime HTTP2-TLS rows, actual updated JIT/AOT
response vectors and final controller review remain necessary before B21 closes.
No B22 implementation or B23 measurement has started early.

B21 must first complete its real service, both database profiles, native
HTTP1/HTTP2/TLS and actual JIT/NativeAOT package-consumer verification. B22 and
B23 may then proceed in separate worktrees; fault injection and timed performance
measurement must not contaminate each other. B23 final acceptance waits for B22.
B24 starts only after B22 and B23 finish.

B22 and pinned D20 require actual 30-minute steady-state, 24-hour regression and
72-hour release-soak profiles. Freeze the workload, seeds and resource thresholds
before each run; persist observations and interrupted durations. A short run does
not satisfy a longer profile. Missing long-duration evidence keeps B22, final B23
acceptance and B24 unaccepted.

Windows and every other platform are deferred outside this run. No all-platform
acceptance or subsequent task package is authorized by this record.

## Next step

Complete B21 within its declared source/test/guide/sample scopes, integrate its
independently reviewed commits, save exact source/native/package/executable
identities and actual logs under `ledger/evidence/B21/`, and update this handoff
with the two draft PRs and the next unlocked work.
