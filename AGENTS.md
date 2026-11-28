# Plan contributor guidance

## Repository purpose

Keep plans, task definitions, dependencies, progress and concise final conclusions.
Design rationale and interface contracts belong in [Korda-Design](https://github.com/IzuSharp/Korda-Design).
Read [CURRENT-PHASE.md](CURRENT-PHASE.md) before interpreting historical tasks.
A recorded acceptance state is not fresh product validation or permission to resume work.

Keep raw logs, per-second measurements, resource samples, binaries, screenshots,
command output, recovery state and temporary receipts on the execution machine.
Regenerate them when needed. Do not commit them, move them into another repository
or service, or upload documents or intermediate material as Actions artifacts.
Submit maintained documents through ordinary Git commits and PRs; do not rewrite history.

## Classify every document change

**Every time a document is added or moved, consider its CI type and confirm that
its destination path is correctly registered in [eng/ci/registry.py](eng/ci/registry.py).**
Reuse an existing directory rule when it covers the path with the right type.
For a new structured document, first look for a suitable existing type. Add a
new type, path rule, check and tests only when there is a real programmable
correctness rule. Ordinary prose is a valid type and may have zero checks.
A file may have several types; all matching checks are combined and deduplicated.
Register affected document types when a schema, task or other dependency changes.

## CI and local verification

[The CI guide](eng/ci/README.md) documents registration and commands. Python owns
classification, dependency impact and execution; YAML only checks out and starts it.
PRs compare their merge-base with the target branch to the PR head. Main pushes
compare the event's actual before and after commits, including multi-commit pushes.
Renames route both paths; deletion validates surviving references. Ordinary prose
selects no checks. Current CI never replays frozen acceptance commits.

After changing CI, run `python3 eng/ci/run.py --all --install-dependencies`. The tests use temporary Git repositories
and the same command as Actions. Inspect a committed change with
`python3 eng/ci/run.py --event pull_request --base origin/main --head HEAD --list`;
remove `--list` to execute it. Keep checks small and routine validation below one minute.

Use a task-named branch and isolated worktree. Review the final diff, references
and selected checks before opening a PR. Preserve task identities, recorded
states and meaningful conclusions; never claim document checks prove database,
AOT, release or performance correctness. Stop at the review boundary requested
by the current user instruction.
