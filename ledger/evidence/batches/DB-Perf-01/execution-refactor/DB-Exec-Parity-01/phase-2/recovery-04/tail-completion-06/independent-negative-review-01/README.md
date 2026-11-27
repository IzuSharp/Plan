# tail06 baseline publication negative — independent review

Reviewer: `/root/candidate_contract_review`. Author: `/root/worker_boundary_review`.

**The deliberate negative control matches its specified failure. It is not a baseline correctness pass.** The input receipt is `negative-control-01/receipt.json`, SHA-256 `9da2b7b5a43b2f344b636ca06ce95a5dcfc412eb76de6d0997dd6524a040ee5e`. Its `negativeControlMatched=true`, `runtimeCorrectnessPassed=false`, `baselineCorrectnessRunPassed=false`, and no-performance-credit fields express the correct distinction.

The actual test-only commit is `4efce12ff6c1ece1f059e5b209e4e6a02a38acce`, tree `be90772a53d239261ae2c1ab43281760cac843e9`. The clean worktree differs from baseline product `2ea67ce1902f330679c3ebff4d6d5733be20f69c` only in `tests/Data.NativeHost/Program.cs` and `ReadySchedulingTests.cs`; both test files are byte-identical to candidate `4a9e4435ea5c836be44fb00dc4219301567072c6`. Product and native source are unchanged. The actual Native AOT ELF, retained symbols, original native assets, publish copies, and raw command/consumer log hashes match the receipt.

The actual child exit is **250**. Its raw log stops at the exact expected assertion:

> Post's exact failure escapes the managed executor once; it is not translated into SchedulingFault.

The selected entry point calls the SQLite `consumeThenRequest: true` case first. That case sets the custom captured context, consumes generation 1 and requests generation 2 synchronously inside Post, and then throws the specific captured exception. The test observes the exception returned by the managed executor and fails the exact-reference assertion. The old coordinator's source keeps `Process()` inside its `SchedulingFault` catch; old HostPull `SchedulingFault` records failure, marks indeterminate, poisons the source and signals again. This static source path explains the demonstrated failed boundary. The raw negative log does not separately expose the caught exception variable or a final generation-2 result, so this review does not claim an additional measured generation-2 outcome.

Because the SQLite assertion fails, the PostgreSQL business call is never reached. The shared runner nevertheless starts and stops its PostgreSQL fixture; the retained PostgreSQL log confirms both readiness and shutdown. `coverage.json` states these scopes correctly. There is no two-provider baseline business-negative claim and no requirement to add an optional second negative run merely to make that label broader.

`validation.json` records **28 checks, all passing**, covering the precise source/test relationships, artifacts and log hashes, actual exit, negative-versus-correctness schema, expected raw assertion, SQLite-first coverage and PostgreSQL fixture lifecycle. This reviewer ran no database, build, test or performance workload. The candidate's already completed two-provider full correctness suite is a separate positive receipt and remains unchanged.

This negative demonstrates that the newly added regression detects the old completion-publication exception boundary. It does not establish a throughput, CPU, allocation, scheduling-time, or final-campaign improvement.
