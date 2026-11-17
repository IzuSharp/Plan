# Task-03 Linux x64 handoff

## Outcome and remaining closeout

All seven components are implemented, integrated and independently accepted for
Linux x64. The latest local acceptance checkpoint has been recovered; old pending
states are superseded by [status-linux.json](status-linux.json) and the exact
[component evidence index](component-evidence-index.json). Do not repeat accepted
implementation or historical acceptance. Batch closeout is still pending the Plan
merge and existing automatic preview consumption. Exact implementation-merge CI passed.

The user authorizes this Task-03 delivery and normal paired PR/release closeout.
Read-only Design remains exactly `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
Implementation baseline is `22b467667bcf44aa8b22e964937446b225e87e61`; Plan baseline
is `7bd04e898344cadc1ae4b331202b4908449f4446`. A01 is reused from
[Task-01](../Task-01/handoff-linux.md); A02/A05/A09 from
[Task-02](../Task-02/handoff-linux.md). All start dependencies are met and the graph
adds no further acceptance prerequisite for these seven component scopes.

## Component results

| Task | Linux state | Accepted verification |
| --- | --- | --- |
| A03 | Accepted and integrated | JIT 97 / AOT 98; admission/retirement schedules, rollback, finalizer and zero live resources |
| A04 | Accepted and integrated | JIT 9,635 / AOT 9,636; 4,778 extent descriptors, retained backing, cancellation/failure and 23-symbol API |
| A10 | Accepted and integrated | 38 commands; 40 generator/API assertions; real JIT/AOT and independent local transitive NuGet consumption |
| A11 | Accepted and integrated | 36 commands; 20 emitter assertions; real C/Rust ABI/export checks, JIT/AOT and incompatible compiler negatives |
| A12 | Accepted and integrated | Original package JIT/AOT and framework negatives; follow-up 48 cases / 157 assertions and real metadata composition |
| A13 | Accepted and integrated | Reproducible native/MSBuild provenance, failure/cancellation checks, JIT/AOT, compiled XML/API and pinned DocFX |
| A22 | Accepted and integrated | 92 commands; 20 JIT/AOT rows, 27 policy, 15 signature and 6 dependency-closure cases; complete rollback |

The evidence index binds each task to original source identities, receipt hashes,
independent-review hashes, actual outcomes and narrow evidence-reuse boundaries.
A03's original dirty lock-registration receipt remains unchanged. A12 follow-up
results and A13's later DocFX/MSBuild targeted checks are not represented as full
reruns on different source. Core compatibility fixtures are distinct from actual
signed HelloWorld preview checks. No unresolved independent finding remains.

## Original evidence retention and recovery

Automatic approval rejected large raw A22 evidence uploads to public GitHub.
After target/authorization inspection and default-rule secret scanning, a later
raw batch was still rejected. The safer disposition is a bounded public evidence
index and complete private retention of the original committed bytes. No rejected
raw payload is sent through another public channel. This changes retention only;
it does not change or recreate any acceptance receipt.

The exact original Plan commit is `e89ff8de234f0aa6c7484c86ebca138c44660579`, tree
`290b8054535033e5aeced2139dd8c8748ddb0816`. It is saved in the private archive
`NativeWeave-Task03-Linux-Evidence-e89ff8d.zip`, with archive/manifest/bundle hashes
in the evidence index. The archive contains the exact incremental Git bundle,
restoration instructions, original failure and success records, all independent
reviews, and the narrow CI-repair review. Existing already-public historical
records are preserved; the new raw evidence is not all in this public PR tree.

For raw detail, recover the archive by its exact filename and SHA-256 and follow
`RESTORE.txt` into a separate worktree. Verify the original commit/tree, then read
the index's `archive_path` entries. An unavailable private archive is an evidence
access blockage, not pending implementation. Do not rerun components to compensate.

## CI repair and merged implementation

Implementation PR: https://github.com/IzuSharp/NativeWeave/pull/14

Plan PR: https://github.com/IzuSharp/Plan/pull/16

CI https://github.com/IzuSharp/NativeWeave/actions/runs/44006785218 failed on 1,052
WHITESPACE diagnostics in two Interop.Memory test files. The repair changes only
whitespace. Independent Roslyn comparison confirms all 4,521 tokens, literal
values, comments/directives and syntax are identical; see
[ci-formatting-review.json](ci-formatting-review.json). No check was weakened.

Repair remote `b0494bbc1b42ca7bb6620bae57594b3ec53276a7` equals local
`f14bb08a2285154f8c035216fa61fd9cb1fe9612`, tree
`7dcd3680e0339ffb27e28110ad696a7b0a168523`. Its normal
[PR CI 44010305466](https://github.com/IzuSharp/NativeWeave/actions/runs/44010305466)
passed all build/package/API/AOT, Rust-free SDK container, drift and security gates.
PR14 merged normally as `5ca367a2fa53e0a756b4c5bcb506113d5c1371a1`.

Exact-merge [CI 44011124664](https://github.com/IzuSharp/NativeWeave/actions/runs/44011124664)
passed on the actual merge commit. [Release 44011125473](https://github.com/IzuSharp/NativeWeave/actions/runs/44011125473)
passed candidate/security gates and is publishing. Its identity allocated
`0.1.0-preview.7.1`; completed publication and registry consumption are not yet
claimed. The existing release scope is HelloWorld/Linux x64.

## Worktrees and next step

Reuse the existing writable checkout parent as ROOT. Batch worktrees remain
`ROOT/.worktree/Task-03-linux/{NativeWeave,Plan}` on `task/Task-03-linux`.
Task branches/worktrees retain `task/Task-03-<ID>-linux` and
`ROOT/.worktree/Task-03-<ID>-linux/NativeWeave`. The index preserves local/remote
commit mappings; Git Data checkpoints use identical trees with separate commit IDs.
Use pinned SDK 11.0.100 and Rust 1.100.0. Only the main executor integrates shared
solution/Cargo/build files. The sibling Design worktree remains read-only.

Finish Plan PR16 checks and normal merge, automatic preview
publication/signature/payload verification and actual registry JIT/AOT consumption.
Record one necessary final closeout checkpoint, merge/check it normally, and stop.
Other platforms, static linking, full A07/Host and later A16/B24 pristine component
package acceptance remain outside this batch. Global historical graphs are unchanged.
Do not start Task-04 or publish new component packages.
