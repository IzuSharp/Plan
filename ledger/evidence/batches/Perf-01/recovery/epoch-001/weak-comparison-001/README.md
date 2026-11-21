# Perf-01 weak-cache comparison and capacity observations

This record preserves the actual fresh ON/OFF/direct-Rust fixed-load comparison,
the frozen resource screen, and both weak-cache capacity searches. It selects no
final product. The resource screen has four vetoes and does not approve retention.
Independent review and the root decision remain separate records.

## Actual fixed-load comparison

All 18 independent processes were valid, met the frozen service standard and
passed correctness, recovery and drain checks. Each used 16 scheduled calls/s,
concurrency 4 and a requested 20-second load (323 guarded scheduled calls).
The common before-produced independent AOT client, HTTP/2 + TLS certificate,
payloads and application/driver source were fixed. All 5,814 ordinary calls
succeeded. There were no expected probes in these two short-comparison profiles.

[comparison.json](comparison.json) retains all 45 scenario/process samples,
18 whole-process resource rows, original A21 arrival-mean decisions, exact
equal-weight aggregates and direct-Rust gaps. No new statistical algorithm was
used. The following p99 values are **means of three process p99 values**, not
pooled percentiles. Rates are each scenario's contribution to its whole mix.

| Scenario | ON successful calls/s | OFF successful calls/s | Rust successful calls/s | ON p99 ms | OFF p99 ms | Rust p99 ms | Original OFF-minus-ON p99 change | A21 arrival-mean decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| grpc-unary 64 B | 8.041878 | 8.047073 | 8.049013 | 34.121362 | 29.883991 | 4.898251 | -12.418529% | inconclusive |
| grpc-unary 65536 B | 7.992237 | 7.997399 | 7.999328 | 32.460615 | 34.638773 | 6.679744 | +6.710158% | inconclusive |
| grpc-client 32 x 4096 B | 5.304808 | 5.300800 | 5.316101 | 121.218379 | 149.001531 | 4.859621 | +22.919917% | inconclusive |
| grpc-duplex 32 x 4096 B | 5.354386 | 5.350340 | 5.365784 | 229.327981 | 181.790832 | 5.709801 | -20.728892% | within_band |
| grpc-server 32 x 4096 B | 5.354386 | 5.350340 | 5.365784 | 180.224892 | 177.628131 | 4.925817 | -1.440845% | within_band |

## Whole-profile resource screen

[resource-screen.json](resource-screen.json) is the byte-identical original
path-free screen, SHA-256 `9c968657aae3b7d45d218393144222b7bbfbc263922225b0389e31add7e2636e`.
Its four vetoes are streaming duplex p99, streaming RSS, unary CPU and unary
RSS. The screen checks the original mean/maximum differences against the
frozen ranges; a mean-only table cannot replace that decision.

| Profile | Role | CPU % of one core | Mean sampled process-peak RSS MiB | Sampled managed allocation MiB/s |
| --- | --- | ---: | ---: | ---: |
| grpc-unary | ON | 3.740990 | 57.286458 | 17.301644 |
| grpc-unary | OFF | 3.704929 | 52.031250 | 17.307046 |
| grpc-unary | direct-Rust | 0.507094 | 13.128906 | N/A |
| grpc-streams | ON | 9.781756 | 90.787760 | 21.540902 |
| grpc-streams | OFF | 15.307160 | 46.506510 | 351.680494 |
| grpc-streams | direct-Rust | 0.944059 | 13.113281 | N/A |

ON lowers sampled streaming CPU and allocation, while its mean sampled
streaming RSS peak is **44.28125 MiB higher**. These observations do not
override the four frozen-screen vetoes. CPU/RSS/GC belong to the mixed
profile, not an individual RPC. Allocation uses a partial sampled managed
bracket; direct Rust managed GC is N/A. Native allocation, FFI and copy counts
are unavailable. Protobuf encoded byte counts exclude gRPC/HTTP2/TLS overhead.

## Actual capacity search, including failures

[capacity.json](capacity.json) retains all 16 ON and 12 OFF cells, including
failed service standards and the invalid ON 240/s confirmation. Both use the
same seven-scenario mix: 95% ordinary RPCs and 5% deadline/cancel probes,
concurrency 64, four HTTP/2 connections and the same quotas. Exploration cells
request 30 seconds; each final rate has three fresh 60-second confirmations.

| Role | Confirmed scheduled calls/s | Three ordinary successful-throughput observations, calls/s | Final recorded failing bracket, calls/s |
| --- | ---: | --- | ---: |
| ON | 216 | 204.918835, 204.917535, 204.902865 | 240 |
| OFF | 208 | 197.484812, 197.548386, 197.476445 | 224 |

The 216/s and 208/s values are the largest consistently passing sampled
offered rates, not exact server ceilings. The final bracket widths are 24/s
and 16/s; the 8/s difference does not establish a precise capacity improvement.
The existing algorithm first bisects to a 10% bracket, then steps down 10%
after failed confirmation and reconfirms. Generator/environment failures
cannot bound server capacity. Capacity p99 includes successful expected
probes; ordinary business throughput excludes those probes. No direct-Rust
capacity search or change to paired-long rates is claimed here.

ON at 240/s passed its 30-second refinement but failed all three 60-second
confirmations. The third is invalid: operation 9628 is a cancellation probe
with `IntegrityFailure: Wait headers were not committed.`, zero response
messages and no successful intentional cancellation. Separately, drain timed
out with one retiring request and 92,096 native payload bytes; the server
closed receipt is absent. Recovery's 32 checks passed. The generic reader
label is preserved verbatim, but it does **not** demonstrate payload corruption.
This record does not establish the defect's cause or whether OFF shares it.

## Identity, provenance and limits

ON product: `2e3995df8d86583ee9443348276ca8d918056bfc`.
OFF product: `4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4`.
Common application/driver: `2e3995df8d86583ee9443348276ca8d918056bfc`.
Original comparison role before means ON, and after means OFF; neither is
the EA5 main baseline/final-product pairing. The two NativeWeave roles loaded
the same native Server hash, with distinct actual AOT executables. Direct
Rust executable and shared client/certificate identities are explicit in JSON.

Caller execution hashes, actual UTC measurement windows, result/selection
hashes and original index/screen hashes are retained. The prior noise record
was published at Plan commit `abc974b50552e07fe4a44b5c0e711f6fabec4abc`
(readback receipt `7378dabbe032a139d55f3bbd985a9daa82ce84de6d401fc18706609bdb09484a`).
Internal paths, command lines, key metadata and full file maps are excluded.

**No final product is selected; retention is not approved. Long credit is
zero and recovery completion remains 0/10 thirty-minute segments.** No
historical numerical samples or duration credit are transferred.
