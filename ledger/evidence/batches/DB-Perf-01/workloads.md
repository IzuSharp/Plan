# Database comparison workload requirements

Compare equivalent business behavior against actual Dapper.AOT consumers using
both PostgreSQL and SQLite. Preserve parameter types, SQL semantics, projection,
transaction boundaries, result checks, cancellation and consumption policy.
Report ordinary Fluent, warmed prepared execution and complete parameterized
SQL separately. Use 1/100/1,000-row phase cases and complete mixed operations;
do not substitute a serializer microbenchmark for whole-query results.

Distinguish client operation CPU, server CPU, process allocation, framework-only
allocation, retained memory and peak RSS. Business DTO/List/string allocations
remain in process totals. Do not subtract a mapper scope from a different workload
to manufacture a framework-only value. Count setup, warmup, steady work, drain
and post-disposal observation under explicit boundaries.

Use successful work and observed duration for completion throughput. Report
rejected arrivals, failures, latency populations and all repeated windows.
A chosen offered rate is not a saturation search. First-row time includes
submission and first mapping; a total quantile is computed from per-operation
phase sums, not from sums of marginal quantiles.

Instrumented FFI/protocol/allocation diagnostics carry only their declared scope.
SQL dispatch, libpq submissions, server replies, notifications and physical RTT
are different quantities. Missing counters are unavailable, never zero.
Source/package and host identities constrain each conclusion. Matched short
before/current measurements cannot become a fabricated long-before comparison.

Performance execution stays local and requires current task authority. Keep raw
samples and command output on the execution machine. Commit the necessary final
tables, conditions, decisions and limitations; do not upload documentation or
intermediate material as Actions artifacts.
