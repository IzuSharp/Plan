# Current phase — complete Public API refinement and exact acceptance

The active scope is the existing 34 Research, 32 Documentation and 48 future
Delivery tasks: source inspection, isolated Design verification, detailed public
API/native contracts, documentation standards, and the authorized Design/Plan
PRs and compliant merges. NativeWeave product files and the 48 Delivery
implementations remain outside this phase.

The 0.4.0 API obligations and contracts require actual independent technical
review and exact binding attestations. Their current states are recorded in the
graphs, Design registry and acceptance indices; candidate preparation alone does
not establish acceptance. Earlier 34R/32D/21-contract Accepted records remain immutable historical
facts, retained in `ledger/public-api-2026-11-14/prior-acceptance.json` and their
original committed evidence. They do not accept new API bytes. No recovered
script or prior successful run is counted as execution against changed inputs.

Database/ORM and Server execution require mature Rust engines. B15 owns the C#
application surface; B17 is the production Rust host. Kestrel is only a comparison
path. Ordinary Entity, DTO and Handler additions use precompiled native modules,
static C# metadata and normal dotnet build/run/publish without manual rd.xml or
user Rust builds. The existing 48 tasks now carry exact API inputs, type-policy
associations, document owners, module-specific guide/example scopes and concrete
consumer/Native AOT acceptance duties.

`public-api-acceptance-workflow.md` defines candidate freezing, actual independent
review, fresh contract/task evidence, per-reviewer binding attestations and the
single PR for each repository. Use original complete historical gates at their
original immutable pair and current gates at the actual pinned API candidate.
After review and CI, merge Design first, pin its returned merge SHA in the same
Plan PR, refresh the exact task bindings and validate again before merging Plan.

Design acceptance means implementation-guiding research and contracts have been
reviewed. Product execution, release, real-service fault/load behavior and
Windows/Linux package conformance retain their separately owned Delivery gates.
All 48 Delivery nodes stay `planned_candidate` with
`implementation_authorization.status: not_authorized` throughout this phase.
