# B19 private literal lookup: actual runtime source review

This note reviews the proposed bounded internal helper repair for B19-PREWALK-IDENTITY-BYTES. It does not replace final committed-source/actual-product regression review.

## Exact source identity

All ten files in `name-lookup-sources/source-manifest.json` were fetched at the actual fixed SDK/runtime VMR `297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`. Every local file has both a computed SHA256 and a Git blob hash matching the fetched source. The earlier `runtime-sources/source-manifest.json` supplies the exact NativeAOT TypeComponentsCache, QueriedMemberList, BindingFlags and NativeFormat CoreGetDeclared files used below.

## Called paths and allocations

Both `CoreCLR.RuntimeAssembly.GetType` and NativeAOT `RuntimeAssemblyInfo.GetType` call the common TypeNameParser for `Assembly.GetType(name, throwOnError:false, ignoreCase:false)`. This is a lookup of an emitted known definition, not a type/assembly scan. A generic definition name contains its arity; no constructed generic argument string is emitted.

`TypeNameParser.ParseNextTypeName` creates one full input string copy and TypeName nodes for its declaring chain. `GetDeclaringType` shares that original full-name string between the parser nodes; it does not eagerly make every full prefix. Common `TypeNameResolver.GetSimpleType` then allocates one nested-name string array, resolves each component name, and asks for the top-level name. `TypeName.Name` uses a small stack-backed builder with a possible pool expansion, then creates the component string. Name unescaping adds no growth beyond a conservative multiple of the literal length for these emitted definitions.

There is no sufficiently small hidden parser depth limit to rely on. `TypeNameParserHelpers.IsMaxDepthExceeded` explicitly returns false under `SYSTEM_PRIVATE_CORELIB`. This agrees with the successful long nested-identity probe.

CoreCLR's case-sensitive, nonextensible Assembly.GetType path calls `RuntimeAssembly.GetTypeCore` with the nested-name span. It does not take the managed GetNestedType reflection fallback used by extensible/ignore-case resolution. UTF8 marshalling remains conservatively covered by the character term.

NativeAOT resolves the top-level definition through its per-assembly case-sensitive cache. The exact native-format lookup splits the top-level namespace into strings and two arrays, then compares metadata names without materializing unrelated type objects. For each nested component it calls case-sensitive GetNestedType. The native-format name-filtered iterator creates only matching nested types; it does not eagerly create every sibling type. A new queried declaring type does create TypeComponentsCache with twelve per-name cache objects and three small object arrays. Each ConcurrentUnifier starts with capacity5, one lock, a container and its two arrays. A name-specific QueriedMemberList starts with64 member/flag entries and is compacted before the result is cached. These costs follow the selected emitted identity chain, and shared parents may be conservatively counted again.

The sources are in this note's two source directories. Particularly relevant locations are parser214-217/declaring construction, common resolver81-89, CoreCLR resolver293-310, AOT resolver209-217, AOT native-format assembly lookup15-32, TypeComponentsCache32-40/84-91/129-145, QueriedMemberList25-30/157-160, and ConcurrentUnifier66-69/132-142/297.

## Conservative admission formula

For each emitted private candidate let `L` be its literal UTF16 code-unit length and `D` its number of nested `+` separators. The implementation may conservatively admit:

`16 KiB helper cold margin + sum(16 KiB + 64L + 8 KiB * (D + 1))`.

This is an implementation-derived upper allowance, not an exact allocation measurement or a new protocol/API limit. The length term covers the retained emitted literal, full parser copy, component strings/builders/encoding, and namespace splitting. Even the worst fragmentation into short namespace pieces remains linear in L, with string headers and both reference arrays covered by that term. The per-node term covers the known NativeAOT runtime-type/member-cache/unifier layouts and temporary arrays; the fixed margins cover top-level lookup/helper/delegate initialization. It deliberately overcounts shared parents and cached candidates.

Admission must occur before entering the private method or materializing its literals. Splitting it behind NoInlining keeps an ordinary direct typeof result from causing private literal resolution during JIT compilation of that method. The direct methods and IdentityLookupBytes query contain no private identity literals. The runtime retains the admitted identity amount while it performs lookup and narrows the full startup grant only after adding identity storage to the complete exporter bound. Charging both count-method calls separately is conservative and avoids assuming parser temporaries from the two calls are free.

No arbitrary cap on unrelated direct roots follows from this review: their actual32/256/2048-case JIT and NativeAOT lookups allocated0 bytes. The byte estimate describes the actual private literal catalog that its private method may inspect. A byte-budget failure must report a bounded tool/context diagnostic before any rejected Type.ToString or FullName formatting. The existing pinned root-shape diagnostic is a separate path.

The proposed correction still requires the ordinary private/closed-generic/external-context JIT and NativeAOT witnesses and the original accepted long-identity product reproduction to verify the new admission boundary.
