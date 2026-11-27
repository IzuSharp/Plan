# Small-query RhSpinWait caller — completed bounded attribution

Eight PostgreSQL money1 diagnostic processes completed: unchanged main, decimal only, Worker-D only, and Worker-D plus decimal; 8,192 checked businesses/process, 256 warmups, two reversed rounds. All business and owner checks passed. The default runtime and original SQL/DTO/workload were retained. These are instrumented observations, with **no ordinary CPU, latency, allocation, RSS or final campaign credit**. The separate ordinary money1 regression is not overwritten by diagnostic timing.

The sampler records user callchains, IP/SP/BP, and 128 bytes of bounded user stack. Native and Native AOT controls, actual loss/overflow negatives, independent raw decoding, strict record checks, generated-reader/runtime/package identities and matching ELF/debug machine code are retained. Seven full validators passed. One full validator remains rejected for a single invalid libc user FP chain; its raw bytes decode correctly and report no loss. The rejected process is not labeled a fully valid stack capture.

| Round / path | Steady user CPU samples | RhSpinWait samples | Verified direct caller | Native-image leaf samples | Verified through WaitSlow |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 main | 2,166 | 1,399 | 1,399 | 211 | 1,377 |
| 1 decimal | 2,167 | 1,507 | 1,507 | 184 | 1,491 |
| 1 Worker-D | 1,661 | 902 | 902 | 228 | 896 |
| 1 combined | 1,815 | 1,154 | 1,154 | 191 | 1,147 |
| 2 combined | 1,510 | 949 | 949 | 184 | 936 |
| 2 Worker-D | 2,002 | 1,262 | 1,262 | 219 | 1,253 |
| 2 decimal | 1,933 | 1,247 | 1,247 | 189 | 1,239 |
| 2 main | 1,805 | 1,023 | 1,023 | 209 | 1,011 |

All 9,443 RhSpinWait direct callers were validated using the sampled instruction, captured register/stack bounds, and the actual CALL instruction preceding its recovered return address. RhSpinWait's 42-byte machine code pushes rbp/r14/rbx; its usual loop return word is SP+24/BP+8. Entry and epilogue samples use their own instruction-bound offsets. No heuristic search for plausible code addresses is used.

Direct callers comprise 9,371 Thread.SpinWait samples, 71 ObjectHeader.TryAcquireUncommon samples and one LowLevelLifoSemaphore.WaitAsWaiter sample. The 9,371 Thread.SpinWait samples decompose completely:

- 9,350 have three verified actual CALL return points through Thread.SpinWait and Backoff.Exponential to LowLevelLifoSemaphore.WaitSlow.
- Three come through Backoff from LowLevelLock.SpinAndAcquire, with observed Timer/WaitSubsystem context. The original overbroad hypothesis that every Backoff sample must be WaitSlow was rejected and remains recorded as a failed hypothesis.
- Seventeen have a Lock.TryEnterSlow return context: an actual CALL to LowLevelSpinWaiter.Wait followed by that helper's verified tail jump to Thread.SpinWait. A tail jump is not relabeled as a direct CALL.
- One is a direct Thread.SpinWait call from SpinWait.SpinOnceCore.

Kernel FP chains are incomplete at five RhSpinWait entry/return boundary samples and skip the frame-pointer-omitting Backoff implementation. The bounded instruction-aware stack proof resolves these specific cases. It does not claim a general-purpose perfect unwinder. The one invalid libc FP-chain record remains unknown and is not used for any spin inference.

Runtime source is pinned through ILCompiler11.0.0 VMR `297acf930fb0f5c07fd4e51d78e521b4ad2e5d1f` to runtime `deae2e32bf0e018e09d64597b7c59b62b73bb3ce`. Actual machine code and source bindings include Thread.NativeAot.cs349, Backoff.cs29, LowLevelLifoSemaphore.cs109–131 and PortableThreadPool.WorkerThread.cs127. Most observed spin therefore belongs to the runtime work-semaphore acquisition/wait path, rather than the decimal parser or an inferred Korda object gate. This does not identify an individual request's waker, exact scheduler delay or exclusive wait CPU.

## Interpretation and retained uncertainty

Decimal and combined native-image leaf counts are lower than their respective controls in both rounds. That image also includes statically linked driver code, so it is not pure framework CPU. Most spin is independently identified as ThreadPool waiting, but diagnostic process CPU did not reproduce the historical ordinary money1 increase consistently. **Its complete causal explanation remains open.** Sample counts are neither invocation counts nor exclusive elapsed/CPU durations; do not multiply by the sampling interval to manufacture phase costs.

There is no offered-load arrival producer in these rate-zero closed-loop captures. Future offered-rate mixed runs do include the producer, and process CPU must retain that cost unless separately measured attribution exists. Runtime settings remain default for ordinary/final consumers; the earlier spin-limit sensitivity remains diagnostic only.

The authoritative local records are `experiments/sampler04/completion.json`, `resume.json`, `money1-02`, `waitslow-proof-01`, source/machine manifests, and the following immutable report plus correction:

| Record | SHA256 |
| --- | --- |
| caller-findings-04.md | `63eaa43322c9ad4853ec4128eefa2788d70138c85e86d5caf7e1f2c56261a445` |
| caller-findings-addendum-04.md | `da9fa98c9d5ddc7c9ece844c68d23274c4111a9645488f37da986cedf1f25977` |
| caller-findings-addendum-04.json | `022ab630cc4e954b14fd47970343ca84b2f9e88a851229f782d4a062b725c4a5` |

The original report's rejected-capture paragraph accidentally used 15,059 (the total steady user CPU samples across all eight processes) for round2 combined. The additive correction preserves the original bytes and records the correct scopes: round2 combined has 1,510 steady CPU samples, 1,616 full-process CPU samples and 190,078 total perf records. Its one invalid libc chain lies in the steady interval. The table above uses the corrected scope.

Continue with the actual integrated ordinary reversed screen. Further local sensitivity is justified only if the residual risk changes the selection decision. A combined completion-tail hypothesis may be reviewed against these new caller observations, but it is not implemented or selected by this report.
