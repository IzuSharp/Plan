# DB-CPP-01 — migration plan

Replace the database native implementation with C++ while preserving the public
C# API, C ABI, package identities, storage formats and all retained behavior.
The fixed Rust reference is `465cd0f90e6af05ec50eb581156240377cf0825b`.
C# owns application models/DTOs and Fluent calls; business schemas remain runtime
metadata, so ordinary C# edits do not rebuild the native layer.

Work proceeded through baseline, Plan, Design decision, native implementation,
behavior comparison, Rust-free consumer packaging, review and delivery. Test the
same business source against both implementations and both real providers; preserve
failure/cancellation/unknown-outcome semantics, resource retirement and stored-data
continuation. Record rejected candidate reasons without turning retries into acceptance.

All seven phases and 21 scoped checks completed. The [migration result](migration-report-linux.md)
and [contract mapping](migration-table.md) preserve the selected libraries, reasons,
compatibility results and limits. DB-API-01, performance work and additional
platform acceptance were separate tasks.
