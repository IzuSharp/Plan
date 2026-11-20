# Perf-01 actual before and ON gRPC functional results

**Both original B18 functional stages passed.** The [curated proof](proof.json)
records actual source/native identities, owners, command counts and runtime
observations. Its cutoff is 2026-11-20 22:04:20.635963 UTC. OFF is not accepted by
this checkpoint; ON remains a candidate rather than the selected final version.

| Role | Actual interval, 2026-11-20 UTC | JIT assertions / retirements | AOT assertions / retirements |
| --- | --- | ---: | ---: |
| Before | 20:48:17.976302–21:02:12.540968 | 308 / 334 | 309 / 333 |
| ON candidate | 21:50:58.243637–22:04:20.635963 | 948 / 578 | 949 / 581 |

Each role completed 11 native-component commands, 18 assembled B18 commands and
25 ordinary-package commands. All returned zero. Both outer child owners retired
without signals or remaining children. Each role checked 48 ABI exports, 8
records, 103 offsets, 71 exact compiled API declarations and 5 negative consumers.
JIT reported dynamic code support; actual Native AOT reported it disabled.

The package proof exercised four RPC cardinalities over HTTP/2 with TLS, binary
metadata/status trailers, and whole-call deadlines after headers. Two static
protobuf services consumed five component packages. Ordinary protobuf/DTO/Handler
edits changed the JIT/AOT executables while preserving the selected native hash;
no Rust-tool trap fired. These are component package checks, separate from public
domain-package release or final application performance acceptance.

Native-component binaries and assembled product Server assets have distinct
hashes and are recorded separately. JIT/AOT completion hashes identify the packaged
asset before/after real calls, matched by the original verifier; this record does
not add an independent mapped-module observation. Assertion/retirement counts are
functional observations from each version's tests, not comparative throughput.
Optional Rust allocation-source revalidation was not performed by these runs.

**Formal performance credit remains zero; all ten fresh 30-minute segments are
outstanding.** This curation ran no new tests or loads and makes no allocation,
capacity, final-selection or public-release claim. Internal paths, commands and
full source/binary inventories are omitted.
