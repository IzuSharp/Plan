# DB-Exec-Parity-01 — eight archive recovery set

This set preserves the actual completed Recovery 03 experiments and the closed Recovery 04 relation-depth and Worker-D count diagnostics. It contains **8 archives, 153 ordered parts and 9,879 expanded members**, totaling **615,994,444 compressed bytes**. The original primary seven archives and supplementary eighth archive were each reconstructed from their parts and every expanded member was SHA256 checked by the unchanged restore tool. Source bytes and measured identities remain unchanged.

This archival operation grants no new ordinary timing, correctness, sustained-workload, parity or release credit. Git blob creation is distinct from a committed reachable reference and its final readback; the caller records that publication step separately.

## Verify or restore

Run from this directory and use a new output directory:

```sh
python3 restore_evidence.py all --output /absolute/new/check-directory
python3 restore_evidence.py all --output /absolute/new/restore-directory --extract
```

The top-level index combines seven primary entries and one supplementary entry. Their original indices and verification logs remain under `records/primary` and `records/supplement-01`. This directory leaves the five historical Stage 1 archives and their original index bytes unchanged. Full workflow recovery additionally requires those Stage 1 support archives at Plan commit `e99b2291be9371c548a5d80a4133281bccb4bc2b`, under `ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/raw-archives`, and the product base Korda commit `7ff7b57b907b689defb880b8af62d83679608603`.

Archive member paths are relative to the original workspace `/workspace/scratch/0669b59f9cae/DB-Exec-Parity-01`. Absolute paths in immutable original commands and receipts remain original provenance; they are not rewritten into claims of new execution.

## Coverage

The primary set contains the matched Release-with-symbols baseline, actual AOT and native artifacts, local provider packages, generated C#, response/export/runtime inputs, source snapshots and verified source Git bundles for 14 candidate/diagnostic worktrees, ordinary forward/reverse screens, targeted risks, failed attempts, native allocator/equivalence and current-ELF sampling evidence, relation allocation diagnostics, Worker-D diagnostics and native/AOT correctness results. The actual PostgreSQL 18.0 installation, locked source tarball and build logs are included. The supplementary set adds the completed relation deep-boundary observations and Worker-D 12-process count proof, along with original failed attempts and the actual diagnostic artifacts.

Active-at-selection `sampler04`, capacity correctness and capacity ordinary measurements are **not in these eight archives**; they require a later increment. No entry in this set claims those later results.

Physical PostgreSQL clusters, SQLite fixture/WAL/SHM bytes and ordinary compiler caches/intermediates are excluded. Deterministic fixture sources, initializer identities, SQL/oracles, commands, server settings, logs and exact selected consumer artifacts remain. This is not a physical database backup. Actual generated source, restore assets and AOT response/export/runtime inputs remain even when originating inside `obj`. Exclusions are explicit in each manifest. Eight PG library symlinks are represented by exact target bytes as regular files with original targets recorded.

## Cleanup and durability

After complete verification, root authorized removal of newly generated redundant compressed staging/roundtrip copies to recover disk space. The exact paths, sizes, hashes and retained restore entry points are in `records/cleanup`. No original source, raw observation, actual ELF/debug file, historical unique archive or retained part was removed. Canonical archive identities continue to refer to exact bytes reconstructible from the retained ordered parts; deletion of a duplicate local container did not change those identities.
