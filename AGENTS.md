# NativeWeave Plan Working Rules

NativeWeave uses Source-Driven Deep Native Integration. C# is the application development language, providing strongly typed Fluent APIs, static metadata/DTOs, and business handlers; database drivers, query/dialect/ORM relational execution, and Server networking/protocols/runtimes must reuse mature Rust engines. Kestrel, Npgsql, and similar implementations serve only as comparison baselines. Ordinary applications do not require handwritten Rust/FFI or native recompilation when an Entity/DTO/Handler is added. Preserve normal dotnet build/run and actual Native AOT publishing; do not build a C# SQL AST, a full LINQ Provider, or a monolithic Core runtime.

1. The current scope is research, design, and refinement of future implementation plans only. The user has authorized the necessary Design/Plan commits, PRs, and merges that comply with repository rules; do not ask repeatedly. Do not write to the NativeWeave product repository.
2. Preserve the 34 Research / 32 Documentation / 48 Delivery tasks and the three graphs; `fragments/` only elaborates existing tasks. Read existing results and actual reviews before filling gaps.
3. Every packet/graph has an exact revision/hash; acceptance binds actual sources, dependencies, and independent review. Do not merely change status or add fabricated evidence.
4. Technical designs may be accepted before product implementation; track product AOT/real-service/long-running-load/release obligations separately. Strictly distinguish source read, upstream tests read, actual execution, and product acceptance.
5. Write only within your own scope. Work in parallel in independent worktrees; integrate shared root build manifests through small A13 integration patches, without a global lock.
6. After changing current graphs/packets/registry, run structural, current-completion, and negative-case gates; run historical frozen checks at their original commits. Do not treat an old proposed snapshot as a rule permanently prohibiting acceptance.
7. Preserve failure records, raw bytes, and separate Windows/Linux identities; when binaries are omitted, state their archive/content hashes and reproduction method explicitly.
8. Subagents may perform actual independent technical review, but the same GitHub identity must not impersonate another approval account. Do not bypass Required Checks or change permissions/licenses to make a merge pass.

## Mandatory C# public API and documentation standard

Every existing Delivery task must follow the exact Design commit pinned in source-driven-baseline.json, including `docs/standards/csharp-public-api-and-documentation.md` and `docs/api/README.md`. The packet's API inputs and documentation owner are acceptance requirements, not optional follow-up work.

1. Research the relevant current stable .NET/C# public API families and actual fixed source; never confuse Preview or upstream capability with NativeWeave product support.
2. Provide complete exact C# signatures, natural minimum/advanced consumers, nullability/defaults, ownership/lifetime, async/cancellation, errors, concurrency, capabilities and cost. Map the public member through managed adapter, C ABI, Rust adapter and actual Engine operation.
3. Keep SQL/network/domain execution in Rust and Core minimal; ordinary Entity/DTO/Handler additions must reuse precompiled native assets with normal dotnet build/run/publish.
4. The implementing task owns XML documentation, generated API Reference, guides, examples, compatibility and the required compilation/AOT/consumer checks. Record justified applicability for internal-only work; do not add unreviewed public scaffolding.
5. Independently review API completeness, usability, correctness, allocation/copy cost, compatibility and documentation. Preserve historical accepted inputs and bind materially changed content to fresh review and hashes.
6. New Engines and independent repositories must actually adopt the versioned standard and install its checks using the Design templates; AGENTS.md is not inherited across repositories. Product adoption is a future A13/A22/A24 obligation, not permission to write product code in this phase.

For the Public API 0.4.0 refinement, follow `public-api-acceptance-workflow.md`.
Preserve original acceptance bytes; current mandatory gates include
`verify_public_api_history.py`, `verify_public_api_plan.py` and exact
`prepare_acceptance.py`/`verify_completion.py` binding checks. API inputs are
individually SHA-256 pinned in each Delivery node and the Design repository is
commit-pinned. A changed input invalidates its current binding; no recovered
script, historical translation review or design stub is new acceptance evidence.
