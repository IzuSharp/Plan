# A01 Linux x64 handoff

Status: component implementation, Linux x64 conformance and independent review complete; batch integration and remote persistence belong to the orchestrator. Windows x64 was not executed.

## Implementation identity

- Branch: `task/Task-01-A01-linux`.
- Initial implementation: `137fd7f1e36d5295e77d26ff3ef33ef8b26150e4`.
- Review fixes: `016be5190c0839ac567337d61ea2e786db38a3bf` (schema-derived signatures and mutation checks) and `502089df15b7da200aac6675d3aade2c4a7f1778` (actual linker provenance).
- Clippy integration fix: `47ca79fec337729499cc9ea7bd54892afafa5f11` (two existing SAFETY comments moved inside test macro expressions; no runtime code change).
- Final tip: `1412604137cc8294d1ffc0c3a7e99f697ec0a431` (separate ordinary and explicit Linux AOT NuGet locks; no runtime/ABI change).
- Worktree: `ROOT/.worktree/Task-01-A01-linux/NativeWeave`.
- NativeWeave base: `1e7f8be161e3e208e0c76b168c197c5c24329e1b`.
- Plan input: `050d54cc2433901cbe896f7490af0e94ba631415`.
- Locked Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
- Every pinned API input and three direct contracts matched its expected SHA-256; see `design-inputs.json`.

The product source defines one versioned ABI schema, generated C/Rust/C# storage, bounded stateless Rust bootstrap writing and internal managed validation. Five shared records contain 21 fields; every size, alignment, offset and width is checked in C, Rust, managed JIT and actual AOT. All 14 status values and defined reserved fields are checked. No raw pointer or new metadata API is public in the managed assembly; A02/A24 remain responsible for public metadata/preflight APIs.

The native test engine exports only `nw_abi_conformance_get_abi_v1` and calls the product writer. Its artificial capability bits do not represent any Database/Server capability. It is not distributed as a production engine. This is a component boundary test, not assembled engine acceptance.

## Accepted execution candidate

`attempt-005/result.json` at `502089df15b7da200aac6675d3aade2c4a7f1778`: all 47 commands exited zero, actual Linux x64 AOT executed, no implementation input changed during verification. Its source hashes were subsequently compared to the committed Git bytes with **zero mismatches**. Source snapshot SHA-256: `92104c0daf67b9091d91ea2ba8476d70d2a6142b9b67a41ef23bc8bb4ad89736`. The worktree was clean after final RID restores completed. The subsequent comment-only tip passed the focused Clippy deny gate, rustfmt and both native tests (`comment-gate/result.json`); the batch orchestrator runs the shared workspace gate.

- Native Rust unit tests: 2 passed.
- C/Rust/JIT/AOT complete layout outputs agree with the checked-in target oracle, with no implicit padding in these records.
- Real compiled C mutations: reordered major/minor offsets and narrowed view length width were both rejected. The narrowed field preserves the struct size, so field-width detection is necessary and exercised.
- Four non-executing schema mutation tests verify callback parameters, callback return values, bootstrap signatures and rejected language booleans. This closes independent review finding A01-REV-001: the C, Rust and C# signatures now derive from the canonical schema, instead of a hardcoded managed function pointer.
- Managed JIT and Native AOT: **682 assertions each**, including all short capacities 0–31, unsupported majors, null/misalignment no-write cases, larger-tail sentinels, incompatible architecture/minor/required capability, unknown status/PENDING rules, all reserved bits and 128 concurrent bootstrap calls.
- Minimal/advanced maintainer samples compiled and executed; actual AOT sample executed with dynamic code unavailable.
- Compiled managed surface: zero public types/members; internal XML documentation and generated API reference contribution checked.
- Exact compiler, SDK, kernel/architecture, commands, source/lock hashes and native/managed/AOT artifact SHA-256 values are in the result and command files. Native ISA is explicitly x86-64-v2. Rust's actual emitted link arguments select the toolchain LLD 23.1.5 (LLVM commit `0a5579eb649d3634a9c30ac873300cc2944fa070`), independently corroborated by the ELF comment. C and the SDK-selected GCC Native AOT driver use GNU ld 2.44. Selected driver/linker paths, binary hashes and versions are recorded separately.

Reproduce with the locked toolchains on PATH:

```sh
python3 tests/Interop.Abi/verify.py
```

This environment used the command's `--offline-packages` option with an existing cache of Microsoft .NET 11 SDK package archives. It creates an explicitly local source with no remote feed and records unavailable vulnerability-data refresh for that local invocation. Normal repository and CI audit settings remain unchanged. No ordinary consumer is required to invoke Rust through MSBuild.

## Ordinary/AOT lock integration follow-up

The shared ordinary locked restore exposed an actual NU1004 failure: the previous AOT restore had overwritten `packages.lock.json` with Linux RID/ILCompiler dependencies. `restore-compatibility-001/negative-ordinary-restore.*` preserves that failure. Final tip `1412604137cc8294d1ffc0c3a7e99f697ec0a431` selects task-owned `packages.linux-x64.aot.lock.json` for explicit AOT and keeps ordinary `packages.lock.json` for normal builds. The three AOT locks retain the previously verified dependency bytes. Both verifier restore paths now use locked mode, and the source stability check includes all six locks.

`restore-compatibility-001/result.json` records six successful, bounded local-feed restores: tests and sample in ordinary mode, explicit Linux AOT mode, then ordinary mode again. Every command exited zero; all six lock hashes stayed unchanged after each step, all changed source/lock hashes matched the final commit, and the worktree remained clean. This was a focused restore validation; the existing immutable JIT/AOT runtime acceptance was not rerun or relabelled. A supplemental independent review of this lock-only integration fix is being recorded separately.

## Preserved earlier attempts

- `attempt-001/`: C/Rust verification completed, then automatic approval review terminated online restore and reported an attempted metadata-endpoint connection. No such endpoint was requested by this task; the restore did not return captured output. `interruption-note.txt` records the boundary. No acceptance claimed.
- `attempt-002/`: successful development JIT/AOT tests, but implementation inputs were refined while the run executed. `implementation-note.txt` explicitly excludes it from single-snapshot acceptance.
- `attempt-003/`: initial immutable implementation passed all 37 commands, then independent review found the generator signature drift gap and linker provenance gap. Its earlier acceptance evidence remains intact, superseded by attempt-005 for the reviewed implementation.
- `attempt-004/`: follow-up stopped at the new MSBuild linker-provenance query, because its isolated target lacked ResolveReferences. No acceptance is claimed. The corrected target and actual Rust linker capture passed in attempt-005.
- A manual provenance-target query outside the runner omitted telemetry opt-out and automatic approval review blocked Application Insights egress. It was not used as evidence. The safer local retry explicitly disabled telemetry and passed; the acceptance runner already sets that opt-out and uses the local SDK feed.

## Integration and remaining review

Root-only integration requested: add `native/interop/abi` to Cargo members and these projects to the solution: `src/Interop.Abi/Interop.Abi.csproj`, `tests/Interop.Abi/Interop.Abi.Tests.csproj`, `samples/api/interop-abi/Interop.Abi.Sample.csproj`. No shared build files were modified by this subtask.

The A19 agent independently reviewed the internal-only API applicability, generated authority, output-write guarantees and exact evidence, and accepted final tip `47ca79fec337729499cc9ea7bd54892afafa5f11` with no unresolved material findings. `A01-review.json` and `A01-followup-audit.json` are in the shared review directory for the batch ledger. Review verified 32 source hashes, 94 output streams, 8 artifacts, 20 Design input hashes and 4 linker/driver hashes. The final comment-only change is explicitly separate from the immutable full execution. A13/A16 later own release composition/pristine package consumers; A01 itself is not an independently released application NuGet. Windows acceptance remains separate and pending.

An ordinary Git push failed with missing HTTPS credentials; no remote write occurred from this subtask. The local commit is available for batch integration and connector-backed persistence. PR creation remains with the batch orchestrator.
