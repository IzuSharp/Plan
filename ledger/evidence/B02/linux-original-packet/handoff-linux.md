# B02 Linux handoff

Status: implementation and component verification complete; independent technical review and batch acceptance remain with the Task-02 lead.

- Branch: `task/Task-02-B02-linux`.
- Worktree: `/workspace/scratch/0898a75257bc/.worktree/Task-02-B02-linux/NativeWeave`.
- Final tested commit: `0f63ddd2ec323181781432c009955250ac06c898`.
- Owned checkpoints: `a2bd1b7`, `1a2ea3b`, `c7ffb81`, `0f63ddd`.
- Shared root contributions already present: `aa33806` (Cargo/TLS closure), `59a2eff` (canonical shared control parser and managed IVT).
- NativeWeave batch PR: https://github.com/IzuSharp/NativeWeave/pull/13 . Plan batch PR: https://github.com/IzuSharp/Plan/pull/14 . Root owns updates, pushes, independent review, merge and post-merge CI/publication.

## Final actual validation

`attempt-003` passed all 27 commands from a clean committed source tree, with every recorded source/lock hash unchanged. Rust 1.100.0 and .NET SDK11.0.100; Linux x64; PostgreSQL18.0 over TCP. Ten actual provider oracle groups ran in native Rust, C# JIT and actual Native AOT (`dynamicCodeSupported=False`). Both managed modes passed 22 assertions. Exact compiled API/XML/reference coverage:12 symbols. The3 exact B04 composition declarations are separately recorded; no fake datasource/factory was introduced.

Cases cover TLS verified server identity and wrong-host/untrusted-root/expired-certificate/plaintext negatives; statement timeout57014 and failed-transaction25P02 with same-backend rollback/reuse; early stream drop and admission cancellation; B07 UUID/numeric/instant/text/NULL conversion; B05 savepoint rollback-to/release and commit/cancel-before-dispatch; actual COMMIT-response loss yielding B05 Unknown despite durable rows; conflict CTE empty old snapshot versus next SELECT; drain-timeout/server-kill quarantine and restored permits; migration advisory-lock1 negative control then0 after product retirement; and session close waiting for an admitted operation.

The final facade requires an actual maintainer-precompiled native asset. MSBuild hashes it into `obj`, emits the bounded A02 output record and copies the exact file. Both ordinary `Inspect()` and advanced explicit-path preflight execute in JIT/AOT. There is no committed machine-specific ELF hash, zero-hash placeholder or consumer Cargo invocation. Generated inputs and actual native/managed/executable hashes are separately bound.

## Row-bound derivation and integration finding

Let P be a producer-owned row, Q a queued row, and H the just-received delivery handoff before counter subtraction. The producer reserves the only channel slot before SQLx next(), so P+Q <=1. The single receiver subtracts the previous delivery charge before another poll, so H<=1. Therefore P+Q+H<=2. SQLx internal buffers and B06 decoded/wire bytes remain separately accounted. The queue capacity is1; two is the conservative retained-row/handoff count, not two queued rows or an RSS bound. Actual B06 integration exposed the original peak1 claim; its first failure is preserved under B06 evidence. B02's final oracle observations are [1, 1, 1], all within2. No execution behavior or queue capacity changed to hide that observation.

## Scope and next steps

Only Linux component acceptance is claimed. B04 Create/UsePostgreSql host composition, B21/B24 full assembled/pristine NuGet consumption and other-platform acceptance remain outside this packet contribution. Native adapter code consumes canonical B01/B07 and B05 policy; no second pool/runtime or managed PostgreSQL provider exists. Root must combine B05/B06 actual-provider evidence and complete independent review before marking the Task-02 batch accepted.

The packet contains raw text/JSON evidence and hashes, excluding PostgreSQL data directories, private test keys, binaries, caches and package payloads. Reproduce with committed `tests/Data.Postgres/verify.py`. `security-independent-review/` is the separately requested independent review of root's narrow Gitleaks config; no config change was made by this agent.
