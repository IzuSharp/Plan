# Final source freeze and identity/ownership supplement

`audit_final_identity.py` supplements the existing four-cell arithmetic report.
It never runs a benchmark, database or build. The `freeze` action runs before
the two final provider output directories exist; `audit` runs after the actual
four final intervals and the unchanged arithmetic analyzer have completed.
Both actions require a fresh JSON output and retain failures as `status=failed`,
exit 1. A successful `freeze` is `status=frozen`; only a successful `audit` is
`status=passed`. Neither action adds a performance threshold or host admission.

The four final cells are SQLite candidate, SQLite Dapper, PostgreSQL candidate
and PostgreSQL Dapper. The before/candidate 120-second supplement remains a
separate comparison. Older before packages may lack `CommandCompletions` in
their ABI; no zero counter is invented for them. The final candidate must
serialize all eight owner counters, including that field.

## What is frozen and checked

| Binding | Required evidence |
| --- | --- |
| Product source | Exact 40-character candidate commit, its actual Git tree, clean Linux x64 release receipt, matching package source and native source metadata |
| Consumer source | Exact harness commit/tree per consumer; every copied C# source and the project match the committed Korda/Dapper/Shared inventories; standalone Release Native AOT publish command and successful producer receipt |
| Korda package | Actual nupkg SHA-256, complete unsigned member inventory and every member hash, nuspec source commit, package-native hash equal to the published native ELF |
| Dapper packages | Complete actual restore package graph and each nupkg SHA-256, including Dapper.AOT and the corresponding driver |
| Generated source | All retained emitted C# hashes for both consumers; actual Dapper command factories and row factory are revalidated against the existing matched SQL validator |
| SQL contract | Unchanged workload manifest, copied contract sources, static contract and lifecycle policy hashes; static and generated proofs are recomputed from the actual emitted consumer files |
| Runner and plan tools | Exact runner commit/tree and committed runner/manifest bytes; fixed original generator, selector and consumer reader hashes; existing arithmetic analyzer hash and its helper source bytes |
| Final invocation | Derived plan bytes equal the source-bound selector's transformation; executed plan/runner bytes and command argv match; actual consumer ELF and loaded native path/hash match frozen producer inputs |
| Ownership | Candidate `Sources`, `Sessions`, `Operations`, `Cursors`, `Buffers`, `Owners`, `PullChannels`, `CommandCompletions` are all present, integer and zero; Dapper's own application connection count is present, integer and zero |
| Time | Each segment retains actual command, steady and consumer start/end boundaries, plus recorded idle end; no synthetic duration or start time is added |

The complete frozen input inventory is rederived at audit time. Dropping a
required input identity from the freeze is a failure, even if the remaining
hashes still match. Every input is rehashed after the audit. Missing fields,
changed bytes, changed package source/tree, missing generated code or a nonzero
owner fail the supplement. A caller must provide the original freeze SHA-256
when auditing; altered freeze bytes do not inherit their predecessor's identity.

Reviewed auditor SHA-256 is
`99f458030b41cfe9f5740cd536a0f5d3314b0955a8a72de9abce10d3ab3c91e2`.

The existing arithmetic analyzer is rerun read-only against its original index,
and the freshly computed report must equal the supplied report. Its complete
four-cell and serial/idle checks must already pass. It remains responsible for
the 1800-second interval, 35-case coverage, per-second business progress,
errors/rejections, count conservation and fixture/timing boundaries. The
supplement does not change those definitions or create final observations.

Source/build records bind the observed compiler inputs and outputs. This is
evidence consistency checking, not an independent compiler attestation. The SQL
proof is source/generated-code evidence; no runtime server wire trace is
inferred. Dapper's internal native/provider ownership is not relabeled as
Korda counters. Host and cgroup limitations remain those in the actual host and
resource observations.

The historical Dapper producer receipt does not contain `builder_sha256`.
Its `builderSource` entry identifies the builder file in the selected exact
harness commit; it does not independently prove that this builder was the
process originally invoked. Copied source/project bytes, publish argv, restore
packages, generated SQL proof and ELF remain bound to their actual receipt
hashes. The Korda producer additionally records its builder hash.

## Freeze specification

Create a fresh JSON file with exactly these top-level fields:

| Field | Value |
| --- | --- |
| `schemaVersion` | Integer `1` |
| `repository` | Absolute Korda source checkout containing the exact runner and harness Git objects |
| `runnerCommit` | Full commit of the source used to generate both final plans |
| `candidateCommit` | Full product commit from both actual candidate package release receipts |
| `generator` | Absolute unchanged `continuation-4/generate_local_plan.py` |
| `selector` | Absolute `continuation-7/local-load-tools/select_load_cohorts.py` |
| `consumerReader` | Absolute `continuation-7/recovered-short-evidence/tools/analyze_command_single_v2.py` |
| `arithmeticAnalyzer` | Absolute unchanged `continuation-3/analysis/analyze_execution.py` |
| `plans` | Object with exactly `sqlite` and `postgresql`, each the absolute new derived final-plan JSON path |
| `consumers` | Object with exactly `sqlite` and `postgresql`; each has exactly `candidate` and `dapper` descriptors below |

Each candidate descriptor contains exactly `buildReceipt`, `harnessCommit` and
`releaseReceipt`. Each Dapper descriptor contains exactly `buildReceipt` and
`harnessCommit`. The receipt paths are absolute. Harness commits are exact full
Git commits; they are distinct from the package's product commit and must match
the actual copied consumer sources. Reused Dapper binaries retain their true
producer/harness identities. Do not relabel them as a new build.

For example, the `consumers` shape is:

```json
{
  "sqlite": {
    "candidate": {
      "buildReceipt": "/actual/sqlite-candidate/build-receipt.json",
      "harnessCommit": "REPLACE_WITH_ACTUAL_FULL_HARNESS_COMMIT",
      "releaseReceipt": "/actual/sqlite-candidate-package/release.json"
    },
    "dapper": {
      "buildReceipt": "/actual/sqlite-dapper/build-receipt.json",
      "harnessCommit": "REPLACE_WITH_ACTUAL_FULL_HARNESS_COMMIT"
    }
  },
  "postgresql": {
    "candidate": {
      "buildReceipt": "/actual/postgresql-candidate/build-receipt.json",
      "harnessCommit": "REPLACE_WITH_ACTUAL_FULL_HARNESS_COMMIT",
      "releaseReceipt": "/actual/postgresql-candidate-package/release.json"
    },
    "dapper": {
      "buildReceipt": "/actual/postgresql-dapper/build-receipt.json",
      "harnessCommit": "REPLACE_WITH_ACTUAL_FULL_HARNESS_COMMIT"
    }
  }
}
```

The example placeholders are intentionally not valid commit IDs. The tool
rejects aliases such as `HEAD`, missing Git objects and guessed source metadata.
Preserve the actual specification alongside its output. The local verification
specification in `verification/freeze-spec-controls-01.json` is a historical
input/control example, not the final campaign choice.

## Invocation order

After calibration selects the actual C/R, prepare the two final plans with the
unchanged generator and the reviewed selector described in [README.md](README.md).
Make sure both final output directories remain absent. Then freeze:

```bash
python3 "$DB_FINAL_AUDITOR" freeze \
  --spec "$DB_ACTUAL_FREEZE_SPEC" --output "$DB_NEW_FREEZE_JSON"

sha256sum "$DB_NEW_FREEZE_JSON"
```

Retain the returned `status=frozen` JSON and its exact SHA-256. Review the two
product source IDs/trees, all four consumer descriptors, executable and loaded
native hashes, SQL proofs and selected plan destinations. The freeze snapshots
are a prerequisite to the final measurements, not timing credit.

Run only the new derived plans, serially, with the actual host observation and
the existing runner. After creating the unchanged load index and arithmetic
report, invoke:

```bash
python3 "$DB_FINAL_AUDITOR" audit \
  --freeze "$DB_NEW_FREEZE_JSON" --freeze-sha256 "$DB_FROZEN_SHA256" \
  --analysis "$DB_NEW_LOAD_ANALYSIS" --output "$DB_NEW_IDENTITY_AUDIT"
```

Final closeout requires both the original report's four complete cells and
serial/idle result, plus this supplement's `status=passed`, four explicit
`segments` and `inputsUnchanged=true`. Keep any exit-1 receipt and use new paths
after correcting its underlying cause. Do not rewrite freeze metadata to make
a changed binary or later source revision inherit an earlier run.

## Evidence index and durable source archive

The final evidence index should link the current source/build/CI records, host
observation, four derived/source plans, 120-second supplement, final arithmetic
index/report and this freeze/audit pair. For each of the four final segments,
point to its original raw JSON, command receipt, resource JSONL, stdout and
owning runner plan. The audit's `segments` give exact times and image/native
identities; its `bindings` give exact source/tree/package/SQL identities.

Archive the union of frozen inputs and actual analysis/audit inputs. Preserve
original bytes, hash each member, encode deterministically, then read back every
member and rehash every original. Include copied and generated consumer source,
original build/publish/restore receipts, release/nuspec/member metadata, SQL
contracts, pinned scripts, plans, host data and failed attempts. Keep the
before comparison in its own explicitly short section. The new baseline phase
consumers and the retained older harness mismatch are separate source evidence;
the final load auditor does not assign them 1800-second credit.

When executable, package or tool binary bytes are excluded from an evidence
archive, list their exact hashes, original locations and exclusion explicitly.
Such an archive preserves analysis and provenance, but it does not contain a
ready-to-rerun binary set. A later rebuild with a different hash is a separately
identified reproduction. Never claim original binary recovery from source and
hashes alone.

## Finite validation

The initial stable auditor completed
[198 offline positive/negative controls](verification/auditor-controls-01.json).
The positive freeze/revalidation uses actual packages, ELF files, native images,
source trees and generated code. Owner/image positives use untouched historical
short receipts. The existing arithmetic is independently rerun on real phase
evidence; altered arithmetic is rejected. The top-level gate rejects that
non-final report. Owner leaks and missing counters, booleans/floats/strings in
zero counters, wrong image/native/package/source hashes, missing source/tree or
input inventory and malformed JSON all fail.

The [independent source review](verification/final-auditor-review.md) reran all
198 controls and added [60 independent cross-image/cohort/owner controls](verification/auditor-independent-extra-01.json),
all passing on the reviewed hash. Their source and result bytes are preserved.
The separately retained [expected top-level rejection](verification/auditor-expected-non-final-rejection-01.json)
shows that a real non-final arithmetic report cannot receive a successful final
supplement merely because its producer/image/owner checks pass.

No successful final gate is claimed from controls. There is no synthetic
1800-second receipt. Real four-cell final validation remains pending until the
actual campaign finishes. Intermediate successful freeze controls and their
exact auditor source versions are retained; each version has its own hash.
