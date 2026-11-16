# A01 Linux x64 summary

Status: implementation and Linux component verification complete; independent review accepted. The scoped raw logs/results and hash records are included in this final evidence tree. Full source/configuration/binary copies remain omitted as listed by the batch archive policy.

ABI records, generated layout/signature contracts, stateless version/bootstrap fixture and managed/Rust conformance. Accepted runtime evidence is attempt-005; later safety-comment and split-lock changes have separate reviews.

## Identity

- Owner: `a01`
- Branch: `task/Task-01-A01-linux`
- Author commit: `1412604137cc8294d1ffc0c3a7e99f697ec0a431`
- Remote equivalent: `c3d55e6dfd0e29963836ca2de1c100cdf27b47b4`
- Exact task tree: `e236fa051622c8852963a62621fd64c6641fb04d`
- Worktree: `ROOT/.worktree/Task-01-A01-linux/NativeWeave`
- Integrated product head: `22fe70a66312f1a8ec0767d244e3b74762e7ff99`

## Actual verification

47 full-run commands;682 assertions each JIT/AOT; C/Rust/C# layout/signature and negative controls;6 supplemental locked restores. Final integrated CI passed at https://github.com/IzuSharp/NativeWeave/actions/runs/43811091217 .

The raw evidence, original failure records, source bindings and independent review outputs are retained under `ledger/evidence/A01/` in this final Plan tree. See the [batch handoff](../batches/Task-01/handoff-linux.md) and [raw evidence receipt](../batches/Task-01/raw-evidence-receipt-linux.json) for the publication history, explicit source/configuration/binary omission policy and aggregate hash identity. No task reimplementation is required.
