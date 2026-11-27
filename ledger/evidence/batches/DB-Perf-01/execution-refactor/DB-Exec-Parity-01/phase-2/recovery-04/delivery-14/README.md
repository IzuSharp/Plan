# Delivery14 evidence index

Read [Continuation14](../continuation-14.md) for the current result and final
recovery rule. Local performance work is finished. Both public `preview.5`
standalone package consumers passed. Performance parity remains unproved.

## Records

- `delivery-verification.json`: observed product/Design/public-package/archive
  results; the Plan record's own future merge/main result is explicitly separate.
- `public-release/public-release-summary.json`: compact two-provider release
  result, exact packages, artifact and payload identities.
- `public-release/public-release-audit-final.json`: complete read-only audit.
- `public-release/evidence-index.json`: original frozen public result files.
- `public-release/delivery-input-manifest.json`: ordinary-file expansion of
  relative audit inputs; no scratch symlink is required to replay the audit.
- `public-release/delivery-safety-audit.json`: the saved-evidence content review.
- `archive06/publication.json`: actual remote tree/commit/ref publication.
- `archive06/readback-passed.json`: all 117 actual blob bytes and exact subtree
  verified, using the already fetched immutable Git objects.
- `archive06/readback-first-attempt.json`: preserved disk-gate stop before any
  blob was read. It is not a failed archive or a performance run.
- `archive06/readback-manifest.json` and `archive06/readback.py`: exact repeatable
  membership/hash contract and the actual successful reader source.
- `repository-receipts/`: prior actual Korda/Design merges and existing CI.
- `status-before14.json`: previous current-status bytes, retained unchanged.
- `entrypoints-before14.json`: identities of the navigation files before update.
- `source-records.json`: all saved delivery payload sizes, hashes and original
  provenance. It excludes its own digest to avoid a recursive hash claim.

All supplied archive/source/runtime identities retain their original scopes.
The original phase evidence manifest is a historical snapshot, not a manifest of
the later mutable navigation files. Reproduce derived audits in a writable copy,
because their original scripts generate fresh observation reports.

## This record's own closure

An immutable commit cannot contain an observed result of its own future merge or
CI. [Plan #36](https://github.com/IzuSharp/Plan/pull/36) carries that final receipt
after both operations occur. On recovery, consult it once; successful exact-head
PR checks, normal merge and exact-merge main CI close this round. A document gate
never authorizes restarting measurement or relabeling incomplete parity as passed.
