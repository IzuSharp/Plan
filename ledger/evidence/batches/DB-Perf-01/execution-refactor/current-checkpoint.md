# DB-Exec-02 current checkpoint — 2026-11-26 Asia/Shanghai

This is an in-progress checkpoint, not final acceptance. Continue the user-authorized complete refactor, local measurements, review, normal merge and existing release verification. Current candidate long cells remain **0/4**.

## Fixed implementation and public CI

- Before: `f0078da720e07031bc56464995af6791c41aaae8`, main `e063f2eb6e2e857e3f19f96bf263cae372651a27`.
- Candidate B local package producer `a27ff3189bd48b9c08d58e38338b2bfde7669bdd`; remote tree-identical producer [c2df05ff01e90a92aa70884827735d7dfa1dbc3d](https://github.com/IzuSharp/Korda/commit/c2df05ff01e90a92aa70884827735d7dfa1dbc3d). Native local `dc82792c519ee90be30f5c49b2f785ecd33ad915` is tree-identical to remote [1f93c5addeae962fee692f5d2a533c596efaa16c](https://github.com/IzuSharp/Korda/commit/1f93c5addeae962fee692f5d2a533c596efaa16c). Exact tree mapping and reason are in [source-parity.json](candidate-b/source-parity.json).
- Existing [CI 45684406029](https://github.com/IzuSharp/Korda/actions/runs/45684406029) passed all selected build/security/provider scopes. Both providers were verified independently. No performance job was added. The local `dotnet format` failure was an AF_UNIX BuildHost limitation; remote existing CI completed the gate.
- Both independent local native producers and bundles succeeded, as did six external public PackageReference consumers (workload/query-phases/resource × two providers). Receipts are in [candidate-b/input-receipts](candidate-b/input-receipts).

## Measured regression and outstanding correctness

[Candidate B](candidate-b/README.md) contains the 48-command current-host comparison with before and actual Dapper.AOT. C8 mixed CPU/throughput improve, but 1000-row read-complete latency regresses; B is not accepted as final. All raw observations are retained, including 5-second sample limits and business allocation.

An independent local full B gate failed native.sqlite14 case 4 (savepoints): source/session owner counts remained 1/1 immediately after closure, with no cursor/buffer/operation, no leased or pending connection and already retired state. An isolated source-bound fixture naturally reproduced it at iteration 290; exact thread-epilogue gates reproduce both finish and deadline closure windows on the first attempt. Releasing the diagnostic gate lets the counters reach zero. This locates retained background references but does not turn the original failure into a pass. The corresponding 20,814-byte Transaction/Savepoint implementation is identical in before and B (SHA-256 c4831377ddaa94659f8c8afcab028a73d416f00043000d6aa6feaf7fdf11f0d5). It does not establish the cause of the two older unexplained aborts.

A separate retirement-fence worktree is implementing a truthful join of final thread references, including Source parent lifetime, deadline thread, failure paths and no self-wait deadlock. Keep physical transaction outcome/Unknown/cleanup publication semantics distinct from final local reference release. Do not add sleeps or weaken owner assertions.

## Scheduling and allocation investigations

The isolated one-prompt retry plus occupied-slot scan candidate is local `81a9fd6` in `DB-Exec-02-retirement`. Its two independent bundles and six external AOT consumers built successfully. The 46-command paired B/C run passed all oracles, but SQLite large-result benefit is not stable. A four-queued-retry variant, `fdf1cb1` in `DB-Exec-02-retirement-four`, has passed the complete Interop.Async AOT gate and is building its separate consumers. These are bounded separately queued retries after actual Pending, with native quiet still mandatory; no spin, inline application continuation or premature owner release is accepted. No experimental source has replaced the formal B images.

The independent ABI diagnostic matrix (two source commits × both providers × 1/100/1000 rows × three routes) passed 12 receipts / 108 windows / 864 sampled queries. Fixed FFI less actual Pending retries is 37→29 for single-row Fluent/raw and 34→26 for prepared. SQL remains one per query; PG successful libpq send calls are 5→4. Raw Pending counts also increased in SQLite 1000-row B and are retained separately. Instrumentation perturbs races and receives no timing credit.

Separate allocation-only consumers instrument the actual generated mapper and List constructor/Add scopes. All six AOT variants (before/B/Dapper × two providers) build; SQLite correctness instrumentation passes all 1/100/1000 rows. Measured mapper+List scopes agree among routes: 136, 7256 and 77816 B/query respectively. These scopes include codec scratch and are not pure live-object estimates; the short 2-operation windows validate the instrument, and framework-only fields remain null. PG execution and larger independent allocation windows remain pending. The original overlay build polling denial is preserved; successful subsequent builds use explicit offline restore and kernel socket restrictions, without metadata requests.

## CI measurement separation

Read-only audit found legacy profiling invoked by default correctness entries (Fluent, Streaming, Abstractions, Binding and NativeHost). Move their pure timing/allocation/RSS sampling to existing explicit local diagnostic entry points while preserving complete functional, owner, wire, cancellation and race assertions. Interop.Negotiation.Supports has a documented public no-per-call-allocation promise; retain a finite contract assertion without its warmup/10,000-call benchmark window. These are existing misplaced routines, not new performance jobs. Proposed patches are not yet applied to frozen B. Re-run the actual impact plan after selection; do not weaken the planner or conceal profiling in tests.

## Resumption

Workspace root: `/workspace/scratch/17ac3f8f2fbf`; source pinned tools from `tools/task-env.sh`. Formal worktrees are `worktrees/DB-Exec-02-korda`, `DB-Exec-02-design`, and `DB-Exec-02-plan`; each has a task-specific identity. `DB-Exec-02-before` is immutable. Use recorded native manifests and independent package feeds, not a combined profile for a provider package. Build with one MSBuild process and no shared compiler because Unix IPC is unavailable. Start task-owned PostgreSQL and consumers in the same exec namespace.

Before timing, stop/pause all task-owned builds, correctness tests and diagnostic loads. Next: finish the transaction fence correctness fix and scheduling comparison; settle remaining command/owner costs; apply reviewed CI measurement separation; freeze final packages/consumers; calibrate actual arrival rate; supplement same-condition before baseline; run four required serial 1800-second candidate/Dapper cells; review and update all three PRs; normally merge and observe unchanged release rules. Keep old failed/unknown observations separate.
