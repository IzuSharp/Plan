# NativeWeave Plan — existing research, specifications and future implementation graphs

The project is currently in the research, detailed design and future Codex development planning phase; **do not write to the NativeWeave product repository or execute A/B Delivery tasks**. The recovery entry point is [source-driven-baseline.json](source-driven-baseline.json); the existing three graphs, exact evidence and reviews determine actual status.

**Final acceptance for this round: all 34 Research / 32 Documentation / 21 technical contracts are accepted.** Design PR #10 was merged as `08e3aaee73aad174620dcff18ed21b3b14c5e632`; 66 tasks bind pinned Plan inputs at `c3947b378e0a251f8dfeaf7fd7d4acc636631974`, that Design commit, actual independent reports and exact confirmations from the corresponding executors. The [acceptance index](ledger/completion-acceptance.json), [final checkpoint](ledger/checkpoints/rd-acceptance-2026-11-13.json) and [complete validation results](verification/completion.json) provide verifiable records. Instructions for 48 Delivery tasks have been reviewed; product implementation and product acceptance have not begun.

NativeWeave uses Source-Driven Deep Native Integration. C# is the application development language, providing strongly typed Fluent APIs, static metadata/DTOs and business Handlers; database drivers, query/dialect/ORM relational execution and Server networking/protocols/runtimes must reuse mature Rust engines. Kestrel, Npgsql and similar components are comparators only. Ordinary applications do not require handwritten Rust/FFI or native recompilation when adding Entity/DTO/Handler types. Preserve normal dotnet build/run and actual Native AOT publication; do not build a C# SQL AST/full LINQ Provider or a monolithic Core runtime.

## Three graphs and responsibilities

| Graph | Existing scope | Current completion requirements |
| --- | --- | --- |
| research-graph.json | R01–R34, 34 tasks | Actual pinned source, appropriate experiments, normal/exceptional/boundary conclusions and independent technical review |
| documentation-graph.json | D01–D32, 32 tasks | 21 specifications, 10 implementation fragments and 1 final review, sufficient to guide implementation |
| delivery-graph.json | A01–A24 / B01–B24, 48 tasks | This round only refines interfaces, steps, ownership, local dependencies, parallelism and acceptance; implementation is not authorized |

The [114 standalone task packets](task-index.md) each have revision 0.3.0 and a packet hash. `fragments/` elaborates existing Delivery tasks and is not a fourth task graph. `start_dependencies` constrain commencement, and `acceptance_dependencies` constrain final acceptance; research/specification references provide traceability only and do not automatically create waits. Contracts have exact versions and content hashes; research acceptance, design acceptance and product validation are recorded separately.

## Established division of responsibilities

The primary Database path uses maintainer-precompiled SeaQuery+SQLx and dynamic business metadata. Reuse SeaORM's mature dynamic-projection/static-relation capabilities within source-established boundaries; optional dedicated static Entity packages must not become a prerequisite for ordinary entities. B01 exclusively owns shared Data interfaces, B07 exclusively owns fallible codecs, B09 only defines query-operation bindings, B11 owns native queries and dialects, B12 owns C# DTO materialization, B13 owns natural strongly typed Fluent APIs, and B14 owns explicit native relations.

B15 is the **C# Server.Application / Handler surface**, and B17 is the **mandatory Rust Server Host**; the two complement each other. B16 provides Body/Bytes and budget components, while B17 reuses actual Tokio/Hyper/Tower/Axum engine capabilities; applications may independently choose Tonic from B18 and rmcp from B19, but both use only B17's Rust Host. The old Kestrel/Rust alternative selection group has been retired; it is not an undecided product architecture.

## Working approach

First verify the actual GitHub HEAD and baseline pairing, then read the corresponding packet and Design specifications. Review complete results without repeating successful experiments. Use one dedicated worktree per task and modify only its owned scopes; A13 integrates small patches to the root solution/Cargo workspace, without creating a global worker lock. Async/database/server each have independently testable local components and final composition acceptance; do not make a future reference application a circular prerequisite for acceptance of every component.

```bash
python3 tools/validate_graphs.py --root . --output verification/graph-validation.json
python3 tools/mutation_checks.py
python3 tools/host_selection_checks.py
python3 tools/verify_completion.py
python3 tools/verify_completion.py --require-complete
```

The two repositories should be sibling directories named `Plan/` and `NativeWeave-Design/`. Current proof tools check structure, hashes and gates; they cannot authenticate actual people's identities or turn research experiments into product execution. Historical frozen validation runs at the original commits; current acceptance validation runs against this round's exact inputs. The two must not be confused.

First check out the full Design SHA specified by the baseline. `--require-complete` requires acceptance of all 34R / 32D / 21 contracts and verifies 840 input entries, 114 packets, 10 fragments and actual independent bindings; it does not execute native experiments or start Delivery.

## Continuation and implementation entry points

For exact progress and independent reviews, see [D32](ledger/reviews/D32.md), the [current phase](CURRENT-PHASE.md) and the [acceptance register](acceptance-register.md). After explicit future product-phase authorization, A01, A19, A21 and B01 may be implemented in parallel first; the remaining tasks follow actual local dependencies. The implementation phase still requires independent NuGet/clean no-Rust consumption, actual Windows/Linux AOT, actual databases/networking, errors/cancellation/resources and sustained-load/performance validation.

Source selection does not depend on ArcForges business logic or architecture. Merging research does not automatically publish packages, change permissions/licenses or bypass Required Checks. Independent subagent technical review is not approval by another GitHub account.
