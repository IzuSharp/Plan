# Task-01 Linux handoff

## Scope and authorization

The current user instruction authorizes implementation of **A01, A19, A21 and B01** on Linux x64, including tests, documentation, commits, pushes and PRs. Historical research-only / `not_authorized` text belongs to the prior planning snapshot. This scoped authorization does not authorize other tasks, Windows execution, or publication outside the existing merge workflow.

- Product base: `1e7f8be161e3e208e0c76b168c197c5c24329e1b`.
- Plan input: `050d54cc2433901cbe896f7490af0e94ba631415`.
- Read-only Design input: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
- ROOT: `/workspace/scratch/0898a75257bc`.
- Batch branches in both repositories: `task/Task-01-linux`.
- Batch worktrees: `ROOT/.worktree/Task-01-linux/{NativeWeave,Plan}`.
- State record: [status-linux.json](status-linux.json).

## Initial recovery findings

No existing Task-01 branches, PRs, batch handoff or A/B completion evidence were found. All four packets have empty start and acceptance dependencies. All packet hashes and 84 API input hash entries match the locked Design input. The existing Hello World is reused as bootstrap infrastructure; it is not formal task acceptance. Existing unrelated dirty historical worktrees were left intact.

| Task | Linux state | Owner | Branch / worktree suffix | Evidence |
| --- | --- | --- | --- | --- |
| A01 | In progress | `/root/a01` | `Task-01-A01-linux` | `ledger/evidence/A01/` |
| A19 | In progress | `/root/a19` | `Task-01-A19-linux` | `ledger/evidence/A19/` |
| A21 | In progress | `/root` | `Task-01-A21-linux` | `ledger/evidence/A21/` |
| B01 | In progress | `/root/b01` | `Task-01-B01-linux` | `ledger/evidence/B01/` |

Each suffix identifies branch `task/<suffix>` and worktree `ROOT/.worktree/<suffix>/NativeWeave`. The batch owner alone integrates shared manifests and Plan state.

## Verification and outstanding work

Implementation and tests are underway; no task has passed acceptance yet. The pinned .NET SDK 11.0.100 is available. Rust 1.100.0 was installed for maintainer tests. Linux Native AOT and native dependencies will be checked with actual executable runs. A19 is finite model execution and makes no Native AOT/product-race proof claim. Windows and other platforms are deferred.

## PRs and next step

PR URLs and integrated/pending commit identities will be added when the first implementation stage is available. Continue all four task worktrees, integrate committed stages, archive raw evidence, perform independent review and package-level integration checks applicable to this batch. Do not start Task-02.
