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
