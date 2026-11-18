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
| B22 | implementation_in_progress | task07_requirements external faults/soak; root public API/transport composition | B21: satisfied | None |
| B23 | verification_blocked_on_adverse_diagnosis | linux_environment controller/report; b21_service comparators | B21; A21: satisfied | B22: pending |
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

### B22 short validation and B23 pre-measurement checkpoint

- The final packaged public API matrix `58082e9` is integrated as `68c9cf9`.
  [Final002](../../B22/api-matrix-002/progress.json) passed all four Linux
  SQLite/PostgreSQL JIT/AOT rows:67/68 cases each,270 assertions total.
  [Independent review](../../B22/api-independent-review/review.json) closes exact
  gRPC terminal status/binary metadata and bounded MCP result assertions.
  Earlier final001 and failed development pilots remain separately identified.
- External faults at executed `e042ec4` passed40 cases and428 assertions across
  both providers and runtimes. [Independent review](../../B22/fault-independent-review/review.json)
  binds actual COMMIT dispatch/acknowledgment, replacement backend PID, busy and
  scoped WAL ENOSPC, outbox/attachment/collector crashes and transport resets.
  [Readback](../../B22/fault-independent-review/readback.json) checked62 artifact
  references and40 distinct source/artifact files with zero mismatches.
- The observed app build004 changes only entrypoint accessibility and wraps its
  unchanged Main body on a joined thread. Final native owner counts and Server
  request/payload gauges reach zero after that task/thread are released. Earlier
  ProcessExit observations still retained an application entry task; they do not
  establish a B21 defect. JIT/AOT EventPipe controls witnessed eight normal and
  four pinned handle allocations/releases with zero lost events. Raw traces are
  retained losslessly compressed under `B22/eventpipe-controls-002`.
- Transport final002 at `9f4e142` passed12 cases and88 assertions. The corrected
  HTTP2 hold keeps reading without issuing credit;4096 bytes remain within the
  initial window throughout the actual2.2-second hold. Slow upload checks exact
  durable response bytes/DTO fields. SIGTERM joins while an admitted incomplete
  client remains open. [Independent closure](../../B22/transport-independent-review/review.json)
  binds final receipt-only `8736c72`, integrated `fe4a72c`; successful network
  observations retain their original hashes. Fault receipt-only `0f98145`,
  integrated `3852ed7`, similarly requires exact selected cases and completed
  outer lifecycle before atomically publishing success.
- B23 comparator `be0bf7f` is integrated as `4b66ab4`: managed NativeAOT and
  direct Rust each pass six ordinary DB/transport cells,1518 assertions total.
  [Manifest and readiness](../../B23/comparators-final-001/manifest.json) retain
  exact source/locks/native/executable identities. Comparator-only Kestrel and
  ADO.NET are never selected as product engines. Missing comparator overload,
  DI/diagnostic and maintenance/fault/soak variants remain explicit.
- Controller `e85bc13`, integrated `333f313`, passed66 functional cells across
  all three routes, DB/TLS/HTTP profiles, nine diagnostic modes and matched
  minimal/DI queries. [Report and portable raw archive](../../B23/report-functional-final-002/report.json)
  explicitly make no timing claim. A later narrow review correction `92f9e6b`,
  integrated `b63a198`, pins actual TLS/PG tools and checks the complete attachment
  DTO. All nine affected stream/TLS/PG cells subsequently passed;
  [independent contract review](../../B23/independent-contract-review/review.json)
  closes both findings and preserves original66-cell attribution.
- The first staged-resource controller `509a373`, integrated `cbfbf13`, completed
  an8-second plumbing probe and an actual five-cycle200-second calibration. The
  calibration confirmed155 items/228 operations/outbox/consumer effects, valid
  runtime controls, zero lost trace events and final owner retirement. It is
  **not frozen**. Review requires fresh per-window GCHeapStats anchors and a
  post-sampling dispatch clock check before a corrected calibration is frozen.
- No30-minute,24-hour or72-hour stage has completed. The B23 isolated
  calibration at92f9e6b is now interrupted:95 completed rows, the96th incomplete,
  and102 not run. See the adverse checkpoint below. No confirmation ran.

All retained short-run files and portable archives are inventoried in
[checkpoint-preservation-002](checkpoint-preservation-002.json). Private configs,
ephemeral keys/databases and rebuildable executables are excluded; their exact
identities and reconstruction commands remain in the receipts.

The transported implementation checkpoint is remote
`5ba50435e4bf8298b13a344fd79f8b6e44300efb`, identical tree to local `2783e18`,
with [passing CI44259221284](https://github.com/IzuSharp/NativeWeave/actions/runs/44259221284).
The transported Plan checkpoint is remote
`e4c7e8bff57a999778db07ee1f4235c61afa63aa`, identical tree to local `5cd8057`,
with [passing CI44261121011](https://github.com/IzuSharp/Plan/actions/runs/44261121011).
[Transport identities](transport-checkpoint-003.json) preserve the exact trees.
Both PRs remain Draft. No Task-07 merge or postmerge publication has occurred.

### Adverse measurement and corrected resource-source checkpoint

B23's original frozen198-process calibration retained95 completed rows before
the96th encountered an actual replay500/unequal-body outcome. The adapter emitted
`ok` with the mismatched fields; A21 correctly rejected the functional result,
but its reader/cleanup path stalled beyond the declared operation/cleanup bounds.
The original execution session was interrupted with Ctrl-C and returned130.
Individual orphaned child exit or native retirement is **not** inferred from that
session result. The [interruption record](../../B23/calibration-001/interruption.json)
retains the exact pre-seal summary, raw mismatch and unfinalized application;
the remaining102 rows were not run. The [portable archive](../../B23/calibration-001-preservation.json)
preserves684 files and the exact frozen measurement source bundle (11,399,333
compressed bytes); no unavailable original response bytes are reconstructed.

The completed rows also contain backlog-cap and dispatch-lag invalidities, plus
two unexpected create500 rows. Exact failed keys have no durable operation and
acknowledged effects reconcile; unsuccessful response headers/body were not
retained by the original adapter. [Diagnostic replay inputs](../../B23/adverse-replay-001/replay-recipes.json)
record this limitation without inventing response bytes or bitwise replay.
The prior B22 SQLite busy fixture shows that a provider failure can become generic
HTTP500, but it does not establish the cause of these new benchmark outcomes.

Required fixes remain in B23-owned code: validate complete business outcomes
before emitting success, preserve bounded failed-response evidence, and supervise
cells externally so A21 cleanup cannot hang the package controller. A21 source
is unchanged. No lower-rate profile may hide the original failures, and no
confirmation/performance benefit claim is permitted before diagnosis. Valid
unrelated data remain preserved; a separately reviewed provenance mechanism is
required if independent complete cohorts are reused.

B22 resource source `cb603c1` and `984b9ee` are integrated as `1e9dd94` and
`bcf9795`. [Independent source closure](../../B22/soak-independent-review/source-review-984b9ee.json)
closes representative240s-load/60s-idle calibration, separate qualified post-GC
native baseline, complete directly executed input/mode identity, final hash
rechecks, and independent four-slot attachment metadata/blob oracles. These are
source fixes. Observer006/TraceReader builds and the corrected8.006-second
SQLiteAOT probe subsequently passed, including exact attachment state and both
input rechecks. A fresh900-second calibration is now separately scheduled while
B23 performs source-only controller repairs; it remains unaccepted until complete
and reviewed. Original200-second results retain their509a373 identity.

B23 final acceptance waits for B22.
B24 starts only after B22 and B23 finish.

B22 and pinned D20 require actual 30-minute steady-state, 24-hour regression and
72-hour release-soak profiles. Freeze the workload, seeds and resource thresholds
before each run; persist observations and interrupted durations. A short run does
not satisfy a longer profile. Missing long-duration evidence keeps B22, final B23
acceptance and B24 unaccepted.

Windows and every other platform are deferred outside this run. No all-platform
acceptance or subsequent task package is authorized by this record.


### Recovery continuation 6b7401

The previous session's source work and accepted B21/short B22 results are reused.
Concurrent old-session writes were observed in the original B22/B23 recovery
locations. The current root uses `task/Task-07-recovery-6b7401-linux` in
`ROOT/.worktree/Task-07-recovery-6b7401-linux/`, with separately suffixed B22/B23
worker worktrees. The original branches and raw output directories are preserved.
The original batch branches and PR18/PR22 remain the remote delivery destinations.

Implementation remote `11f9eceb86dd4f9c69fc975db6eb8b3ab40db2cf` and local
`bcf9795df785207e07a27a15509ffbb3f9ea756a` have the same tree
`791cd91b7907dab253c0e5f48893d03c015684d2`;
[CI44264344510](https://github.com/IzuSharp/NativeWeave/actions/runs/44264344510)
passed. Plan local `b60b3b969cf36dcba601205bbb8ae8fc28ef03fb` is ahead of the last
transported checkpoint. Automatic approval review rejected raw binary evidence
uploads, including the runtime trace and original calibration archive. A second
trace attempt after content inspection was also rejected. No alternate egress
path is used. The exact blocked payload hashes and the scope of the safe text-only
checkpoint are recorded in [recovery-6b7401.json](recovery-6b7401.json). Raw payloads
remain in the original local task worktrees and execution directories; this text
checkpoint does not claim they are remotely preserved.

B22 calibration002 stopped at453.459 seconds and003 at535.608015815 seconds.
Neither completed900 seconds or final trace/retirement analysis, and neither is
credited to a fresh process. The prepared calibration004-6b7401 uses a retained
live execution session; its completion is not assumed. A finite detached-process
probe found that ending the originating executor invocation also ended its child.
No durable multi-day execution host has yet been established.

B23 controller repair `7e75906f688ed8864ea206a72e1b22dc4d048e35` passed17 focused
controller tests. Independent review found two further failure-recording gaps;
the supplement is in progress. A new same-native-byte diagnostic reproduced both
create500 and replay500 at the original offered rates. An observation-only AOT
copy identified `DatabaseException(Provider,5)`, SQLite `SQLITE_BUSY`, at matching
request hashes. Confirmed durable effects reconciled and shutdown joined. These
are bounded diagnostic results, not valid performance measurements. The historical
individual failures still lack exception evidence and are not retroactively proven.
The first observer build was interrupted after automatic approval rejected an
action as metadata-network risk. A separate demonstrably offline build, with an
inherited syscall network denial and a positive control, succeeded without a restore.

B21 remains accepted on Linux. B22 long-duration evidence, final B23 acceptance,
and B24 remain incomplete. Both PRs remain Draft; no Task-07 merge or postmerge
preview has occurred. Windows and other platforms are outside this recovery.

## Next step

Complete B23 bounded outcome/evidence/supervision fixes and independently classify
the actual SQLite500/replay mismatch using the same native product bytes in a
fresh isolated diagnostic execution. Build/probe the corrected B22 observer, then
coordinate its900-second calibration and real30m/24h/72h profiles with subsequent
performance windows. Preserve original adverse data. Transport each stage to the
same branches/PRs. B24 remains unstarted; the multi-day soak is not waived.
