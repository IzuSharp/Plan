# SQLite C16: first formal attempt failed its tail-latency standard

This is an actual failed service-standard sample, preserved without changing the frozen acceptance rule. It is not a completed three-process comparison and grants no performance or long-run acceptance.

The unchanged caller ran at 50 arrivals/s, concurrency 16, 60 seconds, alternating cycle/page requests, using the fixed EA5 baseline, selected 2f final candidate and common 2e driver. The before process met the original service standard. The first after process was measurement-valid but exceeded the frozen 500 ms whole-load p99 limit.

| Actual first process | Before | After |
| --- | ---: | ---: |
| Offered / dispatched / successful | 3,001 / 3,001 / 3,001 | 3,001 / 3,001 / 3,001 |
| Successful calls/s | 49.99706825005386 | 49.830840266080095 |
| p50 ms | 20.322757 | 22.429474 |
| p95 ms | 99.533378 | 132.659480 |
| p99 ms | 232.540914 | 567.131236 |
| Measured provider BUSY / LOCKED exceptions | 0 / 0 | 0 / 0 |
| Explicit business retry attempts | 0 | 0 |
| Independent durable oracle | passed | passed |
| Consumer / database resource release | passed / passed | passed / passed |
| Server state after close | Disposed | Disposed |
| Original measurement-valid flag | true | true |
| Original service-standard flag | true | false |

The oracle reports 1,637 operations/items/outbox entries for each complete fixture. That total is not the 1,501 cycle successes in the measurement window. A zero provider exception count does not measure SQLite's internal busy-handler retry count.

The outer execution started at `2026-11-21T07:13:08.568476+00:00` and ended at `2026-11-21T07:15:47.680431+00:00`. Its SHA-256 is `66e8d576bfc4a339907ff0073a714468d6fec7baa76dbc78885b687a28209fcb`. Both finite child commands actually exited zero and retired; the outer caller then rejected the after result under its original comparison validity/service criteria. Direct/managed processes and later repetitions were not run in this attempt.

The unchanged serial dispatcher stopped with seven of sixteen comparison scenes completed. The failure and all actual outputs remain intact. No generator-invalid flag or correctness failure is recorded; one process per role cannot establish a statistically significant regression or its cause. Root is inspecting the actual sample and relevant source before deciding whether a separate diagnostic or fresh, explicitly identified attempt is justified. No threshold, arrival rate, product identity or acceptance label has been changed.

[Exact numeric checkpoint](comparison-sqlite-c16-failed-001.json) preserves original flags, counts, oracle/release results and existing source receipt identities. Capacity and all ten 30-minute intervals remain outstanding.
