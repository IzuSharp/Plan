# Perf-01 fresh weak-ON noise and frozen ranges

Six independent ON processes completed on 2026-11-20. All recorded results are
valid, meet the frozen service standard, pass their payload/status checks and
drain successfully. This is an ON-only noise collection; it makes no ON/OFF
improvement, capacity, cache-retention or final-selection decision. Independent
review and verified publication remain separate prerequisites.

[The numerical projection](samples.json) retains all 15 scenario/process samples,
six whole-profile resource rows, five original A21 arrival-mean bands and all 11
frozen descriptive vectors. It binds the complete original noise index and the
actual resource-freeze hashes. No historical numerical samples are transferred.

## Actual measured windows

Both profiles use 16 calls/s, concurrency 4 and a 20-second request. The original
guarded schedule offers 323 calls per process; all 1,938 ordinary calls succeeded.
Unary contains 64-byte and 65,536-byte payloads. The streaming profile contains
server/client/duplex streams with 32 messages of 4,096 payload bytes. All use
the same independent AOT client and real HTTP/2 + TLS sockets.

| Profile / repetition | Actual measurement start–end UTC | Server CPU % of one core | Sampled server RSS peak bytes | Sampled allocation MiB/s |
| --- | --- | ---: | ---: | ---: |
| grpc-streams / 0 | 22:34:15.692732–22:34:35.928979 | 9.745185 | 94494720 | 21.252202 |
| grpc-streams / 1 | 22:34:54.012523–22:35:14.150634 | 10.368847 | 92917760 | 21.495609 |
| grpc-streams / 2 | 22:35:31.479306–22:35:51.623695 | 11.092876 | 91533312 | 21.640703 |
| grpc-unary / 0 | 22:32:27.968015–22:32:48.096123 | 3.770439 | 54185984 | 17.294953 |
| grpc-unary / 1 | 22:33:03.401860–22:33:23.568448 | 3.667984 | 54042624 | 17.292110 |
| grpc-unary / 2 | 22:33:38.873795–22:33:59.001026 | 3.824622 | 57479168 | 17.331755 |

## Interpretation

The A21 bands concern independent-process arrival means. The separate 11 resource
vectors cover five scenario p99 values plus CPU, RSS and allocation for each
profile. Their exact ranges are descriptive, not confidence intervals. The JSON
copies the original values and their ordered three-process vectors; it performs
no new aggregation, hypothesis test or adjustment of a frozen threshold.

Scenario rates share the whole measured window. Resource observations belong to
the whole mixed profile, not individual RPCs. CPU is relative to one core; RSS
is sampled; allocation is a partial sampled managed bracket. Client call overlap
is not an exact active-stream counter. Protobuf encoded bytes exclude gRPC
envelope, HTTP/2 and TLS overhead. No network-compression benefit is claimed.

The ON product and common app/driver commit are `2e3995df8d86583ee9443348276ca8d918056bfc`.
The measured Server, loaded native module, fixed before-produced client and TLS
certificate identities are included without private paths or key metadata. The
original weak-reader role name before denotes ON here, not the main EA5 baseline.

**Long credit remains zero; no final candidate is selected by this record.**
The projection is a disclosure of actual samples, not an independent acceptance
receipt. Private operational records and full file maps remain local.
