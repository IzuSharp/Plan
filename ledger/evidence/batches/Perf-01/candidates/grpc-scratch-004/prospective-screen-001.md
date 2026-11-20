# Perf-01 gRPC scratch prospective screen after native and managed ownership corrections

This policy is fixed before new diagnostic timing. It supersedes only the
unexecuted timing portion of `grpc-scratch-003-prospective-001`; all original
failed gates and preparation identities remain preserved.

The control is `db95a9fbdd18c208ba8fa3fdb6dabaa2bcc073c0` and the scratch
candidate is `9de3f74444246e356a2b12ab664ef99286309aaf`. Both contain the same
native metadata ownership correction and managed admission-lifetime correction, with identical regressions. Only the
three managed scratch implementation files differ. Their freshly built and
actually selected native Server bytes must be identical. This isolates scratch
reuse from the separately demonstrated connection-owned metadata defect and managed ticket-tail admission race.

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

The latest correction keeps the request owner until the full managed dispatcher,
protocol continuation and cancellation join complete. Physical release and ticket
removal share a separate admission gate. Delayed final leases keep the managed
close obligation; native release does not hold the host control gate. Its extra
synchronization and retained owner lifetime are costs to observe in the eventual
full application comparison. No improvement is presumed.

The corrected candidate's actual B17 managed JIT and Native AOT gate passed with
105 checks and 43 dispatches in each mode. Its receipt is separately fixed at
`9ba7c4dd2d2d95f0fe911468815dfe980fb4304bbc26244ab673721957c8ddad`.
Before timing, both roles still require fresh native/B24/protocol producers and
full B18 JIT/AOT/API/package verification. The shared Application, MCP and
diagnostics managed/API/package gates must also pass. Existing native-component
evidence is reused only with unchanged source inputs, logs and retained bytes;
its original producer is preserved. B19/B20 managed subsets do not claim that
their entire original native-producing verifiers ran.

The public candidate `12c477f0cdbc01fb026e98ac0e26eb45617424ed` has the same tree
as the locally fixed candidate. Actual producer commits stay explicit. The
original corrected-control AOT failure and the separate deliberately held
causal proof remain preserved; neither grants performance or global acceptance.
