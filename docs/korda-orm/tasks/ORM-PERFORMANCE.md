# ORM-PERFORMANCE — attributable execution and rendering costs

Status: `planned_candidate`; product implementation is not authorized by this plan.

## Objective

Measure Korda.Orm's additional rendering, binding and mapping costs against direct
drivers and Dapper.AOT under comparable conditions. Determine whether the complete
accepted implementation meets a declared performance budget without restarting
historical C++ optimization work.

## Design and source inputs

Use the graph-pinned Design `validation.md`, `execution-aot.md` and contracts
ORM-C03, ORM-C04 and ORM-C06. Pin the actual SDK, drivers, Dapper/Dapper.AOT pair,
database versions and accepted product revision. jOOQ rendering is a separate
cross-runtime reference, not an equivalent .NET execution baseline.

## Start and acceptance dependencies

Start after `ORM-FOUNDATION`: design fixtures, harness boundaries and comparison
criteria against contract doubles. Acceptance requires `ORM-INTEGRATION`; final
results must measure the real combined implementation. Harness readiness does not
accept performance, and this task does not block independent module development.

## Scope and ownership

Own `benchmarks/Orm/**` and associated maintained harness documentation. Submit
root project and registry proposals to their owner. Do not edit drivers, DSL,
generators or shared contracts to conceal unfavorable measurements; necessary
implementation fixes return to their owners.

## Implementation requirements

Separate construction, AST traversal, SQL generation, binding, driver I/O, mapping
and end-to-end paths. Compare fixed shapes, runtime shape changes and controlled
cache misses. Keep SQL, parameter values/types, row shape, preparation state,
connection ownership, buffering and server data equivalent. Inspect Dapper.AOT's
generated code so its baseline is actually intercepted. Separate SQLite's
synchronous work from network-driver async comparisons. Predeclare finite workload,
warmup, repetitions, uncertainty treatment and acceptance budgets; do not adjust
budgets after seeing an unfavorable result.

## Validation and acceptance

First verify result equivalence and negative-case behavior in every comparison.
Run compiled Native AOT .NET consumers; report latency/throughput, allocation/GC,
binary size and relevant resource conditions. Attribute costs using controlled
experiments rather than subtracting unrelated aggregate means. Record limitations,
regressions and rejected optimizations. Keep long campaigns and profiling outside
routine CI; retain only maintained conclusions and reproduction instructions in
Design/Plan, never raw samples or binaries.

## Integration and stop

Provide the acceptance owner with comparable results, explicit pass/fail budgets
and unresolved regressions. Stop after the bounded campaign and necessary scoped
corrections. Do not claim universal Dapper.AOT parity, launch indefinite tuning,
publish packages, merge or authorize product cutover.
