# Perf-01 compiler-cache cleanup 005: actual checklist

Root executed the reviewed fixed cleanup on **2026-11-20, 13:04:43.183785–13:05:15.232779 UTC**, under the exclusive global timing lock on CPU8. The fresh attempt completed successfully in **32.049122112 seconds**. It removed only the exact reproducible compiler intermediates and extracted SDK files in the reviewed allowlist; it grants no functional, performance, capacity or long-test acceptance.

| Candidate kind | Files | Apparent bytes |
| --- | ---: | ---: |
| Inactive Rust intermediates | 1,054 | 1,283,934,968 |
| Expanded SDK members | 6,748 | 1,769,655,265 |
| Total | 7,802 | 3,053,590,233 |

Actual free space changed from **3,200,688,128** to **6,261,362,688 bytes**. It remained below the 10 GiB PostgreSQL long-test preflight, so further headroom is still required. The result does not promise available space after subsequent builds.

## Fixed scope and preserved inputs

The selection covered only the two completed retirement source targets and SDK cache members in the two fresh 004 build directories and five completed B18/B15/B19/B20 gate directories. It was bound to the exact completed 31-command producer receipt and its actual build/artifact inventories. The B19 ordinary and external consumers share one private cache. All ordinary `bin`/`obj` and proof files were outside the candidate rules; only the existing permitted Rust `target` intermediate suffixes and exact SDK archive members were eligible.

The fixed protection set retained **42 package archives, 124 manifest sources, 2,649 actual-artifact hashes and 3,211 absolute references**. It includes prior accepted inputs, the fresh native/package/application assets, all B17 actual inputs, the native-component logs and retained library, B18 original inventories and package snapshots, current B15/B19/B20 actual outputs, and the B19 external reference DLL and generated layout proof. Four hard-linked candidates were excluded. No raw evidence, tested output, source, package archive or measurement state was removed or promoted.

For all 6,748 SDK members, the executor compared every decoded byte and CRC with the current expanded file. It fully hashed every selected file and every retained archive, rechecked anchored ordinary single-link identities, rehashed protected inputs before and after, and wrote a durable verified intent and completion for each removal. The actual journal contains the byte hashes and original identities needed to audit each action. There were no reconciled absences or resumed operations.

The cleanup source changed only the original 004 engine's fixed inventory path, inventory hash and fresh output path. Every function body remained byte-identical. Root reviewed that three-constant difference and reused the original 11 temporary safety checks; no unchanged safety test was rerun. The independent public projection read only the small terminal result and archive-hash list and reconciled them against the fixed preparation summary. It did not replay the full journal, rescan selected paths or repeat archive/artifact hashes during timing.

## Retrieval and reproducibility

[public-summary.json](public-summary.json) contains the numerical result and complete receipt hashes; [manifest.json](manifest.json) binds this checklist.

- Actual result SHA-256: `730633b8801386f204d7f8cf86c1ed2ead91392d64111f5b5fd985317eb3d1e4`.
- Fixed inventory SHA-256: `9b90834c669de58689809a9f6f0e90577712eba28cba88445c8df89312f03aab`.
- Actual journal SHA-256: `70cd28fdc78e88e9d7c411a438f15676e4b1a6b62e0b3627a5acc53b0f63bfab`.
- Retained archive-hash list SHA-256: `29596c6ced7f90b7066b06a1acbef67c08a197e76e79a0da9a80efa256cade79`.
- Executed cleanup source SHA-256: `1384d3276fce24ee351f3a6f773fdd97a2cec6c9a118937039ecad9d201f1309`.

Private inputs, the complete allowlist, actual execution records and per-file journal remain in the measurement workspace under compiler-cache-inventory-005 and compiler-cache-cleanup-005. Extracted SDK bytes can be reproduced from the retained hash-bound NuGet archives; removed Rust intermediates can be rebuilt from the recorded sources, locked tools/dependencies and build options. Actual executables/native outputs were retained and do not need reconstruction for their recorded evidence.

The public synthetic checklist remains in Git while repository history is retained. Private workspace records have no promised remote retention period, and no remote raw archive is claimed. No regeneration or restore was executed by this checklist.
