# Perf-01: prospective gRPC scratch screen

This is a **pre-measurement source and policy checkpoint**, not a performance
result. The candidate remains unretained. Its fresh producer build has started;
actual B18 correctness, package/native identities, noise calibration and
comparison receipts must establish their own outcomes. No formal-matrix,
capacity or 30-minute credit is assigned here.

The accompanying [portable record](prospective-screen-001.json) preserves the
approved policy verbatim, complete source fingerprints and the build-state
snapshot. It excludes workspace paths, TLS private-key material, environment
snapshots and the private operational bundle.

## Exact scope and source

| Identity | Commit or tree |
|---|---|
| Diagnostic control | `0715ffb6376b1ae08259ad7e2cb30ff0320d83e7` |
| Candidate local producer source | `e524ade4b5be0b8d556d2dd6f8e8d9fa9698c2f5` |
| Public candidate counterpart | [`458939dab00d4080cd36076d31d912114f245340`](https://github.com/IzuSharp/NativeWeave/commit/458939dab00d4080cd36076d31d912114f245340) |
| Candidate tree shared by those two commits | `6dad1215d22d5c950c33dafeae3e9d876ec7cd0b` |
| Reviewed diagnostic executor source | Plan `431c835ecd0ac62327257dd0caa2892706b10686` |
| Original formal Perf-01 baseline, unchanged | `ea5fa528035d025bd7a28698ee7c71194432236c` |

The complete prepared execution specification is bound by SHA-256
`96fabcc9891ed0fbe9e1b3eee14c1dd7aeec75a40c500bcd84d52089fa578eeb`.
Independent source review accepted that exact executor for diagnostic gates.
Five bounded utility checks and the clean-source preflight passed in
0.35257 seconds, without compiling a product or running a workload.

The measured target is the remaining full-capacity writer allocation on unary
calls. The internal candidate gives unary and client-stream registrations one
weak scratch slot. Each encoding still receives a fresh scoped writer and the
full encoded-capacity admission credit. Atomic take prevents concurrent loans
of one buffer. The entire backing is cleared after writer disposal and the
synchronous native copy, before weak publication and credit release. Server-stream
and duplex methods keep their existing per-call cache. No public signature, protobuf/TLS
configuration, Rust source or native ABI changes. The executed B18 gate must
still verify the preserved error, cancellation, ownership and bound semantics.

## Fixed workload and calibration boundary

Both profiles retain actual HTTP/2 + TLS, the frozen independent client,
16 configured calls/s, concurrency 4 and 20 configured schedule seconds.
Service CPUs are 2–3, generator CPUs 0–1, and the controller is on CPU 8.
Warmup, 32-call recovery, five-second idle observation and retirement remain
separate from measurement.

| Profile | Frozen mix |
|---|---|
| Unary | Equal 64-byte and 65,536-byte Data payloads; one request and response message per call. |
| Streams | Equal server-stream, client-stream and duplex; 32 messages with 4,096-byte Data. The client-stream response remains its existing acknowledgment. |

The unchanged encoded limit is 1 MiB, with separate 64 MiB managed and native
payload budgets. The service limits remain zero unexpected errors, 500 ms
arrival p99 and 256 MiB sampled whole-process RSS. gRPC compression remains
`identity`; this experiment claims no protocol compression benefit.

Three fresh control-only processes per profile establish **six calibration
processes**. Their complete noise-index hash must be recorded/committed before
the first candidate timing. Each profile then gets three fresh control,
candidate and direct-Tonic triplets, ordered A/B/direct, direct/B/A,
A/B/direct: **eighteen comparison processes** in total. No calibration process
is reused as a comparison process.

The frozen driver, raw reader and A21 algorithms are reused. A separately
hashed reader entry adapter configures only the reader's baseline identity to
the diagnostic control `0715`; its original `ea5fa5` source is unchanged.
Sidecars preserve that distinction. The existing raw validators still decide
correctness, generator validity, producer identity and retirement. A valid
observed SLO miss is retained with its actual exit and classification; it does
not earn acceptance.

## Prospective screen, fixed before candidate timing

Here **A0** denotes the three control-only calibration values, **A** the three
fresh interleaved controls and **B** the three fresh candidate processes. Each
profile and each ordinary scenario keeps its own relevant calibration range.

| Quantity | Fixed decision rule |
|---|---|
| Unary allocated MiB/s, the primary target | `min(A) - max(B) > max(A0) - min(A0)`. Every candidate process must beat every interleaved control by more than the pre-frozen allocation-rate range. |
| Mean latency | An original A21 `regression` verdict vetoes the screen. A latency win is not required; `within_band` or `inconclusive` may coexist with a reproducible allocation reduction. |
| Each ordinary scenario p99 | Both `mean(B) - mean(A)` and `max(B) - max(A)` must be no greater than that scenario's pre-frozen A0 p99 range. |
| Whole-profile server CPU and maximum sampled RSS | The same mean-and-worst rule uses each corresponding A0 resource range. It applies to both unary and streams. |
| Streams allocation | Report the observed mixed-profile allocation separately. Do not attribute the whole-profile value solely to client streaming. |
| Missing or failed observations | Missing/nonfinite required values are unresolved; a failed screen is rejected. No altered threshold, automatic retry or selected replacement is allowed. |

The resource and p99 rules are **descriptive screens**, not statistical
confidence statements. Allocation uses the existing approximate
`GC.GetTotalAllocatedBytes(false)` bracket and its actual observed duration;
it is not exact bytes per writer. CPU/RSS belong to the whole profile, not to
individual scenarios. All original absolute service and correctness limits
remain mandatory.

Screen eligibility permits a retention review. It does not retain the patch,
waive B18, replace an affected final comparison/capacity test, or transfer
existing measurements to a new binary. The five accepted long-duration groups
belong to the original main baseline; no `0715` after-long group is credited.
Actual rebuilt package,
executable and loaded-native hashes must accompany every eventual result.
