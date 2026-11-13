# New Delivery task template (not an accepted artifact)

Template status: is_template=true. After copying it into a standalone task, fill in concrete content; without source/interface grounding, retain planned_candidate status and do not create empty tasks in bulk.

## Identity, purpose and version

Task ID, phase, title, revision, actual author/owner, user requirement IDs and design/research references. Explain the observable capability this work provides, why it is needed and its explicit non-goals.

## Contracts and actual dependencies

List every contract's ID, exact version and accepted requirement; list actual product dependency IDs and revisions; distinguish start and acceptance dependencies. Use conditional_dependencies for optional engines/protocols so that unselected ones do not block other tasks. Do not create a gate requiring all of phase B to wait for the whole of phase A.

## Implementation boundaries and interfaces

Exact write_scopes, outputs and shared files that must not be modified; concrete modules, types, functions/ABI layouts, threading/ownership and state transitions. List tasks that can run in parallel and actual devices/ports/benchmark resources that require local leases.

## Normal, exceptional and race paths

List normal operations, allocators/releasers and error/cancellation/shutdown/reentrancy paths. State verifiable invariants and linearization points for this mechanism; databases must specify commit unknown/rollback/pool states; queries must specify NULL and dialect behavior; streams must specify backpressure/capacity.

## Validation and cost

Concrete unit/integration/property/fuzz/model/fault-injection requirements and why they apply. For every supported target, list OS/arch/RID, toolchain and Native AOT consumer commands, and failure criteria. Record FFI/copy/alloc/handle/thread/startup/RSS/tail-latency costs and benchmark grounding. Do not invent percentage targets without a baseline.

## Delivery and acceptance

Source, tests, logs, lockfiles, artifact hashes, toolchain/platform, input seeds, replayable results and evidence manifests. packet_sha256 binds the task body; independent Review binds the current subject and evidence; unexecuted work remains blocked/partially_verified. Specify the revalidation scope affected by upstream changes.

Generate the actual node, prompt and independent PR according to the specification; update the graph through the integrator's fragment without rewriting unrelated tasks. Substantive evidence is required before accepted status; templates do not participate in acceptance.
