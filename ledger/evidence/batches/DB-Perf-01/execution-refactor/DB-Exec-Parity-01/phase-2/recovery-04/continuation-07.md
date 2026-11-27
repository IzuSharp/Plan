# Continuation07 — tail completion remains a measured hypothesis

This checkpoint continues [Continuation06](continuation-06.md). **The final four 1,800-second cells are still 0/4.** Integrated05 remains the published provisional candidate. Tail-completion06 has passed the selected correctness and source-review gates, but its mechanism and ordinary performance have not yet been measured. Neither implementation is declared at parity.

## Work now completed

The complete finite pressure analysis is directly readable in [pressure-05](pressure-05/README.md). All16 short cells passed587 independent checks: 1,320,000 attempted businesses,1,140,143 successful,179,857 admission rejections and zero business errors. Candidate05 reaches continuing rejection at the high rates; Dapper still mostly tracks the highest offers tested. Transient refusals are non-monotonic, so a first nonzero counter is not a capacity boundary. The report retains per-second ledgers, successful-case mix, latency, client CPU/allocations/RSS/GC and separately scoped PostgreSQL observations. These are existing observations, not reruns or long-cell credit.

The complete zero-cost/pressure raw evidence, wrapper reviews, cleanup receipts and local controls were published in archives03 at Plan `d7e2d96db38e2879e0318692e00575158db42a77`, subtree `3faaaa9b9b034950fe1e517d55e02b18f2027ba6`. Root readback matched all30 entries, including the three upload logs. It contains942 expanded members; it excludes the then-active tail06 work. Plan CI on the preceding `abb995591c914aa6011369992d6f3a2bec5c3b05` succeeded in run45968251781. The archive03-head run45971774868 was still in progress when last observed; this checkpoint does not predict its conclusion.

## Tail-completion06 identities and contract evidence

The [hypothesis](tail-completion-hypothesis-06.md) was recorded before product changes. It tests the interaction of the already-measured Worker-D path and safe completion publication. The old standalone Common-A performance rejection remains unchanged.

| Input | Exact identity |
| --- | --- |
| Integrated05 base | Korda `2ea67ce1902f330679c3ebff4d6d5733be20f69c`, tree `4e3989f2ce9e0c554585aab5a8bbb656e689b18d` |
| Tail product change | Local `39d9b27c27e891b5a48b6541b629a43de3d1036d` |
| Tail ordinary source, including tests | Local `4a9e4435ea5c836be44fb00dc4219301567072c6`, tree `a7065978ba432dfba71f177435232090cf154d34` |
| Before diagnostic source | Local `197f0d3444cf3cfc120982273d48d1dcf74f60db`, tree `37615cdc87f1df5d223bd95714094d87f9b63028` |
| Tail diagnostic source | Local `ba4e7ec9bf93ad313dbbb167457189a5f95429da`, tree `924a6c2958e4bcb8a9b3992bb8ecb9eddb05a84b` |

The [retained ordinary source patch](tail-completion-06/ordinary-source.patch) moves the captured completion publication after old coordinator bookkeeping and retirement, and allows the eligible pending continuation to run inline. Generation/version guards, ownership retirement, exception identity, captured contexts and late registration remain contract requirements. No C++/SQL/DTO/batch/runtime/public API change is included in this hypothesis. An inline continuation is allowed to reset and start the next generation, so the old frame must not read that next generation or translate its exception into a scheduling failure.

The actual Release Native AOT NativeHost suite passed both providers: ReadyScheduling12 scenarios/226 assertions each; WorkerExecution4/21 each; the full run ended with438 assertions,36 managed retirements and zero tracked native owners. The [receipt and raw consumer log](tail-completion-06/correctness-01/receipt.json) are retained. These are project-reference correctness consumers, not package/performance evidence. The independent correctness review retains1,489 checks. Its first review-script schema mismatch remains recorded; the raw product run was not changed to satisfy that checker.

The same new tests on the original implementation form the [negative control](tail-completion-06/negative-control-01/receipt.json). It exited250 at the expected SQLite exact-Post-exception assertion. This is a matched negative control, not a baseline correctness pass. PostgreSQL business assertions were not reached, as the [coverage record](tail-completion-06/negative-control-01/coverage.json) states.

Both ordinary provider consumers were built through actual independent NuGet packages `0.1.0-parity06.1`, then checked by `verify_final_consumer.py`. The [build identity](tail-completion-06/ordinary-consumer-builds-01.json) binds actual generated C#, ELF/debug, package and native image hashes. Native images are reused exact integrated04/05 bytes because the native source is unchanged; their original build identity is preserved. The committed impact plan selects interop, Linux and independently validated PostgreSQL/SQLite top-level packages. No performance CI step is added or selected.

All four diagnostic package consumers are now built and bound; see the [four-consumer identity](tail-completion-06/diagnostic-consumer-builds-01.json). These are separately versioned instrumented packages, with source patches and metadata retained here. Their logger adds allocation, locking and clock P/Invoke calls. It can establish request/queue/setter counts and event relationships; its CPU and latency cannot establish ordinary performance gains. The raw harness does not know about internal instrumentation, so the outer diagnostic record must explicitly deny timing credit.

## Immediate continuation

1. Validate finite same-query traces using the four completed diagnostic consumers. Use controller/generation/version identity, monotonic timestamps, both thread IDs and the actual setter interval. A same-thread observation alone is not inline completion proof. Global log sequence is writer-lock order, not a global timestamp order. Direct coordinator offers/Execute calls and source-inferred MRVTS dispatch must remain separate.
2. If the mechanism is proved, run a quiet ordinary interleaved/reversed integrated05/tail06/Dapper screen on the already built exact consumers. Preserve the original8 SQLite/11 PG cases and existing early-stop/money risks. Bind the reviewed PPid observer, actual input bytes and clean retirement; no new benchmark enters CI.
3. Select or reject the new interaction using measured mechanism and repeated ordinary outcomes, then perform only the indicated mixed/pressure follow-ups. The current candidate05 PG scheduled-p99 and released-RSS regressions remain unresolved evidence, not hidden by the new hypothesis.
4. Freeze the selected actual package consumers; supplement matched before long evidence, execute the requested four serial30-minute candidate/Dapper cells with separate warmup, and collect separately identified native-allocation evidence. Finish independent review, normal merges and existing release/public NuGet AOT verification.

## Recovery and evidence boundary

Resume in `/workspace/scratch/0669b59f9cae/DB-Exec-Parity-01`. The [implementation state](tail-completion-06/implementation-resume.json) and local build receipts distinguish finished work from pending mechanism/performance work. Do not rebuild passed ordinary consumers or repeat the28 completed short mixed cells merely because a chat connection stopped.

An explicitly reviewed cleanup removed only308 old, singly-linked compilation objects and byte-identical duplicate bin outputs, with complete prevalidation and intent. The [receipt](closed-build-cleanup-06/cleanup-actual-receipt.json) records1,167,843,328 allocated bytes released. Actual ELF/debug/native/package/generated/source/raw/failed records remain. Four older Worker-D diagnostic nupkg files totaling27,456,713 bytes were found to lack an archives01/02 member match; their actual ELF/native/debug evidence is archived. The package files remain local and are an explicit [incremental archival todo](closed-build-cleanup-06/pending-package-archive.json), not falsely labelled durable.

This checkpoint publishes source patches, receipts, logs and independent reviews for tail06. The new actual tail06 ordinary/diagnostic ELF/debug/package bytes remain local pending their closed-input increment; archives03 does not contain them. Go drafts Korda#39 and Plan#35 remain untouched. This is a restart checkpoint, not completion or an instruction to stop.
