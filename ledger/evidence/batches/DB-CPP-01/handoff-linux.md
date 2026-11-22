# DB-CPP-01 Linux handoff

## Current state: candidate 5 packages and four-cell comparison passed; full CI pending

The owner authorized the database-only Rust-to-C++ migration, tests, documentation, pushes, PRs and normal merges. DB-API-01 and DB-Perf-01 remain excluded. Product acceptance is **not complete**. Earlier failures remain evidence; a development pass does not attest a new package or CI run.

| Repository | Frozen merged starting commit | Current delivery |
| --- | --- | --- |
| NativeWeave | `465cd0f90e6af05ec50eb581156240377cf0825b` | Candidate 5 `7e70ab8ec9390f4e40f45b4c47e24702f5bf3ed6`, tree `ea00a3871ae4c26b8833d2924b7f94451f006d42`; [draft PR21](https://github.com/IzuSharp/NativeWeave/pull/21) |
| NativeWeave-Design | `8298dc4128b745cf1809bad0c3cf02c45eb7f522` | [PR15](https://github.com/IzuSharp/NativeWeave-Design/pull/15) merged as `de1f4796dc199250b405ea99f2129d611f17b1f6`; exact main CI passed |
| Plan | `1fe52a8bd792ccdbb4bbea17ba59b0ad0c24349d` | [Draft PR26](https://github.com/IzuSharp/Plan/pull/26); previous checkpoint `ce9b0852369a44207819171fe48a9c4bad3fddfc` passed [CI44965665449](https://github.com/IzuSharp/Plan/actions/runs/44965665449) |

All work branches use `task/DB-CPP-01-linux`. Worktrees are `ROOT/.worktree/DB-CPP-01-linux/{NativeWeave,NativeWeave-Design,Plan}`. The read-only Rust reference is `ROOT/baseline/rust`. Preserve old native/package outputs and diagnostic records before producing a new candidate. The initial user-requested orphan cleanup is complete; current work is not disposable old work.

## Reference and toolchain

The twelve fixed Rust packages came from [merged baseline CI44924918463](https://github.com/IzuSharp/NativeWeave/actions/runs/44924918463), artifact `14715983822`, ZIP SHA-256 `7a7982ccda96d3a5d7f3f4b00713a8668ae5548ec189419e3c22af5493248a11`. Individual package and library identities are in [reference provenance](rust-reference-provenance.json) and [package inventory](rust-reference-packages.json).

Linux uses LLVM 23.1.5, CMake 4.3.3, Ninja 1.13.2, .NET 11.0.100, PostgreSQL 18.0 and SQLite 3.51.3. Formal C++ builds use the locked patched libpq tools. The native producer records real compiler paths, hashes and target triples and rejects Rust on its producer PATH. Shared presets are `linux-x64-release` and `linux-x64-asan-ubsan`. Local ASan/UBSan uses `detect_leaks=0` because this host blocks LeakSanitizer process inspection; mandatory CI still requires `detect_leaks=1`.

## Candidate 4 remains rejected

Candidate 4 is `7ad56394a8a119202cfee5088406c5459f4cc6f0`, tree `0bd369df2dabf2391c2c9b508757fdb2a5948afb`. Its clean native build, twelve packages, 19 CTests, full Clang checks, managed build, 56 retained regression commands and four-cell business comparison passed. Full-source review then found relation/CRUD create-time deadlines and relation-capacity error precedence differed from Rust. Official [CI44962483407](https://github.com/IzuSharp/NativeWeave/actions/runs/44962483407) failed the original PostgreSQL provider-drain fault in JIT and AOT. Later mandatory CI gates were not reached.

[Its acceptance snapshot](checkpoints/candidate-4/acceptance-at-rejection.json), [failed CI receipt](receipts/candidate4-ci-drain-failure.json), [blocked review receipt](receipts/candidate4-review-blocked.json), and all earlier checkpoints remain unchanged. The complete previous handoff is preserved at [ce9b085](https://github.com/IzuSharp/Plan/blob/ce9b0852369a44207819171fe48a9c4bad3fddfc/ledger/evidence/batches/DB-CPP-01/handoff-linux.md). Candidate 5 checks begin pending; no candidate 4 pass is rebound to the new commit.

## Candidate 5 correction and development results

The committed correction restores relation/CRUD create-time elapsed budgets and Host capacity precedence, requires the locked Clang for the filesystem fault shim, and restores PostgreSQL explicit protocol confirmations and pool lifecycle behavior. Physical connection retirement no longer returns a still-live Host Session's admission permit. Idle health checks and replacement share the original lower-pool acquisition deadline. The original business fault ordinal, managed executable code, assertion limits and deadlines remain unchanged. Current API XML comments, package description and sample comments now describe the C++ backend; the retained SQLx-compatible checksum format is explicit.

| Development validation | Observed result | Public summary |
| --- | --- | --- |
| B14 actual ABI checks and old/new replay | 352 checks; 16 fixed SQLite/PostgreSQL probes match; two precise negative controls reject | [Existing development checkpoint](checkpoints/candidate-5-development/) |
| PostgreSQL native protocol/Host checks | Release and ASan/UBSan each pass 17 groups / 214 checks | [Correction summary](checkpoints/candidate-5-development/public-summary/postgresql-correction.json) |
| Actual fixed Rust versus corrected PostgreSQL ABI | Eight cases match; six owner counts zero in each; independent persistence/retirement checks pass | [Eight-case summary](checkpoints/candidate-5-development/public-summary/eight-abi-comparisons.json) |
| Precise reverted-confirmation controls | Removing either the first COMMIT confirmation or recovery confirmation makes its real test fail | [Correction summary](checkpoints/candidate-5-development/public-summary/postgresql-correction.json) |
| Non-author delta review | No remaining blocker within the reviewed correction; same-team subagents disclosed | [Review](checkpoints/candidate-5-development/public-summary/independent-review.json), [addendum](checkpoints/candidate-5-development/public-summary/independent-review-addendum.json) |

These summaries contain public source identities, result categories/counts and original evidence hashes. Detailed local protocol diagnostics are retained for verification. The old SQLx pool-return receipt can report Usable even when the pool discards the physical connection, including pool shutdown; this existing observation limit is preserved and disclosed in the report. Its internal return ping has no independent native timeout wrapper. A bounded Host waiter is not proof that native retirement has completed.

## Formal candidate 5 observations and next actions

- Clean native producer and normal twelve-package preparation passed. Raw manifest SHA-256 values are `03032cd7625ea5140ee441c0366a93844279791dd72f767046f0c9bfe2ce9bc7` and `547a1cf36d4621269d203e2c10e9ff48498d9acd4a1253704cc34554c5f45e2b`. [Public source-bound summaries](checkpoints/candidate-5/summary-index.json) retain the actual source, tool, dependency, package, capability and binary identities.
- Fresh same-source old/new comparison passed all four provider/runtime cells, 24 ABI refusals, independent SQL, history handover and DTO-native-hash checks. [Comparison](checkpoints/candidate-5/migration-comparison.json) original SHA-256: `55c41737d1c263ebe6dcdd9ebf8162c770034f6341b92b52b90d06df95ae417f`.
- The original PostgreSQL provider-drain failure now passes in actual normal-package JIT and AOT, plus separate passive runs: four runs, six original assertions each. [Targeted summary](checkpoints/candidate-5/postgresql-package-fault.json). The earlier eight ABI comparisons bind to the identical formal ELF; they were not rerun in this phase.
- [Integrated non-author technical review](reviews/candidate5/integrated-review.json) has no remaining source blocker within its stated coverage. The exact Design review is unchanged. These are same-team reviews with author exclusions, not external approvals.
- Complete local clang-format/tidy, locked restore and Release managed build passed. The full retained regression suite is running against candidate 5. Native/package source and manifests remain unchanged.
- [Product CI44968972018](https://github.com/IzuSharp/NativeWeave/actions/runs/44968972018) is running. Its four security jobs have passed; the full build/package task and later mandatory gates are not yet accepted. [Plan checkpoint CI44969091425](https://github.com/IzuSharp/Plan/actions/runs/44969091425) passed at `1bade8701a54d2185c8765478343683ccc9aacd4`.

Next: finish the complete retained suite and all mandatory CI gates, including LSan, compatibility/fuzz, CPU/runtime, release/recovery/pristine and fresh Rust-free production. Preserve failures and correct causes without relaxing checks. Then normally merge product PR21 and observe exact main CI. Finalize and merge [the report](migration-report-linux.md) with Plan PR26, observe its main CI, and record the delivered identities through the documented evidence-only follow-up. DB-CPP-01 remains incomplete until those gates finish; stop after this task.
