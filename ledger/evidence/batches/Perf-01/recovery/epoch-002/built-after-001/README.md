# Epoch-002 actual selected after build

The selected after producer completed all **eight owned commands** from `2026-11-21T02:28:22.686724+00:00` to `2026-11-21T02:43:32.641508+00:00`. Every command exited zero, retired its owned descendants, left no live owned process or owner child, and sent no cleanup signal. These are build outcomes, not functional or performance acceptance.

Product source: `ccff42c0df4141984ef9de497af7cd768753704a`; actual product tree: `aa7b4d25886e64e71dbf57c75f9592af7b46d37a`. The unchanged common application/driver source is `2e3995df8d86583ee9443348276ca8d918056bfc`. Both source roles were clean in the actual producer records. The selected B24 version is `0.1.0-perf01.recovery002.after.1`; the separately produced upgrade version is not the measured package selection.

## Actual command interval

| Command | Actual start UTC | Actual end UTC | Seconds | Exit | Retired |
|---|---|---|---:|---:|---|
| native-stable | 2026-11-21T02:28:24.211586+00:00 | 2026-11-21T02:36:51.626926+00:00 | 507.415 | 0 | yes |
| packages | 2026-11-21T02:36:51.869406+00:00 | 2026-11-21T02:39:07.114215+00:00 | 135.245 | 0 | yes |
| reference | 2026-11-21T02:39:07.217492+00:00 | 2026-11-21T02:39:59.268818+00:00 | 52.051 | 0 | yes |
| observer | 2026-11-21T02:39:59.330853+00:00 | 2026-11-21T02:40:24.938029+00:00 | 25.607 | 0 | yes |
| protocols | 2026-11-21T02:40:25.005222+00:00 | 2026-11-21T02:41:39.954201+00:00 | 74.949 | 0 | yes |
| codec | 2026-11-21T02:41:40.020486+00:00 | 2026-11-21T02:42:48.427462+00:00 | 68.407 | 0 | yes |
| shared-retirement | 2026-11-21T02:42:48.500309+00:00 | 2026-11-21T02:43:10.032426+00:00 | 21.532 | 0 | yes |
| shared-page | 2026-11-21T02:43:10.095279+00:00 | 2026-11-21T02:43:31.458435+00:00 | 21.363 | 0 | yes |

## Selected B24 packages

| Package | SHA-256 |
|---|---|
| NativeWeave.Core | `5e06ab926054c99163ba002b328ff59c7c29fdd4e2e921b752c5ac518d919cbf` |
| NativeWeave.Data | `1adf108fed31eb778c1e1a2689b2ec02473e627d9fb7d3989faf79d50797f102` |
| NativeWeave.Data.Streaming | `3b66cc618165498eaf836531b279cf2b0b543e01b53ad3ab4b5ca634579472dd` |
| NativeWeave.Database | `bf5e288d9fc0ab6f9b039e4dfa167818a6190b40a4432d68b2200c115c1fd2bc` |
| NativeWeave.Database.PostgreSql | `542d2df376407e5d59dbb51106a9203a786401dc9c21d75de3b833199c432f82` |
| NativeWeave.Database.PostgreSql.Native | `9036a8ea9b621de471db9331f50021b6d4b4c10ded6f74f3f6d0221ba29ec905` |
| NativeWeave.Database.Sqlite | `c99b79e2bdb0b3d092bab28c187cfaeb6e16f4d2fa03a9c709288c9675d963cc` |
| NativeWeave.Database.Sqlite.Native | `7fc717e4e9009e77c3e0697023b4478782958d6a7e21688808d0262c1a4a4a85` |
| NativeWeave.Database.Transactions | `9632166e2152be44092026e794d02519bd950cd9fe3c427a9808439fa430cb83` |
| NativeWeave.Interop.Abi | `b37c3553425294893c6ae04a175652625611e085dcf2a11e647c942a8fe0fc75` |
| NativeWeave.Query.Binding | `30ea6d02e60d5f49ecc491b02786a1fe0f182e6764dc13fe95515b54d9e32330` |
| NativeWeave.Query.Generator | `0e263566508fa80b4ddd65ebdfcb8f3df9663e6bae0f658cf8e5fba339929f04` |
| NativeWeave.Server | `acaecc5fbdb23d75e37d2cb55f27404967b352918dff86cd243ffc2f29f9329e` |
| NativeWeave.Server.Generator | `596965b7538272bf562a4ec9a34e5b34915d1d315b3feeb79ce4bcee387daad9` |
| NativeWeave.Server.Grpc | `1daca01a782d67aed478f51115336402321cc05ea0d8ba7936097de95abc9ad0` |
| NativeWeave.Server.Mcp | `07988897b654d0057dbf832c74aed260be7f7d10192a3688d5bd6a9f595fe9f0` |
| NativeWeave.Server.Native | `a3dba36420193caf3399827016172cdfe65ed80b10969843b1bffd3dc1ef03f4` |

## Stable native producers

| Engine | Library | SHA-256 |
|---|---|---|
| database.sqlite | libnw_database_sqlite.so | `63f01de214b727a6b7c976902e7f508f568ac08629a64c0332d67da028295346` |
| server | libnativeweave_server.so | `1f023b7506bde3f8c4a13b12de92e3e9503004ca3afc2d41a53bec17e44f1d97` |
| database.postgresql | libnw_database_postgresql.so | `9ec17b5fe5fc675b35edef503d3eacf1597aa814879236bf5e97621c70fd3f65` |

SQLite and PostgreSQL native producer hashes equal the corresponding actual before producers. The Server producer has the selected retirement repair. Native byte equality alone is not a performance result, and these build hashes do not claim runtime loading. The separate A17 codec native asset below is not a fourth B24 stable native module.

## Principal consumers and probes

| Role | Artifact | SHA-256 |
|---|---|---|
| reference-aot | NativeWeave.Reference.TaskService | `561ac52eb4d07b97ec35f2cf7b82523130164fd96eb64da87efc9db2b5a64359` |
| database-observer-aot | NativeWeave.Reference.TaskService | `dffa3b067c84fb92eca25b28426037859b8066120338fb382df2e0e9f137b0d5` |
| protocol-server-aot | Perf01.ProtocolServer | `70850429f6bfb147513df4c082048d18d8a33b55e18037d57fa58829a8b379de` |
| protocol-client-aot | Perf01.ProtocolClient | `5c0ae657556f194569815d7f3cf616681108850523c664b8f51263182a625165` |
| shared-retirement-aot | NativeWeave.Data.NativeHost.Tests | `298827db4078d37c67fc0fb030be7a01c1bb41710b780b6187c55a10f3d2c0c1` |
| shared-page-aot | NativeWeave.Perf01.PageProbe | `3aab355e5d8f78280854c4554cc9be6018fab53ef06468df3c18d8a3621970a0` |
| codec-aot | NativeWeave.Engines.SyncProof.Tests | `417b47de1ab7c4b75ef151422ec3bd97724648a124f17c797828e02b0e3b5196` |
| codec-direct-rust | perf01-codec-direct | `31ba63f8a65c6d3a056da4a334b94a9550f585defc84bb560f5c7785f350c212` |
| codec-native-a17 | libnativeweave_engine_syncproof.so | `225891ba2e8ab97381bfb7b35814aea00a16135da01b9afcd6de8e97a58a6d15` |

The after client exists as an actual produced artifact, but the protocol comparison continues to select the **before-produced common client**, SHA-256 `ae59038f6d83b0cdc60677f5d65f50f06298b53a168bee65f73a6599d7832f8e`, for every role including direct Rust. The after client hash is `5c0ae657556f194569815d7f3cf616681108850523c664b8f51263182a625165`; byte equality is `false`. Its existence does not change the selected load generator.

## Actual external-package pair binding

The actual pair stage completed from `2026-11-21T02:44:01.382429+00:00` to `2026-11-21T02:44:03.531613+00:00`. Its execution SHA-256 is `84b8c257f8d755007e0c285bcacb7eb1cd84e50e858c5000afda69152a9d6201` and binding SHA-256 is `410656c611bba99a7c1c71aa622594f2dd8020173ee4a1cf9f67699e3e74a659`. The original equality rule checks archive SHA-256, raw archive SHA-512, NuGet content hash, signature-entry presence and source.

The independently rechecked total is **45 consumer/package entries across eight consumers**, containing **12 distinct external package/version identifiers**. The same external package occurs in several consumers; this is not a count of 45 unique archives.

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

[projection.json](projection.json) contains the exact selected package/native/principal identities, eight producer manifest hashes and actual receipt hashes. Its build execution identity is `a4abd107860ed9ca34edc71b45341cd3a68849e541ebaf25e6d5b44c7f77bc7a` and actual binding identity is `a8aecb795307d49ea7d17fcc1440a57cde03304caac458c96164909803040597`.

A separate local explicit backup allowlist selects **61 manifest-bound files / 244797463 bytes**, derived from the actual after manifests. It includes selected project packages, principal AOT publishes, the built client, Shared and codec outputs, and stable natives. It excludes unselected upgrade packages, JIT outputs, whole caches, build intermediates, control maps, environment and TLS material. It does not replace the original private admission/producer receipts.

This projection asserts no B18 result, B17/B19 subset result, Shared profile execution, benchmark gain, capacity or long-test acceptance. Those require their separate actual receipts. This curation launched no build, profile or workload. No historical measurement or long-test credit is transferred.


## Separate local backup

The explicit selection was archived and verified on CPU4 from `2026-11-21T02:51:34.115151+00:00` to `2026-11-21T02:51:44.220063+00:00`. `NativeWeave-Perf-01-epoch002-after-principal-001.tar.gz` contains 61 original selected files plus one sanitized identity manifest, totaling 62 members; its compressed size is 99628904 bytes and SHA-256 is `9492ec7f2e3c3b0a78f4cd0b190620f76e24765687c4002c601b0a698c3c595e`. Every decompressed member hash and normalized archive metadata was checked; all originals remained unchanged. The identity manifest SHA-256 is `804cc0189495cf26577a0f40786178f904f399b063ac8c007edc2358b961d991`. No upload or remote-readback completion is claimed here. This archive remains separate from the earlier before/common backups.

## Subsequent durable readback

After this immutable build projection and archive were produced, root saved and retrieved the exact archive at `2026-11-21T02:54:39.406245+00:00`. Its outer SHA-256 and all 61 payload member hashes matched; the embedded identity is the 62nd member. The separate [actual readback receipt](archive-readback.json) preserves the filename, size, identities and counts. The user-owned durable file remains until its owner removes it; no automatic expiry was provided. Private provider IDs remain local. This later retrieval changes no build, functional or performance acceptance.
