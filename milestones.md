# DB-Scope-01 — current database product scope

The owner authorized DB-Scope-01 on 2026-11-21: stop Perf-01, retain the PostgreSQL/SQLite strong-typed Fluent ORM with Rust SeaQuery/SQLx and Native AOT, remove NativeWeave-owned Server/gRPC/MCP and non-database engines/demos, run real Linux consumers, review and merge, then stop. Ordinary C# applications choose their own hosting; no new HTTP/gRPC wrapper or ORM feature is in scope.

**Start here:** [current execution plan](ledger/evidence/batches/DB-Scope-01/plan.md), [Linux handoff](ledger/evidence/batches/DB-Scope-01/handoff-linux.md), [acceptance](ledger/evidence/batches/DB-Scope-01/acceptance.json), and `delivery-graph.json.current_execution`. These supersede older phase/authorization/product-scope statements. Database Host remains part of the database execution layer. Performance optimization and 30-minute load tests are deferred.

The three legacy graphs, 114 packets, prior source-driven baseline, original acceptance bindings and delivered Task-01 through Task-07 evidence remain historical. Do not alter them to invent acceptance or resume removed components. Current acceptance requires new source-bound DB-Scope-01 evidence; unchanged historical gates run against their exact original inputs.

## Historical planning text (superseded for current product scope)

# Parallel Milestones for Existing Tasks

The current milestone is completion of the 34 Research / 32 Documentation tasks and mature instructions for the 48 Delivery tasks, without product execution. The actual research order is core ABI/ownership/async and platforms; database and Rust server source/experiments in parallel; then cross-domain performance/packaging/future Engines/overall review. This is only an execution ordering of existing tasks, not a new graph or a global serial lock.

After future authorization of the product phase:

| Work that may proceed in parallel | Subsequent work unlocked | Acceptance ownership |
| --- | --- | --- |
| A01 layout, A19 models, A21 benchmark tooling, B01 shared Data seam | Local Core modules, native providers, and query bindings | Actual code/evidence for each component |
| A03–A12 local Interop/generation; B02/B03/B05/B06/B07/B09 | A17/A18 actual Engines, B04 Host, B11/B12/B13 | Actual native/AOT assembly |
| B15 C# application, B16 streaming component, B17 Rust Host | B18 Tonic, B19 rmcp, B20 diagnostics | Native networking/protocols/release |
| A14/A15 platforms and A16 packages; B21 complete reference service | B22 failure/soak, B23 performance, B24 domain release | Independent NuGet, clean no-Rust, both OSes, real DB/networking, and long-term resources |

The exact edges in delivery-graph.json are authoritative. A/B are not barriers requiring each entire phase to finish serially; an Engine that does not use an optional Core capability does not start that runtime. GUI/GPU/mobile boundaries follow D21; do not make future hardware/platform certification a prerequisite for ordinary Windows/Linux development.
