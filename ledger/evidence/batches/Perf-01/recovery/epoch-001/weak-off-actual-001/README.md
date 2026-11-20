# Perf-01 actual weak-OFF build and gRPC functionality

**The experimental OFF candidate built successfully and passed its assembled B18
functional check. It remains unselected.** The [build identities](build.json)
and [functional proof](functional.json) record actual results for public product
commit `4ae2e15f4825a9b5237734444ff68b0b6d2c5aa4`. The common application/driver
source remains `2e3995df8d86583ee9443348276ca8d918056bfc`.

| Actual stage | Interval, 2026-11-20 UTC | Result |
| --- | --- | --- |
| Full fresh OFF build | 22:04:36.163531–22:19:57.711494 | Eight producers completed and retired, exit 0 |
| Assembled OFF B18 | 22:24:14.822968–22:27:54.318002 | Completed and retired, exit 0 |

All owned commands retired without signals or remaining children. The build
checklist includes exactly 17 selected `.off.1` domain package archives, native
producer assets, A17 codec and principal AOT consumer identities. SQLite,
PostgreSQL and Server native bytes match ON, but each OFF producer actually ran.
The prepared ON/OFF/direct comparison uses the same before-produced client.

OFF reuses the actual completed ON native-component proof after the original
verifier checks applicable gRPC source equality. Those 11 component commands are
reused evidence, not 11 newly executed OFF commands. Its separate component-native
hash is not substituted for the assembled product Server hash.

The new OFF check completed 18 assembled B18 commands and 25 ordinary-package
commands. JIT recorded 948 assertions / 579 managed retirements; Native AOT
recorded 949 / 577 and no dynamic code support. It verified 48 ABI exports, 8
records, 103 offsets, 71 compiled API declarations and 5 negative consumers.
The package proof covers four RPC cardinalities over HTTP/2 + TLS, metadata/status
trailers, whole-call deadlines, and ordinary protobuf/DTO/Handler edits with the
same native asset and no Rust-tool trap. Runtime native identity uses the original
asset-hash completion proof; no independent mapped-module observation is claimed.

**No performance decision or final selection follows from these passes.** Formal
performance credit is zero, and all ten fresh 30-minute groups remain outstanding.
The curated files omit private paths, commands and full inventories. Public domain
package release remains separate. This curation executed no tests or workloads.
