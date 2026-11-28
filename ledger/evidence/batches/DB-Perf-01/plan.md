# DB-Perf-01 / DB-Exec-11 — plan and final scope

The task preserved the C# Fluent contract, Native AOT, C++20/libpq/sqlite3 execution
and independently installable provider packages. Measure actual costs under the
same business contract before selecting changes; separate provider/SQL work,
command construction, values, batching, mapping, scheduling and cleanup.

## Recorded sequence and outcome

1. Establish both-provider baselines and actual end-to-end resource boundaries.
2. Review the native driver/command/stream path, then select safe implementation changes.
3. Validate ownership, cancellation, bounded batches, error propagation and public package use.
4. Compare before/current using bounded short runs; keep instrumented diagnostics separate.
5. Complete the selected four serial 1,800-second Korda/Dapper.AOT cells on Linux.
6. Review and deliver the selected 17da path; preserve remaining gaps and rejected alternatives.

The [final report](execution-refactor/continuation-8/final-report.md) records actual
long results, separate short comparisons and observed delivery. The current
historical graph entry retains its original task state; the final report owns
the later measured outcome. No new benchmark or product change is selected here.

## Retained decisions and open questions

Complete native command compilation, direct bounded batches, typed command
completion and specialized Find shape reuse were retained. The evaluated quiet
final-close alternative failed its declared guard; inline callback completion
was rejected for a post-publication exception/ownership hazard.

The [stopping review](execution-refactor/continuation-8/final-stopping-review-01.md)
rejects an optimality claim. Three [remaining attribution directions](execution-refactor/continuation-7/remaining-hot-path-costs.md)
are general immutable shape lookup, immutable SQL/descriptor ownership and
per-batch readiness/continuation scheduling. Their individual measurable benefit
is unresolved. Required value snapshots and lifetime/notification fences remain.

[Workload requirements](workloads.md) retain the comparison rules. Raw logs,
samples, source/binary copies, receipts and recovery checkpoints stay local;
formal plans and final conclusions are maintained through Git/PRs.
