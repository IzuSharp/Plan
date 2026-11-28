# DB-CPP-01 contract migration table

The fixed Rust reference is `465cd0f90e6af05ec50eb581156240377cf0825b`;
the accepted C++ candidate is `39b5b72ff9bf4d8a485b55debf940f4ded83bbe2`.
See the [final migration result](migration-report-linux.md) for source, delivery
and acceptance boundaries. Earlier candidate failures were not relabeled as accepted.

| Existing contract | C++ owning modules | Reused tests / independent checks | Status |
| --- | --- | --- | --- |
| Shared Core ABI, negotiation, lifetimes, memory, errors, callbacks, async/executor | `interop.hpp/cpp`, original headers and generated layouts | A01–A08, A20 original JIT/AOT, fuzz and fatal controls | Accepted; candidate-7 complete PR and merged-main gates passed |
| Database ABI / metadata / codecs | `host_abi.cpp`, `contracts`, `scalar`, generated schema | Original 42 signatures, B01/B07 exact managed vectors and malformed bytes | Accepted; candidate-7 complete PR and merged-main gates passed |
| Fluent arena / freeze / clone / aliases / ordered parameters / dialect cache | `query` | 630 assertions; 52 fixed old SQL/parameters/row oracles; original Query.Binding/Native consumers | Accepted; candidate-7 complete PR and merged-main gates passed |
| Relations / CRUD / bulk / optimistic concurrency | `mutations`, Host execute | Existing Orm.Relations and business independent SQL | Accepted; candidate-7 complete PR and merged-main gates passed |
| PostgreSQL TLS / lazy rows / state / errors / cleanup | `provider` libpq 18.0, finite Host ownership | Original eleven provider families; real TLS and COMMIT-response-loss proxy | Accepted; candidate-7 complete PR and merged-main gates passed |
| SQLite engine / busy / transactions / durability | `provider` exact 3.51.3 amalgamation | Original fourteen families / 140,219 assertions; managed JIT/AOT | Accepted; candidate-7 complete PR and merged-main gates passed |
| Source / pools / sessions / transaction and savepoint outcomes | `host` | Original Host and B05 native/managed assertions, unknown outcomes and physical retirement | Accepted; candidate-7 complete PR and merged-main gates passed |
| Bounded streaming / backpressure / transferred batches | `host`, `provider`, `contracts` | Original B06 six native families and 598 managed assertions; whole-row payload regression | Accepted; candidate-7 complete PR and merged-main gates passed |
| Migrations / catalog / history / checksums | `administration`, dedicated Host admin lease | 69 actual database assertions, historical-file/PG-copy consumer | Accepted; candidate-7 complete PR and merged-main gates passed |
| Build / presets / format / tidy / sanitizers | CMake, pinned LLVM 23.1.5 and dependency lock | Shared Release + ASan/UBSan presets; source-bound producer; clean-image Rust absence | Accepted; candidate-7 complete PR and merged-main gates passed |
| NuGet IDs / provider leaves / RID / ordinary models | Existing .NET/package graph with C++ inventory producer | Retained Core closure checks; both database packages × JIT/AOT; native hash after DTO edit | Accepted; twelve-package preparation and four-cell comparison passed; complete release/pristine/runtime/no-Rust gates passed |
| PR review / merge / merged-main CI | Three repository task branches | Independent technical review, observed tested-tree and CI results | Accepted; Design15, Product21 and Plan26 normally merged with successful exact PR/main CI; final evidence record checks are separate |
