# DB-CPP-01 contract migration table

The fixed reference is NativeWeave `465cd0f90e6af05ec50eb581156240377cf0825b`. Development passes below do not replace the committed-source acceptance checks in `acceptance.json`.
Current product candidate: `7e70ab8ec9390f4e40f45b4c47e24702f5bf3ed6`. Candidate 5 production, normal packages, four-cell old/new comparison and targeted PostgreSQL package fault passed. Earlier candidate failures remain immutable history. Full retained regression, CI and merges are still required; see [acceptance.json](acceptance.json).


| Existing contract | C++ owning modules | Reused tests / independent checks | Status |
| --- | --- | --- | --- |
| Shared Core ABI, negotiation, lifetimes, memory, errors, callbacks, async/executor | `interop.hpp/cpp`, original headers and generated layouts | A01–A08, A20 original JIT/AOT, fuzz and fatal controls | Implemented; fresh candidate `7e70ab8` source-bound gates pending |
| Database ABI / metadata / codecs | `host_abi.cpp`, `contracts`, `scalar`, generated schema | Original 42 signatures, B01/B07 exact managed vectors and malformed bytes | Implemented; fresh candidate `7e70ab8` source-bound gates pending |
| Fluent arena / freeze / clone / aliases / ordered parameters / dialect cache | `query` | 630 assertions; 52 fixed old SQL/parameters/row oracles; original Query.Binding/Native consumers | Implemented; fresh candidate `7e70ab8` source-bound gates pending |
| Relations / CRUD / bulk / optimistic concurrency | `mutations`, Host execute | Existing Orm.Relations and business independent SQL | Implemented; fresh candidate `7e70ab8` source-bound gates pending |
| PostgreSQL TLS / lazy rows / state / errors / cleanup | `provider` libpq 18.0, finite Host ownership | Original eleven provider families; real TLS and COMMIT-response-loss proxy | Implemented; fresh candidate `7e70ab8` source-bound gates pending |
| SQLite engine / busy / transactions / durability | `provider` exact 3.51.3 amalgamation | Original fourteen families / 140,219 assertions; managed JIT/AOT | Implemented; fresh candidate `7e70ab8` source-bound gates pending |
| Source / pools / sessions / transaction and savepoint outcomes | `host` | Original Host and B05 native/managed assertions, unknown outcomes and physical retirement | Implemented; fresh candidate `7e70ab8` source-bound gates pending |
| Bounded streaming / backpressure / transferred batches | `host`, `provider`, `contracts` | Original B06 six native families and 598 managed assertions; whole-row payload regression | Implemented; fresh candidate `7e70ab8` source-bound gates pending |
| Migrations / catalog / history / checksums | `administration`, dedicated Host admin lease | 69 actual database assertions, historical-file/PG-copy consumer | Implemented; fresh candidate `7e70ab8` source-bound gates pending |
| Build / presets / format / tidy / sanitizers | CMake, pinned LLVM 23.1.5 and dependency lock | Shared Release + ASan/UBSan presets; source-bound producer; clean-image Rust absence | Implemented; fresh candidate `7e70ab8` source-bound gates pending |
| NuGet IDs / provider leaves / RID / ordinary models | Existing .NET/package graph with C++ inventory producer | Core closure pass; both database packages × JIT/AOT; native hash after DTO edit | Candidate5 twelve-package prepare and fresh four-cell comparison passed; full release/runtime CI pending |
| PR review / merge / merged-main CI | Three repository task branches | Independent technical review, exact tested-tree and CI receipts | Design15 merged with green main CI; Product21 and Plan26 remain draft |
