# Closed pull-local07: minimal archive budget 05

**Selection/budget only. No archive compressed or uploaded.** Independent 12-process short screen rejects 07 and retains 05; no mixed run or long test is added. Final source selection must also include the completed old2 retirement record and independent review, then freeze every selected byte before packing.

| Proposed group | Files | Expanded bytes |
| --- | ---: | ---: |
| closed-evidence07 | 423 | 25,282,400 |
| ordinary-consumers07 | 216 | 45,930,310 |
| actual-packages07 | 28 | 13,749,593 |
| support07 | 39 | 2,192,009 |

Current selection: **706 files, 87,154,312 B**, plus a thin source bundle/net patch (budget <1 MiB) and final retirement/restore receipts. Estimated compressed payload **25–45 MB**, a planning estimate only. Conservatively reserve **about 90 MB** without assuming any compression benefit, plus small final metadata. Current observed free space is about 89.7 MB; the independently reviewed two-cluster retirement would add 139.3 MB. No broader cleanup is proposed. Stream output directly into parts and stream-verify once; do not create full canonical/roundtrip copies.

## Included artifacts

- All sealed `experiments/pull-local-07` evidence: failed correctness-01 compile identity/log, successful correctness-02 actual ELF/DBG, real generated C#, retained compiler inputs/response metadata, runtime results, source patches, independent reviews, actual ordinary-ELF branch disassemblies, 12-process ordinary raw and identities, drivers/controls and final rejection.
- Both actual `consumers/pull-local07-{sqlite,postgresql}/korda-workload` sources, generated C#, ELF/DBG, consumer DLL/PDB, response/restore/project metadata and build/binding receipts. Redundant bin/obj bodies and caches are excluded; selected compiler metadata is retained explicitly.
- Both unique real `0.1.0-parity07.1` nupkg files, feed manifests, release/identity/build/command receipts. Their compiler/runtime dependencies are already published and will be referenced by exact hash.
- New wrapper07/freeze07 sources; retained05-gap-summary and remaining-space source clarification; both exact four-file consumer cleanup receipts; the reviewed old2 retirement helper/proposal subset and eventual actual retained configs/receipt.
- Planned source bundle: Korda prerequisite `2ea67ce1902f330679c3ebff4d6d5733be20f69c` through `645cfa5f184d65a67fa71455a5f7271ee8469309`, including 3fb8824, c5b1ddb, 8d400ec and 645cfa5. Both rejected test expectations and the failed compile source remain identifiable.

## Restore dependencies and exclusions

Reuse archives01 baseline/Dapper/toolchain, archives02 integrated05 actual outputs/native build identities, archives03 reviewed observer/wrapper support, and archives04 compiler-package gap closure. Four unchanged native image destinations (two consumer out paths plus two correctness runtime paths) will be restored from the archive04 native members through exact SHA/size aliases; both new raw cache nupkg paths alias their unique selected feeds. These aliases are a plan, not yet a claim of final byte closure. No original files are removed by this selection.

All PostgreSQL physical data, SQLite physical databases, bytecode/cache folders, rebuildable object bodies and duplicate native images are excluded. The new 07 PostgreSQL fixture remains physically present and outside retirement scope. Final closure will verify every source and destination hash and record excluded original paths. Later graph/spin investigations live outside this archive.

`selection-budget-01.json` contains the exact current file paths and sizes, draft aliases, exclusions and remaining additions. It is intentionally not a final expanded hash manifest or publication receipt.
