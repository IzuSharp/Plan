# Review after the primary cleanup permission stop

Observed at **2026-11-26 14:59:53 UTC**. This is an independent read-only review
of the failed cleanup receipt, retained state, remaining top-level paths and
non-platform filesystem metadata. No deletion, chmod/chown, process signalling,
benchmark or build was performed. Platform control directory contents and
credentials were not read.

## Observed partial result

The original helper remains unchanged at SHA-256
`79088224364dd5b1321e83c30aa462a2e3bd79efc7e1a692b3638257b4cdabb7`.
The primary receipt has status `refused-or-partially-completed`, not success:

- Receipt SHA-256:
  `566a4b738cbe5da5c876ee4a14fe669cc8cc111bf64741c715d276b62ad013b4`.
- Retained state SHA-256:
  `ffd76ed4b6ebbe02a0b28255aceec327da0dc4e603df2aed3884ef628add2fb0`.
- **94 completed actions**: 62 worktree removals/unregistrations and 32 temporary
  target actions. All 94 recorded action paths were observed absent afterward.
- `processActions=[]`; the primary receipt records no process termination.
- The completed supplemental receipt contains three more worktree removals,
  making **65 removed worktrees** across the two helpers.
- The first primary root deletion stopped on
  `/workspace/scratch/fd78534029f7/.codex` with `PermissionError` / EACCES.

All three primary roots still exist. Each has a top-level platform control
directory owned by UID/GID 65534, whereas the cleanup process is UID 1000.
These platform directories and their containing roots should be preserved.
The original failure receipt/state must not be rewritten as success.

## Remaining task content

All other remaining top-level entries were owned by UID 1000 and were regular
files or directories, with no top-level symlinks. No target/nested mount was
observed under the three roots.

| Root suffix | Non-platform top-level entries | Non-platform directories | Regular files | Internal symlinks |
| --- | ---: | ---: | ---: | ---: |
| `fd78534029f7` | 1 | 10 | 61 | 0 |
| `4a65d70f0fe1` | 7 | 6,068 | 64,081 | 2,129 |
| `166b48a091b9` | 17 | 2,407 | 24,687 | 0 |

The first root contains only the task `publication` directory outside the
platform control area. The second still contains `artifacts`, `consumers`,
`measurements`, `repos`, `tools`, `validation-evidence` and the empty worktree
container. The third still contains Go inputs/results/toolchain, archives,
publication/recovery records and task containers. These are real remaining
project contents, so the interrupted primary cleanup did not finish the user's
source/cache removal request.

The metadata walk found no foreign-owned directories or special filesystem
nodes in those non-platform subtrees and no traversal error. Internal symlinks
must be removed as links, without following their destinations; the continuation
must retain symlink-resistant recursive deletion rather than relying only on
top-level path checks.

## A second, distinct permission condition

The platform control directory is **not the only permission obstacle**. There
are **198 UID-1000-owned, mode-0555 directories** under:

`/workspace/scratch/166b48a091b9/go-comparison-01/toolchain/modcache`

The exact metadata is in
`primary-cleanup-readonly-cache-observation.json`. These are downloaded Go module
cache directories. Ordinary `rmtree` will encounter a further permission error
when attempting to remove their contents. They must not be silently omitted
while claiming the entire source/cache cleanup is complete.

The already-present Go toolchain source confirms that `go clean -modcache`
invokes `modfetch.RemoveAll` for `cfg.GOMODCACHE`; that standard cache removal
routine adjusts downloaded module directory modes before removing them. If the
root uses that ordinary cache-maintenance operation, it must bind it to this
exact task cache, keep the platform-owned directories excluded, and record the
actual command/result. It must not claim that this operation makes no mode
changes. No such operation was run by this reviewer.

## Assessment of the narrower continuation

Removing only the currently observed non-platform children of the three
already-authorized roots is a materially narrower and appropriate continuation.
Preserving the platform-owned control directories does not require changing
their ownership or permissions. Bind each child to lstat identity, reject
symlinked ancestors and nested mounts, preserve no-follow deletion semantics,
and require no active task writer. Preserve the existing archival evidence gates
and record the new operation separately from the failed original helper.

The current visible project entries would all be covered by that narrowed
child list. Completion still depends on actually removing the read-only module
cache through its normal maintenance path or explicitly reporting it as a
remaining item. Verify the roots afterward: the intended final state is
platform control directories only, not nonexistent roots. This review does not
claim cleanup completion or a machine-wide post-cleanup inventory result.

## Follow-up: cache maintenance resolved and continuation reviewed

At **2026-11-26 15:02:34 UTC**, the standard Go module-cache cleanup receipt
recorded exit 0 and the exact task cache absent. Receipt SHA-256:
`08465599626c101a7b2c99db54183441c3a8c9c7c0ab2e09e44f074286de0956`.
The preceding 198-directory observation is retained as the pre-maintenance
condition. The official cleanup's module-directory mode changes are correctly
separate from platform permissions and from the narrowed helper itself.

I reviewed `finish_project_cleanup.py` at SHA-256
`3c9a8580ab78bae5d36649fafe78206fba44a0e344d419d6baa32b6c3e6c1258`.
**PASS for the narrowed continuation**: original state/archive gates and helper
identity are checked; the 25 exact direct task-owned children are checked against
the residual inventory and current root listing; all three platform controls and
root directories are preserved; no-follow deletion, mount checks and a fresh
combined process check are retained. The new result remains separate from the
original refusal. This helper changes no permissions and sends no signals.

Bytecode generation is disabled before importing the frozen helper. Execute with
`python3 -B`, without `-O`/`-OO` or `PYTHONOPTIMIZE`, because guards use assertions.
Keep other task writers idle. The reviewer did not execute deletion, rewrite the
original failure, or claim that the narrowed cleanup has already completed.
