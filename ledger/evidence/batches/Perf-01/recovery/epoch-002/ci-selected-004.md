# Selected runtime 004: actual GitHub CI

**The selected commit's CI completed successfully: seven workflow jobs and all
eight commit check runs returned success. No CI failure or pending check was
observed in this snapshot. This supplies zero performance or long-test credit.**

- Repository: `IzuSharp/NativeWeave`.
- Selected head: [`2f40348c3db80a4fbee7a99e721b374a597b16df`](https://github.com/IzuSharp/NativeWeave/commit/2f40348c3db80a4fbee7a99e721b374a597b16df).
- Actual [CI run 131, attempt 1](https://github.com/IzuSharp/NativeWeave/actions/runs/44866071462), run ID `44866071462`, event `pull_request`.
- Started: `2026-11-21T04:25:52Z`; last actual job completed: `2026-11-21T04:41:40Z`.
  The run's `updated_at` is also `2026-11-21T04:41:40Z`; a separate run-level
  `completed_at` is not exposed in the fetched run payload.
- Retrieved through the GitHub connector at `2026-11-21 04:55:48 UTC`.

## Actual jobs

Every job below reports the selected head SHA above. Times are UTC.

| Job | Actual result | Started | Completed |
|---|---|---|---|
| [A20 ownership and sanitizers](https://github.com/IzuSharp/NativeWeave/actions/runs/44866071462/job/136729891809) | completed / success | 2026-11-21T04:25:55Z | 2026-11-21T04:27:45Z |
| [security / Dependency review](https://github.com/IzuSharp/NativeWeave/actions/runs/44866071462/job/136729891964) | completed / success | 2026-11-21T04:25:55Z | 2026-11-21T04:26:04Z |
| [build / Build, package and Native AOT](https://github.com/IzuSharp/NativeWeave/actions/runs/44866071462/job/136729891986) | completed / success | 2026-11-21T04:25:55Z | 2026-11-21T04:41:32Z |
| [security / CodeQL (csharp)](https://github.com/IzuSharp/NativeWeave/actions/runs/44866071462/job/136729891993) | completed / success | 2026-11-21T04:25:55Z | 2026-11-21T04:29:22Z |
| [security / Secret scan](https://github.com/IzuSharp/NativeWeave/actions/runs/44866071462/job/136729892116) | completed / success | 2026-11-21T04:25:55Z | 2026-11-21T04:26:07Z |
| [security / CodeQL (python)](https://github.com/IzuSharp/NativeWeave/actions/runs/44866071462/job/136729892313) | completed / success | 2026-11-21T04:25:55Z | 2026-11-21T04:26:54Z |
| [Verify](https://github.com/IzuSharp/NativeWeave/actions/runs/44866071462/job/136733840277) | completed / success | 2026-11-21T04:41:35Z | 2026-11-21T04:41:40Z |

The commit check-run endpoint returned these seven matching checks and this
additional successful CodeQL check from its separate check suite:

| Additional check | Actual result | Started | Completed |
|---|---|---|---|
| [CodeQL](https://github.com/IzuSharp/NativeWeave/runs/136730107964) | completed / success | 2026-11-21T04:26:44Z | 2026-11-21T04:26:50Z |

The jobs and check-run counts match the complete returned populations (7 and
8 respectively, within the requested 100-item pages). The companion JSON
retains each job/check ID, head, URL, timestamps and actual step outcomes.
No test/assertion count is inferred from a job name.

## Source and required configuration

The run references reusable workflows at PR merge commit
[`461afa34cc44f09651c89b721a1aa050a7c64b7d`](https://github.com/IzuSharp/NativeWeave/commit/461afa34cc44f09651c89b721a1aa050a7c64b7d), `refs/pull/19/merge`.
The API reports its tree as `7f803d4f9e57fef1d8cfdef69c505d67f84614c9`, exactly the selected
head's tree. The fetched `.github/workflows/ci.yml` bytes are identical at
both commits. This distinguishes the actual PR merge reference from the run's
selected-head association without substituting a different product tree.

The fetched [CI workflow](https://raw.githubusercontent.com/IzuSharp/NativeWeave/461afa34cc44f09651c89b721a1aa050a7c64b7d/.github/workflows/ci.yml) defines
`Verify` with `if: always()`, dependencies `build, interop, security`, and
explicitly requires each dependency result to equal `success`. Its actual
`Require every gate` step and job both succeeded.

The actual [main branch summary](https://api.github.com/repos/IzuSharp/NativeWeave/branches/main) reports
`required_status_checks.enforcement_level: off` with empty contexts/checks.
The sole returned active [protectmain ruleset](https://github.com/IzuSharp/NativeWeave/rules/27094343)
applies to the default branch and contains deletion and non-fast-forward
protections, with no required-status-check rule. These are observed settings,
not a change or a proposal to relax repository requirements.

The [PR #19](https://github.com/IzuSharp/NativeWeave/pull/19) snapshot is open, draft, unmerged,
`mergeable: true` and `mergeable_state: clean`. This projection does not
claim that the PR was merged or that Perf-01 is ready for final delivery.

## Scope and limits

This was a remote metadata read. No artifact or job log was downloaded; no
local build, target-module import or workload was run. CI success does not
establish local measured binary/native identity, throughput, p99, capacity,
resource recovery, any 30-minute segment or performance improvement. Those
still require their own actual producer, correctness and measurement receipts.
Post-merge CI and the existing preview remain separate delivery checks.

The JSON lists the exact API/source URLs used. This selected-commit snapshot
does not continuously track later Plan documentation-only CI.

