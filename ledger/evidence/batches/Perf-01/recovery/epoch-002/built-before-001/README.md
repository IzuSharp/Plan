# Epoch-002 actual before build

The second fresh before producer completed all **eight owned commands** from `2026-11-21T01:52:44.559771+00:00` to `2026-11-21T02:06:40.950262+00:00`. Every command exited zero and retired its owned tree. This is build evidence; it grants **no B18 functional or performance acceptance and no long-duration credit**.

Runtime source is `ea5fa528035d025bd7a28698ee7c71194432236c`; the common C# application/measurement source is `2e3995df8d86583ee9443348276ca8d918056bfc`. The selected B24 version is `0.1.0-perf01.recovery002.before.1`. Seventeen selected package archives, the three stable native assets and the principal publish outputs were rehashed against their actual producer manifests and completed role binding.

Original execution SHA-256: `892ed498e7dabbaaf1e3398add1d5367ebdb28255378dd793a9cc874d6def224`. Binding SHA-256: `17e8844b8968bda78c6ce1846a664e55a2c00e368dea08f21eb6796afb5407af`. The adjacent path-free JSON preserves exact source trees, freeze/toolchain/build-input identities, complete artifact hashes and producer receipt hashes.

## Actual owned producer intervals

| Producer | Start UTC | End UTC | Owned seconds | Exit | Retired |
|---|---|---|---:|---:|---|
| native-stable | 2026-11-21T01:52:44.726869+00:00 | 2026-11-21T02:00:19.693817+00:00 | 454.967 | 0 | yes |
| packages | 2026-11-21T02:00:20.051921+00:00 | 2026-11-21T02:02:23.556776+00:00 | 123.505 | 0 | yes |
| reference | 2026-11-21T02:02:23.621329+00:00 | 2026-11-21T02:03:12.469779+00:00 | 48.848 | 0 | yes |
| observer | 2026-11-21T02:03:12.536555+00:00 | 2026-11-21T02:03:38.193456+00:00 | 25.657 | 0 | yes |
| protocols | 2026-11-21T02:03:38.259014+00:00 | 2026-11-21T02:04:47.281821+00:00 | 69.023 | 0 | yes |
| codec | 2026-11-21T02:04:47.351622+00:00 | 2026-11-21T02:05:55.645912+00:00 | 68.294 | 0 | yes |
| shared-retirement | 2026-11-21T02:05:55.713636+00:00 | 2026-11-21T02:06:16.751926+00:00 | 21.038 | 0 | yes |
| shared-page | 2026-11-21T02:06:16.830907+00:00 | 2026-11-21T02:06:39.931565+00:00 | 23.101 | 0 | yes |

## Selected B24 package archives

| Package | SHA-256 |
|---|---|
| NativeWeave.Core | `cf6018e24b7fbef960ef50186badb0635c99b5dff87c38e70f91578dad578d58` |
| NativeWeave.Data | `bac03671a45b4b40a05de286f02ddab77186ad4a27ac044b803fe111acc0fb28` |
| NativeWeave.Data.Streaming | `76e33c65ebb2cc0bef13e078305b0fccb906320a1f082962b2d3c36957e9c5b8` |
| NativeWeave.Database | `bee388e02b10909a195706a20a97847be4f18d5d8599c181df794bd9edfdf9bd` |
| NativeWeave.Database.PostgreSql | `b2c3fb9409ae330c390568c646937866e0be982799eb75b815c7404ed9c0610b` |
| NativeWeave.Database.PostgreSql.Native | `5e234ca6acde19232537077b025e442b984152e170e6cb0c6f4b68a485e092da` |
| NativeWeave.Database.Sqlite | `9bace69c3cbb25ea361157bfcb7b8ae6aa7225fd30c8756a51766b904842b5fc` |
| NativeWeave.Database.Sqlite.Native | `9f87d16c03a35f3c0abf849ff1dab500dbd83335cb698b2308755cc8f52d0ec0` |
| NativeWeave.Database.Transactions | `46ac6c0f97ab9b2bf98721518d8eb4d3246c18f1a48a4c73abf1b7cdab3190b1` |
| NativeWeave.Interop.Abi | `cce94dec717594b845084962dec46ca006c89745a7d34413a22d73d736440c6c` |
| NativeWeave.Query.Binding | `59b9041bd5ac4923dc8c3528fe479975149312d6d67de7dbaa8851e339030529` |
| NativeWeave.Query.Generator | `b8e9c07563389f437689766bcdd542fe479a2f0f27ca0f9286c18c5065f2b658` |
| NativeWeave.Server | `3a8218f89907801105c62f5e017177e9ef492b1054cc1dc6dbf5f6b32ef08caf` |
| NativeWeave.Server.Generator | `2cf590ed71a77bb7671dac698cac22628614189967fef7f36e915e55649d9373` |
| NativeWeave.Server.Grpc | `19b13c1d7e0d80d502200063e2c8f8e9187e2fa78d4f69b65d7ca2ce2f0f55c4` |
| NativeWeave.Server.Mcp | `ea44dc08f6039baf9db3d8e53281460862f4ad92816969a6a5d52d93a10e7cf7` |
| NativeWeave.Server.Native | `c86b3ca6c257560460cbae235669a4115b115546805e4988b75103ba9652532f` |

## Stable native assets

| Engine | Library | SHA-256 |
|---|---|---|
| database.sqlite | libnw_database_sqlite.so | `63f01de214b727a6b7c976902e7f508f568ac08629a64c0332d67da028295346` |
| server | libnativeweave_server.so | `63c4950fceab5fe52017b5457b04759201de5a261d8087939cb177a20a5b88e2` |
| database.postgresql | libnw_database_postgresql.so | `9ec17b5fe5fc675b35edef503d3eacf1597aa814879236bf5e97621c70fd3f65` |

## Principal consumers and probes

| Role | Artifact | SHA-256 |
|---|---|---|
| reference-aot | NativeWeave.Reference.TaskService | `5107b6e38d8430b6094d3de7ba93f89ee99937e66cd8ceeefa4659eef95e9be2` |
| database-observer-aot | NativeWeave.Reference.TaskService | `f8378f49b9f8f194969fc01ebfa942a4ce505082efb91a2865a1d54d1b2c6752` |
| protocol-server-aot | Perf01.ProtocolServer | `0ac4867e2cfd626bdfcd453801c8b2646d9e4c20f1191c496fb5837252cf9462` |
| protocol-client-aot | Perf01.ProtocolClient | `ae59038f6d83b0cdc60677f5d65f50f06298b53a168bee65f73a6599d7832f8e` |
| shared-retirement-aot | NativeWeave.Data.NativeHost.Tests | `1bed4dd2422be876dfd7008e83ddf0a2d031a78753ee032fd8f16ad0f05c1f4a` |
| shared-page-aot | NativeWeave.Perf01.PageProbe | `b93b2c0a0b35bcbd8b8a3d124c14779731ca585960d01cbb1fc17534ab3344e4` |
| codec-aot | NativeWeave.Engines.SyncProof.Tests | `a0742d8e6a2c6d2bb3c918b637f90021541d728027a2817db77d3db9eff4dee0` |
| codec-direct-rust | perf01-codec-direct | `31ba63f8a65c6d3a056da4a334b94a9550f585defc84bb560f5c7785f350c212` |
| codec-native-a17 | libnativeweave_engine_syncproof.so | `225891ba2e8ab97381bfb7b35814aea00a16135da01b9afcd6de8e97a58a6d15` |

The A17 codec native module and its two proof packages are separately identified; they are not a fourth B24 stable native asset. The codec direct executable was produced inside the completed before codec command. No completion of the separate common producer stage is inferred.

A local-only, explicit backup allowlist selects 61 manifest-bound files (244651047 bytes): selected project packages, principal publish outputs and stable native assets. It excludes complete caches, build intermediates, control maps, environment files and TLS keys. The allowlist has not created an archive or uploaded any bytes. It is not a replacement for the original private admission/producer receipts.

No runtime load, profile or performance test was launched while preparing this projection. Actual loaded native identity must still be proven by the eventual functional and measurement receipts.
