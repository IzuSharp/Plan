# DB-Perf-01 — Linux recovery entry

## Current state

**In progress: immutable baseline acquired; first managed optimization passed scoped correctness and matching public-package allocation probes. Effective long-load segments: 0/8; accepted effective long-load time: 0 seconds.** No comparative throughput, latency, CPU, memory or whole-framework zero-allocation claim is established by this checkpoint. The first local experiment is not the final campaign candidate.

Read the [plan](plan.md), [allocation source audit](allocation-audit.md), [workload matrix](workloads.md) and [acceptance record](acceptance.json). All unexecuted workload and lifecycle entries remain pending. The original raw receipts, failed attempts, commands and hashes are retained under `preflight/`. A document or structural CI pass is not an execution or performance result.

## Fixed inputs and recovered workspace

- Korda baseline main: `771bc77cbd68d3f932b99ed2497c0697bbba5f02`; tree `ddc4ec36cdade1749127fe5d50cbbf218b2878e6`.
- Plan baseline main: `bc1956936ee77a997a016856c97def6aabc0bbc6`; tree `3dda25b1c0fd6ecb799d3c7359c68ef604b8f9d8`.
- Design reference main: `d23fc89fb7436911b3f5a39995c7edb710a7be0a`.
- Branch: `task/DB-Perf-01-linux` in each participating repository. Worktrees for this session are `/workspace/scratch/754bc732518e/Korda-DB-Perf-01-linux` and `/workspace/scratch/754bc732518e/Plan-DB-Perf-01-linux`.
- An earlier clean worktree at `/workspace/scratch/b94e2a0e0c3f` had the same two baseline commits. New environment and baseline-artifact files appeared there during this session without being written by this session or its reviewers. Treat it as potentially active elsewhere; do not reset it or overwrite its files. This session uses separate git repositories and worktrees. Re-read remote branch heads before any push; integrate new work instead of force-pushing.
- At initial recovery, neither remote repository had a DB-Perf-01 branch/PR and the requested Plan handoff did not exist on main. Korda #19 and Plan #23 are closed, unmerged historical Rust/Server work; none of their old load time is credited to this C++ campaign.

## Original candidate packages

The fixed-main [CI run 45356659607](https://github.com/IzuSharp/Korda/actions/runs/45356659607) completed successfully and produced both original `0.1.0-preview.3` candidates. The exact unsigned candidate archives were downloaded through GitHub. Their ZIP bytes matched the reported GitHub artifact digests:

| Provider | Artifact ID | Artifact ZIP SHA-256 |
| --- | --- | --- |
| PostgreSQL | `14903585207` | `f24a34a23122401816083a53113b6b416d11e6a7c73db6d46bc3c385d5227990` |
| SQLite | `14902997132` | `c49c4a971f8562383319323cd28e02c4aed38471bce877831e9dc26fbb54b8a5` |

Local acquisition: `/workspace/scratch/754bc732518e/baseline-artifacts/{postgresql,sqlite}/`. Each contains `release.json`, its standalone nupkg and the original producer's order-consumer evidence. These original CI logs are historical package-correctness evidence, not new performance measurements. The package and loaded-image hashes must also be recorded in each DB-Perf-01 consumer run.

## Execution environment and scope of current results

The recovered .NET SDK `11.0.100`, Clang `23.1.5`, CMake `4.3.3` and PostgreSQL `18.0` binaries were actually invoked. The tool paths are recoverable under `/workspace/scratch/82a414196324`; their source and archive identities must be checked before reuse. Direct loopback TCP was tested successfully. Creating an AF_UNIX socket returned `EPERM`; use ordinary single-process MSBuild options and a private PostgreSQL cluster with Unix sockets disabled. This is a host capability constraint, not a product change.

The visible process affinity contains CPUs 0–8. Dedicated measurement-resource ownership has not yet been established; another session appears active. Short capability and allocation probes can establish their stated boundaries, but elapsed time collected during concurrent builds is diagnostic only. Do not convert it into an uncontended performance comparison or a qualifying 30-minute segment.

## Actual preflight and first isolated optimization

The ordinary external `PackageReference` consumers ran as real Native AOT ELF
processes. The [before record](preflight/korda-allocation/summary.md) contains three
independent processes per provider, each with 128 complete queries per mode and
256 consumed scalar `long` rows per query. Measurement uses raw process-wide
`GC.GetTotalAllocatedBytes(true)` start/end counters; no empty control is subtracted.
Business DTOs, strings, lists and result arrays are absent in those scalar intervals.

The isolated lazy-join candidate changes only `TypedStream` production code. It
creates a completion join only when disposal actually overlaps a pending move.
The exact local producer is `28110ee03391831c737a54204730730a01b77a34`, version
`0.1.0-perf-lazy.1`. The experiment is distinct from the later remote candidate,
which also contains scalar validation improvements. Both provider packages retain
the byte-identical original native libraries. Every unsigned original package
member and every bound native input was checked before the repository's public
bundle composer and closure validator composed the new managed candidate.

[Matching before/after public-package evidence](preflight/korda-allocation-after-lazy-join/comparison.md):

| Provider | Complete 256-row path | Before raw B / 384 queries | After raw B / 384 queries | Before B/query | After B/query | Change |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| PostgreSQL | Dynamic | 26,711,088 | 18,033,528 | 69,560.125 | 46,962.3125 | -32.486734% |
| PostgreSQL | Parameterless prepared | 21,624,144 | 12,923,104 | 56,312.875 | 33,653.916667 | -40.237616% |
| SQLite | Dynamic | 26,712,560 | 18,033,648 | 69,563.958333 | 46,962.625 | -32.490005% |
| SQLite | Parameterless prepared | 21,623,952 | 12,933,248 | 56,312.375 | 33,680.333333 | -40.190174% |

Each row in that table consumes 98,304 total rows. Complete intervals include
construction/stream creation, final `false`, enumeration disposal and dynamic
query disposal; session acquisition and return are outside. Positive totals are
end-to-end allocations, not an invented exact framework-only attribution.

For each provider, the 384 before synchronous row windows allocated exactly
11,176 B for 127 rows each (88 B/row). Every after window allocated **exactly
0 raw B**. Across both providers, all 768 after windows / 97,536 rows were zero,
with matching empty controls also zero. This passes only the warmed numeric
batch-local synchronous path. Refills still allocate roughly 12 KB including the
new batch's first row; whole queries remain nonzero. Actual thread-changing await
resumptions and incomplete-await observations are recorded separately. All six
native owner categories returned to zero in all twelve before/after processes.
The private PostgreSQL clusters were stopped successfully with durability enabled.

[Internal and real-provider streaming checks](preflight/streaming-lazy-join/summary.md)
passed 46 deterministic lifecycle assertions, a separate exact 0 B / 65,520 row
regression gate, and 615 assertions across 60 real-provider cases plus six shape
preflights. Reused native fixture provenance is explicitly checked against 95
unchanged source/profile inputs. Certain cancellation/overlapping-disposal cases
retire a connection as unusable by existing semantics; release is proven, reuse
is not claimed for those cases.

The [native probe](preflight/native/README.md) actually exercised direct Clang
23.1.5 / libc++ / SQLite 3.51.3 and patched libpq/PostgreSQL 18.0 query consumption,
parameters, owned values, commit and rollback. The
[independent ORM probe](preflight/independent-orm/README.md) actually exercised
Dapper 2.1.79 / Dapper.AOT 1.1.0 with Npgsql 11.0.0 and
Microsoft.Data.Sqlite.Core 11.0.0 as real Native AOT applications. These establish
capability only. SQLite comparator compile-option alignment and complete mixed
business coverage are separate campaign obligations.

## Concurrent work reconciliation and comparison blockers

Another task worktree became active during baseline recovery. Its remote
production checkpoint opened PR37. This session preserved it, then added the
independently validated preflight probes by a normal expected-head fast-forward.
The local lazy-only experimental commit remains immutable for its measurements;
it must not be relabeled as the remote combined candidate. Re-read remote heads
before any mutation and use lease-checked fast-forwards; never overwrite an active
worktree or create a competing campaign/PR.

Two [independent snapshot reviews](reviews/concurrent-harness-snapshot-001.md)
and [native/stream review](reviews/concurrent-native-stream-snapshot-001.md)
identified concrete blockers in an uncommitted earlier harness, not defects
claimed to be merged product behavior:

- `per-operation` workers retained one setup session each, leaving only one free
  connection when `MaxConnections = concurrency + 1`; that can serialize the ramp.
- Korda `mixed` selected 30 reads while the native entry selected five; the minimal
  Dapper application had no matching mixed entry. Those receipts are incomparable.
- The old scheduler was closed-loop and did not represent a frozen offered load;
  native stopped on first error while managed continued.
- Native allocator statistics, physical packet observations and exact positive
  framework allocation attribution remained unmeasured.

The shared contract under `benchmarks/Database/campaign` is being reconciled with
all routes. Its independently generated 30 read oracles reproduce the existing
1,024-order SQLite result digests exactly; the expanded 8,192-order dataset and
PostgreSQL dialect SQL require fresh execution. Source-level synthesis is not a
business-case acceptance receipt. The [adaptation plan](shared-workload-adaptation.md)
keeps transaction writes, conflict, rollback, cancellation and early enumeration
as explicit remaining obligations.

The [dedicated-runner design](preflight/github-runner/design.md) describes one
Linux VM and one serial 8-segment campaign, separate from ordinary short PR CI.
The available GitHub plugin has no workflow-dispatch tool; normal explicit PR
activity triggers are being evaluated without changing access controls. No VM
admission, offered-load calibration or long run has occurred yet.

## Resume order

1. Check remote main/task heads and PR state, then compare this checkpoint and all pending local files. Preserve the fixed baseline and historical records.
2. Read actual preflight receipts and their source/executable/library hashes; reuse only matching results. Do not rerun completed probes just to recreate prose.
3. Reuse the completed original-package allocation baseline, matching lazy-join public-package experiment, independent ORM proof and direct native proof. Their minimal queries do not count as the 30 business cases.
4. Implement and validate the shared workload, dataset and result oracle, then establish short four-column baselines on isolated measurement resources.
5. Perform one evidence-backed production change at a time, then short regressions, composite comparison, all eight long segments, independent review and normal PR/merge/release follow-up.

## Release status

The canonical product review is [Korda PR37](https://github.com/IzuSharp/Korda/pull/37), observed as Draft at `f9f0d6438feb9b29a9fdac05f3c10bdc86ed5d85`. The earlier production checkpoint `a3ba5aded6677dcbb4f56c27ce79196bbbe18d0d` passed [CI45366971791](https://github.com/IzuSharp/Korda/actions/runs/45366971791); its descendant has its own CI and cannot borrow that status. No DB-Perf merge or automatic preview publication is claimed. Existing `0.1.0-preview.3` publication belongs to the fixed baseline. The owner already authorized normal compliant merges and publication verification for DB-Perf-01; do not ask again solely because older task text stopped for review.
