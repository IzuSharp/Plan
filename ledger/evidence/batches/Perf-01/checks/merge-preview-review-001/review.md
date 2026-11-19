# Perf-01 merge and preview review

This read-only GitHub audit finished at **2026-11-19 21:08:45 UTC**. It records the commits actually inspected during that audit, not the current PR heads. No settings, PRs, workflows or repository refs were changed by the audit.

## Inspected PR state

| PR | Inspected head | Observed review state | Observed checks |
| --- | --- | --- | --- |
| [NativeWeave #19](https://github.com/IzuSharp/NativeWeave/pull/19) | `d859b79eedb87dfc372be6c07e516d173c96124b` | Open, draft; mergeable/clean; no submitted reviews, inline review threads or requested reviewers | [CI 44611817761](https://github.com/IzuSharp/NativeWeave/actions/runs/44611817761): all seven checks succeeded |
| [Plan #23](https://github.com/IzuSharp/Plan/pull/23) | `4deae296dc1d65ada0e79b32c775001f04eaf483` | Open, draft; mergeable/clean; no submitted reviews, inline review threads or requested reviewers | [CI 44607644880](https://github.com/IzuSharp/Plan/actions/runs/44607644880): paired-integrity succeeded |

**Plan `4deae296` is a historical inspected head.** Plan advanced afterward. The task owner subsequently reported public head `f2b2ca881954b1c4e6663571870ce2cf73f1567d` and CI `44618742398` in progress at that later observation. Neither that commit nor its CI was rechecked by this audit.

The legacy commit-status endpoints returned `pending` with zero status entries. This is not evidence of an unfinished or failed check run.

## Final merge requirements

[NativeWeave AGENTS](https://github.com/IzuSharp/NativeWeave/blob/d859b79eedb87dfc372be6c07e516d173c96124b/AGENTS.md) and [CONTRIBUTING](https://github.com/IzuSharp/NativeWeave/blob/d859b79eedb87dfc372be6c07e516d173c96124b/CONTRIBUTING.md) require the canonical `python3 eng/build.py verify` gate, truthful JIT/AOT/package-consumption evidence, and scoped API, ownership, cost and documentation review. Independent technical review is a separate obligation; author self-review must not be described as independent approval.

The existing [Linux build workflow](https://github.com/IzuSharp/NativeWeave/blob/d859b79eedb87dfc372be6c07e516d173c96124b/.github/workflows/build.yml) also checks a fresh SDK container without Rust, Task-04 package closure/runtime transfer, Task-07 domain packages/pristine consumers, and source/dependency drift. The [CI aggregator](https://github.com/IzuSharp/NativeWeave/blob/d859b79eedb87dfc372be6c07e516d173c96124b/.github/workflows/ci.yml) requires both build and security success. Security comprises dependency review on PRs, full-history secret scanning, and C# and Python CodeQL.

For Plan, [AGENTS](https://github.com/IzuSharp/Plan/blob/4deae296dc1d65ada0e79b32c775001f04eaf483/AGENTS.md) and the [paired-integrity workflow](https://github.com/IzuSharp/Plan/blob/4deae296dc1d65ada0e79b32c775001f04eaf483/.github/workflows/native-slices-final-check.yml) preserve exact Design/source bindings and existing acceptance history. Ledger changes trigger this workflow on PRs targeting main and on main updates. It checks API history/current bindings, contracts/tasks, attestation/completion, research/lifecycle, graphs/schemas, mutation cases, host selection and Rust-version consistency. No separate CONTRIBUTING file was present in the inspected Plan root or .github directory. Historical research-branch integration workflows are not additional Perf-01 gates.

Before merging, complete the authorized Perf-01 evidence and final independent review, mark the PRs ready, and verify checks on the **final pushed heads**. Earlier green checks do not cover subsequent changes. This audit adds no platform, package-release or performance gate beyond the user's Linux x64 scope and the existing applicable checks.

## Visible protection rules and limits

The active public main rulesets, [NativeWeave 27094343](https://github.com/IzuSharp/NativeWeave/rules/27094343) and [Plan 27113698](https://github.com/IzuSharp/Plan/rules/27113698), contained only deletion and non-fast-forward restrictions, with no bypass actors. They did not list a required approval count or required-check set.

Both classic branch-protection requests returned **403: Resource not accessible by integration**. Therefore this review does not claim complete visibility of all protection settings. Respect any actual final merge restriction; do not change protection or impersonate another approver to make a merge pass.

## Normal post-merge preview

The existing [release guide](https://github.com/IzuSharp/NativeWeave/blob/d859b79eedb87dfc372be6c07e516d173c96124b/docs/releasing.md) and [Release workflow](https://github.com/IzuSharp/NativeWeave/blob/d859b79eedb87dfc372be6c07e516d173c96124b/.github/workflows/release.yml) define the authorized automatic preview:

1. A main update must correspond to an already merged PR with that exact merge commit. A direct push without this evidence skips publication.
2. Candidate and security jobs use the same accepted source commit.
3. Publication uses the retained verified package, subject to the existing publishing variable and nuget environment configuration.
4. Registry verification checks signature/payload consistency and executes JIT and Native AOT consumers using downloaded registry bytes. Completion is evidenced by `publication.json` reaching `published-and-consumed`.

The previously merged main commit `ea5fa528035d025bd7a28698ee7c71194432236c` had a successful [Release 44357807003](https://github.com/IzuSharp/NativeWeave/actions/runs/44357807003), including successful publish-and-consume job `135004169244`. This establishes that the existing flow actually ran; it does not guarantee that future configuration or runs will succeed.

After the final merge, verify the corresponding main CI and normally triggered Release for that exact merge commit. The public preview remains **NativeWeave.HelloWorld**. Tested domain candidates do not become publicly released domain packages through this audit; their public issuance remains a separate task.

CI candidate/verification artifacts retain **14 days**; publication artifacts and Plan paired-integrity artifacts retain **30 days**. Their current upload allowlists do not automatically retain all Perf-01 measurements. Retain authorized numerical evidence and verification records separately and verify readback. Keep measured candidate identities distinct from any subsequently rebuilt preview package identity.
