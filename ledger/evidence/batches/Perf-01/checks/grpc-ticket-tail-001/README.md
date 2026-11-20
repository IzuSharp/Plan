# Perf-01: actual managed ticket admission handoff diagnosis

This bounded **Native AOT diagnostic reproduced an admission defect** in the
existing managed request retirement order. The first real TLS/HTTP/2 request
had physically released its native owner and all native request/byte gauges
were zero, while its managed ticket still occupied the one-request admission
limit. A second request on an independent TLS/HTTP/2 client received the
original `Internal: managed dispatch unavailable` error. Instrumentation
identified the exact `ticket_capacity` rejection branch with one old ticket,
limit one, a different request identity and no second handler invocation.

This run deliberately held the existing managed tail to make the ordering
window observable. It is a successful **defect reproduction**, not a passing
product gate or a new spontaneous failure. The earlier uninstrumented local
B18 AOT failure remains a separate failed record. This diagnostic does not
retroactively add a branch trace to that earlier execution. Performance,
capacity and 30-minute duration credit are all **zero**.

## Exact input and execution identities

| Identity | Actual value |
| --- | --- |
| Corrected-control runtime parent | `da48ccf9d263155ebcbc2a6eea986f6b05972f51` |
| Diagnostic-only source overlay | `ee71bf2e0f30c0ee3b8b6c9ae81adf82c0da7f0a` |
| Executor SHA-256 | `5ce670ffdd584e86ee4eaf0e813672dfc6d7bb234f46d6e586181c2d6da406ac` |
| Actual native Server SHA-256 | `28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2` |
| Actual AOT executable SHA-256 | `49772cb6ddcf15334474921ca871ada5e3d862170a51f8fa20e2e1e7167ae575` |
| Completed execution receipt SHA-256 | `21ac50d2cf6271816468b0716b62c1822bcb78f138481e6b36335e488e510d2a` |
| Collection interval | 2026-11-20 11:51:18.830107–11:52:16.072323 UTC |
| Actual AOT process interval | 2026-11-20 11:52:15.694455–11:52:15.947667 UTC |

The overlay changes only `src/Server.Native/NativeHost.cs` instrumentation,
the explicit diagnostic switch in `tests/Protocols.Grpc/Program.cs`, and the
new `tests/Protocols.Grpc/TicketTailProbe.cs`. Native sources and all original
B18 fixture assertions remain unchanged. The native library is the actual
fresh corrected-control asset already produced before the failed local B18
run. No new Rust producer or performance workload was executed here.

The existing owned process-group and adopted-child guard ran three commands:
locked AOT restore, AOT publish, and exactly one AOT diagnostic. All returned
zero. All process groups and adopted descendants retired without cleanup
signals. The actual output inventory was recorded before execution and checked
afterward; the fixture independently checked the native bytes after the probe.
The controller and all source/artifact identities were independently rehashed
when preparing this report.

## Actual observations

The host's configured active-request limit was one. Host and method timeouts
remained 15 seconds, clients retained their 20-second timeout, individual
observation phases and the held-tail barrier were bounded by three seconds,
and final close retained a five-second bound. The barrier was unconditionally
released in `finally`; original ticket cleanup was also unconditional.

| UTC observation | Event | Native owner retired | Active / queued / retiring | Managed / native bytes |
| --- | --- | --- | --- | --- |
| 11:52:15.9165022 | Existing managed tail held | Yes | 0 / 0 / 0 | 0 / 0 |
| 11:52:15.9165264 | Before the independent second client | Yes | 0 / 0 / 0 | 0 / 0 |
| 11:52:15.9186693 | Second request rejected | First owner already retired | Actual managed ticket count 1; limit 1; new request 2; kind 1 | No snapshot is inferred for this event |

Seven fixture assertions passed: actual Native AOT execution; exact first-call
protobuf and OK status; zero native admission/byte gauges while the old ticket
was held; the second client's exact original Internal error; the observed
ticket-capacity branch and one handler entry; completed close with zero pending
requests and retained bytes; and unchanged actual native-library hash.
`gauge-samples.json` preserves all four diagnostic lines verbatim together with
their parsed numeric fields, including the final AOT/reproduction marker.

## Source explanation and correction boundary

`Application.DispatchAsync` awaits `NativeRequest.CompleteDispatchAsync` before
returning to `HostTicket.RunAsync`. In the observed implementation,
`NativeRequest.CompleteCoreAsync` drops the physical owner and returns the
native admission permit before the later `HostTicket` continuation removes the
managed ticket. `NativeHost.Notify` checks the managed ticket count against the
same configured active-request limit. The controlled window proves that a
legitimate newly admitted native request can therefore encounter a stale
managed admission count.

This defect is separate from the earlier HPACK/header-credit retention
diagnosis: this probe uses the corrected native asset and actually observes
zero native ownership before the managed count rejects the second request.
The existing count and lifecycle assertions were preserved rather than
subtracting retained ownership or adding a private client-side wait.

A product correction and its regressions require separate actual gates. The
proposed ordering must retain request ownership until the entire managed tail
has joined, coordinate final physical release with new managed admissions,
and keep physical retirement a host-close obligation. Merely removing the
ticket early would weaken close semantics. No proposed correction is accepted
by this diagnostic report.

## Independent audit and evidence retention

The offline inspector checked the completed receipt, all six stdout/stderr
hashes, 16 source-file hashes, 12 actual AOT artifact hashes, exact source parent
and three-file overlay, all seven assertion markers, all four diagnostic rows,
and finite process/adopted-child retirement. It ran once on CPU 8, exited zero
in 0.153232714 seconds, and executed no product test or workload.

The four public files contain the complete small numerical projection, fixed
roles, identities and verification hashes. Raw operational commands, host
paths, process identifiers and control records are excluded. The original
execution receipt, test overlay and actual binaries remain owner-controlled
working evidence; this report does not assert a durable external binary
archive. The public projection remains retrievable while the corresponding
Plan repository history is retained. Its manifest binds the inspector and
offline audit receipt as well as the published bytes.
