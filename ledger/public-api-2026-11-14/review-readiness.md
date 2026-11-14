# D32 — Complete Public API refinement and independent review boundary

Author/integrator: `/root`. This is an input to independent D32 review, not an
acceptance decision. The historical `ledger/reviews/D32.md` and preceding accepted
records retain their original bytes and their original scope.

## Scope and authoritative state

The existing 34 Research, 32 Documentation, 21 contracts, 48 future Delivery,
114 packets and ten fragments remain the entire task system. Version 0.4.0 refines
complete C# declarations, native operation mappings, consumer experience and
documentation; the separately versioned public API/documentation standard is
1.0.0. No NativeWeave product file or formal Delivery implementation is included.

Use `source-driven-baseline.json` for the exact current Design input, the Design
`docs/contracts/registry.json` and `acceptance-index.json` for contract state,
and the two Plan R/D graphs plus `ledger/completion-acceptance.json` for task state.
Candidates, prepared bindings and accepted bindings are distinct states. This
document intentionally contains no future acceptance or merge hash.

Database/ORM query, dialect, relation and execution mechanisms remain native Rust
over mature engines. Server networking, protocols and runtimes use mandatory
B17 Rust Host. C# owns strongly typed Fluent, static metadata/DTOs and business
handlers. Ordinary Entity/DTO/Handler changes use precompiled native assets with
normal dotnet build/run/publish, no manual rd.xml and no user Rust compilation.
Core remains minimal, with independent optional packages and no global runtime.

## Independent review allocation

Current reviewer records live in Design `docs/traceability/reviews/public-api-final/`.
Each scoped report supplies one attributable decision per owned subject. Notes
with open findings do not accept any subject, and an overall report does not
duplicate scoped decision rows.

| Actual reviewer | Research | Documentation | Contracts |
| --- | --- | --- | --- |
| `/root/final_architecture_review`, `interop-review.json` | R01–R18, R32–R34 | D01–D13, D21–D26, D31 | Platform, ABI, Binding, Lifetime, Callback, Async, Buffer, Error, Concurrency, Build, Engine, Verification, Performance, Extension |
| `/root/final_database_review`, `database-review.json` | R19–R25 | D14–D17, D27–D28 | Database, Transaction, Query, Query Generation |
| `/root/final_server_overall_review`, `server-review.json` | R26–R31 | D18–D20, D29–D30, D32 | Server, Protocol, Reference Application |

The Server reviewer also performs `global-overall-review.json` after the complete
domain reviews, fixes and necessary validation. These executors did not author
the reviewed technical changes. Their records are technical reviews, not claims
of approval by additional GitHub accounts.

## Completeness and evidence

The four coverage matrices classify relevant current stable .NET feature families
and identify exact managed/native mappings, owner tasks, AOT behavior, costs and
limitations. The compiler inventory and per-type policies determine the actual
symbol count; explicit planned/unsupported features remain visible. Every future
Delivery node binds exact API inputs, unique surface/documentation ownership,
implementation steps and concrete conformance obligations.

The isolated declaration fixture compiles consumers and negative cases, checks
generated reference fidelity, and publishes/executes a static Native AOT fixture.
It does not execute product Database or Server operations. Separate retained
package/generator/native-codec experiments preserve their own input versions,
actual execution, failure attempts and limits. Historical experiments are reused
only at their actual source identity. A hidden Rust PATH is not a pristine
no-Rust operating system, and neither experiment is product release acceptance.

Final review must independently close relationship registration/loading, nullable
FK expression typing, HTTP automatic completion, protocol-context restrictions,
binary gRPC metadata and native retained-byte admission liveness. It must also
check that exact acceptance follows every changed input, report and attestation.
The actual finding records and their rechecks determine closure, not this list.

## Exact acceptance and final integration

Follow `public-api-acceptance-workflow.md`. Commit normative inputs before creating
fresh contract/task input, evidence and review wrappers. The actual independent
reviewer must inspect and attest each exact wrapper hash before acceptance.
D31 binds the acceptance automation and CI as technical inputs; generated indices,
reports and attestations remain separate, avoiding self-referential file hashes.

Required current checks include Design API/history and complete contract binding
validation, Plan history and API ownership checks, exact prepared/accepted binding
verification, completion, graph/schema, general mutation, host selection,
provenance, lifecycle and Rust baseline gates. Targeted acceptance negatives reject
stale semantic inputs, changed independent reports, missing/wrong attestations and
inexact subject/evidence bindings. Actual CI results must identify their final head.

After all technical review and necessary checks, create one final PR per repository.
Merge Design first. Pin its actual merged SHA in the same Plan PR, compare all
reviewed input bytes, preserve candidate bindings, prepare fresh merged-source
bindings, obtain new attestations from the same real reviewers, rerun checks and
complete final review before Plan merges. GitHub rules and checks remain in force.

All 48 Delivery tasks remain `planned_candidate / not_authorized`. Real product
Windows/Linux AOT, pristine NuGet consumption, actual databases/networking,
cancellation/resource faults, load/performance and release duties remain assigned
to those existing tasks for a later explicitly authorized implementation phase.
