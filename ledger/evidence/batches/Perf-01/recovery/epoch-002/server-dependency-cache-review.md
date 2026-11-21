# Epoch-002 Server fixture dependency-cache correction review

**Verdict: ACCEPT the exact source and private descriptor for a fresh execution.**
This is an independent source and read-only identity review. It executes no
restore, build, fixture, service or performance load and grants no duration credit.

| Reviewed input | Identity |
| --- | --- |
| Prepared source commit | `c3c6de71032c1f8785893aa19e1e4420cdabfcc6` |
| Caller source index | `4022da032b06a0aa8af8443909da2dd1e38bb26277dcb6dd589fbb33ad10795a` |
| Caller `run.py` | `58717897b5c518ef83046ac9321401cdf6fde244107d321741daa7a991ebf9e4` |
| Private dependency descriptor | `2e14e0548f2de2be17d696338f1ce7ca9a1e4f19d4c82a20eed3c6640474a2d8` |
| Actual completed B18-after execution | `8b79ac99a39a5870053934abd68a6527fe3f98bbceca000708b1ddbd1229c47d` |
| Selected product | `ccff42c0df4141984ef9de497af7cd768753704a` |

## Finding and correction

The original attempt remains interrupted, with no terminal exit or fixture
result. Its preserved restore log reports an unavailable NuGet index and a
missing ILLink package in the empty cache. The original caller/index remain
byte-for-byte in `attempt-001-source`; this review does not revise that outcome.

Independent project-reference traversal rejected the first unexecuted cache
proposal, `5d17bc1`. Its seven-package reference-consumer cache omitted **13**
generator/transitive dependencies. Both fixtures compile source generators.
The corrected source uses the cache path recorded by the actual completed
B18-after execution and independently binds its current dependency bytes.
The older B18 binding did not include this cache inventory; path provenance
and new byte binding are explicitly separate claims.

Read-only verification traversed **8 projects and 14 JIT/AOT lockfiles**,
confirmed **20 locked external package/version identities**, and included
**3 existing runtime packs**. All locked NuGet content hashes match package
extraction metadata. Raw archive SHA-512 values match their sidecars; they
remain separate from NuGet content hashes. All **1,572** selected cache files
and **22** source/lock files were rehashed against the descriptor. All **1,503**
extracted payloads match actual ZIP bytes, including 23 package-root nuspec
names lowercased by NuGet. Unextracted standard OPC metadata is retained in
the private descriptor's explicit list. The [review projection](server-dependency-cache-review.json)
contains only package identities and aggregate verification counts.

## Preserved behavior and remaining execution

The delta adds a local descriptor path and exact SHA, validates the completed
B18 cache-path provenance, and registers the selected cache/source files with
the existing `Context.pin`/final stability check. It changes no package version,
restore flag, audit setting, fixture selector, native asset, affinity, timeout,
assertion or process owner. All fourteen original owned commands, fresh source
worktrees/bin/obj and mode-specific outputs, no-Rust traps and actual native
mapping requirements remain. The new caller parses as Python AST without a
target-module import; the three indexed source files and four preserved
original files match their declared identities.

The complete extracted-file map stays local and must not be published through
an intermediate preparation history. A new label still must produce actual
successful locked restores, builds, four fixture results, native observations
and finite-owner retirement. This source acceptance does not claim those
outcomes or complete B17/B19 component, performance or long-run acceptance.
