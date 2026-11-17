# B19 static layout proof — final Linux handoff

Status: complete for this compiler/preservation correction. No further owned
production or documentation changes are pending. The worktree is clean at
`4b8b65a1081dbe0f0317222abc0378668c42ec8e` on
`task/Task-06-B19-layout-linux`.

Worktree:
`/workspace/scratch/58d2a6adf1c3/.worktree/Task-06-B19-layout-linux/NativeWeave`.

## Final positive proof

The frozen receipt is `final/result.json`, SHA256
`342d221bf095cbab7ece60e27a90d78243cb5a524210b75bf58ee9a56765008d`.
It records the exact 24 owned source hashes, 101 artifact hashes and all 10
successful command/log entries under SDK 11.0.100 on Linux x64.

| Validation | Result |
| --- | --- |
| Compiler discovery/final-compilation invariant driver | 65 assertions passed |
| Ordinary locked restore/build and JIT witness | 80 assertions passed |
| Separate Linux x64 AOT locked restore/publish and native executable | 80 assertions passed |

The final witness includes ordinary private nested DTOs, inaccessible generic
bases with substituted inline storage, ignored/private fields, explicit layout
padding, records, primary constructor capture, events, and a separate compiled
static JSON context. It also exercises the actual public `AddTool` registration
path for that external context and the bounded missing-proof failure of an
erased generic registration path.

The final compiler is the identity-corrected `7c800ff393574f76a05192c03767f75453e3bc87`
paired with runtime correction `182ead3` (locally cherry-picked as `b2df235`).
The later `4b8b65a` adds the focused reproduction script only. The final positive
run therefore checks the new fixed-literal `Assembly.GetType` private lookup,
not the superseded incoming-`FullName` implementation.

Key immutable artifacts:

| File within `final/` | SHA256 |
| --- | --- |
| `aot-run.log` | `d503c6925c163fa032add62ed31e7f41ebc2f5387d163785b6ae884b2cfc02d4` |
| `aot/NativeWeave.Server.Mcp.Layout.Witness` | `900facf7ab3cb95ab8277d57ef26dc0d3b57dfc5e0140e8c644ae2b80663748f` |
| `jit-run.log` | `e2d6f0f553ad5183b8de79ce04fec8d20527f7087c8e169688c1af6db6337989` |
| `NativeWeave.Mcp.Layout.g.cs` | `8a00b3689cd3a18d889521336648879a3d9c3e2b7c7b663f29f273a7aa15dbc2` |

The supplied native asset has SHA256
`b7ee6eed112490b4ddb040b12dfb762e7afa334493db658e8b61325a66695ecf`.
It is an unchanged Server project build input only: this focused witness does
not rebuild Rust or execute the native MCP protocol. The full product Host,
transport, lease and independent package acceptance belongs to the root/query
receipts using their separately identified final composed native asset.

## Scope and source-backed accounting

The existing MCP package carries this nonpackable compiler component. It adds
no public API, package, runtime registration table, assembly scan or private
runtime-layout dependency. Discovery is limited to explicit static JSON roots
and concrete semantic `AddTool` input/output types.

The generator preserves class/base fields and emits the exact internal helper's
declared-instance and broad-reflection-cache upper bounds. A final-compilation
analyzer rejects an understated proof after other generators have run. Inline
value storage remains measured by the public .NET 11
`RuntimeHelpers.SizeOf(RuntimeTypeHandle)` API. Reference-field storage does not
expand an unrelated ignored/private heap graph.

Accessible identities use direct `typeof` comparisons. Private identities use
fixed emitted names on statically known assembly anchors in a separate
`NoInlining` method. `IdentityLookupBytes` exposes the conservative cold/parser/
literal/cache cost before either count method can materialize those names.
The runtime includes both possible count lookups and all attempted explicit
assemblies in its existing startup scratch grant. Missing or oversized proof
has a bounded diagnostic that does not format the incoming type identity.

The implementation explanation is already committed in
`src/Protocols.Mcp/Generator/README.md`. The exact SDK/runtime VMR
`297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`, official source URLs, verified
content/blob hashes and formula inputs are in
`src/Protocols.Mcp/Generator/runtime-identity-sources.json` (SHA256
`9b49f1f16b3e89b1ddee08b8faed1ea9b88c13e6c081a304763895cc8f86cabe`).

Ordinary project references use the existing SDK
`CompileUsingReferenceAssemblies=false` mechanism through the MCP package
hook. Ref-only third-party compile assets cannot prove absent private fields
and remain uncovered unless their own compiled static-context assembly carries
the helper. No private-field count is guessed from an incomplete reference
assembly. Only the fixed, source-checked framework roots have narrow exceptions.

## Related immutable evidence

The private implementation edit receipt at `private-edit-final/result.json`
has SHA256
`d76c1ffe58d5324b32771e228de9e1a6a2181f6e17e9e431811bfc0e0258e28d`.
It proves normal project-reference rebuilding: the reference DLL hash remains
unchanged, the implementation DLL changes, both generated field bounds rise
by one, and JIT/NativeAOT retain 80 passing assertions without a Rust build.
This earlier receipt establishes the incremental SDK dependency mechanism;
the final positive receipt above establishes compatibility of the corrected
private identity lookup. The final ordinary NuGet equivalent is recorded by
the query agent's package acceptance and is not duplicated here.

The independent reviewer replay of the original legal long-private-name graph
is at
`/workspace/scratch/58d2a6adf1c3/.worktree/Task-05-B14-retention-linux/NativeWeave/artifacts/B19-review/identity-fixed-final/result.json`,
SHA256 `e690b8dc9475a8b525a6cdfe774f4fc3c0cc062fd1a40bd437d270a6045649f3`.
Against the corrected pair at `25c1476`, JIT rejected before expansion with
8,016 allocated bytes and NativeAOT with 30,056 bytes; the diagnostic was 189
characters. The local additional replay is preserved at
`identity-final/result.json`, SHA256
`4b9bed535fd5c0a6511d5b309251e11edee47d918916695b1dadad5046e32195`.
Neither replay needs to be repeated for this handoff.

Earlier preservation-only and failed intermediate probes remain in their
separate stage directories. They are not substitutes for the final receipt.

## Integration handoff

All owned source commits through `4b8b65a` have been sent to root and integrated.
Root owns the shared solution/package composition, Plan evidence import,
remote checks and normal PR completion. The compiler README/source proof is
ready as committed; no additional source commit or validation matrix is needed.
