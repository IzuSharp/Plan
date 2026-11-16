# A02 Linux x64 implementation and verification summary

A02 implementation and component verification are complete on Linux x64. Independent root review and batch integration remain required before acceptance. Windows is unexecuted; no complete Database/Server, A17/A18 engine, A16/B24 release, or pristine-machine claim is made.

- Final owned source commit: `672494e0671fc5c9b5d5f40f753ddbb7e96abcb2`.
- Actual full-run commit: `6886f23a3c6e0dab6efb4f004d576554bfd0d27b`; `attempt-001/result.json`.
- Pinned Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
- Exact public API/XML/reference: **84 symbols**, 11 A02 types, compiled from the actual Core assembly.
- Actual isolated cases: **26 JIT + 26 Linux Native AOT**, **428 assertions per mode**. AOT executables assert dynamic code is unavailable.
- **108 formal commands succeeded**. Raw stdout/stderr and hashes are retained.
- The local NuGet verification consumer uses an independent directory/cache and prebuilt native assets; JIT and AOT succeeded, Rust invocation count **0**. `pristine_machine=false` is retained.
- SDK native destinations were observed: development retains `runtimes/linux-x64/native/`; publish flattens native filenames. The production reader consumed the corresponding exact output records.

## Implemented boundary

The BCL-only Core assembly exposes exact immutable ABI/capability metadata, validated package manifests, bounded explicit catalogs, load options and a process-resident loader. A01 remains the sole wire/status authority; A05 owns the three public exception types. One load/failure publication coordinates concurrent first use without holding its admission lock over native work. Package hash/ELF/RID/ABI/size/capability failures publish no domain owner. Additional capability failure does not poison a valid module. Compatible identities reuse metadata; conflicting content/package/ABI selection requires process restart. A post-load bootstrap failure is latched, while pre-load missing-file repair can retry.

The two independent Rust fixture modules link the actual A01 writer, have distinct prefixed exports and no domain runtime or worker. Known capability names map to actual advertised bits; unknown optional bit63 and a future larger bootstrap prefix are handled without inventing support or reading a tail. Fixed imports verify module identity. Optional function tables are not selected by any task profile and no universal table is invented.

Tests cover grammar/limits/snapshots, duplicate definitions, bounded single enumeration, mutable options, two-module coexistence,64 concurrent callers, exact one bootstrap call, older/newer compatible minors, rejected size/major/pointer/reserved/status combinations, bad DLL/ELF/RID/hash/export/CPU, unknown/default capabilities, bounded output-record malformed/duplicate/traversal/UTF8 controls, failed-selection latching and installation repair. Supports allocated zero managed bytes across10,000 warmed-up calls in each actual mode. This is a narrow measured check, not an engine performance claim.

## Scope and reproduction

Run `tests/Interop.Negotiation/verify.py` with sibling Plan and locked Design paths, the pinned .NET11.0.100/Rust1.100.0 toolchains, and a fresh output directory. This run used an explicit offline feed containing pinned Microsoft SDK/AOT package archives; vulnerability data refresh was unavailable. No repository audit policy changed.

The packages are local verification envelopes containing actual product assemblies and separate prebuilt fixture assets. They do not publish Core, add a product package dependency, or extend the existing automatic HelloWorld preview. A16 owns production SDK output-record generation and final package composition. Source/code is preserved in the implementation commits; the Plan packet contains logs, metadata and hashes, not duplicate implementation or binary payloads.

`final-source-binding.json` preserves the successful runtime source identity. A later sample AOT lock-only supplement passed actual locked restore and changed no runtime code. No complete suite was rerun solely for this lock addition. `failure-records.json` retains development observations and their resolutions. The actual native/AOT linker drivers, binary hashes and source/input hashes are in the run records.
