# B01 Linux x64 summary

Status: implementation and Linux component verification complete; independent review accepted. The scoped raw logs/results and hash records are included in this final evidence tree. Full source/configuration/binary copies remain omitted as listed by the batch archive policy.

Exact Data API, immutable metadata/value contracts, canonical Rust validators and wire/session declarations, public XML/reference, isolated NuGet/JIT/AOT consumer. Provider/host/query/generator work remains outside this task.

## Identity

- Owner: `b01`
- Branch: `task/Task-01-B01-linux`
- Author commit: `4feadc6f8360392b7d8226426bdbd9aaa7bf5a54`
- Remote equivalent: `373afdde31a6e239ba7125fd1f4e0d39d60258f2`
- Exact task tree: `479bd7a866f122599a5d606c688c50ccaa256956`
- Worktree: `ROOT/.worktree/Task-01-B01-linux/NativeWeave`
- Integrated product head: `22fe70a66312f1a8ec0767d244e3b74762e7ff99`

## Actual verification

132 API/XML symbols;12 JIT/AOT families;10 goldens;43 malformed cases;4 expected compile failures;NuGet JIT/AOT and Rust trap0;split-lock and whitespace supplements. Final integrated CI passed at https://github.com/IzuSharp/NativeWeave/actions/runs/43811091217 .

The raw evidence, original failure records, source bindings and independent review outputs are retained under `ledger/evidence/B01/` in this final Plan tree. See the [batch handoff](../batches/Task-01/handoff-linux.md) and [raw evidence receipt](../batches/Task-01/raw-evidence-receipt-linux.json) for the publication history, explicit source/configuration/binary omission policy and aggregate hash identity. No task reimplementation is required.
