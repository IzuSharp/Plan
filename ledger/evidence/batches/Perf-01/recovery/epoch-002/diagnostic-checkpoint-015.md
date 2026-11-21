# Perf-01 — diagnostic checkpoint 015

This checkpoint records completed diagnostics and evidence retention. It does not replace the original SQLite C16 service failure or the formal gRPC server-stream regression. Formal comparisons remain 15/16 complete, capacity executions 0/15 and accepted 30-minute segments 0/10. The ten required effective-load segments still require actual execution on the final matching artifacts.

## Completed observations

- [gRPC buffer ablation](grpc-buffer-ablation-001/README.md): twelve original TLS cells, 37 finite commands, all retired. Streaming allocation fell approximately 97% and CPU fell, while all three server-stream and client-stream p99 pairs increased. After-idle RSS increased in every pair. The buffer-only candidate remains isolated and unselected. [Independent review](grpc-buffer-ablation-review-001.md) checked the original metadata and arithmetic; unavailable means remain unavailable.
- [SQLite full-lifecycle analysis](sqlite-tail-diagnostic-analysis-002.md) and [measured-window transaction-span supplement](sqlite-tail-hold-supplement-003.md): both corrected diagnostic loads completed with durable-oracle and cleanup checks. The selected 1,501 create spans per role place 65.24%/66.04% of their managed transaction proxy in before-take to retirement-observed intervals. This includes taking/materialization and scheduling; it is not physical lock time or a pure timer measurement. Original diagnostic cycle p99 increased from 207.031034 to 227.100834 ms; the formal 567.131236 ms failed sample remains preserved.
- [Two-constructor scheduling source review](binding-retry-1ms-source-review-002.md): the isolated a5748 candidate uses the existing 1 ms interval at the Data and Server consumers. Shared coordinator/ownership/native code is unchanged. The complete scan and possible Timer overlap can raise idle CPU, so source review alone does not select it.

## Actual candidate B18 verification

The original supplied-native verifier completed from **2026-11-21T10:14:32.574758+00:00** to **2026-11-21T10:18:16.172412+00:00**, with the outer command retired and no remaining owned processes. Managed source was `a5748ad4e03825e3da7706d074887952da6c2d43`; native source was `2f40348c3db80a4fbee7a99e721b374a597b16df`; the supplied Server SHA-256 was `8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0`.

The actual suite passed 1,036 JIT assertions / 598 retirements and 1,037 AOT assertions / 595 retirements. All 18 assembled commands and 25 independent-package commands completed successfully. The original four-mode HTTP/2 + TLS package checks and ordinary-code edit consumption ran through the unchanged verifier. This functional result provides no short-comparison, capacity or long-duration credit. The same frozen TLS application comparison remains the next experimental step.

## Resource-series export verification

The unchanged resource projection helper passed **22/22** synthetic cases under its original bounded owner. The earlier fixture attempt is retained as a failed attempt: its checker incorrectly rejected the approved boolean identity/affinity availability flags. The correction narrowed the fixture expectation only; it changed neither the projection helper nor a workload acceptance predicate. Actual project resource-series publication remains a separate step.

## Original raw evidence retention

Archive `NativeWeave-Perf-01-epoch002-postgresql-c16-raw-001.tar.gz` contains the 24 completed PostgreSQL C16 observation/event files and a restore map. Its exact size is **28,685,140 bytes**, SHA-256 **`568d263ecdf6f500f509a252f8cbe3dcd995b8f04130ae1d533c207af8501092`**. It was saved in the project owner's private file collection, retrieved to a distinct destination, and all 25 archive members were rehashed successfully. Original files remain present at this checkpoint.

The archive is private owner evidence, not a public CI artifact. Retention lasts until owner deletion or applicable account/service policy; no fixed automatic expiry is asserted. The exact retrievable file/version identifiers, original execution/result hashes and readback timestamp are in [the numeric checklist](diagnostic-checkpoint-015.json). Public numeric reports are ordinary Plan Git evidence and persist with repository history. This archive does not replace the public before/after tables or the required public resource-series projections.

All timestamps in this repository checkpoint are UTC. No environment maps, TLS credentials, process IDs, native addresses or machine paths are published here.
