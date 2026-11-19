# Perf-01 database observer calibration preparation

Status: source prepared and locally checked; no new calibration, noise extraction
or long segment has run. The integration owner adopted the completed pair only
for fresh database calibration/noise. Execution still follows independent source
review, publication/readback of this contract and an exclusive owner timing window.

## Actual source and pair binding

- Measurement driver commit: `a3ce0f6295c535b0a81de95fc0f98aa19deb259c`; full tree: `eb6b61e7c159c343513f7a50359f1a6c09f8df77`.
- Actual before runtime remains `ea5fa528035d025bd7a28698ee7c71194432236c`. This is a measurement-policy change, not a product optimization.
- Current pair configuration SHA-256: `2f7a7149d3f8de59a90b1cd569032bb16a203957c4807062e8a5330c6f1368e0`.
- Actual completed execution SHA-256: `c64debb45b30388809373695dfda3e59714571debf3db8801b4672a54c7de796`.
- Final independent pair audit SHA-256: `bfca614ae18a47237df7f1fdea5daed54a364cd087a12118fc3937aaedee130d`.

The pair actually completed on 2026-11-19 at 23:01:28 UTC. Both PostgreSQL 120-second
cells completed all 17,282 operations with original validity and service gates;
side audits, independent durability/recovery checks, final equivalence and cleanup
passed. The source-bound final audit has nine passed checklist entries. Its credit
is zero and remains zero here. The adopted modes are explicit `deferred` scheduler
GC plus explicit `threaded` resource sampling. Their hashes are
`a2fa36f9ef4a05d7d56d05dc7d8dcd6f881e3849285907ed1d132b32b9fe9cb7` and
`19d72617af9acb329148dbae9f6e0419e79013f7d9381998957b310eec008826` respectively.

This short control did not reproduce the earlier 100 ms dispatch stall. It is
functional/measurement-coverage qualification, not evidence of a speedup. The
threaded side added about 1.48 percentage points of scheduler CPU and 2.49 of target
CPU (one-core scale), with about 1.17/1.59 MiB additional measured RSS respectively.
The target's two samplers used a shared default pool with 13 unique worker TIDs
observed over the run; A21 separately observed one. Unique TIDs over time are not
a simultaneous-thread count or a fixed one/two-thread pool promise. Application
samples changed from 2,312 to 2,253 and each generator role from 120 to 119 under
the unchanged sleep-after-sample contract. Actual sample intervals remain evidence.
SQLite, the 259,526-operation long plan and finalization/restored-GC RSS remain
unqualified by this pair. New calibration can still fail.

## Minimal changes from the retained implementation

| Source | Scoped change |
|---|---|
| `database_observer_calibrate.py` | New named copy of the unchanged `database_calibrate.py`; explicit threaded CLI, root-confined paths, actual pair adoption, source-bound descriptor/hash and completed-observer checks. |
| `database_freeze_observer_noise.py` | New named copy of `database_freeze_gc_noise.py`; same final-triplet reader/range rule, additionally binds threaded policy, completed observer, actual resource-file bytes and current pair/source closure. Dependencies are hash-checked before import. |
| `run_db_observer_calibration_001.py` | Portable derivative of the old local supervisor; explicit root/document/source SHA, exact driver commit/tree, actual interpreter/version/binary, confined fresh input/output paths and both policy identities. Both future logs are checked before starting either provider. The command document is private. |
| `database-observer-policy-001.json` | New compact public contract with numbers, fixed modes, source/hash identities and relative repository source names. No argv, environment, host paths, process identities or raw control receipt. |

Original controller, noise freezer, policy, rejected PostgreSQL long and failed
25/s deferred/synchronous calibration remain immutable. No earlier cell or noise
triplet is a candidate input for the new noise. Historical invalid raw data is
not required to run this preparation.

## Unchanged calibration and acceptance

The policy-revision-4 algorithm is unchanged: rates 5, 10, 20, 40, 80, 160, 320,
640/s; 30-second stages; doubling extension within original finite limits;
bisection of the pass/fail bracket; exactly three fresh 60-second confirmations;
on a failed triplet, original 10% stepdown and at most ten rounds. Every failure
is retained. An invalid generator observation is not a server-capacity bound.

The full ladder/refinement/confirmation control-flow source is byte-identical to
the original. All eight provider/route pure argv constructions differ only by
adding `--resource-sampling-policy threaded`. Explicit `--scheduler-gc-policy deferred`
remains. Seed, concurrency16, original warmup/recovery/idle, compact accounting,
DB initial state/durability and CPU layout remain unchanged. There is **no diagnostic
continuation whitelist** in calibration acceptance: actual exit0, original valid,
service qualification, all durability/recovery/cleanup and policy checks must pass.
The original classified-overload command flag still records overload and recovery;
it cannot turn a failing cell into a qualifying confirmation.

Keep 100 ms generator lag, zero unexpected errors, 500 ms arrival p99 and 256 MiB
application RSS. Application and generator resources are observed separately.
Dedicated PostgreSQL-process CPU is unavailable in this measurement path; it
must not be inferred from the application's counters or described as a collected
PostgreSQL resource series.
The paired long targets stay PostgreSQL144/s and SQLite40/s, C16, 1802 seconds,
16 warmup requests, 32 recovery requests and 60 seconds idle: 259,526 and 72,091
planned operations. A new capacity below a fixed long target is a failure or
limitation to resolve; no script silently lowers the target. Short confirmation
or noise never earns long credit.

## Noise extraction

Use only each completed fresh calibration's entire last three passing 60-second
confirmation processes at its selected rate, after the controller exits and the
owner checks all failures and the selection. The unchanged database comparator
reads full original rows and verifies validity, persistence, ownership, independent
processes and nonoverlapping windows. The before-only noise rule remains
`max(1000, max(process means) - min(process means))` for mixed, cycle and page slices.
Both policy descriptors/hashes, full plan settings and actual a3ce0f6 source closure
must agree. The freezer resolves the summary's hashed `perf01.json` within its
cell, requires the complete observer object to match, and hashes the actual
`generator-resources.jsonl` within that receipt's directory. Both files join the
final unchanged-input closure. Missing/altered resources or escaped paths are
rejected. No favorable subset, legacy noise or later after/direct data is used.
Those confirmation/noise cells cannot be reused as fresh comparison processes.

The complete noise receipt remains local: it contains private evidence references.
Publish only a separately reviewed numerical projection and immutable receipt hash.
Do not publish the complete receipt or encode rejected controls into an archive.

## Concrete local execution binding

The exact prepared local command document has SHA-256
`fbaee7021be73322b7a73d1169bace6b03679a87ecf36b66bd1700e8c7ec5df8`. It is retained as the owner-provided `PRIVATE_CONFIGURATION`;
its argv, environment reference and absolute paths are not committed here.
`checks/database-observer-calibration-source-002/preparation.json` binds that hash
to the public contract `98f8e537d87cac9de87cb2d1ae1150465a5c9a052333451f0772398b58ad58c3`.
The full actual configuration is specific to the retained measurement workspace;
portable scripts resolve `--root`, reject paths escaping it and verify every input.

After source review and exact public readback, the owner can use the original locked
environment and Python, with the actual private document and an exclusive window:

```bash
taskset -c 8 "$LOCKED_PYTHON" -B \
  "$PLAN_CHECKOUT/ledger/evidence/batches/Perf-01/run_db_observer_calibration_001.py" \
  --root "$PERF01_ROOT" --document "$PRIVATE_CONFIGURATION" \
  --document-sha256 fbaee7021be73322b7a73d1169bace6b03679a87ecf36b66bd1700e8c7ec5df8 \
  --source-sha256 c411e2d998bfaa0278d9ef2092bff785f37bfa50c45a2e1b05c6da153e5201c1
```

Do not add an outer flock: each unchanged measurement argv already owns the timing
lock. Root retains the serial queue between commands. Actual child return codes
are recorded; runtime loss may leave the last running receipt and never implies
success. Supervision explicitly rejects optimized Python before any assertion;
existing outputs, receipts and both logs, including dangling symlinks, fail preflight. Inspect and clean interrupted process trees before any new workload.

After calibration, run the new freezer on CPU8 under the existing nonblocking
lock with explicit `--root`, `--nativeweave`, `--database-amendment` and its hash,
`--calibration`, actual completed `--selection-sha256`/`--controller-sha256`,
`--source-sha256 d4c2a887452985697b3ec69d45500b4cf87185c9b54433ed887224047524f3de`,
`--comparison-source-sha256 0f3ee6ca0d4ce9fcdce256df9b9fce1f9ce5eaa9032c3afa86e443aeceff59b8` and a fresh `--output`.
No future selection/controller/noise hash is invented by this preparation.

## Actual source-only checks

`checks/database-observer-calibration-source-002/check_source.py` ran on CPU8 under
the nonblocking timing lock: actual exit0, **68/68 passed**, 0.118728 seconds.
It checked syntax, exact original/source hashes, unchanged algorithm/triplet bytes,
eight pure argv pairs, original limits, actual pair proof bindings, rejected
unadopted/changed proof and root escapes, and the restricted public contract.
Tiny owned fixtures additionally prove actual resource-byte binding; rejection of
missing/changed resources, receipt mismatch and path escapes; and rejection of
existing/dangling output paths. Source checks cover the actual interpreter guards
and both-log preflight. The exact private configuration additionally passed 26
source/metadata hash checks and two command-policy wiring checks.

The checks extracted only bounded pure argv/path/proof/file-identity helpers from
AST; they did not import the measurement driver or execute controller, freezer,
supervisor, service or load. This is preparation evidence, not executed calibration
or a long acceptance gate. Source snapshot `c592be7` and the original 001 receipts
retain the earlier actual 56/56 result before independent review found the missing
resource-byte pin and supervisor safeguards. Those earlier receipts do not validate
the final source and are superseded by 002 for that purpose.
