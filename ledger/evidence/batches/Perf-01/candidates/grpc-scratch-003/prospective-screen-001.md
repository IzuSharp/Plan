# Perf-01 gRPC scratch prospective screen after native ownership correction

This policy is fixed before new diagnostic timing. It supersedes only the
unexecuted timing portion of `grpc-scratch-002-prospective-001`; all original
failed gates and preparation identities remain preserved.

The control is `da48ccf9d263155ebcbc2a6eea986f6b05972f51` and the scratch
candidate is `1207b8d3b0c273752a28dabdf3e7a2b54c933571`. Both contain the same
native metadata ownership correction and identical new regressions. Only the
three managed scratch implementation files differ. Their freshly built and
actually selected native Server bytes must be identical. This isolates scratch
reuse from the separately demonstrated connection-owned admission defect.

Six fresh control-only processes, three per unary/streaming profile, establish
new descriptive noise ranges. Their complete actual noise index hash must be
committed before the eighteen interleaved A/B/direct processes. No old noise
sample is transferred to the corrected native build. The original profile,
rate 16 calls/s, concurrency four, twenty-second load, TLS, independent client,
payloads, ordering and correctness/service/resource limits remain unchanged.

The decision formulas are exactly the earlier published formulas:

- The primary unary allocation margin is the minimum interleaved control
  allocation MiB/s minus the maximum candidate value. It must strictly exceed
  the maximum-minus-minimum range of the three fresh control-only observations.
- Every original A21 mean-latency regression vetoes eligibility. A proven
  latency improvement is not required if the allocation improvement clears the
  declared margin and every other screen passes.
- For each ordinary scenario's arrival p99 and each profile's server CPU and
  peak RSS, candidate mean minus control mean and candidate maximum minus
  control maximum must each be no larger than the corresponding fresh
  control-only range. Both profiles must pass; streaming allocation is reported
  separately without replacing the unary primary screen.
- Missing required observations remain unresolved. Correctness, generation
  validity, service limits and cleanup remain mandatory. A failed screen is
  rejected; no threshold change, selected replacement or automatic retry follows.

The ranges are descriptive three-process ranges, not confidence intervals for
tail latency or resources. Eligibility permits independent retention review;
it does not itself authorize retention or establish application performance.

The native correction prevents request-owned metadata values entering the
connection's HPACK dynamic table, while allowing existing exact/static index
reuse without retaining that owner. Global HTTP/2 header compression remains
enabled. Repeated response metadata may require additional header bytes; this
cost belongs in the eventual measured protocol comparison. gRPC payload
compression remains identity-only, and no network compression gain is claimed.
