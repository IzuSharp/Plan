# DB-Scope-01 Linux handoff

## Current checkpoint

- Active task: **DB-Scope-01**, Linux x64; branch `task/DB-Scope-01-linux` in all three repositories.
- Sequence: old PR closure and local cleanup complete; initial Plan committed/pushed and [PR24](https://github.com/IzuSharp/Plan/pull/24) created at `b56ef7a6d4fc8c38cf8da04d555f30bae4e0693a`. Design pruning checkpoint is complete and [Design PR14](https://github.com/IzuSharp/NativeWeave-Design/pull/14) exists. **Product pruning is committed and [product PR20](https://github.com/IzuSharp/NativeWeave/pull/20) is open. Formal clean-source Linux regression execution is in progress.**
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

1. Continue formal attempt1 from the clean published product `26328245e69560192e23071a6bba24aa57a3b2fd` (tree `b9074932ece04e4350f7784cb7b79e1ff452266d`), using `_validation/logs/formal-attempt-1.log`. The active command is `../_validation/with-postgres.sh python3 -u eng/build.py verify --design ../_validation/frozen-design --plan ../_validation/frozen-plan`. Do not launch another wrapper against the same PGDATA.
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

This is source inspection only. Plan parent before this correction is published `012324e22f51b2308a5f1fb64e2399fe60f04168`; Design parent is published `02e8eabc8fcb81d61fc9b6468fe099acae17f2b3`. Plan correction publication is pending; Design correction and the additional orphan code pruning are held in that order. Existing original-scope implementation remains in progress. Historical evidence bytes are unchanged.

## Integrated product checkpoint and independent review repairs

- Design final candidate: `3d1b4d5d80b8e3d8790481276a8333c0d2a25754`, tree `74f886a74a38d0478d1c4b4a22ea17383dfd0424`, PR14. Earlier scope-correction head2a8 passed all current/historical workflows; final documentation ownership correction now has its own CI run.
- Product first candidate: `26328245e69560192e23071a6bba24aa57a3b2fd`, tree `b9074932ece04e4350f7784cb7b79e1ff452266d`, PR20. Transported local c16d135 has the identical tree; formal execution uses the published identity.
- 668 changed paths remove owned servers/protocols/proof/demo products and orphan generic tooling. Cargo removes55 dependencies, adds none, and preserves241 retained versions/checksums. Retained database/runtime/public API/ABI sources are unchanged from the fresh main; required Core friend assembly entries are pruned.
- Mixed database fixtures now directly execute ordinary C# business queries. The default package matrix includes both independent PostgreSQL conflict/COMMIT-loss oracles, lifecycle/nullability checks, and finite provider/filesystem/outbox crash/recovery cases in every runtime/provider row. No listener, performance tuning or 30-minute load test is introduced.
- Independent review restored the unique equal-created_at composite-keyset traversal and valid-cursor tamper/tenant/principal checks. It also replaced broad evidence copying with selected sanitized result JSON bound to original raw-file hashes; private configuration and raw argv remain local. The canary test passed.
- Actual preliminary source smoke results exist under `_validation` and are explicitly not candidate-package acceptance. Initial filesystem smoke failures were retained and repaired by a bounded fixture read/write loop; actual SQLite ENOSPC provider13 and both providers' corrected interruption cases passed. Formal candidate execution reruns them.
- Shared packaging keeps all applicable guards: schema/JSON/closure/RID/CPU/ABI/path/native selection,14 release/recovery cases, and actual local unlisted NuGet V3 exact-version restore. The artificial packaging product is removed. The actual PackageClosure API/XML and Core A01–A08 verification remain in the default gates.
- Local environment is Debian13 Linux x64; local Rust traps do not claim a pristine machine or the Ubuntu24.04 baseline. GitHub's unchanged declared Linux row is required for those additional claims. The old HelloWorld public publisher is retired; new database packages are local candidates only.
