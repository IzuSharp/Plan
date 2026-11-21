# DB-Scope-01 Linux handoff

## Current checkpoint

- Active task: **DB-Scope-01**, Linux x64; branch `task/DB-Scope-01-linux` in all three repositories.
- Sequence: old PR closure and local cleanup complete; initial Plan committed/pushed and [PR24](https://github.com/IzuSharp/Plan/pull/24) created at `b56ef7a6d4fc8c38cf8da04d555f30bae4e0693a`. Design pruning checkpoint is complete and [Design PR14](https://github.com/IzuSharp/NativeWeave-Design/pull/14) exists. **Product and packaging pruning is now in progress.**
- Continue from this file and the DB-Scope-01 PRs. Do not delete this new workspace, repeat completed cleanup, resume Perf-01, or relabel historical evidence.
- Read [plan.md](plan.md), [baseline.json](baseline.json), [acceptance.json](acceptance.json) and `delivery-graph.json.current_execution`.
- Dependency correction: the initial `Generators.Model` retention was incorrect. This Plan update is ready for publication; current Design must be corrected before the additional orphan generator/analyzer/native-build/artificial-packaging deletions begin.

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

1. Publish the dependency-audit Plan correction, then update/publish current Design and record its checkpoint. Only then prune the newly identified orphan generic tooling and migrate its relevant guards to real database candidates. Continue the already authorized product pruning and unique database regressions.
2. Confirm current/frozen Design CI for published correction `02e8eabc8fcb81d61fc9b6468fe099acae17f2b3` without changing archived bytes.
3. Run retained Rust/C# and real PostgreSQL/SQLite regressions, then all four external PackageReference JIT/AOT cells.
4. Copy actual task logs/results into this batch and bind passed claims using [evidence-format.md](evidence-format.md); keep pending or failed rows honest.
5. Complete independent review and required PR checks; merge normally and observe exact merged-main CI for all three delivered PRs.
6. Append the observed Plan postmerge receipt in an evidence-only followup record, finalize acceptance without self-referencing a future commit, and stop.

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
