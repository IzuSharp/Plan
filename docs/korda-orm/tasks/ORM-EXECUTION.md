# ORM-EXECUTION — independent command execution

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Implement the driver-independent execution boundary for typed command binding,
buffered results and pull-driven streams. Accept a rendered template and invocation
values without traversing an AST, reparsing SQL or invoking the old C++ engine.

## Design and source inputs

Use the batch's pinned Korda-Design `docs/korda-orm/contracts.md` (ORM-C01, ORM-C03, ORM-C04,
ORM-C06) and `execution-aot.md`. The latter pins Dapper.AOT 1.1.0 `CommandFactory`,
`RowFactory`, `CommandT.Query` and their reviewed limitations. Reuse narrow patterns
with provenance; do not expose upstream runtime types as Korda contracts.

## Start and acceptance dependencies

Start after `ORM-FOUNDATION` establishes contract fixtures. Develop against fake
drivers and explicit factories while other modules proceed. Acceptance requires
`ORM-TYPES`, including final nullability/conversion descriptors. Provider integration
is performed by the driver tasks, not a prerequisite for this packet's start.

## Scope and ownership

Own `src/Orm/Execution/**` and `tests/Orm/Execution/**`. Consume shared contracts;
propose changes to their owner. Do not edit DSL nodes, renderers, provider modules,
schema generators, root package orchestration or historical database code.

## Implementation requirements

Separate reusable, value-free templates from owned per-invocation arguments.
Provide explicit typed binder/projector registrations without reflection or runtime
IL fallback. Validate layout identity, slot presence, NULL policy, connection and
transaction association. Validate result shape once and materialize rows through
typed access. Define ownership for caller-owned connections and data-source-opened
connections. Dispose readers, commands and leased buffers on completion, early
stream break, cancellation and failure. Preserve provider error causes and unknown
commit outcomes. Add neither a pool nor a scheduler nor automatic retries.

## Validation and acceptance

Use deterministic fake readers/commands for slot order, repeated values, duplicate
columns, empty results, required NULLs and conversion failures. Verify disposal
exactly once, including exceptions and abandoned enumerators. Compile and run a
Linux x64 Native AOT consumer using explicit factories; demonstrate no driver is
required by the pure DSL assembly. Register source/test paths and real dependencies;
inspect selected CI checks. Record allocation observations without claiming parity.

## Integration and stop

Publish contract fixtures for generator and provider implementers. Integrate the
accepted type descriptors and run only affected checks. Stop after the reviewed
module deliverable; do not add Dapper.AOT bridging, publish packages or switch the
existing product in this task.
