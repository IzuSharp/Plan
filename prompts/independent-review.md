# Independent technical review inputs

First read the current phase, three graphs, corresponding packets among the 114 and the exact Design registry versions/hashes; inspect actual source locations, input snapshots and raw experiment/failure logs, rather than only the author's summary. NativeWeave uses Source-Driven Deep Native Integration. C# is the application development language, providing strongly typed Fluent APIs, static metadata/DTOs and business Handlers; database drivers, query/dialect/ORM relational execution and Server networking/protocols/runtimes must reuse mature Rust engines. Kestrel, Npgsql and similar components are comparators only. Ordinary applications do not require handwritten Rust/FFI or native recompilation when adding Entity/DTO/Handler types. Preserve normal dotnet build/run and actual Native AOT publication; do not build a C# SQL AST/full LINQ Provider or a monolithic Core runtime.

## Review checklist

1. Whether the task's questions are actually resolved; which existing results merely have stale status, and which new evidence addresses which risk.
2. Whether C#/Rust responsibilities and public APIs/dedicated Adapters/upstream extensions/controlled forks have source grounding; do not expose private layouts across the boundary or duplicate engines.
3. Whether pointer/length/status/ErrorRecord capacity, logical admission/physical leases, cancellation/terminal/take/dual callback retirement and allocators are consistent.
4. Whether SQLx actual transaction/protocol recovery/Unknown, SeaORM dynamic shapes, SeaQuery backend capabilities and parameter binders preserve actual semantics.
5. Whether Server Handler/Body/Bytes/permit/queue/deadline/protocol validation and actual Tonic/rmcp public API restrictions are covered; B17 is the sole production Host.
6. Whether current 34R/32D/21 contracts are sufficient to guide 48 Delivery tasks; whether ownership and local dependencies in the 114 packets/three graphs/fragments are acyclic and avoid unnecessary waits.
7. Whether source read, upstream tests read, actual execution, finite models and product acceptance are strictly distinguished; future product implementation must not be a prerequisite for design acceptance.

Record the actual reviewer/author, exact input SHAs and sources, each conclusion, finding severity/fix rereads, unresolved blockers and future product obligations. Close all blockers before acceptance. Subagent review under the same GitHub account is not an independent platform approval identity.
