# Recovery04/05 evidence increment: archives-02

This directory preserves the sealed caller sampler, the isolated relation-capacity experiment, integrated04/05 actual consumers, and the 122-process combined ordinary screen. It does not add a 30-minute final-acceptance cell or change a failed diagnostic verdict.

## Dependency and scope

Restore the previously published `archives-01` first when recreating the complete workspace. Its Plan commit is `b54054bd1f3befe94e1817cc29f494bd782854b9`, archive tree `c20cd01bd243feecc84e822054d5b9a390521215`. It contains the original baseline/Dapper consumers, PostgreSQL runtime, foundation tooling and earlier diagnostics. This increment deliberately does not recompress those bytes. Its dependency also supplies the earlier `relations-recovery-04/deep-layer` archive.

The increment has four packages:

| Package | Preserved evidence |
|---|---|
| `sampler-caller04` | Sampler source, actual sampler library and AOT fixture outputs, preflight failures/successes, native/AOT/negative controls, all eight business-process raw traces and original validators, caller analysis/addendum/machine code, new Worker-D + codec consumer and nupkg. |
| `relation-capacity04` | Isolated capacity source patches, actual diagnostic/ordinary consumers, packages/generated C#/ELF/debug/native libraries, all correctness attempts, partial disk-full failures, successful reruns, and ordinary AB/BA evidence. |
| `integrated-combined05` | Both integrated04 and integrated05 actual consumer/package/build identities, retained generated inputs, 122 ordinary-screen processes and their commands/raw/receipts, exact Korda source bundles and full binary patches, publication mappings, and sealed independent reviews. |
| `closed-runner-review05` | The subsequently sealed /proc observer adapter, two bounded correctness probes, original failed parallel-setting expectation, offline CPU checks and 475-check independent review. These controls are not ordinary performance results. |

`raw-archives/index.json` and each expanded-file manifest are authoritative for the exact selected paths, hashes, counts and exclusions. `selection.json` records the source stat identities checked at build time. The original workspace root was `/workspace/scratch/0669b59f9cae/DB-Exec-Parity-01`; expanded members keep paths relative to that root.

Physical PostgreSQL clusters and SQLite fixture/WAL/SHM files are excluded. Preserve/reuse the recorded seed sources, initializer commands, database identities and configuration rather than treating this as a physical database backup. Downloadable compiler/SDK/NuGet caches and ordinary build intermediates are also excluded; actual outputs, generated C#, restored assets, AOT response/export inputs and the prior retained-intermediates snapshot remain.

The later `relations-recovery-04/runner-review` was actively being updated while selection was first attempted. A source-stat mismatch rejected that first capacity archive attempt; its identity and failure receipt are retained under `records/attempts/`. It is not a completed package or a performance failure. The capacity retry excludes that directory. After its author explicitly sealed the review, the separate `closed-runner-review05` package preserved it with the exact observer scripts. Incomplete compressed duplicate parts remain only in the local attempt directory; no unique raw data is omitted by not publishing those duplicate compressed bytes.

## Caller statistics and original failure

The original sampler report and its later correction are preserved together. `sampler-addendum-freeze.json` binds the correction to its exact source hashes. The corrected denominators are 15,059 selected steady samples across eight processes and 1,510 selected steady samples in `r2-workerdcodec04`. The 9,371 Thread.SpinWait samples partition into 9,350 WaitSlow, 3 LowLevelLock/Backoff, 17 Lock.TryEnterSlow return contexts via the verified helper tail jump, and 1 SpinOnceCore call. The original whole-process validation remains seven complete passes and one rejected bad callchain. These counts are attribution evidence; they are not exclusive stage durations.

## Stream verification and restore

Python 3 with its standard-library `lzma` support is sufficient. Commands operate on local parts and make no network requests.

```sh
python3 streaming_archive.py verify --index raw-archives/index.json
```

The verifier reads ordered parts directly into the XZ decoder. It checks every part SHA-256/length, the entire compressed stream SHA-256, the entire uncompressed tar SHA-256 including padding, and each member's path, length, content hash and executable mode. It creates no canonical compressed file, uncompressed tar or extraction copy during verification.

To restore this increment into a new workspace:

```sh
python3 streaming_archive.py restore --index raw-archives/index.json --extract /path/to/restored-workspace
```

If `archives-01` has already been extracted to that workspace, overlay this later increment explicitly:

```sh
python3 streaming_archive.py restore --index raw-archives/index.json --extract /path/to/restored-workspace --replace-existing
```

Identical existing members are accepted without replacement. Differing existing files require the explicit overlay option and are replaced only after that member's content verifies. Parent paths are resolved and checked before creating directories, and checked again afterwards; external parent symlinks and final-file symlinks are rejected. Restore assumes the destination is not concurrently modified. A restore commits one verified member at a time: a later damaged part or interruption can leave earlier verified files and temporary files. It is not an atomic transaction across the whole archive. Failed restoration does not grant a successful verification receipt. Enough space for expanded selected files is required only when extraction is requested.

The source snapshots contain a Git bundle, full binary patch from Korda base `7ff7b57b907b689defb880b8af62d83679608603`, changed-file copies and exact HEAD/tree/bundle hashes. The bundles require that base commit to exist in the destination Git repository. Local-built integrated05 `867c869a7e51949122b3dd13e4c7c6df2a914ec7` and connector-published `2ea67ce1902f330679c3ebff4d6d5733be20f69c` share tree `4e3989f2ce9e0c554585aab5a8bbb656e689b18d`; this mapping does not relabel the measured artifact's build commit.

`writer-v1.py` preserves the original writer used for the first sampler package. `writer-v2.py` preserves the version at the rejected capacity attempt. `writer-v3.py` preserves the successful capacity and integrated writer. `writer-v4.py` preserves the later sealed observer selection and the verifier before the contained-path correction. `streaming_archive.py` is the corrected verifier/restorer. The selfcheck receipts retain the cross-part roundtrip, corrupt-part rejection, explicit-overlay, idempotent-restore and external-parent-symlink negative controls. The correction changes no payload part or archived member. Archive construction uses CPU 8, nice 19, single-thread liblzma preset 3 with CRC64; it runs only outside ordinary measurement windows. Source selection relies on explicit cooperative sealing and checks each file's size/mtime/inode before and after its read; it is not a simultaneous filesystem snapshot.

## Publication and recovery

The original 94-target `publication/blob-publication-manifest-04.json` and its 94 successful receipts are preserved as upload history. A later small verifier amendment replaces this README and the active restorer, preserves their earlier identities, and adds its independent-review/tiny-control evidence. `publication/current-path-manifest-05.json` describes the resulting target mapping, excluding its own self-referential hash; `records/verifier-amendment-05.json` records the exact changes. The uploader's receipts are atomically updated after each successful `create_blob`; the resume record contains the cursor and remaining bytes. The bridge reads Base64 in bounded chunks and validates the length before submitting a blob. No create-tree, commit, branch or ref mutation is performed by this uploader.

Blob creation alone does not make an archive reachable. `remotePublication` remains false in the uploader's receipts until the root agent separately publishes a Git tree/ref and verifies the target mappings. The old `archives-01` publication receipt is included as a dependency record; it does not grant publication status to this increment.
