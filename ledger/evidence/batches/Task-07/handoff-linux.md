# Task-07 Linux x64 handoff

## Scope and current state

The current user explicitly authorizes B21, B22, B23 and B24 on Linux x64,
including implementation, necessary verification, documentation, independent
review, commits, pushes, draft PRs, checked merges and the existing postmerge
preview closeout. Historical research-only graph fields remain historical;
this platform ledger records the authorized product work. Design is read-only.

| Task | Linux state | Owner | Start dependencies | Acceptance dependencies |
| --- | --- | --- | --- | --- |
| B21 | implementation_in_progress | b21_service; root integration/tests | B04, B08, B13, B14, B15, B17: satisfied | B20: satisfied |
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
- Implementation PR: not created yet; first reviewable product change pending.
- Plan PR: not created yet; this is the initial recovery checkpoint.
- Integrated Task-07 implementation commits: none yet.
- Pending Task-07 implementation commits: none yet.

## Verification and remaining sequence

The initial read-only dependency audit found all external Linux prerequisites
satisfied. No new B21–B24 runtime or acceptance result is claimed at this checkpoint.
The required maintainer tools and isolated database environment are being restored;
building already accepted component assets is preparation, not new acceptance.

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
