# Perf-01 — independent SQLite transaction-span supplement review

**Disposition: accepted for additive diagnostic publication. No blocking finding.** This is a source and completed-derived-metadata review; it grants no performance, capacity, long-duration or execution credit.

The reviewed supplement is bound to source index `d22669405042f20c549db5d4d17813cec4f5992050dcdfaa33a26be15eae94ba`, Markdown `1eb4a96f31324308b995574c33b507f90dff2c3388be0e3542169630faaa1f1e` and JSON `5eb4e0c63f5364b5748c336fe9064dcccd7ea214fb73a35765bdb70369c78ed3`. The unchanged earlier analysis is `b51259c3d178cd030c1c0ae2b57ad15aa3caf627017cc6173aa4959ecefd1ec9`. Exact machine-readable identities are recorded in the companion review JSON.

## Findings

The analyzer source (`analyze_hold.py`, SHA-256 `4c27afc0e6135d0524d087db3fcaa47a5e3a89d9aae19624664e21d93f620527`) clips each operation interval to the same per-create Begin-exit → Commit-exit proxy, merges overlaps, and separately retains cross-segment overlap and uncovered time. The union helper is at lines 45–57, per-create summaries at 60–80 and clipping/window selection at 83–165. Quantiles describe per-create values. Shares divide by summed proxy durations, not elapsed load wall time. The observed zero overlaps and aggregate arithmetic agree with the derived JSON; table values match its rounded observations.

The clock argument is supported. The review independently fetched and read all eight exact upstream Git blobs recorded in the source index, including Native AOT's shared CoreLib import, Unix Stopwatch and interop, `SystemNative_GetTimestamp`, `minipal_hires_ticks`, and CPython's monotonic-nanosecond path. The actual small SDK/runtime version metadata matches the indexed .NET revision. The unchanged common driver records the window with `time.monotonic_ns()` and launches the child without a time-namespace change. Together with the recorded interpreter clock declaration and 1 GHz trace frequencies, this supports the stated same-machine window comparison. It does not create a business-cycle identity join.

Both roles retain 1,501 inside-window create proxies, 136 before and 16 after, with no observed straddle. The reported take→retirement shares, 65.24% and 66.04%, are correctly limited to the managed proxy. They include materialization, retirement/quiescence waiting and the observing continuation. The trace cannot isolate timer ticks or native pending responses; it does not establish physical SQLite lock ownership or a single cause of the formal failure. Four unscoped startup operations per role remain in the numeric record; the prose's completeness statement concerns recorder/invariant completeness.

The report preserves adverse evidence: diagnostic cycle p99 is **207.031034 → 227.100834 ms**, even though other descriptive intervals decrease. The original formal **567.131236 ms** SQLite failure remains unaccepted. One instrumented process per role is not an independent repeated performance comparison, and the full-lifecycle request tails are explicitly separated from load-window and external-cycle tails.

## Review boundary

Only source, small version metadata and completed derived JSON were read locally, with local helper work pinned to CPU 8. The analyzer was AST-parsed, not imported or executed. No raw trace/resource series, payload or binary was read or hashed; no workload, restore, build or acceptance reader ran. Public filename/hash provenance and aggregate observations introduce no operational paths, process IDs, environment values, addresses or TLS material. Original inputs and results were not altered.
