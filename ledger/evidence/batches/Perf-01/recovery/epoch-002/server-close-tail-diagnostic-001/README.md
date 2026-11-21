# Perf-01 epoch-002: controlled response completion during close

**Both the frozen EA5 baseline and the ccff candidate reproduced a response
completion failure in one controlled diagnostic process each.** Neither result
is functional acceptance. Both diagnostic processes subsequently completed
close and disposal and retired with exit 0. That exit code means the diagnostic
finished recording its result; it does not mean response completion succeeded.

This record summarizes existing execution only. No workload was run to prepare
it, and it grants zero performance or long-running acceptance credit.

## Executed results

| Observation | Before | After |
|---|---|---|
| Product commit | `ea5fa528035d025bd7a28698ee7c71194432236c` | `ccff42c0df4141984ef9de497af7cd768753704a` |
| Diagnostic processes | 1 | 1 |
| Process start, UTC | `2026-11-21T03:58:29.774215+00:00` | `2026-11-21T03:58:51.348118+00:00` |
| Process end, UTC | `2026-11-21T03:58:30.183407+00:00` | `2026-11-21T03:58:51.871668+00:00` |
| Client bytes before close | 4 | 4 |
| Actual close-observation interval | 100.7307 ms | 101.8001 ms |
| Close task completed before gate release | false | false |
| Request cancellation observed on entering completion | false | false |
| `CompleteAsync()` outcome | `InvalidOperationException`; `complete_succeeded=false` | Same |
| Server failure diagnostics | 1 event: `/tail`, HTTP/1.1, `2xx`, `application_failure` | Same |
| Final close | Completed; pending requests 0; retained native bytes 0; retained managed bytes 0 | Same |
| Real `DisposeAsync()` | Returned | Returned |
| Process retirement | Exit 0; retired; remaining owned processes 0; owner children 0 | Same |
| Hook failures | 0 | 0 |

Both captured exceptions have type `System.InvalidOperationException` and
message:

> The native Server operation is not valid in this ownership or response phase.

The curated stack locations are `src/Server.Application/Response.cs:178` and the
diagnostic copy `samples/api/server-close-tail/Program.cs:44`. The latter is an
unchanged copy of the Plan probe source
`ledger/evidence/batches/Perf-01/diagnostics/server-close-tail-001/Program.cs`.
No complete raw stack or machine path is reproduced here. The recorded
exception is not a cancellation exception; the request token was observed as
not cancelled immediately before completion. This does not assert that no
later cancellation occurred during cleanup.

The hook observed these actual current-process native modules:

| Role | File | SHA-256 |
|---|---|---|
| Before | `libnativeweave_server.so` | `63c4950fceab5fe52017b5457b04759201de5a261d8087939cb177a20a5b88e2` |
| After | `libnativeweave_server.so` | `1f023b7506bde3f8c4a13b12de92e3e9503004ca3afc2d41a53bec17e44f1d97` |

## What the controlled path establishes

The same probe declares Content-Length 4, writes and verifies `tail` through an
independent HttpClient on a real HTTP/1.1 loopback connection, and holds the
handler before response completion. The client starts `CloseAsync(5 s)` before
releasing that gate. A nominal 100 ms observation is recorded with its actual
elapsed time. It does **not** prove that an acceptor or the native runtime had
already exited. Completion uses the default cancellation token deliberately;
this is a diagnostic ordering, not a claim of an equivalent production load.

The observed failure therefore exists under this controlled ordering in both
baseline and candidate. It does not establish which native invalid-state
check fired, how often production traffic encounters the condition, or whether
the original 16-request B20 sample failure had the same cause. Runtime teardown
overtaking the managed completion tail remains a source-supported explanation
requiring its own confirmation.

## Earlier unchanged-sample capture was inconclusive

Before this controlled probe, the original ccff Debug sample ran in ten fresh
processes with the StartupHook. All ten processes completed and retired with
exit 0, emitted hook readiness and the expected native module hash, and recorded
zero first-chance captures and zero hook failures. That finite attempt is
**inconclusive**: it did not reproduce the failure and is not evidence of a fix
or a replacement for the original failed functional sequence. Instrumentation
can itself affect scheduling.

The unchanged-sample capture sequence ran from
`2026-11-21T03:37:46.795872+00:00` to
`2026-11-21T03:37:53.703602+00:00`, including its hook build. The controlled
before/after sequence ran from `2026-11-21T03:57:59.654532+00:00` to
`2026-11-21T03:58:51.972163+00:00`, including both probe builds. These are
diagnostic orchestration intervals, not performance measurements.

## Provenance

[checklist.json](checklist.json) preserves project-only numerical observations,
curated source locations, source identities and receipt/stdout/stderr hashes.
Evidence filenames are relative to their named preserved output bundle; source
filenames are relative to their named repository. Original logs, operational
maps and complete stacks are not copied here.

- Controlled execution SHA-256: `a31ce0bb8fee82fef45c2150649389cb65974c05dc850abe0aff8ac955b2f979`.
- Earlier capture execution SHA-256: `e31d2dd37fe9b769f1a5dd17e25b94d9739a217ff096eecf677d016b5346222b`.
- Probe source-index SHA-256: `3d169297caf928ac4d6521810766c7607da31e55e5e7e89314741299680f3814`.
- Probe `Program.cs` SHA-256: `545f0366489f5504502a82e4ea84769505b4c267e6ca594aba5cf1586c1fd0d1`.

The original B20 failure remains recorded separately in
[b20-sample-failure-001](../b20-sample-failure-001/README.md). These diagnostics
do not change its 25 completed / 1 failed / 3 unexecuted outer-command outcome.
