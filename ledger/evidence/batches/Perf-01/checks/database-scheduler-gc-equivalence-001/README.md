# PostgreSQL fixed-before scheduler GC policy equivalence gate

## Verdict and scope

The independent audit passed all **104 checks** for the two already completed
120-second cells. Both retain the same before product, frozen dataset, planned
operation mix, loaded executable/native hashes, independent persistence checks,
recovery and cleanup. The deferred scheduler reports zero cyclic collections
inside the complete original worker call and restores automatic GC on normal
exit. This supports a fresh, policy-bound database calibration. It does not
establish 30-minute resource suitability and claims no product performance gain.
**Formal long-duration credit: 0 seconds.**

The exact pair command document is `21b8f09254b41cbfe46f817d3fb61c0360b1470323b5191ef56c92e73c7d22a9`;
the executed supervisor is `b40dbb3ac829398e4ee1cef2995507414287ee1a61793e1b06cebc8407bbf3c5`.
The product remains before commit `ea5fa528035d025bd7a28698ee7c71194432236c`.
The measurement driver is clean commit `0b2af54419ecf6a11ec83a45725b1c5fbbaeb0d0`.
The pair changes only the scheduler GC policy and fresh output paths between
cells; each uses PostgreSQL, HTTP/1.1, mixed cycle/list, offered rate 144/s,
concurrency 16, seed 20261119, 16 warmup operations, 32 recovery operations and
60 seconds of idle observation. The existing 100 ms dispatch-lag, 500 ms arrival
p99, zero-unexpected-error and 256 MiB application RSS gates remain intact.

## Actual observations

The parent supervisor ran the automatic cell from 2026-11-19T19:26:44.672086Z
to 19:30:10.555156Z and the deferred cell from 19:30:10.557786Z to
19:33:37.207550Z. These are whole-command endpoints, including startup,
warmup, recovery, idle and postprocessing. Both actual process exits are zero.
Their effective measurement windows are 120.034394182 and 120.029942357 seconds.

| Observation | Automatic | Deferred |
|---|---:|---:|
| Successful measured operations | 17,282 | 17,282 |
| Cycle / list mix | 8,641 / 8,641 | 8,641 / 8,641 |
| Successful throughput (operations/s) | 143.975401 | 143.980741 |
| Arrival p50 / p95 / p99 (ms) | 18.464859 / 53.313690 / 123.159958 | 17.721849 / 49.848638 / 63.245867 |
| Maximum dispatch lag (ms) | 12.640345 | 19.613328 |
| Dispatch lag > 100 ms | 0 | 0 |
| Scheduler GC collections during complete worker scope | [1483, 134, 5] | [0, 0, 0] |
| Scheduler measurement CPU seconds | 9.91 | 9.63 |
| Scheduler measurement CPU (% of one core) | 8.302206 | 8.064448 |
| Scheduler measurement RSS peak (bytes) | 68,648,960 | 115,056,640 |
| Scheduler idle end RSS (bytes) | 77,082,624 | 123,506,688 |
| Target measurement CPU seconds | 47.53 | 47.06 |
| Target measurement RSS peak (bytes) | 53,190,656 | 53,407,744 |
| Application measurement RSS peak (bytes) | 50,946,048 | 42,700,800 |
| Independent durable rows per table before / after recovery | 8,777 / 8,809 | 8,777 / 8,809 |
| Recovery operations | 32 | 32 |
| Idle duration (seconds) | 60.001043022 | 60.001564541 |

These are one independent process per mode. The latency differences are retained
as observations, not a noise-qualified improvement claim. In particular, the
maximum dispatch lag is larger in the deferred sample; both samples meet the
existing 100 ms gate. The original failed PostgreSQL long sample remains invalid
and is not replaced or reclassified by this pair.

## Correctness, identity and lifecycle

The extractor streamed every raw observation together with the frozen dataset
and independently compared all 17,282 result values per cell, including list and
cycle contents, timing order, exact 6,944,444 ns schedule spacing and full outcome
counts. Both use dataset SHA-256
`ed18b71b187550b6c92f98057a5ecd1f56a6594719c94077e00717f4f87728bc`.
Each complete original outcome journal has 17,298 rows (16 warmup plus 17,282
measurement). There are no late/error records or unexpected provider exceptions.
The recorded independent SQL checks agree with 128 seed, 8 warmup cycle and
8,641 measured cycle commits: 8,777 rows in each of items, operations and outbox.
The same-process recovery adds 32 successful operations and independently checks
8,809 rows per table. The audit validates these existing independent query
receipts; it did not restart or query a database itself.

Both application closures report released consumer/database resources and a
Disposed server. The registered-process supervisor completed normally, recorded
no forced signals and no live owned processes after cleanup. No PostgreSQL
postmaster PID file remained. The actual scheduler PID/start identities
(44/4779427 and 421/4799975) agree among policy, process ownership and resource
samples. Both keep GC thresholds [700, 10, 10]; their policy, plan and source
hashes agree across actual receipts, frozen inputs and summaries. Restored
`gc.isenabled()` is true in both. Deferred restoration recorded one subsequent
Gen0 collection outside the deferred scope; restored enabled state alone does
not establish that every unreachable cycle was collected.

Actual loaded files are equal in both cells:

| Loaded artifact | SHA-256 |
|---|---|
| `NativeWeave.Reference.TaskService` | `6f2bd3e2b31422393d0e9543388f238226df2e3ab8f7e67c7f6b613a00e650d3` |
| `libnativeweave_server.so` | `4827a6ecc76f871e0b4828f4ff6fe23a0d0a4ca1c57c5fc89a10a8e4d83ffe69` |
| `libnw_database_postgresql.so` | `b0510d35c2b7b633a9aade7a5d3ad9a74498b54fbe23863c770881e38442a6f3` |
| `libnw_database_sqlite.so` | `7254f8e490f19637701d92523c2ba08e0cbdfdbe4c5f28173d4215b5f303da8d` |

## Resource cost and observation limits

Deferral increases scheduler measurement peak RSS by **46,407,680 bytes
(44.2578125 MiB)**. The idle-end difference is 46,424,064 bytes. These are
observed retained process memory differences, not cumulative allocation.
The application RSS bound covers the application; it does not silently extend
to the Python scheduler or PostgreSQL service. Generator roles are reported
separately, with raw per-phase sample counts, CPU counter spans, first/last RSS
and sampled peaks in `public-summary.json`. All three generator roles have
191 valid samples per cell, no identity or metric errors, monotonic CPU counters
and unchanged CPU affinity [0, 1]. CPU percentages use each role's actual sampled
span and one-core denominator; they are not total-host utilization.

The generator observer stops with the target, before the scheduler finishes
its final A21 replay and restores GC. The final sampled scheduler RSS is
77,201,408 / 123,641,856 bytes, but no continuous observations cover all replay
and restoration transients or live post-restoration RSS. Full-worker peak RSS
is therefore **unavailable**. The 17,282-entry plan is substantially smaller
than the 259,526-entry long plan. Neither this short pair nor its enabled-state
restoration proves full-long memory safety, memory neutrality or absence of a
later scheduling stall. Fresh policy-bound calibration/noise and a prospective
DB-only long amendment must retain these limits and validate the complete load.

## Evidence and reproduction

`audit_pair.py` is a bounded, source-bound reader of existing evidence. It uses
the unchanged frozen `verify_long.py` streaming reader SHA-256
`8034692b643f4dbb1385cd61e25c9d4d6f084d7b71268fec02411b5c2fcdbeb4`.
It does not execute a workload, build, test or database query. The actual analysis
ran on CPU 8 with locked Python 3.12.14 from 19:43:36.923581Z to
19:43:50.219173Z, exit 0. `analysis-execution-001.json` records the exact argv,
source/Python hashes and stdout/stderr hashes. The extractor SHA-256 is
`995a20370377f25a44dc57d08e14319cf207b9592fc0359b6c2a902d47b09292`.

`public-summary.json` contains only the actual comparison numbers, per-role and
per-phase resource aggregates, loaded-file basenames/hashes, and all 104 check
names/results. It is an explicit allowlist projection of original analysis
SHA-256 `5b0d75fed3ed26a06ed0d4ffd35196952eabfaf3627ec0bee93bb98acf981769`.
`project_public_summary.py` reproduces it; the projection grants no measurement
credit. Detailed control copies, full result summaries, process identities, raw
receipts and the complete original analysis remain local. They are not published
in this commit.
All original inputs remain unchanged under:

```
/workspace/scratch/01c249676f47/perf01-evidence/diagnostic/database-scheduler-gc-equivalence-001/01-automatic
/workspace/scratch/01c249676f47/perf01-evidence/diagnostic/database-scheduler-gc-equivalence-001/02-deferred
```

To repeat only this read-only audit when no exclusive timing window is active,
use a fresh output directory; never overwrite accepted evidence:

```sh
taskset -c 8 /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 -B   ledger/evidence/batches/Perf-01/checks/database-scheduler-gc-equivalence-001/audit_pair.py   --root /workspace/scratch/01c249676f47 --output /absolute/new/audit-output
```

`calibration-source-review-001.json` binds the subsequent calibration-only
source review, including the final unchanged-rate policy and exact root
supervisor. That source review itself ran no workload and grants no long credit.

## Publication boundary

Automatic approval review rejected the original process-registration tokens.
The token-free public projection was byte-checked against the private originals
and accepted, but a later review separately rejected a detailed raw `perf01.json`
execution receipt as beyond the authorized numerical evidence scope. Raw archive
publication was also rejected on scope grounds. No rejected payload was retried
or sent through another channel. To continue with a materially smaller public
result, this commit omits all copied raw controls and receipts, including the
previous token-free supervision projections. The complete originals, rejected
payload identities and actual review responses remain local and unchanged.

The public result is now limited to the synthetic comparison table above,
`public-summary.json` numerical aggregates and 104-item checklist, reproducible
audit/projection source, and small execution/source-review records. It omits
per-process identities, parent/start ticks, detailed process observations and
full raw database execution receipts. The prior token projection alone did not
resolve the separate scope restriction. No claim is made that the complete raw
evidence is remotely available.
