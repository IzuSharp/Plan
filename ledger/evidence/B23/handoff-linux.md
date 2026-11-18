# B23 Linux checkpoint

Implementation is in progress after accepted B21 and inherited A21. Final B23
acceptance waits for B22 correctness and all required durations. The
[batch handoff](../batches/Task-07/handoff-linux.md) records owners, commits and PRs.

The runnable controller consumes the accepted A21 measurement harness. Its short
functional runs bind the immutable B21 AOT binary and independently reconcile
durable SQL state, replay bytes, ordering and attachment content. Each explicitly
states that it is not performance evidence; no regression bands or comparative
benefit are inferred from those timings.

The standalone C# NativeAOT comparator now runs the normal SQLite/PostgreSQL
business routes across HTTP1, HTTP1 TLS and HTTP2 TLS. Six cells each passed127
independent functional checks. Its packages/assembly contain no NativeWeave
dependency. SQLite uses the same3.51.3 amalgamation as the accepted Rust engine,
with durability, schema and isolation documented in the comparator source.
Raw ADO.NET query execution, absent DI/diagnostics and global byte-credit profiles
remain explicit differences. A successful normal cell does not validate an
unimplemented overload or diagnostic cell.

Direct Rust, full workload profiles, diagnostics variants, predeclared noise-based
bands, repeated isolated measurements and independent review are still ongoing.
`checkpoint-preservation-001.json` binds the raw development receipts. No timed
comparison has started, and no performance/memory benefit is claimed.
