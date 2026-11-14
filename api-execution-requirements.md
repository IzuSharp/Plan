# Complete C# API implementation and documentation requirements

Version: 0.4.0. These are refinements of the existing 48 future Delivery tasks. All remain `planned_candidate` and `not_authorized`; this document does not authorize product implementation.

## Exact implementation inputs

Read the immutable Design commit in `source-driven-baseline.json`, its `docs/api/README.md`, `docs/standards/csharp-public-api-and-documentation.md`, exact declaration/reference inventory, relevant domain specification/operation table, coverage/source manifest and accepted contracts. The declaration fixture is intentionally unimplemented; implement the specified behavior, never copy its throwing bodies as product code.

Each Delivery node records `api_design_inputs`, `api_surface_responsibility`, `documentation_owner_role` and explicit API/documentation/consumer acceptance. Its task packet carries the same information. These fields refine the existing task; they are not a new task graph or a new global execution dependency. Internal-only tasks must keep implementation plumbing internal and document the actual boundary they own.

Every public member needs a full implementation path from C# through managed adapter/C ABI/Rust adapter to an actual Engine operation. Ordinary C# Entity/DTO/Handler changes must reuse precompiled native modules. NativeWeave.Query is a public namespace in the Database facade assembly in v1; splitting it into a separate package must not introduce a Database/Query package cycle. Package names and transitive native capabilities follow the NuGet specification, not one package per task.

## Ownership by existing task

| Concern | Owning tasks | Required result |
| --- | --- | --- |
| Shared SDK/language, XML/docs/sample pipeline | A13 | Install the actual standard adoption manifest, stable SDK/C# selection, public API/reference and documentation checks into the product repository when authorized |
| ABI/status/capability/handle/buffer/error/callback/async/executor | A01–A08 | Implement exact wire/internal boundaries and assigned Interop public types; document lifetimes/errors/costs |
| Bindings, generators and analyzers | A09–A12 | Generated signatures/XML, static metadata diagnostics, closed generic/AOT consumers and negative compilation |
| RID/native assets and independent packages | A14–A16 | Correct assets/default loading, actionable errors, real packed artifact consumption and pristine no-Rust environment |
| Two Engines, models, fuzz/property and resources | A17–A20 | Verify exact public/native semantics using actual components; no replacement with design stubs |
| Cost/compatibility/affinity/scaffold | A21–A24 | Measured facade cost, API/native version diff, affinity checks and explicit adoption by new Engines/repositories |
| Data, providers, source/session, transactions/streams/codecs/migrations | B01–B08 | Canonical typed Data surface, domain outcomes and native SQLx behavior with owned rows and bounded cleanup |
| Metadata, generation, SeaQuery, DTOs, Fluent and relations | B09–B14 | Natural typed C# calls, native AST/dialect/relations, ordinary entity reuse and documented query exclusions |
| Application API, body, Rust host, gRPC/MCP and diagnostics | B15–B20 | Static typed handlers, configuration, exact body/credit/response lifetime, single native host and protocol seams |
| Reference app, fault/soak, costs and release | B21–B24 | Real examples, complete resources/failure behavior, workload comparison and final compatibility/doc/package acceptance |

The module implementing a symbol owns XML documentation, generated reference diff, guides and consumer examples in the same PR. A13 supplies shared infrastructure; it does not become the author or acceptance blocker for every later guide. A22 defines compatibility policy; module owners run it. A16/B24 own final clean-consumer and release composition gates.

## Required acceptance for a relevant task

1. Compile the exact implemented public surface, minimal and advanced consumers, overload/nullability/generic negative cases and generated descriptors/handlers on the pinned stable toolchain.
2. Run the task's actual Windows/Linux Native AOT obligations. A design-only AOT executable is an input oracle, not a passed product row.
3. Produce XML and a generated API Reference entry for every public/protected symbol, including generated output; validate parameters/type parameters/returns/exceptions and inherited lifetime/concurrency/capability/cost semantics.
4. Check managed API/source/binary compatibility and native ABI/domain version effects. Review default values, new overload ambiguity, disposal and error changes that assembly comparison cannot decide alone.
5. Match each feature to the coverage row and concrete native operation. Unsupported capabilities fail before side effects; no silent SQL semantic fallback, reflection fallback or fake implementation.
6. Inspect transitive packages/native assets and the complete installation/using/configuration/normal-operation/error/disposal/AOT journey. Avoid duplicate registration, unnecessary Engine dependencies and user-managed raw handles.
7. Record allocation/copy/pin/FFI/runtime costs and actual correctness/resource evidence. Independent review covers both implementation correctness and a developer consuming the package.

Not every task releases a package or exposes an API. Such tasks record precisely which items are not applicable and which downstream task validates composition; they must not omit their own internal/native boundary tests. Release and product authorization remain separate.

## Versioned maintenance

API changes update affected contract/document versions, node revisions, source/packet hashes and actual independent acceptance. Existing accepted records remain available at their original exact inputs. Current evidence cannot reuse an old translation approval for new API semantics. New projects copy or pin the Design adoption template into their own repository and install checks; no cross-repository AGENTS inheritance is assumed.
