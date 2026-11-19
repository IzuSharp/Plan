# Perf-01 independent protocol harness source review

Reviewer: `/root/perf01_codec`, separate from the protocol harness author.
Review method: read-only source inspection; no edits to the author's worktree,
builds, functional executions, profiling or timing were performed by this
reviewer. Root's exclusive measurement window was respected.

Reviewed product test commits:

- Initial complete harness: `dfaf9469b02cc1af75708580397b94b18d22c7e0`.
- Final reviewed follow-up: `ae2f65fed0cf939a8fd79c3bc5e4975554569716`.

Outcome: **no remaining source blocker found in the reviewed scope** after the
follow-up. This is a source-review result, not a claim that the final direct
binary has been rebuilt, that comparison equivalence has executed successfully,
or that any 30-minute acceptance has passed. Those remain root execution gates.

## Scope and fixed source identity

Read `Client/Program.cs`, `Server/Program.cs`, `Shared.cs`, `adapter.py`,
`run.py`, both build controllers, the direct Rust service and fixture codec,
profile and relevant documentation. Cross-checked A21 `Oracle`, `RunState` and
percentile rules, product HTTP transport defaults, current-thread Tokio setup,
and B18 codec/request-metadata quota formulas. The direct codec's malformed
arbitrary protobuf semantics were not accepted as equivalent to B18; its
documented valid five-field fixture scope remains the comparison boundary.

The author's worktree was clean when the following hashes were read. Paths are
relative to `tests/Perf01.Protocols/` in the final reviewed test commit.

| Source | SHA-256 |
| --- | --- |
| `run.py` | `058af0c7f4fa22cd99a50ecd67f4eb17cd79786886d4f6898eff02f21ef05543` |
| `adapter.py` | `10c4a210d97f386b5b615e3ca8931a74bf4c3a9af5e6ef3360eee55c2103a48f` |
| `build.py` | `068e0f356ee8af3b18df3b5b480b5c3b94b3e296540727c95687ab21852682d3` |
| `build-direct.py` | `d7cc57670e364870ae20a872d03d572c3f8b91632d868535c717b0b5fedf807c` |
| `Client/Program.cs` | `6bfc40c993b7f02ffd4406606d78b692c298482cc786717cdd05316688a4ea4d` |
| `Server/Program.cs` | `c525bca37e6047ae42e412b9bb77efdb1d8f8e387b560b932fa20b641eb6ea03` |
| `Shared.cs` | `7cdf4d7cb1adf5a6ece590559297088991140edd2e706bbd62d06472e86642da` |
| `DirectRust/Cargo.toml` | `b6057805492c646b2f6602e8cf9bdf7e2efc70d2a01f37113e8e69f83152acc3` |
| `DirectRust/src/main.rs` | `728b96d149307032efe752b3c48995e0a985b08a3eca451a1505b91abdd0a0a9` |
| `DirectRust/src/fixture.rs` | `b1320c40997d60a39467c81fde3f3e40cf7712964e79632f48c85fff2ee9eb36` |
| `profile-v1.json` | `b523306d177fe23a9c32025fdb97fa8efb422a182320a64d8f037905e31efa6a` |
| `README.md` | `06182bed678e2e98a74c34d683a13b75edacd5036d117f12a884e093a6d205d9` |

## Findings and observed resolutions

| Initial finding | Resolution observed in final source |
| --- | --- |
| Thirty-minute flag used the scheduled span; initial dispatch lag could shorten the actual span | Planned arrivals include the declared lag guard; result records actual first/last dispatch and requires at least 1,800 seconds plus validity/SLO for full acceptance |
| Interrupted runs lost the request ledger and useful phase timing | Line-buffered dispatch journal is written before dispatch; `finally` saves partial request state, pending/outcome counts and actual partial span |
| No serving recovery check on the same live processes | Thirty-two separately counted low-rate calls run before the original client/server close, bounded to 60 seconds |
| Recovery correctness could fail the SLO while leaving `valid=true` | Follow-up validates recovery event status/value and propagates recovery operation correctness flags into invalid reasons |
| Pre-filling every request timestamp after selecting `origin + 20 ms` could create generator lag itself | Follow-up assigns each scheduled/deadline timestamp lazily within the dispatch loop |
| Build source identity represented the harness rather than the producing package source | Product/native producer commits and cleanliness are checked separately from driver commit; B24 closure package provenance is checked |
| Locks, copied sources and package archives were recorded but not all frozen for the cell | Prepare now includes copied sources, resolved locks, package/cache archive hashes and producer manifests in verified inputs |
| Application identity could change between before/after server builds | Common client executable and application/proto/project source hashes form comparison identity; NativeWeave server sources must match that common build |
| External Python generator/adapter CPU and memory were absent | One-second samples include controller and adapter alongside independent client and server |
| Independent operation JSON was loaded and grouped as full dictionaries | Summary streams operation rows; compact numeric arrays retain exact latencies/concurrency observations |
| Declared native/managed payload caps were omitted from the SLO | Summary checks sampled native gauges, common RSS/p99/error limits, idle owner/request recession and recovery outcome |
| Independent client hello did not verify Native AOT | Adapter requires `dynamic_code_supported == false` for the client as well as server |
| Stream protobuf checks omitted some fields | Server-stream, client-stream aggregate and duplex responses now compare full expected generated `Payload` values |
| Direct Rust TLS/header timers differed and omitted handshake/idle limits | Direct source uses matching ten-second timers, 64 handshake slots per listener and sixty-second idle policy |
| Direct gRPC reservation omitted request metadata floor | Direct reserves another 77,184 bytes per call, matching `2*32768 + 200*48 + 2048` for this fixture's metadata profile |

Root additionally required the direct Rust build to match the actual native
producer's generic x86-64 compiler policy. The follow-up clears `RUSTFLAGS` and
`CARGO_ENCODED_RUSTFLAGS`, records `x86-64-default`, and rejects the old v2 direct
manifest when preparing a final cell. The shared independent AOT client remains
explicit x86-64-v2. The direct dependency resolver checks every registry version
and checksum against the product Cargo lock, and the Release profile matches
thin LTO, one codegen unit, unwind panic and stripped debug information.

## Retained limits and execution gates

The direct comparator uses the same independent generated-protobuf C# client,
real loopback TLS sockets, fixture bytes and hashes, authentication token,
message/stream caps and native quota ceiling. Its typed fixture codec, lazy
Tonic buffer allocation and owned immutable HTTP slices are disclosed
implementation differences. Ordinary unknown protobuf wire fields are handled;
groups are explicitly unsupported. Do not use this fixture review to replace
the product's existing B18 malformed-input, authentication or broader protocol
acceptance.

The sample recorder distinguishes configured HTTP/2 limits, kernel socket counts
and measured independent-client calls in progress. It does not claim that a
socket count is an active stream count. Per-operation native allocation,
physical copies/FFI calls and scheduler switches remain unavailable in timed
cells. Managed/native gauges are sampled observations; they do not prove an
unsampled instantaneous process-memory maximum.

The final source requires common arrival p99 at most 500 ms, sampled server RSS
at most 256 MiB, zero unexpected errors and the declared payload caps. Expected
cancel/deadline probes are checked and counted separately from successful
business calls. Root must use the declared business throughput denominator and
preserve intended arrival versus dispatched/admitted/completed counts when
writing comparisons.

The A21 finite ledger currently permits at most 1,000,000 requests. At an
1,800-second duration plus guard, the maximum representable long-cell rate is
approximately 555.5 calls/second. If baseline calibration selects a larger long
rate, root must resolve and freeze that measurement bound prospectively; it must
not silently lower the after load or claim that an observation bound is target
capacity. Controller memory and dispatch lag still require actual observation
even after streaming the client summary.

Before using final evidence, root must rebuild the final direct Rust source with
the accepted flags, retain exact provenance, execute both routes' complete
correctness/retirement checks, and show unsaturated generation. Same-machine
formal timing remains exclusive. Keep failures and partial attempts, and grant
30-minute credit only to valid complete records for the actual reported binary,
fixture and frozen configuration. This reviewer has made no duration or
performance assertion from compilation or source inspection.
