# Perf-01 recovery-002: actual before-only noise freeze

All ten frozen scenes completed three independently launched before workload cells each: **30 cells in total**. Every original owned command exited zero and retired. The unchanged original readers accepted the scene-specific validity, correctness, service and cleanup gates before producing each noise receipt. No candidate or direct-Rust process contributed to these noise bands.

Baseline is `ea5fa528035d025bd7a28698ee7c71194432236c`; common application/measurement driver is `2e3995df8d86583ee9443348276ca8d918056bfc`. The baseline was freshly produced for this recovery and retains its actual loaded package/native identities. Historical B22/B23 numbers and the two invalid PostgreSQL instrumented profiles are excluded.

## Actual workload and execution ledger

Rates count the original domain operations/calls/actions and must not be added into a cross-domain business denominator. Requested load windows exclude preparation, warmup, recovery, drain and idle. UTC outer timestamps include those other phases and extraction; they are not effective long-test durations.

| Scene | Rate/s | Concurrency / workers | Requested load s/process | Independent cells | Outer start UTC | Outer end UTC |
| --- | ---: | --- | ---: | ---: | --- | --- |
| postgresql-c16 | 180 | 16 concurrent | 60 | 3 | 2026-11-21T05:46:03.751185+00:00 | 2026-11-21T05:50:26.489204+00:00 |
| sqlite-c16 | 50 | 16 concurrent | 60 | 3 | 2026-11-21T05:50:28.630205+00:00 | 2026-11-21T05:54:26.969620+00:00 |
| http1-small | 16 | 4 concurrent | 20 | 3 | 2026-11-21T05:54:29.055502+00:00 | 2026-11-21T05:56:25.566440+00:00 |
| http2-small | 16 | 4 concurrent | 20 | 3 | 2026-11-21T05:56:27.714967+00:00 | 2026-11-21T05:58:25.264530+00:00 |
| http1-large | 8 | 4 concurrent | 30 | 3 | 2026-11-21T05:58:27.390195+00:00 | 2026-11-21T06:00:57.427707+00:00 |
| http2-large | 8 | 4 concurrent | 30 | 3 | 2026-11-21T06:00:59.567343+00:00 | 2026-11-21T06:03:30.641766+00:00 |
| grpc-unary | 16 | 4 concurrent | 20 | 3 | 2026-11-21T06:03:32.691855+00:00 | 2026-11-21T06:05:29.135071+00:00 |
| grpc-streams | 16 | 4 concurrent | 20 | 3 | 2026-11-21T06:05:31.280591+00:00 | 2026-11-21T06:07:34.144144+00:00 |
| codec-w1 | 134 | 1 worker(s) | 120 | 3 | 2026-11-21T06:07:36.283874+00:00 | 2026-11-21T06:15:36.413031+00:00 |
| codec-w2 | 241 | 2 worker(s) | 67 | 3 | 2026-11-21T06:15:39.143641+00:00 | 2026-11-21T06:20:59.021227+00:00 |

## Numeric publication and provenance

[numeric-noise.json](numeric-noise.json) contains an exact value-preserving join of the ten original numeric projections: original bands, original noise-receipt SHA-256 and the three before-process result identities. No new statistical algorithm, revised band, percentile pooling or round-trip through a spreadsheet was used. Its SHA-256 is `b127934f9bde44fbb8b8b67d7c8f7927063f8323bb05094072ae71240d04e090`.

[execution-ledger.json](execution-ledger.json) preserves the actual per-scene execution and finite-command receipt identities, settings and UTC boundaries without operational paths, argv, environment values, PID maps or TLS material. The precise baseline admission is `56725c0a0167e04bb021210d879b6616f85523705bc19bd04bc11e2cbb42d380`; measurement source index is `6b1d1e8ec6ee80271fdbbeb1c6d13909b92ca13c7a28cbc4fd4085f98f6a4c2c`.

The existing measurement gate still requires the actually published commit/path/blob, exact remote readback bytes and retrieval receipt, the local matching Git object path, and all ten original completed noise executions. A committed plan or a successful local Git read alone is insufficient. The integration handoff records publication/readback only after it actually occurs.

The next phase runs the existing interleaved before/final/direct comparisons, with existing managed controls where applicable. These before-only measurements do not establish any optimization gain, capacity limit or direct-Rust gap. **Long-test acceptance remains 0/10 and zero seconds at this checkpoint.**

## Retention

The numeric projection, ledger and readable report are committed project records with no configured artifact expiration; they remain available while the Git history is retained. Original local request/result ledgers, resource time series, correctness records and command logs remain retained under the exact receipt hashes. Final delivery separately records retrievable raw-artifact retention; this noise publication does not claim an upload or replace the original evidence.
