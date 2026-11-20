# Perf-01: paired gRPC cancellation observations

## Result and scope

**Both actual JIT fixtures failed the unchanged three-second whole-host idle
assertion.** The diagnostic collection completed; that is not a functional
pass. The two processes use identical test source over the retained `0715`
implementation and the unretained `e524` scratch candidate. The native library
bytes are identical. This collection receives **zero B18 acceptance,
performance-comparison, capacity or long-test credit**.

The client observes the expected Cancelled status in both processes. After the
blocked encoder is released, the canceled request's cancellation source is
disposed and the observed managed byte charge returns to zero. A different,
whole-host residual remains: one retiring request and 79,264 native bytes.
The same native-byte charge was already observed immediately after the first
successful unary call in both processes, before cancellation case 103 existed.
Only the control had the complete stable counter combination at that first
observation; the candidate still showed one active request and 190 managed
bytes at that instant. Closing the host afterward
passes the original zero-resource assertion. These facts narrow the cause;
they do not make either failed idle assertion pass.

The subsequent [two-client admission probe](../grpc-connection-credit-001/README.md)
completed at 11:15:29 UTC and established the concrete ownership consequence:
with one request slot, an idle first connection retains the completed request's
admission permit and blocks a second independent client. Closing only the first
connection releases that blockage. The two original JIT failures below remain
failed; the later reproduction is separate evidence, not a substituted result.

| Observation | Control | Scratch candidate |
| --- | --- | --- |
| Runtime source | `0715ffb6376b1ae08259ad7e2cb30ff0320d83e7` | `e524ade4b5be0b8d556d2dd6f8e8d9fa9698c2f5` |
| Test-only overlay | `bf2ff028f153f3cc9e78f3b82a8d9a6c1bea42f0` | `63e67ed66c5ea942a6333e0274c1829ffa6bace6` |
| Actual JIT start (UTC) | 2026-11-20 11:10:27.616454 | 2026-11-20 11:11:02.050238 |
| Actual JIT end (UTC) | 2026-11-20 11:10:31.635681 | 2026-11-20 11:11:06.277044 |
| Actual JIT exit | -6, failed | -6, failed |
| Diagnostic stdout rows retained | 47 | 47 |
| First sampled stable residual during idle poll | 255.118 ms | 256.532 ms |
| Stable active / queued / retiring | 0 / 0 / 1 | 0 / 0 / 1 |
| Stable managed / native bytes | 0 / 79,264 | 0 / 79,264 |
| Original three-second idle gate | Failed | Failed |
| Subsequent host close reports zero | Passed | Passed |

The approximately 255 ms observations are sampling points, **not measured
retirement durations or a performance comparison**. The polling interval and
all original assertions remain unchanged. A disposed cancellation-source getter
does not by itself prove that every independent native reference has retired.

## Exact evidence and identities

- [evidence.json](evidence.json) records every restore, build and JIT outcome,
  source identity, all 13 identical fixture hashes, actual executable/dependency
  hashes, native hash, input-log hashes and the selected observations.
- [gauge-samples.json](gauge-samples.json) preserves **all 94 diagnostic rows**
  in original per-process order. Each row includes its original stdout line
  number, parsed fields and exact diagnostic text. No failing observation is
  omitted.
- [manifest.json](manifest.json) binds the public files and the original
  execution/log identities. Original failed B18 attempts and this paired
  diagnostic remain distinct records.

The unchanged loaded native asset is
`7dd16c9f13c394f09e6c88b0f814110a0b1c002166257c02b66a0cb0a99d54b5`.
The collection receipt is
`81cbbb54518ca6168255a7a26568b8f8135e7bc0e99de0ee03216cd55650f5c6`;
the reviewed diagnostic executor is
`261774c513f4284e999b8c42ea736a3a6b12427c0eceab9694da27411355a8eb`.
The overall collection ran from 11:09:54.115997 to 11:11:06.364847 UTC.
All six owned process groups and adopted-child inventories retired without
cleanup signals or controller interruption. The four restore/build commands
exited zero; both JIT commands retain their failed state and exit -6.

This was Release JIT on Linux x64, using the locked .NET 11.0.100 toolchain,
independent grpc-dotnet client, HTTP/2 and TLS, with the existing 15-second
host/method deadline and four-request admission limit. The controller was
affined to CPU 8 and the build/test children to CPUs 2 and 3 under the existing
exclusive measurement lock. No formal timed load was run concurrently.

## Source interpretation at the paired-observation checkpoint

The native snapshot reports whole-host counts and budgets, not the captured
request's individual ownership. The host already reaps completed requests on
a ten-millisecond timer. An absence of subsequent traffic therefore does not
alone explain this residual.

The observed 79,264 bytes exactly match the following **source-derived** sum:

| Credit | Calculation | Bytes |
| --- | --- | ---: |
| Request metadata anchor | `2 * 32768 + 200 * 48 + 2048` | 77,184 |
| Empty initial response metadata | Fixed grant | 1,024 |
| Empty trailer metadata | `4 * 8 + 1024` | 1,056 |
| Total | Sum | 79,264 |

The read source provides a strong ownership hypothesis. NativeWeave's
[`retain_headers`](https://github.com/IzuSharp/NativeWeave/blob/0715ffb6376b1ae08259ad7e2cb30ff0320d83e7/native/protocols/grpc/src/metadata.rs)
wraps each outgoing header value with an owner retaining its metadata credit.
Locked `http` 1.5.0 adopts the supplied `Bytes` without a payload copy.
Locked `h2` 0.4.20's HPACK encoder moves an indexed `Header`, including its
`HeaderValue`, into its persistent dynamic table. Those values can therefore
outlive the response body on an open connection. NativeWeave's
[`fully_retired`](https://github.com/IzuSharp/NativeWeave/blob/0715ffb6376b1ae08259ad7e2cb30ff0320d83e7/native/server/host/src/engine.rs)
predicate waits for the budget and metadata owners, while the request still
holds its admission permit. The exact locally read source-file hashes and
registry package checksums are recorded in `evidence.json`; this is source
inspection, not an upstream test execution.

At the original paired-observation checkpoint the causal admission probe was
**pending**, so the HPACK explanation was an inference. The approved diagnostic
subsequently executed as linked above. It uses a fresh
host with `MaxActiveRequests = 1`: finish a unary call on client A, observe its
physical ABI-owner retirement, keep A's connection open, and show a second
independent client B queued. Closing only A must then admit B without a host
restart; closing B must return all gauges to zero before host close. This
distinguishes an idle connection retaining request admission from a defect in
the scratch candidate's canceled encoder. The existing assertions will not be
weakened or replaced by subtracting a baseline byte count.

## Unimplemented correction option

One narrow option for review is to mark each credit-wrapped outgoing gRPC
`HeaderValue` sensitive using the existing public Rust API. Locked h2 then
avoids inserting that value into its dynamic table. HPACK would remain enabled
globally, including unrelated HTTP headers and inbound traffic, while static
indexing and Huffman encoding remain available. The credit would still cover
the actual header owner until its last wire reference is released.

This option changes neither header contents nor native ABI, public resource
limits, TLS or gRPC payload compression. It can increase encoded header bytes
and must be evaluated with the actual protocol workload. It is **not implemented
or accepted by this report**. Releasing request permits before their existing
ownership boundary or copying headers into unaccounted storage would require
different correctness and budget reasoning and is not an equivalent shortcut.

## Retention and review boundary

These synthetic numerical rows and checklists are retained in Git while its
history is retained. Complete raw logs, controls and binaries remain in the
measurement workspace; no remote raw archive is claimed. The public material
contains no credentials, certificates, private keys or unrelated user data.

Independent review accepted the test-only observation overlays and the owned
executor before execution. The projection additionally rehashed every stdout,
stderr and actual JIT artifact against the completed receipt. Source review,
diagnostic collection and functional acceptance remain separate obligations.
