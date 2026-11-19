# Before gRPC per-mode resource profiles

All four ordinary gRPC modes completed with their actual post-run and existing-reader checks passing. This is **descriptive profiling only**, with zero formal comparison/noise/long duration credit. No product optimization has been applied.

Execution ran from 2026-11-19T21:25:41.311679+00:00 through 2026-11-19T21:28:10.634472+00:00. All16 reviewed command exits were0. Each mode used a fresh before-v2 server/common-client process pair, HTTP/2 plus TLS, identity compression, C4, rate16/s, 24 warmup calls, 323 measurement calls, 32 same-server recovery calls and5s idle. The immutable configuration is published in Plan commit0722639157accd79a6b19b33332dce38aa57c874.

## Actual numerical results

| Mode | Successful calls | Observed peak active calls | Successful calls/s | Arrival p50/p95/p99 ms | Server CPU (% of one core) | Sampled peak RSS MiB | Allocated MiB/s in observed bracket | Gen0/1/2 |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | --- |
| unary | 323 | 1 | 16.047518 | 2.504027 / 17.317414 / 35.474940 | 3.921780 | 56.980469 | 16.306950 | 35 / 34 / 33 |
| server-stream | 323 | 3 | 16.042737 | 24.142053 / 90.326079 / 146.003775 | 15.402583 | 42.785156 | 512.446451 | 917 / 896 / 895 |
| client-stream | 323 | 4 | 16.044168 | 16.512107 / 118.144691 / 180.213727 | 6.395454 | 67.308594 | 21.053005 | 86 / 33 / 33 |
| duplex | 323 | 4 | 15.996770 | 50.805839 / 132.446522 / 182.600513 | 19.702809 | 41.718750 | 518.345020 | 1006 / 932 / 932 |

All four modes recorded zero unexpected errors and zero correctness failures, with323 GrpcOK outcomes each. Independent client verification covers protobuf content/hashes, cardinality, status and trailers. Recovery and normal retirement passed; all ten final owner/request/queue/diagnostic gauges were zero. Cancellation and deadline probes are covered separately by the accepted mixed gRPC long workload.

## Payload and message counts

| Mode | Request messages | Response messages | Request Data bytes | Response Data bytes | Request encoded bytes | Response encoded bytes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| unary | 323 | 323 | 20672 | 20672 | 21964 | 21964 |
| server-stream | 323 | 10336 | 1323008 | 42336256 | 1324623 | 42407962 |
| client-stream | 10336 | 323 | 42336256 | 0 | 42407962 | 23256 |
| duplex | 10336 | 10336 | 42336256 | 42336256 | 42407962 | 42407962 |

Encoded bytes are protobuf payload bytes, excluding the gRPC envelope, HTTP/2 framing and TLS. The client-stream response has no Data bytes but a validated nonempty aggregate acknowledgement. Observed active calls are client counters, not a direct HTTP/2 stream census; socket counts are also not stream counts.

## Actual allocation observation brackets

| Mode | First / last dispatch UTC | Dispatch span s | Allocation bracket s | Samples | Allocated bytes delta |
| --- | --- | ---: | ---: | ---: | ---: |
| unary | 2026-11-19T21:25:43.454062+00:00 / 2026-11-19T21:26:03.579368+00:00 | 20.125305594 | 19.785026586 | 21 | 338305672 |
| server-stream | 2026-11-19T21:26:19.872730+00:00 / 2026-11-19T21:26:39.998589+00:00 | 20.125859335 | 19.750669434 | 21 | 10612805944 |
| client-stream | 2026-11-19T21:26:57.431235+00:00 / 2026-11-19T21:27:17.556870+00:00 | 20.125634806 | 20.033393419 | 22 | 442250704 |
| duplex | 2026-11-19T21:27:35.016808+00:00 / 2026-11-19T21:27:55.141982+00:00 | 20.125173976 | 19.490230838 | 21 | 10593411112 |

Allocation is approximate whole-server-process GC.GetTotalAllocatedBytes(false) growth over the actual first/last one-second snapshots. The bracket excludes some leading/trailing fractions of the load window and includes server fixtures, transport and telemetry. These are not exact allocations per call, per message or allocation-stack attribution. RSS and allocation are different quantities. CPU uses its own sampled process bracket. No confidence interval or between-version latency conclusion can be obtained from these four single-process descriptive cells.

The much greater observed allocation rate in response-streaming modes supports testing the already reviewed exact-E encoder scratch reuse hypothesis. The source mapping and ownership/quota constraints are in ../../source-grpc-writer-reuse.md. This observation does not establish that every allocated byte belongs to that writer and does not predict an after improvement. Preserve unary and client-stream behavior as well when testing the candidate.

## Identities and retained evidence

- Before product: ea5fa528035d025bd7a28698ee7c71194432236c.
- Package version: 0.1.0-perf01.before.1.
- Server AOT SHA-256: 5ba1df0946ece4a490d7bb43b295b7c720c3d32159c7e47e0cd28f0a3098460d.
- Common client AOT SHA-256: acb1c163cd51e291f58dbe51ae12c04f82c2b51538aa36e446a05890e06aadd0.
- Loaded native library SHA-256: 4827a6ecc76f871e0b4828f4ff6fe23a0d0a4ca1c57c5fc89a10a8e4d83ffe69.

summary.json explicitly selects numerical counters, correctness booleans, content hashes and package basenames. It omits raw process identities, host paths, command controls, keys and arbitrary raw strings. The original results, client operations, resource series, close receipts and reader observations remain under ROOT/perf01-evidence/profiling/before/grpc-<mode>-resources-001. Their hashes and the complete17-package closure hashes are in the summary; this is not a claim that every closure package was loaded.

The reviewed existing protocol_compare.read_cell extraction actually ran after all profile processes stopped and returned only its expected profiling-only ineligibility for each cell. It revalidated the source/identity/operation chain; no extra correctness or resource issue was suppressed. project_numbers.py then ran with actual exit0 and produced this explicit public projection. The exact read/launch recipe is ../../grpc-mode-profiles/README.md.

For an after profile, preserve all configuration, TLS, source and common-client identities, change only the actual reviewed after-server producer and fresh output/variant labels, and report its own package/native hashes. These profiles do not replace the formal interleaved comparison queue or either30-minute mixed gRPC group.
