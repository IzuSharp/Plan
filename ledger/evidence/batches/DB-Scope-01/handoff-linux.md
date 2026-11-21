# DB-Scope-01 Linux handoff

## Current checkpoint

- Active task: **DB-Scope-01**, Linux x64; branch `task/DB-Scope-01-linux` in all three repositories.
- Sequence: old PR closure and local cleanup complete; initial Plan committed/pushed and [PR24](https://github.com/IzuSharp/Plan/pull/24) created at `b56ef7a6d4fc8c38cf8da04d555f30bae4e0693a`. Design pruning checkpoint is complete and [Design PR14](https://github.com/IzuSharp/NativeWeave-Design/pull/14) exists. **Product pruning is committed and [product PR20](https://github.com/IzuSharp/NativeWeave/pull/20) is open. Candidate4 is committed/pushed and its clean-source Linux components plus full CI are running after the provider integration repairs passed targeted JIT/AOT.**
- Continue from this file and the DB-Scope-01 PRs. Do not delete this new workspace, repeat completed cleanup, resume Perf-01, or relabel historical evidence.
- Read [plan.md](plan.md), [baseline.json](baseline.json), [acceptance.json](acceptance.json) and `delivery-graph.json.current_execution`.
- Dependency correction completed in order: Plan `d74f6bc` → Design `2a8a300` → orphan code/guard migration `19252c6`, now included in the published product candidate. Query.Generator and actual database binding generation are retained.

## Completed stop/cleanup

Product PR19 and Plan PR23 were observed open and closed without merge on 2026-11-21, with an explicit scope-reduction/Perf-01 termination comment. Dependabot PRs 3/4/7 were untouched. The sole old completion automation `Automation_5cee7a136e348191bbefc5b2f398a189` was already disabled. No current old subagent or task process was found. 42 old worktrees, three old repository caches, old builds/native binaries/performance datasets/temporary databases/scripts and old task toolchain copies were removed. Exact deletion targets and post-deletion checks are in [cleanup-linux.json](cleanup-linux.json). System/account data and unrelated projects were preserved.

Only the current Linux execution host is exposed in this session. No other Linux/MCP/SSH connection was discovered, so no claim is made that inaccessible hosts were stopped. User systemd bus inspection is unavailable; no cron configuration or task-owned unit was found. Old Plan run [44902123431](https://github.com/IzuSharp/Plan/actions/runs/44902123431) still reported in progress after PR closure. The GitHub connector has no cancellation action and the browser is signed out; the run subsequently completed successfully, so there is no remaining old run to cancel. No new old-branch writer or workload was started.

## Fresh main inputs

- Plan: `8afa0311f45ab8a8157fc45c51e95a0b17dd09f2`.
- Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
- Product: `ea5fa528035d025bd7a28698ee7c71194432236c`.
- Local task root: `/workspace/scratch/6c5fd6ee7a2b/.worktree/DB-Scope-01-linux/`.
- Fresh validation tools/caches are under `_validation/`; they are not old Perf-01 artifacts.

## Next actions

1. Continue candidate4 clean-source local components from published `4fb02c9e4cf7d0e46cc0cf8fc9f587bb49ff9a37`, tree `498b34a6fc67ba3361a0be0120a3ed0d7cd1dcd5`. Active command: `../_validation/with-postgres.sh python3 -u ../_validation/run-local-components.py --source-commit 4fb02c9e4cf7d0e46cc0cf8fc9f587bb49ff9a37 --source-tree 498b34a6fc67ba3361a0be0120a3ed0d7cd1dcd5 --attempt candidate4`. Read `_validation/progress-candidate4.json` and `_validation/logs/candidate4-local-components.log`; do not start another wrapper on the same PGDATA or edit product source during this run. Full exact-head CI44910999098 is also running. Prior local artifacts, including candidate3 final workspace outputs, remain under `_validation/attempts/`. Local full-format/strict-container limitations remain unchanged; all production gates remain mandatory in CI.
2. Inspect actual regression/package failures, retain failed attempts, and make only necessary scope regression repairs. New candidate identities require corresponding source-bound evidence; never overwrite a completed attempt.
3. Execute retained Core/minimum CPU checks locally where applicable; exact-head CI supplies the declared Ubuntu baseline, genuinely no-Rust SDK image and runtime-only transfer.
4. Bind actual logs/results and independent reviews using evidence-format.md. Keep all four external PackageReference JIT/AOT cells pending until actual execution validates data and native mappings.
5. Complete required head CI, independent reviews and normal Design/product/Plan merges. Observe exact merged-main CI, then append the honest Plan postmerge closeout receipt and stop.

## Plan-first and validation environment checkpoint

Initial local commit `0fc538018a0e949ff53e0f94be480534f67b1ba8` and remote commit `b56ef7a6d4fc8c38cf8da04d555f30bae4e0693a` have exactly the same tree `1cc04940d6281e80b4ba8aa0f51a291cf37a542e`; local branch was synchronized only after tree verification. Git CLI push lacks credentials, so authorized publication uses the GitHub connector. `verify_db_scope.py` and five meaningful rejection controls passed; existing graph structure passed with 34 research, 32 documentation, 48 delivery and 21 accepted historical contracts unchanged.

Fresh official .NET 11.0.100, Rust/Cargo 1.100.0, Clang 19.1.7 and PostgreSQL 18.0 were installed in `_validation/`. PostgreSQL preflight verified durable settings on. Each execution call has isolated loopback reachability: use `../_validation/with-postgres.sh <command>` so the server and tests run in the same invocation; do not run two wrappers on the same PGDATA. Preparation is not product acceptance.

## Initial CI failure retained

[Initial Plan CI44903409175](https://github.com/IzuSharp/Plan/actions/runs/44903409175) passed current scope validation and historical graph checks, then correctly rejected the changed workflow as differing from an old acceptance-bound input (`Plan:.github/workflows/native-slices-final-check.yml`). No check was suppressed. The workflow now runs the complete original historical gate list against immutable Plan `8afa0311f45ab8a8157fc45c51e95a0b17dd09f2` and Design `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`, while current scope plus preservation validation runs on the actual PR head. This avoids treating historical approval as acceptance of new workflow bytes.

## Design-before-product checkpoint

Design local commit `68c011c6bf78387a8103ee0bc91a845d17434083` and published commit `1d40ddffd11dde731dc5792d0ff9a05883e819cc` share exact tree `9b61c35cbf29497b81f28015a46b810954a2e33e`. [Design PR14](https://github.com/IzuSharp/NativeWeave-Design/pull/14) contains the current database scope and frozen historical separation. The local scope check verified 22 active documents, 24 archived specifications, the twelve-package closure, retained source paths and six rejection controls. This is Design structure/source evidence, not product execution.

Product edits were released only after that Design checkpoint. Database Host and all existing database capabilities remain required; product and packaging agents now work on their disjoint implementation scopes.

Initial Design current-scope CI [44904378111](https://github.com/IzuSharp/NativeWeave-Design/actions/runs/44904378111) passed the scope check but failed its blanket whitespace check on an original archived trailing blank line. Historical acceptance CI [44904378087](https://github.com/IzuSharp/NativeWeave-Design/actions/runs/44904378087) passed. Correction local commit `54d886dba6b47f4e889a81bdf79ae9d5b07b6fc8`, tree `6beeba6a7a82c5059cfab42bcaf9282f21f2bc99`, preserves archived bytes: the validator first proves each exact frozen blob, then excludes only those proven archive paths from whitespace checking. All current files and other additions remain checked. Its local combined scope/whitespace check passed. Published correction `02e8eabc8fcb81d61fc9b6468fe099acae17f2b3` has the same exact tree; current/frozen CI is pending observation.

## Evidence binding and honest closeout

`acceptance.json` now uses evidence schema version 1. A passed claim requires a structured reference to a real task receipt and hashed raw logs/results/reviews, with exact source commit/tree identities matching the candidate. Final PR records require URL, actual head/merge identities and source-bound completed-success CI receipts. The verifier includes in-memory controls for missing files, receipt/artifact hash changes, source mismatch, incomplete merged PRs, wrong CI commits/branches, unfinished required checks and changed merged trees. Both partial and final accepted shapes are exercised using in-memory positive fixtures. These synthetic controls are not product evidence.

Keep acceptance `in_progress` through the Plan PR merge. After its actual merged-main CI is observed, an evidence-only followup can append that receipt and mark the delivered three-PR snapshot accepted. The receipt binds the already observed Plan merge, never the future commit containing the receipt. The containing followup's own CI is checked separately; this avoids circular hashes or predicting a future success.

## Dependency correction checkpoint — generic tooling

The initial Plan row and Design map wrongly retained `src/Generators.Model`. The [immutable fresh-main audit](dependency-audit.json) enumerates actual project references and hashes the inspected inputs. Database static generation is `Query.Generator`; the native binding generator is the existing Query.Binding script/signature inventory. Generic Generators.Model/CSharp/Rust/Metadata and Analyzers have no database runtime or package dependency. Generic Build.Integration native tooling serves proof profiles; retain its actual API documentation tool/checks. Packaging.Release retains its real release engine, MSBuild task/targets and API check; move unique artificial conformance-package guard cases onto real database packages before retiring that fixture.

At the earlier source-inspection checkpoint, Plan parent was `012324e22f51b2308a5f1fb64e2399fe60f04168` and Design parent was `02e8eabc8fcb81d61fc9b6468fe099acae17f2b3`. The correction subsequently completed in order: published Plan `d74f6bc` → published Design `2a8a300` → orphan code and guard migration `19252c6`, included in product candidate26328245. Historical evidence bytes are unchanged.

## Integrated product checkpoint and independent review repairs

- Design final candidate: `3d1b4d5d80b8e3d8790481276a8333c0d2a25754`, tree `74f886a74a38d0478d1c4b4a22ea17383dfd0424`, PR14. Earlier scope-correction head2a8 passed all current/historical workflows; final documentation ownership correction now has its own CI run.
- Product first candidate: `26328245e69560192e23071a6bba24aa57a3b2fd`, tree `b9074932ece04e4350f7784cb7b79e1ff452266d`, PR20. Transported local c16d135 has the identical tree; formal execution uses the published identity.
- 668 changed paths remove owned servers/protocols/proof/demo products and orphan generic tooling. Cargo removes55 dependencies, adds none, and preserves241 retained versions/checksums. Retained database/runtime/public API/ABI sources are unchanged from the fresh main; required Core friend assembly entries are pruned.
- Mixed database fixtures now directly execute ordinary C# business queries. The default package matrix includes both independent PostgreSQL conflict/COMMIT-loss oracles, lifecycle/nullability checks, and finite provider/filesystem/outbox crash/recovery cases in every runtime/provider row. No NativeWeave application server/listener product, performance tuning or 30-minute load test is introduced. Isolated database fault proxies and the NuGet V3 verification fixture retain local listeners solely for regression testing.
- Independent review restored the unique equal-created_at composite-keyset traversal and valid-cursor tamper/tenant/principal checks. It also replaced broad evidence copying with selected sanitized result JSON bound to original raw-file hashes; private configuration and raw argv remain local. The canary test passed.
- Actual preliminary source smoke results exist under `_validation` and are explicitly not candidate-package acceptance. Initial filesystem smoke failures were retained and repaired by a bounded fixture read/write loop; actual SQLite ENOSPC provider13 and both providers' corrected interruption cases passed. Formal candidate execution reruns them.
- Shared packaging keeps all applicable guards: schema/JSON/closure/RID/CPU/ABI/path/native selection,14 release/recovery cases, and actual local unlisted NuGet V3 exact-version restore. The artificial packaging product is removed. The actual PackageClosure API/XML and Core A01–A08 verification remain in the default gates.
- Local environment is Debian13 Linux x64; local Rust traps do not claim a pristine machine or the Ubuntu24.04 baseline. GitHub's unchanged declared Linux row is required for those additional claims. The old HelloWorld public publisher is retired; new database packages are local candidates only.

## Formal attempt1 interim observation

Rust format/Clippy and the retained workspace completed successfully (86 tests passed; zero failed or ignored). Both independently configured database native builds completed and produced native manifest SHA-256 `82ee91583852045c7c66f3496711721b5ed88cd03362f4f65322957a151c8a5e`. The command was deliberately interrupted at the locked C# solution restore with exit130 when candidate2 superseded it; these partial results do not establish package or final acceptance. Product CI44906090871 reported one generic-api-key finding in a reference README; investigation proved a deterministic cursor fixture. Candidate2 replaces that fixed documentation value with private random generation and records only its exact historical false-positive fingerprint. Full-history/upstream rules remain enabled; an unrelated synthetic canary still fails scanning. Independent review corrected a stale Design tree pairing in baseline.json; the initial checkpoint now has a separate explicit record.

## Candidate2 and review corrections

- Published product `5498e971a75df8f6b3b007ec2479cc9d751387c8`, tree `9e8d98499e5394ab3f314c295eb3c7d903fd3b17`; local c2a8024 was transported only after exact tree verification. PR20 now points to this source. Formal attempt2 ran from the synchronized clean source; its local format failure and same-source continuation are recorded below.
- Independent packaging review PACK-01 found that a clean HEAD change during preparation could evade the final dirty-tree check. Preparation now captures the original source-file inventory and requires final commit equality, clean state and unchanged file hashes before manifest emission. The independent reviewer confirmed the correction. No runtime/API/ABI source changed.
- Default parallel solution restore stalled in attempt1 and reproduced a 75-second timeout with no output. The same locked/audited restore using existing single-node/non-reuse/shared-compiler-disabled parameters completed in 16 seconds with zero warnings/errors. Root restore/build now uses those parameters. Attempt2 has passed locked restore and is building the managed workspace.
- The verified historical cursor fixture is not an external credential. The replacement README snippet was actually executed and verified to generate 32 random bytes into a 0600 file under a 0700 directory. Exact-fingerprint scan remediation retained full-history/upstream rules and rejected an unrelated synthetic generic-api-key canary. Safe receipts are under security/.
- Separate exact-source Core/package/minimum-CPU verification is running under `_validation/core-candidate2`, with outputs in `_validation/core-candidate2-evidence`. Local Debian13 does not claim the Ubuntu24 baseline or pristine SDK/runtime containers; exact-head CI remains required.
- Independent Plan reviews preserved all historical graphs/packets and matched the dependency audit to fresh main. Baseline Design commit/tree pairing and stale checkpoint wording were corrected; fixture retirement explicitly remains conditional on actual migrated guard execution. All 14 acceptance claims remain pending.

## Candidate2 local environment limitation and current continuation

The full local attempt2 exited 1 at `dotnet format`: the environment denies creation of Unix sockets used by the Roslyn/MSBuild pipe server. Both a system temporary directory and the task directory reproduced the socket denial. No permission escalation, formatter substitution, ignored failure or CI skip was introduced. Full managed build had already completed with zero warnings/errors; failed logs and source identity are preserved under failures/. Actual format acceptance must come from unchanged exact-head GitHub CI.

The same clean candidate continues with compiled API/XML/DocFX, full database regression, package creation and external consumers through `_validation/run-candidate2-remaining.py`; it writes only a component result, never `artifacts/verification.json`. Compiled API/XML and DocFX now pass (318 site files, 24 HTML files); actual database regressions are running. Exact-head security scan, dependency review and C#/Python CodeQL all passed in CI44907140214.

Separate Core/package checks completed: six retained components pass actual outside-source JIT and Native AOT, zero Rust-trap calls, missing-native rejection, and unchanged AOT outputs on QEMU Nehalem with verified x86-64-v2/no AVX features. Local results remain Debian13, nonpristine; strict Ubuntu24 and runtime-only transfer still require CI. Evidence is under `_validation/core-candidate2-evidence`.

## Candidate2 actual API regression failure

The permitted remaining-component run exited 1 at the strict Data.Abstractions compiled API/XML gate after PostgreSQL version, canonical Query ABI, full Interop.Negotiation/Execution, documentation negative cases and packaging-task API passed. The compiled 149-symbol Data assembly contains 17 existing model-attribute/concurrency-exception symbols absent from the older 132-symbol B01 inventory. Source inspection confirms those implementations and project composition are unchanged from fresh main; all 17 exact signatures already exist in frozen Design c62cdb8 and the existing 149-symbol Orm Data reference. The implementation agent is repairing only the composed API inventory/reference and reported count, while another independent reviewer audits the other retained API gates. No new API or ORM feature is introduced. Failure log and identity are preserved under failures/. Candidate3 will be committed/reviewed/published before new source-bound execution.

## CI confirmation and broader composed API audit

CI44907140214 completed unsuccessfully at the same Data.Abstractions exact API gate; its full format and compiled API/DocFX steps passed, confirming that the earlier local formatter failure was environmental. The downloaded failed-run artifact matched GitHub SHA-256 `3825c3bbd83294e46644988abd886f3d57a63822dd27c82b0ee219ec6974c315`; its receipt and relevant regression log are preserved. Plan PR24 head f111e230 passed its complete historical/current workflow44907391491.

Independent audit found three existing B04 factory/builder symbols omitted from each provider inventory and stale 432-symbol composed Database references in Migrations and Host. Transactions, Streaming, Codecs, Binding, Fluent and Query.Generator strict compiled gates passed; Migrations/Orm/Host full exact Design/XML checks passed. Candidate3 repairs only current inventories/generated documentation and verifier reporting/provenance. Current generated Markdown must also pass the unchanged whitespace gate, so empty inheritdoc rendering is being corrected consistently rather than exempting generated current files.

## Published candidate3 — composed API inventories repaired

Product PR20 now points to `c0b810eb512c8907798a79842dac8eb1d4c6d55f`, tree `545ea5da6ca07b5cc66b0b1fc3b52bb83a12f887`. Local de8aac44 (including author commit 0aa9b1b3 and the root ABI provenance fix) was transported with exact tree equality and synchronized before execution. Only current API inventories/generated references and verification tooling changed; database runtime declaration and ABI source remain unchanged from fresh main.

The repaired full assembly inventories contain Data 149, PostgreSQL 15 and SQLite 32 exact symbols. Every old baseline record is preserved; all 17/3/3 additions already exist in immutable Design c62cdb8. Migrations and Host references now represent all 432 current Database symbols. The empty-XML renderer repair removes only trailing separators; Orm current Markdown was regenerated consistently, and historical Design/Plan bytes remain untouched. Full PR whitespace check passes. B01/A01 provenance inventories no longer hash the intentionally removed proof build target.

Actual strict API/XML/reference checks passed; 18 temporary negative cases still reject missing/extra APIs, changed signatures, missing XML summary/parameters and stale references. The unchanged shared API/DocFX suite passed 17 commands. Independent review reran the six affected API/composition gates, verified 14 generated files byte-for-byte, preserved all old declarations, and bound the result to the published candidate. No full database/package execution is claimed by these targeted checks. Safe review, source and negative-control receipts are under reviews/.

Candidate3 actual local components are running with all mandatory production checks still present in exact-head CI. All 14 acceptance claims remain pending until their new source-bound receipts and final merge/CI records are integrated.

## Candidate3 actual provider-profile integration failure

Candidate3 passed the retained Rust workspace (86 tests), independent native builds, locked full managed build (zero warnings/errors), compiled API/XML/DocFX, PostgreSQL version and ABI checks, complete interop/documentation controls and the repaired Data.Abstractions gate. It failed at the SQLite JIT assertion `exact build descriptor`. Full local verification remains false because the environment cannot run the Roslyn socket-dependent formatter. CI44908802224 independently passed format and the same preceding gates, then failed at Data.Sqlite JIT; all four security jobs passed. The failed CI archive matched GitHub digest `284a99d0b26b52fd612e5cd7edba63398ecbc3d05224f336d831804014090fa1`. Plan head ec0e1af4 passed CI44909007309.

Read-only integration audit traced the public providers to the already-existing full Database Host: `database.sqlite` with `nw_database_sqlite_get_abi_v1` and 23 capabilities, and `database.postgresql` with `nw_database_postgresql_get_abi_v1` and 24 capabilities. The legacy provider tests still assume standalone component IDs/capabilities; PostgreSQL also injects the legacy component library as its public Host asset, and both final asset receipts use obsolete names. The current provider guides contain the same old composition description. Production profile, facade, native ABI and runtime sources remain byte-identical to fresh main.

Candidate4 will separate the still-required private component fixture checks from exact public Host descriptor/asset checks, preserve all fourteen SQLite scenario groups and PostgreSQL TLS/transaction/session/failure oracles, and correct only those current tests/examples/guides. The other eleven audited regression/consumer scopes have no analogous stale public-profile assertion. Targeted development executions do not replace candidate4 clean-source regression or package acceptance. Audit and failed-run receipts are preserved under reviews/ and failures/; all fourteen acceptance claims remain pending.

## Candidate4 development checkpoint — exact profiles and AOT locks

The SQLite targeted dirty-source repair run now passes ordinary locked JIT and actual Native AOT, including all fourteen unchanged SQLite/B05 scenarios in both modes and exact private-component/public-Host preflight. The first targeted attempt correctly failed AOT locked restore because its old lock omitted the existing Host closure; that failure is retained. An independent audit of all 48 retained AOT lockfiles found exactly three stale files (the two provider tests and PostgreSQL sample), and confirmed the regenerated files add only existing project nodes/edges; every external package version and content hash remains unchanged. This is development validation, not clean candidate4 or external NuGet acceptance. PostgreSQL's full native/TLS plus managed JIT/AOT/sample targeted execution is next/in progress.

The two provider guides and all detailed original provider lifecycle/cancellation/transaction/TLS semantics have independent static review. Current CI now exports bounded sanitized per-component result/summary/status JSON even when a regression fails; the original failure still propagates. Private configuration, raw argv and raw fixture logs remain excluded. Three actual build/evidence control tests pass. The reviewer found no production runtime/native-fixture changes. Root owns this export delta, product_scope owns provider tests/sample/locks, and old_task_inventory independently reviews both; design_scope owns the two guides and separately prepares read-only final receipt validation. No agent is continuing Perf-01.

## Published candidate4 — retained provider fixture integration

Product PR20 now points to `4fb02c9e4cf7d0e46cc0cf8fc9f587bb49ff9a37`, tree `498b34a6fc67ba3361a0be0120a3ed0d7cd1dcd5`. Author commit52a38bfd (eleven test/helper/sample/lock files) and root69cfdcba (two guides plus three export/control files) were transported with exact tree equality, then synchronized only after a clean-state/tree check. Production runtime/API/ABI and the original native scenario code remain unchanged.

Targeted development execution passed SQLite JIT/AOT with 44 managed assertions and fourteen native groups per mode; PostgreSQL passed all28 verifier commands, its eleven real native/JIT/AOT oracle cases and both sample JIT/AOT paths. The targeted receipts explicitly retain their dirty-source/preflight-only scope; they are not final package or assembled-Host acceptance. Three lock repairs add only existing project closure and preserve every external package version/hash.

Clean candidate4 actual local components and full CI44910999098 are now running. Design final head3d1b4d5 passed all current/historical CI and exact independent source review; those actual observations are copied under ci/ and reviews/. All fourteen acceptance claims remain pending until clean execution, full external consumers, reviewed evidence and normal merge/main-CI closeout complete.

Independent final delta review confirms candidate4's exact published commit/tree, all sixteen changed file hashes and the successful targeted source inventories (142 SQLite /141 PostgreSQL inputs) against final bytes. It verifies all48 AOT locks, original fixture/runtime preservation, exact current profiles, both successful JIT/AOT paths and unchanged full error propagation/private-evidence controls. No blocker remains in the source delta. The prior c0b810eb product source review and 5498e971 packaging review are preserved as applicable unchanged-source history; the candidate4 delta review covers the newly changed files. Current clean execution and actual package/pristine results remain separate pending acceptance gates.
