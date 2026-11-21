# DB-CPP-01 Linux evidence inputs

`python3 tools/verify_db_cpp.py` validates current progress and rejects contradictory
or unbound evidence. `--require-complete` additionally requires an accepted,
delivered snapshot. The verifier is an offline consistency check. Actual GitHub
observations and execution records must be obtained and independently reviewed;
JSON and SHA-256 alone do not authenticate a remote service or prove execution.

The fixed starting commits/trees and all seven ordered phases are enforced by the
verifier. Historical DB-Scope-01 inputs and its verifier remain unchanged. The
already verified `reference-receipt.json` is retained byte for byte, identified by
its exact hash. Its Rust source is the only baseline exception. It cannot support
a C++ product claim. All newly written receipts use schema 2.

## Sources and references

`acceptance.json` remains schema 1. `candidate_sources` records the exact tested
head commit and tree of each repository. While work is in progress, the Plan
candidate may be absent. Accepted delivery requires all three identities.
Ordinary behavior, build, package and review evidence must name these exact
identities. A different commit with the same tree is not silently substituted.
Merged-main CI uses the separate PR merge identity and verified tree equality.

A receipt reference remains `{ "path": "ledger/evidence/batches/DB-CPP-01/...",
"sha256": "<64 lowercase hex>" }`. Paths are canonical, relative and confined to
this batch; acceptance cannot cite itself. Receipts cannot include themselves or
duplicate artifacts. Every referenced file is hashed from its actual bytes.

```json
{
  "schema_version": 2,
  "task": "DB-CPP-01",
  "platform": "linux-x64",
  "claims": ["historical_data_migrations"],
  "outcome": "passed",
  "sources": {
    "NativeWeave": {"commit": "<tested head>", "tree": "<tested tree>"}
  },
  "artifacts": [
    {"path": "ledger/evidence/batches/DB-CPP-01/.../candidate/result.json", "sha256": "<file hash>", "kind": "migration-run"},
    {"path": "ledger/evidence/batches/DB-CPP-01/.../baseline/result.json", "sha256": "<file hash>", "kind": "migration-run"},
    {"path": "ledger/evidence/batches/DB-CPP-01/.../comparison.json", "sha256": "<file hash>", "kind": "migration-comparison"}
  ]
}
```

Outcomes are `passed`, `failed` or `blocked`. Failed or blocked evidence can be
preserved without declaring its commands or CI successful. It cannot support a
passed check. Pending checks need no evidence. The original progress checkpoint
with only the fixed Rust-reference claim still validates.

## Actual result types

Results may be raw JSON or the existing safe export envelope
`{ "sanitized": true, "source_artifact_sha256": "<original raw hash>", "data": {...} }`.
The exported file hash is verified, then `data` is parsed. Original hashes bind
cross-result references without publishing private connection strings or argv.
Only defined top-level terminal fields and the known result structure determine
success; nested expected-failure probes are not mistaken for failed suites.

| Artifact kind | Required actual evidence |
| --- | --- |
| `native-build` | Native producer manifest: exact source commit/tree, clean source, C++20, Linux Release preset, Clang tools/target, both native assets and successful command exits. |
| `package-manifest` | Exact source/native source, clean Linux candidate and the hash of a `native-build` artifact in the same receipt. |
| `component-result` | Existing component result's top-level terminal result, exact source, clean/stable source and successful commands. |
| `compatibility-result` | Actual A15 pass, clean/stable exact source, `prepare_only=false`, retained 20 matrix/30 policy cases and at least the original 85 commands. |
| `regression-result` | `eng/database_regressions.py` result: exact source identity, successful commands, both providers/modes, required native inventory, retained component verifiers and five complete JIT/AOT suites. |
| `verification-result` | `eng/build.py` result: exact source and completed formatter, native, managed, API, provider and external package checks with native/candidate manifest hashes. |
| `migration-run` | Actual baseline or candidate driver result: exact controller source, all four successful cells, executed commands, all twelve package identities, ABI cases/resource counts and all normal/changed-DTO build identities. Baseline packages bind to fixed Rust; its controller still binds to the current candidate. |
| `migration-comparison` | Both actual run artifacts in the same receipt, linked by original hash; identical consumer, driver, SDK/config, database versions, ABI inputs/outcomes and exact old database snapshots; comparison rows/packages equal executed candidate rows/packages. DTO builds must preserve native hashes. |
| `review` | Top-level pass, exact `sources` equal receipt sources, nonempty `reviewer` and `authorship_disclosure`, and `blocking_findings: []`. Product and Design source coverage is required; observed Plan review can additionally be included. |
| `command-result` | Exact-source auxiliary command result with top-level pass and actual successful exits. This generic kind cannot independently satisfy sanitizer, format or no-Rust gates. |
| `log` | Hashed supporting bytes. A log alone cannot establish any passed product claim. |
| `github-run`, `github-jobs`, `github-pr` | Actual API observations checked through the CI/PR rules below. |

The sanitizer and fresh no-Rust build/package/run claims require the complete
actual product PR CI, including their mandatory successful steps. Format/tidy may
also use the full source-bound `verification-result`. A generic successful shell
command cannot replace these gates. Product CI may support retained regression
and resource claims because its fixed build workflow executes those gates.
Business parity/history/package cells and DTO/hash claims use actual migration
results, not CI summary strings.

## CI and PR input

A schema-2 CI receipt adds `required_checks_complete: true` and `ci` rows:

```json
{
  "repository": "NativeWeave-Design",
  "scope": "pr_head",
  "url": "https://github.com/IzuSharp/NativeWeave-Design/actions/runs/<id>",
  "workflow_path": ".github/workflows/public-api-design.yml",
  "run": {"path": "ledger/evidence/batches/DB-CPP-01/ci/.../run.json", "sha256": "<hash>"},
  "jobs": {"path": "ledger/evidence/batches/DB-CPP-01/ci/.../jobs.json", "sha256": "<hash>"}
}
```

Both referenced raw observations must also be present in `artifacts` with their
matching `github-run`/`github-jobs` kinds. Run URL, repository, workflow, run ID,
attempt, exact head commit/tree, event, branch and completed/success outcome are
checked. Jobs must be a complete response: `total_count == len(jobs)`, no duplicate
IDs/names, and the fixed required job set. Each job must belong to that run,
attempt, branch and head. Required steps must actually complete successfully.

| Repository | Required workflows/jobs |
| --- | --- |
| NativeWeave | `.github/workflows/ci.yml`: build/package/AOT, dependency review, secret scan, both CodeQL languages and Verify. Every fixed build gate, including leak-enabled ASan/UBSan, compatibility/fuzz, CPU/runtime transfer, release recovery, pristine SDK consumption, fresh no-Rust image and artifact retention, must succeed. |
| NativeWeave-Design | `public-api-design.yml`: `api-interface (ubuntu-24.04)`; `english-translation.yml`: `translation-integrity`; both actual verification steps must succeed. |
| Plan | `native-slices-final-check.yml`: `paired-integrity`; current migration and both frozen historical verification steps must succeed. |

PR scope requires `event=pull_request` and `head_branch=task/DB-CPP-01-linux`.
Merged scope requires `event=push` and `head_branch=main`. Only the product's
dependency-review job is expected to be skipped on main, matching its existing
explicit workflow condition. Optional `required_jobs`/`normally_skipped_jobs`
arrays must equal these fixed sets; they cannot weaken them. GitHub sometimes
returns an empty `pull_requests` collection after merge; the separate PR
observation binds the exact head and base. A nonempty collection must contain the
recorded PR. Merged-main receipts contain the actual run/jobs observations;
merged build artifacts do not replace tested-head behavior evidence.

Each `acceptance.prs[repository]` records `url`, `state`, `tested_commit`,
`tested_tree`, `merged_commit`, `merged_tree`, `observation`, `head_checks` and
`merged_main_checks`. `observation` references the raw PR JSON, whose head/source,
main base, merged status and actual merge commit must match. The two check arrays
reference the corresponding CI receipts. Their union must appear in the relevant
global CI acceptance check. Tested/merged trees must be equal. Older incomplete
progress records may lack these receipts, but cannot establish complete delivery.

## Plan delivery without a circular CI claim

1. Finish and review the deliverable in Plan PR26. Keep acceptance in progress
   until its actual merge and main CI have been observed.
2. Record that delivered Plan tested/merged identity, along with product PR21 and
   Design PR15 and their exact-head/merged-main CI. The Plan `candidate_sources`
   entry names the delivered PR26 head, not a future evidence-container commit.
3. An evidence-only followup adds the observed results and sets accepted state.
   It includes `delivery_snapshot` with `plan_pr`, `plan_tested: {commit,tree}`,
   `plan_merged: {commit,tree}`, `record_policy: "evidence-only-followup"` and
   `self_ci: "checked-separately"`. These identities must equal the Plan PR record.
4. Review, PR CI, normal merge and main CI for that evidence-only followup are
   checked separately through GitHub and linked in the handoff/report discussion.
   The file cannot predict the outcome of its own future containing commit.

The verifier runs an entirely in-memory accepted-state positive fixture and
negative controls for altered sources/results/hashes, incomplete or fabricated CI
summaries, missing jobs/steps, missing database/package cells and invalid Plan
closeout. No synthetic result is written into the acceptance ledger.
