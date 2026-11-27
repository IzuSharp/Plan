# Closed-tail06 archive — planning state only

The current plan selects **2,129 files / 541,484,769 expanded bytes**, before small source patch/bundle capture. It is **not a frozen archive selection**: the newly authorized 12 x 30-second, rate500 mixed gate and its closed reviews must be added after completion. No compression, archive payload creation, upload or remote ref change has started. All 1,800-second and before-long measurements were cancelled by the user and are not pending acceptance gates.

## Current selected groups

| Group | Files | Expanded bytes |
|---|---:|---:|
| ordinary-consumers06 | 216 | 98,800,360 |
| diagnostic-consumers06 | 732 | 201,460,888 |
| correctness-negative06 | 159 | 119,704,213 |
| tail-evidence06 | 746 | 68,621,248 |
| wrapper-recovery06 | 104 | 2,655,789 |
| legacy-worker-diag-packages06 | 4 | 27,456,713 |
| source-files06 | 165 | 5,108,768 |
| compiler-package-inputs06 | 3 | 17,676,790 |

`selection-plan-02.json` contains every current path, size and stat stamp, plus explicit exclusion entries. Its SHA256 is `b3fae03894481ff918650729075aa40f4f5121eebf501b6000954a7d748017fc`. Actual correctness and negative-test publish ELF/debug/native outputs are retained; the negative exit250 remains a failed-runtime negative control and is not promoted to correctness success. All existing mechanism/ordinary raw, original review/error/attempt identities and source controls remain selected.

## Storage budget

Estimated compressed output for scheduling: **160–260 MiB**. This is an estimate from previous artifact archives (~25–30% total compression ratios), widened for already-compressed nupkg inputs; no new compression probe or measurement was run.

The disk decision uses the size-based conservative budget instead: **578,596,314 B** for streamed parts and metadata, including **7,773,434 B** of source-capture allowance. Against the last small availability observation of **1,087,422,464 B**, that leaves **508,826,150 B** ignoring other activity. There is no present evidence that archiving itself requires cleanup. Recheck actual free space and the added mixed evidence when the quiet window ends.

Use the exact reviewed restorer SHA256 `b24e6dceb0f7ad9f6e394b267651f18bc62039db2931e20a4a51761b40cf273c` from archives03 unchanged. Stream tar→single-thread XZ→4MiB parts; verify the parts and every tar member by streaming. Create no whole canonical tar/xz or extraction roundtrip copy. Run archive compression/hashing only in root-approved nonmeasurement windows, CPU8/nice19.

## Package path closure

The four old Worker-D diagnostic nupkg files total **27,456,713 B** and are explicitly selected to close the previously reported payload gap.

The six new consumers reference nine distinct raw nupkg dependencies. Three compiler inputs—Microsoft.DotNet.ILCompiler, Microsoft.NET.ILLink.Tasks, and runtime.linux-x64.Microsoft.DotNet.ILCompiler, all11.0.0—were not found by exact SHA in earlier expanded-member indexes. Their three original raw archives total **17,676,790 B** and are now individually selected. This does not select or duplicate their unpacked caches.

The six new provider raw-cache paths are **not asserted to have been archived at those paths**. Their build/binding receipts establish the same exact SHA as the selected original feed nupkg. `restore-alias-plan-01.json` lists each original cache destination, canonical feed source, expected length and SHA. The later restore entry must keep the verified streaming restorer unchanged, then verify source bytes and create these missing aliases by byte-copy with contained-path/symlink checks; it must accept an existing destination only when size/SHA already match. A changed destination must fail, and mutable caches must not be hardlinked to the feed. This small alias hook remains to implement/review/test before claiming one-command complete restoration.

`package-dependency-closure-02.json` records all nine dependencies and the six explicit planned aliases. Actual payload hashes will be checked during archival and again at restore; no fresh bulk hashing occurred during this selection pass.

## Source and dependency recovery

Capture one small source patch/bundle per four distinct measured source heads: ordinary4a9e4435, diagnostic-before197f0d34, diagnostic-tailba4e7ec9, negative4efce12f. `source-worktree-map-01.json` preserves the additional ordinary provider worktree names sharing the4a9e4435 source, avoiding repeated whole repository bundles.

Reuse pinned archives01 (`b54054bd1f3befe94e1817cc29f494bd782854b9`), archives02 (`27e0f35709036b0737ed101ba6472ce1461c0538`) and archives03 (`d7e2d96db38e2879e0318692e00575158db42a77`) for original baseline/Dapper/runtime/toolchain and prior actual artifacts, together with their explicitly documented Stage1 dependencies. Proposed publication location is `phase-2/recovery-04/archives-04`; root owns final tree/ref publication.

## Exclusions and pause

Physical PostgreSQL and SQLite fixtures, unpacked caches, .o/.obj/.a, bin duplicates and compiler work directories are excluded. Actual out and correctness/negative publish artifacts, generated code, response/asset metadata, raw nupkg, source patches/identities and complete raw logs are retained. All original local raw and artifact files remain untouched. The13 old PostgreSQL fixtures and their proposed retirement remain paused; no space cleanup is justified by the cancelled long-run target.

Current state: quiet for the root short mixed gate. After root explicitly ends quiet, incorporate the new sealed evidence and reviews, reselect with fresh closure declarations, and reassess the bounded disk budget before any compression.
