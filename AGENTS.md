# NativeWeave Plan working rules

NativeWeave uses Source-Driven Deep Native Integration. C# is the application development language, providing strongly typed Fluent APIs, static metadata/DTOs and business Handlers; database drivers, query/dialect/ORM relational execution and Server networking/protocols/runtimes must reuse mature Rust engines. Kestrel, Npgsql and similar components are comparators only. Ordinary applications do not require handwritten Rust/FFI or native recompilation when adding Entity/DTO/Handler types. Preserve normal dotnet build/run and actual Native AOT publication; do not build a C# SQL AST/full LINQ Provider or a monolithic Core runtime.

1. The current work is limited to research, design and refinement of future implementation plans. The user has authorized necessary Design/Plan commits, PRs and merges that comply with repository rules; do not repeatedly ask. Do not write to the NativeWeave product repository.
2. Preserve 34R/32D/48Delivery and the three graphs; `fragments/` only elaborates existing tasks. Read existing results and actual reviews before filling gaps.
3. Every packet/graph has an exact revision/hash; acceptance binds actual sources, dependencies and independent review. Do not merely change status or add fabricated evidence.
4. Technical designs may be accepted before product implementation; list product AOT/actual service/sustained-load/release obligations separately. Strictly distinguish source read, upstream tests read, actual execution and product acceptance.
5. Write only within your own scope. Work in parallel in dedicated worktrees; shared root build manifests receive small integration patches through A13, without a global lock.
6. After changing current graphs/packets/registry, run structural, current-completion and negative-case gates; run historical frozen checks at their original commits. Do not treat old proposed snapshots as rules permanently prohibiting acceptance.
7. Preserve failure records, original bytes and separate Windows/Linux identities; when binaries are omitted, identify their archive/content hashes and reproduction methods.
8. Subagents may perform actual independent technical reviews, but a shared GitHub identity must not impersonate another approval account. Do not bypass Required Checks or change permissions/licenses to make a merge succeed.
