# TypedStream lazy join: matching public-package allocation comparison

This report compares the retained original-package baseline with the after candidate using identical external consumer source bytes, fixed 256-row input, 128-row batches and the same SDK support packages. It contains short allocation evidence only. The host was not dedicated; elapsed timestamps do not support a throughput, CPU, RSS or latency ranking.

All allocation totals are process-wide `GC.GetTotalAllocatedBytes(true)` deltas. Original start/end counters and GC counts remain in each raw JSON. No control is subtracted. Numeric `long` values are checked without reference DTO/string/list/result-array output in a measured interval. Positive total bytes are not assigned an estimated framework fraction.

The same probe source deliberately retains its original `measured-baseline` status text in after raw files. Package/source/executable identities and this comparison identify the phase; raw records have not been rewritten to change their labels.

Inputs: [before manifest](../korda-allocation/build-manifest.json), [after manifest](build-manifest.json).

## Complete queries

Each operation includes construction or prepared-stream creation, all 256 mapped rows, final false, enumerator disposal and dynamic-query disposal. The parameterless prepared plan exists before the interval. Session acquisition/return is outside these query measurements.

| Provider | Path | Before raw B / queries / rows | After raw B / queries / rows | Before B/query | After B/query | Change B/query | Change % |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| postgresql | dynamic_complete | 26711088 / 384 / 98304 | 18033528 / 384 / 98304 | 69560.125 | 46962.3125 | -22597.8125 | -32.486734% |
| postgresql | prepared_parameterless_complete | 21624144 / 384 / 98304 | 12923104 / 384 / 98304 | 56312.875 | 33653.91666666666666666666667 | -22658.95833333333333333333333 | -40.237616% |
| sqlite | dynamic_complete | 26712560 / 384 / 98304 | 18033648 / 384 / 98304 | 69563.95833333333333333333333 | 46962.625 | -22601.33333333333333333333333 | -32.490005% |
| sqlite | prepared_parameterless_complete | 21623952 / 384 / 98304 | 12933248 / 384 / 98304 | 56312.375 | 33680.33333333333333333333333 | -22632.04166666666666666666667 | -40.190174% |

The ratios above divide accumulated raw bytes by accumulated successful query counts; individual process totals and GC deltas are retained below and in `comparison.json`. These are allocation differences, not a noise estimate or a latency comparison.

## Individual full-query processes

| Phase | Provider / process | Path | Raw B | Queries | Rows | GC0 / GC1 / GC2 |
| --- | --- | --- | ---: | ---: | ---: | --- |
| before | [postgresql / 1](../korda-allocation/postgresql-run-1.json) | dynamic_complete | 8903792 | 128 | 32768 | 2 / 0 / 0 |
| before | [postgresql / 1](../korda-allocation/postgresql-run-1.json) | prepared_parameterless_complete | 7208048 | 128 | 32768 | 2 / 0 / 0 |
| before | [postgresql / 2](../korda-allocation/postgresql-run-2.json) | dynamic_complete | 8903976 | 128 | 32768 | 2 / 0 / 0 |
| before | [postgresql / 2](../korda-allocation/postgresql-run-2.json) | prepared_parameterless_complete | 7208048 | 128 | 32768 | 2 / 0 / 0 |
| before | [postgresql / 3](../korda-allocation/postgresql-run-3.json) | dynamic_complete | 8903320 | 128 | 32768 | 2 / 0 / 0 |
| before | [postgresql / 3](../korda-allocation/postgresql-run-3.json) | prepared_parameterless_complete | 7208048 | 128 | 32768 | 2 / 0 / 0 |
| before | [sqlite / 1](../korda-allocation/sqlite-run-1.json) | dynamic_complete | 8905064 | 128 | 32768 | 2 / 0 / 0 |
| before | [sqlite / 1](../korda-allocation/sqlite-run-1.json) | prepared_parameterless_complete | 7208048 | 128 | 32768 | 2 / 0 / 0 |
| before | [sqlite / 2](../korda-allocation/sqlite-run-2.json) | dynamic_complete | 8903792 | 128 | 32768 | 2 / 0 / 0 |
| before | [sqlite / 2](../korda-allocation/sqlite-run-2.json) | prepared_parameterless_complete | 7207856 | 128 | 32768 | 2 / 0 / 0 |
| before | [sqlite / 3](../korda-allocation/sqlite-run-3.json) | dynamic_complete | 8903704 | 128 | 32768 | 2 / 0 / 0 |
| before | [sqlite / 3](../korda-allocation/sqlite-run-3.json) | prepared_parameterless_complete | 7208048 | 128 | 32768 | 2 / 0 / 0 |
| after | [postgresql / 1](postgresql-run-1.json) | dynamic_complete | 6010104 | 128 | 32768 | 2 / 0 / 0 |
| after | [postgresql / 1](postgresql-run-1.json) | prepared_parameterless_complete | 4305976 | 128 | 32768 | 1 / 0 / 0 |
| after | [postgresql / 2](postgresql-run-2.json) | dynamic_complete | 6011712 | 128 | 32768 | 2 / 0 / 0 |
| after | [postgresql / 2](postgresql-run-2.json) | prepared_parameterless_complete | 4311152 | 128 | 32768 | 2 / 0 / 0 |
| after | [postgresql / 3](postgresql-run-3.json) | dynamic_complete | 6011712 | 128 | 32768 | 2 / 0 / 0 |
| after | [postgresql / 3](postgresql-run-3.json) | prepared_parameterless_complete | 4305976 | 128 | 32768 | 1 / 0 / 0 |
| after | [sqlite / 1](sqlite-run-1.json) | dynamic_complete | 6011216 | 128 | 32768 | 2 / 0 / 0 |
| after | [sqlite / 1](sqlite-run-1.json) | prepared_parameterless_complete | 4311152 | 128 | 32768 | 2 / 0 / 0 |
| after | [sqlite / 2](sqlite-run-2.json) | dynamic_complete | 6011216 | 128 | 32768 | 2 / 0 / 0 |
| after | [sqlite / 2](sqlite-run-2.json) | prepared_parameterless_complete | 4311032 | 128 | 32768 | 2 / 0 / 0 |
| after | [sqlite / 3](sqlite-run-3.json) | dynamic_complete | 6011216 | 128 | 32768 | 2 / 0 / 0 |
| after | [sqlite / 3](sqlite-run-3.json) | prepared_parameterless_complete | 4311064 | 128 | 32768 | 2 / 0 / 0 |

## Narrow windows and separate controls

Within-batch windows start after the first fetched/parsed row; each remaining 127 moves is required to be completed successfully and synchronous. Supplemental windows include one replenishment fetch and its first mapped row, so their measured row count is one. Final false and disposal remain mandatory outside these narrow intervals and are included in the complete-query measurements.

| Provider | Interval | Phase | Windows | Raw B sum | Min / max B per window | Rows | Incomplete / thread changes |
| --- | --- | --- | ---: | ---: | --- | ---: | --- |
| postgresql | within_first_batch | before | 384 | 4291584 | 11176 / 11176 | 48768 | 0 / 0 |
| postgresql | within_first_batch | after | 384 | 0 | 0 / 0 | 48768 | 0 / 0 |
| postgresql | supplemental_fetch_including_first_row | before | 384 | 4677856 | 12128 / 17304 | 384 | 384 / 202 |
| postgresql | supplemental_fetch_including_first_row | after | 384 | 4620288 | 12032 / 12032 | 384 | 384 / 174 |
| postgresql | empty_sync_control | before | 384 | 0 | 0 / 0 | 48768 | 0 / 0 |
| postgresql | empty_sync_control | after | 384 | 0 | 0 / 0 | 48768 | 0 / 0 |
| sqlite | within_first_batch | before | 384 | 4291584 | 11176 / 11176 | 48768 | 0 / 0 |
| sqlite | within_first_batch | after | 384 | 0 | 0 / 0 | 48768 | 0 / 0 |
| sqlite | supplemental_fetch_including_first_row | before | 384 | 4656504 | 11872 / 12248 | 384 | 381 / 206 |
| sqlite | supplemental_fetch_including_first_row | after | 384 | 4634824 | 11784 / 17208 | 384 | 380 / 211 |
| sqlite | empty_sync_control | before | 384 | 0 | 0 / 0 | 48768 | 0 / 0 |
| sqlite | empty_sync_control | after | 384 | 0 | 0 / 0 | 48768 | 0 / 0 |

An incomplete observation can race with awaiting; the distinct managed-thread-change count demonstrates actual suspension/resumption in those instances. Neither number permits claiming that all other moves were synchronous.

| Provider | Every after in-batch window has exactly zero raw B |
| --- | --- |
| postgresql | True |
| sqlite | True |

**Zero B inside a row window is not zero B for a query or a batch.** Where every exact raw process-wide window is zero, that specific warmed synchronous numeric path passes the zero-allocation gate. No attribution subtraction is required for a zero total. The positive complete-query and replenishment totals remain nonzero; their exact framework/runtime split remains unproved. Cancellation, exceptions, session acquisition/return and high-concurrency allocation are not accepted by this probe.

| Phase | Provider / process | Empty async raw B | Source-open idle raw B |
| --- | --- | ---: | ---: |
| before | postgresql / 1 | 0 | 0 |
| before | postgresql / 2 | 0 | 0 |
| before | postgresql / 3 | 0 | 0 |
| after | postgresql / 1 | 0 | 0 |
| after | postgresql / 2 | 0 | 0 |
| after | postgresql / 3 | 0 | 0 |
| before | sqlite / 1 | 0 | 0 |
| before | sqlite / 2 | 0 | 0 |
| before | sqlite / 3 | 0 | 0 |
| after | sqlite / 1 | 0 | 0 |
| after | sqlite / 2 | 0 | 0 |
| after | sqlite / 3 | 0 | 0 |

The async control uses `Task.Yield` and is not equivalent to a native operation. Every control is reported independently and none is subtracted. All six live native owner counters (sources, sessions, operations, cursors, buffers, handles) returned to zero after source close in every verified process. Cumulative SQL/protocol counters include setup and warmup and do not measure physical network round trips.

## Exact identities

| Phase | Provider | Package version / source commit | Package SHA-256 | Executable SHA-256 | Loaded native SHA-256 |
| --- | --- | --- | --- | --- | --- |
| before | postgresql | `0.1.0-preview.3` / `771bc77cbd68d3f932b99ed2497c0697bbba5f02` | `458c115e12d65ca0719f542ea262aeb3347f5bc3269f99d5ba14f3e36c038e0f` | `dd762d02adebe83cdd85e6911ce3951f41c8d8d1b930a7a7e50988e677bf001b` | `73f725104fb1bee5fc86a9bc371e556ea8358ac3a2d774c4823185e6da8984c6` |
| before | sqlite | `0.1.0-preview.3` / `771bc77cbd68d3f932b99ed2497c0697bbba5f02` | `584d46aa5b08b1e0af46a454ac9f41704c28fe502884017e856ad1b66ca53ef5` | `d5f3a27fe4b04fed2ba87f6d45b6d1c991158ccc5bce1f31d2d3e15d3518f229` | `970a8868290cec37c353bbd8e48bb7bf4ef18cfa1da9e495fc06d7eb08d71d40` |
| after | postgresql | `0.1.0-perf-lazy.1` / `28110ee03391831c737a54204730730a01b77a34` | `59eee79602c5f7d25487e840d1ac78198d3632456d8ae39c4fc72d8a463dcd38` | `135c3e6820597ef5e5ba3404d7a38d7e149b6b6e36ca42d16be1039856072e1c` | `73f725104fb1bee5fc86a9bc371e556ea8358ac3a2d774c4823185e6da8984c6` |
| after | sqlite | `0.1.0-perf-lazy.1` / `28110ee03391831c737a54204730730a01b77a34` | `80db70b602c38858b3afde9952ef27e4c2ef8db1ffcf8b8d5b7ce40274fee617` | `4422cca581fc155af9a71a2223b629f9a75246bbdffa99b6118e6367366d37e1` | `970a8868290cec37c353bbd8e48bb7bf4ef18cfa1da9e495fc06d7eb08d71d40` |

Both phases loaded byte-identical native libraries per provider. The changed managed package and AOT executable are bound to their recorded source identities and release receipts. This evidence uses candidate feeds; it does not establish a public NuGet publication or post-merge download.

Regenerate with `python3 benchmarks/Database/allocations/compare.py --before /absolute/before/evidence --after /absolute/after/evidence`. The command validates raw arithmetic, checksums, all per-window synchronous conditions, independent processes, owner retirement, exact consumer inputs, support packages and native binary equality before writing this comparison. It does not rerun either phase.
