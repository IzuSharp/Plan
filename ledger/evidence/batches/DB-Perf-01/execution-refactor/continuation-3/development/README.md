# Staged development correctness evidence

These checks were executed before the final public package freeze. They retain
their own sources, binaries, commands and failures. The final0f CI is a separate
observation under `../public-ci/`; do not add these stage counts and label the
sum a single final-package local suite.

| Group | Source and evidence boundary |
| --- | --- |
| Streaming | Behavioral migration089ef3c; successful AOT was compiled before final formatting and two assertion-message wording edits. The receipt preserves this limitation. Two providers: 60 cases / 615 main assertions plus scoped/race/reuse gates |
| Core NativeHost | Testf5b7b58 with listed managed products through5cf8343 and isolated native6e3d2df; predates later registration/scheduler/native exception patches. 590 main assertions, 42 transfer-record checks, 32 held-mapper cases |
| Scheduler01 | Original fixture failure: the injected hook remained installed for the session-reuse probe. Its raw consumer and publish logs are retained |
| Scheduler02 | Test92d3b06, managed962071d and nativea781e51; actual AOT across SQLite/PostgreSQL passed8 cases/72 assertions. Test instrumentation cleared before reuse; no product change from attempt01 |
| Primary-error | Mixed development repro and fixed a781e51 four-target ctest gate; see the [precise source and command limits](native-primary-error/README.md) |

The updated [core receipt](DB-Exec-02-correctness-receipt.json) adds original
runner hashes and successful command argv while the original top-level receipt
is preserved. The [scheduler receipt](pull-scheduler-races-02/receipt.json)
binds its exact native images, executable, source files and logs. Binaries are
not copied here; their content hashes remain in the receipts. Relevant original
runner scripts, projects and test source snapshots are under `test-sources/`.
Those snapshots can be matched to the complete pinned product checkout; they
are not standalone substitutes for its build graph.

## Assertions that were retained

The public fetch matrix uses rows0/1/32/64/100/1000 and checks exact accepted
requests/takes/publications1/1/2/3/4/32, one SQL execution per query, and zero
generic retirements before each delivered row. A final generic close can be
zero or one. The original new exact-one assertion failed and is retained in
`nativehost-pull-01/providers/consumer.log`; the corrected run is in
`providers-close-contract/consumer.log`. Zero closes are legal only when the
snapshot already proves the channel worker fence and cursor cleanup retired.
The corrected test preserves those ownership conditions and every per-row
count; it does not add a sleep or weaken the zero-owner predicate.

Stable scoped owners retain generation checks, one-shot result consumption,
held-reader protection, malformed-batch ownership compensation, mapper failure,
NULL/value independence and native finalizer accounting. The 32 held-mapper
provider scenarios cover batchRows1/2, disposal/cancellation/source-close/
session-close and success/failure. Explicit stop boundaries distinguish actual
stop return from merely requesting cancellation.

The scheduler gate holds an overlapping stop before coordinator reservation,
lets setup return a pending ValueTask, then releases stop with every scheduler
offer rejected. Both BeforeRoot and RootAllocated are covered for each provider
with successful and independently failing stop. The exact original setup
exception is published once; a separate stop error is preserved by final join
after cleanup. Callback roots, coordinator slots, controls and native owner
indices0/1/2/3/4/5/8 return to zero. Rejected setup executes zero SQL statements.
Only the normal stop case requires same-session reuse; the deliberately failed
stop poisons its independent source.

The flags and command argv retained here are explicit correctness invocations.
No performance invocation was added to CI, a default test or this archive step.
