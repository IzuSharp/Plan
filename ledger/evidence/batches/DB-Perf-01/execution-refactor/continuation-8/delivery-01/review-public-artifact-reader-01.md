# Independent review of the public artifact reader

## Scope and result

This was a **pre-execution source review** of `/workspace/scratch/166b48a091b9/delivery-01/read_public_artifacts.py`. The reviewer did not execute the reader, add or run tests, build anything, trigger CI, repeat signature verification, or execute an AOT consumer. Public artifact acceptance remains pending actual artifact acquisition and inspection.

The reader's artifact paths, release/package fields, registry verification fields, and consumer receipt schema agree with the existing release implementation and both available candidate artifacts. Three completeness gaps identified in the initial reader have been corrected by the parent and confirmed by one subsequent source read. No remaining concrete correction is identified within this review's scope.

These findings concerned completeness of a new delivery-evidence reader. They were **not observed product failures, CI failures, signature failures, or failed public consumer executions**.

## Sources examined

The existing product checkout is `/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-korda`, corresponding to the previously established frozen source tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc` and public candidate commit `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`. The parent supplied the normal merge identity `7ff7b57b907b689defb880b8af62d83679608603` with the same tree. This review did not independently fetch remote state or recompute tree identity.

Read sources included:

- `.github/workflows/release.yml`: candidate download destination, public artifact paths, registry readback JSON and the `consume.py --public` invocation.
- `src/Packaging.Release/release.py:130–133` and the existing compatibility verifier: exact `verify_registry` result fields and the distinction between upload bytes, signed registry bytes and accepted unsigned entries.
- `eng/ci/bundles.py:120–187`: release/package provenance, `native`, `upload_archive_sha256`, `unsigned_entries`, and package fingerprint fields.
- `eng/ci/orm_experience.py:120–325`: six command receipts, three business rows, exact execution-result extraction, appended row fields and tutorial/DTO comparisons.
- `samples/api/orm-experience/Program.cs:258–260`: the seven-field runtime business receipt.
- Actual `delivery-01/candidate-{sqlite,postgresql}/release.json`, candidate business receipts, and original execution logs, read only to verify the current schema and field names.

## Confirmed bindings and boundaries

The public artifact reader accepts the workflow's common-root layout by locating the unique retained release and plan, the registry verification file, and `consumer-evidence/public/{provider}.json`. The candidate records actually have one package each and use the expected `native.path`, `native.sha256`, `source_commit`, version and package fingerprint fields.

The registry receipt fields read by the helper match the existing writer: `verified`, `resume_allowed`, `unsigned_entries_equal`, `mode`, `upload_sha256`, `registry_sha256`, and nested `signature`. The helper binds the downloaded registry package bytes to `registry_sha256`, and the AOT consumer's `tutorial_package_sha256` to those same signed public archive bytes. It correctly does not demand equality between upload archive SHA and signed registry archive SHA.

The existing CI remains the source of cryptographic signature verification and actual Native AOT execution. The helper reads retained observations and checks byte/receipt consistency; it does not establish those events by rerunning them. A successful helper result must still be reported alongside the applicable CI job/step conclusions. Public artifacts can be uploaded after partial failures because the existing upload step uses `always()` when registry verification was selected.

The two provider release records are independent. Their successful public receipts do not imply execution of the combined two-provider graph.

## Findings and confirmed corrections

| Initial finding | Correction observed in current reader | Source basis |
| --- | --- | --- |
| A length check of six command entries did not guarantee one publish and one execute for every revision. Repeated publish entries could leave execution logs unbound. | Lines 87–90 retain the six-entry count and require the set of `(revision, stage)` values to equal `scaffold/original/edited × publish/execute`. With six required distinct pairs and exactly six entries, each pair occurs once. | `orm_experience.py:143`, `184–224`, `226`, `242`. |
| Runtime result comparison was only a subset comparison; an empty `DB_API_RESULT` object could pass it. | Lines 113–115 require exactly `Provider`, `Aot`, `Dto`, `Checks`, `SqlExecutions`, `ProtocolSubmissions`, `NativeSha256`, and equality with the corresponding row's seven-field projection. | `Program.cs:258`; `orm_experience.py:243–286`. |
| Original and edited tutorial maps were compared only to one another, without binding them to the tutorial manifest. | Lines 99–101 require both maps to match the four-entry mapping from each tutorial's `compiled_file` to `compiled_sha256`. | `orm_experience.py:293–297`. |

The exact runtime fields agree with both actual candidate execution logs. The SQLite candidate records `Provider=Sqlite`, `SqlExecutions=2`, `ProtocolSubmissions=0`; the PostgreSQL candidate records `Provider=PostgreSql`, `SqlExecutions=2`, `ProtocolSubmissions=8`. These are schema corroboration from candidate consumption, not observations of the pending public consumer. The SQL/submission values refer to the consumer's defined page/detail observation window, not all SQL issued by the entire process and not a count of required protocol replies.

## Disposition

The three requested corrections are present and match the source contract. The reader is ready for the parent's eventual public-artifact readback within its stated evidence-binding scope. No execution result is claimed here. A separate review of the actual public artifacts and final CI conclusions remains outstanding.
