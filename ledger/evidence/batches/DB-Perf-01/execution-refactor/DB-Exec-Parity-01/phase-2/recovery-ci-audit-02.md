# DB-Exec-Parity-01 recovery and CI audit 02

Read-only audit of the recovered task, performed on 2026-11-26. No build, benchmark, pressure workload or repository mutation was performed during this audit.

## Conclusion

The measured dual-provider Stage 1 gate is sufficient to start isolated causal experiments. It does not accept any final performance candidate. Final mixed35 campaign credit remains 0/4. Preserve completed Stage 1 and the twelve completed first-screen A/B plans; do not rerun them as recovery work.

The canonical measured table is Plan `ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/phase-1/phase-1-measured-gate.md`. It covers actual generated sources and binary/symbol identities, four routes, 1/32/100/1000 rows and early stop, 168 per-business baseline processes, 140 native-allocation diagnostic processes, SQLite engine counters, PostgreSQL direct poll versus wire-proxy scope, and ownership/cancellation/error contracts. Global scheduler cause, kernel instructions, exclusive spin ownership and complete per-business allocation stacks remain unknown. New lease-lock and numeric-configuration candidates still require their own count/resource evidence.

## Actual first causal screen

`measurements/causal-a-phase-ab-02/completion.json` records completed=true and cells=12. `analysis/causal-a-phase-ab-02.json` contains all 144 route/cohort results. The two rounds of 1000-row hot Prepare show:

| Provider / round | Baseline CPU us/op | Common-A CPU us/op | Provider-A CPU us/op |
| --- | ---: | ---: | ---: |
| SQLite / 0 | 3620.777 | 3531.517 | 3822.697 |
| SQLite / 1 | 3360.404 | 3671.482 | 3558.674 |
| PostgreSQL / 0 | 4424.102 | 4338.447 | 4425.949 |
| PostgreSQL / 1 | 4296.659 | 4386.605 | 4383.361 |

Common-A and PostgreSQL-A have no stable ordinary CPU benefit; successful correctness tests do not override this result. SQLite-A has an independently measured lookaside/malloc mechanism but not stable thousand-row endpoint benefit. None is integrated into the main task product worktree.

The newer local `analysis/postgresql-a-mechanism-01.md` proves Cancel::install 1002->0 in every measured thousand-row request in all three Korda routes. Cancel::detach=97, CallContext::check=2015, advance=1001, SINGLE_TUPLE=1000, PQclear=1004 and batch/SQL/protocol counts are unchanged. This counts-only overlay has no formal timing credit. The std::function heap-allocation premise was already disproved by actual SBO machine code.

Rejected alternatives remain rejected: unconditional libpq chunk32 changes partial-error row delivery and provider-row/byte admission; moving SQLite work onto the initiating thread conflicts with the existing Async contract; global runtime spinlimit changes remain sensitivity diagnostics rather than shipped settings. Historical unsafe completion and quiet-close attempts keep their original identities.

## Baseline and remaining acceptance

Eight rebuilt ordinary consumers, per-query phases, per-case baselines and diagnostic allocation scopes can be reused with their actual identities. Historical continuation-8 long runs cannot be rebound to the newly rebuilt binaries or credited as this task's final cells. No new mixed35 zero-refusal/pressure baseline was present at the reviewed checkpoint. `diagnostics/run_mixed_cell.py` was prepared but had no actual mixed-run receipt yet; its own validation deliberately grants no final-cell credit.

The helper uses the original manifest, fresh deterministic database, default runtime, separate warmup, and original normalized_result checker. Before the final freeze, verify its first real execution and secure adequate same-host before data, zero-refusal costs, increasing offered-rate comparisons and the historical queue/rates. Final evidence requires four serial ordinary 1800-second cells with separate warmup, frozen identities, complete business/second accounting, resource disposal, and independent review.

PostgreSQL server cost needs an explicit scope: the helper does not enable cgroup accounting. The unchanged observer's default non-atomic parent/live/reaped snapshots and wait4 lifetime CPU do not establish exact steady server CPU per success. Report their actual scope or resolve a better observation before long runs; never infer steady server cost from the old report.

## Persistence checkpoint

At audit time local Plan head was `0c4797bd5fb3a4ba491dcdca7340ee8ade10f303`, intended tree `606322ee0e1f43db7ced2bf5d81731ef7b9844fa`. `analysis/publish-Plan-evidence-01-progress.json` had exactly 30/125 uploaded blobs and branchUpdated=false. Partial blob uploads are not durable branch publication of the complete evidence tree. Subsequent upload receipts supersede this point-in-time count. The older SESSION-CONTINUATION contains stale in-progress/build/upload descriptions and must be reconciled against actual receipts.

## CI review

Read Korda AGENTS.md, module registration guide, ci.yml, build.yml, database_plan.py and registered module JSON. Benchmark directories are owned as tests without executable checks. Existing build paths remain compilation, correctness, API/dependency/security, package/AOT consumption and rule-selected release only. No benchmark/profile/calibration/pressure action may be added or called indirectly.

Common-A's committed impact selects interop, linux, postgresql and sqlite. Shared provider.cpp changes select linux plus both independent provider package lanes even if a changed conditional branch serves only one provider. Each selected provider retains build, pack, packed API, tests, public.consume-aot and public.validate. Rerun `python3 eng/ci/impact.py origin/main --output artifacts/plan.json` on the final committed integrated product diff before push; isolated candidate plans do not substitute for it.

## Requested historical PRs and final reports

Read all five live GitHub PR bodies using the repository API, and the locally recovered continuation-8 and continuation-9-go final reports.

| PR | Observed state / binding |
| --- | --- |
| https://github.com/IzuSharp/Korda/pull/37 | Merged; merge `7ff7b57b907b689defb880b8af62d83679608603`; measured predecessor head `17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa` |
| https://github.com/IzuSharp/Korda-Design/pull/20 | Merged; merge `ca9348ad0b5cc93bc75c502460d8e1b75843d109` |
| https://github.com/IzuSharp/Plan/pull/34 | Merged; merge `03efe57ffbe3046bd89919ddb2c16c90a377954d`; evidence head `bd0fbfb589e4380dbd15e5346fde81a9111bea03` |
| https://github.com/IzuSharp/Plan/pull/35 | Open Draft, unmerged, auto_merge=null; head `89804888b2e4967da69c18f09851ab6139717602` |
| https://github.com/IzuSharp/Korda/pull/39 | Open Draft, unmerged, auto_merge=null; head `d5f4f9d6616bad54a08aebb7d1aca7937b18eb93` |

The previous four 1800-second cells and both independent preview.4 signed NuGet/public Native AOT deliveries are completed historical evidence, with their old binary/package/host identities and explicit remaining CPU/latency/allocation gaps. The first PostgreSQL indexing timeout and same-version verification-only retry remain preserved. Sources: Plan continuation-8/final-report.md and delivery-01/README.md at bd0fbfb.

The two Go cells are completed record-only references, not rerun targets. Go SQLite's 222218466 cgo calls and 2992.478 business operations/s cover its mixed workload, retained statements and handwritten DTO mapping. Go PostgreSQL's pgx text protocol is not a libpq result-allocation control. Neither mixed total can become a normalized per-query Korda FFI cost. Both Go drafts must remain unchanged. Sources: Plan continuation-9-go/final-report.md at 39843ba498f618bbdc78415fa92ea753abe9f8c2, and the live PRs above.
