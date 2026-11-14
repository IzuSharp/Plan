# Independent Technical Review Inputs

First read the current phase, the three graphs, the corresponding packets among the 114, and the exact Design registry versions/hashes; read actual source locations, input snapshots, and raw experiment/failure logs, rather than only the author's summary. NativeWeave uses Source-Driven Deep Native Integration. C# is the application development language, providing strongly typed Fluent APIs, static metadata/DTOs, and business handlers; database drivers, query/dialect/ORM relational execution, and Server networking/protocols/runtimes must reuse mature Rust engines. Kestrel, Npgsql, and similar implementations serve only as comparison baselines. Ordinary applications do not require handwritten Rust/FFI or native recompilation when an Entity/DTO/Handler is added. Preserve normal dotnet build/run and actual Native AOT publishing; do not build a C# SQL AST, a full LINQ Provider, or a monolithic Core runtime.

## Review Checklist

1. Has the task's actual question been resolved? Which pre-existing results merely had stale status, and which risks have been addressed by which new evidence?
2. Are the C#/Rust responsibilities and public API/specialized Adapter/upstream extension/controlled fork choices supported by sources? Do not penetrate private layouts or duplicate engines.
3. Are pointers/lengths/state/ErrorRecord capacities, logical admission/physical leases, cancellation/terminal/take/dual callback retirement, and allocators consistent?
4. Do actual SQLx transaction/protocol recovery/Unknown behavior, SeaORM dynamic shapes, SeaQuery backend capabilities, and parameter binders preserve their real semantics?
5. Are Server Handler/Body/Bytes/permit/queue/deadline/protocol validation and actual Tonic/rmcp public API limitations covered? B17 is the only formal Host.
6. Are the current 34 Research / 32 Documentation tasks and 21 contracts sufficient to guide the 48 Delivery tasks? Are ownership and local dependencies across the 114 packets/three graphs/fragments acyclic and free of excessive waiting?
7. Are source read, upstream tests read, actual execution, finite models, and product acceptance strictly distinguished? Do not require future product implementation before accepting the design.

Report the actual reviewer/author, exact input SHAs and sources, each conclusion, finding severity/fix rereads, unresolved blockers, and future product obligations. Close all blockers before acceptance. Subagent review under the same GitHub account is not an independent platform approval identity.
