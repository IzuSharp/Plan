# Task-01 Linux final handoff

## Result and scope

**A01, A19, A21 and B01 are complete for their Linux x64 scope, independently reviewed and integrated.** The final implementation CI passed. This checkpoint includes the sanitized raw execution results, event streams, logs, source identities, review outcomes and batch recovery records. The published raw-evidence checkpoint `cd992c6f965e6b00c198b45229d97b9a2fc935f8` passed the existing Plan `paired-integrity` check. Task-01 Linux delivery is complete and is handed off for normal PR review.

PLATFORM=`linux`, RID=`linux-x64`. All four tasks have empty start/acceptance dependencies and were developed in separate worktrees. No package-external task or new platform/CI matrix was implemented. Other platforms remain unexecuted; global acceptance remains false.

## Inputs and authorization

| Input | Locked commit |
| --- | --- |
| Plan | `050d54cc2433901cbe896f7490af0e94ba631415` |
| Read-only Design | `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9` |
| Product base | `1e7f8be161e3e208e0c76b168c197c5c24329e1b` |

The four task packet hashes and84 API input entries match the locked Design. Historical normative graphs and accepted research bindings remain unchanged. The user's original Task-01 request explicitly authorized implementation, necessary tests/docs, commits, pushes and PR updates. After the exact sanitized evidence scope and automatic-tool-review rejection were explained, the user explicitly instructed continuation. No omitted implementation/probe source payload was restored or moved elsewhere.

## Completed components

| Task | Owner | Actual Linux verification | Evidence |
| --- | --- | --- | --- |
| A01 | a01 | 47 successful full-run commands; C/Rust/C# layout/signature checks;682 assertions each JIT/AOT; mutation controls and six supplemental locked restores | [Summary](../../A01/summary-linux.md), [accepted run](../../A01/attempt-005/result.json), [lock supplement](../../A01/restore-compatibility-001/result.json) |
| A19 | a19 | Five bounded lifecycle models;11 unsafe controls with replayable counterexamples;18 regressions;independent liveness/mailbox checks | [Summary](../../A19/summary-linux.md), [run](../../A19/linux-committed-1/run.json) |
| A21 | root | 24 successful full-run commands;19 regressions;three actual routes in six fresh processes;600 requests/1200 raw events; six supplemental locked restores | [Summary](../../A21/summary-linux.md), [accepted run](../../A21/attempt-003/result.json), [final source binding](../../A21/final-source-binding.json) |
| B01 | b01 | 132 exact API/XML symbols;12 JIT/AOT families;10 goldens;43 malformed cases;four expected compile failures;isolated NuGet JIT/AOT;Rust trap0 | [Summary](../../B01/summary-linux.md), [accepted run](../../B01/run-4/summary.json), [format supplement](../../B01/formatting/source-binding.json) |

All material independent findings were resolved. Final accepted source hashes match101 owned integrated paths with zero mismatches. Every listed integration commit is an ancestor of the final implementation checkpoint. The B01 formatter-only delta preserves all C# tokens, literal values and non-whitespace trivia. Original failures and successful runs retain their actual source identities; supplements are not described as new full runtime runs.

A19 results retain explicit finite bounds/fairness. A21's scalar fixtures validate the controller and make no Database/ORM/Server performance or memory-superiority claim. Existing Hello World gates are reused and do not count as completed A/B tasks. No A13 or downstream package/domain/release acceptance is asserted.

## Integrated checks

- Local implementation commit: `39d3dc3bde90304cf8baf6d59bbfa75959cc8ed5`
- Remote equivalent: `22fe70a66312f1a8ec0767d244e3b74762e7ff99`
- Verified common tree: `814094f77140c01068ac82514709c4dc208360cf`
- [Implementation CI43811091217](https://github.com/IzuSharp/NativeWeave/actions/runs/43811091217): passed all jobs.

The existing CI passed native formatting/Clippy/tests, locked solution restore/build, full C# formatting, API/package checks, actual NativeAOT consumers, fresh Linux SDK-container consumption without Rust, source/dependency drift and security jobs. Local final solution build passed. Local full formatting hit a denied IPC pipe; it remains recorded as environment-blocked locally, while the unchanged formatter subsequently passed in GitHub CI.

Pinned SDKs: .NET11.0.100 and Rust1.100.0. Actual compiler-driver/linker identities are distinct and hash-recorded in component evidence. Local offline restores used cached Microsoft SDK packages and do not claim an audit-data refresh. Existing CI audit/release policy is unchanged.

The shared solution has14 unique projects/assemblies. All22 B01 accepted lock entries and activated Linux features are preserved. Hello World's exact native asset remains dependency-free. Shared integration was serial and minimal. Completed component suites were not repeated merely because the batch was still in progress.

The previous nine-document Plan summary at `88ce0f18a780445b04e56dd52c74c8d2d3756f7b` passed [CI43812171263](https://github.com/IzuSharp/Plan/actions/runs/43812171263). The published raw-evidence checkpoint `cd992c6f965e6b00c198b45229d97b9a2fc935f8` passed [Plan CI 43813848789](https://github.com/IzuSharp/Plan/actions/runs/43813848789), including the existing provenance and graph gates. Its tree `43ff9a7ae65ef5ace3a9c50e0020ee5a43963ee2` exactly matches local checkpoint `3b589fc4e15f78ca98bc3891b29fadf3e7eafe37`, verified by Git fetch. No historical native experiment or completed component suite was rerun during this closeout.

The remaining changes in this closeout are batch handoff/status/publication metadata only. The Plan PR description records the final check on that documentation commit; the linked PR checks remain authoritative for their current heads. The stored evidence run is not a substitute for a check on a different head.

## Archive availability and publication history

Two automatic tool-review rejections are retained as historical events. A smaller nine-document summary was published successfully. Following the user's explicit continuation instruction, the already-described sanitized logs/results/metadata/hash archive was published successfully in `cd992c6f965e6b00c198b45229d97b9a2fc935f8`. The publication blocker is resolved; the two rejections remain historical records.

[Evidence publication policy](evidence-publication-policy.json) enumerates omitted full implementation/probe source, build configuration, duplicate schema and binary payloads. Original execution/review manifests remain byte-identical and may name those omitted local files; their names/hashes do not imply remote availability. [Raw evidence receipt](raw-evidence-receipt-linux.json) and [per-file hash index](raw-evidence-index-linux.json) bind the retained records. Detailed author handoffs retain their original checkpoint context; this batch handoff and task summaries provide the final integration state.

Git-data API publication is used because ordinary HTTPS push lacks credentials. Every published tree is checked against its corresponding local committed snapshot; local and remote commit IDs are recorded separately. No merge, version bump or package publication was performed.

## Recovery and PRs

ROOT: `/workspace/scratch/0898a75257bc`.

| Purpose | Branch | Worktree relative to ROOT |
| --- | --- | --- |
| NativeWeave batch | `task/Task-01-linux` | `.worktree/Task-01-linux/NativeWeave` |
| Plan batch | `task/Task-01-linux` | `.worktree/Task-01-linux/Plan` |
| A01 | `task/Task-01-A01-linux` | `.worktree/Task-01-A01-linux/NativeWeave` |
| A19 | `task/Task-01-A19-linux` | `.worktree/Task-01-A19-linux/NativeWeave` |
| A21 | `task/Task-01-A21-linux` | `.worktree/Task-01-A21-linux/NativeWeave` |
| B01 | `task/Task-01-B01-linux` | `.worktree/Task-01-B01-linux/NativeWeave` |

Implementation PR: https://github.com/IzuSharp/NativeWeave/pull/12

Plan PR: https://github.com/IzuSharp/Plan/pull/12

[Status](status-linux.json) lists owners, all integrated commits, author/remote checkpoints and final checks. [Publication mappings](publication-checkpoints.json) retain exact tree correspondences. [Verification summary](verification-summary-linux.json) records actual scope and results.

## Completed handoff and next step

The sanitized evidence is published and its Plan check passed. All four Linux components are complete, with no pending integration commit or external Task-01 blocker. Both existing PR descriptions identify the completed Linux scope and published evidence. Plan PR readiness follows its successful current-head check; review and merge remain under the existing repository process.

No further Task-01 implementation or component acceptance work is scheduled. Resume from the linked PRs only if a new check or review finding requires action within this scope. Stop after Task-01; do not start Task-02.
