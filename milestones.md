# Parallel milestones for existing tasks

The current milestone is to complete 34R/32D and mature the 48 Delivery task packets, without implementing the product. The actual research order is: core ABI/ownership/async and platforms; database and Rust server source/experiments in parallel; then cross-domain performance/packaging/future Engines/overall review. This order only sequences execution of existing tasks; it is not a new graph or a global serialization lock.

After future product-phase authorization:

| Parallel work | Subsequently unlocks | Acceptance ownership |
| --- | --- | --- |
| A01 layout, A19 models, A21 benchmark tools, B01 shared Data seam | Local Core modules, native providers and query bindings | Each component's actual code/evidence |
| A03–A12 local Interop/generation; B02/B03/B05/B06/B07/B09 | A17/A18 actual Engines, B04 Host, B11/B12/B13 | Actual native/AOT composition |
| B15 C# application, B16 streaming components, B17 Rust Host | B18 Tonic, B19 rmcp, B20 diagnostics | Native networking/protocols/release |
| A14/A15 platforms and A16 packages; B21 complete reference service | B22 fault/soak, B23 performance, B24 domain releases | Independent NuGet, clean no-Rust consumption, both OSes, actual DB/networking and long-term resources |

The exact edges in delivery-graph.json are authoritative. A/B are not barriers requiring entire phases to finish serially; an Engine that does not use an optional Core capability does not start that runtime. GUI/GPU/mobile boundaries follow D21, without making future hardware/platform certification a prerequisite for ordinary Windows/Linux development.
