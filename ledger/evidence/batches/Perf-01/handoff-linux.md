# Perf-01 Linux x64 handoff

## Current state — 2026-11-19 21:16 UTC

**2 of 10 required long groups are accepted**, both before optimization: HTTP
and gRPC at 115 calls/s. Their credited effective load totals 3,604.192232408 s.
No C#/Rust product-runtime optimization has been applied and no product speedup
is claimed. All five accepted before groups remain required before the first
runtime optimization. The current user instruction authorizes this performance
implementation task; older research-only wording remains historical.

The first codec before long attempt was interrupted by an execution connection
reset. Its completed operation records cover only 1,021.572841888 s of measurement;
196,142 measurement operations and 3,861 warmup operations are recorded. Operation
199993 has no completion in the observed ID prefix. Recovery, final result,
normal exit and drain are unavailable. It receives **zero duration credit**.
Original files and the stale original supervisor receipt are unchanged. The
separate audit is `checks/before-codec-long-interrupted-001/summary.json`.
A fresh full codec attempt002 is being prepared; no partial durations are joined.

Database work is also incomplete. The original PG144/s long attempt had correct
business/persistence results but invalid generator lag. A fixed-package 120 s
automatic/deferred scheduler-GC pair passed 104 checks, with an observed memory
cost. Subsequent deferred calibration consistently passed only 25/s and failed
the unchanged 144/s long-selection gate; SQLite was not started. A measurement-
only sampler offload candidate is now being prepared in an independent worktree.
It has not cleared calibration or long acceptance.

## Immutable inputs and workspace

| Input | Exact identity |
| --- | --- |
| Before product main | `ea5fa528035d025bd7a28698ee7c71194432236c` |
| Starting Plan main | `8afa0311f45ab8a8157fc45c51e95a0b17dd09f2` |
| Locked Design | `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9` |
| Original immutable drivers | `ce2a3c75cbd535490897d062b6cbb7c095408307` |
| DB scheduler-GC wrapper | `0b2af54419ecf6a11ec83a45725b1c5fbbaeb0d0` |
| Global freeze SHA-256 | `85061c4e01b28fc72a5b20519ce2d8c01d79cae271238ba36e0a3465b0b8f4a3` |
| Adopted gRPC long amendment002 SHA-256 | `2c4d5a0a00cf2f763e4641043f7d6908319ea4d3e7fdbaf2760039bc6808b513` |

The authoritative gRPC amendment hash is recorded in its own immutable file and
published receipt; verify that file before execution. Do not reconstruct any
command from a prose table. The same rule applies to all commands below.

Primary worktrees are `ROOT/.worktree/Perf-01-linux/{NativeWeave,Plan}`, branch
`task/Perf-01-linux`. Before product and original drivers are respectively under
`Perf-01-baseline-linux/NativeWeave` and `Perf-01-frozen-drivers-linux/NativeWeave`.
The immutable GC-wrapper worktree is `Perf-01-db-generator-fix-linux/NativeWeave`.
Root owns shared runtime integration and the only measurement queue.

All timing uses the existing `ROOT/perf01-evidence/timing.lock`: application and
DB CPUs2,3, generator CPUs0,1, source/supervision CPU8. Long windows exclude other
local work; builds/profiling never overlap formal timing. The frozen Linux x64
host has nine virtual CPUs, EPYC9V74, kernel6.18.57. SHA-256 of **stripped** kernel
boot-ID text remains `d19b8f888214efe7966ce4acd9313f5a8536f876c1e35f78201081604986df45`
after this interruption. Physical-host scheduling and power controls are
unavailable; no bare-metal isolation is claimed.

Source `ROOT/perf01-toolchain/env.sh`. Pinned versions are .NET SDK11.0.100,
Rust1.100.0 and PostgreSQL18.0. The missing SDK was restored from the verified
official archive; original dotnet SHA-256 remains
`bb015c1dbaec79f69addde16893609baf880ccdc5931db354d40096769010e3e`.
Previously measured standalone AOT binaries are unchanged. Original failures and
recovery evidence remain separate. Do not replace pinned dependencies.

## Accepted before long results

| Group | Effective seconds | Recorded operations | Ordinary successful/s | p99 ms | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| HTTP | 1802.091185499 | 901051, including45051 expected cancellations | 474.929480 | 260.565040 | Accepted; recovery32/32, idle60s and zero residual owners/requests |
| gRPC115 | 1802.101046909 | 207243, including4145 cancel and6218 deadline probes | 109.246215 | 152.456566 | Accepted; recovery32/32, idle60s and all10 owner/request/queue gauges zero |
| PostgreSQL | 0 credited | Earlier144/s long invalid generator lag | — | — | Replacement pending |
| SQLite | 0 credited | No accepted before long | — | — | Pending |
| Codec | 0 credited | Attempt001 interrupted | — | — | Full attempt002 pending |

HTTP dispatch UTC: 15:31:55.221462–16:01:57.321053. gRPC dispatch UTC:
16:57:34.317798–17:27:36.421953, all on2026-11-19. Details and exact source,
package/native identities are in `checks/before-http-long-001` and
`checks/before-grpc-long-002`. Original gRPC128 failed with17 ResourceExhausted,
5 unexpected cancellations and1 missing-header/terminal-response record; it is
not rescued by a later steady portion. Its data remain immutable.

All ten long segments must run at least1800 effective seconds with correctness,
SLO, generator-lag, resource and drain gates. Warmup, recovery and idle do not
count. The current total is only2/10; all five after groups remain unstarted.

## Immediate queue and ownership

1. Finish the codec interruption audit and preserve fresh-output attempt002
   commands. Independent preparation uses `Perf-01-codec-resume-linux/Plan`.
   Only the before output directory and corresponding verifier receipt may
   change; keep rate192, workers2, queue64, inflight256, duration1802, warmup20,
   recovery10 at1/s, idle60, deadline1000ms, max lag100ms and the exact before004
   manifest/corpus. Root reviews and starts it; the original run stays untouched.
2. Complete/review the measurement-only observer candidate in
   `Perf-01-db-observer-linux/NativeWeave`, based on immutable0b2af544. Keep
   existing sampling cadence, fields and gates. One in-flight read per sampler;
   shield the same Future from its first await, join through repeated cancel,
   publish its last completed row exactly once, then propagate cancellation.
   Preserve actual worker phase/read times and conservative RSS-window overlap.
   Include thread/Future CPU/RSS cost in the fixed-package diagnostic. No old
   failed result becomes valid through a driver change.
3. Run the four independently reviewed gRPC per-mode profiles from
   `grpc-mode-profiles/commands.json` (SHA-256
   `81921bd9809844d54214f29f398058b68c8c6561991b06ee11f2b8fdb530d5f0`).
   They are ordinary unary/server/client/duplex resource profiles, not formal
   timing or long credit. No profile has run yet. Preserve before-v2 server,
   common client, TLS, identity compression, quotas and validation.
4. After the observer candidate passes finite ownership/cancel tests and actual
   fixed-package checks, freeze its explicit policy/source, rerun DB calibration,
   derive fresh noise from three complete confirmations, and bind the actual
   result to the next DB long amendment. Keep PG144/SQLite40 long rates. The
   failed25/s selection is diagnostic, not accepted clearance or a server limit.
5. Complete all remaining before longs. Only then apply small runtime candidates,
   build actual after packages, run affected correctness/AOT gates, interleaved
   before/after/direct-Rust comparisons and capacity sweeps, then all five after
   longs using the same accepted drivers and fixed load configurations.

## Actual diagnostic findings and candidate boundaries

The before public `ZlibCodec.Descriptor.Inspect(null)` profile completed three
independent processes of1,000,000 steady calls each: **2624 allocated B/call**;
wall638.684064/614.873301/595.548022ns per call. It uses actual before packages
and native mappings. The new test-only source is published in NativeWeave
`d859b79eedb87dfc372be6c07e516d173c96124b`; CI44611817761 passed. This identifies
an allocation candidate, not an after gain or a sampled allocation stack.

The database calibration audit passed121 checks. Its40/s cell completed1201/1201
operations but p99 was8464.161657ms and failed the service standard. The30/s and
27/s cells were invalid for generator dispatch lag. A measured219.076152ms
synchronous target sampler span overlaps a lag cluster; this supports testing
observer offload, not an established explanation of all tail latency. Database
execution, lock wait, pool wait and contemporaneous host steal/iowait attribution
remain unavailable. The earlier120s deferred-GC pair increased sampled scheduler
peak RSS by44.2578125MiB; do not call it memory-neutral.

Reviewed runtime hypotheses are in the existing source notes: default Inspect
cache after validation; resolver lifetime/OS-reference ownership; lazy typed-
stream disposal waiter; bounded A07 retirement retry; bounded JSON initial
buffer; exact-E weak gRPC encoder scratch reuse. Preserve explicit nondefault
Inspect validation, cancellation, ownership, credit limits, thread safety and
all public contracts. Root integrates shared code. Drop regressions/unproven
complex changes. No runtime candidate has yet been applied.

The existing profile limitations are explicit: no usable perf/ptrace allocation
or CPU stacks. Source attribution and timing brackets are not stack samples.
gRPC supports **identity only**; independent A17 codec numbers are not negotiated
network-compression gains. Public domain-package release and24h/72h runs remain
separate deferred tasks.

## Evidence, publication and resume

Public PRs: [NativeWeave#19](https://github.com/IzuSharp/NativeWeave/pull/19) and
[Plan#23](https://github.com/IzuSharp/Plan/pull/23), both still draft. Public Plan
checkpoint `b46991bcbb4fb6fccfe3b657405238d631d99c28` follows `afcdc555` and contains
strict numerical Inspect and failed-DB-calibration summaries. Their fixed-commit
contents were fetched successfully. It does not contain every newer local
source or detailed audit. Inspect summary SHA-256 is
`2dc5e7f7ecbb699c898aae2d6818587be951b40043f602cdbca2a46011e18693`;
full local DB numeric audit SHA-256 is
`f612890c0323e082f110d600e84248f56e0c9d02b439198886780798dd0caa50`.

Raw and detailed controls remain under `ROOT/perf01-evidence`; original frozen
commands, hashes, summaries, source and checklists are in this batch directory.
Full raw archive publication and a mixed checkpoint were blocked by automatic
scope review. Those payloads are not retried in another encoding/channel.
Publish only genuinely narrower authorized synthetic numbers/checklists or
reviewable task artifacts. Never upload process-registration tokens, TLS private
keys, credentials or unrelated data. Do not describe local archives or orphan
Git blobs as publicly retrievable artifacts. Original raw files are retained.

The previous full local handoff is preserved at
`ROOT/perf01-run/handoff-before-scope-029.md`; immutable local commits retain
all preparation history. This current handoff is a concise continuation record.
On resume, inspect it, actual branch/PR heads and the original receipts first.
Reuse an accepted30-minute group only when binaries, cases and configuration
match. Never infer completion from a lost tool session or a stale running flag.

Finish all required gates and independent technical review before ready/merge.
Do not impersonate a separate GitHub approver, bypass protection, or publish
unrelated releases. After authorized merges, confirm both repos' actual CI and
the existing normal HelloWorld preview trigger. Deliver a brief Chinese result
with measured before/after/Rust gaps, retained/reverted changes, all ten durations,
actual commits and retrievable evidence; no completion is currently claimed.
