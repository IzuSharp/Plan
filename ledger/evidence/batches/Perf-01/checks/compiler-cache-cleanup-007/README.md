# Perf-01 compiler/cache cleanup 007: actual checklist

Root executed the fixed cleanup on **2026-11-20,
14:43:41.016545–14:44:13.949965 UTC**. The fresh attempt completed in
**32.933459555 seconds**, with the exclusive global timing lock on CPU 8.
It removed only the reviewed reproducible compiler/cache inputs from the
completed final003 build. No functional, performance, capacity or long-test
acceptance is granted.

| Selected kind | Files | Apparent bytes | Recorded allocated bytes |
| --- | ---: | ---: | ---: |
| Archive-backed non-NativeWeave NuGet members | 5,971 | 1,602,458,406 | 1,614,307,328 |
| Rust compiler intermediates | 528 | 634,623,695 | 635,691,008 |
| Native AOT compiler objects | 8 | 213,969,051 | 214,003,712 |
| Total | **6,507** | **2,451,051,152** | **2,464,002,048** |

The legacy executor label `sdk-extracted-member` covers the selected
non-NativeWeave NuGet members; it does not mean every selected member belongs
to the .NET SDK. Free space increased from **3,307,003,904** to
**5,735,280,640 bytes**, an observed difference of **2,428,276,736 bytes**.
These filesystem observations are separate from the selected-file apparent
and allocated totals. The final observation remained below the 10 GiB
PostgreSQL long-test preflight and does not promise headroom after later work.

## Verified scope and retained evidence

The immutable inventory names the actual completed final003 product source
`2e3995df8d86583ee9443348276ca8d918056bfc`, tree
`246de1eb9368efbc62f46ce10c4a8a894d646152`. Its protection closure retains
**49 archive inputs, 156 manifest/source records, 3,637 actual-artifact hashes
and 4,299 absolute references**. Actual tested executables, native libraries,
package archives, source/proof inputs, raw measurements, logs and database
data remain outside the cleanup scope. The inventories and original
passed, failed or interrupted execution records keep their original outcomes.

For every selected NuGet member, the executor compared all decoded bytes
against the extracted file, checked length and CRC, and computed the original
SHA-256. It hashed each Rust/AOT intermediate. Every AOT object has a recorded
successful publish provenance and a protected actual executable; removing
that intermediate does not require reconstructing the tested output.
Protected manifests/artifacts and the retained archives passed the executor's
before/after checks before it wrote the completed result.

The actual journal contains **6,507 verified unlink intents and 6,507 matching
completed unlinks**, with one attempt-start and one completed attempt-end.
Each intent precedes its own unique completion, names an exact selected file
and records the same file hash as that completion. All **5,971** archive-member
intents include unique durable restore-record references, exact retained
archive hashes and successful full-byte/CRC comparison markers. The eight AOT
intents match their recorded provenance indexes and protected executable pins.
There were no resumed files or reconciled absences.

## Checks and projection method

**No new safety tests were executed for cleanup007.** This record references
the existing **ten temporary-file checks from cleanup006**, receipt
`87032124db515dcb6bb4e0787fcc379186c7ed66f70fbc033de0e6e70fb7f4dd`,
as prior validation of the reused cleanup and member-restoration mechanics.
Those checks are not relabelled as a fresh 007 run, a new functional gate or
a performance test. The current selection and actual operation have their
own distinct inventory, source, journal and result identities below.

This public projection reads seven bounded metadata inputs: the completed
result, existing inventory, retained archive-hash list, AOT provenance,
attempt-start record, prior public check summary and the **11,064,035-byte**
per-file journal. It reconciles the selected counts/bytes, every intent and
completion, ordering, restore references and recorded hashes. It does not
inventory current paths, read selected payloads, rehash package/binary
contents, decode an archive, restore files, or rerun any test/cleanup.
The actual executor's verification and this metadata reconciliation are
reported separately.

## Retrieval and reproducibility

[public-summary.json](public-summary.json) contains the copied numbers,
verified counts, booleans and original receipt hashes.
[manifest.json](manifest.json) binds the two public files.

| Retained evidence | SHA-256 |
| --- | --- |
| Actual completed result | `8b5f0d938930056292674af8bdbdb1602f81c2e6cbbea4438e9794d5e2ae736b` |
| Fixed inventory | `6849297b401ca89f215d8b658d3cbb3693ee9a88508c98aa7facb1f8159ff13b` |
| Actual journal | `30c86855bf2ca35e3aaac27f2540b23a738fac91f04da130e1b1a341ba08c974` |
| Retained archive-hash list | `b135fe9ce6093789dbf7199c6c51db123793a5b40144e2b69a77ba99fb40cc2a` |
| AOT producer provenance | `7b090e8c7ef8e61a9546c250a06a4c32c6423409137dda3e7efc5be0b99b9793` |
| Executed cleanup source | `f7e66fdde299bdcf75c78e004a843a24e18b0a669476d881fa6787880ae82bfc` |
| Explicit member-restore source | `112cec0909fb0f372db1afc9db08f263118ddaa91c1d26341082721c27bd23b6` |

The private execution journal and per-member restore proofs remain under
compiler-cache-cleanup-007; the immutable inventory and AOT provenance remain
under final003-cache-inventory-001. Before reusing an affected extracted
package, use the exact restore command recorded in its original verified
intent. That helper validates the retained archive, decoded bytes and
ordinary mode and refuses to overwrite existing output. A NuGet cache marker
alone does not prove that removed members have been restored.

The compiler intermediates can be rebuilt from their recorded source/project
inputs, locked tools/dependencies and original build/publish options in fresh
isolated outputs, after any required cache restoration. Byte-identical
intermediate reproduction is not claimed. Actual tested binaries remain
protected. This checklist performs neither restoration nor rebuilding.

The synthetic public checklist remains in Git while repository history is
retained. Private workspace records have no promised remote retention period;
no remote raw archive is claimed. Absolute host paths, process identifiers,
command arguments and environment values are excluded from this public set.
