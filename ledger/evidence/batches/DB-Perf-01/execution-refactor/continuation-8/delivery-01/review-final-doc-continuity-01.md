# Final documentation continuity review — DB-Exec-11

Review time: 2026-11-26T11:27:41.646680+00:00. Reviewer: `design_ci_review`. This pass read existing
source, documents and delivery receipts. It did not run a gate, build, test,
benchmark, profiler, archive operation or network mutation.

## Finding and scope

No new product correctness blocker or disagreement between the final report's
measurement scopes and the merged Design implementation record was identified.
Three active Plan navigation entries were stale; following root's explicit
follow-up authorization, only those three files received new current sections.
All previous file content is preserved verbatim under explicit historical labels.
No repository commit was made. Root owns the remaining report/handoff/delivery
updates and final gate execution.

| Binding read | Actual identity |
| --- | --- |
| Plan reviewed baseline | local `55eb3e159af7da744da800d3ee4aa99dc5e6f923`, tree `e154ad070a7ca2dcc8078385afc6f22fa3c51b91`, equivalent to public final evidence `adcdc9172bf47a0df8fe5fcb8259357625526280` |
| Merged Design | `ca9348ad0b5cc93bc75c502460d8e1b75843d109`, tree `ffe6f94306985bacde708e75d1e93a29e096c724`; local reviewed `649bce20e7e14a2e3908107c417e1a5fcfa0fb3b` has that tree |
| Merged product | `7ff7b57b907b689defb880b8af62d83679608603`, tree `bc9087d843d8d741d83d44f53d0b2c5af26dcffc`, identical to measured public `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` |

Merge/tree bindings come from `merge-receipts-01.json` and
`merged-trees-and-main-runs-01.json` in this delivery directory, plus local Git
identity reads. The current main Verify success and still-pending official
registry/public-AOT boundary are root's current delivery observation; the older
main-run receipt itself still records its earlier in-progress state.

## Navigation corrections made

| Plan path | Former active statement | Targeted correction |
| --- | --- | --- |
| `README.md` | DB-Exec-02 proposed target, implementation/performance pending | New current DB-Exec-11 delivery section before the intact historical continuation |
| `CURRENT-PHASE.md` | Repository rename maintenance; DB-Perf stopped | New current delivery section and explicit historical-maintenance boundary |
| `ledger/evidence/batches/DB-Perf-01/execution-refactor/README.md` | Recovered `47fe650`, Find still in progress, final credit 0/4 | New completed-campaign/delivery section; old DB-Exec-10 text explicitly historical |

Each new section links to `continuation-8/final-report.md` and
`continuation-8/delivery-01/README.md`, records the observed normal product/Design
merges and product main Verify success, and keeps official public readback/AOT
pending. The latter file is intentionally owned by root and must exist before
final document validation. All three sections retain short-versus-long scope,
unproven framework-only 0 B, bounded optimization claims and local-only
performance execution. The exact edit receipt is `plan-navigation-edit-01.json`.

## Remaining root-owned final documentation actions

1. Update the active batch `plan.md` and `handoff-linux.md` paragraphs that still
   call evidence publication and normal merges the next step. The final report's
   delivery section and continuation-8 README should link the actual delivery
   receipt, and reflect only the release/public-AOT outcomes already observed.
   Main Verify success alone must not be relabelled as the entire publication
   workflow's success. Root should refresh the three new navigation sections'
   pending sentence after the independent public verification results arrive.
2. The current implementation reference in `continuation-8/final-report.md`
   still pins Design `ca1933e93678039b492f10a8b47045b11827f1a4`. That is a valid
   historical source review, but its top status says 0/4. Use the actual merged
   Design `ca9348ad0b5cc93bc75c502460d8e1b75843d109` for the current
   `docs/database/execution-path-17da.md` link, preserving earlier pins in the
   original evidence/reviews. The implementation tree and source references
   remain unchanged by this status update.
3. The final delivery record should distinguish the measured `ci.1` package and
   executable identities from the independently rebuilt `preview.4` publication
   identities. Equal product trees do not make their binary hashes identical.
   Each provider needs its own actual artifact/readback/public-consumer outcome.
4. The Plan delivery evidence commit's own required checks/main observation remain
   a subsequent receipt; do not predict success from this review or prior CI.

## Claims that must retain their current boundaries

**Ordinary Fluent, Prepare and Find are distinct entry routes.** Merged Design's
entry table correctly says ordinary Fluent still composes a bounded NWQC command
and invokes native compilation; `.Prepare()` retains compiled SQL and parameter/
projection layouts but writes execution values; fixed-key Find reuses a
Source-owned exact-Table/mapper shape and bypasses the general shape-cache
hash/LRU route. Ordinary Fluent and public Prepare still use that general cache.
All row-producing routes converge on the pull transport and typed reader.
Do not describe ordinary Fluent as encoding-free, or `.Prepare()` as a physical
PostgreSQL/SQLite statement cache. Arbitrary Fluent method-body SQL generation
is not implemented.

The final report's combined Prepared/Find row is accurate because it attributes
the cache bypass specifically to Find. Its long workload is explicitly prepared
mode; the separate 1/100/1000-row phase evidence covers ordinary Fluent, warmed
Prepare and complete SQL. Final long rates therefore do not establish a new
30-minute ordinary-dynamic-Fluent comparison.

**The 0 B goal is unmet, with its exclusive numeric cost unmeasured.** The report
already states that source still creates framework execution objects. A fresh
read of product `QueryContext.Stream`, `FindPlan.Execute`, `TypedStream` and
`HostStreamTransport` agrees: stream, transport, controllers, enumerator/gates
and nonempty value frames remain. `FrameworkOnlyBytes=null` is unavailable
exclusive attribution, not zero. The measured approximately 24.8/25.5 KB per
successful mixed operation also includes business output, harness and driver;
it must not be called exclusive framework overhead. Prefer the report's
explicit unmet/unproven language over implying that the only obstacle is a
missing counter.

**Stopping remains bounded.** The report and merged Design correctly retain
17da after the particular quiet-close alternative failed its prospective rule.
This is not evidence that every remaining copy, metadata rebuild, cache lookup
or queue is necessary or that no further measurable gain can exist. The
independent stopping review names concrete, unmeasured alternatives. Final
delivery can close the selected implemented/validated round without claiming
that global optimization or the zero-allocation target is complete.

**Long and short comparisons remain separate.** The report correctly identifies
120-second same-condition before/current improvements (SQLite 542.872 to
2,668.577 success/s; PostgreSQL 1,241.453 to 3,458.224) and four new 1,800-second
candidate/Dapper observations. It does not contain a new 30-minute before
candidate. Preserve this in the final summary; the historical review phrase
“long-run improvements against the matched baseline” must not supply a missing
long-before result. Frozen arrival-rate completion ratios are not saturation
capacity measurements. Historical pre-campaign data retain their original host
record, while the final audit supplies the current campaign's host binding.

**Other scopes remain consistent.** Both documents preserve all 35 diagnostic
SQL text differences per provider and `runtimeSqlTraceVerified=false` despite
source/generated-factory normalization. The final report correctly distinguishes
client CPU from server CPU, measurement-window GC deltas from offered-end
cumulative counts, and observed idle duration from requested 15 seconds. Its
SQLite Dapper peak uses final wait4 maximum 35,479,552 B; endpoint VmHWM
33,923,072 B is a distinct retained observation. Do not replace the final table
with the earlier endpoint value.

## Review sources

- [Final evidence report](https://github.com/IzuSharp/Plan/blob/adcdc9172bf47a0df8fe5fcb8259357625526280/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/final-report.md)
- [Independent stopping review](https://github.com/IzuSharp/Plan/blob/adcdc9172bf47a0df8fe5fcb8259357625526280/ledger/evidence/batches/DB-Perf-01/execution-refactor/continuation-8/final-stopping-review-01.md)
- [Merged Design execution record](https://github.com/IzuSharp/Korda-Design/blob/ca9348ad0b5cc93bc75c502460d8e1b75843d109/docs/database/execution-path-17da.md)
- [Actual Fluent stream construction](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Query.Fluent/QueryContext.cs#L175)
- [Actual Find execution](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Orm.Relations/FindPlan.cs#L160)
- [Actual typed stream layouts and enumeration](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Data.Streaming/TypedStream.cs#L30)
- [Actual pull transport ownership](https://github.com/IzuSharp/Korda/blob/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa/src/Data.NativeHost/HostStreamTransport.cs#L16)
