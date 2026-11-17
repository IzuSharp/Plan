# B18 Linux x64 assembled gRPC handoff

Status: passed. This receipt covers the assembled B18 component on Linux x64.
Other-platform, pristine-machine, public-release and later combined-package gates
are not asserted by this component receipt.

## Frozen identities

- Managed source: `b8081f7975b40a4023e12d946e1f2c13428b1225` on `task/Task-06-B18-docs-linux`.
- Native build source: `6ba04525255132840f4673820d98a62f2c45d3dc`.
- Native asset SHA256: `b7ee6eed112490b4ddb040b12dfb762e7afa334493db658e8b61325a66695ecf` (8152064 bytes).
- Pinned Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
- Result SHA256: `f9edd545c16419b680c6d405585c5b0fbff5cc78d53b0fcd87d2dbceb3e8035d`.
- Command receipt SHA256: `2007d8fceb2991a556afaf9ef25d5df9aa217ac3d6e01da37eca01aaf3b87cef`.
- Exact managed source inventory: 170 files.
- Exact native build input inventory: 154 files, including Cargo lock SHA256 `ce93e01842e07707e6161c12cf273bc3086447f508408d55cc26fd6fd2357223`.

The native source is deliberately separate from the managed source. Later
native formatting or proof documentation does not change the identity claimed
for the supplied binary. The previously accepted native component receipt has a
different complete Server binary composition; its exact gRPC implementation
inputs match, and its command logs are retained under `accepted-native-component/`.
No native implementation tests or Rust build were repeated by this verifier.

## Actual results

| Check | Result |
| --- | --- |
| JIT transport execution | 308 assertions; 332 separately observed A07 retirements |
| NativeAOT transport execution | 309 assertions; 332 retirements; dynamic-code support false |
| Exact public API, XML and reference | 71 compiled declarations |
| Incorrect consumer rejection | 5 compile-negative fixtures |
| Exact native ABI | 48 exports; 8 records; 103 field offsets |
| Formal command receipt | 17 commands, all exit 0 |
| Ordinary NuGet package receipt | 25 commands, all logs and hashes verified; 106 producer/sample inputs unchanged |

The additional NativeAOT assertion checks the actual execution mode. Both
transport runs use the same supplied native binary and exercise clear HTTP/2 and
rustls TLS, unary/server/client/duplex streams, bounds, statuses, metadata,
authorization, deadlines, cancellation and close/retirement contracts.

Frozen JIT executable SHA256: `7da6e02d4f2e356060626c09eeb4636865294ccc041bf9a53697f30f59f75d5e`.
Frozen NativeAOT executable SHA256: `f23a49ba611dc645c1ffccd35d9b50480c27f22cf65853b58d505664021d7f99`.
Both complete output directories remain under `jit/` and `aot/`. Their before-run
inventories are `actual-jit-inputs.json` and `actual-aot-inputs.json`; all files
were checked unchanged immediately after execution.

## Reused independent package proof

Package summary: `/workspace/scratch/58d2a6adf1c3/.worktree/Task-06-B18-docs-linux/NativeWeave/artifacts/B18-docs/package-final/summary.json`.
Summary SHA256: `ba0991b1f2a55a40fa4ab4fc646bc22287687c65f51801273311f583f2cc598a`.
Producer source: `f2ca354547d9c9114fe4473b2953e6e000b0f6d6`.

That proof consumes five exact-version packages with ordinary PackageReference
entries and independent NuGet state, no working Rust tools, two statically
generated Protobuf services, and actual JIT/NativeAOT execution. It then changes a
Protobuf field and typed handler/client and repeats execution without changing
any package or native asset. Its 25 original commands and logs remain unchanged.
The explicit native provenance correction records the actual build commit and
compares 139 byte-identical runtime inputs to the originally recorded later
commit. It does not rewrite historical execution logs.

The package proof's baseline JIT output was intentionally replaced by the edited
build; its original source/lock snapshot and before-execution hash are preserved.
The edited JIT executable, dependencies and native file remain unchanged. Its
sibling `linux-x64/` AOT compilation directory was later rewritten by the edited
AOT publish, as recorded explicitly by the verifier. Both package AOT output
directories are retained unchanged. These retention limits do not apply to the
separately frozen formal `jit/` and `aot/` directories above.

## Next integration action

The root executor can ingest this result, command/log inventories and package
receipt into Plan B18 evidence, then handle the final combined gRPC/MCP asset and
repository PR/CI/release steps. No further B18 product edit is pending here.
