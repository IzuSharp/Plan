# Execution counter semantics

Keep distinct quantities separate:

| Quantity | What it establishes | What it does not establish |
| --- | --- | --- |
| Managed-to-native FFI Calls | Actual counted ABI invocations in the instrumented window | Native-to-managed callbacks, internal provider calls or ordinary timing cost |
| SQL dispatches | Provider dispatches, including internal controls | Server-side successful statement trace |
| libpq submissions | Successful send/Sync API submissions | Packets, replies or physical RTT |
| Pending/OK returns | ABI status returns | Managed suspension count or network round trips |
| Native owner counters | Tracked resource ownership at the named boundary | Whole-process memory or uninstrumented driver internals |

The historical healthy-COMMIT/retirement proxy window reduced SQL dispatches
2→1, forwarded ReadyForQuery replies 6→4 and libpq submissions 10→6, retaining
two standalone Sync messages. It was a narrow correctness observation with its
own source; it is not a final 30-minute protocol trace. Post-COMMIT confirmation
and safe-return proofs remain independent of the omitted healthy pre-COMMIT probe.

The [six final-candidate FFI diagnostics](../continuation-8/final-ffi-diagnostics-01.md)
are separate 15-second C1 cases. Numeric32 records 13 FFI calls and one SQL dispatch
per completed query; PostgreSQL records four libpq submissions. The exact batch
boundary needs a second pull, not another SQL execution. Ordinary phase/mixed
consumers lack FFI arrays and required-reply totals; Dapper internal counts are
unavailable. Do not replace missing observations with zero or source estimates.
