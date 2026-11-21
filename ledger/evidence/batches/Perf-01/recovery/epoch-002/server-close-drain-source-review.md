# Server close versus response completion: independent source review

**ACCEPT exact product candidate `e2610a2b4eaab63cc83be95be445109e15644d4e` for diagnostic and regression execution.**
This is source acceptance, not a successful test, performance result or release approval.
The reviewer ran no restore, build, target-code import, native load, test or profile.

| Identity | Value |
| --- | --- |
| Reviewed selected product base | `ccff42c0df4141984ef9de497af7cd768753704a` |
| First close-drain candidate | `57308b8ad875d3ec38f0655e76d1a5d2b4edd3ee` |
| Accepted amended candidate | `e2610a2b4eaab63cc83be95be445109e15644d4e` |
| Accepted Git tree | `ec0aa6a54eea6f1fd30a9e7ebc3ca48614fca74f` |
| Changed product files | `native/server/host/src/engine.rs`; `tests/Server.Diagnostics/Program.cs` |
| Source review completed | 2026-11-21 03:44:40 UTC |

## Problem and evidence boundary

The original B20 sample performs sixteen real HTTP requests, then immediately
closes the application. A complete declared-length response can reach the
client before the managed producer submits its separate native Finish
operation. Before this change, `Host.run` joined acceptors and their connections,
called `reap` once and returned; `Host.start` then dropped the Tokio runtime.
That ordering did not wait for an admitted managed dispatch to retire.
The same teardown ordering exists in the EA5 baseline
`ea5fa528035d025bd7a28698ee7c71194432236c`; this review does not attribute its
introduction to the selected ccff product.

The reviewer read the actual diagnostic `sample-08/stdout.log` under
`perf01-recovery/epoch-002/b20-diagnostic-002/commands/`. It records two
activities, 44 measurements, five warnings, and an unexpected native
invalid-state exception propagated from the awaited Finish at
`src/Server.Application/Response.cs:178`. Four intentional failure warnings
and the fifth successful-status hello-route warning remain distinct. This
managed stack alone does not uniquely identify the native failure branch.
Other Finish status-4 branches were inspected: request business state,
response phase, raw-protocol eligibility, closed body channel and typed
operation-result transfer. The exact-length/no-trailers channel-close fallback
already accounts for ordinary Hyper body completion. No diagnostic count,
framing rule or original failure record is weakened by this candidate.

## Independent finding and correction

Candidate `57308b8` waited only for every retained request's `retired` flag.
The reviewer requested a narrow correction: this flag does not always imply
zero native cleanup work. In `native/protocols/grpc/host.rs`, the undispatched
reset path in `PendingResponse::drop` can publish retirement, then call
`discard_input`. The gRPC discard path increments request-local `live_ops` and
spawns `call.retire_input()` with an `InputDiscard` guard. Late body cleanup
can also retain that guard after request retirement.

Amendment `e2610a2` changes the predicate to require **both request retirement
and request-local `live_ops == 0`**, using Acquire loads, and clarifies the
comment. It makes no other product change. The existing
`grpc_reaper_waits_for_input_cleanup_before_releasing_metadata` regression in
`native/protocols/grpc/host_tests.rs` retains the real `InputDiscard` guard;
its source was read, but it was not executed by this reviewer.

## Lifetime and concurrency assessment

After joining acceptors, the new loop reaps completed requests, checks the
request-local predicate, and yields through a one-millisecond Tokio sleep
while work remains. Neither the request registry guard nor any other lock
is held across that await. There is no new callback, public API, ABI entry,
host counter, dependency or third-party code. The loop runs only during host
shutdown; this review makes no claim about its measured cost.

The wait has no dependency on worker join or the Close operation itself.
It does not call `close_result` or wait for host-wide `live_ops == 0`.
Managed dispatch completion can finish its native operations, publish dispatch
completion, join operation retirement and close the request control gate while
the runtime remains available. Native rejection paths publish their own
request retirement. Both HTTP and gRPC queued admission paths observe stop
and recheck it before creating an admitted request. Startup failure paths
return before this loop and remain unchanged.

The existing separate Close thread owns its original monotonic deadline.
At expiry it requests cancellation and transport abort, then returns the
existing truthful Pending/Completed snapshot. A canceled Close operation or
an uncooperative managed handler does not authorize premature runtime or
owner release. The new loop can continue after a finite Close returns Pending;
eventual disposal still requires the admitted work to retire. Fault, timeout,
control-callback and cancellation routes remain available during that wait.

Escaped `BodyChunk` ownership does not prevent request retirement or satisfy
the new request-work predicate differently. Its native/managed byte credits
continue to keep `close_result` Pending until release. A final physical lease
on the request SafeHandle can remain after native request retirement; the
unchanged managed ticket checks continue to withhold public close completion.
The loop therefore permits native worker exit in that case without erasing
the managed obligation. Existing B20 `LifetimeAsync` and B17
`RetirementFixtures.FinalLeaseAsync` retain these distinct regression checks.

**Unchanged limitation:** request-less TLS reload operations are not covered
by this request-local predicate. Their create/run paths check the running
state, but a reload accepted concurrently with shutdown can race runtime
removal. This patch is not a general proof that every host operation joins.
Do not report TLS-reload concurrency as fixed or tested by these new gates.

## New network regressions

The two added B20 calls exercise exact HTTP/1.1 and HTTP/2 over real loopback
cleartext sockets. They are not TLS measurements. Each transfers and checks
the exact four-byte declared-length payload before releasing the managed
Finish gate, starts a two-second close, and checks that close remains pending
while the actual elapsed time remains below that deadline. It then requires
Finish success, Completed with zero pending requests and byte owners,
application-stream EOF, one successful Activity, and no failure warning.
The gate is always released in `finally`; disposal and I/O waits are bounded.
The existing sample's sixteen requests and warning expectations are unchanged.

These are functional lifetime regressions, not throughput measurements. The
H1 case isolates the observed early-body-completion race. H2 additionally
checks the same public graceful-close contract; the two transports need not
retire their bodies at the same instant. Root must obtain actual old-native
negative-control and new-native outcomes, rerun the unchanged original
sample, and run affected B17/B18/B19/B20 regressions with the newly built
artifact. Prior binary results do not transfer to the amended product.

## Verification performed

The reviewer read the exact two-file product diff and the dependent lifetime,
admission, cancellation, gRPC cleanup, body-channel, managed ticket and
diagnostic paths named above. The final worktree was clean and
`git diff --check` against ccff reported no whitespace errors. The correction
was independently checked against the first candidate. No runtime outcome,
benchmark identity or artifact hash was manufactured. Original ccff outputs
and diagnostic failures remain preserved. Formal measurement credit: **zero**.
