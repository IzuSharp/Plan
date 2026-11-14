# Existing Task Execution and Parallelism Policy

## Current Phase

Research/Documentation and Design experiments are authorized; all A/B tasks are future implementation instructions only and remain planned_candidate and not_authorized. Acceptance of related contracts does not automatically authorize product writes. Do not repeatedly request confirmation for already authorized research, fixes, reviews, commits, or Design/Plan merges permitted by the rules.

## Local Dependencies and Component Acceptance

Start edges constrain actual starts, and acceptance edges constrain final acceptance; the union of both edge types must be acyclic. References provide traceability only and must not become an implicit lock requiring all Research/Documentation or all of phase A to finish. An individual component may complete component acceptance using actual upstream/ABI fixtures; an explicit downstream task must verify the final assembly using exact component commits. A fixture must not stand in for a Host, and integration must have an owner.

B01 declares public Data interfaces; B02/B03 native providers, B05 transactions, B06 streaming, and B07 codecs may proceed in parallel against those interfaces, while B04 owns the complete Host assembly. B09 depends on B01, and B11 reuses B07, avoiding duplicate metadata/binders. B15 declares the C# application layer and waits for the actual B17 Host at acceptance; B16 is an independent streaming component, and B17 depends on B16, avoiding a B16↔B17 cycle. A16 may prepare packages after A13, but final acceptance waits for A14/A15/A22. A10/A11 verify generated components; A17/A18 and domain Hosts own complete acceptance of assembly with the actual Core.

## Rust Host and Protocols

NativeWeave uses Source-Driven Deep Native Integration. C# is the application development language, providing strongly typed Fluent APIs, static metadata/DTOs, and business handlers; database drivers, query/dialect/ORM relational execution, and Server networking/protocols/runtimes must reuse mature Rust engines. Kestrel, Npgsql, and similar implementations serve only as comparison baselines. Ordinary applications do not require handwritten Rust/FFI or native recompilation when an Entity/DTO/Handler is added. Preserve normal dotnet build/run and actual Native AOT publishing; do not build a C# SQL AST, a full LINQ Provider, or a monolithic Core runtime.

B15 and B17 are not a candidate Host selection group. B17 is the only formal Host; the B18/B19 specifications declare host_task_ids=[B17]. Applications may omit the protocol packages, but both packages remain fully planned within the existing 48 tasks. B24's release scope includes the exact revisions of B01–B23; B04/B17 are always required. The old conditional-selection schema is retained for historical validation; the current graph no longer uses it to express the established Rust mission.

## Worktrees and File Ownership

Each task uses task/<ID>-implementation (or a corresponding research branch during research). Modify only the module/test/evidence paths listed in the packet; native subdirectories do not overlap. The root solution, Directory.Build.props, Directory.Packages.props, global.json, and native/Cargo.toml/lock receive minimal registration patches serially under A13's workspace-manifest-integration lock. Task-specific code and tests continue in parallel; do not lock the entire repository.

For a new version, update affected nodes/contracts and reviews against exact inputs; do not arbitrarily reorder unrelated tasks. First pin failures, input hashes, and actual state, then fix and revalidate. If an actual foundational contract conflict is found, return to its specification/ADR to resolve it; do not work around it by adding another layer of glue in each module.

## Implementation Evidence

Formal product acceptance must cover task-specific normal/failure/cancellation/concurrency/release semantics, actual Windows/Linux AOT, independent NuGet, real DB/HTTP/TLS, and source/artifact identities. A16/B24 require a truly clean no-Rust consumption environment; removing tools from the current PATH is a mechanism verification performed during research and must not stand in for a machine on which Rust has never been installed.

B22/B23 own complete failure/long-term-resource/performance evidence; performance success cannot replace a correctness failure. Comparison paths must have equivalent functionality/protocols/data/durability; Kestrel belongs only to comparison programs. Package publication also requires explicit future authorization; no packages are published in the current phase.

## Public API and documentation acceptance

The exact Design API specification and versioned C# public API/documentation standard are mandatory inputs for every relevant task. Read [API execution requirements](api-execution-requirements.md) and the packet's API inputs, surface responsibility and documentation owner. Implementing a symbol includes its XML, generated reference, guide/examples, compatibility review and actual consumer/AOT checks in the same task. Internal-only work keeps raw handles, ABI records and execution plumbing internal and records exact applicability; no task may claim an upstream capability as an implemented public API.

A13 installs shared enforcement; A22 owns compatibility rules; A24 installs explicit adoption in new Engine scaffolds; each domain owner maintains its own documentation; A16/B24 own final package consumption and release composition. Ordinary Entity/DTO/Handler changes remain C# builds using precompiled native assets. These requirements add no fourth graph and do not authorize any of the 48 Delivery tasks.
