# Document CI

## Registration

[registry.py](registry.py) is the single path → type → check registration entry.
All matching `Registration` rows contribute types; a file may have several.
`DocumentType.checks` lists checks and `affects` lists dependent document types.
`CHECKS` gives each check's command and optional pinned Python requirements.

| Registered content | Type | Selected checks |
| --- | --- | --- |
| Root guidance, `docs/`, authored `ledger/`, templates and prompts | prose | none |
| Three task graphs | task-nodes + task-dependencies | graph-schema, task-links |
| Task packets | prose + task-packets | task-links (surviving graph references) |
| `fragments/*.json` | task-fragments | task-links |
| Graph schema | graph-schema | graph-schema and task-links through current graph users |
| CI Python, tests, requirements and workflow | ci-tooling | ci-self-test and current content checks |
| License and Git metadata | repository-metadata | none |

Directory wildcard rules cover new ordinary documents without per-file entries.
Adding or moving any document requires checking its correct type and destination
registration. Unknown added/current paths fail selection. Removed obsolete paths
without a surviving registration need no invented permanent type. A registered
deleted task or graph still triggers current surviving-reference checks.

For a new structure, reuse an existing type when its rules fit. Add a type only
for a real programmable rule, then add its path registration, command and tests.
Declare affected types when the input changes their validity. Neither the
scheduler nor YAML needs document-specific changes. Plain prose remains valid
with no check. The graph checker uses the standard jsonschema implementation,
not a partial home-grown JSON Schema interpreter.

## One route for PR and main

Actions checks out the PR head or push after commit once, using a shallow blobless
fetch. `run.py` reads the event and verifies the checkout identity. PR selection
uses `merge-base(target, head)..head`; main push selection uses the exact
`before..after`, including several pushed commits. Only missing history needed
for the merge-base is fetched, with a bounded deepening limit. A first push uses
the empty tree. There is no full-history checkout or historical gate execution.

`git diff --no-renames --name-only -z` represents a rename as old deletion plus
new addition. Both types route. Sets deduplicate checks and retain concise
selection reasons. Current graph users are checked after schema changes; task
references and packet existence are checked after deletion. CI changes select
self-tests. Requirements are installed only for selected checks; a prose-only
change selects zero checks and installs nothing.

## Local commands

Run from the repository root with Python 3.11+ and Git:

```sh
python3 eng/ci/run.py --all --install-dependencies
python3 eng/ci/run.py --event pull_request --base origin/main --head HEAD --list
python3 eng/ci/run.py --event pull_request --base origin/main --head HEAD
python3 eng/ci/run.py --event push --base BEFORE_COMMIT --head HEAD
```

Use committed bounds. Executing checks requires the compared head to be checked
out; `--list --json` can inspect a selection without execution. The command checks
the current working files, so stage and commit the intended changes before final
verification. Tests construct real temporary commits, branches, merges, renames,
deletions and a shallow origin, and exercise the normal command/event entrypoint.
They do not write result files to this repository.

The two content checks validate current graph schema, unique task IDs, references,
packet existence, dependency cycles and fragment task ownership. They do not
perform product tests or re-accept historical results. Routine validation should
finish in under one minute. Actions reports selection and elapsed time in logs
and its step summary; no document or intermediate artifact is uploaded.
