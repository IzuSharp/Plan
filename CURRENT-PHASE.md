# Current phase: research, detailed design and future Codex planning

The latest user instruction limits the current work to research, detailed design,
technical experiments and completion of the existing development plans. It supersedes
earlier wording that could be read as permission to start formal product implementation.

| Repository | Current work |
| --- | --- |
| IzuSharp/NativeWeave-Design | Upstream source research, detailed specifications, proposed contracts, ADRs, experimental Rust/C# projects, actual platform tests and preserved evidence |
| IzuSharp/Plan | Existing 34 Research, 32 Documentation and 48 candidate Delivery tasks; dependency graphs, future Codex packets, exact evidence references and acceptance criteria |
| IzuSharp/NativeWeave | Read-only historical source and CI evidence; closing PR #1 is the sole permitted mutation after the verified Design and Plan migration updates have merged |

Never merge NativeWeave PR #1, change product main, create product development branches,
delete its historical branch/commits/evidence, or execute formal A/B Delivery tasks in
this phase. Future Delivery output paths remain product paths because they describe
future Codex implementation; they do not authorize writing there now. A successful
prototype or an accepted design decision does not grant product implementation permission.

Continue source-driven deep native integration and the mandatory Rust Database lower
layer, natural typed C# Fluent APIs and ordinary new entities reusing a precompiled
native engine. Do not introduce a complete managed SQL provider or require per-entity
Cargo builds. Server engine selection remains evidence-driven and must compare modern
C# Native AOT and Rust engine behavior, cost, memory and performance.

## Current migration pair

Design PR #7 is merged at `c7e123a74405a92dc3de1ef450355b08d1c05ceb`.
Its 139-path migration map and original 112-file evidence archive are in
`verification/native-slices/`. Six new Windows/Linux fixture jobs ran at Design
`67b48674e469c98f2f73f1c9ff0d63b113abc47b`, run `43371161177`; they are separate
from original NativeWeave runs. Plan binds this pair in `source-driven-baseline.json`
and `ledger/checkpoints/research-assets-migration-2026-11-12.json`.

The paired Plan update must be checked and merged before closing NativeWeave PR #1.
Do not infer closure from this document. The integrator must reread the PR and main,
verify the expected source head, close without merging, then record the actual outcome.

## Validation and acceptance boundaries

Research and detailed design may proceed in parallel with explicit assumptions and
local evidence. Existing successful fixtures need not be repeated merely to restore
context. Record missing tools, unexecuted cases, failures and remaining proof obligations.
Self-review, an independent agent review, GitHub required review and CI are different
facts and must be recorded separately. This migration does not accept any technical
contract or complete any Research, Documentation or Delivery task.

Future product work awaits a later user-authorized phase transition and its actual
accepted prerequisites. Ordinary technical choices and eligible Design/Plan integration
within the present scope do not need repeated user confirmation.
