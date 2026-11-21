# Perf-01 epoch-002: independent profiling source review

**Verdict: ACCEPT for prospective diagnostic source and schema consistency only.** Reviewed commit: `45435a350d2686eac0adcfe71f6409a8e4698d8a`; profiling index SHA-256: `9664da302025f3f172fe30b38aea22f086661ce78392c0b9acb5758dc55fcd6f`. It binds the separately reviewed measurement interface `b4e07743394c01e2eaf21c8d7d8345f43ea97bb72d0a8ea4fbedd9a15df173c5`.

All 4 caller/plan/documentation files, 15 original repository sources and 6 original protocol profiles were independently rehashed without mismatch. This review imported no probe or measurement module and ran no build, test, service or load.

## Actual original interfaces

The original Inspect preparation accepts the supplied codec-manifest identity and creates one isolated AOT consumer from existing packages, with original no-Rust traps and dependency-lock checks. Its six positional arguments and snake_case result fields match the caller. Each product role has three independent Inspect processes, each with 10,000 warmup calls and ten batches of 100,000 measured calls. The probe self-checks its executable, retained packages, manifest and actual codec native mapping. Metadata lookup is distinct from codec computation.

The Shared Page and Retirement callers reuse the actual role's existing producers. Both original result schemas use PascalCase. Page checks complete ordered 100-row materialization, exact 1,000-page completion, executable/manifest identity and source/session/transaction cleanup. Retirement's actual assembly is `NativeWeave.Data.NativeHost.Tests`; its original hooks enforce complete observed retirement. The caller requires 1,000 scalar calls and actual observations without assuming a fixed operations-per-call count. Retirement's executable is bound through the producer and owned command; its result does not independently report that executable hash.

Loaded native files are matched only against the selected role's artifact map and database provider. No before/after union can satisfy the check. The separate final descriptor is mandatory for after diagnostics and does not relabel baseline evidence.

## PostgreSQL ownership and CPU placement

Shared PostgreSQL probes use the original loopback private-cluster context. Observed settings must be `18.0|on|on|on` before execution. The parent checks actual PostgreSQL/psql identities and the successful final original stop command. The unchanged finite owner covers startup before the context yields, probe execution, teardown and failure cleanup.

The original application profiler's arguments and logging/wait-summary fields match. It retains automatic GC, default sampling and inherited CPUs 2–3 for the generator, database, application and wait observer. These diagnostic policies are explicit; the different formal deferred/threaded database gate is not applied. Protocol generators use CPUs 0–1, services and Shared probes use CPUs 2–3, and the outer owner uses CPU 8. All commands share the existing exclusive reservation and finite ownership control.

## Diagnostic eligibility and evidence

All six original protocol profiles retain `formal_timing_eligible: false`. The unchanged protocol reader must preserve exactly its profiling-only rejection; an additional correctness, identity, service or retirement issue fails the caller. Fresh diagnostic directories cannot overwrite or resume a partial result. Every terminal path retains zero effective-load credit.

The complete declared matrix contains **36 role/profile invocations and 40 probe processes**, plus two Inspect consumer preparations. The four additional probe processes come from Inspect's three processes per product role. This is a planned population, not an execution count.

Interpretation remains limited to the original observations: Shared validation and retirement-hook work are included; wait occupancy is sampled; concurrent SQL durations cannot be subtracted from application wall time; protocol allocation/CPU/RSS are process-wide; exact boundary, pin, wakeup and context-switch attribution is unavailable. Inspect/Shared provide no RSS or post-idle series. Compression remains identity-only on gRPC. Actual owner receipts and numeric results remain pending. Main 30-minute segments credited: **0**.
