# Task-07 Linux x64 handoff

## Scope and current state

The current user explicitly authorizes B21, B22, B23 and B24 on Linux x64,
including implementation, necessary verification, documentation, independent
review, commits, pushes, draft PRs, checked merges and the existing postmerge
preview closeout. Historical research-only graph fields remain historical;
this platform ledger records the authorized product work. Design is read-only.

| Task | Linux state | Owner | Start dependencies | Acceptance dependencies |
| --- | --- | --- | --- | --- |
| B21 | accepted_component_linux | b21_service; root integration/tests; independent task07_requirements/controller reviews | B04, B08, B13, B14, B15, B17: satisfied | B20: satisfied |
| B22 | implementation_in_progress | task07_requirements external faults/soak; root public API composition | B21: satisfied | None |
| B23 | implementation_in_progress | linux_environment controller/report; b21_service comparators | B21; A21: satisfied | B22: pending |
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
  independent literal vectors `15ec950`. Boundary controller `a8c559f` is
  integrated as `fd04f95`; strict PostgreSQL dispatch-window readback is
  `517d1e4`. [B21 Linux acceptance](../../B21/review-linux.json) closes its scope.
- B22 branch/worktree: `task/Task-07-B22-linux`,
  `ROOT/.worktree/Task-07-B22-linux/NativeWeave`. Root API fixture uses
  `task/Task-07-B22-api-linux` and its matching isolated worktree.
- B23 branch/worktree: `task/Task-07-B23-linux`,
  `ROOT/.worktree/Task-07-B23-linux/NativeWeave`. Comparator source uses
  `task/Task-07-B23-comparators-linux` and its matching isolated worktree.
  All three new implementation tracks start from integrated B21 `517d1e4`.
- CLI push is unavailable because no Git HTTPS credential is configured. The
  authorized GitHub connector persists GitData commits; each transported tree is
  compared with its local execution tree. Initial product local `ec619c1` and
  remote `5118f5ffddb3520541212f28b98694c0e1bde9ea` share tree
  `9a49fdb2673e187317eb1bd1194bbd0914ec1683`. Initial Plan local `5029ac7` and
  remote `ed729d51012d1e2c08c35a37c6873ecd73995dc7` share tree
  `abecbc17393bc289aca17675d991f52267278f3a`.

## Verification and remaining sequence

The initial read-only dependency audit found all external Linux prerequisites
satisfied. B21 is accepted by the immutable matrix and targeted supplement below.
Its earlier exploratory results remain separately identified and do not imply
B22–B24 acceptance.
The required maintainer tools and isolated database environment are restored.
Twelve exact local NuGet packages and three native assets were prepared from the
unchanged implementation baseline; building them is preparation, not new
acceptance. The unchanged B18/B19 gRPC/MCP packages were subsequently prepared for
the B22 consumer, bringing the existing local feed to fourteen packages. Native
asset identities remain unchanged. B21 evidence binds its actual inputs; extra
package preparation is under `ROOT/task07-toolchain/protocol-pack-preparation/`.
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
  hashes/results are at `ROOT/task07-runs/b21-review-regressions/` and are bound
  by the accepted B21 source review and retained `focused-source` evidence.
- Actual HTTP/2 frame observation confirmed status 413 for oversized JSON after
  the original HTTPX upload behavior obscured the early response. A reset or
  client-side exception alone is not a passing rejection oracle.

Accepted B21 implementation checkpoint `4d613cba2a17e24e536d6a2fe5310d3b062ed511`
has [passing CI44248323581](https://github.com/IzuSharp/NativeWeave/actions/runs/44248323581).
Plan checkpoint `7d6e4134bdf80691b722a5608c83631582cde45b` has
[passing CI44249625029](https://github.com/IzuSharp/Plan/actions/runs/44249625029).
The first B22/B23 controller stage is transported at product
`3b203d75dbeb113c9e9cd9bedac5289e5cde1bfe`, identical tree to local `19a2768`.
Later stages remain separately recorded below. Both PRs remain Draft; no Task-07
merge or postmerge publication has occurred.

### Accepted immutable B21 matrix and targeted supplement

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
assertions. The final four provider/runtime HTTP2-TLS rows passed all 608
assertions (152 each), including actual updated JIT/AOT response-vector output.
Their exact execution at `fd04f95` ran from 2026-11-18T05:56:23Z to 06:00:59Z;
[their own summary](../../B21/boundary-supplement/summary.json) remains an honest
four-row partial selection. It supplements the original16 under the reviewed
CLI-only source applicability, rather than claiming a newly rerun16-row matrix.
Root rechecked409 artifact/metadata/raw-evidence SHA256 entries with zero
mismatches. [Final controller review](../../B21/controller-review/review.json)
closes actual-TLS inference and the PostgreSQL post-dispatch command window;
[both real protocol traces](../../B21/package-matrix/dispatch-order-readback.json)
also satisfy the stricter assertion. No source/controller finding remains open.

B21 is accepted for Linux x64. B22 and B23 started only after this closure,
in separate worktrees with separate ownership. Their actual timed load windows
must be coordinated: fault stress cannot contaminate performance measurements.

### B22 and B23 implementation checkpoint

- B22 matrix/guide `cc88306` is integrated as `921e3d5`. Public API consumer
  `5a30ce7` is integrated as `ea0496f`; its subsequent exact lock/case checkpoint
  `de3fbf0` is ready for integration. These are implementation stages, not B22
  acceptance. The frozen four-row package matrix is in progress.
- The [retained B22 development faults](../../B22/checkpoint-preservation-001.json)
  include an independently witnessed SQLite busy rejection, a child-only libc
  `pwrite64` ENOSPC injection into the actual native SQLite WAL path, successful
  retry/replay/durable-data checks, and an unrelated-file positive control.
  The failed `ptrace` attempt remains explicitly unavailable. Injected libc I/O
  failure does not claim physical disk exhaustion or a power-loss test. Exact
  provider error and separate owner/root observations are still being completed.
- API pilot001–006 preserve their failures: certificate loading, explicit SQL
  null semantics, output-path assumptions, expected post-header HTTP2 abort and
  padded/unpadded metadata. Pilot007 then passed67 SQLite JIT public API checks.
  The fixed matrix adds a PostgreSQL physical-session check. These probes do not
  substitute for the external crash or long-duration rows.
- B23 controller `4b5e057` is integrated as `19a2768`. It reuses A21 clocks,
  histograms and independent-process reporting. Functional-only checks exercised
  create/replay/recovery, fixed keyset paging and1MiB attachment workloads on the
  immutable B21 AOT executable. Timings from these short checks are not performance
  evidence; [raw development receipts](../../B23/checkpoint-preservation-001.json)
  retain their explicit claim limits.
- Managed comparator `c68ec7b` is integrated as `c296495`. Its standalone AOT
  binary has no NativeWeave package/assembly and passed127 independent normal
  workload checks in each of six database/transport cells. Fixed SQL/raw ADO.NET,
  missing DI/diagnostic and global byte-credit profiles remain explicit limits.
  Direct Rust and the remaining comparison/instrumentation profiles are ongoing.
- No timed B23 measurement or B22 long-duration stage has started at this
  checkpoint. The staged owner/root observation profile must be validated before
  its thresholds can support a soak claim.

B23 final acceptance waits for B22.
B24 starts only after B22 and B23 finish.

B22 and pinned D20 require actual 30-minute steady-state, 24-hour regression and
72-hour release-soak profiles. Freeze the workload, seeds and resource thresholds
before each run; persist observations and interrupted durations. A short run does
not satisfy a longer profile. Missing long-duration evidence keeps B22, final B23
acceptance and B24 unaccepted.

Windows and every other platform are deferred outside this run. No all-platform
acceptance or subsequent task package is authorized by this record.

## Next step

Complete the B22 actual fault/public API/resource driver and B23 equivalent
workload/controller/comparator implementations. Freeze actual run profiles and
schedule isolated measurement windows, preserving every raw result and duration.
Transport each completed stage to the existing batch branches and PRs. B24
remains unstarted until B22 and B23 finish; the multi-day soak is not waived.
