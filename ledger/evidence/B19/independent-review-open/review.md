# B19 independent implementation review — open required correction

Reviewer: `server_track`, independent of the B19 implementation author. Platform: Linux x64.
Review baseline: `9c87f1224a09886c2abc13900752a4d09e54fbe3`.
Pinned Design: `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`.
The B19 worktree was read only. The separate probe lives in the reviewer's ignored artifact directory; it does not build or mutate the implementation worktree.

## Result

**B19-MANAGED-INLINE-WIDTH is a confirmed acceptance blocker until corrected.**
The native managed-peak formula does not bound admitted source-generated DTOs containing nested inline value types. Both public registration and the actual native Host accepted the reproducer and invoked its typed Handler despite the framework-created DTO's live storage exceeding the default 4 MiB per-request managed-side budget.

This is an under-reservation before DTO publication, not an RSS claim, arbitrary application constructor allocation, or leaked retirement. The DTO uses ordinary automatic properties, implicit default constructors and the source-generated System.Text.Json metadata codec. Its large storage is the object instance the framework deserializer allocates; no user converter, custom constructor or allocation-producing getter participates. All instance storage necessarily exists before the value is passed to the application's Handler.

## Binding requirement and source

- `Plan/tasks/B19.md`, implementation steps 4 and 7: reserve the source-justified worst live managed/native peak, including static DTO copies, before public rmcp parsing; an unproved bound may not enable the profile.
- The same task, acceptance requirement at line118: reject wire/tree/UTF8/DTO overlap before SDK parsing and Handler admission when the 4 MiB request/side budget cannot fit.
- Pinned `docs/api/server.md`, section8 static metadata/profile contract and lines1189–1200: reserve proven framework expansion before allocation; the MCP preflight grant covers the decoded arguments/bridge; published DTO allocation transfers to application ownership only at the documented boundary.
- `native/protocols/mcp/src/preflight.rs:228–236`: `managed_peak` uses `3W + 4096N + 8S + 65536` and explicitly claims the coefficient covers sparse declared DTO storage.
- `native/protocols/mcp/host.rs:314–347`: adds the 2 MiB business-reply allowance and admits that managed grant before rmcp.
- `src/Protocols.Mcp/StaticSchema.cs`: admits the finite nested value-type metadata graph without bounding its inline CLR instance width.
- `src/Protocols.Mcp/Registry.cs:102–109`: the framework deserializes the input before publishing it to the Handler.
- `tests/Protocols.Mcp/allocation-proof.md`, Managed materialization and output: the 4096-per-node argument tests wide reference-property objects, which does not prove nested inline value-type storage.

## Isolated actual-Host reproducer

See `inline-value-probe/Program.cs`, `Probe.csproj`, `inputs.json`, `restore.log` and `run.log` in this directory. The input is `Input.Items`, an array of128 `Item` objects. Each Item has80 automatic properties of `Big06`. `Big01` contains one decimal; each of Big02 through Big06 contains two values of its preceding struct. Thus Big06 is512 bytes and each Item's mapped inline storage alone is40,960 bytes. The sparse JSON contains `{}` for every Item, so all that zero-initialized instance storage exists without corresponding property nodes in the wire input. The finite metadata limits and native schema depth limits both accept this shape.

The public-only probe references frozen product assemblies and the actual native asset, with SHA-256 hashes in `inputs.json`. It does not use internal friend access or a fake transport. It sends one real loopback HTTP/1.1 MCP call to the Rust Host and records:

| Observation | Actual result |
| --- | ---: |
| Entire MCP request wire bytes | 600 |
| Structural nodes, including keys | 149 |
| Decoded UTF-8 string bytes | 160 |
| Current input managed formula | 678,920 bytes |
| Current managed formula plus the entire 2 MiB reply allowance | 2,776,072 bytes |
| Default per-request per-side budget | 4,194,304 bytes |
| Warmed source-generated Deserialize allocated bytes | 5,248,664 bytes |
| Simultaneously live mapped inline DTO storage lower bound | 5,242,880 bytes |
| Public AddTool and native schema registration | accepted |
| Actual typed Handler admission | 1 invocation, all128 Items |
| Actual HTTP reply | 200, successful structuredContent |
| Close | Completed; requests/native/managed all zero |

The allocated-byte witness includes all allocations on the same synchronous decoder thread after one warmup. The stronger live lower bound uses `Unsafe.SizeOf<Big06>() * 80 * Items.Length`, so it neither relies on total allocation approximating peak nor counts object headers, array overhead, temporary decoder storage or output allowance. That lower bound alone exceeds the entire4 MiB budget.

Frozen native SHA-256: `d39217a5db19115035af1170d8968f48aa8b6ffb28a32b586092edc0cae75b21`.
Frozen MCP assembly SHA-256: `6e9c3feea650d6df5988eb2c7c5c9637a744ea24caf64f521b7dfc176a386f04`.
The observed source HEAD advanced to the managed close-tail fix `b2edecd42be79a0bd2e36ff51830ac7ae35f9fff` while review ran. Every reviewed B19 implementation/allocation source and the shared reply export is byte-identical to the9c87f12 baseline; `inputs.json` verifies that binding. The newer managed Host-tail change cannot explain the DTO storage mismatch.

## Additional schema-only correction counterexample

The separate `inline-layout-probe` uses the same frozen product/native inputs and a smaller accepted schema. Each Item contains only one property of `[StructLayout(LayoutKind.Sequential, Size = 65_536)] struct Padded { public int A { get; set; } }`. This is BCL layout metadata, not a custom constructor/converter. All128 Items are sparse `{}` objects.

Public AddTool, actual native schema registration, and the real Handler again accept the600-byte request with149 nodes and160 string bytes under the same2,776,072-byte total managed allowance. Warmed deserialization allocates8,394,392 bytes; the simultaneously live inline storage lower bound is8,388,608 bytes. HTTP200 success and completed zero-counter Close are recorded. Its input schema represents only one integer property inside Padded and cannot encode the extra CLR inline storage. Therefore deriving a coefficient solely from that JSON schema does not, by itself, correct the proven failure. This fixture identifies the missing proof boundary; it does not prescribe dropping ordinary struct DTO support.

## Correction expectation

Charge a source-justified bound that includes the admitted DTOs' actual inline instance expansion before rmcp parsing/managed deserialization. Keep the existing supported ordinary struct DTO contract. A correction must not merely reclassify framework materialization storage as arbitrary application code allocation, and a schema-only estimator needs an explicit argument for CLR storage absent from the schema (for example ignored inline members or BCL layout metadata). No new public API, alternate parser or runtime architecture is requested by this finding.

The implementation author and coordinator have the exact reproducer. Add a focused ordinary-inline-struct regression proving pre-parser/Handler rejection under the default insufficient budget and a justified supported success case where the configured budget fits, followed by separate native/managed retirement. Review status stays open pending the concrete correction and its source-bound evidence.

## Other reviewed paths

- Checked StaticSchema's exporter-visit accounting against the exact pinned `JsonSchemaExporter` source, including the `(JsonTypeInfo, JsonPropertyInfo)` cache, nullable uncached recursion, repeated scalar/property visits, inherited attributes, paths and defaults. No additional blocker established in that source inspection. This is not acceptance of the separate managed-materialization coefficient.
- Checked the reply export's validation order: request/kind/byte/schema/derived-peak and operation-slot failures precede consumption of the reservation wrapper. C# fallback therefore retains the same token on a failed create; successful create moves it once into the A07 operation. No owner-transfer blocker established there.
- Checked native preflight partial grant rollback and the Peak/Bridge/Body retained-owner chain through nested managed work, SDK response and actual body retirement. Existing author lifetime evidence remains distinct from this independent source review; historical matrices were not rerun.
- Reviewed the fixed native layout/allocation witness and enabled rmcp profile argument; no separate native coefficient failure was established by this review.

No acceptance is claimed while B19-MANAGED-INLINE-WIDTH remains open.
