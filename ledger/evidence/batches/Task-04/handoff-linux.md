# Task-04 Linux x64 final handoff

## Completion

All ten Linux-applicable tasks are implemented, independently reviewed and accepted.
Both original batch PRs merged normally. Their actual merge CI and the existing
automatic preview publication and registry-consumer workflow succeeded. A15 remains
deferred. This is Linux acceptance; `global_acceptance` remains false.

| Task | Delivered scope | Actual verification |
| --- | --- | --- |
| [A06](../../A06/acceptance-linux.json) | Callback registration, revocation and drain | Native 5; JIT 6,332 / AOT 6,333 |
| [A07](../../A07/acceptance-linux.json) | Task bridge, cancellation and retirement | Native 4; JIT 355 / AOT 356 |
| [A08](../../A08/acceptance-linux.json) | Optional bounded executor and joined shutdown | Native 18; JIT 489 / AOT 490; 47 balanced owners |
| [A14](../../A14/acceptance-linux.json) | Linux native/AOT package closure | Six JIT/AOT consumers; observed emulated minimum CPU; runtime-only transfer |
| A15 | Windows native/AOT packaging | Deferred: outside this Linux run |
| [A16](../../A16/acceptance-linux.json) | Independent packaging and provenance | Fresh no-Rust SDK; 17 build cases; offline application edits; runtime-only transfer |
| [A17](../../A17/acceptance-linux.json) | Real synchronous miniz engine | Native 18; component JIT/AOT 147 each; package 139 each; API/XML 11 |
| [A18](../../A18/acceptance-linux.json) | Real Hyper/Tokio asynchronous HTTP engine | Native 4; component JIT/AOT 127 each; package 123 each; API/XML 36 |
| [A20](../../A20/acceptance-linux.json) | Cross-language properties and fuzzing | JIT/AOT 8,925 each; 72 bounded orders; 20,000 fuzz units |
| [A23](../../A23/acceptance-linux.json) | Linux thread-affinity integration | JIT/AOT 238 each; 15 owner-thread destructors |
| [A24](../../A24/acceptance-linux.json) | Heterogeneous generated Engine packages | Sync JIT/AOT 139 each / API 11; async 123 each / API 36; 66 common inputs unchanged |

Counts are assertions/cases within the named profiles, not an aggregate performance
measure. Normal acknowledged retirement is balanced; deliberately quarantined
negative children retain uncertain owners as documented. C ASan/UBSan cover the
declared A20 subset. Unbounded schedules, whole-process RSS and performance superiority
are not claimed. A23 unavailable GUI/GPU/mobile/static/WASM profiles remain separate.

## Merges, CI and publication

- Implementation [PR15](https://github.com/IzuSharp/NativeWeave/pull/15): `aa16521d609c0749d7c199f70eedad833b0d24c8`.
- Plan [PR18](https://github.com/IzuSharp/Plan/pull/18): `e62cfd630681fad87a59976239247597602befc4`.
- Actual implementation merge [CI](https://github.com/IzuSharp/NativeWeave/actions/runs/44035502220): success.
- Actual Plan merge [CI](https://github.com/IzuSharp/Plan/actions/runs/44036030778): success.
- Automatic [Release](https://github.com/IzuSharp/NativeWeave/actions/runs/44035502241): success; [NativeWeave.HelloWorld 0.1.0-preview.8.1](https://www.nuget.org/packages/NativeWeave.HelloWorld/0.1.0-preview.8.1) is `published-and-consumed`.

The release verified the NuGet.org repository signature, equality of unsigned payload
entries with the retained candidate, and actual HelloWorld/InteropTests JIT and Native
AOT consumers from registry bytes. Publication still covers the existing HelloWorld
package. Task proof packages retain their separately recorded local consumption scope.

A14/A16 also passed actual Ubuntu 24.04/glibc 2.39 composition, QEMU Nehalem minimum-CPU
execution, the pinned Ubuntu 26.04 SDK container without Rust, offline Entity/DTO/Handler
edits preserving native hashes, and an Ubuntu 24.04 runtime-only container without SDK
or native compilers. The CPU result is emulated evidence, not physical certification.

[ci-final-linux.json](ci-final-linux.json) and [publication-linux.json](publication-linux.json)
bind the exact actual runs, source trees, artifacts, receipts and package hashes. The
earlier PR and checkpoint evidence remains distinct from postmerge execution.

## Workspaces and recovery

ROOT is the existing checkout parent. Batch branches remain `task/Task-04-linux` in
both repositories, with worktrees at `ROOT/.worktree/Task-04-linux/NativeWeave` and
`ROOT/.worktree/Task-04-linux/Plan`. The ten prescribed `task/Task-04-<ID>-linux` component
branches are preserved; [source-recovery-linux.json](source-recovery-linux.json) binds
each original execution commit to a remotely fetchable identical source tree. GitData
transport commit metadata differs and is never relabeled as a fresh execution.

Implementation baseline: `5ca367a2fa53e0a756b4c5bcb506113d5c1371a1`.
Plan baseline: `dcf74c700a14fa1983defe2aaef1ca043b9dbc3d`.
Read-only Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
Toolchains: SDK 11.0.100 / C# 15 / Rust 1.100.0.

A02/A05/A09 are reused from [Task-02](../Task-02/handoff-linux.md);
A03/A04/A10/A11/A13/A22 from [Task-03](../Task-03/handoff-linux.md). No completed component
implementation or historical acceptance needs to be repeated for this handoff. Shared
solution/Cargo/friend registrations and fingerprints were integrated serially and
independently reviewed; all 246 task-owned files match their accepted source commits.

## Retained evidence and final record

[status-linux.json](status-linux.json) records all eleven task states, dependencies,
owners, branches, integrated commits and evidence references.
[raw-evidence-index-linux.json](raw-evidence-index-linux.json) identifies two retained
archives with per-file SHA-256 manifests, logs, failures, corpus, packages and runtime
bytes. Every accepted A18/A24 binary reference is retained. Three overwritten historical
preparation-only A18 binaries are explicitly listed as missing in the raw inventory;
their original receipts/logs remain and current bytes are not substituted.

This evidence-only closeout follows the existing Plan PR/check/merge workflow. Its own
PR and merge checks must be observed before the operator reports final completion;
their GitHub records avoid another commit solely to restate check results.

No remaining Task-04 Linux implementation or acceptance action is assigned. Other
platform work stays deferred, and this handoff does not start another task package.
