# B19 correction transport — independent contract assessment

Reviewer: `server_track`. This assessment is limited to the proposed internal transport; it is not acceptance of an implementation not yet reviewed. The confirmed B19-MANAGED-INLINE-WIDTH finding remains open until concrete code and evidence pass review.

## Pinned requirements

Design commit `c62cdb8aee833b6ab1a03e29a3f59f81a1b483f9`, `docs/api/server.md`:

- Section8, lines736–746: normalize only the reference DTO root object/null assertion, retain nested static required/nullable/element assertions, and do not apply a global null-oblivious override.
- Lines757–773: export a bounded static descriptor once from the explicit context, retain actual serializer semantics, and return the exact registered schema through native get_tool.
- Lines795–799: reserve the native/managed overlap before public rmcp admission; the conservative allocation formula is explicitly a B19 implementation acceptance input.
- Section10.1, lines967–990: the version1 protocol descriptor has an exact outer and per-tool key set. Existing input_schema and output_schema carry the static schema; no new descriptor key or repurposed codec identity is allowed by this correction.

## Rejected proposal: machine-required data in $comment

JSON Schema2020-12 Core section8.3 reserves `$comment` for maintainers' comments, permits implementations to strip it, and prohibits processing effects based on its presence or content. Section13 repeats that restriction. It is not an ordinary annotation output. Therefore a native allocation decision that requires a parsed `$comment` value cannot honestly be presented as standard `$comment` semantics. The coordinator agreed and rejected that proposal before implementation.

Primary source retrieved for this assessment: [JSON Schema2020-12 Core, Comments With $comment](https://json-schema.org/draft/2020-12/json-schema-core#name-comments-with-comment), including sections4.3.1,6.5,8.3 and13.

## Permitted narrow interpretation

A clearly namespaced, implementation-specific annotation at the root of the existing input schema is compatible with the JSON Schema extension/unknown-annotation mechanism. It must not be described as a standard keyword or standard allocation meaning. The pinned root-only rule constrains the nullability assertion transformation; it does not explicitly freeze nonassertion annotations. The allocation formula is deliberately left to B19. Keeping the existing descriptor keys, all assertion nodes and the exact registered-schema roundtrip therefore provides a narrow interpretation within the task rather than a new public API or protocol version.

The coordinator explicitly accepted this interpretation. The independent reviewer agrees only with these limits:

1. No extra version1 descriptor key, repurposed codec ID, altered C ABI export/layout, public registration overload or new native protocol exists.
2. The annotation is emitted by bounded registration code from a proven CLR storage bound. It is not derived solely from mapped JSON shape and is never supplied by the incoming client body.
3. The annotation has a bounded, versioned representation with checked numeric types/ranges; missing, malformed or unsupported proof data fails closed where it is required.
4. Existing root and nested descriptions/annotations are retained. Only the existing object/null root assertion normalization applies; no required, nullable, array-element or property assertion is strengthened or loosened.
5. Native list/get_tool returns the exact registered annotated schema, and schema validation/serializer behavior remains unchanged by the annotation.
6. Additional registration allocation/encoded bytes are charged within the startup scratch,64KiB schema and aggregate metadata caps.
7. The native pre-SDK managed reservation uses the proven coefficient for the actual admitted tool/handler. A caller cannot use a smaller proof through header/name/method mismatch and then reach a larger DTO materializer.
8. Focused actual-Host and NativeAOT evidence closes the original ordinary nested-struct, BCL layout, private/base-field and retention cases. The annotation is only the transport; it does not prove the bound by itself.

## Field-preservation work under review

The proposed compiler component preserves the fields of the finite explicit DTO/base closure through the existing MCP package's analyzer, including private/ignored storage and closed generic substitutions. Reference fields contribute reference slots instead of recursively expanding arbitrary application heap graphs. Public `RuntimeHelpers.SizeOf(RuntimeTypeHandle)` supplies exact value-type width, including BCL layout, while classes need a conservative field/base/layout/offset bound. Coverage must fail closed if NativeAOT preservation is missing; inaccessible nested types and external precompiled static contexts require an actual supported witness.

The isolated fixed-toolchain API probe confirms reference types yield8 bytes (the reference slot), a65536-byte explicitly sized struct yields65536, decimal16, and Nullable<Padded>65540. It does not substitute for the forthcoming class-layout proof or NativeAOT generator evidence.
