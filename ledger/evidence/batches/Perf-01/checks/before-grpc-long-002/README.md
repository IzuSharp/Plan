# Perf-01 before gRPC long group: accepted 115/s candidate

The unique prospective candidate in amendment 002 completed successfully. The
original 128/s long group remains rejected with zero duration credit; see
`../grpc-before-long-failed-operations-001/`. Amendment 001 was never executed.
This accepted result does not erase the earlier failure or prove 128/s stability.

- Parent freeze: `85061c4e01b28fc72a5b20519ce2d8c01d79cae271238ba36e0a3465b0b8f4a3`.
- Adopted amendment: `2c4d5a0a00cf2f763e4641043f7d6908319ea4d3e7fdbaf2760039bc6808b513`,
  published and byte-read back at Plan `e2683c13e35dd1be498066813f9ee28dc16aa722`
  before execution. CI run `44571766325` completed successfully for that head.
- Runtime source: `ea5fa528035d025bd7a28698ee7c71194432236c`; harness head:
  `ab8357dd7e3d924e267f584056e5fba6d3a59265`. No runtime optimization yet.
- Exact commands, actual exits and timestamps: `execution.json`. Every command
  exited zero. Independent acceptance and consumed hashes: `verification.json`.
- Native AOT, real HTTP/2 + TLS, identity gRPC encoding, 115 scheduled calls/s,
  64 admission slots, unchanged mixed unary/server/client/duplex/deadline/cancel
  profile. The final after group must use this same adopted configuration.
- First and last dispatch: 2026-11-19T16:57:34.317798Z and
  2026-11-19T17:27:36.421953Z. Final measured completion:
  2026-11-19T17:27:36.485265Z. Independently proved effective load:
  **1802.101046909 seconds**. Warmup, recovery and idle time are excluded.
- 207243/207243 successful logical checks; 196880 ordinary business successes,
  4145 expected cancellation checks and 6218 expected deadline checks. No
  unexpected errors, timeouts or correctness failures. Ordinary throughput:
  109.2462153101036/s; logical-check throughput: 114.9965125940258/s.
- Arrival latency p50/p95/p99: 11.525236/102.848121/152.456566 ms. The p99
  includes the frozen mix; per-scenario contributions remain separate.
- Server CPU: 45.9817113089409% of one core, 828.0 CPU seconds. Sampled
  measurement RSS maximum: 115073024 bytes. Procfs lifetime high-water RSS has
  a different sampling scope and remains separately recorded.
- Server managed allocation delta: 2269694413272 bytes. This is allocation
  volume, not retained memory. Exact copies/FFI counts remain unavailable in
  this timed cell.
- Recovery 32/32 passed; 60-second idle observation, zero final request/owner
  gauges, and completed/disposed server closure passed.

`summary.json` retains exact per-scenario successful calls, messages and payload
bytes, resource summaries, quantiles and limitations. Raw sparse histogram bins
and full ledgers remain unchanged in the source output. These small control
copies are not the complete raw archive: publication and fixed-commit readback
of that archive are still pending. Current total accepted long groups: **2/10**
(before HTTP and before gRPC). PostgreSQL, SQLite and codec before groups follow
before any product runtime edit.
