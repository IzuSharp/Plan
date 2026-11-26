# Final original evidence retained and verified

The original four serial 1,800-second cells completed before this retention
operation. Arithmetic/identity acceptance is recorded separately in
[the final report](../final-report.md). The unchanged archive helper launched
no workload and grants no acceptance by itself.

| Object or check | Observed result |
| --- | --- |
| Archive | [evidence.tar.gz](evidence.tar.gz), 9,895,505 bytes |
| Archive SHA-256 | `a2163d52068b9fb062b140339b183c3626c2e8ad935c3ee2f75b35f9ef2c95bb` |
| Manifest | [manifest.json](manifest.json) |
| Manifest SHA-256 | `bb1f5e54598d9257b3d028a67920db53858131e53814c511088a20592a856afa` |
| Archived originals | 432 files; 59,615,666 original bytes |
| Explicitly recorded exclusions | 1,326 files; 201,758,776 original bytes |
| Original union inventory | 414 pinned entries, SHA-256 `7d0062a17575d4d9b9bd720ba00fc31ba13a13a05891da438b674ca15cf9fd8b` |
| Original-input and root inventory checks | Unchanged |
| Complete archive member/gzip readback | Passed |
| Command exit | 0 |
| Actual operation UTC | 2026-11-26T10:47:42.170792+00:00 through 2026-11-26T10:47:44.818060+00:00 |

[command.json](command.json) retains the exact argv, helper/inventory hashes,
stdout/stderr paths and exit. [receipt.json](receipt.json) is the actual tool
result. The inventory and manifest retain every original path, byte count,
content hash and inclusion member or exclusion reason. Raw final JSON/JSONL,
command/runner/fixture/server records, source/generated code, restore/validation
text, final analysis, identity checks, host observations and independent reviews
are preserved. The original pre-final archive and metadata are included as an
identified dependency; it preserves the prior short/baseline/diagnostic and
rejected-experiment evidence.

The final helper reads and verifies each top-level archive member, rehashes each
registered original, and checks retained-root inventories. The nested pre-final
archive is verified as one byte object. Its earlier inner-member readback remains
supported by its distinct prior receipt; this operation did not recursively
re-run that historical readback.

PostgreSQL pgdata, SQLite files/sidecars, packages, and compiled binary/object
bytes are explicitly excluded with their real hashes. The source/generated/log
metadata beside binaries is retained. `binaryRecoveryClaim=false`: this is not
a ready-to-run database/package bundle, and a future rebuild is not asserted to
reproduce excluded bytes. The original files were not deleted.

The two proposal scripts are retained beside the final report. Their initial
here-document construction failure is preserved within the original recovery
archive; it did not execute an archive or modify source. This final retention
operation succeeded on its first actual invocation with a fresh output path.
