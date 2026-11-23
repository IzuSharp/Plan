# DB-API-01 — Linux handoff

## Checkpoint

Initial planning checkpoint; product implementation and acceptance are pending. Read [plan.md](plan.md), [baseline.json](baseline.json) and [acceptance.json](acceptance.json). Worktrees are `.worktree/DB-API-01-linux/{Korda,NativeWeave-Design,Plan}` on `task/DB-API-01-linux`. No pre-existing DB-API-01 branch, PR or handoff was found. Do not clear these worktrees on resume.

Observed main: Korda `7275396176b928c8879d59f4bf20ad8fa7ffb62c`, Design `de1f4796dc199250b405ea99f2129d611f17b1f6`, Plan `5be447a868be78713ada52f46cee16409f0edc13`. Korda has already migrated to C++20/libpq/sqlite3 and now owns current checks and publication selection. Prior records mentioning NativeWeave/Rust or excluding DB-API-01 retain historical meaning.

The current host initially has no discovered dotnet, clang or PostgreSQL executable on PATH. Normal tool installation and repository CI runners are being investigated. This is an environment observation, not a failed product test. No Native AOT, database, packaging, API or release pass is claimed.

## Next work

Publish this Plan-first checkpoint, record its immutable hash in the new Design overlay, publish Design-before-product, then implement only the gaps demonstrated by the current query/relations samples and the order/customer/detail business scenario. Record exact committed routing, isolated provider AOT evidence, SQL counts, cursor/concurrency/transaction boundaries, migration/scaffold checks and same-native DTO reuse. Obtain scoped review and normal PR checks before merging. Observe actual merged-main CI and every triggered publication before final closeout.

No PR or CI URL exists for this initial local checkpoint. Root coordinates PR creation and merges; the documentation author must not imply those actions occurred. Preserve failures and unexecuted claims honestly. The containing evidence commit's own future CI is always checked separately.
