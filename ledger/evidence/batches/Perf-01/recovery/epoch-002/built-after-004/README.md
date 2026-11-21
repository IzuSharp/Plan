# Epoch-002 actual selected after-004 build

The selected after-004 producer completed all **eight owned commands** from `2026-11-21T04:29:55.627962+00:00` to `2026-11-21T04:44:34.942956+00:00`. Every command exited zero, retired its owned descendants, left no live owned process or owner child, and sent no cleanup signal. These are build outcomes; this projection grants no functional or performance acceptance.

Product source: `2f40348c3db80a4fbee7a99e721b374a597b16df`; actual product tree: `7f803d4f9e57fef1d8cfdef69c505d67f84614c9`. The unchanged common application/driver source is `2e3995df8d86583ee9443348276ca8d918056bfc`. Both source roles were clean in the actual producer record. The selected B24 version is `0.1.0-perf01.recovery004.after.1`; the separately produced upgrade version is not the measured package selection.

## Actual command interval

| Command | Actual start UTC | Actual end UTC | Seconds | Exit | Retired |
|---|---|---|---:|---:|---|
| native-stable | 2026-11-21T04:29:57.041308+00:00 | 2026-11-21T04:37:42.677908+00:00 | 465.637 | 0 | yes |
| packages | 2026-11-21T04:37:43.985608+00:00 | 2026-11-21T04:39:49.102662+00:00 | 125.117 | 0 | yes |
| reference | 2026-11-21T04:39:50.002150+00:00 | 2026-11-21T04:40:50.952698+00:00 | 60.951 | 0 | yes |
| observer | 2026-11-21T04:40:51.604450+00:00 | 2026-11-21T04:41:18.364582+00:00 | 26.760 | 0 | yes |
| protocols | 2026-11-21T04:41:19.110790+00:00 | 2026-11-21T04:42:42.481936+00:00 | 83.371 | 0 | yes |
| codec | 2026-11-21T04:42:43.159994+00:00 | 2026-11-21T04:43:51.578167+00:00 | 68.418 | 0 | yes |
| shared-retirement | 2026-11-21T04:43:52.275329+00:00 | 2026-11-21T04:44:12.004809+00:00 | 19.729 | 0 | yes |
| shared-page | 2026-11-21T04:44:12.671754+00:00 | 2026-11-21T04:44:33.261974+00:00 | 20.590 | 0 | yes |

## Selected B24 packages

| Package | SHA-256 |
|---|---|
| NativeWeave.Core | `679b6ededd8641ae2a12dc98e726a35edb7ef11df0b728c93afa3c0ecb501592` |
| NativeWeave.Data | `a085458b5395a27f5862e0d8d2b593538a99a48d75a9b289d4870c98a44bb626` |
| NativeWeave.Data.Streaming | `8ae79c7f51b2c8e7cf454fb47c3e7081d0729c44477c2d8b0ee355a63d0913af` |
| NativeWeave.Database | `c273a884af33b1ee2323cea7efe840d022b9bff239f2421464ddfad11194bf1e` |
| NativeWeave.Database.PostgreSql | `e093630c17619eafeee8a087642d3bbdee8c2e40c50f64c55a8bb510d2b1b71a` |
| NativeWeave.Database.PostgreSql.Native | `dfa989b33b76c7b6b38c5806aaf3b91164c62e49d0f85532db4768dcca0c378b` |
| NativeWeave.Database.Sqlite | `31c59edd7257e6a1ed7a3614ec0b91a4f2b6c32e538274fd65c4362ae7893672` |
| NativeWeave.Database.Sqlite.Native | `71cec96751ea378e2a0ee6531273bc22726d780308b14a4024974cb09fd4aace` |
| NativeWeave.Database.Transactions | `c7e503ed2752cd6e68a38fa4d05df8419e9f92e263a9358a4e1213691d6baaa0` |
| NativeWeave.Interop.Abi | `f7fa0eb5dc3e0ee5f705d2c2471dc3b602f606c1bfbc4b5ad27377d255d4c1f9` |
| NativeWeave.Query.Binding | `866210783b5377c09a424bb3879959d42e41ff7d86215fd71bc68fc8d2efe8ce` |
| NativeWeave.Query.Generator | `9eeb2d0d77a978480902b27f1f7df13b7f1901b39dd2a68d7c0009211dea0787` |
| NativeWeave.Server | `199cea53854393f0d39e1ddf7ec3f92e80f8f64922491d5b82f3df746a1b59ba` |
| NativeWeave.Server.Generator | `4360cc41f9a22cf18eaa0cca4c124319078ad4fdd54e3dfd034ba6fd024f94d4` |
| NativeWeave.Server.Grpc | `eb4910cf25f689390fab10f0c19fd374503531ce1e25c79115b55abb8d0ae518` |
| NativeWeave.Server.Mcp | `1ad87edbf88ea1edb8b009e8685b5e8a7685d6f2efb2e7159256764437837814` |
| NativeWeave.Server.Native | `a6fadb636b164ed0c323ec018b41d97cd8a4b93b5bff1ac88cb401db7e254fb1` |

## Stable native producers

| Engine | Library | Bytes | SHA-256 |
|---|---|---:|---|
| database.sqlite | libnw_database_sqlite.so | 6601576 | `63f01de214b727a6b7c976902e7f508f568ac08629a64c0332d67da028295346` |
| server | libnativeweave_server.so | 8815464 | `8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0` |
| database.postgresql | libnw_database_postgresql.so | 7870840 | `9ec17b5fe5fc675b35edef503d3eacf1597aa814879236bf5e97621c70fd3f65` |

SQLite and PostgreSQL native producer hashes equal the corresponding actual before producers. The Server producer differs and binds the selected gRPC metadata cleanup and HTTP Close/Finish retirement repairs. Native byte equality alone is not a performance result. These build identities do not claim runtime loading. The separate A17 codec asset below is not a fourth B24 stable native module.

## Principal consumers and probes

| Role | Artifact | SHA-256 |
|---|---|---|
| reference-aot | NativeWeave.Reference.TaskService | `cc6b30baab15deb3c53eb9504687ff8bc6277d2287da21ae240416028c8b230b` |
| database-observer-aot | NativeWeave.Reference.TaskService | `8257d25a2fa53e0f7d307e6541434b93b498a8c2ff8cc3617b2c9f12fd1d47b9` |
| protocol-server-aot | Perf01.ProtocolServer | `4f2715587cbf3bd7be05bdd4419fc2be73fe7dfc20fba8a66186b5a2753397f9` |
| protocol-client-aot | Perf01.ProtocolClient | `cc3b8ad126c6de142d7d7d1d82ab61901c5255364f87fd9360be094e748e0bd6` |
| shared-retirement-aot | NativeWeave.Data.NativeHost.Tests | `7804b2281dbb49fb8ee4a571fd274a8057ea6e0ca05e507e90d4135d461e412f` |
| shared-page-aot | NativeWeave.Perf01.PageProbe | `b66986e89af508906a27f232089ed1ccd44b7d47e156ca894fd3226619cf90ee` |
| codec-aot | NativeWeave.Engines.SyncProof.Tests | `4d8f5a2a4af8d68b781702639be36e886a6528432b26a8017aa85a58a3868075` |
| codec-direct-rust | perf01-codec-direct | `31ba63f8a65c6d3a056da4a334b94a9550f585defc84bb560f5c7785f350c212` |
| codec-native-a17 | libnativeweave_engine_syncproof.so | `225891ba2e8ab97381bfb7b35814aea00a16135da01b9afcd6de8e97a58a6d15` |

The after client was built, but the unchanged comparison caller selects the **before-produced common client**, SHA-256 `ae59038f6d83b0cdc60677f5d65f50f06298b53a168bee65f73a6599d7832f8e`, for every measured role including direct Rust. The after client SHA-256 is `cc3b8ad126c6de142d7d7d1d82ab61901c5255364f87fd9360be094e748e0bd6`; byte equality is `false`. This build projection does not assert that either client has executed a performance measurement.

The separately produced A17 proof packages are:

| Package archive | Bytes | SHA-256 |
|---|---:|---|
| NativeWeave.Core.0.1.0-proof.1.nupkg | 57917 | `132622fe3c4befe8d1a231c2e41328f1fdc2670771a3174cf2a496fd1d183bbf` |
| NativeWeave.Engines.SyncProof.0.1.0-proof.1.nupkg | 234972 | `d002a4fa5a4a301f2436299b3242cd00975c61c63de21d2c522357002c0e7135` |

## Actual external-package pairing

The after-only producer performed the original external-package equality rule before marking its execution completed. The result is stored in the `pairing` field of execution SHA-256 `1eaf0d0a11a533a48be024c07ede85fa29fbc8799ba35c5848469138d1bdf76d`. **No separate pair stage or pair binding receipt was produced.** The comparison uses actual before binding `17e8844b8968bda78c6ce1846a664e55a2c00e368dea08f21eb6796afb5407af` and after binding `106c531683c46cce5090359583e96a424f651507f758bbd03a463766190f8bef`.

The equality fields are archive SHA-256, raw archive SHA-512, NuGet content hash, signature-entry presence and source. This curation independently rechecked **45 consumer/package entries across eight consumers**, containing **12 distinct external package/version identifiers**. The same package may occur in several consumers; this is not a count of 45 unique archives.

| Consumer | Equal external package entries |
|---|---:|
| baseline-aot | 7 |
| baseline-jit | 5 |
| codec | 3 |
| observer | 7 |
| protocol-client | 8 |
| protocol-server | 9 |
| shared-page | 3 |
| shared-retirement | 3 |

## Evidence scope

[projection.json](projection.json) contains the exact selected package/native/principal identities, eight producer manifest hashes and eight command receipt hashes. Build execution SHA-256: `1eaf0d0a11a533a48be024c07ede85fa29fbc8799ba35c5848469138d1bdf76d`. Actual binding SHA-256: `106c531683c46cce5090359583e96a424f651507f758bbd03a463766190f8bef`.

This curation rehashed **61 selected manifest-bound files / 244801843 bytes**, the eight producer manifests, all eight owner receipts and their 16 output logs. The selected files comprise project packages, principal AOT publishes and their bound siblings, the built protocol client, Shared and codec outputs, and stable natives. It did not rehash the full private build file map. No new archive creation, upload or remote readback is claimed by this projection.

The public projection omits operational file maps, absolute workspace paths, process identifiers, command environments and TLS material. Private immutable admission and producer records remain the detailed reproducibility inputs.

This record asserts no B18 result, other module regression result, Shared profile execution, benchmark gain, capacity or long-test acceptance. Those require their own actual receipts. This curation launched no build, profile or workload. Performance credit is **0 seconds** and accepted 30-minute groups are **0**; no historical measurement or long-test credit is transferred.
