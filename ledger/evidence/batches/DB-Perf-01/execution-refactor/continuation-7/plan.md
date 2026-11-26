# DB-Exec-10 — recovered execution-path continuation

This is the 2026-11-26 (Asia/Shanghai) continuation of the owner's complete
database refactor, preserving Korda #37, Korda-Design #20 and Plan #34. Work uses
`/workspace/scratch/fd78534029f7/worktrees/DB-Exec-10-*`. The previous workspace
`/workspace/scratch/4a65d70f0fe1` remains intact and supplies the pinned toolchain,
package consumers, original failures and raw measurements. No prior outcome is
relabelled as a new execution.

## Current execution checkpoint

The formal candidate is now public `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`
with successful existing CI and independently consumed provider packages.
[Current CI/package review](current-ci-review.md),
[Find validation](find-validation/README.md),
[current allocation audit](current-measurements/allocation/README.md) and
[rejected final-close experiment](close-quiet-experiment.md) bind their own
exact sources. The original recovered-state section below is historical.

[Campaign selection](local-load-tools/current-campaign-selection.md) now owns
the remaining offered validation, matched 120-second before supplement and
four serial final cells. Source 17da remains unchanged; final credit is still
0/4 at this pre-campaign checkpoint. Preserve all short observations, rejected
experiments and failures before the final archive and normal reviewed merges.

## Recovered state

- Product public HEAD `47fe650dfed5d7bba1c4d74c4a127c5d08b66082` is tree-identical
  to local `e3298d2356fa35802e7615bd322724bc4d27f9ba`. Existing CI45761578521
  completed successfully. Its preceding `8789a45` run failed formatting; the
  correction and both observations remain distinct.
- Design public HEAD `4a6bb899366a071973f3de2dcd0621683072a705` is tree-identical
  to local `5d9fcf1`. Plan public HEAD `b748d89e` predates recoverable local
  `938d781`. The latter's continuation-6 records and untracked input archives
  are recovered without modifying their bytes.
- The nine groups in `artifacts/command-short-series-01.json` completed. They
  bind row316/command8789 ordinary consumers, separate FFI consumers, query-phase
  consumers and an isolated PostgreSQL commit-proof candidate. Their full
  analyzer run and evidence publication are still required. A directory name
  containing `single-row` does not make its numeric32 workload a one-row query.
- The existing `DB-Exec-09-find-cache` worktree is clean at8789a45. Its complete
  proposal is retained in continuation6; there is no recovered implementation.
- No product build, local load or PostgreSQL process was observed at recovery.
  The remote heads were fetched before editing. Only the root publishes shared
  branches and all remote updates preserve any newly observed commits.

## Ordered work and owners

| Work | Decision and required evidence |
| --- | --- |
| Recover evidence | Recompute strict analysis of the nine completed groups, retain failed analyzer attempts, source/package/ELF hashes and generated Dapper factories. Separate ordinary timings from diagnostic counts. |
| Fixed-key Find | Select the continuation6 proposal in Design before implementing. Reuse NativeQuery/NativePlan/rendering and existing cursor pull, privately compile ordered key slots once, preserve terminal3 and exact Table mapper identity, and bound cache entries/bytes by Source lifetime. No public ParameterRegistry consumption or new public Prepare requirement. |
| PostgreSQL commit proof | Independently review local `cd8bf3d`/`bf2f384`/`d2c137b`; retain only if existing transaction state on this exact idle physical connection safely replaces the pre-COMMIT SELECT1. Keep post-COMMIT, unknown-outcome and pool-return confirmations. Bind negative controls and ordinary measurements separately. |
| Complete path review | Reconcile reuse/rewrite/delete decisions for dynamic composition, fixed/prepared shape, parameter ownership, provider waits, direct batches, generated mapping, cancellation and final release. Delete only replaced paths with no genuine callers. |
| Correctness and packages | Run affected existing Native AOT/module checks, exact API/ABI and independent PostgreSQL/SQLite package consumers. Add finite correctness assertions within their owning existing suites. Inspect `python3 eng/ci/impact.py origin/main --output artifacts/plan.json`; explain all selected scopes before proceeding. |
| Local measurements | Freeze exact candidate source/packages/ELFs, run matched rows1/100/1000 phase and allocation/ABI diagnostics, then calibrate concurrent mixed offered load. Supplement before evidence under the same current-host conditions. Run Korda and Dapper.AOT on both databases in four sequential continuous1800-second cells; do not build, profile or run another load during timing. |
| Delivery | Preserve failures and limitations; report throughput, latency, errors/rejections, CPU, RSS, allocation and process GC with full consumption. Complete independent review, normal PR merges and existing CI/rule-selected release checks. |

Performance remains local Linux x64 work. Existing workflow jobs, diff/dependency
routing, independent package verification and frozen historical checks retain
their roles. Final long-run credit at recovery is0/4. No framework0B or complete
delivery claim follows from short tests, green CI or a compiled candidate.
