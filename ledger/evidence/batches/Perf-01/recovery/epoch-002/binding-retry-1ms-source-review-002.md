# Perf-01 — database and Server retry parameter experiment

**Source-only disposition: no blocking defect found in the two-parameter change; suitable for controlled verification, not selected or performance-accepted.** This is an independent source assessment, not GitHub approval. The reviewer did not build or execute any product, fixture or workload.

The reviewed candidate is `a5748ad4e03825e3da7706d074887952da6c2d43`, parent `3ee5b3eead4b31e50051b324653286f558e71b08`, original base `ea0067114346af4f13383f24df165456bcabe344`. The tracked working tree was clean when read. The complete diff against the original base contains only these two constructor arguments:

| Constructor | Existing capacity | Selected existing interval |
| --- | --- | --- |
| Data `SourceResources` | `MaxQueryNodes + MaxConnections + MaxWaiters + 2` | 1 ms instead of the 10 ms default |
| Server `NativeHost` | `checked(MaxActiveRequests * 10 + 33)` | 1 ms instead of the 10 ms default |

Relative to the database-only parent, only the Server constructor changes. The shared `CallbackCoordinator`, `CoordinatedCallback`, `AsyncOperation`, native implementation, limits and lifetime logic remain unchanged. The previous extra-Signal experiment is not restored. The separate database-only candidate remains useful for attribution; it is not equivalent to this combined candidate.

## Actual affected Server paths

`NativeGrpcTransport.WriteCoreAsync` first awaits the native protocol-write reservation. `NativeRequest.ReserveProtocolWriteAsync` uses `ReserveAndJoinAsync`, whose finally block awaits the reservation operation's `Retirement`. The write then starts its own native operation and again awaits `Retirement` in finally, before clearing `_writing`. Thus there are two retirement joins on this serialized message-write path, without assuming that either operation actually needs a timer retry on a particular call.

The shared Server coordinator also serves gRPC reads, headers/status, request tickets, cancellation/control callbacks, ordinary HTTP I/O and host operations. This is not a gRPC-only setting. Read completion likewise observes retirement before clearing its direction flag. Existing transport/backpressure, result status, cancellation and ownership semantics are unchanged in the source.

`NativeHost.DisposeCoreAsync` still waits for its operations and tickets to become empty, callback entries to reach zero and native `TryRetire` to succeed before disposing the host owner. Its existing 5 ms close-observation delay is unchanged. Constructor failure and unstarted disposal still release the control slot and dispose the coordinator. No new lock acquisition order or native-memory access is introduced by the constructor arguments.

These observations show that retry cadence can affect the application-visible path. They do not establish that the earlier gRPC tail regression was caused by the timer, that the shorter interval will help, or that the buffer-only candidate's resource and latency results transfer to this candidate.

## Resource and idle risks

The [database-only review](database-retry-1ms-source-review-001.md) describes the unchanged full-array scan and timer overlap behavior. Those risks also apply to Server:

- Server's public default, also the protocol driver's source default, is 256 active request slots. The coordinator therefore has **2,593 slots**, including when actual concurrency is small. Its nominal scan work changes from 259,300 to 2,593,000 slot reads/locks per second at the requested periods.
- An open idle host retains its control slot and continues scanning the entire array. Actual callback frequency, CPU cost and timer precision must be observed; the arithmetic is not a measurement or bound on outstanding callbacks.
- For a reference application using that Server default and its existing two database source capacities, the combined nominal scan size is **10,875 slots per period**, or 1,087,500 versus 10,875,000 slot reads/locks per second. This is a conditional source-derived estimate, not a claim about every runtime configuration.
- Each context still coalesces accepted work through `_scheduled`. The complete Timer Retry scan has no overlap guard. At shorter periods, delayed or slow scans can overlap or queue, increasing coordinator-gate and ThreadPool contention. Per-context coalescing does not bound total timer-scan work.
- Server capacity grows with configured `MaxActiveRequests`. The reviewed managed validation requires it to be positive; the constructor retains checked arithmetic and array allocation. This review establishes no universal practical maximum or high-capacity CPU acceptance.

The underlying .NET Timer behavior is unchanged: repeated callbacks are not serialized by `TimerQueueTimer.Fire`, and synchronous `Dispose` is not a join of callbacks already running. Existing completion and owner protections are retained, but a shorter interval exercises them more frequently.

## Verification boundary

The original B18 supplied-native verification is an appropriate first assembled functional check, with the actual candidate managed artifacts, original precompiled native hashes and existing protocol checks. No test, status, trailer, deadline, cancellation or payload-credit assertion should be weakened to admit this candidate.

If the candidate advances, reuse the existing HTTP/1.1 and HTTP/2 immediate-close, response-finish, backpressure, cancellation and drain regressions, together with the affected Server protocol regressions. A Server constructor change also requires actual HTTP observation; gRPC success alone does not establish that Server-wide CPU or tail latency is acceptable. The database checks and original scalar comparisons remain applicable because the candidate includes the database interval change.

Selection requires the same frozen workloads and resource limits, independent interleaved process comparisons, actual arrival/error/drain observations, and open-idle/post-close CPU and ownership evidence. B18 correctness alone carries no timing, capacity or long-duration credit. No product selection or causal conclusion is made in this review.

Source paths, exact file hashes and the locked upstream Timer blob are recorded in the accompanying JSON. No third-party implementation was copied into the product.
