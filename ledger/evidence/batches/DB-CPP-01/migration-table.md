# DB-CPP-01 contract migration table

The fixed reference is NativeWeave `465cd0f90e6af05ec50eb581156240377cf0825b`. Development passes below do not replace the committed-source acceptance checks in `acceptance.json`.

| Existing contract | C++ owning modules | Reused tests / independent checks | Status |
| --- | --- | --- | --- |
| Shared Core ABI, negotiation, lifetimes, memory, errors, callbacks, async/executor | `interop.hpp/cpp`, original headers and generated layouts | A01–A08, A20 original JIT/AOT, fuzz and fatal controls | Development passes; final clean rerun pending |
| Database ABI / metadata / codecs | `host_abi.cpp`, `contracts`, `scalar`, generated schema | Original 42 signatures, B01/B07 exact managed vectors and malformed bytes | Development passes; exact public bytes preserved |
| Fluent arena / freeze / clone / aliases / ordered parameters / dialect cache | `query` | 630 assertions; 52 fixed old SQL/parameters/row oracles; original Query.Binding/Native consumers | Development passes; composed Fluent gate pending |
| Relations / CRUD / bulk / optimistic concurrency | `mutations`, Host execute | Existing Orm.Relations and business independent SQL | Native unit pass; final composed gate pending |
| PostgreSQL TLS / lazy rows / state / errors / cleanup | `provider` libpq 18.0, finite Host ownership | Original eleven provider families; real TLS and COMMIT-response-loss proxy | Development pass; patched-source binding rerun underway |
| SQLite engine / busy / transactions / durability | `provider` exact 3.51.3 amalgamation | Original fourteen families / 140,219 assertions; managed JIT/AOT | Development pass |
| Source / pools / sessions / transaction and savepoint outcomes | `host` | Original Host and B05 native/managed assertions, unknown outcomes and physical retirement | Formal B05 passed on b383c130; remaining composed gate pending |
| Bounded streaming / backpressure / transferred batches | `host`, `provider`, `contracts` | Original B06 six native families and 598 managed assertions; whole-row payload regression | Formal first candidate failed retirement/credit timing; correction underway, original bounds retained |
| Migrations / catalog / history / checksums | `administration`, dedicated Host admin lease | 69 actual database assertions, historical-file/PG-copy consumer | Module pass; old-data consumer underway |
| Build / presets / format / tidy / sanitizers | CMake, pinned LLVM 23.1.5 and dependency lock | Shared Release + ASan/UBSan presets; source-bound producer; clean-image Rust absence | Clean b383c130 native producer and full tidy passed; Release 18/19, final CI/LSan pending |
| NuGet IDs / provider leaves / RID / ordinary models | Existing .NET/package graph with C++ inventory producer | Core closure pass; both database packages × JIT/AOT; native hash after DTO edit | Full candidate feed and old/new parity pending |
| PR review / merge / merged-main CI | Three repository task branches | Independent technical review, exact tested-tree and CI receipts | Plan26, Design15 and product21 draft; first product CI running; none merged |
