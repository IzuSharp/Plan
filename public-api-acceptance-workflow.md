# Public API refinement: exact review, acceptance and merge sequence

This procedure completes the existing 34 Research, 32 Documentation and 21
contract subjects. It does not add a graph, execute any of the 48 Delivery tasks,
or create product acceptance. All work remains on `design/public-api-20261114`
in both repositories, with one final PR per repository.

## Existing accepted history

`ledger/public-api-2026-11-14/prior-acceptance.json` identifies immutable snapshots
of the preceding graphs, registry, acceptance indices and baseline. Original
research/translation evidence and reviewer records retain their bytes. The
earlier Accepted state applies to those exact inputs; it does not accept the
new public API semantics.

`tools/verify_public_api_history.py` verifies these retained bytes and runs the
original English and acceptance tools from the accepted pair, Design
`4c5c385779b753a4f06e59d07f80ad27ca10a841` and Plan
`dacaab7fc346da5b649e943a4d937a756345c492`. Current API content is English and is
checked independently; a historical translation-equivalence review cannot be
relabelled as review of new technical requirements.

## Candidate preparation

1. Finish and commit the authoritative Design declarations, native operations,
   type policies, source/coverage records and actual validation evidence.
   Preserve earlier failed attempts and distinguish design fixtures from actual
   product behavior. Coordinate the Design registry path before invoking the
   paired refinement script.
2. Run `python3 tools/refine_public_api.py --write-design-registry`. It preserves
   the old acceptance snapshots, updates the existing 48 task responsibilities
   and exact API-input hashes, proposes contract revision 0.4.0 and places the
   current Research/Documentation subjects in `review_ready`. It supplies no
   review and grants no acceptance or implementation authorization.
3. Run `python3 tools/render_packets.py` to synchronize the existing 114 packets
   and ten fragments. Run `python3 tools/verify_public_api_plan.py`, graph/schema
   checks and the meaningful negative gates. The packet's exact type policies
   identify related public declarations; its surface responsibility determines
   implementation ownership, avoiding duplicate definitions in shared B01 types.
4. Commit the paired candidate. Pin Plan to the actual committed Design candidate
   and registry hash, using `completion_stage: review_ready` and an explicitly
   unmerged candidate reference kind until acceptance and merge are complete.
   `verify_completion.py` intentionally rejects an uncommitted registry or a
   baseline that names a different Design HEAD.

Re-running refinement before acceptance is allowed when a reviewed fix changes
inputs; the old evidence archive is checked, not overwritten. An already accepted
0.4.0 registry cannot be reset by this script. Do not invoke the renderer after
acceptance without checking whether its bytes invalidate the accepted packet.

## Actual independent review and contract acceptance

The independent reviewer reads the final candidate, existing research and actual
logs, records findings and verifies each fix. A report must distinguish its
technical coverage from a prior author's source inspection or experiment run.
The final overall review must cover both repositories after the domain fixes.
Review reports are written by the actual reviewing agent; an integrator may
format bindings but cannot invent an independent actor or GitHub approval.

The scoped report directory contains `*-review.json` files. Each contract/task
subject has exactly one attributable accepting scoped report. A separate overall
report may discuss all subjects without duplicating scoped decisions. Required
report data includes the actual `reviewer`, UTC review date, an accepting
`decision`, empty unresolved blocker list, exact `review_inputs_sha256`, and
`contract_reviews`/`task_reviews` with the reviewed version/content or packet
identity. Current 0.4.0 review pins must cover the complete `required_paths` set,
and each task decision must include `semantic_node_sha256` computed by
`validate_graphs.node_digest` so unrendered graph semantics cannot drift. The format and required inputs are enforced by `review_bindings.py`.
An unfinished `*-review-notes.json` or a recovered script is not an acceptance.

With a committed Design source `DESIGN_SOURCE` and actual completed reports:

```bash
python3 tools/prepare_acceptance.py prepare-contracts \
  --design-source DESIGN_SOURCE \
  --report-directory ../NativeWeave-Design/docs/traceability/reviews/public-api-final \
  --contract-record-directory verification/public-api-acceptance/contracts/candidate
```

The script creates exact input, evidence and review bindings in a fresh directory
and records `prepared_not_accepted`. It refuses to overwrite any prior record.
The same independent reviewing executor must then inspect the generated bindings
and author an attestation matching the exact evidence/review hashes. Only then:

```bash
python3 tools/prepare_acceptance.py accept-contracts --attestation ACTUAL_CONTRACT_ATTESTATION
python3 tools/prepare_acceptance.py verify-contracts
```

Commit the accepted Design registry and records. Contract `source_commit` remains
the immutable input commit that was actually reviewed; the later acceptance
commit is a separate identity, avoiding self-referential hashes.

## Task acceptance and the two final PRs

Commit Plan's frozen packet/graph input and pin the committed accepted Design
candidate. A current baseline must carry the actual registry hash. Prepare the
66 task bindings with both exact source commits and a fresh record directory:

```bash
python3 tools/prepare_acceptance.py prepare-tasks \
  --design-source DESIGN_ACCEPTANCE_COMMIT --plan-source PLAN_INPUT_COMMIT \
  --report-directory ../NativeWeave-Design/docs/traceability/reviews/public-api-final \
  --task-record-directory ledger/public-api-2026-11-14/acceptance/candidate
```

The scoped reviewer checks the actual wrappers, dependency snapshots and complete
input hashes, and authors the task attestation. Then run `accept-tasks` with that
attestation and `verify-tasks`. Set `completion_stage: accepted_design` only after
all current subjects have actually passed these checks. Current formal gates are:

```bash
python3 tools/verify_public_api_history.py
python3 tools/verify_public_api_plan.py
python3 tools/prepare_acceptance.py verify-contracts
python3 tools/prepare_acceptance.py verify-tasks
python3 tools/verify_completion.py --require-complete
python3 tools/validate_graphs.py --output verification/graph-validation.json
python3 tools/mutation_checks.py
python3 tools/host_selection_checks.py
```

The PR workflow also retains native-source/provenance, logical-admission,
source-lifecycle, Rust and JSON-schema gates. These scripts validate evidence and
bindings; they do not rerun the native experiments or execute Delivery.

After the independent final candidate review and necessary checks, create one
Design PR and one Plan PR. Resolve findings on those same branches and verify the
actual final head and Required Checks. Merge Design first. Record its returned
merge commit and compare its actual normative content to the reviewed candidate.

Update the existing Plan PR to the merged Design SHA and registry hash. Preserve
pre-merge task records, review reports and index as history. A changed acceptance
source requires fresh task input/wrapper records in a new directory and a new
exact binding attestation by the actual independent reviewer; do not edit old
accepted snapshots or reuse their hashes. With the merged Design checked out and
the unchanged Plan input committed, use:

```bash
python3 tools/prepare_acceptance.py rebind-tasks \
  --design-source DESIGN_MERGE_COMMIT --plan-source PLAN_PRE_REBIND_COMMIT \
  --report-directory ../NativeWeave-Design/docs/traceability/reviews/public-api-final \
  --task-record-directory ledger/public-api-2026-11-14/acceptance/merged
```

This verifies the complete previous acceptance, requires byte-identical reviewed
inputs at both new commits, archives the previous index, and returns only the
new source binding to `prepared_not_accepted` / `review_ready`. It does not grant
acceptance. The actual reviewer must inspect the new hashes, author the new
attestation, and then `accept-tasks` may apply it. If normative bytes changed, reopen the
affected technical review as well. The unchanged declaration/specification
content can be confirmed by exact byte comparison without repeating successful
native experiments. Re-run current Plan and historical gates at the merged pair,
obtain the final exact review and merge the same Plan PR.

No script may fabricate CI results, impersonate another GitHub reviewer, disable
Required Checks or modify repository permissions to complete this sequence.
