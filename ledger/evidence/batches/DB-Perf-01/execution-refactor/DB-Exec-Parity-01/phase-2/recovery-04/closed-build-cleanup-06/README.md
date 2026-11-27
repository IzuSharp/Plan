# Closed build cleanup 06 — completed

The root explicitly approved manifest SHA256 `ab53b64d39afe14fc9de9b341809e65d2898355af67b54872f54fcb26b59b309`. Execution completed at `2026-11-27T09:21:37.984547+00:00`: all 308 selected identities/hashes and 21 retained copies passed before any deletion; the intent was recorded; exactly 308 single-link regular files were unlinked. No directory was recursively removed.

Accounted release: **1,167,843,328 B**. Observed available-space increase: **1,125,081,088 B**; concurrent tail06 builds can consume space during the operation. Available space at completion: **1,984,028,672 B**. All 21 retained copies remain unchanged. `cleanup-actual-receipt.json`, `cleanup-intent.json` and `df-after.txt` contain the detailed evidence.

The historical proposal is preserved unchanged as `README-proposal.md`. Four original diagnostic nupkg files remain untouched and are listed in `../archive-recovery-04/pending-worker-d-diagnostic-packages-06.json` for a later incremental archive; no compression was started.
