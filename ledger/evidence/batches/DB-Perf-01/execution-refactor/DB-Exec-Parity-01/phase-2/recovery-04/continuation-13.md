# Continuation13 — frame08 saves allocation but fails adoption

**Reject bounded final-frame rental08 as the current common two-provider product
change. Retain integrated05 plus the independent owner cleanup.** The twelve
predefined ordinary short processes completed successfully. The intended resource
saving repeated, but acceptable CPU/tail behavior did not. No optional mixed,
additional round, pressure or long run is selected for08.

The owner's direct question has a clear answer: **substantial optimization space
remains, but the measured gap is not a guarantee that all of it is recoverable.**
The latest related32 results below bind the current cleanup tree; the older
text1000 comparison in [Continuation10](continuation-10.md) remains bound to the
original05 artifacts. Do not combine their rounds or relabel either identity.

## Decision and actual measurement boundary

The independent actual audit completed 2,470 checks with 836 unique input identities.
All12 business processes returned successfully:24,576 measured businesses and
1,302,528 result rows, with the original53-row digest in every case. Both initializers,
all business children and the PostgreSQL owner have positive completion records.
Task peers stopped builds, profiling, compression and local work during the window.
External host tenancy and kernel scheduling were not proved exclusive.

Each provider ran ownership05, frame08 and Dapper, then the reverse order:
C1, persistent session, batch32,2,048 measured businesses and128 case warmups per
process. The existing mixed35 correctness preflight was additional and outside
those warmups and measurement boundaries. SQLite then PostgreSQL ran serially.
The complete controller window was2026-11-27 13:11:20–13:14:11 UTC, including
preparation, warmup, per-process five-second released-idle observations and retirement.
No arrival queue or offered-load saturation was exercised; successful closed-loop
operations are not a refusal-threshold or sustained-throughput result.

Both Korda variants contain the same owner cleanup and load the same native04
provider image. The retained build source is69b2383dadc280f1a81de592592a1442069eed0c,
package0.1.0-parity05.2, treef7660759bba43ae83324620e2fb731efd479c3b5;
its tree is identical to published Korda106fe68b6f6c2537f478daf65a71ab97cc4b15ff.
Ordinary frame08 is13b25de2b67d858d8b6524f615e3a84b4c541817,
package0.1.0-parity08.1, tree1547f40409892f8e4b89f4ddf99a637664991203.
The synthetic diagnostic sourcec429effc45c6fcd946c999553d0420b71369abfe is separate
and was never used for ordinary timing. Actual PackageReference AOT outputs,
65 generated C# files per new consumer, ELF/DBG, native and package bindings passed.

## All ordinary absolute values

CPU and managed allocation below are the measured steady **client process** costs,
including framework, driver, DTO and harness contributions. No exclusive framework
allocation is inferred. Latencies are histogram upper bounds in milliseconds.
Native allocation profiles are unavailable in these ordinary runs.

| Provider | Round | Route | Success/s, closed loop | CPU µs/business | Managed B/business | p50 ms | p95 ms | p99 ms |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| sqlite | 1 | ownership05 | 243.774 | 4483.250 | 516145.859 | 3.211 | 8.782 | 11.338 |
| sqlite | 1 | frame08 | 201.603 | 5505.271 | 455377.809 | 3.768 | 10.093 | 14.680 |
| sqlite | 1 | Dapper.AOT | 1010.141 | 982.877 | 74098.188 | 0.934 | 1.335 | 1.679 |
| sqlite | 2 | Dapper.AOT | 711.639 | 1404.860 | 74098.172 | 0.991 | 3.326 | 4.981 |
| sqlite | 2 | frame08 | 247.916 | 4481.099 | 455357.445 | 3.211 | 8.454 | 11.272 |
| sqlite | 2 | ownership05 | 237.600 | 4523.294 | 516179.207 | 3.277 | 8.847 | 11.600 |
| postgresql | 1 | ownership05 | 173.554 | 4021.659 | 516146.953 | 5.014 | 10.093 | 13.566 |
| postgresql | 1 | frame08 | 178.885 | 4055.282 | 455360.746 | 4.817 | 9.896 | 12.845 |
| postgresql | 1 | Dapper.AOT | 481.334 | 528.494 | 51224.242 | 1.565 | 4.260 | 5.571 |
| postgresql | 2 | Dapper.AOT | 597.638 | 444.885 | 51224.242 | 1.376 | 3.375 | 4.653 |
| postgresql | 2 | frame08 | 189.983 | 3636.083 | 455373.566 | 4.489 | 9.241 | 12.583 |
| postgresql | 2 | ownership05 | 170.556 | 4470.196 | 516170.172 | 5.079 | 10.420 | 13.369 |

## Resource saving and the rejected tradeoff

| Provider / round | Managed B saved/business | Managed change | CPU change | p99 change | Released-idle RSS change, B |
| --- | ---: | ---: | ---: | ---: | ---: |
| sqlite / 1 | 60768.051 | -11.773% | +22.796% | +29.480% | +45,056 |
| sqlite / 2 | 60821.762 | -11.783% | -0.933% | -2.825% | +143,360 |
| postgresql / 1 | 60786.207 | -11.777% | +0.836% | -5.314% | +667,648 |
| postgresql / 2 | 60796.605 | -11.778% | -18.659% | -5.882% | +548,864 |

All four pairs reduce ordinary managed allocation by about60.77–60.82 KB/business,
11.77–11.78%. This is consistent with eliminating the observed final-array target,
but the whole-process saving is264–318 B larger than the earlier60,504 B scoped
array. That residual is unassigned; do not label every saved byte an exact exclusive
array measurement. Source-tape copying and command fixups remain.

SQLite round1 shows a material CPU/p99 regression while round2 is near neutral.
PG p99 improves in both pairs, but CPU improvement does not repeat. Two reversed
rounds do not supply confidence intervals or an upper regression bound. Dapper's
own SQLite CPU rises between rounds; raw host observations also retain external
variation. These facts prevent assigning the bad interval exclusively to a pool
lock or clear. They do not justify discarding it, averaging it away, or adding
rounds until a favorable result appears.

The predeclared [selection rule](frame-pool-08-hypothesis.md) requires repeated net
resource benefit with acceptable CPU/tail/memory cost. That combined condition is
not established for the common dual-provider change. Reject08, keep its successful
mechanism/correctness evidence, and close its conditional mixed/extra measurements.
No provider-specific product split or runtime setting is selected.

The process lifetime peak RSS decreased in all four pairs; five-second released-idle
RSS increased in all four. These are different observations. The idle sample is
after workload/session/source drain with no forced GC; it is neither the lowest
reclaimable RSS nor a measurement of only the private pool. GC counts and pause
values below retain their process scope.

| Provider | Round | Route | Lifetime peak RSS B | Released-idle RSS B | Gen0 / Gen1 / Gen2 | GC pause ms |
| --- | ---: | --- | ---: | ---: | --- | ---: |
| sqlite | 1 | ownership05 | 33,275,904 | 31,850,496 | 416 / 76 / 1 | 340.289 |
| sqlite | 1 | frame08 | 32,202,752 | 31,895,552 | 311 / 95 / 1 | 328.468 |
| sqlite | 1 | Dapper.AOT | 23,117,824 | 21,557,248 | 72 / 0 / 0 | 29.472 |
| sqlite | 2 | Dapper.AOT | 23,273,472 | 21,790,720 | 72 / 0 / 0 | 23.234 |
| sqlite | 2 | frame08 | 32,276,480 | 31,899,648 | 303 / 89 / 1 | 273.795 |
| sqlite | 2 | ownership05 | 33,398,784 | 31,756,288 | 429 / 73 / 1 | 360.735 |
| postgresql | 1 | ownership05 | 31,641,600 | 29,741,056 | 415 / 82 / 1 | 354.383 |
| postgresql | 1 | frame08 | 31,084,544 | 30,408,704 | 304 / 95 / 0 | 277.549 |
| postgresql | 1 | Dapper.AOT | 31,072,256 | 27,557,888 | 49 / 0 / 0 | 30.615 |
| postgresql | 2 | Dapper.AOT | 30,949,376 | 27,598,848 | 49 / 0 / 0 | 31.511 |
| postgresql | 2 | frame08 | 31,010,816 | 30,187,520 | 309 / 96 / 1 | 269.305 |
| postgresql | 2 | ownership05 | 31,715,328 | 29,638,656 | 425 / 67 / 1 | 374.163 |

## PostgreSQL server costs are separate

The existing visible-process-tree observer supplies the following inner/outer
acquisition-interval CPU sums in seconds. They are non-atomic endpoint
observations, not exact steady CPU or strict mathematical bounds; no cgroup
accounting or extrapolation is claimed. They are not added to client CPU.

| Round | Route | Inner observed CPU s | Outer observed CPU s |
| ---: | --- | ---: | ---: |
| 1 | ownership05 | 3.65 | 3.78 |
| 1 | frame08 | 3.65 | 3.83 |
| 1 | Dapper.AOT | 2.78 | 3.07 |
| 2 | Dapper.AOT | 2.28 | 2.53 |
| 2 | frame08 | 3.55 | 3.71 |
| 2 | ownership05 | 3.41 | 3.59 |

The postmaster owner's complete wait4 lifetime reports22.538294 CPU seconds,
including setup, all six processes and shutdown. It is a separate accounting
scope and must not be added to the intervals above. The actual owner exited0.

## Correctness and mechanism results completed before timing

- Ordinary Binding AOT at e1f18255 completed557 assertions. Its68 Compile,108 Render
  and12 CTE counts belong to the real C++ ABI fixture, not database SQL executions.
- First Relations attempt failed compilation withCS8600/CS8604 and never produced
  an executable or ran a database. The13b fix explicitly types Distinct<byte[]>;
  it changes no product code or lifetime behavior. The second real SQLite/PG run
  passed1,244 assertions and133 managed retirements, including poisoned/re-rented
  frame storage followed by correct old-plan execution. Final selected native
  owners were zero. PostgreSQL retirement here uses successful pg_ctl stop and
  server log, not a claimed direct postmaster wait4.
- Separate local03 AOT ran two fresh processes. Ten faults at the actual Encode,
  metadata and origin sites passed102 assertions. Post-rent Encode faults made
  zero native submissions; the other eight followed native OK/nonzero results,
  each with one target release/forward and zero duplicates after final GC drain.
  This does not reproduce the old unsafe address-reuse bug or force real OOM.
- Resource diagnostics passed99 assertions and retained11 events. The60480-byte
  logical frame rented65536 physical bytes. Cold Rent allocated67,000 B, including
  nested pool construction1,400 B;40 B before construction remains unattributed.
  Three serial warm Rent/Return boundaries allocated0 B. Holding four slots forced
  a distinct-array miss of65,560 B. Return boundaries allocated0 B and all five
  complete65536-byte arrays read back zero. The327,680-byte clearing range follows
  actual lengths and locked implementation, not sampled hardware stores.

The resource recorder retains references and scans returned arrays in a serial
fixture. It does not establish zero whole-query/framework allocation, cold related
business cost, CPU, latency, RSS or database throughput. Actual ordinary ELF/DBG
readback separately confirms the4097–65536 branch, logical native length, rental
handoff before writes, null guards before pool access and true clearing arguments.
Indirect runtime virtual-slot targets were not dynamically inspected; no cycles
are inferred from instruction counts.

## Remaining space and the next decision boundary

Current ownership05 related32 client CPU is3.22–4.56 times Dapper for SQLite and
7.61–10.05 times forPG in these pairs. Managed allocation is about6.97 and10.08 times
Dapper respectively. Even the rejected pool candidate still allocates about6.15
and8.89 times Dapper. These gaps remain substantial after the already retained
private transfer and capacity changes.

The older original05 text1000 CPU gap is5.55/7.10 times Dapper in SQLite and
7.94/9.42 inPG, despite only about1% managed-allocation difference. Reducing the
related-query final array therefore cannot explain or close that execution gap.
RhSpinWait caller sampling and historical runtime-spin sensitivity are already
recorded, but neither sample shares nor these new timings yield exact exclusive
stage CPU. Scheduling/wait behavior, repeated execution work and remaining relation
construction still require a new bounded causal explanation before another code
change. Failed common completion, PG hook, lease, ready-row, tail06 and local07
experiments remain closed; their counter reductions did not automatically earn
endpoint gains. No new hypothesis is selected by this report.

This closes08, not the claim that database parity has been achieved. Only its
repeatable allocation result is accepted as a resource observation. Whole-framework
steady0 B, sustained capacity, full query parity and exclusive native/driver/DTO
allocation attribution remain unproved where not directly observed. The user's
short-only instruction remains binding; no long measurement or matched-before
long supplement is pending.

## Delivery and recovery

Current Korda PR40 remains106fe68b6f6c2537f478daf65a71ab97cc4b15ff: five retained05
changes plus the independent metadata-before-owner-adoption fix. The final finite
independent integration review passed12 checks without an identified contract or
evidence blocker for normal merging; it explicitly retains the earlier mixed
PG queued-p99 increases of26.238% /17.593%, released-idle RSS risks, producer CPU
accounting and remaining parity gaps. The08 product,
ordinary tests and diagnostic hooks are absent. Existing Korda CI45995931048
completed successfully for this head. Plan12 CI45997027741 and Design12
CIs45997113465/45997113479 also succeeded for their exact heads. Their success is
not a claim that this future evidence commit or a future merge/release has passed.

The committed module plan retains independent PostgreSQL and SQLite top-level
package checks alongside shared correctness/security/API work. No CI benchmark,
profiling, calibration or pressure invocation was added. Go drafts Plan35/Korda39
remain outside this task's mutations. Final normal merge/main CI/release/public
NuGet AOT outcomes must be recorded from actual results, not predicted.

The [readable result and receipt index](frame-pool08-results-13/source-records.json)
preserves original bytes and exact local provenance. Archive06 preparation is
separate; its full source/generated/ELF/raw payload is not remotely durable until
an actual publication and byte-readback receipt is appended. Archive01–05 remain
existing dependencies, not new test credit. Skip completed normal, local03,
ordinary08 and earlier rejected tests after an interruption. Never turn an
archive build or document gate into a performance execution.
