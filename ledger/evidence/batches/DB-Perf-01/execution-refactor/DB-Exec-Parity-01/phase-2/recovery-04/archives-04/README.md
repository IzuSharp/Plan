# DB-Exec-Parity-01 — closed tail06 evidence, archive increment 04

This increment preserves **the rejected tail06 candidate and its completed evidence**. The selected implementation remains integrated05. The user cancelled all 1800-second final and before-long measurements for this round. The four mechanism processes, 114 ordinary short processes and twelve 30-second mixed cells retain their original scopes and limitations. Archiving grants no performance, correctness, parity, or long-run credit. Future HostPull source and experiments are excluded.

## Contents and exact size

The nine packages contain **2,404 original files / 559,048,366 expanded bytes** in **52 ordered parts / 195,461,772 compressed bytes**. Each part is at most 4 MiB. No full canonical compressed archive, uncompressed tar, or extraction roundtrip copy was created.

| Package | Members | Expanded bytes | Compressed bytes | Parts |
| --- | ---: | ---: | ---: | ---: |
| ordinary-consumers06 | 216 | 98,800,360 | 36,562,764 | 9 |
| diagnostic-consumers06 | 732 | 201,460,888 | 73,233,924 | 18 |
| correctness-negative06 | 159 | 119,704,213 | 31,791,088 | 8 |
| tail-evidence06 | 1,162 | 86,913,141 | 5,084,968 | 2 |
| wrapper-recovery06 | 105 | 2,659,504 | 195,624 | 1 |
| legacy-worker-diag-packages06 | 4 | 27,456,713 | 27,333,268 | 7 |
| compiler-package-inputs06 | 3 | 17,676,790 | 17,238,028 | 5 |
| source-snapshots06 | 17 | 215,479 | 36,160 | 1 |
| prior-dapper-package-inputs06 | 6 | 4,161,278 | 3,985,948 | 1 |

The payload retains the two ordinary and four diagnostic actual Native AOT consumer ELF/debug/native images, real nupkg, generated C#, harness source and build/binding receipts. Actual correctness and expected-negative publish outputs are retained. The negative failure keeps its original exit/verdict, and every diagnostic or failed attempt keeps its original identity. Raw mechanism, ordinary114 and mixed12 results, independent reviews, the coordinator read-only analysis, wrapper06 source/control identities and cleanup records are included.

All twelve short mixed cells completed with 180,000 successful operations and zero business failure/refusal. This statement identifies the archived gate; the independent mixed review records why tail06 was nevertheless rejected. It is not a claim of Dapper parity. The original wrapper and measurement identities remain in the raw files.

## Required prior archives

Full workspace recovery requires these already published increments, all below `ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/phase-2/recovery-04/` in `IzuSharp/Plan`:

| Directory | Pinned Plan commit | Needed material |
| --- | --- | --- |
| archives-01 | `b54054bd1f3befe94e1817cc29f494bd782854b9` | Actual baseline/Dapper consumers, baseline provider feed packages, PostgreSQL runtime, earlier diagnostics and original foundation inputs |
| archives-02 | `27e0f35709036b0737ed101ba6472ce1461c0538` | Integrated04/05 artifacts and feed packages, source base `2ea67ce1902f330679c3ebff4d6d5733be20f69c`, earlier controls |
| archives-03 | `d7e2d96db38e2879e0318692e00575158db42a77` | Closed zero/pressure05 evidence, prior wrapper/helper/observer controls and publication/cleanup records |

Preserve the historical Stage1 dependencies described by archives-01: the five original raw archives at Plan `e99b2291be9371c548a5d80a4133281bccb4bc2b`, under `ledger/evidence/batches/DB-Perf-01/execution-refactor/DB-Exec-Parity-01/raw-archives`, plus the original Korda base/source prerequisites. SDK, system toolchain and installation caches remain external locked prerequisites; this is not a full machine image.

Some **local compressed duplicates of archives01/02 were removed after their full remote readback**. Those parts must be obtained from the pinned commits. Their original raw/ELF/package/source files and all metadata were preserved. `wrapper-recovery06` includes the archive03 publication receipt, and archive03 preserves the earlier cleanup/publication evidence. Do not infer local availability of old parts from an earlier upload record.

## Check or restore this increment

Obtain this complete published directory, including `raw-archives/**`, the scripts and `dependency-manifests/**`. Run from that directory:

```sh
python3 restore_archive04.py
```

This verifies all 52 parts, each whole compressed stream, the full decompressed tar including padding, every member's size/SHA256/mode and all ten alias-source metadata bindings. It writes no extracted payload. The exact command succeeded locally; see `final-one-command-verification.json` and its log. `expanded-files-all.json` lists every expanded path and digest, while `raw-archives/index.json` binds the packages and ordered parts.

Restore prior dependencies into a target first, then restore this increment:

```sh
python3 restore_archive04.py --extract /path/to/task-root
```

The default rejects a differing existing file. For an intentional overlay of a prior checkpoint, select that target explicitly and add `--replace-existing`; the verified core replaces each differing member only after its own checksum passes. The package alias hook still rejects differing existing aliases, even under this option. Avoid concurrent changes to the destination tree.

Restoration is **per member**, not a whole-archive transaction. A bad late member/part may leave earlier verified files, or a temporary file. Parent containment is checked before and after directory creation. The fixed core SHA256 is `b24e6dceb0f7ad9f6e394b267651f18bc62039db2931e20a4a51761b40cf273c` and is checked by the entry point. Actual file modes are retained. Original absolute command/source paths remain evidence; running a workload after relocating the task root requires reviewing those paths and the pinned prerequisites. The restore command does not start a workload or database.

### Raw package path closure

The current and reused comparison consumers have **54 raw-package references across twelve build receipts, resolving to nineteen distinct raw paths**. All nineteen are represented either by exact selected raw-package bytes or by ten explicit feed-to-cache copies:

- Six current tail06/diagnostic provider raw-cache paths use the byte-identical original feed packages in this increment.
- Four baseline/integrated05 raw-cache paths use provider feed packages from archives01/02. Their complete published expanded manifests are copied under `dependency-manifests`, with SHA256 and pinned commit/path bindings. Old package payload bytes are not duplicated here.
- Three compiler raw nupkg and six Dapper/driver raw nupkg are included as exact individual files. No unpacked cache tree is archived.

After payload restoration, `restore_package_aliases.py` validates every source and existing destination before making any alias. Missing aliases are independent byte copies, installed without overwriting; existing aliases must match their size/SHA256 and must not share the source's inode. Symlinks, traversal, same-path aliases and source/cache hardlinks are rejected. `--check-only` checks all ten existing aliases without writing. It passed against the current workspace; this is separate from the small fresh-copy controls and is not a full extraction roundtrip claim.

The 25 copy/containment/negative controls and 11 source-binding controls passed. Independent review rechecked the final frozen scripts, all ten mappings against actual build receipts, and both copied prior manifests: see `alias-independent-review-01`. Its earlier attempt records the manifest expansion from six to ten items as an unsealed stop, not a successful prior review. The older 20-check implementation and controls remain under `alias-source-v1` and `alias-controls-01` for identity history; use only the final top-level scripts.

`package-path-closure-final.json` gives each exact resolution. This closes the checked consumer raw-package paths; SDK/system/source prerequisites remain explicit in the prior archives and installation locks.

## Source recovery and exclusions

Four small git bundles and binary patches capture ordinary `4a9e4435ea5c836be44fb00dc4219301567072c6`, diagnostic-before `197f0d3444cf3cfc120982273d48d1dcf74f60db`, diagnostic-tail `ba4e7ec9bf93ad313dbbb167457189a5f95429da` and negative `4efce12ff6c1ece1f059e5b209e4e6a02a38acce`. Each bundle has the sole prerequisite `2ea67ce1902f330679c3ebff4d6d5733be20f69c`, already captured in archives02. No whole repository or duplicate changed-files directory is copied. The two provider build worktrees are mapped to the same ordinary source head.

After restoring archives02 source, verify each bundle in that repository with `git bundle verify`, fetch its `HEAD`, then create a detached worktree at the recorded commit. Bundle verification output and complete source identity/changed-file hashes are in the source-snapshots06 payload. These are locally built commit identities, not claims that the rejected candidate was merged or published as a product.

Physical PostgreSQL clusters and SQLite database/WAL/SHM files are excluded, along with reproducible obj/bin/cache intermediates. The six short mixed PostgreSQL fixtures were retired separately with the reviewed helper; all six configuration copies, inventories, stop/return evidence and raw-preservation receipts are included, together with `experiments/recovery/tail06-fixture-retirement-01.json`. The thirteen older proposed fixture retirements were paused and never executed. Unique raw, actual ELF/debug/native/generated/nupkg/source bytes are not deleted by this archive operation.

Selection froze only cooperatively sealed inputs, with file size/mtime/inode checked immediately before and after each read. It is not a filesystem-wide atomic snapshot. The original eight-group selection remains unchanged; `selection-addendum-01.json` records the additional six upstream raw packages discovered while checking reused-consumer dependencies. `archive-completion-validation.json` records 5,402 checks for selected/expanded equality, output hashes, generated-source coverage, raw-package resolution, retired-fixture receipts and source prerequisites. No future HostPull draft is selected.

## Publication state

The uploader creates only GitHub blobs and atomically records each successful SHA match. A blob is not a reachable publication. The root agent alone creates the final tree/commit/ref and performs full remote path/SHA/mode readback. `remotePublication: false` in the local upload/build receipts remains historical until that separate publication receipt exists; it must not be interpreted as a successful deployment or product release. No benchmark, profiler, calibration or load test is added to CI.
