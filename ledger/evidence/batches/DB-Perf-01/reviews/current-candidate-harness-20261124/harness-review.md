# DB-Perf-01: read-only comparison of d665c0c and the frozen local patch

## Decision and scope

The remote commit `d665c0c9629922cfff0e48fa535d6f21393f8162` already contains an independent implementation of both requested fixes: unconditional rejection of workload oracle violations and task-owned PostgreSQL cgroup CPU accounting. Do not apply the older 18-file patch wholesale. Its completed implementation and rejected/successful test attempts remain preserved as recovery evidence.

This review made no source, branch, Plan, workflow, or database changes. It performed no build, test execution, or workload. Only this independent review directory was written. One existing historical preflight sample was also independently recomputed offline; no new runtime was launched. Thirteen remote source files were retrieved at the exact commit; every saved byte stream reproduces the Git blob identity reported by GitHub. `input-hashes.json` binds their SHA-256 values and the API observations. Runtime conclusions below are deliberately narrower than source conclusions.

## Frozen local work already completed

Base: `e8e7a4e93366e17cff0996807a6ab53f993ac4c3`.

The 18 local harness files were frozen before this read-only task. Parent owns their local recovery commit and canonical-worktree transition. No local proof is transferred to the remote d665 source or its binaries.

| Artifact | SHA-256 |
| --- | --- |
| `../active-harness-fixes-003/freeze.json` | `b9bd6a486baa6eb72a07cce8be588d7d06c763e689a5247f35e2669e5f30eb3d` |
| `../active-harness-fixes-003/active-harness.patch` | `98b3e0c96523bfbff2cd516268b7e9ccd164c0d8cad84966ed7215f7f8d8ff8e` |
| `../active-harness-fixes-003/local-validation-summary.json` | `f86dcf38366f82315a1056e0d87a753dc065d1c89cdf6c1865d4a36b0bad7f2e` |
| `../active-harness-fixes-003/independent-review-002/review.md` | `6c212db0f4531c8c368a90a9e810b4b01c88694885135771071d9bba81efea26` |
| `../active-harness-fixes-003/final-review-closure.json` | `f111e237918fff27a1533d82fa20c332a817a093b256d89a4897994786519648` |

Completed local checks, retained without rerunning:

- 34 controller checks, including hard failure below the permitted ordinary error rate, final-sample failure propagation, and synthetic cgroup identity/reset/reap accounting.
- Native AOT reader control 007: three independent processes, 72 paired windows, 360,000 operations and 60,480,000 whole-process allocated bytes per side. All per-window process and current-thread totals agree. Synchronous controls use 0 B/read; actually pending controls use 224 B/read on both sides. Each side records 12 generation-0 collections and no generation-1/2 collections across all measured windows. These are explicit warmed harness controls, not real-provider or full-framework zero-allocation proof.
- Rejected 003/004 controls with +8 B per pending read, and 006 with an unattributed +752 B whole-process first-window delta in each process, remain in the archive. They were neither subtracted nor rounded away.
- Clang 23.1.5 syntax/type check for final local native source SHA `16436bde7a40ccba58c5f4c3948563766d040dd04917dc5646ab2b8efdcd1a81`: passed. No local final linked consumer or actual PostgreSQL cgroup claim.
- Independent review 002 closed the three concrete findings from the first uncommitted snapshot. Full external-consumer and real-VM cgroup gates remained outside that local proof.

## Oracle propagation at d665

| Boundary | Observed source behavior | Fixed source |
| --- | --- | --- |
| Discovery | Process-lifetime atomic failure count; first bounded diagnostic; never reset between recovery phases. Native increments before allocating its error detail. | `managed/Shared/CorrectnessOracle.cs`; `native/main.cpp` 135–200 |
| Row/digest validation | Both managed workers throw through the oracle factory. Native row, typed value, affected-row, transaction, SQL shape, and successful-protocol sequence mismatches call `oracle_violation`. | Both `Measurement.cs`; native 606–725, 813–827, 1016–1073, 1096–1113 |
| Reader failure plus cleanup failure | Typed/contract failure is recorded before retirement. The failure-only helper preserves the primary stack or both exceptions. A cleanup failure independently invalidates the command. Null-reference failures in fixed typed JSON are explicitly included. | `ReadStream.cs`; `CorrectnessOracle.cs` |
| Public consumer result | Before/after and process-lifetime counters plus first failure are emitted; setup/warmup failures can produce a failure sidecar. Recovery retains sticky state. | Both `Measurement.cs`; `OfferedLoad.cs`; `RecoveryMeasurement.cs` |
| Controller | Missing/malformed counters, any total greater than zero, or non-null first failure are rejected before SLO evaluation. Nested offered interval must agree with the enclosing interval. `meets_slo` independently requires explicit correctness and zero oracle failures. | `campaign.py` 214–277, 508–511 |
| Source regression coverage | Tests cover result/offered/cleanup/prior-phase violations, malformed or absent counters, and failure of the direct SLO predicate. These tests were read, not executed in this review. | `test_controller.py` 293–326 |

The remote solution is based on a sticky process counter rather than our per-worker hard-integrity fields. This also prevents an exception overwritten during later cleanup from receiving correctness credit. A counter may record the same causal contract failure at more than one observation point; it is an invalidation count, not a one-to-one failed-operation count.

A remaining narrow source difference exists at `native/main.cpp:1046`: rejection by `PQsetSingleRowMode` still throws ordinary `std::runtime_error`, whereas our patch marked that state-contract failure as hard. No such occurrence was observed in this review. It is not evidence of a current row/digest mismatch, and this review does not recommend interrupting the live campaign on that unobserved path.

## PostgreSQL CPU and retirement at d665

The authoritative server CPU has been changed to cumulative `cpu.stat` values in a new task-owned child cgroup. The shell launcher enters the exact group before it execs PostgreSQL; PostgreSQL descendants inherit it. This avoids a post-launch migration interval. The implementation does not alter host controller permissions or resource limits.

The source validates the group path, device/inode, original PostgreSQL PID/start ticks, relevant controls, live member ancestry, absence of nested groups, and raw nondecreasing integer CPU counters. It checks unchanged parent controls at creation and closure. Every observed server interval must supply this accounting; the live process-tree values remain separately labeled diagnostics. Missing/unreadable group identity or counter evidence cannot fall back to live-tree success.

Cleanup is also fail closed:

- Final process sampling failure populates `finalSampleError` and `shutdown_error`.
- PostgreSQL is still stopped and joined; the group must be empty and removed.
- The controller rejects `shutdownError`, `cpuGroupError`, and `finalSampleError`.
- The before-clients to empty-after-owner-join cumulative delta is recomputed from raw snapshots.
- Raw `wait4` user/system lifetime values are retained alongside the cgroup lifetime values. Their label expressly explains the differing launcher boundaries; the source does not require artificial equality.

Relevant fixed source: `run.py` 214–420 and 525–616; `campaign.py` 452–560 and 713–722. Tests at 36–201 include synthetic disappearing-backend/tree-counter behavior and owner-record binding.

The d665 source does not contain the older patch's dedicated probe that independently observes a backend's positive CPU, records its PID/start identity, waits for its exit, and compares a cumulative lower bound afterward. Its runtime gates instead bind each real seed/cell's complete owner lifetime, cumulative group snapshots, and wait4 cross-record. This is a validation-design difference, not absence of the cgroup fix. This review has not downloaded or independently recomputed the current run's raw VM cgroup evidence, so it does not certify that runtime gate as passed.

Server sampled CPU is explicitly scoped to whole sample-acquisition intervals inside the client steady-plus-drain interval. Unsampled boundary edges are not extrapolated. It must not be relabeled as an exact cutoff-only 1,800-second CPU observation.

### Existing historical runtime observation

A separate, already downloaded preflight archive was inspected offline: SHA-256 `bc4f1195eba7fcd518120e8e3c61b0e1f6304f8a76dd1992ba7d3da4ebc1cb39`, member prefix `runs/postgresql/capacity-korda_before-4/attempt-00/`. This is not current run 45461269267. Its exact selected raw bytes and a narrow recomputation receipt are preserved under `historical-cgroup-sample/`.

Among 41 resource samples, backend identity PID 17218/startTicks 72414 had user/system CPU of 3/1 ticks at monotonic timestamp 724607585266. At 739731277274 that identity was absent from both the process-tree observation and group members. All adjacent group identities and cumulative user/system/usage counters remain stable/nondecreasing. The group was empty after PostgreSQL join, removed, and the owner exited with code 0.

Raw group user CPU was 1,850 microseconds before clients and 3,309,546 after join; raw system CPU was 19,428 and 1,845,272 microseconds. The raw wait4 lifetime cross-record was 3.317197 user seconds and 1.844218 system seconds, with its differing boundary scope preserved. This demonstrates a real workload backend retirement observation while group CPU survives; it does not isolate that backend's exact contribution or certify the current run. The selected result ELF identity is `d4fc9c4f4f0d861a78f56a9417c09c37c0827e6fe7a0ee37a67c455aa7d0dec3`; it is not silently rebound to d665.

## Live run observation

Run: <https://github.com/IzuSharp/Korda/actions/runs/45461269267>

The run API binds attempt 2 to d665, branch `task/DB-Perf-01-linux`, and sole active workflow `.github/workflows/db-perf-campaign.yml`.

At **2026-11-24 18:52:23 UTC**:

- Prepare job 138685089344: completed successfully.
- Measure job 138688263792: in progress.
- Step 5, “Admit this VM and freeze noise, capacity and offered load”: in progress.
- All eight sequential long-segment steps: pending.

Thus no long segment had entered at the latest observation. This is a timestamped job-state finding, not a claim about future run state or completed campaign acceptance. The workflow executes all eight long steps sequentially in that same measure job/VM after short admission, with a checkpoint after each step. Prepare-job success alone is not evidence of eight effective long segments, final package identity, or full acceptance.

## Integration guidance

Retain the frozen local patch and its failed/passing test history as recovery material. Use d665 as the active-source baseline. Do not overlay the 18-file patch or reactivate the archived 36-case workflow. Review actual current-run receipts and exact producer identities before assigning performance, allocation, CPU, long-run, or publication credit. Any later focused integration should target a demonstrated remaining gap and receive its own source/binary binding.
