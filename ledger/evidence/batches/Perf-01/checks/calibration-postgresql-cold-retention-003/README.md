# Perf-01: completed PostgreSQL snapshot retention 003

**245 selected large files from 79 stopped baseline calibration clusters were preserved in verified gzip members and removed from their original locations.** The operation preserved the other database files, all original result and persistence records, and every original validity flag. It is a storage operation and supplies no measurement or performance credit.

| Actual observation | Result |
|---|---:|
| Synthetic finite gate | 15 passed, 0 failed; actual outer exit 0 |
| Finite gate UTC | 2026-11-20 05:35:11.404018–05:35:11.700845 |
| Storage execution UTC | 2026-11-20 05:35:44.358063–05:37:01.847585 |
| Actual storage outer exit | 0 |
| Selected old clusters / removed files | 79 / 245 |
| Original selected bytes removed | 2,364,178,432 B |
| Gzip bytes retained | 447,308,972 B |
| Logical original bytes minus gzip bytes | 1,916,869,460 B |
| Observed filesystem free bytes before | 9,561,346,048 B |
| Observed filesystem free bytes after | 11,477,278,720 B |
| Observed free-space increase | 1,915,932,672 B |
| Complete per-file verification and removal records | 245 |
| Original `valid` flags: true / false | 67 / 12, unchanged |
| Frozen small control files | 484 |

The compressed content is about 18.92% of the selected original bytes. The logical size difference and observed filesystem free-space change differ because free space also reflects allocation and metadata. Neither is a substitute for checking the free space at the start of a subsequent workload. At the recorded end of this operation, free space was 739,860,480 B above the frozen 10 GiB PostgreSQL long-run preflight requirement; this is a historical observation, not a claim about current free space.

## What the proof establishes

The exact completed retainer manifest binds the reviewed source and 245-file selection. Every member has an original SHA-256, gzip SHA-256, original size, complete decoded readback proof, and a durable verification record made before its source unlink. The unchanged storage engine rereads the original source before deletion and checks path/FD identity, controls and archive bytes. All 245 records ended in `removed`; the actual outer process exited zero.

The guard retains the 79 clusters' original terminal state, completed owned-process cleanup, recorded successful PostgreSQL stop and durable settings. It rejects a remaining postmaster PID file or an observable live PostgreSQL process before retention. These are checks made by the completed retainer at its own execution times. The report projection did not check for live processes again during later workloads.

This report was derived from the small, hash-bound execution receipts, selection, manifest and finite-test stderr. It did **not** replay database files, gzip members, application operations, queries, or a benchmark. The per-file content verification is attributed to the actual retainer; the projection checked its recorded identities, selected set, counts, sizes and terminal states.

## Scope and restoration limits

The stat inventory contained 103,381 regular single-link database files and 5,090,282,381 logical bytes. The selected 245 files are at least 1 MiB and occur only in WAL and numbered relation-file locations. The remaining **2,726,103,949 logical bytes** of database files were outside the deletion selection and remain in place, along with configuration, logs, controls, persistence evidence, binaries and packages. No directory was recursively removed.

**The 79 partially cold clusters must not be restarted until their exact selected files have been restored.** A fresh restore produces only those selected files; it must be combined with the retained original files. The recorded original mode and ownership require deliberate handling during reassembly. A restored file has a new inode and ctime. This operation does not establish fresh SQL consistency or turn the 12 originally invalid samples into accepted measurements.

The byte-preserving gzip members and detailed per-file manifest remain in local cold storage. This public entry supplies only portable numbers, enums, UTC timestamps and content hashes; it does not claim that the database snapshots were uploaded publicly. There was no materialized database restore performed by this report projection. The actual synthetic finite gate separately exercised a small lossless roundtrip.

## Exact evidence identities

| Receipt or source | SHA-256 |
|---|---|
| Completed archive manifest | `44699ccb0fcca6107e6dd7fdd88db7252a1f373bcf4c40e47a0085768f940b4c` |
| Actual storage execution | `4ad02b4e94a76c2c1aab28cddd8e849a9b2dd791b84d76441181a8846b6d5cd3` |
| Actual finite execution | `4ff69bb24f78d386919c73c93136cb73f5fd35c0af595dd4df4b4bd6b38463b1` |
| Finite stderr | `566b1f597db4328484a7d7dfcc3a68c9a94f683fdcdbbe2b6d4a8ff2f9abf836` |
| Reviewed retainer source | `5774bfcb9e79bf8d8c2642fc8597f74da4a7b852ea23d847a5aa9edb5ef3ea3e` |
| Exact selection | `0351e8e4cf7d1b344e8b7e24ca007f6b597a1b76bbd220da2b9533c88785cfe5` |
| Finite test source | `b3d345d830efc055e76d8bf67522ac275d3389525b620eebd764507cfac287b2` |

[The numerical checklist](public-checklist.json) includes the original metadata-inventory and projection-source hashes, all actual timings, the complete count projection, and explicit zero-credit fields. [The projection execution receipt](projection-execution.json) binds that checklist to the same input hashes. No product gain, formal comparison completion, or long-duration credit is attributed to this operation.
