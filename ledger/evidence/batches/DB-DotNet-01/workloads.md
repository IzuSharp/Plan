# DB-DotNet-01 equivalent business workload

This is an executable-workload specification. All cells are initially pending; a public API name is not a measured pass. [workload-cases.json](workload-cases.json) contains 31 semantic cases adapted from the retained DB-Perf-01 specification, with no historical result credit. Implement at least 24 distinct cases on **both** Korda and Dapper.AOT and **both** PostgreSQL and SQLite. The list below is a compact implementation index; exact predicates, output contracts and oracles are in the JSON.

| Case | Business operation |
| --- | --- |
| Q01 | Composite tenant/order key lookup and missing key |
| Q02 | Search with optional customer, amount and time filters |
| Q03 | Order page with optional customer through LEFT JOIN |
| Q04 | Three-table order/customer/detail item view |
| Q05 | Grouped customer spending/counts with HAVING |
| Q06 | Product sales-quantity ranking with deterministic ties |
| Q07 | Composite cursor paging across repeated timestamps |
| Q08 | Deep offset page with complete unique ordering |
| Q09 | Order page and one bounded relation batch, including empty groups and duplicate keys |
| Q10 | Narrow reconciliation DTOs containing keys/versions |
| Q11 | Wide manual-review DTOs with text, JSON and money |
| Q12 | Fully consumed large streamed ledger export |
| Q13 | Orders lacking details through an anti-join |
| Q14 | NULL contact details with explicit display fallback |
| Q15 | Typed JSON settings and exact decimal/fixed-scale money |
| Q16 | Qualifying product/quantity through an IN subquery |
| Q17 | Bounded CTE work queue |
| Q18 | Per-customer running sums and row numbers |
| Q19 | UNION ALL populations preserving duplicates |
| Q20 | INTERSECT populations with duplicate elimination |
| Q21 | Distinct customer population, with fixed list/scalar result contract |
| Q22 | Escaped literal substring/prefix business search |
| Q23 | Insert order and consume returned fields |
| Q24 | Patch selected columns with explicit NULL versus omission |
| Q25 | Optimistic version update under two-writer contention |
| Q26 | Read/update order/details transaction with confirmed commit |
| Q27 | Partial work followed by business failure and rollback |
| Q28 | Bounded bulk insertion with fixed atomicity and batch size |
| Q29 | Upsert using an explicit unique conflict target |
| Q30 | Version-checked delete |
| Q31 | Exactly 100 order-summary DTOs returned in an owned list |

Dynamic construction and reusable/precompiled shapes are separate modes, not extra cases. Q25/Q27 and injected failure variants report distinct contention/fault metrics and cannot masquerade as successful normal traffic. Provider-specific unsupported capabilities remain explicit; do not replace a required common business case with an unrelated scalar shortcut.

## Shared data and result oracle

Use the current order/customer/detail models and `Db*` metadata. Freeze DDL, schema/file snapshots, all indexes/statistics, seed algorithm, tenant/key distribution, hot keys, row counts, NULL/empty relationships, repeated timestamps, string lengths, JSON structures and monetary policies. Reuse local IDs across tenants. Include narrow and wide rows and exports crossing many fetches. Keep read-oracle data separate from changing mixed-write data where needed.

Both routes return the same types, fields, multiplicity and ownership. Fully consume results and compare an independent typed oracle plus a complete-result digest outside the timed region. For writes, retain operation IDs/parameters and validate durable invariants, affected rows, return values and transaction outcome; account for every conflict and retry. Capture emitted SQL/parameter order and PostgreSQL EXPLAIN or SQLite EXPLAIN QUERY PLAN. If SQL/plans differ, retain actual business metrics and add a same-SQL diagnostic without replacing the headline route.

## Modes and load schedule

Exercise single connection, concurrency ramp, high-concurrency mixed reads/writes, saturation and recovery. Fix pool bounds, busy/admission timeouts, transaction isolation/durability and result limits. A fixed-arrival-rate scheduler records planned starts separately from actual starts; end-to-end latency includes queueing and rejected/late work remains counted. First compare common offered load; separately find sustainable throughput at common tail-latency/error constraints. Save exact thresholds before looking at final results.

Use independent short processes and interleave the frozen .NET baseline and candidate; retain raw counters and variance. The sole external performance route is Dapper.AOT. Check every measured Dapper invocation has active generated parameter/row handling and that all measured binaries are Native AOT. Driver-only probes are attribution diagnostics.

## Allocation and metrics

Follow plan.md's whole-process accounting. Keep raw allocated bytes, elapsed/CPU ticks, success/failure/rejection/retry/pending counts, rows, latency histogram/counts and process Gen 0/1/2. Report total allocation, business result allocation, attributable Korda overhead and unresolved driver/runtime/tool bytes, with evidence method. Q31 must be separately visible: list, 100 DTOs and strings are business results even when allocated inside the library.

Record client CPU time/success, steady/peak RSS and retained memory after drain, alongside throughput and tails. Measure PostgreSQL server resources independently; SQLite engine memory/CPU belongs to the application. A zero claim must name one exact path and be supported by raw counts and attribution; do not infer it from no collection or rounded B/row.

## Dedicated final campaign

After freezing candidate packages and admitting one exclusive resource set, execute L01 PostgreSQL/Korda, L02 SQLite/Dapper.AOT, L03 PostgreSQL/Dapper.AOT and L04 SQLite/Korda sequentially. IDs bind cells; any schedule revision must be recorded before measurement. Each has 1,800 uninterrupted valid mixed-load seconds, with warmup/calibration/drain additional. Source/package/dependency/executable/seed/workload/environment hashes and raw ledgers are mandatory. The initial state is 0/4, 0 seconds. Ordinary PR CI runs only selected correctness, short regression and AOT package consumption.
