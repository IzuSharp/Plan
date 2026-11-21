# Perf-01: independent review of the interim HTTP projection

Reviewed UTC: 2026-11-21T08:10:02Z. Reviewer: independent `perf01_grpc_review` agent.

**Result: no blocking defect found in the bounded metadata and publication review.** This is a technical review of the three identified public artifacts. It is not a GitHub approval, another benchmark run, a replacement noise decision, or task acceptance.

## Reviewed public artifacts

| Filename | SHA-256 |
| --- | --- |
| `comparison-http-001.sources.json` | `0f61d9e69b425cd752d029068c9f6022a0f5efe8a807e0799a9e2e2791bf9e5d` |
| `comparison-http-001.md` | `f638cb1d25a65e6e4e3adb9c4d74a469b62fe026eae2d7ecf3670250bd30905f` |
| `comparison-http-001.json` | `29b4910401b0abb6867a82a1d515ac6a5d72f992ba1818a20e39b22b5ba74599` |

These three artifact hashes were checked. The four completed `execution.json` files were read and their small metadata hashes checked; the four corresponding `comparison.json` documents were read. Comparison and underlying payload hashes below are the identities already recorded by the completed execution, not new payload verification.

| Profile | Checked execution metadata SHA-256 | Recorded comparison SHA-256 |
| --- | --- | --- |
| http1-small | `b99ee3df1d94888d3ea8d2cef5cb443ccb7ba4e8c8154fa169fb7cee6e8dace6` | `eb29fd329644b1f807b325e236e3a66b5657fe5a00485ab022ea956486db5ca3` |
| http2-small | `e4ababa9118c6f02c488c12c3a6d1418019f7349b47fc98621b54bbb20f8f7f0` | `1ed273bd1f53c3b9a995d7254ab2286bdd586a5bb39e3de69ccf0003b53940e4` |
| http1-large | `d1459accea866f056951e87a3bf147468a171c282524668e6bd6e1f66b56e378` | `a3310bc4dd988a1b275f4ebc8f62784a71b6a4f256f0ac6c5a605267c771fadd` |
| http2-large | `1430e38e7ae1e5ad04e624badfda7f9a77f19193a92c7f16679159665183debd` | `ce7961e19119177289a34ebab77fefdf4800d4566c6f15c7ab579958e58dfea0` |

The preserved identities match every process's source metadata: before product `ea5fa528035d025bd7a28698ee7c71194432236c`, after product `2f40348c3db80a4fbee7a99e721b374a597b16df`, and common driver `2e3995df8d86583ee9443348276ca8d918056bfc`. Final binding SHA-256 is `8f8616f2932dd1c033309e177efa63429829f9ffa2b728a182406d943efdfa8d`; measurement source-index SHA-256 is `6b1d1e8ec6ee80271fdbbeb1c6d13909b92ca13c7a28cbc4fd4085f98f6a4c2c`. The direct role remains the common direct Rust driver, without an invented NativeWeave product/package identity.

## Findings

- All four completed profiles, 36 independent workload processes, 90 process/case observations, 10 aggregate cases and 76 finite command summaries match their original metadata. All command summaries report exit zero and retirement. Eligibility, service-standard results, zero unexpected-error counts and zero correctness-failure counts are preserved; this review does not replay the original verifiers.
- The explicit projection agrees with the original retained fields: load configuration, time windows, integer counts and payload/message/encoded-byte totals, outcomes, process resources, managed-GC observations, native gauges, source/package/native/executable identities and filename/hash provenance. Package and native identities were checked against metadata for every process, without opening binaries or archives.
- All copied before/after/direct metric deltas retain their sign and denominator. Arithmetic cross-checks use `(left - right)` and `100 * (left - right) / right`, retaining null where the original percentage is undefined. The 82 numerical Markdown rows checked against the JSON agree at the displayed precision.
- Original before-to-after noise objects are copied exactly for all ten cases. The reader's after-to-direct gaps are arithmetic comparisons, with no invented direct-comparison noise test. Mean, p50, p95 and p99 are equal-weight means of the three process metrics; p99 is not pooled, and no p99 or resource significance is claimed.
- The headline RSS values are the maximum of the three process peaks. The original mean of process peaks and its original changes are separately retained and labeled. CPU, RSS, allocation and gauges retain whole-profile scope. Managed allocation uses the recorded partial sampled bracket; direct managed-GC values remain null/N/A. No per-case resource attribution or exact bytes-per-call inference is made.
- Unfavorable observations are retained explicitly: HTTP/2 tiny mean-process p99 rises from 7.362738 to 15.087253 ms; HTTP/1.1 8 MiB upload p99 rises from 49.607400 to 58.779180 ms; HTTP/2 large download/upload mean changes are +4.028965%/+2.603341%. Original applicable mean decisions remain inconclusive or within-band. The combined-version data do not attribute changes to an individual patch.
- Byte/correctness reporting does not invent a standalone per-request content-hash flag. Literal encoded-byte fields do not become TLS/framing measurements or compression evidence. No negotiated HTTP compression benefit is claimed. Sampled native-byte maxima remain sampled observations, and positive direct-Rust available-permit capacities are not relabeled as outstanding owners or as zero.

## Public boundary and acceptance limits

The public JSON keys and values, source index and Markdown were checked for operational paths/maps, process identifiers, environment values, addresses, and certificate/key material. No such operational disclosure was found. Filenames contain no path components. The retained slash-separated A21 baseline identifiers are logical comparison identities; the index's exclusion-check label is descriptive metadata, not an operational value. Source, package, native and executable hashes are preserved only as explicit provenance.

This review read completed metadata on CPU 8 and wrote only this review. It did not import project modules, start a build, run a load, scan raw records, hash payloads, create archives, or write remotely. It grants no capacity, cancellation/backpressure, 30-minute, other-domain, or historical execution credit. The separate SQLite C16 service-standard failure remains unaccepted. The reviewed files are an interim public projection; the original evidence and existing acceptance gates remain authoritative.
