# Perf-01 — recovered SQLite application diagnostic

**The completed current2f/candidatea5748 experiment is reusable as diagnostic evidence.** Executed verifier helpers match the independently reviewed bytes, actual plans match terminal receipts, and all six original C16 cells pass their unchanged predicates. This recovery does not rerun the workload or grant formal performance credit.

The candidate reduces observed latency and measurement RSS while consuming more CPU, including during short post-load idle. These descriptive differences do not establish statistical significance, maximum sustainable rate, a unique cause or 30-minute acceptance.

## Observed comparison

Each cohort contains three independent 60-second processes in AB/BA/AB order. Latency values are arithmetic means of process statistics, including process p99; they are not pooled percentiles. CPU and RSS belong to the complete mixed application.

| Metric | Current2f | Candidatea5748 | Candidate − current | Change from current |
|---|---:|---:|---:|---:|
| Whole mixed load mean (ms) | 33.564928 | 16.691281 | -16.873647 | -50.272% |
| Whole mixed load p99 (ms) | 172.307494 | 47.522623 | -124.784871 | -72.420% |
| Cycle conditional mean (ms) | 53.505458 | 25.101314 | -28.404144 | -53.086% |
| Cycle conditional p99 (ms) | 220.725469 | 52.231711 | -168.493759 | -76.336% |
| Page conditional mean (ms) | 13.611104 | 8.275641 | -5.335463 | -39.199% |
| Page conditional p99 (ms) | 36.686881 | 19.652641 | -17.034240 | -46.431% |
| Successful operations/s | 49.949941 | 49.996265 | 0.046324 | +0.093% |
| Measurement application CPU (s) | 20.936667 | 23.523333 | 2.586667 | +12.355% |
| Measurement CPU (% of one core) | 34.880666 | 39.223895 | 4.343229 | +12.452% |
| Mean measurement process RSS peak (MiB) | 40.479167 | 35.395833 | -5.083333 | -12.558% |
| Maximum measurement process RSS peak (MiB) | 41.664062 | 35.781250 | -5.882812 | -14.120% |
| Post-load-idle application CPU (s) | 0.166667 | 0.350000 | 0.183333 | +110.000% |
| Post-load-idle CPU (% of one core) | 3.355638 | 7.072850 | 3.717212 | +110.775% |

At the fixed 50 operations/s offered rate, small success-rate differences follow the measured observation windows and do not establish increased capacity. The candidate uses about 2.587 extra CPU-seconds per measurement process (+12.35%). Mean short-idle CPU rises from about 3.356% to 7.073% of one core. This idle phase precedes final reconciliation/close and is not a post-disposal idle observation.

## Every process retained

| Order / cohort | Success / offered | Whole mean (ms) | Whole p99 (ms) | Cycle p99 (ms) | CPU (s) | Peak RSS (MiB) | Idle CPU (%) | Eligibility |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 / current r1 | 3001 / 3001 | 35.368155 | 187.392029 | 278.046404 | 20.50 | 39.277344 | 3.214995 | passed |
| 2 / candidate r1 | 3001 / 3001 | 16.465751 | 48.223489 | 54.588361 | 23.24 | 35.781250 | 5.429086 | passed |
| 3 / candidate r2 | 3001 / 3001 | 16.686517 | 47.223354 | 50.577345 | 23.12 | 35.265625 | 8.072616 | passed |
| 4 / current r2 | 3001 / 3001 | 32.846692 | 151.600765 | 172.238173 | 21.40 | 40.496094 | 3.627632 | passed |
| 5 / current r3 | 3001 / 3001 | 32.479935 | 177.929689 | 211.891831 | 20.91 | 41.664062 | 3.224286 | passed |
| 6 / candidate r3 | 3001 / 3001 | 16.921575 | 47.121026 | 51.529426 | 24.21 | 35.140625 | 7.716847 | passed |

Every cell records 3,001 successful operations: 1,501 cycle and 1,500 page operations. Each has zero errors, zero observed SQLite BUSY/LOCKED exceptions and zero explicit business retries; 1,501 durable commits belong to the measurement phase. Independent queries verify 1,637 items, operations and outbox rows, with the durable oracle passed. Database and consumer resources report released/Succeeded, and the server reports Disposed. All six original service predicates pass unchanged p99 <= 500 ms and measurement RSS <= 256 MiB thresholds.

BUSY/LOCKED counts cover the whole application lifetime, including setup/recovery; internal SQLite busy-handler retries remain unobserved. Measurement resource error counts are zero. The current r3 final shutdown sample has one descriptor and one memory observation error, with the corresponding values unavailable; this adverse sample is preserved in JSON. Shutdown phases with one CPU sample retain unavailable CPU, not a fabricated zero. Ordinary summaries do not provide managed GC/allocation, pending tasks, byte owners, queues, connection-pool wait or physical SQLite lock wait.

## Actual source, package and execution identity

- Common application/driver: `2e3995df8d86583ee9443348276ca8d918056bfc`.
- Current managed source: `2f40348c3db80a4fbee7a99e721b374a597b16df`; packages `0.1.0-perf01.recovery004.after.1`.
- Candidate managed source: `a5748ad4e03825e3da7706d074887952da6c2d43`; packages `0.1.0-perf01.retry001.1`.
- Both use native assets from `2f40348c3db80a4fbee7a99e721b374a597b16df`. The actual B24 feed records fourteen candidate managed package rows and exactly three current native leaves.
- Current loaded observer SHA-256: `8257d25a2fa53e0f7d307e6541434b93b498a8c2ff8cc3617b2c9f12fd1d47b9`.
- Candidate loaded observer SHA-256: `5107c9cf094124922bc224a235dcae352995ad89ef55324f717c3e916f5b5b3d`.
- Build: `2026-11-21T10:53:09.899616+00:00` to `2026-11-21T10:54:16.830374+00:00`; four commands exited zero and retired.
- Collection/reader: `2026-11-21T10:55:26.769695+00:00` to `2026-11-21T11:03:10.257880+00:00`; six workloads and one collector exited zero and retired. All eleven receipts report zero remaining owned processes/owner children and no signals.

The candidate uses the ordinary B21 package-only baseline AOT application and the existing B23 catch/log/rethrow observer. Actual build checks pass unchanged business/runtime-witness/observer sources, external lock closure, observer lock, exact package/native provenance and no consumer Rust invocation. No SqliteTail recorder is used. Actual mapped executable/native hashes agree with each cohort’s original observer manifest.

Both driver variants remain `after`, selecting the original native route/close rules. The outer current/candidate identities retain their actual commits; current2f is not beforeEA5. This experiment does not isolate effects of individual managed changes.

## Recovery compatibility

No blocking semantic/provenance discrepancy was found for diagnostic reuse. Actual plans are separately receipt-bound; they are not falsely presented as executions of an unmodified private template. Differences are disclosed:

- Actual source/spec/output directories and command labels differ. Actual plans and each executed argv are separately receipt-bound.
- CLI options are reordered; taskset -c equals --cpu-list; RSS threshold 256 equals 256.0. The isolation note identifies diagnostic cohorts. Workload values and CPU affinity are unchanged.
- Actual load explicitly repeats inherited process-count/bytecode values and retains inherited TMPDIR. Actual observer adds explicit Cargo/Rustc traps and removes the Cargo PATH entry.
- Only metadata verifier deadlines differ: build 120 versus 60 seconds; reader 180 versus 900 seconds. Workload deadlines remain 960 seconds; all commands completed without signals.
- Actual outer output inventories contain fewer files; original completed readers retain cell evidence hashes and actual input maps bind both complete observer artifact maps.
- The actual source preparation index predates the populated load plan; the later plan is bound directly by the terminal execution plan SHA.
- Seven external-runtime/tool files are absent from the actual outer preflight map. All six actual frozen-input maps nevertheless exactly match original C16, including those seven recorded hashes. This limitation is disclosed; no stronger formal preflight claim is made.

The missing outer pins are the six HTTP Python package initialization files (h11, httpcore, httpx, h2, hpack, hyperframe) and taskset. All six actual frozen-source maps record the exact same hashes as original C16, and the complete original reader workload/resource signatures are equal. This is evidence of the observed configuration, not a claim that the stronger reviewed outer preflight ran unchanged.

The original run.py still terminates on actual invalid/correctness failure. Valid but service-ineligible samples would remain recorded and fail the final all-six eligibility check. No such failure occurred in these six cells. No raw observation, database, resource JSONL or binary was reread/rehashed for this recovery; completed original reader receipts and metadata were checked.

## Acceptance limits and retained adverse result

The original formal selected2f C16 result remains valid but service-ineligible at **567.131236 ms p99**, summary SHA-256 `44bccdba7b42ff3bac4709db2c7f367a29fb2a88d38777df8d6f51faeb51cd04`. These diagnostic samples do not overwrite or invalidate it.

This report grants **zero formal, capacity or long-duration credit**. Candidate selection must consider the latency/CPU tradeoff. BeforeEA5/final comparisons, the original noise gate and required long runs remain separate. No direct-Rust cohort was run in this diagnostic.

## Evidence identities

Public identities use filenames and hashes; operational paths, environment maps, PIDs and endpoints are excluded. Original evidence remains intact. Publication and durable raw retention are separate controller steps; this draft does not claim remote readback.

| Evidence | Filename | SHA-256 |
|---|---|---|
| actual build execution | `execution.json` | `658fccdc1dbb314e4a81b0a67d3fe967933a9b82f05e40eec9cf73b646d313ec` |
| actual load execution | `execution.json` | `d4283ad89fd634114c287424d1987c26fcd93f5c251eb3771847a2a15c77ae79` |
| actual build plan | `01-build-candidate.actual-001.json` | `ebfa612ae111e98fcd740c04d431315824772bd53c26bc3f092c7c9518efc331` |
| actual load plan | `02-six-cells.actual-001.json` | `f3fe22f1f3dddbde72634a016e8c6b22c140c06d56a8271a0e9e17e2fb193fbe` |
| executed source preparation index | `sources.json` | `323e22f7052b2f1615f20270bfa69f86ca169094cc598af0a78705eda835b43d` |
| independently reviewed recipe index | `sources.json` | `96ff380743055c93c0453f42d684ebabe82bde7ea4462b3ada6c03214610d2f6` |
| executed cell specification | `cells.spec.json` | `414f4e8373d8dc476e93354d259c77f75eb31bb0a30c5de49c167756bc56d664` |
| preserved formal C16 execution | `execution.json` | `66e8d576bfc4a339907ff0073a714468d6fec7baa76dbc78885b687a28209fcb` |
| preserved formal C16 freeze | `frozen-inputs.json` | `1238459cd1c06c3188b17cd539712318eacc29664efd4c8004f1e230b92c323b` |
| preserved formal C16 selected2f summary | `summary.json` | `44bccdba7b42ff3bac4709db2c7f367a29fb2a88d38777df8d6f51faeb51cd04` |
| actual candidate B24 package manifest | `manifest.json` | `efefc111caa3fcd652548f524210b504487f118ce33095367e816e2ccfcc9b9b` |
| current ordinary reference metadata | `progress.json` | `c312238b01eb4fe4f28d3ec97d3c7db09fa7eebf0fd2393f54dd044c2a445e42` |
| current original exception observer | `manifest.json` | `af04199542657e304e30dfce05b028f99b80e7b7f48c7b1618772de4afbf92b9` |
| candidate ordinary reference metadata | `progress.json` | `1276f396fa97db45c0eed26aea1e338e8603c47247cb9accf0ab8fef56999c5a` |
| candidate original exception observer | `manifest.json` | `34f7d53574fe30839ae6aa3d3a1c08b7ce9903b907e4b00e9e16ee7a7236fed5` |

The companion `binding-retry-application-recovered-001.json` preserves all six process metrics/counts, predicates, loaded asset identities, phase resource summaries, source receipts and descriptive delta denominators. `binding-retry-application-recovered-001.sources.json` pins the report files.
