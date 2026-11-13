# Execution and parallelism policy for existing tasks

## Current phase

Research/Documentation and Design experiments are authorized; all A/B tasks are future implementation instructions only and remain planned_candidate and not_authorized. Acceptance of relevant contracts does not automatically grant permission to write product code. Do not repeatedly request confirmation for already-authorized research, fixes, reviews, commits and Design/Plan merges permitted by repository rules.

## Local dependencies and component acceptance

Start edges constrain actual commencement, and acceptance edges constrain final acceptance; the union of both edge types must be acyclic. References provide traceability only and must not become implicit locks waiting for all Research/Documentation or the whole of phase A. A single component may complete component acceptance using actual upstream/ABI fixtures; final composition must be validated by explicit downstream tasks against exact component commits. A fixture must not impersonate a Host, and integration must have an owner.

B01 declares public Data interfaces; B02/B03 native providers, B05 transactions, B06 streams and B07 codecs may proceed in parallel against those interfaces, while B04 owns complete Host composition. B09 depends on B01, and B11 reuses B07 to avoid duplicate metadata/binders. B15 declares the C# application layer and waits for the actual B17 Host for acceptance; B16 is an independent streaming component, and B17 depends on B16, avoiding a B16↔B17 cycle. A16 may prepare packages after A13, with final acceptance waiting for A14/A15/A22. A10/A11 validate generated components; A17/A18 and the domain Hosts own complete acceptance of composition with the actual Core.

## Rust Host and protocols

NativeWeave uses Source-Driven Deep Native Integration. C# is the application development language, providing strongly typed Fluent APIs, static metadata/DTOs and business Handlers; database drivers, query/dialect/ORM relational execution and Server networking/protocols/runtimes must reuse mature Rust engines. Kestrel, Npgsql and similar components are comparators only. Ordinary applications do not require handwritten Rust/FFI or native recompilation when adding Entity/DTO/Handler types. Preserve normal dotnet build/run and actual Native AOT publication; do not build a C# SQL AST/full LINQ Provider or a monolithic Core runtime.

B15 and B17 are not a group of alternative candidate Hosts. B17 is the sole production Host; the B18/B19 specifications declare host_task_ids=[B17]. Applications may omit protocol packages, but the existing 48 tasks still fully plan both packages. B24's release scope includes exact revisions of B01–B23, and B04/B17 are always mandatory. The old conditional-selection schema is retained for historical validation; the current graph no longer uses it to express the already-settled Rust mission.

## Worktrees and file ownership

Each task uses task/<ID>-implementation (a corresponding research branch in the research phase). Modify only the module/test/evidence paths listed in its packet; native subdirectories must not overlap. The root solution, Directory.Build.props, Directory.Packages.props, global.json and native/Cargo.toml/lock receive minimal registration patches serialized under A13's workspace-manifest-integration lock. Task-specific code and tests continue in parallel; the entire repository is not locked.

For new versions, update affected nodes/contracts and reviews against exact inputs; do not arbitrarily reorder unrelated tasks. First pin failures, input hashes and actual status, then fix and revalidate. Resolve actual foundational contract conflicts in their specifications/ADRs, rather than adding another glue layer in every module to work around them.

## Implementation evidence

Formal product acceptance must cover the task's normal/exceptional/cancellation/concurrency/release semantics, actual Windows/Linux AOT, independent NuGet, actual DB/HTTP/TLS and source/artifact identities. A16/B24 require genuinely pristine consumer environments without Rust; removing tools from the current PATH is one mechanism check performed in research and must not be presented as a machine on which Rust was never installed.

B22/B23 own complete fault/long-term resource/performance evidence; correctness failures cannot be replaced with performance successes. Comparison routes must have equivalent features/protocols/data/durability; Kestrel belongs only to comparison executables. Package publication still requires explicit future authorization and is not performed in the current phase.
