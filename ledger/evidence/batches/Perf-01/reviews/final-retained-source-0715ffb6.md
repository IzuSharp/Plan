# Independent recovery review of final retained source 0715ffb6

Status: source and small-receipt review; no build, test, workload or acceptance
execution by this reviewer. The integration owner controls all measured
resources. This report neither approves the reviewer's own new adapter nor
claims final performance acceptance.

## Reviewed identities and limits

The clean product primary and separate `Perf-01-after-002-linux/NativeWeave`
checkout both identify commit
`0715ffb6376b1ae08259ad7e2cb30ff0320d83e7`, tree
`cd0a6022e0115c22f133aedf6c801d9244640523`. The preceding candidate was
`ada13b865ec5d19876745498f6f51d8ad2367399`; the measured isolated no-extra-retry
experiment was `5ac6620015f5096bc3c800b1d95f60af898a097b`.

Actual reads covered the commit diffs, full changed lazy-waiter path, original
A07 test restoration, six-process numerical report, existing regression impact
proposal, build-after-002 recipe, component verifier command interfaces,
canonical workflow, Task04/Task07 scripts and relevant A20/packaging code.
Unchanged R1/R3 implementations retain their existing independent reviews; this
recovery report does not claim a new complete review of those implementations
or a new audit of every raw operation.

| Input | SHA-256 | Observed relationship |
| --- | --- | --- |
| `src/Interop.Async/AsyncOperation.cs` | `cc5dc3815a9db4e7e6ecb381f3ec561c7f6dd901d738601895cfed6aa6aea60c` | Exactly restored to pre-R2 bytes |
| `tests/Interop.Async/Program.cs` | `a581eaaf15c47e376e0cb6f8c5012ba32ae4adc0c2375884bd085674d13444f0` | Exactly restored to pre-R2 bytes |
| `tests/Interop.Async/Fixture.cs` | `0b4e135a084d0695aaba5e5f16b694761226127b9633c0757c3ae1e162ae0d40` | Exactly restored to pre-R2 bytes |
| `src/Data.Streaming/TypedStream.cs` | `5c917739cb57a42240ae6f708a2410c5c0f2d89d36e8bbc49ffc1aaa070c9091` | Retains reviewed lazy waiter; unchanged from both ablation variants |

The complete difference from experiment `5ac6620` to final `0715ffb6` is the two
test restorations. No runtime source differs between those two commits. Their
separate package and executable identities must nevertheless be preserved;
runtime-source equivalence does not rename measured bytes or establish final
application throughput.

## Findings

**PERF01-RECOVERY-001 — resolved in source, execution pending.** The extra
post-result `Signal()` and its per-operation budget are absent. The `Pending`
branch retains `RequestRetry()` with the original timer and ownership rules.
The four tests of the removed optimization and exclusive helper hooks are
removed by exact restoration. Original cancellation, result-before-native-quiet,
rejected scheduling, duplicate result, discarded-task and final zero-owner
assertions remain. Removing those feature-specific tests does not waive A07.

**PERF01-RECOVERY-002 — no source defect found in retained waiter.** The
enumerator's `_moveActive`, `_moveCompletion` and `_closed` transitions occur
under the existing gate. Disposal allocates a completion only when a move is
active; finishing the move clears/captures it under the same gate, then completes
outside that gate. Multiple disposers share the existing active-move completion,
and a closed enumerator cannot admit a new move. Existing asynchronous cleanup,
cancellation and transport ownership remain. Fresh B06 execution must establish
the interaction with restored AsyncOperation retirement.

**PERF01-RECOVERY-003 — final artifact gap remains.** At this review's initial
inspection the nine-step `build_after_002.py` source was prepared, but no
`after-002` producer output or execution receipt existed. It correctly requires
the clean final commit, unchanged thirteen application inputs, repository SDK
identity, version `0.1.0-perf01.after.3`, normal B24 packages, and frozen consumer
drivers. Earlier after-001 observations remain attached to `ada13b8`; all final
affected comparisons and after long runs need actual after-002 binding.

**PERF01-RECOVERY-004 — current CI coverage must be read narrowly.** CI123 run
`44690977311` is associated with `0715ffb6`. The job API showed the A20 job and
canonical source/package/AOT plus fresh-SDK steps successful while Task04 was
still in progress. This is an observation of job status, not an artifact audit
or whole-workflow acceptance. The final actual checkout tree, receipts, command
outcomes and logs must be verified by the integration owner. Reuse matching
completed CI evidence instead of duplicating those exact gates locally.

## Pinned standard and API applicability

The Plan pin and product adoption manifest identify Design commit
`c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`, standard version 1.0.0, SHA-256
`78f2aab2212fbbc49267e7827231a3f64cf9b840206d0acdc33768417e2dbcac`.
The reviewer read the pinned standard and verified these bytes. Its sections
5–6 preserve terminal-result/native-quiescence separation, cancellation and
bounded disposal; section 10 requires a justified no-public-API applicability
record while still checking changed internal boundaries.

The final retry removal changes internal scheduling and test expectations only.
It adds no public symbol, overload, default, nullability, exception category,
native ABI, consumer Rust requirement or package dependency. No API baseline or
guide signature edit is justified for this removal. Existing compiled API/XML
and actual consumer gates remain required for affected components. The lazy
waiter's public `IAsyncEnumerable`/concurrent-move/disposal semantics remain
inherited; its allocation cost change needs measured evidence, not a new API.

## Minimal remaining component verification

Use the unchanged verifiers once on final clean source; preserve new unique
output directories and any failed attempts. Existing full CI A20 and canonical
execution can satisfy those two obligations after actual artifact/source audit.
Task04 includes A07 main fixture execution from packages, but its own script
explicitly says it does not replace component receipts; it does not run every
A07 child failure mode. Task07 composition does not execute the full domain
component verifiers below.

| Gate | Required action | Reuse boundary |
| --- | --- | --- |
| A07 | Full `tests/Interop.Async/verify.py` | Restored runtime and tests need exact final execution |
| A08 | `tests/Interop.Execution/verify.py` | Executor joins retire through AsyncOperation |
| A18 | `tests/Engines.AsyncProof/verify.py` with actual A17 receipt | Unchanged A17 static-cost reference may be reused; HTTP async consumer is fresh |
| B06 | `tests/Data.Streaming/verify.py` with pinned Design and PostgreSQL binaries | Lazy waiter and underlying retirement must be combined |
| B15 | `tests/Server.Application/verify.py` | Actual Host operations and retained JSON tests |
| B16 | `tests/Server.Streaming/verify.py` | Backpressure/cancellation/ownership through AsyncOperation |
| B17 | `tests/Server.Native/verify.py` | Narrow recorded input inventory omits the transitive Async source; old managed execution is insufficient |
| B18 | `tests/Protocols.Grpc/verify.py` | Use actual fresh native hash/source; unchanged native-component receipt is supported, old managed package summary is not |
| B19 | `tests/Protocols.Mcp/verify.py` | Actual Host retirement and retained shutdown regression |
| A20, canonical | Reuse completed final CI when actual artifacts bind the same final tree | Keep ASan/UBSan/LSan and existing full verifiers unchanged |
| A02, A17, A23 | Existing scoped evidence | Their unchanged executed scopes do not use the removed AsyncOperation scheduling change; retain original source identities |

B17's output must remain inside its checkout because its verifier records
artifact paths relative to that checkout and writes a legacy default cost file.
B19 can use the exact freshly built `target/debug/libnativeweave_server.so`
without a composed-manifest argument; its optional composed receipt requires
its documented snake_case schema and accepts no B24-manifest substitution.
B18 must use the existing supported native-component receipt and fresh package
execution, with no old `--package-summary`. These facts avoid the already
preserved earlier launcher/receipt failures; they do not change any gate.

No new 30-minute credit, formal comparison credit, final performance claim,
public package release, merge approval or required-check waiver is granted by
this review.
