# Task ID — title

## Objective and scope

State the intended result, owning module and current authorization boundary.
Identify relevant design contracts and the precise source/revision context.

## Dependencies and ownership

List start and acceptance dependencies separately. Register the task in the
appropriate graph, its packet path and any relevant fragment. Describe write
scope and parallel integration ownership without a project-wide lock.

## Implementation and behavior

Explain normal and failure behavior, interfaces, ownership/lifetimes, cancellation,
threading, capability checks and resource bounds. Preserve ordinary C# consumer
use and the selected native execution boundary. Keep public API documentation,
examples and compatibility work with the implementing task.

## Acceptance

Define observable positive/negative cases, applicable platform/Native AOT checks,
resource behavior and concrete comparison criteria. Product execution and
performance claims need actual results for the tested source and conditions.

## Result and review

Record progress, final conclusions, unresolved limitations, reasons for rejected
alternatives and source/PR links. Keep temporary output, logs, samples, binaries,
archives and recovery state on the execution machine. Submit documents through
Git/PRs; no Actions artifact copy is needed. Confirm the document's type and
path in [the registry](../eng/ci/registry.py).
