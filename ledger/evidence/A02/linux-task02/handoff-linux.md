# A02 Linux handoff

Owner: `/root/plan_requirements`. Branch: `task/Task-02-A02-linux`.
Worktree: `/workspace/scratch/0898a75257bc/.worktree/Task-02-A02-linux/NativeWeave`.

Implementation and Linux component verification are ready for independent root review. See [summary](summary-linux.md), [full run](attempt-001/result.json), [consumer receipt](attempt-001/consumer-receipt.json), [final binding](final-source-binding.json) and [lock supplement](sample-lock-supplement/result.json).

Integrate these owned commits in order:

1. `d13473e` — bounded metadata/catalog/native loader, native fixtures, tests, samples, exact API/XML/reference and guide.
2. `6886f23` — generated-reference whitespace policy; full runtime evidence uses this commit.
3. `672494e` — sample-project Linux AOT restore lock only.

The preceding common dependency commits were cherry-picked as `96fe84d` and `52d3112`, equivalent to root's `5ecde8f` and `e7f5d05`; do not duplicate them. Root owns the Core project and A01 IVT, as well as Core's generated ordinary/AOT lock files. Those two untracked files exist under this worktree's `src/NativeWeave.Core/`, with exact hashes included in the full-run common inputs. No other shared file was edited by this agent.

Root shared registration requested: include the A02 test, maintainer API checker and sample projects in the existing solution as appropriate. No Cargo workspace member is required: fixtures compile the existing A01 source plus task-owned Rust glue directly. They must not become automatic release assets. Tests reference the single Core assembly and use the existing test-only IVT.

The scoped verifier accepts `--plan-root`, `--design-root`, `--output`, optional `--nuget-config` and `--offline`. It preserves failed attempts rather than reusing an output directory. Its API checker reuses B01's compiled Roslyn formatter, excludes the A05-owned three types, and supplements record-struct source classification because metadata omits that source keyword. Product/public member signatures are otherwise compared exactly to the pinned Design baseline.

Copy `artifacts/A02/ledger-packet/` into Plan's `ledger/evidence/A02/` after independent review, and reference it from the batch handoff. The packet includes every formal raw command stream and metadata result, no executables/cache/nupkg/source payloads. Their hashes and reproduction command are retained. Root owns all remote publication, PR updates, acceptance, merge and post-merge CI/preview. The subtask has not changed Plan or pushed remotely.
