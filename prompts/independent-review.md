# Independent review scope

Review the actual changed plans and contracts against their declared scope.
Check task identity, dependency correctness, feasible acceptance criteria and
consistency of source/platform/result claims. Separate accepted historical
meaning from new execution claims. Identify concrete defects and remaining
questions; record useful conclusions and reasons in the relevant document or PR.

For CI changes, inspect [the registry](../eng/ci/registry.py), shared diff route,
current checkers and temporary-Git integration tests. Confirm plain prose selects
no checks, rename/delete impact is covered, checks deduplicate and there are no
raw-material uploads or old fixed-commit replay workflows.

Keep review scratch files and command output local. Do not add another evidence
snapshot or receipt chain to the repository. Do not impersonate another GitHub
approval account.
