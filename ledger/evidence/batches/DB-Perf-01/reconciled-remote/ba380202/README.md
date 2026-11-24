# Reconciliation of the concurrent Plan checkpoint

Origin commit: `ba380202e7b36cbfe8dcd4bc2cfa0afe86048d92`; tree:
`cf94ab3a81351271a7dc0c7eaf49ea3acdbd2a02`; parent:
`bc1956936ee77a997a016856c97def6aabc0bbc6`. The remote commit identifies a separate
execution under `/workspace/scratch/754bc732518e`. Its recorded author is Chris.
The reconciling executor cannot infer which runtime or person launched each
process from that author field. It preserves the original execution attribution
and performs only the read-only identity/counter verification recorded here.

`acceptance.json`, `handoff-linux.md` and `plan.md` in this directory are exact
copies of the three overlapping remote documents. They are historical snapshots,
not the current acceptance schema. All remote-only raw preflight and review files
remain at their original paths. [retained-files.json](retained-files.json) binds
the original remote paths to retained bytes, including the three archived reports.
Local recovery commits `5a7525437d17000952d553d662920582df6469a1` and
`509e1b7c58172834b02795c7329e841a5b6effb0` remain in local merge ancestry.

[public-preflight-verification.json](public-preflight-verification.json) records
the newly executed read-only checks of actual nupkgs, ELF executables, loaded
native files, package-member manifests, twelve raw processes and 386 exact
producer source inputs. Both sides use the same consumer source files. The
before packages are the fixed-main `0.1.0-preview.3` archives. The after packages
are the separately built `0.1.0-perf-lazy.1` candidate at
`28110ee03391831c737a54204730730a01b77a34`, retaining the original native images.
They are not the combined scalar/lazy `ci.1` packages from CI45366971791 and cannot
establish acceptance for that or a later optimized candidate.

Each provider's three after processes has 384 synchronous first-batch numeric
windows / 48,768 rows, every cumulative allocation delta exactly zero. The two
`*-narrow-allocation.json` files translate only this boundary into the current
receipt schema; raw results remain unchanged. Complete queries and refills remain
positive. Their exact framework-owned fraction remains unproven. Environment
exclusivity was not established; elapsed ticks are diagnostic, and long credit is
zero. The current acceptance stays in progress.

Reproduce the read-only check while the original source and artifacts remain:

```sh
python3 ledger/evidence/batches/DB-Perf-01/reconciled-remote/ba380202/reverify.py \
  --harness-repository /workspace/scratch/b94e2a0e0c3f/Korda-DB-Perf-01-linux \
  --candidate-repository /workspace/scratch/754bc732518e/Korda-DB-Perf-01-linux
```

The original package source bundle, build commands and member manifests remain
under `preflight/streaming-lazy-join/` and
`preflight/korda-allocation-after-lazy-join/`; their recovery instructions do not
require editing another active worktree. The reproduction script writes a new
verification timestamp; do not confuse that with the original measurement time.
