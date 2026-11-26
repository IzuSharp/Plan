# Independent review of the final cleanup helpers

Reviewed at **2026-11-26 14:47:18 UTC**. Decision: **PASS for the reviewed design
and recorded dry run, subject to the existing execution gates and a quiescent
workspace**. No deletion, process signalling, database execution, build or test
was performed by this review. The existing supplementary dry run was read; the
large filesystem scan was not repeated.

## Reviewed identities

| Input | SHA-256 |
| --- | --- |
| Original `final_cleanup.py` | `79088224364dd5b1321e83c30aa462a2e3bd79efc7e1a692b3638257b4cdabb7` |
| Original cleanup inventory | `ff44db8a718951a07c15d00035c5ea516ddd0b0af3628d532c8c57e9ef87f71b` |
| Supplementary `additional_cleanup.py` | `7d7534391d956839fb721d06fed8409fd984d17a2432bcee381710a039031721` |
| Supplementary inventory | `ac1bcdcbba1ef5a704b330fd0924861a1f5b680c734a7287001cc7ff3c13f277` |
| Supplementary dry-run file | `cc7a4e2e1f048126795c71433bf190e5d554b3a78a347be833b4494422f7b10f` |
| Supplementary canonical plan | `9360a3466d774a20358f65e2632292832c47b0df6ab36dcca54f572ef2f9ec07` |

Original helper path:
`/workspace/scratch/166b48a091b9/go-comparison-01/final_cleanup.py`.
Supplementary helper and its inventory/dry run are under
`/workspace/scratch/2dfe9fb1bc53`.

I read both complete helpers, checked the fixed inventories, and recalculated the
supplementary helper/inventory/canonical-plan hashes against the stored dry run.
That dry run records no mutations, no signals and no blocking process at its
observation time. This is not a claim that the process list stays unchanged.

## Scope and guards

The original helper has exactly three task roots and 32 recorded temporary
targets. It removes registered task worktrees before the owning bare repositories
and roots, checks inode identities and mounted targets, and requires the reviewed
external helper copy and matching acceptance. It supports recorded interruption
recovery and emits its final receipt to stdout before deleting its temporary
control files. Capture that stdout outside the deleted roots.

The supplement handles two additional source areas, three registered worktrees,
66 exactly inventoried MSBuild temporary directories, a 57-file NuGet HTTP cache,
1,243 empty NuGet scratch lock files, nine Go telemetry files and four identified
wrappers that may be removed only when empty. Its 70 top-level recursive targets
are the two source areas, 66 MSBuild directories and two cache directories. The
original three task roots and 32 temporary paths are process-watch scope only;
the supplementary helper does not delete them. The current recovery workspace
remains outside its deletion targets.

The supplementary helper rejects noncanonical paths, symlinked targets or
ancestors, changed device/inode/owner/mode/file metadata, unexpected cache files,
nested or target mounts, unexpected worktree registrations, changed repository
heads/diffs/refs, and changed accepted tree snapshots. It uses no-follow reads and
requires symlink-resistant `shutil.rmtree`. Empty wrappers use `rmdir`, so
unreviewed contents prevent their deletion. All mutations use fixed argument
arrays or Python filesystem operations, with no shell-command interpolation.

Both execution gates bind the actual helper and reviewed plan to root acceptance,
require immutable repository commit URLs and matching archive/readback hashes,
and rehash critical local source/archive files. Coverage labels are assertions
made by the root agent after inspecting actual evidence; the helpers do not fetch
GitHub or independently prove that a remote URL contains those bytes. Therefore
actual remote archive readback and retained source-history review must precede
the acceptance files. A dry run or this design review does not replace them.

## Process protection and execution sequence

The supplementary helper never sends a signal. It inspects process executable,
cwd, absolute argument paths, open files and mapped files across both deletion
scopes, recognizes build/database processes, and blocks on unreadable live
processes. It repeats process checks before mutation and individual targets.
The original helper can terminate a proven task-owned process using pidfd plus
start-time/executable identity; shared, protected or unknown processes are not
eligible for that action.

The original helper's own process classifier is narrower: it does not cover every
temporary path or mapped file and can skip an unreadable process. **Immediately
before executing the original helper, run the supplementary
`--process-check-only` mode and require an empty blockers array.** This existing
read-only mode covers the original roots and all 32 exact temporary paths as well
as supplemental targets, without rescanning the large source trees. Keep all
other task agents idle until cleanup finishes. Inspect actual process actions in
the final receipt instead of assuming no signal was sent.

Run the supplementary cleanup before the original cleanup if its acceptance
rehashes archives or source files under the original roots. Otherwise the
original cleanup would remove required gate inputs and the supplement would
correctly refuse. Generate and accept a fresh original-helper dry run after all
record publication changes, since those changes may alter reviewed worktree
state. Preserve the original helper bytes.

## Residual limits and conclusion

These are safeguards for an observed quiescent task workspace, not a filesystem
transaction or protection against a hostile concurrent writer. There is no
global filesystem lock. Checks reduce time-of-check/time-of-use races but cannot
eliminate them; expected worktree removals also change source-root snapshots
before final root deletion. Do not start builds, writers or mounts concurrently.
On a refusal or partial receipt, inspect the recorded action and remaining paths;
do not bypass an identity/hash/process gate or replay with guessed values.

System software, platform runtime/skills/session support, certificate stores and
machine identity metadata are outside the deletion lists. This review does not
claim entire-machine absence of project content; that is a separate post-cleanup
inventory result. No helper-source change is required by this review for the
current fixed scope. **Deletion has not been performed by the reviewer.**
