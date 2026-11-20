# Perf-01: persistent HTTP/2 metadata blocks request admission

## Actual result

**The diagnostic reproduced an existing admission bug on unchanged `0715`
runtime code.** A successful unary response and physical managed ABI-owner
retirement leave one native request holding the sole admission slot while its
HTTP/2 connection remains open. A second independent client queues. Closing
only the first client's connection releases the retained metadata and admits
the second call without restarting the host.

The three commands—locked restore, Release JIT build and the actual probe—all
exited zero. This means the diagnostic successfully reproduced the bug. It is
**not a product/B18 acceptance pass**, and receives no performance-comparison,
capacity or long-duration credit. The earlier [paired JIT failures](../grpc-cancel-observation-001/README.md)
remain failed and unchanged.

| Observed event (UTC, 2026-11-20) | Physical ABI owner retired | Active | Queued | Retiring | Managed bytes | Native bytes |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 11:15:29.1338824 — first response complete; client A open | Yes | 0 | 0 | 1 | 0 | 79,264 |
| 11:15:29.1411588 — independent client B queued | Yes | 0 | 1 | 1 | 0 | 79,264 |
| 11:15:29.2403406 — B still blocked; A still open | Yes | 0 | 1 | 1 | 0 | 79,264 |
| 11:15:29.3190353 — only client A disposed | Yes | 0 | 1 | 1 | 0 | 77,184 |
| 11:15:29.3426967 — B succeeds; B connection open | Yes | 0 | 0 | 1 | 0 | 79,264 |
| 11:15:29.3694671 — both clients closed; host still running | Yes | 0 | 0 | 0 | 0 | 0 |

Exactly two handlers enter. Both responses match the expected protobuf content
and OK status. B's handler and response remain incomplete while A's idle
connection retains the first request. All gauges return to zero **before**
host close; the final ordinary close check also passes. These event timestamps
are diagnostic observations, not benchmark latency samples.

## Ownership cause

The actual 79,264-byte residual consists of the 77,184-byte request metadata
anchor, 1,024-byte initial response metadata grant and 1,056-byte empty-trailer
grant. Immediately after only client A closes, the observed charge falls by
exactly 2,080 bytes to the request anchor; native reaping can then release the
request and its admission permit. The second call subsequently completes.

This agrees with the exact locked source path recorded in the paired report:
NativeWeave's `retain_headers` attaches `Arc<Credit>` owners to outgoing header
values; `http` 1.5.0 adopts those `Bytes`; `h2` 0.4.20 stores indexed values in
its persistent HPACK dynamic table. NativeWeave's request retirement predicate
waits for those metadata owners while its request object still holds the active
admission permit. A connection-level compression cache thereby prolongs a
completed request's admission ownership.

This is distinct from canceled encoder 103 retaining its scratch buffer. The
same native-byte charge appeared before that encoder existed in both paired
processes, and this separate probe has no canceled encoder or scratch change.
The reproduced code is `0715`; a source comparison against the fixed pre-Perf-01
main `ea5fa528035d025bd7a28698ee7c71194432236c` finds no changes in
`native/protocols/grpc` or `native/server/streaming`, nor in the host request
ownership/retirement path. The host-file changes concern acceptor shutdown
completion. This establishes that the implicated source path predates Perf-01;
**the causal probe was not executed on the main binary**.

## Exact configuration and identity

The probe uses real TLS HTTP/2 sockets and two independent grpc-dotnet channels
and handlers against one host. `MaxActiveRequests` is one; host and method
deadlines are both 15 seconds. Each observed phase has its declared three-second
bound with five-millisecond snapshot polling. The queued observation contains
a configured 100 ms delay. HPACK and connection-pool settings are unchanged.
The first request's `NativeResourceOwner.Retirement` is awaited before client B
starts, so the observation follows actual physical managed ABI-owner release.

Runtime source:
`0715ffb6376b1ae08259ad7e2cb30ff0320d83e7`.
The test-only overlay is
`01f3e96580edde1ec5bbc676d7000180879a436d`; it adds a separate entry switch and
the two-client fixture without modifying product implementation. The actual
native library remains
`7dd16c9f13c394f09e6c88b0f814110a0b1c002166257c02b66a0cb0a99d54b5`.

The complete execution ran from 11:15:06.252715 to 11:15:29.569607 UTC; the
actual JIT process ran from 11:15:28.706641 to 11:15:29.498365 UTC. The receipt
SHA-256 is
`5d44d527ca24713c09f3d224ac56ef64116b7ed58c01d783fce586726b814251`,
and the independently reviewed executor SHA-256 is
`676c1363693379681f52fa671380b9b2d2ce7f0fa3831e50626cc724288ee8cc`.
All owned groups and adopted descendants retired without cleanup signals or
controller interruption. This is Release JIT evidence, not Native AOT evidence.

## Evidence, failures and next work

- [evidence.json](evidence.json) records the exact commands' outcomes and times,
  fixture and actual artifact hashes, all six snapshots, source comparison,
  and original execution/log hashes.
- [gauge-samples.json](gauge-samples.json) retains all seven `CREDIT-PROBE`
  lines, including the reproduction marker, in original order with stdout line
  numbers and exact text. There are seven original PASS assertions.
- [manifest.json](manifest.json) binds these public files to the input logs and
  receipt. Every input log and JIT artifact was independently rehashed.

An initial source-only description used an incorrect executor hash and failed
before any workload. The unchanged source passed after supplying its actual
hash. Separately, the first report projection incorrectly expected eight PASS
markers instead of the seven actually present; it failed before writing the
numeric files. The recorded projection correction changes that count only.
Neither issue changes the actual probe, outputs or classification.

The per-value never-index correction described in the paired report is being
reviewed separately. No correction or performance benefit is accepted here.
Existing short and long results retain their original binaries and frozen
validity criteria; a changed final native library requires fresh bindings and
the affected final measurements. The failed cancellation gate remains an open
functional obligation until the corrected product passes it.

Public synthetic numbers and checklists remain in Git while its history is
retained. Complete raw controls, logs and binaries remain in the measurement
workspace; no remote full-raw archive is claimed. This report contains no
certificates, private keys, credentials or unrelated data.
