# Recovery 04 archive preparation for completed Recovery 03 evidence

This directory preserves already completed observations and the exact artifacts that produced them. Creating or verifying these archives does not grant new correctness, timing, parity, sustained-workload, or publication credit. The five historical Stage 1 archives are unchanged. The two previously completed local foundation archives are reused without recompression.

The original workspace is `/workspace/scratch/0669b59f9cae/DB-Exec-Parity-01`.

## Check or restore

The completed operation verified **7 archives, 141 ordered parts and all 9,215 members**. Exact compressed archive bytes total **569,623,004**. `verification.json` and `upload-manifest.json` are the authority for the actual archive bytes, hashes, members and files to publish. Remote reference publication remains pending.

The unchanged archive checker verifies every part and every member:

```sh
python3 restore_evidence.py all --output /absolute/new/check-directory
python3 restore_evidence.py all --output /absolute/new/restore-directory --extract
```

Use a fresh destination for each command. Extraction restores the original workspace-relative file paths. Absolute original paths inside immutable raw receipts are retained as provenance; they must not be rewritten or mistaken for newly executed commands.

The standalone new index contains the two foundation archives plus five new archives. Full recovery also requires the five historical Stage 1 archives from Plan commit `e99b2291be9371c548a5d80a4133281bccb4bc2b`, under `ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/raw-archives`. When integrating this publication into Plan, retain those five entries, append the seven new distinct entries, and copy each new named raw-archive folder. The existing Plan `restore_evidence.py all` can then check/extract the combined set in one command.

## Source and runtime recovery

Product base commit is Korda `7ff7b57b907b689defb880b8af62d83679608603`. The candidate artifact archive includes 14 exact candidate or diagnostic source snapshots: commit/tree identity, clean source status, full binary-capable diff from the base, every changed file, and a verified Git bundle when the branch differs from the base. A bundle requires the base repository history. Fetch its `HEAD` into a fresh recovery branch and verify the resulting SHA against that snapshot identity before using it. These archived commits do not become an integrated or accepted product candidate through archival.

Actual Release AOT command ELFs, matching debug files, native libraries, local independent packages, generated C#, actual restore assets, retained AOT compiler response/export files, runtime configuration, build commands and source markers are preserved. PostgreSQL 18.0's actual installed server programs and support files, locked source archive and build/configure/install logs are included to avoid another server rebuild. Eight library symlinks are explicitly represented as regular files with identical target bytes; their original link targets are recorded in the manifests. SDK/LLVM/CMake/Ninja and package download caches are excluded, with dependency locks and installation receipts retained.

Physical PostgreSQL cluster directories and SQLite fixture/WAL/SHM files are excluded. The deterministic fixture source, exact initializer executable identity, SQL, parameter/oracle manifest, commands, server settings and process logs remain. This is not a physical database backup. Compiler intermediates are excluded except for actual generated source, restore metadata and AOT response/export/runtime configuration evidence. Every exclusion is listed in the selection and member manifests. No original raw file, ELF, source, symbol or old archive was deleted.

## Scope boundaries

The ordinary first aborted attempt, both-order successful screens, targeted risks, codec allocator/equivalence and sampling observations, relation allocation diagnostics, actual Worker-D causal counts, full native/AOT correctness suites, and old-mask failure identity are retained. Worker-D old count directories both have their own `completion.json` (six processes/provider, diagnostic-only); they are not unfinished measurement claims.

New work under `recovery-04` paths is intentionally excluded. The source snapshot and selection were taken before ordinary timing; compression runs on CPU 8 at nice 19 with one xz thread. Diagnostic allocation/sample spans remain diagnostic, regardless of ordinary flags in unmodified consumers. Final mixed35 credit remains 0/4 in the checkpoint this archive preserves.

## Publication boundary

`remotePublication` remains false until a committed reachable tree has been published and read back. Existing foundation blob-upload receipts cover 17 of its 18 parts; the first foundation part and the consumer-input part have no earlier upload receipt. A blob upload by itself is not reference publication. The upload manifest supplies Git blob SHA alongside SHA256 so matching earlier objects can be reused without recompression or identity changes.
