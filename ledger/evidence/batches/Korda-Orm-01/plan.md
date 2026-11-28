# Korda-Orm-01 research and implementation-specification plan

Status: **research selection complete; final specification consistency and paired
PR delivery in progress**. The user's 2026-11-28 continuation reopened the earlier
own-executor choice and required instructions detailed enough for implementation
without another architecture design phase. This task authorizes research, formal
Design/Plan changes and necessary document CI only. Product implementation, merge,
publication, cutover and deletion remain unauthorized.

## Objective and fixed result

Design a Native AOT-first C# SQL framework by translating reviewed jOOQ language,
rendering, binding/conversion and nested-result semantics, while reusing mature
execution wherever practical. The supported selected route is unmodified
Dapper.AOT 1.1.0 Runtime, a small typed-layout CommandFactory adapter, statically
generated RowFactory subclasses and mature .NET providers. Normal incremental
generation writes those subclasses directly. The execution choice is now fixed;
implementers do not choose an alternative engine or design a new reader loop.

Original Dapper.AOT with controlled explicit DynamicParameters, stable prebuild
generation and C# Native AOT calling Graal/JDBC were demonstrated separately.
Original object-template bags and unhandled generic interceptor calls have concrete
AOT limitations. LINQ alternatives were source-reviewed and attempted within the
recorded limits. The comparison selects the smallest supported adaptation with a
complete typed native path; it does not mistake an API limitation or one failed
prototype for proof that a whole technology is impossible.

Only IzuSharp/Korda-Design and IzuSharp/Plan may change. Both continue the existing
`task/Korda-Orm-01-linux` branch and paired PRs
[Design #23](https://github.com/IzuSharp/Korda-Design/pull/23) /
[Plan #39](https://github.com/IzuSharp/Plan/pull/39). IzuSharp/Korda remains read-only
at the inspected revision. No new branch or PR is needed. Historical database,
C++, Rust and Server task graphs provide context and do not govern the ORM DAG.

## Formal deliverables and reading order

The [single Linux handoff](handoff-linux.md) records actual revisions, results,
reviews, CI and future product gates. The
[implementation entry](../../../../docs/korda-orm/README.md) and
[30-node graph](../../../../docs/korda-orm/implementation-graph.json) are the
implementation navigation and scheduling authority. The graph pins the immutable
Design input, including ORM-C01–C06 version0.2.0 and implementation-spec.md.

Design contains architecture, exact common declarations and node layout, immutable
capture/template protocols, profile/rule dispatch, execution ownership, generation,
source mappings, capability tables, alternatives and bounded validation. Each Plan
packet adds exact owned files and APIs, ordered algorithms, concrete state
transitions, error codes, positive/negative inputs and expected results, command
arrays, integration seams and stop gates. The plan is intentionally more precise
than a feature list. Any contradiction requires a coordinated contract correction;
it is not an open implementation choice.

## Completed research work and independent ownership

| Workstream | Actual work and formal output |
| --- | --- |
| Mature .NET execution | Original Dapper.AOT bags/interceptors, public runtime CommandFactory/RowFactory, four native provider paths, command initialization faults, typed-cell binding and execution/provider/integration/performance packets |
| Generator integration | Normal SG factory emission, final-consumer roots, closed row registration, stable staged alternative, analyzer host compatibility, portable offline schema, tool, package and documentation protocols |
| Java/jOOQ and SQL semantics | Execution/conversion/nested source inheritance, native shared-library/JDBC feasibility, dialect and nested real SQL edge cases, exact relational/expression/mutation surfaces and corresponding packets |
| Coordination | Read-only product/CI inspection, controlled comparisons, alternative LINQ attempts, shared contracts/signature probes, DAG/ownership, package-runner extension, cross-review and paired delivery |

These were actual parallel assignments with disjoint formal-file ownership.
Reviewers inspected other owners' sources and authored packets. Significant
findings changed the specification: library-only mapping initialization was not a
sufficient native root; template/runtime ownership and conversion provenance needed
explicit seams; SQLite scalar/RETURNING and MariaDB JSON budget behavior required
profile-specific rules; existing package validation needed an exact dependency
closure protocol. The handoff records the final repairs and evidence boundaries.

## Milestones and remaining delivery gates

1. **Complete:** preserve the existing task branches/PRs, formal reopening and
   read-only product scope; retain valid earlier jOOQ work without ritual reruns.
2. **Complete:** inspect pinned sources and distinguish direct reuse, extension,
   source translation, unavailable code and unsuccessful attempts.
3. **Complete:** run bounded complete typed DSL-to-database-to-result Native AOT
   experiments for promising routes and record exact environment/result limits.
4. **Complete:** compare attributable costs/maintenance and select the supported
   Dapper.AOT Runtime route. Research stop condition A is met: a route merits
   implementation. Further equivalent runtime experiments are not a prerequisite.
5. **Substantive authoring complete, final seam review in progress:** replace all
   30 generic task packets with concrete execution specifications; reconcile exact
   contracts, dependency direction, conversion propagation and package ownership.
6. **In progress:** publish final Design corrections, pin that exact revision from
   Plan, perform final independent consistency/file-purpose review and run normal
   local/PR document CI on the resulting heads.
7. **Pending only final delivery:** update this same handoff and existing PR bodies,
   report the supported decision and limits, and stop for paired review without
   implementing, merging, publishing or deleting the product.

Start dependencies are separate from acceptance dependencies. Foundation provides
compiled shared contracts and ownership, then language/rendering/dialects,
schema/generation, execution/providers and verification harnesses start in parallel.
Real modules and services become mandatory at each declared acceptance gate.
Four database profiles plus specified advanced/nested slices are mandatory final
scope; Parser is optional. Product cutover and retirement have later independent
review and concrete authorization requirements.

## Source and evidence policy

Every selected upstream is pinned to a release and full commit. Cite the exact
implementation path/symbol and the behavior it establishes. Preserve Apache/MIT
and transitive notices according to source/package ownership; do not equate a
commercial description, API stub or incomplete public test corpus with available
implementation. Reviewed jOOQ semantics are translated into deliberate C# contracts,
not a claim that Java's entire object model was copied unchanged.

Native research uses the isolated official .NET11.0.100 toolchain and the versions
recorded in Design validation. Actual generation, native execution, database rows,
resource behavior and timing are distinct observations. Signature-only compiles
are not functional implementations. Research probes do not satisfy the future
full public API, all package-consumer, platform, feature or performance gates.
The final strict public execution wrappers and complete plan are not claimed to
have been measured or shipped.

The implementation packets freeze prospective correctness and performance gates,
including negative tests and invalid/noisy measurement outcomes. They never
promote skipped cells or warnings suppressed for a diagnostic experiment into a
successful Native AOT result. Full product parity and zero-allocation claims remain
unestablished.

## Document CI and persistence

The existing docs/ledger prose rules select zero checks. The independent ORM graph
uses its registered schema/reference checks; the historical graph and existing
Python dispatcher/workflow semantics are preserved. No product build, database,
benchmark, cross-repository checkout or raw evidence upload is added to document CI.
Future product CI adaptations are fully specified in ORM-CI/ORM-PACKAGE but are not
implemented by this research delivery.

Commit and push reviewable formal milestones in the two allowed repositories.
Keep decisions, source references, concise results, reproduction methods and next
work in Git. Upstream checkouts, generated code, disposable prototypes, binaries,
logs, benchmark outputs, temporary scripts and agent notes remain only in scratch
and are never uploaded to Git, another application or a file library.
