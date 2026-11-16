# Task-02 Linux x64 handoff

## Scope and baselines

The current user authorizes all nine Task-02 items, implementation, tests, docs,
commits, remote checkpoints, normal PR review/merge and the existing automatic
preview closeout on Linux x64. Historical research-only text does not revoke that
specific authorization. Do not start Task-03 or add platforms/release packages.

A01/B01 are reused from [Task-01](../Task-01/handoff-linux.md), without repeated
implementation or historical acceptance. NativeWeave baseline is
`10915d26b13a5ffd0b1abbe06d5934dfb0f2d771`; Plan baseline is
`5536d6d02cb7b99cd2100d6e73d701d676547ce2`. Read-only Design remains exactly
`c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`. This platform ledger overlays unchanged
historical research/design bindings; it does not relabel those as product runs.

## Current task status

| Task | Linux state | Verification and independent review |
| --- | --- | --- |
| A02 | Component accepted | 108 commands; 84 exact API/XML symbols; 26 isolated cases and 428 assertions in each JIT/AOT mode; [review](../../A02/review-linux.json) |
| A05 | Component accepted | 39 commands; 26 exact symbols; JIT 69/AOT 70 assertions and 23 independent probes; [review](../../A05/linux-independent-review/review.json) |
| A09 | Component accepted | Final 37 commands; JIT 220/AOT 221 assertions; 14 independent probes; all six findings resolved; [review](../../A09/linux-independent-review/final-review.json) |
| B05 | Component and actual-provider acceptance complete | 30 component commands, 79 symbols, 29 managed assertions per mode; final B02/B03 composition and retirement corrections accepted; [review](../../B05/review-linux.json) |
| B07 | Component accepted | 22 full gates plus 9 focused repair commands; 120 actual-provider codec vectors and 4189 malformed rejections per fixture mode; [review](../../B07/review-linux.json) |
| B09 | Component accepted | 31 commands; 16 native groups; 42 exact Cdecl declarations; JIT 66/AOT 67 assertions; [native review](../../B09/independent-native/review-final.json), [managed review](../../B09/independent-managed/final-review.json) |
| B02 | Component accepted | Final 27 commands; 11 actual PostgreSQL groups and 22 managed assertions per JIT/AOT mode; [review](../../B02/review-linux.json) |
| B03 | Component accepted | Final 33 commands; 14 actual SQLite groups and 36 managed assertions per JIT/AOT mode; 29 symbols; [review](../../B03/review-linux.json) |
| B06 | Component and actual-provider acceptance complete | 24 commands; 598 assertions and 58 recorded cases in each JIT/AOT mode across both providers; [review](../../B06/review-linux.json) |

B05/B06 acceptance dependencies are closed inside this batch using its actual
PostgreSQL 18.0 and SQLite 3.51.3 adapters. B02's framed response-loss proxy observes
server COMMIT plus idle ReadyForQuery, discards the replies, and another connection
proves a durable row while the client remains Unknown after local retirement.
Both providers consume the transaction parent lease before deciding whether to
join the final physical lease. SQLite's actual worker acknowledgement is observed;
an OS thread JoinHandle join is not claimed.

B06 records a maximum of two retained provider rows including receiver handoff,
2084 conservative reserved native bytes, and 252 native-wire/managed-copy bytes.
Successful cleanup reaches zero live cursor reservations, batch owners, managed
calls and copies; same-session reuse is checked. These owned budgets are separate
from recorded process RSS and CLR allocation measurements. B06's actual run binds
B03 `22e077e`; the later `c1d249b` only rejects zero/unrepresentable acquisition
deadlines before I/O, with its own final provider receipt. The valid five-second
B06 path is unchanged. Exact source/stream/artifact audits are in
[provider-stream-evidence-audit-linux.json](provider-stream-evidence-audit-linux.json).

The retained history includes original false assumptions and failing regressions,
not only successful reruns. B05's original dirty shared Cargo-manifest fact remains
in its receipt; the exact same bytes are subsequently committed in `7c279861`.
A09's original formal pass was superseded by independent findings and two verified
repair runs. [Retention inventory](evidence-retention-linux.json) and the
[A09/B03 retention mapping](retention-a09-b03/inventory.json) locate original bytes.

Full B04 owning-host composition and pristine package consumption remain their
explicit downstream gates. There are no fake public host types, managed SQL engine,
new consumer Cargo dependency or new release package. Other platforms remain
unexecuted, global/all-platform acceptance is false, and implementation plus Linux component acceptance are complete. Batch PR/CI/publication closeout remains pending.

## Worktrees, commits and recovery

ROOT is `/workspace/scratch/0898a75257bc`. Batch worktrees are
`ROOT/.worktree/Task-02-linux/{NativeWeave,Plan}`, both on `task/Task-02-linux`.
Each task uses `ROOT/.worktree/Task-02-<ID>-linux/NativeWeave` and its own
`task/Task-02-<ID>-linux` branch. The sibling Design worktree is pinned and read-only.
Only the main executor integrates the shared solution, Cargo and build entries.

[status-linux.json](status-linux.json) records owners, source checkpoints, integrated
commits and completed B09 integration. All nine subtask branches now have remote source
checkpoints; see [remote-source-checkpoints-linux.json](remote-source-checkpoints-linux.json).
All nine contain their final source trees; the earlier B09 checkpoint remains mapped as history.
Git Data publication preserves identical Git trees but creates different commit
identities. Restore the mapped remote tree and retain the original receipt SHA;
do not rewrite evidence as if it ran at the remote commit identity.

Implementation PR: https://github.com/IzuSharp/NativeWeave/pull/13 (Draft).
Current remote checkpoint `25692f957adbf49430b26de8f6b2ece92418e058` has exactly tree
`155c26f13aa8cfb9ec3af68914e6cd879303f458` of local
`30c726aab64ab418d40364c8aa5ad9229d68dd78`. Normal CI on this final tree passed: https://github.com/IzuSharp/NativeWeave/actions/runs/43840288797.
The complete combined build passed. Subsequent CI found two verification issues:
a checker dictionary layout and a SQLite cancellation test's timing assumption.
[Formatter follow-up](ci-final-format/result.json) proves unchanged non-whitespace
bytes and a passing compiled API check. The
[SQLite follow-up](../../B03/linux-ci-cancellation-repair/independent-review/review-final.json)
accepts a test/docs-only correction with unchanged production inputs. It establishes
both stopped-EOF and actual in-worker Interrupted paths, plus a 5,000-row fresh
operation after stale cancellation. All 11 focused commands, actual JIT/AOT
provider cases and independent source/log/artifact audits passed. Its original
receipt is accompanied by an explicit metadata erratum; original bytes remain
untouched. All failed CI evidence is retained.

Plan PR: https://github.com/IzuSharp/Plan/pull/14 (Draft). Continue these same PRs.
The prior remote Plan checkpoint `19f65b29b49d126c9e6a43a07a4818f039fcbbf3` passed
https://github.com/IzuSharp/Plan/actions/runs/43831719009.
This checkpoint retains all nine final Linux component reviews, raw evidence and the final combined build.

Use `ROOT/task02-toolchain/env.sh`: SDK 11.0.100, Rust 1.100.0, PostgreSQL 18.0 and
pinned SQLx. Local offline NuGet configuration does not change repository audit
policy. Temporary PostgreSQL and tests must run within one executor invocation.
Full managed formatting remains the normal CI gate; local folder-only whitespace
checks are not represented as equivalent. The final normal CI result is a remaining merge gate.

## Final combined verification

All six commands passed on the clean, unchanged final integration tree: workspace
Rust formatting, Clippy with warnings denied, Release workspace tests, existing
native-asset build, locked solution restore, and Release build of all 50 projects.
The managed build completed with zero warnings/errors. See the original
[combined receipt and logs](integration-final-linux/result.json). These checks
compose the modules; the separate actual provider and JIT/AOT receipts remain
their acceptance evidence. Local restore uses the documented offline source only;
normal CI retains its existing full formatter and audit policy.

## Next step

Publish this final Plan checkpoint and update both existing PRs with all nine
accepted Linux tasks and actual checks. Mark them ready and merge normally after
required checks/review. Verify the exact main merge CI and existing automatic
HelloWorld-only preview publication plus actual registry JIT/AOT consumption.
Record that final closeout once, without repeating completed component tests or
starting another task package.
