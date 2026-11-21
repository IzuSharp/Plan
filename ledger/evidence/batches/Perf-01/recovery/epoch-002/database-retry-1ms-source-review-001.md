# Perf-01 — database retirement retry experiment: source review

**Disposition: suitable for the proposed controlled experiment; no retention or performance acceptance.** This is a source-only peer assessment, not GitHub approval. No build, application, fixture or timed load was executed by the reviewer.

Reviewed local product commit: `3ee5b3eead4b31e50051b324653286f558e71b08`, parent `ea0067114346af4f13383f24df165456bcabe344`.

## Exact scope

The complete product diff changes only the `SourceResources` constructor in `src/Data.NativeHost/NativeHost.cs`:

```csharp
Coordinator = new(capacity, TimeSpan.FromMilliseconds(1));
```

It selects the existing optional interval instead of the coordinator's 10 ms default. The shared `CallbackCoordinator`, `CoordinatedCallback`, `AsyncOperation`, native libraries, capacities, cancellation and close policies are unchanged. The earlier extra-`Signal` experiment is not restored. This setting applies to every database source, including PostgreSQL and the reference application's SQLite consumer. Server coordinators keep their existing setting.

The [measured transaction-span supplement](sqlite-tail-hold-supplement-003.md) supplies a reason to test this setting: approximately 65–66% of the selected managed transaction proxy lies between BeforeTake and retirement observation. `AsyncOperation.Process` requests a coordinator retry when native `TryRetire` returns Pending. That source path can wait for the periodic scan. The measured interval also includes materialization and continuation scheduling; the trace cannot identify its timer-only portion.

## Resource and concurrency risks

`CallbackCoordinator.Retry` scans the complete slot array and acquires the coordinator gate once per slot, even when `Count == 0`. There is no per-tick array/list allocation, but an open idle data source continues periodic work. `DataSource` sizes the array as `MaxQueryNodes + MaxConnections + MaxWaiters + 2`.

| Configuration | Slots per source | Nominal slot reads/s at 10 ms | Nominal slot reads/s at 1 ms |
| --- | ---: | ---: | ---: |
| Default limits | 4,258 | 425,800 | 4,258,000 |
| Maximum accepted limits | 9,218 | 921,800 | 9,218,000 |
| TaskService main source | 4,178 | 417,800 | 4,178,000 |
| TaskService consumer source | 4,104 | 410,400 | 4,104,000 |
| TaskService two-source total | 8,282 | 828,200 | 8,282,000 |

These are arithmetic work estimates at the requested periods, not measured rates, CPU cost, guaranteed wake-up precision or a bound on outstanding timer callbacks.

Per-context callback work remains coalesced by `_scheduled` under `_scheduleGate`: repeated timer signals cannot create multiple accepted work items for that context. However, there is **no coordinator-wide gate preventing concurrent full-array Retry scans**. The locked .NET Timer implementation increments its running-callback count and calls the callback without serializing repeated executions. If scans or scheduler delays exceed the shorter period, timer callbacks can overlap or accumulate. Context coalescing does not make total timer work globally bounded.

The slot array, native-owner limits and operation budgets do not grow. A timer scan drops the coordinator gate before invoking a context, so this parameter change introduces no new lock ordering in the source. `CompleteScheduling` prevents a stale context reference from rescheduling a completed operation. Normal `Timer.Dispose` does not join callbacks already in progress; the existing close/retirement protocol remains responsible for owner safety. The shorter period can increase contention and exercise those existing race windows more often. This review therefore does not certify close behavior at the new cadence.

## Applicable validation

The controller's six interleaved scalar profiles are an appropriate first test when they retain the original workload, actual assets, observations and noise rules. They should be followed by the existing real PostgreSQL and SQLite application checks, including typed paging, persisted create/replay/outbox results, BUSY/retry accounting, cancellation, close and post-drain observations. Preserve the existing capacities and limits while comparing CPU, RSS, allocation, achieved arrivals and idle cost. A latency benefit accompanied by unacceptable idle CPU or timer/thread-pool pressure would not justify retention.

Existing targeted lifecycle coverage is available without creating another framework:

- `tests/Interop.Async/Program.cs`: `BindingFailureAndRejectedScheduling` already constructs a 1 ms coordinator and checks rejection/throw recovery and a maximum single queued work item. `ResultBeforeNativeQuiet`, cancellation-registration drain, failed setup, discarded-task cleanup and `LostWakeRegression` cover the unchanged shared invariants. Existing shared-source evidence is useful context, not proof that the real database domain at this setting has passed.
- `tests/Interop.Callbacks/Program.cs`: `BoundedQueueAndRetry`, `NativeSourceAndControlDrain`, capacity rejection and concurrent stop/GC/cookie reuse cover the coordinator's existing lifecycle boundary. These tests do not establish a bound on full timer-scan overlap.
- `tests/Data.NativeHost/Program.cs`: both provider paths check accepted cancellation, pool capacity, result/materialization failures, cursor ownership, source/session close, orphan retirement and engine counters returning to zero. This suite runs through the changed database constructor and is the relevant assembled ownership regression.
- Existing `tests/Data.Transactions/verify.py` and `tests/Data.Streaming/verify.py`, together with the actual application's migration/transaction/stream use, provide the affected commit/cancel and cursor/backpressure checks. Reuse their current recipes and precompiled native assets; do not substitute fabricated success markers or a new benchmark.

Before retaining the setting, the controller should also observe an open but idle source at the actual application capacities and the shutdown transition. If larger-capacity configurations are claimed as supported by this optimization, their scan cost and saturation must be assessed as well. No maximum-capacity or timer-overlap measurement was performed in this review.

## Sources

Product paths reviewed at the exact experimental commit are `src/Data.NativeHost/NativeHost.cs`, `src/Data.NativeHost/DataSource.cs`, `src/Data.NativeHost/DatabaseOptions.cs`, `src/Interop.Callbacks/CallbackCoordinator.cs`, `src/Interop.Async/AsyncOperation.cs`, `src/Reference.TaskService/ServiceConfiguration.cs` and the existing regression entry points above. File hashes are recorded in the accompanying JSON.

The timer concurrency observation is supported by the locked [.NET Timer source](https://github.com/dotnet/dotnet/blob/297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f/src/runtime/src/libraries/System.Private.CoreLib/src/System/Threading/Timer.cs), `TimerQueueTimer.Fire`; Git blob `19d152d6153bd465454787248fc3acff81efef3b`. No third-party implementation was copied into NativeWeave.
