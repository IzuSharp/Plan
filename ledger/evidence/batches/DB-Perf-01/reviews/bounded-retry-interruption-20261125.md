# Bounded retirement retry: not retained; interrupted execution recovery

## Decision and scope

The isolated one-additional-retry-opportunity candidate is **not retained**.
The already observed SQLite results cannot satisfy its frozen tail-noise screen,
even if the missing third pair were available. No replacement or additional
measurement is authorized by this disposition. This is a decision under the
predeclared local screen, not a statistical-significance or product-fault claim.

The original local execution environment subsequently reported unavailable.
The mixed run has eight complete successful cells, one incomplete cell, and
three unstarted cells. It is not a completed twelve-cell validation.
The isolated source has **not yet been restored**, because the execution
environment cannot be accessed. No version of this candidate was pushed, merged,
published as a normal candidate package, or substituted into the formal campaign.

The current public product remains [db0f674](https://github.com/IzuSharp/Korda/commit/db0f674f3849fa86f69d86eea2c830dc1c84da83),
with successful [ordinary CI 45511550343](https://github.com/IzuSharp/Korda/actions/runs/45511550343).
The newer overall recovery and complete original eight-segment verification are
in the [00:01 handoff at Plan 1b3a29d](https://github.com/IzuSharp/Plan/blob/1b3a29d25ce0e4f11b54db2a04ba94127665aaa9/ledger/evidence/batches/DB-Perf-01/handoff-linux.md).
That original matrix still measures after producer `3d5ba3f`, not `db0f674`.

## Finite experiment and the observed stopping bound

The frozen experiment uses the unchanged 35-case public Fluent application,
ordinary PackageReference Native AOT, both real providers, default runtime
settings, concurrency 4 and fixed offered rates. It planned twelve interleaved
20-second cells with separate idle windows. Its prior rule requires all three
SQLite pairs to improve p95 and p99, with the smallest absolute paired improvement
greater than the larger within-side three-process range.

Four complete SQLite cells have these previously observed scheduled-latency
histogram upper bounds, including queue time:

| Cell | Side | Successful operations | p95 ns | p99 ns |
| --- | --- | ---: | ---: | ---: |
| 1 | Before | 3877 | 27525120 | 56885248 |
| 2 | Candidate | 3877 | 26214400 | 52953088 |
| 5 | Candidate | 3877 | 27000832 | 55312384 |
| 6 | Before | 3877 | 31457280 | 62128128 |

Pairs are 1/2 and 6/5. Independent integer arithmetic over these observed values
gives:

| Metric | Smallest observed paired improvement ns | Observed before range ns | Observed candidate range ns |
| --- | ---: | ---: | ---: |
| p95 | 1310720 | 3932160 | 786432 |
| p99 | 3932160 | 5242880 | 2359296 |

Adding a third pair cannot reduce either existing within-side range and cannot
increase the minimum paired improvement. The strict required inequality is
therefore already impossible for both metrics. No extra cells are needed to
attempt to rescue this candidate. The PostgreSQL and CPU three-process-median
rules remain incomplete and are not marked passed.

These values were read from the original execution output before the environment
became inaccessible. The arithmetic above was recalculated separately afterward.
It is not a new hash/read of inaccessible raw result files. No final freeze
manifest for the mixed run was successfully produced; do not attach an earlier
build freeze SHA to these later measurements.

## Actual interrupted execution boundary

Cells 1–8 completed with exit 0 and observer errors 0. Their planned, attempted,
sent, started, completed and successful counts agree; failed, rejected, retried
and oracle-failed counts are zero. All 35 cases have validated consumption.
Each completed consumer's six exported live owner counters returned to zero.

The eighth completed cell ended at 2026-11-24 23:49:39.709466 UTC.
Cell 9 (SQLite before) has a started record and partial resource samples, but
no result or final command receipt. Its last observed resource timestamp is
2026-11-24 23:49:53.336001 UTC. Cells 10–12 never started.
The original execution session could not be resumed; the executor then reported
transport disconnection and the environment was explicitly marked unavailable.
The termination cause of cell 9 and any product responsibility remain unknown.

The private PostgreSQL cluster has no observed final owner/shutdown receipt.
A retained pidfile and a later connection refusal in a different/current visible
execution namespace do not prove orderly retirement in the original domain.
Do not delete that pidfile, signal an unverified reused PID, or synthesize a
cleanup receipt. Verify process identity and the actual execution domain first
when access returns.

## Previously completed gates remain separately bound

The executed predecessor gates include 6,333 callback assertions; 683 async
assertions with 108 created/released owners; and 8,925 race assertions over
72 finite orders. Three additional real-native Pending scenarios cover a late
signal, timer recovery and queue rejection. Five isolated fault modes passed.
These finite checks do not establish all possible concurrency behavior.

The twelve public allocation processes completed before this interruption.
Their producer manifest is SHA-256
`5d3f4d684f8fefb5242a1a9ec8f7b7a9454d4388dbfcd37629081b583b42b600`.
It records, per process, 128 refill windows totaling 65,536 B (512 B each),
zero raw bytes for the measured buffered and empty-sync windows, and six final
live-owner counters at zero. Complete queries still allocate.
The new independent follow-up audit was interrupted after reading two of the
twelve raw files; it must not be represented as a completed twelve-file audit.
No full-query or whole-framework zero-allocation claim follows.

## Exact local recovery references

The isolated worktree is
`/home/agent/DB-Perf-01-worktrees/Korda-DB-Perf-01-retirement-retry`.
Its base is `7cf6c7db4957fdb27ea408b56d52ce1b28235a5b`.
The only production delta is `src/Interop.Callbacks/CallbackCoordinator.cs`;
the candidate file SHA-256 is
`babc308dd6ce87166a75b3467a94b17d921dbc2915a06ec651630d77d64454e6`,
and its frozen patch SHA-256 is
`e6443cbe841a27608781f89059c23350b80e758539c5daa68cae835b49855003`.
Associated finite-test changes remain in that isolated worktree.

The experiment root is
`/home/agent/DB-Perf-01-experiments/retirement-immediate-retry-001`.
Read `mixed-results-001/manifest.json` first. Preserve all completed cell
directories, the incomplete ninth directory, and `mixed-runtime/postgres-data`.
The fixed plan is `design/execution-plan-v3.json`, SHA-256
`25ba602a1fc31bbef4369e4211c368e99278f26f7f2d4ae9189365093d65138e`.
The allocation receipt is `allocation-results-001/manifest.json`.

On restoration, inspect current remote heads and worktree state, freeze the
existing partial bytes and unknown cleanup state, then restore only this
isolated production delta after verifying its source/patch identity. Do not
modify the shared public product, repeat completed measurements, fill missing
cells, or reuse the old 159-file build-failure checkpoint as a later result freeze.
The three already prepared readable continuation-flag records remain unpublished;
their existing source-only method is public at Korda `0410da7`.

This single readable record preserves the observed interruption and stopping
decision. It does not resume any previously rejected upload queue, publish the
private build archive, replace the full handoff, or claim final batch acceptance.
The final matching campaign, remaining reviews/evidence publication, normal
merges, main checks, automatic preview and downloaded-public-NuGet consumption
remain outstanding.
