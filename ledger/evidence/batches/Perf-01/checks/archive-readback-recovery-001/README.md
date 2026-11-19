# Fixed-commit synthetic archive readback

The existing codec transport smoke was published to `IzuSharp/Plan` commit
`de38d6ed6e8ff919d9263edffc2fdf29b3b2a8f9`, branch
`task/Perf-01-archive-readback-linux`, at
`ledger/evidence/batches/Perf-01/raw-archives/codec-smoke-001`.
All 14 repository files were retrieved with `github_fetch_file` and base64
encoding at that exact commit. Each remote byte sequence equals its local
source, and every Git blob SHA, SHA-256 and length matches. The largest actual
gzip blob transferred and retrieved was 961,665 bytes.

The archived 10 original files (23,921,929 bytes) were restored with the existing
archiver and all original SHA-256 values matched. `readback.json` records actual
argv, UTC start/end, exit codes, source hashes and lock/CPU identity.

`historical-verifier.py` preserves the unchanged NativeWeave verifier bytes with
SHA-256 `fc179e94458d5d86faf7fda67790d1d18d187613bad22b64022f65c478215e2f`.
Those bytes were found in NativeWeave local committed history at
`6b0c74de9c03e3c28c09398ae28e82932b7e4fda` (Git blob
`abe47ca516a83dab5309067a1ff2966981075533`) and are included for independent
reproduction without depending on that historical branch being published.
This artifact-only copy is not the current long-run verifier.

The actual replay exited 1 as expected and reproduced the original rejection:
codec exit/drain/idle observation was incomplete. Only the output directory and
verification timestamp differ in the receipt. That early rejection is not a
claim that every long acceptance gate ran. Complete raw-file equality is
separately proven by the archive checks. Long-duration credit remains zero.

The archive has no scheduled expiry while its Plan commit remains reachable.
Keep the archive branch or integrate the commit into retained project history;
this is not a guarantee against repository deletion or history rewriting.
Future formal archives still require their own complete publish/readback proof.
