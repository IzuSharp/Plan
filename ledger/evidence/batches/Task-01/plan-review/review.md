# Task-01 final Plan validation review

Reviewer: `/root/b01`. Scope: read-only Plan validation/record placement; no product reimplementation, historical native experiment rerun, Plan edit, acceptance mutation or GitHub approval claim.

## Conclusion

The Linux-scoped Task-01 batch ledger is the appropriate record for the user's explicit current authorization and actual A01/A19/A21/B01 component completion. Preserve the exact accepted research/design graphs, source-driven baseline, registry and previous acceptance bindings. The batch must state Linux x64 completion, deferred unexecuted platforms and `global_acceptance_claim: false`; it must bind the four final implementation/evidence/review records and the two existing PRs.

This conclusion follows the current user instruction together with Plan AGENTS rule 4 (track product obligations separately), execution-policy Local Dependencies and Component Acceptance (component completion may precede downstream host assembly), and the actual existing validator scope. It does not turn a historical planning validation into product acceptance.

## Read-only checks actually performed

- `validate_graphs.Validator(Plan).run()` passed, with 34 Research, 32 Documentation and 48 Delivery nodes, no structural errors.
- All four selected packet SHA-256 values and all 84 task API input hash entries matched.
- Sibling read-only Design HEAD exactly equals locked commit `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`; registry content hash matches the baseline.
- Three graphs, source-driven baseline, AGENTS, execution/API policy, four key validators and the relevant PR workflow were byte-identical to initial Plan commit `050d54cc2433901cbe896f7490af0e94ba631415`.
- Results: `graph-validation.json` and `readonly-input-review.json` beside this report. Python ran with `-B`; reports were written outside Plan.

## Relevant existing validators

The standalone structural/pin check accepts an external output path and is safe for this read-only review:

```sh
python3 -B tools/validate_graphs.py --root . --output /absolute/outside/Plan/graph-validation.json
```

`tools/verify_public_api_plan.py` adds current exact API/type/owner checks, preserved-history byte checks and six focused negative cases. Its CLI writes `verification/public-api-plan.json`, so it was inspected rather than invoked in this read-only review. Its graph-based checks explicitly retain all Delivery nodes as `planned_candidate / not_authorized` in the accepted planning snapshot.

`tools/prepare_acceptance.py verify-contracts`, `tools/prepare_acceptance.py verify-tasks` and `tools/verify_completion.py --require-complete` verify the existing 21 contracts and 66 Research/Documentation bindings. They do not accept or inspect the four new Delivery implementations. The completion CLI writes `verification/completion.json`. No `prepare-*`, `accept-*`, `rebind-tasks`, refinement or packet-render action is required for ledger-only additions.

No existing script/schema automatically discovers or validates `ledger/evidence/batches/Task-01/status-linux.json`, the Markdown handoff, or arbitrary component result JSON. `Validator.check_acceptance` follows only evidence referenced by terminal graph nodes. `schemas/evidence-manifest-v1.schema.json` applies to its specific acceptance-manifest format; it is not a schema for all raw result/status JSON.

## Existing PR workflow gates

`.github/workflows/native-slices-final-check.yml` matches `pull_request` to main with `ledger/**` changes. Its `paired-integrity` job checks out the actual PR head and the exact Design SHA read from the unchanged baseline. Preserve and observe that existing workflow. It runs these commands; its step is explicitly labeled no native rerun:

```sh
python3 tools/verify_public_api_history.py
python3 tools/verify_public_api_plan.py
python3 tools/prepare_acceptance.py verify-contracts
python3 tools/prepare_acceptance.py verify-tasks
python3 tools/binding_attestation_checks.py
python3 tools/verify_completion.py --require-complete
python3 tools/verify_research_assets.py
python3 tools/verify_logical_admission_history.py
python3 tools/verify_source_lifecycle.py
python3 tools/source_lifecycle_binding_checks.py
python3 tools/validate_graphs.py --output verification/graph-validation.json
python3 tools/mutation_checks.py
python3 tools/host_selection_checks.py
python3 tools/rust1100_checks.py
```

The job then installs pinned `jsonschema==4.23.0` and applies `jsonschema.Draft202012Validator` with `schemas/graph-v1.schema.json` to each of the three graphs. The historical scripts validate immutable historical records and bindings; they do not require replaying successful native research experiments. No additional local replay or new CI/platform matrix is necessary just because the batch evidence was added. This review does not assert knowledge of GitHub branch-protection settings; the root executor must follow the actual PR checks/review process.

## Why the global planning snapshot should remain unchanged

`verify_public_api_plan.main` and `verify_completion.verify` explicitly require every Delivery node to retain `planned_candidate` and historical `not_authorized`. `validate_graphs.Validator.architecture` rejects in-progress/terminal Delivery states while the accepted historical phase flag is false. Separately, full Delivery terminal acceptance checks every declared platform requirement; Windows is deliberately unexecuted this round. Changing those global fields would falsely broaden this Linux-only delivery and invalidate unrelated accepted planning bindings.

Their report fields such as `product_delivery_executed: false` describe the verification scope/accepted research snapshot. They are not a revocation of this conversation's explicit implementation authorization and are not the source of the Task-01 Linux completion claim. The new ledger already states this distinction; retain it clearly in the final batch handoff.

## Concrete finalization gaps observed during assembly

At review time, `handoff-linux.md` still listed all four tasks in progress and said no task had passed acceptance; `status-linux.json` still carried intermediate checkpoints; A21 and B01 evidence directories had not yet been copied. These are record-finalization gaps, not runtime findings. Root is concurrently assembling them.

Before final publication, the two batch records should agree on the four Linux component results, actual final author/integration/publication commits, integrated versus pending commits, exact independent review paths, package/experiment outputs and required exclusions. All referenced local evidence must exist after copying, and copied manifest hashes must match retained bytes. Preserve the local-to-remote Git tree mapping where GitHub publication produces different commit identities. Retain both actual PR URLs and describe other-platform work as deferred, without marking all-platform/global acceptance.

No additional normative change or task expansion is required.
