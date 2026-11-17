# Task-03 Linux x64 handoff

## Scope and recovered baseline

The current user authorizes Task-03 A03, A04, A10, A11, A12, A13 and A22 implementation,
necessary verification/documentation, separate worktrees, commits, remote checkpoints,
normal PR review/merge and the existing automatic preview closeout for Linux x64.
Historical research-only authorization fields remain historical and do not revoke this
specific scope. Other platforms are unexecuted; global acceptance remains false.

Implementation starts from `22b467667bcf44aa8b22e964937446b225e87e61` and Plan from
`7bd04e898344cadc1ae4b331202b4908449f4446`. Read-only Design is exactly
`c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9` as locked by Plan. Remote branch/PR search
found no earlier Task-03 checkpoint. Older local design checkouts were reused; the
product and Plan were restored from their current remote main commits.

A01 is reused from [Task-01](../Task-01/handoff-linux.md); A02, A05 and A09 are reused
from [Task-02](../Task-02/handoff-linux.md). Their accepted component evidence and
completed merge/CI/preview results are not rerun or relabelled. All seven Task-03
start dependencies are satisfied; the graph has no extra acceptance dependency for
these tasks. A10/A11 may use explicitly labelled component conformance fixtures;
actual later host/dependency-closure acceptance stays with its named downstream owner.

## Current task status

| Task | Linux state | Owner | Next step |
| --- | --- | --- | --- |
| A03 | Component passed; independent review closing | Lifetime worker / main reviewer | Final review and batch integration checks |
| A04 | Component passed; independent review closing | Lifetime worker / main reviewer | Final review and batch integration checks |
| A10 | Implementation and independent review fixes | Bindings worker | Correct nullable/retained ownership and names; formal package/AOT checks |
| A11 | Formal run completed; independent review fixes | Bindings worker | Correct accepted identifiers and negative assertion helper; revalidate |
| A12 | Component passed; review pending | Analyzers worker / main reviewer | Independent review and actual A10 metadata composition |
| A13 | In progress | Main executor | Maintainer build/provenance, compiled reference/DocFX and shared registrations |
| A22 | In progress | Analyzers worker | Compatibility matrix and immutable signed closure validation |

A03, A04 and A12 are integrated into the batch checkpoint. Their exact source trees
are also saved on their named remote task branches. Original local test commit IDs
remain in the unmodified receipts; [status](status-linux.json) maps remote checkpoint
commits separately. No complete Task-03 or all-platform acceptance is claimed.

## Actual evidence and open review

- [A03 formal receipt](../../A03/run-20261117T021812Z/result.json): JIT 97 / AOT 98 assertions,
  controlled acquire/close schedules, finalizer/in-flight checks, zero live resources,
  and allocation-free warmed synchronous calls. The earlier failed lock restore is retained.
  A later narrow clarification makes finalizer-context ownership explicit; it does not
  claim a full rerun of the earlier receipt. A04's later run compiles that clarified owner.
- [A04 formal receipt](../../A04/run-20261117T022403Z/result.json): JIT 9,635 / AOT 9,636 assertions,
  4,778 descriptor comparisons, retained backing charges, pending async write/cancellation,
  exact API/XML and real JIT/AOT samples. Final resource/backing/capacity counters are zero.
- [A12 formal receipt](../../A12/formal-1/result.json): 24 commands, 45 scenarios and 152
  assertions, deterministic rerun, local package installation, real native JIT/AOT and
  framework IL2026/IL3050 negative consumers. Preparation failures remain available.
- Independent A10/A11 probes identified real generator edge cases and a unit-test helper
  that could catch its own failure sentinel. Authors are fixing both implementation and
  tests. The earlier positive actual runs remain evidence, but affected negative assertion
  counts are not final acceptance. Final review must bind corrected source and new receipts.
- A13 has actual cold/incremental/parallel native, stale/failed/cancelled build probes and
  compiled Core XML/API-to-DocFX output. These are development runs pending final clean
  source, remaining integration and independent review. A22 is validating actual historical
  HelloWorld repository signatures and clearly labelled old/current Core component fixtures.

Raw retained logs and SHA inventories live in the original task evidence directories.
Compiled binaries are omitted from git; receipts retain their hashes and exact source,
commands, pins and reproduction paths. This is component evidence, not pristine-machine,
all-platform, released-Core or later Host acceptance.

## Worktrees and integration

ROOT is `/workspace/scratch/58d2a6adf1c3`. Batch worktrees are
`ROOT/.worktree/Task-03-linux/{NativeWeave,Plan}`, both using `task/Task-03-linux`.
Each subtask owns `ROOT/.worktree/Task-03-<ID>-linux/NativeWeave` and
`task/Task-03-<ID>-linux`. The sibling batch Design worktree is pinned and read-only.
Only the main executor changes shared solution, Cargo and build registration files.
The existing Cargo workspace is at repository root; A13 integrates that actual path
instead of creating a conflicting `native/Cargo.toml` workspace.

[Status](status-linux.json) tracks owners, commits, evidence and integration.
Use `source ROOT/task03-toolchain/env.sh`: .NET SDK 11.0.100, Rust 1.100.0 and
Clang 19.1.7 are restored and version-verified. See the task receipts above for actual runs.
HTTPS fetch is available; direct push has no credentials. The Git data API saves
remote checkpoints with exact tree equality; source receipts retain their actual
local commit identity and the status file maps it to the remote checkpoint.

Implementation Draft PR: https://github.com/IzuSharp/NativeWeave/pull/14.

Plan Draft PR: https://github.com/IzuSharp/Plan/pull/16.

## Next step

Complete the seven owned components, their documentation and actual Linux verification.
Integrate and independently review each completed component while other ready work
continues. Continue updating the existing paired Draft PRs and remote task checkpoints. After required checks/review pass, merge normally, confirm exact-merge
CI and the existing automatic preview/consumption, record necessary closeout and stop.
Do not start another task package or extend the release/platform scope.
