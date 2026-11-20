# Perf-01 independent review: fresh weak-ON noise and ranges

**Verdict: ACCEPT for the exact six noise populations, the frozen ranges, and the public files identified below.** No actionable defect was found in these inputs. This decision does not approve weak-cache retention, establish sustainable capacity, select a final product, or grant any 30-minute credit.

The reviewer read the original source and independently recalculated existing raw records with standard-library code on the control CPU. No target modules were imported and no build, service, test or workload was started. This is an evidence review, not a GitHub approval from a second account.

## Bound inputs

| Input | SHA-256 |
| --- | --- |
| Actual finite noise execution | `80b6b0447109885be228b74932a03c33949117a928eb20b4c9b681f78127e19d` |
| Actual finite offline ranges execution | `87eed4bd889c9e99eb21159d358111b13532b0ec254def475a1f65a934ee5f18` |
| Complete six-process noise index | `924e8bd03bff9a50fb56c3038a0bb44a82fa75b2f315a1ab9aa086629539772f` |
| Actual resource-range freeze | `6737006913586e9983e3337d6bcee08d6c015b3a622f1f606d4217011be2ceb8` |
| Original frozen weak policy | `0399d704c04e625412c8a365c6e0b071588d3059632dfcda8d6937fa429b3cc9` |
| Finite caller source index | `a48786a56e0b233b670e6c8f6b4c7d94678610c54f49bdd2093376e4587279a9` |
| Original resource reader | `2271627c6b8053691470509ea31aac7766f0d49595a16200f25cad2d63babce9` |
| Original protocol comparison reader | `9541d89b96a6f874f1f39263724ba526b08d6fc605e1cf2ffd51877c919ce44f` |
| Original A21 statistics | `a25dca7ca09c609bf6984050047b4bed752660bf6aa7f1c540cb113317b61b04` |

The two per-profile noise records are also hash-bound in [the machine-readable review](independent-review.json). Their bytes and all 138 distinct cell evidence files consumed by the retained result/extractor records were rehashed. The caller index is the already accepted `a48786a5…` source; the range reader and policy were unchanged.

## Actual population and identity

Weak-before means **ON `2e3995df8d86583ee9443348276ca8d918056bfc`**. Weak-after means OFF `4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4`, which was not exercised in this noise stage. The original main baseline `ea5fa528035d025bd7a28698ee7c71194432236c` supplied the fixed independent client build; it is not the weak-before role. The common application and driver source remains ON `2e3995df…`.

All six processes use the same Release / Native AOT server, common Native AOT client, loaded Server native library, TLS certificate, profile signatures and locked .NET 11.0.100 producer metadata. The measured package version is `0.1.0-perf01.recovery001.on.1`. Actual server, client and native-library bytes were rehashed against their recorded identities. Source inspection confirms exact HTTP/2 over certificate-pinned loopback TLS, protobuf equality/order/hash checks, terminal status and terminal trailer checks. No network-compression benefit is asserted; this stage uses identity compression.

| Measured component | SHA-256 |
| --- | --- |
| Server executable | `684cd580b54b58e0ae962dcb6175b6ff3d57c2d05aac92bf07377c4f47bef088` |
| Independent client executable | `4f08f8e5f1b999a712f91eb8528e5346b8367d0918bdad6a904865c17145f365` |
| Loaded Server native module | `4de9964f470fe0ed44304d623889d68a4c9754c37321ffaf5f703b4239c9dbc3` |
| TLS certificate | `7791e4ce73571b25ece18e56d6ace786a2db3ea820fdfc10402a364605b09c39` |

Each profile offers 16 calls/s with configured concurrency 4 and the unchanged guarded schedule of 323 calls per process. Service CPUs are 2–3; generator CPUs are 0–1. All recorded thread affinities match those sets. Unary alternates 64-byte and 65,536-byte payloads; streams cover server/client/duplex with 32 messages of 4,096 bytes. Each process has 24 warmup calls and 32 separate same-server recovery calls.

| Profile / repetition | Measurement UTC on 2026-11-20 | Elapsed seconds | Measured successes | Maximum dispatch lag ms | Observed maximum in-progress calls |
| --- | --- | ---: | ---: | ---: | ---: |
| grpc-unary / 0 | 22:32:27.968015–22:32:48.096123 | 20.128107351 | 323 | 9.582670 | 1 |
| grpc-unary / 1 | 22:33:03.401860–22:33:23.568448 | 20.166587687 | 323 | 6.423167 | 1 |
| grpc-unary / 2 | 22:33:38.873795–22:33:59.001026 | 20.127231596 | 323 | 6.836010 | 1 |
| grpc-streams / 0 | 22:34:15.692732–22:34:35.928979 | 20.236247168 | 323 | 7.330481 | 4 |
| grpc-streams / 1 | 22:34:54.012523–22:35:14.150634 | 20.138111290 | 323 | 6.294314 | 3 |
| grpc-streams / 2 | 22:35:31.479306–22:35:51.623695 | 20.144388788 | 323 | 10.077007 | 4 |

There are **1,938/1,938 measured successes, zero unexpected errors, 144 warmup calls and 192 recovery calls**. All 2,274 independent-client operations report correct content and `GrpcOK`; source-bound fixture checks include terminal trailers. Raw successful measurement totals are 21,933 request messages and 22,026 response messages, carrying 117,553,536 request payload bytes and 116,619,648 response payload bytes. Protobuf encoded-byte totals exclude gRPC framing, HTTP/2 and TLS overhead.

The six result hashes and six server PID/start identities are distinct. Their measured windows do not overlap. The largest dispatch lag is **10.077007 ms**, below the frozen 100 ms limit. Both original validity and service-standard flags pass, and independent calculations reproduce the calls, means, nearest-rank percentiles and resource values. The frozen service limits remain zero unexpected errors, arrival p99 ≤500 ms, sampled server RSS ≤256 MiB and each managed/native payload budget ≤64 MiB. Observed call overlap, especially unary's maximum of one, must not be described as sustained four-stream saturation.

## Independent range recomputation

For each listed observation the frozen range equals `max(process values) - min(process values)` over repetitions 0, 1 and 2. All 11 vectors reproduce exactly; there are no unavailable bands. The JSON preserves full precision. The decimal table below is a readable rendering.

| Profile / observation | Process values, in repetition order | Range |
| --- | --- | ---: |
| grpc-streams: grpc-client 4096 B × 32 p99 (ms) | 124.447689, 118.932505, 166.855115 | 47.922610 |
| grpc-streams: grpc-duplex 4096 B × 32 p99 (ms) | 203.806939, 171.858607, 246.240138 | 74.381531 |
| grpc-streams: grpc-server 4096 B × 32 p99 (ms) | 185.489903, 149.472707, 209.850642 | 60.377935 |
| grpc-streams: Sampled managed allocation (MiB/s) | 21.2522020868, 21.4956094689, 21.6407034722 | 0.388501385464 |
| grpc-streams: Server CPU (% of one core) | 9.74518499227, 10.3688471783, 11.0928755034 | 1.34769051115 |
| grpc-streams: Sampled server RSS maximum (bytes) | 94494720, 92917760, 91533312 | 2961408 |
| grpc-unary: grpc-unary 64 B × 1 p99 (ms) | 28.414108, 41.587687, 38.537136 | 13.173579 |
| grpc-unary: grpc-unary 65536 B × 1 p99 (ms) | 37.488555, 35.541979, 39.711202 | 4.169223 |
| grpc-unary: Sampled managed allocation (MiB/s) | 17.294952829, 17.2921096439, 17.331754743 | 0.0396450990764 |
| grpc-unary: Server CPU (% of one core) | 3.77043895455, 3.66798395373, 3.82462216201 | 0.15663820828 |
| grpc-unary: Sampled server RSS maximum (bytes) | 54185984, 54042624, 57479168 | 3436544 |

The separate five original A21 arrival-mean bands also reproduce exactly using `max(1,000 ns, maximum process mean - minimum process mean)` and relative noise zero. They are not p99 bands. Neither kind of three-process range is a confidence interval.

CPU is derived from the first/last in-window process tick samples and their monotonic interval. RSS is the maximum of 20 in-window observations per process, not an exact resident-memory peak. Managed allocation uses the first/last of 21 measurement-phase `GC.GetTotalAllocatedBytes(false)` observations and their sampled interval. These values describe each whole profile, not an individual RPC.

## Retirement, scope and public projection

Both finite owners completed with exit code 0, retired successfully, sent no signals and left no owned processes or owner children. The noise owner ran from 22:32:25.805317 to 22:36:06.037661 UTC; the offline range owner ran from 22:41:15.380147 to 22:41:15.493546 UTC. Every cell passed same-server recovery, all recorded idle gauges returned to zero, and final server state was `Disposed` with zero pending requests and zero retained managed/native bytes. Process exit alone was not used as the drain proof.

The ordinary noise profiles contain no cancellation or deadline probes. Their functional/protocol obligations remain in the existing separate coverage. These six short processes grant **zero long-run credit**; the main 30-minute acceptance obligations are unchanged. No OFF/direct timed population or capacity decision is supplied by this record.

The following exact public files were independently checked. `samples.json` preserves all six process resource rows, all 15 scenario samples, five A21 bands, the original identity/configuration/timestamps and the complete 11 frozen vectors. `resource-ranges.json` is the actual unchanged freeze, not a reserialized substitute. The README accurately states the scope and limits.

| Public file | SHA-256 |
| --- | --- |
| `README.md` | `645b81dd722dc53542758f6e057db523659d9bc5575b70a8833b4922fccec18c` |
| `samples.json` | `280b6ea42fc53aca8d043082da577c126596da627d5f16e6fc8c46b48c5afe4b` |
| `resource-ranges.json` | `6737006913586e9983e3337d6bcee08d6c015b3a622f1f606d4217011be2ceb8` |

The already frozen policy still requires publication and exact readback before comparison. That step is pending at this review. The review itself does not authorize retention, alter a threshold or transfer historical timing credit.
