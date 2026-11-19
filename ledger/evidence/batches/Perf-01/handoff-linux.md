# Perf-01 Linux x64 handoff

## Current state — 2026-11-19 23:12 UTC

**3 of 10 required long groups are accepted**, all before optimization: HTTP,
gRPC at 115 calls/s and codec attempt002. Their credited effective load totals
5,406.296300913 s.
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
The independently reviewed codec attempt002 configuration is published at
`f2dda486fd378519c3eab4c20f3bc81026be24e6`; all nine files were fetched and matched.
The fresh full attempt actually completed at22:17:58.861155Z with driver and
independent verifier exits0. All346005 measurement operations succeeded;
credited effective duration is1802.104068505s. No partial durations were joined.
The original retry supervisor receipt is
`ROOT/perf01-run/before-codec-long-002-execution.json`, and its accepted verifier
receipt is `ROOT/perf01-evidence/long/before/codec-002-verification.json`
(SHA-256 `a49b986b50dd01d0e35265d3bfb892f665aeae0416d7f9747cddc2fd6ba38635`).
The strict numerical report is complete under `checks/before-codec-long-002`;
summary SHA-256 is `488fb6155d5f891fe1668c3bc4f9e92c259ffd4881d599c17592a2f70226acf7`.
It preserves all32 partitions, four action/interface aggregates and30-second
resource buckets. The producer's actual offline extraction exited0, and root
reviewed the reporting source plus independently checked partition totals,
aggregate byte/ratio arithmetic and all report-file hashes. Original raw files
and acceptance are unchanged.

Database work is also incomplete. The original PG144/s long attempt had correct
business/persistence results but invalid generator lag. A fixed-package 120 s
automatic/deferred scheduler-GC pair passed 104 checks, with an observed memory
cost. Subsequent deferred calibration consistently passed only 25/s and failed
the unchanged 144/s long-selection gate; SQLite was not started. The measurement-
only sampler candidate `b846bb43816c8a3515fcd1e7fb512f142a1a6be3` received actual
independent source review against the seven published files at
`77205c1e11e3a19082fa374502885f488078c401`. Core cancellation/lifetime handling
passed. A subsequent two-file correction `583e9d70f6974b91d865fd67a9eb7dc9d27dacb1`
passes the same conservative RSS window to the three generator roles.
Root integrated the changes on current published parentd859 in the separate
`Perf-01-db-observer-measured-linux/NativeWeave` worktree. Its actual local/public
HEAD is `a3ce0f6295c535b0a81de95fc0f98aa19deb259c`, complete tree
`eb6b61e7c159c343513f7a50359f1a6c09f8df77`. The full remote tree and all seven
changed-file contents were checked equal. Ten finite tests and the whitespace
check actually passed on this exact checkout at22:24:27Z; source/tree stayed
unchanged and clean. The generator RSS follow-up was independently closed.
See `checks/database-observer-offload-001/source-and-finite-checklist.json`.
The local b846 lineage and remote772 tree differ in other verifier files; they
are not the measured source identity. The fresh synchronous/threaded load pair
actually completed against a3ce0f6 after independent source review. No new DB
calibration or long acceptance has been granted.

The reviewed observer diagnostic pair ran from22:54:00.025163Z to
23:01:28.735570Z. Both driver processes, both offline cell audits and the final
pair audit exited0. The actual supervisor receipt is
`ROOT/perf01-run/database-observer-fixed-before-pair-001-execution.json` and the
sibling `-supervision.jsonl` preserves progress. Receipt SHA-256 is
`c64debb45b30388809373695dfda3e59714571debf3db8801b4672a54c7de796`.
Final equality analysis SHA-256 is
`bfca614ae18a47237df7f1fdea5daed54a364cd087a12118fc3937aaedee130d`.
Both sides completed17282 measured operations,8641 cycles and8641 pages,
with all expected row values matched. Independent durable totals were8777 per
business table before recovery and8809 after32 recovery operations. Each idle
observation covered60s; registered process cleanup passed without forced signals.
Both original valid/SLO flags are true, with no invalid reasons. The
configuration SHA-256 is
`2f7a7149d3f8de59a90b1cd569032bb16a203957c4807062e8a5330c6f1368e0`,
supervisor SHA-256 is
`4a3a30d8b74c905b419ca6d71e8c059f6ea888dbbfa2b9aef58455c22e680d40`,
and auditor SHA-256 is
`f8013d23a12b5e0a4acb0e2befa800a10120353729330eaad59bc7e6b76bdd43`.
The source preparation is local Planecd530cb, integrated as25bb6f8; its independent
review is in `checks/database-observer-equivalence-001/preparation-001`.
All48 input pins were checked and both sides use identical PG144/C16/120s
before-product workloads with explicit synchronous/threaded observer policies.
The synchronous/threaded arrival p99 values were68.575553/73.439022ms,
maximum dispatch lag21.823064/15.139320ms, and successful throughput
143.945136160/143.923746726op/s. Application sampled peak RSS was
44982272/46891008B; scheduler peak RSS116379648/117608448B. Scheduler CPU
was10.58/12.29s over119.490688952/118.921159540s sampling spans. Both
deferred-GC policy scopes recorded zero cyclic collections and restored the
original policy. This short pair did not reproduce the earlier timing failure
and does not prove a product gain, memory neutrality or30-minute heap stability.
It earns zero formal timing/long credit. The independent evidence review and
strict numerical projection are complete under
`checks/database-observer-equivalence-001/results-001`; public-summary SHA-256 is
`46a3d151e66fff044ea6f082a4be0a03cd6956037e1bd982b904a0491c7904f2`.
Root also independently cross-checked 283 reported scalar/resource fields.
The threaded/deferred policy is adopted prospectively for fresh DB calibration
and matching noise qualification only. It has no diagnostic failure whitelist:
all three confirmation processes must pass the original validity and SLO gates.
PG144/s and SQLite40/s long targets remain unchanged. The new portable
calibration/noise source is in preparation; no other measurement is running.

Automatic publication review rejected the full14-file source/configuration/test-
receipt bundle because of extensive absolute workspace/toolchain/cache paths
and operational metadata. No successful tree/commit/ref was returned for that
attempt, and that payload is not retried through another encoding or channel.
The materially narrower numerical workload/check checklist is published at
Plan `0cd7d9b9cf86ab0587b9882f1de90b698e98b383` and was read back exactly.
Reviewed local source and configuration remain unchanged and committed; the
user-authorized local diagnostic continues. The full source-publication item is
still open. The narrower public checklist commit0cd7d9b passed Plan CI
run44632649728. The earlier codec report and integrated observer numerical checklist
are published at `c1076ee564597451e5415c24eda5d95387ed7d18` with all seven files
read back equal. Do not describe the blocked full bundle as retrievable remotely.

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
| Codec | 1802.104068505 | 346005, all successful | 191.994948 | 105.719745 | Accepted; recovery12/12, idle60.077663s and normal owner drain |

HTTP dispatch UTC: 15:31:55.221462–16:01:57.321053. gRPC dispatch UTC:
16:57:34.317798–17:27:36.421953, all on2026-11-19. Details and exact source,
package/native identities are in `checks/before-http-long-001` and
`checks/before-grpc-long-002`. Original gRPC128 failed with17 ResourceExhausted,
5 unexpected cancellations and1 missing-header/terminal-response record; it is
not rescued by a later steady portion. Its data remain immutable.

Codec dispatch UTC is21:46:34.974014–22:16:37.078450 on2026-11-19; its actual
dispatch span is1802.104435880s. The independent credit uses the smaller ordinary-
operation lower bound. p50/p95/p99 are1.096052/27.814088/105.719745ms. Target CPU
is1160.68s /64.405051% of one core; sampled target peak RSS is120487936B. Maximum
dispatch lag is46.976085ms with zero over50ms. All3861 warmup and12 recovery
operations also succeeded. Actual before004 native identity remains unchanged.

All ten long segments must run at least1800 effective seconds with correctness,
SLO, generator-lag, resource and drain gates. Warmup, recovery and idle do not
count. The current total is3/10; all five after groups remain unstarted.

## Immediate queue and ownership

1. Publish the completed strict numerical codec002 report and preserve its actual accepted
   receipt. Attempt001 remains interrupted with zero credit. The accepted load
   remains rate192, workers2, queue64, inflight256, duration1802, warmup20,
   recovery10 at1/s, idle60, deadline1000ms, max lag100ms, before004 manifest and
   fixed corpus. Preserve these exact settings for the after long group.
2. Finish the reviewed diagnostic pair configuration in the independent
   `Perf-01-db-observer-pair-linux/Plan` worktree, using the actual measured
   a3ce0f6 checkout for both sides. Both explicitly select the same deferred GC
   policy and synchronous/threaded resource policy respectively; keep the
   before package, PG144/C16,120s,W16,recovery32,idle60 and full durable oracle.
   Include thread/Future CPU/RSS cost. Preserve any control-side service/timing
   failure as invalid; continuation requires complete correct outcomes, identity,
   persistence, resource limits and normal drain. The original driver/verifier
   gates are unchanged and the pair receives zero formal or long credit.
3. Preserve the four completed gRPC per-mode profiles from
   `grpc-mode-profiles/commands.json` (SHA-256
   `81921bd9809844d54214f29f398058b68c8c6561991b06ee11f2b8fdb530d5f0`).
   The four before profiles completed at21:28:10Z with all16 command exits0 and
   all323 calls per mode successful. Existing-reader validation passed with only
   expected profiling ineligibility. After replication remains required; before
   profiling is complete and adds no formal timing or long credit. See
   `checks/grpc-modes-before-001`.
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
checkpoint `a6616a1876de93395522e98f19bbe83099ef6f57` includes the gRPC mode
numerical report and merge/preview review, following the reviewed codec retry
atf2dda486, f2b2ca88,07226391,b46991bc andafcdc555. Its paired-integrity CI
44623801574 passed at22:02:32Z; all six changed files were read back and matched.
It also contains
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
Git blobs as publicly retrievable artifacts. Original raw bytes are retained.

At 23:06:41Z the five large inputs from the invalid original PG long attempt
were retained in the already verified lossless archive, after a new complete
byte-for-byte comparison against every uncompressed original and every pinned
compressed/raw chunk hash. Only the uncompressed duplicate copies were removed;
4,279,460,020 bytes were released. The original acceptance remains false and
duration credit remains zero. Small original metadata and all other runs are
unchanged. The local archive is
`ROOT/.worktree/Perf-01-raw-archive-linux/Plan/ledger/evidence/batches/Perf-01/raw/before/postgresql-001-raw8m-001`;
its manifest SHA-256 remains
`8f4669483b3965599657513a06ca81a73a77a9ce0e9fd5a16e2df67a3285491d`.
The actual retention receipt is
`ROOT/perf01-run/invalid-pg-cold-retention-001.json`, SHA-256
`335ddc02ca7cbf0ae39f1ebcde001de180eb35f4868275f907a81c61104e95e3`.
Use the existing `pack_evidence.py restore --bundle <archive> --output <fresh>`
before any future full raw replay of that failed run. This local retention does
not establish remote recoverability. Free workspace space after retention was
20,879,200,256 bytes; recheck before subsequent large builds or long runs.

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

## Completed before gRPC mode profiling — 21:28:10Z

The four ordinary modes each completed323 calls, with no unexpected errors or correctness failures; recovery, retirement and final zero gauges passed. Actual whole-server allocation observation rates were16.306950MiB/s unary,512.446451MiB/s server-stream,21.053005MiB/s client-stream and518.345020MiB/s duplex. Brackets were19.785026586/19.750669434/20.033393419/19.490230838s. They are whole-process sampled deltas, not exact bytes per call or stack attribution. Public projection source and numbers are in checks/grpc-modes-before-001; summary SHA-2565349d95853b31b72d2857cd313be76fcf94b9115c7ebfe711b5cc9a0c454674a. No product-runtime optimization or new long credit is claimed.
