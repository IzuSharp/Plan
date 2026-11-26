# DB-Go-01 final cleanup helper

## Status

`final_cleanup.py` is implemented and **has not been executed in deletion mode**.
Python AST parsing passed. Its default read-only invocation passed and found 62
registered worktrees, the 32 inventoried temporary targets, and only protected
platform processes. `final-cleanup-dry-run.json` is a preparation snapshot; it
must be regenerated after the Go runs, final source commits, and publication.

The user already authorized deleting all local task directories, worktrees and
caches. The acceptance JSON is an execution evidence gate for the root agent,
not a request for another user confirmation.

## Fixed scope

The helper removes only these three exact roots and the exact temporary paths
in `cleanup-inventory.json`:

- `/workspace/scratch/fd78534029f7`
- `/workspace/scratch/4a65d70f0fe1`
- `/workspace/scratch/166b48a091b9`

It validates every registered worktree against this scope before changing
anything. Temporary paths are taken from the reviewed inventory, not from a
deletion glob. New `/tmp` task paths must be explicitly added and reviewed
before the final dry run. The final removal includes the current workspace
directory itself. The helper changes its own cwd to `/tmp` before mutation.

The shared `/opt/codex`, `/usr`, `/usr/local`, unrelated scratch directories,
unrelated temporary files, and shared user configuration/caches are outside the
scope. Platform processes are preserved even when their cwd is in a removed
task directory. Later shell commands must specify a surviving cwd such as
`/tmp`; the framework's old cwd may have been unlinked.

## Required acceptance

`final-cleanup-acceptance.template.json` deliberately has `accepted: false` and
incomplete Go archive entries. It cannot authorize deletion unchanged. After
both requested Go measurements and their idle/recovery observations are
finished, the root agent must supply:

1. Exactly one SQLite and one PostgreSQL Go cell, each with
   `nominalSeconds: 1800`, `completed: true`, and
   `fullDurationObserved: true`. Failed assertions/errors must remain in the
   evidence and report; these flags do not imply zero errors.
2. An immutable fixed-commit report URL under the user's Korda/Plan/Design
   repositories, and confirmation that the results have been reported to the
   user before cleanup.
3. Local archive paths and SHA-256 hashes, immutable fixed-commit URLs, actual
   remote byte readback SHA-256 values, and `readbackVerified: true`. Across the
   archives, `covers` must include `go-source`, `go-results`,
   `legacy-dispositions`, and `cleanup-inventory`.
4. Critical original source/result files and their current SHA-256 values in
   `sourceChecks`. Include the final Go source, pinned dependency files,
   frozen workload/SQL inputs, validation/report results, this helper, the
   inventory, and relevant archive manifests. The helper rehashes these files
   before any destructive action.
5. The exact helper SHA, exact inventory file SHA, embedded inventory contents,
   and `planSha256` from a fresh final dry run. The plan binds target directory
   device/inode identities, worktree HEAD values, and hashes of tracked diffs
   plus untracked file bytes. Clean worktrees do not substitute for archive
   verification.
6. `legacyRetentionResolved: true` and `allTaskDataReviewed: true` only after the
   root has reviewed the actual archive and explicit omission records.

The execution process performs no network lookup. The root must obtain the
remote readback evidence before setting the acceptance fields. Acceptance is
bound to the reviewed bytes and cannot be supplied as a shell command.

## Invocation and output

Preparation-time read-only invocation:

```bash
python3 /workspace/scratch/166b48a091b9/go-comparison-01/final_cleanup.py
```

After the evidence gate is satisfied, copy the **exact reviewed helper bytes**
to `/tmp/DB-Go-01-final-cleanup.py` and write the finalized acceptance JSON to
`/tmp/DB-Go-01-final-cleanup-acceptance.json`. Run another default dry run from
the external copy before accepting its plan. Then, and only then, the root
agent can invoke the external helper with `--execute`, using `/tmp` as cwd.
This document and this agent did not invoke that mode.

The helper writes its final receipt only to stdout. Capture the tool's complete
stdout and publish it immediately to durable storage; do not redirect it into
one of the three roots being deleted. The receipt includes actual removal
actions, already absent paths, process actions, source checks, and observed
workspace filesystem availability before/after. It never equates the sum of
cache sizes with reclaimed filesystem space and does not count earlier cache
deletions again.

## Process ownership and cleanup order

Only a process whose executable is inside a task root, or whose interpreter
is directly running a script inside a task root, is eligible for termination.
Cwd alone is never permission to signal a process. Unknown processes holding a
task cwd or open file block cleanup. The helper preserves PID 1, 2, 5, itself,
its ancestors, and platform executables under `/opt/codex`.

Before signaling an eligible process, the helper rechecks PID start time and
executable identity, opens a Linux pidfd, and rechecks identity again. It sends
SIGTERM to that pidfd, waits up to 10 seconds, and only then sends SIGKILL to
the same pidfd if needed. It never signals a process group.

After archival and process checks, it removes each registered worktree using
its owning bare repository. Locked worktrees are refused; the helper does not
override locks. It then verifies there are no remaining registrations, removes
the exact temporary targets, removes the two old roots, and removes the current
workspace last. It refuses top-level symlinks, changed root inodes, symlinked
ancestors, or nested mounts, and requires Python's symlink-resistant `rmtree`.

## Interrupted cleanup

Before mutation, the helper writes
`/tmp/DB-Go-01-final-cleanup-state.json` using an atomic update. It records the
verified acceptance/helper hashes, original plan and source checks, and each
deletion path before starting that action. A retry with the same reviewed
helper and acceptance can recognize paths already removed without claiming
another removal or freeing the same bytes again. Remaining worktrees and
targets must still match their recorded identities; a newly appearing or
modified worktree blocks the retry.

On failure the state, acceptance and external helper remain for review and
resumption. On complete success the helper checks that all task targets are
absent, removes its state and acceptance files, deletes its own external file
last, and emits the receipt. A successful run therefore leaves no helper or
control file behind. It cannot be rerun after successful self-removal; there
is then no remaining cleanup target.

## Legacy text retention and binary omissions

`legacy-retention-audit.json` indexed actual tracked Plan bytes, gzip-decoded
files and tar regular members. It did not infer archival coverage from a hash
merely mentioned in an exclusion list. The supplemental archive
`legacy-extra-evidence.tar.gz` retains 1,538 unmatched unique text objects with
9,643 original-path mappings: 50,076,719 original bytes, compressed to
10,294,557 bytes. The 1,538 archived objects were read back and verified.

An unmatched file was not proved absent from every public source: the set also
contains published Korda source snapshots and reproducible upstream source.
The supplement preserves these bytes without inventing another performance
result. It includes the small unmatched historical log set and control JSON
so rejected attempts are not discarded during cleanup.

The archive excludes compiled binaries, package/compiler caches, database data
files and tool installations. Existing build/freeze/dedup receipts retain
identities where recorded. `binaryRecoveryClaim` is explicitly false. The root
must publish this supplemental archive and verify remote readback before final
deletion; local compression/readback alone does not satisfy the durable gate.
