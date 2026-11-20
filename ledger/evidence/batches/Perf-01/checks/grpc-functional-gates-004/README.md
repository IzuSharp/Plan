# Perf-01 corrected Server/gRPC functional gates

**The functional prerequisites for scratch diagnostic 004 passed.** The owned
build and verification batch ran from **2026-11-20 12:19:11.227549 UTC to
12:44:33.428564 UTC**. All **31 commands exited zero**; every owned process group
and adopted descendant retired, without cleanup signals or cleanup errors.
This record grants no performance, capacity, long-test or scratch-retention
credit. At this completion point, the separately frozen six-process noise and
eighteen-process comparison had not run.

## Actual verification

| Gate | JIT / Native AOT result | API and consumer result | Scope |
| --- | --- | --- | --- |
| B17 Server.Native prerequisite | 105 checks and 43 dispatches in each mode | Four original cleartext/TLS transport checks and the new HTTP/1.1 + HTTP/2 TLS retirement fixture | Six owned commands completed earlier, 12:07:20.425721–12:08:16.445972 UTC; actual source and native bytes are retained |
| Control B18 gRPC | 948 / 949 assertions; 581 / 580 managed retirements | 71 exact declarations, five negative fixtures, ordinary package JIT/AOT and edited JIT/AOT | Full supplied-native assembled verifier |
| Candidate B18 gRPC | 948 / 949 assertions; 580 / 581 managed retirements | Same API and ordinary package checks | Full supplied-native assembled verifier |
| Candidate B15 Server.Application | 85 / 85 assertions | 278 public symbols; ordinary package, Fluent application and DTO-edit checks | Full supplied-native verifier |
| Candidate B19 MCP | 291 / 291 assertions | 65 exact symbols, five static consumers, ordinary and external private-edit JIT/AOT package proofs | Original managed/API/package subset; no replay claim for its native-producing verifier |
| Candidate B20 diagnostics | 110 / 110 assertions | Ten public context declarations, XML/consumer gate, Debug defaults and samples, ordinary disabled/local JIT/AOT package proof | Original managed/API/package subset; standalone cost modes were not measured |

B18's extra AOT assertion checks that dynamic code is unavailable. The managed
retirement totals are retained as observed functional counters; their one-count
differences do not establish a performance result.

The separate native component prerequisite remains attributed to source
`1207b8d3b0c273752a28dabdf3e7a2b54c933571`: eleven commands passed, with twelve
gRPC leaf tests and seven host tests in each Debug/Release configuration, and
48 Server exports. Its unchanged source inputs and original receipt were
checked rather than rerunning those tests. Its retained native SHA-256 is
`0542a7766a79091c6ea2d51daad74c257fcc7e9f902619bf4eebcc129b6a2e5b`;
this is a different whole-Server composition from the assembled B24 asset.

## Tested producers and isolation

| Role | Actual clean source commit | Tree |
| --- | --- | --- |
| Corrected control | `db95a9fbdd18c208ba8fa3fdb6dabaa2bcc073c0` | `246de1eb9368efbc62f46ce10c4a8a894d646152` |
| Corrected scratch candidate | `9de3f74444246e356a2b12ab664ef99286309aaf` | `0c763ba3b908dcc289528369231daf1788f87571` |

The public candidate counterpart is
[`12c477f0cdbc01fb026e98ac0e26eb45617424ed`](https://github.com/IzuSharp/NativeWeave/commit/12c477f0cdbc01fb026e98ac0e26eb45617424ed),
with the identical tree. Actual producer commits in receipts and packages are
not relabeled. Both roles contain the same native metadata-credit correction
and managed final-release ordering correction. They differ only in the three
established managed scratch files: `CallContext.cs`, `NativeTransport.cs` and
`Registration.cs` under `src/Protocols.Grpc`.

Each role freshly produced its own native manifest, 17 selected B24 package
archives and frozen Release Native AOT protocol application. The protocol
application resolves six packages. Selected versions are
`0.1.0-perf01.grpc-retirement-control.1` and
`0.1.0-perf01.grpc-retirement-candidate.1`. The unused upgrade feeds are not the
tested selection. [completion.json](completion.json) records the complete
selected package identities and hashes, native asset hashes and actual protocol
application artifacts for both roles.

Both fresh producers, both protocol applications and all assembled functional
gates use the same **8,798,736-byte Server library**, SHA-256
`28d793d64bcea642abcaa58b88c775faa2bd0c20ae15c0ef3b25a540f0c65dc2`.
B17's earlier producer remains separately identified while using these exact
bytes. Ordinary DTO/proto/handler edits reused the selected native library.
Neither this gate nor its package proofs authorize public domain package release.

## Ownership and protocol checks retained

The projection reads the original logs and records exact marker text, line
numbers and log hashes. Both B18 roles and modes pass the persistent HTTP/2
header-credit drain, cross-call writer/copy/queue drain and failure-credit drain
assertions. The original three-second zero-resource gate remains unchanged.
The package proofs cover all four gRPC cardinalities through real HTTP/2 + TLS,
whole-call deadlines, binary metadata/status trailers and ordinary application
edits. gRPC payload compression remains identity-only.

B17 covers the actual managed dispatcher tail and delayed final physical lease,
including a throwing cancellation registration and finite close behavior.
The MCP logs retain the finite managed-cancellation-tail wait, canceled nested
callback scope lifetime and final byte-credit drain. Diagnostic logs retain
both throwing-listener retirement and complete ownership joining. These are
the original shared-module assertions, not reduced replacement fixtures.

## Evidence and preserved failures

The main receipt is `perf01-run/grpc-scratch-ablation-004/build/execution.json`,
SHA-256 `2e93747ff1bee94ea1c690f20ea1af0c23dcfedbe785c03714b5a0e80e643414`.
The actual measurement-input SHA-256 is
`17dda4d7989d04591e0ced28ef71d052553746dbace748e21f37ffd1a56bb3e5`;
the build-binding SHA-256 is
`5168b214e1dae056e6eaffc9834b113bc2fdfd5e818f6bc8cce3ba18170fd5be`.
The independent completion review rehashed 580 unique source/artifact/receipt
files plus all 62 outer-command logs. The marker/projection audit separately
hash-checked 324 inputs. Neither audit executed a workload or replayed a gate.

The earlier [paired cancellation failures](../grpc-cancel-observation-001/README.md),
[spontaneous corrected-control AOT failure](../grpc-corrected-build-failure-001/README.md)
and [deliberately held ticket-tail reproduction](../grpc-ticket-tail-001/README.md)
retain their original results. This successful batch follows the two concrete
ownership fixes; it does not overwrite those failures or convert diagnostics
into acceptance.

The still-earlier failed `002` build and failed B18-only continuation also remain
unchanged. Their original receipts are
`perf01-run/grpc-scratch-ablation-002/build/execution.json`, SHA-256
`0330f65bc8fc97bbba229070abe9e1eeedd1f351fb9d24ecc12e91c6b3e097f8`,
and `perf01-run/grpc-scratch-ablation-002-b18-continuation-001/functional/execution.json`,
SHA-256 `0ec9eb69f0ff9c5f50c90b6918c7fcf465c7da0a5920ff1330ae9f5a348cc627`.

The publication allowlist is exactly `README.md`, `completion.json` and
`manifest.json`. These curated synthetic results remain available while Git
history is retained. Original receipts, logs, package archives and tested inputs
remain in the measurement workspace at the paths and hashes recorded here.
No remote full-raw archive, formal performance result or 30-minute result is
claimed by this checklist.
