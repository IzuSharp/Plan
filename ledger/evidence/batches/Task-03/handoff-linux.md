# Task-03 Linux x64 handoff

## Final outcome

Task-03 is complete for Linux x64: all seven components are implemented,
integrated and independently accepted; both source PRs are merged; their exact
merge CI passed; and the existing automatic HelloWorld preview was published and
actually consumed through JIT and Native AOT. No component or release work remains.
Do not repeat accepted implementation or historical acceptance. See
[status-linux.json](status-linux.json), the exact
[component evidence index](component-evidence-index.json), and
[final closeout record](closeout-linux.json).

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

Both original PRs and their normal checks are complete:

| Repository / flow | Merged source or version | Actual result |
| --- | --- | --- |
| NativeWeave PR14 | `5ca367a2fa53e0a756b4c5bcb506113d5c1371a1` | [Merge CI 44011124664](https://github.com/IzuSharp/NativeWeave/actions/runs/44011124664) passed |
| Plan PR16 | `1a271fa8e9e958384380a0cec60005ee849874a5` | [PR CI 44012278309](https://github.com/IzuSharp/Plan/actions/runs/44012278309) and [merge CI 44013010013](https://github.com/IzuSharp/Plan/actions/runs/44013010013) passed |
| Existing automatic Release | `0.1.0-preview.7.1` | [Release 44011125473](https://github.com/IzuSharp/NativeWeave/actions/runs/44011125473) and actual publisher succeeded at the exact implementation merge |

The final publication receipt is `published-and-consumed`. Repository signature
verification, unsigned payload equality and real registry JIT/AOT execution all
passed. The registry consumer used an isolated NuGet cache outside the source tree
with a Rust invocation trap. Its `pristineMachine=false` is preserved honestly;
the separate candidate SDK-container receipt establishes Rust absence in that
image and is not relabelled pristine signed-registry acceptance.

The unchanged existing artifact reader passed all 39 consistency checks. It
independently hashes the retained candidate and native asset and ties them to
actual producer/publisher/consumer records; it does not rebuild or repeat package
acceptance. A separate independent review accepted that evidence with no findings.
The complete release artifacts, raw audit records and review are retained in
`NativeWeave-Task03-Linux-Release-preview.7.1.zip`; exact archive, manifest, artifact,
package and review hashes are in the final closeout record. No new component
package or platform was published.

## Worktrees and stop condition

Reuse the existing writable checkout parent as ROOT. Batch worktrees remain
`ROOT/.worktree/Task-03-linux/{NativeWeave,Plan}` on `task/Task-03-linux`.
Task branches/worktrees retain `task/Task-03-<ID>-linux` and
`ROOT/.worktree/Task-03-<ID>-linux/NativeWeave`. The index preserves local/remote
commit mappings; Git Data checkpoints use identical trees with separate commit IDs.
Use pinned SDK 11.0.100 and Rust 1.100.0. Only the main executor integrates shared
solution/Cargo/build files. The sibling Design worktree remains read-only.

This is the single final progress-only checkpoint. Complete its ordinary PR,
merge and merge-CI checks, then stop; GitHub records those checks without a further
self-referential progress commit. The original paired source PRs, source merge CI
and automatic publication/consumption are already complete.

Other platforms, static linking, full A07/Host and later A16/B24 pristine component
package acceptance remain outside this batch. Global historical graphs are unchanged.
Task-04 was not started; do not start it or seek additional work.
