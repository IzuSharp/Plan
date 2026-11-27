# Pull-local07 — one queue-preference hypothesis, before product edits

Baseline: integrated05 Korda `2ea67ce1902f330679c3ebff4d6d5733be20f69c`,
tree `4e3989f2ce9e0c554585aab5a8bbb656e689b18d`. Tail06 is not adopted.
This is an experiment decision, not a measured optimization result.

## Evidence and uncertainty

Existing diagnostic traces show33 coordinator offers/executes per text1000
business:32 turns with a native Run and one without. Before-tail SQLite crosses
sender/executor thread identities for440/528 offers (83.33%); PG for456/528
(86.36%). Every sender previously executed a coordinator in that process. The
actual four diagnostic ELFs inline `preferLocal:false` in Signal, then the locked
runtime passes `forceGlobal:true` into WorkQueue.Enqueue. The source and actual
machine code select global or assigned-global queues and skip local push.

The read-only analysis is
`experiments/tail-completion-06/coordinator-readonly-01`: README SHA256
`4389e48747916c79aa8d825500e4122b744a2c52a0f3a4d8dda379fc9b571cda`,
summary `2900b25c06b08bd0279a37717124ef8caa1d5411e44a34af0298fbe43deeb099`,
32-command actual-ELF receipt
`9059b3fc32f13d22681cba6d05c3491d04d76f853f929c7eec2ee5a757637e25`.
No new workload was run for that analysis. The matching runtime source pin stays
unchanged; current online runtime implementations are not substituted.

Many Execute entries precede the offer-return probe, so subtraction of those
events is not pure queue waiting. Intrusive intervals and thread changes do not
quantify global-queue exclusive CPU, kernel wakeups, cache loss or ordinary-path
migration frequency. Local queues still request workers and allow stealing.
The prediction to test is a repeated ordinary CPU reduction by changing only
the queue preference; reduced thread handoffs is a separate sub-explanation
which requires its own direct observations if claimed.

## Selected isolated implementation scope

After Design records this strategy, a task-marked worktree may add a minimal
internal singleton scheduler forwarding the same existing
`ThreadPool.UnsafeQueueUserWorkItem(IThreadPoolWorkItem, preferLocal:true)` API.
Only HostPullController's default scheduler selects it. Test scheduler injection
remains authoritative. Keep the existing false-constant global adapter unchanged,
and leave HostCommand, cursor close, callback registration and AsyncOperation
default selection unchanged. Do not add a shared bool field, custom pool,
trampoline, batch loop, inline completion, runtime knob or provider switch.

MRVTS RunContinuationsAsynchronously remains true; all setup, cancellation,
native Run/Take, source retirement, generation, snapshot and error ordering
remain as integrated05. Public APIs and the native libraries do not change.
Adding another interface implementation can nevertheless affect AOT dispatch or
devirtualization; source scope alone does not prove identical machine code in
every other path. Bind and inspect the actual new ELF and preserve that limit.

## Necessary correctness before timing

Use real Release Native AOT and both databases. Existing ownership, rejected
scheduling, cancellation, early-stop and held-native-run regressions remain.
Add focused tests using the actual defaults with all three Test*Scheduler hooks
null, because the old RecordingScheduler always uses preferLocal:false.

Prove public pull does not execute driver work inline on the initiating stack;
another worker may execute before queue return, which is allowed. Hold a real
publisher/worker boundary while an independent cursor completes via another
worker, and ensure cancellation/close can progress without waiting on that held
worker. Exercise competing cursors so recurring local work cannot hide a stuck
older request. Use causal barriers and existing finite deadlines, preserve every
failed attempt, and require zero owners. Do not invent a requirement for the same
cursor's next generation to finish before its old Post returns: that is not the
selected integrated05 boundary. No throughput benchmark belongs in these tests
or CI. Independent review must check actual-default coverage and failure cleanup.

## Minimal short causal screen and stop condition

First build two ordinary real PackageReference Native AOT consumers, one per
provider, with new package identities and unchanged native bytes. Reuse the
existing integrated05 and Dapper consumers. Verify actual generated/source,
package, ELF/symbol and native hashes; inspect the actual local adapter/queue
argument and fallback behavior. Source counts alone do not receive new measured
mechanism credit. A separate diagnostic pair is warranted only to answer a
remaining concrete attribution question, not as an automatic four-build suite.

After explicit peer quiet, run only text1000 C1 first:2,048 measured operations
and128 warmup per process, batch32, prepared/persistent, two completely reversed
three-route rounds for both databases. Retain all ordinary results. If the
intended queue change takes effect but CPU benefit does not repeat beyond the
observed noise, or progress/contract/tail risk is material, reject the candidate
without extending its duration or collecting favorable extra rounds.

Only useful repeated CPU benefit justifies the next short contention gate: the
existing 35-case zero-refusal mixed workload at rate500/queue64, SQLite C4/PG C8,
30 seconds per cell with separate warmup and released-idle observation, two
reversed rounds against05 and Dapper. Inspect service and scheduled tails,
per-kind progress, allocation, GC and released RSS. Address a concrete exposed
contract or scenario risk with a targeted short check; do not automatically
repeat the114-process tail06 campaign or the completed pressure05 ramp.

No1800-second run or before-long supplement is authorized this round. Do not
claim parity from a producer-dominated process CPU ratio. If this bounded
experiment fails its causal or regression gate, stop pursuing queue preference,
retain integrated05 and record the remaining gap and delivery limits honestly.
