# Perf-01 — CI 128 retained-artifact audit

The seven jobs in [NativeWeave CI 128](https://github.com/IzuSharp/NativeWeave/actions/runs/44852311109) completed successfully. This audit downloaded all three retained artifacts, checked their actual bytes against the GitHub sizes and SHA-256 digests, and read the recorded results. It did not run a build, test, profile, or workload. Detailed numerical observations and receipt hashes are in [audit.json](audit.json).

## Source identity

The queried product head is `ccff42c0df4141984ef9de497af7cd768753704a`. The actual CI checkout recorded by the package manifest, A20, Task04, and Task07 is `8e99af18004909e3080551fb4a99998b393eb2ba`. Its [commit metadata](https://github.com/IzuSharp/NativeWeave/commit/8e99af18004909e3080551fb4a99998b393eb2ba) identifies the merge of that head into `ea5fa528035d025bd7a28698ee7c71194432236c`.

The exact-candidate manifest lists 1,496 tracked source paths. Their complete path set and every file-content SHA-256 match the local Git objects at the queried head. The head Git tree is `aa7b4d25886e64e71dbf57c75f9592af7b46d37a`. The merge tree object was not exposed by the retrieved commit response or manifests and was not present locally; this audit therefore claims content-set equality, not Git mode or tree-object equality. Source entrypoint hashes are recorded in the JSON.

## What actually ran

| Gate | Observed execution | Scope and limits |
|---|---|---|
| Canonical build/package verification | Eleven recorded checks passed, including locked workspace Release Rust tests, managed build/format, API/XML checks, actual HelloWorld and interop JIT/AOT execution, package layout, and isolated package consumers. | The exact-candidate archive is the HelloWorld bootstrap package, not the 17-package B24 closure. PostgreSQL/SQLite profile logs are native builds. Solution compilation is not execution of every managed domain fixture. |
| Server Rust regressions | The server suite passed 21 tests with zero failures. Logs explicitly contain both new gRPC reaper cleanup regressions and both acceptor outcome/shutdown regressions. | This proves those Rust tests executed on CI source. It does not replace managed protocol and lifecycle verification against the final locally produced native asset. |
| A20 | All 48 commands had an original expected exit status and no timeout: 40 exited zero and eight deliberately exercised fatal/negative outcomes. JIT and Native AOT each passed 8,925 assertions and 72 finite orders. The C fuzzer completed 20,000 runs. All 96 recorded command-output hashes matched the retained files. | Sanitizers cover the C serialized-input decoder, independent oracles, and fatal-child driver. Stable Rust libraries, CLR, and the Native AOT runtime are not instrumented. Coverage is finite and does not prove all schedules or whole-product acceptance. |
| Task04 A14 | The six Core components A01/A03/A04/A05/A06/A07 passed packaged JIT/AOT consumption. The 45-command receipt includes the expected missing-native failure; all 90 output hashes matched. Six transferred AOT consumers passed in the runtime-only container. | The separate minimum-CPU result passed six consumers under QEMU Nehalem emulation; it explicitly does not certify a physical CPU. |
| Task04 A16 | The consumer receipt passed its actual package/error cases, with 17 commands and all 34 retained output hashes matching. All 17 build cases passed, including expected rejection cases. The separate transferred AOT consumer passed. | Runtime receipts for both A14 and A16 report absence of dotnet, Cargo, Rust, and C compilers. These are separate from the SDK consumer receipts. |
| Task07 B24 | The prepared previous and candidate closures each contain 17 packages. Eleven release-case outcomes passed. The full candidate destination executed six graphs: seven initial JIT runs, two edited combined JIT runs, and seven Native AOT runs; ten package/ABI/error case outcomes passed. Previous and rollback destinations each executed the two-provider combined JIT smoke. | The ordinary Entity/DTO/Handler edits in the combined graph reuse native libraries. Candidate graphs cover SQLite, PostgreSQL, HTTP/1.1 TLS, HTTP/2 TLS, gRPC status/result, MCP result, and owner retirement as declared by their consumer checks. They are package-consumer checks, not the complete domain verifiers. |
| B24 runtime transfer | Seven separate transferred AOT cases passed and exited: combined SQLite/PostgreSQL, gRPC, MCP, PostgreSQL, Server, and SQLite. The runtime receipt reports tool absence. | The candidate destination receipt itself says runtime transfer was not executed there; this claim comes from the separate runtime receipt. B24 destination retention contains receipts and identity hashes, not the individual stdout/stderr or runtime payload. Their recorded output hashes could not be independently rehashed from absent files. |

The canonical container receipt confirms Rust was absent before its build, but its raw `pristineMachine` field remains `false`; this audit preserves that distinction. B24 explicitly records no historical fault/soak/performance rerun, no authenticated new domain signer, and no accepted public domain release.

## Remaining applicability boundaries

The current CI entrypoints are `.github/workflows/build.yml`, `.github/workflows/ci.yml`, `eng/build.py`, `eng/verify-task04-linux.sh`, `eng/verify-task07-linux.sh`, and `tests/Verification.Interop/verify.py`, read at the queried product head. They do not invoke the full B17/B18/B19 managed verifiers, or the full ORM/database and codec managed verifiers. The gRPC/MCP package graphs establish actual packaged calls; they do not establish the complete protocol or managed lifecycle matrix. Fresh applicable local verification remains separately attributable to its tested native asset.

These CI packages are not asserted to equal the local Perf-01 producer outputs. CI adds no capacity, performance-comparison, or thirty-minute measurement credit. This audit grants **zero** of the ten required thirty-minute groups.

## Retrieval and retention

All three downloads were completed on 2026-11-21 between 02:20:38 and 02:20:48 UTC. Use the run link and these exact artifact IDs before their recorded expiry. The JSON records actual retrieval timestamps, byte lengths, digests, and sixteen selected receipt hashes. It includes no private environment maps, operational paths, signed download URLs, or key material.

| Artifact | ID | Bytes | SHA-256 | Expires UTC |
|---|---:|---:|---|---|
| `nativeweave-evidence-44852311109-1` | 14686876847 | 46,773,027 | `19eccfbaa414cf9ed0a6ac5752f2cb8ee7ca7961d2dd6b229c69402b25585380` | 2026-12-05 02:10:03 |
| `nativeweave-a20-44852311109-1` | 14686570099 | 9,643,621 | `735f350c4b717d9bf77e8f5c89de5cb7f3ce05850cfa332e3b7c5912d2b0ba4e` | 2026-12-05 01:50:11 |
| `nativeweave-linux-44852311109-1` | 14686916752 | 321,976 | `a4de5dbed3794b86b1474772c9f5ddf9c11a784d87b4bd15086bc087590b8e53` | 2026-12-05 02:10:08 |

The retained result roots are canonical `verification.json` and consumer receipts; A20 `result.json`; Task04 `A14/ci`, `A14/minimum-cpu`, `A16/consumer`, `A16/build-cases`, and `runtime`; and Task07 `B24/prepared`, `B24/native-build`, `B24/release/evidence`, and `B24/runtime/evidence`. The JSON preserves their exact archive member names and hashes for readback.
