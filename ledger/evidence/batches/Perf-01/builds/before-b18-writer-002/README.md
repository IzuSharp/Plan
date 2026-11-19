# Perf-01: B18 writer regressions on the unchanged baseline

The existing scoped B18 verifier completed successfully on Linux x64 at
**2026-11-19 11:14:05 UTC**, with exit code 0. This is a functional regression
gate, with **no performance or 30-minute load credit**. All verification/build
activity ended before the next exclusive measurement window.

## Identity and scope

| Item | Actual identity |
| --- | --- |
| Product checkout, including the new tests | `e77dfc1c7c463f562bcf9688cd4259b862ad1fd7` |
| Unchanged runtime baseline | `ea5fa528035d025bd7a28698ee7c71194432236c` |
| Pinned Design | `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9` |
| SDK / Rust / Python | .NET SDK `11.0.100`; `rustc 1.100.0 (0ef1bc386 2026-11-09)`; Python `3.12.14` |
| Actual Server native SHA-256 | `4827a6ecc76f871e0b4828f4ff6fe23a0d0a4ca1c57c5fc89a10a8e4d83ffe69` |
| Actual AOT executable SHA-256 | `8ed3a02aa29e82a62da6d63222218a9fc81eebd23d5a1f1c8639fcd63a36bef1` |
| AOT instruction set | `x86-64-v2`, also checked in the actual ILC response file |
| Execution affinity | CPUs `2,3`; subsequent receipt copying used CPU `8` |
| Original successful output | `ROOT/perf01-evidence/functional/before-b18-writer-002` |

`git diff` from the baseline to the tested checkout was empty for `src`,
`native`, `global.json`, `Directory.Build.props`, `Directory.Build.targets`,
`Cargo.lock`, `Cargo.toml`, and `rust-toolchain.toml`; the checkout was clean.
The managed fixture was freshly built from the test checkout while the existing
before Server asset was supplied explicitly. No runtime candidate or native
rebuild was involved.

The verifier reused the accepted B18 native **component** receipt at
`ledger/evidence/B18/linux-final/accepted-native-component/result.json`, checked
its eleven matching gRPC source inputs and command logs, and independently
checked the supplied Server asset, ABI layout and exports. That older component
receipt has a different whole Server binary hash because its module composition
can differ. It does not replace the actual asset identity above. Its original
receipt is retained here; its original command logs remain in the existing B18
Plan record. This gate makes no other-platform, pristine-machine or public
package-release claim.

## Actual results

| Gate | Observed result |
| --- | --- |
| Existing verifier commands | All **18** exited 0 |
| Complete JIT B18 fixture | **662 assertions**, **393** separately observed managed retirements; dynamic code supported |
| Complete Native AOT B18 fixture | **663 assertions**, **394** separately observed managed retirements; dynamic code unsupported |
| Exact native ABI layout | **8 records**, **103 offsets** |
| Public API / XML | **71** exact compiled declarations; **5** negative consumer fixtures |
| Fresh independent NuGet proof | All **25** subordinate commands exited 0; **106** matching producer inputs |
| Package wire coverage | Four gRPC cardinalities in JIT/AOT, HTTP/2 clear and TLS, metadata/trailers and whole-call deadline checks |
| Ordinary application edit reuse | Generated DTO/protobuf/Handler edits rebuilt and ran in JIT/AOT with the same native asset; the Rust trap did not fire |

The new `WriterContracts.cs` exercises public transport behavior at encoded
limits 5,000, 10,000 and 65,539 bytes over a real HTTP/2 + TLS connection. It checks
exact-size backing storage, zeroed uncommitted tails, incremental/exact-limit
serialization, hint and `Advance` bounds, quota rejection before the encoder,
encoder failure compensation, actual native operation-creation denial with all
40 creator slots held, retry, collection of an otherwise unreferenced backing
array, and one-writer admission while an encoder is paused. The independent
client checks the complete ordered protobuf response sequence and terminal
status; the server assertions are surfaced outside protocol error redaction.
The existing B18 protocol, pressure and final ownership-drain assertions also
ran. Assertion totals above describe the complete fixture, not only the new
tests.

These results establish compatibility with the existing eager writer. They do
not demonstrate an allocation improvement, a weak-cache implementation, or a
native frame-credit reduction. Those source proposals are recorded separately
in `source-grpc-writer-reuse.md` and `source-grpc-frame-credit.md`.

## Initial failed setup attempt

`before-b18-writer-001` failed at 11:09:43 UTC before the managed test gates:
the existing exact-layout helper invokes the literal name `clang-19`, which was
not on `PATH`. The result, command receipt and failure log are preserved in
`failed-attempt-001/`.

The successful retry prepended a private directory containing only a
`clang-19` symlink to the already installed locked Clang 19 compiler. The target
binary SHA-256 is
`0a3c55936ac43954fbe4914e6e73b577ca9e35e75d89ef13d3e28c187f41ca1a`.
`compiler-launcher.json` records its exact target. No compiler binary, runtime
source or broad library-search path was changed to address this setup failure.

## Reproduction and retained evidence

Run from `ROOT/.worktree/Perf-01-protocol-linux/NativeWeave` with the recorded
test checkout, toolchain, Design and before asset available. Use a fresh output
directory for a new attempt; the command below records the completed attempt.

```sh
source /workspace/scratch/01c249676f47/perf01-toolchain/env.sh
export PATH=/workspace/scratch/01c249676f47/perf01-build/before/b18-writer-tools:$PATH
export IlcInstructionSet=x86-64-v2
taskset -c 2,3 /opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  tests/Protocols.Grpc/verify.py \
  --output /workspace/scratch/01c249676f47/perf01-evidence/functional/before-b18-writer-002 \
  --design /workspace/scratch/01c249676f47/repos/NativeWeave-Design \
  --sdk /workspace/scratch/58d2a6adf1c3/dotnet-sdk \
  --native /workspace/scratch/01c249676f47/perf01-build/before/native-stable/libnativeweave_server.so \
  --expected-native-sha256 4827a6ecc76f871e0b4828f4ff6fe23a0d0a4ca1c57c5fc89a10a8e4d83ffe69 \
  --native-source-commit ea5fa528035d025bd7a28698ee7c71194432236c \
  --native-component-receipt /workspace/scratch/01c249676f47/.worktree/Perf-01-linux/Plan/ledger/evidence/B18/linux-final/accepted-native-component/result.json
```

`result.json` is the original byte-identical verifier result, SHA-256
`fde4e57df8e143e06f91db9041514035f5c90ded78a988e0a5d4577dced3e8cc`.
`commands.json`, both actual-input inventories, every top-level command log,
the fresh package summary and all package command logs are retained here.
`verification-context.json` adds the launch environment and explicit baseline
equivalence check. `preservation-sha256.json` lists all **54** copied original
files, source locations, sizes and hashes; each destination was read back and
matched before commit. They total 260,645 bytes. The sum of the verifier's
recorded command durations is 165.411 seconds, a functional-gate duration only.

Original absolute paths in the unmodified receipts intentionally remain intact.
This compact record excludes private TLS material and native/executable
binaries. Those build outputs remain at the original local locations pending
the task-wide evidence archive. The committed receipts and logs are retained
with Plan history, without a separate expiration timer. A bounded process scan
after verifier exit found no remaining process matching this attempt or its
verifier; this is an end-of-run check, not continuous process tracing.

The original JIT and AOT logs each contain two trailing spaces after the empty
input in `PASS Strict timeout rejects ` lines. The full `git diff --check`
therefore reports these four preserved log lines. They were not edited because
the command receipts authenticate the original bytes; the Markdown and JSON
files pass their scoped whitespace check.
