# B19 bounded field inspection — exact runtime source review

Reviewer: `server_track`. This note identifies the allocation surface the new compiler/helper proof must cover. It does not claim that the final correction has already passed review.

## Actual fixed-toolchain identity

The installed `dotnet-sdk/shared/Microsoft.NETCore.App/11.0.0/.version` and SDK11.0.100 `.version` both identify the VMR commit `297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f`. The fetched CoreCLR RuntimeType source at that exact `dotnet/dotnet` commit is byte-identical to the corresponding file in the older Design-referenced `dotnet/runtime` commit `deae2e32bf0e018e09d64597b7c59b62b73bb3ce`. This equality is checked, not assumed to apply to all runtime files.

Nine relevant actual-VMR sources are saved in `runtime-sources/`. Its `source-manifest.json` records primary source URLs, exact Git blob SHA-1s and computed SHA-256s; every saved file recomputes the upstream blob identity. CoreCLR RuntimeType SHA-256 is `dae6d94c2c3945634bb56fe246a6c6d1a1119e79ce1a0a9fc50ab1fb9df3a6f0`.

## CoreCLR: the requested BindingFlags do not bound cold cache population

`CoreCLR.RuntimeType.cs`:

- `GetFields` at2687–2690 calls `GetFieldCandidates(null, flags, false)`.
- `GetFieldCandidates` at2618–2637 first obtains the complete cached field list. Only afterward does it filter flags into a candidate list.
- `PopulateFields` at813–853 populates static, instance and literal fields from the type and its base hierarchy, then interface fields. The reflected type's own nonpublic fields participate; inherited private fields are filtered during population, but their declaring type's initial handle/metadata enumeration still occurs.
- `PopulateRtFields` at856–869 uses a64-entry stack buffer, then allocates an `IntPtr[count]` array if the runtime reports more handles.
- `PopulateFields` at842 requests a managed interface Type array before iterating it. Empty interfaces still contribute to this temporary even when they add no fields.
- `PopulateLiteralFields` at925–988 enumerates field metadata before choosing literal fields. A safe generated prelookup work bound can conservatively include the enumerated fields and interface entries without traversing any arbitrary DTO heap references.

There is also a **conditional warm-call temporary**, not just a long-lived runtime cache: `ListBuilder<T>` stores the complete cached length at construction (59–65) but does not allocate then. When a second matching field is added (104–118), it allocates an array of that full capacity; `ToArray` subsequently shrinks it to the matched count. Therefore a warm instance/declared-only query with at least two matching fields can still temporarily allocate according to static/inherited/interface field cache size. The conditional behavior matters; this note does not claim that a zero/one-match call allocates that same array.

## NativeAOT: broad query construction, then a filtered result array

At the actual VMR:

- `AOT.RuntimeTypeInfo.BindingFlags.cs:49,171–185` routes GetFields through the name-agnostic cached member query, then applies the requested flags via QueryResult.
- `AOT.RuntimeTypeInfo.TypeComponentsCache.cs:61–79` constructs a cached list with public/nonpublic, static/instance and inherited visibility, independent of the caller's final flags.
- `AOT.QueriedMemberList.cs` creates member and BindingFlags arrays, walks each base, constructs field objects through the policy, and applies inherited visibility. Both arrays grow in64-entry steps and are compacted afterward. `AOT.FieldPolicies.cs` does not stop at the declaring type.
- `AOT.QueryResult.cs:65–74` allocates only the final matching result count. Unlike the CoreCLR path, this examined final-copy implementation does not allocate the whole unfiltered length on a warm query.

Each queried class has its own reflected-type cache. Walking a derived type and then its bases may construct overlapping inherited member sets in distinct caches. A metadata work/reservation estimate must cover the actual per-query surfaces rather than counting each base field only once for the whole tool. Actual object storage is still calculated only from the declared instance fields; static field metadata is not a DTO payload.

## Field names: do not add a gate without an actual allocation path

For these name-null GetFields paths, CoreCLR skips name comparison and the NativeAOT declared-field iterator checks names only when a name filter exists. NativeAOT field construction stores metadata handles; its MetadataName getter decodes the string later. No eager per-field name-string copy was established for GetFields itself. A field-name byte restriction is therefore not justified solely by this source path. Any separate operation that reads names must be considered on its own actual behavior.

## Narrow correction requirement

The prior draft's declared-instance count after GetFields did not bound the newly framework-owned prewalk, and whole-assembly AssemblyMetadata materialization was likewise not bounded by a per-tool type cap. A known generated helper can supply finite conservative prelookup work bounds before allocation, while DynamicDependency preserves only the required type/field metadata for NativeAOT. The helper proof must incorporate the confirmed static/base/interface enumeration surface; it does not authorize unrelated assembly/type/heap scans.

The pin allows a bounded metadata-only prewalk before exporting schema; it does not turn a post-allocation cap into a proof. This is the existing bounded-prewalk requirement, not an additional acceptance standard. Cold framework-triggered reflection allocations are identified as metadata allocations, not relabeled user DTO allocation. Localized trimming suppressions must be bound to the emitted preservation proof and actual AOT witnesses, never reported as an absence of all suppressions.
