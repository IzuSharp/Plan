# Perf-01: occupied-prefix protocol experiment preparation

Source and recipe preparation only. No build or load was executed in preparing these files. Root owns the unchanged finite execution helper and all measurement resources.

## Exact experiment

Current is the existing actual `a5748ad4e03825e3da7706d074887952da6c2d43` package/application producer. Candidate is its direct child `092e5e2c74d7419772f2455a2922ae4238f389de`. Both retain the one-millisecond Data/Server retry intervals and the same per-message gRPC writer. Only the coordinator occupied-prefix implementation and its callback tests differ. `candidate-sources.json` and `candidate-delta.patch` bind the exact committed delta, before/after source hashes and unchanged native closure.

Both roles reuse native source `2f40348c3db80a4fbee7a99e721b374a597b16df`, with actual Server SHA-256 `8b726c39ec30003479aeb5b28015fcb97ee5350246a9d7b1bcd7b4ee696f78c0`. Common application, independent client and driver remain `2e3995df8d86583ee9443348276ca8d918056bfc`. This is truthful mixed-source diagnostic provenance, not formal before/final admission.

## Three sequential stages

1. Run the original candidate `tests/Protocols.Grpc/verify.py` with the existing selected native library and native-component receipt. Use a fresh `callback-prefix-b18-001` output, including fresh assembled package/consumer results; no prior managed B18 receipt is substituted. The source proof and actual committed coordinator/test hashes belong to 092e5e2. The verifier and its supplied-native contract are unchanged. Root completes the shared callback prerequisites separately before this stage.
2. Only after the candidate B18 command succeeds and retires, bind its new `execution.json` and `assembled/result.json` hashes to the producer template. Run unchanged B24 `src/Packaging.Domain/prepare.py` with the original 2f native manifest into fresh `callback-prefix-protocol-build-001`. Use versions `0.1.0-perf01.prefix001.1` and `.2`, and consume exactly the `.1` previous feed. Run the narrowly derived `build_protocol.py` here to build the unchanged common2e protocol application. Every package, source, native and resolved cache check remains enabled.
3. Only after that producer succeeds and retires, bind the new candidate execution/build metadata and the existing a5748 producer metadata. Run twelve new TLS cells into `callback-prefix-ablation-001`: two original profiles, three process pairs each, in AB/BA/AB order. Current is a5748 and candidate is 092e5e2. All cells are fresh; previous a5748 timing observations are not counted as one half of these new pairs.

The producer adapter is derived from the prior reviewed binding-retry adapter. Its changes are the candidate/base commit identifiers, candidate index hash, exact changed-file predicate, and explanatory messages. The application copy, NuGet configuration, ordinary restore then locked restore, Release Native AOT x86-64-v2 publication, resolved package archive checks, actual native matching and output manifest blocks are otherwise unchanged. The original common2e builder and all older adapters are left intact.

## Fixed load and checks

`commands.example.json` preserves the original two TLS profiles, 16 calls/second, 20 requested seconds, concurrency four, service CPUs 2–3, generator CPUs 0–1 and controller CPU8. Both roles use the same original EA5 client build, certificate and key. The unary cases are 64 B and 65,536 B; stream cases contain 32 messages of 4,096 B. Original warmup, timeout, dispatch-lag, in-flight, recovery, idle, 500 ms p99, zero-error, 256 MiB RSS and 64 MiB payload budgets remain unchanged.

The per-cell original predicate code is byte-identical to the preceding experiment. Original `run.py prepare` and `run` retain 600-second child limits, and metadata checks retain 60-second limits. The outer helper retains the epoch timing lock and original c752 finite owner; the inner protocol runner uses a separate lock in the new output. Stop on failure, preserve partial records and require actual process retirement. No automatic retry, overwrite or relaxed admission is introduced.

The original run's complete-result metadata and any active-window CPU, allocation, RSS, GC, error and drain observations remain diagnostic only. The coordinator hypothesis specifically concerns scan overhead, so lower latency alone does not settle the CPU tradeoff. Original metadata has no mean/sum for these short cells; no new mean estimator or statistical reader is added. Idle CPU must be obtained from suitable original resource evidence rather than inferred from active CPU. Earlier unfavorable server-stream observations and the original formal gRPC regression remain in history.

`idle_projection.py` reads only each completed original result and adapter receipt. It computes server CPU between `recovery_resources_after` and `after_idle_resources` from the recorded CPU ticks, matching tick frequency and monotonic timestamps. This bracket includes the idle transition and diagnostics and precedes final stop/disposal; it is not an isolated scheduler cost. Missing or invalid counters remain unavailable. It retains every paired absolute CPU value and percentage-point change alongside active CPU, and adds no statistical decision, rejection threshold or load. Root may run it after all twelve cells retire, using `--plan ACTUAL_ABLATION_PLAN --output FRESH_IDLE_PROJECTION_JSON`.

## Actual bindings and commands

Private task-local plans name exact source/worktree/native/environment locations. Public files use descriptive placeholders instead of publishing those maps or TLS material. Output destinations are fresh and explicit. A template's `pending_actual_hashes` is a map of future files, not a claim that their hashes or successful results already exist.

For either future producer or ablation template, after its real prerequisites complete:

```sh
python3 DIAGNOSTIC/bind_actual.py --template PRIVATE_TEMPLATE_JSON --output FRESH_ACTUAL_PLAN_JSON
```

The binder checks actual B18 status and source/native identities, relevant actual producer roles and retired finite commands, reads the new file hashes, verifies every already bound input, and refuses existing output destinations. It emits the actual plan hash but executes nothing. New candidate results are never filled with earlier a5748 hashes. The actual plan remains subject to the unchanged finite runner's pre/post hash checks and child predicates.

Root executes a prepared actual plan using the existing pinned Python and owner:

```sh
taskset -c 8 PINNED_PYTHON EXISTING_EPOCH_FINITE_DIAGNOSTIC_RUNNER \
  --plan FRESH_ACTUAL_PLAN_JSON --plan-sha256 ACTUAL_PLAN_SHA256
```

Do not execute a template with pending values. Keep every previous plan, receipt and result immutable. No formal source contract, noise gate, long-test verifier or product API is changed by this preparation. Final matching-artifact comparisons, capacity and all ten continuous 30-minute segments remain separate acceptance obligations.
