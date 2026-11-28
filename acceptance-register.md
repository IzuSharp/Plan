# Recorded acceptance and outcome boundaries

| Record | Preserved state | Scope |
| --- | --- | --- |
| R01–R34 | 34 accepted | Research conclusions in their historical source scope |
| D01–D32 | 32 accepted | Implementation-guiding design and documentation |
| A01–A24 / B01–B24 | 48 planned candidates | Original task definitions; no automatic execution authority |
| DB-Scope-01 | Delivered | Database-only product and retained consumer behavior |
| DB-CPP-01 | Delivered | Linux x64 Rust-to-C++ migration and compatible public behavior |
| DB-API-01 | Delivered | Fluent ORM experience, both providers, public AOT consumption |
| DB-Exec-11 | Recorded scoped results | Selected 17da path and four local long comparisons; parity and framework-only zero remain unproven |

The graph nodes retain their original IDs, states and dependency edges. Their
historical research/design acceptance does not establish acceptance of later
product bytes, future platforms, long-running workloads or packages.

The 2026-11-13 research/design acceptance is associated with Design
`08e3aaee73aad174620dcff18ed21b3b14c5e632` and Plan
`c3947b378e0a251f8dfeaf7fd7d4acc636631974`; see
[Design PR10](https://github.com/IzuSharp/Korda-Design/pull/10) and
[Plan PR8](https://github.com/IzuSharp/Plan/pull/8). Later Public API refinement
has its own recorded source revisions. Git history and PRs preserve those
formal documents; current CI does not replay their former receipt inventories.

Current delivered result documents are indexed in [CURRENT-PHASE.md](CURRENT-PHASE.md).
Keep failures, restrictions and unproven claims in the conclusion itself. Record
new reviews against actual changed scope and source commits. A technical agent
review is not a separate GitHub approval account.

## Earlier Linux implementation batches

These are conclusions from the original Task-01–07 records. They supplement the
unchanged historical task-node states and do not grant current execution authority.

| Batch | Recorded Linux x64 scope and outcome |
| --- | --- |
| Task-01 | A01, A19, A21 and B01 completed, reviewed and integrated; normal delivery and existing preview consumption completed. |
| Task-02 | A02, A05, A09, B02, B03, B05, B06, B07 and B09 accepted for Linux. |
| Task-03 | A03, A04, A10, A11, A12, A13 and A22 completed; merged CI and existing HelloWorld preview consumption passed. |
| Task-04 | A06, A07, A08, A14, A16, A17, A18, A20, A23 and A24 accepted for Linux; A15 Windows scope deferred. |
| Task-05 | B04, B08 and B10–B14 accepted; implementation PR17/Plan PR20 delivered with observed CI and existing preview consumption. |
| Task-06 | B15–B20 accepted and integrated; implementation PR16, merged CI and existing preview publication/consumption completed. The final Plan record had its own later closeout. |
| Task-07 | B21/B22/B23 accepted within recorded scope; B24 candidate C accepted locally and in its applicable CI, with normal merge/main/HelloWorld-preview closeout still pending at that checkpoint. |

Task-07 B22 accepted SQLite/PostgreSQL 30-minute workloads and 60-second idle
observations. The user deferred 24-hour and 72-hour runs; neither was executed.
B23's superseding finite report used 468 valid processes and 30 cases. NativeWeave
was slower than direct Rust beyond measured noise in 13 of 18 matched ordinary
cases; four were inconclusive and one within band. Mean application RSS was lower
than managed AOT and higher than direct Rust in all 18 cases. These are observed
route/process results, not a universal performance advantage, native allocator
measurement or exclusive framework/FFI attribution. C# application edits reused
native assets; other-platform acceptance and global performance claims were absent.

B24's candidate-specific package/runtime checks did not rerun B22/B23 on its
changed native binaries. Its accepted CI was
[44351062732](https://github.com/IzuSharp/Korda/actions/runs/44351062732);
the separate CodeQL aggregate still had two high comparator findings at that
checkpoint, so this record does not describe every check as green or claim its
pending delivery completed. Later database-only/C++ batches have separate scope.
