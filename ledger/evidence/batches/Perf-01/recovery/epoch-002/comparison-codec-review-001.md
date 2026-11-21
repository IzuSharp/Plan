# Perf-01: independent review of the completed codec projection

Status: **accepted as a presentation-only public projection**. No blocking discrepancy was found. This review does not rerun a codec operation, certify raw evidence again, add a statistical decision, establish capacity, or grant long-duration acceptance.

## Exact reviewed files

| File | SHA-256 |
| --- | --- |
| `comparison-codec-001.sources.json` | `b732ace6db7f61b7a44a6a57b312165eac1faae81a8b8d3626c79e8e71108dc2` |
| `comparison-codec-001.json` | `3b9fbd63218594cd47e82f2c445c54c662a91b86b9f28a2d17daef0d385366ea` |
| `comparison-codec-001.md` | `2a6d1e0b293fb260c5eda9fb5e7b0ee944bc8513efb00d6e17bb486af323501b` |
| Original codec-w1 comparison | `fcd8a2a78fc50ae1bb83d45049aa326e38a8cc714a0d92f19d546103c00071cf` |
| Original codec-w2 comparison | `05c9d87ee112f765f940b034a270d139cc1ca25439da222dea4d25ba49719a3e` |
| Original codec-w1 execution | `0eb87978e3a5e7379eed4b9e0bb225adc0dbba364f83c770806eec6b06f3415f` |
| Original codec-w2 execution | `feb6eadca83b2b64cd307ba54ff7f67e892d131ad15a8c8b057304e4d59c374e` |
| Original `codec_compare.py` | `6f09ac17bc60544ef97c147a47cada66344f6ea068318821f204da0a6e468663` |

## Verified projection

Bounded reads on CPU 8 compared the public files with the two completed comparisons and executions, 48 completed small plan/result metadata files for 24 processes, two codec build manifests, and the corpus manifest. Source inspection covered the existing codec comparison reader and the common managed/direct codec timing and validation paths. No raw JSONL, corpus payload, package, executable, or native binary was opened or hashed; no target code was imported or run.

The final check completed 3,726 literal/format comparisons without a discrepancy. All 64 complete observed/noise/delta row trees equal the original comparison values, including all before/after, after/direct, and before/direct results and the original reasons for undefined or unavailable percentages. All 256 detailed Markdown numeric rows match the JSON formatting. All 26 finite command receipts report zero exit and retirement. Every process plan/result hash matches its recorded completed metadata provenance. Build, native, package, source, and corpus identities are preserved as supplied receipt values.

The original decisions remain intact: codec-w1 has 5 of 32 public-call mean improvements and 5 full-operation mean improvements; codec-w2 has 11 of each. Neither profile has a before/after mean regression decision in those two scopes. No arrival-mean improvement is established. Adverse and inconclusive direct-Rust results remain visible; they are not converted into a blanket parity or improvement claim.

The report correctly distinguishes pooled operation means and nearest-rank tails from the three independent process means used by the original noise method. It distinguishes raw MiB/s per summed call time from wall throughput in the fixed mixed workload. The owned-buffer public call excludes later consume/release work, which remains separate. The managed comparator retains its narrower valid-corpus call scope and the owned-label alias; no full NativeBuffer or strict trailing-input equivalence is asserted for it.

Whole-process CPU and maximum sampled RSS retain the original mixed-profile summaries. Per-process resource observations and integer phase/byte/success counts remain available. Derived FFI/copy counts are labelled derived. Drain GC/allocation counters remain cumulative lifecycle observations. Missing direct GC and native-owner values are represented as null; they are not fabricated zero observations. NativeWeave's observed zero live/capacity/active drain counters remain separate from cumulative releases.

## Publication and acceptance boundary

An explicit key/value privacy check of both public JSON files found no operational absolute paths, PIDs, environment maps, TLS material, or endpoint addresses. Source repository paths and filename/hash provenance remain. The Markdown describes these limits and does not infer network compression benefits from the independent codec experiment.

The projection preserves completed evidence only. It does not erase the SQLite failure, the gRPC regression, incomplete capacity work, or outstanding 30-minute segments. Actual process execution credit belongs to the original receipts, not this review.
