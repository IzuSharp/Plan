# Epoch-002 actual common build

The common producer completed all **three owned commands** from `2026-11-21T02:07:00.763461+00:00` to `2026-11-21T02:14:36.133935+00:00`. All exited zero and retired. This projection grants **no B18 functional or performance acceptance and no long-duration credit**.

Common source is `2e3995df8d86583ee9443348276ca8d918056bfc`. The before prerequisite is the actual EA5 producer `ea5fa528035d025bd7a28698ee7c71194432236c`, execution SHA-256 `892ed498e7dabbaaf1e3398add1d5367ebdb28255378dd793a9cc874d6def224`. The HTTP/gRPC client is the exact before Native AOT artifact; the fixed codec corpus was produced by the exact before direct codec executable. Neither was silently rebuilt.

Common execution SHA-256: `bfdd94a1cfcc00f85585864b083b45b0195bfe2157c129b885b73d9e51531581`. Binding SHA-256: `8aed47dda4223bc3812705a68c663a8c9d80fc1ba02455bab6d1363a3762dac8`. The adjacent path-free JSON records complete source, freeze/toolchain/build-input, producer and corpus identities.

## Actual owned producer intervals

| Producer | Start UTC | End UTC | Owned seconds | Exit | Retired |
|---|---|---|---:|---:|---|
| direct-protocols | 2026-11-21T02:07:01.230738+00:00 | 2026-11-21T02:08:30.380213+00:00 | 89.150 | 0 | yes |
| database-comparators | 2026-11-21T02:08:30.443189+00:00 | 2026-11-21T02:14:32.977093+00:00 | 362.534 | 0 | yes |
| codec-corpus | 2026-11-21T02:14:33.130030+00:00 | 2026-11-21T02:14:35.093685+00:00 | 1.964 | 0 | yes |

## Principal common binaries

| Role | Artifact | SHA-256 |
|---|---|---|
| direct-protocol-server | perf01-direct-protocols | `5953ed7a9823c33965892ac6c9acb2c2712a29f8924c960e9e8d791de3fb020b` |
| database-direct-rust | nativeweave-b23-direct-rust | `8b7e1a1e1c4d9fe85a15dbd95af00a712a29db576beb5cfa923f4c434fe89df9` |
| database-managed-aot | NativeWeave.Benchmarks.ManagedComparator | `76e5a9b488f5c527e99348ee92fea08ef625471c09099bb33f2fcf2e37a8a0d5` |
| database-managed-aot-runtime-library | libsqlite3.so | `2b99b38b699d3834c39b1e38d089dade94f64f8beac82d2461217d81a251b654` |

## Reused before identities

| Role | Artifact | SHA-256 |
|---|---|---|
| common-before-client-aot | Perf01.ProtocolClient | `ae59038f6d83b0cdc60677f5d65f50f06298b53a168bee65f73a6599d7832f8e` |
| common-before-client-debug | Perf01.ProtocolClient.dbg | `5578ae5f0a58d855335c83dace59526c3098c84ebe9744fb052993f4a6878cc1` |
| codec-corpus-before-direct-producer | perf01-codec-direct | `31ba63f8a65c6d3a056da4a334b94a9550f585defc84bb560f5c7785f350c212` |

## Fixed codec corpus

The corpus contains eight cases: four raw sizes, each with compressible and fixed-seed pseudo-random data. Actual settings are `zlib`, level `6`, checksum `Adler32`, seed `2654435769`, raw/decoded limit `4194304` / `4194304` bytes and encoded limit `4259840` bytes. These are producer inputs and content identities, not measured codec throughput.

| Case | Entropy | Raw bytes | Encoded bytes | Raw SHA-256 | Encoded SHA-256 |
|---:|---|---:|---:|---|---|
| 0 | compressible | 256 | 109 | `2e60042cdf59c48d4baa216bf3f0e182a95327e2c767df3a9e22a21b7e5d25b3` | `0e373ab64ec5da6f803e1e38cfa0351e655ddb8366913e395936da22b58e87af` |
| 1 | pseudorandom | 256 | 267 | `23ccd8a1ef04ae9b87d4744c822811455703479fe5b411fb061bf084ee962be2` | `9e4910f98b7b62bf4afd1b96f3ca10ec94b63f024818277fb6e35e36c42cb52b` |
| 2 | compressible | 4096 | 126 | `cdc2e5a22e0c4d17f97308c26901092f8154918bd76d06845868cab485b763d7` | `0c370d56439d5b2bd98ad2e707f0ab24589e6c51d017231580b1e5d892961956` |
| 3 | pseudorandom | 4096 | 4107 | `6b1d4bfe25f0144686cade6a6f77f222e6ef929b949a9d688e418d56dd3af609` | `3019500cadf39e89f8d47127cfa10bf340739b254bab81c553e0836d0a9fe7c5` |
| 4 | compressible | 1048576 | 3165 | `258689793f24c14b833519d0c345ebeee0477012ff4a9af3c203f9a8e52b1e84` | `0696eb420594ed102ead4cfd052a8db54f72642f2f7c9e384378e8a3d88f3bf8` |
| 5 | pseudorandom | 1048576 | 1048752 | `b13261ceffb27a120f88c3466a3917bfb2875493d5f802422b433a3599407be6` | `2c0b6147a5c48d6a20d282c415fa84bd190478a94becf4c910932539877f7c59` |
| 6 | compressible | 4194304 | 12311 | `0b71dab93937754514abf84da30e0a0181394ab140dd578e9d1d5308f444b57d` | `e2ebf4564ebbf277894ef780c42cee6dd067afbfc382c7e21018f6d96c035fef` |
| 7 | pseudorandom | 4194304 | 4194975 | `80dd235b29724a85fcee99b55b90a9f32a7e94165dcdb361ad4f1af74ea267f4` | `4ed3b94d8bb79c73428ebd0a8e620faaed42cfa03b4bdbb3203ac5fa152bf221` |

The local-only backup allowlist contains 21 manifest-bound common files (50783519 bytes): four binaries/libraries, sixteen corpus payloads and the path-free corpus manifest. Its three explicit before-file prerequisites already belong to the before backup selection. It excludes control maps, operational/environment files, TLS material, complete caches and intermediates. No archive or upload was performed.

The original comparator producer receipts report successful build/golden commands and `executed_performance: false`. Source or build readiness does not establish service capacity, application runtime loading, comparative benefit or effective load duration. No extra build, test, import, profile or load was launched while curating this snapshot.
