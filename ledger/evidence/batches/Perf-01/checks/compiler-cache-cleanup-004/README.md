# Perf-01 compiler-cache cleanup 004: actual preservation checklist

The reviewed storage operation completed on **2026-11-20, 12:04:38.673797–12:05:20.679869 UTC** (42.006109586 seconds), under the exclusive measurement lock on CPU8. It removed **10,532 reproducible cache files, 4,590,873,180 apparent bytes**. It ran no product workload and grants zero performance or long-duration credit.

| Selected class | Removed files | Apparent bytes |
| --- | ---: | ---: |
| Rust intermediate objects and metadata | 1,844 | 2,438,289,811 |
| Rust incremental cache | 1,272 | 332,808,758 |
| SDK members reproducible from retained nupkg | 7,416 | 1,819,774,611 |
| Total | 10,532 | 4,590,873,180 |

Observed free space was **4,590,960,640 bytes before** and **9,192,603,648 bytes after**. These observations describe this operation only; later builds can consume that space.

## Preservation and verification

All **222 original SDK archives**, totaling **3,756,825,266 bytes**, remain. The executor fully hashed each archive and all **242 protected actual artifacts** before and after cleanup. Each of the 7,416 selected SDK members was compared against its entire decoded archive member and CRC before unlink. Every selected file was separately hashed, checked as a regular single-link file, and checked for unchanged filesystem identity before unlink. The protected references came from 88 actual manifests; none of the 668 protected absolute references overlapped the selection. Thirty-three multiply-linked candidates were excluded.

The narrow Rust selection included only incremental intermediates and explicit compiler metadata/object suffixes in reviewed inactive roots. Actual test/application executables, shared libraries, packages, source, logs, manifests and raw measurement records were preserved.

The append-only journal has exactly 10,532 verification intents and 10,532 matching unlink completions, plus one start and one end record. There was no resume or inferred-absence reconciliation. A separate post-operation review matched every pair, confirmed all selected paths absent, rehashed all 88 protected manifests, checked the filesystem identities of the 222 retained archives and confirmed all 242 actual artifacts still present. That reviewer did not repeat the executor's large archive/artifact hashes.

Eleven temporary-file safety checks passed before the operation, including the explicit inactive `deps` metadata scope. Their wrapper receipt records 0.185349269 seconds and zero actual cache removals. The production operation completed on its first attempt.

## Receipts and recovery

[public-summary.json](public-summary.json) retains exact numbers and hashes; [manifest.json](manifest.json) binds the public files. The execution receipt SHA-256 is `89c76e62ded726cc881d0c4436dd5dec7cecbd550a3157fc579a8304028212c1` and journal SHA-256 is `0ca794759d8f81c7c1936332457c80098fdbba49a71957af3ba1ca1145de5704`. The immutable inventory SHA-256 is `ce1e216903043c18c5c272a91ef06a342d8e35d18df7939b5caedaf80468c5f7`.

Expanded SDK caches are intentionally incomplete. An old consumer may require restoring exact selected members from retained nupkg files, checking archive and decoded member hashes from the journal; ordinary NuGet restore may trust existing completion metadata. Rust intermediates can be reproduced from the pinned source, toolchain and dependencies. Actual tested executables and their dependencies remain available.

The full inventory, durable per-file journal, archive hash list and operational receipts remain in the measurement workspace. These public synthetic counts/checklists remain in Git while repository history is retained. No remote raw operational archive is claimed. No accepted or failed measurement classification changed.
