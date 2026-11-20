# Accepted database raw-duplicate retention

This narrow helper is bound to the actual accepted PostgreSQL/SQLite manifests and completed bytewise restore proofs. The measurement owner explicitly authorized only five named large raw files per provider in the original cell and their five restored counterparts: exactly twenty files. It checks all current compressed shard hashes, both pinned manifests and the exact proof lists, then checks each target SHA-256 immediately before unlink. It never removes a directory, archive, source, binary, database, acceptance receipt, GC/supervision input or other metadata. Actual per-file outcomes are durably recorded, including partial failures.

Four `COLD-STORAGE.md` markers provide the accepted bundle/hash and fresh-restore command before deletion. They explicitly state that a fresh archive restore alone omits the observer wrapper's extra GC/supervision inputs. Full wrapper replay requires restoring the five hash-verified missing files to their original relative paths while preserving the retained extra metadata, or an explicitly relocation-aware workflow.

The source is a specific local retention step, not a new archive format. The existing `pack_evidence.py` produced and restored both bundles; every archived file was compared byte-for-byte with its original. All completed proofs and commands remain in the local execution records. No remote raw-publication/readback is claimed. Numerical public evidence is separate from private operation/control metadata. The helper source was committed before cleanup. The completed scalar evidence below was added after the actual outer exit and per-file results were observed.

## Completed local execution

The existing packer, its independent verification command and its restore command all exited zero for both groups. Every restored archive member was compared byte-for-byte with its corresponding original before cleanup. The archive/restore sequence ran from **2026-11-20 02:07:38.409641 UTC** through **02:18:40.482640 UTC**. Both restores passed a free-space gate requiring the restored raw size plus a **2 GiB** margin.

| Group | Archive members restored and equal | Raw bytes | gzip chunk bytes | gzip chunks | Original files deleted | Restored duplicates deleted |
|---|---:|---:|---:|---:|---:|---:|
| PostgreSQL | 18 / 18 | 4,332,821,712 | 71,145,369 | 532 | 5 | 5 |
| SQLite | 17 / 17 | 1,396,231,441 | 25,204,694 | 181 | 5 | 5 |

The separate authorized retention execution ran from **02:26:27.797672 UTC** to **02:26:40.165523 UTC**, with actual outer exit **0**. It rechecked the accepted manifests and all compressed chunk hashes, then rechecked each target immediately before unlink. Exactly **20** files, totaling **11,413,621,828 logical bytes**, were removed. The sampled filesystem free space increased from **5,847,437,312** to **17,261,117,440 bytes**. The observed free-space increase is **11,413,680,128 bytes**; it is reported separately from file logical bytes because filesystem allocation and contemporaneous small metadata writes are different quantities. These are observations at the recorded cleanup times, not a claim about current free space.

The accepted bundles, every other original/restored file, and all four recovery markers remain. The source-bound helper performed no recursive directory removal and did not change any original acceptance receipt. Archive gzip byte counts describe storage only; they are not NativeWeave codec throughput, protocol compression or an optimization result. Accepted before durations remain 1,802.212239616 seconds for PostgreSQL and 1,802.209932916 seconds for SQLite, with no additional measurement credit.

## Portable public evidence

[public-checklist.json](public-checklist.json) contains only fixed numerical/boolean fields, enums, UTC timestamps and hashes. It includes archive manifests, exact bytewise-proof hashes, accepted-verifier hashes, actual exits, deletion totals, restore-space gates and recovery-marker hashes. [projection-execution.json](projection-execution.json) binds the fourteen small source records read for that checklist. No raw operation file was replayed, no new archive was made and no test, build or business load ran during this projection.

The full private proofs, commands and per-file deletion records remain in their existing local evidence records; this public projection deliberately excludes their operational paths, process/session identities and control metadata. Source retention alone does not claim public upload or remote readback of the raw archives.

Manifest SHA-256 values:

- PostgreSQL: `e913d75191253490e4ba2b1deba86ebd1e81963ff83fd39cc0846a8dab1a5e3a`
- SQLite: `ad7edaa996604f0d4551f5aeab24353bc33958fe4b52d0c00d9bebcaa4f1dc26`
