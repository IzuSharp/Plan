# Perf-01: SQLite request and operation timing diagnostic

**This diagnostic localizes observed time; it does not establish the cause of the failed formal C16 sample.** Both corrected instrumented runs completed with their original business and shutdown checks. Their records contain no recorder overflow or ownership invariant failure. Across the complete process lifecycle, the longest create/replay request scopes are dominated by the interval from BeginImmediate start entry to terminal callback observation. The observed admission and release gate waits are much shorter. The original failed formal comparison is preserved and receives no replacement or acceptance from these runs.

The distributions below include startup, seed, warmup, offered load, recovery and cleanup. They are **not measurement-window trace percentiles**. Each role has one diagnostic process, with observer overhead and preallocated storage. No noise test, capacity credit, long-duration credit, or retained-product-change decision is made.

## Actual identities and completeness

Before diagnostic source: `e494c9890de5af684c4222722fd471379cb5910d` over `ea5fa528035d025bd7a28698ee7c71194432236c`. After: `38b1abac07bcb947291941a6c504fe3fbd40dfd9` over `2f40348c3db80a4fbee7a99e721b374a597b16df`. Common business/driver source: `2e3995df8d86583ee9443348276ca8d918056bfc`. Source indexes, actual executable/module hashes, observer manifests and original execution/summary hashes are recorded in the JSON companion.

Both traces have 49,982 operations and 34,508 scope frames. Before has 18,633 gate records; after has 12,422. Both have 6,211 actual HostTicket request scopes, four unscoped migration/cleanup operations, zero scoped operations missing a public phase, and zero unmatched gate records. All 49,982 operation snapshots in each trace have native status 0 and AcceptedReturned start outcome.

The original recording_complete flag is true in both. Independent checks found contiguous unique operation/frame IDs, matching parent/frame/ticket relationships, and no negative measured intervals. All recorded retirement snapshots report Released and NativeQuiet, with RootLive false, Controls/CallbackEntries/RetainedInputBytes zero. Overflow, recorder faults, reentrancy, duplicate events, scope mismatch, setup failures, missing expected boundaries, late capture, active operations and active frames are all zero. Terminal callback observation legitimately preceded StartReturned 3,607 times before and 4,571 times after; this is not classified as an ordering failure.

The actual SQLite native hash is unchanged: `63f01de214b727a6b7c976902e7f508f568ac08629a64c0332d67da028295346`. Actual Server hashes differ by role exactly as their package manifests require: before `63c4950fceab5fe52017b5457b04759201de5a261d8087939cb177a20a5b88e2`, after `8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0`. PostgreSQL is a supplied package asset, not an actually loaded module in these SQLite processes. No binary was re-read for this analysis; the post-drain recorder hashes were matched to the pinned observer manifests.

Each recorder reports 27,530,152 managed bytes of observed startup preallocation. This overhead is an additional reason not to use diagnostic values as formal before/after performance acceptance.

## Original driver results: descriptive, one process per role


| Role | Successful business operations | Successful operations/s | Whole-mix p99 ms | Cycle p99 ms | List p99 ms | Business retry attempts |
| --- | --- | --- | --- | --- | --- | --- |
| before | 3001 | 50.006482 | 185.795629 | 207.031034 | 42.358732 | 0 |
| after | 3001 | 49.886937 | 167.403169 | 227.100834 | 36.494571 | 0 |

The whole-mix p99 is lower in the after diagnostic, while the cycle p99 is higher: 207.031034 → 227.100834 ms. This adverse distinction is preserved; the mixed percentile is not substituted for the cycle result. Both original summaries are valid and qualify under the unchanged diagnostic run criteria, with zero recorded BUSY/LOCKED errors and retries. That does not measure successful internal SQLite busy-handler waiting or retry activity.

Both independent durable oracles report 1,637 items, operations and outbox entries, with passed=true; both recorded shutdowns show the database and consumer resources released successfully and the Server disposed. These original business checks remain distinct from recording_complete. The original startup failure caused by the missing runtime witness is retained as a failed attempt and is not used to derive these timing distributions.

## Observed operation intervals

All values below are milliseconds, from the complete lifecycle. Start entry is before managed Start-control setup; terminal is when callback fields have been copied into managed state. These values include provider/runtime/callback work and are not physical SQLite lock time. BeforeTake→RetiredObserved includes taking/materialization, native quiescence and continuation observation of existing Retirement; it is not a timestamp of native silence.

| Public phase | Role | Native operations | Start→terminal p99 | Terminal→take p99 | Take→retirement observed p99 |
| --- | --- | --- | --- | --- | --- |
| OpenSession | before | 6211 | 2.990404 | 0.356441 | 9.444160 |
| OpenSession | after | 6211 | 1.257584 | 0.229460 | 9.592548 |
| BeginImmediate | before | 3178 | 179.279885 | 0.255563 | 10.328929 |
| BeginImmediate | after | 3178 | 229.417868 | 0.204798 | 10.805009 |
| ClaimQuery | before | 11187 | 0.886172 | 0.286831 | 11.700597 |
| ClaimQuery | after | 11187 | 0.799646 | 0.260716 | 11.154437 |
| InsertItem | before | 1653 | 1.230479 | 0.301237 | 11.751718 |
| InsertItem | after | 1653 | 1.148586 | 0.188419 | 11.935021 |
| InsertOutbox | before | 1653 | 1.176648 | 0.311689 | 12.067684 |
| InsertOutbox | after | 1653 | 1.010849 | 0.248354 | 11.899827 |
| PageQuery | before | 6032 | 3.555041 | 0.458799 | 10.252244 |
| PageQuery | after | 6032 | 3.356617 | 0.424720 | 10.515603 |
| Commit | before | 1653 | 2.610953 | 0.189905 | 9.455573 |
| Commit | after | 1653 | 2.096902 | 0.106831 | 9.452304 |
| CloseSession | before | 6211 | 1.077089 | 0.258633 | 11.591998 |
| CloseSession | after | 6211 | 0.821985 | 0.276586 | 11.397751 |

BeginImmediate start→terminal has mean 15.514021 ms, p99 179.279885 ms and maximum 2,533.297775 ms before; mean 14.909052 ms, p99 229.417868 ms and maximum 2,431.669099 ms after. These largest values may belong to startup/seed or other nonmeasurement phases and are not identified as the original formal failure.

After BEGIN, InsertItem and InsertOutbox show a separate shared cost to investigate. In after, their native start→terminal means are about 0.249 ms, while take→retirement-observed means are 1.392 and 1.510 ms, with p99 about 11.9 ms. Before also has take→retirement-observed p99 about 11.8–12.1 ms. The current observation therefore identifies a cost present in both roles; it does not attribute the selected regression to that cost or determine which part is result taking, retirement polling, scheduling or continuation observation. ClaimQuery includes several native operations per public query and combines creates and replays, so its aggregate is not a per-transaction hold-time decomposition.

## Gate observations

Wait is wait_enter→acquired and hold is acquired→hold_end. Before owner-disposal/ticket-removal regions have no acquired timestamp, so their wait and hold values remain unavailable. AfterRelease hold includes both the native request release and managed coordinator/ticket removal.

| Role | Region | Records | Wait p99 ms | Wait maximum ms | Hold p99 ms | Hold maximum ms | Whole-region maximum ms |
| --- | --- | --- | --- | --- | --- | --- | --- |
| before | BaselineAdmissionRegistry | 6211 | 0.001012 | 0.224838 | 0.004407 | 4.647984 | 4.648084 |
| before | BaselineOwnerRelease | 6211 | N/A | N/A | N/A | N/A | 0.403557 |
| before | BaselineTicketRemove | 6211 | N/A | N/A | N/A | N/A | 0.670769 |
| after | AfterAdmission | 6211 | 0.000991 | 0.261244 | 0.004647 | 6.835210 | 6.835440 |
| after | AfterRelease | 6211 | 0.000400 | 0.041192 | 0.017567 | 0.740363 | 0.740423 |

The after admission wait maximum is 0.261244 ms; release wait maximum is 0.041192 ms. Release hold maximum is 0.740363 ms. Admission hold has a 6.835210 ms maximum, so not every hold is sub-millisecond. None of these observed gate regions accounts for hundreds of milliseconds in these traces. This conclusion is limited to the recorded diagnostic processes, not a proof about an unobserved formal run.

## Request-local correlation

Operations are joined by their actual captured frame ID and HostTicket ID; phases are grouped under the same actual request. Categories below are inferred from the recorded phase signature: InsertItem for create, ReplayQuery for replay, PageQuery for page, and RecoverQuery for recovery. The three HTTP calls of an external business cycle are not identity-linked in this recorder. Interval totals within each request use merged intervals to avoid double counting overlaps.

| Phase signature | Role | Requests | Request-scope p99 ms | Maximum ms | Slowest 1% count | Largest public phase in slowest 1% | Mean BEGIN pending fraction in slowest 1% |
| --- | --- | --- | --- | --- | --- | --- | --- |
| create_with_insert | before | 1653 | 541.727586 | 2618.883705 | 17 | {"BeginImmediate": 17} | 96.822830% |
| create_with_insert | after | 1653 | 649.450113 | 2466.933364 | 17 | {"BeginImmediate": 17} | 97.729722% |
| replay_with_query | before | 1525 | 133.651227 | 275.095347 | 16 | {"BeginImmediate": 16} | 89.679962% |
| replay_with_query | after | 1525 | 129.674430 | 833.018228 | 16 | {"BeginImmediate": 16} | 91.639260% |
| page | before | 1508 | 39.611071 | 67.562900 | 16 | {"PageQuery": 16} | 0.000000% |
| page | after | 1508 | 35.158184 | 58.982857 | 16 | {"CloseSession": 2, "PageQuery": 14} | 0.000000% |
| recovery | before | 1525 | 37.725615 | 47.992124 | 16 | {"RecoverQuery": 16} | 0.000000% |
| recovery | after | 1525 | 33.693540 | 40.727372 | 16 | {"CloseSession": 2, "RecoverQuery": 14} | 0.000000% |

The slowest 1% of create and replay scopes have BeginImmediate as their largest public phase in both runs. Their pending intervals dominate those particular lifecycle request scopes, while the gates are much smaller. This locates observed waiting; it does not explain why another writer held its transaction or establish physical SQLite lock/pool wait. Request scope includes dispatch, response and cleanup; admission is earlier. It is not client response latency. Phase disposal alone does not certify a successful public call.

## Narrow follow-up still pending

The exact requested write-transaction hold proxy is **BeginImmediate phase exit → Commit phase exit**, with each operation’s start→terminal, terminal→take and take→retirement-observed intervals clipped to that same per-create span and merged before summing. That proxy was not retained in this first aggregate. It cannot be recovered by adding aggregate percentiles; no such calculation is claimed. It also remains a managed public-call proxy, not a direct physical-lock observation.

A measurement-phase split likewise requires a demonstrated driver-phase/request-order or clock-window mapping. No raw trace is being reopened during the subsequent TLS timing. These two bounded follow-ups remain pending until timing is complete; no rerun or new load is proposed.

## Provenance and interpretation limits

The JSON contains the original two driver summaries, complete recorder bookkeeping, phase/gate distributions, per-category request distributions and a bounded ten slowest request breakdowns per category. Raw ticket IDs, operational paths, environment, addresses, native pointers and TLS material are excluded. Actual trace/summary/observer/source-index/load-plan/outer-execution hashes are preserved. Source headers and comments were read from the exact diagnostic commits above, including `SqliteTailDiagnostics.cs`, `DataSource.Start/Complete`, `NativeHost` and `NativeRequest`; original `AsyncOperation.cs` remains unchanged.

- [Derived numeric analysis](sqlite-tail-diagnostic-analysis-002.json)
- [Source and result identities](sqlite-tail-diagnostic-analysis-002.sources.json)

The failed formal C16 sample and the earlier startup failure remain in their original evidence locations. This report grants no new statistical, performance, long-run or overall acceptance.
