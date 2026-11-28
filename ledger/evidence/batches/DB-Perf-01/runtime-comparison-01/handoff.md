# DB-Runtime-Compare-01 recovery

All eight 1,800-second business intervals are complete. No timed workload is active.
Do not repeat a completed cell because the original two-cell runner returned exit 1:
that return belongs to 02's preserved 14.997119729-second released idle, after its
full business interval. Continuations 03–08 all completed; 7 strict passes plus
1 exact-hash reviewed idle deviation remain distinct.

## Durable evidence

- [Final report](final-report.md), [final state](final-state.json), [full analysis](campaign/analysis/offline-01/summary.json).
- [103-file raw manifest](raw/long-campaign-01/manifest.json), [complete readback](raw/long-campaign-01/verification.json), [checksums](raw/long-campaign-01/SHA256SUMS).
- [Independent review](campaign/analysis/final-independent-review.md).
- [Memory policy](campaign/memory-policy-192.json): C# requests 192 MiB GC configuration; no cgroup or total-process enforcement claim; PostgreSQL server separate, Java uncapped by this policy.

The local raw campaign is `/workspace/scratch/4a4a6f01f129/DB-Runtime-Compare-01/long-runs/campaign-01`.
The frozen input matrix is `campaign/matrix-01.json`, SHA256
`450d0e8762db63dd5dada402c1c1b59797f3cb4207ef655375b6b63ba7e715ae`.
The serial run's final cell exited 0 at 2026-11-28T12:42:27.341481+00:00;
all PostgreSQL instances were stopped by their owner and all client sessions exited.
No database/ELF/toolchain contents are included in the raw-result tarballs; actual
binaries and source/build identity records remain at the documented local paths.

## Publication recovery only

Inspect [Plan #37](https://github.com/IzuSharp/Plan/pull/37) for the actual head and
existing CI outcome. Keep it draft/open. The base published checkpoint before
result publication was `dc0480de708ba5fa4dc87e69339986cc3804e301` with tree
`a91fa97f10ba7b6a5343ba309cef1a87217b8812`. A final publication must compare remote
Git tree identity to the locally reviewed tree and update the branch with an
expected-head lease. Do not rewrite original receipts or frozen inputs.

Korda and Korda-Design are unchanged. Old Plan #35/#36 and Korda #39 are closed
unmerged, with source branches/evidence preserved; Dependabot is untouched.
No product merge/release, Korda optimization, capacity sweep, diagnostic rerun or
additional 30-minute cell is selected. CI remains the existing static/correctness
workflow; do not add a performance invocation to it.
