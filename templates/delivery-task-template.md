# New Delivery Task Template (Not an Accepted Artifact)

Template status: is_template=true. After copying this into an independent task, fill in specific content; keep planned_candidate when source/interface support is absent, and do not create empty tasks in bulk.

## Identity, Purpose, and Version

Task ID, phase, title, revision, actual author/owner, user requirement ID, and design/research references. Explain the observable capability this work provides, why it is needed, and its explicit non-goals.

## Contracts and Actual Dependencies

List every contract's ID, exact version, and accepted requirement; list actual product dependency IDs and revisions; distinguish start and acceptance dependencies. Use conditional_dependencies for optional engines/protocols; unselected options must not block other tasks. Do not create a gate requiring all of phase B to wait for all of phase A.

## Implementation Boundaries and Interfaces

Exact write_scopes, outputs, and shared files that must not be modified; specific modules, types, functions/ABI layouts, threads/ownership, and state transitions. List tasks that may run in parallel and actual devices/ports/benchmark resources requiring local leases.

## Normal, Failure, and Race Paths

List normal operations, allocators/releasers, and error/cancellation/shutdown/reentrancy paths. State testable invariants and linearization points for the mechanism; for databases, make commit unknown/rollback/pool states explicit; for queries, make NULL and dialects explicit; for streams, make backpressure/capacity explicit.

## Verification and Cost

Specific unit/integration/property/fuzz/model/fault-injection requirements and why they apply. For each supported target, list OS/arch/RID, toolchain, Native AOT consumer commands, and failure criteria. Record FFI/copy/allocation/handle/thread/startup/RSS/tail-latency costs and benchmark evidence. Do not invent percentage targets without a baseline.

## Delivery and Acceptance

Source, tests, logs, lockfiles, artifact hashes, toolchain/platform, input seeds, replayable results, and evidence manifest. packet_sha256 binds the task body; independent review binds the current subject and evidence; retain blocked/partially_verified for unexecuted work. Identify the revalidation scope affected by upstream changes.

Generate actual nodes, prompts, and independent PRs according to the specification; update the graph through the integrator's fragment without rewriting unrelated tasks. Substantive evidence is required before accepted status; the template does not participate in acceptance.
