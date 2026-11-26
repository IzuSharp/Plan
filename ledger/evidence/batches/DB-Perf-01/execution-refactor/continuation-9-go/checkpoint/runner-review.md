# Go load-generator source review

Reviewed the new `harness/main.go`, `runner.go`, `metrics_linux.go`, and `spin_amd64.s` against the actual frozen `OfferedLoad.cs` and `Measurement.cs` copied into the matched Dapper consumer. The frozen scheduler file hashes to `2adb14584476da8b8a49bb2e5db6bd85b136f3823aee5e2f004bc263eb2bc92b`; the producer-tree copy has the same hash.

This was a source review. The review agent did not compile a consumer, run a benchmark, start a database, or execute the newly added tests. Root coordinates the unified build and correctness checks.

## Conclusion

No blocking success-path scheduling or measurement defect remains in the reviewed source after the fixes below. The Go runtime's scheduler, database/sql implementation, cgo, allocation/GC model, and row iteration differ naturally from the C# implementations; the receipt labels those boundaries rather than equating unobserved protocol counters or .NET generations.

## Findings and resolution

1. The initial `fileHash` used `os.ReadFile` on the complete executable and SQLite shared library before warmup. This introduced an unnecessary large Go-heap allocation and could inflate lifetime peak RSS and alter the initial heap/GC state. Root changed it to `os.Open`, `sha256.New`, and streaming `io.Copy`; the revised source was read back.
2. A snapshot reconciliation error originally returned `nil, err`, causing `main` to discard the raw counter/histogram evidence and emit only a fatal message. Root now preserves the returned receipt and sampled metrics, records the error, closes resources, and marks comparison eligibility false. The revised source was read back.
3. SQL call counts originally had a broader label than their successful-operation accumulation. Root now explicitly labels them as business SQL/control calls in successful operations only; partial SQL of failed operations, driver-internal messages, and network round trips are excluded.
4. The initial zero-connection claim inferred success solely from `Close` returning no error. The worker now records `db.Stats().OpenConnections` after close and returns an oracle failure if nonzero. Therefore the main success flag is backed by an observed count. The revised worker source was read back.

## Confirmed invariants

- Planned arrivals are `ceil(seconds * rate)` and include every scheduled arrival even when the producer is late.
- The global arrival index is delivered unchanged to each worker, and both dispatch case accounting and `Worker.Execute` select the case from that global index. Rejections still consume their scheduled indices.
- The producer uses a locked OS-thread goroutine, sleeps one millisecond only with more than two milliseconds remaining, otherwise executes the bounded x86 PAUSE loop, and performs nonblocking queue admission. Queue capacity is preallocated; a full queue produces an explicit rejection without retry or capacity wait.
- Workers drain accepted jobs before the measurement ends. Throughput divides successful completions by the actual drained duration, not merely the requested offered duration.
- Successful service and successful scheduled-response histograms contain successes only. The all-completed histogram also contains failed operations; the start-delay histogram contains all started operations. Rejections have no fabricated latency sample.
- Histogram arithmetic and selected-bin upper-bound quantiles match the frozen convention. Hand-known examples are 1,000 ns → upper bound 1.004 microseconds, 2,000 ns → 2.008 microseconds, and 1,000,000 ns → 1,003.52 microseconds.
- Whole-process Go heap allocation and GC counters span the steady operations and producer/consumer activity. Prepared scheduler storage is outside the boundary; snapshot aggregation, resource disposal, and the idle sample are after the boundary. No forced GC is introduced.
- Process CPU includes all client threads, the arrival producer, and GC. PostgreSQL server CPU remains an external observer metric. `runtime.NumCgoCall` is explicitly distinct from Korda's command FFI or wire-protocol submissions.
- The result-file path must be fresh. Fatal measurement errors preserve their raw receipt. Explicit worker close errors remain in the result. Idle memory observations occur after worker, statement, connection, and pool close.

## Added unit tests

`harness/runner_test.go` contains four narrow correctness tests: hand-known histogram bins and upper quantiles; clamping nonpositive durations and empty histograms; aggregation of two independently specified worker results including failure evidence and digests; and refusal of four different counter inconsistencies while retaining the diagnostic receipt. These tests perform no database operations and do not measure elapsed performance. The review agent only formatted the source; root runs the tests together with the complete harness.

## Disk and temporary-build recommendation

The new module ZIP cache totals only 13,410,907 bytes; its complete download metadata directory is 13,695,648 bytes. Deleting it would recover little space and weaken offline module re-verification. The initial Go build cache was effectively empty. Keep the compiler's `go/src` and `go/pkg/tool`, which are needed for a source-package build.

At the review, `/workspace` was an ext4 filesystem with about 814 MB available, while `/tmp` was a separate tmpfs with about 3.83 GB available. Deleting old `/tmp` archives therefore cannot free `/workspace` ext4 space. If the unified build needs more temporary headroom, a dedicated task `GOTMPDIR` under `/tmp` can use the separate capacity, with `go build -p=1` reducing concurrent temporary-file peaks. Any such task tmpfs build directory must be removed before formal timing to avoid retaining build artifacts in memory. The review agent did not relocate or delete any cache.
