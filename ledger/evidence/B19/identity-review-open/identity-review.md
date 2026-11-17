# B19 independent review addendum: private identity allocation

Status: **open correctness finding**, B19-PREWALK-IDENTITY-BYTES.

Reviewed runtime correction: `ec8d750aca850f805caaf8713966b25b93790ffe`. Reviewed generator logic: `f71374abcc4032b0503cfcf8ce3580cc39ae8fb5` (8d1b3f8 bounded-helper implementation plus f71374a framework equality-interface correction). The frozen product MCP DLL SHA256 is `d26467b0a13ec89a6a0496c522203fce2a3ed73129abca1ff22253707a4988fc`. Exact frozen assembly/analyzer inputs and probe source/log hashes are in `helper-public-identity-probe/inputs.json`.

## Required contract and exact cause

Plan B19 implementation step7/acceptance requires proving and admitting framework-owned expansion before it is allocated; pinned Design `server.md` section8 also bounds startup schema scratch at4MiB. The new runtime correctly reserves that grant before metadata work and correctly admits field-cache counts before GetFields. However, the generated private-type fallback in `LayoutPreservationGenerator.Emit` first calls `definition.FullName` and `definition.Assembly.GetName().Name`. Its return values contain only declared/reflection field counts. Neither those counts nor the current static scratch formula bounds the selected identity strings before construction.

This is a different allocation from field names. The exact runtime GetFields name-null paths decode no field names eagerly; no new per-field name quota is proposed. It is also not a claim that the unrelated global helper table allocates in proportion to its number of branches.

## Actual public-product reproduction

The independent `helper-public-identity-probe` uses ordinary source-generated JsonTypeInfo, the shipped internal compiler analyzer, and the public `McpRegistry.AddTool` API. It has62 JSON metadata types,120 mapped properties, no recursive JSON shape, no custom constructor/converter, and a shallow JSON object graph. Sixty child classes are private only because their first declaring container is private; the legal70 declaring-type components are500 characters each. CLR declaration nesting is unrelated to JSON graph depth.

Release build succeeded with0 warnings/errors on the fixed SDK11.0.100/runtime11.0.0. Public AddTool accepted the graph against the frozen current product. `run-2.log` records:

- 60 selected FullName values, maximum35,083 characters, total2,104,970 characters;
- UTF16 character storage alone4,209,940 bytes, greater than the4,194,304-byte startup cap, without string headers or any other prewalk/export allocation;
- total measured AddTool allocation9,361,464 bytes;
- one Gen0 collection during AddTool;
- all60 selected FullName strings still strongly reachable after two forced full GCs while the registry/static metadata remain alive.

The strong-retention check matters: CoreCLR RuntimeTypeCache has a weak handle, so merely adding cumulative allocation would not prove the simultaneous live bound. The actual static metadata/product path retains all observed names. The probe keeps only weak references to strings for this check. This is not a no-GC-region result.

A separate compiler/CLR-only probe (`helper-identity-probe/run-2.log`) independently demonstrates that the fixed C# compiler and CLR permit these full nested identities:60 types load successfully and selected FullName/Assembly.GetName reads allocate4,233,448 bytes. A per-component NameTooLong rule therefore cannot establish a sufficiently small total nested FullName bound for these actual APIs.

## What the unrelated-table probe established

`helper-lookup-probe` exercises generated-shape lookups under both actual JIT and Linux NativeAOT. Direct typeof scans through32,256 and2,048 cases allocate0 managed bytes on both first and second calls. An indirect lookup scanning2,048 unrelated string cases has the same bounded selected-identity behavior as a single-case lookup; no proportional branch-table allocation was observed.

| Runtime | One indirect first / second call | 2,048-case indirect first / second call |
| --- | ---: | ---: |
| JIT |1,152 /512 bytes |744 /512 bytes |
| NativeAOT |9,816 /656 bytes |1,264 /640 bytes |

First and second calls remain separate because cold identity/reflection initialization adds a fixed cost. JIT/compiler/code-generation allocations are not being counted as product DTO/storage work. Logs and source are preserved beside the probe. No aggregate helper-table cap follows from these observations.

## Required resolution boundary

Before creating selected private identity strings, the internal proof lookup must have a conservative admitted bound for that storage, or use a lookup that does not create those expanded identities. The correction must preserve the existing public API and ordinary DTO semantics; it need not impose a general public DTO restriction or cap unrelated roots. Retained selected identity storage must remain included when the full4MiB grant is narrowed to the derived exporter grant. The concrete accepted graph above must either be rejected before over-budget identity creation or use an allocation-safe lookup, and the ordinary private/base/closed-generic JIT/NativeAOT witnesses must continue to work.

No other remaining managed-layout/native-annotation correctness blocker was found in the reviewed correction at this point. The original input-inline-width finding remains open only until the complete correction, this addendum, and final immutable product/package receipts are accepted together.
