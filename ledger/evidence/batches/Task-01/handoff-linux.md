# Task-01 Linux handoff

## Status

**All four Linux x64 implementations and component reviews are complete and integrated. Implementation CI passed. Full batch delivery remains incomplete because automatic tool review blocked publication of the raw evidence archive to Plan.**

This remote checkpoint contains only four task summaries, batch status, publication mappings, verification results and aggregate evidence digests. Raw stdout/stderr/log/JSON/JSONL files remain in the local committed Plan worktree; they are not claimed to be remotely available. Full implementation/probe source, build configuration and binary copies have been removed from the proposed raw archive. The reduced raw archive was also rejected, so it is not being retried without specific approval.

## Scope and inputs

Task-01 includes A01, A19, A21 and B01 only. PLATFORM=`linux`, RID=`linux-x64`. Each has empty start and acceptance dependencies; all were started in separate worktrees. The user explicitly authorized this package's implementation, tests, documentation, commits, pushes and PR updates. Historical research-only statuses remain the previously accepted planning snapshot, not a revocation of this authorization.

- Plan input: `050d54cc2433901cbe896f7490af0e94ba631415`
- Locked read-only Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`
- Product base: `1e7f8be161e3e208e0c76b168c197c5c24329e1b`
- Four task packet hashes and 84 API input entries match the lock. The normative graphs/baselines are unchanged.

## Completed Linux work

| Task | Owner | Verified result | Summary |
| --- | --- | --- | --- |
| A01 | a01 | C/Rust/C# layout/signature controls; 682 assertions each JIT/AOT; six supplemental locked restores | [A01](../../A01/summary-linux.md) |
| A19 | a19 | Five bounded lifecycle models, 11 unsafe controls, 18 regressions and independent graph checks | [A19](../../A19/summary-linux.md) |
| A21 | root | Three actual routes, six process cells, 600 requests/1200 raw events, 19 regressions | [A21](../../A21/summary-linux.md) |
| B01 | b01 | 132 exact API/XML symbols, 12 JIT/AOT families, 10 goldens, 43 malformed cases, four compile negatives, isolated NuGet JIT/AOT | [B01](../../B01/summary-linux.md) |

The independent final source audit found zero mismatches across 101 owned integrated paths. All original failed attempts, findings and successful run identities remain locally retained. The B01 formatting supplement changes only whitespace and independently preserves all C# tokens/literals/non-whitespace trivia. No completed module suite was rerun merely to repackage the batch.

A19 results retain finite bounds and fairness assumptions. A21's scalar fixture validates the harness; it does not claim Database/ORM/Server performance superiority. Existing Hello World assets are reused as integration gates, not counted as completed A/B work. A13 and downstream package/domain tasks are not marked complete. Other platforms were not executed; global acceptance remains false.

## Integrated implementation and checks

- Local integrated commit: `39d3dc3bde90304cf8baf6d59bbfa75959cc8ed5`
- Remote integrated commit: `22fe70a66312f1a8ec0767d244e3b74762e7ff99`
- Exact matching tree: `814094f77140c01068ac82514709c4dc208360cf`
- Successful current-head CI: https://github.com/IzuSharp/NativeWeave/actions/runs/43811091217

CI passed the native checks, locked restore, solution build, full formatter, API/package checks, actual NativeAOT consumers, fresh Linux SDK container without Rust, source/dependency drift check and all security jobs. Local final solution build passed. The local full formatter encountered denied named-pipe creation; this is recorded as environment-blocked, while the unchanged formatter later passed in CI.

Pinned toolchains: .NET SDK 11.0.100 and Rust 1.100.0. Offline local restores used cached Microsoft SDK packages with no audit-refresh success claim. Existing CI audit/release policy is unchanged. The solution has 14 unique projects; B01's 22 dependency-lock entries/features are preserved; Hello World's exact native asset remains dependency-free. No release or merge was performed.

## Recovery locations

ROOT in this environment: `/workspace/scratch/0898a75257bc`.

| Purpose | Branch | Worktree relative to ROOT |
| --- | --- | --- |
| NativeWeave batch | `task/Task-01-linux` | `.worktree/Task-01-linux/NativeWeave` |
| Plan full local evidence | `task/Task-01-linux` | `.worktree/Task-01-linux/Plan` |
| Subtasks | `task/Task-01-A01-linux`, `task/Task-01-A19-linux`, `task/Task-01-A21-linux`, `task/Task-01-B01-linux` | `.worktree/Task-01-<ID>-linux/NativeWeave` |

Implementation PR: https://github.com/IzuSharp/NativeWeave/pull/12

Plan PR: https://github.com/IzuSharp/Plan/pull/12

[Status](status-linux.json) records exact integrated/author commits and pending work. [Publication mappings](publication-checkpoints.json) distinguish local commit IDs from remote equivalents and verify equal Git trees. [Verification summary](verification-summary-linux.json) states actual results. [Raw evidence receipt](raw-evidence-receipt-linux.json) records aggregate identities and the explicit local-only retention boundary.

GitHub Git-data publication is used because ordinary HTTPS push lacks credentials. Every published checkpoint is compared against its own local snapshot tree; the remote summary tree is not described as the larger unpublished raw-evidence tree.

## Remaining step

The implementation is ready for normal review. Keep Plan delivery marked incomplete until the reduced raw validation logs/results/hashes can be published to the existing Plan PR and the final current-head checks pass. Automatic tool review—not a repository maintainer or GitHub code reviewer—blocked that write. The smaller summary checkpoint preserves the recovery state without publishing the rejected payload.

After this publication block is resolved, finalize Plan PR readiness and stop at Task-01. No component reimplementation, unrelated historical rerun or next package is required.
