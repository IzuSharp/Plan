# tail-completion06 — independent executed correctness review

Reviewer: `/root/candidate_contract_review`. Candidate and test author: `/root/worker_boundary_review`.

**Conclusion: no blocking correctness or evidence-identity defect found in the reviewed candidate.** The actual two-provider Release Native AOT correctness run supports proceeding to the separate package-consumer, mechanism and ordinary performance gates. It provides no ordinary timing, allocation, or final campaign credit.

## Reviewed identity and execution

The candidate is commit `4a9e4435ea5c836be44fb00dc4219301567072c6`, tree `a7065978ba432dfba71f177435232090cf154d34`. Product code is unchanged from independently reviewed `39d9b27c27e891b5a48b6541b629a43de3d1036d`; the later commit adds the targeted NativeHost regressions. The independent product and source-test reviews remain separate, preserving their chronology.

The author ran `correctness-01/receipt.json` with Release, Linux x64, Native AOT, locked restore, SDK 11.0.100, compiler warnings treated as errors, generated C# retention, one compiler processor, and the already built original two native images. Both recorded publish and full NativeHost runner commands exited 0. Receipt SHA-256 is `ac90c06cbf62e51313f73e7575f3b1ade79d8d61efde470033bbb28b1c0cceaf`.

The actual executable SHA-256 is `d3a89e2681cd3d905c73401eb312eb2fb421c3fc8b6e974a997543daf9867c84`. Its retained debug image SHA-256 is `35e4fc4b82c4b7aee6f8a48714b405d443f27fd7b33d9f1f7c34d96c13b859a2`. Both expose Build ID `05fbbb9bd1bc3f8652604d594138a167d4bb0906`. The native images copied into the publish output match both their original files and frozen native manifests byte for byte; the candidate's native source is unchanged from those manifests' source commit.

## What the actual run proves

The original `runtime/consumer.log` records ReadyScheduling **12 scenarios / 226 assertions for each provider**, including first-generation consumption and a next generation completing while the old managed publication frame is held; the explicit replacement for the old “held Post blocks the next generation” assertion; registration/caller/publisher ExecutionContext separation and restoration on return and exception; late-registration queue behavior; exact captured Post errors both before delivery and after consumption/request of the next generation; ordinary inline continuation failure; and multiple already-consumed publisher frames held concurrently. WorkerExecution remains **4 scenarios / 21 assertions per provider**.

The full default suite also executes the meaningful unreserved scheduler/setup failure paths, preserved setup-versus-stop error ordering, native Run and borrowed-buffer retirement, exact fetch-count rows 0/1/32/64/100/1000, transaction parent and EOF behavior, close/cancellation, public and borrowed readers, and command completion. Its final summary reports **438 B04 assertions / 36 independently observed managed retirements** and zero source/session/operation/cursor/buffer/handle/pull/command native counters. These final aggregate numbers are separate from the individually printed sub-suite assertions; they are not added together into an invented total.

The existing runner starts one isolated TCP PostgreSQL fixture, runs the actual ELF, then stops the server in `finally`; the retained PostgreSQL log records shutdown. This correctness runner is a different lifecycle than the mixed-load observer and does not claim that observer's process accounting.

## Independent integrity checks

`validation-02.json` records **1,489 checks, all passing**. They cover the precise candidate commit/tree and clean tracked source; all **1,408 tracked input hashes**; retained before/after-build equality; all **43 copied generated-source hashes** and their manifest; the executable and debug file hashes and Build IDs; original and published native hashes and manifest identities; the local build driver and toolchain environment hashes; both command-log hashes and exit codes; runtime-log hash and expected provider summaries; PostgreSQL shutdown; and the committed-diff impact plan's separate SQLite/PostgreSQL public groups and empty runtime steps. No test, database, profiler, or benchmark was executed by this reviewer.

The first verification receipt `validation.json` is retained. Its only failure was this reviewer's schema expectation: `impact.py` uses an empty mapping `{}` for `run_steps`, while the first assertion expected an empty list `[]`. The corrected receipt records and hashes that original failure and checks the actual empty-mapping schema. No candidate, measurement, raw receipt, or earlier evidence was changed to obtain the corrected result.

## Scope and remaining gates

- The author driver asserts tracked-input equality once more at completion but does not retain a third after-run manifest. This review independently verifies the retained before/after-build maps and the current unchanged tracked worktree; it does not invent an after-run file.
- This NativeHost correctness image uses the repository's normal project references. The real NuGet PackageReference ordinary consumers and their generated code, ELF/debug/native/input bindings remain a separate gate owned by the campaign coordinator.
- The controlled scheduler's thread-local dynamic Execute interval plus held-stack barriers proves the correctness ordering under test. It is not a precise setter-entry/return CPU or scheduling measurement; the separately identified diagnostic image must establish that mechanism.
- The baseline publication-failure negative control is not part of this receipt. Its entry point runs SQLite first; a failure there leaves PostgreSQL unexecuted and must be reported accordingly.
- This review supports correctness of the demonstrated paths, not an exhaustive proof of every schedule or a performance benefit. Repeated same-machine ordinary comparisons and the required frozen long campaign remain outstanding.

No additional optional test is required before the coordinator continues those already planned gates. Preserve the documented old risks and actual measured outcomes; select or reject this candidate from its new evidence rather than inheriting a verdict from the historical Common-A experiment.
