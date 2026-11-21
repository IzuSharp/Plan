# Perf-01 independent review: weak reuse, actual comparisons and capacity

**Evidence verdict: ACCEPT. Optional weak writer reuse: REJECT under the frozen policy. Final product acceptance: not granted.** The numerical projection is faithful to the retained records. Four resource vetoes reject retention independently of the capacity observations. A separate native retirement failure observed in ON remains unlocalized in lifecycle code shared with OFF; removing the weak buffer alone is not evidence that it is fixed. This record does not select `4ae2e15f…` as final.

The review used source reading and bounded, standard-library calculations over existing evidence on the control CPU. No product modules were imported and no build, test, service, timing load or remote action was performed.

## Exact evidence and prior gate

| Input | SHA-256 |
| --- | --- |
| Complete 18-process comparison index | `ce145c98e585c19180c00e76536dc25ff1df9d3253f305831d5989c6530e37ee` |
| Finite comparison execution | `c602093d8b7e72fb90712b091653e450adf2aef62a180f837278812516e69ef3` |
| Actual resource screen | `9c968657aae3b7d45d218393144222b7bbfbc263922225b0389e31add7e2636e` |
| Finite screen execution | `d53c25e12e32b9432d43a2ce85efe6f392f61592f3fc42138037eae17b08f898` |
| Finite ON capacity execution | `211180723391c0175f807e0708f15de7768ad6941b56bfddc90f16587c6effb5` |
| ON capacity controller | `386ca7bf24ca7412c9403df3788466cf8ca6f0095995455298fdfe0fb7fbd06c` |
| ON capacity selection | `d517b4c8be174aa27690bcc39202c48bf840b261c9a4ce4c5f654d3e106c6ab9` |
| Finite OFF capacity execution | `5beafee75537bc4146cd8f8e9718a1cc3b3b3f2ffbc4cb2a24322d2277846b97` |
| OFF capacity controller | `1e6bc63efcc5a2a6709d868dc542158845cd73e0377c841a3d49bf1a69b6226d` |
| OFF capacity selection | `75879649f17ef528e70295bc0d04bee9de393e5e3da03b84ae9466b02dfae789` |
| OFF terminal and continuity record | `f12686b9359eccbba78d464ca596cd71f7c538ba4bb8f4b465b5797bbb1ce510` |
| Frozen weak-reuse policy | `0399d704c04e625412c8a365c6e0b071588d3059632dfcda8d6937fa429b3cc9` |

The earlier six-process noise index and resource freeze remain unchanged and are bound in [the machine-readable independent review](independent-review.json). Their accepted publication at Plan commit `abc974b50552e07fe4a44b5c0e711f6fabec4abc` was read back before all four reviewed stages. Each finite caller binds that receipt and the previously accepted independent review. All four outer owners completed with exit code 0, retired without signals and left no owned processes or owner children. An outer owner's successful completion does not turn an invalid inner measurement into a valid one.

The reviewer rehashed **1,028 distinct retained cell evidence files**, checked actual executable/native identities, recalculated raw outcome counts, ordinary business counts, message/payload totals, arrival percentiles and sampled resources, and reproduced all five original 2,000-draw seeded A21 bootstrap decisions. The 46 fixed-load/capacity process identities are distinct, and all measurement windows are nonoverlapping. Original values remain exact in the projection; independent derived whole-profile rates can differ only by floating-point summation rounding.

## Fixed-load comparison: 18 valid processes

The before role is **ON `2e3995df8d86583ee9443348276ca8d918056bfc`**; after is **OFF `4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4`**. The common application/driver source stays at ON `2e3995df…`; the independent client is the fixed EA-main-produced Native AOT client. The third role uses the previously pinned direct Tonic fixture. The two NativeWeave roles load the same actual Server native-library hash and different AOT executables. These are weak-reuse experiment roles, not the main baseline/final pairing.

All 18 fixed-load processes are valid, meet the service standard and pass recovery/disposal. All **5,814 ordinary calls succeed**, with zero errors. The same profiles, 16 calls/s, configured concurrency 4, guarded 323-call schedule, real HTTP/2 + TLS, certificate, client, payloads, CPU allocation and limits apply. There are no intentional cancellation/deadline probes in these two fixed-load profiles. The p99 columns below are equal-weight means of three process percentiles, not pooled percentiles.

| Scenario | ON p99 ms | OFF p99 ms | Direct Rust p99 ms | OFF minus ON p99 | Original A21 mean decision |
| --- | ---: | ---: | ---: | ---: | --- |
| grpc-client 4096 B × 32 | 121.218379 | 149.001531 | 4.859621 | +22.919917% | inconclusive |
| grpc-duplex 4096 B × 32 | 229.327981 | 181.790832 | 5.709801 | -20.728892% | within_band |
| grpc-server 4096 B × 32 | 180.224892 | 177.628131 | 4.925817 | -1.440845% | within_band |
| grpc-unary 64 B × 1 | 34.121362 | 29.883991 | 4.898251 | -12.418529% | inconclusive |
| grpc-unary 65536 B × 1 | 32.460615 | 34.638773 | 6.679744 | +6.710158% | inconclusive |

The five A21 decisions contain no demonstrated OFF arrival-mean improvement: three are inconclusive and two within-band. This does not remove the separate p99/resource vetoes. No direct-Rust capacity search is claimed.

## Frozen retention policy: four reproduced vetoes

For a veto metric, the policy rejects ON if either its equal-weight mean or maximum exceeds OFF by more than the original fresh ON-only range. Allocation is descriptive and cannot compensate for a failed veto. All four results below independently reproduce; no threshold or sample was changed.

| Observation | ON minus OFF mean | ON minus OFF maximum | Frozen range | Trigger |
| --- | ---: | ---: | ---: | --- |
| Streaming duplex p99 (ms) | 47.537149 | 79.638704 | 74.381531 | maximum |
| Streaming sampled RSS peak (bytes) | 46432256 | 41115648 | 2961408 | mean and maximum |
| Unary CPU (% of one core) | 0.0360613379751 | 0.262873884888 | 0.15663820828 | maximum |
| Unary sampled RSS peak (bytes) | 5510485.333333 | 15810560 | 3436544 | mean and maximum |

ON reduces streaming whole-profile CPU and sampled managed allocation, but its mean sampled process-peak RSS is **44.28125 MiB higher** than OFF. The recorded stream allocation means are approximately 21.54 MiB/s ON and 351.68 MiB/s OFF; they are sampled whole-process observations, not exact bytes per RPC. The source-level buffer tradeoff is real, but the policy does not allow those benefits to offset the four vetoes. Resource sampling and three-process ranges retain their original limitations; ranges are descriptive, not confidence intervals.

## Capacity: preserve every failed and invalid point

Both unchanged capacity controllers completed: ON has 16 cells (12 qualifying, one invalid); OFF has 12 cells (10 qualifying, none invalid). The common seven-scenario mix has 95% ordinary RPCs and 5% cancellation/deadline probes, configured concurrency 64, four HTTP/2 connections, the same quotas and the same zero-unexpected-error service standard. Exploration requests 30 seconds; each retained rate has three fresh, valid 60-second confirmations. Capacity p99 includes successful expected probes; ordinary throughput excludes them.

| Role | Highest three-confirmation passing offered rate | Ordinary successful throughput in the three confirmations | Recorded higher failing bracket | Bracket width |
| --- | ---: | --- | ---: | ---: |
| ON | 216/s | 204.918835/s, 204.917535/s, 204.902865/s | 240/s | 24/s |
| OFF | 208/s | 197.484812/s, 197.548386/s, 197.476445/s | 224/s | 16/s |

ON's 8/s higher sampled offered rate is smaller than either recorded bracket width, and the brackets overlap. It does not establish a precise sustainable-capacity advantage. The original search bisects to its tolerance, then may step down by 10% after failed confirmation; it does not retune the paired 30-minute workload for these after-labelled experiments. `long_rate` remains null in both selections.

| Role / point | Valid evidence | Original outcomes besides successful checks | Qualification |
| --- | --- | --- | --- |
| ON, 256/s, ladder | true | 1 cancelled, 17 rejected | failed |
| ON, 240/s, confirmation-0 | true | 1 cancelled, 10 rejected | failed |
| ON, 240/s, confirmation-1 | true | 2 rejected | failed |
| ON, 240/s, confirmation-2 | false | 1 failed, 9 rejected | failed |
| OFF, 256/s, ladder | true | 2 rejected | failed |
| OFF, 224/s, refine | true | 1 rejected | failed |

ON's short 240/s refinement passes, but all three 60-second confirmations fail. Two are valid SLO failures; the third is invalid. It is preserved and excluded from successful-capacity qualification. The valid failures above the selected rate remain available; no generator-invalid observation is treated as a server-capacity ceiling.

## Invalid ON 240/s confirmation: two distinct observations

The invalid result is `b0c4a888ff53754bfa7a1baf9a749efb3c50f6653d90bb2fc2766ef4eb940e90`; its failed retirement receipt is `f92f77eaa607592bac400ca93b09df566ff034d264d219711360a5fe9cefcef0`.

**The concrete client failure is a missing expected initial-header marker.** Operation 9628 is `grpc-cancel`, reports `IntegrityFailure: Wait headers were not committed.`, receives zero response messages and has `intentional_cancellation=false`. Nearby calls include nine `ResourceExhausted` rejections. The original generic “response/protobuf/hash correctness failure” text is preserved, but it does not establish payload corruption or an observed terminal gRPC status for operation 9628.

The original client checks the marker immediately after `ResponseHeadersAsync`, before reading the stream/terminal status. A trailers-only error can therefore be classified at that assertion before its terminal status is observed. The lexical `using` still disposes the call when the assertion throws. The raw record alone does not prove which terminal status was present; it must not be rewritten to a speculative rejection outcome.

**The server also has a separate, real retirement failure.** Its idle gauges and final drain observation retain one retiring request and **92,096 native budgeted bytes**, with zero active/queued requests and zero managed payload bytes. The final retained gauge occurs at **23:19:52.506728 UTC**. The server closed receipt is absent. The adapter times out at the original 40-second wait for server stdout to close; the adapter result exit is 1, the enclosing driver exits 2, and the finite owner later completes/retirements successfully. All 32 same-server recovery calls pass, which does not establish that the retained owner was released.

The existing evidence does not identify the retained native request or correlate it to operation 9628. These two observations must remain separate. No leaked product process survives the finite owner, but process termination is not successful application-level drain.

### Shared-path assessment and source hypothesis

The ON-to-OFF source change removes only the optional weak reference and replaces writer-buffer reuse with a new exact-limit byte array in `NativeTransport.cs`. Cancellation, native body ownership, metadata cleanup and request retirement are unchanged. All 12 OFF capacity cells drain successfully, including its nonqualifying overload points. That is positive observed evidence; it does not prove an ON-only cause or a correction of the shared failure.

The shared Rust request lifecycle publishes `dispatch_done` through an AcqRel swap and `body_done` through a Release store. Each path then calls a helper that checks both flags using Acquire loads. Reads of the other flag that observe false do not establish a cross-thread happens-before edge. A missed conjunction is therefore a plausible one-shot cleanup hazard; the existing host reaper only inspects `fully_retired` and does not retry this metadata release. This is a source hypothesis, not an observed memory-order execution or a proved cause of the failed process. Possible late metadata publication is not excluded by the existing trace.

A second source observation narrows the investigation. The unchanged 32,768-byte header bound gives a 77,184-byte request metadata anchor without a binary-segment surcharge. Empty initial metadata reserves 1,024 bytes. The fixture's three successful duplex trailers serialize to 72 bytes and reserve `8 × 72 + 3 × 4096 + 1024 = 13,888` bytes. The sum is **92,096 bytes**, exactly the retained gauge. This supports a completed-duplex metadata hypothesis; it is not identification of the actual retained request. The gauge accounts for reserved native ownership, so its value should not be described as 92,096 bytes of corrupted message payload.

**Shared correctness clearance is not granted by this review.** An isolated diagnosis and appropriate regression evidence are still needed before final acceptance can claim this lifecycle failure resolved or safely isolated to a discarded implementation. No product change or diagnostic test is credited here.

## OFF continuity during orchestration-client replacement

The terminal continuity record binds the exact completed OFF execution. It records orchestration-client replacement at **23:31:36.097477 UTC**, availability of the original measurement session, unchanged boot identity, the original owner's two locks and no duplicate load. Those lock observations are attributed to the contemporaneous control record; the reviewer did not retrospectively observe live locks.

Independent raw checks support continuity across the affected OFF 208/s refinement: its measurement spans **23:31:28.932537–23:31:59.075856 UTC**, six process-resource samples surround the incident, and the largest adjacent sample gap there is **1.005105704 seconds**. Server/client/adapter/controller PIDs remain unchanged near the incident; their PID/start-tick identities also agree across ready, recovery and idle snapshots. The cell is valid and qualifying, the same controller completes all subsequent confirmations, and the original finite owner ends with exit code 0 and complete retirement. There is no evidence here of a restarted, duplicated or interrupted measurement, and this tool-client replacement does not invalidate the recorded OFF samples.

## Reviewed public projection and limits

| Public file | SHA-256 |
| --- | --- |
| `README.md` | `24e04497a5e092d59286cbb695735713cf690e05922c0fd1ddbbd9a78f2da83f` |
| `capacity.json` | `0cbc6d8862ed305878fd5eb683d3757a605e16d02b8a0c47569e2d4cab598a49` |
| `comparison.json` | `08978e38686a49df7f50ead6f61c5e5a4d0d48f9bb1ca38242d5a19788bdc84f` |
| `resource-screen.json` | `9c968657aae3b7d45d218393144222b7bbfbc263922225b0389e31add7e2636e` |

The projection retains all 45 scenario samples, 18 fixed-load resource rows, all 28 capacity cells and the original failure classifications. Its selected aggregates, resource vectors, identities, counts and invalid-operation details match the retained records. The resource screen is byte-identical to the original.

**Optional weak reuse is rejected; no final product is selected.** These are short comparisons and capacity confirmations. They grant **zero 30-minute credit**, and recovery completion remains **0/10** required 30-minute segments. Native allocation/copy/FFI totals and exact active HTTP/2 stream counts remain unavailable in these timed cells. Direct-Rust managed allocation is not applicable. No historical numerical samples or duration credit are transferred.
