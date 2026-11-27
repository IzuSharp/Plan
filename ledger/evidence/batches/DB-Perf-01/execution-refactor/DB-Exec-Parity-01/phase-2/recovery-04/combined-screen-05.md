# Integrated05 — completed ordinary screen and remaining risk

The quiet local Linux x64 window completed **122 serial processes and299,008 checked businesses**, with zero business/oracle failures and returned owners. All recorded actual source/package/generated/ELF/debug/native inputs were unchanged before and after. `experiments/recovery/combined-screen-05/window.json` records the window, commands, exits and identities. All original results, histograms, observations and partial preparation records remain. This is short causal evidence; final1800-second campaign credit remains **0/4**.

The comparison is matching unchanged main, integrated05 and Dapper, using128 warmups plus2,048 operations, two reversed rounds. SQLite covers numeric1, text32/100/1000, early stop, dynamic optional filter, wide32 and related32. PostgreSQL also covers money1/32/1000. Eight additional PostgreSQL processes compare Worker-D with Worker-D+decimal for money1, using256 warmups,8,192 operations and four reversed rounds. Runtime settings are default; no profiler or allocation shim is active. The original observer's incomplete PostgreSQL descendant CPU is not credited as steady server cost.

## Repeated combined improvements

CPU is whole-client process CPU/success, including visible framework, driver, DTO and harness work. It is not exclusive framework CPU. Ratios use each same-round Dapper result; no cross-native identity arithmetic is used.

| Provider / business | Main CPU us, rounds1 /2 | Candidate CPU us, rounds1 /2 | Candidate change | Candidate / Dapper CPU |
| --- | ---: | ---: | ---: | ---: |
| SQLite text1000 | 6,183.88 /7,139.16 | 4,682.32 /4,382.46 | −24.28% /−38.61% | 6.88× /6.35× |
| PostgreSQL text1000 | 6,644.98 /6,828.29 | 5,360.86 /5,458.94 | −19.32% /−20.05% | 9.76× /8.53× |
| PostgreSQL money1000 | 9,391.03 /10,558.90 | 5,523.93 /5,845.48 | −41.18% /−44.64% | 9.06× /5.71× |
| SQLite related32 | 3,827.13 /3,689.73 | 3,467.20 /3,374.02 | −9.40% /−8.56% | 3.66× /3.61× |
| PostgreSQL related32 | 3,561.42 /3,434.17 | 2,950.30 /2,973.07 | −17.16% /−13.43% | 8.29× /7.54× |

Related32 process managed allocation falls from approximately686.4 KB to516.1 KB in both providers and rounds, about170.3 KB/business. The prior clone and capacity scopes explain their own observed pieces; this combined process result is measured directly. Dapper remains approximately74.1 KB on SQLite and51.2 KB on PostgreSQL. Neither allocation parity nor framework-wide zero allocation is established.

Text100 and wide32 also improve CPU in both rounds/providers. Numeric1, exact text32, dynamic filtering and several tails vary by order. The full per-round absolute values are in the unchanged summary/raw files; do not promote isolated favorable short results to universal alignment.

## Risks that still affect selection

PG money1 Worker-D versus Worker-D+decimal CPU changes are **+5.61%, −1.15%, −1.73%, +1.46%**. The earlier consistent CPU rise is not consistently reproduced in this combined context. However, p99 is higher in all four pairs (876.544→2818.048,1097.728→1368.064,909.312→1220.608,901.120→1302.528 us). This is a retained tail risk, not proof that the historical CPU cause is solved. The diagnostic caller evidence remains separate.

PG early-stop candidate CPU rises **13.57% /15.77%**, and service p99 rises **39.88% /43.36%**; service p50 changes −2.00% /−0.61%. The actual business must be described correctly: `--rows32` is not its SQL LIMIT. EarlyCase selects up to1,024 full nine-column Orders, maps three rows, then awaits cursor disposal. Closing/draining is inside the business latency. The original narrow diagnostic that stopped after one row is a different observation and cannot explain this result by itself.

Independent source/raw review verifies the same SQL after provider parameter-placeholder normalization, same DTO and stop rule, and per-business one SQL plus five native protocol-send API calls in all four main/integrated results. Those API counts are not wire-message counts or actual waits. Persistent sessions retain their physical connection through the measurement; each business releases CommandGate, while connection return occurs after the entire worker/session lifetime. Native close still drains remaining results and waits for the extra Sync acknowledgement. Removing that recovery would break the preserved contract.

The next local isolation uses existing main, decimal-only, Worker-D-only, Worker-D+decimal and integrated05 ELFs, two reversed rounds,2,048 operations and128 warmups. The fifth integrated control distinguishes the concrete current binary from the four-factor source variants. No new product change is selected before this attribution. The plan is prepared under `experiments/recovery/early-stop-risk-05`, with an atomic resume record; it has not received measurement credit in this checkpoint.

## PostgreSQL observation is now independently validated

The independently identified local `run_proc_tree_observer.py` adapter uses PPid topology and PID/startTicks checks because task children files are missing here. A real backend visibility control and a positive CPU/retirement control, followed by475 independent checks, support collecting visible-tree intervals. The positive control records child12 user/7 system ticks transferring to parent reaped+12/+8, with aggregate1/17→13/24→13/25. The original control's requested parallel0 versus actual2 failure is retained; the narrower CPU-transfer conclusion does not assume the requested setting took effect.

The adapter can report non-atomic observed inner/outer intervals and full-lifetime wait4 separately. It does not prove exact cgroup/steady CPU, complete short-lived-process coverage or mathematical bounds on unobserved work. Original product `run.py` remains unchanged. Its adapter SHA is `d7db0a60fd171e6124aecec078ee1bdd3331a9b534df340b2155f509ede4d8ff`; original observer SHA is `296e6b802d8bc1bcf964d7faa71d4adaa37226a867c17a9a3b5f00284f769b86`.

Continue with the targeted early-stop screen and the independently reviewed final outer identity/accounting gate, then zero-refusal mixed35 cost, pressure, freeze, matched before evidence and the four serial long cells. No final performance, merge or release credit is added by the current passing product CI.
