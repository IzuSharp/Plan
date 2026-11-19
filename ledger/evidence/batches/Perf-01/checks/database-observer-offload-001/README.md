# Perf-01 database observer: integrated source and finite checks

The measured candidate is NativeWeave
[a3ce0f6295c535b0a81de95fc0f98aa19deb259c](https://github.com/IzuSharp/NativeWeave/commit/a3ce0f6295c535b0a81de95fc0f98aa19deb259c),
tree `eb6b61e7c159c343513f7a50359f1a6c09f8df77`, with parent
`d859b79eedb87dfc372be6c07e516d173c96124b`.
The complete remote tree matched the actual local checkout. All seven changed
files were also retrieved at that exact commit and matched. The primary runtime
and the original immutable measurement drivers remain unchanged.

## Source review

A separate reviewer inspected the actual seven-file observer candidate and the
retained long verifier. The first worker await is shielded; repeated cancellation
joins the same strongly referenced job; a completed final sample is published
once before cancellation propagates. Serial sampling prevents overlapping jobs.
Worker phase and read timestamps are distinct from submission time. Omitting
the new policy preserves the legacy synchronous path.

The review identified that only application RSS initially received the
conservative measurement-window overlap rule. The final candidate passes the
same window to target, scheduler and controller summaries. The reviewer checked
this exact correction at `a3ce0f62`; the issue is closed. The unchanged long
verifier still reports a separate phase-only raw RSS figure, but first requires
the driver's conservative service-standard gate to pass. Reports must distinguish
these scopes.

The earlier local producer lineage and the first published candidate had
different unrelated verifier files. They are not described as identical complete
trees. The integrated measured candidate preserves all current parent verification
tooling and has its own exact source identity.

## Actual finite execution

At 2026-11-19T22:24:27.572325Z–22:24:27.896311Z, the actual integrated checkout
passed six observer lifecycle/boundary tests, four scheduler-GC tests and the
changed-source whitespace check. Execution used CPU8 and the locked Python3.12.14.
HEAD, complete tree and ten source hashes matched before and after; the checkout
remained clean. The verifier was hash-bound but was not executed by this finite
test group.

`source-and-finite-checklist.json` is an explicit projection of the real finite
execution receipt and checked log hashes. It retains source identity, test counts,
actual exits and times. Full local producer and integrated execution records remain
separate. No product-runtime optimization, load, capacity or long-duration credit
is established by these tests.

The next diagnostic uses the same measured source, unchanged before product,
deferred scheduler-GC policy, load and resource rules on both sides. It explicitly
selects synchronous versus threaded resource sampling. Fresh load equivalence,
calibration, noise and long acceptance remain pending.

## Reproduction

Check out the exact candidate, use the locked Python, and run outside measurement
windows:

```bash
taskset -c 8 "$LOCKED_PYTHON" -B tests/Perf01.Database/test_observer_sampling.py
taskset -c 8 "$LOCKED_PYTHON" -B tests/Perf01.Database/test_scheduler_gc.py
git diff --check HEAD^ HEAD
```

These are measurement-tool tests. They do not rebuild or execute a new C#/Rust
product package.
