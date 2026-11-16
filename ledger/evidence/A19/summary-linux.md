# A19 Linux x64 summary

Status: implementation and Linux component verification complete; independent review accepted. The scoped raw logs/results and hash records are included in this final evidence tree. Full source/configuration/binary copies remain omitted as listed by the batch archive policy.

Bounded admission, retirement, result, dispatcher and mailbox models with replayable unsafe controls. No production-runtime proof is claimed.

## Identity

- Owner: `a19`
- Branch: `task/Task-01-A19-linux`
- Author commit: `d78d6ddb81afdb01efc0e2dbe056e7b441f26487`
- Remote equivalent: `7a40391bbcc5cb925e96185a67c87f62a799f58f`
- Exact task tree: `596c14bfdcb3ed4e15825d6181d9f55da1bedaf3`
- Worktree: `ROOT/.worktree/Task-01-A19-linux/NativeWeave`
- Integrated product head: `22fe70a66312f1a8ec0767d244e3b74762e7ff99`

## Actual verification

5 bounded models;11 unsafe controls;18 regressions;independent liveness/mailbox checks. Final integrated CI passed at https://github.com/IzuSharp/NativeWeave/actions/runs/43811091217 .

The raw evidence, original failure records, source bindings and independent review outputs are retained under `ledger/evidence/A19/` in this final Plan tree. See the [batch handoff](../batches/Task-01/handoff-linux.md) and [raw evidence receipt](../batches/Task-01/raw-evidence-receipt-linux.json) for the publication history, explicit source/configuration/binary omission policy and aggregate hash identity. No task reimplementation is required.
