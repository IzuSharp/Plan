# NativeWeave Plan — Existing Research, Specification, and Future Implementation Graphs

The current phase is research, detailed design, and future Codex development planning; **do not write to the NativeWeave product repository or execute A/B Delivery tasks**. The recovery entry point is [source-driven-baseline.json](source-driven-baseline.json); the existing three graphs, exact evidence, and reviews determine the actual state.

**Final acceptance for this round: all 34 Research / 32 Documentation tasks and 21 technical contracts are accepted.** Design PR #10 was merged as `08e3aaee73aad174620dcff18ed21b3b14c5e632`; the 66 tasks bind the pinned Plan input `c3947b378e0a251f8dfeaf7fd7d4acc636631974`, that Design commit, actual independent reports, and exact confirmations by the corresponding executors. The [acceptance index](ledger/completion-acceptance.json), [final checkpoint](ledger/checkpoints/rd-acceptance-2026-11-13.json), and [complete validation results](verification/completion.json) provide verifiable records. Review of the 48 Delivery task descriptions is complete; product implementation and product acceptance have not started.

NativeWeave uses Source-Driven Deep Native Integration. C# is the application development language, providing strongly typed Fluent APIs, static metadata/DTOs, and business handlers; database drivers, query/dialect/ORM relational execution, and Server networking/protocols/runtimes must reuse mature Rust engines. Kestrel, Npgsql, and similar implementations serve only as comparison baselines. Ordinary applications do not require handwritten Rust/FFI or native recompilation when an Entity/DTO/Handler is added. Preserve normal dotnet build/run and actual Native AOT publishing; do not build a C# SQL AST, a full LINQ Provider, or a monolithic Core runtime.

## Three Graphs and Their Responsibilities

| Graph | Existing scope | Current completion requirements |
| --- | --- | --- |
| research-graph.json | R01–R34, 34 tasks | Actual pinned source, appropriate experiments, normal/failure/boundary conclusions, and independent technical review |
| documentation-graph.json | D01–D32, 32 tasks | 21 specifications, 10 implementation-detail fragments, and 1 final review, sufficient to guide implementation |
| delivery-graph.json | A01–A24 / B01–B24, 48 tasks | This round only refines interfaces, steps, ownership, local dependencies, parallelism, and acceptance; implementation is not authorized |

Each of the [114 independent task packets](task-index.md) has revision 0.3.0 and a packet hash. `fragments/` elaborates existing Delivery tasks; it is not a fourth task graph. `start_dependencies` constrain starting, and `acceptance_dependencies` constrain final acceptance; research/specification references provide traceability only and do not automatically impose waiting. Contracts have exact versions and content hashes; research, design acceptance, and product verification are recorded separately.

## Established Division of Responsibilities

The primary Database path uses maintainer-precompiled SeaQuery+SQLx with dynamic business metadata. Mature SeaORM dynamic projection/static relationship capabilities are reused within their source-defined boundaries; optional specialized static Entity packages must not become prerequisites for ordinary entities. B01 exclusively owns shared Data interfaces, B07 exclusively owns fallible codecs, B09 only defines query-operation bindings, B11 owns native queries and dialects, B12 owns C# DTO materialization, B13 owns natural strongly typed Fluent APIs, and B14 owns native explicit relationships.

B15 is the **C# Server.Application / Handler interface**, and B17 is the **required Rust Server Host**; they complement one another. B16 provides Body/Bytes and budget components, and B17 reuses actual Tokio/Hyper/Tower/Axum engine capabilities; applications may independently opt into B18 Tonic and B19 rmcp, but both use only B17's Rust Host. The old Kestrel-versus-Rust exclusive-choice group has been retired; it is not an undecided product architecture.

## Working Method

First verify the actual GitHub HEAD and baseline pairing, then read the corresponding packet and Design specifications. Recheck complete results without repeating successful experiments. Use one independent worktree per task and modify only its owned scope; integrate small root solution/Cargo workspace patches through A13, without creating a global worker lock. Async/database/server work each has independently testable local components and final assembled acceptance; do not make the future reference application a circular prerequisite for every component's acceptance.

```bash
python3 tools/validate_graphs.py --root . --output verification/graph-validation.json
python3 tools/mutation_checks.py
python3 tools/host_selection_checks.py
python3 tools/verify_completion.py
python3 tools/verify_completion.py --require-complete
```

The two repositories should be sibling directories named `Plan/` and `NativeWeave-Design/`. Current verification tools check structure, hashes, and gates; they cannot authenticate actual human identities or turn research experiments into product execution. Historical frozen validation runs against original commits, whereas current acceptance validation runs against the exact inputs for this round; the two must not be confused.

First check out the full Design SHA specified by the baseline. `--require-complete` requires acceptance of all 34 Research / 32 Documentation tasks and 21 contracts, and verifies 840 input entries, 114 packets, 10 fragments, and actual independent bindings; it does not run native experiments or start Delivery.

## Continuation and Implementation Entry Points

See [D32](ledger/reviews/D32.md), the [current phase](CURRENT-PHASE.md), and the [acceptance register](acceptance-register.md) for exact progress and independent review. Once the product phase is explicitly authorized in the future, A01, A19, A21, and B01 may be implemented in parallel first; the rest proceed according to actual local dependencies. Implementation still requires independent NuGet/clean no-Rust consumption, actual Windows/Linux AOT, real databases/networking, error/cancellation/resource behavior, and long-running-load/performance verification.

Source selection does not depend on ArcForges business logic or architecture. Merging research does not automatically publish packages, change permissions/licenses, or bypass Required Checks. Independent subagent technical review is not approval by another GitHub account.
