# Protocol capacity: preserved incomplete owner and exact failure classes

The current final003 candidate is `2e3995df8d86583ee9443348276ca8d918056bfc`. This checkpoint preserves completed group selections and an interrupted direct-Tonic group; it is **not** completion of the entire capacity matrix or final product acceptance.

| Domain | Before sampled offered rate | Current candidate sampled offered rate | Direct Rust sampled offered rate | Current candidate vs before |
| --- | ---: | ---: | ---: | ---: |
| HTTP | 1,088/s | 1,036/s | 1,382/s, completed group selection | −52/s, −4.7794% |
| gRPC | 160/s | 144/s | Incomplete; no selected rate | −16/s, −10% |

Each completed selection uses the original profile, policy and concurrency 64. These are the largest rates passing the existing confirmation rule, not theoretical server bounds. Generator-invalid points remain invalid. Logical call rates include successful probe calls; ordinary business throughput is a separate population in the underlying controller. The current candidate's HTTP sampled rate is 346/s (25.0362%) below the direct group selection. No confidence interval or new statistical decision is inferred from this arithmetic.

## Interruption boundary

The after command completed both groups and retired its owned group and adopted descendants. Direct HTTP completed its own group controller at **2026-11-20 17:02:16.344163 UTC**, including three passing 1,382/s confirmations of 83,060 calls each. The later direct gRPC group was still evaluating lower confirmations when disk headroom became insufficient for continued recording.

Root requested Ctrl-C on the actual current execution session. The tool returned exit 130. The original outer receipt remains `running`; it did not record terminal retirement for the direct command, and was not edited to manufacture one. At the separate **17:18:12.997218 UTC** observation, the exclusive timing lock was available, the last two recorded server endpoints refused connections, and 305,508,352 bytes were available. These observations do not replace the missing terminal owner receipt.

The partial `direct-grpc-final003/15-confirmation-0-576` cell is excluded. No direct gRPC capacity or clean terminal drain is credited to it. The completed direct HTTP selection is preserved with this explicit outer-owner limitation. A fresh, reviewed continuation must preserve all original controls and recover only missing work after storage headroom is restored.

## Exact semantic inspection

During the idle window, an independent review inspected the six completed-operation files identified by the aggregate after/direct failures and matched their SHA-256 values to the original results. It selected eight IntegrityFailure events and two unexpected duplex Cancelled events, without rerunning or changing any sample:

- All eight IntegrityFailure messages are exactly `Wait headers were not committed.` Two are from NativeWeave and six from direct Tonic. Each records one request message and zero response messages. No selected event records a protobuf/order mismatch or a Wait stream ending normally instead of cancellation/deadline.
- The client checks the handler's `perf-started` header before consuming terminal status. Source permits a trailers-only pre-handler error without that header, but the actual status for these eight historical calls was not saved. It must remain unavailable; they cannot be relabeled ResourceExhausted or valid samples.
- Two NativeWeave duplex calls reported client RpcException status Cancelled, with request/response message counts **0/0** and **26/10**. Only the exception type was saved, not Detail or both direction outcomes. They remain unexpected failed calls of unknown cause, not intentional cancellations or ordinary rejections.
- The two cancellations completed before the last measured dispatch and approximately 133 ms before measurement end. Their lifetimes were approximately 0.997 ms and 182.057 ms against the configured 20 s client / 30 s server timeouts. The driver stops the server only after client workers, recovery and idle finish. The retained evidence does not support normal global shutdown or ordinary timeout as their cause.

The raw field named `wire_status` sometimes stores the client's exception-class label. The copied events preserve that original spelling, while `actual_server_terminal_status_available=false` explicitly prevents interpreting IntegrityFailure or a write-direction exception as an observed server trailer. The inspection identifies an observation limitation and actual failing calls; it does not prove payload corruption or identify a new source defect. See the [retained-source review and semantic addendum](../../reviews/final-product-source-2e3995df.md).

## Storage and credit

This synthetic numerical/hash checklist and its exact selected event values are retained with Plan Git history. Original controller, partial operation and resource files remain local in their original task paths, bound by the published digests. This checkpoint does not claim public upload of the complete raw journals. Original invalid classifications, incomplete owner state and missing details remain visible; no new performance or long-test credit is created.
