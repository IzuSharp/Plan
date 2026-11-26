# Independent close-quiet source review — experiment not selected

The selected product remains
[`17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa`](https://github.com/IzuSharp/Korda/commit/17da07e391ba867bbf195baa2e9fdc0bdc0cc0aa).
This review covers the isolated close-quiet experiment's final source
`d18d5654a7a69bce3a379c6fa8621b9d1d4b2767` and its integration identity
`92b923075952bac347619ee7817c372ee6e415cb`. A read-only Git diff confirmed that
their four experiment files are identical: `host.hpp`, `host.cpp`,
`streaming_tests.cpp` and `cursor-pull-v1.md`. The reviewer did not build, execute
tests, run a workload or rehash the author's archive for this review.

## Final ordering and safety disposition

The final ordering fixes the author's self-review finding in initial source
`4bfdbf781ce1ad74b2c3c58b41c68124c9243713`. While holding the pull mutex, the code
constructs the original CloseWorker and action, then evaluates the entire
released-resource predicate **before** publishing `close_` and `closing_`.
Those final assignments are nonthrowing and still precede mutex release. Thus
a potentially throwing nested mutex acquisition cannot leave an accepted
final-close obligation without a dispatched/settling worker. The pull mutex
excludes a new fetch throughout proof and acceptance.

The predicate requires a cursor, no running fetch, no outstanding result,
retained gate, buffer, error, cancellation object or live batch, a quiet fetch
completion fence, and `Cursor::resources_released()`. That method reads cursor
completion under its mutex and requires completion.done, retired and no
unconfirmed cleanup. Checking retired alone would be insufficient: cleanup can
have set retired while its worker still owns the cursor, before independently
publishing completion.

The branch invokes the existing CloseWorker::run after unlocking. It retains
Source control reservation/admission, both detached notification tickets,
join_resources, receipt encoding and original rich-error handling. Only the
control-queue submission is skipped. Source admission_stop still rejects before
acceptance. Callback publication still releases worker accessors/reservation
before notification and completes the tickets after callback return. The
unchanged managed close controller already guards callback readiness before
request/setup return. No mapper/prefetch/limit/protocol behavior is changed.

No source-level correctness blocker was found in the final ordering. This is
not a performance recommendation. Natural EOF closes the provider statement;
it does not itself publish cursor cleanup completion. Consequently only an
already fully retired subset of final closes can take the experimental branch.

## Read test coverage; execution evidence remains separate

The final test diff makes the important distinctions observable:

- An already joined cursor notifies exactly once on the requesting thread before
  close_request returns, with zero control submissions and a one-shot receipt.
- The old-fetch-tail case first proves actual cursor cleanup complete, then
  holds the old independent fetch ticket and requires one queued close.
- A retired=true cursor whose cleanup completion is held unpublished still
  queues and remains pending.
- An outstanding original rich error on a released cursor retains the queue,
  preserves independent fetch/close errors and exercises queue failure.
- Both queued and truly inline held final callbacks keep public snapshots,
  generic join and Source join pending until their detached notification tails
  finish.
- An already released fixture still rejects final-close admission after Source
  admission_stop without a late ticket or notification.

The author's archived validation distinguishes initial `4bfdbf7` streaming 394,
transaction 120 and real PostgreSQL protocol 432 checks from final `d18d565`
streaming 394. The review does not relabel the earlier transaction/protocol runs
as executions of the later source. Exact package validation and archive identity
remain the separate records produced by their executors.

## Selection result

Root reports that the prespecified ordinary paired-performance rule rejected
`92b9230`: PostgreSQL one-row single-route close changed from 34.972 to
50.580 microseconds without stable improvement, and SQLite 1000-row pool total
changed from 1755.582 to 1874.589 microseconds (+6.78%). These values are quoted
from the task's selection report; this source review did not recompute timing.

The experiment remains **not selected**. Its successful correctness evidence
and source review are retained as experiment evidence, not as a change to the
formal `17da07e` entry point or new `17da07e` execution credit. No further
optimization retry is implied by this review.

Source: [final provider/Host implementation](https://github.com/IzuSharp/Korda/blob/92b923075952bac347619ee7817c372ee6e415cb/native/cpp/src/host.cpp),
[streaming assertions](https://github.com/IzuSharp/Korda/blob/92b923075952bac347619ee7817c372ee6e415cb/native/cpp/tests/streaming_tests.cpp),
and [final-close contract](https://github.com/IzuSharp/Korda/blob/92b923075952bac347619ee7817c372ee6e415cb/native/database/binding/cursor-pull-v1.md).
