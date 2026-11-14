# Authoritative English Plan and acceptance migration

This Plan is the one-to-one English rendering of accepted source `eff98a38068478cd4c2abb4ea66c62330156941b`, paired with the Design source `08e3aaee73aad174620dcff18ed21b3b14c5e632`. The task system remains 34 Research tasks, 32 Documentation tasks, 48 future Delivery tasks, three graphs, 114 task packets, and 10 implementation fragments.

The [translation manifest](english-translation-manifest.json) covers 139 existing documentation, graph, fragment, and renderer files plus the completion validator's English task-revision heading literal. It records exact source/target hashes, actual translators, and independent reviews. Current packet input tables point to the translated specification bytes; historical experiment and review hashes remain unchanged. Technical versions and task revisions remain unchanged because this is a language migration.

The original accepted task records remain in `ledger/acceptance/`. New records are separate in [ledger/english-translation/](ledger/english-translation/), and the current [completion acceptance index](ledger/completion-acceptance.json) selects the new exact bindings only after the actual reviewers attest them. Each new input snapshot identifies its original accepted subject, source commit, evidence hashes, and review hashes. The migration validator checks those claims against the original Git objects, rather than merely replacing a hash in an old review.

All current English packet text, graph prose, fragments, policies, templates, and renderer text received independent source-to-target review. Graph review uses `semantic_projection_v1` to avoid a report/graph hash cycle: only packet/content/source/evidence/review binding metadata is excluded, with exact validation of those fields performed separately. IDs, versions, statuses, authorization, dependencies, paths, and all prose remain covered. The final manifest pins the complete graph bytes.

Six files preserve original-language content solely as immutable historical migration/recovery programs or a frozen independent review. The manifest lists their exact paths, hashes, and reasons. They are evidence, not a parallel language edition. No original experiment, result, failure, or review is rewritten or claimed as newly executed.

## Current state and verification

The graphs and acceptance index are authoritative for current formal status. The completed migration retains 34 Research and 32 Documentation tasks as `accepted`, all 21 Design contracts as `accepted`, and every Delivery task as `planned_candidate` with `not_authorized` implementation authorization. It does not start product implementation or change the NativeWeave product repository.

With Design checked out at the exact commit in `source-driven-baseline.json`, run:

```bash
python3 tools/verify_english_translation.py
python3 tools/migrate_english_acceptance.py verify-contracts
python3 tools/migrate_english_acceptance.py verify-tasks
python3 tools/verify_completion.py --require-complete
python3 tools/validate_graphs.py
python3 tools/mutation_checks.py
```

The existing CI also runs the original historical-evidence and schema gates. Final CI does not use the translation checker's `--preflight` mode. Historical gates continue to execute at their original immutable pairs; their old proposed states do not replace current acceptance.

Design merges first. `source-driven-baseline.json` then records its exact merge commit, registry hash, and translation provenance before Plan's final CI and merge. Original acceptance records and historical source references remain available throughout.
