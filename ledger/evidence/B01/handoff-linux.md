# B01 Linux x64 delivery handoff

## Status and exact source

B01's Linux x64 component implementation and required component verification are complete. Windows acceptance is deferred by the user's Task-01 instruction. This is not assembled Database, live provider, generator, pristine-machine, or all-platform acceptance.

- Branch: `task/Task-01-B01-linux`.
- Worktree: `/workspace/scratch/0898a75257bc/.worktree/Task-01-B01-linux/NativeWeave`.
- Final clean source commit: `b34f819d9d0c4032635d292dff7b51872cde7a69`.
- Base: `1e7f8be161e3e208e0c76b168c197c5c24329e1b`.
- Locked Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`; all 18 B01 API input SHA-256 pins verified in `pinned-design-inputs.json`.
- Full runtime/package verification: immutable `run-4/`, tested commit `eaeb04d8b4bf1d7a45ddc6d0f47190e9bc11313a`, with the two actual AOT restore lock mutations recorded honestly in its source identity.
- Final source binding: `final-source-binding.json` maps all 38 owned files to the final commit, preserves every runtime C#/Rust/schema source hash, and records the subsequent lock-only build/documentation delta.

The final delta stores run-4's exact AOT lock bytes as `packages.linux-x64.aot.lock.json`, restores the ordinary lock bytes, selects the explicit-RID AOT lock in the two owned projects, and makes maintainer restores use `--locked-mode`. Both ordinary and AOT locked restores passed afterward (`split-lock-commands.json`, `split-lock-aot.log`, `split-lock-ordinary.log`). No runtime behavior or dependency version changed; the original successful evidence was not rewritten.

## Delivered scope

`NativeWeave.Data` is an independent BCL-only package containing the exact canonical Data declarations and real executable metadata/value/row behavior: typed columns/tables/projections/codecs, immutable entity keys and relation prefixes, changes/concurrency snapshots, typed SQL parameters/command descriptors, stack-only row readers/writers, error taxonomy, stable identity/canonical hashes and internal owned db-wire encoding/validation. It initializes no native runtime.

The native `nativeweave-data-contracts` crate implements the same canonical model/projection and kind23 relation definitions, checked db-wire envelopes, all 17 wire scalar tags, a bounded atomic metadata registry and shared physical-session admission/outcome/disposition/lifetime declarations. Mature `serde_json` and `sha2` implementations own JSON syntax and hashing. The crate has no database driver, native runtime or process-global metadata service.

There is one generated schema source, complete public XML, a generated compiled API reference, an exact compiled 132-symbol API compatibility check, and minimal/advanced natural consumers. Generated/manual identity tests call the same actual public API in two equivalent shapes; no B10 generator execution is claimed.

The related `NativeWeave.Database` source/session concrete classes remain with their owning B tasks, as B01 explicitly specifies. B04 owns the host; B05 physical transaction coordination; B06 actual streamed row owners; B07 provider conversions; B09 query/binding implementation; B10 mapping generator; B14 relation registration and execution. No throwing host stubs, fake driver, SQL parser/AST, managed provider, duplicate query primitive or unused Core package was added. The ownership table and cost/disposal/error experience are documented in `docs/guides/data-abstractions.md`.

## Actual verification

| Gate | Observed result |
| --- | --- |
| Locked Design API inputs | All 18 pinned hashes match |
| Compiled public API, XML and generated reference | 132 exact symbols; no additional public plumbing; complete XML |
| Managed contract test families | 12 passed in JIT and actual Native AOT |
| Independent Rust/C# canonical encodings | 10 golden files; same JIT/AOT bytes |
| Native malformed cases | 43 rejected; all 17 scalar tags exercised |
| Generic/ref-safety compile negatives | Wrong value, wrong entity, value-type entity and row across await all rejected with expected compiler diagnostics |
| Native quality checks | rustfmt check, strict clippy `-D warnings`, locked offline release build passed |
| Package isolation | Packed `NativeWeave.Data.0.1.0-preview.1.nupkg`; no runtime dependencies, native assets or build hooks |
| Outside-checkout package consumer | JIT and Linux x64 Native AOT published and executed; Rust invocation trap count 0 |
| Actual AOT mode | Both AOT binaries asserted `RuntimeFeature.IsDynamicCodeSupported == false` |
| Registry ownership/atomicity | Copy/retain, exact deduplication and failed budget/hash publication tests passed |
| Ordinary and AOT lock modes | Both task projects restore successfully with `--locked-mode`; exact run-4 dependency content retained |

The full runner command was:

```sh
RUSTUP_HOME=/workspace/scratch/d5dd057ef8a6/toolchains/rustup \
CARGO_HOME=/workspace/scratch/d5dd057ef8a6/toolchains/cargo \
PATH=/workspace/scratch/d5dd057ef8a6/toolchains/cargo/bin:/workspace/scratch/58d2a6adf1c3/dotnet-sdk:$PATH \
python3 tests/Data.Abstractions/verify.py \
  --dotnet /workspace/scratch/58d2a6adf1c3/dotnet-sdk/dotnet \
  --offline-packages /workspace/scratch/7d469df8fa51/interop-packaging-attempt-4/packages \
  --output artifacts/B01/run-4
```

The committed runner uses the same gates with the final separate locked-mode files. Use a fresh output directory when reproducing. NuGet was local-only using six pinned .NET 11.0.0 pack archives; vulnerability auditing was unavailable offline. No global/repository NuGet policy was weakened. Cargo was locked/offline and metadata was filtered to this Linux x64 acceptance target.

SDK 11.0.100 and rustc 1.100.0 were checked. Actual Rust linker selection was captured from the real Cargo/rustc link command: rustup's `ld.lld`. Native AOT selected GCC's `/usr/bin/x86_64-linux-gnu-ld.bfd`; the actual MSBuild properties, driver/linker paths, versions, binary hashes, ELF comments, OS release and SDK details are retained in `run-4/toolchain.json` and raw logs.

## Artifact identities

| Artifact | SHA-256 |
| --- | --- |
| NativeWeave.Data NuGet package | `5fefcaed2f8a1c445b8be5d27b56f83d6b17a86b96f5aef618f75a67cddcc758` |
| Product managed DLL | `ecbaaadde9d869b8646cc642005a878741d4bf0319c5c4e8b97793effb8a4cc6` |
| Rust golden verifier | `d66e5be56108c6a43bbd715e7a537b0be755a14e9909e3eafd5cc2a5f9c89ccf` |
| Actual AOT package consumer | `3a35c2a0c49fd03b18568c6317a02d056d56dcc92c7f5316a4e32900dff68728` |
| Actual AOT contract test executable | `9742f21ac3771f30a9edd98f383ceccb27209c6785e0dd2d03dffe02005caa0d` |

These hashes identify the retained run-4 outputs; they do not claim that an integration commit has been rebuilt or that a package has already been published.

## Review and failure records

Independent reviewer `/root/a19` accepted exact final commit `b34f819d9d0c4032635d292dff7b51872cde7a69` as `accepted_linux_x64_task_scope`, with no unresolved material findings. The review found and verified five corrected boundaries/evidence gaps:

1. Explicit zero timeout remains a finite expiration-before-dispatch value.
2. RFC8259 syntax accepts large exponent numbers and arbitrary object keys, with matching 64-container depth bounds; borrowed RawValue avoids numeric/object materialization.
3. The parent-key consumer requires exactly one row while general kind4 mutations retain their multiple-row and generated-only empty-descriptor domains.
4. An explicit scalar projection context admits only the one-field empty alias and preserves every other shape check; ordinary public projections remain strict.
5. Actual AOT binaries assert dynamic code is unavailable, and the executed Rust/AOT linker selections and platform provenance are captured rather than inferred from a default compiler name.

The independent changed-edge probes passed 17 managed and 15 Rust cases. The reviewer also audited the final build-only delta, 42 full-run command results, five output artifact hashes, four driver/linker hashes, ten JIT/AOT golden pairs and 15 Linux dependency nodes. The original and fixed probe sources are maintained by the reviewer under `/workspace/scratch/d5dd057ef8a6/reviews/B01-*`; the root executor owns durable integration of the separate review record.

`failures-and-dispositions.json` retains the observed development, review and environment failures and their precise disposition. It includes the rejected initial network restore attempt, the NULL-versus-empty fix, strict clippy/rustfmt corrections and Linux-filtered offline dependency evidence. Failed runs are not relabeled as successful.

## Dependencies and licenses

The direct native dependencies are pinned `serde_json = 1.0.154` with features `default,raw_value,std`, and `sha2 = 0.10.9` with `default,std`. The Linux build closure contains 14 registry packages plus this MIT component. `run-4/dependency-licenses.json` records the exact versions and licenses; the complete resolved feature graph is in `run-4/rust-dependency-metadata.log`.

The registry closure is block-buffer 0.10.4, cfg-if 1.0.5, cpufeatures 0.2.17, crypto-common 0.1.7, digest 0.10.7, generic-array 0.14.7, itoa 1.0.19, memchr 2.8.3, serde_core 1.0.229, serde_json 1.0.154, sha2 0.10.9, typenum 1.20.1, version_check 0.9.5 and zmij 1.0.23. Generic-array and zmij are MIT; memchr is Unlicense OR MIT; the remaining registry crates are MIT OR Apache-2.0 (version_check spells the same dual license MIT/Apache-2.0). The component Cargo lock also retains inactive target/optional resolution entries; those are not falsely reported as Linux-built dependencies.

## Integration instructions for the root executor

All changes stay within the B01-owned paths. No Plan worktree or shared solution/Cargo/build configuration was edited by this agent. Integrate the branch's six commits in order, or their equivalent cumulative tree:

- `a3775db3972fe3aa6c512198bc8652439a3068dd`
- `48176555c2a45a024fe8eb21c4c4054260935467`
- `69f52130abc4e0cd95fee9bc6bb1302c4d9d239b`
- `f42e520887cb0a8ed99fb2ae0be178eb570215f9`
- `eaeb04d8b4bf1d7a45ddc6d0f47190e9bc11313a`
- `b34f819d9d0c4032635d292dff7b51872cde7a69`

Shared minimal integration is the Cargo member `native/database/interfaces`, its exact dependency lock closure, normal solution inclusion of the Data project/test/sample as appropriate, and root license/build inventory composition. The crate carries explicit equivalents of the workspace's `unsafe_op_in_unsafe_fn = deny` and `clippy::undocumented_unsafe_blocks = deny`, so isolated and assembled checks use the same policy. The API-check project is a fixed-SDK maintainer tool, not a consumer dependency. Do not broaden a Hello World-specific package assertion to claim that Data has native assets or to weaken its existing bootstrap checks.

Copy this handoff, `final-source-binding.json`, pinned-input and failure records, targeted lock logs and the compact `run-4` logs/manifests/goldens to `Plan/ledger/evidence/B01/`; retain links to the independent review record. `ledger-packet/` is prepared as a compact evidence copy without compiler caches, packages or executable blobs. The actual binaries remain under `run-4/` with recorded SHA-256 values.

Root owns batch integration, Plan graph/ledger status, both existing Task-01 PRs (#12 in NativeWeave and Plan), and remote publication. No push was attempted by this agent because the root is preserving exact Git trees through the available GitHub path. No new version/release flow or extra platform/CI matrix was introduced.

There are no remaining B01 Linux implementation actions. The next authorized steps are root integration, scoped combined verification and the existing review/PR process. Do not execute another task packet from this handoff.
