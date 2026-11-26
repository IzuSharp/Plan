> **Measured continuation, 2026-11-26 (Asia/Shanghai):** public0f completed 18 ordinary phase, 12 ABI and 18 allocation commands on the restored Linux host. See the [actual evidence and final-close decision](continuation-3/measured-checkpoint-0f3816c.md). The remaining generic final-close retirement timer is now being replaced in subordinate DB-Exec-03-close worktrees. Current final long credit stays **0/4**; no new final-candidate or merge acceptance is inferred.

# Continuation 3 — final public source frozen

The final published implementation is [0f3816c4](https://github.com/IzuSharp/Korda/commit/0f3816c4006488821f40afde91bbbd717d57ccd6),
tree `9935773d28b3043618285cf0ecd5c476539b2f8c`, identical to reviewed local
`6da0074513d9cb1ff9f13748b058211ec706f230`. Read
[continuation-3/README.md](continuation-3/README.md),
[final parity](continuation-3/source-parity-final.json) and source-bound receipts.
The prior scratch workspace is absent; the missing channel was reconstructed
on ada28311. Ordinary, relation and CRUD streams use lazy native channels and
stable scoped spans. Per-batch generic operations and obsolete wrappers are
removed. Primary-error and refused-scheduler corrections/tests are included.

The final source's [CI45734731584](https://github.com/IzuSharp/Korda/actions/runs/45734731584)
is successful: Linux, interop, both independent providers, security and Verify
passed; modules/publish were skipped. The earlier e0 CI is retained separately.
Both final native producer profiles completed with exit0, both local packages
and four ordinary candidate consumers were built. Those build receipts do not
relabel the isolated development suites as one final local package execution.
Final long credit is **0/4**; no final timing gain, framework-zero allocation,
merge or publication is inferred from these gates.

The workspace is `/workspace/scratch/4a65d70f0fe1`. Its `tools/task-env.sh`
selects the hash-verified toolchain. The 12 ordinary consumer source sets,
including actual generated C#, are preserved in
[consumer-inputs.tar.gz](continuation-3/consumer-inputs.tar.gz) with an external
[manifest](continuation-3/consumer-inputs.manifest.json). Build-only processor/
compiler settings must not be applied to measurement processes. Product
editing uses task worktrees; GitHub updates use expected-head fast-forwards.
Keep the fetched public product/package identity distinct from local-only
diagnostic tool repairs. Continue with separately recorded local measurements
and the required four serial1800-second candidate/Dapper cells.

---

## Previous checkpoint retained below

# DB-Exec-02 current checkpoint — 2026-11-26 Asia/Shanghai

This is an in-progress checkpoint, not final acceptance. Continue the user-authorized complete refactor, local measurements, review, normal merge and existing release verification. Current candidate long cells remain **0/4**.

## Fixed implementation and public CI

- Before: `f0078da720e07031bc56464995af6791c41aaae8`, main `e063f2eb6e2e857e3f19f96bf263cae372651a27`.
- Candidate B local package producer `a27ff3189bd48b9c08d58e38338b2bfde7669bdd`; remote tree-identical producer [c2df05ff01e90a92aa70884827735d7dfa1dbc3d](https://github.com/IzuSharp/Korda/commit/c2df05ff01e90a92aa70884827735d7dfa1dbc3d). Native local `dc82792c519ee90be30f5c49b2f785ecd33ad915` is tree-identical to remote [1f93c5addeae962fee692f5d2a533c596efaa16c](https://github.com/IzuSharp/Korda/commit/1f93c5addeae962fee692f5d2a533c596efaa16c). Exact tree mapping and reason are in [source-parity.json](candidate-b/source-parity.json).
- Existing [CI 45684406029](https://github.com/IzuSharp/Korda/actions/runs/45684406029) passed all selected build/security/provider scopes. Both providers were verified independently. No performance job was added. The local `dotnet format` failure was an AF_UNIX BuildHost limitation; remote existing CI completed the gate.
- Both independent local native producers and bundles succeeded, as did six external public PackageReference consumers (workload/query-phases/resource × two providers). Receipts are in [candidate-b/input-receipts](candidate-b/input-receipts).
- The next integration checkpoint is [ada28311a384ad149fdc3f9db3b14473aedf0061](https://github.com/IzuSharp/Korda/commit/ada28311a384ad149fdc3f9db3b14473aedf0061), publicly tree-identical to local `71bcd5a2365118b2512c0d7597356bfaf947ba85`, tree `1a3eb726457870511ead7e38890d8cd07a972775`. It includes the transaction fence and deadline-order correction, private query-arena transfer, CI correctness separation and occupied coordinator-slot scanning. It does not include the uncompleted cursor channel or adopt prompt retries/1 ms polling. Its CI is a separate pending observation; B's passing CI is not credited to this source.

## Measured regression and outstanding correctness

[Candidate B](candidate-b/README.md) contains the 48-command current-host comparison with before and actual Dapper.AOT. C8 mixed CPU/throughput improve, but 1000-row read-complete latency regresses; B is not accepted as final. All raw observations are retained, including 5-second sample limits and business allocation.

An independent local full B gate failed native.sqlite14 case 4 (savepoints): source/session owner counts remained 1/1 immediately after closure, with no cursor/buffer/operation, no leased or pending connection and already retired state. An isolated source-bound fixture naturally reproduced it at iteration 290; exact thread-epilogue gates reproduce both finish and deadline closure windows on the first attempt. Releasing the diagnostic gate lets the counters reach zero. This locates retained background references but does not turn the original failure into a pass. The corresponding 20,814-byte Transaction/Savepoint implementation is identical in before and B (SHA-256 c4831377ddaa94659f8c8afcab028a73d416f00043000d6aa6feaf7fdf11f0d5). It does not establish the cause of the two older unexplained aborts.

The separate retirement-fence source `4c6f1888badbe4446fe4526c77cb9e88da030b9c` now passes the original immediate-zero oracle in 300/300 natural case-4 repetitions, SQLite14 (140,257 assertions), transaction lifecycle (120 checks), actual provider tests (183), all 11 PostgreSQL fixture groups and PostgreSQL protocol/Unknown tests (325). Independent tickets complete only after worker captures are released; explicit Source/Transaction joins wait those tickets. The Source destructor avoids self-wait. Root review caught and corrected deadline dispatch ordering before the final targeted run. No sleeps, weakened owner predicate or transaction-outcome changes were accepted. [Checkpoint-2 evidence](checkpoint-2/README.md) retains exact isolated sources, failed diagnostics and validation identities. The final combined channel/package gate remains pending.

## Scheduling and allocation investigations

The local C1 (`81a9fd6`), R4 (`fdf1cb1`) and database-only R1ms (`6afbeeb`) variants all built their independent bundles and actual external AOT consumers. Their 46-, 50- and 42-command serial comparisons passed all command/result/owner oracles. [Raw receipts, complete source patches, analysis and decision](retirement-experiments/README.md) retain every short observation. R1ms improves median C8 throughput over R4 from 840.3 to 1416.2 ops/s on SQLite and 1493.3 to 2308.0 on PostgreSQL, but repeated 1000-row completions remain variable. These five-second processes establish neither long-load acceptance nor a stable final solution. The one-second C1/R1ms idle comparison also changes retry count and cannot isolate the timer's CPU cost. No experiment replaces the frozen B inputs.

The selected next rewrite is a cursor-scoped native pull channel with a reusable managed controller and scoped Span batch owner. Its first request opens/validates and then fetches; later requests reuse the channel without a per-batch native operation or generic retirement polling. Each accepted generation detaches exactly one ready callback after provider/read guards finish. Final close still joins all independent native tails and cursor cleanup. Active requests have temporary roots/slots; idle abandoned cursors must not have a strong self-root. The [Design target](https://github.com/IzuSharp/Korda-Design/blob/task/DB-Perf-01-query-optimization/docs/database/query-semantics.md#cursor-pull-channel-remove-the-per-batch-operation-lifetime) defines the proof, deletion and public-package obligations. The earlier operation-wrapper pooling draft was superseded before compilation or measurement and receives no performance credit.

The private complete-command compiler also now consumes its fresh QueryData arena into the immutable plan, consumes an already-private CTE body, and parses literal cells through a borrowed validated frame before one durable cell copy. Public mutable queries retain their snapshots and recoverable copy-on-success behavior. Isolated `native.query` passes overwritten-input and original-query-lifetime checks at `21acc57d448a285b8201d61c314b39092bc7a12c`; integrated source is linked above. This removes specific copies, not NWQC encoding or all AST/parameter allocation. Its timing is not credited to B.

The independent ABI diagnostic matrix (two source commits × both providers × 1/100/1000 rows × three routes) passed 12 receipts / 108 windows / 864 sampled queries. Fixed FFI less actual Pending retries is 37→29 for single-row Fluent/raw and 34→26 for prepared. SQL remains one per query; PG successful libpq send calls are 5→4. Raw Pending counts also increased in SQLite 1000-row B and are retained separately. Instrumentation perturbs races and receives no timing credit.

Separate allocation-only consumers instrument the actual generated mapper and List constructor/Add scopes. All six AOT variants (before/B/Dapper × two providers) build; SQLite correctness instrumentation passes all 1/100/1000 rows. Measured mapper+List scopes agree among routes: 136, 7256 and 77816 B/query respectively. These scopes include codec scratch and are not pure live-object estimates; the short 2-operation windows validate the instrument, and framework-only fields remain null. PG execution and larger independent allocation windows remain pending. The original overlay build polling denial is preserved; successful subsequent builds use explicit offline restore and kernel socket restrictions, without metadata requests.

## CI measurement separation

The reviewed cleanup `e125bcd8bebb27e60a1172ab64d9dec3a996e4e2` is integrated. Nine default profiling subprocesses were removed from Abstractions/Binding/Streaming; Fluent windows became finite behavior assertions; Host snapshot measurements require its existing explicit local flag. All six affected default AOT entries passed, including their actual original provider wrapper arguments. Wire, quota, failure, owner, race and complete-row consumption checks remain. Interop.Negotiation.Supports retains its finite public no-call/no-allocation contract assertion. The restore selector failure and preexisting local formatting findings remain recorded. No performance action, workflow or hidden sampling was added.

The actual integration plan at `71bcd5a` selects `interop`, `linux`, `postgresql`, `sqlite`. Callback/async changes require their conformance checks; shared database/native/source and API consumers require the existing database, Fluent, migrations and relations checks; both provider packages independently build, pack, check shipped APIs/dependencies, test and execute AOT consumers. Benchmark directories appear only as ownership reasons, with no execution action. [The exact plan](checkpoint-2/integration-plan.json) records all paths and actions. The action set is unchanged from B; new test reasons are covered/deduplicated by existing database regression routing.

## Resumption

Workspace root: `/workspace/scratch/17ac3f8f2fbf`; source pinned tools from `tools/task-env.sh`. `DB-Exec-02-korda` and `DB-Exec-02-before` remain frozen measured inputs. `DB-Exec-02-integration` owns combined selected changes; `DB-Exec-02-typed-fetch` owns the coordinated managed channel/scoped implementation. Design/Plan continue their existing PR branches. Build with one MSBuild process and no shared compiler because Unix IPC is unavailable. Start task-owned PostgreSQL and consumers in the same exec namespace. Fetch the eventual published product commit and build final native profiles, independent packages and consumers from that clean public SHA; do not silently equate differing commit identities merely because files match.

Before timing, stop/pause all task-owned builds, correctness tests and diagnostic loads. Next: complete and prove the cursor channel, remove its replaced internal path/unused bit-27 extension, integrate and run full correctness/API/independent-package gates; measure actual first-row/refill/mapping/close and allocation/FFI/SQL costs; freeze final packages/consumers; calibrate actual arrival rate; supplement same-condition before baseline; run four required serial 1800-second candidate/Dapper cells; review all layers and update all three PRs; normally merge and observe unchanged release rules. Keep old failed/unknown observations separate.
