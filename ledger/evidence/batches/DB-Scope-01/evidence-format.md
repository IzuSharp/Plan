# DB-Scope-01 evidence and closeout format

Schema version: 1. [acceptance.json](acceptance.json) owns current claim state. [evidence-schema.json](evidence-schema.json) documents the wire shape; `tools/verify_db_scope.py` enforces file bytes, source binding, package-task boundaries and final CI identities in addition to that shape. Pending claims with empty evidence and partially discovered PRs remain valid.

## Actual evidence files

Copy sanitized command logs, program result JSON, package/native identity reports, independent reviews and GitHub run metadata into this batch before claiming a pass. Preserve failed attempts. A receipt is a small JSON envelope that binds those actual files; a receipt's prose or a URL alone is not raw evidence. All paths below are canonical paths relative to the Plan repository and remain under `ledger/evidence/batches/DB-Scope-01/`.

Each evidence reference has exactly these fields:

```json
{
  "path": "ledger/evidence/batches/DB-Scope-01/receipts/sqlite-jit.json",
  "sha256": "SHA256_OF_EXACT_RECEIPT_BYTES",
  "sources": {
    "NativeWeave": { "commit": "FULL_TESTED_COMMIT", "tree": "FULL_TESTED_TREE" }
  }
}
```

The referenced receipt has this shape:

```json
{
  "schema_version": 1,
  "task": "DB-Scope-01",
  "platform": "linux-x64",
  "claims": ["sqlite_package_jit"],
  "outcome": "passed",
  "sources": {
    "NativeWeave": { "commit": "FULL_TESTED_COMMIT", "tree": "FULL_TESTED_TREE" }
  },
  "artifacts": [
    { "path": "ledger/evidence/batches/DB-Scope-01/results/sqlite-jit.json", "sha256": "SHA256_OF_ACTUAL_RESULT" },
    { "path": "ledger/evidence/batches/DB-Scope-01/logs/sqlite-jit.stdout", "sha256": "SHA256_OF_ACTUAL_STDOUT" }
  ]
}
```

The placeholders are explanatory and fail validation until replaced with actual full lowercase Git SHA-1 and SHA-256 identities. Receipts can include additional observed command, provider/runtime, package, data-assertion or review details. Their `claims` list must contain every claim that cites them. A failed/blocked receipt cannot support a passed claim. Every receipt and raw-artifact hash is checked against the file bytes; missing files fail. References cannot cite `acceptance.json` or cite the receipt itself as a raw artifact.

The receipt's `sources` must exactly equal its reference. Product execution claims must bind `acceptance.json.candidate_sources.NativeWeave`. Independent review evidence collectively binds both the product and Design candidate source identities. A candidate source is `{ "commit": ..., "tree": ... }`; local and transported commits may differ only when the integration record proves their equal tree. Do not silently substitute a different source or reinterpret old measurements.

Files can be prepared in the current task workspace, but commit the receipts and bound artifacts before publishing acceptance. CI reads committed files and cannot validate an uncommitted local log. These checks establish recorded consistency, not authenticity of human identity or physical execution; actual logs, data assertions and independent review remain essential.

## PR and CI evidence

Before merge, a PR record may contain its exact URL, `state: "open"`, observed initial/head identities and pending CI. A final merged record requires:

```json
{
  "url": "https://github.com/IzuSharp/NativeWeave/pull/ACTUAL_NUMBER",
  "state": "merged",
  "head_commit": "ACTUAL_REVIEWED_HEAD",
  "head_tree": "ACTUAL_REVIEWED_TREE",
  "merged_commit": "ACTUAL_MERGE_COMMIT",
  "merged_tree": "ACTUAL_MERGED_TREE",
  "head_checks": ["STRUCTURED_EVIDENCE_REFERENCE"],
  "merged_main_checks": ["STRUCTURED_EVIDENCE_REFERENCE"]
}
```

Replace each explanatory string in the two arrays with the structured reference object above. Its receipt binds actual GitHub metadata artifacts and carries `required_checks_complete: true` plus a nonempty `ci` array:

```json
{
  "repository": "NativeWeave",
  "url": "https://github.com/IzuSharp/NativeWeave/actions/runs/ACTUAL_RUN_ID",
  "head_commit": "ACTUAL_MERGE_COMMIT",
  "scope": "merged_main",
  "branch": "main",
  "status": "completed",
  "conclusion": "success"
}
```

Use `scope: "pr_head"` and claim `required_pr_checks` for the reviewed head, or `scope: "merged_main"` and claim `merged_main_ci` for the merge. The receipt's source commit/tree must match the corresponding PR identity. URLs must name the same IzuSharp repository. Every required run is observed and recorded; unfinished, failed or merely skipped CI is not a pass. Product and Design merged trees must equal their tested/reviewed candidate trees. A changed merge tree requires renewed applicable validation and review.

Passed global PR/main-CI claims require all three repositories' source coverage and valid CI references in their PR records. Truthy strings, a bare PR URL, a merge SHA without CI, or evidence from another head cannot satisfy final acceptance.

## Honest Plan postmerge lifecycle

Keep acceptance `in_progress` while the delivered Plan PR is still open or its main CI has not completed. Merge through the normal required checks. After observing the actual Plan merge and its successful main runs, append their hashed metadata receipt in an evidence-only followup commit/PR and mark the delivered three-PR snapshot accepted.

That record binds the already observed Plan merge, **not the future commit that contains the receipt**. No receipt predicts its own containing commit's CI or hashes itself. The followup's own CI is checked separately before final handoff. Product/Design source bindings remain exact; Plan's CI receipts bind their explicitly recorded head/merge independently. This lets the final record remain truthful without an impossible recursive chain of self-attestation.

## Verifier controls

The verifier tests missing evidence, changed receipt bytes, changed raw artifacts, reference/source disagreement, candidate/source disagreement incomplete merged PR records, wrong CI commits/branches, incomplete required checks and changed merged trees using explicit in-memory fixtures. Both a partial pass and a complete accepted-state shape have positive controls. They are never written to the evidence directory or treated as product execution. Scope/order/premature-acceptance controls and unchanged historical preservation checks remain enabled.
