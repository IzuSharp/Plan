# Local host verification supplement — 2026-11-14

This supplement records the local reproduction of existing Design research on the
authorized Windows and Linux MCP hosts. It adds implementation preparation evidence
to the existing plan; it does not execute Delivery or change a task's acceptance.

The research inputs are Design `4c5c385779b753a4f06e59d07f80ad27ca10a841`.
The planning baseline is Plan `dacaab7fc346da5b649e943a4d937a756345c492`.
The Design supplement is `docs/traceability/local-host-validation-2026-11-14.md`,
with raw records under `verification/local-host/2026-11-14/`. The pull-request
descriptions link the paired PRs; the [local verification index](verification/local-host/2026-11-14/index.json)
records exact evidence identities alongside this supplement's validation results.

## What this closes

The prior final Server review explicitly distinguished the original 13-test
Windows/Linux protocol CI result from the later 19-test Linux result. Running the
current fixture on both local hosts addresses that specific platform coverage gap.
The codec experiment also exercises the full research package path: compile the
mature Rust codec adapter, package the native asset, consume it through NuGet from
a separate consumer directory, build and run without Rust tools on the consumer
PATH, add an ordinary C# type without rebuilding Rust, and publish and execute
Native AOT. Modern C# and database metadata fixtures check the same local setup.

These are bounded research experiments. The separate consumer shares an installed
developer machine, and PATH filtering does not create a pristine operating system.
The protocol fixture executes Rust components, not the future C# Handler bridge.
The database metadata fixture does not execute the complete C# ORM or PostgreSQL
service. No new throughput, memory advantage, soak or release claim follows.

## Local preparation corrections

Use explicit installed-tool paths and a matching `DOTNET_ROOT` in the MCP child
process. The existing service PATH did not reliably select the Scoop/Homebrew SDK.
Both hosts actually used SDK 11.0.100, runtime 11.0.0 and Rust/Cargo 1.100.0.

On this Debian 13 host, the Homebrew SDK's AOT link additionally needed
`libbrotli-dev` and `libzstd-dev`; installation and new-directory retries closed
the observed failure. On Windows, the existing platform research runner requires
`DOTNET_CLI_UI_LANGUAGE=en-US` for its diagnostic assertion and an unset inherited
`Platform` after `vcvars64` initialization for its fixed assembly lookup. Preserve
the MSVC linker/SDK environment. These are reproduced launcher requirements, not
new product architecture or acceptance conditions. The Design evidence retains
all four failed fixture attempts alongside the eight successful suite runs.

## Existing task ownership remains sufficient

| Local evidence or boundary | Existing tasks | Remaining acceptance work |
| --- | --- | --- |
| Tool selection and native linker prerequisites on both hosts | [A14](tasks/A14.md), [A15](tasks/A15.md), [A22](tasks/A22.md) | Validate the declared distribution/CPU profiles, dependency closure and runtime-only targets; one developer host per OS does not certify the platform matrix. |
| NuGet consumer, unchanged native asset after a C# type addition, actual AOT | [A16](tasks/A16.md), [A17](tasks/A17.md), [A18](tasks/A18.md) | Run the production facades and complete package closure on genuinely pristine no-Rust consumers; retain provenance, missing/invalid asset negatives and release checks. |
| Current Rust protocol cases on both OSes | [B17](tasks/B17.md), [B18](tasks/B18.md), [B19](tasks/B19.md) | Execute the production C# bridge, static DTO/Handler surface, transport interoperability, cancellation and pre-parse admission bounds. |
| Runtime metadata/SQL behavior | [B04](tasks/B04.md), [B11](tasks/B11.md), [B14](tasks/B14.md) | Execute the production typed facade, relationships, real backends and complete ordinary-entity reuse path. |
| Complete application end-to-end behavior | [B21](tasks/B21.md) | Run HTTP through the C# Handler and Rust Database with the reference service on both actual AOT targets. |
| Faults and resource stability | [B22](tasks/B22.md) | Run actual product failure/restart and the specified 30-minute, 24-hour and 72-hour load tiers; finite research tests are not soak evidence. |
| Performance and publication | [B23](tasks/B23.md), [B24](tasks/B24.md) | Demonstrate benefits through fair measurements and validate the full release/compatibility/clean-consumer matrix. |

No new task graph, task ID, global prerequisite or product implementation is
necessary for this local supplement. All 48 Delivery nodes retain
`planned_candidate` and `implementation_authorization.status: not_authorized`.
The 34 Research, 32 Documentation and 21 contract acceptances remain bound to their
existing exact inputs and independent reviews.

## Reproduction and acceptance pairing

Use the Design supplement's host-specific commands and fresh output directories.
Preserve an unsuccessful attempt before correcting the environment. Never run a
fixture with a fixed historical output path over its recorded evidence.

The formal Plan gate intentionally requires the Design commit in
`source-driven-baseline.json`. This supplement does not retarget that accepted
baseline to an unmerged evidence PR. For formal checks, use sibling directories
named `Plan` and `NativeWeave-Design`, with Design at the pinned commit. The local
execution working trees live below each repository's `.worktree` directory;
isolated gate checkouts preserve the standard sibling names and prevent runners
with fixed output paths from overwriting historical records.

The supplemental Design evidence and its review identify their own exact source
hashes. They can be reviewed and merged without claiming the old acceptance
attestations reviewed these new files. Future normative changes must follow the
existing affected-scope version, evidence and review rules.
